"""Integration tests: panel draw, preview cache, visibility scope, playback."""

from __future__ import annotations

import os
import tempfile
import unittest
from types import SimpleNamespace

import bpy

from it_common import (
    active_workspace,
    link_camera,
    make_camera,
    make_collection_with_cube,
    new_clip,
    new_workspace,
    reset_scene,
    set_workspace_defaults,
    use_fast_render_engine,
    write_solid_png,
)


# --------------------------------------------------------------------------
# A UILayout stand-in that validates every property / operator / list id used
# by the panel actually exists. Catches typos that only surface at draw time.
# --------------------------------------------------------------------------
class RecordingLayout:
    def __init__(self, recorder: dict):
        self.recorder = recorder

    # container factories -------------------------------------------------
    def box(self):
        return RecordingLayout(self.recorder)

    def row(self, align=False):
        return RecordingLayout(self.recorder)

    def column(self, align=False):
        return RecordingLayout(self.recorder)

    def separator(self, factor=1.0):
        return None

    # leaves --------------------------------------------------------------
    def label(self, text="", icon="NONE", icon_value=0):
        self.recorder["labels"].append(text)

    def prop(self, data, name, text=None, **kwargs):
        properties = data.bl_rna.properties
        if name not in properties:
            raise AssertionError(
                f"panel referenced missing property {name!r} on {data.bl_rna.identifier}"
            )
        self.recorder["props"].append((data.bl_rna.identifier, name))

    def operator(self, idname, text=None, icon="NONE", **kwargs):
        module, _, func = idname.partition(".")
        submodule = getattr(bpy.ops, module, None)
        if submodule is None or func not in dir(submodule):
            raise AssertionError(f"panel referenced unregistered operator {idname!r}")
        self.recorder["operators"].append(idname)
        return OperatorPropsStub(idname)

    def menu(self, idname, text=None, icon="NONE"):
        if not hasattr(bpy.types, idname):
            raise AssertionError(f"panel referenced unregistered menu {idname!r}")
        self.recorder["menus"].append(idname)

    def template_list(self, listtype_name, list_id, dataptr, propname,
                      active_dataptr, active_propname, **kwargs):
        if not hasattr(bpy.types, listtype_name):
            raise AssertionError(f"panel referenced unregistered UIList {listtype_name!r}")
        if propname not in dataptr.bl_rna.properties:
            raise AssertionError(f"template_list missing collection {propname!r}")
        if active_propname not in active_dataptr.bl_rna.properties:
            raise AssertionError(f"template_list missing index {active_propname!r}")
        self.recorder["lists"].append(listtype_name)

    @property
    def alignment(self):
        return "EXPAND"

    @alignment.setter
    def alignment(self, value):
        pass


class OperatorPropsStub:
    """Accepts the ``op.prop = value`` idiom used after ``layout.operator``."""

    def __init__(self, idname):
        object.__setattr__(self, "_idname", idname)

    def __setattr__(self, key, value):
        idname = object.__getattribute__(self, "_idname")
        module, _, func = idname.partition(".")
        operator_class = getattr(bpy.types, f"{module.upper()}_OT_{func}", None)
        if operator_class is None:
            return
        # Operator-declared props live in __annotations__, not the class bl_rna.
        declared = getattr(operator_class, "__annotations__", {})
        if key not in declared:
            raise AssertionError(
                f"operator {idname!r} has no property {key!r}; declared: {sorted(declared)}"
            )


def new_recorder() -> dict:
    return {"labels": [], "props": [], "operators": [], "menus": [], "lists": []}


def draw_panel() -> dict:
    """Run the real ``draw`` body against a validating layout.

    ``bpy_struct`` subclasses cannot be instantiated from Python, so ``draw``
    is invoked as a plain function with a stand-in ``self`` exposing ``layout``.
    """
    from spritesheet_frame_selector.ui.panels import SPRITESHEET_PT_main

    recorder = new_recorder()
    panel_self = SimpleNamespace(layout=RecordingLayout(recorder))
    SPRITESHEET_PT_main.draw(panel_self, bpy.context)
    return recorder


class PanelDrawTests(unittest.TestCase):
    def setUp(self):
        reset_scene()

    def test_draw_with_empty_state(self):
        recorder = draw_panel()
        self.assertIn("No active workspace", recorder["labels"])
        self.assertIn("spritesheet.workspace_add", recorder["operators"])

    def test_draw_with_workspace_but_no_clip(self):
        new_workspace()
        recorder = draw_panel()
        self.assertIn("No active clip", recorder["labels"])

    def test_draw_full_configuration(self):
        camera = make_camera()
        collection, _obj = make_collection_with_cube()
        link_camera(camera, collection)
        workspace = new_workspace()
        set_workspace_defaults(workspace, camera, collection)
        clip = new_clip()
        clip.use_camera_override = True
        clip.use_collection_override = True
        bpy.ops.spritesheet.clip_included_collection_add()
        clip.included_collections[0].collection = collection
        workspace.export_settings.output_folder = "/tmp/x"
        workspace.export_settings.export_png_sequence = True

        recorder = draw_panel()
        self.assertIn("spritesheet.export_spritesheet", recorder["operators"])
        self.assertIn("spritesheet.visual_selector_open", recorder["operators"])
        self.assertIn("SPRITESHEET_MT_preview_size", recorder["menus"])
        self.assertEqual(
            sorted(set(recorder["lists"])),
            ["SPRITESHEET_UL_clips", "SPRITESHEET_UL_workspaces"],
        )

    def test_draw_surfaces_missing_collection_warning(self):
        camera = make_camera()
        collection, _obj = make_collection_with_cube("Gone")
        workspace = new_workspace()
        set_workspace_defaults(workspace, camera, collection)
        new_clip()
        bpy.data.collections.remove(collection)
        recorder = draw_panel()
        self.assertTrue(
            any("Missing" in label for label in recorder["labels"]),
            recorder["labels"],
        )

    def test_sheet_size_label_reflects_included_selection(self):
        camera = make_camera()
        collection, _obj = make_collection_with_cube()
        workspace = new_workspace()
        set_workspace_defaults(workspace, camera, collection)
        clip = new_clip()
        workspace.export_settings.frame_width = 32
        workspace.export_settings.frame_height = 32
        workspace.export_settings.columns = 4
        for frame in clip.frames:
            frame.selected = False
        for frame in list(clip.frames)[:6]:
            frame.selected = True
        recorder = draw_panel()
        self.assertIn("Sheet Size: 128 x 64", recorder["labels"])

    def test_uilist_draw_item_runs(self):
        camera = make_camera()
        collection, _obj = make_collection_with_cube()
        workspace = new_workspace()
        set_workspace_defaults(workspace, camera, collection)
        clip = new_clip()

        from spritesheet_frame_selector.ui.lists import (
            SPRITESHEET_UL_clips,
            SPRITESHEET_UL_workspaces,
        )

        recorder = new_recorder()
        for cls, item in ((SPRITESHEET_UL_workspaces, workspace), (SPRITESHEET_UL_clips, clip)):
            list_self = SimpleNamespace(layout_type="DEFAULT")
            cls.draw_item(
                list_self, bpy.context, RecordingLayout(recorder), None, item, 0, None, "", 0
            )
        self.assertIn(("SpriteSheetClip", "include_in_export"), recorder["props"])


class CollectionVisibilityTests(unittest.TestCase):
    def setUp(self):
        reset_scene()

    def test_nested_ancestors_stay_visible_and_state_is_restored(self):
        from spritesheet_frame_selector.core.visibility import collection_visibility_scope

        parent = bpy.data.collections.new("Parent")
        child = bpy.data.collections.new("Child")
        sibling = bpy.data.collections.new("Sibling")
        bpy.context.scene.collection.children.link(parent)
        parent.children.link(child)
        bpy.context.scene.collection.children.link(sibling)

        view_layer = bpy.context.view_layer
        root = view_layer.layer_collection
        before = {lc.name: lc.exclude for lc in root.children}

        camera = make_camera()
        camera_collection = bpy.data.collections.new("Cams")
        bpy.context.scene.collection.children.link(camera_collection)
        camera_collection.objects.link(camera)

        with collection_visibility_scope(view_layer, [child], camera):
            layers = {lc.name: lc for lc in root.children}
            self.assertFalse(layers["Parent"].exclude, "ancestor must stay visible")
            self.assertFalse(layers["Parent"].children["Child"].exclude)
            self.assertTrue(layers["Sibling"].exclude, "unrelated collection must be excluded")
            self.assertFalse(layers["Cams"].exclude, "camera collection must stay visible")

        after = {lc.name: lc.exclude for lc in root.children}
        self.assertEqual(after["Parent"], before["Parent"])
        self.assertEqual(after["Sibling"], before["Sibling"])

    def test_state_restored_even_when_body_raises(self):
        from spritesheet_frame_selector.core.visibility import collection_visibility_scope

        keep, _obj = make_collection_with_cube("Keep")
        other, _obj2 = make_collection_with_cube("Other")
        view_layer = bpy.context.view_layer
        root = view_layer.layer_collection
        before = {lc.name: lc.exclude for lc in root.children}

        with self.assertRaises(RuntimeError):
            with collection_visibility_scope(view_layer, [keep], None):
                raise RuntimeError("boom")

        after = {lc.name: lc.exclude for lc in root.children}
        self.assertEqual(before, after)
        del other


class PreviewGenerationTests(unittest.TestCase):
    def setUp(self):
        reset_scene()
        use_fast_render_engine()
        self.camera = make_camera()
        self.collection, _obj = make_collection_with_cube()
        link_camera(self.camera, self.collection)
        self.workspace = new_workspace()
        set_workspace_defaults(self.workspace, self.camera, self.collection)
        self.clip = new_clip()
        self.clip.frame_start = 1
        self.clip.frame_end = 3
        from spritesheet_frame_selector.core.frame_math import frame_numbers
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        sync_clip_frames(self.clip, frame_numbers(1, 3, 1))

    def test_rendered_mode_generates_cache_in_background(self):
        self.clip.preview_mode = "RENDERED"
        self.assertEqual(bpy.ops.spritesheet.preview_generate(), {"FINISHED"})
        self.assertFalse(self.clip.cache_dirty)
        self.assertNotEqual(self.clip.cache_key, "")
        self.assertTrue(os.path.isdir(self.clip.cache_folder))
        for frame in self.clip.frames:
            self.assertTrue(os.path.isfile(frame.preview_path), frame.preview_path)
        self.assertIn("previews ready", self.clip.last_preview_note)

    def test_viewport_modes_fail_cleanly_without_a_3d_viewport(self):
        for mode in ("SOLID", "MATERIAL"):
            with self.subTest(mode=mode):
                self.clip.preview_mode = mode
                self.assertEqual(bpy.ops.spritesheet.preview_generate(), {"CANCELLED"})
                self.assertTrue(self.clip.cache_dirty)
                self.assertIn("3D Viewport", self.clip.last_preview_note)

    def test_preview_restores_render_settings(self):
        scene = bpy.context.scene
        scene.frame_set(9)
        scene.render.resolution_x = 111
        scene.render.film_transparent = False
        scene.render.image_settings.file_format = "JPEG"
        self.clip.preview_mode = "RENDERED"
        bpy.ops.spritesheet.preview_generate()
        self.assertEqual(scene.frame_current, 9)
        self.assertEqual(scene.render.resolution_x, 111)
        self.assertFalse(scene.render.film_transparent)
        self.assertEqual(scene.render.image_settings.file_format, "JPEG")

    def test_regenerate_purges_stale_sibling_caches(self):
        self.clip.preview_mode = "RENDERED"
        bpy.ops.spritesheet.preview_generate()
        first_folder = self.clip.cache_folder
        clip_root = os.path.dirname(first_folder)

        self.clip.preview_size = 128  # changes the cache key
        bpy.ops.spritesheet.preview_generate()
        second_folder = self.clip.cache_folder

        self.assertNotEqual(first_folder, second_folder)
        self.assertFalse(os.path.isdir(first_folder), "stale sibling cache must be purged")
        self.assertEqual(os.listdir(clip_root), [os.path.basename(second_folder)])

    def test_clear_cache_removes_files_but_keeps_selection(self):
        self.clip.preview_mode = "RENDERED"
        bpy.ops.spritesheet.preview_generate()
        folder = self.clip.cache_folder
        self.clip.frames[1].selected = False

        self.assertEqual(bpy.ops.spritesheet.preview_clear_cache(), {"FINISHED"})
        self.assertFalse(os.path.isdir(folder))
        self.assertEqual(self.clip.cache_key, "")
        self.assertTrue(self.clip.cache_dirty)
        self.assertEqual([f.preview_path for f in self.clip.frames], ["", "", ""])
        self.assertEqual([f.selected for f in self.clip.frames], [True, False, True])

    def test_clear_cache_refuses_to_delete_unmanaged_folders(self):
        with tempfile.TemporaryDirectory() as unmanaged:
            marker = os.path.join(unmanaged, "precious.txt")
            with open(marker, "w", encoding="utf-8") as handle:
                handle.write("keep me")
            self.clip.cache_folder = unmanaged
            self.assertEqual(bpy.ops.spritesheet.preview_clear_cache(), {"FINISHED"})
            self.assertTrue(os.path.isfile(marker), "unmanaged folder must not be deleted")
            self.assertEqual(self.clip.cache_key, "")

    def test_empty_frame_range_is_reported(self):
        self.clip.frame_start = 10
        self.clip.frame_end = 5
        self.clip.preview_mode = "RENDERED"
        self.assertEqual(bpy.ops.spritesheet.preview_generate(), {"CANCELLED"})
        self.assertEqual(self.clip.last_preview_note, "Frame range is empty")
        self.assertEqual(len(self.clip.frames), 0)

    def test_missing_camera_is_reported(self):
        self.workspace.default_camera = None
        self.clip.preview_mode = "RENDERED"
        self.assertEqual(bpy.ops.spritesheet.preview_generate(), {"CANCELLED"})
        self.assertEqual(self.clip.last_preview_note, "Missing effective camera")

    def test_transparency_probe_reads_real_png_alpha(self):
        from spritesheet_frame_selector.preview.generator import _preview_file_has_transparency

        with tempfile.TemporaryDirectory() as tmp:
            transparent = os.path.join(tmp, "t.png")
            opaque = os.path.join(tmp, "o.png")
            write_solid_png(transparent, 4, 4, (1.0, 0.0, 0.0, 0.0))
            write_solid_png(opaque, 4, 4, (1.0, 0.0, 0.0, 1.0))
            self.assertIs(_preview_file_has_transparency(transparent), True)
            self.assertIs(_preview_file_has_transparency(opaque), False)
            self.assertIsNone(_preview_file_has_transparency(os.path.join(tmp, "missing.png")))


class VisualSelectorTests(unittest.TestCase):
    def setUp(self):
        reset_scene()
        new_workspace()
        self.clip = new_clip()

    def test_selector_is_rejected_without_a_viewport(self):
        self.assertEqual(bpy.ops.spritesheet.visual_selector_open(), {"CANCELLED"})

    def test_selector_reports_when_clip_has_no_frames(self):
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        sync_clip_frames(self.clip, [])
        self.assertEqual(bpy.ops.spritesheet.visual_selector_open(), {"CANCELLED"})

    def test_set_mode_operator_persists_on_workspace(self):
        bpy.ops.spritesheet.visual_selector_set_mode(mode="PLAY")
        self.assertEqual(active_workspace().selector_mode, "PLAY")
        bpy.ops.spritesheet.visual_selector_set_mode(mode="EDIT")
        self.assertEqual(active_workspace().selector_mode, "EDIT")

    def test_cleanup_is_idempotent_without_a_session(self):
        from spritesheet_frame_selector.ui.visual_selector import cleanup_visual_selector_resources

        cleanup_visual_selector_resources()
        cleanup_visual_selector_resources()


class PlaybackRuntimeTests(unittest.TestCase):
    def setUp(self):
        reset_scene()
        use_fast_render_engine()
        camera = make_camera()
        collection, _obj = make_collection_with_cube()
        link_camera(camera, collection)
        self.workspace = new_workspace()
        set_workspace_defaults(self.workspace, camera, collection)
        self.clip = new_clip()
        self.clip.frame_start = 1
        self.clip.frame_end = 3
        self.clip.preview_mode = "RENDERED"
        from spritesheet_frame_selector.core.frame_math import frame_numbers
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        sync_clip_frames(self.clip, frame_numbers(1, 3, 1))
        bpy.ops.spritesheet.preview_generate()

    def tearDown(self):
        from spritesheet_frame_selector.playback.controller import cleanup_playback_resources

        cleanup_playback_resources()

    def test_play_registers_a_real_timer_and_stop_removes_it(self):
        from spritesheet_frame_selector.playback import controller

        self.assertEqual(bpy.ops.spritesheet.playback_play(), {"FINISHED"})
        self.assertTrue(controller.is_playing())
        self.assertTrue(bpy.app.timers.is_registered(controller._timer_callback))

        self.assertEqual(bpy.ops.spritesheet.playback_stop(), {"FINISHED"})
        self.assertFalse(controller.is_playing())
        self.assertFalse(bpy.app.timers.is_registered(controller._timer_callback))

    def test_pause_then_resume_keeps_position(self):
        from spritesheet_frame_selector.playback import controller

        bpy.ops.spritesheet.playback_play()
        controller.tick_playback()
        frame_before = controller.current_frame_number()
        bpy.ops.spritesheet.playback_pause()
        self.assertTrue(controller.is_paused())
        self.assertFalse(bpy.app.timers.is_registered(controller._timer_callback))

        bpy.ops.spritesheet.playback_play()
        self.assertTrue(controller.is_playing())
        self.assertEqual(controller.current_frame_number(), frame_before)

    def test_playback_loops_over_ready_frames(self):
        from spritesheet_frame_selector.playback import controller

        bpy.ops.spritesheet.playback_play(loop=True)
        seen = [controller.current_frame_number()]
        for _ in range(5):
            controller.tick_playback()
            seen.append(controller.current_frame_number())
        self.assertEqual(seen, [1, 2, 3, 1, 2, 3])

    def test_deselecting_frames_refreshes_the_live_session(self):
        from spritesheet_frame_selector.playback import controller

        bpy.ops.spritesheet.playback_play()
        self.assertEqual(controller.active_session_summary()["frame_count"], 3)
        bpy.ops.spritesheet.frame_toggle_selection(index=1)
        self.assertEqual(controller.active_session_summary()["frame_count"], 2)
        self.assertEqual(controller.active_session().frame_numbers, [1, 3])

    def test_deselecting_everything_stops_playback(self):
        from spritesheet_frame_selector.playback import controller

        bpy.ops.spritesheet.playback_play()
        bpy.ops.spritesheet.frame_deselect_all()
        self.assertFalse(controller.is_playing())
        self.assertIsNone(controller.active_session())

    def test_play_without_previews_is_reported(self):
        from spritesheet_frame_selector.playback import controller

        bpy.ops.spritesheet.preview_clear_cache()
        self.assertEqual(bpy.ops.spritesheet.playback_play(), {"CANCELLED"})
        self.assertFalse(controller.is_playing())

    def test_timer_is_unregistered_on_addon_unregister(self):
        import spritesheet_frame_selector as addon
        from spritesheet_frame_selector.playback import controller

        bpy.ops.spritesheet.playback_play()
        self.assertTrue(bpy.app.timers.is_registered(controller._timer_callback))
        addon.unregister()
        try:
            self.assertFalse(bpy.app.timers.is_registered(controller._timer_callback))
            self.assertIsNone(controller.active_session())
        finally:
            addon.register()

    def test_load_pre_handler_stops_playback_on_file_load(self):
        from spritesheet_frame_selector.playback import controller

        bpy.ops.spritesheet.playback_play()
        self.assertTrue(controller.is_playing())
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "reload.blend")
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.open_mainfile(filepath=path)
        self.assertFalse(controller.is_playing())
        self.assertIsNone(controller.active_session())
