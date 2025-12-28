"""
Trained Creation Agent - Session 134

Specialized agent for generating images using trained FLUX LoRA models.
Uses Replicate API with custom LoRA weights from character/style training.

Architecture:
    AI Assistant (detects trained style intent) → Trained Creation Agent → Replicate FLUX API → LoRA Generation
"""

import logging
import requests
import time
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()
logger = logging.getLogger(__name__)


class TrainedCreationAgent:
    """
    Specialized agent for image generation using trained LoRA models.

    Responsibilities:
        - Resolve character/style model by name or ID
        - Generate images using FLUX with LoRA weights
        - Poll Replicate API for results
        - Associate generated images with projects
        - Track agent contributions
    """

    # FLUX model version for generation with LoRA
    FLUX_DEV_VERSION = "85a7e01f60cf31fbb0d22c48f9719fa7f9f6ab8d"

    def __init__(self, user: User, project_id: Optional[str] = None):
        """
        Initialize Trained Creation Agent.

        Args:
            user: User requesting image generation
            project_id: Optional project ID to associate result with
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = "Trained Creation Agent"

        # Get Replicate API key
        self.api_token = settings.EXTERNAL_API_KEYS.get('REPLICATE_API_KEY')
        if not self.api_token:
            raise ValueError("REPLICATE_API_KEY not configured")

    def execute(
        self,
        prompt: str,
        character_model_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute image generation with trained LoRA model.

        Args:
            prompt: Text description of the image to generate
            character_model_name: Name or ID of the trained character/style model
            **kwargs: Additional generation parameters
                - lora_scale: Strength of LoRA effect (default: 0.8)
                - width: Image width (default: 1024)
                - height: Image height (default: 1024)
                - num_outputs: Number of images (default: 1)
                - num_inference_steps: Generation steps (default: 28)
                - guidance_scale: Prompt adherence (default: 3.5)

        Returns:
            Dict with success status and generation results
        """
        logger.info(f"🤖 {self.agent_name} starting LoRA generation")
        logger.info(f"   User: {self.user.username}")
        logger.info(f"   Prompt: {prompt[:80]}...")
        logger.info(f"   Character Model: {character_model_name}")
        logger.info(f"   Project ID: {self.project_id or 'None'}")

        try:
            # Step 1: Resolve character model
            character_model = self._resolve_character_model(character_model_name)
            if not character_model:
                return {
                    'success': False,
                    'error': f'Character model "{character_model_name}" not found or not completed training'
                }

            logger.info(f"✅ Character model resolved: {character_model.name}")
            logger.info(f"   Replicate Model: {character_model.replicate_model_name}")
            logger.info(f"   Version ID: {character_model.replicate_version_id}")

            # Step 2: Extract generation parameters
            lora_scale = kwargs.get('lora_scale', 0.8)
            width = kwargs.get('width', 1024)
            height = kwargs.get('height', 1024)
            num_outputs = kwargs.get('num_outputs', 1)
            num_inference_steps = kwargs.get('num_inference_steps', 28)
            guidance_scale = kwargs.get('guidance_scale', 3.5)

            logger.info(f"🚀 Generating {num_outputs} image(s) with LoRA scale: {lora_scale}")

            # Step 3: Call Replicate API
            # The trained model IS the version we call directly (not LoRA weights parameter)
            prediction = self._create_prediction(
                prompt=prompt,
                model_owner=character_model.replicate_model_name.split('/')[0],
                model_name=character_model.replicate_model_name.split('/')[1],
                version_id=character_model.replicate_version_id,
                width=width,
                height=height,
                num_outputs=num_outputs,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )

            if not prediction:
                return {
                    'success': False,
                    'error': 'Failed to create Replicate prediction'
                }

            prediction_id = prediction.get('id')
            logger.info(f"✅ Prediction created: {prediction_id}")
            logger.info(f"   Status: {prediction.get('status')}")

            # Step 4: Poll for results
            result = self._poll_prediction(prediction_id)

            if not result or result.get('status') == 'failed':
                error_msg = result.get('error', 'Unknown error') if result else 'Polling failed'
                logger.error(f"❌ Generation failed: {error_msg}")
                return {
                    'success': False,
                    'error': f"Generation failed: {error_msg}"
                }

            # Step 5: Save to database
            image_urls = result.get('output', [])
            if not image_urls:
                return {
                    'success': False,
                    'error': 'No images in prediction output'
                }

            image_ids = self._save_images(
                urls=image_urls,
                prompt=prompt,
                character_model=character_model,
                session_id=kwargs.get('session_id'),
                project_id=self.project_id  # Session 134: Fix project association
            )

            logger.info(f"✅ {self.agent_name} completed successfully!")
            logger.info(f"   Generated: {len(image_ids)} image(s)")
            logger.info(f"   Model: {character_model.name}")

            return {
                'success': True,
                'message': f"✨ Generated {len(image_ids)} image(s) using {character_model.name}. Check your project gallery!",
                'image_ids': image_ids,
                'model_used': character_model.replicate_model_name,
                'character_model': character_model.name
            }

        except Exception as e:
            logger.error(f"❌ {self.agent_name} failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _resolve_character_model(self, identifier: str):
        """
        Resolve character model by name, trigger word, or ID.

        Args:
            identifier: Model name, trigger word, or UUID
                Examples:
                - UUID: "2ef834f7-31f5-4689-aae9-710a55f90b72"
                - Name: "ai-content-generation-company-style"
                - Trigger: "AI CONTENT GENERATION COMPANY STYLE" (case-insensitive)

        Returns:
            CharacterModel object or None if not found/not completed
        """
        from content.models import CharacterModel

        try:
            # Try UUID first
            model = CharacterModel.objects.get(id=identifier, user=self.user)
            if model.training_status == 'completed':
                return model
        except (ValueError, CharacterModel.DoesNotExist):
            pass

        # Try by exact name match
        try:
            model = CharacterModel.objects.filter(
                name=identifier,
                user=self.user,
                training_status='completed'
            ).order_by('-created_at').first()
            if model:
                return model
        except Exception:
            pass

        # Session 134: Try by trigger word (case-insensitive, remove dashes/spaces)
        # This handles Whisper transcription: "ai content generation company style"
        # Matches trigger_word: "AI-CONTENT-GENERATION-COMPANY-STYLE"
        try:
            # Normalize identifier: uppercase, remove dashes/spaces/underscores
            normalized_identifier = identifier.upper().replace('-', '').replace('_', '').replace(' ', '')

            # Get all completed models for this user
            models = CharacterModel.objects.filter(
                user=self.user,
                training_status='completed'
            ).order_by('-created_at')

            # Check each model's trigger word
            for model in models:
                if model.trigger_word:
                    # Normalize trigger word same way
                    normalized_trigger = model.trigger_word.upper().replace('-', '').replace('_', '').replace(' ', '')
                    if normalized_identifier == normalized_trigger:
                        logger.info(f"✅ Matched by trigger word: '{identifier}' → '{model.trigger_word}'")
                        return model

        except Exception as e:
            logger.error(f"❌ Error matching trigger word: {e}")

        return None

    def _create_prediction(
        self,
        prompt: str,
        model_owner: str,
        model_name: str,
        version_id: str,
        width: int,
        height: int,
        num_outputs: int,
        num_inference_steps: int,
        guidance_scale: float
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Replicate prediction using a trained model directly.

        Args:
            prompt: Text prompt for generation
            model_owner: Owner of the trained model (e.g., 'clwest')
            model_name: Name of the trained model
            version_id: Version ID of the trained model
            Other args: Generation parameters

        Returns:
            Prediction response dict or None if failed
        """
        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "version": version_id,  # Use the trained model's version directly
            "input": {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_outputs": num_outputs,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "output_format": "png",
                "output_quality": 100
            }
        }

        try:
            logger.info(f"🔍 Replicate API payload:")
            logger.info(f"   URL: https://api.replicate.com/v1/predictions")
            logger.info(f"   Trained model: {model_owner}/{model_name}")
            logger.info(f"   Version: {payload['version']}")

            response = requests.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Replicate API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   Response body: {e.response.text}")
            return None

    def _poll_prediction(
        self,
        prediction_id: str,
        max_wait_seconds: int = 120,
        poll_interval: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        Poll Replicate prediction until completion.

        Args:
            prediction_id: Prediction UUID
            max_wait_seconds: Maximum time to wait (default: 120s)
            poll_interval: Seconds between polls (default: 2s)

        Returns:
            Final prediction dict or None if timeout/error
        """
        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }

        url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
        start_time = time.time()

        while (time.time() - start_time) < max_wait_seconds:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                prediction = response.json()

                status = prediction.get('status')
                logger.info(f"   Polling status: {status}")

                if status == 'succeeded':
                    logger.info(f"✅ Prediction succeeded!")
                    return prediction
                elif status == 'failed':
                    logger.error(f"❌ Prediction failed: {prediction.get('error')}")
                    return prediction
                elif status in ['canceled', 'cancelled']:
                    logger.warning(f"⚠️ Prediction was canceled")
                    return prediction

                # Still processing, wait and poll again
                time.sleep(poll_interval)

            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Polling request failed: {e}")
                return None

        logger.warning(f"⚠️ Polling timeout after {max_wait_seconds}s")
        return None

    def _save_images(
        self,
        urls: list,
        prompt: str,
        character_model,
        session_id: Optional[str],
        project_id: Optional[str] = None  # Session 134: Accept project_id
    ) -> list:
        """
        Save generated images to database.

        Args:
            urls: List of image URLs from Replicate
            prompt: Generation prompt
            character_model: CharacterModel used
            session_id: Optional session ID

        Returns:
            List of image IDs
        """
        import uuid
        import os
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        from core.views_image import save_to_history

        image_ids = []
        for idx, url in enumerate(urls):
            try:
                # Step 1: Download image from Replicate URL
                logger.info(f"📥 Downloading image from Replicate: {url[:80]}...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Step 2: Generate unique filename
                unique_id = uuid.uuid4()
                filename = f"lora-{unique_id}.png"
                file_path = os.path.join('generated', filename)

                # Step 3: Save to media storage
                content_file = ContentFile(response.content)
                saved_path = default_storage.save(file_path, content_file)
                logger.info(f"💾 Saved to: {saved_path}")

                # Step 4: Resolve project if project_id provided
                project_obj = None
                if project_id:
                    try:
                        from content.models import CreativeProject
                        project_obj = CreativeProject.objects.get(id=project_id)
                        logger.info(f"✅ Linked to project: {project_obj.name}")
                    except CreativeProject.DoesNotExist:
                        logger.warning(f"⚠️ Project {project_id} not found, image will be unlinked")
                    except Exception as e:
                        logger.error(f"❌ Error fetching project: {e}")

                # Step 5: Save to ImageHistory using helper function
                history = save_to_history(
                    user=self.user,
                    file_path=saved_path,
                    image_type='generated',
                    prompt=prompt,
                    parameters={
                        'character_model': character_model.name,
                        'lora_version': character_model.replicate_version_id
                    },
                    model_used=character_model.replicate_model_name,
                    style='lora-trained',
                    parent_image=None,
                    seed=None,
                    session=None,  # TODO: Link to AISession if available
                    project=project_obj,  # Session 134: Project association fixed!
                    agent_name='trained-creation-agent'  # Session 133: Agent tracking
                )

                image_ids.append(str(history.id))
                seq_num = history.get_sequential_number()
                logger.info(f"✅ Saved image #{seq_num} to database (LoRA generation)")

            except Exception as e:
                logger.error(f"❌ Failed to save image {idx + 1}: {str(e)}")
                continue

        return image_ids
