"""Shared context helpers for workspace-root operators and UI."""

from __future__ import annotations

from typing import Any

from .workspace_state import active_clip_or_none, active_workspace_or_none


def scene_state(context: Any) -> Any | None:
    """Return the SpriteSheet scene state from a Blender-like context."""
    scene = getattr(context, "scene", None)
    if scene is None:
        return None
    return getattr(scene, "spritesheet_state", None)


def active_workspace(context: Any) -> Any | None:
    """Return the active workspace for ``context`` after clamping its index."""
    state = scene_state(context)
    if state is None:
        return None
    return active_workspace_or_none(state)


def active_clip(context: Any) -> Any | None:
    """Return the active clip for ``context`` after clamping owner indices."""
    workspace = active_workspace(context)
    if workspace is None:
        return None
    return active_clip_or_none(workspace)


def active_workspace_and_clip(context: Any) -> tuple[Any | None, Any | None]:
    """Return active workspace and clip for ``context``."""
    workspace = active_workspace(context)
    clip = active_clip_or_none(workspace) if workspace is not None else None
    return workspace, clip
