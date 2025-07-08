#!/usr/bin/env python3

"""
EMERGENCY FIX SCRIPT: Repair duplicate routes and get site back online
"""

import re

print("🦍 GORILLA CAMPING RESCUE TOOL 🦍")
print("=================================")

# Read the app.py file
try:
    with open('app.py', 'r') as f:
        content = f.read()
    print("✅ Successfully read app.py")
except Exception as e:
    print(f"❌ Error reading app.py: {e}")
    exit(1)

# Find duplicate routes
route_pattern = r"@app\.route\('([^']+)'\)\s*def\s+([^(]+)\("
routes = re.findall(route_pattern, content)

# Track duplicates
route_counts = {}
for route_path, func_name in routes:
    route_counts[func_name] = route_counts.get(func_name, 0) + 1
    
duplicates = [func for func, count in route_counts.items() if count > 1]
print(f"Found {len(duplicates)} duplicate route function(s): {', '.join(duplicates)}")

if 'high_commission_gear' in duplicates:
    # Fix the duplicate high_commission_gear route by renaming second occurrence
    pattern = r"(@app\.route\('/high-commission-gear'\)\s*def high_commission_gear\([^)]*\):)"
    matches = re.findall(pattern, content)
    
    if len(matches) >= 2:
        # Replace second occurrence with premium_gear
        fixed_content = re.sub(pattern, 
                              "@app.route('/premium-gear')\ndef premium_gear():", 
                              content, 
                              count=1)
        
        # Write the fixed content back to app.py
        try:
            with open('app.py', 'w') as f:
                f.write(fixed_content)
            print("✅ Fixed duplicate route 'high_commission_gear' -> 'premium_gear'")
        except Exception as e:
            print(f"❌ Error writing fixed app.py: {e}")
    else:
        print("⚠️ Couldn't locate both instances of high_commission_gear")
else:
    print("⚠️ No 'high_commission_gear' duplicate found - check for other issues")

print("\n🚀 NEXT STEPS:")
print("1. Run this script: python fix_app.py")
print("2. Commit and deploy the fixed code")
print("3. Add the revenue templates from my previous message")
