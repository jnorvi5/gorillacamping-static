@app.route('/pinterest-strategy')
def pinterest_strategy():
    """Leverage free Canva Pro from GitHub Student Pack for viral Pinterest pins"""
    # Canva Pro strategy for creating viral Pinterest pins that drive affiliate traffic
    pin_strategies = [
        {
            "title": "Top 10 Essential Camping Gadgets",
            "template": "Top 10 List Template",
            "target": "Camping and outdoor enthusiasts",
            "affiliate_products": ["Jackery Explorer", "LifeStraw", "Solo Stove"],
            "monthly_views": "50,000-100,000",
            "conversion_rate": "2.5%",
            "estimated_revenue": "$125-250/month"
        },
        {
            "title": "DIY Off-Grid Solar Setup Guide",
            "template": "Step-by-Step Guide Template",
            "target": "Off-grid enthusiasts and preppers",
            "affiliate_products": ["Jackery Explorer", "Solar panels", "Battery banks"],
            "monthly_views": "25,000-75,000",
            "conversion_rate": "3.8%",
            "estimated_revenue": "$95-285/month"
        },
        {
            "title": "Emergency Food Supply Comparison",
            "template": "Comparison Chart Template",
            "target": "Preppers and emergency planners",
            "affiliate_products": ["4Patriots Food Kits", "Emergency water filters"],
            "monthly_views": "15,000-45,000", 
            "conversion_rate": "4.2%",
            "estimated_revenue": "$180-540/month"
        }
    ]
    
    return render_template('pinterest_strategy.html', strategies=pin_strategies)
