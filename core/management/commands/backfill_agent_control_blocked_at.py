"""Session 1092: backfill AgentControlEntry.blocked_at for legacy rows.

Existing entries written before the Session 1092 ``save()`` override may
have ``status='blocked'`` but ``blocked_at=None`` (the AudioAgent entry
flagged this in CTOAgent's platform analysis). This command fills those
gaps using ``updated_at`` as a best-effort proxy for when the block was
last touched, so forensics queries stop coming back empty.

Idempotent — safe to re-run on local and Railway.
"""

from django.core.management.base import BaseCommand

from core.models_unified_system import AgentControlEntry


class Command(BaseCommand):
    help = "Populate AgentControlEntry.blocked_at from updated_at for blocked rows missing the timestamp."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print the rows that would be updated without writing.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        gaps = list(
            AgentControlEntry.objects
            .filter(status='blocked', blocked_at__isnull=True)
            .order_by('agent_name')
        )

        if not gaps:
            self.stdout.write(self.style.SUCCESS("No backfill needed — all blocked entries have blocked_at."))
            return

        self.stdout.write(f"Found {len(gaps)} blocked entries with missing blocked_at:")
        for entry in gaps:
            line = (
                f"  {entry.agent_name}: blocked_at None -> {entry.updated_at}"
                f" (reason: {entry.reason[:80] or 'none'})"
            )
            self.stdout.write(line)

        if dry_run:
            self.stdout.write(self.style.WARNING("(dry-run, not saved)"))
            return

        for entry in gaps:
            entry.blocked_at = entry.updated_at
            entry.save(update_fields=['blocked_at'])
        self.stdout.write(self.style.SUCCESS(f"✓ backfilled {len(gaps)} rows."))
