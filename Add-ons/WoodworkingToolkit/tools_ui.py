import bpy
from . import rotations

class WOODWORKING_PT_tools_panel(bpy.types.Panel):
    #"""Creates a Panel in the Object properties windows"""
    #bl_space_type = "PROPERTIES"
    #bl_region_type = "WINDOW"
    #bl_context = "object"
    bl_label = "Tools"
    bl_idname = "WOODWORKING_PT_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'  # "UI". "TOOLS", "WINDOW"
    bl_category = "Woodworking" # the tab name
    
    def draw(self, context):
        layout = self.layout # creates a layout to arrange elements in the panel
        
        ## Apply All Transforms button
        row = layout.row() # creates a new row in the layout   
        op = row.operator("object.transform_apply", text="Apply All Transforms", icon="CHECKMARK")
        op.location = True
        op.rotation = True
        op.scale = True               

        ## Set Origin on 3D Cursor button
        row = layout.row()
        row.operator("object.origin_set", text="Set Origin on 3D Cursor", icon="CURSOR").type = "ORIGIN_CURSOR"

        ## Rotations        
        rotations.draw_operator(layout)

        ## Round Corner button
        row = layout.row()
        row.operator("woodworking.round_corner", text="Round Corner")

        ## Add panel button
        row = layout.row()
        row.operator("woodworking.add_panel", text="Add Panel", icon="MESH_CUBE")

        ## Add cylinder button
        row = layout.row()
        row.operator("woodworking.add_cylinder", text="Add Cylinder", icon="MESH_CYLINDER")
