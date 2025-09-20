#!/usr/bin/env python3
"""
Update all GPT model references to GPT-5-mini or GPT-5-nano
This script updates all model references across the codebase to use the latest GPT-5 models.
"""

import os
import re
from pathlib import Path

# Model mapping
MODEL_MAPPING = {
    # Map old models to new ones
    '"gpt-4"': '"gpt-5-mini"',
    "'gpt-4'": "'gpt-5-mini'",
    '"gpt-4-turbo"': '"gpt-5-mini"',
    "'gpt-4-turbo'": "'gpt-5-mini'",
    '"gpt-4-turbo-preview"': '"gpt-5-mini"',
    "'gpt-4-turbo-preview'": "'gpt-5-mini'",
    '"gpt-4o"': '"gpt-5-mini"',
    "'gpt-4o'": "'gpt-5-mini'",
    '"gpt-3.5-turbo"': '"gpt-5-nano"',
    "'gpt-3.5-turbo'": "'gpt-5-nano'",
    '"gpt-3.5-turbo-16k"': '"gpt-5-nano"',
    "'gpt-3.5-turbo-16k'": "'gpt-5-nano'",

    # Update model references in code
    'model="gpt-4"': 'model="gpt-5-mini"',
    "model='gpt-4'": "model='gpt-5-mini'",
    'model="gpt-3.5-turbo"': 'model="gpt-5-nano"',
    "model='gpt-3.5-turbo'": "model='gpt-5-nano'",

    # Update llm_model references
    'llm_model="gpt-4"': 'llm_model="gpt-5-mini"',
    "llm_model='gpt-4'": "llm_model='gpt-5-mini'",
    'llm_model="gpt-3.5-turbo"': 'llm_model="gpt-5-nano"',
    "llm_model='gpt-3.5-turbo'": "llm_model='gpt-5-nano'",

    # Update config references
    "'llm_model': 'gpt-4'": "'llm_model': 'gpt-5-mini'",
    '"llm_model": "gpt-4"': '"llm_model": "gpt-5-mini"',
    "'llm_model': 'gpt-3.5-turbo'": "'llm_model': 'gpt-5-nano'",
    '"llm_model": "gpt-3.5-turbo"': '"llm_model": "gpt-5-nano"',

    # Update model_used references
    "'model_used': 'gpt-4'": "'model_used': 'gpt-5-mini'",
    '"model_used": "gpt-4"': '"model_used": "gpt-5-mini"',

    # Update default model references
    'DEFAULT_MODEL = "gpt-4"': 'DEFAULT_MODEL = "gpt-5-mini"',
    "DEFAULT_MODEL = 'gpt-4'": "DEFAULT_MODEL = 'gpt-5-mini'",
    'DEFAULT_MODEL = "gpt-3.5-turbo"': 'DEFAULT_MODEL = "gpt-5-nano"',
    "DEFAULT_MODEL = 'gpt-3.5-turbo'": "DEFAULT_MODEL = 'gpt-5-nano'",
}

# Files to skip (documentation, tests, etc.)
SKIP_FILES = {
    'LLM_ENDPOINTS_AUDIT_REPORT.md',
    'LLM_USAGE_MAP.md',
    'update_to_gpt5_models.py',
    'upgrade_to_gpt5_mini.py',
    '.git',
    'node_modules',
    'venv',
    'venv_ml',
    '__pycache__',
}

def should_process_file(filepath):
    """Check if file should be processed"""
    path = Path(filepath)

    # Skip if in skip list
    for skip in SKIP_FILES:
        if skip in str(path):
            return False

    # Only process Python files and specific config files
    return path.suffix in ['.py', '.yaml', '.yml', '.json', '.env.example']

def update_file(filepath):
    """Update a single file with new model references"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False, "Could not read file"

    original_content = content
    changes_made = []

    # Apply all replacements
    for old_pattern, new_pattern in MODEL_MAPPING.items():
        if old_pattern in content:
            count = content.count(old_pattern)
            content = content.replace(old_pattern, new_pattern)
            changes_made.append(f"  - Replaced '{old_pattern}' with '{new_pattern}' ({count} occurrences)")

    # Check if any changes were made
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
    print("🚀 Updating all GPT model references to GPT-5-mini and GPT-5-nano")
    print("=" * 70)

    # Get project root
    project_root = Path('/Users/donkeyking/development/unified-donkey-betz')

    files_updated = 0
    files_scanned = 0
    total_changes = 0

    # Process all files
    for root, dirs, files in os.walk(project_root):
        # Skip directories in skip list
        dirs[:] = [d for d in dirs if d not in SKIP_FILES]

        for file in files:
            filepath = Path(root) / file

            if not should_process_file(filepath):
                continue

            files_scanned += 1
            updated, changes = update_file(filepath)

            if updated:
                files_updated += 1
                total_changes += len(changes)
                print(f"\n✅ Updated: {filepath.relative_to(project_root)}")
                for change in changes[:3]:  # Show first 3 changes
                    print(change)
                if len(changes) > 3:
                    print(f"  ... and {len(changes) - 3} more changes")

    # Print summary
    print("\n" + "=" * 70)
    print("📊 Update Summary:")
    print(f"  - Files scanned: {files_scanned}")
    print(f"  - Files updated: {files_updated}")
    print(f"  - Total changes: {total_changes}")

    # Model usage summary
    print("\n🎯 Model Migration:")
    print("  - gpt-4, gpt-4-turbo, gpt-4o → gpt-5-mini (high-quality tasks)")
    print("  - gpt-3.5-turbo → gpt-5-nano (fast/efficient tasks)")

    print("\n✨ Update complete! All models have been migrated to GPT-5 series.")

    # Create verification script
    verify_script = """
# Verify no old models remain
echo "Checking for any remaining old model references..."
grep -r "gpt-4[^o]\\|gpt-3\\.5" --include="*.py" --exclude-dir=venv --exclude-dir=.git . | grep -v gpt-5 | grep -v "# Old model" | head -20
    """

    print("\n💡 To verify the update, run:")
    print(verify_script)

if __name__ == "__main__":
    main()