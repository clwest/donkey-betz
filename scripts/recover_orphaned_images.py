#!/usr/bin/env python
"""
Recovery script for orphaned image files.

This script finds image files on disk that are NOT in the database and creates
ImageHistory records for them. This is useful after a database restore that
lost recent data while the files remained on disk.

Usage:
    python manage.py shell < scripts/recover_orphaned_images.py

Or:
    python scripts/recover_orphaned_images.py

Created: Nov 30, 2025 (Session 294 - Data Recovery)
"""

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add Django project to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.conf import settings
from django.utils import timezone
from content.models import ImageHistory
from core.models import UnifiedUser
from PIL import Image as PILImage


def get_file_creation_time(filepath):
    """Get file creation/modification time as timezone-aware datetime."""
    stat = os.stat(filepath)
    # Use modification time as creation time
    timestamp = stat.st_mtime
    return timezone.make_aware(datetime.fromtimestamp(timestamp))


def get_image_dimensions(filepath):
    """Get image width and height."""
    try:
        with PILImage.open(filepath) as img:
            return img.width, img.height
    except Exception:
        return None, None


def detect_image_type(filename):
    """Detect image type from filename."""
    filename_lower = filename.lower()
    if 'upscaled' in filename_lower:
        return 'upscaled'
    elif 'inpainted' in filename_lower:
        return 'inpainted'
    elif 'erased' in filename_lower:
        return 'erased'
    elif 'outpaint' in filename_lower:
        return 'outpainted'
    elif 'variation' in filename_lower:
        return 'variation'
    elif 'structure_control' in filename_lower:
        return 'structure_control'
    elif 'search_replace' in filename_lower:
        return 'search_replace'
    elif 'no_bg' in filename_lower or 'removed_bg' in filename_lower or 'background_removed' in filename_lower:
        return 'background_removed'
    elif 'recolored' in filename_lower:
        return 'recolored'
    elif 'sketch_control' in filename_lower:
        return 'sketch_control'
    elif 'generated' in filename_lower:
        return 'generated'
    else:
        return 'generated'


def get_user_from_path(filepath, admin_user):
    """Determine user from filepath."""
    # Check if path contains a UUID (user folder)
    parts = filepath.split('/')
    for part in parts:
        try:
            user_uuid = uuid.UUID(part)
            user = UnifiedUser.objects.filter(id=user_uuid).first()
            if user:
                return user
        except ValueError:
            continue

    # Check if path contains 'admin'
    if '/admin/' in filepath:
        return admin_user

    # Check if path contains 'anonymous'
    if '/anonymous/' in filepath:
        return admin_user  # Use admin for anonymous images

    # Default to admin
    return admin_user


def recover_orphaned_images(dry_run=True):
    """Find and recover orphaned images."""
    media_root = Path(settings.MEDIA_ROOT)
    images_dir = media_root / 'generated_images'

    if not images_dir.exists():
        print(f"Images directory not found: {images_dir}")
        return

    # Get admin user
    admin_user = UnifiedUser.objects.filter(username='admin').first()
    if not admin_user:
        print("Admin user not found!")
        return

    print(f"Admin user ID: {admin_user.id}")
    print(f"Scanning: {images_dir}")
    print(f"Dry run: {dry_run}")
    print("-" * 60)

    # Get all existing file_paths from DB
    existing_paths = set(ImageHistory.objects.values_list('file_path', flat=True))
    print(f"Found {len(existing_paths)} images in database")

    # Find all image files
    all_files = list(images_dir.rglob('*.png')) + list(images_dir.rglob('*.jpg')) + list(images_dir.rglob('*.jpeg'))
    print(f"Found {len(all_files)} image files on disk")

    orphaned = []
    for filepath in all_files:
        # Get relative path from media root
        rel_path = str(filepath.relative_to(media_root))

        # Check if this file is in the database
        if rel_path not in existing_paths:
            orphaned.append((filepath, rel_path))

    print(f"Found {len(orphaned)} orphaned images (on disk but not in DB)")
    print("-" * 60)

    if not orphaned:
        print("No orphaned images to recover!")
        return

    # Cutoff date - only recover files newer than Nov 8, 2025
    cutoff = timezone.make_aware(datetime(2025, 11, 8, 0, 0, 0))

    recovered = 0
    skipped = 0

    for filepath, rel_path in orphaned:
        created_at = get_file_creation_time(filepath)

        # Skip older files (they might have been deleted intentionally)
        if created_at < cutoff:
            skipped += 1
            continue

        width, height = get_image_dimensions(filepath)
        image_type = detect_image_type(filepath.name)
        user = get_user_from_path(rel_path, admin_user)
        file_size = os.path.getsize(filepath)

        print(f"Recovering: {rel_path}")
        print(f"  Created: {created_at}")
        print(f"  Type: {image_type}")
        print(f"  User: {user.username}")
        print(f"  Size: {width}x{height}, {file_size} bytes")

        if not dry_run:
            try:
                ImageHistory.objects.create(
                    id=uuid.uuid4(),
                    created_at=created_at,
                    updated_at=timezone.now(),
                    metadata={
                        'recovered': True,
                        'recovery_date': str(timezone.now()),
                        'recovery_session': 294
                    },
                    version=1,
                    is_active=True,
                    filename=filepath.name,
                    file_path=rel_path,
                    thumbnail='',
                    image_type=image_type,
                    prompt=f"[Recovered from disk - {image_type}]",
                    parameters={},
                    model_used='unknown',
                    style='',
                    image_width=width,
                    image_height=height,
                    file_size_bytes=file_size,
                    download_count=0,
                    view_count=0,
                    is_favorite=False,
                    user_notes='',
                    tags=[],
                    user=user,
                    was_selected=False,
                )
                recovered += 1
                print(f"  -> RECOVERED")
            except Exception as e:
                print(f"  -> ERROR: {e}")
        else:
            recovered += 1
            print(f"  -> Would recover (dry run)")

    print("-" * 60)
    print(f"Summary:")
    print(f"  Recovered: {recovered}")
    print(f"  Skipped (older than cutoff): {skipped}")
    print(f"  Total orphaned: {len(orphaned)}")

    if dry_run:
        print("\nThis was a DRY RUN. To actually recover, run with dry_run=False")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Recover orphaned image files')
    parser.add_argument('--execute', action='store_true', help='Actually perform recovery (default is dry run)')
    args = parser.parse_args()

    recover_orphaned_images(dry_run=not args.execute)
