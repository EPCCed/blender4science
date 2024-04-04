import bpy
import os
import re

USE_YAML = True
try:
    import yaml
except ModuleNotFoundError:
    USE_YAML = False


def enable_live_update(self, context):
    if context.scene.sequence_data.live_update:
        bpy.app.handlers.frame_change_pre.append(load_object_on_frame_change)
    elif load_object_on_frame_change in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(load_object_on_frame_change)


def load_object_on_frame_change(scene):
    """Load objects at current frame if `live_update` is enabled"""
    if scene.sequence_data.live_update:
        scene.sequence_data.load_objects(scene.frame_current)


class SequenceDataLoadObjects(bpy.types.Operator):
    """Load new sets of objects from file"""
    bl_idname = "sequencedata.load_objects"
    bl_label = "Load Objects"

    def execute(self, context):
        bpy.context.scene.sequence_data.load_objects(bpy.context.scene.frame_current)
        return {"FINISHED"}


class SequenceDataAddObject(bpy.types.Operator):
    """Add new object sequence"""
    bl_idname = "sequencedata.add_object"
    bl_label = "Add Object"

    def execute(self, context):
        context.scene.sequence_data.last_read_time = -1
        context.scene.sequence_data.objects.add()
        return {"FINISHED"}


class SequenceDataRemoveObject(bpy.types.Operator):
    """Remove object sequence"""
    bl_idname = "sequencedata.remove_object"
    bl_label = "Remove Object"
    object_id : bpy.props.IntProperty(default=-1)

    def execute(self, context):
        if self.object_id != -1:
            bpy.context.scene.sequence_data.objects.remove(self.object_id)
        return {"FINISHED"}


class SequenceDataReadConfig(bpy.types.Operator):
    """Read sequence data configuration file, requires pyyaml"""
    bl_idname = "sequencedata.read_config"
    bl_label = "Read config file"

    def execute(self, context):
        filename, status = context.scene.sequence_data.read_config()
        self.report({'INFO'}, f'Read sequence config from {filename}.')
        return status


class SequenceDataWriteConfig(bpy.types.Operator):
    """Export sequence data configuration file, requires pyyaml"""
    bl_idname = "sequencedata.write_config"
    bl_label="Export config file"
    bl_icon="EXPORT"

    def execute(self, context):
        filename, status = context.scene.sequence_data.write_config()
        self.report({'INFO'}, f'Exported sequence config to {filename}.')
        return status


class ObjectDataSequence(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    shade_smooth: bpy.props.BoolProperty(name="Shade Smooth", default=True)
    path: bpy.props.StringProperty(name="Path", subtype="FILE_PATH")
    enable: bpy.props.BoolProperty(name="Enable", default=True)


class SequenceDataLoader(bpy.types.PropertyGroup):
    """
    Class containing all the data and functions to handle sequence data.
    """
    config_file: bpy.props.StringProperty(name="Config file", subtype = 'FILE_PATH')
    timing_interpolate: bpy.props.BoolProperty(name="Interpolate time")
    live_update: bpy.props.BoolProperty(name="Live update", update=enable_live_update)
    timing_time_start: bpy.props.IntProperty(name="Start Time")
    timing_time_end: bpy.props.IntProperty(name="End Time")
    objects: bpy.props.CollectionProperty(type=ObjectDataSequence)
    export_path: bpy.props.StringProperty(name="Export path", subtype = 'DIR_PATH')

    last_read_time: bpy.props.IntProperty(name="Last read time", default=-1)


    def get_time(self, frame):
        """
        Get timestep from frame. Timestep relates to the input data time while frame is a Blender concept
        """
        scene = bpy.context.scene
        frame_start = scene.frame_start
        frame_end = scene.frame_end

        if self.timing_interpolate and (frame_start != frame_end):
            time = int((self.timing_time_end - self.timing_time_start)*(frame - frame_start)/(frame_end - frame_start)) + self.timing_time_start
        else:
            time = (frame - frame_start) + self.timing_time_start

        time = max(time, self.timing_time_start)
        time = min(time, self.timing_time_end)
        return time


    def get_path(self, template_path, time):
        """
        Get the path to the data file from a template stored in the config file. The template has XXXXX as a time placeholder
        """
        time_string_size = len(re.search("X+", template_path).group())
        path = template_path.replace(time_string_size*"X", "{0:0{1}}".format(time, time_string_size))
        return path


    def get_export_path(self, frame=None):
        """
        Returns the path where a frame is to be exported to

        :param frame: frame number to get the path of
        """

        if frame:
            return os.path.join(self.export_path, "export_{:08}.png".format(frame))
        else:
            return self.export_path


    def load_object(self, name, shade_smooth, path):
        """
        Load single .ply file, replaces `name` object and applies `shade_smooth` if required.
        """

        original_object = bpy.data.objects[name]

        for material in original_object.data.materials.values():
            material.use_fake_user = True

        # Only handles ply files for now
        if path.endswith("ply"):
            bpy.ops.wm.ply_import(filepath=path)
        else:
            raise Exception('Only .ply file supported')

        imported_object = bpy.context.object

        materials_list = original_object.material_slots.keys()
        original_mesh_name = original_object.data.name

        # Replace old mesh with new one
        original_object.data = imported_object.data

        # Delete old mesh and new object
        bpy.data.objects.remove(imported_object, do_unlink=True)
        bpy.data.meshes.remove(bpy.data.meshes[original_mesh_name], do_unlink=True)

        # Copy over materials
        for material_name in materials_list:
            original_object.data.materials.append(bpy.data.materials[material_name])

        if shade_smooth:
            for f in original_object.data.polygons:
                f.use_smooth = True


    def load_objects(self, frame):
        """
        Load every object in self.objects for the frame in parameter
        """
        time = self.get_time(frame)

        if time == self.last_read_time:
            return

        for object in self.objects:
            if (not object.enable) or \
                (not bpy.data.objects[object.name].type == "MESH") or \
                (not bpy.data.objects[object.name].mode == "OBJECT"):
                continue


            path = self.get_path(bpy.path.abspath(object.path), time)
            self.load_object(object.name, object.shade_smooth, path)

        self.last_read_time = time


    def read_config(self):
        """
        Read yaml config file and populate class data structure.
        Requires pyyaml library.
        """

        if not USE_YAML:
            raise Exception('yaml library not available, config reading unavailable')

        with open(bpy.path.abspath(self.config_file), 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)

        scene = bpy.context.scene

        if 'render' in config:
            if 'samples' in config['render']:
                scene.cycles.samples = config['render']['samples']

            if 'resolution_percentage' in config['render']:
                scene.render.resolution_percentage = config['render']['resolution_percentage']

            if 'export_path' in config['render']:
                self.export_path = config['render']['export_path']

        if 'time' in config:
            if 'interpolate' in config['time']:
                self.timing_interpolate = config['time']['interpolate']

            if 'time_start' in config['time']:
                self.timing_time_start = config['time']['time_start']

            if 'time_end' in config['time']:
                self.timing_time_end = config['time']['time_end']

        if 'objects' in config:
            self.objects.clear()
            for idx, object in enumerate(config['objects']):
                self.objects.add()
                self.objects[idx].name = object['name']
                self.objects[idx].path = object['path']
                self.objects[idx].shade_smooth = object['shade_smooth']
                self.objects[idx].enable = object['enable']

        return self.config_file, {"FINISHED"}


    def write_config(self):
        """
        Write yaml config file from class data structure.
        Requires pyyaml library.
        """

        if not USE_YAML:
            raise Exception('yaml library not available, config writing unavailable')

        scene = bpy.context.scene
        config = {}
        config['render'] = {}
        config['render']['samples'] = scene.cycles.samples
        config['render']['resolution_percentage'] = scene.render.resolution_percentage
        config['render']['export_path'] = self.export_path

        config['time'] = {}
        config['time']['interpolate'] = self.timing_interpolate
        config['time']['time_start'] = self.timing_time_start
        config['time']['time_end'] = self.timing_time_end

        config['objects'] = []
        for item in self.objects:
            object = {}
            object["name"] = item.name
            object["path"] = item.path
            object["shade_smooth"] = item.shade_smooth
            object["enable"] = item.enable
            config['objects'].append(object)


        with open(bpy.path.abspath(self.config_file), 'w') as yaml_file:
            yaml.dump(config, yaml_file)


        return self.config_file, {"FINISHED"}
