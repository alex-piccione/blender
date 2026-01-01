import bpy
import bmesh

class WOODWORKING_OT_add_panel(bpy.types.Operator):
    """Add a new wood panel"""
    bl_idname = "woodworking.add_panel"
    bl_label = "Add Panel"
    bl_options = {'REGISTER', 'UNDO'}

    length: bpy.props.FloatProperty( # Use type hinting for 4.x
        name="Length",
        description="Length (X axis)",
        default=0.1,
        min=0.01,
        unit='LENGTH',
        # Set soft min/max to guide the user slider to common values
        soft_min=0.01,
        soft_max=1.0
    ) # pyright: ignore[reportInvalidTypeForm]

    width: bpy.props.FloatProperty( 
        name="Width",
        description="Width (Y axis)",
        default=0.02,
        min=0.005,
        unit='LENGTH',
        soft_min=0.02,
        soft_max=0.6
    ) # pyright: ignore[reportInvalidTypeForm]

    thickness: bpy.props.FloatProperty( 
        name="Thickness",
        description="Thickness (Z axis)",
        default=0.02,
        min=0.005,
        unit='LENGTH',
        soft_min=0.003,
        soft_max=0.12
    ) # pyright: ignore[reportInvalidTypeForm]

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "length")
        layout.prop(self, "width")
        layout.prop(self, "thickness")

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        # Create a new mesh with a Cube
        mesh = bpy.data.meshes.new(name="Panel")

        # Create the 1x1x1 cube at origin
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0, calc_uvs=True)

        # scale vertices to match dimensions
        bmesh.ops.scale(
            bm,
            vec=(self.length, self.width, self.thickness),
            verts=bm.verts,
        )

        # write the bmesh back to the mesh
        bm.to_mesh(mesh)
        bm.free()

        # create an object and link to scene
        obj = bpy.data.objects.new("Panel", mesh)
        context.collection.objects.link(obj)

        # set location to 3D cursor or origin
        obj.location = context.scene.cursor.location

        # select and make active
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        self.report({"INFO"}, f"Created Panel: {(self.length*10.):.1f}cm x {(self.width*10.):.1f}cm h {(self.thickness*10.):.1f}cm")

        return {'FINISHED'}