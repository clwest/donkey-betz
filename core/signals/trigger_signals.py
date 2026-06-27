"""
Situation Trigger Signal Handlers - Session 477 (Part 2)
Updated: Session 785 - Added Workspace Trigger evaluation

These signals hook into SpiderData creation and evaluate triggers in real-time.
When a trigger matches, it fires immediately instead of waiting for scheduled runs.

Flow:
1. Spider collects data → SpiderData.post_save fires
2. Signal handler queries all active triggers (SituationTrigger + WorkspaceTriggerConfig)
3. Each trigger evaluates against the new data
4. Matching SituationTriggers create TriggerEvent records
5. Matching WorkspaceTriggerConfigs create WorkspaceTrigger records
6. Celery tasks are queued for processing
"""

import logging
import re
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


# =============================================================================
# Session 785: Workspace Trigger Evaluation
# =============================================================================

def evaluate_workspace_triggers_for_spider_data(spider_data):
    """
    Evaluate all active WorkspaceTriggerConfig rules against new spider data.

    When a config matches, a WorkspaceTrigger work item is created.
    The conductor task (workspace_autopilot_tick) will process these.

    Session 785 - Hybrid Workspace Autopilot
    """
    from core.models_skin_layer import WorkspaceTriggerConfig, WorkspaceTrigger
    from django.utils import timezone

    # Get all active configs
    configs = WorkspaceTriggerConfig.objects.filter(is_active=True)

    triggers_created = []

    for config in configs:
        try:
            # Check cooldown
            if config.is_on_cooldown():
                continue

            # Check spider match
            if config.target_spiders and spider_data.spider_name not in config.target_spiders:
                continue

            # Get raw data
            raw_data = spider_data.raw_data or {}

            # Handle 'items' array - check each item
            items = raw_data.get('items', [raw_data])
            if not isinstance(items, list):
                items = [items]

            for item in items:
                # Get the value to check
                value = _get_nested_value(item, config.match_field)
                if value is None:
                    continue

                # Evaluate match
                matches, matched_value = _evaluate_workspace_match(
                    value, config.match_operator, config.match_value
                )

                if matches:
                    # Create trigger work item
                    title = config.trigger_title_template.format(
                        spider_name=spider_data.spider_name,
                        match_field=config.match_field,
                        matched_value=str(matched_value)[:50]
                    )

                    trigger = WorkspaceTrigger.create_from_spider_data(
                        spider_data=spider_data,
                        trigger_type=config.trigger_type,
                        title=title,
                        description=f"Source: {spider_data.spider_name}\nMatched: {matched_value}",
                        target_agent=config.target_agent,
                        target_category=config.target_category,
                        priority=config.priority,
                        ttl_hours=config.ttl_hours,
                        context_data={
                            'spider_data_id': str(spider_data.id),
                            'spider_name': spider_data.spider_name,
                            'matched_value': str(matched_value)[:500],
                            'raw_item': item if len(str(item)) < 2000 else {'title': item.get('title', '')}
                        }
                    )

                    if trigger:  # None if dedupe blocked
                        triggers_created.append(trigger)

                        # Update config stats
                        config.total_triggers_created += 1
                        config.last_triggered_at = timezone.now()
                        config.save(update_fields=['total_triggers_created', 'last_triggered_at'])

                        logger.info(
                            f"Workspace trigger created: {title} | "
                            f"Spider: {spider_data.spider_name} | "
                            f"Config: {config.name}"
                        )

                    # Only one trigger per config per spider data
                    break

        except Exception as e:
            logger.error(f"Error evaluating workspace config {config.name}: {e}")
            continue

    return triggers_created


def _get_nested_value(data: dict, path: str):
    """
    Extract nested value from dict using dot notation.
    e.g., 'items.0.title' gets data['items'][0]['title']
    """
    if not data or not path:
        return None

    keys = path.split('.')
    value = data

    for key in keys:
        if value is None:
            return None
        if isinstance(value, dict):
            value = value.get(key)
        elif isinstance(value, list):
            try:
                idx = int(key)
                value = value[idx] if idx < len(value) else None
            except (ValueError, IndexError):
                return None
        else:
            return None

    return value


def _evaluate_workspace_match(value, operator: str, match_value: str) -> tuple[bool, any]:
    """Evaluate if a value matches the workspace trigger condition."""
    try:
        if operator == 'contains':
            value_str = str(value).lower()
            # Support multiple keywords separated by |
            keywords = [k.strip().lower() for k in match_value.split('|')]
            for kw in keywords:
                if kw in value_str:
                    return True, kw
            return False, None

        elif operator == 'regex':
            value_str = str(value)
            match = re.search(match_value, value_str, re.IGNORECASE)
            if match:
                return True, match.group(0)
            return False, None

        elif operator in ['gt', 'lt']:
            # Numeric comparison
            if isinstance(value, str):
                value = float(value.replace(',', '').replace('$', ''))
            else:
                value = float(value)
            threshold = float(match_value)

            if operator == 'gt' and value > threshold:
                return True, value
            if operator == 'lt' and value < threshold:
                return True, value
            return False, None

    except (ValueError, TypeError, AttributeError):
        pass

    return False, None


@receiver(post_save, sender='core.LegacySpiderData')
def on_spider_data_created(sender, instance, created, **kwargs):
    """
    Signal handler for SpiderData creation.

    Only fires on new records (created=True) to avoid
    duplicate processing on updates.

    Evaluates both:
    - SituationTriggers (alerts)
    - WorkspaceTriggerConfigs (work items)
    """
    if not created:
        return

    # Skip if no raw data
    if not instance.raw_data:
        return

    # Run trigger evaluation in a separate transaction
    # to avoid blocking the spider data save
    try:
        def evaluate_all_triggers():
            # Original situation triggers (alerts)
            evaluate_triggers_for_spider_data(instance)
            # Session 785: Workspace triggers (work items)
            evaluate_workspace_triggers_for_spider_data(instance)

        transaction.on_commit(evaluate_all_triggers)
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
