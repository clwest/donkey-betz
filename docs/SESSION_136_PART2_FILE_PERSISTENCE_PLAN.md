# Session 136 Part 2: File Persistence & Cloud Storage Implementation

**Date:** November 19, 2025
**Status:** Planning Phase
**Priority:** High - Prevents data loss and improves reliability

## Problem Statement

Image files are being deleted from disk while database records remain, causing:
- `FileNotFoundError` when users try to edit images
- Poor user experience with cryptic error messages
- Data integrity issues between database and file system

## Two-Phase Solution

### Phase 1: Immediate Fix (File Existence Checking)
Prevent errors by detecting missing files and hiding them from UI.

### Phase 2: Cloud Storage (Permanent Solution)
Upload all images to Cloudinary/S3 for permanent, scalable storage.

---

## Phase 1: Immediate Fix

### 1.1 Add File Existence Method to ImageHistory

**File:** `content/models.py`
**Location:** ImageHistory class

Add method to check if file exists:

```python
import os
from django.conf import settings

class ImageHistory(UnifiedBaseModel):
    # ... existing fields ...

    def file_exists(self):
        """Check if the image file exists on disk."""
        if not self.file_path:
            return False

        # Handle both absolute and relative paths
        if os.path.isabs(self.file_path):
            return os.path.exists(self.file_path)
        else:
            # Relative to project root
            full_path = os.path.join(settings.BASE_DIR, self.file_path)
            return os.path.exists(full_path)

    def get_absolute_file_path(self):
        """Get absolute path to the image file."""
        if not self.file_path:
            return None

        if os.path.isabs(self.file_path):
            return self.file_path
        else:
            return os.path.join(settings.BASE_DIR, self.file_path)
```

### 1.2 Filter Missing Images from API

**File:** `core/views_project.py` (or wherever project assets API is)

Update the project assets endpoint to exclude missing images:

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project_assets(request, project_id):
    """Get all assets for a project, excluding missing files."""
    try:
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Get images and filter out missing ones
        all_images = ImageHistory.objects.filter(
            project=project
        ).order_by('-created_at')

        # Only include images where files exist
        images = [img for img in all_images if img.file_exists()]

        # ... rest of code ...
```

### 1.3 Add File Existence Check Before Operations

**File:** `core/views_image.py`

Add check in recolor and other editing operations:

```python
def recolor_image(request):
    """Recolor an existing image."""
    image_id = request.data.get('image_id')

    try:
        image = ImageHistory.objects.get(id=image_id, user=request.user)

        # Check if file exists before proceeding
        if not image.file_exists():
            return JsonResponse({
                'success': False,
                'error': 'Image file no longer available. The file may have been deleted.',
                'error_code': 'FILE_MISSING'
            }, status=404)

        # Continue with recolor operation...
```

### 1.4 Create Cleanup Utility Script

**File:** `cleanup_orphaned_images.py`

Script to identify and optionally remove orphaned records:

```python
#!/usr/bin/env python3
"""
Find and optionally remove ImageHistory records where files no longer exist.
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory

def find_orphaned_images(dry_run=True):
    """Find images where files don't exist."""
    all_images = ImageHistory.objects.all()
    orphaned = []

    print(f"Checking {all_images.count()} images...")

    for img in all_images:
        if not img.file_exists():
            orphaned.append(img)
            print(f"  Orphaned: {img.id} - {img.file_path}")

    print(f"\nFound {len(orphaned)} orphaned images")

    if not dry_run and orphaned:
        confirm = input(f"\nDelete {len(orphaned)} orphaned records? (yes/no): ")
        if confirm.lower() == 'yes':
            for img in orphaned:
                img.delete()
            print(f"Deleted {len(orphaned)} orphaned records")

    return orphaned

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--delete', action='store_true', help='Actually delete orphaned records')
    args = parser.parse_args()

    find_orphaned_images(dry_run=not args.delete)
```

---

## Phase 2: Cloud Storage Integration

### 2.1 Choose Provider: Cloudinary

**Why Cloudinary?**
- Easy Django integration
- Built-in image transformations
- Free tier: 25 credits/month (generous)
- Automatic CDN
- Simple API

**Alternative:** AWS S3 (more setup, but cheaper at scale)

### 2.2 Install Dependencies

```bash
pip install cloudinary django-cloudinary-storage
```

Add to `requirements.txt`:
```
cloudinary==1.36.0
django-cloudinary-storage==0.3.0
```

### 2.3 Configure Cloudinary

**File:** `.env`

Add Cloudinary credentials:
```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

**File:** `core/settings.py`

Add Cloudinary configuration:

```python
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps ...
    'cloudinary_storage',
    'cloudinary',
]

# Configure default file storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### 2.4 Add Cloud URL Field to Model

**File:** `content/models.py`

Add migration to add cloud_url field:

```python
class ImageHistory(UnifiedBaseModel):
    # ... existing fields ...

    # Session 136: Cloud storage support
    cloud_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Cloudinary/S3 URL for permanent storage"
    )

    def get_image_url(self):
        """Get image URL, preferring cloud storage."""
        if self.cloud_url:
            return self.cloud_url
        elif self.file_path and self.file_exists():
            return f"/media/{self.file_path}"
        else:
            return None
```

### 2.5 Create Upload Utility

**File:** `content/cloud_storage.py` (NEW)

```python
"""
Cloud storage utilities for image persistence.
"""
import os
import logging
import cloudinary
import cloudinary.uploader
from django.conf import settings

logger = logging.getLogger(__name__)


class CloudStorageManager:
    """Manage cloud storage uploads for images."""

    @staticmethod
    def upload_image(file_path, public_id=None, folder="ai-content-studio"):
        """
        Upload image to Cloudinary.

        Args:
            file_path: Local file path
            public_id: Optional public ID for the image
            folder: Cloudinary folder path

        Returns:
            dict with 'success', 'url', and 'public_id' or 'error'
        """
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file_path,
                folder=folder,
                public_id=public_id,
                resource_type='image',
                overwrite=False
            )

            logger.info(f"✅ Uploaded to Cloudinary: {result['secure_url']}")

            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id']
            }

        except Exception as e:
            logger.error(f"❌ Cloudinary upload failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def delete_image(public_id):
        """Delete image from Cloudinary."""
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        except Exception as e:
            logger.error(f"❌ Cloudinary delete failed: {e}")
            return False
```

### 2.6 Update Image Generation to Upload

**File:** `core/views_image.py`

Modify `save_to_history()` to upload to cloud:

```python
from content.cloud_storage import CloudStorageManager

def save_to_history(...):
    """Save image to history with cloud upload."""

    # ... existing code to save file locally ...

    # Create database record
    history = ImageHistory.objects.create(...)

    # Upload to cloud storage
    if file_path and os.path.exists(file_path):
        cloud_result = CloudStorageManager.upload_image(
            file_path=file_path,
            public_id=f"image_{history.id}",
            folder="ai-content-studio/images"
        )

        if cloud_result['success']:
            history.cloud_url = cloud_result['url']
            history.save(update_fields=['cloud_url'])
            logger.info(f"✅ Image uploaded to cloud: {cloud_result['url']}")
        else:
            logger.warning(f"⚠️  Cloud upload failed: {cloud_result['error']}")

    return history
```

### 2.7 Migration Script for Existing Images

**File:** `migrate_images_to_cloud.py`

```python
#!/usr/bin/env python3
"""
Migrate existing images to Cloudinary.
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory
from content.cloud_storage import CloudStorageManager

def migrate_images():
    """Upload all existing images to Cloudinary."""
    images = ImageHistory.objects.filter(cloud_url__isnull=True)
    total = images.count()

    print(f"Found {total} images to migrate")

    success_count = 0
    fail_count = 0
    skip_count = 0

    for i, img in enumerate(images, 1):
        print(f"\n[{i}/{total}] Processing {img.id}...")

        # Check if file exists
        if not img.file_exists():
            print(f"  ⏭️  Skipping - file missing")
            skip_count += 1
            continue

        # Upload to cloud
        file_path = img.get_absolute_file_path()
        result = CloudStorageManager.upload_image(
            file_path=file_path,
            public_id=f"image_{img.id}",
            folder="ai-content-studio/images"
        )

        if result['success']:
            img.cloud_url = result['url']
            img.save(update_fields=['cloud_url'])
            print(f"  ✅ Uploaded: {result['url']}")
            success_count += 1
        else:
            print(f"  ❌ Failed: {result['error']}")
            fail_count += 1

    print(f"\n{'='*80}")
    print(f"Migration complete!")
    print(f"  ✅ Success: {success_count}")
    print(f"  ❌ Failed: {fail_count}")
    print(f"  ⏭️  Skipped: {skip_count}")
    print(f"{'='*80}")

if __name__ == "__main__":
    migrate_images()
```

---

## Implementation Steps

### Phase 1 (Immediate - This Session)
1. Add `file_exists()` method to ImageHistory model
2. Update project assets API to filter missing images
3. Add file existence check to editing operations
4. Create cleanup utility script
5. Test with existing images

### Phase 2 (Next Session)
1. Sign up for Cloudinary account (free tier)
2. Install cloudinary packages
3. Add credentials to `.env`
4. Configure Django settings
5. Add `cloud_url` field to ImageHistory (migration needed)
6. Create CloudStorageManager utility
7. Update image generation to upload to cloud
8. Run migration script for existing images
9. Update `get_image_url()` to prefer cloud URLs
10. Test complete flow: generate → upload → display

---

## Testing Plan

### Phase 1 Testing
- [ ] Verify `file_exists()` correctly identifies missing files
- [ ] Confirm missing images are hidden from project gallery
- [ ] Test editing operations reject missing images with clear error
- [ ] Run cleanup script in dry-run mode
- [ ] Verify error messages are user-friendly

### Phase 2 Testing
- [ ] Upload test image to Cloudinary manually
- [ ] Generate new image and verify cloud upload
- [ ] Migrate existing images and verify URLs
- [ ] Delete local file and verify cloud URL still works
- [ ] Test image display from Cloudinary CDN
- [ ] Verify editing operations work with cloud images

---

## Estimated Effort

**Phase 1:** 1-2 hours
**Phase 2:** 2-3 hours
**Total:** 3-5 hours

---

## Cost Analysis

**Cloudinary Free Tier:**
- 25 credits/month
- ~25,000 image transformations
- 25GB storage
- 25GB bandwidth

**Estimated Usage (100 images/month):**
- Storage: ~1GB
- Bandwidth: ~5GB
- Transformations: ~1,000
- **Cost: $0** (within free tier)

**If exceeding free tier:**
- Paid plans start at $89/month
- Or migrate to AWS S3: ~$0.023/GB/month

---

## Rollback Plan

If cloud storage causes issues:
1. Set `DEFAULT_FILE_STORAGE` back to default
2. Continue using local files
3. Cloud URLs remain in database for future use
4. No data loss - files exist both locally and in cloud

---

## Next Steps

**Ready to implement?**

**Option A:** Implement Phase 1 now (immediate fix)
**Option B:** Implement both phases (complete solution)
**Option C:** Review and adjust plan first

Which would you like to proceed with?
