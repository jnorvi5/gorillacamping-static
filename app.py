import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devkey")  # Change for production!

# ---- MailerLite Integration ----
def add_to_mailerlite(email):
    api_key = os.environ.get("MAILERLITE_API_KEY")
    if not api_key:
        print("MailerLite API key missing!")
        return False
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "email": email
    }
    url = "https://connect.mailerlite.com/api/subscribers"
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in (200, 201):
        print("Added to MailerLite!")
        return True
    else:
        print("MailerLite error:", response.text)
        return False

# ---- MongoDB Setup ----
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI environment variable is not set!")

client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

# Confirm MongoDB connection
try:
    client.admin.command("ping")
    print("✅ MongoDB connected successfully")
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    raise

db = client.get_database("gorillacamping")
emails = db.get_collection("subscribers")
posts = db.get_collection("posts")

print("Database names:", client.list_database_names())
print("Collections in gorillacamping:", db.list_collection_names())

# --- Admin Auth ---
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")  # Set in your env

# --- Routes ---

@app.route("/pingdb")
def pingdb():
    try:
        client.admin.command("ping")
        return "MongoDB connected!", 200
    except Exception as e:
        return f"MongoDB connection failed: {e}", 500

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
            add_to_mailerlite(email)
            flash("Thanks for subscribing!", "success")
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

# --- Admin: Add Post ---
@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Simple session-based login
    if not session.get("logged_in"):
        if request.method == "POST":
            pw = request.form.get("password", "")
            if pw == ADMIN_PASSWORD:
                session["logged_in"] = True
                return redirect(url_for("admin"))
            else:
                flash("Wrong password!", "error")
        return render_template("admin_login.html")
    
    # If logged in, show post form and handle submission
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip() or title.lower().replace(" ", "-")
        content = request.form.get("content", "").strip()
        tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
        if not title or not content:
            flash("Title and Content required.", "error")
            return render_template("admin_post.html")
        post = {
            "title": title,
            "slug": slug,
            "content": content,
            "tags": tags,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        posts.insert_one(post)
        flash("✅ Post published!", "success")
        return redirect(url_for("blog_post", slug=slug))
    return render_template("admin_post.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("Logged out.", "info")
    return redirect(url_for("admin"))
@app.route("/debug-subscribers")
def debug_subscribers():
    docs = list(db.subscribers.find())
    return {"count": len(docs), "docs": [str(doc) for doc in docs]}

if __name__ == "__main__":
    app.run(debug=True)

