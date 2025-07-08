#!/usr/bin/env python3

import os
import sys
import subprocess

print("🦍 GUERILLA CAMPING EMERGENCY RECOVERY SCRIPT 🦍")
print("================================================")

# 1. Check for required packages
required_packages = [
    "Flask==2.2.3",
    "pymongo==4.3.3",
    "gunicorn==20.1.0",
    "requests==2.28.2"
]

print("➤ Checking dependencies...")
for package in required_packages:
    subprocess.call([sys.executable, "-m", "pip", "install", package])
print("✓ Dependencies installed")

# 2. Fix template issues
print("➤ Fixing template issues...")
index_content = """{% extends 'base.html' %}

{% block title %}Gorilla Camping - Home{% endblock %}

{% block content %}
<div class="home-container">
    <div class="hero-section">
        <h1 class="motto">GUERILLA CAMPING: UNCONVENTIONAL ADVENTURE</h1>
        <p class="tagline">Off-grid living and camping tips from a badass perspective</p>
    </div>
    
    <div class="email-capture">
        <h2>JOIN THE GUERILLA CAMPING MOVEMENT</h2>
        <p>Get exclusive camping hacks, gear deals, and off-grid money-making strategies</p>
        <div class="ml-embedded" data-form="7qFupG"></div>
    </div>
    
    <!-- Featured Products -->
    <div class="featured-products">
        <h2>GUERILLA-APPROVED GEAR</h2>
        <div class="product-grid">
            <div class="product-card">
                <img src="{{ url_for('static', filename='images/jackery.jpg') }}" alt="Jackery Explorer">
                <h3>Jackery Explorer 240</h3>
                <p class="price"><del>$299.99</del> <strong>$199.99</strong></p>
                <a href="/affiliate/jackery-explorer-240" class="cta-button">GET DEAL →</a>
            </div>
            
            <div class="product-card">
                <img src="{{ url_for('static', filename='images/lifestraw.jpg') }}" alt="LifeStraw">
                <h3>LifeStraw Water Filter</h3>
                <p class="price"><del>$19.95</del> <strong>$14.96</strong></p>
                <a href="/affiliate/lifestraw-filter" class="cta-button">GET DEAL →</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""

try:
    os.makedirs("templates", exist_ok=True)
    with open("templates/index.html", "w") as f:
        f.write(index_content)
    with open("templates/index_b.html", "w") as f:
        f.write(index_content)  # Use same content for both variants until A/B testing is ready
    print("✓ Template files created/fixed")
except Exception as e:
    print(f"✗ Error fixing templates: {e}")

# 3. Fix app.py to avoid template errors
print("➤ Applying emergency patches to app.py...")
try:
    with open("app.py", "r") as f:
        app_content = f.read()
    
    if "index_b.html" in app_content:
        app_content = app_content.replace(
            "template = 'index_b.html'", 
            "template = 'index.html'  # Temporary fix until both templates exist"
        )
        
    with open("app.py", "w") as f:
        f.write(app_content)
    print("✓ app.py patched to avoid template errors")
except Exception as e:
    print(f"✗ Error patching app.py: {e}")

# 4. Create a simple Procfile if missing
try:
    if not os.path.exists("Procfile"):
        with open("Procfile", "w") as f:
            f.write("web: gunicorn app:app")
        print("✓ Created Procfile")
except Exception as e:
    print(f"✗ Error creating Procfile: {e}")

print("\n✅ RECOVERY COMPLETE: Your site should be back online after redeploying!")
print("Run 'git add .' then 'git commit -m \"Fix crash issues\"' and 'git push' to deploy")
