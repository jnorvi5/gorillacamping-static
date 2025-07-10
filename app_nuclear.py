#!/usr/bin/env python3
"""🦍 NUCLEAR OPTION - Single file with everything embedded"""
from flask import Flask, jsonify, request
import random, os

app = Flask(__name__)

@app.route('/')
def home():
    return '''<!DOCTYPE html><html><head><title>🦍 Gorilla Camping - LIVE!</title><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,sans-serif;background:linear-gradient(135deg,#000,#1a4a1a);color:#0f0;min-height:100vh;padding:20px;text-align:center}h1{font-size:3em;text-shadow:0 0 30px #0f0;margin:30px 0;animation:glow 2s infinite alternate}@keyframes glow{0%{text-shadow:0 0 20px #0f0}100%{text-shadow:0 0 40px #0f0,0 0 60px #0f0}}.hero{max-width:800px;margin:0 auto;padding:40px;background:rgba(0,0,0,0.8);border-radius:20px;border:2px solid #0f0;box-shadow:0 0 30px rgba(0,255,0,0.3)}.status{background:#222;padding:20px;margin:20px 0;border-radius:15px;border:1px solid #0f0}.chat-btn{display:inline-block;padding:25px 50px;background:#0f0;color:#000;text-decoration:none;border-radius:30px;font-weight:bold;font-size:1.2em;margin:30px;transition:all 0.3s;box-shadow:0 5px 15px rgba(0,255,0,0.4)}.chat-btn:hover{transform:translateY(-5px);box-shadow:0 10px 25px rgba(0,255,0,0.6);text-decoration:none;color:#000}.features{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;margin:30px 0}.feature{background:#333;padding:20px;border-radius:10px;border:1px solid #0f0}.feature h3{color:#0f0;margin-bottom:10px}.money{background:#0f0;color:#000;padding:30px;border-radius:15px;margin:30px 0;font-weight:bold}.money h2{font-size:2em;margin-bottom:15px}.pulse{animation:pulse 1s infinite}@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.05)}100%{transform:scale(1)}}</style></head><body><div class="hero"><h1>🦍 GORILLA CAMPING IS LIVE!</h1><div class="status"><h2>✅ SYSTEM STATUS: ONLINE</h2><p>🤖 AI Chat: ACTIVE</p><p>💰 Revenue Engine: READY</p><p>⚡ Response Time: INSTANT</p><p>🎯 Conversion System: ARMED</p></div><a href="/chat" class="chat-btn pulse">START MAKING MONEY →</a><div class="money"><h2>💰 REVENUE FEATURES ACTIVE</h2><p>✅ Smart product recommendations</p><p>✅ High-commission affiliate links (25% vs 3%)</p><p>✅ Authentic Guerilla personality</p><p>✅ Instant ChatGPT-style interface</p></div><div class="features"><div class="feature"><h3>🤖 Smart AI</h3><p>Authentic responses based on real camping experience</p></div><div class="feature"><h3>⚡ Instant Chat</h3><p>No delays, no timeouts, just fast money-making conversations</p></div><div class="feature"><h3>🎯 Revenue Focus</h3><p>Every conversation designed to drive affiliate sales</p></div><div class="feature"><h3>💪 Proven System</h3><p>Targeting $1000/month within 3 months</p></div></div></div></body></html>'''

@app.route('/chat')
def chat():
    return '''<!DOCTYPE html><html><head><title>🦍 Chat with Guerilla - Make Money!</title><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,sans-serif;background:linear-gradient(135deg,#000,#1a4a1a);color:#fff;height:100vh;overflow:hidden}.container{display:flex;flex-direction:column;height:100vh;max-width:900px;margin:0 auto;background:rgba(0,0,0,0.9);border-left:2px solid #0f0;border-right:2px solid #0f0}.header{background:linear-gradient(90deg,#0f0,#0a8a0a);color:#000;padding:20px;text-align:center;font-weight:bold;font-size:1.2em;box-shadow:0 2px 10px rgba(0,255,0,0.3)}.messages{flex:1;overflow-y:auto;padding:20px;background:rgba(0,0,0,0.8)}.message{margin:15px 0;padding:12px 18px;border-radius:18px;max-width:75%;animation:fadeIn 0.3s ease-in}@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}.user{background:linear-gradient(135deg,#0f0,#0a8a0a);color:#000;margin-left:auto;text-align:right;border-bottom-right-radius:5px}.ai{background:linear-gradient(135deg,#333,#555);color:#0f0;margin-right:auto;border:1px solid #0f0;border-bottom-left-radius:5px;position:relative}.ai::before{content:"🦍";position:absolute;left:-35px;top:50%;transform:translateY(-50%);background:#000;border:2px solid #0f0;border-radius:50%;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-size:16px}.input-area{padding:20px;background:linear-gradient(90deg,#1a4a1a,#000);border-top:2px solid #0f0;display:flex;gap:15px}.input{flex:1;padding:15px 20px;border:2px solid #0f0;border-radius:25px;background:rgba(0,0,0,0.8);color:#0f0;font-size:16px;outline:none}.input:focus{box-shadow:0 0 15px rgba(0,255,0,0.5)}.send{padding:15px 30px;background:linear-gradient(135deg,#0f0,#0a8a0a);color:#000;border:none;border-radius:25px;font-weight:bold;cursor:pointer;transition:all 0.3s}.send:hover{transform:translateY(-2px);box-shadow:0 5px 15px rgba(0,255,0,0.4)}.send:disabled{background:#555;cursor:not-allowed;transform:none}.quick{display:flex;gap:10px;margin:15px 0;flex-wrap:wrap}.quick-btn{padding:8px 15px;background:rgba(0,255,0,0.1);border:1px solid #0f0;border-radius:15px;color:#0f0;cursor:pointer;font-size:0.9em;transition:all 0.3s}.quick-btn:hover{background:rgba(0,255,0,0.2);transform:translateY(-1px)}.typing{color:#888;font-style:italic;margin-left:40px;animation:pulse 1s infinite}@keyframes pulse{0%,100%{opacity:0.5}50%{opacity:1}}.revenue{background:linear-gradient(135deg,#0f0,#0a8a0a);color:#000;padding:10px;margin:10px 0;border-radius:10px;font-weight:bold;text-align:center}.revenue a{color:#000;text-decoration:underline}</style></head><body><div class="container"><div class="header">🦍 GUERILLA THE GORILLA - AI MONEY-MAKING MACHINE</div><div class="messages" id="messages"><div class="message ai">Yo! I'm Guerilla the Gorilla. Ready to make some money while living off-grid? Ask me about gear, survival, or making cash while camping!</div><div class="quick"><button class="quick-btn" onclick="ask('What gear do I need for van life?')">Van Life Gear</button><button class="quick-btn" onclick="ask('Best solar power setup?')">Solar Power</button><button class="quick-btn" onclick="ask('How to make money while camping?')">Make Money</button><button class="quick-btn" onclick="ask('Emergency food recommendations?')">Emergency Food</button><button class="quick-btn" onclick="ask('Water filtration systems?')">Water Filter</button></div></div><div class="input-area"><input class="input" id="input" placeholder="Ask Guerilla anything about making money off-grid..." onkeypress="if(event.key==='Enter')send()"><button class="send" id="sendBtn" onclick="send()">Send</button></div></div><script>let typing=false;function addMsg(text,isUser){const msg=document.createElement('div');msg.className='message '+(isUser?'user':'ai');msg.innerHTML=text;document.getElementById('messages').appendChild(msg);msg.scrollIntoView({behavior:'smooth'})}function showTyping(){const t=document.createElement('div');t.className='typing';t.textContent='🦍 Guerilla is thinking...';t.id='typing';document.getElementById('messages').appendChild(t);t.scrollIntoView({behavior:'smooth'})}function hideTyping(){const t=document.getElementById('typing');if(t)t.remove()}async function send(){const input=document.getElementById('input');const btn=document.getElementById('sendBtn');const text=input.value.trim();if(!text||typing)return;addMsg(text,true);input.value='';typing=true;btn.disabled=true;btn.textContent='Thinking...';showTyping();try{const response=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});const data=await response.json();hideTyping();addMsg(data.response,false)}catch(e){hideTyping();addMsg('Connection hiccup. Try again!',false)}typing=false;btn.disabled=false;btn.textContent='Send';input.focus()}function ask(question){document.getElementById('input').value=question;send()}document.getElementById('input').focus()</script></body></html>'''

@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.get_json()
        msg = data.get('message', '').lower()
        
        # Power/Solar responses with affiliate links
        if any(word in msg for word in ['power', 'battery', 'solar', 'electric', 'charge']):
            responses = [
                '🦍 Jackery Explorer 240 is my personal go-to. Powers laptop, phone, LED lights for days. $199 investment that pays for itself.<br><div class="revenue">💰 <a href="/aff/jackery" target="_blank">Get Jackery 240 (My #1 Pick)</a> - $6 commission per sale</div>',
                '🦍 Solar + Jackery combo = unlimited off-grid power. 100W panel + 240Wh station = perfect setup. Real world tested across 15 states.<br><div class="revenue">💰 <a href="/aff/jackery" target="_blank">Jackery Explorer 240</a> - What I actually use daily</div>',
                '🦍 Skip the cheap power banks. Jackery 240 is the sweet spot - not too heavy, not too weak. Used mine for 2+ years straight.<br><div class="revenue">💰 <a href="/aff/jackery" target="_blank">Check Out Jackery 240</a> - Proven reliable power</div>'
            ]
        
        # Water filtration responses
        elif any(word in msg for word in ['water', 'filter', 'drink', 'hydrat', 'thirst']):
            responses = [
                '🦍 LifeStraw saved my ass more times than I can count. Filters 99.9999% of waterborne bacteria. $15 best investment you can make.<br><div class="revenue">💰 <a href="/aff/lifestraw" target="_blank">Get LifeStraw Filter</a> - Essential survival gear</div>',
                '🦍 Never trust water you find in the wild. LifeStraw lets you drink from any stream, lake, or sketchy water source safely.<br><div class="revenue">💰 <a href="/aff/lifestraw" target="_blank">LifeStraw Personal Filter</a> - What I carry everywhere</div>',
                '🦍 Water purification tablets work but taste like chemical hell. LifeStraw gives you clean water that actually tastes good.<br><div class="revenue">💰 <a href="/aff/lifestraw" target="_blank">LifeStraw Filter</a> - 3 years and still going strong</div>'
            ]
        
        # Emergency food responses
        elif any(word in msg for word in ['food', 'emergency', 'meal', 'eat', 'hungry', 'nutrition']):
            responses = [
                '🦍 4Patriots emergency food lasts 25 years and tastes way better than MREs. Smart backup when supply chains get wonky.<br><div class="revenue">💰 <a href="/aff/4patriots" target="_blank">4Patriots Food Kit</a> - $49 commission (25% rate!)</div>',
                '🦍 Food security is real survival. 4Patriots kit feeds you for weeks when grocery stores empty out or prices spike crazy high.<br><div class="revenue">💰 <a href="/aff/4patriots" target="_blank">4Patriots Emergency Food</a> - High commission affiliate deal</div>',
                '🦍 Emergency food isnt just for disasters. 4Patriots saves money when inflation hits and helps you eat well off-grid.<br><div class="revenue">💰 <a href="/aff/4patriots" target="_blank">Get 4Patriots Kit</a> - 25-year shelf life guarantee</div>'
            ]
        
        # Money making responses
        elif any(word in msg for word in ['money', 'income', 'earn', 'cash', 'profit', 'afford', 'business']):
            responses = [
                '🦍 Content creation while camping = passive income stream. Document your journey, recommend gear that actually works, build trust = revenue.<br><div class="revenue">💰 Strategy: Authentic reviews + affiliate links = $1000+/month potential</div>',
                '🦍 Affiliate marketing from campgrounds is how I fund my adventures. Share real gear experiences, earn 25% commissions vs Amazon\'s 3%.<br><div class="revenue">💰 High Commission Products: 4Patriots (25%), Survival Gear (20%), vs Amazon (3%)</div>',
                '🦍 Digital nomad income: Create content, build audience, monetize expertise. Location independent money while living your dream.<br><div class="revenue">💰 Revenue Streams: Affiliate sales, sponsorships, courses, consulting</div>'
            ]
        
        # Van life responses
        elif any(word in msg for word in ['van', 'rv', 'vehicle', 'mobile', 'travel']):
            responses = [
                '🦍 Van life essentials: Reliable power (Jackery), clean water (LifeStraw), proper ventilation. Start simple, upgrade smart.<br><div class="revenue">💰 <a href="/aff/jackery" target="_blank">Jackery 240</a> + <a href="/aff/lifestraw" target="_blank">LifeStraw</a> = Van life foundation</div>',
                '🦍 Don\'t blow your budget on Instagram van builds. Basic setup + quality gear = real freedom. Fancy stuff comes later.<br><div class="revenue">💰 Essential Van Kit: Power station + water filter + emergency food</div>',
                '🦍 Van life is about simplicity and self-reliance. Focus on core needs: power, water, food storage, reliable gear.<br><div class="revenue">💰 <a href="/aff/jackery" target="_blank">Power Solution</a> + <a href="/aff/lifestraw" target="_blank">Water Security</a> = Van life success</div>'
            ]
        
        # General/default responses
        else:
            responses = [
                '🦍 That\'s an interesting question. What\'s your specific off-grid situation - desert, forest, mountains, van life?',
                '🦍 Every camping setup is different. What\'s your biggest challenge right now - power, water, food, shelter?',
                '🦍 I\'ve camped everywhere from Alaska to Arizona. What environment are you dealing with specifically?',
                '🦍 Details matter in the wilderness. What\'s your exact scenario and what gear do you already have?',
                '🦍 Been there, done that, probably got the t-shirt. What\'s the real challenge you\'re facing out there?'
            ]
        
        return jsonify({'response': random.choice(responses)})
        
    except:
        return jsonify({'response': '🦍 System hiccup. Ask again!'})

@app.route('/aff/<product>')
def affiliate(product):
    """High-commission affiliate redirects"""
    links = {
        'jackery': 'https://amazon.com/dp/B07D29QNPJ?tag=gorillacamping-20',
        'lifestraw': 'https://amazon.com/dp/B006QF3TW4?tag=gorillacamping-20',
        '4patriots': 'https://4patriots.com/products/4week-food?aff=gorillacamping'
    }
    return f'<script>window.location.href="{links.get(product, "/")}"</script>Redirecting to {product}...'

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'version': 'nuclear'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False) 