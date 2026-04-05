"""
Video Editing Service — Agent-callable ffmpeg operations.

Extracted from core/views_video.py so VideoEditingAgent can call real
ffmpeg operations without going through Django request/response cycle.

Each function takes (user, ...) and returns a plain dict:
    {'success': True/False, 'video_id': ..., 'video_url': ..., ...}
"""

import logging
import os
import shutil
import subprocess
import tempfile

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _resolve_video(user, video_id):
    """Resolve a video_id (UUID string or 1-based numeric) to a VideoHistory."""
    from content.models import VideoHistory

    if isinstance(video_id, str):
        video_id = video_id.strip().strip('"').strip("'")

    # Try UUID first
    try:
        import uuid as uuid_module
        video_uuid = uuid_module.UUID(video_id)
        return VideoHistory.objects.filter(id=video_uuid, user=user).first()
    except (ValueError, AttributeError, TypeError):
        pass

    # Try numeric ID (1-based index)
    try:
        numeric_id = int(video_id)
        if numeric_id < 1:
            return None
        videos = VideoHistory.objects.filter(user=user).order_by('created_at')
        if numeric_id > videos.count():
            return None
        return videos[numeric_id - 1]
    except (ValueError, TypeError):
        return None


def _get_input_path(video):
    """
    Return a local file path for the video.

    For CDN/remote URLs the file is downloaded to a temp directory.
    Returns (input_path, temp_dir_or_None).
    Caller MUST clean up temp_dir when done.
    """
    import requests as http_requests

    if not video or not video.video_url:
        return None, None

    url = video.video_url

    # Local /media/ path
    if url.startswith('/media/') or url.startswith('media/'):
        file_path = url.lstrip('/')
        if file_path.startswith('media/'):
            file_path = file_path[6:]
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if os.path.exists(full_path):
            return full_path, None
        return None, None

    # Remote URL — download to temp
    if url.startswith('http://') or url.startswith('https://'):
        from core.utils.url_validator import validate_url_for_download
        is_valid, error = validate_url_for_download(url)
        if not is_valid:
            logger.warning(f"SSRF protection blocked URL: {url} - {error}")
            return None, None

        try:
            resp = http_requests.get(url, stream=True, timeout=60)
            resp.raise_for_status()
            temp_dir = tempfile.mkdtemp()
            input_path = os.path.join(temp_dir, 'input.mp4')
            with open(input_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return input_path, temp_dir
        except Exception as e:
            logger.error(f"Failed to download video: {e}")
            return None, None

    return None, None


def _run_ffmpeg(cmd, timeout=None):
    """Run an ffmpeg command with timeout protection."""
    if timeout is None:
        timeout = getattr(settings, 'FFMPEG_TIMEOUT', 120)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _save_edited_video(user, output_path, output_filename, source_video,
                       video_type, operation_label, prompt, duration=None):
    """
    Create a VideoHistory record for an edited video.

    Returns dict with success/video_id/video_url.
    """
    from content.models import VideoHistory

    if not os.path.exists(output_path):
        return {'success': False, 'error': f'{operation_label} produced no output'}

    project = getattr(source_video, 'project', None)

    from core.services.workspace_resolver import get_active_workspace
    new_video = VideoHistory.objects.create(
        user=user,
        video_type=video_type,
        prompt=prompt,
        duration=duration if duration is not None else source_video.duration,
        model_used=f'ffmpeg_{operation_label}',
        ratio=source_video.ratio,
        status='completed',
        video_url=f'/media/{output_filename}',
        generation_completed=timezone.now(),
        project=project,
        workspace=get_active_workspace(user),
    )

    # Best-effort agent contribution tracking
    try:
        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
        agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
        AgentContribution.objects.create(
            agent=agent,
            video=new_video,
            project=project,
            contribution_type='editing',
            task_description=f"{operation_label} via VideoEditingAgent",
            execution_time_seconds=0.0,
        )
    except Exception as e:
        logger.warning(f"Could not track agent contribution: {e}")

    return {
        'success': True,
        'video_id': str(new_video.id),
        'video_url': new_video.video_url,
    }


def _cleanup(temp_dir):
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


def _timestamp_str():
    return timezone.now().strftime('%Y%m%d_%H%M%S')


# ---------------------------------------------------------------------------
# 1. Trim
# ---------------------------------------------------------------------------

def trim_video(user, video_id, start_time=0, end_time=None, duration=None):
    """Trim a video to [start_time, end_time] using ffmpeg -c copy."""
    video = _resolve_video(user, video_id)
    if not video:
        return {'success': False, 'error': f'Video {video_id} not found'}
    if video.status != 'completed':
        return {'success': False, 'error': f'Video is {video.status}, must be completed'}

    # Determine end_time from duration if needed
    if end_time is None and duration is not None:
        end_time = float(start_time) + float(duration)
    if end_time is None:
        return {'success': False, 'error': 'end_time or duration is required'}

    start_seconds = float(start_time)
    end_seconds = float(end_time)
    if start_seconds < 0:
        start_seconds = 0
    if end_seconds <= start_seconds:
        return {'success': False, 'error': f'end_time ({end_seconds}s) must be > start_time ({start_seconds}s)'}

    # Clamp to actual duration
    if video.duration and end_seconds > video.duration:
        end_seconds = video.duration

    input_path, temp_dir = _get_input_path(video)
    if not input_path:
        return {'success': False, 'error': 'Could not access video file'}

    try:
        trimmed_duration = end_seconds - start_seconds
        ts = _timestamp_str()
        output_filename = f"videos/{user.id}/trimmed_{start_seconds}-{end_seconds}s_{ts}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cmd = [
            'ffmpeg',
            '-ss', str(start_seconds),
            '-i', input_path,
            '-to', str(trimmed_duration),
            '-c', 'copy',
            '-y', output_path,
        ]
        result = _run_ffmpeg(cmd)

        if result.returncode != 0:
            return {'success': False, 'error': f'ffmpeg trim failed: {result.stderr[:200]}'}

        saved = _save_edited_video(
            user, output_path, output_filename, video,
            video_type='trimmed',
            operation_label='trim',
            prompt=f"Trimmed {start_seconds}s-{end_seconds}s from video {video.id}",
            duration=trimmed_duration,
        )
        saved.update({
            'start_time': start_seconds,
            'end_time': end_seconds,
            'duration': trimmed_duration,
            'message': f'Video trimmed to {start_seconds}s-{end_seconds}s ({trimmed_duration}s)',
            'operation': 'trim',
        })
        return saved
    finally:
        _cleanup(temp_dir)


# ---------------------------------------------------------------------------
# 2. Add text overlay
# ---------------------------------------------------------------------------

def add_text_overlay(user, video_id, text, position='bottom',
                     font_size=48, color='white', start_time=0, end_time=None):
    """Add a text overlay to a video using ffmpeg drawtext filter."""
    video = _resolve_video(user, video_id)
    if not video:
        return {'success': False, 'error': f'Video {video_id} not found'}
    if video.status != 'completed':
        return {'success': False, 'error': f'Video is {video.status}, must be completed'}

    input_path, temp_dir = _get_input_path(video)
    if not input_path:
        return {'success': False, 'error': 'Could not access video file'}

    try:
        ts = _timestamp_str()
        output_filename = f"videos/{user.id}/text_{ts}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        font_size = max(12, min(200, int(font_size)))
        margin = 20

        # Map position names to ffmpeg drawtext x:y expressions
        # Also accept hyphenated names from tool schema (top-left → top_left)
        pos_key = position.replace('-', '_')
        position_map = {
            'top': f'x=(w-text_w)/2:y={margin}',
            'center': 'x=(w-text_w)/2:y=(h-text_h)/2',
            'bottom': f'x=(w-text_w)/2:y=h-text_h-{margin}',
            'top_left': f'x={margin}:y={margin}',
            'top_right': f'x=w-text_w-{margin}:y={margin}',
            'bottom_left': f'x={margin}:y=h-text_h-{margin}',
            'bottom_right': f'x=w-text_w-{margin}:y=h-text_h-{margin}',
        }
        pos_expr = position_map.get(pos_key, position_map['bottom'])

        # Escape text for ffmpeg drawtext
        escaped = text.replace("'", "'\\''").replace(":", "\\:").replace("\\", "\\\\")

        drawtext = f"drawtext=text='{escaped}':fontsize={font_size}:fontcolor={color}:{pos_expr}"

        # Time-based enable
        if start_time and start_time > 0:
            vid_end = end_time if end_time else (video.duration or 9999)
            drawtext += f":enable='between(t,{start_time},{vid_end})'"
        elif end_time:
            drawtext += f":enable='between(t,0,{end_time})'"

        cmd = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-vf', drawtext,
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-c:a', 'copy',
            output_path,
        ]

        result = _run_ffmpeg(cmd)
        if result.returncode != 0:
            return {'success': False, 'error': f'ffmpeg drawtext failed: {result.stderr[:200]}'}

        saved = _save_edited_video(
            user, output_path, output_filename, video,
            video_type='edited',
            operation_label='add_text',
            prompt=f"Added text '{text[:50]}' to video {video.id}",
        )
        saved.update({
            'text': text,
            'position': position,
            'message': f"Text overlay '{text[:30]}' added at {position}",
            'operation': 'add_text',
        })
        return saved
    finally:
        _cleanup(temp_dir)


# ---------------------------------------------------------------------------
# 3. Apply effect
# ---------------------------------------------------------------------------

EFFECT_FILTERS = {
    'cinematic': "eq=contrast=1.1:saturation=0.9,curves=all='0/0 0.5/0.4 1/1'",
    'vintage': "eq=contrast=0.9:saturation=0.7,curves=r='0/0.1 1/0.9':g='0/0.1 1/0.9':b='0/0.2 1/0.8'",
    'vibrant': "eq=contrast=1.2:saturation=1.3:brightness=0.05",
    'noir': "eq=contrast=1.3:saturation=0,curves=all='0/0 0.5/0.5 1/1'",
    'warm': "eq=saturation=1.1,colortemperature=7500",
    'cool': "eq=saturation=1.1,colortemperature=5000",
    'blur': "boxblur=5:1",
    'sharpen': "unsharp=5:5:1.5:5:5:0.0",
}


def _build_effect_filter(effect, intensity=0.5):
    """Build an ffmpeg filter string for the given effect."""
    base = EFFECT_FILTERS.get(effect, EFFECT_FILTERS['cinematic'])
    # For effects that scale with intensity, build dynamically
    if effect == 'vibrant':
        sat = 1.0 + float(intensity) * 0.5
        base = f"eq=contrast=1.2:saturation={sat}:brightness=0.05"
    elif effect == 'noir':
        contrast = 1.2 + float(intensity) * 0.3
        mid = 0.45 + float(intensity) * 0.1
        base = f"eq=contrast={contrast}:saturation=0,curves=all='0/0 0.5/{mid} 1/1'"
    elif effect == 'warm':
        temp = 6500 + float(intensity) * 1500
        base = f"eq=saturation=1.1,colortemperature={temp}"
    elif effect == 'cool':
        temp = 6500 - float(intensity) * 2000
        base = f"eq=saturation=1.1,colortemperature={temp}"
    return base


def apply_effect(user, video_id, effect, intensity=0.5):
    """Apply a color-grading / visual effect via ffmpeg."""
    valid_effects = list(EFFECT_FILTERS.keys())
    if effect not in valid_effects:
        return {'success': False, 'error': f"Invalid effect. Choose from: {', '.join(valid_effects)}"}

    intensity = max(0.0, min(1.0, float(intensity)))

    video = _resolve_video(user, video_id)
    if not video:
        return {'success': False, 'error': f'Video {video_id} not found'}
    if video.status != 'completed':
        return {'success': False, 'error': f'Video is {video.status}, must be completed'}

    input_path, temp_dir = _get_input_path(video)
    if not input_path:
        return {'success': False, 'error': 'Could not access video file'}

    try:
        ts = _timestamp_str()
        output_filename = f"videos/{user.id}/{effect}_{ts}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        filter_chain = _build_effect_filter(effect, intensity)

        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', filter_chain,
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-c:a', 'copy',
            '-y', output_path,
        ]

        result = _run_ffmpeg(cmd)
        if result.returncode != 0:
            return {'success': False, 'error': f'ffmpeg effect failed: {result.stderr[:200]}'}

        saved = _save_edited_video(
            user, output_path, output_filename, video,
            video_type='enhanced',
            operation_label=effect,
            prompt=f"{effect.capitalize()} effect applied to video {video.id}",
        )
        saved.update({
            'effect': effect,
            'intensity': intensity,
            'message': f'{effect.capitalize()} effect applied successfully',
            'operation': 'add_effects',
        })
        return saved
    finally:
        _cleanup(temp_dir)


# ---------------------------------------------------------------------------
# 4. Extract frame
# ---------------------------------------------------------------------------

def extract_frame(user, video_id, time=0, output_format='png'):
    """Extract a single frame from a video as an image."""
    video = _resolve_video(user, video_id)
    if not video:
        return {'success': False, 'error': f'Video {video_id} not found'}
    if video.status != 'completed':
        return {'success': False, 'error': f'Video is {video.status}, must be completed'}

    timestamp = max(0.0, float(time))
    if video.duration and timestamp > video.duration:
        timestamp = max(0, video.duration - 0.1)

    fmt = output_format.lower()
    if fmt not in ('png', 'jpg', 'jpeg'):
        fmt = 'png'
    extension = 'jpg' if fmt in ('jpg', 'jpeg') else 'png'

    input_path, temp_dir = _get_input_path(video)
    if not input_path:
        return {'success': False, 'error': 'Could not access video file'}

    try:
        ts = _timestamp_str()
        output_filename = f"images/{user.id}/frame_{ts}_{timestamp}s.{extension}"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cmd = [
            'ffmpeg',
            '-ss', str(timestamp),
            '-i', input_path,
            '-frames:v', '1',
            '-q:v', '2',
            '-y', output_path,
        ]

        result = _run_ffmpeg(cmd)
        if result.returncode != 0:
            return {'success': False, 'error': f'ffmpeg frame extraction failed: {result.stderr[:200]}'}

        if not os.path.exists(output_path):
            return {'success': False, 'error': 'Frame extraction produced no output'}

        # Save as ImageHistory
        from content.models import ImageHistory
        project = getattr(video, 'project', None)

        from core.services.workspace_resolver import get_active_workspace
        extracted_image = ImageHistory.objects.create(
            user=user,
            prompt=f"Frame extracted at {timestamp}s from video {video.id}",
            image_type='generated',
            filename=os.path.basename(output_filename),
            file_path=f'/media/{output_filename}',
            parameters={
                'source_video_id': str(video.id),
                'timestamp': timestamp,
                'operation': 'frame_extraction',
            },
            project=project,
            workspace=get_active_workspace(user),
        )

        # Best-effort contribution tracking
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=extracted_image,
                project=project,
                contribution_type='extraction',
                task_description=f"Extracted frame at {timestamp}s via VideoEditingAgent",
                execution_time_seconds=0.0,
            )
        except Exception as e:
            logger.warning(f"Could not track agent contribution: {e}")

        return {
            'success': True,
            'image_id': str(extracted_image.id),
            'image_url': extracted_image.file_path,
            'timestamp': timestamp,
            'format': extension,
            'message': f'Frame extracted at {timestamp}s',
            'operation': 'extract_frame',
        }
    finally:
        _cleanup(temp_dir)


# ---------------------------------------------------------------------------
# 5. Concatenate
# ---------------------------------------------------------------------------

def concatenate_videos(user, video_ids, transition='none', transition_duration=0.5):
    """Join multiple videos using ffmpeg concat demuxer (re-encode fallback)."""
    if not video_ids or len(video_ids) < 2:
        return {'success': False, 'error': 'At least 2 video_ids are required'}

    videos = []
    source_paths = []
    temp_dirs = []

    for vid in video_ids:
        video = _resolve_video(user, vid)
        if not video:
            # Clean up any already-downloaded temps
            for td in temp_dirs:
                _cleanup(td)
            return {'success': False, 'error': f'Video {vid} not found'}
        videos.append(video)

        input_path, temp_dir = _get_input_path(video)
        if temp_dir:
            temp_dirs.append(temp_dir)
        if not input_path:
            for td in temp_dirs:
                _cleanup(td)
            return {'success': False, 'error': f'Source file not found for video {vid}'}
        source_paths.append(input_path)

    try:
        ts = _timestamp_str()
        output_filename = f"videos/concatenated/combined_{len(videos)}_videos_{ts}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create concat file list
        concat_list_path = os.path.join(
            settings.MEDIA_ROOT, f"videos/concatenated/concat_list_{ts}.txt"
        )
        os.makedirs(os.path.dirname(concat_list_path), exist_ok=True)

        with open(concat_list_path, 'w') as f:
            for path in source_paths:
                f.write(f"file '{path}'\n")

        # Try fast concat demuxer first (lossless for same-codec)
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', concat_list_path,
            '-c', 'copy',
            '-y', output_path,
        ]
        result = _run_ffmpeg(cmd)

        # Fallback: re-encode with filter_complex
        if result.returncode != 0:
            input_args = []
            filter_parts = []
            for i, path in enumerate(source_paths):
                input_args.extend(['-i', path])
                filter_parts.append(f'[{i}:v:0][{i}:a:0]')

            filter_complex = (
                f"{''.join(filter_parts)}concat=n={len(source_paths)}:v=1:a=1[v][a]"
            )
            cmd = ['ffmpeg'] + input_args + [
                '-filter_complex', filter_complex,
                '-map', '[v]', '-map', '[a]',
                '-y', output_path,
            ]
            result = _run_ffmpeg(cmd)

            # Last fallback: video-only (no audio streams)
            if result.returncode != 0:
                filter_parts = [f'[{i}:v:0]' for i in range(len(source_paths))]
                filter_complex = (
                    f"{''.join(filter_parts)}concat=n={len(source_paths)}:v=1:a=0[v]"
                )
                cmd = ['ffmpeg'] + input_args + [
                    '-filter_complex', filter_complex,
                    '-map', '[v]',
                    '-y', output_path,
                ]
                result = _run_ffmpeg(cmd)

        # Clean up concat list
        try:
            os.remove(concat_list_path)
        except OSError:
            pass

        if result.returncode != 0:
            return {'success': False, 'error': f'ffmpeg concat failed: {result.stderr[:200]}'}

        total_duration = sum(v.duration or 0 for v in videos)

        from content.models import VideoHistory
        project = getattr(videos[0], 'project', None)

        from core.services.workspace_resolver import get_active_workspace
        concat_video = VideoHistory.objects.create(
            user=user,
            video_type='concatenated',
            prompt=f"Concatenated {len(videos)} videos",
            duration=total_duration,
            model_used='ffmpeg_concat',
            ratio=videos[0].ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=timezone.now(),
            project=project,
            workspace=get_active_workspace(user),
        )

        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=concat_video,
                project=project,
                contribution_type='editing',
                task_description=f"Concatenated {len(videos)} videos via VideoEditingAgent",
                execution_time_seconds=0.0,
            )
        except Exception as e:
            logger.warning(f"Could not track agent contribution: {e}")

        return {
            'success': True,
            'video_id': str(concat_video.id),
            'video_url': concat_video.video_url,
            'video_count': len(videos),
            'source_videos': [str(v.id) for v in videos],
            'total_duration': total_duration,
            'message': f'Combined {len(videos)} videos into one ({total_duration}s total)',
            'operation': 'concatenate',
        }
    finally:
        for td in temp_dirs:
            _cleanup(td)


# ---------------------------------------------------------------------------
# 6. Speed change
# ---------------------------------------------------------------------------

def change_speed(user, video_id, speed_factor=1.0, preserve_audio_pitch=True):
    """Change video playback speed using ffmpeg setpts / atempo filters."""
    speed = float(speed_factor)
    if speed <= 0 or speed > 4.0:
        return {'success': False, 'error': 'speed_factor must be between 0.1 and 4.0'}

    video = _resolve_video(user, video_id)
    if not video:
        return {'success': False, 'error': f'Video {video_id} not found'}

    input_path, temp_dir = _get_input_path(video)
    if not input_path:
        return {'success': False, 'error': 'Could not access video file'}

    try:
        ts = _timestamp_str()
        speed_label = f"{speed}x".replace('.', '_')
        output_filename = f"videos/{user.id}/speed_{speed_label}_{ts}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        video_filter = f"setpts=PTS/{speed}"

        # Probe for audio stream
        has_audio = False
        try:
            probe_cmd = [
                'ffprobe', '-v', 'error', '-select_streams', 'a:0',
                '-show_entries', 'stream=codec_type', '-of', 'csv=p=0',
                input_path,
            ]
            probe_result = subprocess.run(
                probe_cmd, capture_output=True, text=True, timeout=30
            )
            has_audio = 'audio' in probe_result.stdout
        except Exception:
            pass

        if preserve_audio_pitch and has_audio:
            # Build atempo chain — atempo only supports 0.5–2.0
            atempo_parts = []
            remaining = speed
            if speed < 0.5:
                while remaining < 0.5:
                    atempo_parts.append('atempo=0.5')
                    remaining *= 2
                if remaining != 1.0:
                    atempo_parts.append(f'atempo={remaining}')
            elif speed > 2.0:
                while remaining > 2.0:
                    atempo_parts.append('atempo=2.0')
                    remaining /= 2
                if remaining != 1.0:
                    atempo_parts.append(f'atempo={remaining}')
            else:
                atempo_parts.append(f'atempo={speed}')

            audio_filter = ','.join(atempo_parts)
            cmd = [
                'ffmpeg', '-i', input_path,
                '-filter_complex',
                f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
                '-map', '[v]', '-map', '[a]',
                '-y', output_path,
            ]
        else:
            # No audio preservation
            cmd = [
                'ffmpeg', '-i', input_path,
                '-vf', video_filter,
                '-an',
                '-y', output_path,
            ]

        result = _run_ffmpeg(cmd)
        if result.returncode != 0:
            return {'success': False, 'error': f'ffmpeg speed change failed: {result.stderr[:200]}'}

        if not os.path.exists(output_path):
            return {'success': False, 'error': 'Speed change produced no output'}

        original_duration = video.duration or 5
        new_duration = original_duration / speed

        saved = _save_edited_video(
            user, output_path, output_filename, video,
            video_type='speed_change',
            operation_label='speed',
            prompt=f"Speed {speed}x of video {video.id}",
            duration=new_duration,
        )
        speed_description = (
            "slow motion" if speed < 1.0
            else "sped up" if speed > 1.0
            else "normal speed"
        )
        saved.update({
            'speed': speed,
            'original_duration': original_duration,
            'new_duration': new_duration,
            'message': f'Video speed changed to {speed}x ({speed_description})',
            'operation': 'speed_change',
        })
        return saved
    finally:
        _cleanup(temp_dir)
