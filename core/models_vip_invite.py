"""
VIP Invite model — magic-link tokens for onboarding demo viewers.

Each invite creates a one-time-use token that recipients exchange for a
read-only VIP account with an auto-expiry.
"""

import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models.base import UnifiedBaseModel


def _default_token():
    return secrets.token_urlsafe(32)


def _default_token_expires():
    return timezone.now() + timedelta(hours=72)


def _default_account_expires():
    return timezone.now() + timedelta(days=14)


class VIPInvite(UnifiedBaseModel):
    """A magic-link invite for VIP demo viewers."""

    token = models.CharField(max_length=64, unique=True, default=_default_token)
    label = models.CharField(
        max_length=120,
        blank=True,
        help_text="Internal note, e.g. 'Austin demo Mar-2026'",
    )

    # Who created it
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vip_invites_created',
    )

    # Workspace + personalization scoping
    workspace = models.ForeignKey(
        'core.ProjectWorkspace',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='vip_invites',
        help_text="Workspace to scope the VIP view to",
    )
    prospect_profile = models.ForeignKey(
        'core.Deliverable',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='vip_invites',
        help_text="Prospect profile deliverable for personalization",
    )
    recipient_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Display name for the invitee (e.g. 'Matthew Berman')",
    )

    # Lifecycle
    token_expires_at = models.DateTimeField(default=_default_token_expires)
    account_expires_at = models.DateTimeField(default=_default_account_expires)

    # Redemption
    redeemed_at = models.DateTimeField(null=True, blank=True)
    redeemed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='vip_invite_used',
    )

    # Revocation
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']

    def __str__(self):
        status = 'revoked' if self.revoked_at else ('used' if self.redeemed_at else 'pending')
        return f"VIPInvite({self.label or 'unlabelled'}, {status})"

    @property
    def is_valid(self):
        """Token is usable: not revoked, not redeemed, not expired."""
        now = timezone.now()
        return (
            self.revoked_at is None
            and self.redeemed_at is None
            and self.token_expires_at > now
        )
