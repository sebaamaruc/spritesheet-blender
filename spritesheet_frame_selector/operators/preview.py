"""Preview cache operators."""

from __future__ import annotations

import os
import shutil

import bpy

from ..core.cache import (
    build_preview_cache_key,
    clear_preview_state,
    count_existing_previews,
)
from ..core.frame_math import frame_numbers
from ..core.frame_sync import sync_clip_frames
from ..core.paths import (
    is_managed_cache_folder,
    preview_cache_folder,
    preview_cache_root,
)
from ..core.workspace_state import (
    active_clip_or_none,
    active_workspace_or_none,
    default_collection_count_error,
    effective_camera_or_none,
    effective_collections,
    effective_preview_mode,
    missing_effective_collection_names,
)
from ..preview.generator import generate_viewport_previews


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


def _expected_frames(clip: bpy.types.PropertyGroup) -> list[int]:
    return frame_numbers(clip.frame_start, clip.frame_end, clip.frame_step)


def _generate_preview_cache(
    operator: bpy.types.Operator,
    context: bpy.types.Context,
    *,
    force: bool,
) -> set[str]:
    workspace = _active_workspace(context)
    if workspace is None:
        operator.report({"WARNING"}, "No active workspace")
        return {"CANCELLED"}

    clip = active_clip_or_none(workspace)
    if clip is None:
        operator.report({"WARNING"}, "No active clip")
        return {"CANCELLED"}

    camera = effective_camera_or_none(workspace, clip)
    if camera is None:
        clip.cache_dirty = True
        clip.last_preview_note = "Missing effective camera"
        operator.report({"WARNING"}, clip.last_preview_note)
        return {"CANCELLED"}

    collections = effective_collections(workspace, clip)
    missing_collections = missing_effective_collection_names(workspace, clip)
    if missing_collections:
        clip.cache_dirty = True
        clip.last_preview_note = "Missing collection: " + ", ".join(missing_collections)
        operator.report({"WARNING"}, clip.last_preview_note)
        return {"CANCELLED"}
    collection_count_error = default_collection_count_error(workspace, clip)
    if collection_count_error:
        clip.cache_dirty = True
        clip.last_preview_note = collection_count_error
        operator.report({"WARNING"}, collection_count_error)
        return {"CANCELLED"}
    if not collections:
        clip.cache_dirty = True
        clip.last_preview_note = "Missing effective collections"
        operator.report({"WARNING"}, clip.last_preview_note)
        return {"CANCELLED"}

    try:
        expected_frames = _expected_frames(clip)
    except ValueError as exc:
        clip.cache_dirty = True
        clip.last_preview_note = str(exc)
        operator.report({"WARNING"}, str(exc))
        return {"CANCELLED"}

    if not expected_frames:
        sync_clip_frames(clip, [])
        clip.cache_dirty = True
        clip.last_preview_note = "Frame range is empty"
        operator.report({"WARNING"}, "Frame range is empty")
        return {"CANCELLED"}

    sync_clip_frames(clip, expected_frames)
    preview_mode = effective_preview_mode(workspace, clip)
    cache_key = build_preview_cache_key(workspace, clip, camera, collections, preview_mode)
    cache_root = preview_cache_root(bpy.data.filepath)
    cache_folder = preview_cache_folder(cache_root, workspace.id, clip.id, cache_key)

    if force and os.path.isdir(cache_folder):
        shutil.rmtree(cache_folder)

    result = generate_viewport_previews(
        context,
        clip,
        camera,
        collections,
        cache_folder,
        expected_frames,
        force=force,
        preview_mode=preview_mode,
    )
    if not result.success:
        clip.cache_dirty = True
        clip.last_preview_note = result.message
        operator.report({"WARNING"}, result.message)
        return {"CANCELLED"}

    for frame in clip.frames:
        frame.preview_path = result.frame_paths.get(frame.frame_number, "")

    clip.cache_key = cache_key
    clip.cache_folder = cache_folder
    clip.cache_dirty = False
    clip.last_preview_note = f"{count_existing_previews(clip)} previews ready"
    return {"FINISHED"}


class SPRITESHEET_OT_preview_generate(bpy.types.Operator):
    bl_idname = "spritesheet.preview_generate"
    bl_label = "Generate Preview"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        return _generate_preview_cache(self, context, force=False)


class SPRITESHEET_OT_preview_clear_cache(bpy.types.Operator):
    bl_idname = "spritesheet.preview_clear_cache"
    bl_label = "Clear Cache"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = _active_workspace(context)
        clip = active_clip_or_none(workspace) if workspace is not None else None
        if clip is None:
            self.report({"WARNING"}, "No active clip")
            return {"CANCELLED"}

        cache_folder = clip.cache_folder
        if cache_folder and os.path.isdir(cache_folder):
            if not is_managed_cache_folder(cache_folder):
                clear_preview_state(clip)
                self.report({"WARNING"}, "Skipped unmanaged cache folder")
                return {"FINISHED"}
            shutil.rmtree(cache_folder)

        clear_preview_state(clip)
        clip.last_preview_note = "Preview cache cleared"
        return {"FINISHED"}


class SPRITESHEET_OT_preview_size_preset(bpy.types.Operator):
    bl_idname = "spritesheet.preview_size_preset"
    bl_label = "Preview Size Preset"
    bl_options = {"REGISTER", "UNDO"}

    size: bpy.props.IntProperty(name="Size", default=64, min=32, max=256)

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = _active_workspace(context)
        clip = active_clip_or_none(workspace) if workspace is not None else None
        if clip is None:
            self.report({"WARNING"}, "No active clip")
            return {"CANCELLED"}
        clip.preview_size = max(32, min(self.size, 256))
        return {"FINISHED"}
