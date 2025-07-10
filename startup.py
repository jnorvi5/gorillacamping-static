#!/usr/bin/env python3
"""
🦍 Guerilla Camping - Azure Startup Script
Handles the fully optimized AI system with fallbacks
"""

import os
import sys

def main():
    """Start the optimized Flask app with proper error handling"""
    
    print("🦍 Starting Guerilla Camping optimized AI system...")
    
    # Set environment variables for production
    os.environ.setdefault('FLASK_ENV', 'production')
    os.environ.setdefault('FLASK_APP', 'app:app')
    
    try:
        # Try to import and run the full optimized app
        from app import app
        print("✅ Full optimized app loaded successfully!")
        
        # Run the app
        port = int(os.environ.get('PORT', 8000))
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except ImportError as e:
        print(f"⚠️ Import error with full app: {e}")
        print("🔄 Falling back to simple app...")
        
        try:
            from app_simple import app
            print("✅ Simple app loaded as fallback!")
            port = int(os.environ.get('PORT', 8000))
            app.run(host='0.0.0.0', port=port, debug=False)
            
        except Exception as e2:
            print(f"❌ Critical error: {e2}")
            sys.exit(1)
            
    except Exception as e:
        print(f"⚠️ Error with optimized app: {e}")
        print("🔄 Falling back to simple app...")
        
        try:
            from app_simple import app
            print("✅ Simple app loaded as fallback!")
            port = int(os.environ.get('PORT', 8000))
            app.run(host='0.0.0.0', port=port, debug=False)
            
        except Exception as e2:
            print(f"❌ Critical error: {e2}")
            sys.exit(1)

if __name__ == '__main__':
    main() 