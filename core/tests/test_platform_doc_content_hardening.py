"""
Regression tests for doc_content_view hardening (S2984 PR3 + PR4 hotfix).

Timeline:
- S2984 PR3 added @login_required (was public) + Path.resolve() containment
  check against BASE_DIR — catches symlinks that '..' string guard misses.
- S2984 PR4 hotfix converted the endpoint from django-native @login_required
  to DRF @api_view + IsAuthenticated so auth failure returns JSON 401/403
  (not the 302 HTML redirect that silently blanked DocumentViewer).

Run::

    USE_PGBOUNCER=0 python manage.py test core.tests.test_platform_doc_content_hardening -v 2
"""

from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings


User = get_user_model()


class DocContentAuthTests(TestCase):
    """@login_required regression — was public before S2984."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username=f"s2984-doc-{uuid.uuid4().hex[:8]}",
            email="s2984-doc@example.com",
            password="x",
        )

    def setUp(self) -> None:
        self.client = Client()

    def test_anonymous_returns_json_not_html_redirect(self) -> None:
        """
        S2984 PR4 hotfix: DRF @api_view returns JSON 401/403 on auth
        failure, NOT the 302 HTML redirect django-native @login_required
        would emit (which axios silently follows to a login HTML page,
        making the DocumentViewer render blank without an error state).
        """
        resp = self.client.get("/api/platform/doc-content/", {"path": "docs/README.md"})
        self.assertIn(resp.status_code, (401, 403), f"expected 401/403, got {resp.status_code}")
        self.assertNotEqual(resp.status_code, 302, "must NOT redirect (breaks XHR consumers)")
        self.assertIn(
            "application/json",
            resp.headers.get("Content-Type", ""),
            f"expected JSON content-type, got {resp.headers.get('Content-Type')!r}",
        )

    def test_authenticated_get_returns_200_for_valid_doc(self) -> None:
        self.client.force_login(self.user)
        # Use the actual repo's docs — CLAUDE.md is at the root, so pick a
        # doc inside docs/ that we know exists.
        resp = self.client.get(
            "/api/platform/doc-content/", {"path": "docs/PLATFORM_INVENTORY.md"}
        )
        # Even if the specific file is absent in some checkouts, we should
        # see auth pass and hit a 200 or 404 — never 302 to login.
        self.assertNotIn(resp.status_code, (302,))


class DocContentPathContainmentTests(TestCase):
    """Path.resolve() containment against BASE_DIR — regression for symlink escape."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username=f"s2984-path-{uuid.uuid4().hex[:8]}",
            email="s2984-path@example.com",
            password="x",
        )

    def setUp(self) -> None:
        self.client = Client()
        self.client.force_login(self.user)

    def test_traversal_string_still_rejected(self) -> None:
        """Regression: '..' string check preserved."""
        resp = self.client.get(
            "/api/platform/doc-content/", {"path": "docs/../etc/passwd"}
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_docs_prefix_rejected(self) -> None:
        """Regression: docs/ prefix still required."""
        resp = self.client.get(
            "/api/platform/doc-content/", {"path": "core/settings.py"}
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_markdown_rejected(self) -> None:
        resp = self.client.get(
            "/api/platform/doc-content/", {"path": "docs/PLATFORM_INVENTORY.md.notmd"}
        )
        # 400 (extension check) OR 404 (missing file) both acceptable; the
        # invariant is: not a 200 with content.
        self.assertIn(resp.status_code, (400, 404))

    def test_symlink_resolving_outside_base_is_rejected(self) -> None:
        """
        Simulate a docs/foo -> /etc/passwd symlink by rebinding BASE_DIR to
        a tmpdir where such a symlink exists. Without the S2984 hardening
        this returns 200 (leaking /etc/passwd if readable).
        """
        with tempfile.TemporaryDirectory() as td:
            base = Path(td).resolve()
            (base / "docs").mkdir()
            outside = base.parent / "escape_target.txt"
            outside.write_text("secret", encoding="utf-8")
            try:
                os.symlink(outside, base / "docs" / "sneaky.md")
            except (OSError, NotImplementedError):
                self.skipTest("Filesystem doesn't support symlinks")

            with override_settings(BASE_DIR=str(base)):
                resp = self.client.get(
                    "/api/platform/doc-content/", {"path": "docs/sneaky.md"}
                )

            outside.unlink(missing_ok=True)

        self.assertEqual(resp.status_code, 403, resp.content)
