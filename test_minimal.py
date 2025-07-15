#!/usr/bin/env python3
"""
🦍 MINIMAL TEST APP
"""
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "🦍 Gorilla Camping is working!"

@app.route('/test')
def test():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8002) 