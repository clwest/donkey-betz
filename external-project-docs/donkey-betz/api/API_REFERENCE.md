# DaVinci Resolve API Reference

## Authentication

All API endpoints require authentication using Django REST Framework's token authentication.

```bash
Authorization: Token your-auth-token
```

## Base URL

```
http://localhost:8001/api/davinci/
```

## Projects API

### List Projects

Get all projects for the authenticated user.

**Endpoint:** `GET /api/davinci/projects/`

**Query Parameters:**
- `status` (optional): Filter by status (created, importing, processing, completed, error)
- `template` (optional): Filter by template type
- `search` (optional): Search in project names and descriptions
- `ordering` (optional): Order by field (default: -created_at)

**Response:**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "My Project",
        "description": "Project description",
        "status": "completed",
        "template": "youtube",
        "progress_percentage": 100,
        "is_processing": false,
        "is_completed": true,
        "is_error": false,
        "timeline_count": 3,
        "render_job_count": 2,
        "obs_recordings_count": 5,
        "ai_images_count": 10,
        "ai_videos_count": 2,
        "created_at": "2025-01-31T10:00:00Z",
        "updated_at": "2025-01-31T11:00:00Z",
        "started_at": "2025-01-31T10:05:00Z",
        "completed_at": "2025-01-31T11:00:00Z",
        "error_message": null,
        "tags": ["tutorial", "product"]
    }
]
```

### Create Project

Create a new DaVinci Resolve project.

**Endpoint:** `POST /api/davinci/projects/`

**Request Body:**
```json
{
    "name": "Product Demo",
    "description": "Product demonstration video",
    "template": "youtube",
    "settings": {
        "timeline_resolution": "1920x1080",
        "timeline_framerate": "30"
    },
    "tags": ["product", "demo"],
    "obs_recording_ids": [1, 2, 3],
    "ai_image_ids": [10, 11],
    "ai_video_ids": [20]
}
```

**Response:** `201 Created`
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Product Demo",
    "status": "created",
    "progress_percentage": 0,
    "...": "..."
}
```

### Get Project Details

Get detailed information about a specific project.

**Endpoint:** `GET /api/davinci/projects/{id}/`

**Response:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Product Demo",
    "description": "Product demonstration video",
    "resolve_project_name": "Product_Demo_2025",
    "resolve_project_id": "12345",
    "template": "youtube",
    "settings": {...},
    "status": "completed",
    "progress_percentage": 100,
    "is_processing": false,
    "is_completed": true,
    "is_error": false,
    "timeline_count": 3,
    "render_job_count": 2,
    "project_file_path": "/path/to/project.drp",
    "output_directory": "/path/to/output",
    "metadata": {...},
    "tags": ["product", "demo"],
    "error_message": null,
    "retry_count": 0,
    "created_at": "2025-01-31T10:00:00Z",
    "updated_at": "2025-01-31T11:00:00Z",
    "started_at": "2025-01-31T10:05:00Z",
    "completed_at": "2025-01-31T11:00:00Z",
    "timelines": [...],
    "recent_render_jobs": [...],
    "obs_recordings": [...],
    "ai_generated_images": [...],
    "ai_generated_videos": [...]
}
```

### Start Project Processing

Start processing a created project.

**Endpoint:** `POST /api/davinci/projects/{id}/start/`

**Response:** `200 OK`
```json
{
    "success": true,
    "message": "Project processing started",
    "project_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Cancel Project

Cancel a processing project.

**Endpoint:** `POST /api/davinci/projects/{id}/cancel/`

**Response:** `200 OK`
```json
{
    "success": true,
    "message": "Project cancelled"
}
```

### Execute Pipeline

Execute a complete automated pipeline for the project.

**Endpoint:** `POST /api/davinci/projects/{id}/execute_pipeline/`

**Request Body:**
```json
{
    "pipeline_type": "complete",
    "content_sources": ["obs_recordings", "ai_images", "ai_videos"],
    "ai_processing": {
        "enable_content_analysis": true,
        "enable_ai_editing": true,
        "editing_style": "dynamic",
        "enable_color_grading": true,
        "color_profile": "cinematic"
    },
    "output_settings": {
        "render_preset": "youtube_4k",
        "upload_to_youtube": true,
        "youtube_metadata": {
            "title": "My Video",
            "description": "Description",
            "tags": ["tag1", "tag2"],
            "privacy_status": "private"
        }
    }
}
```

**Response:** `200 OK`
```json
{
    "success": true,
    "pipeline_id": "pipeline_123",
    "message": "Pipeline execution started"
}
```

### Get Pipeline Status

Get the status of a running pipeline.

**Endpoint:** `GET /api/davinci/projects/{id}/pipeline_status/?pipeline_id={pipeline_id}`

**Response:**
```json
{
    "pipeline_id": "pipeline_123",
    "pipeline_type": "complete",
    "started_at": 1706698800.0,
    "overall_status": "processing",
    "progress_percentage": 45.5,
    "current_step": "ai_editing",
    "steps": [
        {
            "id": "import",
            "name": "Import Media",
            "status": "completed",
            "progress": 100,
            "started_at": 1706698800.0,
            "completed_at": 1706698900.0
        },
        {
            "id": "ai_editing",
            "name": "AI Editing",
            "status": "processing",
            "progress": 45,
            "started_at": 1706699000.0
        }
    ]
}
```

### Get Project Statistics

Get statistics for all user projects.

**Endpoint:** `GET /api/davinci/projects/statistics/`

**Response:**
```json
{
    "total_projects": 25,
    "completed_projects": 20,
    "active_projects": 3,
    "error_projects": 2,
    "recent_projects": [...],
    "templates_used": [
        {"template": "youtube", "count": 15},
        {"template": "instagram", "count": 10}
    ]
}
```

## Timelines API

### List Timelines

Get all timelines.

**Endpoint:** `GET /api/davinci/timelines/`

**Query Parameters:**
- `project` (optional): Filter by project ID
- `is_master_timeline` (optional): Filter master timelines only

### Create Timeline

Create a new timeline.

**Endpoint:** `POST /api/davinci/timelines/`

**Request Body:**
```json
{
    "project": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Main Edit",
    "description": "Main timeline for the project",
    "resolution_width": 1920,
    "resolution_height": 1080,
    "frame_rate": "30",
    "duration_frames": 900,
    "order": 1,
    "is_master_timeline": true
}
```

### Update Timeline Arrangement

Update the clip arrangement in a timeline.

**Endpoint:** `POST /api/davinci/timelines/{id}/update_arrangement/`

**Request Body:**
```json
{
    "arrangement_data": {
        "clips": [
            {
                "id": "clip_1",
                "start_frame": 0,
                "end_frame": 150,
                "track": 1
            }
        ]
    }
}
```

### Add Timeline Marker

Add a marker to the timeline.

**Endpoint:** `POST /api/davinci/timelines/{id}/add_marker/`

**Request Body:**
```json
{
    "frame": 300,
    "name": "Scene Change",
    "note": "Transition to product close-up"
}
```

### Export EDL

Export timeline as EDL (Edit Decision List).

**Endpoint:** `GET /api/davinci/timelines/{id}/export_edl/`

**Response:**
```json
{
    "edl_content": "TITLE: Main Edit\n001  001      V     C        00:00:00:00 00:00:05:00...",
    "filename": "main_edit.edl"
}
```

## Render Jobs API

### List Render Jobs

Get all render jobs.

**Endpoint:** `GET /api/davinci/render-jobs/`

**Query Parameters:**
- `project` (optional): Filter by project ID
- `status` (optional): Filter by status
- `youtube_upload_enabled` (optional): Filter YouTube-enabled jobs

### Create Render Job

Create a new render job.

**Endpoint:** `POST /api/davinci/render-jobs/`

**Request Body:**
```json
{
    "project": "550e8400-e29b-41d4-a716-446655440000",
    "timeline": "660e9500-e29b-41d4-a716-446655440001",
    "name": "YouTube 4K Export",
    "render_preset": "youtube_4k",
    "output_format": "mp4",
    "render_options": {
        "codec": "h265",
        "bitrate": 40000000,
        "audio_codec": "aac",
        "audio_bitrate": 320000
    },
    "youtube_upload_enabled": true,
    "youtube_metadata": {
        "title": "My Video Title",
        "description": "Video description",
        "tags": ["tag1", "tag2"],
        "privacy_status": "private"
    },
    "priority": 5
}
```

### Start Render Job

Start a queued render job.

**Endpoint:** `POST /api/davinci/render-jobs/{id}/start/`

**Response:** `200 OK`
```json
{
    "success": true,
    "message": "Render job started"
}
```

### Cancel Render Job

Cancel a running render job.

**Endpoint:** `POST /api/davinci/render-jobs/{id}/cancel/`

**Response:** `200 OK`
```json
{
    "success": true,
    "message": "Render job cancelled"
}
```

### Get Render Progress

Get real-time render progress.

**Endpoint:** `GET /api/davinci/render-jobs/{id}/progress/`

**Response:**
```json
{
    "render_job_id": "770e9600-e29b-41d4-a716-446655440002",
    "status": "rendering",
    "progress_percentage": 67,
    "estimated_completion_time": 1706699500.0,
    "current_frame": 670,
    "total_frames": 1000,
    "error_message": null
}
```

### Upload to YouTube

Upload completed render to YouTube.

**Endpoint:** `POST /api/davinci/render-jobs/{id}/upload_to_youtube/`

**Request Body (optional):**
```json
{
    "title": "Override Title",
    "description": "Override Description",
    "privacy_status": "public"
}
```

**Response:** `200 OK`
```json
{
    "success": true,
    "youtube_video_id": "dQw4w9WgXcQ",
    "video_url": "https://youtube.com/watch?v=dQw4w9WgXcQ"
}
```

## Color Profiles API

### List Color Profiles

Get all color profiles.

**Endpoint:** `GET /api/davinci/color-profiles/`

**Query Parameters:**
- `is_public` (optional): Filter public profiles
- `profile_type` (optional): Filter by type

### Create Color Profile

Create a new color profile.

**Endpoint:** `POST /api/davinci/color-profiles/`

**Request Body:**
```json
{
    "name": "Cinematic Look",
    "description": "High contrast cinematic color grade",
    "profile_type": "cinematic",
    "lift": [0.0, 0.0, 0.0, 0.0],
    "gamma": [1.0, 1.0, 1.0, 1.0],
    "gain": [1.2, 1.1, 1.0, 1.1],
    "contrast": 1.2,
    "saturation": 0.9,
    "temperature": 6500,
    "tint": 0,
    "color_settings": {
        "highlight_recovery": true,
        "shadow_detail": 0.3
    },
    "is_public": true,
    "tags": ["cinematic", "dramatic"]
}
```

## Editing Profiles API

### List Editing Profiles

Get all editing profiles.

**Endpoint:** `GET /api/davinci/editing-profiles/`

### Create Editing Profile

Create a new editing profile.

**Endpoint:** `POST /api/davinci/editing-profiles/`

**Request Body:**
```json
{
    "name": "Fast Cuts",
    "description": "Quick cutting style for action sequences",
    "editing_style": "dynamic",
    "average_clip_duration": 2.5,
    "transition_style": "cut",
    "music_sync_enabled": true,
    "editing_rules": {
        "remove_silence": true,
        "minimum_clip_duration": 0.5,
        "maximum_clip_duration": 5.0
    },
    "is_public": true,
    "tags": ["action", "fast-paced"]
}
```

## Advanced API Endpoints (Phase 8)

### Workflow Templates

#### List Templates
**Endpoint:** `GET /api/davinci/advanced/workflow-templates/`

**Response:**
```json
[
    {
        "id": "youtube_tutorial",
        "name": "YouTube Tutorial",
        "description": "Optimized for educational content"
    }
]
```

#### Create Custom Template
**Endpoint:** `POST /api/davinci/advanced/workflow-templates/create_custom/`

**Request:**
```json
{
    "name": "My Custom Workflow",
    "base_template": "youtube_tutorial",
    "customizations": {
        "ai_processing": {
            "enable_color_grading": false
        }
    }
}
```

### Performance Analytics

#### Render Statistics
**Endpoint:** `GET /api/davinci/advanced/analytics/render_stats/?days=30`

#### Full Performance Report
**Endpoint:** `GET /api/davinci/advanced/analytics/full_report/`

### Error Recovery

#### Diagnose Failure
**Endpoint:** `POST /api/davinci/advanced/error-recovery/diagnose_failure/`

**Request:**
```json
{
    "render_job_id": "uuid"
}
```

**Response:**
```json
{
    "render_job_id": "uuid",
    "error_message": "GPU memory allocation failed",
    "possible_causes": ["Insufficient memory"],
    "suggested_actions": ["Reduce render resolution", "Close other applications"]
}
```

### Extended AI

#### Multi-Version Edits
**Endpoint:** `POST /api/davinci/advanced/ai-extended/multi_version_edits/`

**Request:**
```json
{
    "timeline_id": "uuid",
    "versions": [
        {
            "name": "YouTube Long",
            "duration": 600,
            "style": "tutorial",
            "platform": "youtube"
        }
    ]
}
```

## WebSocket API

### Connection

Connect to the WebSocket endpoint:

```javascript
const ws = new WebSocket('ws://localhost:8001/ws/davinci/');
```

### Message Format

All messages use JSON format:

```json
{
    "type": "message_type",
    "data": {}
}
```

### Client → Server Messages

#### Subscribe to Render Progress
```json
{
    "type": "subscribe_render_progress",
    "render_job_id": "770e9600-e29b-41d4-a716-446655440002"
}
```

#### Subscribe to Pipeline Status
```json
{
    "type": "subscribe_pipeline_status",
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "pipeline_id": "pipeline_123"
}
```

#### Get Project Status
```json
{
    "type": "get_project_status",
    "project_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Server → Client Messages

#### Render Progress Update
```json
{
    "type": "render_progress",
    "render_job_id": "770e9600-e29b-41d4-a716-446655440002",
    "status": "rendering",
    "progress_percentage": 67,
    "estimated_completion_time": 1706699500.0,
    "current_frame": 670,
    "total_frames": 1000
}
```

#### Pipeline Status Update
```json
{
    "type": "pipeline_status",
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "pipeline_id": "pipeline_123",
    "overall_status": "processing",
    "progress_percentage": 45.5,
    "current_step": "ai_editing",
    "steps": [...]
}
```

#### Project Status Update
```json
{
    "type": "project_status",
    "project": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "processing",
        "progress_percentage": 75,
        "...": "..."
    }
}
```

#### Notification
```json
{
    "type": "notification",
    "level": "info",
    "message": "Render job completed successfully",
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": 1706699500.0
}
```

## Error Responses

All endpoints return consistent error responses:

### 400 Bad Request
```json
{
    "error": "Invalid request data",
    "details": {
        "field_name": ["Error message"]
    }
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error",
    "message": "An unexpected error occurred"
}
```

## Rate Limiting

API endpoints are rate-limited:
- Anonymous requests: 100/hour
- Authenticated requests: 1000/hour
- WebSocket connections: 10 concurrent per user

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1706700000
```

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response:**
```json
{
    "count": 150,
    "next": "http://localhost:8001/api/davinci/projects/?page=2",
    "previous": null,
    "results": [...]
}
```