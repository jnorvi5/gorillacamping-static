// Guerilla the Gorilla - AI Chatbot with Revenue-Driving Features
document.addEventListener('DOMContentLoaded', function() {
  // Initialize elements
  const toggle = document.getElementById('guerilla-toggle');
  const chatContainer = document.querySelector('.guerilla-chat-container');
  const closeButton = document.getElementById('guerilla-close');
  const sendButton = document.getElementById('guerilla-send');
  const inputField = document.getElementById('guerilla-input');
  const messagesContainer = document.getElementById('guerilla-messages');
  const notification = document.getElementById('guerilla-notification');
  const initialSuggestion = document.getElementById('guerilla-initial-suggestion');
  const modal = document.getElementById('guerilla-product-modal');
  const modalClose = document.querySelector('.guerilla-modal-close');
  const modalBody = document.getElementById('guerilla-modal-body');
  
  // Product database with affiliate links
  const products = {
    'jackery-explorer-240': {
      name: 'Jackery Explorer 240',
      image: 'https://m.media-amazon.com/images/I/41XePYWYlAL._AC_US300_.jpg',
      originalPrice: '$299.99',
      price: '$199.99',
      description: 'My #1 recommended portable power station for camping. I use this daily for charging my gear, running lights, and even making viral TikTok videos while off-grid. It\'s paid for itself many times over through affiliate commissions.',
      badges: ['BESTSELLER', '33% OFF', 'GUERILLA APPROVED'],
      link: '/affiliate/jackery-explorer-240',
      testimonial: '"This solar generator literally saved my camping business - I can create content all day without worrying about power." - Mike T.',
      visitors: generateRandomNumber(3, 15),
      inventory: generateRandomNumber(2, 8)
    },
    'lifestraw-filter': {
      name: 'LifeStraw Personal Water Filter',
      image: 'https://m.media-amazon.com/images/I/71SYsNwj7hL._AC_UL320_.jpg',
      originalPrice: '$19.95',
      price: '$14.96',
      description: 'Essential survival gear that filters 99.9999% of waterborne bacteria. I never go camping without one - and it makes for awesome demonstration videos that earn solid affiliate commissions.',
      badges: ['BESTSELLER', '25% OFF', 'VIRAL CONTENT'],
      link: '/affiliate/lifestraw-filter',
      testimonial: '"I\'ve made $300+ just from reviewing this filter on my social media." - Sarah K.',
      visitors: generateRandomNumber(5, 18),
      inventory: generateRandomNumber(5, 15)
    },
    '4patriots-food': {
      name: '4Patriots Emergency Food Kit',
      image: 'https://via.placeholder.com/300x300?text=Emergency+Food',
      originalPrice: '$297.00',
      price: '$197.00',
      description: 'Long-term emergency food with 25-year shelf life. Perfect for off-grid camping and emergency preparedness. High-commission product (25%) that\'s been my #1 earner for months.',
      badges: ['HIGH COMMISSION', '25% COMMISSION', 'LIMITED STOCK'],
      link: '/affiliate/4patriots-food',
      testimonial: '"Made $142 from a single Instagram post featuring this kit!" - John D.',
      visitors: generateRandomNumber(4, 12),
      inventory: generateRandomNumber(1, 5)
    }
  };
  
  // Popular keywords that trigger product recommendations
  const keywordMap = {
    'power': 'jackery-explorer-240',
    'battery': 'jackery-explorer-240',
    'charging': 'jackery-explorer-240',
    'electricity': 'jackery-explorer-240',
    'water': 'lifestraw-filter',
    'drink': 'lifestraw-filter',
    'filter': 'lifestraw-filter',
    'food': '4patriots-food',
    'meal': '4patriots-food',
    'emergency': '4patriots-food'
  };
  
  // Money-making conversation paths
  const revenuePaths = [
    "Tell me more about how you make money camping",
    "What gear do I need to start?",
    "How can I power my devices off-grid?",
    "What's the best survival gear?",
    "Show me your top recommendations"
  ];
  
  // Open chat when toggle is clicked
  toggle.addEventListener('click', function() {
    chatContainer.style.display = 'flex';
    notification.style.display = 'none';
    toggle.classList.add('guerilla-breathing');
    
    // Show initial product suggestion after 10 seconds
    setTimeout(() => {
      if (initialSuggestion) {
        initialSuggestion.style.display = 'flex';
        scrollToBottom();
      }
    }, 10000);
    
    // Track open in analytics
    trackEvent('guerilla_chat_open');
  });
  
  // Close chat when close button is clicked
  closeButton.addEventListener('click', function() {
    chatContainer.style.display = 'none';
    toggle.classList.remove('guerilla-breathing');
    
    // Track close in analytics
    trackEvent('guerilla_chat_close');
  });
  
  // Handle send button click
  sendButton.addEventListener('click', function() {
    sendMessage();
  });
  
  // Handle enter key press
  inputField.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });
  
  // Close modal when X is clicked
  modalClose.addEventListener('click', function() {
    modal.style.display = 'none';
  });
  
  // Close modal when clicking outside the modal content
  window.addEventListener('click', function(event) {
    if (event.target === modal) {
      modal.style.display = 'none';
    }
  });
  
  // Send user message and get response
  function sendMessage() {
    const message = inputField.value.trim();
    if (message === '') return;
    
    // Display user message
    appendMessage(message, 'outgoing');
    
    // Clear input field
    inputField.value = '';
    
    // Check for product keywords
    let productMatch = null;
    Object.keys(keywordMap).forEach(keyword => {
      if (message.toLowerCase().includes(keyword)) {
        productMatch = keywordMap[keyword];
      }
    });
    
    // Process message
    processMessage(message, productMatch);
    
    // Track in analytics
    trackEvent('guerilla_chat_message', {
      message_text: message,
      product_match: productMatch
    });
  }
  
  // Process user message and generate response
  function processMessage(message, productMatch) {
    // Show typing indicator
    appendTypingIndicator();
    
    // Make API call to backend or use local logic
    setTimeout(() => {
      // Remove typing indicator
      removeTypingIndicator();
      
      // Generate response based on message or use backend API
      let response = '';
      
      if (message.toLowerCase().includes('make money') || 
          message.toLowerCase().includes('earn') ||
          message.toLowerCase().includes('income')) {
        response = "The 3 easiest ways to make $1000/month camping are:<br><br>1. <strong>Affiliate marketing</strong> with high-commission camping gear (25-30% vs Amazon's 3-4%)<br>2. <strong>Digital products</strong> like camping guides and prepping manuals<br>3. <strong>Content creation</strong> about survival skills and gear reviews<br><br>Want me to break down how to start with any of these?";
      } 
      else if (message.toLowerCase().includes('affiliate') || 
              message.toLowerCase().includes('commission')) {
        response = "Forget Amazon's puny 3-4% commissions! Focus on these high-commission programs:<br><br>1. <strong>4Patriots</strong> - 25% commission ($49+ per sale)<br>2. <strong>Bluetti Power</strong> - 20-25% ($60-120 per sale)<br>3. <strong>Survival Frog</strong> - 15-20% ($30-45 per sale)<br><br>I can show you my top earner if you're interested.";
        
        // Add product recommendation
        setTimeout(() => {
          appendProductSuggestion('4patriots-food');
        }, 1000);
      }
      else if (message.toLowerCase().includes('power') || 
              message.toLowerCase().includes('battery') || 
              message.toLowerCase().includes('charging')) {
        response = "Power is CRITICAL for camping success. I recommend the Jackery Explorer 240 - it's what I use daily for my gear, lights, and content creation equipment. At $199 it pays for itself quickly if you're creating content.";
        
        // Add product recommendation
        setTimeout(() => {
          appendProductSuggestion('jackery-explorer-240');
        }, 1000);
      }
      else if (message.toLowerCase().includes('water') || 
              message.toLowerCase().includes('drink') || 
              message.toLowerCase().includes('filter')) {
        response = "For water filtration, I've tested dozens of systems. The LifeStraw is unbeatable for value and reliability - filters 99.9999% of bacteria and parasites. Plus it makes for super viral demonstration videos that earn affiliate commissions.";
        
        // Add product recommendation
        setTimeout(() => {
          appendProductSuggestion('lifestraw-filter');
        }, 1000);
      }
      else if (message.toLowerCase().includes('food') || 
              message.toLowerCase().includes('eat') || 
              message.toLowerCase().includes('meal')) {
        response = "For food when camping, I keep it simple: cooking basics plus emergency backup. The 4Patriots kit is my #1 recommendation - 25-year shelf life and tastes way better than you'd expect. Plus it has a 25% commission rate versus Amazon's 3-4%.";
        
        // Add product recommendation
        setTimeout(() => {
          appendProductSuggestion('4patriots-food');
        }, 1000);
      }
      else if (productMatch) {
        // If we detected a product keyword but didn't hit the specific conditions above
        response = "I know exactly what you need. Let me show you my personal recommendation:";
        
        // Add product recommendation
        setTimeout(() => {
          appendProductSuggestion(productMatch);
        }, 1000);
      }
      else {
        // Default responses with revenue-generating paths
        const responses = [
          `Good question! While we're talking about camping, many people ask me how I make $1000+/month while living off-grid. Want me to share my method?`,
          `I can help with that! By the way, have you seen the gear that's helped me make a consistent income while camping? I can show you my top picks.`,
          `I've got some thoughts on that! Most campers I talk to are also interested in how to make money while traveling. Should I share some tips about that too?`
        ];
        response = responses[Math.floor(Math.random() * responses.length)];
        
        // 30% chance to show a revenue path suggestion
        if (Math.random() < 0.3) {
          setTimeout(() => {
            appendRevenuePathSuggestions();
          }, 1500);
        }
      }
      
      // Display bot response
      appendMessage(response, 'incoming');
    }, 1000); // Simulate thinking time
  }
  
  // Append message to chat
  function appendMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `guerilla-message guerilla-${type}`;
    
    if (type === 'incoming') {
      // Bot message with avatar
      messageDiv.innerHTML = `
        <img src="${window.location.origin}/static/images/guerilla-mascot.png" class="guerilla-msg-avatar">
        <div class="guerilla-msg-content">
          <p>${message}</p>
        </div>
      `;
    } else {
      // User message
      messageDiv.innerHTML = `
        <div class="guerilla-msg-content">
          <p>${message}</p>
        </div>
      `;
    }
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
  }
  
  // Append typing indicator
  function appendTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'guerilla-message guerilla-incoming guerilla-typing';
    typingDiv.innerHTML = `
      <img src="${window.location.origin}/static/images/guerilla-mascot.png" class="guerilla-msg-avatar">
      <div class="guerilla-msg-content">
        <div class="guerilla-typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>
    `;
    messagesContainer.appendChild(typingDiv);
    scrollToBottom();
  }
  
  // Remove typing indicator
  function removeTypingIndicator() {
    const typingIndicator = document.querySelector('.guerilla-typing');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }
  
  // Append product suggestion
  function appendProductSuggestion(productId) {
    if (!products[productId]) return;
    
    const product = products[productId];
    const suggestionDiv = document.createElement('div');
    suggestionDiv.className = 'guerilla-message guerilla-incoming guerilla-product-suggestion';
    suggestionDiv.innerHTML = `
      <img src="${window.location.origin}/static/images/guerilla-mascot.png" class="guerilla-msg-avatar">
      <div class="guerilla-msg-content">
        <p>Here's what I personally use and recommend:</p>
        <div style="margin-top:10px; display:flex; gap:10px; align-items:center;">
          <img src="${product.image}" style="width:60px; height:60px; object-fit:contain; border-radius:5px;">
          <div>
            <strong>${product.name}</strong>
            <div>${product.price} <span style="text-decoration:line-through;color:#aaa;font-size:0.9em;">${product.originalPrice}</span></div>
          </div>
        </div>
        <div class="guerilla-suggestion-actions">
          <button class="guerilla-suggestion-btn" onclick="showProductRecommendation('${productId}')">View Details</button>
          <button class="guerilla-suggestion-btn guerilla-suggestion-secondary">No Thanks</button>
        </div>
      </div>
    `;
    
    messagesContainer.appendChild(suggestionDiv);
    scrollToBottom();
    
    // Track in analytics
    trackEvent('guerilla_product_suggestion', {
      product_id: productId,
      product_name: product.name
    });
  }
  
  // Append revenue path suggestions
  function appendRevenuePathSuggestions() {
    // Select 3 random revenue paths
    const selectedPaths = revenuePaths
      .sort(() => 0.5 - Math.random())
      .slice(0, 3);
    
    const suggestionDiv = document.createElement('div');
    suggestionDiv.className = 'guerilla-message guerilla-incoming';
    
    let buttonsHtml = '';
    selectedPaths.forEach(path => {
      buttonsHtml += `<button class="guerilla-suggestion-btn" onclick="userSendMessage('${path}')">${path}</button>`;
    });
    
    suggestionDiv.innerHTML = `
      <img src="${window.location.origin}/static/images/guerilla-mascot.png" class="guerilla-msg-avatar">
      <div class="guerilla-msg-content">
        <p>Many campers also ask me:</p>
        <div class="guerilla-suggestion-actions" style="flex-direction:column; align-items:flex-start;">
          ${buttonsHtml}
        </div>
      </div>
    `;
    
    messagesContainer.appendChild(suggestionDiv);
    scrollToBottom();
    
    // Track in analytics
    trackEvent('guerilla_revenue_paths_shown');
  }
  
  // Scroll to bottom of chat
  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  // Helper to generate random numbers
  function generateRandomNumber(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }
  
  // Track events in Google Analytics and/or other analytics tools
  function trackEvent(eventName, params = {}) {
    // Google Analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', eventName, params);
    }
    
    // Microsoft Clarity (custom event)
    if (typeof clarity !== 'undefined') {
      clarity('set', eventName, params);
    }
    
    // Log to console in development
    console.log(`[Guerilla Analytics] ${eventName}`, params);
  }
  
  // Make these functions globally available
  window.showProductRecommendation = function(productId) {
    if (!products[productId]) return;
    
    const product = products[productId];
    
    // Build modal content
    modalBody.innerHTML = `
      <div class="guerilla-product-card">
        <div class="guerilla-product-header">
          <img src="${product.image}" class="guerilla-product-image">
          <div class="guerilla-product-info">
            <div>
              <h2 class="guerilla-product-title">${product.name}</h2>
              <div class="guerilla-product-badges">
                ${product.badges.map(badge => `<span class="guerilla-badge">${badge}</span>`).join('')}
              </div>
              <div class="guerilla-product-price">
                <span class="original">${product.originalPrice}</span>
                <span class="discounted">${product.price}</span>
              </div>
            </div>
            
            <div class="guerilla-live-visitors">
              <span class="dot"></span>
              <span>${product.visitors} people viewing this right now</span>
            </div>
          </div>
        </div>
        
        <p class="guerilla-product-desc">${product.description}</p>
        
        <div class="guerilla-testimonial">
          ${product.testimonial}
        </div>
        
        <div class="guerilla-countdown">
          <span>Limited-time offer ends in:</span>
          <div class="guerilla-countdown-timer" id="product-countdown">23:59:59</div>
        </div>
        
        <div class="guerilla-buttons">
          <a href="${product.link}" class="guerilla-buy-btn" target="_blank" rel="noopener" 
             onclick="trackProductClick('${productId}')">
            GET THIS DEAL
          </a>
          <button class="guerilla-wishlist-btn">Save for Later</button>
        </div>
        
        <div class="guerilla-guarantee">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>Only ${product.inventory} left at this price</span>
        </div>
      </div>
    `;
    
    // Display modal
    modal.style.display = 'block';
    
    // Start countdown timer
    startProductCountdown();
    
    // Track in analytics
    trackEvent('guerilla_product_view', {
      product_id: productId,
      product_name: product.name
    });
  };
  
  window.trackProductClick = function(productId) {
    if (!products[productId]) return;
    
    // Track in analytics
    trackEvent('guerilla_product_click', {
      product_id: productId,
      product_name: products[productId].name,
      product_price: products[productId].price
    });
  };
  
  window.userSendMessage = function(message) {
    // Display user message
    appendMessage(message, 'outgoing');
    
    // Process message
    processMessage(message);
    
    // Track in analytics
    trackEvent('guerilla_suggested_path_click', {
      message: message
    });
  };
  
  // Start product countdown
  function startProductCountdown() {
    const countdownEl = document.getElementById('product-countdown');
    if (!countdownEl) return;
    
    // Generate random hours (3-23) for urgency
    const hours = generateRandomNumber(3, 23);
    const minutes = generateRandomNumber(0, 59);
    const seconds = generateRandomNumber(0, 59);
    
    let totalSeconds = hours * 3600 + minutes * 60 + seconds;
    
    const interval = setInterval(() => {
      totalSeconds--;
      
      if (totalSeconds <= 0) {
        clearInterval(interval);
        countdownEl.textContent = "EXPIRED";
        return;
      }
      
      const h = Math.floor(totalSeconds / 3600);
      const m = Math.floor((totalSeconds % 3600) / 60);
      const s = totalSeconds % 60;
      
      countdownEl.textContent = 
        String(h).padStart(2, '0') + ':' +
        String(m).padStart(2, '0') + ':' +
        String(s).padStart(2, '0');
      
      // Add urgency effect when under 1 hour
      if (h < 1 && totalSeconds % 10 === 0) {
        countdownEl.style.fontSize = '20px';
        setTimeout(() => {
          countdownEl.style.fontSize = '18px';
        }, 500);
      }
    }, 1000);
  }
  
  // Show a notification after 30 seconds if chat is not open
  setTimeout(() => {
    if (chatContainer.style.display !== 'flex') {
      notification.style.display = 'flex';
      toggle.classList.add('guerilla-breathing');
    }
  }, 30000);
});
