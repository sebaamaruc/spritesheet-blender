"""Integration tests: modal visual selector event dispatch and geometry.

The modal surface needs a real 3D Viewport to *draw*, but its event handling is
plain Python. These tests install a session by hand, populate the hit-test cells
the draw pass would have produced, and feed synthetic events through the real
dispatcher.
"""

from __future__ import annotations

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
)

from spritesheet_frame_selector.ui import visual_selector as vs


def make_event(event_type="MOUSEMOVE", value="PRESS", x=100, y=100, **kwargs):
    event = SimpleNamespace(
        type=event_type,
        value=value,
        mouse_region_x=x,
        mouse_region_y=y,
        alt=False,
        ctrl=False,
        oskey=False,
        shift=False,
        mouse_x=x,
        mouse_y=y,
        mouse_prev_x=x,
        mouse_prev_y=y,
    )
    for key, val in kwargs.items():
        setattr(event, key, val)
    return event


class SelectorGeometryTests(unittest.TestCase):
    def test_panel_rect_shrinks_for_small_regions(self):
        big = vs._selector_panel_rect(1600, 1000, None)
        small = vs._selector_panel_rect(400, 300, None)
        self.assertEqual(big.x, vs.SURFACE_SAFE_LEFT)
        self.assertEqual(small.x, 12)
        self.assertGreaterEqual(small.width, 260)
        self.assertGreaterEqual(small.height, 220)

    def test_panel_rect_reserves_room_for_the_sidebar(self):
        area = SimpleNamespace(regions=[SimpleNamespace(type="UI", width=300, x=1300)])
        without = vs._selector_panel_rect(1600, 1000, None)
        with_sidebar = vs._selector_panel_rect(1600, 1000, area)
        self.assertLess(with_sidebar.width, without.width)

    def test_sidebar_without_x_falls_back_to_bounded_width(self):
        area = SimpleNamespace(regions=[SimpleNamespace(type="UI", width=900, x=None)])
        self.assertLessEqual(vs._right_ui_overlay_width(area, 1600), 460.0)

    def test_collapsed_sidebar_is_ignored(self):
        area = SimpleNamespace(regions=[SimpleNamespace(type="UI", width=1, x=1599)])
        self.assertEqual(vs._right_ui_overlay_width(area, 1600), 0)

    def test_rect_contains_is_inclusive_on_edges(self):
        rect = vs.Rect(10, 20, 100, 50)
        self.assertTrue(rect.contains(10, 20))
        self.assertTrue(rect.contains(110, 70))
        self.assertFalse(rect.contains(9.9, 20))
        self.assertFalse(rect.contains(110.1, 70))

    def test_image_fit_rect_preserves_aspect_and_centers(self):
        wide = SimpleNamespace(size=(200, 100))
        fitted = vs._image_fit_rect(wide, vs.Rect(0, 0, 100, 100))
        self.assertAlmostEqual(fitted.width, 100)
        self.assertAlmostEqual(fitted.height, 50)
        self.assertAlmostEqual(fitted.y, 25)

    def test_grid_scroll_helpers(self):
        self.assertEqual(vs.clamp_grid_offset(-5, 30, 10), 0)
        self.assertEqual(vs.clamp_grid_offset(99, 30, 10), 20)
        self.assertEqual(vs.scrolled_grid_offset(0, 1, 30, 10, 5), 5)
        self.assertEqual(vs.scrolled_grid_offset(0, -1, 30, 10, 5), 0)
        self.assertEqual(vs.scroll_direction_from_event(make_event("WHEELDOWNMOUSE")), 1)
        self.assertEqual(vs.scroll_direction_from_event(make_event("WHEELUPMOUSE")), -1)


class SelectorEventDispatchTests(unittest.TestCase):
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
        self.clip.frame_end = 4
        self.clip.preview_mode = "RENDERED"
        from spritesheet_frame_selector.core.frame_math import frame_numbers
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        sync_clip_frames(self.clip, frame_numbers(1, 4, 1))
        bpy.ops.spritesheet.preview_generate()

        self.session = self.install_session()

    def tearDown(self):
        vs._session = None
        from spritesheet_frame_selector.playback.controller import cleanup_playback_resources

        cleanup_playback_resources()

    def install_session(self):
        """Install a session with the hit-test cells the draw pass would create."""
        fake_context = SimpleNamespace(
            area=None,
            region=SimpleNamespace(width=1200, height=800),
        )
        session = vs.VisualSelectorSession(
            operator=None,
            context=fake_context,
            workspace_id=self.workspace.id,
            clip_id=self.clip.id,
        )
        session.grid_columns = 4
        session.grid_max_visible = 4
        session.frame_cells = [
            vs.FrameCell(index, vs.Rect(100 + index * 60, 100, 50, 50))
            for index in range(len(self.clip.frames))
        ]
        session.button_cells = [
            vs.ButtonCell(action, vs.Rect(600, 100 + offset * 30, 80, 24))
            for offset, action in enumerate(
                ("mode_edit", "mode_play", "play", "pause", "stop",
                 "select_all", "deselect_all", "invert", "every_n", "close")
            )
        ]
        vs._session = session
        return session

    def click_button(self, action):
        cell = next(c for c in self.session.button_cells if c.action == action)
        return vs.handle_visual_selector_event(
            bpy.context,
            make_event("LEFTMOUSE", "PRESS", x=cell.rect.x + 5, y=cell.rect.y + 5),
        )

    def click_frame(self, index):
        cell = self.session.frame_cells[index]
        return vs.handle_visual_selector_event(
            bpy.context,
            make_event("LEFTMOUSE", "PRESS", x=cell.rect.x + 5, y=cell.rect.y + 5),
        )

    # -- lifecycle --------------------------------------------------------
    def test_escape_cancels_and_releases_the_session(self):
        result = vs.handle_visual_selector_event(bpy.context, make_event("ESC", "PRESS"))
        self.assertEqual(result, {"CANCELLED"})
        self.assertIsNone(vs._session)

    def test_right_mouse_cancels(self):
        self.assertEqual(
            vs.handle_visual_selector_event(bpy.context, make_event("RIGHTMOUSE", "PRESS")),
            {"CANCELLED"},
        )
        self.assertIsNone(vs._session)

    def test_events_are_rejected_once_the_clip_changes(self):
        bpy.ops.spritesheet.clip_add()  # different active clip
        result = vs.handle_visual_selector_event(bpy.context, make_event("MOUSEMOVE"))
        self.assertEqual(result, {"CANCELLED"})
        self.assertIsNone(vs._session)

    def test_navigation_events_pass_through_to_the_viewport(self):
        for event_type in ("MIDDLEMOUSE", "TRACKPADZOOM", "NDOF_MOTION"):
            with self.subTest(event_type=event_type):
                self.assertEqual(
                    vs.handle_visual_selector_event(bpy.context, make_event(event_type)),
                    {"RUNNING_MODAL", "PASS_THROUGH"},
                )

    def test_modifier_events_pass_through(self):
        self.assertEqual(
            vs.handle_visual_selector_event(bpy.context, make_event("SPACE", "PRESS", ctrl=True)),
            {"RUNNING_MODAL", "PASS_THROUGH"},
        )

    def test_click_outside_the_panel_passes_through(self):
        self.assertEqual(
            vs.handle_visual_selector_event(
                bpy.context, make_event("LEFTMOUSE", "PRESS", x=5, y=5)
            ),
            {"RUNNING_MODAL", "PASS_THROUGH"},
        )

    # -- selection --------------------------------------------------------
    def test_edit_mode_click_toggles_selection(self):
        self.workspace.selector_mode = "EDIT"
        self.assertTrue(self.clip.frames[2].selected)
        self.click_frame(2)
        self.assertFalse(self.clip.frames[2].selected)
        self.click_frame(2)
        self.assertTrue(self.clip.frames[2].selected)

    def test_play_mode_click_moves_the_cursor_without_changing_selection(self):
        self.workspace.selector_mode = "PLAY"
        before = [f.selected for f in self.clip.frames]
        self.click_frame(3)
        self.assertEqual([f.selected for f in self.clip.frames], before)
        self.assertEqual(self.clip.active_frame_index, 3)

    def test_selection_buttons_delegate_to_registered_operators(self):
        self.click_button("deselect_all")
        self.assertEqual([f.selected for f in self.clip.frames], [False] * 4)
        self.click_button("select_all")
        self.assertEqual([f.selected for f in self.clip.frames], [True] * 4)
        self.click_button("invert")
        self.assertEqual([f.selected for f in self.clip.frames], [False] * 4)
        self.click_button("every_n")
        self.assertEqual([f.selected for f in self.clip.frames], [True, False, True, False])

    def test_mode_buttons_persist_selector_mode(self):
        self.click_button("mode_play")
        self.assertEqual(active_workspace().selector_mode, "PLAY")
        self.click_button("mode_edit")
        self.assertEqual(active_workspace().selector_mode, "EDIT")

    def test_tab_toggles_selector_mode(self):
        self.workspace.selector_mode = "EDIT"
        vs.handle_visual_selector_event(bpy.context, make_event("TAB", "PRESS"))
        self.assertEqual(active_workspace().selector_mode, "PLAY")
        vs.handle_visual_selector_event(bpy.context, make_event("TAB", "PRESS"))
        self.assertEqual(active_workspace().selector_mode, "EDIT")

    # -- playback ---------------------------------------------------------
    def test_playback_buttons_drive_the_controller(self):
        from spritesheet_frame_selector.playback import controller

        self.click_button("play")
        self.assertTrue(controller.is_playing())
        self.click_button("pause")
        self.assertTrue(controller.is_paused())
        self.click_button("play")
        self.assertTrue(controller.is_playing())
        self.click_button("stop")
        self.assertIsNone(controller.active_session())

    def test_space_toggles_play_pause_and_switches_to_play_mode(self):
        from spritesheet_frame_selector.playback import controller

        self.workspace.selector_mode = "EDIT"
        vs.handle_visual_selector_event(bpy.context, make_event("SPACE", "PRESS"))
        self.assertTrue(controller.is_playing())
        self.assertEqual(active_workspace().selector_mode, "PLAY")
        vs.handle_visual_selector_event(bpy.context, make_event("SPACE", "PRESS"))
        self.assertTrue(controller.is_paused())
        vs.handle_visual_selector_event(bpy.context, make_event("SPACE", "PRESS"))
        self.assertTrue(controller.is_playing())

    def test_shift_left_arrow_returns_to_first_frame_and_stops(self):
        from spritesheet_frame_selector.playback import controller

        self.click_button("play")
        controller.tick_playback()
        vs.handle_visual_selector_event(
            bpy.context, make_event("LEFT_ARROW", "PRESS", shift=True)
        )
        self.assertFalse(controller.is_playing())
        self.assertEqual(self.clip.active_frame_index, 0)

    def test_play_mode_click_seeks_the_live_session(self):
        from spritesheet_frame_selector.playback import controller

        self.workspace.selector_mode = "PLAY"
        self.click_button("play")
        self.click_frame(2)
        self.assertEqual(controller.current_frame_number(), 3)
        self.assertTrue(controller.is_playing())

    def test_toggling_a_frame_off_refreshes_the_live_session(self):
        from spritesheet_frame_selector.playback import controller

        self.workspace.selector_mode = "EDIT"
        self.click_button("play")
        self.assertEqual(controller.active_session_summary()["frame_count"], 4)
        self.click_frame(0)
        self.assertEqual(controller.active_session().frame_numbers, [2, 3, 4])

    # -- scrolling --------------------------------------------------------
    def test_wheel_scrolls_the_grid_inside_the_panel(self):
        from spritesheet_frame_selector.core.frame_math import frame_numbers
        from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

        sync_clip_frames(self.clip, frame_numbers(1, 40, 1))
        self.session.grid_columns = 4
        self.session.grid_max_visible = 8

        vs.handle_visual_selector_event(
            bpy.context, make_event("WHEELDOWNMOUSE", "PRESS", x=400, y=400)
        )
        self.assertEqual(self.session.grid_offset, 4)
        vs.handle_visual_selector_event(
            bpy.context, make_event("WHEELUPMOUSE", "PRESS", x=400, y=400)
        )
        self.assertEqual(self.session.grid_offset, 0)

    def test_wheel_outside_the_panel_passes_through_without_scrolling(self):
        result = vs.handle_visual_selector_event(
            bpy.context, make_event("WHEELDOWNMOUSE", "PRESS", x=5, y=5)
        )
        self.assertEqual(result, {"RUNNING_MODAL", "PASS_THROUGH"})
        self.assertEqual(self.session.grid_offset, 0)

    # -- close button -----------------------------------------------------
    def test_close_button_releases_the_session(self):
        self.click_button("close")
        self.assertIsNone(vs._session)
        # The modal operator only learns about it on the next event.
        self.assertEqual(
            vs.handle_visual_selector_event(bpy.context, make_event("MOUSEMOVE")),
            {"CANCELLED"},
        )

    def test_close_stops_playback(self):
        from spritesheet_frame_selector.playback import controller

        self.click_button("play")
        self.click_button("close")
        self.assertIsNone(controller.active_session())

    # -- cache invalidation ----------------------------------------------
    def test_regenerating_previews_drops_cached_selector_images(self):
        path = self.clip.frames[0].preview_path
        image = vs._load_preview_image(self.session, path)
        self.assertIsNotNone(image)
        self.assertIn(path, self.session.images)
        self.session.image_cache_key = "abc"

        before = len(bpy.data.images)
        vs.notify_preview_cache_regenerated(self.workspace.id, self.clip.id)
        self.assertEqual(self.session.images, {})
        self.assertEqual(self.session.image_cache_key, "")
        # the unused datablock must be released, not leaked
        self.assertEqual(len(bpy.data.images), before - 1)

    def test_regeneration_for_another_clip_is_ignored(self):
        self.session.image_cache_key = "abc"
        vs.notify_preview_cache_regenerated("other-workspace", "other-clip")
        self.assertEqual(self.session.image_cache_key, "abc")

    def test_display_frame_falls_back_through_active_then_selected(self):
        self.clip.active_frame_index = 2
        self.assertEqual(vs._current_display_frame(self.workspace, self.clip), 3)
        self.clip.active_frame_index = -1
        for frame in self.clip.frames:
            frame.selected = False
        self.clip.frames[1].selected = True
        self.assertEqual(vs._current_display_frame(self.workspace, self.clip), 2)
        for frame in self.clip.frames:
            frame.selected = False
        self.assertEqual(vs._current_display_frame(self.workspace, self.clip), 1)
