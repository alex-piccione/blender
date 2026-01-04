import bpy
import bmesh

class WOODWORKING_OT_round_corner(bpy.types.Operator):
    """Bevel selected edges with 5 segments and 5mm radius"""
    bl_idname = "woodworking.round_corner"
    bl_label = "Round Corner"
    bl_options = {'REGISTER', 'UNDO'}

    radius: bpy.props.FloatProperty( # Use type hinting for 4.x
        name="Radius",
        description="Bevel radius",
        default=0.005,
        min=0.0,
        unit='LENGTH',
        # Set soft min/max to guide the user slider to common values
        soft_min=0.001,
        soft_max=0.05
    ) # pyright: ignore[reportInvalidTypeForm]
        
    segments: bpy.props.IntProperty(
        name="Segments",
        description="Number of segments for smoothness",
        default=5,
        min=1,
        max=32
    ) # pyright: ignore[reportInvalidTypeForm]

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "radius")
        layout.prop(self, "segments")

    @classmethod
    def poll(cls, context):
        # Only allow if an active object exists and we are in Edit Mode
        return (context.active_object is not None and 
                context.active_object.type == 'MESH' and
                context.mode == 'EDIT_MESH')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        # Check if selection exists
        bm = bmesh.from_edit_mesh(context.active_object.data)
        if not any(e.select for e in bm.edges):
            self.report({'WARNING'}, "No edges selected.")
            return {'CANCELLED'}

        # Apply bevel using the property values
        bpy.ops.mesh.bevel(
            offset=self.radius, 
            segments=self.segments,
            profile=0.5        # For a smooth quarter-circle curve
        )
        
        return {'FINISHED'}