"""Runtime-telemetry zero-fire audit — which registered Celery tasks haven't fired.

Companion to `build_celery_audit.py` (static caller analysis writing
`docs/CELERY_AUDIT.md`). This command answers the *runtime* question:
of the registered tasks, which have NOT fired in the last N days, and
of those, which are already known-deferred per `AUDIT_FINDINGS.md` #12?

Built in Session 1245, after the S1244 Celery wiring audit deferred
"dead-task analysis" to a telemetry-based approach. S1245's first pass
surfaced 14 "disconnected" tasks — verify-before-delete cross-reference
showed that 11 of the 14 were already documented as deferred-by-policy
in `AUDIT_FINDINGS.md` #12 (S1115 multi-batch audit, 272 → 10 orphan
reduction). The remaining 3 were 1 probe false positive (direct Python
caller missed) + 2 net-new dormant-subsystem findings (`content/`
character training).

The KNOWN_DEFERRED set below is the canonical list from
`AUDIT_FINDINGS.md` #12 — keep it in sync when that audit evolves.

Session 1246 — added `--include-direct-calls` axis. The S1245 probe blind
spot was a task that was zero-fire AND not in KNOWN_DEFERRED, but had a
direct Python caller in a mgmt command. Without this axis, that task
looked deletable. The axis runs `rg "\\b<short>\\s*\\("` per uncategorized
zero-fire task, excludes the def-site file, and reports the remaining
caller-hit count. Any non-zero hit means deletion is unsafe without
deeper review.

Run::

    python manage.py audit_celery_zero_fire
    python manage.py audit_celery_zero_fire --days 7
    python manage.py audit_celery_zero_fire --json
    python manage.py audit_celery_zero_fire --include-deferred  # show all
    python manage.py audit_celery_zero_fire --include-direct-calls
"""
from __future__ import annotations

import inspect
import json
import re
import shutil
import subprocess
from datetime import timedelta
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


# Canonical task-discovery list — mirrors `core/tests/test_celery_queue_parity.py`
# setUp. Update both together when a new tasks_*.py module is added.
TASK_MODULES = (
    'core.tasks', 'core.tasks_agents', 'core.tasks_content',
    'core.tasks_spiders', 'core.tasks_financial', 'core.tasks_ops',
    'core.tasks_initiatives', 'core.tasks_misc',
    'core.tasks_conversations', 'core.tasks_body_systems',
    'core.tasks_media', 'core.tasks_executor',
    'core.tasks_push_notifications', 'core.celery',
    'ai_core.tasks', 'ai_core.spiders.tasks',
    'intelligence.tasks',
    'agents.tasks', 'agents.tasks_enhanced',
    'content.tasks',
    'pipelines.tasks',
    'sports.tasks',
    'ml.tasks',
)


# Deferred-by-policy task set, sourced from `docs/AUDIT_FINDINGS.md` #12
# (S1115 multi-batch Celery audit). Each task here was reviewed in that
# audit and intentionally left without a beat row pending the named
# constraint. When AUDIT_FINDINGS.md #12 evolves, update this set.
#
# Categories (informational; not enforced):
#   LLM_COST    — deferred until OpenAI credits / cost review
#   AGENT_CHAIN — deferred for green-light on agent-dispatch chain
#   S1031       — explicitly DISABLED comment, S1031 quarantine
#   NEVER_WIRED — "should-be-scheduled but never wired" per #12 line 882
KNOWN_DEFERRED = {
    # LLM_COST
    'core.tasks.rag_retrieval_canary',
    'core.tasks.send_weekly_kpi_summary',
    'core.tasks.run_ops_autopilot',
    'core.tasks.post_ops_digest',
    'core.tasks.maintain_knowledge_freshness',
    # AGENT_CHAIN
    'core.tasks.check_blocked_research_for_unblock',
    'intelligence.tasks.process_pending_action_plans',
    # S1031
    'core.tasks.assign_open_findings_to_agents',
    'core.tasks.discover_and_import_audits',
    # NEVER_WIRED (from #12 line 890-895 explicit examples)
    'core.tasks.aggregate_roi_metrics_daily',
    'core.tasks.calculate_daily_revenue_metrics',
    'core.tasks.check_learning_loop_slo',
    'core.tasks.claim_stale_events',
    'core.tasks.expire_old_opportunities',
    'core.tasks.expire_old_suggestions',
    'core.tasks.expire_overdue_validations',
    'core.tasks.maintain_dream_backlog',
    'core.tasks.post_coo_daily_diagnostic',
    'core.tasks.post_cto_daily_diagnostic',
    'core.tasks.post_trend_daily_diagnostic',
}


def _resolve_task_defsite(task_name: str) -> Path | None:
    """Best-effort lookup of the .py file where this Celery task is defined.

    Used to exclude the def-site from the direct-call probe — we want to
    count callers, not the function's own def line. Returns None on any
    inspection failure; the probe just treats every match as a caller in
    that case (slight overcount, never undercount).
    """
    try:
        from celery import current_app
        task_obj = current_app.tasks.get(task_name)
        if task_obj is None:
            return None
        run_fn = getattr(task_obj, 'run', None)
        if run_fn is None:
            return None
        source = inspect.getsourcefile(run_fn) or inspect.getfile(run_fn)
        return Path(source).resolve() if source else None
    except Exception:
        return None


def _count_direct_callers(task_name: str, repo_root: Path) -> dict[str, Any]:
    """Run ripgrep for `\\b<short>\\s*\\(` and return the caller-hit count.

    "Short name" is the last dotted segment (e.g., `core.tasks.foo` → `foo`).
    Hits in the def-site file are excluded so they don't count against the
    task itself. Hits in this audit command + the static-audit command are
    also excluded — both reference task short-names as data, not callers.

    Returns ``{'hits': int, 'sample': list[str], 'skipped': bool, 'reason': str}``.
    On any failure (rg not installed, malformed name, regex error) sets
    ``skipped=True`` so the caller can render a warning instead of a count.
    """
    short = task_name.rsplit('.', 1)[-1]
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', short):
        return {'hits': 0, 'sample': [], 'skipped': True, 'reason': 'name_not_identifier'}

    defsite = _resolve_task_defsite(task_name)

    # Exclude this audit cmd + the static caller-analysis cmd: they enumerate
    # task names as data and would inflate the hit count for every task.
    self_paths = {
        repo_root / 'core' / 'management' / 'commands' / 'audit_celery_zero_fire.py',
        repo_root / 'core' / 'management' / 'commands' / 'build_celery_audit.py',
    }

    try:
        result = subprocess.run(
            [
                'rg',
                '--type', 'py',
                '--no-heading',
                '--with-filename',
                '--line-number',
                '--no-messages',
                rf'\b{short}\s*\(',
                str(repo_root),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        return {'hits': 0, 'sample': [], 'skipped': True, 'reason': 'rg_not_found'}
    except subprocess.TimeoutExpired:
        return {'hits': 0, 'sample': [], 'skipped': True, 'reason': 'rg_timeout'}

    # rg exits 1 when there are zero matches — not an error for our purposes.
    if result.returncode not in (0, 1):
        return {'hits': 0, 'sample': [], 'skipped': True, 'reason': f'rg_exit_{result.returncode}'}

    hits: list[str] = []
    for line in result.stdout.splitlines():
        try:
            path_str, _lineno, content = line.split(':', 2)
        except ValueError:
            continue
        try:
            path = Path(path_str).resolve()
        except Exception:
            continue
        if defsite is not None and path == defsite:
            continue
        if path in self_paths:
            continue
        # Filter out the def line itself (defensive — covers the case where
        # _resolve_task_defsite returned None but the def is still in the
        # file we're scanning).
        if re.search(rf'\bdef\s+{re.escape(short)}\s*\(', content):
            continue
        hits.append(f'{path_str}:{_lineno}')

    return {
        'hits': len(hits),
        'sample': hits[:5],
        'skipped': False,
        'reason': '',
    }


class Command(BaseCommand):
    help = (
        'Audit Celery tasks that have not fired in the last N days, '
        'classified against the known-deferred set from AUDIT_FINDINGS.md #12.'
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--days', type=int, default=30,
            help='Telemetry window in days (default 30). Bounded by CeleryTaskEvent '
                 'retention (CELERY_TASK_EVENT_RETENTION_DAYS, default 30). If actual '
                 'telemetry history is shorter, the effective window is the shorter value.',
        )
        parser.add_argument(
            '--include-deferred', action='store_true',
            help='Include AUDIT_FINDINGS.md #12 deferred tasks in the output. '
                 'Default behavior filters them out so only NET-NEW orphans show.',
        )
        parser.add_argument(
            '--json', dest='as_json', action='store_true',
            help='Output JSON instead of human-readable table.',
        )
        parser.add_argument(
            '--include-direct-calls', action='store_true',
            help='For each uncategorized zero-fire task, run ripgrep '
                 'against the repo for direct Python calls (`\\b<short>\\s*\\(`), '
                 'excluding the task def-site. Adds a "direct callers" hit '
                 'count per task. S1245 surfaced a probe blind spot where a '
                 'zero-fire task with a single direct-Python caller in a mgmt '
                 'command looked deletable; this axis catches that case. '
                 'Requires `rg` on PATH; skipped with a warning otherwise.',
        )

    def handle(self, *args: Any, **opts: Any) -> None:
        # Trigger task discovery
        for module in TASK_MODULES:
            try:
                __import__(module)
            except Exception as exc:
                self.stderr.write(
                    self.style.WARNING(f'IMPORT_FAIL {module}: {type(exc).__name__}')
                )

        from celery import current_app
        from core.models import CeleryTaskEvent

        registered = {
            t for t in current_app.tasks.keys() if not t.startswith('celery.')
        }

        now = timezone.now()
        cutoff = now - timedelta(days=opts['days'])
        all_seen = set(
            CeleryTaskEvent.objects.filter(started_at__gte=cutoff)
            .values_list('task_name', flat=True)
            .distinct()
        )
        zero_fire = sorted(registered - all_seen)

        # Telemetry horizon — earliest row tells us if --days is effective.
        earliest = CeleryTaskEvent.objects.order_by('started_at').first()
        actual_window_days = (
            (now - earliest.started_at).days if earliest else 0
        )
        effective_days = min(opts['days'], actual_window_days)

        deferred_in_zero = sorted(set(zero_fire) & KNOWN_DEFERRED)
        uncategorized = sorted(set(zero_fire) - KNOWN_DEFERRED)

        # Session 1246 — 5th axis. Only run when explicitly asked; rg per
        # task adds 50-300ms each, and the default run shouldn't pay that
        # unless the operator is preparing a deletion PR.
        direct_call_report: dict[str, Any] = {}
        direct_call_skipped_reason = ''
        if opts['include_direct_calls']:
            if shutil.which('rg') is None:
                direct_call_skipped_reason = 'rg_not_on_path'
            else:
                repo_root = Path(settings.BASE_DIR).resolve()
                for task_name in uncategorized:
                    direct_call_report[task_name] = _count_direct_callers(task_name, repo_root)

        if opts['as_json']:
            self.stdout.write(json.dumps({
                'window_days_requested': opts['days'],
                'window_days_effective': effective_days,
                'telemetry_earliest': earliest.started_at.isoformat() if earliest else None,
                'registered': len(registered),
                'seen_in_window': len(all_seen),
                'zero_fire': len(zero_fire),
                'deferred_in_zero_fire': deferred_in_zero,
                'uncategorized_zero_fire': uncategorized,
                'direct_call_report': direct_call_report or None,
                'direct_call_skipped_reason': direct_call_skipped_reason or None,
            }, indent=2))
            return

        self.stdout.write(self.style.MIGRATE_HEADING(
            f'Celery zero-fire audit — window={opts["days"]}d '
            f'(effective={effective_days}d, telemetry from {earliest.started_at if earliest else "(empty)"})'
        ))
        self.stdout.write('')
        self.stdout.write(f'  registered                  : {len(registered)}')
        self.stdout.write(f'  seen_in_window              : {len(all_seen)}')
        self.stdout.write(f'  zero_fire                   : {len(zero_fire)}')
        self.stdout.write(f'  in AUDIT_FINDINGS #12 set   : {len(deferred_in_zero)}')
        self.stdout.write(
            f'  uncategorized (need lookup) : {len(uncategorized)}'
        )

        if effective_days < opts['days']:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(
                f'⚠  Effective window is {effective_days}d (less than requested {opts["days"]}d).'
            ))
            self.stdout.write(self.style.WARNING(
                '   CeleryTaskEvent telemetry has not accumulated long enough yet.'
            ))
            self.stdout.write(self.style.WARNING(
                '   Re-run after retention period (CELERY_TASK_EVENT_RETENTION_DAYS) elapses.'
            ))

        self.stdout.write('')
        self.stdout.write(self.style.WARNING(
            'IMPORTANT — interpretation rules:'
        ))
        self.stdout.write(
            '  • "zero_fire" means "no CeleryTaskEvent row in window" — NOT "orphan".'
        )
        self.stdout.write(
            '  • A task can be zero-fire because: (a) deferred-by-policy [see #12],'
        )
        self.stdout.write(
            '    (b) fired before the telemetry retention window started,'
        )
        self.stdout.write(
            '    (c) only fires on rare external triggers (webhooks/HITL/CLI),'
        )
        self.stdout.write(
            '    (d) genuinely orphan (no callers, no schedule).'
        )
        self.stdout.write(
            '  • To distinguish (c) vs (d), run: python manage.py build_celery_audit'
        )
        self.stdout.write(
            '    and check the per-task callers column in docs/CELERY_AUDIT.md.'
        )
        self.stdout.write(
            '  • A task with zero callers AND zero fires AND not in KNOWN_DEFERRED'
        )
        self.stdout.write(
            '    is a candidate orphan. Verify direct-Python-call references with'
        )
        self.stdout.write(
            '    `rg "\\b<short_name>\\s*\\("` before any cleanup PR.'
        )

        if opts['include_deferred']:
            self.stdout.write('')
            self.stdout.write(self.style.MIGRATE_HEADING(
                f'=== Deferred-by-policy zero-fire (AUDIT_FINDINGS.md #12): {len(deferred_in_zero)} ==='
            ))
            for t in deferred_in_zero:
                self.stdout.write(f'  {t}')

        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING(
            f'=== Uncategorized zero-fire (not in #12 set): {len(uncategorized)} ==='
        ))
        self.stdout.write(
            '(Most of these have static callers — see docs/CELERY_AUDIT.md to confirm.)'
        )
        if opts['include_direct_calls']:
            if direct_call_skipped_reason:
                self.stdout.write(self.style.WARNING(
                    f'⚠  Direct-call axis skipped: {direct_call_skipped_reason}'
                ))
            else:
                self.stdout.write(
                    self.style.NOTICE(
                        'Direct-call hit column shows non-def-site, non-self-audit '
                        'matches of `\\b<short>\\s*\\(` in *.py. Non-zero ⇒ unsafe '
                        'to delete without deeper review.'
                    )
                )
        for t in uncategorized:
            if opts['include_direct_calls']:
                rep = direct_call_report.get(t, {})
                if rep.get('skipped'):
                    suffix = f' direct=SKIPPED ({rep.get("reason", "?")})'
                else:
                    suffix = f' direct={rep.get("hits", 0)}'
            else:
                suffix = ''
            self.stdout.write(f'  {t}{suffix}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            'Cross-reference: docs/AUDIT_FINDINGS.md §12 + docs/CELERY_AUDIT.md'
        ))
        self.stdout.write(self.style.SUCCESS(
            'Companion audit: `python manage.py build_celery_audit` (static caller analysis)'
        ))
