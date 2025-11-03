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
    Requires: image file, direction (left/right/up/down), pixels (how much to extend), prompt
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Missing image file'
            }, status=400)

        prompt = request.POST.get('prompt', '').strip()
        direction = request.POST.get('direction', '').strip().lower()
        pixels_str = request.POST.get('pixels', '').strip()

        if not all([prompt, direction, pixels_str]):
            return JsonResponse({
                'success': False,
                'error': 'Missing prompt, direction, or pixels'
            }, status=400)

        try:
            pixels = int(pixels_str)
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid pixels value'
            }, status=400)

        if direction not in ['left', 'right', 'up', 'down']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid direction (must be left/right/up/down)'
            }, status=400)

        image_file = request.FILES['image']

        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"📐 Outpaint request: {direction} by {pixels}px - {prompt}")

        url = "https://api.stability.ai/v2beta/stable-image/edit/outpaint"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type)
        }

        data = {
            'prompt': prompt,
            direction: pixels,  # e.g., 'left': 500
            'output_format': 'png'
        }

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Save to server
            filename = f'outpainted_{direction}_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)
            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Outpaint complete - saved to {saved_path}")

            # Save to history (Session 36: Feature 9)
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='outpainted',
                prompt=prompt,
                parameters={
                    'operation': 'outpaint',
                    'direction': direction,
                    'pixels': pixels,
                    'prompt': prompt
                }
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI outpaint error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

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
