from typing import List, Dict, Optional, TypedDict

class StoryState(TypedDict, total=False):
    problem_text: str
    emotion_tags: List[str]
    plan: Dict              # {"sources":["rag","llm","search"], "persona":"krishna", "work":"Bhagavad Gita"}
    rag_hits: List[Dict]    # [{doc:str, meta:{...}, score:float}]
    web_snippets: List[Dict]
    llm_story: str
    citations: List[Dict]
    story_payload: Dict
