import bpy
import os
import shutil
import json
from .utils import resolve_blend_path
from .render_queue import render_selected_frames, get_temp_export_dir
from .composer_numpy import NumpyComposer

def write_metadata_json(output_dir, sheet_name, frame_width, frame_height, columns, clips_data):
    """Writes a JSON file containing metadata about the spritesheet and animation clips.
    
    clips_data should be a dict: { clip_name: { 'count': int, 'fps': int } }
    """
    metadata = {
        "sheet": sheet_name,
        "frameWidth": frame_width,
        "frameHeight": frame_height,
        "columns": columns,
        "clips": {}
    }
    
    current_start = 0
    for clip_name, clip_info in clips_data.items():
        count = clip_info['count']
        metadata["clips"][clip_name] = {
            "start": current_start,
            "end": max(0, current_start + count - 1),
            "count": count,
            "fps": clip_info.get('fps', 12)
        }
        current_start += count
        
    json_path = os.path.join(output_dir, f"{sheet_name}.json")
    try:
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        return True
    except Exception as e:
        print(f"exporter: Error writing metadata JSON: {e}")
        return False


def export_multiple_clips(clips, export_settings, context):
    """Handles the complete export pipeline for multiple animation clips:
    1. Renders selected frames for all selected clips at target dimensions.
    2. Concatenates the frame paths sequentially in a single global list.
    3. Composes final spritesheet PNG using NumpyComposer.
    4. Exports individual frame sequence if enabled.
    5. Writes JSON metadata.
    6. Cleans up temporary render directories.
    """
    output_dir = resolve_blend_path(export_settings.output_folder)
    os.makedirs(output_dir, exist_ok=True)
    
    sheet_name = export_settings.sheet_name
    output_png = os.path.join(output_dir, f"{sheet_name}.png")
    
    # Filter to only clips that are marked to be included and have selected frames
    clips_to_export = [c for c in clips if c.include_in_export and any(f.selected for f in c.frames)]
    
    if not clips_to_export:
        print("exporter: No clips included with selected frames to export.")
        return False
        
    print(f"exporter: Exporting {len(clips_to_export)} clips...")
    
    all_frame_paths = []
    clips_data = {}
    
    success = False
    try:
        # 1. Render selected frames for all clips in sequence using unique global paths
        from .render_queue import render_multi_clip_frames
        all_frame_paths, clips_data = render_multi_clip_frames(clips_to_export, export_settings, context)
                
        if not all_frame_paths:
            print("exporter: No frames were rendered.")
            return False
            
        # 2. Compose spritesheet using the global list
        print(f"exporter: Composing spritesheet with {len(all_frame_paths)} total frames...")
        composer = NumpyComposer()
        success = composer.compose(
            frame_paths=all_frame_paths,
            frame_width=export_settings.frame_width,
            frame_height=export_settings.frame_height,
            columns=export_settings.columns,
            padding=export_settings.padding,
            margin=export_settings.margin,
            output_path=output_png,
            transparent=export_settings.transparent
        )
        
        if success:
            print(f"exporter: Spritesheet composed successfully: {output_png}")
            
            # 3. Export PNG sequence if enabled
            if export_settings.export_png_sequence:
                seq_dir = os.path.join(output_dir, f"{sheet_name}_sequence")
                os.makedirs(seq_dir, exist_ok=True)
                print(f"exporter: Exporting PNG sequence to {seq_dir}...")
                
                for idx, path in enumerate(all_frame_paths):
                    filename = f"{sheet_name}_{idx:03d}.png"
                    dest_path = os.path.join(seq_dir, filename)
                    shutil.copy(path, dest_path)
            
            # 4. Write JSON metadata
            write_metadata_json(
                output_dir=output_dir,
                sheet_name=sheet_name,
                frame_width=export_settings.frame_width,
                frame_height=export_settings.frame_height,
                columns=export_settings.columns,
                clips_data=clips_data
            )
            
    except Exception as e:
        print(f"exporter: Exception during export pipeline: {e}")
        success = False
        
    finally:
        # 5. Clean up temporary render folder
        from .render_queue import get_global_temp_export_dir
        temp_dir = get_global_temp_export_dir()
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"exporter: Error cleaning up temporary folder {temp_dir}: {e}")
                    
    return success


def export_single_clip(clip, export_settings, context):
    """Legacy wrapper for exporting a single clip."""
    return export_multiple_clips([clip], export_settings, context)
