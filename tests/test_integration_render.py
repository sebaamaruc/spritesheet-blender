import unittest
import bpy
import os
import sys
import tempfile
import numpy as np

# Add spritesheet_frame_selector to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spritesheet_frame_selector.utils import (
    save_collection_visibility,
    restore_collection_visibility,
    apply_clip_visibility
)
from spritesheet_frame_selector.render_queue import render_multi_clip_frames
from spritesheet_frame_selector.composer_numpy import NumpyComposer

class TestIntegrationRender(unittest.TestCase):
    def setUp(self):
        # 1. Clean existing data to avoid conflicts
        bpy.ops.wm.read_homefile(use_empty=True)
        
        self.scene = bpy.context.scene
        self.master_collection = self.scene.collection
        
        # 2. Create collections
        self.coll_char = bpy.data.collections.new("Character_Main")
        self.master_collection.children.link(self.coll_char)
        
        self.coll_lights = bpy.data.collections.new("Shared_Lights")
        self.master_collection.children.link(self.coll_lights)
        
        self.coll_cameras = bpy.data.collections.new("Shared_Cameras")
        self.master_collection.children.link(self.coll_cameras)
        
        # 3. Create a Cube in Character_Main
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        self.cube_obj = bpy.context.active_object
        # Relink to Character_Main and unlink from master
        self.coll_char.objects.link(self.cube_obj)
        self.master_collection.objects.unlink(self.cube_obj)
        
        # 4. Create a Light in Shared_Lights
        light_data = bpy.data.lights.new(name="SunLight", type="SUN")
        self.light_obj = bpy.data.objects.new(name="SunLight", object_data=light_data)
        self.coll_lights.objects.link(self.light_obj)
        
        # 5. Create a Camera in Shared_Cameras
        self.camera_data = bpy.data.cameras.new("TestCamera")
        self.camera_obj = bpy.data.objects.new("TestCamera", self.camera_data)
        self.camera_obj.location = (0, -10, 0)
        self.camera_obj.rotation_euler = (np.pi/2, 0, 0) # point at cube
        self.coll_cameras.objects.link(self.camera_obj)
        self.scene.camera = self.camera_obj
        
        # 6. Initialize addon properties
        # Register if not registered, but we run in background with registered addon
        import spritesheet_frame_selector
        try:
            spritesheet_frame_selector.register()
        except Exception as e:
            # might already be registered in this Blender process
            pass
            
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()
        import spritesheet_frame_selector
        try:
            spritesheet_frame_selector.unregister()
        except:
            pass

    def test_rendering_and_composition_transparency(self):
        # Create clip Idle
        clip = self.scene.spritesheet_clips.add()
        clip.name = "Idle"
        clip.frame_start = 1
        clip.frame_end = 2
        clip.frame_step = 1
        clip.camera = self.camera_obj
        clip.include_in_export = True
        
        # Add Character_Main and Shared_Lights to included_collections whitelist
        item_char = clip.included_collections.add()
        item_char.collection = self.coll_char
        item_char.collection_name = self.coll_char.name
        
        item_lights = clip.included_collections.add()
        item_lights.collection = self.coll_lights
        item_lights.collection_name = self.coll_lights.name
        
        # Setup selection state
        frame_1 = clip.frames.add()
        frame_1.frame_number = 1
        frame_1.selected = True
        
        frame_2 = clip.frames.add()
        frame_2.frame_number = 2
        frame_2.selected = True
        
        # Export Settings
        export_settings = self.scene.spritesheet_export
        export_settings.frame_width = 64
        export_settings.frame_height = 64
        export_settings.columns = 2
        export_settings.padding = 0
        export_settings.margin = 0
        export_settings.transparent = True
        export_settings.output_folder = self.temp_dir.name
        export_settings.sheet_name = "integration_sheet"
        
        # 1. Execute rendering
        clips_to_export = [clip]
        frame_paths, clips_data = render_multi_clip_frames(clips_to_export, export_settings, bpy.context)
        
        # 2. Check output paths exist
        self.assertEqual(len(frame_paths), 2)
        for path in frame_paths:
            self.assertTrue(os.path.exists(path))
            
            # Load and verify dimensions and transparency
            img = bpy.data.images.load(path, check_existing=False)
            self.assertEqual(img.size[0], 64)
            self.assertEqual(img.size[1], 64)
            
            # Read pixels (64 * 64 * 4 float values)
            pixels = np.empty(64 * 64 * 4, dtype=np.float32)
            img.pixels.foreach_get(pixels)
            pixels = pixels.reshape((64, 64, 4))
            
            # Check transparency (alpha channel is index 3)
            alpha_channel = pixels[:, :, 3]
            
            # Background should be transparent (alpha = 0.0)
            # The cube in the center should be non-transparent (alpha > 0.0)
            has_transparent_pixels = np.any(alpha_channel < 0.1)
            has_solid_pixels = np.any(alpha_channel > 0.9)
            
            self.assertTrue(has_transparent_pixels, f"Rendered frame {path} lacks transparency in background.")
            self.assertTrue(has_solid_pixels, f"Rendered frame {path} lacks solid pixels (cube/mesh might be hidden or missing).")
            
            # Clean up image from Blender DB
            bpy.data.images.remove(img)
            
        # 3. Perform Composition
        output_png = os.path.join(self.temp_dir.name, "integration_sheet.png")
        composer = NumpyComposer()
        success = composer.compose(
            frame_paths=frame_paths,
            frame_width=64,
            frame_height=64,
            columns=2,
            padding=0,
            margin=0,
            output_path=output_png,
            transparent=True
        )
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_png))
        
        # Verify composed sheet pixels
        sheet_img = bpy.data.images.load(output_png, check_existing=False)
        self.assertEqual(sheet_img.size[0], 128) # 2 columns of 64
        self.assertEqual(sheet_img.size[1], 64)  # 1 row of 64
        
        sheet_pixels = np.empty(128 * 64 * 4, dtype=np.float32)
        sheet_img.pixels.foreach_get(sheet_pixels)
        sheet_pixels = sheet_pixels.reshape((64, 128, 4))
        
        # Verify composed transparency and solid pixels
        sheet_alpha = sheet_pixels[:, :, 3]
        self.assertTrue(np.any(sheet_alpha < 0.1), "Composed spritesheet lacks transparency.")
        self.assertTrue(np.any(sheet_alpha > 0.9), "Composed spritesheet lacks solid pixels (cube missing).")
        
        bpy.data.images.remove(sheet_img)

    def test_preview_generation_all_shading_modes(self):
        from spritesheet_frame_selector.preview_generator import generate_clip_previews
        
        # Create clip for preview testing
        clip = self.scene.spritesheet_clips.add()
        clip.name = "PreviewClip"
        clip.frame_start = 5
        clip.frame_end = 6
        clip.frame_step = 1
        clip.camera = self.camera_obj
        clip.preview_size = '64'
        
        # Add Character_Main and Shared_Lights to included_collections whitelist
        item_char = clip.included_collections.add()
        item_char.collection = self.coll_char
        item_char.collection_name = self.coll_char.name
        
        item_lights = clip.included_collections.add()
        item_lights.collection = self.coll_lights
        item_lights.collection_name = self.coll_lights.name
        
        # Define a mock context helper to simulate different viewport shading modes
        class MockContext:
            def __init__(self, scene, shading_type='SOLID'):
                self.scene = scene
                self.window_manager = scene.connection if hasattr(scene, "connection") else bpy.context.window_manager
                self.view_layer = bpy.context.view_layer
                self.area = None
                self.screen = bpy.context.screen
                
                # Mock space_data
                class MockShading:
                    def __init__(self):
                        self.type = shading_type
                        self.studio_light = 'studio.exr'
                        self.studiolight_rotate_z = 0.785
                        self.studiolight_intensity = 1.0
                        self.use_scene_lights = False
                        
                class MockSpaceData:
                    def __init__(self):
                        self.type = 'VIEW_3D'
                        self.shading = MockShading()
                        
                self.space_data = MockSpaceData()

        # Save initial scene states to verify absolute restoration later
        initial_world = self.scene.world
        initial_engine = self.scene.render.engine
        initial_samples = self.scene.eevee.taa_render_samples
        initial_light_hide = self.light_obj.hide_render

        # --- 1. Test SOLID (Workbench) shading mode ---
        mock_ctx_solid = MockContext(self.scene, 'SOLID')
        success_solid = generate_clip_previews(clip, mock_ctx_solid)
        self.assertTrue(success_solid)
        
        # Verify states restored
        self.assertEqual(self.scene.world, initial_world)
        self.assertEqual(self.scene.render.engine, initial_engine)
        self.assertEqual(self.light_obj.hide_render, initial_light_hide)
        
        # --- 2. Test MATERIAL (LookDev World Swap) shading mode ---
        mock_ctx_material = MockContext(self.scene, 'MATERIAL')
        success_material = generate_clip_previews(clip, mock_ctx_material)
        self.assertTrue(success_material)
        
        # Verify states restored
        self.assertEqual(self.scene.world, initial_world)
        self.assertEqual(self.scene.render.engine, initial_engine)
        self.assertEqual(self.scene.eevee.taa_render_samples, initial_samples)
        self.assertEqual(self.light_obj.hide_render, initial_light_hide)
        
        # Verify previews generated in cache directory are valid transparent PNGs
        self.assertEqual(len(clip.frames), 2)
        for frame in clip.frames:
            self.assertTrue(os.path.exists(frame.preview_path))
            img = bpy.data.images.load(frame.preview_path, check_existing=False)
            self.assertEqual(img.size[0], 64)
            self.assertEqual(img.size[1], 64)
            
            pixels = np.empty(64 * 64 * 4, dtype=np.float32)
            img.pixels.foreach_get(pixels)
            pixels = pixels.reshape((64, 64, 4))
            
            alpha = pixels[:, :, 3]
            self.assertTrue(np.any(alpha < 0.1), "Preview lacks transparent background.")
            self.assertTrue(np.any(alpha > 0.9), "Preview lacks solid object pixels.")
            bpy.data.images.remove(img)

        # --- 3. Test RENDERED shading mode ---
        mock_ctx_rendered = MockContext(self.scene, 'RENDERED')
        success_rendered = generate_clip_previews(clip, mock_ctx_rendered)
        self.assertTrue(success_rendered)
        
        # Verify states restored
        self.assertEqual(self.scene.world, initial_world)
        self.assertEqual(self.scene.render.engine, initial_engine)
        self.assertEqual(self.light_obj.hide_render, initial_light_hide)

if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])

