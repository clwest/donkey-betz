"""
Dream Execution Signals
=======================

Session 766: Signal handlers for dream approval and execution.

When a dream's decision_outcome changes to 'approved', this signal
triggers the DreamExecutionPipeline to:
1. Create a PartnershipProject from the dream
2. Generate a CustomWorkflow
3. Execute via the Orchestration Layer

This closes Dead End #1 from the DATA_FLOW_DEAD_ENDS.md audit.
"""

import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(pre_save, sender='core.AgentDream')
def track_dream_approval_change(sender, instance, **kwargs):
    """
    Track when a dream's decision_outcome changes to 'approved'.

    We use pre_save to detect the change by comparing the current
    value with what's in the database.
    """
    if instance.pk:
        try:
            # Get the old value from database
            old_instance = sender.objects.get(pk=instance.pk)
            instance._was_approved = (
                old_instance.decision_outcome != 'approved' and
                instance.decision_outcome == 'approved'
            )
        except sender.DoesNotExist:
            instance._was_approved = False
    else:
        # New instance - check if created as approved
        instance._was_approved = instance.decision_outcome == 'approved'


@receiver(post_save, sender='core.AgentDream')
def trigger_dream_execution_on_approval(sender, instance, created, **kwargs):
    """
    Trigger dream execution when a dream is approved.

    This handler fires after the dream is saved and:
    1. Session 862: Creates an Initiative from the dream (content flow bridge)
    2. Queues the dream for execution via Celery task
    """
    # Check if this save resulted in a new approval
    was_approved = getattr(instance, '_was_approved', False)

    if was_approved:
        logger.info(
            f"💭 [DREAM SIGNAL] Dream approved: {instance.title[:50]} (ID: {instance.id})"
        )

        # Session 862: Create Initiative from approved Dream
        # This establishes the content flow: Dream → Initiative → Stages → Deliverable
        try:
            initiative = instance.promote_to_initiative(approved_by='boardroom')
            logger.info(
                f"💭 [DREAM SIGNAL] Created Initiative {initiative.id} from Dream {instance.id}"
            )
        except Exception as e:
            logger.error(
                f"💭 [DREAM SIGNAL] Failed to create Initiative from Dream {instance.id}: {e}"
            )
            # Continue with execution even if Initiative creation fails

        # Check if already has a project (already executed)
        if instance.project_id:
            logger.info(
                f"💭 [DREAM SIGNAL] Dream already has project, skipping: {instance.project_id}"
            )
            return

        # Queue for async execution via Celery
        try:
            from core.tasks import execute_single_dream
            execute_single_dream.delay(str(instance.id))
            logger.info(
                f"💭 [DREAM SIGNAL] Queued dream for execution: {instance.id}"
            )
        except Exception as e:
            logger.error(
                f"💭 [DREAM SIGNAL] Failed to queue dream {instance.id}: {e}"
            )


def connect_dream_signals():
    """
    Connect dream signals.

    Called during app ready() to ensure signals are registered.
    The @receiver decorators handle registration, but this function
    ensures the module is imported.
    """
    logger.info("💭 Dream execution signals connected")


# For explicit connection during tests or reloads
__all__ = [
    'track_dream_approval_change',
    'trigger_dream_execution_on_approval',
    'connect_dream_signals',
]
