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

# Enable GZIP compression on responses (no visual changes to the site).
Compress(app)

# Slightly decrease default static file send time to allow refreshing if needed without losing performance gains.
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600

# 🎯 GUERILLA CONFIG - Your affiliate IDs and tracking
GOOGLE_ANALYTICS_ID = "G-JPKKPRXX6S"
COOKIEYES_SITE_ID = os.environ.get('COOKIEYES_SITE_ID', 'YOUR_COOKIEYES_ID')  # Get from CookieYes dashboard
AMAZON_ASSOCIATE_TAG = os.environ.get('AMAZON_TAG', 'gorillacamping-20')  # Your Amazon Associates tag
MAILERLITE_API_KEY = os.environ.get('MAILERLITE_API_KEY', '')

# MongoDB connection with error handling
try:
    mongodb_uri = os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URI')
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

@app.before_serving
async def create_indexes():
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

# Guerilla security headers for maximum SEO/trust
@app.after_request
def security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # 🚀 Cache optimization for speed
    if request.endpoint in ['static', 'sitemap', 'robots']:
        response.headers['Cache-Control'] = 'public, max-age=86400'
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

# 💰 Track user consent for affiliate revenue optimization
def track_user_consent(consent_data, user_info=None):
    """Track consent for affiliate attribution analysis"""
    def save_consent():
        consent_record = {
            'timestamp': datetime.utcnow(),
            'ip_hash': hash(request.remote_addr) if request.remote_addr else None,
            'user_agent': request.headers.get('User-Agent'),
            'analytics_consent': consent_data.get('analytics', False),
            'marketing_consent': consent_data.get('advertisement', False),
            'functional_consent': consent_data.get('functional', False),
            'referrer': request.referrer,
            'page': request.path,
            'revenue_potential': 'high' if consent_data.get('advertisement') else 'low'
        }
        db.consent_analytics.insert_one(consent_record)
        return consent_record
    
    return safe_db_operation(save_consent, {})

# Get recent posts with error handling
def get_recent_posts(limit=5):
    def fetch_posts():
        return list(db.posts.find({"status": "published"}).sort("date", -1).limit(limit))
    
    posts = safe_db_operation(fetch_posts, [])
    
    # 🎯 Guerilla fallback posts optimized for affiliate sales
    if not posts:
        posts = [
            {
                "title": "Best Budget Camping Gear Under $20 (Amazon Finds 2024)",
                "slug": "budget-camping-gear-under-20-amazon",
                "excerpt": "Military surplus secrets + Amazon deals = Complete guerilla camping kit for under $50. Real gear I actually use!",
                "date": datetime.now() - timedelta(days=1),
                "category": "Budget Gear",
                "affiliate_ready": True,
                "revenue_potential": "high"
            },
            {
                "title": "Stealth Camping Essentials: 5 Must-Have Items",
                "slug": "stealth-camping-essentials-gear",
                "excerpt": "The exact 5 items that make stealth camping possible. Tested in urban environments and wild camping.",
                "date": datetime.now() - timedelta(days=3),
                "category": "Stealth Tactics",
                "affiliate_ready": True,
                "revenue_potential": "high"
            },
            {
                "title": "DIY Ultralight Backpacking Gear (Save $300+)",
                "slug": "diy-ultralight-backpacking-gear",
                "excerpt": "How I built ultralight gear for 1/3 the price. Complete tutorials + where to buy materials.",
                "date": datetime.now() - timedelta(days=5),
                "category": "DIY Projects",
                "affiliate_ready": True,
                "revenue_potential": "medium"
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

# 💰 Enhanced affiliate click tracking with revenue attribution
def track_affiliate_click(product_id, source_page, user_consent=None):
    """Track affiliate clicks with consent-aware revenue attribution"""
    def save_click():
        click_data = {
            "product_id": product_id,
            "source_page": source_page,
            "timestamp": datetime.utcnow(),
            "user_agent": request.headers.get('User-Agent'),
            "referrer": request.referrer,
            "ip_hash": hash(request.remote_addr) if request.remote_addr else None,
            "has_marketing_consent": user_consent and user_consent.get('advertisement', False),
            "revenue_trackable": bool(user_consent and user_consent.get('advertisement')),
            "session_id": session.get('session_id', 'anonymous'),
            "click_type": "affiliate_conversion"
        }
        db.affiliate_clicks.insert_one(click_data)
        
        # Update product performance metrics
        db.product_performance.update_one(
            {"product_id": product_id},
            {
                "$inc": {"clicks": 1},
                "$set": {"last_clicked": datetime.utcnow()}
            },
            upsert=True
        )
        return True
    
    return safe_db_operation(save_click, False)

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

# 🎯 Context processor for global template variables
@app.context_processor
def inject_globals():
    return {
        'google_analytics_id': GOOGLE_ANALYTICS_ID,
        'cookieyes_site_id': COOKIEYES_SITE_ID,
        'amazon_tag': AMAZON_ASSOCIATE_TAG,
        'current_year': datetime.now().year,
        'site_name': 'Gorilla Camping',
        'site_url': 'https://gorillacamping.site'
    }

# 🎯 Context processor to inject "now" for use in base.html (this is the fix!)
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Home page with latest posts
@app.route("/")
def index():
    latest_posts = get_recent_posts(6)
    
    # 🎯 SEO meta data optimized for affiliate revenue
    meta_description = "Guerilla camping gear reviews, budget outdoor equipment, and off-grid survival tips. Real advice from someone living the lifestyle. Save money, make adventures happen."
    meta_keywords = "guerilla camping, budget camping gear, stealth camping, off-grid living, camping gear reviews, amazon camping deals, cheap outdoor gear"
    
    # Track page view for analytics
    track_click("homepage", "internal", request.headers.get('User-Agent'), request.referrer)
    
    return render_template("index.html", 
                         latest_posts=latest_posts,
                         meta_description=meta_description,
                         meta_keywords=meta_keywords,
                         page_type="homepage")

# Blog listing with pagination and SEO
@app.route("/blog")
def blog():
    page = int(request.args.get("page", 1))
    per_page = 12
    all_posts, total = get_posts_paginated(page, per_page)
    
    meta_description = "Guerilla camping guides, gear reviews, and outdoor survival tips. Real advice from someone living off-grid. Budget gear that actually works."
    meta_keywords = "guerilla camping blog, off-grid living, camping gear reviews, budget camping, DIY camping gear, outdoor survival tips"
    
    return render_template("blog.html", 
                         posts=all_posts, 
                         page=page, 
                         total=total, 
                         per_page=per_page,
                         meta_description=meta_description,
                         meta_keywords=meta_keywords,
                         page_type="blog")

# Individual blog post with affiliate optimization
@app.route("/blog/<slug>")
def post(slug):
    def fetch_post():
        return db.posts.find_one({"slug": slug, "status": "published"})
    
    post_data = safe_db_operation(fetch_post)
    
    # 🎯 Demo posts optimized for affiliate conversions
    if not post_data:
        demo_posts = {
            "budget-camping-gear-under-20-amazon": {
                "title": "Best Budget Camping Gear Under $20 (Amazon Finds 2024)",
                "content": """
# The Ultimate Guerilla Camping Gear Guide (Under $20 Each!)

Living off-grid for 3+ years, I've learned that **expensive gear doesn't make you a better camper**. Here's my battle-tested list of budget gear that actually works:

## 1. Military Surplus Poncho ($15) - The Swiss Army Knife of Camping
This thing is INSANE value. Use it as:
- Rain protection 
- Tarp/shelter
- Ground cover
- Emergency blanket

**[🔥 GET THE EXACT ONE I USE (Amazon)](https://gorillacamping.site/go/poncho)**

## 2. Lifestraw Personal Water Filter ($12-18)
Never buy bottled water again. I've used this in sketchy streams and it works.

**[💧 GRAB YOUR LIFESTRAW HERE](https://gorillacamping.site/go/lifestraw)**

## 3. Emergency Mylar Sleeping Bag ($8)
90% as effective as a $200 sleeping bag. Not kidding.

**[🛏️ CHECK CURRENT PRICE](https://gorillacamping.site/go/mylar-bag)**

## The Complete $50 Setup
- Poncho: $15
- LifeStraw: $15  
- Mylar bag: $8
- Paracord (50ft): $5
- Emergency fire starter: $7

**Total: $50** vs. $500+ for "premium" gear that does the same thing.

Want the complete list with exact Amazon links? **[Join my email list](https://gorillacamping.site/subscribe)** - I send weekly gear finds and survival tips.
                """,
                "date": datetime.now() - timedelta(days=1),
                "category": "Budget Gear",
                "slug": slug,
                "affiliate_ready": True,
                "meta_description": "Complete guerilla camping setup for under $50. Military surplus secrets + Amazon deals. Real gear I actually use daily.",
                "featured_products": ["poncho", "lifestraw", "mylar-bag"]
            },
            "stealth-camping-essentials-gear": {
                "title": "Stealth Camping Essentials: 5 Must-Have Items",
                "content": """
# Stealth Camping Essentials: Don't Get Caught!

After 100+ nights of stealth camping (urban and wilderness), these 5 items are NON-NEGOTIABLE:

## 1. Silent Setup Gear
**Ninja Tarp System** - No metal grommets that clink
**[🥷 GET THE SILENT TARP](https://gorillacamping.site/go/silent-tarp)**

## 2. Light Discipline 
Red headlamp only. Blue/white light = busted.
**[🔴 RED HEADLAMP (Amazon)](https://gorillacamping.site/go/red-headlamp)**

## 3. Scent Control
Urban camping = don't smell like a camper.
**[🧼 CAMPING SOAP SHEETS](https://gorillacamping.site/go/soap-sheets)**

## 4. Quick Exit Strategy
Everything packed in 60 seconds or less.
**[⚡ QUICK-PACK SYSTEM](https://gorillacamping.site/go/quick-pack)**

## 5. Legal Insurance
Know your rights, carry proof of income/address.

**Total stealth kit: Under $75**

**Want my complete stealth camping guide?** Join 2,000+ guerilla campers getting weekly tips: **[Subscribe here](https://gorillacamping.site/subscribe)**
                """,
                "date": datetime.now() - timedelta(days=3),
                "category": "Stealth Tactics",
                "slug": slug,
                "affiliate_ready": True,
                "meta_description": "5 essential items for successful stealth camping. Tested in urban environments. Don't get caught - stay invisible.",
                "featured_products": ["silent-tarp", "red-headlamp", "soap-sheets"]
            }
        }
        
        post_data = demo_posts.get(slug, {
            "title": "Guerilla Camping Guide Coming Soon!",
            "content": "This post is being crafted with real field experience. Check back soon for authentic gear reviews and money-saving tips!",
            "date": datetime.now(),
            "category": "Coming Soon",
            "slug": slug,
            "meta_description": "Guerilla camping tips and tricks from someone living the lifestyle."
        })
    
    # Track post view
    track_click(f"post_{slug}", "internal", request.headers.get('User-Agent'), request.referrer)
    
    return render_template("post.html", 
                         post=post_data,
                         meta_description=post_data.get('meta_description', 'Guerilla camping tips and tricks'),
                         meta_keywords=f"guerilla camping, {post_data.get('category', 'camping')}, budget outdoor gear",
                         page_type="article")
@app.route("/gear")
def gear():
    def fetch_gear():
        return list(db.gear.find({"active": True}).sort("order", 1))
    gear_items = safe_db_operation(fetch_gear, [])
    meta_description = "Guerilla-tested camping gear that won't break the bank. Real reviews from someone who lives this lifestyle. Budget gear that actually works."
    meta_keywords = "budget camping gear, guerilla camping equipment, cheap camping gear, military surplus camping, amazon camping deals, outdoor gear reviews"
    return render_template("gear.html",
                           gear_items=gear_items,
                           meta_description=meta_description,
                           meta_keywords=meta_keywords,
                           page_type="product")
@app.route("/about")
def about():
    meta_description = "Meet the guerilla camper behind the blog. Real stories, real gear, real advice from someone living off-grid on a shoestring budget."
    meta_keywords = "about guerilla camping, off-grid lifestyle, camping blog author, budget outdoor living"
    
    return render_template("about.html",
                         meta_description=meta_description,
                         meta_keywords=meta_keywords,
                         page_type="about")

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
                    "user_agent": request.headers.get('User-Agent', 'Unknown'),
                    "revenue_opportunity": "high" if "collaboration" in subject.lower() or "brand" in message.lower() else "medium"
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
                         meta_keywords=meta_keywords,
                         page_type="contact")

# AS-IS terms and affiliate disclaimer page
@app.route("/as-is")
def as_is():
    meta_description = "Gorilla Camping affiliate marketing disclaimer, terms of use, and product recommendations policy. Guerilla-style transparency."
    meta_keywords = "affiliate disclaimer, as-is terms, gorilla camping legal, product reviews disclaimer"
    
    return render_template("as_is.html",
                         meta_description=meta_description,
                         meta_keywords=meta_keywords,
                         page_type="legal")

# Privacy policy
@app.route("/privacy")
def privacy():
    meta_description = "Gorilla Camping privacy policy. How we protect your data while helping you master guerilla camping."
    meta_keywords = "privacy policy, data protection, gorilla camping privacy"
    
    return render_template("privacy.html",
                         meta_description=meta_description,
                         meta_keywords=meta_keywords,
                         page_type="legal")

# 💰 Enhanced affiliate link tracker with conversion optimization
@app.route("/go/<product_id>")
def affiliate_redirect(product_id):
    # Track the click with enhanced analytics
    user_consent = session.get('cookie_consent', {})
    track_affiliate_click(product_id, request.referrer or 'direct', user_consent)

    # 🎯 Your actual affiliate links (UPDATE: now with your real links)
  # REPLACE LINES 516-532 WITH THIS CORRECTED VERSION:

# 💰 Enhanced affiliate link tracker with conversion optimization
@app.route("/go/<product_id>")
def affiliate_redirect(product_id):
    # Track the click with enhanced analytics
    user_consent = session.get('cookie_consent', {})
    track_affiliate_click(product_id, request.referrer or 'direct', user_consent)

    # 🎯 Your actual affiliate links (FIXED SYNTAX!)
    affiliate_links = {
        "jackery-explorer-240": "https://amzn.to/43ZFIvfV",
        "coleman-stove": "https://amzn.to/44eem7c", 
        "lifestraw-filter": "https://amzn.to/4dZjAae",
        # NEW MONEY-MAKERS:
        "leatherman-wave": "https://amzn.to/4k3C5ff",
        "survival-kit": "https://amzn.to/3GfUirZ",
        "budget-sleeping-bag": "https://amzn.to/3HYhjjG",  # FIXED - Added quotes, removed extra quote
        "viral-camping-bundle": "https://amzn.to/4niYcRo",
        "phone-tripod": "https://amzn.to/4eg8bCZ",
        "power-bank": "https://amzn.to/4l8bS04",
        "led-light": "https://amzn.to/45zljks",  # FIXED - Added missing colon
        "popup-tent": "https://amzn.to/4lg5kfE",
        # GUERRILLA BONUS LINKS:
        "poncho": f"https://amzn.to/3YourPonchoLink?tag={AMAZON_ASSOCIATE_TAG}",
        "lifestraw": f"https://amzn.to/3YourLifestrawLink?tag={AMAZON_ASSOCIATE_TAG}",
        "mylar-bag": f"https://amzn.to/3YourMylarLink?tag={AMAZON_ASSOCIATE_TAG}",
        "silent-tarp": f"https://amzn.to/3YourTarpLink?tag={AMAZON_ASSOCIATE_TAG}",
        "red-headlamp": f"https://amzn.to/3YourHeadlampLink?tag={AMAZON_ASSOCIATE_TAG}",
        "soap-sheets": f"https://amzn.to/3YourSoapLink?tag={AMAZON_ASSOCIATE_TAG}",
        "quick-pack": f"https://amzn.to/3YourPackLink?tag={AMAZON_ASSOCIATE_TAG}",
    }

    destination = affiliate_links.get(
        product_id, 
        f"https://amazon.com/s?k=camping+{product_id}&tag={AMAZON_ASSOCIATE_TAG}"
    )
    return redirect(destination)

    destination = affiliate_links.get(
        product_id, 
        f"https://amazon.com/s?k=camping+{product_id}&tag={AMAZON_ASSOCIATE_TAG}"
    )
    return redirect(destination)

@app.route("/social/<platform>")
def social_redirect(platform):
    track_click(f"social_{platform}", "external", request.headers.get('User-Agent'), request.referrer)
    
    social_links = {
        "youtube": "https://youtube.com/@gorillacamping",
        "instagram": "https://instagram.com/gorillacamping",
        "tiktok": "https://tiktok.com/@gorillacamping",
        "facebook": "https://www.facebook.com/profile.php?id=61577334442896",
        "reddit": "https://reddit.com/r/gorrilacamping",
        "twitter": "https://twitter.com/gorillacamping"
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
    
    meta_description = f"Guerilla camping guides about {category_name}. Real advice from someone living the lifestyle. Budget-friendly {category_name} tips."
    meta_keywords = f"guerilla camping {category_name}, camping {category_name}, off-grid {category_name}, budget {category_name}"
    
    return render_template("category.html", 
                         posts=posts, 
                         category=category_name,
                         meta_description=meta_description,
                         meta_keywords=meta_keywords,
                         page_type="category")

# 🎯 API endpoint for consent tracking
@app.route('/api/consent-update', methods=['POST'])
def consent_update():
    try:
        consent_data = request.json or {}
        session['cookie_consent'] = consent_data
        
        # Track consent for revenue optimization
        consent_record = track_user_consent(consent_data, {
            'page': request.referrer,
            'timestamp': datetime.utcnow()
        })
        
        return jsonify({
            "success": True, 
            "message": "Consent updated",
            "revenue_tracking": consent_data.get('advertisement', False)
        })
    except Exception as e:
        print(f"Consent update error: {e}")
        return jsonify({"success": False, "message": "Error updating consent"})

# Sitemap for SEO
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    pages = []
    
    # Static pages with priority optimization
    static_pages = [
        ('index', 1.0, 'daily'),
        ('blog', 0.9, 'daily'),
        ('gear', 0.95, 'weekly'),  # High priority - revenue page
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
    
    # Add demo posts to sitemap
    demo_posts = ['budget-camping-gear-under-20-amazon', 'stealth-camping-essentials-gear']
    for slug in demo_posts:
        pages.append({
            'loc': url_for('post', slug=slug, _external=True),
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'priority': 0.9,  # High priority for affiliate posts
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

# 💰 Newsletter signup with MailerLite integration
@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email', '').strip()
    name = request.form.get('name', '').strip()
    
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
            "name": name,
            "timestamp": datetime.utcnow(),
            "status": "active",
            "source": request.referrer or "direct",
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get('User-Agent'),
            "revenue_potential": "high",  # Email subscribers = money
            "tags": ["guerilla_camping", "budget_gear"]
        }
        db.subscribers.insert_one(subscriber_data)
        return True
    
    saved = safe_db_operation(save_subscriber, False)
    
    # TODO: Add actual MailerLite API integration here
    # import requests
    # mailerlite_response = requests.post(
    #     "https://api.mailerlite.com/api/v2/subscribers",
    #     headers={"X-MailerLite-ApiKey": MAILERLITE_API_KEY},
    #     json={"email": email, "name": name}
    # )
    
    if saved:
        return jsonify({
            "success": True, 
            "message": "🎯 Welcome to the guerilla camping tribe! Check your email for exclusive gear deals! 🏕️"
        })
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
