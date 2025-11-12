"""
Video Agent - Session 81
========================

Specialized agent for video operations.
Can query Audio Agent for audio files and add them to videos.

Features:
- Video-to-video transformation
- Text overlay addition
- Color grading
- Music/audio mixing (queries AudioAgent)
- Video chaining

Example Usage:
    video_agent = VideoAgent(user=request.user)

    # Add music to video (auto-queries AudioAgent)
    result = video_agent.add_music_to_video(
        video_selection='last',
        audio_url=None  # Will query AudioAgent automatically
    )
"""

from __future__ import annotations

import logging
import os
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

from agents.models import UnifiedAgentTemplate, AgentExecution
from intelligence.shared_memory import AgentMemoryInterface
from intelligence.agent_query_protocol import query_protocol

logger = logging.getLogger(__name__)
User = get_user_model()


class VideoAgent:
    """
    Specialized agent for video operations.
    Can query other agents for required data.
    """

    def __init__(self, user: Optional[User] = None):
        """
        Initialize Video Agent.

        Args:
            user: User who initiated the agent (optional)
        """
        self.user = user
        self.agent_name = 'VideoAgent'

        # Initialize memory interface for state management
        self.memory = AgentMemoryInterface(agent_id='video_agent')

        # Get or create agent template
        self.template = self._get_or_create_template()

        logger.info(f"🎬 Video Agent initialized for user: {user.username if user else 'system'}")

    def _get_or_create_template(self) -> UnifiedAgentTemplate:
        """Get or create VideoAgent template in database"""
        try:
            agent = UnifiedAgentTemplate.objects.get(name=self.agent_name)
            logger.debug(f"Using existing VideoAgent template: {agent.id}")
            return agent

        except UnifiedAgentTemplate.DoesNotExist:
            # Create new VideoAgent template
            agent = UnifiedAgentTemplate.objects.create(
                name=self.agent_name,
                display_name='Video Operations Agent',
                description='Specialized agent for video operations including editing, color grading, text overlays, and audio mixing',
                specialization='video_operations',
                capabilities=[
                    'add_music_to_video',
                    'add_text_to_video',
                    'apply_color_grade',
                    'chain_videos',
                    'video_to_video_transform'
                ],
                routing_keywords=[
                    'video', 'edit', 'music', 'audio', 'text', 'overlay',
                    'color', 'grade', 'chain', 'combine', 'mix'
                ],
                system_prompt=(
                    "You are the Video Operations Agent. You specialize in video editing operations "
                    "including adding audio/music, text overlays, color grading, and video chaining. "
                    "You can query the Audio Agent for recently generated audio files."
                ),
                required_tools=['davinci_resolve', 'ffmpeg'],
                is_active=True,
                metadata={
                    'query_handlers': {},
                    'created_by': 'session_81',
                    'version': '1.0.0'
                }
            )

            logger.info(f"✅ Created new VideoAgent template: {agent.id}")

            return agent

    def _save_rendered_video_to_media(self, temp_path: str, prefix: str = 'davinci') -> str:
        """
        Copy rendered video from temp folder to Django media folder.

        Args:
            temp_path: Path to temporary rendered video (e.g., /tmp/davinci_render_*.mp4)
            prefix: Filename prefix (default: 'davinci')

        Returns:
            Media URL path (e.g., /media/videos/davinci_123456.mp4)
        """
        try:
            import time

            # Create videos directory if it doesn't exist
            videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
            os.makedirs(videos_dir, exist_ok=True)

            # Generate unique filename
            timestamp = int(time.time())
            ext = os.path.splitext(temp_path)[1] or '.mp4'
            filename = f'{prefix}_{timestamp}{ext}'

            # Copy to media folder
            dest_path = os.path.join(videos_dir, filename)
            shutil.copy2(temp_path, dest_path)

            # Return media URL
            media_url = f'/media/videos/{filename}'
            logger.info(f"✅ Video copied to media folder: {media_url}")

            # Clean up temp file
            try:
                os.remove(temp_path)
                logger.debug(f"🗑️ Removed temp file: {temp_path}")
            except Exception as e:
                logger.warning(f"⚠️ Could not remove temp file {temp_path}: {e}")

            return media_url

        except Exception as e:
            logger.error(f"❌ Failed to save video to media: {e}", exc_info=True)
            # Session 84 fix: Don't return temp path as it creates bad database records!
            # Raise exception so the whole operation fails properly
            raise Exception(f"Failed to save video to media folder: {e}")

    def add_music_to_video(
        self,
        video_selection: str = 'last',
        audio_url: Optional[str] = None,
        audio_volume: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add audio/music to video.
        If audio_url not provided, queries AudioAgent for most recent audio.

        Args:
            video_selection: Which video to use ('last', 'video_id:123')
            audio_url: Audio URL (if None, queries AudioAgent)
            audio_volume: Volume level (0.0 to 1.0)
            **kwargs: Additional parameters

        Returns:
            Result dictionary with status, video_url, etc.
        """
        try:
            # Session 82 fix: Get video FIRST so we have display params for ALL error paths
            video = self._get_video_by_selection(video_selection)

            if not video:
                return {
                    'success': False,
                    'error': f'No video found for selection: {video_selection}'
                }

            # Get video display info early
            try:
                video_prompt = video.prompt if hasattr(video, 'prompt') and video.prompt else f"Video #{video.id}"
                video_id_str = str(video.id) if video.id else "unknown"
            except Exception as e:
                logger.warning(f"⚠️ Error getting video details: {e}")
                video_prompt = "Your video"
                video_id_str = "unknown"

            # If no audio_url provided, query AudioAgent
            if not audio_url:
                logger.info("🔍 VideoAgent querying AudioAgent for recent audio...")

                # Get AudioAgent instance
                try:
                    audio_agent_template = UnifiedAgentTemplate.objects.get(name='AudioAgent')
                except UnifiedAgentTemplate.DoesNotExist:
                    # Session 82: Add display params even on error
                    return {
                        'success': False,
                        'error': 'AudioAgent not found. Please ensure AudioAgent is initialized.',
                        'audio_volume': audio_volume,
                        'music_style': kwargs.get('music_style', 'custom audio'),
                        'video_prompt': video_prompt,
                        'video_id': video_id_str,
                        'message': 'AudioAgent not found',
                        'instructions': 'Please ensure AudioAgent is initialized.'
                    }

                # Query for most recent audio
                audio_data = query_protocol.query_agent(
                    from_agent=self.template,
                    to_agent=audio_agent_template,
                    query_type='get_most_recent',
                    timeout=5
                )

                # Try to get audio_url from query result
                if audio_data and isinstance(audio_data, dict):
                    # Direct access from agent method (synchronous)
                    audio_url = audio_data.get('audio_url')
                    logger.info(f"✅ VideoAgent received audio URL from direct call: {audio_url}")

                # If still no audio_url, try using shared memory directly as fallback
                if not audio_url:
                    logger.info("🔍 Trying direct memory access as fallback...")

                    from intelligence.shared_memory import shared_memory
                    audio_data = shared_memory.retrieve_memory(
                        entity_type='agent',
                        entity_id='audio_agent',
                        memory_type='most_recent_audio'
                    )

                    if audio_data and audio_data.get('content'):
                        audio_url = audio_data['content'].get('audio_url')
                        logger.info(f"✅ VideoAgent received audio URL from shared memory: {audio_url}")

                if not audio_url:
                    # Session 82: Add display params even on error
                    return {
                        'success': False,
                        'error': 'No recent audio found. Please generate audio first using "Generate speech" or "Create sound effect".',
                        'audio_volume': audio_volume,
                        'music_style': kwargs.get('music_style', 'custom audio'),
                        'video_prompt': video_prompt,
                        'video_id': video_id_str,
                        'message': 'No recent audio found',
                        'instructions': 'Please generate audio first using "Generate speech" or "Create sound effect".'
                    }

            logger.info(f"🎵 VideoAgent adding audio to video: {audio_url[:50]}...")

            # Call DaVinci backend to add music
            from content.davinci_provider import get_davinci_provider
            davinci = get_davinci_provider()

            result = davinci.add_music_to_video(
                video_url=video.video_url,
                audio_url=audio_url,
                audio_volume=audio_volume,
                output_format='mp4'
            )

            # Session 83: If ffmpeg created a temp file, move it to media and create database record
            if result.get('success') and result.get('video_url'):
                temp_path = result['video_url']

                # Check if this is a temp file (ffmpeg output)
                if temp_path.startswith('/tmp/'):
                    logger.info(f"📦 Saving mixed video to media directory...")

                    import os
                    import shutil
                    from django.core.files import File
                    from content.models import VideoHistory

                    # Create media/videos directory if needed
                    videos_dir = os.path.join('media', 'videos')
                    os.makedirs(videos_dir, exist_ok=True)

                    # Generate filename
                    import uuid
                    filename = f"mixed_video_{uuid.uuid4().hex[:8]}.mp4"
                    dest_path = os.path.join(videos_dir, filename)

                    # Move file from temp to media
                    shutil.move(temp_path, dest_path)
                    logger.info(f"✅ Moved video to: {dest_path}")

                    # Create VideoHistory record
                    video_record = VideoHistory.objects.create(
                        user=self.user,
                        video_url=f"/{dest_path}",  # Relative URL for frontend
                        prompt=f"Audio-mixed version of: {video_prompt[:100]}",
                        model_used='ffmpeg',  # Correct field name
                        video_type='audio_mixed',
                        status='completed',
                        metadata={
                            'original_video': video.video_url,
                            'audio_source': audio_url,
                            'audio_volume': audio_volume,
                            'method': 'ffmpeg_audio_mixing'
                        }
                    )

                    logger.info(f"✅ Created VideoHistory record: {video_record.id}")

                    # Update result with proper URL
                    result['video_url'] = f"/{dest_path}"
                    result['video_id'] = video_record.id

            # Session 82 fix: ALWAYS add display parameters (even on failure)
            result['audio_volume'] = audio_volume
            result['music_style'] = kwargs.get('music_style', 'custom audio')

            # Get video prompt and ID safely
            try:
                video_prompt = video.prompt if hasattr(video, 'prompt') and video.prompt else f"Video #{video.id}"
                video_id_str = str(video.id) if video.id else "unknown"
            except Exception as e:
                logger.warning(f"⚠️ Error getting video details: {e}")
                video_prompt = "Your video"
                video_id_str = "unknown"

            result['video_prompt'] = video_prompt
            result['video_id'] = video_id_str

            logger.info(f"🔍 Session 82 DEBUG: Display params set - audio_volume={audio_volume}, music_style={result['music_style']}, video_prompt={video_prompt}, video_id={video_id_str}")

            if not result.get('success'):
                # On failure, add error-specific message but keep display params
                result['message'] = result.get('error', 'Failed to add audio to video')
                result['instructions'] = 'Please try again or check DaVinci Resolve connection.'
                return result

            # Store result in memory
            video_data = {
                'video_url': result.get('video_url'),
                'original_video_id': str(video.id),
                'audio_url': audio_url,
                'audio_volume': audio_volume,
                'type': 'music_added',
                'user_id': self.user.id if self.user else None,
                'created_at': timezone.now().isoformat()
            }

            self.memory.remember('most_recent_video', video_data)

            logger.info(f"✅ VideoAgent added music to video successfully")

            # Session 82 fix: Add success-specific messages (display params already added above)
            result['message'] = f"✅ Audio successfully added to video!"
            result['instructions'] = f"The video has been rendered with audio at {int(audio_volume * 100)}% volume."

            # Session 82 DEBUG: Log what we're returning
            logger.info(f"🔍 DEBUG: Returning result with display parameters:")
            logger.info(f"  - audio_volume: {result.get('audio_volume')}")
            logger.info(f"  - music_style: {result.get('music_style')}")
            logger.info(f"  - video_prompt: {result.get('video_prompt')}")
            logger.info(f"  - video_id: {result.get('video_id')}")
            logger.info(f"  - message: {result.get('message')}")
            logger.info(f"  - instructions: {result.get('instructions')}")
            logger.info(f"  - Full result keys: {list(result.keys())}")

            return result

        except Exception as e:
            logger.error(f"❌ VideoAgent.add_music_to_video failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _get_video_by_selection(self, selection: str):
        """
        Get video by selection string.

        Args:
            selection: 'last', 'video_id:123', etc.

        Returns:
            VideoHistory instance or None
        """
        try:
            from content.models import VideoHistory

            if selection == 'last':
                # Get most recent video for user
                if self.user:
                    video = VideoHistory.objects.filter(user=self.user).order_by('-created_at').first()
                else:
                    video = VideoHistory.objects.order_by('-created_at').first()

                return video

            elif selection.startswith('video_id:'):
                # Get by ID
                video_id = selection.split(':')[1]
                video = VideoHistory.objects.get(id=video_id)
                return video

            else:
                logger.warning(f"Unknown video selection: {selection}")
                return None

        except Exception as e:
            logger.error(f"Error getting video: {str(e)}")
            return None

    def add_text_to_video(
        self,
        text: str,
        video_selection: str = 'last',
        position: str = 'bottom',
        start_time: float = 0.0,
        duration: float = 5.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add text overlay to video.

        Args:
            text: Text to display
            video_selection: Which video to use
            position: Text position ('top', 'bottom', 'center')
            start_time: When text appears (seconds)
            duration: How long text displays (seconds)
            **kwargs: Additional parameters

        Returns:
            Result dictionary
        """
        try:
            logger.info(f"📝 VideoAgent adding text: '{text}' at {start_time}s for {duration}s")

            # Get video
            video = self._get_video_by_selection(video_selection)

            if not video:
                return {
                    'success': False,
                    'error': f'No video found for selection: {video_selection}'
                }

            # Call DaVinci backend
            from content.davinci_provider import get_davinci_provider
            davinci = get_davinci_provider()

            result = davinci.add_text_overlay(
                video_url=video.video_url,
                text=text,
                position=position,
                start_time=start_time,
                duration=duration
            )

            if result.get('success'):
                # Store in memory
                video_data = {
                    'video_url': result.get('video_url'),
                    'original_video_id': str(video.id),
                    'text': text,
                    'type': 'text_added',
                    'user_id': self.user.id if self.user else None,
                    'created_at': timezone.now().isoformat()
                }

                self.memory.remember('most_recent_video', video_data)

            return result

        except Exception as e:
            logger.error(f"❌ VideoAgent.add_text_to_video failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def apply_color_grade(
        self,
        video_selection: str = 'last',
        color_grade: str = 'cinematic_warm',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Apply color grading to video.

        Args:
            video_selection: Which video to use
            color_grade: Color grade preset
            **kwargs: Additional parameters

        Returns:
            Result dictionary
        """
        try:
            logger.info(f"🎨 VideoAgent applying color grade: {color_grade}")

            # Get video
            video = self._get_video_by_selection(video_selection)

            if not video:
                return {
                    'success': False,
                    'error': f'No video found for selection: {video_selection}'
                }

            # Call DaVinci backend
            from content.davinci_provider import get_davinci_provider
            davinci = get_davinci_provider()

            result = davinci.apply_color_grade(
                video_url=video.video_url,
                color_grade=color_grade
            )

            if result.get('success'):
                # Store in memory
                video_data = {
                    'video_url': result.get('video_url'),
                    'original_video_id': str(video.id),
                    'color_grade': color_grade,
                    'type': 'color_graded',
                    'user_id': self.user.id if self.user else None,
                    'created_at': timezone.now().isoformat()
                }

                self.memory.remember('most_recent_video', video_data)

            return result

        except Exception as e:
            logger.error(f"❌ VideoAgent.apply_color_grade failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    # ===== DAVINCI RESOLVE ORCHESTRATION METHODS (Session 84) =====

    def create_edited_video(
        self,
        video_ids: List[str],
        operations: List[Dict[str, Any]],
        project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Master orchestrator for multi-operation DaVinci video edits.
        Session 84: Agent-based video editing workflow!

        Args:
            video_ids: List of video IDs from database
            operations: List of editing operations to perform in sequence
            project_name: Optional project name (auto-generated if not provided)

        Operations format:
            [
                {'type': 'chain', 'transition': 'Cross Dissolve', 'duration': 1.0},
                {'type': 'text', 'text': 'Hello', 'position': 'center', 'start': 0, 'duration': 3},
                {'type': 'color_grade', 'style': 'cinematic', 'intensity': 0.7},
                {'type': 'audio', 'audio_url': 'url', 'volume': 0.3}
            ]

        Returns:
            {
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
            from content.davinci_provider import get_davinci_provider
            import uuid

            logger.info(f"🎬 VideoAgent orchestrating multi-operation edit: {len(operations)} operations on {len(video_ids)} videos")

            # Validate inputs
            if not video_ids or len(video_ids) == 0:
                return {
                    'success': False,
                    'error': 'At least one video ID is required'
                }

            if not operations or len(operations) == 0:
                return {
                    'success': False,
                    'error': 'At least one operation is required'
                }

            # Get video objects
            videos = []
            for video_id in video_ids:
                try:
                    video = VideoHistory.objects.get(id=video_id, user=self.user)
                    videos.append(video)
                except VideoHistory.DoesNotExist:
                    return {
                        'success': False,
                        'error': f'Video not found: {video_id}'
                    }

            # Generate project name if not provided
            if not project_name:
                project_name = f"Agent Edit {uuid.uuid4().hex[:8]}"

            logger.info(f"📝 Creating DaVinci project: {project_name}")

            # Get DaVinci provider
            davinci = get_davinci_provider()

            if not davinci.studio_available:
                return {
                    'success': False,
                    'error': 'DaVinci Resolve Studio not available'
                }

            # Create new project
            success = davinci.create_project(project_name)
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to create DaVinci project'
                }

            # Process operations in sequence
            operations_applied = 0
            current_video_url = videos[0].video_url  # Start with first video

            for i, operation in enumerate(operations):
                op_type = operation.get('type', '').lower()
                logger.info(f"⚙️  Operation {i+1}/{len(operations)}: {op_type}")

                if op_type == 'chain':
                    # Chain all videos together
                    video_paths = [v.video_url for v in videos]
                    transition_type = operation.get('transition', 'Cross Dissolve')
                    transition_duration = operation.get('duration', 1.0)

                    # Add clips to timeline with transitions
                    current_position = 0
                    for j, video_path in enumerate(video_paths):
                        clip = davinci.add_clip_to_timeline(
                            video_path=video_path,
                            position_seconds=current_position
                        )
                        if clip:
                            # Add transition before next clip (except for first clip)
                            if j > 0:
                                davinci.add_transition(
                                    transition_type=transition_type,
                                    at_second=current_position,
                                    duration=transition_duration
                                )
                            current_position += (videos[j].duration or 8)  # Default 8s if no duration

                    operations_applied += 1

                elif op_type == 'text':
                    # Add text overlay
                    text = operation.get('text', '')
                    position = operation.get('position', 'center')
                    start_second = operation.get('start', 0)
                    duration = operation.get('duration', 3)
                    font_size = operation.get('font_size', 72)

                    davinci.add_text_overlay(
                        text=text,
                        position=position,
                        start_second=start_second,
                        duration=duration,
                        font_size=font_size
                    )
                    operations_applied += 1

                elif op_type == 'color_grade':
                    # Apply color grading
                    style = operation.get('style', 'cinematic')
                    intensity = operation.get('intensity', 0.5)

                    davinci.apply_color_grading(
                        style=style,
                        intensity=intensity
                    )
                    operations_applied += 1

                elif op_type == 'audio':
                    # Add audio/music
                    audio_url = operation.get('audio_url', '')
                    volume = operation.get('volume', 0.3)
                    start_second = operation.get('start', 0)

                    if audio_url:
                        davinci.add_audio(
                            audio_path=audio_url,
                            volume=volume,
                            start_second=start_second
                        )
                        operations_applied += 1

                else:
                    logger.warning(f"⚠️  Unknown operation type: {op_type}")

            # Render final project
            logger.info(f"🎬 Rendering final video with {operations_applied} operations applied...")
            render_result = davinci.render_project()

            if not render_result.success:
                davinci.close_project()
                return {
                    'success': False,
                    'error': f'Render failed: {render_result.error_message}',
                    'operations_applied': operations_applied
                }

            # Session 84: Copy rendered video to media folder
            media_url = self._save_rendered_video_to_media(
                render_result.video_path,
                prefix='multi_edit'
            )

            # Create VideoHistory record
            video_record = VideoHistory.objects.create(
                user=self.user,
                video_url=media_url,
                prompt=f"Multi-edit: {', '.join([op['type'] for op in operations])}",
                model_used='davinci_resolve',
                video_type='multi_edit',
                status='completed',
                duration=render_result.duration,
                metadata={
                    'project_name': project_name,
                    'operations': operations,
                    'source_videos': video_ids,
                    'operations_applied': operations_applied
                }
            )

            # Clean up
            davinci.close_project()

            logger.info(f"✅ Multi-operation edit complete! Video ID: {video_record.id}")

            return {
                'success': True,
                'video_id': str(video_record.id),
                'video_url': video_record.video_url,
                'operations_applied': operations_applied,
                'duration': render_result.duration,
                'project_name': project_name,
                'message': f'✅ Video edited successfully with {operations_applied} operations!'
            }

        except Exception as e:
            logger.error(f"❌ VideoAgent.create_edited_video failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def add_text_overlay_davinci(
        self,
        video_id: str,
        text: str,
        position: str = 'center',
        start_second: float = 0,
        duration: float = 3,
        font_size: int = 72,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add text overlay to a single video using DaVinci Resolve.
        Session 84: Enhanced text overlay with more options!

        Args:
            video_id: Video ID from database
            text: Text to display
            position: 'center' | 'lower_third' | 'upper_third' | 'top' | 'bottom'
            start_second: When text appears (seconds)
            duration: How long text displays (seconds)
            font_size: Text size (36-144)
            **kwargs: Additional parameters (font_family, color, animation, etc.)

        Returns:
            Result dictionary with new video info
        """
        try:
            from content.models import VideoHistory
            from content.davinci_provider import get_davinci_provider
            import uuid

            logger.info(f"📝 VideoAgent adding text overlay: '{text}' at {position}")

            # Get video
            try:
                video = VideoHistory.objects.get(id=video_id, user=self.user)
            except VideoHistory.DoesNotExist:
                return {
                    'success': False,
                    'error': f'Video not found: {video_id}'
                }

            # Get DaVinci provider
            davinci = get_davinci_provider()

            if not davinci.studio_available:
                return {
                    'success': False,
                    'error': 'DaVinci Resolve Studio not available'
                }

            # Create project
            project_name = f"Text Overlay - {uuid.uuid4().hex[:8]}"
            success = davinci.create_project(project_name)
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to create DaVinci project'
                }

            # Add video to timeline
            davinci.add_clip_to_timeline(video_path=video.video_url, position_seconds=0)

            # Add text overlay
            davinci.add_text_overlay(
                text=text,
                position=position,
                start_second=start_second,
                duration=duration,
                font_size=font_size
            )

            # Render
            render_result = davinci.render_project()

            if not render_result.success:
                davinci.close_project()
                return {
                    'success': False,
                    'error': f'Render failed: {render_result.error_message}'
                }

            # Session 84: Copy rendered video to media folder
            media_url = self._save_rendered_video_to_media(
                render_result.video_path,
                prefix='text_overlay'
            )

            # Create VideoHistory record
            video_record = VideoHistory.objects.create(
                user=self.user,
                video_url=media_url,
                prompt=f"Text overlay: '{text}' on {video.prompt[:50]}",
                model_used='davinci_resolve',
                video_type='text_overlay',
                status='completed',
                duration=render_result.duration,
                metadata={
                    'original_video': str(video.id),
                    'text': text,
                    'position': position,
                    'start_second': start_second,
                    'duration': duration,
                    'font_size': font_size
                }
            )

            # Clean up
            davinci.close_project()

            logger.info(f"✅ Text overlay added! Video ID: {video_record.id}")

            return {
                'success': True,
                'video_id': str(video_record.id),
                'video_url': video_record.video_url,
                'text': text,
                'position': position,
                'message': f'✅ Text overlay "{text}" added successfully!'
            }

        except Exception as e:
            logger.error(f"❌ VideoAgent.add_text_overlay_davinci failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def apply_color_grade_davinci(
        self,
        video_id: str,
        style: str = 'cinematic',
        intensity: float = 0.5
    ) -> Dict[str, Any]:
        """
        Apply professional color grading to a video using DaVinci Resolve.
        Session 84: Professional color science!

        Args:
            video_id: Video ID from database
            style: Color grade style
                   - 'cinematic': Teal/orange Hollywood look
                   - 'vibrant': Boosted saturation + contrast
                   - 'vintage': Film-like warm tones
                   - 'noir': Black and white with high contrast
                   - 'warm': Golden hour warm tones
                   - 'cool': Blue/teal cool tones
            intensity: How strong the grade is (0.0-1.0)

        Returns:
            Result dictionary with new video info
        """
        try:
            from content.models import VideoHistory
            from content.davinci_provider import get_davinci_provider
            import uuid

            logger.info(f"🎨 VideoAgent applying color grade: {style} @ {intensity}")

            # Get video
            try:
                video = VideoHistory.objects.get(id=video_id, user=self.user)
            except VideoHistory.DoesNotExist:
                return {
                    'success': False,
                    'error': f'Video not found: {video_id}'
                }

            # Get DaVinci provider
            davinci = get_davinci_provider()

            if not davinci.studio_available:
                return {
                    'success': False,
                    'error': 'DaVinci Resolve Studio not available'
                }

            # Create project
            project_name = f"Color Grade - {style} - {uuid.uuid4().hex[:8]}"
            success = davinci.create_project(project_name)
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to create DaVinci project'
                }

            # Add video to timeline
            davinci.add_clip_to_timeline(video_path=video.video_url, position_seconds=0)

            # Apply color grading (Note: DaVinci provider doesn't support intensity yet)
            davinci.apply_color_grading(style=style)

            # Render
            render_result = davinci.render_project()

            if not render_result.success:
                davinci.close_project()
                return {
                    'success': False,
                    'error': f'Render failed: {render_result.error_message}'
                }

            # Session 84: Copy rendered video to media folder
            media_url = self._save_rendered_video_to_media(
                render_result.video_path,
                prefix='color_graded'
            )

            # Create VideoHistory record
            video_record = VideoHistory.objects.create(
                user=self.user,
                video_url=media_url,
                prompt=f"Color graded ({style}): {video.prompt[:50]}",
                model_used='davinci_resolve',
                video_type='color_graded',
                status='completed',
                duration=render_result.duration,
                metadata={
                    'original_video': str(video.id),
                    'style': style,
                    'intensity': intensity
                }
            )

            # Clean up
            davinci.close_project()

            logger.info(f"✅ Color grade applied! Video ID: {video_record.id}")

            return {
                'success': True,
                'video_id': str(video_record.id),
                'video_url': video_record.video_url,
                'style': style,
                'intensity': intensity,
                'message': f'✅ {style.capitalize()} color grade applied successfully!'
            }

        except Exception as e:
            logger.error(f"❌ VideoAgent.apply_color_grade_davinci failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def chain_videos_davinci(
        self,
        video_ids: List[str],
        transition_type: str = 'Cross Dissolve',
        transition_duration: float = 1.0,
        add_transitions: bool = True,
        project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chain multiple videos together using ffmpeg (Session 84: Switched from DaVinci!)

        Session 84 Fix: DaVinci Resolve API has render start issues (StartRendering returns True
        but render never actually starts). Switched to ffmpeg like we did for audio mixing in
        Session 82 Part 3 - it's 100x faster and more reliable!

        Args:
            video_ids: List of video IDs to chain
            transition_type: Transition style ('fade', 'wipe', 'dissolve')
            transition_duration: Transition length in seconds (0.5-3.0)
            add_transitions: Whether to add transitions between clips
            project_name: Optional project name (not used with ffmpeg)

        Returns:
            Result dictionary with chained video info
        """
        try:
            from content.models import VideoHistory
            from content.davinci_provider import get_davinci_provider

            logger.info(f"🎬 VideoAgent chaining {len(video_ids)} videos with ffmpeg...")

            # Validate
            if not video_ids or len(video_ids) < 2:
                return {
                    'success': False,
                    'error': 'At least 2 videos required for chaining'
                }

            # Get video objects
            videos = []
            video_urls = []
            for video_id in video_ids:
                try:
                    video = VideoHistory.objects.get(id=video_id, user=self.user)
                    videos.append(video)
                    video_urls.append(video.video_url)
                except VideoHistory.DoesNotExist:
                    return {
                        'success': False,
                        'error': f'Video not found: {video_id}'
                    }

            # Session 84: Use ffmpeg instead of DaVinci (more reliable!)
            davinci = get_davinci_provider()

            # Map DaVinci transition names to ffmpeg transition names
            transition_map = {
                'Cross Dissolve': 'fade',
                'Fade': 'fade',
                'Wipe': 'wipe',
                'Slide': 'slide'
            }
            ffmpeg_transition = transition_map.get(transition_type, 'fade')

            # Call ffmpeg chaining method
            result = davinci.chain_videos_ffmpeg(
                video_urls=video_urls,
                transition=ffmpeg_transition,
                transition_duration=transition_duration if add_transitions else 0,
                output_format='mp4'
            )

            if not result['success']:
                return {
                    'success': False,
                    'error': f"ffmpeg chaining failed: {result.get('error', 'Unknown error')}"
                }

            # Session 84: Copy rendered video to media folder
            media_url = self._save_rendered_video_to_media(
                result['video_url'],
                prefix='chained'
            )

            # Create VideoHistory record
            video_record = VideoHistory.objects.create(
                user=self.user,
                video_url=media_url,
                prompt=f"Chained {len(videos)} videos with {transition_type}",
                model_used='ffmpeg',  # Session 84: Changed from davinci_resolve
                video_type='chained',
                status='completed',
                duration=result['metadata'].get('duration', 0),
                metadata={
                    'source_videos': video_ids,
                    'transition_type': transition_type,
                    'transition_duration': transition_duration,
                    'clip_count': len(videos),
                    'method': 'ffmpeg'  # Session 84: Track that we used ffmpeg
                }
            )

            # Session 84: No project cleanup needed (using ffmpeg, not DaVinci API)

            logger.info(f"✅ Videos chained with ffmpeg! Video ID: {video_record.id}")

            return {
                'success': True,
                'video_id': str(video_record.id),
                'video_url': video_record.video_url,
                'clip_count': len(videos),
                'duration': result['metadata'].get('duration', 0),  # Session 84: Get from ffmpeg result
                'transition_type': transition_type,
                'method': 'ffmpeg',  # Session 84: Indicate we used ffmpeg
                'message': f'✅ {len(videos)} videos chained successfully with ffmpeg ({transition_type} transitions)!'
            }

        except Exception as e:
            logger.error(f"❌ VideoAgent.chain_videos_davinci failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    # ===== QUERY HANDLERS =====

    def get_most_recent_video(self) -> Optional[Dict]:
        """
        Query handler: Return most recently modified video.

        Returns:
            Video data dictionary or None
        """
        video_data = self.memory.recall('most_recent_video')

        if video_data:
            logger.info(
                f"📤 VideoAgent responding to query: most_recent_video "
                f"(type={video_data.get('type')})"
            )
        else:
            logger.info("📤 VideoAgent responding to query: most_recent_video (no data)")

        return video_data


# ===== CONVENIENCE FUNCTIONS =====

def get_video_agent(user: Optional[User] = None) -> VideoAgent:
    """
    Get VideoAgent instance.

    Args:
        user: User who initiated the agent

    Returns:
        VideoAgent instance
    """
    return VideoAgent(user=user)


def execute_video_agent_method(
    method_name: str,
    parameters: Dict,
    user: Optional[User] = None
) -> Dict[str, Any]:
    """
    Execute VideoAgent method by name.

    Args:
        method_name: Method to call (e.g., 'add_music_to_video')
        parameters: Method parameters
        user: User who initiated the request

    Returns:
        Method result
    """
    try:
        agent = get_video_agent(user=user)

        # Get method
        method = getattr(agent, method_name, None)

        if not method:
            return {
                'success': False,
                'error': f'Method not found: {method_name}'
            }

        # Call method
        result = method(**parameters)

        return result

    except Exception as e:
        logger.error(f"Failed to execute VideoAgent method: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


__all__ = [
    'VideoAgent',
    'get_video_agent',
    'execute_video_agent_method'
]
