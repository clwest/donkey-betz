"""
Tests for the Research Arcs Scanner + endpoint (Session 2984 / PR3).

Spec provenance:
- ENGINEERING SPEC — Workspace Home v1 PR3 (Repo Research Arcs +
  In-App Doc Viewer links) deliverable `be68f1d1-1c88-4d72-a908-e57f6ce310dc`
- Initiative `1b9ef2c4-1d7f-4dec-89f4-a4f5a3f38746`

Run::

    USE_PGBOUNCER=0 python manage.py test core.tests.test_research_arcs_scanner -v 2

The pgbouncer note from S2983 tests applies here.
"""

from __future__ import annotations

import os
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from core.services import research_arcs_scanner as scanner


User = get_user_model()


class _ArcFixture:
    """Small helper: build an arc folder tree under a tempdir root."""

    def __init__(self, root: Path):
        self.root = root

    def add_arc(self, slug: str, files: dict[str, str]) -> Path:
        arc = self.root / slug
        arc.mkdir(parents=True, exist_ok=True)
        for name, body in files.items():
            (arc / name).write_text(body, encoding="utf-8")
        return arc

    def touch(self, path: Path, mtime_dt: datetime) -> None:
        os.utime(path, (mtime_dt.timestamp(), mtime_dt.timestamp()))


def _no_git(*_args, **_kwargs) -> None:
    """Force scanner into mtime-fallback mode for deterministic tests."""
    return None


class ResearchArcsScannerTests(TestCase):
    """Pure-Python scanner behavior (no git required — mtime fallback path)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        # Simulate a repo layout: <tmp>/docs/research/domains/<arc>
        self.repo_root = Path(self._tmp.name)
        self.arcs_root = self.repo_root / "docs" / "research" / "domains"
        self.arcs_root.mkdir(parents=True)
        self.fx = _ArcFixture(self.arcs_root)
        # Frozen "now" so days_since is deterministic.
        self.now = datetime(2026, 7, 26, 12, 0, 0, tzinfo=timezone.utc)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_empty_root_returns_empty_arcs(self) -> None:
        with patch.object(scanner, "_git_last_touched", side_effect=_no_git):
            payload = scanner.scan_research_arcs(self.arcs_root, now=self.now)
        self.assertEqual(payload["arcs"], [])
        self.assertEqual(payload["active_days"], 14)
        self.assertEqual(payload["stale_days"], 60)

    def test_missing_root_returns_empty_arcs(self) -> None:
        payload = scanner.scan_research_arcs(self.arcs_root / "nope", now=self.now)
        self.assertEqual(payload["arcs"], [])

    def test_active_status_when_recent(self) -> None:
        arc = self.fx.add_arc(
            "recent_active",
            {
                "1099_recent_active_canonical_summary.md": "# summary\nno hangers.",
                "1000_recent_active_scoping.md": "content",
            },
        )
        # Touch files 3 days ago — well inside ACTIVE_DAYS=14.
        recent = self.now - timedelta(days=3)
        for md in arc.rglob("*.md"):
            self.fx.touch(md, recent)

        with patch.object(scanner, "_git_last_touched", side_effect=_no_git):
            payload = scanner.scan_research_arcs(self.arcs_root, now=self.now)

        self.assertEqual(len(payload["arcs"]), 1)
        arc_row = payload["arcs"][0]
        self.assertEqual(arc_row["arc_id"], "recent_active")
        self.assertEqual(arc_row["title"], "recent_active")  # spec: title=slug
        self.assertEqual(arc_row["path"], "docs/research/domains/recent_active")
        self.assertEqual(arc_row["status"], "active")
        self.assertLessEqual(arc_row["days_since_touched"], 4)
        self.assertTrue(arc_row["signals"]["has_canonical_summary"])
        self.assertEqual(arc_row["signals"]["open_questions_markers"], 0)

    def test_done_status_requires_canonical_and_zero_open_qs_and_not_stale(self) -> None:
        arc = self.fx.add_arc(
            "medium_done",
            {
                "2099_medium_done_canonical_summary.md": "# clean summary — nothing outstanding.",
            },
        )
        # 30 days = past ACTIVE (14) but under STALE (60).
        older = self.now - timedelta(days=30)
        for md in arc.rglob("*.md"):
            self.fx.touch(md, older)

        with patch.object(scanner, "_git_last_touched", side_effect=_no_git):
            payload = scanner.scan_research_arcs(self.arcs_root, now=self.now)

        self.assertEqual(payload["arcs"][0]["status"], "done")

    def test_hanging_status_when_open_questions_hit(self) -> None:
        arc = self.fx.add_arc(
            "medium_hanging",
            {
                "2099_medium_hanging_canonical_summary.md": "# summary\nSome TODO items remain.",
                "2001_medium_hanging_audit.md": "Body TBD later.",
            },
        )
        older = self.now - timedelta(days=30)
        for md in arc.rglob("*.md"):
            self.fx.touch(md, older)

        with patch.object(scanner, "_git_last_touched", side_effect=_no_git):
            payload = scanner.scan_research_arcs(self.arcs_root, now=self.now)

        self.assertEqual(payload["arcs"][0]["status"], "hanging")
        self.assertGreaterEqual(payload["arcs"][0]["signals"]["open_questions_markers"], 2)
        self.assertGreaterEqual(payload["arcs"][0]["signals"]["todo_hits"], 2)

    def test_stale_status_when_older_than_stale_days(self) -> None:
        arc = self.fx.add_arc(
            "old_stale",
            {"1099_old_stale_canonical_summary.md": "# clean"},
        )
        very_old = self.now - timedelta(days=200)
        for md in arc.rglob("*.md"):
            self.fx.touch(md, very_old)

        with patch.object(scanner, "_git_last_touched", side_effect=_no_git):
            payload = scanner.scan_research_arcs(self.arcs_root, now=self.now)

        self.assertEqual(payload["arcs"][0]["status"], "stale")

    def test_stale_status_when_last_touched_is_unknown(self) -> None:
        # Arc folder exists but has no .md files (nothing to mtime).
        self.fx.add_arc("no_docs", {})

        with patch.object(scanner, "_git_last_touched", side_effect=_no_git):
            payload = scanner.scan_research_arcs(self.arcs_root, now=self.now)

        arc_row = payload["arcs"][0]
        self.assertEqual(arc_row["status"], "stale")
        self.assertIsNone(arc_row["last_touched_at"])
        self.assertIsNone(arc_row["days_since_touched"])

    def test_entrypoint_precedence_canonical_readme_openqs_fallback(self) -> None:
        arc = self.fx.add_arc(
            "full_entrypoints",
            {
                "1099_full_entrypoints_canonical_summary.md": "# canonical",
                "README.md": "index",
                "OPEN_QUESTIONS.md": "open qs",
                "9999_random.md": "extra",
            },
        )
        for md in arc.rglob("*.md"):
            self.fx.touch(md, self.now - timedelta(days=1))

        with patch.object(scanner, "_git_last_touched", side_effect=_no_git):
            payload = scanner.scan_research_arcs(self.arcs_root, now=self.now)

        labels = [e["label"] for e in payload["arcs"][0]["entrypoints"]]
        self.assertEqual(labels[:3], ["Canonical summary", "Index", "Open questions"])
        # Fallback NOT emitted when at least one preferred entry hit.
        self.assertNotIn("Latest doc", labels)

    def test_entrypoint_fallback_when_no_preferred_files(self) -> None:
        arc = self.fx.add_arc(
            "fallback_only",
            {
                "1001_fallback_only_audit.md": "content",
                "1002_fallback_only_other.md": "content",
            },
        )
        # 1002 is newer.
        self.fx.touch(arc / "1001_fallback_only_audit.md", self.now - timedelta(days=5))
        self.fx.touch(arc / "1002_fallback_only_other.md", self.now - timedelta(days=1))

        with patch.object(scanner, "_git_last_touched", side_effect=_no_git):
            payload = scanner.scan_research_arcs(self.arcs_root, now=self.now)

        entries = payload["arcs"][0]["entrypoints"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["label"], "Latest doc")
        self.assertEqual(
            entries[0]["path"],
            "docs/research/domains/fallback_only/1002_fallback_only_other.md",
        )

    def test_arcs_sorted_deterministically_by_arc_id(self) -> None:
        for slug in ["zeta", "alpha", "mike"]:
            self.fx.add_arc(slug, {"1099_x_canonical_summary.md": "x"})
        with patch.object(scanner, "_git_last_touched", side_effect=_no_git):
            payload = scanner.scan_research_arcs(self.arcs_root, now=self.now)
        self.assertEqual([a["arc_id"] for a in payload["arcs"]], ["alpha", "mike", "zeta"])

    def test_git_mode_used_when_available(self) -> None:
        arc = self.fx.add_arc("git_mode", {"1099_git_mode_canonical_summary.md": "x"})
        # File is 100 days stale on disk, but git says 5 days ago -> "active".
        very_old = self.now - timedelta(days=100)
        for md in arc.rglob("*.md"):
            self.fx.touch(md, very_old)
        recent_iso = (self.now - timedelta(days=5)).isoformat()

        with patch.object(scanner, "_git_last_touched", return_value=recent_iso):
            payload = scanner.scan_research_arcs(self.arcs_root, now=self.now)

        self.assertEqual(payload["arcs"][0]["status"], "active")
        self.assertEqual(payload["arcs"][0]["last_touched_at"], recent_iso)


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class ResearchArcsEndpointTests(TestCase):
    """Endpoint smoke: auth + shape + 200/401."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username=f"s2984-user-{uuid.uuid4().hex[:8]}",
            email="s2984@example.com",
            password="x",
        )

    def setUp(self) -> None:
        cache.clear()
        self.client = APIClient()

    def test_requires_authentication(self) -> None:
        url = reverse("repo-research-arcs")
        resp = self.client.get(url)
        # DRF default returns 403 for anonymous with SessionAuth; 401 also valid.
        self.assertIn(resp.status_code, (401, 403))

    def test_returns_shape_for_real_repo(self) -> None:
        """Live scan against the real docs/research/domains — should return
        the same shape as the fixture tests."""
        self.client.force_authenticate(user=self.user)
        url = reverse("repo-research-arcs")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()

        self.assertIn("generated_at", body)
        self.assertIn("arcs", body)
        self.assertEqual(body["active_days"], 14)
        self.assertEqual(body["stale_days"], 60)
        self.assertIsInstance(body["arcs"], list)
        if body["arcs"]:
            first = body["arcs"][0]
            self.assertIn("arc_id", first)
            self.assertIn("title", first)
            self.assertIn("status", first)
            self.assertIn("entrypoints", first)
            self.assertIn("signals", first)
            self.assertIn(first["status"], {"active", "hanging", "done", "stale"})

    def test_response_cached_by_ttl(self) -> None:
        """Second call within TTL hits cache — scanner not re-invoked."""
        self.client.force_authenticate(user=self.user)
        url = reverse("repo-research-arcs")

        with patch(
            "core.views_repo_research.scan_research_arcs",
            return_value={
                "generated_at": "2026-01-01T00:00:00+00:00",
                "root": "x",
                "active_days": 14,
                "stale_days": 60,
                "arcs": [],
            },
        ) as mocked:
            r1 = self.client.get(url)
            r2 = self.client.get(url)

        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(mocked.call_count, 1)
