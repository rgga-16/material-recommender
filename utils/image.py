import base64
import logging
import math
import os
import re
import shutil
from base64 import encodebytes
from io import BytesIO

from PIL import Image

log = logging.getLogger(__name__)

# Borrowed function from: https://www.generacodice.com/en/articolo/4761261/check-if-a-string-is-encoded-in-base64-using-python
RE_BASE64 = "^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$"
def is_b64(s: str) -> bool:
    return False if s is None or not re.search(RE_BASE64, s) else True

# Convert Image to Base64
def im_2_b64(image):
    buff = BytesIO()
    image.save(buff, format="JPEG")
    return base64.b64encode(buff.getvalue())

# Convert Base64 to Image
def b64_2_img(data):
    return Image.open(BytesIO(base64.b64decode(data)))

def impath_2_b64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def degrees_to_radians(degree):
    return math.radians(degree)

# Encodes image into base64. https://stackoverflow.com/questions/64065587/how-to-return-multiple-images-with-flask
def encode_image(image_path):
    pil_img = Image.open(image_path, mode="r")
    byte_arr = BytesIO()
    pil_img.save(byte_arr, format="PNG")
    return encodebytes(byte_arr.getvalue()).decode("ascii")

def emptydir(dir, delete_dirs=False):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif delete_dirs and os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            log.warning("failed to delete %s: %s", file_path, e)

def makedir(dir_path):
    os.makedirs(dir_path, exist_ok=True)
