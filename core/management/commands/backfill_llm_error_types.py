"""S3038 A3 — Backfill `LLMCallLog.error_type` from `error_message`.

Runs the same regex classifier used by the model's `save()` pre-persist hook
against historical rows that landed before the hook shipped. Idempotent —
only touches rows with a non-empty `error_message` and empty `error_type`.

Usage:
  python manage.py backfill_llm_error_types                # dry-run
  python manage.py backfill_llm_error_types --apply        # write changes
  python manage.py backfill_llm_error_types --apply --limit 500
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from core.models_llm_routing import LLMCallLog
from core.services.llm_error_classifier import classify_llm_error


class Command(BaseCommand):
    help = (
        "Backfill LLMCallLog.error_type from error_message via the S3038 A3 "
        "regex classifier. Dry-run by default; pass --apply to write."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Write changes (default: dry-run counts only)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Cap rows processed (default: no cap)',
        )

    def handle(self, *args, apply: bool = False, limit: int | None = None, **opts):
        qs = (
            LLMCallLog.objects
            .exclude(error_message='')
            .filter(error_type='')
            .only('id', 'error_message')
            .order_by('-created_at')
        )
        if limit:
            qs = qs[:limit]

        rows = list(qs)
        counts: dict[str, int] = {}
        for row in rows:
            tag = classify_llm_error(row.error_message)
            counts[tag] = counts.get(tag, 0) + 1
            if apply:
                # .update() bypasses the save() hook — we're already inside
                # the classifier logic and don't need the hook to re-fire.
                LLMCallLog.objects.filter(id=row.id).update(error_type=tag)

        mode = 'APPLIED' if apply else 'DRY-RUN'
        self.stdout.write(f'{mode}: classified {len(rows)} rows')
        for tag, n in sorted(counts.items(), key=lambda x: -x[1]):
            label = tag or '(empty)'
            self.stdout.write(f'  {label:30} {n}')
