"""
ML Celery Tasks - Session 24
Automated model retraining tasks using evaluated predictions
"""

import logging
from celery import shared_task
from typing import Dict, Any

logger = logging.getLogger(__name__)


@shared_task(name='ml.check_retraining_needed')
def check_retraining_needed():
    """
    Check all sports to see if retraining needed
    Runs daily at 3 AM

    Returns:
        dict: Status of retraining check for each sport
    """
    from ml.training.model_retrainer import ModelRetrainer

    logger.info("🔍 Checking if model retraining needed...")

    retrainer = ModelRetrainer()
    sports = ['nfl', 'nba', 'mlb', 'nhl']
    results = {}

    for sport in sports:
        try:
            should_retrain, reason = retrainer.should_retrain(sport)
            results[sport] = {
                'should_retrain': should_retrain,
                'reason': reason
            }

            if should_retrain:
                logger.info(f"🚀 Triggering retraining for {sport.upper()}: {reason}")
                # Trigger async retraining
                retrain_sport_model.delay(sport)
            else:
                logger.info(f"✅ {sport.upper()} model OK: {reason}")

        except Exception as e:
            logger.error(f"❌ Error checking {sport.upper()}: {e}")
            results[sport] = {
                'should_retrain': False,
                'reason': f'Error: {str(e)}'
            }

    logger.info(f"✅ Retraining check complete: {sum(1 for r in results.values() if r['should_retrain'])} sports queued")

    return results


@shared_task(name='ml.retrain_sport_model', bind=True)
def retrain_sport_model(self, sport_type: str, force: bool = False) -> Dict[str, Any]:
    """
    Retrain model for specific sport

    Args:
        sport_type: 'nfl', 'nba', 'mlb', or 'nhl'
        force: Force retraining even if criteria not met

    Returns:
        dict: Retraining result with status and metrics
    """
    from ml.training.model_retrainer import ModelRetrainer

    logger.info(f"🏋️ Starting model retraining for {sport_type.upper()}")

    try:
        retrainer = ModelRetrainer()
        result = retrainer.retrain_model(sport_type, force=force)

        if result['success']:
            if result['deployed']:
                logger.info(f"✅ {sport_type.upper()} model v{result['version']} deployed: {result['message']}")
            else:
                logger.warning(f"⚠️ {sport_type.upper()} model v{result['version']} trained but not deployed: {result['message']}")
        else:
            logger.error(f"❌ {sport_type.upper()} retraining failed: {result['message']}")

        return result

    except Exception as e:
        logger.error(f"❌ Exception during {sport_type.upper()} retraining: {e}", exc_info=True)
        return {
            'sport_type': sport_type,
            'success': False,
            'message': f'Exception: {str(e)}',
            'metrics': {},
            'version': None,
            'deployed': False
        }


@shared_task(name='ml.retrain_all_models')
def retrain_all_models(force: bool = False) -> Dict[str, Any]:
    """
    Retrain all sport models
    Runs weekly on Sunday at 2 AM

    Args:
        force: Force retraining even if criteria not met

    Returns:
        dict: Results for all sports
    """
    logger.info("🏋️ Starting weekly model retraining for all sports")

    sports = ['nfl', 'nba', 'mlb', 'nhl']
    results = {}

    for sport in sports:
        try:
            logger.info(f"Processing {sport.upper()}...")
            result = retrain_sport_model(sport, force=force)
            results[sport] = result
        except Exception as e:
            logger.error(f"❌ Error retraining {sport.upper()}: {e}")
            results[sport] = {
                'success': False,
                'message': f'Error: {str(e)}'
            }

    # Summary
    successful = sum(1 for r in results.values() if r.get('success', False))
    deployed = sum(1 for r in results.values() if r.get('deployed', False))

    logger.info(f"✅ Weekly retraining complete: {successful}/{len(sports)} successful, {deployed} deployed")

    return {
        'total_sports': len(sports),
        'successful': successful,
        'deployed': deployed,
        'results': results
    }


@shared_task(name='ml.cleanup_old_model_files')
def cleanup_old_model_files(keep_versions: int = 5):
    """
    Clean up old model files (keep only recent versions)

    Args:
        keep_versions: Number of versions to keep per sport

    Returns:
        dict: Cleanup statistics
    """
    import os
    from ml.models import MLModelVersion

    logger.info(f"🧹 Cleaning up old model files (keeping {keep_versions} versions per sport)")

    sports = ['nfl', 'nba', 'mlb', 'nhl']
    deleted_count = 0
    kept_count = 0

    for sport in sports:
        try:
            # Get all versions for this sport
            versions = MLModelVersion.objects.filter(
                sport_type=sport
            ).order_by('-version')

            # Keep the most recent N versions
            versions_to_keep = list(versions[:keep_versions])
            versions_to_delete = list(versions[keep_versions:])

            for version in versions_to_delete:
                # Delete model file
                if version.model_file_path and os.path.exists(version.model_file_path):
                    os.remove(version.model_file_path)
                    logger.info(f"Deleted {version.model_file_path}")
                    deleted_count += 1

                # Delete scaler file if exists
                scaler_path = version.training_metadata.get('scaler_path')
                if scaler_path and os.path.exists(scaler_path):
                    os.remove(scaler_path)
                    logger.info(f"Deleted {scaler_path}")

                # Delete database record
                version.delete()

            kept_count += len(versions_to_keep)
            logger.info(f"✅ {sport.upper()}: kept {len(versions_to_keep)}, deleted {len(versions_to_delete)}")

        except Exception as e:
            logger.error(f"❌ Error cleaning up {sport.upper()}: {e}")

    logger.info(f"✅ Cleanup complete: deleted {deleted_count} files, kept {kept_count} versions")

    return {
        'deleted_files': deleted_count,
        'kept_versions': kept_count,
        'keep_versions': keep_versions
    }


@shared_task(name='ml.get_model_stats')
def get_model_stats() -> Dict[str, Any]:
    """
    Get statistics for all active models

    Returns:
        dict: Model statistics
    """
    from ml.models import MLModelVersion

    logger.info("📊 Gathering model statistics...")

    sports = ['nfl', 'nba', 'mlb', 'nhl']
    stats = {}

    for sport in sports:
        try:
            active_model = MLModelVersion.get_active_model(sport)

            if active_model:
                stats[sport] = {
                    'version': active_model.version,
                    'accuracy': active_model.test_accuracy,
                    'calibration_score': active_model.calibration_score,
                    'trained_date': active_model.trained_date.isoformat(),
                    'deployment_date': active_model.deployment_date.isoformat() if active_model.deployment_date else None,
                    'training_samples': active_model.training_samples,
                    'days_active': active_model.days_active
                }
            else:
                stats[sport] = {
                    'version': None,
                    'message': 'No active model'
                }

        except Exception as e:
            logger.error(f"❌ Error getting stats for {sport.upper()}: {e}")
            stats[sport] = {
                'error': str(e)
            }

    logger.info(f"✅ Model statistics gathered for {len(sports)} sports")

    return stats