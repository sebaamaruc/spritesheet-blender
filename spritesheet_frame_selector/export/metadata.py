"""Spritesheet metadata JSON helpers."""

from __future__ import annotations

from typing import Any, Iterable

from .layout import ClipRange


def build_spritesheet_metadata(
    sheet_name: str,
    frame_width: int,
    frame_height: int,
    columns: int,
    ranges: Iterable[ClipRange],
) -> dict[str, Any]:
    """Build metadata matching the approved simple JSON contract."""
    return {
        "sheet": sheet_name,
        "frameWidth": frame_width,
        "frameHeight": frame_height,
        "columns": columns,
        "clips": {
            clip_range.name: {
                "start": clip_range.start,
                "end": clip_range.end,
                "count": clip_range.count,
                "fps": clip_range.fps,
            }
            for clip_range in ranges
        },
    }
