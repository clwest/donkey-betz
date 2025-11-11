"""
Character Training API Views
Session 74 Phase 2: Backend endpoints for character training

Provides REST API endpoints for:
- Creating characters
- Uploading training images
- Submitting training jobs
- Checking training status
- Managing trained characters
"""

import logging
from typing import List

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import UploadedFile

from content.models import CharacterModel, CharacterTrainingImage
from content.character_training import (
    create_character_workflow,
    submit_training_job,
    update_training_status,
    ImageValidationError,
    TrainingWorkflowError,
    MIN_IMAGES,
    MAX_IMAGES
)

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def list_characters(request):
    """
    List user's trained characters

    GET /api/characters/

    Returns:
        JSON list of characters with status
    """
    try:
        characters = CharacterModel.objects.filter(user=request.user).order_by('-created_at')

        character_list = []
        for char in characters:
            character_list.append({
                'id': char.id,
                'name': char.name,
                'description': char.description,
                'trigger_word': char.trigger_word,
                'training_status': char.training_status,
                'training_progress': char.training_progress,
                'training_images_count': char.training_images_count,
                'generations_count': char.generations_count,
                'is_favorite': char.is_favorite,
                'thumbnail': char.thumbnail.url if char.thumbnail else None,
                'created_at': char.created_at.isoformat(),
                'last_used_at': char.last_used_at.isoformat() if char.last_used_at else None,
                'can_generate': char.training_status == 'completed' and bool(char.replicate_version_id)
            })

        return JsonResponse({
            'success': True,
            'characters': character_list,
            'count': len(character_list)
        })

    except Exception as e:
        logger.error(f"Failed to list characters: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_character(request, character_id):
    """
    Get detailed character information

    GET /api/characters/<id>/

    Returns:
        JSON with character details and training images
    """
    try:
        character = CharacterModel.objects.get(id=character_id, user=request.user)

        # Get training images
        training_images = character.training_images.order_by('order')
        images_data = []
        for img in training_images:
            images_data.append({
                'id': img.id,
                'url': img.image.url,
                'filename': img.original_filename,
                'width': img.width,
                'height': img.height,
                'order': img.order,
                'is_valid': img.is_valid,
                'validation_notes': img.validation_notes
            })

        data = {
            'id': character.id,
            'name': character.name,
            'description': character.description,
            'trigger_word': character.trigger_word,
            'training_status': character.training_status,
            'training_progress': character.training_progress,
            'training_id': character.training_id,
            'training_images_count': character.training_images_count,
            'training_images': images_data,
            'training_steps': character.training_steps,
            'learning_rate': character.learning_rate,
            'training_started_at': character.training_started_at.isoformat() if character.training_started_at else None,
            'training_completed_at': character.training_completed_at.isoformat() if character.training_completed_at else None,
            'training_duration_seconds': character.training_duration_seconds,
            'generations_count': character.generations_count,
            'last_used_at': character.last_used_at.isoformat() if character.last_used_at else None,
            'error_message': character.error_message,
            'replicate_version_id': character.replicate_version_id,
            'is_favorite': character.is_favorite,
            'tags': character.tags,
            'thumbnail': character.thumbnail.url if character.thumbnail else None,
            'created_at': character.created_at.isoformat(),
            'updated_at': character.updated_at.isoformat(),
        }

        return JsonResponse({
            'success': True,
            'character': data
        })

    except CharacterModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Character not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Failed to get character: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt  # We'll handle CSRF in the form
@require_http_methods(["POST"])
def create_character(request):
    """
    Create new character with training images

    POST /api/characters/create/

    Form data:
        - name: Character name
        - description: Character description (optional)
        - trigger_word: Trigger word (default: TOK)
        - training_steps: Training steps (default: 1000)
        - learning_rate: Learning rate (default: 0.0004)
        - images: Multiple image files (10-20 images)
        - auto_submit: Whether to auto-submit training (default: false)

    Returns:
        JSON with character data and any warnings
    """
    try:
        # Get form data
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        trigger_word = request.POST.get('trigger_word', 'TOK').strip().upper()
        training_steps = int(request.POST.get('training_steps', 1000))
        learning_rate = float(request.POST.get('learning_rate', 0.0004))
        auto_submit = request.POST.get('auto_submit', 'false').lower() == 'true'

        # Validate required fields
        if not name:
            return JsonResponse({
                'success': False,
                'error': 'Character name is required'
            }, status=400)

        if not trigger_word:
            trigger_word = 'TOK'

        # Get uploaded images
        image_files: List[UploadedFile] = request.FILES.getlist('images')

        if not image_files:
            return JsonResponse({
                'success': False,
                'error': 'No images uploaded'
            }, status=400)

        if len(image_files) < MIN_IMAGES:
            return JsonResponse({
                'success': False,
                'error': f'Not enough images: {len(image_files)} provided (minimum: {MIN_IMAGES})'
            }, status=400)

        if len(image_files) > MAX_IMAGES:
            return JsonResponse({
                'success': False,
                'error': f'Too many images: {len(image_files)} provided (maximum: {MAX_IMAGES})'
            }, status=400)

        logger.info(f"📝 Creating character '{name}' with {len(image_files)} images")

        # Create character with workflow
        character, warnings = create_character_workflow(
            user=request.user,
            name=name,
            description=description,
            trigger_word=trigger_word,
            image_files=image_files,
            training_steps=training_steps,
            learning_rate=learning_rate,
            auto_submit=auto_submit
        )

        logger.info(f"✅ Character created: {character.id}")

        return JsonResponse({
            'success': True,
            'character_id': character.id,
            'name': character.name,
            'trigger_word': character.trigger_word,
            'training_status': character.training_status,
            'training_images_count': character.training_images_count,
            'warnings': warnings,
            'message': 'Character created successfully!' + (
                ' Training started!' if auto_submit else ' Ready to train.'
            )
        })

    except ImageValidationError as e:
        logger.error(f"Image validation error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': 'validation'
        }, status=400)

    except TrainingWorkflowError as e:
        logger.error(f"Training workflow error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': 'workflow'
        }, status=500)

    except Exception as e:
        logger.error(f"Failed to create character: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def submit_training(request, character_id):
    """
    Submit character for training

    POST /api/characters/<id>/submit-training/

    Returns:
        JSON with training job details
    """
    try:
        character = CharacterModel.objects.get(id=character_id, user=request.user)

        # Check if already training or completed
        if character.training_status in ('pending', 'training'):
            return JsonResponse({
                'success': False,
                'error': 'Training already in progress'
            }, status=400)

        if character.training_status == 'completed':
            return JsonResponse({
                'success': False,
                'error': 'Character already trained. Create a new character to retrain.'
            }, status=400)

        logger.info(f"📤 Submitting training for character: {character.name}")

        # Submit training
        result = submit_training_job(character)

        logger.info(f"✅ Training submitted: {result['training_id']}")

        return JsonResponse({
            'success': True,
            'training_id': result['training_id'],
            'status': result['status'],
            'estimated_time_minutes': result['estimated_time_minutes'],
            'message': result['message']
        })

    except CharacterModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Character not found'
        }, status=404)

    except TrainingWorkflowError as e:
        logger.error(f"Training submission error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

    except Exception as e:
        logger.error(f"Failed to submit training: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def check_training_status(request, character_id):
    """
    Check training status and update character

    GET /api/characters/<id>/training-status/

    Returns:
        JSON with current training status and progress
    """
    try:
        character = CharacterModel.objects.get(id=character_id, user=request.user)

        # Update status from Replicate
        status_result = update_training_status(character)

        if not status_result.get('success'):
            return JsonResponse(status_result, status=500)

        # Refresh character from DB to get updated values
        character.refresh_from_db()

        return JsonResponse({
            'success': True,
            'character_id': character.id,
            'name': character.name,
            'training_status': character.training_status,
            'training_progress': character.training_progress,
            'training_id': character.training_id,
            'model_version': character.replicate_version_id,
            'error_message': character.error_message,
            'training_started_at': character.training_started_at.isoformat() if character.training_started_at else None,
            'training_completed_at': character.training_completed_at.isoformat() if character.training_completed_at else None,
            'training_duration_seconds': character.training_duration_seconds,
        })

    except CharacterModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Character not found'
        }, status=404)

    except Exception as e:
        logger.error(f"Failed to check training status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def toggle_favorite(request, character_id):
    """
    Toggle character favorite status

    POST /api/characters/<id>/toggle-favorite/

    Returns:
        JSON with new favorite status
    """
    try:
        character = CharacterModel.objects.get(id=character_id, user=request.user)

        character.is_favorite = not character.is_favorite
        character.save(update_fields=['is_favorite', 'updated_at'])

        return JsonResponse({
            'success': True,
            'character_id': character.id,
            'is_favorite': character.is_favorite
        })

    except CharacterModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Character not found'
        }, status=404)

    except Exception as e:
        logger.error(f"Failed to toggle favorite: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_character(request, character_id):
    """
    Delete a character and all associated data

    DELETE /api/characters/<id>/

    Returns:
        JSON confirmation
    """
    try:
        character = CharacterModel.objects.get(id=character_id, user=request.user)

        # Prevent deletion if training in progress
        if character.training_status in ('pending', 'training'):
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete character while training is in progress'
            }, status=400)

        character_name = character.name
        character.delete()  # Cascade will delete training images

        logger.info(f"🗑️  Deleted character: {character_name}")

        return JsonResponse({
            'success': True,
            'message': f'Character "{character_name}" deleted successfully'
        })

    except CharacterModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Character not found'
        }, status=404)

    except Exception as e:
        logger.error(f"Failed to delete character: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def training_requirements(request):
    """
    Get training requirements and guidelines

    GET /api/characters/requirements/

    Returns:
        JSON with training requirements
    """
    return JsonResponse({
        'success': True,
        'requirements': {
            'min_images': MIN_IMAGES,
            'max_images': MAX_IMAGES,
            'min_resolution': 512,
            'max_resolution': 2048,
            'max_file_size_mb': 10,
            'supported_formats': ['JPEG', 'JPG', 'PNG', 'WEBP'],
            'recommended_count': 12,
            'training_time_minutes': '30-60',
            'guidelines': [
                'Use high-quality, well-lit images',
                'Include variety of angles and poses',
                'Consistent subject across all images',
                'Avoid heavy filters or editing',
                'Images should clearly show the character/logo',
                'Square or near-square aspect ratios work best'
            ]
        }
    })
