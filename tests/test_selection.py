import unittest
from types import SimpleNamespace

from spritesheet_frame_selector.core.selection import (
    frame_selection_summary,
    invert_frame_selection,
    select_every_n_frames,
    set_all_frames_selected,
)


class FakeCollection(list):
    def __init__(self, factory):
        super().__init__()
        self._factory = factory

    def add(self):
        item = self._factory()
        self.append(item)
        return item


def fake_frame():
    return SimpleNamespace(
        frame_number=0,
        selected=False,
        preview_path="",
    )


def fake_clip(count=4):
    clip = SimpleNamespace(
        frames=FakeCollection(fake_frame),
        cache_key="cache-key",
        cache_folder="/tmp/cache",
        cache_dirty=False,
        render_dirty=False,
    )
    for index in range(count):
        frame = clip.frames.add()
        frame.frame_number = index + 1
    return clip


class SelectionTests(unittest.TestCase):
    def test_select_all_and_deselect_all(self):
        clip = fake_clip()

        set_all_frames_selected(clip, True)
        self.assertTrue(all(frame.selected for frame in clip.frames))

        set_all_frames_selected(clip, False)
        self.assertFalse(any(frame.selected for frame in clip.frames))

    def test_invert_frame_selection(self):
        clip = fake_clip()
        clip.frames[0].selected = True
        clip.frames[2].selected = True

        invert_frame_selection(clip)

        self.assertEqual(
            [frame.selected for frame in clip.frames],
            [False, True, False, True],
        )

    def test_select_every_n_frames(self):
        clip = fake_clip(5)

        select_every_n_frames(clip, 2)

        self.assertEqual(
            [frame.selected for frame in clip.frames],
            [True, False, True, False, True],
        )

    def test_select_every_n_rejects_invalid_n(self):
        with self.assertRaises(ValueError):
            select_every_n_frames(fake_clip(), 0)

    def test_summary_counts_selection_and_preview_paths(self):
        clip = fake_clip(3)
        clip.frames[0].selected = True
        clip.frames[0].preview_path = "/tmp/a.png"
        clip.frames[2].preview_path = "/tmp/c.png"

        summary = frame_selection_summary(clip)

        self.assertEqual(summary.total, 3)
        self.assertEqual(summary.selected, 1)
        self.assertEqual(summary.previews, 2)

    def test_helpers_do_not_touch_cache_state(self):
        clip = fake_clip()
        select_every_n_frames(clip, 2)

        self.assertEqual(clip.cache_key, "cache-key")
        self.assertEqual(clip.cache_folder, "/tmp/cache")
        self.assertFalse(clip.cache_dirty)

    def test_selection_changes_mark_render_dirty(self):
        clip = fake_clip()

        set_all_frames_selected(clip, True)

        self.assertTrue(clip.render_dirty)


if __name__ == "__main__":
    unittest.main()
