#!/usr/bin/env python3
"""
🦍 DEBUG VERSION - Show exact error
"""
from flask import Flask, render_template, current_app, url_for
import traceback

app = Flask(__name__)

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"""
        <h1>500 Error</h1>
        <h2>Error: {str(e)}</h2>
        <pre>{traceback.format_exc()}</pre>
        """, 500

@app.route('/test')
def test():
    return "🦍 Basic app works!"

if __name__ == '__main__':
    app.run(debug=True, port=8007) 