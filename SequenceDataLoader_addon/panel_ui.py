import bpy
from .sequence_data_loader import *

USE_YAML = True
try:
    import yaml
except ModuleNotFoundError:
    USE_YAML = False

class SequenceDataPanel(bpy.types.Panel):
    """Defines the sequence data loader panel in a 3d view tab"""
    bl_label = "Sequence Data Loader"
    bl_idname = "SEQ_DATA_LOADER_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Sequence Data Loader"
    

    def draw(self, context):
        layout = self.layout
        
        #layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        sequence_data = scene.sequence_data
        
        # Configuration
        layout.label(text="Configuration", icon="FILE")
        col = layout.column()
        col.prop(sequence_data, "config_file")
        col.enabled = USE_YAML
        
        row = layout.row(align=True)
        row.operator("sequencedata.read_config", icon="IMPORT")
        row.enabled = USE_YAML
        row.operator("sequencedata.write_config", icon="EXPORT")

        layout.separator(factor=2)

        # Timing
        layout.label(text="Timing", icon="TIME")

        col = layout.column()
        col.prop(sequence_data, "timing_interpolate")
        
        row = layout.grid_flow(columns=2, align=True)
        row.prop(sequence_data, "timing_time_start")
        row.prop(sequence_data, "timing_time_end")

        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")        

        layout.separator(factor=2)

        # Objects
        layout.label(text="Objects", icon="OBJECT_DATA")
        col = layout.column()
        for idx, item in enumerate(sequence_data.objects):

            box = layout.box()
            box.prop_search(item, "name", scene, "objects")
            box.prop(item, "path")
            split = box.split()
            split.prop(item, "shade_smooth")
            split.prop(item, "enable")
            row = box.row()
            row.operator("sequencedata.remove_object", icon="X").object_id = idx

        row = layout.row()
        row.operator("sequencedata.add_object", icon="ADD")

        layout.separator(factor=2)

        # Update
        layout.label(text="Update data", icon="FILE_REFRESH")
        row = layout.split(align=True)
        row.prop(sequence_data, "live_update")
        row.prop(scene, "frame_current")
        
        row = layout.column()
        row.scale_y = 3.0
        row.alert = (sequence_data.last_read_time != sequence_data.get_time(scene.frame_current))
        row.operator("sequencedata.load_objects", text="Load Current Frame")

        
        layout.separator(factor=2)

        # Render settings
        layout.label(text="Render settings", icon="RENDER_RESULT")
        
        col = layout.column()
        col.prop(scene.cycles, "samples")
        col.prop(scene.render, "resolution_percentage")
        col.prop(sequence_data, "export_path")

