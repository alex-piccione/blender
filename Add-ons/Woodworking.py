import bpy

info = {
    "name": "Woodworking",
    "author": "Alessandro Piccione",
    "version": (25, 6, 17),
    "blender": (4, 2, 0),  # minimum Blender version
    "category": "Object",
    "description": "Add various woodworking utilities (e.g., Add wire, Add panel, ...)"
}

class WOODWORKING_PT_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties windows"""
    bl_label = info["name"]
    bl_idname = "WOODWORKING_PT_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout  # creates a layout to arrange elements in the panel

        ## Version label
        row = layout.row()  # creates a new row in the layout
        row.label(text="Version: " + ".".join(map(str, info["version"])))

        ## Add Wire button
        row = layout.row()
        row.operator("object.add_wire", text="Add Wire")

        ## Add Panel button
        row = layout.row()
        row.operator("object.add_panel", text="Add Panel")


def register():
    bpy.utils.register_class(WOODWORKING_PT_panel)
    
def unregister():
    bpy.utils.unregiste_class(WOODWORKING_PT_panel)
        
if __name__ == "__main__" :
    register()    