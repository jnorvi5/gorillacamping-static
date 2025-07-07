# Azure Integration Guide for Gorilla Camping

This guide explains how to connect your Gorilla Camping application to Azure services for enhanced scalability, reliability, and performance.

## 🎯 Overview

The application now supports Azure services as primary options with fallback to existing services:

- **Azure Cosmos DB** - Primary database (MongoDB fallback)
- **Azure Blob Storage** - File storage and static content
- **Azure Key Vault** - Secrets management 
- **Azure Application Insights** - Monitoring and analytics

## 🔧 Azure Services Setup

### 1. Azure Cosmos DB (Database)

1. Create an Azure Cosmos DB account in the Azure portal
2. Choose "Core (SQL)" API for best compatibility
3. Create a database named `gorillacamping` 
4. Note the endpoint and primary key

**Environment Variables:**
```bash
AZURE_COSMOS_ENDPOINT=https://your-account.documents.azure.com:443/
AZURE_COSMOS_KEY=your-primary-key
AZURE_COSMOS_DATABASE=gorillacamping
```

### 2. Azure Blob Storage (File Storage)

1. Create a Storage Account in the Azure portal
2. Create containers for your content (e.g., `uploads`, `images`)
3. Get the connection string

**Environment Variables:**
```bash
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
```

### 3. Azure Key Vault (Secrets Management)

1. Create a Key Vault in the Azure portal
2. Add secrets like `GEMINI-API-KEY`, `SECRET-KEY`, etc.
3. Configure access policies for your app

**Environment Variables:**
```bash
AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/
```

### 4. Azure Application Insights (Monitoring)

1. Create an Application Insights resource
2. Get the connection string

**Environment Variables:**
```bash
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
```

## 🚀 Deployment Methods

### Method 1: GitHub Actions (Current Setup)

Your app is already deployed to Azure App Service via GitHub Actions. To add Azure services:

1. Go to your Azure App Service in the portal
2. Navigate to "Configuration" → "Application settings"
3. Add the Azure environment variables listed above

### Method 2: Azure CLI

```bash
# Set environment variables in your App Service
az webapp config appsettings set --resource-group your-rg --name gorillacamping --settings \
  AZURE_COSMOS_ENDPOINT="https://your-account.documents.azure.com:443/" \
  AZURE_COSMOS_KEY="your-primary-key" \
  AZURE_COSMOS_DATABASE="gorillacamping"
```

### Method 3: Local Development

Create a `.env` file from the template:

```bash
cp azure.env.template .env
# Edit .env with your Azure service details
```

## 📊 Migration from MongoDB

If you have existing data in MongoDB, use the migration helper:

```bash
# Set both MongoDB and Azure Cosmos DB environment variables
export MONGODB_URI="your-mongodb-connection-string"
export AZURE_COSMOS_ENDPOINT="https://your-account.documents.azure.com:443/"
export AZURE_COSMOS_KEY="your-primary-key"

# Run migration
python azure_migrate.py
```

## 🔄 Fallback Behavior

The application intelligently falls back to existing services:

1. **Database**: Azure Cosmos DB → MongoDB → Demo mode
2. **Secrets**: Azure Key Vault → Environment variables
3. **File Storage**: Azure Blob Storage → Local file system
4. **Monitoring**: Azure Application Insights → Local logging

## 🛠️ Configuration Examples

### Complete Azure Configuration
```bash
# Azure Services
AZURE_COSMOS_ENDPOINT=https://gorillacamping.documents.azure.com:443/
AZURE_COSMOS_KEY=your-cosmos-key
AZURE_COSMOS_DATABASE=gorillacamping
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=gorillacamping;...
AZURE_KEY_VAULT_URL=https://gorillacamping-vault.vault.azure.net/
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...

# Optional: MongoDB fallback
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/gorillacamping
```

### Hybrid Configuration (Gradual Migration)
```bash
# Use Azure for some services, keep existing for others
AZURE_COSMOS_ENDPOINT=https://gorillacamping.documents.azure.com:443/
AZURE_COSMOS_KEY=your-cosmos-key

# Keep existing MongoDB as fallback
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/gorillacamping

# Traditional environment variables for secrets
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
```

## 📈 Benefits of Azure Integration

### Performance
- **Azure Cosmos DB**: Global distribution, automatic scaling
- **Azure Blob Storage**: CDN integration, high availability
- **Azure App Service**: Auto-scaling based on demand

### Security
- **Azure Key Vault**: Centralized secrets management
- **Azure Identity**: Managed service identity
- **Azure Security Center**: Threat detection

### Monitoring
- **Application Insights**: Real-time performance monitoring
- **Azure Monitor**: Infrastructure monitoring
- **Custom dashboards**: Business metrics tracking

### Cost Optimization
- **Pay-as-you-go**: Scale costs with usage
- **Reserved instances**: Discounts for predictable workloads
- **Azure free tier**: Many services have free quotas

## 🔍 Troubleshooting

### Connection Issues
1. Check environment variables are set correctly
2. Verify Azure service endpoints and keys
3. Check firewall rules and network security groups

### Migration Issues
1. Ensure both source and destination databases are accessible
2. Check document structure compatibility
3. Monitor for rate limiting in Cosmos DB

### Performance Issues
1. Review Cosmos DB request units (RU/s)
2. Check blob storage access patterns
3. Monitor Application Insights for bottlenecks

## 📞 Support

For Azure-specific issues:
- Azure Support: https://azure.microsoft.com/support/
- Azure Documentation: https://docs.microsoft.com/azure/

For application-specific issues:
- Check Application Insights logs
- Review app service diagnostic logs
- Monitor system health via Azure Monitor

## 🎉 Next Steps

1. **Set up Azure services** following the guide above
2. **Configure environment variables** in your deployment
3. **Test the application** to ensure everything works
4. **Migrate existing data** using the migration helper
5. **Monitor performance** using Azure Application Insights
6. **Optimize costs** by reviewing usage patterns

Your Gorilla Camping application is now ready for enterprise-scale Azure deployment! 🚀