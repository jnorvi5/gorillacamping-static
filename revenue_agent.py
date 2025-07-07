# NEW FILE: revenue_agent.py
import os
import requests
import random
import time
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient

# MongoDB connection
MONGO_URI = os.environ.get("MONGODB_URI", "your_connection_string")
client = MongoClient(MONGO_URI)
db = client.get_database()

# MailerLite API (free tier)
MAILERLITE_API_KEY = os.environ.get("MAILERLITE_API_KEY", "your_api_key")
MAILERLITE_GROUP_ID = os.environ.get("MAILERLITE_GROUP_ID", "your_group_id")

class RevenueAgent:
    def __init__(self):
        self.last_run = datetime.now() - timedelta(days=1)
    
    def run(self):
        print("🤖 Revenue Agent starting...")
        
        while True:
            try:
                current_time = datetime.now()
                
                # Run these tasks once per day
                if (current_time - self.last_run).total_seconds() > 86400:
                    self.analyze_affiliate_clicks()
                    self.optimize_gear_rankings()
                    self.re_engage_subscribers()
                    self.last_run = current_time
                
                # Run these tasks every hour
                self.generate_dynamic_urgency()
                
                # Sleep for an hour
                time.sleep(3600)
                
            except Exception as e:
                print(f"🚨 Agent error: {e}")
                time.sleep(300)  # Sleep for 5 minutes on error
    
    def analyze_affiliate_clicks(self):
        """Analyze click patterns and optimize product display order"""
        print("📊 Analyzing affiliate clicks...")
        
        try:
            # Get clicks from last 7 days
            seven_days_ago = datetime.now() - timedelta(days=7)
            clicks = list(db.affiliate_clicks.find({
                "timestamp": {"$gte": seven_days_ago}
            }))
            
            if not clicks:
                print("No recent clicks found.")
                return
            
            # Group by product and count
            product_counts = {}
            for click in clicks:
                product_id = click.get("product_id")
                if product_id:
                    product_counts[product_id] = product_counts.get(product_id, 0) + 1
            
            # Sort by popularity
            sorted_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Update product rankings
            for i, (product_id, count) in enumerate(sorted_products):
                db.gear.update_one(
                    {"affiliate_id": product_id},
                    {"$set": {"popularity_rank": i+1, "recent_clicks": count}}
                )
            
            print(f"✅ Updated rankings for {len(sorted_products)} products")
            
            # Create visualization
            self.create_click_chart(product_counts)
            
        except Exception as e:
            print(f"Error in click analysis: {e}")
    
    def create_click_chart(self, product_counts):
        """Generate chart of product clicks"""
        try:
            # Create simple bar chart
            if not product_counts:
                return
                
            products = list(product_counts.keys())
            clicks = list(product_counts.values())
            
            plt.figure(figsize=(10, 6))
            plt.bar(products, clicks, color='#00ff88')
            plt.title('Product Clicks (Last 7 Days)')
            plt.xlabel('Product')
            plt.ylabel('Clicks')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save chart
            chart_path = 'static/images/charts/product_clicks.png'
            os.makedirs(os.path.dirname(chart_path), exist_ok=True)
            plt.savefig(chart_path)
            plt.close()
            
            print(f"📈 Generated click chart at {chart_path}")
        except Exception as e:
            print(f"Chart creation error: {e}")
    
    def optimize_gear_rankings(self):
        """Re-order products based on conversion rate"""
        print("🔄 Optimizing gear rankings...")
        
        try:
            # Get all products
            products = list(db.gear.find())
            
            for product in products:
                # Calculate conversion score (mix of clicks, views, popularity)
                clicks = db.affiliate_clicks.count_documents({
                    "product_id": product.get("affiliate_id", ""),
                    "timestamp": {"$gte": datetime.now() - timedelta(days=14)}
                })
                
                views = db.product_views.count_documents({
                    "product_id": product.get("affiliate_id", ""),
                    "timestamp": {"$gte": datetime.now() - timedelta(days=14)}
                })
                
                # Calculate conversion rate (avoid division by zero)
                conversion_rate = clicks / max(views, 1)
                
                # Calculate overall score (conversion rate + popularity boost)
                score = (conversion_rate * 0.7) + (clicks * 0.3)
                
                # Update product score
                db.gear.update_one(
                    {"_id": product["_id"]},
                    {"$set": {
                        "conversion_rate": round(conversion_rate * 100, 2),
                        "conversion_score": score,
                        "updated_at": datetime.now()
                    }}
                )
            
            print(f"✅ Updated scores for {len(products)} products")
            
        except Exception as e:
            print(f"Optimization error: {e}")
    
    def re_engage_subscribers(self):
        """Send re-engagement emails to subscribers who haven't clicked recently"""
        print("✉️ Running subscriber re-engagement...")
        
        try:
            # Find subscribers who haven't engaged in 7+ days
            seven_days_ago = datetime.now() - timedelta(days=7)
            recent_clickers = set()
            
            # Get emails of recent clickers
            recent_clicks = db.affiliate_clicks.find({
                "timestamp": {"$gte": seven_days_ago}
            })
            
            for click in recent_clicks:
                if "user_id" in click:
                    recent_clickers.add(click["user_id"])
            
            # Find subscribers who haven't clicked
            inactive_subscribers = db.subscribers.find({
                "user_id": {"$nin": list(recent_clickers)},
                "created_at": {"$lt": seven_days_ago}
            })
            
            # Export list for MailerLite campaign
            inactive_emails = [sub["email"] for sub in inactive_subscribers]
            
            if not inactive_emails:
                print("No inactive subscribers found.")
                return
            
            # Create re-engagement campaign in MailerLite
            self.create_mailerlite_campaign(inactive_emails)
            
        except Exception as e:
            print(f"Re-engagement error: {e}")
    
    def create_mailerlite_campaign(self, emails):
        """Create a campaign in MailerLite"""
        if not MAILERLITE_API_KEY or not emails:
            return
        
        try:
            # Add subscribers to a specific group
            headers = {
                "X-MailerLite-ApiKey": MAILERLITE_API_KEY,
                "Content-Type": "application/json"
            }
            
            # Create segment for re-engagement
            segment_name = f"Re-engagement {datetime.now().strftime('%m-%d')}"
            segment_data = {
                "name": segment_name,
                "emails": emails
            }
            
            response = requests.post(
                "https://api.mailerlite.com/api/v2/segments",
                headers=headers,
                json=segment_data
            )
            
            print(f"📧 Created re-engagement segment with {len(emails)} subscribers")
            
        except Exception as e:
            print(f"MailerLite error: {e}")
    
    def generate_dynamic_urgency(self):
        """Dynamically adjust product urgency based on time of day and visitor patterns"""
        print("⏰ Generating dynamic urgency...")
        
        try:
            # Get all products
            products = list(db.gear.find())
            
            # Time-based urgency factors
            current_hour = datetime.now().hour
            
            # Prime conversion hours (7-10pm local time)
            is_prime_time = 19 <= current_hour <= 22
            
            for product in products:
                # Dynamically adjust inventory and urgency
                base_inventory = random.randint(3, 12)
                
                # More urgent during prime hours
                if is_prime_time:
                    inventory = max(1, base_inventory - random.randint(2, 5))
                    countdown = random.randint(1, 12)  # 1-12 hours
                else:
                    inventory = base_inventory
                    countdown = random.randint(12, 36)  # 12-36 hours
                
                # Higher urgency for popular products
                popularity = product.get("popularity_rank", 999)
                if popularity <= 3:
                    inventory = max(1, inventory - random.randint(1, 3))
                    countdown = max(1, countdown - random.randint(1, 6))
                
                # Update product urgency
                db.gear.update_one(
                    {"_id": product["_id"]},
                    {"$set": {
                        "inventory": inventory,
                        "countdown_hours": countdown,
                        "urgency_updated_at": datetime.now()
                    }}
                )
            
            print(f"⏱️ Updated urgency for {len(products)} products")
            
        except Exception as e:
            print(f"Urgency generation error: {e}")

if __name__ == "__main__":
    agent = RevenueAgent()
    agent.run()
