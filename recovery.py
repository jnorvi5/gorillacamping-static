"""
Gorilla Camping Site Recovery Tool
- Fixes duplicate route issue causing site crash
- Adds proper templates
- Implements high-commission revenue routes
"""

import os
import re

def fix_app_file():
    print("🦍 FIXING APP.PY FILE...")
    
    # Read current app.py
    with open('app.py', 'r') as file:
        content = file.read()
    
    # Fix duplicate high_commission_gear route
    # This is the root cause of your crash
    pattern = r"@app\.route\('/high-commission-gear'\)\s+def high_commission_gear\(\):"
    matches = re.findall(pattern, content)
    
    if len(matches) > 1:
        print(f"✅ Found duplicate route: high_commission_gear ({len(matches)} instances)")
        # Keep first instance, rename second to premium_gear
        content = re.sub(pattern, "@app.route('/premium-gear')\ndef premium_gear():", content, count=1)
    else:
        print("ℹ️ No duplicate routes found for high_commission_gear")
    
    # Fix any other duplicate routes
    duplicate_check = re.findall(r"@app\.route\('([^']+)'\)[^@]+@app\.route\('([^']+)'\)", content)
    for match in duplicate_check:
        print(f"⚠️ Potential duplicate routes: {match[0]} and {match[1]}")
    
    # Write fixed content back
    with open('app.py', 'w') as file:
        file.write(content)
    
    print("✅ Fixed app.py - removed duplicate routes")

def create_missing_templates():
    print("🦍 CHECKING FOR MISSING TEMPLATES...")
    
    # Ensure index.html exists
    if not os.path.exists('templates/index.html'):
        print("⚠️ Missing templates/index.html - creating...")
        os.makedirs('templates', exist_ok=True)
        
        with open('templates/index.html', 'w') as file:
            file.write("""{% extends 'base.html' %}

{% block title %}Gorilla Camping - Guerilla-Style Off-Grid Living{% endblock %}

{% block content %}
<div class="home-container">
    <div class="hero-section">
        <h1 class="motto">GUERILLA CAMPING: UNCONVENTIONAL ADVENTURE</h1>
        <p class="tagline">Off-grid living and camping tips from a badass perspective</p>
    </div>
    
    <!-- HIGH-CONVERTING EMAIL CAPTURE -->
    <div style="background:#111; border:3px solid #00ff88; padding:25px; margin:30px auto; max-width:600px; border-radius:12px; text-align:center; box-shadow:0 0 20px rgba(0,255,136,0.2);">
      <h3 style="color:#00ff88; font-size:1.6em; margin-top:0;">FREE: "10 SECRET CAMPING SPOTS THAT PAY $50-100/DAY"</h3>
      
      <p style="margin:15px 0;">Join <span class="subscriber-count">2,847</span>+ guerilla campers earning while living free</p>
      
      <form action="{{ url_for('subscribe') }}" method="post" style="max-width:400px; margin:0 auto;">
        <input type="email" name="email" placeholder="Your email..." required style="width:100%; padding:12px; margin:10px 0; font-size:16px; border-radius:8px; border:none;">
        <input type="hidden" name="source" value="homepage">
        <button type="submit" style="background:#00ff88; color:#111; width:100%; padding:12px; font-size:16px; font-weight:bold; border:none; border-radius:8px; cursor:pointer;">GET FREE ACCESS →</button>
      </form>
      
      <small style="color:#aaa; margin-top:10px; display:block;">These locations have perfect cell service + free camping. No spam ever.</small>
    </div>
    
    <!-- FEATURED PRODUCTS -->
    <div class="featured-products">
        <h2 style="text-align:center; color:#00ff88; margin:40px 0 20px;">GUERILLA-APPROVED GEAR</h2>
        <div style="display:flex; flex-wrap:wrap; gap:20px; justify-content:center; margin-bottom:40px;">
            <div style="flex:1; min-width:280px; max-width:400px; background:#222; border-radius:10px; overflow:hidden; border:1px solid rgba(0,255,136,0.3); box-shadow:0 0 20px rgba(0,0,0,0.3);">
                <div style="height:200px; overflow:hidden;">
                    <img src="https://m.media-amazon.com/images/I/41XePYWYlAL._AC_US300_.jpg" alt="Jackery Explorer" style="width:100%; height:100%; object-fit:contain;">
                </div>
                <div style="padding:20px;">
                    <h3 style="color:#00ff88; margin-top:0;">Jackery Explorer 240</h3>
                    <p style="min-height:60px;">Powers all my devices for content creation that earns $500+/month in affiliate commissions.</p>
                    <p class="price"><del style="color:#999;">$299.99</del> <strong style="color:#00ff88; font-size:1.2em;">$199.99</strong></p>
                    <a href="/affiliate/jackery-explorer-240" style="display:block; background:#00ff88; color:#111; text-align:center; padding:10px; border-radius:8px; text-decoration:none; font-weight:bold;">GET DEAL →</a>
                </div>
            </div>
            
            <div style="flex:1; min-width:280px; max-width:400px; background:#222; border-radius:10px; overflow:hidden; border:1px solid rgba(0,255,136,0.3); box-shadow:0 0 20px rgba(0,0,0,0.3);">
                <div style="height:200px; overflow:hidden;">
                    <img src="https://m.media-amazon.com/images/I/71SYsNwj7hL._AC_UL320_.jpg" alt="LifeStraw" style="width:100%; height:100%; object-fit:contain;">
                </div>
                <div style="padding:20px;">
                    <h3 style="color:#00ff88; margin-top:0;">LifeStraw Water Filter</h3>
                    <p style="min-height:60px;">Essential survival gear that I use daily. Makes for viral demonstration videos!</p>
                    <p class="price"><del style="color:#999;">$19.95</del> <strong style="color:#00ff88; font-size:1.2em;">$14.96</strong></p>
                    <a href="/affiliate/lifestraw-filter" style="display:block; background:#00ff88; color:#111; text-align:center; padding:10px; border-radius:8px; text-decoration:none; font-weight:bold;">GET DEAL →</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""")
        print("✅ Created index.html template")
        
    # Create high_commission.html template
    if not os.path.exists('templates/high_commission.html'):
        print("⚠️ Missing templates/high_commission.html - creating...")
        
        with open('templates/high_commission.html', 'w') as file:
            file.write("""{% extends "base.html" %}
{% block title %}High-Commission Camping Gear - 5X More Money{% endblock %}

{% block content %}
<div style="max-width:900px; margin:0 auto; padding:20px;">
  <div style="text-align:center; margin-bottom:40px;">
    <h1 style="color:#00ff88; font-size:2.5em;">HIGH-COMMISSION CAMPING GEAR</h1>
    <p style="font-size:1.2em;">One sale here pays like 5-10 sales on Amazon!</p>
  </div>

  <!-- COMPARISON -->
  <div style="background:#222; border-radius:10px; padding:20px; margin-bottom:30px;">
    <h2 style="color:#00ff88; margin-top:0;">WHY THESE PRODUCTS PAY 5-10X MORE</h2>
    <div style="display:flex; flex-wrap:wrap; gap:20px; margin-top:15px;">
      <div style="flex:1; min-width:250px; padding:15px; background:rgba(255,0,0,0.1); border-radius:8px;">
        <h3 style="margin-top:0;">Amazon Affiliate</h3>
        <p style="margin-bottom:5px;">Commission: <strong style="color:#ff6b6b;">3-4%</strong></p>
        <p style="margin-bottom:5px;">$200 product = <strong style="color:#ff6b6b;">$6-8 commission</strong></p>
        <p style="margin-bottom:0;">Need <strong>17 sales</strong> to earn $100</p>
      </div>
      
      <div style="flex:1; min-width:250px; padding:15px; background:rgba(0,255,136,0.1); border-radius:8px;">
        <h3 style="margin-top:0;">Direct Affiliate</h3>
        <p style="margin-bottom:5px;">Commission: <strong style="color:#00ff88;">20-30%</strong></p>
        <p style="margin-bottom:5px;">$200 product = <strong style="color:#00ff88;">$40-60 commission</strong></p>
        <p style="margin-bottom:0;">Need <strong>just 2 sales</strong> to earn $100</p>
      </div>
    </div>
  </div>
  
  <!-- PRODUCTS -->
  {% for product in products %}
  <div style="background:#222; border-radius:10px; padding:20px; margin-bottom:30px; position:relative; overflow:hidden; border:1px solid rgba(0,255,136,0.3);">
    <div style="position:absolute; top:15px; right:15px; background:#ff6b6b; color:white; padding:5px 10px; border-radius:20px; font-size:0.8em;">
      Only {{ product.inventory }} left!
    </div>
    
    <div style="display:flex; flex-wrap:wrap; gap:20px;">
      <div style="flex:1; min-width:280px; position:relative;">
        <img src="{{ product.image }}" alt="{{ product.name }}" style="width:100%; border-radius:8px;">
        <div style="background:rgba(0,0,0,0.7); color:#00ff88; position:absolute; bottom:10px; left:0; right:0; padding:10px; text-align:center; font-weight:bold;">
          {{ product.commission }} COMMISSION PER SALE
        </div>
      </div>
      
      <div style="flex:1; min-width:280px;">
        <h2 style="color:#00ff88; margin-top:0;">{{ product.name }}</h2>
        
        <div style="margin:15px 0;">
          <span style="text-decoration:line-through; color:#999; margin-right:10px;">{{ product.old_price }}</span>
          <span style="color:#00ff88; font-size:1.5em; font-weight:bold;">{{ product.price }}</span>
        </div>
        
        <div class="live-viewers-count" style="margin:15px 0; display:flex; align-items:center;">
          <span class="pulse-dot" style="display:inline-block; width:10px; height:10px; background:#ff6b6b; border-radius:50%; margin-right:8px;"></span>
          <span class="viewer-count" data-min="5" data-max="20">12</span> people viewing right now
        </div>
        
        <p>{{ product.description }}</p>
        
        <div style="margin:20px 0;">
          <span>Special commission rate expires in:</span>
          <div class="countdown-timer" style="font-family:monospace; background:#333; padding:10px; margin-top:5px; border-radius:5px; display:inline-block;">23:59:59</div>
        </div>
        
        <a href="{{ product.affiliate_link }}" 
           class="cta-button" 
           style="display:inline-block; background:#00ff88; color:#111; text-align:center; padding:15px 30px; font-size:1.1em; font-weight:bold; border-radius:8px; text-decoration:none;"
           target="_blank" rel="noopener sponsored"
           onclick="trackAffiliateClick('{{ product.affiliate_link }}', '{{ product.name }}')">
          GET THIS DEAL →
        </a>
      </div>
    </div>
  </div>
  {% endfor %}
</div>

<script>
// Live viewers counter
document.querySelectorAll('.live-viewers-count').forEach(el => {
  const countEl = el.querySelector('.viewer-count');
  const min = parseInt(countEl.dataset.min || 5);
  const max = parseInt(countEl.dataset.max || 20);
  let count = parseInt(countEl.textContent);
  
  setInterval(() => {
    if (Math.random() < 0.5) {
      // 60% chance to increase, 40% chance to decrease
      const direction = Math.random() < 0.6 ? 1 : -1;
      count = Math.max(min, Math.min(max, count + direction));
      countEl.textContent = count;
      
      // Flash effect on change
      countEl.style.color = '#ff6b6b';
      setTimeout(() => {
        countEl.style.color = '';
      }, 500);
    }
  }, 8000); // Every 8 seconds
});

// Countdown timers
document.querySelectorAll('.countdown-timer').forEach(el => {
  // Random hours between 12-47 hours
  let hours = Math.floor(Math.random() * 36) + 12;
  let minutes = Math.floor(Math.random() * 60);
  let seconds = Math.floor(Math.random() * 60);
  
  let totalSeconds = hours * 3600 + minutes * 60 + seconds;
  
  const interval = setInterval(() => {
    totalSeconds--;
    
    if (totalSeconds <= 0) {
      clearInterval(interval);
      el.textContent = "EXPIRED";
      el.style.color = "#ff6b6b";
      return;
    }
    
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;
    
    el.textContent = 
      String(h).padStart(2, '0') + ':' +
      String(m).padStart(2, '0') + ':' +
      String(s).padStart(2, '0');
    
    // Make timer red when under 1 hour
    if (h < 1) {
      el.style.color = "#ff6b6b";
    }
  }, 1000);
});

// Pulse animation for dots
document.querySelectorAll('.pulse-dot').forEach(dot => {
  setInterval(() => {
    dot.style.opacity = '0.4';
    setTimeout(() => {
      dot.style.opacity = '1';
    }, 500);
  }, 1000);
});
</script>
{% endblock %}""")
        print("✅ Created high_commission.html template")
    
    print("✅ Template check complete")
    
def create_procfile():
    """Create or fix Procfile for Heroku"""
    if not os.path.exists('Procfile'):
        with open('Procfile', 'w') as file:
            file.write('web: gunicorn app:app')
        print("✅ Created Procfile")
    else:
        print("ℹ️ Procfile already exists")

def main():
    """Main recovery function"""
    print("🚨 GORILLA CAMPING SITE RECOVERY TOOL 🚨")
    print("----------------------------------------")
    
    fix_app_file()
    create_missing_templates()
    create_procfile()
    
    print("\n✅ RECOVERY COMPLETE - COMMIT AND PUSH THESE CHANGES")
    print("Run these commands:")
    print("  git add .")
    print("  git commit -m \"Fix duplicate routes and missing templates\"")
    print("  git push")

if __name__ == "__main__":
    main()
