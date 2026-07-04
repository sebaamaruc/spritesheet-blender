import unittest

from spritesheet_frame_selector.core.frame_math import frame_count, frame_numbers


class FrameMathTests(unittest.TestCase):
    def test_normal_range(self):
        self.assertEqual(frame_numbers(1, 5, 1), [1, 2, 3, 4, 5])
        self.assertEqual(frame_count(1, 5, 1), 5)

    def test_frame_step(self):
        self.assertEqual(frame_numbers(1, 6, 2), [1, 3, 5])
        self.assertEqual(frame_count(1, 6, 2), 3)

    def test_inverted_range_is_empty(self):
        self.assertEqual(frame_numbers(10, 1, 1), [])
        self.assertEqual(frame_count(10, 1, 1), 0)

    def test_invalid_step_raises(self):
        with self.assertRaises(ValueError):
            frame_numbers(1, 5, 0)


if __name__ == "__main__":
    unittest.main()
