import unittest
import os
import sys
import tempfile
import json

# Add spritesheet_frame_selector to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock bpy/gpu modules before imports
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

from spritesheet_frame_selector.exporter import write_metadata_json

class TestMultiClipMetadata(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        self.test_dir.cleanup()
        
    def test_multi_clip_json_ranges(self):
        clips_data = {
            "idle": {
                "count": 10,
                "fps": 12
            },
            "walk": {
                "count": 12,
                "fps": 24
            },
            "jump": {
                "count": 5,
                "fps": 15
            }
        }
        
        sheet_name = "test_spritesheet"
        success = write_metadata_json(
            output_dir=self.test_dir.name,
            sheet_name=sheet_name,
            frame_width=64,
            frame_height=64,
            columns=8,
            clips_data=clips_data
        )
        
        self.assertTrue(success)
        
        # Verify JSON content
        json_path = os.path.join(self.test_dir.name, f"{sheet_name}.json")
        self.assertTrue(os.path.exists(json_path))
        
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        self.assertEqual(data["sheet"], sheet_name)
        self.assertEqual(data["frameWidth"], 64)
        self.assertEqual(data["frameHeight"], 64)
        self.assertEqual(data["columns"], 8)
        
        clips = data["clips"]
        self.assertIn("idle", clips)
        self.assertIn("walk", clips)
        self.assertIn("jump", clips)
        
        # Check idle (start = 0, count = 10 -> end = 9)
        self.assertEqual(clips["idle"]["start"], 0)
        self.assertEqual(clips["idle"]["end"], 9)
        self.assertEqual(clips["idle"]["count"], 10)
        self.assertEqual(clips["idle"]["fps"], 12)
        
        # Check walk (start = 10, count = 12 -> end = 21)
        self.assertEqual(clips["walk"]["start"], 10)
        self.assertEqual(clips["walk"]["end"], 21)
        self.assertEqual(clips["walk"]["count"], 12)
        self.assertEqual(clips["walk"]["fps"], 24)
        
        # Check jump (start = 22, count = 5 -> end = 26)
        self.assertEqual(clips["jump"]["start"], 22)
        self.assertEqual(clips["jump"]["end"], 26)
        self.assertEqual(clips["jump"]["count"], 5)
        self.assertEqual(clips["jump"]["fps"], 15)

if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])
