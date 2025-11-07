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
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from PIL import Image as PILImage

logger = logging.getLogger(__name__)


# ========================================
# IMAGE HISTORY HELPER (Session 36: Feature 9)
# ========================================

def save_to_history(user, file_path, image_type, prompt='', parameters=None,
                    model_used='', style='', parent_image=None):
    """
    Helper function to save image to ImageHistory database.

    Args:
        user: User object
        file_path: Path to saved image file
        image_type: Type of image (generated, erased, inpainted, etc.)
        prompt: Prompt used for generation/editing
        parameters: Dict of parameters used
        model_used: Model name (core, sdxl, sd3, ultra)
        style: Style preset name
        parent_image: Parent ImageHistory object if this is an edit
    """
    try:
        from content.models import ImageHistory

        # Get image dimensions and file size
        full_path = default_storage.path(file_path)
        try:
            with PILImage.open(full_path) as img:
                width, height = img.size
        except Exception as e:
            logger.warning(f"Could not read image dimensions: {e}")
            width, height = None, None

        try:
            file_size = os.path.getsize(full_path)
        except Exception as e:
            logger.warning(f"Could not read file size: {e}")
            file_size = None

        # Create history record
        history = ImageHistory.objects.create(
            user=user,
            filename=os.path.basename(file_path),
            file_path=file_path,
            image_type=image_type,
            prompt=prompt,
            parameters=parameters or {},
            model_used=model_used,
            style=style,
            image_width=width,
            image_height=height,
            file_size_bytes=file_size,
            parent_image=parent_image
        )

        logger.info(f"✅ Saved to history: {image_type} - {history.filename} (ID: {history.id})")
        return history

    except Exception as e:
        logger.error(f"❌ Failed to save image history: {e}")
        # Don't fail the request if history save fails
        return None


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
        if not prompt:
            return Response({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)

        negative_prompt = data.get('negative_prompt', 'blurry, low quality, distorted')
        width = int(data.get('width', 1024))
        height = int(data.get('height', 1024))
        num_images = int(data.get('num_images', 1))
        style = data.get('style', 'photorealistic')
        quality = data.get('quality', 'balanced')  # NEW: Support for quality selector

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
        for img_data in generated_images:
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
                            file_path = default_storage.save(filename, ContentFile(image_data))
                            url = default_storage.url(file_path)
                        else:
                            continue
                    else:
                        # Regular HTTP/HTTPS URL - download it
                        response = requests.get(image_url, timeout=30)
                        if response.status_code == 200:
                            file_path = default_storage.save(filename, ContentFile(response.content))
                            url = default_storage.url(file_path)
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

                    # Save to history (Session 36: Feature 9)
                    save_to_history(
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
                        style=style
                    )

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


def generate_with_stability(prompt, negative_prompt, width, height, num_images, api_key):
    """
    Generate images using Stability AI API
    Documentation: https://platform.stability.ai/docs/api-reference
    """
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

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

        return {
            'success': True,
            'images': images,
            'cost': 0.04 * num_images  # Approximate cost
        }
    else:
        error_msg = response.json().get('message', response.text)
        logger.error(f"Stability AI error: {error_msg}")
        return {
            'success': False,
            'error': error_msg
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_image_generation(request):
    """
    Test endpoint to verify image generation is configured
    """
    stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
    replicate_key = os.getenv('REPLICATE_API_KEY') or settings.AI_PROVIDERS.get('REPLICATE_API_KEY')

    return Response({
        'success': True,
        'image_generation_configured': bool(stability_key or replicate_key),
        'providers': {
            'stability': {
                'configured': bool(stability_key),
                'status': 'ready' if stability_key else 'missing_api_key'
            },
            'replicate': {
                'configured': bool(replicate_key),
                'status': 'ready' if replicate_key else 'missing_api_key'
            }
        },
        'message': 'Image generation is ready' if (stability_key or replicate_key) else 'Configure API keys to enable image generation'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def optimize_image_prompt(request):
    """
    Optimize an image generation prompt using the Intelligent Prompting System
    
    Takes a simple prompt like "donkey walking a dog" and a style like "pixar"
    and returns an enhanced, detailed prompt for better image generation.
    
    Expected request body:
    {
        "prompt": "donkey walking a dog",
        "style": "pixar",
        "quality": "balanced"
    }
    
    Returns:
    {
        "success": true,
        "original_prompt": "donkey walking a dog",
        "enhanced_prompt": "A professional animated donkey character walking a friendly dog...",
        "negative_prompt": "...",
        "optimization_notes": "Added lighting details, anatomical specifications..."
    }
    """
    try:
        user = request.user
        data = request.data
        
        original_prompt = data.get('prompt', '').strip()
        style = data.get('style', '')
        quality = data.get('quality', 'balanced')
        
        if not original_prompt:
            return Response({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)
        
        logger.info(f"🎨 Optimizing prompt for {user.username}: '{original_prompt}' (style: {style})")
        
        # Build style-specific guidance
        style_guidance_map = {
            'pixar': 'Pixar-style 3D animation with expressive characters, smooth rendering, professional lighting',
            'disney': 'Disney animated style with vibrant colors, magical atmosphere, professional quality',
            'studio-ghibli': 'Studio Ghibli hand-drawn animation style, detailed backgrounds, atmospheric lighting',
            'dreamworks': 'DreamWorks animation style with dynamic poses, cinematic composition',
            'cinematic': 'Cinematic photography with dramatic lighting, professional composition, 8K quality',
            'photographic': 'Professional photography, crystal clear focus, proper exposure, realistic details',
            'anime': 'Anime art style with clean lines, vibrant colors, dynamic composition',
            'digital-art': 'Digital art style, highly detailed, professional quality, trending on ArtStation',
        }

        style_guidance = style_guidance_map.get(style.lower()) if style else None

        # Use the Intelligent Prompting System
        from core.agent_integration import IntelligentPromptOptimizer
        from content.ai_providers import AIProviderManager

        # Create a specialized optimization request for image generation
        # Build style instruction conditionally
        style_instruction = ""
        if style and style_guidance:
            style_instruction = f"3. Apply style-specific enhancements: {style_guidance}\n"

        optimization_request = f"""Enhance this image generation prompt for Stability AI:

Original Prompt: "{original_prompt}"
Style: {style or 'natural (no specific style)'}
Quality Level: {quality}

ENHANCEMENT REQUIREMENTS:
1. Keep the core concept from the original prompt
2. Add specific details about:
   - Character/subject anatomy (specify "two legs", "two arms", "perfect anatomy" for characters)
   - Lighting (golden hour, cinematic lighting, volumetric lighting, etc.)
   - Composition (hero shot, wide angle, close-up, etc.)
   - Quality markers (8K, professional, crystal clear, highly detailed)
   - Environment/background details
{style_instruction}{"3" if not style_instruction else "4"}. Avoid vague terms - be specific and descriptive
{"4" if not style_instruction else "5"}. Keep the enhanced prompt under 200 words

Return ONLY the enhanced prompt text, no explanations or formatting."""
        
        # Use AI to enhance the prompt
        ai_manager = AIProviderManager()
        try:
            response = ai_manager.generate_completion(
                prompt=optimization_request,
                provider='anthropic',  # Use Claude for prompt optimization
                model='claude-3-5-sonnet-20241022',
                max_tokens=500,
                temperature=0.7
            )
            
            enhanced_prompt = response.get('content', '').strip()
            
            # If AI fails, use rule-based enhancement as fallback
            if not enhanced_prompt or len(enhanced_prompt) < 20:
                enhanced_prompt = _enhance_prompt_rule_based(original_prompt, style, style_guidance)
            
        except Exception as e:
            logger.warning(f"AI optimization failed, using rule-based fallback: {e}")
            enhanced_prompt = _enhance_prompt_rule_based(original_prompt, style, style_guidance)
        
        # Generate style-specific negative prompt
        negative_prompt = "blurry, low quality, distorted, deformed, extra limbs, extra fingers, extra legs, bad anatomy, disfigured, mutated, ugly, poorly drawn, bad proportions, gross proportions"
        
        if style in ['pixar', 'disney', 'studio-ghibli', 'dreamworks', 'anime']:
            negative_prompt += ", realistic, photograph, 3D render"
        elif style in ['photographic', 'cinematic']:
            negative_prompt += ", cartoon, anime, illustrated, painting, drawing"
        
        logger.info(f"✅ Prompt optimized: {len(original_prompt)} → {len(enhanced_prompt)} chars")
        
        return Response({
            'success': True,
            'original_prompt': original_prompt,
            'enhanced_prompt': enhanced_prompt,
            'negative_prompt': negative_prompt,
            'style': style,
            'quality': quality,
            'optimization_method': 'ai_enhanced'
        })
        
    except Exception as e:
        logger.error(f"❌ Prompt optimization error: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'fallback_prompt': data.get('prompt', '')
        }, status=500)


def _enhance_prompt_rule_based(original_prompt: str, style: str, style_guidance: str = None) -> str:
    """
    Rule-based fallback for prompt enhancement when AI fails

    Args:
        original_prompt: The original user prompt
        style: The selected style (can be empty string)
        style_guidance: Style-specific guidance text (can be None if no style)
    """
    # Add anatomical specifications for character prompts
    character_keywords = ['person', 'man', 'woman', 'character', 'donkey', 'dog', 'cat', 'animal', 'creature']
    has_character = any(keyword in original_prompt.lower() for keyword in character_keywords)

    enhanced = original_prompt

    if has_character:
        enhanced += ", with perfect anatomy, correct proportions, two arms, two legs"

    # Add style guidance only if style is specified
    if style and style_guidance:
        enhanced += f", {style_guidance}"

    # Add quality markers
    enhanced += ", professional quality, highly detailed, 8K resolution, sharp focus"

    # Add lighting
    enhanced += ", cinematic lighting, dramatic shadows, golden hour"

    return enhanced


# ========================================
# IMAGE EDITING FUNCTIONS (Session 35)
# ========================================

@csrf_exempt
@api_view(['POST'])
def remove_background(request):
    """
    Remove background from an uploaded image using Stability AI.

    Expected request: Form data with 'image' file
    Returns: {success: true, image_url: 'data:image/png;base64,...'}
    """
    try:
        # Get uploaded image
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)

        image_file = request.FILES['image']

        # Get Stability AI API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🎭 Remove background request for {image_file.name}")

        # Call Stability AI remove-background API
        url = "https://api.stability.ai/v2beta/stable-image/edit/remove-background"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type)
        }

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            # Save the image to media directory for reliable downloads
            filename = f'background_removed_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)

            # Save to media directory
            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Background removed successfully - saved to {saved_path}")

            # Save to history (Session 36: Feature 9)
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='background_removed',
                prompt='',
                parameters={'operation': 'remove_background'}
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Remove background error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def recolor_image(request):
    """
    Recolor a specific object in an image using Stability AI.

    Expected request: Form data with:
    - 'image': image file
    - 'prompt': object to recolor (e.g., 'shirt')
    - 'select_prompt': object to recolor (same as prompt)
    - 'color': new color name (e.g., 'red', 'blue')

    Returns: {success: true, image_url: 'data:image/png;base64,...'}
    """
    try:
        # Get parameters
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)

        image_file = request.FILES['image']
        prompt = request.POST.get('prompt', '').strip()
        select_prompt = request.POST.get('select_prompt', prompt).strip()
        color = request.POST.get('color', '').strip()

        if not prompt or not color:
            return JsonResponse({
                'success': False,
                'error': 'Missing prompt or color'
            }, status=400)

        # Get Stability AI API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🎨 Recolor request: {prompt} → {color}")

        # Call Stability AI search-and-recolor API
        url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type)
        }

        data = {
            'prompt': f'{select_prompt}, {color}',
            'select_prompt': select_prompt,
            'output_format': 'png'
        }

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Save the image to media directory for reliable downloads
            filename = f'recolored_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)

            # Save to media directory
            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Recolor complete: {prompt} → {color} - saved to {saved_path}")

            # Save to history (Session 36: Feature 9)
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='recolored',
                prompt=f'Recolor {prompt} to {color}',
                parameters={
                    'operation': 'recolor',
                    'object': prompt,
                    'color': color
                }
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Recolor error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def upscale_image(request):
    """
    Upscale an image using Stability AI.

    Expected request: Form data with:
    - 'image': image file
    - 'method': 'fast' (4x), 'conservative' (4K), or 'creative' (AI enhancement)

    Returns: {success: true, image_url: 'data:image/png;base64,...'}
    """
    try:
        # Get parameters
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)

        image_file = request.FILES['image']
        method = request.POST.get('method', 'fast').strip().lower()

        # Validate method
        valid_methods = ['fast', 'conservative', 'creative']
        if method not in valid_methods:
            return JsonResponse({
                'success': False,
                'error': f'Invalid method. Must be one of: {", ".join(valid_methods)}'
            }, status=400)

        # Get Stability AI API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"📈 Upscale request: {method} method")

        # Resize image if needed (max 1,048,576 pixels = 1024x1024)
        from PIL import Image
        import io

        # Read image
        img = Image.open(image_file)
        width, height = img.size
        total_pixels = width * height

        logger.info(f"📏 Image dimensions: {width}x{height} = {total_pixels:,} pixels")

        # Resize if too large
        max_pixels = 1_048_576  # 1024x1024
        if total_pixels > max_pixels:
            # Calculate scaling factor
            scale = (max_pixels / total_pixels) ** 0.5
            new_width = int(width * scale)
            new_height = int(height * scale)

            logger.info(f"🔄 Resizing from {width}x{height} to {new_width}x{new_height}")
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save resized image to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            image_data = img_bytes.read()
        else:
            # Use original image
            image_file.seek(0)
            image_data = image_file.read()

        # Map method to Stability AI endpoint
        endpoint_map = {
            'fast': 'https://api.stability.ai/v2beta/stable-image/upscale/fast',
            'conservative': 'https://api.stability.ai/v2beta/stable-image/upscale/conservative',
            'creative': 'https://api.stability.ai/v2beta/stable-image/upscale/creative'
        }

        url = endpoint_map[method]

        files = {
            'image': (image_file.name, image_data, 'image/png')
        }

        data = {
            'output_format': 'png'
        }

        # Creative upscale requires a prompt
        if method == 'creative':
            data['prompt'] = 'enhance quality, add details, improve clarity'

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Check if we got an image or a job ID (creative upscale is async)
            content_type = response.headers.get('Content-Type', '')

            if 'application/json' in content_type:
                # Creative upscale returns a job ID - need to poll for result
                import json
                import time

                result_data = json.loads(response.text)
                generation_id = result_data.get('id')

                if not generation_id:
                    return JsonResponse({
                        'success': False,
                        'error': 'No generation ID received from Stability AI'
                    }, status=500)

                logger.info(f"🔄 Creative upscale job started: {generation_id}, polling for result...")

                # Poll for the result (max 60 seconds)
                result_url = f"https://api.stability.ai/v2beta/stable-image/upscale/creative/result/{generation_id}"

                for attempt in range(30):  # 30 attempts * 2 seconds = 60 seconds max
                    time.sleep(2)

                    result_response = requests.get(
                        result_url,
                        headers={
                            'Authorization': f'Bearer {stability_key}',
                            'Accept': 'image/*'
                        }
                    )

                    if result_response.status_code == 200:
                        # Got the image!
                        filename = f'upscaled_{method}_{uuid.uuid4().hex[:8]}.png'
                        filepath = os.path.join('generated_images', filename)
                        saved_path = default_storage.save(filepath, ContentFile(result_response.content))
                        image_url = default_storage.url(saved_path)

                        logger.info(f"✅ Creative upscale complete after {(attempt+1)*2}s - saved to {saved_path}")

                        # Save to history (Session 36: Feature 9)
                        save_to_history(
                            user=request.user,
                            file_path=saved_path,
                            image_type='upscaled_creative',
                            prompt='enhance quality, add details, improve clarity',
                            parameters={'operation': 'upscale', 'method': 'creative'}
                        )

                        return JsonResponse({
                            'success': True,
                            'image_url': image_url
                        })
                    elif result_response.status_code == 202:
                        # Still processing
                        logger.info(f"⏳ Still processing... attempt {attempt+1}/30")
                        continue
                    else:
                        # Error
                        logger.error(f"❌ Poll error: {result_response.status_code} - {result_response.text}")
                        return JsonResponse({
                            'success': False,
                            'error': f'Polling error: {result_response.text[:200]}'
                        }, status=500)

                # Timeout
                return JsonResponse({
                    'success': False,
                    'error': 'Creative upscale timed out after 60 seconds. Try fast or conservative method instead.'
                }, status=500)

            elif 'image' in content_type:
                # Fast/Conservative methods return image directly
                filename = f'upscaled_{method}_{uuid.uuid4().hex[:8]}.png'
                filepath = os.path.join('generated_images', filename)

                # Save to media directory
                saved_path = default_storage.save(filepath, ContentFile(response.content))
                image_url = default_storage.url(saved_path)

                logger.info(f"✅ Upscale complete: {method} method - saved to {saved_path}")

                # Save to history (Session 36: Feature 9)
                image_type_map = {
                    'fast': 'upscaled_fast',
                    'conservative': 'upscaled_conservative'
                }
                save_to_history(
                    user=request.user,
                    file_path=saved_path,
                    image_type=image_type_map.get(method, 'upscaled_fast'),
                    prompt='',
                    parameters={'operation': 'upscale', 'method': method}
                )

                return JsonResponse({
                    'success': True,
                    'image_url': image_url
                })
            else:
                logger.error(f"❌ Unexpected content type: {content_type}")
                return JsonResponse({
                    'success': False,
                    'error': f'Unexpected response type: {content_type}'
                }, status=500)
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Upscale error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def erase_object(request):
    """
    Erase objects from image using Stability AI erase endpoint.
    Requires: image file, mask (drawn areas to erase)
    """
    try:
        if 'image' not in request.FILES or 'mask' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Missing image or mask file'
            }, status=400)

        image_file = request.FILES['image']
        mask_file = request.FILES['mask']

        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🖌️ Erase request for {image_file.name}")

        url = "https://api.stability.ai/v2beta/stable-image/edit/erase"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type),
            'mask': (mask_file.name, mask_file.read(), mask_file.content_type)
        }

        data = {'output_format': 'png'}

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Save to server
            filename = f'erased_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)
            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Erase complete - saved to {saved_path}")

            # Save to history (Session 36: Feature 9)
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='erased',
                prompt='',
                parameters={'operation': 'erase'}
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI erase error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Erase error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def inpaint_image(request):
    """
    Inpaint (regenerate) areas of image using Stability AI inpaint endpoint.
    Requires: image file, mask (areas to regenerate), prompt (what to generate)
    """
    try:
        if 'image' not in request.FILES or 'mask' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Missing image or mask file'
            }, status=400)

        prompt = request.POST.get('prompt', '').strip()
        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Missing prompt'
            }, status=400)

        image_file = request.FILES['image']
        mask_file = request.FILES['mask']

        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEYS')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🎨 Inpaint request: {prompt}")

        url = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type),
            'mask': (mask_file.name, mask_file.read(), mask_file.content_type)
        }

        data = {
            'prompt': prompt,
            'output_format': 'png'
        }

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Save to server
            filename = f'inpainted_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)
            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Inpaint complete - saved to {saved_path}")

            # Save to history (Session 36: Feature 9)
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='inpainted',
                prompt=prompt,
                parameters={'operation': 'inpaint', 'prompt': prompt}
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI inpaint error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Inpaint error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def outpaint_image(request):
    """
    Outpaint (extend) image beyond edges using Stability AI outpaint endpoint.
    Session 64: Now supports multiple directions in one call!
    Requires: image file, directions (comma-separated: left,right,up,down), pixels, prompt
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Missing image file'
            }, status=400)

        prompt = request.POST.get('prompt', '').strip()
        directions_str = request.POST.get('directions', '').strip().lower()  # Session 64: Changed from 'direction' to 'directions'
        pixels_str = request.POST.get('pixels', '').strip()

        if not all([prompt, directions_str, pixels_str]):
            return JsonResponse({
                'success': False,
                'error': 'Missing prompt, directions, or pixels'
            }, status=400)

        try:
            pixels = int(pixels_str)
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid pixels value'
            }, status=400)

        # Session 64: Parse multiple directions (comma-separated)
        directions = [d.strip() for d in directions_str.split(',') if d.strip()]

        if not directions:
            return JsonResponse({
                'success': False,
                'error': 'No directions specified'
            }, status=400)

        # Validate all directions
        valid_directions = ['left', 'right', 'up', 'down']
        for direction in directions:
            if direction not in valid_directions:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid direction: {direction} (must be left/right/up/down)'
                }, status=400)

        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"📐 Multi-direction outpaint: {', '.join(directions)} by {pixels}px each - {prompt}")

        # Session 64: Sequential outpainting - each uses result from previous
        current_image_data = request.FILES['image'].read()
        current_filename = request.FILES['image'].name

        url = "https://api.stability.ai/v2beta/stable-image/edit/outpaint"
        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        # Process each direction sequentially
        for i, direction in enumerate(directions):
            logger.info(f"  📐 Step {i+1}/{len(directions)}: Extending {direction}...")

            files = {
                'image': (current_filename, current_image_data, 'image/png')
            }

            data = {
                'prompt': prompt,
                direction: pixels,  # e.g., 'left': 500
                'output_format': 'png'
            }

            response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code != 200:
                error_msg = response.text
                logger.error(f"❌ Stability AI outpaint error on {direction}: {error_msg}")
                return JsonResponse({
                    'success': False,
                    'error': f'Outpaint failed on {direction}: {error_msg}'
                }, status=500)

            # Use this result as input for next direction
            current_image_data = response.content
            logger.info(f"  ✅ {direction.capitalize()} extension complete")

        # Save final result
        filename = f'outpainted_{"_".join(directions)}_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', filename)
        saved_path = default_storage.save(filepath, ContentFile(current_image_data))
        image_url = default_storage.url(saved_path)

        logger.info(f"✅ Multi-direction outpaint complete - saved to {saved_path}")

        # Save to history (Session 36: Feature 9)
        save_to_history(
            user=request.user,
            file_path=saved_path,
            image_type='outpainted',
            prompt=prompt,
            parameters={
                'operation': 'outpaint',
                'directions': directions,  # Session 64: Save as list
                'pixels': pixels,
                'prompt': prompt
            }
        )

        return JsonResponse({
            'success': True,
            'image_url': image_url,
            'directions_completed': directions  # Session 64: Let frontend know what was done
        })

    except Exception as e:
        logger.error(f"❌ Outpaint error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# IMAGE HISTORY / GALLERY (Feature 9)
# ========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def image_history(request):
    """
    Retrieve user's image history for gallery display.

    Query parameters:
    - image_type: Filter by type (generated, erased, inpainted, upscaled_fast, etc.)
    - model_used: Filter by model (core, sdxl, sd3, ultra)
    - style: Filter by style preset
    - is_favorite: Filter favorites (true/false)
    - sort_by: Sort field (created_at, view_count, download_count) - default: -created_at
    - limit: Max results (default: 50)
    - offset: Pagination offset (default: 0)

    Returns:
    {
        "success": true,
        "images": [
            {
                "id": 123,
                "filename": "image.png",
                "url": "/media/...",
                "thumbnail_url": "/media/...",
                "image_type": "generated",
                "prompt": "...",
                "model_used": "sdxl",
                "style": "pixar",
                "width": 1024,
                "height": 1024,
                "created_at": "2025-11-03T...",
                "is_favorite": false,
                "view_count": 5,
                "download_count": 2,
                "has_children": true  // has edits
            }
        ],
        "total": 245,
        "limit": 50,
        "offset": 0
    }
    """
    try:
        from content.models import ImageHistory

        user = request.user

        # Start with user's images
        queryset = ImageHistory.objects.filter(user=user)

        # Apply filters
        image_type = request.query_params.get('image_type')
        if image_type:
            queryset = queryset.filter(image_type=image_type)

        model_used = request.query_params.get('model_used')
        if model_used:
            queryset = queryset.filter(model_used=model_used)

        style = request.query_params.get('style')
        if style:
            queryset = queryset.filter(style=style)

        is_favorite = request.query_params.get('is_favorite')
        if is_favorite is not None:
            queryset = queryset.filter(is_favorite=is_favorite.lower() == 'true')

        # Get total count
        total = queryset.count()

        # Apply sorting
        sort_by = request.query_params.get('sort_by', '-created_at')
        queryset = queryset.order_by(sort_by)

        # Apply pagination
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))

        queryset = queryset[offset:offset + limit]

        # Build response
        images = []
        for img in queryset:
            images.append({
                'id': img.id,
                'filename': img.filename,
                'url': img.get_full_url(),
                'thumbnail_url': img.get_thumbnail_url(),
                'image_type': img.image_type,
                'prompt': img.prompt,
                'model_used': img.model_used,
                'style': img.style,
                'width': img.image_width,
                'height': img.image_height,
                'file_size': img.file_size_bytes,
                'created_at': img.created_at.isoformat(),
                'is_favorite': img.is_favorite,
                'view_count': img.view_count,
                'download_count': img.download_count,
                'has_children': img.child_images.exists(),
                'user_notes': img.user_notes,
                'tags': img.tags
            })

        logger.info(f"📊 Gallery request: returned {len(images)}/{total} images for {user.username}")

        return Response({
            'success': True,
            'images': images,
            'total': total,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"❌ Image history error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, image_id):
    """
    Toggle favorite status for an image.

    Returns updated favorite status.
    """
    try:
        from content.models import ImageHistory

        image = ImageHistory.objects.get(id=image_id, user=request.user)
        image.is_favorite = not image.is_favorite
        image.save(update_fields=['is_favorite'])

        logger.info(f"⭐ Toggled favorite for image {image_id}: {image.is_favorite}")

        return Response({
            'success': True,
            'is_favorite': image.is_favorite
        })

    except ImageHistory.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Image not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Toggle favorite error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_image(request, image_id):
    """
    Delete an image from history.

    Also deletes the actual file from storage.
    """
    try:
        from content.models import ImageHistory

        image = ImageHistory.objects.get(id=image_id, user=request.user)

        # Delete file from storage
        try:
            if default_storage.exists(image.file_path):
                default_storage.delete(image.file_path)
            if image.thumbnail and default_storage.exists(image.thumbnail):
                default_storage.delete(image.thumbnail)
        except Exception as e:
            logger.warning(f"⚠️ Could not delete files for image {image_id}: {e}")

        # Delete database record
        image.delete()

        logger.info(f"🗑️ Deleted image {image_id} for {request.user.username}")

        return Response({
            'success': True,
            'message': 'Image deleted successfully'
        })

    except ImageHistory.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Image not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Delete image error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# BATCH DOWNLOAD (Session 37: Feature 10)
# ========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_download_images(request):
    """
    Download multiple images as a ZIP file.

    Expects JSON: { "image_ids": ["uuid1", "uuid2", ...] }

    Returns ZIP file containing:
    - All selected images
    - metadata.json with image information
    """
    try:
        from content.models import ImageHistory

        image_ids = request.data.get('image_ids', [])

        if not image_ids:
            return Response({
                'success': False,
                'error': 'No images selected'
            }, status=400)

        # Fetch images for this user only
        images = ImageHistory.objects.filter(
            id__in=image_ids,
            user=request.user
        ).order_by('-created_at')

        if not images.exists():
            return Response({
                'success': False,
                'error': 'No images found'
            }, status=404)

        logger.info(f"📦 Creating ZIP with {images.count()} images for {request.user.username}")

        # Create ZIP file in memory
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:

            # Metadata for JSON file
            metadata = {
                'downloaded_at': datetime.now().isoformat(),
                'total_images': images.count(),
                'images': []
            }

            # Add each image to ZIP
            for idx, img in enumerate(images, 1):
                try:
                    # Get file from storage
                    if not default_storage.exists(img.file_path):
                        logger.warning(f"⚠️ File not found: {img.file_path}")
                        continue

                    # Read file data
                    logger.info(f"📂 Reading file: {img.file_path}")
                    with default_storage.open(img.file_path, 'rb') as f:
                        image_data = f.read()

                    # Create unique filename
                    file_ext = os.path.splitext(img.filename)[1] or '.png'
                    safe_filename = f"{idx:03d}_{img.image_type}_{img.id}{file_ext}"

                    # Add to ZIP
                    zip_file.writestr(safe_filename, image_data)
                    logger.info(f"✅ Added {safe_filename} to ZIP ({len(image_data)} bytes)")

                    # Build metadata entry with safe defaults
                    try:
                        metadata_entry = {
                            'filename': safe_filename,
                            'original_filename': img.filename or 'unknown.png',
                            'image_type': img.image_type or 'unknown',
                            'prompt': img.prompt or '',
                            'model_used': img.model_used or '',
                            'style': img.style or '',
                            'dimensions': f"{img.image_width or 0}x{img.image_height or 0}",
                            'file_size_bytes': img.file_size_bytes or 0,
                            'created_at': img.created_at.isoformat() if img.created_at else '',
                            'is_favorite': bool(img.is_favorite),
                            'tags': img.tags or '',
                            'parameters': img.parameters if img.parameters else {}
                        }
                        metadata['images'].append(metadata_entry)
                        logger.info(f"📝 Added metadata for {safe_filename}")
                    except Exception as meta_error:
                        logger.error(f"❌ Error building metadata for {img.id}: {meta_error}", exc_info=True)
                        # Add simplified metadata entry
                        metadata['images'].append({
                            'filename': safe_filename,
                            'image_type': str(img.image_type),
                            'error': 'Metadata partially unavailable'
                        })

                except Exception as e:
                    logger.error(f"❌ Error processing image {img.id}: {e}", exc_info=True)
                    continue

            # Add metadata.json
            metadata_json = json.dumps(metadata, indent=2)
            zip_file.writestr('metadata.json', metadata_json)
            logger.info("✅ Added metadata.json to ZIP")

        # Prepare response
        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="images_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip"'

        logger.info(f"🎉 ZIP created successfully with {images.count()} images")

        return response

    except Exception as e:
        logger.error(f"❌ Batch download error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# SESSION 38: FEATURE 11 - IMAGE-TO-IMAGE CONTROL
# =============================================================================

def control_sketch(request):
    """
    Convert a sketch into a refined image using Stability AI Control Sketch.

    Expected request: Form data with:
    - 'image': sketch image file (can be hand-drawn or canvas generated)
    - 'prompt': text description of desired result
    - 'control_strength': float 0-1 (how much to follow sketch, default 0.7)
    - 'negative_prompt': optional negative prompt

    Returns: {success: true, image_url: 'url_to_generated_image'}
    """
    try:
        # Validate inputs
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No sketch image provided'
            }, status=400)

        sketch_file = request.FILES['image']
        prompt = request.POST.get('prompt', '').strip()
        control_strength = float(request.POST.get('control_strength', 0.7))
        negative_prompt = request.POST.get('negative_prompt', '').strip()

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🎨 Control Sketch request: {prompt} (strength: {control_strength})")

        # Call Stability AI control/sketch endpoint
        url = "https://api.stability.ai/v2beta/stable-image/control/sketch"

        files = {
            'image': (sketch_file.name, sketch_file.read(), sketch_file.content_type or 'image/png')
        }

        data = {
            'prompt': prompt,
            'control_strength': control_strength,
            'output_format': 'png'
        }

        if negative_prompt:
            data['negative_prompt'] = negative_prompt

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Save the generated image
            filename = f'sketch_control_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)

            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Sketch control complete - saved to {saved_path}")

            # Save to history
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='sketch_control',
                prompt=prompt,
                parameters={
                    'operation': 'control_sketch',
                    'control_strength': control_strength,
                    'negative_prompt': negative_prompt
                }
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Control sketch error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def control_structure(request):
    """
    Transform an image while maintaining its structure using Stability AI Control Structure.

    Expected request: Form data with:
    - 'image': reference image file (structure will be preserved)
    - 'prompt': text description of desired style/transformation
    - 'control_strength': float 0-1 (how much to follow structure, default 0.7)
    - 'negative_prompt': optional negative prompt

    Returns: {success: true, image_url: 'url_to_generated_image'}
    """
    try:
        # Validate inputs
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No reference image provided'
            }, status=400)

        ref_image = request.FILES['image']
        prompt = request.POST.get('prompt', '').strip()
        control_strength = float(request.POST.get('control_strength', 0.7))
        negative_prompt = request.POST.get('negative_prompt', '').strip()

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🏗️ Control Structure request: {prompt} (strength: {control_strength})")

        # Call Stability AI control/structure endpoint
        url = "https://api.stability.ai/v2beta/stable-image/control/structure"

        files = {
            'image': (ref_image.name, ref_image.read(), ref_image.content_type or 'image/png')
        }

        data = {
            'prompt': prompt,
            'control_strength': control_strength,
            'output_format': 'png'
        }

        if negative_prompt:
            data['negative_prompt'] = negative_prompt

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Save the generated image
            filename = f'structure_control_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)

            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Structure control complete - saved to {saved_path}")

            # Save to history
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='structure_control',
                prompt=prompt,
                parameters={
                    'operation': 'control_structure',
                    'control_strength': control_strength,
                    'negative_prompt': negative_prompt
                }
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Control structure error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# WORKFLOW EXECUTION (Session 41: Real API Integration)
# ========================================

@csrf_exempt
@api_view(['POST'])
def execute_workflow_step(request):
    """
    Execute a single workflow step by routing to the appropriate operation.

    Expected JSON request body:
    {
        "operation": "upscale_fast" | "upscale_conservative" | "upscale_creative" |
                     "remove_background" | "recolor" | "erase" | "inpaint" |
                     "outpaint" | "sketch" | "structure" | "generate",
        "inputImageUrl": "url_to_image" (required for all except generate),
        "config": {
            // Operation-specific parameters
            "prompt": "...",           // for generate, recolor, inpaint, outpaint, sketch, structure
            "search_prompt": "...",    // for recolor
            "select_prompt": "...",    // for recolor
            "creativity": 0.5,         // for outpaint
            "direction": "up",         // for outpaint
            "control_strength": 0.7,   // for sketch, structure
            // ... etc
        }
    }

    Returns: {success: true, imageUrl: "url_to_result_image"}
    """
    try:
        # Parse JSON request (DRF already parses request.body for us)
        data = request.data
        operation = (data.get('operation') or '').strip().lower()
        input_image_url = (data.get('inputImageUrl') or '').strip()
        config = data.get('config', {})

        logger.info(f"🎭 Workflow step execution: {operation}")

        # Validate operation
        valid_operations = [
            'upscale_fast', 'upscale_conservative', 'upscale_creative',
            'remove_background', 'recolor', 'erase', 'inpaint', 'outpaint',
            'sketch', 'structure', 'generate'
        ]

        if operation not in valid_operations:
            return JsonResponse({
                'success': False,
                'error': f'Invalid operation: {operation}'
            }, status=400)

        # Download input image if URL provided (all operations except generate need this)
        image_file = None
        if input_image_url and operation != 'generate':
            try:
                # Download image from URL
                if input_image_url.startswith('http'):
                    img_response = requests.get(input_image_url, timeout=10)
                    img_response.raise_for_status()
                    image_data = img_response.content
                elif input_image_url.startswith('/media/'):
                    # Local file - read from filesystem
                    local_path = os.path.join(settings.MEDIA_ROOT, input_image_url.replace('/media/', ''))
                    with open(local_path, 'rb') as f:
                        image_data = f.read()
                elif input_image_url.startswith('data:image'):
                    # Data URI - extract base64 data
                    if 'base64,' in input_image_url:
                        base64_data = input_image_url.split('base64,')[1]
                        image_data = base64.b64decode(base64_data)
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': 'Invalid data URI format'
                        }, status=400)
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid image URL format'
                    }, status=400)

                # Check and resize if needed (Stability AI limits: 10MiB file size, 1,048,576 pixels)
                # Note: Different operations have different limits, using most conservative (1024x1024)
                from PIL import Image
                import io

                max_size_bytes = 10 * 1024 * 1024  # 10MiB
                max_pixels = 1_048_576  # 1024x1024 (most conservative limit across all operations)

                # Open image to check dimensions
                img = Image.open(io.BytesIO(image_data))
                width, height = img.size
                total_pixels = width * height

                logger.info(f"📏 Original image: {width}x{height} = {total_pixels:,} pixels, {len(image_data):,} bytes")

                # Check if we need to resize due to pixel count
                needs_resize = False
                if total_pixels > max_pixels:
                    # Calculate scale factor to fit within pixel limit
                    scale_factor = (max_pixels / total_pixels) ** 0.5
                    new_width = int(width * scale_factor)
                    new_height = int(height * scale_factor)

                    logger.info(f"⚠️ Too many pixels ({total_pixels:,}), resizing to {new_width}x{new_height}")

                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    needs_resize = True

                # Check if we need to resize due to file size
                if needs_resize or len(image_data) > max_size_bytes:
                    logger.info(f"⚠️ Optimizing image size...")

                    # Save with optimization
                    quality = 85
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='PNG', optimize=True, quality=quality)
                    image_data = img_bytes.getvalue()

                    # If still too large, reduce quality iteratively
                    while len(image_data) > max_size_bytes and quality > 60:
                        quality -= 10
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='PNG', optimize=True, quality=quality)
                        image_data = img_bytes.getvalue()

                    logger.info(f"✅ Optimized image to {len(image_data):,} bytes (quality={quality})")

                # Create a file-like object
                from django.core.files.uploadedfile import InMemoryUploadedFile

                image_io = io.BytesIO(image_data)
                image_file = InMemoryUploadedFile(
                    image_io,
                    field_name='image',
                    name=f'workflow_input_{uuid.uuid4().hex[:8]}.png',
                    content_type='image/png',
                    size=len(image_data),
                    charset=None
                )

                logger.info(f"✅ Downloaded input image: {len(image_data):,} bytes")

            except Exception as e:
                logger.error(f"❌ Failed to download input image: {e}")
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to download input image: {str(e)}'
                }, status=500)

        # Route to appropriate operation
        if operation == 'upscale_fast':
            # Call Stability AI directly
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/upscale/fast'

                # Prepare image data
                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {'output_format': 'png'}
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'upscaled_fast_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='upscaled_fast',
                        prompt='Fast Upscale (4x)'
                    )

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Fast upscale failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'upscale_conservative':
            # Call Stability AI directly
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/upscale/conservative'

                # Prepare image data
                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}

                # Conservative upscale requires a prompt
                prompt = config.get('prompt', 'High quality image, detailed, sharp')
                data = {
                    'output_format': 'png',
                    'prompt': prompt
                }
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'upscaled_conservative_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='upscaled_conservative',
                        prompt='Conservative Upscale (4K)'
                    )

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Conservative upscale failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'upscale_creative':
            # Call Stability AI directly
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/upscale/creative'

                # Prepare image data
                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {
                    'output_format': 'png',
                    'prompt': config.get('prompt', 'enhance quality, add details, improve clarity')
                }
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'application/json'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    # Creative upscale is async - poll for result
                    import time
                    result_data = response.json()
                    generation_id = result_data.get('id')

                    result_url = f"https://api.stability.ai/v2beta/stable-image/upscale/creative/result/{generation_id}"

                    for attempt in range(30):
                        time.sleep(2)
                        result_response = requests.get(
                            result_url,
                            headers={'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}
                        )

                        if result_response.status_code == 200:
                            filename = f'upscaled_creative_{uuid.uuid4().hex[:8]}.png'
                            filepath = os.path.join('generated_images', request.user.username, filename)
                            saved_path = default_storage.save(filepath, ContentFile(result_response.content))
                            image_url = default_storage.url(saved_path)

                            # Save to history
                            from content.models import ImageHistory
                            ImageHistory.objects.create(
                                user=request.user,
                                filename=filename,
                                file_path=saved_path,
                                image_type='upscaled_creative',
                                prompt=config.get('prompt', 'enhance quality')
                            )

                            return JsonResponse({'success': True, 'image_url': image_url})

                    return JsonResponse({'success': False, 'error': 'Timeout waiting for creative upscale'}, status=500)
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Creative upscale failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'remove_background':
            # Call Stability AI directly
            try:
                from PIL import Image
                img = Image.open(image_file)

                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/remove-background'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {'output_format': 'png'}
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'removed_bg_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    from content.models import ImageHistory
                    ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='background_removed',
                        prompt='Remove Background'
                    )

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Remove background failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'recolor':
            # Recolor uses automatic object detection
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Validate required config
                if not config:
                    config = {}

                search_prompt = config.get('search_prompt', '').strip()
                prompt = config.get('prompt', '').strip()

                # Provide helpful defaults if empty
                if not search_prompt:
                    search_prompt = 'object'
                if not prompt:
                    prompt = 'red color'

                logger.info(f"🎨 Recolor: '{search_prompt}' → '{prompt}'")

                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {
                    'prompt': prompt,
                    'search_prompt': search_prompt,
                    'select_prompt': config.get('select_prompt', search_prompt),
                    'output_format': 'png'
                }
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'recolored_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    from content.models import ImageHistory
                    ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='recolored',
                        prompt=f"Recolor {config.get('search_prompt', 'object')} to {config.get('prompt', 'red')}"
                    )

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Recolor failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'outpaint':
            # Outpaint uses direction parameters
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Validate config
                if not config:
                    config = {}

                # Check if at least one direction is selected
                has_direction = any([
                    config.get('left'),
                    config.get('right'),
                    config.get('up'),
                    config.get('down')
                ])

                if not has_direction:
                    # Default to extending right
                    logger.info("⚠️ No direction specified, defaulting to right")
                    config['right'] = True

                logger.info(f"📐 Outpaint directions: L={config.get('left')} R={config.get('right')} U={config.get('up')} D={config.get('down')}")

                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/outpaint'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {
                    'output_format': 'png',
                    'creativity': config.get('creativity', 0.5)
                }

                # Add prompt if provided
                prompt = config.get('prompt', '').strip()
                if prompt:
                    data['prompt'] = prompt

                # Add direction parameters (in pixels, max 2000 per side)
                if config.get('left'):
                    data['left'] = 500
                if config.get('right'):
                    data['right'] = 500
                if config.get('up'):
                    data['up'] = 500
                if config.get('down'):
                    data['down'] = 500

                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'outpainted_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    from content.models import ImageHistory
                    ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='outpainted',
                        prompt=config.get('prompt', 'Extend image')
                    )

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Outpaint failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'erase':
            # Erase object using mask from workflow
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Check for mask data
                mask_data = config.get('maskData', '').strip()
                if not mask_data:
                    return JsonResponse({
                        'success': False,
                        'error': 'Missing mask. Please draw areas to erase.'
                    }, status=400)

                # Decode base64 mask
                if 'base64,' in mask_data:
                    mask_data = mask_data.split('base64,')[1]
                mask_bytes = base64.b64decode(mask_data)

                # Create file-like object for mask
                mask_io = io.BytesIO(mask_bytes)
                mask_file = InMemoryUploadedFile(
                    mask_io,
                    field_name='mask',
                    name='mask.png',
                    content_type='image/png',
                    size=len(mask_bytes),
                    charset=None
                )

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/erase'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {
                    'image': ('image.png', img_bytes.read(), 'image/png'),
                    'mask': ('mask.png', mask_file.read(), 'image/png')
                }
                data = {'output_format': 'png'}
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'erased_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='erased',
                        prompt='Erase Object'
                    )

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Erase failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'inpaint':
            # Inpaint using mask and prompt from workflow
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Check for mask data
                mask_data = config.get('maskData', '').strip()
                if not mask_data:
                    return JsonResponse({
                        'success': False,
                        'error': 'Missing mask. Please draw areas to inpaint.'
                    }, status=400)

                # Check for prompt
                prompt = config.get('prompt', '').strip()
                if not prompt:
                    return JsonResponse({
                        'success': False,
                        'error': 'Missing prompt. What should we fill the area with?'
                    }, status=400)

                # Decode base64 mask
                if 'base64,' in mask_data:
                    mask_data = mask_data.split('base64,')[1]
                mask_bytes = base64.b64decode(mask_data)

                # Create file-like object for mask
                mask_io = io.BytesIO(mask_bytes)
                mask_file = InMemoryUploadedFile(
                    mask_io,
                    field_name='mask',
                    name='mask.png',
                    content_type='image/png',
                    size=len(mask_bytes),
                    charset=None
                )

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/inpaint'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {
                    'image': ('image.png', img_bytes.read(), 'image/png'),
                    'mask': ('mask.png', mask_file.read(), 'image/png')
                }
                data = {
                    'prompt': prompt,
                    'output_format': 'png'
                }
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'inpainted_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='inpainted',
                        prompt=prompt
                    )

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Inpaint failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'generate':
            # Generate image from prompt
            try:
                from content.image_generation import ImageGenerationService

                # Use improved_prompt if available, fallback to basic prompt
                # Session 61: This ensures GPT-5 enhanced prompts are actually used!
                prompt = config.get('improved_prompt') or config.get('prompt', '')
                if not prompt:
                    return JsonResponse({
                        'success': False,
                        'error': 'Prompt is required for generate operation'
                    }, status=400)

                # Get configuration
                style = config.get('style', '')
                quality = config.get('quality', 'balanced')  # fast, balanced, high, premium
                negative_prompt = config.get('negative_prompt', '')

                # Session 61: Add strong negative prompts for logo generation to prevent text/brands
                # If style indicates this is a logo, add logo-specific negative prompts
                if style in ['vector', 'flat'] or 'logo' in prompt.lower():
                    logo_negative = 'text, letters, words, typography, starbucks, nike, apple, brand names, existing logos, trademarks, copyrighted logos, photographic, realistic, people, crowds'
                    negative_prompt = f'{logo_negative}, {negative_prompt}' if negative_prompt else logo_negative
                    logger.info(f"🚫 Added logo-specific negative prompts to prevent text/brands")

                # Map quality to model
                quality_map = {
                    'fast': 'core',
                    'balanced': 'sdxl',
                    'high': 'sd3',
                    'premium': 'ultra'
                }
                model = quality_map.get(quality, 'sdxl')

                logger.info(f"🎨 Generating image: prompt='{prompt[:50]}...', model={model}, style={style}")

                # Generate image
                generator = ImageGenerationService()
                result = generator.generate_image(
                    prompt=prompt,
                    model=model,
                    style=style,
                    negative_prompt=negative_prompt,
                    aspect_ratio='1:1'
                )

                if result.success and result.images:
                    # Save the generated image
                    # Extract base64 data from data URI (format: "data:image/png;base64,...")
                    data_uri = result.images[0]
                    if 'base64,' in data_uri:
                        base64_data = data_uri.split('base64,')[1]
                    else:
                        base64_data = data_uri
                    image_data = base64.b64decode(base64_data)
                    filename = f'generated_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(image_data))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='generated',
                        prompt=prompt
                    )

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({
                        'success': False,
                        'error': result.error_message or 'Generation failed'
                    }, status=500)

            except Exception as e:
                logger.error(f"❌ Generate failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation in ['sketch', 'structure']:
            # These operations need separate implementations
            return JsonResponse({
                'success': False,
                'error': f'Operation "{operation}" requires different implementation. Please use the dedicated tab.'
            }, status=400)

        else:
            return JsonResponse({
                'success': False,
                'error': f'Operation not implemented: {operation}'
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        logger.error(f"❌ Workflow step execution error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# UNIFIED GALLERY API (Session 53: Phase 2)
# ========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unified_batch_download(request):
    """
    Download multiple items (images, videos, audio) as a ZIP file.

    Expects JSON: {
        "items": [
            {"id": "uuid1", "type": "image"},
            {"id": "uuid2", "type": "video"},
            ...
        ]
    }

    Returns ZIP file containing:
    - All selected media files
    - metadata.json with information about all items
    """
    try:
        from content.models import ImageHistory, VideoHistory
        from django.http import HttpResponse
        import zipfile
        from io import BytesIO
        import os

        items = request.data.get('items', [])

        if not items:
            return Response({
                'success': False,
                'error': 'No items selected'
            }, status=400)

        logger.info(f"📦 Creating unified ZIP with {len(items)} items for {request.user.username}")

        # Separate items by type
        image_ids = [item['id'] for item in items if item['type'] == 'image']
        video_ids = [item['id'] for item in items if item['type'] == 'video']

        # Fetch all items for this user only
        images = ImageHistory.objects.filter(
            id__in=image_ids,
            user=request.user
        ).order_by('-created_at')

        videos = VideoHistory.objects.filter(
            id__in=video_ids,
            user=request.user,
            status='completed'
        ).order_by('-created_at')

        total_items = images.count() + videos.count()

        if total_items == 0:
            return Response({
                'success': False,
                'error': 'No items found'
            }, status=404)

        logger.info(f"📦 Found {images.count()} images and {videos.count()} videos")

        # Create ZIP file in memory
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:

            # Metadata for JSON file
            metadata = {
                'downloaded_at': datetime.now().isoformat(),
                'total_items': total_items,
                'total_images': images.count(),
                'total_videos': videos.count(),
                'items': []
            }

            item_counter = 1

            # Add images to ZIP
            for img in images:
                try:
                    # Get file from storage
                    if not default_storage.exists(img.file_path):
                        logger.warning(f"⚠️ File not found: {img.file_path}")
                        continue

                    # Read file data
                    with default_storage.open(img.file_path, 'rb') as f:
                        image_data = f.read()

                    # Create unique filename
                    file_ext = os.path.splitext(img.filename)[1] or '.png'
                    safe_filename = f"{item_counter:03d}_image_{img.image_type}_{img.id}{file_ext}"

                    # Add to ZIP
                    zip_file.writestr(safe_filename, image_data)
                    logger.info(f"✅ Added {safe_filename} to ZIP ({len(image_data)} bytes)")

                    # Add metadata
                    metadata['items'].append({
                        'filename': safe_filename,
                        'type': 'image',
                        'image_type': img.image_type or 'unknown',
                        'prompt': img.prompt or '',
                        'model_used': img.model_used or '',
                        'style': img.style or '',
                        'dimensions': f"{img.image_width or 0}x{img.image_height or 0}",
                        'file_size_bytes': img.file_size_bytes or 0,
                        'created_at': img.created_at.isoformat() if img.created_at else '',
                        'is_favorite': bool(img.is_favorite),
                        'parameters': img.parameters if img.parameters else {}
                    })

                    item_counter += 1

                except Exception as e:
                    logger.error(f"❌ Error processing image {img.id}: {e}")
                    continue

            # Add videos to ZIP
            for video in videos:
                try:
                    # Videos are stored by URL, need to download them
                    import requests

                    # Download video
                    response = requests.get(video.video_url, timeout=60)
                    response.raise_for_status()
                    video_data = response.content

                    # Create unique filename
                    file_ext = '.mp4'  # Runway videos are MP4
                    safe_filename = f"{item_counter:03d}_video_{video.video_type}_{video.id}{file_ext}"

                    # Add to ZIP
                    zip_file.writestr(safe_filename, video_data)
                    logger.info(f"✅ Added {safe_filename} to ZIP ({len(video_data)} bytes)")

                    # Add metadata
                    metadata['items'].append({
                        'filename': safe_filename,
                        'type': 'video',
                        'video_type': video.video_type or 'unknown',
                        'prompt': video.prompt or '',
                        'model_used': video.model_used or '',
                        'duration': video.duration,
                        'ratio': video.ratio or '',
                        'dimensions': f"{video.dimensions}" if video.dimensions else '',
                        'file_size_bytes': len(video_data),
                        'created_at': video.created_at.isoformat() if video.created_at else '',
                        'is_favorite': bool(video.is_favorite),
                        'parameters': video.parameters if video.parameters else {}
                    })

                    item_counter += 1

                except Exception as e:
                    logger.error(f"❌ Error processing video {video.id}: {e}")
                    continue

            # Add metadata.json
            metadata_json = json.dumps(metadata, indent=2)
            zip_file.writestr('metadata.json', metadata_json)
            logger.info("✅ Added metadata.json to ZIP")

        # Prepare response
        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="donkey_betz_content_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip"'

        logger.info(f"🎉 Unified ZIP created successfully with {total_items} items")

        return response

    except Exception as e:
        logger.error(f"❌ Unified batch download error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unified_toggle_favorite(request):
    """
    Toggle favorite status for any media type (image, video, audio).

    Expects JSON: {
        "id": "uuid",
        "type": "image" | "video" | "audio"
    }

    Returns: {
        "success": true,
        "is_favorite": true/false
    }
    """
    try:
        from content.models import ImageHistory, VideoHistory

        item_id = request.data.get('id')
        item_type = request.data.get('type')

        if not item_id or not item_type:
            return Response({
                'success': False,
                'error': 'Missing id or type'
            }, status=400)

        # Toggle favorite based on type
        if item_type == 'image':
            try:
                item = ImageHistory.objects.get(id=item_id, user=request.user)
                item.is_favorite = not item.is_favorite
                item.save()

                logger.info(f"{'⭐' if item.is_favorite else '☆'} Image {item_id} favorite: {item.is_favorite}")

                return Response({
                    'success': True,
                    'is_favorite': item.is_favorite
                })

            except ImageHistory.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Image not found'
                }, status=404)

        elif item_type == 'video':
            try:
                item = VideoHistory.objects.get(id=item_id, user=request.user)
                item.is_favorite = not item.is_favorite
                item.save()

                logger.info(f"{'⭐' if item.is_favorite else '☆'} Video {item_id} favorite: {item.is_favorite}")

                return Response({
                    'success': True,
                    'is_favorite': item.is_favorite
                })

            except VideoHistory.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Video not found'
                }, status=404)

        else:
            return Response({
                'success': False,
                'error': f'Unsupported type: {item_type}'
            }, status=400)

    except Exception as e:
        logger.error(f"❌ Unified toggle favorite error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_image_view(request, image_id):
    """
    Track when a user views an image in fullsize.

    URL: POST /api/images/view/<uuid>/
    """
    try:
        image = ImageHistory.objects.get(id=image_id, user=request.user)
        image.view_count += 1
        image.save(update_fields=['view_count'])

        logger.info(f"✅ Image view tracked: {image_id} (total: {image.view_count})")

        return Response({
            'success': True,
            'view_count': image.view_count
        })
    except ImageHistory.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Image not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Track image view error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_image_download(request, image_id):
    """
    Track when a user downloads an image.

    URL: POST /api/images/download/<uuid>/
    """
    try:
        image = ImageHistory.objects.get(id=image_id, user=request.user)
        image.download_count += 1
        image.save(update_fields=['download_count'])

        logger.info(f"✅ Image download tracked: {image_id} (total: {image.download_count})")

        return Response({
            'success': True,
            'download_count': image.download_count
        })
    except ImageHistory.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Image not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Track image download error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unified_gallery(request):
    """
    Unified gallery endpoint combining images, videos, and audio.

    Query parameters:
    - type: Filter by media type (all/images/videos/audio) - default: all
    - favorite: Filter favorites (true/false)
    - search: Search term (searches in prompts)
    - sort_by: Sort field (-created_at, created_at, -view_count, etc.) - default: -created_at
    - limit: Max results (default: 20)
    - offset: Pagination offset (default: 0)

    Returns:
    {
        "count": 100,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": "uuid",
                "type": "image" | "video" | "audio",
                "url": "...",
                "thumbnail_url": "...",
                "prompt": "...",
                "created_at": "...",
                "is_favorite": true/false,
                "view_count": 10,
                "download_count": 5,
                "model_used": "...",
                "parameters": {...},
                // Type-specific fields
                "image_type": "generated" (for images),
                "video_type": "text_to_video" (for videos),
                ...
            }
        ]
    }
    """
    try:
        from content.models import ImageHistory, VideoHistory
        from django.db.models import Q

        user = request.user

        # Get query parameters
        media_type = request.query_params.get('type', 'all').lower()
        is_favorite = request.query_params.get('favorite')
        search_term = request.query_params.get('search', '').strip()
        sort_by = request.query_params.get('sort_by', '-created_at')
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))

        # Collect results from different media types
        all_items = []

        # Fetch images if requested
        if media_type in ['all', 'images']:
            image_queryset = ImageHistory.objects.filter(user=user)

            # Apply filters
            if is_favorite is not None:
                image_queryset = image_queryset.filter(is_favorite=is_favorite.lower() == 'true')

            if search_term:
                image_queryset = image_queryset.filter(
                    Q(prompt__icontains=search_term) |
                    Q(user_notes__icontains=search_term)
                )

            # Convert to unified format
            for img in image_queryset:
                all_items.append({
                    'id': str(img.id),
                    'type': 'image',
                    'url': img.get_full_url(),
                    'thumbnail_url': img.get_thumbnail_url(),
                    'prompt': img.prompt,
                    'created_at': img.created_at,
                    'is_favorite': img.is_favorite,
                    'view_count': img.view_count,
                    'download_count': img.download_count,
                    'model_used': img.model_used,
                    'parameters': img.parameters,
                    # Image-specific fields
                    'image_type': img.image_type,
                    'style': img.style,
                    'width': img.image_width,
                    'height': img.image_height,
                    'filename': img.filename,
                    'user_notes': img.user_notes,
                    'tags': img.tags,
                })

        # Fetch videos if requested
        if media_type in ['all', 'videos']:
            video_queryset = VideoHistory.objects.filter(user=user, status='completed')

            # Apply filters
            if is_favorite is not None:
                video_queryset = video_queryset.filter(is_favorite=is_favorite.lower() == 'true')

            if search_term:
                video_queryset = video_queryset.filter(
                    Q(prompt__icontains=search_term) |
                    Q(user_notes__icontains=search_term)
                )

            # Convert to unified format
            for video in video_queryset:
                all_items.append({
                    'id': str(video.id),
                    'type': 'video',
                    'url': video.video_url,
                    'thumbnail_url': video.thumbnail_url or video.video_url,
                    'prompt': video.prompt,
                    'created_at': video.created_at,
                    'is_favorite': video.is_favorite,
                    'view_count': video.view_count,
                    'download_count': video.download_count,
                    'model_used': video.model_used,
                    'parameters': video.parameters,
                    # Video-specific fields
                    'video_type': video.video_type,
                    'duration': video.duration,
                    'ratio': video.ratio,
                    'video_id': video.video_id,
                    'user_notes': video.user_notes,
                    'tags': video.tags,
                })

        # TODO: Add audio when AudioHistory model is created
        # if media_type in ['all', 'audio']:
        #     audio_queryset = AudioHistory.objects.filter(user=user)
        #     ...

        # Sort all items
        reverse = sort_by.startswith('-')
        sort_field = sort_by.lstrip('-')

        all_items.sort(
            key=lambda x: x.get(sort_field, ''),
            reverse=reverse
        )

        # Get total count before pagination
        total_count = len(all_items)

        # Apply pagination
        paginated_items = all_items[offset:offset + limit]

        # Convert datetime objects to ISO format strings
        for item in paginated_items:
            if isinstance(item['created_at'], datetime):
                item['created_at'] = item['created_at'].isoformat()

        # Build pagination URLs
        base_url = request.build_absolute_uri(request.path)
        next_url = None
        previous_url = None

        if offset + limit < total_count:
            next_offset = offset + limit
            next_url = f"{base_url}?type={media_type}&limit={limit}&offset={next_offset}"
            if is_favorite:
                next_url += f"&favorite={is_favorite}"
            if search_term:
                next_url += f"&search={search_term}"

        if offset > 0:
            previous_offset = max(0, offset - limit)
            previous_url = f"{base_url}?type={media_type}&limit={limit}&offset={previous_offset}"
            if is_favorite:
                previous_url += f"&favorite={is_favorite}"
            if search_term:
                previous_url += f"&search={search_term}"

        return Response({
            'count': total_count,
            'next': next_url,
            'previous': previous_url,
            'results': paginated_items
        })

    except Exception as e:
        logger.error(f"❌ Unified gallery error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_featured_examples(request):
    """
    Get curated featured examples for the Examples Gallery
    Session 56: Phase A Task 2
    Returns diverse, high-quality images showcasing platform capabilities
    """
    try:
        from content.models import ImageHistory
        from django.db.models import Q

        # Get diverse examples - ONLY generated images (Session 56: Bug fix)
        # Edited images (upscale, remove bg, etc.) have operation names as prompts,
        # not useful for "Try This Prompt" feature
        examples = []

        # Strategy: Get up to 12 recent generated images with variety
        # Prioritize diverse models and styles to showcase platform capabilities
        examples = ImageHistory.objects.filter(
            user=request.user,
            image_type='generated'  # ONLY show generated images!
        ).order_by('-created_at')[:12]

        # Format response
        formatted_examples = []
        for img in examples:
            formatted_examples.append({
                'id': str(img.id),
                'url': img.file_path if img.file_path.startswith('http') else f'/media/{img.file_path}',
                'prompt': img.prompt or f'{img.image_type.replace("_", " ").title()}',
                'image_type': img.image_type,
                'model_used': img.model_used or 'sdxl',
                'style': img.style or '',
                'created_at': img.created_at.isoformat()
            })

        logger.info(f"✨ Returning {len(formatted_examples)} featured examples")
        return Response({
            'examples': formatted_examples,
            'count': len(formatted_examples)
        })

    except Exception as e:
        logger.error(f"❌ Error loading featured examples: {str(e)}")
        return Response({
            'error': str(e),
            'examples': []
        }, status=500)


# ========================================
# INTELLIGENT PROMPT IMPROVEMENT (Session 56: Phase B.1)
# ========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def improve_workflow_prompt(request):
    """
    Improve user's workflow prompt using AI intelligence
    Session 56: Phase B.1 - Intelligent Workflow Prompting

    Takes a user's simple prompt and workflow type, returns an optimized
    prompt that will generate better results for that specific workflow.

    Example:
        Input: "Light Work Handyman services" (Logo Creator)
        Output: "Professional logo for 'Light Work' handyman services..."
    """
    try:
        user_prompt = request.data.get('prompt', '').strip()
        workflow_type = request.data.get('workflow_type', '').lower()

        # Normalize workflow type: convert hyphens to underscores
        workflow_type = workflow_type.replace('-', '_')

        if not user_prompt:
            return Response({
                'error': 'Prompt is required'
            }, status=400)

        if not workflow_type:
            return Response({
                'error': 'Workflow type is required'
            }, status=400)

        # Workflow-specific system prompts
        # Session 61: Enhanced with examples, negative prompts, and success patterns
        WORKFLOW_CONTEXTS = {
            'logo_creator': {
                'context': 'logo design for businesses and brands',
                'instructions': """You are an AI prompt enhancement assistant. The user has already built a complete logo prompt with their chosen style (Character Mascot, Vector, Illustrative, etc.).

Your task: ENHANCE the existing prompt by adding specific visual details that will improve the result. DO NOT rewrite or change the style.

CRITICAL RULES:
✅ KEEP the existing style (Character Mascot, Vector, Minimalist, etc.) - NEVER change it
✅ KEEP the brand name, colors, and core concept
✅ ADD helpful visual details (specific features, expressions, poses, details)
✅ ADD quality markers (4K, professional, cinematic lighting)
✅ Be like Claude helping the user - suggest improvements, don't rewrite

❌ NEVER change "Character Mascot" to "minimalist vector"
❌ NEVER change "DreamWorks animation" to "flat design"
❌ NEVER override the user's style choice
❌ NEVER add assumptions (like "sports betting" if not mentioned)

EXAMPLES OF ENHANCEMENT (Not Rewriting):

Example 1:
User's prompt: "Donkey Betz, gray-blue/orange/white colors, character mascot, DreamWorks style"
❌ BAD (Rewriting): "Minimalist vector logo, flat design, avoid cartoonish"
✅ GOOD (Enhancing): "Donkey Betz character mascot with VERY LONG PROMINENT BLACK-TIPPED EARS (key donkey feature), gray-blue colored body with white muzzle, wearing orange accent (vest or gear), confident smart expression, stocky muscular build (not sleek like horse), DreamWorks animation quality, expressive detailed face with personality, cinematic lighting, 4K resolution, professional character design"

Example 2:
User's prompt: "Light Work handyman, navy blue and yellow, wrench and lightbulb, vector style"
❌ BAD (Rewriting): "Character mascot, cartoon style"
✅ GOOD (Enhancing): "Light Work handyman logo in clean vector style, light bulb with wrench incorporated, navy blue and bright yellow colors, simple geometric shapes, sharp clean lines, professional icon design, centered composition, white background, scalable vector art, modern minimalist aesthetic"

Example 3:
User's prompt: "Coffee shop logo, warm browns, illustrative style, hand-drawn feel"
❌ BAD (Rewriting): "Flat minimalist vector"
✅ GOOD (Enhancing): "Coffee shop logo in hand-drawn illustrative style, warm brown tones with cream accents, artistic linework showing coffee cup with steam wisps, cozy approachable feel, sketch-like quality with personality, detailed but not cluttered, professional illustration quality, unique character"

YOUR ROLE:
Think of yourself as Claude did in the conversation - the user said "donkey logo" and Claude said "Great! To make it clearly a DONKEY not a horse, emphasize: VERY LONG EARS with black tips, stocky build, gray-blue coloring, white muzzle."

That's enhancement. That's helpful. That's what you should do.

CRITICAL PROMPT STRUCTURE:
Your enhanced prompt MUST follow this exact order (AI commits to subject in first 10 words!):

1. **SUBJECT FIRST** - What creature/character (T-Rex, donkey, person, etc.)
2. **POSE/ACTION** - What they're doing (standing, dancing, running, etc.)
3. **CLOTHING/ACCESSORIES** - What they're wearing (emphasize heavily!)
4. **STYLE** - Art style (DreamWorks, vector, minimalist, etc.)
5. **COLORS** - Color scheme
6. **DETAILS** - Background, lighting, mood

Example with clothing:
User: "T-Rex wearing disco ball necklace and bell-bottom pants"
❌ WRONG ORDER: "WEARING sparkly disco ball necklace, DRESSED IN bell-bottom pants... T-Rex dinosaur character..."
✅ CORRECT ORDER: "T-Rex dinosaur character standing upright in disco pose, WEARING sparkly disco ball necklace around neck, DRESSED IN purple bell-bottom pants with wide flared legs, platform shoes on feet, DreamWorks animation style..."

WHY: If you say "WEARING disco necklace" first, AI generates a human wearing jewelry. If you say "T-Rex dinosaur" first, AI generates a T-Rex, then adds the jewelry to the T-Rex!

CLOTHING EMPHASIS (after subject is established):
- Use emphatic language: "WEARING [item]", "DRESSED IN [item]", "clearly visible [item]"
- Repeat key items: "disco ball necklace... necklace shining... reflective necklace"
- Describe vividly: colors, materials, fit, details
- AI models ignore clothing unless heavily emphasized!

IMPORTANT: Keep your enhanced prompt under 1200 characters total (Stability AI hard limit is 2000, but shorter is better for accuracy). Be specific but VERY concise - prioritize the most important visual details.

Format your response as a single enhanced prompt. Keep the user's style sacred, just add helpful details."""
            },
            'portrait_enhancer': {
                'context': 'professional portrait photography',
                'instructions': """You are a professional portrait photographer. The user wants to create a high-quality portrait.

Your task: Transform their input into a detailed portrait prompt that will generate professional, polished results.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "headshot"
✅ Good: "professional corporate headshot, business attire, studio lighting with soft key light and rim light, neutral gray background, shallow depth of field, confident friendly expression, sharp focus on eyes, 85mm lens perspective, high resolution"

❌ Bad: "portrait of a woman"
✅ Good: "elegant portrait of a professional woman in her 30s, natural confident expression, soft studio lighting with subtle fill, blurred bokeh background, sharp focus, professional quality, warm color tones, business casual attire"

❌ Bad: "CEO photo"
✅ Good: "executive portrait of confident CEO, tailored suit, modern office environment blurred in background, dramatic side lighting, sharp focus, professional quality, sophisticated composition, approachable expression"

NEGATIVE PROMPTS (avoid these):
- Distorted anatomy, extra limbs, deformed features
- Harsh direct flash, unnatural lighting
- Cluttered busy backgrounds
- Low resolution, blurry, grainy
- Awkward poses, forced expressions
- Oversaturated colors, heavy filters

STABILITY AI SUCCESS PATTERNS:
- Specify lighting: "studio lighting", "soft natural light", "golden hour", "dramatic side lighting"
- Mention depth of field: "shallow depth of field", "bokeh background", "blurred background"
- Include camera details: "85mm lens", "portrait lens", "professional camera"
- Quality markers: "high resolution", "sharp focus", "professional quality", "4K"
- Composition: "centered composition", "rule of thirds", "headshot framing"
- Expression: "confident", "friendly", "professional", "natural smile"

Consider:
- Subject description (person, profession, mood)
- Lighting (studio, natural, dramatic, soft)
- Background (neutral, blurred, contextual)
- Camera settings implied (shallow depth of field, sharp focus)
- Professional quality indicators (high resolution, well-lit, polished)
- Pose and expression appropriate for the context

Format your response as a single, clear prompt suitable for AI image generation."""
            },
            'social_media_pack': {
                'context': 'social media content creation',
                'instructions': """You are a social media content strategist. The user wants to create engaging social media visuals.

Your task: Transform their input into a prompt that will generate eye-catching, platform-appropriate content.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "food photo"
✅ Good: "vibrant overhead food photography of colorful smoothie bowl topped with fresh berries and granola, natural daylight, Instagram aesthetic, bright colors, sharp focus, clean white background, appetizing composition"

❌ Bad: "fitness post"
✅ Good: "motivational fitness scene, athletic person mid-workout, dynamic action shot, energetic composition, vibrant colors with teal and orange tones, inspirational mood, Instagram square format, professional quality"

❌ Bad: "product announcement"
✅ Good: "sleek product showcase on gradient background, centered composition, modern minimalist aesthetic, vibrant brand colors, dramatic lighting, social media ready format, eye-catching visual hierarchy"

NEGATIVE PROMPTS (avoid these):
- Cluttered composition, too many elements
- Dull muted colors, low contrast
- Poor lighting, dark shadows
- Blurry unfocused subjects
- Generic stock photo look
- Text-heavy designs (AI can't render text well)

STABILITY AI SUCCESS PATTERNS:
- Specify platform aesthetic: "Instagram aesthetic", "Pinterest-style", "Facebook-friendly"
- Use vibrant colors: "vibrant colors", "bold contrast", "eye-catching palette"
- Mention composition: "centered", "rule of thirds", "overhead shot", "flat lay"
- Include lighting: "natural daylight", "bright lighting", "soft shadows"
- Format hints: "square format", "vertical format", "social media ready"
- Mood descriptors: "energetic", "inspiring", "professional", "fun", "elegant"

Consider:
- Platform expectations (Instagram, Facebook, Twitter aesthetics)
- Visual hierarchy and composition
- Color vibrancy and contrast
- Subject clarity and appeal
- Trending visual styles
- Brand consistency if applicable

Format your response as a single, clear prompt suitable for AI image generation."""
            },
            'product_mockup': {
                'context': 'product photography and presentation',
                'instructions': """You are a product photographer. The user wants to showcase a product professionally.

Your task: Transform their input into a prompt that will generate professional product mockups.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "coffee mug"
✅ Good: "elegant ceramic coffee mug on white marble surface, soft natural lighting from left, minimalist composition, shallow depth of field, product photography, clean white background, professional e-commerce quality"

❌ Bad: "phone case"
✅ Good: "sleek phone case held in hand, modern lifestyle shot, blurred urban background, natural lighting, focus on product texture and design, professional product photography, premium quality"

❌ Bad: "watch photo"
✅ Good: "luxury wristwatch on dark wooden surface, dramatic side lighting creating subtle shadows, macro detail shot showing craftsmanship, black background, professional jewelry photography, high-end catalog quality"

NEGATIVE PROMPTS (avoid these):
- Cluttered backgrounds, distracting elements
- Harsh shadows, uneven lighting
- Unclear product features
- Low resolution, poor focus
- Awkward angles, unflattering views
- Busy patterns competing with product

STABILITY AI SUCCESS PATTERNS:
- Specify surface: "white marble", "wooden table", "clean background", "floating on gradient"
- Lighting direction: "soft natural light from left", "studio lighting", "dramatic side lighting"
- Context options: "hand holding", "on surface", "lifestyle shot", "hero shot"
- Background: "white background", "blurred background", "minimal background"
- Quality markers: "product photography", "e-commerce quality", "professional", "high resolution"
- Composition: "centered", "rule of thirds", "macro detail", "overhead view"

Consider:
- Product type and key features to highlight
- Composition and angle (hero shot, lifestyle, detail)
- Background (clean, contextual, lifestyle)
- Lighting (studio, natural, dramatic)
- Context (hand holding, on surface, in use)
- Professional e-commerce quality

Format your response as a single, clear prompt suitable for AI image generation."""
            },
            'creative_upscale': {
                'context': 'image enhancement and upscaling',
                'instructions': """You are an image enhancement specialist. The user wants to guide how their image should be enhanced.

Your task: Transform their input into clear enhancement directions.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "make it better"
✅ Good: "enhance fine details and textures, improve sharpness and clarity, boost color vibrancy while maintaining natural tones, increase resolution to 4K, preserve original composition and style"

❌ Bad: "fix this image"
✅ Good: "enhance facial details and skin texture, improve lighting and shadow definition, sharpen focus on subject while maintaining soft background blur, upscale to high resolution, professional portrait quality"

❌ Bad: "upscale"
✅ Good: "creative upscaling with enhanced artistic details, add fine textures and intricate patterns, improve color depth and contrast, maintain original artistic style while adding painterly refinement, 4K resolution"

NEGATIVE PROMPTS (avoid these):
- Change original style completely
- Add new elements or objects
- Alter composition significantly
- Over-saturate or distort colors
- Remove important details
- Change subject or mood

STABILITY AI SUCCESS PATTERNS:
- Specify preservation: "maintain original composition", "preserve artistic style", "keep color palette"
- Enhancement targets: "enhance fine details", "improve sharpness", "boost clarity"
- Quality goals: "4K resolution", "high resolution", "professional quality"
- Texture emphasis: "add fine textures", "enhance surface details", "intricate patterns"
- Color work: "improve color depth", "enhance vibrancy", "natural color balance"
- Style continuity: "painterly refinement", "artistic enhancement", "stylistic consistency"

Consider:
- What details should be emphasized
- What artistic style to enhance toward
- What quality improvements to prioritize (sharpness, color, detail)
- What mood or atmosphere to maintain/enhance
- Technical quality targets (resolution, clarity, color accuracy)

Format your response as a single, clear prompt suitable for AI image enhancement."""
            },
            'style_explorer': {
                'context': 'artistic style exploration and variation',
                'instructions': """You are an art director exploring creative possibilities. The user wants to see their concept in multiple styles.

Your task: Transform their input into a rich, detailed prompt that will generate interesting variations.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "sunset"
✅ Good: "dramatic sunset over mountain landscape, vibrant orange and purple sky with layered clouds, detailed mountain silhouettes in foreground, golden light rays breaking through clouds, epic composition, high detail, cinematic quality"

❌ Bad: "forest scene"
✅ Good: "enchanted forest with tall ancient trees, dappled sunlight filtering through canopy, moss-covered ground with small wildflowers, mystical atmosphere with soft fog, rich green tones, fantasy illustration style, detailed foliage"

❌ Bad: "city view"
✅ Good: "modern city skyline at dusk, illuminated skyscrapers reflecting in water, dynamic composition with leading lines, rich blue hour lighting with warm building lights, urban architecture, professional photography quality, detailed cityscape"

NEGATIVE PROMPTS (avoid these):
- Vague subjects, unclear focus
- Minimal details, generic descriptions
- Flat composition, no depth
- Boring lighting, plain presentation
- Lack of specific visual elements
- No style direction or mood

STABILITY AI SUCCESS PATTERNS:
- Rich details: "detailed foliage", "intricate patterns", "fine textures", "layered elements"
- Lighting descriptions: "dramatic lighting", "golden hour", "dappled sunlight", "atmospheric lighting"
- Composition terms: "epic composition", "dynamic perspective", "leading lines", "rule of thirds"
- Quality markers: "high detail", "professional quality", "cinematic", "photorealistic"
- Mood and atmosphere: "mystical atmosphere", "energetic mood", "serene feeling", "dramatic tone"
- Style hints: "illustration style", "photography quality", "painterly", "artistic rendering"

Consider:
- Core concept/subject clarity
- Visual elements that work across styles
- Compositional strength
- Color palette flexibility
- Detail level that shows style differences
- Artistic merit and visual interest

Format your response as a single, clear prompt suitable for AI image generation."""
            },
            'video_generation': {
                'context': 'video animation and motion',
                'instructions': """You are a video director and cinematographer. The user wants to create engaging animated video content.

Your task: Transform their input into a detailed video prompt that will generate dynamic, cinematic motion.

🚨 CRITICAL: IMAGE-TO-VIDEO vs TEXT-TO-VIDEO DISTINCTION! 🚨

**IMAGE-TO-VIDEO PROMPTS (User uploading an existing image):**
- Focus ONLY on MOVEMENT and CAMERA WORK
- DO NOT re-describe the character, colors, clothing, or appearance
- The uploaded image ALREADY shows what the subject looks like!
- Example: "Dancing with arms waving side to side, hips swaying, spinning 360 degrees"
- NOT: "Purple T-Rex with disco outfit dancing..." (This creates a DIFFERENT character!)

**TEXT-TO-VIDEO PROMPTS (Generating video from scratch):**
- Describe BOTH character appearance AND movement
- Include subject description, colors, setting, AND actions
- Example: "Purple T-Rex in disco outfit, dancing with arms waving..."

**HOW TO DETECT:**
If user prompt mentions specific visual details (colors, clothing, character traits), they're likely doing TEXT-TO-VIDEO.
If user prompt focuses only on actions/movements, they're likely doing IMAGE-TO-VIDEO.
WHEN IN DOUBT: Focus on movement only - it works for both!

SESSION 64 KEY LEARNING: Specific body part movements + sequences work MUCH better than generic descriptions!

EXAMPLES OF GOOD VS BAD VIDEO PROMPTS:

❌ Bad (generic): "T-Rex dancing"
Result: Just swaying at knees, minimal movement

✅ Good (specific): "T-Rex disco dancing with exaggerated movements: arms waving side to side, hips swaying dramatically, head bobbing rhythmically, spinning 360 degrees, attempting dance splits with legs spreading wide, platform shoes tapping floor in rhythm"
Result: Dynamic animation with multiple distinct movements!

❌ Bad: "eagle flying"
✅ Good: "majestic eagle soaring through clouds, wings spreading wide then folding in powerful downstrokes, body banking left then right through air currents, head turning to scan below, talons extending forward, diving through layers of cumulus clouds with increasing speed"

❌ Bad: "person walking"
✅ Good: "confident person walking forward with purposeful stride, arms swinging naturally in rhythm, shoulders squared, head held high with slight nod, coat billowing behind in breeze, footsteps creating small dust clouds, approaching camera with determined expression"

CRITICAL VIDEO PROMPT RULES:

1. **SPECIFY BODY PARTS + DIRECTIONS**
   - "arms pointing up and down" not just "moving arms"
   - "head turning left to right" not just "head movement"
   - "legs kicking forward and back" not just "leg motion"

2. **SEQUENCE THE MOVEMENTS**
   - "First: arms wave overhead, Then: spin 360 degrees, Finally: strike a pose"
   - Describe the flow of action from start to finish
   - Multiple distinct moves create better results than one vague action

3. **EMPHASIZE DRAMATIC ACTIONS**
   - "spinning in the air", "jumping high", "sliding across floor"
   - Big, exaggerated movements work better than subtle ones
   - Use emphatic language: "dramatically", "powerfully", "energetically"

4. **DESCRIBE CAMERA MOVEMENT**
   - "camera slowly zooms in on subject"
   - "camera circles around character"
   - "camera pans left to right following action"
   - "dynamic camera angle shifting from low to high"

5. **ADD ENVIRONMENT INTERACTIONS**
   - "splashing through water puddles"
   - "leaves swirling around feet"
   - "casting shadows that dance on walls"
   - "reflections in mirrors/water"

NEGATIVE PROMPTS (avoid these):
- Generic descriptions: "moving around", "doing something", "being active"
- Single vague action: "dancing", "fighting", "flying" (add specifics!)
- Static poses with no movement sequence
- Missing camera direction or angle description
- No environmental or atmospheric details

RUNWAY ML SUCCESS PATTERNS:
- Specific body part actions: "arms extending", "legs bending", "head tilting"
- Directional movement: "upward", "left to right", "spinning clockwise", "forward motion"
- Sequential actions: "first... then... followed by... finally..."
- Camera work: "zoom", "pan", "tracking shot", "dolly in"
- Lighting changes: "spotlight follows", "shadows lengthening", "glow intensifying"
- Physics and weight: "bouncing energetically", "graceful floating", "powerful stomping"
- Expressions: "smiling broadly", "concentrating intensely", "surprised reaction"

VIDEO-SPECIFIC TECHNICAL NOTES:
- Keep total prompt under 500 characters for best results
- Front-load the most important movement in first sentence
- Use active verbs: "jumping", "spinning", "reaching", "diving"
- Describe the arc of motion: "from standing to jumping to landing"

Consider:
- What specific movements will create engaging motion
- Which body parts should move and in what direction
- What sequence of actions tells the story
- How the camera should capture the action
- What environmental elements add to the scene
- What atmosphere or mood enhances the motion

Format your response as a single, cinematic prompt suitable for AI video generation."""
            }
        }

        # Get workflow context
        workflow_context = WORKFLOW_CONTEXTS.get(workflow_type)
        if not workflow_context:
            return Response({
                'error': f'Unknown workflow type: {workflow_type}'
            }, status=400)

        # Call OpenAI GPT-5 for prompt improvement (Session 56: Phase B.1, Session 57: Fixed to use Responses API)
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        logger.info(f"✨ Improving prompt for {workflow_type}: '{user_prompt[:50]}...'")

        # Use the new Responses API with GPT-5 (not Chat Completions API)
        # Session 64: Changed from "transform" to "enhance" - GPT-5 should add details, not rewrite
        response = client.responses.create(
            model="gpt-5",
            instructions=workflow_context['instructions'],
            input=f"User's complete prompt (already includes their chosen style): {user_prompt}\n\nPlease ENHANCE this prompt by adding specific helpful visual details. Keep the style and core concept exactly as-is, just make it better with specific details."
        )

        logger.info(f"🔍 OpenAI Response: {response}")
        logger.info(f"🔍 Output text length: {len(response.output_text) if hasattr(response, 'output_text') else 'NO OUTPUT_TEXT'}")

        improved_prompt = response.output_text if hasattr(response, 'output_text') else None
        if not improved_prompt:
            logger.error(f"❌ OpenAI returned empty content! Full response: {response}")
            improved_prompt = f"ERROR: OpenAI returned no content. Using original prompt: {user_prompt}"

        improved_prompt = improved_prompt.strip()
        logger.info(f"✅ Improved prompt generated ({len(improved_prompt)} chars): {improved_prompt[:100]}...")

        return Response({
            'original_prompt': user_prompt,
            'improved_prompt': improved_prompt,
            'workflow_type': workflow_type,
            'explanation': f'Optimized for {workflow_context["context"]}'
        })

    except Exception as e:
        logger.error(f"❌ Error improving prompt: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# ========================================
# WORKFLOW HISTORY & FAVORITES (Session 57: Phase B.2)
# ========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_workflow_history(request):
    """
    List user's workflow execution history
    Session 57: Phase B.2 - Workflow History & Favorites

    Query parameters:
    - limit: Number of results (default: 10)
    - offset: Pagination offset (default: 0)
    - workflow_type: Filter by workflow type (optional)
    - status: Filter by status (optional)
    - favorites_only: Show only favorites (optional, default: false)
    """
    try:
        from content.models import WorkflowHistory

        user = request.user
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        workflow_type = request.GET.get('workflow_type', '').strip()
        status = request.GET.get('status', '').strip()
        favorites_only = request.GET.get('favorites_only', 'false').lower() == 'true'

        # Build query
        queryset = WorkflowHistory.objects.filter(user=user)

        if workflow_type:
            queryset = queryset.filter(workflow_type=workflow_type)

        if status:
            queryset = queryset.filter(status=status)

        if favorites_only:
            queryset = queryset.filter(is_favorite=True)

        # Get total count
        total_count = queryset.count()

        # Paginate
        workflows = queryset[offset:offset+limit]

        # Serialize
        results = []
        for workflow in workflows:
            results.append({
                'id': workflow.id,
                'workflow_type': workflow.workflow_type,
                'workflow_name': workflow.workflow_name,
                'prompt': workflow.prompt,
                'improved_prompt': workflow.improved_prompt,
                'status': workflow.status,
                'execution_time': workflow.execution_time,
                'result_count': workflow.result_count,
                'result_images': workflow.result_images,
                'is_favorite': workflow.is_favorite,
                'rerun_count': workflow.rerun_count,
                'created_at': workflow.created_at.isoformat(),
                'config': workflow.config,
            })

        return Response({
            'workflows': results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
        })

    except Exception as e:
        logger.error(f"❌ Error listing workflow history: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workflow_history(request, workflow_id):
    """
    Get specific workflow execution details
    Session 57: Phase B.2 - Workflow History & Favorites
    """
    try:
        from content.models import WorkflowHistory

        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        return Response({
            'id': workflow.id,
            'workflow_type': workflow.workflow_type,
            'workflow_name': workflow.workflow_name,
            'prompt': workflow.prompt,
            'improved_prompt': workflow.improved_prompt,
            'config': workflow.config,
            'input_image_id': workflow.input_image_id,
            'execution_time': workflow.execution_time,
            'status': workflow.status,
            'error_message': workflow.error_message,
            'result_images': workflow.result_images,
            'result_count': workflow.result_count,
            'is_favorite': workflow.is_favorite,
            'rerun_count': workflow.rerun_count,
            'user_notes': workflow.user_notes,
            'tags': workflow.tags,
            'created_at': workflow.created_at.isoformat(),
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error getting workflow: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_workflow_favorite(request, workflow_id):
    """
    Toggle workflow favorite status
    Session 57: Phase B.2 - Workflow History & Favorites
    """
    try:
        from content.models import WorkflowHistory

        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        # Toggle favorite
        workflow.is_favorite = not workflow.is_favorite
        workflow.save(update_fields=['is_favorite'])

        return Response({
            'success': True,
            'is_favorite': workflow.is_favorite,
            'workflow_id': workflow.id
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error toggling favorite: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_workflow_favorite(request):
    """
    Save workflow as a named favorite
    Session 57: Phase B.2 - Workflow History & Favorites

    Expected JSON:
    {
        "workflow_id": 123,
        "name": "My Logo Style",
        "description": "Custom description (optional)",
        "category": "Logos (optional)"
    }
    """
    try:
        from content.models import WorkflowHistory, WorkflowFavorite

        workflow_id = request.data.get('workflow_id')
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        category = request.data.get('category', '').strip()

        if not workflow_id or not name:
            return Response({
                'error': 'workflow_id and name are required'
            }, status=400)

        # Get workflow
        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        # Create or update favorite
        favorite, created = WorkflowFavorite.objects.get_or_create(
            user=request.user,
            workflow_history=workflow,
            defaults={
                'name': name,
                'description': description,
                'category': category,
            }
        )

        if not created:
            # Update existing
            favorite.name = name
            favorite.description = description
            favorite.category = category
            favorite.save()

        # Mark workflow as favorite
        if not workflow.is_favorite:
            workflow.is_favorite = True
            workflow.save(update_fields=['is_favorite'])

        return Response({
            'success': True,
            'favorite_id': favorite.id,
            'created': created
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error saving favorite: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_workflow_favorites(request):
    """
    List user's favorite workflows
    Session 57: Phase B.2 - Workflow History & Favorites
    """
    try:
        from content.models import WorkflowFavorite

        favorites = WorkflowFavorite.objects.filter(
            user=request.user
        ).select_related('workflow_history')

        results = []
        for favorite in favorites:
            workflow = favorite.workflow_history
            results.append({
                'favorite_id': favorite.id,
                'name': favorite.name,
                'description': favorite.description,
                'category': favorite.category,
                'use_count': favorite.use_count,
                'last_used_at': favorite.last_used_at.isoformat() if favorite.last_used_at else None,
                'created_at': favorite.created_at.isoformat(),
                'workflow': {
                    'id': workflow.id,
                    'workflow_type': workflow.workflow_type,
                    'workflow_name': workflow.workflow_name,
                    'prompt': workflow.prompt,
                    'improved_prompt': workflow.improved_prompt,
                    'config': workflow.config,
                    'result_images': workflow.result_images,
                    'execution_time': workflow.execution_time,
                }
            })

        return Response({
            'favorites': results,
            'total_count': len(results)
        })

    except Exception as e:
        logger.error(f"❌ Error listing favorites: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_workflow_favorite(request, favorite_id):
    """
    Delete a workflow favorite
    Session 57: Phase B.2 - Workflow History & Favorites
    """
    try:
        from content.models import WorkflowFavorite

        favorite = WorkflowFavorite.objects.get(
            id=favorite_id,
            user=request.user
        )

        workflow_id = favorite.workflow_history.id
        favorite.delete()

        # Check if workflow has any other favorites
        from content.models import WorkflowHistory
        workflow = WorkflowHistory.objects.get(id=workflow_id)
        has_other_favorites = WorkflowFavorite.objects.filter(
            workflow_history=workflow
        ).exists()

        # Unmark workflow as favorite if no other favorites exist
        if not has_other_favorites and workflow.is_favorite:
            workflow.is_favorite = False
            workflow.save(update_fields=['is_favorite'])

        return Response({
            'success': True,
            'favorite_id': favorite_id
        })

    except WorkflowFavorite.DoesNotExist:
        return Response({
            'error': 'Favorite not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error deleting favorite: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rerun_workflow(request, workflow_id):
    """
    Re-run a previous workflow with same configuration
    Session 57: Phase B.2 - Workflow History & Favorites

    Optional JSON body:
    {
        "use_favorite_id": 123  // If re-running from favorite
    }
    """
    try:
        from content.models import WorkflowHistory, WorkflowFavorite

        # Get original workflow
        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        # Increment rerun count
        workflow.increment_rerun_count()

        # If re-running from favorite, increment favorite use count
        favorite_id = request.data.get('use_favorite_id')
        if favorite_id:
            try:
                favorite = WorkflowFavorite.objects.get(
                    id=favorite_id,
                    user=request.user
                )
                favorite.increment_use_count()
            except WorkflowFavorite.DoesNotExist:
                pass  # Non-critical error

        # Return workflow configuration for frontend to re-execute
        return Response({
            'success': True,
            'workflow_type': workflow.workflow_type,
            'workflow_name': workflow.workflow_name,
            'prompt': workflow.improved_prompt or workflow.prompt,
            'config': workflow.config,
            'input_image_id': workflow.input_image_id,
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error rerunning workflow: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# ========================================
# USER PREFERENCE LEARNING (Session 59: Phase B.4)
# ========================================

def get_user_preferences(user):
    """
    Analyze user's workflow history to identify patterns and preferences
    Session 59: Phase B.4 - Memory System Integration

    Returns a dictionary with:
    - favorite_workflow: Most frequently used workflow type
    - favorite_styles: List of most commonly used styles
    - successful_prompts: Prompts from favorited workflows
    - total_workflows: Total number of workflows executed
    - workflow_patterns: Common workflow sequences
    - recent_activity: Last 5 workflows for context
    """
    from content.models import WorkflowHistory, WorkflowFavorite
    from collections import Counter

    # Get all workflow history for this user
    history = WorkflowHistory.objects.filter(
        user=user,
        status='completed'  # Only count successful executions
    ).order_by('-created_at')

    total_count = history.count()

    if total_count == 0:
        return {
            'has_history': False,
            'total_workflows': 0,
            'message': 'No workflow history yet - start creating to build your preferences!'
        }

    # Analyze workflow type preferences
    workflow_counts = Counter(h.workflow_type for h in history)
    favorite_workflow = workflow_counts.most_common(1)[0] if workflow_counts else None

    # Analyze style preferences from config JSON
    style_usage = Counter()
    model_usage = Counter()

    for h in history:
        if h.config:
            # Check for style in first step (usually generate)
            steps = h.config.get('steps', [])
            if steps and len(steps) > 0:
                first_step = steps[0]
                if isinstance(first_step, dict):
                    step_config = first_step.get('config', {})
                    if 'style' in step_config:
                        style_usage[step_config['style']] += 1
                    if 'model' in step_config:
                        model_usage[step_config['model']] += 1

    favorite_styles = [style for style, count in style_usage.most_common(3)]
    favorite_models = [model for model, count in model_usage.most_common(2)]

    # Find successful patterns (favorited workflows)
    favorites = WorkflowFavorite.objects.filter(user=user).select_related('workflow_history')
    successful_prompts = []

    for fav in favorites[:5]:  # Top 5 favorites
        wf = fav.workflow_history
        if wf.improved_prompt:
            successful_prompts.append({
                'workflow_type': wf.workflow_type,
                'prompt': wf.improved_prompt,
                'use_count': fav.use_count
            })
        elif wf.prompt:
            successful_prompts.append({
                'workflow_type': wf.workflow_type,
                'prompt': wf.prompt,
                'use_count': fav.use_count
            })

    # Analyze workflow sequences (what user does after what)
    recent_workflows = list(history[:20])  # Last 20 for pattern detection
    sequences = []

    for i in range(len(recent_workflows) - 1):
        sequences.append({
            'from': recent_workflows[i].workflow_type,
            'to': recent_workflows[i+1].workflow_type
        })

    sequence_counts = Counter(f"{seq['from']}->{seq['to']}" for seq in sequences)
    common_patterns = [pattern for pattern, count in sequence_counts.most_common(3) if count >= 2]

    # Recent activity for context
    recent_activity = [{
        'workflow_type': h.workflow_type,
        'workflow_name': h.workflow_name,
        'created_at': h.created_at.isoformat(),
        'execution_time': h.execution_time,
        'result_count': h.result_count
    } for h in recent_workflows[:5]]

    return {
        'has_history': True,
        'total_workflows': total_count,
        'favorite_workflow': {
            'type': favorite_workflow[0],
            'count': favorite_workflow[1],
            'percentage': round((favorite_workflow[1] / total_count) * 100, 1)
        } if favorite_workflow else None,
        'favorite_styles': favorite_styles,
        'favorite_models': favorite_models,
        'successful_prompts': successful_prompts,
        'common_patterns': common_patterns,
        'recent_activity': recent_activity,
        'favorites_count': favorites.count()
    }


# ========================================
# AI ASSISTANT CHAT (Session 58: Phase B.3)
# ========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_preferences_api(request):
    """
    Get user preferences and patterns from workflow history
    Session 59: Phase B.4 - Memory System Integration

    Returns user's favorite workflows, styles, patterns, and recent activity
    for smart defaults and personalized recommendations.

    Example response:
    {
        "has_history": true,
        "favorite_workflow": {"type": "logo_creator", "count": 15, "percentage": 45.5},
        "favorite_styles": ["vector", "minimalist", "photographic"],
        "successful_prompts": [...],
        "common_patterns": ["logo_creator->creative_upscale"]
    }
    """
    try:
        preferences = get_user_preferences(request.user)
        return Response(preferences)
    except Exception as e:
        logger.error(f"❌ Error fetching user preferences: {str(e)}")
        return Response({
            'has_history': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assistant_chat(request):
    """
    AI Assistant chat endpoint using GPT-5
    Session 58: Phase B.3 - Personal Assistant Integration
    Session 59: Phase B.4 - Enhanced with user preference learning

    Handles general conversational queries from the AI Assistant.
    Fast, intelligent responses for questions about the platform,
    creative advice, and general help.

    Now includes personalized context based on user's workflow history!

    Example:
        Input: "What's the best way to create professional images?"
        Output: Helpful advice from GPT-5 about image generation techniques
                (personalized based on user's favorite workflows and styles)
    """
    try:
        user_message = request.data.get('message', '').strip()
        conversation_history = request.data.get('history', [])  # Optional for context

        if not user_message:
            return Response({
                'error': 'Message is required'
            }, status=400)

        # Session 59: Phase B.4 - Get user preferences for personalized assistance
        user_prefs = get_user_preferences(request.user)

        # Session 62: Phase C.3.2 - Get user's projects for strategic planning
        from content.models import CreativeProject
        user_projects = CreativeProject.objects.filter(user=request.user).order_by('-created_at')[:5]

        # Build personalized system instructions based on user history
        ASSISTANT_INSTRUCTIONS = """You are a helpful AI assistant for the Donkey Betz AI Studio platform.

The platform provides:
- **Image Generation**: 4 models (Core, SDXL, SD3, Ultra) with 69 style presets
- **Image Editing**: Recolor, erase, inpaint, outpaint, remove background
- **Image Upscaling**: Fast 4x, Conservative 4K, Creative upscale
- **Video Generation**: Text-to-video and image-to-video (Runway ML)
- **Audio Generation**: Voice synthesis, sound effects, music
- **AI Workflows**: 6 professional templates (Logo Creator, Portrait Enhancer, Style Explorer, Social Media Pack, Product Mockup, Creative Upscale)
- **Projects & Campaigns**: Organize workflows into projects, use campaign templates (Brand Launch, Client Portfolio, Content Series, Marketing Materials, Product Launch)

Your role:
- Answer questions about platform features and capabilities
- Provide creative advice for image, video, and audio generation
- Explain how to use different tools and workflows
- Give tips for better prompts and results
- Provide STRATEGIC PLANNING advice for campaigns and projects
- Suggest workflow sequences for different creative goals
- Help users plan timelines and organize their creative work
- Be friendly, concise, and helpful

Keep responses under 200 words. Be conversational and practical."""

        # Session 59: Add personalized context based on user preferences
        if user_prefs.get('has_history'):
            personalization = "\n\n**USER PREFERENCES & HISTORY:**\n"

            # Favorite workflow
            if user_prefs.get('favorite_workflow'):
                fav = user_prefs['favorite_workflow']
                workflow_name = fav['type'].replace('_', ' ').title()
                personalization += f"- This user LOVES {workflow_name} ({fav['count']} times, {fav['percentage']}% of workflows)\n"

            # Favorite styles
            if user_prefs.get('favorite_styles'):
                styles_str = ", ".join(user_prefs['favorite_styles'])
                personalization += f"- Preferred styles: {styles_str}\n"

            # Favorite models
            if user_prefs.get('favorite_models'):
                models_str = ", ".join(user_prefs['favorite_models'])
                personalization += f"- Preferred models: {models_str}\n"

            # Total experience
            personalization += f"- Total workflows completed: {user_prefs['total_workflows']}\n"

            # Favorites
            if user_prefs.get('favorites_count', 0) > 0:
                personalization += f"- Has saved {user_prefs['favorites_count']} favorite workflows\n"

            # Common patterns
            if user_prefs.get('common_patterns'):
                patterns_str = ", ".join(user_prefs['common_patterns'][:2])
                personalization += f"- Common workflow patterns: {patterns_str}\n"

            # Recent activity
            if user_prefs.get('recent_activity'):
                recent = user_prefs['recent_activity'][0]
                workflow_name = recent['workflow_name']
                personalization += f"- Most recent: {workflow_name}\n"

            personalization += "\nUSE THIS CONTEXT to give personalized, relevant advice. Mention their preferences when helpful!"

            ASSISTANT_INSTRUCTIONS += personalization

        # Session 62: Phase C.3.2 - Add project context for strategic planning
        if user_projects.exists():
            project_context = "\n\n**ACTIVE PROJECTS:**\n"
            for project in user_projects:
                project_context += f"- {project.name} ({project.status}): {project.goal}\n"
                project_context += f"  Category: {project.category}, Workflows: {project.total_workflows}, Progress: {project.progress_percentage}%\n"
                if project.deadline:
                    project_context += f"  Deadline: {project.deadline.strftime('%Y-%m-%d')}\n"

            project_context += "\nProvide strategic advice based on their active projects. Suggest workflows, timelines, and organization strategies!"
            ASSISTANT_INSTRUCTIONS += project_context

        # Build input with conversation history if provided
        input_text = f"User question: {user_message}"

        if conversation_history and len(conversation_history) > 0:
            # Include last 3 messages for context
            recent_history = conversation_history[-3:]
            history_text = "\n".join([
                f"{'User' if msg.get('role') == 'user' else 'Assistant'}: {msg.get('content', '')}"
                for msg in recent_history
            ])
            input_text = f"Recent conversation:\n{history_text}\n\nCurrent question: {user_message}"

        # Call OpenAI GPT-5 using Responses API (same as workflow improvement)
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        logger.info(f"💬 Assistant chat request from {request.user.username}: '{user_message[:50]}...'")

        response = client.responses.create(
            model="gpt-5",
            instructions=ASSISTANT_INSTRUCTIONS,
            input=input_text
        )

        assistant_response = response.output_text if hasattr(response, 'output_text') else None

        if not assistant_response:
            logger.error(f"❌ GPT-5 returned empty response")
            assistant_response = "I apologize, but I encountered an issue generating a response. Please try rephrasing your question!"

        assistant_response = assistant_response.strip()
        logger.info(f"✅ Assistant response generated ({len(assistant_response)} chars)")

        return Response({
            'message': assistant_response,
            'model': 'gpt-5',
            'user_message': user_message
        })

    except Exception as e:
        logger.error(f"❌ Error in assistant chat: {str(e)}")
        return Response({
            'error': 'Sorry, I encountered an error. Please try again!',
            'details': str(e) if settings.DEBUG else None
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_workflow_execution(request):
    """
    Create workflow history record when workflow execution starts
    Session 57: Phase B.2 - Workflow History & Favorites

    Expected JSON:
    {
        "workflow_type": "logo_creator",
        "workflow_name": "Logo Creator",
        "prompt": "User's prompt",
        "improved_prompt": "AI-improved prompt (optional)",
        "config": {...},  // Workflow configuration
        "input_image_id": 123  // Optional
    }

    Returns: {"workflow_history_id": 123}
    """
    try:
        from content.models import WorkflowHistory

        workflow_type = request.data.get('workflow_type', '').strip()
        workflow_name = request.data.get('workflow_name', '').strip()
        prompt = request.data.get('prompt', '').strip()
        improved_prompt = request.data.get('improved_prompt', '').strip()
        config = request.data.get('config', {})
        input_image_id = request.data.get('input_image_id')

        if not workflow_type or not workflow_name:
            return Response({
                'error': 'workflow_type and workflow_name are required'
            }, status=400)

        # Create workflow history record
        workflow_history = WorkflowHistory.objects.create(
            user=request.user,
            workflow_type=workflow_type,
            workflow_name=workflow_name,
            prompt=prompt,
            improved_prompt=improved_prompt,
            config=config,
            input_image_id=input_image_id,
            status='running'
        )

        logger.info(f"✅ Started tracking workflow execution: {workflow_history.id} ({workflow_name})")

        return Response({
            'success': True,
            'workflow_history_id': workflow_history.id
        })

    except Exception as e:
        logger.error(f"❌ Error starting workflow execution: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_workflow_execution(request, workflow_id):
    """
    Update workflow history record when workflow completes
    Session 57: Phase B.2 - Workflow History & Favorites

    Expected JSON:
    {
        "status": "completed" | "failed",
        "execution_time": 12.5,  // seconds
        "result_images": ["url1", "url2"],  // For completed
        "error_message": "Error details"  // For failed
    }
    """
    try:
        from content.models import WorkflowHistory

        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        status = request.data.get('status', '').strip().lower()
        execution_time = float(request.data.get('execution_time', 0))

        if status == 'completed':
            result_images = request.data.get('result_images', [])
            workflow.mark_completed(execution_time, result_images)
            logger.info(f"✅ Completed workflow execution: {workflow.id} ({workflow.workflow_name}) - {len(result_images)} results")

        elif status == 'failed':
            error_message = request.data.get('error_message', 'Unknown error')
            workflow.mark_failed(error_message)
            workflow.execution_time = execution_time
            workflow.save(update_fields=['execution_time'])
            logger.error(f"❌ Failed workflow execution: {workflow.id} ({workflow.workflow_name}) - {error_message}")

        else:
            return Response({
                'error': 'status must be "completed" or "failed"'
            }, status=400)

        return Response({
            'success': True,
            'workflow_history_id': workflow.id,
            'status': workflow.status
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error completing workflow execution: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# =============================================================================
# SESSION 60: PHASE C.1.2 - PROJECT MANAGEMENT API ENDPOINTS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_projects(request):
    """
    List all creative projects for current user
    Session 60: Phase C.1.2 - Project Management API

    GET /api/projects/

    Returns:
        {
            "projects": [
                {
                    "id": "uuid",
                    "name": "Brand Launch Campaign",
                    "description": "...",
                    "goal": "...",
                    "status": "in_progress",
                    "category": "Branding",
                    "deadline": "2025-12-31T23:59:59Z",
                    "total_workflows": 5,
                    "completed_workflows": 2,
                    "progress_percentage": 40,
                    "is_overdue": false,
                    "created_at": "2025-11-06T12:00:00Z",
                    "updated_at": "2025-11-06T14:00:00Z"
                }
            ]
        }
    """
    try:
        from content.models import CreativeProject

        projects = CreativeProject.objects.filter(user=request.user).order_by('-created_at')

        project_data = []
        for project in projects:
            project_data.append({
                'id': str(project.id),
                'name': project.name,
                'description': project.description,
                'goal': project.goal,
                'status': project.status,
                'category': project.category,
                'colors': project.colors,  # Session 63: Professional agency intake field
                'tags': project.tags,
                'deadline': project.deadline.isoformat() if project.deadline else None,
                'total_workflows': project.total_workflows,
                'completed_workflows': project.completed_workflows,
                'progress_percentage': project.progress_percentage,
                'is_overdue': project.is_overdue,
                'is_shared': project.is_shared,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat()
            })

        logger.info(f"✅ Loaded {len(project_data)} projects for user {request.user.username}")

        return Response({'projects': project_data})

    except Exception as e:
        logger.error(f"❌ Error listing projects: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    """
    Create a new creative project
    Session 60: Phase C.1.2 - Project Management API

    POST /api/projects/
    Body:
        {
            "name": "Brand Launch Campaign",
            "description": "Complete brand identity for new startup",
            "goal": "Create professional brand assets",
            "deadline": "2025-12-31T23:59:59Z" (optional),
            "category": "Branding" (optional),
            "tags": ["logo", "branding", "social"] (optional)
        }

    Returns:
        {
            "success": true,
            "project": { ... project data ... }
        }
    """
    try:
        from content.models import CreativeProject
        from django.utils.dateparse import parse_datetime

        # Validate required fields
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        goal = request.data.get('goal', '').strip()

        if not name:
            return Response({
                'error': 'Project name is required'
            }, status=400)

        if not goal:
            return Response({
                'error': 'Project goal is required'
            }, status=400)

        # Optional fields
        deadline_str = request.data.get('deadline')
        deadline = None
        if deadline_str:
            deadline = parse_datetime(deadline_str)

        category = request.data.get('category', '')
        colors = request.data.get('colors', '')  # Session 63: Professional agency intake field
        tags = request.data.get('tags', [])

        # Create project
        project = CreativeProject.objects.create(
            user=request.user,
            name=name,
            description=description,
            goal=goal,
            deadline=deadline,
            category=category,
            colors=colors,
            tags=tags
        )

        logger.info(f"✅ Created project '{name}' for user {request.user.username}")

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.name,
                'description': project.description,
                'goal': project.goal,
                'status': project.status,
                'category': project.category,
                'colors': project.colors,  # Session 63: Professional agency intake field
                'tags': project.tags,
                'deadline': project.deadline.isoformat() if project.deadline else None,
                'total_workflows': project.total_workflows,
                'completed_workflows': project.completed_workflows,
                'progress_percentage': project.progress_percentage,
                'created_at': project.created_at.isoformat()
            }
        }, status=201)

    except Exception as e:
        logger.error(f"❌ Error creating project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project(request, project_id):
    """
    Get detailed information about a specific project
    Session 60: Phase C.1.2 - Project Management API

    GET /api/projects/<uuid:project_id>/

    Returns:
        {
            "project": {
                ... project data ...,
                "workflows": [
                    {
                        "id": "uuid",
                        "workflow_name": "Logo Creator",
                        "workflow_type": "logo_creator",
                        "status": "completed",
                        "order": 0,
                        "notes": "Main logo design",
                        "created_at": "...",
                        "result_count": 3
                    }
                ]
            }
        }
    """
    try:
        from content.models import CreativeProject

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Get all workflows in this project
        workflows_data = []
        for pw in project.workflows.all():
            workflows_data.append({
                'id': str(pw.id),
                'workflow_history_id': str(pw.workflow_history.id),
                'workflow_name': pw.workflow_history.workflow_name,
                'workflow_type': pw.workflow_history.workflow_type,
                'status': pw.workflow_history.status,
                'order': pw.order,
                'notes': pw.notes,
                'added_at': pw.added_at.isoformat(),
                'result_count': pw.workflow_history.result_count,
                'execution_time': pw.workflow_history.execution_time
            })

        project_data = {
            'id': str(project.id),
            'name': project.name,
            'description': project.description,
            'goal': project.goal,
            'status': project.status,
            'category': project.category,
            'colors': project.colors,  # Session 63: Professional agency intake field
            'tags': project.tags,
            'deadline': project.deadline.isoformat() if project.deadline else None,
            'total_workflows': project.total_workflows,
            'completed_workflows': project.completed_workflows,
            'progress_percentage': project.progress_percentage,
            'is_overdue': project.is_overdue,
            'is_shared': project.is_shared,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat(),
            'workflows': workflows_data
        }

        return Response({'project': project_data})

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error getting project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_project(request, project_id):
    """
    Update an existing project
    Session 60: Phase C.1.2 - Project Management API

    PUT/PATCH /api/projects/<uuid:project_id>/
    Body:
        {
            "name": "Updated Name" (optional),
            "description": "..." (optional),
            "goal": "..." (optional),
            "status": "in_progress" (optional),
            "deadline": "..." (optional),
            "category": "..." (optional),
            "tags": [...] (optional)
        }

    Returns:
        {
            "success": true,
            "project": { ... updated project data ... }
        }
    """
    try:
        from content.models import CreativeProject
        from django.utils.dateparse import parse_datetime

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Update fields if provided
        if 'name' in request.data:
            project.name = request.data['name'].strip()

        if 'description' in request.data:
            project.description = request.data['description'].strip()

        if 'goal' in request.data:
            project.goal = request.data['goal'].strip()

        if 'status' in request.data:
            status = request.data['status']
            valid_statuses = ['planning', 'in_progress', 'review', 'completed', 'archived']
            if status in valid_statuses:
                project.status = status

        if 'deadline' in request.data:
            deadline_str = request.data['deadline']
            if deadline_str:
                project.deadline = parse_datetime(deadline_str)
            else:
                project.deadline = None

        if 'category' in request.data:
            project.category = request.data['category']

        if 'colors' in request.data:  # Session 63: Professional agency intake field
            project.colors = request.data['colors']

        if 'tags' in request.data:
            project.tags = request.data['tags']

        project.save()

        logger.info(f"✅ Updated project '{project.name}' for user {request.user.username}")

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.name,
                'description': project.description,
                'goal': project.goal,
                'status': project.status,
                'category': project.category,
                'colors': project.colors,  # Session 63: Professional agency intake field
                'tags': project.tags,
                'deadline': project.deadline.isoformat() if project.deadline else None,
                'progress_percentage': project.progress_percentage,
                'updated_at': project.updated_at.isoformat()
            }
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error updating project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_project(request, project_id):
    """
    Delete a project
    Session 60: Phase C.1.2 - Project Management API

    DELETE /api/projects/<uuid:project_id>/

    Returns:
        {
            "success": true,
            "message": "Project deleted successfully"
        }
    """
    try:
        from content.models import CreativeProject

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        project_name = project.name
        project.delete()

        logger.info(f"✅ Deleted project '{project_name}' for user {request.user.username}")

        return Response({
            'success': True,
            'message': f"Project '{project_name}' deleted successfully"
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error deleting project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_workflow_to_project(request, project_id):
    """
    Add a workflow to a project
    Session 60: Phase C.1.2 - Project Management API

    POST /api/projects/<uuid:project_id>/workflows/
    Body:
        {
            "workflow_history_id": "uuid",
            "order": 0 (optional),
            "notes": "Main logo design" (optional)
        }

    Returns:
        {
            "success": true,
            "project_workflow": { ... }
        }
    """
    try:
        from content.models import CreativeProject, ProjectWorkflow, WorkflowHistory

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        workflow_history_id = request.data.get('workflow_history_id')
        if not workflow_history_id:
            return Response({
                'error': 'workflow_history_id is required'
            }, status=400)

        # Session 60: Using UUID for workflow lookup
        workflow_history = WorkflowHistory.objects.get(
            id=workflow_history_id,
            user=request.user
        )

        # Check if already in project
        existing = ProjectWorkflow.objects.filter(
            project=project,
            workflow_history=workflow_history
        ).exists()

        if existing:
            return Response({
                'error': 'Workflow already in this project'
            }, status=400)

        # Get order (default to end of list)
        order = request.data.get('order')
        if order is None:
            # Add to end
            max_order = project.workflows.count()
            order = max_order

        notes = request.data.get('notes', '')

        # Create link
        project_workflow = ProjectWorkflow.objects.create(
            project=project,
            workflow_history=workflow_history,
            order=order,
            notes=notes
        )

        logger.info(f"✅ Added workflow '{workflow_history.workflow_name}' to project '{project.name}'")

        return Response({
            'success': True,
            'project_workflow': {
                'id': str(project_workflow.id),
                'project_id': str(project.id),
                'workflow_history_id': str(workflow_history.id),
                'workflow_name': workflow_history.workflow_name,
                'order': project_workflow.order,
                'notes': project_workflow.notes,
                'added_at': project_workflow.added_at.isoformat()
            }
        }, status=201)

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error adding workflow to project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_workflow_from_project(request, project_id, workflow_id):
    """
    Remove a workflow from a project
    Session 60: Phase C.1.2 - Project Management API

    DELETE /api/projects/<uuid:project_id>/workflows/<uuid:workflow_id>/

    Returns:
        {
            "success": true,
            "message": "Workflow removed from project"
        }
    """
    try:
        from content.models import CreativeProject, ProjectWorkflow

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Session 60: Using UUID for ProjectWorkflow lookup
        project_workflow = ProjectWorkflow.objects.get(
            id=workflow_id,
            project=project
        )

        workflow_name = project_workflow.workflow_history.workflow_name
        project_workflow.delete()

        logger.info(f"✅ Removed workflow '{workflow_name}' from project '{project.name}'")

        return Response({
            'success': True,
            'message': f"Workflow '{workflow_name}' removed from project"
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except ProjectWorkflow.DoesNotExist:
        return Response({
            'error': 'Workflow not in this project'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error removing workflow from project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# ===================================================================
# SESSION 61: PHASE C.2.1 - PORTFOLIO VIEW API
# ===================================================================
# Portfolio aggregates ALL content (images, videos, audio) from ALL projects
# Provides unified view with filtering and sorting capabilities
# ===================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_portfolio(request):
    """
    GET /api/portfolio/

    Aggregate all content (images, videos, audio) from all user's creative projects

    Query Parameters:
    - project_id: Filter by specific project (UUID)
    - content_type: Filter by type (image/video/audio)
    - date_from: Start date (ISO format)
    - date_to: End date (ISO format)
    - sort_by: Sort field (created_at/project_name/type) default: -created_at
    - search: Search across prompts, models, styles (Session 62: Phase C.2.1)
    """
    try:
        # Import models locally
        from content.models import ImageHistory, VideoHistory
        from django.utils.dateparse import parse_datetime
        from django.db.models import Q

        logger.info(f"📊 Loading portfolio for user: {request.user.username}")

        # Get query parameters
        project_id = request.GET.get('project_id')
        content_type = request.GET.get('content_type')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        sort_by = request.GET.get('sort_by', '-created_at')
        search_query = request.GET.get('search', '').strip()  # Session 62: Phase C.2.1

        # Base filters
        image_filter = {'user': request.user}
        video_filter = {'user': request.user}
        audio_filter = {'user': request.user}

        # Apply date filtering
        if date_from:
            try:
                from_date = parse_datetime(date_from)
                if from_date:
                    image_filter['created_at__gte'] = from_date
                    video_filter['created_at__gte'] = from_date
                    audio_filter['created_at__gte'] = from_date
            except Exception as e:
                logger.warning(f"⚠️ Invalid date_from: {date_from}")

        if date_to:
            try:
                to_date = parse_datetime(date_to)
                if to_date:
                    image_filter['created_at__lte'] = to_date
                    video_filter['created_at__lte'] = to_date
                    audio_filter['created_at__lte'] = to_date
            except Exception as e:
                logger.warning(f"⚠️ Invalid date_to: {date_to}")

        # Collect content items
        portfolio_items = []

        # Query images
        if not content_type or content_type == 'image':
            images_query = ImageHistory.objects.filter(**image_filter).select_related('user')

            # Session 62: Phase C.2.1 - Apply search filter
            if search_query:
                images_query = images_query.filter(
                    Q(prompt__icontains=search_query) |
                    Q(model_used__icontains=search_query) |
                    Q(style__icontains=search_query) |
                    Q(image_type__icontains=search_query)
                )

            images = images_query
            for img in images:
                # Session 63: Find associated projects - check direct project field first
                projects = []

                # Session 63: Check direct project relationship (new approach)
                if hasattr(img, 'project') and img.project:
                    if not project_id or str(img.project.id) == project_id:
                        projects.append({
                            'id': str(img.project.id),
                            'name': img.project.name,
                            'status': img.project.status
                        })
                # Also check via WorkflowHistory (legacy approach)
                elif hasattr(img, 'workflow_executions') and img.workflow_executions.exists():
                    for wf in img.workflow_executions.all():
                        project_workflows = wf.projects.select_related('project').all()
                        for pw in project_workflows:
                            if not project_id or str(pw.project.id) == project_id:
                                projects.append({
                                    'id': str(pw.project.id),
                                    'name': pw.project.name,
                                    'status': pw.project.status
                                })

                # Skip if project filter doesn't match
                if project_id and not projects:
                    continue

                portfolio_items.append({
                    'id': str(img.id),
                    'type': 'image',
                    'content_url': img.get_full_url(),
                    'thumbnail_url': img.get_thumbnail_url(),
                    'prompt': img.prompt,
                    'model': img.model_used,
                    'style': img.style,
                    'operation_type': img.image_type,
                    'created_at': img.created_at.isoformat(),
                    'view_count': img.view_count,
                    'download_count': img.download_count,
                    'is_favorite': img.is_favorite,
                    'projects': projects,
                    'metadata': {
                        'width': img.image_width,
                        'height': img.image_height,
                        'file_size': img.file_size_bytes,
                        'parameters': img.parameters
                    }
                })

        # Query videos
        if not content_type or content_type == 'video':
            videos_query = VideoHistory.objects.filter(**video_filter).select_related('user')

            # Session 62: Phase C.2.1 - Apply search filter
            if search_query:
                videos_query = videos_query.filter(
                    Q(prompt__icontains=search_query) |
                    Q(model_used__icontains=search_query) |
                    Q(video_type__icontains=search_query)
                )

            videos = videos_query
            for vid in videos:
                # Session 63: Find associated projects - check direct project field first
                projects = []

                # Session 63: Check direct project relationship (new approach)
                if hasattr(vid, 'project') and vid.project:
                    if not project_id or str(vid.project.id) == project_id:
                        projects.append({
                            'id': str(vid.project.id),
                            'name': vid.project.name,
                            'status': vid.project.status
                        })
                # Also check via WorkflowHistory (legacy approach)
                elif hasattr(vid, 'workflow_executions') and vid.workflow_executions.exists():
                    for wf in vid.workflow_executions.all():
                        project_workflows = wf.projects.select_related('project').all()
                        for pw in project_workflows:
                            if not project_id or str(pw.project.id) == project_id:
                                projects.append({
                                    'id': str(pw.project.id),
                                    'name': pw.project.name,
                                    'status': pw.project.status
                                })

                if project_id and not projects:
                    continue

                portfolio_items.append({
                    'id': str(vid.id),
                    'type': 'video',
                    'content_url': vid.video_url,
                    'thumbnail_url': vid.thumbnail_url or vid.video_url,
                    'prompt': vid.prompt,
                    'operation_type': vid.video_type,
                    'created_at': vid.created_at.isoformat(),
                    'view_count': vid.view_count,
                    'download_count': vid.download_count,
                    'is_favorite': vid.is_favorite,
                    'projects': projects,
                    'metadata': {
                        'duration': vid.duration,
                        'width': vid.video_width,
                        'height': vid.video_height,
                        'provider': 'runway',
                        'model': vid.model_used,
                        'status': vid.status
                    }
                })

        # Query audio
        # TODO: Implement AudioHistory model first (currently using Runway ML but no model tracking)
        # if not content_type or content_type == 'audio':
        #     audio_items = AudioHistory.objects.filter(**audio_filter).select_related('user')
        #     for aud in audio_items:
        #         # Find associated projects
        #         projects = []
        #         if hasattr(aud, 'workflow_executions') and aud.workflow_executions.exists():
        #             for wf in aud.workflow_executions.all():
        #                 project_workflows = wf.projects.select_related('project').all()
        #                 for pw in project_workflows:
        #                     if not project_id or str(pw.project.id) == project_id:
        #                         projects.append({
        #                             'id': str(pw.project.id),
        #                             'name': pw.project.name,
        #                             'status': pw.project.status
        #                         })
        #
        #         if project_id and not projects:
        #             continue
        #
        #         portfolio_items.append({
        #             'id': str(aud.id),
        #             'type': 'audio',
        #             'content_url': aud.audio_url,
        #             'thumbnail_url': None,
        #             'prompt': aud.prompt,
        #             'operation_type': aud.operation_type,
        #             'created_at': aud.created_at.isoformat(),
        #             'view_count': aud.view_count,
        #             'download_count': aud.download_count,
        #             'is_favorite': aud.is_favorite,
        #             'projects': projects,
        #             'metadata': {
        #                 'duration': aud.duration,
        #                 'voice': aud.voice,
        #                 'provider': 'runway'
        #             }
        #         })

        # Sort results
        if sort_by == 'created_at':
            portfolio_items.sort(key=lambda x: x['created_at'])
        elif sort_by == '-created_at':
            portfolio_items.sort(key=lambda x: x['created_at'], reverse=True)
        elif sort_by == 'type':
            portfolio_items.sort(key=lambda x: x['type'])
        elif sort_by == 'project_name':
            # Sort by first project name if exists
            portfolio_items.sort(key=lambda x: x['projects'][0]['name'] if x['projects'] else 'zzzz')

        # Get summary stats
        stats = {
            'total_items': len(portfolio_items),
            'images': sum(1 for item in portfolio_items if item['type'] == 'image'),
            'videos': sum(1 for item in portfolio_items if item['type'] == 'video'),
            'audio': sum(1 for item in portfolio_items if item['type'] == 'audio'),
            'favorites': sum(1 for item in portfolio_items if item['is_favorite']),
            'total_views': sum(item['view_count'] for item in portfolio_items),
            'total_downloads': sum(item['download_count'] for item in portfolio_items)
        }

        logger.info(f"✅ Portfolio loaded: {stats['total_items']} items ({stats['images']} images, {stats['videos']} videos, {stats['audio']} audio)")

        return Response({
            'success': True,
            'portfolio': portfolio_items,
            'stats': stats,
            'filters': {
                'project_id': project_id,
                'content_type': content_type,
                'date_from': date_from,
                'date_to': date_to,
                'sort_by': sort_by
            }
        })

    except Exception as e:
        logger.error(f"❌ Error loading portfolio: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_workflow_for_project(request):
    """
    Session 63: Execute workflow and link results to project
    Endpoint: /api/workflows/execute-for-project/
    """
    try:
        project_id = request.data.get('project_id')
        workflow_type = request.data.get('workflow_type')
        form_data = request.data.get('form_data')

        if not all([project_id, workflow_type, form_data]):
            return Response({
                'success': False,
                'error': 'Missing required fields: project_id, workflow_type, form_data'
            }, status=400)

        # Verify project exists and belongs to user
        from content.models import CreativeProject
        try:
            project = CreativeProject.objects.get(id=project_id, user=request.user)
        except CreativeProject.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        logger.info(f"🎨 Executing {workflow_type} for project: {project.name}")

        # Session 63: Build prompt from form data AND PROJECT GOAL!
        prompt = build_prompt_from_form(workflow_type, form_data, project)

        if not prompt:
            return Response({
                'success': False,
                'error': f'Could not build prompt for workflow type: {workflow_type}'
            }, status=400)

        logger.info(f"📝 Built prompt: {prompt}")

        # Execute workflow based on type
        results = []
        error_messages = []  # Session 64: Collect error messages for debugging

        if workflow_type == 'logo-creator':
            # Session 64: Choose model based on logo style - SDXL for character mascots, Core for flat logos
            logo_style = form_data.get('logoStyle', 'character-mascot')
            model = 'sdxl' if logo_style == 'character-mascot' else 'core'

            # Session 64: Truncate prompt if too long (SDXL limit is 2000 chars)
            if len(prompt) > 2000:
                logger.warning(f"⚠️ Prompt too long ({len(prompt)} chars), truncating intelligently")

                # Session 64: Intelligent truncation - prioritize CRITICAL keywords
                # GPT-5 puts clothing in the middle, which gets cut by naive truncation!

                # Extract sentences with critical keywords (clothing, accessories, key features)
                import re
                critical_keywords = ['WEARING', 'DRESSED', 'PLATFORM', 'necklace', 'pants', 'shoes',
                                   'outfit', 'clothing', 'accessory', 'bell-bottom', 'disco ball']

                # Split into sentences
                sentences = re.split(r'[.!?]\s+', prompt)

                # Categorize sentences
                critical_sentences = []
                normal_sentences = []

                for sent in sentences:
                    if any(keyword.lower() in sent.lower() for keyword in critical_keywords):
                        critical_sentences.append(sent)
                    else:
                        normal_sentences.append(sent)

                # Build truncated prompt: critical details + as many normal details as fit
                prompt_parts = []
                char_count = 0

                # Always include critical sentences (clothing!)
                for sent in critical_sentences:
                    if char_count + len(sent) + 2 < 1900:  # Leave room for period
                        prompt_parts.append(sent)
                        char_count += len(sent) + 2

                # Add normal sentences until we hit limit
                for sent in normal_sentences:
                    if char_count + len(sent) + 2 < 1950:
                        prompt_parts.append(sent)
                        char_count += len(sent) + 2
                    else:
                        break

                prompt = '. '.join(prompt_parts) + '.'
                logger.info(f"📝 Intelligently truncated to {len(prompt)} chars, kept {len(critical_sentences)} critical sentences")
                logger.info(f"📝 Truncated prompt: {prompt[:200]}...")

            # Generate 1 logo (style already included in prompt by build_prompt_from_form)
            # Session 64: Pass empty string as style since prompt already contains style terms
            result = generate_image_with_stability(
                prompt=prompt,
                model=model,
                style='',  # Use empty string to avoid applying additional style preset (prompt has style terms already)
                user=request.user
            )
            if result and result.get('success'):
                results.append(result)
            elif result and result.get('error'):
                error_messages.append(f"Logo generation failed: {result.get('error')}")
            else:
                error_messages.append("Logo generation returned no result")

        elif workflow_type == 'portrait-enhancer':
            # Generate 1 high-quality portrait
            result = generate_image_with_stability(
                prompt=prompt,
                model='sd3',
                style='photographic',
                user=request.user
            )
            if result and result.get('success'):
                results.append(result)

        elif workflow_type == 'style-explorer':
            # Generate 5 images in different styles
            styles = ['photographic', 'digital-art', 'cinematic', 'anime', 'fantasy-art']
            for style in styles:
                result = generate_image_with_stability(
                    prompt=prompt,
                    model='sdxl',
                    style=style,
                    user=request.user
                )
                if result and result.get('success'):
                    results.append(result)

        elif workflow_type == 'social-media-pack':
            # Generate 3 optimized images
            for i in range(3):
                result = generate_image_with_stability(
                    prompt=prompt,
                    model='sdxl',
                    style='photographic',
                    user=request.user
                )
                if result and result.get('success'):
                    results.append(result)

        elif workflow_type == 'product-mockup':
            # Generate 1 product visualization
            result = generate_image_with_stability(
                prompt=prompt,
                model='ultra',
                style='photographic',
                user=request.user
            )
            if result and result.get('success'):
                results.append(result)

        elif workflow_type == 'creative-upscale':
            # Note: This requires an existing image - handle separately
            return Response({
                'success': False,
                'error': 'Creative Upscale requires selecting an existing image first'
            }, status=400)

        # Link all generated images to the project
        if results:
            from content.models import ImageHistory
            linked_count = 0

            for result in results:
                if result.get('image_id'):
                    try:
                        image = ImageHistory.objects.get(id=result['image_id'], user=request.user)
                        image.project = project
                        image.save()
                        linked_count += 1
                        logger.info(f"✅ Linked image {image.id} to project {project.name}")
                    except ImageHistory.DoesNotExist:
                        logger.warning(f"⚠️ Image {result['image_id']} not found")

            logger.info(f"🎉 Successfully generated and linked {linked_count} assets to project {project.name}")

            return Response({
                'success': True,
                'count': linked_count,
                'message': f'Generated {linked_count} assets for {project.name}'
            })
        else:
            # Session 64: Include actual error messages for debugging
            error_detail = 'No images were generated'
            if error_messages:
                error_detail += ': ' + '; '.join(error_messages)

            return Response({
                'success': False,
                'error': error_detail
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Error executing workflow for project: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


def build_prompt_from_form(workflow_type, form_data, project=None):
    """
    Build prompt string from form data based on workflow type
    Session 63: GOAL-DRIVEN prompt builder - Vision comes FIRST!
    """
    # Session 63: If user provided a custom prompt, use it directly
    custom_prompt = form_data.get('customPrompt', '').strip()
    if custom_prompt:
        return custom_prompt

    if workflow_type == 'logo-creator':
        parts = []

        # Session 64: CORE VISUAL SUBJECT FIRST! AI commits to the subject in first few tokens.
        # If we say "Disco Dinosaur logo" first, AI generates disco (human dancer).
        # If we say "T-Rex dinosaur in disco style" first, AI generates T-Rex!
        details = form_data.get('additionalDetails', '')
        if details:
            parts.append(details)

        # Session 64: Style terms come SECOND to reinforce the subject
        logo_style = form_data.get('logoStyle', 'character-mascot')
        style_map = {
            'character-mascot': 'cool cartoon character mascot standing upright, anthropomorphic, DreamWorks animation style, expressive, detailed illustration, cinematic lighting, 4K resolution, professional quality',
            'vector': 'professional vector art, flat design, clean lines, minimalist, iconic symbol, modern, simple shapes',
            'illustrative': 'hand-drawn illustration style, artistic, detailed linework, creative, sketch-like quality, unique character',
            'minimalist': 'minimalist design, simple and clean, negative space, modern, geometric, essential elements only',
            'badge': 'badge design, emblem style, traditional, detailed ornamental, crest, vintage feel, professional seal',
            'geometric': 'geometric shapes, abstract patterns, angular design, modern, mathematical precision, structured'
        }
        style_terms = style_map.get(logo_style, style_map['character-mascot'])
        parts.append(style_terms)

        # Business name comes AFTER subject is clear
        business_name = form_data.get('businessName', '')
        if business_name:
            parts.append(f"for {business_name}")

        colors = form_data.get('colors', '')
        if colors:
            parts.append(f'color scheme: {colors}')

        # Session 63: Vision/Goal adds context but comes AFTER core subject
        if project and project.goal:
            parts.append(f"Brand vision: {project.goal.strip()}")

        industry = form_data.get('industry', '')
        if industry:
            industry_map = {
                'tech': 'technology company',
                'coffee': 'coffee shop',
                'fitness': 'fitness gym',
                'food': 'restaurant',
                'finance': 'financial services',
                'health': 'healthcare',
                'education': 'education',
                'retail': 'retail store',
                'creative': 'creative agency',
                'construction': 'construction company'
            }
            parts.append(industry_map.get(industry, industry))

        # Additional project context comes last
        if project and project.description:
            parts.append(project.description.strip())

        parts.append('logo design')

        return ', '.join(parts)

    elif workflow_type == 'portrait-enhancer':
        subject = form_data.get('subject', '')
        style = form_data.get('style', '')
        lighting = form_data.get('lighting', '')
        background = form_data.get('background', '')

        parts = [subject, 'professional portrait']

        if style:
            parts.append(style)

        if lighting:
            parts.append(f'{lighting}')

        if background:
            parts.append(f'{background} background')

        parts.extend(['high quality', '4K', 'sharp focus', 'professional photography'])

        return ', '.join(parts)

    elif workflow_type == 'social-media-pack':
        content = form_data.get('content', '')
        platform = form_data.get('platform', '')
        colors = form_data.get('colors', '')
        mood = form_data.get('mood', '')

        parts = [content]

        if mood:
            parts.append(mood)

        if colors:
            parts.append(f'colors: {colors}')

        if platform:
            parts.append(f'optimized for {platform}')

        parts.extend(['high quality', 'professional', 'eye-catching'])

        return ', '.join(parts)

    elif workflow_type == 'product-mockup':
        description = form_data.get('description', '')
        colors = form_data.get('colors', '')
        context = form_data.get('context', '')
        style = form_data.get('style', '')

        parts = [description]

        if colors:
            parts.append(colors)

        if context:
            context_map = {
                'studio': 'studio white background',
                'lifestyle': 'lifestyle in-use setting',
                'desk': 'on modern desk workspace',
                'outdoor': 'outdoor natural environment',
                'premium': 'luxury premium setting'
            }
            parts.append(context_map.get(context, context))

        if style:
            parts.append(style)

        parts.extend(['product photography', 'high quality', 'professional'])

        return ', '.join(parts)

    elif workflow_type == 'style-explorer':
        subject = form_data.get('subject', '')
        description = form_data.get('description', '')

        parts = [subject]

        if description:
            parts.append(description)

        return ', '.join(parts)

    return None


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
            image_history = ImageHistory.objects.create(
                user=user,
                filename=image_url.split('/')[-1][:255],  # Session 63: Truncate to 255 chars for database constraint
                file_path=image_url,
                prompt=prompt,
                model_used=model,  # Session 63: Fixed field name
                style=style,
                image_type='generated'  # Session 64: Fixed - 'generated' not 'generation' to match model choices
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
