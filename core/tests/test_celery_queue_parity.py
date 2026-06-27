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
        # in a running celery worker / beat process.
        for module in (
            'core.tasks', 'core.tasks_agents', 'core.tasks_content',
            'core.tasks_spiders', 'core.tasks_financial', 'core.tasks_ops',
            'core.tasks_initiatives', 'core.tasks_misc',
            'core.tasks_conversations', 'core.tasks_body_systems',
            'core.tasks_media', 'core.celery',
            'ai_core.tasks', 'intelligence.tasks',
            'agents.tasks_enhanced', 'ml.tasks',
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
