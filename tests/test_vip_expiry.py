"""T-VIP-1 — VIP account expiry enforcement + backstop cleanup task.

Ratifies ADR-0005 §3.5 F-C-VIP-1 risk-gate:
- Middleware denies (401) VIP requests when account_expires_at ≤ now or revoked.
- Nightly Celery task deactivates expired VIP users as backstop.
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.utils import timezone

from core.models_vip_invite import VIPInvite
from core.vip_middleware import VIPReadOnlyMiddleware


User = get_user_model()


def _make_vip_user(username: str, is_active: bool = True):
    user = User.objects.create_user(username=username, is_active=is_active)
    from core.models import EnhancedUserProfile
    profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)
    profile.primary_role = 'vip_demo_viewer'
    profile.save(update_fields=['primary_role'])
    # Bust any cached reverse-OneToOne descriptor set by post_save signals
    # during create_user (e.g. auto-profile creation with empty primary_role).
    return User.objects.get(pk=user.pk)


def _make_admin(username: str):
    return User.objects.create_user(username=username, is_staff=True)


@pytest.fixture
def middleware():
    return VIPReadOnlyMiddleware(get_response=lambda req: _PassThrough())


class _PassThrough:
    status_code = 200


@pytest.fixture
def factory():
    return RequestFactory()


# ── Middleware enforcement ────────────────────────────────────────────────

@pytest.mark.django_db
class TestVIPExpiryMiddleware:

    def test_unexpired_vip_passes(self, middleware, factory):
        admin = _make_admin('admin_ok')
        vip = _make_vip_user('vip_ok')
        VIPInvite.objects.create(
            created_by=admin,
            redeemed_by=vip,
            redeemed_at=timezone.now() - timedelta(days=1),
            account_expires_at=timezone.now() + timedelta(days=5),
        )
        request = factory.get('/api/deliverables/')
        request.user = vip
        response = middleware(request)
        assert response.status_code == 200

    def test_expired_vip_gets_401(self, middleware, factory):
        admin = _make_admin('admin_exp')
        vip = _make_vip_user('vip_exp')
        VIPInvite.objects.create(
            created_by=admin,
            redeemed_by=vip,
            redeemed_at=timezone.now() - timedelta(days=20),
            account_expires_at=timezone.now() - timedelta(hours=1),
        )
        request = factory.get('/api/deliverables/')
        request.user = vip
        response = middleware(request)
        assert response.status_code == 401
        assert b'expired' in response.content
        assert response['X-VIP-Expired'] == 'true'

    def test_revoked_vip_gets_401(self, middleware, factory):
        admin = _make_admin('admin_rev')
        vip = _make_vip_user('vip_rev')
        VIPInvite.objects.create(
            created_by=admin,
            redeemed_by=vip,
            redeemed_at=timezone.now() - timedelta(days=1),
            account_expires_at=timezone.now() + timedelta(days=10),
            revoked_at=timezone.now(),
        )
        request = factory.get('/api/deliverables/')
        request.user = vip
        response = middleware(request)
        assert response.status_code == 401
        assert response['X-VIP-Expired'] == 'true'

    def test_vip_without_invite_row_denied(self, middleware, factory):
        vip = _make_vip_user('vip_orphan')
        request = factory.get('/api/deliverables/')
        request.user = vip
        response = middleware(request)
        assert response.status_code == 401
        assert response['X-VIP-Expired'] == 'true'

    def test_non_vip_user_untouched_by_expiry_check(self, middleware, factory):
        regular = User.objects.create_user(username='regular')
        request = factory.get('/api/deliverables/')
        request.user = regular
        response = middleware(request)
        assert response.status_code == 200

    def test_most_recent_invite_wins(self, middleware, factory):
        """When a user has multiple invite rows, the most recent controls."""
        admin = _make_admin('admin_multi')
        vip = _make_vip_user('vip_multi')
        VIPInvite.objects.create(
            created_by=admin,
            redeemed_by=vip,
            redeemed_at=timezone.now() - timedelta(days=30),
            account_expires_at=timezone.now() - timedelta(days=16),
        )
        VIPInvite.objects.create(
            created_by=admin,
            redeemed_by=vip,
            redeemed_at=timezone.now() - timedelta(days=2),
            account_expires_at=timezone.now() + timedelta(days=12),
        )
        request = factory.get('/api/deliverables/')
        request.user = vip
        response = middleware(request)
        assert response.status_code == 200


# ── Cleanup task ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCleanupExpiredVIPUsers:

    def test_deactivates_expired_active_user(self):
        from core.tasks_vip import cleanup_expired_vip_users
        admin = _make_admin('admin_c1')
        vip = _make_vip_user('vip_c1', is_active=True)
        VIPInvite.objects.create(
            created_by=admin,
            redeemed_by=vip,
            redeemed_at=timezone.now() - timedelta(days=20),
            account_expires_at=timezone.now() - timedelta(hours=1),
        )
        result = cleanup_expired_vip_users()
        vip.refresh_from_db()
        assert vip.is_active is False
        assert result['deactivated'] == 1

    def test_skips_unexpired_user(self):
        from core.tasks_vip import cleanup_expired_vip_users
        admin = _make_admin('admin_c2')
        vip = _make_vip_user('vip_c2', is_active=True)
        VIPInvite.objects.create(
            created_by=admin,
            redeemed_by=vip,
            redeemed_at=timezone.now() - timedelta(days=1),
            account_expires_at=timezone.now() + timedelta(days=5),
        )
        result = cleanup_expired_vip_users()
        vip.refresh_from_db()
        assert vip.is_active is True
        assert result['deactivated'] == 0

    def test_idempotent_on_already_inactive(self):
        from core.tasks_vip import cleanup_expired_vip_users
        admin = _make_admin('admin_c3')
        vip = _make_vip_user('vip_c3', is_active=False)
        VIPInvite.objects.create(
            created_by=admin,
            redeemed_by=vip,
            redeemed_at=timezone.now() - timedelta(days=20),
            account_expires_at=timezone.now() - timedelta(hours=1),
        )
        result = cleanup_expired_vip_users()
        assert result['deactivated'] == 0
