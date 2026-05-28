import bpy
import os
import shutil
import tempfile
from .utils import save_render_settings, restore_render_settings, resolve_blend_path

def get_cache_dir(clip):
    """Returns the absolute path to the preview cache directory for the given clip.
    If the .blend file is saved, it uses a folder relative to the .blend.
    If not, it uses a folder in the system temp directory.
    """
    blend_file = bpy.data.filepath
    clip_safe_name = "".join([c if c.isalnum() or c in ('-', '_') else '_' for c in clip.name])
    
    if blend_file:
        # Relative to .blend file
        cache_root = resolve_blend_path("//spritesheet_cache")
        return os.path.join(cache_root, clip_safe_name)
    else:
        # Temp dir
        temp_dir = os.path.join(tempfile.gettempdir(), "spritesheet_frame_selector_cache")
        return os.path.join(temp_dir, clip_safe_name)


def clear_clip_previews(clip):
    """Deletes all files in the cache directory for a clip and clears the frame list."""
    cache_dir = get_cache_dir(clip)
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
        except Exception as e:
            print(f"Error clearing cache directory {cache_dir}: {str(e)}")
            
    # Clear the collection data
    clip.frames.clear()
    clip.cache_dirty = True


def generate_clip_previews(clip, context):
    """Generates preview thumbnails for all frames in the clip's range.
    Preserves selection state of existing frames.
    
    This uses Blender's production render engine (Option B) to render EEVEE/Workbench 
    previews off-screen without viewport flickering. This may be slightly slower than 
    OpenGL rendering (especially for Cycles in Rendered mode), but is extremely stable, 
    clean, and respects the active viewport's shading mode.
    """
    scene = context.scene
    render = scene.render
    
    # 1. Save existing selection states to avoid losing them
    selection_states = {f.frame_number: f.selected for f in clip.frames}
    
    # Clear frames collection to rebuild
    clip.frames.clear()
    
    # 2. Get and create cache directory
    cache_dir = get_cache_dir(clip)
    os.makedirs(cache_dir, exist_ok=True)
    
    # 3. Save render settings, engine, and collection visibility
    orig_settings = save_render_settings(scene)
    orig_engine = scene.render.engine
    from .utils import save_collection_visibility, restore_collection_visibility, apply_clip_visibility
    orig_visibility = save_collection_visibility(context)
    
    try:
        # Apply visibility
        try:
            apply_clip_visibility(context, clip)
        except Exception as e:
            print(f"preview_generator: Visibility error: {e}")
            clip.cache_dirty = True
            return False
            
        # Determine target camera with fallbacks
        target_camera = None
        if clip.camera:
            target_camera = clip.camera
        elif scene.camera:
            target_camera = scene.camera
        else:
            # Fallback to first camera found in scene objects
            cameras = [obj for obj in scene.objects if obj.type == 'CAMERA']
            if cameras:
                target_camera = cameras[0]
                
        if not target_camera:
            print("preview_generator: Error - No camera found in the scene for previews.")
            restore_render_settings(scene, orig_settings)
            clip.cache_dirty = True
            return False
            
        # Set active camera override
        scene.camera = target_camera
        
        # 4. Configure render settings for preview
        size = int(clip.preview_size)
        render.resolution_x = size
        render.resolution_y = size
        render.resolution_percentage = 100
        render.image_settings.file_format = 'PNG'
        render.image_settings.color_mode = 'RGBA'
        render.image_settings.color_depth = '8'
        scene.render.film_transparent = True  # Ensure transparent background for previews
        
        # 5. Identify active SpaceView3D and inherit its shading mode
        active_space = None
        if context.space_data and context.space_data.type == 'VIEW_3D':
            active_space = context.space_data
        elif context.area and context.area.type == 'VIEW_3D':
            active_space = context.area.spaces.active
        else:
            # Fallback: search for first 3D View area in current screen
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    active_space = area.spaces.active
                    break
                    
        shading_type = 'SOLID'
        if active_space and hasattr(active_space, 'shading'):
            shading_type = active_space.shading.type
            
        # Temporarily change scene render engine based on viewport shading mode
        if shading_type in ('WIREFRAME', 'SOLID'):
            scene.render.engine = 'BLENDER_WORKBENCH'
        elif shading_type == 'MATERIAL':
            scene.render.engine = 'BLENDER_EEVEE'
        elif shading_type == 'RENDERED':
            # Keep scene's active render engine (EEVEE, Cycles, or Workbench)
            pass
            
        frames_to_render = list(range(clip.frame_start, clip.frame_end + 1, clip.frame_step))
        total_frames = len(frames_to_render)
        
        if total_frames == 0:
            restore_render_settings(scene, orig_settings)
            clip.cache_dirty = True
            return False
            
        # Start progress indicator
        context.window_manager.progress_begin(0, total_frames)
        
        try:
            for idx, frame_num in enumerate(frames_to_render):
                # Set frame
                scene.frame_set(frame_num)
                
                # Setup path
                filepath = os.path.join(cache_dir, f"frame_{frame_num:05d}.png")
                render.filepath = filepath
                
                # Perform standard render (EEVEE / Workbench / Cycles) off-screen
                # write_still=True writes the output directly to disk
                bpy.ops.render.render(write_still=True)
                
                # Add to frames collection
                item = clip.frames.add()
                item.frame_number = frame_num
                item.preview_path = filepath
                # Restore selection state if it existed before, otherwise default to True
                item.selected = selection_states.get(frame_num, True)
                
                # Update progress
                context.window_manager.progress_update(idx + 1)
                
            clip.cache_dirty = False
            
        except Exception as e:
            print(f"Error generating previews: {str(e)}")
            clip.cache_dirty = True
            raise e
            
        finally:
            # End progress
            context.window_manager.progress_end()
            # ALWAYS restore settings
            restore_render_settings(scene, orig_settings)
            
        return True
    finally:
        # ALWAYS restore original engine and collection visibility
        scene.render.engine = orig_engine
        restore_collection_visibility(context, orig_visibility)
