# 🦍 HEROKU DEPLOYMENT - GET GORILLACAMPING MAKING MONEY

## Why Heroku?
- ✅ **Student Developer Pack** gives you $13/month credit
- ✅ **Better AI support** than Azure
- ✅ **Simple deployment** - just git push
- ✅ **Reliable uptime** for affiliate revenue

## Step 1: Install Heroku CLI
```bash
# Download from: https://devcenter.heroku.com/articles/heroku-cli
# Or if you have winget:
winget install Heroku.CLI
```

## Step 2: Login & Create App
```bash
heroku login
heroku create gorillacamping-live
```

## Step 3: Set Environment Variables (for AI later)
```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key-here
# We'll add GEMINI_API_KEY later when we re-enable AI
```

## Step 4: Deploy
```bash
git push heroku main
```

## Step 5: Check Logs
```bash
heroku logs --tail
```

## Student Pack Benefits
- **$13/month Heroku credits** (covers Basic dyno)
- **GitHub integration** (auto-deploy on push)
- **Add-ons included** (Redis for caching later)

## Cost Breakdown
- **Hobby Dyno:** $7/month (covered by student pack)
- **Domain:** You already have gorillacamping.site
- **AI costs:** We'll optimize to $10-15/month max

## Revenue Potential
- **Target:** $1000/month in 3 months
- **High-commission affiliates:** 25% vs Amazon's 3%
- **ROI:** 2000%+ with optimized AI chat 