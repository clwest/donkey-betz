"""
Session 800: Migrate existing images to Cloudinary

This command uploads all locally-stored images to Cloudinary and updates
their file_path to use Cloudinary URLs directly. This eliminates the need
to serve media files through Railway, drastically reducing egress costs.

Usage:
    python manage.py migrate_images_to_cloudinary
    python manage.py migrate_images_to_cloudinary --batch-size=100
    python manage.py migrate_images_to_cloudinary --dry-run
    python manage.py migrate_images_to_cloudinary --skip-existing

Options:
    --batch-size: Number of images to process per batch (default: 50)
    --dry-run: Show what would be migrated without actually uploading
    --skip-existing: Skip images that already have Cloudinary URLs
    --user: Only migrate images for a specific username
"""

import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate locally-stored images to Cloudinary for reduced egress costs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of images to process per batch (default: 50)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without uploading'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            default=True,
            help='Skip images that already have Cloudinary URLs (default: True)'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Only migrate images for a specific username'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of images to migrate'
        )

    def handle(self, *args, **options):
        from content.models import ImageHistory
        from content.cloud_storage import CloudStorageManager
        from django.contrib.auth import get_user_model

        User = get_user_model()

        batch_size = options['batch_size']
        dry_run = options['dry_run']
        skip_existing = options['skip_existing']
        username = options.get('user')
        limit = options.get('limit')

        # Check Cloudinary configuration
        is_configured, message = CloudStorageManager.is_configured()
        if not is_configured and not dry_run:
            self.stderr.write(self.style.ERROR(f'Cloudinary not configured: {message}'))
            return

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Session 800: Cloudinary Image Migration'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Build query
        queryset = ImageHistory.objects.all()

        if username:
            try:
                user = User.objects.get(username=username)
                queryset = queryset.filter(user=user)
                self.stdout.write(f'Filtering to user: {username}')
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f'User not found: {username}'))
                return

        if skip_existing:
            # Skip images that already have Cloudinary URLs
            queryset = queryset.exclude(file_path__startswith='http')
            # Also skip data URIs
            queryset = queryset.exclude(file_path__startswith='data:')

        total_count = queryset.count()
        self.stdout.write(f'Found {total_count} images to migrate')

        if limit:
            queryset = queryset[:limit]
            self.stdout.write(f'Limited to {limit} images')

        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('No images to migrate!'))
            return

        # Stats
        stats = {
            'uploaded': 0,
            'skipped': 0,
            'failed': 0,
            'not_found': 0,
        }

        # Process in batches
        processed = 0
        images = list(queryset.order_by('created_at')[:batch_size])

        while images:
            for image in images:
                processed += 1

                # Get local file path
                if image.file_path.startswith('http') or image.file_path.startswith('data:'):
                    stats['skipped'] += 1
                    continue

                # Construct full local path
                try:
                    local_path = default_storage.path(image.file_path)
                except NotImplementedError:
                    # S3 or other storage that doesn't support path()
                    local_path = os.path.join(settings.MEDIA_ROOT, image.file_path)

                if not os.path.exists(local_path):
                    self.stdout.write(
                        self.style.WARNING(f'[{processed}/{total_count}] File not found: {image.file_path}')
                    )
                    stats['not_found'] += 1
                    continue

                # Generate public_id for Cloudinary
                # Use image UUID to ensure uniqueness
                public_id = f"img_{image.id}"
                folder = f"ai-content-studio/migrated/{image.user.username}"

                if dry_run:
                    self.stdout.write(
                        f'[{processed}/{total_count}] Would upload: {image.file_path} -> {folder}/{public_id}'
                    )
                    stats['uploaded'] += 1
                    continue

                # Upload to Cloudinary
                result = CloudStorageManager.upload_image(
                    file_path=local_path,
                    public_id=public_id,
                    folder=folder
                )

                if result['success']:
                    # Update the file_path to Cloudinary URL
                    old_path = image.file_path
                    image.file_path = result['url']
                    image.save(update_fields=['file_path'])

                    stats['uploaded'] += 1

                    if processed % 10 == 0 or processed == total_count:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'[{processed}/{total_count}] Migrated: {old_path[:40]}... -> Cloudinary'
                            )
                        )
                else:
                    stats['failed'] += 1
                    self.stdout.write(
                        self.style.ERROR(f'[{processed}/{total_count}] Failed: {image.file_path} - {result["error"]}')
                    )

            # Get next batch
            if limit and processed >= limit:
                break
            last_id = images[-1].id
            images = list(
                queryset.filter(id__gt=last_id).order_by('created_at')[:batch_size]
            )

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Migration Summary'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f"Uploaded to Cloudinary: {stats['uploaded']}")
        self.stdout.write(f"Skipped (already cloud): {stats['skipped']}")
        self.stdout.write(f"Not found locally: {stats['not_found']}")
        self.stdout.write(f"Failed: {stats['failed']}")

        if dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('This was a DRY RUN. Run without --dry-run to apply changes.'))
        else:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Migration complete! Images now served from Cloudinary.'))
