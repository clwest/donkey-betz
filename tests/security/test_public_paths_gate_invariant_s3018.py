"""S3018 (Fold A from S3017): route-decorator invariant test.

Locks the current gate status of every URL pattern under a
`UnifiedTokenAuthenticationMiddleware.PUBLIC_PATHS` bare-prefix (plus
`PUBLIC_PATHS_EXACT`). See
`tests/security/public_paths_gate_snapshot_builder.py` for the full
design + Rigby T0 SIGN provenance.

**Failure modes this catches:**
1. New URL pattern added under a bare-prefix with `gate: none` — the
   S3017 F-2/F-3 class regression signal. Snapshot must be regenerated
   AND the reviewer must consciously decide "this new endpoint IS
   intentionally public" before merging.
2. Existing gated endpoint changed to ungated — silent regression.
3. Existing view relocated across modules without the same gate — module
   drift.

**How to regenerate the snapshot** (when the diff is intentional):

    python manage.py refresh_public_paths_gate_snapshot

Diff the resulting snapshot in your PR; the invariant test enforces
that the diff is intentional at code-review time.
"""
from __future__ import annotations

import json

from django.test import TestCase

from tests.security.public_paths_gate_snapshot_builder import (
    GATED_SNAPSHOT_PATH,
    UNGATED_SNAPSHOT_PATH,
    build_snapshot,
    read_snapshot,
)


class PublicPathsGateSnapshotInvariant(TestCase):
    """Snapshot-lock the gate status of every route under PUBLIC_PATHS."""

    maxDiff = None

    def test_snapshot_matches_live_state(self) -> None:
        live = build_snapshot()
        try:
            stored = read_snapshot()
        except FileNotFoundError:
            self.fail(
                f"Snapshot missing at {GATED_SNAPSHOT_PATH} or "
                f"{UNGATED_SNAPSHOT_PATH}. Regenerate with "
                "`python manage.py refresh_public_paths_gate_snapshot`."
            )

        # Compare schema_version + routes structure first so a schema bump
        # produces a clear message rather than a giant route diff.
        self.assertEqual(
            live["schema_version"],
            stored["schema_version"],
            "Snapshot schema_version drifted. Regenerate the snapshot.",
        )

        live_routes = live["routes"]
        stored_routes = stored["routes"]

        # New-route callout (Rigby T0 §1 refinement) — surface added
        # bare-prefix routes explicitly so snapshot regen isn't a silent
        # rubber-stamp.
        added = sorted(set(live_routes) - set(stored_routes))
        removed = sorted(set(stored_routes) - set(live_routes))
        added_ungated = [p for p in added if live_routes[p]["gate"] == "none"]

        if added_ungated:
            self.fail(
                "NEW URL patterns under a PUBLIC_PATHS bare-prefix landed "
                "WITHOUT an auth gate. Either (a) add "
                "`@token_auth_required` / `@superuser_required` / DRF "
                "`permission_classes`, OR (b) confirm the endpoint is "
                "intentionally public, THEN regenerate the snapshot with "
                "`python manage.py refresh_public_paths_gate_snapshot`. "
                f"Ungated new routes:\n{json.dumps(added_ungated, indent=2)}"
            )

        # Now enforce the full route-dict match.
        if live_routes != stored_routes:
            # Build a compact diff summary for the failure message.
            changed = [
                p for p in sorted(set(live_routes) & set(stored_routes))
                if live_routes[p] != stored_routes[p]
            ]
            self.fail(
                "PUBLIC_PATHS gate snapshot drifted from live state.\n"
                f"  added routes: {len(added)}\n"
                f"  removed routes: {len(removed)}\n"
                f"  changed routes: {len(changed)}\n"
                "Regenerate with `python manage.py refresh_public_paths_gate_snapshot` "
                "and review the diff in your PR."
            )

    def test_marker_attr_present_on_gated_test_view(self) -> None:
        """Sanity check: the marker-detection path actually works.

        Confirms that a view we KNOW is gated (`get_memory_detail` from
        the S3017 fix) shows up as `decorator:token_required` in the
        live snapshot. Guards against a silent break in the detector
        that would let real regressions slip through as `gate: none`.
        """
        live = build_snapshot()
        target = "/api/memory-palace/memory/<uuid:memory_id>/"
        self.assertIn(
            target, live["routes"],
            f"S3017-gated endpoint {target} missing from live snapshot",
        )
        self.assertEqual(
            live["routes"][target]["gate"], "decorator:token_required",
            f"S3017-gated endpoint {target} not detected as token-required",
        )
