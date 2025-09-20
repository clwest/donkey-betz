#!/usr/bin/env python3
"""
Fix remaining /api/v1/ references in service files that use template literals
"""

import os
import re

def fix_api_urls_in_file(filepath):
    """Fix /api/v1/ references in a single file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Count initial matches
    initial_count = len(re.findall(r'/api/v1/', content))
    
    if initial_count == 0:
        return 0
    
    # Fix template literal patterns
    patterns = [
        # Template literals with apiClient methods
        (r"(\`)/api/v1/", r"\1/v1/"),
        # String concatenation patterns
        (r"(['\"])/api/v1/", r"\1/v1/"),
        # Property assignments
        (r"(=\s*['\"])/api/v1/", r"\1/v1/"),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Count remaining matches
    final_count = len(re.findall(r'/api/v1/', content))
    
    # Write back if changes were made
    if final_count < initial_count:
        with open(filepath, 'w') as f:
            f.write(content)
        return initial_count - final_count
    
    return 0

def main():
    services_dir = 'frontend/src/services'
    total_fixed = 0
    files_modified = []
    
    for filename in os.listdir(services_dir):
        if filename.endswith('.ts') or filename.endswith('.tsx'):
            filepath = os.path.join(services_dir, filename)
            fixed = fix_api_urls_in_file(filepath)
            if fixed > 0:
                total_fixed += fixed
                files_modified.append(f"{filename} ({fixed} occurrences)")
    
    print(f"Fixed {total_fixed} /api/v1/ references")
    if files_modified:
        print("Modified files:")
        for file in files_modified:
            print(f"  - {file}")
    
    # Check for any remaining /api/v1/ references
    remaining = []
    for filename in os.listdir(services_dir):
        if filename.endswith('.ts') or filename.endswith('.tsx'):
            filepath = os.path.join(services_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()
                matches = re.findall(r'/api/v1/', content)
                if matches:
                    remaining.append(f"{filename} ({len(matches)} remaining)")
    
    if remaining:
        print("\nFiles with remaining /api/v1/ references:")
        for file in remaining:
            print(f"  - {file}")

if __name__ == '__main__':
    main()