from llm.adapter import generate_with_gemini

async def curate_context(scripture_text: str, web_snippets: list[str]) -> str:
    prompt = f"""
Combine these into a single meaningful spiritual theme.

SCRIPTURE:
{scripture_text}

WEB KNOWLEDGE:
{"".join(web_snippets)}

Return a unified short insight paragraph.
"""

    return generate_with_gemini(prompt)
