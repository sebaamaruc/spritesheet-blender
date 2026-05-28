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
    
    NOTE ON SHADING MODE LIMITATION:
    Currently, the OpenGL/viewport render used for previews inherits the shading mode
    (Solid, Material Preview, Rendered, etc.) of the active 3D viewport.
    This is a known limitation. In the future, this generator can be expanded to force 
    a specific shading mode by overriding the active space shading properties:
        active_space.shading.type = 'SOLID'  # e.g., to force solid view
    For now, it maintains the current shading mode of the active viewport.
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
    
    # 3. Save render settings and collection visibility
    orig_settings = save_render_settings(scene)
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
        
        # 5. Identify active SpaceView3D and temporarily disable overlays & gizmos locally
        # to get clean previews. We only modify the viewport initiating the context to minimize side effects.
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
                    
        orig_overlays = None
        orig_gizmos = None
        
        if active_space:
            orig_overlays = active_space.overlay.show_overlays
            orig_gizmos = active_space.show_gizmo
            try:
                active_space.overlay.show_overlays = False
                active_space.show_gizmo = False
            except Exception as e:
                print(f"preview_generator: Error disabling local viewport overlays: {e}")
                
        frames_to_render = list(range(clip.frame_start, clip.frame_end + 1, clip.frame_step))
        total_frames = len(frames_to_render)
        
        if total_frames == 0:
            # Restore viewport settings
            if active_space and orig_overlays is not None:
                try:
                    active_space.overlay.show_overlays = orig_overlays
                    active_space.show_gizmo = orig_gizmos
                except:
                    pass
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
                
                # Render OpenGL preview (viewport render using active camera but view_context=False
                # so that it does not visually snap the user's viewport perspective view)
                bpy.ops.render.opengl(write_still=True, view_context=False)
                
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
            # If something goes wrong, we mark cache dirty
            clip.cache_dirty = True
            raise e
            
        finally:
            # End progress
            context.window_manager.progress_end()
            # Restore viewport settings local to the active space
            if active_space and orig_overlays is not None:
                try:
                    active_space.overlay.show_overlays = orig_overlays
                    active_space.show_gizmo = orig_gizmos
                except:
                    pass
            # ALWAYS restore settings
            restore_render_settings(scene, orig_settings)
            
        return True
    finally:
        # ALWAYS restore collection visibility
        restore_collection_visibility(context, orig_visibility)
