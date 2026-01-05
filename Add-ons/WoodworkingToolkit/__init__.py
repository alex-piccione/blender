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
from . import round_corner
from . import rotations
from . import add_panel
from . import add_cylinder
from . import copy_material_from_last_selected

# To make non-class stuff visible in Blender
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

classes = (
    ui.WOODWORKING_PT_panel,
    round_corner.WOODWORKING_OT_round_corner,
    rotations.WOODWORKING_OT_rotate_object,
    add_panel.WOODWORKING_OT_add_panel,
    add_cylinder.WOODWORKING_OT_add_cylinder,
    copy_material_from_last_selected.WOODWORKING_OT_copy_material_from_last_selected,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
