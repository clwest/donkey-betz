"""
S2973: Policy list for `[NO_ITEMS]` denominator exclusions.

Some LegacySpiderData rows are marked `embedding_text='[NO_ITEMS]'` because
they were never meant to carry embeddable content in the first place —
analytics rollups (e.g., `betting_coordinator` writes `top_plays` /
`arbitrage` / `predictions` summaries) or non-text APIs (e.g., `openmeteo`
returns weather metrics). Counting these against embedding coverage makes
the pipeline look broken when it's operating correctly.

This module lists spiders and data_types whose rows are STRUCTURALLY
non-embeddable and should be excluded from denominators that measure
"searchable content supply". It does NOT hide the rows themselves — the
raw counts stay in the primary `total` field; only derived denominators
change.

## Conservative v1 policy

The initial exclusion list is intentionally small: two spiders confirmed
via S2973 sampling.  Every entry here is a claim of "this row shape
cannot be embedded by design" — a false entry HIDES real data-quality
issues (broken extractors, upstream auth failures, etc.). Extend only
after sampling the target spider and confirming the shape genuinely has
no embeddable content.

## Not in this policy (deliberately)

- **theodds** — currently 100% [NO_ITEMS] over 7d, but sampled rows are
  `auth_failure_circuit_breaker` envelopes (upstream API auth issue,
  fixable). Excluding it would mask the auth failure.
- **spotify / giphy / unsplash** — media APIs; probably don't fit text
  embedding, but need shape sampling before exclusion.
- **legal spiders** (lii / findlaw / colorado_family_law / justia_family_law)
  — 100% [NO_ITEMS] but likely extractor misses on real content.

These are follow-up candidates, not exclusions.
"""

from __future__ import annotations

from typing import FrozenSet


EXCLUDED_SPIDER_NAMES: FrozenSet[str] = frozenset({
    'betting_coordinator',
    'openmeteo',
})

EXCLUDED_DATA_TYPES: FrozenSet[str] = frozenset()
