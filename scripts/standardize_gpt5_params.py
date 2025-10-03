#!/usr/bin/env python3
"""
Standardize all GPT-5-mini API calls to use correct parameters.

GPT-5-mini Standard Parameters:
- model="gpt-5-mini"
- max_completion_tokens=XXX  (NOT max_tokens)
- reasoning_effort="medium"   (NEW GPT-5 feature)
- NO temperature parameter    (GPT-5 uses fixed temp)
"""

import os
import re
from pathlib import Path


def standardize_file(filepath):
    """Standardize GPT-5-mini calls in a single file"""

    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content
    changes_made = []

    # Pattern to find GPT-5-mini API calls
    # Look for: model="gpt-5-mini" followed by parameters
    pattern = r'(\.chat\.completions\.create\s*\()(.*?)(model="gpt-5-mini".*?)(\))'

    def fix_call(match):
        """Fix a single API call"""
        prefix = match.group(1)
        pre_model = match.group(2)
        call_body = match.group(3)
        suffix = match.group(4)

        # Track if we made changes
        modified = False

        # 1. Replace max_tokens with max_completion_tokens
        if 'max_tokens=' in call_body and 'max_completion_tokens=' not in call_body:
            # Extract the token value
            token_match = re.search(r'max_tokens=(\d+)', call_body)
            if token_match:
                token_value = token_match.group(1)
                call_body = re.sub(r'max_tokens=\d+', f'max_completion_tokens={token_value}', call_body)
                modified = True
                changes_made.append(f"  ✓ Changed max_tokens to max_completion_tokens")

        # 2. Add reasoning_effort if missing
        if 'reasoning_effort=' not in call_body:
            # Find where to insert it (after max_completion_tokens or temperature)
            if 'max_completion_tokens=' in call_body:
                call_body = re.sub(
                    r'(max_completion_tokens=\d+)',
                    r'\1,\n                reasoning_effort="medium"  # GPT-5 reasoning capability',
                    call_body
                )
            elif 'temperature=' in call_body:
                call_body = re.sub(
                    r'(temperature=[\d.]+)',
                    r'\1,\n                reasoning_effort="medium"  # GPT-5 reasoning capability',
                    call_body
                )
            modified = True
            changes_made.append(f"  ✓ Added reasoning_effort parameter")

        # 3. Remove or comment out temperature (GPT-5 doesn't support custom temperature)
        if 'temperature=' in call_body and '# temperature=' not in call_body:
            # Comment it out instead of removing (for user review)
            call_body = re.sub(
                r'(\s+)(temperature=[\d.]+,?)',
                r'\1# \2  # GPT-5-mini uses fixed temperature',
                call_body
            )
            modified = True
            changes_made.append(f"  ✓ Commented out temperature (GPT-5 uses fixed temp)")

        if modified:
            return prefix + pre_model + call_body + suffix
        return match.group(0)

    # Apply fixes
    content = re.sub(pattern, fix_call, content, flags=re.DOTALL)

    # Write back if changes were made
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return len(changes_made)

    return 0


def main():
    """Standardize all Python files"""

    directories = ['./ai_core', './intelligence', './core', './config']
    total_files = 0
    total_changes = 0

    print("=" * 70)
    print("GPT-5-mini Parameter Standardization")
    print("=" * 70)
    print("\n📋 Standard Parameters:")
    print("  • model='gpt-5-mini'")
    print("  • max_completion_tokens=XXX  (NOT max_tokens)")
    print("  • reasoning_effort='medium'   (NEW)")
    print("  • temperature=X.X             (REMOVED - GPT-5 uses fixed)")
    print("\n" + "=" * 70)

    for directory in directories:
        if not os.path.exists(directory):
            continue

        for filepath in Path(directory).rglob('*.py'):
            # Skip __pycache__ and venv
            if '__pycache__' in str(filepath) or 'venv' in str(filepath):
                continue

            # Check if file contains gpt-5-mini
            with open(filepath, 'r') as f:
                if 'gpt-5-mini' not in f.read():
                    continue

            print(f"\n📄 Processing: {filepath}")
            changes = standardize_file(filepath)

            if changes > 0:
                print(f"  ✅ Made {changes} parameter fixes")
                total_files += 1
                total_changes += changes
            else:
                print(f"  ℹ️  Already standardized")

    print("\n" + "=" * 70)
    print(f"✅ Complete!")
    print(f"   Files updated: {total_files}")
    print(f"   Total changes: {total_changes}")
    print("=" * 70)


if __name__ == '__main__':
    main()
