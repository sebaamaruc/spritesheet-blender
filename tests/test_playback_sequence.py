import unittest
import sys
from types import SimpleNamespace

if "bpy" not in sys.modules:
    sys.modules["bpy"] = SimpleNamespace(
        app=SimpleNamespace(
            timers=SimpleNamespace(
                register=lambda *_args, **_kwargs: None,
                unregister=lambda *_args, **_kwargs: None,
                is_registered=lambda *_args, **_kwargs: False,
            )
        ),
        ops=SimpleNamespace(
            render=SimpleNamespace(
                opengl=lambda **_kwargs: {"FINISHED"},
                render=lambda **_kwargs: {"FINISHED"},
            ),
        ),
        context=SimpleNamespace(window_manager=SimpleNamespace(windows=[])),
        types=SimpleNamespace(
            Context=object,
            PropertyGroup=object,
            Object=object,
            Collection=object,
        ),
    )

from spritesheet_frame_selector.playback import controller
from spritesheet_frame_selector.playback.controller import PlaybackSession
from spritesheet_frame_selector.playback.controller import refresh_playback_session
from spritesheet_frame_selector.playback.controller import resume_playback
from spritesheet_frame_selector.playback.controller import seek_playback_frame
from spritesheet_frame_selector.playback.sequence import (
    next_playback_index,
    playback_frame_numbers,
    playback_interval_seconds,
    playback_preview_paths,
    playback_ready_summary,
    selected_playback_frames,
)


def fake_frame(frame_number, selected=False, preview_path=""):
    return SimpleNamespace(
        frame_number=frame_number,
        selected=selected,
        preview_path=preview_path,
    )


def fake_clip():
    return SimpleNamespace(
        frames=[
            fake_frame(10, selected=True, preview_path="/tmp/10.png"),
            fake_frame(1, selected=False, preview_path="/tmp/1.png"),
            fake_frame(5, selected=True, preview_path=""),
            fake_frame(3, selected=True, preview_path="/tmp/3.png"),
        ],
        cache_key="cache",
        cache_folder="/tmp/cache",
        cache_dirty=False,
    )


class PlaybackSequenceTests(unittest.TestCase):
    def tearDown(self):
        controller._session = None
        controller._timer_registered = False
        controller.bpy.context = SimpleNamespace(window_manager=SimpleNamespace(windows=[]))

    def test_selected_frames_are_sorted_by_frame_number(self):
        clip = fake_clip()

        self.assertEqual(
            [frame.frame_number for frame in selected_playback_frames(clip)],
            [3, 5, 10],
        )

    def test_playback_frame_numbers_use_only_ready_selected_frames(self):
        self.assertEqual(playback_frame_numbers(fake_clip()), [3, 10])

    def test_playback_preview_paths_use_only_ready_selected_frames(self):
        self.assertEqual(
            playback_preview_paths(fake_clip()),
            ["/tmp/3.png", "/tmp/10.png"],
        )

    def test_playback_interval_rejects_invalid_fps(self):
        self.assertAlmostEqual(playback_interval_seconds(12), 1 / 12)
        with self.assertRaises(ValueError):
            playback_interval_seconds(0)

    def test_next_playback_index_without_loop_finishes(self):
        self.assertEqual(next_playback_index(0, 2, loop=False), 1)
        self.assertIsNone(next_playback_index(1, 2, loop=False))

    def test_next_playback_index_with_loop_wraps(self):
        self.assertEqual(next_playback_index(1, 2, loop=True), 0)

    def test_next_playback_index_empty_sequence_finishes(self):
        self.assertIsNone(next_playback_index(0, 0, loop=True))

    def test_ready_summary_reports_missing_previews(self):
        summary = playback_ready_summary(fake_clip())

        self.assertEqual(summary.selected, 3)
        self.assertEqual(summary.ready, 2)
        self.assertEqual(summary.missing_preview, 1)
        self.assertTrue(summary.can_play)

    def test_helpers_do_not_mutate_selection_or_cache(self):
        clip = fake_clip()
        before_selection = [frame.selected for frame in clip.frames]

        playback_frame_numbers(clip)
        playback_preview_paths(clip)

        self.assertEqual([frame.selected for frame in clip.frames], before_selection)
        self.assertEqual(clip.cache_key, "cache")
        self.assertEqual(clip.cache_folder, "/tmp/cache")
        self.assertFalse(clip.cache_dirty)

    def test_seek_playback_frame_moves_to_existing_frame_and_preserves_status(self):
        controller._session = PlaybackSession(
            workspace_id="workspace",
            clip_id="clip",
            frame_numbers=[3, 10, 12],
            preview_paths=["/tmp/3.png", "/tmp/10.png", "/tmp/12.png"],
            fps=12,
            loop=True,
            current_index=0,
            status="playing",
        )

        self.assertTrue(seek_playback_frame(10))
        self.assertEqual(controller._session.current_index, 1)
        self.assertEqual(controller._session.status, "playing")

    def test_seek_playback_frame_returns_false_for_missing_frame(self):
        controller._session = PlaybackSession(
            workspace_id="workspace",
            clip_id="clip",
            frame_numbers=[3, 10],
            preview_paths=["/tmp/3.png", "/tmp/10.png"],
            fps=12,
            loop=True,
            current_index=1,
            status="paused",
        )

        self.assertFalse(seek_playback_frame(99))
        self.assertEqual(controller._session.current_index, 1)
        self.assertEqual(controller._session.status, "paused")

    def test_seek_playback_frame_returns_false_without_session(self):
        controller._session = None

        self.assertFalse(seek_playback_frame(3))

    def test_resume_playback_uses_current_fps_when_provided(self):
        controller._session = PlaybackSession(
            workspace_id="workspace",
            clip_id="clip",
            frame_numbers=[3, 10],
            preview_paths=["/tmp/3.png", "/tmp/10.png"],
            fps=12,
            loop=True,
            current_index=0,
            status="paused",
        )

        self.assertTrue(resume_playback(fps=24))
        self.assertEqual(controller._session.fps, 24)
        self.assertEqual(controller._session.status, "playing")

    def test_resume_playback_rejects_invalid_current_fps(self):
        controller._session = PlaybackSession(
            workspace_id="workspace",
            clip_id="clip",
            frame_numbers=[3, 10],
            preview_paths=["/tmp/3.png", "/tmp/10.png"],
            fps=12,
            loop=True,
            current_index=0,
            status="paused",
        )

        self.assertFalse(resume_playback(fps=0))
        self.assertEqual(controller._session.fps, 12)
        self.assertEqual(controller._session.status, "paused")

    def test_tag_redraw_only_marks_view3d_areas(self):
        class FakeArea:
            def __init__(self, area_type):
                self.type = area_type
                self.redraws = 0

            def tag_redraw(self):
                self.redraws += 1

        view3d = FakeArea("VIEW_3D")
        properties = FakeArea("PROPERTIES")
        outliner = FakeArea("OUTLINER")
        controller.bpy.context = SimpleNamespace(
            window_manager=SimpleNamespace(
                windows=[
                    SimpleNamespace(
                        screen=SimpleNamespace(
                            areas=[view3d, properties, outliner],
                        )
                    )
                ]
            )
        )

        controller._tag_redraw()

        self.assertEqual(view3d.redraws, 1)
        self.assertEqual(properties.redraws, 0)
        self.assertEqual(outliner.redraws, 0)

    def test_refresh_playback_session_replaces_stale_selection_snapshot(self):
        controller._session = PlaybackSession(
            workspace_id="workspace",
            clip_id="clip",
            frame_numbers=[3, 10],
            preview_paths=["/tmp/3.png", "/tmp/10.png"],
            fps=12,
            loop=True,
            current_index=1,
            status="playing",
        )

        refreshed = refresh_playback_session(
            workspace_id="workspace",
            clip_id="clip",
            frame_numbers=[3, 12],
            preview_paths=["/tmp/3.png", "/tmp/12.png"],
            fps=24,
        )

        self.assertTrue(refreshed)
        self.assertEqual(controller._session.frame_numbers, [3, 12])
        self.assertEqual(controller._session.preview_paths, ["/tmp/3.png", "/tmp/12.png"])
        self.assertEqual(controller._session.fps, 24)
        self.assertEqual(controller._session.current_index, 1)
        self.assertEqual(controller._session.status, "playing")

    def test_refresh_playback_session_preserves_current_frame_when_possible(self):
        controller._session = PlaybackSession(
            workspace_id="workspace",
            clip_id="clip",
            frame_numbers=[3, 10],
            preview_paths=["/tmp/3.png", "/tmp/10.png"],
            fps=12,
            loop=True,
            current_index=0,
            status="paused",
        )

        refresh_playback_session(
            workspace_id="workspace",
            clip_id="clip",
            frame_numbers=[2, 3, 4],
            preview_paths=["/tmp/2.png", "/tmp/3.png", "/tmp/4.png"],
            fps=12,
        )

        self.assertEqual(controller._session.current_index, 1)
        self.assertEqual(controller._session.status, "paused")

    def test_refresh_playback_session_stops_when_selection_has_no_ready_frames(self):
        controller._session = PlaybackSession(
            workspace_id="workspace",
            clip_id="clip",
            frame_numbers=[3, 10],
            preview_paths=["/tmp/3.png", "/tmp/10.png"],
            fps=12,
            loop=True,
            current_index=0,
            status="playing",
        )

        self.assertTrue(
            refresh_playback_session(
                workspace_id="workspace",
                clip_id="clip",
                frame_numbers=[],
                preview_paths=[],
                fps=12,
            )
        )
        self.assertIsNone(controller._session)

    def test_refresh_playback_session_ignores_other_clip(self):
        controller._session = PlaybackSession(
            workspace_id="workspace",
            clip_id="clip",
            frame_numbers=[3, 10],
            preview_paths=["/tmp/3.png", "/tmp/10.png"],
            fps=12,
            loop=True,
            current_index=0,
            status="playing",
        )

        self.assertFalse(
            refresh_playback_session(
                workspace_id="workspace",
                clip_id="other",
                frame_numbers=[12],
                preview_paths=["/tmp/12.png"],
                fps=12,
            )
        )
        self.assertEqual(controller._session.frame_numbers, [3, 10])


if __name__ == "__main__":
    unittest.main()
