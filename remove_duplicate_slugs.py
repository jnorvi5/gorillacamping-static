                                                             from pymongo import MongoClient

# Replace with your actual MongoDB URI
MONGO_URI = "mongodb+srv://jnorvi5:gorillaSecure2025@cluster0.c0gofgp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "gorillacamping"
COLLECTION_NAME = "posts"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

print("Finding duplicate slugs in posts...")

pipeline = [
    {"$group": {"_id": "$slug", "count": {"$sum": 1}, "ids": {"$push": "$_id"}}},
    {"$match": {"count": {"$gt": 1}}}
]
duplicates = list(collection.aggregate(pipeline))

if not duplicates:
    print("✅ No duplicate slugs found. You're ready to redeploy!")
else:
    print(f"Found {len(duplicates)} slugs with duplicates. Removing extras...")
    for dup in duplicates:
        # Keep the first ID, remove the rest
        ids_to_remove = dup["ids"][1:]
        result = collection.delete_many({"_id": {"$in": ids_to_remove}})
        print(f"Removed {result.deleted_count} duplicate(s) for slug: {dup['_id']}")

    print("✅ All duplicates removed. You're ready to redeploy!")

client.close()
