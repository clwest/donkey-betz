# SESSION 2974 — Legislation extractor hardening + retriage

**HEAD at close:** `c331a0404` (PR #3602 merged; docs cascade PR TBD)

**Branch shape:**
- `feat/s2974-legislation-extractor-hardening` → main (merged, branch deleted)

**Deliverables:**
- S2974 spec: `914b1118-4eed-4abf-8c84-86ff42a459c3` — Engineering Spec: Classify & Reduce [NO_ITEMS] for huggingface + legislation (Rigby-drafted per Chris ratification, second walk of the Rigby-drafted-spec origination variant)

**Support conversation:** `pa-3377eb5f247a` (shared with S2972+S2973)

---

## Three-part summary (Chris-facing)

**What was done.** Sixth walk of the reframe pattern. Chris handed spec deliverable `914b1118` asking to classify + reduce [NO_ITEMS] for huggingface + legislation. I sampled 25 [NO_ITEMS] rows per spider via Django ORM **before writing any code** — the sampling itself picked the fix. Huggingface's recent NO_ITEMS is 100% legitimate `all_deduped` (spider ran, everything was a duplicate; the historical 95.1% 30d rate is a moving-window artifact from Class 3 rows that self-resolved 2026-07-17). Legislation was 100% Class 4: every item is a wrapped envelope with pre-computed `item['embedding_text']` like `"H7030. Establishes the healthcare worker platform..."` — the extractor just never looked there. Fix at `core/models_unified_system.py:3898`: new `_extract_item_text` helper supports three shapes (spider-provided embedding_text with sentinel + length guards, nested `item['raw_data']`, flat top-level unchanged) + new `retriage_no_items --spider <name> [--apply]` command that recomputes and clears the sentinel only where the new extractor returns text. PR #3602 merged with `--admin`; workers recycled to `c331a0404`; retriage applied; 61 rows re-embedded. All 5 Rigby T1 folds shipped. 50/50 tests pass.

**How it improves the platform.** Before: legislation was 100% NO_ITEMS across ALL time (625 rows, 0 embedded); 24h intake NO_ITEMS rate 79.1%; legislative bill data was invisible to search. After: 61 legislative bills (all 7d rows) recovered from limbo — every bill now searchable including H7030 (RI Healthcare Worker Platform Act) as a working proof; 24h NO_ITEMS rate dropped **79.1% → 71.0%** (~10 points from one spider's fix); 7d rate 38.1%; legislation dropped OFF the top-20 producers in both 24h and 7d windows. Durable: new legislation rows going forward embed at 100% (was 0%). 564 historical rows with `raw_data={}` are unrecoverable — same Class 3 pattern huggingface resolved 9 days ago (data gone at ingest time).

**Next session first action.** Wait for Chris. Two follow-up seeds queued: (a) **huggingface `all_deduped` write suppression** — spider writes an audit row every 30 min for "all items were duplicates"; consider dropping to a run-log table (Rigby's suggested follow-up); (b) **theodds auth-failure fix** — still top NO_ITEMS producer at ~294 rows/30d, unchanged from S2972; needs Chris to rotate `THE_ODDS_API_KEY`. Reframe fold trigger count = **6** (S2969→S2974) — strong Playbook rule candidate at S2975 close if the pattern holds one more walk.

---

## Root cause narrative

**huggingface** — the "95.1% 30d NO_ITEMS rate" was misleading. Sampling revealed two distinct classes:
- Class 3 (184 rows, 2026-06-27 → 2026-07-17): `raw_data={}` empty dict, `source_url=https://huggingface.co/api/models?...` — spider dropped response body somewhere; ROW-BUG that self-resolved 2026-07-17 (last empty-raw row).
- Class 2 (9 rows, 2026-07-26 today): `diagnostic.status=success_empty, empty_reason=all_deduped, duplicates=49` — spider ran fine, all items were dupes. Legitimate.
- **No fix needed.** The high-rate 30d window is stale.

**legislation** — the "100% NO_ITEMS across all time" was a pure extractor mismatch. Sampling revealed every item is a WRAPPED envelope:
```json
{
  "data_type": "bill_summary",
  "platform": "legislation",
  "tags": [...],
  "embedding_text": "H7030. Establishes the healthcare worker platform...",  ← pre-computed
  "raw_data": {                                                                ← nested content
    "bill_number": "H7030",
    "title": "...",
    "description": "...",
    "sponsors": [...],
    ...
  }
}
```
The pre-S2974 extractor only looked at `item['title']|['name']|['modelId']|['id']` at TOP level — none present at top level in the wrapped shape, so every item contributed zero text, every row got marked [NO_ITEMS]. Cross-spider audit: legislation is the ONLY spider with this shape across the top-20 [NO_ITEMS] producers.

---

## Ground-truth numbers (quote verbatim in future work)

### From ORM sampling (pre-fix, HEAD `fa3213b4c`)

| spider | window | total | [NO_ITEMS] | rate |
|---|---|---|---|---|
| huggingface | 7d | 18 | 9 | 50.0% |
| huggingface | 30d | 203 | 193 | 95.1% |
| huggingface | lifetime | 573 | 258 | 45.0% |
| legislation | 7d | 61 | 61 | 100% |
| legislation | 30d | 255 | 255 | 100% |
| legislation | lifetime | 625 | 625 | 100% |

### Huggingface 30d class distribution (pre-fix)
- Class 3 (empty raw_data, historical): 184 / 193
- Class 2 (all_deduped, current): 9 / 193
- Last empty-raw row: 2026-07-17T22:10
- First all_deduped row: 2026-07-26 (today)

### From live-verify (post-fix, HEAD `c331a0404`, after `retriage_no_items --spider legislation --apply` + direct backfill)

| Metric | Pre-S2974 | Post-S2974 |
|---|---|---|
| present (embedded rows) | 5,596 | **5,657** (+61) |
| coverage_percent (legacy) | 32.5% | **32.9%** |
| embeddable_coverage_percent | 100.0% | 100.0% |
| 24h no_items_rate | 79.1% | **71.0%** |
| 7d no_items_rate | — | **38.1%** |
| 30d no_items_rate | 86.7% | **85.3%** |
| legislation lifetime | 625 total / 0 embedded / 625 [NO_ITEMS] | **626 total / 61 embedded / 564 [NO_ITEMS]** |
| legislation in top-20 (24h) | top-2 at 15 | **OFF top-20** |
| legislation in top-20 (7d) | top-1 at 61 | **OFF top-20** |
| legislation in top-20 (30d) | top-2 at 255 | still present at 193 (older unrecoverable rows) |

### Retriage apply
```
scanned:  625
cleared:  61   (7d wrapped-shape rows — extractor now returns text)
still empty: 564  (historical raw_data={} rows — unrecoverable Class 3)
```

### Backfill (direct call, batch=100, hours=720)
```
processed: 61, succeeded: 61, failed: 0, skipped: 0, marked_empty: 0
```

### Recovered row proof
```
id: d3ee2c75-c8e8-44f0-bed1-2ac459c682df
created_at: 2026-07-26T12:31:11
embedding_text[:200]: "H7030. Establishes the healthcare worker platform and would
                        require platforms offering healthcare shifts to register with
                        the department of health by June 1, 2027..."
embedding.shape: (1536,)
```

Rigby's semantic search from her tool surface returned this row as top match for query "healthcare worker platform" post-merge.

---

## The workflow reframe: walk 6

S2969 established the pattern. S2970–S2973 validated 4 more times. **S2974 validates the sixth walk.** Second walk of the Rigby-drafted-spec origination variant (S2973 was first).

The full 10-step reframe shape held:

1. Spec pointer arrives (Chris relays Rigby-drafted deliverable `914b1118`).
2. Claude reads spec + targeted "existing implementation analysis" (Cycle 1A — 4 parallel greps/reads for extractor + sentinel + spider code).
3. **Sampled 25 rows/spider via ORM BEFORE T1 SIGN** — sampling picked the fix; T1 SIGN was evidence-grounded, not plan-based.
4. T1 SIGN to Rigby with reuse-first plan + explicit zoom-out ask (5 questions).
5. Rigby AGREE + 5 substantive folds (no F-BLOCKERs).
6. Fold all 5; implement backend + tests + management command.
7. A2 SIGN with file+line evidence + correction on expected impact numbers (dry-run revealed 61/625 recoverable, not 100%).
8. Rigby AGREE + optional operator-proof suggestion.
9. Merge with `--admin`, `make recycle-all`, `retriage --apply`, direct backfill call.
10. Live-verify in-shell (Django Client().force_login, HTTP_HOST=localhost) + Rigby tool-surface verify + PR comment with before/after table.

**Cost this session:** minimal — 5 PA turns (fetch-spec / T1 / A2 / tool-verify / verdict), no v2 subprocess dispatches, no back-and-forth revision cycles.

---

## Rigby's T1 folds — all shipped

1. **HF `all_deduped` write cadence** — deferred to follow-up (agreed, don't expand scope).
2. **Guards on `item['embedding_text']`** — reject sentinels (`''`, `[NO_ITEMS]`, `[EMPTY]`, `[NONE]`), require ≥20 chars OR title fallback, cap per-item text at 1000 chars.
3. **Retriage as management command** — `retriage_no_items --spider <name> [--apply] [--days N] [--limit N]` — recompute-driven clear only where new extractor returns text; dry-run default; `--spider` required.
4. **Regression test** for "flat item missing title|name|id → 0 text" added.
5. **PR body notes the invariant** — backfill excludes `[NO_ITEMS]` by design (`core/services/spider_semantic_search.py:457`); extractor improvements do NOT retroactively re-embed; explicit sentinel-clear required.

## Rigby's A2 refinements — all noted

- Optional allowlist regex on `--spider` — not needed (argparse required + no shell expansion path).
- 1000-char cap is reasonable for legislation; module constant leaves knob for future tuning.
- Sentinel list staleness is low-risk (defense-in-depth is enough).
- Added the operator-proof before/after table as PR #3602 comment per Rigby's suggestion.

---

## Shipped code

### PR #3602 — `feat/s2974-legislation-extractor-hardening`

**Backend (`core/`)**
- `models_unified_system.py:54-102` — new module-level helpers `_TITLE_FIELDS`, `_DESC_FIELDS`, `_has_title_like_field`, `_build_flat_item_text`.
- `models_unified_system.py:3898-3961` — reworked `LegacySpiderData.get_searchable_text` + new `_extract_item_text` classmethod with sentinel + length + per-item cap guards.
- `management/commands/retriage_no_items.py` (NEW, 105 lines) — recompute-driven sentinel-clear command.
- `tests/test_signals_ui_api.py:572-670` — new `GetSearchableTextExtractorTests` class (9 tests).

---

## Live-verify results

### Coverage endpoint via Django `Client().force_login`, `HTTP_HOST='localhost'`

| Query | Status | Payload highlight |
|---|---|---|
| `GET /api/signals/embedding-coverage/?include_breakdown=1&window=168` | 200 | `total=17,195 present=5,657 coverage_percent=32.9%` |

### Direct stats via `SpiderSemanticSearch.get_embedding_stats(include_breakdown=True, breakdown_window_hours=168)`

| window | total_rows | no_items_total | no_items_rate | legislation in top-20 |
|---|---|---|---|---|
| 24h | 970 | 689 | 71.0% | **OFF** |
| 7d | 2,075 | 790 | 38.1% | **OFF** |
| 30d | 9,527 | 8,123 | 85.3% | present at 193 (older unrecoverable) |

### Test suite
`USE_PGBOUNCER=0 python manage.py test core.tests.test_signals_ui_api -v0 --keepdb` → **50/50 pass** (41 prior + 9 new).

---

## Known follow-ups (Chris picks whether to open)

### High-value seeds for S2975
- **huggingface `all_deduped` write suppression.** Rigby's suggested follow-up during T1: spider currently writes an audit row every 30 min for "all items were duplicates" — arguably a data-hygiene concern of its own. Consider dropping to a separate run-log table or suppressing writes on `success_empty` diagnostic status. Not urgent (only 9 rows / day) but adds noise to intake metrics.
- **theodds auth-failure fix.** Unchanged from S2972+S2973. Top NO_ITEMS producer at ~294 rows / 30d. Rigby confirmed rows carry `auth_failure_circuit_breaker` / `error_summary` envelopes. Fix requires Chris to rotate `THE_ODDS_API_KEY` (or verify quota).
- **Shape sampling for remaining top producers** — `securityweek`, `udemy`, `colorado_family_law`, `behance`, `freecodecamp`, `techcrunch_startups`, `education_rss` (all tied at 10 rows in 7d top-10). Could yield another extractor-hardening win or policy exclusions.

### Deferred from S2974 spec
- **Policy B (further extractor hardening)** — none needed for this arc; the wrapped-item helper already covers the primary miss.
- **NO_ITEMS discriminator field on `LegacySpiderData`** — would tag rows as `rollup` / `empty` / `error_envelope` at write time. Still deferred pending schema work.

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

Carrying forward from S2969-S2973:

1. **Soft-key-vs-LLM-schema-gate.** **Trigger count: 1** (S2968).
2. **"Duplicate of a thing we already have" pattern.** **Trigger count: 2** (S2968).
3. **"Auditability primitive already exists in a different plane" pattern.** **Trigger count: 1** (S2969).
4. **"Deliverable-as-spec first walk validates the workflow reframe."** **Trigger count: 6** (S2969-S2974). **Six-trigger corpus. Strong Playbook rule candidate.** Two variants observed: Chris-paste (S2969/2970/2971/2972) and Rigby-drafted-per-Chris-ratification (S2973, S2974). Both walk the same 10-step shape. **Recommend proposing as a Playbook §5 or §6 rule at S2975 session close if the pattern holds one more walk.**
5. **"Live-verify surfaces the real root cause the observability layer was designed to expose."** **Trigger count: 3** (S2970, S2972, S2974). At S2974: sampling via ORM (the observability plane) picked the fix — huggingface's 30d "high rate" was exposed as historical + resolved; legislation's "100%" was exposed as a single-line extractor gap. Watch for a fourth.
6. **"Post-merge live-verify reveals scope-adjacent infra bug; scope-in a flag-gated fix, don't defer."** **Trigger count: 1** (S2970).
7. **"Route-placement is a settable expectation, not a spec constraint."** **Trigger count: 1** (S2971).
8. **"Rigby web_fetch_tool can't authenticate against Django session-cookie endpoints."** **Trigger count: 2** (S2971, S2972). Not surfaced at S2974 (avoided auth-gated verification by handing Rigby ORM-inspectable proofs).
9. **"Rigby-drafted spec deliverable is a first-class origination path."** **Trigger count: 2** (S2973, S2974). Second occurrence — could formalize as a variant of the reframe pattern under fold #4.
10. **"Sampling extrapolation past ~10k rows produces cross-session drift."** **Trigger count: 1** (S2972).

New at S2974:

11. **"Sample-before-plan cuts T1 revision cycles to zero."** **Trigger count: 1** (S2974). I ran the 25-row-per-spider sampling BEFORE drafting T1 — sampling revealed both the huggingface "no fix needed" and the legislation single-line extractor gap. T1 SIGN was evidence-grounded, Rigby returned 5 refinements + zero F-BLOCKERs on first turn, no revision cycle. Contrast with plan-first T1 SIGNs which often eat 1-2 revision loops before Rigby has enough evidence to AGREE. Watch for a second occurrence — could become a rule about "for diagnostic-shape arcs, complete the diagnostic BEFORE T1 SIGN".

12. **"Retriage-command-as-primitive over blanket ORM update"** — first walk of the pattern "when extractor improvement retroactively unblocks marked rows, ship a recompute-driven clear command rather than a blanket ORM update or a generic 're-triage all' primitive." Balances YAGNI (no over-general primitive) against auditability (dry-run default; explicit spider required; counts logged). **Trigger count: 1** (S2974). Watch for a second when the next extractor improvement lands.

---

## Post-close addendum

**S2974 pipeline stats (as of live-verify at HEAD `c331a0404`):**
- Total LegacySpiderData rows: 17,195 → 17,196 (small drift from ~15 min of intake during the session)
- Embedded (searchable): 5,596 → **5,657** (+61 legislative bills)
- Ineligible empty ([NO_ITEMS]): 11,599 → **11,538** (-61)
- Real backfill queue: 0
- Policy-excluded lifetime: 616 (unchanged — `betting_coordinator` + `openmeteo`)
- 24h intake NO_ITEMS rate: 79.1% → **71.0%**
- 7d intake NO_ITEMS rate: — → **38.1%**
- 30d intake NO_ITEMS rate: 86.7% → **85.3%**

Legislation-specific:
- Lifetime: 625 → 626 total; 0 → 61 embedded; 625 → 564 [NO_ITEMS]
- Dropped OFF top-20 producers in 24h AND 7d windows
- Still visible in 30d top-20 at ~193 (older unrecoverable rows will fade as the window rolls forward)

---

## What's forbidden at S2975 (carry-forward)

All prior forbidden entries carry forward. Nothing new at S2974.

- Do not automatically merge S2968 PR-B.
- Do not proactively dispatch v2 test runs at session open.
- Do not chase spider parsing bugs for reddit / sports_injuries (fixed S2970).
- Do not flip `SPIDER_USE_THREADED_DNS_RESOLVER` off in this env.
- **Do NOT expand the Policy A exclusion list without shape sampling first** (from S2973) — false exclusions HIDE real data-quality bugs. Sample before adding.
- **NEW: Do NOT clear `[NO_ITEMS]` sentinels via blanket ORM update.** Always route through `retriage_no_items --spider <name>` which recomputes `get_searchable_text` per row and clears only where non-empty. Blanket clears cause backfill thrash (rows re-mark themselves).

---

## For fuller context (S2846 → S2974)

- **S2974 handoff (current):** `docs/handoffs/SESSION_2974_LEGISLATION_EXTRACTOR.md`
- **S2974 shipped code:** PR #3602 (`feat(s2974): legislation extractor hardening — wrapped-item shape support + retriage command`)
- **S2974 spec deliverable:** `914b1118-4eed-4abf-8c84-86ff42a459c3` (Rigby-drafted)
- **Support conversation (shared):** `pa-3377eb5f247a`
- **S2972+S2973 handoff:** `docs/handoffs/SESSION_2972_2973_STATS_ALIGNMENT_AND_NO_ITEMS.md`
- **S2971 handoff:** `docs/handoffs/SESSION_2971_SIGNAL_INTELLIGENCE_UI.md`
- **S2970 handoff:** `docs/handoffs/SESSION_2970_PR_B_RSS_FIRST.md`
- **S2969 handoff:** `docs/handoffs/SESSION_2969_SPIDER_DIAGNOSTIC_PERSISTENCE.md`
- **S2968 handoff:** `docs/handoffs/SESSION_2968_OPTION_BETA_AND_REFRAME.md`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
