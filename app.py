import os
import uuid
import random
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

# --- FLASK SETUP ---
app = Flask(__name__)
CORS(app, supports_credentials=True)

# --- MONGODB SETUP ---
mongodb_uri = os.environ.get('MONGODB_URI')
client = MongoClient(mongodb_uri)
db = client.get_default_database()

def generate_visitor_id():
    return str(uuid.uuid4())

# --- API ENDPOINTS ---
@app.route('/api/blog-posts', methods=['GET'])
def get_blog_posts():
    """Return all blog posts as JSON"""
    posts = list(db.posts.find({"status": "published"}))
    for post in posts:
        post['_id'] = str(post['_id'])
        post['created_at'] = post['created_at'].strftime('%Y-%m-%d')
    return jsonify(posts)

@app.route('/api/blog-post/<slug>', methods=['GET'])
def get_blog_post(slug):
    """Return a single post by slug"""
    post = db.posts.find_one({'slug': slug, 'status': 'published'})
    if post:
        post['_id'] = str(post['_id'])
        post['created_at'] = post['created_at'].strftime('%Y-%m-%d')
        return jsonify(post)
    return jsonify({'error': 'Post not found'}), 404

@app.route('/api/guerilla-chat', methods=['POST'])
def guerilla_chat():
    """AI chat endpoint (dummy response for now)"""
    data = request.get_json()
    user_message = data.get('message')
    response = "Guerilla says: Used Jackery 240 for 2 years. Still charges my laptop, phone, lights. Lightweight, reliable. Works."
    # TODO: Integrate real AI here
    return jsonify({'response': response})

@app.route('/api/affiliate-click', methods=['POST'])
def affiliate_click():
    """Track affiliate clicks"""
    data = request.get_json()
    product_id = data.get('product_id')
    db.affiliate_clicks.insert_one({
        'product_id': product_id,
        'timestamp': datetime.utcnow(),
        'visitor_id': request.cookies.get('visitor_id', generate_visitor_id())
    })
    return jsonify({'success': True})

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """Add email to subscribers"""
    data = request.get_json()
    email = data.get('email')
    source = data.get('source', 'general')
    if not email or '@' not in email:
        return jsonify({'success': False, 'error': 'Invalid email'}), 400
    existing = db.subscribers.find_one({'email': email})
    if existing:
        return jsonify({'success': False, 'error': 'Already subscribed'})
    db.subscribers.insert_one({
        'email': email,
        'source': source,
        'timestamp': datetime.utcnow(),
        'visitor_id': request.cookies.get('visitor_id', generate_visitor_id()),
        'active': True
    })
    return jsonify({'success': True})

@app.route('/api/gear', methods=['GET'])
def get_gear():
    """Return gear items as JSON"""
    gear_items = [
        {
            'name': 'Jackery Explorer 240',
            'image': 'https://m.media-amazon.com/images/I/41XePYWYlAL._AC_US300_.jpg',
            'description': 'Perfect for keeping devices charged off-grid.',
            'affiliate_id': 'jackery-explorer-240',
            'price': '$199.99',
            'old_price': '$299.99',
            'savings': 'Save $100',
            'rating': 5,
            'badges': ['HOT DEAL', 'BEST VALUE'],
            'specs': ['240Wh', '250W output', 'Multiple ports'],
        },
        {
            'name': 'LifeStraw Personal Water Filter',
            'image': 'https://m.media-amazon.com/images/I/71SYsNwj7hL._AC_UL320_.jpg',
            'description': 'Essential survival gear.',
            'affiliate_id': 'lifestraw-filter',
            'price': '$14.96',
            'old_price': '$19.95',
            'savings': 'Save 25%',
            'rating': 5,
            'badges': ['BESTSELLER'],
            'specs': ['1000L capacity', 'No chemicals', 'Compact'],
        }
    ]
    return jsonify(gear_items)

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
