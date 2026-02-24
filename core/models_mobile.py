"""
Mobile-specific models — push tokens, device registration, etc.
"""

from django.conf import settings
from django.db import models


class MobilePushToken(models.Model):
    """Expo push token registered per user/device."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_tokens',
    )
    token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(
        max_length=10,
        choices=[('ios', 'iOS'), ('android', 'Android')],
    )
    device_name = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_mobile_push_token'
        ordering = ['-last_seen_at']

    def __str__(self):
        return f'{self.user} — {self.platform} — {self.token[:20]}...'
