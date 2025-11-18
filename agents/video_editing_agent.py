"""
Video Editing Agent - Session 128 Part 2

Specialized agent for video editing operations using ffmpeg.
Handles text overlays, color grading, and post-production effects.

Architecture:
    AI Assistant (detects intent) → Video Editing Agent → DaVinci Endpoints → ffmpeg
"""

import logging
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.http import QueryDict
import json

from content.models import VideoHistory

User = get_user_model()
logger = logging.getLogger(__name__)


class VideoEditingAgent:
    """
    Specialized agent for video editing operations.

    Responsibilities:
        - Add text overlays with precise timing
        - Apply professional color grading
        - Handle video trimming and speed adjustments
        - Process videos with ffmpeg
        - Associate edited videos with projects
    """

    def __init__(self, user: User, project_id: Optional[str] = None):
        """
        Initialize Video Editing Agent.

        Args:
            user: User requesting video editing
            project_id: Optional project ID to associate result with
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = "Video Editing Agent"

    def execute(
        self,
        operation: str,
        video_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a video editing operation.

        Args:
            operation: Type of operation ('add_text_overlay', 'apply_color_grading',
                      'trim_video', 'speed_adjust')
            video_id: UUID or sequential number of the video to edit
            **kwargs: Operation-specific parameters

        Returns:
            Dict with success status and edited video results
        """
        logger.info(f"🤖 {self.agent_name} starting {operation} workflow")
        logger.info(f"   User: {self.user.username}")
        logger.info(f"   Video ID: {video_id}")
        logger.info(f"   Operation: {operation}")

        try:
            # Step 1: Validate and resolve video ID
            video = self._resolve_video_id(video_id)
            if not video:
                return {
                    'success': False,
                    'error': f'Video {video_id} not found for user {self.user.username}'
                }

            seq_num = video.get_sequential_number() if hasattr(video, 'get_sequential_number') else 'unknown'
            logger.info(f"✅ Video validated: #{seq_num} ({video.id})")
            logger.info(f"   Duration: {video.duration if hasattr(video, 'duration') else 'unknown'}s")

            # Step 2: Route to appropriate operation
            operation_map = {
                'add_text_overlay': self._add_text_overlay,
                'apply_color_grading': self._apply_color_grading,
                'trim_video': self._trim_video,
                'speed_adjust': self._speed_adjust
            }

            if operation not in operation_map:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}'
                }

            logger.info(f"🚀 Executing {operation} operation...")

            # Execute the operation
            result = operation_map[operation](str(video.id), **kwargs)

            if result.get('success'):
                logger.info(f"✅ {self.agent_name} {operation} completed successfully")
            else:
                logger.error(f"❌ {self.agent_name} {operation} failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"❌ {self.agent_name} failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _add_text_overlay(self, video_id: str, **kwargs) -> Dict[str, Any]:
        """Add text overlay to video."""
        try:
            from core.views_davinci import add_text_overlay_endpoint

            text = kwargs.get('text', '')
            position = kwargs.get('position', 'center')
            start_second = kwargs.get('start_second', 0)
            duration = kwargs.get('duration', 3)
            font_size = kwargs.get('font_size', 72)

            logger.info(f"📝 Adding text overlay: '{text}' at {start_second}s for {duration}s")

            factory = RequestFactory()
            post_data = QueryDict('', mutable=True)
            post_data['video_id'] = str(video_id)
            post_data['text'] = text
            post_data['position'] = position
            post_data['start_second'] = str(start_second)
            post_data['duration'] = str(duration)
            post_data['font_size'] = str(font_size)

            view_request = factory.post('/api/v1/davinci/add-text-overlay/', post_data)
            view_request.user = self.user
            view_request.POST = post_data

            response = add_text_overlay_endpoint(view_request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'video_url': result.get('video_url'),
                    'video_id': result.get('video_id'),
                    'message': f"✅ Text overlay added successfully!\n\n" + \
                              f"Text: '{text}'\n" + \
                              f"Position: {position}\n" + \
                              f"Timing: {start_second}s for {duration}s\n" + \
                              f"Font size: {font_size}\n\n" + \
                              f"The video with text overlay is ready in the gallery!"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error_message', 'Text overlay failed')
                }

        except Exception as e:
            logger.error(f"❌ Add text overlay operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to add text overlay: {str(e)}"
            }

    def _apply_color_grading(self, video_id: str, **kwargs) -> Dict[str, Any]:
        """Apply color grading to video."""
        try:
            from core.views_davinci import apply_color_grading_endpoint

            style = kwargs.get('style', 'cinematic_warm')

            logger.info(f"🎨 Applying {style} color grading...")

            factory = RequestFactory()
            post_data = QueryDict('', mutable=True)
            post_data['video_id'] = str(video_id)
            post_data['style'] = style

            view_request = factory.post('/api/v1/davinci/apply-color-grading/', post_data)
            view_request.user = self.user
            view_request.POST = post_data

            response = apply_color_grading_endpoint(view_request)
            result = json.loads(response.content)

            if result.get('success'):
                style_descriptions = {
                    'cinematic_warm': 'warm orange tones - film-like',
                    'cinematic_cool': 'cool blue tones - professional',
                    'vintage': 'retro film look with grain',
                    'modern': 'clean and crisp',
                    'high_contrast': 'bold dramatic look',
                    'soft': 'muted gentle tones',
                    'vibrant': 'saturated vivid colors'
                }
                style_desc = style_descriptions.get(style, style)

                return {
                    'success': True,
                    'video_url': result.get('video_url'),
                    'video_id': result.get('video_id'),
                    'message': f"✅ Color grading applied successfully!\n\n" + \
                              f"Style: {style}\n" + \
                              f"Look: {style_desc}\n\n" + \
                              f"The color-graded video is ready in the gallery!"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error_message', 'Color grading failed')
                }

        except Exception as e:
            logger.error(f"❌ Apply color grading operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to apply color grading: {str(e)}"
            }

    def _trim_video(self, video_id: str, **kwargs) -> Dict[str, Any]:
        """Trim video to specific duration."""
        # Placeholder for future implementation
        return {
            'success': False,
            'error': 'Trim video operation not yet implemented in agent'
        }

    def _speed_adjust(self, video_id: str, **kwargs) -> Dict[str, Any]:
        """Adjust video playback speed."""
        # Placeholder for future implementation
        return {
            'success': False,
            'error': 'Speed adjust operation not yet implemented in agent'
        }

    def _resolve_video_id(self, video_id: str) -> Optional[VideoHistory]:
        """
        Resolve video ID (UUID or sequential number) to VideoHistory object.

        Args:
            video_id: UUID string or sequential number as string

        Returns:
            VideoHistory object or None if not found
        """
        try:
            # Try UUID first
            return VideoHistory.objects.get(id=video_id, user=self.user)
        except (ValueError, VideoHistory.DoesNotExist):
            # Try sequential number
            try:
                seq_num = int(video_id)
                videos = VideoHistory.objects.filter(user=self.user).order_by('created_at')
                if seq_num > 0 and seq_num <= videos.count():
                    return videos[seq_num - 1]
            except (ValueError, IndexError):
                pass

        return None
