"""Integration tests: paths, scene isolation, undo, naming and scale limits."""

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
    read_png_pixels,
    reset_scene,
    set_workspace_defaults,
    use_fast_render_engine,
)


def sync(clip, start, end, step=1):
    from spritesheet_frame_selector.core.frame_math import frame_numbers
    from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

    clip.frame_start = start
    clip.frame_end = end
    clip.frame_step = step
    sync_clip_frames(clip, frame_numbers(start, end, step))
    return clip


class SceneIsolationTests(unittest.TestCase):
    """State lives on the Scene, so scenes must not share workspaces."""

    def test_each_scene_keeps_its_own_workspaces(self):
        reset_scene()
        first = bpy.context.scene
        first.name = "SceneA"
        new_workspace("OnlyInA")
        self.assertEqual(len(first.spritesheet_state.workspaces), 1)

        bpy.ops.scene.new(type="NEW")
        second = bpy.context.scene
        second.name = "SceneB"
        self.assertNotEqual(first, second)
        self.assertEqual(len(second.spritesheet_state.workspaces), 0)

        new_workspace("OnlyInB")
        self.assertEqual(
            [w.name for w in second.spritesheet_state.workspaces], ["OnlyInB"]
        )
        self.assertEqual(
            [w.name for w in first.spritesheet_state.workspaces], ["OnlyInA"]
        )

    def test_full_copy_scene_duplicates_state(self):
        reset_scene()
        new_workspace("Original")
        bpy.ops.scene.new(type="FULL_COPY")
        copied = bpy.context.scene
        self.assertEqual([w.name for w in copied.spritesheet_state.workspaces], ["Original"])


class CachePathTests(unittest.TestCase):
    def setUp(self):
        reset_scene()
        use_fast_render_engine()
        camera = make_camera()
        collection, _obj = make_collection_with_cube()
        link_camera(camera, collection)
        self.workspace = new_workspace()
        set_workspace_defaults(self.workspace, camera, collection)
        self.clip = sync(new_clip(), 1, 2)
        self.clip.preview_mode = "RENDERED"

    def test_unsaved_file_caches_under_the_system_temp_root(self):
        from spritesheet_frame_selector.core.paths import (
            TEMP_CACHE_ROOT_NAME,
            is_managed_cache_folder,
        )

        self.assertEqual(bpy.data.filepath, "")
        bpy.ops.spritesheet.preview_generate()
        self.assertIn(TEMP_CACHE_ROOT_NAME, self.clip.cache_folder)
        self.assertTrue(is_managed_cache_folder(self.clip.cache_folder))

    def test_saved_file_caches_next_to_the_blend(self):
        from spritesheet_frame_selector.core.paths import (
            ADDON_CACHE_NAME,
            CACHE_ROOT_NAME,
        )

        with tempfile.TemporaryDirectory() as tmp:
            blend = os.path.join(tmp, "scene.blend")
            bpy.ops.wm.save_as_mainfile(filepath=blend)
            workspace = active_workspace()
            clip = workspace.clips[0]
            clip.preview_mode = "RENDERED"
            self.assertEqual(bpy.ops.spritesheet.preview_generate(), {"FINISHED"})
            expected_root = os.path.join(tmp, CACHE_ROOT_NAME, ADDON_CACHE_NAME)
            self.assertTrue(
                os.path.abspath(clip.cache_folder).startswith(os.path.realpath(expected_root))
                or os.path.realpath(clip.cache_folder).startswith(os.path.realpath(expected_root)),
                f"{clip.cache_folder} not under {expected_root}",
            )

    def test_cache_key_is_independent_of_visible_names(self):
        bpy.ops.spritesheet.preview_generate()
        key_before = self.clip.cache_key
        folder_before = self.clip.cache_folder
        self.clip.name = "Renamed Clip"
        self.workspace.name = "Renamed Workspace"
        bpy.ops.spritesheet.preview_generate()
        self.assertEqual(self.clip.cache_key, key_before)
        self.assertEqual(self.clip.cache_folder, folder_before)


class RelativeOutputPathTests(unittest.TestCase):
    def setUp(self):
        reset_scene()
        use_fast_render_engine()
        camera = make_camera()
        collection, _obj = make_collection_with_cube()
        link_camera(camera, collection)
        self.workspace = new_workspace()
        set_workspace_defaults(self.workspace, camera, collection)

    def test_blend_relative_output_folder_resolves_next_to_the_blend(self):
        with tempfile.TemporaryDirectory() as tmp:
            blend = os.path.join(tmp, "scene.blend")
            bpy.ops.wm.save_as_mainfile(filepath=blend)
            workspace = active_workspace()
            clip = sync(new_clip(), 1, 2)
            configure_export(workspace, "//out/", frame_width=8, frame_height=8, columns=2)
            self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})
            self.assertTrue(os.path.isfile(os.path.join(tmp, "out", "sheet.png")))
            self.assertTrue(os.path.isfile(os.path.join(tmp, "out", "sheet.json")))
            del clip

    def test_blend_relative_output_folder_on_an_unsaved_file_does_not_crash(self):
        clip = sync(new_clip(), 1, 2)
        configure_export(self.workspace, "//out/", frame_width=8, frame_height=8, columns=2)
        result = bpy.ops.spritesheet.export_spritesheet()
        # Either it exports somewhere resolvable or it reports; it must not raise.
        self.assertIn(result, ({"FINISHED"}, {"CANCELLED"}))
        del clip


class SheetNamingTests(unittest.TestCase):
    def setUp(self):
        reset_scene()
        use_fast_render_engine()
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        camera = make_camera()
        collection, _obj = make_collection_with_cube()
        link_camera(camera, collection)
        self.workspace = new_workspace()
        set_workspace_defaults(self.workspace, camera, collection)
        self.clip = sync(new_clip(), 1, 2)
        configure_export(self.workspace, self.tmp, frame_width=8, frame_height=8, columns=2)

    def tearDown(self):
        self._tmp.cleanup()

    def test_sheet_name_with_spaces_and_accents(self):
        self.workspace.export_settings.sheet_name = "hoja de sprites ñ"
        self.workspace.export_settings.export_png_sequence = True
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "hoja de sprites ñ.png")))
        frames = sorted(os.listdir(os.path.join(self.tmp, "hoja de sprites ñ_frames")))
        self.assertEqual(
            frames, ["hoja de sprites ñ_frame_001.png", "hoja de sprites ñ_frame_002.png"]
        )

    def test_dotted_sheet_name_keeps_only_the_stem(self):
        self.workspace.export_settings.sheet_name = "hero.v2.final"
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})
        # os.path.splitext strips the last extension-looking suffix.
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "hero.v2.png")))
        with open(os.path.join(self.tmp, "hero.v2.json"), encoding="utf-8") as handle:
            self.assertEqual(json.load(handle)["sheet"], "hero.v2")

    def test_duplicate_clip_names_across_export_are_rejected(self):
        # Names are unique per workspace by construction; force a collision to
        # confirm the export guard still refuses rather than overwrite ranges.
        second = sync(new_clip(), 1, 2)
        from spritesheet_frame_selector import properties

        properties._RENAMING_CLIP = True
        try:
            second.name = self.clip.name
        finally:
            properties._RENAMING_CLIP = False
        self.assertEqual(self.clip.name, second.name)
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"CANCELLED"})
        self.assertIn("unique", active_workspace().last_export_note)


# NOTE: undo/redo cannot be exercised in background Blender -- `ed.undo` polls
# for a window context that only exists with a GUI. Those checks live in
# tests/blender/gui_checks.py instead.


class ScaleTests(unittest.TestCase):
    def setUp(self):
        reset_scene()
        use_fast_render_engine()
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        camera = make_camera()
        collection, _obj = make_collection_with_cube()
        link_camera(camera, collection)
        self.workspace = new_workspace()
        set_workspace_defaults(self.workspace, camera, collection)

    def tearDown(self):
        self._tmp.cleanup()

    def test_single_frame_clip_exports_a_one_cell_sheet(self):
        sync(new_clip(), 1, 1)
        configure_export(self.workspace, self.tmp, frame_width=8, frame_height=8, columns=4)
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})
        _pixels, width, height = read_png_pixels(os.path.join(self.tmp, "sheet.png"))
        # One frame still occupies a full-width grid row.
        self.assertEqual((width, height), (32, 8))

    def test_frame_step_skips_frames(self):
        clip = sync(new_clip(), 1, 10, step=3)
        self.assertEqual([f.frame_number for f in clip.frames], [1, 4, 7, 10])
        configure_export(self.workspace, self.tmp, frame_width=8, frame_height=8, columns=2)
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})
        with open(os.path.join(self.tmp, "sheet.json"), encoding="utf-8") as handle:
            self.assertEqual(json.load(handle)["clips"]["Clip"]["count"], 4)

    def test_frame_zero_is_allowed(self):
        clip = sync(new_clip(), 0, 2)
        self.assertEqual([f.frame_number for f in clip.frames], [0, 1, 2])
        configure_export(self.workspace, self.tmp, frame_width=8, frame_height=8, columns=3)
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})
        with open(os.path.join(self.tmp, "sheet.json"), encoding="utf-8") as handle:
            self.assertEqual(json.load(handle)["clips"]["Clip"]["count"], 3)

    def test_exactly_999_individual_frames_is_accepted(self):
        from spritesheet_frame_selector.export.sequence import validate_individual_frame_limit

        validate_individual_frame_limit([""] * 999)
        with self.assertRaises(ValueError):
            validate_individual_frame_limit([""] * 1000)

    def test_many_clips_produce_contiguous_ranges(self):
        for index in range(5):
            sync(new_clip(f"Clip{index}"), 1, 2)
        configure_export(self.workspace, self.tmp, frame_width=8, frame_height=8, columns=4)
        self.assertEqual(bpy.ops.spritesheet.export_spritesheet(), {"FINISHED"})
        with open(os.path.join(self.tmp, "sheet.json"), encoding="utf-8") as handle:
            clips = json.load(handle)["clips"]
        self.assertEqual(len(clips), 5)
        starts = [clips[name]["start"] for name in clips]
        ends = [clips[name]["end"] for name in clips]
        self.assertEqual(starts, [0, 2, 4, 6, 8])
        self.assertEqual(ends, [1, 3, 5, 7, 9])
