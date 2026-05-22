"""Add an additional active key to an existing fleet identity (Round 2).

Usage:
    python manage.py add_fleet_key --app-slug=contract-concierge

Dual-active key support per Rigby's Round-2 heads-up — the new key
starts in ``active`` state alongside the existing one(s). Use this
for:
- Pre-rotation: mint new key, flip fleet app's env, then disable old.
- Emergency recovery: existing key was leaked but rotation lifecycle
  hasn't been built yet; this is the simplest way to get a fresh key.

Prints a copy-paste env block + the raw secret EXACTLY ONCE.
"""
from django.core.management.base import BaseCommand, CommandError

from core.services.fleet_provisioning import (
    ProvisioningError,
    add_key_for_identity,
)


class Command(BaseCommand):
    help = "Add an additional active key to an existing fleet identity."

    def add_arguments(self, parser):
        parser.add_argument(
            "--app-slug",
            required=True,
            help="Fleet app identifier (existing identity).",
        )

    def handle(self, *args, **opts):
        try:
            result = add_key_for_identity(app_slug=opts["app_slug"])
        except ProvisioningError as e:
            raise CommandError(f"add-key failed: {e}")

        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Added active key to {result.app_slug!r}\n"
        ))
        self.stdout.write(f"  key_id:        {result.key_id}")
        self.stdout.write(f"  status:        {result.status}")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING(
            "─" * 70 + "\n"
            "RAW SECRET — shown EXACTLY ONCE; save now to fleet app env\n"
            + "─" * 70
        ))
        self.stdout.write(f"\nFLEET_KEY_ID={result.key_id}")
        self.stdout.write(f"FLEET_SERVICE_SECRET={result.secret}")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("─" * 70))
        self.stdout.write(
            "\nOld keys remain active. Flip the fleet app's env to the new "
            "key_id + secret, verify with a signed /api/pa/chat/ call, then "
            "disable the old key via the rotation endpoints (Round 3).\n"
        )
