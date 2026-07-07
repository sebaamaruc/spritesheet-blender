"""Synchronize persistent frame items with expected frame numbers."""

from __future__ import annotations

from typing import Any, Iterable

from .workspace_state import clear_collection


def sync_clip_frames(clip: Any, expected_frame_numbers: Iterable[int]) -> None:
    """Rebuild ``clip.frames`` while preserving selection by frame number."""
    previous = {
        frame.frame_number: {
            "selected": frame.selected,
            "preview_path": frame.preview_path,
        }
        for frame in clip.frames
    }

    clear_collection(clip.frames)
    for frame_number in expected_frame_numbers:
        item = clip.frames.add()
        item.frame_number = frame_number
        if frame_number in previous:
            item.selected = previous[frame_number]["selected"]
            item.preview_path = previous[frame_number]["preview_path"]
        else:
            item.selected = True
            item.preview_path = ""

    if not 0 <= clip.active_frame_index < len(clip.frames):
        clip.active_frame_index = -1
