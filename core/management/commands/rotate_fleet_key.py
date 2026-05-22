"""Manage fleet service key rotations (Move 1 Round 3).

Usage:
    # Start a rotation — mints a new key alongside the existing one
    python manage.py rotate_fleet_key plan --app-slug=contract-concierge

    # Move from `planned` → `active` (flips old key to draining)
    python manage.py rotate_fleet_key activate --rotation-id=<uuid>

    # After the fleet app starts using the new key, finalize the rotation
    python manage.py rotate_fleet_key complete --rotation-id=<uuid>
    #   (use --force if the new key hasn't been used within 6h)

    # Cancel a rotation (only valid before complete)
    python manage.py rotate_fleet_key abort --rotation-id=<uuid>

State machine: planned → active → completed (or → aborted). See
`core/services/fleet_rotation.py` for the invariants.
"""
from django.core.management.base import BaseCommand, CommandError

from core.services.fleet_rotation import (
    RotationError,
    abort_rotation,
    activate_rotation,
    complete_rotation,
    plan_rotation,
)


class Command(BaseCommand):
    help = "Plan / activate / complete / abort a fleet service key rotation."

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=["plan", "activate", "complete", "abort"],
            help="Lifecycle stage to drive.",
        )
        parser.add_argument(
            "--app-slug",
            help="(plan only) Fleet app identifier.",
        )
        parser.add_argument(
            "--rotation-id",
            help="(activate/complete/abort) Rotation UUID returned by plan.",
        )
        parser.add_argument(
            "--ends-in-hours",
            type=int,
            default=72,
            help="(plan only) When the rotation window expires (default 72h).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="(complete only) Skip the 'new key used recently' check.",
        )

    def handle(self, *args, **opts):
        action = opts["action"]

        try:
            if action == "plan":
                if not opts.get("app_slug"):
                    raise CommandError("--app-slug required for 'plan'")
                result = plan_rotation(
                    app_slug=opts["app_slug"],
                    ends_in_hours=opts["ends_in_hours"],
                )
                self._print_plan(result)
            else:
                if not opts.get("rotation_id"):
                    raise CommandError(f"--rotation-id required for {action!r}")
                if action == "activate":
                    state = activate_rotation(rotation_id=opts["rotation_id"])
                elif action == "complete":
                    state = complete_rotation(
                        rotation_id=opts["rotation_id"],
                        force=opts["force"],
                    )
                else:  # abort
                    state = abort_rotation(rotation_id=opts["rotation_id"])
                self._print_state(action, state)
        except RotationError as e:
            raise CommandError(f"{action} failed: {e}")

    def _print_plan(self, result):
        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Planned rotation\n"
        ))
        self.stdout.write(f"  rotation_id:   {result.rotation_id}")
        self.stdout.write(f"  status:        {result.status}")
        self.stdout.write(f"  old_key_id:    {result.old_key_id}")
        self.stdout.write(f"  new_key_id:    {result.new_key_id}")
        self.stdout.write(f"  ends_at:       {result.ends_at}")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING(
            "─" * 70 + "\n"
            "RAW SECRET for new key — shown EXACTLY ONCE; save now\n"
            + "─" * 70
        ))
        self.stdout.write(f"\nFLEET_KEY_ID={result.new_key_id}")
        self.stdout.write(f"FLEET_SERVICE_SECRET={result.new_key_secret}")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("─" * 70))
        self.stdout.write(
            "\nNext steps:\n"
            f"  1. Flip the fleet app's env to the new key.\n"
            f"  2. python manage.py rotate_fleet_key activate --rotation-id={result.rotation_id}\n"
            f"  3. python manage.py rotate_fleet_key complete --rotation-id={result.rotation_id}\n"
            f"\nAbort if needed:\n"
            f"  python manage.py rotate_fleet_key abort --rotation-id={result.rotation_id}\n"
        )

    def _print_state(self, action, state):
        self.stdout.write(self.style.SUCCESS(
            f"\n✓ {action.capitalize()}d rotation {state.rotation_id}\n"
        ))
        self.stdout.write(f"  status:           {state.status}")
        self.stdout.write(f"  old_key ({state.old_key_id}): {state.old_key_status}")
        self.stdout.write(f"  new_key ({state.new_key_id}): {state.new_key_status}")
        if state.starts_at:
            self.stdout.write(f"  starts_at:        {state.starts_at}")
        if state.ends_at:
            self.stdout.write(f"  ends_at:          {state.ends_at}")
