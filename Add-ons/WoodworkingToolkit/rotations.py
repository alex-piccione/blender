import math

DEG90 = math.radians(90)  # 1.5708 radians

def draw(layout):

    box = layout.box()
    box.label(text="Rotation")
    
    # X Axis
    row_x = box.row()
    row_x.label(text="X:")
    op = row_x.operator("transform.rotate", text="+90")
    op.value = DEG90
    op.constraint_axis = (True, False, False)
    op = row_x.operator("transform.rotate", text="-90")
    op.value = -DEG90
    op.constraint_axis = (True, False, False)
    op.release_confirm=True # apply
    
    # Y Axis
    row_y = box.row()
    row_y.label(text="Y:")
    op = row_y.operator("transform.rotate", text="+90")
    op.value = DEG90
    op.constraint_axis = (False, True, False)
    op = row_y.operator("transform.rotate", text="-90")
    op.value = -DEG90
    op.constraint_axis = (False, True, False)
    op.release_confirm=True
    
    # Z Axis
    row_z = box.row()
    row_z.label(text="Z:")
    op = row_z.operator("transform.rotate", text="+90")
    op.value = DEG90
    op.constraint_axis = (False, False, True)
    op = row_z.operator("transform.rotate", text="-90")
    op.value = -DEG90
    op.constraint_axis = (False, False, True)
    op.release_confirm=True
