import bpy

def poll_camera(self, object):
    return object.type == 'CAMERA'

class SpriteSheetFrameItem(bpy.types.PropertyGroup):
    frame_number: bpy.props.IntProperty(
        name="Frame Number",
        default=0
    )
    selected: bpy.props.BoolProperty(
        name="Selected",
        default=True
    )
    preview_path: bpy.props.StringProperty(
        name="Preview Path",
        default=""
    )


def on_clip_settings_change(self, context):
    self.cache_dirty = True

class SpriteSheetClip(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Clip Name",
        default="Clip"
    )
    include_in_export: bpy.props.BoolProperty(
        name="Include in Export",
        description="Include this clip in the final spritesheet export",
        default=False
    )
    frame_start: bpy.props.IntProperty(
        name="Start Frame",
        default=1,
        min=0,
        update=on_clip_settings_change
    )
    frame_end: bpy.props.IntProperty(
        name="End Frame",
        default=24,
        min=0,
        update=on_clip_settings_change
    )
    frame_step: bpy.props.IntProperty(
        name="Frame Step",
        default=1,
        min=1,
        update=on_clip_settings_change
    )
    camera: bpy.props.PointerProperty(
        name="Camera Override",
        type=bpy.types.Object,
        poll=poll_camera,
        update=on_clip_settings_change
    )
    preview_size: bpy.props.EnumProperty(
        name="Preview Size",
        items=[
            ('32', '32 x 32', "Generate 32x32 previews"),
            ('64', '64 x 64', "Generate 64x64 previews"),
            ('128', '128 x 128', "Generate 128x128 previews")
        ],
        default='64',
        update=on_clip_settings_change
    )
    frames: bpy.props.CollectionProperty(
        type=SpriteSheetFrameItem
    )
    
    # Internal state tracking
    active_frame_index: bpy.props.IntProperty(
        name="Active Frame Index",
        default=0
    )
    cache_dirty: bpy.props.BoolProperty(
        name="Cache Dirty",
        default=True
    )
    
    # Timing for playback
    fps: bpy.props.IntProperty(
        name="FPS",
        default=12,
        min=1,
        max=120
    )
    playback_loop: bpy.props.BoolProperty(
        name="Loop",
        default=True
    )


class SpriteSheetExportSettings(bpy.types.PropertyGroup):
    frame_width: bpy.props.IntProperty(
        name="Frame Width",
        default=64,
        min=1
    )
    frame_height: bpy.props.IntProperty(
        name="Frame Height",
        default=64,
        min=1
    )
    columns: bpy.props.IntProperty(
        name="Columns",
        default=8,
        min=1
    )
    padding: bpy.props.IntProperty(
        name="Padding",
        default=0,
        min=0
    )
    margin: bpy.props.IntProperty(
        name="Margin",
        default=0,
        min=0
    )
    transparent: bpy.props.BoolProperty(
        name="Transparent",
        default=True
    )
    output_folder: bpy.props.StringProperty(
        name="Output Folder",
        description="Folder where the spritesheet will be saved",
        default="",
        subtype='DIR_PATH'
    )
    sheet_name: bpy.props.StringProperty(
        name="Sheet Name",
        default="spritesheet"
    )
    export_png_sequence: bpy.props.BoolProperty(
        name="Export PNG Sequence",
        description="Also export individual PNG frames",
        default=False
    )


classes = (
    SpriteSheetFrameItem,
    SpriteSheetClip,
    SpriteSheetExportSettings,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.spritesheet_clips = bpy.props.CollectionProperty(type=SpriteSheetClip)
    bpy.types.Scene.active_clip_index = bpy.props.IntProperty(default=0)
    bpy.types.Scene.spritesheet_export = bpy.props.PointerProperty(type=SpriteSheetExportSettings)

def unregister():
    del bpy.types.Scene.spritesheet_export
    del bpy.types.Scene.active_clip_index
    del bpy.types.Scene.spritesheet_clips
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
