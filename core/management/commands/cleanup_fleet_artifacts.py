"""Run the fleet artifact cleanup task on demand (Move 2 Round 2).

Usage:
    python manage.py cleanup_fleet_artifacts

Same effect as the daily Celery beat task (`core.tasks.
cleanup_expired_fleet_artifacts`) but synchronous. Useful for:
- Ops/manual cleanup runs
- Staging validation of the TTL/cleanup pipeline
- Test harness invocation when the celery beat isn't running

Prints per-run stats (scanned/soft_deleted/capped/duration_ms).
"""
import json

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run fleet artifact soft-delete cleanup (synchronous)."

    def handle(self, *args, **opts):
        from core.services.fleet_artifact_cleanup import run_cleanup
        stats = run_cleanup()
        self.stdout.write(self.style.SUCCESS(
            "✓ Cleanup complete\n"
            + json.dumps(stats.as_dict(), indent=2)
        ))
