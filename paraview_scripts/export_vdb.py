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
    

def update_file(filename, export_path, samplingBounds, samplingDimensions, cellSize, **kwargs):
    """
    update_file reads in the xmf input file, implements a sampling filter and then outputs the 
    resultant data in the default openvdb format. It outputs a different file for each timestep.

    :param filename: path for the input xmf file  
    :param export_path: directory for the output files 
    :param samplingBounds: list of max and min bounds in each dimensions for paraview in format: [xmax, xmin, ymax, ymin, zmax, zmin]. 
        This can be null in which case paraview will set default ones.
    :param samplingDimensions: list of image dimensions for paraview in format: [x_dim, y_dim, z_dim]. 
        This can be null but then cellSizes will need to be populated
    :param cellSize: Cell size for all dimensions for paraview
    """ 
    print("reading ", filename)
    # create a new 'XDMF Reader'
    if filename.endswith("xdmf"):
        reader = XDMFReader(FileNames=[filename]) 
    elif filename.endswith("vtu"):
        reader = XMLUnstructuredGridReader(FileName=[filename])
    else:
        file_list = os.listdir(filename)
        file_list.sort()
        file_list = [os.path.join(filename, x) for x in file_list]
        reader = XMLUnstructuredGridReader(FileName=file_list)

    
    # create index list of timesteps to be used
    animationScene1 = GetAnimationScene()
    timeKeeper = GetTimeKeeper()
    #jtimestep_list = animationScene1.TimeKeeper.TimestepValues
    timestep_list = timeKeeper.TimestepValues

    # create a new 'Resample To Image' with sampling bounds and dimensions 
    resampleToImage1 = ResampleToImage(registrationName='ResampleToImage1', Input=reader)

    # chose file extension for output.
    format = "vdb"
    if kwargs and ("format" in kwargs):
            format = kwargs["format"]

    if samplingBounds:
        resampleToImage1.UseInputBounds = 0
        resampleToImage1.SamplingBounds = samplingBounds 
    else: 
        resampleToImage1.UseInputBounds = 1 # use paraview's default sampling bounds 

    # obtain samplingDimensions from cell sizes or directly from arguments
    if not samplingDimensions:
        samplingDimensions = [] 
        if cellSize:
            samplingBounds = resampleToImage1.SamplingBounds
            samplingDimensions = [ int((samplingBounds[2*i+1] - samplingBounds[2*i])/cellSize) for i in range(3) ]
        else:
            raise Exception("Need either cell sizes or sampling dimensions. Both can't be empty.")

    print("Sampling dimensions: ", samplingDimensions)
    resampleToImage1.SamplingDimensions = samplingDimensions 

    # update timeline for the first timestep onwards 
    UpdatePipeline(time=timestep_list[0], proxy=resampleToImage1) 

    # iterate over timesteps and save each one in different directory marked by an index
    for step, time in enumerate(timestep_list):

        output_filename = get_filename(export_path, step,format)
        output_filename_tmp = output_filename + "tmp"
        if os.path.isfile(output_filename) or os.path.isfile(output_filename_tmp):
            continue 

        # Create empty temporary file
        with open(output_filename_tmp, 'w') as fp:
            pass

        print("  - Export timestep {}/{} ({})".format(step, len(timestep_list), time))

        # set time for that animation
        animationScene1.AnimationTime = time 

        UpdatePipeline(time=time, proxy=resampleToImage1)

        save_data(output_filename, resampleToImage1)
        os.remove(output_filename_tmp)

def save_data(output_name, resampleToImage1):
    """
    save_data saves the output of the resampleToImage1 filter to a file.

    :param output_name: path for the output file
    :param resampleToImage1: paraview filter object
    """
    array_vals = resampleToImage1.PointData.keys()
    cell_vals = resampleToImage1.CellData.keys() 
    SaveData(output_name, proxy=resampleToImage1,
             LookupTable=None, 
             PointDataArrays=array_vals,
             CellDataArrays=cell_vals
             ) 

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", required=True, help="Path to the solution data")
    parser.add_argument("--export-path", default="paraview_export", help="Path to export vdb files")
    parser.add_argument("--sampling-bounds", help="Bounds of the box to export, comma separated list of values xmin,xmax,ymin...")
    parser.add_argument("--sampling-dims", help="Number of cells in x, y and z")
    parser.add_argument("--cell-size", help="Size of each cell (to use instead of --sampling-dims)")
    args = parser.parse_args()

    samplingDimensions = None
    samplingBounds = None
    cellSize = None
    if args.sampling_bounds:
        samplingBounds = [ float(x) for x in args.sampling_bounds.split(',') ]

    if args.sampling_dims:
        samplingDimensions = [ int(x) for x in args.sampling_dims.split(',') ]

    if args.cell_size:
        cellSize = float(args.cell_size)

    # create export directory if it doesn't exist
    Path(args.export_path).mkdir(parents=True, exist_ok=True) 

    update_file(args.data_path, args.export_path, samplingBounds, samplingDimensions, cellSize)
