import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("Set your MONGO_URI env variable.")

client = MongoClient(MONGO_URI)
db = client["gorillacamping"]
gear = db["gear"]

# Example items (add as many as you want!)
items = [
    {
        "name": "Jackery Explorer 240 Solar Generator",
        "affiliate_id": "jackery-explorer-240",
        "price": "$199.99",
        "image": "https://m.media-amazon.com/images/I/41XePYWYlAL._AC_US300_.jpg",
        "description": "Solar generator that powers all my content gear for a week.",
        "badges": ["LIMITED TIME", "CONTENT KING"],
        "specs": ["240Wh Capacity", "Powers Laptop 8hrs", "Content Creation Ready"],
        "old_price": "$299.99",
        "savings": "SAVE $100!",
        "rating": 5,
        "why_recommend": "Made me $2,847 from one viral video",
        "order": 1,
        "active": True
    },
    {
        "name": "Coleman Classic Propane Stove",
        "affiliate_id": "coleman-stove",
        "price": "$49.99",
        "image": "https://m.media-amazon.com/images/I/71vA6lQyFPL._AC_SY355_.jpg",
        "description": "Cooked 100+ meals on this stove - reliable everywhere.",
        "badges": ["BUDGET PICK"],
        "specs": ["2 Burners", "20,000 BTU", "under $50"],
        "old_price": "$59.99",
        "savings": "SAVE $10!",
        "rating": 4,
        "why_recommend": "It's ugly, but it works every time.",
        "order": 2,
        "active": True
    },
    # ...add more gear items here
]

for item in items:
    gear.update_one({"affiliate_id": item["affiliate_id"]}, {"$set": item}, upsert=True)

print("✅ Gear inserted/updated!")
