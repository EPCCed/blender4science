
import bpy
from .sequence_data_loader import *
from .panel_ui import *


bl_info = {
    "name": "Sequence Data Loader",
    "description": "Load a sequence of objects from .PLY files",
    "author": "Sebastien Lemaire",
    "version": (0, 9, 0),
    "blender": (4, 0, 0),
    "category": "Import"
}



def register():
    bpy.app.handlers.frame_change_pre.append(load_object_on_frame_change)
    bpy.utils.register_class(SequenceDataWriteConfig)
    bpy.utils.register_class(SequenceDataReadConfig)
    bpy.utils.register_class(SequenceDataAddObject)
    bpy.utils.register_class(SequenceDataRemoveObject)
    bpy.utils.register_class(SequenceDataLoadObjects)
    
    bpy.utils.register_class(ObjectDataSequence)
    bpy.utils.register_class(SequenceDataLoader)
    bpy.types.Scene.sequence_data = bpy.props.PointerProperty(type=SequenceDataLoader)    
    
    bpy.utils.register_class(SequenceDataPanel)


def unregister():
    bpy.app.handlers.frame_change_pre.remove(load_object_on_frame_change) 
    bpy.utils.unregister_class(SequenceDataWriteConfig)    
    bpy.utils.unregister_class(SequenceDataReadConfig)
    bpy.utils.unregister_class(SequenceDataAddObject)
    bpy.utils.unregister_class(SequenceDataRemoveObject)
    bpy.utils.unregister_class(SequenceDataLoadObjects)
    
    bpy.utils.unregister_class(SequenceDataLoader)
    bpy.utils.unregister_class(ObjectDataSequence)
    bpy.utils.unregister_class(SequenceDataPanel)

if __name__ == "__main__":
    register()
       