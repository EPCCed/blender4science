
import bpy
import os
import argparse
import yaml
import re
from pathlib import Path



def get_time(frame):
    """
        Get timestep from frame. Timestep relates to the input data time while frame is a Blender concept
    """
    frame_start = Scene.frame_start
    frame_end = Scene.frame_end
    time_start = config['time']['time_start']
    time_end = config['time']['time_end']
    if config['time']['interpolate']:
        return (time_end - time_start)*(frame - frame_start)/(frame_end - frame_start) + time_start
    else:
        return (frame - frame_start) + time_start
    

def get_data_path(template_path, time):
    """
        Get the path to the data file from a template stored in the config file. The template has XXXXX as a time placeholder
    """
    time_string_size = len(re.search("X+", template_path).group())
    path = template_path.replace(time_string_size*"X", "{0:0{1}}".format(time, time_string_size))

    if DATA_PATH:
        return os.join(DATA_PATH, path)
    else:
        return path

def load_data(frame):
    """
        Load data
    """
    time = get_time(frame)
    object_list = []

    for object in config['objects']:
        original_object = bpy.data.objects[object['name']]
        path = get_data_path(object['path'], time)

        imported_object = bpy.ops.wm.ply_import(filepath=path)

        if object['shade_smooth']:
            for f in imported_object.data.polygons:
                f.use_smooth = True

        # Copy materials to imported object
        for material in original_object.data.materials.values():
            imported_object.data.materials.append(material)

        imported_object.data.materials.values()
        original_object.hide_render = True
        object_list.append(imported_object)

    return object_list

def cleanup_objects(object_list):
    """
        Delete objects given in argument
    """
    for object in object_list:
        bpy.data.objects.remove(object, do_unlink=True)


def set_render_options():
    """
        Set render options from the config file
    """
    if config['render']['samples']:
        Scene.cycles.max_samples = config['render']['samples']

    if config['render']['device']:
        Scene.cycles.device = config['render']['device']

    if config['render']['resolution_percentage']:
        Scene.cycles.render.resolution_percentage = config['render']['resolution_percentage']


def get_export_path(frame):
    """
        Generates the path where a frame is to be exported to
    """
    if EXPORT_PATH:
        path = EXPORT_PATH
    else:
        path = config['render']['export_path']
    
    return os.path.join(path, "export_{:08}.png".format(frame))


def render(frame):
    """
        Load the data and render a single frame
    """
    print("Render frame:", frame)
    set_render_options()
    Scene.frame_current = frame

    imported_object_list = load_data(frame)
    export_path = get_export_path(frame)
    print("Export to {}".format(export_path))

    bpy.ops.render.render()
    bpy.data.images['Render Result'].save_render(filepath=export_path)

    cleanup_objects(imported_object_list)


Scene = bpy.data.scenes[0]

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("configfile", help="Render configuration file")
parser.add_argument("--datapath", help="Path to the solution data")
parser.add_argument("--renderpath", help="Path to export the renders")
parser.add_argument("--frames", help="Set of frames to render in format '1-25'")

args = parser.parse_args()


config_file = args.configfile

with open(config_file, 'r') as yaml_file:
    config = yaml.safe_load(yaml_file)

EXPORT_PATH = args.exportpath
DATA_PATH = args.datapath


if args.frames:
    FRAME_START = args.frames.split("-")[0]
    FRAME_END = args.frames.split("-")[1]
else:
    FRAME_START = Scene.frame_start
    FRAME_END = Scene.frame_end


# Render each frame
for frame in range(FRAME_START, FRAME_END+1):
    export_path = get_export_path(frame)
    # Check if render has already been done
    if os.path.exists(export_path):
        continue

    # Create empty file
    with open(export_path, 'w') as fp:
        pass

    render(frame)