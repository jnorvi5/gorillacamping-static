import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

app = Flask(__name__)

# Load MongoDB connection string from environment variable
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI environment variable is not set!")

# Connect to MongoDB with URI
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

# Confirm MongoDB connection
try:
    client.admin.command("ping")
    print("✅ MongoDB connected successfully")
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    raise

# Database setup
db = client.get_database("gorillacamping")
emails = db.get_collection("subscribers")
posts = db.get_collection("posts")

# Home route: handle newsletter form
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form.get("email")
        if email:
            emails.insert_one({
                "email": email,
                "timestamp": datetime.utcnow()
            })
            return redirect(url_for("home"))
    return render_template("index.html")

# Blog listing
@app.route("/blog")
def blog():
    all_posts = posts.find().sort("created_at", -1)
    return render_template("blog.html", posts=all_posts)

# Individual blog post
@app.route("/blog/<slug>")
def blog_post(slug):
    post = posts.find_one({"slug": slug})
    if not post:
        return "404 Not Found", 404
    return render_template("post.html", post=post)

if __name__ == "__main__":
    app.run(debug=True)
