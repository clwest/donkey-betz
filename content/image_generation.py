"""
Image Generation Service

Provides image generation using multiple AI providers:
- OpenAI DALL-E 3
- Stable Diffusion (via Stability AI API)
- Replicate (for additional models)
"""

import logging
import time
import requests
import base64
from io import BytesIO
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from PIL import Image

from django.conf import settings
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

# Import required libraries
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import replicate
    HAS_REPLICATE = True
except ImportError:
    HAS_REPLICATE = False


@dataclass
class ImageGenerationResult:
    """Result from image generation"""
    success: bool
    images: List[str] = None  # List of image URLs or base64 data
    error_message: str = ""
    generation_time_ms: int = 0
    provider_used: str = ""
    model_used: str = ""
    cost: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.metadata is None:
            self.metadata = {}


class ImageGenerationService:
    """Service for generating images using various AI providers"""
    
    def __init__(self):
        # Get API keys from settings
        self.openai_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY', '')
        self.stability_key = settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY', '')
        self.replicate_key = settings.AI_PROVIDERS.get('REPLICATE_API_KEY', '')
        
        # Initialize OpenAI client if available
        if HAS_OPENAI and self.openai_key:
            openai.api_key = self.openai_key
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
        else:
            self.openai_client = None
        
        # Initialize Replicate client if available
        if HAS_REPLICATE and self.replicate_key:
            self.replicate_client = replicate.Client(api_token=self.replicate_key)
        else:
            self.replicate_client = None
    
    def generate_image(
        self,
        prompt: str,
        provider: str = 'auto',
        model: str = None,
        size: str = '1024x1024',
        style: str = None,
        negative_prompt: str = None,
        num_images: int = 1,
        quality: str = 'standard',
        cfg_scale: float = 7.0,
        steps: int = 30,
        **kwargs
    ) -> ImageGenerationResult:
        """
        Generate images based on text prompt
        
        Args:
            prompt: Text description of the image
            provider: 'openai', 'stability', 'replicate', or 'auto'
            model: Specific model to use (provider-dependent)
            size: Image size (e.g., '1024x1024', '512x512')
            style: Visual style to apply
            negative_prompt: What to avoid in the image (Stable Diffusion)
            num_images: Number of images to generate
            quality: 'standard' or 'hd' (OpenAI)
            cfg_scale: Classifier-free guidance scale (Stable Diffusion)
            steps: Number of inference steps (Stable Diffusion)
        """
        start_time = time.time()
        
        # Auto-select provider based on availability
        if provider == 'auto':
            if self.stability_key:
                provider = 'stability'
            elif self.openai_client:
                provider = 'openai'
            elif self.replicate_client:
                provider = 'replicate'
            else:
                return ImageGenerationResult(
                    success=False,
                    error_message="No image generation providers available. Please configure API keys."
                )
        
        # Apply style to prompt if provided
        if style:
            prompt = self._apply_style_to_prompt(prompt, style)
        
        # Route to appropriate provider
        if provider == 'openai':
            return self._generate_with_openai(
                prompt, size, num_images, quality, start_time
            )
        elif provider == 'stability':
            return self._generate_with_stability(
                prompt, size, negative_prompt, cfg_scale, steps, num_images, start_time
            )
        elif provider == 'replicate':
            return self._generate_with_replicate(
                prompt, model, size, negative_prompt, num_images, start_time
            )
        else:
            return ImageGenerationResult(
                success=False,
                error_message=f"Unknown provider: {provider}",
                generation_time_ms=int((time.time() - start_time) * 1000)
            )
    
    def _apply_style_to_prompt(self, prompt: str, style: str) -> str:
        """Apply a visual style to the prompt"""
        style_mappings = {
            'photorealistic': f"{prompt}, photorealistic, high quality, detailed photography",
            'digital_art': f"{prompt}, digital art, trending on artstation, highly detailed",
            'oil_painting': f"{prompt}, oil painting, masterpiece, classical art style",
            'watercolor': f"{prompt}, watercolor painting, soft colors, artistic",
            'anime': f"{prompt}, anime style, manga, cel shaded",
            'cyberpunk': f"{prompt}, cyberpunk style, neon lights, futuristic",
            '3d_render': f"{prompt}, 3D render, octane render, unreal engine",
            'pixel_art': f"{prompt}, pixel art, 8-bit style, retro gaming",
            'pop_art': f"{prompt}, pop art style, Andy Warhol style, bold colors",
            'van_gogh': f"{prompt}, Van Gogh style, post-impressionist, swirling brushstrokes",
            'pixar': f"{prompt}, Pixar style, 3D animated movie, Disney Pixar",
            'south_park': f"{prompt}, South Park style, simple cartoon, cut-out animation"
        }
        
        # Use style mapping or append style directly
        return style_mappings.get(style, f"{prompt}, {style} style")
    
    def _generate_with_openai(
        self,
        prompt: str,
        size: str,
        num_images: int,
        quality: str,
        start_time: float
    ) -> ImageGenerationResult:
        """Generate images using OpenAI DALL-E"""
        if not self.openai_client:
            return ImageGenerationResult(
                success=False,
                error_message="OpenAI client not initialized",
                generation_time_ms=int((time.time() - start_time) * 1000)
            )
        
        try:
            # DALL-E 3 supports specific sizes
            dalle_sizes = {
                '1024x1024': '1024x1024',
                '1024x1792': '1024x1792',
                '1792x1024': '1792x1024',
                '512x512': '1024x1024',  # Upscale smaller requests
                '768x768': '1024x1024'
            }
            
            size = dalle_sizes.get(size, '1024x1024')
            
            # Generate images
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1  # DALL-E 3 only supports n=1
            )
            
            # Extract image URLs
            images = [img.url for img in response.data]
            
            # Calculate cost (approximate)
            cost = 0.04 if quality == 'standard' else 0.08  # Per image
            
            return ImageGenerationResult(
                success=True,
                images=images,
                generation_time_ms=int((time.time() - start_time) * 1000),
                provider_used='openai',
                model_used='dall-e-3',
                cost=cost,
                metadata={
                    'size': size,
                    'quality': quality,
                    'revised_prompt': response.data[0].revised_prompt if response.data else None
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI image generation failed: {str(e)}")
            return ImageGenerationResult(
                success=False,
                error_message=str(e),
                generation_time_ms=int((time.time() - start_time) * 1000),
                provider_used='openai'
            )
    
    def _generate_with_stability(
        self,
        prompt: str,
        size: str,
        negative_prompt: str,
        cfg_scale: float,
        steps: int,
        num_images: int,
        start_time: float
    ) -> ImageGenerationResult:
        """Generate images using Stability AI (Stable Diffusion)"""
        if not self.stability_key:
            return ImageGenerationResult(
                success=False,
                error_message="Stability AI API key not configured",
                generation_time_ms=int((time.time() - start_time) * 1000)
            )
        
        try:
            # Parse and adjust size for SDXL requirements
            width, height = map(int, size.split('x'))
            
            # SDXL allowed dimensions
            sdxl_sizes = {
                (512, 512): (1024, 1024),
                (768, 768): (768, 1344),
                (1024, 1024): (1024, 1024),
                (1152, 896): (1152, 896),
                (1216, 832): (1216, 832),
                (1344, 768): (1344, 768),
                (1536, 640): (1536, 640),
                (640, 1536): (640, 1536),
                (768, 1344): (768, 1344),
                (832, 1216): (832, 1216),
                (896, 1152): (896, 1152),
            }
            
            # Find closest valid size
            if (width, height) not in sdxl_sizes.values():
                # Default to 1024x1024 for most cases
                if width <= 1024 and height <= 1024:
                    width, height = 1024, 1024
                elif width > height:
                    width, height = 1344, 768
                else:
                    width, height = 768, 1344
            
            # Stability AI API endpoint
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Authorization": f"Bearer {self.stability_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            body = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": cfg_scale,
                "height": height,
                "width": width,
                "samples": num_images,
                "steps": steps
            }
            
            if negative_prompt:
                body["text_prompts"].append({
                    "text": negative_prompt,
                    "weight": -1
                })
            
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code != 200:
                raise Exception(f"Stability AI error: {response.text}")
            
            data = response.json()
            
            # Extract base64 images and convert to URLs or save
            images = []
            for artifact in data.get("artifacts", []):
                if artifact.get("finishReason") == "SUCCESS":
                    base64_image = artifact.get("base64")
                    if base64_image:
                        # For now, return as data URL
                        images.append(f"data:image/png;base64,{base64_image}")
            
            # Calculate approximate cost
            cost = 0.002 * num_images  # Approximate cost per image
            
            return ImageGenerationResult(
                success=True,
                images=images,
                generation_time_ms=int((time.time() - start_time) * 1000),
                provider_used='stability',
                model_used='stable-diffusion-xl-1024-v1-0',
                cost=cost,
                metadata={
                    'size': size,
                    'cfg_scale': cfg_scale,
                    'steps': steps,
                    'negative_prompt': negative_prompt
                }
            )
            
        except Exception as e:
            logger.error(f"Stability AI image generation failed: {str(e)}")
            return ImageGenerationResult(
                success=False,
                error_message=str(e),
                generation_time_ms=int((time.time() - start_time) * 1000),
                provider_used='stability'
            )
    
    def _generate_with_replicate(
        self,
        prompt: str,
        model: str,
        size: str,
        negative_prompt: str,
        num_images: int,
        start_time: float
    ) -> ImageGenerationResult:
        """Generate images using Replicate"""
        if not self.replicate_client:
            return ImageGenerationResult(
                success=False,
                error_message="Replicate client not initialized",
                generation_time_ms=int((time.time() - start_time) * 1000)
            )
        
        try:
            # Default to SDXL if no model specified
            if not model:
                model = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
            
            width, height = map(int, size.split('x'))
            
            # Run the model
            output = self.replicate_client.run(
                model,
                input={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt or "",
                    "width": width,
                    "height": height,
                    "num_outputs": num_images
                }
            )
            
            # Extract image URLs
            images = []
            if isinstance(output, list):
                images = [str(url) for url in output]
            else:
                images = [str(output)]
            
            return ImageGenerationResult(
                success=True,
                images=images,
                generation_time_ms=int((time.time() - start_time) * 1000),
                provider_used='replicate',
                model_used=model.split(':')[0],
                metadata={
                    'size': size,
                    'negative_prompt': negative_prompt
                }
            )
            
        except Exception as e:
            logger.error(f"Replicate image generation failed: {str(e)}")
            return ImageGenerationResult(
                success=False,
                error_message=str(e),
                generation_time_ms=int((time.time() - start_time) * 1000),
                provider_used='replicate'
            )
    
    def image_to_image(
        self,
        base_image: Any,
        prompt: str,
        strength: float = 0.75,
        provider: str = 'auto',
        **kwargs
    ) -> ImageGenerationResult:
        """Transform an existing image based on a prompt"""
        # Implementation for img2img would go here
        # For now, return a placeholder
        return ImageGenerationResult(
            success=False,
            error_message="Image-to-image not yet implemented"
        )


# Global instance
image_generation_service = ImageGenerationService()