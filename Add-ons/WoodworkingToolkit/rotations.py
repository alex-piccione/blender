import bpy
import math
from mathutils import Matrix

class WOODWORKING_OT_rotate_object(bpy.types.Operator):
    """Rotate object by fixed amount"""
    bl_idname = "woodworking.rotate_object"
    bl_label = "Rotate Object"
    bl_options = {'UNDO'}  # {'REGISTER', 'UNDO'}  with REGISTER we have the REDO panel
    
    axis: bpy.props.EnumProperty(
        name="Axis",
        items=[
            ('X', "X", "X axis"),
            ('Y', "Y", "Y axis"),
            ('Z', "Z", "Z axis"),
        ]
    ) # type: ignore
    
    angle: bpy.props.FloatProperty(
        name="Angle",
        default=90.0,
        unit='ROTATION'  # This tells Blender it's in degrees!
    ) # type: ignore
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        obj = context.active_object
        
        # Convert angle to radians for the rotation matrix
        angle_rad = math.radians(self.angle)
        
        # Create rotation matrix
        rot_mat = Matrix.Rotation(angle_rad, 4, self.axis)
        
        # Apply rotation to object's matrix
        obj.matrix_world = obj.matrix_world @ rot_mat
        
        # Update the object
        obj.update_tag()

        # Apply rotation so Item tab shows 0°
        bpy.ops.object.transform_apply(
            location=False,
            rotation=True,
            scale=False
        )

        return {'FINISHED'}


# In your UI draw function:
def draw_operator (layout):
    box = layout.box()
    box.label(text="Rotate")
    
    # X (Red)
    row_x = box.row(align=True)
    row_x.label(text="X:")

    op = row_x.operator("woodworking.rotate_object", text="-90°")
    op.axis = 'X'
    op.angle = -90.0
    
    op = row_x.operator("woodworking.rotate_object", text="+90°")
    op.axis = 'X'
    op.angle = 90.0   
    
    # Y (Green)
    row_y = box.row(align=True)
    row_y.label(text="Y:")
    
    op = row_y.operator("woodworking.rotate_object", text="-90°")
    op.axis = 'Y'
    op.angle = -90.0
    
    op = row_y.operator("woodworking.rotate_object", text="+90°")
    op.axis = 'Y'
    op.angle = 90.0
    
    # Z (Blue)
    row_z = box.row(align=True)
    row_z.label(text="Z:")

    op = row_z.operator("woodworking.rotate_object", text="-90°")
    op.axis = 'Z'
    op.angle = -90.0
    
    op = row_z.operator("woodworking.rotate_object", text="+90°")
    op.axis = 'Z'
    op.angle = 90.0    
