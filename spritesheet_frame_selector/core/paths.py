"""Path helpers for derived preview cache files."""

from __future__ import annotations

import os
import re
import tempfile


CACHE_ROOT_NAME = ".spritesheet_cache"
ADDON_CACHE_NAME = "spritesheet_frame_selector"
TEMP_CACHE_ROOT_NAME = "spritesheet_frame_selector_preview_cache"


def preview_cache_root(blend_filepath: str, temp_root: str | None = None) -> str:
    """Return the root folder for preview cache without creating it."""
    if blend_filepath:
        blend_dir = os.path.dirname(os.path.abspath(blend_filepath))
        return os.path.join(blend_dir, CACHE_ROOT_NAME, ADDON_CACHE_NAME)

    root = temp_root if temp_root is not None else tempfile.gettempdir()
    return os.path.join(os.path.abspath(root), TEMP_CACHE_ROOT_NAME)


def preview_cache_folder(
    cache_root: str,
    workspace_id: str,
    clip_id: str,
    cache_key: str,
) -> str:
    safe_workspace_id = safe_path_part(workspace_id or "workspace")
    safe_clip_id = safe_path_part(clip_id or "clip")
    safe_cache_key = safe_path_part(cache_key)
    return os.path.join(cache_root, safe_workspace_id, safe_clip_id, safe_cache_key)


def safe_path_part(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned.strip("._") or "unnamed"


def safe_file_prefix(value: str, fallback: str = "spritesheet") -> str:
    """Return a filesystem-safe basename prefix compatible with cache names."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned.strip("._") or fallback


def is_managed_cache_folder(path: str) -> bool:
    if not path:
        return False

    normalized = os.path.abspath(path)
    parts = normalized.split(os.sep)
    for index, part in enumerate(parts):
        if part == CACHE_ROOT_NAME and index + 1 < len(parts):
            if parts[index + 1] == ADDON_CACHE_NAME:
                return True

    temp_root = os.path.join(tempfile.gettempdir(), TEMP_CACHE_ROOT_NAME)
    try:
        return os.path.commonpath((normalized, temp_root)) == temp_root
    except ValueError:
        return False
