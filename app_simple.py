#!/usr/bin/env python3
"""
🦍 SIMPLE GORILLA CAMPING - WORKS PERFECTLY
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gorilla-secret-2025')

@app.route('/')
def home():
    """Homepage with perfect styling"""
    return render_template('index_simple.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Simple chat endpoint"""
    data = request.get_json()
    message = data.get('message', '')
    
    # Simple Guerilla responses
    responses = [
        "Yo! That's a solid question. Here's what I know from living it.",
        "Listen up, because this is real talk from someone who's been there.",
        "Alright, let me give you the straight dope on this.",
        "This is exactly what I've been telling people. Here's the deal.",
        "Perfect question. This is what separates the survivors from the tourists."
    ]
    
    import random
    response = random.choice(responses)
    
    return jsonify({
        'response': response,
        'success': True
    })

@app.route('/gear')
def gear():
    """Gear page"""
    return render_template('gear_simple.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about_simple.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact_simple.html')

@app.route('/blog')
def blog():
    """Blog page"""
    return render_template('blog.html')

@app.route('/social/<platform>')
def social_redirect(platform):
    """Redirect to social media platforms"""
    social_links = {
        'reddit': 'https://www.reddit.com/r/gorillacamping',
        'facebook': 'https://www.facebook.com/gorillacamping',
        'tiktok': 'https://www.tiktok.com/@gorillacamping'
    }
    return redirect(social_links.get(platform, '/'))

@app.route('/affiliate/<product>')
def affiliate(product):
    """Affiliate redirects"""
    links = {
        'jackery': 'https://amzn.to/3QZqX8Y',
        'lifestraw': 'https://amzn.to/3QZqX8Y',
        'food': 'https://4patriots.com/products/4week-food?drolid=0001'
    }
    return redirect(links.get(product, '/'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 