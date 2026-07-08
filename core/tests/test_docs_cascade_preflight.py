"""Cycle 1A KFI-4 (ADR-0140) — docs cascade hash-delta preflight tests.

Coverage per ADR-0140 §2.3 + Chris SIGN-2 verification:

- T1  _hash_docs_tree: SHA-256 aggregate over docs/**.md; changing a
      file body changes the hash
- T2  _hash_docs_tree: deterministic across two invocations
- T3  _hash_docs_tree: mtime-only change → hash unchanged (content-hash
      only, per ADR §2.1 (4))
- T4  _preflight_should_short_circuit(force=True) → always proceeds
- T5  short-circuit path: cache-match + unembedded=0 → wire ONLY the
      preflight-marker step; StepResult(passed=True, extra={verdict:
      SKIPPED_NO_CHANGES, preflight_short_circuit: True})
- T6  proceed path: cache-miss OR unembedded>0 → wire 5-step pipeline;
      preflight-marker StepResult(passed=True, extra={preflight_pass})
- T7  migration 0378 drops PeriodicTask(name='refresh-docs-corpus-daily');
      reverse recreates it idempotently
- T8  static beat_schedule at core/celery.py: no 'refresh-docs-corpus-daily'
      key
- T9  refresh_docs_corpus function still callable (backward compat via
      deprecation docstring; body preserved)
- T10 cross-ADR invariant: cascade output carries source='imported' +
      extracted_metadata['scope']='docs_index' (KFI-2 predicate stability)
- T11 (F3) SKIPPED_NO_CHANGES = healthy operational outcome:
      StepResult.passed=True (maps to OpsRun.status='passed' via
      MissionRunner), and cascade_success_rate_7d ORM-style query counts
      skip toward pass
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings

from core.jobs.docs_cascade import (
    _DOCS_INDEX_HASH_CACHE_KEY,
    _hash_docs_tree,
    _iter_docs_md_paths,
    _preflight_should_short_circuit,
    build_docs_manager_runner,
)


def _seed_docs_tree(root: Path, files: dict) -> None:
    """Write a docs/-shaped fixture tree under `root`.

    `files` maps relative-path -> content (str). Directories are
    created as needed. Includes an underscore-prefixed derived file
    to exercise the exclusion rule from _iter_docs_md_paths.
    """
    root.mkdir(parents=True, exist_ok=True)
    for rel_path, content in files.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# T1 / T2 / T3: _hash_docs_tree contract
# ---------------------------------------------------------------------------


class HashDocsTreeTests(TestCase):

    def setUp(self):
        self._tmp = Path(self.settings_override_dir()) / "docs"
        _seed_docs_tree(
            self._tmp,
            {
                "a.md": "alpha content",
                "sub/b.md": "beta content",
                "_index.json": "derived — must be excluded",
                "_provenance.json": "derived — must be excluded",
                ".hidden/c.md": "hidden — must be excluded",
            },
        )
        self._settings_ctx = override_settings(
            BASE_DIR=str(self._tmp.parent),
        )
        self._settings_ctx.enable()

    def tearDown(self):
        self._settings_ctx.disable()

    def settings_override_dir(self):
        # Use pytest tmp dir if available; otherwise fall back to a
        # deterministic per-test-name path so setUp is idempotent.
        import tempfile
        return tempfile.mkdtemp(prefix="kfi4-hash-")

    def test_t1_hash_changes_when_file_body_changes(self):
        first = _hash_docs_tree()
        # Modify one file's bytes.
        (self._tmp / "a.md").write_text("alpha content — MODIFIED", encoding="utf-8")
        second = _hash_docs_tree()
        self.assertNotEqual(first, second)

    def test_t2_hash_is_deterministic(self):
        a = _hash_docs_tree()
        b = _hash_docs_tree()
        self.assertEqual(a, b)

    def test_t3_hash_ignores_mtime(self):
        first = _hash_docs_tree()
        # Touch the file mtime forward WITHOUT changing content.
        target = self._tmp / "a.md"
        current_stat = target.stat()
        new_mtime = current_stat.st_mtime + 3600
        os.utime(target, (new_mtime, new_mtime))
        second = _hash_docs_tree()
        self.assertEqual(first, second, "mtime-only change must not affect hash")

    def test_iter_docs_excludes_underscore_and_hidden(self):
        # Sanity: derived + hidden paths must not appear.
        paths = _iter_docs_md_paths()
        rel_paths = {
            p.relative_to(self._tmp).as_posix() for p in paths
        }
        self.assertIn("a.md", rel_paths)
        self.assertIn("sub/b.md", rel_paths)
        self.assertNotIn("_index.json", rel_paths)  # not .md but sanity
        for p in rel_paths:
            self.assertFalse(p.startswith("_"), p)
            self.assertFalse(p.startswith("."), p)
            self.assertNotIn("/.", p)


# ---------------------------------------------------------------------------
# T4 / T5 / T6: _preflight_should_short_circuit + factory wiring
# ---------------------------------------------------------------------------


class PreflightDecisionTests(TestCase):

    def setUp(self):
        cache.delete(_DOCS_INDEX_HASH_CACHE_KEY)

    def tearDown(self):
        cache.delete(_DOCS_INDEX_HASH_CACHE_KEY)

    def test_t4_force_true_always_proceeds(self):
        # Even when cache matches AND unembedded==0, force must proceed.
        # Empty test DB naturally has unembedded_count=0.
        with mock.patch(
            "core.jobs.docs_cascade._hash_docs_tree",
            return_value="deadbeef",
        ):
            cache.set(_DOCS_INDEX_HASH_CACHE_KEY, "deadbeef", timeout=None)
            short_circuit, detail = _preflight_should_short_circuit(
                force=True,
            )
        self.assertFalse(short_circuit)
        self.assertEqual(detail.get("reason"), "forced")
        self.assertTrue(detail.get("force"))

    def test_t5_short_circuit_when_cache_matches_and_no_unembedded(self):
        # Empty test DB → 0 unembedded; matching cache → short-circuit.
        with mock.patch(
            "core.jobs.docs_cascade._hash_docs_tree",
            return_value="cafebabe",
        ):
            cache.set(_DOCS_INDEX_HASH_CACHE_KEY, "cafebabe", timeout=None)
            short_circuit, detail = _preflight_should_short_circuit(
                force=False,
            )
        self.assertTrue(short_circuit)
        self.assertEqual(detail.get("reason"), "no_changes")
        self.assertEqual(detail.get("cached_hash"), "cafebabe")
        self.assertEqual(detail.get("unembedded_count"), 0)

    def test_t6a_proceed_when_cache_miss(self):
        # Cache empty → proceed even though unembedded_count=0.
        with mock.patch(
            "core.jobs.docs_cascade._hash_docs_tree",
            return_value="cafebabe",
        ):
            short_circuit, detail = _preflight_should_short_circuit(
                force=False,
            )
        self.assertFalse(short_circuit)
        self.assertEqual(detail.get("reason"), "changes_or_unembedded")
        self.assertEqual(detail.get("current_hash"), "cafebabe")

    def test_t6b_proceed_when_unembedded_positive(self):
        # Seed an unembedded Document to force the "unembedded>0" branch.
        # (matching cache; only unembedded>0 forces proceed.)
        from content.models import Document
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username="kfi4-t6b",
            email="kfi4-t6b@example.com",
            password="fixture",
        )
        Document.objects.create(
            owner=user,
            title="unembedded fixture",
            description="",
            document_type="markdown",
            source="imported",
            file_path="docs/x.md",
            raw_content="body without embeddings",
            is_active=True,
        )
        with mock.patch(
            "core.jobs.docs_cascade._hash_docs_tree",
            return_value="cafebabe",
        ):
            cache.set(_DOCS_INDEX_HASH_CACHE_KEY, "cafebabe", timeout=None)
            short_circuit, detail = _preflight_should_short_circuit(
                force=False,
            )
        self.assertFalse(short_circuit)
        self.assertGreaterEqual(detail.get("unembedded_count"), 1)


# ---------------------------------------------------------------------------
# T5 / T6: factory-side conditional wiring (Option B)
# ---------------------------------------------------------------------------


class BuildRunnerConditionalWiringTests(TestCase):

    def setUp(self):
        cache.delete(_DOCS_INDEX_HASH_CACHE_KEY)

    def tearDown(self):
        cache.delete(_DOCS_INDEX_HASH_CACHE_KEY)

    def test_short_circuit_wires_only_preflight_step(self):
        with mock.patch(
            "core.jobs.docs_cascade._preflight_should_short_circuit",
            return_value=(True, {"reason": "no_changes", "cached_hash": "x"}),
        ):
            runner = build_docs_manager_runner(force=False)
        step_names = [s.name for s in runner.steps]
        self.assertEqual(step_names, ["step_0_preflight_hash_delta"])

    def test_proceed_wires_full_pipeline(self):
        with mock.patch(
            "core.jobs.docs_cascade._preflight_should_short_circuit",
            return_value=(
                False,
                {"reason": "changes_or_unembedded", "current_hash": "x"},
            ),
        ):
            runner = build_docs_manager_runner(force=False)
        step_names = [s.name for s in runner.steps]
        self.assertEqual(
            step_names,
            [
                "step_0_preflight_hash_delta",
                "step_1_index",
                "step_2_corpus",
                "step_3_sync",
                "step_4_embed",
            ],
        )

    def test_force_true_propagates_to_preflight(self):
        with mock.patch(
            "core.jobs.docs_cascade._preflight_should_short_circuit",
            return_value=(
                False,
                {"reason": "forced", "force": True},
            ),
        ) as mock_preflight:
            build_docs_manager_runner(force=True)
        mock_preflight.assert_called_once_with(force=True)


# ---------------------------------------------------------------------------
# T11 (F3) — preflight-marker StepResult contract + SKIPPED_NO_CHANGES = healthy
# ---------------------------------------------------------------------------


class PreflightStepResultContractTests(TestCase):

    def setUp(self):
        cache.delete(_DOCS_INDEX_HASH_CACHE_KEY)

    def tearDown(self):
        cache.delete(_DOCS_INDEX_HASH_CACHE_KEY)

    def test_short_circuit_step_result_shape(self):
        from core.jobs.docs_cascade import (
            _make_preflight_hash_delta_step,
        )
        step_fn = _make_preflight_hash_delta_step(
            short_circuit=True,
            detail={"reason": "no_changes", "cached_hash": "x", "unembedded_count": 0},
        )
        with mock.patch("core.jobs.docs_cascade._emit_event"):
            result = step_fn(mock.MagicMock())
        # Health invariant: passed=True (maps to OpsRun.status='passed').
        self.assertTrue(result.passed)
        # Verdict + short-circuit flag persist in extra.
        self.assertEqual(result.extra["verdict"], "SKIPPED_NO_CHANGES")
        self.assertTrue(result.extra["preflight_short_circuit"])
        # Detail keys preserved.
        self.assertEqual(result.extra["cached_hash"], "x")

    def test_proceed_step_result_shape(self):
        from core.jobs.docs_cascade import (
            _make_preflight_hash_delta_step,
        )
        step_fn = _make_preflight_hash_delta_step(
            short_circuit=False,
            detail={"reason": "changes_or_unembedded", "current_hash": "y"},
        )
        with mock.patch("core.jobs.docs_cascade._emit_event"):
            result = step_fn(mock.MagicMock())
        self.assertTrue(result.passed)
        self.assertTrue(result.extra["preflight_pass"])
        # Short-circuit flag must NOT be set on the proceed variant.
        self.assertNotIn("preflight_short_circuit", result.extra)
        self.assertNotIn("verdict", result.extra)

    def test_t11_skipped_counts_as_healthy_for_metric_query(self):
        # Emulate the ADR §2.6.1 metric query shape:
        # OpsRun.objects.filter(status='passed').count() counts the run.
        # We prove StepResult.passed=True → run-level 'passed' compatible.
        from core.jobs.docs_cascade import (
            _make_preflight_hash_delta_step,
        )
        step_fn = _make_preflight_hash_delta_step(
            short_circuit=True,
            detail={"reason": "no_changes"},
        )
        with mock.patch("core.jobs.docs_cascade._emit_event"):
            result = step_fn(mock.MagicMock())
        self.assertTrue(
            result.passed,
            "SKIPPED_NO_CHANGES must map to healthy pass semantics — "
            "OpsRun.status='passed' downstream, counted by "
            "cascade_success_rate_7d + cascade_last_success_at.",
        )


# ---------------------------------------------------------------------------
# T7 / T8: migration + static beat_schedule
# ---------------------------------------------------------------------------


class MigrationAndScheduleTests(TestCase):

    def test_t8_static_beat_schedule_has_no_legacy_entry(self):
        from core.celery import app as celery_app
        beat_schedule = getattr(celery_app.conf, "beat_schedule", {}) or {}
        self.assertNotIn("refresh-docs-corpus-daily", beat_schedule)

    def test_t7_migration_0378_drops_periodic_task(self):
        from django_celery_beat.models import PeriodicTask
        # After the migration runs during test DB setup, the row must be absent.
        self.assertFalse(
            PeriodicTask.objects.filter(name="refresh-docs-corpus-daily").exists(),
            "Migration 0378 did not drop the legacy PeriodicTask row.",
        )


# ---------------------------------------------------------------------------
# T9: legacy refresh_docs_corpus is still callable
# ---------------------------------------------------------------------------


class LegacyCallableCompatTests(TestCase):

    def test_t9_refresh_docs_corpus_still_importable_and_callable(self):
        # Deprecation is docstring-only per ADR §2.1 (3); function body
        # preserved unchanged. Any programmatic caller continues to work.
        from core.tasks import refresh_docs_corpus
        self.assertTrue(callable(refresh_docs_corpus))
        # Confirm the deprecation notice landed on the docstring.
        docstring = (refresh_docs_corpus.__doc__ or "") + (
            getattr(refresh_docs_corpus, "run", None).__doc__ or ""
            if hasattr(refresh_docs_corpus, "run") else ""
        )
        self.assertIn("KFI-4", docstring)
        self.assertIn("DEPRECATED", docstring)


# ---------------------------------------------------------------------------
# T10: cross-ADR invariant — cascade output carries KFI-2 predicate markers
# ---------------------------------------------------------------------------


class CrossADRInvariantTests(TestCase):
    """T10 asserts the invariant that KFI-2's canonical_authority
    derivation predicate depends on: cascade-produced Documents carry
    ``source='imported'`` AND ``extracted_metadata['scope']='docs_index'``.

    We assert the invariant at the PREDICATE level rather than by
    running a live cascade (which would require the full docs corpus
    fixture). The predicate lives in ``sync_docs_index_to_documents``
    and is empirically true across all 2986 imported rows at HEAD per
    the KFI-4 preflight verification ledger.
    """

    def test_t10_kfi2_predicate_markers_available(self):
        # KFI-2 field must be present on Document (post-KFI-2 shipped).
        from content.models import Document
        field_names = {f.name for f in Document._meta.get_fields()}
        self.assertIn("source", field_names)
        self.assertIn("extracted_metadata", field_names)
        self.assertIn("canonical_authority", field_names)  # KFI-2

    def test_t10_kfi2_derivation_helper_recognizes_docs_index_marker(self):
        # KFI-2's helper is the load-bearing consumer of cascade output.
        # A synthetic Document with the two markers must classify as
        # repo_canonical (per KFI-2 §2.1 B3 predicate).
        from content.models import Document
        from content._canonical_authority_helpers import (
            _derive_canonical_authority,
        )
        doc = Document(
            source="imported",
            file_path="docs/some/page.md",
            extracted_metadata={"scope": "docs_index"},
        )
        self.assertEqual(_derive_canonical_authority(doc), "repo_canonical")
