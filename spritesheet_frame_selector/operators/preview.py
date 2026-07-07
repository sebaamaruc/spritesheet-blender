"""Preview cache operators."""

from __future__ import annotations

import os
import re
import shutil

import bpy

from ..core.cache import (
    build_preview_cache_key,
    clear_preview_state,
    count_existing_previews,
)
from ..core.context import active_workspace
from ..core.frame_math import frame_numbers
from ..core.frame_sync import sync_clip_frames
from ..core.paths import (
    is_managed_cache_folder,
    preview_cache_folder,
    preview_cache_root,
    safe_path_part,
)
from ..core.progress import progress_scope
from ..core.validation import validate_preview_context
from ..core.workspace_state import (
    active_clip_or_none,
    effective_camera_or_none,
    effective_collections,
    effective_preview_mode,
)
from ..preview.generator import generate_viewport_previews
from ..ui.visual_selector import notify_preview_cache_regenerated


def _expected_frames(clip: bpy.types.PropertyGroup) -> list[int]:
    return frame_numbers(clip.frame_start, clip.frame_end, clip.frame_step)


def _generate_preview_cache(
    operator: bpy.types.Operator,
    context: bpy.types.Context,
    *,
    force: bool,
) -> set[str]:
    workspace = active_workspace(context)
    if workspace is None:
        operator.report({"WARNING"}, "No active workspace")
        return {"CANCELLED"}

    clip = active_clip_or_none(workspace)
    if clip is None:
        operator.report({"WARNING"}, "No active clip")
        return {"CANCELLED"}

    context_errors = validate_preview_context(workspace, clip)
    if context_errors:
        clip.cache_dirty = True
        clip.last_preview_note = context_errors[0]
        operator.report({"WARNING"}, clip.last_preview_note)
        return {"CANCELLED"}

    camera = effective_camera_or_none(workspace, clip)
    collections = effective_collections(workspace, clip)

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
    preview_mode = effective_preview_mode(clip)
    cache_key = build_preview_cache_key(workspace, clip, camera, collections, preview_mode)
    cache_root = preview_cache_root(bpy.data.filepath)
    cache_folder = preview_cache_folder(cache_root, workspace.id, clip.id, cache_key)

    if force and os.path.isdir(cache_folder):
        shutil.rmtree(cache_folder)

    with progress_scope(context, len(expected_frames)) as progress:
        result = generate_viewport_previews(
            context,
            clip,
            camera,
            collections,
            cache_folder,
            expected_frames,
            force=force,
            preview_mode=preview_mode,
            progress_callback=progress.step,
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
    if result.alpha_warning:
        clip.last_preview_note = f"{clip.last_preview_note}; {result.message}"
    _purge_sibling_preview_caches(cache_root, workspace.id, clip.id, cache_key)
    notify_preview_cache_regenerated(workspace.id, clip.id)
    return {"FINISHED"}


class SPRITESHEET_OT_preview_generate(bpy.types.Operator):
    bl_idname = "spritesheet.preview_generate"
    bl_label = "Generate Preview"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        return _generate_preview_cache(self, context, force=False)


class SPRITESHEET_OT_preview_regenerate(bpy.types.Operator):
    bl_idname = "spritesheet.preview_regenerate"
    bl_label = "Regenerate Preview"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        return _generate_preview_cache(self, context, force=True)


class SPRITESHEET_OT_preview_clear_cache(bpy.types.Operator):
    bl_idname = "spritesheet.preview_clear_cache"
    bl_label = "Clear Cache"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = active_workspace(context)
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


def _purge_sibling_preview_caches(
    cache_root: str,
    workspace_id: str,
    clip_id: str,
    current_cache_key: str,
) -> None:
    clip_cache_root = os.path.join(
        cache_root,
        safe_path_part(workspace_id or "workspace"),
        safe_path_part(clip_id or "clip"),
    )
    if not os.path.isdir(clip_cache_root):
        return

    current_name = safe_path_part(current_cache_key)
    for entry_name in os.listdir(clip_cache_root):
        if entry_name == current_name:
            continue
        entry_path = os.path.join(clip_cache_root, entry_name)
        if not os.path.isdir(entry_path):
            continue
        if _is_cache_key_folder_name(entry_name) and is_managed_cache_folder(entry_path):
            shutil.rmtree(entry_path)


def _is_cache_key_folder_name(name: str) -> bool:
    return re.fullmatch(r"[0-9a-f]{16}", name) is not None


class SPRITESHEET_OT_preview_size_preset(bpy.types.Operator):
    bl_idname = "spritesheet.preview_size_preset"
    bl_label = "Preview Size Preset"
    bl_options = {"REGISTER", "UNDO"}

    size: bpy.props.IntProperty(name="Size", default=64, min=32, max=256)

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = active_workspace(context)
        clip = active_clip_or_none(workspace) if workspace is not None else None
        if clip is None:
            self.report({"WARNING"}, "No active clip")
            return {"CANCELLED"}
        clip.preview_size = max(32, min(self.size, 256))
        return {"FINISHED"}
