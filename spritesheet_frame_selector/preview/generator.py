"""Viewport/OpenGL preview generation backend."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Iterable
from typing import Any

import bpy

from ..core.cache import preview_file_path
from ..core.visibility import collection_visibility_scope


@dataclass(frozen=True)
class PreviewGenerationResult:
    success: bool
    frame_paths: dict[int, str]
    message: str


@dataclass(frozen=True)
class ViewportRenderContext:
    window: Any
    screen: Any
    area: Any
    region: Any
    space: Any


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
    original_color_mode = getattr(image_settings, "color_mode", None)
    original_color_depth = getattr(image_settings, "color_depth", None)
    original_compression = getattr(image_settings, "compression", None)
    original_film_transparent = render.film_transparent
    original_use_file_extension = render.use_file_extension
    original_camera = scene.camera

    frame_paths: dict[int, str] = {}
    try:
        with collection_visibility_scope(context.view_layer, collections, camera):
            scene.camera = camera
            render.resolution_x = clip.preview_size
            render.resolution_y = clip.preview_size
            render.resolution_percentage = 100
            image_settings.file_format = "PNG"
            image_settings.color_mode = "RGBA"
            if original_color_depth is not None:
                image_settings.color_depth = "8"
            render.film_transparent = True
            render.use_file_extension = True

            for frame_number in frame_numbers:
                target_path = preview_file_path(cache_folder, frame_number)
                frame_paths[frame_number] = target_path
                if not force and os.path.isfile(target_path):
                    continue

                scene.frame_set(frame_number)
                render.filepath = target_path
                result = _write_thumbnail(context, preview_mode)
                if not result or not os.path.isfile(target_path):
                    return PreviewGenerationResult(
                        False,
                        frame_paths,
                        f"Preview generation failed for frame {frame_number}",
                    )
                if preview_mode in {"SOLID", "MATERIAL"}:
                    has_transparency = _preview_file_has_transparency(target_path)
                    if has_transparency is False:
                        _remove_file_if_exists(target_path)
                        return PreviewGenerationResult(
                            False,
                            frame_paths,
                            f"{preview_mode.title()} preview did not produce transparent alpha",
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
        if original_color_mode is not None:
            image_settings.color_mode = original_color_mode
        if original_color_depth is not None:
            image_settings.color_depth = original_color_depth
        if original_compression is not None:
            image_settings.compression = original_compression
        render.film_transparent = original_film_transparent
        render.use_file_extension = original_use_file_extension

    return PreviewGenerationResult(True, frame_paths, f"{preview_mode.title()} preview cache generated")


def _write_thumbnail(context: bpy.types.Context, preview_mode: str) -> bool:
    if preview_mode == "RENDERED":
        return _write_render_thumbnail()
    if bpy.app.background:
        raise RuntimeError(f"{preview_mode.title()} preview requires an open 3D Viewport")

    viewport_context = _find_view3d_render_context(context)
    if viewport_context is None:
        raise RuntimeError(f"{preview_mode.title()} preview requires an open 3D Viewport")

    return _write_viewport_thumbnail(context, viewport_context, preview_mode)


def _write_viewport_thumbnail(
    context: bpy.types.Context,
    viewport_context: ViewportRenderContext,
    preview_mode: str,
) -> bool:
    space = viewport_context.space
    shading = getattr(space, "shading", None)
    overlay = getattr(space, "overlay", None)
    original_shading_type = getattr(shading, "type", None)
    original_overlay = getattr(overlay, "show_overlays", None)
    try:
        if shading is not None:
            shading.type = preview_mode
        if overlay is not None and original_overlay is not None:
            overlay.show_overlays = False
        with context.temp_override(
            window=viewport_context.window,
            screen=viewport_context.screen,
            area=viewport_context.area,
            region=viewport_context.region,
            space_data=space,
        ):
            result = bpy.ops.render.opengl(write_still=True, view_context=True)
    except RuntimeError:
        return False
    finally:
        if shading is not None and original_shading_type is not None:
            shading.type = original_shading_type
        if overlay is not None and original_overlay is not None:
            overlay.show_overlays = original_overlay
    return "CANCELLED" not in result


def _find_view3d_render_context(context: bpy.types.Context) -> ViewportRenderContext | None:
    area = getattr(context, "area", None)
    if getattr(area, "type", None) == "VIEW_3D":
        viewport_context = _viewport_context_from_area(context, area)
        if viewport_context is not None:
            return viewport_context

    screen = getattr(getattr(context, "window", None), "screen", None)
    for candidate_area in getattr(screen, "areas", ()):
        if getattr(candidate_area, "type", None) != "VIEW_3D":
            continue
        viewport_context = _viewport_context_from_area(context, candidate_area)
        if viewport_context is not None:
            return viewport_context
    return None


def _viewport_context_from_area(context: bpy.types.Context, area: Any) -> ViewportRenderContext | None:
    window = getattr(context, "window", None)
    screen = getattr(window, "screen", None)
    if window is None or screen is None:
        return None

    region = next(
        (candidate for candidate in getattr(area, "regions", ()) if getattr(candidate, "type", None) == "WINDOW"),
        None,
    )
    space = getattr(area, "spaces", None)
    active_space = getattr(space, "active", None)
    if getattr(active_space, "type", None) != "VIEW_3D":
        active_space = next(
            (
                candidate
                for candidate in getattr(area, "spaces", ())
                if getattr(candidate, "type", None) == "VIEW_3D"
            ),
            None,
        )
    if region is None or active_space is None:
        return None

    return ViewportRenderContext(
        window=window,
        screen=screen,
        area=area,
        region=region,
        space=active_space,
    )


def _write_render_thumbnail() -> bool:
    try:
        result = bpy.ops.render.render(write_still=True)
    except RuntimeError:
        return False
    return "CANCELLED" not in result


def _preview_file_has_transparency(path: str) -> bool | None:
    images = getattr(getattr(bpy, "data", None), "images", None)
    load = getattr(images, "load", None)
    remove = getattr(images, "remove", None)
    if load is None or remove is None:
        return None

    image = None
    try:
        image = load(path, check_existing=False)
        channels = getattr(image, "channels", 0)
        if channels < 4:
            return False
        pixels = getattr(image, "pixels", ())
        return any(alpha < 0.999 for alpha in pixels[3::channels])
    except Exception:
        return None
    finally:
        if image is not None:
            try:
                remove(image)
            except Exception:
                pass


def _remove_file_if_exists(path: str) -> None:
    try:
        if os.path.isfile(path):
            os.remove(path)
    except OSError:
        pass
