"""Playback preview operators."""

from __future__ import annotations

import bpy

from ..core.context import active_workspace_and_clip
from ..playback.controller import active_session_matches
from ..playback.controller import pause_playback
from ..playback.controller import resume_playback
from ..playback.controller import start_playback
from ..playback.controller import stop_playback
from ..playback.sequence import playback_frame_numbers
from ..playback.sequence import playback_preview_paths
from ..playback.sequence import playback_ready_summary


class SPRITESHEET_OT_playback_play(bpy.types.Operator):
    bl_idname = "spritesheet.playback_play"
    bl_label = "Play"
    bl_options = {"REGISTER"}

    loop: bpy.props.BoolProperty(name="Loop", default=True)

    def execute(self, context: bpy.types.Context) -> set[str]:
        workspace, clip = active_workspace_and_clip(context)
        if workspace is None or clip is None:
            self.report({"WARNING"}, "No active workspace or clip")
            return {"CANCELLED"}

        if active_session_matches(workspace.id, clip.id):
            if clip.fps <= 0:
                self.report({"WARNING"}, "Clip FPS must be greater than 0")
                return {"CANCELLED"}
            if resume_playback(fps=clip.fps):
                return {"FINISHED"}

        summary = playback_ready_summary(clip)
        if summary.selected == 0:
            self.report({"WARNING"}, "No selected frames to play")
            return {"CANCELLED"}
        if not summary.can_play:
            self.report({"WARNING"}, "Selected frames do not have preview paths")
            return {"CANCELLED"}
        if clip.fps <= 0:
            self.report({"WARNING"}, "Clip FPS must be greater than 0")
            return {"CANCELLED"}

        try:
            start_playback(
                workspace_id=workspace.id,
                clip_id=clip.id,
                frame_numbers=playback_frame_numbers(clip),
                preview_paths=playback_preview_paths(clip),
                fps=clip.fps,
                loop=self.loop,
            )
        except ValueError as exc:
            self.report({"WARNING"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


class SPRITESHEET_OT_playback_pause(bpy.types.Operator):
    bl_idname = "spritesheet.playback_pause"
    bl_label = "Pause"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        pause_playback()
        return {"FINISHED"}


class SPRITESHEET_OT_playback_stop(bpy.types.Operator):
    bl_idname = "spritesheet.playback_stop"
    bl_label = "Stop"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        stop_playback()
        return {"FINISHED"}
