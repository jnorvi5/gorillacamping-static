#!/usr/bin/env python3
"""
🦍 DEBUG VERSION
"""
import os
import random
from flask import Flask, render_template, jsonify, request, current_app, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gorilla-secret-2025')

# Add CDN filter
@app.template_filter('cdn')
def cdn_filter(filename):
    cdn_url = current_app.config.get('CDN_URL')
    if cdn_url:
        return f"{cdn_url.rstrip('/')}/{filename.lstrip('/')}"
    return url_for('static', filename=filename)

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/test')
def test():
    return "�� App is working!"

@app.route('/social/<platform>')
def social_redirect(platform):
    social_links = {
        'reddit': 'https://www.reddit.com/r/gorillacamping',
        'facebook': 'https://www.facebook.com/gorillacamping',
        'tiktok': 'https://www.tiktok.com/@gorillacamping'
    }
    return f'<script>window.location.href="{social_links.get(platform, "/")}";</script>'

if __name__ == '__main__':
    app.run(debug=True, port=8004) 