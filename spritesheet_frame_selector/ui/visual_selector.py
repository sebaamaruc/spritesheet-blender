"""Modal visual selector surface for cached frame previews."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

import bpy

from ..playback.controller import active_session_matches
from ..playback.controller import active_session_summary
from ..playback.controller import current_frame_number
from ..playback.controller import seek_playback_frame
from ..playback.controller import stop_playback


SELECTED_COLOR = (0.05, 0.55, 1.0, 1.0)
CURRENT_COLOR = (1.0, 0.68, 0.05, 1.0)
PANEL_COLOR = (0.06, 0.06, 0.06, 1.0)
PREVIEW_CHECKER_DARK = (0.24, 0.27, 0.36, 1.0)
PREVIEW_CHECKER_LIGHT = (0.31, 0.34, 0.44, 1.0)
FRAME_BORDER_BG_COLOR = (0.015, 0.017, 0.022, 1.0)
TEXT_COLOR = (0.92, 0.92, 0.92, 1.0)
MUTED_COLOR = (0.45, 0.45, 0.45, 1.0)
SURFACE_SAFE_LEFT = 78
SURFACE_SAFE_TOP = 88
SURFACE_SAFE_RIGHT = 36
SURFACE_SAFE_BOTTOM = 18
SURFACE_RIGHT_UI_GUTTER = 34


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    def contains(self, x: float, y: float) -> bool:
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height


@dataclass
class FrameCell:
    index: int
    rect: Rect


@dataclass
class ButtonCell:
    action: str
    rect: Rect


@dataclass(frozen=True)
class CheckerboardLayout:
    key: tuple[Any, ...]
    base_batch: Any
    light_batch: Any


class VisualSelectorSession:
    """Runtime state for the modal selector."""

    def __init__(
        self,
        operator: bpy.types.Operator,
        context: bpy.types.Context,
        workspace_id: str,
        clip_id: str,
    ) -> None:
        self.operator = operator
        self.workspace_id = workspace_id
        self.clip_id = clip_id
        self.area = context.area
        self.region = context.region
        self.draw_handler: Any | None = None
        self.frame_cells: list[FrameCell] = []
        self.button_cells: list[ButtonCell] = []
        self.images: dict[str, bpy.types.Image] = {}
        self.checkerboard_layout: CheckerboardLayout | None = None
        self.rect_shader: Any | None = None
        self.grid_offset = 0
        self.grid_columns = 1
        self.grid_max_visible = 1

    def open(self) -> None:
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            self.draw,
            (),
            "WINDOW",
            "POST_PIXEL",
        )

    def close(self) -> None:
        if self.draw_handler is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
            except (ReferenceError, ValueError):
                pass
            self.draw_handler = None
        stop_playback()
        self._release_images()
        self.checkerboard_layout = None
        self.rect_shader = None
        _tag_redraw(self.area)

    def draw(self) -> None:
        try:
            self._draw()
        except ReferenceError:
            cleanup_visual_selector_resources()

    def _draw(self) -> None:
        try:
            import blf
            import gpu
            from gpu_extras.batch import batch_for_shader
        except Exception:
            return

        workspace, clip = active_workspace_clip_readonly(bpy.context)
        if workspace is None or clip is None:
            return
        if workspace.id != self.workspace_id or clip.id != self.clip_id:
            return

        region_width = self.region.width if self.region is not None else 1200
        region_height = self.region.height if self.region is not None else 800
        panel = _selector_panel_rect(region_width, region_height, self.area)
        margin = 12
        header_h = 34
        controls_w = min(220, max(170, panel.width * 0.28))

        self.frame_cells = []
        self.button_cells = []

        _draw_rect(gpu, batch_for_shader, panel, PANEL_COLOR)
        _draw_outline(gpu, batch_for_shader, panel, (0.18, 0.2, 0.24, 1.0), 1)
        _draw_text(blf, panel.x + margin, panel.y + panel.height - 24, f"{workspace.name} / {clip.name}", 15)
        _draw_text(
            blf,
            panel.x + panel.width - min(310, panel.width * 0.48),
            panel.y + panel.height - 24,
            f"Mode: {workspace.selector_mode}   Preview: {effective_preview_label(workspace, clip)}",
            12,
        )

        available_viewer_h = max(150, panel.height - header_h - margin * 3 - 96)
        viewer_h = max(150, min(260, available_viewer_h, panel.height * 0.42))
        viewer_w = max(180, panel.width - controls_w - margin * 3)
        viewer_y = panel.y + panel.height - header_h - viewer_h - margin
        viewer = Rect(panel.x + margin, viewer_y, viewer_w, viewer_h)
        controls = Rect(viewer.x + viewer.width + margin, viewer.y, controls_w, viewer_h)
        _draw_rect(gpu, batch_for_shader, controls, (0.03, 0.03, 0.03, 1.0))

        current_number = _current_display_frame(workspace, clip)
        current_frame = _frame_by_number(clip, current_number) if current_number is not None else None
        preview_display_rect = _preview_display_rect(self, current_frame, viewer, float(clip.preview_size))

        grid_top = viewer.y - margin
        grid_bottom = panel.y + margin
        grid_height = max(0, grid_top - grid_bottom)
        if grid_height < 48:
            try:
                _draw_batched_checkerboard(gpu, batch_for_shader, self, preview_display_rect, [])
            except Exception:
                _draw_preview_fallback_backgrounds(gpu, batch_for_shader, preview_display_rect, [])
            if current_frame is not None:
                _draw_preview_image(gpu, batch_for_shader, self, current_frame.preview_path, viewer)
                _draw_text(blf, viewer.x + 12, viewer.y + 12, f"Frame {current_frame.frame_number}", 18)
            else:
                _draw_text(blf, viewer.x + 20, viewer.y + viewer.height / 2, "No frame selected", 18, MUTED_COLOR)
            self._draw_controls(blf, gpu, batch_for_shader, controls, workspace)
            _draw_text(blf, panel.x + margin, panel.y + margin, "Viewport too small for frame grid", 11, MUTED_COLOR)
            return
        cell_size = max(48, min(float(clip.preview_size), 128.0, grid_height))
        gap = 10
        columns = max(1, int((panel.width - margin * 2 + gap) // (cell_size + gap)))
        rows = max(1, int((grid_height + gap) // (cell_size + gap)))
        max_visible = max(1, columns * rows)
        self.grid_columns = columns
        self.grid_max_visible = max_visible
        self.grid_offset = clamp_grid_offset(self.grid_offset, len(clip.frames), max_visible)
        x = panel.x + margin
        y = grid_top - cell_size
        session_matches = active_session_matches(workspace.id, clip.id)
        active_frame_number = current_frame_number() if session_matches else current_number

        visible_entries = visible_frame_window(clip.frames, self.grid_offset, max_visible)
        frame_rects: list[Rect] = []
        for visible_index, _real_index, _frame in visible_entries:
            rect = Rect(x, y, cell_size, cell_size)
            frame_rects.append(rect)
            x += cell_size + gap
            if (visible_index + 1) % columns == 0:
                x = panel.x + margin
                y -= cell_size + gap

        for rect in frame_rects:
            _draw_rect(gpu, batch_for_shader, rect, FRAME_BORDER_BG_COLOR)

        try:
            _draw_batched_checkerboard(
                gpu,
                batch_for_shader,
                self,
                preview_display_rect,
                frame_rects,
            )
        except Exception:
            _draw_preview_fallback_backgrounds(gpu, batch_for_shader, preview_display_rect, frame_rects)

        if current_frame is not None:
            _draw_preview_image(gpu, batch_for_shader, self, current_frame.preview_path, viewer)
            _draw_text(blf, viewer.x + 12, viewer.y + 12, f"Frame {current_frame.frame_number}", 18)
        else:
            _draw_text(blf, viewer.x + 20, viewer.y + viewer.height / 2, "No frame selected", 18, MUTED_COLOR)

        self._draw_controls(blf, gpu, batch_for_shader, controls, workspace)

        for visible_index, real_index, frame in visible_entries:
            rect = frame_rects[visible_index]
            self.frame_cells.append(FrameCell(real_index, rect))
            _draw_preview_image(gpu, batch_for_shader, self, frame.preview_path, rect)
            _draw_text(blf, rect.x + 6, rect.y + 6, str(frame.frame_number), 11)
            if frame.selected:
                _draw_outline(gpu, batch_for_shader, rect, SELECTED_COLOR, 3)
            if frame.frame_number == active_frame_number:
                _draw_outline(gpu, batch_for_shader, _inset_rect(rect, 4), CURRENT_COLOR, 3)
        if len(clip.frames) > max_visible:
            first = self.grid_offset + 1
            last = min(len(clip.frames), self.grid_offset + max_visible)
            _draw_text(
                blf,
                panel.x + margin,
                panel.y + 6,
                f"Showing {first}-{last} / {len(clip.frames)} frames",
                11,
                MUTED_COLOR,
            )

    def _draw_controls(self, blf: Any, gpu: Any, batch_for_shader: Any, rect: Rect, workspace: Any) -> None:
        y = rect.y + rect.height - 34
        _draw_text(blf, rect.x + 12, y + 8, "Selector", 14)
        left = rect.x + 12
        usable_width = max(120, rect.width - 24)
        gap = 8
        half = (usable_width - gap) / 2
        third = (usable_width - gap * 2) / 3
        y -= 32
        self._button(blf, gpu, batch_for_shader, "mode_edit", "Edit", left, y, half, workspace.selector_mode == "EDIT")
        self._button(blf, gpu, batch_for_shader, "mode_play", "Play", left + half + gap, y, half, workspace.selector_mode == "PLAY")
        y -= 34
        self._button(blf, gpu, batch_for_shader, "play", "Play", left, y, third, False)
        self._button(blf, gpu, batch_for_shader, "pause", "Pause", left + third + gap, y, third, False)
        self._button(blf, gpu, batch_for_shader, "stop", "Stop", left + (third + gap) * 2, y, third, False)
        y -= 34
        self._button(blf, gpu, batch_for_shader, "select_all", "All", left, y, half, False)
        self._button(blf, gpu, batch_for_shader, "deselect_all", "None", left + half + gap, y, half, False)
        y -= 34
        self._button(blf, gpu, batch_for_shader, "invert", "Invert", left, y, half, False)
        self._button(blf, gpu, batch_for_shader, "every_n", "Every 2", left + half + gap, y, half, False)
        y -= 34
        self._button(blf, gpu, batch_for_shader, "close", "Close", left, y, usable_width, False)
        session = active_session_summary()
        _draw_text(blf, rect.x + 12, rect.y + 12, f"Status: {session['status']}", 12, MUTED_COLOR)

    def _button(
        self,
        blf: Any,
        gpu: Any,
        batch_for_shader: Any,
        action: str,
        label: str,
        x: float,
        y: float,
        width: float,
        active: bool,
    ) -> None:
        rect = Rect(x, y, width, 24)
        color = (0.12, 0.18, 0.24, 1.0) if active else (0.11, 0.11, 0.11, 1.0)
        _draw_rect(gpu, batch_for_shader, rect, color)
        _draw_outline(gpu, batch_for_shader, rect, SELECTED_COLOR if active else (0.25, 0.25, 0.25, 1.0), 1)
        _draw_text(blf, x + 8, y + 7, label, 11)
        self.button_cells.append(ButtonCell(action, rect))

    def _release_images(self) -> None:
        for image in self.images.values():
            try:
                if image.users == 0:
                    bpy.data.images.remove(image)
            except ReferenceError:
                pass
        self.images.clear()


_session: VisualSelectorSession | None = None


def open_visual_selector(
    operator: bpy.types.Operator,
    context: bpy.types.Context,
    workspace_id: str,
    clip_id: str,
) -> bool:
    if bpy.app.background or context.area is None or context.area.type != "VIEW_3D":
        operator.report({"WARNING"}, "Visual selector requires a 3D Viewport UI context")
        return False
    cleanup_visual_selector_resources()
    global _session
    _session = VisualSelectorSession(operator, context, workspace_id, clip_id)
    _session.open()
    context.window_manager.modal_handler_add(operator)
    _tag_redraw(context.area)
    return True


def cleanup_visual_selector_resources() -> None:
    global _session
    if _session is not None:
        _session.close()
        _session = None


def handle_visual_selector_event(context: bpy.types.Context, event: bpy.types.Event) -> set[str] | None:
    if _session is None:
        return {"CANCELLED"}
    if not _session_matches_context(context):
        cleanup_visual_selector_resources()
        return {"CANCELLED"}
    if event.type in {"ESC", "RIGHTMOUSE"} and event.value == "PRESS":
        cleanup_visual_selector_resources()
        return {"CANCELLED"}
    if _event_has_modifier(event):
        return {"RUNNING_MODAL", "PASS_THROUGH"}
    if event.type == "SPACE" and event.value == "PRESS":
        _handle_space_playback(context)
        _tag_redraw(context.area)
        return {"RUNNING_MODAL"}
    if event.type == "TAB" and event.value == "PRESS":
        _toggle_selector_mode(context)
        _tag_redraw(context.area)
        return {"RUNNING_MODAL"}
    if event.type == "LEFT_ARROW" and event.value == "PRESS" and getattr(event, "shift", False):
        _return_to_first_frame(context)
        _tag_redraw(context.area)
        return {"RUNNING_MODAL"}
    if event.type == "LEFTMOUSE" and event.value == "PRESS":
        if not _event_inside_panel(event):
            return {"RUNNING_MODAL", "PASS_THROUGH"}
        _handle_click(context, event.mouse_region_x, event.mouse_region_y)
        _tag_redraw(context.area)
        return {"RUNNING_MODAL"}
    if event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE", "TRACKPADPAN"}:
        if not _event_inside_panel(event):
            return {"RUNNING_MODAL", "PASS_THROUGH"}
        _scroll_frame_grid(event)
        _tag_redraw(context.area)
        return {"RUNNING_MODAL"}
    if event.type == "TIMER":
        _tag_redraw(context.area)
        return {"RUNNING_MODAL"}
    if _event_should_pass_through(event):
        return {"RUNNING_MODAL", "PASS_THROUGH"}
    return None


def active_workspace_clip_readonly(context: bpy.types.Context) -> tuple[Any | None, Any | None]:
    scene = getattr(context, "scene", None)
    state = getattr(scene, "spritesheet_state", None) if scene is not None else None
    if state is None:
        return None, None
    workspace_index = getattr(state, "active_workspace_index", -1)
    if workspace_index < 0 or workspace_index >= len(state.workspaces):
        return None, None
    workspace = state.workspaces[workspace_index]
    clip_index = getattr(workspace, "active_clip_index", -1)
    if clip_index < 0 or clip_index >= len(workspace.clips):
        return workspace, None
    return workspace, workspace.clips[clip_index]


def effective_preview_label(workspace: Any, clip: Any) -> str:
    return getattr(clip, "preview_mode", "SOLID")


def _session_matches_context(context: bpy.types.Context) -> bool:
    if _session is None:
        return False
    workspace, clip = active_workspace_clip_readonly(context)
    return (
        workspace is not None
        and clip is not None
        and workspace.id == _session.workspace_id
        and clip.id == _session.clip_id
    )


def _event_inside_panel(event: bpy.types.Event) -> bool:
    if _session is None:
        return False
    region_width = _session.region.width if _session.region is not None else 1200
    region_height = _session.region.height if _session.region is not None else 800
    panel = _selector_panel_rect(region_width, region_height, _session.area)
    return panel.contains(event.mouse_region_x, event.mouse_region_y)


def _event_should_pass_through(event: bpy.types.Event) -> bool:
    if _event_has_modifier(event):
        return True
    if event.type in {
        "MIDDLEMOUSE",
        "WHEELUPMOUSE",
        "WHEELDOWNMOUSE",
        "WHEELINMOUSE",
        "WHEELOUTMOUSE",
        "TRACKPADPAN",
        "TRACKPADZOOM",
        "NDOF_MOTION",
    }:
        return True
    return False


def _event_has_modifier(event: bpy.types.Event) -> bool:
    return bool(getattr(event, "alt", False) or getattr(event, "ctrl", False) or getattr(event, "oskey", False))


def clamp_grid_offset(offset: int, total_frames: int, max_visible: int) -> int:
    max_start = max(0, total_frames - max(1, max_visible))
    return max(0, min(int(offset), max_start))


def scrolled_grid_offset(offset: int, direction: int, total_frames: int, max_visible: int, columns: int) -> int:
    step = max(1, columns)
    if direction > 0:
        offset += step
    elif direction < 0:
        offset -= step
    return clamp_grid_offset(offset, total_frames, max_visible)


def scroll_direction_from_event(event: Any) -> int:
    event_type = getattr(event, "type", "")
    if event_type == "WHEELDOWNMOUSE":
        return 1
    if event_type == "WHEELUPMOUSE":
        return -1
    if event_type == "TRACKPADPAN":
        current_y = getattr(event, "mouse_y", None)
        previous_y = getattr(event, "mouse_prev_y", None)
        if current_y is None or previous_y is None:
            return 0
        delta_y = current_y - previous_y
        if delta_y < 0:
            return 1
        if delta_y > 0:
            return -1
    return 0


def visible_frame_window(frames: Any, offset: int, max_visible: int) -> list[tuple[int, int, Any]]:
    clamped = clamp_grid_offset(offset, len(frames), max_visible)
    end = min(len(frames), clamped + max(1, max_visible))
    return [
        (visible_index, real_index, frames[real_index])
        for visible_index, real_index in enumerate(range(clamped, end))
    ]


def _scroll_frame_grid(event: bpy.types.Event) -> None:
    if _session is None:
        return
    _workspace, clip = active_workspace_clip_readonly(bpy.context)
    if clip is None:
        return
    direction = scroll_direction_from_event(event)
    if direction == 0:
        return
    _session.grid_offset = scrolled_grid_offset(
        _session.grid_offset,
        direction,
        len(clip.frames),
        _session.grid_max_visible,
        _session.grid_columns,
    )


def _handle_click(context: bpy.types.Context, x: float, y: float) -> None:
    if _session is None:
        return
    workspace, clip = active_workspace_clip_readonly(context)
    if workspace is None or clip is None:
        return

    for button in _session.button_cells:
        if button.rect.contains(x, y):
            _execute_button_action(context, workspace, clip, button.action)
            return

    for cell in _session.frame_cells:
        if cell.rect.contains(x, y):
            if cell.index < 0 or cell.index >= len(clip.frames):
                return
            if workspace.selector_mode == "EDIT":
                clip.frames[cell.index].selected = not clip.frames[cell.index].selected
            else:
                _set_play_mode_current_frame(workspace, clip, cell.index)
            return


def _execute_button_action(context: bpy.types.Context, workspace: Any, clip: Any, action: str) -> None:
    if action == "close":
        cleanup_visual_selector_resources()
    elif action == "mode_edit":
        workspace.selector_mode = "EDIT"
    elif action == "mode_play":
        workspace.selector_mode = "PLAY"
    elif action == "play":
        bpy.ops.spritesheet.playback_play()
    elif action == "pause":
        bpy.ops.spritesheet.playback_pause()
    elif action == "stop":
        bpy.ops.spritesheet.playback_stop()
    elif action == "select_all":
        bpy.ops.spritesheet.frame_select_all()
    elif action == "deselect_all":
        bpy.ops.spritesheet.frame_deselect_all()
    elif action == "invert":
        bpy.ops.spritesheet.frame_invert_selection()
    elif action == "every_n":
        bpy.ops.spritesheet.frame_select_every_n(n=2)


def _handle_space_playback(context: bpy.types.Context) -> None:
    session = active_session_summary()
    if session["status"] == "playing":
        bpy.ops.spritesheet.playback_pause()
        return
    if session["status"] == "paused":
        bpy.ops.spritesheet.playback_play()
        return
    workspace, clip = active_workspace_clip_readonly(context)
    if workspace is None or clip is None:
        return
    workspace.selector_mode = "PLAY"
    bpy.ops.spritesheet.playback_play()


def _toggle_selector_mode(context: bpy.types.Context) -> None:
    workspace, _clip = active_workspace_clip_readonly(context)
    if workspace is None:
        return
    workspace.selector_mode = "PLAY" if workspace.selector_mode == "EDIT" else "EDIT"


def _return_to_first_frame(context: bpy.types.Context) -> None:
    workspace, clip = active_workspace_clip_readonly(context)
    if workspace is None or clip is None or len(clip.frames) == 0:
        return
    stop_playback()
    clip.active_frame_index = 0


def _set_play_mode_current_frame(workspace: Any, clip: Any, index: int) -> None:
    if index < 0 or index >= len(clip.frames):
        return
    clip.active_frame_index = index
    frame_number = clip.frames[index].frame_number
    if not active_session_matches(workspace.id, clip.id):
        return
    if seek_playback_frame(frame_number):
        return
    stop_playback()


def _current_display_frame(workspace: Any, clip: Any) -> int | None:
    if active_session_matches(workspace.id, clip.id):
        return current_frame_number()
    active_index = getattr(clip, "active_frame_index", -1)
    if 0 <= active_index < len(clip.frames):
        return clip.frames[active_index].frame_number
    for frame in clip.frames:
        if getattr(frame, "selected", False):
            return frame.frame_number
    if len(clip.frames):
        return clip.frames[0].frame_number
    return None


def _frame_by_number(clip: Any, frame_number: int | None) -> Any | None:
    if frame_number is None:
        return None
    for frame in clip.frames:
        if frame.frame_number == frame_number:
            return frame
    return None


def _draw_preview_image(gpu: Any, batch_for_shader: Any, session: VisualSelectorSession, path: str, rect: Rect) -> None:
    if not path:
        return
    absolute_path = bpy.path.abspath(path)
    if not os.path.isfile(absolute_path):
        return
    try:
        image = session.images.get(absolute_path)
        if image is None:
            image = bpy.data.images.load(absolute_path, check_existing=True)
            session.images[absolute_path] = image
        texture = gpu.texture.from_image(image)
        draw_rect = _image_fit_rect(image, rect)
        shader = gpu.shader.from_builtin("IMAGE")
        vertices = (
            (draw_rect.x, draw_rect.y),
            (draw_rect.x + draw_rect.width, draw_rect.y),
            (draw_rect.x + draw_rect.width, draw_rect.y + draw_rect.height),
            (draw_rect.x, draw_rect.y + draw_rect.height),
        )
        tex_coords = ((0, 0), (1, 0), (1, 1), (0, 1))
        batch = batch_for_shader(shader, "TRI_FAN", {"pos": vertices, "texCoord": tex_coords})
        gpu.state.blend_set("ALPHA")
        shader.bind()
        shader.uniform_sampler("image", texture)
        batch.draw(shader)
        gpu.state.blend_set("NONE")
    except Exception:
        try:
            gpu.state.blend_set("NONE")
        except Exception:
            pass
        return


def _preview_display_rect(session: VisualSelectorSession, frame: Any | None, viewer: Rect, preview_size: float) -> Rect:
    if frame is not None:
        image = _cached_image_or_none(session, getattr(frame, "preview_path", ""))
        if image is not None:
            return _image_fit_rect(image, viewer)
    size = max(32.0, min(preview_size, viewer.height, viewer.width))
    return Rect(
        viewer.x + (viewer.width - size) / 2,
        viewer.y + (viewer.height - size) / 2,
        size,
        size,
    )


def _cached_image_or_none(session: VisualSelectorSession, path: str) -> Any | None:
    if not path:
        return None
    absolute_path = bpy.path.abspath(path)
    if not os.path.isfile(absolute_path):
        return None
    try:
        image = session.images.get(absolute_path)
        if image is None:
            image = bpy.data.images.load(absolute_path, check_existing=True)
            session.images[absolute_path] = image
        return image
    except Exception:
        return None


def _draw_rect(gpu: Any, batch_for_shader: Any, rect: Rect, color: tuple[float, float, float, float]) -> None:
    shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    vertices = (
        (rect.x, rect.y),
        (rect.x + rect.width, rect.y),
        (rect.x + rect.width, rect.y + rect.height),
        (rect.x, rect.y + rect.height),
    )
    batch = batch_for_shader(shader, "TRI_FAN", {"pos": vertices})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def _draw_batched_checkerboard(
    gpu: Any,
    batch_for_shader: Any,
    session: VisualSelectorSession,
    viewer: Rect,
    frame_rects: list[Rect],
) -> None:
    areas = [(viewer, 18)]
    areas.extend((_inset_rect(rect, 2), 16) for rect in frame_rects)
    key = _checkerboard_layout_key(areas)
    if session.checkerboard_layout is None or session.checkerboard_layout.key != key:
        session.checkerboard_layout = _build_checkerboard_layout(gpu, batch_for_shader, session, areas, key)

    layout = session.checkerboard_layout
    shader = session.rect_shader
    if layout is None or shader is None:
        raise RuntimeError("Checkerboard batch unavailable")
    _draw_colored_batch(shader, layout.base_batch, PREVIEW_CHECKER_DARK)
    _draw_colored_batch(shader, layout.light_batch, PREVIEW_CHECKER_LIGHT)


def _build_checkerboard_layout(
    gpu: Any,
    batch_for_shader: Any,
    session: VisualSelectorSession,
    areas: list[tuple[Rect, int]],
    key: tuple[Any, ...],
) -> CheckerboardLayout:
    if session.rect_shader is None:
        session.rect_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    shader = session.rect_shader
    base_vertices: list[tuple[float, float]] = []
    light_vertices: list[tuple[float, float]] = []
    for rect, cell_size in areas:
        _append_rect_triangles(base_vertices, rect)
        _append_checker_light_triangles(light_vertices, rect, cell_size)
    if not base_vertices:
        raise RuntimeError("Empty checkerboard layout")
    base_batch = batch_for_shader(shader, "TRIS", {"pos": base_vertices})
    light_batch = batch_for_shader(shader, "TRIS", {"pos": light_vertices}) if light_vertices else None
    return CheckerboardLayout(key=key, base_batch=base_batch, light_batch=light_batch)


def _append_checker_light_triangles(vertices: list[tuple[float, float]], rect: Rect, cell_size: int) -> None:
    cell = max(8, int(cell_size))
    columns = int(rect.width // cell) + 1
    rows = int(rect.height // cell) + 1
    for row in range(rows):
        y = rect.y + row * cell
        height = min(cell, rect.y + rect.height - y)
        if height <= 0:
            continue
        for column in range(columns):
            if (row + column) % 2 != 0:
                continue
            x = rect.x + column * cell
            width = min(cell, rect.x + rect.width - x)
            if width <= 0:
                continue
            _append_rect_triangles(vertices, Rect(x, y, width, height))


def _append_rect_triangles(vertices: list[tuple[float, float]], rect: Rect) -> None:
    x1 = rect.x
    y1 = rect.y
    x2 = rect.x + rect.width
    y2 = rect.y + rect.height
    vertices.extend(
        (
            (x1, y1),
            (x2, y1),
            (x2, y2),
            (x1, y1),
            (x2, y2),
            (x1, y2),
        )
    )


def _draw_colored_batch(
    shader: Any,
    batch: Any | None,
    color: tuple[float, float, float, float],
) -> None:
    if batch is None:
        return
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def _checkerboard_layout_key(areas: list[tuple[Rect, int]]) -> tuple[Any, ...]:
    return tuple(
        (
            round(rect.x, 2),
            round(rect.y, 2),
            round(rect.width, 2),
            round(rect.height, 2),
            int(cell_size),
        )
        for rect, cell_size in areas
    )


def _draw_preview_fallback_backgrounds(
    gpu: Any,
    batch_for_shader: Any,
    viewer: Rect,
    frame_rects: list[Rect],
) -> None:
    _draw_rect(gpu, batch_for_shader, viewer, PREVIEW_CHECKER_DARK)
    for rect in frame_rects:
        _draw_rect(gpu, batch_for_shader, _inset_rect(rect, 2), PREVIEW_CHECKER_DARK)


def _selector_panel_rect(region_width: float, region_height: float, area: Any) -> Rect:
    safe_left = SURFACE_SAFE_LEFT if region_width >= 520 else 12
    safe_top = SURFACE_SAFE_TOP if region_height >= 420 else 24
    right_overlay = _right_ui_overlay_width(area, region_width)
    available_width = max(260, region_width - safe_left - SURFACE_SAFE_RIGHT - right_overlay)
    available_height = max(220, region_height - safe_top - SURFACE_SAFE_BOTTOM)
    return Rect(safe_left, SURFACE_SAFE_BOTTOM, available_width, available_height)


def _right_ui_overlay_width(area: Any, region_width: float) -> float:
    if area is None:
        return 0
    overlay_width = 0
    for region in getattr(area, "regions", ()):
        if getattr(region, "type", None) != "UI":
            continue
        width = float(getattr(region, "width", 0) or 0)
        if width <= 1:
            continue
        x = getattr(region, "x", None)
        if x is not None:
            x = float(x)
            if 0 <= x < region_width:
                overlay_width = max(overlay_width, region_width - x + SURFACE_RIGHT_UI_GUTTER)
            continue
        overlay_width = max(overlay_width, min(width + SURFACE_RIGHT_UI_GUTTER, 460.0))
    return overlay_width


def _image_fit_rect(image: Any, rect: Rect) -> Rect:
    image_width = max(1, int(image.size[0])) if hasattr(image, "size") else 1
    image_height = max(1, int(image.size[1])) if hasattr(image, "size") else 1
    image_ratio = image_width / image_height
    rect_ratio = rect.width / max(1, rect.height)
    if image_ratio > rect_ratio:
        width = rect.width
        height = rect.width / image_ratio
    else:
        height = rect.height
        width = rect.height * image_ratio
    return Rect(
        rect.x + (rect.width - width) / 2,
        rect.y + (rect.height - height) / 2,
        width,
        height,
    )


def _draw_outline(
    gpu: Any,
    batch_for_shader: Any,
    rect: Rect,
    color: tuple[float, float, float, float],
    width: int,
) -> None:
    _draw_rect(gpu, batch_for_shader, Rect(rect.x, rect.y, rect.width, width), color)
    _draw_rect(gpu, batch_for_shader, Rect(rect.x, rect.y + rect.height - width, rect.width, width), color)
    _draw_rect(gpu, batch_for_shader, Rect(rect.x, rect.y, width, rect.height), color)
    _draw_rect(gpu, batch_for_shader, Rect(rect.x + rect.width - width, rect.y, width, rect.height), color)


def _draw_text(
    blf: Any,
    x: float,
    y: float,
    text: str,
    size: int,
    color: tuple[float, float, float, float] = TEXT_COLOR,
) -> None:
    font_id = 0
    blf.size(font_id, size)
    blf.color(font_id, *color)
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, text)


def _inset_rect(rect: Rect, amount: float) -> Rect:
    return Rect(rect.x + amount, rect.y + amount, max(1, rect.width - amount * 2), max(1, rect.height - amount * 2))


def _tag_redraw(area: Any) -> None:
    if area is not None:
        try:
            area.tag_redraw()
        except ReferenceError:
            pass
