#!/usr/bin/env python3
"""
Fix GPT-5 parameter usage - replace max_tokens with max_completion_tokens for GPT-5 models
"""

import os
import re
from pathlib import Path

def fix_max_tokens_in_file(filepath):
    """Fix max_tokens parameter in a single file for GPT-5 models"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False, "Could not read file"

    original_content = content
    changes_made = []

    # Pattern to find GPT-5 model calls with max_tokens
    patterns = [
        # Pattern 1: Files that explicitly use GPT-5 models
        (r'(model\s*=\s*["\']gpt-5[^"\']*["\'][^}]*?)max_tokens(\s*=)', r'\1max_completion_tokens\2'),

        # Pattern 2: When model is a variable that could be GPT-5
        (r'(\.chat\.completions\.create\([^)]*?)max_tokens(\s*=)', r'\1max_completion_tokens\2'),
    ]

    for pattern, replacement in patterns:
        # Check if this file has GPT-5 references
        if 'gpt-5' in content.lower() or 'GPT-5' in content:
            # Apply the replacement
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes_made.append(f"Fixed max_tokens -> max_completion_tokens for GPT-5")
                content = new_content

    # Save if changes were made
    if content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes_made
        except:
            return False, "Could not write file"

    return False, []

def main():
    """Main execution"""
    print("🔧 Fixing GPT-5 max_tokens parameter usage")
    print("=" * 70)

    # Get project root
    project_root = Path('/Users/donkeyking/development/unified-donkey-betz')

    # Files to check
    critical_files = [
        'intelligence/income_builder.py',
        'intelligence/agent_execution_pipeline.py',
        'intelligence/agent_factory.py',
        'ai_core/agents/real_content_creator.py',
        'ai_core/agents/job_application_orchestrator.py',
        'agents/executors/content_creator_executor.py',
        'agents/executors/income_builder_executor.py',
        'agents/executors/base_executor.py',
        'content/ai_providers.py'
    ]

    files_fixed = 0

    for file_path in critical_files:
        full_path = project_root / file_path
        if full_path.exists():
            fixed, changes = fix_max_tokens_in_file(full_path)
            if fixed:
                files_fixed += 1
                print(f"✅ Fixed: {file_path}")
                for change in changes:
                    print(f"   - {change}")

    # Also search for any other Python files with the issue
    print("\n🔍 Scanning for any other files needing fixes...")

    for root, dirs, files in os.walk(project_root):
        # Skip directories
        if any(skip in str(root) for skip in ['.git', 'venv', '__pycache__', 'node_modules']):
            continue

        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file

                # Skip if already processed
                if any(str(filepath).endswith(cf) for cf in critical_files):
                    continue

                # Check if file needs fixing
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Quick check if file has GPT-5 and max_tokens
                    if ('gpt-5' in content.lower() or 'GPT-5' in content) and 'max_tokens' in content:
                        fixed, changes = fix_max_tokens_in_file(filepath)
                        if fixed:
                            files_fixed += 1
                            print(f"✅ Fixed: {filepath.relative_to(project_root)}")
                except:
                    continue

    # Summary
    print("\n" + "=" * 70)
    print(f"📊 Fixed {files_fixed} files")
    print("✨ GPT-5 parameter updates complete!")

if __name__ == "__main__":
    main()