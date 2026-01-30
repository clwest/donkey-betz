"""
Stability AI Service - Session 872
==================================

Centralized service for Stability AI image generation with:
- Adaptive timeout based on model complexity
- Exponential backoff retry logic for transient failures
- Unified API key retrieval

This service is used by:
- ImageAgent (core/agents/image_agent.py)
- ImageGenerationService (content/image_generation.py)
"""

import logging
import os
import time
from typing import Dict, Any, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Model complexity affects generation time
MODEL_TIMEOUT_MULTIPLIERS = {
    'core': 1.0,      # Fastest - ~3.5s typical
    'sdxl': 1.5,      # Balanced - ~5.8s typical
    'sd3': 2.0,       # High quality - ~8.7s typical
    'ultra': 2.5,     # Premium - ~10.4s typical
}


def get_stability_api_key() -> Optional[str]:
    """
    Get Stability AI API key from environment or settings.

    Returns:
        API key string or None if not configured
    """
    # Check environment first
    key = os.getenv('STABILITY_API_KEY')
    if key:
        return key

    # Check Django settings
    if hasattr(settings, 'EXTERNAL_API_KEYS'):
        key = settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if key:
            return key

    # Check direct attribute
    return getattr(settings, 'STABILITY_API_KEY', None)


def calculate_adaptive_timeout(model: str, num_images: int = 1, base_timeout: int = 45) -> int:
    """
    Calculate adaptive timeout based on model and number of images.

    Args:
        model: Stability AI model name (core, sdxl, sd3, ultra)
        num_images: Number of images to generate
        base_timeout: Base timeout in seconds

    Returns:
        Timeout in seconds
    """
    multiplier = MODEL_TIMEOUT_MULTIPLIERS.get(model, 1.5)

    # Calculate timeout: base + (per_image * multiplier * num_images)
    per_image_time = 15  # Base time per image
    timeout = base_timeout + int(per_image_time * multiplier * num_images)

    # Cap at 180 seconds (3 minutes)
    return min(timeout, 180)


def stability_request_with_retry(
    url: str,
    headers: Dict[str, str],
    data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = 60,
    max_retries: int = 3,
    accept_type: str = "image/*"
) -> Dict[str, Any]:
    """
    Make a request to Stability AI API with retry logic.

    Features:
    - Exponential backoff retry for transient failures
    - Detailed error reporting
    - Support for both JSON and multipart/form-data requests

    Args:
        url: API endpoint URL
        headers: Request headers
        data: Form data (for multipart requests)
        files: Files to upload (for multipart requests)
        json_data: JSON body (for JSON requests)
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        accept_type: Accept header value

    Returns:
        Dict with success, content/data, error, status_code, retries_used
    """
    last_error = None
    retries_used = 0

    for attempt in range(max_retries):
        try:
            logger.info(f"🎨 Stability AI request attempt {attempt + 1}/{max_retries} "
                       f"(timeout={timeout}s)")

            if json_data:
                # JSON request (SDXL)
                response = requests.post(
                    url,
                    headers=headers,
                    json=json_data,
                    timeout=timeout
                )
            else:
                # Multipart/form-data request (SD3, Core, Ultra)
                response = requests.post(
                    url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=timeout
                )

            if response.status_code == 200:
                logger.info(f"✅ Stability AI request succeeded on attempt {attempt + 1}")

                # Return appropriate content based on accept type
                if accept_type == "application/json":
                    return {
                        'success': True,
                        'data': response.json(),
                        'retries_used': retries_used,
                        'status_code': 200
                    }
                else:
                    return {
                        'success': True,
                        'content': response.content,
                        'retries_used': retries_used,
                        'status_code': 200
                    }

            # Check if error is retryable
            if response.status_code in [429, 500, 502, 503, 504]:
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                retries_used += 1
                wait_time = (2 ** attempt) + 1  # Exponential backoff: 2s, 5s, 9s
                logger.warning(f"⚠️ Stability AI request failed (retryable): {last_error}. "
                              f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            else:
                # Non-retryable error
                logger.error(f"❌ Stability AI request failed (non-retryable): {response.text[:200]}")
                return {
                    'success': False,
                    'error': response.text,
                    'status_code': response.status_code,
                    'retries_used': retries_used
                }

        except requests.exceptions.Timeout:
            last_error = f"Timeout after {timeout} seconds"
            retries_used += 1
            logger.warning(f"⚠️ Stability AI timeout on attempt {attempt + 1}")
            # Increase timeout on retry
            timeout = min(timeout + 30, 180)
            continue

        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection error: {str(e)}"
            retries_used += 1
            wait_time = (2 ** attempt) + 1
            logger.warning(f"⚠️ Stability AI connection error. Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
            continue

        except Exception as e:
            logger.error(f"❌ Stability AI unexpected error: {e}")
            return {
                'success': False,
                'error': str(e),
                'retries_used': retries_used
            }

    # All retries exhausted
    logger.error(f"❌ Stability AI request failed after {max_retries} attempts: {last_error}")
    return {
        'success': False,
        'error': f'Request failed after {max_retries} attempts: {last_error}',
        'retries_used': retries_used
    }
