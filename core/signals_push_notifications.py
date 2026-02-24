"""
Django signals that trigger mobile push notifications.

Connected in core/apps.py ready() method.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender='core.HumanAttentionItem')
def on_critical_attention_item(sender, instance, created, **kwargs):
    """Trigger push notification when a critical attention item is created."""
    if not created:
        return
    if getattr(instance, 'urgency', None) != 'critical':
        return

    try:
        from core.tasks_push_notifications import notify_critical_attention_item
        notify_critical_attention_item.delay(str(instance.id))
    except Exception as e:
        logger.error('[PushSignal] Failed to queue critical attention push: %s', e)


@receiver(post_save, sender='core.ExtractedArtifact')
def on_artifact_needs_classification(sender, instance, created, **kwargs):
    """Trigger push notification when an unclassified artifact is created."""
    if not created:
        return
    # Only notify for unclassified artifacts
    if getattr(instance, 'classified', True):
        return

    try:
        from core.tasks_push_notifications import notify_needs_classification
        notify_needs_classification.delay(str(instance.id))
    except Exception as e:
        logger.error('[PushSignal] Failed to queue classification push: %s', e)
