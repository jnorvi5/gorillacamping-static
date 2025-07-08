#!/usr/bin/env python
"""
EMERGENCY SITE FIX: Repairs duplicate routes in app.py
"""
import re
import os

print("🦍 GORILLA CAMPING EMERGENCY FIX")
print("--------------------------------")

# Check if app.py exists
if not os.path.exists('app.py'):
    print("❌ ERROR: app.py not found!")
    exit(1)

# Read the current app.py file
with open('app.py', 'r') as f:
    content = f.read()
    print("✅ Successfully read app.py file")

# Count duplicates
high_gear_count = content.count("def high_commission_gear()")
print(f"Found {high_gear_count} instances of high_commission_gear()")

if high_gear_count <= 1:
    print("No duplicates found. Site should be working correctly.")
    exit(0)

# Create pattern to find the second instance of the route
pattern = r'(@app\.route\(\'/high-commission-gear\'\)[^@]*?def high_commission_gear\(\):)'
matches = list(re.finditer(pattern, content))

if len(matches) > 1:
    # Get the second match
    match = matches[1]
    start, end = match.span()
    
    # Replace with premium_gear
    replacement = content[start:end].replace(
        "@app.route('/high-commission-gear')", 
        "@app.route('/premium-gear')"
    ).replace(
        "def high_commission_gear():", 
        "def premium_gear():"
    )
    
    # Create new content
    new_content = content[:start] + replacement + content[end:]
    
    # Write back to file
    with open('app.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Successfully replaced duplicate route!")
else:
    print("❌ Could not locate duplicate pattern")

# Verify fix
with open('app.py', 'r') as f:
    fixed_content = f.read()
    if fixed_content.count("def high_commission_gear()") == 1:
        print("✅ VERIFICATION: Duplicate routes fixed successfully!")
    else:
        print("❌ VERIFICATION FAILED: Still found multiple routes")
