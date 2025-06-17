import bpy

bl_info = {
    "name": "Quick Actions",
    "author": "Alessandro Piccione",
    "version": (25, 5, 6),
    "blender": (4, 2, 0), # minimum Blender version
    "category": "Object",
    "description": "Add some quick actions (Apply All Transforms, Set Origin on Point...)"
}

class QUICK_ACTIONS_PT_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties windows"""
    bl_label = bl_info["name"] 
    bl_idname = "QUICK_ACTIONS_PT_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    def draw(self, context):
        layout = self.layout # creates a layout to arrange elements in the panel
        #layout.label(text="Panel is active")
        #obj = context.object # get the current selected object        
        
        ## Version label
        row = layout.row() # creates a new row in the layout   
        row.label(text="Version: " + ".".join(map(str, bl_info["version"])))

        ## Apply All Transforms button
        row = layout.row() # creates a new row in the layout   
        op = row.operator("object.transform_apply", text="Apply All Transforms")
        op.location = True
        op.rotation = True
        op.scale = True               

        ## Set Origin on 3D Cursor button
        row = layout.row()
        #bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        row.operator("object.origin_set", text="Set Origin on 3D Cursor").type = "ORIGIN_CURSOR"

        #layout.operator("object.origin_set", text="Origin to Center").type = 'ORIGIN_CENTER_OF_MASS'
        #row.operator("object.select", text="Select Object").toggle = True
        
def register():
    bpy.utils.register_class(QUICK_ACTIONS_PT_panel)
    
def unregister():
    bpy.utils.unregiste_class(QUICK_ACTIONS_PT_panel)
        
if __name__ == "__main__" :
    register()    