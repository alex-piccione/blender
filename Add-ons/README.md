# Add-On

An add-on is simply an installed Python script.  
Edit -> Preferences (CTRL ,) -> Add-ons.  
On the top right menu you can select "Install from Disk..." .  

``import bpy``  is required to add the Python library for Blender.  


## Package add-on

For a single file add-on you just need to import it as it is.  
For a package add-on you need to import the compressed folder that commonly contains _init.py_, _ui.py_ and _operators.py_.  
The zip should contain the full folder, not only the files.  


## Sources

0. Blender doc: https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html
0. https://blog.cg-wire.com/blender-addon-ui-scripting-guide


# Python setup

## Virtual environment (for development tools only)

Create the virtual environment (only once):

    python -m venv .venv_woodworking

Activate it:

    . .venv_woodworking/Scripts/activate



## Blender Python modules (bpy, bmesh)

`bpy` and `bmesh` are **provided by Blender itself**  
They are **not installed via pip**.

To get autocomplete and type checking in the virtual environment,
install Blender Python *stubs*:

    pip install fake-bpy-module