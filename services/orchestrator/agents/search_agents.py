import aiohttp
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SEARCH_API_URL = "https://openrouter.ai/api/v1/chat/completions"

async def web_search_agent(query: str) -> list[str]:
    """
    Uses LLM to call search engine indirectly (OpenRouter / Bing / etc.)
    """
    prompt = f"Search the web for: {query}\nExtract 5 relevant bullet summaries."

    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            SEARCH_API_URL,
            json={
                "model": "perplexity/sonar-small-chat",  # free search model
                "messages": [{"role": "user", "content": prompt}],
            },
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
        )

        data = await resp.json()
        result = data["choices"][0]["message"]["content"]

        return result.split("\n")
