# Session 451: User Video Upload Feature

**Date:** December 14, 2025
**Status:** COMPLETE
**Impact:** ALL 4 PRE-MARKET ITEMS NOW DONE!

---

## Overview

Implemented complete user upload functionality allowing users to inject their own videos and images into the AI content pipeline. This completes the final pre-market item from the Golden Goose Strategy.

## What Was Built

### 1. Backend Models & Storage

**File:** `content/models.py`

Added `MediaSourceType` choices class:
```python
class MediaSourceType(models.TextChoices):
    GENERATED = 'generated', 'AI Generated'
    UPLOADED = 'uploaded', 'User Uploaded'
    IMPORTED = 'imported', 'External Import'
    EDITED = 'edited', 'Edited Version'
```

Extended `ImageHistory` with upload fields:
- `source_type` - Track if AI-generated or uploaded
- `original_file` - FileField for uploaded images
- `original_filename` - Original file name
- `mime_type` - MIME type for validation

Extended `VideoHistory` with upload fields:
- `source_type` - Track if AI-generated or uploaded
- `video_file` - FileField for uploaded videos
- `original_filename` - Original file name
- `mime_type` - MIME type
- `fps` - Frames per second (extracted from video)
- `codec` - Video codec (extracted from video)

Created `UploadSession` model for chunked uploads:
- Supports files up to 500MB via chunked upload
- Tracks chunk progress (uploaded_chunks vs total_chunks)
- Status tracking (pending/uploading/processing/complete/failed/expired)
- Auto-expiration after 24 hours

### 2. API Endpoints

**File:** `core/views_upload.py` (NEW - ~500 lines)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload/image/` | POST | Simple image upload (<50MB) |
| `/api/upload/video/` | POST | Simple video upload (<50MB) |
| `/api/upload/chunked/init/` | POST | Initialize chunked upload |
| `/api/upload/chunked/<id>/chunk/` | POST | Upload individual chunk |
| `/api/upload/chunked/<id>/status/` | GET | Check upload progress |
| `/api/upload/list/` | GET | List user's uploaded content |

Features:
- ffprobe for video metadata extraction
- PIL/Pillow for image processing
- Automatic thumbnail generation
- MIME type detection with fallbacks

### 3. Celery Tasks

**File:** `core/tasks.py`

Added two new tasks:
- `assemble_chunked_upload(upload_id)` - Assembles chunks into final file, creates ImageHistory/VideoHistory record
- `cleanup_expired_uploads()` - Periodic task to clean abandoned uploads

### 4. Frontend UI Panel

**File:** `ai_core/templates/components/panels/upload_panel.html` (NEW - 564 lines)

Features:
- Drag-and-drop upload zone with visual feedback
- Progress tracking for uploads
- Grid display of uploaded content
- Filter by type (images/videos/all)
- MediaUploader JavaScript class handling both simple and chunked uploads

Added to navigation:
- New "Upload" tab in `studio_tabs.html`
- Panel included in main template

### 5. AISeriesWorkflowAgent Integration

**File:** `core/agents/ai_series_workflow_agent.py`

Added two new tools:

1. `list_uploaded_content` - List available user uploads
   - Filter by content_type (video/image/all)
   - Returns metadata (filename, duration, resolution, etc.)

2. `use_uploaded_content` - Assign uploads to episodes
   - content_type: video or image
   - content_id: ID of the upload
   - episode_number: Target episode (0 = apply globally)
   - usage: background, main_video, character_reference, scene_reference

Modified episode generation:
- Step 1 (Images): Checks for uploaded image references before generating
- Step 4 (Video): Checks for uploaded video before generating

Updated system prompt to document upload capabilities.

## Files Changed/Created

| File | Action | Lines |
|------|--------|-------|
| `content/models.py` | Modified | +60 |
| `content/migrations/0036_session_451_user_upload_support.py` | Created | ~100 |
| `core/views_upload.py` | Created | ~500 |
| `core/tasks.py` | Modified | +150 |
| `core/urls.py` | Modified | +10 |
| `ai_core/templates/components/panels/upload_panel.html` | Created | 564 |
| `ai_core/templates/components/navigation/studio_tabs.html` | Modified | +6 |
| `ai_core/templates/ai_image_studio.html` | Modified | +10 |
| `core/agents/ai_series_workflow_agent.py` | Modified | +200 |

## Usage Examples

### Simple Upload (Frontend)
1. Navigate to AI Studio
2. Click "Upload" tab
3. Drag-and-drop files or click to browse
4. Wait for upload to complete
5. Files appear in gallery grid

### Chunked Upload (Large Files)
1. Initialize: `POST /api/upload/chunked/init/` with filename, size, chunks
2. Upload chunks: `POST /api/upload/chunked/<id>/chunk/` with chunk_number, file
3. Check status: `GET /api/upload/chunked/<id>/status/`
4. Celery assembles when complete

### Using in AI Series

Via Discord or Web:
```
User: "Create a 3-episode series about my product launch"

AI: "First, let me check your uploaded content..."
[Calls list_uploaded_content]

AI: "I see you have a product demo video. Would you like me to use it in episode 1?"
[Calls use_uploaded_content with video_id]

AI: "Now generating the series with your video..."
[Generates episodes, using uploaded video instead of AI-generated]
```

## Configuration

**File Size Limits:**
- Simple uploads: 50MB max
- Chunked uploads: 500MB max
- Chunk size: 5MB

**Supported Formats:**
- Images: jpg, jpeg, png, gif, webp
- Videos: mp4, mov, avi, mkv, webm

**Storage:**
- Images: `media/uploads/images/`
- Videos: `media/uploads/videos/`
- Thumbnails: Generated automatically

## What's Next

With all 4 pre-market items complete:
1. ~~Stripe Integration~~ - Done (Session 450)
2. ~~AISeriesWorkflowAgent~~ - Done (Sessions 445-448)
3. ~~User Video Upload~~ - Done (Session 451)
4. ~~Learning Loops~~ - Done (Session 449)

**GO TO MARKET IS READY!**

See `docs/GOLDEN_GOOSE_STRATEGY.md` for launch plan.

## Testing

To test uploads:
```bash
# Start server
make start

# Navigate to AI Studio
open http://localhost:8000/ai-studio/

# Click Upload tab, drag files
```

To test API directly:
```bash
# Simple image upload
curl -X POST http://localhost:8000/api/upload/image/ \
  -H "Authorization: Bearer <token>" \
  -F "file=@test_image.jpg"

# List uploads
curl http://localhost:8000/api/upload/list/ \
  -H "Authorization: Bearer <token>"
```
