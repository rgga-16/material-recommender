"""Smoke test for the local Ollama-backed LLM service.

Run from repo root:
    .venv/Scripts/python.exe scripts/test_llm.py

Checks that Ollama is reachable, runs a plain chat turn, runs a
generate_json call against COLOR_PALETTES_SCHEMA and validates its shape,
and runs an EN->JA translation.
"""
import os
import re
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from server.services import llm, prompts

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def main():
    print(f"Checking Ollama availability at {llm.OLLAMA_URL} ...")
    assert llm.is_available(), (
        "Ollama is not reachable. Install from https://ollama.com and run: "
        "ollama pull qwen2.5:1.5b-instruct"
    )
    print("Ollama is available.")

    # 1. Plain chat turn.
    print("\nRunning chat() ...")
    start = time.time()
    reply = llm.chat(
        [{"role": "user", "content": "Say hello in one short sentence."}],
        system=prompts.SYSTEM_PROMPT,
        temperature=0.5,
    )
    elapsed = time.time() - start
    assert isinstance(reply, str) and len(reply.strip()) > 0, "chat() returned empty reply"
    print(f"chat() reply ({elapsed:.1f}s): {reply.strip()}")

    # 2. generate_json with COLOR_PALETTES_SCHEMA.
    print("\nRunning generate_json() with COLOR_PALETTES_SCHEMA ...")
    start = time.time()
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.suggest_color_palettes_prompt(
            "Suggest color palettes for a cozy Scandinavian living room.")}],
        schema=prompts.COLOR_PALETTES_SCHEMA,
        system=prompts.SYSTEM_PROMPT,
    )
    elapsed = time.time() - start
    print(f"generate_json() took {elapsed:.1f}s")
    print(f"Parsed: {parsed}")

    assert isinstance(parsed, dict), "generate_json() did not return a dict"
    assert "color_palettes" in parsed, "Missing 'color_palettes' key"
    palettes = parsed["color_palettes"]
    assert isinstance(palettes, list) and len(palettes) > 0, "color_palettes should be a non-empty list"
    for palette in palettes:
        assert "name" in palette and isinstance(palette["name"], str)
        assert "description" in palette and isinstance(palette["description"], str)
        assert "codes" in palette and isinstance(palette["codes"], list) and len(palette["codes"]) > 0
        for code in palette["codes"]:
            assert HEX_RE.match(code), f"Invalid hex color code: {code!r}"
    print("color_palettes shape validated OK.")

    # 3. Translation EN -> JA.
    print("\nRunning translate prompt EN -> JA ...")
    start = time.time()
    translated = llm.chat(
        [{"role": "user", "content": prompts.translate_prompt(
            "This oak wood texture would look great on your dining table.", "Japanese", "English")}],
        system=prompts.TRANSLATE_SYSTEM_PROMPT,
        temperature=0.1,
    )
    elapsed = time.time() - start
    assert isinstance(translated, str) and len(translated.strip()) > 0, "translate reply was empty"
    print(f"Translation ({elapsed:.1f}s): {translated.strip()}")

    print("\ntest_llm.py: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
