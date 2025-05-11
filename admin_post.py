import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("Set MONGO_URI in your environment")

client = MongoClient(MONGO_URI)
db = client["gorillacamping"]
posts = db["posts"]

title = input("Post title: ").strip()
slug = input("Slug (leave empty to auto-generate): ").strip() or title.lower().replace(" ", "-")
content = input("Post content (HTML or Markdown): ").strip()
tags = input("Tags (comma-separated): ").split(",")
tags = [tag.strip() for tag in tags if tag.strip()]

post = {
    "title": title,
    "slug": slug,
    "content": content,
    "tags": tags,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

result = post.insert_one(post)
print(f" Blog post created with ID: {result.inserted_id}")
result = posts.insert_one(post)
print(f"✅ Blog post created with ID: {result.inserted_id}")
<<<<<<< HEAD
=======
import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("Set MONGO_URI in your environment")

client = MongoClient(MONGO_URI)
db = client["gorillacamping"]
posts = db["posts"]

title = input("Post title: ").strip()
slug = input("Slug (leave empty to auto-generate): ").strip() or title.lower().replace(" ", "-")
content = input("Post content (HTML or Markdown): ").strip()
tags = input("Tags (comma-separated): ").split(",")
tags = [tag.strip() for tag in tags if tag.strip()]

post = {
    "title": title,
    "slug": slug,
    "content": content,
    "tags": tags,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

result = posts.insert_one(post)
print(f"✅ Blog post created with ID: {result.inserted_id}")

>>>>>>> 097fcc0 (Add CLI blog post admin script)
