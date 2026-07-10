"""
Regenerate the pinned HTTP endpoint snapshot at
``tests/security/http_endpoint_snapshot.json`` for the I-0301 Phase 4
Coverage Denominator Machinery.

Contract ref:
    docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md
    docs/research/implementation/tenant_boundary_lockdown/I-0301_scoping.md §5, §7.1

Usage:

    # Fail fast if any AllowAny endpoint isn't classified in
    # tests/security/endpoints_covered.txt (Rigby S2742 Phase 4 SIGN Q4)
    python manage.py regenerate_endpoint_snapshot

    # Regenerate without the AllowAny gate — dangerous; use only when
    # intentionally adding unclassified AllowAny during triage
    python manage.py regenerate_endpoint_snapshot --unsafe-skip-classification-check

Rigby S2742 Phase 4 SIGN Q4 material amendment: this command fails fast
if the regenerated snapshot contains any AllowAny (or A2 token+throttle)
endpoint that is not present in ``endpoints_covered.txt``. Prevents
"we'll classify later" security debt.

Exit codes:
- 0 — snapshot regenerated successfully
- 1 — regeneration blocked because an AllowAny endpoint is missing from
  endpoints_covered.txt
- 2 — file write error
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from django.core.management.base import BaseCommand

from core.management.commands.enumerate_public_http_endpoints import (
    enumerate_endpoints,
)

DEFAULT_SNAPSHOT_PATH = Path("tests/security/http_endpoint_snapshot.json")
ENDPOINTS_COVERED_PATH = Path("tests/security/endpoints_covered.txt")

_ALLOWANY_PERMISSION = "rest_framework.permissions.AllowAny"


def _classified_url_patterns() -> set[str]:
    """Parse endpoints_covered.txt and return the set of url patterns
    already explicitly classified into a bucket."""
    classified: set[str] = set()
    if not ENDPOINTS_COVERED_PATH.exists():
        return classified

    for raw_line in ENDPOINTS_COVERED_PATH.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        # bucket, url, view, status — url is index 1
        url = parts[1]
        # Normalize: pin file may use /-leading; enumerator produces the
        # resolver-pattern form (without leading /). Compare stripped.
        classified.add(url.lstrip("/"))
    return classified


def _endpoints_needing_classification(endpoints: list[dict]) -> list[dict]:
    """Return the endpoints that require explicit bucketing per the safety
    contract discipline: AllowAny OR AllowAny + non-default auth (A2).

    Missing from ``endpoints_covered.txt`` → regenerate blocks (Rigby
    SIGN Q4).
    """
    needing: list[dict] = []
    classified = _classified_url_patterns()
    for ep in endpoints:
        perms = ep.get("permission_classes") or []
        if _ALLOWANY_PERMISSION not in perms:
            continue

        url_pattern = ep["url_pattern"]
        # Strip trailing regex $ and leading ^
        normalized = url_pattern.rstrip("$").lstrip("^")
        if normalized in classified or url_pattern in classified:
            continue

        # Also accept when the pin file's URL is a substring of the
        # concrete pattern (Django URL patterns may include named group
        # syntax like ``<path:filename>``).
        matched = False
        for classified_url in classified:
            if normalized.startswith(classified_url) or classified_url.startswith(
                normalized
            ):
                matched = True
                break
        if matched:
            continue

        needing.append(ep)
    return needing


class Command(BaseCommand):
    help = (
        "Regenerate tests/security/http_endpoint_snapshot.json from the "
        "live URL resolver. Fails fast if any AllowAny endpoint is "
        "unclassified (Rigby Phase 4 SIGN Q4). See file docstring."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default=str(DEFAULT_SNAPSHOT_PATH),
            help=(
                f"Snapshot file path (default: {DEFAULT_SNAPSHOT_PATH})."
            ),
        )
        parser.add_argument(
            "--unsafe-skip-classification-check",
            action="store_true",
            help=(
                "Regenerate without the AllowAny classification gate. "
                "Use only during intentional triage; not for CI."
            ),
        )

    def handle(self, *args, **options):
        endpoints = enumerate_endpoints()

        if not options.get("unsafe_skip_classification_check"):
            needing = _endpoints_needing_classification(endpoints)
            if needing:
                self.stderr.write(self.style.ERROR(
                    f"\n{len(needing)} AllowAny endpoint(s) require "
                    f"classification in {ENDPOINTS_COVERED_PATH} before "
                    f"the snapshot can be regenerated:\n"
                ))
                for ep in needing:
                    self.stderr.write(
                        f"  - {ep['url_pattern']} "
                        f"({ep.get('view', 'unknown')})\n"
                    )
                self.stderr.write(self.style.ERROR(
                    "\nFix: add each endpoint to "
                    f"{ENDPOINTS_COVERED_PATH} with a bucket "
                    "(A / A2 / B / C / D) and status "
                    "(pending / remediated / dead-gated / in-flight), "
                    "then re-run this command.\n"
                    "\nOverride (dangerous, only during triage): pass "
                    "--unsafe-skip-classification-check.\n"
                ))
                sys.exit(1)

        payload = {
            "endpoint_count": len(endpoints),
            "endpoints": endpoints,
        }
        serialized = json.dumps(payload, indent=2, sort_keys=True)

        try:
            output_path = Path(options["output"])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(serialized + "\n")
        except OSError as exc:
            self.stderr.write(self.style.ERROR(
                f"Failed to write snapshot: {exc}"
            ))
            sys.exit(2)

        self.stdout.write(self.style.SUCCESS(
            f"Wrote snapshot with {len(endpoints)} endpoints → "
            f"{options['output']}"
        ))
