"""
VIP Magic Link Exchange — Regression Tests

Ensures the VIP exchange endpoint stays publicly accessible through
the auth middleware and works end-to-end.

Initiative: 14ef9a24 (VIP Magic Link Hardening & Regression Suite)
"""

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from core.models_vip_invite import VIPInvite


@pytest.fixture
def anon_client():
    """Unauthenticated API client — simulates a VIP user with no session/token."""
    return APIClient()


@pytest.fixture
def admin_client(admin_user):
    """Authenticated admin client for creating invites."""
    client = APIClient()
    client.login(username='admin', password='admin123')
    return client


@pytest.fixture
def admin_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user, _ = User.objects.get_or_create(
        username='admin',
        defaults={'is_staff': True, 'is_superuser': True},
    )
    user.set_password('admin123')
    user.save()
    return user


@pytest.fixture
def valid_invite(admin_user, db):
    """Create a valid VIP invite for testing."""
    return VIPInvite.objects.create(
        created_by=admin_user,
        label='Test invite',
    )


# ── Test 1: Middleware doesn't block exchange endpoint ─────────────────────

@pytest.mark.django_db
class TestVIPExchangePublicAccess:
    """Verify the exchange endpoint passes through the auth middleware."""

    def test_exchange_not_blocked_by_middleware(self, anon_client):
        """POST to exchange without auth should reach the DRF view (not middleware 401)."""
        response = anon_client.post(
            '/api/v1/vip-invites/exchange/',
            {},
            format='json',
        )
        # Should get 400 "Token is required" from the VIEW, not 401 from middleware
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
        assert data['error'] == 'Token is required.'
        # NOT the middleware response:
        assert data.get('error', {}) != {'code': 'authentication_required'}

    def test_exchange_with_invalid_token_returns_404(self, anon_client):
        """Invalid token should return 404 from the view."""
        response = anon_client.post(
            '/api/v1/vip-invites/exchange/',
            {'token': 'totally-fake-token-that-does-not-exist'},
            format='json',
        )
        assert response.status_code == 404
        assert response.json()['error'] == 'Invalid or expired invite.'


# ── Test 2: Full end-to-end exchange ───────────────────────────────────────

@pytest.mark.django_db
class TestVIPExchangeEndToEnd:
    """Verify the complete invite → exchange → API key flow."""

    def test_valid_exchange_returns_api_key(self, anon_client, valid_invite):
        """Exchange a valid invite token and get an API key back."""
        response = anon_client.post(
            '/api/v1/vip-invites/exchange/',
            {'token': valid_invite.token},
            format='json',
        )
        assert response.status_code == 200
        data = response.json()
        assert 'api_key' in data
        assert len(data['api_key']) == 40  # DRF token length
        assert 'username' in data
        assert data['username'].startswith('vip_')
        assert data['role'] == 'vip_demo_viewer'
        assert 'expires_at' in data

    def test_exchange_marks_invite_redeemed(self, anon_client, valid_invite):
        """After exchange, the invite should be marked as redeemed."""
        anon_client.post(
            '/api/v1/vip-invites/exchange/',
            {'token': valid_invite.token},
            format='json',
        )
        valid_invite.refresh_from_db()
        assert valid_invite.redeemed_at is not None
        assert valid_invite.redeemed_by is not None

    def test_redeemed_invite_cannot_be_exchanged_again(self, anon_client, valid_invite):
        """A redeemed invite should not be exchangeable a second time."""
        # First exchange
        resp1 = anon_client.post(
            '/api/v1/vip-invites/exchange/',
            {'token': valid_invite.token},
            format='json',
        )
        assert resp1.status_code == 200

        # Second exchange should fail
        resp2 = anon_client.post(
            '/api/v1/vip-invites/exchange/',
            {'token': valid_invite.token},
            format='json',
        )
        assert resp2.status_code == 410  # Gone


# ── Test 3: Non-public endpoints still require auth ────────────────────────

@pytest.mark.django_db
class TestNonPublicEndpointsStillProtected:
    """Verify that the PUBLIC_PATHS fix didn't weaken auth globally."""

    def test_vip_create_requires_auth(self, anon_client):
        """Creating an invite should require admin auth."""
        response = anon_client.post(
            '/api/v1/vip-invites/create/',
            {'label': 'should fail'},
            format='json',
        )
        # Should be blocked by middleware (401) or DRF (403)
        assert response.status_code in (401, 403)

    def test_vip_list_requires_auth(self, anon_client):
        """Listing invites should require admin auth."""
        response = anon_client.get('/api/v1/vip-invites/')
        assert response.status_code in (401, 403)

    def test_pa_chat_requires_auth(self, anon_client):
        """PA chat endpoint should require auth."""
        response = anon_client.post(
            '/api/pa/chat/',
            {'message': 'test'},
            format='json',
        )
        assert response.status_code in (401, 403)


# ── Test 4: PUBLIC_PATHS registry check ────────────────────────────────────

@pytest.mark.django_db
class TestPublicPathsRegistry:
    """Verify critical public paths are in the middleware allowlist."""

    def test_vip_exchange_in_public_paths(self):
        """VIP exchange must be in PUBLIC_PATHS to prevent auth middleware blocking."""
        from core.auth_middleware import UnifiedTokenAuthenticationMiddleware
        public_paths = UnifiedTokenAuthenticationMiddleware.PUBLIC_PATHS
        assert '/api/v1/vip-invites/exchange/' in public_paths

    def test_review_portal_in_public_paths(self):
        """Review portal must be accessible for magic link users."""
        from core.auth_middleware import UnifiedTokenAuthenticationMiddleware
        public_paths = UnifiedTokenAuthenticationMiddleware.PUBLIC_PATHS
        assert '/api/review/' in public_paths

    def test_health_in_public_paths(self):
        """Health check must always be public."""
        from core.auth_middleware import UnifiedTokenAuthenticationMiddleware
        public_paths = UnifiedTokenAuthenticationMiddleware.PUBLIC_PATHS
        assert '/api/v1/health/' in public_paths
