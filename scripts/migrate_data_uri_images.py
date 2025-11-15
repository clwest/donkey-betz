#!/usr/bin/env python
"""
Data URI to File Storage Migration Script

This script migrates ImageHistory records with data URI file_paths to actual file storage.

Purpose:
- Convert base64-encoded data URIs to real files in media storage
- Update database records with actual file paths
- Free up database space (119 MB of base64 data)
- Make images visible in all galleries (currently hidden by data URI filters)

Session: 96 - UI Cleanup & Consistency
Date: November 14, 2025

Usage:
    python scripts/migrate_data_uri_images.py [--dry-run]

Options:
    --dry-run    Preview what would be migrated without making changes
"""

import os
import sys
import re
import base64
import argparse
from datetime import datetime

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from content.models import ImageHistory


class DataURIMigrator:
    """Migrates data URI images to file storage"""

    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.migrated = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []

    def print_header(self):
        """Print migration header"""
        print("=" * 70)
        print("DATA URI TO FILE STORAGE MIGRATION")
        print("=" * 70)
        if self.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            print("=" * 70)
        print()

    def analyze_scope(self):
        """Analyze migration scope"""
        print("📊 Analyzing migration scope...")
        print("-" * 70)

        data_uri_images = ImageHistory.objects.filter(file_path__startswith='data:')
        total = data_uri_images.count()

        if total == 0:
            print("✅ No data URI images found - migration not needed!")
            return False

        print(f"   Total data URI images: {total}")

        # Calculate total size
        total_size = sum(len(img.file_path) for img in data_uri_images)
        avg_size = total_size / total if total > 0 else 0

        print(f"   Total database bloat: {total_size/(1024*1024):.1f} MB")
        print(f"   Average image size: {avg_size/1024:.1f} KB")

        # Show date range
        oldest = data_uri_images.order_by('created_at').first()
        newest = data_uri_images.order_by('-created_at').first()
        print(f"   Date range: {oldest.created_at.strftime('%Y-%m-%d')} to {newest.created_at.strftime('%Y-%m-%d')}")

        # Show user distribution
        users = data_uri_images.values('user__username').distinct().count()
        print(f"   Affected users: {users}")

        print()
        return True

    def migrate_image(self, img):
        """Migrate a single image from data URI to file storage"""
        try:
            # Extract base64 data from data URI
            base64_match = re.search(r'base64,(.+)', img.file_path)
            if not base64_match:
                raise ValueError(f"Invalid data URI format - no base64 data found")

            # Decode base64 data
            base64_data = base64_match.group(1)
            image_data = base64.b64decode(base64_data)

            # Generate filename
            # Format: migrated_images/{user_id}/{image_id}.png
            filename = f"migrated_images/{img.user.id}/{img.id}.png"

            if self.dry_run:
                # Dry run - just report what would happen
                size_kb = len(image_data) / 1024
                print(f"   Would migrate: {str(img.id)[:8]}... ({size_kb:.1f} KB) -> {filename}")
                return True

            # Save to file storage
            file_path = default_storage.save(filename, ContentFile(image_data))

            # Verify file was saved
            if not default_storage.exists(file_path):
                raise IOError(f"File was not saved successfully: {file_path}")

            # Get file size for logging
            file_size = default_storage.size(file_path)

            # Update database record
            old_path = img.file_path[:50] + "..." if len(img.file_path) > 50 else img.file_path
            img.file_path = file_path
            img.save(update_fields=['file_path'])

            # Log success
            print(f"   ✅ Migrated: {str(img.id)[:8]}... ({file_size/1024:.1f} KB)")
            print(f"      Old: {old_path}")
            print(f"      New: {file_path}")

            return True

        except Exception as e:
            error_msg = f"Failed to migrate {img.id}: {str(e)}"
            self.errors.append(error_msg)
            print(f"   ❌ {error_msg}")
            return False

    def migrate_all(self):
        """Migrate all data URI images"""
        print("🚀 Starting migration...")
        print("-" * 70)

        data_uri_images = ImageHistory.objects.filter(
            file_path__startswith='data:'
        ).order_by('created_at')

        total = data_uri_images.count()

        for idx, img in enumerate(data_uri_images, 1):
            print(f"\n[{idx}/{total}]")

            if self.migrate_image(img):
                self.migrated += 1
            else:
                self.failed += 1

        print()

    def print_summary(self):
        """Print migration summary"""
        print()
        print("=" * 70)
        print("MIGRATION SUMMARY")
        print("=" * 70)

        if self.dry_run:
            print(f"🔍 Dry Run Complete - No changes made")
            print(f"   Would migrate: {self.migrated} images")
        else:
            print(f"✅ Successfully migrated: {self.migrated} images")

        if self.failed > 0:
            print(f"❌ Failed: {self.failed} images")

        if self.skipped > 0:
            print(f"⏭️  Skipped: {self.skipped} images")

        print()

        if self.failed > 0 and self.errors:
            print("Errors encountered:")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more errors")
            print()

        if not self.dry_run and self.migrated > 0:
            print("Next steps:")
            print("   1. Verify galleries show images: http://localhost:8000/ai-studio/")
            print("   2. Check Image Gallery - should show all migrated images")
            print("   3. Check All Gallery - should show all migrated images")
            print("   4. Check Portfolio - should still show all images")
            print("   5. Test Copy ID button on migrated images")
            print()

        print("=" * 70)

    def verify_migration(self):
        """Verify migration was successful"""
        if self.dry_run:
            return

        print("\n🔍 Verifying migration...")
        print("-" * 70)

        remaining = ImageHistory.objects.filter(file_path__startswith='data:').count()

        if remaining == 0:
            print("   ✅ All data URI images successfully migrated!")
        else:
            print(f"   ⚠️  Warning: {remaining} data URI images still remain")

        total_images = ImageHistory.objects.count()
        file_images = ImageHistory.objects.exclude(file_path__startswith='data:').count()

        print(f"   📊 Total images: {total_images}")
        print(f"   📊 Images with file paths: {file_images} ({file_images/total_images*100:.1f}%)")
        print()

    def run(self):
        """Run the complete migration process"""
        self.print_header()

        # Analyze scope
        if not self.analyze_scope():
            return 0

        # Confirm if not dry run
        if not self.dry_run:
            print("⚠️  This will modify the database and create files in media storage.")
            response = input("Continue? [y/N]: ")
            if response.lower() != 'y':
                print("Migration cancelled.")
                return 1
            print()

        # Migrate all images
        self.migrate_all()

        # Verify migration
        self.verify_migration()

        # Print summary
        self.print_summary()

        return 0 if self.failed == 0 else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Migrate data URI images to file storage'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview migration without making changes'
    )

    args = parser.parse_args()

    migrator = DataURIMigrator(dry_run=args.dry_run)
    exit_code = migrator.run()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
