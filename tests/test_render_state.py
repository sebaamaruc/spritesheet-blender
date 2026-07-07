import unittest
from types import SimpleNamespace

from spritesheet_frame_selector.core.render_state import (
    render_file_path,
    render_output_file_name,
    selected_frame_numbers,
)
from spritesheet_frame_selector.core.validation import validate_active_clip_render_context


class FakeCollection(list):
    def __init__(self, factory):
        super().__init__()
        self._factory = factory

    def add(self):
        item = self._factory()
        self.append(item)
        return item


def fake_frame(frame_number=1, selected=True):
    return SimpleNamespace(
        frame_number=frame_number,
        selected=selected,
        preview_path=f"/tmp/preview_{frame_number}.png",
    )


def fake_collection_item():
    return SimpleNamespace(
        collection=SimpleNamespace(name="Collection", name_full="Collection"),
        collection_name="Collection",
    )


def fake_export_settings():
    return SimpleNamespace(
        frame_width=64,
        frame_height=64,
        columns=8,
        transparent=True,
        output_folder="/tmp/out",
        sheet_name="spritesheet",
    )


def fake_clip():
    return SimpleNamespace(
        id="clip-id",
        name="Visible Clip Name",
        frame_start=1,
        frame_end=3,
        frame_step=1,
        use_camera_override=False,
        camera=None,
        use_collection_override=False,
        included_collections=FakeCollection(fake_collection_item),
        frames=[fake_frame(1, True), fake_frame(2, False), fake_frame(3, True)],
    )


def fake_workspace():
    collections = FakeCollection(fake_collection_item)
    collections.add()
    return SimpleNamespace(
        id="workspace-id",
        name="Visible Workspace Name",
        default_camera=SimpleNamespace(name="Camera", name_full="Camera"),
        default_collections=collections,
        export_settings=fake_export_settings(),
    )


class RenderStateTests(unittest.TestCase):
    def test_selected_frame_numbers_use_persistent_order(self):
        self.assertEqual(selected_frame_numbers(fake_clip()), [1, 3])

    def test_render_output_paths_use_output_index_not_frame_number(self):
        self.assertEqual(
            render_output_file_name(7, "Run Cycle"),
            "Run_Cycle_frame_007.png",
        )
        self.assertEqual(
            render_output_file_name(1, "Run Cycle"),
            "Run_Cycle_frame_001.png",
        )
        self.assertEqual(
            render_file_path("/tmp/render", 2, "Run Cycle"),
            "/tmp/render/Run_Cycle_frame_002.png",
        )

    def test_validation_requires_camera_collections_and_selected_frames(self):
        workspace = fake_workspace()
        clip = fake_clip()
        self.assertEqual(validate_active_clip_render_context(workspace, clip), [])

        workspace.default_camera = None
        self.assertIn("Missing effective camera", validate_active_clip_render_context(workspace, clip))

        workspace.default_camera = SimpleNamespace(name="Camera")
        clip.frames = [fake_frame(1, False)]
        self.assertIn("No selected frames to render", validate_active_clip_render_context(workspace, clip))

    def test_validation_rejects_multiple_workspace_default_collections(self):
        workspace = fake_workspace()
        workspace.default_collections.add()
        clip = fake_clip()

        self.assertIn(
            "Workspace supports only one default collection",
            validate_active_clip_render_context(workspace, clip),
        )

if __name__ == "__main__":
    unittest.main()
