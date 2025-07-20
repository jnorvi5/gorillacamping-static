#!/usr/bin/env python3
"""
🦍 GORILLA CAMPING - CLEAN & SIMPLE
"""
from flask import Flask, render_template, jsonify, request, redirect
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gorilla-secret-2025')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gear')
def gear():
    return render_template('gear.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    
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

@app.route('/affiliate/<product>')
def affiliate(product):
    links = {
        'jackery': 'https://amzn.to/3QZqX8Y',
        'lifestraw': 'https://amzn.to/3QZqX8Y',
        'food': 'https://4patriots.com/products/4week-food?drolid=0001'
    }
    return redirect(links.get(product, '/'))

@app.route('/social/<platform>')
def social_redirect(platform):
    social_links = {
        'reddit': 'https://www.reddit.com/r/gorillacamping',
        'facebook': 'https://www.facebook.com/gorillacamping',
        'tiktok': 'https://www.tiktok.com/@gorillacamping'
    }
    return redirect(social_links.get(platform, '/'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 