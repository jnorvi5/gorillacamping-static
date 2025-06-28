import os
import pymongo
import requests
import re
from bs4 import BeautifulSoup

MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = "gorillacamping"
COLLECTION = "gear"

def get_amazon_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.content, "html.parser")
    # Try multiple price selectors
    price = None
    for selector in [
        "#priceblock_ourprice", "#priceblock_dealprice", ".a-price .a-offscreen", "#price_inside_buybox"
    ]:
        el = soup.select_one(selector)
        if el:
            price = el.text.strip()
            break
    if not price:
        # Try regex fallback
        m = re.search(r'\$\d{1,4}(\.\d{2})?', soup.text)
        if m:
            price = m.group(0)
    return price

def main():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    gear = db[COLLECTION]
    for item in gear.find({"active": True}):
        amzn_url = item.get("amazon_url") or item.get("affiliate_url")
        if not amzn_url or "amazon.com" not in amzn_url:
            continue
        price = get_amazon_price(amzn_url)
        if price:
            gear.update_one({"_id": item["_id"]}, {"$set": {"price": price}})
            print(f"{item['name']}: {price}")
        else:
            print(f"Could not fetch price for {item['name']}")
    print("✅ Amazon price update complete.")

if __name__ == "__main__":
    main()
