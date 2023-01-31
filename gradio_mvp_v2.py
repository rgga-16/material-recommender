import gradio as gr
from texture_transfer_3d import TextureDiffusion
from models.text2image.paella import net
import os, time, json, copy
import pathlib as p
from PIL import Image
from models.llm import bloom_inference_api as BLOOM_API
from models.llm.chatgpt_module import ChatGPT_Bot
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from utils.image import css 

from spacy import displacy
from spacy.matcher import Matcher
from nltk import tokenize


nlp = spacy.load("en_core_web_md")
nlp.add_pipe('spacytextblob')

#############################
# Set variables here
#############################
n_gen_materials = 4
gen_material = ""
gen_texture_choices_dict = {}
saved_renderings_list = []
saved_texture_parts = []
current_texture_parts = None 
curr_render_id = 1
#############################

bot = ChatGPT_Bot()

################# Load initial 3D model, textures, & rendering ################
products = [
    "nightstand_family",
]

data_dir = os.path.join(os.getcwd(),"data","3d_models",products[0])
rendering_setup_path = os.path.join(data_dir,"rendering_setup.json")

f=open(rendering_setup_path)
objects_data = json.load(f)

n_objects = objects_data["objects"]
renderings_dir = os.path.join(data_dir,"renderings")
init_texture_parts_path = os.path.join(renderings_dir, str(curr_render_id),"object_part_material.json")
f=open(init_texture_parts_path)
init_texture_parts = json.load(f)
current_texture_parts = copy.deepcopy(init_texture_parts)
current_material_specs = []
init_rendering_outdir = os.path.join(renderings_dir,str(curr_render_id))

command_str = f'blender --background --python render_obj_and_textures.py -- --out_dir {init_rendering_outdir} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {init_texture_parts_path}'
# command_str = f'blender --python render_obj_and_textures.py -- --out_dir {init_rendering_outdir} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {init_texture_parts_path}'
os.system(command_str)

init_rendering = Image.open(os.path.join(init_rendering_outdir,"rendering.png"))
saved_renderings_list.append(init_rendering)
######################################################

def transfer_material_texture(mat_option, finish_option, *part_inputs):

    global current_texture_parts
    global curr_obj_part_matname_txtboxes
    # global curr_part_matname_txtboxes

    selected_material_image = gen_texture_choices_dict[mat_option]
    selected_material_name = gen_material

    selected_material_finish = finish_option

    selected_material_impath = os.path.join(os.getcwd(),f'tmp/{selected_material_name}.png')
    selected_material_image.save(selected_material_impath)

    new_texture_parts = copy.deepcopy(current_texture_parts)
    new_curr_obj_part_matname_txtboxes = copy.deepcopy(curr_obj_part_matname_txtboxes)

    for object,parts in zip(object_inputs,part_inputs):
        for part in parts:
            new_texture_parts[object][part]["mat_name"]=selected_material_name
            new_texture_parts[object][part]["mat_finish"]=selected_material_finish
            new_texture_parts[object][part]["mat_image_texture"]=selected_material_impath

    current_texture_parts = new_texture_parts
    
    tmp_texture_parts_path = os.path.join(os.getcwd(),"tmp/texture_parts.json")
    with open(tmp_texture_parts_path,"w") as tmpfile:
        json.dump(current_texture_parts,tmpfile)
    
    tmp_rendering_outdir = os.path.join(os.getcwd(), "tmp")
    command_str = f'blender --background --python render_obj_and_textures.py -- --out_dir {tmp_rendering_outdir} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {tmp_texture_parts_path}'
    os.system(command_str)
    
    # Load rendered image
    rendering = Image.open(os.path.join(tmp_rendering_outdir,"rendering.png"))

    new_curr_part_matname_txtboxes = []
    for object in list(current_texture_parts.keys()):
        object_dict = current_texture_parts[object]
        
        part_txtboxes = []
        for part in list(object_dict.keys()):
            part_dict = object_dict[part]
            matpart_txtbox = gr.Textbox.update(value=part_dict['mat_name'],label=part)
            part_txtboxes.append(matpart_txtbox)
            new_curr_part_matname_txtboxes.append(matpart_txtbox)
        new_curr_obj_part_matname_txtboxes[object] = part_txtboxes


    return rendering, *new_curr_part_matname_txtboxes

def save_rendering(rendering):

    global current_texture_parts
    global curr_render_id
    global renderings_dir
    global saved_renderings_list
    curr_render_id+=1
    
    #create new dir in product/renderings/curr_id
    new_rendering_savedir = os.path.join(renderings_dir, str(curr_render_id))
    os.mkdir(new_rendering_savedir)

    #save texture images into the dir
    for obj in current_texture_parts: 
        for part in current_texture_parts[obj]:
            mat_name = current_texture_parts[obj][part]["mat_name"]
            old_texture_path = current_texture_parts[obj][part]["mat_image_texture"]
            img_texture = Image.open(old_texture_path)

            new_texture_path = os.path.join(new_rendering_savedir,f"{mat_name}.png")
            img_texture.save(new_texture_path)
            # Update the texture parts json to the new image texture paths.
            current_texture_parts[obj][part]["mat_image_texture"] = new_texture_path
    
    #save texture parts json into the dir
    save_texture_parts_path = os.path.join(new_rendering_savedir,"object_part_material.json")
    with open(save_texture_parts_path,"w") as tmpfile:
        json.dump(current_texture_parts,tmpfile)
    
    rendering_img = Image.fromarray(rendering.astype('uint8'), 'RGB')
    
    rendering_img.save(os.path.join(new_rendering_savedir,"rendering.png"))
    saved_renderings_list.append(rendering_img)
    return saved_renderings_list#Add rendering image to list

def generate_material_textures(material_str, n=n_gen_materials):
    global gen_material
    gen_material = material_str
    gen_texture_choices_dict.clear()
    material_textures = texture_generator.text2texture(material_str,n=n, gen_imsize=512)
    material_options = []; gen_mats = []
    for i in range(len(material_textures)):
        mat_texture = material_textures[i]
        mat_option = f"option_{i}"
        gen_texture_choices_dict[mat_option] = mat_texture
        gen_mats.append(gr.Image.update(value=mat_texture,label=mat_option))
        material_options.append(mat_option)
    return (gr.Radio.update(choices=material_options),*gen_mats)

def get_parts_from_object(object):
    global object_inputs
    selected_parts = copy.deepcopy(object_inputs[object]["parts"]["names"])
    selected_parts.insert(0,"No specific part")
    return gr.Dropdown.update(choices=selected_parts,value=selected_parts[0],visible=True)

def set_material_specs(descriptor_str):
    global current_material_specs
    descriptor_list = descriptor_str.split(";"); 
    descriptor_list = [d for d in descriptor_list if d.strip()]
    current_material_specs = descriptor_list
    descriptor_list.insert(0,"No descriptor")
    return gr.Dropdown.update(choices=descriptor_list,value=descriptor_list[0])

def set_targets(target_place, target_market):
    targets = [target_place,target_market]
    return gr.Dropdown.update(choices=targets,value=targets[0])

def make_suggest_prompt(material,design_style,descriptor,product,part,target):
    if part=="No specific part":
        part=""
    if material=="All materials":
        material=""
    if target=="No targets set":
        target=""
    if descriptor=="No descriptor":
        descriptor=""
    
    prompt = f"Examples of {material} materials"

    prompt = f"{prompt} that are of {design_style} "

    if descriptor!="":
        prompt = f"{prompt} and are {descriptor}"

    prompt = f"{prompt} for {product} {part}"

    if target != "":
        prompt = f"{prompt} for {target}"
    prompt = f"{prompt} are "
    return gr.Textbox.update(value=prompt,visible=True), gr.Button.update(visible=True)

def get_suggestion(prompt, selected_material_type):
    global nlp 
    # response = BLOOM_API.iterative_query(prompt) # Send prompt to BLOOM API here. Get their response.
    response = bot.ask(prompt)

    if selected_material_type=="No specific material":
        selected_material_type="material"
    
    filtered_response = response.replace(prompt,"")
    
    material_token = nlp(selected_material_type)
    response_embedding = nlp(filtered_response)

    similarities = [(i, material_token, material_token.similarity(i)) for i in response_embedding]

    sorted_similarities = sorted(similarities, key=lambda tup: tup[2], reverse=True)
    k=10
    sorted_similar_words = [tuple_[0] for tuple_ in sorted_similarities]

    top_k_words=sorted_similar_words[:k]

    top_k_words = [t.text for t in top_k_words]
    top_k_words_str = ", ".join(top_k_words)

    # top_k_words_str = f"Estimated material suggestions: {top_k_words_str}"
    # similarities = [(i, material_token, material_token.similarity(i)) for i in response_embedding if material_token.similarity(i) > similarity_threshold]
    return gr.Textbox.update(value=f"{response}"), gr.Textbox.update(value=f"{top_k_words_str}")


def parts_assembling_critique(product, mat1,part1,mat2,part2, n=1):
    # question = f"Can a {mat1} {product} {part1} be attached to a {mat2} {product} {part2}?"
    # prompt=question
    # response = get_critique(prompt)
    recommendation_prompt = f"What can be used to attach a {product} {part1} made of {mat1} to a {product} {part2} made of {mat2}? Give {n} recommendations."
    recommendation = get_critique(recommendation_prompt)
    return recommendation

def matspec_critique(matspec, material, product=None):

    if product is None:
        question = f"Is {material} a suitable material that is {matspec}?"
    else: 
        question = f"Is {material} a suitable material for a {product} that is {matspec}?"
    
    prompt = f'''
            Q: {question}
            A: Let's think step-by-step. 
    '''

    response = get_critique(prompt)

    # Sentimental Analysis
    doc = nlp(response)
    polarity = doc._.blob.polarity

    response = get_critique(prompt)
    return question, response, polarity

def critique_mats_by_spec(matspecs_critique_tab:gr.layouts.TabItem):

    matspec_critiques_tab.children=[]
    return matspec_critiques_tab

def environment_critique(target_env, material, material_type, product=None):

    if product is None: 
        question = f"Is {material} a suitable {material_type} material for {target_env}?"
    else: 
        question = f"Is {material} a suitable {material_type} material for a {product} for {target_env}?"
    
    prompt = f'''
        Q: {question}
        A: Let's think step-by-step. 
    '''

    response = get_critique(prompt)
    
    # Sentimental Analysis
    doc = nlp(response)
    polarity = doc._.blob.polarity
    
    response = get_critique(prompt)

    return question, response, polarity

def get_critique(prompt):
    global nlp 
    response = bot.ask(prompt)
    # response = BLOOM_API.iterative_query(prompt) # Send prompt to BLOOM API here. Get their response.
    filtered_response = response.replace(prompt,"")
    return filtered_response

selected_gen_texture = None 
texture_part_dict = {}
texture_generator = TextureDiffusion()
# texture_generator = net.Paella()
print('texture generator loaded')

gen_material_images = []
# obj_part_matname_txtboxes Contains dictionary of lists. Each key is an object; 
# its corresponding list is a list of textboxes, where each textbox shows the material of a part.
curr_obj_part_matname_txtboxes = {}
curr_part_matname_txtboxes = [] #List of all current parts
interface = gr.Blocks(css=css)

with interface:
    with gr.Accordion(label="Design Specifications",open=False) as design_specs:
        with gr.Row() as design_specs_row:
            with gr.Column():
                target_place = gr.Textbox(label="Target Place", interactive=True)
                target_market = gr.Textbox(label="Target Market", interactive=True)
                styles = ['Modern', 'Traditional', 'Contemporary', 'Industrial', 'Transitional', 'Rustic', 'Bohemian', 'Minimalist', 'Hollywood Regency', 'Scandinavian']
                interior_design_style = gr.Dropdown(choices = styles,label="Target Interior Design Style", interactive=True)
                set_targets_button = gr.Button(label="Set targets",value="Set targets")
            with gr.Column():
                gr.Markdown("Material Specifications for AI")
                descriptors = gr.Textbox(label="The materials should be... (separate each descriptor with a \";\") ", interactive=True)
                set_descriptors_button = gr.Button(value="Set descriptors")
    
    with gr.Row() as main_row:
        with gr.Column(variant="panel") as materials_generator_column:
            ####################################################################################
            # Left section. Section for generating material texture and transferring onto parts.
            ####################################################################################
            with gr.Column() as material_inputs:
                with gr.Column():
                    input_material = gr.Textbox(label="Input material texture")
                    generate_button = gr.Button("Generate")
                    with gr.Row() as material_outputs:
                        with gr.Column():
                            with gr.Row():
                                gen_img1 = gr.Image(interactive=False,shape=(128,128))
                                gen_material_images.append(gen_img1)
                                gen_img2 = gr.Image(interactive=False,shape=(128,128))
                                gen_material_images.append(gen_img2)
                            with gr.Row():
                                gen_img3 = gr.Image(interactive=False,shape=(128,128))
                                gen_material_images.append(gen_img3)
                                gen_img4 = gr.Image(interactive=False,shape=(128,128))
                                gen_material_images.append(gen_img4)
                        gen_material_options = gr.Radio(label="Material Options", interactive=True,choices=None,type="value")
                        
                        finishes = ['none','matte','glossy']
                        material_finish_options = gr.Radio(label="Material Finishes", value=finishes[0],interactive=True, choices = finishes,type="value")

                        part_inputs = []
                        object_inputs = objects_data["objects"]
                        with gr.Column():
                            for object in objects_data["objects"]:
                                with gr.Tab(f"{object}"):
                                    parts = objects_data["objects"][object]["parts"]["names"]
                                    checkboxes = gr.CheckboxGroup(choices=parts,label=object)
                                part_inputs.append(checkboxes)
                            transfer_button = gr.Button("Transfer textures")
            ####################################################################################

        ####################################################################################
        # Middle section. Section for generating material texture and transferring onto parts.
        ####################################################################################
        with gr.Column(variant="panel") as middle_section:
            with gr.Accordion(label="Current materials",open=False) as display_material_names_column: 
                # Iterate over current materials
                for object in list(current_texture_parts.keys()):
                    object_dict = current_texture_parts[object]
                    with gr.Tab(label=object):
                        with gr.Row():
                            part_txtboxes = []
                            for part in list(object_dict.keys()):
                                part_dict = object_dict[part]
                                matpart_txtbox = gr.Textbox(part_dict['mat_name'],label=part,interactive=False)
                                part_txtboxes.append(matpart_txtbox)
                                curr_part_matname_txtboxes.append(matpart_txtbox)
                            curr_obj_part_matname_txtboxes[object] = part_txtboxes
            with gr.Column() as display_rendering_column:
                current_rendering = gr.Image(value=init_rendering, interactive=False, label="Current rendering")
                save_rendering_button = gr.Button("Save to gallery")
                saved_scenes = gr.Gallery(value=saved_renderings_list,label="Saved renderings").style(grid=5,height="auto")
        
        ##########################################################################################
        # Right section. Section for requesting suggestions and critiques, and receiving critiques
        ##########################################################################################
        with gr.Tab(label="Request suggestion") as ai_suggest_tab:
            with gr.Column():
                suggest_material_type = ["All types","wood","metal","fabric","ceramic"]
                suggest_material_dropdown = gr.Dropdown(label="Material Type",choices=suggest_material_type,value=suggest_material_type[1],interactive=True)
                suggest_interior_design_style_dropdown = gr.Dropdown(value=styles[0],choices = styles,label="Interior Design Style", interactive=True)
                with gr.Row():
                    suggest_products = list(object_inputs.keys()); 
                    suggest_product_dropdown = gr.Dropdown(label="Product",value="Select a product", choices=suggest_products,interactive=True)
                    suggest_select_product = gr.Button(value="Select product")
                    suggest_part_dropdown = gr.Dropdown(label="Parts",value="Please select an object first",choices=["Please select a product first"],interactive=True,visible=False)
                with gr.Row():
                    suggest_descriptor_dropdown = gr.Dropdown(label="Descriptor (optional)", value="No descriptor", choices=["No descriptor"], interactive=True)
                    suggest_target_dropdown = gr.Dropdown(label="Targets (optional)",value="No targets set",choices=["No targets set"], interactive=True)
                preview_prompt_button = gr.Button("Preview prompt")
                with gr.Row():
                    preview_prompt = gr.Textbox(label="Prompt preview",value="",interactive=True,visible=False)
                    suggest_button = gr.Button("Suggest materials",visible=False)
            with gr.Column():
                with gr.Row():
                    ai_suggestion = gr.Textbox("(Currently no response)", label="ChatGPT says...")
                    extracted_words = gr.Textbox("(Currently no suggested materials)", label="Suggested materials")
        
        with gr.Tab(label="View feedback", id="ai_critiques_tab") as ai_critiques_tab:  
            materials = []
            for object in list(current_texture_parts.keys()):
                object_dict = current_texture_parts[object]
                for part in list(object_dict.keys()):
                    part_dict = object_dict[part]
                    materials.append(part_dict['mat_name'])
            unique_materials = [*set(materials)]

            with gr.Tab(label="Assembly") as assembly_critiques_tab:
                # For each object, make a tab. Each tab contains a list of its parts.
                for object in list(current_texture_parts.keys()):
                    gr.Tab(label=f"{object}")
                    object_dict = current_texture_parts[object]
                    for part in list(object_dict.keys()):
                        part_dict = object_dict[part]
                        part_mat = part_dict['mat_name']
                        parents = part_dict['parents']
                        for parent in parents:
                            parent_mat = object_dict[parent]['mat_name']
                            # recommendation = parts_assembling_critique(object, part_mat, part, parent_mat,parent,n=3)
                            # with gr.Row():
                            #     gr.Markdown(value=f"{part_mat} {str(part)} ==> {parent_mat} {str(parent)}")
                            #     gr.Textbox(value=f"Recommendation: {recommendation}", interactive=False)

            targetenv_sentanalyses = []
            with gr.Tab(label="Target Environment"):
                with gr.Row():
                    for mat in unique_materials:
                        with gr.Row():
                            gr.Markdown(f"{mat}")
                            gr.Markdown(f"No eval")
                            gr.Button(f"View feedback")
            matspec_sentanalyses = []
            with gr.Tab(label="Material Specs") as matspec_critiques_tab:
                # empty_specs = gr.Markdown("No material specifications set. Please set them first.")
                pass
            
            

    generate_button.click(fn=generate_material_textures, inputs=[input_material],outputs=[gen_material_options,*gen_material_images], scroll_to_output=True)
    transfer_button.click(fn=transfer_material_texture, inputs=[gen_material_options, material_finish_options, *part_inputs], outputs=[current_rendering, *curr_part_matname_txtboxes],scroll_to_output=True)
    save_rendering_button.click(fn=save_rendering, inputs=[current_rendering], outputs=[saved_scenes])
    suggest_select_product.click(fn=get_parts_from_object,inputs=[suggest_product_dropdown],outputs=[suggest_part_dropdown])
    set_targets_button.click(fn=set_targets, inputs=[target_place, target_market], outputs=[suggest_target_dropdown])
    set_descriptors_button.click(fn=set_material_specs, inputs=[descriptors], outputs=[suggest_descriptor_dropdown])
    preview_prompt_button.click(fn=make_suggest_prompt, inputs = [suggest_material_dropdown,suggest_interior_design_style_dropdown,suggest_descriptor_dropdown,suggest_product_dropdown,suggest_part_dropdown,suggest_target_dropdown],outputs=[preview_prompt,suggest_button])
    suggest_button.click(fn=get_suggestion, inputs=[preview_prompt, suggest_material_dropdown],outputs=[ai_suggestion, extracted_words])

interface.launch(debug=True)


