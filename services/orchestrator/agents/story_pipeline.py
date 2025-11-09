from llm.adapter import generate_with_gemini
from rag.retrieve import search_gita

async def run_story_pipeline(problem_text: str, emotion_tags: list[str]):
    # STEP 1 — RAG search (scriptures / ancient content)
    rag_hits = search_gita(problem_text, k=3)

    # → insert context (if found)
    rag_context = ""
    if rag_hits:
        for h in rag_hits:
            rag_context += f"- {h['doc']}\n"

    # STEP 2 — build a natural prompt
    final_prompt = f"""
You are a compassionate ancient guide.
User is experiencing: {emotion_tags}

Problem:
{problem_text}

Relevant scripture / context:
{rag_context}

Write a short calming story using:
• simple english
• very emotional empathic voice
• 2–3 emojis (no more)
• include one subtle life lesson

Output JSON as:
{{
  "title": "...",
  "narration_text": "...",
  "slides": [
    {{"image_prompt": "description for image generation"}},
    {{"image_prompt": "description for image generation"}}
  ],
  "takeaways": ["...", "..."],
  "citations": [{{"work":"Bhagavad Gita","ref":"2.47"}}]
}}
"""

    story_text = generate_with_gemini(final_prompt)

    import json
    return {
        "story_payload": json.loads(story_text)
    }
