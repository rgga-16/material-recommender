import torch
from torch import autocast
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from diffusers.schedulers import DDIMScheduler, LMSDiscreteScheduler, PNDMScheduler
import time, os
import pathlib as p
from PIL import Image

if __name__=="__main__":
    SEED=45632

    model_id = "CompVis/stable-diffusion-v1-4"
    device = "cuda"
    

    lms = PNDMScheduler(
        beta_start=0.005, 
        beta_end=0.12, 
        beta_schedule="scaled_linear"
    )

    im2im_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        model_id,scheduler=lms, 
        use_auth_token=True, 
        torch_dtype=torch.float16,
        revision="fp16",
    ).to(device)

    texture_name = "hardwood"
    prompt = f"{texture_name} texture map, 4k"
    init_impath = './hardwood-texture.png'
    init_im = Image.open(init_impath)
    init_im = init_im.resize((256, 256))

    n_images = 5
    with autocast("cuda"):
        '''
        output_dict
        ['sample'] - [PIL Image]
        ['nsfw_content_detected'] - [bool]
        '''
        output_dict = im2im_pipe([prompt]*n_images, init_image=init_im, strength=0.8,guidance_scale=7.5,num_inference_steps=50)

        out_images = output_dict["images"]

        for i in range(len(out_images)):
            out_im = out_images[i]
            text_impath = f"similar_{i}.png"
            text_path = str(p.Path.cwd() / text_impath)
            out_im.save(text_path)