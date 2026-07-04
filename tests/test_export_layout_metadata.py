import unittest
import os
import tempfile

from spritesheet_frame_selector.export.layout import (
    ExportClip,
    clip_ranges,
    frame_rect,
    sheet_dimensions,
)
from spritesheet_frame_selector.export.metadata import build_spritesheet_metadata
from spritesheet_frame_selector.export.sequence import export_individual_frames


class ExportLayoutMetadataTests(unittest.TestCase):
    def test_sheet_dimensions_without_padding_or_margin(self):
        dimensions = sheet_dimensions(10, 64, 32, 4)

        self.assertEqual(dimensions.rows, 3)
        self.assertEqual(dimensions.width, 256)
        self.assertEqual(dimensions.height, 96)

    def test_sheet_dimensions_with_padding_and_margin(self):
        dimensions = sheet_dimensions(5, 10, 20, 4, padding=2, margin=3)

        self.assertEqual(dimensions.rows, 2)
        self.assertEqual(dimensions.width, 52)
        self.assertEqual(dimensions.height, 48)

    def test_frame_rect_uses_top_left_grid_coordinates(self):
        rect = frame_rect(5, 16, 8, 4, padding=2, margin=1)

        self.assertEqual(rect.x, 19)
        self.assertEqual(rect.y, 11)
        self.assertEqual(rect.width, 16)
        self.assertEqual(rect.height, 8)

    def test_clip_ranges_are_global_and_end_inclusive(self):
        ranges = clip_ranges(
            [
                ExportClip("shoot", 12, tuple(["a"] * 33)),
                ExportClip("run", 18, tuple(["b"] * 13)),
                ExportClip("idle", 12, tuple(["c"] * 89)),
            ]
        )

        self.assertEqual(ranges[0].start, 0)
        self.assertEqual(ranges[0].end, 32)
        self.assertEqual(ranges[1].start, 33)
        self.assertEqual(ranges[1].end, 45)
        self.assertEqual(ranges[2].start, 46)
        self.assertEqual(ranges[2].end, 134)

    def test_metadata_matches_approved_contract(self):
        ranges = clip_ranges(
            [
                ExportClip("shoot", 12, tuple(["a"] * 33)),
                ExportClip("run", 18, tuple(["b"] * 13)),
            ]
        )

        metadata = build_spritesheet_metadata(
            "shading_back_player_soccer",
            128,
            128,
            16,
            ranges,
        )

        self.assertEqual(
            metadata,
            {
                "sheet": "shading_back_player_soccer",
                "frameWidth": 128,
                "frameHeight": 128,
                "columns": 16,
                "clips": {
                    "shoot": {"start": 0, "end": 32, "count": 33, "fps": 12},
                    "run": {"start": 33, "end": 45, "count": 13, "fps": 18},
                },
            },
        )

    def test_individual_frames_use_three_digit_export_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_paths = []
            for index in range(2):
                source_path = os.path.join(temp_dir, f"source_{index}.png")
                with open(source_path, "wb") as handle:
                    handle.write(b"png")
                source_paths.append(source_path)

            sequence_folder = os.path.join(temp_dir, "spritesheet_frames")
            os.makedirs(sequence_folder)
            old_path = os.path.join(sequence_folder, "spritesheet_frame_000001.png")
            with open(old_path, "wb") as handle:
                handle.write(b"old")

            export_individual_frames(source_paths, sequence_folder, "spritesheet")

            self.assertFalse(os.path.exists(old_path))
            self.assertTrue(os.path.exists(os.path.join(sequence_folder, "spritesheet_frame_001.png")))
            self.assertTrue(os.path.exists(os.path.join(sequence_folder, "spritesheet_frame_002.png")))


if __name__ == "__main__":
    unittest.main()
