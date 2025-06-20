import bpy
import bmesh
from bpy.types import Operator, Panel
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from typing import NamedTuple

bl_info = {
    "name": "Drill Hole",
    "author": "Alessandro Piccione",
    "version": (25, 6, 19),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Tool",
    "description": "Create drill holes through objects",
    "category": "Mesh",
}

# Constants to avoid magic strings
OPERATOR_ID = "mesh.drill_hole"
PANEL_ID = "VIEW3D_PT_drill_hole"
PANEL_LABEL = "Drill Hole"
PANEL_CATEGORY = "Tool"

# Property names (with unique prefixes to avoid conflicts)
PROP_HOLE_DIAMETER = "drill_tool_hole_diameter"
PROP_HOLE_LENGTH = "drill_tool_hole_length"
PROP_USE_CURSOR = "drill_tool_use_cursor"

# COSTANT for the max length of the hole
MAX_DRILL_LENGTH = 150/1000 # 150mm = 15 cm
HOLE_CYLINDER_SEGMENTS = 16  # Number of segments for the drill hole cylinder

# Data for the Drill
class DrillData(NamedTuple):
    start_point: Vector
    direction: Vector

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
        hole_length = getattr(context.scene, PROP_HOLE_LENGTH)
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
        self.create_hole(obj, drill_data, hole_diameter, hole_length)
        
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
    
    def calculate_drill_path(self, obj, drill_point_world):
        """Calculates drill entry point and direction, in world space."""
        
        # Convert drill point to object local space
        drill_point_local = obj.matrix_world.inverted() @ drill_point_world
        
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bvh = BVHTree.FromBMesh(bm)
        
        # Find the closest surface point and its normal
        # This is the "target" surface where the drill should start
        # The '10.0' is just a max search distance for find_nearest, not the drill depth
        location_on_surface_local, normal_on_surface_local, face_index, distance = bvh.find_nearest(drill_point_local, 10.0) 
        
        if location_on_surface_local is None:
            bm.free()
            print("DEBUG: No surface point found near drill_point_world. Object might be empty or too far.")
            return None
        
        # The drill direction is the normal of the surface pointing INTO the object.
        # BVH normals point "outside". So we use the negative normal.
        drill_direction_local = -normal_on_surface_local.normalized()
        
        # --- First Raycast: Find the exact entry point from *outside* the object ---
        # We need to start our ray from a point clearly outside the object,
        # along the inverse direction of the drill (so, along the surface normal).
        bbox_max_dim = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
        offset_dist = bbox_max_dim * 1.5 # Safe distance outside
        if offset_dist < 0.1: 
            offset_dist = 0.1

        # Start outside, move inwards along the drill direction
        # The ray starts from location_on_surface_local, goes OUT along the normal, 
        # then we cast a ray back IN along the drill direction.
        ray_start_outside_local = location_on_surface_local + normal_on_surface_local * offset_dist # Go out along surface normal
        
        entry_location_local, entry_normal_local, entry_face_index, entry_distance = bvh.ray_cast(
            ray_start_outside_local, drill_direction_local, offset_dist * 2 # Cast back in along drill direction
        )
        
        if entry_location_local is None:
            bm.free()
            print("DEBUG: Raycast for entry point failed. Object might be open or ray direction is wrong.")
            return None 

        bm.free()   

        # Calculate the world space start point and direction for the drill
        return DrillData(
            entry_location_local @ obj.matrix_world, 
            drill_direction_local @ obj.matrix_world.to_3x3()
            )
            
    def create_hole(self, obj, drill_data:DrillData, hole_diameter, hole_length):
        """Create the actual hole using boolean operations"""
        
        # Ensure we are in object mode before creating / modifying objects
        bpy.ops.object.mode_set(mode='OBJECT')
        
        radius = (hole_diameter) / 2 # Convert mm to meters and get radius
        depth = (hole_length) # + 0.001 # Convert to meters and add a tiny margin to ensure clean cut

        # Create cylinder at the world start point of the drill path
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius,
            depth=depth,
            location=drill_data.start_point,
            vertices=HOLE_CYLINDER_SEGMENTS,
            enter_editmode=False # Create in Object Mode
        )
        
        cylinder = bpy.context.active_object # The newly created cylinder
        cylinder.name = "DrillHole_Temp_Cutter"
        
        # Align cylinder with drill direction
        # The cylinder is created along its local Z-axis. 
        # We need to rotate it so its Z-axis aligns with drill direction
        # then applying the rotation to the cylinder which is in world space.
               
        # Calculate rotation from global Z-axis (cylinder default) to drill_direction_world
        # This correctly aligns the cylinder's axis
        rot_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(drill_data.direction)
        cylinder.rotation_mode = 'QUATERNION'
        cylinder.rotation_quaternion = rot_quat
        
        # CeMoventer the cylinder along its new axis.
        
        # The cylinder is created with its origin at its center, that is the start point of the drill.
        # We need to offset it along its own aligned axis by half its depth 
        offset_vector = cylinder.matrix_world.to_3x3() @ Vector((0,0,1)) * (depth / 2)
        cylinder.location -= offset_vector # Subtract because we want the start of cylinder to be at world_start
        
        # Apply boolean modifier to the original object
        # Ensure original object is active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        modifier = obj.modifiers.new(name="DrillHole", type='BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.object = cylinder
        modifier.solver = 'EXACT' # 'EXACT' is generally more robust for complex geometry like holes

        # Apply modifier
        try:
            bpy.ops.object.modifier_apply(modifier="DrillHole")
        except RuntimeError as e:
            self.report({'ERROR'}, f"Failed to apply boolean modifier: {e}. Check mesh for non-manifold geometry.")
            
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
        
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Instructions:", icon='INFO')
        col.separator(factor=0.5)
        col.label(text="1. Select target object")
        col.label(text="2. Adjust settings below")
        col.label(text="3. Position 3D cursor or select faces")
        col.label(text="4. Click 'Drill Hole'")
        
        layout.separator()
        
        # Settings section - these directly control the Scene properties
        layout.label(text="Drill Settings:", icon='SETTINGS')
        col = layout.column(align=True)
        
        # Show the Scene properties in the UI
        col.prop(context.scene, PROP_USE_CURSOR)
        col.prop(context.scene, PROP_HOLE_DIAMETER, icon='MESH_UVSPHERE')
        col.prop(context.scene, PROP_HOLE_LENGTH, icon='OUTLINER_OB_MESH') #MESH_CYLINDER
        
        layout.separator()
        
        # The drill button - uses settings from above
        layout.operator(OPERATOR_ID, text="Drill Hole", icon='TOOL_SETTINGS')


def register():
    # Register Scene properties with unique names to avoid conflicts
    bpy.types.Scene.drill_tool_hole_diameter = bpy.props.FloatProperty(
        name="Hole Diameter",
        description="Diameter",
        default=4/1000, # 4mm
        min=2.0/1000,
        max=50.0/1000,
        step=5/1000,
        #soft_min=3/1000,
        soft_max=14/1000,  # soft limits for UI slider
        unit='LENGTH',
    )

    bpy.types.Scene.drill_tool_hole_length = bpy.props.FloatProperty(
        name="Hole Length",
        description="Length",
        default=MAX_DRILL_LENGTH,  # by default is a passing-by drill
        min=5/1000,  # minimum length is 5mm
        max=MAX_DRILL_LENGTH,
        step=5/1000,
        #soft_min=20/1000,  # 3cm
        #soft_max=50/1000,  # 5cm
        unit='LENGTH',
    )
    
    bpy.types.Scene.drill_tool_use_cursor = bpy.props.BoolProperty(
        name="Use 3D Cursor",
        description="Use 3D cursor position as hole center (otherwise object center will be used)",
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
    del bpy.types.Scene.drill_tool_hole_length
    del bpy.types.Scene.drill_tool_use_cursor


if __name__ == "__main__":
    register()