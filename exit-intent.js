let exitIntentShown = false;

document.addEventListener('mouseleave', function(e) {
    if (e.clientY <= 0 && !exitIntentShown) {
        exitIntentShown = true;
        showExitIntentPopup();
    }
});

function showExitIntentPopup() {
    const popup = document.createElement('div');
    popup.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; display: flex; align-items: center; justify-content: center;">
            <div style="background: white; padding: 30px; border-radius: 15px; max-width: 500px; text-align: center;">
                <h2 style="color: #ff4757; margin-bottom: 15px;">⚠️ WAIT! Don't Miss This!</h2>
                <p>Get my SECRET gear list that made me $5,000 in 90 days!</p>
                <button onclick="this.closest('div').remove()" style="background: #28a745; color: white; padding: 12px 25px; border: none; border-radius: 8px; font-weight: bold; margin: 10px;">GIVE ME THE LIST!</button>
                <br><small><a href="#" onclick="this.closest('div').remove()" style="color: #999;">No thanks, I'll figure it out myself</a></small>
            </div>
        </div>
    `;
    document.body.appendChild(popup);
}
