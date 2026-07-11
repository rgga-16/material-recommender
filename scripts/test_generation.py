"""Smoke test for the local SD-Turbo texture generation service.

Run from repo root:
    .venv/Scripts/python.exe scripts/test_generation.py

Generates two textures, runs normal/height map generation on one of them,
asserts the output files exist, and prints timing + peak VRAM usage.
"""
import os
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import torch

from server.services import maps, texture_gen

OUT_DIR = os.path.join(REPO_ROOT, "client", "public", "gen_images")

PROMPTS = [
    "weathered red brick wall",
    "light oak wood grain",
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    saved_paths = []
    per_image_times = []

    for prompt in PROMPTS:
        start = time.time()
        images = texture_gen.generate(prompt, n=1, imsize=512, seamless=True)
        elapsed = time.time() - start
        per_image_times.append(elapsed)

        assert len(images) == 1, f"Expected 1 image for prompt {prompt!r}, got {len(images)}"

        filename = f"{prompt}.png".replace(" ", "_").replace("/", "_")
        savepath = os.path.join(OUT_DIR, filename)
        images[0].save(savepath)
        assert os.path.exists(savepath), f"Missing saved texture: {savepath}"
        saved_paths.append(savepath)
        print(f"Generated {prompt!r} -> {savepath} in {elapsed:.2f}s")

    # Run normal/height map generation on the first saved texture.
    normal_path, height_path, ao_path = maps.generate_normal_and_height(saved_paths[0])
    assert os.path.exists(normal_path), f"Missing normal map: {normal_path}"
    assert os.path.exists(height_path), f"Missing height map: {height_path}"
    print(f"Normal map: {normal_path}")
    print(f"Height map: {height_path}")

    texture_gen.unload()

    total_time = sum(per_image_times)
    avg_time = total_time / len(per_image_times)
    print(f"Per-image generation times: {[f'{t:.2f}s' for t in per_image_times]}")
    print(f"Average time per image: {avg_time:.2f}s")

    if torch.cuda.is_available():
        peak_vram_gb = torch.cuda.max_memory_allocated() / 1e9
        print(f"Peak VRAM allocated: {peak_vram_gb:.2f} GB")
    else:
        print("CUDA not available; ran on CPU, no VRAM stats.")

    print("test_generation.py: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
