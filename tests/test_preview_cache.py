import unittest
import tempfile
import sys
from types import SimpleNamespace

if "bpy" not in sys.modules:
    sys.modules["bpy"] = SimpleNamespace(
        app=SimpleNamespace(background=False),
        ops=SimpleNamespace(
            render=SimpleNamespace(
                opengl=lambda **_kwargs: {"FINISHED"},
                render=lambda **_kwargs: {"FINISHED"},
            ),
        ),
        types=SimpleNamespace(
            Context=object,
            PropertyGroup=object,
            Object=object,
            Collection=object,
        ),
    )

from spritesheet_frame_selector.core.cache import build_preview_cache_key, clear_preview_state
from spritesheet_frame_selector.core.frame_sync import sync_clip_frames
from spritesheet_frame_selector.core.paths import preview_cache_folder, preview_cache_root
from spritesheet_frame_selector.core.workspace_state import (
    effective_camera_or_none,
    effective_collections,
    effective_preview_mode,
    default_collection_count_error,
    missing_effective_collection_names,
)
from spritesheet_frame_selector.preview import generator


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


def fake_frame():
    return SimpleNamespace(
        frame_number=0,
        selected=True,
        preview_path="",
        original_index=-1,
    )


def fake_clip():
    return SimpleNamespace(
        id="clip-id",
        name="Clip",
        frame_start=1,
        frame_end=3,
        frame_step=1,
        preview_size=64,
        use_camera_override=False,
        camera=None,
        use_collection_override=False,
        included_collections=FakeCollection(fake_collection_item),
        preview_mode="SOLID",
        frames=FakeCollection(fake_frame),
        active_frame_index=-1,
        cache_key="cache",
        cache_folder="/tmp/cache",
        cache_dirty=False,
        last_preview_note="note",
    )


def fake_workspace():
    return SimpleNamespace(
        id="workspace-id",
        name="Workspace",
        default_camera=SimpleNamespace(name="Default Camera"),
        default_collections=FakeCollection(fake_collection_item),
    )


def fake_collection_item():
    return SimpleNamespace(
        collection=SimpleNamespace(name="Collection", name_full="Collection"),
        collection_name="Collection",
    )


class FrameSyncTests(unittest.TestCase):
    def test_sync_frames_preserves_selection_and_removes_out_of_range(self):
        clip = fake_clip()
        sync_clip_frames(clip, [1, 2, 3])
        clip.frames[1].selected = False
        clip.frames[1].preview_path = "/tmp/frame_2.png"
        clip.frames[2].selected = False
        clip.active_frame_index = 2

        sync_clip_frames(clip, [2, 4])

        self.assertEqual([frame.frame_number for frame in clip.frames], [2, 4])
        self.assertFalse(clip.frames[0].selected)
        self.assertEqual(clip.frames[0].preview_path, "/tmp/frame_2.png")
        self.assertTrue(clip.frames[1].selected)
        self.assertEqual(clip.active_frame_index, -1)

    def test_sync_frames_empty_range_clears_frames_and_active_index(self):
        clip = fake_clip()
        sync_clip_frames(clip, [1, 2])
        clip.frames[0].selected = False
        clip.active_frame_index = 1

        sync_clip_frames(clip, [])

        self.assertEqual(len(clip.frames), 0)
        self.assertEqual(clip.active_frame_index, -1)


class WorkspacePreviewCacheTests(unittest.TestCase):
    def test_cache_key_uses_workspace_clip_camera_and_collections_not_names(self):
        workspace = fake_workspace()
        workspace.default_collections.add()
        clip = fake_clip()
        camera = workspace.default_camera
        collections = effective_collections(workspace, clip)

        original = build_preview_cache_key(workspace, clip, camera, collections)
        workspace.name = "Renamed Workspace"
        clip.name = "Renamed Clip"

        self.assertEqual(
            build_preview_cache_key(workspace, clip, camera, collections),
            original,
        )

        clip.preview_size = 128
        self.assertNotEqual(
            build_preview_cache_key(workspace, clip, camera, collections),
            original,
        )

    def test_cache_key_changes_with_preview_mode(self):
        workspace = fake_workspace()
        workspace.default_collections.add()
        clip = fake_clip()
        camera = workspace.default_camera
        collections = effective_collections(workspace, clip)

        solid = build_preview_cache_key(workspace, clip, camera, collections, "SOLID")
        rendered = build_preview_cache_key(workspace, clip, camera, collections, "RENDERED")

        self.assertNotEqual(solid, rendered)

    def test_effective_preview_mode_uses_clip_mode(self):
        workspace = fake_workspace()
        clip = fake_clip()

        clip.preview_mode = "RENDERED"

        self.assertEqual(effective_preview_mode(workspace, clip), "RENDERED")

    def test_cache_path_includes_workspace_and_clip_id(self):
        root = preview_cache_root("", temp_root=tempfile.gettempdir())
        path = preview_cache_folder(root, "workspace-id", "clip-id", "cache-key")

        self.assertIn("workspace-id", path)
        self.assertIn("clip-id", path)
        self.assertTrue(path.startswith(tempfile.gettempdir()))

    def test_effective_camera_and_collections_prefer_clip_overrides(self):
        workspace = fake_workspace()
        workspace.default_collections.add()
        clip = fake_clip()
        override_camera = SimpleNamespace(name="Override Camera")
        override_collection = SimpleNamespace(name="Override", name_full="Override")
        clip.use_camera_override = True
        clip.camera = override_camera
        clip.use_collection_override = True
        clip.included_collections.add()
        clip.included_collections[0].collection = override_collection
        clip.included_collections[0].collection_name = "Override"

        self.assertIs(effective_camera_or_none(workspace, clip), override_camera)
        self.assertEqual(effective_collections(workspace, clip), [override_collection])

    def test_missing_effective_collection_names_are_reported(self):
        workspace = fake_workspace()
        item = workspace.default_collections.add()
        item.collection = None
        item.collection_name = "Deleted Collection"

        self.assertEqual(
            missing_effective_collection_names(workspace, fake_clip()),
            ["Deleted Collection"],
        )

    def test_multiple_default_collections_are_rejected_without_clip_override(self):
        workspace = fake_workspace()
        workspace.default_collections.add()
        workspace.default_collections.add()
        clip = fake_clip()

        self.assertEqual(
            default_collection_count_error(workspace, clip),
            "Workspace supports only one default collection",
        )

        clip.use_collection_override = True
        self.assertEqual(default_collection_count_error(workspace, clip), "")

    def test_clear_preview_state_keeps_frames_and_selection(self):
        clip = fake_clip()
        sync_clip_frames(clip, [1, 2])
        clip.frames[0].selected = False
        clip.frames[0].preview_path = "/tmp/frame_1.png"

        clear_preview_state(clip)

        self.assertEqual(len(clip.frames), 2)
        self.assertFalse(clip.frames[0].selected)
        self.assertEqual(clip.frames[0].preview_path, "")
        self.assertTrue(clip.cache_dirty)


class PreviewViewportContextTests(unittest.TestCase):
    def test_find_view3d_context_prefers_active_area(self):
        view_area = fake_view3d_area()
        screen = SimpleNamespace(areas=[fake_area("IMAGE_EDITOR"), view_area])
        context = SimpleNamespace(area=view_area, window=SimpleNamespace(screen=screen))

        result = generator._find_view3d_render_context(context)

        self.assertIsNotNone(result)
        self.assertIs(result.area, view_area)
        self.assertEqual(result.region.type, "WINDOW")
        self.assertEqual(result.space.type, "VIEW_3D")

    def test_find_view3d_context_falls_back_to_screen_area(self):
        view_area = fake_view3d_area()
        screen = SimpleNamespace(areas=[fake_area("IMAGE_EDITOR"), view_area])
        context = SimpleNamespace(area=fake_area("PROPERTIES"), window=SimpleNamespace(screen=screen))

        result = generator._find_view3d_render_context(context)

        self.assertIsNotNone(result)
        self.assertIs(result.area, view_area)

    def test_find_view3d_context_returns_none_without_window_region(self):
        view_area = fake_view3d_area(regions=[SimpleNamespace(type="UI")])
        context = SimpleNamespace(area=view_area, window=SimpleNamespace(screen=SimpleNamespace(areas=[view_area])))

        self.assertIsNone(generator._find_view3d_render_context(context))

    def test_viewport_thumbnail_restores_shading_and_overlay(self):
        view_area = fake_view3d_area()
        context = FakeOverrideContext()
        viewport_context = generator.ViewportRenderContext(
            window=SimpleNamespace(),
            screen=SimpleNamespace(),
            area=view_area,
            region=view_area.regions[0],
            space=view_area.spaces.active,
        )
        original_opengl = generator.bpy.ops.render.opengl
        observed = {}
        try:
            def fake_opengl(**kwargs):
                observed["shading_type"] = view_area.spaces.active.shading.type
                observed["show_overlays"] = view_area.spaces.active.overlay.show_overlays
                observed["kwargs"] = kwargs
                return {"FINISHED"}

            generator.bpy.ops.render.opengl = fake_opengl

            result = generator._write_viewport_thumbnail(context, viewport_context, "MATERIAL")
        finally:
            generator.bpy.ops.render.opengl = original_opengl

        self.assertTrue(result)
        self.assertEqual(observed["shading_type"], "MATERIAL")
        self.assertFalse(observed["show_overlays"])
        self.assertTrue(observed["kwargs"]["write_still"])
        self.assertTrue(observed["kwargs"]["view_context"])
        self.assertEqual(view_area.spaces.active.shading.type, "SOLID")
        self.assertTrue(view_area.spaces.active.overlay.show_overlays)
        self.assertTrue(context.override_used)


class FakeOverrideContext:
    def __init__(self):
        self.override_used = False

    def temp_override(self, **_kwargs):
        self.override_used = True
        return self

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        return False


class FakeSpaces(list):
    @property
    def active(self):
        return self[0] if self else None


def fake_area(area_type):
    return SimpleNamespace(type=area_type, regions=[], spaces=FakeSpaces())


def fake_view3d_area(regions=None):
    space = SimpleNamespace(
        type="VIEW_3D",
        shading=SimpleNamespace(type="SOLID"),
        overlay=SimpleNamespace(show_overlays=True),
    )
    return SimpleNamespace(
        type="VIEW_3D",
        regions=regions if regions is not None else [SimpleNamespace(type="WINDOW")],
        spaces=FakeSpaces([space]),
    )


if __name__ == "__main__":
    unittest.main()
