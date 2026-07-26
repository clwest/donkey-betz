# SESSION 2975 — NO_ITEMS stale-ghost cleanup + Policy A expansion

**HEAD at close:** `8bd3daf3e` (PRs #3604 + #3605 + #3606 merged; docs cascade PR TBD)

**Branch shape:**
- `feat/s2975-cleanup-stale-no-items` → main (merged, branch deleted)
- `feat/s2975-policy-a-discord-training` → main (merged, branch deleted)
- `fix/s2975-spider-feed-stale-sentinel` → main (merged, branch deleted)

**Deliverables:**
- S2975 spec: `cb8a622c-ca94-4b96-b044-c5d7417955a8` — Engineering Spec (S2975): Continue NO_ITEMS discovery + targeted repairs (defer TheOdds key) — Rigby-drafted per Chris ratification, **third walk** of the Rigby-drafted-spec origination variant

**Support conversation:** `pa-f545685143384188` (fresh S2975 pin)

---

## Three-part summary (Chris-facing)

**What was done.** Seventh walk of the reframe pattern. Chris handed spec `cb8a622c` asking to classify + reduce [NO_ITEMS] for high-volume producers (theodds deferred). Sampled 25 rows/spider via Django ORM across FOUR candidates (discord_training, securityweek, remoteok, techcrunch_startups) **before writing any code** — the sampling picked the fix. Cross-spider audit revealed a system-wide pattern: **10,738 historical rows with `raw_data={}` AND `embedding_text='[NO_ITEMS]'`** — artifacts of a cross-spider ingest bug that fully self-resolved 2026-07-19. These ghosts dominated the 30d NO_ITEMS rate (89.5%) while 7d/24h rates were unaffected (0 ghost rows). Shipped 3 PRs: **#3604** — `cleanup_stale_no_items` command + observable `stale_empty_raw_data_total` bucket + centralized `BACKFILL_SKIP_SENTINELS` helper (Rigby T1 mitigation for predicate drift); **#3605** — `discord_training` added to Policy A (statistics-rollup shape confirmed by sampling); **#3606** — `spider_feed` bug fix (stale rows were leaking into `present` filter), caught by Rigby A2 SIGN grep spot-check. All merged with `--admin`; workers recycled per PLAYBOOK-7.4.4; live-verified.

**How it improves the platform.** Before: 30d NO_ITEMS rate was 86.7% — dominated by a resolved historical bug, making the intake-quality metric operationally useless; Feed Explorer would have shown 10.7K historical ghosts as if they were properly embedded content. After: **30d NO_ITEMS rate is 9.1%** (77.6-point drop; 10,728 rows flagged, not deleted); the metric now reflects reality across all spiders (not spider-specific — the fix benefits legislation, remoteok, huggingface, securityweek, techcrunch_startups, and 10+ others). `stale_empty_raw_data_total` bucket keeps the forensic evidence observable. `BACKFILL_SKIP_SENTINELS` centralizes the sentinel set so future additions can't accidentally reintroduce the counting bug. discord_training's 31 rows/30d correctly excluded from denominators alongside betting_coordinator + openmeteo.

**Next session first action.** Wait for Chris. Two seeds queued: (a) **remoteok pre-dedup filter** — spider-side fix in `ai_core/spiders/remoteok_spider.py` to skip the API's legal preamble item (S2975 sampling identified: `type: "item", legal: "API Terms of Service..."` with mutating `last_updated` field that beats dedup while real jobs get deduped); (b) **theodds auth-failure fix** — still spec-deferred, needs `THE_ODDS_API_KEY` rotation. Reframe fold trigger count = **7** (S2969→S2975) — Playbook rule candidate strengthened.

---

## Root cause narrative

Sampling 25 [NO_ITEMS] rows per spider across FOUR candidates (all high-volume producers per the S2973 breakdown endpoint) revealed a cross-spider historical class that S2974 saw one instance of (huggingface's Class 3) but was NOT flagged as system-wide.

**Four candidates, one shared pattern:**

| spider | 7d NO_ITEMS | 30d NO_ITEMS | dominant classes |
|---|---|---|---|
| discord_training | 30/30 (100%) | 204/204 (100%) | Class 1 rollup (statistics-dict item) + Class 2 empty runs |
| securityweek | 11/23 (48%) | ~193/30d | Class 2 all_deduped (current) + **Class 3 historical (self-resolved 2026-07-17)** |
| remoteok | ~11/7d | 188/211 (89%) | Class 1 (spider saves API legal preamble as unique item after dedup) + **Class 3 historical** |
| techcrunch_startups | 11/22 (50%) | ~192/30d | Class 2 empty runs (current) + **Class 3 historical (self-resolved 2026-07-17)** |

The cross-spider empirical claim: three unrelated spiders showed the SAME "last empty-raw-row date" — 2026-07-17. Combined with S2974's huggingface finding (same date), this triggered a system-wide audit.

**Cross-spider size:**
- **10,738 total** rows with `raw_data={}` AND `embedding_text='[NO_ITEMS]'` across all spiders, all time
- **7,323 of 8,183 (89.5%)** of the 30d NO_ITEMS window
- **0 of 850 (0.0%)** of the 7d NO_ITEMS window — bug fully self-resolved after 2026-07-19
- Temporal distribution (candidates by day): 2026-07-19 n=4, 2026-07-18 n=22, 2026-07-17 n=150, 2026-07-16 n=244, 2026-07-15 n=232, ... (200-460/day before 2026-07-17)
- Top affected: theodds(591), legislation(564 — matches S2974's unrecoverable-empty-raw count exactly), openmeteo(553), discord_training(547), remoteok(500), huggingface(249), then 15+ more spiders at 220+ each

**The fix (PR1):** Non-destructive reclassification. Rows matching `raw_data={} AND embedding_text='[NO_ITEMS]' AND created_at < 2026-07-19` bumped to a distinct `[NO_ITEMS_STALE_EMPTY_RAW]` sentinel. Backfill still skips them (via `BACKFILL_SKIP_SENTINELS` helper). `get_embedding_stats` exposes them in a separate observable `stale_empty_raw_data_total` bucket instead of counting them as NO_ITEMS. Reversible; audit trail preserved.

**discord_training (PR2):** Sampling confirmed 14/25 rows are a single-item statistics snapshot (`by_topic`, `high_quality_conversations`, `medium_quality_conversations`, `sample_formats`, `statistics`) and 11/25 are empty runs. Structurally not embeddable — legitimate Policy A addition.

**remoteok (deferred):** Sampling identified the spider is saving the remoteok API's legal preamble (`type: "item", legal: "API Terms of Service..."`) because its `last_updated` field mutates every fetch, beating dedup while real jobs get deduped (30 fetched, 29 duplicated, 1 "unique" = the preamble). Root cause is spider-side (`ai_core/spiders/remoteok_spider.py`), not policy — logged as follow-up seed for a dedicated arc.

**Spider Feed bug (PR3):** Rigby A2 SIGN grep spot-check surfaced two sites in `core/services/spider_feed.py` that filtered the literal `[NO_ITEMS]` string but not the new stale sentinel: `_embedding_status()` returned `'present'` for stale rows (would show 10.7K ghosts as embedded content in the UI); `query_spider_feed(embedding_status='present')` filter excluded only `[NO_ITEMS]`. Both fixed to use `BACKFILL_SKIP_SENTINELS`. This is EXACTLY the predicate-drift risk Rigby flagged in T1 zoom-out.

---

## Ground-truth numbers (quote verbatim in future work)

### From ORM sampling (pre-fix, HEAD `3ede6f398`)

Cross-spider ghost-row size:
| bucket | count | note |
|---|---|---|
| all-time raw_data={} + [NO_ITEMS] | 10,738 | historical Class 3 across all spiders |
| 30d NO_ITEMS total | 8,183 | |
| 30d NO_ITEMS with raw_data={} | 7,323 (89.5%) | dominated by the historical bug |
| 7d NO_ITEMS total | 850 | |
| 7d NO_ITEMS with raw_data={} | 0 (0.0%) | bug fully self-resolved |

### From live-verify (post-fix, HEAD `8bd3daf3e`, after `cleanup_stale_no_items --apply`)

| Metric | Pre-S2975 | Post-S2975 |
|---|---|---|
| total | 17,275 | 17,275 (unchanged) |
| present (embedded) | 5,657 | 5,677 (natural intake) |
| pending_eligible | ~0 | 0 |
| ineligible_empty | ~8,200 (mixed w/ ghosts) | 870 (real NO_ITEMS only) |
| stale_empty_raw_data_total | (didn't exist) | **10,728** (new observable bucket) |
| coverage_percent | 32.9% | 32.9% (unchanged — no embedding writes) |
| embeddable_coverage_percent | 100.0% | 100.0% |
| **30d no_items_rate** | 86.7% | **9.1%** (−77.6 pt) |
| **30d no_items_total** | 8,183 | **870** (−89.4%) |
| 7d no_items_rate | 41.0% | 41.0% (unchanged) |
| 24h no_items_rate | 71.0% (S2974 close) | 77.2% (natural drift, not S2975) |

### Top 5 by spider post-cleanup

**30d window (720h):**
1. theodds: 84 (spec-deferred)
2. openmeteo: 31 (Policy A)
3. discord_training: 31 (Policy A — PR2)
4. behance: 11
5. udemy: 11

**7d window (168h):**
1. theodds: 76
2. openmeteo: 30
3. discord_training: 30
4. coursera: 11
5. behance: 11

**Policy A now:** `['betting_coordinator', 'discord_training', 'openmeteo']` (was 2 names, now 3)

---

## SIGN cycle log (Rigby)

### T1 (pre-implementation, tool-grounded via search_docs)
- **All 4 items AGREE.** A2 (non-destructive) over A1 (delete). Default cutoff 2026-07-19. Two-PR split. Zoom-out refinement: add visible `stale_empty_raw_data_total` in breakdown; centralize predicate; consider optional `include_stale=1` param.
- Rigby cited existing precedent: `spider_semantic_search.backfill_embeddings` already non-destructively excludes `[NO_ITEMS]`.
- No F-BLOCKERs.

### A2 (post-ship verification, tool-grounded via kb_tool)
- **All 4 items AGREE.** Metric integrity check ("this is reclassification + explicit observability, not concealment"). Discord_training display OK (breakdown as audit lens; annotate with `excluded_by_policy` for UI). 
- **F-blocker-adjacent zoom-out**: "grep for missed `[NO_ITEMS]` predicate sites — main failure mode is a third call site that filters only the old sentinel but not the new one." Verified — surfaced 3 real gaps in `spider_feed.py`, shipped PR3 (#3606) same-session.
- Three follow-ups logged for future consumers: (a) semantic-change release note; (b) rollup logic that assumes `no_items_rate` semantics may need updating; (c) sentinel-sprawl watch (mitigation: centralized helper already in place).

---

## Live-verify results

```bash
# Live dry-run before apply (against prod DB, HEAD 5b1342e6e)
$ python manage.py cleanup_stale_no_items
=== cleanup_stale_no_items scope=all spiders before=2026-07-19T00:00:00+00:00 mode=DRY RUN ===
  candidates:  10,728
[dry-run] no rows modified. Re-run with --apply to flag.

# Live apply after worker recycle (HEAD 5b1342e6e)
$ python manage.py cleanup_stale_no_items --apply
=== cleanup_stale_no_items scope=all spiders before=2026-07-19T00:00:00+00:00 mode=APPLY ===
  candidates:  10,728
  flagged:     10,728
```

Endpoint verification (Django shell, HEAD `8bd3daf3e`):
```
excluded_spider_names: ['betting_coordinator', 'discord_training', 'openmeteo']  ✓
30d no_items_rate: 9.1%  (was 86.7% at S2974 close)
stale_empty_raw_data_total: 10,728  (matches apply count exactly)
```

Test suite: **65/65 pass** (`USE_PGBOUNCER=0 python manage.py test core.tests.test_signals_ui_api --keepdb`)
- 15 new S2975 tests covering: sentinel helper, bucket separation, backfill exclusion, command dry-run/apply/scoping/cutoff/limit/error paths, spider_feed status bucketing
- All 49 pre-existing tests unchanged and passing (S2971, S2972, S2973, S2974)

---

## PRs shipped

| PR | Title | Merge SHA |
|---|---|---|
| [#3604](https://github.com/clwest/donkey-betz-platform/pull/3604) | feat(s2975): cleanup stale NO_ITEMS ghost rows + observable bucket | `5b1342e6e` |
| [#3605](https://github.com/clwest/donkey-betz-platform/pull/3605) | feat(s2975): add discord_training to Policy A (statistics-rollup shape) | `e1c5d08bb` |
| [#3606](https://github.com/clwest/donkey-betz-platform/pull/3606) | fix(s2975): spider_feed embedding_status must include stale sentinel | `8bd3daf3e` |

## Follow-up seeds (Chris picks whether to open)

**remoteok pre-dedup filter (small mini-PR).** Sampling confirmed `ai_core/spiders/remoteok_spider.py` saves the remoteok API's legal preamble (`type: "item", legal: "API Terms of Service..."`) because its `last_updated` field mutates every fetch and beats dedup while real jobs get deduped (30 fetched, 29 duplicated, 1 "unique" = the preamble). Fix: pre-dedup filter to skip items where `type == "item"` AND `legal` is present. Small surface (one spider file); needs tests + a retriage_no_items --spider remoteok --apply after merge.

**theodds auth-failure fix (STILL OPEN from S2972+S2973+S2974).** Top NO_ITEMS producer at ~294 rows / 30d, unchanged. Fix requires Chris to rotate `THE_ODDS_API_KEY` (or verify API quota). Post-fix: re-run 24h + 30d breakdown to validate top-producers list re-ranks.

**huggingface `all_deduped` write suppression (STILL OPEN from S2974).** Spider writes an audit row every 30 min saying "all items were duplicates" — post-cleanup, this is one of the top 5 non-deferred producers (via `openmeteo` in the breakdown). Options: drop to a separate run-log table, or suppress writes on `diagnostic.status='success_empty'`. Small (~1-2 files touched) but touches spider write path — needs testing.

**Shape sampling for remaining top-10 producers post-cleanup.** After S2975, non-deferred top spiders are behance / udemy / coursera / freecodecamp (all at 11/30d). Sample ~10 rows each, classify per S2973+S2974 rubric. May yield another extractor-hardening win or 1-2 policy additions.

**Deliverable-as-spec fold @ trigger 7 — Playbook rule candidate.** Reframe pattern has now walked 7 times (S2969–S2975) across 3 variants (Chris-paste in S2969–S2972, Rigby-drafted in S2973+S2974+S2975). Threshold reached per PLAYBOOK §14.2 default two-trigger; well past for a rule proposal. Substrate ready.

---

## Candidate folds surfaced through S2975 (NOT codified)

1. **Rigby A2 SIGN grep spot-check catches predicate-drift bugs same-session.** **Trigger count: 1** (S2975 PR3). Rigby's tool-grounded A2 zoom-out surfaced 3 real `spider_feed.py` gaps that would have shipped as latent bugs. Same-PR-mitigatable — PR3 landed within the session. Watch for corroboration in future SIGN cycles that introduce new sentinels/predicates.

2. **Sampling picks the fix — CROSS-SPIDER extension.** **Trigger count: 2** (S2974 legislation + S2975 stale cleanup). S2974's fold was "sampling picks the fix for ONE spider". S2975 extends to "sampling ACROSS multiple spiders picks a SYSTEM-WIDE fix" — the cross-spider audit that identified the 10.7K historical Class 3 pattern only happened because I sampled 4 spiders with the deliberate intent to find shared patterns. Consider promoting the S2974 fold to include cross-spider sampling as an explicit sub-pattern.

3. **Deliverable-as-spec fold trigger 7** (S2969–S2975). Now well past PLAYBOOK §14.2 default two-trigger threshold. Third variant emerged this session (Rigby-drafted at S2973, S2974, S2975 — variant now has 3 instances).

---

## Session cost this session

Higher than S2974 (which was minimal) — S2975 had one extra safety-check PR:
- ~6 PA dispatches (fetch-spec / T1 / A2 post-ship / grep verification / potential final Rigby verification)
- 3 PRs shipped (2 planned via SIGN + 1 discovered via A2 grep spot-check)
- No v2 subprocess dispatches
- No revision cycles required — all 3 PRs landed clean at first attempt

Justified: cross-spider audit was strictly wider in scope than S2974's single-spider fix.
