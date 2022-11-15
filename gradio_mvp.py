import gradio as gr
from texture_transfer_3d import TextureDiffusion
import os, time, json
import pathlib as p
from PIL import Image

#############################
# Put variables here
#############################
n_gen_materials = 5
gen_material = ""

gen_texture_choices_dict = {}
#############################
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


def transfer_material_texture(mat_option, *object_part_inputs):

    for checkboxgroup in object_part_inputs:
        print()

    selected_image = gen_texture_choices_dict[mat_option]

    print()

    return 


def generate_material_textures(material_str, n=n_gen_materials):
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

    # gen_mats = [gr.Image.update(value=mt,visible=True,label="") for mt in material_textures]

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
            with gr.Row() as object_part_inputs:
                with gr.Column():
                    input_material = gr.Textbox(label="Input material texture")
                    generate_button = gr.Button("Generate")
                    with gr.Row() as material_outputs:
                        with gr.Column():
                            for i in range(n_gen_materials):
                                gen_img = gr.Image(interactive=False,visible=False,shape=(128,128))
                                gen_material_images.append(gen_img)
                        gen_material_options = gr.Radio(label="Generated material texture names", interactive=True,choices=None,type="value")
                    # For each object, create a checkbox group of its parts.
                    # with gr.Row():
                        object_part_inputs = []
                        with gr.Column():
                            for i in range(4):
                                with gr.Tab(f"Nighstand parts {i}"):
                                    nightstand_parts = [f"base_{i}", f"top_drawer_{i}", f"bottom_drawer_{i}", f"top_handle_{i}", f"bottom_handle_{i}", f"legs_{i}"]
                                    checkboxes = gr.CheckboxGroup(choices=nightstand_parts,label="Nightstand")
                                object_part_inputs.append(checkboxes)
                            transfer_button = gr.Button("Transfer textures")
            ####################################################################################
        
        
        with gr.Column() as display_column:
            current_rendering = gr.Image(interactive=False, label="Current renderings")
            save_button = gr.Button("Save to gallery")
            saved_scenes = gr.Gallery(label="Saved renderings").style(grid=5,height="auto")

        # with gr.Column() as ai_suggest_column:
        #     text1 = gr.Textbox(label="Nighstand base")


    generate_button.click(fn=generate_material_textures, inputs=[input_material],outputs=[gen_material_options,*gen_material_images])
    transfer_button.click(fn=transfer_material_texture, inputs=[gen_material_options, *object_part_inputs], outputs=[current_rendering])


################# Load obj files here ################



######################################################

interface.launch(debug=True)



def main():
    ######################### Script to render the initial 3D shape in. #########################

    #########################
    interface = gr.Interface(fn=transfer_texture, inputs = ['text','text','text','text','text','text'], outputs = ['image'])
    interface.launch(share=True)
    return 

