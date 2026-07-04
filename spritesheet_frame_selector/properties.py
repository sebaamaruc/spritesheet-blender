"""Persistent workspace-root data model for SpriteSheet Frame Selector V2."""

from __future__ import annotations

import bpy

from .core.workspace_state import unique_item_name_at_index


SCHEMA_VERSION = 2


PREVIEW_MODE_ITEMS = (
    ("SOLID", "Solid", "Fast solid viewport preview"),
    ("MATERIAL", "Material", "Material/texture viewport preview"),
    ("RENDERED", "Rendered", "Rendered preview with scene lighting"),
)

SELECTOR_MODE_ITEMS = (
    ("EDIT", "Edit", "Click frames to include or exclude them"),
    ("PLAY", "Play", "Click frames to inspect/play without changing selection"),
)

_RENAMING_CLIP = False


def camera_object_poll(self: bpy.types.PropertyGroup, obj: bpy.types.Object) -> bool:
    return obj is None or getattr(obj, "type", None) == "CAMERA"


def update_collection_name(self: bpy.types.PropertyGroup, context: bpy.types.Context) -> None:
    if self.collection is not None:
        self.collection_name = self.collection.name
    _mark_collection_owner_dirty(self, context)


def update_clip_cache_dirty(self: bpy.types.PropertyGroup, context: bpy.types.Context) -> None:
    self.cache_dirty = True
    if hasattr(self, "render_dirty"):
        self.render_dirty = True


def update_clip_name_unique(self: bpy.types.PropertyGroup, context: bpy.types.Context) -> None:
    global _RENAMING_CLIP
    if _RENAMING_CLIP:
        return

    scene = getattr(context, "scene", None)
    state = getattr(scene, "spritesheet_state", None) if scene is not None else None
    if state is None:
        return

    for workspace in state.workspaces:
        for index, clip in enumerate(workspace.clips):
            if clip != self:
                continue
            unique_name = unique_item_name_at_index(
                workspace.clips,
                index,
                self.name,
                fallback="Clip",
            )
            if unique_name != self.name:
                _RENAMING_CLIP = True
                try:
                    self.name = unique_name
                finally:
                    _RENAMING_CLIP = False
            return


def update_workspace_defaults_dirty(self: bpy.types.PropertyGroup, context: bpy.types.Context) -> None:
    for clip in self.clips:
        clip.cache_dirty = True


def _mark_collection_owner_dirty(
    collection_item: bpy.types.PropertyGroup,
    context: bpy.types.Context,
) -> None:
    scene = getattr(context, "scene", None)
    state = getattr(scene, "spritesheet_state", None) if scene is not None else None
    if state is None:
        return

    for workspace in state.workspaces:
        if any(item == collection_item for item in workspace.default_collections):
            for clip in workspace.clips:
                clip.cache_dirty = True
            return
        for clip in workspace.clips:
            if any(item == collection_item for item in clip.included_collections):
                clip.cache_dirty = True
                return


class SpriteSheetIncludedCollection(bpy.types.PropertyGroup):
    collection: bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection,
        update=update_collection_name,
    )
    collection_name: bpy.props.StringProperty(
        name="Collection Name",
        default="",
    )


class SpriteSheetFrameItem(bpy.types.PropertyGroup):
    frame_number: bpy.props.IntProperty(
        name="Frame Number",
        default=1,
        min=0,
    )
    selected: bpy.props.BoolProperty(
        name="Selected",
        default=True,
    )
    preview_path: bpy.props.StringProperty(
        name="Preview Path",
        subtype="FILE_PATH",
        default="",
    )
    render_path: bpy.props.StringProperty(
        name="Render Path",
        subtype="FILE_PATH",
        default="",
    )
    original_index: bpy.props.IntProperty(
        name="Original Index",
        default=-1,
        min=-1,
    )


class SpriteSheetExportSettings(bpy.types.PropertyGroup):
    frame_width: bpy.props.IntProperty(
        name="Frame Width",
        default=64,
        min=1,
    )
    frame_height: bpy.props.IntProperty(
        name="Frame Height",
        default=64,
        min=1,
    )
    columns: bpy.props.IntProperty(
        name="Columns",
        default=8,
        min=1,
    )
    padding: bpy.props.IntProperty(
        name="Padding",
        default=0,
        min=0,
    )
    margin: bpy.props.IntProperty(
        name="Margin",
        default=0,
        min=0,
    )
    transparent: bpy.props.BoolProperty(
        name="Transparent",
        default=True,
    )
    output_folder: bpy.props.StringProperty(
        name="Output Folder",
        subtype="DIR_PATH",
        default="",
    )
    sheet_name: bpy.props.StringProperty(
        name="Sheet Name",
        default="spritesheet",
    )
    export_png_sequence: bpy.props.BoolProperty(
        name="Export Individual Frames",
        default=False,
    )
    png_sequence_folder: bpy.props.StringProperty(
        name="Last Individual Frames Folder",
        subtype="DIR_PATH",
        default="",
    )


class SpriteSheetClip(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty(
        name="ID",
        default="",
    )
    name: bpy.props.StringProperty(
        name="Name",
        default="Clip",
        update=update_clip_name_unique,
    )
    include_in_export: bpy.props.BoolProperty(
        name="Include in Export",
        default=True,
    )
    frame_start: bpy.props.IntProperty(
        name="Start",
        default=1,
        update=update_clip_cache_dirty,
    )
    frame_end: bpy.props.IntProperty(
        name="End",
        default=20,
        update=update_clip_cache_dirty,
    )
    frame_step: bpy.props.IntProperty(
        name="Step",
        default=1,
        min=1,
        update=update_clip_cache_dirty,
    )
    fps: bpy.props.IntProperty(
        name="FPS",
        default=12,
        min=1,
    )
    use_camera_override: bpy.props.BoolProperty(
        name="Use Camera Override",
        default=False,
        update=update_clip_cache_dirty,
    )
    camera: bpy.props.PointerProperty(
        name="Camera",
        type=bpy.types.Object,
        poll=camera_object_poll,
        update=update_clip_cache_dirty,
    )
    use_collection_override: bpy.props.BoolProperty(
        name="Use Collection Override",
        default=False,
        update=update_clip_cache_dirty,
    )
    included_collections: bpy.props.CollectionProperty(type=SpriteSheetIncludedCollection)
    preview_mode: bpy.props.EnumProperty(
        name="Preview Mode",
        items=PREVIEW_MODE_ITEMS,
        default="SOLID",
        update=update_clip_cache_dirty,
    )
    preview_size: bpy.props.IntProperty(
        name="Preview Size",
        default=64,
        min=32,
        max=256,
        update=update_clip_cache_dirty,
    )
    frames: bpy.props.CollectionProperty(type=SpriteSheetFrameItem)
    active_frame_index: bpy.props.IntProperty(
        name="Active Frame Index",
        default=-1,
        min=-1,
    )
    cache_key: bpy.props.StringProperty(
        name="Cache Key",
        default="",
    )
    cache_folder: bpy.props.StringProperty(
        name="Cache Folder",
        subtype="DIR_PATH",
        default="",
    )
    cache_dirty: bpy.props.BoolProperty(
        name="Cache Dirty",
        default=True,
    )
    last_preview_note: bpy.props.StringProperty(
        name="Last Preview Note",
        default="",
    )
    render_key: bpy.props.StringProperty(
        name="Render Key",
        default="",
    )
    render_folder: bpy.props.StringProperty(
        name="Render Folder",
        subtype="DIR_PATH",
        default="",
    )
    render_dirty: bpy.props.BoolProperty(
        name="Render Dirty",
        default=True,
    )
    last_render_note: bpy.props.StringProperty(
        name="Last Render Note",
        default="",
    )


class SpriteSheetWorkspace(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty(
        name="ID",
        default="",
    )
    name: bpy.props.StringProperty(
        name="Name",
        default="Workspace",
    )
    default_camera: bpy.props.PointerProperty(
        name="Default Camera",
        type=bpy.types.Object,
        poll=camera_object_poll,
        update=update_workspace_defaults_dirty,
    )
    default_collections: bpy.props.CollectionProperty(type=SpriteSheetIncludedCollection)
    selector_mode: bpy.props.EnumProperty(
        name="Selector Mode",
        items=SELECTOR_MODE_ITEMS,
        default="EDIT",
    )
    clips: bpy.props.CollectionProperty(type=SpriteSheetClip)
    active_clip_index: bpy.props.IntProperty(
        name="Active Clip Index",
        default=-1,
        min=-1,
    )
    export_settings: bpy.props.PointerProperty(type=SpriteSheetExportSettings)
    last_export_note: bpy.props.StringProperty(
        name="Last Export Note",
        default="",
    )
    last_export_png: bpy.props.StringProperty(
        name="Last Export PNG",
        subtype="FILE_PATH",
        default="",
    )
    last_export_json: bpy.props.StringProperty(
        name="Last Export JSON",
        subtype="FILE_PATH",
        default="",
    )


class SpriteSheetSceneState(bpy.types.PropertyGroup):
    schema_version: bpy.props.IntProperty(
        name="Schema Version",
        default=SCHEMA_VERSION,
        min=1,
    )
    workspaces: bpy.props.CollectionProperty(type=SpriteSheetWorkspace)
    active_workspace_index: bpy.props.IntProperty(
        name="Active Workspace Index",
        default=-1,
        min=-1,
    )
