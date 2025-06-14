import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

# Load MongoDB connection string
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("❌ Set MONGO_URI in your environment")

# Connect to MongoDB
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client["gorillacamping"]
posts = db["posts"]

# Prompt for post details
title = input("Post title: ").strip()
slug = input("Slug (leave empty to auto-generate): ").strip() or title.lower().replace(" ", "-")
content = input("Post content (HTML or Markdown): ").strip()
tags = input("Tags (comma-separated): ").split(",")
tags = [tag.strip() for tag in tags if tag.strip()]

# Build post document
post = {
    "title": title,
    "slug": slug,
    "content": content,
    "tags": tags,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "status": "published"  # Ensure the post is published!
}

# Insert post into DB
result = posts.insert_one(post)
print(f"✅ Blog post created with ID: {result.inserted_id}")


