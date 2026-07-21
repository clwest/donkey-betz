"""
S2868 backfill — flip already-flagged rows of the 4 newly-exempt
deliverable_types (`engineering_backlog`, `engineering_record`,
`code_review`, `session_handoff`) into the `cleared` sentinel state.

The S2868 PR grew `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT` from a
1-type frozenset to 5. Historically-created rows of the 4 new types
that were flagged `missing_initiative_id` before the exemption grew
remain as UI noise until they're proactively transitioned.

Idempotent + dry-run by default. Only touches rows matching:
    deliverable_type IN {engineering_backlog, engineering_record,
                         code_review, session_handoff}
    AND diagnostic_status = 'diagnostic'
    AND diagnostic_code = 'missing_initiative_id'

Flips each row to `diagnostic_status='cleared'` with a synthetic
manual_clear_reason marking the backfill and preserves prior code +
marked_at as audit residue (parity with `deliverable_tool.clear_diagnostic`).

Usage::

    # Preview (default)
    python manage.py backfill_s2868_exempt_type_diagnostics

    # Execute
    python manage.py backfill_s2868_exempt_type_diagnostics --confirm
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models_deliverables import Deliverable
from core.services.deliverable_factory import _TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT


# The 4 types the S2868 PR added to the exemption set.
_S2868_NEW_EXEMPT_TYPES = frozenset({
    'engineering_backlog',
    'engineering_record',
    'code_review',
    'session_handoff',
})


class Command(BaseCommand):
    help = (
        "S2868 backfill: flip diagnostic rows of newly-exempt deliverable "
        "types into the 'cleared' sentinel state."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm', action='store_true',
            help='Execute the flip. Without this flag, prints a dry-run preview.',
        )

    def handle(self, *args, **options):
        confirm = options['confirm']

        # Belt-and-suspenders: verify the runtime exemption set actually
        # contains the 4 target types. Guards against a partial revert
        # where the code was reverted but the backfill wasn't.
        missing = _S2868_NEW_EXEMPT_TYPES - _TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT
        if missing:
            self.stderr.write(self.style.ERROR(
                f"Runtime exemption set does not contain: {sorted(missing)}. "
                "Backfill aborted — the code fix has not landed. See "
                "core/services/deliverable_factory.py:_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT."
            ))
            return

        qs = Deliverable.objects.filter(
            deliverable_type__in=_S2868_NEW_EXEMPT_TYPES,
            diagnostic_status='diagnostic',
            diagnostic_code='missing_initiative_id',
        ).order_by('deliverable_type', '-diagnostic_marked_at')

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS(
                "No rows to backfill — all rows of the 4 newly-exempt types "
                "are already clean."
            ))
            return

        # Preview breakdown
        from collections import Counter
        by_type = Counter(qs.values_list('deliverable_type', flat=True))
        self.stdout.write(f"Rows eligible for backfill: {total}")
        for t, n in sorted(by_type.items()):
            self.stdout.write(f"  {t}: {n}")

        if not confirm:
            self.stdout.write(self.style.WARNING(
                "\nDRY RUN — no changes made. Re-run with --confirm to execute."
            ))
            return

        # Execute — flip each row idempotently. We iterate rather than bulk
        # update because we need to merge the existing diagnostic_payload
        # dict per-row.
        now = timezone.now()
        now_iso = now.isoformat()
        clear_reason = 'S2868 backfill: type exempt from initiative alignment.'
        flipped = 0
        for row in qs:
            prior_payload = dict(row.diagnostic_payload) if row.diagnostic_payload else {}
            prior_code = row.diagnostic_code
            prior_marked_at = row.diagnostic_marked_at

            row.diagnostic_status = 'cleared'
            row.diagnostic_expires_at = None
            row.diagnostic_payload = {
                **prior_payload,
                'manually_cleared_at': now_iso,
                'manually_cleared_by_user_id': None,
                'manual_clear_reason': clear_reason,
                'manual_clear_trace_id': 'backfill_s2868',
                'prior_diagnostic_code': prior_code,
                'prior_marked_at': prior_marked_at.isoformat() if prior_marked_at else None,
            }
            row.save(update_fields=[
                'diagnostic_status',
                'diagnostic_expires_at',
                'diagnostic_payload',
            ])
            flipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Flipped {flipped}/{total} rows to 'cleared' sentinel."
        ))
