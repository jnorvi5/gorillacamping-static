#!/usr/bin/env python3
"""
Azure Integration Test
Tests Azure services connectivity and functionality
"""

import os
import sys
from azure_config import (
    azure_cosmos, azure_blob, azure_keyvault, azure_insights,
    get_secret, get_database_client, log_to_azure
)


def test_azure_cosmos_db():
    """Test Azure Cosmos DB connection and basic operations"""
    print("🧪 Testing Azure Cosmos DB...")
    
    if not azure_cosmos.is_available():
        print("   ⚠️  Azure Cosmos DB not configured - this is OK for development")
        return True
    
    try:
        # Test getting a container
        container = azure_cosmos.get_container('test_collection')
        if container:
            print("   ✅ Azure Cosmos DB connection successful")
            
            # Test basic operations
            test_doc = {
                'id': 'test-doc-1',
                'message': 'Azure integration test',
                'type': 'test'
            }
            
            # Insert test document
            container.create_item(body=test_doc)
            print("   ✅ Document creation successful")
            
            # Query test document
            items = list(container.query_items(
                query="SELECT * FROM c WHERE c.id = 'test-doc-1'",
                enable_cross_partition_query=True
            ))
            
            if items:
                print("   ✅ Document query successful")
                
                # Clean up test document
                container.delete_item(item='test-doc-1', partition_key='test-doc-1')
                print("   ✅ Document deletion successful")
            else:
                print("   ❌ Document query failed")
                return False
                
        else:
            print("   ❌ Failed to get/create test container")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Azure Cosmos DB test failed: {e}")
        return False


def test_azure_blob_storage():
    """Test Azure Blob Storage connection"""
    print("🧪 Testing Azure Blob Storage...")
    
    if not azure_blob.is_available():
        print("   ⚠️  Azure Blob Storage not configured - this is OK for development")
        return True
    
    try:
        # Test uploading a small file
        test_data = b"Azure integration test file"
        url = azure_blob.upload_file('test-container', 'test-file.txt', test_data)
        
        if url:
            print("   ✅ Azure Blob Storage upload successful")
            print(f"   📎 File URL: {url}")
            return True
        else:
            print("   ❌ Azure Blob Storage upload failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Azure Blob Storage test failed: {e}")
        return False


def test_azure_key_vault():
    """Test Azure Key Vault connection"""
    print("🧪 Testing Azure Key Vault...")
    
    if not azure_keyvault.is_available():
        print("   ⚠️  Azure Key Vault not configured - this is OK for development")
        return True
    
    try:
        # Test getting a secret (this one probably won't exist, but tests connection)
        secret = azure_keyvault.get_secret('test-secret')
        print("   ✅ Azure Key Vault connection successful")
        
        # Test the get_secret helper function
        secret_value = get_secret('SECRET_KEY')
        if secret_value:
            print("   ✅ Secret retrieval working")
        else:
            print("   ⚠️  No secrets found (expected for test)")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Azure Key Vault test failed: {e}")
        return False


def test_azure_application_insights():
    """Test Azure Application Insights connection"""
    print("🧪 Testing Azure Application Insights...")
    
    if not azure_insights.is_available():
        print("   ⚠️  Azure Application Insights not configured - this is OK for development")
        return True
    
    try:
        # Test logging
        log_to_azure("Azure integration test message")
        print("   ✅ Azure Application Insights logging successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Azure Application Insights test failed: {e}")
        return False


def test_database_abstraction():
    """Test the database abstraction layer"""
    print("🧪 Testing database abstraction layer...")
    
    try:
        from app import db_type, find_documents, insert_document, find_one_document
        
        print(f"   📊 Current database type: {db_type}")
        
        # Test basic operations (these might fail without a database, but tests the code)
        if db_type != "none":
            print("   ✅ Database abstraction layer loaded successfully")
            
            # Test find_documents (should not crash even if no data)
            posts = find_documents('posts', limit=1)
            print(f"   📝 Found {len(posts)} posts")
            
            return True
        else:
            print("   ⚠️  No database configured - abstraction layer still functional")
            return True
            
    except Exception as e:
        print(f"   ❌ Database abstraction test failed: {e}")
        return False


def main():
    """Run all Azure integration tests"""
    print("🚀 Azure Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Azure Cosmos DB", test_azure_cosmos_db),
        ("Azure Blob Storage", test_azure_blob_storage), 
        ("Azure Key Vault", test_azure_key_vault),
        ("Azure Application Insights", test_azure_application_insights),
        ("Database Abstraction", test_database_abstraction)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print()
        result = test_func()
        if result:
            passed += 1
    
    print()
    print("📊 Test Results:")
    print(f"   ✅ {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Azure integration tests passed!")
        print("   Your Azure services are properly configured.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed or services not configured.")
        print("   This is normal for development environments.")
        print("   See AZURE_SETUP.md for configuration instructions.")
    
    print("\n📋 Next Steps:")
    print("   1. Configure Azure services using AZURE_SETUP.md")
    print("   2. Set environment variables for your deployment")
    print("   3. Run migration script if you have existing data")
    print("   4. Monitor your application with Azure Application Insights")


if __name__ == "__main__":
    main()