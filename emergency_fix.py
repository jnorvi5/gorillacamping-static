#!/usr/bin/env python
"""
COMPLETE DUPLICATE FUNCTION AUDIT AND FIX
"""
import re
import os

print("🦍 EMERGENCY: COMPLETE FUNCTION AUDIT")
print("=====================================")

with open('app.py', 'r') as f:
    content = f.read()

# Find ALL @app.route declarations
route_pattern = r'@app\.route\([\'"][^\'"]+[\'"][^)]*\)\s*\ndef\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
matches = re.findall(route_pattern, content)

# Count function occurrences
function_counts = {}
for func_name in matches:
    function_counts[func_name] = function_counts.get(func_name, 0) + 1

# Find duplicates
duplicates = [func for func, count in function_counts.items() if count > 1]

print(f"Total route functions found: {len(matches)}")
print(f"Duplicate functions: {duplicates}")

if duplicates:
    print("\n🔧 FIXING DUPLICATES...")
    for func_name in duplicates:
        print(f"Fixing duplicate: {func_name}")
        
        # Find all occurrences
        pattern = f'(@app\\.route\\([\'"][^\'"]+[\'"][^)]*\\)\\s*\\ndef\\s+{func_name}\\s*\\([^:]*:)'
        all_matches = list(re.finditer(pattern, content))
        
        # Rename all but the first occurrence
        offset = 0
        for i, match in enumerate(all_matches[1:], 1):  # Skip first occurrence
            start = match.start() + offset
            end = match.end() + offset
            
            # Create new function name
            new_func_name = f"{func_name}_{i}"
            
            # Replace function name in match
            old_text = content[start:end]
            new_text = old_text.replace(f'def {func_name}(', f'def {new_func_name}(')
            
            # Update content
            content = content[:start] + new_text + content[end:]
            offset += len(new_text) - len(old_text)
            
            print(f"  Renamed {func_name} #{i+1} to {new_func_name}")

    # Write fixed content
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ ALL DUPLICATES FIXED!")
else:
    print("✅ No duplicate functions found")

print("\n🚀 Deploy with: git add app.py && git commit -m 'Fix all duplicate functions' && git push origin main")
