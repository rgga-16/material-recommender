"""Texture generation service (local diffusers pipeline, SD-Turbo by default).

Public contract:

    generate(prompt: str, n: int = 1, imsize: int = 512, seamless: bool = True)
        -> list[PIL.Image.Image]
    unload() -> None   # free GPU memory

The pipeline is a lazy singleton: it loads on the first generate() call and
stays resident afterward. Thread safety is handled by the caller (the
single-worker jobs executor serializes all GPU-bound work), so no locking is
needed here.
"""
import logging

from server.config import MIN_FREE_VRAM_GB, OLLAMA_MODEL, OLLAMA_URL, SD_MODEL_ID

log = logging.getLogger(__name__)

# torch is imported lazily inside the functions that need it, so importing
# this module (e.g. registering routes, running the API tests) doesn't pull
# in the multi-GB ML stack.

_pipe = None
_device = None

PROMPT_SUFFIX = ", seamless texture, top-down close-up, high detail"


def ensure_vram(min_free_gb=MIN_FREE_VRAM_GB):
    """Best-effort: evict the local Ollama model if VRAM is tight.

    Failures are logged but never raised — this is an optimization, not a
    hard dependency.
    """
    import torch
    if not torch.cuda.is_available():
        return
    try:
        free_bytes, _total_bytes = torch.cuda.mem_get_info()
        free_gb = free_bytes / 1e9
        if free_gb < min_free_gb:
            import requests
            try:
                requests.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={"model": OLLAMA_MODEL, "keep_alive": 0},
                    timeout=5,
                )
            except Exception:
                log.warning("could not ask Ollama to release VRAM", exc_info=True)
    except Exception:
        log.warning("VRAM check failed", exc_info=True)


def _clamp_imsize(imsize):
    """Clamp to a positive multiple of 64, default 512."""
    try:
        imsize = int(imsize)
    except (TypeError, ValueError):
        return 512
    if imsize <= 0:
        return 512
    rounded = max(64, round(imsize / 64) * 64)
    return rounded


def _set_seamless(pipe, seamless):
    import torch
    mode = "circular" if seamless else "zeros"
    for module in (pipe.unet, pipe.vae):
        for m in module.modules():
            if isinstance(m, torch.nn.Conv2d):
                m.padding_mode = mode


def _get_pipeline():
    global _pipe, _device
    if _pipe is not None:
        return _pipe

    import torch
    from diffusers import AutoPipelineForText2Image

    _device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if _device == "cuda" else torch.float32

    kwargs = {"torch_dtype": dtype}
    if _device == "cuda":
        kwargs["variant"] = "fp16"

    # The machine's cached/env HF token may be stale/expired; sd-turbo is a
    # public, non-gated repo, so force an anonymous download rather than
    # failing on a bad stored credential.
    import os
    if not os.environ.get("HF_TOKEN_OVERRIDE_DISABLE_ANON"):
        kwargs["token"] = False

    log.info("loading %s on %s", SD_MODEL_ID, _device)
    pipe = AutoPipelineForText2Image.from_pretrained(SD_MODEL_ID, **kwargs)
    pipe = pipe.to(_device)

    # sd-turbo doesn't ship a safety checker, but guard against pipelines that do.
    if hasattr(pipe, "safety_checker") and pipe.safety_checker is not None:
        pipe.safety_checker = None

    try:
        pipe.enable_attention_slicing()
    except Exception:
        log.warning("attention slicing unavailable", exc_info=True)

    try:
        pipe.vae.enable_tiling()
    except AttributeError:
        try:
            pipe.enable_vae_tiling()
        except Exception:
            log.warning("VAE tiling unavailable", exc_info=True)

    _pipe = pipe
    return _pipe


def generate(prompt, n=1, imsize=512, seamless=True):
    ensure_vram()

    pipe = _get_pipeline()
    _set_seamless(pipe, seamless)

    size = _clamp_imsize(imsize)
    full_prompt = f"{prompt}{PROMPT_SUFFIX}"

    images = []
    for _ in range(n):
        output = pipe(
            prompt=full_prompt,
            num_inference_steps=2,
            guidance_scale=0.0,
            width=size,
            height=size,
        )
        images.append(output.images[0])
    return images


def unload():
    global _pipe
    _pipe = None
    import torch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
