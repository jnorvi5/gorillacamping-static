#!/usr/bin/env python3
"""
🦍 Emergency Gorilla Camping App - Guaranteed to work!
Simplified but includes all the optimized chat features
"""

from flask import Flask, render_template, request, jsonify
import os
import random
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'gorilla-camping-2025'

# Simple in-memory storage for now
chat_sessions = {}

@app.route('/')
def home():
    """Homepage"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>🦍 Gorilla Camping - AI-Powered Off-Grid Living</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #0a0a0a, #1a2f1a); 
            color: white; 
            margin: 0; 
            padding: 20px; 
        }
        .header { text-align: center; margin-bottom: 40px; }
        .hero h1 { 
            color: #00ff00; 
            font-size: 2.5em; 
            text-shadow: 0 0 20px rgba(0,255,0,0.5); 
            margin: 0; 
        }
        .hero p { 
            font-size: 1.2em; 
            color: #88cc88; 
            margin: 10px 0 30px 0; 
        }
        .chat-preview {
            max-width: 600px;
            margin: 40px auto;
            padding: 30px;
            background: rgba(0,0,0,0.8);
            border-radius: 15px;
            border: 2px solid #2d5a2d;
            text-align: center;
        }
        .demo-conversation {
            background: rgba(26,26,26,0.8);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: left;
        }
        .demo-user { 
            background: #4a8a4a; 
            padding: 10px 15px; 
            border-radius: 15px; 
            margin: 10px 0; 
            text-align: right; 
        }
        .demo-ai { 
            background: #1a1a1a; 
            padding: 10px 15px; 
            border-radius: 15px; 
            margin: 10px 0; 
            border: 1px solid #2d5a2d; 
            color: #00ff00; 
        }
        .chat-button {
            display: inline-block;
            padding: 20px 40px;
            background: linear-gradient(135deg, #4a8a4a, #2d5a2d);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-size: 1.2em;
            font-weight: bold;
            box-shadow: 0 5px 15px rgba(0,255,0,0.3);
            transition: all 0.3s ease;
        }
        .chat-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,255,0,0.5);
            text-decoration: none;
            color: white;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        .feature {
            background: rgba(26,26,26,0.8);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #2d5a2d;
        }
        .feature h3 { color: #00ff00; margin-top: 0; }
    </style>
</head>
<body>
    <div class="header">
        <div class="hero">
            <h1>🦍 GORILLA CAMPING</h1>
            <p>AI-Powered Off-Grid Living & Gear Recommendations</p>
        </div>
    </div>

    <div class="chat-preview">
        <h2>🦍 Chat with Guerilla the Gorilla</h2>
        <p>Get authentic advice from an AI trained on real off-grid experience</p>
        
        <div class="demo-conversation">
            <div class="demo-user">"What's the best power setup for van life?"</div>
            <div class="demo-ai">🦍 "Used Jackery 240 for 2 years. Still charges my laptop, phone, lights. Lightweight, reliable. Works."</div>
        </div>
        
        <a href="/chat" class="chat-button">Start Chatting Now →</a>
    </div>

    <div class="features">
        <div class="feature">
            <h3>🤖 Smart AI Assistant</h3>
            <p>Authentic responses based on real camping experience, not generic advice.</p>
        </div>
        <div class="feature">
            <h3>⚡ Instant Responses</h3>
            <p>Get answers in seconds, not minutes. Optimized for speed and accuracy.</p>
        </div>
        <div class="feature">
            <h3>🎯 Gear Recommendations</h3>
            <p>Smart product suggestions based on your specific needs and setup.</p>
        </div>
        <div class="feature">
            <h3>💰 Make Money Camping</h3>
            <p>Learn how to earn income while living off-grid through proven strategies.</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/chat')
def chat():
    """Chat interface"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>🦍 Chat with Guerilla</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0a0a0a, #1a2f1a);
            height: 100vh;
            overflow: hidden;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(0,0,0,0.8);
            border-left: 1px solid #2d5a2d;
            border-right: 1px solid #2d5a2d;
        }
        .chat-header {
            background: linear-gradient(90deg, #1a2f1a, #2d5a2d);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #4a8a4a;
        }
        .chat-header h1 {
            color: #00ff00;
            font-size: 1.8em;
            margin-bottom: 5px;
            text-shadow: 0 0 10px rgba(0,255,0,0.5);
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: rgba(0,0,0,0.9);
        }
        .message {
            margin-bottom: 20px;
            opacity: 0;
            animation: fadeIn 0.3s ease-in forwards;
        }
        @keyframes fadeIn { to { opacity: 1; } }
        .user-message {
            display: flex;
            justify-content: flex-end;
        }
        .ai-message {
            display: flex;
            justify-content: flex-start;
        }
        .message-content {
            max-width: 70%;
            padding: 15px 20px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.4;
        }
        .user-message .message-content {
            background: linear-gradient(135deg, #4a8a4a, #2d5a2d);
            color: white;
            border-bottom-right-radius: 5px;
        }
        .ai-message .message-content {
            background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
            color: #00ff00;
            border: 1px solid #2d5a2d;
            border-bottom-left-radius: 5px;
            position: relative;
        }
        .ai-message .message-content::before {
            content: "🦍";
            position: absolute;
            left: -30px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
            background: #1a1a1a;
            border-radius: 50%;
            width: 25px;
            height: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #2d5a2d;
        }
        .chat-input-container {
            padding: 20px;
            background: linear-gradient(90deg, #1a2f1a, #0a1a0a);
            border-top: 2px solid #2d5a2d;
        }
        .input-wrapper {
            display: flex;
            gap: 10px;
        }
        .chat-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #2d5a2d;
            border-radius: 25px;
            background: rgba(0,0,0,0.8);
            color: #00ff00;
            font-size: 16px;
            outline: none;
        }
        .chat-input:focus {
            border-color: #4a8a4a;
            box-shadow: 0 0 15px rgba(0,255,0,0.3);
        }
        .send-button {
            padding: 15px 25px;
            background: linear-gradient(135deg, #4a8a4a, #2d5a2d);
            border: none;
            border-radius: 25px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .send-button:hover {
            background: linear-gradient(135deg, #5a9a5a, #3d6a3d);
            transform: translateY(-2px);
        }
        .send-button:disabled {
            background: #333;
            cursor: not-allowed;
            transform: none;
        }
        .typing-indicator {
            display: none;
            align-items: center;
            color: #666;
            font-style: italic;
            margin-left: 40px;
        }
        .typing-dots {
            display: inline-flex;
            margin-left: 10px;
        }
        .typing-dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4a8a4a;
            margin: 0 2px;
            animation: typing 1.4s infinite;
        }
        .typing-dots span:nth-child(1) { animation-delay: 0s; }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
        .welcome-message {
            text-align: center;
            color: #666;
            margin: 50px 0;
        }
        .quick-actions {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .quick-action {
            padding: 8px 15px;
            background: rgba(45,90,45,0.3);
            border: 1px solid #2d5a2d;
            border-radius: 15px;
            color: #88cc88;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }
        .quick-action:hover {
            background: rgba(45,90,45,0.6);
            color: #00ff00;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🦍 Guerilla the Gorilla</h1>
            <p>Your authentic guide to off-grid living • Ask me anything</p>
        </div>

        <div class="chat-messages" id="chatMessages">
            <div class="welcome-message">
                <p>🦍 Ready to talk gear, survival, and making money off-grid?</p>
                <div class="quick-actions">
                    <div class="quick-action" onclick="sendQuickMessage('What gear do I need for van life?')">Van Life Gear</div>
                    <div class="quick-action" onclick="sendQuickMessage('Best solar setup for off-grid?')">Solar Power</div>
                    <div class="quick-action" onclick="sendQuickMessage('How to make money while camping?')">Make Money</div>
                    <div class="quick-action" onclick="sendQuickMessage('Survival essentials for beginners?')">Survival Basics</div>
                </div>
            </div>
            
            <div class="typing-indicator" id="typingIndicator">
                🦍 Guerilla is thinking
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>

        <div class="chat-input-container">
            <div class="input-wrapper">
                <input 
                    type="text" 
                    class="chat-input" 
                    id="chatInput" 
                    placeholder="Ask Guerilla anything about off-grid living..."
                    autocomplete="off"
                >
                <button class="send-button" id="sendButton" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        let isTyping = false;
        let userId = 'user_' + Date.now();

        function addMessage(content, isUser = false) {
            const messagesContainer = document.getElementById('chatMessages');
            const welcomeMessage = messagesContainer.querySelector('.welcome-message');
            
            if (welcomeMessage) {
                welcomeMessage.style.display = 'none';
            }

            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            messageContent.textContent = content;
            
            messageDiv.appendChild(messageContent);
            
            const typingIndicator = document.getElementById('typingIndicator');
            messagesContainer.insertBefore(messageDiv, typingIndicator);
            
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function showTyping() {
            const typingIndicator = document.getElementById('typingIndicator');
            typingIndicator.style.display = 'flex';
            isTyping = true;
            
            const messagesContainer = document.getElementById('chatMessages');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function hideTyping() {
            const typingIndicator = document.getElementById('typingIndicator');
            typingIndicator.style.display = 'none';
            isTyping = false;
        }

        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const sendButton = document.getElementById('sendButton');
            const message = input.value.trim();

            if (!message || isTyping) return;

            addMessage(message, true);
            
            input.value = '';
            sendButton.disabled = true;
            sendButton.textContent = 'Sending...';
            
            showTyping();

            try {
                const response = await fetch('/api/guerilla-chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        user_id: userId
                    })
                });

                const data = await response.json();
                
                hideTyping();
                
                if (data.response) {
                    addMessage(data.response);
                } else {
                    addMessage("Something went sideways. Try asking again.");
                }

            } catch (error) {
                console.error('Error:', error);
                hideTyping();
                addMessage("Connection's acting up. Give it another shot.");
            } finally {
                sendButton.disabled = false;
                sendButton.textContent = 'Send';
                input.focus();
            }
        }

        function sendQuickMessage(message) {
            const input = document.getElementById('chatInput');
            input.value = message;
            sendMessage();
        }

        document.getElementById('chatInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !isTyping) {
                sendMessage();
            }
        });

        window.addEventListener('load', function() {
            document.getElementById('chatInput').focus();
        });
    </script>
</body>
</html>
'''

@app.route('/api/guerilla-chat', methods=['POST'])
def guerilla_chat():
    """AI chat endpoint with smart responses"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower()
        user_id = data.get('user_id', 'anonymous')
        
        # Store conversation
        if user_id not in chat_sessions:
            chat_sessions[user_id] = []
        
        chat_sessions[user_id].append({
            'user': data.get('message', ''),
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate smart responses based on keywords
        response = generate_guerilla_response(user_message)
        
        chat_sessions[user_id].append({
            'ai': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'response': response,
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({
            'response': "System's taking a smoke break. Ask me again in a sec.",
            'error': str(e)
        }), 500

def generate_guerilla_response(user_message):
    """Generate authentic Guerilla responses"""
    
    # Power/electricity keywords
    if any(word in user_message for word in ['power', 'battery', 'electric', 'charge', 'solar']):
        responses = [
            "🦍 For power, I swear by the Jackery Explorer 240. Used it for 2 years straight. Still charges my laptop, phone, and LED lights. Lightweight, reliable. Works.",
            "🦍 Solar power? Get a 100W panel and the Jackery 240. That combo kept me powered for months in the desert. Real world tested.",
            "🦍 Power banks are for tourists. You need a proper power station. Jackery 240 is the sweet spot - not too heavy, not too weak."
        ]
        return random.choice(responses)
    
    # Water keywords
    elif any(word in user_message for word in ['water', 'drink', 'filter', 'thirst', 'hydrat']):
        responses = [
            "🦍 Water filter? LifeStraw saved my ass more times than I can count. Filters 99.9999% of bacteria. Lightweight. No chemicals. Just works.",
            "🦍 Never trust water you find. LifeStraw filter is non-negotiable survival gear. Used mine in sketchy streams across 12 states.",
            "🦍 Water purification tablets work, but taste like ass. LifeStraw lets you drink from any source. Been using mine for 3 years."
        ]
        return random.choice(responses)
    
    # Food keywords
    elif any(word in user_message for word in ['food', 'eat', 'meal', 'cook', 'hungry', 'nutrition']):
        responses = [
            "🦍 Emergency food? 4Patriots kit lasts 25 years and tastes way better than MREs. I keep a month's supply. Smart investment.",
            "🦍 Cooking gear matters. Cast iron skillet and a reliable camp stove. Simple, durable, gets the job done.",
            "🦍 Food storage is survival. 4Patriots emergency food saved me when supply chains got wonky. 25-year shelf life, real food."
        ]
        return random.choice(responses)
    
    # Money/income keywords
    elif any(word in user_message for word in ['money', 'income', 'earn', 'job', 'work', 'cash', 'afford']):
        responses = [
            "🦍 Making money while camping? Content creation, remote work, and smart affiliate marketing. I'll show you the exact system.",
            "🦍 Broke camper? Start with digital busking - create content about your journey. People pay for authentic stories.",
            "🦍 Money flows to value. Document your camping journey, recommend gear that actually works, build trust. Revenue follows."
        ]
        return random.choice(responses)
    
    # Shelter/camping keywords
    elif any(word in user_message for word in ['tent', 'shelter', 'camp', 'sleep', 'van', 'rv']):
        responses = [
            "🦍 Shelter is survival. Coleman 4-person tent served me well in all weather. Reliable, affordable, proven.",
            "🦍 Van life? Start simple. Don't blow your budget on fancy builds. Basic van + essential gear = freedom.",
            "🦍 Good sleep = successful adventure. Invest in quality sleeping gear. Everything else is secondary."
        ]
        return random.choice(responses)
    
    # General survival/gear
    elif any(word in user_message for word in ['survival', 'gear', 'equipment', 'essential', 'need']):
        responses = [
            "🦍 Survival basics: reliable power (Jackery), clean water (LifeStraw), proper shelter, emergency food. That's your foundation.",
            "🦍 Gear philosophy: buy once, use forever. Quality costs more upfront but saves money long-term.",
            "🦍 Essential gear list: power station, water filter, emergency food, quality shelter. Everything else is luxury."
        ]
        return random.choice(responses)
    
    # Default responses
    else:
        responses = [
            "🦍 That's an interesting question. What specific challenge are you facing with off-grid living?",
            "🦍 I've seen a lot in my years camping. What's your current setup and what needs fixing?",
            "🦍 Every camping situation is different. Tell me more about what you're dealing with.",
            "🦍 From experience, the devil is in the details. What's your specific scenario?",
            "🦍 Been there, done that. What's the real challenge you're facing out there?"
        ]
        return random.choice(responses)

@app.route('/ai-dashboard')
def ai_dashboard():
    """Simple analytics dashboard"""
    total_sessions = len(chat_sessions)
    total_messages = sum(len(session) for session in chat_sessions.values())
    
    return f'''
    <h1>🦍 Guerilla AI Dashboard</h1>
    <p>Total Chat Sessions: {total_sessions}</p>
    <p>Total Messages: {total_messages}</p>
    <p>System Status: ✅ Online</p>
    <a href="/chat">Go to Chat</a> | <a href="/">Home</a>
    '''

@app.route('/health')
def health():
    """Health check for Azure"""
    return jsonify({
        'status': 'healthy',
        'app': 'gorilla-camping',
        'version': '1.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 