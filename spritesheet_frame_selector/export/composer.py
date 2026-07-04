"""Spritesheet PNG composer using Blender image APIs."""

from __future__ import annotations

from dataclasses import dataclass
import os

from .layout import frame_rect, sheet_dimensions


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
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    alpha = 0.0 if transparent else 1.0
    canvas = [0.0, 0.0, 0.0, alpha] * (dimensions.width * dimensions.height)
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

            source_pixels = list(image.pixels)
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
    canvas: list[float],
    canvas_width: int,
    canvas_height: int,
    source_pixels: list[float],
    dest_x: int,
    dest_y_top: int,
    width: int,
    height: int,
) -> None:
    """Paste source pixels into canvas; rect coordinates are top-left based."""
    dest_y_bottom = canvas_height - dest_y_top - height
    for y in range(height):
        for x in range(width):
            source_index = (y * width + x) * 4
            dest_index = ((dest_y_bottom + y) * canvas_width + dest_x + x) * 4
            canvas[dest_index : dest_index + 4] = source_pixels[source_index : source_index + 4]
