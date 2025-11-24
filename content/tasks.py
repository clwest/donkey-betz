"""
Content Tasks - Celery background tasks for content operations
Session 175: Character training status polling

Handles:
- Automatic polling of Replicate training status
- Updates database when training completes
- Runs every 30 seconds for pending/training jobs
"""

import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def poll_pending_trainings(self):
    """
    Poll all pending/training character models and update their status.

    This task runs periodically (via Celery Beat) to ensure training status
    is updated even if the user closes their browser during training.

    Session 175: Fixes the issue where trainings complete but database isn't updated
    """
    from content.models import CharacterModel
    from content.character_training import update_training_status

    try:
        # Find all trainings that are pending or in progress
        active_trainings = CharacterModel.objects.filter(
            training_status__in=['pending', 'training'],
            training_id__isnull=False
        ).exclude(training_id='')

        if not active_trainings.exists():
            return {
                'success': True,
                'message': 'No active trainings to poll',
                'checked': 0,
                'updated': 0
            }

        checked = 0
        updated = 0
        errors = []

        for character in active_trainings:
            checked += 1
            old_status = character.training_status

            try:
                # Update status from Replicate
                result = update_training_status(character)

                if result.get('success'):
                    # Refresh from DB to get new status
                    character.refresh_from_db()

                    if character.training_status != old_status:
                        updated += 1
                        logger.info(
                            f"✅ Training status updated: {character.name} "
                            f"({old_status} -> {character.training_status})"
                        )

                        # If completed, log the model version
                        if character.training_status == 'completed':
                            logger.info(f"   Model version: {character.replicate_version_id}")
                else:
                    errors.append(f"{character.name}: {result.get('error', 'Unknown error')}")

            except Exception as e:
                errors.append(f"{character.name}: {str(e)}")
                logger.error(f"Error polling training {character.id}: {str(e)}")

        result = {
            'success': True,
            'checked': checked,
            'updated': updated,
            'timestamp': timezone.now().isoformat()
        }

        if errors:
            result['errors'] = errors

        if updated > 0:
            logger.info(f"📊 Training poll complete: {updated}/{checked} trainings updated")

        return result

    except Exception as e:
        logger.error(f"Training poll task failed: {str(e)}")
        raise self.retry(exc=e)


@shared_task
def check_single_training(character_id: int):
    """
    Check training status for a single character.

    Can be called manually or scheduled after training submission.

    Args:
        character_id: ID of the CharacterModel to check
    """
    from content.models import CharacterModel
    from content.character_training import update_training_status

    try:
        character = CharacterModel.objects.get(id=character_id)

        if not character.training_id:
            return {
                'success': False,
                'error': 'No training ID found'
            }

        old_status = character.training_status
        result = update_training_status(character)

        if result.get('success'):
            character.refresh_from_db()

            return {
                'success': True,
                'character_id': character_id,
                'name': character.name,
                'old_status': old_status,
                'new_status': character.training_status,
                'progress': character.training_progress,
                'changed': character.training_status != old_status
            }

        return result

    except CharacterModel.DoesNotExist:
        return {
            'success': False,
            'error': f'Character {character_id} not found'
        }
    except Exception as e:
        logger.error(f"Error checking training {character_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def cleanup_stale_trainings():
    """
    Clean up trainings that have been pending/training for too long.

    If a training has been in pending/training status for more than 3 hours,
    it's likely stuck or failed without proper error reporting.

    Runs once per hour via Celery Beat.
    """
    from content.models import CharacterModel

    try:
        cutoff_time = timezone.now() - timedelta(hours=3)

        stale_trainings = CharacterModel.objects.filter(
            training_status__in=['pending', 'training'],
            training_started_at__lt=cutoff_time
        )

        stale_count = stale_trainings.count()

        if stale_count == 0:
            return {
                'success': True,
                'message': 'No stale trainings found',
                'cleaned': 0
            }

        # Mark as failed with explanation
        for training in stale_trainings:
            # One last check before marking as failed
            from content.character_training import update_training_status
            result = update_training_status(training)

            # If still not completed after fresh check, mark as failed
            training.refresh_from_db()
            if training.training_status in ['pending', 'training']:
                training.training_status = 'failed'
                training.error_message = (
                    f"Training timed out after {(timezone.now() - training.training_started_at).total_seconds() / 3600:.1f} hours. "
                    "Please try again or contact support."
                )
                training.save(update_fields=['training_status', 'error_message', 'updated_at'])
                logger.warning(f"⚠️ Marked stale training as failed: {training.name} (ID: {training.id})")

        return {
            'success': True,
            'cleaned': stale_count,
            'message': f'Cleaned up {stale_count} stale trainings'
        }

    except Exception as e:
        logger.error(f"Stale training cleanup failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
