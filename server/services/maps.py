"""Normal and height map generation via DeepBump (ONNX), called in-process.

Replaces the old os.system("python utils/DeepBump-7/cli.py ...") subprocess
calls: the DeepBump modules are plain functions over numpy + onnxruntime and
resolve their .onnx weights relative to their own directory.
"""
import os
import sys

import numpy as np
import imageio.v3 as iio

from server.config import CWD

_DEEPBUMP_DIR = os.path.join(CWD, "utils", "DeepBump-7")
if _DEEPBUMP_DIR not in sys.path:
    sys.path.insert(0, _DEEPBUMP_DIR)

import module_color_to_normals  # noqa: E402
import module_normals_to_height  # noqa: E402


def _read_chw(path):
    img = iio.imread(path)
    if img.ndim == 2:
        img = np.stack([img] * 3, axis=-1)
    return np.transpose(img[:, :, :3], (2, 0, 1)) / 255


def _write_chw(path, img):
    iio.imwrite(path, (np.transpose(img, (1, 2, 0)) * 255).astype(np.uint8))


def generate_normal_and_height(texture_filepath):
    """Create <name>_normal.png and <name>_height.png next to the texture."""
    directory = os.path.dirname(texture_filepath)
    name = os.path.splitext(os.path.basename(texture_filepath))[0]

    normal_path = os.path.join(directory, f"{name}_normal.png")
    normals = module_color_to_normals.apply(_read_chw(texture_filepath), "MEDIUM", None)
    _write_chw(normal_path, normals)

    height_path = os.path.join(directory, f"{name}_height.png")
    height = module_normals_to_height.apply(normals, True, None)
    _write_chw(height_path, height)

    return normal_path, height_path
