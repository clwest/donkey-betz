"""
Session 2731 — Rigby Tool Validation Engineering Campaign, Batch D tool 1
regression tests for the PA_USE_FUNCTION_CALLING env flag.

Covers the F-WF-* findings surfaced during code trace + patched at
Session 2731. See:
- `docs/research/tools/validation/pa_use_function_calling_env_validation.md`
- `docs/research/tools/tools_validation_engineering_campaign_plan.md` §3.4

Findings covered:

- F-WF-1 code default flipped from 'false' to 'true'; docs updated.
- F-WF-2 Procfile declares PA_USE_FUNCTION_CALLING=true on every
  celery-* line as belt-and-suspenders against Railway env drift.
- F-WF-3 [PA_ROUTING_INIT] startup log emitted at module scope.
- F-WF-4 [PA_TASK_SUMMARY] includes routing_path=fc|keyword field.
- F-WF-6 MEMORY rule feedback_pa_worker_function_calling_env
  verified accurate at HEAD.

Existing coverage NOT duplicated:
- _detect_intent_and_route claude-code source short-circuit —
  covered in test_pa_intent_claude_code_source.py.

Run::

    python manage.py test core.tests.test_pa_use_function_calling_env_validation_2728 -v2
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

from django.test import SimpleTestCase


REPO_ROOT = Path(__file__).resolve().parents[2]


# ─── F-WF-1: code default flipped to 'true' ─────────────────────────────


class FWF1CodeDefaultTests(SimpleTestCase):
    """F-WF-1 — settings.py env-read default is 'true'; docs updated."""

    def test_settings_default_is_true(self):
        """Source-level guard against a regression to 'false'."""
        settings_path = REPO_ROOT / 'core' / 'settings.py'
        src = settings_path.read_text()
        # The exact line — allow whitespace variance but pin the default value.
        match = re.search(
            r"PA_USE_FUNCTION_CALLING\s*=\s*os\.environ\.get\(\s*"
            r"'PA_USE_FUNCTION_CALLING'\s*,\s*'([a-zA-Z]+)'\s*\)",
            src,
        )
        self.assertIsNotNone(
            match,
            'PA_USE_FUNCTION_CALLING env-read pattern not found in settings.py',
        )
        self.assertEqual(
            match.group(1), 'true',
            f"Code default must be 'true' (F-WF-1); got {match.group(1)!r}",
        )

    def test_docs_narrative_documents_current_default(self):
        """Narrative doc must not claim the code default is 'true' on
        Railway without qualifying that this is the code default AND the
        Procfile declaration; the pre-S2731 phrasing was ambiguous and
        conflated infra config with code default."""
        doc_path = REPO_ROOT / 'docs' / 'narratives' / 'PERSONAL_ASSISTANT.md'
        src = doc_path.read_text()
        # The rewritten line names Session 2731 F-WF-1 explicitly so a
        # reader knows the current default is the ratified state.
        self.assertIn('F-WF-1', src)
        # Both references (the table cell + the "How-to-verify" row) updated.
        self.assertEqual(
            src.count('F-WF-1'), 2,
            f"Expected 2 F-WF-1 references in narrative doc (table cell + "
            f"how-to-verify row); found {src.count('F-WF-1')}",
        )


# ─── F-WF-2: Procfile belt-and-suspenders ───────────────────────────────


class FWF2ProcfileTests(SimpleTestCase):
    """F-WF-2 — every celery-* line in Procfile declares
    PA_USE_FUNCTION_CALLING=true."""

    def _procfile_lines(self) -> list[str]:
        procfile = REPO_ROOT / 'Procfile'
        return procfile.read_text().splitlines()

    def test_every_celery_line_sets_env_flag(self):
        """Every non-comment line starting with `celery-` or `code-worker`
        must include `PA_USE_FUNCTION_CALLING=true`. beat is included —
        it's a scheduler that dispatches tasks that may indirectly
        depend on the flag, so belt-and-suspenders parity keeps the
        Procfile consistent."""
        procfile_lines = self._procfile_lines()
        celery_lines = [
            ln for ln in procfile_lines
            if (ln.startswith('celery-') or ln.startswith('code-worker'))
            and not ln.startswith('#')
        ]
        # Sanity check — we expect at least 6 celery lines + code-worker.
        self.assertGreaterEqual(
            len(celery_lines), 7,
            f"Expected ≥ 7 celery/code-worker lines in Procfile; got "
            f"{len(celery_lines)}: {celery_lines}",
        )
        for line in celery_lines:
            self.assertIn(
                'PA_USE_FUNCTION_CALLING=true',
                line,
                f"Procfile line missing PA_USE_FUNCTION_CALLING=true: {line}",
            )


# ─── F-WF-3: startup log ────────────────────────────────────────────────


class FWF3StartupLogTests(SimpleTestCase):
    """F-WF-3 — unified_pa_entrypoint emits [PA_ROUTING_INIT] at module
    scope so worker log tails show the routing path immediately."""

    def test_source_contains_routing_init_log(self):
        """Source-level guard that the log line exists at module scope."""
        pa_entry_path = (
            REPO_ROOT / 'core' / 'services' / 'unified_pa_entrypoint.py'
        )
        src = pa_entry_path.read_text()
        self.assertIn('[PA_ROUTING_INIT]', src)
        self.assertIn('routing_path=', src)
        # Emitted at module scope (before the class definition) — the
        # env raw + effective + routing_path together give operators
        # enough context to diagnose without triggering a Rigby turn.
        idx_log = src.find('[PA_ROUTING_INIT]')
        idx_class = src.find('class UnifiedPAEntrypoint')
        self.assertGreater(idx_log, 0, '[PA_ROUTING_INIT] log not found')
        self.assertGreater(idx_class, 0, 'class UnifiedPAEntrypoint not found')
        self.assertLess(
            idx_log, idx_class,
            '[PA_ROUTING_INIT] must be emitted at module scope BEFORE the '
            'class definition, so it fires once per worker at import time',
        )

    def test_log_reports_env_raw_and_effective(self):
        """The log format must expose both the raw env value AND the
        effective boolean — operators can distinguish 'unset (using code
        default)' from 'set to true' from 'set to yes fell through to False'."""
        pa_entry_path = (
            REPO_ROOT / 'core' / 'services' / 'unified_pa_entrypoint.py'
        )
        src = pa_entry_path.read_text()
        # The format string must contain both `env=` and `effective=`.
        # Search inside the F-WF-3 block scoped to the module head.
        head = src[:src.find('class UnifiedPAEntrypoint')]
        self.assertIn('env=', head)
        self.assertIn('effective=', head)


# ─── F-WF-4: PA_TASK_SUMMARY routing_path field ─────────────────────────


class FWF4TaskSummaryRoutingPathTests(SimpleTestCase):
    """F-WF-4 — [PA_TASK_SUMMARY] emits routing_path=fc|keyword."""

    def test_task_summary_format_includes_routing_path(self):
        pa_entry_path = (
            REPO_ROOT / 'core' / 'services' / 'unified_pa_entrypoint.py'
        )
        src = pa_entry_path.read_text()
        # The [PA_TASK_SUMMARY] format string must include `routing_path=`.
        idx = src.find('[PA_TASK_SUMMARY]')
        self.assertGreater(idx, 0)
        # Look at the ~20 lines after the [PA_TASK_SUMMARY] marker for
        # the routing_path field.
        window = src[idx:idx + 1500]
        self.assertIn('routing_path=', window)

    def test_routing_path_values_are_fc_or_keyword(self):
        """The routing_path value is computed from the settings flag as
        exactly 'fc' or 'keyword' — no other values, no None."""
        pa_entry_path = (
            REPO_ROOT / 'core' / 'services' / 'unified_pa_entrypoint.py'
        )
        src = pa_entry_path.read_text()
        # The computation should read `_routing_path = 'fc' if ... else 'keyword'`.
        self.assertIn("_routing_path = 'fc'", src)
        self.assertIn("else 'keyword'", src)


# ─── F-WF-6: MEMORY rule verified accurate at HEAD ─────────────────────


class FWF6MemoryRuleAccuracyTests(SimpleTestCase):
    """F-WF-6 — MEMORY rule feedback_pa_worker_function_calling_env
    accurately describes HEAD behavior after F-WF-1/2/3/4 patches."""

    def test_makefile_still_sets_flag(self):
        """The MEMORY rule's `make celery` claim rests on the Makefile
        declaring the flag on every celery target."""
        makefile_path = REPO_ROOT / 'Makefile'
        src = makefile_path.read_text()
        # Every celery target should still declare the flag (verified
        # via count — pre-S2731 was 5 celery targets, all with the flag).
        celery_target_count = src.count('PA_USE_FUNCTION_CALLING=true')
        self.assertGreaterEqual(
            celery_target_count, 5,
            f"Expected ≥ 5 PA_USE_FUNCTION_CALLING=true declarations in "
            f"Makefile; got {celery_target_count}",
        )

    def test_settings_env_read_pattern_unchanged(self):
        """The settings.py env-read pattern remains
        `os.environ.get('PA_USE_FUNCTION_CALLING', <default>).lower() == 'true'`.
        This shape is load-bearing for the MEMORY rule's claim that
        setting the env variable to any non-'true' value produces False."""
        settings_path = REPO_ROOT / 'core' / 'settings.py'
        src = settings_path.read_text()
        self.assertIn(
            ".lower() == 'true'",
            src,
            'settings.py must retain the case-insensitive true-only pattern',
        )

    def test_unified_pa_entrypoint_reads_via_getattr(self):
        """The MEMORY rule's claim that `getattr(settings,
        'PA_USE_FUNCTION_CALLING', False)` returns False when the setting
        isn't loaded is load-bearing. Guard the pattern."""
        pa_entry_path = (
            REPO_ROOT / 'core' / 'services' / 'unified_pa_entrypoint.py'
        )
        src = pa_entry_path.read_text()
        # Two `getattr(settings, 'PA_USE_FUNCTION_CALLING', False)` sites
        # — the main branch (line ~989) and the FC sanitizer (line ~1230).
        pattern_count = src.count(
            "getattr(settings, 'PA_USE_FUNCTION_CALLING', False)"
        )
        self.assertGreaterEqual(
            pattern_count, 2,
            f"Expected ≥ 2 getattr(settings, 'PA_USE_FUNCTION_CALLING', False) "
            f"sites in unified_pa_entrypoint.py; got {pattern_count}",
        )
