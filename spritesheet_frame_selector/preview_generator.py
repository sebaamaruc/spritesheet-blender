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
    
    # 3. Save render settings
    orig_settings = save_render_settings(scene)
    
    # 4. Configure render settings for preview
    size = int(clip.preview_size)
    render.resolution_x = size
    render.resolution_y = size
    render.resolution_percentage = 100
    render.image_settings.file_format = 'PNG'
    render.image_settings.color_mode = 'RGBA'
    render.image_settings.color_depth = '8'
    scene.render.film_transparent = True  # Ensure transparent background for previews
    
    # Set camera override if specified
    if clip.camera:
        scene.camera = clip.camera
        
    # 5. Save and disable viewport overlays & gizmos to get clean previews
    orig_view_settings = []
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    orig_view_settings.append({
                        'space': space,
                        'show_overlays': space.overlay.show_overlays,
                        'show_gizmo': space.show_gizmo
                    })
                    try:
                        space.overlay.show_overlays = False
                        space.show_gizmo = False
                    except Exception as e:
                        print(f"Error disabling viewport overlays: {e}")
                        
    frames_to_render = list(range(clip.frame_start, clip.frame_end + 1, clip.frame_step))
    total_frames = len(frames_to_render)
    
    if total_frames == 0:
        # Restore viewport settings
        for s in orig_view_settings:
            try:
                s['space'].overlay.show_overlays = s['show_overlays']
                s['space'].show_gizmo = s['show_gizmo']
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
            
            # Render OpenGL preview (viewport render)
            # write_still=True writes the output to render.filepath
            bpy.ops.render.opengl(write_still=True)
            
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
        # Restore viewport settings
        for s in orig_view_settings:
            try:
                s['space'].overlay.show_overlays = s['show_overlays']
                s['space'].show_gizmo = s['show_gizmo']
            except:
                pass
        # ALWAYS restore settings
        restore_render_settings(scene, orig_settings)
        
    return True
