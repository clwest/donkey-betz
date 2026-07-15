"""S2794 — CLI entrypoint for the cross-tenant regression umbrella.

Runs the RUR-C1 shared cross-tenant regression harness and either
prints the JSON summary to stdout (default) or persists a
``TenantBoundaryHealthReport`` row (``--persist``) — or both
(``--json --persist``).

Invoked by:
  * Chris / operator manually
  * Celery periodic task (see ``core.tasks_tenant_boundary_health``)
  * CI job (future — GitHub Action wire-up not in S2794 scope)

Consumed by:
  * ``/api/governance/tenant-boundary-health/`` REST endpoint (persist mode)
  * Tenant Boundary Health Workspace sub-tab (via the endpoint)

Advisory posture — reports are longitudinal signal, not a launch gate
(S2794 F1 mitigation).
"""
from __future__ import annotations

import json

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run the RUR-C1 cross-tenant regression umbrella suite."

    def add_arguments(self, parser):
        parser.add_argument(
            "--persist",
            action="store_true",
            help="Persist a TenantBoundaryHealthReport row with the result. "
                 "Default off — dry-run prints summary only.",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Emit the summary as JSON on stdout. "
                 "Default on when --persist is off; explicit here if you want both.",
        )
        parser.add_argument(
            "--verbose-pytest",
            action="store_true",
            help="Let pytest print its default output (default: suppress).",
        )

    def handle(self, *args, **options):
        from core.services.cross_tenant_regression_service import (
            run_cross_tenant_regression,
        )

        persist = bool(options.get("persist"))
        emit_json = bool(options.get("json")) or not persist
        quiet = not bool(options.get("verbose_pytest"))

        result = run_cross_tenant_regression(quiet=quiet)

        if persist:
            from core.models import TenantBoundaryHealthReport

            row = TenantBoundaryHealthReport.objects.create(
                env=result["env"],
                git_sha=result["git_sha"],
                runner_identity=result["runner_identity"],
                elapsed_secs=result["elapsed_secs"],
                total_tests=result["total_tests"],
                passed=result["passed"],
                failed=result["failed"],
                errored=result["errored"],
                skipped=result["skipped"],
                failing_test_ids=result["failing_test_ids"],
                coverage_metadata=result["coverage_metadata"],
                summary_json=result["summary_json"],
            )
            # Emit the row identity as diagnostic (stderr) so the JSON
            # blob on stdout stays parse-clean.
            self.stderr.write(f"[persist] TenantBoundaryHealthReport id={row.id}")

        if emit_json:
            self.stdout.write(json.dumps(result, indent=2, default=str))
