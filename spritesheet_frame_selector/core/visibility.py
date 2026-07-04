"""Reversible collection visibility helpers for preview/render operations."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import bpy


@contextmanager
def collection_visibility_scope(
    view_layer: bpy.types.ViewLayer,
    collections: list[bpy.types.Collection],
    camera: bpy.types.Object | None,
) -> Iterator[None]:
    """Temporarily whitelist collections and restore LayerCollection state."""
    root = view_layer.layer_collection
    snapshot: dict[bpy.types.LayerCollection, bool] = {}
    for layer_collection in _walk_layer_collections(root):
        snapshot[layer_collection] = layer_collection.exclude

    visible_collections = _expanded_visible_collections(collections, camera)
    try:
        _apply_visibility(root, visible_collections, is_root=True)
        yield
    finally:
        for layer_collection, exclude in snapshot.items():
            layer_collection.exclude = exclude


def _expanded_visible_collections(
    collections: list[bpy.types.Collection],
    camera: bpy.types.Object | None,
) -> set[bpy.types.Collection]:
    visible: set[bpy.types.Collection] = set()
    for collection in collections:
        _add_collection_tree(collection, visible)
    if camera is not None:
        for collection in getattr(camera, "users_collection", ()):
            visible.add(collection)
    return visible


def _add_collection_tree(
    collection: bpy.types.Collection,
    visible: set[bpy.types.Collection],
) -> None:
    visible.add(collection)
    for child in collection.children:
        _add_collection_tree(child, visible)


def _apply_visibility(
    layer_collection: bpy.types.LayerCollection,
    visible_collections: set[bpy.types.Collection],
    *,
    is_root: bool = False,
) -> bool:
    collection = layer_collection.collection
    descendant_visible = False
    for child in layer_collection.children:
        descendant_visible = (
            _apply_visibility(child, visible_collections) or descendant_visible
        )

    self_visible = collection in visible_collections
    should_show = is_root or self_visible or descendant_visible
    if not is_root:
        layer_collection.exclude = not should_show
    return should_show


def _walk_layer_collections(
    layer_collection: bpy.types.LayerCollection,
) -> Iterator[bpy.types.LayerCollection]:
    yield layer_collection
    for child in layer_collection.children:
        yield from _walk_layer_collections(child)
