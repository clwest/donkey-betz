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
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)


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

        logger.info(f"🎨 Image generation request from {user.username}: {prompt[:50]}...")

        # Try Stability AI first (if API key available)
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        replicate_key = os.getenv('REPLICATE_API_KEY') or settings.AI_PROVIDERS.get('REPLICATE_API_KEY')

        generated_images = []
        provider = None
        cost = 0.0

        if stability_key:
            logger.info("🎨 Attempting generation with Stability AI...")
            try:
                result = generate_with_stability(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_images=num_images,
                    api_key=stability_key
                )
                if result['success']:
                    generated_images = result['images']
                    provider = 'stability'
                    cost = result.get('cost', 0.04)
                    logger.info(f"✅ Stability AI generated {len(generated_images)} images")
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

                # Download image from URL and save
                if 'url' in img_data:
                    response = requests.get(img_data['url'], timeout=30)
                    if response.status_code == 200:
                        file_path = default_storage.save(filename, ContentFile(response.content))
                        url = default_storage.url(file_path)

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
