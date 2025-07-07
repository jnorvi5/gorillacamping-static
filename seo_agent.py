# NEW FILE: seo_agent.py
import os
import requests
import random
import time
from datetime import datetime
from pymongo import MongoClient
from bs4 import BeautifulSoup

# MongoDB connection
MONGO_URI = os.environ.get("MONGODB_URI", "your_connection_string")
client = MongoClient(MONGO_URI)
db = client.get_database()

# Cloudflare API (free tier with GitHub Student Pack)
CLOUDFLARE_API_KEY = os.environ.get("CLOUDFLARE_API_KEY", "")
CLOUDFLARE_EMAIL = os.environ.get("CLOUDFLARE_EMAIL", "")
CLOUDFLARE_ZONE_ID = os.environ.get("CLOUDFLARE_ZONE_ID", "")

class SEOAgent:
    def __init__(self):
        self.target_keywords = [
            "guerilla camping", "camping affiliate", "camping money",
            "off grid camping income", "best camping gear", "survival gear affiliate",
            "make money camping", "camping blog income"
        ]
        
        self.last_update = datetime.now()
    
    def run(self):
        print("🔍 SEO Agent starting...")
        
        while True:
            try:
                self.audit_site_structure()
                self.optimize_meta_tags()
                self.check_competitor_backlinks()
                self.purge_cloudflare_cache()
                
                # Sleep for 24 hours
                time.sleep(86400)
                
            except Exception as e:
                print(f"🚨 SEO agent error: {e}")
                time.sleep(3600)  # Sleep for 1 hour on error
    
    def audit_site_structure(self):
        """Analyze site structure and suggest improvements"""
        print("🔍 Auditing site structure...")
        
        try:
            # Get all blog posts
            posts = list(db.posts.find())
            
            # Check for missing metadata
            missing_meta = []
            for post in posts:
                if not post.get("meta_description") or not post.get("tags"):
                    missing_meta.append(post["_id"])
                    
                    # Auto-generate metadata if missing
                    if not post.get("meta_description"):
                        # Simple extraction of first 160 characters
                        content = BeautifulSoup(post.get("content", ""), "html.parser").text
                        meta_desc = content[:160] + "..." if len(content) > 160 else content
                        
                        db.posts.update_one(
                            {"_id": post["_id"]},
                            {"$set": {"meta_description": meta_desc}}
                        )
            
            print(f"✅ Fixed metadata for {len(missing_meta)} posts")
            
            # Check internal linking
            self.analyze_internal_links(posts)
            
        except Exception as e:
            print(f"Audit error: {e}")
    
    def analyze_internal_links(self, posts):
        """Check and improve internal linking"""
        try:
            # Build keyword to post mapping
            keyword_map = {}
            for post in posts:
                content = post.get("content", "")
                for keyword in self.target_keywords:
                    if keyword.lower() in content.lower():
                        if keyword not in keyword_map:
                            keyword_map[keyword] = []
                        keyword_map[keyword].append(post)
            
            # Find opportunities for internal linking
            linking_opportunities = []
            for post in posts:
                content = BeautifulSoup(post.get("content", ""), "html.parser")
                
                # Get all links in the post
                existing_links = set()
                for link in content.find_all('a'):
                    if link.get('href'):
                        existing_links.add(link.get('href'))
                
                # Check for keywords without links
                for keyword in self.target_keywords:
                    if keyword.lower() in content.text.lower():
                        # Find relevant posts to link to
                        relevant_posts = keyword_map.get(keyword, [])
                        for rel_post in relevant_posts:
                            # Don't link to self
                            if rel_post["_id"] != post["_id"]:
                                link_url = f"/blog/{rel_post.get('slug', '')}"
                                if link_url not in existing_links:
                                    linking_opportunities.append({
                                        "source_id": post["_id"],
                                        "target_id": rel_post["_id"],
                                        "keyword": keyword,
                                        "source_title": post.get("title", ""),
                                        "target_title": rel_post.get("title", "")
                                    })
            
            # Store linking opportunities for later
            for opp in linking_opportunities:
                db.seo_opportunities.update_one(
                    {
                        "source_id": opp["source_id"],
                        "target_id": opp["target_id"],
                    },
                    {"$set": opp},
                    upsert=True
                )
            
            print(f"🔗 Found {len(linking_opportunities)} internal linking opportunities")
            
        except Exception as e:
            print(f"Link analysis error: {e}")
    
    def optimize_meta_tags(self):
        """Optimize meta tags for pages"""
        print("🏷️ Optimizing meta tags...")
        
        try:
            # Get all gear pages
            gear_items = list(db.gear.find())
            
            for item in gear_items:
                # Build SEO-friendly title
                name = item.get("name", "")
                if name:
                    seo_title = f"{name} - Best Price for Guerilla Camping | Top Rated Gear"
                    
                    # Build meta description
                    desc = item.get("description", "")
                    meta_desc = f"Get the {name} at the best price. Perfect for off-grid adventures. Used by real guerilla campers. Free shipping & limited-time discounts available."
                    
                    # Update item
                    db.gear.update_one(
                        {"_id": item["_id"]},
                        {"$set": {
                            "seo_title": seo_title,
                            "meta_description": meta_desc,
                            "seo_updated_at": datetime.now()
                        }}
                    )
            
            print(f"✅ Optimized meta tags for {len(gear_items)} products")
            
        except Exception as e:
            print(f"Meta tag optimization error: {e}")
    
    def check_competitor_backlinks(self):
        """Analyze competitor backlinks for opportunities"""
        print("🔍 Checking competitor backlinks...")
        
        try:
            competitors = [
                "theoutbound.com",
                "rei.com/blog",
                "outdoorsy.com/blog",
                "campsaver.com/blog"
            ]
            
            backlink_opportunities = []
            
            for competitor in competitors:
                # This would normally use an API like Ahrefs or SEMrush
                # For this example, we'll just log the competitor
                print(f"Would check backlinks for: {competitor}")
                
                # In a real implementation, you would:
                # 1. Get competitor backlinks via API
                # 2. Filter for relevant sites
                # 3. Store outreach opportunities
                
                # Simulate finding some opportunities
                for i in range(3):
                    backlink_opportunities.append({
                        "target_site": f"example{i}.com",
                        "competitor": competitor,
                        "relevance_score": random.randint(60, 100),
                        "discovered_at": datetime.now()
                    })
            
            # Store backlink opportunities
            if backlink_opportunities:
                db.backlink_opportunities.insert_many(backlink_opportunities)
                
            print(f"🔗 Found {len(backlink_opportunities)} backlink opportunities")
            
        except Exception as e:
            print(f"Backlink analysis error: {e}")
    
    def purge_cloudflare_cache(self):
        """Purge Cloudflare cache to ensure fresh content"""
        print("🔄 Purging Cloudflare cache...")
        
        if not all([CLOUDFLARE_API_KEY, CLOUDFLARE_EMAIL, CLOUDFLARE_ZONE_ID]):
            print("⚠️ Cloudflare credentials not set. Skipping cache purge.")
            return
        
        try:
            headers = {
                "X-Auth-Email": CLOUDFLARE_EMAIL,
                "X-Auth-Key": CLOUDFLARE_API_KEY,
                "Content-Type": "application/json"
            }
            
            # Purge everything
            response = requests.post(
                f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/purge_cache",
                headers=headers,
                json={"purge_everything": True}
            )
            
            if response.status_code == 200:
                print("✅ Successfully purged Cloudflare cache")
            else:
                print(f"❌ Failed to purge cache: {response.text}")
                
        except Exception as e:
            print(f"Cloudflare cache purge error: {e}")

if __name__ == "__main__":
    agent = SEOAgent()
    agent.run()
