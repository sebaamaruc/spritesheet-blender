import bpy
import os

def resolve_blend_path(path):
    """Resolves a Blender relative path (starting with '//') to absolute path.
    If the file is not saved, it returns the path as is or resolves relative to standard temp dir.
    """
    if not path:
        return ""
    if path.startswith("//"):
        blend_file_path = bpy.data.filepath
        if blend_file_path:
            base_dir = os.path.dirname(blend_file_path)
            return os.path.abspath(os.path.join(base_dir, path[2:]))
        else:
            # File not saved, resolve relative to system temp
            import tempfile
            return os.path.abspath(os.path.join(tempfile.gettempdir(), path[2:]))
    return os.path.abspath(path)


def save_render_settings(scene):
    """Saves the current render settings and scene states to a dictionary so they can be restored later."""
    render = scene.render
    settings = {
        'resolution_x': render.resolution_x,
        'resolution_y': render.resolution_y,
        'resolution_percentage': render.resolution_percentage,
        'filepath': render.filepath,
        'file_format': render.image_settings.file_format,
        'color_mode': render.image_settings.color_mode,
        'color_depth': render.image_settings.color_depth,
        'film_transparent': scene.render.film_transparent,
        'camera': scene.camera,
        'frame_current': scene.frame_current,
    }
    return settings


def restore_render_settings(scene, settings):
    """Restores render settings and scene states from a dictionary."""
    render = scene.render
    render.resolution_x = settings['resolution_x']
    render.resolution_y = settings['resolution_y']
    render.resolution_percentage = settings['resolution_percentage']
    render.filepath = settings['filepath']
    render.image_settings.file_format = settings['file_format']
    render.image_settings.color_mode = settings['color_mode']
    render.image_settings.color_depth = settings['color_depth']
    scene.render.film_transparent = settings['film_transparent']
    scene.camera = settings['camera']
    scene.frame_set(settings['frame_current'])


def calculate_sheet_dimensions(n_frames, frame_w, frame_h, columns, padding=0, margin=0):
    """Calculates rows, sheet width, and sheet height for a spritesheet."""
    if n_frames <= 0 or columns <= 0:
        return 0, 0, 0
    
    rows = (n_frames + columns - 1) // columns
    
    sheet_w = margin * 2 + columns * frame_w + max(0, columns - 1) * padding
    sheet_h = margin * 2 + rows * frame_h + max(0, rows - 1) * padding
    
    return rows, sheet_w, sheet_h


def validate_export_settings(scene):
    """Validates the scene export configuration.
    Returns (is_valid, error_message).
    """
    if len(scene.spritesheet_clips) == 0:
        return False, "No animation clips defined. Add a clip first."
    
    clip_idx = scene.active_clip_index
    if clip_idx < 0 or clip_idx >= len(scene.spritesheet_clips):
        return False, "No active clip selected."
        
    clip = scene.spritesheet_clips[clip_idx]
    
    # Check if there are frames
    selected_frames = [f for f in clip.frames if f.selected]
    if not selected_frames:
        return False, "No frames selected for export. Open the Visual Selector and select frames."
        
    # Check export settings pointer
    export_settings = scene.spritesheet_export
    if not export_settings:
        return False, "Export settings are missing."
        
    if export_settings.frame_width <= 0 or export_settings.frame_height <= 0:
        return False, "Frame dimensions must be greater than 0."
        
    if export_settings.columns <= 0:
        return False, "Columns count must be greater than 0."
        
    if not export_settings.output_folder:
        return False, "Output folder is not set."
        
    # Check output directory
    out_dir = resolve_blend_path(export_settings.output_folder)
    if not os.path.exists(out_dir):
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception as e:
            return False, f"Could not create output directory: {str(e)}"
            
    # Check camera override or active camera
    cam = clip.camera if clip.camera else scene.camera
    if not cam:
        return False, "No active camera or camera override. Please select a camera in the viewport or clip settings."
        
    if cam.type != 'CAMERA':
        return False, f"Selected object '{cam.name}' is not a camera."
        
    return True, ""
