"""S3039 D10 Phase 1 — LLMCallLog workspace-attribution gap audit.

Answers the question the S3037 Reliability Audit surfaced: of the
34,049 LLMCallLog rows in the 30d window with `workspace IS NULL`,
which are *legitimately* system-level (no user context available at
call time) vs which are code-path bugs (workspace context was
present but got dropped by the caller)?

The S3037 backlog framed D10 as "reporting quality, not runtime
correctness." Phase 0 (ORM probe during S3039) surfaced that the
NULL bucket includes ~6,177 `conversation × PersonalAssistant` rows
alongside ~5,995 correctly-attributed PA rows — a ~50/50 split of
Rigby calls losing workspace attribution. That's not reporting
quality; that's a code path dropping context. Phase 1 (this command)
classifies rows so the code-path bug is visible without ad-hoc ORM
spelunking, and future runs catch new drift.

Buckets:

- ``system_embedding`` — task_type='embedding' from a known system
  caller (SpiderSemanticSearch, docs_index_sync,
  MemoryEmbeddingService, KnowledgeFirstRouter,
  SemanticDriftDetector, `system`, `scoped_retrieval`,
  `rag_integration`, `conversation_tool`). NULL is CORRECT — these
  callers have no user context by design.
- ``system_test`` — task_type='test'. Test / dev traffic; NULL is
  acceptable (historical dev data).
- ``pa_workspace_lost`` — task_type='conversation' AND
  agent_name='PersonalAssistant'. **FLAGGED** — PA calls normally
  carry a user, so NULL workspace signals a code path that dropped
  the context. Compare against attributed PA rows (workspace NOT
  NULL) for the split.
- ``unclassified`` — everything else. Needs manual triage. Zero-count
  on a clean run.

Output is human-readable by default, JSON via ``--json``. Read-only —
no writes to LLMCallLog. The paired backfill command (D10 Phase 2, if
ever needed) would consume this classification.

Run::

    python manage.py audit_llmcalllog_workspace_gaps
    python manage.py audit_llmcalllog_workspace_gaps --window-days 7
    python manage.py audit_llmcalllog_workspace_gaps --json
"""
from __future__ import annotations

import json
from datetime import timedelta
from typing import Any, Dict

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone


# System-caller agent_names for the `embedding` task_type. These callers
# execute outside any user request context — e.g. Celery beat tasks that
# rebuild embeddings for RAG. NULL workspace is expected and correct.
SYSTEM_EMBEDDING_AGENTS = frozenset({
    'SpiderSemanticSearch',
    'docs_index_sync',
    'MemoryEmbeddingService',
    'KnowledgeFirstRouter',
    'SemanticDriftDetector',
    'system',
    'scoped_retrieval',
    'rag_integration',
    'conversation_tool',
})


def _classify(task_type: str, agent_name: str) -> str:
    """Bucket a NULL-workspace LLMCallLog row by (task_type, agent_name).

    Rigby SIGN ask #1: `task_type == 'embedding'` is treated as
    system-level regardless of agent_name — the callers of the
    embedding path are all Celery beat tasks or RAG helpers that run
    outside a user request. The allowlist above is retained as
    documentation of the currently-known callers; new callers that
    appear in a future window still bucket correctly (and their exact
    `agent_name` surfaces in `top_pairs` for review), so we don't
    false-positive them into `unclassified` just because they're new.
    """
    if task_type == 'embedding':
        return 'system_embedding'
    if task_type == 'test':
        return 'system_test'
    if task_type == 'conversation' and agent_name == 'PersonalAssistant':
        return 'pa_workspace_lost'
    return 'unclassified'


class Command(BaseCommand):
    help = (
        "Audit LLMCallLog rows with NULL workspace attribution. "
        "Classifies the NULL bucket into legitimate system-level rows "
        "vs code-path bugs (PA workspace loss). Read-only diagnostic."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--window-days',
            type=int,
            default=30,
            help='Lookback window in days (default 30).',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Emit machine-readable JSON instead of human text.',
        )

    def handle(self, *args, **options):
        from core.models_llm_routing import LLMCallLog

        window_days = options['window_days']
        as_json = options['json']

        cutoff = timezone.now() - timedelta(days=window_days)
        window_qs = LLMCallLog.objects.filter(created_at__gte=cutoff)

        total = window_qs.count()
        attributed_qs = window_qs.filter(workspace__isnull=False)
        null_qs = window_qs.filter(workspace__isnull=True)
        attributed_n = attributed_qs.count()
        null_n = null_qs.count()

        # Classify NULL rows by (task_type, agent_name). Do the cross-tab
        # in the DB, then bucket in Python — avoids pulling 34k rows.
        crosstab = list(
            null_qs.values('task_type', 'agent_name').annotate(
                n=Count('id'),
            ).order_by('-n')
        )

        buckets: Dict[str, Dict[str, Any]] = {
            'system_embedding': {'count': 0, 'pairs': []},
            'system_test': {'count': 0, 'pairs': []},
            'pa_workspace_lost': {'count': 0, 'pairs': []},
            'unclassified': {'count': 0, 'pairs': []},
        }
        for row in crosstab:
            bucket = _classify(row['task_type'] or '', row['agent_name'] or '')
            buckets[bucket]['count'] += row['n']
            buckets[bucket]['pairs'].append({
                'task_type': row['task_type'] or '',
                'agent_name': row['agent_name'] or '',
                'count': row['n'],
            })

        # PA split — flagged finding companion metric. Compare NULL PA
        # rows to attributed PA rows so the 50/50 gap surfaces at-a-glance.
        pa_null = buckets['pa_workspace_lost']['count']
        pa_attributed = attributed_qs.filter(
            task_type='conversation', agent_name='PersonalAssistant',
        ).count()
        pa_total = pa_null + pa_attributed
        pa_loss_pct = (pa_null / pa_total * 100) if pa_total else 0.0

        payload = {
            'window_days': window_days,
            'total_rows': total,
            'attributed_rows': attributed_n,
            'null_rows': null_n,
            'attributed_pct': round(attributed_n / total * 100, 2) if total else 0.0,
            'null_pct': round(null_n / total * 100, 2) if total else 0.0,
            'buckets': {
                name: {
                    'count': data['count'],
                    'pct_of_null': (
                        round(data['count'] / null_n * 100, 2) if null_n else 0.0
                    ),
                    'top_pairs': data['pairs'][:5],
                }
                for name, data in buckets.items()
            },
            'flagged_findings': [],
        }

        # Flag PA workspace loss when NULL PA rows are non-trivial. The
        # 50/50 split threshold catches the S3039 D10 finding without
        # false-positiving on a session where PA barely fired.
        if pa_null >= 100 or (pa_total >= 100 and pa_loss_pct >= 10):
            payload['flagged_findings'].append({
                'severity': 'HIGH',
                'code': 'pa_workspace_attribution_loss',
                'null_count': pa_null,
                'attributed_count': pa_attributed,
                'loss_pct': round(pa_loss_pct, 2),
                'message': (
                    f'PersonalAssistant workspace attribution loss: '
                    f'{pa_null} NULL vs {pa_attributed} attributed '
                    f'({pa_loss_pct:.1f}% of PA calls in window). '
                    'PA callers normally carry a user; NULL workspace '
                    'signals a code path dropping the context. '
                    'Grep unified_pa_entrypoint.py + workspace_resolver.py '
                    'for missing user threading. '
                    # S3039 D10-follow: user-threading fix shipped for 4
                    # direct `self.llm_enforcer.enforce_real_ai` sites in
                    # unified_pa_entrypoint.py. Historical windows still
                    # contain pre-fix rows; expect loss_pct to trend to 0
                    # for windows entirely after the D10-follow ship.
                    # If loss_pct stays high on a post-ship window, a new
                    # regression opened — grep for direct enforce_real_ai
                    # calls missing user= per the S3039 lint test.
                    '(D10-follow fix shipped; pre-fix rows persist in '
                    'historical windows.)'
                ),
            })

        if as_json:
            self.stdout.write(json.dumps(payload, indent=2, default=str))
            return

        self._print_human(payload)

    def _print_human(self, payload: Dict[str, Any]) -> None:
        w = self.stdout.write

        w(self.style.NOTICE(
            f"\n=== LLMCallLog workspace-attribution audit "
            f"({payload['window_days']}d window) ===\n"
        ))
        w(f"Total rows:      {payload['total_rows']:>7,}")
        w(f"Attributed:      {payload['attributed_rows']:>7,} "
          f"({payload['attributed_pct']}%)")
        w(f"NULL workspace:  {payload['null_rows']:>7,} "
          f"({payload['null_pct']}%)")

        w("\n--- NULL bucket classification ---")
        for name, data in payload['buckets'].items():
            style = self.style.SUCCESS
            if name == 'pa_workspace_lost' and data['count']:
                style = self.style.WARNING
            elif name == 'unclassified' and data['count']:
                style = self.style.ERROR
            label = style(f"{name:>20s}")
            w(f"  {label}: {data['count']:>6,} rows ({data['pct_of_null']}% of NULL)")
            for pair in data['top_pairs'][:3]:
                w(f"      {pair['task_type']:<20s} × {pair['agent_name']:<35s} {pair['count']:>6,}")

        if payload['flagged_findings']:
            w(self.style.WARNING("\n--- FLAGGED FINDINGS ---"))
            for finding in payload['flagged_findings']:
                w(self.style.WARNING(
                    f"  [{finding['severity']}] {finding['code']}"
                ))
                w(f"    {finding['message']}")
        else:
            w(self.style.SUCCESS("\nNo flagged findings."))
