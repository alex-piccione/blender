import bpy


class WOODWORKING_OT_copy_material_from_last_selected(bpy.types.Operator):
    """Copy the Material from the last selected object to all the selected ones"""
    bl_idname = "woodworking.copy_material_from_last_selected"
    bl_label = "Copy Material Object"
    bl_options = {'REGISTER', 'UNDO'}  # {'REGISTER', 'UNDO'}  with REGISTER we have the REDO panel
    
    def poll(self, context):
        return (context.active_object and 
                context.active_object.type == 'MESH' and 
                len(context.selected_objects) > 1)

    def execute(self, context):
            # Just call the built-in operator!
            bpy.ops.object.material_slot_copy()
            self.report({"INFO"}, "Copied materials to selected objects")
            return {'FINISHED'}

# In your UI draw function:
def draw_operator(layout):
    layout.operator("woodworking.copy_material_from_last_selected", 
                   text="Copy Material from last selected", 
                   icon='MATERIAL')