from typing import List
from datetime import datetime
from rag.chroma_client import get_collection
from rag.embedder import embed_texts

COLLECTION_NAME = "user_memory"

def _col():
    return get_collection(COLLECTION_NAME)

def summarize_turns_to_note(turns: List[dict]) -> str:
    """
    Very small, deterministic stub (no LLM):
    - take last 2 user/guide turns
    - make a compact note we can embed
    - simple English, no PII
    """
    if not turns:
        return ""
    last_user = next((t["text"] for t in reversed(turns) if t.get("role")=="user"), "")
    last_guide = next((t["text"] for t in reversed(turns) if t.get("role")=="guide"), "")
    note = (
        f"User concern (short): {last_user[:160]}. "
        f"Guide hint (short): {last_guide[:160]}."
    )
    return note

def upsert_summary(user_id: str, session_id: str, turns: List[dict]):
    note = summarize_turns_to_note(turns)
    if not note:
        return
    emb = embed_texts([note])[0]
    doc = note
    meta = {
        "user_id": user_id,
        "session_id": session_id,
        "type": "summary",
        "ts": datetime.utcnow().isoformat(),
    }
    _col().upsert(
        ids=[f"{user_id}:{session_id}:{meta['ts']}"],
        embeddings=[emb],
        documents=[doc],
        metadatas=[meta],
    )

def summarize_if_needed(user_id: str, session_id: str, turns: List[dict], every_n:int=6):
    """
    Call this after appending a turn.
    Writes to user_memory every N turns (shared across all chatbots).
    """
    if len(turns) % every_n == 0:
        upsert_summary(user_id, session_id, turns)
