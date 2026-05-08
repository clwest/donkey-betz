"""
Smoke tests for the mounted broken-route fallbacks (Session 1110, PR
fix/mounted-broken-route-fallbacks).

Each route below was previously raising 500 because the legacy Django
template it called via `render(...)` no longer exists. The fix replaces
the broken renders with either a redirect to the React SPA equivalent or
an inline HTML fallback that preserves the original status semantics.

These tests assert non-500 + the expected fallback shape. They use
`SimpleTestCase` so they don't require DB access; the share-token paths
are exercised via `view_shared_project` directly with a mocked queryset
so we don't depend on `content_creativeproject` rows existing in test DB.
"""

from unittest.mock import patch

from django.test import Client, SimpleTestCase


class MountedRouteFallbackTests(SimpleTestCase):
    """No-DB smoke checks: each previously-broken Django route returns non-500."""

    def setUp(self):
        self.client = Client()

    # --- /visualization/ -------------------------------------------------
    def test_visualization_redirects_to_neural_orchestra(self):
        response = self.client.get('/visualization/')
        # Was 500 (TemplateDoesNotExist: visualization.html). Now redirects.
        self.assertNotEqual(response.status_code, 500)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/neural-orchestra')

    # --- /ai-building-products/ -----------------------------------------
    def test_ai_building_products_redirects_to_agents(self):
        response = self.client.get('/ai-building-products/')
        # Was 500 (TemplateDoesNotExist: ai_building_products_with_agents.html).
        self.assertNotEqual(response.status_code, 500)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/agents')

    # --- /nexus/ and /intelligence/ -------------------------------------
    # The unified_intelligence_dashboard view is decorated with @login_required
    # (preserved from the original implementation for security). Unauthenticated
    # callers therefore get a 302 to the login URL; authenticated callers get
    # the React SPA shell. Either way, the previous 500-on-TemplateDoesNotExist
    # is gone.
    def test_nexus_does_not_500(self):
        response = self.client.get('/nexus/')
        self.assertNotEqual(response.status_code, 500)
        # Either login redirect (unauthenticated) or SPA shell (authenticated).
        self.assertIn(response.status_code, (200, 302))

    def test_intelligence_does_not_500(self):
        response = self.client.get('/intelligence/')
        self.assertNotEqual(response.status_code, 500)
        self.assertIn(response.status_code, (200, 302))

    # --- /share/<token>/ -------------------------------------------------
    def test_share_token_not_found_returns_404_html_fallback(self):
        # ProjectShare.DoesNotExist branch → 404 with inline HTML body.
        from content.models import ProjectShare
        with patch.object(
            ProjectShare.objects, 'select_related', return_value=ProjectShare.objects
        ), patch.object(
            ProjectShare.objects, 'get', side_effect=ProjectShare.DoesNotExist,
        ):
            response = self.client.get('/share/nonexistent-token-abc123/')
        self.assertNotEqual(response.status_code, 500)
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Share not found', response.content)

    def test_share_token_unexpected_error_returns_500_with_fallback_body(self):
        # Generic Exception branch → preserves 500 status but returns a
        # rendered fallback (not a Django TemplateDoesNotExist crash).
        from content.models import ProjectShare
        with patch.object(
            ProjectShare.objects, 'select_related', return_value=ProjectShare.objects
        ), patch.object(
            ProjectShare.objects, 'get', side_effect=RuntimeError('boom'),
        ):
            response = self.client.get('/share/error-token-abc123/')
        self.assertEqual(response.status_code, 500)
        # The key assertion: it's our fallback HTML, not a Django debug page
        # or a TemplateDoesNotExist trace.
        self.assertIn(b'Something went wrong', response.content)
        self.assertNotIn(b'TemplateDoesNotExist', response.content)
