import bpy

class WOODWORKING_OT_assign_material(bpy.types.Operator):
    bl_idname = "woodworking.assign_material"
    bl_label = "Assign Material to Selected"
    bl_options = {'UNDO'}
    
    material: bpy.props.StringProperty() # type: ignore
    
    def execute(self, context):
        mat = bpy.data.materials.get(self.material)

        if not mat:
            self.report({"ERROR"}, f"Material '{self.material}' not found")
            return {'CANCELLED'}
        
        assigned_count = 0
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                obj.data.materials.clear()
                obj.data.materials.append(mat)
                assigned_count += 1

        self.report({"INFO"}, f"Assigned '{mat.name}' to {assigned_count} objects")
        return {'FINISHED'}

class WOODWORKING_OT_delete_material(bpy.types.Operator):
    """Delete unused material"""
    bl_idname = "woodworking.delete_material"
    bl_label = "Delete Material"
    bl_options = {'UNDO'}
    
    material: bpy.props.StringProperty()  #type: ignore
    
    @classmethod
    def poll(cls, context):
        mat = bpy.data.materials.get(context.scene.delete_material_name)
        return mat and len(mat.users) == 0
    
    def execute(self, context):
        mat = bpy.data.materials.get(self.material)
        if mat and len(mat.users) == 0:
            bpy.data.materials.remove(mat)
            self.report({"INFO"}, f"Deleted {self.material}")
            return {'FINISHED'}
        else:
            self.report({"WARNING"}, f"Cannot delete {self.material} (in use)")
            return {'CANCELLED'}
