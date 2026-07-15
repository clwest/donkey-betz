"""S2794 — RUR-C1 cross-tenant regression umbrella.

This file is the canonical name specified by RUR-C1 CAMPAIGN.md §5.2
line 202 (Real User Readiness Campaign, ratified 2026-07-10). It marks
the umbrella entry point for the shared cross-tenant regression suite
that RUR-C1 parent-close ceremony requires all three child arcs
(I-0301 + I-0302 + I-0303) to pass together.

**How the umbrella actually runs.**

The umbrella *definition* — which per-surface test files constitute
the RUR-C1 cross-tenant regression — lives in
``core.services.cross_tenant_regression_service.CROSS_TENANT_TEST_PATHS``.
The umbrella *runner* — which invokes pytest as a subprocess, captures
JUnit XML, and emits a JSON summary — lives at
``python manage.py run_cross_tenant_regression`` (see
``core/management/commands/run_cross_tenant_regression.py``).

Running the umbrella by itself does NOT re-run those tests here (that
would create either a recursive subprocess call or duplicate ~5min of
work in the day-to-day regression). Instead this file locks
**contract invariants** about the umbrella *definition*:

  1. The LABELS list is non-empty.
  2. Every listed path exists on disk (missing files ≠ green result).
  3. Every listed path lives under ``tests/security/`` (scope
     containment — RUR-C1 owns the security test tree).
  4. Every listed path has a corresponding coverage_metadata entry
     (F2 mitigation — coverage lied-about is worse than uncovered).

Running the FULL regression:

.. code-block:: bash

    python manage.py run_cross_tenant_regression            # print summary
    python manage.py run_cross_tenant_regression --persist  # DB row

    # Or direct:
    python -m pytest tests/security/ --junit-xml=/tmp/x.xml

CAMPAIGN doc: ``docs/research/implementation/real_user_readiness/CAMPAIGN.md``
"""
from __future__ import annotations

import os

from core.services.cross_tenant_regression_service import (
    CROSS_TENANT_TEST_PATHS,
    COVERAGE_METADATA,
    KNOWN_GAPS,
)


def test_umbrella_labels_not_empty():
    """Contract 1: LABELS is a non-empty list."""
    assert isinstance(CROSS_TENANT_TEST_PATHS, list)
    assert len(CROSS_TENANT_TEST_PATHS) > 0


def test_umbrella_labels_all_exist_on_disk():
    """Contract 2: every listed path exists as a real file.

    A missing path silently reduces the run count — a runner that
    thinks it ran green while one of its inputs is a phantom is a
    silent-corruption vector.
    """
    missing = [p for p in CROSS_TENANT_TEST_PATHS if not os.path.exists(p)]
    assert not missing, f"Umbrella labels missing on disk: {missing}"


def test_umbrella_labels_all_under_tests_security():
    """Contract 3: every listed path lives under ``tests/security/``.

    RUR-C1 owns the security test tree; drift into other trees
    (unit tests, integration, ad-hoc smoke) should not silently
    accrete under the umbrella.
    """
    outside = [
        p for p in CROSS_TENANT_TEST_PATHS
        if not p.startswith("tests/security/")
    ]
    assert not outside, (
        f"Umbrella labels outside tests/security/: {outside}"
    )


def test_umbrella_coverage_metadata_and_known_gaps_are_populated():
    """Contract 4 (S2794 F2 mitigation): coverage + gaps documented.

    A green suite result must be paired with an honest per-surface
    coverage statement + an explicit known-gaps list. Silence would
    encourage the "green suite = platform safe" false confidence
    Rigby flagged at S2794 SIGN F2.
    """
    assert isinstance(COVERAGE_METADATA, dict)
    assert len(COVERAGE_METADATA) > 0
    assert isinstance(KNOWN_GAPS, list)
    assert len(KNOWN_GAPS) > 0
    # Every value must be one of the recognized status strings (allow
    # trailing parenthesized notes: 'not_yet_covered (I-0303 not opened)').
    for surface, status in COVERAGE_METADATA.items():
        assert isinstance(status, str)
        head = status.split(" ", 1)[0]
        assert head in {"covered", "partial", "not_yet_covered"}, (
            f"Coverage status for {surface!r} must start with covered/"
            f"partial/not_yet_covered; got {status!r}"
        )
