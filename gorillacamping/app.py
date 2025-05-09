from flask import Flask, render_template
from pymongo import MongoClient
import os
from datetime import datetime

app = Flask(__name__)
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database("gorillacamping")
posts_collection = db.get_collection("posts")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/blog")
def blog():
    posts = posts_collection.find().sort("created_at", -1)
    return render_template("blog.html", posts=posts)

@app.route("/blog/<slug>")
def blog_post(slug):
    post = posts_collection.find_one({"slug": slug})
    if post:
        return render_template("post.html", post=post)
    return "404 Not Found", 404

if __name__ == "__main__":
    app.run(debug=True)