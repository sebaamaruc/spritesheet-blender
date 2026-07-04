"""Preview cache helpers."""

from __future__ import annotations

import hashlib
import os
from typing import Any


CACHE_VERSION = "preview-cache-workspace-v1"


def build_preview_cache_key(
    workspace: Any,
    clip: Any,
    camera: Any | None = None,
    collections: list[Any] | tuple[Any, ...] = (),
    preview_mode: str = "SOLID",
) -> str:
    """Build a stable cache key from workspace-aware thumbnail settings."""
    camera_name = getattr(camera, "name", "") if camera is not None else ""
    collection_keys = ",".join(
        sorted(
            getattr(collection, "name_full", getattr(collection, "name", ""))
            for collection in collections
        )
    )
    payload = "|".join(
        (
            CACHE_VERSION,
            str(getattr(workspace, "id", "")),
            str(getattr(clip, "id", "")),
            str(getattr(clip, "frame_start", "")),
            str(getattr(clip, "frame_end", "")),
            str(getattr(clip, "frame_step", "")),
            str(getattr(clip, "preview_size", "")),
            preview_mode,
            camera_name,
            collection_keys,
        )
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def preview_file_name(frame_number: int) -> str:
    return f"frame_{frame_number:03d}.png"


def preview_file_path(cache_folder: str, frame_number: int) -> str:
    return os.path.join(cache_folder, preview_file_name(frame_number))


def count_preview_references(clip: Any) -> int:
    return sum(1 for frame in clip.frames if getattr(frame, "preview_path", ""))


def count_existing_previews(clip: Any) -> int:
    return sum(
        1
        for frame in clip.frames
        if getattr(frame, "preview_path", "") and os.path.isfile(frame.preview_path)
    )


def clear_preview_state(clip: Any) -> None:
    for frame in clip.frames:
        frame.preview_path = ""
    clip.cache_key = ""
    clip.cache_folder = ""
    clip.cache_dirty = True
    clip.last_preview_note = ""


def cache_warning(clip: Any, expected_cache_key: str | None = None) -> str:
    if getattr(clip, "cache_dirty", True):
        return "Preview cache needs refresh"
    if expected_cache_key is not None and getattr(clip, "cache_key", "") != expected_cache_key:
        return "Preview cache is stale"
    if len(clip.frames) > 0 and count_preview_references(clip) < len(clip.frames):
        return "Some previews are missing"
    return ""
