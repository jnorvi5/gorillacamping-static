from pymongo import MongoClient
import os



# Make sure MONGO_URI is set in your environment before running this

client = MongoClient(os.environ["MONGO_URI"])
db = client["gorillacamping"]
subscribers = db["subscribers"]


print("Email Subscribers:")
for sub in subscribers.find():
    print(sub)



for sub in subscribers.find():
    print(sub)

