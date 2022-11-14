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

def main():
    ######################### Script to render the initial 3D shape in. #########################

    #########################
    interface = gr.Interface(fn=transfer_texture, inputs = ['text','text','text','text','text','text'], outputs = ['image'])
    interface.launch(share=True)
    return 

if __name__=='__main__':
    texture_part_dict = {}
    texture_generator = TextureDiffusion()
    main()