"""Minimal workspace-root status panel."""

from __future__ import annotations

import bpy

from ..core.cache import cache_warning, count_preview_references
from ..core.frame_math import frame_count
from ..core.selection import selected_frame_count
from ..core.workspace_state import (
    clip_at_active_index_or_none,
    effective_preview_mode,
    missing_effective_collection_names,
    preview_context_warnings,
    workspace_at_active_index_or_none,
)
from ..playback.sequence import playback_ready_summary


class SPRITESHEET_MT_preview_size(bpy.types.Menu):
    bl_label = "Preview Size"
    bl_idname = "SPRITESHEET_MT_preview_size"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        for size in (32, 64, 128, 256):
            op = layout.operator("spritesheet.preview_size_preset", text=f"{size}px")
            op.size = size


class SPRITESHEET_PT_main(bpy.types.Panel):
    bl_label = "SpriteSheet"
    bl_idname = "SPRITESHEET_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SpriteSheet"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        state = getattr(context.scene, "spritesheet_state", None)

        layout.label(text="SpriteSheet Frame Selector V2")
        if state is None:
            layout.label(text="Scene state unavailable", icon="ERROR")
            return

        row = layout.row()
        row.template_list(
            "SPRITESHEET_UL_workspaces",
            "",
            state,
            "workspaces",
            state,
            "active_workspace_index",
            rows=2,
        )
        controls = row.column(align=True)
        controls.operator("spritesheet.workspace_add", text="", icon="ADD")
        controls.operator("spritesheet.workspace_remove", text="", icon="REMOVE")
        controls.operator("spritesheet.workspace_duplicate", text="", icon="DUPLICATE")
        controls.separator()
        controls.operator("spritesheet.workspace_move", text="", icon="TRIA_UP").direction = "UP"
        controls.operator("spritesheet.workspace_move", text="", icon="TRIA_DOWN").direction = "DOWN"

        workspace = workspace_at_active_index_or_none(state)
        if workspace is None:
            layout.label(text="No active workspace")
            return

        layout.separator()
        workspace_box = layout.box()
        workspace_box.label(text="Workspace")
        workspace_box.prop(workspace, "name", text="Name")
        workspace_box.prop(workspace, "default_camera")

        collections_box = workspace_box.box()
        collections_box.label(text="Default Collection")
        if len(workspace.default_collections) == 0:
            collections_box.operator(
                "spritesheet.workspace_default_collection_add",
                text="Set Default Collection",
                icon="ADD",
            )
        else:
            item = workspace.default_collections[0]
            collection_row = collections_box.row(align=True)
            collection_row.prop(item, "collection", text="")
            if item.collection is None and item.collection_name:
                collection_row.label(text=f"Missing: {item.collection_name}", icon="ERROR")
            op = collection_row.operator(
                "spritesheet.workspace_default_collection_remove",
                text="",
                icon="REMOVE",
            )
            op.index = 0
            if len(workspace.default_collections) > 1:
                collections_box.label(text="Only one default collection is supported", icon="ERROR")

        layout.separator()
        row = layout.row()
        row.template_list(
            "SPRITESHEET_UL_clips",
            "",
            workspace,
            "clips",
            workspace,
            "active_clip_index",
            rows=4,
        )
        controls = row.column(align=True)
        controls.operator("spritesheet.clip_add", text="", icon="ADD")
        controls.operator("spritesheet.clip_remove", text="", icon="REMOVE")
        controls.operator("spritesheet.clip_duplicate", text="", icon="DUPLICATE")
        controls.separator()
        controls.operator("spritesheet.clip_move", text="", icon="TRIA_UP").direction = "UP"
        controls.operator("spritesheet.clip_move", text="", icon="TRIA_DOWN").direction = "DOWN"

        clip = clip_at_active_index_or_none(workspace)
        if clip is None:
            layout.label(text="No active clip")
            return

        clip_box = layout.box()
        clip_box.label(text="Clip")
        clip_box.prop(clip, "name")
        clip_box.prop(clip, "include_in_export", text="Include in Export")
        row = clip_box.row(align=True)
        row.prop(clip, "frame_start", text="Start")
        row.prop(clip, "frame_end", text="End")
        row.prop(clip, "frame_step", text="Step")
        clip_box.prop(clip, "fps")

        clip_box.prop(clip, "use_camera_override")
        if clip.use_camera_override:
            clip_box.prop(clip, "camera")

        clip_box.prop(clip, "use_collection_override")
        if clip.use_collection_override:
            for index, item in enumerate(clip.included_collections):
                collection_row = clip_box.row(align=True)
                collection_row.prop(item, "collection", text="")
                if item.collection is None and item.collection_name:
                    collection_row.label(text=f"Missing: {item.collection_name}", icon="ERROR")
                op = collection_row.operator(
                    "spritesheet.clip_included_collection_remove",
                    text="",
                    icon="REMOVE",
                )
                op.index = index
            clip_box.operator(
                "spritesheet.clip_included_collection_add",
                text="Add Clip Collection",
                icon="ADD",
            )

        try:
            expected_frames = frame_count(clip.frame_start, clip.frame_end, clip.frame_step)
        except ValueError:
            expected_frames = 0
        preview_box = layout.box()
        preview_refs = count_preview_references(clip)
        preview_box.label(text="Preview")
        preview_box.prop(clip, "preview_mode", text="Mode")
        preview_box.menu("SPRITESHEET_MT_preview_size", text=f"Preview Size: {clip.preview_size}px")
        row = preview_box.row(align=True)
        row.operator("spritesheet.preview_generate", text="Generate Preview", icon="RENDER_STILL")
        row.operator("spritesheet.preview_clear_cache", text="Clear Cache", icon="TRASH")

        status_box = layout.box()
        status_box.label(text="Preview Status")
        for warning in preview_context_warnings(workspace, clip):
            status_box.label(text=warning, icon="ERROR")
        for name in missing_effective_collection_names(workspace, clip):
            status_box.label(text=f"Missing collection: {name}", icon="ERROR")
        cache_note = cache_warning(clip)
        if cache_note:
            status_box.label(text=cache_note, icon="INFO")
        if clip.last_preview_note:
            status_box.label(text=clip.last_preview_note)
        status_box.label(text=f"Mode: {effective_preview_mode(workspace, clip)}")
        status_box.label(text=f"Previews: {preview_refs}")

        playback_summary = playback_ready_summary(clip)
        selector_box = layout.box()
        selector_box.label(text="Selector")
        selector_row = selector_box.row(align=True)
        selector_row.operator("spritesheet.visual_selector_open", icon="IMAGE_DATA")
        selector_box.label(text=f"Selected: {selected_frame_count(clip)} / Playable: {playback_summary.ready}")
        if playback_summary.selected == 0:
            selector_box.label(text="No selected frames to play", icon="INFO")
        elif playback_summary.missing_preview:
            selector_box.label(
                text=f"Selected frames missing previews: {playback_summary.missing_preview}",
                icon="ERROR",
            )

        layout.label(text=f"Expected Frames: {expected_frames}")
        layout.label(text=f"Stored Frames: {len(clip.frames)}")
        layout.label(text=f"Selected Frames: {selected_frame_count(clip)}")

        export_box = layout.box()
        export_box.label(text="Export Settings")
        export_box.prop(workspace.export_settings, "sheet_name", text="Sheet")
        export_box.prop(workspace.export_settings, "output_folder", text="Folder")
        row = export_box.row(align=True)
        row.prop(workspace.export_settings, "frame_width", text="W")
        row.prop(workspace.export_settings, "frame_height", text="H")
        row.prop(workspace.export_settings, "columns", text="Columns")
        export_box.label(text=_sheet_resolution_label(workspace.export_settings, _included_selected_count(workspace)))
        export_box.prop(workspace.export_settings, "export_png_sequence", text="Export Individual Frames")
        if workspace.export_settings.export_png_sequence:
            export_box.label(
                text=f"Frames Folder: {_individual_frames_folder_name(workspace.export_settings)}"
            )
        export_box.operator("spritesheet.export_spritesheet", icon="EXPORT")
        if workspace.last_export_note:
            export_box.label(text=workspace.last_export_note)


def _sheet_resolution_label(
    export_settings: bpy.types.PropertyGroup,
    selected_frames: int,
) -> str:
    columns = max(1, export_settings.columns)
    rows = 0 if selected_frames == 0 else (selected_frames + columns - 1) // columns
    width = export_settings.frame_width * columns
    height = export_settings.frame_height * rows
    return f"Sheet Size: {width} x {height}"


def _included_selected_count(workspace: bpy.types.PropertyGroup) -> int:
    return sum(
        selected_frame_count(clip)
        for clip in workspace.clips
        if getattr(clip, "include_in_export", False)
    )


def _individual_frames_folder_name(export_settings: bpy.types.PropertyGroup) -> str:
    sheet_name = export_settings.sheet_name.strip() or "spritesheet"
    return f"{sheet_name}_frames"
