import bpy
import math
from mathutils import Matrix

class WOODWORKING_OT_rotate_object(bpy.types.Operator):
    """Rotate object by fixed amount"""
    bl_idname = "woodworking.rotate_object"
    bl_label = "Rotate Object"
    bl_options = {'REGISTER', 'UNDO'}
    
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
        if self.axis == 'X':
            rot_mat = Matrix.Rotation(angle_rad, 4, 'X')
        elif self.axis == 'Y':
            rot_mat = Matrix.Rotation(angle_rad, 4, 'Y')
        else:  # 'Z'
            rot_mat = Matrix.Rotation(angle_rad, 4, 'Z')
        
        # Apply rotation to object's matrix
        obj.matrix_world = obj.matrix_world @ rot_mat
        
        # Update the object
        obj.update_tag()
        
        return {'FINISHED'}


# In your draw function:
def draw_rotation_controls (layout):
    box = layout.box()
    box.label(text="Rotation")
    
    #row_x = box.row(align=True)
    #row_x.label(text="X:", icon='GIZMO_ARROW_X')
    #row_x.operator("woodworking.rotate_object", text="+90°", icon='GIZMO_ARROW_X', emboss=False).axis = 'X'; row_x.operator.axis = 90.0
    #row_x.operator("woodworking.rotate_object", text="-90°", icon='GIZMO_ARROW_X', emboss=False).axis = 'X'; row_x.operator.angle = -90.0

    # X (Red)
    row_x = box.row(align=True)
    row_x.label(text="X:", icon='COLOR_RED')
    
    op = row_x.operator("woodworking.rotate_object", text="+90°", icon='COLOR_RED', emboss=False)
    op.axis = 'X';  op.angle = 90.0
    
    op = row_x.operator("woodworking.rotate_object", text="-90", icon='COLOR_RED', emboss=False)
    op.axis = 'X';  op.angle = -90.0
    
    # Y Axis
    row_y = box.row()
    row_y.label(text="Y:")
    
    op = row_y.operator("woodworking.rotate_object", text="+90")
    op.axis = 'Y'
    op.angle = 90.0
    
    op = row_y.operator("woodworking.rotate_object", text="-90")
    op.axis = 'Y'
    op.angle = -90.0
    
    # Z Axis
    row_z = box.row()
    row_z.label(text="Z:")
    
    op = row_z.operator("woodworking.rotate_object", text="+90")
    op.axis = 'Z'
    op.angle = 90.0
    
    op = row_z.operator("woodworking.rotate_object", text="-90")
    op.axis = 'Z'
    op.angle = -90.0