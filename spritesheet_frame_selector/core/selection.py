"""Pure helpers for persistent frame selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FrameSelectionSummary:
    total: int
    selected: int
    previews: int


def selected_frame_count(clip: Any) -> int:
    return sum(1 for frame in clip.frames if frame.selected)


def preview_ready_count(clip: Any) -> int:
    return sum(1 for frame in clip.frames if getattr(frame, "preview_path", ""))


def set_all_frames_selected(clip: Any, selected: bool) -> None:
    for frame in clip.frames:
        frame.selected = selected
    _mark_render_dirty(clip)


def invert_frame_selection(clip: Any) -> None:
    for frame in clip.frames:
        frame.selected = not frame.selected
    _mark_render_dirty(clip)


def select_every_n_frames(clip: Any, n: int) -> None:
    if n < 1:
        raise ValueError("N must be at least 1")

    for index, frame in enumerate(clip.frames):
        frame.selected = index % n == 0
    _mark_render_dirty(clip)


def frame_selection_summary(clip: Any) -> FrameSelectionSummary:
    return FrameSelectionSummary(
        total=len(clip.frames),
        selected=selected_frame_count(clip),
        previews=preview_ready_count(clip),
    )


def _mark_render_dirty(clip: Any) -> None:
    if hasattr(clip, "render_dirty"):
        clip.render_dirty = True
