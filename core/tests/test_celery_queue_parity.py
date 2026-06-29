"""Celery queue parity canary — Procfile ↔ Makefile ↔ task_routes.

Session 1244 closed the Celery wiring audit by enforcing this invariant:
every queue declared in `task_routes` (via `Celery.conf.task_routes` /
`CELERY_TASK_ROUTES`) must be consumed by BOTH a Procfile worker line
(Railway production) AND a Makefile celery target block (local dev).

If this invariant breaks, tasks routed to the missing queue silently
hang forever — no telemetry, no exception, no visible failure. The
canonical symptom is `CeleryTaskEvent.objects.filter(task_name=...)
.count() == 0` for tasks that should be running periodically.

The S1244 audit caught a real instance: `sports` queue was declared in
`task_routes` (8 task patterns including `core.tasks.snapshot_odds_for_
line_movement`, `core.tasks.scan_arbs_and_notify`, etc.) + consumed by
Procfile's `celery-worker` line — but missing from Makefile's local
default worker. Locally-dispatched sports tasks would hang. Fixed in
the same PR that added this test.

Reference memory rule: `feedback_procfile_makefile_queue_parity.md`.

Run: `python manage.py test core.tests.test_celery_queue_parity -v2`
"""

import os
import re

from django.test import SimpleTestCase

REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')
)


def extract_queues_from_file(path):
    """Pull all `-Q foo,bar` and `--queues=foo,bar` queue names from a file."""
    with open(path) as f:
        content = f.read()
    queues = set()
    for m in re.finditer(r'(?:-Q[ =]|--queues[= ])([\w,]+)', content):
        for q in m.group(1).split(','):
            q = q.strip()
            if q:
                queues.add(q)
    return queues


class CeleryQueueParityTests(SimpleTestCase):
    """Lock in the Procfile ↔ Makefile ↔ task_routes parity invariant."""

    def setUp(self):
        # Trigger task discovery so task_routes is populated as it would be
        # in a running celery worker / beat process. The complete list below
        # must stay in sync with every `tasks.py` and `tasks_*.py` under apps
        # in INSTALLED_APPS — if a new task module is added, register it here
        # OR rely on Django autodiscover (only fires at app-ready, not in
        # SimpleTestCase setUp).
        for module in (
            # core/ — the monolith plus tasks_*.py siblings
            'core.tasks', 'core.tasks_agents', 'core.tasks_content',
            'core.tasks_spiders', 'core.tasks_financial', 'core.tasks_ops',
            'core.tasks_initiatives', 'core.tasks_misc',
            'core.tasks_conversations', 'core.tasks_body_systems',
            'core.tasks_media', 'core.tasks_executor',
            'core.tasks_push_notifications', 'core.celery',
            # other apps' tasks.py files
            'ai_core.tasks', 'ai_core.spiders.tasks',
            'intelligence.tasks',
            'agents.tasks', 'agents.tasks_enhanced',
            'content.tasks',
            'pipelines.tasks',
            'sports.tasks',
            'ml.tasks',
        ):
            try:
                __import__(module)
            except Exception:
                pass

    def _declared_queues(self):
        from celery import current_app
        routes = current_app.conf.task_routes or {}
        queues = set()
        for route_info in routes.values():
            if isinstance(route_info, dict):
                q = route_info.get('queue')
                if q:
                    queues.add(q)
            elif isinstance(route_info, str):
                queues.add(route_info)
        return queues

    def test_every_declared_queue_has_a_procfile_consumer(self):
        """Production worker (Procfile) must consume every declared queue."""
        declared = self._declared_queues()
        proc_queues = extract_queues_from_file(os.path.join(REPO_ROOT, 'Procfile'))
        missing = declared - proc_queues
        self.assertFalse(
            missing,
            f"Queues declared in task_routes but no Procfile worker consumes them: "
            f"{sorted(missing)}. Add `-Q {','.join(sorted(missing))}` to an "
            f"existing Procfile worker line, or add a new worker. Production "
            f"tasks routed to these queues will hang forever.\n"
            f"  Declared: {sorted(declared)}\n  Procfile:  {sorted(proc_queues)}"
        )

    def test_every_declared_queue_has_a_makefile_consumer(self):
        """Local dev worker (Makefile) must consume every declared queue."""
        declared = self._declared_queues()
        make_queues = extract_queues_from_file(os.path.join(REPO_ROOT, 'Makefile'))
        missing = declared - make_queues
        self.assertFalse(
            missing,
            f"Queues declared in task_routes but no Makefile worker consumes them: "
            f"{sorted(missing)}. Add `--queues=...,{','.join(sorted(missing))}` "
            f"to a worker block in the Makefile `celery` target. Local "
            f"dispatches to these queues will hang silently.\n"
            f"  Declared: {sorted(declared)}\n  Makefile:  {sorted(make_queues)}"
        )

    def test_no_consumed_queue_lacks_a_route_declaration(self):
        """Procfile/Makefile workers shouldn't consume queues nothing routes to.

        Less critical (no runtime hang), but signals a stale worker
        configuration — a queue that no task gets routed to is a dormant
        capacity drain.
        """
        declared = self._declared_queues()
        proc_queues = extract_queues_from_file(os.path.join(REPO_ROOT, 'Procfile'))
        make_queues = extract_queues_from_file(os.path.join(REPO_ROOT, 'Makefile'))
        consumed = (proc_queues | make_queues)
        orphan = consumed - declared
        self.assertFalse(
            orphan,
            f"Queues consumed by Procfile/Makefile but not declared in "
            f"task_routes: {sorted(orphan)}. Either add a route declaration "
            f"or remove the consumer to free capacity.\n"
            f"  Consumed: {sorted(consumed)}\n  Declared: {sorted(declared)}"
        )

    def test_every_route_pattern_matches_a_registered_task(self):
        """Every task_routes pattern must match at least 1 registered task.

        Catches orphan routes — declarations pointing at tasks that no
        @shared_task claims. Orphan routes are no-ops at runtime (they
        route nothing because the target task doesn't exist), but they
        pollute the routing config and signal stale references that
        survived a task rename/delete.

        Patterns can be exact dotted-paths or wildcards (`app.*`).
        Short-name patterns (no dot) match by task name lookup.

        S1244 caught 7 orphan routes:
        - 3x narrative_drift.* (process_spider_data, send_daily_digest,
          process_shifts_for_content) — siblings of run_detector_cycle
          which IS registered
        - unified_pipeline.run_complete_cycle — sibling of health_check
        - 3x core.tasks.* (workspace_autopilot_tick, aggregate_spider_signals,
          process_pending_auto_topics) — short-name routes for these still
          work; the full-path routes were dead duplicates
        """
        from celery import current_app
        registered = {t for t in current_app.tasks.keys()
                      if not t.startswith('celery.')}
        routes = current_app.conf.task_routes or {}

        orphan_patterns = []
        for pattern in routes.keys():
            if pattern.endswith('.*'):
                prefix = pattern[:-2]
                if not any(t.startswith(prefix + '.') or t == prefix
                           for t in registered):
                    orphan_patterns.append(pattern)
            else:
                if pattern not in registered:
                    orphan_patterns.append(pattern)

        if orphan_patterns:
            lines = ["task_routes patterns with no matching registered task:"]
            for p in sorted(orphan_patterns):
                queue = routes[p].get('queue', '?') if isinstance(routes[p], dict) else '?'
                lines.append(f"  [{queue}] {p}")
            lines.append("")
            lines.append(
                "Remove the orphan pattern(s) from CELERY_TASK_ROUTES in "
                "core/settings.py, OR add the @shared_task back if it was "
                "removed by mistake. Orphan routes are runtime no-ops but "
                "pollute the routing config."
            )
            self.fail("\n".join(lines))


class DocsManagerTaskRegistrationTests(SimpleTestCase):
    """S1253 hotfix lock-in: docs-manager beat task must register at worker boot.

    Background: S1252 PR #2730 added `@shared_task rigby_documentation_manager_daily`
    in `core/tasks_documentation_manager.py` (non-standard tasks_*.py module name).
    Cutover verification went through `manage.py run_docs_manager_daily` which
    imports the module directly, so the worker dispatch path was never exercised.
    First beat fire 2026-06-29 06:30 MDT was rejected with
    `KeyError: 'rigby_documentation_manager_daily'` because the module was never
    added to `app.conf.imports` in `core/celery.py`.

    These tests catch both ways the registration can regress:
    - module dropped from `app.conf.imports`
    - `@shared_task` renamed/removed in the module
    """

    def test_rigby_documentation_manager_daily_in_registry(self):
        from celery import current_app
        current_app.finalize()
        self.assertIn(
            'rigby_documentation_manager_daily',
            current_app.tasks,
            "rigby_documentation_manager_daily missing from Celery task "
            "registry. Either core.tasks_documentation_manager was removed "
            "from app.conf.imports in core/celery.py, or the @shared_task "
            "decorator/name was changed in tasks_documentation_manager.py. "
            "See S1253 hotfix.",
        )

    def test_docs_manager_module_pinned_in_app_conf_imports(self):
        from celery import current_app
        imports = tuple(current_app.conf.imports or ())
        self.assertIn(
            'core.tasks_documentation_manager',
            imports,
            "'core.tasks_documentation_manager' removed from "
            "core/celery.py:app.conf.imports — worker boots will not pick up "
            "the @shared_task. See S1253 hotfix.",
        )


class PlatformAuditTaskRegistrationTests(SimpleTestCase):
    """Session 1257 PR 2.2 lock-in: Platform Auditor task must register at
    worker boot.

    Mirrors the S1253 docs-manager registration tests. Catches both
    regression shapes:
      - `core.tasks_platform_audit` dropped from `app.conf.imports`
      - `@shared_task` renamed/removed in tasks_platform_audit.py
    """

    def test_platform_auditor_run_in_registry(self):
        from celery import current_app
        current_app.finalize()
        self.assertIn(
            'platform_auditor_run',
            current_app.tasks,
            "platform_auditor_run missing from Celery task registry. "
            "Either core.tasks_platform_audit was removed from "
            "app.conf.imports in core/celery.py, or the @shared_task "
            "decorator/name was changed in tasks_platform_audit.py. "
            "See PR 2.2.",
        )

    def test_platform_audit_module_pinned_in_app_conf_imports(self):
        from celery import current_app
        imports = tuple(current_app.conf.imports or ())
        self.assertIn(
            'core.tasks_platform_audit',
            imports,
            "'core.tasks_platform_audit' removed from "
            "core/celery.py:app.conf.imports — worker boots will not "
            "pick up the @shared_task. See PR 2.2.",
        )

    def test_platform_audit_task_eager_import_listed(self):
        """The eager-import hook must include core.tasks_platform_audit
        so `app.tasks` reads at finalize time see it."""
        import inspect

        from core.celery import _eager_import_session1115_modules

        source = inspect.getsource(_eager_import_session1115_modules)
        self.assertIn(
            "core.tasks_platform_audit", source,
            "Platform Audit task module missing from the eager-import set "
            "in core/celery.py:_eager_import_session1115_modules. "
            "Without this, build_celery_audit / verify_doc_claims may "
            "fail to see the task at finalize time. See PR 2.2.",
        )
