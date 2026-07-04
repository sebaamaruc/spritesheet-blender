import unittest
from types import SimpleNamespace

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


if __name__ == "__main__":
    unittest.main()
