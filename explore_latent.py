"""
stable diffusion dreaming
creates hypnotic moving videos by smoothly walking randomly through the sample space

example way to run this script:

$ python stablediffusionwalk.py --prompt "blueberry spaghetti" --name blueberry

to stitch together the images, e.g.:
$ ffmpeg -r 10 -f image2 -s 512x512 -i blueberry/frame%06d.jpg -vcodec libx264 -crf 10 -pix_fmt yuv420p blueberry.mp4

nice slerp def from @xsteenbrugge ty
you have to have access to stablediffusion checkpoints from https://huggingface.co/CompVis
and install all the other dependencies (e.g. diffusers library)

uses diffusers==0.3.0
"""

import os
import inspect
import fire
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from diffusers.schedulers import DDIMScheduler, LMSDiscreteScheduler, PNDMScheduler
from time import time
from PIL import Image
from einops import rearrange
import numpy as np
import torch
from torch import autocast
from torchvision.utils import make_grid
from utils import slerp
from torchvision import transforms as tfms

# Using torchvision.transforms.ToTensor
to_tensor_tfm = tfms.ToTensor()

def pil_to_latent(vae,input_im):
  # Single image -> single latent in a batch (so size 1, 4, 64, 64)
  with torch.no_grad():
    tensor = to_tensor_tfm(input_im).unsqueeze(0).to(torch_device)*2-1
    # tensor = tensor.type(torch.float16).to(torch_device)
    latent = vae.encode(tensor) # Note scaling
  return 0.18215 * latent['latent_dist'].mean # or .mean or .sample

def latents_to_pil(vae,latents):
  # bath of latents -> list of images
  latents = (1 / 0.18215) * latents
  with torch.no_grad():
    image = vae.decode(latents)
  image = (image / 2 + 0.5).clamp(0, 1)
  image = image.detach().cpu().permute(0, 2, 3, 1).numpy()
  images = (image * 255).round().astype("uint8")
  pil_images = [Image.fromarray(image) for image in images]
  return pil_images



def run(
        # --------------------------------------
        # args you probably want to change
        prompt = "cube patterns, texture map, 4k", # prompt to dream about
        gpu = 0, # id of the gpu to run on
        name = 'red leather_walk', # name of this project, for the output directory
        rootdir = './out',
        num_steps = 10, # number of steps between each pair of sampled points
        max_frames = 50, # number of frames to write and then exit the script
        num_inference_steps = 50, # more (e.g. 100, 200 etc) can create slightly better images
        guidance_scale = 7.5, # can depend on the prompt. usually somewhere between 3-10 is good
        seed = 1337,
        # --------------------------------------
        # args you probably don't want to change
        quality = 90, # for jpeg compression of the output images
        eta = 0.0,
        width = 512,
        height = 512,
        weights_path = "CompVis/stable-diffusion-v1-4",
        # --------------------------------------
    ):
    assert torch.cuda.is_available()
    assert height % 8 == 0 and width % 8 == 0
    torch.manual_seed(seed)
    torch_device = f"cuda:{gpu}"

    # init the output dir
    outdir = os.path.join(rootdir, name)
    os.makedirs(outdir, exist_ok=True)

    # init all of the models and move them to a given GPU
    # lms = LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear")
    # text2im_pipe = StableDiffusionPipeline.from_pretrained(weights_path, revision="fp16", scheduler=lms, use_auth_token=True, torch_dtype=torch.float16).to(torch_device)
    im2im_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(weights_path, revision="fp16", torch_dtype=torch.float16,use_auth_token=True).to(torch_device)
    # im2im_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(weights_path, use_auth_token=True).to(torch_device)
    n_images=10
    
    # t2i_vae = t2i_pipe.vae
    # i2i_vae = im2im_pipe.vae

    input_image = Image.open('./moodboard/cube_pattern3.png').resize((width,height))
    input_image = input_image.convert('RGB')
    
    for i in range(n_images):
      with autocast("cuda"):
        '''
        strength - [0,1] How familiar or various u want the images to be from the init_image. higher means more variation.
        guidance_scale - [0,15] How much the prompt should guide the generation. People say 6-12
        '''
        out_image = im2im_pipe(prompt=prompt, init_image=input_image, strength=0.8, guidance_scale=8.0, generator=generator).images[0]
        out_image.save(f'out_{i}.jpg')
    # outpath = os.path.join(outdir, f'init.jpg')
    # input_image.save(outpath)
    
    # Encode to the latent space
    # init_im_encoding = pil_to_latent(t2i_vae,input_image)
    # source_latent = torch.randn((1, text2im_pipe.unet.in_channels, height // 8, width // 8), device=torch_device)
    # target_latent = torch.randn((1, text2im_pipe.unet.in_channels, height // 8, width // 8), device=torch_device)

    # frame_index = 0
    
    # for _, t in enumerate(np.linspace(0, 1, num_steps)):
    #     init_latent = slerp(float(t), init_im_encoding , target_latent )

    #     with autocast("cuda"):
    #         image = text2im_pipe(prompt, num_inference_steps=num_inference_steps, latents=init_latent , guidance_scale=guidance_scale)["sample"][0]  
    #     outpath = os.path.join(outdir, f'frame{frame_index}.jpg')
    #     image.save(outpath)

    #     frame_index += 1
    
if __name__ == '__main__':
    torch_device = "cuda" if torch.cuda.is_available() else "cpu"
    generator = torch.Generator(device=torch_device).manual_seed(1024)
    fire.Fire(run)
