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

def update_use_collection_override(self, context):
    self.cache_dirty = True
    if self.use_collection_override and len(self.included_collections) == 0:
        self.included_collections.add()

def update_collection_name(self, context):
    if self.collection:
        self.collection_name = self.collection.name
    
    # Mark cache dirty on all clips that might be affected in the active workspace
    from .utils import get_active_workspace
    try:
        ws = get_active_workspace(context)
        if ws:
            for clip in ws.clips:
                clip.cache_dirty = True
    except Exception as e:
        print(f"properties: error updating cache for workspace clips: {e}")
    
    # Fallback to legacy clips
    try:
        scene = context.scene
        if hasattr(scene, "spritesheet_clips"):
            for clip in scene.spritesheet_clips:
                clip.cache_dirty = True
    except Exception as e:
        print(f"properties: error updating cache for legacy clips: {e}")

class SpriteSheetIncludedCollection(bpy.types.PropertyGroup):
    collection: bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection,
        update=update_collection_name
    )
    collection_name: bpy.props.StringProperty(
        name="Collection Name",
        default=""
    )

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
    use_camera_override: bpy.props.BoolProperty(
        name="Use Camera Override",
        default=False,
        update=on_clip_settings_change
    )
    included_collections: bpy.props.CollectionProperty(
        type=SpriteSheetIncludedCollection
    )
    use_collection_override: bpy.props.BoolProperty(
        name="Use Collection Override",
        default=False,
        update=update_use_collection_override
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
    export_png_sequence: bpy.props.BoolProperty(
        name="Export PNG Sequence",
        description="Also export individual PNG frames",
        default=False
    )
    # Legacy compatibility fields (output_folder and sheet_name)
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


def update_workspace_default_camera(self, context):
    for clip in self.clips:
        clip.cache_dirty = True


class SpriteSheetWorkspace(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Workspace Name",
        default="Workspace"
    )
    default_camera: bpy.props.PointerProperty(
        name="Default Camera",
        type=bpy.types.Object,
        poll=poll_camera,
        update=update_workspace_default_camera
    )
    default_collections: bpy.props.CollectionProperty(
        type=SpriteSheetIncludedCollection
    )
    clips: bpy.props.CollectionProperty(
        type=SpriteSheetClip
    )
    active_clip_index: bpy.props.IntProperty(
        default=0
    )
    export_settings: bpy.props.PointerProperty(
        type=SpriteSheetExportSettings
    )


classes = (
    SpriteSheetFrameItem,
    SpriteSheetIncludedCollection,
    SpriteSheetClip,
    SpriteSheetExportSettings,
    SpriteSheetWorkspace,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Legacy registrations
    bpy.types.Scene.spritesheet_clips = bpy.props.CollectionProperty(type=SpriteSheetClip)
    bpy.types.Scene.active_clip_index = bpy.props.IntProperty(default=0)
    bpy.types.Scene.spritesheet_export = bpy.props.PointerProperty(type=SpriteSheetExportSettings)
    
    # Workspace V1 registrations
    bpy.types.Scene.spritesheet_workspaces = bpy.props.CollectionProperty(type=SpriteSheetWorkspace)
    bpy.types.Scene.active_workspace_index = bpy.props.IntProperty(default=0)

def unregister():
    # Workspace V1 deregistrations
    del bpy.types.Scene.active_workspace_index
    del bpy.types.Scene.spritesheet_workspaces
    
    # Legacy deregistrations
    del bpy.types.Scene.spritesheet_export
    del bpy.types.Scene.active_clip_index
    del bpy.types.Scene.spritesheet_clips
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
