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
    
    # Get all clips marked for export
    clips_to_export = [c for c in scene.spritesheet_clips if c.include_in_export]
    if not clips_to_export:
        return False, "No clips marked for export. Check 'Include in Export' on at least one clip."
        
    # Check if there are any frames selected across the included clips
    has_selected_frames = False
    for clip in clips_to_export:
        if any(f.selected for f in clip.frames):
            has_selected_frames = True
            break
            
    if not has_selected_frames:
        return False, "No frames selected for export in any of the included clips. Open the Visual Selector and select frames."
        
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
            
    # Check camera override or active camera for each clip with selected frames,
    # and also validate included_collections.
    for clip in clips_to_export:
        if not any(f.selected for f in clip.frames):
            continue
            
        # 1. Camera validation
        cam = clip.camera if clip.camera else scene.camera
        if not cam:
            return False, f"No active camera or camera override for clip '{clip.name}'."
            
        if cam.type != 'CAMERA':
            return False, f"Selected object '{cam.name}' for clip '{clip.name}' is not a camera."
            
        # 2. Included Collections validation
        included_items = list(clip.included_collections)
        if not included_items:
            return False, f"Clip '{clip.name}' has no included collections. Add at least one collection."
            
        valid_collections = [item.collection for item in included_items if item.collection is not None]
        if not valid_collections:
            deleted_names = [item.collection_name for item in included_items if item.collection_name != ""]
            if deleted_names:
                return False, f"Clip '{clip.name}' collections {deleted_names} no longer exist in the scene."
            else:
                return False, f"Clip '{clip.name}' has empty included collection slots."
            
    return True, ""


def save_collection_visibility(context):
    """Saves the current exclude state of all layer collections in the active view layer.
    Returns a list of tuples: (layer_collection, exclude_value)
    """
    view_layer = context.view_layer
    state = []
    
    def traverse(layer_coll):
        state.append((layer_coll, layer_coll.exclude))
        for child in layer_coll.children:
            traverse(child)
            
    traverse(view_layer.layer_collection)
    return state


def restore_collection_visibility(context, state):
    """Restores the exclude state of layer collections from the saved state list of tuples."""
    for layer_coll, exclude_val in state:
        try:
            layer_coll.exclude = exclude_val
        except Exception as e:
            print(f"utils: Warning restoring visibility for '{layer_coll.name}': {e}")


def apply_clip_visibility(context, clip):
    """Applies the whitelist of included collections for the given clip.
    Also ensures that the camera override/scene camera is always visible.
    Automatically handles parent (ancestors) un-exclusion and children (descendants) un-exclusion.
    """
    view_layer = context.view_layer
    
    # 1. Filter out empty references and check if we have any collections
    included_items = list(clip.included_collections)
    valid_collections = [item.collection for item in included_items if item.collection is not None]
    
    # Show warnings for deleted collections (where pointer is None but collection_name is set)
    for item in included_items:
        if item.collection is None and item.collection_name != "":
            print(f"Warning: Collection '{item.collection_name}' in clip '{clip.name}' no longer exists in the blend file.")
            
    if not included_items:
        raise ValueError(f"Clip '{clip.name}' has no included collections configured.")
        
    if not valid_collections:
        # Check if they were all deleted
        deleted_names = [item.collection_name for item in included_items if item.collection_name != ""]
        if deleted_names:
            raise ValueError(f"Clip '{clip.name}' collections {deleted_names} no longer exist in the scene.")
        else:
            raise ValueError(f"Clip '{clip.name}' has empty included collection slots.")
            
    # 2. Build mapping and parents map
    # Since Blender LayerCollection doesn't have a .parent attribute, we traverse and build it.
    mapping = {}      # collection -> list of layer_collections (for multi-parent support)
    parent_map = {}   # layer_collection -> parent_layer_collection
    
    def traverse(layer_coll, parent=None):
        coll = layer_coll.collection
        if coll not in mapping:
            mapping[coll] = []
        mapping[coll].append(layer_coll)
        
        if parent is not None:
            parent_map[layer_coll] = parent
            
        for child in layer_coll.children:
            traverse(child, layer_coll)
            
    traverse(view_layer.layer_collection)
    
    # 3. Determine which layer collections should be visible (un-excluded)
    visible_layer_collections = set()
    visible_layer_collections.add(view_layer.layer_collection) # root is always visible
    
    # Helper to add a layer collection and all its descendants to the visible set
    def add_descendants(layer_coll):
        visible_layer_collections.add(layer_coll)
        for child in layer_coll.children:
            add_descendants(child)
            
    # Helper to add all ancestors of a layer collection to the visible set
    def add_ancestors(layer_coll):
        curr = layer_coll
        while curr is not None:
            visible_layer_collections.add(curr)
            curr = parent_map.get(curr)
            
    # Add whitelisted collections
    for coll in valid_collections:
        if coll not in mapping:
            print(f"utils: Warning - Collection '{coll.name}' is not in the active view layer '{view_layer.name}'.")
            continue
        for layer_coll in mapping[coll]:
            add_ancestors(layer_coll)
            add_descendants(layer_coll)
            
    # 4. Camera automatic visibility override:
    # Find active camera for the clip (hierarchical fallback matching preview_generator / render_queue)
    target_camera = None
    if clip.camera:
        target_camera = clip.camera
    elif context.scene.camera:
        target_camera = context.scene.camera
    else:
        cameras = [obj for obj in context.scene.objects if obj.type == 'CAMERA']
        if cameras:
            target_camera = cameras[0]
            
    if target_camera:
        # Find which collection(s) contain the camera
        for camera_coll in target_camera.users_collection:
            if camera_coll in mapping:
                for layer_coll in mapping[camera_coll]:
                    # Automatically un-exclude the camera collection and its ancestors
                    add_ancestors(layer_coll)
                    # Note: We do NOT need to add descendants of camera collection unless desired,
                    # but adding ancestors is essential so the camera itself isn't excluded.
                    visible_layer_collections.add(layer_coll)
                    
    # 5. Apply exclusion to all layer collections in the active view layer
    def apply_exclusion(layer_coll):
        if layer_coll != view_layer.layer_collection:
            should_be_visible = (layer_coll in visible_layer_collections)
            layer_coll.exclude = not should_be_visible
            
        for child in layer_coll.children:
            apply_exclusion(child)
            
    apply_exclusion(view_layer.layer_collection)

