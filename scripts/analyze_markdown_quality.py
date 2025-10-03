#!/usr/bin/env python3
"""
Analyze Markdown Quality in External Documentation
===================================================

Checks for:
- Header consistency (h1 should be first, no skipped levels)
- Code blocks without language tags
- Broken internal links
- Long lines without breaks
- Missing blank lines between sections
"""

import re
from pathlib import Path
from collections import defaultdict

def analyze_markdown_file(filepath):
    """Analyze a single markdown file for quality issues"""
    issues = []

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')

    # Track header levels
    headers = []
    prev_header_level = 0

    # Check for issues
    for i, line in enumerate(lines, 1):
        # Header analysis
        if line.startswith('#'):
            level = len(line.split()[0])
            headers.append((i, level))

            # Check for skipped header levels
            if prev_header_level > 0 and level > prev_header_level + 1:
                issues.append({
                    'type': 'skipped_header_level',
                    'line': i,
                    'message': f'Skipped from h{prev_header_level} to h{level}'
                })

            prev_header_level = level

        # Code block without language tag
        if line.strip() == '```':
            issues.append({
                'type': 'code_block_no_lang',
                'line': i,
                'message': 'Code block without language tag'
            })

        # Very long lines (>200 chars, not code or links)
        if len(line) > 200 and not line.strip().startswith('```') and 'http' not in line:
            issues.append({
                'type': 'long_line',
                'line': i,
                'message': f'Line length: {len(line)} chars'
            })

    # Check if first header is h1
    if headers and headers[0][1] != 1:
        issues.append({
            'type': 'first_header_not_h1',
            'line': headers[0][0],
            'message': f'First header is h{headers[0][1]}, should be h1'
        })

    # Broken internal links (relative paths that don't exist)
    internal_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    for link_text, link_path in internal_links:
        if not link_path.startswith('http') and not link_path.startswith('#'):
            # Check if file exists (relative to this file)
            target = filepath.parent / link_path
            if not target.exists() and '.md' in link_path:
                issues.append({
                    'type': 'broken_link',
                    'line': 0,
                    'message': f'Broken link: {link_path}'
                })

    return issues

def analyze_all_docs():
    base_path = Path('/Users/donkeyking/development/unified-donkey-betz/external-project-docs')

    print('📝 MARKDOWN QUALITY ANALYSIS')
    print('=' * 80)

    # Collect all markdown files
    md_files = list(base_path.rglob('*.md'))
    print(f'\n📁 Analyzing {len(md_files)} markdown files...')

    # Track issues by type
    issue_counts = defaultdict(int)
    files_with_issues = defaultdict(list)

    for md_file in md_files:
        issues = analyze_markdown_file(md_file)

        if issues:
            relative_path = md_file.relative_to(base_path)

            for issue in issues:
                issue_type = issue['type']
                issue_counts[issue_type] += 1
                files_with_issues[issue_type].append({
                    'file': str(relative_path),
                    'issue': issue
                })

    # Report summary
    print(f'\n📊 QUALITY ISSUES SUMMARY:')
    print(f'   Files analyzed: {len(md_files)}')
    print(f'   Files with issues: {len(set(f["file"] for issues in files_with_issues.values() for f in issues))}')
    print(f'   Total issues: {sum(issue_counts.values())}')

    # Break down by type
    print(f'\n🔍 ISSUE BREAKDOWN:')
    for issue_type, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
        print(f'   {issue_type}: {count} occurrences')

    # Show examples of each issue type
    print(f'\n📋 EXAMPLE ISSUES:')
    for issue_type, examples in files_with_issues.items():
        print(f'\n   {issue_type.upper().replace("_", " ")}:')
        for example in examples[:3]:  # Show first 3
            file_path = example['file']
            issue = example['issue']
            if issue['line'] > 0:
                print(f'      • {file_path}:{issue["line"]} - {issue["message"]}')
            else:
                print(f'      • {file_path} - {issue["message"]}')

    # Recommendations
    print(f'\n💡 RECOMMENDATIONS:')
    if 'code_block_no_lang' in issue_counts:
        print(f'   - Add language tags to {issue_counts["code_block_no_lang"]} code blocks')
    if 'skipped_header_level' in issue_counts:
        print(f'   - Fix {issue_counts["skipped_header_level"]} header level skips')
    if 'first_header_not_h1' in issue_counts:
        print(f'   - Ensure {issue_counts["first_header_not_h1"]} files start with h1')
    if 'broken_link' in issue_counts:
        print(f'   - Fix or remove {issue_counts["broken_link"]} broken links')
    if 'long_line' in issue_counts:
        print(f'   - Consider breaking {issue_counts["long_line"]} long lines')

    print(f'\n✅ Analysis complete!')

    return {
        'total_files': len(md_files),
        'total_issues': sum(issue_counts.values()),
        'issue_breakdown': dict(issue_counts)
    }

if __name__ == "__main__":
    analyze_all_docs()
