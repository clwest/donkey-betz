"""
Session 1039: Tenant / Organization model for multi-tenant customer access.

Phase 1 of 3 — foundation model only.  No enforcement logic or new API
endpoints yet; those come in Phases 2 and 3.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Tenant(models.Model):
    """
    An organization / billing entity that groups users and tracks spend.

    Every paying customer gets one Tenant row.  Internal (platform-admin)
    users may have tenant=NULL on their UnifiedUser record.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_tenants',
    )

    subscription_tier = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free Tier'),
            ('pro', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='free',
    )

    # --- cost guardrails ------------------------------------------------
    monthly_cost_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=10.00,
        help_text='Hard cap in USD for the current billing period',
    )
    monthly_cost_used = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )
    cost_period_start = models.DateTimeField(default=timezone.now)

    # --- feature gates ---------------------------------------------------
    features = models.JSONField(
        default=dict,
        blank=True,
        help_text='e.g. {"max_agents": 5, "daily_tasks": 50}',
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.subscription_tier})"
