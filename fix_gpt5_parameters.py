#!/usr/bin/env python3
"""
Fix GPT-5-mini parameters to use correct naming conventions
- max_tokens -> max_completion_tokens
- reasoning_steps -> reasoning_effort
- thought parameter is removed (not needed)
- temperature is always 1.0 (implicit, can be omitted)
"""

import re
from pathlib import Path

def fix_agent_factory():
    """Fix parameters in agent_factory.py"""

    file_path = Path("intelligence/agent_factory.py")
    with open(file_path, 'r') as f:
        content = f.read()

    original = content

    # Fix the API call parameters
    content = re.sub(
        r'max_tokens=32768,  # GPT-5 enhanced token limit\s*\n\s*temperature=0\.9,  # GPT-5 enhanced temperature\s*\n\s*thought=True,  # Enable GPT-5 reasoning\s*\n\s*reasoning_steps=3  # Multi-step reasoning',
        'max_completion_tokens=2000,  # GPT-5-mini completion tokens\n                        temperature=1.0,  # GPT-5 always uses 1.0\n                        reasoning_effort="medium"  # GPT-5-mini reasoning capability',
        content
    )

    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def fix_real_agents():
    """Fix parameters in real_agents.py"""

    file_path = Path("intelligence/real_agents.py")
    with open(file_path, 'r') as f:
        content = f.read()

    original = content

    # Replace all occurrences of the incorrect parameters
    # Pattern 1: Fix max_tokens parameter
    content = re.sub(
        r'max_tokens=32768\s*#.*',
        'max_completion_tokens=2000  # GPT-5-mini completion tokens',
        content
    )

    # Pattern 2: Fix temperature, thought, and reasoning_steps
    content = re.sub(
        r'temperature=1\.2,\s*#.*\n\s*thought=True,\s*#.*\n\s*reasoning_steps=3,\s*#.*',
        'temperature=1.0,  # GPT-5 always uses 1.0\n                reasoning_effort="medium"  # GPT-5-mini reasoning capability',
        content
    )

    # Also need to fix the closing parenthesis alignment
    content = re.sub(
        r'max_completion_tokens=2000  # GPT-5-mini completion tokens\n            \)',
        'max_completion_tokens=2000,  # GPT-5-mini completion tokens\n                reasoning_effort="medium"  # GPT-5-mini reasoning capability\n            )',
        content
    )

    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def fix_agent_execution_pipeline():
    """Fix parameters in agent_execution_pipeline.py"""

    file_path = Path("intelligence/agent_execution_pipeline.py")
    if not file_path.exists():
        return False

    with open(file_path, 'r') as f:
        content = f.read()

    original = content

    # Fix max_tokens to max_completion_tokens
    content = re.sub(
        r'max_tokens=32768\s*#.*',
        'max_completion_tokens=2000  # GPT-5-mini completion tokens',
        content
    )

    # Fix any temperature/thought/reasoning_steps patterns
    content = re.sub(
        r'temperature=1\.2,.*\n.*thought=True,.*\n.*reasoning_steps=\d+',
        'temperature=1.0,  # GPT-5 always uses 1.0\n                    reasoning_effort="medium"  # GPT-5-mini reasoning capability',
        content
    )

    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Main function to fix all GPT-5-mini parameters"""

    print("=" * 80)
    print("FIXING GPT-5-MINI PARAMETERS")
    print("=" * 80)
    print()

    print("Correct GPT-5-mini parameters:")
    print("  • max_completion_tokens (NOT max_tokens)")
    print("  • reasoning_effort='medium' (NOT reasoning_steps)")
    print("  • temperature=1.0 (always, can be omitted)")
    print("  • NO 'thought' parameter needed")
    print()

    files_fixed = []

    # Fix agent_factory.py
    print("Fixing intelligence/agent_factory.py...")
    if fix_agent_factory():
        files_fixed.append("agent_factory.py")
        print("  ✅ Fixed!")
    else:
        print("  ⚠️  No changes needed or file not found")

    # Fix real_agents.py
    print("Fixing intelligence/real_agents.py...")
    if fix_real_agents():
        files_fixed.append("real_agents.py")
        print("  ✅ Fixed!")
    else:
        print("  ⚠️  No changes needed or file not found")

    # Fix agent_execution_pipeline.py
    print("Fixing intelligence/agent_execution_pipeline.py...")
    if fix_agent_execution_pipeline():
        files_fixed.append("agent_execution_pipeline.py")
        print("  ✅ Fixed!")
    else:
        print("  ⚠️  No changes needed or file not found")

    print()
    print("=" * 80)
    print("FIX COMPLETE!")
    print("=" * 80)

    if files_fixed:
        print(f"✅ Fixed {len(files_fixed)} files:")
        for f in files_fixed:
            print(f"   • {f}")
        print()
        print("GPT-5-mini will now use correct parameters:")
        print("  • max_completion_tokens=2000")
        print("  • reasoning_effort='medium'")
        print("  • temperature=1.0")
        print()
        print("This prevents empty string responses!")
    else:
        print("⚠️  No files needed fixing")

if __name__ == "__main__":
    main()