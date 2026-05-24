---
title: "Session 1140 — (A) Action-card pre-generation, vertical slice complete"
date: 2026-05-24
status: merged
session: 1140
previous_handoff: SESSION_1140_CLUSTER_METHOD_MIRROR_AND_JUDGE_STATS.md
next_session_primary: Read v1 rejection rate once sample reaches n≥20 (Session 1139 acceptance — unchanged)
team: chris + claude + rigby (PR-review on all three PRs)
udb_pr: 2174
signal_studio_ingest_pr: 18
signal_studio_frontend_pr: 19
udb_merge_commit: 1c268726
signal_studio_ingest_merge_commit: 3f279730
signal_studio_frontend_merge_commit: 11bee51f
udb_merged_at: 2026-05-24T22:39:19Z
signal_studio_ingest_merged_at: 2026-05-24T22:39:03Z
signal_studio_frontend_merged_at: 2026-05-24T22:54:16Z
---

# Session 1140 — (A) Action-card pre-generation vertical slice

> **Read this if** you want the Session 1140 (A) action-card slice
> details — Rigby's locked design contract, the three-PR split, what
> ships in each layer, the empirical findings from real-LLM smoke,
> and what carries into Session 1141.
>
> **Companion to** the earlier-in-session
> [SESSION_1140_CLUSTER_METHOD_MIRROR_AND_JUDGE_STATS](SESSION_1140_CLUSTER_METHOD_MIRROR_AND_JUDGE_STATS.md)
> handoff which covered the mirror + judge-stats tool. Both shipped
> in the same Session 1140 window.

## TL;DR

**Closed carryover (A) from the start-here.** Curated snapshots now ship
with LLM-generated action cards paired 1:1 with each cluster_pick. The
data flow runs end-to-end through three coordinated PRs (u-d-b backend
+ signal-studio mirror + signal-studio frontend), all merged today.
Curated tab → click any cluster → "Suggested Next Steps" section
renders action_type badge + status pill + concrete steps + outreach
draft (when populated).

Rigby's design locks (conversation `pa-d19c1674b936`) drove the shape:
typed `CuratedSignalEntry` rows (NOT payload blob), two-phase u-d-b flow
(snapshot stays pure-deterministic, action gen is async + non-fatal),
mirror signal-studio's existing ActionCard fields, evergreen tool
descriptions (no SLO numbers in LLM-facing schemas). Three PR reviews
mid-build caught the merge-blocker bugs and locked the user-facing copy
before merge.

**Acceptance bar (Q5) — vertical slice met:**
- ✅ 10 cluster_pick rows from snapshot in u-d-b
- ✅ 10 matching action_card rows in u-d-b
- ✅ Mirror ingests both via `signal.curated_actions_ready` event
- ✅ Curated tab renders actions inline (visual-verified via Playwright)
- ✅ ≥3 cards with non-empty outreach drafts (4 in current snapshot)
- ✅ Failure modes graceful (`needs_regen` status flag + amber UI tint)

## What landed (3 PRs)

### u-d-b PR [#2174](https://github.com/clwest/donkey-betz-platform/pull/2174) → `1c268726`

Source branch: `feat/session-1140-curated-action-cards-backend` (3 commits before squash). Backend + emit half of the slice.

| Path | Change |
|---|---|
| `core/migrations/0352_session_1140_typed_curated_entries.py` | Typed `CuratedSignalEntry` extension: `entry_type` discriminator + nullable cluster_pick-only fields + new action_card fields + `unique(snapshot, cluster, entry_type)` constraint (replaces old `unique(snapshot, rank)`). |
| `core/migrations/0353_session_1140_action_status_needs_regen.py` | Rigby PR-review fix-up: extends `ACTION_STATUS_CHOICES` with `needs_regen` + reverts Meta.ordering to drop `entry_type` (alphabetical sort would've put action_card before its paired pick). |
| `core/models_signal_intelligence.py` | `CuratedSignalEntry` model code matching the migrations. |
| `core/services/curated_action_card_generator.py` | New. LLM (gpt-5-mini, `max_completion_tokens=1500`) → JSON parse → normalize → persist. Soft fallback always returns a usable card; idempotent on retries. |
| `core/services/signal_curator_service.py` | New `build_curated_actions_envelope` + `emit_curated_actions_ready` for the second fleet event. |
| `core/tasks.py` | New `generate_curated_action_cards` celery task on `long_running` queue. |
| `core/tasks_spiders.py` | `_impl_curate_signal_clusters` auto-schedules action-gen follow-on on success (non-fatal). |
| `tests/services/test_curated_action_card_generator.py` | 35 unit tests (pure functions + mocked OpenAI). |

### signal-studio PR [#18](https://github.com/clwest/signal-studio/pull/18) → `3f279730`

Source branch: `feat/session-1140-curated-actions-ingest` (2 commits before squash). Mirror ingest of the new event.

| Path | Change |
|---|---|
| `backend/app/models.py` | `ActionCard.external_id` (u-d-b CuratedSignalEntry.id, unique-where-not-null) + `ActionCard.generated_by` (audit). NULL on legacy on-demand cards. |
| `backend/app/signal_ingest.py` | New `_apply_curated_actions` handler routed off `signal.curated_actions_ready`. Idempotent upsert by `external_id`. Missing cluster = silent skip + log (per Rigby's no-dual-upsert-path lock). `_ensure_schema` extended for new columns + partial unique index. |
| `backend/tests/test_curated_actions_ingest.py` | 11 unit tests covering schema, happy path, missing cluster, idempotent re-emit, mixed present/missing, empty payload, status vocab passthrough. |

### signal-studio PR [#19](https://github.com/clwest/signal-studio/pull/19) → `11bee51f`

Source branch: `feat/session-1140-curated-actions-frontend` (2 commits before squash). Last-mile UI per `feedback_vertical_slice.md`.

| Path | Change |
|---|---|
| `backend/app/main.py` | `/api/signals/{id}` action_cards response gains `outreach_draft` + `external_id` + `generated_by` + derived `is_curated_pregen` boolean. |
| `frontend/src/App.tsx` | `ActionCardData` interface extended. "Action Plan" header → "Suggested Next Steps" when any card is curated-pregen. Per-card header row with action_type badge (color per type), status pill ("AI draft" / "Needs retry"), `generated_by` audit label. Border color differentiates real-LLM (blue-purple) from `needs_regen` (amber-tinted). New outreach_draft block (monospace, preserved line breaks) when populated. |

## Empirical findings worth saving

**`max_completion_tokens=600` returned 100% empty content from gpt-5-mini.** Reasoning tokens consumed the entire budget before output emission. Bumped to 1500 — 80% real LLM / 20% fallback observed across smoke runs. Cost ≈ $0.003/card, $0.03/day at the Top-10 cadence. Distinct warning log on the empty-response path so this can be triaged from logs vs genuine JSON parse failures.

**Local pgvector dependency.** The action-card generation depends on `aggregate_spider_signals` producing real cluster rows for the curator to score. That depends on `SpiderData` queries succeeding — which depended on the pgvector blocker closing earlier in the same session (#2172, `3ec9e074`). Without that fix this entire slice would have run against empty / stale clusters.

**Soft-fallback shape choice.** Per Rigby Q2 + Q3 reviews: every cluster ALWAYS gets a row, never half-row UI. Fallback rows are explicitly tagged via two independent fields:
- `generated_by='fallback_placeholder'` (audit metadata)
- `action_status='needs_regen'` (queryable status separate from audit)

That separation enables a future regen-path scheduler to filter on status without coupling to the audit field. Future PR territory.

**Real LLM output quality (sample from live smoke):**
- "Audit Reuters 'Trump' coverage for immediate product / PR risk" — investigate
- "Offer an immediate 30-day pilot to top 20 prospects" + outreach DM — pitch
- "Run a 24-hour trend validation sprint" — investigate
- "Launch Cybersecurity Upskilling Program" + 4-step concrete plan — build
- "Hire top in-demand skills: audit, post 3 roles, outreach 50 candidates" + outreach template — hire

Compared to the legacy placeholder ("Research deeper into ${category} signal") this is a real product improvement, not a wrapper on a stub.

## Rigby's three PR reviews

Mid-build design reviews on every PR caught real issues before merge. Saved in conversation `pa-d19c1674b936`.

**PR #2174 (u-d-b backend) — 5 questions, 1 merge-blocker:**
- Q1 storage shape: confirmed typed-rows-not-blob.
- Q2 LLM location: confirmed two-phase async, never block snapshot.
- Q3 action shape: confirmed mirror signal-studio fields + add audit.
- Q4 frontend: deferred to PR 3.
- Q5 acceptance: ≥3 outreach cards, graceful failure.
- **Blocker:** Meta.ordering included `entry_type` which interleaved action_card BEFORE cluster_pick alphabetically. Fixed in `0eb3f1d9`.
- **Nice-to-have:** action_status='needs_regen' for fallback rows (vs hidden under generated_by). Shipped in same fix-up.

**PR #18 (signal-studio ingest) — 5 questions, 0 blockers:**
- Confirmed all five design calls (shared table, skip-on-missing-cluster, status passthrough, partial unique index, trust UUID immutability).
- **Nice-to-have:** include `snapshot_id` in missing-cluster skip log for replay traceability. Shipped in `5d5bee5`.
- **Merge sequencing:** option C — co-merge PR1 + PR2, then PR 3 separately.

**PR #19 (signal-studio frontend) — 7 questions, 0 blockers:**
- Confirmed: action_type palette OK, amber border on needs_regen correct, outreach block styling OK, drill-in-only render OK, no regen button this PR.
- **Copy polish wins** (shipped in `d7c5e90`):
  - "Pre-generated Action Plan" → "Suggested Next Steps"
  - "Pre-generated" pill → "AI draft"
  - "Needs regen" pill → "Needs retry"
- Rationale: implementation terms leak internals; user-facing copy should describe state + what to do with it.

## Files touched (summary)

```
u-d-b (PR #2174):
  core/models_signal_intelligence.py             # +184 / -19   (CuratedSignalEntry typed-rows)
  core/migrations/0352_session_1140_typed_curated_entries.py   # +266 / -0   (new)
  core/migrations/0353_session_1140_action_status_needs_regen.py # +66 / -0   (new, post-review)
  core/services/curated_action_card_generator.py # +407 / -0    (new)
  core/services/signal_curator_service.py        # +105 / -0    (envelope + emit)
  core/tasks.py                                  # +13 / -0     (celery task)
  core/tasks_spiders.py                          # +88 / -0     (follow-on trigger)
  tests/services/test_curated_action_card_generator.py # +352 / -0  (new, 35 tests)

signal-studio (PR #18):
  backend/app/models.py                          # +30 / -3     (ActionCard schema)
  backend/app/signal_ingest.py                   # +192 / -1    (_apply_curated_actions + schema)
  backend/tests/test_curated_actions_ingest.py   # +275 / -0    (new, 11 tests)

signal-studio (PR #19):
  backend/app/main.py                            # +10 / -0     (is_curated_pregen)
  frontend/src/App.tsx                           # +109 / -17   (inline render + copy polish)
```

**Total:** ~2300 LOC across 11 files, 3 PRs, 7 commits-before-squash, 3 Rigby design-review passes.

## Test posture

- **57/57 new unit tests** across the three PRs (35 + 11 + 11). All pass.
- **122/122 regression** across pre-existing signal-adjacent suites (curator_phase2, fleet_signals_phase1, entity_clusterer, judge_stats_tool) — no breakage.
- **End-to-end live verification** in 4 separate smoke runs:
  1. u-d-b `generate_for_snapshot` synchronous: 10 picks → 10 paired action_cards
  2. u-d-b → signal-studio fleet event → mirror ingest: 10 rows pairing 1:1
  3. Re-emit idempotency: second fire produces 0 new rows (upsert by external_id)
  4. Headless Playwright screenshot of signal detail showing the new render
- **Live status mapping** verified end-to-end: real LLM cards land as `status='draft' + generated_by='gpt-5-mini'`, fallback cards as `status='needs_regen' + generated_by='fallback_placeholder'`. Zero invariant mismatch.

## Honest scope notes

- **List-card preview deferred.** Action cards only render in signal detail (drill-in). The Curated tab list itself doesn't yet show a 1-line action teaser. Rigby called this OK for first ship; can add later.
- **Regen scheduler deferred.** Fallback rows now have `status='needs_regen'` which a future scheduler could filter on. Not in this slice's scope — Rigby explicitly suggested deferring because regen has product/ops dependencies (rate limit, audit, which model, who triggered) that warrant a deliberate follow-on.
- **No copy button on outreach_draft.** Monospace + preserved line breaks are correct shape for templates with `[Name]` / `[Role]` placeholders, but a 1-click Copy button would tighten the loop. Future PR.
- **on-demand `/api/signals/{id}/generate-action` endpoint kept.** Q4 said "hide on curated, keep on non-curated" but the frontend never wired the endpoint anyway, so there was no button to hide. Endpoint stays available for future on-demand cases.
- **Inline render only fires when action_cards present on the cluster.** Pre-1140 curated snapshots that lacked action_cards (the LLM cards never existed for those) will render the legacy "Action Plan" header without the new chrome. As beat cycles produce new snapshots with action cards, the upgraded render takes over.
- **24-hour-after-merge measurement still pending.** Session 1139's acceptance test (v1 rejection rate < 30%?) is unrelated to this slice and remains the headline 1141 ask. Currently at sample size n=3 v1 cards judged — below Rigby's locked n≥20 read threshold.

## Carryovers into Session 1141

**Action-card slice follow-ups (new):**
- **Regen scheduler** for `needs_regen` rows. Now visible in UI; needs explicit design pass (rate limit, audit, retry budget, model selection). Status-field separation already in place from PR 1's review fix-up.
- **Copy button** on outreach_draft block (Rigby Q4 non-blocking).
- **Curated tab list-card inline action preview** — 1-line title teaser before drill-in. Separate UX scope.
- **Action-card rendering on legacy clusters** — pre-1140 snapshots show empty action_cards arrays. Either backfill via manual one-off OR let time-decay carry it (new snapshots inherit the upgraded render naturally).

**Unchanged from prior 1140 close:**
- Session 1139 acceptance read at n≥20 (still the headline 1141 ask).
- (Y) reject-mode flip in unified_pa_chat — gated on 3-day audit telemetry.
- Legacy SignalCluster bulk-archive — conditional on victory measurement.

## Companion handoffs

- [SESSION_1140_CLUSTER_METHOD_MIRROR_AND_JUDGE_STATS](SESSION_1140_CLUSTER_METHOD_MIRROR_AND_JUDGE_STATS.md) — Earlier-in-session work: mirror column + judge-stats endpoint + PA tool.
- [SESSION_1139_UPSTREAM_CLUSTERING_QUALITY](SESSION_1139_UPSTREAM_CLUSTERING_QUALITY.md) — Upstream entity-token clusterer that produces the v1 SignalClusters this slice's action cards are generated against.
- [SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION](SESSION_1138_F1_PAID_INTEREST_IMPLEMENTATION.md) — Sibling demand-gate slice for architectural reference.

---

*Session 1140 (A) closed. The Decision-13 → entity-token clusterer → mirror + judge-stats → action-cards arc that started in Session 1138 is now complete: spiders produce signals → entity-token clusterer creates v1 clusters → curator scores Top-10 → action-card generator drafts the next move per cluster → mirror persists → UI renders inline. Next session reads the acceptance number once samples accumulate.*
