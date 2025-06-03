import os
import re
import random
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session, Response
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import check_password_hash
import requests
from urllib.parse import urlparse

# --- Config & Secrets ---
SECRET_KEY = os.environ.get("SECRET_KEY")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")
MONGO_URI = os.environ.get("MONGO_URI")
MAILERLITE_API_KEY = os.environ.get("MAILERLITE_API_KEY")
AFFILIATE_ID = os.environ.get("AFFILIATE_ID", "gorillacamping")

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
            "script-src 'self' 'unsafe-inline' https://*.mailerlite.com https://www.googletagmanager.com https://www.google-analytics.com https://www.clarity.ms https://assets.mlcdn.com https://affiliate-program.amazon.com https://*.amazon.com; "
            "connect-src 'self' https://*.mailerlite.com https://www.google-analytics.com https://analytics.google.com https://www.clarity.ms https://l.clarity.ms; "
            "img-src 'self' data: https://*.mailerlite.com https://www.google-analytics.com https://www.googletagmanager.com https://www.clarity.ms https://*.amazon.com https://m.media-amazon.com; "
            "style-src 'self' 'unsafe-inline' https://*.mailerlite.com https://assets.mlcdn.com; "
            "font-src 'self' https://assets.mlcdn.com; "
            "frame-src 'self' https://*.mailerlite.com https://www.google.com;"
        ),
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY'
    })
    return response

# --- MongoDB Setup with Error Handling ---
client = None
db = None
emails = None
posts = None
clicks = None

def init_mongodb():
    global client, db, emails, posts, clicks
    try:
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("✅ MongoDB connected successfully")
        
        db = client.get_database("gorillacamping")
        emails = db.get_collection("subscribers")
        posts = db.get_collection("posts")
        clicks = db.get_collection("affiliate_clicks")
        
        # Create indexes
        try:
            emails.create_index("email", unique=True)
            posts.create_index("slug", unique=True)
            clicks.create_index([("timestamp", -1), ("affiliate_url", 1)])
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
            
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("⚠️ App will run in limited mode without database")
        return False

# Try to connect to MongoDB
mongodb_connected = init_mongodb()

# Helper function to safely use database
def safe_db_operation(operation, fallback_result=None):
    if not mongodb_connected or db is None:
        print("⚠️ Database not available, using fallback")
        return fallback_result
    try:
        return operation()
    except Exception as e:
        print(f"❌ Database operation failed: {e}")
        return fallback_result

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
                "source": "gorilla_camping_guerilla_marketing"
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

def track_affiliate_click(affiliate_url, referrer_page=None):
    """Track affiliate link clicks for analytics"""
    def _track():
        clicks.insert_one({
            "type": "affiliate_click",
            "affiliate_url": affiliate_url,
            "timestamp": datetime.utcnow(),
            "ip": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', ''),
            "referrer_page": referrer_page,
            "affiliate_id": AFFILIATE_ID
        })
        return True
    
    safe_db_operation(_track, False)

def track_social_click(platform, action=None):
    """Track social media clicks for analytics"""
    def _track():
        clicks.insert_one({
            "type": "social_click",
            "platform": platform,
            "action": action,
            "timestamp": datetime.utcnow(),
            "ip": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', ''),
            "referrer": request.referrer
        })
        return True
    
    safe_db_operation(_track, False)

# --- Blog Pagination Helper ---
def get_posts_paginated(page=1, per_page=10):
    def _get_posts():
        skip = (page - 1) * per_page
        total = posts.count_documents({})
        cursor = posts.find().sort("created_at", -1).skip(skip).limit(per_page)
        return list(cursor), total
    
    return safe_db_operation(_get_posts, ([], 0))

# --- Routes ---
@app.route("/pingdb")
def pingdb():
    if not mongodb_connected:
        return "❌ MongoDB not connected", 500
    try:
        client.admin.command("ping")
        return "✅ MongoDB connected!", 200
    except Exception as e:
        return f"❌ MongoDB connection failed: {e}", 500

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
        
        # Enhanced email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Try to save to database, but don't fail if it's down
        def save_email():
            emails.insert_one({
                "email": email,
                "timestamp": datetime.utcnow(),
                "source": "guerilla-homepage-form",
                "ip": request.remote_addr
            })
            return True
            
        saved = safe_db_operation(save_email, False)
        
        # Always try MailerLite (more important for revenue)
        mailerlite_success = add_to_mailerlite(email)
        
        if saved and mailerlite_success:
            flash("✅ Subscribed successfully!", "success")
        elif mailerlite_success:
            flash("✅ Subscribed to email list!", "success")
        else:
            flash("⚠️ Subscription may have failed. Please try again.", "error")
            
        return redirect(url_for("thank_you"))
    
    # Get latest blog posts for homepage (or empty list if database is down)
    latest_posts = safe_db_operation(
        lambda: list(posts.find().sort("created_at", -1).limit(3)),
        []
    )
    return render_template("index.html", latest_posts=latest_posts)

# Blog listing with pagination and SEO
@app.route("/blog")
def blog():
    page = int(request.args.get("page", 1))
    per_page = 12
    all_posts, total = get_posts_paginated(page, per_page)
    
    # SEO meta data
    meta_description = "Guerilla-style camping guides, gear reviews, and off-grid living tips. Real advice from someone living the lifestyle."
    meta_keywords = "guerilla camping, off-grid living, camping gear reviews, budget camping, DIY camping, veteran camping"
    
    return render_template("blog.html", 
                         posts=all_posts, 
                         page=page, 
                         total=total, 
                         per_page=per_page,
                         meta_description=meta_description,
                         meta_keywords=meta_keywords)

@app.route("/
