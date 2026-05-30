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
    
    # 1. Save settings and collection visibility
    orig_settings = save_render_settings(scene)
    from .utils import save_collection_visibility, restore_collection_visibility, apply_clip_visibility
    orig_visibility = save_collection_visibility(context)
    
    # 2. Configure for final render resolution
    render.resolution_x = export_settings.frame_width
    render.resolution_y = export_settings.frame_height
    render.resolution_percentage = 100
    render.image_settings.file_format = 'PNG'
    render.image_settings.color_mode = 'RGBA'
    render.image_settings.color_depth = '8'
    scene.render.film_transparent = export_settings.transparent
    
    rendered_paths = []
    total = len(selected_frames)
    
    # Start progress
    context.window_manager.progress_begin(0, total)
    
    try:
        # Apply visibility
        apply_clip_visibility(context, clip)
        
        # Active camera override if specified
        from .utils import resolve_clip_camera, get_active_workspace
        ws = get_active_workspace(context)
        resolved_cam = resolve_clip_camera(ws, clip, scene)
        if resolved_cam:
            scene.camera = resolved_cam
            
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
        restore_collection_visibility(context, orig_visibility)
        
    return rendered_paths


def get_global_temp_export_dir():
    """Returns a temporary directory path for global multi-clip export.
    Located in the blend file directory if saved, or system temp if not.
    """
    blend_file = bpy.data.filepath
    if blend_file:
        cache_root = resolve_blend_path("//spritesheet_cache/export_temp")
        return os.path.join(cache_root, "global_export")
    else:
        temp_dir = os.path.join(tempfile.gettempdir(), "spritesheet_export_temp")
        return os.path.join(temp_dir, "global_export")


def render_multi_clip_frames(clips_to_export, export_settings, context):
    """Renders all selected frames for multiple clips sequentially using unique global paths.
    Returns (all_frame_paths, clips_data).
    """
    scene = context.scene
    render = scene.render
    
    # 1. Save settings and collection visibility
    orig_settings = save_render_settings(scene)
    from .utils import save_collection_visibility, restore_collection_visibility, apply_clip_visibility
    orig_visibility = save_collection_visibility(context)
    
    # 2. Configure for final render resolution
    render.resolution_x = export_settings.frame_width
    render.resolution_y = export_settings.frame_height
    render.resolution_percentage = 100
    render.image_settings.file_format = 'PNG'
    render.image_settings.color_mode = 'RGBA'
    render.image_settings.color_depth = '8'
    scene.render.film_transparent = export_settings.transparent
    
    # Create temporary directory for render output
    render_dir = get_global_temp_export_dir()
    if os.path.exists(render_dir):
        import shutil
        try:
            shutil.rmtree(render_dir)
        except Exception as e:
            print(f"render_queue: Warning clearing old temp dir: {e}")
    os.makedirs(render_dir, exist_ok=True)
    
    all_frame_paths = []
    clips_data = {}
    global_idx = 0
    
    # Calculate total frames to render for progress bar
    total_frames = sum(sum(1 for f in c.frames if f.selected) for c in clips_to_export)
    context.window_manager.progress_begin(0, total_frames)
    
    current_progress = 0
    try:
        for clip in clips_to_export:
            selected_frames = [f for f in clip.frames if f.selected]
            if not selected_frames:
                continue
                
            # Apply collection visibility whitelist for this clip
            try:
                apply_clip_visibility(context, clip)
            except Exception as e:
                print(f"render_queue: Error applying visibility for '{clip.name}': {e}")
                raise e
                
            # Configure camera override for this clip if specified
            from .utils import resolve_clip_camera, get_active_workspace
            ws = get_active_workspace(context)
            resolved_cam = resolve_clip_camera(ws, clip, scene)
            if resolved_cam:
                scene.camera = resolved_cam
            else:
                scene.camera = orig_settings['camera']
                
            clip_frame_count = 0
            for frame_item in selected_frames:
                frame_num = frame_item.frame_number
                scene.frame_set(frame_num)
                
                # Setup unique global output file path
                filepath = os.path.join(render_dir, f"global_{global_idx:05d}.png")
                render.filepath = filepath
                
                # Perform standard render (Cycles / EEVEE / Workbench)
                bpy.ops.render.render(write_still=True)
                
                all_frame_paths.append(filepath)
                global_idx += 1
                clip_frame_count += 1
                current_progress += 1
                
                # Update progress
                context.window_manager.progress_update(current_progress)
                
            clips_data[clip.name] = {
                'count': clip_frame_count,
                'fps': clip.fps
            }
            
    except Exception as e:
        print(f"render_queue: Error during multi-clip frame rendering: {e}")
        raise e
    finally:
        # Stop progress and restore settings
        context.window_manager.progress_end()
        restore_render_settings(scene, orig_settings)
        # ALWAYS restore collection visibility at the end of the batch
        restore_collection_visibility(context, orig_visibility)
        
    return all_frame_paths, clips_data
