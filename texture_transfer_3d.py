import torch
from torch import autocast
from diffusers import StableDiffusionPipeline, LMSDiscreteScheduler
# from rendering import renderer as r
# from rendering.blender import BlenderRenderer
import time, os
import pathlib as p

if __name__=="__main__":

    start_synth = time.time() 
    
    # Create texture
    model_id = "CompVis/stable-diffusion-v1-4"
    device = "cuda"

    lms = LMSDiscreteScheduler(
        beta_start=0.00085, 
        beta_end=0.012, 
        beta_schedule="scaled_linear"
    )

    pipe = StableDiffusionPipeline.from_pretrained(model_id,scheduler=lms, use_auth_token=True, torch_dtype=torch.float16)
    pipe = pipe.to(device)

    prompt = "blue nylon texture map, 4k"
    images = []
    sample_num = 1
    with autocast("cuda"):
        '''
        output_dict
        ['sample'] - [PIL Image]
        ['nsfw_content_detected'] - [bool]
        '''
        output_dict = pipe(prompt, width=512,height=512,guidance_scale=7.5,prompt_strength=0.8,num_inference_steps=50)
        image = output_dict["sample"][0]
        text_impath = "texture.png"
        text_path = str(p.Path.cwd() / text_impath)
        image.save(text_path)
    end_synth = time.time()
    print(f'Time elapsed for text-to-texture synthesis: {abs(end_synth-start_synth)}s')

    start_transfer = time.time()
    # mesh_path = "./data/3d_models/chair/backseat.obj"
    mesh_folder = "./data/3d_models/chair"
    rendering_folder = str(p.Path.cwd() / "out")
    command_str = f'blender --background --python rendering/blender_pix2surf.py -- --mesh_folder {mesh_folder} --texture {text_path} --renderfolder {rendering_folder}'
    print(command_str)
    os.system(command_str)
    end_transfer = time.time()
    print(f'Time elapsed for texture transfer: {abs(end_transfer-start_transfer)}s')

    # unwrap_method='cube_project'
    # obj = renderer.load_object(mesh_path)
    # renderer.recalculate_normals(obj)
    # renderer.bake_texture(obj,unwrap_method,text_path)
    