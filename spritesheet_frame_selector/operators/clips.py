"""Workspace-root clip management operators."""

from __future__ import annotations

import uuid

import bpy

from ..core.frame_math import frame_numbers
from ..core.frame_sync import sync_clip_frames
from ..core.workspace_state import (
    active_clip_or_none,
    active_workspace_or_none,
    clamp_active_clip_index,
    duplicate_clip_data,
    move_item,
    next_item_name,
)


def _active_workspace(context: bpy.types.Context) -> bpy.types.PropertyGroup | None:
    scene = getattr(context, "scene", None)
    state = getattr(scene, "spritesheet_state", None) if scene is not None else None
    return active_workspace_or_none(state) if state is not None else None


class SPRITESHEET_OT_clip_add(bpy.types.Operator):
    bl_idname = "spritesheet.clip_add"
    bl_label = "Add Clip"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = _active_workspace(context)
        if workspace is None:
            self.report({"WARNING"}, "No active workspace")
            return {"CANCELLED"}

        existing_names = [workspace.clips[index].name for index in range(len(workspace.clips))]
        clip = workspace.clips.add()
        clip.id = uuid.uuid4().hex
        clip.name = next_item_name(existing_names, "Clip")
        clip.include_in_export = True
        clip.active_frame_index = -1
        clip.cache_dirty = True
        try:
            sync_clip_frames(clip, frame_numbers(clip.frame_start, clip.frame_end, clip.frame_step))
        except ValueError:
            pass
        workspace.active_clip_index = len(workspace.clips) - 1
        return {"FINISHED"}


class SPRITESHEET_OT_clip_remove(bpy.types.Operator):
    bl_idname = "spritesheet.clip_remove"
    bl_label = "Remove Clip"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = _active_workspace(context)
        if workspace is None:
            self.report({"WARNING"}, "No active workspace")
            return {"CANCELLED"}

        if len(workspace.clips) == 0:
            workspace.active_clip_index = -1
            return {"FINISHED"}

        index = clamp_active_clip_index(workspace)
        workspace.clips.remove(index)
        if len(workspace.clips) == 0:
            workspace.active_clip_index = -1
        else:
            workspace.active_clip_index = min(index, len(workspace.clips) - 1)
        return {"FINISHED"}


class SPRITESHEET_OT_clip_duplicate(bpy.types.Operator):
    bl_idname = "spritesheet.clip_duplicate"
    bl_label = "Duplicate Clip"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = _active_workspace(context)
        if workspace is None:
            self.report({"WARNING"}, "No active workspace")
            return {"CANCELLED"}

        source = active_clip_or_none(workspace)
        if source is None:
            self.report({"WARNING"}, "No active clip to duplicate")
            return {"CANCELLED"}

        existing_names = [workspace.clips[index].name for index in range(len(workspace.clips))]
        target = workspace.clips.add()
        duplicate_clip_data(source, target, new_id=uuid.uuid4().hex)
        target.name = next_item_name(existing_names, source.name)
        workspace.active_clip_index = len(workspace.clips) - 1
        return {"FINISHED"}


class SPRITESHEET_OT_clip_select(bpy.types.Operator):
    bl_idname = "spritesheet.clip_select"
    bl_label = "Select Clip"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(name="Index", default=-1)

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = _active_workspace(context)
        if workspace is None:
            self.report({"WARNING"}, "No active workspace")
            return {"CANCELLED"}

        workspace.active_clip_index = self.index
        clamp_active_clip_index(workspace)
        return {"FINISHED"}


class SPRITESHEET_OT_clip_move(bpy.types.Operator):
    bl_idname = "spritesheet.clip_move"
    bl_label = "Move Clip"
    bl_options = {"REGISTER", "UNDO"}

    direction: bpy.props.EnumProperty(
        name="Direction",
        items=(
            ("UP", "Up", "Move clip up"),
            ("DOWN", "Down", "Move clip down"),
        ),
        default="UP",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = _active_workspace(context)
        if workspace is None:
            self.report({"WARNING"}, "No active workspace")
            return {"CANCELLED"}
        if len(workspace.clips) < 2:
            clamp_active_clip_index(workspace)
            return {"FINISHED"}

        index = clamp_active_clip_index(workspace)
        target = index - 1 if self.direction == "UP" else index + 1
        workspace.active_clip_index = move_item(workspace.clips, index, target)
        return {"FINISHED"}


class SPRITESHEET_OT_clip_included_collection_add(bpy.types.Operator):
    bl_idname = "spritesheet.clip_included_collection_add"
    bl_label = "Add Clip Collection"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = _active_workspace(context)
        clip = active_clip_or_none(workspace) if workspace is not None else None
        if clip is None:
            self.report({"WARNING"}, "No active clip")
            return {"CANCELLED"}

        clip.included_collections.add()
        clip.cache_dirty = True
        return {"FINISHED"}


class SPRITESHEET_OT_clip_included_collection_remove(bpy.types.Operator):
    bl_idname = "spritesheet.clip_included_collection_remove"
    bl_label = "Remove Clip Collection"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(name="Index", default=-1)

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = _active_workspace(context)
        clip = active_clip_or_none(workspace) if workspace is not None else None
        if clip is None:
            self.report({"WARNING"}, "No active clip")
            return {"CANCELLED"}

        if 0 <= self.index < len(clip.included_collections):
            clip.included_collections.remove(self.index)
            clip.cache_dirty = True
        return {"FINISHED"}
