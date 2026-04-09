"""
Newsletter subscriber model for Operator Edge.
"""
import uuid
from django.db import models


class NewsletterSubscriber(models.Model):
    """Tracks newsletter signups from the Operator Edge landing page."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, default='')
    source = models.CharField(
        max_length=100, default='landing_page',
        help_text='Where the signup came from (landing_page, referral, social, etc.)'
    )
    referral_code = models.CharField(max_length=100, blank=True, default='')
    utm_source = models.CharField(max_length=100, blank=True, default='')
    utm_medium = models.CharField(max_length=100, blank=True, default='')
    utm_campaign = models.CharField(max_length=100, blank=True, default='')
    is_confirmed = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-subscribed_at']

    def __str__(self):
        return f'{self.email} ({self.source})'
