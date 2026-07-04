"""UI lists for SpriteSheet Frame Selector."""

from __future__ import annotations

import bpy

from ..core.frame_math import frame_count
from ..core.selection import selected_frame_count


class SPRITESHEET_UL_workspaces(bpy.types.UIList):
    """Native Blender list for workspaces."""

    def draw_item(
        self,
        context: bpy.types.Context,
        layout: bpy.types.UILayout,
        data: bpy.types.PropertyGroup,
        item: bpy.types.PropertyGroup,
        icon: int,
        active_data: bpy.types.PropertyGroup,
        active_propname: str,
        index: int,
    ) -> None:
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)
            row.prop(item, "name", text="", icon="WORKSPACE", emboss=False)
            row.label(text=f"{len(item.clips)} clips")
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class SPRITESHEET_UL_clips(bpy.types.UIList):
    """Native Blender list for clips."""

    def draw_item(
        self,
        context: bpy.types.Context,
        layout: bpy.types.UILayout,
        data: bpy.types.PropertyGroup,
        item: bpy.types.PropertyGroup,
        icon: int,
        active_data: bpy.types.PropertyGroup,
        active_propname: str,
        index: int,
    ) -> None:
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)
            row.prop(item, "include_in_export", text="")
            row.prop(item, "name", text="", icon="SEQUENCE", emboss=False)
            row.label(text=f"{_selected_or_expected_count(item)} selected")
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


def _selected_or_expected_count(clip: bpy.types.PropertyGroup) -> int:
    if len(clip.frames) > 0:
        return selected_frame_count(clip)
    try:
        return frame_count(clip.frame_start, clip.frame_end, clip.frame_step)
    except ValueError:
        return 0
