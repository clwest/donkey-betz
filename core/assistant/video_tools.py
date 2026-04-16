"""
Video Tool Handlers for AI Assistant
====================================

Tool execution handlers for video generation and editing operations.
Includes both video generation (Runway ML) and video editing (ffmpeg/DaVinci).

Session 184: Extracted from personal_ai_assistant_enhanced.py
"""

import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class VideoGenerationToolsMixin:
    """
    Mixin class providing video generation tool handler methods.

    This mixin expects the following attributes on the class it's mixed into:
    - self.user: Django User object
    - self.project: Optional CreativeProject object
    """

    def _tool_generate_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the generate_video tool via Video Generation Agent."""
        logger.info("GENERATE_VIDEO TOOL CALLED!")
        logger.info("Delegating to Video Generation Agent...")

        try:
            prompt = arguments['prompt']
            duration = arguments.get('duration', 5)
            image_id = arguments.get('image_id')
            quality = arguments.get('quality', 'gen4_turbo')
            ratio = arguments.get('ratio', '1280:720')

            current_project = getattr(self, 'project', None)

            from core.agents import VideoAgent

            agent = VideoAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('VideoAgent', trigger_source='user_chat'); log_decision(_pd, 'VideoAgent')
            result = agent.execute(
                prompt=prompt,
                image_id=image_id,
                duration=duration,
                quality=quality,
                ratio=ratio
            )

            if result.get('success'):
                video_type = "Image-to-video" if image_id else "Text-to-video"
                message = f"{video_type} generation started!\n\n"
                message += f"Task ID: {result.get('task_id')}\n"
                message += f"Estimated time: {result.get('estimated_time_seconds', 90)}s\n\n"
                message += "The video will automatically appear in the gallery when ready."

                return {
                    'success': True,
                    'video_id': result.get('video_id'),
                    'task_id': result.get('task_id'),
                    'message': message
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video generation failed')
                }

        except Exception as e:
            logger.error(f"Generate video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_extend_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the extend_video tool via Video Generation Agent."""
        logger.info("EXTEND_VIDEO TOOL CALLED!")
        logger.info("Delegating to Video Generation Agent...")

        try:
            video_id = arguments['video_id']
            extension_seconds = arguments.get('extension_seconds', 10)
            prompt = arguments.get('prompt')

            from core.agents import VideoAgent

            agent = VideoAgent(user=self.user, project_id=None)

            result = agent.extend_video(
                video_id=video_id,
                extension_seconds=extension_seconds,
                prompt=prompt
            )

            if result.get('success'):
                message = f"Video extension started!\n\n"
                message += f"Adding {extension_seconds} seconds to video {video_id}\n"
                message += f"Task ID: {result.get('task_id')}\n"
                message += f"Estimated time: {result.get('estimated_time_seconds', 120)}s\n\n"
                message += "The extended video will appear in the gallery when ready."

                return {
                    'success': True,
                    'video_id': result.get('video_id'),
                    'task_id': result.get('task_id'),
                    'message': message
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video extension failed')
                }

        except Exception as e:
            logger.error(f"Extend video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_chain_videos(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the chain_videos tool to combine multiple videos."""
        try:
            from django.test import RequestFactory

            video_ids = arguments['video_ids']
            add_transitions = arguments.get('add_transitions', True)
            project_id = arguments.get('project_id')

            logger.info(f"Chaining {len(video_ids)} videos...")

            factory = RequestFactory()
            data = {
                'video_ids': video_ids,
                'add_transitions': add_transitions
            }
            if project_id:
                data['project_id'] = project_id

            from core.views_video import chain_videos_view
            view_request = factory.post('/api/tool/chain-videos/',
                                       json.dumps(data),
                                       content_type='application/json')
            view_request.user = self.user

            response = chain_videos_view(view_request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'video_url': result.get('video_path'),
                    'message': f"Successfully combined {len(video_ids)} videos!\n\n" +
                              f"Duration: {result.get('duration', 0):.1f}s\n" +
                              f"The combined video is now available in your gallery."
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error_message', 'Video chaining failed')
                }

        except Exception as e:
            logger.error(f"Chain videos tool error: {e}")
            return {'success': False, 'error': str(e)}

    def _tool_animate_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the animate_image tool (image-to-video without speech)."""
        logger.info("ANIMATE_IMAGE TOOL CALLED!")

        try:
            image_id = arguments.get('image_id')
            motion_prompt = arguments.get('motion_prompt', 'natural motion')
            duration = arguments.get('duration', 5)
            project_id = arguments.get('project_id')

            if not image_id:
                return {'success': False, 'error': 'image_id is required'}

            current_project = getattr(self, 'project', None)

            from core.agents import VideoAgent

            agent = VideoAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else project_id
            )

            # Resolve image URL
            image_url = self._resolve_image_url(image_id)
            if not image_url:
                return {'success': False, 'error': f'Could not resolve image {image_id}'}

            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('VideoAgent', trigger_source='user_chat'); log_decision(_pd, 'VideoAgent')
            result = agent.execute(
                prompt=motion_prompt,
                image_id=image_id,
                duration=duration
            )

            if result.get('success'):
                return {
                    'success': True,
                    'video_id': result.get('video_id'),
                    'task_id': result.get('task_id'),
                    'message': f"Image animation started!\n\n" +
                              f"Task ID: {result.get('task_id')}\n" +
                              f"Estimated time: {result.get('estimated_time_seconds', 90)}s\n\n" +
                              "The animated video will appear in the gallery when ready."
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Animation failed')
                }

        except Exception as e:
            logger.error(f"Animate image tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _resolve_image_url(self, image_id: str) -> Optional[str]:
        """Resolve image ID to URL."""
        try:
            from content.models import ImageHistory

            if str(image_id).isdigit():
                images = ImageHistory.objects.filter(user=self.user).order_by('created_at')
                numeric_id = int(image_id)
                if numeric_id > 0 and numeric_id <= images.count():
                    image = images[numeric_id - 1]
                else:
                    return None
            else:
                image = ImageHistory.objects.get(id=image_id, user=self.user)

            if image.file_path:
                if image.file_path.startswith('http'):
                    return image.file_path
                elif image.file_path.startswith('data:'):
                    return None  # Data URIs not supported
                else:
                    path = image.file_path if image.file_path.startswith('/') else f"/{image.file_path}"
                    return f"http://localhost:8000{path}"

            return None

        except Exception as _e:
            logger.warning(
                "video_tools._resolve_image_url: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None

    def _tool_lip_sync(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the lip_sync tool to sync lip movements to audio."""
        logger.info("LIP_SYNC TOOL CALLED!")

        try:
            video_url = arguments.get('video_url')
            audio_url = arguments.get('audio_url')
            sync_mode = arguments.get('sync_mode', 'cut_off')
            temperature = float(arguments.get('temperature', 0.5))

            if not video_url:
                return {'success': False, 'error': 'video_url is required - provide URL to video with face'}

            if not audio_url:
                return {'success': False, 'error': 'audio_url is required - provide URL to audio file'}

            logger.info(f"   Video: {video_url[:60]}...")
            logger.info(f"   Audio: {audio_url[:60]}...")
            logger.info(f"   Mode: {sync_mode}, Temperature: {temperature}")

            from content.replicate_provider import get_replicate_provider

            provider = get_replicate_provider()
            result = provider.lip_sync(
                video_url=video_url,
                audio_url=audio_url,
                sync_mode=sync_mode,
                temperature=temperature,
                active_speaker=False
            )

            if not result.success:
                return {
                    'success': False,
                    'error': result.error_message
                }

            return {
                'success': True,
                'prediction_id': result.prediction_id,
                'status': result.status,
                'estimated_time': result.estimated_time,
                'poll_endpoint': f'/api/video/lip-sync/status/{result.prediction_id}/',
                'message': f"**Lip Sync Started!**\n\n" +
                          f"Your video is being processed to sync lip movements to the audio.\n\n" +
                          f"**Prediction ID:** `{result.prediction_id}`\n" +
                          f"**Estimated Time:** ~{result.estimated_time} seconds\n\n" +
                          f"Use the poll endpoint to check status when complete.",
                'agent': 'LipSyncAgent',
                'operation': 'lip_sync',
                'operation_display': 'Syncing lip movements to audio'
            }

        except Exception as e:
            logger.error(f"Lip sync tool error: {e}")
            return {'success': False, 'error': str(e)}

    def _tool_talking_character(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the talking_character tool.

        Complete pipeline: Image + Text -> Talking Character Video
        Combines TTS (ElevenLabs) + Image-to-Video (Runway) + Lip Sync
        """
        logger.info("TALKING_CHARACTER TOOL CALLED!")

        try:
            image_id = arguments.get('image_id')
            image_url = arguments.get('image_url')
            text = arguments.get('text')
            voice = arguments.get('voice', 'Rachel')
            duration = int(arguments.get('duration', 5))
            motion_prompt = arguments.get('motion_prompt', 'subtle talking motion, slight head movements')
            sync_mode = arguments.get('sync_mode', 'cut_off')
            temperature = float(arguments.get('temperature', 0.5))
            lipsync_model = arguments.get('lipsync_model', 'auto')

            current_project = getattr(self, 'project', None)
            project_id = str(current_project.id) if current_project else arguments.get('project_id')

            # Validate inputs
            if not image_id and not image_url:
                return {'success': False, 'error': 'image_id or image_url is required'}

            if not text:
                return {'success': False, 'error': 'text is required - provide script for character to speak'}

            if duration not in [5, 10]:
                return {'success': False, 'error': 'duration must be 5 or 10 seconds'}

            logger.info(f"   Image ID: {image_id}")
            logger.info(f"   Text: {text[:50]}...")
            logger.info(f"   Voice: {voice}, Duration: {duration}s")

            # Resolve image URL if needed
            if not image_url and image_id:
                image_url = self._resolve_image_url(image_id)
                if not image_url:
                    return {'success': False, 'error': f'Could not resolve image URL for {image_id}'}

            # Create pipeline instance
            from content.talking_character_pipeline import get_talking_character_pipeline

            pipeline = get_talking_character_pipeline(user=self.user)

            # Show cost estimate
            cost_estimate = pipeline.estimate_cost(text, duration)
            logger.info(f"   Estimated cost: ${cost_estimate['total_cost']:.3f}")

            # Start async pipeline
            result = pipeline.generate_talking_video_async(
                image_url=image_url,
                text=text,
                voice=voice,
                motion_prompt=motion_prompt,
                duration=duration,
                sync_mode=sync_mode,
                temperature=temperature,
                lipsync_model=lipsync_model,
                project_id=project_id
            )

            if not result.success:
                return {
                    'success': False,
                    'error': result.error_message,
                    'failed_stage': result.failed_stage
                }

            response = {
                'success': True,
                'status': result.status.value,
                'current_stage': result.current_stage,
                'progress_percent': result.progress_percent,
                'progress_message': result.progress_message,
                'estimated_cost': result.estimated_cost,
                'message': f"**Talking Character Pipeline Started!**\n\n" +
                          f"Your character is being brought to life with speech!\n\n" +
                          f"**Stage:** {result.current_stage}\n" +
                          f"**Progress:** {result.progress_percent}%\n" +
                          f"**Estimated Cost:** ${result.estimated_cost:.3f}\n\n" +
                          f"{result.progress_message}",
                'agent': 'TalkingCharacterAgent',
                'operation': 'talking_character',
                'operation_display': 'Creating talking character video'
            }

            # Add task IDs for polling
            if result.tts_task_id:
                response['tts_task_id'] = result.tts_task_id
            if result.video_task_id:
                response['video_task_id'] = result.video_task_id
                response['video_poll_endpoint'] = f'/api/video/status/{result.video_task_id}/'
            if result.lipsync_task_id:
                response['lipsync_task_id'] = result.lipsync_task_id
                response['lipsync_poll_endpoint'] = f'/api/video/lip-sync/status/{result.lipsync_task_id}/'

            # Add URLs when available
            if result.audio_url:
                response['audio_url'] = result.audio_url
            if result.base_video_url:
                response['base_video_url'] = result.base_video_url
            if result.final_video_url:
                response['final_video_url'] = result.final_video_url

            if project_id:
                response['project_id'] = project_id

            return response

        except Exception as e:
            logger.error(f"Talking character tool error: {e}")
            return {'success': False, 'error': str(e)}


class VideoEditingToolsMixin:
    """
    Mixin class providing video editing tool handler methods.

    Uses ffmpeg for local video processing operations.
    """

    def _make_video_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to make video API requests via RequestFactory."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.post(
            endpoint,
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user = self.user
        return request

    def _tool_extract_video_frame(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Extract a single frame from a video at specified timestamp."""
        logger.info("EXTRACT_VIDEO_FRAME TOOL CALLED!")

        try:
            video_id = arguments.get('video_id')
            timestamp = arguments.get('timestamp', 0.0)
            output_format = arguments.get('format', 'jpg')
            project_id = arguments.get('project_id')

            if not video_id:
                return {'success': False, 'error': 'video_id is required'}

            request = self._make_video_request('/api/video/extract-frame/', {
                'video_id': video_id,
                'timestamp': timestamp,
                'format': output_format,
                'project_id': project_id
            })

            from core.views_video import extract_video_frame
            response = extract_video_frame(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'message': result.get('message', f'Frame extracted at {timestamp}s successfully'),
                    'image_id': result.get('image_id'),
                    'image_url': result.get('image_url'),
                    'timestamp': timestamp,
                    'format': output_format,
                    'agent': 'VideoEditingAgent',
                    'operation': 'extract_frame',
                    'operation_display': f'Extracting frame at {timestamp}s'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Frame extraction failed')
                }

        except Exception as e:
            logger.error(f"Extract video frame tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_reverse_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse a video (play backwards)."""
        logger.info("REVERSE_VIDEO TOOL CALLED!")

        try:
            video_id = arguments.get('video_id')
            reverse_audio = arguments.get('reverse_audio', True)
            project_id = arguments.get('project_id')

            if not video_id:
                return {'success': False, 'error': 'video_id is required'}

            request = self._make_video_request('/api/video/reverse/', {
                'video_id': video_id,
                'reverse_audio': reverse_audio,
                'project_id': project_id
            })

            from core.views_video import reverse_video
            response = reverse_video(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'message': result.get('message', 'Video reversed successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'reverse_audio': reverse_audio,
                    'agent': 'VideoEditingAgent',
                    'operation': 'reverse',
                    'operation_display': f'Reversing video' + (' with audio' if reverse_audio else ' (silent)')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video reverse failed')
                }

        except Exception as e:
            logger.error(f"Reverse video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_trim_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Trim a video to a specific time range."""
        logger.info("TRIM_VIDEO TOOL CALLED!")

        try:
            video_id = arguments.get('video_id')
            start_time = arguments.get('start_time', 0)
            end_time = arguments.get('end_time')
            keep_audio = arguments.get('keep_audio', True)
            project_id = arguments.get('project_id')

            if not video_id:
                return {'success': False, 'error': 'video_id is required'}
            if end_time is None:
                return {'success': False, 'error': 'end_time is required'}

            request = self._make_video_request('/api/video/trim/', {
                'video_id': video_id,
                'start_time': start_time,
                'end_time': end_time,
                'keep_audio': keep_audio,
                'project_id': project_id
            })

            from core.views_video import trim_video
            response = trim_video(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'message': result.get('message', 'Video trimmed successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': result.get('duration'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'trim',
                    'operation_display': f'Trimming video to {start_time}s-{end_time}s'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video trim failed')
                }

        except Exception as e:
            logger.error(f"Trim video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_change_video_speed(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Change video playback speed (slow motion or speed up)."""
        logger.info("CHANGE_VIDEO_SPEED TOOL CALLED!")

        try:
            video_id = arguments.get('video_id')
            params = arguments.get('params', {})
            speed = params.get('speed', arguments.get('speed', 1.0))
            preserve_audio = params.get('preserve_audio', arguments.get('preserve_audio', True))
            project_id = arguments.get('project_id')

            if not video_id:
                return {'success': False, 'error': 'video_id is required'}

            request = self._make_video_request('/api/video/speed/', {
                'video_id': video_id,
                'speed': speed,
                'preserve_audio': preserve_audio,
                'project_id': project_id
            })

            from core.views_video import change_video_speed
            response = change_video_speed(request)
            result = json.loads(response.content)

            if result.get('success'):
                speed_desc = "slow motion" if speed < 1.0 else "sped up" if speed > 1.0 else "normal"
                return {
                    'success': True,
                    'message': result.get('message', f'Video speed changed to {speed}x'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'speed': speed,
                    'original_duration': result.get('original_duration'),
                    'new_duration': result.get('new_duration'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'speed_change',
                    'operation_display': f'Changing video speed to {speed}x ({speed_desc})'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video speed change failed')
                }

        except Exception as e:
            logger.error(f"Change video speed tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_concatenate_videos(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Combine multiple videos into one."""
        logger.info("CONCATENATE_VIDEOS TOOL CALLED!")

        try:
            params = arguments.get('params', {})
            video_ids = params.get('video_ids', arguments.get('video_ids', []))
            project_id = arguments.get('project_id')

            # Parse video_id if video_ids not provided
            if not video_ids and arguments.get('video_id'):
                video_id_str = arguments.get('video_id', '')
                if ',' in video_id_str or '-' in video_id_str:
                    video_ids = self._parse_video_id_range(video_id_str)
                else:
                    video_ids = [video_id_str]

            if not video_ids or len(video_ids) < 2:
                return {'success': False, 'error': 'At least 2 video_ids are required for concatenation'}

            request = self._make_video_request('/api/video/concatenate/', {
                'video_ids': video_ids,
                'project_id': project_id
            })

            from core.views_video import concatenate_videos
            response = concatenate_videos(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'message': result.get('message', 'Videos concatenated successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'video_count': result.get('video_count'),
                    'total_duration': result.get('total_duration'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'concatenate',
                    'operation_display': f'Combining {result.get("video_count")} videos'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video concatenation failed')
                }

        except Exception as e:
            logger.error(f"Concatenate videos tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_rotate_flip_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate or flip a video."""
        logger.info("ROTATE_FLIP_VIDEO TOOL CALLED!")

        try:
            video_id = arguments.get('video_id')
            rotation = arguments.get('rotation', 90)
            project_id = arguments.get('project_id')

            request = self._make_video_request('/api/video/rotate/', {
                'video_id': video_id,
                'rotation': rotation,
                'project_id': project_id
            })

            from core.views_video import rotate_flip_video
            response = rotate_flip_video(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'message': result.get('message', 'Video rotated successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'rotation': result.get('rotation'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'rotate_flip',
                    'operation_display': f'Rotating video {result.get("rotation")}'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Video rotation failed')}

        except Exception as e:
            logger.error(f"Rotate/flip video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_fade_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Add fade in/out effects to a video."""
        logger.info("FADE_VIDEO TOOL CALLED!")

        try:
            video_id = arguments.get('video_id')
            fade_in = arguments.get('fade_in', 1.0)
            fade_out = arguments.get('fade_out', 1.0)
            fade_color = arguments.get('fade_color', 'black')
            project_id = arguments.get('project_id')

            request = self._make_video_request('/api/video/fade/', {
                'video_id': video_id,
                'fade_in': fade_in,
                'fade_out': fade_out,
                'fade_color': fade_color,
                'project_id': project_id
            })

            from core.views_video import fade_video
            response = fade_video(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'message': result.get('message', 'Fade effects added successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'fade_in': result.get('fade_in'),
                    'fade_out': result.get('fade_out'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'fade',
                    'operation_display': 'Adding fade effects'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Fade effect failed')}

        except Exception as e:
            logger.error(f"Fade video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_crop_resize_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Crop, resize, or change aspect ratio of a video."""
        logger.info("CROP_RESIZE_VIDEO TOOL CALLED!")

        try:
            video_id = arguments.get('video_id')
            mode = arguments.get('mode', 'aspect')
            width = arguments.get('width')
            height = arguments.get('height')
            crop_x = arguments.get('crop_x', 0)
            crop_y = arguments.get('crop_y', 0)
            crop_width = arguments.get('crop_width')
            crop_height = arguments.get('crop_height')
            aspect = arguments.get('aspect', '16:9')
            project_id = arguments.get('project_id')

            request = self._make_video_request('/api/video/crop/', {
                'video_id': video_id,
                'mode': mode,
                'width': width,
                'height': height,
                'crop_x': crop_x,
                'crop_y': crop_y,
                'crop_width': crop_width,
                'crop_height': crop_height,
                'aspect': aspect,
                'project_id': project_id
            })

            from core.views_video import crop_resize_video
            response = crop_resize_video(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'message': result.get('message', 'Video cropped/resized successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'mode': result.get('mode'),
                    'new_ratio': result.get('new_ratio'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'crop_resize',
                    'operation_display': result.get('operation_display', 'Cropping/resizing video')
                }
            else:
                return {'success': False, 'error': result.get('error', 'Crop/resize failed')}

        except Exception as e:
            logger.error(f"Crop/resize video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_audio_controls(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust volume, mute, or extract audio from a video."""
        logger.info("AUDIO_CONTROLS TOOL CALLED!")

        try:
            video_id = arguments.get('video_id')
            operation = arguments.get('audio_operation', 'volume')
            volume = arguments.get('volume', 1.0)
            output_format = arguments.get('output_format', 'mp3')
            project_id = arguments.get('project_id')

            request = self._make_video_request('/api/video/audio/', {
                'video_id': video_id,
                'operation': operation,
                'volume': volume,
                'output_format': output_format,
                'project_id': project_id
            })

            from core.views_video import audio_controls
            response = audio_controls(request)
            result = json.loads(response.content)

            if result.get('success'):
                if operation == 'extract':
                    return {
                        'success': True,
                        'message': result.get('message', 'Audio extracted successfully'),
                        'audio_url': result.get('audio_url'),
                        'format': result.get('format'),
                        'source_video_id': result.get('source_video_id'),
                        'agent': 'VideoEditingAgent',
                        'operation': 'audio_extract',
                        'operation_display': f'Extracting audio as {result.get("format", "MP3").upper()}'
                    }
                else:
                    return {
                        'success': True,
                        'message': result.get('message', 'Audio operation completed'),
                        'video_id': result.get('video_id'),
                        'video_url': result.get('video_url'),
                        'agent': 'VideoEditingAgent',
                        'operation': f'audio_{operation}',
                        'operation_display': result.get('operation_display', f'Audio {operation}')
                    }
            else:
                return {'success': False, 'error': result.get('error', 'Audio operation failed')}

        except Exception as e:
            logger.error(f"Audio controls tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_picture_in_picture(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Overlay one video on another (picture-in-picture)."""
        logger.info("PICTURE_IN_PICTURE TOOL CALLED!")

        try:
            bg_video_id = arguments.get('video_id')
            overlay_video_id = arguments.get('overlay_video_id')
            position = arguments.get('position', 'bottom-right')
            scale = arguments.get('scale', 0.25)
            margin = arguments.get('margin', 10)
            opacity = arguments.get('opacity', 1.0)
            project_id = arguments.get('project_id')

            if not overlay_video_id:
                return {'success': False, 'error': 'overlay_video_id is required for picture-in-picture'}

            request = self._make_video_request('/api/video/pip/', {
                'background_video_id': bg_video_id,
                'overlay_video_id': overlay_video_id,
                'position': position,
                'scale': scale,
                'margin': margin,
                'opacity': opacity,
                'project_id': project_id
            })

            from core.views_video import picture_in_picture
            response = picture_in_picture(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'message': result.get('message', 'Picture-in-picture created successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'background_video': result.get('background_video'),
                    'overlay_video': result.get('overlay_video'),
                    'position': result.get('position'),
                    'scale': result.get('scale'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'picture_in_picture',
                    'operation_display': f'Creating PiP with overlay in {position}'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Picture-in-picture failed')}

        except Exception as e:
            logger.error(f"Picture-in-picture tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_add_watermark(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Add an image (logo/watermark) overlay to video."""
        logger.info("ADD_WATERMARK TOOL CALLED!")

        try:
            video_id = arguments.get('video_id')
            image_id = arguments.get('image_id')
            position = arguments.get('position', 'bottom_right')
            scale = arguments.get('scale', 0.15)
            opacity = arguments.get('opacity', 0.8)
            margin = arguments.get('margin', 20)
            project_id = arguments.get('project_id')

            if not image_id:
                return {'success': False, 'error': 'image_id is required for watermark (the logo/watermark image)'}

            request = self._make_video_request('/api/video/watermark/', {
                'video_id': video_id,
                'image_id': image_id,
                'position': position,
                'scale': scale,
                'opacity': opacity,
                'margin': margin,
                'project_id': project_id
            })

            from core.views_video import add_watermark
            response = add_watermark(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'message': result.get('message', 'Watermark added successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'watermark_image_id': result.get('watermark_image_id'),
                    'position': result.get('position'),
                    'scale': result.get('scale'),
                    'opacity': result.get('opacity'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'add_watermark',
                    'operation_display': f'Adding watermark at {position}'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Watermark failed')}

        except Exception as e:
            logger.error(f"Watermark tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_blur_region(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Add blur to a region of video for privacy/censoring."""
        logger.info("BLUR_REGION TOOL CALLED!")

        try:
            video_id = arguments.get('video_id')
            region = arguments.get('region', 'center')
            blur_strength = arguments.get('blur_strength', 15)
            x = arguments.get('x', 0)
            y = arguments.get('y', 0)
            width = arguments.get('width')
            height = arguments.get('height')
            start_time = arguments.get('start_time')
            end_time = arguments.get('end_time')
            project_id = arguments.get('project_id')

            request_data = {
                'video_id': video_id,
                'region': region,
                'blur_strength': blur_strength,
                'x': x,
                'y': y,
                'project_id': project_id
            }
            if width:
                request_data['width'] = width
            if height:
                request_data['height'] = height
            if start_time is not None:
                request_data['start_time'] = start_time
            if end_time is not None:
                request_data['end_time'] = end_time

            request = self._make_video_request('/api/video/blur/', request_data)

            from core.views_video import blur_region
            response = blur_region(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'message': result.get('message', 'Blur added successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'region': result.get('region'),
                    'blur_strength': result.get('blur_strength'),
                    'blur_area': result.get('blur_area'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'blur_region',
                    'operation_display': f'Adding blur at {region}'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Blur failed')}

        except Exception as e:
            logger.error(f"Blur region tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _parse_video_id_range(self, video_id_str: str) -> List[str]:
        """Parse video ID range string into list of IDs."""
        from core.assistant.utils import parse_id_range
        return parse_id_range(video_id_str)
