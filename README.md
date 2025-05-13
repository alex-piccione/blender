# Blender

Scripts and tips for Blender 3D program.  
Docs: https://docs.blender.org/manual/en/latest/search.html?q=grid&check_keywords=yes&area=default

## Settings

https://docs.blender.org/manual/en/latest/search.html?q=grid&check_keywords=yes&area=default

### Set Grid to 1mm
Prooperties -> Unit -> Metric  
Prooperties -> Unit -> Grid -> Millimeters

Viewport Overlays -> Scale: 0.001

## Shortcuts

"Add": SHIFT + A
"n": shows the Transformation panel (Roration, Location, Scale, Dimensions)
TAB: switch between Objewct and Edit mode


## Tips

### Create a parallelepipede

"Add" -> Mesh.Plane  
"n" -> show vakues, set X and Y val-ues.  
Extrude -> select Z and enter the value


### Apply Transformations
When you resize and/or rotate an object this transformation become part of the object itself and the values are not "0".  
To reset teh values to "0" you need to "Apply" these transformation.  
_Object_ -> _Apply_ -> _All Transformations_  (CTRL + A, All)

### Set Origin point on a Vertex

Is not possible to se teh pivot point directly on a vertex.  
(with version 4.4 is only possible trought a plugin)  
- Go in Edit mode and select the vertex we want to use
- Right click on the Vertex and select _Snap_ -> _Cursor to selected_
- Move to Object mode and select _Object_ -> _Set Origin_ -> _Origin to 3D Cursor_ 

### Move Objects

When you want to move an object and it is selected, clicking "G" will initially move the object to have its Origin where the cursor is in that moment.  
This behaviour is orrendus, because when you are close to the object and need to move it a little, it moveds the object soo much much that all the screen is not sufficient to move the object where you want.  
It force you to zoom out, while you had zoom in exactly to have more control over the small movement you needed.   
To correct this behaviour you need to add "Increment" to the Snap.  

### Take an object from a file to another

Use the "Append" function. In the destination file use "Append" and select the source file.  
Select "Objects" and than object to copy.

## Tutorials

1. Blender beginner Tutorial - Part 1
   https://www.youtube.com/watch?v=98qKfdJRzr0&ab_channel=CGFastTrack


## Plugins


