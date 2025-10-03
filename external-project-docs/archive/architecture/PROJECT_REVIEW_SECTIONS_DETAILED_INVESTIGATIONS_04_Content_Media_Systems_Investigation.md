# Detailed Investigation: Content & Media Systems

## Common Issues to Investigate

### Issue 1: Style System Not Applied Correctly
**Problem**: Users select a visual style but generated images don't reflect the chosen style

**Investigation Steps:**

1. **Trace Style Selection Flow**
   ```
   File: donkey-betz-frontend/src/features/content-studio/components/ImageGenerator.tsx
   
   Check:
   - How is style selected in UI?
   - What value is sent to backend?
   - Is it kebab-case or Title Case?
   ```

2. **API Request Analysis**
   ```bash
   # Monitor network tab or add logging
   # In backend/api/content_creation/views.py
   logger.info(f"Received style: {request.data.get('style')}")
   logger.info(f"Received prompt: {request.data.get('prompt')}")
   ```

3. **Style Mapping Investigation**
   ```
   File: backend/content/services/visual_styles/style_mapper.py
   
   Verify:
   - Does this file exist?
   - How does it map frontend values to backend styles?
   - Are all 32 styles mapped?
   ```

4. **Prompt Enhancement Check**
   ```
   File: backend/media_studio/services/dalle_service.py
   Method: enhance_prompt_with_style()
   
   Add logging:
   logger.info(f"Original prompt: {prompt}")
   logger.info(f"Selected style: {style}")
   logger.info(f"Enhanced prompt: {enhanced_prompt}")
   ```

### Issue 2: Image Generation Failures
**Problem**: Image generation requests fail or timeout

**Investigation Steps:**

1. **Check API Keys**
   ```python
   # Django shell
   from django.conf import settings
   print(f"OpenAI key present: {bool(settings.OPENAI_API_KEY)}")
   print(f"SD API URL: {settings.STABLE_DIFFUSION_API_URL}")
   ```

2. **Trace Generation Pipeline**
   ```
   Entry: backend/api/content_creation/views/image_views.py
   ↓
   Service selection: backend/media_studio/services/image_generator_service.py
   ↓
   DALL-E: backend/media_studio/services/dalle_service.py
   OR
   Stable Diffusion: backend/media_studio/services/stable_diffusion_service.py
   ```

3. **Check Celery Task Execution**
   ```bash
   # Check if tasks are queued
   celery -A server inspect active
   
   # Check for failed tasks
   grep -r "image.*generation.*failed" backend/logs/
   ```

### Issue 3: Media Storage Issues
**Problem**: Generated media not accessible or disappearing

**Investigation Steps:**

1. **Storage Configuration**
   ```python
   # backend/server/settings/media.py or settings.py
   MEDIA_ROOT = ?
   MEDIA_URL = ?
   
   # Check if directory exists and has permissions
   ls -la /path/to/media/root/
   ```

2. **CDN Integration Check**
   ```
   File: backend/media_studio/services/storage_service.py
   
   Questions:
   - Is local storage or S3 used?
   - Are URLs generated correctly?
   - Is there a cleanup job deleting files?
   ```

## Specific Code Queries

### Query 1: Find All Style Definitions
```bash
# Find where styles are defined
find backend -name "*.py" -exec grep -l "magical.*mountain\|visual.*style\|style.*definition" {} \;

# List all available styles
grep -r "class.*Style\|STYLES\s*=\|styles\s*=" backend/content/ --include="*.py"
```

### Query 2: Trace Image Generation
```bash
# Find all image generation endpoints
grep -r "generate.*image\|create.*image" backend/api/ --include="*.py"

# Find Celery tasks for media
grep -r "@shared_task.*image\|@shared_task.*video" backend/ --include="*.py"
```

### Query 3: Debug Storage Issues
```python
# Django shell - Check media files
from media_studio.models import MediaAsset

# Recent assets
recent = MediaAsset.objects.order_by('-created_at')[:10]
for asset in recent:
    print(f"Type: {asset.media_type}")
    print(f"URL: {asset.file_url}")
    print(f"Exists: {asset.file.exists() if asset.file else 'No file'}")
    print("---")
```

## Testing Scenarios

### Test 1: Style Application
```python
# Test each style
styles = ['photorealistic', 'anime-manga', 'cyberpunk', 'oil-painting']
prompt = "A majestic mountain landscape"

for style in styles:
    # Make API call
    response = requests.post('/api/content/generate-image/', {
        'prompt': prompt,
        'style': style
    })
    # Verify style markers in final prompt
```

### Test 2: Generation Performance
```python
import time

# Time image generation
start = time.time()
response = generate_image(prompt="Test image")
duration = time.time() - start

print(f"Generation took: {duration}s")
# Should be < 30s for DALL-E, < 60s for SD
```

## Critical Files to Examine

1. **Style System Core**
   - `backend/content/services/visual_styles/prompt_helpers.py` - Style definitions
   - `backend/content/services/visual_styles/style_mapper.py` - Mapping logic
   - `backend/content/services/visual_styles/prompt_categories.py` - Categories

2. **Generation Services**
   - `backend/media_studio/services/dalle_service.py` - DALL-E integration
   - `backend/media_studio/services/stable_diffusion_service.py` - SD integration
   - `backend/media_studio/services/image_processor.py` - Post-processing

3. **API Layer**
   - `backend/api/content_creation/views/image_views.py` - Endpoints
   - `backend/api/content_creation/serializers/image_serializers.py` - Validation

## Common Issues and Fixes

### Issue: Style Not Applied
```python
# Fix in dalle_service.py
def enhance_prompt_with_style(self, prompt, style_name):
    # Normalize style name
    style_name = style_name.lower().replace('-', '_')
    
    # Get style from prompt_helpers
    style = STYLES.get(style_name)
    if not style:
        logger.warning(f"Unknown style: {style_name}")
        return prompt
    
    # Apply style modifiers
    enhanced = f"{prompt}, {style['modifiers']}"
    return enhanced
```

### Issue: Generation Timeout
```python
# Add timeout handling
from celery.exceptions import SoftTimeLimitExceeded

@shared_task(soft_time_limit=60, time_limit=90)
def generate_image_task(prompt, style):
    try:
        # Generation code
    except SoftTimeLimitExceeded:
        # Save partial result or return error
        return {'error': 'Generation timeout'}
```

### Issue: Missing Media Files
```python
# Add file verification
def save_generated_image(image_data, metadata):
    # Save file
    media_asset = MediaAsset.objects.create(...)
    
    # Verify file exists
    if not media_asset.file.exists():
        logger.error(f"File not saved: {media_asset.id}")
        raise FileNotFoundError()
    
    return media_asset
```

## Performance Optimization

### Check Generation Queue
```bash
# Monitor Celery queue depth
celery -A server inspect stats | grep -A5 "content\|media"

# Check Redis memory usage
redis-cli info memory | grep used_memory_human
```

### Optimize Style Processing
```python
# Cache style definitions
from django.core.cache import cache

def get_style_definition(style_name):
    cache_key = f"style:{style_name}"
    style = cache.get(cache_key)
    
    if not style:
        style = load_style_from_file(style_name)
        cache.set(cache_key, style, timeout=3600)
    
    return style
```