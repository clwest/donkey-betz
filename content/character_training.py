"""
Character Training Business Logic
Session 74 Phase 2: Training workflow implementation

Handles the complete character training workflow:
1. Image upload and validation
2. Zip file creation for Replicate
3. Training job submission
4. Status polling and updates
5. Model management
"""

import logging
import os
import zipfile
from io import BytesIO
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.utils import timezone

from content.models import CharacterModel, CharacterTrainingImage
from content.replicate_provider import get_replicate_provider

logger = logging.getLogger(__name__)

# Training image requirements
MIN_IMAGES = 5  # Lowered for testing (production: 10)
MAX_IMAGES = 20
MIN_RESOLUTION = 512
MAX_RESOLUTION = 2048
MAX_FILE_SIZE_MB = 10
SUPPORTED_FORMATS = {'JPEG', 'JPG', 'PNG', 'WEBP'}


class ImageValidationError(Exception):
    """Raised when an image doesn't meet training requirements"""
    pass


class TrainingWorkflowError(Exception):
    """Raised when training workflow encounters an error"""
    pass


def validate_training_image(image_file: UploadedFile) -> Dict[str, Any]:
    """
    Validate a single training image

    Args:
        image_file: Uploaded image file

    Returns:
        Dict with validation results and image metadata

    Raises:
        ImageValidationError: If image doesn't meet requirements
    """
    errors = []
    warnings = []

    # Check file size
    file_size_mb = image_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        errors.append(f"File too large: {file_size_mb:.1f}MB (max: {MAX_FILE_SIZE_MB}MB)")

    # Open and validate image
    try:
        img = Image.open(image_file)
        img.verify()  # Verify it's a valid image

        # Re-open after verify (verify closes the file)
        image_file.seek(0)
        img = Image.open(image_file)

        # Check format
        if img.format not in SUPPORTED_FORMATS:
            errors.append(f"Unsupported format: {img.format} (supported: {', '.join(SUPPORTED_FORMATS)})")

        # Check dimensions
        width, height = img.size
        if width < MIN_RESOLUTION or height < MIN_RESOLUTION:
            errors.append(f"Resolution too low: {width}x{height} (min: {MIN_RESOLUTION}x{MIN_RESOLUTION})")

        if width > MAX_RESOLUTION or height > MAX_RESOLUTION:
            warnings.append(f"High resolution: {width}x{height} (will be resized to {MAX_RESOLUTION})")

        # Check aspect ratio
        aspect_ratio = width / height
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:
            warnings.append(f"Unusual aspect ratio: {aspect_ratio:.2f} (recommended: 0.5-2.0)")

        # Check if image is too dark or bright
        if img.mode in ('RGB', 'RGBA'):
            grayscale = img.convert('L')
            avg_brightness = sum(grayscale.getdata()) / len(grayscale.getdata())

            if avg_brightness < 30:
                warnings.append("Image is very dark - may affect training quality")
            elif avg_brightness > 225:
                warnings.append("Image is very bright - may affect training quality")

        result = {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'width': width,
            'height': height,
            'format': img.format,
            'mode': img.mode,
            'file_size': image_file.size,
        }

        return result

    except Exception as e:
        raise ImageValidationError(f"Failed to validate image: {str(e)}")


def process_training_images(
    character: CharacterModel,
    image_files: List[UploadedFile]
) -> Tuple[List[CharacterTrainingImage], List[str]]:
    """
    Process and save training images

    Args:
        character: CharacterModel instance
        image_files: List of uploaded image files

    Returns:
        Tuple of (saved_images, validation_warnings)

    Raises:
        ImageValidationError: If images don't meet requirements
    """

    # Check image count
    if len(image_files) < MIN_IMAGES:
        raise ImageValidationError(
            f"Not enough images: {len(image_files)} provided (minimum: {MIN_IMAGES})"
        )

    if len(image_files) > MAX_IMAGES:
        raise ImageValidationError(
            f"Too many images: {len(image_files)} provided (maximum: {MAX_IMAGES})"
        )

    saved_images = []
    all_warnings = []

    with transaction.atomic():
        for idx, image_file in enumerate(image_files):
            # Validate image
            try:
                validation = validate_training_image(image_file)
            except ImageValidationError as e:
                raise ImageValidationError(f"Image {idx + 1} ({image_file.name}): {str(e)}")

            if not validation['valid']:
                error_msg = f"Image {idx + 1} ({image_file.name}): " + "; ".join(validation['errors'])
                raise ImageValidationError(error_msg)

            # Collect warnings
            if validation['warnings']:
                for warning in validation['warnings']:
                    all_warnings.append(f"Image {idx + 1}: {warning}")

            # Reset file pointer
            image_file.seek(0)

            # Create CharacterTrainingImage record
            training_image = CharacterTrainingImage(
                character_model=character,
                image=image_file,
                original_filename=image_file.name,
                file_size=validation['file_size'],
                width=validation['width'],
                height=validation['height'],
                order=idx,
                is_valid=True,
                validation_notes="\n".join(validation['warnings']) if validation['warnings'] else ""
            )
            training_image.save()
            saved_images.append(training_image)

            logger.info(f"✅ Saved training image {idx + 1}/{len(image_files)}: {image_file.name}")

        # Update character with image count
        character.training_images_count = len(saved_images)
        character.save(update_fields=['training_images_count', 'updated_at'])

    return saved_images, all_warnings


def create_training_zip(character: CharacterModel) -> str:
    """
    Create a ZIP file of training images

    Args:
        character: CharacterModel with uploaded training images

    Returns:
        Path to created ZIP file

    Raises:
        TrainingWorkflowError: If ZIP creation fails
    """

    training_images = character.training_images.filter(is_valid=True).order_by('order')

    if training_images.count() < MIN_IMAGES:
        raise TrainingWorkflowError(
            f"Not enough valid images: {training_images.count()} (minimum: {MIN_IMAGES})"
        )

    # Create ZIP in memory first
    zip_buffer = BytesIO()

    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, training_image in enumerate(training_images):
                # Read image file
                training_image.image.seek(0)
                image_data = training_image.image.read()

                # Get file extension
                ext = Path(training_image.original_filename).suffix
                if not ext:
                    ext = '.jpg'

                # Add to ZIP with numbered filename
                zip_filename = f"image_{idx + 1:03d}{ext}"
                zip_file.writestr(zip_filename, image_data)

                logger.info(f"📦 Added to ZIP: {zip_filename}")

        # Save ZIP file
        zip_buffer.seek(0)

        # Create directory if it doesn't exist
        zip_dir = os.path.join(settings.MEDIA_ROOT, 'character_training', 'zips')
        os.makedirs(zip_dir, exist_ok=True)

        # Generate filename
        zip_filename = f"character_{character.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(zip_dir, zip_filename)

        # Write to disk
        with open(zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())

        # Update character with ZIP path
        relative_path = os.path.join('character_training', 'zips', zip_filename)
        character.training_zip_path = relative_path
        character.save(update_fields=['training_zip_path', 'updated_at'])

        logger.info(f"✅ Created training ZIP: {zip_path} ({len(list(training_images))} images)")

        return zip_path

    except Exception as e:
        raise TrainingWorkflowError(f"Failed to create training ZIP: {str(e)}")


def get_training_zip_public_url(character: CharacterModel) -> str:
    """
    Get public URL for training ZIP file

    For development: Returns Django media URL
    For production: Would return CDN/S3 URL

    Args:
        character: CharacterModel with training_zip_path

    Returns:
        Public URL to ZIP file
    """

    if not character.training_zip_path:
        raise TrainingWorkflowError("No training ZIP file found")

    # For development: Use Django media URL
    # In production, you'd upload to S3/CDN and return that URL
    media_url = settings.MEDIA_URL.rstrip('/')
    zip_url = f"{media_url}/{character.training_zip_path}"

    # If running on localhost, need full URL for Replicate
    if 'localhost' in settings.ALLOWED_HOSTS or '127.0.0.1' in settings.ALLOWED_HOSTS:
        # You'll need to use ngrok or similar for local development
        logger.warning(
            "⚠️  Running on localhost - Replicate needs public URL. "
            "Consider using ngrok or uploading ZIP to S3."
        )

    return zip_url


def submit_training_job(
    character: CharacterModel,
    destination: Optional[str] = None
) -> Dict[str, Any]:
    """
    Submit training job to Replicate

    Args:
        character: CharacterModel with training data ready
        destination: Optional Replicate destination (username/model-name)

    Returns:
        Dict with training results

    Raises:
        TrainingWorkflowError: If submission fails
    """

    # Validate character has training data
    if character.training_images_count < MIN_IMAGES:
        raise TrainingWorkflowError(
            f"Not enough training images: {character.training_images_count} (minimum: {MIN_IMAGES})"
        )

    if not character.training_zip_path:
        raise TrainingWorkflowError("Training ZIP not created yet")

    # Get public URL for ZIP
    try:
        zip_url = get_training_zip_public_url(character)

        # Store URL in character
        character.training_zip_url = zip_url
        character.save(update_fields=['training_zip_url', 'updated_at'])

    except Exception as e:
        raise TrainingWorkflowError(f"Failed to get public URL: {str(e)}")

    # Get Replicate provider
    provider = get_replicate_provider()

    if not provider.available:
        raise TrainingWorkflowError("Replicate API not available")

    # Submit training
    try:
        logger.info(f"📤 Submitting training job for character: {character.name}")
        logger.info(f"   Trigger word: {character.trigger_word}")
        logger.info(f"   Images: {character.training_images_count}")
        logger.info(f"   Steps: {character.training_steps}")
        logger.info(f"   Learning rate: {character.learning_rate}")

        result = provider.train_character(
            training_zip_url=zip_url,
            trigger_word=character.trigger_word,
            steps=character.training_steps,
            learning_rate=character.learning_rate,
            destination=destination
        )

        if not result.success:
            raise TrainingWorkflowError(f"Training submission failed: {result.error_message}")

        # Update character with training info
        with transaction.atomic():
            character.training_id = result.training_id
            character.training_status = 'pending'  # Replicate status: starting → processing
            character.training_progress = 0
            character.training_started_at = timezone.now()
            character.error_message = ""
            character.save(update_fields=[
                'training_id',
                'training_status',
                'training_progress',
                'training_started_at',
                'error_message',
                'updated_at'
            ])

        logger.info(f"✅ Training submitted! ID: {result.training_id}")
        logger.info(f"   Estimated time: {result.estimated_time_minutes} minutes")

        return {
            'success': True,
            'training_id': result.training_id,
            'status': result.status,
            'estimated_time_minutes': result.estimated_time_minutes,
            'message': f"Training started! Estimated time: {result.estimated_time_minutes} minutes"
        }

    except Exception as e:
        # Update character with error
        character.training_status = 'failed'
        character.error_message = str(e)
        character.save(update_fields=['training_status', 'error_message', 'updated_at'])

        raise TrainingWorkflowError(f"Failed to submit training: {str(e)}")


def update_training_status(character: CharacterModel) -> Dict[str, Any]:
    """
    Check and update training status

    Args:
        character: CharacterModel with training_id

    Returns:
        Dict with current status and progress
    """

    if not character.training_id:
        return {
            'success': False,
            'error': 'No training ID found'
        }

    provider = get_replicate_provider()

    if not provider.available:
        return {
            'success': False,
            'error': 'Replicate API not available'
        }

    try:
        # Check status with Replicate
        status_result = provider.check_training_status(character.training_id)

        if not status_result.get('success'):
            return status_result

        # Map Replicate status to our status
        replicate_status = status_result['status']
        status_mapping = {
            'starting': 'pending',
            'processing': 'training',
            'succeeded': 'completed',
            'failed': 'failed',
            'canceled': 'cancelled'
        }

        new_status = status_mapping.get(replicate_status, 'pending')
        progress = status_result.get('progress', 0)

        # Update character
        with transaction.atomic():
            character.training_status = new_status
            character.training_progress = progress

            # If completed, extract model info
            if new_status == 'completed':
                character.training_completed_at = timezone.now()

                # Calculate duration
                if character.training_started_at:
                    duration = (character.training_completed_at - character.training_started_at).total_seconds()
                    character.training_duration_seconds = int(duration)

                # Extract model version if available
                if status_result.get('model_version'):
                    character.replicate_version_id = status_result['model_version']

                logger.info(f"🎉 Training completed for character: {character.name}")
                logger.info(f"   Model version: {character.replicate_version_id}")

            # If failed, store error
            elif new_status == 'failed':
                character.error_message = status_result.get('error', 'Training failed')
                logger.error(f"❌ Training failed for character {character.name}: {character.error_message}")

            character.save()

        return {
            'success': True,
            'status': new_status,
            'progress': progress,
            'replicate_status': replicate_status,
            'training_id': character.training_id,
            'model_version': character.replicate_version_id if new_status == 'completed' else None
        }

    except Exception as e:
        logger.error(f"Failed to update training status: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def create_character_workflow(
    user,
    name: str,
    description: str,
    trigger_word: str,
    image_files: List[UploadedFile],
    training_steps: int = 1000,
    learning_rate: float = 0.0004,
    auto_submit: bool = False
) -> Tuple[CharacterModel, List[str]]:
    """
    Complete workflow: Create character, upload images, optionally submit training

    Args:
        user: User creating the character
        name: Character name
        description: Character description
        trigger_word: Trigger word for prompts
        image_files: List of training images
        training_steps: Number of training steps
        learning_rate: Learning rate
        auto_submit: If True, automatically submit training

    Returns:
        Tuple of (character, warnings)
    """

    logger.info(f"📝 Creating character: {name} (trigger: {trigger_word})")

    # Create character
    character = CharacterModel.objects.create(
        user=user,
        name=name,
        description=description,
        trigger_word=trigger_word,
        training_steps=training_steps,
        learning_rate=learning_rate,
        training_status='preparing'
    )

    # Process images
    try:
        saved_images, warnings = process_training_images(character, image_files)
        logger.info(f"✅ Processed {len(saved_images)} training images")

        # Create ZIP
        zip_path = create_training_zip(character)
        logger.info(f"✅ Created training ZIP: {zip_path}")

        # Auto-submit if requested
        if auto_submit:
            submit_result = submit_training_job(character)
            logger.info(f"✅ Training submitted: {submit_result['training_id']}")

        return character, warnings

    except (ImageValidationError, TrainingWorkflowError) as e:
        # Clean up character if workflow fails
        character.delete()
        raise
