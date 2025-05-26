from pymongo import MongoClient
import os

<<<<<<< HEAD
=======
# Make sure MONGO_URI is set in your environment before running this
>>>>>>> 30df87ff0fb1d411f4b547104854a6bcabb6f668
client = MongoClient(os.environ["MONGO_URI"])
db = client["gorillacamping"]
subscribers = db["subscribers"]

<<<<<<< HEAD
print("Email Subscribers:")
for sub in subscribers.find():
    print(sub)


=======
for sub in subscribers.find():
    print(sub)
>>>>>>> 30df87ff0fb1d411f4b547104854a6bcabb6f668
