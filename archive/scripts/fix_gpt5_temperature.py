#!/usr/bin/env python3
"""
Fix temperature parameter for GPT-5 models
GPT-5 models only support default temperature (1.0), not custom values
"""

import os
import re
from pathlib import Path

def fix_temperature_for_gpt5(file_path):
    """Remove temperature parameter when using GPT-5 models"""
    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content
    changes = []

    # Pattern 1: Remove temperature from GPT-5 calls in create() methods
    pattern1 = r'(model\s*=\s*["\']gpt-5-(?:mini|nano)["\'][^)]*?)(\s*,\s*temperature\s*=\s*[^,)]+)'
    matches = re.findall(pattern1, content, re.MULTILINE | re.DOTALL)
    if matches:
        content = re.sub(pattern1, r'\1', content, flags=re.MULTILINE | re.DOTALL)
        changes.append(f"Removed temperature parameter from GPT-5 calls")

    # Pattern 2: Conditional temperature based on model
    # Look for places where we set temperature and add conditional logic
    if 'temperature=' in content and ('gpt-5-mini' in content or 'gpt-5-nano' in content):
        # For llm_enforcer.py specifically
        if 'llm_enforcer.py' in str(file_path):
            # Find the enforce_real_ai method and modify it
            pattern = r'(response = self\.openai_client\.chat\.completions\.create\([^)]*\))'
            def replace_create_call(match):
                call = match.group(1)
                if 'temperature=' in call:
                    # Build the call without temperature for GPT-5
                    new_call = '''# GPT-5 models only support default temperature
        params = {
            'model': "gpt-5-nano",  # Using GPT-5-nano for fast operations
            'messages': messages,
            'max_completion_tokens': max_tokens
        }

        # Only add temperature for non-GPT-5 models
        # (GPT-5 only supports default temperature of 1.0)
        # if temperature != 1.0:
        #     params['temperature'] = temperature

        response = self.openai_client.chat.completions.create(**params)'''
                    return new_call
                return call

            if 'def enforce_real_ai' in content:
                # Find the method and update it
                method_start = content.find('def enforce_real_ai')
                method_end = content.find('\n    def ', method_start + 1)
                if method_end == -1:
                    method_end = len(content)
                method_content = content[method_start:method_end]

                # Replace the create call in this method
                updated_method = re.sub(pattern, replace_create_call, method_content)
                if updated_method != method_content:
                    content = content[:method_start] + updated_method + content[method_end:]
                    changes.append("Modified enforce_real_ai to handle GPT-5 temperature")

    # Pattern 3: For agent files that use temperature
    if 'temperature=' in content and 'gpt-5' in content.lower():
        # For files that have simple temperature settings
        simple_pattern = r'temperature\s*=\s*[\d.]+\s*,?\s*(?:#[^\n]*)?\n'
        if 'gpt-5-mini' in content or 'gpt-5-nano' in content:
            # Comment out temperature lines for GPT-5 specific files
            new_content = re.sub(
                r'(\s*)(temperature\s*=\s*[\d.]+)',
                r'\1# \2  # GPT-5 only supports default temperature',
                content
            )
            if new_content != content:
                content = new_content
                changes.append("Commented out temperature parameters for GPT-5")

    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return changes
    return None

def main():
    """Fix temperature issues in all Python files using GPT-5"""
    project_root = Path(__file__).parent

    # Priority files that definitely need fixing based on test results
    priority_files = [
        'core/llm_enforcer.py',
        'agents/content_executor.py',
        'agents/executors/content_creator_executor.py',
        'intelligence/real_agents.py',
        'ai_core/agents/real_content_creator.py',
        'core/personal_ai_assistant_enhanced.py'
    ]

    print("🔧 Fixing temperature parameters for GPT-5 models...")
    print("=" * 60)

    total_fixed = 0

    # Fix priority files first
    for file_name in priority_files:
        file_path = project_root / file_name
        if file_path.exists():
            changes = fix_temperature_for_gpt5(file_path)
            if changes:
                print(f"✅ Fixed {file_name}")
                for change in changes:
                    print(f"   - {change}")
                total_fixed += 1

    # Also scan all Python files for any other GPT-5 usage with temperature
    for py_file in project_root.rglob('*.py'):
        if '.venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        if str(py_file.relative_to(project_root)) in priority_files:
            continue  # Already processed

        with open(py_file, 'r') as f:
            content = f.read()
            if 'gpt-5' in content.lower() and 'temperature=' in content:
                changes = fix_temperature_for_gpt5(py_file)
                if changes:
                    print(f"✅ Fixed {py_file.relative_to(project_root)}")
                    for change in changes:
                        print(f"   - {change}")
                    total_fixed += 1

    print("=" * 60)
    print(f"✨ Fixed {total_fixed} files to handle GPT-5 temperature requirements")
    print("\nNote: GPT-5 models only support the default temperature of 1.0")
    print("Temperature parameters have been removed or commented for GPT-5 calls")

if __name__ == "__main__":
    main()