import unittest
import tempfile
import sys
import os
from contextlib import contextmanager
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
            Operator=object,
            PropertyGroup=object,
            Object=object,
            Collection=object,
        ),
        props=SimpleNamespace(IntProperty=lambda **_kwargs: None),
    )
else:
    bpy_stub = sys.modules["bpy"]
    if not hasattr(bpy_stub, "types"):
        bpy_stub.types = SimpleNamespace()
    if not hasattr(bpy_stub.types, "Operator"):
        bpy_stub.types.Operator = object
    if not hasattr(bpy_stub, "props"):
        bpy_stub.props = SimpleNamespace(IntProperty=lambda **_kwargs: None)

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
from spritesheet_frame_selector.operators import preview as preview_ops
from spritesheet_frame_selector.preview import generator
from spritesheet_frame_selector.render import renderer


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
        clip = fake_clip()

        clip.preview_mode = "RENDERED"

        self.assertEqual(effective_preview_mode(clip), "RENDERED")

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

    def test_viewport_scope_restores_shading_overlay_and_camera_view(self):
        view_area = fake_view3d_area()
        context = FakeOverrideContext()
        viewport_context = generator.ViewportRenderContext(
            window=SimpleNamespace(),
            screen=SimpleNamespace(),
            area=view_area,
            region=view_area.regions[0],
            space=view_area.spaces.active,
            region_3d=view_area.spaces.active.region_3d,
        )
        original_opengl = generator.bpy.ops.render.opengl
        observed = {}
        try:
            def fake_opengl(**kwargs):
                observed["shading_type"] = view_area.spaces.active.shading.type
                observed["show_overlays"] = view_area.spaces.active.overlay.show_overlays
                observed["view_perspective"] = view_area.spaces.active.region_3d.view_perspective
                observed["kwargs"] = kwargs
                return {"FINISHED"}

            generator.bpy.ops.render.opengl = fake_opengl

            with generator._viewport_render_scope(viewport_context, "MATERIAL"):
                result = generator._write_viewport_thumbnail(context, viewport_context)
        finally:
            generator.bpy.ops.render.opengl = original_opengl

        self.assertTrue(result)
        self.assertEqual(observed["shading_type"], "MATERIAL")
        self.assertFalse(observed["show_overlays"])
        self.assertEqual(observed["view_perspective"], "CAMERA")
        self.assertTrue(observed["kwargs"]["write_still"])
        self.assertTrue(observed["kwargs"]["view_context"])
        self.assertEqual(view_area.spaces.active.shading.type, "SOLID")
        self.assertTrue(view_area.spaces.active.overlay.show_overlays)
        self.assertEqual(view_area.spaces.active.region_3d.view_perspective, "PERSP")
        self.assertTrue(context.override_used)

    def test_viewport_thumbnail_requires_region_3d(self):
        view_area = fake_view3d_area(region_3d=None)
        context = FakeOverrideContext()
        viewport_context = generator.ViewportRenderContext(
            window=SimpleNamespace(),
            screen=SimpleNamespace(),
            area=view_area,
            region=view_area.regions[0],
            space=view_area.spaces.active,
            region_3d=None,
        )

        with self.assertRaisesRegex(RuntimeError, "requires a 3D Viewport with RegionView3D"):
            with generator._viewport_render_scope(viewport_context, "SOLID"):
                generator._write_viewport_thumbnail(context, viewport_context)


class PreviewAlphaSettingsTests(unittest.TestCase):
    def test_generate_previews_configures_alpha_png_and_restores_render_settings(self):
        clip = fake_clip()
        context = fake_preview_context()
        camera = SimpleNamespace(users_collection=())
        collection = SimpleNamespace(children=())
        observed = {}
        original_writer_scope = generator._thumbnail_writer_scope
        original_visibility_scope = generator.collection_visibility_scope
        try:
            @contextmanager
            def fake_writer_scope(_context, preview_mode):
                def write_thumbnail():
                    render = context.scene.render
                    image_settings = render.image_settings
                    observed["preview_mode"] = preview_mode
                    observed["file_format"] = image_settings.file_format
                    observed["color_mode"] = image_settings.color_mode
                    observed["color_depth"] = image_settings.color_depth
                    observed["film_transparent"] = render.film_transparent
                    observed["use_file_extension"] = render.use_file_extension
                    with open(render.filepath, "wb") as handle:
                        handle.write(b"png")
                    return True

                yield write_thumbnail

            generator._thumbnail_writer_scope = fake_writer_scope
            generator.collection_visibility_scope = fake_visibility_scope
            with tempfile.TemporaryDirectory() as tmpdir:
                result = generator.generate_viewport_previews(
                    context,
                    clip,
                    camera,
                    [collection],
                    tmpdir,
                    [1],
                    preview_mode="RENDERED",
                )
        finally:
            generator._thumbnail_writer_scope = original_writer_scope
            generator.collection_visibility_scope = original_visibility_scope

        self.assertTrue(result.success)
        self.assertEqual(observed["preview_mode"], "RENDERED")
        self.assertEqual(observed["file_format"], "PNG")
        self.assertEqual(observed["color_mode"], "RGBA")
        self.assertEqual(observed["color_depth"], "8")
        self.assertTrue(observed["film_transparent"])
        self.assertTrue(observed["use_file_extension"])
        self.assertEqual(context.scene.frame_current, 7)
        self.assertEqual(context.scene.camera, "original-camera")
        self.assertEqual(context.scene.render.filepath, "/tmp/original")
        self.assertEqual(context.scene.render.resolution_x, 1920)
        self.assertEqual(context.scene.render.resolution_y, 1080)
        self.assertEqual(context.scene.render.resolution_percentage, 50)
        self.assertFalse(context.scene.render.film_transparent)
        self.assertFalse(context.scene.render.use_file_extension)
        self.assertEqual(context.scene.render.image_settings.file_format, "JPEG")
        self.assertEqual(context.scene.render.image_settings.color_mode, "RGB")
        self.assertEqual(context.scene.render.image_settings.color_depth, "16")

    def test_solid_preview_keeps_opaque_png_as_warning_when_alpha_can_be_validated(self):
        clip = fake_clip()
        context = fake_preview_context()
        camera = SimpleNamespace(users_collection=())
        collection = SimpleNamespace(children=())
        original_writer_scope = generator._thumbnail_writer_scope
        original_visibility_scope = generator.collection_visibility_scope
        original_has_transparency = generator._preview_file_has_transparency
        try:
            @contextmanager
            def fake_writer_scope(_context, _preview_mode):
                def write_thumbnail():
                    with open(context.scene.render.filepath, "wb") as handle:
                        handle.write(b"opaque")
                    return True

                yield write_thumbnail

            generator._thumbnail_writer_scope = fake_writer_scope
            generator.collection_visibility_scope = fake_visibility_scope
            generator._preview_file_has_transparency = lambda _path: False
            with tempfile.TemporaryDirectory() as tmpdir:
                result = generator.generate_viewport_previews(
                    context,
                    clip,
                    camera,
                    [collection],
                    tmpdir,
                    [1],
                    preview_mode="SOLID",
                )
                generated_path = next(iter(result.frame_paths.values()))
                file_exists = os.path.exists(generated_path)
        finally:
            generator._thumbnail_writer_scope = original_writer_scope
            generator.collection_visibility_scope = original_visibility_scope
            generator._preview_file_has_transparency = original_has_transparency

        self.assertTrue(result.success)
        self.assertIn("no transparent pixels detected", result.message)
        self.assertTrue(file_exists)

    def test_preview_file_has_transparency_detects_alpha_values(self):
        original_data = getattr(generator.bpy, "data", None)
        try:
            generator.bpy.data = SimpleNamespace(
                images=FakeImages(
                    SimpleNamespace(channels=4, pixels=[1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.25])
                )
            )

            self.assertTrue(generator._preview_file_has_transparency("/tmp/frame.png"))
        finally:
            if original_data is None:
                delattr(generator.bpy, "data")
            else:
                generator.bpy.data = original_data

    def test_preview_file_has_transparency_rejects_opaque_or_rgb_images(self):
        original_data = getattr(generator.bpy, "data", None)
        try:
            generator.bpy.data = SimpleNamespace(
                images=FakeImages(SimpleNamespace(channels=4, pixels=[1.0, 1.0, 1.0, 1.0]))
            )
            self.assertFalse(generator._preview_file_has_transparency("/tmp/opaque.png"))

            generator.bpy.data = SimpleNamespace(
                images=FakeImages(SimpleNamespace(channels=3, pixels=[1.0, 1.0, 1.0]))
            )
            self.assertFalse(generator._preview_file_has_transparency("/tmp/rgb.png"))
        finally:
            if original_data is None:
                delattr(generator.bpy, "data")
            else:
                generator.bpy.data = original_data


class PreviewCacheGcTests(unittest.TestCase):
    def test_purge_sibling_preview_caches_keeps_current_and_unmanaged_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = preview_cache_root(os.path.join(tmpdir, "scene.blend"))
            current_key = "a" * 16
            stale_key = "b" * 16
            current = preview_cache_folder(root, "workspace-id", "clip-id", current_key)
            stale = preview_cache_folder(root, "workspace-id", "clip-id", stale_key)
            unmanaged = os.path.join(os.path.dirname(current), "manual-folder")
            os.makedirs(current)
            os.makedirs(stale)
            os.makedirs(unmanaged)

            preview_ops._purge_sibling_preview_caches(root, "workspace-id", "clip-id", current_key)

            self.assertTrue(os.path.isdir(current))
            self.assertFalse(os.path.exists(stale))
            self.assertTrue(os.path.isdir(unmanaged))


class FinalRenderAlphaSettingsTests(unittest.TestCase):
    def test_render_clip_frames_forces_rgba_for_transparent_exports_and_restores(self):
        context = fake_preview_context()
        camera = SimpleNamespace(users_collection=())
        collection = SimpleNamespace(children=())
        export_settings = SimpleNamespace(
            frame_width=32,
            frame_height=48,
            transparent=True,
            sheet_name="sheet",
        )
        observed = {}
        original_render_op = renderer.bpy.ops.render.render
        original_visibility_scope = renderer.collection_visibility_scope
        try:
            def fake_render(**_kwargs):
                render = context.scene.render
                image_settings = render.image_settings
                observed["file_format"] = image_settings.file_format
                observed["color_mode"] = image_settings.color_mode
                observed["color_depth"] = image_settings.color_depth
                observed["film_transparent"] = render.film_transparent
                with open(render.filepath, "wb") as handle:
                    handle.write(b"png")
                return {"FINISHED"}

            renderer.bpy.ops.render.render = fake_render
            renderer.collection_visibility_scope = fake_visibility_scope
            with tempfile.TemporaryDirectory() as tmpdir:
                result = renderer.render_clip_frames(
                    context,
                    fake_clip(),
                    camera,
                    [collection],
                    tmpdir,
                    [3],
                    export_settings,
                )
        finally:
            renderer.bpy.ops.render.render = original_render_op
            renderer.collection_visibility_scope = original_visibility_scope

        self.assertTrue(result.success)
        self.assertEqual(observed["file_format"], "PNG")
        self.assertEqual(observed["color_mode"], "RGBA")
        self.assertEqual(observed["color_depth"], "8")
        self.assertTrue(observed["film_transparent"])
        self.assertEqual(context.scene.render.image_settings.file_format, "JPEG")
        self.assertEqual(context.scene.render.image_settings.color_mode, "RGB")
        self.assertEqual(context.scene.render.image_settings.color_depth, "16")


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


_DEFAULT_REGION_3D = object()


def fake_view3d_area(regions=None, region_3d=_DEFAULT_REGION_3D):
    if region_3d is _DEFAULT_REGION_3D:
        region_3d = SimpleNamespace(view_perspective="PERSP")
    space = SimpleNamespace(
        type="VIEW_3D",
        shading=SimpleNamespace(type="SOLID"),
        overlay=SimpleNamespace(show_overlays=True),
        region_3d=region_3d,
    )
    return SimpleNamespace(
        type="VIEW_3D",
        regions=regions if regions is not None else [SimpleNamespace(type="WINDOW")],
        spaces=FakeSpaces([space]),
    )


@contextmanager
def fake_visibility_scope(_view_layer, _collections, _camera):
    yield


class FakeImages:
    def __init__(self, image):
        self.image = image
        self.removed = None

    def load(self, _path, check_existing=False):
        return self.image

    def remove(self, image):
        self.removed = image


class FakeScene:
    def __init__(self):
        self.frame_current = 7
        self.camera = "original-camera"
        self.render = SimpleNamespace(
            filepath="/tmp/original",
            resolution_x=1920,
            resolution_y=1080,
            resolution_percentage=50,
            film_transparent=False,
            use_file_extension=False,
            image_settings=SimpleNamespace(
                file_format="JPEG",
                color_mode="RGB",
                color_depth="16",
            ),
        )

    def frame_set(self, frame_number):
        self.frame_current = frame_number


def fake_preview_context():
    return SimpleNamespace(
        scene=FakeScene(),
        view_layer=SimpleNamespace(),
    )


if __name__ == "__main__":
    unittest.main()
