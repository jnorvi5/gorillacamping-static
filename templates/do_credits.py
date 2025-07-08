"""
DigitalOcean Credit Strategy - Use $100 Student Pack credits to host multiple sites

Each $5/mo droplet can host multiple Flask sites with uWSGI+Nginx
"""

DO_STRATEGY = [
    {
        "droplet": "Base Flask Server",
        "monthly_cost": "$5/mo (covered by Student Pack)",
        "sites_hosted": ["gorillacamping.site", "campinggeardeals.tech", "solargear.me"],
        "total_revenue": "$400-600/mo"
    },
    {
        "droplet": "Affiliate Microsites",
        "monthly_cost": "$5/mo (covered by Student Pack)",
        "sites_hosted": ["emergencyfoodkits.site", "offgridpower.tech", "campingsurvival.me"],
        "total_revenue": "$300-500/mo"
    },
    {
        "droplet": "Digital Product Server",
        "monthly_cost": "$5/mo (covered by Student Pack)",
        "sites_hosted": ["guerillabible.com", "campingtemplates.site", "offgridcourse.me"],
        "total_revenue": "$200-400/mo"
    }
]

# Implementation
"""
1. Create $5/mo droplets using Student Pack credits
2. Set up Nginx with multiple server blocks
3. Deploy Flask apps with uWSGI for each site
4. Point domains to the droplets
5. Monitor and optimize top performers
"""
