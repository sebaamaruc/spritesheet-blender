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
    try:
        collection, _, _ = get_clip_context(bpy.context)
    except:
        collection = scene.spritesheet_clips

    if len(collection) == 0:
        return False, "No animation clips defined. Add a clip first."
    
    # Get all clips marked for export
    clips_to_export = [c for c in collection if c.include_in_export]
    if not clips_to_export:
        return False, "No clips marked for export. Check 'Include in Export' on at least one clip."
        
    # Check for duplicate clip names among clips included in export
    clip_names = [c.name for c in clips_to_export]
    duplicates = sorted(list(set([name for name in clip_names if clip_names.count(name) > 1])))
    if duplicates:
        dup_list_str = " - ".join(duplicates)
        return False, f"Duplicate clip names detected: - {dup_list_str}"
        
    # Check if there are any frames selected across the included clips
    has_selected_frames = False
    for clip in clips_to_export:
        if any(f.selected for f in clip.frames):
            has_selected_frames = True
            break
            
    if not has_selected_frames:
        return False, "No frames selected for export in any of the included clips. Open the Visual Selector and select frames."
        
    # Resolve Workspace
    try:
        ws = get_active_workspace(bpy.context)
    except:
        ws = None

    # Check export settings pointer
    if ws:
        export_settings = ws.export_settings
    else:
        export_settings = scene.spritesheet_export
        
    output_folder = export_settings.output_folder if export_settings else ""

    if not export_settings:
        return False, "Export settings are missing."
        
    if export_settings.frame_width <= 0 or export_settings.frame_height <= 0:
        return False, "Frame dimensions must be greater than 0."
        
    if export_settings.columns <= 0:
        return False, "Columns count must be greater than 0."
        
    if not output_folder:
        return False, "Output folder is not set."
        
    # Check output directory
    out_dir = resolve_blend_path(output_folder)
    if not os.path.exists(out_dir):
        curr = out_dir
        parent_found = False
        while curr:
            parent = os.path.dirname(curr)
            if not parent or parent == curr:
                break
            if os.path.exists(parent):
                if not os.access(parent, os.W_OK):
                    return False, f"Directory '{parent}' is not writable."
                parent_found = True
                break
            curr = parent
            
        if not parent_found:
            return False, "Output path is invalid or parent directory does not exist."
    else:
        if not os.path.isdir(out_dir):
            return False, f"Output path '{out_dir}' is a file, not a directory."
        if not os.access(out_dir, os.W_OK):
            return False, f"Output directory '{out_dir}' is not writable."
            
    # Check camera override/workspace camera or active camera,
    # and also validate included_collections.
    for clip in clips_to_export:
        if not any(f.selected for f in clip.frames):
            continue
            
        # 1. Camera validation
        cam = resolve_clip_camera(ws, clip, scene)
        if not cam:
            if ws:
                return False, f"Workspace '{ws.name}' has no default camera and clip '{clip.name}' has no camera override."
            else:
                return False, f"No active camera or camera override for clip '{clip.name}'."
            
        if cam.type != 'CAMERA':
            return False, f"Selected object '{cam.name}' for clip '{clip.name}' is not a camera."
            
        # 2. Included Collections validation
        resolved_colls = resolve_clip_collections(ws, clip)
        if not resolved_colls:
            if ws:
                return False, f"Workspace '{ws.name}' has no default collections and clip '{clip.name}' has no collection override."
            else:
                return False, f"Clip '{clip.name}' has no included collections. Add at least one collection."
            
        valid_collections = [item.collection for item in resolved_colls if item.collection is not None]
        if not valid_collections:
            deleted_names = [item.collection_name for item in resolved_colls if item.collection_name != ""]
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
    
    # Resolve workspace
    ws = get_active_workspace(context)
    resolved_collections = resolve_clip_collections(ws, clip)
    clip_camera = resolve_clip_camera(ws, clip, context.scene)
    
    # 1. Filter out empty references and check if we have any collections
    included_items = list(resolved_collections)
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
    target_camera = None
    if clip_camera:
        target_camera = clip_camera
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


class WorldSwapContext:
    """Context manager to simulate Blender's Material Preview (LookDev) shading mode off-screen.
    Swaps the scene's World with a temporary LookDev World using the specified HDRI,
    switches the engine to EEVEE with low samples (4), and hides physical scene lights if configured.
    All changes are fully restored in a robust try/finally block on exit.
    """
    def __init__(self, scene, studio_light='studio.exr', rotate_z=0.0, intensity=1.0, use_scene_lights=False):
        self.scene = scene
        self.studio_light = studio_light
        self.rotate_z = rotate_z
        self.intensity = intensity
        self.use_scene_lights = use_scene_lights
        
        self.orig_world = None
        self.orig_engine = None
        self.orig_samples = None
        self.temp_world = None
        self.temp_image = None
        self.hidden_lights = []

    def __enter__(self):
        # 1. Save original states
        self.orig_world = self.scene.world
        self.orig_engine = self.scene.render.engine
        
        # Save EEVEE samples if engine is EEVEE (or if properties exist)
        if hasattr(self.scene, "eevee") and hasattr(self.scene.eevee, "taa_render_samples"):
            self.orig_samples = self.scene.eevee.taa_render_samples
        else:
            self.orig_samples = 64 # Safe default if not available
            
        # Track whether changes were actually made to support robust rollback
        swapped_world = False
        swapped_engine = False
        swapped_samples = False
        
        try:
            # 2. Resolve HDRI path using Blender's studio lights preference API
            hdri_path = ""
            if hasattr(bpy.context, "preferences") and hasattr(bpy.context.preferences, "studio_lights"):
                for sl in bpy.context.preferences.studio_lights:
                    if sl.type == 'WORLD' and sl.name == self.studio_light:
                        hdri_path = sl.path
                        break
                        
            # Fallback to default Blender installation directories if not resolved via preferences
            if not hdri_path:
                version = f"{bpy.app.version[0]}.{bpy.app.version[1]}"
                binary_dir = os.path.dirname(bpy.app.binary_path)
                possible_dirs = [
                    os.path.normpath(os.path.join(binary_dir, '..', 'Resources', version, 'datafiles', 'studiolights', 'world')),
                    os.path.normpath(os.path.join(binary_dir, version, 'datafiles', 'studiolights', 'world')),
                ]
                for d in possible_dirs:
                    test_path = os.path.join(d, self.studio_light)
                    if os.path.exists(test_path):
                        hdri_path = test_path
                        break
                        
            # Fallback to any valid WORLD studio light if the requested one is missing
            if not hdri_path and hasattr(bpy.context, "preferences") and hasattr(bpy.context.preferences, "studio_lights"):
                print(f"utils: HDRI '{self.studio_light}' not found. Falling back to first available WORLD studio light.")
                for sl in bpy.context.preferences.studio_lights:
                    if sl.type == 'WORLD' and sl.path:
                        hdri_path = sl.path
                        break
                        
            if not hdri_path:
                raise FileNotFoundError(f"Could not find HDRI '{self.studio_light}' or any fallback studio light in Blender.")
    
            # 3. Load HDRI image (Blender automatically reuse images via check_existing)
            try:
                self.temp_image = bpy.data.images.load(hdri_path, check_existing=True)
            except Exception as e:
                print(f"utils: Error loading HDRI '{hdri_path}': {e}")
                raise
    
            # 4. Get or create temporary World block (session persistent, no aggressive deletion)
            temp_world_name = f"Temp_LookDev_World_{self.studio_light}"
            self.temp_world = bpy.data.worlds.get(temp_world_name)
            if not self.temp_world:
                self.temp_world = bpy.data.worlds.new(name=temp_world_name)
                
            # Rebuild/configure the node tree to match LookDev specifications
            if hasattr(self.temp_world, "use_nodes"):
                self.temp_world.use_nodes = True
            nt = self.temp_world.node_tree
            nt.nodes.clear()
            
            node_out = nt.nodes.new('ShaderNodeOutputWorld')
            node_bg = nt.nodes.new('ShaderNodeBackground')
            node_tex = nt.nodes.new('ShaderNodeTexEnvironment')
            node_mapping = nt.nodes.new('ShaderNodeMapping')
            node_coord = nt.nodes.new('ShaderNodeTexCoord')
            
            node_tex.image = self.temp_image
            node_mapping.inputs['Rotation'].default_value[2] = self.rotate_z
            node_bg.inputs['Strength'].default_value = self.intensity
            
            nt.links.new(node_coord.outputs['Generated'], node_mapping.inputs['Vector'])
            nt.links.new(node_mapping.outputs['Vector'], node_tex.inputs['Vector'])
            nt.links.new(node_tex.outputs['Color'], node_bg.inputs['Color'])
            nt.links.new(node_bg.outputs['Background'], node_out.inputs['Surface'])
            
            # 5. Swap World and engine settings
            self.scene.world = self.temp_world
            swapped_world = True
            
            self.scene.render.engine = 'BLENDER_EEVEE'
            swapped_engine = True
            
            if hasattr(self.scene, "eevee") and hasattr(self.scene.eevee, "taa_render_samples"):
                self.scene.eevee.taa_render_samples = 4
                swapped_samples = True
                
            # 6. Optionally hide physical scene lights
            if not self.use_scene_lights:
                for obj in self.scene.objects:
                    if obj.type == 'LIGHT':
                        try:
                            orig_hide = obj.hide_render
                            obj.hide_render = True
                            self.hidden_lights.append((obj, orig_hide))
                        except Exception as e:
                            print(f"utils: Warning - Could not hide light '{obj.name}' (possibly read-only linked data): {e}")
                            
        except Exception:
            # ROLLBACK: Revert any partial changes if initialization fails
            if swapped_world:
                try:
                    self.scene.world = self.orig_world
                except Exception:
                    pass
            if swapped_engine:
                try:
                    self.scene.render.engine = self.orig_engine
                except Exception:
                    pass
            if swapped_samples and self.orig_samples is not None:
                try:
                    self.scene.eevee.taa_render_samples = self.orig_samples
                except Exception:
                    pass
            for obj, orig_hide in self.hidden_lights:
                try:
                    obj.hide_render = orig_hide
                except Exception:
                    pass
            raise
            
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore scene lights
        for obj, orig_hide in self.hidden_lights:
            try:
                obj.hide_render = orig_hide
            except Exception as e:
                print(f"utils: Warning restoring hide_render for object '{obj.name}': {e}")
                
        # Restore original world, engine and EEVEE samples
        try:
            self.scene.world = self.orig_world
        except Exception as e:
            print(f"utils: Warning restoring original world: {e}")
            
        try:
            self.scene.render.engine = self.orig_engine
        except Exception as e:
            print(f"utils: Warning restoring original render engine: {e}")
            
        if self.orig_samples is not None and hasattr(self.scene, "eevee") and hasattr(self.scene.eevee, "taa_render_samples"):
            try:
                self.scene.eevee.taa_render_samples = self.orig_samples
            except Exception as e:
                print(f"utils: Warning restoring original EEVEE samples: {e}")


def get_clip_context(context):
    """
    Retorna (collection, index_prop_name, owner_data_block).
    Si no hay workspace configurado, retorna la colección legacy en scene para evitar romper la UI antigua.
    """
    ws = get_active_workspace(context)
    if ws is None:
        scene = context.scene
        return getattr(scene, "spritesheet_clips", None), "active_clip_index", scene
    return ws.clips, "active_clip_index", ws


def get_clip_collection_name(context):
    """
    Returns the string name of the clips collection property on the owner.
    """
    ws = get_active_workspace(context)
    if ws is None:
        return "spritesheet_clips"
    return "clips"


def get_active_workspace(context):
    """Retorna el workspace activo o None."""
    scene = context.scene
    workspaces = getattr(scene, "spritesheet_workspaces", None)
    if not workspaces or len(workspaces) == 0:
        return None
    idx = max(0, min(scene.active_workspace_index, len(workspaces) - 1))
    return workspaces[idx]


def resolve_clip_camera(workspace, clip, scene):
    """Resuelve la cámara efectiva para un clip.
    Chequea en orden:
    1. Si use_camera_override es True y clip.camera está seteada -> clip.camera (override local)
    2. Si workspace y workspace.default_camera está seteada -> workspace.default_camera
    3. Si clip.camera está seteada (legacy fallback / compatibilidad) -> clip.camera
    4. Si no hay workspace (modo legacy puro) -> scene.camera (legacy fallback / compatibilidad)
    5. De lo contrario -> None (NO fallback a scene.camera si hay workspace activo)
    """
    if getattr(clip, "use_camera_override", False) and clip.camera:
        return clip.camera
    if workspace and workspace.default_camera:
        return workspace.default_camera
    if clip.camera:
        return clip.camera
    if workspace is None:
        return scene.camera
    return None


def resolve_clip_collections(workspace, clip):
    """Resuelve las colecciones efectivas para un clip.
    Retorna una lista de SpriteSheetIncludedCollection items, o lista vacía.
    Chequea en orden:
    1. Si use_collection_override es True y tiene elementos -> clip.included_collections
    2. Si workspace.default_collections tiene elementos -> workspace.default_collections
    3. Si no hay overrides ni defaults pero el clip tiene colecciones legacy -> clip.included_collections
    4. De lo contrario -> []
    """
    if getattr(clip, "use_collection_override", False) and len(clip.included_collections) > 0:
        return list(clip.included_collections)
    if workspace and len(workspace.default_collections) > 0:
        return list(workspace.default_collections)
    if len(clip.included_collections) > 0:  # Legacy fallback si no hay configuraciones del workspace
        return list(clip.included_collections)
    return []



