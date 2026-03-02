"""
Session 451: User Upload Views

Handles file uploads for images, videos, and audio.
Supports both simple uploads (< 50MB) and chunked uploads for large files.

Endpoints:
- POST /api/upload/image/ - Simple image upload
- POST /api/upload/video/ - Simple video upload (< 50MB)
- POST /api/upload/chunked/init/ - Initialize chunked upload
- POST /api/upload/chunked/<uuid>/chunk/ - Upload a chunk
- GET /api/upload/chunked/<uuid>/status/ - Check upload status
"""

import uuid
import json
import subprocess
import logging
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from content.models import ImageHistory, VideoHistory, UploadSession, MediaSourceType

logger = logging.getLogger(__name__)

# Configuration
MAX_IMAGE_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
MAX_VIDEO_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB
MAX_AUDIO_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
UPLOAD_CHUNK_SIZE = 5 * 1024 * 1024  # 5MB chunks
UPLOAD_SESSION_EXPIRY_HOURS = 24

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm', 'video/x-matroska']
ALLOWED_AUDIO_TYPES = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/flac', 'audio/mp4']


def get_mime_type(file_obj):
    """Get MIME type from file using magic numbers or extension."""
    # Try to detect from file content
    try:
        import magic
        header = file_obj.read(2048)
        file_obj.seek(0)
        mime = magic.from_buffer(header, mime=True)
        if mime:
            return mime
    except (ImportError, Exception):
        pass

    # Fallback to content_type from upload
    if hasattr(file_obj, 'content_type') and file_obj.content_type:
        return file_obj.content_type

    # Last resort: extension mapping
    ext = Path(file_obj.name).suffix.lower()
    ext_map = {
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
        '.gif': 'image/gif', '.webp': 'image/webp',
        '.mp4': 'video/mp4', '.mov': 'video/quicktime', '.avi': 'video/x-msvideo',
        '.webm': 'video/webm', '.mkv': 'video/x-matroska',
        '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.ogg': 'audio/ogg',
        '.flac': 'audio/flac', '.m4a': 'audio/mp4',
    }
    return ext_map.get(ext, 'application/octet-stream')


# =============================================================================
# Simple Upload (Small Files < 50MB)
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
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
    mime_type = get_mime_type(uploaded_file)

    if mime_type not in ALLOWED_IMAGE_TYPES:
        return JsonResponse({
            'error': f'Invalid file type: {mime_type}',
            'allowed': ALLOWED_IMAGE_TYPES
        }, status=400)

    # Validate file size
    if uploaded_file.size > MAX_IMAGE_UPLOAD_SIZE:
        max_mb = MAX_IMAGE_UPLOAD_SIZE / (1024 * 1024)
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
    width, height = None, None
    try:
        from PIL import Image
        uploaded_file.seek(0)
        with Image.open(uploaded_file) as img:
            width, height = img.size
    except Exception as e:
        logger.warning(f"Could not get image dimensions: {e}")

    # Create ImageHistory record
    project_id = request.POST.get('project_id')

    image = ImageHistory.objects.create(
        user=request.user,
        source_type=MediaSourceType.UPLOADED,
        original_file=saved_path,
        original_filename=uploaded_file.name,
        filename=new_filename,
        file_path=default_storage.url(saved_path),
        file_size_bytes=uploaded_file.size,
        mime_type=mime_type,
        image_type='uploaded',
        image_width=width,
        image_height=height,
        prompt=request.POST.get('title', f'Uploaded: {uploaded_file.name}'),
        project_id=project_id if project_id else None,
    )

    # Generate thumbnail
    _generate_image_thumbnail(image, uploaded_file)

    logger.info(f"User {request.user.username} uploaded image: {image.filename}")

    return JsonResponse({
        'success': True,
        'image': {
            'id': str(image.id),
            'sequential_number': image.get_sequential_number(),
            'filename': image.filename,
            'url': image.file_path,
            'thumbnail': image.thumbnail,
            'width': image.image_width,
            'height': image.image_height,
            'source_type': image.source_type,
            'created_at': image.created_at.isoformat(),
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
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
    simple_limit = 50 * 1024 * 1024
    if uploaded_file.size > simple_limit:
        return JsonResponse({
            'error': 'File too large for simple upload. Use chunked upload.',
            'use_chunked': True,
            'init_url': '/api/upload/chunked/init/',
            'file_size': uploaded_file.size,
            'limit': simple_limit
        }, status=400)

    # Validate file type
    mime_type = get_mime_type(uploaded_file)

    if mime_type not in ALLOWED_VIDEO_TYPES:
        return JsonResponse({
            'error': f'Invalid file type: {mime_type}',
            'allowed': ALLOWED_VIDEO_TYPES
        }, status=400)

    # Generate unique filename
    ext = Path(uploaded_file.name).suffix.lower()
    new_filename = f"{uuid.uuid4()}{ext}"

    # Save file
    upload_path = f"uploads/videos/{timezone.now().strftime('%Y/%m')}/{new_filename}"
    saved_path = default_storage.save(upload_path, uploaded_file)
    try:
        full_path = default_storage.path(saved_path)
    except NotImplementedError:
        full_path = None

    # Extract video metadata using ffprobe
    metadata = {}
    if full_path:
        metadata = _extract_video_metadata(full_path)

    # Create VideoHistory record
    project_id = request.POST.get('project_id')

    video = VideoHistory.objects.create(
        user=request.user,
        source_type=MediaSourceType.UPLOADED,
        video_file=saved_path,
        original_filename=uploaded_file.name,
        video_url=default_storage.url(saved_path),
        file_size_bytes=uploaded_file.size,
        mime_type=mime_type,
        video_type='uploaded',
        prompt=request.POST.get('title', f'Uploaded: {uploaded_file.name}'),
        project_id=project_id if project_id else None,
        duration=int(metadata.get('duration', 0)) if metadata.get('duration') else None,
        video_width=metadata.get('width'),
        video_height=metadata.get('height'),
        fps=metadata.get('fps'),
        codec=metadata.get('codec'),
        status='completed',
    )

    # Generate thumbnail from first frame
    if full_path:
        _generate_video_thumbnail(video, full_path)

    logger.info(f"User {request.user.username} uploaded video: {video.original_filename}")

    return JsonResponse({
        'success': True,
        'video': {
            'id': str(video.id),
            'sequential_number': video.get_sequential_number(),
            'url': video.video_url,
            'thumbnail': video.thumbnail_url,
            'duration': video.duration,
            'width': video.video_width,
            'height': video.video_height,
            'resolution': f"{video.video_width}x{video.video_height}" if video.video_width else None,
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
        - project_id: UUID (optional)

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
        return JsonResponse({'error': 'Missing required fields: filename, file_size, mime_type'}, status=400)

    # Convert file_size to int
    try:
        file_size = int(file_size)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid file_size'}, status=400)

    # Validate limits
    if content_type == 'video' and file_size > MAX_VIDEO_UPLOAD_SIZE:
        return JsonResponse({
            'error': f'File exceeds maximum video size ({MAX_VIDEO_UPLOAD_SIZE // (1024*1024)}MB)'
        }, status=400)
    elif content_type == 'image' and file_size > MAX_IMAGE_UPLOAD_SIZE:
        return JsonResponse({
            'error': f'File exceeds maximum image size ({MAX_IMAGE_UPLOAD_SIZE // (1024*1024)}MB)'
        }, status=400)
    elif content_type == 'audio' and file_size > MAX_AUDIO_UPLOAD_SIZE:
        return JsonResponse({
            'error': f'File exceeds maximum audio size ({MAX_AUDIO_UPLOAD_SIZE // (1024*1024)}MB)'
        }, status=400)

    # Calculate chunks
    chunk_size = UPLOAD_CHUNK_SIZE
    chunks_total = (file_size + chunk_size - 1) // chunk_size

    # Create temp directory for chunks
    upload_id = uuid.uuid4()
    temp_dir = Path(settings.MEDIA_ROOT) / 'uploads' / 'temp' / str(upload_id)
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Get project_id if provided
    project_id = data.get('project_id')

    # Create upload session
    session = UploadSession.objects.create(
        id=upload_id,
        user=request.user,
        filename=filename,
        file_size=file_size,
        mime_type=mime_type,
        content_type=content_type,
        chunk_size=chunk_size,
        chunks_total=chunks_total,
        temp_path=str(temp_dir),
        expires_at=timezone.now() + timedelta(hours=UPLOAD_SESSION_EXPIRY_HOURS),
        status='uploading',
        project_id=project_id if project_id else None,
    )

    logger.info(f"User {request.user.username} initialized chunked upload: {filename} ({file_size} bytes, {chunks_total} chunks)")

    return JsonResponse({
        'success': True,
        'upload_id': str(upload_id),
        'chunk_size': chunk_size,
        'chunks_total': chunks_total,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def chunked_upload_chunk(request, upload_id):
    """
    Upload a single chunk.

    POST /api/upload/chunked/<upload_id>/chunk/

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
    chunk_number_str = request.POST.get('chunk_number', '0')

    if not chunk:
        return JsonResponse({'error': 'No chunk data'}, status=400)

    try:
        chunk_number = int(chunk_number_str)
    except ValueError:
        return JsonResponse({'error': 'Invalid chunk_number'}, status=400)

    # Save chunk to temp directory
    chunk_path = Path(session.temp_path) / f"chunk_{chunk_number:06d}"
    with open(chunk_path, 'wb') as f:
        for part in chunk.chunks():
            f.write(part)

    # Update session
    session.chunks_received += 1
    session.bytes_received += chunk.size
    session.status = 'uploading'
    session.save()

    # Check if complete
    complete = session.chunks_received >= session.chunks_total

    if complete:
        # Trigger assembly in background via Celery
        from core.tasks import assemble_chunked_upload
        assemble_chunked_upload.delay(str(upload_id))
        session.status = 'processing'
        session.save()
        logger.info(f"Chunked upload {upload_id} complete, starting assembly")

    return JsonResponse({
        'success': True,
        'chunks_received': session.chunks_received,
        'chunks_total': session.chunks_total,
        'bytes_received': session.bytes_received,
        'progress_percent': session.progress_percent,
        'complete': complete,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chunked_upload_status(request, upload_id):
    """
    Get status of a chunked upload.

    GET /api/upload/chunked/<upload_id>/status/
    """
    try:
        session = UploadSession.objects.get(id=upload_id, user=request.user)
    except UploadSession.DoesNotExist:
        return JsonResponse({'error': 'Upload session not found'}, status=404)

    response = {
        'upload_id': str(session.id),
        'status': session.status,
        'filename': session.filename,
        'content_type': session.content_type,
        'chunks_received': session.chunks_received,
        'chunks_total': session.chunks_total,
        'bytes_received': session.bytes_received,
        'file_size': session.file_size,
        'progress_percent': session.progress_percent,
    }

    if session.status == 'completed' and session.result_id:
        response['result'] = {
            'content_type': session.result_content_type,
            'id': str(session.result_id),
        }
    elif session.status == 'failed':
        response['error'] = session.error_message

    return JsonResponse(response)


# =============================================================================
# Gallery Endpoints with Upload Support
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_uploads(request):
    """
    Get user's uploaded content.

    GET /api/upload/list/

    Query params:
        - content_type: 'image', 'video', or 'all' (default: 'all')
        - limit: Number of items (default: 50)
        - offset: Pagination offset (default: 0)
    """
    content_type = request.GET.get('content_type', 'all')
    limit = min(int(request.GET.get('limit', 50)), 100)
    offset = int(request.GET.get('offset', 0))

    items = []

    if content_type in ['all', 'image']:
        images = ImageHistory.objects.filter(
            user=request.user,
            source_type=MediaSourceType.UPLOADED
        ).order_by('-created_at')[offset:offset+limit]

        for img in images:
            items.append({
                'type': 'image',
                'id': str(img.id),
                'sequential_number': img.get_sequential_number(),
                'filename': img.original_filename or img.filename,
                'url': img.file_path,
                'thumbnail': img.thumbnail,
                'width': img.image_width,
                'height': img.image_height,
                'created_at': img.created_at.isoformat(),
            })

    if content_type in ['all', 'video']:
        videos = VideoHistory.objects.filter(
            user=request.user,
            source_type=MediaSourceType.UPLOADED
        ).order_by('-created_at')[offset:offset+limit]

        for vid in videos:
            items.append({
                'type': 'video',
                'id': str(vid.id),
                'sequential_number': vid.get_sequential_number(),
                'filename': vid.original_filename,
                'url': vid.video_url,
                'thumbnail': vid.thumbnail_url,
                'duration': vid.duration,
                'width': vid.video_width,
                'height': vid.video_height,
                'created_at': vid.created_at.isoformat(),
            })

    # Sort by created_at
    items.sort(key=lambda x: x['created_at'], reverse=True)

    return JsonResponse({
        'success': True,
        'items': items[:limit],
        'count': len(items),
    })


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
            logger.warning(f"ffprobe failed for {file_path}: {result.stderr}")
            return {}

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
                fps = float(num) / float(den) if float(den) != 0 else None
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


def _generate_image_thumbnail(image_record, uploaded_file):
    """Generate thumbnail for uploaded image."""
    try:
        from PIL import Image
        uploaded_file.seek(0)

        with Image.open(uploaded_file) as img:
            # Create thumbnail
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)

            # Convert to RGB if necessary (for JPEG)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Save thumbnail
            thumb_filename = f"thumb_{image_record.filename}"
            thumb_path = f"uploads/images/thumbnails/{thumb_filename}"

            from io import BytesIO
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)

            saved_path = default_storage.save(thumb_path, ContentFile(buffer.read()))
            image_record.thumbnail = default_storage.url(saved_path)
            image_record.save(update_fields=['thumbnail'])

    except Exception as e:
        logger.error(f"Failed to generate thumbnail: {e}")


def _generate_video_thumbnail(video_record, file_path):
    """Generate thumbnail from video first frame."""
    try:
        thumb_filename = f"thumb_{video_record.id}.jpg"
        thumb_dir = Path(settings.MEDIA_ROOT) / 'uploads' / 'videos' / 'thumbnails'
        thumb_dir.mkdir(parents=True, exist_ok=True)
        thumb_path = thumb_dir / thumb_filename

        cmd = [
            'ffmpeg', '-i', file_path,
            '-vf', 'thumbnail,scale=300:-1',
            '-frames:v', '1',
            '-y', str(thumb_path)
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)

        if thumb_path.exists():
            video_record.thumbnail_url = f"/media/uploads/videos/thumbnails/{thumb_filename}"
            video_record.save(update_fields=['thumbnail_url'])

    except Exception as e:
        logger.error(f"Failed to generate video thumbnail: {e}")
