import unittest
from types import SimpleNamespace

from spritesheet_frame_selector.core.workspace_state import (
    active_clip_or_none,
    active_workspace_or_none,
    clip_at_active_index_or_none,
    clamp_active_clip_index,
    clamp_active_workspace_index,
    duplicate_clip_data,
    duplicate_workspace_data,
    move_item,
    next_item_name,
    unique_item_name_at_index,
    workspace_at_active_index_or_none,
)


class FakeCollection(list):
    def __init__(self, factory):
        super().__init__()
        self._factory = factory

    def add(self):
        item = self._factory()
        self.append(item)
        return item

    def remove(self, index):
        del self[index]

    def move(self, from_index, to_index):
        item = self.pop(from_index)
        self.insert(to_index, item)


def fake_collection_item():
    return SimpleNamespace(collection=None, collection_name="")


def fake_frame():
    return SimpleNamespace(
        frame_number=1,
        selected=True,
        preview_path="preview.png",
    )


def fake_export_settings():
    return SimpleNamespace(
        frame_width=64,
        frame_height=64,
        columns=8,
        padding=0,
        margin=0,
        transparent=True,
        output_folder="",
        sheet_name="spritesheet",
        export_png_sequence=False,
        png_sequence_folder="",
    )


def fake_clip():
    return SimpleNamespace(
        id="clip-source",
        name="Clip",
        include_in_export=True,
        frame_start=1,
        frame_end=20,
        frame_step=1,
        fps=12,
        use_camera_override=False,
        camera=None,
        use_collection_override=False,
        included_collections=FakeCollection(fake_collection_item),
        preview_size=64,
        frames=FakeCollection(fake_frame),
        active_frame_index=-1,
        cache_key="old-cache-key",
        cache_folder="/tmp/old-cache",
        cache_dirty=False,
        last_preview_note="old note",
    )


def fake_workspace():
    return SimpleNamespace(
        id="workspace-source",
        name="Workspace",
        default_camera=None,
        default_collections=FakeCollection(fake_collection_item),
        clips=FakeCollection(fake_clip),
        active_clip_index=-1,
        export_settings=fake_export_settings(),
    )


class WorkspaceStateTests(unittest.TestCase):
    def test_next_item_name_uses_incremental_suffix(self):
        self.assertEqual(next_item_name([], "Workspace"), "Workspace")
        self.assertEqual(next_item_name(["Workspace"], "Workspace"), "Workspace 2")
        self.assertEqual(
            next_item_name(["Workspace", "Workspace 2"], "Workspace"),
            "Workspace 3",
        )

    def test_unique_item_name_at_index_ignores_current_item(self):
        collection = FakeCollection(fake_clip)
        first = collection.add()
        first.name = "Run"
        second = collection.add()
        second.name = "Idle"
        third = collection.add()
        third.name = "Run 2"

        self.assertEqual(unique_item_name_at_index(collection, 1, "Run", fallback="Clip"), "Run 3")
        self.assertEqual(unique_item_name_at_index(collection, 0, "Run", fallback="Clip"), "Run")
        self.assertEqual(unique_item_name_at_index(collection, 1, "", fallback="Clip"), "Clip")

    def test_empty_workspace_index_clamps_to_minus_one(self):
        state = SimpleNamespace(workspaces=[], active_workspace_index=4)

        self.assertEqual(clamp_active_workspace_index(state), -1)
        self.assertIsNone(active_workspace_or_none(state))

    def test_out_of_range_workspace_index_clamps_to_last_workspace(self):
        state = SimpleNamespace(
            workspaces=[fake_workspace(), fake_workspace()],
            active_workspace_index=7,
        )

        self.assertEqual(clamp_active_workspace_index(state), 1)
        self.assertIs(active_workspace_or_none(state), state.workspaces[1])

    def test_workspace_at_active_index_is_read_only(self):
        state = SimpleNamespace(
            workspaces=[fake_workspace(), fake_workspace()],
            active_workspace_index=7,
        )

        self.assertIsNone(workspace_at_active_index_or_none(state))
        self.assertEqual(state.active_workspace_index, 7)

    def test_empty_clip_index_clamps_to_minus_one(self):
        workspace = fake_workspace()
        workspace.active_clip_index = 5

        self.assertEqual(clamp_active_clip_index(workspace), -1)
        self.assertIsNone(active_clip_or_none(workspace))

    def test_out_of_range_clip_index_clamps_to_last_clip(self):
        workspace = fake_workspace()
        workspace.clips.add()
        workspace.clips.add()
        workspace.active_clip_index = 9

        self.assertEqual(clamp_active_clip_index(workspace), 1)
        self.assertIs(active_clip_or_none(workspace), workspace.clips[1])

    def test_clip_at_active_index_is_read_only(self):
        workspace = fake_workspace()
        workspace.clips.add()
        workspace.active_clip_index = 4

        self.assertIsNone(clip_at_active_index_or_none(workspace))
        self.assertEqual(workspace.active_clip_index, 4)

    def test_duplicate_clip_copies_authored_data_and_clears_cache(self):
        source = fake_clip()
        source.name = "Run"
        source.frame_start = 3
        source.frame_end = 9
        source.frame_step = 2
        source.frames.add()
        source.frames[0].frame_number = 3
        source.frames[0].selected = False
        source.frames[0].preview_path = "cached-3.png"
        target = fake_clip()

        duplicate_clip_data(source, target, new_id="clip-new")

        self.assertEqual(target.id, "clip-new")
        self.assertEqual(target.name, "Run")
        self.assertEqual(target.frame_start, 3)
        self.assertEqual(target.frame_end, 9)
        self.assertEqual(target.frame_step, 2)
        self.assertEqual(len(target.frames), 1)
        self.assertFalse(target.frames[0].selected)
        self.assertEqual(target.frames[0].preview_path, "")
        self.assertEqual(target.cache_key, "")
        self.assertEqual(target.cache_folder, "")
        self.assertTrue(target.cache_dirty)
        self.assertEqual(target.last_preview_note, "")

    def test_duplicate_workspace_assigns_new_ids_and_cleans_clip_cache(self):
        source = fake_workspace()
        source.name = "Combat"
        source.clips.add()
        source.clips[0].name = "Idle"
        source.clips[0].cache_key = "stale"
        source.clips[0].cache_folder = "/tmp/stale"
        source.active_clip_index = 0
        target = fake_workspace()

        duplicate_workspace_data(
            source,
            target,
            new_workspace_id="workspace-new",
            clip_id_factory=lambda: "clip-new",
        )

        self.assertEqual(target.id, "workspace-new")
        self.assertEqual(target.name, "Combat")
        self.assertEqual(target.active_clip_index, 0)
        self.assertEqual(len(target.clips), 1)
        self.assertEqual(target.clips[0].id, "clip-new")
        self.assertEqual(target.clips[0].name, "Idle")
        self.assertEqual(target.clips[0].cache_key, "")
        self.assertEqual(target.clips[0].cache_folder, "")
        self.assertTrue(target.clips[0].cache_dirty)

    def test_move_item_returns_final_index_and_reorders(self):
        collection = FakeCollection(fake_clip)
        first = collection.add()
        first.name = "A"
        second = collection.add()
        second.name = "B"
        third = collection.add()
        third.name = "C"

        final_index = move_item(collection, 2, 0)

        self.assertEqual(final_index, 0)
        self.assertEqual([item.name for item in collection], ["C", "A", "B"])


if __name__ == "__main__":
    unittest.main()
