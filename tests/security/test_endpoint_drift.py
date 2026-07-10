"""
I-0301 Phase 4 Coverage Denominator Machinery — endpoint drift test.

Diffs live URL resolver enumeration against the pinned snapshot at
``tests/security/http_endpoint_snapshot.json``. Blocks PRs that:

1. Add a NEW AllowAny endpoint without classifying it in
   ``endpoints_covered.txt``.
2. Regress an endpoint from IsAuthenticated (or stricter) → AllowAny.
3. Change HTTP methods for an existing endpoint (Rigby S2742 Phase 4
   SIGN Q2 addition — method drift).
4. Change authentication_classes for an existing endpoint (Rigby SIGN
   Q2 addition — auth-class drift).

Contract ref:
    docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md
    docs/research/implementation/tenant_boundary_lockdown/I-0301_scoping.md §5, §7.1

Regenerating the snapshot after intentional changes:

    python manage.py regenerate_endpoint_snapshot

That command fails fast if any AllowAny endpoint is unclassified in
``endpoints_covered.txt`` (Rigby SIGN Q4). Use
``--unsafe-skip-classification-check`` only during triage.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.management.commands.enumerate_public_http_endpoints import (
    enumerate_endpoints,
)

_SNAPSHOT_PATH = Path("tests/security/http_endpoint_snapshot.json")
_ENDPOINTS_COVERED_PATH = Path("tests/security/endpoints_covered.txt")

_ALLOWANY_PERMISSION = "rest_framework.permissions.AllowAny"


def _load_snapshot() -> list[dict]:
    if not _SNAPSHOT_PATH.exists():
        raise RuntimeError(
            f"Endpoint snapshot missing at {_SNAPSHOT_PATH}. Run "
            "`python manage.py regenerate_endpoint_snapshot "
            "--unsafe-skip-classification-check` to bootstrap."
        )
    data = json.loads(_SNAPSHOT_PATH.read_text())
    return data["endpoints"]


def _classified_url_patterns() -> set[str]:
    """Return url_pattern strings already classified in endpoints_covered.txt."""
    classified: set[str] = set()
    if not _ENDPOINTS_COVERED_PATH.exists():
        return classified
    for raw_line in _ENDPOINTS_COVERED_PATH.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            classified.add(parts[1].lstrip("/"))
    return classified


def _endpoint_key(ep: dict) -> tuple:
    """Deterministic dict → tuple key for set-diff operations."""
    return (
        ep["url_pattern"],
        ep.get("namespace", ""),
        ep.get("url_name", ""),
        ep.get("view", ""),
    )


def _has_allowany(ep: dict) -> bool:
    return _ALLOWANY_PERMISSION in (ep.get("permission_classes") or [])


def _matches_classified(url_pattern: str, classified: set[str]) -> bool:
    normalized = url_pattern.rstrip("$").lstrip("^")
    if normalized in classified or url_pattern in classified:
        return True
    for cu in classified:
        if normalized.startswith(cu) or cu.startswith(normalized):
            return True
    return False


class TestEndpointDrift:
    """Drift detector — the load-bearing Phase 4 invariant."""

    def test_snapshot_exists(self):
        assert _SNAPSHOT_PATH.exists(), (
            f"Snapshot missing at {_SNAPSHOT_PATH}. Run "
            "regenerate_endpoint_snapshot to bootstrap."
        )

    def test_no_new_allowany_endpoint_without_classification(self):
        """Any NEW AllowAny endpoint added since the snapshot must appear
        in ``endpoints_covered.txt``. (Rigby S2742 Phase 4 SIGN Q4.)"""
        snapshot = _load_snapshot()
        live = enumerate_endpoints()
        classified = _classified_url_patterns()

        snapshot_keys = {_endpoint_key(ep) for ep in snapshot}

        new_allowany_unclassified: list[dict] = []
        for ep in live:
            if _endpoint_key(ep) in snapshot_keys:
                continue
            if not _has_allowany(ep):
                continue
            if _matches_classified(ep["url_pattern"], classified):
                continue
            new_allowany_unclassified.append(ep)

        if new_allowany_unclassified:
            msg_lines = [
                (
                    f"{len(new_allowany_unclassified)} NEW AllowAny "
                    "endpoint(s) added without classification in "
                    f"{_ENDPOINTS_COVERED_PATH}:"
                )
            ]
            for ep in new_allowany_unclassified:
                msg_lines.append(f"  - {ep['url_pattern']} ({ep.get('view')})")
            msg_lines.append(
                "\nFix: classify each in tests/security/endpoints_covered.txt "
                "with a bucket (A / A2 / B / C / D) and status "
                "(pending / remediated / dead-gated / in-flight), then run "
                "`python manage.py regenerate_endpoint_snapshot`."
            )
            pytest.fail("\n".join(msg_lines))

    def test_no_endpoint_regressed_to_allowany(self):
        """Rigby S2742 Phase 4 SIGN Q3 HARD-FAIL invariant.

        If any endpoint that was NOT AllowAny in the snapshot becomes
        AllowAny in the live enumeration, CI fails.
        """
        snapshot = _load_snapshot()
        live = enumerate_endpoints()

        snapshot_by_key = {_endpoint_key(ep): ep for ep in snapshot}

        regressions: list[tuple[dict, dict]] = []
        for ep in live:
            key = _endpoint_key(ep)
            prior = snapshot_by_key.get(key)
            if prior is None:
                continue  # New endpoint — handled by other test
            if _has_allowany(ep) and not _has_allowany(prior):
                regressions.append((prior, ep))

        if regressions:
            msg_lines = [
                (
                    f"{len(regressions)} endpoint(s) REGRESSED from "
                    "non-AllowAny → AllowAny (Rigby SIGN Q3 hard-fail "
                    "invariant):"
                )
            ]
            for prior, live_ep in regressions:
                msg_lines.append(
                    f"  - {live_ep['url_pattern']} ({live_ep.get('view')})\n"
                    f"      prior: {prior.get('permission_classes')}\n"
                    f"      live:  {live_ep.get('permission_classes')}"
                )
            msg_lines.append(
                "\nFix: restore the tighter permission_classes or remove "
                "the endpoint. This regression is NEVER allowed to land."
            )
            pytest.fail("\n".join(msg_lines))

    def test_no_method_drift_on_existing_endpoints(self):
        """Rigby S2742 Phase 4 SIGN Q2 method-drift category.

        HTTP method changes on an existing endpoint must be reflected in
        the snapshot (i.e., regenerated after the change lands).
        """
        snapshot = _load_snapshot()
        live = enumerate_endpoints()
        snapshot_by_key = {_endpoint_key(ep): ep for ep in snapshot}

        drifted: list[tuple[dict, dict]] = []
        for ep in live:
            key = _endpoint_key(ep)
            prior = snapshot_by_key.get(key)
            if prior is None:
                continue
            prior_methods = set(prior.get("http_methods") or [])
            live_methods = set(ep.get("http_methods") or [])
            if prior_methods != live_methods:
                drifted.append((prior, ep))

        if drifted:
            msg_lines = [
                f"{len(drifted)} endpoint(s) show HTTP method drift:"
            ]
            for prior, live_ep in drifted:
                msg_lines.append(
                    f"  - {live_ep['url_pattern']}\n"
                    f"      prior methods: {sorted(prior.get('http_methods') or [])}\n"
                    f"      live methods:  {sorted(live_ep.get('http_methods') or [])}"
                )
            msg_lines.append(
                "\nFix: `python manage.py regenerate_endpoint_snapshot` "
                "if the change is intentional."
            )
            pytest.fail("\n".join(msg_lines))

    def test_no_auth_class_drift_on_existing_endpoints(self):
        """Rigby S2742 Phase 4 SIGN Q2 auth-class-drift category.

        authentication_classes changes on existing endpoints must be
        reflected in the snapshot.
        """
        snapshot = _load_snapshot()
        live = enumerate_endpoints()
        snapshot_by_key = {_endpoint_key(ep): ep for ep in snapshot}

        drifted: list[tuple[dict, dict]] = []
        for ep in live:
            key = _endpoint_key(ep)
            prior = snapshot_by_key.get(key)
            if prior is None:
                continue
            prior_auth = tuple(prior.get("authentication_classes") or [])
            live_auth = tuple(ep.get("authentication_classes") or [])
            if prior_auth != live_auth:
                drifted.append((prior, ep))

        if drifted:
            msg_lines = [
                f"{len(drifted)} endpoint(s) show authentication_classes drift:"
            ]
            for prior, live_ep in drifted:
                msg_lines.append(
                    f"  - {live_ep['url_pattern']}\n"
                    f"      prior auth: {prior.get('authentication_classes')}\n"
                    f"      live auth:  {live_ep.get('authentication_classes')}"
                )
            msg_lines.append(
                "\nFix: `python manage.py regenerate_endpoint_snapshot` "
                "if the change is intentional."
            )
            pytest.fail("\n".join(msg_lines))
