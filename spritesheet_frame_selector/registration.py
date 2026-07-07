"""Centralized Blender registration for SpriteSheet Frame Selector V2."""

from __future__ import annotations

import bpy
from bpy.app.handlers import persistent

from .operators.clips import (
    SPRITESHEET_OT_clip_add,
    SPRITESHEET_OT_clip_duplicate,
    SPRITESHEET_OT_clip_included_collection_add,
    SPRITESHEET_OT_clip_included_collection_remove,
    SPRITESHEET_OT_clip_move,
    SPRITESHEET_OT_clip_remove,
    SPRITESHEET_OT_clip_select,
)
from .operators.export import SPRITESHEET_OT_export_spritesheet
from .operators.preview import (
    SPRITESHEET_OT_preview_clear_cache,
    SPRITESHEET_OT_preview_generate,
    SPRITESHEET_OT_preview_regenerate,
    SPRITESHEET_OT_preview_size_preset,
)
from .operators.playback import (
    SPRITESHEET_OT_playback_pause,
    SPRITESHEET_OT_playback_play,
    SPRITESHEET_OT_playback_stop,
)
from .operators.visual_selector import (
    SPRITESHEET_OT_frame_deselect_all,
    SPRITESHEET_OT_frame_invert_selection,
    SPRITESHEET_OT_frame_select_all,
    SPRITESHEET_OT_frame_select_every_n,
    SPRITESHEET_OT_frame_toggle_selection,
    SPRITESHEET_OT_visual_selector_open,
    SPRITESHEET_OT_visual_selector_set_mode,
)
from .operators.workspaces import (
    SPRITESHEET_OT_workspace_add,
    SPRITESHEET_OT_workspace_default_collection_add,
    SPRITESHEET_OT_workspace_default_collection_remove,
    SPRITESHEET_OT_workspace_duplicate,
    SPRITESHEET_OT_workspace_move,
    SPRITESHEET_OT_workspace_remove,
    SPRITESHEET_OT_workspace_select,
)
from .preferences import SpriteSheetAddonPreferences
from .playback.controller import cleanup_playback_resources
from .properties import (
    SpriteSheetClip,
    SpriteSheetExportSettings,
    SpriteSheetFrameItem,
    SpriteSheetIncludedCollection,
    SpriteSheetSceneState,
    SpriteSheetWorkspace,
)
from .ui.lists import SPRITESHEET_UL_clips, SPRITESHEET_UL_workspaces
from .ui.panels import SPRITESHEET_MT_preview_size, SPRITESHEET_PT_main
from .ui.visual_selector import cleanup_visual_selector_resources


CLASSES = (
    SpriteSheetAddonPreferences,
    SpriteSheetIncludedCollection,
    SpriteSheetFrameItem,
    SpriteSheetExportSettings,
    SpriteSheetClip,
    SpriteSheetWorkspace,
    SpriteSheetSceneState,
    SPRITESHEET_UL_workspaces,
    SPRITESHEET_UL_clips,
    SPRITESHEET_OT_workspace_add,
    SPRITESHEET_OT_workspace_remove,
    SPRITESHEET_OT_workspace_duplicate,
    SPRITESHEET_OT_workspace_select,
    SPRITESHEET_OT_workspace_move,
    SPRITESHEET_OT_workspace_default_collection_add,
    SPRITESHEET_OT_workspace_default_collection_remove,
    SPRITESHEET_OT_clip_add,
    SPRITESHEET_OT_clip_remove,
    SPRITESHEET_OT_clip_duplicate,
    SPRITESHEET_OT_clip_select,
    SPRITESHEET_OT_clip_move,
    SPRITESHEET_OT_clip_included_collection_add,
    SPRITESHEET_OT_clip_included_collection_remove,
    SPRITESHEET_OT_export_spritesheet,
    SPRITESHEET_OT_preview_generate,
    SPRITESHEET_OT_preview_regenerate,
    SPRITESHEET_OT_preview_clear_cache,
    SPRITESHEET_OT_preview_size_preset,
    SPRITESHEET_OT_visual_selector_open,
    SPRITESHEET_OT_visual_selector_set_mode,
    SPRITESHEET_OT_frame_select_all,
    SPRITESHEET_OT_frame_deselect_all,
    SPRITESHEET_OT_frame_invert_selection,
    SPRITESHEET_OT_frame_select_every_n,
    SPRITESHEET_OT_frame_toggle_selection,
    SPRITESHEET_OT_playback_play,
    SPRITESHEET_OT_playback_pause,
    SPRITESHEET_OT_playback_stop,
    SPRITESHEET_MT_preview_size,
    SPRITESHEET_PT_main,
)


_registered_classes: list[type] = []


@persistent
def _cleanup_runtime_sessions_on_load(_dummy: object) -> None:
    cleanup_playback_resources()
    cleanup_visual_selector_resources()


def _register_scene_properties() -> None:
    if not hasattr(bpy.types.Scene, "spritesheet_state"):
        bpy.types.Scene.spritesheet_state = bpy.props.PointerProperty(type=SpriteSheetSceneState)


def _unregister_scene_properties() -> None:
    if hasattr(bpy.types.Scene, "spritesheet_state"):
        del bpy.types.Scene.spritesheet_state


def _register_file_load_handler() -> None:
    if _cleanup_runtime_sessions_on_load not in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.append(_cleanup_runtime_sessions_on_load)


def _unregister_file_load_handler() -> None:
    if _cleanup_runtime_sessions_on_load in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(_cleanup_runtime_sessions_on_load)


def register() -> None:
    """Register classes and scene properties, surfacing registration errors."""
    _register_file_load_handler()
    for cls in CLASSES:
        bpy.utils.register_class(cls)
        _registered_classes.append(cls)

    _register_scene_properties()


def unregister() -> None:
    """Unregister scene properties and classes in reverse order."""
    _unregister_file_load_handler()
    cleanup_playback_resources()
    cleanup_visual_selector_resources()
    _unregister_scene_properties()

    while _registered_classes:
        cls = _registered_classes.pop()
        try:
            bpy.utils.unregister_class(cls)
        except (RuntimeError, ValueError):
            pass
