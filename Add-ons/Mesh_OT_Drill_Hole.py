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

# NUOVA COSTANTE per la lunghezza massima del foro
MAX_DRILL_LENGTH_FALLBACK = 0.1 # 0.1 metri = 10 cm

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
    
    def calculate_drill_path(self, obj, drill_point_world):
        """
        Calculate drill direction and depth by raycasting through the object.
        Finds the closest surface point to drill_point_world, then raycasts from outside
        through the object to find entry and exit points.
        """
        
        # Convert drill point to object local space
        drill_point_local = obj.matrix_world.inverted() @ drill_point_world
        
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bvh = BVHTree.FromBMesh(bm)
        
        # Find the closest surface point and its normal
        # This will be our initial "entry" surface and drill direction
        # distance param is max distance to search for nearest point
        location_on_surface_local, normal_on_surface_local, face_index, distance = bvh.find_nearest(drill_point_local, 10.0) 
        
        if location_on_surface_local is None:
            bm.free()
            print("DEBUG: No surface point found near drill_point_world. Object might be empty or too far.")
            return None
        
        print(f"DEBUG: Surface point found at {location_on_surface_local}, normal: {normal_on_surface_local}")
        
        drill_direction_local = -normal_on_surface_local.normalized()
        print(f"DEBUG: drill_direction_local: {drill_direction_local}")

        # --- First Raycast: Find the exact entry point from *outside* the object ---
        # Start the ray from a point well outside the object along the normal
        # The bounding box diagonal length is a safe bet for a "large enough" distance
        bbox_max_dim = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
        # Add some margin to ensure we are definitely outside
        offset_dist = bbox_max_dim * 1.5 # 1.5 times the longest dimension
        if offset_dist < 0.1: # Ensure a minimum offset for very small objects
            offset_dist = 0.1

        ray_start_outside_local = location_on_surface_local - drill_direction_local * offset_dist
        print(f"DEBUG: ray_start_outside_local: {ray_start_outside_local}")
        
        entry_location_local, entry_normal_local, entry_face_index, entry_distance = bvh.ray_cast(
            ray_start_outside_local, drill_direction_local, offset_dist * 2 # Max distance for raycast
        )
        
        if entry_location_local is None:
            bm.free()
            print("DEBUG: Raycast for entry point failed. Object might be open or ray direction is wrong.")
            return None # Fallback to general error

        # --- Second Raycast: Find the exit point from *inside* the object ---
        # Start slightly *after* the entry point to avoid immediate re-intersection with the same face
        # This epsilon must be very small but not zero to ensure the ray doesn't hit the starting face again
        epsilon = 0.00001
        ray_start_inside_local = entry_location_local + drill_direction_local * epsilon
        
        # We need to cast a long ray to find the exit point
        # The max_dim of object is a good guess for depth
        # NON USIAMO PIÙ bbox_max_dim * 2.0 come max_ray_dist, ma il nostro MAX_DRILL_LENGTH_FALLBACK
        max_ray_dist_for_exit = MAX_DRILL_LENGTH_FALLBACK + 0.01 # Un po' più del massimo desiderato
        
        exit_location_local, exit_normal_local, exit_face_index, exit_distance = bvh.ray_cast(
            ray_start_inside_local, drill_direction_local, max_ray_dist_for_exit
        )
        
        drill_depth = 0.0 # Default if no exit found

        if exit_location_local is None:
            # Se il punto di uscita non viene trovato, usa il valore massimo del trapano (10 cm)
            print(f"DEBUG: No distinct exit point found. Object might not be manifold or ray missed. Using fallback drill length: {MAX_DRILL_LENGTH_FALLBACK:.4f}m.")
            drill_depth = MAX_DRILL_LENGTH_FALLBACK 
            # Il punto di partenza è ancora entry_location_local
        else:
            # Calcola la profondità tra il punto di ingresso e quello di uscita
            drill_depth = (exit_location_local - entry_location_local).length
            
            # Assicurati che la profondità calcolata non superi il limite massimo (10 cm)
            if drill_depth > MAX_DRILL_LENGTH_FALLBACK:
                print(f"DEBUG: Calculated depth {drill_depth:.4f}m exceeds max. Clamping to {MAX_DRILL_LENGTH_FALLBACK:.4f}m.")
                drill_depth = MAX_DRILL_LENGTH_FALLBACK

            print(f"DEBUG: Exit point: {exit_location_local}, calculated depth: {drill_depth:.4f}m")

        bm.free()
        
        # Return data in local space for the cylinder creation, and world_start for its global placement
        return {
            'start_point_local': entry_location_local, # Local space start point
            'direction_local': drill_direction_local, # Local space direction
            'depth': drill_depth,
            'world_start': obj.matrix_world @ entry_location_local # World space start point
        }
    
    def create_hole(self, obj, drill_data, hole_diameter_mm):
        """Create the actual hole using boolean operations"""
        
        # Ensure we are in object mode before creating / modifying objects
        bpy.ops.object.mode_set(mode='OBJECT')
        
        radius = (hole_diameter_mm / 1000) / 2 # Convert mm to meters and get radius
        depth = drill_data['depth'] + 0.001 # Add a tiny margin to ensure clean cut

        # Create cylinder at the world start point of the drill path
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius,
            depth=depth,
            location=drill_data['world_start'],
            vertices=16,
            enter_editmode=False # Create in Object Mode
        )
        
        cylinder = bpy.context.active_object # The newly created cylinder
        cylinder.name = "DrillHole_Temp_Cutter"
        
        # Align cylinder with drill direction
        # The cylinder is created along its local Z-axis. 
        # We need to rotate it so its Z-axis aligns with drill_data['direction_local']
        # This requires converting the local normal to a world normal for the rotation, 
        # then applying the rotation to the cylinder which is in world space.
        
        # Get the world space direction from the local space direction
        drill_direction_world = obj.matrix_world.to_3x3() @ drill_data['direction_local']
        
        # Calculate rotation from global Z-axis (cylinder default) to drill_direction_world
        # This correctly aligns the cylinder's axis
        rot_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(drill_direction_world)
        cylinder.rotation_mode = 'QUATERNION'
        cylinder.rotation_quaternion = rot_quat
        
        # Center the cylinder along its new axis.
        # The cylinder is created with its origin at its center.
        # We want the 'start_point' (entry_location_local) to be at one end of the cylinder.
        # So we move the cylinder's origin by half its depth *along its axis* from the world_start.
        # The 'start_point' is the entry location. The cylinder's center should be (start_point + direction + depth/2)
        
        # The cylinder's current location is already 'world_start'
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
            # Still try to delete cutter even if boolean fails
            bpy.data.objects.remove(cylinder, do_unlink=True)
            return
            
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