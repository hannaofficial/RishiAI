import os, json
import httpx

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini-translate")

async def llm_generate(system: str, user: str) -> str:
    """
    If OPENROUTER_API_KEY present, call OpenRouter; else return a safe template.
    Non-blocking for offline demo.
    """
    if not OPENROUTER_KEY:
        # Offline fallback: tiny rule-based "LLM"
        takeaways = ["Do one tiny step today. 🌱","Breathe slow before you act.","Let results be light."]
        return (
            "You feel heavy because you hold the result too tight. "
            "Take one small, kind action. Let the future be light. 💙\n\n"
            "Takeaways:\n- " + "\n- ".join(takeaways)
        )

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type":"application/json"}
    body = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role":"system","content":system},
            {"role":"user","content":user}
        ],
        "temperature": 0.7
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=body)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
