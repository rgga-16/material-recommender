"""Best-effort DuckDuckGo web search (ddgs) for grounding assistant prompts.

Every failure mode — package missing, offline, rate-limited, timeout —
returns empty results so callers can always proceed without web context.
"""
import logging

from server.config import WEBSEARCH_MAX_RESULTS, WEBSEARCH_TIMEOUT_S

log = logging.getLogger(__name__)


def search(query: str, max_results: int | None = None) -> list[dict]:
    """Return [{title, snippet, url}, ...] for the query, or [] on any failure."""
    query = (query or "").strip()
    if not query:
        return []
    try:
        from ddgs import DDGS
    except ImportError:
        log.warning("ddgs package not installed; web search disabled")
        return []
    try:
        with DDGS(timeout=WEBSEARCH_TIMEOUT_S) as client:
            hits = client.text(query, max_results=max_results or WEBSEARCH_MAX_RESULTS)
            return [{"title": h.get("title", ""),
                     "snippet": h.get("body", ""),
                     "url": h.get("href", "")}
                    for h in (hits or [])]
    except Exception:
        log.warning("web search failed for %r", query, exc_info=True)
        return []


def context_block(query: str) -> tuple[str, str]:
    """(prompt_context, references_markdown) for the query; ("", "") when
    the search yields nothing."""
    results = search(query)
    if not results:
        return "", ""
    context_lines = ["Relevant web search results (use where helpful):"]
    reference_lines = []
    for r in results:
        title = r["title"] or r["url"]
        context_lines.append(f"- {title}: {r['snippet']}")
        if r["url"]:
            reference_lines.append(f"- [{title}]({r['url']})")
    references = ""
    if reference_lines:
        references = "**References:**\n" + "\n".join(reference_lines)
    return "\n".join(context_lines), references
