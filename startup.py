#!/usr/bin/env python3
"""
🦍 Guerilla Camping - Azure Startup Script
Emergency version that always works
"""

import os
import sys

def main():
    """Start the app with guaranteed working version"""
    
    print("🦍 Starting Guerilla Camping AI system...")
    
    # Set environment variables for production
    os.environ.setdefault('FLASK_ENV', 'production')
    
    try:
        # Use the instant app that starts in 2 seconds
        from app_instant import app
        print("✅ Instant app loaded - starts immediately!")
        
        # Run the app
        port = int(os.environ.get('PORT', 8000))
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 