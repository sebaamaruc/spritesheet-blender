"""
Test script to verify Blender PropertyGroup nesting patterns for Workspace V1.
Tests both Option A (PointerProperty) and Option B (embedded/flat) approaches.

Run with:
  /Applications/Blender.app/Contents/MacOS/Blender --background --python scratch/test_property_nesting.py
"""
import bpy
import sys

# =========================================================
# Option A: PointerProperty to a separate PropertyGroup
# =========================================================

class ExportSettingsA(bpy.types.PropertyGroup):
    frame_width: bpy.props.IntProperty(name="Frame Width", default=64)
    frame_height: bpy.props.IntProperty(name="Frame Height", default=64)
    columns: bpy.props.IntProperty(name="Columns", default=8)
    transparent: bpy.props.BoolProperty(name="Transparent", default=True)

class WorkspaceA(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="Workspace")
    output_name: bpy.props.StringProperty(name="Output Name", default="spritesheet")
    # PointerProperty to embedded sub-struct
    export_settings: bpy.props.PointerProperty(type=ExportSettingsA)

# =========================================================
# Option B: Flat/embedded properties directly
# =========================================================

class WorkspaceB(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="Workspace")
    output_name: bpy.props.StringProperty(name="Output Name", default="spritesheet")
    # Embedded directly
    frame_width: bpy.props.IntProperty(name="Frame Width", default=64)
    frame_height: bpy.props.IntProperty(name="Frame Height", default=64)
    columns: bpy.props.IntProperty(name="Columns", default=8)
    transparent: bpy.props.BoolProperty(name="Transparent", default=True)


def test():
    # Register in correct order (inner first)
    bpy.utils.register_class(ExportSettingsA)
    bpy.utils.register_class(WorkspaceA)
    bpy.utils.register_class(WorkspaceB)
    
    # Register collections on Scene
    bpy.types.Scene.test_workspaces_a = bpy.props.CollectionProperty(type=WorkspaceA)
    bpy.types.Scene.test_workspaces_b = bpy.props.CollectionProperty(type=WorkspaceB)
    
    scene = bpy.context.scene
    
    # ---- Test Option A ----
    print("\n=== Option A: PointerProperty ===")
    ws_a = scene.test_workspaces_a.add()
    ws_a.name = "Goblin_A"
    ws_a.output_name = "goblin_front"
    
    # Access nested export_settings via PointerProperty
    print(f"  Created workspace: {ws_a.name}")
    print(f"  export_settings type: {type(ws_a.export_settings)}")
    print(f"  export_settings.frame_width (default): {ws_a.export_settings.frame_width}")
    
    # Modify nested property
    ws_a.export_settings.frame_width = 128
    ws_a.export_settings.columns = 16
    ws_a.export_settings.transparent = False
    print(f"  export_settings.frame_width (modified): {ws_a.export_settings.frame_width}")
    print(f"  export_settings.columns (modified): {ws_a.export_settings.columns}")
    print(f"  export_settings.transparent (modified): {ws_a.export_settings.transparent}")
    
    # Test duplication by copying properties
    ws_a2 = scene.test_workspaces_a.add()
    ws_a2.name = ws_a.name + "_copy"
    ws_a2.output_name = ws_a.output_name
    ws_a2.export_settings.frame_width = ws_a.export_settings.frame_width
    ws_a2.export_settings.columns = ws_a.export_settings.columns
    ws_a2.export_settings.transparent = ws_a.export_settings.transparent
    
    print(f"  Duplicated workspace: {ws_a2.name}")
    print(f"  Duplicate frame_width: {ws_a2.export_settings.frame_width}")
    
    # Verify independence
    ws_a2.export_settings.frame_width = 256
    print(f"  Original frame_width after modifying copy: {ws_a.export_settings.frame_width} (should be 128)")
    print(f"  Copy frame_width: {ws_a2.export_settings.frame_width} (should be 256)")
    
    assert ws_a.export_settings.frame_width == 128, "FAIL: Original was modified!"
    assert ws_a2.export_settings.frame_width == 256, "FAIL: Copy was not modified!"
    print("  ✓ Independence verified")
    
    # ---- Test Option B ----
    print("\n=== Option B: Flat/Embedded ===")
    ws_b = scene.test_workspaces_b.add()
    ws_b.name = "Goblin_B"
    ws_b.output_name = "goblin_back"
    ws_b.frame_width = 128
    ws_b.columns = 16
    ws_b.transparent = False
    
    print(f"  Created workspace: {ws_b.name}")
    print(f"  frame_width: {ws_b.frame_width}")
    print(f"  columns: {ws_b.columns}")
    
    # ---- Test CollectionProperty count ----
    print(f"\n=== Collection counts ===")
    print(f"  Option A workspaces: {len(scene.test_workspaces_a)}")
    print(f"  Option B workspaces: {len(scene.test_workspaces_b)}")
    
    # ---- Test iterating over nested PointerProperty ----
    print(f"\n=== Iteration test (Option A) ===")
    for ws in scene.test_workspaces_a:
        print(f"  {ws.name}: frame_width={ws.export_settings.frame_width}, cols={ws.export_settings.columns}")
    
    # ---- Test removal ----
    scene.test_workspaces_a.remove(0)
    print(f"\n=== After removing first workspace (Option A) ===")
    print(f"  Remaining: {len(scene.test_workspaces_a)}")
    for ws in scene.test_workspaces_a:
        print(f"  {ws.name}: frame_width={ws.export_settings.frame_width}")
    
    # Cleanup
    del bpy.types.Scene.test_workspaces_a
    del bpy.types.Scene.test_workspaces_b
    bpy.utils.unregister_class(WorkspaceB)
    bpy.utils.unregister_class(WorkspaceA)
    bpy.utils.unregister_class(ExportSettingsA)
    
    print("\n=== ALL TESTS PASSED ===\n")

if __name__ == '__main__':
    test()
