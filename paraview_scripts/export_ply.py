from paraview.simple import *
import os
import sys
from pathlib import Path
import argparse


def get_filename(export_path, step, name="", ext=""):
    folder = "{}/t{:08}".format(export_path, step)
    filename = os.path.join(folder, "{}.{}".format(name, ext))
    return folder, filename


def export_ply(filename, source, displayProp):

    export_args = {}
    if displayProp.ColorArrayName[0] == "POINTS":
        export_args = {'PointDataArrays': [displayProp.ColorArrayName[1]]}
    elif displayProp.ColorArrayName[0] == "CELLS":
        export_args = {'CellDataArrays': [displayProp.ColorArrayName[1]]}

    if displayProp.ColorArrayName[1] == '':
        print("      Skipping {}".format(filename))
        return

    print("      Writing {}".format(filename))
    SaveData(filename, proxy=source,
             EnableColoring=1,
             ColorArrayName=list(displayProp.ColorArrayName),
             LookupTable=displayProp.LookupTable, **export_args)
    return 


parser = argparse.ArgumentParser()

parser.add_argument("statefile", help="ParaView Statefile to process")
parser.add_argument("--datapath", help="Path to the solution data")
parser.add_argument("--exportpath", default="paraview_export", help="Path to export .ply files")

args = parser.parse_args()

state_file = args.statefile
export_path = args.exportpath

print("Loading {}".format(state_file))
kwargs = {}
if args.datapath: 
    print("Data directory: {}".format(args.datapath))
    kwargs = {"data_directory": args.datapath}

LoadState(state_file, **kwargs)
print("Export path: {}".format(export_path))

renderView = FindViewOrCreate('RenderView1', viewtype='RenderView')

animationScene = GetAnimationScene()

timestep_list = animationScene.TimeKeeper.TimestepValues

for step, time in enumerate(timestep_list):
    export_folder, _ = get_filename(export_path, step)
    if os.path.exists(export_folder):
        continue

    print("  - Export timestep {}/{} ({})".format(step, len(timestep_list), time))

    Path(export_folder).mkdir(parents=True, exist_ok=True)

    animationScene.AnimationTime = time

    for name, source in GetSources().items():
        display = GetDisplayProperties(source, view=renderView)
        if display.Visibility == 1:
            _, filename = get_filename(export_path, step, name[0], "ply")
            export_ply(filename, source, display)



