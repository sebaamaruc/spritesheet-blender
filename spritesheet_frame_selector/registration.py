"""Centralized Blender registration for the V2 scaffold."""

from __future__ import annotations

import bpy

from .preferences import SpriteSheetAddonPreferences
from .properties import SpriteSheetSceneState
from .ui.panels import SPRITESHEET_PT_main


CLASSES = (
    SpriteSheetAddonPreferences,
    SpriteSheetSceneState,
    SPRITESHEET_PT_main,
)


_registered_classes: list[type] = []


def _register_scene_properties() -> None:
    if not hasattr(bpy.types.Scene, "spritesheet_state"):
        bpy.types.Scene.spritesheet_state = bpy.props.PointerProperty(type=SpriteSheetSceneState)


def _unregister_scene_properties() -> None:
    if hasattr(bpy.types.Scene, "spritesheet_state"):
        del bpy.types.Scene.spritesheet_state


def register() -> None:
    """Register classes and scene properties defensively."""
    for cls in CLASSES:
        if cls in _registered_classes:
            continue
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass
        _registered_classes.append(cls)

    _register_scene_properties()


def unregister() -> None:
    """Unregister scene properties and classes in reverse order."""
    _unregister_scene_properties()

    while _registered_classes:
        cls = _registered_classes.pop()
        try:
            bpy.utils.unregister_class(cls)
        except (RuntimeError, ValueError):
            pass
