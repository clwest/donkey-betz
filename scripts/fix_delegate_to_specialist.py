#!/usr/bin/env python3
"""
Session 833: Batch fix for delegate_to_specialist tool handling

This script finds all agent files that have _execute_tool methods returning
"Unknown tool" errors, and adds proper delegate_to_specialist handling.

Usage:
    python scripts/fix_delegate_to_specialist.py --dry-run  # Preview changes
    python scripts/fix_delegate_to_specialist.py            # Apply changes
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Tuple

# Root directory for agents
AGENTS_DIR = Path(__file__).parent.parent / "core" / "agents"

# Pattern to find files with "Unknown tool" error
UNKNOWN_TOOL_PATTERN = re.compile(r'Unknown tool')

# Pattern to check if delegate_to_specialist is already handled
DELEGATE_PATTERN = re.compile(r'delegate_to_specialist')

# Patterns to find the else clause before "Unknown tool"
ELSE_PATTERNS = [
    # Pattern 1: else: return {"error": f"Unknown tool...
    (
        re.compile(
            r'(\n(\s+))else:\s*\n\s+return\s*\{[^}]*Unknown tool',
            re.MULTILINE | re.DOTALL
        ),
        'simple_else'
    ),
    # Pattern 2: Direct return {"error": f"Unknown tool...  (no else, possibly blank line before)
    (
        re.compile(
            r'(\n\n(\s+))return\s*\{[^}]*Unknown tool[^}]*\}',
            re.MULTILINE
        ),
        'direct_return_blank'
    ),
    # Pattern 3: Direct return {"error": f"Unknown tool... (no blank line)
    (
        re.compile(
            r'(\n(\s+))return\s*\{[^}]*Unknown tool[^}]*\}',
            re.MULTILINE
        ),
        'direct_return'
    ),
]


def get_delegation_code(indent: str, arg_name: str = 'arguments') -> str:
    """Generate the delegate_to_specialist handler code with proper indentation."""
    # Strip any newlines from indent - we only want spaces
    indent = indent.replace('\n', '')
    lines = [
        f'{indent}elif tool_name == "delegate_to_specialist":',
        f'{indent}    # Session 833: Handle delegation properly',
        f'{indent}    return self._handle_delegate_to_specialist(',
        f"{indent}        specialist_agent={arg_name}.get('specialist_agent', ''),",
        f"{indent}        task={arg_name}.get('task', ''),",
        f"{indent}        context={arg_name}.get('context', ''),",
        f"{indent}        delegation_context=getattr(self, '_current_delegation_context', {{}})",
        f'{indent}    )',
    ]
    return '\n' + '\n'.join(lines)


def detect_arg_name(content: str) -> str:
    """Detect what argument name is used in the _execute_tool method."""
    # Common patterns
    if re.search(r'def _execute_tool\(self,\s*tool_name[^,]*,\s*tool_input', content):
        return 'tool_input'
    if re.search(r'def _execute_tool\(self,\s*tool_name[^,]*,\s*args', content):
        return 'args'
    if re.search(r'def _execute_tool\(self,\s*tool_name[^,]*,\s*arguments', content):
        return 'arguments'
    if re.search(r'def _execute_tool\(self,\s*tool_name[^,]*,\s*parameters', content):
        return 'parameters'
    # Default
    return 'arguments'


def find_agents_needing_fix() -> List[Path]:
    """Find all agent files that need the delegate_to_specialist fix."""
    agents_needing_fix = []

    for root, dirs, files in os.walk(AGENTS_DIR):
        # Skip __pycache__ and test directories
        dirs[:] = [d for d in dirs if d not in ('__pycache__', 'tests', '__init__')]

        for file in files:
            if not file.endswith('.py'):
                continue
            if file.startswith('__'):
                continue

            filepath = Path(root) / file
            content = filepath.read_text()

            # Check if file has "Unknown tool" error
            if not UNKNOWN_TOOL_PATTERN.search(content):
                continue

            # Check if delegate_to_specialist is already handled
            if DELEGATE_PATTERN.search(content):
                # Already has the handler
                continue

            agents_needing_fix.append(filepath)

    return agents_needing_fix


def fix_agent_file(filepath: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Fix a single agent file by adding delegate_to_specialist handler.

    Returns:
        Tuple of (success, message)
    """
    content = filepath.read_text()
    original_content = content

    # Detect the argument name used
    arg_name = detect_arg_name(content)

    # Try each pattern to find where to insert the delegation code
    for pattern, pattern_type in ELSE_PATTERNS:
        match = pattern.search(content)
        if match:
            # Get the indentation from the match
            indent = match.group(2) if len(match.groups()) >= 2 else '        '

            # Generate the delegation code
            delegation_code = get_delegation_code(indent, arg_name)

            if pattern_type == 'direct_return_blank':
                # Insert before the blank line + return
                insert_pos = match.start() + 1  # After the first newline
                new_content = content[:insert_pos] + delegation_code + content[insert_pos:]
            elif pattern_type == 'direct_return':
                # Insert before the direct return
                insert_pos = match.start() + 1  # After the newline
                new_content = content[:insert_pos] + delegation_code + content[insert_pos:]
            else:
                # Insert before the else clause
                insert_pos = match.start() + 1  # After the newline
                new_content = content[:insert_pos] + delegation_code + content[insert_pos:]

            if dry_run:
                return True, f"Would add delegate_to_specialist handler (arg: {arg_name}, pattern: {pattern_type})"

            # Write the fixed content
            filepath.write_text(new_content)
            return True, f"Added delegate_to_specialist handler (arg: {arg_name}, pattern: {pattern_type})"

    return False, "Could not find suitable insertion point"


def main():
    parser = argparse.ArgumentParser(description='Fix delegate_to_specialist handling in agents')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    print("=" * 60)
    print("Session 833: Batch fix for delegate_to_specialist")
    print("=" * 60)

    if args.dry_run:
        print("\n[DRY RUN MODE - No changes will be made]\n")

    # Find agents needing fix
    agents = find_agents_needing_fix()

    print(f"\nFound {len(agents)} agents needing delegate_to_specialist fix:\n")

    fixed_count = 0
    failed_count = 0

    for agent_path in sorted(agents):
        relative_path = agent_path.relative_to(AGENTS_DIR.parent.parent)

        success, message = fix_agent_file(agent_path, dry_run=args.dry_run)

        if success:
            fixed_count += 1
            status = "✅" if not args.dry_run else "🔍"
            print(f"{status} {relative_path}")
            if args.verbose:
                print(f"   {message}")
        else:
            failed_count += 1
            print(f"❌ {relative_path}")
            print(f"   {message}")

    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"Summary: {fixed_count} files would be fixed, {failed_count} failed")
        print("\nRun without --dry-run to apply changes.")
    else:
        print(f"Summary: {fixed_count} files fixed, {failed_count} failed")
    print("=" * 60)


if __name__ == '__main__':
    main()
