"""
RunwayML Video Generation Provider

Handles text-to-video and image-to-video generation using RunwayML Gen-3 Alpha.
"""

import logging
import time
import json
import base64
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from django.conf import settings
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


@dataclass
class VideoGenerationResult:
    """Result from video generation"""
    success: bool
    task_id: str = ""
    status: str = "pending"
    video_url: str = ""
    thumbnail_url: str = ""
    duration: int = 0
    error_message: str = ""
    estimated_time: int = 0
    progress: int = 0


class RunwayMLProvider:
    """RunwayML video generation provider"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'RUNWAY_API_KEY', '')
        self.api_base = "https://api.dev.runwayml.com/v1"  # Correct API endpoint
        self.mock_mode = getattr(settings, 'RUNWAY_MOCK_MODE', False)  # Disable mock mode - use real API
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"  # Updated API version
        }
    
    def text_to_video(
        self,
        prompt: str,
        duration: int = 4,
        quality: str = "veo3.1_fast",
        style: str = "realistic",
        enhance_prompt: bool = True,
        enhancement_level: str = "advanced",
        ratio: str = "1920:1080",
        **kwargs
    ) -> VideoGenerationResult:
        """
        Generate video from text prompt using RunwayML

        Args:
            prompt: Text description of the video
            duration: Video duration (4 seconds for veo3.1 models)
            quality: "veo3.1_fast" (fast) or "veo3.1" (high quality)
            style: Visual style preset
            enhance_prompt: Whether to enhance the prompt
            enhancement_level: Level of prompt enhancement
            ratio: Aspect ratio - "1920:1080", "1080:1920", "1280:720", "720:1280"
        """

        if not self.api_key:
            return VideoGenerationResult(
                success=False,
                error_message="RunwayML API key not configured"
            )

        try:
            # Enhance prompt if requested
            if enhance_prompt:
                prompt = self._enhance_prompt(prompt, style, enhancement_level)

            # Map old model names to new ones
            model_mapping = {
                "gen3a_turbo": "veo3.1_fast",
                "gen3a": "veo3.1",
                "gen3_turbo": "veo3.1_fast",
                "gen3": "veo3.1"
            }
            model = model_mapping.get(quality, quality)

            # Prepare request payload (camelCase for Runway API)
            payload = {
                "model": model,
                "promptText": prompt,  # Changed to camelCase
                "duration": duration,
                "ratio": ratio
            }

            # Add optional parameters
            if kwargs.get('seed'):
                payload['seed'] = kwargs['seed']

            # Submit generation request
            response = requests.post(
                f"{self.api_base}/text_to_video",  # Updated endpoint path
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                return VideoGenerationResult(
                    success=False,
                    error_message=f"RunwayML API error ({response.status_code}): {response.text}"
                )

            data = response.json()

            return VideoGenerationResult(
                success=True,
                task_id=data.get('id', ''),
                status='pending',
                estimated_time=self._estimate_generation_time(model, duration)
            )

        except Exception as e:
            logger.error(f"RunwayML text-to-video error: {str(e)}")
            return VideoGenerationResult(
                success=False,
                error_message=str(e)
            )
    
    def image_to_video(
        self,
        image_url: str,
        motion_prompt: str,
        duration: int = 5,
        quality: str = "gen4_turbo",
        enhance_prompt: bool = True,
        ratio: str = "1280:720",
        **kwargs
    ) -> VideoGenerationResult:
        """
        Generate video from image using RunwayML

        Args:
            image_url: URL or base64 of the input image
            motion_prompt: Description of the motion/animation
            duration: Video duration (5 seconds for gen4_turbo)
            quality: "gen4_turbo" (currently the main image-to-video model)
            enhance_prompt: Whether to enhance the motion prompt
            ratio: Aspect ratio - "1280:720", "720:1280", "1104:832", "832:1104", "960:960", "1584:672"
        """

        if not self.api_key:
            return VideoGenerationResult(
                success=False,
                error_message="RunwayML API key not configured"
            )

        try:
            # Enhance motion prompt if requested
            if enhance_prompt:
                motion_prompt = self._enhance_motion_prompt(motion_prompt)

            # Handle image input (URL or base64)
            image_data = self._prepare_image(image_url)

            # Map old model names to new ones
            model_mapping = {
                "gen3a_turbo": "gen4_turbo",
                "gen3a": "gen4_turbo",
                "gen3_turbo": "gen4_turbo",
                "gen3": "gen4_turbo"
            }
            model = model_mapping.get(quality, quality)

            # Prepare request payload (camelCase for Runway API)
            payload = {
                "model": model,
                "promptImage": image_data,  # Changed to camelCase
                "promptText": motion_prompt,  # Changed to camelCase
                "duration": duration,
                "ratio": ratio
            }

            # Add optional parameters
            if kwargs.get('seed'):
                payload['seed'] = kwargs['seed']

            # Log payload (with truncated image data)
            log_payload = payload.copy()
            if isinstance(log_payload.get('promptImage'), str) and len(log_payload['promptImage']) > 100:
                log_payload['promptImage'] = log_payload['promptImage'][:100] + f"... ({len(payload['promptImage'])} chars total)"
            logger.info(f"📤 [RUNWAY] Sending image-to-video request:")
            logger.info(f"   Payload: {log_payload}")

            # Submit generation request
            response = requests.post(
                f"{self.api_base}/image_to_video",  # Updated endpoint path
                headers=self.headers,
                json=payload,
                timeout=30
            )

            logger.info(f"📥 [RUNWAY] Response status: {response.status_code}")

            if response.status_code != 200:
                return VideoGenerationResult(
                    success=False,
                    error_message=f"RunwayML API error ({response.status_code}): {response.text}"
                )

            data = response.json()

            return VideoGenerationResult(
                success=True,
                task_id=data.get('id', ''),
                status='pending',
                estimated_time=self._estimate_generation_time(model, duration)
            )

        except Exception as e:
            logger.error(f"RunwayML image-to-video error: {str(e)}")
            return VideoGenerationResult(
                success=False,
                error_message=str(e)
            )
    
    def check_status(self, task_id: str) -> VideoGenerationResult:
        """
        Check the status of a video generation task

        Args:
            task_id: The task ID from generation request
        """

        if not self.api_key:
            return VideoGenerationResult(
                success=False,
                error_message="RunwayML API key not configured"
            )

        try:
            response = requests.get(
                f"{self.api_base}/tasks/{task_id}",
                headers=self.headers,
                timeout=30
            )

            if response.status_code != 200:
                return VideoGenerationResult(
                    success=False,
                    task_id=task_id,
                    error_message=f"Failed to check status ({response.status_code}): {response.text}"
                )

            data = response.json()
            status = data.get('status', 'unknown')

            # Map RunwayML status to our status
            status_map = {
                'PENDING': 'pending',
                'RUNNING': 'processing',
                'SUCCEEDED': 'completed',
                'FAILED': 'failed',
                'CANCELED': 'failed',
                'THROTTLED': 'pending'
            }

            mapped_status = status_map.get(status, status.lower())

            # Calculate progress based on status
            progress = 0
            if mapped_status == 'processing':
                progress = data.get('progress', 50)
            elif mapped_status == 'completed':
                progress = 100

            result = VideoGenerationResult(
                success=mapped_status == 'completed',
                task_id=task_id,
                status=mapped_status,
                progress=progress
            )

            # Add video URL if completed
            if mapped_status == 'completed':
                # Check for both possible output structures
                output = data.get('output', [])
                if isinstance(output, str):
                    # Output is the URL directly as a string
                    result.video_url = output
                elif isinstance(output, list) and len(output) > 0:
                    # Output is a list of objects
                    if isinstance(output[0], dict):
                        result.video_url = output[0].get('url', '')
                    elif isinstance(output[0], str):
                        result.video_url = output[0]
                elif isinstance(output, dict):
                    # Output is a single object
                    result.video_url = output.get('url', '')
                else:
                    # Try alternate field names
                    result.video_url = data.get('videoUrl', data.get('url', ''))

                result.duration = data.get('duration', 0)

            # Add error message if failed
            if mapped_status == 'failed':
                result.error_message = data.get('failure', data.get('failureReason', 'Generation failed'))

            return result

        except Exception as e:
            logger.error(f"RunwayML status check error: {str(e)}")
            return VideoGenerationResult(
                success=False,
                task_id=task_id,
                error_message=str(e)
            )
    
    def _enhance_prompt(self, prompt: str, style: str, level: str) -> str:
        """Enhance text prompt for better video generation"""
        
        style_enhancements = {
            'cinematic': 'cinematic quality, professional cinematography, film grain, depth of field',
            'realistic': 'photorealistic, natural lighting, high detail, lifelike',
            'anime': 'anime style, cel shaded, vibrant colors, dynamic motion',
            'abstract': 'abstract art, experimental visuals, artistic interpretation',
            'fantasy': 'fantasy art style, magical atmosphere, ethereal lighting',
            'documentary': 'documentary style, handheld camera, authentic feel',
        }
        
        level_enhancements = {
            'basic': 'clear subject, good composition',
            'advanced': 'dynamic camera movement, professional quality, smooth motion',
            'expert': 'masterpiece quality, award-winning cinematography, perfect execution, temporal consistency'
        }
        
        # Build enhanced prompt
        enhanced = prompt
        
        if style in style_enhancements:
            enhanced = f"{enhanced}, {style_enhancements[style]}"
        
        if level in level_enhancements:
            enhanced = f"{enhanced}, {level_enhancements[level]}"
        
        # Add general video quality enhancers
        enhanced = f"{enhanced}, smooth motion, temporal coherence, high quality"
        
        return enhanced
    
    def _enhance_motion_prompt(self, motion_prompt: str) -> str:
        """Enhance motion prompt for image-to-video"""
        
        # Add motion-specific enhancements
        enhanced = f"{motion_prompt}, smooth camera movement, natural motion flow, consistent animation"
        
        # Add common motion descriptors if not present
        motion_keywords = ['zoom', 'pan', 'orbit', 'track', 'dolly', 'tilt']
        if not any(keyword in motion_prompt.lower() for keyword in motion_keywords):
            enhanced = f"{enhanced}, dynamic camera work"
        
        return enhanced
    
    def _prepare_image(self, image_input: str) -> str:
        """Prepare image for API (convert to base64 if needed)"""

        # If it's already a base64 string
        if image_input.startswith('data:image'):
            return image_input

        # Check if it's a local media path (relative or full URL)
        is_local_media = (
            image_input.startswith('/media/') or  # Relative path
            'localhost' in image_input or          # Localhost URL
            '127.0.0.1' in image_input or         # 127.0.0.1 URL
            (image_input.startswith('http') and '/media/' in image_input)  # Any URL with /media/
        )

        if is_local_media:
            # This is a local media file - convert to file path and base64
            try:
                from django.conf import settings
                import os
                from urllib.parse import urlparse, unquote

                # Extract path - handle both relative paths and URLs
                if image_input.startswith('http'):
                    parsed = urlparse(image_input)
                    url_path = unquote(parsed.path)
                else:
                    url_path = image_input

                # Remove /media/ prefix if present
                if url_path.startswith('/media/'):
                    url_path = url_path[7:]  # Remove '/media/'

                # Construct full file path
                file_path = os.path.join(settings.MEDIA_ROOT, url_path)

                logger.info(f"Converting local media to base64: {image_input}")
                logger.info(f"File path: {file_path}")

                # Read file and convert to base64
                with open(file_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')

                    # Detect image type from extension
                    ext = os.path.splitext(file_path)[1].lower()
                    mime_type = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.webp': 'image/webp',
                        '.gif': 'image/gif'
                    }.get(ext, 'image/jpeg')

                    data_uri = f"data:{mime_type};base64,{image_data}"
                    logger.info(f"✅ Converted to base64 ({len(data_uri)} chars)")
                    return data_uri

            except Exception as e:
                logger.error(f"Failed to convert local media to base64: {str(e)}")
                raise Exception(f"Failed to prepare image: {str(e)}")

        # If it's a public URL
        if image_input.startswith('http'):
            # Public URL - RunwayML can fetch directly
            return image_input

        # If it's a local file path, convert to base64
        try:
            with open(image_input, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{image_data}"
        except:
            # Assume it's already in a format RunwayML can handle
            return image_input
    
    def _estimate_generation_time(self, quality: str, duration: int) -> int:
        """Estimate generation time in seconds"""

        # Base estimates (in seconds) for new models
        base_times = {
            'veo3.1_fast': {4: 90, 5: 120},  # 1.5-2 minutes
            'veo3.1': {4: 180, 5: 240},  # 3-4 minutes
            'veo3': {4: 180, 5: 240},  # 3-4 minutes
            'gen4_turbo': {5: 120, 10: 180},  # 2-3 minutes
            'gen4_aleph': {5: 240, 10: 360},  # 4-6 minutes
        }

        return base_times.get(quality, {}).get(duration, 180)

    def video_to_video(
        self,
        video_url: str,
        prompt: str,
        duration: int = 4,
        quality: str = "gen4_aleph",
        reference_images: list = None,
        ratio: str = "1280:720",  # Valid ratio for gen4_aleph (changed from 1920:1080)
        **kwargs
    ) -> VideoGenerationResult:
        """
        Transform existing video with text prompts using RunwayML

        Args:
            video_url: URL or path to input video
            prompt: Description of desired transformation
            duration: Video duration (4-10 seconds)
            quality: "gen4_aleph" (video editing and transformation)
            reference_images: List of reference images for style control
            ratio: Aspect ratio - "1920:1080", "1280:720", etc.
        """

        if not self.api_key:
            return VideoGenerationResult(
                success=False,
                error_message="RunwayML API key not configured"
            )

        try:
            # Prepare video input (URL or base64)
            video_data = self._prepare_video(video_url)

            # Prepare reference images if provided
            references = []
            if reference_images:
                for ref in reference_images:
                    references.append({
                        "type": "image",
                        "uri": self._prepare_image(ref.get('uri', ref)) if isinstance(ref, dict) else self._prepare_image(ref)
                    })

            # Prepare request payload
            payload = {
                "model": quality,
                "videoUri": video_data,
                "promptText": prompt,
                "duration": duration,
                "ratio": ratio
            }

            # Add optional parameters
            if references:
                payload['references'] = references
            if kwargs.get('seed'):
                payload['seed'] = kwargs['seed']

            logger.info(f"📤 [RUNWAY] Sending video-to-video request")

            # Submit generation request
            response = requests.post(
                f"{self.api_base}/video_to_video",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            logger.info(f"📥 [RUNWAY] Response status: {response.status_code}")

            if response.status_code != 200:
                return VideoGenerationResult(
                    success=False,
                    error_message=f"RunwayML API error ({response.status_code}): {response.text}"
                )

            data = response.json()

            return VideoGenerationResult(
                success=True,
                task_id=data.get('id', ''),
                status='pending',
                estimated_time=self._estimate_generation_time(quality, duration)
            )

        except Exception as e:
            logger.error(f"RunwayML video-to-video error: {str(e)}")
            return VideoGenerationResult(
                success=False,
                error_message=str(e)
            )

    def video_upscale(
        self,
        video_url: str,
        **kwargs
    ) -> VideoGenerationResult:
        """
        Upscale video resolution to 4K using RunwayML

        Args:
            video_url: URL or path to input video
        """

        if not self.api_key:
            return VideoGenerationResult(
                success=False,
                error_message="RunwayML API key not configured"
            )

        try:
            # Prepare video input
            video_data = self._prepare_video(video_url)

            # Prepare request payload
            payload = {
                "model": "upscale_v1",
                "videoUri": video_data
            }

            logger.info(f"📤 [RUNWAY] Sending video upscale request")

            # Submit upscale request
            response = requests.post(
                f"{self.api_base}/video_upscale",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            logger.info(f"📥 [RUNWAY] Response status: {response.status_code}")

            if response.status_code != 200:
                return VideoGenerationResult(
                    success=False,
                    error_message=f"RunwayML API error ({response.status_code}): {response.text}"
                )

            data = response.json()

            return VideoGenerationResult(
                success=True,
                task_id=data.get('id', ''),
                status='pending',
                estimated_time=120  # ~2 minutes for upscaling
            )

        except Exception as e:
            logger.error(f"RunwayML video upscale error: {str(e)}")
            return VideoGenerationResult(
                success=False,
                error_message=str(e)
            )

    def text_to_image(
        self,
        prompt: str,
        quality: str = "gen4_image",
        ratio: str = "1920:1080",
        reference_images: list = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image from text prompt using RunwayML

        Args:
            prompt: Text description of the image
            quality: "gen4_image", "gen4_image_turbo", or "gemini_2.5_flash"
            ratio: Aspect ratio - "1920:1080", "1280:720", "960:960", etc.
            reference_images: List of reference images with optional tags
        """

        if not self.api_key:
            return {
                "success": False,
                "error_message": "RunwayML API key not configured"
            }

        try:
            # Prepare reference images if provided
            references = []
            if reference_images:
                for ref in reference_images:
                    ref_obj = {
                        "uri": self._prepare_image(ref.get('uri', ref)) if isinstance(ref, dict) else self._prepare_image(ref)
                    }
                    # Add tag if provided for @-mention in prompt
                    if isinstance(ref, dict) and ref.get('tag'):
                        ref_obj['tag'] = ref['tag']
                    references.append(ref_obj)

            # Prepare request payload
            payload = {
                "model": quality,
                "promptText": prompt,
                "ratio": ratio
            }

            # Add optional parameters
            if references:
                payload['referenceImages'] = references
            if kwargs.get('seed'):
                payload['seed'] = kwargs['seed']

            logger.info(f"📤 [RUNWAY] Sending text-to-image request")

            # Submit generation request
            response = requests.post(
                f"{self.api_base}/text_to_image",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            logger.info(f"📥 [RUNWAY] Response status: {response.status_code}")

            if response.status_code != 200:
                return {
                    "success": False,
                    "error_message": f"RunwayML API error ({response.status_code}): {response.text}"
                }

            data = response.json()

            return {
                "success": True,
                "task_id": data.get('id', ''),
                "status": "pending",
                "estimated_time": 30  # ~30 seconds for image generation
            }

        except Exception as e:
            logger.error(f"RunwayML text-to-image error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def text_to_speech(
        self,
        text: str,
        voice: str = "Rachel",
        model: str = "eleven_multilingual_v2",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convert text to speech using RunwayML/ElevenLabs

        Args:
            text: Text to convert to speech
            voice: Voice name (Rachel, Drew, Clyde, Paul, Aria, Domi, Dave, etc.)
            model: "eleven_multilingual_v2" (default)
        """

        if not self.api_key:
            return {
                "success": False,
                "error_message": "RunwayML API key not configured"
            }

        try:
            # Prepare request payload
            payload = {
                "promptText": text,
                "voice": {
                    "type": "runway-preset",  # Correct type discriminator from API docs!
                    "presetId": voice  # Changed from "name" to "presetId"
                },
                "model": model
            }

            # Add optional parameters
            if kwargs.get('language_code'):
                payload['languageCode'] = kwargs['language_code']
            if kwargs.get('output_format'):
                payload['outputFormat'] = kwargs['output_format']
            if kwargs.get('apply_text_normalization'):
                payload['applyTextNormalization'] = kwargs['apply_text_normalization']

            logger.info(f"📤 [RUNWAY] Sending text-to-speech request")

            # Submit TTS request
            response = requests.post(
                f"{self.api_base}/text_to_speech",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            logger.info(f"📥 [RUNWAY] Response status: {response.status_code}")

            if response.status_code != 200:
                return {
                    "success": False,
                    "error_message": f"RunwayML API error ({response.status_code}): {response.text}"
                }

            data = response.json()

            return {
                "success": True,
                "task_id": data.get('id', ''),
                "status": "pending",
                "estimated_time": 10  # ~10 seconds for TTS
            }

        except Exception as e:
            logger.error(f"RunwayML text-to-speech error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def text_to_sound(
        self,
        prompt: str,
        duration: float = 5.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate sound effects from text description using RunwayML/ElevenLabs

        Args:
            prompt: Description of the sound effect
            duration: Duration in seconds (0.5 to 30)
        """

        if not self.api_key:
            return {
                "success": False,
                "error_message": "RunwayML API key not configured"
            }

        try:
            # Prepare request payload
            payload = {
                "promptText": prompt,  # Changed from "text" to "promptText"
                "duration": duration,
                "model": "eleven_text_to_sound_v2"
            }

            # Add optional parameters
            if kwargs.get('prompt_influence'):
                payload['promptInfluence'] = kwargs['prompt_influence']

            logger.info(f"📤 [RUNWAY] Sending text-to-sound request")

            # Submit sound generation request
            response = requests.post(
                f"{self.api_base}/sound_effect",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            logger.info(f"📥 [RUNWAY] Response status: {response.status_code}")

            if response.status_code != 200:
                return {
                    "success": False,
                    "error_message": f"RunwayML API error ({response.status_code}): {response.text}"
                }

            data = response.json()

            return {
                "success": True,
                "task_id": data.get('id', ''),
                "status": "pending",
                "estimated_time": int(duration) + 5  # Duration + processing time
            }

        except Exception as e:
            logger.error(f"RunwayML text-to-sound error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def character_performance(
        self,
        image_url: str,
        driving_video_url: str = None,
        prompt: str = "",
        **kwargs
    ) -> VideoGenerationResult:
        """
        Animate character from image using RunwayML Act Two

        Args:
            image_url: URL or path to character image
            driving_video_url: Optional driving video for performance
            prompt: Text description of desired performance
        """

        if not self.api_key:
            return VideoGenerationResult(
                success=False,
                error_message="RunwayML API key not configured"
            )

        try:
            # Prepare image input
            image_data = self._prepare_image(image_url)

            # Prepare request payload with proper structure
            # API expects "character" object with type and uri, and "reference" object (always required)
            payload = {
                "model": "act_two",
                "character": {
                    "type": "image",  # Required type discriminator
                    "uri": image_data  # Changed from imageUri to uri
                },
                "reference": {  # Always required, even if no driving video
                    "type": "video" if driving_video_url else "image"
                }
            }

            # Add driving video URI if provided
            if driving_video_url:
                payload['reference']['uri'] = self._prepare_video(driving_video_url)
            else:
                # Use the character image as reference if no driving video
                payload['reference']['uri'] = image_data

            # Add prompt if provided
            if prompt:
                payload['promptText'] = prompt

            logger.info(f"📤 [RUNWAY] Sending character performance request")

            # Submit generation request
            response = requests.post(
                f"{self.api_base}/character_performance",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            logger.info(f"📥 [RUNWAY] Response status: {response.status_code}")

            if response.status_code != 200:
                return VideoGenerationResult(
                    success=False,
                    error_message=f"RunwayML API error ({response.status_code}): {response.text}"
                )

            data = response.json()

            return VideoGenerationResult(
                success=True,
                task_id=data.get('id', ''),
                status='pending',
                estimated_time=120  # ~2 minutes for character animation
            )

        except Exception as e:
            logger.error(f"RunwayML character performance error: {str(e)}")
            return VideoGenerationResult(
                success=False,
                error_message=str(e)
            )

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        Cancel a running generation task

        Args:
            task_id: The task ID to cancel
        """

        if not self.api_key:
            return {
                "success": False,
                "error_message": "RunwayML API key not configured"
            }

        try:
            response = requests.delete(
                f"{self.api_base}/tasks/{task_id}",
                headers=self.headers,
                timeout=30
            )

            if response.status_code not in [200, 204]:
                return {
                    "success": False,
                    "error_message": f"Failed to cancel task ({response.status_code}): {response.text}"
                }

            return {
                "success": True,
                "message": f"Task {task_id} cancelled successfully"
            }

        except Exception as e:
            logger.error(f"RunwayML cancel task error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def get_organization(self) -> Dict[str, Any]:
        """
        Get organization information
        """

        if not self.api_key:
            return {
                "success": False,
                "error_message": "RunwayML API key not configured"
            }

        try:
            response = requests.get(
                f"{self.api_base}/organization",
                headers=self.headers,
                timeout=30
            )

            if response.status_code != 200:
                return {
                    "success": False,
                    "error_message": f"Failed to get organization ({response.status_code}): {response.text}"
                }

            data = response.json()

            return {
                "success": True,
                "organization": data
            }

        except Exception as e:
            logger.error(f"RunwayML get organization error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def get_credit_usage(self) -> Dict[str, Any]:
        """
        Query credit usage and balance
        """

        if not self.api_key:
            return {
                "success": False,
                "error_message": "RunwayML API key not configured"
            }

        try:
            response = requests.post(
                f"{self.api_base}/organization/usage",
                headers=self.headers,
                timeout=30
            )

            if response.status_code != 200:
                return {
                    "success": False,
                    "error_message": f"Failed to get usage ({response.status_code}): {response.text}"
                }

            data = response.json()

            return {
                "success": True,
                "usage": data
            }

        except Exception as e:
            logger.error(f"RunwayML get credit usage error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def voice_dubbing(
        self,
        audio_url: str,
        target_lang: str = "en",
        disable_voice_cloning: bool = False,
        drop_background_audio: bool = False,
        num_speakers: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Dub audio content to a target language

        Args:
            audio_url: URL or data URI of the audio file
            target_lang: Target language code (e.g., "es" for Spanish, "fr" for French)
            disable_voice_cloning: Whether to use generic voice instead of cloning
            drop_background_audio: Whether to remove background audio
            num_speakers: Number of speakers (auto-detected if not provided)

        Returns:
            Dict with success status and task_id
        """

        if not self.api_key:
            return {
                "success": False,
                "error_message": "RunwayML API key not configured"
            }

        try:
            # Prepare request payload
            payload = {
                "audioUri": audio_url,
                "targetLang": target_lang,
                "model": "eleven_voice_dubbing"
            }

            # Add optional parameters
            if disable_voice_cloning is not None:
                payload['disableVoiceCloning'] = disable_voice_cloning
            if drop_background_audio is not None:
                payload['dropBackgroundAudio'] = drop_background_audio
            if num_speakers is not None:
                payload['numSpeakers'] = num_speakers

            logger.info(f"📤 [RUNWAY] Sending voice dubbing request")

            # Submit request
            response = requests.post(
                f"{self.api_base}/voice_dubbing",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            logger.info(f"📥 [RUNWAY] Response status: {response.status_code}")

            if response.status_code != 200:
                return {
                    "success": False,
                    "error_message": f"Voice dubbing failed ({response.status_code}): {response.text}"
                }

            data = response.json()
            task_id = data.get('id')

            return {
                "success": True,
                "task_id": task_id,
                "estimated_time": 30  # Estimated processing time
            }

        except Exception as e:
            logger.error(f"RunwayML voice dubbing error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def voice_isolation(
        self,
        audio_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Isolate voice from background audio
        Audio duration must be > 4.6s and < 3600s

        Args:
            audio_url: URL or data URI of the audio file

        Returns:
            Dict with success status and task_id
        """

        if not self.api_key:
            return {
                "success": False,
                "error_message": "RunwayML API key not configured"
            }

        try:
            # Prepare request payload
            payload = {
                "audioUri": audio_url,
                "model": "eleven_voice_isolation"
            }

            logger.info(f"📤 [RUNWAY] Sending voice isolation request")

            # Submit request
            response = requests.post(
                f"{self.api_base}/voice_isolation",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            logger.info(f"📥 [RUNWAY] Response status: {response.status_code}")

            if response.status_code != 200:
                return {
                    "success": False,
                    "error_message": f"Voice isolation failed ({response.status_code}): {response.text}"
                }

            data = response.json()
            task_id = data.get('id')

            return {
                "success": True,
                "task_id": task_id,
                "estimated_time": 20  # Estimated processing time
            }

        except Exception as e:
            logger.error(f"RunwayML voice isolation error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def speech_to_speech(
        self,
        media_url: str,
        media_type: str,  # "audio" or "video"
        voice: str = "Rachel",
        remove_background_noise: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convert speech from one voice to another in audio or video

        Args:
            media_url: URL or data URI of the audio/video file
            media_type: Type of media ("audio" or "video")
            voice: Preset voice ID to use (e.g., "Rachel", "Maya")
            remove_background_noise: Whether to remove background noise

        Returns:
            Dict with success status and task_id
        """

        if not self.api_key:
            return {
                "success": False,
                "error_message": "RunwayML API key not configured"
            }

        try:
            # Prepare request payload
            payload = {
                "media": {
                    "type": media_type,
                    "uri": media_url
                },
                "voice": {
                    "type": "runway-preset",
                    "presetId": voice
                },
                "model": "eleven_multilingual_sts_v2"
            }

            # Add optional parameters
            if remove_background_noise is not None:
                payload['removeBackgroundNoise'] = remove_background_noise

            logger.info(f"📤 [RUNWAY] Sending speech-to-speech request")

            # Submit request
            response = requests.post(
                f"{self.api_base}/speech_to_speech",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            logger.info(f"📥 [RUNWAY] Response status: {response.status_code}")

            if response.status_code != 200:
                return {
                    "success": False,
                    "error_message": f"Speech-to-speech failed ({response.status_code}): {response.text}"
                }

            data = response.json()
            task_id = data.get('id')

            return {
                "success": True,
                "task_id": task_id,
                "estimated_time": 25  # Estimated processing time
            }

        except Exception as e:
            logger.error(f"RunwayML speech-to-speech error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def _prepare_video(self, video_input: str) -> str:
        """Prepare video for API (convert to URL or base64 if needed)"""

        # If it's already a URL
        if video_input.startswith('http'):
            return video_input

        # If it's a local file path, we'll need to upload it or convert to base64
        # For now, assume it's a URL or will be handled by caller
        return video_input


# Singleton instance
runway_provider = RunwayMLProvider()