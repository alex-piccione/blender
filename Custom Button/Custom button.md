# Custom button

To add a custom button, you need a custom panel.  

Script to add the button:
```python
import bpy

class OBJECT_PT_apply_all_button(bpy.types.Panel):
    """Creates a Panel in the Object properties windows"""
    bl_label = "Quick Apply"
    bl_idname = "OBJECT_PT_apply_transformations"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    def draw(self, context):
        layout = self.layout # creates a layout to arrange elements in the panel
        #layout.label(text="Panel is active")
        #obj = context.object # get the current selected object        
        
        row = layout.row() # creates a new row in the layout   
        op = row.operator("object.transform_apply", text="Apply All Transforms")
        op.location = True
        op.rotation = True
        op.scale = True    
        
            
        
        #layout.operator("object.origin_set", text="Origin to Center").type = 'ORIGIN_CENTER_OF_MASS'
        #row.operator("object.select", text="Select Object").toggle = True
        
def register():
    bpy.utils.register_class(OBJECT_PT_apply_all_button)
    
def unregister():
    bpy.utils.unregiste_class(OBJECT_PT_apply_all_button)
        
if __name__ == "__main__" :
    register()    
```

After you run the script and you test it, you need to save it as .py file.  
Now, in Blender Edit -> Preferences -> Add-on, uset he "Install from Disk".  
  