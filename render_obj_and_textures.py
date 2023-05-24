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


metals = [    "metal","gold", "silver", "copper", "platinum", "iron", "aluminum", "lead", "nickel", "titanium",    "zinc", "cadmium", "mercury", "chromium", "manganese", "tungsten", "steel", "bronze",    "palladium", "rhodium", "magnesium", "cobalt", "tin", "osmium", "ruthenium", "iridium",    "stainless steel", "brass", "bismuth", "invar", "monel", "gunmetal", "electrum",    "pewter", "alnico", "duralumin", "silicon", "germanium", "gallium arsenide", "indium antimonide",    "aluminum gallium arsenide", "silicon carbide", "tungsten carbide", "boron carbide", "diamond",    "nickel-chromium", "cobalt-chromium", "aluminum-silicon"]
ceramics = ['ceramic', 'marble', 'granite', 'porcelain']
woods = [    "wood","birch", "cherry", "maple", "oak", "walnut", "ash", "pine", "redwood", "cedar",    "mahogany", "teak", "ebony", "rosewood", "ipe", "padauk", "purpleheart",    "jatoba", "larch", "spruce", "fir", "hemlock", "Douglas fir", "balsa",    "poplar", "sycamore", "butternut", "hickory", "beech", "elm", "aspen"]
plastics = [    "plastic","polyethylene", "polypropylene", "polyvinyl chloride", "polystyrene", "acrylonitrile butadiene styrene",    "polycarbonate", "polyethylene terephthalate", "polyurethane", "polyamides", "polyimides",    "polyvinylidene fluoride", "polyacetal", "polymethyl methacrylate", "polybutylene terephthalate",    "polyphenylene oxide", "polyphenylene sulfide", "polyetheretherketone", "polyvinyl acetate",    "polylactic acid", "polybutene", "polyvinyl butyral", "polyvinyl alcohol"]
fabrics = ['cotton', 'wool', 'silk','linen', 'cashmere', 'mohair', 'alpaca', 'angora', 'viscose', 'polyester', 'nylon', 'acrylic', 'spandex', 'rayon', 'leather', 'suede','fur', 'denim', 'canvas', 'lace', 'tulle', 'velour', 'chiffon', 'organza', 'satin', 'taffeta', 'tweed']


glossy = {
    'Specular':1.0,
    'Roughness':0.00,
    # 'Sheen Tint':0.5,
    'Clearcoat':1.0,
    'Clearcoat Roughness':0.05,
    # 'IOR':1.47,
}

matte = {
    'Specular':0.5,
    'Roughness':0.5,
    # 'Sheen Tint':0.5,
    'Clearcoat':0.0,
    'Clearcoat Roughness':0.95,
    # 'IOR':1.47,
}

mat_finish_settings = {
    'glossy': glossy,
    'matte': matte,
}

def setup_fabric(principled_node: bpy.types.Node, mat_node_tree, image_texture_node: bpy.types.Node):
    bump_node = mat_node_tree.nodes.new('ShaderNodeBump')
    bump_node.inputs['Strength'].default_value=0.1


    mat_node_tree.links.new(image_texture_node.outputs['Color'], bump_node.inputs['Height'])
    mat_node_tree.links.new(bump_node.outputs['Normal'], principled_node.inputs['Normal'])

    principled_node.inputs['Sheen'].default_value=1.0
    principled_node.inputs['Specular'].default_value=0.0
    principled_node.inputs['Clearcoat'].default_value=0.0
    principled_node.inputs['Metallic'].default_value=0.0
    return 

def setup_plastic(principled_node: bpy.types.Node, mat_node_tree):
    return 

def setup_metal(principled_node: bpy.types.Node, mat_node_tree):
    noise_node = mat_node_tree.nodes.new('ShaderNodeTexNoise')
    noise_node.inputs['Scale'].default_value=500
    noise_node.inputs['Roughness'].default_value=1.0
    
    bump_node = mat_node_tree.nodes.new('ShaderNodeBump')
    bump_node.inputs['Strength'].default_value=0.1

    mat_node_tree.links.new(noise_node.outputs['Fac'], bump_node.inputs['Height'])
    mat_node_tree.links.new(bump_node.outputs['Normal'], principled_node.inputs['Normal'])
    principled_node.inputs['Metallic'].default_value=1.0
    return 

def setup_wood(principled_node: bpy.types.Node, mat_node_tree, image_texture_node):
    bump_node = mat_node_tree.nodes.new('ShaderNodeBump')
    bump_node.inputs['Strength'].default_value=0.1

    mat_node_tree.links.new(image_texture_node.outputs['Color'],bump_node.inputs['Height'])
    mat_node_tree.links.new(bump_node.outputs['Normal'],principled_node.inputs['Normal'])
    return

def isin_materials(input_material_type,materials_list):
    for mat in materials_list:
        if mat in input_material_type:
            print(f'Material {input_material_type} detected as {mat}!')
            return True 
    return False

def setup_material(principled_node: bpy.types.Node, mat_node_tree, image_texture_node: bpy.types.Node, material_type:str, material_finish:str='glossy',material_finish_settings:dict=None):
    material_type=material_type.lower()

    # Do another pass here on the type of finish. For now, default finish is "glossy"
    set_pbsdf_settings_by_str(principled_node,material_finish)
    if material_finish_settings is not None: 
        set_pbsdf_settings_by_dict(principled_node,material_finish_settings)
    
    if isin_materials(material_type,metals):
        setup_metal(principled_node,mat_node_tree)
        pass 
    elif isin_materials(material_type,woods):
        setup_wood(principled_node,mat_node_tree,image_texture_node)
        pass 
    elif isin_materials(material_type,ceramics):
        # No need to add additional nodes so leave as is.
        pass 
    elif isin_materials(material_type,plastics):
        # No need to add additional nodes so leave as is.
        pass
    elif isin_materials(material_type,fabrics):
        setup_fabric(principled_node,mat_node_tree,image_texture_node)
        pass 
    else:
        print(f'ERROR: Material type {material_type} unknown')
    return

def set_pbsdf_settings_by_dict(principled_node: bpy.types.Node, material_finish_settings:dict):
    for k in material_finish_settings.keys():
        print(f"ADJUSTING {k}")
        principled_node.inputs[k].default_value = material_finish_settings[k]
    return


def set_pbsdf_settings_by_str(principled_node: bpy.types.Node, material_finish:str):
    if material_finish:
        material_finish = material_finish.lower()
        for k in mat_finish_settings.keys():
            k = k.lower()
            if k in material_finish:
                print("material finish detected. adjusting corresponding material settings")
                ms = mat_finish_settings[k]
                for k2 in ms.keys():
                    principled_node.inputs[k2].default_value = ms[k2]
                break 
    return 


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

# Code from https://blender.stackexchange.com/questions/158896/how-set-hex-in-rgb-node-python
def srgb_to_linearrgb(c):
    if   c < 0:       return 0
    elif c < 0.04045: return c/12.92
    else:             return ((c+0.055)/1.055)**2.4

def hex_to_rgb(h,alpha=1):
    r = (h & 0xff0000) >> 16
    g = (h & 0x00ff00) >> 8
    b = (h & 0x0000ff)
    return tuple([srgb_to_linearrgb(c/0xff) for c in (r,g,b)] + [alpha])


def add_color_finish(rgb_node, hex_code:str):
    # print(f'HEX: {hex_code}')
    hex_code_with_0x = hex(int(hex_code[1:], 16))
    hex_code_with_0x = int(hex_code_with_0x, 16)
    # print(f'HEX_WITH_0x: {hex_code_with_0x}')
    # print(f'TYPE of HEX_WITH_0x: {type(hex_code_with_0x)}')
    rgb = hex_to_rgb(hex_code_with_0x)
    # print(f'RGB: {rgb}')
    rgb_node.outputs['Color'].default_value = rgb
    return 

def transform_material(mapping_node:bpy.types.Node, transforms:dict):
    mapping_node.inputs["Location"].default_value = transforms["location"]
    mapping_node.inputs["Rotation"].default_value = Euler(transforms["rotation"], "XYZ")
    mapping_node.inputs["Scale"].default_value = transforms["scale"]
    return 


class Renderer():
    def __init__(self,cam_info, light_info=None, resolution=(1024,1024)):
        self.resolution = resolution
        self.set_gpu("CYCLES")
        self.setup_render()
        self.setup_background()
        self.setup_camera(cam_info['loc'],cam_info['rot'],cam_info['scale'])
        if light_info: self.setup_light(light_info['loc'],light_info['rot'],light_info['scale'])
        
        self.objects = []
    
    def set_gpu(self, rendering_engine):
        assert rendering_engine in ['CYCLES', 'BLENDER_EEVEE']
        bpy.context.scene.render.engine = rendering_engine
        bpy.context.scene.view_settings.view_transform = 'Standard'
        if rendering_engine=='CYCLES':
            bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
            bpy.context.preferences.addons['cycles'].preferences.get_devices()
            bpy.context.preferences.addons['cycles'].preferences.devices[0].use= True
            bpy.context.scene.cycles.device = 'GPU'
            bpy.context.scene.cycles.samples=4096
        elif rendering_engine=='BLENDER_EEVEE':
            bpy.context.scene.eevee.taa_render_samples=1024
            #Enable bloom
            bpy.context.scene.eevee.use_bloom=True
            #Enable ambient occlusion
            bpy.data.scenes["Scene"].world.use_nodes=True
            bpy.context.scene.eevee.use_gtao=True
            bpy.context.scene.eevee.gtao_distance=1.0
            bpy.context.scene.eevee.gtao_quality=1.0
            # Enable screen space reflections
            bpy.context.scene.eevee.use_ssr=True
            # Increase shadow resolution
            bpy.context.scene.eevee.shadow_cube_size='4096'
            bpy.context.scene.eevee.shadow_cascade_size='4096'

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

    def setup_light(self, loc=(14.188, -13.29, 16.627), rot=(11.7,-54.7,126), scale=(1.0,1.0,1.0)):
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

    def setup_camera(self,location=(13.244,-12.473,5.12852), 
                    rotation=(86.3394,0,46.6919),
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
    
    def load_object_gltf(self,mesh_path, loc=(0.0,0.0,2.636), rot=(90,0,0), scale=(1.0,1.0,1.0), axis_forward='-Z', axis_up='Y'):
        bpy.ops.import_scene.gltf(filepath=mesh_path)

        mesh_file = os.path.basename(mesh_path)
        selected = bpy.context.selected_objects
        obj = bpy.context.selected_objects.pop()
        # obj.location = loc
        # obj.rotation_euler = (math.radians(rot[0]),
        #                     math.radians(rot[1]),
        #                     math.radians(rot[2]))
        # obj.scale = scale
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
    
    def apply_texture(self,obj,unwrap_method_,texture_path,texture_name, material_finish, 
                    material_transforms=None, material_color=None, material_finish_settings=None):
        self.set_gpu("CYCLES")
        bpy.context.scene.cycles.device = 'GPU'
        obj.select_set(True)
        bpy.context.view_layer.objects.active=obj

        # Get uv map of obj
        bpy.ops.object.mode_set(mode="EDIT")
        obj.select_set(True)
        # unwrap_method(unwrap_method_)

        # Load texture image
        image = bpy.data.images.load(texture_path,check_existing=True)
        # Load object material's Principal BSDF node
        mat = bpy.data.materials.new(name='Material')
        mat.use_nodes=True     
        bsdf = mat.node_tree.nodes["Principled BSDF"]

        # Link texture_image's node Color to BSDF node BaseColor
        image_texture_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
        image_texture_node.image = image 

        mapping_node = mat.node_tree.nodes.new('ShaderNodeMapping')
        texture_coord_node = mat.node_tree.nodes.new('ShaderNodeTexCoord')
        mat.node_tree.links.new(texture_coord_node.outputs['UV'], mapping_node.inputs['Vector'])
        mat.node_tree.links.new(mapping_node.outputs['Vector'], image_texture_node.inputs['Vector'])

        rgb_node = mat.node_tree.nodes.new('ShaderNodeRGB')
        rgb_node.outputs['Color'].default_value = (0.0, 0.0, 0.0, 1.0)
        mix_node = mat.node_tree.nodes.new(type='ShaderNodeMixRGB')
        # mix_node.blend_type = 'MIX'
        mat.node_tree.links.new(image_texture_node.outputs['Color'], mix_node.inputs['Color1'])
        mat.node_tree.links.new(rgb_node.outputs['Color'], mix_node.inputs['Color2'])

        # mat.node_tree.links.new(bsdf.inputs['Base Color'],image_texture_node.outputs['Color'])
        mat.node_tree.links.new(mix_node.outputs['Color'],bsdf.inputs['Base Color'])
        mat.node_tree.links.new(bsdf.inputs['Alpha'],image_texture_node.outputs['Alpha'])

        setup_material(bsdf,mat.node_tree,image_texture_node,material_type=texture_name,material_finish=material_finish,material_finish_settings=material_finish_settings)

        # Add some function here to adjust the values of the  mapping node
        if material_transforms:
            transform_material(mapping_node,material_transforms)
        
        if material_color:
            add_color_finish(rgb_node,material_color)

        obj.data.materials.clear()
        obj.data.materials.append(mat)
        image_texture_node.select=True 
        mat.node_tree.nodes.active=image_texture_node

        # Bake
        # bpy.ops.object.bake(type='COMBINED',pass_filter={'COLOR'},margin=32)
        image_texture_node.select=False
        obj.select_set(False) 
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action='DESELECT')
        self.set_gpu("BLENDER_EEVEE")
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
        ap.add_argument("--rendering_setup_json", type = str, help = "Path to .json file containing filenames of 3D parts and their placements, lighting, & camera configs in Blender.")
        ap.add_argument("--texture_object_parts_json", type = str, help = "Path to .json file containing 3D parts and their corresponding textures.")
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
        light_info=None
        if 'light' in info: light_info = info['light'] 
        resolution = info['resolution']

    renderer = Renderer(cam_info=cam_info,light_info=light_info,resolution=resolution)

    with open(args.texture_object_parts_json) as json_file:
        texture_object_parts = json.load(json_file)

    for model_key in models_info:
        model_info = models_info[model_key]
        print(model_info)
        parts_info = model_info['parts']
        for part in parts_info['names']:
            part_material_path = os.path.join(CWD,texture_object_parts[model_key][part]["mat_image_texture"])
            part_material_name = texture_object_parts[model_key][part]["mat_name"]
            part_material_finish = texture_object_parts[model_key][part]["mat_finish"]
            part_material_transforms = None
            part_material_color = None
            part_material_finish_settings = None

            if "mat_finish_settings" in texture_object_parts[model_key][part].keys():
                part_material_finish_settings = texture_object_parts[model_key][part]["mat_finish_settings"]

            if "mat_transforms" in texture_object_parts[model_key][part].keys(): 
                part_material_transforms = texture_object_parts[model_key][part]["mat_transforms"]

            if "mat_color" in texture_object_parts[model_key][part].keys():
                part_material_color = texture_object_parts[model_key][part]["mat_color"]
            
            # part_path = os.path.join(models_dir,model_key, f'{part}.obj')
            # obj = renderer.load_object(part_path,loc=parts_info['loc'],rot=parts_info['rot'],scale=parts_info['scale'])
            part_path = os.path.join(models_dir,model_key, f'{part}.glb')
            obj = renderer.load_object_gltf(part_path,loc=parts_info['loc'],rot=parts_info['rot'],scale=parts_info['scale'])
            # renderer.recalculate_normals(obj)
            # renderer.apply_texture(obj,unwrap_method_,part_material_path,part_material_name,part_material_finish, part_material_transforms, part_material_color,part_material_finish_settings)
    renderer.render(out_path=args.out_path)
    
if __name__=="__main__":
    main()
