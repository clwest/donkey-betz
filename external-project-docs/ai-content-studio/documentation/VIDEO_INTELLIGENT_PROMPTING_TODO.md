# 🎬 Video Generation - Intelligent Prompting Integration TODO

**Status**: NOT IMPLEMENTED  
**Priority**: HIGH  
**Discovered**: August 31, 2025 (Session 11)

## Current State

Video generation currently uses only basic prompt enhancement:

```python
# backend/integrations/runway_service.py (line 52-53)
if enhance_prompt:
    prompt = f"{prompt}, cinematic quality, smooth motion, professional"
```

This is a simple string concatenation, NOT using the sophisticated `IntelligentPromptingService` that powers our other content generation.

## What Needs to Be Done

### 1. Import Intelligent Prompting Service

```python
# backend/api/views_video.py
from ai_partner.prompting_services.intelligent_prompting_service import IntelligentPromptingService
```

### 2. Update TextToVideoView

```python
def post(self, request):
    prompt = request.data.get('prompt')
    enhance_prompt = request.data.get('enhance_prompt', True)
    enhancement_level = request.data.get('enhancement_level', 'advanced')
    
    if enhance_prompt:
        # Use intelligent prompting instead of basic enhancement
        prompting_service = IntelligentPromptingService(request.user)
        enhanced_result = prompting_service.enhance_prompt(
            prompt=prompt,
            context_type='video',
            enhancement_level=enhancement_level,
            additional_context={
                'duration': duration,
                'style': request.data.get('style', 'cinematic'),
                'quality': quality
            }
        )
        prompt = enhanced_result['enhanced_prompt']
        
        # Log the enhancement
        logger.info(f"Video prompt enhanced: {enhanced_result['stats']}")
```

### 3. Update ImageToVideoView for Motion Prompts

```python
def post(self, request):
    motion_prompt = request.data.get('motion_prompt')
    enhance_prompt = request.data.get('enhance_prompt', True)
    
    if enhance_prompt and motion_prompt:
        prompting_service = IntelligentPromptingService(request.user)
        enhanced_result = prompting_service.enhance_prompt(
            prompt=motion_prompt,
            context_type='motion',  # New context type for motion
            enhancement_level='advanced',
            additional_context={
                'source_image': image_url,
                'duration': duration
            }
        )
        motion_prompt = enhanced_result['enhanced_prompt']
```

### 4. Add Video-Specific Context to Prompting Service

```python
# backend/ai_partner/prompting_services/intelligent_prompting_service.py

# Add to CONTEXT_TEMPLATES
'video': {
    'description': 'Video generation from text',
    'keywords': ['cinematic', 'motion', 'camera', 'lighting', 'composition'],
    'style_hints': ['smooth transitions', 'professional quality', 'dynamic movement']
},
'motion': {
    'description': 'Motion description for image-to-video',
    'keywords': ['camera movement', 'subject motion', 'transitions', 'pacing'],
    'style_hints': ['natural physics', 'smooth interpolation', 'cinematic flow']
}
```

### 5. Learn from Video Generation Success

```python
# Add video learning to style memory
class StyleMemoryAgent:
    def capture_video_generation(self, user, prompt, video_url, motion_prompt=None):
        # Store successful video prompts
        # Learn motion patterns
        # Build video style preferences
```

## Benefits of Implementation

1. **Consistency**: Video prompts will match the quality of image generation
2. **Learning**: System learns what makes successful videos
3. **Memory Integration**: Videos can reference past successful generations
4. **Style Evolution**: Video styles can evolve like image styles
5. **Better Results**: More sophisticated prompt enhancement = better videos

## Testing Plan

1. Generate video with basic prompt
2. Generate same video with intelligent prompting
3. Compare quality and relevance
4. A/B test with users
5. Measure success rates

## Estimated Implementation Time

- Basic Integration: 2-3 hours
- Full Feature Parity: 4-6 hours  
- Testing & Refinement: 2-3 hours
- **Total: 1-2 days**

## Priority Justification

This is the LAST MAJOR FEATURE needed for complete platform consistency. Every other content type uses intelligent prompting:
- ✅ Images
- ✅ Blog posts
- ✅ Social media
- ✅ Campaigns
- ❌ Videos (only basic enhancement)

Implementing this brings the platform to true 100% completion with consistent AI enhancement across all content types.