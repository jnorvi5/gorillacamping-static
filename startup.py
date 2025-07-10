#!/usr/bin/env python3
"""
🦍 Simple startup - back to basics
"""
import os

try:
    from app import app
    print("✅ Original app loaded")
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
except Exception as e:
    print(f"Error: {e}")
    exit(1) 