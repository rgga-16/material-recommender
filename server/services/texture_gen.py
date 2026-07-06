"""Texture generation service.

TEMPORARY (Phase 2 stub): delegates to the legacy DALL-E generator so the app
keeps running until Phase 3B replaces this file with the local SD-Turbo
implementation. The public interface below is the contract Phase 3B keeps:

    generate(prompt: str, n: int = 1, imsize: int = 512, seamless: bool = True)
        -> list[PIL.Image.Image]
    unload() -> None   # free GPU memory
"""

_generator = None


def _get_generator():
    global _generator
    if _generator is None:
        from texture_transfer_3d import DALLE2
        _generator = DALLE2()
    return _generator


def generate(prompt, n=1, imsize=512, seamless=True):
    return _get_generator().text2texture(prompt, n=n, gen_imsize=imsize)


def unload():
    global _generator
    _generator = None
