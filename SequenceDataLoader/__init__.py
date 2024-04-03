
import bpy
from .sequence_data_loader import *
from .panel_ui import *
from .batch_render import *

classes = (
    SequenceDataWriteConfig,
    SequenceDataReadConfig,
    SequenceDataAddObject,
    SequenceDataRemoveObject,
    SequenceDataLoadObjects,
    ObjectDataSequence,
    SequenceDataLoader,
    SequenceDataRender,
    SequenceDataPanel,
)

bl_info = {
    "name": "Sequence Data Loader",
    "description": "Load sequences of .ply files.",
    "author": "Sebastien Lemaire",
    "version": (0, 9, 0),
    "blender": (4, 0, 0),
    "category": "Import"
}


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.sequence_data = bpy.props.PointerProperty(type=SequenceDataLoader)
    bpy.types.Scene.sequence_data_render = bpy.props.PointerProperty(type=SequenceDataRender)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
