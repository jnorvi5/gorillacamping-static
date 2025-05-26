from pymongo import MongoClient
import os

client = MongoClient(os.environ["MONGO_URI"])
db = client["gorillacamping"]
subscribers = db["subscribers"]

print("Email Subscribers:")
for sub in subscribers.find():
    print(sub)


