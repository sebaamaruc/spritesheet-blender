import unittest
from types import SimpleNamespace

from spritesheet_frame_selector.core.render_state import (
    build_render_key,
    clear_render_state,
    count_render_references,
    render_file_name,
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
        render_path=f"/tmp/render_{frame_number}.png",
        original_index=-1,
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
        render_key="render-key",
        render_folder="/tmp/render-folder",
        render_dirty=False,
        last_render_note="note",
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

    def test_render_key_uses_ids_settings_and_context_not_visible_names(self):
        workspace = fake_workspace()
        clip = fake_clip()
        collections = [workspace.default_collections[0].collection]

        original = build_render_key(
            workspace,
            clip,
            workspace.default_camera,
            collections,
            workspace.export_settings,
            [1, 3],
        )
        workspace.name = "Renamed Workspace"
        clip.name = "Renamed Clip"

        self.assertEqual(
            build_render_key(
                workspace,
                clip,
                workspace.default_camera,
                collections,
                workspace.export_settings,
                [1, 3],
            ),
            original,
        )

        workspace.export_settings.frame_width = 128
        self.assertNotEqual(
            build_render_key(
                workspace,
                clip,
                workspace.default_camera,
                collections,
                workspace.export_settings,
                [1, 3],
            ),
            original,
        )

    def test_render_key_changes_with_selected_frames(self):
        workspace = fake_workspace()
        clip = fake_clip()
        collections = [workspace.default_collections[0].collection]

        first = build_render_key(
            workspace,
            clip,
            workspace.default_camera,
            collections,
            workspace.export_settings,
            [1, 3],
        )
        second = build_render_key(
            workspace,
            clip,
            workspace.default_camera,
            collections,
            workspace.export_settings,
            [1],
        )

        self.assertNotEqual(first, second)

    def test_render_file_names_are_stable_and_sheet_prefixed(self):
        self.assertEqual(render_file_name(7), "frame_007.png")
        self.assertEqual(
            render_output_file_name(7, "Run Cycle"),
            "Run_Cycle_frame_007.png",
        )
        self.assertEqual(
            render_output_file_name(1, "Run Cycle"),
            "Run_Cycle_frame_001.png",
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

    def test_clear_render_state_keeps_selection_and_preview_paths(self):
        clip = fake_clip()
        preview_paths = [frame.preview_path for frame in clip.frames]

        clear_render_state(clip)

        self.assertEqual(count_render_references(clip), 0)
        self.assertEqual([frame.preview_path for frame in clip.frames], preview_paths)
        self.assertEqual([frame.selected for frame in clip.frames], [True, False, True])
        self.assertEqual(clip.render_key, "")
        self.assertEqual(clip.render_folder, "")
        self.assertTrue(clip.render_dirty)
        self.assertEqual(clip.last_render_note, "")


if __name__ == "__main__":
    unittest.main()
