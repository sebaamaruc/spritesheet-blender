import sys
import unittest
from types import SimpleNamespace

if "bpy" not in sys.modules:
    sys.modules["bpy"] = SimpleNamespace(
        app=SimpleNamespace(background=False),
        data=SimpleNamespace(images=SimpleNamespace(remove=lambda _image: None)),
        path=SimpleNamespace(abspath=lambda path: path),
        ops=SimpleNamespace(
            spritesheet=SimpleNamespace(),
        ),
        types=SimpleNamespace(
            Context=object,
            Event=object,
            Image=object,
            Operator=object,
            SpaceView3D=SimpleNamespace(
                draw_handler_add=lambda *_args, **_kwargs: object(),
                draw_handler_remove=lambda *_args, **_kwargs: None,
            ),
        ),
    )
else:
    bpy_stub = sys.modules["bpy"]
    if not hasattr(bpy_stub, "path"):
        bpy_stub.path = SimpleNamespace(abspath=lambda path: path)
    if not hasattr(bpy_stub, "data"):
        bpy_stub.data = SimpleNamespace(images=SimpleNamespace(remove=lambda _image: None))

from spritesheet_frame_selector.ui.visual_selector import (
    VisualSelectorSession,
    clamp_grid_offset,
    _load_preview_image,
    scroll_direction_from_event,
    scrolled_grid_offset,
    visible_frame_window,
)


class VisualSelectorScrollTests(unittest.TestCase):
    def test_clamp_grid_offset_keeps_offset_in_valid_window(self):
        self.assertEqual(clamp_grid_offset(-5, 20, 6), 0)
        self.assertEqual(clamp_grid_offset(4, 20, 6), 4)
        self.assertEqual(clamp_grid_offset(99, 20, 6), 14)
        self.assertEqual(clamp_grid_offset(10, 4, 6), 0)

    def test_scrolled_grid_offset_moves_by_rows(self):
        self.assertEqual(scrolled_grid_offset(0, 1, 20, 6, 3), 3)
        self.assertEqual(scrolled_grid_offset(3, -1, 20, 6, 3), 0)
        self.assertEqual(scrolled_grid_offset(12, 1, 20, 6, 3), 14)

    def test_scroll_direction_supports_wheel_and_trackpad(self):
        self.assertEqual(scroll_direction_from_event(SimpleNamespace(type="WHEELDOWNMOUSE")), 1)
        self.assertEqual(scroll_direction_from_event(SimpleNamespace(type="WHEELUPMOUSE")), -1)
        self.assertEqual(
            scroll_direction_from_event(SimpleNamespace(type="TRACKPADPAN", mouse_y=10, mouse_prev_y=20)),
            1,
        )
        self.assertEqual(
            scroll_direction_from_event(SimpleNamespace(type="TRACKPADPAN", mouse_y=20, mouse_prev_y=10)),
            -1,
        )
        self.assertEqual(scroll_direction_from_event(SimpleNamespace(type="TRACKPADPAN")), 0)

    def test_visible_frame_window_returns_visible_and_real_indices(self):
        frames = [SimpleNamespace(frame_number=number) for number in range(10)]

        visible = visible_frame_window(frames, 4, 3)

        self.assertEqual(
            [(visible_index, real_index, frame.frame_number) for visible_index, real_index, frame in visible],
            [(0, 4, 4), (1, 5, 5), (2, 6, 6)],
        )

    def test_load_preview_image_reloads_only_on_first_session_cache(self):
        class FakeImage:
            def __init__(self):
                self.reloads = 0

            def reload(self):
                self.reloads += 1

        image = FakeImage()
        loads = []
        bpy_module = sys.modules["bpy"]
        original_images = bpy_module.data.images
        bpy_module.data.images = SimpleNamespace(
            load=lambda path, check_existing=True: loads.append((path, check_existing)) or image,
            remove=lambda _image: None,
        )
        try:
            session = SimpleNamespace(images={})

            first = _load_preview_image(session, "/tmp/frame.png")
            second = _load_preview_image(session, "/tmp/frame.png")
        finally:
            bpy_module.data.images = original_images

        self.assertIs(first, image)
        self.assertIs(second, image)
        self.assertEqual(loads, [("/tmp/frame.png", True)])
        self.assertEqual(image.reloads, 1)

    def test_visual_selector_session_resets_images_when_cache_key_changes(self):
        session = VisualSelectorSession.__new__(VisualSelectorSession)
        session.image_cache_key = ""
        session.images = {"old": SimpleNamespace(users=1)}
        session.checkerboard_layout = object()

        session._sync_image_cache_key("cache-a")
        self.assertIn("old", session.images)

        session._sync_image_cache_key("cache-b")

        self.assertEqual(session.image_cache_key, "cache-b")
        self.assertEqual(session.images, {})
        self.assertIsNone(session.checkerboard_layout)


if __name__ == "__main__":
    unittest.main()
