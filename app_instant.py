"""
🦍 Instant Gorilla Camping - Starts in 2 seconds!
Ultra-lightweight version for Azure
"""

from flask import Flask, jsonify, request
import json
import random

app = Flask(__name__)

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>🦍 Gorilla Camping - Live!</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body{font-family:Arial;background:#111;color:#0f0;margin:0;padding:20px;text-align:center}
        h1{font-size:3em;margin:20px 0;text-shadow:0 0 20px #0f0}
        .chat-btn{display:inline-block;padding:20px 40px;background:#0f0;color:#111;text-decoration:none;border-radius:25px;font-weight:bold;margin:20px}
        .status{background:#222;padding:20px;border-radius:10px;margin:20px auto;max-width:600px}
    </style>
</head>
<body>
    <h1>🦍 GORILLA CAMPING IS LIVE!</h1>
    <div class="status">
        <h2>✅ System Status: ONLINE</h2>
        <p>AI Chat System: ACTIVE</p>
        <p>Revenue Engine: READY</p>
        <p>Response Time: INSTANT</p>
    </div>
    <a href="/chat" class="chat-btn">START MAKING MONEY →</a>
    <div class="status">
        <h3>🎯 What's Working:</h3>
        <p>✅ ChatGPT-style interface</p>
        <p>✅ Smart product recommendations</p>
        <p>✅ Authentic Guerilla personality</p>
        <p>✅ High-commission affiliate links</p>
    </div>
</body>
</html>"""

@app.route('/chat')
def chat():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>🦍 Chat with Guerilla</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:Arial;background:#111;color:#fff;height:100vh;overflow:hidden}
        .container{display:flex;flex-direction:column;height:100vh;max-width:800px;margin:0 auto;background:#222}
        .header{background:#0f0;color:#111;padding:15px;text-align:center;font-weight:bold}
        .messages{flex:1;overflow-y:auto;padding:20px}
        .message{margin:15px 0;padding:10px 15px;border-radius:15px;max-width:80%}
        .user{background:#0f0;color:#111;margin-left:auto;text-align:right}
        .ai{background:#333;color:#0f0;margin-right:auto}
        .ai::before{content:"🦍 ";font-size:1.2em}
        .input-area{padding:15px;background:#333;display:flex;gap:10px}
        .input{flex:1;padding:10px;border:none;border-radius:20px;background:#555;color:#fff;outline:none}
        .send{padding:10px 20px;background:#0f0;color:#111;border:none;border-radius:20px;font-weight:bold;cursor:pointer}
        .quick{display:flex;gap:10px;margin:10px 0;flex-wrap:wrap}
        .quick-btn{padding:5px 10px;background:#555;border:none;border-radius:10px;color:#0f0;cursor:pointer;font-size:0.9em}
        .typing{color:#666;font-style:italic;margin-left:30px}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">🦍 GUERILLA THE GORILLA - MONEY-MAKING CHAT</div>
        <div class="messages" id="messages">
            <div class="message ai">Ready to talk gear, survival, and making money off-grid! What's your question?</div>
            <div class="quick">
                <button class="quick-btn" onclick="ask('What gear for van life?')">Van Life Gear</button>
                <button class="quick-btn" onclick="ask('Best solar power setup?')">Solar Power</button>
                <button class="quick-btn" onclick="ask('How to make money camping?')">Make Money</button>
                <button class="quick-btn" onclick="ask('Emergency food recommendations?')">Emergency Food</button>
            </div>
        </div>
        <div class="input-area">
            <input class="input" id="input" placeholder="Ask Guerilla anything..." onkeypress="if(event.key==='Enter')send()">
            <button class="send" onclick="send()">Send</button>
        </div>
    </div>

    <script>
        let typing = false;
        
        function addMsg(text, isUser) {
            const msg = document.createElement('div');
            msg.className = 'message ' + (isUser ? 'user' : 'ai');
            msg.textContent = text;
            document.getElementById('messages').appendChild(msg);
            msg.scrollIntoView();
        }
        
        function showTyping() {
            const typing = document.createElement('div');
            typing.className = 'typing';
            typing.textContent = '🦍 Guerilla is thinking...';
            typing.id = 'typing';
            document.getElementById('messages').appendChild(typing);
            typing.scrollIntoView();
        }
        
        function hideTyping() {
            const t = document.getElementById('typing');
            if(t) t.remove();
        }
        
        async function send() {
            const input = document.getElementById('input');
            const text = input.value.trim();
            if(!text || typing) return;
            
            addMsg(text, true);
            input.value = '';
            typing = true;
            showTyping();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await response.json();
                hideTyping();
                addMsg(data.response, false);
            } catch(e) {
                hideTyping();
                addMsg("Connection hiccup. Try again!", false);
            }
            typing = false;
        }
        
        function ask(question) {
            document.getElementById('input').value = question;
            send();
        }
    </script>
</body>
</html>"""

@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.get_json()
        msg = data.get('message', '').lower()
        
        # Smart responses based on keywords
        if 'power' in msg or 'battery' in msg or 'solar' in msg:
            responses = [
                "🦍 Jackery Explorer 240 is my go-to. Powers laptop, phone, lights for days. $199 and worth every penny.",
                "🦍 Solar + Jackery combo = unlimited power. 100W panel charges the 240 perfectly. Real world tested.",
                "🦍 Skip the cheap power banks. Jackery 240 is the sweet spot - reliable, lightweight, proven."
            ]
        elif 'water' in msg or 'filter' in msg:
            responses = [
                "🦍 LifeStraw saved my life more than once. Filters 99.9999% of bacteria. $15 best investment ever.",
                "🦍 Never trust found water. LifeStraw lets you drink from any source safely. Compact, reliable.",
                "🦍 Water purification tablets taste terrible. LifeStraw gives you clean water that actually tastes good."
            ]
        elif 'food' in msg or 'emergency' in msg:
            responses = [
                "🦍 4Patriots emergency food lasts 25 years and tastes way better than MREs. Smart backup plan.",
                "🦍 Food security is survival. 4Patriots kit feeds you for weeks when supply chains break down.",
                "🦍 Emergency food isn't just for disasters. 4Patriots saves money when grocery prices spike."
            ]
        elif 'money' in msg or 'income' in msg or 'earn' in msg:
            responses = [
                "🦍 Content creation while camping = passive income. Document your journey, recommend gear that works.",
                "🦍 Affiliate marketing from campgrounds is how I fund my adventures. Authentic recommendations pay.",
                "🦍 Digital nomad life: create content, build audience, monetize expertise. Location independent income."
            ]
        elif 'van' in msg or 'rv' in msg:
            responses = [
                "🦍 Van life essentials: reliable power (Jackery), clean water (LifeStraw), proper ventilation. Start simple.",
                "🦍 Don't blow your budget on Instagram van builds. Basic setup + quality gear = real freedom.",
                "🦍 Van life is about simplicity. Focus on essentials first, fancy stuff later."
            ]
        else:
            responses = [
                "🦍 That's interesting. What's your specific camping situation? Desert, forest, mountains?",
                "🦍 Every setup is different. What's your biggest challenge right now?",
                "🦍 I've camped everywhere. What environment are you dealing with?",
                "🦍 Details matter in the wilderness. What's your exact scenario?"
            ]
        
        response = random.choice(responses)
        
        # Add product recommendations for relevant keywords
        if any(word in msg for word in ['power', 'battery', 'solar']):
            response += "\n\n💰 Check out the Jackery Explorer 240 - my personal recommendation: /affiliate/jackery"
        elif any(word in msg for word in ['water', 'filter']):
            response += "\n\n💰 Get the LifeStraw I use: /affiliate/lifestraw"
        elif any(word in msg for word in ['food', 'emergency']):
            response += "\n\n💰 4Patriots Emergency Food (my choice): /affiliate/4patriots"
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'response': "System hiccup. Ask again!"})

@app.route('/affiliate/<product>')
def affiliate(product):
    links = {
        'jackery': 'https://amazon.com/dp/B07D29QNPJ?tag=gorillacamping-20',
        'lifestraw': 'https://amazon.com/dp/B006QF3TW4?tag=gorillacamping-20', 
        '4patriots': 'https://4patriots.com/products/4week-food?aff=gorilla'
    }
    return f'<script>window.location.href="{links.get(product, "/")}"</script>'

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'app': 'instant'})

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False) 