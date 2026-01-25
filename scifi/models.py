# scifi/models.py
"""
AgentMood model with automatic mood_expires_at handling.

When a new AgentMood is created and mood_expires_at is None, the save()
override ensures mood_expires_at is set to created_at (or now) plus
SCIFI_MOOD_TTL_DAYS (default 30 days).
"""

from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.db import models
from django.utils import timezone


def _get_mood_ttl_days() -> int:
    """
    Returns configured TTL days for moods. Defaults to 30 when not set.
    """
    return int(getattr(settings, "SCIFI_MOOD_TTL_DAYS", 30))


class AgentMood(models.Model):
    """
    Represents an agent mood entry.

    Fields:
    - mood: short descriptor of the mood
    - created_at: timestamp the row was created (timezone-aware)
    - mood_expires_at: when this mood should expire; can be NULL for older rows,
      but new rows will have this set automatically if not provided.
    """

    mood = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    mood_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"AgentMood({self.mood}, expires={self.mood_expires_at})"

    def save(self, *args, **kwargs):
        """
        Ensure that on creation, if mood_expires_at is None, it will be set to
        created_at (or now) + SCIFI_MOOD_TTL_DAYS.

        We set created_at explicitly if it's falsy to guarantee a timezone-aware
        timestamp to base the expiry calculation on.
        """
        ttl_days = _get_mood_ttl_days()

        # If created_at is not set (falsy), set it to now to calculate expiry.
        if not self.created_at:
            self.created_at = timezone.now()

        # Only set expiry automatically for new instances (no pk) and when
        # mood_expires_at is not explicitly provided.
        if self.pk is None and self.mood_expires_at is None:
            # Use created_at (already ensured to be set) as base.
            self.mood_expires_at = self.created_at + timedelta(days=ttl_days)

        super().save(*args, **kwargs)