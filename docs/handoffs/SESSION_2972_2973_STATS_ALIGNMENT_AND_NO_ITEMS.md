# SESSION 2972+2973 — Backfill stats-alignment + NO_ITEMS breakdown

**HEAD at close:** `fa3213b4c` (PRs #3599 + #3600 merged; docs cascade PR TBD)

**Branch shape:**
- `feat/s2972-backfill-stats-alignment` → main (merged, branch deleted)
- `feat/s2973-no-items-breakdown-policy` → main (merged, branch deleted)

**Deliverables:**
- S2972: `2f6e0cfa-39a3-485e-a77a-9f970728a4f5` — Fix Spider Embedding Backfill no-op + Align Signal Intelligence embedding coverage stats
- S2973: `64f9f576-7e4a-4520-89a6-858e696d7b16` — [NO_ITEMS] root-cause + searchable denominator policy + extractor hardening (Rigby-drafted per Chris ratification)

**Support conversation (shared):** `pa-3377eb5f247a`

---

## Three-part summary (Chris-facing)

**What was done.** Two-arc session. Chris reported the Signal Intelligence UI showing "25.3% coverage / 12,851 pending" while manually-triggered backfill returned `{skipped: concurrent run}`. Two problems fell out: (1) the lock hit was a transient beat collision — real backfill queue was **zero** because every "pending" row was already marked `[NO_ITEMS]`; (2) the stats UI conflated waiting-for-backfill with already-triaged-empty and used a stale 5,000-row sampling extrapolation that drifted 1% per session. S2972 fixed the stats contract (new `pending_eligible` / `ineligible_empty` split, direct COUNT queries, `embeddable_coverage_percent`). Live-verify surfaced the real story: **79.1% of new rows in the last 24h are marked [NO_ITEMS]** — the platform is writing lots of non-embeddable content into `LegacySpiderData`. Chris green-lit the follow-up arc; Rigby drafted the S2973 spec. S2973 added a `?include_breakdown=1&window=N` param to the coverage endpoint with top-10 producers by spider and data_type, a conservative 2-spider exclusion list (`betting_coordinator`, `openmeteo`), and a collapsible reveal in the existing CoverageCard. Ships in **two PRs**: #3599 (S2972) and #3600 (S2973). Both merged with `--admin`, workers recycled to `fa3213b4c`, all live-verified.

**How it improves the platform.** Before: Chris couldn't distinguish "backfill has real work" from "everything already triaged empty" without opening Django shell. Coverage widget over-reported pending, sampling drift moved the % between sessions. After: `/workspace?tab=intelligence&sub=signals` shows **three separate numbers** (embedded / eligible queue / no items) with tooltips; embeddable coverage reads 100% when the pipeline is healthy regardless of how many rollup rows exist; 24h intake-quality strip includes `no_items_rate`; expanding "Top no-items producers" reveals the ranked list with policy-badge markers. The API surface preserves every legacy field for backward compat. `coverage_percent` (legacy) went from 25.3% (with sampling drift) to 32.5% (exact count) — sampling was over-counting NULLs by ~28%.

**Next session first action.** Wait for Chris. Two obvious follow-up arcs are queued: (a) **theodds auth-failure fix** — needs Chris to rotate `THE_ODDS_API_KEY` (top NO_ITEMS producer at 294 rows / 30d); (b) **shape sampling for huggingface / legislation / discord_training / udemy** to classify their [NO_ITEMS] rows into rollup vs empty-run vs error-envelope before deciding on Policy A expansion. Reframe pattern (spec-pointer → SIGN → implement → live-verify → close) held for the fourth and fifth walk this session — fold 4 in candidate ledger now at trigger count 5.

---

## Root cause narrative (per Rigby's anchor request)

Backfill wasn't broken: **eligible backfill queue is genuinely empty** (`pending_eligible=0`) because embeddable rows embed within one 15-min beat cycle. The "stuck at ~25%" perception was a **stats-contract bug** (sampling/extrapolation drift + `pending` conflating `[NO_ITEMS]` with eligible work). The real issue is **intake quality / row semantics**: the platform is writing lots of non-embeddable rows and/or error envelopes into `LegacySpiderData`, yielding **very high `[NO_ITEMS]` rates** (79.1% 24h, 86.7% 30d).

---

## Ground-truth numbers (quote verbatim in future work)

### From S2972 live-verify (HEAD `615369e97`)
- `total = 17,195`
- `present = 5,596`
- `ineligible_empty ([NO_ITEMS]) = 11,599`
- `pending_eligible = 0`
- `embeddable_total = 5,596`
- `embeddable_coverage_percent = 100%`
- `coverage_percent (legacy present/total) = 32.5%` (previously ~25.3% via sampling drift)
- `recent_24h`: total 890, embedded 186, marked_no_items 704, still_pending 0, no_items_rate 79.1%

### From S2973 live-verify (HEAD `fa3213b4c`)
- `policy_excluded_total (lifetime) = 616` (exclusion list: `betting_coordinator`, `openmeteo`)
- 24h breakdown: total_rows 890, no_items_total 704, no_items_rate 79.1%
- 30d breakdown: total_rows 9,493, no_items_total 8,230, no_items_rate 86.7%

### Top NO_ITEMS producers
**24h top-5:** theodds 15, legislation 15, openmeteo 12, discord_training 12, udemy 10
**30d top-5:** theodds 294, legislation 255, openmeteo 212, discord_training 204, huggingface 193

**Insight:** huggingface is top-5 over 30d but not 24h → shape sampling before any exclusion.

---

## Classification framework — 3-shape NO_ITEMS model

Preserve for the next arc:

1. **Rollup / non-content rows (expected NO_ITEMS)** — e.g., `betting_coordinator` writes `top_plays` / `arbitrage` / `predictions` summaries; `openmeteo` returns weather metrics. Correctly marked [NO_ITEMS]; excluded from denominator in v1 Policy A.
2. **Empty-run / "no items fetched" rows** — spider produced zero usable items on a given run; often transient (finnhub sample: `diagnostic.status='success_empty'`, `empty_reason='no_items'`). Legitimate; keep in denominator.
3. **Error-envelope rows** — e.g., theodds returns `auth_failure_circuit_breaker` / `error_summary` envelopes when the API auth is broken. **Should be embeddable once fixed.** Excluding them would HIDE the auth-failure signal.

Rigby's sampling during S2973 T1 confirmed all three patterns exist in the current data.

---

## Policy A semantics (what Policy A does and does NOT do)

Policy A ships in S2973 as a conservative 2-spider exclusion list:
- `EXCLUDED_SPIDER_NAMES = frozenset({'betting_coordinator', 'openmeteo'})`
- `EXCLUDED_DATA_TYPES = frozenset()` (empty)

**What it does:**
- Adds `policy_excluded_total` (int) to every `/api/signals/embedding-coverage/` response — count of rows matching the exclusion list, regardless of embedding state.
- Reflects the current list into the breakdown response as `excluded_spider_names` + `excluded_data_types` sorted arrays, so the UI can render "Excludes: X, Y" without hardcoding.
- Marks excluded rows in the top-producers reveal with a "policy" badge.

**What it does NOT do:**
- Does **not** hide excluded rows from the breakdown (they still appear in the top-producers list).
- Does **not** create a new `coverage_percent_policy_v2` field (rejected in T1 pushback #1 as surface-area bloat).
- Does **not** touch `theodds`, legal spiders, media APIs — these need shape sampling before any exclusion (per module docstring guidance).

---

## The workflow reframe: walks 4 and 5

S2969 established the pattern. S2970 validated once. S2971 validated twice. **S2972 validates the third time; S2973 validates the fourth** — even more meaningfully because Chris ratified opening a new arc mid-session and Rigby drafted the spec (deliverable-as-spec origination pattern extended to Rigby-authored specs, not just Claude-authored).

The full 10-step reframe shape held for both:

1. Spec pointer arrives (Chris paste for S2972; Rigby draft on Chris ratification for S2973).
2. Claude reads spec + targeted "existing implementation analysis" (Cycle 1A).
3. T1 SIGN to Rigby with reuse-first plan + explicit zoom-out ask.
4. Fold Rigby's F-BLOCKERs and refinements.
5. Implement backend → tests → frontend → build check.
6. A2 SIGN with file+line evidence.
7. Merge with `--admin`, `make recycle-all`.
8. Live-verify in-shell (Django `Client().force_login`).
9. Rigby verifies from her tool surface (with the known limitation her `web_fetch_tool` can't carry session cookies).
10. Docs cascade + wrapper pin bump.

Cost per session in this shape: minimal — a handful of PA calls, no v2 subprocess dispatches. This session covered two full arcs (S2972 + S2973) in one terminal session — first time a session has back-to-backed two spec-driven arcs cleanly.

---

## Rigby's T1 folds — all shipped

### S2972 folds (all AGREE):
1. **Add last-24h intake-quality metric IN this PR** — shipped as `recent_24h.marked_no_items` / `still_pending` / `no_items_rate` fields.
2. **Extend widget, don't add a new tile** — CoverageCard reworked in place with explicit "Coverage (embeddable rows)" label + 3-cell strip + 24h line.
3. **Invariant test `pending == pending_eligible + ineligible_empty`** — `test_pending_invariant_equals_split_sum`.

### S2972 A2 refinements (all folded):
- Legacy-field grep sweep: only `core/tasks.py:1490` uses `get_embedding_stats()` legacy fields; all preserved.
- Log-line rephrase to numbers-only: `pending_null=X, triaged_no_items=Y, eligible=Z, batch_size=B, hours=H`.
- Defer legacy `coverage_percent` deprecation: keep both perspectives in the API surface.

### S2973 T1 pushbacks (all AGREE from Rigby):
1. **No `_policy_v2` percent fields** — added ONE `policy_excluded_total` int field instead.
2. **2-spider exclusion list max** — `betting_coordinator` + `openmeteo` only (theodds excluded from list to preserve the auth-failure signal).
3. **Breakdown inside CoverageCard, collapsible** — chevron toggle reveals inline; fetches only when opened.

### S2973 T1 refinement Rigby added:
- Expose `excluded_spider_names` + `excluded_data_types` in the breakdown payload so the UI reads them without hardcoding.

### S2973 A2 zoom-out reads (all AGREE):
- Keep query-key rotation on breakdown toggle (single query path; brief loader flicker acceptable).
- Defer theodds `auth_failure_circuit_breaker` badge — needs schema work, separate arc.
- Keep `policy_excluded_total` always-on — cheap, curated list.

---

## Shipped code

### S2972 (PR #3599)
**Backend (`core/`)**
- `services/spider_semantic_search.py` — rework `get_embedding_stats` (direct COUNT via `.aggregate()`, new bucket split + 24h intake-quality); add "0 eligible" logging in `backfill_embeddings`; add `NO_ITEMS_SENTINEL` constant.
- `tests/test_signals_ui_api.py` — new `EmbeddingCoverageStatsTests` class (4 tests) + update existing coverage mock.

**Frontend (`frontend/src/`)**
- `pages/workspace/tabs/signals/SignalsDashboardView.tsx` — extend `CoverageResponse` interface; rework `CoverageCard` with primary/subtext/24h-breakdown layout.

### S2973 (PR #3600)
**Backend (`core/`)**
- `services/no_items_policy.py` (NEW, 52 lines) — two frozensets + docstring explaining the conservative-v1 rationale + spiders deliberately NOT excluded.
- `services/spider_semantic_search.py` — extend `get_embedding_stats` with `include_breakdown` + `breakdown_window_hours` kwargs; add `policy_excluded_total`; new `_get_no_items_breakdown` helper.
- `views/signals_ui.py` — parse `?include_breakdown=1&window=N` on the embedding-coverage endpoint; new `SUPPORTED_BREAKDOWN_WINDOWS` constant.
- `tests/test_signals_ui_api.py` — 8 new tests across `NoItemsPolicyTests` + `SignalsBreakdownEndpointTests`.

**Frontend (`frontend/src/`)**
- `lib/api.ts` — typed params for `embeddingCoverage()`.
- `pages/workspace/tabs/signals/SignalsDashboardView.tsx` — collapsible "Top no-items producers (24h)" reveal in CoverageCard.

---

## Live-verify results (post-merge + recycle)

### S2972 (via Django `Client().force_login`, HTTP_HOST=localhost):

| Endpoint | Status | Payload highlights |
|---|---|---|
| `GET /api/signals/embedding-coverage/` | 200 | `pending_eligible=0`, `embeddable_coverage_percent=100.0`, `recent_24h.no_items_rate=79.1%` |

### S2973 (same shell pattern):

| Endpoint | Status | Payload highlights |
|---|---|---|
| `GET /api/signals/embedding-coverage/` (baseline) | 200 | `policy_excluded_total=616`, no breakdown block |
| `GET /api/signals/embedding-coverage/?include_breakdown=1&window=24` | 200 | 890 rows / 704 no_items (79.1%), top-5 spiders + data_types + excluded_spider_names |
| `GET /api/signals/embedding-coverage/?include_breakdown=1&window=720` | 200 | 9,493 rows / 8,230 no_items (86.7%), 30d ranking |
| `GET /api/signals/embedding-coverage/?include_breakdown=1&window=999` | 200 | Clamps to `window_hours=24` gracefully |

Test suites: 33/33 (S2972) then 41/41 (S2973) pass.

---

## Known follow-ups (Chris picks whether to open)

### High-value seeds for S2974
- **theodds auth-failure fix.** Top NO_ITEMS producer at 294 rows / 30d. Rigby confirmed rows carry `auth_failure_circuit_breaker` / `error_summary` envelopes. Fix requires Chris to rotate `THE_ODDS_API_KEY` (or verify quota). Post-fix: re-run 24h + 30d breakdown to validate the top-producers list re-ranks and 30d rate drops.
- **Shape sampling for huggingface / legislation / discord_training / udemy.** These are all in the top-5 producers at some window. Sample ~10 rows each, classify into rollup / empty-run / error-envelope. May yield 1-2 additions to the Policy A exclusion list, or may surface real extractor misses (Policy B territory).

### Deferred from S2972 spec
- **Backfill lock TTL / behavior review.** No action needed — lock working correctly; the observed "concurrent run" hit was a transient beat collision.

### Deferred from S2973 spec
- **Policy B (extractor hardening in `get_searchable_text`).** Separate arc after sampling.
- **NO_ITEMS discriminator field on `LegacySpiderData`.** Would tag rows as `rollup` / `empty` / `error_envelope` at write time. Needs schema work + spider-side annotation. Separate arc.
- **"Likely auth failure" badge in the top-producers reveal.** Deferred per A2 (needs per-row raw_data inspection at breakdown time).

### Standing (unchanged)
- Rail shortcut for `/signals` (~5 min, from S2971)
- Per-view window selector (from S2971)
- URL persistence for filter state (from S2971)
- "Create Initiative from Cluster" button (from S2971)
- `persistence.SpiderData` migration (from S2971)
- sports_injuries keyword tuning (from S2970)
- Worker egress validation arc (from S2969)

---

## Candidate folds surfaced this session (NOT codified)

**Trigger count building toward Playbook rules — do NOT amend without a second trigger unless otherwise noted:**

Carrying forward from S2969-S2971:

1. **Soft-key-vs-LLM-schema-gate.** **Trigger count: 1** (S2968).
2. **"Duplicate of a thing we already have" pattern.** **Trigger count: 2** (S2968).
3. **"Auditability primitive already exists in a different plane" pattern.** **Trigger count: 1** (S2969).
4. **"Deliverable-as-spec first walk validates the workflow reframe."** **Trigger count: 5** (S2969-S2973). **Five-trigger corpus reached; strong Playbook rule candidate.** Two variants observed: Chris-paste (S2969/2970/2971/2972) and Rigby-drafted-per-Chris-ratification (S2973). Both walk the same 10-step shape. Consider proposing as a Playbook §5 or §6 rule at S2974 session close.
5. **"Live-verify surfaces the real root cause the observability layer was designed to expose."** **Trigger count: 2** (S2970, S2972). Second corroboration this session — the "0 eligible / 79.1% no-items" story only surfaced because live-verify hit the actual endpoint with real data. Watch for a third.
6. **"Post-merge live-verify reveals scope-adjacent infra bug; scope-in a flag-gated fix, don't defer."** **Trigger count: 1** (S2970).
7. **"Route-placement is a settable expectation, not a spec constraint."** **Trigger count: 1** (S2971).
8. **"Rigby web_fetch_tool can't authenticate against Django session-cookie endpoints."** **Trigger count: 2** (S2971, S2972 — she confirmed she still can't authenticate via web_fetch). Consider adding to Rigby Tool Gap Ledger — second occurrence promotes it from candidate to logged gap per feedback_rigby_tool_gap_ledger.

New at S2972-S2973:

9. **"Rigby-drafted spec deliverable is a first-class origination path."** S2973 opened by Chris ratifying my option-b close-note; I asked Rigby to draft the spec; she used `deliverable_tool.create` + `kb_tool` + raw ORM queries to author a thorough spec (Deliverable ID `64f9f576...`) I then implemented against. Different origination than S2969-S2972 (Chris-paste). **Trigger count: 1** (S2973). Watch for a second — could formalize as a variant of the reframe pattern under fold #4.

10. **"Sampling extrapolation past ~10k rows produces cross-session drift."** S2972's `get_embedding_stats` sampled 5,000 rows and extrapolated by `total/sample_size` — at 17,195 rows the extrapolation factor was 3.44x, causing 25.3% (S2971) vs 32.5% (S2972 exact) coverage drift. Direct COUNT is cheap at this scale and eliminates drift. **Trigger count: 1** (S2972). Could generalize to a rule about avoiding sampling for numbers reported in operator UI.

---

## Post-close addendum

**S2972+S2973 pipeline stats (as of live-verify at HEAD `fa3213b4c`):**
- Total LegacySpiderData rows: 17,195
- Embedded (searchable): 5,596 (32.5% of total; 100% of embeddable)
- Ineligible empty ([NO_ITEMS]): 11,599 (67.5% of total)
- Real backfill queue: 0
- Policy-excluded lifetime: 616 (from `betting_coordinator` + `openmeteo`)
- 24h intake-quality: 890 new rows / 186 embedded / 704 marked no_items → 79.1% no_items rate
- 30d intake-quality: 9,493 rows / ~1,263 embedded / 8,230 marked no_items → 86.7% no_items rate

Backfill Beat task (`backfill-spider-embeddings`) continues to run every 15 min per prior schedule. No behavior change to the backfill queryset — only observability + logging additions.

---

## What's forbidden at S2974 (carry-forward)

All prior forbidden entries carry forward. Nothing new at S2972 or S2973.

- Do not automatically merge S2968 PR-B.
- Do not proactively dispatch v2 test runs at session open.
- Do not chase spider parsing bugs for reddit / sports_injuries (fixed S2970).
- Do not flip `SPIDER_USE_THREADED_DNS_RESOLVER` off in this env.
- **New: Do NOT expand the Policy A exclusion list without shape sampling first** — false exclusions HIDE real data-quality bugs (theodds auth failure, extractor misses). Sample before adding.

---

## For fuller context (S2846 → S2973)

- **S2972+S2973 handoff (current):** `docs/handoffs/SESSION_2972_2973_STATS_ALIGNMENT_AND_NO_ITEMS.md`
- **S2972 shipped code:** PR #3599 (`feat(s2972): fix backfill stats-alignment — pending_eligible bucket + 24h intake-quality metric`)
- **S2973 shipped code:** PR #3600 (`feat(s2973): NO_ITEMS breakdown + Policy A denominator exclusion (2-spider start)`)
- **S2972 spec deliverable:** `2f6e0cfa-39a3-485e-a77a-9f970728a4f5`
- **S2973 spec deliverable:** `64f9f576-7e4a-4520-89a6-858e696d7b16` (Rigby-drafted)
- **Support conversation (shared):** `pa-3377eb5f247a`
- **S2971 handoff:** `docs/handoffs/SESSION_2971_SIGNAL_INTELLIGENCE_UI.md`
- **S2970 handoff:** `docs/handoffs/SESSION_2970_PR_B_RSS_FIRST.md`
- **S2969 handoff:** `docs/handoffs/SESSION_2969_SPIDER_DIAGNOSTIC_PERSISTENCE.md`
- **S2968 handoff:** `docs/handoffs/SESSION_2968_OPTION_BETA_AND_REFRAME.md`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
