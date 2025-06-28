import os
import csv
import pymongo
import requests
from datetime import datetime

GOOGLE_SHEET_CSV_URL = os.environ.get("GSHEET_CSV_URL")  # e.g. https://docs.google.com/spreadsheets/d/xxx/export?format=csv
LOCAL_CSV = "gear.csv"
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = "gorillacamping"
COLLECTION = "gear"

def fetch_csv(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text.splitlines()

def parse_bool(val):
    return str(val).strip().lower() in ["1", "true", "yes"]

def parse_list(val):
    return [x.strip() for x in val.split("|")] if val else []

def get_csv_rows():
    # Try Google Sheets CSV first, fallback to local CSV
    try:
        lines = fetch_csv(GOOGLE_SHEET_CSV_URL)
        print("✅ Pulled gear from Google Sheets.")
    except Exception as ex:
        print("⚠️ Google Sheets failed, using local gear.csv. Error:", ex)
        with open(LOCAL_CSV, encoding="utf-8") as f:
            lines = f.readlines()
    return csv.DictReader(lines)

def main():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    gear = db[COLLECTION]
    updated = 0
    for row in get_csv_rows():
        doc = {
            "name": row["name"].strip(),
            "affiliate_id": row["affiliate_id"].strip(),
            "price": row["price"].strip(),
            "image": row["image"].strip(),
            "description": row["description"].strip(),
            "badges": parse_list(row.get("badges", "")),
            "specs": parse_list(row.get("specs", "")),
            "old_price": row.get("old_price", "").strip(),
            "savings": row.get("savings", "").strip(),
            "rating": int(row.get("rating", "0")),
            "why_recommend": row.get("why_recommend", "").strip(),
            "order": int(row.get("order", "0")),
            "active": parse_bool(row.get("active", "TRUE")),
            "updated_at": datetime.utcnow(),
        }
        gear.update_one({"affiliate_id": doc["affiliate_id"]}, {"$set": doc}, upsert=True)
        updated += 1
    print(f"✅ Imported/updated {updated} gear items to MongoDB Atlas.")

if __name__ == "__main__":
    main()
