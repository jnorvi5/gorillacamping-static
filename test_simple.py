#!/usr/bin/env python3
"""
🦍 MINIMAL TEST - Find the exact error
"""
from flask import Flask, render_template, current_app, url_for

app = Flask(__name__)

# Add CDN filter
@app.template_filter('cdn')
def cdn_filter(filename):
    return url_for('static', filename=filename)

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/test')
def test():
    return "🦍 Basic app works!"

if __name__ == '__main__':
    app.run(debug=True, port=8006) 