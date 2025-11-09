from typing import Dict, List

PHILOS_MAP = [
    # (trigger words, persona, work_hint)
    ({"anxiety","overthinking","fear","stress"}, "krishna", "Bhagavad Gita"),
    ({"rational","logic","analysis","question"}, "jiddu", None),
    ({"breath","meditation","still","yoga"}, "patanjali", "Yoga Sutra"),
]

def plan_sources(problem_text: str, emotion_tags: List[str]) -> Dict:
    t = {w.lower() for w in emotion_tags or []}
    persona, work = "omniphilosopher", None
    for keys, p, w in PHILOS_MAP:
        if t.intersection(keys):
            persona, work = p, w
            break
    # simple plan: try RAG first; if no hits, include LLM; search kept optional
    return {"sources": ["rag","llm"], "persona": persona, "work": work}
