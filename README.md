# ASiMoV-visu

This repository contains a set of tools as well as a blender addon meant to ease the render of sequence data stored in separate (`.ply`) files. 


## Blender addon

One of the limitation of Blender is its inability to import some file types as a sequence, meaning importing a new file for each frame. This addon handles this for `.ply` files as well as providing some quality of life features when rendering .blend files headlessly.

### Installation

#### pyyaml
```Bash
blender -b --python-expr "import pip; pip.main(['install', 'pyyaml', '--user'])"
```

#### Addon


### Usage


#### GUI
add screenshot


#### Headless

```Bash
blender -b file.blend --python batch_render.py -- --configfile config.yaml --exportpath blender_export --frames 1-17
```



## ParaView scripts

#### `export_ply.py`

usage:
```Bash
pvpython export_ply.py --datapath path/with/input/data --exportpath ply_export statefile.pvsm
```

This script will will load the statefile and, for every single timestep, export the visible filters to separate `.ply` files in the folder specified by `--exportpath`.



#### `export_vdb.py`


