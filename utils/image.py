import matplotlib.pyplot as plt 
import numpy as np 
from PIL import Image
import torch 
import os, shutil 
import io
from base64 import encodebytes

css= '''
    .gradio-container #materials_generator {
        background-color: red;
    }
'''

# Encodes image into base64. https://stackoverflow.com/questions/64065587/how-to-return-multiple-images-with-flask 
def encode_image(image_path):
    pil_img = Image.open(image_path, mode='r') # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
    return encoded_img

def emptydir(dir,delete_dirs=False):
    # loop through all the files and subdirectories in the directory
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path):
                # remove the file
                print(f"{file_path} deleted")
                os.remove(file_path)
            elif delete_dirs and os.path.isdir(file_path):
                # remove the subdirectory and its contents
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def makedir(dir_path):
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        pass

def show2images(leftpic,rightpic):
    f = plt.figure()
    f.add_subplot(1,2, 1)
    plt.imshow(np.rot90(leftpic,2))
    f.add_subplot(1,2, 2)
    plt.imshow(np.rot90(rightpic,2))
    plt.show(block=True)

def export_as_gif(filename, images, frames_per_second=10, rubber_band=False):
    if rubber_band:
        images += images[2:-1][::-1]
    images[0].save(
        filename,
        save_all=True,
        append_images=images[1:],
        duration=1000 // frames_per_second,
        loop=0,
    )

def slerp(t, v0, v1, DOT_THRESHOLD=0.9995):
    """ helper function to spherically interpolate two arrays v1 v2 """

    if not isinstance(v0, np.ndarray):
        inputs_are_torch = True
        input_device = v0.device
        v0 = v0.cpu().numpy()
        v1 = v1.cpu().numpy()

    dot = np.sum(v0 * v1 / (np.linalg.norm(v0) * np.linalg.norm(v1)))
    if np.abs(dot) > DOT_THRESHOLD:
        v2 = (1 - t) * v0 + t * v1
    else:
        theta_0 = np.arccos(dot)
        sin_theta_0 = np.sin(theta_0)
        theta_t = theta_0 * t
        sin_theta_t = np.sin(theta_t)
        s0 = np.sin(theta_0 - theta_t) / sin_theta_0
        s1 = sin_theta_t / sin_theta_0
        v2 = s0 * v0 + s1 * v1

    if inputs_are_torch:
        v2 = torch.from_numpy(v2).to(input_device)

    return v2