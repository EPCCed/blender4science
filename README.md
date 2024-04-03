# ASiMoV-visu

This repository contains a set of tools as well as a blender addon meant to ease the render of sequence data stored in separate (`.ply`) files. 


## Blender addon

One of the limitation of Blender is its inability to import some file types as a sequence, meaning importing a new file for each frame. This addon handles this for `.ply` files as well as providing some quality of life features when rendering .blend files headlessly and in parallel.

### Installation

This addon requires pyyaml when using yaml configuration files. It can be installed inside blender via pip. Alternatively, the `setup_blender.py` script handles it as well as installing the `SequenceDataLoader` blender addon.


#### Headless

Just running the script with the It can be run with headlessly with:
```
blender -b --python setup_blender.py -- path/to/SequenceDataLoader.zip
```

#### GUI

pyyaml can be installed by running the following command inside blender's python terminal:
```Python
import pip
pip.main(['install', 'pyyaml', '--user'])
```
Finally, like any addon, `SequenceDataLoader` can be installed by going in Edit>Preferences>Add-ons>Install and selecting the .zip file associated with the release


### Running

#### Headless


```Bash
blender -b file.blend --python-expr "import bpy; bpy.context.scene.sequence_data_render.render_frames()" -- --configfile config.yaml --renderpath blender_export --frames 1-17
```



## ParaView scripts

#### `export_ply.py`

usage:
```Bash
pvpython export_ply.py --datapath path/with/input/data --exportpath ply_export statefile.pvsm
```

This script will will load the statefile and, for every single timestep, export the visible filters to separate `.ply` files in the folder specified by `--exportpath`.



#### `export_vdb.py`


