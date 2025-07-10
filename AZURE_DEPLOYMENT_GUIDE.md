# ☁️ Azure Deployment Guide for Guerilla AI

## 🎓 **Student Credits Advantage**

You're making a smart choice with Azure! Here's why:

### ✅ **Student Benefits**
- **$100 Azure credits** per year
- **Free tier services** available
- **Reduced pricing** on premium services
- **No credit card required** for student account

### 💰 **Cost Analysis**
| Service | Regular Price | Student Price | Your Cost |
|---------|---------------|---------------|-----------|
| App Service (F1) | $13/month | $0/month | **FREE** |
| Redis Cache (Basic) | $13/month | $13/month | $13/month |
| Bandwidth | $0.087/GB | $0.087/GB | ~$5/month |
| **Total** | **$26+/month** | **$18/month** | **$18/month** |

## 🚀 **Quick Azure Setup (10 Minutes)**

### 1. **Install Azure CLI**
```bash
# Windows
winget install Microsoft.AzureCLI

# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 2. **Login to Azure**
```bash
az login
```

### 3. **Set Student Subscription**
```bash
# List subscriptions
az account list --output table

# Set your student subscription
az account set --subscription "Your-Student-Subscription-Name"
```

### 4. **Run Azure Deployment**
```bash
python azure_deployment.py
```

## 📋 **Manual Deployment Steps**

### **Step 1: Create Resource Group**
```bash
az group create --name gorillacamping-rg --location eastus
```

### **Step 2: Create App Service Plan (Free Tier)**
```bash
az appservice plan create \
  --name gorillacamping-plan \
  --resource-group gorillacamping-rg \
  --location eastus \
  --sku F1 \
  --is-linux
```

### **Step 3: Create Web App**
```bash
az webapp create \
  --name gorillacamping-ai \
  --resource-group gorillacamping-rg \
  --plan gorillacamping-plan \
  --runtime "PYTHON:3.11"
```

### **Step 4: Configure Environment Variables**
```bash
# Set your environment variables
az webapp config appsettings set \
  --name gorillacamping-ai \
  --resource-group gorillacamping-rg \
  --settings \
    GEMINI_API_KEY="your_gemini_api_key" \
    MONGODB_URI="your_mongodb_uri" \
    REDIS_URL="your_redis_url" \
    SECRET_KEY="your_secret_key"
```

### **Step 5: Create Redis Cache (Optional but Recommended)**
```bash
# Create Redis Cache for AI caching
az redis create \
  --name gorillacamping-redis \
  --resource-group gorillacamping-rg \
  --location eastus \
  --sku Basic \
  --vm-size C0
```

### **Step 6: Deploy Your Code**
```bash
# Deploy using Git
az webapp deployment source config-local-git \
  --name gorillacamping-ai \
  --resource-group gorillacamping-rg

# Get deployment URL
az webapp show \
  --name gorillacamping-ai \
  --resource-group gorillacamping-rg \
  --query defaultHostName \
  --output tsv
```

## 🔧 **Azure-Specific Optimizations**

### **1. Startup Configuration**
Your `startup.py` file is configured for Azure:
```python
#!/usr/bin/env python3
import os
from app_optimized import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### **2. Web.config for IIS**
The `azure-web.config` file handles IIS configuration:
```xml
<httpPlatform processPath="D:\Python311\python.exe" 
              arguments="D:\home\site\wwwroot\startup.py" 
              requestTimeout="00:04:00" 
              startupTimeLimit="60">
```

### **3. Environment Variables**
Set these in Azure App Service:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `MONGODB_URI`: Your MongoDB connection string
- `REDIS_URL`: Your Redis connection string (optional)
- `SECRET_KEY`: Flask secret key
- `WEBSITES_PORT`: 5000
- `PYTHON_VERSION`: 3.11

## 📊 **Cost Optimization Strategies**

### **1. Use Free Tier Services**
- **App Service Plan**: F1 (Free) tier
- **Web App**: Free tier included
- **Bandwidth**: First 5GB free per month

### **2. Optimize Redis Usage**
- **Basic tier**: $13/month (sufficient for caching)
- **Cache hit rate**: 70% reduces AI costs by 70%
- **Net savings**: $70-100/month on AI costs

### **3. Monitor Usage**
```bash
# Check resource usage
az monitor metrics list \
  --resource gorillacamping-ai \
  --metric CPUPercentage,MemoryPercentage

# Check costs
az consumption usage list \
  --billing-period-name "2024-01"
```

## 🎯 **Student Credit Management**

### **1. Check Credit Balance**
```bash
# Check remaining credits
az billing account show \
  --query "properties.spendingLimit"
```

### **2. Set Spending Limits**
```bash
# Set budget alerts
az monitor action-group create \
  --name "budget-alerts" \
  --resource-group gorillacamping-rg \
  --short-name "budget"
```

### **3. Optimize for Credits**
- Use free tier services when possible
- Monitor usage daily
- Set up budget alerts
- Use student discounts

## 🚨 **Troubleshooting**

### **Common Azure Issues**

**1. Deployment Fails**
```bash
# Check deployment logs
az webapp log tail --name gorillacamping-ai --resource-group gorillacamping-rg

# Restart app
az webapp restart --name gorillacamping-ai --resource-group gorillacamping-rg
```

**2. Environment Variables Not Set**
```bash
# List current settings
az webapp config appsettings list \
  --name gorillacamping-ai \
  --resource-group gorillacamping-rg

# Set missing variables
az webapp config appsettings set \
  --name gorillacamping-ai \
  --resource-group gorillacamping-rg \
  --settings VARIABLE_NAME="value"
```

**3. Redis Connection Issues**
```bash
# Check Redis status
az redis show \
  --name gorillacamping-redis \
  --resource-group gorillacamping-rg

# Get connection string
az redis list-keys \
  --name gorillacamping-redis \
  --resource-group gorillacamping-rg
```

## 📈 **Performance Monitoring**

### **1. Azure Monitor**
```bash
# Enable monitoring
az monitor diagnostic-settings create \
  --name "gorillacamping-monitoring" \
  --resource gorillacamping-ai \
  --resource-group gorillacamping-rg \
  --logs '[{"category": "AppServiceHTTPLogs", "enabled": true}]'
```

### **2. Application Insights**
```bash
# Create Application Insights
az monitor app-insights component create \
  --app "gorillacamping-insights" \
  --location eastus \
  --resource-group gorillacamping-rg \
  --application-type web
```

## 🎯 **Success Metrics**

### **Week 1 Goals**
- [ ] Azure deployment successful
- [ ] App accessible via URL
- [ ] AI system responding
- [ ] Costs under $20/month

### **Month 1 Goals**
- [ ] $500+ revenue generated
- [ ] <$30 total monthly costs
- [ ] 70% cache hit rate
- [ ] <2s response times

### **Month 3 Goals**
- [ ] $1000+ monthly revenue
- [ ] <$50 monthly costs
- [ ] 2000%+ ROI achieved
- [ ] System fully optimized

## 💡 **Pro Tips for Azure**

### **1. Cost Optimization**
- Use F1 (Free) App Service Plan
- Monitor usage daily
- Set budget alerts
- Use student credits strategically

### **2. Performance Optimization**
- Enable Redis caching
- Use CDN for static files
- Optimize Python dependencies
- Monitor response times

### **3. Security**
- Use managed identities
- Enable HTTPS only
- Set up monitoring alerts
- Regular security updates

## 🦍 **Guerilla Style Summary**

**You're getting:**
- **Free hosting** with student credits
- **70% AI cost reduction** with caching
- **Professional infrastructure** at student prices
- **Scalable platform** for growth

**Your advantage:**
- Student credits cover most costs
- Azure's enterprise features
- Professional monitoring tools
- Global CDN and scaling

**Next steps:**
1. Deploy to Azure using the script
2. Monitor costs and performance
3. Scale based on revenue
4. Profit from the optimization

**Remember:** Student credits are your secret weapon - use them wisely and scale smart! 🚀

---

*"Student credits + AI optimization = Maximum ROI" - Guerilla the Gorilla* 