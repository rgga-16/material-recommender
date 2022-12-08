import torch
from torch import autocast
from diffusers import StableDiffusionPipeline, LMSDiscreteScheduler
# StableDiffusionImg2ImgPipeline
import time, os
import pathlib as p


class TextureDiffusion():
    def __init__(self, model_id="CompVis/stable-diffusion-v1-4"):

        print("Initializing diffusion model")
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        
        self.lms = LMSDiscreteScheduler(
            beta_start=0.00085, 
            beta_end=0.012, 
            beta_schedule="scaled_linear"
        )

        self.diffusion_model = StableDiffusionPipeline.from_pretrained(model_id,scheduler=self.lms, use_auth_token=True, torch_dtype=torch.float16).to(self.device)
    
    def text2texture(self, texture_str,n=4, gen_imsize=512):
        prompt = f'{texture_str} texture map, 4k'
        images = []
        for _ in range(n):
            with autocast("cuda"):
                output_dict = self.diffusion_model(prompt, width=gen_imsize,height=gen_imsize,guidance_scale=7.5,prompt_strength=1.0,num_inference_steps=50)
                image = output_dict["sample"][0]
                images.append(image)
        return images



if __name__=="__main__":

    model = TextureDiffusion()

    prompt = "blue resin"
    images = []
    sample_num = 10

    start_synth = time.time() 
    images = model.text2texture(prompt,imsize=512, n=sample_num)
    end_synth = time.time()
    print(f'Time elapsed for text-to-texture synthesis: {abs(end_synth-start_synth)}s')

    for i in range(len(images)):
        text_impath = f"./out/texture_{i}.png"
        text_path = str(p.Path.cwd() / text_impath)
        images[i].save(text_path)

    # start_transfer = time.time()
    # mesh_folder = "./data/3d_models/nightstand"
    # mesh_path = os.path.join(mesh_folder,'base.obj')
    # rendering_folder = str(p.Path.cwd() / "out")
    # command_str = f'blender --background --python rendering/blender.py -- --mesh_folder {mesh_folder} --texture {text_path} --renderfolder {rendering_folder}'
    
    # print(command_str)
    # os.system(command_str)
    # end_transfer = time.time()
    # print(f'Time elapsed for texture transfer: {abs(end_transfer-start_transfer)}s')

    