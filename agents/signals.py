"""
Agent Contribution Signals
Session 120: Auto-track agent contributions when content is created

This module contains Django signal handlers that automatically create
AgentContribution records when agents create images or videos.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from content.models import ImageHistory, VideoHistory
from agents.models import AgentContribution
from agents.services import AgentContributionService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ImageHistory)
def track_image_contribution(sender, instance, created, **kwargs):
    """
    Auto-track agent contribution when image is created.

    This runs after every ImageHistory.save() call. If the image has:
    - An agent assigned
    - A project assigned
    - Was just created (not updated)

    Then we automatically create an AgentContribution record.
    """
    # Only track on creation, not updates
    if not created:
        return

    # Must have both agent and project to track
    if not instance.agent or not instance.project:
        return

    try:
        service = AgentContributionService()

        # Determine contribution type based on image type
        contribution_type = 'generation'
        if instance.image_type in ['edited', 'enhanced']:
            contribution_type = 'editing'
        elif instance.image_type == 'upscaled':
            contribution_type = 'editing'
        elif instance.image_type == 'inpainted':
            contribution_type = 'editing'

        # Track the contribution
        service.track_image_contribution(
            agent=instance.agent,
            project=instance.project,
            image=instance,
            contribution_type=contribution_type,
            contribution_role='Primary Creator',
            contribution_percentage=100,
            task_description=f"Generated {instance.image_type} image using {instance.model_used}",
            execution_time_seconds=None,  # Not tracked yet
            tokens_used=None  # Not tracked yet
        )

        logger.info(
            f"✓ Auto-tracked image contribution: {instance.agent.display_name} → "
            f"Image #{instance.get_sequential_number()} in {instance.project.name}"
        )

    except Exception as e:
        # Don't fail image creation if tracking fails
        logger.error(f"Error auto-tracking image contribution: {e}")


@receiver(post_save, sender=VideoHistory)
def track_video_contribution(sender, instance, created, **kwargs):
    """
    Auto-track agent contribution when video is created.

    This runs after every VideoHistory.save() call. If the video has:
    - An agent assigned
    - A project assigned
    - Was just created (not updated)

    Then we automatically create an AgentContribution record.
    """
    # Only track on creation, not updates
    if not created:
        return

    # Must have both agent and project to track
    if not instance.agent or not instance.project:
        return

    try:
        service = AgentContributionService()

        # Determine contribution type based on video type
        contribution_type = 'generation'
        if instance.video_type in ['edited', 'enhanced']:
            contribution_type = 'editing'
        elif instance.video_type == 'extended':
            contribution_type = 'editing'

        # Track the contribution
        service.track_video_contribution(
            agent=instance.agent,
            project=instance.project,
            video=instance,
            contribution_type=contribution_type,
            contribution_role='Primary Creator',
            contribution_percentage=100,
            task_description=f"Generated {instance.video_type} video",
            execution_time_seconds=None,  # Not tracked yet
            tokens_used=None  # Not tracked yet
        )

        logger.info(
            f"✓ Auto-tracked video contribution: {instance.agent.display_name} → "
            f"Video #{instance.get_sequential_number()} in {instance.project.name}"
        )

    except Exception as e:
        # Don't fail video creation if tracking fails
        logger.error(f"Error auto-tracking video contribution: {e}")
