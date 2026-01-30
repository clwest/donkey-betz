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
from core.error_messages import ErrorMessageBuilder

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
        # Get API keys from settings - check AI_PROVIDERS dict first
        if hasattr(settings, 'AI_PROVIDERS'):
            self.openai_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY', '')
            # Stability key is in EXTERNAL_API_KEYS, not AI_PROVIDERS
            self.stability_key = settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY', '') if hasattr(settings, 'EXTERNAL_API_KEYS') else ''
            self.replicate_key = settings.AI_PROVIDERS.get('REPLICATE_API_KEY', '')
        else:
            # Fallback to direct attributes
            self.openai_key = getattr(settings, 'OPENAI_API_KEY', '')
            self.stability_key = getattr(settings, 'STABILITY_API_KEY', '')
            self.replicate_key = getattr(settings, 'REPLICATE_API_KEY', '')
        
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
        quality: str = 'balanced',
        cfg_scale: float = 7.0,
        steps: int = 30,
        **kwargs
    ) -> ImageGenerationResult:
        """
        Generate images based on text prompt

        Args:
            prompt: Text description of the image
            provider: 'openai', 'stability', 'replicate', or 'auto'
            model: Specific Stability AI model ('sdxl', 'sd3', 'ultra', 'core') or None for auto
            size: Image size (e.g., '1024x1024', '512x512')
            style: Visual style to apply (69 presets available!)
            negative_prompt: What to avoid in the image (Stable Diffusion)
            num_images: Number of images to generate
            quality: Quality preset - 'fast', 'balanced', 'high', 'premium'
                     fast = Core (3.5s, cost-effective)
                     balanced = SDXL 1.0 (5.8s, very good)
                     high = SD3 (8.7s, excellent)
                     premium = Ultra (10.4s, flagship quality)
            cfg_scale: Classifier-free guidance scale (Stable Diffusion)
            steps: Number of inference steps (Stable Diffusion)
        """
        start_time = time.time()

        # Auto-select provider based on availability (Stable Diffusion priority)
        if provider == 'auto':
            if self.stability_key:
                provider = 'stability'  # First priority: Stable Diffusion
            elif self.replicate_client:
                provider = 'replicate'  # Second priority: Replicate (for SDXL)
            elif self.openai_client:
                provider = 'openai'     # Last priority: DALL-E
            else:
                return ImageGenerationResult(
                    success=False,
                    error_message="No image generation providers available. Please configure API keys."
                )

        # Map quality presets to Stability AI models
        quality_to_model = {
            'fast': 'core',        # Stable Image Core - 3.5s
            'balanced': 'sdxl',    # SDXL 1.0 - 5.8s
            'high': 'sd3',         # SD3 - 8.7s
            'premium': 'ultra',    # Stable Image Ultra - 10.4s
            'standard': 'balanced' # Alias for backward compatibility
        }

        # If quality preset is provided and no explicit model, use the mapping
        if provider == 'stability' and not model:
            model = quality_to_model.get(quality, 'balanced')

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
                prompt, size, negative_prompt, cfg_scale, steps, num_images, start_time, model
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
        """Apply a visual style to the prompt - optimized for Stable Diffusion"""
        # Stable Diffusion optimized style prompts - 50+ styles!
        style_mappings = {
            # Photography Styles
            'photorealistic': f"{prompt}, photorealistic, ultra detailed, professional photography, 8k uhd, dslr, high quality, film grain, Fujifilm XT3",
            'photographic': f"{prompt}, photorealistic, ultra detailed, professional photography, 8k uhd, dslr, high quality",
            'portrait': f"{prompt}, portrait photography, 85mm lens, f/1.8, shallow depth of field, studio lighting, professional headshot",
            'landscape': f"{prompt}, landscape photography, wide angle, golden hour, dramatic sky, national geographic quality",
            'macro': f"{prompt}, macro photography, extreme close-up, detailed texture, shallow depth of field, nature photography",
            'street': f"{prompt}, street photography, candid, urban, documentary style, henri cartier-bresson inspired",
            'fashion': f"{prompt}, fashion photography, vogue style, high fashion, editorial, studio lighting, professional model",
            'architectural': f"{prompt}, architectural photography, clean lines, modern architecture, professional real estate photo",
            'black_white': f"{prompt}, black and white photography, high contrast, dramatic lighting, ansel adams style",
            'vintage': f"{prompt}, vintage photography, retro, old film camera, grainy, sepia tones, 1950s style",

            # Digital Art Styles
            'digital-art': f"{prompt}, digital art, trending on artstation, highly detailed, concept art, sharp focus, illustration",
            'digital_art': f"{prompt}, digital art, trending on artstation, highly detailed, concept art, sharp focus, illustration",
            'concept_art': f"{prompt}, concept art, professional, detailed, game art, cinematic, artstation showcase",
            'matte_painting': f"{prompt}, matte painting, cinematic, epic scale, detailed environment, movie concept art",
            'vector': f"{prompt}, vector art, clean lines, flat design, adobe illustrator style, minimalist",
            'low_poly': f"{prompt}, low poly art, geometric, faceted, 3d modeling, polygon art style",
            'voxel': f"{prompt}, voxel art, 3d pixels, minecraft style, cubic, blocky aesthetic",
            'isometric': f"{prompt}, isometric art, 3d illustration, technical drawing, architectural visualization",

            # Traditional Art Styles
            'oil_painting': f"{prompt}, oil painting on canvas, masterpiece, classical art style, detailed brushstrokes, museum quality",
            'watercolor': f"{prompt}, watercolor painting, soft colors, artistic, wet on wet technique, paper texture",
            'acrylic': f"{prompt}, acrylic painting, vibrant colors, textured canvas, contemporary art",
            'gouache': f"{prompt}, gouache painting, opaque watercolor, illustration, children's book art style",
            'ink': f"{prompt}, ink drawing, pen and ink, crosshatching, detailed linework, traditional illustration",
            'charcoal': f"{prompt}, charcoal drawing, dramatic shadows, sketch, artistic study, fine art",
            'pencil': f"{prompt}, pencil drawing, detailed sketch, graphite, realistic shading, academic drawing",
            'pastel': f"{prompt}, pastel painting, soft colors, impressionist style, textured paper",

            # Animation & Comic Styles
            'anime': f"{prompt}, anime style, manga art, cel shaded, by makoto shinkai, studio ghibli style",
            'manga': f"{prompt}, manga style, black and white, japanese comic art, detailed linework, shounen style",
            'pixar': f"{prompt}, Pixar 3D animation style, Disney Pixar movie quality, subsurface scattering, detailed",
            'disney': f"{prompt}, Disney animation style, classic cartoon, hand-drawn animation quality",
            'dreamworks': f"{prompt}, DreamWorks 3D animation style, stylized expressive characters, bold rounded shapes, vibrant saturated colors, smooth shading, cinematic lighting, professional animation quality",
            'south_park': f"{prompt}, South Park animation style, simple 2D cutout animation, flat colors, basic shapes, crude cartoon style, construction paper aesthetic",
            'southpark': f"{prompt}, South Park animation style, simple 2D cutout animation, flat colors, basic shapes, crude cartoon style, construction paper aesthetic",
            'simpsons': f"{prompt}, The Simpsons animation style, yellow skin tones, overbite characters, bold outlines, bright saturated colors, Matt Groening style",
            'family_guy': f"{prompt}, Family Guy animation style, simple cartoon, bold outlines, exaggerated features, Seth MacFarlane style, adult animated series",
            'ghibli': f"{prompt}, Studio Ghibli anime style, hand-drawn animation, watercolor backgrounds, soft colors, detailed environments, Hayao Miyazaki aesthetic, whimsical atmosphere",
            'studio_ghibli': f"{prompt}, Studio Ghibli anime style, hand-drawn animation, watercolor backgrounds, soft colors, detailed environments, Hayao Miyazaki aesthetic, whimsical atmosphere",
            'comic': f"{prompt}, comic book style, marvel comics, detailed ink lines, dynamic pose, action scene",
            'cartoon': f"{prompt}, cartoon style, simple, colorful, animated series quality, nickelodeon style",
            'chibi': f"{prompt}, chibi style, super deformed, cute, kawaii, big head small body",
            'looney_tunes': f"{prompt}, Looney Tunes classic cartoon style, exaggerated expressions, slapstick animation, Warner Bros aesthetic, vibrant colors, rubberhose animation",
            'rick_and_morty': f"{prompt}, Rick and Morty animation style, Adult Swim aesthetic, wobbly lines, sci-fi cartoon, vibrant neon colors, Justin Roiland style",
            'archer': f"{prompt}, Archer animation style, stylized adult animation, bold graphic lines, mid-century modern aesthetic, spy thriller cartoon",
            'adventure_time': f"{prompt}, Adventure Time animation style, Pendleton Ward style, simple round shapes, pastel colors, whimsical cartoon, Cartoon Network aesthetic",
            'gravity_falls': f"{prompt}, Gravity Falls animation style, Alex Hirsch style, mystery cartoon aesthetic, detailed backgrounds, Disney XD quality",
            'bojack': f"{prompt}, BoJack Horseman animation style, anthropomorphic characters, flat colors, adult animation, melancholic aesthetic, Netflix animated series style",

            # Artistic Movements
            'impressionist': f"{prompt}, impressionist painting, monet style, loose brushwork, light and color focus",
            'expressionist': f"{prompt}, expressionist art, emotional, bold colors, distorted forms, german expressionism",
            'surreal': f"{prompt}, surrealism, salvador dali inspired, dreamlike, impossible geometry, melting objects",
            'abstract': f"{prompt}, abstract art, non-representational, modern art, kandinsky style, geometric shapes",
            'cubist': f"{prompt}, cubist style, pablo picasso inspired, geometric fragmentation, multiple perspectives",
            'art_nouveau': f"{prompt}, art nouveau style, alphonse mucha inspired, decorative, flowing lines, ornamental",
            'art_deco': f"{prompt}, art deco style, 1920s aesthetic, geometric patterns, luxury, great gatsby era",
            'pop_art': f"{prompt}, pop art style, Andy Warhol inspired, Roy Lichtenstein, bold colors, halftone dots",
            'minimalist': f"{prompt}, minimalist style, simple composition, clean lines, negative space, modern art",
            'baroque': f"{prompt}, baroque style painting, dramatic lighting, rich colors, ornate details, caravaggio inspired",
            'renaissance': f"{prompt}, renaissance style painting, leonardo da vinci inspired, classical, realistic, sfumato technique",

            # Genre Styles
            'fantasy': f"{prompt}, fantasy art, magical, ethereal, epic composition, dramatic lighting, artstation winner",
            'scifi': f"{prompt}, science fiction art, futuristic, space art, technological, alien worlds, star wars style",
            'cyberpunk': f"{prompt}, cyberpunk style, neon lights, futuristic city, blade runner 2049, high tech low life",
            'steampunk': f"{prompt}, steampunk style, victorian era, brass and copper, gears and clockwork, industrial",
            'gothic': f"{prompt}, gothic art style, dark atmosphere, medieval, cathedral architecture, dark fantasy",
            'horror': f"{prompt}, horror art style, dark, scary, atmospheric, lovecraftian, disturbing imagery",
            'retro': f"{prompt}, retro style, 80s aesthetic, synthwave, neon colors, miami vice, nostalgic",
            'vaporwave': f"{prompt}, vaporwave aesthetic, 90s nostalgia, purple and pink, glitch art, japanese text",

            # 3D & Rendering Styles
            '3d_render': f"{prompt}, 3D render, octane render, unreal engine 5, ray tracing, physically based rendering, 4k",
            'clay_render': f"{prompt}, clay render, 3d sculpture, zbrush, soft lighting, subsurface scattering",
            'wireframe': f"{prompt}, wireframe render, 3d mesh, technical visualization, CAD model, blueprint style",

            # Special Effects
            'neon': f"{prompt}, neon lights, glowing effects, cyberpunk aesthetic, dark background, vibrant colors",
            'holographic': f"{prompt}, holographic effect, iridescent, rainbow reflections, futuristic, prismatic",
            'glitch': f"{prompt}, glitch art, digital distortion, corrupted data, pixel sorting, databending",

            # Cultural Styles
            'japanese': f"{prompt}, traditional japanese art, ukiyo-e style, woodblock print, hokusai inspired",
            'chinese': f"{prompt}, traditional chinese painting, ink wash, mountain water, calligraphy, sung dynasty style",
            'indian': f"{prompt}, indian art style, vibrant colors, intricate patterns, mandala, rajasthani miniature",
            'african': f"{prompt}, african art style, tribal patterns, bold geometric shapes, traditional masks",
            'aztec': f"{prompt}, aztec art style, pre-columbian, geometric patterns, gold and turquoise, temple art",

            # Other Unique Styles
            'pixel_art': f"{prompt}, pixel art, 16-bit style, retro gaming aesthetic, sprite art",
            'graffiti': f"{prompt}, graffiti art, street art, spray paint, urban, banksy style, wall mural",
            'collage': f"{prompt}, collage art, mixed media, paper cutouts, layered composition, contemporary art",
            'mosaic': f"{prompt}, mosaic art, tile work, byzantine style, colored glass pieces, ancient roman",
            'stained_glass': f"{prompt}, stained glass window, cathedral art, translucent colors, lead lines, religious art",
            'origami': f"{prompt}, origami art, paper folding, geometric shapes, japanese paper art, minimalist",
            'psychedelic': f"{prompt}, psychedelic art, trippy, swirling colors, 1960s style, kaleidoscope patterns"
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
            error = ErrorMessageBuilder.api_key_error("OpenAI", "OPENAI_API_KEY")
            return ImageGenerationResult(
                success=False,
                error_message=error["user_message"],
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
        start_time: float,
        model: str = 'balanced'
    ) -> ImageGenerationResult:
        """
        Generate images using Stability AI

        Supports 4 models:
        - 'core' / 'fast': Stable Image Core (fastest, cost-effective)
        - 'sdxl' / 'balanced': SDXL 1.0 (legacy, very good quality)
        - 'sd3' / 'high': SD3 (latest base model, excellent quality)
        - 'ultra' / 'premium': Stable Image Ultra (flagship, best quality)
        """
        if not self.stability_key:
            error = ErrorMessageBuilder.api_key_error("Stability AI", "STABILITY_API_KEY")
            return ImageGenerationResult(
                success=False,
                error_message=error["user_message"],
                generation_time_ms=int((time.time() - start_time) * 1000)
            )

        # Map model aliases
        model_map = {
            'fast': 'core',
            'balanced': 'sdxl',
            'high': 'sd3',
            'premium': 'ultra',
            'standard': 'sdxl'
        }
        model = model_map.get(model, model)

        # Route to appropriate model implementation
        if model == 'sdxl':
            return self._generate_with_sdxl(
                prompt, size, negative_prompt, cfg_scale, steps, num_images, start_time
            )
        elif model in ['sd3', 'core', 'ultra']:
            return self._generate_with_stable_image(
                model, prompt, size, negative_prompt, num_images, start_time
            )
        else:
            # Default to balanced (SDXL)
            return self._generate_with_sdxl(
                prompt, size, negative_prompt, cfg_scale, steps, num_images, start_time
            )

    def _generate_with_sdxl(
        self,
        prompt: str,
        size: str,
        negative_prompt: str,
        cfg_scale: float,
        steps: int,
        num_images: int,
        start_time: float
    ) -> ImageGenerationResult:
        """Generate images using SDXL 1.0 (JSON API)"""
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
                if width <= 1024 and height <= 1024:
                    width, height = 1024, 1024
                elif width > height:
                    width, height = 1344, 768
                else:
                    width, height = 768, 1344

            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

            headers = {
                "Authorization": f"Bearer {self.stability_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            body = {
                "text_prompts": [{"text": prompt, "weight": 1}],
                "cfg_scale": cfg_scale,
                "height": height,
                "width": width,
                "samples": num_images,
                "steps": steps
            }

            if negative_prompt:
                body["text_prompts"].append({"text": negative_prompt, "weight": -1})

            # Session 872: Use centralized service with retry logic and adaptive timeout
            from core.services.stability_ai_service import (
                stability_request_with_retry, calculate_adaptive_timeout
            )

            timeout = calculate_adaptive_timeout('sdxl', num_images)
            result = stability_request_with_retry(
                url=url,
                headers=headers,
                json_data=body,
                timeout=timeout,
                max_retries=3,
                accept_type="application/json"
            )

            if not result['success']:
                error = ErrorMessageBuilder.parse_api_error(
                    "Stability AI", result.get('status_code', 500), result.get('error', 'Unknown error')
                )
                raise Exception(error["user_message"])

            data = result['data']

            # Extract base64 images and seeds
            images = []
            seeds = []
            finish_reasons = []  # Session 806: Track finish reasons for debugging
            for artifact in data.get("artifacts", []):
                finish_reason = artifact.get("finishReason", "UNKNOWN")
                finish_reasons.append(finish_reason)
                if finish_reason == "SUCCESS":
                    base64_image = artifact.get("base64")
                    seed = artifact.get("seed")  # Extract seed for reproducibility
                    if base64_image:
                        images.append(f"data:image/png;base64,{base64_image}")
                        seeds.append(seed if seed is not None else 0)

            # Session 806: Check if any images were generated
            if not images:
                # Log what happened for debugging
                logger.warning(f"SDXL returned no successful images. Finish reasons: {finish_reasons}")
                error_msg = "No images generated"
                if "CONTENT_FILTERED" in finish_reasons:
                    error_msg = "Image blocked by content moderation"
                elif "ERROR" in finish_reasons:
                    error_msg = "Stability AI returned an error during generation"
                elif not finish_reasons:
                    error_msg = "Stability AI returned no artifacts"
                return ImageGenerationResult(
                    success=False,
                    error_message=error_msg,
                    generation_time_ms=int((time.time() - start_time) * 1000),
                    provider_used='stability',
                    model_used='sdxl-1.0',
                    metadata={'finish_reasons': finish_reasons}
                )

            return ImageGenerationResult(
                success=True,
                images=images,
                generation_time_ms=int((time.time() - start_time) * 1000),
                provider_used='stability',
                model_used='sdxl-1.0',
                cost=0.002 * num_images,
                metadata={
                    'size': f"{width}x{height}",
                    'cfg_scale': cfg_scale,
                    'steps': steps,
                    'negative_prompt': negative_prompt,
                    'seeds': seeds  # Session 95: Add seeds for reproducibility
                }
            )

        except Exception as e:
            logger.error(f"SDXL generation failed: {str(e)}")
            return ImageGenerationResult(
                success=False,
                error_message=str(e),
                generation_time_ms=int((time.time() - start_time) * 1000),
                provider_used='stability'
            )

    def _generate_with_stable_image(
        self,
        model: str,
        prompt: str,
        size: str,
        negative_prompt: str,
        num_images: int,
        start_time: float
    ) -> ImageGenerationResult:
        """
        Generate images using Stable Image API (SD3, Core, Ultra)
        Uses multipart/form-data format
        """
        try:
            # Map models to endpoints
            endpoints = {
                'sd3': 'https://api.stability.ai/v2beta/stable-image/generate/sd3',
                'core': 'https://api.stability.ai/v2beta/stable-image/generate/core',
                'ultra': 'https://api.stability.ai/v2beta/stable-image/generate/ultra'
            }

            url = endpoints.get(model)
            if not url:
                raise ValueError(f"Unknown Stable Image model: {model}")

            # Parse size to aspect ratio
            width, height = map(int, size.split('x'))
            if width == height:
                aspect_ratio = "1:1"
            elif width > height:
                aspect_ratio = "16:9" if width / height > 1.5 else "4:3"
            else:
                aspect_ratio = "9:16" if height / width > 1.5 else "3:4"

            headers = {
                "authorization": f"Bearer {self.stability_key}",
                "accept": "image/*"
            }

            # Build form data
            payload = {
                "prompt": prompt,
                "output_format": "png",
                "aspect_ratio": aspect_ratio
            }

            if negative_prompt:
                payload["negative_prompt"] = negative_prompt

            # Session 872: Use centralized service with retry logic and adaptive timeout
            from core.services.stability_ai_service import (
                stability_request_with_retry, calculate_adaptive_timeout
            )

            # Note: num_images > 1 may not be supported by all models
            # We'll generate multiple times if needed
            images = []
            total_cost = 0

            for _ in range(num_images):
                timeout = calculate_adaptive_timeout(model, 1)
                result = stability_request_with_retry(
                    url=url,
                    headers=headers,
                    files={"none": ''},  # Makes it multipart/form-data
                    data=payload,
                    timeout=timeout,
                    max_retries=3,
                    accept_type="image/*"
                )

                if not result['success']:
                    error = ErrorMessageBuilder.parse_api_error(
                        "Stability AI", result.get('status_code', 500), result.get('error', 'Unknown error')
                    )
                    raise Exception(error["user_message"])

                # Response is raw image bytes
                image_bytes = result['content']
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                images.append(f"data:image/png;base64,{base64_image}")

                # Approximate costs (adjust as needed)
                model_costs = {
                    'core': 0.003,   # Cost-effective
                    'sd3': 0.0065,   # Standard
                    'ultra': 0.008   # Premium
                }
                total_cost += model_costs.get(model, 0.005)

            # Session 806: Check if any images were generated
            if not images:
                logger.warning(f"Stable Image ({model}) returned no images")
                return ImageGenerationResult(
                    success=False,
                    error_message=f"No images generated by {model} model",
                    generation_time_ms=int((time.time() - start_time) * 1000),
                    provider_used='stability',
                    model_used=model
                )

            return ImageGenerationResult(
                success=True,
                images=images,
                generation_time_ms=int((time.time() - start_time) * 1000),
                provider_used='stability',
                model_used=model,
                cost=total_cost,
                metadata={
                    'aspect_ratio': aspect_ratio,
                    'negative_prompt': negative_prompt,
                    'original_size': size
                }
            )

        except Exception as e:
            logger.error(f"Stable Image ({model}) generation failed: {str(e)}")
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
            error = ErrorMessageBuilder.api_key_error("Replicate", "REPLICATE_API_KEY")
            return ImageGenerationResult(
                success=False,
                error_message=error["user_message"],
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
        model: str = 'sd3',
        negative_prompt: str = '',
        **kwargs
    ) -> ImageGenerationResult:
        """
        Transform an existing image based on a prompt using Stability AI Structure Control

        Args:
            base_image: Either a file path (str), URL (str), or PIL Image object
            prompt: Text description of desired output
            strength: How much to transform (0.0-1.0, higher = more change)
            provider: 'stability' or 'auto'
            model: 'sd3', 'core', or 'ultra'
            negative_prompt: What to avoid

        Returns:
            ImageGenerationResult with transformed image
        """
        start_time = time.time()

        # Auto-select provider
        if provider == 'auto':
            provider = 'stability' if self.stability_key else None

        if not provider or provider == 'stability':
            if not self.stability_key:
                return ImageGenerationResult(
                    success=False,
                    error_message="Stability AI API key not configured",
                    generation_time_ms=int((time.time() - start_time) * 1000)
                )
            return self._image_to_image_stability(
                base_image, prompt, strength, model, negative_prompt, start_time
            )
        else:
            return ImageGenerationResult(
                success=False,
                error_message=f"Image-to-image not supported for provider: {provider}",
                generation_time_ms=int((time.time() - start_time) * 1000)
            )

    def _image_to_image_stability(
        self,
        base_image: Any,
        prompt: str,
        strength: float,
        model: str,
        negative_prompt: str,
        start_time: float
    ) -> ImageGenerationResult:
        """
        Stability AI image-to-image using Structure Control
        This maintains the composition/structure of the reference image
        """
        try:
            from PIL import Image
            import io

            # Map model to endpoint
            endpoints = {
                'sd3': 'https://api.stability.ai/v2beta/stable-image/control/structure',
                'core': 'https://api.stability.ai/v2beta/stable-image/control/structure',
                'ultra': 'https://api.stability.ai/v2beta/stable-image/control/structure'
            }

            url = endpoints.get(model, endpoints['sd3'])

            # Load and prepare the base image
            if isinstance(base_image, str):
                # Could be file path or URL
                if base_image.startswith('http'):
                    # Download from URL
                    response = requests.get(base_image, timeout=30)
                    response.raise_for_status()
                    img = Image.open(io.BytesIO(response.content))
                elif base_image.startswith('data:image'):
                    # Base64 data URI
                    base64_data = base_image.split(',', 1)[1]
                    img_data = base64.b64decode(base64_data)
                    img = Image.open(io.BytesIO(img_data))
                else:
                    # File path
                    img = Image.open(base_image)
            else:
                # Assume PIL Image
                img = base_image

            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize if too large (Stability AI max is usually 1024x1024 or 2048x2048)
            max_size = 1024
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # Prepare API request
            headers = {
                "authorization": f"Bearer {self.stability_key}",
                "accept": "image/*"
            }

            # Build form data
            files = {
                "image": ("reference.png", img_bytes, "image/png")
            }

            data = {
                "prompt": prompt,
                "control_strength": strength,  # 0.0-1.0, how much to preserve structure
                "output_format": "png"
            }

            if negative_prompt:
                data["negative_prompt"] = negative_prompt

            # Make request
            response = requests.post(
                url,
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )

            if response.status_code != 200:
                raise Exception(f"Stability API error ({response.status_code}): {response.text[:200]}")

            # Response is raw image bytes
            image_bytes = response.content
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            # Approximate cost
            model_costs = {
                'core': 0.003,
                'sd3': 0.0065,
                'ultra': 0.008
            }
            cost = model_costs.get(model, 0.005)

            return ImageGenerationResult(
                success=True,
                images=[f"data:image/png;base64,{base64_image}"],
                generation_time_ms=int((time.time() - start_time) * 1000),
                provider_used='stability',
                model_used=f'{model}-structure-control',
                cost=cost,
                metadata={
                    'strength': strength,
                    'negative_prompt': negative_prompt,
                    'method': 'structure-control'
                }
            )

        except Exception as e:
            logger.error(f"Stability image-to-image failed: {str(e)}")
            return ImageGenerationResult(
                success=False,
                error_message=str(e),
                generation_time_ms=int((time.time() - start_time) * 1000),
                provider_used='stability'
            )


# Global instance
image_generation_service = ImageGenerationService()