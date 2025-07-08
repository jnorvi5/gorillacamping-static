#!/usr/bin/env python
"""
EMERGENCY SITE FIX: Repairs duplicate routes in app.py
"""
import re
import os
import sys

print("🦍 GORILLA CAMPING EMERGENCY FIX")
print("--------------------------------")

try:
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ ERROR: app.py not found! Make sure you're in the right directory.")
        sys.exit(1)

    # Read the current app.py file
    with open('app.py', 'r') as f:
        content = f.read()
        print("✅ Successfully read app.py file")

    # Fix the duplicate high_commission_gear route
    if content.count("def high_commission_gear()") > 1:
        print("🔍 Found duplicate high_commission_gear route - fixing...")
        content = content.replace("@app.route('/high-commission-gear')\ndef high_commission_gear():", 
                               "@app.route('/premium-gear')\ndef premium_gear():", 1)

    # Fix duplicate sms_signup route if it exists
    if content.count("def sms_signup()") > 1:
        print("🔍 Found duplicate sms_signup route - fixing...")
        content = content.replace("@app.route('/sms-signup', methods=['POST'])\ndef sms_signup():", 
                               "@app.route('/sms-subscribe', methods=['POST'])\ndef sms_subscribe():", 1)

    # Write the fixed content back
    with open('app.py', 'w') as f:
        f.write(content)
        print("✅ SUCCESS! Fixed app.py - duplicate routes removed")

    print("\n🚀 DEPLOYMENT INSTRUCTIONS:")
    print("1. Run: git add app.py")
    print("2. Run: git commit -m \"Fix duplicate route definitions\"")
    print("3. Run: git push origin main")
    print("4. Check if site is back online")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    sys.exit(1)
