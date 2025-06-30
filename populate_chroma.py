import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "gorillacamping_kb"
hf_ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
try:
    collection = chroma_client.create_collection(name=COLLECTION_NAME, embedding_function=hf_ef)
except:
    collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=hf_ef)

docs = [
    "How to stealth camp near public land without getting caught.",
    "Best solar generator for off-grid video creators is Jackery Explorer 240.",
    "To make $1,000/month camping, combine YouTube, affiliate links, and blog traffic.",
    "For water on the go, use a LifeStraw. It’s cheap, reliable, and packs small.",
    "Cannabis grows best outdoors in Virginia after the last frost, with organic soil."
]

collection.add(
    documents=docs,
    metadatas=[{"source": "manual"}]*len(docs),
    ids=[f"doc_{i}" for i in range(len(docs))]
)

print("✅ ChromaDB populated with starter knowledge.")
