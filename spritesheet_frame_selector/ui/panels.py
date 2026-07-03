"""Minimal UI panel for the V2 scaffold."""

from __future__ import annotations

import bpy


class SPRITESHEET_PT_main(bpy.types.Panel):
    bl_label = "SpriteSheet"
    bl_idname = "SPRITESHEET_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SpriteSheet"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        state = getattr(context.scene, "spritesheet_state", None)

        layout.label(text="SpriteSheet Frame Selector V2")
        if state is None:
            layout.label(text="Scaffold state unavailable", icon="ERROR")
        else:
            layout.label(text="Scaffold ready", icon="CHECKMARK")
