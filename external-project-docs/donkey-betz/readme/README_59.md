# DaVinci Resolve Integration Documentation

## Overview

The DaVinci Resolve integration provides a comprehensive Python API for automating video editing workflows within the move_that_ass platform. This integration enables AI-powered video editing, automated rendering, and direct YouTube publishing.

## Table of Contents

1. [Architecture](#architecture)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Core Services](#core-services)
5. [API Reference](#api-reference)
6. [WebSocket Integration](#websocket-integration)
7. [AI Features](#ai-features)
8. [Performance Optimization](#performance-optimization)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
├─────────────────────────────────────────────────────────────┤
│                  WebSocket Layer (Django Channels)           │
├─────────────────────────────────────────────────────────────┤
│                    REST API (Django REST Framework)          │
├─────────────────────────────────────────────────────────────┤
│                      Service Layer                          │
│  ┌─────────────┬──────────────┬────────────┬─────────────┐ │
│  │ProjectService│TimelineService│RenderService│YouTubeService│ │
│  └─────────────┴──────────────┴────────────┴─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   DaVinci Resolve Python API                 │
├─────────────────────────────────────────────────────────────┤
│                    Database (PostgreSQL)                     │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Import**: OBS recordings, AI-generated content → DaVinci project
2. **Edit**: AI-powered timeline creation and editing
3. **Enhance**: Color grading and effects application
4. **Render**: Multiple format presets for different platforms
5. **Publish**: Direct upload to YouTube with metadata

## Advanced Features (Phase 8)

### Workflow Templates
- **YouTube Tutorial**: Optimized for educational content
- **Social Media Reel**: Fast-paced content for Instagram/TikTok
- **Documentary**: Long-form content with narrative structure
- **Podcast Video**: Multi-camera podcast with audio focus
- **Music Video**: Beat-synced editing for music content

### Performance Monitoring
- Real-time system resource monitoring
- Render queue analytics
- Pipeline execution tracking
- Alert management system
- Comprehensive dashboard

### Error Recovery
- Automatic failure diagnosis
- Recovery checkpoints
- Smart retry with adjusted settings
- Detailed error analysis

### Extended AI Capabilities
- Multi-version edit generation
- Audience engagement prediction
- Smart thumbnail generation
- Platform-specific optimizations

## Installation

### Prerequisites

1. **DaVinci Resolve Studio** (v18.0 or higher)
2. **Python 3.9+** with DaVinci Resolve Python API enabled
3. **PostgreSQL** database
4. **Redis** for caching and Celery
5. **YouTube Data API v3** credentials

### Setup Steps

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Run database migrations
python manage.py migrate davinci_resolve

# 3. Create database indexes
python manage.py optimize_davinci_db

# 4. Configure DaVinci Resolve Python API
export RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
export PYTHONPATH="${PYTHONPATH}:${RESOLVE_SCRIPT_API}/Modules/"

# 5. Test connection
python manage.py test_davinci_connection
```

## Configuration

### Django Settings

```python
# settings.py

DAVINCI_RESOLVE = {
    'PROJECT_PATH': '/path/to/davinci/projects',
    'MEDIA_POOL_PATH': '/path/to/media/pool',
    'RENDER_OUTPUT_PATH': '/path/to/render/output',
    'CACHE_TIMEOUT': 3600,
    'MAX_CONCURRENT_RENDERS': 3,
    'DEFAULT_FRAME_RATE': '30',
    'DEFAULT_RESOLUTION': '1920x1080'
}

# YouTube configuration
YOUTUBE_API = {
    'CLIENT_ID': 'your-client-id',
    'CLIENT_SECRET': 'your-client-secret',
    'REDIRECT_URI': 'http://localhost:8000/api/youtube/callback',
    'SCOPES': ['https://www.googleapis.com/auth/youtube.upload']
}
```

### Environment Variables

```bash
# .env file
DAVINCI_RESOLVE_PATH=/Applications/DaVinci Resolve/DaVinci Resolve.app
DAVINCI_PROJECT_DB=/Users/Shared/DaVinci Resolve/Projects
YOUTUBE_API_KEY=your-api-key
```

## Core Services

### ProjectService

Manages DaVinci Resolve projects and media pools.

```python
from davinci_resolve.services import ProjectService

# Create a new project
service = ProjectService(user=request.user)
project = service.create_project(
    name="My Video Project",
    template="youtube",
    settings={
        'timeline_resolution': '1920x1080',
        'timeline_framerate': '30'
    }
)

# Import media
service.import_media_to_project(
    project_id=project.id,
    media_paths=['/path/to/video1.mp4', '/path/to/video2.mp4'],
    target_bin='Imported Media'
)
```

### TimelineService

Creates and manages timelines with AI assistance.

```python
from davinci_resolve.services import TimelineService

service = TimelineService(project_id)
timeline = service.create_timeline_from_sources(
    name="Main Edit",
    source_clips=['clip1.mp4', 'clip2.mp4'],
    ai_arrange=True,
    music_sync=True
)
```

### RenderingService

Handles render job creation and monitoring.

```python
from davinci_resolve.services import RenderingService

service = RenderingService(project_id)
render_job = service.create_render_job(
    timeline_id=timeline.id,
    render_preset='youtube_4k',
    quality_settings={
        'codec': 'h265',
        'bitrate': 40000000
    }
)

# Monitor progress
progress = service.get_render_progress(render_job.id)
print(f"Rendering: {progress['progress_percentage']}%")
```

### YouTubeIntegrationService

Uploads rendered videos to YouTube.

```python
from davinci_resolve.services import YouTubeIntegrationService

service = YouTubeIntegrationService(user=request.user)
result = service.upload_rendered_video(
    render_job_id=render_job.id,
    upload_options={
        'title': 'My Amazing Video',
        'description': 'Created with AI assistance',
        'tags': ['ai', 'automated', 'davinci'],
        'privacy_status': 'private'
    }
)
```

## API Reference

### Endpoints

#### Projects

- `GET /api/davinci/projects/` - List user projects
- `POST /api/davinci/projects/` - Create new project
- `GET /api/davinci/projects/{id}/` - Get project details
- `POST /api/davinci/projects/{id}/start/` - Start project processing
- `POST /api/davinci/projects/{id}/cancel/` - Cancel project
- `POST /api/davinci/projects/{id}/execute_pipeline/` - Execute complete pipeline
- `GET /api/davinci/projects/statistics/` - Get user statistics

#### Timelines

- `GET /api/davinci/timelines/` - List timelines
- `POST /api/davinci/timelines/` - Create timeline
- `GET /api/davinci/timelines/{id}/` - Get timeline details
- `POST /api/davinci/timelines/{id}/update_arrangement/` - Update clip arrangement
- `POST /api/davinci/timelines/{id}/add_marker/` - Add timeline marker
- `GET /api/davinci/timelines/{id}/export_edl/` - Export EDL

#### Render Jobs

- `GET /api/davinci/render-jobs/` - List render jobs
- `POST /api/davinci/render-jobs/` - Create render job
- `GET /api/davinci/render-jobs/{id}/` - Get render job details
- `POST /api/davinci/render-jobs/{id}/start/` - Start rendering
- `POST /api/davinci/render-jobs/{id}/cancel/` - Cancel render
- `GET /api/davinci/render-jobs/{id}/progress/` - Get render progress
- `POST /api/davinci/render-jobs/{id}/upload_to_youtube/` - Upload to YouTube

### Request/Response Examples

#### Create Project

```bash
POST /api/davinci/projects/
Content-Type: application/json
Authorization: Token your-auth-token

{
    "name": "Product Demo Video",
    "description": "AI-enhanced product demonstration",
    "template": "youtube",
    "tags": ["product", "demo", "marketing"],
    "obs_recording_ids": [1, 2, 3],
    "ai_image_ids": [10, 11, 12]
}
```

Response:
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Product Demo Video",
    "status": "created",
    "progress_percentage": 0,
    "timeline_count": 0,
    "render_job_count": 0,
    "created_at": "2025-01-31T10:00:00Z"
}
```

## WebSocket Integration

### Connection

```javascript
// Frontend WebSocket connection
const ws = new WebSocket('ws://localhost:8001/ws/davinci/');

ws.onopen = () => {
    console.log('Connected to DaVinci Resolve WebSocket');
    
    // Subscribe to render progress
    ws.send(JSON.stringify({
        type: 'subscribe_render_progress',
        render_job_id: 'job-uuid'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'render_progress':
            updateProgressBar(data.progress_percentage);
            break;
        case 'pipeline_status':
            updatePipelineUI(data.steps);
            break;
        case 'notification':
            showNotification(data.message);
            break;
    }
};
```

### Message Types

- `subscribe_render_progress` - Subscribe to render job updates
- `subscribe_pipeline_status` - Subscribe to pipeline execution updates
- `get_project_status` - Get current project status
- `render_progress` - Render progress update (server → client)
- `pipeline_status` - Pipeline status update (server → client)
- `notification` - General notifications (server → client)

## AI Features

### Content Analysis

The system analyzes video content to make intelligent editing decisions:

```python
from davinci_resolve.services import ContentAnalysisService

analyzer = ContentAnalysisService()
analysis = analyzer.analyze_media_files(media_paths)

# Returns:
{
    'scene_changes': [...],
    'face_detection': [...],
    'motion_intensity': {...},
    'audio_analysis': {...},
    'recommended_cuts': [...]
}
```

### AI-Powered Editing

```python
from davinci_resolve.services import AIEditingService

editor = AIEditingService()
editing_decisions = editor.generate_edit_decisions(
    content_analysis=analysis,
    style='dynamic',
    target_duration=60
)
```

### Automated Color Grading

```python
from davinci_resolve.services import ColorGradingService

grader = ColorGradingService()
color_profile = grader.analyze_and_grade(
    timeline_id=timeline.id,
    style='cinematic',
    reference_image='/path/to/reference.jpg'
)
```

## Performance Optimization

### Query Optimization

```python
from davinci_resolve.optimizations import QueryOptimizer

# Get optimized queryset with prefetched data
projects = QueryOptimizer.get_optimized_project_queryset(user=request.user)
```

### Caching

```python
from davinci_resolve.optimizations import CacheManager, cached_result

# Cache project data
CacheManager.cache_project_data(project_id, project_data)

# Use cached decorator
@cached_result(timeout=3600)
def expensive_operation():
    # This result will be cached for 1 hour
    return compute_something()
```

### Batch Operations

```python
from davinci_resolve.optimizations import BatchOperationManager

# Bulk create timelines
timelines = BatchOperationManager.bulk_create_timelines(
    project_id=project.id,
    timeline_data=[...]
)

# Process renders in parallel
BatchOperationManager.batch_process_renders(
    render_jobs=jobs,
    operation='start'
)
```

### Database Optimization

```bash
# Run optimization command
python manage.py optimize_davinci_db

# Analyze performance
python manage.py optimize_davinci_db --analyze

# Clear caches
python manage.py optimize_davinci_db --clear-cache
```

## Testing

### Running Tests

```bash
# Run all DaVinci Resolve tests
python manage.py test davinci_resolve

# Run specific test module
python manage.py test davinci_resolve.tests.test_services

# Run with coverage
coverage run --source='davinci_resolve' manage.py test davinci_resolve
coverage report
```

### Test Categories

1. **Unit Tests**: Model methods, service functions
2. **Integration Tests**: Service interactions, API endpoints
3. **WebSocket Tests**: Real-time communication
4. **Performance Tests**: Query optimization, batch operations

### Example Test

```python
from django.test import TestCase
from davinci_resolve.services import ProjectService

class ProjectServiceTest(TestCase):
    def test_create_project(self):
        service = ProjectService(user=self.user)
        project = service.create_project(
            name="Test Project",
            template="default"
        )
        
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.status, "created")
```

## Troubleshooting

### Common Issues

#### DaVinci Resolve Connection Failed

```python
# Check connection
from davinci_resolve.services import ResolveConnectionService

conn = ResolveConnectionService()
resolve = conn.connect()
if not resolve:
    print("Failed to connect to DaVinci Resolve")
    print("Make sure DaVinci Resolve is running")
```

#### Render Job Stuck

```python
# Reset stuck render job
from davinci_resolve.models import DaVinciRenderJob

job = DaVinciRenderJob.objects.get(id=job_id)
job.status = 'failed'
job.error_message = 'Manually reset due to stuck state'
job.save()
```

#### YouTube Upload Failed

```python
# Check YouTube credentials
from davinci_resolve.services import YouTubeIntegrationService

service = YouTubeIntegrationService(user=user)
if not service.youtube_service:
    print("YouTube authentication required")
    print(f"Visit: {service.get_auth_url()}")
```

### Debug Mode

Enable debug logging:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'davinci_resolve.log',
        },
    },
    'loggers': {
        'davinci_resolve': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Performance Monitoring

```python
from davinci_resolve.optimizations import PerformanceMonitor

@PerformanceMonitor.measure_execution_time
@PerformanceMonitor.log_database_queries
def slow_operation():
    # This will log execution time and query count
    pass
```

## Best Practices

1. **Always use batch operations** for multiple items
2. **Cache frequently accessed data** (projects, profiles)
3. **Prefetch related objects** to avoid N+1 queries
4. **Use WebSockets** for real-time updates
5. **Implement proper error handling** in pipeline operations
6. **Monitor render queue** to prevent overload
7. **Clean up temporary files** after rendering
8. **Use appropriate render presets** for target platforms

## Support

For issues or questions:
1. Check the [troubleshooting guide](#troubleshooting)
2. Review the [API documentation](#api-reference)
3. Contact the development team

---

*Last updated: January 31, 2025*