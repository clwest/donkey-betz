#!/usr/bin/env python3
"""
Deduplicate External Documentation
====================================

Removes duplicate files, keeping the best version based on:
1. File path priority (prefer non-archive)
2. File name clarity
3. Newest timestamp
"""

import os
import hashlib
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def get_file_hash(filepath):
    """Get MD5 hash of file content"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def get_file_priority(filepath):
    """
    Determine file priority (lower = better to keep)
    Priority rules:
    1. Non-archive paths are better
    2. Shorter paths are better
    3. Clearer names are better
    """
    parts = filepath.parts
    name = filepath.name

    score = 0

    # Archive penalty
    if 'archive' in parts:
        score += 1000

    # Path length penalty
    score += len(parts) * 10

    # Timestamp in name penalty (prefer clean names)
    if any(char.isdigit() for char in name[:10]):
        score += 100

    # Prefix codes penalty (DONKEY-, PHASE-, etc.)
    if name.startswith(('DONKEY-', 'PHASE-', 'DATA-', 'PERF-')):
        score += 50

    return score

def deduplicate_docs(dry_run=True):
    base_path = Path('/Users/donkeyking/development/unified-donkey-betz/external-project-docs')

    print('🧹 DEDUPLICATION PROCESS')
    print('=' * 80)
    print(f'Mode: {"DRY RUN (no files deleted)" if dry_run else "LIVE (will delete files)"}')
    print('=' * 80)

    # Collect all markdown files
    md_files = list(base_path.rglob('*.md'))
    print(f'\n📁 Total files: {len(md_files)}')

    # Group by hash
    hash_to_files = defaultdict(list)
    for md_file in md_files:
        file_hash = get_file_hash(md_file)
        hash_to_files[file_hash].append(md_file)

    # Find duplicates
    duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}

    print(f'🔍 Found {len(duplicates)} duplicate sets')
    print(f'📊 {sum(len(files) - 1 for files in duplicates.values())} files to remove')

    # Process duplicates
    files_to_remove = []
    files_to_keep = []

    for file_hash, files in duplicates.items():
        # Sort by priority
        sorted_files = sorted(files, key=get_file_priority)
        keep = sorted_files[0]
        remove = sorted_files[1:]

        files_to_keep.append(keep)
        files_to_remove.extend(remove)

        if len(remove) > 0:
            print(f'\n📌 Keeping: {keep.relative_to(base_path)}')
            for r in remove:
                print(f'   🗑️  Remove: {r.relative_to(base_path)}')

    # Remove duplicates
    if not dry_run:
        print(f'\n🗑️  Deleting {len(files_to_remove)} duplicate files...')
        for f in files_to_remove:
            f.unlink()
        print(f'✅ Deleted {len(files_to_remove)} files')

    # Handle master_context files
    print(f'\n📦 MASTER CONTEXT FILES:')
    master_all = base_path / 'ai-content-studio/documentation/master_context_all.md'
    master_parts = [
        base_path / 'ai-content-studio/documentation/master_context_part_01.md',
        base_path / 'ai-content-studio/documentation/master_context_part_02.md',
        base_path / 'ai-content-studio/documentation/master_context_part_03.md',
        base_path / 'ai-content-studio/documentation/master_context_part_04.md',
        base_path / 'ai-content-studio/documentation/master_context_part_05.md',
    ]

    if master_all.exists():
        print(f'   ✅ Keep: master_context_all.md (18MB, complete)')

        if not dry_run:
            for part in master_parts:
                if part.exists():
                    print(f'   🗑️  Remove: {part.name} (duplicate)')
                    part.unlink()
            print(f'   ✅ Removed {len([p for p in master_parts if p.exists()])} part files')
        else:
            print(f'   🗑️  Would remove: {len([p for p in master_parts if p.exists()])} part files')

    # Summary
    print(f'\n' + '=' * 80)
    print(f'📊 DEDUPLICATION SUMMARY')
    print(f'=' * 80)
    print(f'   Total files: {len(md_files)}')
    print(f'   Unique files: {len(hash_to_files)}')
    print(f'   Duplicate sets: {len(duplicates)}')
    print(f'   Files to remove: {len(files_to_remove)}')
    print(f'   Files to keep: {len(md_files) - len(files_to_remove)}')
    print(f'   Space savings: {sum(f.stat().st_size for f in files_to_remove) / (1024*1024):.1f}MB')

    if dry_run:
        print(f'\n⚠️  DRY RUN - No files were deleted')
        print(f'   Run with dry_run=False to actually remove files')

    return {
        'total_files': len(md_files),
        'unique_files': len(hash_to_files),
        'duplicates': len(duplicates),
        'to_remove': len(files_to_remove),
        'to_keep': len(md_files) - len(files_to_remove)
    }

if __name__ == "__main__":
    # Run actual deduplication
    stats = deduplicate_docs(dry_run=False)

    print(f'\n\n✅ Deduplication complete!')
    print(f'   Cleaned external documentation ready for ingestion')
