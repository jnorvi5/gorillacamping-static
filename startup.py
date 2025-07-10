#!/usr/bin/env python3
"""
🦍 Working startup - back to what was working this morning
"""
import os

# Set environment variables for Azure
os.environ.setdefault('PORT', '8000')

try:
    from app import app
    print("✅ Working app.py loaded (pre-optimization version)")
    
    if __name__ == "__main__":
        port = int(os.environ.get('PORT', 8000))
        print(f"🦍 Starting on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1) 