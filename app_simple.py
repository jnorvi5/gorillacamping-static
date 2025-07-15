#!/usr/bin/env python3
"""
🦍 GORILLA CAMPING - SIMPLE AZURE VERSION
"""
import os
import random
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gorilla-secret-2025')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/guerilla-chat', methods=['POST'])
def guerilla_chat():
    """Simple Guerilla AI chat with keyword responses"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data.get('message', '').lower()
        
        # Guerilla responses based on keywords
        if any(word in user_message for word in ['power', 'battery', 'charging', 'electricity']):
            response = "🦍 For power, I swear by the Jackery Explorer 240. It's what I use for all my devices when I'm out there making content. Reliable as hell."
        elif any(word in user_message for word in ['water', 'drink', 'filter', 'hydration']):
            response = "🦍 LifeStraw is my go-to water filter. Lightweight, reliable, and has saved my ass more times than I can count. Essential gear."
        elif any(word in user_message for word in ['food', 'eat', 'meal', 'cook', 'emergency']):
            response = "🦍 4Patriots emergency food kit is solid - lasts 25 years and actually tastes decent. Perfect for long camping trips or emergencies."
        elif any(word in user_message for word in ['tent', 'shelter', 'sleep', 'weather']):
            response = "🦍 Coleman tents are bulletproof. I've used mine in everything from desert heat to mountain storms. Get one that's rated for worse weather than you expect."
        elif any(word in user_message for word in ['money', 'income', 'revenue', 'business']):
            response = "🦍 Camping can pay for itself! I make money through affiliate gear recommendations, YouTube videos from cool locations, and selling my camping guides. The key is authentic content."
        elif any(word in user_message for word in ['youtube', 'video', 'content', 'social']):
            response = "🦍 Best camping content? Show the real stuff - setup struggles, gear failures, awesome sunrises. People connect with authentic experiences, not perfect Instagram shots."
        else:
            # General Guerilla responses
            responses = [
                "🦍 Hell yeah! What specific gear are you looking for? I've tested pretty much everything.",
                "🦍 I got you covered. What's your camping situation? Car camping, backpacking, or full-on survival mode?",
                "🦍 Badass question! Tell me more about your setup and I'll help you optimize it.",
                "🦍 That's what I'm here for. What's your biggest camping challenge right now?",
                "🦍 Good thinking! What kind of environment are you camping in? Desert, mountains, forests?",
                "🦍 I've been there. What's your experience level? New to camping or already have some gear?",
                "🦍 Smart question! Are you looking for budget gear or ready to invest in quality stuff?",
                "🦍 Love it! What's your main goal - comfort, survival, or making money while camping?"
            ]
            response = random.choice(responses)
        
        return jsonify({
            'response': response,
            'user_id': f"user_{int(random.random() * 10000)}"
        })
        
    except Exception as e:
        return jsonify({
            'response': "🦍 Something went sideways. Try asking again - maybe rephrase your question?",
            'error': str(e)
        }), 500

@app.route('/chat')
def chat():
    return render_template('guerilla_chat_live.html')

@app.route('/gear')
def gear():
    return render_template('gear.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/social/<platform>')
def social_redirect(platform):
    """Redirect to social media platforms"""
    social_links = {
        'reddit': 'https://www.reddit.com/r/gorillacamping',
        'facebook': 'https://www.facebook.com/gorillacamping',
        'tiktok': 'https://www.tiktok.com/@gorillacamping'
    }
    return f'<script>window.location.href="{social_links.get(platform, "/")}";</script>'

@app.route('/affiliate/<product_id>')
def affiliate_redirect(product_id):
    """Redirect to affiliate links"""
    affiliate_links = {
        'jackery-explorer-240': 'https://amzn.to/3jackery240',
        'lifestraw-filter': 'https://amzn.to/3lifestraw',
        '4patriots-food': 'https://4patriots.com/products/4week-food',
        'coleman-tent': 'https://amzn.to/3coleman'
    }
    
    link = affiliate_links.get(product_id, 'https://gorillacamping.com')
    return f'<script>window.location.href="{link}";</script>'

@app.route('/robots.txt')
def robots():
    return '''User-agent: *
Allow: /
Sitemap: https://gorillacamping.azurewebsites.net/sitemap.xml'''

@app.route('/sitemap.xml')
def sitemap():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://gorillacamping.azurewebsites.net/</loc></url>
    <url><loc>https://gorillacamping.azurewebsites.net/chat</loc></url>
    <url><loc>https://gorillacamping.azurewebsites.net/gear</loc></url>
    <url><loc>https://gorillacamping.azurewebsites.net/about</loc></url>
</urlset>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False) 