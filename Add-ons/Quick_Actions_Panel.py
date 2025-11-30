import bpy
import bmesh

bl_info = {
    "name": "Quick Actions",
    "author": "Alessandro Piccione",
    "version": (25, 11, 30.2),
    "blender": (4, 3, 0), # minimum Blender version
    "category": "Object",
    "description": "Add some quick actions (Apply All Transforms, Set Origin on Point, ...)"
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

        ## Round Corner button
        row = layout.row()
        row.operator("quick_actions.round_corner", text="Round Corner")

        #layout.operator("object.origin_set", text="Origin to Center").type = 'ORIGIN_CENTER_OF_MASS'
        #row.operator("object.select", text="Select Object").toggle = True
        
class QUICK_ACTIONS_OT_round_corner(bpy.types.Operator):
    """Bevel selected edges with 5 segments and 5mm radius"""
    bl_idname = "quick_actions.round_corner"
    bl_label = "Round Corner"
    bl_options = {'REGISTER', 'UNDO'}

    radius = bpy.props.FloatProperty(
        name="Radius",
        description="Bevel radius",
        default=0.005,
        min=0.0,
        unit='LENGTH'
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == 'EDIT_MESH'

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        
        # Check if any edges are selected
        selected_edges = [e for e in bm.edges if e.select]
        
        if not selected_edges:
            self.report({'WARNING'}, "No edges selected")
            return {'CANCELLED'}
            
        # Apply bevel
        bpy.ops.mesh.bevel(offset=self.radius, segments=5)
        
        return {'FINISHED'}
        
def register():
    bpy.utils.register_class(QUICK_ACTIONS_PT_panel)
    bpy.utils.register_class(QUICK_ACTIONS_OT_round_corner)
    
def unregister():
    bpy.utils.unregister_class(QUICK_ACTIONS_PT_panel)
    bpy.utils.unregister_class(QUICK_ACTIONS_OT_round_corner)
        
if __name__ == "__main__" :
    register()