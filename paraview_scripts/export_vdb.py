#### import the simple module from the paraview
from paraview.simple import *
import argparse
import os
import sys 
from pathlib import Path

def get_filename(export_path, step, format):
    """
    get_filename outputs updated filename based on timestep.

    :param export_path: directory for the output files 
    :param step: index of the timestep
    :param format: file extension for the output
    """ 
    filename = "{}/t{:08}.{}".format(export_path, step,format)
    return(filename)
    

def update_file(filename, export_path, samplingBounds, samplingDimensions, cellSizes, **kwargs):
    """
    update_file reads in the xmf input file, implements a sampling filter and then outputs the 
    resultant data in the default openvdb format. It outputs a different file for each timestep.

    :param filename: path for the input xmf file  
    :param export_path: directory for the output files 
    :param samplingBounds: list of max and min bounds in each dimensions for paraview in format: [xmax, xmin, ymax, ymin, zmax, zmin]. 
        This can be null in which case paraview will set default ones.
    :param samplingDimensions: list of image dimensions for paraview in format: [x_dim, y_dim, z_dim]. 
        This can be null but then cellSizes will need to be populated
    :param cellSizes: list of cell sizes in all dimensions for paraview in format: [x, y, z]
    """ 
    # create a new 'XDMF Reader'
    xmf_reader = XDMFReader(FileNames=[filename]) 
    
    # create index list of timesteps to be used
    animationScene1 = GetAnimationScene()
    timestep_list = animationScene1.TimeKeeper.TimestepValues

    # create a new 'Resample To Image' with sampling bounds and dimensions 
    resampleToImage1 = ResampleToImage(registrationName='ResampleToImage1', Input=xmf_reader)

    # chose file extension for output.
    format="vdb"
    if kwargs and ("format" in kwargs):
            format=kwargs["format"]

    if samplingBounds != None:
        resampleToImage1.UseInputBounds = 0
        resampleToImage1.SamplingBounds = samplingBounds 
    else: 
        resampleToImage1.UseInputBounds = 1 # use paraview's default sampling bounds 

        # obtain samplingDimensions from cell sizes or directly from arguments
        if samplingDimensions == None:
            samplingDimensions = [] 
            if cellSizes != None :
                for i in range(len(cellSizes)):
                    samplingDimensions.append(abs(resampleToImage1.SamplingBounds[i+1] - resampleToImage1.SamplingBounds[i])/cellSizes[i])
            else:
                raise Exception("Need either cell sizes or sampling dimensions. Both can't be empty.")
        else:
            resampleToImage1.SamplingDimensions = samplingDimensions 

    # update timeline for the first timestep onwards 
    UpdatePipeline(time=timestep_list[0], proxy=resampleToImage1) 

    # iterate over timesteps and save each one in different directory marked by an index
    for step, time in enumerate(timestep_list):

        output_filename = get_filename(export_path, step,format)
        if os.path.isfile(output_filename):
            continue 

        if os.path.isdir(output_filename):
            raise Exception(f"Error, {output_filename} can't be a directory.")

        print("  - Export timestep {}/{} ({})".format(step, len(timestep_list), time))

        # set time for that animation
        animationScene1.AnimationTime = time 

        save_data(output_filename, resampleToImage1)

def save_data(output_name, resampleToImage1):
    """
    save_data saves the output of the resampleToImage1 filter to a file.

    :param output_name: path for the output file
    :param resampleToImage1: paraview filter object
    """
    array_vals = resampleToImage1.PointData.keys()
    cell_vals= resampleToImage1.CellData.keys() 
    SaveData(output_name, proxy=resampleToImage1,
             LookupTable=None, 
             PointDataArrays=array_vals,
             CellDataArrays=cell_vals
    ) 

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--datapath", required=True, help="Path to the solution data")
    parser.add_argument("--exportpath", default="paraview_export", help="Path to export vdb files")
    args = parser.parse_args()

    samplingBounds = None
    samplingDimensions = None
    cellSizes = [100,100,100]
     
    update_file(args.datapath, args.exportpath, samplingBounds, samplingDimensions, cellSizes)