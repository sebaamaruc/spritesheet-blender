import unittest
import bpy
import os
import sys

# Add spritesheet_frame_selector to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spritesheet_frame_selector.utils import (
    save_collection_visibility,
    restore_collection_visibility,
    apply_clip_visibility
)

class TestVisibilityHelpers(unittest.TestCase):
    def setUp(self):
        # Create some test collections in the scene
        self.scene = bpy.context.scene
        self.master_collection = self.scene.collection
        
        # Create root collection A
        self.coll_a = bpy.data.collections.new("Test_Coll_A")
        self.master_collection.children.link(self.coll_a)
        
        # Create nested collection B inside A
        self.coll_b = bpy.data.collections.new("Test_Coll_B")
        self.coll_a.children.link(self.coll_b)
        
        # Create root collection C
        self.coll_c = bpy.data.collections.new("Test_Coll_C")
        self.master_collection.children.link(self.coll_c)
        
        # Create a dummy camera inside a collection
        self.camera_data = bpy.data.cameras.new("Test_Camera")
        self.camera_obj = bpy.data.objects.new("Test_Camera", self.camera_data)
        self.coll_c.objects.link(self.camera_obj)
        
    def tearDown(self):
        # Unlink and delete collections
        for coll in [self.coll_b, self.coll_a, self.coll_c]:
            if coll.name in bpy.data.collections:
                # Unlink from all parents
                for parent in bpy.data.collections:
                    if coll.name in parent.children:
                        parent.children.unlink(coll)
                if coll.name in self.master_collection.children:
                    self.master_collection.children.unlink(coll)
                bpy.data.collections.remove(coll)
                
        if hasattr(self, 'camera_obj') and self.camera_obj.name in bpy.data.objects:
            bpy.data.objects.remove(self.camera_obj)
        if hasattr(self, 'camera_data') and self.camera_data.name in bpy.data.cameras:
            bpy.data.cameras.remove(self.camera_data)
            
    def test_save_and_restore(self):
        # Save visibility
        orig_state = save_collection_visibility(bpy.context)
        
        # Manually alter exclude states
        view_layer = bpy.context.view_layer
        # Find layer collection for A
        layer_coll_a = view_layer.layer_collection.children.get("Test_Coll_A")
        self.assertIsNotNone(layer_coll_a)
        
        orig_exclude = layer_coll_a.exclude
        layer_coll_a.exclude = not orig_exclude
        
        # Restore
        restore_collection_visibility(bpy.context, orig_state)
        
        # Check restored
        self.assertEqual(layer_coll_a.exclude, orig_exclude)
        
    def test_apply_visibility_whitelist(self):
        # Create a mock clip with included_collections
        class DummyIncludedItem:
            def __init__(self, collection):
                self.collection = collection
                self.collection_name = collection.name if collection else ""
                
        class DummyClip:
            def __init__(self, name, collections, camera=None):
                self.name = name
                self.included_collections = [DummyIncludedItem(c) for c in collections]
                self.camera = camera
                
        # Clip only includes Test_Coll_B (nested inside Test_Coll_A)
        # Should automatically include Test_Coll_A (parent) and Camera collection (Test_Coll_C)
        clip = DummyClip("TestClip", [self.coll_b], camera=self.camera_obj)
        
        orig_state = save_collection_visibility(bpy.context)
        try:
            apply_clip_visibility(bpy.context, clip)
            
            view_layer = bpy.context.view_layer
            layer_coll_a = view_layer.layer_collection.children.get("Test_Coll_A")
            layer_coll_b = layer_coll_a.children.get("Test_Coll_B")
            layer_coll_c = view_layer.layer_collection.children.get("Test_Coll_C")
            
            # Since Test_Coll_B is whitelisted:
            # - Test_Coll_B should not be excluded (exclude = False)
            # - Test_Coll_A (parent of B) should not be excluded (exclude = False)
            # - Test_Coll_C (contains the camera) should not be excluded (exclude = False)
            self.assertFalse(layer_coll_b.exclude)
            self.assertFalse(layer_coll_a.exclude)
            self.assertFalse(layer_coll_c.exclude)
            
        finally:
            restore_collection_visibility(bpy.context, orig_state)

if __name__ == '__main__':
    import sys
    unittest.main(argv=[sys.argv[0]])
