import unittest
import sys
import os

# Add spritesheet_frame_selector to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock bpy/gpu modules before imports if we are not running inside Blender
if 'bpy' not in sys.modules:
    from unittest.mock import MagicMock
    import types
    sys.modules['bpy'] = MagicMock()
    sys.modules['gpu'] = MagicMock()
    sys.modules['blf'] = MagicMock()

    # Create dummy modules for packages
    gpu_extras = types.ModuleType('gpu_extras')
    sys.modules['gpu_extras'] = gpu_extras

    gpu_extras_batch = types.ModuleType('gpu_extras.batch')
    sys.modules['gpu_extras.batch'] = gpu_extras_batch
    gpu_extras_batch.batch_for_shader = MagicMock()

    gpu_extras_presets = types.ModuleType('gpu_extras.presets')
    sys.modules['gpu_extras.presets'] = gpu_extras_presets
    gpu_extras_presets.draw_texture_2d = MagicMock()


from spritesheet_frame_selector.composer import ComposerBackend

class MockComposer(ComposerBackend):
    def compose(self, frame_paths, frame_width, frame_height, columns, padding=0, margin=0, output_path="", transparent=True):
        return True

class TestComposerMath(unittest.TestCase):
    def test_dimensions(self):
        composer = MockComposer()
        
        # Test basic cases
        rows, w, h = composer.calculate_dimensions(n_frames=6, frame_w=64, frame_h=64, columns=3, padding=0, margin=0)
        self.assertEqual(rows, 2)
        self.assertEqual(w, 64 * 3)
        self.assertEqual(h, 64 * 2)
        
        # Test padding
        rows, w, h = composer.calculate_dimensions(n_frames=6, frame_w=64, frame_h=64, columns=3, padding=10, margin=0)
        self.assertEqual(rows, 2)
        self.assertEqual(w, 64 * 3 + 10 * 2) # columns - 1 padding gaps
        self.assertEqual(h, 64 * 2 + 10 * 1) # rows - 1 padding gaps
        
        # Test margin
        rows, w, h = composer.calculate_dimensions(n_frames=6, frame_w=64, frame_h=64, columns=3, padding=10, margin=15)
        self.assertEqual(rows, 2)
        self.assertEqual(w, 64 * 3 + 10 * 2 + 15 * 2) # margin on both sides
        self.assertEqual(h, 64 * 2 + 10 * 1 + 15 * 2)
        
        # Test edge case: 1 frame
        rows, w, h = composer.calculate_dimensions(n_frames=1, frame_w=64, frame_h=64, columns=5, padding=10, margin=0)
        self.assertEqual(rows, 1)
        self.assertEqual(w, 64 * 5 + 10 * 4) # width is calculated for max columns layout
        self.assertEqual(h, 64 * 1)

if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])
