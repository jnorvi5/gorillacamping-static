#!/usr/bin/env python3
"""
🦍 Guerilla AI Deployment Optimizer

This script helps deploy your AI-optimized app across different platforms
with cost-effective configurations for maximum ROI.
"""

import os
import json
import subprocess
import sys
from datetime import datetime

class DeploymentOptimizer:
    """
    Optimizes deployment across different platforms:
    - Heroku (current)
    - Railway (cheaper alternative)
    - Render (free tier available)
    - Azure (student credits)
    """
    
    def __init__(self):
        self.platforms = {
            'heroku': {
                'name': 'Heroku',
                'cost': '$7-25/month',
                'pros': ['Easy deployment', 'Good for small apps'],
                'cons': ['Expensive', 'Limited resources'],
                'setup': self.setup_heroku
            },
            'railway': {
                'name': 'Railway',
                'cost': '$5-20/month',
                'pros': ['Cheaper than Heroku', 'Good performance'],
                'cons': ['Less mature', 'Fewer integrations'],
                'setup': self.setup_railway
            },
            'render': {
                'name': 'Render',
                'cost': '$0-25/month',
                'pros': ['Free tier available', 'Good performance'],
                'cons': ['Sleeps on free tier', 'Limited bandwidth'],
                'setup': self.setup_render
            },
            'azure': {
                'name': 'Azure',
                'cost': '$0-50/month (student credits)',
                'pros': ['Student credits', 'Enterprise features'],
                'cons': ['Complex setup', 'Can be expensive'],
                'setup': self.setup_azure
            }
        }
    
    def analyze_current_setup(self):
        """Analyze current deployment and suggest optimizations"""
        print("🔍 Analyzing current setup...")
        
        # Check current platform
        if os.path.exists('Procfile'):
            print("✅ Heroku detected (current)")
            current_platform = 'heroku'
        elif os.path.exists('railway.json'):
            print("✅ Railway detected")
            current_platform = 'railway'
        elif os.path.exists('render.yaml'):
            print("✅ Render detected")
            current_platform = 'render'
        else:
            print("❓ Platform not detected")
            current_platform = None
        
        # Check AI dependencies
        ai_dependencies = [
            'google-generativeai',
            'redis',
            'chromadb',
            'sentence-transformers'
        ]
        
        missing_deps = []
        for dep in ai_dependencies:
            try:
                __import__(dep.replace('-', '_'))
                print(f"✅ {dep} installed")
            except ImportError:
                print(f"❌ {dep} missing")
                missing_deps.append(dep)
        
        # Check environment variables
        required_env_vars = [
            'GEMINI_API_KEY',
            'MONGODB_URI',
            'REDIS_URL'
        ]
        
        missing_env = []
        for var in required_env_vars:
            if not os.environ.get(var):
                print(f"❌ {var} not set")
                missing_env.append(var)
            else:
                print(f"✅ {var} configured")
        
        return {
            'current_platform': current_platform,
            'missing_dependencies': missing_deps,
            'missing_env_vars': missing_env
        }
    
    def suggest_optimizations(self, analysis):
        """Suggest optimizations based on analysis"""
        print("\n🎯 OPTIMIZATION SUGGESTIONS:")
        
        # Platform optimization
        if analysis['current_platform'] == 'heroku':
            print("💰 Consider migrating to Railway or Render for cost savings:")
            print("   - Railway: $5-20/month vs Heroku $7-25/month")
            print("   - Render: Free tier available")
        
        # Dependencies
        if analysis['missing_dependencies']:
            print(f"📦 Install missing dependencies: {', '.join(analysis['missing_dependencies'])}")
            print("   Run: pip install -r requirements.txt")
        
        # Environment variables
        if analysis['missing_env_vars']:
            print(f"🔧 Configure missing environment variables: {', '.join(analysis['missing_env_vars'])}")
        
        # AI optimization suggestions
        print("\n🤖 AI OPTIMIZATION RECOMMENDATIONS:")
        print("1. Enable Redis caching (70% cost reduction)")
        print("2. Implement conversation memory")
        print("3. Use smart product recommendations")
        print("4. Add response time tracking")
        print("5. Implement fallback systems")
    
    def setup_heroku(self):
        """Setup Heroku deployment"""
        print("🚀 Setting up Heroku deployment...")
        
        # Create Procfile if not exists
        if not os.path.exists('Procfile'):
            with open('Procfile', 'w') as f:
                f.write('web: gunicorn app_optimized:app')
            print("✅ Created Procfile")
        
        # Create runtime.txt
        if not os.path.exists('runtime.txt'):
            with open('runtime.txt', 'w') as f:
                f.write('python-3.11.7')
            print("✅ Created runtime.txt")
        
        print("📋 Heroku setup complete!")
        print("   Run: heroku create gorillacamping-ai")
        print("   Run: git push heroku main")
    
    def setup_railway(self):
        """Setup Railway deployment"""
        print("🚂 Setting up Railway deployment...")
        
        # Create railway.json
        railway_config = {
            "build": {
                "builder": "nixpacks"
            },
            "deploy": {
                "startCommand": "gunicorn app_optimized:app",
                "healthcheckPath": "/",
                "healthcheckTimeout": 300,
                "restartPolicyType": "ON_FAILURE",
                "restartPolicyMaxRetries": 10
            }
        }
        
        with open('railway.json', 'w') as f:
            json.dump(railway_config, f, indent=2)
        
        print("✅ Created railway.json")
        print("📋 Railway setup complete!")
        print("   Run: railway login")
        print("   Run: railway init")
        print("   Run: railway up")
    
    def setup_render(self):
        """Setup Render deployment"""
        print("🎨 Setting up Render deployment...")
        
        # Create render.yaml
        render_config = {
            "services": [
                {
                    "type": "web",
                    "name": "gorillacamping-ai",
                    "env": "python",
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": "gunicorn app_optimized:app",
                    "healthCheckPath": "/",
                    "autoDeploy": True
                }
            ]
        }
        
        with open('render.yaml', 'w') as f:
            json.dump(render_config, f, indent=2)
        
        print("✅ Created render.yaml")
        print("📋 Render setup complete!")
        print("   Deploy via Render dashboard")
    
    def setup_azure(self):
        """Setup Azure deployment"""
        print("☁️ Setting up Azure deployment...")
        
        # Create azure.yaml
        azure_config = {
            "language": "python",
            "buildCommands": [
                "pip install -r requirements.txt"
            ],
            "startCommand": "gunicorn app_optimized:app"
        }
        
        with open('azure.yaml', 'w') as f:
            json.dump(azure_config, f, indent=2)
        
        print("✅ Created azure.yaml")
        print("📋 Azure setup complete!")
        print("   Use Azure App Service for deployment")
    
    def create_cost_analysis(self):
        """Create cost analysis for different platforms"""
        print("\n💰 COST ANALYSIS:")
        
        monthly_costs = {
            'Heroku': {
                'Basic': 7,
                'Standard': 25,
                'Performance': 250
            },
            'Railway': {
                'Starter': 5,
                'Pro': 20,
                'Team': 50
            },
            'Render': {
                'Free': 0,
                'Starter': 7,
                'Standard': 25
            },
            'Azure': {
                'Student Credits': 0,
                'Basic': 13,
                'Standard': 73
            }
        }
        
        for platform, plans in monthly_costs.items():
            print(f"\n{platform}:")
            for plan, cost in plans.items():
                print(f"  {plan}: ${cost}/month")
        
        print("\n💡 RECOMMENDATION:")
        print("   Start with Render (Free) or Railway ($5) for cost optimization")
        print("   Use Azure if you have student credits available")
    
    def optimize_for_revenue(self):
        """Optimize deployment for maximum revenue generation"""
        print("\n💸 REVENUE OPTIMIZATION STRATEGY:")
        
        optimizations = [
            "1. Use cheapest platform (Render Free → Railway $5)",
            "2. Enable AI caching (70% cost reduction)",
            "3. Implement smart product recommendations",
            "4. Add conversation memory for better conversions",
            "5. Track AI performance and costs",
            "6. Use high-commission products (25% vs 3%)",
            "7. Implement A/B testing for AI responses"
        ]
        
        for opt in optimizations:
            print(f"   {opt}")
        
        print(f"\n🎯 TARGET: $1000/month revenue with <$50/month costs")
        print("   ROI: 2000% return on hosting investment")
    
    def run_optimization(self):
        """Run full optimization process"""
        print("🦍 GUERILLA AI OPTIMIZATION SYSTEM")
        print("=" * 50)
        
        # Analyze current setup
        analysis = self.analyze_current_setup()
        
        # Suggest optimizations
        self.suggest_optimizations(analysis)
        
        # Show cost analysis
        self.create_cost_analysis()
        
        # Revenue optimization
        self.optimize_for_revenue()
        
        # Ask for deployment choice
        print("\n🚀 DEPLOYMENT OPTIONS:")
        for key, platform in self.platforms.items():
            print(f"   {key}: {platform['name']} ({platform['cost']})")
        
        choice = input("\nChoose platform to setup (or 'skip'): ").lower()
        
        if choice in self.platforms:
            self.platforms[choice]['setup']()
        elif choice != 'skip':
            print("Invalid choice. Skipping deployment setup.")
        
        print("\n✅ Optimization complete!")
        print("   Next steps:")
        print("   1. Install missing dependencies")
        print("   2. Configure environment variables")
        print("   3. Deploy to chosen platform")
        print("   4. Monitor AI performance and costs")

def main():
    """Main function"""
    optimizer = DeploymentOptimizer()
    optimizer.run_optimization()

if __name__ == "__main__":
    main() 