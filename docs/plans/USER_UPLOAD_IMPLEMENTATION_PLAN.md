<!-- DOC-POINTER-V1 -->
> **⚠ HISTORICAL PLAN (Q4 2025 / Q1 2026 build phase).** Drafted during platform build-out; may be partially shipped, renamed in code, or quietly superseded. Preserved for historical reference, not current truth. For current truth see [`docs/INDEX.md`](../INDEX.md) + [`PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) + the latest handoff. See [`docs/plans/INDEX.md`](INDEX.md) for directory scope.

# User Upload Implementation Plan

**Created:** December 12, 2025
**Purpose:** Enable users to upload their own videos, images, and audio to the platform
**Priority:** High - Fills major gap in content creation workflow
**Estimated Effort:** 3-4 sessions

---

## Problem Statement

The platform is built entirely around AI-generated content. Users cannot:
- Upload videos they've recorded
- Upload images for AI enhancement
- Mix their own content with AI-generated content
- Use their photos as inputs for image-to-video generation

This limits the platform to "AI creation" rather than "content creation."

---

## Goals

1. **Upload any media type** - Video, image, audio files
2. **Unified gallery** - Uploaded and AI content in same views
3. **AI integration** - Use uploads as inputs for AI operations
4. **Large file support** - Handle videos up to 500MB with chunked uploads
5. **Format flexibility** - Accept common formats, transcode if needed

---

## Phase 1: Model & Storage Foundation

### 1.1 Add Source Type to Existing Models

```python
# content/models.py

class MediaSourceType(models.TextChoices):
    GENERATED = 'generated', 'AI Generated'
    UPLOADED = 'uploaded', 'User Uploaded'
    IMPORTED = 'imported', 'External Import'
    EDITED = 'edited', 'Edited Version'

class ImageHistory(UnifiedBaseModel):
    # ... existing fields ...

    # NEW: Track content source
    source_type = models.CharField(
        max_length=20,
        choices=MediaSourceType.choices,
        default=MediaSourceType.GENERATED,
        help_text="How this content was created"
    )

    # NEW: Original file for uploads
    original_file = models.FileField(
        upload_to='uploads/images/%Y/%m/',
        null=True,
        blank=True,
        help_text="Original uploaded file"
    )

    # NEW: Original filename (preserve user's name)
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        help_text="Original filename from upload"
    )

    # NEW: File metadata
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="MIME type of original file"
    )


class VideoHistory(UnifiedBaseModel):
    # ... existing fields ...

    # NEW: Track content source
    source_type = models.CharField(
        max_length=20,
        choices=MediaSourceType.choices,
        default=MediaSourceType.GENERATED,
        help_text="How this content was created"
    )

    # NEW: Local file storage for uploads
    video_file = models.FileField(
        upload_to='uploads/videos/%Y/%m/',
        null=True,
        blank=True,
        help_text="Uploaded video file"
    )

    # NEW: Original filename
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        help_text="Original filename from upload"
    )

    # NEW: Video metadata
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="MIME type"
    )

    # NEW: Extracted video properties
    duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Video duration in seconds"
    )

    resolution_width = models.IntegerField(
        null=True,
        blank=True
    )

    resolution_height = models.IntegerField(
        null=True,
        blank=True
    )

    fps = models.FloatField(
        null=True,
        blank=True,
        help_text="Frames per second"
    )

    codec = models.CharField(
        max_length=50,
        blank=True,
        help_text="Video codec (h264, hevc, etc.)"
    )
```

### 1.2 Create Upload Tracking Model

```python
# content/models.py

class UploadSession(models.Model):
    """
    Track multi-part/chunked uploads for large files.
    Enables resume capability for failed uploads.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Upload metadata
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    chunk_size = models.IntegerField(default=5242880)  # 5MB chunks

    # Progress tracking
    chunks_received = models.IntegerField(default=0)
    chunks_total = models.IntegerField()
    bytes_received = models.BigIntegerField(default=0)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('uploading', 'Uploading'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )

    # Temp storage path
    temp_path = models.CharField(max_length=500, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()  # Auto-cleanup incomplete uploads

    # Result
    result_content_type = models.CharField(max_length=50, blank=True)  # 'image' or 'video'
    result_id = models.UUIDField(null=True, blank=True)  # ImageHistory or VideoHistory ID

    class Meta:
        ordering = ['-created_at']
```

### 1.3 Storage Configuration

```python
# core/settings.py additions

# Upload limits
MAX_IMAGE_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
MAX_VIDEO_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB
MAX_AUDIO_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# Allowed formats
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm']
ALLOWED_AUDIO_TYPES = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/flac']

# Upload chunk size for large files
UPLOAD_CHUNK_SIZE = 5 * 1024 * 1024  # 5MB

# Temp upload directory (cleaned up after processing)
UPLOAD_TEMP_DIR = BASE_DIR / 'media' / 'uploads' / 'temp'

# Upload session expiry (incomplete uploads deleted after this)
UPLOAD_SESSION_EXPIRY_HOURS = 24
```

### 1.4 Migration

```python
# core/migrations/0087_user_upload_support.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('content', '0086_...'),  # Previous migration
    ]

    operations = [
        # Add source_type to ImageHistory
        migrations.AddField(
            model_name='imagehistory',
            name='source_type',
            field=models.CharField(
                choices=[
                    ('generated', 'AI Generated'),
                    ('uploaded', 'User Uploaded'),
                    ('imported', 'External Import'),
                    ('edited', 'Edited Version'),
                ],
                default='generated',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='imagehistory',
            name='original_file',
            field=models.FileField(blank=True, null=True, upload_to='uploads/images/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='imagehistory',
            name='original_filename',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='imagehistory',
            name='file_size',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='imagehistory',
            name='mime_type',
            field=models.CharField(blank=True, max_length=100),
        ),

        # Add source_type to VideoHistory
        migrations.AddField(
            model_name='videohistory',
            name='source_type',
            field=models.CharField(
                choices=[
                    ('generated', 'AI Generated'),
                    ('uploaded', 'User Uploaded'),
                    ('imported', 'External Import'),
                    ('edited', 'Edited Version'),
                ],
                default='generated',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='videohistory',
            name='video_file',
            field=models.FileField(blank=True, null=True, upload_to='uploads/videos/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='videohistory',
            name='original_filename',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='videohistory',
            name='file_size',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='videohistory',
            name='mime_type',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='videohistory',
            name='duration_seconds',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='videohistory',
            name='resolution_width',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='videohistory',
            name='resolution_height',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='videohistory',
            name='fps',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='videohistory',
            name='codec',
            field=models.CharField(blank=True, max_length=50),
        ),

        # Create UploadSession model
        migrations.CreateModel(
            name='UploadSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to='auth.user')),
                ('filename', models.CharField(max_length=255)),
                ('file_size', models.BigIntegerField()),
                ('mime_type', models.CharField(max_length=100)),
                ('chunk_size', models.IntegerField(default=5242880)),
                ('chunks_received', models.IntegerField(default=0)),
                ('chunks_total', models.IntegerField()),
                ('bytes_received', models.BigIntegerField(default=0)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('temp_path', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField()),
                ('result_content_type', models.CharField(blank=True, max_length=50)),
                ('result_id', models.UUIDField(blank=True, null=True)),
            ],
        ),
    ]
```

---

## Phase 2: Upload API Endpoints

### 2.1 Create Upload Views

```python
# core/views_upload.py

"""
User Upload Views

Handles file uploads for images, videos, and audio.
Supports chunked uploads for large files.
"""

import os
import uuid
import magic
import hashlib
import subprocess
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from content.models import ImageHistory, VideoHistory, UploadSession, MediaSourceType

import logging
logger = logging.getLogger(__name__)


# =============================================================================
# Simple Upload (Small Files < 10MB)
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    """
    Upload a single image file.

    POST /api/upload/image/

    Form data:
        - file: Image file (required)
        - project_id: UUID (optional)
        - title: String (optional)

    Returns:
        - ImageHistory object as JSON
    """
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    uploaded_file = request.FILES['file']

    # Validate file type
    mime_type = magic.from_buffer(uploaded_file.read(2048), mime=True)
    uploaded_file.seek(0)

    if mime_type not in settings.ALLOWED_IMAGE_TYPES:
        return JsonResponse({
            'error': f'Invalid file type: {mime_type}',
            'allowed': settings.ALLOWED_IMAGE_TYPES
        }, status=400)

    # Validate file size
    if uploaded_file.size > settings.MAX_IMAGE_UPLOAD_SIZE:
        max_mb = settings.MAX_IMAGE_UPLOAD_SIZE / (1024 * 1024)
        return JsonResponse({
            'error': f'File too large. Maximum size is {max_mb}MB'
        }, status=400)

    # Generate unique filename
    ext = Path(uploaded_file.name).suffix.lower()
    new_filename = f"{uuid.uuid4()}{ext}"

    # Save file
    upload_path = f"uploads/images/{timezone.now().strftime('%Y/%m')}/{new_filename}"
    saved_path = default_storage.save(upload_path, uploaded_file)

    # Get image dimensions
    from PIL import Image
    uploaded_file.seek(0)
    with Image.open(uploaded_file) as img:
        width, height = img.size

    # Create ImageHistory record
    image = ImageHistory.objects.create(
        user=request.user,
        source_type=MediaSourceType.UPLOADED,
        original_file=saved_path,
        original_filename=uploaded_file.name,
        filename=new_filename,
        file_path=default_storage.url(saved_path),
        file_size=uploaded_file.size,
        mime_type=mime_type,
        image_type='uploaded',
        width=width,
        height=height,
        prompt=request.POST.get('title', f'Uploaded: {uploaded_file.name}'),
        project_id=request.POST.get('project_id'),
    )

    # Generate thumbnail
    _generate_thumbnail(image, uploaded_file)

    return JsonResponse({
        'success': True,
        'image': {
            'id': str(image.id),
            'filename': image.filename,
            'url': image.file_path,
            'thumbnail': image.thumbnail,
            'width': image.width,
            'height': image.height,
            'source_type': image.source_type,
            'created_at': image.created_at.isoformat(),
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_video(request):
    """
    Upload a single video file (small files only, < 50MB).
    For larger files, use chunked upload.

    POST /api/upload/video/

    Form data:
        - file: Video file (required)
        - project_id: UUID (optional)
        - title: String (optional)
    """
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    uploaded_file = request.FILES['file']

    # For files > 50MB, require chunked upload
    if uploaded_file.size > 50 * 1024 * 1024:
        return JsonResponse({
            'error': 'File too large for simple upload. Use chunked upload.',
            'use_chunked': True,
            'init_url': '/api/upload/chunked/init/'
        }, status=400)

    # Validate file type
    mime_type = magic.from_buffer(uploaded_file.read(2048), mime=True)
    uploaded_file.seek(0)

    if mime_type not in settings.ALLOWED_VIDEO_TYPES:
        return JsonResponse({
            'error': f'Invalid file type: {mime_type}',
            'allowed': settings.ALLOWED_VIDEO_TYPES
        }, status=400)

    # Generate unique filename
    ext = Path(uploaded_file.name).suffix.lower()
    new_filename = f"{uuid.uuid4()}{ext}"

    # Save file
    upload_path = f"uploads/videos/{timezone.now().strftime('%Y/%m')}/{new_filename}"
    saved_path = default_storage.save(upload_path, uploaded_file)
    full_path = default_storage.path(saved_path)

    # Extract video metadata using ffprobe
    metadata = _extract_video_metadata(full_path)

    # Create VideoHistory record
    video = VideoHistory.objects.create(
        user=request.user,
        source_type=MediaSourceType.UPLOADED,
        video_file=saved_path,
        original_filename=uploaded_file.name,
        video_url=default_storage.url(saved_path),
        file_size=uploaded_file.size,
        mime_type=mime_type,
        prompt=request.POST.get('title', f'Uploaded: {uploaded_file.name}'),
        project_id=request.POST.get('project_id'),
        duration_seconds=metadata.get('duration'),
        resolution_width=metadata.get('width'),
        resolution_height=metadata.get('height'),
        fps=metadata.get('fps'),
        codec=metadata.get('codec'),
        status='completed',
    )

    # Generate thumbnail from first frame
    _generate_video_thumbnail(video, full_path)

    return JsonResponse({
        'success': True,
        'video': {
            'id': str(video.id),
            'url': video.video_url,
            'thumbnail': video.thumbnail_url,
            'duration': video.duration_seconds,
            'resolution': f"{video.resolution_width}x{video.resolution_height}",
            'source_type': video.source_type,
            'created_at': video.created_at.isoformat(),
        }
    })


# =============================================================================
# Chunked Upload (Large Files)
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chunked_upload_init(request):
    """
    Initialize a chunked upload session.

    POST /api/upload/chunked/init/

    JSON body:
        - filename: Original filename
        - file_size: Total file size in bytes
        - mime_type: MIME type
        - content_type: 'image', 'video', or 'audio'

    Returns:
        - upload_id: UUID for subsequent chunk uploads
        - chunk_size: Recommended chunk size
        - chunks_total: Number of chunks expected
    """
    data = request.data

    filename = data.get('filename')
    file_size = data.get('file_size')
    mime_type = data.get('mime_type')
    content_type = data.get('content_type', 'video')

    if not all([filename, file_size, mime_type]):
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    # Validate limits
    if content_type == 'video' and file_size > settings.MAX_VIDEO_UPLOAD_SIZE:
        return JsonResponse({'error': 'File exceeds maximum video size'}, status=400)
    elif content_type == 'image' and file_size > settings.MAX_IMAGE_UPLOAD_SIZE:
        return JsonResponse({'error': 'File exceeds maximum image size'}, status=400)

    # Calculate chunks
    chunk_size = settings.UPLOAD_CHUNK_SIZE
    chunks_total = (file_size + chunk_size - 1) // chunk_size

    # Create temp directory for chunks
    upload_id = uuid.uuid4()
    temp_dir = Path(settings.UPLOAD_TEMP_DIR) / str(upload_id)
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Create upload session
    session = UploadSession.objects.create(
        id=upload_id,
        user=request.user,
        filename=filename,
        file_size=file_size,
        mime_type=mime_type,
        chunk_size=chunk_size,
        chunks_total=chunks_total,
        temp_path=str(temp_dir),
        expires_at=timezone.now() + timedelta(hours=settings.UPLOAD_SESSION_EXPIRY_HOURS),
        status='uploading',
    )

    return JsonResponse({
        'success': True,
        'upload_id': str(upload_id),
        'chunk_size': chunk_size,
        'chunks_total': chunks_total,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chunked_upload_chunk(request, upload_id):
    """
    Upload a single chunk.

    POST /api/upload/chunked/{upload_id}/chunk/

    Form data:
        - chunk: Chunk data
        - chunk_number: 0-indexed chunk number

    Returns:
        - chunks_received: Number of chunks received so far
        - complete: True if all chunks received
    """
    try:
        session = UploadSession.objects.get(id=upload_id, user=request.user)
    except UploadSession.DoesNotExist:
        return JsonResponse({'error': 'Upload session not found'}, status=404)

    if session.status not in ['pending', 'uploading']:
        return JsonResponse({'error': f'Upload session is {session.status}'}, status=400)

    chunk = request.FILES.get('chunk')
    chunk_number = int(request.POST.get('chunk_number', 0))

    if not chunk:
        return JsonResponse({'error': 'No chunk data'}, status=400)

    # Save chunk to temp directory
    chunk_path = Path(session.temp_path) / f"chunk_{chunk_number:06d}"
    with open(chunk_path, 'wb') as f:
        for part in chunk.chunks():
            f.write(part)

    # Update session
    session.chunks_received += 1
    session.bytes_received += chunk.size
    session.save()

    # Check if complete
    complete = session.chunks_received >= session.chunks_total

    if complete:
        # Trigger assembly in background
        from core.tasks import assemble_chunked_upload
        assemble_chunked_upload.delay(str(upload_id))
        session.status = 'processing'
        session.save()

    return JsonResponse({
        'success': True,
        'chunks_received': session.chunks_received,
        'chunks_total': session.chunks_total,
        'bytes_received': session.bytes_received,
        'complete': complete,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chunked_upload_status(request, upload_id):
    """
    Get status of a chunked upload.

    GET /api/upload/chunked/{upload_id}/status/
    """
    try:
        session = UploadSession.objects.get(id=upload_id, user=request.user)
    except UploadSession.DoesNotExist:
        return JsonResponse({'error': 'Upload session not found'}, status=404)

    response = {
        'upload_id': str(session.id),
        'status': session.status,
        'filename': session.filename,
        'chunks_received': session.chunks_received,
        'chunks_total': session.chunks_total,
        'bytes_received': session.bytes_received,
        'file_size': session.file_size,
        'progress_percent': round(session.bytes_received / session.file_size * 100, 1),
    }

    if session.status == 'completed' and session.result_id:
        response['result'] = {
            'content_type': session.result_content_type,
            'id': str(session.result_id),
        }

    return JsonResponse(response)


# =============================================================================
# Helper Functions
# =============================================================================

def _extract_video_metadata(file_path):
    """Extract video metadata using ffprobe."""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return {}

        import json
        data = json.loads(result.stdout)

        # Find video stream
        video_stream = next(
            (s for s in data.get('streams', []) if s.get('codec_type') == 'video'),
            {}
        )

        format_info = data.get('format', {})

        # Parse frame rate (e.g., "30/1" or "29.97")
        fps = None
        if 'r_frame_rate' in video_stream:
            fps_str = video_stream['r_frame_rate']
            if '/' in fps_str:
                num, den = fps_str.split('/')
                fps = float(num) / float(den)
            else:
                fps = float(fps_str)

        return {
            'duration': float(format_info.get('duration', 0)),
            'width': video_stream.get('width'),
            'height': video_stream.get('height'),
            'fps': fps,
            'codec': video_stream.get('codec_name'),
        }
    except Exception as e:
        logger.error(f"Failed to extract video metadata: {e}")
        return {}


def _generate_thumbnail(image_record, uploaded_file):
    """Generate thumbnail for uploaded image."""
    try:
        from PIL import Image
        uploaded_file.seek(0)

        with Image.open(uploaded_file) as img:
            # Create thumbnail
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)

            # Save thumbnail
            thumb_filename = f"thumb_{image_record.filename}"
            thumb_path = f"uploads/images/thumbnails/{thumb_filename}"

            from io import BytesIO
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)

            saved_path = default_storage.save(thumb_path, ContentFile(buffer.read()))
            image_record.thumbnail = default_storage.url(saved_path)
            image_record.save()
    except Exception as e:
        logger.error(f"Failed to generate thumbnail: {e}")


def _generate_video_thumbnail(video_record, file_path):
    """Generate thumbnail from video first frame."""
    try:
        thumb_filename = f"thumb_{video_record.id}.jpg"
        thumb_path = Path(settings.MEDIA_ROOT) / 'uploads' / 'videos' / 'thumbnails' / thumb_filename
        thumb_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            'ffmpeg', '-i', file_path,
            '-vf', 'thumbnail,scale=300:-1',
            '-frames:v', '1',
            '-y', str(thumb_path)
        ]
        subprocess.run(cmd, capture_output=True, timeout=30)

        if thumb_path.exists():
            video_record.thumbnail_url = f"/media/uploads/videos/thumbnails/{thumb_filename}"
            video_record.save()
    except Exception as e:
        logger.error(f"Failed to generate video thumbnail: {e}")
```

### 2.2 Celery Task for Chunk Assembly

```python
# core/tasks.py additions

@shared_task
def assemble_chunked_upload(upload_id: str):
    """
    Assemble chunks into final file and create content record.
    """
    from content.models import UploadSession, ImageHistory, VideoHistory, MediaSourceType

    try:
        session = UploadSession.objects.get(id=upload_id)
    except UploadSession.DoesNotExist:
        logger.error(f"Upload session {upload_id} not found")
        return

    try:
        temp_dir = Path(session.temp_path)

        # Get all chunks in order
        chunks = sorted(temp_dir.glob('chunk_*'))

        if len(chunks) != session.chunks_total:
            raise ValueError(f"Expected {session.chunks_total} chunks, found {len(chunks)}")

        # Determine final path
        ext = Path(session.filename).suffix.lower()
        new_filename = f"{uuid.uuid4()}{ext}"

        if session.mime_type.startswith('video/'):
            final_dir = Path(settings.MEDIA_ROOT) / 'uploads' / 'videos' / timezone.now().strftime('%Y/%m')
        else:
            final_dir = Path(settings.MEDIA_ROOT) / 'uploads' / 'images' / timezone.now().strftime('%Y/%m')

        final_dir.mkdir(parents=True, exist_ok=True)
        final_path = final_dir / new_filename

        # Assemble chunks
        with open(final_path, 'wb') as final_file:
            for chunk_path in chunks:
                with open(chunk_path, 'rb') as chunk:
                    final_file.write(chunk.read())

        # Create content record
        if session.mime_type.startswith('video/'):
            metadata = _extract_video_metadata(str(final_path))

            video = VideoHistory.objects.create(
                user=session.user,
                source_type=MediaSourceType.UPLOADED,
                video_file=str(final_path.relative_to(settings.MEDIA_ROOT)),
                original_filename=session.filename,
                video_url=f"/media/{final_path.relative_to(settings.MEDIA_ROOT)}",
                file_size=session.file_size,
                mime_type=session.mime_type,
                prompt=f'Uploaded: {session.filename}',
                duration_seconds=metadata.get('duration'),
                resolution_width=metadata.get('width'),
                resolution_height=metadata.get('height'),
                fps=metadata.get('fps'),
                codec=metadata.get('codec'),
                status='completed',
            )

            _generate_video_thumbnail(video, str(final_path))

            session.result_content_type = 'video'
            session.result_id = video.id
        else:
            # Image handling
            from PIL import Image
            with Image.open(final_path) as img:
                width, height = img.size

            image = ImageHistory.objects.create(
                user=session.user,
                source_type=MediaSourceType.UPLOADED,
                original_file=str(final_path.relative_to(settings.MEDIA_ROOT)),
                original_filename=session.filename,
                filename=new_filename,
                file_path=f"/media/{final_path.relative_to(settings.MEDIA_ROOT)}",
                file_size=session.file_size,
                mime_type=session.mime_type,
                image_type='uploaded',
                width=width,
                height=height,
                prompt=f'Uploaded: {session.filename}',
            )

            session.result_content_type = 'image'
            session.result_id = image.id

        # Cleanup temp files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

        session.status = 'completed'
        session.save()

        logger.info(f"Chunked upload {upload_id} completed successfully")

    except Exception as e:
        logger.error(f"Failed to assemble chunked upload {upload_id}: {e}")
        session.status = 'failed'
        session.save()


@shared_task
def cleanup_expired_uploads():
    """
    Clean up incomplete upload sessions older than expiry time.
    Run hourly via Celery Beat.
    """
    from content.models import UploadSession

    expired = UploadSession.objects.filter(
        status__in=['pending', 'uploading'],
        expires_at__lt=timezone.now()
    )

    for session in expired:
        # Remove temp files
        if session.temp_path:
            import shutil
            shutil.rmtree(session.temp_path, ignore_errors=True)

        session.status = 'cancelled'
        session.save()
        logger.info(f"Cleaned up expired upload session {session.id}")
```

### 2.3 URL Configuration

```python
# core/urls.py additions

# User Uploads
path('api/upload/image/', views_upload.upload_image, name='upload_image'),
path('api/upload/video/', views_upload.upload_video, name='upload_video'),
path('api/upload/chunked/init/', views_upload.chunked_upload_init, name='chunked_upload_init'),
path('api/upload/chunked/<uuid:upload_id>/chunk/', views_upload.chunked_upload_chunk, name='chunked_upload_chunk'),
path('api/upload/chunked/<uuid:upload_id>/status/', views_upload.chunked_upload_status, name='chunked_upload_status'),
```

---

## Phase 3: Frontend Implementation

### 3.1 Upload Component (JavaScript)

```javascript
// Add to ai_image_studio.html or separate JS file

class MediaUploader {
    constructor(options = {}) {
        this.chunkSize = options.chunkSize || 5 * 1024 * 1024; // 5MB
        this.simpleUploadLimit = 50 * 1024 * 1024; // 50MB
        this.onProgress = options.onProgress || (() => {});
        this.onComplete = options.onComplete || (() => {});
        this.onError = options.onError || (() => {});
    }

    async uploadFile(file, contentType = 'auto') {
        // Detect content type
        if (contentType === 'auto') {
            if (file.type.startsWith('video/')) contentType = 'video';
            else if (file.type.startsWith('image/')) contentType = 'image';
            else if (file.type.startsWith('audio/')) contentType = 'audio';
            else {
                this.onError('Unsupported file type');
                return;
            }
        }

        // Use simple upload for small files
        if (file.size < this.simpleUploadLimit) {
            return this.simpleUpload(file, contentType);
        }

        // Use chunked upload for large files
        return this.chunkedUpload(file, contentType);
    }

    async simpleUpload(file, contentType) {
        const formData = new FormData();
        formData.append('file', file);

        const endpoint = contentType === 'video'
            ? '/api/upload/video/'
            : '/api/upload/image/';

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: formData,
            });

            const result = await response.json();

            if (result.success) {
                this.onComplete(result);
            } else {
                this.onError(result.error);
            }

            return result;
        } catch (error) {
            this.onError(error.message);
            throw error;
        }
    }

    async chunkedUpload(file, contentType) {
        // Initialize upload session
        const initResponse = await fetch('/api/upload/chunked/init/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({
                filename: file.name,
                file_size: file.size,
                mime_type: file.type,
                content_type: contentType,
            }),
        });

        const initData = await initResponse.json();

        if (!initData.success) {
            this.onError(initData.error);
            return;
        }

        const uploadId = initData.upload_id;
        const chunksTotal = initData.chunks_total;

        // Upload chunks
        for (let i = 0; i < chunksTotal; i++) {
            const start = i * this.chunkSize;
            const end = Math.min(start + this.chunkSize, file.size);
            const chunk = file.slice(start, end);

            const formData = new FormData();
            formData.append('chunk', chunk);
            formData.append('chunk_number', i);

            const chunkResponse = await fetch(`/api/upload/chunked/${uploadId}/chunk/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: formData,
            });

            const chunkData = await chunkResponse.json();

            if (!chunkData.success) {
                this.onError(chunkData.error);
                return;
            }

            // Report progress
            const progress = Math.round(((i + 1) / chunksTotal) * 100);
            this.onProgress(progress, chunkData.bytes_received, file.size);

            if (chunkData.complete) {
                // Poll for processing completion
                return this.pollUploadStatus(uploadId);
            }
        }
    }

    async pollUploadStatus(uploadId) {
        const maxAttempts = 60; // 2 minutes max

        for (let i = 0; i < maxAttempts; i++) {
            await this.sleep(2000);

            const response = await fetch(`/api/upload/chunked/${uploadId}/status/`);
            const data = await response.json();

            if (data.status === 'completed') {
                this.onComplete(data);
                return data;
            } else if (data.status === 'failed') {
                this.onError('Upload processing failed');
                return;
            }

            this.onProgress(100, data.file_size, data.file_size, 'Processing...');
        }

        this.onError('Upload processing timeout');
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.cookie.match(/csrftoken=([^;]+)/)?.[1];
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}


// Drag & Drop Zone
function initUploadZone(elementId) {
    const zone = document.getElementById(elementId);
    if (!zone) return;

    const uploader = new MediaUploader({
        onProgress: (percent, received, total, status) => {
            updateUploadProgress(percent, status);
        },
        onComplete: (result) => {
            showUploadSuccess(result);
            refreshGallery();
        },
        onError: (error) => {
            showUploadError(error);
        },
    });

    // Drag events
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('drag-over');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('drag-over');
    });

    zone.addEventListener('drop', async (e) => {
        e.preventDefault();
        zone.classList.remove('drag-over');

        const files = Array.from(e.dataTransfer.files);
        for (const file of files) {
            await uploader.uploadFile(file);
        }
    });

    // Click to select
    zone.addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*,video/*';
        input.multiple = true;
        input.onchange = async (e) => {
            const files = Array.from(e.target.files);
            for (const file of files) {
                await uploader.uploadFile(file);
            }
        };
        input.click();
    });
}
```

### 3.2 Upload UI Components

```html
<!-- Add to ai_image_studio.html in appropriate tab -->

<!-- Upload Zone -->
<div id="upload-zone" class="upload-dropzone">
    <div class="upload-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
    </div>
    <div class="upload-text">
        <p class="upload-title">Drop files here or click to upload</p>
        <p class="upload-subtitle">Images up to 50MB, Videos up to 500MB</p>
    </div>
</div>

<!-- Upload Progress -->
<div id="upload-progress" class="upload-progress hidden">
    <div class="progress-bar">
        <div class="progress-fill" style="width: 0%"></div>
    </div>
    <div class="progress-text">
        <span class="progress-percent">0%</span>
        <span class="progress-status">Uploading...</span>
    </div>
</div>

<style>
.upload-dropzone {
    border: 2px dashed rgba(255,255,255,0.3);
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: rgba(255,255,255,0.02);
}

.upload-dropzone:hover,
.upload-dropzone.drag-over {
    border-color: #6366f1;
    background: rgba(99, 102, 241, 0.1);
}

.upload-icon {
    color: rgba(255,255,255,0.5);
    margin-bottom: 16px;
}

.upload-title {
    font-size: 16px;
    font-weight: 500;
    color: #fff;
    margin-bottom: 8px;
}

.upload-subtitle {
    font-size: 13px;
    color: rgba(255,255,255,0.5);
}

.upload-progress {
    margin-top: 20px;
    padding: 16px;
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
}

.progress-bar {
    height: 8px;
    background: rgba(255,255,255,0.1);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    transition: width 0.3s ease;
}

.progress-text {
    display: flex;
    justify-content: space-between;
    margin-top: 8px;
    font-size: 13px;
    color: rgba(255,255,255,0.7);
}

.hidden {
    display: none;
}
</style>
```

---

## Phase 4: AI Integration

### 4.1 Use Uploaded Images for Image-to-Video

```python
# Modify core/views_video.py

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def image_to_video(request):
    """
    Generate video from image - now supports uploaded images.
    """
    image_id = request.data.get('image_id')

    # Resolve image - works for both generated and uploaded
    image = ImageHistory.objects.filter(
        id=image_id,
        user=request.user
    ).first()

    if not image:
        return JsonResponse({'error': 'Image not found'}, status=404)

    # Get image URL - handle both uploaded files and CDN URLs
    if image.source_type == 'uploaded' and image.original_file:
        # For uploaded files, use local path or serve via URL
        image_url = request.build_absolute_uri(image.original_file.url)
    else:
        image_url = image.file_path

    # Send to Runway ML
    # ... existing image-to-video logic ...
```

### 4.2 Apply AI Editing to Uploaded Videos

```python
# Modify core/views_video.py

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_video_effects(request):
    """
    Apply effects to any video - generated or uploaded.
    """
    video_id = request.data.get('video_id')
    effects = request.data.get('effects', [])

    video = VideoHistory.objects.filter(
        id=video_id,
        user=request.user
    ).first()

    if not video:
        return JsonResponse({'error': 'Video not found'}, status=404)

    # Get video path - works for both uploaded and generated
    if video.source_type == 'uploaded' and video.video_file:
        video_path = video.video_file.path
    else:
        # Download from CDN URL if needed
        video_path = _download_video_to_temp(video.video_url)

    # Apply effects using ffmpeg
    # ... existing effect logic ...
```

---

## Phase 5: Gallery Updates

### 5.1 Unified Gallery View

Update gallery queries to include both generated and uploaded content:

```python
# core/views_image.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_gallery(request):
    """
    Get all user images - generated AND uploaded.
    """
    source_filter = request.GET.get('source')  # 'all', 'generated', 'uploaded'

    queryset = ImageHistory.objects.filter(user=request.user)

    if source_filter == 'generated':
        queryset = queryset.filter(source_type='generated')
    elif source_filter == 'uploaded':
        queryset = queryset.filter(source_type='uploaded')
    # 'all' returns everything

    images = queryset.order_by('-created_at')[:100]

    return JsonResponse({
        'images': [{
            'id': str(img.id),
            'url': img.file_path,
            'thumbnail': img.thumbnail,
            'source_type': img.source_type,  # NEW: Include source
            'created_at': img.created_at.isoformat(),
            # ... other fields
        } for img in images]
    })
```

### 5.2 Source Type Badge in UI

```javascript
// In gallery rendering
function renderGalleryItem(item) {
    const sourceIcon = item.source_type === 'uploaded'
        ? '<span class="badge badge-upload" title="Uploaded">↑</span>'
        : '<span class="badge badge-ai" title="AI Generated">✨</span>';

    return `
        <div class="gallery-item" data-id="${item.id}">
            <img src="${item.thumbnail || item.url}" alt="">
            ${sourceIcon}
        </div>
    `;
}
```

---

## Testing Checklist

### Phase 1: Models
- [ ] Migration runs without errors
- [ ] Existing ImageHistory/VideoHistory records get default `source_type='generated'`
- [ ] UploadSession model created

### Phase 2: API
- [ ] Simple image upload works (< 50MB)
- [ ] Simple video upload works (< 50MB)
- [ ] Chunked upload initializes correctly
- [ ] Chunks upload and assemble
- [ ] Progress polling works
- [ ] Thumbnails generated for both

### Phase 3: Frontend
- [ ] Drag-drop zone works
- [ ] Click-to-select works
- [ ] Progress bar updates
- [ ] Large file chunking visible in UI
- [ ] Success notification shows

### Phase 4: Integration
- [ ] Uploaded image works as image-to-video source
- [ ] Video effects apply to uploaded videos
- [ ] Uploaded content appears in projects

### Phase 5: Gallery
- [ ] Both types appear in gallery
- [ ] Filter by source works
- [ ] Source badges display correctly

---

## Dependencies

```
python-magic==0.4.27  # File type detection
Pillow>=9.0.0         # Image processing (already installed)
ffmpeg                # Video processing (already installed)
```

---

## Rollout Plan

1. **Session A:** Implement Phase 1 (Models) + Phase 2 (API for images only)
2. **Session B:** Add video upload + chunked uploads
3. **Session C:** Frontend implementation
4. **Session D:** AI integration + testing

---

## Future Enhancements

1. **Audio uploads** - Similar pattern for audio files
2. **Batch uploads** - Upload multiple files at once
3. **Cloud import** - Import from Google Drive, Dropbox
4. **URL import** - Download from URL
5. **Transcription** - Auto-transcribe uploaded videos
6. **Scene detection** - AI-powered scene splitting

---

**This plan transforms the platform from "AI generator" to "complete content studio."**
