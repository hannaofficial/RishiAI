from .chroma_client import get_collection
from .embedder import embed_texts


def search_gita(query: str, k: int = 3):
    col = get_collection("gita")
    emb = embed_texts([query])[0]

    res = col.query(
        query_embeddings=[emb],
        n_results=k,
        include=["metadatas", "documents", "distances"]
    )

    hits = []
    for md, doc, dist in zip(res["metadatas"][0], res["documents"][0], res["distances"][0]):
        hits.append({
            "doc": doc,
            "meta": md,
            "score": 1 - dist  # cosine score hack
        })

    return hits
