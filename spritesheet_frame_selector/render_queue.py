import bpy
import os
import tempfile
from .utils import save_render_settings, restore_render_settings, resolve_blend_path

def get_temp_export_dir(clip):
    """Returns a temporary directory path for exporting frames of a clip.
    Located in the blend file directory if saved, or system temp if not.
    """
    blend_file = bpy.data.filepath
    clip_safe_name = "".join([c if c.isalnum() or c in ('-', '_') else '_' for c in clip.name])
    
    if blend_file:
        cache_root = resolve_blend_path("//spritesheet_cache/export_temp")
        return os.path.join(cache_root, clip_safe_name)
    else:
        temp_dir = os.path.join(tempfile.gettempdir(), "spritesheet_export_temp")
        return os.path.join(temp_dir, clip_safe_name)


def render_selected_frames(clip, export_settings, context):
    """Renders all selected frames in the clip using the active scene renderer.
    Returns a list of file paths to the rendered frames.
    """
    scene = context.scene
    render = scene.render
    
    selected_frames = [f for f in clip.frames if f.selected]
    if not selected_frames:
        return []
        
    # Create temporary directory for render output
    render_dir = get_temp_export_dir(clip)
    os.makedirs(render_dir, exist_ok=True)
    
    # 1. Save settings
    orig_settings = save_render_settings(scene)
    
    # 2. Configure for final render resolution
    render.resolution_x = export_settings.frame_width
    render.resolution_y = export_settings.frame_height
    render.resolution_percentage = 100
    render.image_settings.file_format = 'PNG'
    render.image_settings.color_mode = 'RGBA'
    render.image_settings.color_depth = '8'
    scene.render.film_transparent = export_settings.transparent
    
    # Active camera override if specified
    if clip.camera:
        scene.camera = clip.camera
        
    rendered_paths = []
    total = len(selected_frames)
    
    # Start progress
    context.window_manager.progress_begin(0, total)
    
    try:
        for idx, frame_item in enumerate(selected_frames):
            frame_num = frame_item.frame_number
            scene.frame_set(frame_num)
            
            # Setup output file path
            filepath = os.path.join(render_dir, f"export_frame_{frame_num:05d}.png")
            render.filepath = filepath
            
            # Perform standard render (Cycles / EEVEE / Workbench)
            # write_still=True writes the output directly to disk
            bpy.ops.render.render(write_still=True)
            
            rendered_paths.append(filepath)
            
            # Update progress
            context.window_manager.progress_update(idx + 1)
            
    except Exception as e:
        print(f"render_queue: Error during frame rendering: {e}")
        raise e
    finally:
        # Stop progress and restore settings
        context.window_manager.progress_end()
        restore_render_settings(scene, orig_settings)
        
    return rendered_paths
