"""
Image Agent - Unified Image Specialist
======================================

Session 202: CREATED - Consolidated from ImageEditingAgent, LogoAgent, SocialMediaAgent, EditingOrchestratorAgent
Session 203: Added preference learning and memory (Phase 4)
Session 255: Added Time Travel Debugging for decision tracking

This is the ONE agent for ALL image operations:
- Image generation with 80+ built-in styles
- Logo generation with brand expertise
- Social media content with platform-specific sizing
- Image editing (upscale, remove_bg, variations, recolor, etc.)
- Multi-step editing workflows
- USER PREFERENCE LEARNING (Session 203)
- TIME TRAVEL DEBUGGING (Session 255)

Example Usage:
    image_agent = ImageAgent(user=request.user)

    # Generate any image with style
    result = image_agent.generate(prompt="A dancing donkey", style="pixar")

    # Generate with user's learned preferences applied automatically
    result = image_agent.generate(prompt="A dancing donkey")  # Uses learned style!

    # Generate a logo with brand expertise
    result = image_agent.generate_logo(brand_name="TechCorp", industry="technology")

    # Generate social media content
    result = image_agent.generate_social(prompt="New product launch", platform="instagram_square")

    # Edit an image
    result = image_agent.edit(image_id='123', operation='upscale')

    # Get user's preferences
    prefs = image_agent.get_user_preferences()
"""

from __future__ import annotations

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import RequestFactory
import json

from content.models import ImageHistory
from content.image_generation import ImageGenerationService
from agents.time_travel_mixin import TimeTravelMixin

logger = logging.getLogger(__name__)
User = get_user_model()


class ImageAgent(TimeTravelMixin):
    """
    Unified agent for all image operations.
    Session 202: Consolidates ImageEditingAgent, LogoAgent, SocialMediaAgent, EditingOrchestratorAgent.
    """

    # Platform size presets (from SocialMediaAgent)
    PLATFORM_SIZES = {
        'instagram_square': '1080x1080',
        'instagram_portrait': '1080x1350',
        'instagram_story': '1080x1920',
        'facebook_post': '1200x1200',
        'facebook_link': '1200x630',
        'twitter_post': '1200x675',
        'twitter_header': '1500x500',
        'linkedin_post': '1200x627',
        'linkedin_banner': '1584x396',
        'youtube_thumbnail': '1280x720',
        'logo': '1024x1024',
    }

    def __init__(self, user: Optional[User] = None, project_id: Optional[str] = None):
        """
        Initialize Image Agent.

        Args:
            user: User who initiated the agent
            project_id: Optional project ID to associate results with
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = 'ImageAgent'

        # Initialize image generation service
        self.stability = ImageGenerationService()

        # Session 203: Initialize preference manager for memory
        self._preference_manager = None

        logger.info(f"🎨 ImageAgent initialized for user: {user.username if user else 'system'}")

    @property
    def preference_manager(self):
        """Lazy load preference manager."""
        if self._preference_manager is None and self.user:
            from agents.preference_manager import AgentPreferenceManager
            self._preference_manager = AgentPreferenceManager(self.user, self.project_id)
        return self._preference_manager

    def get_user_preferences(self) -> Dict[str, Any]:
        """
        Get user's learned image preferences.

        Returns:
            Dict with preferred style, model, aspect_ratio, etc.
        """
        if self.preference_manager:
            return self.preference_manager.get_image_preferences()
        return {}

    def _apply_preferences(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply user preferences to parameters (fill in missing values).
        User-specified values always take precedence.
        """
        if self.preference_manager:
            return self.preference_manager.apply_preferences('image', params)
        return params

    def _record_success(self, params: Dict[str, Any], user_rating: Optional[int] = None):
        """Record a successful generation for preference learning."""
        if self.preference_manager:
            self.preference_manager.record_successful_generation('image', params, user_rating)

    # ===== GENERATION METHODS =====

    def generate(
        self,
        prompt: str,
        style: Optional[str] = None,
        model: str = 'sd3-large-turbo',
        size: str = '1024x1024',
        negative_prompt: Optional[str] = None,
        count: int = 1,
        session=None,
        project=None,
        apply_preferences: bool = True,
        learn: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Text description of the image
            style: Style preset (pixar, cyberpunk, watercolor, etc.) - uses 80+ built-in styles
            model: Model to use (sd3-large-turbo, core, ultra, etc.)
            size: Image dimensions (1024x1024, 1280x720, etc.)
            negative_prompt: What to avoid in the image
            count: Number of images to generate
            session: Optional AI session to link to
            project: Optional project to associate with
            apply_preferences: Whether to apply user's learned preferences (default True)
            learn: Whether to learn from this generation for future preferences (default True)

        Returns:
            Dict with success status, image_url, image_id
        """
        logger.info(f"🎨 ImageAgent generating image")
        logger.info(f"   Prompt: {prompt[:60]}...")
        logger.info(f"   Style: {style or 'none'}")
        logger.info(f"   Model: {model}")

        # Session 255: Time Travel Debugging - wrap in session
        with self.time_travel_session(
            task_type="image_generation",
            task_description=f"Generate: {prompt[:50]}...",
            input_data={'prompt': prompt, 'style': style, 'model': model, 'size': size}
        ):
            try:
                # Use the centralized image generation that has the 80+ style library
                from core.views_image import _execute_generate_image

                # Session 255: Record prompt analysis decision
                self.record_decision(
                    decision_type="analysis",
                    action=f"Analyzing prompt: {prompt[:50]}...",
                    reasoning="Parsing user intent and requirements",
                    context={'prompt_length': len(prompt), 'has_style': bool(style)},
                    confidence=0.9,
                    thoughts=[
                        f"User wants to generate: {prompt[:30]}...",
                        f"Style specified: {style or 'none (will use default or learned)'}",
                        f"Model selected: {model}"
                    ]
                )

                parameters = {
                    'prompt': prompt,
                    'model': model,
                    'size': size,
                    'count': count,
                }

                if style:
                    parameters['style'] = style
                if negative_prompt:
                    parameters['negative_prompt'] = negative_prompt

                # Session 203: Apply user preferences for missing values
                if apply_preferences:
                    original_style = parameters.get('style')
                    parameters = self._apply_preferences(parameters)
                    if parameters.get('style') and not style:
                        logger.info(f"   Applied learned style: {parameters.get('style')}")
                        # Session 255: Record preference application decision
                        self.record_decision(
                            decision_type="preference_application",
                            action=f"Applied learned style: {parameters.get('style')}",
                            reasoning="User has established style preferences from past generations",
                            alternatives=["Use default style", "Ask user for style"],
                            context={'learned_style': parameters.get('style')},
                            confidence=0.85
                        )

                # Session 255: Record model selection decision
                self.record_decision(
                    decision_type="model_selection",
                    action=f"Using model: {parameters.get('model')}",
                    reasoning=f"Model {parameters.get('model')} selected for {size} generation",
                    alternatives=["sd3", "sd3-large-turbo", "core", "ultra"],
                    context={'model': parameters.get('model'), 'size': size},
                    confidence=0.9
                )

                result = _execute_generate_image(self.user, parameters, session=session)

                if result.get('success'):
                    logger.info(f"✅ Image generated successfully")
                    logger.info(f"   Image ID: {result.get('image_id')}")

                    # Session 255: Record success
                    self.record_decision(
                        decision_type="generation_complete",
                        action=f"Successfully generated image: {result.get('image_id')}",
                        reasoning="Image generation completed without errors",
                        context={'image_id': result.get('image_id')},
                        confidence=1.0
                    )
                    self.mark_decision_outcome(True, f"Image {result.get('image_id')} created")

                    # Session 203: Record success for preference learning
                    if learn:
                        self._record_success(parameters)
                else:
                    # Session 255: Record failure
                    self.record_decision(
                        decision_type="generation_failed",
                        action=f"Generation failed: {result.get('error', 'Unknown error')}",
                        reasoning="API returned error or unexpected response",
                        context={'error': result.get('error')},
                        confidence=0.5
                    )
                    self.mark_decision_outcome(False, result.get('error', 'Unknown error'))
                    self.flag_decision("Generation failed - needs review")

                return result

            except Exception as e:
                logger.error(f"❌ ImageAgent.generate failed: {str(e)}", exc_info=True)
                # Session 255: Record exception
                self.record_decision(
                    decision_type="exception",
                    action=f"Exception occurred: {str(e)[:100]}",
                    reasoning="Unexpected error during generation",
                    context={'exception': str(e)},
                    confidence=0.0
                )
                self.flag_decision(f"Exception: {str(e)[:50]}")
                return {
                    'success': False,
                    'error': str(e)
                }

    def generate_logo(
        self,
        brand_name: str,
        industry: str,
        style: Optional[str] = None,
        color_scheme: Optional[str] = None,
        include_text: bool = True,
        count: int = 3,
        model: str = 'sd3-large-turbo',
        session=None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate professional logo options with brand expertise.
        Session 202: Consolidated from LogoAgent.

        Args:
            brand_name: Name of the brand/company
            industry: Industry/sector (technology, food, fashion, etc.)
            style: Visual style (minimalist, modern, vintage, etc.)
            color_scheme: Preferred colors
            include_text: Whether to include brand name in logo
            count: Number of logo options to generate
            model: Model to use
            session: Optional AI session

        Returns:
            Dict with success status and generated logos
        """
        logger.info(f"🎨 ImageAgent generating logo for '{brand_name}'")
        logger.info(f"   Industry: {industry}")
        logger.info(f"   Style: {style or 'professional'}")

        try:
            # Build expert logo prompt with brand expertise
            prompt_parts = [
                f"Professional logo design for '{brand_name}'",
                f"a {industry} company",
            ]

            if style:
                prompt_parts.append(f"{style} style")
            else:
                prompt_parts.append("clean professional style")

            if color_scheme:
                prompt_parts.append(f"using {color_scheme} colors")

            if include_text:
                prompt_parts.append(f"incorporating the text '{brand_name}'")
            else:
                prompt_parts.append("symbol/icon only, no text")

            # Add logo expertise enhancements
            prompt_parts.extend([
                "vector-style clean lines",
                "scalable design suitable for various sizes",
                "professional brand identity",
                "centered composition on clean background",
                "high contrast for visibility"
            ])

            prompt = ", ".join(prompt_parts)

            # Generate logos
            # Session 238: Use SD3 for better text avoidance + strong negative prompt
            results = []
            logo_negative_prompt = (
                "text, text, text, words, words, letters, letters, typography, font, writing, "
                "alphabet, numbers, watermark, signature, label, caption, title, slogan, "
                "brand name, company name, initials, monogram, readable text, any text, "
                "blurry, low quality, pixelated, distorted, cluttered, busy background"
            )
            for i in range(count):
                result = self.generate(
                    prompt=prompt,
                    style=style,
                    model='sd3',  # Session 238: SD3 follows text-avoidance instructions better
                    size='1024x1024',
                    session=session,
                    negative_prompt=logo_negative_prompt
                )
                if result.get('success'):
                    results.append({
                        'image_id': result.get('image_id'),
                        'image_url': result.get('image_url'),
                        'variant': i + 1
                    })

            if results:
                return {
                    'success': True,
                    'logos': results,
                    'count': len(results),
                    'brand_name': brand_name,
                    'message': f"✅ Generated {len(results)} logo options for {brand_name}"
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to generate any logos'
                }

        except Exception as e:
            logger.error(f"❌ ImageAgent.generate_logo failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def generate_social(
        self,
        prompt: str,
        platform: str,
        style: Optional[str] = None,
        include_cta: bool = False,
        cta_text: Optional[str] = None,
        model: str = 'sd3-large-turbo',
        session=None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate platform-optimized social media content.
        Session 202: Consolidated from SocialMediaAgent.

        Args:
            prompt: Content description
            platform: Target platform (instagram_square, facebook_post, twitter_post, etc.)
            style: Visual style
            include_cta: Whether to include call-to-action
            cta_text: CTA text if included
            model: Model to use
            session: Optional AI session

        Returns:
            Dict with success status and generated image
        """
        logger.info(f"🎨 ImageAgent generating social media content")
        logger.info(f"   Platform: {platform}")
        logger.info(f"   Prompt: {prompt[:60]}...")

        try:
            # Get platform-specific size
            size = self.PLATFORM_SIZES.get(platform, '1080x1080')
            logger.info(f"   Size: {size}")

            # Enhance prompt with social media expertise
            prompt_parts = [prompt]

            # Platform-specific enhancements
            if 'instagram' in platform:
                prompt_parts.append("eye-catching, vibrant, instagram-worthy")
            elif 'linkedin' in platform:
                prompt_parts.append("professional, corporate, business-appropriate")
            elif 'twitter' in platform:
                prompt_parts.append("bold, attention-grabbing, shareable")
            elif 'facebook' in platform:
                prompt_parts.append("engaging, social media optimized")

            if include_cta and cta_text:
                prompt_parts.append(f"with clear call-to-action: '{cta_text}'")

            prompt_parts.append("high quality social media content")

            enhanced_prompt = ", ".join(prompt_parts)

            result = self.generate(
                prompt=enhanced_prompt,
                style=style,
                model=model,
                size=size,
                session=session,
                negative_prompt="blurry, low quality, unprofessional"
            )

            if result.get('success'):
                result['platform'] = platform
                result['platform_size'] = size
                result['message'] = f"✅ Generated {platform} content ({size})"

            return result

        except Exception as e:
            logger.error(f"❌ ImageAgent.generate_social failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    # ===== EDITING METHODS (from ImageEditingAgent) =====

    def edit(
        self,
        image_id: str,
        operation: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an image editing operation.
        Session 202: Consolidated from ImageEditingAgent.

        Args:
            image_id: UUID or sequential number of the image to edit
            operation: Type of operation ('upscale', 'remove_background', 'variations',
                      'recolor', 'search_and_replace', 'creative_upscale')
            **kwargs: Operation-specific parameters

        Returns:
            Dict with success status and operation results
        """
        logger.info(f"🎨 ImageAgent editing image {image_id}: {operation}")

        try:
            # Validate and resolve image ID
            image = self._resolve_image_id(image_id)
            if not image:
                return {
                    'success': False,
                    'error': f'Image {image_id} not found for user {self.user.username if self.user else "unknown"}'
                }

            # Route to appropriate operation
            operation_map = {
                'upscale': self._upscale,
                'remove_background': self._remove_background,
                'remove_bg': self._remove_background,
                'variations': self._create_variations,
                'recolor': self._recolor,
                'search_and_replace': self._search_and_replace,
                'erase': self._search_and_replace,  # Erase uses search_and_replace with empty replace
                'creative_upscale': self._creative_upscale,
                'inpaint': self._inpaint,
                'outpaint': self._outpaint,
            }

            if operation not in operation_map:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}. Supported: {list(operation_map.keys())}'
                }

            result = operation_map[operation](str(image.id), **kwargs)
            return result

        except Exception as e:
            logger.error(f"❌ ImageAgent.edit failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _upscale(self, image_id: str, **kwargs) -> Dict[str, Any]:
        """Upscale image to 4x resolution."""
        try:
            from core.views_image import upscale_image_view

            factory = RequestFactory()
            request_data = {'image_id': image_id}
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/upscale/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = upscale_image_view(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                return {
                    'success': True,
                    'message': "✨ Successfully upscaling image to 4x resolution.",
                    'image_id': result.get('image_id')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Upscale operation failed')
                }

        except Exception as e:
            logger.error(f"❌ Upscale operation error: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _remove_background(self, image_id: str, **kwargs) -> Dict[str, Any]:
        """Remove background from image."""
        try:
            from core.views_image import remove_background_view

            factory = RequestFactory()
            request_data = {'image_id': image_id}
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/remove-background/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = remove_background_view(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                return {
                    'success': True,
                    'message': "✨ Background removed successfully!",
                    'image_id': result.get('image_id'),
                    'image_url': result.get('image_url')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Background removal failed')
                }

        except Exception as e:
            logger.error(f"❌ Remove background error: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _create_variations(self, image_id: str, count: int = 3, **kwargs) -> Dict[str, Any]:
        """Create variations of an image."""
        try:
            from core.views_image import create_variations_view

            factory = RequestFactory()
            request_data = {
                'image_id': image_id,
                'count': count
            }
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/variations/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = create_variations_view(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'message': f"✨ Created {count} variations!",
                    'variations': result.get('variations', [])
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Variations creation failed')
                }

        except Exception as e:
            logger.error(f"❌ Create variations error: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _recolor(self, image_id: str, select_prompt: str, new_color: str, **kwargs) -> Dict[str, Any]:
        """Recolor objects in an image."""
        try:
            from core.views_image import recolor_image_view

            factory = RequestFactory()
            request_data = {
                'image_id': image_id,
                'select_prompt': select_prompt,
                'new_color': new_color
            }
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/recolor/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = recolor_image_view(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                return {
                    'success': True,
                    'message': f"✨ Recolored '{select_prompt}' to {new_color}!",
                    'image_id': result.get('image_id'),
                    'image_url': result.get('image_url')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Recolor operation failed')
                }

        except Exception as e:
            logger.error(f"❌ Recolor error: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _search_and_replace(self, image_id: str, search_prompt: str, replace_prompt: str = '', **kwargs) -> Dict[str, Any]:
        """Search and replace objects in an image (or erase if replace_prompt is empty)."""
        try:
            from core.views_image import search_and_replace_view

            factory = RequestFactory()
            request_data = {
                'image_id': image_id,
                'search_prompt': search_prompt,
                'replace_prompt': replace_prompt
            }
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/search-and-replace/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = search_and_replace_view(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                action = 'Replaced' if replace_prompt else 'Erased'
                return {
                    'success': True,
                    'message': f"✨ {action} '{search_prompt}'" + (f" with '{replace_prompt}'" if replace_prompt else ""),
                    'image_id': result.get('image_id'),
                    'image_url': result.get('image_url')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Search and replace operation failed')
                }

        except Exception as e:
            logger.error(f"❌ Search and replace error: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _creative_upscale(self, image_id: str, creativity: float = 0.3, **kwargs) -> Dict[str, Any]:
        """Creative upscale with AI enhancement."""
        try:
            from core.views_image import creative_upscale_view

            factory = RequestFactory()
            request_data = {
                'image_id': image_id,
                'creativity': creativity
            }
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/creative-upscale/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = creative_upscale_view(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                return {
                    'success': True,
                    'message': f"✨ Creative upscale complete (creativity: {creativity})!",
                    'image_id': result.get('image_id'),
                    'image_url': result.get('image_url')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Creative upscale failed')
                }

        except Exception as e:
            logger.error(f"❌ Creative upscale error: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _inpaint(self, image_id: str, mask_prompt: str, fill_prompt: str, **kwargs) -> Dict[str, Any]:
        """Inpaint (fill) areas of an image."""
        try:
            from core.views_image import _execute_inpaint

            parameters = {
                'image_id': image_id,
                'mask_prompt': mask_prompt,
                'fill_prompt': fill_prompt
            }

            result = _execute_inpaint(self.user, parameters)
            return result

        except Exception as e:
            logger.error(f"❌ Inpaint error: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _outpaint(self, image_id: str, direction: str = 'all', **kwargs) -> Dict[str, Any]:
        """Outpaint (extend) an image."""
        try:
            from core.views_image import outpaint_view

            factory = RequestFactory()
            request_data = {
                'image_id': image_id,
                'direction': direction
            }

            request = factory.post('/api/stability/outpaint/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = outpaint_view(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                return {
                    'success': True,
                    'message': f"✨ Outpainted image ({direction})!",
                    'image_id': result.get('image_id'),
                    'image_url': result.get('image_url')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Outpaint failed')
                }

        except Exception as e:
            logger.error(f"❌ Outpaint error: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}

    # ===== HELPER METHODS =====

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


# ===== CONVENIENCE FUNCTIONS =====

def get_image_agent(user: Optional[User] = None, project_id: Optional[str] = None) -> ImageAgent:
    """
    Get ImageAgent instance.
    Convenience function for other modules.

    Args:
        user: User who initiated the agent
        project_id: Optional project ID

    Returns:
        ImageAgent instance
    """
    return ImageAgent(user=user, project_id=project_id)


__all__ = [
    'ImageAgent',
    'get_image_agent'
]
