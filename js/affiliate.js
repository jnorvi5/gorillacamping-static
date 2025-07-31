/**
 * Guerilla Camping Affiliate Tracker
 * Tracks affiliate link clicks and handles redirects
 */

document.addEventListener('DOMContentLoaded', function() {
  // Find all affiliate links
  const affiliateLinks = document.querySelectorAll('a[href^="/affiliate/"]');
  
  // Add click handler to each link
  affiliateLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Extract product ID from URL
      const productId = this.href.split('/affiliate/')[1];
      
      // Track click with API
      window.gorillaCampingAPI.trackAffiliateClick(productId).then(() => {
        // After tracking, redirect to the original destination
        window.location.href = this.href;
      }).catch(() => {
        // If tracking fails, still redirect
        window.location.href = this.href;
      });
    });
  });
});
