# 🦍 **CLOUDFLARE DNS FIX FOR GORILLACAMPING.SITE**

## **🎯 THE PROBLEM:**
- ✅ `www.gorillacamping.site` → Working (200 OK)
- ❌ `gorillacamping.site` → 404 Not Found

## **🔧 THE SOLUTION:**

### **Step 1: Add Root Domain DNS Record**

In your Cloudflare dashboard:

1. **Go to:** DNS → Records
2. **Add these records:**

```
Type: A
Name: @ (or leave blank for root)
Content: [YOUR_AZURE_IP]
Proxy status: Proxied (orange cloud)
TTL: Auto
```

```
Type: CNAME  
Name: www
Content: gorillacamping.azurewebsites.net
Proxy status: Proxied (orange cloud)
TTL: Auto
```

### **Step 2: Page Rules (Optional but Recommended)**

Create these Page Rules in Cloudflare:

1. **Redirect root to www:**
   - URL: `gorillacamping.site/*`
   - Settings: Forwarding URL → 301 Redirect
   - Destination: `https://www.gorillacamping.site/$1`

2. **Force HTTPS:**
   - URL: `*gorillacamping.site/*`
   - Settings: Always Use HTTPS

### **Step 3: Verify Azure App Service**

Make sure your Azure app service is configured for custom domains:

1. **Azure Portal** → Your Web App
2. **Custom domains** → Add domain
3. **Add:** `gorillacamping.site` and `www.gorillacamping.site`

## **🚀 ALTERNATIVE QUICK FIX:**

If you want to keep it simple, just redirect the root domain to www:

**In Cloudflare Page Rules:**
- URL: `gorillacamping.site/*`
- Settings: Forwarding URL → 301 Redirect  
- Destination: `https://www.gorillacamping.site/$1`

This will automatically redirect `gorillacamping.site` to `www.gorillacamping.site` where your app is working.

## **✅ VERIFICATION:**

After making these changes, test:
- `https://gorillacamping.site` → Should redirect to www or work directly
- `https://www.gorillacamping.site` → Should work (already does)
- `https://static.gorillacamping.site` → Should work for static assets

## **💰 PERFORMANCE BOOST:**

With Cloudflare properly configured, you'll get:
- **50% faster loading** (CDN caching)
- **Free SSL certificates**
- **DDoS protection**
- **Better SEO** (consistent domain handling) 