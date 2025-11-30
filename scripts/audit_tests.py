#!/usr/bin/env python3
"""
Test File Audit Script for Unified Donkey Betz Platform.

Analyzes all test files in the tests/ directory to determine:
- Which files are proper tests (contain test_ functions/classes)
- Which files are debug/verification scripts (should move to scripts/)
- Which files are empty or broken
- Test framework usage (pytest vs unittest vs django.test)
- Duplicate file names across directories

Usage:
    python scripts/audit_tests.py
"""
import os
import ast
import sys
from collections import defaultdict
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def analyze_test_file(filepath: str) -> dict:
    """Analyze a single test file for structure and quality."""
    result = {
        'path': filepath,
        'relative_path': str(Path(filepath).relative_to(ROOT)),
        'filename': os.path.basename(filepath),
        'directory': str(Path(filepath).parent.relative_to(ROOT)),
        'lines': 0,
        'test_functions': [],
        'test_classes': [],
        'test_count': 0,
        'is_proper_test': False,
        'uses_pytest': False,
        'uses_unittest': False,
        'uses_django_test': False,
        'has_main_block': False,
        'imports': [],
        'error': None,
        'category': 'unknown',
        'recommendation': None,
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        result['error'] = f'Read error: {e}'
        result['category'] = 'error'
        result['recommendation'] = 'Fix or remove'
        return result

    result['lines'] = len(content.split('\n'))

    # Check for empty files
    if result['lines'] < 5 or len(content.strip()) < 50:
        result['category'] = 'empty'
        result['recommendation'] = 'Remove or add tests'
        return result

    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        result['error'] = f'Parse error: {e}'
        result['category'] = 'error'
        result['recommendation'] = 'Fix syntax or remove'
        return result

    # Analyze AST
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith('test_'):
                result['test_functions'].append(node.name)
        elif isinstance(node, ast.ClassDef):
            if node.name.startswith('Test'):
                result['test_classes'].append(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                result['imports'].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                result['imports'].append(node.module)

    # Check for if __name__ == '__main__': block (indicates script)
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            if isinstance(node.test, ast.Compare):
                if hasattr(node.test, 'left') and isinstance(node.test.left, ast.Name):
                    if node.test.left.id == '__name__':
                        result['has_main_block'] = True
                        break

    result['test_count'] = len(result['test_functions'])
    result['is_proper_test'] = result['test_count'] > 0 or len(result['test_classes']) > 0

    # Check framework usage
    imports_str = ' '.join(result['imports'])
    result['uses_pytest'] = 'pytest' in imports_str
    result['uses_unittest'] = 'unittest' in imports_str
    result['uses_django_test'] = 'django.test' in imports_str or 'django' in imports_str

    # Categorize the file
    filename = result['filename'].lower()

    # Check for debug/verification scripts
    if filename.startswith('debug_') or 'debug' in result['directory']:
        result['category'] = 'debug_script'
        result['recommendation'] = 'Move to scripts/debug/'
    elif filename.startswith('verify_') or filename.startswith('quick_'):
        result['category'] = 'verification_script'
        result['recommendation'] = 'Move to scripts/'
    elif '_backup' in filename or 'backup' in filename:
        result['category'] = 'backup'
        result['recommendation'] = 'Delete'
    elif not result['is_proper_test'] and result['has_main_block']:
        result['category'] = 'script'
        result['recommendation'] = 'Move to scripts/'
    elif not result['is_proper_test']:
        result['category'] = 'not_test'
        result['recommendation'] = 'Add test functions or move to scripts/'
    elif result['test_count'] == 0 and len(result['test_classes']) > 0:
        result['category'] = 'valid_class_based'
        result['recommendation'] = 'Keep - uses class-based tests'
    else:
        result['category'] = 'valid'
        result['recommendation'] = 'Keep'

    return result


def find_duplicates(results: list) -> dict:
    """Find duplicate filenames across directories."""
    filename_map = defaultdict(list)
    for r in results:
        filename_map[r['filename']].append(r['relative_path'])

    duplicates = {k: v for k, v in filename_map.items() if len(v) > 1}
    return duplicates


def main():
    tests_dir = ROOT / 'tests'

    if not tests_dir.exists():
        print("ERROR: tests/ directory not found!")
        return

    print("=" * 70)
    print("TEST FILE AUDIT REPORT")
    print("=" * 70)
    print(f"\nScanning: {tests_dir}\n")

    results = []

    # Find all Python files in tests/
    for root, dirs, files in os.walk(tests_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']

        for f in files:
            if f.endswith('.py') and not f.startswith('__'):
                filepath = os.path.join(root, f)
                analysis = analyze_test_file(filepath)
                results.append(analysis)

    # Sort by category for organized output
    results.sort(key=lambda x: (x['category'], x['relative_path']))

    # Group by category
    categories = defaultdict(list)
    for r in results:
        categories[r['category']].append(r)

    # Print summary
    print("-" * 70)
    print("SUMMARY BY CATEGORY")
    print("-" * 70)

    category_order = ['valid', 'valid_class_based', 'debug_script', 'verification_script',
                      'script', 'backup', 'not_test', 'empty', 'error', 'unknown']

    total_tests = 0
    for cat in category_order:
        if cat in categories:
            items = categories[cat]
            test_count = sum(r['test_count'] for r in items)
            total_tests += test_count

            emoji = {
                'valid': '✓',
                'valid_class_based': '✓',
                'debug_script': '⚠',
                'verification_script': '⚠',
                'script': '⚠',
                'backup': '✗',
                'not_test': '?',
                'empty': '✗',
                'error': '✗',
                'unknown': '?'
            }.get(cat, '?')

            print(f"\n{emoji} {cat.upper()}: {len(items)} files, {test_count} test functions")

            for r in items[:10]:  # Show first 10 of each category
                test_info = f"({r['test_count']} tests)" if r['test_count'] > 0 else ""
                print(f"   {r['relative_path']} {test_info}")

            if len(items) > 10:
                print(f"   ... and {len(items) - 10} more")

    # Find duplicates
    duplicates = find_duplicates(results)
    if duplicates:
        print("\n" + "-" * 70)
        print("DUPLICATE FILENAMES")
        print("-" * 70)
        for filename, paths in duplicates.items():
            print(f"\n  {filename}:")
            for p in paths:
                print(f"    - {p}")

    # Print actionable items
    print("\n" + "=" * 70)
    print("ACTIONABLE ITEMS")
    print("=" * 70)

    # Files to move to scripts/
    to_move = [r for r in results if r['recommendation'] and 'Move' in r['recommendation']]
    if to_move:
        print(f"\n📁 FILES TO MOVE TO scripts/ ({len(to_move)} files):")
        for r in to_move:
            print(f"   mv {r['relative_path']} scripts/")

    # Files to delete
    to_delete = [r for r in results if r['recommendation'] == 'Delete']
    if to_delete:
        print(f"\n🗑️  FILES TO DELETE ({len(to_delete)} files):")
        for r in to_delete:
            print(f"   rm {r['relative_path']}")

    # Files to fix
    to_fix = [r for r in results if r['category'] in ['error', 'empty']]
    if to_fix:
        print(f"\n🔧 FILES TO FIX OR REMOVE ({len(to_fix)} files):")
        for r in to_fix:
            error_info = f" - {r['error']}" if r['error'] else ""
            print(f"   {r['relative_path']}{error_info}")

    # Files that are not tests but could be
    not_tests = [r for r in results if r['category'] == 'not_test']
    if not_tests:
        print(f"\n❓ FILES WITHOUT TEST FUNCTIONS ({len(not_tests)} files):")
        for r in not_tests[:15]:
            print(f"   {r['relative_path']} ({r['lines']} lines)")
        if len(not_tests) > 15:
            print(f"   ... and {len(not_tests) - 15} more")

    # Final stats
    valid_tests = [r for r in results if r['category'] in ['valid', 'valid_class_based']]
    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    print(f"\nTotal files scanned: {len(results)}")
    print(f"Valid test files: {len(valid_tests)}")
    print(f"Total test functions: {total_tests}")
    print(f"Files to move: {len(to_move)}")
    print(f"Files to delete: {len(to_delete)}")
    print(f"Files needing attention: {len(to_fix) + len(not_tests)}")

    # Framework usage
    pytest_count = sum(1 for r in valid_tests if r['uses_pytest'])
    unittest_count = sum(1 for r in valid_tests if r['uses_unittest'])
    django_count = sum(1 for r in valid_tests if r['uses_django_test'])

    print(f"\nFramework usage in valid tests:")
    print(f"  - pytest: {pytest_count} files")
    print(f"  - unittest: {unittest_count} files")
    print(f"  - django.test: {django_count} files")

    # Write detailed report to file
    report_path = ROOT / 'docs' / 'TEST_AUDIT_REPORT.md'
    with open(report_path, 'w') as f:
        f.write("# Test Audit Report\n\n")
        f.write(f"**Generated:** {__import__('datetime').datetime.now().isoformat()}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- Total files: {len(results)}\n")
        f.write(f"- Valid tests: {len(valid_tests)}\n")
        f.write(f"- Test functions: {total_tests}\n")
        f.write(f"- Files to move: {len(to_move)}\n")
        f.write(f"- Files to delete: {len(to_delete)}\n\n")

        f.write("## Files by Category\n\n")
        for cat in category_order:
            if cat in categories:
                items = categories[cat]
                f.write(f"### {cat.upper()} ({len(items)} files)\n\n")
                for r in items:
                    test_info = f" - {r['test_count']} tests" if r['test_count'] > 0 else ""
                    rec = f" → {r['recommendation']}" if r['recommendation'] else ""
                    f.write(f"- `{r['relative_path']}`{test_info}{rec}\n")
                f.write("\n")

        if duplicates:
            f.write("## Duplicate Filenames\n\n")
            for filename, paths in duplicates.items():
                f.write(f"### {filename}\n")
                for p in paths:
                    f.write(f"- `{p}`\n")
                f.write("\n")

    print(f"\n📄 Detailed report written to: {report_path}")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
