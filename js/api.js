/**
 * Gorilla Camping API Connection
 * Handles all communication with the backend API
 */

const API_BASE_URL = 'https://gorillacamping.azurewebsites.net/api';

// API request wrapper with error handling
async function apiRequest(endpoint, options = {}) {
  try {
    const url = `${API_BASE_URL}/${endpoint}`;
    
    // Default options
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include cookies for auth
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    // Handle non-200 responses
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Request Failed:', error);
    // Return standardized error object
    return { error: true, message: error.message || 'API request failed' };
  }
}

// Guerilla AI Chat
async function sendChatMessage(message) {
  return apiRequest('guerilla-chat', {
    method: 'POST',
    body: JSON.stringify({ message })
  });
}

// Newsletter subscription
async function subscribeEmail(email) {
  return apiRequest('subscribe', {
    method: 'POST',
    body: JSON.stringify({ email })
  });
}

// Get blog posts
async function getBlogPosts() {
  return apiRequest('blog-posts');
}

// Get single blog post
async function getBlogPost(slug) {
  return apiRequest(`blog-post/${slug}`);
}

// Affiliate click tracking
async function trackAffiliateClick(productId, source = 'website') {
  return apiRequest('affiliate-click', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId, source })
  });
}

// Export all functions
window.gorillaCampingAPI = {
  sendChatMessage,
  subscribeEmail,
  getBlogPosts,
  getBlogPost,
  trackAffiliateClick
};
