import os
import re
import uuid
import random
import requests
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session, Response, send_file, send_from_directory, make_response
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs
import traceback

# --- FLASK SETUP ---
app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY') or 'guerilla-camping-secret-2025'
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
        genai = None
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
    if db is not None:
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
            'specs': ['240Wh', '250W output', 'Multiple ports'],
            'commission': '$6.00 (3%)'
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
            'specs': ['1000L capacity', 'No chemicals', 'Compact'],
            'commission': '$0.45 (3%)'
        }
    ]

def get_high_commission_gear():
    """Return high-commission gear (20-30% instead of Amazon's 3-4%)"""
    return [
        {
            'name': '4Patriots Emergency Food Kit',
            'image': 'https://via.placeholder.com/300x200?text=Emergency+Food',
            'description': 'My #1 recommended survival food - lasts 25 years and tastes great!',
            'affiliate_id': '4patriots-food',
            'price': '$197',
            'old_price': '$297',
            'commission': '$49.25 (25%)',  # vs $5.91 on Amazon (3%)
            'inventory': random.randint(2, 7),
            'affiliate_link': 'https://4patriots.com/products/4week-food?drolid=0001'
        },
        {
            'name': 'Alexapure Pro Water Filter',
            'image': 'https://via.placeholder.com/300x200?text=Water+Filter',
            'description': 'The ultimate off-grid water solution - I use this daily at camp.',
            'affiliate_id': 'alexapure-pro',
            'price': '$249',
            'old_price': '$349',
            'commission': '$74.70 (30%)',  # vs $7.47 on Amazon (3%)
            'inventory': random.randint(1, 5),
            'affiliate_link': 'https://4patriots.com/products/alexapure-pro?drolid=0001'
        }
    ]

def generate_visitor_id():
    """Generate a unique visitor ID for tracking"""
    return str(uuid.uuid4())

def track_page_view(page_name, source=None, metadata=None):
    """Track page view with metadata"""
    if db is None:
        return
        
    visitor_id = request.cookies.get('visitor_id', generate_visitor_id())
    
    view_data = {
        'page': page_name,
        'timestamp': datetime.utcnow(),
        'visitor_id': visitor_id,
        'user_agent': request.headers.get('User-Agent', ''),
        'ip_hash': hash(request.remote_addr) if request.remote_addr else None,
        'referrer': request.referrer
    }
    
    if source:
        view_data['source'] = source
        
    if metadata and isinstance(metadata, dict):
        view_data.update(metadata)
    
    try:
        db.page_views.insert_one(view_data)
    except Exception as e:
        print(f"❌ Error tracking page view: {e}")

# --- ROUTES ---
@app.before_request
def redirect_www():
    """SEO Improvement: Redirect www to non-www for better SEO and analytics"""
    if request.host.startswith('www.'):
        url = request.url.replace('www.', '', 1)
        return redirect(url, code=301)

# Add these routes to your app.py file

@app.route('/api/guerilla-chat', methods=['POST'])
def guerilla_chat():
    """AI-powered mascot chat that drives revenue"""
    if request.method == 'POST':
        data = request.get_json()
        user_message = data.get('message', '')
        
        # Track this conversation in the database
        if db is not None:
            db.guerilla_chats.insert_one({
                'user_message': user_message,
                'timestamp': datetime.utcnow(),
                'visitor_id': request.cookies.get('visitor_id', 'unknown'),
                'page': request.headers.get('Referer')
            })
        
        # Check for product recommendations
        product_recs = []
        
        # Power-related keywords
        if any(word in user_message.lower() for word in ['power', 'battery', 'charging', 'electricity']):
            product_recs.append({
                'id': 'jackery-explorer-240',
                'name': 'Jackery Explorer 240',
                'reason': 'This is what I personally use for all my power needs when camping'
            })
        
        # Water-related keywords
        if any(word in user_message.lower() for word in ['water', 'drink', 'thirsty', 'filter']):
            product_recs.append({
                'id': 'lifestraw-filter', 
                'name': 'LifeStraw Water Filter',
                'reason': 'It filters 99.9999% of waterborne bacteria from any water source'
            })
        
        # Food-related keywords  
        if any(word in user_message.lower() for word in ['food', 'eat', 'meal', 'hungry']):
            product_recs.append({
                'id': '4patriots-food',
                'name': '4Patriots Emergency Food Kit',
                'reason': '25-year shelf life emergency food that tastes amazing'
            })
        
        # Generate AI response using Gemini if available
        try:
            if genai:
                ai_response = ask_gemini(
                    user_message,
                    context="You are Guerilla the Gorilla, a badass camping expert with a focus on off-grid living, survival skills, and making money while camping. You have a rugged, no-nonsense personality. Your responses should be helpful but have an edge to them. You curse occasionally. You're an expert on camping gear and especially like recommending products that help people make money while camping through content creation."
                )
            else:
                # Fallback responses if Gemini not available
                responses = [
                    "Hell yeah, I can help with that. The key to successful camping is always having the right gear.",
                    "As a badass gorilla who's seen it all, let me tell you - camping is about preparation and having the right equipment.",
                    "Listen up, camper. The difference between a miserable night and an awesome adventure is the gear you bring.",
                    "I've spent years in the wilderness, and the #1 mistake I see is people cheaping out on essential equipment.",
                    "Want to know how I make money while camping? It's all about creating content and leveraging affiliate marketing."
                ]
                ai_response = random.choice(responses)
            
            # Add product recommendations to response if appropriate
            if product_recs and random.random() < 0.7:  # 70% chance to include recommendation
                product = random.choice(product_recs)
                rec_text = f"\n\nBy the way, for {product['id'].split('-')[0]} needs, I personally use the {product['name']} - {product['reason']}. Want me to show you more details?"
                ai_response += rec_text
                
            return jsonify({
                'response': ai_response,
                'recommendations': product_recs
            })
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return jsonify({
                'response': "Sorry, I'm having a bit of trouble right now. Can you try again?",
                'recommendations': product_recs
            })

@app.route('/guerilla-bible')
def guerilla_bible():
    """Digital product sales page"""
    # Track this page view
    if db is not None:
        db.page_views.insert_one({
            'page': 'guerilla_bible',
            'timestamp': datetime.utcnow(),
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })
    
    # Testimonials to display (randomly selected)
    testimonials = [
        {"name": "Mike T.", "location": "Colorado", "text": "I was dead broke when I started. Following just Chapter 2, I made $438 in my first month with the high-commission affiliate strategy."},
        {"name": "Sarah K.", "location": "Oregon", "text": "The free camping locations in Chapter 1 saved me $600/month in rent while I built my affiliate business."},
        {"name": "John D.", "location": "Montana", "text": "Now earning $50-100/day with minimal effort from camp."},
        {"name": "Lisa M.", "location": "Washington", "text": "The Student Pack secrets alone are worth 10X the price of this guide!"}
    ]
    
    return render_template('guerilla_bible.html', 
                         testimonials=random.sample(testimonials, 2))
@app.route('/guerilla-stats')
def guerilla_stats():
    """Admin dashboard for Guerilla AI revenue stats"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    stats = {
        'total_chats': 0,
        'product_recommendations': 0,
        'product_clicks': 0,
        'conversion_rate': 0,
        'estimated_revenue': 0,
        'top_products': []
    }
    
    if db is not None:
        # Get chat stats
        stats['total_chats'] = db.guerilla_chats.count_documents({})
        
        # Get recommendation stats
        product_views = list(db.guerilla_product_views.aggregate([
            {"$group": {"_id": "$product_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]))
        
        stats['product_recommendations'] = sum(p['count'] for p in product_views)
        
        # Get click stats
        product_clicks = list(db.guerilla_product_clicks.aggregate([
            {"$group": {"_id": "$product_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]))
        
        stats['product_clicks'] = sum(p['count'] for p in product_clicks)
        
        # Calculate conversion rate
        if stats['product_recommendations'] > 0:
            stats['conversion_rate'] = round((stats['product_clicks'] / stats['product_recommendations']) * 100, 2)
        
        # Estimated revenue (based on average commission)
        stats['estimated_revenue'] = round(stats['product_clicks'] * 15.75, 2)  # $15.75 average commission
        
        # Get top products
        top_products = []
        for product in product_clicks[:5]:  # Top 5 products
            product_info = {
                'id': product['_id'],
                'views': next((p['count'] for p in product_views if p['_id'] == product['_id']), 0),
                'clicks': product['count']
            }
            
            # Add product details
            if product['_id'] == 'jackery-explorer-240':
                product_info['name'] = 'Jackery Explorer 240'
                product_info['commission'] = '$6.00'
            elif product['_id'] == 'lifestraw-filter':
                product_info['name'] = 'LifeStraw Water Filter'
                product_info['commission'] = '$0.45'
            elif product['_id'] == '4patriots-food':
                product_info['name'] = '4Patriots Food Kit'
                product_info['commission'] = '$49.25'
            else:
                product_info['name'] = product['_id']
                product_info['commission'] = '$5.00'
                
            # Calculate conversion rate for this product
            if product_info['views'] > 0:
                product_info['conversion_rate'] = round((product_info['clicks'] / product_info['views']) * 100, 2)
            else:
                product_info['conversion_rate'] = 0
                
            top_products.append(product_info)
            
        stats['top_products'] = top_products
    
    return render_template('guerilla_stats.html', stats=stats)

@app.route('/track/guerilla-view', methods=['POST'])
def track_guerilla_view():
    """Track Guerilla product view"""
    data = request.get_json()
    product_id = data.get('product_id')
    
    if db is not None and product_id:
        db.guerilla_product_views.insert_one({
            'product_id': product_id,
            'timestamp': datetime.utcnow(),
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })
    
    return jsonify({'success': True})

@app.route('/track/guerilla-click', methods=['POST'])
def track_guerilla_click():
    """Track Guerilla product click"""
    data = request.get_json()
    product_id = data.get('product_id')
    
    if db is not None and product_id:
        db.guerilla_product_clicks.insert_one({
            'product_id': product_id,
            'timestamp': datetime.utcnow(),
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })
    
    return jsonify({'success': True})
@app.route('/')
def home():
    # Track visitor for analytics and user count
    visitor_id = request.cookies.get('visitor_id')
    if not visitor_id:
        visitor_id = generate_visitor_id()
    
    # Track visit in MongoDB
    if db is not None:
        db.visits.update_one(
            {"visitor_id": visitor_id},
            {"$set": {"last_visit": datetime.utcnow()},
             "$setOnInsert": {"first_visit": datetime.utcnow()}},
            upsert=True
        )
    
    # Track page view with UTM parameters
    utm_source = request.args.get('utm_source')
    utm_medium = request.args.get('utm_medium')
    utm_campaign = request.args.get('utm_campaign')
    
    if utm_source or utm_medium or utm_campaign:
        track_page_view('home', source='utm', metadata={
            'utm_source': utm_source,
            'utm_medium': utm_medium,
            'utm_campaign': utm_campaign
        })
    else:
        track_page_view('home')
    
    # FIXED: Use only index.html until we create index_b.html
    template = 'index.html'
    
    response = make_response(render_template(template))
    response.set_cookie('visitor_id', visitor_id, max_age=60*60*24*365)
    return response

@app.route('/blog')
def blog():
    """Blog listing page"""
    posts = []
    if db is not None:
        try:
            posts = list(db.posts.find().sort("created_at", -1))
        except Exception as e:
            print(f"Error fetching posts: {e}")
    
    track_page_view('blog')
    return render_template('blog.html', posts=posts)

@app.route('/api/gorilla-ai', methods=['POST'])
def gorilla_ai():
    """Gorilla AI assistant that recommends affiliate products"""
    data = request.json
    user_query = data.get('query', '')
    
    # Track analytics
    if db is not None:
        db.ai_interactions.insert_one({
            'query': user_query,
            'timestamp': datetime.utcnow(),
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })
    
    # Check for product recommendation opportunities
    product_matches = []
    
    if any(word in user_query.lower() for word in ['power', 'battery', 'charging', 'electricity']):
        product_matches.append({
            'name': 'Jackery Explorer 240',
            'link': '/affiliate/jackery-explorer-240',
            'reason': 'perfect for keeping devices charged at camp'
        })
    
    if any(word in user_query.lower() for word in ['water', 'drink', 'thirsty', 'hydration']):
        product_matches.append({
            'name': 'LifeStraw Filter',
            'link': '/affiliate/lifestraw-filter',
            'reason': 'ensures safe drinking water from any source'
        })
        
    if any(word in user_query.lower() for word in ['food', 'eat', 'hungry', 'meal', 'cook']):
        product_matches.append({
            'name': '4Patriots Food Kit',
            'link': '/affiliate/4patriots-food',
            'reason': '25-year shelf life emergency food'
        })
    
    # Generate AI response
    try:
        ai_response = ask_gemini(user_query)
        
        # Add subtle product recommendations
        if product_matches:
            ai_response += "\n\n🦍 GORILLA RECOMMENDS:\n"
            for product in product_matches:
                ai_response += f"• [{product['name']}]({product['link']}) - {product['reason']}\n"
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'recommendations': product_matches
        })
    except Exception as e:
        print(f"AI Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })
@app.route('/blog/<slug>')
def post(slug):
    """Individual blog post page"""
    if db is not None:
        post = db.posts.find_one({'slug': slug})
        if post:
            # Increment view counter
            db.posts.update_one(
                {'_id': post['_id']},
                {'$inc': {'views': 1}}
            )
            
            # Find related posts
            related_posts = list(db.posts.find({
                '_id': {'$ne': post['_id']}
            }).limit(3))
            
            # Track view with metadata
            track_page_view('blog_post', metadata={'post_slug': slug, 'post_title': post.get('title', '')})
            
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
    if db is None:
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
            
    # Track visit with metadata
    track_page_view('gear', source=source, metadata={
        'utm_campaign': utm_campaign
    })

    return render_template('gear.html', gear_items=gear_items)
@app.route('/premium-gear')
def premium_gear():
    """High-commission products page (20-30% commission vs Amazon's 3-4%)"""
    # Get high-commission gear with inventory urgency
    items = [
        {
            'name': '4Patriots Food Storage Kit',
            'image': 'https://via.placeholder.com/600x400?text=4Patriots+Food+Kit',
            'description': 'Long-term emergency food with 25-year shelf life. Perfect for off-grid camping and prepping.',
            'price': '$197.00',
            'old_price': '$297.00',
            'commission': '$49.25 (25%)',  # vs $5.91 on Amazon (3%)
            'affiliate_link': 'https://4patriots.com/products/4week-food?rfsn=YOUR_ID_HERE',
            'inventory': 7
        },
        {
            'name': 'Bluetti Portable Power Station',
            'image': 'https://via.placeholder.com/600x400?text=Bluetti+Power+Station',
            'description': 'Complete off-grid power solution I personally use for my viral TikTok content creation.',
            'price': '$249.00',
            'old_price': '$349.00',
            'commission': '$74.70 (30%)', # vs $7.47 on Amazon (3%)
            'affiliate_link': 'https://www.bluettipower.com/products/bluetti-eb70s-portable-power-station?ref=YOUR_ID_HERE',
            'inventory': 4
        }
    ]
    
    # Track page view with UTM parameters
    source = request.args.get('source', 'direct')
    track_page_view('premium_gear', source=source)
    
    return render_template('premium_gear.html', items=items)

@app.route('/about')
def about():
    """About page"""
    track_page_view('about')
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if db is not None:
            db.contacts.insert_one({
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'created_at': datetime.utcnow()
            })
        
        # Also add to email list for marketing
        if db is not None and email:
            db.subscribers.update_one(
                {'email': email},
                {'$set': {'email': email, 'source': 'contact_form', 'updated_at': datetime.utcnow()}, 
                 '$setOnInsert': {'created_at': datetime.utcnow()}},
                upsert=True
            )
        
        flash('Message received! We will get back to you soon.', 'success')
        log_event("contact_form", f"Contact form submitted by {email}")
        return redirect(url_for('contact'))
    
    track_page_view('contact')
    return render_template('contact.html')

@app.route('/student-pack-strategy')
def student_pack_strategy():
    """Revenue strategy using Student Pack tools"""
    tools = [
        {
            'name': 'Name.com',
            'benefit': 'Free domain name + SSL',
            'revenue_strategy': 'Create dedicated landing domains for different affiliate categories',
            'example': 'SurvivalGearHub.me → 26% conversion on survival products'
        },
        {
            'name': 'DigitalOcean',
            'benefit': '$200 free credit',
            'revenue_strategy': 'Create multiple niche microsites targeting specific keywords',
            'example': 'SolarCampingGuide.com → $317 monthly affiliate revenue'
        },
        {
            'name': 'Bootstrap Studio',
            'benefit': 'Free pro license',
            'revenue_strategy': 'Create high-converting landing pages without coding',
            'example': 'Created 7 landing pages in 1 day → $412 in first-month sales'
        },
        {
            'name': 'Canva Pro',
            'benefit': 'Free premium subscription',
            'revenue_strategy': 'Create viral Pinterest pins for affiliate products',
            'example': '1 viral pin → 4,700 clicks → $539 in commissions'
        }
    ]
    
    return render_template('student_pack.html', tools=tools)
@app.route('/affiliate/<product_id>')
def affiliate_redirect(product_id):
    """Affiliate link redirect with tracking"""
    affiliate_urls = {
        'jackery-explorer-240': 'https://www.amazon.com/Jackery-Portable-Explorer-Generator-Emergency/dp/B07D29QNMJ?&linkCode=ll1&tag=gorillcamping-20',
        'lifestraw-filter': 'https://www.amazon.com/LifeStraw-Personal-Filtering-Emergency-Preparedness/dp/B07VMSR74F?&linkCode=ll1&tag=gorillcamping-20',
        # High-commission affiliate products (20-30% vs Amazon's 3-4%)
        '4patriots-food': 'https://4patriots.com/products/4week-food?drolid=0001',
        'alexapure-pro': 'https://4patriots.com/products/alexapure-pro?drolid=0001'
    }
    
    url = affiliate_urls.get(product_id, 'https://www.amazon.com/?&linkCode=ll2&tag=gorillcamping-20')
    
    # Track click in database
    if db is not None:
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
    if db is not None:
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
    if db is not None:
        db.subscribers.update_one(
            {'email': email},
            {'$set': {'email': email, 'source': source, 'updated_at': datetime.utcnow()}, 
             '$setOnInsert': {'created_at': datetime.utcnow()}},
            upsert=True
        )
    
    log_event("new_subscriber", f"New subscriber: {email} from {source}")
    
    # MailerLite Integration - replace with your own API key and group ID
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-MailerLite-ApiKey': os.environ.get('MAILERLITE_API_KEY', '')
        }
        
        data = {
            'email': email,
            'name': '',  # Can be blank
            'fields': {
                'source': source
            },
            'resubscribe': True,
            'type': 'active'
        }
        
        # Send to MailerLite
        if os.environ.get('MAILERLITE_API_KEY'):
            group_id = os.environ.get('MAILERLITE_GROUP_ID', '123456')
            response = requests.post(
                f'https://api.mailerlite.com/api/v2/groups/{group_id}/subscribers',
                headers=headers,
                json=data
            )
            
            if response.status_code not in (200, 201):
                print(f"MailerLite API error: {response.text}")
    except Exception as e:
        print(f"Error adding subscriber to MailerLite: {e}")
    
    return jsonify({'success': True, 'message': 'Subscribed successfully'})

# --- MONEY-MAKING ROUTES ---

@app.route('/guerilla-guide')
def guerilla_guide():
    """Digital product sales page with A/B price testing"""
    # A/B test price points (27 vs 37)
    test_group = 'a' if random.random() < 0.5 else 'b'
    price = '$27' if test_group == 'a' else '$37'
    
    # Track visit with test group
    source = request.args.get('source', 'direct')
    
    if db is not None:
        db.page_views.insert_one({
            'page': 'guerilla_guide',
            'source': source,
            'test_group': test_group,
            'price': price,
            'timestamp': datetime.utcnow(),
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })
    
    # Dynamic testimonials
    testimonials = [
        {"name": "Mike T.", "location": "Colorado", "text": "Made $486 in my first month using these camping spots."},
        {"name": "Sarah K.", "location": "Oregon", "text": "This paid for my entire camping setup in 2 weeks!"},
        {"name": "John D.", "location": "Montana", "text": "Now earning $50-100/day with minimal effort from camp."}
    ]
    
    return render_template('guerilla_guide.html', 
                         price=price, 
                         testimonials=random.sample(testimonials, 2),
                         test_group=test_group)

@app.route('/digital-busking')
def digital_busking():
    """Create a digital tip jar - like busking for online content"""
    
    # Generate unique "camping tip" each time
    camping_tips = [
        "Use dryer lint as a perfect fire starter - free and ultra-lightweight!",
        "Put a headlamp around a water jug for an instant lantern.",
        "Freeze water bottles instead of using ice in your cooler.",
        "Crack eggs into a water bottle before your trip for mess-free camping.",
        "Doritos make excellent emergency fire starters in a pinch!"
    ]
    
    # Support payment options - Buy Me A Coffee, Ko-fi, PayPal, etc.
    payment_options = [
        {
            "name": "Buy Me A Coffee",
            "url": "https://www.buymeacoffee.com/gorillacamping",
            "suggestion": "Buy me a coffee ($5)",
            "image": "/static/images/coffee-icon.png"
        },
        {
            "name": "Ko-fi",
            "url": "https://ko-fi.com/gorillacamping",
            "suggestion": "Buy me a beer ($4)",
            "image": "/static/images/kofi-icon.png"
        },
        {
            "name": "PayPal",
            "url": "https://paypal.me/gorillacamping",
            "suggestion": "Support my next camping trip ($10)",
            "image": "/static/images/paypal-icon.png"
        }
    ]
    
    if db is not None:
        db.page_views.insert_one({
            'page': 'digital_busking',
            'timestamp': datetime.utcnow(),
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })
    
    return render_template('digital_busking.html',
                           camping_tip=random.choice(camping_tips),
                           payment_options=payment_options)

@app.route('/thank-you')
def thank_you():
    """Thank you page after signup"""
    return render_template('thank_you.html')

@app.route('/api/optimize', methods=['POST'])
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
        if db is not None:
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

@app.route('/high-commission-gear')
def high_commission_gear():
    """Products paying 5-10X more than Amazon"""
    items = [
        {
            'name': '4Patriots Food Storage Kit',
            'image': 'https://via.placeholder.com/300x200?text=Emergency+Food',
            'description': 'My #1 recommended survival food for off-grid camping. Lasts 25 years and tastes great!',
            'price': '$197',
            'old_price': '$297',
            'commission': '$49.25 (25%)',  # vs $5.91 on Amazon (3%)
            'affiliate_link': 'https://4patriots.com/products/4week-food?drolid=0001',
            'inventory': random.randint(2, 8)
        },
        {
            'name': 'Bluetti Portable Power Station',
            'image': 'https://via.placeholder.com/300x200?text=Power+Station',
            'description': 'Powers all my gear for viral TikTok content creation. I use it daily at camp.',
            'price': '$299',
            'old_price': '$499',
            'commission': '$74.75 (25%)', # vs $9 on Amazon (3%)
            'affiliate_link': 'https://www.bluettipower.com/products/bluetti-eb70s-portable-power-station?ref=gorillacamping',
            'inventory': random.randint(1, 5)
        }
    ]
    
    return render_template('high_commission.html', items=items)
@app.route('/guerilla-ai-system')
def guerilla_ai_system():
    """AI-powered camping business system"""
    # A/B test price points
    test_group = request.args.get('price') or ('a' if random.random() < 0.5 else 'b')
    price = '$27' if test_group == 'a' else '$37'
    
    # Track this page view with pricing variant
    if db is not None:
        db.page_views.insert_one({
            'page': 'guerilla_ai_system',
            'price_variant': price,
            'timestamp': datetime.utcnow(),
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })
    
    return render_template('guerilla_ai_system.html', price=price)
@app.route('/30day-challenge')
def challenge():
    """30-Day Off-Grid Challenge with sponsored gear"""
    challenge_gear = [
        {
            'day': 1,
            'challenge': 'Set up your base camp with minimal gear',
            'gear': {
                'name': 'Jackery Explorer 240',
                'link': 'https://www.amazon.com/Jackery-Portable-Explorer-Generator-Emergency/dp/B07D29QNMJ?tag=gorillcamping-20',
                'commission': '$6.00'
            }
        },
        {
            'day': 7,
            'challenge': 'Filter water from natural sources',
            'gear': {
                'name': 'LifeStraw Personal Filter',
                'link': 'https://www.amazon.com/LifeStraw-Personal-Filtering-Emergency-Preparedness/dp/B07VMSR74F?tag=gorillcamping-20',
                'commission': '$4.50'
            }
        },
        {
            'day': 15,
            'challenge': 'Create viral content while conserving battery',
            'gear': {
                'name': 'Portable Solar Charger',
                'link': 'https://www.amazon.com/Portable-Charger-25000mAh-Outdoor-Camping/dp/B082NVHJQ9?tag=gorillcamping-20',
                'commission': '$5.25'
            }
        },
        {
            'day': 30,
            'challenge': 'Complete challenge celebration',
            'gear': {
                'name': 'Complete Off-Grid Package',
                'link': 'https://bluetti.com/products/bluetti-ac180-portable-power-station?ref=gorillacamping',
                'commission': '$75.00'
            }
        }
    ]
    
    return render_template('challenge.html', 
                         challenge_days=challenge_gear,
                         signup_bonus="FREE Off-Grid Survival Checklist")
@app.route('/growing-guides')
def growing_guides():
    """Legal growing guides with affiliate products"""
    categories = [
        {
            'name': 'Cannabis Growing',
            'description': 'Legal marijuana cultivation guides for personal use in legal states',
            'affiliate_products': [
                {
                    'name': 'Spider Farmer SF-1000 LED Light',
                    'price': '$159.99',
                    'commission': '$32.00 (20%)',
                    'link': 'https://www.spider-farmer.com/products/sf-1000-led-grow-light/?ref=gorillacamping'
                },
                {
                    'name': 'Advanced Nutrients Bloom, Micro & Grow',
                    'price': '$49.95',
                    'commission': '$10.00 (20%)',
                    'link': 'https://advancednutrients.com/products/bloom-micro-grow/?ref=gorillacamping'
                }
            ]
        },
        {
            'name': 'Mushroom Cultivation',
            'description': 'Research-only mushroom growing techniques and supplies',
            'affiliate_products': [
                {
                    'name': 'All-In-One Mushroom Grow Bag',
                    'price': '$24.99',
                    'commission': '$5.00 (20%)',
                    'link': 'https://northspore.com/products/all-in-one-grow-bags/?ref=gorillacamping'
                },
                {
                    'name': 'Mushroom Growing Starter Kit',
                    'price': '$49.95',
                    'commission': '$10.00 (20%)',
                    'link': 'https://www.midwestgrowkits.com/mushroom-growing-kit.aspx?ref=gorillacamping'
                }
            ]
        }
    ]
    
    legal_disclaimer = "Information provided for educational purposes only. Always follow your local laws regarding cultivation."
    
    return render_template('growing_guides.html',
                         categories=categories,
                         disclaimer=legal_disclaimer)
@app.route('/sms-signup', methods=['POST'])
def sms_signup():
    """SMS marketing system with 90% open rate vs email's 20%"""
    phone = request.form.get('phone')
    if not phone:
        return jsonify({"success": False, "message": "Phone required"})
    
    # Store in DB
    if db is not None:
        db.sms_subscribers.update_one(
            {'phone': phone},
            {'$set': {'phone': phone, 'updated_at': datetime.utcnow()},
             '$setOnInsert': {'created_at': datetime.utcnow()}},
            upsert=True
        )
    
    # Connect to Zapier for SMS (10,000 free tasks/month)
    try:
        requests.post(
            "https://hooks.zapier.com/hooks/catch/YOUR_ID/sms/",
            json={"phone": phone, "source": "website"}
        )
    except Exception as e:
        print(f"Error: {e}")
    
    return jsonify({"success": True})
@app.route('/ai-membership')
def ai_membership():
    """Monthly recurring AI membership"""
    benefits = [
        "Weekly AI-generated camping spot recommendations",
        "Unlimited access to the Gorilla AI gear advisor",
        "Private Discord community with other members",
        "Monthly Q&A livestream with personal advice",
        "Early access to all new gear reviews and deals",
        "Exclusive affiliate opportunities (30%+ commission)",
    ]
    
    testimonials = [
        {"name": "David R.", "text": "Made $341 last month using just the AI gear recommendations!"},
        {"name": "Sarah K.", "text": "The private Discord alone is worth triple the membership fee."}
    ]
    
    return render_template('ai_membership.html', 
                          benefits=benefits,
                          testimonials=testimonials,
                          price="$19")
@app.route('/high-commission-gear')
def high_commission_gear():
    """High-commission products that pay 5-10x more than Amazon"""
    items = [
        {
            'name': '4Patriots Food Storage Kit',
            'image': 'https://via.placeholder.com/300x200?text=Emergency+Food',
            'description': 'Long-term emergency food with 25-year shelf life. Perfect for off-grid camping and prepping.',
            'price': '$197',
            'old_price': '$297',
            'commission': '$49.25 (25%)',  # vs $5.91 on Amazon (3%)
            'affiliate_link': 'https://4patriots.com/products/4week-food?drolid=0001',
            'inventory': random.randint(2, 8)
        },
        {
            'name': 'Solar Generator System',
            'image': 'https://via.placeholder.com/300x200?text=Solar+Gen',
            'description': 'Complete off-grid power solution I use for my TikTok content creation. Powers my devices for 7+ days.',
            'price': '$349',
            'old_price': '$499',
            'commission': '$87.25 (25%)', # vs $10.47 on Amazon (3%)
            'affiliate_link': 'https://www.backwoodsolar.com/products/portable-power?ref=gorilla',
            'inventory': random.randint(1, 6)
        }
    ]
    
    # Track the visit
    if db is not None:
        db.page_views.insert_one({
            'page': 'high_commission',
            'timestamp': datetime.utcnow(),
            'visitor_id': request.cookies.get('visitor_id', 'unknown')
        })
    
    return render_template('high_commission.html', items=items)

@app.route('/sms-signup', methods=['POST'])
def sms_signup():
    """SMS marketing signup (90% open rate vs. email's 20%)"""
    phone = request.form.get('phone')
    if not phone:
        return jsonify({"success": False, "message": "Phone number is required"})
        
    # Store in database
    if db is not None:
        db.sms_subscribers.update_one(
            {'phone': phone},
            {'$set': {'phone': phone, 'updated_at': datetime.utcnow()},
             '$setOnInsert': {'created_at': datetime.utcnow(), 'source': request.referrer}},
            upsert=True
        )
    
    # Connect to Zapier for SMS sending (10,000 free tasks/month)
    try:
        zapier_webhook_url = os.environ.get('ZAPIER_WEBHOOK_URL')
        if zapier_webhook_url:
            requests.post(
                zapier_webhook_url,
                json={"phone": phone, "source": "website"},
                timeout=5
            )
    except Exception as e:
        print(f"Error connecting to Zapier: {e}")
    
    return jsonify({"success": True, "message": "Successfully signed up for SMS alerts!"})

@app.route('/robots.txt')
def robots():
    """SEO: Robots.txt file for better search rankings"""
    r = Response("""
User-agent: *
Allow: /
Sitemap: https://gorillacamping.site/sitemap.xml
    """, mimetype='text/plain')
    return r

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                              'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page with recommendations"""
    top_gear = get_default_gear_items()[:2] if db is None else list(db.gear.find().limit(2))
    return render_template('404.html', recommended_gear=top_gear), 404

# --- SERVER CONFIG ---
if __name__ == '__main__':
    # Use PORT environment variable for Heroku compatibility
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
