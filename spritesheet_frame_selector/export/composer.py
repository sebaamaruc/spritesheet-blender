"""Spritesheet PNG composer using Blender image APIs."""

from __future__ import annotations

from array import array
from dataclasses import dataclass
import os

from .layout import frame_rect, sheet_dimensions, validate_sheet_dimension_limit


@dataclass(frozen=True)
class ComposeResult:
    success: bool
    message: str


def compose_spritesheet_png(
    frame_paths: list[str],
    output_path: str,
    *,
    frame_width: int,
    frame_height: int,
    columns: int,
    padding: int = 0,
    margin: int = 0,
    transparent: bool = True,
) -> ComposeResult:
    """Compose rendered frame PNGs into a final spritesheet PNG."""
    if not frame_paths:
        return ComposeResult(False, "No frames to compose")

    import bpy

    dimensions = sheet_dimensions(
        len(frame_paths),
        frame_width,
        frame_height,
        columns,
        padding,
        margin,
    )
    dimension_error = validate_sheet_dimension_limit(dimensions)
    if dimension_error:
        return ComposeResult(False, dimension_error)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    alpha = 0.0 if transparent else 1.0
    canvas = array("f", [0.0, 0.0, 0.0, alpha]) * (dimensions.width * dimensions.height)
    loaded_images = []
    sheet_image = None

    try:
        for index, frame_path in enumerate(frame_paths):
            if not os.path.isfile(frame_path):
                return ComposeResult(False, f"Missing rendered frame: {frame_path}")

            image = bpy.data.images.load(frame_path, check_existing=False)
            loaded_images.append(image)
            if int(image.size[0]) != frame_width or int(image.size[1]) != frame_height:
                return ComposeResult(
                    False,
                    f"Frame size mismatch: {os.path.basename(frame_path)}",
                )

            source_pixels = array("f", [0.0]) * len(image.pixels)
            image.pixels.foreach_get(source_pixels)
            rect = frame_rect(index, frame_width, frame_height, columns, padding, margin)
            _paste_pixels(
                canvas,
                dimensions.width,
                dimensions.height,
                source_pixels,
                rect.x,
                rect.y,
                frame_width,
                frame_height,
            )

        sheet_image = bpy.data.images.new(
            "SpriteSheet Export",
            width=dimensions.width,
            height=dimensions.height,
            alpha=True,
        )
        sheet_image.pixels.foreach_set(canvas)
        sheet_image.filepath_raw = output_path
        sheet_image.file_format = "PNG"
        sheet_image.save()
    except Exception as exc:
        return ComposeResult(False, str(exc))
    finally:
        for image in loaded_images:
            bpy.data.images.remove(image)
        if sheet_image is not None:
            bpy.data.images.remove(sheet_image)

    if not os.path.isfile(output_path):
        return ComposeResult(False, "Spritesheet PNG was not written")
    return ComposeResult(True, "Spritesheet PNG exported")


def _paste_pixels(
    canvas,
    canvas_width: int,
    canvas_height: int,
    source_pixels,
    dest_x: int,
    dest_y_top: int,
    width: int,
    height: int,
) -> None:
    """Paste source pixels into canvas; rect coordinates are top-left based.

    ``canvas``/``source_pixels`` accept any mutable sequence supporting slice
    assignment from a same-type slice (``list`` or ``array.array('f')``).
    """
    dest_y_bottom = canvas_height - dest_y_top - height
    for y in range(height):
        source_start = y * width * 4
        source_end = source_start + width * 4
        dest_start = ((dest_y_bottom + y) * canvas_width + dest_x) * 4
        dest_end = dest_start + width * 4
        canvas[dest_start:dest_end] = source_pixels[source_start:source_end]
