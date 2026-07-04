"""Pure helpers for final render state."""

from __future__ import annotations

import hashlib
import os
import re
from typing import Any, Iterable


RENDER_CACHE_VERSION = "final-render-workspace-v1"


def selected_frame_numbers(clip: Any) -> list[int]:
    """Return selected frame numbers in persistent frame order."""
    return [
        int(frame.frame_number)
        for frame in clip.frames
        if getattr(frame, "selected", False)
    ]


def build_render_key(
    workspace: Any,
    clip: Any,
    camera: Any | None,
    collections: Iterable[Any],
    export_settings: Any,
    frame_numbers: Iterable[int],
) -> str:
    """Build a stable render key without depending on visible item names."""
    camera_key = _id_key(camera)
    collection_keys = ",".join(sorted(_id_key(collection) for collection in collections))
    frames_key = ",".join(str(frame_number) for frame_number in frame_numbers)
    payload = "|".join(
        (
            RENDER_CACHE_VERSION,
            str(getattr(workspace, "id", "")),
            str(getattr(clip, "id", "")),
            str(getattr(clip, "frame_start", "")),
            str(getattr(clip, "frame_end", "")),
            str(getattr(clip, "frame_step", "")),
            frames_key,
            str(getattr(export_settings, "frame_width", "")),
            str(getattr(export_settings, "frame_height", "")),
            str(getattr(export_settings, "transparent", "")),
            camera_key,
            collection_keys,
        )
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def render_file_name(frame_number: int) -> str:
    return f"frame_{frame_number:03d}.png"


def render_output_file_name(frame_number: int, sheet_name: str) -> str:
    prefix = _safe_file_prefix(sheet_name or "spritesheet")
    return f"{prefix}_frame_{frame_number:03d}.png"


def render_file_path(render_folder: str, frame_number: int, sheet_name: str = "") -> str:
    if sheet_name:
        return os.path.join(render_folder, render_output_file_name(frame_number, sheet_name))
    return os.path.join(render_folder, render_file_name(frame_number))


def count_render_references(clip: Any) -> int:
    return sum(1 for frame in clip.frames if getattr(frame, "render_path", ""))


def count_existing_renders(clip: Any) -> int:
    return sum(
        1
        for frame in clip.frames
        if getattr(frame, "render_path", "") and os.path.isfile(frame.render_path)
    )


def clear_render_state(clip: Any) -> None:
    """Clear derived final render state without touching selection or previews."""
    for frame in clip.frames:
        if hasattr(frame, "render_path"):
            frame.render_path = ""
    clip.render_key = ""
    clip.render_folder = ""
    clip.render_dirty = True
    clip.last_render_note = ""


def render_warning(clip: Any, expected_render_key: str | None = None) -> str:
    if getattr(clip, "render_dirty", True):
        return "Final render needs refresh"
    if expected_render_key is not None and getattr(clip, "render_key", "") != expected_render_key:
        return "Final render is stale"
    selected = len(selected_frame_numbers(clip))
    if selected > 0 and count_render_references(clip) < selected:
        return "Some final renders are missing"
    return ""


def _id_key(item: Any | None) -> str:
    if item is None:
        return ""
    library = getattr(getattr(item, "library", None), "filepath", "")
    name = getattr(item, "name_full", getattr(item, "name", ""))
    return f"{library}:{name}"


def _safe_file_prefix(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned.strip("._") or "spritesheet"
