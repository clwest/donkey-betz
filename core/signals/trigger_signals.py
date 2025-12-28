"""
Situation Trigger Signal Handlers - Session 477 (Part 2)

These signals hook into SpiderData creation and evaluate triggers in real-time.
When a trigger matches, it fires immediately instead of waiting for scheduled runs.

Flow:
1. Spider collects data → SpiderData.post_save fires
2. Signal handler queries all active triggers
3. Each trigger evaluates against the new data
4. Matching triggers create TriggerEvent records
5. Celery task is queued for immediate alert generation
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

logger = logging.getLogger(__name__)


def evaluate_triggers_for_spider_data(spider_data):
    """
    Evaluate all active triggers against new spider data.

    This is the core function that makes the system event-driven.
    Called from the post_save signal on SpiderData.
    """
    from core.models_situation_triggers import SituationTrigger

    # Get all active triggers
    triggers = SituationTrigger.objects.filter(is_active=True).order_by('-priority')

    events_created = []

    for trigger in triggers:
        try:
            # Evaluate the trigger
            matches, matched_value = trigger.evaluate(spider_data)

            if matches:
                # Fire the trigger
                event = trigger.fire(spider_data, matched_value)
                events_created.append(event)

                logger.info(
                    f"Trigger fired: {trigger.name} | "
                    f"Spider: {spider_data.spider_name} | "
                    f"Value: {matched_value}"
                )

        except Exception as e:
            logger.error(f"Error evaluating trigger {trigger.name}: {e}")
            continue

    # Queue immediate alert generation for fired triggers
    if events_created:
        try:
            from core.tasks import process_trigger_events
            # Queue with slight delay to allow transaction to commit
            process_trigger_events.apply_async(
                args=[[str(e.id) for e in events_created]],
                countdown=2  # 2 second delay
            )
        except Exception as e:
            logger.error(f"Failed to queue trigger event processing: {e}")

    return events_created


@receiver(post_save, sender='core.SpiderData')
def on_spider_data_created(sender, instance, created, **kwargs):
    """
    Signal handler for SpiderData creation.

    Only fires on new records (created=True) to avoid
    duplicate processing on updates.
    """
    if not created:
        return

    # Skip if no raw data
    if not instance.raw_data:
        return

    # Run trigger evaluation in a separate transaction
    # to avoid blocking the spider data save
    try:
        transaction.on_commit(
            lambda: evaluate_triggers_for_spider_data(instance)
        )
    except Exception as e:
        logger.error(f"Failed to schedule trigger evaluation: {e}")


def connect_trigger_signals():
    """
    Explicitly connect signals. Called from apps.py ready().

    This ensures signals are connected even if the module
    isn't imported elsewhere.
    """
    # The @receiver decorator handles connection, but this
    # function can be called to ensure the module is loaded
    logger.info("Situation trigger signals connected")


# =============================================================================
# Manual Trigger Evaluation (for testing or backfill)
# =============================================================================

def evaluate_triggers_batch(spider_data_queryset, dry_run=False):
    """
    Evaluate triggers against a batch of spider data.

    Useful for:
    - Testing trigger configurations
    - Backfilling triggers on historical data
    - Manual trigger evaluation

    Args:
        spider_data_queryset: QuerySet of SpiderData to evaluate
        dry_run: If True, don't create events or fire alerts

    Returns:
        List of (spider_data, trigger, matched_value) tuples that matched
    """
    from core.models_situation_triggers import SituationTrigger

    triggers = SituationTrigger.objects.filter(is_active=True).order_by('-priority')
    matches = []

    for spider_data in spider_data_queryset:
        for trigger in triggers:
            try:
                matched, value = trigger.evaluate(spider_data)
                if matched:
                    matches.append((spider_data, trigger, value))

                    if not dry_run:
                        # Fire the trigger
                        trigger.fire(spider_data, value)

            except Exception as e:
                logger.error(f"Error in batch evaluation: {e}")
                continue

    return matches
