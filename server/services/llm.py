"""Local LLM client backed by Ollama.

Talks to a locally running Ollama server (https://ollama.com) over its HTTP
API. Chat history is kept per client session (the frontend sends a session
id) instead of one process-global conversation; idle sessions expire after
CHAT_SESSION_TTL_SECONDS.
"""
import json
import logging
import threading
import time

import requests

from server.config import (CHAT_SESSION_TTL_SECONDS, MAX_HISTORY_MESSAGES,
                           OLLAMA_MODEL, OLLAMA_URL, OLLAMA_VISION_MODEL)
from server.services import design_brief
from server.services.prompts import system_prompt

log = logging.getLogger(__name__)

MODEL = OLLAMA_MODEL
VISION_MODEL = OLLAMA_VISION_MODEL

DEFAULT_SESSION = "default"


class LLMUnavailableError(Exception):
    """Raised when the local Ollama server can't be reached."""
    pass


UNAVAILABLE_MSG = (
    "Ollama is not running. Install from https://ollama.com and run: "
    f"ollama pull {OLLAMA_MODEL}"
)


def is_available() -> bool:
    """Return True if the Ollama server is reachable."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return resp.ok
    except requests.exceptions.RequestException:
        return False


def vision_available() -> bool:
    """True if the configured multimodal model is pulled and Ollama is up."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        resp.raise_for_status()
    except requests.exceptions.RequestException:
        return False
    names = [m.get("name", "") for m in resp.json().get("models", [])]
    return any(VISION_MODEL in (name, name.split(":")[0]) for name in names)


def _attach_images(messages, images):
    """Copy of messages with base64 images attached to the last user message
    (Ollama multimodal format)."""
    if not images:
        return messages
    messages = [dict(m) for m in messages]
    for m in reversed(messages):
        if m.get("role") == "user":
            m["images"] = list(images)
            break
    return messages


def _chat_payload(messages, temperature, format_schema=None, stream=False,
                  model=None):
    payload = {
        "model": model or MODEL,
        "messages": messages,
        "stream": stream,
        "options": {"temperature": temperature},
        "keep_alive": "2m",
    }
    if format_schema is not None:
        payload["format"] = format_schema
    return payload


def _post_chat(messages, temperature=0.7, format_schema=None, timeout=120,
               model=None):
    payload = _chat_payload(messages, temperature, format_schema, model=model)
    try:
        resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise LLMUnavailableError(UNAVAILABLE_MSG) from e

    data = resp.json()
    message = data.get("message", {})
    return message.get("content", "")


def _post_chat_stream(messages, temperature=0.7, timeout=120):
    """Yield reply text chunks from a streaming Ollama chat completion."""
    payload = _chat_payload(messages, temperature, stream=True)
    try:
        resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload,
                             stream=True, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise LLMUnavailableError(UNAVAILABLE_MSG) from e

    for line in resp.iter_lines():
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        chunk = data.get("message", {}).get("content", "")
        if chunk:
            yield chunk
        if data.get("done"):
            break


def chat(messages: list, system: str | None = None, temperature: float = 0.7,
         images: list | None = None) -> str:
    """Run a single chat completion (no persisted history).

    images: optional list of base64-encoded images (no data: prefix); routes
    the request to the multimodal model.
    """
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)
    full_messages = _attach_images(full_messages, images)
    return _post_chat(full_messages, temperature=temperature,
                      model=VISION_MODEL if images else None)


def generate_json(messages: list, schema: dict, system: str | None = None,
                   temperature: float = 0.3, images: list | None = None) -> dict:
    """Run a chat completion constrained to a JSON schema, returning parsed JSON.

    Retries once (with a stricter reminder) if the first reply fails to parse.
    images: optional list of base64-encoded images; routes to the multimodal model.
    """
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)
    full_messages = _attach_images(full_messages, images)
    model = VISION_MODEL if images else None

    content = _post_chat(full_messages, temperature=temperature,
                         format_schema=schema, model=model)
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        retry_messages = full_messages + [
            {"role": "user", "content": "Your previous reply was not valid JSON. "
                                         "Reply again with ONLY valid JSON matching the schema."}
        ]
        content = _post_chat(retry_messages, temperature=temperature,
                             format_schema=schema, model=model)
        try:
            return json.loads(content)
        except (json.JSONDecodeError, TypeError):
            log.warning("LLM returned unparseable JSON twice; returning {}")
            return {}


# ---------------------------------------------------------------------------
# Chatbot conversation history, per client session
# ---------------------------------------------------------------------------

_sessions = {}  # session_id -> {"messages": [...], "last_used": monotonic}
_sessions_lock = threading.Lock()


def _system_message():
    return {"role": "system",
            "content": system_prompt(design_brief.get_brief())}


def _evict_stale_locked():
    cutoff = time.monotonic() - CHAT_SESSION_TTL_SECONDS
    for sid in [s for s, sess in _sessions.items() if sess["last_used"] < cutoff]:
        del _sessions[sid]


def _session_messages(session_id, reset=False):
    """A copy of the session's message list (creating the session if needed).

    The leading system message is rebuilt on every call so design-brief edits
    reach existing sessions immediately.
    """
    with _sessions_lock:
        _evict_stale_locked()
        sess = _sessions.get(session_id)
        if sess is None or reset:
            sess = {"messages": [_system_message()], "last_used": time.monotonic()}
            _sessions[session_id] = sess
        elif sess["messages"] and sess["messages"][0]["role"] == "system":
            sess["messages"][0] = _system_message()
        sess["last_used"] = time.monotonic()
        return list(sess["messages"])


def _store_turn(session_id, user_msg, assistant_reply):
    """Append a completed user/assistant exchange to the session history."""
    with _sessions_lock:
        sess = _sessions.get(session_id)
        if sess is None:
            sess = {"messages": [_system_message()], "last_used": time.monotonic()}
            _sessions[session_id] = sess
        sess["messages"].append(user_msg)
        sess["messages"].append({"role": "assistant", "content": assistant_reply})
        sess["messages"] = _trimmed(sess["messages"])
        sess["last_used"] = time.monotonic()


def _trimmed(messages):
    """Keep at most MAX_HISTORY_MESSAGES messages, always preserving the
    leading system message."""
    if not messages:
        return messages
    system_msg = messages[0] if messages[0]["role"] == "system" else None
    rest = messages[1:] if system_msg else messages[:]
    max_rest = MAX_HISTORY_MESSAGES - (1 if system_msg else 0)
    if len(rest) > max_rest:
        rest = rest[-max_rest:]
    return ([system_msg] if system_msg else []) + rest


def init_conversation(session_id: str = DEFAULT_SESSION) -> str:
    """Reset the session's history and return the assistant's intro."""
    messages = _session_messages(session_id, reset=True)
    intro_msg = {"role": "user", "content": "Introduce yourself briefly to the user."}
    reply = _post_chat(messages + [intro_msg], temperature=0.7)
    _store_turn(session_id, intro_msg, reply)
    return reply


def _context_message(context):
    """Ephemeral system message carrying per-turn context (e.g. web search
    results); sent with the request but never stored in the history."""
    return {"role": "system", "content": context}


def query(prompt: str, session_id: str = DEFAULT_SESSION, role: str = "user",
          temperature: float = 0.7, context: str | None = None) -> str:
    """Run one conversation turn against the session history."""
    messages = _session_messages(session_id)
    if context:
        messages = messages + [_context_message(context)]
    user_msg = {"role": role, "content": prompt}
    reply = _post_chat(_trimmed(messages + [user_msg]), temperature=temperature)
    _store_turn(session_id, user_msg, reply)
    return reply


def query_stream(prompt: str, session_id: str = DEFAULT_SESSION,
                 role: str = "user", temperature: float = 0.7,
                 context: str | None = None):
    """Streaming version of query(): yields reply chunks, then persists the
    full exchange to the session history."""
    messages = _session_messages(session_id)
    if context:
        messages = messages + [_context_message(context)]
    user_msg = {"role": role, "content": prompt}
    parts = []
    for chunk in _post_chat_stream(_trimmed(messages + [user_msg]),
                                   temperature=temperature):
        parts.append(chunk)
        yield chunk
    _store_turn(session_id, user_msg, "".join(parts))
