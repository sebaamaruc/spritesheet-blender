import bpy
from .preview_generator import generate_clip_previews, clear_clip_previews

class SPRITESHEET_OT_add_clip(bpy.types.Operator):
    bl_idname = "spritesheet.add_clip"
    bl_label = "Add Clip"
    bl_description = "Add a new animation clip configuration"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        clip = scene.spritesheet_clips.add()
        clip.name = f"Clip_{len(scene.spritesheet_clips)}"
        
        # Set default frames to match scene start/end
        clip.frame_start = scene.frame_start
        clip.frame_end = scene.frame_end
        
        # Select the newly added clip
        scene.active_clip_index = len(scene.spritesheet_clips) - 1
        
        self.report({'INFO'}, f"Added clip: {clip.name}")
        return {'FINISHED'}


class SPRITESHEET_OT_remove_clip(bpy.types.Operator):
    bl_idname = "spritesheet.remove_clip"
    bl_label = "Remove Clip"
    bl_description = "Remove the selected animation clip"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return len(scene.spritesheet_clips) > 0

    def execute(self, context):
        scene = context.scene
        idx = scene.active_clip_index
        
        if idx < 0 or idx >= len(scene.spritesheet_clips):
            self.report({'WARNING'}, "No active clip selected")
            return {'CANCELLED'}
            
        clip = scene.spritesheet_clips[idx]
        clip_name = clip.name
        
        # Clear cache files
        clear_clip_previews(clip)
        
        # Remove from collection
        scene.spritesheet_clips.remove(idx)
        
        # Adjust active index
        if scene.active_clip_index >= len(scene.spritesheet_clips):
            scene.active_clip_index = max(0, len(scene.spritesheet_clips) - 1)
            
        self.report({'INFO'}, f"Removed clip: {clip_name}")
        return {'FINISHED'}


class SPRITESHEET_OT_duplicate_clip(bpy.types.Operator):
    bl_idname = "spritesheet.duplicate_clip"
    bl_label = "Duplicate Clip"
    bl_description = "Duplicate the active clip configuration"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return len(scene.spritesheet_clips) > 0

    def execute(self, context):
        scene = context.scene
        idx = scene.active_clip_index
        
        if idx < 0 or idx >= len(scene.spritesheet_clips):
            self.report({'WARNING'}, "No active clip selected")
            return {'CANCELLED'}
            
        src = scene.spritesheet_clips[idx]
        
        # Create new clip
        dst = scene.spritesheet_clips.add()
        dst.name = f"{src.name}_copy"
        dst.frame_start = src.frame_start
        dst.frame_end = src.frame_end
        dst.frame_step = src.frame_step
        dst.camera = src.camera
        dst.preview_size = src.preview_size
        dst.fps = src.fps
        dst.playback_loop = src.playback_loop
        
        # We don't copy cached frames preview paths as we want to regenerate them, 
        # but we can copy the selection states if frames exists.
        if len(src.frames) > 0:
            for src_frame in src.frames:
                item = dst.frames.add()
                item.frame_number = src_frame.frame_number
                item.selected = src_frame.selected
                # preview_path remains empty, marking cache_dirty=True by default
            dst.cache_dirty = True
        
        scene.active_clip_index = len(scene.spritesheet_clips) - 1
        self.report({'INFO'}, f"Duplicated clip: {src.name} as {dst.name}")
        return {'FINISHED'}


class SPRITESHEET_OT_generate_preview(bpy.types.Operator):
    bl_idname = "spritesheet.generate_preview"
    bl_label = "Generate Preview"
    bl_description = "Generate viewport previews for the active clip"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if len(scene.spritesheet_clips) == 0:
            return False
        idx = scene.active_clip_index
        return 0 <= idx < len(scene.spritesheet_clips)

    def execute(self, context):
        scene = context.scene
        clip = scene.spritesheet_clips[scene.active_clip_index]
        
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
        scene = context.scene
        clip = scene.spritesheet_clips[scene.active_clip_index]
        
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
        scene = context.scene
        clip = scene.spritesheet_clips[scene.active_clip_index]
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
        scene = context.scene
        if len(scene.spritesheet_clips) == 0:
            return False
        clip = scene.spritesheet_clips[scene.active_clip_index]
        return len(clip.frames) > 0

    def execute(self, context):
        clip = context.scene.spritesheet_clips[context.scene.active_clip_index]
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
        clip = context.scene.spritesheet_clips[context.scene.active_clip_index]
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
        clip = context.scene.spritesheet_clips[context.scene.active_clip_index]
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
        clip = context.scene.spritesheet_clips[context.scene.active_clip_index]
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
        scene = context.scene
        if len(scene.spritesheet_clips) == 0:
            return False
        idx = scene.active_clip_index
        if idx < 0 or idx >= len(scene.spritesheet_clips):
            return False
        return len(scene.spritesheet_clips[idx].frames) > 0

    def invoke(self, context, event):
        return bpy.ops.spritesheet.visual_selector('INVOKE_DEFAULT')


class SPRITESHEET_OT_export_clip(bpy.types.Operator):
    bl_idname = "spritesheet.export_clip"
    bl_label = "Export SpriteSheet"
    bl_description = "Export active/selected clips to a spritesheet"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if len(scene.spritesheet_clips) == 0:
            return False
        return any(c.include_in_export and any(f.selected for f in c.frames) for c in scene.spritesheet_clips)

    def execute(self, context):
        from .utils import validate_export_settings
        from .exporter import export_multiple_clips
        
        scene = context.scene
        is_valid, err_msg = validate_export_settings(scene)
        if not is_valid:
            self.report({'ERROR'}, err_msg)
            return {'CANCELLED'}
        
        clips = list(scene.spritesheet_clips)
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
        if len(context.scene.spritesheet_clips) > 0:
            clip = context.scene.spritesheet_clips[context.scene.active_clip_index]
            self.fps = clip.fps
        return context.window_manager.invoke_props_dialog(self)
        
    def execute(self, context):
        if len(context.scene.spritesheet_clips) > 0:
            clip = context.scene.spritesheet_clips[context.scene.active_clip_index]
            clip.fps = self.fps
            # Trigger redrawing of viewports
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        return {'FINISHED'}


classes = (
    SPRITESHEET_OT_set_playback_fps,
    SPRITESHEET_OT_add_clip,
    SPRITESHEET_OT_remove_clip,
    SPRITESHEET_OT_duplicate_clip,
    SPRITESHEET_OT_generate_preview,
    SPRITESHEET_OT_refresh_preview,
    SPRITESHEET_OT_clear_cache,
    SPRITESHEET_OT_select_all,
    SPRITESHEET_OT_deselect_all,
    SPRITESHEET_OT_invert_selection,
    SPRITESHEET_OT_select_every_n,
    SPRITESHEET_OT_open_visual_selector,
    SPRITESHEET_OT_export_clip,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
