from flask import Flask, send_from_directory, request, jsonify, send_file
import random, requests, json, copy, shutil, os, base64, io, time, deepl
from PIL import Image
from texture_transfer_3d import DALLE2, text2texture_similar
from configs import *
import embedding as e
import pandas as pd


from utils.image import makedir, emptydir, degrees_to_radians, im_2_b64, is_b64, impath_2_b64

import models.llm.gpt3 as gpt3

STATIC_IMDIR = os.path.join(CWD,"client","public")
SERVER_IMDIR = os.path.join(STATIC_IMDIR,"gen_images") 
SERVER_PRESET_IMDIR = os.path.join(STATIC_IMDIR,"preset_materials")
CLIENT_IMDIR = os.path.join("gen_images")
LATEST_RENDER_ID=0
use_chatgpt = True
RENDER_MODE = 'CYCLES'

MATERIAL_PRESETS = {
    "Concrete": os.path.join(SERVER_PRESET_IMDIR,"concrete01-1k","concrete01 diffuse 1k.jpg"), 
    "Wood": os.path.join(SERVER_PRESET_IMDIR,"wood-01-1k","wood 01 Diffuse.jpg"),
    "Wood2": os.path.join(SERVER_PRESET_IMDIR,"wood-05-1k","wood 05 diffuse 1k.jpg"),
    "Marble": os.path.join(SERVER_PRESET_IMDIR,"marble07-1k","marble07 diffuse 1k.jpg"),
    "Marble2": os.path.join(SERVER_PRESET_IMDIR,"Marble01-1k","Marble01 diffuse 1k.jpg"),
    "Fabric": os.path.join(SERVER_PRESET_IMDIR,"Fabric04-1k","Fabric04 diffuse 1k.jpg"),
    "Fabric2": os.path.join(SERVER_PRESET_IMDIR,"Fabric02-1k","Fabric03 diffuse 1k.jpg"),
    "Plaster": os.path.join(SERVER_PRESET_IMDIR,"plaster04-1k","plaster04 diffuse 1k.jpg"),
    "Stone": os.path.join(SERVER_PRESET_IMDIR,"stone08-1k","stone08 diffuse 1k.jpg"),
    "Stone2": os.path.join(SERVER_PRESET_IMDIR,"Stone03-1k","Stone04 diffuse 1k.jpg"),
    "Tiles": os.path.join(SERVER_PRESET_IMDIR,"tiles03-1k","tiles03 diffuse 1k.jpg"),
    "Tiles2": os.path.join(SERVER_PRESET_IMDIR,"tiles06-1k","tiles06 diffuse 1k.jpg"),
}

texture_generator = DALLE2()
# texture_generator = TextureDiffusion(model_id="runwayml/stable-diffusion-v1-5")

# fast_texture_generator = TextureDiffusion(model_id="runwayml/stable-diffusion-v1-5")


app = Flask(__name__, static_folder="./client/public")

@app.route("/translate", methods=['POST'])
def translate_gpt(): 
    form_data = request.get_json()
    text = form_data["text"]
    target_lang = form_data["target_lang"]
    source_lang = form_data["source_lang"]
    translated_text = gpt3.translate(text,target_lang,source_lang)
    return jsonify({"text":translated_text})

@app.route("/get_static_dir")
def get_static_dir():
    return STATIC_IMDIR

@app.route("/init_query", methods=['GET'])
def init_query():
    response = gpt3.init_query()
    return jsonify({"response":response,"role":"assistant"})

@app.route("/use_chatgpt", methods=['GET'])
def use_chatgpt():
    return jsonify({"use_chatgpt":use_chatgpt})

@app.route("/retrieve_textures_from_action_history", methods=['POST'])
def retrieve_textures_from_history():
    form_data = request.get_json()
    current_history_index = form_data["current_history_index"]
    no_material = os.path.join(SERVER_IMDIR,'renderings','current',"no_material.png")
    old = form_data["old_or_new"]
    old_img_path = form_data["old_img_path"]
    old_normal_path = form_data["old_normal_path"] if form_data["old_normal_path"] else no_material
    old_height_path = form_data["old_height_path"] if form_data["old_height_path"] else no_material

    old_img_filename = os.path.basename(old_img_path)
    old_normal_filename = os.path.basename(old_normal_path) 
    old_height_filename = os.path.basename(old_height_path) 

    curr_dir = os.path.join(SERVER_IMDIR,"renderings","current")

    updated_old_img_path = os.path.join(curr_dir,old_img_filename)
    updated_old_normal_path = os.path.join(curr_dir,old_normal_filename)
    updated_old_height_path = os.path.join(curr_dir,old_height_filename)

    Image.open(old_img_path).save(updated_old_img_path)
    Image.open(old_normal_path).save(updated_old_normal_path) 
    Image.open(old_height_path).save(updated_old_height_path)

    return jsonify({
        "updated_old_img_path":updated_old_img_path,
        "updated_old_normal_path":updated_old_normal_path,
        "updated_old_height_path":updated_old_height_path        
    })

@app.route("/add_old_and_new_textures_to_action_history", methods=['POST'])
def add_old_and_new_texures_to_history():
    form_data = request.get_json()
    no_material = os.path.join(SERVER_IMDIR,'renderings','current',"no_material.png")
    current_history_index = form_data["current_history_index"]
    old_img_path = form_data["old_img_path"]
    old_normal_path = form_data["old_normal_path"] if form_data["old_normal_path"] else no_material
    old_height_path = form_data["old_height_path"] if form_data["old_height_path"] else no_material

    old_img_filename = os.path.basename(old_img_path)
    old_normal_filename = os.path.basename(old_normal_path) 
    old_height_filename = os.path.basename(old_height_path) 

    new_img_path = form_data["new_img_path"]
    new_normal_path = form_data["new_normal_path"] if form_data["new_normal_path"] else no_material
    new_height_path = form_data["new_height_path"] if form_data["new_height_path"] else no_material

    new_img_filename = os.path.basename(new_img_path)
    new_normal_filename = os.path.basename(new_normal_path) 
    new_height_filename = os.path.basename(new_height_path) 

    action_history_dir = os.path.join(SERVER_IMDIR,"action_history")
    history_index_dir = os.path.join(action_history_dir, str(current_history_index))

    makedir(history_index_dir)
    makedir(os.path.join(history_index_dir,"old"))
    makedir(os.path.join(history_index_dir,"new"))

    updated_old_img_path = os.path.join(history_index_dir,"old",old_img_filename)
    updated_old_normal_path = os.path.join(history_index_dir,"old",old_normal_filename) 
    updated_old_height_path = os.path.join(history_index_dir,"old",old_height_filename) 

    Image.open(old_img_path).save(updated_old_img_path)
    Image.open(old_normal_path).save(updated_old_normal_path) 
    Image.open(old_height_path).save(updated_old_height_path)

    updated_new_img_path = os.path.join(history_index_dir,"new",new_img_filename)
    updated_new_normal_path = os.path.join(history_index_dir,"new",new_normal_filename) 
    updated_new_height_path = os.path.join(history_index_dir,"new",new_height_filename) 

    Image.open(new_img_path).save(updated_new_img_path)
    Image.open(new_normal_path).save(updated_new_normal_path) 
    Image.open(new_height_path).save(updated_new_height_path)

    return jsonify({
        "updated_old_img_path":updated_old_img_path,
        "updated_old_normal_path":updated_old_normal_path,
        "updated_old_height_path":updated_old_height_path,
        "updated_new_img_path":updated_new_img_path,
        "updated_new_normal_path":updated_new_normal_path,
        "updated_new_height_path":updated_new_height_path
    })

@app.route("/query", methods=['POST'])
def query():
    form_data = request.get_json()
    response = gpt3.query(form_data["prompt"],form_data["role"])
    return jsonify({"response":response,"role":"assistant"})

def format_references(references):
    references_str=""
    for ref in references:
        references_str+=f"{ref['number']}. [{ref['title']}]({ref['url']})\n"
    return references_str

@app.route("/transfer_texture", methods=['POST'])
def transfer_texture():
    form_data = request.get_json()
    src_url = form_data["src_url"]
    curr_textureparts_path = form_data["curr_textureparts_path"]
    curr_textureparts = form_data["curr_textureparts"]

    src_filename = os.path.basename(src_url)
    src_dir = os.path.dirname(src_url)
    src_filename_noext = os.path.splitext(src_filename)[0]
    src_ext= os.path.splitext(src_filename)[1]
    
    curr_dir = os.path.dirname(curr_textureparts_path)
    dest_url = os.path.join(curr_dir, src_filename)
    Image.open(src_url).save(dest_url)

    # Color to Normal Map. Create normal map from color map
    # Check if mat_image_normal exists in curr_textureparts
    normal_src_url = os.path.join(src_dir, f"{src_filename_noext}_normal{src_ext}")
    normal_dest_url = os.path.join(curr_dir, f"{src_filename_noext}_normal{src_ext}")
    Image.open(normal_src_url).save(normal_dest_url)

    # Normal to Height Map. Create height map from normal map
    # Check if mat_image_height exists in curr_textureparts
    height_src_url = os.path.join(src_dir, f"{src_filename_noext}_height{src_ext}")
    height_dest_url = os.path.join(curr_dir, f"{src_filename_noext}_height{src_ext}")
    Image.open(height_src_url).save(height_dest_url)

    # TEST GENERATING TEXTURES AND DRAGIGING
    return jsonify({
        "img_url":dest_url,
        "normal_url":normal_dest_url,
        "height_url":height_dest_url
    })

@app.route("/get_texture_prompts", methods=['POST'])
def get_texture_prompts():
    form_data = request.get_json()
    prompt = form_data["prompt"]
    n = form_data["n"]
    image_path = form_data["image_path"]
    design_brief = form_data["design_brief"]

    hardcoded_interior_state_path = os.path.join(SERVER_PRESET_IMDIR,"visual_context.png")
    hardcoded_interior_state_b64 = impath_2_b64(hardcoded_interior_state_path)

    # Convert image_path to b64
    image_b64 = impath_2_b64(image_path) 
    texture_prompts = gpt3.suggest_texture_prompts(prompt,n, image_b64, design_brief, interior_state=hardcoded_interior_state_b64)
    return jsonify({"texture_prompts":texture_prompts})

@app.route("/get_materials", methods=['POST'])
def get_materials():
    form_data = request.get_json()
    prompt = form_data["prompt"]
    n = form_data["n"]
    design_brief = form_data["design_brief"]
    material_name = form_data["material_name"]
    image_path = form_data["image_path"]

    hardcoded_interior_state_path = os.path.join(SERVER_PRESET_IMDIR,"visual_context.png")
    hardcoded_interior_state_b64 = impath_2_b64(hardcoded_interior_state_path)

    # Convert image_path to b64
    texture_image = impath_2_b64(image_path) 


    materials, explanations, prompts = gpt3.suggest_materials_texturebased(material_name, prompt, n, texture_image, design_brief, interior_state=hardcoded_interior_state_b64)
    return jsonify({
        "materials":materials,
        "explanations":explanations,
        "prompts":prompts
    })


@app.route("/feedback_materials", methods=['POST'])
def feedback_materials():
    material_feedback_start_time=time.time()
    form_data = request.get_json()
    material_name = form_data["material_name"]
    object_name = form_data["object_name"]
    part_name = form_data["part_name"]
    attached_parts = form_data["attached_parts"]
    design_brief = form_data["design_brief"]

    # intro_text, response, suggestions_dict, references = gpt3.provide_material_feedback(material_name, object_name, part_name, use_internet=True, attached_parts=attached_parts,design_brief=design_brief)
    intro_text, response, suggestions_dict, references = gpt3.provide_material_feedback2(material_name, object_name, part_name, use_internet=False, attached_parts=attached_parts,design_brief=design_brief)
    
    references_str = ""
    if references:
        references_str = format_references(references)

    for aspect in suggestions_dict:
        for suggestion in suggestions_dict[aspect]['suggestions']:
            type=suggestion[1]; name=suggestion[0]
            if type=="material":
                material_creation_start_time = time.time()
                texture_prompt = f"{name}, texture map, seamless, 4k"
                image, filenames = generate_textures(texture_prompt,n=1, imsize=256,generator=texture_generator); 
                image=image[0]; filename=filenames[0]
                filename = filename.replace(" ","_"); filename = filename.replace("/","_")
                filenames[0] = filename
                savepath = os.path.join(SERVER_IMDIR,"feedbacked",filename)
                image.save(savepath)
                normal_path, height_path = generate_normal_and_heightmap(savepath)
                # b64_url = im_2_b64(image)
                # suggestion.append(b64_url.decode('utf-8'))
                suggestion.append(savepath)
                material_creation_end_time = time.time()
                print(f"Time to create suggested material: {material_creation_end_time-material_creation_start_time}")
            elif type=="attachment":
                attachment_creation_start_time = time.time()
                texture_prompt = f"{name}, photorealistic, 4k"
                image, _ = generate_textures(texture_prompt,n=1, imsize=256,generator=texture_generator) 
                image=image[0]
                b64_url = im_2_b64(image)
                suggestion.append(b64_url.decode('utf-8'))
                attachment_creation_end_time = time.time()
                print(f"Time to create suggested attachment: {attachment_creation_end_time-attachment_creation_start_time}")
            # elif type=="finish": 
            #     finish_creation_start_time = time.time()
            #     suggested_finish_settings = gpt3.suggest_finish_settings(name, material_name, object_name, part_name)
            #     suggestion.append(suggested_finish_settings)
            #     finish_creation_end_time = time.time()
            #     print(f"Time to create suggested finish: {finish_creation_end_time-finish_creation_start_time}")
            else: 
                texture_prompt = f"{name}, photorealistic, 4k"
                image, _ = generate_textures(texture_prompt,n=1, imsize=256, generator=texture_generator); image=image[0]
                b64_url = im_2_b64(image)
                suggestion.append(b64_url.decode('utf-8'))
    # suggestions_creation_end_time = time.time()

    material_feedback_end_time=time.time()
    material_feedback_time = material_feedback_end_time-material_feedback_start_time
    print(f"Material feedback time: {material_feedback_time}")
    return jsonify({
        "intro_text":intro_text,
        "unformatted_response":response,
        "formatted_response":suggestions_dict,
        "references":references_str,
        "role":"assistant"
    })

@app.route("/suggest_materials_education", methods=['POST'])
def suggest_materials_education():
    form_data = request.get_json()
    context = form_data["context"]

    document_db = pd.read_pickle("./document_db.pickle")

    n_rows_documents = document_db.shape[0]
    top_n_documents = int(10)
    document_excerpts, relatednesses = e.strings_ranked_by_relatedness(
        form_data["prompt"], 
        document_db,
        top_n=top_n_documents
    )
    document_excerpts_string = "\n".join(document_excerpts)

    intro_text, suggested_materials_dict = gpt3.suggest_materials_3(form_data["prompt"],role=form_data["role"],resources=document_excerpts_string,design_brief=context)
    suggested_materials = []

    for sm in suggested_materials_dict:
        texture_prompt = f"{sm}, texture map, seamless, 4k"
        images, filenames = generate_textures(texture_prompt,n=1, imsize=256); 
        image=images[0]; filename=filenames[0]
        filename = filename.replace(" ","_"); filename = filename.replace("/","_")
        filenames[0] = filename
        savepath = os.path.join(SERVER_IMDIR,"suggested",filename)
        image.save(savepath)

        normal_path, height_path = generate_normal_and_heightmap(savepath)

        suggested_materials.append({
            "name":sm,
            "reason":suggested_materials_dict[sm],
            "filepath":savepath
        })

    return jsonify({"intro_text":intro_text,"role":"assistant","suggested_materials":suggested_materials})


@app.route("/suggest_materials", methods=['POST'])
def suggest_materials():
    start_time = time.time()
    form_data = request.get_json()
    context = form_data["context"]
    intro_text, suggested_materials_dict = gpt3.suggest_materials_2(form_data["prompt"],role=form_data["role"],use_internet=form_data["use_internet"],design_brief=context)
    suggested_materials = []
    for sm in suggested_materials_dict:
        texture_prompt = f"{sm}, texture map, seamless, 4k"
        images, filenames = generate_textures(texture_prompt,n=1, imsize=256); 
        image=images[0]; filename=filenames[0]
        filename = filename.replace(" ","_"); filename = filename.replace("/","_")
        filenames[0] = filename
        savepath = os.path.join(SERVER_IMDIR,"suggested",filename)
        image.save(savepath)

        normal_path, height_path = generate_normal_and_heightmap(savepath)

        suggested_materials.append({
            "name":sm,
            "reason":suggested_materials_dict[sm],
            "filepath":savepath
        })
    end_time = time.time()
    print(f"Time to create suggested materials: {end_time-start_time}")
    return jsonify({"intro_text":intro_text,"role":"assistant","suggested_materials":suggested_materials})



@app.route("/suggest_colors", methods=['POST'])
def suggest_colors():
    form_data = request.get_json()
    intro_text, suggested_color_palettes = gpt3.suggest_color_palettes(form_data["prompt"],role=form_data["role"],use_internet=form_data["use_internet"])
    return jsonify({"intro_text":intro_text,"role":"assistant","suggested_color_palettes":suggested_color_palettes})

@app.route("/brainstorm_prompt_keywords", methods=['POST']) 
def brainstorm_prompt_keywords():
    form_data = request.get_json()
    material_prompt = form_data["texture_string"]
    design_brief = form_data["design_brief"]

    brainstormed_prompt_keywords = gpt3.brainstorm_prompt_keywords(material_prompt,design_brief)
    # brainstormed_prompt_keywords = gpt3.brainstorm_prompt_keywords(material_prompt,None)
    return jsonify({"brainstormed_prompt_keywords":brainstormed_prompt_keywords,"role":"assistant"})


@app.route("/brainstorm_material_queries", methods=['GET'])
def brainstorm_material_queries():
    prompts = gpt3.brainstorm_material_queries()
    return jsonify({"prompts":prompts,"role":"assistant"})

@app.route("/get_preset_materials", methods=['GET'])
def get_presets():

    return jsonify({"preset_material_paths":MATERIAL_PRESETS})


@app.route("/get_image", methods=['POST'])
def get_image(): 
    form_data = request.get_json()
    img_data = form_data["image_data"]

    if is_b64(img_data):
        print("IT'S b64 URL")
        img_bytes = base64.b64decode(img_data)  
        return send_file(io.BytesIO(img_bytes),mimetype='image/png')
    else:
        print("Image data is not base64 encoded. Detecting it as an image path instead.")
    img_path = img_data 
    _, file_extension = os.path.splitext(img_path)
    return send_file(img_path,mimetype=f'image/{file_extension[1:]}')

@app.route("/generate_similar_textures",methods=['POST'])
def generate_similar_textures():
    form_data = request.get_json()
    texture_str = form_data["texture_string"]
    n_textures = form_data["n"]
    n_textures-=1
    impath = form_data["impath"]

    similar_textures = text2texture_similar(texture_str,impath,n_textures,gen_imsize=256)

    # texture_filenames = []
    impath = impath.replace(" ","_")
    texture_loadpaths = [{
        'rendering': None,
        'texture': impath
    }]
    for i in range(0,len(similar_textures)):
        texture_filename = f"{texture_str}_similar_{i+1}.png"
        texture_filename = texture_filename.replace(" ","_")
        savepath = os.path.join(SERVER_IMDIR,texture_filename)
        similar_textures[i].save(savepath)
        normal_path, height_path = generate_normal_and_heightmap(savepath)
        texture_loadpaths.append({
            'rendering': None,
            'texture': savepath
        })
    return {"results": texture_loadpaths}



@app.route("/generate_textures", methods=['POST'])
def generate_textures_():
    form_data = request.get_json()
    texture_string = form_data["texture_string"]
    n = form_data["n"]
    imsize = form_data["imsize"]
    # emptydir(SERVER_IMDIR,delete_dirs=False)
    #################### Generating the textures ################
    textures, filenames = generate_textures(texture_string, n, imsize)

    texture_savepaths = []


    texture_loadpaths = []
    for i in range(len(textures)):
        filenames[i] = filenames[i].replace(" ","_")
        savepath = os.path.join(SERVER_IMDIR,filenames[i])
        textures[i].save(savepath)
        normal_path, height_path = generate_normal_and_heightmap(savepath)

        texture_loadpaths.append({
            'rendering': None,
            'texture': savepath
        })

    return {"results": texture_loadpaths}

@app.route("/apply_textures", methods=['POST'])
def apply_textures():
    form_data = request.get_json()
    obj_part_dict = form_data["obj_parts_dict"]
    selected_texturepaths = form_data["selected_texturepaths"]
    texture_string = form_data["texture_string"]

    emptydir(os.path.join(SERVER_IMDIR,"renderings"),delete_dirs=False)

    #################### Transferring the textures ##############
    rendering_texture_pairs = []

    for i in range(len(selected_texturepaths)):
        filename = os.path.basename(selected_texturepaths[i])
        texture_savepath = os.path.join(SERVER_IMDIR,filename)

        new_texture_parts = copy.deepcopy(current_texture_parts)
        for obj in list(obj_part_dict.keys()):
            for part in obj_part_dict[obj]:
                new_texture_parts[obj][part]["mat_name"]=texture_string
                new_texture_parts[obj][part]["mat_image_texture"]=texture_savepath

        
        tmp_texture_parts_savepath = os.path.join(SERVER_IMDIR,"renderings",f"texture_parts_{i}.json")
        
        with open(tmp_texture_parts_savepath,"w") as tmpfile:
            json.dump(new_texture_parts,tmpfile,indent=4)

        rendering_savepath = os.path.join(SERVER_IMDIR,"renderings",f"rendering_{i}.png")
        
        command_str = f'blender --background --python render_obj_and_textures.py -- --out_path {rendering_savepath} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {tmp_texture_parts_savepath} --render_mode {RENDER_MODE}'
        os.system(command_str)

        rendering_texture_pairs.append(
            {'rendering':rendering_savepath, 'texture':texture_savepath, 'info':new_texture_parts, 'info_path':tmp_texture_parts_savepath}
        )

    return {"results": rendering_texture_pairs}

def generate_normal_and_heightmap(texture_filepath):
    
    dir = os.path.dirname(texture_filepath)
    filename = os.path.basename(texture_filepath)
    filename_noext = os.path.splitext(filename)[0]

    #  Color to Normal Map. Create normal map from color map
    normal_path = os.path.join(dir, f"{filename_noext}_normal.png")
    color_to_normal_command = f'python {CWD}/utils/DeepBump-7/cli.py {texture_filepath} {normal_path} color_to_normals --color_to_normals-overlap MEDIUM'
    normalmap_start_time = time.time()
    os.system(color_to_normal_command)
    normalmap_end_time = time.time()
    print(f"Time to create normal map: {normalmap_end_time-normalmap_start_time}")

    # Normal to Height Map. Create height map from normal map
    height_path = os.path.join(dir, f"{filename_noext}_height.png")
    normal_to_height_command = f'python {CWD}/utils/DeepBump-7/cli.py {normal_path} {height_path} normals_to_height --normals_to_height-seamless TRUE'
    heightmap_start_time = time.time()
    os.system(normal_to_height_command)
    heightmap_end_time = time.time()

    # print(f"Time to create height map: {heightmap_end_time-heightmap_start_time}")

    return normal_path, height_path


def generate_textures(texture_string, n, imsize, generator=texture_generator):
    generated_textures = generator.text2texture(texture_string, n=n, gen_imsize=imsize)
    texture_filenames = []

    for i in range(len(generated_textures)):
        texture_filenames.append(f"{texture_string}_{i}.png")
    return generated_textures, texture_filenames

def apply_to_current_rendering(renderpath, texture_parts_path):
    global current_texture_parts
    curr_render_savedir = os.path.join(SERVER_IMDIR,'renderings','current')
    curr_render_loaddir = os.path.join(CLIENT_IMDIR,'renderings','current')

    if(not os.path.isdir(curr_render_savedir)):
        makedir(curr_render_savedir)
    
    # emptydir(curr_render_savedir)
    
    curr_render_path = os.path.join(curr_render_savedir,"rendering.png")
    curr_textureparts_path = os.path.join(curr_render_savedir,"object_part_material.json")

    texture_parts = json.load(open(texture_parts_path))

    texture_filenames = []
    for obj in list(texture_parts.keys()):
        for part in list(texture_parts[obj].keys()):
            # This portion is to copy the texture to the current rendering directory
            texture_path = texture_parts[obj][part]["mat_image_texture"]
            texture_filename = os.path.basename(texture_path)
            curr_texture_path = os.path.join(curr_render_savedir,texture_filename)
            Image.open(texture_path).save(curr_texture_path)
            texture_parts[obj][part]["mat_image_texture"] = curr_texture_path

            if("mat_normal_texture" in list(texture_parts[obj][part].keys())):
                normal_path = texture_parts[obj][part]["mat_normal_texture"]
                normal_filename = os.path.basename(normal_path)
                curr_normal_path = os.path.join(curr_render_savedir,normal_filename)
                Image.open(normal_path).save(curr_normal_path)
                texture_parts[obj][part]["mat_normal_texture"] = curr_normal_path
            
            if("mat_height_texture" in list(texture_parts[obj][part].keys())):
                height_path = texture_parts[obj][part]["mat_height_texture"]
                height_filename = os.path.basename(height_path)
                curr_height_path = os.path.join(curr_render_savedir,height_filename)
                Image.open(height_path).save(curr_height_path)
                texture_parts[obj][part]["mat_height_texture"] = curr_height_path

            # This portion is to copy the model to the current rendering directory
            if("model" in list(texture_parts[obj][part].keys())):
                model_path = texture_parts[obj][part]["model"] #Note: the model is a .gltf file which includes the texture map from ["mat_image_texture"]
                model_filename = os.path.basename(model_path)
                parent_obj = obj 
                texture_parts[obj][part]["model"] = os.path.join(curr_render_loaddir,parent_obj,model_filename)
                destpath = os.path.join(curr_render_savedir,parent_obj,model_filename)
                if not os.path.exists(destpath):
                    os.makedirs(os.path.dirname(destpath), exist_ok=True)
                shutil.copy(model_path, destpath)   

    current_texture_parts = copy.deepcopy(texture_parts)
    with open(curr_textureparts_path,"w") as f:
        json.dump(texture_parts,f,indent=4)

    shutil.copy(renderpath, curr_render_path) 
    print("done applying to current rendering!")
    return curr_render_path, curr_textureparts_path

@app.route("/save_model", methods=['POST'])
def update_3d_model():
    form_data = request.get_json()
    model = form_data["model"]
    model_name = form_data["name"]
    model_parent = form_data["parent"]
    model_path = form_data["url"]
    server_model_path = os.path.join(STATIC_IMDIR,model_path)
    filename, fileext = os.path.splitext(server_model_path)
    server_model_path = filename + ".gltf"

    with open(server_model_path,'w') as f:
        f.write(model)
    
    return "ok"

@app.route("/render", methods=['POST'])
def render():
    global current_texture_parts
    form_data = request.get_json()
    renderpath = form_data['renderpath']
    textureparts = form_data['textureparts']
    texturepartspath = form_data['texturepartspath']
    
    # curr_render_loaddir = os.path.join(CLIENT_IMDIR,'renderings','current')
    curr_render_savedir = os.path.join(SERVER_IMDIR,'renderings','current')
    for obj in list(textureparts.keys()):
        for part in list(textureparts[obj].keys()):
            # This portion is to add the current rendering directory to the model path 
            if("model" in list(textureparts[obj][part].keys())):
                model_path = textureparts[obj][part]["model"] #Note: the model is a .gltf file which includes the texture map from ["mat_image_texture"]
                model_filename = os.path.basename(model_path)
                parent_obj = obj 
                destpath = os.path.join(curr_render_savedir,parent_obj,model_filename)
                if not os.path.exists(destpath):
                    os.makedirs(os.path.dirname(destpath), exist_ok=True)
                textureparts[obj][part]["model"] = os.path.join(curr_render_savedir,parent_obj,model_filename) 
    # current_texture_parts = copy.deepcopy(textureparts)

    with open(texturepartspath,"w") as f:
        json.dump(textureparts,f,indent=4)

    # Code to render initial rendering. Uncomment the below code if you want to re-render the initial rendering.
    command_str = f'blender --background --python render_obj_and_textures.py -- --out_path {renderpath} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {texturepartspath} --render_mode {RENDER_MODE}'
    os.system(command_str)

    # # Code to load current rendering into frontend (client folder).
    # init_texture_parts = json.load(open(os.path.join(RENDER_DIR, "current","object_part_material.json")))
    # current_texture_parts = copy.deepcopy(init_texture_parts)
    return "ok"


@app.route("/apply_to_current_rendering", methods= ['POST'])
def set_current_rendering():
    form_data = request.get_json()

    rendering_path = os.path.join(CWD,"client","public", form_data["rendering_path"])
    texture_parts = form_data["texture_parts"]
    textureparts_path = form_data["textureparts_path"]

    curr_renderpath, curr_textureparts_path = apply_to_current_rendering(rendering_path,textureparts_path)

    return get_current_rendering()

def add_to_saved_renderings(renderpath, texture_parts_path):
    global LATEST_RENDER_ID

    save_render_dir = os.path.join(SERVER_IMDIR,'renderings','saved',str(LATEST_RENDER_ID))
    save_render_path = os.path.join(save_render_dir,"rendering.png")
    save_textureparts_path = os.path.join(save_render_dir,"object_part_material.json")
    
    if(not os.path.isdir(save_render_dir)):
        makedir(save_render_dir)
    
    texture_parts = json.load(open(texture_parts_path))
    for obj in list(texture_parts.keys()):
        for part in list(texture_parts[obj].keys()):
            texture_path = texture_parts[obj][part]["mat_image_texture"]
            texture_filename = os.path.basename(texture_path)
            save_texture_path = os.path.join(save_render_dir,texture_filename)
            Image.open(texture_path).save(save_texture_path)
            texture_parts[obj][part]["mat_image_texture"] = save_texture_path

            if("mat_normal_texture" in list(texture_parts[obj][part].keys())):
                normal_path = texture_parts[obj][part]["mat_normal_texture"]
                normal_filename = os.path.basename(normal_path)
                save_normal_path = os.path.join(save_render_dir,normal_filename)
                Image.open(normal_path).save(save_normal_path)
                texture_parts[obj][part]["mat_normal_texture"] = save_normal_path
            
            if("mat_height_texture" in list(texture_parts[obj][part].keys())):
                height_path = texture_parts[obj][part]["mat_height_texture"]
                height_filename = os.path.basename(height_path)
                save_height_path = os.path.join(save_render_dir,height_filename)
                Image.open(height_path).save(save_height_path)
                texture_parts[obj][part]["mat_height_texture"] = save_height_path

            # This portion is to copy the model to the current rendering directory
            if("model" in list(texture_parts[obj][part].keys())):
                model_path = texture_parts[obj][part]["model"] #Note: the model is a .gltf file which includes the texture map from ["mat_image_texture"]
                model_filename = os.path.basename(model_path)
                parent_obj = obj 
                destpath = os.path.join(save_render_dir,parent_obj,model_filename)
                if not os.path.exists(destpath):
                    os.makedirs(os.path.dirname(destpath), exist_ok=True)
                texture_parts[obj][part]["model"] = destpath
                full_model_path = os.path.join(STATIC_IMDIR,model_path)
                shutil.copy(full_model_path, destpath)   
    
    with open(save_textureparts_path,"w") as f:
        json.dump(texture_parts,f,indent=4)
    shutil.copy(renderpath, save_render_path)
    LATEST_RENDER_ID+=1
    return save_render_path,save_textureparts_path

@app.route("/save_rendering", methods=['POST'])
def save_rendering():
    form_data = request.get_json()
    rendering_path =  os.path.join(CWD,"client","public",form_data["rendering_path"])
    texture_parts = form_data["texture_parts"]
    textureparts_path = form_data["textureparts_path"]

    # Add to saved renderings
    add_to_saved_renderings(rendering_path,textureparts_path)
    return  get_saved_renderings()

@app.route("/get_saved_renderings")
def get_saved_renderings():
    saved_renderings = []
    saved_renderings_loaddir_client = os.path.join(CLIENT_IMDIR,'renderings','saved')
    saved_renderings_loaddir_server = os.path.join(SERVER_IMDIR,'renderings','saved')

    dir_names = [f for f in os.listdir(saved_renderings_loaddir_server) if os.path.isdir(os.path.join(saved_renderings_loaddir_server, f))]
    dir_names.reverse()

    for d in dir_names:
        saved_rendering_loaddir = os.path.join(saved_renderings_loaddir_client,d)
        textureparts_path = os.path.join(saved_renderings_loaddir_server,d,"object_part_material.json")
        texture_parts = json.load(open(textureparts_path))
        render_path = os.path.join(saved_rendering_loaddir,"rendering.png")
        saved_renderings.append({
            "rendering_path":render_path,
            "texture_parts":texture_parts,
            "textureparts_path":textureparts_path
        })

    return {"saved_renderings":saved_renderings}

@app.route("/get_current_rendering")
def get_current_rendering():
    print("Getting current rendering")
    # curr_render_loaddir = os.path.join(CLIENT_IMDIR,'renderings','current')
    curr_render_savedir = os.path.join(SERVER_IMDIR,'renderings','current')

    current_textureparts_path = os.path.join(SERVER_IMDIR,'renderings','current',"object_part_material.json")
    texture_parts = json.load(open(current_textureparts_path))

    for obj in list(texture_parts.keys()):
        for part in list(texture_parts[obj].keys()):
            texture_path = texture_parts[obj][part]["mat_image_texture"]
            texture_parts[obj][part]["mat_image_texture"] = texture_path

    current_render_path = os.path.join(curr_render_savedir,"rendering.png")
    
    return {"rendering_path":current_render_path, "texture_parts":texture_parts, "textureparts_path":current_textureparts_path}

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

'''
STATIC_IMDIR = os.path.join(CWD,"client","public")
SERVER_IMDIR = os.path.join(STATIC_IMDIR,"gen_images") 
CLIENT_IMDIR = os.path.join("gen_images")
LATEST_RENDER_ID=0
use_chatgpt = True
RENDER_MODE = 'CYCLES'
'''
if __name__ == "__main__":

    # If starting a new scene
    ############################################
    emptydir(SERVER_IMDIR,delete_dirs=True)

    # Here, you should make the necessary dirs under client/public.
    makedir(SERVER_IMDIR)
    makedir(os.path.join(SERVER_IMDIR,"suggested"))
    makedir(os.path.join(SERVER_IMDIR,"feedbacked"))
    makedir(os.path.join(SERVER_IMDIR,"generated"))
    makedir(os.path.join(SERVER_IMDIR,"action_history"))
    makedir(os.path.join(SERVER_IMDIR,"renderings","current"))
    makedir(os.path.join(SERVER_IMDIR,"renderings","saved"))
    
    

    products = [
        "nightstand_family",
        "bedroom",
        "pool-side",
        "pool-side-small",
        "regular_bathroom",
    ]

    DATA_DIR = os.path.join(os.getcwd(),"data","3d_models",products[3]) #Dir where the 3D scene (information, models, textures, renderings) is stored
    RENDER_DIR = os.path.join(DATA_DIR,"renderings")
    rendering_setup_path = os.path.join(DATA_DIR,"rendering_setup.json")

    init_texture_parts_path = os.path.join(RENDER_DIR, "current","object_part_material.json")
    init_render_path = os.path.join(RENDER_DIR,"current","rendering.png")

    # Code to render initial rendering. Uncomment the below code if you want to re-render the initial rendering.
    # command_str = f'blender --background --python render_obj_and_textures.py -- --out_path {init_render_path} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {init_texture_parts_path} --render_mode {RENDER_MODE}'
    # os.system(command_str)

    # Code to load current rendering into frontend (client folder).
    init_texture_parts = json.load(open(init_texture_parts_path))
    current_texture_parts = copy.deepcopy(init_texture_parts)
    apply_to_current_rendering(init_render_path,init_texture_parts_path)

    init_saved_renderings_dir = os.path.join(RENDER_DIR,"saved")
    dir_names = list(map(int,[f for f in os.listdir(init_saved_renderings_dir) if os.path.isdir(os.path.join(init_saved_renderings_dir, f))]))

    # Code to load the saved renderings into frontend (client folder)
    for d in dir_names:
        dir_path = os.path.join(init_saved_renderings_dir,str(d))
        render_path = os.path.join(dir_path,"rendering.png")
        textureparts_path = os.path.join(dir_path,"object_part_material.json")
        add_to_saved_renderings(render_path,textureparts_path)
    
    #####################################################




    print(f"Latest rendering ID: {LATEST_RENDER_ID}")

    app.run(debug=False,port=2099)


