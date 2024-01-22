# Meeting Minutes

## 2024-01-22

- How are we doing on hardware specs?
  - **SL**: working on assessment of memory requirements, testing rendering of Q-criterion isosurface
    from 25M cell mesh, duplicated 28\times requires < 0.5GB of RAM in Blender
  - **SL**: we should also look at requirements for volumetric renderings using OpenVDB, for this the
    ParaView export required > 16 GB of RAM
    - otherwise 24GB VRAM cards should be sufficient
    - can we do decimation in OpenVDB (tree-based data structure)?
  - **SL**: the ParaView \rightarrow Blender can also be done using =.ply= files, these are binary (=.x3d= are ASCII)
    giving: smaller files, parallel I/O and faster import times
    - task to optimise the Blender import may no longer be necessary
- Discussion of task farm design
  - Initial design:
    1) Farm accepts rendering requests as input, adding to a queue
       - Blender script
       - associated =.x3d/.ply= or OpenVDB files
       - **SL**: to avoid reloading/startup time we should have each task maintain an open Blender
         instance. A potential solution is to have each Blender script (Python) run through every
         rendering in the task, creating a lock file for each frame, this will allow "dynamic" work
         allocation
         - project should develop a Python library/module to facilitate writing these Blender
           scripts
       - **PB**: could we use SLURM to queue the tasks?
    2) Tasks launch Blender on a first-come, first-served basis
    3) On task completion, move rendering to long-term (slow) storage
       - **SL**: rendered outputs (=.png=, /etc./) are small enough that writing direct to long-term storage
         is unlikely to be a bottleneck
         - still useful to have fast storage tier for import...
- **TODO:**
  - Start a gitlab for the project
  - **SL**: continue looking into RAM requirements from OpenVDB renderings
  - **PB**: writeup specification for task farm
- **DONM**: TBD, consider merging with regular CCS call?
