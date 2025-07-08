import os
import re
import uuid
import random
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session, Response, send_file, send_from_directory, make_response
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs
import traceback

# --- FLASK SETUP ---
app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY') or 'guerilla-camping-secret-2024'
app.config['SESSION_COOKIE_SECURE'] = True  # For HTTPS

# --- HANDLE OPTIONAL DEPENDENCIES ---
try:
    from flask_compress import Compress
    compress = Compress()
    compress.init_app(app)
    print("✅ Flask-Compress initialized")
except ImportError:
    print("⚠️ flask_compress not installed, continuing without compression")

try:
    import google.generativeai as genai
    
    # --- GEMINI AI SETUP ---
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        print("✅ Google Generative AI initialized")
    else:
        print("⚠️ GEMINI_API_KEY not set, AI features disabled")
except ImportError:
    print("⚠️ google.generativeai not installed, continuing without AI features")
    genai = None

# --- MONGODB SETUP ---
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
    print(f"❌ MongoDB connection error: {e}")
    db = None

# --- HELPER FUNCTIONS ---
def log_event(event_type, message, level="INFO"):
    """Simple logging function"""
    print(f"{level}: {event_type} - {message}")
    if db:
        try:
            db.logs.insert_one({
                "type": event_type,
                "message": message,
                "level": level,
                "timestamp": datetime.utcnow()
            })
        except Exception as e:
            print(f"❌ Error logging to MongoDB: {e}")

def ask_gemini(user_query, context=""):
    """Generate AI response with Google Gemini"""
    if not genai:
        return "AI services are currently unavailable."
    
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content([{"role":"user", "parts":[context + "\n\n" + user_query]}])
        return response.text
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return "Sorry, I'm having trouble processing your request right now. Please try again later."

def get_default_gear_items():
    """Return default gear items with highest affiliate payouts"""
    return [
        {
            'name': 'Jackery Explorer 240',
            'image': 'https://m.media-amazon.com/images/I/41XePYWYlAL._AC_US300_.jpg',
            'description': 'Perfect for keeping devices charged off-grid. This paid for itself with just 2 viral videos I made from camp.',
            'affiliate_id': 'jackery-explorer-240',
            'price': '$199.99',
            'old_price': '$299.99',
            'savings': 'Save $100',
            'rating': 5,
            'badges': ['HOT DEAL', 'BEST VALUE'],
            'specs': ['240Wh', '250W output', 'Multiple ports']
        },
        {
            'name': 'LifeStraw Personal Water Filter',
            'image': 'https://m.media-amazon.com/images/I/71SYsNwj7hL._AC_UL320_.jpg',
            'description': 'Essential survival gear that filters 99.9999% of waterborne bacteria. My #1 affiliate earner!',
            'affiliate_id': 'lifestraw-filter',
            'price': '$14.96',
            'old_price': '$19.95',
            'savings': 'Save 25%',
            'rating': 5,
            'badges': ['BESTSELLER'],
            'specs': ['1000L capacity', 'No chemicals', 'Compact']
        }
    ]

# --- ROUTES ---
@app.before_request
def redirect_www():
    """SEO Improvement: Redirect www to non-www for better SEO and analytics"""
    if request.host.startswith('www.'):
        url = request.url.replace('www.', '', 1)
        return redirect(url, code=301)

@app.route('/')
def home():
    """Homepage with high-conversion email capture"""
    # Track visitor for analytics and user count
    visitor_id = request.cookies.get('visitor_id')
    if not visitor_id:
        visitor_id = str(uuid.uuid4())
    
    # Track visit in MongoDB
    if db:
        db.visits.update_one(
            {"visitor_id": visitor_id},
            {"$set": {"last_visit": datetime.utcnow()},
             "$setOnInsert": {"first_visit": datetime.utcnow()}},
            upsert=True
        )
    
    response = make_response(render_template('index.html'))
    response.set_cookie('visitor_id', visitor_id, max_age=60*60*24*365)
    return response

@app.route('/blog')
def blog():
    """Blog listing page"""
    posts = []
    if db:
        try:
            posts = list(db.posts.find().sort("created_at", -1))
        except Exception as e:
            print(f"Error fetching posts: {e}")
    return render_template('blog.html', posts=posts)

@app.route('/blog/<slug>')
def post(slug):
    """Individual blog post page"""
    if db:
        post = db.posts.find_one({'slug': slug})
        if post:
            # Increment view counter
            db.posts.update_one(
                {'_id': post['_id']},
                {'$inc': {'views': 1}}
            )
            
            # Find related posts
            related_posts = list(db.posts.find({'_id': {'$ne': post['_id']}}).limit(3))
            return render_template('post.html', post=post, related_posts=related_posts)
    return redirect(url_for('blog'))

@app.route('/gear')
def gear():
    """Gear page - highest revenue generator"""
    gear_items = []

    # Tracking for analytics
    source = request.args.get('source', 'direct')
    utm_campaign = request.args.get('utm_campaign', '')
    
    # Get gear items from DB or use default
    if not db:
        gear_items = get_default_gear_items()
    else:
        try:
            gear_items = list(db.gear.find())
            if not gear_items:  # If empty collection
                gear_items = get_default_gear_items()
                
                # Store default items in DB
                for item in gear_items:
                    db.gear.insert_one(item)
        except Exception as e:
            print(f"Error fetching gear items: {e}")
            gear_items = get_default_gear_items()
            
    # Track visit
    if db:
        db.page_views.insert_one({
            'page': 'gear',
            'source': source,
            'utm_campaign': utm_campaign,
            'timestamp': datetime.utcnow(),
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })

    return render_template('gear.html', gear_items=gear_items)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if db:
            db.contacts.insert_one({
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'created_at': datetime.utcnow()
            })
        
        # Also add to email list for marketing
        if db and email:
            db.subscribers.update_one(
                {'email': email},
                {'$set': {'email': email, 'source': 'contact_form', 'updated_at': datetime.utcnow()}, 
                 '$setOnInsert': {'created_at': datetime.utcnow()}},
                upsert=True
            )
        
        flash('Message received! We will get back to you soon.', 'success')
        log_event("contact_form", f"Contact form submitted by {email}")
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/affiliate/<product_id>')
def affiliate_redirect(product_id):
    """Affiliate link redirect with tracking"""
    affiliate_urls = {
        'jackery-explorer-240': 'https://www.amazon.com/Jackery-Portable-Explorer-Generator-Emergency/dp/B07D29QNMJ?&linkCode=ll1&tag=gorillcamping-20',
        'lifestraw-filter': 'https://www.amazon.com/LifeStraw-Personal-Filtering-Emergency-Preparedness/dp/B07VMSR74F?&linkCode=ll1&tag=gorillcamping-20'
    }
    
    url = affiliate_urls.get(product_id, 'https://www.amazon.com/?&linkCode=ll2&tag=gorillcamping-20')
    
    # Track click in database
    if db:
        db.affiliate_clicks.insert_one({
            'product_id': product_id,
            'timestamp': datetime.utcnow(),
            'user_agent': request.headers.get('User-Agent', ''),
            'referrer': request.referrer,
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })
    
    log_event("affiliate_click", f"Affiliate click: {product_id}")
    return redirect(url)

@app.route('/social/<platform>')
def social_redirect(platform):
    """Social media redirect with tracking"""
    social_urls = {
        'reddit': 'https://www.reddit.com/r/gorillacamping',
        'facebook': 'https://www.facebook.com/profile.php?id=61577334442896',
        'tiktok': 'https://www.tiktok.com/@gorillacamping'
    }
    
    url = social_urls.get(platform, 'https://www.reddit.com/r/gorillacamping')
    
    # Track social click
    if db:
        db.social_clicks.insert_one({
            'platform': platform,
            'timestamp': datetime.utcnow(),
            'user_agent': request.headers.get('User-Agent', ''),
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })
    
    log_event("social_click", f"Social click: {platform}")
    return redirect(url)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Email subscriber collection endpoint"""
    email = request.form.get('email')
    source = request.form.get('source', 'unknown')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'})
    
    # Store in our own DB
    if db:
        db.subscribers.update_one(
            {'email': email},
            {'$set': {'email': email, 'source': source, 'updated_at': datetime.utcnow()}, 
             '$setOnInsert': {'created_at': datetime.utcnow()}},
            upsert=True
        )
    
    log_event("new_subscriber", f"New subscriber: {email}")
    
    # Create a MailerLite webhook or other email service integration here
    
    return jsonify({'success': True, 'message': 'Subscribed successfully'})

@app.route('/guerilla-camping-bible')
def ebook():
    """Ebook sales page"""
    return render_template('ebook.html')

@app.route('/thank-you')
def thank_you():
    """Thank you page after signup"""
    return render_template('thank_you.html')

@app.route('/sitemap.xml')
def sitemap():
    """Dynamic sitemap for SEO"""
    pages = []
    # Add static pages
    base_url = request.host_url.rstrip('/')
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Core pages
    pages.append({"loc": f"{base_url}/", "lastmod": today, "priority": "1.0"})
    pages.append({"loc": f"{base_url}/gear", "lastmod": today, "priority": "0.9"})
    pages.append({"loc": f"{base_url}/about", "lastmod": today, "priority": "0.8"})
    pages.append({"loc": f"{base_url}/blog", "lastmod": today, "priority": "0.7"})
    
    # Add dynamic blog pages
    if db:
        posts = db.posts.find({}, {"slug": 1, "updated_at": 1})
        for post in posts:
            last_mod = post.get('updated_at', datetime.now()).strftime('%Y-%m-%d')
            pages.append({
                "loc": f"{base_url}/blog/{post['slug']}",
                "lastmod": last_mod,
                "priority": "0.6"
            })
    
    xml = render_template('sitemap.xml', pages=pages)
    response = make_response(xml)
    response.headers["Content-Type"] = "application/xml"
    return response

@app.route("/api/optimize", methods=['POST'])
def generative_ai_assistant():
    """AI assistant with affiliate recommendations"""
    # Limit: 3 free queries per session unless Pro
    if not session.get("pro_user"):
        session['queries'] = session.get('queries', 0) + 1
        if session['queries'] > 3:
            return jsonify({"success": False, "message": "Upgrade to Pro for unlimited AI!"})
    
    data = request.json
    user_query = data.get("query", "I need some camping advice.")
    
    # Generate response
    try:
        ai_response = ask_gemini(user_query)
        
        # Recommend gear based on query content
        gear_links = ""
        keywords = ["power", "charging", "battery", "electricity", "devices"]
        if any(word in user_query.lower() for word in keywords):
            gear_links = "\n\n*Recommendation: [Jackery Explorer 240](https://gorillacamping.site/affiliate/jackery-explorer-240) - Perfect for keeping devices charged while camping.*"
        
        keywords = ["water", "drink", "filter", "stream", "river"]
        if any(word in user_query.lower() for word in keywords):
            gear_links += "\n\n*Recommendation: [LifeStraw Filter](https://gorillacamping.site/affiliate/lifestraw-filter) - Essential for safe drinking water in the wilderness.*"
        
        # Log AI interaction
        if db:
            db.ai_logs.insert_one({
                "question": user_query,
                "ai_response": ai_response,
                "timestamp": datetime.utcnow(),
                "visitor_id": request.cookies.get('visitor_id', 'unknown'),
                "recommendations": gear_links != ""
            })
        
        log_event("ai_query", f"AI query processed: {user_query[:50]}...")
        return jsonify({"success": True, "response": ai_response + gear_links})
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return jsonify({"success": False, "message": "The AI brain is currently offline. Please try again later."})

@app.route('/robots.txt')
def robots():
    """SEO: Robots.txt file"""
    r = Response("""
User-agent: *
Allow: /
Sitemap: https://gorillacamping.site/sitemap.xml
    """, mimetype='text/plain')
    return r

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page with recommendations"""
    top_gear = get_default_gear_items()[:2] if not db else list(db.gear.find().limit(2))
    return render_template('404.html', recommended_gear=top_gear), 404

# --- REVENUE TRACKING ENDPOINTS ---

@app.route('/track/view', methods=['POST'])
def track_view():
    """Track page views and product impressions"""
    data = request.json
    if db:
        db.view_tracking.insert_one({
            'page': data.get('page'),
            'products': data.get('products', []),
            'timestamp': datetime.utcnow(),
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })
    return jsonify({'success': True})

@app.route('/track/conversion', methods=['POST'])
def track_conversion():
    """Track successful conversions for analytics"""
    data = request.json
    if db:
        db.conversions.insert_one({
            'type': data.get('type'),
            'value': data.get('value'),
            'source': data.get('source'),
            'timestamp': datetime.utcnow(),
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })
    return jsonify({'success': True})

# --- SERVER CONFIG ---
if __name__ == '__main__':
    # Use PORT environment variable for Heroku compatibility
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
