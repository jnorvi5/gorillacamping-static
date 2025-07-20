document.addEventListener('DOMContentLoaded', function() {
    // Create chat container if it doesn't exist
    if (!document.getElementById('guerilla-chat')) {
        const chatContainer = document.createElement('div');
        chatContainer.id = 'guerilla-chat';
        chatContainer.style = "position:fixed; bottom:20px; right:20px; z-index:9999;";
        
        chatContainer.innerHTML = `
            <div id="guerilla-toggle" style="width:60px; height:60px; background:#111; border-radius:50%; border:2px solid #00ff88; box-shadow:0 0 15px rgba(0,255,136,0.4); display:flex; align-items:center; justify-content:center; cursor:pointer; position:relative;">
                <img src="/img/logo.png" alt="Guerilla" style="width:40px; height:40px; border-radius:50%;">
                <span id="guerilla-badge" style="position:absolute; top:-5px; right:-5px; background:#ff4136; color:white; width:20px; height:20px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:bold; border:2px solid #111;">1</span>
            </div>
            
            <div id="guerilla-box" style="position:absolute; bottom:75px; right:0; width:320px; background:#222; border-radius:10px; overflow:hidden; display:none; box-shadow:0 0 20px rgba(0,0,0,0.3); border:2px solid rgba(0,255,136,0.3);">
                <div style="background:#111; padding:10px 15px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid rgba(0,255,136,0.3);">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <img src="/img/logo.png" style="width:30px; height:30px; border-radius:50%; border:2px solid #00ff88;">
                        <div>
                            <div style="font-weight:bold; color:#00ff88;">Guerilla</div>
                            <div style="font-size:12px; color:#aaa;">Camping Expert</div>
                        </div>
                    </div>
                    <div id="guerilla-close" style="cursor:pointer; font-size:20px; color:#aaa;">×</div>
                </div>
                
                <div id="guerilla-messages" style="height:300px; overflow-y:auto; padding:15px;"></div>
                
                <div style="padding:10px; display:flex; gap:10px; border-top:1px solid rgba(255,255,255,0.1);">
                    <input id="guerilla-input" type="text" placeholder="Ask about camping gear..." style="flex:1; padding:8px 12px; border-radius:20px; border:1px solid rgba(0,255,136,0.3); background:#333; color:white; outline:none;">
                    <button id="guerilla-send" style="background:#00ff88; color:#111; border:none; width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; cursor:pointer;">→</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(chatContainer);
    }

    const toggle = document.getElementById('guerilla-toggle');
    const close = document.getElementById('guerilla-close');
    const chatBox = document.getElementById('guerilla-box');
    const messages = document.getElementById('guerilla-messages');
    const input = document.getElementById('guerilla-input');
    const sendBtn = document.getElementById('guerilla-send');
    const badge = document.getElementById('guerilla-badge');
    
    // Toggle chat
    toggle.addEventListener('click', function() {
        chatBox.style.display = chatBox.style.display === 'none' ? 'block' : 'none';
        badge.style.display = 'none';
        
        // Show initial message if it's the first time
        if (messages.children.length === 0) {
            addMessage("Yo! I'm Guerilla. Need advice on camping gear, survival tips, or making money while living off-grid?", 'ai');
            
            // Show gear suggestion after 3 seconds
            setTimeout(function() {
                addMessage("Most people ask me about power solutions for camping. Check out what I personally use:", 'ai');
                addProduct('jackery-explorer-240');
            }, 3000);
        }
    });
    
    // Close chat
    close.addEventListener('click', function() {
        chatBox.style.display = 'none';
    });
    
    // Send message
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    function sendMessage() {
        const text = input.value.trim();
        if (!text) return;
        
        // Add user message
        addMessage(text, 'user');
        input.value = '';
        
        // Add loading indicator
        const loadingId = 'loading-' + Date.now();
        addLoadingMessage(loadingId);
        
        // Send to Azure backend AI
        fetch(`${CONFIG.API_URL}/api/guerilla-chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: text })
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response failed');
            return response.json();
        })
        .then(data => {
            // Remove loading indicator
            const loadingEl = document.getElementById(loadingId);
            if (loadingEl) loadingEl.remove();
            
            // Add AI response
            addMessage(data.response, 'ai');
            
            // Add product recommendation if available
            if (data.recommendations && data.recommendations.length > 0) {
                setTimeout(function() {
                    addProduct(data.recommendations[0].id);
                }, 800);
            }
        })
        .catch(error => {
            // Remove loading indicator
            const loadingEl = document.getElementById(loadingId);
            if (loadingEl) loadingEl.remove();
            
            // Add error message
            addMessage("Sorry, I'm having trouble connecting right now. Try again or check out my recommended gear below:", 'ai');
            
            // Show fallback product
            setTimeout(function() {
                addProduct('jackery-explorer-240');
            }, 800);
            
            console.error('Error:', error);
        });
    }
    
    // Rest of the chat functions...
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.style.marginBottom = '15px';
        messageDiv.style.display = 'flex';
        messageDiv.style.gap = '10px';
        
        if (sender === 'ai') {
            messageDiv.innerHTML = `
                <img src="/img/logo.png" style="width:30px; height:30px; border-radius:50%; align-self:flex-start;">
                <div style="background:#333; padding:10px; border-radius:10px; color:white; max-width:80%;">${text}</div>
            `;
        } else {
            messageDiv.style.flexDirection = 'row-reverse';
            messageDiv.innerHTML = `
                <div style="background:rgba(0,255,136,0.2); padding:10px; border-radius:10px; color:white; max-width:80%;">${text}</div>
            `;
        }
        
        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }
    
    function addLoadingMessage(id) {
        const messageDiv = document.createElement('div');
        messageDiv.id = id;
        messageDiv.style.marginBottom = '15px';
        messageDiv.style.display = 'flex';
        messageDiv.style.gap = '10px';
        
        messageDiv.innerHTML = `
            <img src="/img/logo.png" style="width:30px; height:30px; border-radius:50%; align-self:flex-start;">
            <div style="background:#333; padding:10px; border-radius:10px; color:white; max-width:80%;">
                <div class="loading-dots">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </div>
            </div>
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            .loading-dots {
                display: flex;
                gap: 6px;
            }
            .dot {
                width: 8px;
                height: 8px;
                background: rgba(0,255,136,0.5);
                border-radius: 50%;
                animation: bounce 1.4s infinite ease-in-out both;
            }
            .dot:nth-child(1) { animation-delay: -0.32s; }
            .dot:nth-child(2) { animation-delay: -0.16s; }
            @keyframes bounce {
                0%, 80%, 100% { transform: scale(0); }
                40% { transform: scale(1); }
            }
        `;
        document.head.appendChild(style);
        
        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }
    
    // Products with affiliate links
    const products = {
        'jackery-explorer-240': {
            name: 'Jackery Explorer 240',
            image: '/img/products/jackery.jpg',
            price: '$199.99',
            link: '/affiliate/jackery-explorer-240'
        },
        'lifestraw-filter': {
            name: 'LifeStraw Filter',
            image: '/img/products/lifestraw.jpg',
            price: '$14.96',
            link: '/affiliate/lifestraw-filter'
        },
        '4patriots-food': {
            name: '4Patriots Food Kit',
            image: '/img/products/4patriots.jpg',
            price: '$27.00',
            link: '/affiliate/4patriots-food'
        }
    };
    
    function addProduct(productId) {
        if (!products[productId]) return;
        
        const product = products[productId];
        const productDiv = document.createElement('div');
        productDiv.style.marginBottom = '15px';
        productDiv.style.display = 'flex';
        productDiv.style.gap = '10px';
        
        productDiv.innerHTML = `
            <img src="/img/logo.png" style="width:30px; height:30px; border-radius:50%; align-self:flex-start;">
            <div style="max-width:80%;">
                <div style="background:#333; padding:10px; border-radius:10px 10px 0 0; color:white;">Check this out:</div>
                <div style="border:1px solid rgba(0,255,136,0.3); border-top:none; border-radius:0 0 10px 10px; overflow:hidden; background:rgba(0,0,0,0.3);">
                    <div style="display:flex; padding:10px; gap:10px; align-items:center;">
                        <img src="${product.image}" style="width:50px; height:50px; object-fit:contain; border-radius:5px;">
                        <div>
                            <div style="font-weight:bold;">${product.name}</div>
                            <div style="color:#00ff88;">${product.price}</div>
                        </div>
                    </div>
                    <div style="background:#00ff88; text-align:center; padding:8px;">
                        <a href="${product.link}" style="color:#111; text-decoration:none; font-weight:bold;" 
                           onclick="trackAffiliateClick('${product.link}', '${product.name}')">VIEW DEAL →</a>
                    </div>
                </div>
            </div>
        `;
        
        messages.appendChild(productDiv);
        messages.scrollTop = messages.scrollHeight;
        
        // Track this recommendation with the backend
        try {
            fetch(`${CONFIG.API_URL}/api/affiliate-click`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    product_id: productId,
                    source: 'chat'
                })
            });
        } catch(e) {
            console.log('Error tracking view', e);
        }
    }
    
    // Show chat bubble after 30 seconds
    setTimeout(() => {
        if (chatBox.style.display !== 'block') {
            badge.style.display = 'flex';
            
            // Add animation to attract attention
            toggle.style.animation = 'pulse 2s infinite';
            
            // Style for animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }
            `;
            document.head.appendChild(style);
        }
    }, 30000);
});
