import gradio as gr
from texture_transfer_3d import TextureDiffusion
import os, time
import pathlib as p


def transfer_texture(body, top_drawer, top_handle, bottom_drawer, bottom_handle, legs):
    str = f'{body} {top_drawer} {top_handle} {bottom_drawer} {bottom_handle} {legs}'

    texture_part_prompts = [body, top_drawer, top_handle, bottom_drawer, bottom_handle, legs]

    for tp in texture_part_prompts:
        images = texture_generator.text2texture(tp,n=1)

        for i in range(len(images)):
            text_impath = f"./out/texture_{i}.png"
            text_path = str(p.Path.cwd() / text_impath)
            images[i].save(text_path)

            start_transfer = time.time()
            mesh_folder = "./data/3d_models/nightstand"
            mesh_path = os.path.join(mesh_folder,'base.obj')
            rendering_folder = str(p.Path.cwd() / "out")
            command_str = f'blender --background --python rendering/blender.py -- --mesh_folder {mesh_folder} --texture {text_path} --renderfolder {rendering_folder}'
    
    print(command_str)
    os.system(command_str)
    end_transfer = time.time()
    print(f'Time elapsed for texture transfer: {abs(end_transfer-start_transfer)}s')
    return str


def main():
    interface = gr.Interface(fn=transfer_texture, inputs = ['text','text','text','text','text','text'], outputs = ['text'])
    interface.launch(share=True)
    return 




if __name__=='__main__':
    texture_generator = TextureDiffusion()
    main()