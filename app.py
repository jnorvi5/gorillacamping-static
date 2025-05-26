from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
from datetime import datetime
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devkey")  # Change for production!

from flask import Flask, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secure-fallback-key")

# Enhanced security config
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600
)

@app.after_request
def security_headers(response):
    response.headers.update({
        'Content-Security-Policy': "default-src 'self' https://*.mailerlite.com",
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY'
    })
    return response




def add_to_mailerlite(email):
    """Add email to MailerLite with proper error handling and timeout"""
    try:
        api_key = os.environ.get("MAILERLITE_API_KEY")
        if not api_key:
            print("❌ MAILERLITE_API_KEY environment variable missing!")
            return False

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "fields": {
                "source": "gorilla_camping"
            }
        }

        # Add timeout and better error handling
        response = requests.post(
            "https://connect.mailerlite.com/api/subscribers",
            headers=headers,
            json=data,
            timeout=10  # 10 seconds for connection and read
        )

        # This will raise for 4xx/5xx status codes
        response.raise_for_status()

        # Check for MailerLite-specific errors in successful response
        response_data = response.json()
        if 'error' in response_data:
            print(f"⚠️ MailerLite API error: {response_data['error']}")
            return False

        print(f"✅ Successfully added {email} to MailerLite")
        return True

    except requests.exceptions.HTTPError as http_err:
        # Get detailed error message from response
        error_msg = response.text if response else str(http_err)
        print(f"❌ HTTP error ({response.status_code}): {error_msg}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Network connection error - check internet/MailerLite status")
    
    except requests.exceptions.Timeout:
        print("❌ Request timed out - MailerLite API not responding")
    
    except requests.exceptions.RequestException as err:
        print(f"❌ Unexpected error: {str(err)}")
    
    except json.JSONDecodeError:
        print("❌ Invalid JSON response from MailerLite API")

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

# ... [keep all your imports and setup]

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = (
            request.form.get("email")
            or (request.json.get("email") if request.is_json else None)
            or request.values.get("email")
        )
        if not email:
            print("No email provided!")
            return jsonify({"error": "No email provided"}), 400

        email = email.strip().lower()
        try:
            # Save to MongoDB
            emails.insert_one({
                "email": email,
                "timestamp": datetime.utcnow(),
                "source": "website-form"
            })
            
            # Add to MailerLite
            add_to_mailerlite(email)  # NOW ACTIVE
            
            flash("Thanks for subscribing!", "success")
        except Exception as e:
            print(f"❌ FATAL ERROR: {str(e)}")
            flash("Submission failed - try again", "error")
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

