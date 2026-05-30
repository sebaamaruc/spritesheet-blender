import bpy
from .preview_generator import generate_clip_previews, clear_clip_previews
from .utils import get_clip_context, get_active_workspace

class SPRITESHEET_OT_add_clip(bpy.types.Operator):
    bl_idname = "spritesheet.add_clip"
    bl_label = "Add Clip"
    bl_description = "Add a new animation clip configuration"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        collection, index_name, owner = get_clip_context(context)
        clip = collection.add()
        clip.name = f"Clip_{len(collection)}"
        
        # Set default frames to match scene start/end
        clip.frame_start = scene.frame_start
        clip.frame_end = scene.frame_end
        
        # Select the newly added clip
        setattr(owner, index_name, len(collection) - 1)
        
        self.report({'INFO'}, f"Added clip: {clip.name}")
        return {'FINISHED'}


class SPRITESHEET_OT_remove_clip(bpy.types.Operator):
    bl_idname = "spritesheet.remove_clip"
    bl_label = "Remove Clip"
    bl_description = "Remove the selected animation clip"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collection, index_name, owner = get_clip_context(context)
        return len(collection) > 0

    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        idx = getattr(owner, index_name)
        
        if idx < 0 or idx >= len(collection):
            self.report({'WARNING'}, "No active clip selected")
            return {'CANCELLED'}
            
        clip = collection[idx]
        clip_name = clip.name
        
        # Clear cache files
        clear_clip_previews(clip)
        
        # Remove from collection
        collection.remove(idx)
        
        # Adjust active index
        curr_idx = getattr(owner, index_name)
        if curr_idx >= len(collection):
            setattr(owner, index_name, max(0, len(collection) - 1))
            
        self.report({'INFO'}, f"Removed clip: {clip_name}")
        return {'FINISHED'}


class SPRITESHEET_OT_duplicate_clip(bpy.types.Operator):
    bl_idname = "spritesheet.duplicate_clip"
    bl_label = "Duplicate Clip"
    bl_description = "Duplicate the active clip configuration"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collection, index_name, owner = get_clip_context(context)
        return len(collection) > 0

    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        idx = getattr(owner, index_name)
        
        if idx < 0 or idx >= len(collection):
            self.report({'WARNING'}, "No active clip selected")
            return {'CANCELLED'}
            
        src = collection[idx]
        
        # Create new clip
        dst = collection.add()
        dst.name = f"{src.name}_copy"
        dst.frame_start = src.frame_start
        dst.frame_end = src.frame_end
        dst.frame_step = src.frame_step
        dst.camera = src.camera
        dst.use_camera_override = src.use_camera_override
        dst.use_collection_override = src.use_collection_override
        dst.preview_size = src.preview_size
        dst.fps = src.fps
        dst.playback_loop = src.playback_loop
        
        # Copy included_collections
        for src_item in src.included_collections:
            dst_item = dst.included_collections.add()
            dst_item.collection = src_item.collection
            dst_item.collection_name = src_item.collection_name
            
        # We don't copy cached frames preview paths as we want to regenerate them, 
        # but we can copy the selection states if frames exists.
        if len(src.frames) > 0:
            for src_frame in src.frames:
                item = dst.frames.add()
                item.frame_number = src_frame.frame_number
                item.selected = src_frame.selected
            dst.cache_dirty = True
        
        setattr(owner, index_name, len(collection) - 1)
        self.report({'INFO'}, f"Duplicated clip: {src.name} as {dst.name}")
        return {'FINISHED'}


class SPRITESHEET_OT_generate_preview(bpy.types.Operator):
    bl_idname = "spritesheet.generate_preview"
    bl_label = "Generate Preview"
    bl_description = "Generate viewport previews for the active clip"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        collection, index_name, owner = get_clip_context(context)
        if len(collection) == 0:
            return False
        idx = getattr(owner, index_name)
        return 0 <= idx < len(collection)

    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        idx = getattr(owner, index_name)
        clip = collection[idx]
        
        # Generate previews
        success = generate_clip_previews(clip, context)
        if success:
            self.report({'INFO'}, f"Generated previews for {clip.name}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Could not generate previews. Check frame range.")
            return {'CANCELLED'}


class SPRITESHEET_OT_refresh_preview(bpy.types.Operator):
    bl_idname = "spritesheet.refresh_preview"
    bl_label = "Refresh Previews"
    bl_description = "Force refresh/regenerate previews for the active clip"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return SPRITESHEET_OT_generate_preview.poll(context)

    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        clip = collection[getattr(owner, index_name)]
        
        # Clear existing previews first
        clear_clip_previews(clip)
        
        # Regenerate
        success = generate_clip_previews(clip, context)
        if success:
            self.report({'INFO'}, f"Refreshed previews for {clip.name}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Could not refresh previews.")
            return {'CANCELLED'}


class SPRITESHEET_OT_clear_cache(bpy.types.Operator):
    bl_idname = "spritesheet.clear_cache"
    bl_label = "Clear Cache"
    bl_description = "Delete preview cache files for the active clip"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return SPRITESHEET_OT_generate_preview.poll(context)

    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        clip = collection[getattr(owner, index_name)]
        clear_clip_previews(clip)
        self.report({'INFO'}, f"Cleared preview cache for {clip.name}")
        return {'FINISHED'}


# Selection modifiers
class SPRITESHEET_OT_select_all(bpy.types.Operator):
    bl_idname = "spritesheet.select_all"
    bl_label = "Select All"
    bl_description = "Select all frames in the active clip"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collection, index_name, owner = get_clip_context(context)
        if len(collection) == 0:
            return False
        clip = collection[getattr(owner, index_name)]
        return len(clip.frames) > 0

    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        clip = collection[getattr(owner, index_name)]
        for frame in clip.frames:
            frame.selected = True
        return {'FINISHED'}


class SPRITESHEET_OT_deselect_all(bpy.types.Operator):
    bl_idname = "spritesheet.deselect_all"
    bl_label = "Deselect All"
    bl_description = "Deselect all frames in the active clip"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return SPRITESHEET_OT_select_all.poll(context)

    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        clip = collection[getattr(owner, index_name)]
        for frame in clip.frames:
            frame.selected = False
        return {'FINISHED'}


class SPRITESHEET_OT_invert_selection(bpy.types.Operator):
    bl_idname = "spritesheet.invert_selection"
    bl_label = "Invert Selection"
    bl_description = "Invert frame selection in the active clip"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return SPRITESHEET_OT_select_all.poll(context)

    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        clip = collection[getattr(owner, index_name)]
        for frame in clip.frames:
            frame.selected = not frame.selected
        return {'FINISHED'}


class SPRITESHEET_OT_select_every_n(bpy.types.Operator):
    bl_idname = "spritesheet.select_every_n"
    bl_label = "Select Every N"
    bl_description = "Select every Nth frame and deselect the rest"
    bl_options = {'REGISTER', 'UNDO'}

    n: bpy.props.IntProperty(
        name="N",
        default=2,
        min=1,
        description="Select every Nth frame"
    )

    @classmethod
    def poll(cls, context):
        return SPRITESHEET_OT_select_all.poll(context)

    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        clip = collection[getattr(owner, index_name)]
        for i, frame in enumerate(clip.frames):
            frame.selected = (i % self.n == 0)
        self.report({'INFO'}, f"Selected every {self.n}th frame")
        return {'FINISHED'}


class SPRITESHEET_OT_open_visual_selector(bpy.types.Operator):
    bl_idname = "spritesheet.open_visual_selector"
    bl_label = "Open Visual Selector"
    bl_description = "Open the interactive grid frame selector"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        collection, index_name, owner = get_clip_context(context)
        if len(collection) == 0:
            return False
        idx = getattr(owner, index_name)
        if idx < 0 or idx >= len(collection):
            return False
        return len(collection[idx].frames) > 0

    def invoke(self, context, event):
        return bpy.ops.spritesheet.visual_selector('INVOKE_DEFAULT')


class SPRITESHEET_OT_export_clip(bpy.types.Operator):
    bl_idname = "spritesheet.export_clip"
    bl_label = "Export SpriteSheet"
    bl_description = "Export active/selected clips to a spritesheet"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        collection, index_name, owner = get_clip_context(context)
        return len(collection) > 0

    def execute(self, context):
        from .utils import validate_export_settings, get_active_workspace
        from .exporter import export_multiple_clips
        
        scene = context.scene
        is_valid, err_msg = validate_export_settings(scene)
        if not is_valid:
            self.report({'ERROR'}, err_msg)
            return {'CANCELLED'}
        
        collection, index_name, owner = get_clip_context(context)
        clips = list(collection)
        
        ws = get_active_workspace(context)
        if ws:
            export_settings = ws.export_settings
        else:
            export_settings = scene.spritesheet_export
        
        success = export_multiple_clips(clips, export_settings, context)
        if success:
            self.report({'INFO'}, "Export completed successfully!")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Export failed. Check console for details.")
            return {'CANCELLED'}

class SPRITESHEET_OT_set_playback_fps(bpy.types.Operator):
    bl_idname = "spritesheet.set_playback_fps"
    bl_label = "Set Playback FPS"
    bl_options = {'INTERNAL'}
    
    fps: bpy.props.IntProperty(
        name="FPS",
        description="Playback speed in frames per second",
        min=1,
        max=120,
        default=24
    )
    
    def invoke(self, context, event):
        collection, index_name, owner = get_clip_context(context)
        if len(collection) > 0:
            clip = collection[getattr(owner, index_name)]
            self.fps = clip.fps
        return context.window_manager.invoke_props_dialog(self)
        
    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        if len(collection) > 0:
            clip = collection[getattr(owner, index_name)]
            clip.fps = self.fps
            # Trigger redrawing of viewports
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        return {'FINISHED'}


class SPRITESHEET_OT_add_included_collection(bpy.types.Operator):
    bl_idname = "spritesheet.add_included_collection"
    bl_label = "Add Included Collection"
    bl_description = "Add a collection to the visibility whitelist for this clip"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collection, index_name, owner = get_clip_context(context)
        return (len(collection) > 0 
                and 0 <= getattr(owner, index_name) < len(collection))

    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        clip = collection[getattr(owner, index_name)]
        clip.included_collections.add()
        clip.cache_dirty = True
        return {'FINISHED'}


class SPRITESHEET_OT_remove_included_collection(bpy.types.Operator):
    bl_idname = "spritesheet.remove_included_collection"
    bl_label = "Remove Included Collection"
    bl_description = "Remove a collection from the visibility whitelist for this clip"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty(name="Index")

    @classmethod
    def poll(cls, context):
        collection, index_name, owner = get_clip_context(context)
        return (len(collection) > 0 
                and 0 <= getattr(owner, index_name) < len(collection))

    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        clip = collection[getattr(owner, index_name)]
        if 0 <= self.index < len(clip.included_collections):
            clip.included_collections.remove(self.index)
            clip.cache_dirty = True
            return {'FINISHED'}
        return {'CANCELLED'}


class SPRITESHEET_OT_move_clip(bpy.types.Operator):
    bl_idname = "spritesheet.move_clip"
    bl_label = "Move Clip"
    bl_description = "Move the active animation clip up or down in the list"
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.EnumProperty(
        items=[
            ('UP', "Up", "Move clip up"),
            ('DOWN', "Down", "Move clip down")
        ],
        name="Direction",
        default='UP'
    )

    @classmethod
    def poll(cls, context):
        collection, index_name, owner = get_clip_context(context)
        return len(collection) > 1

    def execute(self, context):
        collection, index_name, owner = get_clip_context(context)
        idx = getattr(owner, index_name)
        
        if idx < 0 or idx >= len(collection):
            self.report({'WARNING'}, "No active clip selected")
            return {'CANCELLED'}

        if self.direction == 'UP':
            if idx == 0:
                self.report({'INFO'}, "Clip is already at the top")
                return {'CANCELLED'}
            new_idx = idx - 1
        else: # DOWN
            if idx == len(collection) - 1:
                self.report({'INFO'}, "Clip is already at the bottom")
                return {'CANCELLED'}
            new_idx = idx + 1
            
        collection.move(idx, new_idx)
        setattr(owner, index_name, new_idx)
        
        return {'FINISHED'}


class SPRITESHEET_OT_add_workspace(bpy.types.Operator):
    bl_idname = "spritesheet.add_workspace"
    bl_label = "Add Workspace"
    bl_description = "Add a new export workspace"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        ws = scene.spritesheet_workspaces.add()
        ws.name = f"Workspace_{len(scene.spritesheet_workspaces)}"
        # Initialize default values
        ws.output_name = "spritesheet"
        ws.output_folder = ""
        ws.active_clip_index = 0
        # Initialize PointerProperty export_settings
        ws.export_settings.frame_width = 64
        ws.export_settings.frame_height = 64
        ws.export_settings.columns = 8
        ws.export_settings.padding = 0
        ws.export_settings.margin = 0
        ws.export_settings.transparent = True
        ws.export_settings.export_png_sequence = False
        ws.export_settings.sheet_name = "spritesheet"

        scene.active_workspace_index = len(scene.spritesheet_workspaces) - 1
        self.report({'INFO'}, f"Added workspace: {ws.name}")
        return {'FINISHED'}


class SPRITESHEET_OT_remove_workspace(bpy.types.Operator):
    bl_idname = "spritesheet.remove_workspace"
    bl_label = "Remove Workspace"
    bl_description = "Remove the active export workspace"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.spritesheet_workspaces) > 0

    def execute(self, context):
        scene = context.scene
        idx = scene.active_workspace_index
        if idx < 0 or idx >= len(scene.spritesheet_workspaces):
            self.report({'WARNING'}, "No active workspace selected")
            return {'CANCELLED'}

        ws_name = scene.spritesheet_workspaces[idx].name
        scene.spritesheet_workspaces.remove(idx)
        scene.active_workspace_index = max(0, idx - 1)
        self.report({'INFO'}, f"Removed workspace: {ws_name}")
        return {'FINISHED'}


class SPRITESHEET_OT_duplicate_workspace(bpy.types.Operator):
    bl_idname = "spritesheet.duplicate_workspace"
    bl_label = "Duplicate Workspace"
    bl_description = "Duplicate the active export workspace and its configuration"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.spritesheet_workspaces) > 0

    def execute(self, context):
        scene = context.scene
        idx = scene.active_workspace_index
        if idx < 0 or idx >= len(scene.spritesheet_workspaces):
            self.report({'WARNING'}, "No active workspace selected")
            return {'CANCELLED'}

        src = scene.spritesheet_workspaces[idx]
        dst = scene.spritesheet_workspaces.add()
        dst.name = f"{src.name}_copy"
        dst.output_name = src.output_name
        dst.output_folder = src.output_folder
        dst.default_camera = src.default_camera

        # Copy default_collections (by reference to the same Blender collections)
        for src_coll in src.default_collections:
            dst_coll = dst.default_collections.add()
            dst_coll.collection = src_coll.collection
            dst_coll.collection_name = src_coll.collection_name

        # Copy export_settings
        dst.export_settings.frame_width = src.export_settings.frame_width
        dst.export_settings.frame_height = src.export_settings.frame_height
        dst.export_settings.columns = src.export_settings.columns
        dst.export_settings.padding = src.export_settings.padding
        dst.export_settings.margin = src.export_settings.margin
        dst.export_settings.transparent = src.export_settings.transparent
        dst.export_settings.export_png_sequence = src.export_settings.export_png_sequence
        dst.export_settings.sheet_name = src.export_settings.sheet_name

        # Copy clips
        for src_clip in src.clips:
            dst_clip = dst.clips.add()
            dst_clip.name = src_clip.name
            dst_clip.include_in_export = src_clip.include_in_export
            dst_clip.frame_start = src_clip.frame_start
            dst_clip.frame_end = src_clip.frame_end
            dst_clip.frame_step = src_clip.frame_step
            dst_clip.camera = src_clip.camera
            dst_clip.use_camera_override = src_clip.use_camera_override
            dst_clip.use_collection_override = src_clip.use_collection_override
            dst_clip.preview_size = src_clip.preview_size
            dst_clip.fps = src_clip.fps
            dst_clip.playback_loop = src_clip.playback_loop

            # Copy collection references (included_collections)
            for src_included in src_clip.included_collections:
                dst_included = dst_clip.included_collections.add()
                dst_included.collection = src_included.collection
                dst_included.collection_name = src_included.collection_name

            # Copy frames and selection state
            for src_frame in src_clip.frames:
                dst_frame = dst_clip.frames.add()
                dst_frame.frame_number = src_frame.frame_number
                dst_frame.selected = src_frame.selected
                dst_frame.preview_path = src_frame.preview_path

        scene.active_workspace_index = len(scene.spritesheet_workspaces) - 1
        self.report({'INFO'}, f"Duplicated workspace: {src.name} to {dst.name}")
        return {'FINISHED'}


class SPRITESHEET_OT_add_ws_collection(bpy.types.Operator):
    bl_idname = "spritesheet.add_ws_collection"
    bl_label = "Add Workspace Collection"
    bl_description = "Add a collection to the workspace default visibility whitelist"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.spritesheet_workspaces) > 0

    def execute(self, context):
        ws = get_active_workspace(context)
        if ws:
            ws.default_collections.add()
            for clip in ws.clips:
                clip.cache_dirty = True
            return {'FINISHED'}
        return {'CANCELLED'}


class SPRITESHEET_OT_remove_ws_collection(bpy.types.Operator):
    bl_idname = "spritesheet.remove_ws_collection"
    bl_label = "Remove Workspace Collection"
    bl_description = "Remove a collection from the workspace default visibility whitelist"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty(name="Index to Remove")

    @classmethod
    def poll(cls, context):
        try:
            ws = get_active_workspace(context)
            return ws is not None and len(ws.default_collections) > 0
        except:
            return False

    def execute(self, context):
        ws = get_active_workspace(context)
        if ws and 0 <= self.index < len(ws.default_collections):
            ws.default_collections.remove(self.index)
            for clip in ws.clips:
                clip.cache_dirty = True
            return {'FINISHED'}
        return {'CANCELLED'}


classes = (
    SPRITESHEET_OT_set_playback_fps,
    SPRITESHEET_OT_add_clip,
    SPRITESHEET_OT_remove_clip,
    SPRITESHEET_OT_duplicate_clip,
    SPRITESHEET_OT_move_clip,
    SPRITESHEET_OT_generate_preview,
    SPRITESHEET_OT_refresh_preview,
    SPRITESHEET_OT_clear_cache,
    SPRITESHEET_OT_select_all,
    SPRITESHEET_OT_deselect_all,
    SPRITESHEET_OT_invert_selection,
    SPRITESHEET_OT_select_every_n,
    SPRITESHEET_OT_open_visual_selector,
    SPRITESHEET_OT_export_clip,
    SPRITESHEET_OT_add_included_collection,
    SPRITESHEET_OT_remove_included_collection,
    SPRITESHEET_OT_add_workspace,
    SPRITESHEET_OT_remove_workspace,
    SPRITESHEET_OT_duplicate_workspace,
    SPRITESHEET_OT_add_ws_collection,
    SPRITESHEET_OT_remove_ws_collection,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
