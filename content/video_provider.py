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
        self.api_base = "https://api.dev.runwayml.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-09-13"
        }
    
    def text_to_video(
        self,
        prompt: str,
        duration: int = 5,
        quality: str = "gen3a_turbo",
        style: str = "realistic",
        enhance_prompt: bool = True,
        enhancement_level: str = "advanced",
        **kwargs
    ) -> VideoGenerationResult:
        """
        Generate video from text prompt using RunwayML Gen-3 Alpha
        
        Args:
            prompt: Text description of the video
            duration: Video duration (5 or 10 seconds)
            quality: "gen3a_turbo" (fast) or "gen3a" (high quality)
            style: Visual style preset
            enhance_prompt: Whether to enhance the prompt
            enhancement_level: Level of prompt enhancement
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
            
            # Prepare request payload
            payload = {
                "model": quality,  # gen3a_turbo or gen3a
                "prompt": prompt,
                "duration": duration,
                "watermark": False,
                "enhance_prompt": False,  # We handle enhancement ourselves
            }
            
            # Add optional parameters
            if kwargs.get('seed'):
                payload['seed'] = kwargs['seed']
            
            # Submit generation request
            response = requests.post(
                f"{self.api_base}/text-to-video",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                return VideoGenerationResult(
                    success=False,
                    error_message=f"RunwayML API error: {response.text}"
                )
            
            data = response.json()
            
            return VideoGenerationResult(
                success=True,
                task_id=data.get('id', ''),
                status='pending',
                estimated_time=self._estimate_generation_time(quality, duration)
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
        quality: str = "gen3a_turbo",
        enhance_prompt: bool = True,
        **kwargs
    ) -> VideoGenerationResult:
        """
        Generate video from image using RunwayML Gen-3 Alpha
        
        Args:
            image_url: URL or base64 of the input image
            motion_prompt: Description of the motion/animation
            duration: Video duration (5 or 10 seconds)
            quality: "gen3a_turbo" or "gen3a"
            enhance_prompt: Whether to enhance the motion prompt
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
            
            # Prepare request payload
            payload = {
                "model": quality,
                "image": image_data,
                "prompt": motion_prompt,
                "duration": duration,
                "watermark": False,
            }
            
            # Add optional parameters
            if kwargs.get('seed'):
                payload['seed'] = kwargs['seed']
            
            # Submit generation request
            response = requests.post(
                f"{self.api_base}/image-to-video",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                return VideoGenerationResult(
                    success=False,
                    error_message=f"RunwayML API error: {response.text}"
                )
            
            data = response.json()
            
            return VideoGenerationResult(
                success=True,
                task_id=data.get('id', ''),
                status='pending',
                estimated_time=self._estimate_generation_time(quality, duration)
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
                headers=self.headers
            )
            
            if response.status_code != 200:
                return VideoGenerationResult(
                    success=False,
                    task_id=task_id,
                    error_message=f"Failed to check status: {response.text}"
                )
            
            data = response.json()
            status = data.get('status', 'unknown')
            
            # Map RunwayML status to our status
            status_map = {
                'PENDING': 'pending',
                'RUNNING': 'processing',
                'SUCCEEDED': 'completed',
                'FAILED': 'failed',
                'CANCELED': 'failed'
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
                result.video_url = data.get('output', {}).get('url', '')
                result.thumbnail_url = data.get('output', {}).get('thumbnail', '')
                result.duration = data.get('output', {}).get('duration', 0)
            
            # Add error message if failed
            if mapped_status == 'failed':
                result.error_message = data.get('failure_reason', 'Generation failed')
            
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
        
        # If it's a URL
        if image_input.startswith('http'):
            # For public URLs, RunwayML can fetch directly
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
        
        # Base estimates (in seconds)
        base_times = {
            'gen3a_turbo': {5: 180, 10: 300},  # 3-5 minutes
            'gen3a': {5: 300, 10: 600}  # 5-10 minutes
        }
        
        return base_times.get(quality, {}).get(duration, 300)


# Singleton instance
runway_provider = RunwayMLProvider()