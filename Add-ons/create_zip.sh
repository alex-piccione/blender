#!/bin/bash
# Create a ZIP file with the add-on usable in Blender

# Create a backup of manifest
cp "./WoodworkingToolkit/blender_manifest.toml" "./WoodworkingToolkit/blender_manifest.toml.bak"

# Replace the version in the manifest
sed -i 's/__VERSION__/0.0.0/g' "./WoodworkingToolkit/blender_manifest.toml"

# create the ZIP archive of the add-on
powershell Compress-Archive -Path ./WoodworkingToolkit -DestinationPath ./woodworking_toolkit-0.0.0.zip -Force

# Restore the manifest from backup
cp "./WoodworkingToolkit/blender_manifest.toml.bak" "./WoodworkingToolkit/blender_manifest.toml"
rm "./WoodworkingToolkit/blender_manifest.toml.bak"