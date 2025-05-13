from pymongo import MongoClient
from datetime import datetime

uri = "mongodb+srv://jnorvi5:gorillaSecure2025@cluster0.c0gofgp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client["gorillacamping"]

# Insert test blog post
db.posts.insert_one({
    "title": "Welcome to the Blog!",
    "slug": "welcome-blog",
    "content": "This is the first post. More coming soon!",
    "tags": ["intro", "welcome"],
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
})

# Insert test subscriber
db.subscribers.insert_one({
    "email": "test@example.com",
    "timestamp": datetime.utcnow()
})

print("✅ Database initialized with test data.")
