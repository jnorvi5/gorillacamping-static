import os
import re
import random
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session, Response
from flask_compress import Compress
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs
import traceback
import openai
import chromadb
from chromadb.utils import embedding_functions
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'guerilla-camping-secret-2024')

def pro_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('pro_user'):
            flash("You need GorillaCamping Pro for that feature!", "error")
            return redirect(url_for("pro_landing_page"))
        return f(*args, **kwargs)
    return decorated_function

Compress(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "gorillacamping_kb"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=openai.api_key, model_name="text-embedding-3-small")
knowledge_base = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=openai_ef)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600

GOOGLE_ANALYTICS_ID = "G-JPKKPRXX6S"
COOKIEYES_SITE_ID = os.environ.get('COOKIEYES_SITE_ID', 'YOUR_COOKIEYES_ID')
AMAZON_ASSOCIATE_TAG = os.environ.get('AMAZON_TAG', 'gorillacamping-20')
MAILERLITE_API_KEY = os.environ.get('MAILERLITE_API_KEY', '')

# MongoDB connection
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

startup_complete = False

@app.before_request
def create_indexes_once():
    global startup_complete
    if not startup_complete and db is not None:
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
        startup_complete = True

def safe_db_operation(operation, default_return=None):
    try:
        if db is not None:
            return operation()
        else:
            return default_return
    except Exception as e:
        print(f"Database operation failed: {e}")
        return default_return

def track_user_consent(consent_data, user_info=None):
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

def get_recent_posts(limit=5):
    def fetch_posts():
        return list(db.posts.find({"status": "published"}).sort("date", -1).limit(limit))
    posts = safe_db_operation(fetch_posts, [])
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

def get_posts_paginated(page=1, per_page=12):
    def fetch_paginated():
        skip = (page - 1) * per_page
        posts = list(db.posts.find({"status": "published"}).sort("date", -1).skip(skip).limit(per_page))
        total = db.posts.count_documents({"status": "published"})
        return posts, total
    result = safe_db_operation(fetch_paginated, ([], 0))
    return result

def track_affiliate_click(product_id, source_page, user_consent=None):
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

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.route("/api/optimize", methods=['POST'])
def generative_ai_assistant():
    data = request.json
    user_query = data.get("query", "I need some camping advice.")
    results = knowledge_base.query(query_texts=[user_query], n_results=5)
    context = "\n\n---\n\n".join(results['documents'][0])
    system_prompt = (
        "You are the GorillaCamping AI assistant. You are an expert in budget, off-grid, and 'guerilla' style camping. "
        "Your tone is direct, knowledgeable, and a bit rugged, like a seasoned veteran camper. "
        "Use ONLY the provided context below to answer the user's question. Do not make up information. "
        "If the context doesn't contain the answer, say 'I don't have that information in my knowledge base, but here's a general tip...'"
    )
    try:
        completion = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is my question: {user_query}\n\nHere is the relevant context from the GorillaCamping knowledge base:\n\n{context}"}
            ]
        )
        ai_response = completion.choices[0].message.content
        gear_links = recommend_gear_links(user_query, ai_response)
        db.ai_logs.insert_one({
            "question": user_query,
            "ai_response": ai_response,
            "timestamp": datetime.utcnow(),
            "user_agent": request.headers.get('User-Agent'),
            "ip_hash": hash(request.remote_addr) if request.remote_addr else None,
        })
        return jsonify({"success": True, "response": ai_response + gear_links})
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return jsonify({"success": False, "message": "The AI brain is currently offline. Please try again later."})

def recommend_gear_links(user_query, ai_response):
    if not db:
        return ""
    keywords = set(user_query.lower().split())
    gear_matches = []
    for gear in db.gear.find({"active": True}):
        gear_text = (gear["name"] + " " + gear.get("description", "")).lower()
        if any(word in gear_text for word in keywords):
            gear_matches.append(gear)
    links = [
        f"<br><a href='/go/{g['affiliate_id']}' target='_blank' rel='noopener sponsored'>👉 {g['name']} (My Pick)</a>"
        for g in gear_matches[:2]
    ]
    if links:
        return "<br><br><b>Recommended for you:</b> " + " ".join(links)
    return ""

@app.route("/api/feedback", methods=["POST"])
def user_feedback():
    data = request.json
    db.feedback.insert_one({
        "question": data.get("question"),
        "ai_response": data.get("ai_response"),
        "feedback": data.get("feedback"),
        "timestamp": datetime.utcnow(),
        "user_agent": request.headers.get('User-Agent'),
        "ip_hash": hash(request.remote_addr) if request.remote_addr else None,
    })
    return jsonify({"success": True})

@app.route("/")
def index():
    latest_posts = get_recent_posts(6)
    meta_description = "Guerilla camping gear reviews, budget outdoor equipment, and off-grid survival tips. Real advice from someone living the lifestyle. Save money, make adventures happen."
    meta_keywords = "guerilla camping, budget camping gear, stealth camping, off-grid living, camping gear reviews, amazon camping deals, cheap outdoor gear"
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

@app.route('/pro')
def pro_landing_page():
    return render_template("pro_landing.html")  # Make this page: features, Stripe Checkout button, testimonials, etc.

@app.route("/blog/<slug>")
def post(slug):
    def fetch_post():
        return db.posts.find_one({"slug": slug, "status": "published"})
    post_data = safe_db_operation(fetch_post)
    if not post_data:
        demo_posts = {
            "budget-camping-gear-under-20-amazon": {
                "title": "Best Budget Camping Gear Under $20 (Amazon Finds 2024)",
                "content": "...",
                "date": datetime.now() - timedelta(days=1),
                "category": "Budget Gear",
                "slug": slug,
                "affiliate_ready": True,
                "meta_description": "...",
                "featured_products": ["poncho", "lifestraw", "mylar-bag"]
            },
            "stealth-camping-essentials-gear": {
                "title": "Stealth Camping Essentials: 5 Must-Have Items",
                "content": "...",
                "date": datetime.now() - timedelta(days=3),
                "category": "Stealth Tactics",
                "slug": slug,
                "affiliate_ready": True,
                "meta_description": "...",
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

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            subject = request.form.get("subject", "").strip()
            message = request.form.get("message", "").strip()
            if not all([name, email, subject, message]):
                flash("All fields are required! Don't leave money on the table.", "error")
                return redirect(url_for("contact"))
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                flash("Please enter a valid email address.", "error")
                return redirect(url_for("contact"))
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
            # Only try to update pro status if logged in
            try:
                if "email" in session:
                    db.users.update_one({"email": session["email"]}, {
                        "$set": {"is_pro": True, "pro_since": datetime.utcnow()}
                    })
                    session["pro_user"] = True
            except Exception:
                pass
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
    meta_description = "Contact Gorilla Camping for gear reviews, brand collaborations, and guerilla camping advice. Let's make money together!"
    meta_keywords = "contact gorilla camping, brand collaboration, gear review, affiliate partnership, camping blog"
    return render_template("contact.html", 
                         meta_description=meta_description,
                         meta_keywords=meta_keywords,
                         page_type="contact")

@app.route("/as-is")
def as_is():
    meta_description = "Gorilla Camping affiliate marketing disclaimer, terms of use, and product recommendations policy. Guerilla-style transparency."
    meta_keywords = "affiliate disclaimer, as-is terms, gorilla camping legal, product reviews disclaimer"
    return render_template("as_is.html",
                         meta_description=meta_description,
                         meta_keywords=meta_keywords,
                         page_type="legal")

@app.route("/privacy")
def privacy():
    meta_description = "Gorilla Camping privacy policy. How we protect your data while helping you master guerilla camping."
    meta_keywords = "privacy policy, data protection, gorilla camping privacy"
    return render_template("privacy.html",
                         meta_description=meta_description,
                         meta_keywords=meta_keywords,
                         page_type="legal")

@app.route("/go/<product_id>")
def affiliate_redirect(product_id):
    user_consent = session.get('cookie_consent', {})
    track_affiliate_click(product_id, request.referrer or 'direct', user_consent)
    affiliate_links = {
        "jackery-explorer-240": "https://amzn.to/43ZFIvfV",
        "coleman-stove": "https://amzn.to/44eem7c", 
        "lifestraw-filter": "https://amzn.to/4dZjAae",
        "leatherman-wave": "https://amzn.to/4k3C5ff",
        "survival-kit": "https://amzn.to/3GfUirZ",
        "budget-sleeping-bag": "https://amzn.to/3HYhjjG",
        "viral-camping-bundle": "https://amzn.to/4niYcRo",
        "phone-tripod": "https://amzn.to/4eg8bCZ",
        "power-bank": "https://amzn.to/4l8bS04",
        "led-light": "https://amzn.to/45zljks",
        "popup-tent": "https://amzn.to/4lg5kfE",
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

@app.route("/category/<category_name>")
def category(category_name):
    def fetch_category_posts():
        return list(db.posts.find({"category": category_name, "status": "published"}).sort("date", -1).limit(20))
    posts = safe_db_operation(fetch_category_posts, [])
    meta_description = f"Guerilla camping guides about {category_name}. Real advice from someone living the lifestyle. Budget-friendly {category_name} tips."
    meta_keywords = f"guerilla camping {category_name}, camping {category_name}, off-grid {category_name}, budget {category_name}"
    return render_template("category.html", 
                         posts=posts, 
                         category=category_name,
                         meta_description=meta_description,
                         meta_keywords=meta_keywords,
                         page_type="category")

@app.route('/api/consent-update', methods=['POST'])
def consent_update():
    try:
        consent_data = request.json or {}
        session['cookie_consent'] = consent_data
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

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    pages = []
    static_pages = [
        ('index', 1.0, 'daily'),
        ('blog', 0.9, 'daily'),
        ('gear', 0.95, 'weekly'),
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
    demo_posts = ['budget-camping-gear-under-20-amazon', 'stealth-camping-essentials-gear']
    for slug in demo_posts:
        pages.append({
            'loc': url_for('post', slug=slug, _external=True),
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'priority': 0.9,
            'changefreq': 'weekly'
        })
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = Response(sitemap_xml, mimetype='application/xml')
    return response

@app.route('/robots.txt')
def robots():
    return Response(
        f"User-agent: *\nAllow: /\nSitemap: {url_for('sitemap', _external=True)}\n",
        mimetype='text/plain'
    )

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email', '').strip()
    name = request.form.get('name', '').strip()
    if not email:
        return jsonify({"success": False, "message": "Email is required!"})
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({"success": False, "message": "Please enter a valid email address."})
    def save_subscriber():
        subscriber_data = {
            "email": email,
            "name": name,
            "timestamp": datetime.utcnow(),
            "status": "active",
            "source": request.referrer or "direct",
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get('User-Agent'),
            "revenue_potential": "high",
            "tags": ["guerilla_camping", "budget_gear"]
        }
        db.subscribers.insert_one(subscriber_data)
        return True
    saved = safe_db_operation(save_subscriber, False)
    if saved:
        return jsonify({
            "success": True, 
            "message": "🎯 Welcome to the guerilla camping tribe! Check your email for exclusive gear deals! 🏕️"
        })
    else:
        return jsonify({"success": False, "message": "Something went wrong. Try again!"})

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
