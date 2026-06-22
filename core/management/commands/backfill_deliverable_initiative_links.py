"""Session 1195 — Plan C Phase 1: Initiative-link backfill recon.

Quantitative report over real deliverable data answering:

  - how many rows are missing initiative_id and/or workspace_id
  - how many are mismatched against initiative.target_workspace_id
  - what would happen under each candidate §6.2 inference rule

Default is **read-only** (no writes). ``--apply`` is reserved for a
later phase once Chris ratifies a specific inference rule; without
``--apply`` the command computes counts + simulation only.

Output:
  - Human-readable summary table
  - JSON blob for copy-paste into the §6.2 decision doc

Usage:

  # Default — recon over all deliverables
  python manage.py backfill_deliverable_initiative_links

  # Scope by workspace
  python manage.py backfill_deliverable_initiative_links \\
      --workspace-id b4503364-2573-4401-9e28-61a739e0ce50

  # Scope by recency (ISO date or datetime)
  python manage.py backfill_deliverable_initiative_links --since 2026-05-01

  # Show sample IDs per bucket (for follow-up via deliverable_tool.detail)
  python manage.py backfill_deliverable_initiative_links --sample 5

  # Emit JSON for piping into a decision doc / dashboard
  python manage.py backfill_deliverable_initiative_links --json-only

Spec: docs/specs/INITIATIVES_FIRST_BACKBONE.md §3.C / §6.2.
"""

import json
from collections import Counter, defaultdict

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils.dateparse import parse_datetime, parse_date


TOP_N = 10


class Command(BaseCommand):
    help = (
        "Read-only recon over deliverables to quantify Initiative-link "
        "drift and simulate §6.2 inference rules. Default writes nothing."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help=(
                "Reserved for a later phase once a specific inference rule "
                "is ratified. Currently a no-op safety stub — printing a "
                "warning if set. Defaults to read-only recon."
            ),
        )
        parser.add_argument(
            '--workspace-id', type=str, default=None,
            help="Restrict recon to a single workspace UUID.",
        )
        parser.add_argument(
            '--since', type=str, default=None,
            help=(
                "Only inspect deliverables with created_at >= <since>. "
                "Accepts ISO date (YYYY-MM-DD) or datetime."
            ),
        )
        parser.add_argument(
            '--limit', type=int, default=0,
            help="Max rows to inspect (0 = no limit; default 0).",
        )
        parser.add_argument(
            '--offset', type=int, default=0,
            help="Skip first N rows (chunked runs; default 0).",
        )
        parser.add_argument(
            '--sample', type=int, default=0,
            help="Print N sample deliverable IDs per bucket (default 0).",
        )
        parser.add_argument(
            '--json-only', action='store_true',
            help="Emit only the JSON blob (no human-readable table).",
        )

    def handle(self, *args, **opts):
        from core.models_deliverables import Deliverable
        from core.models_document_registry import Initiative

        if opts['apply']:
            self.stderr.write(self.style.WARNING(
                "--apply is a no-op stub in Phase 1; ignored. The recon "
                "below is the input for the §6.2 inference-rule decision."
            ))

        # ── Build the scoped queryset ───────────────────────────────────
        qs = Deliverable.objects.all()

        if opts['workspace_id']:
            qs = qs.filter(workspace_id=opts['workspace_id'])

        if opts['since']:
            dt = parse_datetime(opts['since']) or parse_date(opts['since'])
            if dt is None:
                self.stderr.write(self.style.ERROR(
                    f"--since: could not parse {opts['since']!r}"
                ))
                return
            qs = qs.filter(created_at__gte=dt)

        # Ordering for deterministic chunked runs
        qs = qs.order_by('created_at')

        if opts['offset']:
            qs = qs[opts['offset']:]
        if opts['limit']:
            qs = qs[:opts['limit']]

        # ── Pre-compute the active-initiative workspace map ─────────────
        # Used for the inference simulation. Each ACTIVE initiative with
        # a target_workspace_id contributes a (workspace_id, initiative_id)
        # candidate. workspaces with multiple candidates are ambiguous.
        initiative_qs = (
            Initiative.objects
            .filter(status='ACTIVE', target_workspace_id__isnull=False)
            .values('id', 'name', 'target_workspace_id')
        )
        ws_to_initiatives = defaultdict(list)
        for init in initiative_qs:
            ws_to_initiatives[str(init['target_workspace_id'])].append({
                'id': str(init['id']),
                'name': init['name'],
            })

        # Spine "Initiatives-First Wiring + No-Orphan Output" — used as
        # Rule 2 fallback when workspace-exact has zero matches AND the
        # deliverable lives in the Donkey Betz workspace. Looked up by
        # name (no hardcoded UUID) so the simulation stays portable.
        spine_initiative = (
            Initiative.objects
            .filter(name__icontains='Initiatives-First Wiring', status='ACTIVE')
            .values('id', 'target_workspace_id')
            .first()
        )
        spine_ws_id = (
            str(spine_initiative['target_workspace_id'])
            if spine_initiative and spine_initiative['target_workspace_id']
            else None
        )
        spine_init_id = str(spine_initiative['id']) if spine_initiative else None

        # ── Walk the queryset and bucket ────────────────────────────────
        # Stream rows via iterator() so we don't blow memory on large
        # scans (no chunked .objects.all().iterator() materializes >100k
        # rows in RAM either).
        rows_iter = qs.values(
            'id', 'agent_name', 'workspace_id', 'initiative_id',
            'deliverable_type', 'category',
            # joined initiative.target_workspace_id (single SELECT JOIN)
            'initiative__target_workspace_id',
        ).iterator(chunk_size=500)

        total = 0
        missing_initiative_ids: list = []
        missing_workspace_ids: list = []
        workspace_mismatch_ids: list = []
        initiative_missing_target_ws_ids: list = []
        aligned = 0

        # Breakdowns (top-N per bucket)
        agent_buckets = {
            'missing_initiative_id': Counter(),
            'missing_workspace_id': Counter(),
            'workspace_mismatch': Counter(),
        }
        workspace_buckets = {
            'missing_initiative_id': Counter(),
            'workspace_mismatch': Counter(),
        }
        type_buckets = {
            'missing_initiative_id': Counter(),
            'workspace_mismatch': Counter(),
        }

        # Inference simulation (per-rule counters)
        infer = {
            'rule1_workspace_exact': {'assignable': 0, 'ambiguous': 0, 'unassignable': 0},
            'rule2_spine_fallback': {'assignable': 0, 'ambiguous': 0, 'unassignable': 0},
            'rule3_require_explicit': {'assignable': 0, 'ambiguous': 0, 'unassignable': 0},
        }
        sample_per_bucket = max(0, opts['sample'])
        samples = defaultdict(list)

        def _add_sample(bucket, row_id):
            if sample_per_bucket and len(samples[bucket]) < sample_per_bucket:
                samples[bucket].append(str(row_id))

        for row in rows_iter:
            total += 1
            agent = row['agent_name'] or '<none>'
            ws_id = str(row['workspace_id']) if row['workspace_id'] else None
            init_id = str(row['initiative_id']) if row['initiative_id'] else None
            target_ws = (
                str(row['initiative__target_workspace_id'])
                if row['initiative__target_workspace_id']
                else None
            )

            if not ws_id:
                missing_workspace_ids.append(row['id'])
                agent_buckets['missing_workspace_id'][agent] += 1
                _add_sample('missing_workspace_id', row['id'])

            if not init_id:
                missing_initiative_ids.append(row['id'])
                agent_buckets['missing_initiative_id'][agent] += 1
                workspace_buckets['missing_initiative_id'][ws_id or '<none>'] += 1
                type_buckets['missing_initiative_id'][row['deliverable_type'] or '<none>'] += 1
                _add_sample('missing_initiative_id', row['id'])

                # Inference simulation only runs on missing-initiative rows.
                candidates = ws_to_initiatives.get(ws_id, [])
                # Rule 1 — workspace exact match
                if len(candidates) == 1:
                    infer['rule1_workspace_exact']['assignable'] += 1
                elif len(candidates) > 1:
                    infer['rule1_workspace_exact']['ambiguous'] += 1
                else:
                    infer['rule1_workspace_exact']['unassignable'] += 1

                # Rule 2 — Rule 1, with spine fallback when zero matches
                # AND deliverable lives in the spine's target workspace.
                if len(candidates) == 1:
                    infer['rule2_spine_fallback']['assignable'] += 1
                elif len(candidates) > 1:
                    infer['rule2_spine_fallback']['ambiguous'] += 1
                else:
                    if spine_init_id and ws_id and ws_id == spine_ws_id:
                        infer['rule2_spine_fallback']['assignable'] += 1
                    else:
                        infer['rule2_spine_fallback']['unassignable'] += 1

                # Rule 3 — always unassignable (baseline)
                infer['rule3_require_explicit']['unassignable'] += 1

            elif init_id and target_ws is None:
                initiative_missing_target_ws_ids.append(row['id'])
                _add_sample('initiative_missing_target_workspace', row['id'])
            elif init_id and target_ws and ws_id != target_ws:
                workspace_mismatch_ids.append(row['id'])
                agent_buckets['workspace_mismatch'][agent] += 1
                workspace_buckets['workspace_mismatch'][ws_id or '<none>'] += 1
                type_buckets['workspace_mismatch'][row['deliverable_type'] or '<none>'] += 1
                _add_sample('workspace_mismatch', row['id'])
            else:
                aligned += 1

        # ── Assemble report ─────────────────────────────────────────────
        report = {
            'mode': 'dry-run' if not opts['apply'] else 'apply-noop',
            'filters': {
                'workspace_id': opts['workspace_id'],
                'since': opts['since'],
                'limit': opts['limit'] or None,
                'offset': opts['offset'] or None,
            },
            'totals': {
                'scanned': total,
                'aligned': aligned,
                'missing_initiative_id': len(missing_initiative_ids),
                'missing_workspace_id': len(missing_workspace_ids),
                'workspace_mismatch': len(workspace_mismatch_ids),
                'initiative_missing_target_workspace': len(initiative_missing_target_ws_ids),
            },
            'top_agents': {
                k: dict(c.most_common(TOP_N)) for k, c in agent_buckets.items()
            },
            'top_workspaces': {
                k: dict(c.most_common(TOP_N)) for k, c in workspace_buckets.items()
            },
            'top_types': {
                k: dict(c.most_common(TOP_N)) for k, c in type_buckets.items()
            },
            'inference_simulation': infer,
            'samples': {k: v for k, v in samples.items()} if sample_per_bucket else {},
            'spine_initiative_id': spine_init_id,
            'spine_target_workspace_id': spine_ws_id,
        }

        if opts['json_only']:
            self.stdout.write(json.dumps(report, indent=2, default=str))
            return

        # Human-readable table
        out = self.stdout
        out.write(self.style.SUCCESS(
            f"\n=== Initiative-link recon — scanned {total} deliverables "
            f"(mode: {report['mode']}) ===\n"
        ))

        out.write("Filters:")
        for k, v in report['filters'].items():
            out.write(f"  {k}: {v}")

        out.write("\nTotals:")
        t = report['totals']
        out.write(f"  aligned (no diagnostic needed): {t['aligned']}")
        out.write(f"  missing_initiative_id:          {t['missing_initiative_id']}")
        out.write(f"  missing_workspace_id:           {t['missing_workspace_id']}")
        out.write(f"  workspace_mismatch:             {t['workspace_mismatch']}")
        out.write(f"  initiative_missing_target_ws:   {t['initiative_missing_target_workspace']}")

        out.write("\nInference simulation (over missing_initiative_id rows):")
        for rule, counts in report['inference_simulation'].items():
            total_for_rule = sum(counts.values())
            assignable_pct = (counts['assignable'] * 100 / total_for_rule) if total_for_rule else 0
            out.write(
                f"  {rule}:  assignable={counts['assignable']} "
                f"ambiguous={counts['ambiguous']} unassignable={counts['unassignable']} "
                f"({assignable_pct:.0f}% assignable)"
            )

        for bucket_name, top_dict in report['top_agents'].items():
            if top_dict:
                out.write(f"\nTop agents for {bucket_name}:")
                for name, n in top_dict.items():
                    out.write(f"  {n:6d}  {name}")

        for bucket_name, top_dict in report['top_workspaces'].items():
            if top_dict:
                out.write(f"\nTop workspaces for {bucket_name}:")
                for ws, n in top_dict.items():
                    out.write(f"  {n:6d}  {ws}")

        if sample_per_bucket and report['samples']:
            out.write("\nSample IDs per bucket:")
            for bucket, ids in report['samples'].items():
                out.write(f"  {bucket}: {ids}")

        out.write("\n--- JSON blob (copy into §6.2 decision doc) ---")
        out.write(json.dumps(report, indent=2, default=str))
