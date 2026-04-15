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
from core.error_messages import ErrorMessageBuilder

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


@dataclass
class ThreeDGenerationResult:
    """Result from 3D model generation (TRELLIS)"""
    success: bool
    prediction_id: str = ""
    model_file: str = ""  # GLB file URL
    color_video: str = ""  # Color render video URL
    gaussian_ply: str = ""  # Point cloud file URL
    status: str = "starting"
    error_message: str = ""


@dataclass
class LipSyncResult:
    """Result from lip sync video generation (Sync Labs Lipsync-2)"""
    success: bool
    prediction_id: str = ""
    video_url: str = ""  # Output video URL with synced lips
    status: str = "starting"  # starting, processing, succeeded, failed
    error_message: str = ""
    estimated_time: int = 60  # Estimated processing time in seconds


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
                error_message=ErrorMessageBuilder.api_key_error("Replicate", "REPLICATE_API_KEY")["user_message"]
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
                "error_message": ErrorMessageBuilder.api_key_error("Replicate", "REPLICATE_API_KEY")["user_message"]
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
                "error_message": ErrorMessageBuilder.api_key_error("Replicate", "REPLICATE_API_KEY")["user_message"]
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


    def generate_3d_from_images(
        self,
        image_urls: List[str],
        generate_model: bool = True,
        generate_color: bool = True,
        save_gaussian_ply: bool = True,
        **kwargs
    ) -> ThreeDGenerationResult:
        """
        Generate 3D model from images using TRELLIS

        Args:
            image_urls: List of public image URLs (1-4 images for multi-view)
            generate_model: Generate GLB 3D model file (default: True)
            generate_color: Generate color video render (default: True)
            save_gaussian_ply: Save Gaussian point cloud (default: True)
            **kwargs: Additional TRELLIS parameters (texture_size, mesh_simplify, etc.)

        Returns:
            ThreeDGenerationResult with prediction_id and status
        """

        if not self.available:
            return ThreeDGenerationResult(
                success=False,
                error_message=ErrorMessageBuilder.api_key_error("Replicate", "REPLICATE_API_KEY")["user_message"]
            )

        if not image_urls:
            return ThreeDGenerationResult(
                success=False,
                error_message="At least one image URL is required"
            )

        # Track opened file handles for cleanup (Phase 2 P1: Fix file handle leaks)
        opened_files = []
        try:
            # Process image URLs/paths - Replicate SDK handles file uploads automatically
            processed_images = []
            for img_path in image_urls:
                if isinstance(img_path, str):
                    if img_path.startswith('http://') or img_path.startswith('https://'):
                        # Public URL - use as-is
                        processed_images.append(img_path)
                    else:
                        # Local file path - open and pass file handle
                        # Replicate SDK will automatically upload the file
                        import pathlib
                        file_path = pathlib.Path(img_path)
                        if file_path.exists():
                            # Use 'file' prefix for Replicate SDK file upload
                            # Track for cleanup to prevent file handle leaks
                            file_handle = open(img_path, 'rb')
                            opened_files.append(file_handle)
                            processed_images.append(file_handle)
                        else:
                            logger.warning(f"File not found: {img_path}")
                else:
                    # Already a file handle
                    processed_images.append(img_path)

            if not processed_images:
                return ThreeDGenerationResult(
                    success=False,
                    error_message="No valid images provided"
                )

            # Build TRELLIS input parameters
            input_params = {
                "images": processed_images,
                "generate_model": generate_model,
                "generate_color": generate_color,
                "save_gaussian_ply": save_gaussian_ply,
            }

            # Add optional parameters
            if 'texture_size' in kwargs:
                input_params['texture_size'] = kwargs['texture_size']
            if 'mesh_simplify' in kwargs:
                input_params['mesh_simplify'] = kwargs['mesh_simplify']
            if 'ss_sampling_steps' in kwargs:
                input_params['ss_sampling_steps'] = kwargs['ss_sampling_steps']
            if 'slat_sampling_steps' in kwargs:
                input_params['slat_sampling_steps'] = kwargs['slat_sampling_steps']

            logger.info(f"🎨 [REPLICATE] Starting 3D generation from {len(image_urls)} image(s)")
            logger.info(f"   Model: firtoz/trellis (version: e8f6c45...)")
            logger.info(f"   Generate GLB: {generate_model}, Color Video: {generate_color}, Gaussian: {save_gaussian_ply}")

            # Create prediction using TRELLIS model version
            # Note: Use version (not model) for pinned production behavior
            prediction = self.client.predictions.create(
                version="e8f6c45206993f297372f5436b90350817bd9b4a0d52d2a76df50c1c8afa2b3c",
                input=input_params
            )

            logger.info(f"✅ [REPLICATE] 3D generation submitted: {prediction.id}")
            logger.info(f"   Status: {prediction.status}")
            logger.info(f"   Estimated time: <1 minute")

            return ThreeDGenerationResult(
                success=True,
                prediction_id=prediction.id,
                status=prediction.status
            )

        except ReplicateError as e:
            logger.error(f"Replicate API error: {str(e)}")
            return ThreeDGenerationResult(
                success=False,
                error_message=f"Replicate API error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"3D generation submission error: {str(e)}")
            return ThreeDGenerationResult(
                success=False,
                error_message=str(e)
            )
        finally:
            # Phase 2 P1: Ensure all file handles are closed to prevent leaks
            for file_handle in opened_files:
                try:
                    file_handle.close()
                except Exception as _e:
                    logger.warning(
                        "replicate_provider.generate_3d_from_images: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )


    def check_3d_generation_status(self, prediction_id: str) -> Dict[str, Any]:
        """
        Check status of a 3D generation prediction

        Args:
            prediction_id: Prediction ID from generate_3d_from_images()

        Returns:
            Dict with status, model_file, color_video, gaussian_ply URLs
        """

        if not self.available:
            return {
                "success": False,
                "error_message": ErrorMessageBuilder.api_key_error("Replicate", "REPLICATE_API_KEY")["user_message"]
            }

        try:
            prediction = self.client.predictions.get(prediction_id)

            result = {
                "success": True,
                "prediction_id": prediction.id,
                "status": prediction.status,  # starting, processing, succeeded, failed, canceled
            }

            if prediction.status == "succeeded" and prediction.output:
                output = prediction.output
                # TRELLIS returns an object with model_file, color_video, gaussian_ply, etc.
                if isinstance(output, dict):
                    result["model_file"] = output.get("model_file", "")
                    result["color_video"] = output.get("color_video", "")
                    result["gaussian_ply"] = output.get("gaussian_ply", "")
                    result["normal_video"] = output.get("normal_video", "")
                else:
                    result["error"] = "Unexpected output format from TRELLIS"
            elif prediction.status == "failed":
                result["error"] = prediction.error if hasattr(prediction, 'error') else "3D generation failed"

            return result

        except ReplicateError as e:
            logger.error(f"Failed to check 3D generation status: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
        except Exception as e:
            logger.error(f"3D generation status check error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }

    # ===== LIP SYNC (Sync Labs Lipsync-2) =====
    # Session 175: Add lip sync for video production workflows

    def lip_sync(
        self,
        video_url: str,
        audio_url: str,
        sync_mode: str = "cut_off",
        temperature: float = 0.5,
        active_speaker: bool = False
    ) -> LipSyncResult:
        """
        Generate video with lip-synced speech using Sync Labs Lipsync-2

        Takes a video and audio file, and generates a new video where the
        speaker's lips are synced to match the audio.

        Args:
            video_url: URL to input video file (.mp4)
            audio_url: URL to input audio file (.wav, .mp3)
            sync_mode: How to handle audio/video duration mismatch
                       - "cut_off": Cut video when audio ends (default)
                       - "loop": Loop video to match audio length
                       - "bounce": Bounce (reverse) video to match audio
                       - "silence": Add silence if audio is shorter
                       - "remap": Remap video timing to match audio
            temperature: Expression intensity 0-1 (0.5 = natural, 1 = expressive)
            active_speaker: Auto-detect and only sync the active speaker

        Returns:
            LipSyncResult with prediction_id for polling

        Cost: ~$0.05 per second of output video
        """

        if not self.available:
            return LipSyncResult(
                success=False,
                error_message=ErrorMessageBuilder.api_key_error("Replicate", "REPLICATE_API_KEY")["user_message"]
            )

        if not video_url:
            return LipSyncResult(
                success=False,
                error_message="video_url is required - provide a URL to the input video"
            )

        if not audio_url:
            return LipSyncResult(
                success=False,
                error_message="audio_url is required - provide a URL to the audio file"
            )

        # Validate sync_mode
        valid_modes = ["loop", "bounce", "cut_off", "silence", "remap"]
        if sync_mode not in valid_modes:
            sync_mode = "cut_off"
            logger.warning(f"Invalid sync_mode, defaulting to 'cut_off'")

        # Clamp temperature
        temperature = max(0.0, min(1.0, temperature))

        try:
            logger.info(f"🎬 [LIP SYNC] Starting lip sync generation")
            logger.info(f"   Video: {video_url[:80]}...")
            logger.info(f"   Audio: {audio_url[:80]}...")
            logger.info(f"   Mode: {sync_mode}, Temperature: {temperature}")

            # Use Sync Labs Lipsync-2 model on Replicate
            # Model: sync/lipsync-2
            prediction = self.client.predictions.create(
                model="sync/lipsync-2",
                input={
                    "video": video_url,
                    "audio": audio_url,
                    "sync_mode": sync_mode,
                    "temperature": temperature,
                    "active_speaker": active_speaker
                }
            )

            logger.info(f"✅ [LIP SYNC] Prediction created: {prediction.id}")
            logger.info(f"   Status: {prediction.status}")

            return LipSyncResult(
                success=True,
                prediction_id=prediction.id,
                status=prediction.status,
                estimated_time=60  # Typically 30-120 seconds
            )

        except ReplicateError as e:
            logger.error(f"Replicate lip sync error: {str(e)}")
            return LipSyncResult(
                success=False,
                error_message=f"Lip sync failed: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Lip sync error: {str(e)}")
            return LipSyncResult(
                success=False,
                error_message=str(e)
            )

    # Session 1069: LatentSync version hash — community model requires explicit version
    LATENTSYNC_VERSION = "637ce1919f807ca20da3a448ddc2743535d2853649574cd52a933120e9b9e293"

    def lip_sync_latent(
        self,
        video_url: str,
        audio_url: str,
        guidance_scale: float = 1.0,
        seed: int = 0
    ) -> LipSyncResult:
        """
        Generate video with lip-synced speech using ByteDance LatentSync

        OPTIMIZED FOR: Cartoon, stylized, Pixar-style, and non-photorealistic characters!

        LatentSync uses an audio-conditioned latent diffusion model without
        intermediate motion representation, making it more flexible for
        stylized and animated content.

        Args:
            video_url: URL to input video file (.mp4)
            audio_url: URL to input audio file (.wav, .mp3)
            guidance_scale: Guidance scale (0-10, default 1)
            seed: Random seed (0 = random)

        Returns:
            LipSyncResult with prediction_id for polling

        Cost: ~$0.05-0.10 per second of output video
        Model: bytedance/latentsync v637ce191 (March 2025)
        """

        if not self.available:
            return LipSyncResult(
                success=False,
                error_message=ErrorMessageBuilder.api_key_error("Replicate", "REPLICATE_API_KEY")["user_message"]
            )

        if not video_url:
            return LipSyncResult(
                success=False,
                error_message="video_url is required - provide a URL to the input video"
            )

        if not audio_url:
            return LipSyncResult(
                success=False,
                error_message="audio_url is required - provide a URL to the audio file"
            )

        try:
            logger.info(f"🎨 [LATENT SYNC] Starting cartoon-optimized lip sync")
            logger.info(f"   Video: {video_url[:80]}...")
            logger.info(f"   Audio: {audio_url[:80]}...")
            logger.info(f"   Model: ByteDance LatentSync (cartoon-optimized)")

            # Session 1069: Use version= instead of model= — community models
            # require explicit version hash (model= returns 404)
            prediction = self.client.predictions.create(
                version=self.LATENTSYNC_VERSION,
                input={
                    "video": video_url,
                    "audio": audio_url,
                    "guidance_scale": guidance_scale,
                    "seed": seed
                }
            )

            logger.info(f"✅ [LATENT SYNC] Prediction created: {prediction.id}")
            logger.info(f"   Status: {prediction.status}")

            return LipSyncResult(
                success=True,
                prediction_id=prediction.id,
                status=prediction.status,
                estimated_time=100  # Typically completes in ~100 seconds
            )

        except ReplicateError as e:
            logger.error(f"LatentSync error: {str(e)}")
            return LipSyncResult(
                success=False,
                error_message=f"LatentSync failed: {str(e)}"
            )
        except Exception as e:
            logger.error(f"LatentSync error: {str(e)}")
            return LipSyncResult(
                success=False,
                error_message=str(e)
            )

    def check_lip_sync_status(self, prediction_id: str) -> Dict[str, Any]:
        """
        Check status of a lip sync prediction (works for both Sync Labs and LatentSync)

        Args:
            prediction_id: The prediction ID from lip_sync() or lip_sync_latent()

        Returns:
            Dict with status, progress, video_url (if complete), and error info
        """

        if not self.available:
            return {
                "success": False,
                "error_message": ErrorMessageBuilder.api_key_error("Replicate", "REPLICATE_API_KEY")["user_message"]
            }

        try:
            prediction = self.client.predictions.get(prediction_id)

            result = {
                "success": True,
                "prediction_id": prediction.id,
                "status": prediction.status,
            }

            # Map status to progress
            if prediction.status == "starting":
                result["progress"] = 10
                result["progress_message"] = "Initializing lip sync..."
            elif prediction.status == "processing":
                result["progress"] = 50
                result["progress_message"] = "Syncing lip movements to audio..."
            elif prediction.status == "succeeded":
                result["progress"] = 100
                result["progress_message"] = "Lip sync complete!"
                # Output is the video URL
                if prediction.output:
                    result["video_url"] = prediction.output
                    logger.info(f"✅ [LIP SYNC] Complete: {prediction.output}")
            elif prediction.status == "failed":
                result["progress"] = 0
                result["progress_message"] = "Lip sync failed"
                result["error"] = prediction.error or "Unknown error"
                logger.error(f"❌ [LIP SYNC] Failed: {prediction.error}")
            elif prediction.status == "canceled":
                result["progress"] = 0
                result["progress_message"] = "Lip sync canceled"

            return result

        except ReplicateError as e:
            logger.error(f"Failed to check lip sync status: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
        except Exception as e:
            logger.error(f"Lip sync status check error: {str(e)}")
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
