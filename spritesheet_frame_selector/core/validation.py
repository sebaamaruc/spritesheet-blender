"""Validation helpers for workspace-aware final render."""

from __future__ import annotations

from typing import Any

from .render_state import selected_frame_numbers
from .workspace_state import (
    default_collection_count_error,
    effective_camera_or_none,
    effective_collections,
    missing_effective_collection_names,
)


def validate_active_clip_render_context(workspace: Any | None, clip: Any | None) -> list[str]:
    """Return blocking validation messages for final render."""
    if workspace is None:
        return ["No active workspace"]
    if clip is None:
        return ["No active clip"]

    errors: list[str] = []
    if effective_camera_or_none(workspace, clip) is None:
        errors.append("Missing effective camera")

    collection_count_error = default_collection_count_error(workspace, clip)
    if collection_count_error:
        errors.append(collection_count_error)

    missing_collections = missing_effective_collection_names(workspace, clip)
    for name in missing_collections:
        errors.append(f"Missing collection: {name}")
    if not collection_count_error and not missing_collections and not effective_collections(workspace, clip):
        errors.append("Missing effective collections")

    if not selected_frame_numbers(clip):
        errors.append("No selected frames to render")

    settings = getattr(workspace, "export_settings", None)
    if settings is None:
        errors.append("Missing export settings")
    else:
        if getattr(settings, "frame_width", 0) < 1:
            errors.append("Frame width must be at least 1")
        if getattr(settings, "frame_height", 0) < 1:
            errors.append("Frame height must be at least 1")
        if not getattr(settings, "output_folder", ""):
            errors.append("Missing export output folder")

    return errors
