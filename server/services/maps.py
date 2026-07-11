"""Normal and height map generation via DeepBump (ONNX), called in-process.

The ONNX session is created once (per process) and reused for every texture;
the vendored module_color_to_normals.apply() would otherwise reload the 26MB
model from disk on every call. GPU execution providers are used when the
installed onnxruntime exposes them, falling back to CPU.
"""
import logging
import os
import sys

import numpy as np
import imageio.v3 as iio
import onnxruntime as ort

from server.config import CWD

log = logging.getLogger(__name__)

# DeepBump-7 contains its own utils.py which would shadow the repo's utils
# package, so its dir goes on sys.path only for the duration of the import.
_DEEPBUMP_DIR = os.path.join(CWD, "utils", "DeepBump-7")
sys.path.insert(0, _DEEPBUMP_DIR)
try:
    import utils_inference  # noqa: E402
    import module_normals_to_height  # noqa: E402
    import module_normals_to_curvature  # noqa: E402
finally:
    sys.path.remove(_DEEPBUMP_DIR)

ort.disable_telemetry_events()

_session = None


def _get_session():
    global _session
    if _session is None:
        available = ort.get_available_providers()
        providers = [p for p in ("CUDAExecutionProvider", "DmlExecutionProvider")
                     if p in available] + ["CPUExecutionProvider"]
        _session = ort.InferenceSession(
            os.path.join(_DEEPBUMP_DIR, "deepbump256.onnx"), providers=providers)
        log.info("DeepBump ONNX session ready (providers: %s)",
                 ", ".join(_session.get_providers()))
    return _session


def _color_to_normals(color_img, overlap="MEDIUM"):
    """module_color_to_normals.apply() with a cached ONNX session."""
    img = np.mean(color_img[0:3], axis=0, keepdims=True)

    tile_size = 256
    overlaps = {"SMALL": tile_size // 6, "MEDIUM": tile_size // 4,
                "LARGE": tile_size // 2}
    stride_size = tile_size - overlaps[overlap]
    tiles, paddings = utils_inference.tiles_split(
        img, (tile_size, tile_size), (stride_size, stride_size)
    )

    pred_tiles = utils_inference.tiles_infer(tiles, _get_session(),
                                             progress_callback=None)
    pred_img = utils_inference.tiles_merge(
        pred_tiles, (stride_size, stride_size),
        (3, img.shape[1], img.shape[2]), paddings,
    )
    return utils_inference.normalize(pred_img)


def _read_chw(path):
    img = iio.imread(path)
    if img.ndim == 2:
        img = np.stack([img] * 3, axis=-1)
    return np.transpose(img[:, :, :3], (2, 0, 1)) / 255


def _write_chw(path, img):
    iio.imwrite(path, (np.transpose(img, (1, 2, 0)) * 255).astype(np.uint8))


def generate_normal_and_height(texture_filepath):
    """Create <name>_normal.png, <name>_height.png, and <name>_ao.png next
    to the texture."""
    directory = os.path.dirname(texture_filepath)
    name = os.path.splitext(os.path.basename(texture_filepath))[0]

    normal_path = os.path.join(directory, f"{name}_normal.png")
    normals = _color_to_normals(_read_chw(texture_filepath))
    _write_chw(normal_path, normals)

    height_path = os.path.join(directory, f"{name}_height.png")
    height = module_normals_to_height.apply(normals, True, None)
    _write_chw(height_path, height)

    # Ambient occlusion from curvature: the curvature map is normalized with
    # cavities dark and flat areas mid-gray, so shift it up so flat surfaces
    # are fully unoccluded (1.0) and only cavities darken.
    ao_path = os.path.join(directory, f"{name}_ao.png")
    curvature = module_normals_to_curvature.apply(normals, "SMALL", None)
    _write_chw(ao_path, np.clip(curvature + 0.5, 0.0, 1.0))

    return normal_path, height_path, ao_path
