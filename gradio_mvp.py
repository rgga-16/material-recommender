import gradio as gr
from texture_transfer_3d import TextureDiffusion
import os, time, json
import pathlib as p
from PIL import Image


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


def select_gen_material_texture():

    return 



def generate_material_textures(material_str, n=5):
    material_textures = texture_generator.text2texture(material_str,n=n, gen_imsize=512)
    material_names = [f'{material_str}_{i}' for i in range(len(material_textures))]


    return material_textures

def transfer_material_texture():

    return 


def create_interface():

    with gr.Blocks() as interface:
        with gr.Row() as design_specs_row:
            with gr.Row() as design_specs:
                design_specs_str = """ Location: Indoors\nTarget market: Class A"""
                design_specs = gr.Textbox(label="Design Specifications", value = design_specs_str,lines=5,)
        
        with gr.Row() as main_row:
            with gr.Column() as materials_generator_column:
                with gr.Row() as object_part_inputs:

                    with gr.Column():
                        input_material = gr.Textbox(label="Input material texture")
                        generate_button = gr.Button("Generate")
                    
                    with gr.Row() as material_outputs:
                        generated_materials = gr.Gallery(label="Generated material texture images").style(grid=4,height="auto")
                        generated_material_labels =gr.Radio(label="Generated material texture names", interactive=True,choices=None,type="value")
                    
                    # For each object, create a checkbox group of its parts.
                    with gr.Row():
                        texture_transfer_inputlist = []
                        for i in range(4):
                            with gr.Tab(f"Nighstand parts {i}"):
                                nightstand_parts = [f"base_{i}", f"top_drawer_{i}", f"bottom_drawer_{i}", f"top_handle_{i}", f"bottom_handle_{i}", f"legs_{i}"]
                                checkboxes = gr.CheckboxGroup(choices=nightstand_parts,label="Nightstand")
                            texture_transfer_inputlist.append(checkboxes)
                        transfer_button = gr.Button("Transfer textures")

                # https://gradio.app/docs/#button
                generate_button.click(fn=generate_material_textures, inputs=input_material,outputs=generated_materials)
                # transfer_button.click(fn=, inputs=, outputs=)

            with gr.Column() as display_column:
                image = gr.Image(interactive=False, label="Current renderings")
                save_button = gr.Button("Save to gallery")
                saved_scenes = gr.Gallery(label="Saved renderings").style(grid=5,height="auto")

            with gr.Column() as ai_suggest_column:
                text1 = gr.Textbox(label="Nighstand base")

    return interface

def main2():
    interface = create_interface()
    interface.launch(debug=True)


def main():
    ######################### Script to render the initial 3D shape in. #########################

    #########################
    interface = gr.Interface(fn=transfer_texture, inputs = ['text','text','text','text','text','text'], outputs = ['image'])
    interface.launch(share=True)
    return 

if __name__=='__main__':
    selected_gen_texture = None 
    texture_part_dict = {}
    texture_generator = TextureDiffusion()
    # main()
    main2()