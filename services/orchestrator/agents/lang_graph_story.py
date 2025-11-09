from typing import List, Dict
from langgraph.graph import StateGraph, START, END
from .schemas import StoryState
from .planner import plan_sources
from .search_agents import plan_queries, web_search_stub
from rag.retrieve import search_gita
from .prompts import STORY_SYSTEM, STORY_USER_TEMPLATE
from .llm_adapter import llm_generate

def _format_context(rag_hits: List[Dict], web_snippets: List[Dict]) -> str:
    parts = []
    if rag_hits:
        for h in rag_hits[:3]:
            meta = h.get("meta", {}) or {}
            cite = f"{meta.get('work','')} {meta.get('chapter','')}.{meta.get('verse','')}".strip()
            parts.append(f"[RAG] {cite}: {h.get('doc','')}")
    if web_snippets:
        for s in web_snippets[:2]:
            parts.append(f"[WEB] {s.get('title','')}: {s.get('snippet','')}")
    return "\n".join(parts) if parts else "(no context)"

def router(state: StoryState) -> StoryState:
    state["plan"] = plan_sources(state["problem_text"], state.get("emotion_tags", []))
    return state

def rag_node(state: StoryState) -> StoryState:
    sources = state["plan"]["sources"]
    if "rag" not in sources:
        state["rag_hits"] = []
        return state
    hits = []
    try:
        hits = search_gita(state["problem_text"], k=3)
    except Exception:
        hits = []
    state["rag_hits"] = hits
    return state

def search_node(state: StoryState) -> StoryState:
    sources = state["plan"]["sources"]
    if "search" not in sources:
        state["web_snippets"] = []
        return state
    qs = plan_queries(state["problem_text"], state["plan"].get("work"))
    state["web_snippets"] = web_search_stub(qs)
    return state

async def llm_node(state: StoryState) -> StoryState:
    sources = state["plan"]["sources"]
    use_llm = "llm" in sources or not state.get("rag_hits")
    if not use_llm:
        state["llm_story"] = ""
        return state
    ctx = _format_context(state.get("rag_hits", []), state.get("web_snippets", []))
    user = STORY_USER_TEMPLATE.format(problem=state["problem_text"], context=ctx)
    out = await llm_generate(STORY_SYSTEM, user)
    state["llm_story"] = out or ""
    return state

def compose_node(state: StoryState) -> StoryState:
    # Prefer RAG citation if exists
    cites = []
    if state.get("rag_hits"):
        meta = state["rag_hits"][0].get("meta", {}) or {}
        work = meta.get("work", "Bhagavad Gita")
        ch, vs = meta.get("chapter"), meta.get("verse")
        ref = f"{ch}.{vs}" if ch and vs else None
        cites = [{"work": work, "ref": ref}]
    else:
        cites = [{"work": "Bhagavad Gita", "ref": "2.47"}]  # safe default

    # If LLM produced a story, try to split takeaways; else use a tiny template
    text = state.get("llm_story") or (
        "You feel heavy because you hold the results too tight. "
        "Take one kind step. Let the rest be light. 💙\n\n"
        "Takeaways:\n- Do one tiny step today. 🌱\n- Breathe slow before you act.\n- Let results be light."
    )

    # Extract takeaways if present
    takeaways: List[str] = []
    if "Takeaways:" in text:
        parts = text.split("Takeaways:", 1)
        story_text = parts[0].strip()
        lines = [l.strip(" -•\t") for l in parts[1].strip().splitlines() if l.strip()]
        takeaways = [l for l in lines if l][:3]
    else:
        story_text = text
        takeaways = ["Do one tiny step today. 🌱","Breathe slow before you act.","Let results be light."]

    persona = state["plan"].get("persona","omniphilosopher")
    work = state["plan"].get("work", "Bhagavad Gita")
    state["citations"] = cites
    state["story_payload"] = {
        "title": "Do Your Part. Let Worry Be Light.",
        "slides": [
            {"image_url": "/assets/kurukshetra_1.jpg", "caption": "Arjuna feels fear on the field."},
            {"image_url": "/assets/krishna_guides.jpg", "caption": "Krishna speaks with care."},
        ],
        "narration_text": story_text,
        "takeaways": takeaways,
        "citations": cites,
        # bg_music_url filled in API
    }
    return state

# ---- Build the graph
def build_story_graph():
    g = StateGraph(StoryState)
    g.add_node("router", router)
    g.add_node("rag", rag_node)
    g.add_node("search", search_node)
    g.add_node("llm", llm_node)  # async
    g.add_node("compose", compose_node)

    g.add_edge(START, "router")
    # simple linear for demo; later you can branch dynamically
    g.add_edge("router", "rag")
    g.add_edge("rag", "search")
    g.add_edge("search", "llm")
    g.add_edge("llm", "compose")
    g.add_edge("compose", END)
    return g.compile()

# convenience runner
async def run_story_pipeline(problem_text: str, emotion_tags: List[str]) -> Dict:
    graph = build_story_graph()
    init: StoryState = {"problem_text": problem_text, "emotion_tags": emotion_tags}
    final: StoryState = await graph.ainvoke(init)
    return final
