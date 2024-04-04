
import os
import sys
import bpy
import pip

# install pyyaml
pip.main(['install', 'pyyaml', '--user'])

# install addon
addon_path = os.path.abspath(sys.argv[-1])
if addon_path.endswith(".zip"):
    bpy.ops.preferences.addon_install(filepath=addon_path, overwrite=True)
    bpy.ops.preferences.addon_enable(module='SequenceDataLoader')
    bpy.ops.wm.save_userpref()
else:
    print("Please provide the path to the addon .zip as argument")
