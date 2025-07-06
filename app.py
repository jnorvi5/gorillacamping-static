import os
import re
import random
import requests
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session, Response, send_file
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs
import traceback

# Import Azure services
from azure_config import (
    azure_cosmos, azure_blob, azure_keyvault, azure_insights,
    get_secret, get_database_client, log_to_azure
)

# --- FLASK SETUP ---
app = Flask(__name__)
app.secret_key = get_secret('SECRET_KEY', 'SECRET_KEY') or 'guerilla-camping-secret-2024'

# --- HANDLE OPTIONAL DEPENDENCIES ---
try:
    from flask_compress import Compress
    compress = Compress()
    compress.init_app(app)
    print("✅ Flask-Compress initialized")
except ImportError:
    print("⚠️ flask_compress not installed, continuing without compression")

try:
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    
    # --- CHROMADB + HUGGINGFACE EMBEDDINGS ---
    CHROMA_PATH = "./chroma_db"
    COLLECTION_NAME = "gorillacamping_kb"
    hf_ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    knowledge_base = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=hf_ef)
    print("✅ ChromaDB initialized")
except ImportError:
    print("⚠️ ChromaDB not installed, continuing without knowledge base")
    knowledge_base = None

try:
    import google.generativeai as genai
    
    # --- GEMINI AI SETUP ---
    gemini_api_key = get_secret('GEMINI_API_KEY', 'GEMINI_API_KEY')
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        print("✅ Google Generative AI initialized")
    else:
        print("⚠️ GEMINI_API_KEY not set, AI features disabled")
except ImportError:
    print("⚠️ google.generativeai not installed, continuing without AI features")
    genai = None

def ask_gemini(user_query, context=""):
    if not genai:
        return "AI services are currently unavailable."
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content([{"role":"user", "parts":[context + "\n\n" + user_query]}])
    return response.text

# --- DB SETUP ---
# Try Azure Cosmos DB first, fallback to MongoDB
azure_db = get_database_client()
db = None
db_type = "none"

if azure_db and azure_db.is_available():
    # Use Azure Cosmos DB
    db = azure_db
    db_type = "azure_cosmos"
    print("✅ Using Azure Cosmos DB")
else:
    # Fallback to MongoDB
    try:
        mongodb_uri = get_secret('MONGODB_URI', 'MONGODB_URI') or get_secret('MONGO_URI', 'MONGO_URI')
        if mongodb_uri:
            client = MongoClient(mongodb_uri)
            db = client.get_default_database()
            db.command('ping')
            db_type = "mongodb"
            print("✅ MongoDB connected successfully!")
        else:
            print("⚠️ No database URI found - running in demo mode")
            db = None
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        db = None

# --- DATABASE ADAPTER FUNCTIONS ---
def get_collection(collection_name):
    """Get database collection/container with abstraction for both MongoDB and Cosmos DB"""
    if not db:
        return None
    
    if db_type == "azure_cosmos":
        return db.get_container(collection_name)
    elif db_type == "mongodb":
        return getattr(db, collection_name)
    return None

def find_documents(collection_name, query=None, sort=None, limit=None):
    """Find documents with abstraction for both MongoDB and Cosmos DB"""
    collection = get_collection(collection_name)
    if not collection:
        return []
    
    try:
        if db_type == "azure_cosmos":
            # Cosmos DB SQL query
            if query is None:
                sql_query = "SELECT * FROM c"
            else:
                # Convert MongoDB-style query to Cosmos DB SQL (simplified)
                sql_query = "SELECT * FROM c"
                if query:
                    conditions = []
                    for key, value in query.items():
                        if key == '_id':
                            conditions.append(f"c.id = '{value}'")
                        elif isinstance(value, dict) and '$ne' in value:
                            conditions.append(f"c.{key} != '{value['$ne']}'")
                        else:
                            conditions.append(f"c.{key} = '{value}'")
                    if conditions:
                        sql_query += " WHERE " + " AND ".join(conditions)
            
            if sort:
                # Add ORDER BY for sort (simplified)
                sort_field, sort_order = next(iter(sort))
                direction = "DESC" if sort_order == -1 else "ASC"
                sql_query += f" ORDER BY c.{sort_field} {direction}"
            
            items = list(collection.query_items(query=sql_query, enable_cross_partition_query=True))
            
            if limit:
                items = items[:limit]
            
            # Convert Cosmos DB format to MongoDB-like format
            for item in items:
                if 'id' in item:
                    item['_id'] = item['id']
            
            return items
            
        elif db_type == "mongodb":
            # MongoDB query
            cursor = collection.find(query or {})
            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
    except Exception as e:
        print(f"❌ Error querying {collection_name}: {e}")
        return []
    
    return []

def find_one_document(collection_name, query):
    """Find single document with abstraction for both MongoDB and Cosmos DB"""
    collection = get_collection(collection_name)
    if not collection:
        return None
    
    try:
        if db_type == "azure_cosmos":
            # Convert query for Cosmos DB
            if '_id' in query:
                # Use point read for better performance
                try:
                    return collection.read_item(item=query['_id'], partition_key=query['_id'])
                except:
                    # Fallback to query
                    items = find_documents(collection_name, query, limit=1)
                    return items[0] if items else None
            else:
                items = find_documents(collection_name, query, limit=1)
                return items[0] if items else None
                
        elif db_type == "mongodb":
            return collection.find_one(query)
    except Exception as e:
        print(f"❌ Error finding document in {collection_name}: {e}")
        return None
    
    return None

def insert_document(collection_name, document):
    """Insert document with abstraction for both MongoDB and Cosmos DB"""
    collection = get_collection(collection_name)
    if not collection:
        return None
    
    try:
        if db_type == "azure_cosmos":
            # Ensure document has an id field for Cosmos DB
            if '_id' not in document and 'id' not in document:
                import uuid
                document['id'] = str(uuid.uuid4())
            elif '_id' in document:
                document['id'] = str(document['_id'])
            
            return collection.create_item(body=document)
            
        elif db_type == "mongodb":
            result = collection.insert_one(document)
            return result.inserted_id
    except Exception as e:
        print(f"❌ Error inserting document into {collection_name}: {e}")
        return None

def update_document(collection_name, query, update_data, upsert=False):
    """Update document with abstraction for both MongoDB and Cosmos DB"""
    collection = get_collection(collection_name)
    if not collection:
        return None
    
    try:
        if db_type == "azure_cosmos":
            # For Cosmos DB, we need to read, modify, then replace
            existing = find_one_document(collection_name, query)
            if existing:
                # Apply updates
                if '$set' in update_data:
                    existing.update(update_data['$set'])
                if '$setOnInsert' in update_data and not existing:
                    existing.update(update_data['$setOnInsert'])
                
                return collection.replace_item(item=existing['id'], body=existing)
            elif upsert:
                # Create new document
                new_doc = {}
                if '$set' in update_data:
                    new_doc.update(update_data['$set'])
                if '$setOnInsert' in update_data:
                    new_doc.update(update_data['$setOnInsert'])
                new_doc.update(query)
                return insert_document(collection_name, new_doc)
                
        elif db_type == "mongodb":
            return collection.update_one(query, update_data, upsert=upsert)
    except Exception as e:
        print(f"❌ Error updating document in {collection_name}: {e}")
        return None

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/blog')
def blog():
    posts = []
    if db:
        try:
            posts = find_documents('posts', sort=[('created_at', -1)])
        except Exception as e:
            print(f"Error fetching posts: {e}")
            log_to_azure(f"Error fetching posts: {e}", "ERROR")
    return render_template('blog.html', posts=posts)

@app.route('/post/<slug>')
def post(slug):
    if db:
        post = find_one_document('posts', {'slug': slug})
        if post:
            related_posts = find_documents('posts', {'_id': {'$ne': post['_id']}}, limit=3)
            return render_template('post.html', post=post, related_posts=related_posts)
    return redirect(url_for('blog'))

@app.route('/gear')
def gear():
    gear_items = []
    # Add some hardcoded gear items if we don't have a DB
    gear_from_db = find_documents('gear') if db else []
    if not db or not gear_from_db:
        gear_items = [
            {
                'name': 'Jackery Explorer 240',
                'image': 'https://m.media-amazon.com/images/I/41XePYWYlAL._AC_US300_.jpg',
                'description': 'Perfect for keeping devices charged off-grid',
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
                'description': 'Essential survival gear that filters 99.9999% of waterborne bacteria',
                'affiliate_id': 'lifestraw-filter',
                'price': '$14.96',
                'old_price': '$19.95',
                'savings': 'Save 25%',
                'rating': 5,
                'badges': ['BESTSELLER'],
                'specs': ['1000L capacity', 'No chemicals', 'Compact']
            }
        ]
    else:
        gear_items = gear_from_db
    return render_template('gear.html', gear_items=gear_items)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if db:
            insert_document('contacts', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'created_at': datetime.utcnow()
            })
        
        flash('Message received! We will get back to you soon.', 'success')
        log_to_azure(f"Contact form submitted by {email}")
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/affiliate/<product_id>')
def affiliate_redirect(product_id):
    affiliate_urls = {
        'jackery-explorer-240': 'https://www.amazon.com/Jackery-Portable-Explorer-Generator-Emergency/dp/B07D29QNMJ?&linkCode=ll1&tag=gorillcamping-20',
        'lifestraw-filter': 'https://www.amazon.com/LifeStraw-Personal-Filtering-Emergency-Preparedness/dp/B07VMSR74F?&linkCode=ll1&tag=gorillcamping-20'
    }
    
    url = affiliate_urls.get(product_id, 'https://www.amazon.com/?&linkCode=ll2&tag=gorillcamping-20')
    
    # Track click in database
    if db:
        insert_document('affiliate_clicks', {
            'product_id': product_id,
            'timestamp': datetime.utcnow(),
            'user_agent': request.headers.get('User-Agent'),
            'referrer': request.referrer
        })
    
    log_to_azure(f"Affiliate click: {product_id}")
    return redirect(url)

@app.route('/social/<platform>')
def social_redirect(platform):
    social_urls = {
        'reddit': 'https://www.reddit.com/r/gorillacamping',
        'facebook': 'https://www.facebook.com/profile.php?id=61577334442896',
        'tiktok': 'https://www.tiktok.com/@gorillacamping'
    }
    
    url = social_urls.get(platform, 'https://www.reddit.com/r/gorillacamping')
    
    # Track social click
    if db:
        insert_document('social_clicks', {
            'platform': platform,
            'timestamp': datetime.utcnow(),
            'user_agent': request.headers.get('User-Agent')
        })
    
    log_to_azure(f"Social click: {platform}")
    return redirect(url)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'})
    
    # Store in our own DB
    if db:
        update_document('subscribers',
            {'email': email},
            {'$set': {'email': email, 'updated_at': datetime.utcnow()}, 
             '$setOnInsert': {'created_at': datetime.utcnow()}},
            upsert=True
        )
    
    log_to_azure(f"New subscriber: {email}")
    return jsonify({'success': True, 'message': 'Subscribed successfully'})

@app.route('/guerilla-camping-bible')
def ebook():
    return render_template('ebook.html')

@app.route('/sms-signup', methods=['POST'])
def sms_signup():
    phone = request.form.get('phone')
    if not phone:
        return jsonify({"success": False})
        
    # Use pre-paid Twilio credits from Student Pack
    try:
        requests.post('https://hooks.zapier.com/hooks/catch/YOUR_ZAPHOOK_ID/', 
                    json={"phone": phone})
        return jsonify({"success": True})
    except:
        return jsonify({"success": False})

@app.route("/api/optimize", methods=['POST'])
def generative_ai_assistant():
    # Limit: 3 free queries per session unless Pro
    if not session.get("pro_user"):
        session['queries'] = session.get('queries', 0) + 1
        if session['queries'] > 3:
            return jsonify({"success": False, "message": "Upgrade to Pro for unlimited AI!"})
    
    data = request.json
    user_query = data.get("query", "I need some camping advice.")
    
    # 1. RAG: Retrieve context from your knowledge base using HuggingFace embeddings
    context = ""
    if knowledge_base:
        try:
            results = knowledge_base.query(query_texts=[user_query], n_results=5)
            context = "\n\n---\n\n".join(results['documents'][0]) if results['documents'] else ""
        except Exception as e:
            print(f"❌ Knowledge base error: {e}")
    
    # 2. Generate response
    try:
        ai_response = ask_gemini(user_query, context)
        # Optionally recommend gear based on AI answer
        gear_links = ""
        
        if db:
            insert_document('ai_logs', {
                "question": user_query,
                "ai_response": ai_response,
                "timestamp": datetime.utcnow(),
                "user_agent": request.headers.get('User-Agent'),
                "ip_hash": hash(request.remote_addr) if request.remote_addr else None,
            })
        
        log_to_azure(f"AI query processed: {user_query[:50]}...")
        return jsonify({"success": True, "response": ai_response + gear_links})
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return jsonify({"success": False, "message": "The AI brain is currently offline. Please try again later."})

@app.route('/tools')
def tools():
    # Create a tools comparison site using DO credit
    # Each tool has affiliate links
    return render_template('tools.html')

@app.route('/infographic/<name>')
def infographic(name):
    # Track downloads
    if db:
        insert_document('downloads', {
            "infographic": name,
            "timestamp": datetime.utcnow()
        })
    
    log_to_azure(f"Infographic downloaded: {name}")
    try:
        return send_file(f'static/infographics/{name}.pdf')
    except:
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
