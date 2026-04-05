"""
TemplateManagerAgent - Reproducible Creative Results

Philosophy: Perfect once → Save forever → Use everywhere

This agent solves the consistency problem by saving approved creative results
as reusable templates with ALL parameters needed for exact reproduction.

Session 90 - The Perfect Workflow: Phase 3 "Lock It Down"
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone

from content.models import ImageHistory
from ai_core.agents.agent_memory_interface import AgentMemoryInterface
from content.image_generation import ImageGenerationService


class BrandTemplate:
    """
    In-memory representation of a saved brand template.

    This will eventually become a Django model, but for now we store
    templates in agent memory (Redis) for fast iteration.
    """

    def __init__(
        self,
        template_id: str,
        user_id: int,
        name: str,
        # Original generation
        seed: int,
        prompt: str,
        model: str,
        style: Optional[str],
        width: int,
        height: int,
        reference_image_url: str,
        # Metadata
        created_at: datetime,
        tags: List[str] = None,
        notes: str = ""
    ):
        self.template_id = template_id
        self.user_id = user_id
        self.name = name
        self.seed = seed
        self.prompt = prompt
        self.model = model
        self.style = style
        self.width = width
        self.height = height
        self.reference_image_url = reference_image_url
        self.created_at = created_at
        self.tags = tags or []
        self.notes = notes

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'template_id': self.template_id,
            'user_id': self.user_id,
            'name': self.name,
            'seed': self.seed,
            'prompt': self.prompt,
            'model': self.model,
            'style': self.style,
            'width': self.width,
            'height': self.height,
            'reference_image_url': self.reference_image_url,
            'created_at': self.created_at.isoformat(),
            'tags': self.tags,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'BrandTemplate':
        """Create from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class TemplateManagerAgent:
    """
    Manages creative templates for reproducible results.

    Workflow:
    1. User generates multiple options (CreativeDirectorAgent)
    2. User picks favorite
    3. TemplateManager saves it with ALL parameters
    4. Later: Generate new content using same template

    This is THE solution to the consistency problem!
    """

    def __init__(self, user: User, session_id: Optional[str] = None):
        """
        Initialize TemplateManagerAgent.

        Args:
            user: Django user object
            session_id: Optional session identifier
        """
        self.user = user
        self.session_id = session_id or f"template_manager_{user.id}_{uuid.uuid4().hex[:8]}"

        # Initialize agent memory interface
        self.memory = AgentMemoryInterface(
            agent_name="TemplateManagerAgent",
            user_id=user.id,
            agent_id=self.session_id,
            redis_db=3
        )

        # Initialize image generation provider
        self.stability = ImageGenerationService()

        # Log initialization
        self.memory.log_agent_action(
            action="agent_initialized",
            details={
                "user_id": user.id,
                "session_id": self.session_id
            }
        )

    def save_as_template(
        self,
        image_id: int,
        template_name: str,
        tags: List[str] = None,
        notes: str = ""
    ) -> Dict:
        """
        Save an approved image as a reusable template.

        This is the "Lock It Down" step from the Perfect Workflow!
        Saves EVERYTHING needed to reproduce this exact result.

        Args:
            image_id: ID of the ImageHistory record to save as template
            template_name: User-friendly name for this template
            tags: Optional tags for organization (e.g., ['logo', 'coffee', 'mountain'])
            notes: Optional notes about this template

        Returns:
            Dict with template info and success status
        """
        try:
            # Get the image
            image = ImageHistory.objects.get(id=image_id, user=self.user)

            # Verify it has seed (required for reproduction)
            if not image.seed:
                return {
                    'success': False,
                    'error': 'Image does not have seed - cannot create reproducible template'
                }

            # Create template ID
            template_id = f"template_{uuid.uuid4().hex[:12]}"

            # Create BrandTemplate
            template = BrandTemplate(
                template_id=template_id,
                user_id=self.user.id,
                name=template_name,
                seed=image.seed,
                prompt=image.prompt,
                model=image.model,
                style=image.style,
                width=image.width,
                height=image.height,
                reference_image_url=image.image_url,
                created_at=timezone.now(),
                tags=tags or [],
                notes=notes
            )

            # Store in Redis (agent memory)
            # Key format: template_manager:user_{user_id}:templates:{template_id}
            template_key = f"template_manager:user_{self.user.id}:templates:{template_id}"
            self.memory.redis.set(template_key, str(template.to_dict()))

            # Add to user's template list
            list_key = f"template_manager:user_{self.user.id}:template_list"
            self.memory.redis.sadd(list_key, template_id)

            # Log action
            self.memory.log_agent_action(
                action="template_saved",
                details={
                    'template_id': template_id,
                    'template_name': template_name,
                    'image_id': image_id,
                    'seed': image.seed,
                    'has_reference': bool(image.image_url)
                }
            )

            return {
                'success': True,
                'template_id': template_id,
                'template_name': template_name,
                'seed': image.seed,
                'message': f'✅ Template "{template_name}" saved! You can now reproduce this exact style anytime.',
                'reproduction_info': {
                    'seed': image.seed,
                    'prompt': image.prompt,
                    'model': image.model,
                    'style': image.style
                }
            }

        except ImageHistory.DoesNotExist:
            return {
                'success': False,
                'error': 'Image not found or does not belong to user'
            }
        except Exception as e:
            self.memory.log_agent_action(
                action="save_template_error",
                details={'error': str(e)}
            )
            return {
                'success': False,
                'error': str(e)
            }

    def get_template(self, template_id: str) -> Optional[BrandTemplate]:
        """
        Get a template by ID.

        Args:
            template_id: The template ID

        Returns:
            BrandTemplate object or None if not found
        """
        try:
            template_key = f"template_manager:user_{self.user.id}:templates:{template_id}"
            template_data = self.memory.redis.get(template_key)

            if template_data:
                # Redis returns bytes, need to parse
                import ast
                template_dict = ast.literal_eval(template_data.decode('utf-8'))
                return BrandTemplate.from_dict(template_dict)

            return None

        except Exception as e:
            self.memory.log_agent_action(
                action="get_template_error",
                details={'template_id': template_id, 'error': str(e)}
            )
            return None

    def list_templates(self, tags: List[str] = None) -> List[Dict]:
        """
        List all templates for this user.

        Args:
            tags: Optional tag filter

        Returns:
            List of template dictionaries
        """
        try:
            list_key = f"template_manager:user_{self.user.id}:template_list"
            template_ids = self.memory.redis.smembers(list_key)

            templates = []
            for template_id_bytes in template_ids:
                template_id = template_id_bytes.decode('utf-8')
                template = self.get_template(template_id)

                if template:
                    # Filter by tags if provided
                    if tags:
                        if any(tag in template.tags for tag in tags):
                            templates.append(template.to_dict())
                    else:
                        templates.append(template.to_dict())

            # Sort by created_at (newest first)
            templates.sort(key=lambda t: t['created_at'], reverse=True)

            self.memory.log_agent_action(
                action="list_templates",
                details={
                    'count': len(templates),
                    'tags_filter': tags
                }
            )

            return templates

        except Exception as e:
            self.memory.log_agent_action(
                action="list_templates_error",
                details={'error': str(e)}
            )
            return []

    def generate_from_template(
        self,
        template_id: str,
        prompt_override: Optional[str] = None,
        variation_seed_offset: int = 0
    ) -> Dict:
        """
        Generate new content using a saved template.

        This is THE key to reproducibility!
        Uses exact same parameters as the approved original.

        Args:
            template_id: The template to use
            prompt_override: Optional new prompt (uses template prompt if not provided)
            variation_seed_offset: Offset to add to seed for controlled variations
                                  0 = exact reproduction
                                  1-10 = slight variations

        Returns:
            Dict with generation result
        """
        try:
            # Get template
            template = self.get_template(template_id)

            if not template:
                return {
                    'success': False,
                    'error': f'Template {template_id} not found'
                }

            # Determine prompt
            prompt = prompt_override or template.prompt

            # Calculate seed for this generation
            generation_seed = template.seed + variation_seed_offset

            # Generate with exact template parameters
            result = self.stability.text_to_image(
                prompt=prompt,
                model=template.model,
                style_preset=template.style,
                width=template.width,
                height=template.height,
                seed=generation_seed,
                output_format='png'
            )

            # Create ImageHistory record
            from core.services.workspace_resolver import get_active_workspace
            image_history = ImageHistory.objects.create(
                user=self.user,
                prompt=prompt,
                image_url=result['image_url'],
                model=template.model,
                style=template.style,
                width=template.width,
                height=template.height,
                seed=generation_seed,
                workspace=get_active_workspace(self.user),
            )

            self.memory.log_agent_action(
                action="generated_from_template",
                details={
                    'template_id': template_id,
                    'template_name': template.name,
                    'seed_offset': variation_seed_offset,
                    'generation_seed': generation_seed,
                    'image_id': image_history.id
                }
            )

            return {
                'success': True,
                'image_id': image_history.id,
                'image_url': result['image_url'],
                'template_name': template.name,
                'seed_used': generation_seed,
                'message': f'✅ Generated using "{template.name}" template! {"Exact reproduction" if variation_seed_offset == 0 else f"Variation {variation_seed_offset}"}',
                'is_exact_reproduction': variation_seed_offset == 0
            }

        except Exception as e:
            self.memory.log_agent_action(
                action="generate_from_template_error",
                details={
                    'template_id': template_id,
                    'error': str(e)
                }
            )
            return {
                'success': False,
                'error': str(e)
            }

    def delete_template(self, template_id: str) -> Dict:
        """
        Delete a template.

        Args:
            template_id: The template to delete

        Returns:
            Dict with success status
        """
        try:
            # Remove from Redis
            template_key = f"template_manager:user_{self.user.id}:templates:{template_id}"
            self.memory.redis.delete(template_key)

            # Remove from list
            list_key = f"template_manager:user_{self.user.id}:template_list"
            self.memory.redis.srem(list_key, template_id)

            self.memory.log_agent_action(
                action="template_deleted",
                details={'template_id': template_id}
            )

            return {
                'success': True,
                'message': f'Template {template_id} deleted'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_state_summary(self) -> Dict:
        """
        Get current state summary of the agent.

        Returns:
            Dict with agent state
        """
        templates = self.list_templates()

        return {
            'agent_name': 'TemplateManagerAgent',
            'session_id': self.session_id,
            'user_id': self.user.id,
            'total_templates': len(templates),
            'templates': templates
        }
