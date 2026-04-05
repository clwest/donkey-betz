"""
CreativeDirectorAgent - AI Partnership Model for Image Generation

Philosophy: AI suggests → Human chooses → Agent learns → Gets better!

This agent generates MULTIPLE creative options, lets humans pick their favorite,
and learns their taste over time. It's about PARTNERSHIP, not automation.

Session 90 - The Perfect Workflow Implementation
"""

import random
import uuid
import base64
import re
from typing import Dict, List, Optional

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from content.models import ImageHistory, UserCreativePreference
from content.image_generation import ImageGenerationService
from ai_core.agents.agent_memory_interface import AgentMemoryInterface


class CreativeDirectorAgent:
    """
    Partnership model for creative generation:
    - AI generates 3-5 options (creative diversity)
    - Human picks favorite (taste + judgment)
    - System learns patterns (personalization)
    - Agent gets SMARTER every time!

    Learning stages:
    - 0 choices: Generate random options
    - 1-4 choices: Start learning preferences
    - 5-9 choices: Show pattern recognition
    - 10+ choices: Strong personalization
    """

    def __init__(self, user: User, session_id: Optional[str] = None):
        """
        Initialize CreativeDirectorAgent.

        Args:
            user: Django user object
            session_id: Optional session identifier for agent memory
        """
        self.user = user
        self.session_id = session_id or f"creative_director_{user.id}_{uuid.uuid4().hex[:8]}"

        # Initialize agent memory interface
        self.memory = AgentMemoryInterface(
            agent_name="CreativeDirectorAgent",
            user_id=user.id,
            agent_id=self.session_id,
            redis_db=3
        )

        # Initialize image generation service
        self.stability = ImageGenerationService()

        # Get or create user preferences
        self.preferences, created = UserCreativePreference.objects.get_or_create(
            user=user
        )

        # Log initialization
        self.memory.log_agent_action(
            action="agent_initialized",
            details={
                "user_id": user.id,
                "total_choices": self.preferences.total_choices,
                "learning_stage": self.preferences.get_learning_stage()
            }
        )

    def generate_options(
        self,
        prompt: str,
        count: int = 3,
        style: Optional[str] = None,
        model: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        **kwargs
    ) -> Dict:
        """
        Generate multiple creative options for user choice.

        This is where the magic happens:
        1. Uses learned preferences for SMART generation (70%)
        2. Explores new possibilities (30%)
        3. Returns batch with seeds for exact reproduction
        4. User picks favorite → Agent learns!

        Args:
            prompt: User's creative prompt
            count: Number of options to generate (default: 3)
            style: Optional style preset
            model: Optional model selection
            width: Image width
            height: Image height
            **kwargs: Additional generation parameters

        Returns:
            Dict with:
                - batch_id: UUID linking all options
                - options: List of generated images with metadata
                - learning_message: What agent learned/will learn
        """
        batch_id = uuid.uuid4()

        # Session 92: Pre-select DIVERSE styles for maximum variety (if no style specified)
        # Session 92.1: Ignore "vector" style (GPT-5 often defaults to this for logos) - force diversity!
        if style == "vector" or style == "digital-art":
            style = None  # Treat common defaults as no style preference

        diverse_styles = None
        if style is None:
            # Pick COUNT different styles randomly
            all_styles = self._get_all_styles()
            diverse_styles = random.sample(all_styles, min(count, len(all_styles)))

        # Log generation request
        self.memory.log_agent_action(
            action="generate_options_requested",
            details={
                "prompt": prompt,
                "count": count,
                "style": style,
                "diverse_styles": diverse_styles,
                "model": model,
                "total_choices": self.preferences.total_choices
            }
        )

        options = []
        errors = []  # Track errors for debugging
        project_info = None  # Session 96: Track if project was auto-created

        for i in range(count):
            # Session 92: Use pre-selected diverse style for this option
            option_style = diverse_styles[i] if diverse_styles else style

            # Prepare smart generation parameters based on learned preferences
            gen_params = self._prepare_generation_params(
                prompt=prompt,
                style=option_style,
                model=model,
                option_number=i,
                exploration_rate=0.3  # 30% exploration, 70% exploitation
            )

            # Generate with specific seed for reproducibility
            seed = gen_params['seed']

            try:
                # Call Stability AI with prepared parameters
                result = self.stability.generate_image(
                    prompt=gen_params['prompt'],
                    provider='stability',
                    model=gen_params['model'],
                    style=gen_params['style'],
                    size=f"{width}x{height}",
                    seed=seed,
                    **kwargs
                )

                # Check if generation was successful
                if not result.success or not result.images:
                    raise Exception(result.error_message or "No images generated")

                # Session 95: Download and save data URI to actual file storage
                image_url = result.images[0]
                filename = f"generated_images/{self.user.id}/option_{i+1}_{batch_id}.png"

                # Extract base64 data from data URI and save to storage
                if image_url.startswith('data:image'):
                    base64_match = re.search(r'base64,(.+)', image_url)
                    if base64_match:
                        image_data = base64.b64decode(base64_match.group(1))
                        file_path = default_storage.save(filename, ContentFile(image_data))
                        stored_url = default_storage.url(file_path)
                    else:
                        raise Exception("Invalid data URI format")
                else:
                    # Regular URL - save directly
                    file_path = image_url
                    stored_url = image_url

                # Session 96: Extract session from kwargs if provided
                session = kwargs.get('session')

                from core.services.workspace_resolver import get_active_workspace
                image_history = ImageHistory.objects.create(
                    user=self.user,
                    filename=filename,
                    file_path=file_path,  # Session 95: Now uses actual file path, not data URI
                    image_type='generated',
                    prompt=gen_params['prompt'],
                    model_used=gen_params['model'],
                    style=gen_params['style'],
                    image_width=width,
                    image_height=height,
                    seed=seed,
                    generation_batch_id=batch_id,
                    option_number=i + 1,
                    was_selected=False,
                    session=session,  # Session 96: Link to AI session for tracking
                    workspace=get_active_workspace(self.user),
                )

                # Session 96: Update session counter for auto-project creation
                if session:
                    from core.views_image import increment_session_counter
                    result_info = increment_session_counter(session, 'image')
                    # Capture project creation info (only returned when threshold hit)
                    if result_info and not project_info:
                        project_info = result_info

                options.append({
                    'id': image_history.id,
                    'image_url': image_url,
                    'seed': seed,
                    'option_number': i + 1,
                    'model': gen_params['model'],
                    'style': gen_params['style'],
                    'reasoning': gen_params['reasoning']
                })

                self.memory.log_agent_action(
                    action="option_generated",
                    details={
                        'option_number': i + 1,
                        'seed': seed,
                        'model': gen_params['model'],
                        'style': gen_params['style'],
                        'reasoning': gen_params['reasoning']
                    }
                )

            except Exception as e:
                error_msg = f"Option {i + 1}: {str(e)}"
                errors.append(error_msg)
                self.memory.log_agent_action(
                    action="generation_error",
                    details={
                        'option_number': i + 1,
                        'error': str(e)
                    }
                )
                # Continue with next option on error
                continue

        # Generate learning message based on user's progress
        learning_message = self._get_learning_message(len(options))

        result = {
            'batch_id': str(batch_id),
            'options': options,
            'learning_message': learning_message,
            'total_choices': self.preferences.total_choices,
            'learning_stage': self.preferences.get_learning_stage(),
            'errors': errors if errors else None  # Include errors for debugging
        }

        # Session 96: Include project creation info if project was auto-created
        if project_info:
            result.update(project_info)

        return result

    def record_choice(self, selected_image_id: int) -> Dict:
        """
        Record user's choice - THIS IS HOW THE AGENT LEARNS!

        Every choice teaches the agent:
        - Which styles the user prefers
        - Which models produce better results
        - Color palette preferences
        - Composition preferences

        After 5-10 choices, the agent KNOWS your taste!

        Args:
            selected_image_id: ID of the ImageHistory record user selected

        Returns:
            Dict with learning insights and updated preferences
        """
        try:
            # Get the selected image
            selected_image = ImageHistory.objects.get(
                id=selected_image_id,
                user=self.user
            )

            # Mark as selected
            with transaction.atomic():
                selected_image.was_selected = True
                selected_image.selection_timestamp = timezone.now()
                selected_image.save()

                # Mark other options in batch as not selected
                if selected_image.generation_batch_id:
                    ImageHistory.objects.filter(
                        generation_batch_id=selected_image.generation_batch_id,
                        user=self.user
                    ).exclude(
                        id=selected_image_id
                    ).update(was_selected=False)

            # Update user preferences based on choice
            insights = self._update_preferences(selected_image)

            # Increment total choices
            self.preferences.total_choices += 1
            self.preferences.save()

            self.memory.log_agent_action(
                action="choice_recorded",
                details={
                    'image_id': selected_image_id,
                    'seed': selected_image.seed,
                    'model': selected_image.model_used,
                    'style': selected_image.style,
                    'total_choices': self.preferences.total_choices,
                    'learning_stage': self.preferences.get_learning_stage(),
                    'insights': insights
                }
            )

            return {
                'success': True,
                'insights': insights,
                'total_choices': self.preferences.total_choices,
                'learning_stage': self.preferences.get_learning_stage(),
                'message': self._get_choice_feedback_message()
            }

        except ImageHistory.DoesNotExist:
            return {
                'success': False,
                'error': 'Image not found or does not belong to user'
            }
        except Exception as e:
            self.memory.log_agent_action(
                action="record_choice_error",
                details={'error': str(e)}
            )
            return {
                'success': False,
                'error': str(e)
            }

    def get_smart_recommendation(self, prompt: str) -> Optional[Dict]:
        """
        Get smart recommendations based on learned preferences.

        Available after 5+ choices when agent has learned enough.

        Args:
            prompt: User's creative prompt

        Returns:
            Dict with recommended style, model, and reasoning, or None if not enough data
        """
        if self.preferences.total_choices < 5:
            return None

        # Analyze user preferences
        preferred_styles = self.preferences.preferred_styles or []
        preferred_models = self.preferences.preferred_models or []

        recommendation = {
            'recommended_style': preferred_styles[0] if preferred_styles else None,
            'recommended_model': preferred_models[0] if preferred_models else None,
            'reasoning': self._generate_recommendation_reasoning(),
            'confidence': self._calculate_recommendation_confidence()
        }

        self.memory.log_agent_action(
            action="recommendation_generated",
            details=recommendation
        )

        return recommendation

    # Private helper methods

    def _prepare_generation_params(
        self,
        prompt: str,
        style: Optional[str],
        model: Optional[str],
        option_number: int,
        exploration_rate: float
    ) -> Dict:
        """
        Prepare smart generation parameters based on learned preferences.

        Balances exploitation (using learned preferences) with exploration (trying new things).
        """
        # Generate deterministic seed for this option
        base_seed = random.randint(100000, 999999)
        seed = base_seed + option_number

        # Decide whether to explore or exploit
        should_explore = random.random() < exploration_rate

        if should_explore or self.preferences.total_choices < 3:
            # Exploration mode: Try new styles/models
            reasoning = "Exploring new creative possibilities"

            # Use provided style/model or pick random
            final_style = style or self._get_random_style()
            final_model = model or self._get_random_model()

        else:
            # Exploitation mode: Use learned preferences
            reasoning = "Using your preferred style based on past choices"

            # Use learned preferences
            preferred_styles = self.preferences.preferred_styles or []
            preferred_models = self.preferences.preferred_models or []

            final_style = style or (preferred_styles[0] if preferred_styles else None)
            final_model = model or (preferred_models[0] if preferred_models else 'sdxl')

        return {
            'prompt': prompt,
            'seed': seed,
            'style': final_style,
            'model': final_model,
            'reasoning': reasoning
        }

    def _update_preferences(self, selected_image: ImageHistory) -> Dict:
        """
        Update user preferences based on selected image.

        Returns insights about what was learned.
        """
        insights = {}

        # Update style preferences
        if selected_image.style:
            styles = self.preferences.preferred_styles or []

            # Move selected style to front (most preferred)
            if selected_image.style in styles:
                styles.remove(selected_image.style)
            styles.insert(0, selected_image.style)

            # Keep only top 5 styles
            self.preferences.preferred_styles = styles[:5]
            insights['style'] = f"Learning you prefer '{selected_image.style}' style"

        # Update model preferences
        if selected_image.model_used:
            models = self.preferences.preferred_models or []

            if selected_image.model_used in models:
                models.remove(selected_image.model_used)
            models.insert(0, selected_image.model_used)

            self.preferences.preferred_models = models[:3]
            insights['model'] = f"Learning you prefer '{selected_image.model_used}' model"

        # Save updated preferences
        self.preferences.save()

        return insights

    def _get_learning_message(self, options_count: int) -> str:
        """Generate contextual learning message based on user's progress."""
        stage = self.preferences.get_learning_stage()

        if stage == "new":
            return f"🎨 Here are {options_count} creative options! Pick your favorite and I'll learn your taste."
        elif stage == "learning":
            return f"🎨 Generated {options_count} options! I'm starting to learn your style..."
        elif stage == "patterns":
            return f"🎨 Generated {options_count} options based on your preferences! Pick your favorite to refine my understanding."
        else:  # knows_taste
            return f"🎨 Generated {options_count} options tailored to YOUR taste! I'm getting good at this 😊"

    def _get_choice_feedback_message(self) -> str:
        """Generate feedback message after user makes a choice."""
        total = self.preferences.total_choices

        if total == 1:
            return "🎯 First choice recorded! I'm starting to learn your taste."
        elif total == 5:
            return "🎯 5 choices! I'm beginning to see patterns in what you like."
        elif total == 10:
            return "🎯 10 choices! I really understand your creative style now!"
        elif total % 10 == 0:
            return f"🎯 {total} choices! I know your taste better than ever!"
        else:
            return "🎯 Choice recorded! Getting smarter about your preferences."

    def _generate_recommendation_reasoning(self) -> str:
        """Generate reasoning for recommendations."""
        total = self.preferences.total_choices
        styles = self.preferences.preferred_styles or []

        if not styles:
            return "Based on your choices, I recommend trying different styles."

        top_style = styles[0]
        return f"Based on {total} choices, you consistently prefer '{top_style}' style."

    def _calculate_recommendation_confidence(self) -> float:
        """Calculate confidence in recommendations (0.0 to 1.0)."""
        total = self.preferences.total_choices

        if total < 5:
            return 0.0
        elif total < 10:
            return 0.5
        elif total < 20:
            return 0.7
        else:
            return 0.9

    def _get_all_styles(self) -> List[str]:
        """Get ALL 69 available styles for diversity!"""
        return [
            # Photography (10)
            'photorealistic', 'photographic', 'portrait', 'landscape', 'macro',
            'street', 'fashion', 'architectural', 'black_white', 'vintage',

            # Digital Art (8)
            'digital-art', 'concept_art', 'matte_painting', 'vector',
            'low_poly', 'voxel', 'isometric',

            # Traditional Art (8)
            'oil_painting', 'watercolor', 'acrylic', 'gouache', 'ink',
            'charcoal', 'pencil', 'pastel',

            # Animation & Comics (7)
            'anime', 'manga', 'pixar', 'disney', 'comic', 'cartoon', 'chibi',

            # Artistic Movements (11)
            'impressionist', 'expressionist', 'surreal', 'abstract', 'cubist',
            'art_nouveau', 'art_deco', 'pop_art', 'minimalist', 'baroque', 'renaissance',

            # Genre Styles (8)
            'fantasy', 'scifi', 'cyberpunk', 'steampunk', 'gothic', 'horror',
            'retro', 'vaporwave',

            # 3D & Rendering (3)
            '3d_render', 'clay_render', 'wireframe',

            # Special Effects (3)
            'neon', 'holographic', 'glitch',

            # Cultural (5)
            'japanese', 'chinese', 'indian', 'african', 'aztec',

            # Unique Styles (6)
            'pixel_art', 'graffiti', 'collage', 'mosaic', 'stained_glass',
            'origami', 'psychedelic'
        ]

    def _get_random_style(self) -> Optional[str]:
        """Get random style for exploration - ALL 69 STYLES!"""
        return random.choice(self._get_all_styles())

    def _get_random_model(self) -> str:
        """Get random model for exploration."""
        models = ['core', 'sdxl', 'sd3', 'ultra']
        return random.choice(models)

    def get_state_summary(self) -> Dict:
        """
        Get current state summary of the agent.

        Returns:
            Dict with agent state including preferences and learning progress
        """
        return {
            'agent_name': 'CreativeDirectorAgent',
            'session_id': self.session_id,
            'user_id': self.user.id,
            'total_choices': self.preferences.total_choices,
            'learning_stage': self.preferences.get_learning_stage(),
            'preferred_styles': self.preferences.preferred_styles,
            'preferred_models': self.preferences.preferred_models,
            'can_make_recommendations': self.preferences.total_choices >= 5
        }
