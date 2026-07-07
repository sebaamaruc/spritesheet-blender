"""Visual selector operators."""

from __future__ import annotations

import bpy

from ..core.context import active_workspace
from ..core.selection import (
    invert_frame_selection,
    select_every_n_frames,
    set_all_frames_selected,
)
from ..core.workspace_state import (
    active_clip_or_none,
)
from ..ui.visual_selector import handle_visual_selector_event
from ..ui.visual_selector import open_visual_selector
from ..playback.controller import refresh_playback_session
from ..playback.sequence import playback_frame_numbers
from ..playback.sequence import playback_preview_paths


def _refresh_playback_after_selection(
    workspace: bpy.types.PropertyGroup | None,
    clip: bpy.types.PropertyGroup | None,
) -> None:
    if workspace is None or clip is None:
        return
    refresh_playback_session(
        workspace_id=workspace.id,
        clip_id=clip.id,
        frame_numbers=playback_frame_numbers(clip),
        preview_paths=playback_preview_paths(clip),
        fps=clip.fps,
    )


class SPRITESHEET_OT_visual_selector_open(bpy.types.Operator):
    bl_idname = "spritesheet.visual_selector_open"
    bl_label = "Open Visual Selector"
    bl_options = {"REGISTER"}

    _workspace_id: str = ""
    _clip_id: str = ""

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        workspace = active_workspace(context)
        clip = active_clip_or_none(workspace) if workspace is not None else None
        if workspace is None or clip is None:
            self.report({"WARNING"}, "No active workspace or clip")
            return {"CANCELLED"}
        if len(clip.frames) == 0:
            self.report({"WARNING"}, "No frames available. Generate previews first.")
            return {"CANCELLED"}

        self._workspace_id = workspace.id
        self._clip_id = clip.id
        if not open_visual_selector(self, context, self._workspace_id, self._clip_id):
            return {"CANCELLED"}
        return {"RUNNING_MODAL"}

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        result = handle_visual_selector_event(context, event)
        if result is not None:
            return result
        return {"RUNNING_MODAL", "PASS_THROUGH"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        self.report({"WARNING"}, "Visual selector must be opened from a 3D Viewport invoke context")
        return {"CANCELLED"}


class SPRITESHEET_OT_visual_selector_set_mode(bpy.types.Operator):
    bl_idname = "spritesheet.visual_selector_set_mode"
    bl_label = "Set Selector Mode"
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=(
            ("EDIT", "Edit", ""),
            ("PLAY", "Play", ""),
        ),
        default="EDIT",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = active_workspace(context)
        if workspace is None:
            self.report({"WARNING"}, "No active workspace")
            return {"CANCELLED"}
        workspace.selector_mode = self.mode
        return {"FINISHED"}


class SPRITESHEET_OT_frame_select_all(bpy.types.Operator):
    bl_idname = "spritesheet.frame_select_all"
    bl_label = "Select All"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = active_workspace(context)
        clip = active_clip_or_none(workspace) if workspace is not None else None
        if workspace is None or clip is None:
            self.report({"WARNING"}, "No active clip")
            return {"CANCELLED"}
        set_all_frames_selected(clip, True)
        _refresh_playback_after_selection(workspace, clip)
        return {"FINISHED"}


class SPRITESHEET_OT_frame_deselect_all(bpy.types.Operator):
    bl_idname = "spritesheet.frame_deselect_all"
    bl_label = "Deselect All"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = active_workspace(context)
        clip = active_clip_or_none(workspace) if workspace is not None else None
        if workspace is None or clip is None:
            self.report({"WARNING"}, "No active clip")
            return {"CANCELLED"}
        set_all_frames_selected(clip, False)
        _refresh_playback_after_selection(workspace, clip)
        return {"FINISHED"}


class SPRITESHEET_OT_frame_invert_selection(bpy.types.Operator):
    bl_idname = "spritesheet.frame_invert_selection"
    bl_label = "Invert Selection"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = active_workspace(context)
        clip = active_clip_or_none(workspace) if workspace is not None else None
        if workspace is None or clip is None:
            self.report({"WARNING"}, "No active clip")
            return {"CANCELLED"}
        invert_frame_selection(clip)
        _refresh_playback_after_selection(workspace, clip)
        return {"FINISHED"}


class SPRITESHEET_OT_frame_select_every_n(bpy.types.Operator):
    bl_idname = "spritesheet.frame_select_every_n"
    bl_label = "Select Every N"
    bl_options = {"REGISTER", "UNDO"}

    n: bpy.props.IntProperty(name="N", default=2, min=1)

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = active_workspace(context)
        clip = active_clip_or_none(workspace) if workspace is not None else None
        if workspace is None or clip is None:
            self.report({"WARNING"}, "No active clip")
            return {"CANCELLED"}
        try:
            select_every_n_frames(clip, self.n)
        except ValueError as exc:
            self.report({"WARNING"}, str(exc))
            return {"CANCELLED"}
        _refresh_playback_after_selection(workspace, clip)
        return {"FINISHED"}


class SPRITESHEET_OT_frame_toggle_selection(bpy.types.Operator):
    bl_idname = "spritesheet.frame_toggle_selection"
    bl_label = "Toggle Frame"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(name="Frame Index", default=-1)

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace = active_workspace(context)
        clip = active_clip_or_none(workspace) if workspace is not None else None
        if workspace is None or clip is None:
            self.report({"WARNING"}, "No active clip")
            return {"CANCELLED"}
        if not 0 <= self.index < len(clip.frames):
            self.report({"WARNING"}, "Frame index is out of range")
            return {"CANCELLED"}
        clip.frames[self.index].selected = not clip.frames[self.index].selected
        _refresh_playback_after_selection(workspace, clip)
        return {"FINISHED"}
