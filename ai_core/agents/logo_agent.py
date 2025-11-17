"""
LogoAgent - Professional Logo & Brand Identity Specialist

Philosophy: Purpose over style → Professional logos for any brand → Any aesthetic

This agent specializes in professional logo generation with:
- Typography and brand identity expertise
- Scalability awareness (SVG-ready designs)
- Negative space and composition mastery
- Color psychology for branding
- Accepts ANY style parameter (minimalist, modern, vintage, cyberpunk, etc.)

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


class LogoAgent:
    """
    Domain specialist for professional logo generation.

    Use cases:
    - "Create a logo for my tech startup" (any style: minimalist, futuristic, etc.)
    - "Generate a coffee shop logo" (any style: vintage, modern, rustic, etc.)
    - "Design a gaming company logo" (any style: cyberpunk, neon, grunge, etc.)

    This agent adds PROFESSIONAL LOGO EXPERTISE to any style:
    - Typography best practices
    - Brand identity principles
    - Scalability considerations
    - Negative space usage
    - Color psychology

    The user specifies the STYLE, we provide the EXPERTISE!
    """

    def __init__(self, user: User, session_id: Optional[str] = None, project: Optional[CreativeProject] = None):
        """
        Initialize LogoAgent.

        Args:
            user: Django user object
            session_id: Optional session identifier
            project: Optional project for auto-linking generated content
        """
        self.user = user
        self.session_id = session_id or f"logo_agent_{user.id}_{uuid.uuid4().hex[:8]}"
        self.project = project

        # Initialize agent memory interface
        self.memory = AgentMemoryInterface(
            agent_name="LogoAgent",
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

    def generate_logo(
        self,
        brand_name: str,
        industry: str,
        style: Optional[str] = None,
        count: int = 3,
        color_scheme: Optional[str] = None,
        include_text: bool = True,
        model: str = "sd3-large-turbo",
        size: str = "1024x1024",
        **kwargs
    ) -> Dict:
        """
        Generate professional logo options.

        This method adds logo-specific expertise to the generation:
        - Professional typography guidance
        - Brand identity principles
        - Scalability considerations
        - Negative space awareness

        Args:
            brand_name: Name of the brand/company
            industry: Industry/domain (tech, coffee, gaming, etc.)
            style: Style aesthetic (minimalist, vintage, modern, cyberpunk, etc.)
            count: Number of options to generate (default: 3)
            color_scheme: Color guidance (e.g., "blue and white", "warm earth tones")
            include_text: Include brand name in logo? (default: True)
            model: Stability AI model (default: sd3-large-turbo)
            size: Output size (default: 1024x1024)
            **kwargs: Additional generation parameters

        Returns:
            Dict with:
                - success: Boolean
                - logos: List of generated logo options
                - batch_id: UUID linking all options
                - message: User-friendly message
        """
        try:
            # Build professional logo prompt with domain expertise
            base_prompt = self._build_logo_prompt(
                brand_name=brand_name,
                industry=industry,
                style=style,
                color_scheme=color_scheme,
                include_text=include_text
            )

            batch_id = uuid.uuid4()

            self.memory.log_agent_action(
                action="generate_logo_requested",
                details={
                    "brand_name": brand_name,
                    "industry": industry,
                    "style": style,
                    "count": count,
                    "batch_id": str(batch_id)
                }
            )

            logos = []
            errors = []

            # Parse size
            width, height = self._parse_size(size)

            for i in range(count):
                try:
                    # Add variation to each option while maintaining quality
                    variation_prompt = self._add_prompt_variation(base_prompt, i, count)

                    # Generate with Stability AI
                    result = self.stability.generate_image(
                        prompt=variation_prompt,
                        provider='stability',
                        model=model,
                        style=style if style else 'digital-art',  # Default to digital-art if no style
                        size=size,
                        **kwargs
                    )

                    if not result.success or not result.images:
                        raise Exception(result.error_message or "No images generated")

                    # Save to storage (handle data URI)
                    image_url = result.images[0]
                    filename = f"logos/{self.user.id}/{brand_name.lower().replace(' ', '_')}_{i+1}_{batch_id}.png"

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
                        logo_agent_template = UnifiedAgentTemplate.objects.get(name="LogoAgent")
                    except UnifiedAgentTemplate.DoesNotExist:
                        logo_agent_template = None  # Will create in registration phase

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
                        agent=logo_agent_template  # Session 120: Auto-track contribution!
                    )

                    logos.append({
                        'id': image_history.id,
                        'image_url': image_url,
                        'option_number': i + 1,
                        'brand_name': brand_name,
                        'style': style or 'digital-art',
                        'prompt': variation_prompt
                    })

                    self.memory.log_agent_action(
                        action="logo_generated",
                        details={
                            'option_number': i + 1,
                            'image_id': image_history.id,
                            'brand_name': brand_name
                        }
                    )

                except Exception as e:
                    error_msg = f"Option {i + 1}: {str(e)}"
                    errors.append(error_msg)
                    self.memory.log_agent_action(
                        action="generation_error",
                        details={'option_number': i + 1, 'error': str(e)}
                    )

            if not logos:
                return {
                    'success': False,
                    'error': f'Failed to generate any logos. Errors: {"; ".join(errors)}'
                }

            success_message = f"✅ Generated {len(logos)} professional logo options for {brand_name}!"
            if errors:
                success_message += f" ({len(errors)} failed)"

            return {
                'success': True,
                'logos': logos,
                'batch_id': str(batch_id),
                'brand_name': brand_name,
                'count': len(logos),
                'message': success_message,
                'errors': errors if errors else None
            }

        except Exception as e:
            self.memory.log_agent_action(
                action="generate_logo_error",
                details={'error': str(e)}
            )
            return {
                'success': False,
                'error': str(e)
            }

    def _build_logo_prompt(
        self,
        brand_name: str,
        industry: str,
        style: Optional[str],
        color_scheme: Optional[str],
        include_text: bool
    ) -> str:
        """
        Build professional logo prompt with domain expertise.

        This is where the LOGO SPECIALIST knowledge lives!
        """
        # Start with core logo requirements
        prompt_parts = []

        if include_text:
            prompt_parts.append(f"Professional logo design for '{brand_name}'")
        else:
            prompt_parts.append(f"Professional logo mark/symbol for {industry} brand")

        # Add industry context
        prompt_parts.append(f"{industry} industry")

        # Add professional logo design principles
        logo_expertise = [
            "clean composition",
            "scalable vector-ready design",
            "professional typography" if include_text else "iconic symbol",
            "memorable brand identity",
            "balanced negative space",
            "works in monochrome"
        ]
        prompt_parts.append(", ".join(logo_expertise))

        # Add color guidance if provided
        if color_scheme:
            prompt_parts.append(f"color palette: {color_scheme}")
        else:
            prompt_parts.append("professional color palette")

        # Add style aesthetic (user's choice!)
        if style:
            prompt_parts.append(f"style: {style}")

        # Professional quality indicators
        prompt_parts.append("high-quality professional logo design, centered composition, white or transparent background")

        return ", ".join(prompt_parts)

    def _add_prompt_variation(self, base_prompt: str, index: int, total: int) -> str:
        """Add subtle variation to each option while maintaining quality."""
        variations = [
            "emphasis on typography",
            "emphasis on iconic symbol",
            "balanced text and symbol"
        ]

        if index < len(variations):
            return f"{base_prompt}, {variations[index]}"
        return base_prompt

    def _parse_size(self, size: str) -> tuple:
        """Parse size string to (width, height) tuple."""
        if 'x' in size:
            parts = size.split('x')
            return int(parts[0]), int(parts[1])
        return 1024, 1024  # Default

    def get_state_summary(self) -> Dict:
        """
        Get current state summary of the agent.

        Returns:
            Dict with agent state
        """
        # Count logos generated by this agent
        logo_count = ImageHistory.objects.filter(
            user=self.user,
            filename__startswith=f"logos/{self.user.id}/"
        ).count()

        return {
            'agent_name': 'LogoAgent',
            'session_id': self.session_id,
            'user_id': self.user.id,
            'project_id': self.project.id if self.project else None,
            'total_logos_generated': logo_count,
            'specialization': 'Professional logo and brand identity design'
        }
