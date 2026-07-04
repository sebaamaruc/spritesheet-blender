"""Synchronize persistent frame items with expected frame numbers."""

from __future__ import annotations

from typing import Any, Iterable


def sync_clip_frames(clip: Any, expected_frame_numbers: Iterable[int]) -> None:
    """Rebuild ``clip.frames`` while preserving selection by frame number."""
    previous = {
        frame.frame_number: {
            "selected": frame.selected,
            "preview_path": frame.preview_path,
            "render_path": getattr(frame, "render_path", ""),
            "original_index": frame.original_index,
        }
        for frame in clip.frames
    }

    _clear_collection(clip.frames)
    for index, frame_number in enumerate(expected_frame_numbers):
        item = clip.frames.add()
        item.frame_number = frame_number
        if frame_number in previous:
            item.selected = previous[frame_number]["selected"]
            item.preview_path = previous[frame_number]["preview_path"]
            if hasattr(item, "render_path"):
                item.render_path = previous[frame_number]["render_path"]
            item.original_index = previous[frame_number]["original_index"]
        else:
            item.selected = True
            item.preview_path = ""
            if hasattr(item, "render_path"):
                item.render_path = ""
            item.original_index = index

    if not 0 <= clip.active_frame_index < len(clip.frames):
        clip.active_frame_index = -1


def _clear_collection(collection: Any) -> None:
    if hasattr(collection, "clear"):
        collection.clear()
        return

    while len(collection) > 0:
        collection.remove(0)
