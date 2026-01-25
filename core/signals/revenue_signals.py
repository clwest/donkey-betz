"""
Session 822: Revenue Tracking Signals

Signal handlers to ensure a Revenue record exists whenever an Opportunity
is marked 'accepted'. This fixes the "$0 revenue recorded" audit finding.

Implementation:
- pre_save: caches the previous status to detect transitions
- post_save: creates Revenue record when transitioning to 'accepted'

The implementation is defensive, transactional, idempotent, and logs
actions for observability.
"""

import logging
from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger(__name__)


def connect_revenue_signals():
    """
    Connect revenue tracking signals.
    Called from CoreConfig.ready() to ensure signals are registered.
    """
    # Signals are connected via @receiver decorators below
    # This function exists for explicit registration and logging
    logger.info("Revenue tracking signals connected")


@receiver(pre_save, sender='core.Opportunity', weak=False)
def opportunity_pre_save(sender, instance, **kwargs):
    """
    Cache the previous status of the Opportunity so post_save can detect transitions.
    """
    try:
        if instance.pk:
            # Fetch current state from DB to know what status was before this save
            try:
                prev = sender.objects.only("status").get(pk=instance.pk)
                instance._previous_status = getattr(prev, "status", None)
            except sender.DoesNotExist:
                instance._previous_status = None
        else:
            instance._previous_status = None
    except Exception:
        logger.exception(
            "Failed to fetch previous Opportunity status for pk=%s",
            getattr(instance, "pk", None)
        )
        instance._previous_status = None


@receiver(post_save, sender='core.Opportunity', weak=False)
def opportunity_post_save_create_revenue(sender, instance, created: bool, **kwargs):
    """
    Create a Revenue record when an Opportunity transitions to 'accepted'.

    Behavior:
    - Detects transition by comparing instance._previous_status to current status
    - On transition to 'accepted', creates Revenue if none exists for this Opportunity
    - Uses transaction.atomic for DB consistency
    - Logs all actions and errors
    """
    from core.models_unified_system import Revenue

    try:
        previous_status = getattr(instance, "_previous_status", None)
        current_status = getattr(instance, "status", None)

        # Normalize for safe comparison
        prev_status_str = str(previous_status).lower() if previous_status else None
        curr_status_str = str(current_status).lower() if current_status else None

        transitioned_to_accepted = (prev_status_str != "accepted") and (curr_status_str == "accepted")

        # New instance created with 'accepted' status is also a transition
        if created and curr_status_str == "accepted":
            transitioned_to_accepted = True

        if not transitioned_to_accepted:
            logger.debug(
                "Opportunity (pk=%s) did not transition to 'accepted' "
                "(previous=%s, current=%s). No revenue action.",
                getattr(instance, "pk", None),
                previous_status,
                current_status,
            )
            return

        # Create Revenue if not already present
        with transaction.atomic():
            # Check for existing Revenue linked to this Opportunity
            existing = Revenue.objects.filter(
                source_type='opportunity',
                source_id=str(instance.pk)
            ).exists()

            if existing:
                logger.info(
                    "Revenue creation skipped: existing record for Opportunity pk=%s",
                    instance.pk
                )
                return

            # Get amount from potential_revenue
            amount = getattr(instance, "potential_revenue", Decimal("0.00"))
            if amount is None:
                amount = Decimal("0.00")

            # Create the Revenue record
            revenue = Revenue.objects.create(
                user=instance.user,
                source_type='opportunity',
                source_id=str(instance.pk),
                agent=getattr(instance, 'recommended_by', None),
                amount=amount,
                currency='USD',
                status='pending',
                description=f"Revenue from accepted opportunity: {instance.title}",
                metadata={
                    'opportunity_id': str(instance.pk),
                    'opportunity_title': instance.title,
                    'opportunity_type': instance.opportunity_type,
                    'match_score': instance.match_score,
                    'accepted_at': timezone.now().isoformat(),
                }
            )

            logger.info(
                "Revenue (pk=%s) created for Opportunity pk=%s: $%s",
                revenue.pk,
                instance.pk,
                amount
            )

    except Exception:
        # Log errors but don't interrupt the save flow
        logger.exception(
            "Error creating Revenue for Opportunity pk=%s",
            getattr(instance, "pk", None)
        )
