"""Persistent properties for the V2 scaffold."""

from __future__ import annotations

import bpy


class SpriteSheetSceneState(bpy.types.PropertyGroup):
    scaffold_ready: bpy.props.BoolProperty(
        name="Scaffold Ready",
        description="Internal marker used to validate the V2 scaffold lifecycle",
        default=True,
    )
