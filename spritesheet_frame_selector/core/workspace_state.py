"""Pure helpers for workspace-root active state."""

from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Callable
from typing import Any


def active_workspace_or_none(state: Any) -> Any | None:
    """Return the active workspace after clamping the active index."""
    index = clamp_active_workspace_index(state)
    if index < 0:
        return None
    return state.workspaces[index]


def workspace_at_active_index_or_none(state: Any) -> Any | None:
    """Return the active workspace without mutating the owner index."""
    index = _bounded_index_or_none(state, "workspaces", "active_workspace_index")
    if index is None:
        return None
    return state.workspaces[index]


def clamp_active_workspace_index(state: Any) -> int:
    """Clamp ``state.active_workspace_index`` to available workspaces."""
    return _clamp_owner_index(state, "workspaces", "active_workspace_index")


def active_clip_or_none(workspace: Any) -> Any | None:
    """Return the active clip from a workspace after clamping the index."""
    index = clamp_active_clip_index(workspace)
    if index < 0:
        return None
    return workspace.clips[index]


def clip_at_active_index_or_none(workspace: Any) -> Any | None:
    """Return the active clip without mutating the owner index."""
    index = _bounded_index_or_none(workspace, "clips", "active_clip_index")
    if index is None:
        return None
    return workspace.clips[index]


def effective_camera_or_none(workspace: Any, clip: Any) -> Any | None:
    """Return the explicit camera resolved from clip override or workspace default."""
    if getattr(clip, "use_camera_override", False):
        return getattr(clip, "camera", None)
    return getattr(workspace, "default_camera", None)


def effective_collection_items(workspace: Any, clip: Any) -> Any:
    """Return collection pointer items resolved from clip override or workspace defaults."""
    if getattr(clip, "use_collection_override", False):
        return getattr(clip, "included_collections")
    return getattr(workspace, "default_collections")


def effective_collections(workspace: Any, clip: Any) -> list[Any]:
    """Return non-null effective collection pointers."""
    return [
        item.collection
        for item in effective_collection_items(workspace, clip)
        if getattr(item, "collection", None) is not None
    ]


def effective_preview_mode(workspace: Any, clip: Any) -> str:
    """Return the clip preview mode used for on-demand preview generation."""
    return getattr(clip, "preview_mode", "SOLID")


def missing_effective_collection_names(workspace: Any, clip: Any) -> list[str]:
    """Return last-known names for effective collection references that are missing."""
    return [
        item.collection_name
        for item in effective_collection_items(workspace, clip)
        if getattr(item, "collection", None) is None and getattr(item, "collection_name", "")
    ]


def default_collection_count_error(workspace: Any, clip: Any) -> str:
    """Return an error when workspace defaults contain unsupported multiple collections."""
    if getattr(clip, "use_collection_override", False):
        return ""
    if len(getattr(workspace, "default_collections", ())) > 1:
        return "Workspace supports only one default collection"
    return ""


def preview_context_warnings(workspace: Any | None, clip: Any | None) -> list[str]:
    """Return passive validation warnings for workspace-aware preview generation."""
    if workspace is None:
        return ["No active workspace"]
    if clip is None:
        return ["No active clip"]

    warnings: list[str] = []
    if effective_camera_or_none(workspace, clip) is None:
        warnings.append("Missing effective camera")
    collection_count_error = default_collection_count_error(workspace, clip)
    if collection_count_error:
        warnings.append(collection_count_error)
    if not effective_collections(workspace, clip):
        warnings.append("Missing effective collections")
    for name in missing_effective_collection_names(workspace, clip):
        warnings.append(f"Missing collection: {name}")
    return warnings


def clamp_active_clip_index(workspace: Any) -> int:
    """Clamp ``workspace.active_clip_index`` to available workspace clips."""
    return _clamp_owner_index(workspace, "clips", "active_clip_index")


def next_item_name(existing_names: Iterable[str], base: str) -> str:
    """Return ``base`` or the next available ``base N`` name."""
    clean_base = base.strip() or "Item"
    names = set(existing_names)
    if clean_base not in names:
        return clean_base

    suffix = 2
    while f"{clean_base} {suffix}" in names:
        suffix += 1
    return f"{clean_base} {suffix}"


def unique_item_name_at_index(
    collection: Any,
    index: int,
    desired_name: str,
    *,
    fallback: str = "Item",
) -> str:
    """Return a unique name for ``collection[index]`` among sibling items."""
    base = desired_name.strip() or fallback
    existing_names = [
        item.name
        for item_index, item in enumerate(collection)
        if item_index != index
    ]
    return next_item_name(existing_names, base)


def move_item(collection: Any, from_index: int, to_index: int) -> int:
    """Move an item in a Blender-like collection and return the final index."""
    count = len(collection)
    if count == 0:
        return -1
    source = max(0, min(from_index, count - 1))
    target = max(0, min(to_index, count - 1))
    if source == target:
        return target
    collection.move(source, target)
    return target


def duplicate_clip_data(source: Any, target: Any, *, new_id: str = "") -> None:
    """Copy user-authored clip data while invalidating derived cache state."""
    target.id = new_id
    target.name = source.name
    target.include_in_export = source.include_in_export
    target.frame_start = source.frame_start
    target.frame_end = source.frame_end
    target.frame_step = source.frame_step
    target.fps = source.fps
    target.use_camera_override = source.use_camera_override
    target.camera = source.camera
    target.use_collection_override = source.use_collection_override
    target.preview_mode = getattr(source, "preview_mode", "SOLID")
    target.preview_size = source.preview_size
    target.active_frame_index = source.active_frame_index

    _copy_included_collections(source.included_collections, target.included_collections)
    _clear_collection(target.frames)
    for source_frame in source.frames:
        target_frame = target.frames.add()
        target_frame.frame_number = source_frame.frame_number
        target_frame.selected = source_frame.selected
        target_frame.preview_path = ""
        if hasattr(target_frame, "render_path"):
            target_frame.render_path = ""
        target_frame.original_index = source_frame.original_index

    clear_clip_cache_state(target)
    clear_clip_render_state(target)


def duplicate_workspace_data(
    source: Any,
    target: Any,
    *,
    new_workspace_id: str = "",
    clip_id_factory: Callable[[], str] | None = None,
) -> None:
    """Copy workspace data while assigning new IDs and invalidating derived cache."""
    target.id = new_workspace_id
    target.name = source.name
    target.default_camera = source.default_camera
    target.active_clip_index = source.active_clip_index
    target.selector_mode = getattr(source, "selector_mode", "EDIT")

    _copy_included_collections(source.default_collections, target.default_collections)
    _copy_export_settings(source.export_settings, target.export_settings)

    _clear_collection(target.clips)
    for source_clip in source.clips:
        target_clip = target.clips.add()
        duplicate_clip_data(
            source_clip,
            target_clip,
            new_id=clip_id_factory() if clip_id_factory is not None else "",
        )

    clamp_active_clip_index(target)


def clear_clip_cache_state(clip: Any) -> None:
    """Clear derived cache fields without removing persistent frame selection."""
    for frame in clip.frames:
        frame.preview_path = ""
    clip.cache_key = ""
    clip.cache_folder = ""
    clip.cache_dirty = True
    clip.last_preview_note = ""


def clear_clip_render_state(clip: Any) -> None:
    """Clear derived final render fields without removing persistent selection."""
    for frame in clip.frames:
        if hasattr(frame, "render_path"):
            frame.render_path = ""
    if hasattr(clip, "render_key"):
        clip.render_key = ""
    if hasattr(clip, "render_folder"):
        clip.render_folder = ""
    if hasattr(clip, "render_dirty"):
        clip.render_dirty = True
    if hasattr(clip, "last_render_note"):
        clip.last_render_note = ""


def _clamp_owner_index(owner: Any, collection_name: str, index_name: str) -> int:
    collection = getattr(owner, collection_name)
    index = getattr(owner, index_name)
    item_count = len(collection)

    if item_count == 0:
        index = -1
    elif index < 0:
        index = 0
    elif index >= item_count:
        index = item_count - 1

    if getattr(owner, index_name) != index:
        setattr(owner, index_name, index)
    return index


def _bounded_index_or_none(
    owner: Any,
    collection_name: str,
    index_name: str,
) -> int | None:
    collection = getattr(owner, collection_name)
    index = getattr(owner, index_name)
    if len(collection) == 0 or index < 0 or index >= len(collection):
        return None
    return index


def _copy_included_collections(source_collection: Any, target_collection: Any) -> None:
    _clear_collection(target_collection)
    for source_item in source_collection:
        target_item = target_collection.add()
        target_item.collection = source_item.collection
        target_item.collection_name = source_item.collection_name


def _copy_export_settings(source: Any, target: Any) -> None:
    target.frame_width = source.frame_width
    target.frame_height = source.frame_height
    target.columns = source.columns
    target.padding = source.padding
    target.margin = source.margin
    target.transparent = source.transparent
    target.output_folder = source.output_folder
    target.sheet_name = source.sheet_name
    target.export_png_sequence = source.export_png_sequence
    target.png_sequence_folder = source.png_sequence_folder


def _clear_collection(collection: Any) -> None:
    if hasattr(collection, "clear"):
        collection.clear()
        return

    while len(collection) > 0:
        collection.remove(0)
