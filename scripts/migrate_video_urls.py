#!/usr/bin/env python
"""
Video URL Migration Script

This script migrates VideoHistory records with external CDN URLs to local file storage.

Purpose:
- Download videos from expiring CDN URLs (CloudFront, Google Storage)
- Save to local media storage
- Update database with local file paths
- Prevent 401 Unauthorized errors from expired JWT tokens

Session: 96 - UI Cleanup & Consistency
Date: November 14, 2025

Usage:
    python scripts/migrate_video_urls.py [--dry-run]

Options:
    --dry-run    Preview what would be migrated without making changes
"""

import os
import sys
import argparse
import requests
from datetime import datetime
from urllib.parse import urlparse

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from content.models import VideoHistory


class VideoURLMigrator:
    """Migrates external video URLs to local file storage"""

    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.migrated = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []

    def print_header(self):
        """Print migration header"""
        print("=" * 70)
        print("VIDEO URL TO FILE STORAGE MIGRATION")
        print("=" * 70)
        if self.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            print("=" * 70)
        print()

    def is_external_url(self, url):
        """Check if URL is an external CDN URL that should be migrated"""
        if not url:
            return False

        # Check for external CDN domains
        external_domains = [
            'cloudfront.net',
            'storage.googleapis.com',
            'storage.cloud.google.com',
            'amazonaws.com',
            'runwayml.com'
        ]

        return any(domain in url for domain in external_domains)

    def analyze_scope(self):
        """Analyze migration scope"""
        print("📊 Analyzing migration scope...")
        print("-" * 70)

        all_videos = VideoHistory.objects.all()
        total = all_videos.count()

        if total == 0:
            print("✅ No videos found - migration not needed!")
            return False

        # Count external URLs
        external_count = sum(1 for v in all_videos if self.is_external_url(v.video_url))
        local_count = total - external_count

        print(f"   Total videos: {total}")
        print(f"   External CDN URLs: {external_count}")
        print(f"   Local file paths: {local_count}")

        if external_count == 0:
            print("\n✅ All videos already using local storage!")
            return False

        # Show date range
        if external_count > 0:
            external_videos = [v for v in all_videos if self.is_external_url(v.video_url)]
            external_videos.sort(key=lambda v: v.created_at)
            oldest = external_videos[0]
            newest = external_videos[-1]
            print(f"   Date range: {oldest.created_at.strftime('%Y-%m-%d')} to {newest.created_at.strftime('%Y-%m-%d')}")

        # Show user distribution
        users = VideoHistory.objects.values('user__username').distinct().count()
        print(f"   Affected users: {users}")

        # Estimate download size
        print(f"\n   ⚠️  This will download {external_count} videos from CDN")
        print(f"   ⏱️  Estimated time: {external_count * 10} seconds (~10s per video)")

        print()
        return True

    def download_video(self, url, timeout=60):
        """Download video from URL"""
        try:
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()

            # Read content
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    content += chunk

            return content
        except requests.exceptions.RequestException as e:
            raise Exception(f"Download failed: {str(e)}")

    def migrate_video(self, video):
        """Migrate a single video from external URL to file storage"""
        try:
            # Skip if already local
            if not self.is_external_url(video.video_url):
                self.skipped += 1
                return True

            # Extract filename from URL or use ID
            parsed = urlparse(video.video_url)
            filename_from_url = os.path.basename(parsed.path)
            if not filename_from_url or filename_from_url == '':
                filename_from_url = f"{video.id}.mp4"

            # Generate local filename
            # Format: migrated_videos/{user_id}/{filename}
            local_filename = f"migrated_videos/{video.user.id}/{filename_from_url}"

            if self.dry_run:
                # Dry run - just report what would happen
                print(f"   Would download: {str(video.id)[:8]}...")
                print(f"      From: {video.video_url[:80]}...")
                print(f"      To: {local_filename}")
                return True

            # Download video
            print(f"   Downloading: {str(video.id)[:8]}...")
            print(f"      URL: {video.video_url[:80]}...")

            video_data = self.download_video(video.video_url)

            # Save to file storage
            file_path = default_storage.save(local_filename, ContentFile(video_data))

            # Verify file was saved
            if not default_storage.exists(file_path):
                raise IOError(f"File was not saved successfully: {file_path}")

            # Get file size for logging
            file_size = default_storage.size(file_path)

            # Update database record
            video.video_url = default_storage.url(file_path)
            video.save(update_fields=['video_url'])

            # Log success
            print(f"   ✅ Migrated: {str(video.id)[:8]}... ({file_size/(1024*1024):.1f} MB)")
            print(f"      Saved to: {file_path}")

            return True

        except Exception as e:
            error_msg = f"Failed to migrate {video.id}: {str(e)}"
            self.errors.append(error_msg)
            print(f"   ❌ {error_msg}")
            return False

    def migrate_all(self):
        """Migrate all external video URLs"""
        print("🚀 Starting migration...")
        print("-" * 70)

        all_videos = VideoHistory.objects.all().order_by('created_at')
        external_videos = [v for v in all_videos if self.is_external_url(v.video_url)]

        total = len(external_videos)

        if total == 0:
            print("No external videos to migrate.")
            return

        for idx, video in enumerate(external_videos, 1):
            print(f"\n[{idx}/{total}]")

            if self.migrate_video(video):
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
            print(f"   Would migrate: {self.migrated} videos")
        else:
            print(f"✅ Successfully migrated: {self.migrated} videos")

        if self.failed > 0:
            print(f"❌ Failed: {self.failed} videos")

        if self.skipped > 0:
            print(f"⏭️  Skipped (already local): {self.skipped} videos")

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
            print("   1. Verify videos play in Portfolio: http://localhost:8000/ai-studio/")
            print("   2. Check Video Gallery - all videos should play")
            print("   3. Check All Gallery - videos should be visible")
            print("   4. No more 401 Unauthorized errors!")
            print()

        print("=" * 70)

    def verify_migration(self):
        """Verify migration was successful"""
        if self.dry_run:
            return

        print("\n🔍 Verifying migration...")
        print("-" * 70)

        all_videos = VideoHistory.objects.all()
        external_remaining = sum(1 for v in all_videos if self.is_external_url(v.video_url))

        if external_remaining == 0:
            print("   ✅ All videos successfully migrated to local storage!")
        else:
            print(f"   ⚠️  Warning: {external_remaining} videos still have external URLs")

        total_videos = all_videos.count()
        local_videos = total_videos - external_remaining

        print(f"   📊 Total videos: {total_videos}")
        print(f"   📊 Videos with local paths: {local_videos} ({local_videos/total_videos*100:.1f}%)")
        print()

    def run(self):
        """Run the complete migration process"""
        self.print_header()

        # Analyze scope
        if not self.analyze_scope():
            return 0

        # Confirm if not dry run
        if not self.dry_run:
            print("⚠️  This will download videos from CDN and modify the database.")
            print("⚠️  Videos with expired tokens may fail to download.")
            response = input("Continue? [y/N]: ")
            if response.lower() != 'y':
                print("Migration cancelled.")
                return 1
            print()

        # Migrate all videos
        self.migrate_all()

        # Verify migration
        self.verify_migration()

        # Print summary
        self.print_summary()

        return 0 if self.failed == 0 else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Migrate external video URLs to local file storage'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview migration without making changes'
    )

    args = parser.parse_args()

    migrator = VideoURLMigrator(dry_run=args.dry_run)
    exit_code = migrator.run()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
