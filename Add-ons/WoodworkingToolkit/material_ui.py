import bpy
from . import copy_material_from_last_selected

class WOODWORKING_PT_material_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties windows"""
    bl_label = "Material"
    bl_idname = "WOODWORKING_PT_material_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Woodworking"

    def draw(self, context):
        layout = self.layout
        
        # List all materials
        layout.template_list(
            "WOODWORKING_UL_material_list",
            "",
            bpy.data,
            "materials",
            context.scene,
            "woodworking_material_index"
        )

        ## Copy Material
        copy_material_from_last_selected.draw_operator(layout)


class WOODWORKING_UL_material_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # FIXED: item = index (int), data.materials[index] = actual material
        material = data.materials[index]
        
        row = layout.row(align=True)
        row.template_ID_preview(material, "preview", new="material.new")
        
        sub = row.row()
        sub.prop(material, "name", text="", emboss=False)
        sub.label(text=f"({material.users })") 
        
        # Assign button
        assign = row.operator("woodworking.assign_material", text="", icon='MATERIAL_DATA')
        assign.material = material.name
        
        # Delete unused
        if len(material.users) == 0:
            op = row.operator("woodworking.delete_material", text="", icon='X').material
            op.material = material.name