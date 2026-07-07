"""Local LLM client backed by Ollama.

Replaces the old OpenAI-based models/llm/gpt3 module. Talks to a locally
running Ollama server (https://ollama.com) over its HTTP API.
"""
import json

import requests

from server.services.prompts import SYSTEM_PROMPT

MODEL = "qwen2.5:1.5b-instruct"
OLLAMA_URL = "http://localhost:11434"

MAX_HISTORY_MESSAGES = 20


class LLMUnavailableError(Exception):
    """Raised when the local Ollama server can't be reached."""
    pass


UNAVAILABLE_MSG = (
    "Ollama is not running. Install from https://ollama.com and run: "
    "ollama pull qwen2.5:1.5b-instruct"
)


def is_available() -> bool:
    """Return True if the Ollama server is reachable."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return resp.ok
    except requests.exceptions.RequestException:
        return False


def _post_chat(messages, temperature=0.7, format_schema=None, timeout=120):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
        "keep_alive": "2m",
    }
    if format_schema is not None:
        payload["format"] = format_schema

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise LLMUnavailableError(UNAVAILABLE_MSG) from e

    data = resp.json()
    message = data.get("message", {})
    return message.get("content", "")


def chat(messages: list, system: str | None = None, temperature: float = 0.7) -> str:
    """Run a single chat completion (no persisted history)."""
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)
    return _post_chat(full_messages, temperature=temperature)


def generate_json(messages: list, schema: dict, system: str | None = None,
                   temperature: float = 0.3) -> dict:
    """Run a chat completion constrained to a JSON schema, returning parsed JSON.

    Retries once (with a stricter reminder) if the first reply fails to parse.
    """
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    content = _post_chat(full_messages, temperature=temperature, format_schema=schema)
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        retry_messages = full_messages + [
            {"role": "user", "content": "Your previous reply was not valid JSON. "
                                         "Reply again with ONLY valid JSON matching the schema."}
        ]
        content = _post_chat(retry_messages, temperature=temperature, format_schema=schema)
        try:
            return json.loads(content)
        except (json.JSONDecodeError, TypeError):
            return {}


# ---------------------------------------------------------------------------
# Chatbot conversation history (ported from the old gpt3.message_history)
# ---------------------------------------------------------------------------

message_history = []


def _system_message():
    return {"role": "system", "content": SYSTEM_PROMPT}


def init_conversation() -> str:
    """Reset the conversation history and return the assistant's intro."""
    global message_history
    message_history = [_system_message()]
    intro_prompt = "Introduce yourself briefly to the user."
    message_history.append({"role": "user", "content": intro_prompt})
    reply = _post_chat(message_history, temperature=0.7)
    message_history.append({"role": "assistant", "content": reply})
    _trim_history()
    return reply


def _trim_history():
    """Keep at most MAX_HISTORY_MESSAGES messages, always preserving the
    leading system message."""
    global message_history
    if not message_history:
        return
    system_msg = message_history[0] if message_history[0]["role"] == "system" else None
    rest = message_history[1:] if system_msg else message_history[:]
    max_rest = MAX_HISTORY_MESSAGES - (1 if system_msg else 0)
    if len(rest) > max_rest:
        rest = rest[-max_rest:]
    message_history = ([system_msg] if system_msg else []) + rest


def query(prompt: str, role: str = "user", temperature: float = 0.7) -> str:
    """Append a user turn to the conversation history and return the reply."""
    global message_history
    if not message_history:
        message_history = [_system_message()]
    message_history.append({"role": role, "content": prompt})
    _trim_history()
    try:
        reply = _post_chat(message_history, temperature=temperature)
    except LLMUnavailableError:
        message_history.pop()
        raise
    message_history.append({"role": "assistant", "content": reply})
    _trim_history()
    return reply


def get_message_history():
    return message_history
