"""Pure frame range helpers."""

from __future__ import annotations


def frame_numbers(frame_start: int, frame_end: int, frame_step: int) -> list[int]:
    """Return frame numbers for an inclusive Blender frame range."""
    if frame_step < 1:
        raise ValueError("frame_step must be >= 1")
    if frame_end < frame_start:
        return []
    return list(range(frame_start, frame_end + 1, frame_step))


def frame_count(frame_start: int, frame_end: int, frame_step: int) -> int:
    """Return the number of frames for an inclusive Blender frame range."""
    return len(frame_numbers(frame_start, frame_end, frame_step))
