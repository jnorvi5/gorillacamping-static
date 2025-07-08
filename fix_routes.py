#!/usr/bin/env python3

import re
import os
import sys

print("🦍 GORILLA CAMPING EMERGENCY FIX SCRIPT 🦍")

# Check if app.py exists
if not os.path.exists('app.py'):
    print("❌ app.py not found! Make sure you're in the right directory.")
    sys.exit(1)

# Read app.py content
with open('app.py', 'r') as f:
    content = f.read()
    print("✅ Successfully read app.py file")

# Count routes and functions
route_pattern = r"@app\.route\('([^']+)'\)\s*def\s+([^(]+)\("
routes = re.findall(route_pattern, content)

print(f"Found {len(routes)} route definitions")

# Check for duplicates
route_counts = {}
func_counts = {}
for route_path, func_name in routes:
    route_counts[route_path] = route_counts.get(route_path, 0) + 1
    func_counts[func_name] = func_counts.get(func_name, 0) + 1

duplicate_routes = [route for route, count in route_counts.items() if count > 1]
duplicate_funcs = [func for func, count in func_counts.items() if count > 1]

print(f"Duplicate routes: {duplicate_routes}")
print(f"Duplicate functions: {duplicate_funcs}")

# Replace the second high_commission_gear function with premium_gear
if 'high_commission_gear' in duplicate_funcs or '/high-commission-gear' in duplicate_routes:
    print("🔍 Found duplicate high_commission_gear - fixing...")
    
    # Find all matches
    pattern = r"(@app\.route\('/high-commission-gear'\)\s*def high_commission_gear\([^)]*\):)"
    matches = list(re.finditer(pattern, content))
    
    if len(matches) >= 2:
        # Get the second occurrence position
        start = matches[1].start()
        end = matches[1].end()
        
        # Replace with premium_gear
        new_route = "@app.route('/premium-gear')\ndef premium_gear():"
        new_content = content[:start] + new_route + content[end:]
        
        # Write back to app.py
        with open('app.py', 'w') as f:
            f.write(new_content)
            print("✅ SUCCESS! Fixed duplicate route by changing second high_commission_gear to premium_gear")
        
        # Create a backup just in case
        with open('app.py.bak', 'w') as f:
            f.write(content)
            print("✅ Created backup at app.py.bak")
    else:
        print("⚠️ Couldn't find multiple occurrences of the route/function")

# Check for sms_signup duplicates
if 'sms_signup' in duplicate_funcs or '/sms-signup' in duplicate_routes:
    print("🔍 Found duplicate sms_signup - fixing...")
    
    # Find all matches
    pattern = r"(@app\.route\('/sms-signup', methods=\['POST'\]\)\s*def sms_signup\([^)]*\):)"
    matches = list(re.finditer(pattern, content))
    
    if len(matches) >= 2:
        # Get the second occurrence position
        start = matches[1].start()
        end = matches[1].end()
        
        # Replace with sms_subscribe
        new_route = "@app.route('/sms-subscribe', methods=['POST'])\ndef sms_subscribe():"
        new_content = content[:start] + new_route + content[end:]
        
        # Write back to app.py
        with open('app.py', 'w') as f:
            f.write(new_content)
            print("✅ SUCCESS! Fixed duplicate route by changing second sms_signup to sms_subscribe")
    else:
        print("⚠️ Couldn't find multiple occurrences of sms_signup")

print("\n🚀 DEPLOYMENT INSTRUCTIONS:")
print("1. Commit this change: git add app.py && git commit -m \"Fix duplicate route definitions\"")
print("2. Push to Heroku: git push heroku main")
print("3. Verify deployment: heroku logs --tail")
