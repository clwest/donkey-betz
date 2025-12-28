"""
Video Agent - Unified Video Specialist
======================================

Session 81: Original creation
Session 202: CONSOLIDATED - Merged VideoGenerationAgent + VideoEditingAgent into this unified agent
Session 203: Added preference learning and memory (Phase 4)

This is the ONE agent for ALL video operations:
- Text-to-video generation (RunwayML)
- Image-to-video animation (RunwayML)
- Video extension
- Text overlay addition
- Color grading
- Music/audio mixing (queries AudioAgent)
- Video chaining
- Video editing operations
- USER PREFERENCE LEARNING (Session 203)

Example Usage:
    video_agent = VideoAgent(user=request.user)

    # Generate video from text
    result = video_agent.generate(prompt="A beautiful sunset over the ocean")

    # Generate with learned preferences (duration, quality auto-applied)
    result = video_agent.generate(prompt="A dancing donkey")

    # Animate an image
    result = video_agent.animate_image(image_id='123', motion_prompt='zoom in slowly')

    # Add music to video (auto-queries AudioAgent)
    result = video_agent.add_music_to_video(video_selection='last')

    # Edit video
    result = video_agent.edit(video_id='456', operation='add_text_overlay', text='Hello')

    # Get user's preferences
    prefs = video_agent.get_user_preferences()
"""

from __future__ import annotations

import logging
import os
import shutil
from typing import Dict, Any, Optional, List

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

from core.models.agents_registry import UnifiedAgentTemplate
from intelligence.shared_memory import AgentMemoryInterface
from intelligence.agent_query_protocol import query_protocol

logger = logging.getLogger(__name__)
User = get_user_model()


class VideoAgent:
    """
    Specialized agent for video operations.
    Can query other agents for required data.
    """

    def __init__(self, user: Optional[User] = None, project_id: Optional[str] = None):
        """
        Initialize Video Agent.

        Args:
            user: User who initiated the agent (optional)
            project_id: Optional project ID to associate results with
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = 'VideoAgent'

        # Initialize memory interface for state management
        self.memory = AgentMemoryInterface(agent_id='video_agent')

        # Get or create agent template
        self.template = self._get_or_create_template()

        # Session 203: Initialize preference manager for memory
        self._preference_manager = None

        logger.info(f"🎬 Video Agent initialized for user: {user.username if user else 'system'}")

    @property
    def preference_manager(self):
        """Lazy load preference manager."""
        if self._preference_manager is None and self.user:
            from agents.preference_manager import AgentPreferenceManager
            self._preference_manager = AgentPreferenceManager(self.user, self.project_id)
        return self._preference_manager

    def get_user_preferences(self) -> Dict[str, Any]:
        """
        Get user's learned video preferences.

        Returns:
            Dict with preferred duration, quality, aspect_ratio, etc.
        """
        if self.preference_manager:
            return self.preference_manager.get_video_preferences()
        return {}

    def _apply_preferences(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply user preferences to parameters (fill in missing values).
        User-specified values always take precedence.
        """
        if self.preference_manager:
            return self.preference_manager.apply_preferences('video', params)
        return params

    def _record_success(self, params: Dict[str, Any], user_rating: Optional[int] = None):
        """Record a successful generation for preference learning."""
        if self.preference_manager:
            self.preference_manager.record_successful_generation('video', params, user_rating)

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

                    # Session 144: Track agent contribution for audio mixing
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                        AgentContribution.objects.create(
                            agent=agent,
                            video=video_record,
                            project=getattr(video, 'project', None),
                            contribution_type='editing',
                            task_description=f"Mixed audio to video using ffmpeg (volume={audio_volume})",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for video {video_record.id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")

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

            # Session 144: Track agent contribution for multi-edit
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=video_record,
                    project=getattr(videos[0], 'project', None) if videos else None,
                    contribution_type='editing',
                    task_description=f"Multi-edit with DaVinci Resolve ({len(operations)} operations on {len(videos)} videos)",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for video {video_record.id}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")

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

            # Session 144: Track agent contribution for text overlay
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=video_record,
                    project=getattr(video, 'project', None),
                    contribution_type='editing',
                    task_description=f"Added text overlay using DaVinci Resolve (text='{text}', position={position})",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for video {video_record.id}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")

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

            # Session 144: Track agent contribution for color grading
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=video_record,
                    project=getattr(video, 'project', None),
                    contribution_type='editing',
                    task_description=f"Applied color grading using DaVinci Resolve (style={style}, intensity={intensity})",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for video {video_record.id}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")

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

            # Session 144: Track agent contribution for video chaining
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=video_record,
                    project=getattr(videos[0], 'project', None) if videos else None,
                    contribution_type='editing',
                    task_description=f"Chained {len(videos)} videos using ffmpeg (transition={transition_type})",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for video {video_record.id}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")

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

    # ===== SESSION 127: IMAGE-TO-VIDEO ANIMATION =====

    def animate_image(
        self,
        image_id: str,
        motion_prompt: Optional[str] = None,
        duration: int = 5,
        project=None,  # Session 127 Part 2: Accept project context
        session=None,  # Session 127 Part 2: Accept session context
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convert a static image into an animated video using Runway ML.
        Session 127: Agent-based image-to-video animation!

        Args:
            image_id: Image ID from database (UUID or sequential number)
            motion_prompt: Optional description of desired motion (e.g., 'zoom in slowly', 'pan left')
            duration: Video duration in seconds (5 or 10)
            **kwargs: Additional parameters

        Returns:
            Result dictionary with video info
        """
        try:
            from content.models import ImageHistory, VideoHistory
            from content.video_provider import runway_provider

            logger.info(f"🎬 VideoAgent.animate_image CALLED with image_id: '{image_id}' (type: {type(image_id).__name__})")

            # Session 127: Hybrid ID support - EXACT pattern from Session 122 Bug #4 fix
            # Use .isdigit() to check BEFORE touching Django's UUID field!
            image = None

            if isinstance(image_id, str) and image_id.isdigit():
                # User asked for "image 271" - get the 271st image chronologically
                numeric_index = int(image_id)
                logger.info(f"🔍 Numeric ID detected: {numeric_index}")

                try:
                    image = ImageHistory.objects.filter(
                        user=self.user
                    ).order_by('created_at')[numeric_index - 1]  # 1-indexed
                    logger.info(f"✅ Resolved image #{numeric_index} to UUID: {image.id}")

                except (IndexError, ImageHistory.DoesNotExist):
                    total_images = ImageHistory.objects.filter(user=self.user).count()
                    logger.error(f"❌ Image #{numeric_index} not found. User has {total_images} images.")
                    return {
                        'success': False,
                        'error': f'Image #{numeric_index} not found. You have {total_images} images.'
                    }
            else:
                # Full UUID provided
                logger.info(f"🔍 UUID detected: {image_id}")
                try:
                    image = ImageHistory.objects.get(id=image_id, user=self.user)
                    logger.info(f"✅ Resolved UUID {image_id} to image")
                except ImageHistory.DoesNotExist:
                    logger.error(f"❌ Image not found for UUID: {image_id}")
                    return {
                        'success': False,
                        'error': f'Image with ID {image_id} not found.'
                    }
                except Exception as e:
                    logger.error(f"❌ Unexpected error on UUID lookup: {e}", exc_info=True)
                    return {
                        'success': False,
                        'error': f'Error finding image: {str(e)}'
                    }

            # Get image display info
            try:
                seq_num = image.get_sequential_number() if hasattr(image, 'get_sequential_number') else image_id
                image_prompt = image.prompt if hasattr(image, 'prompt') and image.prompt else f"Image #{seq_num}"
            except Exception as e:
                logger.warning(f"⚠️ Error getting image details: {e}")
                seq_num = image_id
                image_prompt = "Your image"

            # Default motion prompt if not provided
            if not motion_prompt:
                motion_prompt = 'natural motion'

            # Get image URL using the proper method
            logger.info(f"🔍 DEBUG: About to call image.get_full_url()")
            logger.info(f"🔍 DEBUG: image object type: {type(image)}")
            logger.info(f"🔍 DEBUG: image dir: {[attr for attr in dir(image) if 'url' in attr.lower()]}")

            image_url = image.get_full_url()

            logger.info(f"🎬 Calling Runway ML image-to-video: {image_url[:100]}...")
            logger.info(f"   Motion: {motion_prompt}, Duration: {duration}s")

            # Call Runway ML image-to-video API
            result = runway_provider.image_to_video(
                image_url=image_url,
                motion_prompt=motion_prompt,
                duration=duration,
                quality=kwargs.get('quality', 'gen4_turbo')  # Use gen4_turbo by default for image-to-video
            )

            if not result.success:
                return {
                    'success': False,
                    'error': result.error_message or 'Image-to-video generation failed',
                    'image_id': str(image.id),
                    'image_prompt': image_prompt
                }

            # Create VideoHistory record with pending status
            # Session 127 Part 2: Include project and session context!
            video_record = VideoHistory.objects.create(
                video_id=result.task_id,
                user=self.user,
                project=project,  # Associate with project!
                session=session,  # Associate with session!
                video_type='image_to_video',
                prompt=f"Animated from image #{seq_num}: {motion_prompt}",
                duration=duration,
                model_used=kwargs.get('quality', 'gen4_turbo'),  # Use correct model name
                status='pending',
                metadata={
                    'source_image_id': str(image.id),
                    'source_image_prompt': image_prompt,
                    'source_image_url': image_url,  # Store in metadata instead
                    'motion_prompt': motion_prompt,
                    'method': 'runway_ml_image_to_video',
                    'agent': 'VideoAgent'
                }
            )

            # Store in memory
            video_data = {
                'video_id': str(video_record.id),
                'task_id': result.task_id,
                'source_image_id': str(image.id),
                'motion_prompt': motion_prompt,
                'type': 'image_to_video_animation',
                'user_id': self.user.id if self.user else None,
                'created_at': timezone.now().isoformat()
            }

            self.memory.remember('most_recent_video', video_data)

            logger.info(f"✅ VideoAgent started image animation! Task ID: {result.task_id}")

            # Session 144: Track agent contribution for image-to-video
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=video_record,
                    project=project,
                    contribution_type='generation',
                    task_description=f"Generated image-to-video using Runway ML (image #{seq_num}, motion='{motion_prompt}')",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for video {video_record.id}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")

            return {
                'success': True,
                'task_id': result.task_id,
                'video_id': str(video_record.id),
                'status': 'pending',
                'image_id': str(image.id),
                'image_prompt': image_prompt,
                'motion_prompt': motion_prompt,
                'duration': duration,
                'message': f'✅ Image animation started!\n\n'
                          f'Motion: {motion_prompt}\n'
                          f'Duration: {duration}s\n'
                          f'Task ID: {result.task_id}\n\n'
                          f'The animated video will appear in the gallery in ~60 seconds.'
            }

        except Exception as e:
            logger.error(f"❌ VideoAgent.animate_image failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    # ===== SESSION 202: UNIFIED GENERATION METHODS (from VideoGenerationAgent) =====

    def generate(
        self,
        prompt: str,
        image_id: Optional[str] = None,
        duration: int = 5,
        quality: str = 'gen4_turbo',
        ratio: str = '1280:720',
        project=None,
        session=None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a video from text prompt or image.
        Session 202: Consolidated from VideoGenerationAgent.

        Args:
            prompt: Text description for text-to-video, or motion description for image-to-video
            image_id: Optional image UUID or sequential number for image-to-video
            duration: Video duration in seconds (4-10)
            quality: Model quality ('gen4_turbo', 'veo3.1_fast', 'veo3.1', etc.)
            ratio: Aspect ratio ('1280:720', '1920:1080', etc.)
            project: Optional project to associate with
            session: Optional session to associate with

        Returns:
            Dict with success status, task_id, and estimated time
        """
        from content.models import VideoHistory
        from content.video_provider import runway_provider

        logger.info(f"🎬 VideoAgent generating video")
        logger.info(f"   User: {self.user.username if self.user else 'system'}")
        logger.info(f"   Type: {'Image-to-Video' if image_id else 'Text-to-Video'}")
        logger.info(f"   Quality: {quality} | Duration: {duration}s | Ratio: {ratio}")

        try:
            if image_id:
                # Image-to-video - delegate to existing animate_image method
                return self.animate_image(
                    image_id=image_id,
                    motion_prompt=prompt,
                    duration=duration,
                    project=project,
                    session=session,
                    quality=quality,
                    **kwargs
                )
            else:
                # Text-to-video workflow
                logger.info(f"✅ Text prompt validated: {prompt[:80]}...")
                logger.info(f"🚀 Creating text-to-video job with RunwayML {quality}...")

                result = runway_provider.text_to_video(
                    prompt=prompt,
                    duration=duration,
                    quality=quality,
                    ratio=ratio,
                    **kwargs
                )

                if not result.success:
                    logger.error(f"❌ RunwayML generation failed: {result.error_message}")
                    return {
                        'success': False,
                        'error': result.error_message
                    }

                logger.info(f"✅ Video generation job created")
                logger.info(f"   Task ID: {result.task_id}")

                # Create VideoHistory record
                video_history = VideoHistory.objects.create(
                    user=self.user,
                    prompt=prompt,
                    video_type='text_to_video',
                    status='pending',
                    runway_task_id=result.task_id,
                    duration=duration,
                    model_used=quality,
                    project=project,
                    session=session
                )

                # Track agent contribution
                try:
                    from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                    agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                    AgentContribution.objects.create(
                        agent=agent,
                        video=video_history,
                        project=project,
                        contribution_type='generation',
                        task_description=f"Generated text-to-video (duration={duration}s, quality={quality})",
                        execution_time_seconds=0.0
                    )
                except Exception as e:
                    logger.error(f"❌ Failed to create agent contribution: {e}")

                # Store in memory
                video_data = {
                    'video_id': str(video_history.id),
                    'task_id': result.task_id,
                    'prompt': prompt,
                    'type': 'text_to_video',
                    'user_id': self.user.id if self.user else None,
                    'created_at': timezone.now().isoformat()
                }
                self.memory.remember('most_recent_video', video_data)

                return {
                    'success': True,
                    'video_id': str(video_history.id),
                    'task_id': result.task_id,
                    'status': result.status,
                    'estimated_time_seconds': result.estimated_time,
                    'message': f'Video generation started. Estimated time: {result.estimated_time}s'
                }

        except Exception as e:
            logger.error(f"❌ VideoAgent.generate failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def check_status(self, video_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation job.
        Session 202: Consolidated from VideoGenerationAgent.

        Args:
            video_id: VideoHistory UUID

        Returns:
            Dict with status, video URL, progress, and completion info
        """
        from content.models import VideoHistory
        from content.video_provider import runway_provider

        logger.info(f"🔍 VideoAgent checking status for video {video_id}")

        try:
            video = VideoHistory.objects.get(id=video_id, user=self.user)

            if not video.runway_task_id:
                return {
                    'success': False,
                    'error': 'No RunwayML task ID found for this video'
                }

            result = runway_provider.check_status(video.runway_task_id)

            status_map = {
                'pending': 'pending',
                'processing': 'processing',
                'completed': 'completed',
                'failed': 'failed'
            }
            video.status = status_map.get(result.status, result.status)

            if result.status == 'completed':
                logger.info(f"✅ Video generation completed!")
                if result.video_url:
                    video.video_url = result.video_url
                    video.duration = result.duration if result.duration else video.duration
            elif result.status == 'failed':
                logger.error(f"❌ Video generation failed: {result.error_message}")
                video.error_message = result.error_message

            video.save()

            response = {
                'success': True,
                'video_id': video_id,
                'status': video.status,
                'progress': result.progress,
                'progress_message': result.progress_message
            }

            if video.status == 'completed' and video.video_url:
                response['video_url'] = video.video_url
                response['duration'] = video.duration
                response['message'] = 'Video ready! Click to play or download.'
            elif video.status == 'failed':
                response['error'] = video.error_message or 'Video generation failed'
            elif video.status in ['pending', 'processing']:
                response['message'] = result.progress_message or 'Generating video...'

            return response

        except VideoHistory.DoesNotExist:
            return {'success': False, 'error': f'Video {video_id} not found'}
        except Exception as e:
            logger.error(f"❌ Status check failed: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def extend_video(
        self,
        video_id: str,
        extension_seconds: int = 10,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extend an existing video by generating a continuation.
        Session 202: Consolidated from VideoGenerationAgent.

        Args:
            video_id: VideoHistory UUID of video to extend
            extension_seconds: Seconds to add (4-10)
            prompt: Optional prompt to guide extension

        Returns:
            Dict with success status and new video job info
        """
        from content.models import VideoHistory
        from content.video_provider import runway_provider

        logger.info(f"🎬 VideoAgent extending video {video_id} by {extension_seconds}s")

        try:
            original_video = VideoHistory.objects.get(id=video_id, user=self.user)

            if original_video.status != 'completed':
                return {'success': False, 'error': 'Original video must be completed before extending'}

            if not original_video.video_url:
                return {'success': False, 'error': 'Original video URL not found'}

            if not prompt:
                prompt = "Continue the motion and atmosphere from the video"

            result = runway_provider.extend_video(
                video_url=original_video.video_url,
                extension_seconds=extension_seconds,
                prompt=prompt
            )

            if not result.success:
                return {'success': False, 'error': result.error_message}

            extended_video = VideoHistory.objects.create(
                user=self.user,
                prompt=f"Extension of video {video_id}: {prompt}",
                video_type='video_extension',
                status='pending',
                runway_task_id=result.task_id,
                duration=extension_seconds,
                model_used=original_video.model_used,
                project=original_video.project
            )

            # Track agent contribution
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=extended_video,
                    project=original_video.project,
                    contribution_type='editing',
                    task_description=f"Extended video {video_id} by {extension_seconds}s",
                    execution_time_seconds=0.0
                )
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")

            return {
                'success': True,
                'video_id': str(extended_video.id),
                'task_id': result.task_id,
                'status': result.status,
                'estimated_time_seconds': result.estimated_time,
                'message': f'Video extension started. Original + {extension_seconds}s extension.'
            }

        except VideoHistory.DoesNotExist:
            return {'success': False, 'error': f'Video {video_id} not found'}
        except Exception as e:
            logger.error(f"❌ VideoAgent.extend_video failed: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def edit(
        self,
        video_id: str,
        operation: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a video editing operation.
        Session 202: Consolidated from VideoEditingAgent.

        Args:
            operation: Type of operation ('add_text_overlay', 'apply_color_grading',
                      'trim_video', 'speed_adjust')
            video_id: UUID or sequential number of the video to edit
            **kwargs: Operation-specific parameters

        Returns:
            Dict with success status and edited video results
        """
        logger.info(f"🎬 VideoAgent editing video {video_id}: {operation}")

        operation_map = {
            'add_text_overlay': self.add_text_to_video,
            'apply_color_grading': self.apply_color_grade,
            'apply_color_grade': self.apply_color_grade,
            'add_music': self.add_music_to_video,
            'chain': self.chain_videos_davinci,
        }

        if operation in operation_map:
            method = operation_map[operation]
            if operation == 'add_text_overlay':
                return method(
                    text=kwargs.get('text', ''),
                    video_selection=f'video_id:{video_id}',
                    position=kwargs.get('position', 'center'),
                    start_time=kwargs.get('start_second', 0),
                    duration=kwargs.get('duration', 3)
                )
            elif operation in ['apply_color_grading', 'apply_color_grade']:
                return method(
                    video_selection=f'video_id:{video_id}',
                    color_grade=kwargs.get('style', 'cinematic_warm')
                )
            elif operation == 'add_music':
                return method(
                    video_selection=f'video_id:{video_id}',
                    audio_url=kwargs.get('audio_url'),
                    audio_volume=kwargs.get('volume', 0.3)
                )
            else:
                return method(**kwargs)

        return {
            'success': False,
            'error': f'Unknown operation: {operation}. Supported: {list(operation_map.keys())}'
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
