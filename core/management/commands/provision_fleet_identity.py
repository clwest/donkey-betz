"""Provision a new fleet service identity + first key (Move 1 Round 2).

Usage:
    python manage.py provision_fleet_identity \\
        --app-slug=contract-concierge \\
        --name="Contract Concierge"

    # Custom capabilities (overrides per-app default):
    python manage.py provision_fleet_identity \\
        --app-slug=new-app --name="New App" \\
        --capabilities-json='{"routing": {"can_request_hint": true}}' \\
        --allowed-routes-json='["/api/pa/chat/"]' \\
        --no-defaults

Prints a copy-paste env block + the raw secret EXACTLY ONCE. Save the
output to the fleet app's deployment secrets immediately — u-d-b stores
only the SHA256 hash and cannot recover the raw secret.
"""
import json

from django.core.management.base import BaseCommand, CommandError

from core.services.fleet_provisioning import (
    ProvisioningError,
    provision_identity,
)


class Command(BaseCommand):
    help = "Provision a new fleet service identity + first signing key."

    def add_arguments(self, parser):
        parser.add_argument(
            "--app-slug",
            required=True,
            help="Fleet app identifier (e.g. contract-concierge). "
                 "Must match the key in config/fleet_agent_routing.json.",
        )
        parser.add_argument(
            "--name",
            required=True,
            help="Human-readable label for the identity.",
        )
        parser.add_argument(
            "--capabilities-json",
            default=None,
            help="JSON dict of capabilities to override the per-app default.",
        )
        parser.add_argument(
            "--allowed-routes-json",
            default=None,
            help="JSON list of allowed routes to override the default.",
        )
        parser.add_argument(
            "--no-defaults",
            action="store_true",
            help="Require --capabilities-json + --allowed-routes-json; "
                 "no per-app defaults will be applied.",
        )

    def handle(self, *args, **opts):
        capabilities = None
        if opts.get("capabilities_json"):
            try:
                capabilities = json.loads(opts["capabilities_json"])
            except json.JSONDecodeError as e:
                raise CommandError(f"--capabilities-json is not valid JSON: {e}")

        allowed_routes = None
        if opts.get("allowed_routes_json"):
            try:
                allowed_routes = json.loads(opts["allowed_routes_json"])
            except json.JSONDecodeError as e:
                raise CommandError(f"--allowed-routes-json is not valid JSON: {e}")

        try:
            result = provision_identity(
                app_slug=opts["app_slug"],
                name=opts["name"],
                capabilities=capabilities,
                allowed_routes=allowed_routes,
                use_defaults=not opts["no_defaults"],
            )
        except ProvisioningError as e:
            raise CommandError(f"provisioning failed: {e}")

        # ─── Copy-paste output block ────────────────────────────────
        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Provisioned fleet identity for {result.app_slug!r}\n"
        ))
        self.stdout.write(f"  key_id:        {result.key_id}")
        self.stdout.write(f"  status:        {result.status}")
        self.stdout.write(f"  capabilities:  {json.dumps(result.capabilities, indent=2)}")
        self.stdout.write(f"  allowed_routes:{json.dumps(result.allowed_routes, indent=2)}")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING(
            "─" * 70 + "\n"
            "RAW SECRET — shown EXACTLY ONCE; save now to fleet app env\n"
            + "─" * 70
        ))
        self.stdout.write(f"\nFLEET_APP_SLUG={result.app_slug}")
        self.stdout.write(f"FLEET_KEY_ID={result.key_id}")
        self.stdout.write(f"FLEET_SERVICE_SECRET={result.secret}")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("─" * 70))
        self.stdout.write(
            "\nu-d-b stores only SHA256(secret). If lost, mint a new key via:\n"
            f"  python manage.py add_fleet_key --app-slug={result.app_slug}\n"
        )
