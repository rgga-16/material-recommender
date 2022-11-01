
'''
Code heavily adapted from:
1) https://colab.research.google.com/drive/1dlgggNa5Mz8sEAGU0wFCHhGLFooW_pf1#scrollTo=cbmk3JqVs5yQ 
2) https://keras.io/examples/generative/random_walks_with_stable_diffusion/#a-walk-around-a-text-prompt
requires diffusers==0.2.4
'''
import torch
import inspect
from transformers import CLIPTextModel, CLIPTokenizer
from diffusers import AutoencoderKL, UNet2DConditionModel, LMSDiscreteScheduler
from tqdm.auto import tqdm
from torch import autocast
from PIL import Image
from matplotlib import pyplot as plt
import numpy
from torchvision import transforms as tfms
import utils 

# Set device
torch_device = "cuda" if torch.cuda.is_available() else "cpu"
height = 256                      # default height of Stable Diffusion
width = 256                     # default width of Stable Diffusion
num_inference_steps = 50  #@param           # Number of denoising steps
guidance_scale = 8                # Scale for classifier-free guidance
generator = torch.manual_seed(32)   # Seed generator to create the inital latent noise
batch_size = 1

# Using torchvision.transforms.ToTensor
to_tensor_tfm = tfms.ToTensor()

def pil_to_latent(input_im):
  # Single image -> single latent in a batch (so size 1, 4, 64, 64)
  with torch.no_grad():
    latent = vae.encode(to_tensor_tfm(input_im).unsqueeze(0).to(torch_device)*2-1) # Note scaling
  return 0.18215 * latent.mean # or .mean or .sample

def latents_to_pil(latents):
  # bath of latents -> list of images
  latents = (1 / 0.18215) * latents
  with torch.no_grad():
    image = vae.decode(latents)
  image = (image / 2 + 0.5).clamp(0, 1)
  image = image.detach().cpu().permute(0, 2, 3, 1).numpy()
  images = (image * 255).round().astype("uint8")
  pil_images = [Image.fromarray(image) for image in images]
  return pil_images

# MODEL LOADING
#####################################################################################################################
# Load the autoencoder model which will be used to decode the latents into image space. 
vae = AutoencoderKL.from_pretrained("CompVis/stable-diffusion-v1-4", subfolder="vae",use_auth_token=True)
# Load the tokenizer and text encoder to tokenize and encode the text. 
tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
text_encoder = CLIPTextModel.from_pretrained("openai/clip-vit-large-patch14")
# The UNet model for generating the latents.
unet = UNet2DConditionModel.from_pretrained("CompVis/stable-diffusion-v1-4", subfolder="unet", use_auth_token=True)
# The noise scheduler
scheduler = LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear", num_train_timesteps=1000)
# To the GPU we go!
vae = vae.to(torch_device)
text_encoder = text_encoder.to(torch_device)
unet = unet.to(torch_device)
#####################################################################################################################

input_image = Image.open('./init_redleather.png').resize((64,64))

# Encode to the latent space
encoded = pil_to_latent(input_image)
image_encoding = torch.clone(encoded)

prompt = ["red leather texture map, 4k"]
# Prep text 
text_input = tokenizer(prompt, padding="max_length", max_length=tokenizer.model_max_length, truncation=True, return_tensors="pt")
with torch.no_grad():
  text_embeddings = text_encoder(text_input.input_ids.to(torch_device))[0]

# Walk around an image encoding
###########################################################
walk_steps = 3
batch_size = 1
batches = walk_steps // batch_size
step_size = 0.005

# classifier guidance: add the unconditional embedding
max_length = text_input.input_ids.shape[-1]
uncond_input = tokenizer([""] * batch_size, padding="max_length", max_length=max_length, return_tensors="pt")
with torch.no_grad():
  uncond_embeddings = text_encoder(uncond_input.input_ids.to(torch_device))[0] 
text_embeddings = torch.cat([uncond_embeddings, text_embeddings])

delta = torch.ones_like(image_encoding) * step_size
walked_encodings = []
for step_index in range(walk_steps):
    walked_encodings.append(image_encoding)
    image_encoding += delta
walked_encodings = torch.stack(walked_encodings)


for cond_latents in walked_encodings:
  # if we use LMSDiscreteScheduler, let's make sure latents are mulitplied by sigmas
  if isinstance(scheduler, LMSDiscreteScheduler):
    cond_latents = cond_latents * scheduler.sigmas[0]

  # init the scheduler
  accepts_offset = "offset" in set(inspect.signature(scheduler.set_timesteps).parameters.keys())
  extra_set_kwargs = {}
  if accepts_offset:
      extra_set_kwargs["offset"] = 1
  scheduler.set_timesteps(num_inference_steps, **extra_set_kwargs)
  accepts_eta = "eta" in set(inspect.signature(scheduler.step).parameters.keys())
  extra_step_kwargs = {}
  if accepts_eta:
      extra_step_kwargs["eta"] = 0.0
  
  # diffuse!
  for i, t in enumerate(scheduler.timesteps):
    # expand the latents for classifier free guidance
    latent_model_input = torch.cat([cond_latents] * 2)
    if isinstance(scheduler, LMSDiscreteScheduler):
      sigma = scheduler.sigmas[i]
      latent_model_input = latent_model_input / ((sigma**2 + 1) ** 0.5)

    # predict the noise residual
    noise_pred = unet(latent_model_input, t, encoder_hidden_states=text_embeddings)["sample"]

    # cfg
    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)

    # compute the previous noisy sample x_t -> x_t-1
    if isinstance(scheduler, LMSDiscreteScheduler):
        '''
        cond_latents: contains ['pred_original_sample'] and ['prev_sample']
        '''
        cond_latents = scheduler.step(noise_pred, i, cond_latents, **extra_step_kwargs)
        cond_latents = cond_latents["prev_sample"]
    else:
        cond_latents = scheduler.step(noise_pred, t, cond_latents, **extra_step_kwargs)["prev_sample"]

  # scale and decode the image latents with vae
  cond_latents = 1 / 0.18215 * cond_latents
  image = vae.decode(cond_latents)['sample']

  

# Start step
start_step = 0 #@param Explore ;) The earlier the step, the higher the sigma which means more noise is added. The later the step, the less noise.
start_sigma = scheduler.sigmas[start_step]
start_timestep = int(scheduler.timesteps[start_step])

# Prep latents
noise = torch.randn_like(walked_encodings)
latents = scheduler.add_noise(walked_encodings, noise, start_timestep)
latents = latents.to(torch_device)
latents = latents * start_sigma  # << NB


with autocast("cuda"):
  for i, t in tqdm(enumerate(scheduler.timesteps)):
    # expand the latents if we are doing classifier-free guidance to avoid doing two forward passes.
    latent_model_input = torch.cat([latents] * 2)
    sigma = scheduler.sigmas[i]
    latent_model_input = latent_model_input / ((sigma**2 + 1) ** 0.5)

    latent_model_input = latent_model_input.squeeze(1)
    # predict the noise residual
    noise_pred = unet(latent_model_input, t, encoder_hidden_states=text_embeddings)["sample"]
    
    # cfg
    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
    
    # compute the previous noisy sample x_t -> x_t-1
    if isinstance(scheduler, LMSDiscreteScheduler):
      '''
      cond_latents: contains ['pred_original_sample'] and ['prev_sample']
      '''
      cond_latents = scheduler.step(noise_pred, i, cond_latents, **extra_step_kwargs)
      cond_latents = cond_latents["prev_sample"]
      print()
    else:
      cond_latents = scheduler.step(noise_pred, t, cond_latents, **extra_step_kwargs)["prev_sample"]
    
    print()

# scale and decode the image latents with vae
decoded_images = latents_to_pil(cond_latents)

for i in range(len(decoded_images)):
  im=decoded_images[i]
  im.save(f'im_{i}.png')
print()























# STEERING AN image encoding
#####################################################################################################################
prompt = ["blue steel texture map, 4k"]
# Prep text 
text_input = tokenizer(prompt, padding="max_length", max_length=tokenizer.model_max_length, truncation=True, return_tensors="pt")
with torch.no_grad():
  text_embeddings = text_encoder(text_input.input_ids.to(torch_device))[0]
max_length = text_input.input_ids.shape[-1]
uncond_input = tokenizer(
    [""] * batch_size, padding="max_length", max_length=max_length, return_tensors="pt"
)
with torch.no_grad():
  uncond_embeddings = text_encoder(uncond_input.input_ids.to(torch_device))[0] 
text_embeddings = torch.cat([uncond_embeddings, text_embeddings])

# Prep Scheduler
scheduler.set_timesteps(num_inference_steps)

# Start step
start_step = 0 #@param Explore ;) The earlier the step, the higher the sigma which means more noise is added. The later the step, the less noise.
start_sigma = scheduler.sigmas[start_step]
start_timestep = int(scheduler.timesteps[start_step])

# Prep latents
noise = torch.randn_like(encoded)
latents = scheduler.add_noise(encoded, noise, start_timestep)
latents = latents.to(torch_device)
latents = latents * start_sigma  # << NB

# Loop
with autocast("cuda"):
  for i, t in tqdm(enumerate(scheduler.timesteps)):
    if i > start_step:
      # expand the latents if we are doing classifier-free guidance to avoid doing two forward passes.
      latent_model_input = torch.cat([latents] * 2)
      sigma = scheduler.sigmas[i]
      latent_model_input = latent_model_input / ((sigma**2 + 1) ** 0.5)

      # predict the noise residual
      with torch.no_grad():
        noise_pred = unet(latent_model_input, t, encoder_hidden_states=text_embeddings)["sample"]

      # perform guidance
      noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
      noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)

      # compute the previous noisy sample x_t -> x_t-1
      latents = scheduler.step(noise_pred, i, latents)["prev_sample"]

decoded_img = latents_to_pil(latents)[0]
utils.show2images(input_image,decoded_img)
print()