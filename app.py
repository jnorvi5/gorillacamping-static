import os
import re
from datetime import datetime
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import check_password_hash
import requests

# --- Config & Secrets ---
SECRET_KEY = os.environ.get("SECRET_KEY")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")
MONGO_URI = os.environ.get("MONGO_URI")
MAILERLITE_API_KEY = os.environ.get("MAILERLITE_API_KEY")
AFFILIATE_ID = os.environ.get("AFFILIATE_ID", "")

assert SECRET_KEY, "❌ SECRET_KEY environment variable is not set!"
assert ADMIN_PASSWORD_HASH, "❌ ADMIN_PASSWORD_HASH environment variable is not set!"
assert MONGO_URI, "❌ MONGO_URI environment variable is not set!"

app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- Security Config ---
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600
)

@app.after_request
def security_headers(response):
    response.headers.update({
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://*.mailerlite.com https://www.googletagmanager.com https://www.google-analytics.com https://www.clarity.ms https://assets.mlcdn.com; "
            "connect-src 'self' https://*.mailerlite.com https://www.google-analytics.com https://www.clarity.ms https://l.clarity.ms; "
            "img-src 'self' data: https://*.mailerlite.com https://www.google-analytics.com https://www.googletagmanager.com https://www.clarity.ms; "
            "style-src 'self' 'unsafe-inline' https://*.mailerlite.com https://assets.mlcdn.com; "
            "font-src 'self' https://assets.mlcdn.com; "
            "frame-src 'self' https://*.mailerlite.com https://www.google.com;"
        ),
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY'
    })
    return response

# --- MongoDB Setup ---
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

try:
    client.admin.command("ping")
    print("✅ MongoDB connected successfully")
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    raise

db = client.get_database("gorillacamping")
emails = db.get_collection("subscribers")
posts = db.get_collection("posts")

# --- Indexes ---
emails.create_index("email", unique=True)
posts.create_index("slug", unique=True)

print("Database names:", client.list_database_names())
print("Collections in gorillacamping:", db.list_collection_names())

# --- Helper Functions ---
def add_to_mailerlite(email):
    """Add email to MailerLite with error handling and timeout"""
    try:
        if not MAILERLITE_API_KEY:
            print("❌ MAILERLITE_API_KEY environment variable missing!")
            return False

        headers = {
            "Authorization": f"Bearer {MAILERLITE_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "fields": {
                "source": "gorilla_camping"
            }
        }
        response = requests.post(
            "https://connect.mailerlite.com/api/subscribers",
            headers=headers,
            json=data,
            timeout=10
        )
        response.raise_for_status()
        response_data = response.json()
        if 'error' in response_data:
            print(f"⚠️ MailerLite API error: {response_data['error']}")
            return False
        print(f"✅ Successfully added {email} to MailerLite")
        return True
    except Exception as e:
        print(f"❌ MailerLite error: {e}")
        return False

def sanitize_slug(slug):
    slug = slug.lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    return slug

def affiliate_link(slug):
    if not AFFILIATE_ID:
        return None
    return f"https://affiliate-site.com/?id={AFFILIATE_ID}&ref={slug}"

# --- Blog Pagination Helper ---
def get_posts_paginated(page=1, per_page=10):
    skip = (page - 1) * per_page
    total = posts.count_documents({})
    cursor = posts.find().sort("created_at", -1).skip(skip).limit(per_page)
    return list(cursor), total

# --- Routes ---
@app.route("/pingdb")
def pingdb():
    try:
        client.admin.command("ping")
        return "MongoDB connected!", 200
    except Exception as e:
        return f"MongoDB connection failed: {e}", 500

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = (
            request.form.get("email")
            or (request.json.get("email") if request.is_json else None)
            or request.values.get("email")
        )
        if not email:
            return jsonify({"error": "No email provided"}), 400
        email = email.strip().lower()
        # Basic email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email format"}), 400
        try:
            emails.insert_one({
                "email": email,
                "timestamp": datetime.utcnow(),
                "source": "website-form"
            })
            add_to_mailerlite(email)
            return redirect(url_for("thank_you"))
        except Exception as e:
            print(f"Email insert error: {e}")
            return jsonify({"error": "Email submission failed"}), 500
    return render_template("index.html")

# Blog listing with pagination
@app.route("/blog")
def blog():
    page = int(request.args.get("page", 1))
    per_page = 10
    all_posts, total = get_posts_paginated(page, per_page)
    return render_template("blog.html", posts=all_posts, page=page, total=total, per_page=per_page)

# Individual blog post
@app.route("/blog/<slug>")
def blog_post(slug):
    post = posts.find_one({"slug": slug})
    if not post:
        return "404 Not Found", 404
    post["affiliate_link"] = affiliate_link(slug)
    return render_template("post.html", post=post)

# --- Admin: Add Post ---
@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Secure session-based login (using hashed password)
    if not session.get("logged_in"):
        if request.method == "POST":
            pw = request.form.get("password", "")
            if ADMIN_PASSWORD_HASH and check_password_hash(ADMIN_PASSWORD_HASH, pw):
                session["logged_in"] = True
                return redirect(url_for("admin"))
            else:
                flash("Wrong password!", "error")
        return render_template("admin_login.html")
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip() or title.lower().replace(" ", "-")
        slug = sanitize_slug(slug)
        if not slug:
            flash("Invalid slug.", "error")
            return render_template("admin_post.html")
        if posts.find_one({"slug": slug}):
            flash("Slug already exists!", "error")
            return render_template("admin_post.html")
        content = request.form.get("content", "").strip()
        tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
        meta_description = request.form.get("meta_description", "").strip()
        meta_keywords = [k.strip() for k in request.form.get("meta_keywords", "").split(",") if k.strip()]
        if not title or not content:
            flash("Title and Content required.", "error")
            return render_template("admin_post.html")
        post = {
            "title": title,
            "slug": slug,
            "content": content,
            "tags": tags,
            "meta_description": meta_description,
            "meta_keywords": meta_keywords,
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

# Paginated Debug Subscribers
@app.route("/debug-subscribers")
def debug_subscribers():
    page = int(request.args.get("page", 1))
    per_page = 25
    skip = (page - 1) * per_page
    docs = list(emails.find().skip(skip).limit(per_page))
    total = emails.count_documents({})
    return {
        "count": len(docs),
        "total": total,
        "page": page,
        "per_page": per_page,
        "docs": [str(doc) for doc in docs]
    }

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)
