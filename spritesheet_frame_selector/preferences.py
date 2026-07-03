"""Addon preferences for SpriteSheet Frame Selector V2."""

from __future__ import annotations

import bpy


class SpriteSheetAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__ or "spritesheet_frame_selector"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.label(text="SpriteSheet Frame Selector V2 scaffold is installed.")
