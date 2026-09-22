"""Shared helpers for Blender-in-process integration tests.

These tests run inside a real Blender (``blender -b --python run_all.py``),
not against the ``bpy`` stub used by ``tests/*.py``.
"""

from __future__ import annotations

import os
import sys

import bpy


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def reset_scene() -> None:
    """Return to a clean factory-like file without touching addon registration."""
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_camera(name: str = "TestCam") -> bpy.types.Object:
    camera_data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, camera_data)
    camera.location = (0.0, -6.0, 0.0)
    camera.rotation_euler = (1.5707963, 0.0, 0.0)
    return camera


def make_collection_with_cube(
    collection_name: str = "Props",
    object_name: str = "Cube",
) -> tuple[bpy.types.Collection, bpy.types.Object]:
    collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(collection)

    mesh = bpy.data.meshes.new(object_name)
    verts = [(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1)]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.update()
    obj = bpy.data.objects.new(object_name, mesh)
    collection.objects.link(obj)
    return collection, obj


def link_camera(camera: bpy.types.Object, collection: bpy.types.Collection | None = None) -> None:
    target = collection if collection is not None else bpy.context.scene.collection
    target.objects.link(camera)


def new_workspace(name: str | None = None) -> bpy.types.PropertyGroup:
    bpy.ops.spritesheet.workspace_add()
    workspace = bpy.context.scene.spritesheet_state.workspaces[-1]
    if name is not None:
        workspace.name = name
    return workspace


def new_clip(name: str | None = None) -> bpy.types.PropertyGroup:
    bpy.ops.spritesheet.clip_add()
    workspace = active_workspace()
    clip = workspace.clips[workspace.active_clip_index]
    if name is not None:
        clip.name = name
    return clip


def active_workspace() -> bpy.types.PropertyGroup:
    state = bpy.context.scene.spritesheet_state
    return state.workspaces[state.active_workspace_index]


def set_workspace_defaults(
    workspace: bpy.types.PropertyGroup,
    camera: bpy.types.Object,
    collection: bpy.types.Collection,
) -> None:
    workspace.default_camera = camera
    bpy.ops.spritesheet.workspace_default_collection_add()
    workspace.default_collections[0].collection = collection


def configure_export(
    workspace: bpy.types.PropertyGroup,
    output_folder: str,
    *,
    sheet_name: str = "sheet",
    frame_width: int = 16,
    frame_height: int = 16,
    columns: int = 4,
    padding: int = 0,
    margin: int = 0,
    transparent: bool = True,
    export_png_sequence: bool = False,
) -> None:
    settings = workspace.export_settings
    settings.output_folder = output_folder
    settings.sheet_name = sheet_name
    settings.frame_width = frame_width
    settings.frame_height = frame_height
    settings.columns = columns
    settings.padding = padding
    settings.margin = margin
    settings.transparent = transparent
    settings.export_png_sequence = export_png_sequence


def use_fast_render_engine() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_percentage = 100


def write_solid_png(path: str, width: int, height: int, rgba: tuple[float, float, float, float]) -> None:
    """Write a solid-colour PNG through Blender's own image pipeline."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    image = bpy.data.images.new("solid_src", width=width, height=height, alpha=True)
    try:
        image.pixels.foreach_set(list(rgba) * (width * height))
        image.filepath_raw = path
        image.file_format = "PNG"
        image.save()
    finally:
        bpy.data.images.remove(image)


def read_png_pixels(path: str) -> tuple[list[float], int, int]:
    """Return (pixels, width, height) for a PNG using Blender's loader."""
    image = bpy.data.images.load(path, check_existing=False)
    try:
        width, height = int(image.size[0]), int(image.size[1])
        pixels = [0.0] * len(image.pixels)
        image.pixels.foreach_get(pixels)
        return pixels, width, height
    finally:
        bpy.data.images.remove(image)


def pixel_at(pixels: list[float], width: int, height: int, x: int, y_top: int) -> tuple[float, ...]:
    """Sample RGBA at top-left based coordinates."""
    y_bottom = height - 1 - y_top
    offset = (y_bottom * width + x) * 4
    return tuple(pixels[offset:offset + 4])
