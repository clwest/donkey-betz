# DaVinci Resolve Integration Guide

This guide covers how to integrate the DaVinci Resolve functionality into your applications and workflows.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Frontend Integration](#frontend-integration)
3. [Backend Integration](#backend-integration)
4. [Workflow Examples](#workflow-examples)
5. [AI Features Integration](#ai-features-integration)
6. [Performance Best Practices](#performance-best-practices)
7. [Security Considerations](#security-considerations)

## Quick Start

### Basic Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
npm install @donkey-betz/davinci-client
```

2. **Configure Environment**
```bash
# .env
DAVINCI_RESOLVE_PATH=/Applications/DaVinci Resolve/DaVinci Resolve.app
YOUTUBE_CLIENT_ID=your-client-id
YOUTUBE_CLIENT_SECRET=your-client-secret
```

3. **Run Migrations**
```bash
python manage.py migrate davinci_resolve
python manage.py optimize_davinci_db
```

### Simple Example

```python
from davinci_resolve.services import PipelineOrchestratorService

# Create and execute a complete pipeline
orchestrator = PipelineOrchestratorService(project_id)
result = orchestrator.execute_complete_pipeline({
    'pipeline_type': 'complete',
    'content_sources': ['obs_recordings'],
    'ai_processing': {
        'enable_content_analysis': True,
        'enable_ai_editing': True,
        'enable_color_grading': True
    },
    'output_settings': {
        'render_preset': 'youtube_hd',
        'upload_to_youtube': True
    }
})
```

## Frontend Integration

### React Components

#### Project Manager Component

```jsx
import React, { useEffect, useState } from 'react';
import { DaVinciAPI } from '@donkey-betz/davinci-client';

const ProjectManager = () => {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        loadProjects();
    }, []);
    
    const loadProjects = async () => {
        try {
            const data = await DaVinciAPI.projects.list();
            setProjects(data);
        } catch (error) {
            console.error('Failed to load projects:', error);
        } finally {
            setLoading(false);
        }
    };
    
    const createProject = async (projectData) => {
        try {
            const newProject = await DaVinciAPI.projects.create(projectData);
            setProjects([newProject, ...projects]);
            
            // Start pipeline execution
            await DaVinciAPI.projects.executePipeline(newProject.id, {
                pipeline_type: 'complete',
                ai_processing: { enable_all: true }
            });
        } catch (error) {
            console.error('Failed to create project:', error);
        }
    };
    
    return (
        <div className="project-manager">
            {/* UI components */}
        </div>
    );
};
```

#### Real-time Progress Monitor

```jsx
import React, { useEffect, useState } from 'react';
import { DaVinciWebSocket } from '@donkey-betz/davinci-client';

const ProgressMonitor = ({ renderJobId }) => {
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState('pending');
    
    useEffect(() => {
        const ws = new DaVinciWebSocket();
        
        ws.connect();
        ws.subscribeToRenderProgress(renderJobId);
        
        ws.on('render_progress', (data) => {
            setProgress(data.progress_percentage);
            setStatus(data.status);
        });
        
        return () => ws.disconnect();
    }, [renderJobId]);
    
    return (
        <div className="progress-monitor">
            <div className="progress-bar">
                <div 
                    className="progress-fill" 
                    style={{ width: `${progress}%` }}
                />
            </div>
            <span>{status}: {progress}%</span>
        </div>
    );
};
```

### TypeScript Types

```typescript
// types/davinci.ts
export interface DaVinciProject {
    id: string;
    name: string;
    description: string;
    status: ProjectStatus;
    progress_percentage: number;
    timeline_count: number;
    render_job_count: number;
    created_at: string;
    updated_at: string;
}

export enum ProjectStatus {
    CREATED = 'created',
    IMPORTING = 'importing',
    PROCESSING = 'processing',
    RENDERING = 'rendering',
    COMPLETED = 'completed',
    ERROR = 'error'
}

export interface PipelineConfig {
    pipeline_type: 'complete' | 'ai_enhanced' | 'batch_processing';
    content_sources: ContentSource[];
    ai_processing: AIProcessingOptions;
    output_settings: OutputSettings;
}

export interface RenderProgress {
    render_job_id: string;
    status: string;
    progress_percentage: number;
    estimated_completion_time?: number;
    current_frame?: number;
    total_frames?: number;
}
```

### WebSocket Client

```javascript
// services/davinciWebSocket.js
class DaVinciWebSocketClient {
    constructor(url = 'ws://localhost:8001/ws/davinci/') {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.listeners = {};
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('Connected to DaVinci WebSocket');
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.emit(data.type, data);
        };
        
        this.ws.onclose = () => {
            this.reconnect();
        };
    }
    
    reconnect() {
        if (this.reconnectAttempts < 5) {
            setTimeout(() => {
                this.reconnectAttempts++;
                this.connect();
            }, Math.pow(2, this.reconnectAttempts) * 1000);
        }
    }
    
    send(type, data) {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, ...data }));
        }
    }
    
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }
    
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }
    
    subscribeToRenderProgress(renderJobId) {
        this.send('subscribe_render_progress', { render_job_id: renderJobId });
    }
    
    subscribeToPipelineStatus(projectId, pipelineId) {
        this.send('subscribe_pipeline_status', { 
            project_id: projectId,
            pipeline_id: pipelineId 
        });
    }
}

export default DaVinciWebSocketClient;
```

## Backend Integration

### Django Views Integration

```python
# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from davinci_resolve.services import ProjectService, PipelineOrchestratorService

@login_required
def create_video_project(request):
    if request.method == 'POST':
        # Get form data
        project_name = request.POST.get('name')
        obs_recording_ids = request.POST.getlist('recordings')
        
        # Create project
        service = ProjectService(user=request.user)
        project = service.create_project(
            name=project_name,
            template='youtube'
        )
        
        # Link OBS recordings
        project.obs_recordings.set(obs_recording_ids)
        
        # Start automated pipeline
        orchestrator = PipelineOrchestratorService(str(project.id))
        orchestrator.execute_complete_pipeline({
            'pipeline_type': 'complete',
            'content_sources': ['obs_recordings'],
            'ai_processing': {
                'enable_content_analysis': True,
                'enable_ai_editing': True,
                'enable_color_grading': True
            },
            'output_settings': {
                'render_preset': 'youtube_hd',
                'upload_to_youtube': True
            }
        })
        
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'create_project.html')
```

### Celery Tasks Integration

```python
# tasks.py
from celery import shared_task
from davinci_resolve.services import RenderingService, YouTubeIntegrationService

@shared_task
def process_video_pipeline(project_id, pipeline_config):
    """Process complete video pipeline asynchronously"""
    from davinci_resolve.services import PipelineOrchestratorService
    
    orchestrator = PipelineOrchestratorService(project_id)
    result = orchestrator.execute_complete_pipeline(pipeline_config)
    
    return result

@shared_task
def batch_render_videos(render_job_ids):
    """Batch process multiple render jobs"""
    results = []
    
    for job_id in render_job_ids:
        service = RenderingService(job_id)
        result = service.execute_render()
        results.append(result)
    
    return results

@shared_task
def upload_to_youtube_async(render_job_id, upload_options=None):
    """Upload rendered video to YouTube asynchronously"""
    from davinci_resolve.models import DaVinciRenderJob
    
    render_job = DaVinciRenderJob.objects.get(id=render_job_id)
    service = YouTubeIntegrationService(user=render_job.project.user)
    
    result = service.upload_rendered_video(
        render_job_id=render_job_id,
        upload_options=upload_options
    )
    
    return result
```

### Custom Middleware

```python
# middleware.py
from django.utils.deprecation import MiddlewareMixin
from davinci_resolve.optimizations import CacheManager

class DaVinciCacheMiddleware(MiddlewareMixin):
    """Middleware to handle DaVinci Resolve caching"""
    
    def process_request(self, request):
        # Add cache manager to request
        request.davinci_cache = CacheManager()
    
    def process_response(self, request, response):
        # Invalidate caches based on response
        if request.method in ['POST', 'PUT', 'DELETE']:
            if 'davinci/projects' in request.path:
                # Invalidate user statistics cache
                if hasattr(request, 'user') and request.user.is_authenticated:
                    CacheManager.invalidate_user_stats_cache(request.user.id)
        
        return response
```

## Workflow Examples

### OBS Recording to YouTube Pipeline

```python
from davinci_resolve.services import PipelineOrchestratorService
from obs_studio.models import OBSRecording

# Get OBS recordings
recordings = OBSRecording.objects.filter(
    user=request.user,
    status='completed'
).order_by('-created_at')[:5]

# Create project with recordings
project_service = ProjectService(user=request.user)
project = project_service.create_project(
    name="Weekly Tutorial",
    template="youtube"
)

# Link recordings to project
project.obs_recordings.set(recordings)

# Configure and execute pipeline
pipeline_config = {
    'pipeline_type': 'complete',
    'content_sources': ['obs_recordings'],
    'ai_processing': {
        'enable_content_analysis': True,
        'enable_ai_editing': True,
        'editing_style': 'tutorial',
        'enable_color_grading': True,
        'color_profile': 'natural'
    },
    'output_settings': {
        'render_preset': 'youtube_hd',
        'upload_to_youtube': True,
        'youtube_metadata': {
            'title': 'Tutorial: ' + project.name,
            'description': 'Learn how to...',
            'tags': ['tutorial', 'education', 'howto'],
            'privacy_status': 'private',
            'playlist_id': 'PLxxxxxx'
        }
    }
}

orchestrator = PipelineOrchestratorService(str(project.id))
result = orchestrator.execute_complete_pipeline(pipeline_config)
```

### AI Content Generation Pipeline

```python
from content.services import ImageGenerationService, VideoGenerationService
from davinci_resolve.services import TimelineService, AIEditingService

# Generate AI content
image_service = ImageGenerationService()
images = []
for prompt in ["futuristic city", "flying cars", "neon lights"]:
    image = image_service.generate_image(
        prompt=prompt,
        model="dall-e-3"
    )
    images.append(image)

# Create video from images
video_service = VideoGenerationService()
ai_video = video_service.create_video_from_images(
    images=images,
    transition="smooth",
    duration_per_image=3
)

# Create DaVinci project
project = project_service.create_project(
    name="AI Generated Content",
    template="social_media"
)

# Link AI content
project.ai_generated_images.set(images)
project.ai_generated_videos.set([ai_video])

# Create timeline with AI assistance
timeline_service = TimelineService(str(project.id))
timeline = timeline_service.create_timeline_from_ai_content(
    name="AI Montage",
    ai_arrange=True,
    music_sync=True
)

# Apply AI editing
editor = AIEditingService()
editing_decisions = editor.generate_edit_decisions(
    timeline_id=str(timeline.id),
    style='dynamic',
    target_duration=30
)
editor.apply_edit_decisions(timeline.id, editing_decisions)
```

### Batch Processing Workflow

```python
from davinci_resolve.optimizations import BatchOperationManager
from davinci_resolve.models import DaVinciProject, DaVinciRenderJob

# Get projects needing rendering
projects_to_render = DaVinciProject.objects.filter(
    user=request.user,
    status='completed',
    render_jobs__isnull=True
)[:10]

# Create render jobs in batch
render_jobs = []
for project in projects_to_render:
    timeline = project.timelines.filter(is_master_timeline=True).first()
    if timeline:
        render_jobs.append(DaVinciRenderJob(
            project=project,
            timeline=timeline,
            name=f"Batch Render - {project.name}",
            render_preset='youtube_hd',
            output_format='mp4',
            priority=3
        ))

# Bulk create render jobs
created_jobs = DaVinciRenderJob.objects.bulk_create(render_jobs)

# Process in parallel
BatchOperationManager.batch_process_renders(
    render_jobs=created_jobs,
    operation='start'
)
```

## AI Features Integration

### Content Analysis Integration

```python
from davinci_resolve.services import ContentAnalysisService
from davinci_resolve.services import TimelineService

# Analyze content
analyzer = ContentAnalysisService()
analysis = analyzer.analyze_obs_recording(recording_id)

# Use analysis for intelligent timeline creation
timeline_service = TimelineService(project_id)
timeline = timeline_service.create_timeline_with_analysis(
    name="Smart Edit",
    content_analysis=analysis,
    optimization_goals={
        'remove_silence': True,
        'detect_highlights': True,
        'optimize_pacing': True
    }
)

# Analysis results structure
{
    'scene_changes': [
        {'timestamp': 5.2, 'confidence': 0.95},
        {'timestamp': 12.7, 'confidence': 0.88}
    ],
    'face_detection': [
        {'start': 0.0, 'end': 10.5, 'faces': 2},
        {'start': 15.0, 'end': 25.0, 'faces': 1}
    ],
    'audio_analysis': {
        'silence_periods': [[30.0, 32.5], [45.0, 46.2]],
        'peak_moments': [18.3, 42.1, 55.7],
        'music_beats': [...]
    },
    'motion_intensity': {
        'low': [[0, 10], [25, 35]],
        'medium': [[10, 20], [35, 45]],
        'high': [[20, 25], [45, 60]]
    },
    'recommended_cuts': [
        {'frame': 150, 'reason': 'scene_change', 'confidence': 0.92},
        {'frame': 380, 'reason': 'silence_detected', 'confidence': 0.88}
    ]
}
```

### AI Editing Styles

```python
from davinci_resolve.services import AIEditingService

editor = AIEditingService()

# Different editing styles
styles = {
    'tutorial': {
        'pace': 'moderate',
        'transitions': 'simple',
        'emphasis_on': 'clarity',
        'average_clip_duration': 5.0
    },
    'dynamic': {
        'pace': 'fast',
        'transitions': 'energetic',
        'emphasis_on': 'engagement',
        'average_clip_duration': 2.0
    },
    'cinematic': {
        'pace': 'slow',
        'transitions': 'smooth',
        'emphasis_on': 'atmosphere',
        'average_clip_duration': 8.0
    },
    'social_media': {
        'pace': 'very_fast',
        'transitions': 'trendy',
        'emphasis_on': 'hooks',
        'average_clip_duration': 1.5
    }
}

# Apply style
editing_decisions = editor.generate_edit_decisions(
    timeline_id=timeline_id,
    style='dynamic',
    style_params=styles['dynamic'],
    target_duration=60
)
```

### AI Color Grading

```python
from davinci_resolve.services import ColorGradingService

grader = ColorGradingService()

# Analyze and suggest color grade
color_analysis = grader.analyze_timeline_colors(timeline_id)
suggested_profile = grader.suggest_color_profile(
    analysis=color_analysis,
    target_mood='cinematic',
    reference_image='/path/to/reference.jpg'
)

# Apply AI color grading
result = grader.apply_ai_color_grade(
    timeline_id=timeline_id,
    profile=suggested_profile,
    intensity=0.8  # 80% strength
)

# Custom color profiles
profiles = {
    'natural': {
        'temperature': 6500,
        'tint': 0,
        'contrast': 1.1,
        'saturation': 1.0
    },
    'cinematic': {
        'temperature': 5800,
        'tint': -5,
        'contrast': 1.3,
        'saturation': 0.85,
        'lift': [-0.05, -0.05, -0.08, -0.06]
    },
    'vibrant': {
        'temperature': 6800,
        'tint': 2,
        'contrast': 1.2,
        'saturation': 1.2,
        'gain': [1.05, 1.02, 1.0, 1.02]
    }
}
```

## Performance Best Practices

### Query Optimization

```python
from davinci_resolve.optimizations import QueryOptimizer

# Use optimized querysets
projects = QueryOptimizer.get_optimized_project_queryset(user=request.user)

# This prevents N+1 queries when accessing related data
for project in projects:
    print(f"Project: {project.name}")
    print(f"Timelines: {project.timeline_count}")  # No additional query
    print(f"Active renders: {project.active_renders}")  # No additional query
```

### Caching Strategy

```python
from davinci_resolve.optimizations import CacheManager, cached_result

# Cache expensive operations
@cached_result(timeout=3600)
def get_user_render_statistics(user_id):
    # This expensive calculation will be cached for 1 hour
    stats = DaVinciRenderJob.objects.filter(
        project__user_id=user_id
    ).aggregate(
        total_renders=Count('id'),
        completed_renders=Count('id', filter=Q(status='completed')),
        total_duration=Sum('actual_duration'),
        avg_render_time=Avg('actual_duration')
    )
    return stats

# Manual cache management
def update_project_and_clear_cache(project_id, update_data):
    project = DaVinciProject.objects.get(id=project_id)
    
    for key, value in update_data.items():
        setattr(project, key, value)
    project.save()
    
    # Clear related caches
    CacheManager.invalidate_project_cache(project_id)
    CacheManager.invalidate_user_stats_cache(project.user_id)
```

### Batch Processing

```python
from davinci_resolve.optimizations import BatchOperationManager, ResourceOptimizer

# Optimal batch sizing
total_items = 500
batch_size = ResourceOptimizer.get_optimal_batch_size(total_items)
chunks = ResourceOptimizer.chunk_list(items, batch_size)

for chunk in chunks:
    BatchOperationManager.bulk_create_timelines(project_id, chunk)
```

### Monitoring Performance

```python
from davinci_resolve.optimizations import PerformanceMonitor

@PerformanceMonitor.measure_execution_time
@PerformanceMonitor.log_database_queries
def complex_operation():
    # This function will log execution time and query count
    projects = DaVinciProject.objects.all()
    for project in projects:
        process_project(project)
```

## Security Considerations

### API Authentication

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from davinci_resolve.permissions import IsProjectOwner

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsProjectOwner])
def sensitive_operation(request, project_id):
    # Only authenticated users who own the project can access
    pass
```

### File Path Validation

```python
import os
from django.core.exceptions import ValidationError

def validate_media_path(path):
    """Validate media file paths for security"""
    # Resolve to absolute path
    abs_path = os.path.abspath(path)
    
    # Check if path is within allowed directories
    allowed_dirs = [
        settings.MEDIA_ROOT,
        settings.DAVINCI_RESOLVE['MEDIA_POOL_PATH']
    ]
    
    if not any(abs_path.startswith(allowed) for allowed in allowed_dirs):
        raise ValidationError("Invalid media path")
    
    # Check file exists and is readable
    if not os.path.exists(abs_path) or not os.access(abs_path, os.R_OK):
        raise ValidationError("Media file not accessible")
    
    return abs_path
```

### YouTube OAuth Security

```python
from django.core.signing import Signer
from django.conf import settings

class SecureYouTubeAuth:
    def __init__(self):
        self.signer = Signer()
    
    def get_auth_url(self, user_id):
        """Generate secure OAuth URL with signed state"""
        state = self.signer.sign(f"youtube_auth:{user_id}")
        
        flow = Flow.from_client_config(
            settings.YOUTUBE_OAUTH_CONFIG,
            scopes=['https://www.googleapis.com/auth/youtube.upload']
        )
        flow.redirect_uri = settings.YOUTUBE_REDIRECT_URI
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            state=state,
            include_granted_scopes='true'
        )
        
        return auth_url
    
    def verify_callback(self, state):
        """Verify OAuth callback state"""
        try:
            unsigned = self.signer.unsign(state)
            if unsigned.startswith('youtube_auth:'):
                user_id = unsigned.split(':')[1]
                return user_id
        except:
            pass
        return None
```

### Rate Limiting

```python
from django.core.cache import cache
from django.http import HttpResponseTooManyRequests
import time

def rate_limit(key_prefix, limit=10, window=60):
    """Rate limiting decorator"""
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            # Generate unique key for user
            user_id = request.user.id if request.user.is_authenticated else 'anon'
            key = f"{key_prefix}:{user_id}"
            
            # Check current count
            current = cache.get(key, 0)
            if current >= limit:
                return HttpResponseTooManyRequests(
                    f"Rate limit exceeded. Try again in {window} seconds."
                )
            
            # Increment counter
            cache.set(key, current + 1, timeout=window)
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@rate_limit('davinci_render', limit=5, window=300)  # 5 renders per 5 minutes
def create_render_job(request):
    pass
```