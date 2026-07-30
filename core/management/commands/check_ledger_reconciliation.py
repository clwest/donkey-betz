"""Standalone management command for the S3041 ledger-reconciliation
meta-fix. Runs the same check that ``session_lifecycle close`` runs but
without any close side effects — useful for pre-close verification or
CI-style spot checks on a handoff draft.

Usage examples::

    python manage.py check_ledger_reconciliation --handoff docs/handoffs/SESSION_3041_LEDGER_RECONCILIATION.md
    python manage.py check_ledger_reconciliation --handoff <path> --allow-ledger-drift
    python manage.py check_ledger_reconciliation --handoff <path> --ledger-deliverable-id <UUID>
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from core.services.ledger_reconciliation import (
    LedgerReconciliationError,
    check_ledger_reconciliation_at_close,
)


class Command(BaseCommand):
    help = (
        "S3041 meta-fix: verify that every `Ledger #N` reference in a "
        "session handoff has a matching `Ledger #N status flip` block "
        "in the Rigby Tool Gap Ledger deliverable. Same check "
        "session_lifecycle close runs, but without close side effects."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--handoff",
            required=True,
            help="Path to the session handoff to check.",
        )
        parser.add_argument(
            "--ledger-deliverable-id",
            default=None,
            help=(
                "UUID of the ledger deliverable to check against. "
                "Defaults to the Rigby Tool Gap Ledger."
            ),
        )
        parser.add_argument(
            "--allow-ledger-drift",
            action="store_true",
            help=(
                "Report drift but do not raise. Same escape hatch as "
                "session_lifecycle close --allow-ledger-drift."
            ),
        )

    def handle(self, *args, **options):
        try:
            result = check_ledger_reconciliation_at_close(
                handoff_path=options["handoff"],
                ledger_deliverable_id=options.get("ledger_deliverable_id"),
                allow_ledger_drift=bool(options.get("allow_ledger_drift")),
            )
        except LedgerReconciliationError as exc:
            raise CommandError(str(exc)) from exc

        if result.mode == "no_handoff":
            self.stdout.write(
                f"[LEDGER-RECON NO_HANDOFF] handoff not found at "
                f"{result.handoff_path} — nothing to check."
            )
            return

        assert result.handoff_path is not None  # narrowed by mode != 'no_handoff'
        handoff_name = result.handoff_path.name

        if not result.referenced_entries:
            self.stdout.write(
                f"[LEDGER-RECON CLEAN] {handoff_name}: "
                f"no `Ledger #N` references — nothing to check."
            )
            return

        refs_str = ", ".join(f"#{n}" for n in result.referenced_entries)
        flipped_str = (
            ", ".join(f"#{n}" for n in result.flipped_entries) or "(none)"
        )
        self.stdout.write(f"[LEDGER-RECON] handoff: {handoff_name}")
        self.stdout.write(f"  referenced: {refs_str}")
        self.stdout.write(f"  flipped:    {flipped_str}")

        if result.drift_entries:
            drift_str = ", ".join(f"#{n}" for n in result.drift_entries)
            self.stdout.write(
                f"  drift:      {drift_str} — no `Ledger #N status flip` "
                f"block in ledger deliverable"
            )
            self.stdout.write(
                f"  mode:       {result.mode} (--allow-ledger-drift set)"
            )
        else:
            self.stdout.write("  drift:      (none)")
            self.stdout.write("  mode:       clean")
