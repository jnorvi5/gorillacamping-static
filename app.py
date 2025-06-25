import os
import re
import random
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session, Response
from flask_compress import Compress
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs
import traceback

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'guerilla-camping-secret-2024')

# Enable GZIP compression on responses
Compress(app)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600

try:
    mongodb_uri = os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URI')
    if mongodb_uri:
        client = MongoClient(mongodb_uri)
        db = client.get_default_database()
        db.command('ping')
        print("✅ MongoDB connected successfully!")
    else:
        print("⚠️ No MongoDB URI found - running in demo mode")
        db = None
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None

with app.app_context():
    if db:
        try:
            db.posts.create_index([("slug", 1)], unique=True)
            db.posts.create_index([("status", 1)])
            db.contacts.create_index([("email", 1)])
            db.affiliate_clicks.create_index([("product_id", 1)])
            db.clicks.create_index([("source", 1)])
            db.subscribers.create_index([("email", 1)], unique=True)
            print("✅ MongoDB indexes created/verified!")
        except Exception as ex:
            print(f"⚠️ Could not create indexes: {ex}")

@app.after_request
def security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    if request.endpoint in ['static', 'sitemap', 'robots']:
        response.headers['Cache-Control'] = 'public, max-age=86400'
    return response

def safe_db_operation(operation, default_return=None):
    try:
        if db is not None:
            return operation()
        else:
            return default_return
    except Exception as e:
        print(f"Database operation failed: {e}")
        return default_return

def track_click(source, destination, user_agent=None, referrer=None):
    def save_click():
        click_data = {
            "source": source,
            "destination": destination,
            "timestamp": datetime.utcnow(),
            "user_agent": user_agent,
            "referrer": referrer,
            "ip_address": request.remote_addr
        }
        db.clicks.insert_one(click_data)
        return True
    
    return safe_db_operation(save_click, False)

def get_recent_posts(limit=5):
    def fetch_posts():
        return list(db.posts.find({"status": "published"}).sort("date", -1).limit(limit))
    
    posts = safe_db_operation(fetch_posts, [])
    
    if not posts:
        posts = [
            {
                "title": "Best Budget Camping Gear Under $20",
                "slug": "budget-camping-gear-under-20",
                "excerpt": "Military surplus secrets + Amazon deals for under $50.",
                "date": datetime.now() - timedelta(days=1),
                "category": "Budget Gear",
                "affiliate_ready": True
            },
            {
                "title": "Stealth Camping Essentials",
                "slug": "stealth-camping-essentials",
                "excerpt": "5 items for invisible urban camping.",
                "date": datetime.now() - timedelta(days=3),
                "category": "Stealth Tactics",
                "affiliate_ready": True
            }
        ]
    
    return posts

def get_posts_paginated(page=1, per_page=12):
    def fetch_paginated():
        skip = (page - 1) * per_page
        posts_list = list(db.posts.find({"status": "published"}).sort("date", -1).skip(skip).limit(per_page))
        total = db.posts.count_documents({"status": "published"})
        return posts_list, total
    
    return safe_db_operation(fetch_paginated, ([], 0))

@app.route("/")
def index():
    latest_posts = get_recent_posts(6)
    meta_description = "Camping gear reviews, budget outdoor equipment, and off-grid survival tips."
    meta_keywords = "camping, stealth camping, off-grid"
    track_click("homepage", "internal", request.headers.get('User-Agent'), request.referrer)
    return render_template("index.html",
                           latest_posts=latest_posts,
                           meta_description=meta_description,
                           meta_keywords=meta_keywords,
                           page_type="homepage")

@app.route("/blog")
def blog():
    page = int(request.args.get("page", 1))
    per_page = 12
    all_posts, total = get_posts_paginated(page, per_page)
    meta_description = "Guerilla camping guides, gear reviews, and survival tips."
    meta_keywords = "blog, camping tips, gear reviews"
    return render_template("blog.html",
                           posts=all_posts,
                           page=page,
                           total=total,
                           per_page=per_page,
                           meta_description=meta_description,
                           meta_keywords=meta_keywords,
                           page_type="blog")

@app.route("/blog/<slug>")
def post(slug):
    def fetch_post():
        return db.posts.find_one({"slug": slug, "status": "published"})
    
    post_data = safe_db_operation(fetch_post)
    if not post_data:
        post_data = {
            "title": "Post Not Found",
            "content": "This post doesn't exist or hasn't been published yet.",
            "date": datetime.now(),
            "category": "Misc"
        }
    track_click(f"post_{slug}", "internal", request.headers.get('User-Agent'), request.referrer)
    return render_template("post.html",
                           post=post_data,
                           meta_description=post_data.get('meta_description', ''),
                           meta_keywords=post_data.get('meta_keywords', ''),
                           page_type="article")

@app.route("/about")
def about():
    return render_template("about.html", page_type="about")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            subject = request.form.get("subject", "").strip()
            message = request.form.get("message", "").strip()
            
            if not all([name, email, subject, message]):
                flash("All fields are required!", "error")
                return redirect(url_for("contact"))
            
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                flash("Please enter a valid email address.", "error")
                return redirect(url_for("contact"))
            
            def save_contact():
                return db.contacts.insert_one({
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message,
                    "timestamp": datetime.utcnow()
                })
            
            safe_db_operation(save_contact)
            flash("Message sent successfully!", "success")
            return redirect(url_for("contact"))
        except Exception as e:
            print(f"Contact form error: {e}")
            flash("An error occurred. Please try again.", "error")
            return redirect(url_for("contact"))
    return render_template("contact.html", page_type="contact")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
