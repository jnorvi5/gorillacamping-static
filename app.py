from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

# 1. Load and validate your Mongo URI
MONGO_URI = os.environ.get("MONGO_URI")
print("🔑 MONGO_URI =", MONGO_URI)
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set")

# 2. Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client.get_database("gorillacamping")
emails = db.get_collection("subscribers")
posts = db.get_collection("posts")

# 3. Home route: GET shows form, POST captures email
@app.route("/", methods=["GET", "POST"])
def home():
    print("🔎 home() called with method:", request.method)
    if request.method == "POST":
        print("🔎 form data:", request.form)
        email = request.form.get("email")
        if email:
            print("📬 Capturing email:", email)
            emails.insert_one({
                "email": email,
                "timestamp": datetime.utcnow()
            })
            return redirect(url_for("home"))
    return render_template("index.html")

# 4. Blog listing
@app.route("/blog")
def blog():
    all_posts = posts.find().sort("created_at", -1)
    return render_template("blog.html", posts=all_posts)

# 5. Individual post by slug
@app.route("/blog/<slug>")
def blog_post(slug):
    post = posts.find_one({"slug": slug})
    if not post:
        return "404 Not Found", 404
    return render_template("post.html", post=post)

if __name__ == "__main__":
    app.run(debug=True)
