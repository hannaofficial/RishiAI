from typing import List, Dict

def plan_queries(problem_text: str, rag_citations: List[Dict]) -> List[str]:
    """
    Tiny heuristic planner for demo:
    - If no RAG citations, generate 2 generic queries.
    - Else generate one query that includes the cited work name.
    """
    queries: List[str] = []
    if not rag_citations:
        queries = [
            f"{problem_text} site:wikipedia.org",
            f"bhagavad gita verse action results meaning"
        ]
    else:
        work = rag_citations[0].get("work", "Bhagavad Gita")
        queries = [f"{work} summary action without attachment"]
    return queries

def web_search_stub(queries: List[str]) -> List[Dict]:
    """
    STUB: returns an empty list for now.
    Replace with real search integration later (Serper, Tavily, etc.)
    """
    return []

def adequacy_gate(problem_text: str, rag_citations: List[Dict], web_snippets: List[Dict]) -> Dict:
    """
    Rates sufficiency of current evidence.
    For demo: sufficient if we have at least one RAG citation.
    """
    sufficient = bool(rag_citations)
    return {
        "sufficient": sufficient,
        "reason": "RAG had at least one grounded citation." if sufficient else "No grounded citations; consider web search."
    }
