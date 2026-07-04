"""Spritesheet export operators."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any

import bpy

from ..core.frame_math import frame_numbers
from ..core.frame_sync import sync_clip_frames
from ..core.render_state import selected_frame_numbers
from ..core.validation import validate_active_clip_render_context
from ..core.workspace_state import (
    active_workspace_or_none,
    effective_camera_or_none,
    effective_collections,
)
from ..export.composer import compose_spritesheet_png
from ..export.layout import ExportClip, clip_ranges
from ..export.metadata import build_spritesheet_metadata
from ..export.sequence import export_individual_frames
from ..render.renderer import render_clip_frames


def _scene_state(context: bpy.types.Context) -> bpy.types.PropertyGroup | None:
    scene = getattr(context, "scene", None)
    if scene is None:
        return None
    return getattr(scene, "spritesheet_state", None)


def _active_workspace(context: bpy.types.Context) -> bpy.types.PropertyGroup | None:
    state = _scene_state(context)
    if state is None:
        return None
    return active_workspace_or_none(state)


class SPRITESHEET_OT_export_spritesheet(bpy.types.Operator):
    bl_idname = "spritesheet.export_spritesheet"
    bl_label = "Export Spritesheet"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = _active_workspace(context)
        if workspace is None:
            self.report({"WARNING"}, "No active workspace")
            return {"CANCELLED"}

        settings = workspace.export_settings
        sheet_name = _safe_sheet_name(settings.sheet_name)
        errors = _validate_workspace_export(workspace, sheet_name)
        if errors:
            workspace.last_export_note = errors[0]
            self.report({"WARNING"}, errors[0])
            return {"CANCELLED"}

        output_folder = bpy.path.abspath(settings.output_folder)
        included_clips = [clip for clip in workspace.clips if clip.include_in_export]
        try:
            prepared = _prepare_export_clips(included_clips)
        except ValueError as exc:
            workspace.last_export_note = str(exc)
            self.report({"WARNING"}, str(exc))
            return {"CANCELLED"}

        os.makedirs(output_folder, exist_ok=True)
        png_path = os.path.join(output_folder, f"{sheet_name}.png")
        json_path = os.path.join(output_folder, f"{sheet_name}.json")
        sequence_folder = (
            os.path.join(output_folder, f"{sheet_name}_frames")
            if settings.export_png_sequence
            else ""
        )

        with tempfile.TemporaryDirectory(prefix="spritesheet_export_") as temp_dir:
            try:
                frame_paths = _ensure_rendered_frames(
                    self,
                    context,
                    workspace,
                    prepared,
                    temp_dir,
                )
            except RuntimeError as exc:
                workspace.last_export_note = str(exc)
                self.report({"WARNING"}, str(exc))
                return {"CANCELLED"}

            compose_result = compose_spritesheet_png(
                frame_paths,
                png_path,
                frame_width=settings.frame_width,
                frame_height=settings.frame_height,
                columns=settings.columns,
                padding=settings.padding,
                margin=settings.margin,
                transparent=settings.transparent,
            )
            if not compose_result.success:
                workspace.last_export_note = compose_result.message
                self.report({"WARNING"}, compose_result.message)
                return {"CANCELLED"}

            if settings.export_png_sequence:
                try:
                    export_individual_frames(frame_paths, sequence_folder, sheet_name)
                except (OSError, ValueError) as exc:
                    workspace.last_export_note = str(exc)
                    self.report({"WARNING"}, str(exc))
                    return {"CANCELLED"}
                settings.png_sequence_folder = sequence_folder

        ranges = clip_ranges(
            ExportClip(
                name=item["clip"].name,
                fps=item["clip"].fps,
                frame_paths=tuple(item["paths"]),
            )
            for item in prepared
        )
        metadata = build_spritesheet_metadata(
            sheet_name,
            settings.frame_width,
            settings.frame_height,
            settings.columns,
            ranges,
        )
        try:
            with open(json_path, "w", encoding="utf-8") as handle:
                json.dump(metadata, handle, indent=4)
                handle.write("\n")
        except OSError as exc:
            workspace.last_export_note = str(exc)
            self.report({"WARNING"}, str(exc))
            return {"CANCELLED"}

        workspace.last_export_png = png_path
        workspace.last_export_json = json_path
        if settings.export_png_sequence:
            workspace.last_export_note = (
                f"Exported {os.path.basename(png_path)} and individual frames"
            )
        else:
            workspace.last_export_note = f"Exported {os.path.basename(png_path)}"
        return {"FINISHED"}


def _validate_workspace_export(
    workspace: bpy.types.PropertyGroup,
    sheet_name: str,
) -> list[str]:
    settings = workspace.export_settings
    errors: list[str] = []
    if not settings.output_folder:
        errors.append("Missing export output folder")
    if not sheet_name:
        errors.append("Missing sheet name")
    if settings.frame_width < 1:
        errors.append("Frame width must be at least 1")
    if settings.frame_height < 1:
        errors.append("Frame height must be at least 1")
    if settings.columns < 1:
        errors.append("Columns must be at least 1")
    if settings.padding < 0:
        errors.append("Padding must be non-negative")
    if settings.margin < 0:
        errors.append("Margin must be non-negative")

    included_clips = [clip for clip in workspace.clips if clip.include_in_export]
    if not included_clips:
        errors.append("No clips included in export")
    names = [clip.name for clip in included_clips]
    if len(names) != len(set(names)):
        errors.append("Clip names must be unique")
    return errors


def _prepare_export_clips(clips: list[bpy.types.PropertyGroup]) -> list[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []
    for clip in clips:
        expected_frames = frame_numbers(clip.frame_start, clip.frame_end, clip.frame_step)
        sync_clip_frames(clip, expected_frames)
        selected_numbers = selected_frame_numbers(clip)
        if not selected_numbers:
            raise ValueError(f"Clip {clip.name} has no selected frames")
        prepared.append(
            {
                "clip": clip,
                "frame_numbers": selected_numbers,
                "paths": [],
            }
        )
    return prepared


def _ensure_rendered_frames(
    operator: bpy.types.Operator,
    context: bpy.types.Context,
    workspace: bpy.types.PropertyGroup,
    prepared: list[dict[str, Any]],
    temp_dir: str,
) -> list[str]:
    all_paths: list[str] = []
    for clip_index, item in enumerate(prepared):
        clip = item["clip"]
        frame_numbers_to_export = item["frame_numbers"]
        existing_paths = _existing_render_paths_for_clip(clip, frame_numbers_to_export)
        if existing_paths is not None and not clip.render_dirty:
            item["paths"] = existing_paths
            all_paths.extend(existing_paths)
            continue

        errors = validate_active_clip_render_context(workspace, clip)
        if errors:
            raise RuntimeError(errors[0])

        camera = effective_camera_or_none(workspace, clip)
        collections = effective_collections(workspace, clip)
        clip_folder = os.path.join(temp_dir, f"clip_{clip_index:03d}_{clip.id or clip_index}")
        result = render_clip_frames(
            context,
            clip,
            camera,
            collections,
            clip_folder,
            frame_numbers_to_export,
            workspace.export_settings,
        )
        if not result.success:
            raise RuntimeError(result.message)

        clip.last_render_note = f"Export rendered {len(result.frame_paths)} frames"

        paths = [result.frame_paths[frame_number] for frame_number in frame_numbers_to_export]
        item["paths"] = paths
        all_paths.extend(paths)
    return all_paths


def _existing_render_paths_for_clip(
    clip: bpy.types.PropertyGroup,
    frame_numbers_to_export: list[int],
) -> list[str] | None:
    by_frame = {frame.frame_number: frame for frame in clip.frames}
    paths: list[str] = []
    for frame_number in frame_numbers_to_export:
        frame = by_frame.get(frame_number)
        path = getattr(frame, "render_path", "") if frame is not None else ""
        if not path or not os.path.isfile(path):
            return None
        paths.append(path)
    return paths


def _safe_sheet_name(value: str) -> str:
    return os.path.splitext(os.path.basename(value.strip()))[0]
