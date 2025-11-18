"""
Video Generation Agent - Session 128

Specialized agent for video generation using RunwayML Gen-3 Alpha and Gen-4 models.
Handles text-to-video, image-to-video, and video extension workflows.

Architecture:
    AI Assistant (detects intent) → Video Generation Agent → Video Provider → RunwayML API
"""

import logging
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model

from content.models import VideoHistory, ImageHistory
from content.video_provider import runway_provider

User = get_user_model()
logger = logging.getLogger(__name__)


class VideoGenerationAgent:
    """
    Specialized agent for video generation from text and images.

    Responsibilities:
        - Validate prompts and source images
        - Create video generation jobs with RunwayML
        - Monitor generation progress
        - Store completed videos in database
        - Associate videos with user projects
    """

    def __init__(self, user: User, project_id: Optional[str] = None):
        """
        Initialize Video Generation Agent.

        Args:
            user: User requesting video generation
            project_id: Optional project ID to associate result with
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = "Video Generation Agent"

    def execute(
        self,
        prompt: str,
        image_id: Optional[str] = None,
        duration: int = 5,
        quality: str = 'gen4_turbo',
        ratio: str = '1280:720',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a video from text prompt or image.

        Args:
            prompt: Text description for text-to-video, or motion description for image-to-video
            image_id: Optional image UUID or sequential number for image-to-video
            duration: Video duration in seconds (4-10)
            quality: Model quality ('gen4_turbo', 'veo3.1_fast', 'veo3.1', etc.)
            ratio: Aspect ratio ('1280:720', '1920:1080', etc.)

        Returns:
            Dict with success status, task_id, and estimated time
        """
        logger.info(f"🤖 {self.agent_name} starting video generation workflow")
        logger.info(f"   User: {self.user.username}")
        logger.info(f"   Type: {'Image-to-Video' if image_id else 'Text-to-Video'}")
        logger.info(f"   Quality: {quality} | Duration: {duration}s | Ratio: {ratio}")

        try:
            # Step 1: Determine video type and validate inputs
            if image_id:
                # Image-to-video workflow
                image = self._resolve_image_id(image_id)
                if not image:
                    return {
                        'success': False,
                        'error': f'Image {image_id} not found for user {self.user.username}'
                    }

                logger.info(f"✅ Image validated: {image.id}")
                logger.info(f"   Image URL: {image.image_url}")
                logger.info(f"   Motion prompt: {prompt[:80]}...")

                # Step 2: Create image-to-video job
                logger.info(f"🚀 Creating image-to-video job with RunwayML {quality}...")
                result = runway_provider.image_to_video(
                    image_url=image.image_url,
                    motion_prompt=prompt,
                    duration=duration,
                    quality=quality,
                    ratio=ratio,
                    **kwargs
                )
            else:
                # Text-to-video workflow
                logger.info(f"✅ Text prompt validated: {prompt[:80]}...")

                # Step 2: Create text-to-video job
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
            logger.info(f"   Status: {result.status}")
            logger.info(f"   Estimated time: {result.estimated_time}s")

            # Step 3: Create VideoHistory record to track this job
            video_type = 'image_to_video' if image_id else 'text_to_video'
            video_history = VideoHistory.objects.create(
                user=self.user,
                prompt=prompt,
                video_type=video_type,
                status='pending',
                runway_task_id=result.task_id,
                duration=duration,
                quality=quality,
                aspect_ratio=ratio
            )

            # Associate with project if provided
            if self.project_id:
                from content.models import Project
                try:
                    project = Project.objects.get(id=self.project_id, user=self.user)
                    video_history.project = project
                    video_history.save()
                    logger.info(f"✅ Video associated with project: {project.name}")
                except Project.DoesNotExist:
                    logger.warning(f"⚠️  Project {self.project_id} not found for user")

            logger.info(f"⏳ Video generation submitted to RunwayML")
            logger.info(f"   Video ID: {video_history.id}")
            logger.info(f"   Frontend will poll for completion")

            return {
                'success': True,
                'video_id': str(video_history.id),
                'task_id': result.task_id,
                'status': result.status,
                'estimated_time_seconds': result.estimated_time,
                'message': f'Video generation started. Estimated time: {result.estimated_time}s'
            }

        except Exception as e:
            logger.error(f"❌ {self.agent_name} failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def check_status(self, video_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation job.

        Args:
            video_id: VideoHistory UUID

        Returns:
            Dict with status, video URL, progress, and completion info
        """
        logger.info(f"🔍 {self.agent_name} checking status for video {video_id}")

        try:
            # Get video record
            video = VideoHistory.objects.get(id=video_id, user=self.user)

            if not video.runway_task_id:
                return {
                    'success': False,
                    'error': 'No RunwayML task ID found for this video'
                }

            # Check status with RunwayML
            result = runway_provider.check_status(video.runway_task_id)

            # Update video record
            status_map = {
                'pending': 'pending',
                'processing': 'processing',
                'completed': 'completed',
                'failed': 'failed'
            }
            video.status = status_map.get(result.status, result.status)

            if result.status == 'completed':
                logger.info(f"✅ Video generation completed!")
                logger.info(f"   Video URL: {result.video_url}")

                # Download and store video
                if result.video_url:
                    video.video_url = result.video_url
                    video.duration = result.duration if result.duration else video.duration
                    logger.info(f"✅ Video URL saved to database")

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
            logger.error(f"❌ Video {video_id} not found")
            return {
                'success': False,
                'error': f'Video {video_id} not found'
            }
        except Exception as e:
            logger.error(f"❌ Status check failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def extend_video(
        self,
        video_id: str,
        extension_seconds: int = 10,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extend an existing video by generating a continuation.

        Args:
            video_id: VideoHistory UUID of video to extend
            extension_seconds: Seconds to add (4-10)
            prompt: Optional prompt to guide extension

        Returns:
            Dict with success status and new video job info
        """
        logger.info(f"🤖 {self.agent_name} extending video {video_id}")
        logger.info(f"   Extension: {extension_seconds}s")

        try:
            # Get original video
            original_video = VideoHistory.objects.get(id=video_id, user=self.user)

            if original_video.status != 'completed':
                return {
                    'success': False,
                    'error': 'Original video must be completed before extending'
                }

            if not original_video.video_url:
                return {
                    'success': False,
                    'error': 'Original video URL not found'
                }

            logger.info(f"✅ Original video validated")
            logger.info(f"   URL: {original_video.video_url}")

            # Use default prompt if not provided
            if not prompt:
                prompt = "Continue the motion and atmosphere from the video"

            # Create extension job
            logger.info(f"🚀 Creating video extension job with RunwayML...")
            result = runway_provider.extend_video(
                video_url=original_video.video_url,
                extension_seconds=extension_seconds,
                prompt=prompt
            )

            if not result.success:
                logger.error(f"❌ Extension failed: {result.error_message}")
                return {
                    'success': False,
                    'error': result.error_message
                }

            logger.info(f"✅ Video extension job created")
            logger.info(f"   Task ID: {result.task_id}")

            # Create new VideoHistory record for extension
            extended_video = VideoHistory.objects.create(
                user=self.user,
                prompt=f"Extension of video {video_id}: {prompt}",
                video_type='video_extension',
                status='pending',
                runway_task_id=result.task_id,
                duration=extension_seconds,
                quality=original_video.quality,
                aspect_ratio=original_video.aspect_ratio,
                project=original_video.project  # Keep same project
            )

            logger.info(f"✅ Extension video record created")
            logger.info(f"   New Video ID: {extended_video.id}")

            return {
                'success': True,
                'video_id': str(extended_video.id),
                'task_id': result.task_id,
                'status': result.status,
                'estimated_time_seconds': result.estimated_time,
                'message': f'Video extension started. Original + {extension_seconds}s extension.'
            }

        except VideoHistory.DoesNotExist:
            logger.error(f"❌ Video {video_id} not found")
            return {
                'success': False,
                'error': f'Video {video_id} not found'
            }
        except Exception as e:
            logger.error(f"❌ {self.agent_name} extend failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _resolve_image_id(self, image_id: str) -> Optional[ImageHistory]:
        """
        Resolve image ID (UUID or sequential number) to ImageHistory object.

        Args:
            image_id: UUID string or sequential number as string

        Returns:
            ImageHistory object or None if not found
        """
        try:
            # Try UUID first
            return ImageHistory.objects.get(id=image_id, user=self.user)
        except (ValueError, ImageHistory.DoesNotExist):
            # Try sequential number
            try:
                seq_num = int(image_id)
                images = ImageHistory.objects.filter(user=self.user).order_by('created_at')
                if seq_num > 0 and seq_num <= images.count():
                    return images[seq_num - 1]
            except (ValueError, IndexError):
                pass

        return None
