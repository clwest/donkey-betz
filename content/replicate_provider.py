"""
Replicate API Provider for Character Training
Session 74: Integrated from super-me-photo-ai-api project

Provides FLUX LoRA training for consistent character generation.

Features:
- Train custom character models with 10-12 images
- Generate images with trained models using trigger words
- Track training progress and status
- Manage model versions and deployments

Uses Replicate's ostris/flux-dev-lora-trainer for training.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from django.conf import settings

logger = logging.getLogger(__name__)

# Import replicate
try:
    import replicate
    from replicate.exceptions import ReplicateError
    HAS_REPLICATE = True
except ImportError:
    HAS_REPLICATE = False
    logger.warning("Replicate package not installed. Character training unavailable.")


@dataclass
class TrainingResult:
    """Result from training submission"""
    success: bool
    training_id: str = ""
    status: str = "starting"
    error_message: str = ""
    estimated_time_minutes: int = 45  # Average 30-60 minutes


@dataclass
class GenerationResult:
    """Result from image generation with trained model"""
    success: bool
    prediction_id: str = ""
    images: List[str] = None  # List of URLs
    status: str = "starting"
    error_message: str = ""

    def __post_init__(self):
        if self.images is None:
            self.images = []


class ReplicateProvider:
    """
    Replicate API provider for character training & generation
    Extracted and integrated from super-me-photo-ai-api project
    """

    def __init__(self):
        """Initialize Replicate client"""
        # Get API key from settings
        self.api_key = settings.EXTERNAL_API_KEYS.get('REPLICATE_API_KEY', '') if hasattr(settings, 'EXTERNAL_API_KEYS') else ''

        self.available = HAS_REPLICATE and bool(self.api_key)

        if not HAS_REPLICATE:
            logger.warning("Replicate package not available")
            return

        if not self.api_key:
            logger.warning("REPLICATE_API_KEY not configured")
            return

        # Initialize client
        try:
            self.client = replicate.Client(api_token=self.api_key)
            logger.info("✅ Replicate client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Replicate client: {str(e)}")
            self.available = False


    def train_character(
        self,
        training_zip_url: str,
        trigger_word: str = "TOK",
        steps: int = 1000,
        learning_rate: float = 0.0004,
        destination: Optional[str] = None,
        **kwargs
    ) -> TrainingResult:
        """
        Train a FLUX LoRA model on character images

        Args:
            training_zip_url: Public URL to zip file with training images
            trigger_word: Trigger word to use in prompts (e.g., "TOK")
            steps: Number of training steps (default: 1000)
            learning_rate: Learning rate (default: 0.0004)
            destination: Where to save model (username/model-name)

        Returns:
            TrainingResult with training_id for status tracking
        """

        if not self.available:
            return TrainingResult(
                success=False,
                error_message="Replicate API not available or not configured"
            )

        try:
            # Training parameters
            training_params = {
                "input_images": training_zip_url,
                "trigger_word": trigger_word,
                "steps": steps,
                "learning_rate": learning_rate,
            }

            # Add optional parameters
            if kwargs.get('lora_rank'):
                training_params['lora_rank'] = kwargs['lora_rank']
            if kwargs.get('batch_size'):
                training_params['batch_size'] = kwargs['batch_size']
            if kwargs.get('resolution'):
                training_params['resolution'] = kwargs['resolution']

            logger.info(f"📤 [REPLICATE] Starting training with trigger word: {trigger_word}")
            logger.info(f"   Steps: {steps}, Learning rate: {learning_rate}")

            # Submit training job
            # Using the official FLUX LoRA trainer
            training = self.client.trainings.create(
                model="ostris/flux-dev-lora-trainer",
                version="e440909d3512c31646ee2e0c7d6f6f4923224863a6a10c494606e79fb5844497",  # Latest stable version
                input=training_params,
                destination=destination  # Where to save the model
            )

            logger.info(f"✅ [REPLICATE] Training submitted: {training.id}")
            logger.info(f"   Status: {training.status}")

            return TrainingResult(
                success=True,
                training_id=training.id,
                status=training.status,
                estimated_time_minutes=45  # Typical 30-60 minutes
            )

        except ReplicateError as e:
            logger.error(f"Replicate API error: {str(e)}")
            return TrainingResult(
                success=False,
                error_message=f"Replicate API error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Training submission error: {str(e)}")
            return TrainingResult(
                success=False,
                error_message=str(e)
            )


    def check_training_status(self, training_id: str) -> Dict[str, Any]:
        """
        Check status of a training job

        Args:
            training_id: Training ID returned from train_character()

        Returns:
            Dict with status, progress, and model info
        """

        if not self.available:
            return {
                "success": False,
                "error_message": "Replicate API not available"
            }

        try:
            training = self.client.trainings.get(training_id)

            result = {
                "success": True,
                "training_id": training.id,
                "status": training.status,  # starting, processing, succeeded, failed, canceled
                "logs": training.logs if hasattr(training, 'logs') else None,
            }

            # Add progress estimate based on status
            if training.status == "starting":
                result["progress"] = 5
            elif training.status == "processing":
                result["progress"] = 50  # Rough estimate, can be refined
            elif training.status == "succeeded":
                result["progress"] = 100
                # Extract model info
                if training.output:
                    result["model_version"] = training.output.get("version")
                    result["weights_url"] = training.output.get("weights")
            elif training.status == "failed":
                result["progress"] = 0
                result["error"] = training.error if hasattr(training, 'error') else "Training failed"

            return result

        except ReplicateError as e:
            logger.error(f"Failed to check training status: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
        except Exception as e:
            logger.error(f"Training status check error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }


    def generate_with_character(
        self,
        model_version: str,
        prompt: str,
        trigger_word: str = "TOK",
        num_outputs: int = 2,
        guidance_scale: float = 3.5,
        num_inference_steps: int = 28,
        **kwargs
    ) -> GenerationResult:
        """
        Generate images using a trained character model

        Args:
            model_version: Full model version ID (user/model:version)
            prompt: Generation prompt (should include trigger word)
            trigger_word: Trigger word for character (default: TOK)
            num_outputs: Number of images to generate (1-4)
            guidance_scale: Guidance scale (default: 3.5)
            num_inference_steps: Inference steps (default: 28)

        Returns:
            GenerationResult with prediction_id and image URLs
        """

        if not self.available:
            return GenerationResult(
                success=False,
                error_message="Replicate API not available"
            )

        # Ensure trigger word is in prompt
        if trigger_word not in prompt:
            logger.warning(f"Trigger word '{trigger_word}' not found in prompt. Adding it.")
            prompt = f"{trigger_word} {prompt}"

        try:
            input_params = {
                "prompt": prompt,
                "num_outputs": num_outputs,
                "guidance_scale": guidance_scale,
                "num_inference_steps": num_inference_steps,
                "output_format": "jpg",
                "output_quality": 90,
            }

            # Add optional parameters
            if kwargs.get('aspect_ratio'):
                input_params['aspect_ratio'] = kwargs['aspect_ratio']
            if kwargs.get('seed'):
                input_params['seed'] = kwargs['seed']

            logger.info(f"📤 [REPLICATE] Generating with model: {model_version}")
            logger.info(f"   Prompt: {prompt}")

            # Submit generation request
            prediction = self.client.predictions.create(
                version=model_version,
                input=input_params
            )

            logger.info(f"✅ [REPLICATE] Generation submitted: {prediction.id}")

            return GenerationResult(
                success=True,
                prediction_id=prediction.id,
                status=prediction.status
            )

        except ReplicateError as e:
            logger.error(f"Replicate API error: {str(e)}")
            return GenerationResult(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            return GenerationResult(
                success=False,
                error_message=str(e)
            )


    def check_prediction_status(self, prediction_id: str) -> Dict[str, Any]:
        """
        Check status of a generation prediction

        Args:
            prediction_id: Prediction ID from generate_with_character()

        Returns:
            Dict with status, images, and progress
        """

        if not self.available:
            return {
                "success": False,
                "error_message": "Replicate API not available"
            }

        try:
            prediction = self.client.predictions.get(prediction_id)

            result = {
                "success": True,
                "prediction_id": prediction.id,
                "status": prediction.status,  # starting, processing, succeeded, failed, canceled
            }

            if prediction.status == "succeeded" and prediction.output:
                result["images"] = prediction.output if isinstance(prediction.output, list) else [prediction.output]
            elif prediction.status == "failed":
                result["error"] = prediction.error if hasattr(prediction, 'error') else "Generation failed"

            return result

        except ReplicateError as e:
            logger.error(f"Failed to check prediction status: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
        except Exception as e:
            logger.error(f"Prediction status check error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }


# Singleton instance
_replicate_provider = None

def get_replicate_provider() -> ReplicateProvider:
    """Get singleton instance of Replicate provider"""
    global _replicate_provider
    if _replicate_provider is None:
        _replicate_provider = ReplicateProvider()
    return _replicate_provider
