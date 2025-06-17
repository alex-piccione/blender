import bpy
import bmesh
from bpy.types import Operator, Panel
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import gpu
from gpu_extras.batch import batch_for_shader

bl_info = {
    "name": "Drill Hole Tool",
    "author": "Alessandro Piccione",
    "version": (25, 6, 17),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Tool",
    "description": "Create drill holes through objects",
    "category": "Mesh",
}

# Constants to avoid magic strings
OPERATOR_ID = "mesh.drill_hole"
PANEL_ID = "VIEW3D_PT_drill_hole"
PANEL_LABEL = "Drill Hole Tool"
PANEL_CATEGORY = "Tool"

# Property names (with unique prefixes to avoid conflicts)
PROP_HOLE_DIAMETER = "drill_tool_hole_diameter"
PROP_USE_CURSOR = "drill_tool_use_cursor"

class MESH_OT_drill_hole(Operator):
    """Drill a hole through the selected object"""
    bl_idname = OPERATOR_ID
    bl_label = "Drill Hole"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and 
                context.active_object.type == 'MESH')
    
    def execute(self, context):
        obj = context.active_object
        
        # Read settings from Scene properties (set by the panel)
        hole_diameter = getattr(context.scene, PROP_HOLE_DIAMETER)
        use_cursor = getattr(context.scene, PROP_USE_CURSOR)
        
        if use_cursor:
            # Use 3D cursor position
            drill_point = context.scene.cursor.location.copy()
        else:
            # Use selection center
            drill_point = self.get_selection_center(obj)
            if drill_point is None:
                self.report({'ERROR'}, "No valid selection found. Select vertices/faces or enable 'Use 3D Cursor'")
                return {'CANCELLED'}
        
        # Calculate drill direction and depth
        drill_data = self.calculate_drill_path(obj, drill_point)
        if drill_data is None:
            self.report({'ERROR'}, "Could not calculate drill path")
            return {'CANCELLED'}
        
        # Create the hole
        self.create_hole(obj, drill_data, hole_diameter)
        
        self.report({'INFO'}, f"Hole drilled with diameter {hole_diameter}mm")
        return {'FINISHED'}
    
    def get_selection_center(self, obj):
        """Get center point of selected mesh elements"""
        if obj.mode != 'EDIT':
            return None
        
        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = [v for v in bm.verts if v.select]
        selected_faces = [f for f in bm.faces if f.select]
        
        if selected_verts:
            center = sum((v.co for v in selected_verts), Vector()) / len(selected_verts)
            return obj.matrix_world @ center
        elif selected_faces:
            center = sum((f.calc_center_median() for f in selected_faces), Vector()) / len(selected_faces)
            return obj.matrix_world @ center
        
        return None
    
    def calculate_drill_path(self, obj, drill_point):
        """Calculate drill direction and depth by raycasting"""
        # Convert drill point to object local space
        local_point = obj.matrix_world.inverted() @ drill_point
        
        # Create BVH tree for raycasting
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bvh = BVHTree.FromBMesh(bm)
        
        # Find the closest surface point and get its normal
        location, normal, face_index, distance = bvh.find_nearest(local_point)
        if location is None:
            bm.free()
            return None
        
        # Use the surface normal as drill direction
        drill_direction = normal.normalized()
        
        # Raycast through the object to find exit point
        # Cast ray in both directions to find the longest path
        ray_start = location + drill_direction * 0.001  # Slightly inside
        ray_direction = -drill_direction  # Drill inward
        
        hit_location, hit_normal, hit_face_index, hit_distance = bvh.ray_cast(ray_start, ray_direction)
        
        if hit_location is None:
            # Try opposite direction
            ray_direction = drill_direction
            hit_location, hit_normal, hit_face_index, hit_distance = bvh.ray_cast(ray_start, ray_direction)
        
        if hit_location is None:
            bm.free()
            return None
        
        # Calculate drill depth
        drill_depth = (hit_location - location).length
        
        bm.free()
        
        return {
            'start_point': location,
            'direction': drill_direction,
            'depth': drill_depth,
            'world_start': obj.matrix_world @ location
        }
    
    def create_hole(self, obj, drill_data, hole_diameter):
        """Create the actual hole using boolean operations"""
        # Switch to Object mode
        bpy.context.view_layer.objects.active = obj
        if obj.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Create cylinder for boolean operation
        radius = (hole_diameter / 1000) / 2  # Convert mm to meters and get radius
        depth = drill_data['depth'] + 0.01  # Add small margin
        
        # Add cylinder
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius,
            depth=depth,
            location=drill_data['world_start']
        )
        
        cylinder = bpy.context.active_object
        cylinder.name = "DrillHole_Temp"
        
        # Align cylinder with drill direction
        drill_direction = obj.matrix_world.to_3x3() @ drill_data['direction']
        cylinder.rotation_euler = drill_direction.to_track_quat('Z', 'Y').to_euler()
        
        # Move cylinder to correct position (center it on the drill path)
        offset = drill_direction.normalized() * (depth / 2)
        cylinder.location = drill_data['world_start'] + offset
        
        # Apply boolean modifier
        bpy.context.view_layer.objects.active = obj
        modifier = obj.modifiers.new(name="DrillHole", type='BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.object = cylinder
        
        # Apply modifier
        bpy.ops.object.modifier_apply(modifier="DrillHole")
        
        # Delete temporary cylinder
        bpy.data.objects.remove(cylinder, do_unlink=True)


class VIEW3D_PT_drill_hole_panel(Panel):
    """Panel for drill hole tool"""
    bl_label = PANEL_LABEL
    bl_idname = PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = PANEL_CATEGORY
    
    def draw(self, context):
        layout = self.layout
        
        # Instructions
        box = layout.box()
        box.label(text="Instructions:", icon='INFO')
        box.label(text="1. Select target object")
        box.label(text="2. Adjust settings below")
        box.label(text="3. Position 3D cursor or")
        box.label(text="   select face/vertices")
        box.label(text="4. Click 'Drill Hole'")
        
        layout.separator()
        
        # Settings section - these directly control the Scene properties
        layout.label(text="Drill Settings:", icon='SETTINGS')
        col = layout.column(align=True)
        
        # Show the Scene properties in the UI
        col.prop(context.scene, PROP_HOLE_DIAMETER)
        col.prop(context.scene, PROP_USE_CURSOR)
        
        layout.separator()
        
        # The drill button - uses settings from above
        layout.operator(OPERATOR_ID, text="Drill Hole", icon='TOOL_SETTINGS')


def register():
    # Register Scene properties with unique names to avoid conflicts
    bpy.types.Scene.drill_tool_hole_diameter = bpy.props.FloatProperty(
        name="Hole Diameter (mm)",
        description="Diameter of the hole in millimeters",
        default=4.0,
        min=0.1,
        max=50.0
    )
    
    bpy.types.Scene.drill_tool_use_cursor = bpy.props.BoolProperty(
        name="Use 3D Cursor",
        description="Use 3D cursor position as hole center",
        default=True
    )
    
    # Register classes
    bpy.utils.register_class(MESH_OT_drill_hole)
    bpy.utils.register_class(VIEW3D_PT_drill_hole_panel)


def unregister():
    bpy.utils.unregister_class(MESH_OT_drill_hole)
    bpy.utils.unregister_class(VIEW3D_PT_drill_hole_panel)
    
    # Clean up Scene properties
    del bpy.types.Scene.drill_tool_hole_diameter
    del bpy.types.Scene.drill_tool_use_cursor


if __name__ == "__main__":
    register()