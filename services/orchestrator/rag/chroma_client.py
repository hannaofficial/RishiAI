import os
import chromadb
from dotenv import load_dotenv

os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"


load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_DIR", "./.chroma")

client = chromadb.PersistentClient(path=CHROMA_DIR)

def get_collection(name: str):
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )
