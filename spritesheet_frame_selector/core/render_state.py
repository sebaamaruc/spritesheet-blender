"""Pure helpers for final render state."""

from __future__ import annotations

import os
from typing import Any

from .paths import safe_file_prefix


def selected_frame_numbers(clip: Any) -> list[int]:
    """Return selected frame numbers in persistent frame order."""
    return [
        int(frame.frame_number)
        for frame in clip.frames
        if getattr(frame, "selected", False)
    ]


def render_output_file_name(output_index: int, sheet_name: str) -> str:
    """Return the exported PNG name for a 1-based output index."""
    prefix = safe_file_prefix(sheet_name or "spritesheet")
    return f"{prefix}_frame_{output_index:03d}.png"


def render_file_path(render_folder: str, output_index: int, sheet_name: str) -> str:
    """Return an export render path named by 1-based output index, not Blender frame."""
    return os.path.join(render_folder, render_output_file_name(output_index, sheet_name))

