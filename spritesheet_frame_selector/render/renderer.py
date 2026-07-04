"""Final render backend for selected workspace-aware clip frames."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Iterable

import bpy

from ..core.render_state import render_file_path
from ..core.visibility import collection_visibility_scope


@dataclass(frozen=True)
class FinalRenderResult:
    success: bool
    frame_paths: dict[int, str]
    message: str


def render_clip_frames(
    context: bpy.types.Context,
    clip: bpy.types.PropertyGroup,
    camera: bpy.types.Object,
    collections: list[bpy.types.Collection],
    output_folder: str,
    frame_numbers: Iterable[int],
    export_settings: bpy.types.PropertyGroup,
) -> FinalRenderResult:
    """Render selected frames to PNG files and restore touched Blender state."""
    scene = getattr(context, "scene", None)
    if scene is None:
        return FinalRenderResult(False, {}, "Scene is unavailable")
    if camera is None:
        return FinalRenderResult(False, {}, "A camera is required for final render")
    if not collections:
        return FinalRenderResult(False, {}, "At least one collection is required")

    os.makedirs(output_folder, exist_ok=True)

    render = scene.render
    image_settings = render.image_settings
    original_frame = scene.frame_current
    original_camera = scene.camera
    original_filepath = render.filepath
    original_resolution_x = render.resolution_x
    original_resolution_y = render.resolution_y
    original_percentage = render.resolution_percentage
    original_file_format = image_settings.file_format
    original_film_transparent = render.film_transparent
    original_use_file_extension = render.use_file_extension

    frame_paths: dict[int, str] = {}
    try:
        with collection_visibility_scope(context.view_layer, collections, camera):
            scene.camera = camera
            render.resolution_x = export_settings.frame_width
            render.resolution_y = export_settings.frame_height
            render.resolution_percentage = 100
            render.film_transparent = export_settings.transparent
            render.use_file_extension = True
            image_settings.file_format = "PNG"

            for output_index, frame_number in enumerate(frame_numbers, start=1):
                target_path = render_file_path(
                    output_folder,
                    output_index,
                    export_settings.sheet_name,
                )
                frame_paths[frame_number] = target_path
                scene.frame_set(frame_number)
                render.filepath = target_path
                result = bpy.ops.render.render(write_still=True)
                if "CANCELLED" in result or not os.path.isfile(target_path):
                    return FinalRenderResult(
                        False,
                        frame_paths,
                        f"Final render failed for frame {frame_number}",
                    )
    except Exception as exc:
        return FinalRenderResult(False, frame_paths, str(exc))
    finally:
        scene.frame_set(original_frame)
        scene.camera = original_camera
        render.filepath = original_filepath
        render.resolution_x = original_resolution_x
        render.resolution_y = original_resolution_y
        render.resolution_percentage = original_percentage
        render.film_transparent = original_film_transparent
        render.use_file_extension = original_use_file_extension
        image_settings.file_format = original_file_format

    return FinalRenderResult(True, frame_paths, "Final render generated")
