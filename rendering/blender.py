# run as blender -b fig.blend -P blender_multiple.py
import bpy, sys, os
import numpy as np
import argparse
# sys.path.append("C:/Users/r-gal/OneDrive/Documents/Generative-AI-Projects/Libraries/BlenderToolbox")
# import BlenderToolBox as bt 
import logging, math


def unwrap_method(method:str):
        if method.lower()=='SMART_PROJECT'.lower():
            bpy.ops.uv.smart_project(correct_aspect=True,scale_to_bounds=True)
        elif method.lower()=='UNWRAP'.lower():
            bpy.ops.uv.unwrap(correct_aspect=True)
        elif method.lower()=='CUBE_PROJECT'.lower():
            bpy.ops.uv.cube_project(cube_size=5.0, 
                        correct_aspect=True, 
                        clip_to_bounds=True, 
                        scale_to_bounds=True) 
        elif method.lower()=='CYLINDER_PROJECT'.lower():
            bpy.ops.uv.cylinder_project(direction='ALIGN_TO_OBJECT', 
                            align='POLAR_ZX', radius=5.0, correct_aspect=True, 
                            clip_to_bounds=True, scale_to_bounds=True)
        elif method.lower()=='SPHERE_PROJECT'.lower():
            bpy.ops.uv.sphere_project(clip_to_bounds=True,correct_aspect=True, scale_to_bounds=True)
            pass
        elif method.lower()=='LIGHTMAP_PACK'.lower():
            bpy.ops.uv.lightmap_pack(PREF_CONTEXT='ALL_FACES')
        else: 
            logging.exception('ERROR: Invalid unwrapping method.')



class Renderer():
    def __init__(self):
        self.get_args()
        self.set_gpu()
        self.make_dirs()
        self.setup_scene()
        self.setup_camera()
        self.setup_lights()
        self.objects = []
        

    def get_args(self):
        ap = argparse.ArgumentParser()
        # ap.add_argument("--mesh", type = str, help = "location of mesh")
        ap.add_argument("--mesh_folder", type = str, help = "location of mesh folder")

        ap.add_argument("--texture", type = str, help = "location of texture")
        ap.add_argument("--scene_width", type = int, default = 512, help = "scene width")
        ap.add_argument("--scene_height", type = str, default = 512, help = "scene height")
        ap.add_argument("--total_frame", type = int, default = 1, help = "Total frames to render")
        ap.add_argument("--renderfolder", type = str, default="./out",help = "Location of rendering folder")
        
        # ap.add_argument("--obj_loc",nargs="*",type=float)
        # ap.add_argument("--obj_rot",nargs="*",type=float)
        # ap.add_argument("--obj_scale",nargs="*",type=float)

        # ap.add_argument("--cam_loc",nargs="*",type=float)
        # ap.add_argument("--cam_rot",nargs="*",type=float)
        # ap.add_argument("--cam_scale",nargs="*",type=float)

        # ap.add_argument("--lamp_loc",nargs="*",type=float)
        # ap.add_argument("--lamp_rot",nargs="*",type=float)
        # ap.add_argument("--lamp_scale",nargs="*",type=float)


        print(ap)
        self.args = ap.parse_args(self.extract_args())
        print(self.args.mesh_folder)

    def make_dirs(self):
        if not os.path.isdir(self.args.renderfolder):
            os.makedirs(self.args.renderfolder)
    
    def set_gpu(self):
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
        bpy.context.preferences.addons['cycles'].preferences.get_devices()
        bpy.context.preferences.addons['cycles'].preferences.devices[0].use= True
        bpy.context.scene.cycles.device = 'GPU'
    
    def delete_object(self,obj):
        # bpy.ops.object.select_all(action='DESELECT')
        # obj.select_set(True)
        objs = [obj]
        bpy.ops.object.delete({"selected_objects": objs})
    
    def clear(self):
        bpy.ops.object.delete({"selected_objects": self.objects})
        self.objects=[]

    def setup_scene(self):
        self.scene = bpy.context.scene
        self.scene.render.resolution_x = self.args.scene_width
        self.scene.render.resolution_y = self.args.scene_height

        self.scene.render.image_settings.quality = 100
        self.scene.render.image_settings.file_format = 'PNG'
        self.scene.render.image_settings.color_mode = 'RGBA'

        self.scene.render.resolution_percentage = 100
        self.scene.render.use_border = False

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

    def setup_lights(self):
        # Create new lamp datablock
        lamp_data = bpy.data.lights.new(name="New Lamp", type='SUN')
        lamp_data.energy = 7
        # Create new object with our lamp datablock
        lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
        # Link lamp object to the scene so it'll appear in this scene
        self.scene.collection.objects.link(lamp_object)
        # Place lamp to a specified location
        lamp_object.location = (14.188, -13.29, 16.627)
        lamp_object.rotation_euler = (math.radians(11.7), math.radians(-54.7), math.radians(126))
        # And finally select it make active
        lamp_object.select_set(state=True)
        # self.scene.objects.active = lamp_object
        bpy.context.view_layer.objects.active = lamp_object
        self.lamp=lamp_object

    def setup_camera(self,location=(13.244,-12.473,5.12852), rotation=(math.radians(86.3394),math.radians(0),math.radians(46.6919))):
        bpy.ops.object.camera_add()
        self.camera = bpy.data.objects['Camera']
        self.camera.rotation_mode = 'XYZ'
        self.camera.location=location
        self.camera.rotation_euler = rotation
        self.camera.scale = (1.0,1.0,1.0)
        # Add camera to scene
        bpy.context.scene.camera = self.camera

    def load_object(self,mesh_path):
        bpy.ops.import_scene.obj(filepath=mesh_path)
        mesh_file = os.path.basename(mesh_path)
        selected = bpy.context.selected_objects

        obj = bpy.context.selected_objects.pop()
        obj.location = (0.0,0.0,2.636)
        obj.scale = (1.0, 1.0, 1.0)

        obj.rotation_euler = (math.radians(90),
                            math.radians(0),
                            math.radians(0))

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
    
    def bake_texture(self,obj,unwrap_method_,texture):
        bpy.context.scene.cycles.device = 'GPU'
        # Select object
        obj.select_set(True)
        bpy.context.view_layer.objects.active=obj

        # Get uv map of obj
        bpy.ops.object.mode_set(mode="EDIT")
        obj.select_set(True)
        # bpy.context.view_layer.objects.active = obj
        
        # if obj.type=='MESH' and 'UV_ao' not in obj.data.uv_layers:
        #     obj.data.uv_layers.new(name='UV_ao')
        unwrap_method(unwrap_method_)

        # Load object material's Principal BSDF node
        mat = bpy.data.materials.new(name='Material')
        mat.use_nodes=True     
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Roughness'].default_value = 1.0
        bsdf.inputs['Sheen Tint'].default_value = 0

        # Link texture_image's node Color to BSDF node BaseColor
        texture_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
        image = bpy.data.images.load(texture,check_existing=True)
        texture_image.image = image 

        mat.node_tree.links.new(bsdf.inputs['Base Color'],texture_image.outputs['Color'])
        mat.node_tree.links.new(bsdf.inputs['Alpha'],texture_image.outputs['Alpha'])
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        texture_image.select=True 
        mat.node_tree.nodes.active=texture_image

        # Bake
        bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'},margin=32)
        texture_image.select=False
        obj.select_set(False ) 
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action='DESELECT')
        return 

    def setup_objects(self):
        # mesh_path = getattr(self.args, 'mesh')

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

    def run(self):
        radius = 9.0
        for i in range(self.args.total_frame):
            bpy.context.scene.render.filepath = os.path.join(self.args.renderfolder, f'im_{i:02}.png')
            bpy.ops.render.render(write_still=True)
        # sys.exit()


if __name__ == "__main__":
    renderer = Renderer()
    renderer.setup_objects()
    renderer.run()

    
    # def insert_object(self, gar_loc, tex_loc):
    #     bpy.ops.import_scene.obj(filepath=gar_loc)
    #     obj_object = bpy.context.selected_objects[0]  #### Imported objected gets id 0
    #     obj_object.scale = (1.0, 1.0, 1.0)
    #     obj_object.rotation_euler[1] = 0

    #     mat = bpy.data.materials.new(name='MeshMaterial')  # setup material
    #     obj_object.data.materials.clear()
    #     obj_object.data.materials.append(mat)
    #     obj_object.active_material = mat
    #     mat.use_nodes=True 
    #     tree = mat.node_tree

    #     print(list(tree.nodes))

    #     PRI = tree.nodes["Principled BSDF"]
    #     PRI.inputs['Roughness'].default_value = 1.0
    #     PRI.inputs['Sheen Tint'].default_value = 0

    #     #Import Texture Image
    #     img = bpy.data.images.load(tex_loc,check_existing=True)
    #     cTex = bpy.data.textures.new('Texture', type='IMAGE')
    #     cTex.image = img  # setup texture

    #     texture_image = tree.nodes.new('ShaderNodeTexImage')
    #     texture_image.image = img
       
        
    #     # tree.links.new(bsdf.inputs['Base Color'],texture_image.outputs['Color'])
    #     # tree.links.new(bsdf.inputs['Alpha'],texture_image.outputs['Alpha'])
        
    #     # # add texture to material
    #     # mtex = mat.texture_slots.add()
    #     # mtex.texture = cTex
    #     # # Texture properties
    #     # mat.specular_color = (1, 1, 1)
    #     # mat.use_shadeless = True
    #     # tree.nodes.active=texture_image
    #     # bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'},margin=32)