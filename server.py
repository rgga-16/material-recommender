from flask import Flask, send_from_directory, request, jsonify
import random, requests, json, copy 
from PIL import Image

from texture_transfer_3d import TextureDiffusion
from configs import *
import os 

'''
Tutorial on how to use Svelte to fetch APIs 
https://sveltesociety.dev/recipes/component-recipes/using-fetch-to-consume-apis
'''

SERVER_IMDIR = os.path.join(CWD,"client","public","gen_images")
CLIENT_IMDIR = os.path.join("gen_images")
CURR_RENDER_ID = 1

products = [
    "nightstand_family",
]

data_dir = os.path.join(os.getcwd(),"data","3d_models",products[0])
renderings_dir = os.path.join(data_dir,"renderings")
init_texture_parts_path = os.path.join(renderings_dir, str(CURR_RENDER_ID),"object_part_material.json")
rendering_setup_path = os.path.join(data_dir,"rendering_setup.json")

init_texture_parts = json.load(open(os.path.join(renderings_dir, str(CURR_RENDER_ID),"object_part_material.json")))
current_texture_parts = copy.deepcopy(init_texture_parts)

app = Flask(__name__, static_folder="./client/public")

@app.route("/generate_and_transfer_textures", methods= ['POST'])
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
            {'rendering':rendering_loadpath, 'texture':texture_loadpath, 'info':new_texture_parts}
        )

    return {"results": rendering_texture_pairs}

def generate_textures(texture_string, n, imsize):

    generated_textures = texture_generator.text2texture(texture_string, n=n, gen_imsize=imsize)
    texture_filenames = []

    for i in range(len(generated_textures)):
        texture_filenames.append(f"{texture_string}_{i}.png")
    return generated_textures, texture_filenames

@app.route("/get_current_rendering")
def get_rendering():
    current_texture_parts = copy.deepcopy(init_texture_parts)

@app.route("/get_initial_rendering")
def get_initial_rendering():
    rendering_loadpath = os.path.join(CLIENT_IMDIR,"renderings",f"init_rendering.png")
    return {"rendering_path":rendering_loadpath}

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
    texture_generator = TextureDiffusion()
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