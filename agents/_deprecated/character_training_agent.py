"""
Character Training Agent - Session 128 Part 2

Specialized agent for character training using Replicate FLUX LoRA.
Handles training image upload, validation, and model training workflows.

Architecture:
    AI Assistant (detects intent) → Character Training Agent → Character Training Service → Replicate API
"""

import logging
from typing import Dict, Any, Optional, List
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from content.models import CharacterModel
from content.character_training import (
    validate_training_image,
    process_training_images,
    create_training_zip,
    submit_training_job,
    update_training_status,
    create_character_workflow
)

User = get_user_model()
logger = logging.getLogger(__name__)


class CharacterTrainingAgent:
    """
    Specialized agent for character training operations.

    Responsibilities:
        - Validate training images (minimum 5-20 images)
        - Create training datasets
        - Submit FLUX LoRA training jobs to Replicate
        - Monitor training progress
        - Register trained models
        - Associate characters with user projects
    """

    def __init__(self, user: User, project_id: Optional[str] = None):
        """
        Initialize Character Training Agent.

        Args:
            user: User creating the character
            project_id: Optional project ID to associate result with
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = "Character Training Agent"

    def execute(
        self,
        operation: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a character training operation.

        Args:
            operation: Type of operation ('create_character', 'check_training_status',
                      'submit_training')
            **kwargs: Operation-specific parameters

        Returns:
            Dict with success status and operation results
        """
        logger.info(f"🤖 {self.agent_name} starting {operation} workflow")
        logger.info(f"   User: {self.user.username}")
        logger.info(f"   Operation: {operation}")

        try:
            # Route to appropriate operation
            operation_map = {
                'create_character': self._create_character,
                'check_training_status': self._check_training_status,
                'submit_training': self._submit_training
            }

            if operation not in operation_map:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}'
                }

            logger.info(f"🚀 Executing {operation} operation...")

            # Execute the operation
            result = operation_map[operation](**kwargs)

            if result.get('success'):
                logger.info(f"✅ {self.agent_name} {operation} completed successfully")
            else:
                logger.error(f"❌ {self.agent_name} {operation} failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"❌ {self.agent_name} failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _create_character(self, **kwargs) -> Dict[str, Any]:
        """Create a new character with training images."""
        try:
            name = kwargs.get('name')
            description = kwargs.get('description', '')
            trigger_word = kwargs.get('trigger_word')
            image_urls = kwargs.get('image_urls', [])
            training_steps = kwargs.get('training_steps', 1000)
            learning_rate = kwargs.get('learning_rate', 0.0004)
            auto_submit = kwargs.get('auto_submit', False)

            if not name or not trigger_word:
                return {
                    'success': False,
                    'error': 'Name and trigger_word are required'
                }

            if not image_urls or len(image_urls) < 5:
                return {
                    'success': False,
                    'error': 'At least 5 training images are required'
                }

            logger.info(f"📝 Creating character: {name}")
            logger.info(f"   Trigger word: {trigger_word}")
            logger.info(f"   Images: {len(image_urls)}")
            logger.info(f"   Training steps: {training_steps}")

            # Convert image URLs to uploaded files
            # Note: This is a simplified implementation
            # In production, you'd download images from URLs or accept file uploads
            image_files = []
            for url in image_urls[:20]:  # Max 20 images
                # Placeholder - would need to download images from URLs
                logger.info(f"   Processing image: {url}")

            if not image_files:
                return {
                    'success': False,
                    'error': 'No valid images found. Image download not yet implemented.'
                }

            # Create character using service layer
            character, warnings = create_character_workflow(
                user=self.user,
                name=name,
                description=description,
                trigger_word=trigger_word,
                image_files=image_files,
                training_steps=training_steps,
                learning_rate=learning_rate,
                auto_submit=auto_submit
            )

            logger.info(f"✅ Character created successfully!")
            logger.info(f"   Character ID: {character.id}")
            logger.info(f"   Status: {character.training_status}")

            return {
                'success': True,
                'character_id': str(character.id),
                'name': character.name,
                'trigger_word': character.trigger_word,
                'status': character.training_status,
                'warnings': warnings,
                'message': f"✅ Character '{name}' created successfully!\n\n" + \
                          f"Trigger word: {trigger_word}\n" + \
                          f"Training images: {len(image_files)}\n" + \
                          f"Status: {character.training_status}\n\n" + \
                          (f"Training submitted to Replicate!" if auto_submit else "Ready to submit for training.")
            }

        except Exception as e:
            logger.error(f"❌ Create character operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to create character: {str(e)}"
            }

    def _submit_training(self, **kwargs) -> Dict[str, Any]:
        """Submit character for training on Replicate."""
        try:
            character_id = kwargs.get('character_id')

            if not character_id:
                return {
                    'success': False,
                    'error': 'character_id is required'
                }

            logger.info(f"🚀 Submitting character {character_id} for training...")

            # Get character
            character = CharacterModel.objects.get(id=character_id, user=self.user)

            # Submit training job
            result = submit_training_job(character)

            if result.get('success'):
                logger.info(f"✅ Training submitted successfully!")
                logger.info(f"   Training ID: {result.get('training_id')}")
                logger.info(f"   Status: {result.get('status')}")

                return {
                    'success': True,
                    'character_id': str(character.id),
                    'training_id': result.get('training_id'),
                    'status': result.get('status'),
                    'estimated_time_minutes': result.get('estimated_time', 20),
                    'message': f"✅ Training submitted to Replicate!\n\n" + \
                              f"Character: {character.name}\n" + \
                              f"Trigger word: {character.trigger_word}\n" + \
                              f"Training ID: {result.get('training_id')}\n" + \
                              f"Estimated time: ~{result.get('estimated_time', 20)} minutes\n\n" + \
                              f"Check status with: 'Check training status for character {character.name}'"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Training submission failed')
                }

        except CharacterModel.DoesNotExist:
            logger.error(f"❌ Character {character_id} not found")
            return {
                'success': False,
                'error': f'Character {character_id} not found'
            }
        except Exception as e:
            logger.error(f"❌ Submit training operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to submit training: {str(e)}"
            }

    def _check_training_status(self, **kwargs) -> Dict[str, Any]:
        """Check training status for a character."""
        try:
            character_id = kwargs.get('character_id')

            if not character_id:
                return {
                    'success': False,
                    'error': 'character_id is required'
                }

            logger.info(f"🔍 Checking training status for character {character_id}...")

            # Get character
            character = CharacterModel.objects.get(id=character_id, user=self.user)

            # Update status from Replicate
            result = update_training_status(character)

            logger.info(f"📊 Training status: {character.training_status}")

            status_messages = {
                'preparing': 'Preparing training data...',
                'pending': 'Queued for training...',
                'processing': 'Training in progress...',
                'completed': 'Training completed! Model ready to use.',
                'failed': 'Training failed.',
                'cancelled': 'Training cancelled.'
            }

            message = status_messages.get(character.training_status, 'Unknown status')

            response = {
                'success': True,
                'character_id': str(character.id),
                'name': character.name,
                'status': character.training_status,
                'message': f"📊 Character '{character.name}' Status\n\n" + \
                          f"Status: {character.training_status}\n" + \
                          f"{message}\n"
            }

            if character.training_status == 'completed':
                response['model_url'] = result.get('output', {}).get('version') if result else None
                response['message'] += f"\n✅ Ready to generate images with trigger word: '{character.trigger_word}'"

            elif character.training_status == 'failed':
                response['error'] = result.get('error') if result else 'Unknown error'
                response['message'] += f"\n❌ Error: {response['error']}"

            return response

        except CharacterModel.DoesNotExist:
            logger.error(f"❌ Character {character_id} not found")
            return {
                'success': False,
                'error': f'Character {character_id} not found'
            }
        except Exception as e:
            logger.error(f"❌ Check status operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to check training status: {str(e)}"
            }
