/**
 * Gorilla Camping - Analytics & Tracking
 * STATIC SITE: This file belongs in gorillacamping-static/js/analytics.js
 */

// Initialize Google Analytics
function initAnalytics() {
    // Load Google Analytics
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${CONFIG.GA_ID}`;
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', CONFIG.GA_ID, {
        'custom_map': {
            'dimension1': 'user_type',
            'dimension2': 'traffic_source'
        }
    });
    
    // Set custom dimensions
    const userType = localStorage.getItem('user_type') || 'new';
    const trafficSource = sessionStorage.getItem('traffic_source') || document.referrer || 'direct';
    
    gtag('set', 'user_type', userType);
    gtag('set', 'traffic_source', trafficSource);
    
    // Mark as initialized
    window.analyticsInitialized = true;
}

// Track page view
function trackPageView(pageName = null, pageData = {}) {
    if (!window.analyticsInitialized) initAnalytics();
    
    const data = {
        page_title: pageName || document.title,
        page_location: window.location.href,
        page_path: window.location.pathname,
        ...pageData
    };
    
    // Send to Google Analytics
    if (typeof gtag === 'function') {
        gtag('event', 'page_view', data);
    }
    
    // Track with backend for custom analytics
    try {
        navigator.sendBeacon(`${CONFIG.API_URL}/api/track-view`, 
            JSON.stringify({
                page: window.location.pathname,
                referrer: document.referrer,
                data: pageData
            })
        );
    } catch(e) {
        console.log('Error tracking view', e);
    }
}

// Track affiliate clicks
function trackAffiliateClick(productId, productName, position = 'unknown') {
    if (!window.analyticsInitialized) initAnalytics();
    
    // Track with Google Analytics
    if (typeof gtag === 'function') {
        gtag('event', 'affiliate_click', {
            'event_category': 'Affiliate',
            'event_label': productName,
            'value': 1,
            'position': position
        });
    }
    
    // Track with backend
    try {
        navigator.sendBeacon(`${CONFIG.API_URL}/api/affiliate-click`, 
            JSON.stringify({
                product_id: productId,
                product_name: productName,
                position: position,
                source: window.location.pathname
            })
        );
    } catch(e) {
        console.log('Error tracking affiliate click', e);
    }
    
    return true; // Allow the default link action
}

// Track social media clicks
function trackSocialClick(platform, action = 'click') {
    if (!window.analyticsInitialized) initAnalytics();
    
    // Track with Google Analytics
    if (typeof gtag === 'function') {
        gtag('event', 'social_click', {
            'event_category': 'Social',
            'event_label': platform,
            'value': 1,
            'action': action
        });
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize analytics
    initAnalytics();
    
    // Track page view on load
    trackPageView();
    
    // Check UTM parameters
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('utm_source')) {
        sessionStorage.setItem('traffic_source', urlParams.get('utm_source'));
        sessionStorage.setItem('utm_medium', urlParams.get('utm_medium'));
        sessionStorage.setItem('utm_campaign', urlParams.get('utm_campaign'));
    }
    
    // If new user, update user type
    if (!localStorage.getItem('user_type')) {
        localStorage.setItem('user_type', 'new');
        localStorage.setItem('first_visit', new Date().toISOString());
    }
    
    // Update last visit
    localStorage.setItem('last_visit', new Date().toISOString());
});
