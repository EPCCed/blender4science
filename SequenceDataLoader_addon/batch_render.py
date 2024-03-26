
import bpy
import os
import sys
import argparse
from sequence_data_loader import *

bpy.utils.register_class(ObjectDataSequence)
bpy.utils.register_class(SequenceDataLoader)
bpy.types.Scene.sequence_data = bpy.props.PointerProperty(type=SequenceDataLoader)

Scene = bpy.context.scene


def get_export_path(frame):
    """
        Generates the path where a frame is to be exported to
    """
    if RENDER_PATH:
        path = RENDER_PATH
    else:
        path = Scene.sequence_data.export_path
    
    return os.path.join(path, "export_{:08}.png".format(frame))


def render(frame):
    """
        Load the data and render a single frame
    """
    print("Render frame:", frame)
    Scene.frame_current = frame

    Scene.sequence_data.load_objects(frame)

    export_path = get_export_path(frame)
    print("Export to {}".format(export_path))

    bpy.ops.render.render()
    bpy.data.images['Render Result'].save_render(filepath=export_path)


# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--configfile", help="Render configuration file")
parser.add_argument("--renderpath", help="Path to export the renders")
parser.add_argument("--frames", help="Set of frames to render in format '1-25'")

# Parse arguments after "--"
args = parser.parse_args(args=sys.argv[sys.argv.index("--") + 1:])

if args.configfile:
    print(f"Loading config file at: {args.configfile}")
    Scene.sequence_data.config_file = args.configfile
    Scene.sequence_data.read_config()

if args.renderpath:
    RENDER_PATH = args.renderpath
else:
    RENDER_PATH = "."

if args.frames:
    FRAME_START = int(args.frames.split("-")[0])
    FRAME_END = int(args.frames.split("-")[1])
else:
    FRAME_START = Scene.frame_start
    FRAME_END = Scene.frame_end


# Render each frame
for frame in range(FRAME_START, FRAME_END+1):
    export_path = get_export_path(frame)
    export_path_tmp = export_path + ".tmp"
    # Check if render has already been done
    if os.path.exists(export_path) or os.path.exists(export_path_tmp):
        continue

    # Create empty file
    with open(export_path_tmp, 'w') as fp:
        pass

    render(frame)
    os.remove(export_path_tmp)
