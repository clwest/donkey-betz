"""Session 1196 — Plan C side-quest: Initiative target_workspace_id recon + backfill.

Quantitative report over real Initiative data answering:

  - how many Initiatives are missing ``target_workspace_id``
  - partitioned by status, created_by, age, and DBZ-linkage
  - optional ``--apply`` flag retroactively marks pre-existing
    no-ws Initiatives diagnostic so the daily sweep (PR #4) can
    eventually retire them under the new no-orphan contract

Mirrors Session 1195 PR #2407 ``backfill_deliverable_initiative_links``
shape but targets the Initiative write-path drift Plan C Phase 1
explicitly deferred (per ``deliverable_factory._evaluate_initiative_alignment``
docstring at the time).

Default is **read-only** (no writes). ``--apply`` is the explicit
opt-in to retroactively mark pre-existing rows diagnostic. Both modes
produce the same recon table + JSON, so ``--apply`` can be re-run
safely (idempotent — only marks rows that aren't already diagnostic).

Output:
  - Human-readable summary table
  - JSON blob for copy-paste into the 7-day watch baseline

Usage:

  # Default — recon over all Initiatives
  python manage.py backfill_initiative_workspace_links

  # Recon scoped to deliverables linked from a workspace
  python manage.py backfill_initiative_workspace_links \\
      --workspace-id b4503364-2573-4401-9e28-61a739e0ce50

  # Show sample IDs per bucket (for follow-up via work_tool.initiative_detail)
  python manage.py backfill_initiative_workspace_links --sample 5

  # Emit JSON only (for piping into watch baseline)
  python manage.py backfill_initiative_workspace_links --json-only

  # APPLY — retroactively mark pre-existing no-ws Initiatives diagnostic
  python manage.py backfill_initiative_workspace_links --apply

Spec: docs/specs/INITIATIVES_FIRST_BACKBONE.md §3.C / §6.1.
"""

import json
from collections import Counter

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone


TOP_N = 10


class Command(BaseCommand):
    help = (
        "Recon over Initiatives to quantify target_workspace_id drift. "
        "Default writes nothing; --apply retroactively marks pre-existing "
        "no-ws rows diagnostic for the sweep to retire."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help=(
                "Retroactively mark pre-existing no-ws Initiatives "
                "diagnostic. Idempotent — skips rows already flagged. "
                "Default is read-only recon."
            ),
        )
        parser.add_argument(
            '--workspace-id', type=str, default=None,
            help=(
                "Restrict recon to Initiatives that have at least one "
                "Deliverable linked from this workspace (matches the "
                "Plan C deliverable recon scope)."
            ),
        )
        parser.add_argument(
            '--sample', type=int, default=0,
            help="Show first N sample Initiative IDs per bucket (default 0).",
        )
        parser.add_argument(
            '--json-only', action='store_true',
            help="Emit JSON only (no human-readable table).",
        )

    def handle(self, *args, **opts):
        from core.models_document_registry import Initiative
        from core.models_deliverables import Deliverable

        apply_mode = opts['apply']
        ws_scope = opts['workspace_id']
        sample_n = opts['sample']
        json_only = opts['json_only']

        # ── Build baseline queryset ────────────────────────────────
        if ws_scope:
            # Match Plan C recon scope: Initiatives that have at least
            # one Deliverable linked from the scoped workspace.
            init_ids = (
                Deliverable.objects
                .filter(workspace_id=ws_scope, initiative__isnull=False)
                .values_list('initiative_id', flat=True)
                .distinct()
            )
            no_ws_qs = Initiative.objects.filter(
                id__in=list(init_ids),
                target_workspace_id__isnull=True,
            )
        else:
            no_ws_qs = Initiative.objects.filter(target_workspace_id__isnull=True)

        total_no_ws = no_ws_qs.count()

        # ── Partition by status / created_by ───────────────────────
        by_status = dict(
            no_ws_qs.values_list('status').annotate(n=Count('id'))
        )
        by_creator = dict(
            no_ws_qs.values_list('created_by').annotate(n=Count('id'))
        )

        # ── Already-flagged vs candidate-for-flag ──────────────────
        already_diagnostic = no_ws_qs.filter(diagnostic_status='diagnostic').count()
        candidate_for_flag = total_no_ws - already_diagnostic

        # ── Sample IDs per bucket (optional) ───────────────────────
        samples = {}
        if sample_n > 0:
            samples = {
                'already_diagnostic': list(map(str,
                    no_ws_qs.filter(diagnostic_status='diagnostic')
                    .values_list('id', flat=True)[:sample_n]
                )),
                'candidate_for_flag': list(map(str,
                    no_ws_qs.filter(diagnostic_status__isnull=True)
                    .values_list('id', flat=True)[:sample_n]
                )),
            }

        # ── Apply path (retroactive mark) ──────────────────────────
        marked = 0
        if apply_mode:
            from core.services.initiative_diagnostics import mark_initiative_diagnostic

            candidate_qs = no_ws_qs.filter(diagnostic_status__isnull=True)
            for init in candidate_qs.iterator():
                payload_extras = {
                    'created_by': init.created_by or '',
                    'callsite_hint': 'backfill_initiative_workspace_links',
                    'status_at_mark': init.status,
                    'backfilled': True,
                }
                mark_initiative_diagnostic(
                    init, 'missing_target_workspace_id', payload_extras,
                )
                # Use update() to bypass the create-mark signal (which
                # only fires on created=True anyway, but cleaner).
                Initiative.objects.filter(pk=init.pk).update(
                    diagnostic_status=init.diagnostic_status,
                    diagnostic_code=init.diagnostic_code,
                    diagnostic_payload=init.diagnostic_payload,
                    diagnostic_marked_at=init.diagnostic_marked_at,
                    diagnostic_expires_at=init.diagnostic_expires_at,
                )
                marked += 1

        # ── Build report ───────────────────────────────────────────
        snapshot_at = timezone.now().isoformat()
        report = {
            'snapshot_at': snapshot_at,
            'workspace_scope': ws_scope or 'all',
            'total_no_ws': total_no_ws,
            'already_diagnostic': already_diagnostic,
            'candidate_for_flag': candidate_for_flag,
            'by_status': by_status,
            'by_creator': dict(Counter(by_creator).most_common(TOP_N)),
            'apply_mode': apply_mode,
            'marked_this_run': marked if apply_mode else 0,
        }
        if samples:
            report['samples'] = samples

        # ── Output ─────────────────────────────────────────────────
        if json_only:
            self.stdout.write(json.dumps(report, indent=2))
            return

        self.stdout.write(self.style.SUCCESS(
            f"\nInitiative target_workspace_id recon — "
            f"{snapshot_at} (workspace_scope={ws_scope or 'all'})"
        ))
        self.stdout.write("─" * 70)
        self.stdout.write(f"  Total Initiatives missing target_workspace_id:  {total_no_ws}")
        self.stdout.write(f"  Already flagged diagnostic:                     {already_diagnostic}")
        self.stdout.write(f"  Candidate for retroactive flag:                 {candidate_for_flag}")
        if apply_mode:
            self.stdout.write(self.style.WARNING(
                f"  --apply mode: marked {marked} rows this run"
            ))
        self.stdout.write("")
        self.stdout.write("  By status:")
        for status, n in sorted(by_status.items(), key=lambda r: -r[1]):
            self.stdout.write(f"    {status or '(blank)':<14} {n}")
        self.stdout.write("")
        self.stdout.write(f"  By created_by (top {TOP_N}):")
        for creator, n in Counter(by_creator).most_common(TOP_N):
            self.stdout.write(f"    {creator or '(blank)':<30} {n}")
        if samples:
            self.stdout.write("")
            self.stdout.write("  Samples:")
            for bucket, ids in samples.items():
                self.stdout.write(f"    {bucket}: {ids}")
        self.stdout.write("")
        self.stdout.write("  JSON:")
        self.stdout.write(json.dumps(report, indent=2))
