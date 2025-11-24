# Testing Scripts - Reusable Audit Procedures

**Created:** November 24, 2025 - Session 178
**Purpose:** Reusable test procedures for ongoing quality assurance

---

## Database Integrity Checks

### Script 1: Full Database Audit

```python
# Run in Django shell: python manage.py shell

from content.models import ImageHistory, VideoHistory, MiniFigAsset
from django.utils import timezone
from datetime import timedelta

print("=" * 60)
print("DATABASE INTEGRITY AUDIT")
print("=" * 60)

# Count totals
total_images = ImageHistory.objects.count()
total_videos = VideoHistory.objects.count()
total_3d = MiniFigAsset.objects.count()

print(f"\nTOTAL RECORDS:")
print(f"  Images: {total_images}")
print(f"  Videos: {total_videos}")
print(f"  3D Models: {total_3d}")

# Orphans
orphaned_images = ImageHistory.objects.filter(project__isnull=True).count()
orphaned_videos = VideoHistory.objects.filter(project__isnull=True).count()

print(f"\nORPHANED RECORDS:")
print(f"  Images: {orphaned_images}")
print(f"  Videos: {orphaned_videos}")

# Stuck videos
stuck_videos = VideoHistory.objects.filter(
    status='pending',
    created_at__lt=timezone.now() - timedelta(hours=24)
).count()

print(f"\nSTUCK PENDING (>24h):")
print(f"  Videos: {stuck_videos}")

# Broken (completed but no URL)
broken_videos = VideoHistory.objects.filter(status='completed', video_url='').count()
broken_3d = MiniFigAsset.objects.filter(status='completed', glb_file='').count()

print(f"\nBROKEN COMPLETED:")
print(f"  Videos (no URL): {broken_videos}")
print(f"  3D Models (no GLB): {broken_3d}")

# Calculate integrity score
total_issues = orphaned_images + orphaned_videos + stuck_videos + broken_videos + broken_3d
total_records = total_images + total_videos + total_3d
integrity_score = ((total_records - total_issues) / total_records) * 100 if total_records > 0 else 100

print(f"\nDATA INTEGRITY SCORE: {integrity_score:.1f}%")
print("=" * 60)
```

### Script 2: List Orphaned Videos

```python
# Run in Django shell: python manage.py shell

from content.models import VideoHistory

orphaned = VideoHistory.objects.filter(project__isnull=True)
print(f"ORPHANED VIDEOS: {orphaned.count()}")
print("-" * 60)

for vid in orphaned:
    prompt_preview = vid.prompt[:50] if vid.prompt else "No prompt"
    print(f"ID: {vid.id}")
    print(f"  Prompt: {prompt_preview}...")
    print(f"  Status: {vid.status}")
    print(f"  Created: {vid.created_at}")
    print(f"  Has URL: {bool(vid.video_url)}")
    print()
```

### Script 3: Fix Orphaned Videos

```python
# Run in Django shell: python manage.py shell
# CAUTION: Review output before running cleanup

from content.models import VideoHistory, ImageHistory, CreativeProject

# Strategy 1: Find source video/image and inherit project
orphaned = VideoHistory.objects.filter(project__isnull=True)

for vid in orphaned:
    prompt = vid.prompt or ""

    # Pattern 1: "Speed 0.5x of video UUID"
    if "of video" in prompt:
        import re
        match = re.search(r'of video ([0-9a-f-]{36})', prompt)
        if match:
            source_id = match.group(1)
            try:
                source = VideoHistory.objects.get(id=source_id)
                if source.project:
                    vid.project = source.project
                    vid.save()
                    print(f"Fixed {vid.id} -> {source.project.name}")
            except VideoHistory.DoesNotExist:
                print(f"Source not found for {vid.id}")

    # Pattern 2: "Animated from image #N"
    elif "from image" in prompt:
        # Try to find source image and its project
        pass

    # Pattern 3: "Talking character" - assign to most recent project
    elif "lip sync" in prompt.lower() or "talking character" in prompt.lower():
        recent_project = CreativeProject.objects.filter(user=vid.user).order_by('-created_at').first()
        if recent_project:
            vid.project = recent_project
            vid.save()
            print(f"Fixed {vid.id} -> {recent_project.name}")
```

---

## API Validation Tests

### Script 4: Test All API Keys

```bash
# Run from project root
python3 scripts/test_api_keys.py
```

### Script 5: Test Stability AI

```python
# Run in Django shell: python manage.py shell

from content.image_generation import ImageGenerationService

service = ImageGenerationService()
print(f"Stability Key: {'Valid' if service.stability_key else 'Missing'}")

# Test API call (uses credits!)
# result = service.generate_image("test image", provider="stability")
# print(f"Test Result: {result.success}")
```

### Script 6: Test Runway ML

```python
# Run in Django shell: python manage.py shell

from content.video_provider import runway_provider

print(f"Runway Provider: {'Configured' if runway_provider else 'Missing'}")
print(f"API Key: {'Valid' if runway_provider.api_key else 'Missing'}")

# Test API call (uses credits!)
# result = runway_provider.get_credits()
# print(f"Credits: {result}")
```

### Script 7: Test ElevenLabs

```python
# Run in Django shell: python manage.py shell

from content.elevenlabs_provider import ElevenLabsProvider

provider = ElevenLabsProvider()
print(f"ElevenLabs: {'Configured' if provider.is_configured() else 'Not configured'}")
print(f"API Key: {'Valid' if provider.api_key else 'Missing'}")
```

---

## Feature Verification Tests

### Script 8: Test Image Generation

```python
# Run in Django shell: python manage.py shell
# WARNING: Uses credits!

from content.image_generation import ImageGenerationService

service = ImageGenerationService()

# Test text-to-image
result = service.generate_image(
    prompt="A simple red circle on white background",
    provider="stability",
    model="core",
    size="512x512"
)

print(f"Success: {result.success}")
print(f"Provider: {result.provider_used}")
print(f"Model: {result.model_used}")
print(f"Cost: ${result.cost:.4f}")
if result.success:
    print(f"Images: {len(result.images)}")
else:
    print(f"Error: {result.error_message}")
```

### Script 9: Test Video Enhancement

```python
# Run in Django shell: python manage.py shell

import subprocess
import os

# Test FFmpeg availability
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
    print(f"FFmpeg: Available")
    print(f"Version: {result.stdout.split('\\n')[0]}")
except FileNotFoundError:
    print("FFmpeg: NOT INSTALLED")
```

### Script 10: Verify Project Association

```python
# Run in Django shell: python manage.py shell
# Test that new content gets proper project association

from content.models import ImageHistory, VideoHistory, CreativeProject
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

# Get recent items
recent_images = ImageHistory.objects.filter(user=user).order_by('-created_at')[:5]
recent_videos = VideoHistory.objects.filter(user=user).order_by('-created_at')[:5]

print("RECENT IMAGES:")
for img in recent_images:
    project_name = img.project.name if img.project else "NO PROJECT"
    print(f"  {img.id}: {project_name}")

print("\nRECENT VIDEOS:")
for vid in recent_videos:
    project_name = vid.project.name if vid.project else "NO PROJECT"
    print(f"  {vid.id}: {project_name}")
```

---

## Integration Test Workflows

### Workflow 1: Image Enhancement Pipeline

```markdown
## Test: Image Enhancement Pipeline

### Prerequisites
- Platform running (make start)
- User logged in
- Active project selected

### Steps
1. Go to AI Studio (http://localhost:8000/ai-studio/)
2. Type: "Generate an image of a red sports car"
3. Wait for image to appear in gallery
4. Type: "Remove background from image 1"
5. Type: "Upscale image 1 by 2x"
6. Type: "Create 2 variations of image 1"

### Expected Results
- [ ] Original image appears in project gallery
- [ ] Background-removed image in same project
- [ ] Upscaled image in same project
- [ ] 2 variation images in same project
- [ ] Total: 5 images in project

### Pass Criteria
All images visible in the same project (not "All Images" only)
```

### Workflow 2: Video Creation Pipeline

```markdown
## Test: Video Creation Pipeline

### Prerequisites
- Platform running
- User logged in
- Image already generated

### Steps
1. Type: "Animate image 1 with subtle motion"
2. Wait for video to complete (~2-3 minutes)
3. Type: "Extend video 1 by 5 seconds"
4. Type: "Apply cinematic color grading to video 1"

### Expected Results
- [ ] Animated video appears in project
- [ ] Extended video in same project
- [ ] Color-graded video in same project

### Pass Criteria
All videos visible in source image's project
```

### Workflow 3: Talking Character Pipeline

```markdown
## Test: Talking Character Pipeline

### Prerequisites
- Platform running
- Character image available

### Steps
1. Type: "Create talking video of image 1 saying 'Hello, I am your AI assistant' using Daniel voice"
2. Wait for pipeline to complete (~3-5 minutes)
3. Play video and check audio

### Expected Results
- [ ] Final video appears in project
- [ ] Video has audio track
- [ ] Voice is Daniel (not Rachel)
- [ ] Lip sync matches audio

### Pass Criteria
- Video in correct project
- Correct voice used
- Audio/video synchronized
```

---

## Automated Health Check

### Script 11: Full Health Check

```bash
#!/bin/bash
# save as scripts/health_check.sh

echo "===================================="
echo "Unified Donkey Betz Health Check"
echo "===================================="

# Check services
echo -e "\n[Services]"
curl -s http://localhost:8000/health/ping/ && echo " - Django: OK" || echo " - Django: FAIL"
redis-cli ping > /dev/null 2>&1 && echo " - Redis: OK" || echo " - Redis: FAIL"

# Check API keys
echo -e "\n[API Keys]"
python3 scripts/test_api_keys.py 2>&1 | grep -E "✓|⚠|✗"

# Check database
echo -e "\n[Database]"
python manage.py shell -c "
from content.models import ImageHistory, VideoHistory
print(f'  Images: {ImageHistory.objects.count()}')
print(f'  Videos: {VideoHistory.objects.count()}')
print(f'  Orphaned: {ImageHistory.objects.filter(project__isnull=True).count() + VideoHistory.objects.filter(project__isnull=True).count()}')
" 2>&1 | grep -v "DEBUG\|INFO\|WARNING"

echo -e "\n===================================="
```

---

## Usage Notes

1. **Run database scripts** in Django shell: `python manage.py shell`
2. **API tests use credits** - mark tests that consume API resources
3. **Integration tests** require browser - use AI Studio UI
4. **Health check** can be run anytime for quick status

---

**Last Updated:** November 24, 2025 - Session 178
