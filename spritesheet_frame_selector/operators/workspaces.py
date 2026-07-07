"""Workspace management operators."""

from __future__ import annotations

import uuid

import bpy

from ..core.context import scene_state
from ..core.workspace_state import (
    active_workspace_or_none,
    clamp_active_workspace_index,
    duplicate_workspace_data,
    move_item,
    next_item_name,
)


class SPRITESHEET_OT_workspace_add(bpy.types.Operator):
    bl_idname = "spritesheet.workspace_add"
    bl_label = "Add Workspace"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        state = scene_state(context)
        if state is None:
            self.report({"ERROR"}, "SpriteSheet scene state is unavailable")
            return {"CANCELLED"}

        existing_names = [state.workspaces[index].name for index in range(len(state.workspaces))]
        workspace = state.workspaces.add()
        workspace.id = uuid.uuid4().hex
        workspace.name = next_item_name(existing_names, "Workspace")
        workspace.active_clip_index = -1
        state.active_workspace_index = len(state.workspaces) - 1
        return {"FINISHED"}


class SPRITESHEET_OT_workspace_remove(bpy.types.Operator):
    bl_idname = "spritesheet.workspace_remove"
    bl_label = "Remove Workspace"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        state = scene_state(context)
        if state is None:
            self.report({"ERROR"}, "SpriteSheet scene state is unavailable")
            return {"CANCELLED"}

        if len(state.workspaces) == 0:
            state.active_workspace_index = -1
            return {"FINISHED"}

        index = clamp_active_workspace_index(state)
        state.workspaces.remove(index)
        if len(state.workspaces) == 0:
            state.active_workspace_index = -1
        else:
            state.active_workspace_index = min(index, len(state.workspaces) - 1)
        return {"FINISHED"}


class SPRITESHEET_OT_workspace_duplicate(bpy.types.Operator):
    bl_idname = "spritesheet.workspace_duplicate"
    bl_label = "Duplicate Workspace"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        state = scene_state(context)
        if state is None:
            self.report({"ERROR"}, "SpriteSheet scene state is unavailable")
            return {"CANCELLED"}

        source = active_workspace_or_none(state)
        if source is None:
            self.report({"WARNING"}, "No active workspace to duplicate")
            return {"CANCELLED"}

        existing_names = [state.workspaces[index].name for index in range(len(state.workspaces))]
        target = state.workspaces.add()
        duplicate_workspace_data(
            source,
            target,
            new_workspace_id=uuid.uuid4().hex,
            clip_id_factory=lambda: uuid.uuid4().hex,
        )
        target.name = next_item_name(existing_names, source.name)
        state.active_workspace_index = len(state.workspaces) - 1
        return {"FINISHED"}


class SPRITESHEET_OT_workspace_select(bpy.types.Operator):
    bl_idname = "spritesheet.workspace_select"
    bl_label = "Select Workspace"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(name="Index", default=-1)

    def execute(self, context: bpy.types.Context) -> set[str]:
        state = scene_state(context)
        if state is None:
            self.report({"ERROR"}, "SpriteSheet scene state is unavailable")
            return {"CANCELLED"}

        state.active_workspace_index = self.index
        clamp_active_workspace_index(state)
        return {"FINISHED"}


class SPRITESHEET_OT_workspace_move(bpy.types.Operator):
    bl_idname = "spritesheet.workspace_move"
    bl_label = "Move Workspace"
    bl_options = {"REGISTER", "UNDO"}

    direction: bpy.props.EnumProperty(
        name="Direction",
        items=(
            ("UP", "Up", "Move workspace up"),
            ("DOWN", "Down", "Move workspace down"),
        ),
        default="UP",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        state = scene_state(context)
        if state is None:
            self.report({"ERROR"}, "SpriteSheet scene state is unavailable")
            return {"CANCELLED"}
        if len(state.workspaces) < 2:
            clamp_active_workspace_index(state)
            return {"FINISHED"}

        index = clamp_active_workspace_index(state)
        target = index - 1 if self.direction == "UP" else index + 1
        state.active_workspace_index = move_item(state.workspaces, index, target)
        return {"FINISHED"}


class SPRITESHEET_OT_workspace_default_collection_add(bpy.types.Operator):
    bl_idname = "spritesheet.workspace_default_collection_add"
    bl_label = "Add Default Collection"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        state = scene_state(context)
        workspace = active_workspace_or_none(state) if state is not None else None
        if workspace is None:
            self.report({"WARNING"}, "No active workspace")
            return {"CANCELLED"}
        if len(workspace.default_collections) >= 1:
            self.report({"WARNING"}, "Workspace already has a default collection")
            return {"CANCELLED"}

        workspace.default_collections.add()
        for clip in workspace.clips:
            clip.cache_dirty = True
        return {"FINISHED"}


class SPRITESHEET_OT_workspace_default_collection_remove(bpy.types.Operator):
    bl_idname = "spritesheet.workspace_default_collection_remove"
    bl_label = "Remove Default Collection"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(name="Index", default=-1)

    def execute(self, context: bpy.types.Context) -> set[str]:
        state = scene_state(context)
        workspace = active_workspace_or_none(state) if state is not None else None
        if workspace is None:
            self.report({"WARNING"}, "No active workspace")
            return {"CANCELLED"}

        if 0 <= self.index < len(workspace.default_collections):
            workspace.default_collections.remove(self.index)
            for clip in workspace.clips:
                clip.cache_dirty = True
        return {"FINISHED"}
