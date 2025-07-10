#!/usr/bin/env python3
"""🦍 NUCLEAR STARTUP - Single file deployment"""
import os

try:
    from app_nuclear import app
    print("🦍 NUCLEAR APP LOADED - Single file, guaranteed deployment!")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=False)
except Exception as e:
    print(f"💥 Error: {e}")
    exit(1) 