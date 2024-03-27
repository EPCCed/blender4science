
import bpy
import os
import sys
import argparse
from sequence_data_loader import *

bpy.utils.register_class(ObjectDataSequence)
bpy.utils.register_class(SequenceDataLoader)
bpy.types.Scene.sequence_data = bpy.props.PointerProperty(type=SequenceDataLoader)

Scene = bpy.context.scene


def get_export_path(frame=None):
    """
    Returns the path where a frame is to be exported to

    :param frame: frame number to get the path of
    """
    if RENDER_PATH:
        path = RENDER_PATH
    else:
        path = Scene.sequence_data.export_path
    
    if frame:
        return os.path.join(path, "export_{:08}.png".format(frame))
    else:
        return path


def render(frame):
    """
    Load the data and render a single frame

    :param frame: frame number to render
    """
    Scene.sequence_data.live_update = False

    print("Render frame:", frame)
    Scene.frame_current = frame

    Scene.sequence_data.load_objects(frame)

    export_path = get_export_path(frame)
    print("Export to {}".format(export_path))

    bpy.ops.render.render()
    bpy.data.images['Render Result'].save_render(filepath=export_path)


# Parse command line arguments
parser = argparse.ArgumentParser(description="""When called by a blender instance, renders a set of frames 
                                 by first importing the corresponding sequence data objects. 
                                 It also handles running multiple instances concurently by rendering each frame only once.""")
parser.add_argument("--configfile", help="File to read the configuration from, if absent setting stored in the .blend file are used. Requires pyyaml lib installed inside blender.")
parser.add_argument("--renderpath", help="Path where renders are to be exported, supresed the config file render/export_path parameter.")
parser.add_argument("--frames", help="Range of frame to render, should be in format '1-17'. If absent, using the frame range inside the .blend file.")

# Parse arguments after "--"
args = parser.parse_args(args=sys.argv[sys.argv.index("--") + 1:])

if args.configfile:
    print(f"Loading config file at: {args.configfile}")
    Scene.sequence_data.config_file = args.configfile
    Scene.sequence_data.read_config()

if args.renderpath:
    RENDER_PATH = args.renderpath
else:
    RENDER_PATH = None

if args.frames:
    FRAME_START = int(args.frames.split("-")[0])
    FRAME_END = int(args.frames.split("-")[1])
else:
    FRAME_START = Scene.frame_start
    FRAME_END = Scene.frame_end

# Create export folder
export_folder = get_export_path()
if not os.path.exists(export_folder):
    os.makedirs(export_folder)

# Render each frame
for frame in range(FRAME_START, FRAME_END+1):
    export_path = get_export_path(frame)
    export_path_tmp = export_path + ".tmp"
    # Check if render has already been done
    if os.path.exists(export_path) or os.path.exists(export_path_tmp):
        continue

    # Create empty temporary file
    with open(export_path_tmp, 'w') as fp:
        pass

    render(frame)
    os.remove(export_path_tmp)
