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

## S2975 addition — discord_training

Confirmed Class 1 (rollup by design) via S2975 sampling (25 most recent
30d rows on 2026-07-26). Every hourly-ish row is either an empty run
(`items=[]`, `empty_reason=no_items`) or a single-item statistics
snapshot with keys `by_topic`, `high_quality_conversations`,
`medium_quality_conversations`, `sample_formats`, `statistics` — a
rollup of accumulated training data, not an embeddable content unit.
Top NO_ITEMS producer by volume post-S2975 cleanup (31 rows/30d,
30 rows/7d in the non-deferred set).

## Not in this policy (deliberately)

- **theodds** — currently 100% [NO_ITEMS] over 7d, but sampled rows are
  `auth_failure_circuit_breaker` envelopes (upstream API auth issue,
  fixable). Excluding it would mask the auth failure.
- **remoteok** — S2975 sampling confirmed the spider only saves the
  remoteok API's legal preamble (`type: item, legal: API Terms of
  Service...`) because that item's `last_updated` field mutates every
  fetch and beats dedup while real jobs get deduped. Root cause is
  spider-side, not a policy exclusion — needs a pre-dedup filter in
  `ai_core/spiders/remoteok_spider.py`. Logged as follow-up seed.
- **spotify / giphy / unsplash** — media APIs; probably don't fit text
  embedding, but need shape sampling before exclusion.
- **legal spiders** (lii / findlaw / colorado_family_law / justia_family_law)
  — 100% [NO_ITEMS] but likely extractor misses on real content.

These are follow-up candidates, not exclusions.

## S2975: stale-empty-raw-data sentinel

Pre-2026-07-19, a cross-spider ingestion bug dropped response bodies,
leaving ~10.7K rows with `raw_data={}` that got correctly marked
`[NO_ITEMS]` but represent an artifact — the extractor is doing its
job, the *data* is missing. These rows dominated the 30d NO_ITEMS
rate (~89.5%) even though the bug fully self-resolved by 2026-07-19.

`cleanup_stale_no_items` (S2975) bumps those rows to a distinct
`[NO_ITEMS_STALE_EMPTY_RAW]` sentinel so they:
  - stay skipped by backfill (via `BACKFILL_SKIP_SENTINELS`),
  - stop being counted against operational NO_ITEMS metrics, and
  - remain observable as a separate `stale_empty_raw_data_total`
    bucket in `get_embedding_stats`.

Centralize the sentinel set here (not string literals across
callers) so predicate drift can't reintroduce the counting bug.
"""

from __future__ import annotations

from typing import FrozenSet


NO_ITEMS_SENTINEL: str = '[NO_ITEMS]'
STALE_EMPTY_SENTINEL: str = '[NO_ITEMS_STALE_EMPTY_RAW]'

BACKFILL_SKIP_SENTINELS: FrozenSet[str] = frozenset({
    NO_ITEMS_SENTINEL,
    STALE_EMPTY_SENTINEL,
})

EXCLUDED_SPIDER_NAMES: FrozenSet[str] = frozenset({
    'betting_coordinator',
    'discord_training',  # S2975: statistics-rollup shape, not embeddable content.
    'openmeteo',
})

EXCLUDED_DATA_TYPES: FrozenSet[str] = frozenset()
