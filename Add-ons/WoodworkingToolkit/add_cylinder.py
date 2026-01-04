import bpy
import bmesh
from helper import mm, cm

class WOODWORKING_OT_add_cylinder(bpy.types.Operator):
    """Add a cylinder"""
    bl_idname = "woodworking.add_cylinder"
    bl_label = "Add Cylinder"
    bl_options = {'REGISTER', 'UNDO'}

    diameter: bpy.props.FloatProperty( 
        name="Diameter",
        description="Diameter (Y-Z axis)",
        default=mm(6),
        min=mm(1),
        unit='LENGTH',
        soft_min=mm(2),
        soft_max=mm(10)
    ) # pyright: ignore[reportInvalidTypeForm]

    length: bpy.props.FloatProperty( # Use type hinting for 4.x
        name="Length",
        description="Length (X axis)",
        default=cm(2),
        min=cm(1),
        unit='LENGTH',
        # Set soft min/max to guide the user slider to common values
        soft_min=cm(10),
        soft_max=cm(50)
    ) # pyright: ignore[reportInvalidTypeForm]


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "diameter")
        layout.prop(self, "length")

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        # Create a new mesh with a Cylinder
        mesh = bpy.data.meshes.new(name="Cylinder")

        # Create the 1x1x1 cylinder at origin
        bm = bmesh.new()
        bmesh.ops.create_cylinder(bm, size=1.0, calc_uvs=True)

        # scale vertices to match dimensions
        bmesh.ops.scale(
            bm,
            vec=(self.length, self.diameter, self.diameter),
            verts=bm.verts,
        )

        # write the bmesh back to the mesh
        bm.to_mesh(mesh)
        bm.free()

        # create an object and link to scene
        obj = bpy.data.objects.new("Cylinder", mesh)
        context.collection.objects.link(obj)

        # set location to 3D cursor or origin
        obj.location = context.scene.cursor.location

        # select and make active
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        self.report({"INFO"}, f"Created Cylinder. Diameter: {(self.diameter*10.):.1f}cm, Length: {(self.length*10.):.1f}cm")

        return {'FINISHED'}