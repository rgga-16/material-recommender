from flask import Flask, send_from_directory, request, jsonify
import random, requests, json, copy, shutil 
from PIL import Image

from texture_transfer_3d import TextureDiffusion
from configs import *
import os 
from utils.image import makedir

import gpt_wizard


app = Flask(__name__, static_folder="./client/public")

@app.route("/suggest_colors_by_style", methods=['POST'])
def suggest_colors_by_style():

    form_data = request.get_json()
    style = form_data["style"]
    # material_type = form_data["material_type"]

    suggested_color_palettes = []

    color_palettes_dict = gpt_wizard.suggest_color_by_style(style=style)

    for key in color_palettes_dict.keys():
        suggested_color_palettes.append({
            "name":key,
            "palette":color_palettes_dict[key]
        })

    return suggested_color_palettes

@app.route("/suggest_materials_by_style", methods=['POST'])
def suggest_materials_by_style():

    form_data = request.get_json()
    style = form_data["style"]
    material_type = form_data["material_type"]

    materials = gpt_wizard.suggest_materials_by_style2(style=style,material_type=material_type)

    suggested_materials = []
    for m in materials:
        reason=m["reason"] ; m = m["name"];
        prompt = m if material_type.lower()=='all types' else f"{m} {material_type}"
        image, filename = generate_textures(prompt,n=1,imsize=448); image=image[0]; filename=filename[0]
        image.save(os.path.join(SERVER_IMDIR,"suggested",filename))
        loadpath = os.path.join(CLIENT_IMDIR,"suggested",filename)
        suggested_materials.append({
            "name":m,
            # "texture":image,
            "reason":reason,
            "filepath":loadpath
        })
    
    return suggested_materials

@app.route("/suggest_by_style", methods=['POST'])
def suggest_by_style():

    form_data = request.get_json()

    return 


@app.route("/generate_and_transfer_textures", methods=['POST'])
def generate_and_transfer_textures():
    form_data = request.get_json()

    texture_string = form_data["texture_string"]
    n = form_data["n"]
    imsize = form_data["imsize"]
    obj_part_dict = form_data["obj_parts_dict"]

    #################### Generating the textures ################
    textures, filenames = generate_textures(texture_string, n, imsize)

    #################### Transferring the textures ##############
    rendering_texture_pairs = []

    for i in range(len(textures)):

        textures[i].save(os.path.join(SERVER_IMDIR,filenames[i]))
        texture_loadpath = os.path.join(CLIENT_IMDIR,filenames[i])

        new_texture_parts = copy.deepcopy(current_texture_parts)
        for obj in list(obj_part_dict.keys()):
            for part in obj_part_dict[obj]:
                new_texture_parts[obj][part]["mat_name"]=texture_string
                new_texture_parts[obj][part]["mat_finish"]="glossy"
                new_texture_parts[obj][part]["mat_image_texture"]=os.path.join(SERVER_IMDIR,filenames[i])
                
        tmp_texture_parts_savepath = os.path.join(SERVER_IMDIR,"renderings",f"texture_parts_{i}.json")
        
        with open(tmp_texture_parts_savepath,"w") as tmpfile:
            json.dump(new_texture_parts,tmpfile)

        rendering_savepath = os.path.join(SERVER_IMDIR,"renderings",f"rendering_{i}.png")
        rendering_loadpath = os.path.join(CLIENT_IMDIR,"renderings",f"rendering_{i}.png")

        command_str = f'blender --background --python render_obj_and_textures.py -- --out_path {rendering_savepath} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {tmp_texture_parts_savepath}'
        os.system(command_str)

        rendering_texture_pairs.append(
            {'rendering':rendering_loadpath, 'texture':texture_loadpath, 'info':new_texture_parts, 'info_path':tmp_texture_parts_savepath}
        )

    return {"results": rendering_texture_pairs}

def generate_textures(texture_string, n, imsize):
    generated_textures = texture_generator.text2texture(texture_string, n=n, gen_imsize=imsize)
    texture_filenames = []

    for i in range(len(generated_textures)):
        texture_filenames.append(f"{texture_string}_{i}.png")
    return generated_textures, texture_filenames


def apply_to_current_rendering(renderpath, texture_parts_path):
    global current_texture_parts
    curr_render_savedir = os.path.join(SERVER_IMDIR,'renderings','current')
    if(not os.path.isdir(curr_render_savedir)):
        makedir(curr_render_savedir)
    
    curr_render_path = os.path.join(curr_render_savedir,"rendering.png")
    curr_textureparts_path = os.path.join(curr_render_savedir,"texture_parts.json")

    texture_parts = json.load(open(texture_parts_path))

    texture_filenames = []
    for obj in list(texture_parts.keys()):
        for part in list(texture_parts[obj].keys()):
            texture_path = texture_parts[obj][part]["mat_image_texture"]
            texture_filename = os.path.basename(texture_path)
            curr_texture_path = os.path.join(curr_render_savedir,texture_filename)
            img = Image.open(texture_path)
            img.save(curr_texture_path)
            texture_parts[obj][part]["mat_image_texture"] = curr_texture_path

    current_texture_parts = copy.deepcopy(texture_parts)
    with open(curr_textureparts_path,"w") as f:
        json.dump(texture_parts,f)

    shutil.copy(renderpath, curr_render_path) 
    return curr_render_path, curr_textureparts_path

@app.route("/apply_to_current_rendering", methods= ['POST'])
def set_current_rendering():
    form_data = request.get_json()

    rendering_path = os.path.join(CWD,"client","public", form_data["rendering_path"])
    texture_parts = form_data["texture_parts"]
    textureparts_path = form_data["textureparts_path"]

    curr_renderpath, curr_textureparts_path = apply_to_current_rendering(rendering_path,textureparts_path)

    return get_current_rendering()



@app.route("/get_current_rendering")
def get_current_rendering():
    curr_render_loaddir = os.path.join(CLIENT_IMDIR,'renderings','current')

    current_textureparts_path = os.path.join(SERVER_IMDIR,'renderings','current',"texture_parts.json")
    texture_parts = json.load(open(current_textureparts_path))

    current_render_path = os.path.join(curr_render_loaddir,"rendering.png")
    
    return {"rendering_path":current_render_path, "texture_parts":texture_parts}

@app.route("/get_objects_and_parts")
def load_object_data():
    objects_data = json.load(open(rendering_setup_path))
    object_inputs = objects_data["objects"]
    return object_inputs

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('./client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('./client/public', path)

if __name__ == "__main__":

    SERVER_IMDIR = os.path.join(CWD,"client","public","gen_images")
    CLIENT_IMDIR = os.path.join("gen_images")
    CURR_RENDER_ID = 1

    products = [
        "nightstand_family",
    ]

    DATA_DIR = os.path.join(os.getcwd(),"data","3d_models",products[0])
    RENDER_DIR = os.path.join(DATA_DIR,"renderings")

    init_texture_parts_path = os.path.join(RENDER_DIR, str(CURR_RENDER_ID),"object_part_material.json")
    init_render_path = os.path.join(RENDER_DIR,str(CURR_RENDER_ID),"rendering.png")

    init_texture_parts = json.load(open(os.path.join(RENDER_DIR, str(CURR_RENDER_ID),"object_part_material.json")))
    current_texture_parts = copy.deepcopy(init_texture_parts)

    rendering_setup_path = os.path.join(DATA_DIR,"rendering_setup.json")

    apply_to_current_rendering(init_render_path,init_texture_parts_path)


    texture_generator = TextureDiffusion(model_id="runwayml/stable-diffusion-v1-5")
    app.run(debug=True)









################### Dump


# @app.route("/transfer_textures", methods=['POST'])
# def transfer_textures():
#     form_data = request.get_json()

#     texture_string = form_data["texture_string"]
#     obj_part_dict = form_data["obj_parts_dict"]
#     texture_paths = form_data["texture_paths"]

#     rendering_paths = []

#     for i in range(len(texture_paths)):
#         new_texture_parts = copy.deepcopy(current_texture_parts)
#         for obj in list(obj_part_dict.keys()):
#             for part in obj_part_dict[obj]:
#                 new_texture_parts[obj][part]["mat_name"]=texture_string
#                 new_texture_parts[obj][part]["mat_finish"]="glossy"
#                 new_texture_parts[obj][part]["mat_image_texture"]=texture_paths[i]
                
#         tmp_texture_parts_savepath = os.path.join(SERVER_IMDIR,"renderings",f"texture_parts_{i}.json")
        
#         with open(tmp_texture_parts_savepath,"w") as tmpfile:
#             json.dump(new_texture_parts,tmpfile)

#         tmp_rendering_savepath = os.path.join(SERVER_IMDIR,"renderings",f"rendering_{i}.png")
#         tmp_rendering_loadpath = os.path.join(CLIENT_IMDIR,"renderings",f"rendering_{i}.png")
#         rendering_paths.append(tmp_rendering_loadpath)
#         command_str = f'blender --background --python render_obj_and_textures.py -- --out_path {tmp_rendering_savepath} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {tmp_texture_parts_savepath}'
#         os.system(command_str)

#     return rendering_paths