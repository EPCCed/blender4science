
import bpy
import os
import sys
import argparse


class SequenceDataRender(bpy.types.PropertyGroup):

    def render(self, Scene, frame):
        """
        Load the data and render a single frame

        :param frame: frame number to render
        """
        Scene.sequence_data.live_update = False

        print("Render frame:", frame)
        Scene.frame_current = frame

        Scene.sequence_data.load_objects(frame)

        export_path = Scene.sequence_data.get_export_path(frame)
        print("Export to {}".format(export_path))

        bpy.ops.render.render()
        bpy.data.images['Render Result'].save_render(filepath=export_path)


    def parse_arguments(self, Scene):
        """
        Parse command line arguments meant for sequence data and overwrite some of the 
        """
        parser = argparse.ArgumentParser(description="""When called by a blender instance, renders a set of frames
                                        by first importing the corresponding sequence data objects.
                                        It also handles running multiple instances concurently by rendering each frame only once.""")
        parser.add_argument("--configfile", help="File to read the configuration from, if absent setting stored in the .blend file are used. Requires pyyaml lib installed inside blender.")
        parser.add_argument("--renderpath", help="Path where renders are to be exported, supresed the config file render/export_path parameter.")
        parser.add_argument("--frames", help="Range of frame to render, should be in format '1-17'. If absent, using the frame range inside the .blend file.")

        # Parse arguments after "--"
        if not "--" in sys.argv:
            return
        args = parser.parse_args(args=sys.argv[sys.argv.index("--") + 1:])

        if args.configfile:
            print(f"Loading config file at: {args.configfile}")
            Scene.sequence_data.config_file = args.configfile
            Scene.sequence_data.read_config()

        if args.renderpath:
            Scene.sequence_data.export_path = args.renderpath

        if args.frames:
            Scene.frame_start = int(args.frames.split("-")[0])
            Scene.frame_end = int(args.frames.split("-")[1])


    def render_frames(self):
        """
        Render frames from scene.frame_start to scene.frame_end. 
        Render isn't triggered for frames that are already present in the folder
        """
        Scene = bpy.context.scene

        self.parse_arguments(Scene)

        # Create export folder
        export_folder = Scene.sequence_data.get_export_path()
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)

        # Render each frame
        for frame in range(Scene.frame_start, Scene.frame_end+1):
            export_path = Scene.sequence_data.get_export_path(frame)
            export_path_tmp = export_path + ".tmp"

            # Check if render has already been done
            if os.path.exists(export_path) or os.path.exists(export_path_tmp):
                continue

            # Create empty temporary file
            with open(export_path_tmp, 'w') as fp:
                pass

            self.render(Scene, frame)
            os.remove(export_path_tmp)
