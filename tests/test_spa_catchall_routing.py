"""
Regression tests for SPA catch-all routing bug.

Bug: Django APPEND_SLASH caused /vite.svg -> 301 /vite.svg/ and the
catch-all regex previously allowed file-like paths (ending with .ext or
.ext/) to be served index.html instead of returning 404.

Fix: Negative lookahead in the catch-all URL pattern now excludes paths
that end with a file extension (e.g. .svg, .js, .png) with or without a
trailing slash. All regex groups are non-capturing so react_app view
(which only accepts `request`) does not receive unexpected positional args.
"""

import pytest
from django.test import Client
from django.test.utils import override_settings


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestSPACatchAllRouting:
    """Regression tests for SPA catch-all file-extension exclusion."""

    # ------------------------------------------------------------------
    # Static asset paths must NOT be served as HTML (404 expected)
    # ------------------------------------------------------------------

    @override_settings(APPEND_SLASH=True)
    def test_vite_svg_returns_404(self, client):
        """GET /vite.svg must not be caught by the SPA catch-all."""
        response = client.get("/vite.svg")
        assert response.status_code == 404, (
            f"Expected 404 for /vite.svg, got {response.status_code}"
        )

    @override_settings(APPEND_SLASH=True)
    def test_vite_svg_trailing_slash_returns_404(self, client):
        """GET /vite.svg/ must not be caught by the SPA catch-all."""
        response = client.get("/vite.svg/")
        assert response.status_code == 404, (
            f"Expected 404 for /vite.svg/, got {response.status_code}"
        )

    @override_settings(APPEND_SLASH=True)
    def test_js_asset_not_served_as_html(self, client):
        """Generic .js asset path must not be served as text/html."""
        response = client.get("/assets/main.js")
        assert response.status_code != 200 or "text/html" not in response.get("Content-Type", ""), (
            "Static asset path /assets/main.js should not return text/html"
        )

    @override_settings(APPEND_SLASH=True)
    def test_png_asset_not_served_as_html(self, client):
        """Generic .png asset path must not be served as text/html."""
        response = client.get("/images/logo.png")
        assert response.status_code != 200 or "text/html" not in response.get("Content-Type", ""), (
            "Static asset path /images/logo.png should not return text/html"
        )

    # ------------------------------------------------------------------
    # SPA application routes MUST be served as HTML (200 expected)
    # ------------------------------------------------------------------

    @override_settings(APPEND_SLASH=True)
    def test_vip_accept_returns_html(self, client):
        """GET /vip/accept must be served by the SPA catch-all as text/html."""
        response = client.get("/vip/accept")
        assert response.status_code == 200, (
            f"Expected 200 for /vip/accept, got {response.status_code}"
        )
        content_type = response.get("Content-Type", "")
        assert "text/html" in content_type, (
            f"/vip/accept should return text/html, got Content-Type: {content_type}"
        )

    @override_settings(APPEND_SLASH=True)
    def test_ai_studio_returns_html(self, client):
        """GET /ai-studio/ must be served by the SPA catch-all as text/html."""
        response = client.get("/ai-studio/")
        assert response.status_code == 200, (
            f"Expected 200 for /ai-studio/, got {response.status_code}"
        )
        content_type = response.get("Content-Type", "")
        assert "text/html" in content_type, (
            f"/ai-studio/ should return text/html, got Content-Type: {content_type}"
        )

    @override_settings(APPEND_SLASH=True)
    def test_spa_html_contains_doctype(self, client):
        """SPA responses should contain a valid HTML document."""
        response = client.get("/ai-studio/")
        if response.status_code == 200:
            content = response.content.decode("utf-8", errors="replace")
            assert "<!DOCTYPE html" in content or "<html" in content, (
                "SPA response for /ai-studio/ does not contain an HTML document"
            )

    # ------------------------------------------------------------------
    # Ensure APPEND_SLASH redirect for SVG does not cascade to text/html
    # ------------------------------------------------------------------

    @override_settings(APPEND_SLASH=True)
    def test_vite_svg_redirect_not_text_html(self, client):
        """
        Even if /vite.svg returns a redirect (301), following it must not
        land on a 200 text/html SPA page.
        """
        response = client.get("/vite.svg", follow=True)
        if response.status_code == 200:
            content_type = response.get("Content-Type", "")
            assert "text/html" not in content_type, (
                "/vite.svg (after redirects) returned text/html — "
                "SPA catch-all is incorrectly matching file extensions"
            )

    @override_settings(APPEND_SLASH=True)
    def test_vite_svg_slash_redirect_not_text_html(self, client):
        """
        GET /vite.svg/ must not resolve to the SPA index page even after
        following any redirects.
        """
        response = client.get("/vite.svg/", follow=True)
        if response.status_code == 200:
            content_type = response.get("Content-Type", "")
            assert "text/html" not in content_type, (
                "/vite.svg/ (after redirects) returned text/html — "
                "SPA catch-all is incorrectly matching extension+slash paths"
            )
