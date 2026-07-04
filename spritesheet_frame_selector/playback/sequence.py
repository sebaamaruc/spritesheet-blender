"""Pure playback sequence helpers for cached frame previews."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PlaybackReadySummary:
    selected: int
    ready: int
    missing_preview: int
    can_play: bool


def selected_playback_frames(clip: Any) -> list[Any]:
    """Return selected frames sorted by frame number."""
    return sorted(
        (frame for frame in clip.frames if getattr(frame, "selected", False)),
        key=lambda frame: getattr(frame, "frame_number", 0),
    )


def playback_frame_numbers(clip: Any) -> list[int]:
    return [frame.frame_number for frame in playback_ready_frames(clip)]


def playback_preview_paths(clip: Any) -> list[str]:
    return [frame.preview_path for frame in playback_ready_frames(clip)]


def playback_ready_frames(clip: Any) -> list[Any]:
    return [
        frame
        for frame in selected_playback_frames(clip)
        if getattr(frame, "preview_path", "")
    ]


def playback_interval_seconds(fps: int) -> float:
    if fps <= 0:
        raise ValueError("FPS must be greater than 0")
    return 1.0 / fps


def next_playback_index(current_index: int, frame_count: int, loop: bool) -> int | None:
    if frame_count <= 0:
        return None

    next_index = current_index + 1
    if next_index < frame_count:
        return next_index
    if loop:
        return 0
    return None


def playback_ready_summary(clip: Any) -> PlaybackReadySummary:
    selected = selected_playback_frames(clip)
    ready = [frame for frame in selected if getattr(frame, "preview_path", "")]
    missing_preview = len(selected) - len(ready)
    return PlaybackReadySummary(
        selected=len(selected),
        ready=len(ready),
        missing_preview=missing_preview,
        can_play=len(ready) > 0,
    )
