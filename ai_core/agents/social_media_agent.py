"""
SocialMediaAgent - Platform-Optimized Social Content Specialist

Philosophy: Platform expertise + Style flexibility → Engagement-optimized content

This agent specializes in social media content generation with:
- Platform-specific size optimization (Instagram, Facebook, Twitter, LinkedIn)
- Engagement psychology and attention-grabbing techniques
- Trending visual patterns and social media best practices
- Call-to-action integration
- Accepts ANY style parameter (modern, professional, bold, minimalist, etc.)

Session 121 - Domain Specialist Agents (Logo + Social)
"""

import uuid
import base64
import re
from typing import Dict, List, Optional
from datetime import datetime

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from content.models import ImageHistory, CreativeProject
from content.image_generation import ImageGenerationService
from ai_core.agents.agent_memory_interface import AgentMemoryInterface


class SocialMediaAgent:
    """
    Domain specialist for platform-optimized social media content.

    Use cases:
    - "Create Instagram post about my new product" (any style)
    - "Generate LinkedIn announcement graphic" (professional style)
    - "Design Twitter header for tech brand" (bold, futuristic style)
    - "Make Facebook ad for coffee shop" (warm, vintage style)

    This agent adds SOCIAL MEDIA EXPERTISE to any style:
    - Platform-specific size optimization
    - Engagement psychology (attention, emotion, action)
    - Trending visual patterns
    - Social media design best practices

    Platform sizes:
    - Instagram: 1080x1080 (square post), 1080x1350 (portrait)
    - Facebook: 1200x630 (link preview), 1200x1200 (post)
    - Twitter: 1200x675 (post), 1500x500 (header)
    - LinkedIn: 1200x627 (post), 1584x396 (banner)

    The user specifies the PLATFORM and STYLE, we provide the EXPERTISE!
    """

    # Platform size presets
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
    }

    def __init__(self, user: User, session_id: Optional[str] = None, project: Optional[CreativeProject] = None):
        """
        Initialize SocialMediaAgent.

        Args:
            user: Django user object
            session_id: Optional session identifier
            project: Optional project for auto-linking generated content
        """
        self.user = user
        self.session_id = session_id or f"social_media_agent_{user.id}_{uuid.uuid4().hex[:8]}"
        self.project = project

        # Initialize agent memory interface
        self.memory = AgentMemoryInterface(
            agent_name="SocialMediaAgent",
            user_id=user.id,
            agent_id=self.session_id,
            redis_db=3
        )

        # Initialize image generation service
        self.stability = ImageGenerationService()

        # Log initialization
        self.memory.log_agent_action(
            action="agent_initialized",
            details={
                "user_id": user.id,
                "session_id": self.session_id,
                "project_id": project.id if project else None
            }
        )

    def generate_social_content(
        self,
        message: str,
        platform: str = 'instagram_square',
        style: Optional[str] = None,
        count: int = 3,
        include_text: bool = True,
        cta: Optional[str] = None,
        model: str = "sd3-large-turbo",
        **kwargs
    ) -> Dict:
        """
        Generate platform-optimized social media content.

        This method adds social media expertise to the generation:
        - Platform-specific size optimization
        - Engagement psychology (grab attention, evoke emotion)
        - Trending visual patterns
        - Social media design best practices

        Args:
            message: Core message/topic of the post
            platform: Platform preset (instagram_square, facebook_post, etc.)
            style: Style aesthetic (modern, professional, bold, minimalist, etc.)
            count: Number of options to generate (default: 3)
            include_text: Include text overlay? (default: True)
            cta: Optional call-to-action (e.g., "Shop Now", "Learn More")
            model: Stability AI model (default: sd3-large-turbo)
            **kwargs: Additional generation parameters

        Returns:
            Dict with:
                - success: Boolean
                - posts: List of generated social media content
                - batch_id: UUID linking all options
                - message: User-friendly message
        """
        try:
            # Get platform size
            size = self.PLATFORM_SIZES.get(platform, '1080x1080')

            # Build professional social media prompt with domain expertise
            base_prompt = self._build_social_prompt(
                message=message,
                platform=platform,
                style=style,
                include_text=include_text,
                cta=cta
            )

            batch_id = uuid.uuid4()

            self.memory.log_agent_action(
                action="generate_social_content_requested",
                details={
                    "message": message,
                    "platform": platform,
                    "style": style,
                    "count": count,
                    "batch_id": str(batch_id)
                }
            )

            posts = []
            errors = []

            # Parse size
            width, height = self._parse_size(size)

            for i in range(count):
                try:
                    # Add variation to each option while maintaining engagement
                    variation_prompt = self._add_prompt_variation(base_prompt, i, count)

                    # Generate with Stability AI
                    result = self.stability.generate_image(
                        prompt=variation_prompt,
                        provider='stability',
                        model=model,
                        style=style if style else 'digital-art',
                        size=size,
                        **kwargs
                    )

                    if not result.success or not result.images:
                        raise Exception(result.error_message or "No images generated")

                    # Save to storage (handle data URI)
                    image_url = result.images[0]
                    filename = f"social_media/{self.user.id}/{platform}_{i+1}_{batch_id}.png"

                    if image_url.startswith('data:image'):
                        base64_match = re.search(r'base64,(.+)', image_url)
                        if base64_match:
                            image_data = base64.b64decode(base64_match.group(1))
                            file_path = default_storage.save(filename, ContentFile(image_data))
                            stored_url = default_storage.url(file_path)
                        else:
                            raise Exception("Invalid data URI format")
                    else:
                        file_path = image_url
                        stored_url = image_url

                    # Create ImageHistory record
                    # Session 120: agent field will trigger auto-contribution tracking via signals!
                    from agents.models import UnifiedAgentTemplate

                    try:
                        social_agent_template = UnifiedAgentTemplate.objects.get(name="SocialMediaAgent")
                    except UnifiedAgentTemplate.DoesNotExist:
                        social_agent_template = None  # Will create in registration phase

                    image_history = ImageHistory.objects.create(
                        user=self.user,
                        filename=filename,
                        file_path=file_path,
                        image_type='generated',
                        prompt=variation_prompt,
                        model_used=model,
                        style=style or 'digital-art',
                        image_width=width,
                        image_height=height,
                        generation_batch_id=batch_id,
                        option_number=i + 1,
                        project=self.project,
                        agent=social_agent_template  # Session 120: Auto-track contribution!
                    )

                    posts.append({
                        'id': image_history.id,
                        'image_url': image_url,
                        'option_number': i + 1,
                        'platform': platform,
                        'size': size,
                        'style': style or 'digital-art',
                        'prompt': variation_prompt
                    })

                    self.memory.log_agent_action(
                        action="social_content_generated",
                        details={
                            'option_number': i + 1,
                            'image_id': image_history.id,
                            'platform': platform
                        }
                    )

                except Exception as e:
                    error_msg = f"Option {i + 1}: {str(e)}"
                    errors.append(error_msg)
                    self.memory.log_agent_action(
                        action="generation_error",
                        details={'option_number': i + 1, 'error': str(e)}
                    )

            if not posts:
                return {
                    'success': False,
                    'error': f'Failed to generate any social media content. Errors: {"; ".join(errors)}'
                }

            success_message = f"✅ Generated {len(posts)} platform-optimized posts for {platform.replace('_', ' ').title()}!"
            if errors:
                success_message += f" ({len(errors)} failed)"

            return {
                'success': True,
                'posts': posts,
                'batch_id': str(batch_id),
                'platform': platform,
                'size': size,
                'count': len(posts),
                'message': success_message,
                'errors': errors if errors else None
            }

        except Exception as e:
            self.memory.log_agent_action(
                action="generate_social_content_error",
                details={'error': str(e)}
            )
            return {
                'success': False,
                'error': str(e)
            }

    def _build_social_prompt(
        self,
        message: str,
        platform: str,
        style: Optional[str],
        include_text: bool,
        cta: Optional[str]
    ) -> str:
        """
        Build platform-optimized social media prompt with domain expertise.

        This is where the SOCIAL MEDIA SPECIALIST knowledge lives!
        """
        # Start with core social media requirements
        prompt_parts = []

        # Platform context
        platform_name = platform.replace('_', ' ').title()
        prompt_parts.append(f"Engaging social media post for {platform_name}")

        # Core message
        prompt_parts.append(f"about: {message}")

        # Add social media design expertise
        social_expertise = [
            "eye-catching composition",
            "attention-grabbing visual hierarchy",
            "scroll-stopping design",
            "social media optimized",
            "high engagement potential"
        ]

        # Platform-specific expertise
        if 'instagram' in platform:
            social_expertise.append("Instagram-ready aesthetic")
            social_expertise.append("vibrant and appealing")
        elif 'linkedin' in platform:
            social_expertise.append("professional LinkedIn aesthetic")
            social_expertise.append("corporate-appropriate")
        elif 'twitter' in platform:
            social_expertise.append("Twitter-optimized impact")
            social_expertise.append("quick visual message")
        elif 'facebook' in platform:
            social_expertise.append("Facebook-friendly design")
            social_expertise.append("broad appeal")

        prompt_parts.append(", ".join(social_expertise))

        # Text overlay guidance
        if include_text:
            if cta:
                prompt_parts.append(f"bold text overlay with call-to-action: '{cta}'")
            else:
                prompt_parts.append("bold text overlay with clear message")

        # Add style aesthetic (user's choice!)
        if style:
            prompt_parts.append(f"style: {style}")

        # Professional quality indicators
        prompt_parts.append("high-quality social media graphic, professional design, engaging composition")

        return ", ".join(prompt_parts)

    def _add_prompt_variation(self, base_prompt: str, index: int, total: int) -> str:
        """Add subtle variation to each option while maintaining engagement."""
        variations = [
            "emphasis on bold typography",
            "emphasis on striking visuals",
            "balanced text and imagery"
        ]

        if index < len(variations):
            return f"{base_prompt}, {variations[index]}"
        return base_prompt

    def _parse_size(self, size: str) -> tuple:
        """Parse size string to (width, height) tuple."""
        if 'x' in size:
            parts = size.split('x')
            return int(parts[0]), int(parts[1])
        return 1080, 1080  # Default to Instagram square

    def list_platforms(self) -> List[Dict]:
        """
        List all available platform presets with sizes.

        Returns:
            List of platform dictionaries
        """
        platforms = []
        for key, size in self.PLATFORM_SIZES.items():
            platform_name = key.replace('_', ' ').title()
            platforms.append({
                'key': key,
                'name': platform_name,
                'size': size,
                'width': int(size.split('x')[0]),
                'height': int(size.split('x')[1])
            })
        return platforms

    def get_state_summary(self) -> Dict:
        """
        Get current state summary of the agent.

        Returns:
            Dict with agent state
        """
        # Count social media content generated by this agent
        social_count = ImageHistory.objects.filter(
            user=self.user,
            filename__startswith=f"social_media/{self.user.id}/"
        ).count()

        return {
            'agent_name': 'SocialMediaAgent',
            'session_id': self.session_id,
            'user_id': self.user.id,
            'project_id': self.project.id if self.project else None,
            'total_posts_generated': social_count,
            'available_platforms': len(self.PLATFORM_SIZES),
            'specialization': 'Platform-optimized social media content'
        }
