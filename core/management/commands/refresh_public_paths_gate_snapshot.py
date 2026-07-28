"""S3018 (Fold A): regenerate the PUBLIC_PATHS gate-status snapshot.

Emits `tests/security/public_paths_gate_snapshot.json` from live URL
resolver + decorator introspection. Use whenever a URL pattern is added,
removed, or re-gated under a `PUBLIC_PATHS` bare-prefix and the invariant
test at `tests/security/test_public_paths_gate_invariant_s3018.py` starts
failing.

Diff the resulting snapshot in your PR — every route change is visible
at code-review time.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand

from tests.security.public_paths_gate_snapshot_builder import (
    GATED_SNAPSHOT_PATH,
    UNGATED_SNAPSHOT_PATH,
    build_snapshot,
    write_snapshot,
)


class Command(BaseCommand):
    help = "Refresh the PUBLIC_PATHS gate-status snapshot (S3018 Fold A invariant)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print counts without writing to disk.",
        )

    def handle(self, *args, **options):
        snapshot = build_snapshot()
        gates: dict[str, int] = {}
        for row in snapshot["routes"].values():
            gates[row["gate"]] = gates.get(row["gate"], 0) + 1

        self.stdout.write(
            f"Built snapshot with {len(snapshot['routes'])} in-scope routes "
            f"across {snapshot['in_scope_prefixes_count']} prefixes."
        )
        for k, v in sorted(gates.items(), key=lambda x: -x[1]):
            self.stdout.write(f"  {k}: {v}")

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("--dry-run: skipping write."))
            return

        write_snapshot(snapshot)
        self.stdout.write(
            self.style.SUCCESS(
                f"Wrote gated snapshot → {GATED_SNAPSHOT_PATH}\n"
                f"Wrote ungated snapshot → {UNGATED_SNAPSHOT_PATH}"
            )
        )
