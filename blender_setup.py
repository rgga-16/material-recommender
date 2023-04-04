# from rendering import blender
import numpy as np
import argparse, sys, json, os
from mathutils import Euler, Color
from pathlib import Path
import bpy, sys, os
import numpy as np
import argparse


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CWD)
# import BlenderToolBox as bt 
import logging, math

working_dir_path = CWD



class Renderer():
    def __init__(self,cam_info, light_info, resolution=(1024,1024)):
        self.resolution = resolution
        self.set_gpu("BLENDER_EEVEE")
        self.setup_render()
        self.setup_background()
        self.setup_camera(cam_info['loc'],cam_info['rot'],cam_info['scale'])
        self.setup_light(light_info['loc'],light_info['rot'],light_info['scale'])
        
        self.objects = []
    
    def set_gpu(self, rendering_engine):
        assert rendering_engine in ['CYCLES', 'BLENDER_EEVEE']
        bpy.context.scene.render.engine = rendering_engine

        if rendering_engine=='CYCLES':
            bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
            bpy.context.preferences.addons['cycles'].preferences.get_devices()
            bpy.context.preferences.addons['cycles'].preferences.devices[0].use= True
            bpy.context.scene.cycles.device = 'GPU'
            bpy.context.scene.cycles.samples=1024
        elif rendering_engine=='BLENDER_EEVEE':
            bpy.context.scene.eevee.taa_render_samples=1024

    def delete_object(self,obj):
        objs = [obj]
        bpy.ops.object.delete({"selected_objects": objs})
    
    def clear(self):
        bpy.ops.object.delete({"selected_objects": self.objects})
        self.objects=[]

    def setup_background(self,hdri_path: str = os.path.join(working_dir_path, 'data', 'hdri', 'interior.exr') , rotation: float = 0.0) -> None:
        scene = bpy.data.scenes["Scene"]
        world = scene.world

        world.use_nodes = True
        node_tree = world.node_tree

        environment_texture_node = node_tree.nodes.new(type="ShaderNodeTexEnvironment")
        environment_texture_node.image = bpy.data.images.load(hdri_path)

        mapping_node = node_tree.nodes.new(type="ShaderNodeMapping")
        if bpy.app.version >= (2, 81, 0):
            mapping_node.inputs["Rotation"].default_value = (0.0, 0.0, rotation)
        else:
            mapping_node.rotation[2] = rotation

        tex_coord_node = node_tree.nodes.new(type="ShaderNodeTexCoord")

        node_tree.links.new(tex_coord_node.outputs["Generated"], mapping_node.inputs["Vector"])
        node_tree.links.new(mapping_node.outputs["Vector"], environment_texture_node.inputs["Vector"])
        node_tree.links.new(environment_texture_node.outputs["Color"], node_tree.nodes["Background"].inputs["Color"])

    
    def setup_render(self):
        self.scene = bpy.context.scene
        self.scene.render.resolution_x = self.resolution[0]
        self.scene.render.resolution_y = self.resolution[1]

        self.scene.render.image_settings.quality = 100
        self.scene.render.image_settings.file_format = 'PNG'
        self.scene.render.image_settings.color_mode = 'RGBA'

        self.scene.render.resolution_percentage = 100
        self.scene.render.use_border = False

        self.scene.render.film_transparent = True

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

    def setup_light(self, loc=(4.07625, 1.00545, 5.90386), rot=(11.7,-54.7,126), scale=(1.0,1.0,1.0)):
        # Create new lamp datablock
        lamp_data = bpy.data.lights.new(name="New Lamp", type='SUN')
        lamp_data.energy = 10
        # Create new object with our lamp datablock
        lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
        # Link lamp object to the scene so it'll appear in this scene
        self.scene.collection.objects.link(lamp_object)
        # Place lamp to a specified location
        lamp_object.location = loc
        lamp_object.rotation_euler = (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))
        lamp_object.scale = scale
        # And finally select it make active
        lamp_object.select_set(state=True)
        # self.scene.objects.active = lamp_object
        bpy.context.view_layer.objects.active = lamp_object
        self.lamp=lamp_object

    def setup_camera(self,location=(7.35889,-6.92579,4.95831), 
                    rotation=(63.5593,0,46.6919),
                    scale = (1.0,1.0,1.0)):
        bpy.ops.object.camera_add()
        self.camera = bpy.data.objects['Camera']
        self.camera.rotation_mode = 'XYZ'
        self.camera.location=location
        self.camera.rotation_euler = (math.radians(rotation[0]), 
                                    math.radians(rotation[1]), 
                                    math.radians(rotation[2]))
        self.camera.scale = scale
        bpy.context.scene.camera = self.camera

    def load_object(self,mesh_path, loc=(0.0,0.0,2.636), rot=(90,0,0), scale=(1.0,1.0,1.0), axis_forward='-Z', axis_up='Y'):
        bpy.ops.import_scene.obj(filepath=mesh_path, axis_forward=axis_forward, axis_up=axis_up)


        mesh_file = os.path.basename(mesh_path)
        selected = bpy.context.selected_objects
        obj = bpy.context.selected_objects.pop()
        obj.location = loc
        obj.rotation_euler = (math.radians(rot[0]),
                            math.radians(rot[1]),
                            math.radians(rot[2]))
        obj.scale = scale
        self.objects.append(obj)
        return obj 
    
    def recalculate_normals(self,obj):
        # obj_objects = bpy.context.selected_objects[:]
        bpy.ops.object.select_all(action='DESELECT')
        # for obj in obj_objects:    
        obj.select_set(state=True)
        bpy.context.view_layer.objects.active = obj
        # go edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        # select al faces
        bpy.ops.mesh.select_all(action='SELECT')
        # recalculate outside normals 
        # bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.average_normals(average_type='FACE_AREA', weight=50, threshold=0.01)
        # go object mode again
        bpy.ops.object.editmode_toggle()
        return


    def setup_objects(self):
        mesh_folder = getattr(self.args, 'mesh_folder')
        texture_path = getattr(self.args, 'texture')
        unwrap_method='smart_project'

        for m in os.listdir(mesh_folder):
            mesh_path = os.path.join(mesh_folder,m)
            if os.path.isdir(mesh_path):
                continue
            if os.path.splitext(m)[1]=='.obj':
                obj = self.load_object(mesh_path)
                self.recalculate_normals(obj)
                self.bake_texture(obj,unwrap_method,texture_path)

    def extract_args(self, input_argv=None):
        """
        Pull out command-line arguments after "--". Blender ignores command-line flags
        after --, so this lets us forward command line arguments from the blender
        invocation to our own script.
        """
        if input_argv is None:
            input_argv = sys.argv
            print(input_argv)
        output_argv = []
        if '--' in input_argv:
            idx = input_argv.index('--')
            print(idx)
            output_argv = input_argv[(idx + 1):]
            print(output_argv)
        return output_argv

    def render(self, out_path):
        bpy.context.scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(working_dir_path,'temp.blend'))
        sys.exit()

def extract_args(input_argv=None):
        """
        Pull out command-line arguments after "--". Blender ignores command-line flags
        after --, so this lets us forward command line arguments from the blender
        invocation to our own script.
        """
        if input_argv is None:
            input_argv = sys.argv
            print(input_argv)
        output_argv = []
        if '--' in input_argv:
            idx = input_argv.index('--')
            print(idx)
            output_argv = input_argv[(idx + 1):]
            print(output_argv)
        return output_argv

def get_args():
        ap = argparse.ArgumentParser()
        ap.add_argument("--out_path", type = str, help = "File path to save the rendering.")
        args = ap.parse_args(extract_args())
        return args

def main(): 
    args = get_args()
    unwrap_method_='UNWRAP'
    with open(args.rendering_setup_json) as json_file:
        info = json.load(json_file)
        models_dir = info['dir']
        models_info = info['objects']
        cam_info = info['camera']
        light_info = info['light']
        resolution = info['resolution']

    renderer = Renderer(cam_info=cam_info,light_info=light_info,resolution=resolution)


    renderer.render(out_path=args.out_path)
    
if __name__=="__main__":
    main()
