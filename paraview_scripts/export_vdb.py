#### import the simple module from the paraview
from paraview.simple import *
import argparse
import os 
from pathlib import Path

def get_filename(export_path, step, format):
    filename = "{}/t{:08}.{}".format(export_path, step,format)
    return(filename)
    

def update_file(filename, export_path, **kwargs):
    # create a new 'XDMF Reader'
    xmf_reader = XDMFReader(FileNames=[filename]) 
    
    # read cell array status 
    xmf_reader.CellArrayStatus = xmf_reader.CellData.keys()

    # create index list of timesteps to be used
    animationScene1 = GetAnimationScene()
    timestep_list = animationScene1.TimeKeeper.TimestepValues

    # create a new 'Resample To Image' with sampling bounds and dimensions 
    resampleToImage1 = ResampleToImage(registrationName='ResampleToImage1', Input=xmf_reader)
    resampleToImage1.SamplingBounds = [kwargs["xmin"], kwargs["xmax"], kwargs["ymin"], kwargs["ymax"], kwargs["zmin"], kwargs["zmax"]] 

    resampleToImage1.UseInputBounds = 0
    resampleToImage1.SamplingDimensions = [kwargs["xdim"], kwargs["ydim"], kwargs["zdim"]]

    # update timeline for the first timestep onwards 
    UpdatePipeline(time=timestep_list[0], proxy=resampleToImage1) 

    # iterate over timesteps and save each one in different directory marked by an index
    for step, time in enumerate(timestep_list):

        # make folder for the index 
        filename = get_filename(export_path, step, format="vdb")
        print(filename)
        if os.path.exists(filename):
            continue

        print("  - Export timestep {}/{} ({})".format(step, len(timestep_list), time))

        Path(filename).mkdir(parents=True, exist_ok=True)
        exit() 

        # set time for that animation
        animationScene1.AnimationTime = time 
        
        # # set active source
        SetActiveSource(xmf_reader)

        # # set active source
        SetActiveSource(resampleToImage1)

        # save data
        output_name = filename + "/output.vdb"
        # get properties for writing 
        renderView = FindViewOrCreate('RenderView1', viewtype='RenderView')
        for name, source in GetSources().items():
            displayProp = GetDisplayProperties(source,view=renderView)
            if(displayProp.Visibility==1):
                save_data(output_name, resampleToImage1,displayProp)

"""
save data in vdb format 
"""
def save_data(output_name, resampleToImage1, displayProp):

    export_args = {}
    if displayProp.ColorArrayName[0] == "POINTS":
        export_args = {'PointDataArrays': [displayProp.ColorArrayName[1]]}
    elif displayProp.ColorArrayName[0] == "CELLS":
        export_args = {'CellDataArrays': [displayProp.ColorArrayName[1]]}
    if displayProp.ColorArrayName[1] == '':
        print("      Skipping {}".format(filename))
        return

    # generated data 
    # SaveData(output_name, proxy=resampleToImage1,
    #     ColorArrayName=['POINTS', ''],
    #     LookupTable=None,
    #     PointDataArrays=['enstrophy', 'kinetic energy', 'pressure', 'velocity', 'vtkGhostType', 'vtkValidPointMask'],
    #     CellDataArrays=['vtkGhostType'])

    # similar to export ply 
    SaveData(output_name, proxy=resampleToImage1,
        ColorArrayName=list(displayProp.ColorArrayName),
        LookupTable=displayProp.LookupTable, **export_args)
    exit() 

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--datapath", help="Path to the solution data")
    parser.add_argument("--exportpath", default="paraview_export", help="Path to export vdb files")
    args = parser.parse_args()

    if(args.datapath != None):
        filename = args.datapath
    else:
        print("Error. Enter data path")
        exit(1) 
    outputdirname = args.exportpath

    img_bounds= { 
        "xmin":-0.15,
        "xmax":0.7,
        "ymin":-0.15,
        "ymax":0.15,
        "zmin":-0.15,
        "zmax":0.15,
        "xdim":100,
        "ydim":100,
        "zdim":100
    }

    update_file(filename, outputdirname, **img_bounds)