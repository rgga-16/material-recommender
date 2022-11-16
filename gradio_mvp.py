import gradio as gr
from texture_transfer_3d import TextureDiffusion
import os, time, json, copy
import pathlib as p
from PIL import Image

#############################
# Set variables here
#############################
n_gen_materials = 5
gen_material = ""

gen_texture_choices_dict = {}
saved_renderings_list = []
saved_texture_parts = []
current_texture_parts = None 
curr_render_id = 1
#############################

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


init_rendering_outdir = os.path.join(renderings_dir,str(curr_render_id))

command_str = f'blender --background --python render_obj_and_textures.py -- --out_dir {init_rendering_outdir} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {init_texture_parts_path}'
os.system(command_str)

init_rendering = Image.open(os.path.join(init_rendering_outdir,"rendering.png"))
saved_renderings_list.append(init_rendering)
######################################################

def transfer_texture(base, top_drawer, top_handle, bottom_drawer, bottom_handle, legs):
    output_str = f'{base} {top_drawer} {top_handle} {bottom_drawer} {bottom_handle} {legs}'
    texture_part_prompts = [base, top_drawer, top_handle, bottom_drawer, bottom_handle, legs]
    
    texture_paths=[]

    start_synth = time.time() 
    if base != "":
        texture_paths = []
        base_textures = texture_generator.text2texture(base,n=1)
        for i in range(len(base_textures)):
            text_impath = f"./tmp/texture_base_{i}.png"
            text_path = str(p.Path.cwd() / text_impath)
            base_textures[i].save(text_path)
            texture_paths.append(text_path)
        texture_part_dict['base'] = texture_paths[0] #Temporarily, get the 1st element. add selection functionality later.

    if top_drawer != "":
        texture_paths = []
        top_drawer_textures = texture_generator.text2texture(top_drawer,n=1)
        for i in range(len(top_drawer_textures)):
            text_impath = f"./tmp/texture_top_drawer_{i}.png"
            text_path = str(p.Path.cwd() / text_impath)
            top_drawer_textures[i].save(text_path)
            texture_paths.append(text_path)
        texture_part_dict['top_drawer'] = texture_paths[0] #Temporarily, get the 1st element. add selection functionality later.

    if top_handle != "":
        texture_paths = []
        top_handle_textures = texture_generator.text2texture(top_handle,n=1)
        for i in range(len(top_handle_textures)):
            text_impath = f"./tmp/texture_top_handle_{i}.png"
            text_path = str(p.Path.cwd() / text_impath)
            top_handle_textures[i].save(text_path)
            texture_paths.append(text_path)
        texture_part_dict['top_handle'] = texture_paths[0] #Temporarily, get the 1st element. add selection functionality later.

    if bottom_drawer != "":
        texture_paths = []
        bottom_drawer_textures = texture_generator.text2texture(bottom_drawer,n=1)
        for i in range(len(bottom_drawer_textures)):
            text_impath = f"./tmp/texture_bottom_drawer_{i}.png"
            text_path = str(p.Path.cwd() / text_impath)
            bottom_drawer_textures[i].save(text_path)
            texture_paths.append(text_path)
        texture_part_dict['bottom_drawer'] = texture_paths[0] #Temporarily, get the 1st element. add selection functionality later.

    if bottom_handle != "":
        texture_paths = []
        bottom_handle_textures = texture_generator.text2texture(bottom_handle,n=1)
        for i in range(len(bottom_handle_textures)):
            text_impath = f"./tmp/texture_bottom_handle_{i}.png"
            text_path = str(p.Path.cwd() / text_impath)
            bottom_handle_textures[i].save(text_path)
            texture_paths.append(text_path)
        texture_part_dict['bottom_handle'] = texture_paths[0] #Temporarily, get the 1st element. add selection functionality later.

    if legs != "":
        texture_paths = []
        legs_textures = texture_generator.text2texture(legs,n=1)
        for i in range(len(legs_textures)):
            text_impath = f"./tmp/texture_legs_{i}.png"
            text_path = str(p.Path.cwd() / text_impath)
            legs_textures[i].save(text_path)
            texture_paths.append(text_path)
        texture_part_dict['legs'] = texture_paths[0] #Temporarily, get the 1st element. add selection functionality later.

    with open("./tmp/texture_parts.json","w") as tmpfile:
        json.dump(texture_part_dict,tmpfile)

    end_synth = time.time()
    print(f'Time elapsed for text-to-texture synthesis: {abs(end_synth-start_synth)}s')

    # Call script to render each part
    command_str = f'blender --background --python render_obj_and_textures.py -- --obj_json ./nightstand.json --texture_parts_json ./tmp/texture_parts.json'
    os.system(command_str)
    
    # Load rendered image
    rendering = Image.open('./tmp/rendering.png')

    return rendering

def transfer_material_texture(mat_option, *part_inputs):

    global current_texture_parts

    selected_material_image = gen_texture_choices_dict[mat_option]
    selected_material_name = gen_material

    selected_material_impath = os.path.join(os.getcwd(),f'tmp/{selected_material_name}.png')
    selected_material_image.save(selected_material_impath)

    new_texture_parts = copy.deepcopy(current_texture_parts)

    for object,parts in zip(object_inputs,part_inputs):
        for part in parts:
            new_texture_parts[object][part]["mat_name"]=selected_material_name
            new_texture_parts[object][part]["mat_image_texture"]=selected_material_impath

    current_texture_parts = new_texture_parts
    
    tmp_texture_parts_path = "./tmp/texture_parts.json"
    with open(tmp_texture_parts_path,"w") as tmpfile:
        json.dump(current_texture_parts,tmpfile)
    
    tmp_rendering_outdir = "./tmp"
    command_str = f'blender --background --python render_obj_and_textures.py -- --out_dir {tmp_rendering_outdir} --rendering_setup_json {rendering_setup_path} --texture_object_parts_json {tmp_texture_parts_path}'
    os.system(command_str)
    
    # Load rendered image
    rendering = Image.open(os.path.join(tmp_rendering_outdir,"rendering.png"))

    return rendering

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
        gen_mats.append(gr.Image.update(value=mat_texture,visible=True,label=mat_option))
        material_options.append(mat_option)

    return (gr.Radio.update(choices=material_options),*gen_mats)


selected_gen_texture = None 
texture_part_dict = {}
texture_generator = TextureDiffusion()
gen_material_images = []

interface = gr.Blocks()

with interface:
    with gr.Row() as design_specs_row:
        with gr.Row() as design_specs:
            design_specs_str = """ Location: Indoors\nTarget market: Class A"""
            design_specs = gr.Textbox(label="Design Specifications", value = design_specs_str,lines=5,)
    
    with gr.Row() as main_row:
        with gr.Column() as materials_generator_column:
            ####################################################################################
            # Left section. Section for generating material texture and transferring onto parts.
            ####################################################################################
            with gr.Row() as material_inputs:
                with gr.Column():
                    input_material = gr.Textbox(label="Input material texture")
                    generate_button = gr.Button("Generate")
                    with gr.Row() as material_outputs:
                        with gr.Column():
                            for i in range(n_gen_materials):
                                gen_img = gr.Image(interactive=False,visible=False,shape=(128,128))
                                gen_material_images.append(gen_img)
                        gen_material_options = gr.Radio(label="Generated material texture names", interactive=True,choices=None,type="value")

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

        with gr.Column() as display_column:
            current_rendering = gr.Image(value=init_rendering, interactive=False, label="Current rendering")
            save_rendering_button = gr.Button("Save to gallery")
            saved_scenes = gr.Gallery(value=saved_renderings_list,label="Saved renderings").style(grid=5,height="auto")

        # with gr.Column() as ai_suggest_column:
        #     text1 = gr.Textbox(label="Nightstand base")

    generate_button.click(fn=generate_material_textures, inputs=[input_material],outputs=[gen_material_options,*gen_material_images])
    transfer_button.click(fn=transfer_material_texture, inputs=[gen_material_options, *part_inputs], outputs=[current_rendering])
    save_rendering_button.click(fn=save_rendering, inputs=[current_rendering], outputs=[saved_scenes])
interface.launch(debug=True)

def main():
    ######################### Script to render the initial 3D shape in. #########################

    #########################
    interface = gr.Interface(fn=transfer_texture, inputs = ['text','text','text','text','text','text'], outputs = ['image'])
    interface.launch(share=True)
    return 

