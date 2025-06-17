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
This behaviour is orrendus, because when you are close to the object and need to move it a little, it moves the object soo much much that all the screen  
 is not sufficient to move the object where you want and laso it amke you loose the visual reference of WHERE you wanted to move the object.    
It force you to zoom out, while you had zoom in exactly to have more control over the small movement you needed.   
To correct, in part, this behaviour you need to add "Increment" to the Snap.  
It will help to get the anchor to the grid so close to where we want to move the object, but sometime it does not help at all. 
  
#### Move a group of objects

When you have objects that needs to move together, like 2 pieces of wood that are glued, 

### Take an object from a file to another

Use the "Append" function. In the destination file use "Append" and select the source file.  
Select "Objects" and than object to copy.

### Link Material
I have a Material set on Object A and I want it applied to Object B. If I assign it from the drop down a new copy is created with suffix ".001", ".002" etc.  
To use the same material you need to "Link" the material.  



## Tutorials

1. Blender beginner Tutorial - Part 1
   https://www.youtube.com/watch?v=98qKfdJRzr0&ab_channel=CGFastTrack


## Plugins


