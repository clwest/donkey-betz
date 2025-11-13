"""
BrandStyleAgent - Consistent Brand Aesthetic Training

Philosophy: Train once on brand aesthetic → Use trigger word forever → Perfect consistency

This agent extends character training to train on COMPLETE brand aesthetics:
- Logos, color palettes, compositions, lighting, style
- Not just characters, but entire visual identity
- One trigger word = consistent brand across all content

Session 90 - The Perfect Workflow: Brand Style Training
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from content.models import ImageHistory, CharacterModel, CharacterTrainingImage
from content.replicate_provider import ReplicateProvider
from ai_core.agents.agent_memory_interface import AgentMemoryInterface


class BrandStyleAgent:
    """
    Trains FLUX LoRA models on complete brand aesthetics.

    Differences from character training:
    - Character training: Train on ONE character from multiple angles
    - Brand training: Train on ENTIRE aesthetic (logo, style, colors, mood)

    Use cases:
    - "Train on my coffee shop brand" → "ALPINE_BRAND modern bakery logo" works!
    - "Train on these 7 images" → All future generations match aesthetic
    - "Save as brand style" → Trigger word for all future content

    This is THE solution for brand consistency!
    """

    def __init__(self, user: User, session_id: Optional[str] = None):
        """
        Initialize BrandStyleAgent.

        Args:
            user: Django user object
            session_id: Optional session identifier
        """
        self.user = user
        self.session_id = session_id or f"brand_style_{user.id}_{uuid.uuid4().hex[:8]}"

        # Initialize agent memory interface
        self.memory = AgentMemoryInterface(
            agent_name="BrandStyleAgent",
            user_id=user.id,
            agent_id=self.session_id,
            redis_db=3
        )

        # Initialize Replicate provider (FLUX training)
        self.replicate = ReplicateProvider()

        # Log initialization
        self.memory.log_agent_action(
            action="agent_initialized",
            details={
                "user_id": user.id,
                "session_id": self.session_id
            }
        )

    def create_brand_style(
        self,
        brand_name: str,
        image_ids: List[int],
        trigger_word: Optional[str] = None,
        description: str = ""
    ) -> Dict:
        """
        Create a brand style from multiple images.

        This uses the existing character training system but with brand focus.

        Args:
            brand_name: Name of the brand (e.g., "Alpine Coffee Co.")
            image_ids: List of ImageHistory IDs representing the brand aesthetic
            trigger_word: Optional custom trigger word (auto-generated if not provided)
            description: Description of the brand style

        Returns:
            Dict with character model info and training status
        """
        try:
            # Validate image count (FLUX needs 5-10 images)
            if len(image_ids) < 5:
                return {
                    'success': False,
                    'error': f'Need at least 5 images for brand training (got {len(image_ids)})'
                }

            if len(image_ids) > 10:
                return {
                    'success': False,
                    'error': f'Maximum 10 images for brand training (got {len(image_ids)})'
                }

            # Get all images and verify ownership
            images = []
            for image_id in image_ids:
                try:
                    image = ImageHistory.objects.get(id=image_id, user=self.user)
                    images.append(image)
                except ImageHistory.DoesNotExist:
                    return {
                        'success': False,
                        'error': f'Image {image_id} not found or does not belong to user'
                    }

            # Generate trigger word if not provided
            if not trigger_word:
                # Convert brand name to trigger word: "Alpine Coffee" → "ALPINE_BRAND"
                trigger_word = brand_name.upper().replace(' ', '_').replace('.', '') + '_BRAND'

            # Create CharacterModel (repurposing for brand style)
            character = CharacterModel.objects.create(
                user=self.user,
                name=f"{brand_name} Brand Style",
                trigger_word=trigger_word,
                description=description or f"Brand style for {brand_name}",
                status='pending'
            )

            # Create CharacterTrainingImage records for each image
            for idx, image in enumerate(images):
                CharacterTrainingImage.objects.create(
                    character=character,
                    image_url=image.image_url,
                    caption=f"{brand_name} style example {idx + 1}"
                )

            self.memory.log_agent_action(
                action="brand_style_created",
                details={
                    'character_id': character.id,
                    'brand_name': brand_name,
                    'trigger_word': trigger_word,
                    'image_count': len(images)
                }
            )

            return {
                'success': True,
                'character_id': character.id,
                'brand_name': brand_name,
                'trigger_word': trigger_word,
                'status': 'pending',
                'message': f'✅ Brand style "{brand_name}" created with trigger word "{trigger_word}"! Ready to train.',
                'next_steps': 'Call submit_training() to start FLUX LoRA training'
            }

        except Exception as e:
            self.memory.log_agent_action(
                action="create_brand_style_error",
                details={'error': str(e)}
            )
            return {
                'success': False,
                'error': str(e)
            }

    def submit_training(self, character_id: int) -> Dict:
        """
        Submit brand style for FLUX LoRA training.

        This uses the existing Replicate training infrastructure.

        Args:
            character_id: ID of CharacterModel to train

        Returns:
            Dict with training status
        """
        try:
            # Get character
            character = CharacterModel.objects.get(id=character_id, user=self.user)

            if character.status != 'pending':
                return {
                    'success': False,
                    'error': f'Brand style is already {character.status}'
                }

            # Get training images
            training_images = CharacterTrainingImage.objects.filter(character=character)

            if training_images.count() < 5:
                return {
                    'success': False,
                    'error': 'Need at least 5 images for training'
                }

            # Submit to Replicate for training
            # (This uses the existing character training workflow)
            result = self.replicate.train_character(
                trigger_word=character.trigger_word,
                training_images=training_images,
                steps=1000,  # Good for brand style
                learning_rate=4e-4
            )

            if result['success']:
                # Update character status
                character.status = 'training'
                character.replicate_training_id = result['training_id']
                character.save()

                self.memory.log_agent_action(
                    action="training_submitted",
                    details={
                        'character_id': character_id,
                        'training_id': result['training_id'],
                        'trigger_word': character.trigger_word
                    }
                )

                return {
                    'success': True,
                    'character_id': character_id,
                    'training_id': result['training_id'],
                    'trigger_word': character.trigger_word,
                    'estimated_time': '30-60 minutes',
                    'message': f'✅ Brand style training started! Trigger word: "{character.trigger_word}"'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Training submission failed')
                }

        except CharacterModel.DoesNotExist:
            return {
                'success': False,
                'error': 'Brand style not found'
            }
        except Exception as e:
            self.memory.log_agent_action(
                action="submit_training_error",
                details={'character_id': character_id, 'error': str(e)}
            )
            return {
                'success': False,
                'error': str(e)
            }

    def check_training_status(self, character_id: int) -> Dict:
        """
        Check status of brand style training.

        Args:
            character_id: ID of CharacterModel

        Returns:
            Dict with current training status
        """
        try:
            character = CharacterModel.objects.get(id=character_id, user=self.user)

            if not character.replicate_training_id:
                return {
                    'success': True,
                    'status': character.status,
                    'message': 'Training not yet started'
                }

            # Check with Replicate
            status_result = self.replicate.check_training_status(
                character.replicate_training_id
            )

            if status_result['success']:
                # Update character status
                old_status = character.status
                character.status = status_result['status']

                if status_result['status'] == 'succeeded':
                    character.trained_model_url = status_result.get('model_url')

                character.save()

                # Log status change
                if old_status != character.status:
                    self.memory.log_agent_action(
                        action="training_status_changed",
                        details={
                            'character_id': character_id,
                            'old_status': old_status,
                            'new_status': character.status
                        }
                    )

                return {
                    'success': True,
                    'character_id': character_id,
                    'status': character.status,
                    'trigger_word': character.trigger_word,
                    'model_url': character.trained_model_url if character.status == 'succeeded' else None,
                    'message': self._get_status_message(character.status, character.trigger_word)
                }
            else:
                return status_result

        except CharacterModel.DoesNotExist:
            return {
                'success': False,
                'error': 'Brand style not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_brand_styles(self, include_training: bool = False) -> List[Dict]:
        """
        List all brand styles for this user.

        Args:
            include_training: Include styles currently training

        Returns:
            List of brand style dictionaries
        """
        try:
            # Get all character models (which include brand styles)
            query = CharacterModel.objects.filter(user=self.user)

            if not include_training:
                query = query.filter(status='succeeded')

            # Filter to only brand styles (name ends with "Brand Style")
            brand_styles = query.filter(name__icontains='Brand Style')

            styles = []
            for character in brand_styles:
                styles.append({
                    'character_id': character.id,
                    'brand_name': character.name.replace(' Brand Style', ''),
                    'trigger_word': character.trigger_word,
                    'status': character.status,
                    'description': character.description,
                    'model_url': character.trained_model_url,
                    'created_at': character.created_at.isoformat()
                })

            self.memory.log_agent_action(
                action="list_brand_styles",
                details={'count': len(styles)}
            )

            return styles

        except Exception as e:
            self.memory.log_agent_action(
                action="list_brand_styles_error",
                details={'error': str(e)}
            )
            return []

    def _get_status_message(self, status: str, trigger_word: str) -> str:
        """Generate user-friendly status message."""
        messages = {
            'pending': f'Brand style ready to train. Call submit_training() to start.',
            'training': f'Brand style is training... Use trigger word "{trigger_word}" when ready (30-60 min).',
            'succeeded': f'✅ Brand style ready! Use trigger word "{trigger_word}" in your prompts for consistent branding.',
            'failed': f'❌ Training failed. Please try again with different images.',
            'canceled': f'Training was canceled.'
        }
        return messages.get(status, f'Status: {status}')

    def get_state_summary(self) -> Dict:
        """
        Get current state summary of the agent.

        Returns:
            Dict with agent state
        """
        all_styles = self.list_brand_styles(include_training=True)
        ready_styles = [s for s in all_styles if s['status'] == 'succeeded']

        return {
            'agent_name': 'BrandStyleAgent',
            'session_id': self.session_id,
            'user_id': self.user.id,
            'total_brand_styles': len(all_styles),
            'ready_styles': len(ready_styles),
            'training_styles': len([s for s in all_styles if s['status'] == 'training'])
        }
