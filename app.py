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

# --- REMOVE THESE LINES - They'll crash if database is down ---
# emails.create_index("email", unique=True)  # DELETE THIS
# posts.create_index("slug", unique=True)    # DELETE THIS
# clicks.create_index([("timestamp", -1), ("affiliate_url", 1)])  # DELETE THIS
# print("Database names:", client.list_database_names())  # DELETE THIS
# print("Collections in gorillacamping:", db.list_collection_names())  # DELETE THIS

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
            "affiliate_url": affiliate_url,
            "timestamp": datetime.utcnow(),
            "ip": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', ''),
            "referrer_page": referrer_page,
            "affiliate_id": AFFILIATE_ID
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

@app.route("/blog/<slug>")
def blog_post(slug):
    post = safe_db_operation(lambda: posts.find_one({"slug": slug}), None)
    if not post:
        return "404 Not Found", 404
    
    # Get 3 random related posts
    def get_related():
        all_slugs = [p["slug"] for p in posts.find({"slug": {"$ne": slug}})]
        related_slugs = random.sample(all_slugs, min(3, len(all_slugs)))
        return list(posts.find({"slug": {"$in": related_slugs}}))
    
    related_posts = safe_db_operation(get_related, [])
    
    return render_template("post.html", post=post, related_posts=related_posts)

# Affiliate link tracking
@app.route("/go/<path:encoded_url>")
def affiliate_redirect(encoded_url):
    try:
        # Simple base64-like encoding for affiliate URLs
        import base64
        affiliate_url = base64.b64decode(encoded_url.encode()).decode()
        
        # Track the click
        referrer = request.referrer or "direct"
        track_affiliate_click(affiliate_url, referrer)
        
        return redirect(affiliate_url)
    except Exception as e:
        print(f"Affiliate redirect error: {e}")
        return redirect(url_for("gear"))

# --- Admin: Add Post ---
@app.route("/admin", methods=["GET", "POST"])
def admin():
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
        if not mongodb_connected:
            flash("❌ Database not available - cannot publish posts", "error")
            return render_template("admin_post.html")
            
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip() or title.lower().replace(" ", "-")
        slug = sanitize_slug(slug)
        
        if not slug:
            flash("Invalid slug.", "error")
            return render_template("admin_post.html")
        
        if safe_db_operation(lambda: posts.find_one({"slug": slug}), None):
            flash("Slug already exists!", "error")
            return render_template("admin_post.html")
        
        content = request.form.get("content", "").strip()
        tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
        meta_description = request.form.get("meta_description", "").strip()
        meta_keywords = [k.strip() for k in request.form.get("meta_keywords", "").split(",") if k.strip()]
        
        if not title or not content:
            flash("Title and Content required.", "error")
            return render_template("admin_post.html")
        
        # Auto-generate meta description if not provided
        if not meta_description:
            meta_description = content[:160].replace('<', '').replace('>', '') + "..."
        
        post = {
            "title": title,
            "slug": slug,
            "content": content,
            "tags": tags,
            "meta_description": meta_description,
            "meta_keywords": meta_keywords,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "author": "Gorilla Camping"
        }
        
        def save_post():
            posts.insert_one(post)
            return True
            
        if safe_db_operation(save_post, False):
            flash("✅ Post published!", "success")
            return redirect(url_for("blog_post", slug=slug))
        else:
            flash("❌ Failed to publish post - database error", "error")
    
    return render_template("admin_post.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("Logged out.", "info")
    return redirect(url_for("admin"))

# Analytics Dashboard (Admin only)
@app.route("/analytics")
def analytics():
    if not session.get("logged_in"):
        return redirect(url_for("admin"))
    
    if not mongodb_connected:
        return render_template("analytics.html", 
                             total_subscribers=0,
                             total_posts=0,
                             total_clicks=0,
                             recent_clicks=[],
                             error="Database not available")
    
    # Get basic stats
    total_subscribers = safe_db_operation(lambda: emails.count_documents({}), 0)
    total_posts = safe_db_operation(lambda: posts.count_documents({}), 0)
    total_clicks = safe_db_operation(lambda: clicks.count_documents({}), 0)
    
    # Recent clicks
    recent_clicks = safe_db_operation(
        lambda: list(clicks.find().sort("timestamp", -1).limit(10)),
        []
    )
    
    return render_template("analytics.html", 
                         total_subscribers=total_subscribers,
                         total_posts=total_posts,
                         total_clicks=total_clicks,
                         recent_clicks=recent_clicks)

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    pages = []
    
    # Static pages
    pages.append(['/', datetime.now().date().isoformat()])
    pages.append(['/blog', datetime.now().date().isoformat()])
    pages.append(['/gear', datetime.now().date().isoformat()])
    pages.append(['/about', datetime.now().date().isoformat()])
    pages.append(['/contact', datetime.now().date().isoformat()])
    
    # Blog posts (only if database is available)
    def add_blog_posts():
        for post in posts.find():
            url = f"/blog/{post['slug']}"
            lastmod = post.get('updated_at', post.get('created_at', datetime.now())).date().isoformat()
            pages.append([url, lastmod])
    
    safe_db_operation(add_blog_posts, None)
    
    sitemap_xml = render_template('sitemap_template.xml', pages=pages)
    return Response(sitemap_xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    return Response("""User-agent: *
Allow: /
Disallow: /admin
Disallow: /analytics
Disallow: /debug-subscribers

Sitemap: https://gorillacamping.site/sitemap.xml
""", mimetype='text/plain')

# --- Static Pages with SEO ---
@app.route("/about")
def about():
    meta_description = "Jon's story: From Army vet to off-grid guerilla camper. Building a tribe of like-minded adventurers who live life on their own terms."
    meta_keywords = "gorilla camping founder, army veteran camping, off-grid lifestyle, guerilla camping story"
    return render_template("about.html", meta_description=meta_description, meta_keywords=meta_keywords)

@app.route("/contact")
def contact():
    meta_description = "Contact Gorilla Camping for collaborations, gear questions, or to join our guerilla camping community."
    meta_keywords = "gorilla camping contact, guerilla camping community, camping collaboration"
    return render_template("contact.html", meta_description=meta_description, meta_keywords=meta_keywords)

@app.route("/gear")
def gear():
    meta_description = "Hand-picked camping gear by Gorilla Camping. Budget-friendly, tested gear for guerilla-style outdoor adventures."
    meta_keywords = "camping gear reviews, budget camping gear, guerilla camping equipment, affiliate camping gear"
    return render_template("gear.html", meta_description=meta_description, meta_keywords=meta_keywords)

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)
