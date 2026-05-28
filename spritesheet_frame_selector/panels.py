import bpy
from .utils import calculate_sheet_dimensions, validate_export_settings

class SPRITESHEET_UL_clip_list(bpy.types.UIList):
    """UIList for animation clips"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "include_in_export", text="")
            row.label(icon='ACTION')
            row.prop(item, "name", text="", emboss=False)
            
            # Show frame range summary
            frames_count = ((item.frame_end - item.frame_start) // item.frame_step) + 1
            row.label(text=f"({frames_count} frames)", translate=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.name, icon='ACTION')


class SPRITESHEET_PT_main(bpy.types.Panel):
    """Parent panel for the SpriteSheet Frame Selector"""
    bl_label = "SpriteSheet Frame Selector"
    bl_idname = "SPRITESHEET_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SpriteSheet"

    def draw(self, context):
        layout = self.layout
        # Main panel acts as container, subpanels do the drawing.
        # But we can display a brief info/status if empty.
        scene = context.scene
        if len(scene.spritesheet_clips) == 0:
            layout.label(text="Get started by adding an animation clip.")
            layout.operator("spritesheet.add_clip", text="Add Animation Clip", icon='ADD')


class SPRITESHEET_PT_clips(bpy.types.Panel):
    bl_label = "Animation Clips"
    bl_idname = "SPRITESHEET_PT_clips"
    bl_parent_id = "SPRITESHEET_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        return (len(scene.spritesheet_clips) > 0
                and 0 <= scene.active_clip_index < len(scene.spritesheet_clips))

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # List of clips
        row = layout.row()
        row.template_list(
            "SPRITESHEET_UL_clip_list", "",
            scene, "spritesheet_clips",
            scene, "active_clip_index",
            rows=3
        )
        
        col = row.column(align=True)
        col.operator("spritesheet.add_clip", text="", icon='ADD')
        col.operator("spritesheet.remove_clip", text="", icon='REMOVE')
        col.operator("spritesheet.duplicate_clip", text="", icon='DUPLICATE')
        
        # Selected clip settings
        if len(scene.spritesheet_clips) > 0 and 0 <= scene.active_clip_index < len(scene.spritesheet_clips):
            clip = scene.spritesheet_clips[scene.active_clip_index]
            
            box = layout.box()
            box.label(text=f"Clip Settings: {clip.name}", icon='PROPERTIES')
            
            box.prop(clip, "name", text="Name")
            
            row = box.row(align=True)
            row.prop(clip, "frame_start", text="Start")
            row.prop(clip, "frame_end", text="End")
            
            row = box.row(align=True)
            row.prop(clip, "frame_step", text="Step")
            row.prop(clip, "fps", text="FPS")
            
            box.prop(clip, "camera", text="Camera Override")
            
            box.separator()
            box.label(text="Included Collections (Whitelist):", icon='OUTLINER_COLLECTION')
            
            col_box = box.column(align=True)
            for idx, item in enumerate(clip.included_collections):
                row = col_box.row(align=True)
                row.prop(item, "collection", text="")
                
                if item.collection is None and item.collection_name != "":
                    row.label(text=f"⚠️ Missing: {item.collection_name}")
                    
                op = row.operator("spritesheet.remove_included_collection", text="", icon='REMOVE')
                op.index = idx
                
            row = box.row()
            row.operator("spritesheet.add_included_collection", text="Add Collection", icon='ADD')


class SPRITESHEET_PT_preview(bpy.types.Panel):
    bl_label = "Preview Cache"
    bl_idname = "SPRITESHEET_PT_preview"
    bl_parent_id = "SPRITESHEET_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return (len(scene.spritesheet_clips) > 0
                and 0 <= scene.active_clip_index < len(scene.spritesheet_clips))

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        clip = scene.spritesheet_clips[scene.active_clip_index]
        
        layout.prop(clip, "preview_size", text="Preview Size")
        
        # Preview buttons
        row = layout.row(align=True)
        row.operator("spritesheet.generate_preview", text="Generate Previews", icon='RENDER_STILL')
        row.operator("spritesheet.refresh_preview", text="Refresh", icon='FILE_REFRESH')
        row.operator("spritesheet.clear_cache", text="Clear Cache", icon='TRASH')
        
        # Status display
        total_frames = ((clip.frame_end - clip.frame_start) // clip.frame_step) + 1
        cached_frames = len(clip.frames)
        
        if cached_frames > 0:
            if clip.cache_dirty:
                layout.label(text=f"Cached: {cached_frames}/{total_frames} (Outdated)", icon='ERROR')
            else:
                layout.label(text=f"Cached: {cached_frames}/{total_frames} frames", icon='CHECKBOX_HLT')
        else:
            layout.label(text="No previews cached yet.", icon='QUESTION')


class SPRITESHEET_PT_selection(bpy.types.Panel):
    bl_label = "Visual Selection"
    bl_idname = "SPRITESHEET_PT_selection"
    bl_parent_id = "SPRITESHEET_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if len(scene.spritesheet_clips) == 0:
            return False
        if not (0 <= scene.active_clip_index < len(scene.spritesheet_clips)):
            return False
        clip = scene.spritesheet_clips[scene.active_clip_index]
        return len(clip.frames) > 0

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        clip = scene.spritesheet_clips[scene.active_clip_index]
        
        # Open visual selector button
        layout.scale_y = 1.3
        layout.operator("spritesheet.open_visual_selector", text="Open Visual Selector", icon='WINDOW')
        layout.scale_y = 1.0
        
        # Selection count
        selected_count = sum(1 for f in clip.frames if f.selected)
        layout.label(text=f"Selected: {selected_count} / {len(clip.frames)} frames", icon='SELECT_SET')
        
        # Selection operations
        box = layout.box()
        box.label(text="Quick Selection Tools")
        
        row = box.row(align=True)
        row.operator("spritesheet.select_all", text="All")
        row.operator("spritesheet.deselect_all", text="None")
        row.operator("spritesheet.invert_selection", text="Invert")
        
        # Select Every N row
        row = box.row(align=True)
        row.operator("spritesheet.select_every_n", text="Every N")


class SPRITESHEET_PT_export(bpy.types.Panel):
    bl_label = "Export Configuration"
    bl_idname = "SPRITESHEET_PT_export"
    bl_parent_id = "SPRITESHEET_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return (len(scene.spritesheet_clips) > 0
                and 0 <= scene.active_clip_index < len(scene.spritesheet_clips))

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        export_settings = scene.spritesheet_export
        clip = scene.spritesheet_clips[scene.active_clip_index]
        
        layout.prop(export_settings, "sheet_name", text="Sheet Name")
        layout.prop(export_settings, "output_folder", text="Output Path")
        
        # Frame size and packaging
        row = layout.row(align=True)
        row.prop(export_settings, "frame_width", text="Width")
        row.prop(export_settings, "frame_height", text="Height")
        
        row = layout.row(align=True)
        row.prop(export_settings, "columns", text="Columns")
        row.prop(export_settings, "transparent", text="Alpha")
        
        row = layout.row(align=True)
        row.prop(export_settings, "padding", text="Padding")
        row.prop(export_settings, "margin", text="Margin")
        
        layout.prop(export_settings, "export_png_sequence", text="Export individual PNG sequence")
        
        # Stats & Verification
        clips_to_export = [c for c in scene.spritesheet_clips if c.include_in_export]
        n_selected = sum(sum(1 for f in c.frames if f.selected) for c in clips_to_export)
        
        if n_selected > 0:
            rows, width, height = calculate_sheet_dimensions(
                n_selected, 
                export_settings.frame_width, 
                export_settings.frame_height, 
                export_settings.columns, 
                export_settings.padding, 
                export_settings.margin
            )
            
            box = layout.box()
            box.label(text="Estimated Output Details", icon='INFO')
            box.label(text=f"Clips Included: {len(clips_to_export)}")
            box.label(text=f"Total Frames: {n_selected}")
            box.label(text=f"Grid: {export_settings.columns} col x {rows} rows")
            box.label(text=f"Resolution: {width} x {height} px")
            
            # Dimensions warning
            if width > 8192 or height > 8192:
                box.label(text="⚠️ Sheet exceeds 8192px! (Huge resolution)", icon='ERROR')
            elif width > 4096 or height > 4096:
                box.label(text="⚠️ Sheet exceeds 4096px (Large resolution)", icon='WARNING')
        
        # Validation checks & Export Button
        is_valid, err_msg = validate_export_settings(scene)
        
        layout.separator()
        layout.scale_y = 1.5
        
        # Always keep button active
        layout.operator("spritesheet.export_clip", text="EXPORT SPRITESHEET", icon='EXPORT')
        
        if not is_valid:
            # Show validation error message in small font
            box = layout.box()
            col = box.column()
            col.label(text="Cannot Export:")
            col.label(text=f"- {err_msg}")


classes = (
    SPRITESHEET_UL_clip_list,
    SPRITESHEET_PT_main,
    SPRITESHEET_PT_clips,
    SPRITESHEET_PT_preview,
    SPRITESHEET_PT_selection,
    SPRITESHEET_PT_export,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
