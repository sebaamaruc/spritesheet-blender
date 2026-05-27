# SpriteSheet Frame Selector
# Entry point for Blender 5.x extension

import bpy
from . import properties, operators, panels, visual_selector

def register():
    properties.register()
    operators.register()
    panels.register()
    bpy.utils.register_class(visual_selector.SPRITESHEET_OT_visual_selector)

def unregister():
    bpy.utils.unregister_class(visual_selector.SPRITESHEET_OT_visual_selector)
    panels.unregister()
    operators.unregister()
    properties.unregister()
