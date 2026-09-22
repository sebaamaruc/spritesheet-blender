"""Integration tests: composer pixel correctness and end-to-end export."""

from __future__ import annotations

import json
import os
import tempfile
import unittest

import bpy

from it_common import (
    active_workspace,
    configure_export,
    link_camera,
    make_camera,
    make_collection_with_cube,
    new_clip,
    new_workspace,
    pixel_at,
    read_png_pixels,
    reset_scene,
    set_workspace_defaults,
    use_fast_render_engine,
    write_solid_png,
)

from spritesheet_frame_selector.export.composer import compose_spritesheet_png
from spritesheet_frame_selector.export.layout import (
    MAX_SHEET_DIMENSION,
    sheet_dimensions,
    validate_sheet_dimension_limit,
)


RED = (1.0, 0.0, 0.0, 1.0)
GREEN = (0.0, 1.0, 0.0, 1.0)
BLUE = (0.0, 0.0, 1.0, 1.0)
WHITE = (1.0, 1.0, 1.0, 1.0)


class ComposerPixelTests(unittest.TestCase):
    """Verify the composed sheet against exact expected pixels."""

    def setUp(self):
        reset_scene()
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def make_frames(self, colors, size=8):
        paths = []
        for index, color in enumerate(colors):
            path = os.path.join(self.tmp, "src", f"f{index}.png")
            write_solid_png(path, size, size, color)
            paths.append(path)
        return paths

    def test_frames_land_in_row_major_order(self):
        paths = self.make_frames([RED, GREEN, BLUE, WHITE])
        out = os.path.join(self.tmp, "out", "sheet.png")
        result = compose_spritesheet_png(
            paths, out, frame_width=8, frame_height=8, columns=2, transparent=True
        )
        self.assertTrue(result.success, result.message)

        pixels, width, height = read_png_pixels(out)
        self.assertEqual((width, height), (16, 16))
        # index 0 -> top-left, 1 -> top-right, 2 -> bottom-left, 3 -> bottom-right
        self.assertAlmostEqualColor(pixel_at(pixels, width, height, 4, 4), RED)
        self.assertAlmostEqualColor(pixel_at(pixels, width, height, 12, 4), GREEN)
        self.assertAlmostEqualColor(pixel_at(pixels, width, height, 4, 12), BLUE)
        self.assertAlmostEqualColor(pixel_at(pixels, width, height, 12, 12), WHITE)

    def test_padding_and_margin_leave_transparent_gutters(self):
        paths = self.make_frames([RED, GREEN])
        out = os.path.join(self.tmp, "out", "padded.png")
        result = compose_spritesheet_png(
            paths, out, frame_width=8, frame_height=8, columns=2,
            padding=4, margin=3, transparent=True,
        )
        self.assertTrue(result.success, result.message)

        pixels, width, height = read_png_pixels(out)
        # width = 3*2 + 2*8 + 1*4 = 26 ; height = 3*2 + 1*8 + 0 = 14
        self.assertEqual((width, height), (26, 14))
        self.assertAlmostEqualColor(pixel_at(pixels, width, height, 3 + 4, 3 + 4), RED)
        self.assertAlmostEqualColor(pixel_at(pixels, width, height, 3 + 8 + 4 + 4, 3 + 4), GREEN)
        # margin corner and the padding gutter must stay fully transparent
        self.assertAlmostEqual(pixel_at(pixels, width, height, 0, 0)[3], 0.0, places=2)
        self.assertAlmostEqual(pixel_at(pixels, width, height, 3 + 8 + 2, 3 + 4)[3], 0.0, places=2)

    def test_opaque_background_when_transparent_disabled(self):
        paths = self.make_frames([RED])
        out = os.path.join(self.tmp, "out", "opaque.png")
        result = compose_spritesheet_png(
            paths, out, frame_width=8, frame_height=8, columns=2,
            margin=2, transparent=False,
        )
        self.assertTrue(result.success, result.message)
        pixels, width, height = read_png_pixels(out)
        self.assertAlmostEqual(pixel_at(pixels, width, height, 0, 0)[3], 1.0, places=2)

    def test_partial_last_row_keeps_full_grid_width(self):
        paths = self.make_frames([RED, GREEN, BLUE])
        out = os.path.join(self.tmp, "out", "partial.png")
        result = compose_spritesheet_png(
            paths, out, frame_width=8, frame_height=8, columns=2, transparent=True
        )
        self.assertTrue(result.success, result.message)
        pixels, width, height = read_png_pixels(out)
        self.assertEqual((width, height), (16, 16))
        # unused bottom-right cell stays transparent
        self.assertAlmostEqual(pixel_at(pixels, width, height, 12, 12)[3], 0.0, places=2)

    def test_alpha_is_preserved_round_trip(self):
        half = (1.0, 0.0, 0.0, 0.5)
        paths = self.make_frames([half])
        out = os.path.join(self.tmp, "out", "alpha.png")
        result = compose_spritesheet_png(
            paths, out, frame_width=8, frame_height=8, columns=1, transparent=True
        )
        self.assertTrue(result.success, result.message)
        pixels, width, height = read_png_pixels(out)
        self.assertAlmostEqual(pixel_at(pixels, width, height, 4, 4)[3], 0.5, places=2)

    def test_size_mismatch_is_reported_not_crashed(self):
        good = self.make_frames([RED], size=8)[0]
        bad = os.path.join(self.tmp, "src", "bad.png")
        write_solid_png(bad, 4, 4, GREEN)
        out = os.path.join(self.tmp, "out", "mismatch.png")
        result = compose_spritesheet_png(
            [good, bad], out, frame_width=8, frame_height=8, columns=2, transparent=True
        )
        self.assertFalse(result.success)
        self.assertIn("Frame size mismatch", result.message)

    def test_missing_frame_is_reported(self):
        out = os.path.join(self.tmp, "out", "missing.png")
        result = compose_spritesheet_png(
            [os.path.join(self.tmp, "nope.png")], out,
            frame_width=8, frame_height=8, columns=1, transparent=True,
        )
        self.assertFalse(result.success)
        self.assertIn("Missing rendered frame", result.message)

    def test_empty_frame_list_is_reported(self):
        result = compose_spritesheet_png(
            [], os.path.join(self.tmp, "out", "empty.png"),
            frame_width=8, frame_height=8, columns=1,
        )
        self.assertFalse(result.success)
        self.assertEqual(result.message, "No frames to compose")

    def test_composer_does_not_leak_image_datablocks(self):
        paths = self.make_frames([RED, GREEN])
        before = len(bpy.data.images)
        out = os.path.join(self.tmp, "out", "leak.png")
        compose_spritesheet_png(
            paths, out, frame_width=8, frame_height=8, columns=2, transparent=True
        )
        self.assertEqual(len(bpy.data.images), before)

    def test_oversized_sheet_is_rejected_before_allocation(self):
        dims = sheet_dimensions(4, MAX_SHEET_DIMENSION, 100, 4)
        self.assertNotEqual(validate_sheet_dimension_limit(dims), "")
        paths = self.make_frames([RED])
        out = os.path.join(self.tmp, "out", "huge.png")
        result = compose_spritesheet_png(
            paths, out,
            frame_width=MAX_SHEET_DIMENSION, frame_height=8, columns=4, transparent=True,
        )
        self.assertFalse(result.success)
        self.assertIn("exceed", result.message)
        self.assertFalse(os.path.exists(out))

    def assertAlmostEqualColor(self, actual, expected, places=2):
        for channel, (a, e) in enumerate(zip(actual, expected)):
            self.assertAlmostEqual(a, e, places=places, msg=f"channel {channel}: {actual} != {expected}")


class ExportOperatorTests(unittest.TestCase):
    """End-to-end: real render -> compose -> PNG + JSON."""

    def setUp(self):
        reset_scene()
        use_fast_render_engine()
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name

        self.camera = make_camera()
        self.collection, self.obj = make_collection_with_cube()
        link_camera(self.camera, self.collection)
        self.workspace = new_workspace("W")
        set_workspace_defaults(self.workspace, self.camera, self.collection)
        configure_export(self.workspace, self.tmp, frame_width=16, frame_height=16, columns=3)

    def tearDown(self):
        self._tmp.cleanup()

    def make_clip(self, name, start, end, fps=12, step=1):
        from spritesheet_frame_selector.core.frame_math import frame_numbers
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        clip = new_clip(name)
        clip.frame_start = start
        clip.frame_end = end
        clip.frame_step = step
        clip.fps = fps
        sync_clip_frames(clip, frame_numbers(start, end, step))
        return clip

    def test_single_clip_export_writes_png_and_json(self):
        self.make_clip("Walk", 1, 4)
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})

        png = os.path.join(self.tmp, "sheet.png")
        meta = os.path.join(self.tmp, "sheet.json")
        self.assertTrue(os.path.isfile(png))
        self.assertTrue(os.path.isfile(meta))

        _pixels, width, height = read_png_pixels(png)
        self.assertEqual((width, height), (48, 32))  # 3 cols x 16, 2 rows x 16

        with open(meta, encoding="utf-8") as handle:
            data = json.load(handle)
        self.assertEqual(data["sheet"], "sheet")
        self.assertEqual(data["frameWidth"], 16)
        self.assertEqual(data["frameHeight"], 16)
        self.assertEqual(data["columns"], 3)
        self.assertEqual(data["clips"], {"Walk": {"start": 0, "end": 3, "count": 4, "fps": 12}})

    def test_multi_clip_ranges_are_contiguous_and_ordered(self):
        self.make_clip("Walk", 1, 3, fps=12)
        self.make_clip("Run", 1, 2, fps=24)
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})

        with open(os.path.join(self.tmp, "sheet.json"), encoding="utf-8") as handle:
            data = json.load(handle)
        self.assertEqual(
            data["clips"],
            {
                "Walk": {"start": 0, "end": 2, "count": 3, "fps": 12},
                "Run": {"start": 3, "end": 4, "count": 2, "fps": 24},
            },
        )

    def test_excluded_clip_is_omitted(self):
        self.make_clip("Walk", 1, 2)
        skipped = self.make_clip("Skip", 1, 2)
        skipped.include_in_export = False
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})
        with open(os.path.join(self.tmp, "sheet.json"), encoding="utf-8") as handle:
            data = json.load(handle)
        self.assertEqual(list(data["clips"]), ["Walk"])

    def test_deselected_frames_are_not_rendered(self):
        clip = self.make_clip("Walk", 1, 4)
        clip.frames[1].selected = False
        clip.frames[3].selected = False
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})
        with open(os.path.join(self.tmp, "sheet.json"), encoding="utf-8") as handle:
            data = json.load(handle)
        self.assertEqual(data["clips"]["Walk"]["count"], 2)

    def test_individual_frames_are_sequentially_numbered(self):
        self.make_clip("Walk", 5, 8)
        self.workspace.export_settings.export_png_sequence = True
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})

        folder = os.path.join(self.tmp, "sheet_frames")
        self.assertTrue(os.path.isdir(folder))
        names = sorted(os.listdir(folder))
        # Named by export order (001..), not by native Blender frame (005..).
        self.assertEqual(
            names,
            ["sheet_frame_001.png", "sheet_frame_002.png",
             "sheet_frame_003.png", "sheet_frame_004.png"],
        )
        self.assertEqual(self.workspace.export_settings.png_sequence_folder, folder)

    def test_reexport_with_fewer_frames_clears_stale_individual_frames(self):
        clip = self.make_clip("Walk", 1, 4)
        self.workspace.export_settings.export_png_sequence = True
        bpy.ops.spritesheet.export_spritesheet()
        folder = os.path.join(self.tmp, "sheet_frames")
        self.assertEqual(len(os.listdir(folder)), 4)

        clip.frames[2].selected = False
        clip.frames[3].selected = False
        bpy.ops.spritesheet.export_spritesheet()
        self.assertEqual(sorted(os.listdir(folder)), ["sheet_frame_001.png", "sheet_frame_002.png"])

    def test_export_restores_scene_render_state(self):
        scene = bpy.context.scene
        scene.frame_set(7)
        scene.render.resolution_x = 321
        scene.render.resolution_y = 123
        scene.render.filepath = "/tmp/original_path"
        scene.render.film_transparent = False
        scene.render.image_settings.file_format = "JPEG"
        other_cam = make_camera("OtherCam")
        link_camera(other_cam)
        scene.camera = other_cam

        self.make_clip("Walk", 1, 3)
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})

        self.assertEqual(scene.frame_current, 7)
        self.assertEqual(scene.render.resolution_x, 321)
        self.assertEqual(scene.render.resolution_y, 123)
        self.assertEqual(scene.render.filepath, "/tmp/original_path")
        self.assertFalse(scene.render.film_transparent)
        self.assertEqual(scene.render.image_settings.file_format, "JPEG")
        self.assertEqual(scene.camera, other_cam)

    def test_export_restores_collection_visibility(self):
        hidden, _obj = make_collection_with_cube("Hidden", "HiddenCube")
        layer = bpy.context.view_layer.layer_collection.children["Hidden"]
        layer.exclude = False
        self.make_clip("Walk", 1, 2)
        bpy.ops.spritesheet.export_spritesheet()
        self.assertFalse(bpy.context.view_layer.layer_collection.children["Hidden"].exclude)
        del hidden

    def test_export_leaves_no_temporary_files_behind(self):
        self.make_clip("Walk", 1, 3)
        bpy.ops.spritesheet.export_spritesheet()
        leftovers = [
            name for name in os.listdir(tempfile.gettempdir())
            if name.startswith("spritesheet_export_")
        ]
        self.assertEqual(leftovers, [])

    def test_export_does_not_leak_image_datablocks(self):
        # Blender itself owns a reusable 'Render Result' datablock; only
        # addon-created/loaded images count as a leak.
        def addon_images():
            return [i.name for i in bpy.data.images if i.type != "RENDER_RESULT"]

        self.make_clip("Walk", 1, 3)
        before = addon_images()
        bpy.ops.spritesheet.export_spritesheet()
        self.assertEqual(addon_images(), before)


class ExportValidationTests(unittest.TestCase):
    """Predictable failures must be reported, never raised."""

    def setUp(self):
        reset_scene()
        use_fast_render_engine()
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.camera = make_camera()
        self.collection, _obj = make_collection_with_cube()
        link_camera(self.camera, self.collection)
        self.workspace = new_workspace("W")
        set_workspace_defaults(self.workspace, self.camera, self.collection)
        configure_export(self.workspace, self.tmp, frame_width=8, frame_height=8, columns=2)

    def tearDown(self):
        self._tmp.cleanup()

    def make_clip(self, name="Walk", start=1, end=3):
        from spritesheet_frame_selector.core.frame_math import frame_numbers
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        clip = new_clip(name)
        clip.frame_start = start
        clip.frame_end = end
        sync_clip_frames(clip, frame_numbers(start, end, 1))
        return clip

    def assertCancelledWith(self, fragment):
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"CANCELLED"})
        note = active_workspace().last_export_note
        self.assertIn(fragment, note, f"unexpected note: {note!r}")

    def test_no_workspace(self):
        reset_scene()
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"CANCELLED"})

    def test_no_clips(self):
        self.assertCancelledWith("No clips included in export")

    def test_missing_output_folder(self):
        self.make_clip()
        self.workspace.export_settings.output_folder = ""
        self.assertCancelledWith("Missing export output folder")

    def test_missing_sheet_name(self):
        self.make_clip()
        self.workspace.export_settings.sheet_name = "   "
        self.assertCancelledWith("Missing sheet name")

    def test_no_selected_frames(self):
        clip = self.make_clip()
        for frame in clip.frames:
            frame.selected = False
        self.assertCancelledWith("has no selected frames")

    def test_missing_camera(self):
        self.make_clip()
        self.workspace.default_camera = None
        self.assertCancelledWith("Missing effective camera")

    def test_deleted_camera_is_reported_not_crashed(self):
        self.make_clip()
        bpy.data.objects.remove(self.camera)
        self.assertCancelledWith("Missing effective camera")

    def test_missing_collection_is_reported_by_last_known_name(self):
        self.make_clip()
        bpy.data.collections.remove(self.collection)
        self.assertCancelledWith("Missing collection: Props")

    def test_empty_frame_range_is_reported(self):
        clip = self.make_clip(start=10, end=5)
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        sync_clip_frames(clip, [])
        self.assertCancelledWith("has no selected frames")

    def test_individual_frame_limit_is_enforced_before_rendering(self):
        clip = self.make_clip(start=1, end=1200)
        self.workspace.export_settings.export_png_sequence = True
        self.assertCancelledWith("up to 999 frames")
        # Nothing should have been rendered or written.
        self.assertFalse(os.path.isfile(os.path.join(self.tmp, "sheet.png")))
        del clip

    def test_oversized_sheet_is_reported(self):
        self.make_clip(start=1, end=3)
        self.workspace.export_settings.frame_width = 9000
        self.workspace.export_settings.frame_height = 8
        self.workspace.export_settings.columns = 3
        self.assertCancelledWith("exceed")

    def test_sheet_name_with_path_separators_is_confined_to_output_folder(self):
        self.make_clip()
        self.workspace.export_settings.sheet_name = "../escaped"
        bpy.ops.spritesheet.export_spritesheet()
        self.assertFalse(os.path.exists(os.path.join(os.path.dirname(self.tmp), "escaped.png")))
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "escaped.png")))
