from flask import Flask, send_from_directory, request, jsonify, send_file
import random, requests, json, copy, shutil, os, base64, io, time
from PIL import Image
from texture_transfer_3d import TextureDiffusion, DALLE2, text2texture_similar
from configs import *


from utils.image import makedir, emptydir, degrees_to_radians, im_2_b64, is_b64

import models.llm.gpt3 as gpt3

STATIC_IMDIR = os.path.join(CWD,"client","public")
SERVER_IMDIR = os.path.join(STATIC_IMDIR,"gen_images") 
CLIENT_IMDIR = os.path.join("gen_images")
LATEST_RENDER_ID=0
use_chatgpt = True
RENDER_MODE = 'CYCLES'

app = Flask(__name__, static_folder="./client/public")

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
    
    curr_dir = os.path.dirname(curr_textureparts_path)
    dest_url = os.path.join(curr_dir, src_filename)
    Image.open(src_url).save(dest_url)

    # Color to Normal Map. Create normal map from color map
    # Check if mat_image_normal exists in curr_textureparts
    normal_src_url = os.path.join(src_dir, f"{src_filename_noext}_normal.png")
    normal_dest_url = os.path.join(curr_dir, f"{src_filename_noext}_normal.png")
    Image.open(normal_src_url).save(normal_dest_url)
    # color_to_normal_command = f'python {CWD}/utils/DeepBump-7/cli.py {src_url} {normal_url} color_to_normals --color_to_normals-overlap MEDIUM'
    # normalmap_start_time = time.time()
    # os.system(color_to_normal_command)
    # normalmap_end_time = time.time()
    # print(f"Time to create normal map: {normalmap_end_time-normalmap_start_time}")

    # Normal to Height Map. Create height map from normal map
    # Check if mat_image_height exists in curr_textureparts
    height_src_url = os.path.join(src_dir, f"{src_filename_noext}_height.png")
    height_dest_url = os.path.join(curr_dir, f"{src_filename_noext}_height.png")
    Image.open(height_src_url).save(height_dest_url)
    # normal_to_height_command = f'python {CWD}/utils/DeepBump-7/cli.py {normal_url} {height_url} normals_to_height --normals_to_height-seamless TRUE'
    # heightmap_start_time = time.time()
    # os.system(normal_to_height_command)
    # heightmap_end_time = time.time()
    # print(f"Time to create height map: {heightmap_end_time-heightmap_start_time}")
    # TEST GENERATING TEXTURES AND DRAGIGING
    return jsonify({
        "img_url":dest_url,
        "normal_url":normal_dest_url,
        "height_url":height_dest_url
    })

@app.route("/feedback_materials", methods=['POST'])
def feedback_materials():
    form_data = request.get_json()
    material_name = form_data["material_name"]
    object_name = form_data["object_name"]
    part_name = form_data["part_name"]
    attached_parts = form_data["attached_parts"]
    design_brief = form_data["design_brief"]

    intro_text, response, suggestions_dict, references = gpt3.provide_material_feedback(material_name, object_name, part_name, use_internet=True, attached_parts=attached_parts,design_brief=design_brief)
    references_str = format_references(references)

    for aspect in suggestions_dict:
        for suggestion in suggestions_dict[aspect]['suggestions']:
            type=suggestion[1]; name=suggestion[0]
            if type=="material":
                material_creation_start_time = time.time()
                texture_prompt = f"{name}, texture map, seamless, 4k"
                image, _ = generate_textures(texture_prompt,n=1, imsize=448); image=image[0]
                b64_url = im_2_b64(image)
                suggestion.append(b64_url.decode('utf-8'))
                material_creation_end_time = time.time()
                print(f"Time to create suggested material: {material_creation_end_time-material_creation_start_time}")
            elif type=="attachment":
                attachment_creation_start_time = time.time()
                texture_prompt = f"{name}, photorealistic, 4k"
                image, _ = generate_textures(texture_prompt,n=1, imsize=448); image=image[0]
                b64_url = im_2_b64(image)
                suggestion.append(b64_url.decode('utf-8'))
                attachment_creation_end_time = time.time()
                print(f"Time to create suggested attachment: {attachment_creation_end_time-attachment_creation_start_time}")
            elif type=="finish": 
                finish_creation_start_time = time.time()
                suggested_finish_settings = gpt3.suggest_finish_settings(name, material_name, object_name, part_name)
                suggestion.append(suggested_finish_settings)
                finish_creation_end_time = time.time()
                print(f"Time to create suggested finish: {finish_creation_end_time-finish_creation_start_time}")
            else: 
                texture_prompt = f"{name}, photorealistic, 4k"
                image, _ = generate_textures(texture_prompt,n=1, imsize=448); image=image[0]
                b64_url = im_2_b64(image)
                suggestion.append(b64_url.decode('utf-8'))
    # suggestions_creation_end_time = time.time()

                
    return jsonify({
        "intro_text":intro_text,
        "unformatted_response":response,
        "formatted_response":suggestions_dict,
        "references":references_str,
        "role":"assistant"
    })

@app.route("/suggest_materials", methods=['POST'])
def suggest_materials():
    form_data = request.get_json()
    context = form_data["context"]
    intro_text, suggested_materials_dict = gpt3.suggest_materials(form_data["prompt"],role=form_data["role"],use_internet=form_data["use_internet"],design_brief=context)
    suggested_materials = []
    for sm in suggested_materials_dict:
        texture_prompt = f"{sm}, texture map, seamless, 4k"
        images, filenames = generate_textures(texture_prompt,n=1, imsize=448); image=images[0]; filename=filenames[0]
        filename = filename.replace(" ","_"); filenames[0] = filename
        savepath = os.path.join(SERVER_IMDIR,"suggested",filename)


        image.save(savepath)
        suggested_materials.append({
            "name":sm,
            "reason":suggested_materials_dict[sm],
            "filepath":savepath
        })
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

    brainstormed_prompt_keywords = gpt3.brainstorm_prompt_keywords(material_prompt)
    return jsonify({"brainstormed_prompt_keywords":brainstormed_prompt_keywords,"role":"assistant"})


@app.route("/brainstorm_material_queries", methods=['GET'])
def brainstorm_material_queries():
    prompts = gpt3.brainstorm_material_queries()
    return jsonify({"prompts":prompts,"role":"assistant"})

@app.route("/get_feedback_on_assembly", methods=['POST'])
def feedback_on_assembly():
    form_data = request.get_json()

    object = form_data["object"]
    child_part = form_data["child_part"]; child_material = form_data["child_material"]
    parent_part = form_data["parent_part"]; parent_material = form_data["parent_material"]

    recommended_attachments = gpt3.feedback_on_assembly(object,child_part,child_material,parent_part,parent_material)
    return recommended_attachments

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
                new_texture_parts[obj][part]["mat_image_texture"]=os.path.join(SERVER_IMDIR,filenames[i])

        tmp_texture_parts_savepath = os.path.join(SERVER_IMDIR,"renderings",f"texture_parts_{i}.json")
        
        with open(tmp_texture_parts_savepath,"w") as tmpfile:
            json.dump(new_texture_parts,tmpfile,indent=4)

        rendering_savepath = os.path.join(SERVER_IMDIR,"renderings",f"rendering_{i}.png")
        rendering_loadpath = os.path.join(CLIENT_IMDIR,"renderings",f"rendering_{i}.png")

        command_str = f'blender --background --python render_obj_and_textures.py -- --out_path {rendering_savepath} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {tmp_texture_parts_savepath} --render_mode {RENDER_MODE}'
        os.system(command_str)

        rendering_texture_pairs.append(
            {'rendering':rendering_loadpath, 'texture':texture_loadpath, 'info':new_texture_parts, 'info_path':tmp_texture_parts_savepath}
        )

    return {"results": rendering_texture_pairs}

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
    texture_loadpaths = [{
        'rendering': None,
        'texture': impath
    }]
    for i in range(0,len(similar_textures)):
        texture_filename = f"{texture_str}_similar_{i+1}.png"
        savepath = os.path.join(SERVER_IMDIR,texture_filename)
        similar_textures[i].save(savepath)
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

    print(f"Time to create height map: {heightmap_end_time-heightmap_start_time}")

    return normal_path, height_path


def generate_textures(texture_string, n, imsize):
    generated_textures = texture_generator.text2texture(texture_string, n=n, gen_imsize=imsize)
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
                # textureparts[obj][part]["model"] = os.path.join(curr_render_savedir,model_filename) 
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
            # 'C:\\Users\\r-gal\\OneDrive\\Documents\\Academics\\PhD\\exploring-textures-with-stablediffusion\\client\\public\\gen_images\\renderings\\current\\blue marble.png'
            texture_path = texture_parts[obj][part]["mat_image_texture"]
            # Output should be gen_images\\renderings\\current\\blue marble.png'
            # texture_parts[obj][part]["mat_image_texture"] = texture_path.replace(STATIC_IMDIR,"")
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
'''

if __name__ == "__main__":

    # Here, you should make the necessary dirs under client/public.
    
    ######################################
    # texture_generator = TextureDiffusion(model_id="runwayml/stable-diffusion-v1-5")
    texture_generator = DALLE2()
    emptydir(SERVER_IMDIR,delete_dirs=False)
    emptydir(os.path.join(SERVER_IMDIR,"renderings","current"),delete_dirs=True)
    emptydir(os.path.join(SERVER_IMDIR,"renderings","saved"),delete_dirs=True)

    products = [
        "nightstand_family",
        "bedroom",
        "pool-side"
    ]

    DATA_DIR = os.path.join(os.getcwd(),"data","3d_models",products[2]) #Dir where the 3D scene (information, models, textures, renderings) is stored
    RENDER_DIR = os.path.join(DATA_DIR,"renderings")
    rendering_setup_path = os.path.join(DATA_DIR,"rendering_setup.json")

    init_texture_parts_path = os.path.join(RENDER_DIR, "current","object_part_material.json")
    # init_texture_parts_path = os.path.join(RENDER_DIR, "current","object_part_material_new.json")
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
    
    print(f"Latest rendering ID: {LATEST_RENDER_ID}")

    app.run(debug=True,port=2099)




################################# DUMPSTER #########################################



@app.route("/add_color_to_rendering", methods=['POST'])
def add_color_to_rendering():
    form_data = request.get_json()
    texture_parts = form_data["selected_textureparts"]
    textureparts_path = form_data["selected_textureparts_path"]
    render_path = form_data["selected_rendering"]
    obj = form_data["selected_obj"]
    part = form_data["selected_part"]

    texture_parts[obj][part]["mat_color"] = form_data["color"] if "color" in list(form_data.keys()) else None

    with open(textureparts_path,"w") as f:
        json.dump(texture_parts,f,indent=4)

    command_str = f'blender --background --python render_obj_and_textures.py -- --out_path {render_path} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {textureparts_path} --render_mode CYCLES'
    os.system(command_str)
    return {"updated_rendering": render_path, "updated_textureparts": texture_parts,"updated_textureparts_path": textureparts_path,}

@app.route("/add_finish_to_rendering", methods=['POST'])
def add_finish_to_rendering():
    form_data = request.get_json()
    texture_parts = form_data["selected_textureparts"]
    textureparts_path = form_data["selected_textureparts_path"]
    render_path = form_data["selected_rendering"]
    obj = form_data["selected_obj"]
    part = form_data["selected_part"]
    texture_parts[obj][part]["mat_finish"] = form_data["finish"]
    texture_parts[obj][part]["mat_finish_settings"] = form_data["psbdf_settings"]

    with open(textureparts_path,"w") as f:
        json.dump(texture_parts,f,indent=4)

    command_str = f'blender --background --python render_obj_and_textures.py -- --out_path {render_path} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {textureparts_path}'
    os.system(command_str)
    return {"updated_rendering": render_path, "updated_textureparts": texture_parts,"updated_textureparts_path": textureparts_path,}

@app.route("/add_transform_to_rendering", methods=['POST'])
def add_transform_to_rendering():
    form_data = request.get_json()
    texture_parts = form_data["selected_textureparts"]
    textureparts_path = form_data["selected_textureparts_path"]
    render_path = form_data["selected_rendering"]
    obj = form_data["selected_obj"]
    part = form_data["selected_part"]

    location = tuple(form_data["location"])
    rotation = tuple(form_data["rotation"])
    rotation = tuple(degrees_to_radians(deg) for deg in rotation)
    scale = tuple(form_data["scale"])

    texture_parts[obj][part]["mat_transforms"]= {
        "location": location,
        "rotation": rotation,
        "scale": scale
    }

    with open(textureparts_path,"w") as f:
        json.dump(texture_parts,f,indent=4)

    command_str = f'blender --background --python render_obj_and_textures.py -- --out_path {render_path} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {textureparts_path}'
    os.system(command_str)
    return {"updated_rendering": render_path, "updated_textureparts": texture_parts,"updated_textureparts_path": textureparts_path,}

@app.route("/suggest_colors_by_style", methods=['POST'])
def suggest_colors_by_style():
    form_data = request.get_json()
    style = form_data["style"]
    suggested_color_palettes=[]
    color_palettes_dict = gpt3.suggest_color_by_style(style=style)

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

    materials = gpt3.suggest_materials_by_style(style=style,material_type=material_type)

    suggested_materials = []
    for m in materials:
        reason=m["reason"] ; m = m["name"];
        prompt = m if material_type.lower()=='all types' else f"{m} {material_type}"
        image, filename = generate_textures(prompt,n=1,imsize=448); image=image[0]; filename=filename[0]
        savepath = os.path.join(SERVER_IMDIR,"suggested",filename)
        image.save(savepath)
        # loadpath = os.path.join(CLIENT_IMDIR,"suggested",filename)
        suggested_materials.append({
            "name":m,
            "reason":reason,
            "filepath":savepath
        })
    
    return suggested_materials