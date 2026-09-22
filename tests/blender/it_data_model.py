"""Integration tests: registration lifecycle, persistent data model, CRUD operators."""

from __future__ import annotations

import os
import tempfile
import unittest

import bpy

from it_common import (
    active_workspace,
    make_camera,
    make_collection_with_cube,
    new_clip,
    new_workspace,
    reset_scene,
)

import spritesheet_frame_selector as addon


class RegistrationLifecycleTests(unittest.TestCase):
    """The addon must survive repeated register/unregister cycles."""

    def test_unregister_removes_scene_property_and_operators(self):
        # ``bpy.ops`` resolves lazily, so ``hasattr`` stays True after unregister;
        # ``dir(bpy.ops)`` and an actual call are the reliable probes.
        addon.unregister()
        try:
            self.assertFalse(hasattr(bpy.types.Scene, "spritesheet_state"))
            self.assertNotIn("spritesheet", dir(bpy.ops))
            with self.assertRaises(AttributeError):
                bpy.ops.spritesheet.workspace_add()
        finally:
            addon.register()
        self.assertTrue(hasattr(bpy.types.Scene, "spritesheet_state"))
        self.assertIn("spritesheet", dir(bpy.ops))

    def test_repeated_register_cycles_do_not_leak_classes(self):
        from spritesheet_frame_selector import registration

        baseline = len(registration._registered_classes)
        for _ in range(3):
            addon.unregister()
            addon.register()
        self.assertEqual(len(registration._registered_classes), baseline)

    def test_load_pre_handler_registered_once(self):
        from spritesheet_frame_selector.registration import _cleanup_runtime_sessions_on_load

        occurrences = [h for h in bpy.app.handlers.load_pre if h is _cleanup_runtime_sessions_on_load]
        self.assertEqual(len(occurrences), 1)


class PropertyDefaultsTests(unittest.TestCase):
    def setUp(self):
        reset_scene()

    def test_scene_state_defaults(self):
        state = bpy.context.scene.spritesheet_state
        self.assertEqual(state.schema_version, 2)
        self.assertEqual(len(state.workspaces), 0)
        self.assertEqual(state.active_workspace_index, -1)

    def test_negative_frame_values_are_clamped_to_zero(self):
        new_workspace()
        clip = new_clip()
        clip.frame_start = -50
        clip.frame_end = -10
        self.assertEqual(clip.frame_start, 0)
        self.assertEqual(clip.frame_end, 0)

    def test_frame_step_and_fps_have_positive_floors(self):
        new_workspace()
        clip = new_clip()
        clip.frame_step = 0
        clip.fps = 0
        self.assertEqual(clip.frame_step, 1)
        self.assertEqual(clip.fps, 1)

    def test_preview_size_is_bounded(self):
        new_workspace()
        clip = new_clip()
        clip.preview_size = 1
        self.assertEqual(clip.preview_size, 32)
        clip.preview_size = 9999
        self.assertEqual(clip.preview_size, 256)

    def test_camera_pointer_poll_rejects_non_cameras(self):
        new_workspace()
        clip = new_clip()
        mesh = bpy.data.meshes.new("m")
        obj = bpy.data.objects.new("NotACamera", mesh)
        # poll() is enforced by the UI; verify the poll function itself is wired.
        from spritesheet_frame_selector.properties import camera_object_poll

        self.assertFalse(camera_object_poll(clip, obj))
        self.assertTrue(camera_object_poll(clip, make_camera()))
        self.assertTrue(camera_object_poll(clip, None))


class WorkspaceCrudTests(unittest.TestCase):
    def setUp(self):
        reset_scene()

    def test_add_assigns_unique_id_and_incremental_name(self):
        first = new_workspace()
        second = new_workspace()
        self.assertNotEqual(first.id, "")
        self.assertNotEqual(first.id, second.id)
        self.assertEqual(first.name, "Workspace")
        self.assertEqual(second.name, "Workspace 2")

    def test_remove_clamps_active_index(self):
        new_workspace()
        new_workspace()
        state = bpy.context.scene.spritesheet_state
        self.assertEqual(state.active_workspace_index, 1)
        bpy.ops.spritesheet.workspace_remove()
        self.assertEqual(len(state.workspaces), 1)
        self.assertEqual(state.active_workspace_index, 0)
        bpy.ops.spritesheet.workspace_remove()
        self.assertEqual(len(state.workspaces), 0)
        self.assertEqual(state.active_workspace_index, -1)

    def test_remove_on_empty_state_is_a_noop(self):
        state = bpy.context.scene.spritesheet_state
        self.assertEqual(bpy.ops.spritesheet.workspace_remove(), {"FINISHED"})
        self.assertEqual(state.active_workspace_index, -1)

    def test_move_reorders_and_follows_active(self):
        first = new_workspace("Alpha")
        second = new_workspace("Beta")
        state = bpy.context.scene.spritesheet_state
        bpy.ops.spritesheet.workspace_move(direction="UP")
        self.assertEqual([w.name for w in state.workspaces], ["Beta", "Alpha"])
        self.assertEqual(state.active_workspace_index, 0)
        bpy.ops.spritesheet.workspace_move(direction="UP")  # already at top
        self.assertEqual(state.active_workspace_index, 0)
        del first, second

    def test_select_clamps_out_of_range_index(self):
        new_workspace()
        state = bpy.context.scene.spritesheet_state
        bpy.ops.spritesheet.workspace_select(index=99)
        self.assertEqual(state.active_workspace_index, 0)
        bpy.ops.spritesheet.workspace_select(index=-5)
        self.assertEqual(state.active_workspace_index, 0)

    def test_duplicate_deep_copies_clips_with_fresh_ids(self):
        workspace = new_workspace("Source")
        camera = make_camera()
        collection, _obj = make_collection_with_cube()
        workspace.default_camera = camera
        bpy.ops.spritesheet.workspace_default_collection_add()
        workspace.default_collections[0].collection = collection
        clip = new_clip("Walk")
        clip.frame_start = 3
        clip.frame_end = 9
        clip.frames[0].selected = False

        bpy.ops.spritesheet.workspace_duplicate()
        state = bpy.context.scene.spritesheet_state
        copy = state.workspaces[1]

        self.assertEqual(copy.name, "Source 2")
        self.assertNotEqual(copy.id, workspace.id)
        self.assertEqual(copy.default_camera, camera)
        self.assertEqual(copy.default_collections[0].collection, collection)
        self.assertEqual(len(copy.clips), 1)
        self.assertNotEqual(copy.clips[0].id, clip.id)
        self.assertEqual(copy.clips[0].frame_start, 3)
        self.assertEqual(copy.clips[0].frame_end, 9)
        self.assertFalse(copy.clips[0].frames[0].selected)
        self.assertTrue(copy.clips[0].cache_dirty)

    def test_only_one_default_collection_allowed(self):
        new_workspace()
        self.assertEqual(bpy.ops.spritesheet.workspace_default_collection_add(), {"FINISHED"})
        self.assertEqual(bpy.ops.spritesheet.workspace_default_collection_add(), {"CANCELLED"})
        self.assertEqual(len(active_workspace().default_collections), 1)


class ClipCrudTests(unittest.TestCase):
    def setUp(self):
        reset_scene()
        new_workspace()

    def test_clip_names_are_unique_on_create(self):
        a = new_clip()
        b = new_clip()
        c = new_clip()
        self.assertEqual([a.name, b.name, c.name], ["Clip", "Clip 2", "Clip 3"])

    def test_renaming_to_an_existing_name_auto_suffixes(self):
        new_clip("Walk")
        second = new_clip("Run")
        second.name = "Walk"
        self.assertEqual(second.name, "Walk 2")

    def test_blank_rename_falls_back_to_default_base(self):
        clip = new_clip("Walk")
        clip.name = "   "
        self.assertEqual(clip.name, "Clip")

    def test_duplicate_clip_gets_new_id_and_unique_name(self):
        from spritesheet_frame_selector.core.frame_math import frame_numbers
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        source = new_clip("Walk")
        source.frame_start = 5
        source.frame_end = 8
        source.fps = 24
        sync_clip_frames(source, frame_numbers(5, 8, 1))
        source.frames[1].selected = False

        bpy.ops.spritesheet.clip_duplicate()
        workspace = active_workspace()
        copy = workspace.clips[1]
        self.assertEqual(copy.name, "Walk 2")
        self.assertNotEqual(copy.id, source.id)
        self.assertEqual(copy.fps, 24)
        self.assertEqual([f.frame_number for f in copy.frames], [5, 6, 7, 8])
        self.assertEqual([f.selected for f in copy.frames], [True, False, True, True])
        # Derived cache state must not be inherited.
        self.assertTrue(copy.cache_dirty)
        self.assertEqual(copy.cache_key, "")
        self.assertEqual([f.preview_path for f in copy.frames], [""] * 4)

    def test_editing_frame_range_does_not_resync_stored_frames(self):
        """Contract: ``clip.frames`` is resynced lazily (preview generation / export).

        Documented here because the panel surfaces "Expected" and "Stored" frame
        counts separately; the counts diverge until a sync point runs.
        """
        clip = new_clip("Walk")
        self.assertEqual(len(clip.frames), 20)
        clip.frame_start = 5
        clip.frame_end = 8
        self.assertEqual(len(clip.frames), 20)  # still stale
        self.assertTrue(clip.cache_dirty)

        from spritesheet_frame_selector.core.frame_math import frame_numbers
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        sync_clip_frames(clip, frame_numbers(5, 8, 1))
        self.assertEqual([f.frame_number for f in clip.frames], [5, 6, 7, 8])

    def test_new_clip_syncs_frames_from_default_range(self):
        clip = new_clip()
        self.assertEqual(len(clip.frames), 20)
        self.assertEqual(clip.frames[0].frame_number, 1)
        self.assertEqual(clip.frames[-1].frame_number, 20)
        self.assertTrue(all(f.selected for f in clip.frames))

    def test_remove_clip_clamps_active_index(self):
        new_clip()
        new_clip()
        workspace = active_workspace()
        self.assertEqual(workspace.active_clip_index, 1)
        bpy.ops.spritesheet.clip_remove()
        self.assertEqual(workspace.active_clip_index, 0)
        bpy.ops.spritesheet.clip_remove()
        self.assertEqual(workspace.active_clip_index, -1)

    def test_clip_operators_report_cancelled_without_workspace(self):
        reset_scene()
        self.assertEqual(bpy.ops.spritesheet.clip_add(), {"CANCELLED"})
        self.assertEqual(bpy.ops.spritesheet.clip_duplicate(), {"CANCELLED"})

    def test_clip_included_collection_add_and_remove(self):
        clip = new_clip()
        bpy.ops.spritesheet.clip_included_collection_add()
        bpy.ops.spritesheet.clip_included_collection_add()
        self.assertEqual(len(clip.included_collections), 2)
        bpy.ops.spritesheet.clip_included_collection_remove(index=0)
        self.assertEqual(len(clip.included_collections), 1)
        # Out-of-range removal must not raise or change anything.
        bpy.ops.spritesheet.clip_included_collection_remove(index=99)
        self.assertEqual(len(clip.included_collections), 1)

    def test_collection_pointer_records_last_known_name(self):
        clip = new_clip()
        collection, _obj = make_collection_with_cube("Hero")
        bpy.ops.spritesheet.clip_included_collection_add()
        clip.included_collections[0].collection = collection
        self.assertEqual(clip.included_collections[0].collection_name, "Hero")


class SelectionOperatorTests(unittest.TestCase):
    def setUp(self):
        reset_scene()
        new_workspace()
        self.clip = new_clip()
        self.clip.frame_start = 1
        self.clip.frame_end = 6
        from spritesheet_frame_selector.core.frame_math import frame_numbers
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        sync_clip_frames(self.clip, frame_numbers(1, 6, 1))

    def selected(self):
        return [f.selected for f in self.clip.frames]

    def test_select_and_deselect_all(self):
        bpy.ops.spritesheet.frame_deselect_all()
        self.assertEqual(self.selected(), [False] * 6)
        bpy.ops.spritesheet.frame_select_all()
        self.assertEqual(self.selected(), [True] * 6)

    def test_invert(self):
        bpy.ops.spritesheet.frame_deselect_all()
        self.clip.frames[0].selected = True
        bpy.ops.spritesheet.frame_invert_selection()
        self.assertEqual(self.selected(), [False, True, True, True, True, True])

    def test_every_n(self):
        bpy.ops.spritesheet.frame_select_every_n(n=3)
        self.assertEqual(self.selected(), [True, False, False, True, False, False])

    def test_toggle_rejects_out_of_range_index(self):
        self.assertEqual(bpy.ops.spritesheet.frame_toggle_selection(index=99), {"CANCELLED"})
        self.assertEqual(bpy.ops.spritesheet.frame_toggle_selection(index=-1), {"CANCELLED"})
        self.assertEqual(self.selected(), [True] * 6)

    def test_toggle_flips_single_frame(self):
        bpy.ops.spritesheet.frame_toggle_selection(index=2)
        self.assertFalse(self.clip.frames[2].selected)
        bpy.ops.spritesheet.frame_toggle_selection(index=2)
        self.assertTrue(self.clip.frames[2].selected)


class FrameSyncPersistenceTests(unittest.TestCase):
    def setUp(self):
        reset_scene()
        new_workspace()
        self.clip = new_clip()

    def test_range_change_preserves_selection_by_frame_number(self):
        from spritesheet_frame_selector.core.frame_math import frame_numbers
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        self.clip.frames[4].selected = False  # frame 5
        self.clip.frame_end = 30
        sync_clip_frames(self.clip, frame_numbers(self.clip.frame_start, self.clip.frame_end, 1))
        self.assertEqual(len(self.clip.frames), 30)
        self.assertFalse(self.clip.frames[4].selected)
        self.assertTrue(self.clip.frames[25].selected)

    def test_editing_range_marks_cache_dirty(self):
        self.clip.cache_dirty = False
        self.clip.frame_end = 25
        self.assertTrue(self.clip.cache_dirty)

    def test_changing_workspace_default_camera_dirties_all_clips(self):
        second = new_clip()
        self.clip.cache_dirty = False
        second.cache_dirty = False
        active_workspace().default_camera = make_camera()
        self.assertTrue(self.clip.cache_dirty)
        self.assertTrue(second.cache_dirty)


class BlendPersistenceTests(unittest.TestCase):
    """State must survive a save/reload round trip."""

    def test_state_round_trips_through_a_blend_file(self):
        reset_scene()
        workspace = new_workspace("Hero")
        camera = make_camera("HeroCam")
        collection, _obj = make_collection_with_cube("HeroProps")
        collection.objects.link(camera)
        workspace.default_camera = camera
        bpy.ops.spritesheet.workspace_default_collection_add()
        workspace.default_collections[0].collection = collection
        workspace.selector_mode = "PLAY"
        workspace.export_settings.sheet_name = "hero_sheet"
        workspace.export_settings.columns = 5

        clip = new_clip("Idle")
        clip.frame_start = 2
        clip.frame_end = 7
        clip.fps = 18
        clip.preview_mode = "MATERIAL"
        from spritesheet_frame_selector.core.frame_math import frame_numbers
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        sync_clip_frames(clip, frame_numbers(2, 7, 1))
        clip.frames[1].selected = False  # frame 3

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "persist.blend")
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.read_factory_settings(use_empty=True)
            self.assertEqual(len(bpy.context.scene.spritesheet_state.workspaces), 0)
            bpy.ops.wm.open_mainfile(filepath=path)

            state = bpy.context.scene.spritesheet_state
            self.assertEqual(state.schema_version, 2)
            self.assertEqual(len(state.workspaces), 1)
            reloaded = state.workspaces[0]
            self.assertEqual(reloaded.name, "Hero")
            self.assertEqual(reloaded.selector_mode, "PLAY")
            self.assertEqual(reloaded.export_settings.sheet_name, "hero_sheet")
            self.assertEqual(reloaded.export_settings.columns, 5)
            self.assertIsNotNone(reloaded.default_camera)
            self.assertEqual(reloaded.default_camera.name, "HeroCam")
            self.assertEqual(reloaded.default_collections[0].collection.name, "HeroProps")

            self.assertEqual(len(reloaded.clips), 1)
            reloaded_clip = reloaded.clips[0]
            self.assertEqual(reloaded_clip.name, "Idle")
            self.assertEqual(reloaded_clip.fps, 18)
            self.assertEqual(reloaded_clip.preview_mode, "MATERIAL")
            self.assertEqual([f.frame_number for f in reloaded_clip.frames], [2, 3, 4, 5, 6, 7])
            self.assertEqual(
                [f.selected for f in reloaded_clip.frames],
                [True, False, True, True, True, True],
            )

    def test_deleted_collection_leaves_recoverable_name(self):
        reset_scene()
        workspace = new_workspace()
        collection, _obj = make_collection_with_cube("Doomed")
        bpy.ops.spritesheet.workspace_default_collection_add()
        workspace.default_collections[0].collection = collection
        self.assertEqual(workspace.default_collections[0].collection_name, "Doomed")

        bpy.data.collections.remove(collection)
        item = active_workspace().default_collections[0]
        self.assertIsNone(item.collection)
        self.assertEqual(item.collection_name, "Doomed")

        from spritesheet_frame_selector.core.validation import validate_preview_context

        clip = new_clip()
        errors = validate_preview_context(active_workspace(), clip)
        self.assertIn("Missing collection: Doomed", errors)
