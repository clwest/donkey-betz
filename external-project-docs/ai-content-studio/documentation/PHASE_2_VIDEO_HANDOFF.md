# Phase 2: Video Generation Integration Handoff
## AI Content Studio - Runway ML Video Generation Phase

**Date**: August 28, 2025  
**Phase**: Video Generation & Motion Content  
**Duration**: 8-10 Hours  
**Previous Phase**: ✅ Complete - Images, Blog Posts, Social Media

---

## 🎯 OVERVIEW

This handoff document outlines the video generation phase, integrating Runway ML's API to add video creation capabilities to the AI Content Studio. The system will enable users to create videos from text prompts, animate existing images, and generate dynamic content for social media and marketing campaigns.

### Current System Status ✅
- **Image Generation**: Fully functional with 53+ professional styles, batch generation
- **Blog Post Creation**: Complete with SEO optimization, tone control, memory/enhancement options
- **Social Media Posts**: Multi-platform generation with hashtags and variations
- **Gallery System**: Complete with save, filter, search capabilities
- **Consistent UI/UX**: Memory context and prompt enhancement across all features
- **Backend API**: Robust authentication, proper error handling
- **Frontend**: Professional dark theme UI with Tailwind CSS

### What's Already in Place 🔧
- **Runway API Key**: Already configured in `/backend/.env` file
- **Content generation patterns**: Established in blog and social writers
- **UI components**: Reusable patterns for generation interfaces
- **Enhancement system**: Memory context and prompt enhancement ready

---

## 📋 DEVELOPMENT ROADMAP

## **PHASE 1: Runway API Integration (Hours 1-3)**

### Priority 1: Core Runway Service
**Estimated Time**: 1.5 hours  
**Files to Create**:
```
/backend/integrations/__init__.py
/backend/integrations/runway_service.py
/backend/api/views_video.py
```

**Runway Service Implementation**:
```python
# /backend/integrations/runway_service.py
import logging
import requests
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class RunwayMLService:
    """
    Runway ML API integration for video generation.
    Supports Gen-3 Alpha models for text-to-video and image-to-video.
    """
    
    def __init__(self):
        self.api_key = settings.RUNWAY_API_KEY
        self.base_url = "https://api.runwayml.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def text_to_video(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "720p",
        use_memory: bool = True,
        enhance_prompt: bool = True
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt using Gen-3 Alpha.
        
        Args:
            prompt: Text description of desired video
            duration: Video length in seconds (5 or 10)
            resolution: Output resolution (720p or 1080p)
            use_memory: Apply memory context
            enhance_prompt: Apply prompt enhancement
            
        Returns:
            Dict with task_id and status
        """
        
        # Apply prompt enhancement if requested
        if enhance_prompt:
            prompt = f"{prompt}, cinematic quality, smooth motion, professional"
            
        endpoint = f"{self.base_url}/generations"
        
        payload = {
            "prompt": prompt,
            "model": "gen3a_turbo",  # or "gen3a" for higher quality
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": "16:9"
        }
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Runway API error: {e}")
            raise
            
    def image_to_video(
        self,
        image_url: str,
        motion_prompt: str,
        duration: int = 5
    ) -> Dict[str, Any]:
        """
        Animate an existing image with motion.
        
        Args:
            image_url: URL of source image
            motion_prompt: Description of desired motion
            duration: Video length in seconds
            
        Returns:
            Dict with task_id and status
        """
        
        endpoint = f"{self.base_url}/image-to-video"
        
        payload = {
            "image_url": image_url,
            "prompt": motion_prompt,
            "duration": duration,
            "model": "gen3a_turbo"
        }
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Runway image-to-video error: {e}")
            raise
            
    def get_generation_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check video generation progress.
        
        Returns:
            Dict with status, progress, and video_url when complete
        """
        
        endpoint = f"{self.base_url}/generations/{task_id}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Status check error: {e}")
            raise
```

### Priority 2: Video API Views
**Estimated Time**: 1 hour

**API Endpoints**:
```python
# /backend/api/views_video.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from integrations.runway_service import RunwayMLService
from content.models import Content

class TextToVideoView(APIView):
    """
    POST /api/video/text-to-video/
    Generate video from text prompt
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        prompt = request.data.get('prompt')
        duration = request.data.get('duration', 5)
        use_memory = request.data.get('use_memory', True)
        enhance_prompt = request.data.get('enhance_prompt', True)
        
        runway = RunwayMLService()
        result = runway.text_to_video(
            prompt=prompt,
            duration=duration,
            use_memory=use_memory,
            enhance_prompt=enhance_prompt
        )
        
        # Save to database
        content = Content.objects.create(
            user=request.user,
            type='video',
            prompt=prompt,
            metadata={
                'task_id': result['task_id'],
                'duration': duration,
                'status': 'processing'
            }
        )
        
        return Response({
            'success': True,
            'content_id': content.id,
            'task_id': result['task_id']
        })

class VideoStatusView(APIView):
    """
    GET /api/video/status/<task_id>/
    Check video generation progress
    """
    
    def get(self, request, task_id):
        runway = RunwayMLService()
        status_data = runway.get_generation_status(task_id)
        
        # Update database if complete
        if status_data['status'] == 'completed':
            Content.objects.filter(
                metadata__task_id=task_id
            ).update(
                result_url=status_data['video_url'],
                metadata__status='completed'
            )
            
        return Response(status_data)
```

### Priority 3: URL Configuration
**Estimated Time**: 30 minutes

**Update `/backend/api/urls.py`**:
```python
from .views_video import (
    TextToVideoView,
    ImageToVideoView,
    VideoStatusView,
    VideoGalleryView
)

urlpatterns += [
    # Video generation endpoints
    path('video/text-to-video/', TextToVideoView.as_view(), name='text-to-video'),
    path('video/image-to-video/', ImageToVideoView.as_view(), name='image-to-video'),
    path('video/status/<str:task_id>/', VideoStatusView.as_view(), name='video-status'),
    path('video/gallery/', VideoGalleryView.as_view(), name='video-gallery'),
]
```

---

## **PHASE 2: Frontend Video UI (Hours 4-6)**

### Priority 1: Video Generation Interface
**Estimated Time**: 1.5 hours

**Add to `/frontend/index.html`**:
```html
<!-- Video Generation Options -->
<div id="videoOptions" class="bg-gray-800 rounded-lg p-6 mb-6 hidden">
    <h2 class="text-xl font-semibold mb-4">Video Generator</h2>
    
    <!-- Generation Mode Tabs -->
    <div class="flex gap-2 mb-6">
        <button onclick="setVideoMode('text')" class="px-4 py-2 bg-purple-600 rounded">
            Text to Video
        </button>
        <button onclick="setVideoMode('image')" class="px-4 py-2 bg-gray-700 rounded">
            Image to Video
        </button>
    </div>
    
    <!-- Text to Video Mode -->
    <div id="textToVideoMode">
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium mb-2">Describe your video</label>
                <textarea id="videoPrompt" 
                    class="w-full bg-gray-700 rounded px-4 py-2 h-24"
                    placeholder="A serene lake at sunrise with mist rising from the water...">
                </textarea>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium mb-2">Duration</label>
                    <select id="videoDuration" class="w-full bg-gray-700 rounded px-4 py-2">
                        <option value="5">5 seconds</option>
                        <option value="10">10 seconds</option>
                    </select>
                </div>
                
                <div>
                    <label class="block text-sm font-medium mb-2">Quality</label>
                    <select id="videoQuality" class="w-full bg-gray-700 rounded px-4 py-2">
                        <option value="gen3a_turbo">Fast (Gen-3 Turbo)</option>
                        <option value="gen3a">High Quality (Gen-3)</option>
                    </select>
                </div>
            </div>
            
            <!-- Style Presets -->
            <div>
                <label class="block text-sm font-medium mb-2">Style Preset</label>
                <div class="grid grid-cols-4 gap-2">
                    <button class="video-style-btn active" data-style="cinematic">
                        🎬 Cinematic
                    </button>
                    <button class="video-style-btn" data-style="realistic">
                        📷 Realistic
                    </button>
                    <button class="video-style-btn" data-style="anime">
                        🎌 Anime
                    </button>
                    <button class="video-style-btn" data-style="abstract">
                        🎨 Abstract
                    </button>
                </div>
            </div>
            
            <!-- Enhancement Options -->
            <div class="flex items-center gap-4">
                <label class="flex items-center gap-2">
                    <input type="checkbox" id="videoUseMemory" checked>
                    <span class="text-sm">Use memory context</span>
                </label>
                <label class="flex items-center gap-2">
                    <input type="checkbox" id="videoEnhance" checked>
                    <span class="text-sm">Enhance prompt</span>
                </label>
            </div>
        </div>
    </div>
    
    <!-- Image to Video Mode -->
    <div id="imageToVideoMode" class="hidden">
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium mb-2">Select Image</label>
                <div class="flex gap-3">
                    <button onclick="openGallerySelector('video')" 
                        class="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700">
                        Choose from Gallery
                    </button>
                    <button onclick="uploadImageForVideo()" 
                        class="px-4 py-2 bg-gray-600 rounded hover:bg-gray-500">
                        Upload New
                    </button>
                </div>
                <div id="selectedImagePreview" class="mt-3 hidden">
                    <img id="videoSourceImage" class="w-32 h-32 object-cover rounded" />
                </div>
            </div>
            
            <div>
                <label class="block text-sm font-medium mb-2">Motion Description</label>
                <textarea id="motionPrompt" 
                    class="w-full bg-gray-700 rounded px-4 py-2 h-20"
                    placeholder="Camera slowly zooms in while clouds drift across the sky...">
                </textarea>
            </div>
            
            <!-- Motion Presets -->
            <div>
                <label class="block text-sm font-medium mb-2">Motion Preset</label>
                <div class="grid grid-cols-3 gap-2">
                    <button class="motion-preset-btn" data-motion="zoom-in">
                        🔍 Zoom In
                    </button>
                    <button class="motion-preset-btn" data-motion="pan-left">
                        ← Pan Left
                    </button>
                    <button class="motion-preset-btn" data-motion="orbit">
                        🔄 Orbit
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Generate Button -->
    <button onclick="generateVideo()" 
        class="w-full mt-6 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:opacity-90">
        🎬 Generate Video
    </button>
</div>

<!-- Video Generation Progress -->
<div id="videoProgress" class="bg-gray-800 rounded-lg p-6 mb-6 hidden">
    <h3 class="text-lg font-semibold mb-4">Generating Video...</h3>
    <div class="space-y-3">
        <div class="flex items-center justify-between">
            <span class="text-sm">Progress</span>
            <span id="progressPercent">0%</span>
        </div>
        <div class="w-full bg-gray-700 rounded-full h-2">
            <div id="progressBar" class="bg-gradient-to-r from-purple-600 to-pink-600 h-2 rounded-full" 
                style="width: 0%"></div>
        </div>
        <p class="text-sm text-gray-400" id="progressMessage">
            Initializing video generation...
        </p>
    </div>
</div>
```

### Priority 2: Video Player Component
**Estimated Time**: 1 hour

**Video Player HTML**:
```html
<!-- Video Result Display -->
<div id="videoResult" class="bg-gray-800 rounded-lg p-6 hidden">
    <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Generated Video</h3>
        <div class="flex gap-2">
            <button onclick="downloadVideo()" class="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700">
                ⬇️ Download
            </button>
            <button onclick="shareVideo()" class="px-4 py-2 bg-green-600 rounded hover:bg-green-700">
                🔗 Share
            </button>
            <button onclick="saveToGallery()" class="px-4 py-2 bg-purple-600 rounded hover:bg-purple-700">
                💾 Save to Gallery
            </button>
        </div>
    </div>
    
    <div class="video-container bg-black rounded-lg overflow-hidden">
        <video id="generatedVideo" class="w-full" controls>
            Your browser does not support the video tag.
        </video>
    </div>
    
    <div class="mt-4 p-4 bg-gray-700 rounded">
        <p class="text-sm text-gray-300 mb-2">
            <strong>Prompt:</strong> <span id="videoPromptDisplay"></span>
        </p>
        <p class="text-sm text-gray-300">
            <strong>Duration:</strong> <span id="videoDurationDisplay"></span> seconds
        </p>
    </div>
    
    <!-- Action Buttons -->
    <div class="flex gap-3 mt-4">
        <button onclick="generateVariation()" class="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600">
            🔄 Generate Variation
        </button>
        <button onclick="extendVideo()" class="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600">
            ➕ Extend Video
        </button>
        <button onclick="createGif()" class="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600">
            🎞️ Create GIF
        </button>
    </div>
</div>
```

### Priority 3: JavaScript Integration
**Estimated Time**: 1.5 hours

**Add to frontend JavaScript**:
```javascript
// Video Generation Functions
let currentVideoTask = null;
let progressInterval = null;

async function generateVideo() {
    const mode = document.querySelector('#textToVideoMode').classList.contains('hidden') ? 'image' : 'text';
    
    if (mode === 'text') {
        const prompt = document.getElementById('videoPrompt').value;
        const duration = document.getElementById('videoDuration').value;
        const quality = document.getElementById('videoQuality').value;
        const useMemory = document.getElementById('videoUseMemory').checked;
        const enhancePrompt = document.getElementById('videoEnhance').checked;
        
        if (!prompt) {
            alert('Please describe your video');
            return;
        }
        
        try {
            // Show progress
            document.getElementById('videoProgress').classList.remove('hidden');
            document.getElementById('videoResult').classList.add('hidden');
            
            const response = await fetch(`${API_BASE}/video/text-to-video/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${AUTH_TOKEN}`
                },
                body: JSON.stringify({
                    prompt: prompt,
                    duration: parseInt(duration),
                    quality: quality,
                    use_memory: useMemory,
                    enhance_prompt: enhancePrompt
                })
            });
            
            const data = await response.json();
            if (data.success) {
                currentVideoTask = data.task_id;
                startProgressTracking(data.task_id);
            }
        } catch (error) {
            console.error('Video generation error:', error);
            alert('Failed to start video generation');
        }
    } else {
        // Image to video mode
        await generateVideoFromImage();
    }
}

function startProgressTracking(taskId) {
    let progress = 0;
    
    progressInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/video/status/${taskId}/`, {
                headers: {
                    'Authorization': `Token ${AUTH_TOKEN}`
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'processing') {
                progress = Math.min(progress + 10, 90);
                updateProgress(progress, 'Processing your video...');
            } else if (data.status === 'completed') {
                updateProgress(100, 'Video ready!');
                clearInterval(progressInterval);
                displayVideo(data.video_url);
            } else if (data.status === 'failed') {
                clearInterval(progressInterval);
                alert('Video generation failed. Please try again.');
                document.getElementById('videoProgress').classList.add('hidden');
            }
        } catch (error) {
            console.error('Progress check error:', error);
        }
    }, 2000); // Check every 2 seconds
}

function updateProgress(percent, message) {
    document.getElementById('progressPercent').textContent = `${percent}%`;
    document.getElementById('progressBar').style.width = `${percent}%`;
    document.getElementById('progressMessage').textContent = message;
}

function displayVideo(videoUrl) {
    document.getElementById('videoProgress').classList.add('hidden');
    document.getElementById('videoResult').classList.remove('hidden');
    
    const video = document.getElementById('generatedVideo');
    video.src = videoUrl;
    video.load();
    
    // Update display info
    document.getElementById('videoPromptDisplay').textContent = 
        document.getElementById('videoPrompt').value;
    document.getElementById('videoDurationDisplay').textContent = 
        document.getElementById('videoDuration').value;
}

function setVideoMode(mode) {
    if (mode === 'text') {
        document.getElementById('textToVideoMode').classList.remove('hidden');
        document.getElementById('imageToVideoMode').classList.add('hidden');
    } else {
        document.getElementById('textToVideoMode').classList.add('hidden');
        document.getElementById('imageToVideoMode').classList.remove('hidden');
    }
}

// Video style presets
document.querySelectorAll('.video-style-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.video-style-btn').forEach(b => 
            b.classList.remove('active'));
        this.classList.add('active');
        
        // Apply style to prompt
        const style = this.dataset.style;
        const promptField = document.getElementById('videoPrompt');
        // Add style keywords to enhance prompt
    });
});
```

---

## **PHASE 3: Advanced Features (Hours 7-8)**

### Priority 1: Video Gallery Integration
**Estimated Time**: 1 hour

**Features**:
- Display generated videos in gallery grid
- Video thumbnails with duration overlay
- Preview on hover
- Filter by date, duration, style
- Search by prompt keywords

### Priority 2: Video Variations & Extensions
**Estimated Time**: 1 hour

**Capabilities**:
- Generate variations of existing videos
- Extend video duration (add 5 more seconds)
- Create GIF versions for social media
- Basic trimming (start/end points)

---

## 🔧 TECHNICAL REQUIREMENTS

### Environment Variables
```bash
# Already in /backend/.env
RUNWAY_API_KEY=your_runway_key_here

# Verify it's loaded in settings.py
RUNWAY_API_KEY = os.getenv('RUNWAY_API_KEY')
```

### Dependencies to Add
```bash
# backend/requirements.txt
requests>=2.31.0  # For API calls
Pillow>=10.0.0    # For image processing
python-magic>=0.4.27  # For file type detection
```

### Database Updates
```python
# Update Content model to support video
class Content(models.Model):
    TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),  # Add this
    ]
    
    # Existing fields...
    duration = models.IntegerField(null=True, blank=True)  # For videos
    thumbnail_url = models.URLField(blank=True)  # For video thumbnails
```

### CORS & Media Settings
```python
# backend/core/settings.py
# Ensure these are configured for video files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Add video folder
VIDEO_UPLOAD_PATH = 'videos/'
```

---

## 📁 FILE STRUCTURE

```
ai-content-studio/
├── backend/
│   ├── integrations/
│   │   ├── __init__.py            # NEW
│   │   └── runway_service.py      # NEW - Core Runway integration
│   ├── api/
│   │   ├── views_video.py         # NEW - Video API endpoints
│   │   └── urls.py                # UPDATE - Add video routes
│   ├── content/
│   │   └── models.py              # UPDATE - Add video support
│   └── media/
│       └── videos/                # NEW - Video storage
├── frontend/
│   └── index.html                 # UPDATE - Add video UI
└── documentation/
    └── PHASE_2_VIDEO_HANDOFF.md  # THIS FILE
```

---

## 🎯 SUCCESS CRITERIA

### Phase 1 Complete ✅
- [ ] Runway API service class implemented
- [ ] Text-to-video endpoint working
- [ ] Image-to-video endpoint working
- [ ] Status checking endpoint functional

### Phase 2 Complete ✅
- [ ] Video generation UI integrated
- [ ] Progress tracking displays correctly
- [ ] Video player shows generated content
- [ ] Download and save functions work

### Phase 3 Complete ✅
- [ ] Videos appear in gallery
- [ ] Variations can be generated
- [ ] All enhancement options functional

---

## ⚠️ POTENTIAL ISSUES & SOLUTIONS

### Issue 1: Runway API Rate Limits
**Solution**: 
- Implement request queuing
- Show estimated wait times
- Cache generation status to reduce API calls

### Issue 2: Large Video Files
**Solution**:
- Stream videos instead of downloading
- Implement CDN for video delivery
- Compress videos after generation

### Issue 3: Long Generation Times
**Solution**:
- WebSocket for real-time updates
- Email notifications when complete
- Allow background processing

---

## 🚀 TESTING CHECKLIST

1. **API Integration**:
   ```bash
   # Test Runway connection
   curl -X POST http://localhost:8001/api/video/text-to-video/ \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "A sunset over mountains", "duration": 5}'
   ```

2. **Frontend Flow**:
   - Generate video from text prompt
   - Generate video from gallery image
   - Check progress updates work
   - Verify video plays correctly
   - Test download functionality

3. **Error Handling**:
   - Invalid API key
   - Network timeout
   - Failed generation
   - Invalid file formats

---

## 📝 HANDOFF NOTES FOR NEXT DEVELOPER

### What You're Building On
1. **Completed Features**:
   - Full image generation system with 53 styles
   - Blog post generation with SEO
   - Social media content for all platforms
   - Consistent UI with memory/enhancement options

2. **Established Patterns**:
   - API view structure in `/backend/api/`
   - Frontend UI components with Tailwind
   - Progress tracking patterns from batch generation
   - Gallery integration patterns

3. **Key Files to Review**:
   - `/backend/api/views_batch.py` - Similar async pattern
   - `/frontend/index.html` - UI component structure
   - `/backend/content/models.py` - Content model

### Development Tips
1. Start with basic text-to-video to test Runway connection
2. Reuse progress tracking from batch image generation
3. Follow existing UI patterns for consistency
4. Test with short durations first (5 seconds)
5. Implement proper error handling early

### API Documentation
- Runway API Docs: https://docs.runwayml.com/
- Gen-3 Models: https://docs.runwayml.com/gen3
- Rate Limits: 30 requests/minute for standard tier

---

**Time Estimate**: 8-10 hours  
**Complexity**: Medium-High (new API integration)  
**Priority**: High (key differentiator feature)

**Next Steps After This Phase**:
1. Campaign mode (orchestrate all content types)
2. Video editing features (trim, merge, effects)
3. AI-powered video templates
4. Bulk video generation

Good luck! The foundation is solid, and the patterns are established. Follow the existing structure and you'll have video generation working smoothly. 🚀