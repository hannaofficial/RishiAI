from .chroma_client import get_collection
from .embedder import embed_texts

# few verses for demo
verses = [
    {
        "id": "gita-2-47",
        "text": "You have a right to action, not to the fruits of action.",
        "work": "Bhagavad Gita",
        "chapter": 2,
        "verse": 47,
        "translation": "Act, but do not cling to results."
    },
    {
        "id": "gita-2-48",
        "text": "Be steadfast in yoga; perform your duty and abandon attachment to success or failure.",
        "work": "Bhagavad Gita",
        "chapter": 2,
        "verse": 48,
        "translation": "Do your duty with an even mind."
    }
]

def main():
    col = get_collection("gita")
    texts = [v["text"] + " " + v["translation"] for v in verses]
    embeddings = embed_texts(texts)
    ids = [v["id"] for v in verses]
    metadatas = verses

    col.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    print("✅ Seeded Bhagavad Gita verses:", ids)

if __name__ == "__main__":
    main()
