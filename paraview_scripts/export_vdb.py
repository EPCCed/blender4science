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
    
    # create index list of timesteps to be used
    animationScene1 = GetAnimationScene()
    timestep_list = animationScene1.TimeKeeper.TimestepValues

    # create a new 'Resample To Image' with sampling bounds and dimensions 
    resampleToImage1 = ResampleToImage(registrationName='ResampleToImage1', Input=xmf_reader)

    format="vdb"
    # dynamic selection of input bounds 
    if(kwargs!=None):
        
        resampleToImage1.UseInputBounds = 0
        resampleToImage1.SamplingBounds = [kwargs["xmin"], kwargs["xmax"], kwargs["ymin"], kwargs["ymax"], kwargs["zmin"], kwargs["zmax"]] 
        resampleToImage1.SamplingDimensions = [kwargs["xdim"], kwargs["ydim"], kwargs["zdim"]]
    else: 
        resampleToImage1.UseInputBounds = 1

    # update timeline for the first timestep onwards 
    UpdatePipeline(time=timestep_list[0], proxy=resampleToImage1) 

    # iterate over timesteps and save each one in different directory marked by an index
    for step, time in enumerate(timestep_list):

        output_filename = get_filename(export_path, step,format)
        if os.path.isfile(output_filename):
            continue 

        if os.path.isdir(output_filename):
            print(f"Error, {output_filename} can't be a directory.") 
            continue  

        print("  - Export timestep {}/{} ({})".format(step, len(timestep_list), time))

        # set time for that animation
        animationScene1.AnimationTime = time 

        save_data(output_filename, resampleToImage1)

"""
save data in vdb format 
"""
def save_data(output_name, resampleToImage1):

    array_vals = resampleToImage1.PointData.keys()
    cell_vals= resampleToImage1.CellData.keys() 
    SaveData(output_name, proxy=resampleToImage1,
             LookupTable=None, 
             PointDataArrays=array_vals,
             CellDataArrays=cell_vals
    ) 

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