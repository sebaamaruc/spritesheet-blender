"""Pure layout helpers for spritesheet export."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Iterable


MAX_SHEET_DIMENSION = 16384
"""Largest supported spritesheet width/height in pixels.

Composition materializes the full sheet as an in-memory pixel buffer,
so this bounds worst-case memory use to a documented ceiling instead of
letting arbitrarily large exports attempt to allocate unbounded buffers.
"""


@dataclass(frozen=True)
class SheetDimensions:
    width: int
    height: int
    rows: int


@dataclass(frozen=True)
class FrameRect:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class ClipRange:
    name: str
    start: int
    end: int
    count: int
    fps: int


@dataclass(frozen=True)
class ExportClip:
    name: str
    fps: int
    frame_paths: tuple[str, ...]


def sheet_dimensions(
    total_frames: int,
    frame_width: int,
    frame_height: int,
    columns: int,
    padding: int = 0,
    margin: int = 0,
) -> SheetDimensions:
    """Return final sheet dimensions for a uniform grid."""
    _validate_positive(frame_width, "frame_width")
    _validate_positive(frame_height, "frame_height")
    _validate_positive(columns, "columns")
    if total_frames < 0:
        raise ValueError("total_frames must be non-negative")
    if padding < 0:
        raise ValueError("padding must be non-negative")
    if margin < 0:
        raise ValueError("margin must be non-negative")

    rows = 0 if total_frames == 0 else ceil(total_frames / columns)
    used_columns = 0 if total_frames == 0 else columns
    width = margin * 2 + used_columns * frame_width + max(used_columns - 1, 0) * padding
    height = margin * 2 + rows * frame_height + max(rows - 1, 0) * padding
    return SheetDimensions(width=width, height=height, rows=rows)


def validate_sheet_dimension_limit(dimensions: SheetDimensions) -> str:
    """Return a blocking error message if the sheet exceeds ``MAX_SHEET_DIMENSION``."""
    if dimensions.width > MAX_SHEET_DIMENSION or dimensions.height > MAX_SHEET_DIMENSION:
        return (
            f"Spritesheet dimensions {dimensions.width}x{dimensions.height} exceed the "
            f"{MAX_SHEET_DIMENSION}x{MAX_SHEET_DIMENSION} limit"
        )
    return ""


def frame_rect(
    index: int,
    frame_width: int,
    frame_height: int,
    columns: int,
    padding: int = 0,
    margin: int = 0,
) -> FrameRect:
    """Return top-left based rect for a frame index in the sheet grid."""
    if index < 0:
        raise ValueError("index must be non-negative")
    _validate_positive(frame_width, "frame_width")
    _validate_positive(frame_height, "frame_height")
    _validate_positive(columns, "columns")
    if padding < 0:
        raise ValueError("padding must be non-negative")
    if margin < 0:
        raise ValueError("margin must be non-negative")

    column = index % columns
    row = index // columns
    return FrameRect(
        x=margin + column * (frame_width + padding),
        y=margin + row * (frame_height + padding),
        width=frame_width,
        height=frame_height,
    )


def clip_ranges(export_clips: Iterable[ExportClip]) -> list[ClipRange]:
    """Return global inclusive ranges for exported clips."""
    ranges: list[ClipRange] = []
    cursor = 0
    for clip in export_clips:
        count = len(clip.frame_paths)
        if count <= 0:
            raise ValueError(f"Clip {clip.name} has no frames to export")
        start = cursor
        end = cursor + count - 1
        ranges.append(
            ClipRange(
                name=clip.name,
                start=start,
                end=end,
                count=count,
                fps=clip.fps,
            )
        )
        cursor += count
    return ranges


def _validate_positive(value: int, name: str) -> None:
    if value < 1:
        raise ValueError(f"{name} must be at least 1")
