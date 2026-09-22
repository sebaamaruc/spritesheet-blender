"""Viewport-dependent checks that need a real Blender window.

Run with a GUI Blender (no ``-b``); results are written to the path given after
``--`` and Blender quits by itself:

    blender --factory-startup --python tests/blender/gui_checks.py -- /tmp/out.json
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import bpy

import it_common  # noqa: F401  (puts the repo root on sys.path)
import spritesheet_frame_selector as addon

RESULTS: list[dict] = []
OUTPUT_PATH = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "/tmp/gui_checks.json"


def check(name):
    def decorator(func):
        def wrapper():
            try:
                detail = func()
                RESULTS.append({"name": name, "status": "PASS", "detail": detail or ""})
            except Exception as exc:
                RESULTS.append({
                    "name": name,
                    "status": "FAIL",
                    "detail": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(),
                })
        return wrapper
    return decorator


def window():
    """Stable window handle; ``bpy.context.window`` is None inside timers."""
    return bpy.context.window_manager.windows[0]


def find_view3d():
    for area in window().screen.areas:
        if area.type == "VIEW_3D":
            return area
    return None


def viewport_override():
    area = find_view3d()
    assert area is not None, "no VIEW_3D area in the startup screen"
    region = next(r for r in area.regions if r.type == "WINDOW")
    return bpy.context.temp_override(
        window=window(), screen=window().screen, area=area, region=region
    )


_SCENE_COUNTER = [0]


def build_scene():
    """Fresh workspace/clip data.

    Deliberately avoids ``read_factory_settings``: reloading the file inside a
    timer callback invalidates the window context for every later check.
    """
    from it_common import (
        link_camera, make_camera, make_collection_with_cube,
        new_clip, new_workspace, set_workspace_defaults, use_fast_render_engine,
    )
    from spritesheet_frame_selector.core.frame_math import frame_numbers
    from spritesheet_frame_selector.core.frame_sync import sync_clip_frames

    _SCENE_COUNTER[0] += 1
    tag = _SCENE_COUNTER[0]

    state = bpy.context.scene.spritesheet_state
    state.workspaces.clear()
    state.active_workspace_index = -1

    use_fast_render_engine()
    camera = make_camera(f"Cam{tag}")
    collection, _obj = make_collection_with_cube(f"Props{tag}", f"Cube{tag}")
    link_camera(camera, collection)
    workspace = new_workspace(f"W{tag}")
    set_workspace_defaults(workspace, camera, collection)
    clip = new_clip()
    clip.frame_start = 1
    clip.frame_end = 3
    sync_clip_frames(clip, frame_numbers(1, 3, 1))
    return workspace, clip


@check("sidebar panel is present in the VIEW_3D UI region")
def check_panel_present():
    area = find_view3d()
    assert area is not None, "no VIEW_3D area in the default startup screen"
    from spritesheet_frame_selector.ui.panels import SPRITESHEET_PT_main

    assert SPRITESHEET_PT_main.bl_space_type == "VIEW_3D"
    assert SPRITESHEET_PT_main.bl_region_type == "UI"
    assert hasattr(bpy.types, "SPRITESHEET_PT_main"), "panel class not registered"
    regions = [r.type for r in area.regions]
    assert "UI" in regions, f"no UI region: {regions}"
    return f"category={SPRITESHEET_PT_main.bl_category}, regions={regions}"


@check("SOLID viewport preview renders real thumbnails")
def check_solid_preview():
    _workspace, clip = build_scene()
    clip.preview_mode = "SOLID"
    with viewport_override():
        result = bpy.ops.spritesheet.preview_generate()
    assert result == {"FINISHED"}, f"{result} note={clip.last_preview_note!r}"
    missing = [f.frame_number for f in clip.frames if not os.path.isfile(f.preview_path)]
    assert not missing, f"missing preview files for frames {missing}"
    sizes = [os.path.getsize(f.preview_path) for f in clip.frames]
    assert all(s > 0 for s in sizes), f"empty preview files: {sizes}"
    return f"note={clip.last_preview_note!r} sizes={sizes}"


@check("MATERIAL viewport preview renders real thumbnails (EEVEE)")
def check_material_preview():
    _workspace, clip = build_scene()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    clip.preview_mode = "MATERIAL"
    with viewport_override():
        result = bpy.ops.spritesheet.preview_generate()
    assert result == {"FINISHED"}, f"{result} note={clip.last_preview_note!r}"
    assert all(os.path.isfile(f.preview_path) for f in clip.frames)
    return f"note={clip.last_preview_note!r}"


@check("MATERIAL preview under Workbench reports an actionable message")
def check_material_preview_workbench():
    _workspace, clip = build_scene()
    bpy.context.scene.render.engine = "BLENDER_WORKBENCH"
    clip.preview_mode = "MATERIAL"
    area = find_view3d()
    space = area.spaces.active
    space.shading.type = "SOLID"
    with viewport_override():
        result = bpy.ops.spritesheet.preview_generate()
    note = clip.last_preview_note
    assert result == {"CANCELLED"}, result
    assert "bpy_struct" not in note, f"raw RNA error leaked to the user: {note!r}"
    assert "render engine" in note, f"unhelpful note: {note!r}"
    assert space.shading.type == "SOLID", f"shading not restored: {space.shading.type}"
    return f"note={note!r}"


@check("viewport shading / camera view / overlays are restored after preview")
def check_viewport_state_restored():
    _workspace, clip = build_scene()
    clip.preview_mode = "SOLID"
    area = find_view3d()
    space = area.spaces.active
    space.shading.type = "WIREFRAME"
    space.overlay.show_overlays = True
    space.region_3d.view_perspective = "PERSP"

    with viewport_override():
        bpy.ops.spritesheet.preview_generate()

    assert space.shading.type == "WIREFRAME", f"shading not restored: {space.shading.type}"
    assert space.overlay.show_overlays is True, "overlays not restored"
    assert space.region_3d.view_perspective == "PERSP", \
        f"view_perspective not restored: {space.region_3d.view_perspective}"
    return "shading, overlays and view_perspective restored"


@check("preview thumbnails honour the effective camera framing")
def check_preview_uses_camera():
    workspace, clip = build_scene()
    clip.preview_mode = "SOLID"
    area = find_view3d()
    # Point the viewport somewhere unrelated; camera view must still be forced.
    area.spaces.active.region_3d.view_perspective = "PERSP"
    with viewport_override():
        bpy.ops.spritesheet.preview_generate()

    image = bpy.data.images.load(clip.frames[0].preview_path, check_existing=False)
    try:
        width, height = int(image.size[0]), int(image.size[1])
        assert (width, height) == (clip.preview_size, clip.preview_size), \
            f"preview size {width}x{height} != {clip.preview_size}"
        pixels = [0.0] * len(image.pixels)
        image.pixels.foreach_get(pixels)
        opaque = sum(1 for a in pixels[3::4] if a > 0.01)
        assert opaque > 0, "preview is fully transparent - subject not framed by the camera"
        transparent = sum(1 for a in pixels[3::4] if a <= 0.01)
        return f"{width}x{height}, opaque={opaque}, transparent={transparent} (workspace={workspace.name})"
    finally:
        bpy.data.images.remove(image)


@check("visual selector modal opens, installs a draw handler and closes cleanly")
def check_selector_modal():
    from spritesheet_frame_selector.ui import visual_selector as vs

    _workspace, clip = build_scene()
    clip.preview_mode = "RENDERED"
    with viewport_override():
        bpy.ops.spritesheet.preview_generate()
        result = bpy.ops.spritesheet.visual_selector_open("INVOKE_DEFAULT")

    assert result == {"RUNNING_MODAL"}, result
    assert vs._session is not None, "no selector session"
    assert vs._session.draw_handler is not None, "draw handler was not installed"

    vs.cleanup_visual_selector_resources()
    assert vs._session is None, "session not released"
    return "modal opened and released"


@check("selector draw pass runs against a live GPU context")
def check_selector_draw():
    from spritesheet_frame_selector.ui import visual_selector as vs

    _workspace, clip = build_scene()
    clip.preview_mode = "RENDERED"
    area = find_view3d()
    with viewport_override():
        bpy.ops.spritesheet.preview_generate()
        bpy.ops.spritesheet.visual_selector_open("INVOKE_DEFAULT")

    errors: list[str] = []
    session = vs._session

    original_draw = session._draw

    def instrumented():
        try:
            original_draw()
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")

    session._draw = instrumented
    area.tag_redraw()
    # Force Blender to process a redraw so the POST_PIXEL handler actually runs.
    with viewport_override():
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=2)

    drew = session.frame_cells or session.button_cells
    vs.cleanup_visual_selector_resources()

    assert not errors, errors[0]
    assert drew, "draw pass produced no hit-test cells"
    return f"frame_cells={len(session.frame_cells)}, button_cells={len(session.button_cells)}"


@check("export end-to-end from a GUI session")
def check_export_gui():
    workspace, clip = build_scene()
    tmp = tempfile.mkdtemp(prefix="sfs_gui_export_")
    workspace.export_settings.output_folder = tmp
    workspace.export_settings.sheet_name = "gui_sheet"
    workspace.export_settings.frame_width = 16
    workspace.export_settings.frame_height = 16
    workspace.export_settings.columns = 2
    result = bpy.ops.spritesheet.export_spritesheet()
    assert result == {"FINISHED"}, f"{result} note={workspace.last_export_note!r}"
    png = os.path.join(tmp, "gui_sheet.png")
    assert os.path.isfile(png), "sheet png missing"
    assert os.path.isfile(os.path.join(tmp, "gui_sheet.json")), "metadata json missing"
    del clip
    return f"wrote {os.path.getsize(png)} bytes"



@check("addon state is covered by Blender's undo stack")
def check_undo_covers_state():
    """Verify memfile undo restores workspaces, clips and selection.

    Operator-driven undo pushes do not fire when operators are called from a
    timer callback, so steps are pushed explicitly here. This proves the state
    is undo-*coverable*; that each operator pushes its own step in interactive
    use rests on bl_options={'REGISTER','UNDO'} and needs a manual Ctrl+Z check.
    """
    build_scene()
    with viewport_override():
        state = bpy.context.scene.spritesheet_state
        state.workspaces.clear()
        bpy.ops.ed.undo_push(message="s0 empty")
        bpy.ops.spritesheet.workspace_add()
        bpy.ops.ed.undo_push(message="s1 workspace")
        bpy.ops.spritesheet.clip_add()
        bpy.ops.ed.undo_push(message="s2 clip")
        bpy.ops.spritesheet.frame_deselect_all()
        bpy.ops.ed.undo_push(message="s3 deselect")

        def snapshot():
            st = bpy.context.scene.spritesheet_state
            return (
                len(st.workspaces),
                sum(len(w.clips) for w in st.workspaces),
                sum(1 for w in st.workspaces for c in w.clips for f in c.frames if f.selected),
            )

        assert snapshot() == (1, 1, 0), f"unexpected pre-undo state {snapshot()}"
        bpy.ops.ed.undo()
        after_first = snapshot()
        assert after_first == (1, 1, 20), f"selection not restored: {after_first}"
        bpy.ops.ed.undo()
        after_second = snapshot()
        assert after_second == (1, 0, 0), f"clip not rolled back: {after_second}"
        bpy.ops.ed.undo()
        after_third = snapshot()
        assert after_third == (0, 0, 0), f"workspace not rolled back: {after_third}"
    return f"{after_first} -> {after_second} -> {after_third}"


CHECKS = [
    check_panel_present,
    check_solid_preview,
    check_material_preview,
    check_material_preview_workbench,
    check_viewport_state_restored,
    check_preview_uses_camera,
    check_selector_modal,
    check_selector_draw,
    check_export_gui,
    check_undo_covers_state,
]


def run_all():
    addon.register()
    try:
        for item in CHECKS:
            item()
    finally:
        try:
            addon.unregister()
        except Exception as exc:
            RESULTS.append({"name": "unregister", "status": "FAIL", "detail": repr(exc)})

    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(RESULTS, handle, indent=2)
    print("GUI_CHECKS_WRITTEN", OUTPUT_PATH)
    sys.stdout.flush()
    # quit_blender() from a timer callback crashes (null context); results are
    # already on disk, so exit the process directly.
    os._exit(0)


bpy.app.timers.register(run_all, first_interval=1.5)
