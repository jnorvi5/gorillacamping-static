from flask import Flask, request, render_template, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('guerilla_chat_live.html')

@app.route('/api/guerilla-chat', methods=['POST'])
def guerilla_chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    # Simple responses for now
    responses = [
        f"🦍 Got it - you asked about: {user_message}. The AI system is coming online soon!",
        f"🦍 Heard you loud and clear about: {user_message}. Full AI launching shortly!",
        f"🦍 Roger that on: {user_message}. Guerilla AI is almost ready to roll!"
    ]
    
    import random
    response = random.choice(responses)
    
    return jsonify({
        'response': response,
        'user_id': 'temp_user'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 