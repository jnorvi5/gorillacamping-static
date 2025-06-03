import os
import re
import random
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session, Response
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs
import traceback

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'guerilla-camping-secret-2024')

# MongoDB connection with error handling
try:
    mongodb_uri = os.environ.get('MONGODB_URI')
    if mongodb_uri:
        client = MongoClient(mongodb_uri)
        db = client.get_default_database()
        # Test connection
        db.command('ping')
        print("✅ MongoDB connected successfully!")
    else:
        print("⚠️ No MongoDB URI found - running in demo mode")
        db = None
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None

# Guerilla security headers for maximum SEO/trust
@app.after_request
def security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Safe database operations (guerilla-style error handling)
def safe_db_operation(operation, default_return=None):
    try:
        if db is not None:
            return operation()
        else:
            return default_return
    except Exception as e:
        print(f"Database operation failed: {e}")
        return default_return

# Get recent posts with error handling
def get_recent_posts(limit=5):
    def fetch_posts():
        return list(db.posts.find({"status": "published"}).sort("date", -1).limit(limit))
    
    posts = safe_db_operation(fetch_posts, [])
    
    # Fallback demo posts if database is unavailable
    if not posts:
        posts = [
            {
                "title": "Guerilla Camping Setup: $50 Budget Challenge",
                "slug": "guerilla-camping-50-budget",
                "excerpt": "How to set up a complete guerilla camping kit for under $50. Military surplus secrets revealed!",
                "date": datetime.now() - timedelta(days=1),
                "category": "Budget Gear"
            },
            {
                "title": "Stealth Camping in Urban Areas: Legal & Safe",
                "slug": "stealth-camping-urban-guide",
                "excerpt": "Master the art of urban stealth camping without breaking laws or getting caught.",
                "date": datetime.now() - timedelta(days=3),
                "category": "Stealth Tactics"
            }
        ]
    
    return posts

# Get paginated posts
def get_posts_paginated(page=1, per_page=12):
    def fetch_paginated():
        skip = (page - 1) * per_page
        posts = list(db.posts.find({"status": "published"})
                    .sort("date", -1)
                    .skip(skip)
                    .limit(per_page))
        total = db.posts.count_documents({"status": "published"})
        return posts, total
    
    result = safe_db_operation(fetch_paginated, ([], 0))
    return result

# Track affiliate clicks and sources
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

# Home page with latest posts
@app.route("/")
def index():
    latest_posts = get_recent_posts(6)
    
    # SEO meta data
    meta_description = "Guerilla-style camping guides, budget gear reviews, and off-grid survival tips. Real advice from someone living the lifestyle."
    meta_keywords = "guerilla camping, budget camping, stealth camping, off-grid living, camping gear reviews"
    
    return render_template("index.html", 
                         latest_posts=latest_posts,
                         meta_description=meta_description,
                         meta_keywords=meta_keywords)

# Blog listing with pagination and SEO
@app.route("/blog")
def blog():
    page = int(request.args.get("page", 1))
    per_page = 12
    all_posts, total = get_posts_paginated(page, per_page)
    
    meta_description = "Guerilla-style camping guides, gear reviews, and off-grid living tips. Real advice from someone living the lifestyle."
    meta_keywords = "guerilla camping, off-grid living, camping gear reviews, budget camping, DIY camping"
    
    return render_template("blog.html", 
                         posts=all_posts, 
                         page=page, 
                         total=total, 
                         per_page=per_page,
                         meta_description=meta_description,
                         meta_keywords=meta_keywords)

# Individual blog post
@app.route("/blog/<slug>")
def post(slug):
    def fetch_post():
        return db.posts.find_one({"slug": slug, "status": "published"})
    
    post_data = safe_db_operation(fetch_post)
    
    if not post_data:
        # Demo post for testing
        post_data = {
            "title": "Guerilla Camping Setup: $50 Budget Challenge",
            "content": "Coming soon! This post will show you how to build a complete guerilla camping setup for under $50 using military surplus and DIY hacks.",
            "date": datetime.now(),
            "category": "Budget Gear",
            "slug": slug
        }
    
    return render_template("post.html", 
                         post=post_data,
                         meta_description=post_data.get('excerpt', 'Guerilla camping tips and tricks'),
                         meta_keywords=f"guerilla camping, {post_data.get('category', 'camping')}")

# Gear page with affiliate products
@app.route("/gear")
def gear():
    # Track page visit
    track_click("gear_page", "internal", request.headers.get('User-Agent'), request.referrer)
    
    meta_description = "Guerilla-approved camping gear that won't break the bank. Real reviews from someone who lives this lifestyle."
    meta_keywords = "budget camping gear, guerilla camping equipment, cheap camping gear, military surplus camping"
    
    return render_template("gear.html",
                         meta_description=meta_description,
                         meta_keywords=meta_keywords)

# About page
@app.route("/about")
def about():
    meta_description = "Meet the guerilla camper behind the blog. Real stories, real gear, real advice from someone living off-grid."
    meta_keywords = "about guerilla camping, off-grid lifestyle, camping blog author"
    
    return render_template("about.html",
                         meta_description=meta_description,
                         meta_keywords=meta_keywords)

# Contact form - Revenue generating lead capture
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        try:
            # Get form data with error handling
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            subject = request.form.get("subject", "").strip()
            message = request.form.get("message", "").strip()
            
            # Basic validation
            if not all([name, email, subject, message]):
                flash("All fields are required! Don't leave money on the table.", "error")
                return redirect(url_for("contact"))
            
            # Email validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                flash("Please enter a valid email address.", "error")
                return redirect(url_for("contact"))
            
            # Save to database with error handling
            def save_contact():
                contact_data = {
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message,
                    "timestamp": datetime.utcnow(),
                    "status": "new",
                    "ip_address": request.remote_addr,
                    "user_agent": request.headers.get('User-Agent', 'Unknown')
                }
                db.contacts.insert_one(contact_data)
                return True
            
            contact_saved = safe_db_operation(save_contact, False)
            
            # Success message with revenue focus
            success_messages = [
                "Message sent! I'll get back to you guerilla-fast! 🚀",
                "Got it! Expect a response within 24 hours. Let's make money! 💰",
                "Message received! Time to turn this into revenue! 🏕️"
            ]
            flash(random.choice(success_messages), "success")
            return redirect(url_for("contact"))
            
        except Exception as e:
            print(f"Contact form error: {e}")
            flash("Oops! Something went wrong. Try again - don't let tech stop the money!", "error")
            return redirect(url_for("contact"))
    
    # GET request - show the form
    meta_description = "Contact Gorilla Camping for gear reviews, brand collaborations, and guerilla camping advice. Let's make money together!"
    meta_keywords = "contact gorilla camping, brand collaboration, gear review, affiliate partnership, camping blog"
    
    return render_template("contact.html", 
                         meta_description=meta_description,
                         meta_keywords=meta_keywords)

# AS-IS terms and affiliate disclaimer page
@app.route("/as-is")
def as_is():
    meta_description = "Gorilla Camping affiliate marketing disclaimer, terms of use, and product recommendations policy. Guerilla-style transparency."
    meta_keywords = "affiliate disclaimer, as-is terms, gorilla camping legal, product reviews disclaimer"
    
    return render_template("as_is.html",
                         meta_description=meta_description,
                         meta_keywords=meta_keywords)

# Privacy policy
@app.route("/privacy")
def privacy():
    meta_description = "Gorilla Camping privacy policy. How we protect your data while helping you master guerilla camping."
    meta_keywords = "privacy policy, data protection, gorilla camping privacy"
    
    return render_template("privacy.html",
                         meta_description=meta_description,
                         meta_keywords=meta_keywords)

# Affiliate link tracker
@app.route("/go/<product_id>")
def affiliate_redirect(product_id):
    # Track the click
    track_click(f"affiliate_{product_id}", "external", request.headers.get('User-Agent'), request.referrer)
    
    # Affiliate links mapping (add your real affiliate links here)
    affiliate_links = {
        "tent": "https://amzn.to/your-tent-link",
        "sleeping-bag": "https://amzn.to/your-sleeping-bag-link",
        "backpack": "https://amzn.to/your-backpack-link",
        "gear-kit": "https://amzn.to/your-gear-kit-link"
    }
    
    # Get the destination URL
    destination = affiliate_links.get(product_id, "https://amazon.com")
    
    return redirect(destination)

# Social media redirects with tracking
@app.route("/social/<platform>")
def social_redirect(platform):
    track_click(f"social_{platform}", "external", request.headers.get('User-Agent'), request.referrer)
    
    social_links = {
        "youtube": "https://youtube.com/@gorillacamping",
        "instagram": "https://instagram.com/gorillacamping",
        "tiktok": "https://tiktok.com/@gorillacamping",
        "facebook": "https://facebook.com/gorillacamping",
        "reddit": "https://reddit.com/r/gorillacamping"
    }
    
    destination = social_links.get(platform, "https://gorillacamping.site")
    return redirect(destination)

# Category pages for better SEO
@app.route("/category/<category_name>")
def category(category_name):
    def fetch_category_posts():
        return list(db.posts.find({"category": category_name, "status": "published"})
                   .sort("date", -1).limit(20))
    
    posts = safe_db_operation(fetch_category_posts, [])
    
    meta_description = f"Guerilla camping guides about {category_name}. Real advice from someone living the lifestyle."
    meta_keywords = f"guerilla camping {category_name}, camping {category_name}, off-grid {category_name}"
    
    return render_template("category.html", 
                         posts=posts, 
                         category=category_name,
                         meta_description=meta_description,
                         meta_keywords=meta_keywords)

# Sitemap for SEO
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    pages = []
    
    # Static pages
    static_pages = [
        ('index', 1.0, 'daily'),
        ('blog', 0.9, 'daily'),
        ('gear', 0.8, 'weekly'),
        ('about', 0.6, 'monthly'),
        ('contact', 0.7, 'monthly'),
        ('as_is', 0.5, 'yearly'),
        ('privacy', 0.5, 'yearly')
    ]
    
    for page, priority, changefreq in static_pages:
        pages.append({
            'loc': url_for(page, _external=True),
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'priority': priority,
            'changefreq': changefreq
        })
    
    # Dynamic blog posts
    def fetch_published_posts():
        return list(db.posts.find({"status": "published"}, {"slug": 1, "date": 1}))
    
    posts = safe_db_operation(fetch_published_posts, [])
    
    for post in posts:
        pages.append({
            'loc': url_for('post', slug=post['slug'], _external=True),
            'lastmod': post['date'].strftime('%Y-%m-%d'),
            'priority': 0.8,
            'changefreq': 'weekly'
        })
    
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = Response(sitemap_xml, mimetype='application/xml')
    return response

# robots.txt for SEO
@app.route('/robots.txt')
def robots():
    return Response(
        f"User-agent: *\nAllow: /\nSitemap: {url_for('sitemap', _external=True)}\n",
        mimetype='text/plain'
    )

# Newsletter signup (MailerLite integration)
@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email', '').strip()
    
    if not email:
        return jsonify({"success": False, "message": "Email is required!"})
    
    # Email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({"success": False, "message": "Please enter a valid email address."})
    
    # Save to database
    def save_subscriber():
        subscriber_data = {
            "email": email,
            "timestamp": datetime.utcnow(),
            "status": "active",
            "source": request.referrer or "direct"
        }
        db.subscribers.insert_one(subscriber_data)
        return True
    
    saved = safe_db_operation(save_subscriber, False)
    
    if saved:
        return jsonify({"success": True, "message": "Welcome to the guerilla camping tribe! 🏕️"})
    else:
        return jsonify({"success": False, "message": "Something went wrong. Try again!"})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
