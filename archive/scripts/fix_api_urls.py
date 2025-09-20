#!/usr/bin/env python3
import os
import re

# Directory containing service files
services_dir = "frontend/src/services"

# Pattern to match apiClient calls with /api/v1/
pattern = r"(apiClient\.(get|post|put|delete|patch)\(')(/api/v1/)"

# Replacement - remove the /api prefix
replacement = r"\1/v1/"

# Process each TypeScript file
for filename in os.listdir(services_dir):
    if filename.endswith(".ts"):
        filepath = os.path.join(services_dir, filename)
        
        # Read the file
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Count replacements
        original_count = len(re.findall(pattern, content))
        
        if original_count > 0:
            # Replace all occurrences
            updated_content = re.sub(pattern, replacement, content)
            
            # Write back
            with open(filepath, 'w') as f:
                f.write(updated_content)
            
            print(f"Fixed {original_count} URLs in {filename}")
        else:
            # Check for other patterns
            if '/api/v1/' in content and 'apiClient' in content:
                print(f"Note: {filename} may have different patterns that need manual review")

print("\nDone! All standard API URLs have been fixed.")
print("Please check the files marked for manual review if any.")