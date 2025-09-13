"""
Script to standardize API responses across all views
This updates all views to use the standardized APIResponseEnvelope
"""

import os
import re
from pathlib import Path

# Base directory for the project
BASE_DIR = Path("/Users/donkeyking/development/unified-donkey-betz")

# Files to update
VIEW_FILES = [
    "core/views_odds_sports.py",
    "sports/views.py",
    "agents/views.py",
    "core/views.py",
    "core/views_agent_orchestration.py",
    "core/views_analytics.py",
    "core/views_assistant_intelligent.py",
    "core/views_content.py",
    "core/views_knowledge.py",
    "core/views_multi_llm.py",
]

def update_imports(content):
    """Add standardized API response imports to files"""
    # Check if import already exists
    if "from core.api_responses import" in content:
        return content
    
    # Add import after other imports
    import_line = "\nfrom core.api_responses import (\n    api_success, api_error, api_paginated,\n    api_unauthorized, api_forbidden, api_not_found,\n    api_validation_error, APIResponseEnvelope\n)\n"
    
    # Find the last import statement
    import_pattern = re.compile(r"^(from|import)\s+.*$", re.MULTILINE)
    matches = list(import_pattern.finditer(content))
    
    if matches:
        last_import = matches[-1]
        insert_pos = last_import.end()
        content = content[:insert_pos] + import_line + content[insert_pos:]
    else:
        # If no imports found, add at the beginning
        content = import_line + content
    
    return content

def standardize_responses(content):
    """Replace common response patterns with standardized ones"""
    
    # Pattern 1: Response with success/error dict
    # Before: Response({'success': False, 'error': 'message'}, status=400)
    # After: api_error('message')
    content = re.sub(
        r"Response\(\s*\{\s*['\"]success['\"]\s*:\s*False\s*,\s*['\"]error['\"]\s*:\s*([^}]+)\}\s*,\s*status\s*=\s*400\s*\)",
        r"api_error(\1)",
        content
    )
    
    # Pattern 2: Response with success dict
    # Before: Response({'success': True, 'data': ...})
    # After: api_success(data=...)
    content = re.sub(
        r"Response\(\s*\{\s*['\"]success['\"]\s*:\s*True\s*,\s*['\"]data['\"]\s*:\s*([^}]+)\}\s*\)",
        r"api_success(data=\1)",
        content
    )
    
    # Pattern 3: 404 responses
    # Before: Response({'error': 'Not found'}, status=404)
    # After: api_not_found('Not found')
    content = re.sub(
        r"Response\(\s*\{[^}]*['\"]error['\"]\s*:\s*([^}]+)\}\s*,\s*status\s*=\s*404\s*\)",
        r"api_not_found(\1)",
        content
    )
    
    # Pattern 4: 401 responses
    # Before: Response({'error': 'Unauthorized'}, status=401)
    # After: api_unauthorized('Unauthorized')
    content = re.sub(
        r"Response\(\s*\{[^}]*['\"]error['\"]\s*:\s*([^}]+)\}\s*,\s*status\s*=\s*401\s*\)",
        r"api_unauthorized(\1)",
        content
    )
    
    # Pattern 5: 500 responses
    # Before: Response({'error': 'Server error'}, status=500)
    # After: APIResponseEnvelope.server_error('Server error')
    content = re.sub(
        r"Response\(\s*\{[^}]*['\"]error['\"]\s*:\s*([^}]+)\}\s*,\s*status\s*=\s*500\s*\)",
        r"APIResponseEnvelope.server_error(\1)",
        content
    )
    
    # Pattern 6: JsonResponse patterns
    # Before: JsonResponse({'success': False, 'error': 'message'}, status=400)
    # After: api_error('message')
    content = re.sub(
        r"JsonResponse\(\s*\{\s*['\"]success['\"]\s*:\s*False\s*,\s*['\"]error['\"]\s*:\s*([^}]+)\}\s*,\s*status\s*=\s*400\s*\)",
        r"api_error(\1)",
        content
    )
    
    return content

def process_file(file_path):
    """Process a single file to standardize responses"""
    try:
        full_path = BASE_DIR / file_path
        
        if not full_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return False
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Update imports
        updated_content = update_imports(content)
        
        # Standardize responses
        updated_content = standardize_responses(updated_content)
        
        # Only write if changes were made
        if updated_content != content:
            with open(full_path, 'w') as f:
                f.write(updated_content)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return False

def main():
    """Main function to process all view files"""
    print("🔧 Starting API Response Standardization")
    print("-" * 50)
    
    updated_count = 0
    
    for file_path in VIEW_FILES:
        if process_file(file_path):
            updated_count += 1
    
    print("-" * 50)
    print(f"✨ Standardization complete! Updated {updated_count}/{len(VIEW_FILES)} files")

if __name__ == "__main__":
    main()
