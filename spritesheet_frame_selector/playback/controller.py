"""Runtime playback controller for cached frame previews."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import bpy

from .sequence import next_playback_index
from .sequence import playback_interval_seconds


@dataclass
class PlaybackSession:
    workspace_id: str
    clip_id: str
    frame_numbers: list[int]
    preview_paths: list[str]
    fps: int
    loop: bool
    current_index: int = 0
    status: str = "stopped"


_session: PlaybackSession | None = None
_timer_registered = False


def start_playback(
    *,
    workspace_id: str,
    clip_id: str,
    frame_numbers: list[int],
    preview_paths: list[str],
    fps: int,
    loop: bool = True,
) -> PlaybackSession:
    """Start or restart playback for an explicit workspace/clip snapshot."""
    if not frame_numbers or not preview_paths:
        raise ValueError("Playback requires at least one preview frame")
    if len(frame_numbers) != len(preview_paths):
        raise ValueError("Frame number and preview path counts must match")

    interval = playback_interval_seconds(fps)
    stop_playback()

    global _session
    _session = PlaybackSession(
        workspace_id=workspace_id,
        clip_id=clip_id,
        frame_numbers=list(frame_numbers),
        preview_paths=list(preview_paths),
        fps=fps,
        loop=loop,
        status="playing",
    )
    _register_timer(interval)
    _tag_redraw()
    return _session


def resume_playback() -> bool:
    if _session is None or _session.status != "paused":
        return False
    _session.status = "playing"
    _register_timer(playback_interval_seconds(_session.fps))
    _tag_redraw()
    return True


def pause_playback() -> bool:
    if _session is None or _session.status != "playing":
        return False
    _unregister_timer()
    _session.status = "paused"
    _tag_redraw()
    return True


def stop_playback() -> bool:
    global _session
    had_session = _session is not None
    _unregister_timer()
    _session = None
    _tag_redraw()
    return had_session


def cleanup_playback_resources() -> None:
    stop_playback()


def tick_playback() -> bool:
    """Advance one frame. Intended for tests and background validation."""
    if _session is None or _session.status != "playing":
        return False
    next_index = next_playback_index(
        _session.current_index,
        len(_session.frame_numbers),
        _session.loop,
    )
    if next_index is None:
        stop_playback()
        return False
    _session.current_index = next_index
    _tag_redraw()
    return True


def is_playing() -> bool:
    return _session is not None and _session.status == "playing"


def is_paused() -> bool:
    return _session is not None and _session.status == "paused"


def active_session() -> PlaybackSession | None:
    return _session


def active_session_matches(workspace_id: str, clip_id: str) -> bool:
    return (
        _session is not None
        and _session.workspace_id == workspace_id
        and _session.clip_id == clip_id
    )


def current_frame_number() -> int | None:
    if _session is None or not _session.frame_numbers:
        return None
    return _session.frame_numbers[_session.current_index]


def current_preview_path() -> str:
    if _session is None or not _session.preview_paths:
        return ""
    return _session.preview_paths[_session.current_index]


def active_session_summary() -> dict[str, Any]:
    if _session is None:
        return {
            "status": "stopped",
            "workspace_id": "",
            "clip_id": "",
            "current_frame": None,
            "frame_count": 0,
            "fps": 0,
            "loop": False,
        }
    return {
        "status": _session.status,
        "workspace_id": _session.workspace_id,
        "clip_id": _session.clip_id,
        "current_frame": current_frame_number(),
        "frame_count": len(_session.frame_numbers),
        "fps": _session.fps,
        "loop": _session.loop,
    }


def _register_timer(interval: float) -> None:
    global _timer_registered
    if _timer_registered:
        return
    bpy.app.timers.register(_timer_callback, first_interval=interval)
    _timer_registered = True


def _unregister_timer() -> None:
    global _timer_registered
    if not _timer_registered:
        return
    try:
        if bpy.app.timers.is_registered(_timer_callback):
            bpy.app.timers.unregister(_timer_callback)
    except ValueError:
        pass
    _timer_registered = False


def _timer_callback() -> float | None:
    global _timer_registered
    _timer_registered = False
    if _session is None or _session.status != "playing":
        return None
    if not _session_matches_context():
        stop_playback()
        return None
    if not tick_playback():
        return None
    _timer_registered = True
    return playback_interval_seconds(_session.fps) if _session is not None else None


def _session_matches_context() -> bool:
    if _session is None:
        return False
    try:
        scene = getattr(bpy.context, "scene", None)
        state = getattr(scene, "spritesheet_state", None) if scene is not None else None
        if state is None:
            return False
        workspace_index = getattr(state, "active_workspace_index", -1)
        if workspace_index < 0 or workspace_index >= len(state.workspaces):
            return False
        workspace = state.workspaces[workspace_index]
        if getattr(workspace, "id", "") != _session.workspace_id:
            return False
        clip_index = getattr(workspace, "active_clip_index", -1)
        if clip_index < 0 or clip_index >= len(workspace.clips):
            return False
        clip = workspace.clips[clip_index]
        return getattr(clip, "id", "") == _session.clip_id
    except Exception:
        return False


def _tag_redraw() -> None:
    try:
        window_manager = getattr(bpy.context, "window_manager", None)
        windows = getattr(window_manager, "windows", []) if window_manager is not None else []
        for window in windows:
            screen = getattr(window, "screen", None)
            areas = getattr(screen, "areas", []) if screen is not None else []
            for area in areas:
                area.tag_redraw()
    except Exception:
        pass
