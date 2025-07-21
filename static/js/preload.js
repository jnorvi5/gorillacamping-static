/**
 * Gorilla Camping - Preloader for API Data
 * STATIC SITE: This file belongs in gorillacamping-static/js/preload.js
 */

document.addEventListener('DOMContentLoaded', function() {
    // Only preload if caching is enabled in config
    if (!CONFIG || !CONFIG.ENABLE_CACHING) return;
    
    const CACHE_TTL = CONFIG.CACHE_TTL || 300000; // 5 minutes default
    const now = new Date().getTime();
    
    // Function to check if data is stale
    function isStale(timestamp) {
        return !timestamp || (now - parseInt(timestamp) > CACHE_TTL);
    }
    
    // Preload blog posts if needed
    const blogCachedTime = localStorage.getItem('blog_posts_timestamp');
    if (isStale(blogCachedTime)) {
        console.log('Preloading blog posts...');
        fetch(`${CONFIG.API_URL}/api/blog-posts`)
            .then(res => {
                if (!res.ok) throw new Error('Network response failed');
                return res.json();
            })
            .then(posts => {
                localStorage.setItem('blog_posts', JSON.stringify(posts));
                localStorage.setItem('blog_posts_timestamp', now.toString());
                console.log('✓ Blog posts cached successfully');
            })
            .catch(e => {
                console.log('Error preloading blog posts:', e.message);
            });
    }
    
    // Preload gear items if needed
    const gearCachedTime = localStorage.getItem('gear_items_timestamp');
    if (isStale(gearCachedTime)) {
        console.log('Preloading gear data...');
        fetch(`${CONFIG.API_URL}/api/gear`)
            .then(res => {
                if (!res.ok) throw new Error('Network response failed');
                return res.json();
            })
            .then(gear => {
                localStorage.setItem('gear_items', JSON.stringify(gear));
                localStorage.setItem('gear_items_timestamp', now.toString());
                console.log('✓ Gear items cached successfully');
            })
            .catch(e => {
                console.log('Error preloading gear:', e.message);
            });
    }
    
    // Prefetch common resources
    ['/img/logo.png', '/css/guerilla.css'].forEach(url => {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = url;
        document.head.appendChild(link);
    });
});
