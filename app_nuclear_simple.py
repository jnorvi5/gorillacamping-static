import os
from flask import Flask, render_template, jsonify, request
import random

# Simple Flask app
app = Flask(__name__)
app.secret_key = 'simple-key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/guerilla-chat', methods=['POST'])
def guerilla_chat():
    """Super simple AI chat"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        # Simple responses based on keywords
        if 'power' in user_message.lower() or 'battery' in user_message.lower():
            response = "For power, I recommend the Jackery Explorer 240. It's what I use for all my devices when camping."
        elif 'water' in user_message.lower():
            response = "LifeStraw is my go-to water filter. Lightweight and reliable for any water source."
        elif 'food' in user_message.lower():
            response = "4Patriots emergency food kit is solid - 25 year shelf life and actually tastes decent."
        else:
            responses = [
                "Hell yeah! What specific gear are you looking for?",
                "I got you covered. What's your camping situation?",
                "Badass question! Tell me more about your setup.",
                "That's what I'm here for. What do you need help with?",
                "Good thinking! What's your biggest camping challenge?"
            ]
            response = random.choice(responses)
        
        return jsonify({
            'response': response,
            'recommendations': []
        })
        
    except Exception as e:
        return jsonify({
            'response': "Something went sideways. Try asking again.",
            'recommendations': []
        })

@app.route('/gear')
def gear():
    return render_template('gear.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False) 