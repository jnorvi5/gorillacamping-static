import os
from pymongo import MongoClient
import chromadb
from chromadb.utils import embedding_functions

# --- CONFIGURATION ---
MONGO_URI = os.environ.get("MONGO_URI")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "gorillacamping_kb"

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-3-small"
)
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=openai_ef,
    metadata={"hnsw:space": "cosine"}
)

# --- Ingest blog posts ---
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["gorillacamping"]
blog_posts = list(db.posts.find({"status": "published"}))

documents = []
metadatas = []
ids = []

for post in blog_posts:
    content = f"Title: {post['title']}\n\n{post['content']}"
    documents.append(content)
    metadatas.append({"source": "blog", "slug": post['slug']})
    ids.append(str(post['_id']))

# --- Ingest gear (optional, but HIGHLY recommended) ---
for gear in db.gear.find({"active": True}):
    content = f"Gear: {gear['name']}\nDescription: {gear['description']}\nSpecs: {', '.join(gear.get('specs', []))}"
    documents.append(content)
    metadatas.append({"source": "gear", "affiliate_id": gear['affiliate_id']})
    ids.append(f"gear_{gear['affiliate_id']}")

if documents:
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"✅ Knowledge base built with {len(documents)} items.")
else:
    print("⚠️ No posts or gear found for ingestion.")
