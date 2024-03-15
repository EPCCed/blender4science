#### import the simple module from the paraview
from paraview.simple import *
import os 
from pathlib import Path

def get_filename(export_path, step, name="", ext=""):
    folder = "{}/t{:08}".format(export_path, step)
    filename = os.path.join(folder, "{}.{}".format(name, ext))
    return folder, filename

def update_file(filename, output_name, **kwargs):
    # create a new 'XDMF Reader'
    sandiasolxmf = XDMFReader(registrationName='Sandia.sol.xmf', FileNames=[filename])
    sandiasolxmf.CellArrayStatus = ['enstrophy', 'kinetic energy', 'pressure', 'velocity']
    # sandiasolxmf.GridStatus = ['Mesh', 'Mesh[10]', 'Mesh[11]', 'Mesh[12]', 'Mesh[13]', 'Mesh[14]', 'Mesh[15]', 'Mesh[16]', 'Mesh[17]', 'Mesh[18]', 'Mesh[19]', 'Mesh[1]', 'Mesh[20]', 'Mesh[21]', 'Mesh[22]', 'Mesh[23]', 'Mesh[24]', 'Mesh[25]', 'Mesh[26]', 'Mesh[27]', 'Mesh[28]', 'Mesh[29]', 'Mesh[2]', 'Mesh[30]', 'Mesh[31]', 'Mesh[32]', 'Mesh[33]', 'Mesh[34]', 'Mesh[35]', 'Mesh[36]', 'Mesh[37]', 'Mesh[38]', 'Mesh[39]', 'Mesh[3]', 'Mesh[40]', 'Mesh[41]', 'Mesh[42]', 'Mesh[43]', 'Mesh[44]', 'Mesh[45]', 'Mesh[46]', 'Mesh[47]', 'Mesh[48]', 'Mesh[49]', 'Mesh[4]', 'Mesh[50]', 'Mesh[51]', 'Mesh[5]', 'Mesh[6]', 'Mesh[7]', 'Mesh[8]', 'Mesh[9]']
    
    # create a new 'Resample To Image'
    resampleToImage1 = ResampleToImage(registrationName='ResampleToImage1', Input=sandiasolxmf)
    # resampleToImage1.SamplingBounds = [-0.15000000596046448, 0.6000000238418579, -0.15000000596046448, 0.15000000596046448, -0.15000000596046448, 0.15000000596046448]

    resampleToImage1.SamplingBounds = [kwargs["xmin"], kwargs["xmax"], kwargs["ymin"], kwargs["ymax"], kwargs["zmin"], kwargs["zmax"]] 
    # get animation scene
    animationScene1 = GetAnimationScene()

    # get list of timesteps
    timestep_list = animationScene1.TimeKeeper.TimestepValues
    export_path="/home/shrey/Coding/AppDev/CCS/output"
    # create index list of timesteps to be used
    print(timestep_list)

    # test timestep list
    timestep_list = [1e-05, 0.001]

    for step, time in enumerate(timestep_list):
        export_folder, _ = get_filename(export_path, step)
        print(export_folder)
        if os.path.exists(export_folder):
            continue
        print("  - Export timestep {}/{} ({})".format(step, len(timestep_list), time))

        Path(export_folder).mkdir(parents=True, exist_ok=True)

        animationScene1.AnimationTime = time
        
        UpdatePipeline(time=time, proxy=sandiasolxmf)

        UpdatePipeline(time=time, proxy=resampleToImage1)

        # set active source
        SetActiveSource(sandiasolxmf)

        # set active source
        SetActiveSource(resampleToImage1)

        # save data
        output_name = export_folder + "/output.vdb"
        save_data(output_name, resampleToImage1)

    exit() 

    # update animation scene based on data timesteps
    animationScene1.UpdateAnimationUsingDataTimeSteps()

    UpdatePipeline(time=1e-05, proxy=sandiasolxmf)


    UpdatePipeline(time=1e-05, proxy=resampleToImage1)

    # set active source
    # SetActiveSource(sandiasolxmf)

    # set active source
    SetActiveSource(resampleToImage1)

    save_data(output_name, resampleToImage1)

def save_data(output_name, resampleToImage1):

    SaveData(output_name, proxy=resampleToImage1, PointDataArrays=['enstrophy', 'kinetic energy', 'pressure', 'velocity', 'vtkGhostType', 'vtkValidPointMask'],
        CellDataArrays=['vtkGhostType'])

if __name__ == '__main__':
    filename = "/home/shrey/Coding/AppDev/CCS/sol_data/Sandia.sol.xmf"
    outputname = "/home/shrey/Coding/AppDev/CCS/output/output.vdb"
    img_bounds= { 
        "xmin":-0.15,
        "xmax":0.15,
        "ymin":-0.15,
        "ymax":0.15,
        "zmin":-0.15,
        "zmax":0.15
    }
    update_file(filename, outputname, **img_bounds)