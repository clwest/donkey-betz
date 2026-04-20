#!/usr/bin/env python3
"""
Session 136 Part 2: Find and optionally remove ImageHistory records where files no longer exist.

This script helps maintain database integrity by identifying images where:
- Database record exists in ImageHistory
- Physical file has been deleted from disk

Usage:
    python cleanup_orphaned_images.py              # Dry run (list orphaned images)
    python cleanup_orphaned_images.py --delete     # Actually delete orphaned records
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory


def find_orphaned_images(dry_run=True):
    """
    Find images where files don't exist.

    Args:
        dry_run: If True, only list orphaned images. If False, prompt for deletion.

    Returns:
        list: List of orphaned ImageHistory objects
    """
    all_images = ImageHistory.objects.all()
    orphaned = []

    print("=" * 80)
    print(f"🔍 Scanning {all_images.count()} images for missing files...")
    print("=" * 80)
    print()

    for img in all_images:
        if not img.file_exists():
            orphaned.append(img)
            seq_num = img.get_sequential_number()
            print(f"  ⚠️  Orphaned: #{seq_num} (ID: {img.id})")
            print(f"     File: {img.file_path}")
            print(f"     Type: {img.image_type}")
            print(f"     Created: {img.created_at.strftime('%Y-%m-%d %H:%M')}")
            print()

    print("=" * 80)
    print(f"📊 Summary: Found {len(orphaned)} orphaned images out of {all_images.count()} total")
    print("=" * 80)
    print()

    if not dry_run and orphaned:
        print(f"⚠️  WARNING: This will permanently delete {len(orphaned)} database records!")
        print("   (The missing files are already gone, only database records will be removed)")
        print()
        confirm = input(f"Delete {len(orphaned)} orphaned records? Type 'yes' to confirm: ")

        if confirm.lower() == 'yes':
            print()
            print(f"🗑️  Deleting {len(orphaned)} orphaned records...")
            for img in orphaned:
                seq_num = img.get_sequential_number()
                img_id = img.id
                img.delete()
                print(f"   ✅ Deleted: #{seq_num} (ID: {img_id})")

            print()
            print(f"✅ Successfully deleted {len(orphaned)} orphaned records")
        else:
            print()
            print("❌ Deletion cancelled")
    elif not orphaned:
        print("✅ No orphaned images found! All database records have corresponding files.")
    elif dry_run and orphaned:
        print(f"💡 To delete these {len(orphaned)} orphaned records, run:")
        print(f"   python {os.path.basename(__file__)} --delete")

    print()
    return orphaned


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Find and optionally remove ImageHistory records where files no longer exist'
    )
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Actually delete orphaned records (default is dry-run mode)'
    )

    args = parser.parse_args()

    find_orphaned_images(dry_run=not args.delete)
