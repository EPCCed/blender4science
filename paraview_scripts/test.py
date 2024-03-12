#### import the simple module from the paraview
from paraview.simple import *
import pyopenvdb as vdb
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'XDMF Reader'
sandiasolxmf = XDMFReader(registrationName='Sandia.sol.xmf', FileNames=['/home/shrey/Coding/AppDev/CCS/sol_data/Sandia.sol.xmf'])
sandiasolxmf.CellArrayStatus = ['enstrophy', 'kinetic energy', 'pressure', 'velocity']
sandiasolxmf.GridStatus = ['Mesh', 'Mesh[10]', 'Mesh[11]', 'Mesh[12]', 'Mesh[13]', 'Mesh[14]', 'Mesh[15]', 'Mesh[16]', 'Mesh[17]', 'Mesh[18]', 'Mesh[19]', 'Mesh[1]', 'Mesh[20]', 'Mesh[21]', 'Mesh[22]', 'Mesh[23]', 'Mesh[24]', 'Mesh[25]', 'Mesh[26]', 'Mesh[27]', 'Mesh[28]', 'Mesh[29]', 'Mesh[2]', 'Mesh[30]', 'Mesh[31]', 'Mesh[32]', 'Mesh[33]', 'Mesh[34]', 'Mesh[35]', 'Mesh[36]', 'Mesh[37]', 'Mesh[38]', 'Mesh[39]', 'Mesh[3]', 'Mesh[40]', 'Mesh[41]', 'Mesh[42]', 'Mesh[43]', 'Mesh[44]', 'Mesh[45]', 'Mesh[46]', 'Mesh[47]', 'Mesh[48]', 'Mesh[49]', 'Mesh[4]', 'Mesh[50]', 'Mesh[51]', 'Mesh[5]', 'Mesh[6]', 'Mesh[7]', 'Mesh[8]', 'Mesh[9]']

# get animation scene
animationScene1 = GetAnimationScene()

# get the time-keeper
timeKeeper1 = GetTimeKeeper()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

UpdatePipeline(time=1e-05, proxy=sandiasolxmf)

# create a new 'Resample To Image'
resampleToImage1 = ResampleToImage(registrationName='ResampleToImage1', Input=sandiasolxmf)
resampleToImage1.SamplingBounds = [-0.15000000596046448, 0.6000000238418579, -0.15000000596046448, 0.15000000596046448, -0.15000000596046448, 0.15000000596046448]

UpdatePipeline(time=1e-05, proxy=resampleToImage1)

# set active source
SetActiveSource(sandiasolxmf)

# set active source
SetActiveSource(resampleToImage1)

# Properties modified on resampleToImage1
resampleToImage1.UseInputBounds = 0

# Properties modified on resampleToImage1
resampleToImage1.SamplingBounds = [-0.15000000596046448, 0.6000000238418579, -0.15000000596046448, 0.15000000596046448, -0.15000000596046448, 0.5]

# save data
# SaveData('/home/shrey/Coding/AppDev/CCS/output.vdb', proxy=resampleToImage1, ColorArrayName=['POINTS', ''],
#     LookupTable=None,
#     PointDataArrays=['enstrophy', 'kinetic energy', 'pressure', 'velocity', 'vtkGhostType', 'vtkValidPointMask'],
#     CellDataArrays=['vtkGhostType'])
# <source lang="python"> from paraview.simple import *

# Specifying the source explicitly
# writer= CreateWriter("filename.vdb",sandiasolxmf)

# Using the active source
writer= CreateWriter("filename.vdb")

# Now one change change the ivars on the writer
# To do the actual writing, use:
writer.UpdatePipeline()
# SaveData('/home/shrey/Coding/AppDev/CCS/output.vdb', proxy=resampleToImage1, ArrayName='') 


# save data in vtk format 
# SaveData('/home/shrey/Coding/AppDev/CCS/gui2.vtk', proxy=resampleToImage1, PointDataArrays=['enstrophy', 'kinetic energy', 'pressure', 'velocity', 'vtkGhostType', 'vtkValidPointMask'],
#     CellDataArrays=['vtkGhostType'])

# convert vtk to vdb format 

# # save data
# SaveData('/home/shrey/Coding/AppDev/CCS/output.pvd', proxy=resampleToImage1, PointDataArrays=['enstrophy', 'kinetic energy', 'pressure', 'velocity', 'vtkGhostType', 'vtkValidPointMask'],
#     CellDataArrays=['vtkGhostType'])

# # save data
# SaveData('/home/shrey/Coding/AppDev/CCS/gui3.json', proxy=resampleToImage1, ArrayName='')