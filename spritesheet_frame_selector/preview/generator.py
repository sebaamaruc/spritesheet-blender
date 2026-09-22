"""Viewport/OpenGL preview generation backend."""

from __future__ import annotations

from array import array
from dataclasses import dataclass
import os
from typing import Callable, Iterable
from typing import Any
from contextlib import contextmanager

import bpy

from ..core.cache import preview_file_path
from ..core.debug import debug_log
from ..core.visibility import collection_visibility_scope


@dataclass(frozen=True)
class PreviewGenerationResult:
    success: bool
    frame_paths: dict[int, str]
    message: str
    alpha_warning: bool = False


@dataclass(frozen=True)
class ViewportRenderContext:
    window: Any
    screen: Any
    area: Any
    region: Any
    space: Any
    region_3d: Any


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
    progress_callback: Callable[[], None] | None = None,
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
    original_film_transparent = render.film_transparent
    original_use_file_extension = render.use_file_extension
    original_camera = scene.camera

    frame_paths: dict[int, str] = {}
    alpha_warning = False
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

            with _thumbnail_writer_scope(context, preview_mode) as thumbnail_writer:
                for frame_number in frame_numbers:
                    target_path = preview_file_path(cache_folder, frame_number)
                    frame_paths[frame_number] = target_path
                    if not force and os.path.isfile(target_path):
                        if progress_callback is not None:
                            progress_callback()
                        continue

                    scene.frame_set(frame_number)
                    render.filepath = target_path
                    result = thumbnail_writer()
                    if not result or not os.path.isfile(target_path):
                        return PreviewGenerationResult(
                            False,
                            frame_paths,
                            f"Preview generation failed for frame {frame_number}",
                        )
                    if preview_mode in {"SOLID", "MATERIAL"}:
                        has_transparency = _preview_file_has_transparency(target_path)
                        if has_transparency is False:
                            alpha_warning = True
                    if progress_callback is not None:
                        progress_callback()
    except Exception as exc:
        debug_log("Viewport preview generation failed", exc)
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
        render.film_transparent = original_film_transparent
        render.use_file_extension = original_use_file_extension

    message = f"{preview_mode.title()} preview cache generated"
    if alpha_warning:
        message = f"{message}; no transparent pixels detected in one or more thumbnails"
    return PreviewGenerationResult(True, frame_paths, message, alpha_warning=alpha_warning)


@contextmanager
def _thumbnail_writer_scope(context: bpy.types.Context, preview_mode: str):
    if preview_mode == "RENDERED":
        yield _write_render_thumbnail
        return
    if bpy.app.background:
        raise RuntimeError(f"{preview_mode.title()} preview requires an open 3D Viewport")

    viewport_context = _find_view3d_render_context(context)
    if viewport_context is None:
        raise RuntimeError(f"{preview_mode.title()} preview requires an open 3D Viewport")

    with _viewport_render_scope(viewport_context, preview_mode):
        yield lambda: _write_viewport_thumbnail(context, viewport_context)


def _apply_shading_type(shading: Any, preview_mode: str) -> None:
    """Set the viewport shading mode, reporting engine limits in plain language.

    ``View3DShading.type`` is filtered by the scene render engine: Workbench
    offers only WIREFRAME/SOLID/RENDERED, so requesting MATERIAL there raises a
    raw ``TypeError`` that is useless to the user.
    """
    try:
        shading.type = preview_mode
    except TypeError as exc:
        engine = getattr(getattr(getattr(bpy, "context", None), "scene", None), "render", None)
        engine_name = getattr(engine, "engine", "") or "the current"
        raise RuntimeError(
            f"{preview_mode.title()} preview is not available with the "
            f"{engine_name} render engine; switch the render engine or pick "
            f"another preview mode"
        ) from exc


@contextmanager
def _viewport_render_scope(viewport_context: ViewportRenderContext, preview_mode: str):
    space = viewport_context.space
    region_3d = viewport_context.region_3d
    if region_3d is None:
        raise RuntimeError(f"{preview_mode.title()} preview requires a 3D Viewport with RegionView3D")

    shading = getattr(space, "shading", None)
    overlay = getattr(space, "overlay", None)
    original_view_perspective = getattr(region_3d, "view_perspective", None)
    original_shading_type = getattr(shading, "type", None)
    original_overlay = getattr(overlay, "show_overlays", None)
    try:
        if original_view_perspective is not None:
            region_3d.view_perspective = "CAMERA"
        if shading is not None:
            _apply_shading_type(shading, preview_mode)
        if overlay is not None and original_overlay is not None:
            overlay.show_overlays = False
        yield
    finally:
        if original_view_perspective is not None:
            region_3d.view_perspective = original_view_perspective
        if shading is not None and original_shading_type is not None:
            shading.type = original_shading_type
        if overlay is not None and original_overlay is not None:
            overlay.show_overlays = original_overlay


def _write_viewport_thumbnail(
    context: bpy.types.Context,
    viewport_context: ViewportRenderContext,
) -> bool:
    space = viewport_context.space
    try:
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
        region_3d=getattr(active_space, "region_3d", None),
    )


def _write_render_thumbnail() -> bool:
    try:
        result = bpy.ops.render.render(write_still=True)
    except RuntimeError:
        return False
    return "CANCELLED" not in result


def _alpha_channel(pixels: Any, channels: int) -> Any:
    """Return the alpha values of a flat RGBA pixel buffer.

    ``bpy_prop_array`` rejects strided slicing, so real Blender images are
    copied into a plain buffer first via ``foreach_get``.
    """
    foreach_get = getattr(pixels, "foreach_get", None)
    if foreach_get is not None:
        buffer = array("f", [0.0]) * len(pixels)
        foreach_get(buffer)
        pixels = buffer
    return pixels[3::channels]


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
        return any(alpha < 0.999 for alpha in _alpha_channel(pixels, channels))
    except Exception as exc:
        debug_log(f"Preview transparency probe failed for {path}", exc)
        return None
    finally:
        if image is not None:
            try:
                remove(image)
            except Exception as exc:
                debug_log(f"Preview transparency image cleanup failed for {path}", exc)
