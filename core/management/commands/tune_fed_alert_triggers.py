"""Session 1092: tune Fed Alert situation triggers to reduce governance noise.

Existing 'Fed/Interest Rate News' was firing every market headline as 'high'
urgency, producing 5+ Fed Alert attention items per 24h. This command:

  1. Downgrades the broad trigger to severity=medium, cooldown=720m (12h).
  2. Seeds a narrow 'FOMC Rate Decision' trigger at severity=high for actually
     market-moving Fed events (FOMC statements, dot plots, emergency action).

Idempotent — safe to re-run on local and Railway.
"""

from django.core.management.base import BaseCommand

from core.models_situation_triggers import DEFAULT_TRIGGERS, SituationTrigger

BROAD_TRIGGER_NAME = "Fed/Interest Rate News"
NARROW_TRIGGER_NAME = "FOMC Rate Decision"


class Command(BaseCommand):
    help = "Tune Fed Alert situation triggers (Session 1092 noise reduction)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print intended changes without writing to DB.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        defaults_by_name = {t["name"]: t for t in DEFAULT_TRIGGERS}

        broad_target = defaults_by_name[BROAD_TRIGGER_NAME]
        narrow_target = defaults_by_name[NARROW_TRIGGER_NAME]

        self._update_broad(broad_target, dry_run)
        self._upsert_narrow(narrow_target, dry_run)

    def _update_broad(self, target: dict, dry_run: bool) -> None:
        try:
            row = SituationTrigger.objects.get(name=BROAD_TRIGGER_NAME)
        except SituationTrigger.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f"  '{BROAD_TRIGGER_NAME}' not present — will be created on next seed."
                )
            )
            return

        fields_to_check = [
            "severity",
            "cooldown_minutes",
            "priority",
            "description",
            "threshold_value",
        ]
        changes = {f: target[f] for f in fields_to_check if getattr(row, f) != target[f]}

        if not changes:
            self.stdout.write(
                self.style.SUCCESS(f"  '{BROAD_TRIGGER_NAME}' already tuned — no change.")
            )
            return

        self.stdout.write(f"  Updating '{BROAD_TRIGGER_NAME}':")
        for field, new_val in changes.items():
            self.stdout.write(f"    {field}: {getattr(row, field)!r} -> {new_val!r}")

        if dry_run:
            self.stdout.write(self.style.WARNING("  (dry-run, not saved)"))
            return

        for field, new_val in changes.items():
            setattr(row, field, new_val)
        row.save(update_fields=list(changes.keys()))
        self.stdout.write(self.style.SUCCESS("  ✓ saved."))

    def _upsert_narrow(self, target: dict, dry_run: bool) -> None:
        existing = SituationTrigger.objects.filter(name=NARROW_TRIGGER_NAME).first()

        if existing:
            self.stdout.write(
                self.style.SUCCESS(f"  '{NARROW_TRIGGER_NAME}' already exists — no change.")
            )
            return

        self.stdout.write(f"  Creating '{NARROW_TRIGGER_NAME}' (severity={target['severity']})")
        if dry_run:
            self.stdout.write(self.style.WARNING("  (dry-run, not created)"))
            return

        SituationTrigger.objects.create(**target)
        self.stdout.write(self.style.SUCCESS("  ✓ created."))
