# Woodworking Toolkit  
A Blender add-on that provides a set of tools to improve general 3D modeling workflow, with a focus on modeling woodworking objects and performing fast precision operations.

---

## Features
- Quick-access modeling utilities  
- Tools designed specifically for woodworking objects creation  
- Integrated panel in the **3D View > Sidebar > Woodworking** tab
- Supports Blender **4.3 and later**

## Operators

### Add Cylinder (`woodworking.add_cylinder`)
Add a cylinder with customizable diameter and length.
- **Diameter**: Y-Z axis dimension (default: 6mm, range: 1-1000mm)
- **Length**: X axis dimension (default: 2cm, range: 1-100cm)

### Add Panel (`woodworking.add_panel`)
Add a rectangular panel (cube-based) with customizable dimensions.
- **Length**: X axis dimension (default: 0.1m)
- **Width**: Y axis dimension (default: 0.02m)
- **Thickness**: Z axis dimension (default: 0.02m)

### Round Corner (`woodworking.round_corner`)
Bevel selected edges with customizable radius and smoothness.
- **Requirements**: Must be in Edit Mode with edges selected
- **Radius**: Bevel radius (default: 5mm, range: 1-50mm)
- **Segments**: Number of segments for smoothness (default: 5, range: 1-32)

### Rotate Object (`woodworking.rotate_object`)
Rotate the active object by a fixed angle around a specified axis.
- **Axis**: X, Y, or Z axis selection
- **Angle**: Rotation angle in degrees (default: 90°)
- Pre-defined buttons for ±90° rotations on each axis

### Copy Material from Last Selected (`woodworking.copy_material_from_last_selected`)
Copy materials from the last selected object to all other selected objects.
- **Requirements**: Active object must be a mesh, and at least 2 objects must be selected  

---

## Installation

Release: https://github.com/alex-piccione/blender/releases

### From ZIP (recommended)
1. Download the latest release ZIP (or generate one from this repository).  
2. In Blender, go to **Edit → Preferences → Add-ons**.  
3. Click **Install from disk**  
4. Select the ZIP file.  
5. Done

### From source directory (development)
If you want to test the local changes or build it yourself:
1. Clone this repository.  
2. Create the valid ZIP of the add-on with this Bash script (it uses Windows Powershell for zip):
```bash 
create_zip.sh
``` 
3. In Blender, go to **Edit → Preferences → Add-ons**.  
4. Click **Install from disk**  
5. Select the ZIP file.  
6. Done

**Note**  
If it fails, with this error:
> register_class(...): already registered as a subclass 'WOODWORKING_PT_panel'

you need to delete the existing add-on; go to the Blender folder and delete the add-on folder from the _extensions_ folder.  
