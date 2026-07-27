"""Session 2995 — staleness detector at ingest (v2 item #4).

Four orthogonal axes now on DocResearchFinding:
- status (lifecycle: open/fixed/dismissed) — S2989
- close_mode (closure mechanism, nullable) — S2991
- finding_type (classification: decision_evidence/executable/unknown) — S2992
- staleness (fresh/suspected) — S2995 (this PR)

Detector extracts `path:line` references via EXECUTABLE_FILE_LINE_RE (reused
from the finding_type classifier) and checks each against the local
filesystem. Bare-filename refs are resolved via a `git ls-files` basename
index built once per invocation. Any failed ref flips the finding to
`suspected`; failed refs land in `metadata['staleness_failed_refs']` so
downstream consumers (v2 item #8) can surface them.

Existing 900 rows default to `fresh` via the schema default (migration
0402). PR (b) will backfill via `--recheck-staleness --apply` in a
data migration.
"""
from __future__ import annotations

import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from core.management.commands.index_doc_research_findings import (
    _build_repo_file_index,
    _check_staleness_at_head,
    _resolve_ref_path,
)
from core.models_audit_findings import DocResearchFinding


class StalenessHelperTests(TestCase):
    """_check_staleness_at_head is deterministic, fail-safe, honors bare refs."""

    def setUp(self):
        # Build a tiny sandbox repo layout for path checks.
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        (self.base / "core").mkdir()
        (self.base / "frontend" / "src").mkdir(parents=True)
        # File with 100 lines.
        (self.base / "core" / "models_x.py").write_text(
            "\n".join(f"line {i}" for i in range(1, 101)) + "\n"
        )
        # File with 5 lines.
        (self.base / "core" / "tiny.py").write_text("a\nb\nc\nd\ne\n")
        # Bare-filename target (only file named `bare_only.py`).
        (self.base / "frontend" / "src" / "bare_only.py").write_text(
            "\n".join(f"row {i}" for i in range(1, 21)) + "\n"
        )
        self.file_index = {
            "models_x.py": {"core/models_x.py"},
            "tiny.py": {"core/tiny.py"},
            "bare_only.py": {"frontend/src/bare_only.py"},
        }

    def test_empty_text_is_fresh(self):
        self.assertEqual(
            _check_staleness_at_head("", self.base, self.file_index),
            (DocResearchFinding.STALENESS_FRESH, []),
        )

    def test_no_refs_at_all_is_fresh(self):
        self.assertEqual(
            _check_staleness_at_head(
                "This finding mentions no code references at all.",
                self.base,
                self.file_index,
            ),
            (DocResearchFinding.STALENESS_FRESH, []),
        )

    def test_existing_path_within_range_is_fresh(self):
        stale, failed = _check_staleness_at_head(
            "See core/models_x.py:42 for context.",
            self.base,
            self.file_index,
        )
        self.assertEqual(stale, DocResearchFinding.STALENESS_FRESH)
        self.assertEqual(failed, [])

    def test_missing_path_is_suspected(self):
        stale, failed = _check_staleness_at_head(
            "Broken ref at core/does_not_exist.py:12 — will fail.",
            self.base,
            self.file_index,
        )
        self.assertEqual(stale, DocResearchFinding.STALENESS_SUSPECTED)
        self.assertEqual(failed, ["core/does_not_exist.py:12"])

    def test_line_out_of_range_is_suspected(self):
        stale, failed = _check_staleness_at_head(
            "tiny file overrun at core/tiny.py:999",
            self.base,
            self.file_index,
        )
        self.assertEqual(stale, DocResearchFinding.STALENESS_SUSPECTED)
        self.assertEqual(failed, ["core/tiny.py:999"])

    def test_bare_filename_resolves_via_index(self):
        # `bare_only.py:5` should resolve to `frontend/src/bare_only.py`
        # via the file_index and check line 5 (well within 20 lines).
        stale, failed = _check_staleness_at_head(
            "Bare ref at bare_only.py:5 should resolve.",
            self.base,
            self.file_index,
        )
        self.assertEqual(stale, DocResearchFinding.STALENESS_FRESH)
        self.assertEqual(failed, [])

    def test_bare_filename_unresolvable_is_suspected(self):
        # No entry in file_index for `phantom.py`.
        stale, failed = _check_staleness_at_head(
            "Phantom bare ref at phantom.py:1",
            self.base,
            self.file_index,
        )
        self.assertEqual(stale, DocResearchFinding.STALENESS_SUSPECTED)
        self.assertEqual(failed, ["phantom.py:1"])

    def test_multi_ref_any_fail_is_suspected(self):
        stale, failed = _check_staleness_at_head(
            "See core/models_x.py:10 AND core/missing.py:5 for context.",
            self.base,
            self.file_index,
        )
        self.assertEqual(stale, DocResearchFinding.STALENESS_SUSPECTED)
        self.assertEqual(failed, ["core/missing.py:5"])

    def test_multi_ref_all_pass_is_fresh(self):
        stale, failed = _check_staleness_at_head(
            "Both core/models_x.py:10 and core/tiny.py:3 are fine.",
            self.base,
            self.file_index,
        )
        self.assertEqual(stale, DocResearchFinding.STALENESS_FRESH)
        self.assertEqual(failed, [])

    def test_backticked_ref_still_detected(self):
        # Corpus routinely wraps refs in backticks — the regex should
        # still match the `path:line` slice inside the backticks.
        stale, failed = _check_staleness_at_head(
            "See `core/models_x.py:1` for the top of file.",
            self.base,
            self.file_index,
        )
        self.assertEqual(stale, DocResearchFinding.STALENESS_FRESH)
        self.assertEqual(failed, [])

    def test_empty_file_index_treats_bare_refs_as_suspected(self):
        # When git isn't available, file_index is empty; bare refs
        # can't be resolved and correctly flip to suspected.
        stale, failed = _check_staleness_at_head(
            "Bare bare_only.py:5",
            self.base,
            {},  # empty index
        )
        self.assertEqual(stale, DocResearchFinding.STALENESS_SUSPECTED)


class ResolveRefPathTests(TestCase):
    """_resolve_ref_path handles /-paths directly and bare via index."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        (self.base / "a").mkdir()
        (self.base / "a" / "shallow.py").write_text("x\n")
        (self.base / "a" / "b" / "c").mkdir(parents=True)
        (self.base / "a" / "b" / "c" / "deep.py").write_text("y\n")
        self.index = {
            "shallow.py": {"a/shallow.py"},
            "deep.py": {"a/b/c/deep.py"},
            "collision.py": {"a/collision.py", "a/b/c/collision.py"},
        }
        (self.base / "a" / "collision.py").write_text("collision-shallow\n")
        (self.base / "a" / "b" / "c" / "collision.py").write_text("collision-deep\n")

    def test_slash_path_resolves_directly(self):
        p = _resolve_ref_path("a/shallow.py", self.base, self.index)
        self.assertIsNotNone(p)

    def test_slash_path_missing_returns_none(self):
        p = _resolve_ref_path("a/missing.py", self.base, self.index)
        self.assertIsNone(p)

    def test_bare_ref_resolves_via_index(self):
        p = _resolve_ref_path("deep.py", self.base, self.index)
        self.assertIsNotNone(p)
        self.assertTrue(str(p).endswith("a/b/c/deep.py"))

    def test_bare_ref_missing_returns_none(self):
        p = _resolve_ref_path("phantom.py", self.base, self.index)
        self.assertIsNone(p)

    def test_bare_ref_collision_prefers_shortest(self):
        # `collision.py` exists at both a/ and a/b/c/. Shortest wins.
        p = _resolve_ref_path("collision.py", self.base, self.index)
        self.assertIsNotNone(p)
        self.assertTrue(str(p).endswith("a/collision.py"))

    def test_bare_ref_without_index_returns_none(self):
        # No file_index → bare refs unresolvable (git isn't available).
        p = _resolve_ref_path("shallow.py", self.base, None)
        self.assertIsNone(p)


class BuildRepoFileIndexTests(TestCase):
    """_build_repo_file_index degrades to empty dict when git isn't available."""

    def test_returns_empty_dict_when_git_missing(self):
        # Point at a non-git directory; git ls-files will fail cleanly.
        with tempfile.TemporaryDirectory() as tmp:
            idx = _build_repo_file_index(Path(tmp))
        self.assertEqual(idx, {})

    def test_returns_populated_dict_on_real_repo(self):
        # Runs against the actual project repo; should have entries.
        from django.conf import settings
        idx = _build_repo_file_index(Path(settings.BASE_DIR))
        # The manage.py file must be present in ls-files.
        self.assertIn("manage.py", idx)
        # Sanity: FindingsTab exists somewhere and its basename is indexed.
        self.assertIn("FindingsTab.tsx", idx)


class RecheckStalenessCommandTests(TestCase):
    """`--recheck-staleness` mode: dry-run default, --apply persists."""

    def setUp(self):
        # Create rows with texts referencing files that don't exist in
        # the temp base_dir passed to the command. We patch BASE_DIR so
        # ALL refs go stale.
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        # Empty repo: no files → all refs suspected.

        def _mk(text, existing_staleness=DocResearchFinding.STALENESS_FRESH):
            return DocResearchFinding.objects.create(
                source_type="audit",
                source_heading="Executable Actions",
                doc_path="docs/x.md",
                domain_slug="test",
                text=text,
                text_hash=f"h-{timezone.now().timestamp()}-{text[:20]}"[:64],
                confidence="high",
                status=DocResearchFinding.STATUS_OPEN,
                finding_type=DocResearchFinding.FINDING_TYPE_EXECUTABLE,
                staleness=existing_staleness,
            )

        # Row 1: has a ref → would go suspected under empty base_dir.
        self.f_with_ref = _mk("Fix at core/nonexistent.py:5")
        # Row 2: no refs → stays fresh.
        self.f_no_ref = _mk("Just a general observation.")

    def _call(self, *extra):
        stdout = StringIO()
        with patch(
            "core.management.commands.index_doc_research_findings.settings"
        ) as mock_settings:
            mock_settings.BASE_DIR = str(self.base)
            call_command(
                "index_doc_research_findings",
                "--recheck-staleness",
                *extra,
                stdout=stdout,
            )
        return stdout.getvalue()

    def test_dry_run_default_does_not_persist(self):
        out = self._call()
        self.assertIn("dry-run", out)
        self.assertIn("Rows that would change: 1", out)
        # Nothing persisted.
        self.f_with_ref.refresh_from_db()
        self.assertEqual(
            self.f_with_ref.staleness, DocResearchFinding.STALENESS_FRESH
        )

    def test_apply_persists_and_writes_failed_refs(self):
        out = self._call("--apply")
        self.assertIn("Applied: 1", out)
        self.f_with_ref.refresh_from_db()
        self.assertEqual(
            self.f_with_ref.staleness, DocResearchFinding.STALENESS_SUSPECTED
        )
        # failed_refs land in metadata for downstream (v2 item #8).
        self.assertIn(
            "core/nonexistent.py:5",
            self.f_with_ref.metadata.get("staleness_failed_refs", []),
        )
        # Unchanged row stays fresh; no failed_refs pollution.
        self.f_no_ref.refresh_from_db()
        self.assertEqual(
            self.f_no_ref.staleness, DocResearchFinding.STALENESS_FRESH
        )
        self.assertNotIn("staleness_failed_refs", self.f_no_ref.metadata)


class SerializerAndFilterTests(TestCase):
    """`staleness` appears in serializer payload + is filterable on the list view."""

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            username="s2995_view_tester", password="pw", email="s2995@test.local"
        )
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.fresh = DocResearchFinding.objects.create(
            source_type="audit",
            source_heading="X",
            doc_path="docs/a.md",
            domain_slug="test",
            text="fresh row",
            text_hash="hash-fresh",
            confidence="high",
            status=DocResearchFinding.STATUS_OPEN,
            staleness=DocResearchFinding.STALENESS_FRESH,
        )
        self.stale = DocResearchFinding.objects.create(
            source_type="audit",
            source_heading="X",
            doc_path="docs/b.md",
            domain_slug="test",
            text="stale row",
            text_hash="hash-stale",
            confidence="high",
            status=DocResearchFinding.STATUS_OPEN,
            staleness=DocResearchFinding.STALENESS_SUSPECTED,
        )

    def test_serializer_includes_staleness(self):
        resp = self.client.get("/api/repo/doc-research-findings/?status=open")
        self.assertEqual(resp.status_code, 200)
        rows = {f["id"]: f for f in resp.json()["findings"]}
        self.assertEqual(
            rows[str(self.fresh.id)]["staleness"],
            DocResearchFinding.STALENESS_FRESH,
        )
        self.assertEqual(
            rows[str(self.stale.id)]["staleness"],
            DocResearchFinding.STALENESS_SUSPECTED,
        )

    def test_filter_by_staleness_suspected(self):
        resp = self.client.get(
            "/api/repo/doc-research-findings/?status=open&staleness=suspected"
        )
        self.assertEqual(resp.status_code, 200)
        ids = [f["id"] for f in resp.json()["findings"]]
        self.assertIn(str(self.stale.id), ids)
        self.assertNotIn(str(self.fresh.id), ids)

    def test_filter_by_staleness_fresh(self):
        resp = self.client.get(
            "/api/repo/doc-research-findings/?status=open&staleness=fresh"
        )
        self.assertEqual(resp.status_code, 200)
        ids = [f["id"] for f in resp.json()["findings"]]
        self.assertIn(str(self.fresh.id), ids)
        self.assertNotIn(str(self.stale.id), ids)

    def test_invalid_staleness_ignored(self):
        # An unknown value should be silently ignored, not 400.
        resp = self.client.get(
            "/api/repo/doc-research-findings/?status=open&staleness=bogus"
        )
        self.assertEqual(resp.status_code, 200)
        # Both rows returned (filter didn't apply).
        ids = [f["id"] for f in resp.json()["findings"]]
        self.assertIn(str(self.fresh.id), ids)
        self.assertIn(str(self.stale.id), ids)
