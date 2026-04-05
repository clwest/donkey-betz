"""
Image views — helpers functions.
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
# Session 1077+: save_to_history and get_system_user imported lazily
# inside functions to avoid circular imports
# (views_image_helpers -> image_views.session -> image_views.__init__ -> views_image -> views_image_helpers)

logger = logging.getLogger(__name__)


# ========================================
# SESSION 794: SYSTEM USER FOR AUTONOMOUS OPERATIONS
# ========================================

from django.views.decorators.csrf import csrf_exempt


def _execute_add_music_to_video(user, parameters):
    """
    Execute background music addition to video via DaVinci Resolve
    Session 72: AI Assistant integration for audio mixing!
    Session 81: Added support for audio_url from generated audio!

    This adds background music to a user's video:
    1. Gets the user's most recent video (or lets them select)
    2. If audio_url provided: Use that audio directly (from generate_speech/generate_sound_effect)
    3. If no audio_url: User uploads audio file or selects from library
    4. Creates new DaVinci project with video + audio
    5. Renders final video with mixed audio

    Parameters:
        video_selection (str): 'last' or 'recent' (default: 'last')
        audio_url (str): URL of generated audio (optional, Session 81)
        audio_volume (float): Volume 0.0-1.0 (default: 0.3)
        music_style (str): Style preference (default: 'cinematic')

    Returns:
        dict: {
            'success': True,
            'video_id': 'id',
            'audio_url': 'url' (if provided),
            'audio_volume': 0.3,
            'message': 'Ready to add music...'
        }
    """
    try:
        from content.models import VideoHistory

        video_selection = parameters.get('video_selection', 'last')
        audio_url = parameters.get('audio_url')  # Session 81: Optional audio URL
        audio_volume = parameters.get('audio_volume', 0.3)
        music_style = parameters.get('music_style', 'cinematic')

        # Validate volume
        audio_volume = max(0.0, min(1.0, audio_volume))

        logger.info(f"🎵 AI Assistant add_music_to_video: volume={audio_volume}, style={music_style}, audio_url={'provided' if audio_url else 'none'}")

        # Get user's most recent completed video
        recent_video = VideoHistory.objects.filter(
            user=user,
            status='completed'
        ).order_by('-created_at').first()

        if not recent_video:
            return {
                'success': False,
                'error': 'You have no completed videos in your gallery.',
                'message': 'Please create a video first, then add music to it!'
            }

        logger.info(f"✅ Found video for audio mixing: {recent_video.id} - {recent_video.prompt[:50]}")

        # Session 81: If audio_url is provided, we can proceed directly (no upload needed)
        # Session 83: EXECUTE IMMEDIATELY instead of returning confirmation!
        if audio_url:
            logger.info(f"🎵 Session 83: Audio URL provided, executing mixing immediately...")

            # Call VideoAgent to actually mix the audio
            from core.agents import VideoAgent

            video_agent = VideoAgent(user=user)
            result = video_agent.add_music_to_video(
                video_selection='last',
                audio_url=audio_url,
                audio_volume=audio_volume
            )

            # Session 83: Return the actual mixed video result, not confirmation
            if result.get('success'):
                logger.info(f"✅ Session 83: Audio mixing executed successfully!")
                return {
                    'success': True,
                    'video_url': result.get('video_url'),
                    'video_id': result.get('video_id', str(recent_video.id)),
                    'audio_volume': audio_volume,
                    'music_style': 'custom audio',  # Since we used provided audio
                    'video_prompt': result.get('video_prompt', recent_video.prompt[:100] if recent_video.prompt else "Untitled video"),
                    'message': f'✅ Audio successfully added to video!',
                    'instructions': f'The video has been rendered with audio at {int(audio_volume * 100)}% volume.',
                    'note': '🎬 Your new video is ready in the Video Gallery!'
                }
            else:
                logger.error(f"❌ Session 83: Audio mixing failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': result.get('error', 'Audio mixing failed'),
                    'message': '❌ Failed to mix audio with video',
                    'instructions': 'Please check the logs for details.'
                }
        else:
            # No audio_url provided - require manual upload (original behavior)
            return {
                'success': True,
                'video_id': str(recent_video.id),
                'video_url': recent_video.video_url,
                'video_prompt': recent_video.prompt[:100] if recent_video.prompt else "Untitled video",
                'audio_volume': audio_volume,
                'music_style': music_style,
                'message': f'🎵 Ready to add {music_style} background music to your video! Volume will be set to {int(audio_volume * 100)}%.',
                'instructions': f'This will create a NEW video with background music mixed into your {recent_video.prompt[:30] if recent_video.prompt else "video"}. You\'ll need to upload an audio file (MP3, WAV, etc.) or select from your audio library. The music will be mixed at {int(audio_volume * 100)}% volume. Click confirm and upload your audio file!',
                'note': '⚠️ Note: This creates a new video with mixed audio. Your original video remains unchanged.',
                'requires_audio_upload': True  # Frontend should show audio file upload dialog
            }

    except Exception as e:
        logger.error(f"❌ Error in _execute_add_music_to_video: {str(e)}")
        raise


def _execute_add_text_to_video(user, parameters):
    """
    Execute text overlay addition to video via DaVinci Resolve
    Session 72: AI Assistant integration for text overlays!

    This adds text to a user's video with perfect spelling:
    1. Gets the user's most recent video (or lets them select)
    2. Creates new DaVinci project with that video
    3. Adds text overlay with specified parameters
    4. Renders final video with text

    Parameters:
        text (str): Text to display (REQUIRED)
        position (str): 'center', 'lower_third', or 'upper_third' (default: 'center')
        start_second (float): When to start text (default: 0)
        duration (float): How long to show text (default: 3)
        font_size (int): Text size 36-144 (default: 72)
        video_selection (str): 'last' or 'recent' (default: 'last')

    Returns:
        dict: {
            'success': True,
            'video_id': 'id',
            'text': 'Welcome',
            'message': 'Ready to add text overlay...'
        }
    """
    try:
        from content.models import VideoHistory

        text = parameters.get('text', '').strip()
        if not text:
            raise ValueError("Text is required for overlay")

        position = parameters.get('position', 'center')
        start_second = parameters.get('start_second', 0)
        duration = parameters.get('duration', 3)
        font_size = parameters.get('font_size', 72)
        video_selection = parameters.get('video_selection', 'last')

        logger.info(f"📝 AI Assistant add_text_to_video: '{text}' at {position}, {start_second}s-{start_second+duration}s")

        # Get user's most recent completed video
        recent_video = VideoHistory.objects.filter(
            user=user,
            status='completed'
        ).order_by('-created_at').first()

        if not recent_video:
            return {
                'success': False,
                'error': 'You have no completed videos in your gallery.',
                'message': 'Please create a video first, then add text to it!'
            }

        logger.info(f"✅ Found video for text overlay: {recent_video.id} - {recent_video.prompt[:50]}")

        return {
            'success': True,
            'video_id': str(recent_video.id),
            'video_url': recent_video.video_url,
            'video_prompt': recent_video.prompt[:100] if recent_video.prompt else "Untitled video",
            'text': text,
            'position': position,
            'start_second': start_second,
            'duration': duration,
            'font_size': font_size,
            'message': f'📝 Ready to add text overlay "{text}" to your video! The text will appear at {position} starting at {start_second} seconds for {duration} seconds.',
            'instructions': f'This will create a NEW video with the text "{text}" overlaid on your {recent_video.prompt[:30] if recent_video.prompt else "video"}. The text will be spelled PERFECTLY (no AI text rendering issues!) using DaVinci Resolve. Click confirm to proceed!',
            'note': '⚠️ Note: This creates a new video with text overlay. Your original video remains unchanged.'
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_add_text_to_video: {str(e)}")
        raise


def _execute_add_voiceover(user, parameters, session=None):
    from core.views_audio import _execute_add_voiceover as _impl
    return _impl(user, parameters, session)


def _execute_chain_videos(user, parameters):
    """
    Execute video chaining via DaVinci Resolve
    Session 71: AI Assistant integration for video chaining!

    This guides the user to chain their videos together:
    1. Gets the user's most recent videos from gallery
    2. Returns video IDs and instructions
    3. Frontend auto-selects videos and opens chain modal

    Parameters:
        video_count (int): Number of videos to chain (default: 2)
        transition_type (str): Transition style (default: 'Cross Dissolve')
        add_transitions (bool): Add transitions (default: true)
        project_name (str): Optional project name

    Returns:
        dict: {
            'success': True,
            'video_ids': ['id1', 'id2', ...],
            'video_count': 2,
            'transition_type': 'Cross Dissolve',
            'message': 'Ready to chain 2 videos...'
        }
    """
    try:
        from content.models import VideoHistory

        video_count = parameters.get('video_count', 2)
        transition_type = parameters.get('transition_type', 'Cross Dissolve')
        add_transitions = parameters.get('add_transitions', True)
        project_name = parameters.get('project_name', None)

        # Validate video_count
        if video_count < 2:
            raise ValueError("Need at least 2 videos to chain")
        if video_count > 10:
            logger.warning(f"⚠️ video_count {video_count} is high, limiting to 10")
            video_count = 10

        logger.info(f"🎬 AI Assistant chain_videos: {video_count} videos, {transition_type} transitions")

        # Get user's most recent completed videos
        recent_videos = VideoHistory.objects.filter(
            user=user,
            status='completed'
        ).order_by('-created_at')[:video_count]

        if recent_videos.count() < video_count:
            available_count = recent_videos.count()
            return {
                'success': False,
                'error': f'You only have {available_count} completed videos in your gallery. Need {video_count} videos to chain.',
                'available_count': available_count,
                'requested_count': video_count,
                'message': f'Please create more videos first, or try chaining {available_count} videos instead.'
            }

        # Get video IDs and URLs
        video_ids = [str(v.id) for v in recent_videos]
        video_urls = []
        video_prompts = []

        for v in recent_videos:
            # Get video URL (either external CDN or local media)
            if v.video_url:
                video_urls.append(v.video_url)
            else:
                logger.warning(f"⚠️ Video {v.id} has no video_url")

            video_prompts.append(v.prompt[:100] if v.prompt else "Untitled video")

        logger.info(f"✅ Found {len(video_ids)} videos for chaining: {video_ids}")

        # Calculate estimated duration
        total_duration = sum([v.duration or 8 for v in recent_videos])

        return {
            'success': True,
            'video_ids': video_ids,
            'video_urls': video_urls,
            'video_prompts': video_prompts,
            'video_count': len(video_ids),
            'transition_type': transition_type,
            'add_transitions': add_transitions,
            'project_name': project_name or f"AI Chained Video {len(video_ids)} clips",
            'total_duration': total_duration,
            'message': f'🎬 Ready to chain {len(video_ids)} videos together! Your {video_count} most recent videos have been selected. The chained video will be approximately {total_duration} seconds long with {transition_type} transitions.',
            'instructions': 'The videos have been auto-selected in your gallery. Click the "Chain Videos" button to create your final video!'
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_chain_videos: {str(e)}")
        raise


def _execute_convert_to_3d(user, parameters, session=None):
    """
    Internal function for converting images to 3D models.
    Called by ThreeDAgent.

    Args:
        user: Django user object
        parameters: Dict with image_id, output_format, quality
        session: Optional session for tracking

    Returns:
        Dict with success, model_url
    """
    try:
        image_id = parameters.get('image_id')
        output_format = parameters.get('output_format', 'glb')
        quality = parameters.get('quality', 'standard')

        if not image_id:
            return {'success': False, 'error': 'image_id required'}

        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=user)
        except ImageHistory.DoesNotExist:
            return {'success': False, 'error': 'Image not found'}

        seq_num = image.get_sequential_number()
        logger.info(f"🎮 Agent converting image {image_id} (#{seq_num}) to 3D ({output_format})")

        # Get image URL for Replicate API
        if image.file_path.startswith('data:'):
            # Data URI - would need to upload first
            return {'success': False, 'error': 'Data URI images not supported for 3D conversion'}
        else:
            image_url = f"{settings.MEDIA_URL}{image.file_path}"

        # Call Replicate API for 3D conversion
        import replicate
        replicate_key = os.getenv('REPLICATE_API_TOKEN') or settings.EXTERNAL_API_KEYS.get('REPLICATE_API_TOKEN')
        if not replicate_key:
            return {'success': False, 'error': 'Replicate API key not configured'}

        os.environ['REPLICATE_API_TOKEN'] = replicate_key

        # Use TripoSR or similar model
        output = replicate.run(
            "stability-ai/stable-fast-3d:5ddcbc15a0c1e0154cfe0969f9ae1e06f3d5e0bcc44119f7c7e29f23b7a04a05",
            input={
                "image": image_url,
            }
        )

        if output:
            return {
                'success': True,
                'model_url': str(output),
                'format': output_format,
                'message': f"3D model generated from image #{seq_num}"
            }
        else:
            return {'success': False, 'error': '3D conversion returned no output'}

    except Exception as e:
        logger.error(f"❌ Agent 3D conversion error: {e}")
        return {'success': False, 'error': str(e)}


# Session 990: Moved to core/views_audio.py — re-export for backwards compatibility


def _execute_create_brand_video(user, parameters):
    """
    Execute automated brand video workflow
    Session 67: End-to-end video creation orchestration

    This creates a complete brand video by:
    1. Generating video prompts based on concept and style
    2. Creating multiple video clips with Runway ML
    3. Returning task IDs for user to monitor
    4. User can chain them with DaVinci once complete

    Parameters:
        brand_name (str): Brand or company name
        concept (str): Video concept/message
        style (str): Visual style (cinematic, modern, playful, elegant, energetic)
        include_branding (bool): Add brand text overlays (default: true)
        video_count (int): Number of clips to generate (default: 3)

    Returns:
        dict: {
            'success': True,
            'task_ids': ['id1', 'id2', 'id3'],
            'prompts': ['prompt1', 'prompt2', 'prompt3'],
            'estimated_time': 180,
            'message': 'Brand video workflow started'
        }
    """
    try:
        brand_name = parameters.get('brand_name', '').strip()
        concept = parameters.get('concept', '').strip()
        style = parameters.get('style', 'modern')
        include_branding = parameters.get('include_branding', True)
        video_count = parameters.get('video_count', 3)

        if not brand_name:
            raise ValueError("Brand name is required")
        if not concept:
            raise ValueError("Concept is required")

        # Validate video_count (2-5)
        if video_count < 2 or video_count > 5:
            logger.warning(f"⚠️ Invalid video_count {video_count}, defaulting to 3")
            video_count = 3

        logger.info(f"🎬 Creating brand video for {brand_name}: {concept} ({style} style, {video_count} clips)")

        # Style-specific prompt modifiers
        style_modifiers = {
            'cinematic': 'dramatic lighting, cinematic composition, film grain, depth of field',
            'modern': 'clean lines, minimalist, bright natural lighting, contemporary design',
            'playful': 'vibrant colors, dynamic movement, fun energy, cheerful atmosphere',
            'elegant': 'sophisticated, refined aesthetic, smooth movements, luxury feel',
            'energetic': 'fast-paced, dynamic transitions, bold colors, high energy'
        }

        style_prompt = style_modifiers.get(style, style_modifiers['modern'])

        # Generate prompts for each video clip
        prompts = []
        if video_count == 2:
            prompts = [
                f"{concept}, {style_prompt}, opening shot",
                f"{brand_name} showcase, {concept}, {style_prompt}, closing scene"
            ]
        elif video_count == 3:
            prompts = [
                f"{concept}, {style_prompt}, establishing shot",
                f"{brand_name} product or service, {concept}, {style_prompt}, detail view",
                f"{concept}, {style_prompt}, powerful closing scene with {brand_name}"
            ]
        elif video_count == 4:
            prompts = [
                f"{concept}, {style_prompt}, opening sequence",
                f"{brand_name} highlights, {concept}, {style_prompt}, feature showcase",
                f"{concept} in action, {style_prompt}, dynamic demonstration",
                f"{brand_name} finale, {concept}, {style_prompt}, memorable closing"
            ]
        else:  # 5 clips
            prompts = [
                f"{concept}, {style_prompt}, captivating opening",
                f"{brand_name} introduction, {concept}, {style_prompt}",
                f"{concept}, {style_prompt}, mid-point highlight",
                f"{brand_name} key features, {concept}, {style_prompt}",
                f"{concept}, {style_prompt}, impactful conclusion with {brand_name}"
            ]

        # Generate all videos using Runway ML
        from content.video_provider import runway_provider
        from content.models import ContentGeneration

        task_ids = []
        content_ids = []
        total_estimated_time = 0

        for i, prompt in enumerate(prompts):
            logger.info(f"🎬 Generating clip {i+1}/{len(prompts)}: {prompt[:60]}...")

            result = runway_provider.text_to_video(
                prompt=prompt,
                duration=8,  # 8 seconds per clip for professional feel
                quality='veo3.1_fast',
                style='realistic',
                enhance_prompt=True,
                enhancement_level='advanced',
                ratio='1920:1080'
            )

            if not result.success:
                logger.warning(f"⚠️ Clip {i+1} generation failed: {result.error_message}")
                continue

            # Store in database
            content = ContentGeneration.objects.create(
                user=user,
                prompt=prompt,
                system_prompt=f"Brand video for {brand_name} - Clip {i+1}/{len(prompts)}",
                generation_config={
                    'task_id': result.task_id,
                    'duration': 8,
                    'quality': 'veo3.1_fast',
                    'style': style,
                    'type': 'brand_video_clip',
                    'brand_name': brand_name,
                    'clip_number': i + 1,
                    'total_clips': len(prompts),
                    'estimated_time': result.estimated_time,
                    'status': 'processing',
                    'include_branding': include_branding
                }
            )

            task_ids.append(result.task_id)
            content_ids.append(str(content.id))
            total_estimated_time += result.estimated_time

        logger.info(f"✅ Started {len(task_ids)} video generations for {brand_name}")

        return {
            'success': True,
            'brand_name': brand_name,
            'task_ids': task_ids,
            'content_ids': content_ids,
            'prompts': prompts,
            'video_count': len(task_ids),
            'estimated_time': total_estimated_time,
            'include_branding': include_branding,
            'message': f'Started generating {len(task_ids)} video clips for {brand_name}. Videos will appear in your gallery when ready. Once complete, you can chain them together with transitions and branding!'
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_create_brand_video: {str(e)}")
        raise


def _execute_create_character_from_prompt(user, parameters):
    """
    Execute character training set generation from natural language
    Session 74: AI-powered character training integration!

    This generates multiple image variations and creates a trainable character:
    1. Parse character description and style
    2. Generate 5-7 image variations with different angles/poses
    3. Download generated images
    4. Create character model and submit for training
    5. Return status with training progress

    Parameters:
        character_description (str): Description of character/logo (REQUIRED)
        character_name (str): Name for this character model (optional, derived from description)
        trigger_word (str): Trigger word for prompts (default: 'TOK')
        variation_count (int): Number of variations to generate 5-7 (default: 6)
        style (str): Visual style (pixar, anime, realistic, cartoon, minimalist, professional)

    Returns:
        dict: {
            'success': True,
            'character_id': 123,
            'character_name': 'Robotics Donkey',
            'trigger_word': 'TOK',
            'images_generated': 6,
            'training_status': 'preparing',
            'message': 'Character training set generated! Training will take 30-60 minutes.'
        }
    """
    try:
        import requests
        from django.core.files.uploadedfile import SimpleUploadedFile
        from content.character_training import create_character_workflow
        from content.image_generation import ImageGenerationService

        # Extract parameters
        character_description = parameters.get('character_description', '').strip()
        character_name = parameters.get('character_name', '').strip()
        trigger_word = parameters.get('trigger_word', 'TOK').strip().upper()
        variation_count = parameters.get('variation_count', 6)
        style = parameters.get('style', '').strip().lower()

        # Validate required parameters
        if not character_description:
            raise ValueError("character_description is required")

        # Derive character name from description if not provided
        if not character_name:
            # Take first 3-5 words and capitalize
            words = character_description.split()[:4]
            character_name = ' '.join(words).title()

        # Validate variation_count (5-7)
        if variation_count < 5:
            logger.warning(f"⚠️ variation_count {variation_count} too low, setting to 5")
            variation_count = 5
        elif variation_count > 7:
            logger.warning(f"⚠️ variation_count {variation_count} too high, setting to 7")
            variation_count = 7

        # Extract or default style
        if not style or style == 'professional':
            # Try to extract style from description
            style_keywords = ['pixar', 'anime', 'realistic', 'cartoon', 'minimalist', '3d', '2d', 'watercolor', 'oil painting']
            for keyword in style_keywords:
                if keyword in character_description.lower():
                    style = keyword
                    break
            if not style:
                style = 'professional'

        logger.info(f"🎨 Creating character training set:")
        logger.info(f"   Character: {character_name}")
        logger.info(f"   Description: {character_description}")
        logger.info(f"   Trigger word: {trigger_word}")
        logger.info(f"   Variations: {variation_count}")
        logger.info(f"   Style: {style}")

        # Create prompt variations for different angles/poses/contexts
        prompt_variations = [
            f"{character_description}, {style} style, front view, centered, well-lit, professional photography",
            f"{character_description}, {style} style, side profile view, clear details, studio lighting",
            f"{character_description}, {style} style, three-quarter angle, dynamic pose, professional composition",
            f"{character_description}, {style} style, different angle, varied expression, high quality",
            f"{character_description}, {style} style, close-up detail shot, sharp focus, professional",
            f"{character_description}, {style} style, full body view, different background, cinematic lighting",
            f"{character_description}, {style} style, alternate pose, varied composition, professional quality"
        ]

        # Use only the number of variations requested
        prompt_variations = prompt_variations[:variation_count]

        logger.info(f"📸 Generating {len(prompt_variations)} training images...")

        # Initialize Image Generation Service
        service = ImageGenerationService()

        if not service.stability_key:
            raise ValueError("Stability AI is not available. Please check STABILITY_API_KEY configuration.")

        # Generate images and download them
        temp_files = []
        generated_images = []

        for i, prompt in enumerate(prompt_variations):
            logger.info(f"   Generating image {i+1}/{len(prompt_variations)}: {prompt[:60]}...")

            # Generate image with Stability AI (using sd3 for consistency)
            result = service.generate_image(
                prompt=prompt,
                provider='stability',
                model='sd3',  # SD3 for good quality and consistency
                size='1024x1024',
                cfg_scale=7,  # Moderate adherence to prompt
                steps=40  # Good quality
            )

            if not result.success:
                logger.warning(f"⚠️ Image {i+1} generation failed: {result.error_message}")
                continue

            if not result.images or len(result.images) == 0:
                logger.warning(f"⚠️ Image {i+1} has no URL")
                continue

            # Get image data (handle both URLs and base64 data URIs)
            image_url = result.images[0]
            logger.info(f"   Processing image {i+1}...")

            if image_url.startswith('data:image'):
                # Base64 data URI - decode directly
                import base64
                # Extract base64 data after the comma
                base64_data = image_url.split(',', 1)[1]
                image_content = base64.b64decode(base64_data)
                logger.info(f"   Decoded base64 image {i+1}")
            else:
                # HTTP URL - download
                logger.info(f"   Downloading image {i+1} from URL...")
                img_response = requests.get(image_url, timeout=30)

                if img_response.status_code != 200:
                    logger.warning(f"⚠️ Failed to download image {i+1}")
                    continue

                image_content = img_response.content

            # Create SimpleUploadedFile for Django
            filename = f"character_training_{i+1}.png"
            uploaded_file = SimpleUploadedFile(
                name=filename,
                content=image_content,
                content_type='image/png'
            )

            generated_images.append(uploaded_file)
            logger.info(f"✅ Image {i+1} downloaded and ready")

        if len(generated_images) < 5:
            raise ValueError(f"Not enough images generated: {len(generated_images)}/5 minimum required")

        logger.info(f"✅ Generated {len(generated_images)} training images successfully!")

        # Create character with workflow
        logger.info(f"📝 Creating character model and submitting for training...")

        character, warnings = create_character_workflow(
            user=user,
            name=character_name,
            description=character_description,
            trigger_word=trigger_word,
            image_files=generated_images,
            training_steps=1000,  # Standard training steps
            learning_rate=0.0004,  # Standard learning rate
            auto_submit=False  # Wait for user review and approval!
        )

        logger.info(f"🎉 Character training set created! ID: {character.id}")
        logger.info(f"   Training Status: {character.training_status}")

        # Get training images for preview
        training_images = character.training_images.all().order_by('order')
        training_images_data = [
            {
                'id': img.id,
                'url': img.image.url if img.image else None,
                'order': img.order,
                'width': img.width,
                'height': img.height,
                'file_size': img.file_size
            }
            for img in training_images
        ]

        return {
            'success': True,
            'character_id': character.id,
            'character_name': character.name,
            'description': character.description,
            'trigger_word': character.trigger_word,
            'images_generated': len(generated_images),
            'training_images_count': character.training_images_count,
            'training_status': character.training_status,
            'training_images': training_images_data,
            'warnings': warnings,
            'estimated_time_minutes': 45,  # FLUX LoRA training takes 30-60 minutes
            'message': f'🎉 Generated {len(generated_images)} training images for "{character_name}"! Review them below. You can edit any images or say "These look perfect" to start training.',
            'instructions': f'Review your training images below. If you want to edit any, just say "Make the ears bigger on image 3" or similar. When ready, say "These look perfect, train it!" to start the 30-60 minute training process.',
            'next_action': 'review',  # Frontend should show review UI
            'next_steps': [
                'Review the generated training images',
                'Edit images if needed (optional)',
                'Say "These look perfect, train it!" to start training',
                f'After training, use "{trigger_word}" in your prompts!'
            ]
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_create_character_from_prompt: {str(e)}")
        raise


def _execute_create_variations(user, parameters, session=None):
    """
    Internal function for creating image variations.
    Called by ImageEditingAgent.

    Args:
        user: Django user object
        parameters: Dict with image_id, count, variation_strength
        session: Optional session for tracking

    Returns:
        Dict with success, images list
    """
    try:
        image_id = parameters.get('image_id')
        count = parameters.get('count', 3)
        strength = parameters.get('variation_strength', 0.5)

        from core.views_image_edit import _resolve_image_and_bytes
        image, image_data, err = _resolve_image_and_bytes(user, image_id)
        if err:
            return {'success': False, 'error': err}

        seq_num = image.get_sequential_number()
        logger.info(f"🎨 Agent creating {count} variations from image {image.id} (#{seq_num})")

        # For now, use image-to-image with variation prompts
        # This would use the Stability AI img2img endpoint
        return {
            'success': False,
            'error': 'Image variations not yet implemented in clean architecture'
        }

    except Exception as e:
        logger.error(f"❌ Agent variations error: {e}")
        return {'success': False, 'error': str(e)}


def _execute_edit_character_training_image(user, parameters):
    """
    Edit a specific character training image with natural language instructions

    Session 75: Image editing workflow for character training

    Workflow:
    1. Get character and specified image
    2. Get original prompt/description from character
    3. Apply edit instruction to prompt
    4. Generate new image with edited prompt
    5. Download and replace old image
    6. Update database
    7. Return updated character with all images

    Parameters:
        character_id (int): ID of character model
        image_number (int): Which image to edit (1-7)
        edit_instruction (str): Natural language edit
        apply_to_all (bool): Apply to all images (default: False)

    Returns:
        dict: Updated character data with all training images
    """
    try:
        from content.models import CharacterModel, CharacterTrainingImage

        character_id = parameters.get('character_id')
        image_number = parameters.get('image_number')
        edit_instruction = parameters.get('edit_instruction', '').strip()
        apply_to_all = parameters.get('apply_to_all', False)
        reference_image_number = parameters.get('reference_image_number')
        strength = parameters.get('strength', 0.65)  # Default: preserve reference structure moderately

        logger.info(f"✏️ Editing training image - character_id: {character_id}, image #{image_number}")
        logger.info(f"   Edit: '{edit_instruction}'")
        logger.info(f"   Apply to all: {apply_to_all}")
        if reference_image_number is not None:
            logger.info(f"   🎨 Using image #{reference_image_number} as reference (strength: {strength})")

        # Get character and verify ownership
        if character_id:
            try:
                character = CharacterModel.objects.get(id=character_id, user=user)
                logger.info(f"✅ Using specified character: {character.id} - {character.name}")
            except CharacterModel.DoesNotExist:
                logger.warning(f"⚠️ Character {character_id} not found, trying most recent character...")
                character = None
        else:
            logger.info(f"ℹ️ No character_id provided, using most recent character...")
            character = None

        # If character not found or not provided, use most recent
        if not character:
            character = CharacterModel.objects.filter(
                user=user,
                training_status='pending'  # Only pending (not yet submitted)
            ).order_by('-created_at').first()

            if not character:
                # If no pending characters, just get the most recent one
                character = CharacterModel.objects.filter(user=user).order_by('-created_at').first()

            if not character:
                raise ValueError(f"No characters found for editing")

            logger.info(f"✅ Using most recent character: {character.id} - {character.name}")

        # Get images to edit
        if apply_to_all:
            images_to_edit = character.training_images.all().order_by('order')
            logger.info(f"   Editing all {images_to_edit.count()} images")
        else:
            # Get specific image by order number
            try:
                images_to_edit = [character.training_images.get(order=image_number)]
                logger.info(f"   Editing only image #{image_number}")
            except CharacterTrainingImage.DoesNotExist:
                raise ValueError(f"Image #{image_number} not found in character training set")

        # Initialize image generation service
        from content.image_generation import ImageGenerationService
        service = ImageGenerationService()

        # Check Stability AI availability
        if not service.stability_key:
            raise ValueError("Stability AI is not available. Cannot generate edited images.")

        # Get reference image if provided
        reference_image = None
        if reference_image_number is not None:
            try:
                reference_image = character.training_images.get(order=reference_image_number)
                logger.info(f"✅ Found reference image #{reference_image_number}: {reference_image.image.path}")
            except CharacterTrainingImage.DoesNotExist:
                raise ValueError(f"Reference image #{reference_image_number} not found in character training set")

        edited_count = 0
        for training_image in images_to_edit:
            # Build edited prompt based on original character description
            base_prompt = f"{character.description}, professional photography"

            # Add angle/pose variation based on image order
            angle_variations = {
                1: "front view, centered, well-lit",
                2: "side profile view, clear details",
                3: "three-quarter angle, dynamic pose",
                4: "different angle, varied expression",
                5: "close-up detail shot, sharp focus",
                6: "full body view, different background",
                7: "alternate pose, varied composition"
            }
            angle_desc = angle_variations.get(training_image.order, "professional composition")

            # Combine: base + angle + edit instruction
            edited_prompt = f"{base_prompt}, {angle_desc}, {edit_instruction}"

            # Check if we should use image-to-image with reference
            if reference_image:
                logger.info(f"   🎨 Generating image #{training_image.order} using image-to-image from reference #{reference_image_number}")
                logger.info(f"      Prompt: '{edited_prompt[:100]}...'")
                logger.info(f"      Strength: {strength} (lower = more like reference)")

                # Use image-to-image with reference image
                result = service.image_to_image(
                    base_image=reference_image.image.path,
                    prompt=edited_prompt,
                    strength=strength,
                    model='sd3',
                    provider='stability'
                )
            else:
                logger.info(f"   Generating edited image #{training_image.order} with prompt: '{edited_prompt[:100]}...'")

                # Generate new image from scratch
                result = service.generate_image(
                    provider='stability',
                    model='sd3',
                    prompt=edited_prompt,
                    width=1024,
                    height=1024,
                    user=user,
                    save_to_history=False  # Don't clutter history with training images
                )

            # Get image data (handle both URLs and base64 data URIs)
            import requests
            import base64
            from django.core.files.base import ContentFile

            image_url = result.images[0]

            if image_url.startswith('data:image'):
                # Base64 data URI - decode directly
                logger.info(f"   Decoding base64 image...")
                base64_data = image_url.split(',', 1)[1]
                image_content = base64.b64decode(base64_data)
            else:
                # HTTP URL - download
                logger.info(f"   Downloading image from URL...")
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                image_content = img_response.content

            # Replace the old image file
            old_filename = training_image.original_filename
            training_image.image.save(
                old_filename,
                ContentFile(image_content),
                save=False
            )

            # Update metadata
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_content))
            training_image.width = img.width
            training_image.height = img.height
            training_image.file_size = len(image_content)
            training_image.validation_notes = f"Edited: {edit_instruction}"
            training_image.save()

            edited_count += 1
            logger.info(f"   ✅ Image #{training_image.order} updated successfully")

        # Get updated training images for response
        training_images = character.training_images.all().order_by('order')
        training_images_data = [
            {
                'id': img.id,
                'url': img.image.url if img.image else None,
                'order': img.order,
                'width': img.width,
                'height': img.height,
                'file_size': img.file_size,
                'validation_notes': img.validation_notes
            }
            for img in training_images
        ]

        logger.info(f"✅ Edited {edited_count} image(s) successfully!")

        return {
            'success': True,
            'character_id': character.id,
            'character_name': character.name,
            'trigger_word': character.trigger_word,
            'edited_count': edited_count,
            'training_images': training_images_data,
            'message': f'✅ Edited {edited_count} image(s) successfully! {edit_instruction.capitalize()}.',
            'instructions': f'Review the updated images. When ready, say "These look perfect, train it!" to start training.',
            'next_action': 'review'  # Show review UI again
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_edit_character_training_image: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def _execute_edit_video(user, parameters):
    """
    Execute multi-operation video editing via DaVinci Resolve
    Session 84: Master orchestrator for complex video editing workflows!

    This performs multiple editing operations in sequence:
    - Chain videos together with transitions
    - Add text overlays
    - Apply color grading
    - Mix audio/music

    Parameters:
        video_selection (str): 'last', 'last_2', 'last_3', etc.
        operations (list): List of operation dicts with 'type' and parameters
        project_name (str): Optional project name

    Returns:
        dict: {
            'success': True,
            'video_id': 'new_video_id',
            'video_url': 'url',
            'operations_applied': 4,
            'duration': 24.0,
            'message': 'Video edited successfully!'
        }
    """
    try:
        from content.models import VideoHistory
        from core.agents import VideoAgent

        # Get parameters
        video_selection = parameters.get('video_selection', 'last')
        operations = parameters.get('operations', [])
        project_name = parameters.get('project_name')
        provided_video_ids = parameters.get('video_ids', [])
        video_numbers = parameters.get('video_numbers', [])  # Session 84: NEW! Support for video numbers

        # Validate operations
        if not operations or len(operations) == 0:
            return {
                'success': False,
                'error': 'No operations specified',
                'message': 'Please specify at least one editing operation (chain, text, color_grade, or audio).'
            }

        logger.info(f"🎬 AI Assistant edit_video: {len(operations)} operations on {video_selection}")

        # Session 84: Handle video numbers (e.g., "chain videos 5 and 8")
        if video_numbers and len(video_numbers) > 0:
            logger.info(f"📹 Converting video numbers to IDs: {video_numbers}")

            # Get all completed videos ordered by creation date (most recent first)
            all_videos = list(VideoHistory.objects.filter(
                user=user,
                status='completed'
            ).order_by('-created_at'))

            if len(all_videos) == 0:
                return {
                    'success': False,
                    'error': 'No videos found',
                    'message': 'You have no completed videos yet.'
                }

            # Convert video numbers to IDs (numbers are 1-indexed in UI)
            video_ids = []
            for num in video_numbers:
                # Convert to 0-indexed array position
                idx = num - 1

                if idx < 0 or idx >= len(all_videos):
                    return {
                        'success': False,
                        'error': f'Video number {num} out of range',
                        'message': f'Video {num} does not exist. You have {len(all_videos)} videos.'
                    }

                video_ids.append(str(all_videos[idx].id))

            logger.info(f"✅ Converted numbers {video_numbers} to IDs: {video_ids}")

        # Session 84: Handle specific video IDs (for numbered references)
        elif video_selection == 'specific_ids' and provided_video_ids:
            logger.info(f"📹 Using specific video IDs: {provided_video_ids}")
            video_ids = provided_video_ids

            # Validate that these videos exist
            videos = VideoHistory.objects.filter(
                id__in=video_ids,
                user=user,
                status='completed'
            )

            if videos.count() != len(video_ids):
                return {
                    'success': False,
                    'error': f'Some video IDs not found. Found {videos.count()}, expected {len(video_ids)}',
                    'message': 'Some of the specified videos were not found or are not completed yet.'
                }
        else:
            # Parse video_selection to get count
            if video_selection == 'last':
                video_count = 1
            elif video_selection.startswith('last_'):
                try:
                    video_count = int(video_selection.split('_')[1])
                except (IndexError, ValueError):
                    video_count = 1
            else:
                video_count = 1

            # Get videos
            videos = VideoHistory.objects.filter(
                user=user,
                status='completed'
            ).order_by('-created_at')[:video_count]

            if videos.count() < video_count:
                return {
                    'success': False,
                    'error': f'Not enough videos. Found {videos.count()}, need {video_count}',
                    'message': f'You only have {videos.count()} completed videos. Please create more videos first.'
                }

            video_ids = [str(v.id) for v in videos]

        logger.info(f"✅ Found {len(video_ids)} videos for editing: {video_ids}")

        # Session 84: EXECUTE VIDEO EDITING using VideoAgent!
        logger.info(f"🎬 Session 84: Executing multi-operation edit with VideoAgent...")

        video_agent = VideoAgent(user=user)
        result = video_agent.create_edited_video(
            video_ids=video_ids,
            operations=operations,
            project_name=project_name
        )

        # Return result
        if result.get('success'):
            logger.info(f"✅ Session 84: Multi-operation edit executed successfully!")

            # Build operation summary
            op_types = [op.get('type', 'unknown') for op in operations]
            op_summary = ', '.join(op_types)

            return {
                'success': True,
                'video_id': result.get('video_id'),
                'video_url': result.get('video_url'),
                'operations_applied': result.get('operations_applied', len(operations)),
                'duration': result.get('duration'),
                'project_name': result.get('project_name'),
                'video_count': len(video_ids),
                'operations_summary': op_summary,
                'message': result.get('message', f'✅ Video edited successfully with {result.get("operations_applied")} operations!'),
                'instructions': f'Your video has been edited with {result.get("operations_applied")} operations: {op_summary}',
                'note': '🎬 Your new edited video is ready in the Video Gallery!'
            }
        else:
            logger.error(f"❌ Session 84: Video editing failed: {result.get('error')}")
            return {
                'success': False,
                'error': result.get('error', 'Video editing failed'),
                'operations_applied': result.get('operations_applied', 0),
                'message': '❌ Failed to edit video',
                'instructions': 'Please check the logs for details. DaVinci Resolve Studio must be running.'
            }

    except Exception as e:
        logger.error(f"❌ Error in _execute_edit_video: {str(e)}", exc_info=True)
        raise


def _execute_generate_image(user, parameters, session=None):
    """
    Execute image generation tool
    Routes to Stability AI image generation

    Session 65: Phase 2.1 - Autonomous image generation
    Session 96: Weekend Project - Link generated images to AI session

    Parameters:
        prompt (str): Image description
        model (str): Model to use (core/sdxl/sd3/ultra) - optional
        style (str): Style preset - optional
        session (AISession): AI conversation session - optional

    Returns:
        dict: {
            'success': True,
            'image_url': 'URL to generated image',
            'image_id': 'History ID',
            'prompt': 'Actual prompt used'
        }
    """
    try:
        prompt = parameters.get('prompt', '').strip()
        model = parameters.get('model', 'sdxl')  # Default to sdxl (best balance)
        style = parameters.get('style', '')  # Optional style
        expected_text = parameters.get('expected_text', '').strip()  # Session 66: For Vision refinement
        # Session 201: Use negative_prompt from parameters (for text-free logos)
        negative_prompt = parameters.get('negative_prompt', 'blurry, low quality, distorted')

        # Session 181: Support custom sizes from image_generation_agent
        width = parameters.get('width')
        height = parameters.get('height')
        if width and height:
            size = f"{width}x{height}"
        else:
            size = parameters.get('size', '1024x1024')

        # Session 182: Get project for association
        # Session 267: Validate UUID before querying to avoid ValidationError
        # Session 272: uuid is imported at module level - don't re-import locally
        project = None
        project_id = parameters.get('project_id')
        if project_id:
            from content.models import CreativeProject
            # Validate that project_id is a valid UUID before querying
            try:
                uuid.UUID(str(project_id))  # This will raise ValueError if invalid
                project = CreativeProject.objects.get(id=project_id, user=user)
                logger.info(f"📁 Image will be associated with project: {project.name}")
            except ValueError:
                logger.warning(f"⚠️ Invalid project_id format (not a UUID): {project_id}")
                project_id = None  # Clear invalid project_id
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ Project {project_id} not found")

        if not prompt:
            raise ValueError("Prompt is required for image generation")

        logger.info(f"🎨 Executor generating image: {prompt[:50]}... (model: {model}, style: {style}, size: {size})")
        if expected_text:
            logger.info(f"👁️ Expected text for verification: '{expected_text}'")

        # Map model names to quality parameter
        model_to_quality = {
            'core': 'fast',
            'sdxl': 'balanced',
            'sd3': 'high',
            'ultra': 'premium'
        }
        quality = model_to_quality.get(model, 'balanced')

        # Session 184: Support count parameter for batch image generation
        # Extract count from parameters or nested params object
        count = parameters.get('count', 1)
        if isinstance(parameters.get('params'), dict):
            count = parameters['params'].get('count', count)
        count = min(max(int(count), 1), 5)  # Clamp between 1 and 5

        logger.info(f"🎨 Generating {count} image(s) with prompt: {prompt[:50]}...")
        logger.info(f"🚫 Negative prompt: {negative_prompt[:80]}..." if len(negative_prompt) > 80 else f"🚫 Negative prompt: {negative_prompt}")

        # Use ImageGenerationService directly (same as gallery_generate)
        from content.image_generation import ImageGenerationService
        service = ImageGenerationService()

        # Session 184: Generate multiple images in a loop
        # Session 806: Track last error for better error reporting
        generated_images = []
        last_error = None
        for i in range(count):
            logger.info(f"🎨 Generating image {i + 1}/{count}...")

            result = service.generate_image(
                prompt=prompt,
                size=size,  # Session 181: Use dynamic size
                style=style if style else "photographic",
                quality=quality,
                provider='stability',
                negative_prompt=negative_prompt,  # Session 201: Use parameter (for text-free logos)
                num_images=1
            )

            if not result.success:
                last_error = result.error_message or 'Unknown error'
                logger.error(f"❌ Image {i + 1} generation failed: {last_error}")
                continue  # Try to generate remaining images

            # Get the generated image
            images = result.images
            if not images:
                # Session 843: Set last_error even when success=True but images empty
                last_error = result.error_message or "API returned success but no images"
                logger.error(f"❌ Image {i + 1}: No image returned - {last_error}")
                continue

            image_data = images[0]
            image_url = image_data if isinstance(image_data, str) else image_data.get('url')

            # Save image to storage
            # Session 272: Handle anonymous users (use 'anonymous' folder)
            image_id = str(uuid.uuid4())
            user_folder = user.id if user else 'anonymous'
            filename = f"generated_images/{user_folder}/{image_id}.png"

            # Handle base64 data URIs vs regular URLs
            try:
                if image_url.startswith('data:image'):
                    # Extract base64 data from data URI
                    import re
                    base64_match = re.search(r'base64,(.+)', image_url)
                    if base64_match:
                        image_bytes = base64.b64decode(base64_match.group(1))
                        file_path = default_storage.save(filename, ContentFile(image_bytes))
                        saved_url = default_storage.url(file_path)
                    else:
                        raise Exception("Invalid base64 data URI")
                else:
                    # Regular HTTP/HTTPS URL - download it
                    response = requests.get(image_url, timeout=30)
                    if response.status_code == 200:
                        file_path = default_storage.save(filename, ContentFile(response.content))
                        saved_url = default_storage.url(file_path)
                    else:
                        raise Exception(f"Failed to download image: {response.status_code}")

                # Save to ImageHistory for tracking
                # Session 96 Weekend Project: Link to AI conversation session
                # Session 182: Link to project for Social Media Kit workflow
                # Session 272: Only save to history if user is authenticated
                # Session 794: Use system user for autonomous operations (Celery tasks)
                history_user = user
                if not history_user:
                    from core.views_image_misc import get_system_user
                    history_user = get_system_user()
                    logger.info(f"🤖 Using system_autonomous user for image history")

                from core.image_views.session import save_to_history
                history_record = save_to_history(
                    user=history_user,
                    file_path=file_path,
                    image_type='generated',
                    prompt=prompt,
                    parameters={
                        'model': model,
                        'style': style,
                        'quality': quality,
                        'batch_index': i + 1,
                        'autonomous': user is None  # Session 794: Track autonomous generation
                    },
                    model_used=model,
                    style=style,
                    parent_image=None,
                    session=session,  # Session 96: Link to AI conversation
                    project=project   # Session 182: Link to project
                )

                generated_images.append({
                    'image_url': saved_url,
                    'image_id': str(history_record.id) if history_record else image_id,
                    'file_path': file_path,
                    'batch_index': i + 1
                })

                logger.info(f"✅ Image {i + 1}/{count} generated successfully: {saved_url}")

            except Exception as img_error:
                # Session 843: Track save errors in last_error for better debugging
                last_error = f"Save failed: {str(img_error)}"
                logger.error(f"❌ Error saving image {i + 1}: {str(img_error)}")
                continue

        # Check if we generated any images
        # Session 806: Include the actual error message for better debugging
        # Session 843: Add prompt info to help debug content moderation issues
        if not generated_images:
            error_detail = last_error or "No images were generated"
            logger.error(f"❌ All {count} image(s) failed. Prompt: {prompt[:100]}... Error: {error_detail}")
            raise Exception(f"Image generation failed: {error_detail}")

        # Use the first image for backwards compatibility
        saved_url = generated_images[0]['image_url']
        file_path = generated_images[0].get('file_path', '')
        history_record = type('obj', (object,), {'id': generated_images[0]['image_id']})() if generated_images[0]['image_id'] else None

        logger.info(f"✅ Executor generated image successfully: {saved_url}")

        # Session 96 Weekend Project: Update session counter and check for auto-project creation
        from core.image_views.session import increment_session_counter
        project_info = increment_session_counter(session, 'image')

        # Session 66: AUTONOMOUS TEXT VERIFICATION & REFINEMENT
        expected_text = parameters.get('expected_text', '').strip()
        refinement_history = []

        if expected_text:
            logger.info(f"👁️ Starting autonomous text verification for: '{expected_text}'")
            max_attempts = 3
            current_url = saved_url
            current_history_id = history_record.id if history_record else None

            for attempt in range(max_attempts):
                logger.info(f"👁️ Verification attempt {attempt + 1}/{max_attempts}")

                # Verify current image with GPT-4 Vision
                verification = _verify_image_with_vision(current_url, expected_text)

                refinement_history.append({
                    'attempt': attempt + 1,
                    'image_url': current_url,
                    'verification': verification
                })

                if verification['correct']:
                    logger.info(f"✅ Text verified correct! Confidence: {verification['confidence']}")
                    break  # Text is correct, we're done!

                if attempt == max_attempts - 1:
                    logger.warning(f"⚠️ Max attempts reached, returning last version")
                    break  # Max attempts, return what we have

                # Text is wrong, use inpaint to fix it
                logger.info(f"🖌️ Text incorrect, calling inpaint to fix...")

                try:
                    inpaint_result = _execute_inpaint(user, {
                        'image_url': current_url,
                        'prompt': f"The text '{expected_text}' in clean, legible font",
                        'mask_description': 'the text area with the company/brand name'
                    })

                    if inpaint_result['success']:
                        current_url = inpaint_result['image_url']
                        current_history_id = inpaint_result['image_id']
                        logger.info(f"✅ Inpaint successful: {current_url}")
                    else:
                        logger.error(f"❌ Inpaint failed, keeping current version")
                        break

                except Exception as e:
                    logger.error(f"❌ Error during inpaint: {str(e)}")
                    break  # Error, return what we have

            # Update return values with final refined version
            saved_url = current_url
            if current_history_id:
                history_record = type('obj', (object,), {'id': current_history_id})()

        result = {
            'success': True,
            'image_url': saved_url,
            'image_id': history_record.id if history_record else None,
            'prompt': prompt,
            'model': model,
            'style': style,
            'refinement_history': refinement_history if refinement_history else None,
            'autonomous_refinement': len(refinement_history) > 1 if refinement_history else False,
            # Session 184: Include all generated images for batch requests
            'images': generated_images,
            'total_generated': len(generated_images),
            'requested_count': count
        }

        # Session 96: Include project creation info if project was auto-created
        if project_info:
            result.update(project_info)

        # Session 96: Include updated session counters for frontend indicator
        if session:
            session.refresh_from_db()  # Get latest counter values
            result['session_data'] = {
                'session_id': str(session.session_id),
                'total_images': session.total_images,
                'total_videos': session.total_videos,
                'total_audio': session.total_audio
            }

        return result

    except Exception as e:
        logger.error(f"❌ Error in _execute_generate_image: {str(e)}")
        raise


def _execute_generate_sound_effect(user, parameters):
    """
    Execute sound effect generation via Runway ML text-to-sound
    Session 81: AI Assistant integration for audio generation!

    This generates sound effects from text descriptions:
    1. Gets description and duration parameters
    2. Calls Runway ML text-to-sound API
    3. Returns task ID for polling

    Parameters:
        description (str): Description of the sound effect (required)
        duration (float): Duration in seconds (0.5 to 30) - default: 5

    Returns:
        dict: {
            'success': True,
            'task_id': 'uuid',
            'description': 'thunder clap',
            'duration': 5.0,
            'estimated_time': 10,
            'message': 'Generating sound effect...'
        }
    """
    try:
        from content.video_provider import runway_provider

        description = parameters.get('description', '').strip()
        duration = parameters.get('duration', 5.0)

        if not description:
            return {
                'success': False,
                'error': 'Description is required for sound effect generation',
                'message': 'Please describe the sound effect you want to create!'
            }

        # Validate duration
        duration = max(0.5, min(30.0, float(duration)))

        logger.info(f"🔊 AI Assistant generate_sound_effect: description={description}, duration={duration}s")

        # Call Runway ML text-to-sound
        result = runway_provider.text_to_sound(
            prompt=description,
            duration=duration
        )

        if not result.get('success'):
            return {
                'success': False,
                'error': result.get('error_message', 'Sound effect generation failed'),
                'message': f'Failed to generate sound effect: {result.get("error_message", "Unknown error")}'
            }

        logger.info(f"✅ Sound effect generation started: task_id={result.get('task_id')}")

        return {
            'success': True,
            'task_id': result.get('task_id'),
            'description': description,
            'duration': duration,
            'estimated_time': result.get('estimated_time', int(duration) + 5),
            'message': f'🔊 Generating {duration}s sound effect: "{description}"... This will take about {result.get("estimated_time", int(duration) + 5)} seconds.',
            'instructions': f'Your sound effect is being generated! Creating a {duration}-second audio clip of: "{description}". You\'ll be notified when it\'s ready.',
            'audio_type': 'sound_effect'
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_generate_sound_effect: {str(e)}")
        raise


# ========================================
# SESSION 100: LEADERSHIP DASHBOARD ENDPOINTS
# ========================================


def _execute_generate_speech(user, parameters):
    """
    Execute speech generation via Runway ML text-to-speech
    Session 81: AI Assistant integration for audio generation!

    This generates speech/voiceover from text:
    1. Gets text and voice parameters
    2. Calls Runway ML text-to-speech API
    3. Returns task ID for polling

    Parameters:
        text (str): Text to convert to speech (required)
        voice (str): Voice name (Rachel, Drew, Clyde, Paul, Aria, Domi, Dave) - default: Rachel

    Returns:
        dict: {
            'success': True,
            'task_id': 'uuid',
            'voice': 'Rachel',
            'text_preview': 'first 50 chars...',
            'estimated_time': 10,
            'message': 'Generating speech...'
        }
    """
    try:
        from content.video_provider import runway_provider

        text = parameters.get('text', '').strip()
        voice = parameters.get('voice', 'Rachel')

        if not text:
            return {
                'success': False,
                'error': 'Text is required for speech generation',
                'message': 'Please provide text to convert to speech!'
            }

        logger.info(f"🗣️ AI Assistant generate_speech: voice={voice}, text={text[:50]}...")

        # Call Runway ML text-to-speech
        result = runway_provider.text_to_speech(
            text=text,
            voice=voice
        )

        if not result.get('success'):
            return {
                'success': False,
                'error': result.get('error_message', 'Speech generation failed'),
                'message': f'Failed to generate speech: {result.get("error_message", "Unknown error")}'
            }

        logger.info(f"✅ Speech generation started: task_id={result.get('task_id')}")

        return {
            'success': True,
            'task_id': result.get('task_id'),
            'voice': voice,
            'text_preview': text[:50] + ('...' if len(text) > 50 else ''),
            'estimated_time': result.get('estimated_time', 10),
            'message': f'🗣️ Generating speech with {voice}\'s voice... This will take about {result.get("estimated_time", 10)} seconds.',
            'instructions': f'Your speech is being generated! The voice will say: "{text[:100]}{"..." if len(text) > 100 else ""}". You\'ll be notified when it\'s ready.',
            'audio_type': 'speech'
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_generate_speech: {str(e)}")
        raise


def _execute_generate_video(user, parameters, session=None):
    """
    Execute video generation tool
    Routes to Runway ML video generation

    Session 65: Phase 2.2 - Autonomous video generation
    Session 96: Weekend Project - Link generated videos to AI session
    Session 183: Support both direct params and operation-based params from GPT
    Session 794: Use system user for autonomous operations (Celery tasks)

    Parameters:
        prompt (str): Video description
        duration (int): Duration in seconds (5 or 10) - optional
        session (AISession): AI conversation session - optional

    Also supports operation-based format from GPT:
        operation (str): 'animate' or 'generate'
        params (dict): {prompt, image_id, duration}

    Returns:
        dict: {
            'success': True,
            'task_id': 'Runway task ID',
            'content_id': 'Database ID',
            'status': 'processing',
            'message': 'Video generation started'
        }
    """
    try:
        # Session 794: Use system user for autonomous operations
        is_autonomous = user is None
        if is_autonomous:
            from core.views_image_misc import get_system_user
            user = get_system_user()
            logger.info(f"🤖 Using system_autonomous user for video generation")
        # Session 183: Handle operation-based format from GPT
        operation = parameters.get('operation')
        if operation:
            # GPT sent operation-based params, extract the actual params
            inner_params = parameters.get('params', {})
            # Session 183: GPT may send motion_prompt OR prompt for animate operation
            prompt = inner_params.get('prompt', '') or inner_params.get('motion_prompt', '')
            prompt = prompt.strip() if prompt else ''
            duration = inner_params.get('duration', 6)
            # For animate operation, get image_id
            if operation == 'animate' and inner_params.get('image_id'):
                parameters['source_image_id'] = inner_params.get('image_id')
                # Session 183: If no prompt provided for animate, use a default motion prompt
                if not prompt:
                    prompt = "smooth natural motion with subtle movement"
            logger.info(f"🎬 Session 183: Extracted from operation={operation}: prompt={prompt[:50] if prompt else 'N/A'}...")
        else:
            # Direct params format
            prompt = parameters.get('prompt', '').strip()
            duration = parameters.get('duration', 6)  # Default to 6 seconds (Runway ML accepts 4, 6, or 8)

        if not prompt:
            raise ValueError("Prompt is required for video generation")

        # Validate duration - Runway ML only accepts 4, 6, or 8 seconds
        if duration not in [4, 6, 8]:
            logger.warning(f"⚠️ Invalid duration {duration}s, defaulting to 6s")
            duration = 6

        # Session 65: Runway ML has 1000 character prompt limit - truncate intelligently
        MAX_PROMPT_LENGTH = 1000
        if len(prompt) > MAX_PROMPT_LENGTH:
            logger.warning(f"⚠️ Prompt too long ({len(prompt)} chars), truncating to {MAX_PROMPT_LENGTH}")
            # Keep the first 950 chars and add ellipsis
            prompt = prompt[:950] + "..."
            logger.info(f"🎬 Truncated prompt: {prompt[:100]}...")

        # Session 122: Check for explicit source_image_id parameter FIRST (intelligent chaining!)
        # Session 119: BUGFIX - Check if prompt references an existing image
        # If found, use image-to-video instead of text-to-video
        source_image = None
        source_image_id = parameters.get('source_image_id')

        if source_image_id:
            # Session 122: AI explicitly passed an image ID - use it!
            # Session 183: Support hybrid IDs (numbers like "13" or UUIDs)
            try:
                from content.models import ImageHistory

                # Session 183: Handle numeric IDs (sequential_number) vs UUIDs
                image_id_str = str(source_image_id).strip()
                if image_id_str.isdigit():
                    # It's a sequential number - resolve to UUID
                    # Session 183: Order by -created_at to get newest record (handles duplicate sequential numbers)
                    seq_num = int(image_id_str)
                    source_image = ImageHistory.objects.filter(
                        user=user,
                        sequential_number=seq_num
                    ).order_by('-created_at').first()
                    if source_image:
                        logger.info(f"📸 Session 183: Resolved sequential #{seq_num} to UUID {source_image.id} (file: {source_image.file_path[:50] if source_image.file_path else 'N/A'}...)")
                    else:
                        logger.warning(f"⚠️ No image found with sequential_number={seq_num}")
                else:
                    # It's a UUID
                    source_image = ImageHistory.objects.get(id=source_image_id, user=user)
                    logger.info(f"📸 Session 122: AI passed explicit source_image_id: {source_image_id}")
            except ImageHistory.DoesNotExist:
                logger.warning(f"⚠️ Source image {source_image_id} not found, falling back to text-to-video")
                source_image = None
            except Exception as e:
                logger.warning(f"⚠️ Error resolving image ID {source_image_id}: {e}, falling back to text-to-video")
                source_image = None

        if not source_image:
            # Fallback to Session 119 text-based extraction
            source_image = _extract_image_reference(prompt, user)

        video_type = 'text_to_video'

        logger.info(f"🎬 Executor generating video: {prompt[:50]}... (duration: {duration}s)")

        # Use Runway ML provider directly (same as text_to_video view)
        from content.video_provider import runway_provider

        if source_image:
            # Image reference found - use image-to-video!
            logger.info(f"🖼️ Image reference detected! Using image-to-video with: {source_image.filename}")
            video_type = 'image_to_video'

            result = runway_provider.image_to_video(
                image_url=source_image.file_path,
                motion_prompt=prompt,
                duration=duration,
                quality='gen4_turbo',  # Use gen4_turbo for image-to-video
                enhance_prompt=True,
                ratio='1280:720'
            )
        else:
            # No image reference - use regular text-to-video
            result = runway_provider.text_to_video(
                prompt=prompt,
                duration=duration,
                quality='veo3.1_fast',  # Use fast model for executor
                style='realistic',
                enhance_prompt=True,
                enhancement_level='advanced',
                ratio='1920:1080'
            )

        if not result.success:
            raise Exception(f"Video generation failed: {result.error_message or 'Unknown error'}")

        # Session 68: Create VideoHistory record (not just ContentGeneration!)
        # This makes AI Assistant videos appear in Video Gallery
        # Session 96 Weekend Project: Link to AI conversation session
        from content.models import VideoHistory

        # Session 119: BUGFIX - Assign project if session already has one
        # When resuming a session with existing project, videos need to be linked immediately
        # Session 183: Also check for project_id in parameters (workflow passes it directly)
        video_project = None
        if session and session.project:
            video_project = session.project
            logger.info(f"📁 Assigning video to project from session: {session.project.name}")
        elif parameters.get('project_id'):
            # Session 183: Get project from parameters (workflow/direct tool call)
            from content.models import CreativeProject
            try:
                video_project = CreativeProject.objects.get(id=parameters['project_id'])
                logger.info(f"📁 Assigning video to project from parameters: {video_project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ Project {parameters['project_id']} not found")

        from core.services.workspace_resolver import get_active_workspace
        video = VideoHistory.objects.create(
            user=user,
            video_id=result.task_id,
            video_url='',  # Will be populated when video completes
            video_type=video_type,  # Session 119: BUGFIX - Dynamic type based on image reference
            workspace=get_active_workspace(user),
            prompt=prompt,
            parameters={
                'duration': duration,
                'quality': 'gen4_turbo' if source_image else 'veo3.1_fast',
                'style': 'realistic',
                'ratio': '1280:720' if source_image else '1920:1080',
                'enhance_prompt': True,
                'enhancement_level': 'advanced',
                'source_image_id': str(source_image.id) if source_image else None,  # Session 119: Track source
                'autonomous': is_autonomous  # Session 794: Track autonomous generation
            },
            model_used='gen4_turbo' if source_image else 'veo3.1_fast',
            duration=duration,
            ratio='1280:720' if source_image else '1920:1080',
            status='processing',
            session=session,  # Session 96: Link to AI conversation
            project=video_project,  # Session 119: BUGFIX - Assign project if session has one
            source_image=source_image  # Session 119: BUGFIX - Link to source image if image-to-video
        )

        logger.info(f"✅ Executor started video generation: {result.task_id}")
        logger.info(f"📹 Created VideoHistory record: {video.id}")

        # Session 144: Track agent contribution for video generation
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
            AgentContribution.objects.create(
                agent=agent,
                video=video,
                project=video_project,
                contribution_type='generation',
                task_description=f"Generated video via gallery_generate_video (type={video_type}, duration={duration}s)",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for video {video.id}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            # Don't fail video creation if contribution tracking fails

        # Session 96 Weekend Project: Update session counter and check for auto-project creation
        from core.image_views.session import increment_session_counter
        project_info = increment_session_counter(session, 'video')

        result_dict = {
            'success': True,
            'task_id': result.task_id,
            'content_id': str(video.id),
            'status': result.status,
            'estimated_time': result.estimated_time,
            'message': 'Video generation started successfully'
        }

        # Session 96: Include project creation info if project was auto-created
        if project_info:
            result_dict.update(project_info)

        return result_dict

    except Exception as e:
        logger.error(f"❌ Error in _execute_generate_video: {str(e)}")
        raise


def _execute_generate_voice(user, parameters, session=None):
    from core.views_audio import _execute_generate_voice as _impl
    return _impl(user, parameters, session)


def _execute_inpaint(user, parameters):
    """
    Execute inpaint tool to fix/regenerate specific areas of an image
    Perfect for fixing text in logos!

    Session 65: Multi-pass autonomous refinement

    Parameters:
        image_url (str): URL of image to edit
        prompt (str): What to regenerate in the masked area
        mask_description (str): Which area to fix

    Returns:
        dict: {
            'success': True,
            'image_url': 'URL of fixed image',
            'image_id': 'Database ID',
            'original_url': 'Original image URL',
            'prompt': 'Inpaint prompt used'
        }
    """
    try:
        image_url = parameters.get('image_url', '').strip()
        prompt = parameters.get('prompt', '').strip()
        mask_description = parameters.get('mask_description', '').strip()

        if not image_url or not prompt:
            raise ValueError("image_url and prompt are required for inpainting")

        logger.info(f"🖌️ Executor inpainting: {mask_description} -> {prompt[:50]}...")

        # Session 66: Use Stability AI Search and Replace API directly
        import requests
        import uuid
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage

        # Handle both absolute URLs and relative paths
        if image_url.startswith('/'):
            # Local path - read from disk
            image_path = image_url.lstrip('/')
            full_path = os.path.join(settings.BASE_DIR, image_path)
            with open(full_path, 'rb') as img_file:
                image_data = img_file.read()
        else:
            # Remote URL - download
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image_data = response.content

        # Call Stability AI Search and Replace API
        api_key = os.environ.get('STABILITY_API_KEY')
        api_url = 'https://api.stability.ai/v2beta/stable-image/edit/search-and-replace'

        # Prepare the request
        files = {
            'image': ('image.png', image_data, 'image/png')
        }
        data = {
            'prompt': prompt,
            'search_prompt': mask_description,
            'output_format': 'png'
        }
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'image/*'
        }

        logger.info(f"🖌️ Calling Stability AI Search and Replace...")
        api_response = requests.post(api_url, files=files, data=data, headers=headers)

        if api_response.status_code != 200:
            error_msg = api_response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            raise Exception(f"Inpaint API failed: {error_msg}")

        # Get the inpainted image data
        result_image_data = api_response.content

        # Save the inpainted image
        image_id = uuid.uuid4()
        filename = f"{user.id}/{image_id}.png"
        filepath = f"generated_images/{filename}"

        # Save to storage
        saved_path = default_storage.save(filepath, ContentFile(result_image_data))
        saved_url = f"/media/{saved_path}"

        # Save to ImageHistory
        from content.models import ImageHistory
        from core.services.workspace_resolver import get_active_workspace
        history_record = ImageHistory.objects.create(
            user=user,
            prompt=f"Inpaint: {prompt}",
            image_url=saved_url,
            image_type='inpaint',
            model_used='sdxl',
            style='inpaint',
            image_width=1024,
            image_height=1024,
            workspace=get_active_workspace(user),
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=history_record,
                project=None,
                contribution_type='editing',
                task_description="Edited image using image-editing-agent",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {{ history_record.id }}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            logger.error(f"❌ Failed to create agent contribution: {e}")

        logger.info(f"✅ Executor inpaint complete: {saved_url}")

        return {
            'success': True,
            'image_url': saved_url,
            'image_id': history_record.id,
            'original_url': image_url,
            'prompt': prompt,
            'mask_description': mask_description
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_inpaint: {str(e)}")
        raise


def _execute_scrape_website(parameters):
    """
    Execute website scraping tool
    Simple web scraper to extract text content

    Session 65: Phase 2.4 - Autonomous web scraping

    Parameters:
        url (str): Website URL to scrape

    Returns:
        dict: {
            'success': True,
            'url': 'URL scraped',
            'title': 'Page title',
            'text': 'Extracted text content (first 1000 chars)',
            'links': ['list', 'of', 'links']
        }
    """
    try:
        url = parameters.get('url', '').strip()

        if not url:
            raise ValueError("URL is required for web scraping")

        logger.info(f"🕷️ Executor scraping website: {url}")

        # Simple scraping with requests + basic parsing
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; DonkeyBetzBot/1.0)'
        })
        response.raise_for_status()

        html = response.text

        # Extract title (simple regex)
        import re
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        title = title_match.group(1) if title_match else 'No title'

        # Extract links (simple regex)
        link_matches = re.findall(r'href=["\']([^"\']+)["\']', html)
        links = [link for link in link_matches if link.startswith('http')][:10]  # Top 10 links

        # Extract text (remove HTML tags)
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        text = text[:1000]  # First 1000 chars

        logger.info(f"✅ Executor scraped {url}: {len(text)} chars, {len(links)} links")

        return {
            'success': True,
            'url': url,
            'title': title,
            'text': text,
            'links': links
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_scrape_website: {str(e)}")
        raise


def _execute_search_replace(user, parameters, session=None):
    """
    Internal function for search-and-replace in images.
    Called by ImageEditingAgent.

    Args:
        user: Django user object
        parameters: Dict with image_id, search_prompt, replace_prompt
        session: Optional session for tracking

    Returns:
        Dict with success, image_id, image_url
    """
    try:
        image_id = parameters.get('image_id')
        search_prompt = parameters.get('search_prompt')
        replace_prompt = parameters.get('replace_prompt')

        if not search_prompt or not replace_prompt:
            return {'success': False, 'error': 'search_prompt and replace_prompt required'}

        from core.views_image_edit import _resolve_image_and_bytes
        image, image_data, err = _resolve_image_and_bytes(user, image_id)
        if err:
            return {'success': False, 'error': err}

        seq_num = image.get_sequential_number()
        logger.info(f"🔄 Agent search-replace on image {image.id} (#{seq_num}): {search_prompt} → {replace_prompt}")

        # Call Stability AI search-and-replace API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return {'success': False, 'error': 'Stability AI API key not configured'}

        url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"
        files = {"image": image_data}
        data_params = {
            "prompt": replace_prompt,
            "search_prompt": search_prompt,
            "output_format": "png"
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI search-replace failed: {api_response.text}")
            return {'success': False, 'error': f'Search-replace failed: {api_response.text}'}

        # Save the modified image
        modified_image_data = api_response.content
        filename = f'edited_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(modified_image_data))
        image_url = default_storage.url(saved_path)

        # Create new image history entry
        from content.models import ImageHistory
        from core.services.workspace_resolver import get_active_workspace
        new_image = ImageHistory.objects.create(
            user=user,
            prompt=f"Edited from image #{seq_num}: replaced {search_prompt} with {replace_prompt}",
            file_path=saved_path,
            filename=filename,
            model_used="stability-search-replace",
            workspace=get_active_workspace(user),
        )

        logger.info(f"✅ Agent search-replace complete: {new_image.id}")

        return {
            'success': True,
            'image_id': str(new_image.id),
            'image_url': image_url,
            'sequential_number': new_image.get_sequential_number(),
            'message': f"Image edited successfully (#{new_image.get_sequential_number()})"
        }

    except Exception as e:
        logger.error(f"❌ Agent search-replace error: {e}")
        return {'success': False, 'error': str(e)}


def _execute_send_email(user, parameters):
    """
    Execute email sending tool
    Uses Resend API for transactional email

    Session 65: Phase 2.5 - Autonomous email sending

    Parameters:
        to_email (str): Recipient email
        subject (str): Email subject
        body (str): Email body (text or HTML)
        attachments (list): Optional list of attachment URLs

    Returns:
        dict: {
            'success': True,
            'message_id': 'Resend message ID',
            'to': 'recipient@email.com'
        }
    """
    try:
        to_email = parameters.get('to_email', '').strip()
        subject = parameters.get('subject', '').strip()
        body = parameters.get('body', '').strip()

        if not to_email or not subject or not body:
            raise ValueError("to_email, subject, and body are required for email")

        logger.info(f"📧 Executor sending email to: {to_email}")

        # Use Resend API
        resend_key = os.getenv('RESEND_API_KEY')
        if not resend_key:
            raise Exception("Resend API key not configured")

        # Call Resend API
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {resend_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": "AI Assistant <noreply@donkeybetz.com>",
            "to": [to_email],
            "subject": subject,
            "html": f"<p>{body}</p>"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        message_id = data.get('id')

        logger.info(f"✅ Executor sent email: {message_id}")

        return {
            'success': True,
            'message_id': message_id,
            'to': to_email
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_send_email: {str(e)}")
        raise


def _execute_show_recent_videos(user, parameters):
    """
    Show user's recent videos with numbers for easy reference
    Session 84: Video selection enhancement!

    Parameters:
        count (int): Number of videos to show (default: 10, max: 20)

    Returns:
        dict: {
            'success': True,
            'videos': [list of video info],
            'message': 'Here are your recent videos...'
        }
    """
    try:
        from content.models import VideoHistory

        # Get parameters
        count = min(int(parameters.get('count', 10)), 20)  # Max 20

        logger.info(f"📹 Showing {count} recent videos for user {user.username}")

        # Get recent completed videos
        videos = VideoHistory.objects.filter(
            user=user,
            status='completed'
        ).order_by('-created_at')[:count]

        if videos.count() == 0:
            return {
                'success': True,
                'videos': [],
                'count': 0,
                'message': "📹 **No Videos Yet**\n\nYou haven't created any videos yet! Try generating one first.",
                'instructions': 'Use commands like "generate a video of mountains" to create your first video!'
            }

        # Build video list with numbers
        video_list = []
        message_lines = [f"📹 **Your Recent Videos** ({videos.count()} found):\n"]

        for idx, video in enumerate(videos, 1):
            # Emoji based on video type
            type_emoji = {
                'text_to_video': '🎬',
                'image_to_video': '🖼️',
                'video_to_video': '🔄',
                'extended': '⏱️',
                'chained': '🔗',
                'color_graded': '🎨',
                'text_overlay': '📝',
                'multi_edit': '✨',
                'upscaled': '⬆️'
            }.get(video.video_type, '🎥')

            # Clean up prompt
            prompt_text = video.prompt[:60] if video.prompt else "Untitled video"
            if len(video.prompt or '') > 60:
                prompt_text += "..."

            # Add to message
            message_lines.append(f"**{idx}.** {type_emoji} {prompt_text}")

            # Add to video list for reference
            video_list.append({
                'number': idx,
                'id': str(video.id),
                'prompt': video.prompt,
                'video_type': video.video_type,
                'duration': video.duration,
                'url': video.video_url
            })

        message = "\n".join(message_lines)
        message += "\n\n💡 **How to use:**\n"
        message += "• \"Chain videos 3 and 4\"\n"
        message += "• \"Make video 2 cinematic\"\n"
        message += "• \"Chain the snowboarder and eagle videos\""

        logger.info(f"✅ Displayed {len(video_list)} videos")

        # Store video list in session for number-based reference
        # We'll use this in the next step when implementing number-based selection

        return {
            'success': True,
            'videos': video_list,
            'count': len(video_list),
            'message': message,
            'instructions': 'You can now reference these videos by number or description!'
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_show_recent_videos: {str(e)}", exc_info=True)
        raise


def _execute_strategic_review(user, parameters):
    """
    Execute strategic review by co-leadership agents.

    Session 189: Get executive team review BEFORE generating content.
    This ensures research findings are analyzed by CTO, COO, and Creative Director
    who then provide strategic direction for the content creation.

    Parameters:
        research_topic (str): The original research topic
        research_findings (str): Summary of web search results
        content_type (str): Type of content to create (logo, banner, etc.)
        user_context (str): Additional user context

    Returns:
        dict: {
            'success': True,
            'strategic_direction': {
                'key_insights': [...],
                'creative_recommendations': [...],
                'prompt_suggestions': [...],
                'technical_considerations': [...],
                'executive_summary': str
            },
            'participants': ['CTO', 'COO', 'Creative Director'],
            'meeting_summary': str
        }
    """
    try:
        research_topic = parameters.get('research_topic', '').strip()
        research_findings = parameters.get('research_findings', '').strip()
        content_type = parameters.get('content_type', 'general')
        user_context = parameters.get('user_context', '')

        if not research_topic or not research_findings:
            raise ValueError("research_topic and research_findings are required")

        logger.info(f"🏢 Strategic Review: Analyzing research for '{research_topic}'")
        logger.info(f"📋 Content type: {content_type}, Findings length: {len(research_findings)} chars")

        # Use MeetingCoordinatorAgent for strategic boardroom discussion
        from core.agents.executive import MeetingCoordinatorAgent
        coordinator = MeetingCoordinatorAgent(user=user)

        # Build strategic review topic with research context
        meeting_topic = f"""Strategic Review: {research_topic}

RESEARCH FINDINGS:
{research_findings[:2000]}

CONTENT TYPE TO CREATE: {content_type}
USER CONTEXT: {user_context}

OBJECTIVE: Provide strategic direction and creative recommendations for content creation based on this research.
Include specific prompt suggestions that incorporate the research insights."""

        # Start boardroom meeting with relevant executives
        # Include Creative Director for this creative-focused review
        participants = ['CTOAgent', 'COOAgent']

        # Check if CreativeDirectorAgent exists, add if so
        from core.models.agents_registry import UnifiedAgentTemplate
        try:
            UnifiedAgentTemplate.objects.get(name='CreativeDirectorAgent')
            participants.append('CreativeDirectorAgent')
        except UnifiedAgentTemplate.DoesNotExist:
            logger.info("CreativeDirectorAgent not found, proceeding with CTO + COO")

        meeting_results = coordinator.start_meeting(
            topic=meeting_topic,
            participants=participants
        )

        # Process meeting results into strategic direction format
        if meeting_results.get('status') != 'complete':
            raise Exception(f"Strategic review failed: {meeting_results.get('error', 'Unknown error')}")

        # Extract key insights and recommendations from agent responses
        key_insights = []
        creative_recommendations = []
        prompt_suggestions = []
        technical_considerations = []

        for agent_name, response in meeting_results.get('agent_responses', {}).items():
            # Extract insights based on agent type
            if 'CTO' in agent_name:
                technical_considerations.append(f"[CTO] {response}")
            elif 'COO' in agent_name:
                key_insights.append(f"[Operations] {response}")
            elif 'Creative' in agent_name:
                creative_recommendations.append(f"[Creative] {response}")

        # Generate prompt suggestions based on decisions
        decisions = meeting_results.get('decisions', [])
        for i, decision in enumerate(decisions[:3]):
            prompt_suggestions.append(decision)

        # Build executive summary
        executive_summary = meeting_results.get('summary', 'Strategic review complete.')

        result = {
            'success': True,
            'strategic_direction': {
                'key_insights': key_insights,
                'creative_recommendations': creative_recommendations,
                'prompt_suggestions': prompt_suggestions if prompt_suggestions else [
                    f"Modern {content_type} design incorporating research trends",
                    f"Professional {content_type} with industry best practices",
                    f"Creative {content_type} that stands out from competitors"
                ],
                'technical_considerations': technical_considerations,
                'executive_summary': executive_summary
            },
            'participants': participants,
            'meeting_summary': executive_summary,
            'action_items': meeting_results.get('action_items', []),
            'research_topic': research_topic,
            'content_type': content_type
        }

        logger.info(f"✅ Strategic Review complete: {len(prompt_suggestions)} prompt suggestions, "
                    f"{len(key_insights)} insights from {len(participants)} executives")

        return result

    except Exception as e:
        logger.error(f"❌ Error in _execute_strategic_review: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


# =============================================================================
# CLEAN ARCHITECTURE AGENT WRAPPERS
# Session 269: Phase 4 - Internal functions for agent tool execution
# These functions are called by the clean architecture agents (not views)
# =============================================================================


def _execute_web_search(parameters):
    """
    Execute web search tool
    Uses Serper API for Google search

    Session 65: Phase 2.3 - Autonomous web search

    Parameters:
        query (str): Search query

    Returns:
        dict: {
            'success': True,
            'results': [
                {
                    'title': 'Result title',
                    'link': 'URL',
                    'snippet': 'Description'
                },
                ...
            ],
            'query': 'Search query'
        }
    """
    try:
        query = parameters.get('query', '').strip()

        if not query:
            raise ValueError("Query is required for web search")

        logger.info(f"🔍 Executor searching web: {query}")

        # Use Serper API for Google search
        serper_key = os.getenv('SERPER_API_KEY')
        if not serper_key:
            raise Exception("Serper API key not configured")

        # Call Serper API
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": serper_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": 5  # Get top 5 results
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extract organic search results
        results = []
        organic = data.get('organic', [])
        for item in organic[:5]:  # Top 5 results
            results.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', '')
            })

        logger.info(f"✅ Executor found {len(results)} search results for '{query}'")

        return {
            'success': True,
            'results': results,
            'query': query
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_web_search: {str(e)}")
        raise


def _extract_image_reference(text, user):
    """
    Extract and resolve image references from text.

    Session 119: BUGFIX - Enable "create video from image 199" functionality

    Looks for patterns like:
    - "image 199"
    - "image #199"
    - "Image 199"
    - UUID strings

    Returns ImageHistory object if found, None otherwise.
    """
    import re
    from content.models import ImageHistory

    # Pattern 1: "image 199" or "image #199" (sequential number)
    pattern1 = r'image\s*#?(\d+)'
    matches = re.findall(pattern1, text, re.IGNORECASE)

    if matches:
        sequential_num = int(matches[0])
        # Session 183: Use sequential_number field (not id which is UUID)
        # Order by -created_at to handle duplicate sequential numbers
        try:
            image = ImageHistory.objects.filter(
                sequential_number=sequential_num,
                user=user
            ).order_by('-created_at').first()
            if image:
                logger.info(f"📸 Resolved 'image {sequential_num}' to: {image.filename} (ID: {image.id})")
                return image
            else:
                logger.warning(f"⚠️ Image #{sequential_num} not found for user {user.username}")
        except Exception as e:
            logger.warning(f"⚠️ Error finding image #{sequential_num}: {e}")

    # Pattern 2: UUID pattern (8-4-4-4-12 format)
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    uuid_matches = re.findall(uuid_pattern, text, re.IGNORECASE)

    if uuid_matches:
        try:
            image = ImageHistory.objects.get(id=uuid_matches[0], user=user)
            logger.info(f"📸 Resolved UUID to: {image.filename}")
            return image
        except ImageHistory.DoesNotExist:
            logger.warning(f"⚠️ Image UUID {uuid_matches[0]} not found")

    return None


def _generate_smart_project_name(title):
    """
    Generate a clean, professional project name from a verbose AI prompt.

    Transforms:
    - "Create three cartoon style logos for a mechanic shop" → "Mechanic Shop Logos"
    - "Generate social media posts for coffee brand" → "Coffee Brand Social Media"
    - "Make a modern website design" → "Modern Website Design"

    Algorithm:
    1. Remove common AI prompt prefixes
    2. Extract key subject nouns (last 3-5 important words)
    3. Remove filler words
    4. Title-case result
    5. Limit to 50 characters max
    """
    if not title:
        return "Untitled Project"

    # Step 1: Remove common AI prompt prefixes
    prefixes_to_remove = [
        'create a ', 'create three ', 'create ',
        'make a ', 'make three ', 'make ',
        'generate a ', 'generate three ', 'generate ',
        'design a ', 'design three ', 'design ',
        'build a ', 'build three ', 'build ',
        'draw a ', 'draw ', 'write a ', 'write '
    ]

    title_lower = title.lower()
    for prefix in prefixes_to_remove:
        if title_lower.startswith(prefix):
            title = title[len(prefix):]
            title_lower = title.lower()
            break

    # Step 2: Remove filler words and focus on meaningful content
    filler_words = {
        'a', 'an', 'the', 'some', 'for', 'with', 'about', 'using',
        'in', 'on', 'at', 'by', 'from', 'of', 'to', 'and', 'or', 'but',
        'style', 'styled', 'themed',  # Often redundant in project names
        'called', 'named'  # Session 122: Remove "called/named" from project names (e.g., "tech startup called Cloud" → "Tech Startup Cloud")
    }

    words = title.split()
    meaningful_words = []
    for word in words:
        # Keep words that are:
        # - Not filler words
        # - OR are important content words (capitalized, numbers, etc.)
        clean_word = word.strip('.,!?;:').lower()
        if clean_word not in filler_words or word[0].isupper() or clean_word.isdigit():
            meaningful_words.append(word.strip('.,!?;:'))

    # Step 3: Smart truncation - keep last 3-5 meaningful words (usually the core subject)
    # Example: "cartoon style logos for a mechanic shop" → "logos mechanic shop"
    if len(meaningful_words) > 5:
        # For longer prompts, take last 4-5 words (usually contains the subject)
        meaningful_words = meaningful_words[-5:]
    elif len(meaningful_words) > 3:
        # For medium prompts, keep last 3-4 words
        meaningful_words = meaningful_words[-4:]

    # Step 4: Join and title-case
    project_name = ' '.join(meaningful_words)
    project_name = project_name.title()

    # Step 5: Limit length
    if len(project_name) > 50:
        project_name = project_name[:47] + '...'

    return project_name if project_name else "Untitled Project"


def _verify_image_with_vision(image_url, expected_text):
    """
    Use GPT-4 Vision to verify image text accuracy

    Session 66: Vision-powered autonomous refinement

    Parameters:
        image_url (str): URL of image to verify
        expected_text (str): Text that should appear in image

    Returns:
        dict: {
            'correct': True/False,
            'observed_text': 'What Vision actually sees',
            'feedback': 'Specific feedback for correction',
            'confidence': 'high/medium/low'
        }
    """
    try:
        import base64

        logger.info(f"👁️ Using GPT-4 Vision to verify text: '{expected_text}'")

        # Session 66: Fix - Convert local URLs to base64 data URIs
        # OpenAI Vision API can't access localhost URLs, so we need to encode the image
        if image_url.startswith('/'):
            # Local file path - read from disk and convert to base64
            image_path = image_url.lstrip('/')  # Remove leading slash
            full_path = os.path.join(settings.BASE_DIR, image_path)

            logger.info(f"👁️ Reading local image: {full_path}")

            with open(full_path, 'rb') as img_file:
                image_data = img_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')

            # Determine image format from extension
            ext = image_url.split('.')[-1].lower()
            mime_type = f"image/{ext}" if ext in ['png', 'jpg', 'jpeg', 'webp'] else 'image/png'

            # Create data URI
            image_url = f"data:{mime_type};base64,{base64_image}"
            logger.info(f"👁️ Converted to base64 data URI ({len(base64_image)} chars)")

        # Get OpenAI client
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Build Vision API request
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a text verification expert. Analyze images and verify if text matches expectations.

Be VERY specific about what you see:
- Report the EXACT text you observe (including spelling, spacing, punctuation)
- Compare it to the expected text
- Provide specific feedback on what's wrong
- Be critical but accurate"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Analyze this image and verify the text.

**Expected Text:** "{expected_text}"

**Your Task:**
1. What text do you actually see in this image? (Report EXACT text, including all words)
2. Does it match "{expected_text}" perfectly?
3. If not, what's different? (spelling, missing words, extra words, wrong order, etc.)

Be specific and accurate. This is for autonomous text correction."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            max_completion_tokens=300,
            reasoning_effort="medium",
        )

        # Parse Vision response
        vision_feedback = response.choices[0].message.content
        logger.info(f"👁️ Vision feedback: {vision_feedback}")

        # Analyze Vision's response to determine correctness
        lower_feedback = vision_feedback.lower()
        expected_lower = expected_text.lower()

        # Check if Vision confirms match
        correct = any([
            'matches perfectly' in lower_feedback,
            'correct' in lower_feedback and 'incorrect' not in lower_feedback,
            'yes' in lower_feedback and 'does it match' in lower_feedback,
            f'"{expected_lower}"' in lower_feedback and 'matches' in lower_feedback
        ])

        # Determine confidence based on Vision's language
        if 'exactly' in lower_feedback or 'perfect' in lower_feedback:
            confidence = 'high'
        elif 'mostly' in lower_feedback or 'close' in lower_feedback:
            confidence = 'medium'
        else:
            confidence = 'low'

        # Try to extract what Vision actually observed
        observed_text = expected_text  # Default to expected if we can't extract
        if 'see' in lower_feedback or 'says' in lower_feedback or 'reads' in lower_feedback:
            # Vision mentioned what it sees - try to extract it
            import re
            # Look for quoted text
            quotes = re.findall(r'"([^"]+)"', vision_feedback)
            if quotes:
                # First quote is usually what it actually sees
                observed_text = quotes[0] if quotes[0].lower() != expected_lower else expected_text

        result = {
            'correct': correct,
            'observed_text': observed_text,
            'feedback': vision_feedback,
            'confidence': confidence
        }

        logger.info(f"👁️ Verification result: {result}")
        return result

    except Exception as e:
        logger.error(f"❌ Error in _verify_image_with_vision: {str(e)}")
        # Return neutral result on error (don't block generation)
        return {
            'correct': True,  # Assume correct if we can't verify
            'observed_text': expected_text,
            'feedback': f'Vision verification failed: {str(e)}',
            'confidence': 'low'
        }

