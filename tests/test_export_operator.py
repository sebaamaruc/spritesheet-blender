import sys
import unittest
from types import SimpleNamespace

if "bpy" not in sys.modules:
    sys.modules["bpy"] = SimpleNamespace(
        app=SimpleNamespace(
            background=False,
            timers=SimpleNamespace(
                register=lambda *_args, **_kwargs: None,
                unregister=lambda *_args, **_kwargs: None,
                is_registered=lambda *_args, **_kwargs: False,
            ),
        ),
        ops=SimpleNamespace(
            render=SimpleNamespace(
                opengl=lambda **_kwargs: {"FINISHED"},
                render=lambda **_kwargs: {"FINISHED"},
            ),
        ),
        path=SimpleNamespace(abspath=lambda path: path),
        types=SimpleNamespace(
            Context=object,
            Operator=object,
            PropertyGroup=object,
        ),
    )
else:
    bpy_stub = sys.modules["bpy"]
    if not hasattr(bpy_stub, "path"):
        bpy_stub.path = SimpleNamespace(abspath=lambda path: path)
    if not hasattr(bpy_stub, "app"):
        bpy_stub.app = SimpleNamespace(
            background=False,
            timers=SimpleNamespace(
                register=lambda *_args, **_kwargs: None,
                unregister=lambda *_args, **_kwargs: None,
                is_registered=lambda *_args, **_kwargs: False,
            ),
        )
    if not hasattr(bpy_stub, "ops"):
        bpy_stub.ops = SimpleNamespace(
            render=SimpleNamespace(
                opengl=lambda **_kwargs: {"FINISHED"},
                render=lambda **_kwargs: {"FINISHED"},
            ),
        )
    if not hasattr(bpy_stub, "types"):
        bpy_stub.types = SimpleNamespace()
    if not hasattr(bpy_stub.types, "Operator"):
        bpy_stub.types.Operator = object
    if not hasattr(bpy_stub.types, "PropertyGroup"):
        bpy_stub.types.PropertyGroup = object

from spritesheet_frame_selector.operators.export import (
    _export_progress_total,
    _validate_prepared_individual_frame_limit,
)


class ExportOperatorTests(unittest.TestCase):
    def test_prepared_frame_limit_can_be_checked_before_render(self):
        prepared = [
            {"frame_numbers": list(range(500))},
            {"frame_numbers": list(range(500))},
        ]

        with self.assertRaisesRegex(ValueError, "up to 999 frames"):
            _validate_prepared_individual_frame_limit(prepared)

    def test_export_progress_total_counts_render_compose_sequence_and_json(self):
        prepared = [
            {"frame_numbers": [1, 2, 3]},
            {"frame_numbers": [4]},
        ]

        self.assertEqual(_export_progress_total(prepared, export_png_sequence=False), 6)
        self.assertEqual(_export_progress_total(prepared, export_png_sequence=True), 7)


if __name__ == "__main__":
    unittest.main()
