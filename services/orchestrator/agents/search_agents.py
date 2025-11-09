from __future__ import annotations
from typing import List, Dict
import os, re, asyncio
import aiohttp

# ---------- Config ----------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# You can change this to any search-capable model you have access to on OpenRouter.
# Perplexity Sonar models are popular for retrieval-ish answers.
OPENROUTER_SEARCH_MODEL = os.getenv("OPENROUTER_SEARCH_MODEL", "perplexity/sonar-small-chat")

# ---------- Helpers ----------
_BULLET_RE = re.compile(r"^\s*[-•*]\s*", flags=re.MULTILINE)

def _to_bullets(text: str, max_items: int = 5) -> List[str]:
    if not text:
        return []
    # Split by lines; keep non-empty; strip bullets and whitespace
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    cleaned = []
    for l in lines:
        l = _BULLET_RE.sub("", l).strip()
        # also split numbered lists like "1) ..." or "1. ..."
        l = re.sub(r"^\d+[\)\.]\s*", "", l)
        if l:
            cleaned.append(l)
        if len(cleaned) >= max_items:
            break
    # If the model returned a single paragraph, split sentences as fallback
    if not cleaned:
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        cleaned = [p.strip() for p in parts if p.strip()][:max_items]
    return cleaned[:max_items]

# ---------- API used by lang_graph_story ----------
def plan_queries(problem_text: str, work_hint: str | None = None) -> List[str]:
    """
    Build simple search queries given the user's problem and (optional) scripture hint.
    """
    if work_hint:
        return [
            f"{work_hint} story meaning for: {problem_text}",
            f"{work_hint} advice act without attachment simple explanation",
        ]
    return [
        f"Indian epic story that helps with: {problem_text}",
        f"how to handle {problem_text} spiritual wisdom simple",
    ]

def web_search_stub(queries: List[str]) -> List[Dict]:
    """
    Synchronous stub (no network). Return empty list for now.
    Shape: [{"title": "...", "snippet": "...", "url": "..."}]
    """
    return []

# ---------- API used by /story/stream ----------
async def web_search_agent(query: str) -> List[str]:
    """
    Use OpenRouter to get a small set of concise bullet insights for 'query'.
    Returns a list of strings (bullets).
    """
    # Safety: if no key set, return a tiny static fallback so pipeline continues.
    if not OPENROUTER_API_KEY:
        return [
            f"Quick note about: {query}",
            "People often find calm by taking one small, kind action.",
            "Slow, even breathing reduces anxious loops.",
        ]

    prompt = (
        "You are a concise research assistant.\n"
        f"Task: Search the web for this user need and extract 3-5 crisp bullet insights:\n\n"
        f"QUERY: {query}\n\n"
        "Return only short bullets (no URLs), simple English, helpful and neutral."
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": OPENROUTER_SEARCH_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(OPENROUTER_URL, headers=headers, json=body) as resp:
                resp.raise_for_status()
                data = await resp.json()
                text = data["choices"][0]["message"]["content"]
                bullets = _to_bullets(text, max_items=5)
                # Guard: ensure we have something meaningful
                return bullets or [
                    f"Perspective on: {query}",
                    "Act on one tiny, controllable step.",
                    "Detach a little from the outcome to reduce pressure.",
                ]
    except Exception:
        # Soft-fail: keep the pipeline alive with generic but useful lines
        return [
            f"General insight about: {query}",
            "Name the worry, then do one 5-minute task.",
            "Breathe slowly (4-4-4-4) to settle the body.",
        ]
