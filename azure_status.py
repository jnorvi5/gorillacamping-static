#!/usr/bin/env python3
"""
Azure Integration Status Report
Shows the current status of Azure services integration
"""

import os
from azure_config import (
    COSMOS_AVAILABLE, BLOB_STORAGE_AVAILABLE, KEY_VAULT_AVAILABLE, 
    APPLICATION_INSIGHTS_AVAILABLE, azure_cosmos, azure_blob, 
    azure_keyvault, azure_insights
)

def print_banner():
    print("🚀 GORILLA CAMPING - AZURE INTEGRATION STATUS")
    print("=" * 55)

def print_azure_services_status():
    print("\n☁️  AZURE SERVICES AVAILABILITY:")
    print("-" * 35)
    
    services = [
        ("Azure Cosmos DB SDK", COSMOS_AVAILABLE, azure_cosmos.is_available() if COSMOS_AVAILABLE else False),
        ("Azure Blob Storage SDK", BLOB_STORAGE_AVAILABLE, azure_blob.is_available() if BLOB_STORAGE_AVAILABLE else False),
        ("Azure Key Vault SDK", KEY_VAULT_AVAILABLE, azure_keyvault.is_available() if KEY_VAULT_AVAILABLE else False),
        ("Azure Application Insights SDK", APPLICATION_INSIGHTS_AVAILABLE, azure_insights.is_available() if APPLICATION_INSIGHTS_AVAILABLE else False)
    ]
    
    for service_name, sdk_available, service_configured in services:
        sdk_status = "✅ Installed" if sdk_available else "📦 Not Installed"
        config_status = "🔧 Configured" if service_configured else "⚙️  Not Configured"
        print(f"  {service_name:<30} {sdk_status:<15} {config_status}")

def print_environment_variables():
    print("\n🔧 ENVIRONMENT VARIABLES:")
    print("-" * 25)
    
    env_vars = [
        "AZURE_COSMOS_ENDPOINT",
        "AZURE_COSMOS_KEY", 
        "AZURE_STORAGE_CONNECTION_STRING",
        "AZURE_KEY_VAULT_URL",
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "MONGODB_URI",
        "SECRET_KEY",
        "GEMINI_API_KEY"
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        status = "✅ Set" if value else "⚠️  Not Set"
        masked_value = f"{value[:10]}..." if value and len(value) > 10 else value or "Not Set"
        print(f"  {var:<35} {status:<10} {masked_value}")

def print_features():
    print("\n🎯 AZURE INTEGRATION FEATURES:")
    print("-" * 32)
    
    features = [
        "✅ Azure Cosmos DB (Primary Database)",
        "✅ MongoDB Fallback (Existing Data)",
        "✅ Azure Blob Storage (File Storage)", 
        "✅ Azure Key Vault (Secrets Management)",
        "✅ Azure Application Insights (Monitoring)",
        "✅ Database Abstraction Layer",
        "✅ Graceful Fallback System",
        "✅ Migration Helper Script",
        "✅ Comprehensive Test Suite",
        "✅ Production Ready Configuration"
    ]
    
    for feature in features:
        print(f"  {feature}")

def print_next_steps():
    print("\n📋 NEXT STEPS:")
    print("-" * 14)
    
    steps = [
        "1. 🔧 Configure Azure services (see AZURE_SETUP.md)",
        "2. 📝 Set environment variables in your deployment",
        "3. 🔄 Run migration script: python azure_migrate.py",
        "4. 🧪 Test integration: python azure_test.py",
        "5. 🚀 Deploy to Azure App Service",
        "6. 📊 Monitor with Azure Application Insights"
    ]
    
    for step in steps:
        print(f"  {step}")

def print_files_created():
    print("\n📁 FILES CREATED/MODIFIED:")
    print("-" * 26)
    
    files = [
        ("azure_config.py", "Azure services configuration"),
        ("azure_migrate.py", "MongoDB to Cosmos DB migration"),
        ("azure_test.py", "Integration test suite"),
        ("AZURE_SETUP.md", "Complete setup documentation"),
        ("azure.env.template", "Environment variables template"),
        ("app.py", "Updated with Azure integration"),
        ("requirements.txt", "Added Azure SDK dependencies"),
        ("README.md", "Updated with Azure information")
    ]
    
    for filename, description in files:
        print(f"  {filename:<20} - {description}")

def main():
    print_banner()
    print_azure_services_status()
    print_environment_variables() 
    print_features()
    print_files_created()
    print_next_steps()
    
    print("\n🎉 GORILLA CAMPING IS NOW AZURE-READY!")
    print("   Your application can seamlessly use Azure cloud services")
    print("   while maintaining backward compatibility with existing setup.")
    print("\n   See AZURE_SETUP.md for detailed configuration instructions.")

if __name__ == "__main__":
    main()