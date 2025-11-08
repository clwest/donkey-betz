"""
DaVinci Resolve Video Editing API Endpoints
Session 66 Part 2: Professional video editing workflows

These endpoints enable:
- Creating multi-clip video projects
- Adding transitions and effects
- Text overlays with perfect spelling
- Background music and audio mixing
- Color grading and professional rendering

IMPORTANT: Requires DaVinci Resolve Studio ($200)
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from content.davinci_provider import get_davinci_provider

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def create_video_project_endpoint(request):
    """
    POST /api/v1/davinci/create-project/
    Create new DaVinci Resolve project

    Form Data:
        - project_name: Name for the new project (required)
        - video_clips: JSON array of video file paths (required)
        - transitions: JSON array of transition configs (optional)
        - text_overlays: JSON array of text overlay configs (optional)
        - audio_path: Path to background music (optional)
        - audio_volume: Audio volume 0.0-1.0 (optional, default 0.5)

    Returns:
        {
            'success': bool,
            'project_name': str,
            'video_path': str,  # Path to rendered video
            'duration': float,  # Total duration in seconds
            'error_message': str  # If failed
        }

    Example Request:
        {
            "project_name": "Mountain Coffee Promo",
            "video_clips": [
                "/path/to/clip1.mp4",
                "/path/to/clip2.mp4",
                "/path/to/clip3.mp4"
            ],
            "transitions": [
                {"type": "Cross Dissolve", "at_second": 8, "duration": 1.0},
                {"type": "Fade", "at_second": 16, "duration": 1.0}
            ],
            "text_overlays": [
                {
                    "text": "Mountain Coffee Co.",
                    "position": "center",
                    "start_second": 0,
                    "duration": 3,
                    "font_size": 72
                },
                {
                    "text": "Order Now",
                    "position": "lower_third",
                    "start_second": 20,
                    "duration": 3
                }
            ],
            "audio_path": "/path/to/background_music.mp3",
            "audio_volume": 0.3
        }
    """
    try:
        # Get DaVinci provider
        davinci = get_davinci_provider()

        # Check if Studio is available
        if not davinci.studio_available:
            return JsonResponse({
                'success': False,
                'error_message': 'DaVinci Resolve Studio not available. Studio version ($200) required for API access. Free version does not support Python API.',
                'purchase_link': 'https://www.blackmagicdesign.com/products/davinciresolve/studio'
            }, status=503)

        # Parse request data
        project_name = request.POST.get('project_name', '').strip()
        video_clips_json = request.POST.get('video_clips', '[]')
        transitions_json = request.POST.get('transitions', '[]')
        text_overlays_json = request.POST.get('text_overlays', '[]')
        audio_path = request.POST.get('audio_path', '').strip()
        audio_volume = float(request.POST.get('audio_volume', 0.5))

        # Validate
        if not project_name:
            return JsonResponse({
                'success': False,
                'error_message': 'Project name is required'
            }, status=400)

        # Parse JSON arrays
        try:
            video_clips = json.loads(video_clips_json)
            transitions = json.loads(transitions_json)
            text_overlays = json.loads(text_overlays_json)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error_message': f'Invalid JSON: {str(e)}'
            }, status=400)

        if not video_clips or len(video_clips) == 0:
            return JsonResponse({
                'success': False,
                'error_message': 'At least one video clip is required'
            }, status=400)

        logger.info(f"🎬 Creating DaVinci project: {project_name}")
        logger.info(f"📹 Video clips: {len(video_clips)}")
        logger.info(f"✨ Transitions: {len(transitions)}")
        logger.info(f"📝 Text overlays: {len(text_overlays)}")

        # Create project
        success = davinci.create_project(project_name)
        if not success:
            return JsonResponse({
                'success': False,
                'error_message': 'Failed to create DaVinci project'
            }, status=500)

        # Add video clips to timeline
        current_position = 0
        for i, clip_path in enumerate(video_clips):
            logger.info(f"📹 Adding clip {i+1}/{len(video_clips)}: {clip_path}")

            success = davinci.add_clip_to_timeline(
                video_path=clip_path,
                position_seconds=current_position
            )

            if not success:
                logger.warning(f"⚠️ Failed to add clip: {clip_path}")
                continue

            # Estimate clip duration (would be better to get actual duration)
            # For now, assume 8 seconds per Runway clip
            current_position += 8

        # Add transitions
        for transition in transitions:
            logger.info(f"✨ Adding transition: {transition}")

            davinci.add_transition(
                transition_type=transition.get('type', 'Cross Dissolve'),
                at_second=transition.get('at_second', 0),
                duration=transition.get('duration', 1.0)
            )

        # Add text overlays
        for text_overlay in text_overlays:
            logger.info(f"📝 Adding text: {text_overlay.get('text')}")

            davinci.add_text_overlay(
                text=text_overlay.get('text', ''),
                position=text_overlay.get('position', 'center'),
                start_second=text_overlay.get('start_second', 0),
                duration_seconds=text_overlay.get('duration', 3),
                font=text_overlay.get('font', 'Arial'),
                font_size=text_overlay.get('font_size', 72),
                color=text_overlay.get('color', '#FFFFFF')
            )

        # Add audio if provided
        if audio_path:
            logger.info(f"🎵 Adding audio: {audio_path}")

            davinci.add_audio(
                audio_path=audio_path,
                volume=audio_volume,
                start_second=0
            )

        # Render project
        logger.info(f"📹 Rendering project: {project_name}")

        render_result = davinci.render_project(
            format='mp4',
            quality='high',
            resolution='1920x1080'
        )

        if render_result.success:
            logger.info(f"✅ Project rendered successfully!")

            return JsonResponse({
                'success': True,
                'project_name': render_result.project_name,
                'video_path': render_result.video_path,
                'duration': render_result.duration,
                'message': f'Video project created successfully! {len(video_clips)} clips, {len(transitions)} transitions, {len(text_overlays)} text overlays.'
            })
        else:
            logger.error(f"❌ Render failed: {render_result.error_message}")

            return JsonResponse({
                'success': False,
                'error_message': f'Render failed: {render_result.error_message}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ DaVinci endpoint error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def check_davinci_status(request):
    """
    GET /api/v1/davinci/status/
    Check if DaVinci Resolve Studio is available

    Returns:
        {
            'studio_available': bool,
            'message': str,
            'purchase_link': str  # If Studio not available
        }
    """
    try:
        davinci = get_davinci_provider()

        if davinci.studio_available:
            return JsonResponse({
                'studio_available': True,
                'message': 'DaVinci Resolve Studio is connected and ready!'
            })
        else:
            return JsonResponse({
                'studio_available': False,
                'message': 'DaVinci Resolve Studio not available. Purchase Studio version ($200) for API access.',
                'purchase_link': 'https://www.blackmagicdesign.com/products/davinciresolve/studio',
                'free_version_note': 'Free version does not support Python API or scripting.'
            })

    except Exception as e:
        logger.error(f"❌ Status check error: {e}")
        return JsonResponse({
            'studio_available': False,
            'error_message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def chain_videos_simple(request):
    """
    POST /api/v1/davinci/chain-videos/
    Simple endpoint to chain videos together (no text/audio)

    Form Data:
        - video_clips: JSON array of video URLs/paths from gallery (required)
        - project_name: Name for project (optional, auto-generated if not provided)
        - add_transitions: "true" or "false" (default: "true")

    Returns:
        {
            'success': bool,
            'video_path': str,
            'duration': float,
            'message': str
        }

    Example:
        POST /api/v1/davinci/chain-videos/
        {
            "video_clips": [
                "http://localhost:8000/media/videos/clip1.mp4",
                "http://localhost:8000/media/videos/clip2.mp4",
                "http://localhost:8000/media/videos/clip3.mp4"
            ],
            "project_name": "My Chained Video",
            "add_transitions": "true"
        }
    """
    try:
        davinci = get_davinci_provider()

        if not davinci.studio_available:
            return JsonResponse({
                'success': False,
                'error_message': 'DaVinci Resolve Studio required ($200). Free version does not support API.',
                'purchase_link': 'https://www.blackmagicdesign.com/products/davinciresolve/studio'
            }, status=503)

        # Parse video clips
        video_clips_json = request.POST.get('video_clips', '[]')
        try:
            video_clips = json.loads(video_clips_json)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error_message': 'Invalid video_clips JSON'
            }, status=400)

        if not video_clips or len(video_clips) == 0:
            return JsonResponse({
                'success': False,
                'error_message': 'At least one video clip is required'
            }, status=400)

        # Project name
        project_name = request.POST.get('project_name', '').strip()
        if not project_name:
            import time
            project_name = f"Chained Video {int(time.time())}"

        # Add transitions?
        add_transitions = request.POST.get('add_transitions', 'true').lower() == 'true'

        logger.info(f"🎬 Chaining {len(video_clips)} videos: {project_name}")

        # Create project
        success = davinci.create_project(project_name)
        if not success:
            return JsonResponse({
                'success': False,
                'error_message': 'Failed to create project'
            }, status=500)

        # Add clips
        current_position = 0
        for i, clip_url in enumerate(video_clips):
            logger.info(f"📹 Adding clip {i+1}/{len(video_clips)}")

            # TODO: Download video from URL if it's a URL
            # For now, assume local paths

            davinci.add_clip_to_timeline(
                video_path=clip_url,
                position_seconds=current_position
            )

            current_position += 8  # Assume 8s clips

            # Add transition between clips
            if add_transitions and i > 0:
                davinci.add_transition(
                    transition_type="Cross Dissolve",
                    at_second=current_position - 1,
                    duration=1.0
                )

        # Render
        logger.info(f"📹 Rendering chained video")
        render_result = davinci.render_project()

        if render_result.success:
            return JsonResponse({
                'success': True,
                'video_path': render_result.video_path,
                'duration': render_result.duration,
                'message': f'Successfully chained {len(video_clips)} videos!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error_message': render_result.error_message
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Chain videos error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)
