#!/usr/bin/env python3
"""
Session 136 Part 2: Migrate existing images to Cloudinary.

This script uploads all existing images from local storage to Cloudinary for
permanent cloud storage, preventing future file loss issues.

Features:
    - Finds all images without cloud URLs
    - Skips images where local files are missing
    - Uploads to Cloudinary with proper public_id format
    - Updates database with cloud URLs
    - Provides detailed progress reporting

Usage:
    python migrate_images_to_cloud.py

Requirements:
    - Cloudinary account (free tier works fine)
    - Environment variables set: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory
from content.cloud_storage import CloudStorageManager


def migrate_images():
    """
    Upload all existing images to Cloudinary.

    Finds all ImageHistory records that don't have a cloud_url set and attempts
    to upload their files to Cloudinary for permanent storage.
    """
    print("=" * 80)
    print("☁️  Migrating Images to Cloudinary")
    print("=" * 80)
    print()

    # Check if Cloudinary is configured
    configured, message = CloudStorageManager.is_configured()
    if not configured:
        print(f"❌ Cloudinary not configured: {message}")
        print()
        print("Please set the following environment variables in .env:")
        print("  - CLOUDINARY_CLOUD_NAME")
        print("  - CLOUDINARY_API_KEY")
        print("  - CLOUDINARY_API_SECRET")
        print()
        print("Get your credentials from https://cloudinary.com/ (free account)")
        return

    print(f"✅ Cloudinary configured: {message}")
    print()

    # Find images without cloud URLs
    images = ImageHistory.objects.filter(cloud_url__isnull=True)
    total = images.count()

    if total == 0:
        print("✅ All images already migrated to Cloudinary!")
        print()
        return

    print(f"📊 Found {total} images to migrate")
    print()

    success_count = 0
    fail_count = 0
    skip_count = 0

    for i, img in enumerate(images, 1):
        seq_num = img.get_sequential_number()
        print(f"[{i}/{total}] Processing image #{seq_num} (ID: {img.id})...")

        # Check if file exists
        if not img.file_exists():
            print(f"  ⏭️  Skipping - file missing: {img.file_path}")
            skip_count += 1
            continue

        # Get absolute file path
        file_path = img.get_absolute_file_path()
        if not file_path:
            print(f"  ⏭️  Skipping - no valid file path")
            skip_count += 1
            continue

        # Upload to Cloudinary
        print(f"  📤 Uploading to Cloudinary...")
        result = CloudStorageManager.upload_image(
            file_path=file_path,
            public_id=f"image_{img.id}",
            folder="ai-content-studio/images"
        )

        if result['success']:
            # Update database with cloud URL
            img.cloud_url = result['url']
            img.save(update_fields=['cloud_url'])
            print(f"  ✅ Success!")
            print(f"     URL: {result['url']}")
            success_count += 1
        else:
            print(f"  ❌ Failed: {result['error']}")
            fail_count += 1

        print()

    # Summary
    print("=" * 80)
    print("📊 Migration Summary")
    print("=" * 80)
    print(f"  Total images:        {total}")
    print(f"  ✅ Successfully uploaded: {success_count}")
    print(f"  ❌ Failed:           {fail_count}")
    print(f"  ⏭️  Skipped (no file): {skip_count}")
    print("=" * 80)
    print()

    if success_count > 0:
        print(f"🎉 Successfully migrated {success_count} images to Cloudinary!")
        print()
        print("Next steps:")
        print("  1. Verify images are accessible in your Cloudinary dashboard")
        print("  2. Test image display in the application")
        print("  3. Optionally run cleanup_orphaned_images.py to remove local-only records")
    elif skip_count == total:
        print("⚠️  No images could be uploaded (all files missing)")
        print()
        print("Consider running cleanup_orphaned_images.py --delete to remove")
        print("database records for missing files.")
    else:
        print(f"⚠️  Only {success_count} of {total - skip_count} uploadable images succeeded")

    print()


if __name__ == "__main__":
    migrate_images()
