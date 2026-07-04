"""Viewport/OpenGL preview generation backend."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Iterable

import bpy

from ..core.cache import preview_file_path
from ..core.visibility import collection_visibility_scope


@dataclass(frozen=True)
class PreviewGenerationResult:
    success: bool
    frame_paths: dict[int, str]
    message: str


def generate_viewport_previews(
    context: bpy.types.Context,
    clip: bpy.types.PropertyGroup,
    camera: bpy.types.Object,
    collections: list[bpy.types.Collection],
    cache_folder: str,
    frame_numbers: Iterable[int],
    *,
    force: bool = False,
    preview_mode: str = "SOLID",
) -> PreviewGenerationResult:
    """Generate OpenGL thumbnails and restore touched scene/render state."""
    scene = getattr(context, "scene", None)
    if scene is None:
        return PreviewGenerationResult(False, {}, "Scene is unavailable")

    if camera is None:
        return PreviewGenerationResult(False, {}, "A camera is required to generate previews")
    if not collections:
        return PreviewGenerationResult(False, {}, "At least one collection is required")

    os.makedirs(cache_folder, exist_ok=True)
    render = scene.render
    image_settings = render.image_settings
    original_frame = scene.frame_current
    original_filepath = render.filepath
    original_resolution_x = render.resolution_x
    original_resolution_y = render.resolution_y
    original_percentage = render.resolution_percentage
    original_file_format = image_settings.file_format
    original_camera = scene.camera

    frame_paths: dict[int, str] = {}
    try:
        with collection_visibility_scope(context.view_layer, collections, camera):
            scene.camera = camera
            render.resolution_x = clip.preview_size
            render.resolution_y = clip.preview_size
            render.resolution_percentage = 100
            image_settings.file_format = "PNG"

            for frame_number in frame_numbers:
                target_path = preview_file_path(cache_folder, frame_number)
                frame_paths[frame_number] = target_path
                if not force and os.path.isfile(target_path):
                    continue

                scene.frame_set(frame_number)
                render.filepath = target_path
                result = _write_thumbnail(preview_mode)
                if not result or not os.path.isfile(target_path):
                    return PreviewGenerationResult(
                        False,
                        frame_paths,
                        f"Preview generation failed for frame {frame_number}",
                    )
    except Exception as exc:
        return PreviewGenerationResult(False, frame_paths, str(exc))
    finally:
        scene.frame_set(original_frame)
        scene.camera = original_camera
        render.filepath = original_filepath
        render.resolution_x = original_resolution_x
        render.resolution_y = original_resolution_y
        render.resolution_percentage = original_percentage
        image_settings.file_format = original_file_format

    return PreviewGenerationResult(True, frame_paths, f"{preview_mode.title()} preview cache generated")


def _write_thumbnail(preview_mode: str) -> bool:
    if preview_mode == "RENDERED":
        return _write_render_thumbnail()
    if bpy.app.background:
        if preview_mode != "RENDERED":
            raise RuntimeError(f"{preview_mode} preview requires a viewport context")
        return _write_render_thumbnail()

    try:
        result = bpy.ops.render.opengl(write_still=True, view_context=False)
    except RuntimeError:
        if preview_mode == "RENDERED":
            return _write_render_thumbnail()
        return False
    return "CANCELLED" not in result


def _write_render_thumbnail() -> bool:
    try:
        result = bpy.ops.render.render(write_still=True)
    except RuntimeError:
        return False
    return "CANCELLED" not in result
