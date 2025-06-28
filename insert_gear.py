import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI")  # Or hardcode your URI
client = MongoClient(MONGO_URI)
db = client["gorillacamping"]
gear = db["gear"]

items = [
    {
        "name": "Leatherman Wave+ Multitool",
        "affiliate_id": "leatherman-wave",
        "price": "$99.99",
        "image": "https://m.media-amazon.com/images/I/61lKQ5J2yTL._AC_SY355_.jpg",
        "description": "My EDC for everything from food to repairs.",
        "badges": ["BESTSELLER", "MULTITOOL KING"],
        "specs": ["17 tools", "Stainless Steel"],
        "old_price": "$119.99",
        "savings": "SAVE $20!",
        "rating": 5,
        "why_recommend": "Never broke one. Saved my bacon many times.",
        "order": 4,
        "active": True
    },
    # ... Add more items here
]

for item in items:
    gear.update_one({"affiliate_id": item["affiliate_id"]}, {"$set": item}, upsert=True)

print("✅ Gear inserted/updated!")
