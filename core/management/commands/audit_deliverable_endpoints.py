"""
Audit deliverable_tool.list vs content_tool.content_recent for shape + count drift.

Session 1194 — AC1 of docs/specs/INITIATIVES_FIRST_BACKBONE.md. Surfaces the
divergence that Plan A's field-projection fix closed, and acts as an ongoing
drift detector. Both endpoints SHOULD return the same row shape and (modulo
documented filter differences) the same row counts when given the same
workspace_id + time window.

Usage:
    python manage.py audit_deliverable_endpoints --workspace <uuid>
    python manage.py audit_deliverable_endpoints --workspace <uuid> --days 30
    python manage.py audit_deliverable_endpoints --workspace <uuid> --fail-on-drift
    python manage.py audit_deliverable_endpoints --workspace <uuid> --json

Exit codes:
    0 — both endpoints agree (within expected band)
    1 — drift detected (with --fail-on-drift)
"""

import json
import sys
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models_deliverables import Deliverable

# Expected field shape — Session 1194 Plan A fix. Both endpoints
# project these via .values(); if either drops one, we drifted.
EXPECTED_FIELDS = {
    'id', 'title', 'deliverable_type', 'category',
    'agent_name', 'quality_score', 'created_at', 'status',
    'initiative_id', 'workspace_id',
}


class Command(BaseCommand):
    help = (
        'Audit deliverable_tool.list vs content_tool.content_recent for shape + '
        'count drift on a given workspace. AC1 of INITIATIVES_FIRST_BACKBONE.md.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--workspace', type=str, required=True,
            help='Workspace UUID to audit (e.g. b4503364-2573-4401-9e28-61a739e0ce50 for Donkey Betz)',
        )
        parser.add_argument(
            '--days', type=int, default=30,
            help='Time window for content_recent (default: 30)',
        )
        parser.add_argument(
            '--fail-on-drift', action='store_true',
            help='Exit 1 if either endpoint drops expected fields or counts diverge beyond band',
        )
        parser.add_argument(
            '--json', action='store_true',
            help='Emit JSON instead of human-readable text',
        )

    def handle(self, *args, **options):
        workspace_id = options['workspace']
        days = options['days']
        fail_on_drift = options['fail_on_drift']
        as_json = options['json']

        report = self._build_report(workspace_id, days)

        if as_json:
            self.stdout.write(json.dumps(report, indent=2, default=str))
        else:
            self._print_report(report)

        if fail_on_drift and report['drift_detected']:
            sys.exit(1)

    def _build_report(self, workspace_id, days):
        """Run the two endpoints + ORM baseline and compute drift."""
        from core.services.tool_dispatcher import ToolDispatcher

        since = timezone.now() - timedelta(days=days)

        # Ground truth — direct ORM count
        orm_count_workspace_all = Deliverable.objects.filter(
            workspace_id=workspace_id,
        ).count()
        orm_count_workspace_window = Deliverable.objects.filter(
            workspace_id=workspace_id,
            created_at__gte=since,
        ).count()

        # Dispatch both PA-tool paths via the canonical ToolDispatcher.execute_sync.
        # user_id=None — staff/PA-equivalent path; workspace filter is authoritative
        # See _handle_deliverables comment at td_handlers_agents.py:1529.
        dispatcher = ToolDispatcher()
        deliverable_tr = dispatcher.execute_sync(
            tool_name='deliverable_tool',
            payload={'action': 'list', 'workspace_id': workspace_id, 'limit': 200},
            user_id=None,
        )
        content_tr = dispatcher.execute_sync(
            tool_name='content_tool',
            payload={
                'action': 'content_recent',
                'workspace_id': workspace_id,
                'days': days,
                'limit': 200,
            },
            user_id=None,
        )

        deliverable_payload = deliverable_tr.result if (deliverable_tr.ok and isinstance(deliverable_tr.result, dict)) else {}
        content_payload = content_tr.result if (content_tr.ok and isinstance(content_tr.result, dict)) else {}

        deliverable_items = deliverable_payload.get('items', []) or []
        content_items = content_payload.get('items', []) or []
        deliverable_total = deliverable_payload.get('total', len(deliverable_items))
        content_count = content_payload.get('count', len(content_items))

        # Shape audit — which expected fields appear on the first row of each?
        def _fields_of(items):
            if not items:
                return set()
            return set(items[0].keys())

        deliverable_fields = _fields_of(deliverable_items)
        content_fields = _fields_of(content_items)

        deliverable_missing = EXPECTED_FIELDS - deliverable_fields
        content_missing = EXPECTED_FIELDS - content_fields

        # Workspace-filter honor check — every row's workspace_id should match
        def _wrong_workspace_count(items):
            return sum(
                1 for it in items
                if str(it.get('workspace_id', '')) != workspace_id
            )

        deliverable_off_workspace = _wrong_workspace_count(deliverable_items)
        content_off_workspace = _wrong_workspace_count(content_items)

        # Drift detection
        drift_reasons = []
        if deliverable_missing:
            drift_reasons.append(f"deliverable_tool.list missing fields: {sorted(deliverable_missing)}")
        if content_missing:
            drift_reasons.append(f"content_tool.content_recent missing fields: {sorted(content_missing)}")
        if deliverable_off_workspace:
            drift_reasons.append(f"deliverable_tool.list returned {deliverable_off_workspace} off-workspace rows")
        if content_off_workspace:
            drift_reasons.append(f"content_tool.content_recent returned {content_off_workspace} off-workspace rows")

        # Count expectation: deliverable_tool.list (all-time) should match ORM
        # workspace count; content_tool.content_recent (windowed) should match
        # ORM windowed count. ±5 row band for in-flight inserts during audit.
        TOLERANCE = 5
        if abs(deliverable_total - orm_count_workspace_all) > TOLERANCE:
            drift_reasons.append(
                f"deliverable_tool.list total ({deliverable_total}) diverges from "
                f"ORM workspace count ({orm_count_workspace_all}) beyond ±{TOLERANCE}"
            )
        if abs(content_count - orm_count_workspace_window) > TOLERANCE:
            drift_reasons.append(
                f"content_tool.content_recent count ({content_count}) diverges from "
                f"ORM workspace+window count ({orm_count_workspace_window}) beyond ±{TOLERANCE}"
            )

        return {
            'workspace_id': workspace_id,
            'days': days,
            'orm_count_workspace_all': orm_count_workspace_all,
            'orm_count_workspace_window': orm_count_workspace_window,
            'deliverable_tool_list': {
                'total': deliverable_total,
                'returned': len(deliverable_items),
                'fields': sorted(deliverable_fields),
                'missing_fields': sorted(deliverable_missing),
                'off_workspace_rows': deliverable_off_workspace,
            },
            'content_tool_content_recent': {
                'count': content_count,
                'returned': len(content_items),
                'fields': sorted(content_fields),
                'missing_fields': sorted(content_missing),
                'off_workspace_rows': content_off_workspace,
            },
            'drift_detected': bool(drift_reasons),
            'drift_reasons': drift_reasons,
        }

    def _print_report(self, report):
        out = self.stdout.write
        out(f"\nWorkspace: {report['workspace_id']}")
        out(f"Time window: last {report['days']}d\n")

        out(f"ORM baseline:")
        out(f"  workspace (all-time):  {report['orm_count_workspace_all']}")
        out(f"  workspace + {report['days']}d window: {report['orm_count_workspace_window']}\n")

        d = report['deliverable_tool_list']
        out(f"deliverable_tool.list:")
        out(f"  total / returned: {d['total']} / {d['returned']}")
        out(f"  off-workspace rows: {d['off_workspace_rows']}")
        if d['missing_fields']:
            out(self.style.WARNING(f"  missing fields: {d['missing_fields']}"))
        else:
            out(self.style.SUCCESS(f"  field shape: complete"))

        c = report['content_tool_content_recent']
        out(f"\ncontent_tool.content_recent:")
        out(f"  count / returned: {c['count']} / {c['returned']}")
        out(f"  off-workspace rows: {c['off_workspace_rows']}")
        if c['missing_fields']:
            out(self.style.WARNING(f"  missing fields: {c['missing_fields']}"))
        else:
            out(self.style.SUCCESS(f"  field shape: complete"))

        out("")
        if report['drift_detected']:
            out(self.style.ERROR("DRIFT DETECTED:"))
            for r in report['drift_reasons']:
                out(f"  - {r}")
        else:
            out(self.style.SUCCESS("OK — endpoints agree on shape + counts."))
