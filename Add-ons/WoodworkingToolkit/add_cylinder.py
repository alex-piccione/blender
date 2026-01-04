import bpy
import bmesh
from .utils import *  # relative path

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
        max=cm(100),
        unit='LENGTH',
        step=1,
        precision=3,
        soft_min=mm(2),
        soft_max=mm(10)
    ) # pyright: ignore[reportInvalidTypeForm]

    length: bpy.props.FloatProperty( # Use type hinting for 4.x
        name="Length",
        description="Length (X axis)",
        default=cm(2),
        min=cm(1),
        max=cm(100),
        unit='LENGTH',
        # Set soft min/max to guide the user slider to common values
        soft_min=cm(2),
        soft_max=cm(50),
        step=10
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
        # Use built-in primitive operator with your params
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,                    # Sides (adjust as needed)
            radius=self.diameter / 2,       # Diameter → radius
            depth=self.length,              # Length = depth
            location=context.scene.cursor.location,
            enter_editmode=False
        )

        # Get the new cylinder
        obj = context.active_object
        obj.name = "Cylinder"

        # Select and activate
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        self.report({"INFO"}, f"Created Cylinder. Diameter: {self.diameter*1000:.1f}mm, Length: {self.length*1000:.1f}mm")
        return {'FINISHED'}

"""

        # Create a new mesh with a Cylinder
        mesh = bpy.data.meshes.new(name="Cylinder")
        bm = bmesh.new()

        # Create base circle (segments=16 for medium-smooth cylinder)
        circle = bmesh.ops.create_circle(
            bm,
            cap_ends=False,      # No end caps yet
            diameter=1.0,        # Scale later
            segments=16
        )
        verts_base = [v for v in circle["verts"]]

        # Extrude to length
        circle = bmesh.ops.extrude_vert_indiv(bm, verts=verts_base)
        verts_extrude = [e for e in ret["faces"]][0].verts  # Top ring




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
"""