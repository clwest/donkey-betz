"""
Session 2731 — Rigby Tool Validation Engineering Campaign, Batch D tool 2
regression tests for Celery worker lifecycle.

Covers the F-CW-* findings surfaced during code trace + patched at
Session 2731. See:
- `docs/research/tools/validation/celery_worker_lifecycle_validation.md`
- `docs/research/tools/tools_validation_engineering_campaign_plan.md` §3.4

Findings covered:

- F-CW-1 Makefile `celery-recycle` target + solo-pool recycle note.
- F-CW-2 `worker_process_init` + `worker_process_shutdown` signal
  handlers in `core/celery.py`.
- F-CW-3 `make celery-status` checks all 5 workers (default, pa,
  long_running, broadcast, code_jobs).
- F-CW-4 MEMORY rule `feedback_local_celery_stall_playbook` diagnostic
  sequence still valid at HEAD.

Existing coverage NOT duplicated:
- Celery task retry semantics — covered in
  test_retry_behavior_validation_2728.py (Batch C tool 5 F-RB-4).

Run::

    python manage.py test core.tests.test_celery_worker_lifecycle_validation_2728 -v2
"""
from __future__ import annotations

from pathlib import Path

from django.test import SimpleTestCase


REPO_ROOT = Path(__file__).resolve().parents[2]


# ─── F-CW-1: Makefile celery-recycle + solo-pool note ─────────────────


class FCW1MakefileTests(SimpleTestCase):
    """F-CW-1 — Makefile has `celery-recycle` target + documents
    solo-pool implication."""

    def _makefile_src(self) -> str:
        return (REPO_ROOT / 'Makefile').read_text()

    def test_celery_recycle_target_exists(self):
        src = self._makefile_src()
        self.assertIn('celery-recycle:', src)

    def test_celery_recycle_in_phony(self):
        """Target must be in .PHONY declaration or make will confuse it
        with a file target."""
        src = self._makefile_src()
        # Search the first .PHONY line (there are multiple; F-CW-1 lives
        # on the celery-family line).
        phony_lines = [
            ln for ln in src.splitlines() if ln.startswith('.PHONY:')
        ]
        self.assertTrue(
            any('celery-recycle' in ln for ln in phony_lines),
            f"celery-recycle not in .PHONY: {phony_lines}",
        )

    def test_solo_pool_recycle_note_present(self):
        """Header comment on the `celery` target block must explain the
        solo-pool implication so future operators reading the Makefile
        don't have to trace to settings.py."""
        src = self._makefile_src()
        # Naming keys — accept either the F-CW-1 tag or the phrase
        # "silently ignored" which is load-bearing to the explanation.
        self.assertIn('F-CW-1', src)
        self.assertIn('silently ignored', src)


# ─── F-CW-2: worker_process_init/shutdown handlers ─────────────────────


class FCW2CelerySignalHandlerTests(SimpleTestCase):
    """F-CW-2 — `core/celery.py` registers worker lifecycle handlers."""

    def _celery_src(self) -> str:
        return (REPO_ROOT / 'core' / 'celery.py').read_text()

    def test_imports_worker_process_signals(self):
        src = self._celery_src()
        self.assertIn(
            'from celery.signals import worker_process_init, worker_process_shutdown',
            src,
        )

    def test_worker_init_handler_registered(self):
        src = self._celery_src()
        self.assertIn('@worker_process_init.connect', src)
        self.assertIn('[CELERY_WORKER_INIT]', src)

    def test_worker_shutdown_handler_registered(self):
        src = self._celery_src()
        self.assertIn('@worker_process_shutdown.connect', src)
        self.assertIn('[CELERY_WORKER_SHUTDOWN]', src)

    def test_handlers_are_importable_at_module_load(self):
        """Importing `core.celery` must not raise. If the signal wiring
        broke, this test fails at import time before the assertion runs."""
        from core import celery as core_celery
        self.assertTrue(hasattr(core_celery, '_log_worker_process_init'))
        self.assertTrue(hasattr(core_celery, '_log_worker_process_shutdown'))


# ─── F-CW-3: celery-status checks all 5 workers ────────────────────────


class FCW3CeleryStatusCompletenessTests(SimpleTestCase):
    """F-CW-3 — `make celery-status` checks every worker `make celery`
    starts, not just three of them."""

    def _makefile_src(self) -> str:
        return (REPO_ROOT / 'Makefile').read_text()

    def test_status_checks_pa_worker(self):
        """The critical addition — pre-S2731 pa was NOT verified."""
        src = self._makefile_src()
        # Locate the celery-status target body.
        idx = src.find('celery-status:')
        self.assertGreater(idx, 0)
        # Look at the next ~2000 chars for the pa hostname check.
        window = src[idx:idx + 2000]
        self.assertIn('hostname=pa@', window)
        # The failure-path hint tells the operator where to look.
        self.assertIn('celery-pa.log', window)

    def test_status_checks_code_jobs_worker(self):
        """F-CW-3 — code_jobs missing pre-S2731. Verify present at HEAD."""
        src = self._makefile_src()
        idx = src.find('celery-status:')
        window = src[idx:idx + 2000]
        self.assertIn('hostname=code_jobs', window)

    def test_status_checks_all_five_workers(self):
        """Overall completeness: default + pa + long_running + broadcast
        + code_jobs = 5 worker hostnames checked."""
        src = self._makefile_src()
        idx = src.find('celery-status:')
        window = src[idx:idx + 2000]
        expected_hostnames = (
            'hostname=default',
            'hostname=pa@',
            'hostname=long_running',
            'hostname=broadcast',
            'hostname=code_jobs',
        )
        for hostname in expected_hostnames:
            self.assertIn(
                hostname, window,
                f"celery-status missing check for {hostname!r}",
            )


# ─── F-CW-4: MEMORY rule stall playbook verified at HEAD ──────────────


class FCW4StallPlaybookMemoryRuleTests(SimpleTestCase):
    """F-CW-4 — the MEMORY rule feedback_local_celery_stall_playbook
    diagnostic 6-step sequence still references files/paths that exist
    at HEAD."""

    def test_redis_broker_still_at_db_2(self):
        """Step 2 of the rule assumes broker at redis://localhost:6379/2.
        If the broker DB number changed, the rule's `redis-cli` recipes
        would query the wrong DB."""
        from django.conf import settings
        self.assertIn(
            '/2', settings.CELERY_BROKER_URL,
            f"CELERY_BROKER_URL is {settings.CELERY_BROKER_URL!r} — "
            f"MEMORY rule assumes db 2",
        )

    def test_celery_task_event_model_exists(self):
        """Step 1 of the rule queries `core_celerytaskevent` table.
        Verify the model exists at HEAD."""
        # Import path check — if the model was moved / renamed, the
        # MEMORY rule's SQL becomes stale.
        try:
            from core.models import CeleryTaskEvent  # noqa: F401
        except ImportError:
            self.fail(
                'core.models.CeleryTaskEvent not importable — MEMORY rule '
                'stall-playbook step 1 SQL is stale',
            )

    def test_settings_still_has_prefork_recycle_config(self):
        """The stall-playbook rests on prefork recycle being the
        production discipline. If these settings disappear, Railway
        workers stop recycling and the failure class returns."""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'CELERY_WORKER_MAX_TASKS_PER_CHILD'))
        self.assertTrue(hasattr(settings, 'CELERY_WORKER_MAX_MEMORY_PER_CHILD'))
        # Values must be positive ints (any specific number is OK — the
        # rule doesn't rest on the exact number).
        self.assertIsInstance(settings.CELERY_WORKER_MAX_TASKS_PER_CHILD, int)
        self.assertGreater(settings.CELERY_WORKER_MAX_TASKS_PER_CHILD, 0)


# ─── F-CW-5 companion: Procfile prefork recycle discipline verified ────


class FCWProcfilePreforkRecycleTests(SimpleTestCase):
    """F-CW-5 companion — Procfile still declares --max-tasks-per-child
    on every prefork celery-* line. If Railway ever silently changed
    this, workers would stop recycling and the failure class returns."""

    def test_procfile_prefork_workers_all_declare_max_tasks(self):
        procfile = REPO_ROOT / 'Procfile'
        lines = procfile.read_text().splitlines()
        prefork_lines = [
            ln for ln in lines
            if ln.startswith(('celery-', 'code-worker'))
            and 'prefork' in ln
            and not ln.startswith('#')
        ]
        self.assertGreaterEqual(
            len(prefork_lines), 6,
            f"Expected ≥ 6 prefork celery/code-worker lines in Procfile; "
            f"got {len(prefork_lines)}: {prefork_lines}",
        )
        for line in prefork_lines:
            self.assertIn(
                '--max-tasks-per-child=',
                line,
                f"Procfile prefork line missing --max-tasks-per-child: {line}",
            )
