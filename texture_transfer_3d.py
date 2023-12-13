import torch
from torch import autocast
torch.cuda.empty_cache()
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import time, os
import openai
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
 #If first time using this repo, set the environment variable "OPENAI_API_KEY", to your API key from OPENAI
from utils import image
from PIL import Image 

import pathlib as p

def patch_conv(cls):
    init = cls.__init__
    def __init__(self, *args, **kwargs):
        return init(self, *args, **kwargs, padding_mode='circular')
    cls.__init__ = __init__
patch_conv(torch.nn.Conv2d)

# class StableDiffusionAPI():
#     def __init__(self) -> None:
#         pass

def text2texture_similar(texture_str, img_path,n=4, gen_imsize=256):
    images_b64 = []
    images = []
    for _ in range(n):
        try: 
            response = client.images.generate(image=open(img_path, 'rb'), #BUG: TypeError: Object of type BufferedReader is not JSON serializable
            n=1,
            # size=f"{gen_imsize}x{gen_imsize}",
            size=f"{256}x{256}",
            response_format="b64_json")
            image_b64 = response['data'][0]['b64_json']
        except openai.OpenAIError as e:
            print(e.http_status)
            print(e.error)
            blank_img = Image.new('RGB',(256,256),color='black')
            image_b64 = image.im_2_b64(blank_img)  
        im = image.b64_2_img(image_b64).convert('RGB')
        images.append(im)
        images_b64.append(image_b64)
    return images

    return 


class DALLE2():
    def __init__(self) -> None:
        pass

    def text2texture(self,texture_str,n=4, gen_imsize=512):
        images_b64 = []
        images = []

        for _ in range(n):
            # try: 
            response = client.images.generate(prompt=texture_str,
            n=1,
            size=f"{256}x{256}",
            response_format="b64_json")
            image_b64 = response['data'][0]['b64_json']
            # except openai.error.OpenAIError as e:
            #     print(e.http_status)
            #     print(e.error)
            #     blank_img = Image.new('RGB',(256,256),color='black')
            #     image_b64 = image.im_2_b64(blank_img)  
            im = image.b64_2_img(image_b64).convert('RGB')
            images.append(im)
            images_b64.append(image_b64)
        return images



class TextureDiffusion():
    def __init__(self, model_id="CompVis/stable-diffusion-v1-4"):

        print("Initializing diffusion model")
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

        self.pipe = StableDiffusionPipeline.from_pretrained(model_id,use_auth_token=True, torch_dtype=torch.float16).to(self.device)
        
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
        # self.pipe.enable_sequential_cpu_offload()
        self.pipe.enable_attention_slicing(1)

    def to_cpu(self):
        self.pipe.to('cpu')
    
    def to_gpu(self):
        self.pipe.to(self.device)
    
    def text2texture(self, texture_str,n=4, gen_imsize=256):
        prompt = f'{texture_str}'
        # print(f"PROMPT: {prompt}")
        images = []
        for _ in range(n):
            with autocast("cuda"):
                output_dict = self.pipe(prompt, width=gen_imsize,height=gen_imsize,guidance_scale=7.5,num_inference_steps=20)
                image = output_dict["images"][0]
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

    