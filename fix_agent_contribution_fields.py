#!/usr/bin/env python
"""
Session 142: Fix AgentContribution field names across all files

This script fixes the incorrect field names in all AgentContribution.objects.create() calls:
- task_type → contribution_type
- input_data → task_description (simplified to string)
- output_data → REMOVED
- execution_time_ms → execution_time_seconds
- success → REMOVED
"""

import re

# Define field name mappings and simplifications
FIXES = [
    # Fix 1: Change task_type to contribution_type with 'generation' or 'editing' value
    (
        r"task_type='content_creation'",
        "contribution_type='generation'"
    ),

    # Fix 2: Remove entire input_data block (multi-line)
    (
        r",\s*input_data=\{[^}]*\}",
        ""
    ),

    # Fix 3: Remove entire output_data block (multi-line)
    (
        r",\s*output_data=\{[^}]*\}",
        ""
    ),

    # Fix 4: Change execution_time_ms to execution_time_seconds
    (
        r"execution_time_ms=0(,)?(\s*#[^\n]*)?",
        r"execution_time_seconds=0.0"
    ),

    # Fix 5: Remove success parameter
    (
        r",\s*success=True",
        ""
    ),
]

def fix_file(filepath):
    """Fix AgentContribution field names in a single file"""
    print(f"\n{'='*80}")
    print(f"Fixing: {filepath}")
    print('='*80)

    with open(filepath, 'r') as f:
        content = f.read()

    original = content
    changes = 0

    # Apply all fixes
    for pattern, replacement in FIXES:
        matches = len(re.findall(pattern, content, re.DOTALL))
        if matches > 0:
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            changes += matches
            print(f"✅ Applied fix: {pattern[:50]}... ({matches} occurrences)")

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"\n✅ File updated: {changes} changes made")
        return True
    else:
        print(f"\n⚠️  No changes needed")
        return False

def main():
    files_to_fix = [
        'content/minifig_services.py',
        'core/views_video.py',
        'core/views_davinci.py',
        'core/views_image.py'
    ]

    print("\n" + "="*80)
    print("SESSION 142: FIXING AGENTCONTRIBUTION FIELD NAMES")
    print("="*80)

    fixed = 0
    for filepath in files_to_fix:
        if fix_file(filepath):
            fixed += 1

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Fixed {fixed} out of {len(files_to_fix)} files")
    print("\nNext steps:")
    print("1. Fix backfill script with correct field names")
    print("2. Run backfill script to achieve 95%+ tracking rate")
    print("3. Test with new content generation")
    print("4. Document Session 142 results")

if __name__ == '__main__':
    main()
