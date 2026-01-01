bl_info = {
    "name": "Woodworking Toolkit",
    "author": "Alessandro Piccione",
    "version": (25, 11, 30, 3),
    "blender": (4, 3, 0), # minimum Blender version
    "location": "View3D > Sidebar > Woodworking Tab",
    #"category": "Object",
    "category": "3D View",
    "description": "Add actions usefull for general 3D modeling and more specific for model wood objects."
}

import bpy
from . import ui
from . import operators
from . import add_panel

classes = (
    ui.WOODWORKING_PT_panel,
    operators.WOODWORKING_OT_round_corner,
    add_panel.WOODWORKING_OT_add_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
