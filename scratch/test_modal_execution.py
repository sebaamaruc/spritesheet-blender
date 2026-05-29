import bpy
import sys
import os

# Add spritesheet_frame_selector to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spritesheet_frame_selector.visual_selector import SPRITESHEET_OT_visual_selector

# Create a mock region
class MockRegion:
    def __init__(self):
        self.width = 1024
        self.height = 768
        self.x = 0
        self.y = 0
        self.type = 'WINDOW'

class MockArea:
    def __init__(self):
        self.type = 'VIEW_3D'
        self.regions = [MockRegion()]
    def tag_redraw(self):
        pass

class MockWindowManager:
    def modal_handler_add(self, op):
        pass

class MockContext:
    def __init__(self):
        self.scene = bpy.context.scene
        self.area = MockArea()
        self.region = self.area.regions[0]
        self.window_manager = MockWindowManager()
        self.view_layer = bpy.context.view_layer

class MockEvent:
    def __init__(self):
        self.type = 'MOUSEMOVE'
        self.value = 'NOTHING'
        self.mouse_region_x = 100
        self.mouse_region_y = 100
        self.shift = False
        self.ctrl = False
        self.mouse_y = 100
        self.mouse_prev_y = 100

class DummySelf:
    def __init__(self):
        self._handle = None
        self.mouse_x = 0
        self.mouse_y = 0
        self.cell_w = 80
        self.cell_h = 100
        self.padding = 12
        self.margin_top = 60
        self.margin_bottom = 60
        self.viewer_height = 0
        self.x_start = 0
        self.avail_width = 100
        self.y_start = 0
        self.avail_height = 100
        self.scroll_y = 0
        self.max_scroll_y = 0
        self.is_dragging_scrollbar = False
        self.scrollbar_drag_start_y = 0
        self.scrollbar_drag_start_scroll_y = 0
        self.is_panning = False
        self.pan_start_y = 0
        self.pan_start_scroll_y = 0
        self.is_dragging = False
        self.drag_action = None
        self.last_hovered_idx = -1
        self.preview_images = {}
        self.playback_timer = None
        self.playback_index = 0
        self.is_playing = False
        
    def load_previews(self, clip):
        pass
        
    def unload_previews(self):
        pass
        
    def close_modal(self, context):
        pass
        
    def get_visible_frames_layout(self, width, height, clip, context):
        return SPRITESHEET_OT_visual_selector.get_visible_frames_layout(self, width, height, clip, context)
        
    def hit_test(self, x, y, layout_items):
        return -1
        
    def draw_callback(self, context):
        pass

def test():
    # Setup test clip
    scene = bpy.context.scene
    scene.spritesheet_clips.clear()
    clip = scene.spritesheet_clips.add()
    clip.name = "TestClip"
    clip.frame_start = 1
    clip.frame_end = 5
    clip.preview_size = '64'
    for i in range(1, 6):
        f = clip.frames.add()
        f.frame_number = i
        f.selected = False
        
    scene.active_clip_index = 0
    
    # Create operator instance
    dummy_self = DummySelf()
    
    # Mock draw handler registration
    import unittest.mock as mock
    with mock.patch('bpy.types.SpaceView3D.draw_handler_add', return_value="fake_handle") as mock_add, \
         mock.patch('bpy.types.SpaceView3D.draw_handler_remove', return_value=None):
         
        # Invoke
        ctx = MockContext()
        event = MockEvent()
        res = SPRITESHEET_OT_visual_selector.invoke(dummy_self, ctx, event)
        print("Invoke result:", res)
        
        # Call modal
        res_modal = SPRITESHEET_OT_visual_selector.modal(dummy_self, ctx, event)
        print("Modal result:", res_modal)

if __name__ == '__main__':
    test()
