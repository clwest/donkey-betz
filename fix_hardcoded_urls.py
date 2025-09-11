#!/usr/bin/env python3
"""
Fix hardcoded URLs in frontend code to use configuration
"""

import os
import re
from pathlib import Path

def fix_hardcoded_urls(file_path):
    """Fix hardcoded URLs in a single file"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Patterns to replace
    replacements = [
        # Replace hardcoded API URLs with config
        (r"'http://localhost:8001/api/v1'", "'http://localhost:8000/api/v1'"),
        (r'"http://localhost:8001/api/v1"', '"http://localhost:8000/api/v1"'),
        (r"'http://localhost:8001/api'", "'http://localhost:8000/api'"),
        (r'"http://localhost:8001/api"', '"http://localhost:8000/api"'),
        (r"'http://localhost:8001'", "'http://localhost:8000'"),
        (r'"http://localhost:8001"', '"http://localhost:8000"'),
        
        # Replace hardcoded WebSocket URLs
        (r"'ws://localhost:8001'", "'ws://localhost:8000'"),
        (r'"ws://localhost:8001"', '"ws://localhost:8000"'),
        (r"`ws://localhost:8001", "`ws://localhost:8000"),
        
        # Fix port references in template strings
        (r":8001/", ":8000/"),
        (r":8001'", ":8000'"),
        (r':8001"', ':8000"'),
        (r":8001`", ":8000`"),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Main function to fix all files"""
    
    frontend_dir = Path('/Users/donkeyking/development/unified-donkey-betz/frontend/src')
    
    files_to_fix = [
        'store/sportsStore.ts',
        'components/editor/ChapterEditorModal.tsx',
        'features/odds/api/odds.ts',
        'pages/gallery/GalleryPage.tsx',
        'pages/AgentOrchestrationPage.tsx',
        'components/editor/MetadataEditorModal.tsx',
        'pages/voice/VoicePage.tsx',
        'services/api-simple.config.ts',
        'features/connectivity/components/ConnectivityMini.tsx',
        'features/agent-orchestra/pages/OrchestraPage.tsx',
        'components/publishing/PublishingModal.tsx',
        'components/dashboard/EmbeddingsTracker.tsx',
        'components/features/connectivity/api/health.ts',
        'components/features/research-books/ResearchBooks.tsx',
        'components/features/connectivity/api/useWSProbe.ts',
        'components/features/connectivity/components/ConnectivityPanel.tsx',
        'components/features/content-generation/ImageEditor.tsx',
    ]
    
    fixed_count = 0
    for file_rel_path in files_to_fix:
        file_path = frontend_dir / file_rel_path
        if file_path.exists():
            if fix_hardcoded_urls(file_path):
                print(f"✅ Fixed: {file_rel_path}")
                fixed_count += 1
            else:
                print(f"⏩ No changes needed: {file_rel_path}")
        else:
            print(f"❌ File not found: {file_rel_path}")
    
    print(f"\n📊 Summary: Fixed {fixed_count} files")
    
    # Also check for any remaining 8001 references
    print("\n🔍 Checking for any remaining :8001 references...")
    remaining_files = []
    for file_path in frontend_dir.rglob('*.ts'):
        if check_for_8001(file_path):
            remaining_files.append(file_path.relative_to(frontend_dir))
    for file_path in frontend_dir.rglob('*.tsx'):
        if check_for_8001(file_path):
            remaining_files.append(file_path.relative_to(frontend_dir))
    
    if remaining_files:
        print(f"⚠️  Found {len(remaining_files)} files still containing :8001")
        for f in remaining_files[:10]:  # Show first 10
            print(f"   - {f}")
    else:
        print("✅ No remaining :8001 references found!")

def check_for_8001(file_path):
    """Check if a file contains :8001"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            return ':8001' in content
    except:
        return False

if __name__ == '__main__':
    main()