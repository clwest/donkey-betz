#!/usr/bin/env python3
"""
Analyze External Documentation for Duplicates and Cleaning
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict
import json

def get_file_hash(filepath):
    """Get MD5 hash of file content"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def analyze_docs():
    base_path = Path('/Users/donkeyking/development/unified-donkey-betz/external-project-docs')

    print('📊 EXTERNAL DOCUMENTATION ANALYSIS')
    print('=' * 80)

    # Collect all markdown files
    md_files = list(base_path.rglob('*.md'))
    print(f'\n📁 Total markdown files: {len(md_files)}')

    # Check for duplicates by hash
    hash_to_files = defaultdict(list)
    size_distribution = defaultdict(int)

    for md_file in md_files:
        file_hash = get_file_hash(md_file)
        hash_to_files[file_hash].append(md_file)

        size = md_file.stat().st_size
        size_bucket = f"{size // (1024*100) * 100}KB-{(size // (1024*100) + 1) * 100}KB"
        size_distribution[size_bucket] += 1

    # Find duplicates
    duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}

    print(f'\n🔍 DUPLICATE ANALYSIS:')
    print(f'   Unique files: {len(hash_to_files)}')
    print(f'   Duplicate sets: {len(duplicates)}')

    if duplicates:
        print(f'\n   Duplicate files:')
        for file_hash, files in list(duplicates.items())[:10]:
            print(f'\n   Hash: {file_hash[:16]}...')
            for f in files:
                print(f'      • {f.relative_to(base_path)}')

    # Check for master_context aggregations
    print(f'\n📦 CHECKING FOR AGGREGATED FILES:')
    master_files = list(base_path.rglob('master_context*.md'))
    for mf in master_files:
        size_mb = mf.stat().st_size / (1024*1024)
        lines = sum(1 for _ in open(mf))
        print(f'   • {mf.name}: {size_mb:.1f}MB, {lines:,} lines')

    # Size distribution
    print(f'\n📏 SIZE DISTRIBUTION:')
    for size_range in sorted(size_distribution.keys())[:10]:
        print(f'   {size_range}: {size_distribution[size_range]} files')

    # Directory breakdown
    print(f'\n📂 DIRECTORY BREAKDOWN:')
    dir_counts = defaultdict(int)
    dir_sizes = defaultdict(int)

    for md_file in md_files:
        relative = md_file.relative_to(base_path)
        top_dir = str(relative.parts[0]) if len(relative.parts) > 1 else 'root'
        dir_counts[top_dir] += 1
        dir_sizes[top_dir] += md_file.stat().st_size

    for dir_name in sorted(dir_counts.keys()):
        size_mb = dir_sizes[dir_name] / (1024*1024)
        print(f'   {dir_name}: {dir_counts[dir_name]} files, {size_mb:.1f}MB')

    # Save duplicate report
    report = {
        'total_files': len(md_files),
        'unique_files': len(hash_to_files),
        'duplicate_sets': len(duplicates),
        'duplicates': [
            {
                'hash': h,
                'files': [str(f.relative_to(base_path)) for f in files]
            }
            for h, files in duplicates.items()
        ]
    }

    report_path = base_path / 'DUPLICATE_ANALYSIS.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f'\n📄 Report saved to: {report_path}')

    return report

if __name__ == "__main__":
    analyze_docs()
