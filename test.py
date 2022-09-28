# make sure you're logged in with `huggingface-cli login`

import torch
from torch import autocast
from diffusers import StableDiffusionPipeline, LMSDiscreteScheduler
import time 

start = time.time() 

model_id = "CompVis/stable-diffusion-v1-4"
device = "cuda"

lms = LMSDiscreteScheduler(
    beta_start=0.00085, 
    beta_end=0.012, 
    beta_schedule="scaled_linear"
)

pipe = StableDiffusionPipeline.from_pretrained(model_id,scheduler=lms, use_auth_token=True, torch_dtype=torch.float16)
pipe = pipe.to(device)

# prompt = "African teak wood texture, PBR, base color, albedo, 4k"
prompt = "hardwood texture map for flooring, 4k"
images = []
sample_num = 10
for i in range(sample_num):
    with autocast("cuda"):
        '''
        output_dict
        ['sample'] - [PIL Image]
        ['nsfw_content_detected'] - [bool]
        '''
        output_dict = pipe(prompt, width=256,height=256,guidance_scale=7.5,prompt_strength=0.8,num_inference_steps=50)
        if not output_dict['nsfw_content_detected'][0]:
            images.append(output_dict["sample"][0])  

for i in range(len(images)):
    image = images[i]
    image.save(f"{prompt}_{i}.png")

end = time.time()
print(f'Time elapsed: {abs(end-start)}s')