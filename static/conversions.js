/**
 * Gorilla Camping Conversion Optimization Framework
 * Implements split testing and conversion tracking for higher affiliate revenue
 */

// Configuration
const VARIANTS = {
  'button-color': ['#00ff88', '#ff4500', '#1e90ff'],
  'countdown': ['visible', 'hidden'],
  'urgency-text': [
    'Limited Time Offer', 
    'Almost Sold Out', 
    'Deal Ends Soon',
    'X Left at This Price'
  ]
};

// User segmentation (simple but effective)
function getUserSegment() {
  let userId = localStorage.getItem('gc_user_id');
  if (!userId) {
    userId = Math.random().toString(36).substring(2, 15);
    localStorage.setItem('gc_user_id', userId);
  }
  
  // Get consistent variant for this user
  const variantMap = {};
  for (const [testName, options] of Object.entries(VARIANTS)) {
    const hash = hashCode(userId + testName) % options.length;
    variantMap[testName] = options[Math.abs(hash)];
  }
  
  return {
    userId,
    variants: variantMap
  };
}

// Apply variants to page
function applyVariants() {
  const segment = getUserSegment();
  
  // Button color variant
  document.querySelectorAll('.affiliate-link, .gear-button, .cta-button').forEach(button => {
    button.style.background = segment.variants['button-color'];
    
    // Track which variant was shown
    button.setAttribute('data-variant-button', segment.variants['button-color']);
  });
  
  // Countdown visibility
  if (segment.variants['countdown'] === 'hidden') {
    document.querySelectorAll('.countdown, [id^=countdown]').forEach(el => {
      el.style.display = 'none';
    });
  }
  
  // Urgency text
  document.querySelectorAll('.urgency-badge').forEach(badge => {
    badge.textContent = segment.variants['urgency-text'];
    badge.setAttribute('data-variant-urgency', segment.variants['urgency-text']);
  });
  
  // Log impression for analysis
  trackEvent('variant_impression', {
    userId: segment.userId,
    variants: segment.variants,
    page: window.location.pathname
  });
}

// Track conversions and events
function trackEvent(eventName, data = {}) {
  // Send to Google Analytics if available
  if (typeof gtag !== 'undefined') {
    gtag('event', eventName, data);
  }
  
  // Also store locally for backup
  const events = JSON.parse(localStorage.getItem('gc_events') || '[]');
  events.push({
    event: eventName,
    data: data,
    timestamp: new Date().toISOString()
  });
  localStorage.setItem('gc_events', JSON.stringify(events));
}

// Track affiliate clicks with variant data
document.addEventListener('DOMContentLoaded', function() {
  // Apply variants
  applyVariants();
  
  // Track affiliate clicks
  document.querySelectorAll('.affiliate-link, [href*="amzn.to"], [href*="amazon.com"]').forEach(link => {
    link.addEventListener('click', function(e) {
      const segment = getUserSegment();
      
      trackEvent('affiliate_click', {
        userId: segment.userId,
        variants: segment.variants,
        product: this.getAttribute('data-product') || this.innerText,
        url: this.href
      });
    });
  });
});

// Helper function for consistent hashing
function hashCode(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return hash;
}
