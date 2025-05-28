from pymongo import MongoClient

# Replace with your actual MongoDB URI!
MONGO_URI = "your-mongodb-connection-string"
DB_NAME = "gorillacamping"
COLLECTION_NAME = "subscribers"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

print("Finding duplicate emails...")

# Step 1: Find duplicates (emails that appear more than once)
pipeline = [
    {"$group": {"_id": "$email", "count": {"$sum": 1}, "ids": {"$push": "$_id"}}},
    {"$match": {"count": {"$gt": 1}}}
]
duplicates = list(collection.aggregate(pipeline))

if not duplicates:
    print("✅ No duplicate emails found. You're ready to redeploy!")
else:
    print(f"Found {len(duplicates)} emails with duplicates. Removing extras...")
    for dup in duplicates:
        # Keep the first ID, remove the rest
        ids_to_remove = dup["ids"][1:]
        result = collection.delete_many({"_id": {"$in": ids_to_remove}})
        print(f"Removed {result.deleted_count} duplicate(s) for {dup['_id']}")

    print("✅ All duplicates removed. You're ready to redeploy!")

client.close()
