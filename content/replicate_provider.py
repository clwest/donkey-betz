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


    def create_model_if_needed(self, destination: str) -> bool:
        """
        Create a model on Replicate if it doesn't exist

        Args:
            destination: Model destination (username/model-name)

        Returns:
            True if model exists or was created, False on error
        """
        if not destination or '/' not in destination:
            logger.error(f"Invalid destination format: {destination}")
            return False

        try:
            owner, name = destination.split('/', 1)

            # Try to get the model - if it exists, we're done
            try:
                model = self.client.models.get(f"{owner}/{name}")
                logger.info(f"✅ Model {destination} already exists")
                return True
            except ReplicateError as e:
                if '404' not in str(e):
                    # Some other error
                    raise
                # Model doesn't exist, create it
                logger.info(f"📦 Creating new model: {destination}")

            # Create the model
            model = self.client.models.create(
                owner=owner,
                name=name,
                visibility="private",  # Keep it private by default
                hardware="gpu-t4",  # Default hardware
                description=f"FLUX LoRA model for character: {name}"
            )

            logger.info(f"✅ Created model: {destination}")
            return True

        except Exception as e:
            logger.error(f"Failed to create model {destination}: {str(e)}")
            return False

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
            # Training parameters for Replicate's fast-flux-trainer
            # Note: fast-flux-trainer uses 'lora_type' instead of 'learning_rate'
            training_params = {
                "input_images": training_zip_url,
                "trigger_word": trigger_word,
                "lora_type": "subject",  # 'subject' for characters, 'style' for styles
                "steps": steps,
            }

            # Add optional parameters (fast-flux-trainer ignores most of these)
            # Keep for backward compatibility
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
            # NOTE: Replicate REQUIRES a destination for training
            if not destination:
                return TrainingResult(
                    success=False,
                    error_message="Destination is required. Please create a model on Replicate.com first, then provide the destination as 'username/model-name'"
                )

            # Check if destination exists or try to create it
            logger.info(f"   Checking destination: {destination}")
            if not self.create_model_if_needed(destination):
                # Model doesn't exist and can't be created - provide helpful error
                return TrainingResult(
                    success=False,
                    error_message=f"Model '{destination}' doesn't exist and cannot be created automatically (permission denied). "
                                f"Please manually create the model on Replicate.com: "
                                f"https://replicate.com/create-model (Name: {destination.split('/')[-1]}, Visibility: Private)"
                )

            # Create training with destination
            # Using Replicate's official fast-flux-trainer (faster than ostris trainer!)
            logger.info(f"   Training with destination: {destination}")
            logger.info(f"   Using fast-flux-trainer for faster training")
            training = self.client.trainings.create(
                model="replicate/fast-flux-trainer",
                version="8b10794665aed907bb98a1a5324cd1d3a8bea0e9b31e65210967fb9c9e2e08ed",
                input=training_params,
                destination=destination
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

            # Add progress estimate based on status with detailed messages
            if training.status == "starting":
                result["progress"] = 10
                result["progress_message"] = "🚀 Preparing training environment..."
            elif training.status == "processing":
                # Try to parse logs for better progress estimation
                progress = 50  # Default mid-point
                progress_message = "🧠 Training character model..."

                # Parse logs to estimate progress more accurately
                if result.get("logs"):
                    logs = result["logs"]
                    # Look for epoch/step information in logs
                    if "epoch" in logs.lower():
                        # Try to extract epoch progress
                        # Most LoRA training is 10-50 epochs
                        # This is a rough estimation
                        if "epoch 1/" in logs.lower() or "epoch 2/" in logs.lower():
                            progress = 20
                            progress_message = "🎨 Training initial patterns..."
                        elif "epoch 3/" in logs.lower() or "epoch 4/" in logs.lower() or "epoch 5/" in logs.lower():
                            progress = 40
                            progress_message = "🖼️ Learning character features..."
                        elif "epoch 6/" in logs.lower() or "epoch 7/" in logs.lower() or "epoch 8/" in logs.lower():
                            progress = 60
                            progress_message = "✨ Refining character details..."
                        elif "epoch 9/" in logs.lower() or "epoch 10/" in logs.lower():
                            progress = 80
                            progress_message = "🎯 Finalizing model..."
                        else:
                            # Later epochs
                            progress = 90
                            progress_message = "🏁 Almost complete..."

                result["progress"] = progress
                result["progress_message"] = progress_message
            elif training.status == "succeeded":
                result["progress"] = 100
                result["progress_message"] = "✅ Character training complete!"
                # Extract model info
                if training.output:
                    result["model_version"] = training.output.get("version")
                    result["weights_url"] = training.output.get("weights")
            elif training.status == "failed":
                result["progress"] = 0
                result["progress_message"] = "❌ Training failed"
                result["error"] = training.error if hasattr(training, 'error') else "Training failed"
            elif training.status == "canceled":
                result["progress"] = 0
                result["progress_message"] = "⚠️ Training canceled"

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
