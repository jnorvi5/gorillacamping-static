// Price fluctuation simulator (builds urgency)
function simulatePriceChanges() {
    const priceElements = document.querySelectorAll('.new-price');
    priceElements.forEach(el => {
        const originalPrice = parseFloat(el.textContent.replace('$', ''));
        setInterval(() => {
            const fluctuation = (Math.random() - 0.5) * 2; // +/- $1
            const newPrice = (originalPrice + fluctuation).toFixed(2);
            el.textContent = '$' + newPrice;
        }, 30000); // Change every 30 seconds
    });
}

// Visitor counter (social proof)
function showVisitorCount() {
    const count = 847 + Math.floor(Math.random() * 50);
    document.querySelector('.visitor-count').textContent = count + ' people viewed this page today';
}

document.addEventListener('DOMContentLoaded', function() {
    simulatePriceChanges();
    showVisitorCount();
});
