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
from . import tools_ui
from . import round_corner
from . import rotations
from . import add_panel
from . import add_cylinder
from . import copy_material_from_last_selected
from . import material_ui
from . import material_operators

# To make non-class stuff visible in Blender
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

classes = (
    tools_ui.WOODWORKING_PT_tools_panel,
    # operators
    round_corner.WOODWORKING_OT_round_corner,
    rotations.WOODWORKING_OT_rotate_object,
    add_panel.WOODWORKING_OT_add_panel,
    add_cylinder.WOODWORKING_OT_add_cylinder,
    copy_material_from_last_selected.WOODWORKING_OT_copy_material_from_last_selected,

    # other
    material_ui.WOODWORKING_UL_material_list, 
    material_ui.WOODWORKING_PT_material_panel,
    material_operators.WOODWORKING_OT_assign_material,
    material_operators.WOODWORKING_OT_delete_material,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.woodworking_material_index = bpy.props.IntProperty()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.woodworking_material_index

if __name__ == "__main__":
    register()
