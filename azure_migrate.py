#!/usr/bin/env python3
"""
Azure Migration Helper
Helps migrate data from MongoDB to Azure Cosmos DB
"""

import os
import sys
from pymongo import MongoClient
from azure_config import azure_cosmos
from datetime import datetime


def migrate_collection(mongo_collection_name, cosmos_container_name=None):
    """Migrate a MongoDB collection to Azure Cosmos DB container"""
    if cosmos_container_name is None:
        cosmos_container_name = mongo_collection_name
    
    # Connect to MongoDB
    mongodb_uri = os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URI')
    if not mongodb_uri:
        print("❌ No MongoDB URI found")
        return False
    
    # Check Azure Cosmos DB
    if not azure_cosmos.is_available():
        print("❌ Azure Cosmos DB not configured")
        return False
    
    try:
        # Connect to MongoDB
        mongo_client = MongoClient(mongodb_uri)
        mongo_db = mongo_client.get_default_database()
        mongo_collection = getattr(mongo_db, mongo_collection_name)
        
        # Get Cosmos DB container
        cosmos_container = azure_cosmos.get_container(cosmos_container_name)
        if not cosmos_container:
            print(f"❌ Failed to get/create Cosmos DB container: {cosmos_container_name}")
            return False
        
        # Count documents
        total_docs = mongo_collection.count_documents({})
        print(f"📊 Found {total_docs} documents in MongoDB collection '{mongo_collection_name}'")
        
        if total_docs == 0:
            print("✅ No documents to migrate")
            return True
        
        # Migrate documents
        migrated = 0
        errors = 0
        
        for doc in mongo_collection.find():
            try:
                # Convert MongoDB _id to Cosmos DB id
                if '_id' in doc:
                    doc['id'] = str(doc['_id'])
                    # Keep _id for compatibility
                
                # Insert into Cosmos DB
                cosmos_container.create_item(body=doc)
                migrated += 1
                
                if migrated % 100 == 0:
                    print(f"📝 Migrated {migrated}/{total_docs} documents...")
                    
            except Exception as e:
                errors += 1
                print(f"❌ Error migrating document: {e}")
                if errors > 10:  # Stop if too many errors
                    print("❌ Too many errors, stopping migration")
                    break
        
        print(f"✅ Migration completed: {migrated} migrated, {errors} errors")
        return errors == 0
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def main():
    """Main migration function"""
    print("🚀 Azure Migration Helper for Gorilla Camping")
    print("=" * 50)
    
    # Check configuration
    mongodb_uri = os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URI')
    if not mongodb_uri:
        print("❌ MongoDB URI not found. Set MONGODB_URI or MONGO_URI environment variable.")
        sys.exit(1)
    
    if not azure_cosmos.is_available():
        print("❌ Azure Cosmos DB not configured. Check your Azure environment variables.")
        print("   Required: AZURE_COSMOS_ENDPOINT, AZURE_COSMOS_KEY")
        sys.exit(1)
    
    print("✅ Both MongoDB and Azure Cosmos DB are configured")
    print()
    
    # Collections to migrate
    collections = [
        'posts',
        'gear', 
        'contacts',
        'subscribers',
        'affiliate_clicks',
        'social_clicks',
        'ai_logs',
        'downloads'
    ]
    
    print("📋 Collections to migrate:")
    for i, collection in enumerate(collections, 1):
        print(f"  {i}. {collection}")
    print()
    
    # Ask for confirmation
    response = input("Do you want to proceed with migration? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Migration cancelled")
        sys.exit(0)
    
    # Migrate each collection
    print("\n🔄 Starting migration...")
    success_count = 0
    
    for collection in collections:
        print(f"\n📦 Migrating collection: {collection}")
        if migrate_collection(collection):
            success_count += 1
            print(f"✅ {collection} migrated successfully")
        else:
            print(f"❌ {collection} migration failed")
    
    print(f"\n🎉 Migration Summary:")
    print(f"   ✅ {success_count}/{len(collections)} collections migrated successfully")
    
    if success_count == len(collections):
        print("\n🎊 All collections migrated successfully!")
        print("   You can now switch to Azure Cosmos DB by updating your app configuration.")
    else:
        print("\n⚠️  Some collections failed to migrate. Check the errors above.")


if __name__ == "__main__":
    main()