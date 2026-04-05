"""
Image views — generate functions.
"""

"""
Image Generation Views
Phase 2: Frontend Reality Fix - Image Generation

Handles image generation requests using:
- Stability AI (Stable Diffusion) - Primary
- Replicate API - Fallback

Created: September 30, 2025
"""

import os
import logging
import requests
import uuid
import json
import zipfile
import base64
from openai import OpenAI
from io import BytesIO
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone  # Session 96 Weekend Project
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from PIL import Image as PILImage

# Phase 2 P1: Rate limiting for image operations
from core.decorators import rate_limit
# Phase 2 P1: Input validation
from core.validators import validate_prompt, sanitize_prompt, validate_uuid, validate_numeric_range
# Phase 2 P1: Safe error handling
# Session 487: Creator watermark integration
from core.services.watermark_integration import save_watermarked_image
# Session 769: Cost tracking for external APIs
from core.services.api_cost_config import calculate_stability_cost
# Session 1036: save_to_history needed for gallery_generate
from core.views_image_misc import save_to_history

logger = logging.getLogger(__name__)


# ========================================
# SESSION 794: SYSTEM USER FOR AUTONOMOUS OPERATIONS
# ========================================

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@rate_limit('ai_generation')  # Phase 2 P1: Rate limit AI generation (10 requests/min)
def gallery_generate(request):
    """
    Generate images using Stable Diffusion or Replicate

    Expected request body:
    {
        "prompt": "A beautiful sunset over mountains",
        "negative_prompt": "blurry, low quality",
        "width": 1024,
        "height": 1024,
        "num_images": 1,
        "style": "photorealistic"
    }

    Returns:
    {
        "success": true,
        "images": [
            {
                "id": "uuid",
                "url": "/media/generated_images/...",
                "prompt": "...",
                "created_at": "2025-09-30T..."
            }
        ],
        "provider": "stability|replicate",
        "cost": 0.04
    }
    """
    try:
        user = request.user
        data = request.data

        # Extract parameters
        prompt = data.get('prompt', '')

        # Phase 2 P1: Validate prompt
        is_valid, validation_error = validate_prompt(prompt, min_length=1, max_length=2000)
        if not is_valid:
            return Response({
                'success': False,
                'error': validation_error,
                'error_code': 'VALIDATION_ERROR'
            }, status=400)

        # Sanitize prompt to prevent injection
        prompt = sanitize_prompt(prompt)

        negative_prompt = data.get('negative_prompt', 'blurry, low quality, distorted')
        if negative_prompt:
            negative_prompt = sanitize_prompt(negative_prompt)

        # Phase 2 P1: Validate dimensions
        width = int(data.get('width', 1024))
        height = int(data.get('height', 1024))
        width_valid, width_error = validate_numeric_range(width, 256, 2048, 'width')
        if not width_valid:
            return Response({'success': False, 'error': width_error, 'error_code': 'VALIDATION_ERROR'}, status=400)
        height_valid, height_error = validate_numeric_range(height, 256, 2048, 'height')
        if not height_valid:
            return Response({'success': False, 'error': height_error, 'error_code': 'VALIDATION_ERROR'}, status=400)

        # Phase 2 P1: Validate num_images
        num_images = int(data.get('num_images', 1))
        num_valid, num_error = validate_numeric_range(num_images, 1, 10, 'num_images')
        if not num_valid:
            return Response({'success': False, 'error': num_error, 'error_code': 'VALIDATION_ERROR'}, status=400)

        style = data.get('style', 'photorealistic')
        quality = data.get('quality', 'balanced')  # NEW: Support for quality selector

        # Session 124: Extract project_id for project-scoped generation
        project_id = data.get('project_id')

        # Phase 2 P1: Validate project_id if provided
        if project_id:
            is_valid, uuid_error = validate_uuid(project_id)
            if not is_valid:
                return Response({'success': False, 'error': uuid_error, 'error_code': 'VALIDATION_ERROR'}, status=400)
        project = None

        # Check direct parameter first
        if project_id:
            try:
                from content.models import CreativeProject
                project = CreativeProject.objects.get(id=project_id, user=user)
                logger.info(f"🎨 Image generation for project (direct): {project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ Project {project_id} not found, generating without project")

        # Session 124: Check Redis for project context set by Assistant
        if not project:
            try:
                import redis
                r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)
                stored_project_id = r.get(f"user:{user.id}:current_project")
                if stored_project_id:
                    from content.models import CreativeProject
                    project = CreativeProject.objects.get(id=stored_project_id, user=user)
                    logger.info(f"🎨 Image generation for project (from Redis): {project.name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not retrieve project from Redis: {e}")

        logger.info(f"🎨 Image generation request from {user.username}: {prompt[:50]}... (quality: {quality}, style: {style})")

        # Try Stability AI first (if API key available)
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        replicate_key = os.getenv('REPLICATE_API_KEY') or settings.AI_PROVIDERS.get('REPLICATE_API_KEY')

        generated_images = []
        provider = None
        cost = 0.0

        # Use the new ImageGenerationService with quality support
        if stability_key:
            logger.info(f"🎨 Attempting generation with Stability AI ({quality} quality)...")
            try:
                from content.image_generation import ImageGenerationService

                service = ImageGenerationService()
                result = service.generate_image(
                    prompt=prompt,
                    size=f"{width}x{height}",
                    style=style,
                    quality=quality,
                    provider='stability',
                    negative_prompt=negative_prompt,
                    num_images=num_images
                )

                if result.success:
                    generated_images = result.images  # Fixed: attribute is 'images' not 'image_urls'
                    provider = 'stability'
                    cost = result.cost if hasattr(result, 'cost') else 0.0
                    logger.info(f"✅ Stability AI generated {len(generated_images)} images (cost: ${cost:.4f})")
            except Exception as e:
                logger.warning(f"⚠️ Stability AI failed: {e}, trying Replicate...")

        # Fallback to Replicate if Stability failed or not available
        if not generated_images and replicate_key:
            logger.info("🎨 Attempting generation with Replicate...")
            try:
                result = generate_with_replicate(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_images=num_images,
                    api_key=replicate_key
                )
                if result['success']:
                    generated_images = result['images']
                    provider = 'replicate'
                    cost = result.get('cost', 0.02)
                    logger.info(f"✅ Replicate generated {len(generated_images)} images")
            except Exception as e:
                logger.error(f"❌ Replicate also failed: {e}")

        # If both failed or no API keys
        if not generated_images:
            return Response({
                'success': False,
                'error': 'Image generation failed. Please check API keys.',
                'details': {
                    'stability_configured': bool(stability_key),
                    'replicate_configured': bool(replicate_key)
                }
            }, status=500)

        # Save images and create records
        saved_images = []
        # Session 95: Extract seeds from result metadata if available
        seeds = []
        if hasattr(result, 'metadata') and result.metadata and 'seeds' in result.metadata:
            seeds = result.metadata['seeds']

        for img_index, img_data in enumerate(generated_images):
            try:
                # Save to media storage
                image_id = str(uuid.uuid4())
                filename = f"generated_images/{user.id}/{image_id}.png"

                # img_data can be either a string (URL/data URI) or dict with 'url' key
                image_url = img_data if isinstance(img_data, str) else img_data.get('url')

                # Handle base64 data URIs vs regular URLs
                if image_url:
                    if image_url.startswith('data:image'):
                        # Extract base64 data from data URI
                        import base64
                        import re
                        base64_match = re.search(r'base64,(.+)', image_url)
                        if base64_match:
                            image_data = base64.b64decode(base64_match.group(1))
                            # Session 487: Apply creator watermark before saving
                            # Session 800: Now returns Cloudinary URL in production
                            file_path = save_watermarked_image(
                                image_bytes=image_data,
                                filename=filename,
                                user=user,
                                generation_params={'prompt': prompt, 'model': quality, 'style': style}
                            )
                            # Session 800: file_path may be Cloudinary URL or local path
                            url = file_path if file_path.startswith('http') else default_storage.url(file_path)
                        else:
                            continue
                    else:
                        # Regular HTTP/HTTPS URL - download it
                        response = requests.get(image_url, timeout=30)
                        if response.status_code == 200:
                            # Session 487: Apply creator watermark before saving
                            # Session 800: Now returns Cloudinary URL in production
                            file_path = save_watermarked_image(
                                image_bytes=response.content,
                                filename=filename,
                                user=user,
                                generation_params={'prompt': prompt, 'model': quality, 'style': style}
                            )
                            # Session 800: file_path may be Cloudinary URL or local path
                            url = file_path if file_path.startswith('http') else default_storage.url(file_path)
                        else:
                            continue

                    # Map quality to model_used for history
                    quality_to_model = {
                        'fast': 'core',
                        'balanced': 'sdxl',
                        'high': 'sd3',
                        'premium': 'ultra'
                    }
                    model_used = quality_to_model.get(quality, 'sdxl')

                    # Session 95: Get seed for this image if available
                    image_seed = seeds[img_index] if img_index < len(seeds) else None

                    # Save to history (Session 36: Feature 9)
                    history = save_to_history(
                        user=user,
                        file_path=file_path,
                        image_type='generated',
                        prompt=prompt,
                        parameters={
                            'provider': provider,
                            'width': width,
                            'height': height,
                            'quality': quality,
                            'negative_prompt': negative_prompt,
                            'num_images': num_images
                        },
                        model_used=model_used,
                        style=style,
                        seed=image_seed,  # Session 95: Add seed for reproducibility
                        project=project  # Session 124: Associate with project
                    )

                    # Session 143: Track agent contribution for gallery generation
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=history,
                            project=project,
                            contribution_type='generation',
                            task_description=f"Generated image via gallery_generate (provider={provider}, quality={quality}, style={style}, resolution={width}x{height})",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {history.id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        # Don't fail image creation if contribution tracking fails

                    # Session 122: Track generated image in AI Assistant for intelligent chaining
                    try:
                        from django.core.cache import cache
                        cache_key = f'assistant_{user.id}'
                        assistant = cache.get(cache_key)
                        if assistant and history:
                            # Determine asset type based on context
                            asset_type = 'image'
                            if 'logo' in prompt.lower():
                                asset_type = 'logo'
                            elif any(word in prompt.lower() for word in ['character', 'mascot', 'avatar']):
                                asset_type = 'character'
                            elif any(word in prompt.lower() for word in ['product', 'merchandise']):
                                asset_type = 'product'

                            assistant.track_generated_image(
                                image_id=str(history.id),
                                image_url=url,
                                prompt=prompt,
                                asset_type=asset_type
                            )
                            logger.info(f"📸 Tracked image {history.id} as {asset_type} in AI Assistant")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to track image in AI Assistant: {e}")

                    # Save image record (works for both base64 and HTTP URLs)
                    saved_images.append({
                        'id': image_id,
                        'url': url,
                        'prompt': prompt,
                        'width': width,
                        'height': height,
                        'provider': provider,
                        'created_at': datetime.now().isoformat()
                    })
                    logger.info(f"✅ Saved image {image_id}")
            except Exception as e:
                logger.error(f"❌ Failed to save image: {e}")

        if not saved_images:
            return Response({
                'success': False,
                'error': 'Generated images but failed to save'
            }, status=500)

        return Response({
            'success': True,
            'images': saved_images,
            'provider': provider,
            'cost': cost,
            'prompt': prompt,
            'total_images': len(saved_images)
        })

    except Exception as e:
        logger.error(f"❌ Image generation error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


def generate_image_with_stability(prompt, model, style, user):
    """
    Helper function to generate image using Stability AI
    Session 63: Wrapper around existing generation logic
    """
    try:
        from content.image_generation import ImageGenerationService
        from content.models import ImageHistory

        service = ImageGenerationService()

        # Map model to quality
        quality_map = {
            'core': 'fast',
            'sdxl': 'balanced',
            'sd3': 'high',
            'ultra': 'premium'
        }
        quality = quality_map.get(model, 'balanced')

        # Generate image
        result = service.generate_image(
            prompt=prompt,
            size='1024x1024',
            style=style,
            quality=quality,
            provider='stability',
            negative_prompt='blurry, low quality, distorted',
            num_images=1
        )

        if result.success and result.images:
            # Get the first image
            image_url = result.images[0]

            # Save to ImageHistory
            from core.services.workspace_resolver import get_active_workspace
            image_history = ImageHistory.objects.create(
                user=user,
                filename=image_url.split('/')[-1][:255],  # Session 63: Truncate to 255 chars for database constraint
                file_path=image_url,
                prompt=prompt,
                model_used=model,  # Session 63: Fixed field name
                style=style,
                image_type='generated',  # Session 64: Fixed - 'generated' not 'generation' to match model choices
                workspace=get_active_workspace(user),
            )

            logger.info(f"✅ Generated and saved image {image_history.id}")

            return {
                'success': True,
                'image_id': image_history.id,
                'url': image_url
            }
        else:
            # Session 64: Return error info instead of None
            error_msg = getattr(result, 'error_message', 'Unknown error')
            logger.error(f"❌ Image generation failed: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }

    except Exception as e:
        logger.error(f"❌ Error generating image: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Session 64: Return error info instead of None
        return {
            'success': False,
            'error': str(e)
        }


def generate_with_replicate(prompt, negative_prompt, width, height, num_images, api_key):
    """
    Generate images using Replicate API
    Model: stability-ai/sdxl
    Documentation: https://replicate.com/docs/reference/http
    """
    url = "https://api.replicate.com/v1/predictions"

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",  # SDXL
        "input": {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_outputs": num_images,
            "num_inference_steps": 30,
            "guidance_scale": 7.5
        }
    }

    # Start prediction
    response = requests.post(url, json=payload, headers=headers, timeout=30)

    if response.status_code == 201:
        prediction = response.json()
        prediction_id = prediction['id']

        # Poll for completion (max 60 seconds)
        import time
        for _ in range(30):  # 30 attempts, 2 seconds each = 60s max
            time.sleep(2)

            status_response = requests.get(
                f"{url}/{prediction_id}",
                headers=headers,
                timeout=10
            )

            if status_response.status_code == 200:
                status_data = status_response.json()

                if status_data['status'] == 'succeeded':
                    output_urls = status_data.get('output', [])
                    images = [{'url': url} for url in output_urls]

                    return {
                        'success': True,
                        'images': images,
                        'cost': 0.02 * num_images  # Approximate cost
                    }
                elif status_data['status'] == 'failed':
                    return {
                        'success': False,
                        'error': status_data.get('error', 'Generation failed')
                    }

        # Timeout
        return {
            'success': False,
            'error': 'Generation timeout after 60 seconds'
        }
    else:
        error_msg = response.json().get('detail', response.text)
        logger.error(f"Replicate error: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }


def generate_with_stability(prompt, negative_prompt, width, height, num_images, api_key):
    """
    Generate images using Stability AI API
    Documentation: https://platform.stability.ai/docs/api-reference

    Session 769: Added cost tracking using api_cost_config
    """
    model_id = "stable-diffusion-xl-1024-v1-0"
    url = f"https://api.stability.ai/v1/generation/{model_id}/text-to-image"

    # Session 769: Calculate cost before making the API call
    resolution = f"{width}x{height}"
    cost_info = calculate_stability_cost(
        model=model_id,
        resolution=resolution,
        image_count=num_images
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1
            },
            {
                "text": negative_prompt,
                "weight": -1
            }
        ],
        "cfg_scale": 7,
        "height": height,
        "width": width,
        "samples": num_images,
        "steps": 30
    }

    response = requests.post(url, json=payload, headers=headers, timeout=60)

    if response.status_code == 200:
        result = response.json()
        images = []

        # Stability returns base64 encoded images
        for i, artifact in enumerate(result.get('artifacts', [])):
            if artifact.get('base64'):
                import base64
                image_data = base64.b64decode(artifact['base64'])

                # Create temporary URL (we'll save this properly in the main function)
                images.append({
                    'data': image_data,
                    'format': 'png'
                })

        logger.info(f"💰 Stability AI cost: ${cost_info['cost']:.4f} ({num_images} images @ {resolution})")

        return {
            'success': True,
            'images': images,
            'cost': float(cost_info['cost']),  # Session 769: Use calculated cost
            'cost_info': cost_info,  # Session 769: Full cost breakdown
        }
    else:
        error_msg = response.json().get('message', response.text)
        logger.error(f"Stability AI error: {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'cost_info': None,
        }

