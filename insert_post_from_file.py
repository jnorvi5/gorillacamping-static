import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

# Load MongoDB connection string
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("❌ Set MONGO_URI in your environment")

# Auto-correct connection string format if needed
if not MONGO_URI.startswith("mongodb"):
    MONGO_URI = "mongodb+srv://" + MONGO_URI.split("://")[-1]

# Connect to MongoDB with error handling
try:
    client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
    client.admin.command("ping")
    print("✅ Connected to MongoDB!")
except Exception as e:
    print("❌ Connection failed:", e)
    exit(1)

db = client["gorillacamping"]
posts = db["posts"]

# Prompt for post details
title = input("Post title: ").strip()
slug = input("Slug (leave empty to auto-generate): ").strip() or title.lower().replace(" ", "-")
filepath = input("Path to Markdown file with post content (e.g. myblog.md): ").strip()
tags = input("Tags (comma-separated): ").split(",")
tags = [tag.strip() for tag in tags if tag.strip()]

# Read the content from the file
try:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
except Exception as e:
    print(f"❌ Error reading file: {e}")
    exit(1)

# Build post document
post = {
    "title": title,
    "slug": slug,
    "content": content,
    "tags": tags,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "status": "published"
}

# Insert post into DB with error handling
try:
    result = posts.insert_one(post)
    print(f"✅ Blog post created with ID: {result.inserted_id}")
except Exception as e:
    print("❌ FATAL INSERT ERROR:", e)
