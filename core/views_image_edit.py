"""
Image views — edit functions.
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

logger = logging.getLogger(__name__)


def _resolve_image_and_bytes(user, image_id, max_pixels=4_194_304):
    """
    Session 1036: Resolve image_id (UUID, sequential number, or Cloudinary URL)
    to an ImageHistory record and its raw bytes.

    Auto-downscales images exceeding max_pixels (default 4MP for Stability AI).

    Returns: (image: ImageHistory, image_data: bytes, error: str | None)
    """
    from content.models import ImageHistory

    if not image_id:
        return None, None, 'image_id required'

    image = None

    # 1. Try as UUID
    try:
        import uuid as _uuid
        _uuid.UUID(str(image_id))
        image = ImageHistory.objects.get(id=image_id, user=user)
    except (ValueError, ImageHistory.DoesNotExist):
        pass

    # 2. Try as Cloudinary URL — lookup by file_path
    if image is None and str(image_id).startswith('http'):
        # Try exact match on file_path
        image = ImageHistory.objects.filter(user=user, file_path=image_id).first()
        if image is None:
            # Try matching the Cloudinary public ID from the URL
            # URLs look like: https://res.cloudinary.com/.../uploads/images/2026/03/<uuid>_<suffix>
            # file_path might be: uploads/images/2026/03/<uuid>.<ext>
            url_path = image_id.split('/upload/')[-1] if '/upload/' in image_id else ''
            if url_path:
                # Strip version prefix (v1/, v2/) if present
                if url_path.startswith('v') and '/' in url_path:
                    url_path = url_path.split('/', 1)[-1]
                # Strip /media/ prefix if present
                if url_path.startswith('media/'):
                    url_path = url_path[6:]
                image = ImageHistory.objects.filter(user=user, file_path__contains=url_path[:40]).first()

    # 3. Try as sequential number
    if image is None:
        try:
            seq = int(image_id)
            images = ImageHistory.objects.filter(user=user).order_by('created_at')
            if 0 < seq <= images.count():
                image = images[seq - 1]
        except (ValueError, TypeError):
            pass

    if image is None:
        return None, None, f'Image not found for: {str(image_id)[:80]}'

    # Fetch image bytes — handle Cloudinary URLs, data URIs, and local paths
    try:
        if image.file_path and image.file_path.startswith('http'):
            resp = requests.get(image.file_path, timeout=30)
            resp.raise_for_status()
            image_data = resp.content
        elif image.file_path and image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()
    except Exception as e:
        logger.error(f"Failed to read image bytes for {image.id}: {e}")
        return None, None, f'Failed to read image file: {e}'

    # Auto-downscale if image exceeds Stability AI's pixel limit
    try:
        from io import BytesIO
        img = PILImage.open(BytesIO(image_data))
        w, h = img.size
        total_pixels = w * h
        if total_pixels > max_pixels:
            scale = (max_pixels / total_pixels) ** 0.5
            new_w = int(w * scale)
            new_h = int(h * scale)
            logger.info(f"Auto-downscaling image {image.id} from {w}x{h} ({total_pixels:,}px) to {new_w}x{new_h} for Stability AI")
            img = img.resize((new_w, new_h), PILImage.LANCZOS)
            buf = BytesIO()
            # Preserve format (PNG for transparency, JPEG otherwise)
            fmt = img.format or ('PNG' if img.mode == 'RGBA' else 'JPEG')
            img.save(buf, format=fmt, quality=95)
            image_data = buf.getvalue()
    except Exception as e:
        logger.warning(f"Auto-downscale check failed for {image.id}, proceeding with original: {e}")

    return image, image_data, None


# ========================================
# SESSION 794: SYSTEM USER FOR AUTONOMOUS OPERATIONS
# ========================================

from django.views.decorators.csrf import csrf_exempt


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


def _execute_apply_color_grade(user, parameters):
    """
    Execute color grading application to video via DaVinci Resolve
    Session 72: AI Assistant integration for color grading!
    Session 84: Enhanced with VideoAgent DaVinci method - NOW ACTUALLY EXECUTES!

    This applies professional color grading to a user's video:
    1. Gets the user's most recent video (or lets them select)
    2. Calls VideoAgent to create DaVinci project
    3. Applies specified color grading style
    4. Renders final video with enhanced colors
    5. Returns the actual color-graded video!

    Parameters:
        style (str): Color grading style (default: 'cinematic')
        video_selection (str): 'last' or 'video_id' (default: 'last')
        video_id (str): Video ID if video_selection is 'video_id'
        intensity (float): Color grade intensity 0.0-1.0 (default: 0.5)

    Returns:
        dict: {
            'success': True,
            'video_id': 'new_video_id',
            'video_url': 'url',
            'style': 'cinematic',
            'intensity': 0.5,
            'message': 'Color grade applied!'
        }
    """
    try:
        from content.models import VideoHistory
        from core.agents import VideoAgent

        # Get parameters
        style = parameters.get('style', 'cinematic').lower()
        video_selection = parameters.get('video_selection', 'last')
        video_id = parameters.get('video_id')
        intensity = parameters.get('intensity', 0.5)

        # Session 84: Map old style names to new ones for backwards compatibility
        style_mappings = {
            'cinematic_warm': 'warm',
            'cinematic_cool': 'cool',
            'somatic': 'cinematic',
            'somatic warm': 'warm',
            'sim-matic': 'cinematic',
            'blue': 'cool',
            'retro': 'vintage',
            'film': 'vintage',
            'modern': 'vibrant',
            'clean': 'vibrant',
            'high_contrast': 'noir',
            'dramatic': 'noir',
            'bold': 'vibrant',
            'soft': 'warm',
            'muted': 'vintage',
            'gentle': 'warm',
            'colorful': 'vibrant',
            'saturated': 'vibrant'
        }

        # Map style or use as-is if it's already a valid new style
        valid_styles = ['cinematic', 'vibrant', 'vintage', 'noir', 'warm', 'cool']
        if style not in valid_styles:
            style = style_mappings.get(style, 'cinematic')

        # Ensure intensity is in range
        intensity = max(0.0, min(1.0, intensity))

        logger.info(f"🎨 AI Assistant apply_color_grade: style={style}, intensity={intensity}")

        # Get video
        if video_selection == 'video_id' and video_id:
            try:
                video = VideoHistory.objects.get(id=video_id, user=user, status='completed')
            except VideoHistory.DoesNotExist:
                return {
                    'success': False,
                    'error': f'Video not found: {video_id}',
                    'message': 'The specified video was not found.'
                }
        else:
            # Get most recent video
            video = VideoHistory.objects.filter(
                user=user,
                status='completed'
            ).order_by('-created_at').first()

            if not video:
                return {
                    'success': False,
                    'error': 'You have no completed videos in your gallery.',
                    'message': 'Please create a video first, then apply color grading to it!'
                }

        logger.info(f"✅ Found video for color grading: {video.id} - {video.prompt[:50]}")

        # Session 84: ACTUALLY EXECUTE COLOR GRADING using VideoAgent!
        logger.info(f"🎬 Session 84: Executing color grading with VideoAgent...")

        video_agent = VideoAgent(user=user)
        result = video_agent.apply_color_grade_davinci(
            video_id=str(video.id),
            style=style,
            intensity=intensity
        )

        # Return result
        if result.get('success'):
            logger.info(f"✅ Session 84: Color grading executed successfully!")
            return {
                'success': True,
                'video_id': result.get('video_id'),
                'video_url': result.get('video_url'),
                'style': style,
                'intensity': intensity,
                'original_video': str(video.id),
                'message': result.get('message', f'✅ {style.capitalize()} color grade applied successfully!'),
                'instructions': f'Your video has been color graded with a professional {style} look at {int(intensity * 100)}% intensity!',
                'note': '🎬 Your new color-graded video is ready in the Video Gallery!'
            }
        else:
            logger.error(f"❌ Session 84: Color grading failed: {result.get('error')}")
            # Session 84: Include all fields even in error response so frontend doesn't crash
            style_descriptions = {
                'cinematic': 'Teal & orange Hollywood look',
                'vibrant': 'Boosted saturation and vivid colors',
                'vintage': 'Retro film aesthetic',
                'noir': 'High contrast black & white',
                'warm': 'Golden hour glow',
                'cool': 'Blue tones and icy feel'
            }
            return {
                'success': False,
                'error': result.get('error', 'Color grading failed'),
                'error_message': result.get('error', 'Color grading failed'),
                'message': '❌ Failed to apply color grade',
                'instructions': 'Please check the logs for details. DaVinci Resolve Studio must be running.',
                'style': style,
                'style_description': style_descriptions.get(style, 'Professional color grading'),
                'video_prompt': video.prompt[:50] if video.prompt else 'Unknown video',
                'video_id': str(video.id)
            }

    except Exception as e:
        logger.error(f"❌ Error in _execute_apply_color_grade: {str(e)}", exc_info=True)
        raise


def _execute_recolor(user, parameters, session=None):
    """
    Internal function for recoloring images.
    Called by ImageEditingAgent.

    Args:
        user: Django user object
        parameters: Dict with image_id, target_color, new_color
        session: Optional session for tracking

    Returns:
        Dict with success, image_id, image_url
    """
    try:
        image_id = parameters.get('image_id')
        target_color = parameters.get('target_color')
        new_color = parameters.get('new_color')

        if not target_color or not new_color:
            return {'success': False, 'error': 'target_color and new_color required'}

        image, image_data, err = _resolve_image_and_bytes(user, image_id)
        if err:
            return {'success': False, 'error': err}

        seq_num = image.get_sequential_number()
        logger.info(f"🎨 Agent recoloring image {image.id} (#{seq_num}): {target_color} → {new_color}")

        # Call Stability AI search-and-recolor API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return {'success': False, 'error': 'Stability AI API key not configured'}

        url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"
        files = {"image": image_data}
        data_params = {
            "prompt": f"Change {target_color} to {new_color}",
            "select_prompt": target_color,
            "output_format": "png"
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI recolor failed: {api_response.text}")
            return {'success': False, 'error': f'Recolor failed: {api_response.text}'}

        # Save the recolored image
        recolored_image_data = api_response.content
        filename = f'recolor_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(recolored_image_data))
        image_url = default_storage.url(saved_path)

        # Create new image history entry
        from content.models import ImageHistory
        new_image = ImageHistory.objects.create(
            user=user,
            prompt=f"Recolored from image #{seq_num}: {target_color} → {new_color}",
            file_path=saved_path,
            filename=filename,
            model_used="stability-recolor",
        )

        logger.info(f"✅ Agent recolored image: {new_image.id}")

        return {
            'success': True,
            'image_id': str(new_image.id),
            'image_url': image_url,
            'sequential_number': new_image.get_sequential_number(),
            'message': f"Image recolored successfully (#{new_image.get_sequential_number()})"
        }

    except Exception as e:
        logger.error(f"❌ Agent recolor error: {e}")
        return {'success': False, 'error': str(e)}


def _execute_remove_background(user, parameters, session=None):
    """
    Internal function for removing image backgrounds.
    Called by ImageEditingAgent.

    Args:
        user: Django user object
        parameters: Dict with image_id
        session: Optional session for tracking

    Returns:
        Dict with success, image_id, image_url
    """
    try:
        image_id = parameters.get('image_id')

        image, image_data, err = _resolve_image_and_bytes(user, image_id)
        if err:
            return {'success': False, 'error': err}

        seq_num = image.get_sequential_number()
        logger.info(f"🎭 Agent removing background from image {image.id} (#{seq_num})")

        # Call Stability AI remove-background API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return {'success': False, 'error': 'Stability AI API key not configured'}

        url = "https://api.stability.ai/v2beta/stable-image/edit/remove-background"
        files = {"image": image_data}
        data_params = {"output_format": "png"}

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI remove-bg failed: {api_response.text}")
            return {'success': False, 'error': f'Remove background failed: {api_response.text}'}

        # Save the processed image
        processed_image_data = api_response.content
        filename = f'nobg_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(processed_image_data))
        image_url = default_storage.url(saved_path)

        # Create new image history entry
        from content.models import ImageHistory
        new_image = ImageHistory.objects.create(
            user=user,
            prompt=f"Background removed from image #{seq_num}",
            file_path=saved_path,
            filename=filename,
            model_used="stability-remove-bg",
        )

        logger.info(f"✅ Agent removed background: {new_image.id}")

        return {
            'success': True,
            'image_id': str(new_image.id),
            'image_url': image_url,
            'sequential_number': new_image.get_sequential_number(),
            'message': f"Background removed successfully (#{new_image.get_sequential_number()})"
        }

    except Exception as e:
        logger.error(f"❌ Agent remove-bg error: {e}")
        return {'success': False, 'error': str(e)}


def _execute_resize_image_for_format(user, parameters):
    """
    Session 182: Resize/adapt an image for different social media formats.

    This creates a new image by resizing and/or cropping the source image
    to fit the target dimensions while maintaining the visual content.

    Parameters:
        source_image_id (str): UUID of the source image
        target_width (int): Target width in pixels
        target_height (int): Target height in pixels
        format_name (str): Optional name for the format (e.g., "banner", "avatar")
        fit_mode (str): "cover" (crop to fill), "contain" (fit within), "stretch"
        project_id (str): Optional project to associate with

    Returns:
        dict: {
            'success': True,
            'image_url': 'URL to resized image',
            'image_id': 'History ID',
            'format': 'banner/post/avatar'
        }
    """
    from PIL import Image
    from io import BytesIO
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    from content.models import ImageHistory
    import os

    try:
        # Session 182: Accept both 'image_id' and 'source_image_id' for compatibility
        source_image_id = parameters.get('image_id') or parameters.get('source_image_id')
        target_width = int(parameters.get('target_width', 1080))
        target_height = int(parameters.get('target_height', 1080))
        format_name = parameters.get('format_name', 'resized')
        fit_mode = parameters.get('fit_mode', 'cover')
        project_id = parameters.get('project_id')

        if not source_image_id:
            raise ValueError("image_id or source_image_id is required")

        # Session 182: Support hybrid ID resolution (sequential number or UUID)
        source_image = None
        try:
            # First, try as UUID
            source_image = ImageHistory.objects.get(id=source_image_id, user=user)
        except (ImageHistory.DoesNotExist, ValueError):
            # Try as sequential number (e.g., "7" or "#7")
            try:
                seq_num = int(str(source_image_id).replace('#', '').strip())
                # Get all user's images ordered by creation date
                user_images = ImageHistory.objects.filter(user=user).order_by('created_at')
                if 1 <= seq_num <= user_images.count():
                    source_image = user_images[seq_num - 1]  # Sequential numbers are 1-based
                    logger.info(f"📍 Resolved sequential number #{seq_num} to image {source_image.id}")
            except (ValueError, TypeError):
                pass

        if not source_image:
            raise ValueError(f"Source image {source_image_id} not found")

        # Load the image
        source_path = source_image.file_path
        if source_path.startswith('/'):
            full_path = source_path
        else:
            full_path = os.path.join(settings.MEDIA_ROOT, source_path)

        if not os.path.exists(full_path):
            # Try with default_storage
            if default_storage.exists(source_path):
                with default_storage.open(source_path, 'rb') as f:
                    img = Image.open(f)
                    img.load()
            else:
                raise ValueError(f"Source image file not found: {source_path}")
        else:
            img = Image.open(full_path)

        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        original_width, original_height = img.size
        target_ratio = target_width / target_height
        original_ratio = original_width / original_height

        if fit_mode == 'cover':
            # Crop to fill target dimensions (most common for social media)
            if original_ratio > target_ratio:
                # Image is wider, crop sides
                new_width = int(original_height * target_ratio)
                left = (original_width - new_width) // 2
                img = img.crop((left, 0, left + new_width, original_height))
            else:
                # Image is taller, crop top/bottom
                new_height = int(original_width / target_ratio)
                top = (original_height - new_height) // 2
                img = img.crop((0, top, original_width, top + new_height))
            # Resize to target
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        elif fit_mode == 'contain':
            # Fit within dimensions with padding
            img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
            # Create background and paste centered
            background = Image.new('RGB', (target_width, target_height), (255, 255, 255))
            offset = ((target_width - img.size[0]) // 2, (target_height - img.size[1]) // 2)
            background.paste(img, offset)
            img = background

        else:  # stretch
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG', quality=95)
        buffer.seek(0)

        # Save to storage
        new_filename = f"generated_images/{user.id}/{format_name}_{uuid.uuid4().hex[:8]}.png"
        file_path = default_storage.save(new_filename, ContentFile(buffer.read()))
        saved_url = default_storage.url(file_path)

        # Get project if specified
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=user)
            except CreativeProject.DoesNotExist:
                pass

        # Session 183: Detect if this is a social media kit image based on format_name
        is_social_media = any(keyword in format_name.lower() for keyword in [
            'social media', 'banner', 'post', 'avatar', 'profile', 'story', 'instagram', 'facebook', 'twitter', 'linkedin'
        ])

        # Save to ImageHistory
        history_record = save_to_history(
            user=user,
            file_path=file_path,
            image_type='social_media' if is_social_media else 'resized',
            prompt=f"Resized for {format_name} ({target_width}x{target_height}) from Image #{source_image.get_sequential_number()}",
            parameters={
                'source_id': str(source_image_id),
                'width': target_width,
                'height': target_height,
                'fit_mode': fit_mode,
                'is_social_media_kit': is_social_media,
                'format_name': format_name
            },
            model_used='PIL',
            style=format_name,
            parent_image=source_image,
            project=project
        )

        logger.info(f"✅ Resized image for {format_name}: {target_width}x{target_height}")

        return {
            'success': True,
            'image_url': saved_url,
            'image_id': str(history_record.id) if history_record else None,
            'format': format_name,
            'dimensions': f"{target_width}x{target_height}"
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_resize_image_for_format: {str(e)}")
        raise


def _execute_upscale(user, parameters, session=None):
    """
    Internal function for upscaling images.
    Called by ImageEditingAgent.

    Args:
        user: Django user object
        parameters: Dict with image_id, scale_factor, creative_upscale
        session: Optional session for tracking

    Returns:
        Dict with success, image_id, image_url
    """
    try:
        image_id = parameters.get('image_id')

        image, image_data, err = _resolve_image_and_bytes(user, image_id)
        if err:
            return {'success': False, 'error': err}

        seq_num = image.get_sequential_number()
        logger.info(f"📈 Agent upscaling image {image.id} (sequential #{seq_num})")

        # Call Stability AI upscale API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return {'success': False, 'error': 'Stability AI API key not configured'}

        url = "https://api.stability.ai/v2beta/stable-image/upscale/conservative"
        files = {"image": image_data}
        data_params = {
            "prompt": "high quality upscale",
            "output_format": "png"
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI upscale failed: {api_response.text}")
            return {'success': False, 'error': f'Upscale failed: {api_response.text}'}

        # Save the upscaled image
        upscaled_image_data = api_response.content
        filename = f'upscaled_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(upscaled_image_data))
        image_url = default_storage.url(saved_path)

        # Create new image history entry
        from content.models import ImageHistory
        new_image = ImageHistory.objects.create(
            user=user,
            prompt=f"Upscaled from image #{seq_num}",
            file_path=saved_path,
            filename=filename,
            model_used="stability-upscale-4x",
        )

        logger.info(f"✅ Agent upscaled image: {new_image.id}")

        return {
            'success': True,
            'image_id': str(new_image.id),
            'image_url': image_url,
            'sequential_number': new_image.get_sequential_number(),
            'message': f"Image upscaled successfully (#{new_image.get_sequential_number()})"
        }

    except Exception as e:
        logger.error(f"❌ Agent upscale error: {e}")
        return {'success': False, 'error': str(e)}


@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def creative_upscale_view(request):
    """
    Creative upscale with prompt - upscale image AND add creative details based on prompt.
    Not just pixel upscaling - actually generates new details!

    Session 151: Advanced Image Editing Suite
    Accepts JSON: {
        image_id: uuid,
        prompt: str (what details to add/enhance),
        creativity: float (0.0-0.35, default 0.3),
        project_id: uuid (optional)
    }
    Note: @login_required removed to support internal RequestFactory calls from agents
    """
    try:
        # Manual authentication check for web requests
        if not request.user or not request.user.is_authenticated:
            logger.warning(f"⚠️ Unauthenticated request to creative_upscale_view")
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

        data = json.loads(request.body)
        image_id = data.get('image_id')
        prompt = data.get('prompt', '').strip()
        creativity = float(data.get('creativity', 0.3))
        project_id = data.get('project_id')

        if not image_id or not prompt:
            return JsonResponse({
                'success': False,
                'error': 'image_id and prompt required'
            }, status=400)

        # Validate creativity range
        if not (0.0 <= creativity <= 0.35):
            creativity = 0.3

        # Get the image from history
        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=request.user)
        except ImageHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        seq_num = image.get_sequential_number()
        logger.info(f"✨ Creative upscale image {image_id} (#{seq_num}) with prompt: '{prompt}'")

        # Get image data
        if image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Call Stability AI creative upscale API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        url = "https://api.stability.ai/v2beta/stable-image/upscale/creative"

        files = {"image": image_data}
        data_params = {
            "prompt": prompt,
            "creativity": creativity,
            "output_format": "png"
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=90)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI creative upscale failed: {api_response.text}")
            return JsonResponse({
                'success': False,
                'error': f'Creative upscale failed: {api_response.text}'
            }, status=500)

        # Save the upscaled image
        upscaled_image_data = api_response.content

        filename = f'creative_upscale_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', request.user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(upscaled_image_data))
        image_url = default_storage.url(saved_path)

        logger.info(f"✅ Saved creative upscale image: {saved_path}")

        # Create new image history entry
        from content.models import CreativeProject
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass

        new_image = ImageHistory.objects.create(
            user=request.user,
            prompt=f"Creative upscale from image #{seq_num}: {prompt}",
            file_path=saved_path,
            filename=filename,
            model_used="stability-creative-upscale",
            project=project
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=new_image,
                project=project,
                contribution_type='editing',
                task_description=f"Creative upscale with details: {prompt}",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {new_image.id}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")

        logger.info(f"✅ Creative upscale successful: {new_image.id}")

        return JsonResponse({
            'success': True,
            'image_id': str(new_image.id),
            'image_url': new_image.file_path,
            'sequential_number': new_image.get_sequential_number()
        })

    except Exception as e:
        logger.error(f"❌ Creative upscale error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
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

            # Session 487: Apply creator watermark before saving
            # Session 800: Now returns Cloudinary URL in production
            saved_path = save_watermarked_image(
                image_bytes=response.content,
                filename=filepath,
                user=request.user,
                generation_params={'operation': 'recolor', 'object': prompt, 'color': color}
            )
            # Session 800: saved_path may be Cloudinary URL or local path
            image_url = saved_path if saved_path.startswith('http') else default_storage.url(saved_path)

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


@login_required
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def recolor_image_view(request):
    """
    Recolor specific objects/areas in an image.
    Accepts JSON: {image_id: uuid, select_prompt: str, color: str (optional), project_id: uuid (optional)}
    """
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        select_prompt = data.get('select_prompt', 'entire image')
        color = data.get('color', 'vibrant colors')
        project_id = data.get('project_id')

        if not image_id:
            return JsonResponse({'success': False, 'error': 'image_id required'}, status=400)

        # Get the image from history
        from content.models import ImageHistory, CreativeProject
        try:
            image = ImageHistory.objects.get(id=image_id, user=request.user)
        except ImageHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        seq_num = image.get_sequential_number()
        logger.info(f"🎨 Recoloring '{select_prompt}' to '{color}' in image {image_id} (sequential #{seq_num})")

        # Get image data (handle both data URIs and file paths)
        if image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return JsonResponse({'success': False, 'error': 'Stability AI API key not configured'}, status=500)

        # Call Stability AI search-and-recolor API
        url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"

        files = {'image': image_data}
        data_params = {
            'prompt': f'{select_prompt}, {color}',
            'select_prompt': select_prompt,
            'output_format': 'png'
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI search-and-recolor failed: {api_response.text}")
            return JsonResponse({'success': False, 'error': f'Recolor failed: {api_response.text}'}, status=500)

        # Save the result image
        result_image_data = api_response.content
        image_base64 = base64.b64encode(result_image_data).decode('utf-8')

        # Create new image history entry
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass

        new_image = ImageHistory.objects.create(
            user=request.user,
            prompt=f"Recolored '{select_prompt}' to '{color}' from image #{seq_num}",
            file_path=f"data:image/png;base64,{image_base64}",
            model_used="stability-search-recolor",
            project=project
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=new_image,
                project=project,
                contribution_type='editing',
                task_description="Edited image using image-editing-agent",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {{ new_image.id }}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            logger.error(f"❌ Failed to create agent contribution: {e}")

        logger.info(f"✅ Recolor successful: {new_image.id}")

        return JsonResponse({
            'success': True,
            'image_id': str(new_image.id),
            'image_url': new_image.file_path,
            'sequential_number': new_image.get_sequential_number()
        })

    except Exception as e:
        logger.error(f"❌ Recolor error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# SESSION 148: PROJECT EXPORT ENDPOINTS
# ============================================================================


@csrf_exempt
@api_view(['POST'])
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
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

            # Session 487: Apply creator watermark before saving
            # Session 800: Now returns Cloudinary URL in production
            saved_path = save_watermarked_image(
                image_bytes=response.content,
                filename=filepath,
                user=request.user,
                generation_params={'operation': 'remove_background'}
            )
            # Session 800: saved_path may be Cloudinary URL or local path
            image_url = saved_path if saved_path.startswith('http') else default_storage.url(saved_path)

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


@login_required
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def remove_background_view(request):
    """
    Remove background from an existing image from history using its ID.
    Accepts JSON: {image_id: uuid, project_id: uuid (optional)}
    """
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        project_id = data.get('project_id')

        if not image_id:
            return JsonResponse({'success': False, 'error': 'image_id required'}, status=400)

        # Get the image from history
        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=request.user)
        except ImageHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        seq_num = image.get_sequential_number()
        logger.info(f"🎭 Removing background from image {image_id} (sequential #{seq_num})")

        # Get image data (handle both data URIs and file paths)
        if image.file_path.startswith('data:'):
            # Data URI - extract base64 data
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            # File path - read from storage
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Call Stability AI remove-background API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return JsonResponse({'success': False, 'error': 'Stability AI API key not configured'}, status=500)

        url = "https://api.stability.ai/v2beta/stable-image/edit/remove-background"
        files = {"image": image_data}
        data_params = {"output_format": "png"}

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI remove-background failed: {api_response.text}")
            return JsonResponse({'success': False, 'error': f'Remove background failed: {api_response.text}'}, status=500)

        # Save the result image to file (NOT as data URI!)
        result_image_data = api_response.content

        # Generate unique filename and save to disk
        filename = f'no_bg_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', request.user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(result_image_data))
        image_url = default_storage.url(saved_path)

        logger.info(f"✅ Saved background-removed image: {saved_path}")

        # Create new image history entry
        from content.models import CreativeProject
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass

        new_image = ImageHistory.objects.create(
            user=request.user,
            prompt=f"Background removed from image #{seq_num}",
            file_path=saved_path,  # Save FILE PATH, not data URI!
            filename=filename,
            model_used="stability-remove-bg",
            project=project
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=new_image,
                project=project,
                contribution_type='editing',
                task_description="Edited image using image-editing-agent",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {{ new_image.id }}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            logger.error(f"❌ Failed to create agent contribution: {e}")

        logger.info(f"✅ Background removed successfully: {new_image.id}")

        return JsonResponse({
            'success': True,
            'image_id': str(new_image.id),
            'image_url': new_image.file_path,
            'sequential_number': new_image.get_sequential_number()
        })

    except Exception as e:
        logger.error(f"❌ Remove background error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
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
                        # Session 487: Apply creator watermark before saving
                        # Session 800: Now returns Cloudinary URL in production
                        saved_path = save_watermarked_image(
                            image_bytes=result_response.content,
                            filename=filepath,
                            user=request.user,
                            generation_params={'operation': 'upscale', 'method': 'creative'}
                        )
                        # Session 800: saved_path may be Cloudinary URL or local path
                        image_url = saved_path if saved_path.startswith('http') else default_storage.url(saved_path)

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

                # Session 487: Apply creator watermark before saving
                # Session 800: Now returns Cloudinary URL in production
                saved_path = save_watermarked_image(
                    image_bytes=response.content,
                    filename=filepath,
                    user=request.user,
                    generation_params={'operation': 'upscale', 'method': method}
                )
                # Session 800: saved_path may be Cloudinary URL or local path
                image_url = saved_path if saved_path.startswith('http') else default_storage.url(saved_path)

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


@login_required
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def upscale_image_view(request):
    """
    Upscale an existing image from history using its ID.
    Accepts JSON: {image_id: uuid, project_id: uuid (optional)}
    """
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        project_id = data.get('project_id')

        if not image_id:
            return JsonResponse({'success': False, 'error': 'image_id required'}, status=400)

        # Get the image from history
        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=request.user)
        except ImageHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        seq_num = image.get_sequential_number()
        logger.info(f"📈 Upscaling image {image_id} (sequential #{seq_num})")

        # Get image data (handle both data URIs and file paths)
        if image.file_path.startswith('data:'):
            # Data URI - extract base64 data
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            # File path - read from storage
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Call Stability AI upscale API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return JsonResponse({'success': False, 'error': 'Stability AI API key not configured'}, status=500)

        url = "https://api.stability.ai/v2beta/stable-image/upscale/conservative"
        files = {"image": image_data}
        data_params = {
            "prompt": "high quality upscale",  # Required by Stability AI API
            "output_format": "png"
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI upscale failed: {api_response.text}")
            return JsonResponse({'success': False, 'error': f'Upscale failed: {api_response.text}'}, status=500)

        # Save the upscaled image to file (NOT as data URI!)
        upscaled_image_data = api_response.content

        # Generate unique filename and save to disk
        filename = f'upscaled_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', request.user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(upscaled_image_data))
        image_url = default_storage.url(saved_path)

        logger.info(f"✅ Saved upscaled image: {saved_path}")

        # Create new image history entry
        from content.models import CreativeProject
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass

        new_image = ImageHistory.objects.create(
            user=request.user,
            prompt=f"Upscaled from image #{seq_num}",
            file_path=saved_path,  # Save FILE PATH, not data URI!
            filename=filename,
            model_used="stability-upscale-4x",
            project=project
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=new_image,
                project=project,
                contribution_type='editing',
                task_description="Edited image using image-generation-agent",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {{ new_image.id }}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            logger.error(f"❌ Failed to create agent contribution: {e}")

        logger.info(f"✅ Image upscaled successfully: {new_image.id}")

        return JsonResponse({
            'success': True,
            'image_id': str(new_image.id),
            'image_url': new_image.file_path,
            'sequential_number': new_image.get_sequential_number()
        })

    except Exception as e:
        logger.error(f"❌ Upscale error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

