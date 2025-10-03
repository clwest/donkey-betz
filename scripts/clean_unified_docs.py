#!/usr/bin/env python3
"""
Unified Donkey Betz Documentation Cleaner
ONLY processes files in /unified-donkey-betz/ - does NOT touch other projects
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

# CRITICAL: Only scan unified-donkey-betz directory
PROJECT_ROOT = Path('/Users/donkeyking/development/unified-donkey-betz')
OUTPUT_DIR = PROJECT_ROOT / 'scripts/doc_analysis'

# DO NOT SCAN these directories
EXCLUDE_DIRS = [
    'node_modules',
    'venv',
    '.venv',
    'venv_ml',
    '__pycache__',
    '.git',
    'dist',
    'build',
    'cache',
    'logs',
    'media',
    'static',
    'mlb-pitch-data',
    'nba-game-data',
    'nhl-game-0data',
    '.claude'
]

# DO NOT TOUCH this directory - it's already organized
PROTECTED_DIR = PROJECT_ROOT / 'docs'

def get_file_hash(content):
    """Generate MD5 hash for duplicate detection"""
    return hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()

def extract_metadata(content, file_path):
    """Extract metadata from markdown"""
    metadata = {
        'title': None,
        'category': 'general',
        'tags': []
    }

    # Extract title from first header
    header_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if header_match:
        metadata['title'] = header_match.group(1).strip()

    # Categorize by directory structure
    rel_path = str(file_path.relative_to(PROJECT_ROOT)).lower()

    if 'agents' in rel_path:
        metadata['category'] = 'agents'
    elif 'core' in rel_path:
        metadata['category'] = 'core'
    elif 'intelligence' in rel_path:
        metadata['category'] = 'intelligence'
    elif 'ml' in rel_path or 'ai' in rel_path:
        metadata['category'] = 'ml'
    elif 'sports' in rel_path:
        metadata['category'] = 'sports'
    elif 'content' in rel_path:
        metadata['category'] = 'content'
    elif 'revenue' in rel_path:
        metadata['category'] = 'revenue'
    elif 'scripts' in rel_path:
        metadata['category'] = 'scripts'
    elif 'tests' in rel_path or 'test_' in file_path.name:
        metadata['category'] = 'tests'
    elif 'config' in rel_path:
        metadata['category'] = 'config'
    elif file_path.name.upper() == 'README.md':
        metadata['category'] = 'readme'

    return metadata

def scan_unified_docs():
    """Scan ONLY unified-donkey-betz markdown files"""
    print("🔍 Scanning unified-donkey-betz documentation...")
    print(f"   Root: {PROJECT_ROOT}")
    print(f"   Protected: {PROTECTED_DIR} (will NOT be scanned)")

    inventory = []
    stats = defaultdict(int)

    # Find all .md files in unified-donkey-betz
    for md_file in PROJECT_ROOT.rglob('*.md'):
        # Skip excluded directories
        if any(excl in str(md_file) for excl in EXCLUDE_DIRS):
            stats['excluded_dirs'] += 1
            continue

        # SKIP the protected /docs/ directory
        if str(md_file).startswith(str(PROTECTED_DIR)):
            stats['protected'] += 1
            continue

        try:
            with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            file_stat = md_file.stat()
            metadata = extract_metadata(content, md_file)

            doc_info = {
                'path': str(md_file),
                'relative_path': str(md_file.relative_to(PROJECT_ROOT)),
                'filename': md_file.name,
                'size_bytes': len(content),
                'size_kb': round(len(content) / 1024, 2),
                'hash': get_file_hash(content),
                'preview': content[:500].strip(),
                'word_count': len(content.split()),
                'line_count': len(content.split('\n')),
                'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                'title': metadata['title'] or md_file.stem,
                'category': metadata['category']
            }

            inventory.append(doc_info)
            stats['total'] += 1
            stats[f"category_{metadata['category']}"] += 1

        except Exception as e:
            print(f"   ⚠️  Error: {md_file}: {e}")
            stats['errors'] += 1

    # Generate summary
    summary = {
        'scan_date': datetime.now().isoformat(),
        'project': 'unified-donkey-betz',
        'project_root': str(PROJECT_ROOT),
        'total_files': stats['total'],
        'protected_files': stats['protected'],
        'excluded_files': stats['excluded_dirs'],
        'errors': stats['errors'],
        'total_size_mb': round(sum(doc['size_bytes'] for doc in inventory) / 1024 / 1024, 2),
        'by_category': {k.replace('category_', ''): v for k, v in stats.items() if k.startswith('category_')}
    }

    return inventory, summary

def find_duplicates(inventory):
    """Find duplicate files by hash"""
    print("\n🔍 Finding duplicates...")

    hash_map = defaultdict(list)
    for doc in inventory:
        hash_map[doc['hash']].append(doc)

    duplicates = []
    for file_hash, docs in hash_map.items():
        if len(docs) > 1:
            duplicates.append({
                'hash': file_hash,
                'count': len(docs),
                'files': [{'path': d['path'], 'size': d['size_kb']} for d in docs],
                'potential_savings_kb': sum(d['size_kb'] for d in docs[1:])
            })

    return sorted(duplicates, key=lambda x: x['potential_savings_kb'], reverse=True)

def organize_by_category(inventory):
    """Organize files by category"""
    organized = defaultdict(list)

    for doc in inventory:
        organized[doc['category']].append(doc)

    return dict(organized)

def generate_reports(inventory, summary, duplicates, organized):
    """Generate comprehensive reports"""
    print("\n📊 Generating reports...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Full inventory
    inventory_file = OUTPUT_DIR / 'unified_inventory.json'
    with open(inventory_file, 'w') as f:
        json.dump(inventory, f, indent=2)
    print(f"   ✅ Inventory: {inventory_file}")

    # 2. Summary
    summary_file = OUTPUT_DIR / 'unified_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"   ✅ Summary: {summary_file}")

    # 3. Duplicates
    duplicates_file = OUTPUT_DIR / 'unified_duplicates.json'
    with open(duplicates_file, 'w') as f:
        json.dump(duplicates, f, indent=2)
    print(f"   ✅ Duplicates: {duplicates_file}")

    # 4. Organized by category
    organized_file = OUTPUT_DIR / 'unified_organized.json'
    with open(organized_file, 'w') as f:
        json.dump(organized, f, indent=2)
    print(f"   ✅ Organized: {organized_file}")

    # 5. Markdown report
    report_file = OUTPUT_DIR / 'UNIFIED_DOCS_REPORT.md'
    with open(report_file, 'w') as f:
        f.write("# Unified Donkey Betz Documentation Analysis\n\n")
        f.write(f"**Project**: unified-donkey-betz ONLY\n")
        f.write(f"**Scan Date**: {summary['scan_date']}\n")
        f.write(f"**Root**: `{summary['project_root']}`\n\n")

        f.write("## ⚠️ Important Notes\n\n")
        f.write(f"- **Protected**: `/docs/` directory NOT scanned ({summary['protected_files']} files protected)\n")
        f.write(f"- **Excluded**: {summary['excluded_files']} files in venv/node_modules/etc\n")
        f.write(f"- **Scope**: ONLY unified-donkey-betz project files\n\n")

        f.write("## 📊 Summary Statistics\n\n")
        f.write(f"- **Total Files Scanned**: {summary['total_files']:,}\n")
        f.write(f"- **Total Size**: {summary['total_size_mb']:.2f} MB\n")
        f.write(f"- **Duplicate Groups**: {len(duplicates)}\n")
        f.write(f"- **Potential Savings**: {sum(d['potential_savings_kb'] for d in duplicates)/1024:.2f} MB\n\n")

        f.write("## 📁 By Category\n\n")
        for category, count in sorted(summary['by_category'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{category}**: {count:,} files\n")

        f.write("\n## 🔄 Top Duplicates\n\n")
        for idx, dup in enumerate(duplicates[:10], 1):
            f.write(f"### {idx}. {dup['count']} copies (save {dup['potential_savings_kb']:.2f} KB)\n")
            for file_info in dup['files']:
                f.write(f"- `{file_info['path']}`\n")
            f.write("\n")

        f.write("\n## 📚 File Organization\n\n")
        for category, docs in sorted(organized.items(), key=lambda x: len(x[1]), reverse=True):
            f.write(f"\n### {category.upper()} ({len(docs)} files)\n\n")
            for doc in docs[:5]:  # Show first 5
                f.write(f"- `{doc['relative_path']}` - {doc['title']}\n")
            if len(docs) > 5:
                f.write(f"- *... and {len(docs) - 5} more*\n")

    print(f"   ✅ Report: {report_file}")

    return {
        'inventory': str(inventory_file),
        'summary': str(summary_file),
        'duplicates': str(duplicates_file),
        'organized': str(organized_file),
        'report': str(report_file)
    }

def main():
    """Main execution"""
    print("=" * 70)
    print("📚 Unified Donkey Betz Documentation Analysis")
    print("=" * 70)
    print("\n⚠️  PROTECTION ENABLED:")
    print(f"   ✅ /docs/ directory will NOT be scanned or modified")
    print(f"   ✅ Only unified-donkey-betz files will be processed")
    print(f"   ✅ Other projects (ai-content-studio, dbao-studio, etc.) excluded\n")

    # 1. Scan unified-donkey-betz files only
    inventory, summary = scan_unified_docs()

    # 2. Find duplicates
    duplicates = find_duplicates(inventory)

    # 3. Organize by category
    organized = organize_by_category(inventory)

    # 4. Generate reports
    reports = generate_reports(inventory, summary, duplicates, organized)

    # 5. Print summary
    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE - /docs/ PROTECTED")
    print("=" * 70)
    print(f"\n📊 Unified Donkey Betz Documentation:")
    print(f"   • Files Found: {summary['total_files']:,}")
    print(f"   • Total Size: {summary['total_size_mb']:.2f} MB")
    print(f"   • Protected (/docs/): {summary['protected_files']} files (untouched)")
    print(f"   • Excluded (venv/etc): {summary['excluded_files']} files")
    print(f"   • Duplicates: {len(duplicates)} groups")
    print(f"   • Potential Savings: {sum(d['potential_savings_kb'] for d in duplicates)/1024:.2f} MB")

    print(f"\n📁 By Category:")
    for category, count in sorted(summary['by_category'].items(), key=lambda x: x[1], reverse=True):
        print(f"   • {category}: {count:,} files")

    print(f"\n📄 Reports saved to:")
    for report_type, path in reports.items():
        print(f"   • {report_type}: {path}")

    print(f"\n🚀 Next Steps:")
    print(f"   1. Review: {reports['report']}")
    print(f"   2. Upload to database with project='unified-donkey-betz'")
    print(f"   3. /docs/ remains completely untouched ✅")

if __name__ == "__main__":
    main()
