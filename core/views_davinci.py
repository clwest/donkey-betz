"""
DaVinci Resolve Video Editing API Endpoints
Session 66 Part 2: Professional video editing workflows
Session 67: Frontend UI integration + database saving

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
import re
import requests
import shutil
import time
import uuid
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from content.davinci_provider import get_davinci_provider
from content.models import VideoHistory

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

        # Download videos to temp directory
        temp_dir = Path('/tmp/davinci_chain')
        temp_dir.mkdir(parents=True, exist_ok=True)

        local_video_paths = []
        total_duration = 0

        for i, clip_url in enumerate(video_clips):
            logger.info(f"📥 Processing clip {i+1}/{len(video_clips)}: {clip_url}")

            try:
                temp_path = temp_dir / f"clip_{i+1}.mp4"

                # Session 71: Handle both local files and external URLs
                if clip_url.startswith('/media/'):
                    # Local file - copy directly from filesystem
                    local_file_path = Path(clip_url.lstrip('/'))  # Remove leading slash for relative path

                    if not local_file_path.exists():
                        # Try absolute path
                        local_file_path = Path('/Users/donkeyking/development/unified-donkey-betz') / clip_url.lstrip('/')

                    if local_file_path.exists():
                        shutil.copy2(local_file_path, temp_path)
                        file_size = local_file_path.stat().st_size / 1024
                        logger.info(f"✅ Copied local file {file_size:.1f} KB to {temp_path}")
                    else:
                        raise FileNotFoundError(f"Local file not found: {clip_url}")
                else:
                    # External URL - download with requests
                    response = requests.get(clip_url, timeout=30)
                    response.raise_for_status()
                    temp_path.write_bytes(response.content)
                    logger.info(f"✅ Downloaded {len(response.content) / 1024:.1f} KB to {temp_path}")

                local_video_paths.append(str(temp_path))

                # Assume 8s per clip for duration calculation (could use ffprobe for accuracy)
                total_duration += 8
            except Exception as e:
                logger.error(f"❌ Failed to process clip {i+1}: {e}")
                return JsonResponse({
                    'success': False,
                    'error_message': f'Failed to download video {i+1}: {str(e)}'
                }, status=500)

        # Add clips to timeline
        current_position = 0
        for i, video_path in enumerate(local_video_paths):
            logger.info(f"📹 Adding clip {i+1}/{len(local_video_paths)} to timeline")

            davinci.add_clip_to_timeline(
                video_path=video_path,
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

        # Session 67: Add advanced features
        # Text overlays
        text_overlays_json = request.POST.get('text_overlays', '[]')
        try:
            text_overlays = json.loads(text_overlays_json)
            for text_overlay in text_overlays:
                logger.info(f"📝 Adding text overlay: {text_overlay.get('text')}")
                davinci.add_text_overlay(
                    text=text_overlay.get('text', ''),
                    position=text_overlay.get('position', 'center'),
                    start_second=text_overlay.get('start_second', 0),
                    duration_seconds=text_overlay.get('duration', 3),
                    font=text_overlay.get('font', 'Arial'),
                    font_size=text_overlay.get('font_size', 72),
                    color=text_overlay.get('color', '#FFFFFF')
                )
        except json.JSONDecodeError:
            logger.warning("⚠️ Invalid text_overlays JSON, skipping")

        # Background music
        if 'audio_file' in request.FILES:
            audio_file = request.FILES['audio_file']
            audio_volume = float(request.POST.get('audio_volume', 0.3))

            # Save audio to temp file
            audio_path = temp_dir / f"audio_{int(time.time())}.{audio_file.name.split('.')[-1]}"
            with open(audio_path, 'wb') as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)

            logger.info(f"🎵 Adding background music: {audio_path}")
            davinci.add_audio(
                audio_path=str(audio_path),
                volume=audio_volume,
                start_second=0
            )

        # Color grading
        color_grade = request.POST.get('color_grade', '')
        if color_grade:
            logger.info(f"🎨 Applying color grading: {color_grade}")
            # Note: DaVinci provider would need apply_color_grade() method
            # For now, log it - implementation depends on DaVinci API capabilities
            logger.warning(f"⚠️ Color grading '{color_grade}' requested but not yet implemented in provider")

        # Render
        logger.info(f"📹 Rendering chained video")
        # Session 71: Sanitize project_name to remove invalid filename characters (colons, slashes, etc.)
        safe_project_name = re.sub(r'[^\w\s-]', '', project_name)  # Remove special chars
        safe_project_name = safe_project_name.replace(' ', '_')    # Replace spaces
        output_path = str(temp_dir / f"{safe_project_name}_chained.mp4")

        # Session 67: Get render quality from request
        render_quality = request.POST.get('render_quality', '1920x1080')
        logger.info(f"📹 Render quality: {render_quality}")

        render_result = davinci.render_project(
            output_path=output_path,
            format='mp4',
            quality='high',
            resolution=render_quality
        )

        if render_result.success:
            logger.info(f"✅ Video rendered successfully: {output_path}")

            # Save to VideoHistory database (Session 70: Fixed video_url field)
            try:
                # Ensure media directory exists
                media_dir = Path('media/generated_videos')
                media_dir.mkdir(parents=True, exist_ok=True)

                # Generate unique filename
                unique_id = uuid.uuid4().hex[:8]
                filename = f"chained_{unique_id}.mp4"
                destination = media_dir / filename

                # Copy rendered video to media directory
                shutil.copy2(output_path, destination)
                logger.info(f"📦 Copied video to: {destination}")

                # Create VideoHistory record (Session 70: Use video_url not file_path!)
                from core.services.workspace_resolver import get_active_workspace
                video_history = VideoHistory.objects.create(
                    user=request.user,  # Required field!
                    prompt=f"Chained video: {project_name} ({len(video_clips)} clips)",
                    model_used="DaVinci Resolve Studio",
                    video_type="chained_video",  # New type for chained videos
                    duration=total_duration,
                    status='completed',
                    video_url=f"/media/generated_videos/{filename}",  # Local media URL
                    workspace=get_active_workspace(request.user),
                )

                # Session 142: Track agent contribution
                try:
                    from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                    agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                    AgentContribution.objects.create(
                        agent=agent,
                        video=video_history,
                        project=None,
                        contribution_type='generation',
                        task_description="Generated video using VideoAgent",
                        execution_time_seconds=0.0
                    )
                    logger.info(f"✅ Agent contribution tracked for video {{ video_history.id }}")
                except Exception as e:
                    logger.error(f"❌ Failed to create agent contribution: {e}")
                    # Don't fail content creation if contribution tracking fails

                # Get the full URL for the video
                video_url = request.build_absolute_uri(video_history.video_url)

                logger.info(f"✅ Saved chained video to database: {video_history.id}")

                return JsonResponse({
                    'success': True,
                    'video_url': video_url,
                    'video_path': output_path,
                    'duration': total_duration,
                    'video_id': str(video_history.id),
                    'message': f'Successfully chained {len(video_clips)} videos!'
                })
            except Exception as db_error:
                logger.error(f"❌ Failed to save to database: {db_error}")
                # Still return success but note database save failed
                return JsonResponse({
                    'success': True,
                    'video_path': output_path,
                    'duration': total_duration,
                    'message': f'Successfully chained {len(video_clips)} videos! (Database save failed: {str(db_error)})'
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


@csrf_exempt
@require_http_methods(["POST"])
def add_text_overlay_endpoint(request):
    """
    POST /api/v1/davinci/add-text-overlay/
    Add text overlay to a video using DaVinci Resolve
    Session 72: Voice-controlled text overlays!

    Form Data:
        - video_id: UUID of source video (required)
        - text: Text to display (required)
        - position: 'center', 'lower_third', or 'upper_third' (default: 'center')
        - start_second: When to show text (default: 0)
        - duration: How long to show text in seconds (default: 3)
        - font_size: Text size 36-144 (default: 72)
        - project_name: Optional project name

    Returns:
        {
            'success': bool,
            'video_url': str,
            'video_id': str,
            'message': str
        }
    """
    try:
        # Session 128: Removed DaVinci Studio check - this endpoint uses ffmpeg (Session 73)
        # Parse parameters
        video_id = request.POST.get('video_id', '').strip()
        text = request.POST.get('text', '').strip()
        position = request.POST.get('position', 'center')
        start_second = float(request.POST.get('start_second', 0))
        duration = float(request.POST.get('duration', 3))
        font_size = int(request.POST.get('font_size', 72))
        project_name = request.POST.get('project_name', f'Text_Overlay_{int(time.time())}')

        if not video_id or not text:
            return JsonResponse({
                'success': False,
                'error_message': 'video_id and text are required'
            }, status=400)

        logger.info(f"📝 Adding text overlay '{text}' to video {video_id}")

        # Session 128: Hybrid ID resolution (numeric or UUID)
        try:
            if video_id.isdigit():
                # Sequential number - resolve to UUID
                seq_num = int(video_id)
                video = VideoHistory.objects.filter(user=request.user).order_by('created_at')[seq_num - 1]
            else:
                # UUID
                video = VideoHistory.objects.get(id=video_id, user=request.user)
        except (VideoHistory.DoesNotExist, IndexError):
            return JsonResponse({
                'success': False,
                'error_message': f'Video {video_id} not found'
            }, status=404)

        # Create temporary directory
        temp_dir = Path('/tmp/davinci_text')
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Download source video
        source_path = temp_dir / f"source_{video_id}.mp4"
        if video.video_url.startswith('/media/'):
            local_file = Path(video.video_url.lstrip('/'))
            shutil.copy2(local_file, source_path)
        else:
            response = requests.get(video.video_url, timeout=30)
            source_path.write_bytes(response.content)

        logger.info(f"✅ Source video downloaded to {source_path}")

        # Session 73: Use ffmpeg for text overlay (simpler and more reliable than Fusion!)
        # Position mapping for ffmpeg
        position_map = {
            'center': '(w-text_w)/2:(h-text_h)/2',
            'lower_third': '(w-text_w)/2:h*0.75',
            'upper_third': '(w-text_w)/2:h*0.25'
        }

        ffmpeg_position = position_map.get(position, '(w-text_w)/2:(h-text_h)/2')

        # Escape text for ffmpeg (handle special characters)
        escaped_text = text.replace("'", "'\\''").replace(":", "\\:")

        # Create output path
        safe_project_name = re.sub(r'[^\w\s-]', '', project_name).replace(' ', '_')
        output_path = str(temp_dir / f"{safe_project_name}_with_text.mp4")

        logger.info(f"🎨 Using ffmpeg for text overlay (better than Fusion API!)")
        logger.info(f"📝 Text: '{text}' at {position}")

        # Build ffmpeg command for text overlay
        # Uses drawtext filter with perfect spelling!
        import subprocess

        ffmpeg_cmd = [
            'ffmpeg',
            '-i', str(source_path),
            '-vf', f"drawtext=text='{escaped_text}':fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:fontsize={font_size}:fontcolor=white:borderw=2:bordercolor=black:x={ffmpeg_position.split(':')[0]}:y={ffmpeg_position.split(':')[1]}:enable='between(t,{start_second},{start_second + duration})'",
            '-c:a', 'copy',  # Copy audio without re-encoding
            '-y',  # Overwrite output
            output_path
        ]

        logger.info(f"🎬 Running ffmpeg text overlay...")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg error: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error_message': f'Text overlay failed: {result.stderr[:200]}'
            }, status=500)

        logger.info(f"✅ Text overlay complete!")

        # Create a simple render result (ffmpeg already did the work!)
        from content.davinci_provider import DaVinciRenderResult
        render_result = DaVinciRenderResult(
            success=True,
            video_path=output_path,
            project_name=project_name
        )

        if render_result.success:
            # Save to database
            media_dir = Path('media/generated_videos')
            media_dir.mkdir(parents=True, exist_ok=True)

            unique_id = uuid.uuid4().hex[:8]
            filename = f"text_overlay_{unique_id}.mp4"
            destination = media_dir / filename

            shutil.copy2(output_path, destination)

            from core.services.workspace_resolver import get_active_workspace
            video_history = VideoHistory.objects.create(
                user=request.user,
                prompt=f"Text overlay: '{text}' on {video.prompt[:50]}",
                model_used="DaVinci Resolve Studio",
                video_type="text_overlay",
                duration=video.duration or 8,
                status='completed',
                video_url=f"/media/generated_videos/{filename}",
                workspace=get_active_workspace(request.user),
            )

            # Session 142: Track agent contribution
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=video_history,
                    project=None,
                    contribution_type='generation',
                    task_description="Generated video using VideoAgent",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for video {{ video_history.id }}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")
                # Don't fail content creation if contribution tracking fails

            video_url = request.build_absolute_uri(video_history.video_url)

            return JsonResponse({
                'success': True,
                'video_url': video_url,
                'video_id': str(video_history.id),
                'message': f'Text overlay "{text}" added successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error_message': render_result.error_message
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Text overlay error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def apply_color_grading_endpoint(request):
    """
    POST /api/v1/davinci/apply-color-grading/
    Apply color grading to a video using DaVinci Resolve
    Session 72: Voice-controlled color grading!

    Form Data:
        - video_id: UUID of source video (required)
        - style: Color grading style (default: 'cinematic_warm')
        - project_name: Optional project name

    Returns:
        {
            'success': bool,
            'video_url': str,
            'video_id': str,
            'message': str
        }
    """
    try:
        # Session 128: Removed DaVinci Studio check - this endpoint uses ffmpeg (Session 73)
        # Parse parameters
        video_id = request.POST.get('video_id', '').strip()
        style = request.POST.get('style', 'cinematic_warm')
        project_name = request.POST.get('project_name', f'Color_Grade_{int(time.time())}')

        if not video_id:
            return JsonResponse({
                'success': False,
                'error_message': 'video_id is required'
            }, status=400)

        logger.info(f"🎨 Applying {style} color grading to video {video_id}")

        # Session 128: Hybrid ID resolution (numeric or UUID)
        try:
            if video_id.isdigit():
                # Sequential number - resolve to UUID
                seq_num = int(video_id)
                video = VideoHistory.objects.filter(user=request.user).order_by('created_at')[seq_num - 1]
            else:
                # UUID
                video = VideoHistory.objects.get(id=video_id, user=request.user)
        except (VideoHistory.DoesNotExist, IndexError):
            return JsonResponse({
                'success': False,
                'error_message': f'Video {video_id} not found'
            }, status=404)

        # Create temporary directory
        temp_dir = Path('/tmp/davinci_color')
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Download source video
        source_path = temp_dir / f"source_{video_id}.mp4"
        if video.video_url.startswith('/media/'):
            local_file = Path(video.video_url.lstrip('/'))
            shutil.copy2(local_file, source_path)
        else:
            response = requests.get(video.video_url, timeout=30)
            source_path.write_bytes(response.content)

        logger.info(f"✅ Source video downloaded")

        # Session 73: Use ffmpeg for color grading (much simpler than DaVinci!)
        # Session 81: Fixed invalid curves presets - using valid ffmpeg syntax
        # Color grading filter presets
        color_filters = {
            'cinematic_warm': 'eq=contrast=1.1:brightness=0.05:saturation=1.2,colortemperature=5500',  # Warm orange tones
            'cinematic_cool': 'eq=contrast=1.1:saturation=1.1,colortemperature=9000',  # Cool blue tones
            'vintage': 'eq=contrast=1.2:saturation=0.8,curves=vintage,noise=alls=10:allf=t',  # Film look with grain
            'modern': 'eq=contrast=1.05:brightness=0.02:saturation=1.05',  # Clean and crisp
            'high_contrast': 'eq=contrast=1.3:brightness=0.0:saturation=1.1',  # Bold dramatic look
            'soft': 'eq=contrast=0.9:brightness=0.03:saturation=0.85,curves=lighter',  # Muted gentle tones (lighter is valid)
            'vibrant': 'eq=contrast=1.15:saturation=1.5:brightness=0.02'  # Saturated colors
        }

        # Get the filter for the requested style
        color_filter = color_filters.get(style, color_filters['cinematic_warm'])

        # Create output path
        safe_project_name = re.sub(r'[^\w\s-]', '', project_name).replace(' ', '_')
        output_path = str(temp_dir / f"{safe_project_name}_graded.mp4")

        logger.info(f"🎨 Using ffmpeg for color grading: {style}")
        logger.info(f"🎬 Filter: {color_filter}")

        # Build ffmpeg command for color grading
        import subprocess

        ffmpeg_cmd = [
            'ffmpeg',
            '-i', str(source_path),
            '-vf', color_filter,
            '-c:a', 'copy',  # Copy audio without re-encoding
            '-y',  # Overwrite output
            output_path
        ]

        logger.info(f"🎬 Running ffmpeg color grading...")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg error: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error_message': f'Color grading failed: {result.stderr[:200]}'
            }, status=500)

        logger.info(f"✅ Color grading complete!")

        # Create a simple render result (ffmpeg already did the work!)
        from content.davinci_provider import DaVinciRenderResult
        render_result = DaVinciRenderResult(
            success=True,
            video_path=output_path,
            project_name=project_name
        )

        if render_result.success:
            # Save to database
            media_dir = Path('media/generated_videos')
            media_dir.mkdir(parents=True, exist_ok=True)

            unique_id = uuid.uuid4().hex[:8]
            filename = f"color_graded_{unique_id}.mp4"
            destination = media_dir / filename

            shutil.copy2(output_path, destination)

            from core.services.workspace_resolver import get_active_workspace
            video_history = VideoHistory.objects.create(
                user=request.user,
                prompt=f"{style} color grading on {video.prompt[:50]}",
                model_used="DaVinci Resolve Studio",
                video_type="color_graded",
                duration=video.duration or 8,
                status='completed',
                video_url=f"/media/generated_videos/{filename}",
                workspace=get_active_workspace(request.user),
            )

            # Session 142: Track agent contribution
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=video_history,
                    project=None,
                    contribution_type='generation',
                    task_description="Generated video using VideoAgent",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for video {{ video_history.id }}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")
                # Don't fail content creation if contribution tracking fails

            video_url = request.build_absolute_uri(video_history.video_url)

            return JsonResponse({
                'success': True,
                'video_url': video_url,
                'video_id': str(video_history.id),
                'message': f'{style} color grading applied successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error_message': render_result.error_message
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Color grading error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_audio_to_video_endpoint(request):
    """
    POST /api/v1/davinci/add-audio-to-video/
    Add background music/audio to a video using DaVinci Resolve
    Session 73: Voice-controlled audio mixing!

    Form Data:
        - video_id: UUID of source video (required)
        - audio_file: Audio file to mix (required)
        - audio_volume: Volume 0.0-1.0 (default: 0.3)
        - project_name: Optional project name

    Returns:
        {
            'success': bool,
            'video_url': str,
            'video_id': str,
            'message': str
        }
    """
    try:
        davinci = get_davinci_provider()

        if not davinci.studio_available:
            return JsonResponse({
                'success': False,
                'error_message': 'DaVinci Resolve Studio required.'
            }, status=503)

        # Parse parameters
        video_id = request.POST.get('video_id', '').strip()
        audio_file = request.FILES.get('audio_file')
        audio_volume = float(request.POST.get('audio_volume', 0.3))
        project_name = request.POST.get('project_name', f'Audio_Mix_{int(time.time())}')

        if not video_id or not audio_file:
            return JsonResponse({
                'success': False,
                'error_message': 'video_id and audio_file are required'
            }, status=400)

        # Validate volume
        audio_volume = max(0.0, min(1.0, audio_volume))

        logger.info(f"🎵 Adding audio {audio_file.name} to video {video_id} at {audio_volume * 100}% volume")

        # Get source video
        video = VideoHistory.objects.get(id=video_id, user=request.user)

        # Create temporary directory
        temp_dir = Path('/tmp/davinci_audio')
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Download source video
        source_path = temp_dir / f"source_{video_id}.mp4"
        if video.video_url.startswith('/media/'):
            local_file = Path(video.video_url.lstrip('/'))
            shutil.copy2(local_file, source_path)
        else:
            response = requests.get(video.video_url, timeout=30)
            source_path.write_bytes(response.content)

        # Save uploaded audio file
        audio_path = temp_dir / f"audio_{int(time.time())}{Path(audio_file.name).suffix}"
        with open(audio_path, 'wb+') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        logger.info(f"✅ Source video and audio downloaded")

        # Session 73: Use ffmpeg for audio mixing (much simpler than DaVinci!)
        # Create output path
        safe_project_name = re.sub(r'[^\w\s-]', '', project_name).replace(' ', '_')
        output_path = str(temp_dir / f"{safe_project_name}_with_audio.mp4")

        logger.info(f"🎵 Using ffmpeg for audio mixing at {audio_volume * 100}% volume")

        # Build ffmpeg command for audio mixing
        # Mixing strategy: Original video audio + new background audio
        import subprocess

        ffmpeg_cmd = [
            'ffmpeg',
            '-i', str(source_path),  # Video input (with original audio)
            '-i', str(audio_path),   # Background music input
            '-filter_complex', f'[1:a]volume={audio_volume}[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2',
            '-c:v', 'copy',  # Copy video without re-encoding
            '-y',  # Overwrite output
            output_path
        ]

        logger.info(f"🎬 Running ffmpeg audio mixing...")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg error: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error_message': f'Audio mixing failed: {result.stderr[:200]}'
            }, status=500)

        logger.info(f"✅ Audio mixing complete!")

        # Create a simple render result (ffmpeg already did the work!)
        from content.davinci_provider import DaVinciRenderResult
        render_result = DaVinciRenderResult(
            success=True,
            video_path=output_path,
            project_name=project_name
        )

        if render_result.success:
            # Save to database
            media_dir = Path('media/generated_videos')
            media_dir.mkdir(parents=True, exist_ok=True)

            unique_id = uuid.uuid4().hex[:8]
            filename = f"audio_mix_{unique_id}.mp4"
            destination = media_dir / filename

            shutil.copy2(output_path, destination)

            from core.services.workspace_resolver import get_active_workspace
            video_history = VideoHistory.objects.create(
                user=request.user,
                prompt=f"Audio mixing: {audio_file.name} on {video.prompt[:50]}",
                model_used="DaVinci Resolve Studio",
                video_type="audio_mixed",
                duration=video.duration or 8,
                status='completed',
                video_url=f"/media/generated_videos/{filename}",
                workspace=get_active_workspace(request.user),
            )

            # Session 142: Track agent contribution
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=video_history,
                    project=None,
                    contribution_type='generation',
                    task_description="Generated video using VideoAgent",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for video {{ video_history.id }}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")
                # Don't fail content creation if contribution tracking fails

            video_url = request.build_absolute_uri(video_history.video_url)

            return JsonResponse({
                'success': True,
                'video_url': video_url,
                'video_id': str(video_history.id),
                'message': f'Audio "{audio_file.name}" mixed successfully at {int(audio_volume * 100)}% volume!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error_message': render_result.error_message
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Audio mixing error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)
