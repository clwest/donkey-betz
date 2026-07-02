---
title: "S1501 Sports Odds Ingestion & Normalization — Child Audit (Category A / P1 under Group 1500)"
status: active (child audit — first child of Group 1500 Sports/DBAO/Intelligence arc; drafted 2026-07-01; Rigby Full SIGN cycle 1 SIGN-with-edits at Medium-High confidence → F1-F7 folds landed at commit-time → Rigby Full SIGN cycle 2 SIGN-clean at High confidence 2026-07-01 on fresh isolation pin `pa-a39069230ab64450`; D48 preemptive stability-probe gate arm 4 — clean probe + zero worker-instability across 4 substantive SIGN batches — D48 CODIFICATION-READY for playbook v3 per S1405+S1406+S1499+S1501 4-arc pattern)
authority: child-audit for Category A per parent §5 sequence + first sibling to apply the pre-brief mini-schema per D62 = (a) propagate upfront (Chris-ratified S1501 open 2026-07-01)
category: child_audit
session: 1501
date: 2026-07-01
domain_slug: sports
subdomain_category: A
research_group: 1500
parent_doc: docs/research/domains/sports/1500_sports_domain_scoping.md
authors: Claude Code (Chris directed via short command "Continue research group 1500: Category A")
supersedes: none
related:
  - docs/research/domains/sports/1500_sports_domain_scoping.md                       # parent scoping — arc-open + Phase 0 F.i/F.ii/F.iii second application UNCHANGED per D58 + candidate subdomain taxonomy A-F + D62 = (a) pre-brief mini-schema propagation ratification
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                        # §9 28 canonical questions + §11.2 20-section child template + §13 6-parallel-sweep + §14 evidence rules + §15 SIGN
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                               # OS bootstrap + child-audit contract §8
  - docs/research/OPEN_ARCS.md                                                       # arc manifest — Group 1500 In-progress
  - docs/research/platform_architecture_inventory.md §3.10                           # S1273 Sports Intelligence / Betting Pipeline LIGHT baseline
  - docs/research/platform/cross_domain_integration_audit.md §14 Finding #6          # S1274 sports_odds not a SignalCluster.pattern_type HIGH
  - docs/research/platform/cross_domain_integration_audit.md §12.3                   # S1274 v2 P1 island-vs-integrated posture decision point (framing owed to Cat F evidence plan)
  - docs/PLATFORM_INVENTORY.md                                                       # runtime inventory anchor (regenerable)
  - docs/PLATFORM_WHAT_IT_IS.md                                                      # narrative anchor
  - docs/topics/spider-network.md                                                    # existing topic doc — closest current-state Cat A narrative
  - docs/topics/celery-workers.md                                                    # existing topic doc — sports queue + task cadence
  - docs/narratives/SPORTS_MONETIZATION_ML.md                                        # existing narrative — TheOddsSpider + GamePredictor auto-create chain
scope: audit Category A ONLY — sports odds ingestion (5 spiders + 3 lightweight configs) + persistence (OddsSnapshot + GameLineHistory + SpiderData sports_odds rows) + Cat A Celery task surface + Cat A beat schedule + Cat A Discord bridge; boundary ends at persisted odds + line-movement history
non_goals:
  - Category B — prediction / analytics agents (sports_odds_analyst, game_predictor, sharp_action_detector, arbitrage_detector — S1502 owns)
  - Category C — wager tracking / outcome verification (PlacedWager, PlacedWagerLeg, BettingStats, BettingOutcomeVerifier — S1503 owns)
  - Category D — betting content pipeline (generate_daily_betting_brief, daily_betting_digest, SportsContentContextBuilder, Discord /odds — S1504 owns)
  - Category E — frontend sports surface (BettingPage 9 tabs, /betting route — S1505 owns)
  - Category F — cross-domain integration lens + posture decision framing + evidence plan (S1506 owns; consumes P1-P5)
  - actually deciding the S1274 §12.3 island-vs-integrated posture (Chris-gated, post-arc — see D59 refinement)
  - implementation proposals (this is research; PRs come later per playbook §14 "no implementation during research")
  - external companion project scope (`BILLING_MONETIZATION_SYSTEM.md` from ai-content-studio — S1400 anti-scope pattern inherited)
  - Odds API vendor selection (product decision, not architecture)
  - mobile / React Native betting-app scope
owner: claude (Chris ratified S1501 P1 open via "Continue research group 1500: Category A" short command 2026-07-01)
verifier_loop: Rigby Full SIGN cycle 1 SIGN-with-edits at Medium-High confidence 2026-07-01 on fresh isolation pin `pa-a39069230ab64450` (D48 4th arm — stability probe clean + zero substantive-turn instability across 4 batches; D48 CODIFICATION-READY for playbook v3 per S1405+S1406+S1499+S1501 4-arc pattern) → F1-F7 folds landed → Rigby Full SIGN cycle 2 SIGN-clean at High confidence 2026-07-01 (cycle 1 prediction accurate; do-not-regress notes for PR: keep §2.1 Cat A contract statement + keep posture-decision-pending framing throughout §9 Q15 + §17 + preserve enum-resolution HIGH severity in §15 debt #1 + §19 rank #2)
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/platform_architecture_inventory.md
  - docs/research/platform/cross_domain_integration_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/domains/sports/1500_sports_domain_scoping.md
---

# Session 1501 — Sports Odds Ingestion & Normalization Audit (Category A)

> **What this doc is.** The first child audit of Group 1500. It answers
> the 28 canonical questions from playbook §9 for **Category A only** —
> sports odds ingestion, normalization, and persistence — using six
> parallel Explore sub-agents (per §13) + Claude parent verifier-loop
> passes on load-bearing claims (per §14 "trust but verify"). Every
> surface inventoried carries the 4-item pre-brief mini-schema per D62 =
> (a) propagate upfront (Chris-ratified S1501 open 2026-07-01) so P6/F
> (Category F, S1506) inherits consistent evidence shape when it drafts
> the posture-decision evidence plan owed to xx99 (S1599).
>
> **What this doc is not.** A design proposal. A posture recommendation.
> An audit of the downstream consumers (agents, wagers, content, UI,
> cross-domain lens — those are P2-P6 scope per parent §5 sequence). An
> implementation plan. This is research.

---

## 1. Executive Summary

Category A — sports odds ingestion + normalization — is **WORKING
(fragile contract) at ingestion, PARTIAL at normalization** (Rigby SIGN
cycle 1 fold — see §13 for the wording rationale). Data flows
end-to-end in production (TheOddsSpider fetches from The Odds API
every 30 minutes, KalshiSpider from Kalshi prediction markets every
hour at :15, both write to `persistence.SpiderData`;
`_impl_snapshot_odds_for_line_movement` writes `OddsSnapshot` +
`GameLineHistory` rows for line-movement tracking). Consumers (Cat B
market agents) filter `data_type = 'sports_odds'` from `SpiderData`
and reconstruct odds schema in memory. The 9-tab BettingPage renders
both surfaces to users. Discord
`_impl_collect_sports_odds_intelligence` posts an intelligence digest
every 30 minutes to `CHANNEL_BOARDROOM`.

**Three load-bearing findings owed to xx99 posture-decision brief
via Cat F evidence plan** — top-ranked by Rigby SIGN cycle 1 Q7 as
enum-resolution + posture-decision + fixture-identity being the three
most consequential surfaces:

1. **[HIGH — riskiest operational finding per Rigby SIGN cycle 1 Q6]
   Silent choices-enum violation on `SpiderData` writes (drift, HIGH).**
   `SpiderData.data_type` at `persistence/models.py:693-712` declares 14
   valid choices; `'sports_odds'` is not one of them. Same drift on
   `source_platform` at `persistence/models.py:641-663` (writes
   `'theodds'` and `'kalshi'` — neither in the enum). Django CharField
   `choices=` validates only at Form/Admin layer, not at
   `Model.save()`, so writes silently persist. Cat B agents filter
   `data_type == 'sports_odds'` (see e.g., `sports_odds_analyst`,
   `game_predictor`, `arbitrage_detector` — Cat B P2 owns full agent
   inventory), which means the entire Cat A → Cat B contract is
   established via a schema-invalid string that neither model layer
   nor form layer validates. This is the code-level materialization of
   the S1274 §14 Finding #6 "sports_odds not a valid data_type" gap —
   and it extends beyond `SignalCluster.pattern_type` (the S1274
   framing) to the `SpiderData.data_type` and
   `SpiderData.source_platform` fields as well.

2. **Two disjoint persistence stores for the same domain (dual-store
   with no reconciler — posture-decision surface, LOW-MED per Rigby
   SIGN cycle 1 Q4 fold).** `SpiderData` (persistence app,
   `sports_odds` rows) and `OddsSnapshot`/`GameLineHistory` (core app,
   `core/models_odds_history.py`) both persist odds data but neither
   is FK-linked to the other and there is no reconciliation service.
   `SpiderData` is written by `_impl_collect_sports_odds` (Session 558,
   for semantic search + agent consumption). `OddsSnapshot` is written
   by `_impl_snapshot_odds_for_line_movement` (Session 561, for
   line-movement charts). Both call `TheOddsSpider().fetch_data(...)`
   independently — two distinct API calls, two distinct persistence
   paths, no shared idempotency layer. This is not "duplicate models"
   in the classic sense (they serve different purposes — semantic
   search vs time-series line-movement); Rigby SIGN cycle 1 Q4
   confirmed this may be **intentional read-optimized-vs-semantic
   separation** rather than a missing reconciler defect. Whether a
   canonicalizer is required is a Cat F posture decision, not a Cat A
   prescription. Cat A observation: "SpiderData = semantic/log surface;
   OddsSnapshot = UI read-model; no canonicalizer exists today" — no
   further judgment about whether one should exist.

3. **No unified normalization service exists (parked P1 issue confirmed
   NEGATIVE — architecture-decision-pending, not automatic HIGH, per
   Rigby SIGN cycle 1 Q5 fold).** Parent scoping §6 P1-parked issue #1
   asked "does one exist as a canonical surface consuming all 5
   spiders, or does each spider write its own path?". Sub-agent 2
   grepped `core/services/` for `class.*OddsNormaliz`,
   `def.*normaliz.*odds`, and cross-referenced
   `OddsSnapshot`/`GameLineHistory` service consumers — **zero
   matches**. Each spider persists via its own task
   (`_impl_collect_sports_odds` for TheOdds,
   `_impl_collect_kalshi_prediction_markets` for Kalshi — direct writes
   to `SpiderData` via `update_or_create()`), and
   `_impl_snapshot_odds_for_line_movement` writes directly to
   `OddsSnapshot`/`GameLineHistory` bypassing `SpiderData` entirely.
   There is no canonical `SportsOddsNormalizationService`. Rigby SIGN
   cycle 1 Q5 fold: whether this counts as HIGH debt depends on
   whether normalization is part of Cat A's contract to Cat B. It is
   not (see §2.1 Cat A contract statement below). Reclassified as
   architecture-decision-pending; Cat F posture decision determines
   direction.

**Other observations:** `snapshot_odds_for_line_movement` (`core/tasks.py:6114` →
`core/tasks_financial.py:2140`) docstring claims "Runs every 20 minutes"
but has **no beat entry** — verified absent from `core/celery.py:37-797`.
This task is on-demand only despite the docstring promise; line-movement
tracking may be latent or manually triggered. Discord `send_betting_digest`
posts to `CHANNEL_BOARDROOM` (`1448819855557136595`) but `_impl_collect_
sports_odds_intelligence` docstring says "post to Discord #market-
intelligence" — real docstring drift. `OddsSnapshot` has no unique
constraint (intentionally append-only for line-movement charts, but no
retention job — unbounded growth risk). Fixture / entity identity resolution
across TheOdds `event_id`, Kalshi `ticker`, and internal
`GameLineHistory.game_id` is **UNKNOWN** at code level — a Rigby SIGN
cycle 1 Q8 fold added this as a discoverable P1 scope; the answer
appears to be: TheOdds `event_id` flows through to `OddsSnapshot.game_id`
via direct copy, but Kalshi and other spiders have no cross-referenced
identity in the persisted surface (Kalshi writes its own `ticker`-keyed
rows to `SpiderData` with `data_type='prediction_market'` — a different
type from `'sports_odds'`).

**What xx99 owes (through Cat F evidence plan):** Cat A is close to
Chris's "sports as an island" mental frame at the persistence layer:
5 spiders + 3 lightweight configs + 2 core-app models + 1 shared
persistence app model + 3 Celery tasks (1 beat) + 1 Discord bridge, with
zero body-system integration and zero SignalCluster integration.
Integration posture would require the following non-trivial refactors:
add `sports_odds` to `SpiderData.data_type` enum + `SignalCluster.
pattern_type` enum + add a canonical normalization service + add
`OddsSnapshot` ↔ `SpiderData` sync + resolve fixture-identity across
spiders. Island posture would require: retention/TTL job + explicit
schema separation into a DBAO app or PostgreSQL `dbao` schema + explicit
API contract for what "island" means for the Cat F consumers (agents,
frontend, wagers) that still cross the boundary. Neither posture is
zero-cost. Cat A evidence lands cleanly on both sides of the F decision.

---

## 2. Domain Purpose

**Q1 — What is this domain for?** Category A is the ingestion +
persistence tier for sports betting odds data: it acquires raw odds
snapshots from external vendors (The Odds API, Kalshi, RSS/PRAW
sources) and lands them in Django models where Category B analytics
agents and Category E frontend consumers can read them.

**Q2 — What problem does it solve?** Sports betting content pipelines
(Cat D), user-facing wager tracking (Cat C), and downstream frontend
displays (Cat E) all depend on fresh odds. The runtime problem: The
Odds API has a rate-limited paid tier (20,000 requests/month) — we
can't call it from a request path. Ingestion has to be a bounded
background job that keeps a local snapshot fresh enough to serve UI
and predictions without exceeding quota. The design problem: the odds
surface has to work as both (a) semantic-search-embeddable content
(for RAG / agent context) and (b) time-series data (for line-movement
charts). Cat A's current architecture split those two use cases into
two persistence paths (`SpiderData` for semantic; `OddsSnapshot` for
time-series) driven by the same underlying spider.

### 2.1 Cat A contract statement (Rigby SIGN cycle 1 Q9 fold)

To prevent this doc from being read as promising Cat B / Cat D / Cat F
behavior it does not own, Cat A's runtime contract is stated
explicitly here.

**Cat A guarantees today:**

- 5 ingestion spiders + 3 lightweight configs land on `main` and
  execute in production (verified §5).
- Beat schedule fires `collect-sports-odds-intelligence` @ 30-min and
  `collect-kalshi-prediction-markets` @ hourly-at-15 (verified
  `core/celery.py:787-796`).
- Odds and prediction-market rows persist to `SpiderData` (via
  `_impl_collect_sports_odds` and `_impl_collect_kalshi_
  prediction_markets`) with idempotency at `(spider_name, source_url)`.
- Line-movement snapshots persist to `OddsSnapshot` + `GameLineHistory`
  (via `_impl_snapshot_odds_for_line_movement`) — but the beat entry
  for automatic firing is absent (see §14.3); this is a Cat A
  known-drift item, not a contract guarantee.
- The Discord `#boardroom` digest fires with the same 30-min cadence
  (verified §7.4).

**Cat A explicitly does NOT guarantee:**

- Normalization of odds across the 5 spiders into a canonical odds
  surface. Cat B agents that filter on `data_type == 'sports_odds'`
  operate on a string that isn't in the `SpiderData.data_type` enum
  and there is no canonicalizer between spiders. Whether Cat A should
  own such a normalizer is a Cat F posture decision.
- Emission of `SignalCluster` rows or Initiative auto-creation from
  sports data. That is a posture-decision bridge (S1274 §12.3 two
  legitimate postures), not a Cat A contract.
- Cross-spider fixture / entity identity reconciliation. TheOdds
  `event_id` and Kalshi `ticker` live in different namespaces on
  `SpiderData.structured_data`; no canonical `Game` model reconciles.
- Retention / TTL / cleanup of `OddsSnapshot` or `GameLineHistory`.
  None exists (§8.1).
- Feedback loops from wager outcomes (`BettingOutcomeVerifier`) into
  odds signal scoring. That is Cat C surface.

Consumers who need any of the "does NOT guarantee" behaviors depend on
Cat F posture decision + follow-on design work. Cat A does not
foreclose any posture; it just doesn't ship the bridge.

---

## 3. Canonical Entry Points

**Q3 — What are the canonical entry points?**

### 3.1 Celery tasks (in-scope for Cat A)

| Task name | Trigger | Impl | Queue | Cadence | Beat |
|---|---|---|---|---|---|
| `collect_sports_odds` | on-demand | `core/tasks.py:6094` → `core/tasks_financial.py:1659` `_impl_collect_sports_odds` | default (implicit fallback per `core/settings.py:1171-1250` — no explicit route) | on-demand | none |
| `collect_sports_odds_intelligence` | beat + on-demand | `core/tasks.py:6098` → `core/tasks_financial.py:1815` `_impl_collect_sports_odds_intelligence` | `long_running` (per beat `options.queue` at `core/celery.py:790`) | 30 min | `core/celery.py:787-791` `collect-sports-odds-intelligence` @ `crontab(minute='*/30')` expires 1800s |
| `collect_kalshi_prediction_markets` | beat + on-demand | `core/tasks.py:N/A` (verify — Kalshi task decorator lives elsewhere or per `core/celery.py:792-796` name mapping) → `core/tasks_financial.py:1464` `_impl_collect_kalshi_prediction_markets` | `long_running` (per beat `options.queue` at `core/celery.py:795`) | hourly at :15 | `core/celery.py:792-796` `collect-kalshi-prediction-markets` @ `crontab(minute=15)` expires 3600s |
| `snapshot_odds_for_line_movement` | on-demand | `core/tasks.py:6114` → `core/tasks_financial.py:2140` `_impl_snapshot_odds_for_line_movement` | `long_running` (task decoration `@shared_task(ignore_result=True)` — verify routing) | **on-demand only — NOT beat-scheduled** | none (docstring claims "every 20 minutes"; verified absent from `core/celery.py`) |

**Load-bearing observations on §3.1:**
- **snapshot_odds_for_line_movement is dormant vs docstring** (drift finding — see §14). Line-movement tracking is latent unless another surface triggers it (no such trigger found).
- Kalshi is Cat A per parent §3.A ("prediction markets"). Its beat entry sits alongside sports-odds intelligence and runs on offset (`:15` vs `*/30`) — this offset is intentional per code comment ("every hour at :15 — offset from sports odds"). Kalshi persistence writes `data_type='prediction_market'` (not `'sports_odds'`) — a shape observation Cat F consumes.

### 3.2 Management commands

**Q8 — What are the major management commands?** **NONE.** Sub-agent 3
grepped `core/management/commands/` for `collect_odds`, `backfill_odds`,
`test_odds_spider` — zero matches. Only reference is a comment in
`core/management/commands/add_critical_celery_tasks.py:1` naming
`collect-sports-odds-intelligence` and `collect-kalshi-prediction-markets`
as materialize-targets when django-celery-beat DB rows need repair.
Ingestion is exclusively Celery-driven with no CLI hooks.

### 3.3 REST + WebSocket entry points

**REST (for reading persisted odds — Cat E scope):** `GET /api/v1/sports/live-odds/`,
`GET /api/v1/sports/live-odds-scores/`, `GET /api/sports-odds/`,
`GET /api/v1/odds/convert-odds/`, `GET /api/v1/odds/arbitrage/` (all
consumer-side, deferred to P5 Cat E audit).

**REST (for triggering / configuring ingestion — Cat A scope):**
**NONE.** Sub-agent 3 grep proof:
`grep -r "collect_sports_odds|snapshot_odds|odds.*trigger" core/views*.py core/urls*.py`
→ 0 matches. Ingestion cannot be triggered via REST — only via Celery
beat, direct task dispatch, or Rigby PA tools (see §3.4 — also absent).

**WebSocket for Cat A:** `SportsUpdatesConsumer` at
`core/consumers_sports.py:15` handles `handle_force_odds_update`
messages that call `update_game_odds(game_id)` — these are read-side
DB queries pushed to subscribed UI clients, not ingestion triggers.
`/ws/dbao/` is referenced in `tests/one-off/test_websockets.py:51` as a
realtime metrics namespace but NOT surfaced by any consumer in
`core/consumers*.py` or route in `core/routing.py` on `main` HEAD — Cat
F should verify whether `/ws/dbao/` exists in a deployed config or is a
test-only reference.

### 3.4 PA tools

**NONE for Cat A ingestion.** Sub-agent 3 grepped
`core/services/pa_tool_schemas.py` and `core/services/tool_dispatcher.py`
for odds-collection triggers. Only match: an `"odds"` field inside a
`sports_record_wager` schema — Cat C scope (wager outcome recording),
not Cat A. **Rigby has no way to trigger sports odds collection.** This
is an explicit surface absence to name in the audit — not an
oversight, and not a debt item unless Cat F posture-decision brief
determines Rigby should have it.

### 3.5 Discord `/odds` command

`/odds` slash command at `core/services/discord_bot.py:1108` is a Cat D
output surface (reads persisted odds for user display), out of scope
here. But the Cat A **outbound Discord** post at
`_impl_collect_sports_odds_intelligence:1815` → `send_betting_digest` →
`CHANNEL_BOARDROOM` is Cat A's own external surface (see §6.5).

---

## 4. Major Models

**Q4 — What are the major models?**

### 4.1 `OddsSnapshot` — `core/models_odds_history.py:15`

Point-in-time odds capture. Append-only design (no unique constraint).

| Field | Type | Constraint / Index |
|---|---|---|
| `id` | BigAutoField | PK auto |
| `game_id` | CharField(100) | `db_index=True` — The Odds API game ID (copied from spider's `event_id`) |
| `sport_key` | CharField(50) | `db_index=True` |
| `home_team` | CharField(100) | — |
| `away_team` | CharField(100) | — |
| `commence_time` | DateTimeField | — |
| `bookmaker` | CharField(50) | `db_index=True` |
| `bookmaker_title` | CharField(100) | `blank=True` |
| `market` | CharField(20, choices=`h2h`/`spreads`/`totals`) | `db_index=True` |
| `outcome_name` | CharField(100) | — |
| `price` | IntegerField | American odds format |
| `point` | DecimalField(5,1) | `null=True, blank=True` — spread/total line |
| `captured_at` | DateTimeField | `default=timezone.now, db_index=True` |

**Meta.ordering:** `['-captured_at']`
**Meta.indexes:**
- `Index(fields=['game_id', 'bookmaker', 'market', 'outcome_name'])` — line-movement reconstruction path
- `Index(fields=['sport_key', 'captured_at'])`
- `Index(fields=['game_id', 'captured_at'])`

**Properties:** `decimal_odds` (computed from American price),
`implied_probability` (computed).

**No `unique_together`. No FK to `GameLineHistory`. No FK anywhere.**
Deliberate: line-movement charts need every snapshot; dedup at write is
skipped.

### 4.2 `GameLineHistory` — `core/models_odds_history.py:82`

Denormalized aggregate per game.

| Field | Type | Constraint |
|---|---|---|
| `game_id` | CharField(100) | **`unique=True, db_index=True`** |
| `sport_key` | CharField(50) | `db_index=True` |
| `home_team, away_team, commence_time` | — | — |
| `open_spread_home, open_spread_price, open_total, open_ml_home, open_ml_away` | Decimal / Integer | nullable — first snapshot values |
| `current_spread_home, current_spread_price, current_total, current_ml_home, current_ml_away` | Decimal / Integer | nullable — latest snapshot values |
| `spread_movement, total_movement` | Decimal(5,1) | `default=0` — delta open→current |
| `snapshot_count` | PositiveIntegerField | `default=0` |
| `first_snapshot_at, last_snapshot_at` | DateTimeField | nullable |
| `created_at` | DateTimeField | `auto_now_add=True` |
| `updated_at` | DateTimeField | `auto_now=True` |

**Meta.ordering:** `['-commence_time']`
**Meta.indexes:** none declared beyond field-level `db_index=True`.

**Property:** `has_significant_movement` (bool — spread ≥ 0.5 or total ≥ 1.0).

**Write pattern:** `get_or_create(game_id=..., defaults=...)` at
`core/tasks_financial.py:2256`. Only writer visible.

### 4.3 `SpiderData` (sports_odds rows) — `persistence/models.py:611`

Multi-domain persistent store. Sports odds are a sub-slice via
`data_type='sports_odds'`.

- `spider_name` — `'theodds'` in Cat A writes
- `spider_execution_id` — nullable UUID
- `source_url` — vendor URL (`https://the-odds-api.com/sports/{sport_key}/{event_id}`)
- `source_platform` — declared choices at `persistence/models.py:641-663`; **`'theodds'` is NOT in the enum**; writes at `core/tasks_financial.py:1770` bypass form validation (Django only validates `choices=` in Forms/Admin, not at `Model.save()`)
- `title` / `content` / `structured_data` / `raw_html`
- `data_type` — declared choices at `persistence/models.py:693-712`; **`'sports_odds'` is NOT in the enum** (14 valid: `opportunity, job_posting, market_data, competitor_info, trend_data, user_feedback, product_info, pricing_data, content_idea, collaboration, news, research, tool_discovery, learning_resource`); same silent-drift pattern
- `category, tags, relevance_score, opportunity_score, quality_score, urgency_score, is_processed, ...`

`structured_data` JSONField holds a `metadata` sub-dict with the full
odds shape (`event_id, sport_key, home_team, away_team, home_odds,
away_odds, home_implied_prob, home_spread, total_line, over_odds,
under_odds, favorite, favorite_probability, bookmaker_count,
best_bookmaker, is_live, tags`) — see `core/tasks_financial.py:1739-1762`.

**Write mechanism:**
`SpiderData.objects.update_or_create(spider_name='theodds',
source_url=..., defaults={...})` at `core/tasks_financial.py:1766-1782`.
Idempotent per (spider_name, source_url) pair.

### 4.4 `SpiderData` (prediction_market rows) — same model, `data_type='prediction_market'`

KalshiSpider writes `data_type='prediction_market'` (per Sub-agent 4
verification of `ai_core/spiders/specialized/kalshi_spider.py:357`),
which is **also not in the enum** at `persistence/models.py:695-711`.
Same silent-drift pattern. Cat A observation only — Cat F evidence plan
consumes it.

### 4.5 `SpiderItemHash` — `core/models_unified_system.py:3845`

Cross-spider dedup surface. `unique_together=[['spider_name',
'content_hash']]`. **NOT currently referenced by Cat A ingestion.**
TheOddsSpider does not compute or query `SpiderItemHash` on its write
path (grep across the 5 spider files + `lightweight_spider_system.py`
returned zero). Idempotency for Cat A ingestion is achieved at
`SpiderData.update_or_create()` layer, not at `SpiderItemHash`. Whether
non-Cat-A spiders use `SpiderItemHash` is deferred to a Cat B / spider
framework audit if / when Chris opens one.

### 4.6 4-item pre-brief mini-schema per model (D62 fold)

| Model | (a) sports-only vs shared | (b) DBAO schema vs public schema | (c) integration posture (refactor vs extend) | (d) island posture (additional isolation) |
|---|---|---|---|---|
| `OddsSnapshot` | sports-only (all fields sports-specific) | **public schema, core app.** `Meta` declares no `db_table` override; no DATABASE_ROUTERS visible in `core/settings.py`. Writes to `default` database. | **extend** — no refactor needed to feed a SignalCluster / Initiative surface; a sync task from `OddsSnapshot` → downstream signals could be added without touching model schema. | **strong isolation already** — no FK to any non-Cat-A model. If posture chooses full island, adding retention job + explicit `dbao` schema move would complete isolation. |
| `GameLineHistory` | sports-only (denormalized aggregate) | **public schema, core app.** Same routing story as `OddsSnapshot`. | **extend** — no refactor needed. Could add FK to Cat C `PlacedWager` for outcome joins under integration posture (but Cat C would drive that, not Cat A). | **strong isolation already** — no FK. Denormalized-aggregate design is compatible with island shape. |
| `SpiderData` (sports_odds rows) | **shared** — SpiderData is a multi-domain container; sports_odds is one of many `data_type` slices (14 valid + 2 undeclared including `sports_odds` and `prediction_market`) | **public schema, persistence app.** Writes to `default` DB per `persistence` app config. | **refactor + extend** — silent choices-enum violation requires either (a) adding `'sports_odds'` + `'prediction_market'` to `SpiderData.data_type` choices (extend) OR (b) moving sports_odds writes off `SpiderData` into a dedicated model (refactor). Both are Cat F posture choices, not Cat A prescription. | **cannot fully isolate without breaking Cat B agents** who filter `SpiderData.data_type == 'sports_odds'` (see §9). Island posture would need to also design an agent-consumption bridge. |
| `SpiderData` (prediction_market rows — Kalshi) | **shared** — same container | **public schema, persistence app.** Same routing. | Same as sports_odds row — extend enum OR refactor to dedicated model. | Same isolation caveat — Cat B agents already read this shape. |
| `SpiderItemHash` | shared (cross-spider dedup) | **public schema, core app.** | **N/A for Cat A on `main`** — not referenced by Cat A. Sibling audits inherit the question. | N/A — surface not currently in Cat A's boundary. |

---

## 5. Major Services

**Q5 — What are the major services?**

### 5.1 Spider layer

| Spider | file:line | class | vendor / source | writes | credentials |
|---|---|---|---|---|---|
| `TheOddsSpider` | `ai_core/spiders/specialized/theodds_spider.py:33` | `TheOddsSpider` | The Odds API (40+ bookmakers) | dict with `data_type='sports_odds'` returned from `fetch_data()` — persistence happens in task layer (`_impl_collect_sports_odds` / `_impl_snapshot_odds_for_line_movement`) | `THE_ODDS_API_KEY` env var — circuit breaker on 401 (`_auth_failed` flag per Sub-agent 4 reading) |
| `KalshiSpider` | `ai_core/spiders/specialized/kalshi_spider.py:28` | `KalshiSpider` | Kalshi Prediction Markets (public API — no auth) | dict with `data_type='prediction_market'` — persistence via `_impl_collect_kalshi_prediction_markets` | none required |
| `CombatSportsSpider` | `ai_core/spiders/specialized/combat_sports_spider.py:30` | `CombatSportsSpider` | Reddit (PRAW) + UFC.com + Sherdog + Tapology | dict with `data_type='combat_sports_intelligence'` — cross-cutting to Cat A vs Cat B: this spider produces **intelligence content**, not odds proper. Sub-agent 4 verified no `'sports_odds'` write path from this spider. Belongs on the boundary — Cat A collects it under "sports data ingestion" but downstream consumer is more Cat D content than Cat B analytics. See §16 boundary observation. | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` |
| `HorseRacingSpider` | `ai_core/spiders/specialized/horse_racing_spider.py:18` | `HorseRacingSpider` | BloodHorse, HorseRacingNation, PaulickReport, TDN RSS feeds + Reddit | dict with `data_type='horse_racing'` — no `'sports_odds'` write. Similar boundary observation to Combat spider. | none (RSS + PRAW) |
| `SportsDataSpider` | `ai_core/spiders/sports_data_spider.py:18` | `SportsDataSpider` | ESPN API + The Odds API (fallback) | Sub-agent 4 finding: **incomplete persistence layer** — `fetch_and_store_data()` at line 317 has async logic but the DB write block at lines 330-334 is a placeholder (`logger.info` only). Operational status UNKNOWN. | `ODDS_API_KEY` optional (falls back to sample data if absent) |

Plus 3× `SportsOddsSpider` config rows at
`ai_core/spiders/lightweight_spider_system.py:330-332`. Sub-agent 4
resolved these to a lightweight orchestrator that generates **mock**
NFL/NBA/arbitrage data on a 60-second parallel loop, publishing to
Redis stream `spider:data:stream`. **Not production data path.** Cat A
observation only — Cat F evidence plan should consume that the "3
configs" from parent §2.5 evidence table are mock/orchestrator, not
production. Sub-agent 4 verified no direct persistence to `SpiderData`
or `OddsSnapshot` from these 3 configs.

### 5.2 Normalization / coordination layer

**Sub-agent 2 grep result — the load-bearing negative:**

```
$ grep -r "def.*normaliz.*odds|class.*OddsNormaliz|class.*Coordinator.*Odds" core/services/ --include="*.py"
(no output)

$ grep -r "OddsSnapshot|GameLineHistory" core/services/ --include="*.py"
(no output)
```

**No unified normalization service.** Each spider's output is persisted
by its own task, which handles field mapping inline. Parent scoping §6
P1-parked issue #1 is answered NEGATIVE at code level.

`SportsBettingCoordinator` (`core/services/sports_betting_coordinator.py:21`)
exists but is a Cat B agent orchestrator (fires 4 market agents +
generates unified brief) — it does not touch ingestion. Deferred to
P2 audit.

### 5.3 Dependency chain + god-service check

- Cat A services import only external libs (`requests, aiohttp,
  feedparser, praw, redis`) and internal spider bases (`ai_core.spiders.
  base_spider` etc.). No cross-domain imports out of Cat A.
- No Cat A service exceeds 3000 lines. Largest: `TheOddsSpider` at 895
  lines (per Sub-agent 2 line count). `lightweight_spider_system.py`
  (orchestrator + 3 configs) at 485 lines. Both well under threshold.

### 5.4 4-item pre-brief mini-schema per service (D62 fold)

| Service | (a) sports-only vs shared | (b) DBAO vs public | (c) integration posture | (d) island posture |
|---|---|---|---|---|
| `TheOddsSpider` | sports-only (40+ sports leagues) | writes to public `SpiderData` + `OddsSnapshot`/`GameLineHistory` via task layer — no schema choice at spider level | extend — spider is a stateless HTTP client; contract change lives above | strong isolation already at spider layer; no additional isolation needed |
| `KalshiSpider` | **sports-subset** — prediction markets include sports contracts but also non-sports (elections, tech, weather, economics). Kalshi's own category enum includes `'sports'` as one of 8-10 categories (per `kalshi_spider.py:36`) | writes public `SpiderData` | extend — could add sports-only filter at task layer if island posture wants sports-only in this path | Kalshi's non-sports rows are already in-scope for Cat A ingestion under D60 anti-scope reading (parent §7 restricts to sports-scope only). Explicit island posture would need to route sports vs non-sports Kalshi rows to different persistence surfaces. |
| `CombatSportsSpider` | sports-only (UFC/MMA/Boxing) | public `SpiderData` `data_type='combat_sports_intelligence'` — **not `'sports_odds'`** | extend — spider inherits `BaseIntelligenceSpider`; adding sports-specific keywords is add-only | isolated at spider layer already; PRAW auth already encapsulated |
| `HorseRacingSpider` | sports-only (horse racing) | public `SpiderData` `data_type='horse_racing'` | extend — RSS parser inherits base framework; add-only changes | isolated (RSS feeds are public) |
| `SportsDataSpider` | sports-only | **UNKNOWN persistence status** — placeholder DB code (Sub-agent 4). If operational, writes via Django ORM at `fetch_and_store_data()`. | **refactor OR deprecate** — either complete the persistence layer OR remove and route ingestion via TheOddsSpider path. Current state (dormant / half-shipped) is a debt item — see §15. | N/A if deprecated |
| `SportsOddsSpider ×3 configs` (mock) | sports-only (mock NFL/NBA/arbitrage) | writes to Redis (`spider:data:stream`) — **transient, TTL 24h.** Not persistent DB. | **refactor OR deprecate** — currently mock-only 60-second parallel loop. Confirm intent (test-only / production-fallback / prototype). | high isolation needed if kept — mock rows must not mix with real odds in downstream consumers |
| `SportsBettingCoordinator` | (Cat B — deferred to P2) | — | — | — |

---

## 6. Major APIs and Interfaces

**Q6 — What are the major APIs?**

### 6.1 REST — 0 ingestion-control endpoints

See §3.3 — grep-verified absence. All `/api/*` sports and odds endpoints
are read-side and deferred to Cat E (P5).

### 6.2 WebSocket — 0 for Cat A

See §3.3 — `SportsUpdatesConsumer` is read-side. `/ws/dbao/` is a
test-only reference on `main` HEAD.

### 6.3 PA tools — 0 for Cat A ingestion

See §3.4.

### 6.4 Discord bot commands — 0 inbound for Cat A

`/odds` and `/bankroll` are Cat D and Cat C output surfaces. Cat A has
no inbound Discord command that triggers ingestion.

### 6.5 Discord `#boardroom` outbound bridge — Cat A's sole external surface

`_impl_collect_sports_odds_intelligence` at
`core/tasks_financial.py:1815-1902`:

1. Fires from beat `collect-sports-odds-intelligence` (`core/celery.py:788`) every 30 min.
2. Calls `TheOddsSpider().get_upcoming_events(hours=24)` (per Sub-agent 3).
3. Groups events by sport, identifies "toss-ups" (implied probability 45-55%), builds a Discord embed with sport blocks + top 3 games + toss-up section.
4. Posts via `DiscordNotificationService().send_betting_digest()` at line 1880.
5. `send_betting_digest` (per `core/services/discord_notifications.py:499` / around) routes to `CHANNEL_BOARDROOM = "1448819855557136595"` (`discord_notifications.py:40`).

**Docstring vs code drift:** the task docstring at
`tasks_financial.py:1817` claims "post to Discord #market-intelligence".
The channel MAPPING at `discord_notifications.py:1091` maps
`'market-intelligence'` → `self.CHANNEL_MARKET_ALERTS` = "1448867150948335777"
(line 44). But `send_betting_digest` hardcodes `CHANNEL_BOARDROOM`, not
`CHANNEL_MARKET_ALERTS`. **Real drift** — see §14.

### 6.6 4-item pre-brief mini-schema per external surface (D62 fold)

| Surface | (a) sports-only vs shared | (b) DBAO vs public | (c) integration posture | (d) island posture |
|---|---|---|---|---|
| `collect_sports_odds` task | sports-only | writes public `SpiderData` | extend | strong isolation already |
| `collect_sports_odds_intelligence` task + beat | sports-only | writes to Discord (public channel `#boardroom`) — no DB write | extend | partial: could add circuit breaker for Discord API failure |
| `snapshot_odds_for_line_movement` task | sports-only | writes public `OddsSnapshot` + `GameLineHistory` (core app) | **extend + choose schedule** — need beat entry OR explicit trigger contract | strong isolation |
| `collect_kalshi_prediction_markets` task + beat | sports-subset (Kalshi has non-sports categories) | writes public `SpiderData` with `data_type='prediction_market'` | extend (add sports filter for island) OR refactor (dedicated `PredictionMarket` model) | needs category-scope decision |
| Discord `#boardroom` post | sports-only content | public channel | extend | partial: add delivery-status tracking |

---

## 7. Runtime Flows

**Q9 — What are the major runtime flows?**

### 7.1 Flow A — TheOddsSpider → SpiderData (semantic-search + agent-consumption path)

```
[Beat fires nothing directly for `_impl_collect_sports_odds` — but
 `collect_sports_odds_intelligence` fires every 30 min and calls into
 a related surface. `_impl_collect_sports_odds` itself is on-demand.]
        ↓
[core/tasks_financial.py:1659 _impl_collect_sports_odds]
        ↓
[TheOddsSpider() → spider.fetch_data(max_results=150)]
    ├─ TheOddsSpider._get_active_sports() → HTTP GET /sports
    ├─ for each active sport: HTTP GET /sports/{sport}/odds
    │   with markets=['h2h', 'spreads', 'totals']
    └─ returns List[Dict] with data_type='sports_odds' | 'futures_odds' | 'api_status' | 'fetch_failure'
        ↓
[Filter: e.get('data_type') == 'sports_odds' → sports_events list]
        ↓
[For each event:
    · Build content = "Sports Event: ...\nSport: ...\nMoneyline: ..."
    · Build metadata = {event_id, sport_key, home_team, ..., is_live, tags}
    · SpiderData.objects.update_or_create(
          spider_name='theodds',
          source_url=f"https://the-odds-api.com/sports/{sport_key}/{event_id}",
          defaults={
              source_platform='theodds',      ← NOT in choices enum (drift)
              data_type='sports_odds',        ← NOT in choices enum (drift)
              title=..., content=...,
              structured_data={metadata, **event},
              relevance_score=0.85,
              quality_score=0.85,
          }
      )
    · created ? new_records++ : updated_records++
]
        ↓
[Log API usage from spider.get_api_usage() — requests_used / monthly_limit]
        ↓
[Return {success: True, events_fetched, new_records, updated_records, sports: {...}, api_usage}]
```

### 7.2 Flow B — TheOddsSpider → OddsSnapshot + GameLineHistory (time-series path)

```
[On-demand — no beat entry despite docstring claim (drift finding §14).]
        ↓
[core/tasks_financial.py:2140 _impl_snapshot_odds_for_line_movement]
        ↓
[TheOddsSpider() → spider.fetch_data(sports=['americanfootball_nfl',
                                              'basketball_nba',
                                              'icehockey_nhl',
                                              'baseball_mlb'],
                                     include_futures=False,
                                     max_results=100)]
        ↓
[Skip records where !game_id or data_type == 'api_status']
        ↓
[For each game with home_odds:
    OddsSnapshot.objects.create(
        game_id=..., sport_key=..., home_team=..., away_team=...,
        commence_time=..., bookmaker=best_bookmaker or 'consensus',
        market='h2h', outcome_name=home_team,
        price=int(home_odds)
    )   [line 2192]
]
[If away_odds: same shape for away_team] [line 2206]
[If home_spread: market='spreads', point=Decimal(home_spread)] [line 2223]
[If total_line: market='totals', outcome_name='Over',
                point=Decimal(total_line), price=over_odds] [line 2240]
        ↓
[GameLineHistory.get_or_create(game_id=..., defaults={sport_key,
                                                        home_team, away_team,
                                                        commence_time})]
        ↓
[If created: history.first_snapshot_at = now]
[Always: increment snapshot_count, update last_snapshot_at, save]
        ↓
[Return {success, total_snapshots, games_updated}]
```

### 7.3 Flow C — Kalshi → SpiderData (prediction markets path)

```
[Beat fires `collect-kalshi-prediction-markets` @ crontab(minute=15) — hourly.]
        ↓
[core/tasks_financial.py:1464 _impl_collect_kalshi_prediction_markets]
        ↓
[KalshiSpider() → spider.fetch_data(max_results=500,
                                     include_events=True,
                                     include_series=True)]
    ├─ _fetch_markets(limit=500) — HTTP GET /markets (paginated, cursor)
    ├─ _fetch_trending_markets(limit=125)
    ├─ _fetch_events(limit=100)
    └─ _fetch_series(limit=50)
        ↓
[For each market (per Sub-agent 4 reading of Kalshi task path):
    SpiderData.objects.update_or_create(
        spider_name='kalshi',
        source_url=f"https://kalshi.com/markets/{ticker}",
        defaults={
            source_platform='kalshi',      ← NOT in choices enum (same drift as theodds)
            data_type='prediction_market', ← NOT in choices enum (same drift)
            title=..., content=..., structured_data={metadata, **market},
            relevance_score=0.80, quality_score=0.85,
        }
    )
]
```

### 7.4 Flow D — Discord digest (Cat A's outbound observability surface)

```
[Beat fires `collect-sports-odds-intelligence` @ crontab(minute='*/30')]
        ↓
[core/tasks_financial.py:1815 _impl_collect_sports_odds_intelligence]
        ↓
[TheOddsSpider().get_upcoming_events(hours=24)]
        ↓
[Group by sport (top 3 events per sport); identify toss-ups (45-55% prob)]
        ↓
[Build Discord embed: title='🎰 Sports Betting Odds',
                     fields=[prediction_markets, sports_events, toss_ups],
                     footer='AI Studio Betting Intelligence | Session 558',
                     color=0x9B59B6]
        ↓
[DiscordNotificationService().send_betting_digest(embed)]
        ↓
[_send_message(self.CHANNEL_BOARDROOM = "1448819855557136595", "", embed=embed)]
        ↓
[Result: single Discord post per 30 min to #boardroom]
        ↓
[NOTE: docstring claims target is #market-intelligence — code actually routes to #boardroom. Drift — see §14.]
```

---

## 8. Data Ownership and Lifecycle

**Q16 — What data does it own?**

Cat A **exclusively owns** `OddsSnapshot` and `GameLineHistory` (no
external writer). Cat A **shares** `SpiderData` with all other spiders
(Cat A writes `data_type='sports_odds'` and `'prediction_market'`
rows; other subsystems write `'opportunity'`, `'news'`, etc.).

**Q17 — What data does it consume?** External APIs (The Odds API,
Kalshi API, Reddit, RSS feeds). No internal cross-domain reads on the
write path.

**Q18 — What data does it produce?** For Cat B agents: `SpiderData`
sports_odds rows (filtered by `data_type` string). For Cat E frontend:
`OddsSnapshot` + `GameLineHistory` (line-movement dashboards). For
Discord #boardroom subscribers: text/embed digest every 30 min.

### 8.1 Retention

**None.** Sub-agent 1 grep verified: no TTL / cleanup / retention
task for `OddsSnapshot` or `GameLineHistory` in `core/tasks*.py`
or `core/celery.py`. `SpiderData` has an `expires_at` field but no
Celery job to prune expired rows.

At current cadence (30-min beat × ~150 sports events × ~2-4 markets
per event when the line-movement task runs), row accumulation on
`OddsSnapshot` is unbounded. If line-movement task were beat-scheduled
per its docstring ("every 20 minutes"), append-only rows would grow at
roughly 100k-500k rows/month — feasible but requires an eventual
retention policy.

### 8.2 Idempotency

- `SpiderData` writes are idempotent per `(spider_name, source_url)`
  via `update_or_create()`.
- `OddsSnapshot` writes are **NOT** idempotent — each call creates new
  rows (intentional for line-movement).
- `GameLineHistory` uses `get_or_create(game_id=...)` — idempotent per
  game.

### 8.3 Fixture / entity identity resolution (Rigby Q8 fold surface)

`OddsSnapshot.game_id` and `GameLineHistory.game_id` are both copied
verbatim from TheOdds spider's `event_id`. There is **no** internal
canonicalization to a shared `Game` or `SportsEvent` model. Kalshi
`ticker` is a distinct namespace stored on `SpiderData.source_url` and
`structured_data['metadata']['ticker']` — no cross-reference. Cat B
agents that consume both surfaces (e.g., if `arbitrage_detector` reads
sports_odds AND prediction_market) would need to reconcile identity at
agent-code level. Cat A does not solve this.

### 8.4 4-item mini-schema per data owned (D62 fold)

| Data | (a) sports-only vs shared | (b) DBAO vs public | (c) integration | (d) island |
|---|---|---|---|---|
| `OddsSnapshot` rows | sports-only | public core app schema | extend — add sync to SignalCluster | strong isolation already; add retention job for full island |
| `GameLineHistory` rows | sports-only | public core app schema | extend — could FK to Cat C wagers | strong isolation already |
| `SpiderData` sports_odds rows | shared container | public persistence app | refactor (extend enum) OR refactor (dedicated model) | breaks Cat B contract if fully isolated |
| `SpiderData` prediction_market rows (Kalshi) | shared container, sports-subset | public persistence app | same as above | same |
| Discord `#boardroom` embed | sports-only content | public channel | extend | partial (add delivery tracking) |

---

## 9. Integrations With Other Domains

**Q14 — What integrations does it have?**

| Direction | Peer domain | Surface | Strength |
|---|---|---|---|
| outbound (Cat A → Cat B) | market agents (sports_odds_analyst, game_predictor, arbitrage_detector, sharp_action_detector) | agents filter `SpiderData` rows by `data_type == 'sports_odds'` in memory (see e.g., Cat B P2 audit — deferred). | **WEAK** — string-typed filter on an off-enum value; no schema contract; no join to `OddsSnapshot` |
| outbound (Cat A → Cat E) | BettingPage 9 tabs | REST reads on `OddsSnapshot` + `GameLineHistory` (see §6.1) | **STRONG** — direct DB reads through consumer-side REST |
| outbound (Cat A → Cat D) | betting brief / digest | `SportsContentContextBuilder` reads live odds through TheOddsSpider re-invocation OR via `SpiderData` — Cat D audit will clarify | **UNKNOWN** — Cat D P4 owns this contract |
| outbound (Cat A → Discord) | `#boardroom` | Cat A's `send_betting_digest` — direct HTTP post | **STRONG** but with docstring drift on channel name |
| inbound (external → Cat A) | The Odds API, Kalshi, Reddit, RSS | HTTPS fetch | **STRONG** — production paths verified live |

**Q15 — What integrations are absent by posture-decision-pending vs
missing-by-defect?** (reference S1274 §3 gaps; Rigby SIGN cycle 1 Q4 +
Q8 fold — reframe from defect language to posture-decision language
per S1274 §12.3 "two legitimate postures" precedent)

1. **`sports_odds` → `SignalCluster` — POSTURE-DECISION-PENDING (not
   defect).** S1274 §14 Finding #6 lands here. `SignalCluster.
   pattern_type` at `core/models_signal_intelligence.py:75-86` declares
   10 canonical types (demand_spike, trend_emergence, sentiment_shift,
   opportunity_window, knowledge_gap, competitive_signal,
   market_movement, skill_demand, content_gap, user_need);
   `sports_odds` is not there. Sports odds do not participate in signal
   aggregation. Per S1274 v2 reframe: this is a decision point with two
   legitimate postures (integration would add a `sports_market_movement`
   or `sports_opportunity_window` pattern; island would formally close
   the bridge). Cat F evidence plan owns the disposition. Cat A does
   not claim this as a defect.
2. **`sports_odds` → Initiative auto-creation — POSTURE-DECISION-
   PENDING.** No pipeline converts a sports-odds row into an Initiative
   row. Not a defect for the same reason as (1). Confirms S1273 §3.10
   observation without prescribing.
3. **`BettingOutcomeVerifier` → SignalCluster / Deliberation —
   POSTURE-DECISION-PENDING.** Cat C owns this per parent §3.C. Same
   posture rationale.
4. **Cross-domain reconciliation for fixture identity — POSTURE-
   DECISION-PENDING.** See §8.3. Under an integration posture that
   requires cross-book aggregation or cross-spider line-movement
   intelligence, this becomes a HIGH item (Rigby SIGN cycle 1 Q7
   conditional). Under island posture, it is acceptable.
5. **Learning-loop bridge (sports signal → Memory Domain S1300) —
   POSTURE-DECISION-PENDING + delegated.** S1300 per parent
   `delegates_to` metadata.

**Q21 — What other domains depend on it?** Cat B (all 4 market agents),
Cat C (`BettingOutcomeVerifier` reads odds to settle wagers), Cat D
(brief generation reads live odds via TheOddsSpider re-invocation
and/or persisted `SpiderData`), Cat E (BettingPage), Cat F
(posture-decision brief consumes this audit).

**Q22 — What domains does it depend on?** External vendors only. No
internal cross-domain dependencies on the write path.

---

## 10. Event Flows

**Q19 — What events does it emit?** **None on the internal Django
signal / event bus surface.** Cat A does not fire Django signals or
publish to an internal event bus. Its "events" are:

- **Discord post** every 30 min (Flow D §7.4) — external observability side-channel.
- **Log records** — no persisted event surface.
- **Redis stream `spider:data:stream`** — only the 3 lightweight
  SportsOddsSpider mock configs publish here (not the 5 primary
  spiders); Sub-agent 4 verified.

**Q20 — What events should it emit?** (reference S1274 §6 event gaps)

- `sports_odds_snapshot_landed` (event surface consumed by SignalCluster
  aggregation) — currently MISSING. Cat F owns disposition.
- `line_movement_significant` (event surface consumed by Cat D content
  pipeline for reactive briefs) — currently MISSING. Cat D audit will
  scope.
- `ingestion_quota_warning` (event surface fired when The Odds API
  usage crosses N% of monthly cap) — currently MISSING (see debt §15).

---

## 11. Existing Documentation

**Q10 — What existing documentation exists?**

Per Sub-agent 5 exhaustive corpus sweep:

- `docs/topics/spider-network.md` lines 26, 40, 59-76, 91-120 — closest
  current-state Cat A narrative; discusses TheOddsSpider score fetching,
  signal aggregation flow, and lists `sports_odds` as a valid
  `SpiderData.data_type` (which conflicts with the enum reality — see §14).
- `docs/topics/celery-workers.md` lines 40, 104, 169-180 — sports queue
  task table; 8 sports tasks with schedules (Cat A subset: `collect_sports_odds`
  every 20m, `update_game_scores` every 30m, others Cat B-D).
- `docs/narratives/SPORTS_MONETIZATION_ML.md` lines 37-43, 89 — TheOddsSpider
  narrative + GamePredictor auto-create chain (21 SPORT_KEY_LEAGUE mappings) +
  8-task table.
- `docs/PLATFORM_WHAT_IT_IS.md` lines 97, 112-113, 199, 207, 326 — Sports
  Betting listed as a value stream + The Odds API + 40+ bookmakers +
  9-tab dashboard.
- `docs/SPIDERS.md` lines 78-79, 351 — theodds + kalshi status rows;
  combat_sports + horse_racing listed as "not in current focus".
- `docs/AUDIT_FINDINGS.md` §12 — canonical Celery deferred-by-policy list;
  Sub-agent 3 grep verified: **zero Cat A tasks on the deferred list**.
- Handoffs — 9 sessions reference Cat A (Sessions 950, 995, 995B, 998B,
  1010, 1011, 1012, 1500). Sub-agent 5 report §2 lists relevant hits.
- No `docs/topics/sports*.md` OR `docs/topics/betting*.md`. Sub-agent 5
  confirmed parent scoping §2.5 claim.

**Q11 — What research already exists?** Cross-reference
`ARCHITECTURE_INDEX.md`:

- S1273 §3.10 (Sports Intelligence / Betting Pipeline row — LIGHT).
- S1274 §3.10 + §14 Finding #6 (Sports/DBAO ↔ Signal/Content pipeline break — HIGH).
- S1274 §12.3 (Product/Architecture Decision Point P1 — island vs integrated postures).
- S1500 parent scoping doc §2.5 + §3.A + §5 + §6 (this arc's parent).
- No prior child audit.

---

## 12. Research Coverage

**Q13 — What is the research coverage?**

**Baseline before S1501:** LIGHT (per S1273 §5.10 coverage matrix; per
parent scoping §2.6 finding "Sports surface is larger than S1273 §3.10
captured").

**Post-S1501 verdict:** **MODERATE.** This audit produces:
- First formal Cat A ingestion inventory (5 spiders + 3 configs, sourced
  via 6-parallel Explore sweep + verifier loop).
- Grep-verified negative on unified normalization service.
- Grep-verified negative on retention job.
- Grep-verified negative on `SpiderData.data_type='sports_odds'` and
  `source_platform='theodds'` choices membership.
- Explicit runtime flow diagrams (4 flows).
- 4-item pre-brief mini-schema per surface, ready for Cat F consumption.

Cat A doesn't reach DEEP yet — that would require multiple focused
research docs (e.g., separate audit on bookmaker canonicalization,
separate audit on API cost / rate-limit management, separate audit on
retention policy design). Deferred to xx99 §8 follow-on queue if Cat F
posture decision warrants.

---

## 13. Architecture Maturity

**Q12 — What is the architecture maturity?**

**Ingestion layer: WORKING (fragile contract) — per Rigby SIGN cycle 1
Q2 fold.** Data flows in production. 5 spiders covering 40+ sports
leagues + prediction markets. Beat schedule runs. Discord digest posts.
Frontend renders reads. Nothing is broken at the runtime path — but the
Cat A → Cat B string-typed filter contract sits on top of two silent
choices-enum violations (§14.1). Runtime behavior is producing data
and downstream consumers are actively filtering those rows, so the
label is WORKING; the qualifier "(fragile contract)" acknowledges that
runtime success is not the same as schema-contract stability. Not
STABLE precisely because of the fragility, not below WORKING because
end-to-end flows succeed.

**Normalization layer: PARTIAL.** Two disjoint persistence stores
(`SpiderData` and `OddsSnapshot`/`GameLineHistory`) each populated by
its own task; no unified normalizer; no cross-store reconciler
(intent-status per Rigby SIGN cycle 1 Q4 fold: may be intentional
read-optimized-vs-semantic separation — see §2.1 Cat A contract
statement). Cat B agents filter by string that isn't in the model
enum. Continuous-language alignment per S1274 EventBus lesson: not
"dormant" (production verified), not "canonical" (schema contract not
stable + no source-of-truth doc), sits at PARTIAL.

**Composite verdict per playbook §12:** **WORKING (fragile contract)
at ingestion, PARTIAL at normalization.** Not `STABLE` (silent
choices-enum drift is not stable). Not `CANONICAL` (no source-of-truth
doc, no explicit contract statement outside this audit's §2.1).

---

## 14. Known Drift

**Q27 — What is drift?**

### 14.1 Silent choices-enum violations (2 fields, HIGH)

- `SpiderData.data_type` (`persistence/models.py:693-712`) enum lists
  14 valid values. `_impl_collect_sports_odds` at
  `core/tasks_financial.py:1771` writes `'sports_odds'`. Kalshi writes
  `'prediction_market'`. Neither is in the enum. Writes succeed because
  Django `CharField.choices=` validates only via `full_clean()` (Form /
  Admin path), not at `Model.save()`. Cat B agents match on the invalid
  string (see §9 Q14). This is the code-level materialization of S1274
  §14 Finding #6 and extends the finding's scope (S1274 named
  `SignalCluster.pattern_type` only).
- `SpiderData.source_platform` (`persistence/models.py:641-663`) enum
  lists 19 platforms (reddit, upwork, fiverr, ..., other). Cat A writes
  `'theodds'` and `'kalshi'` — neither in enum. Same silent-drift
  pattern.

### 14.2 Docstring vs code — Discord channel target (LOW)

`_impl_collect_sports_odds_intelligence` docstring at
`core/tasks_financial.py:1817` names target as "Discord
#market-intelligence". Code calls `send_betting_digest`
(`core/services/discord_notifications.py`), which routes to
`CHANNEL_BOARDROOM` (`1448819855557136595`, line 40) — NOT
`CHANNEL_MARKET_ALERTS` (`1448867150948335777`, line 44, which is the
one the internal `_send_by_name` map at line 1091 associates with the
string `'market-intelligence'`). Two consistent readings both possible:
(a) docstring is stale and code intent = #boardroom; (b) code should
have called a market-intelligence-scoped method but got wired to
boardroom. Cat A observation only — no design change proposed.

### 14.3 `snapshot_odds_for_line_movement` dormant vs docstring (MEDIUM)

Task docstring at `core/tasks_financial.py:2144`: "Runs every 20
minutes to build historical odds data for line movement charts."
Beat schedule at `core/celery.py:37-797` has **no entry** for
`snapshot_odds_for_line_movement` — Sub-agent 3 grep verified. Task is
only invocable via manual call or on-demand dispatch. Line-movement
tracking is latent unless another surface triggers it. `GameLineHistory`
row growth in production is bounded only by whatever trigger exists.

### 14.4 `docs/topics/spider-network.md` line 40 stale enum claim (LOW)

Topic doc lists `sports_odds` as a valid `SpiderData.data_type`. Reality
per §14.1: it is not. Doc drift.

### 14.5 Parent scoping §3.A "3× SportsOddsSpider configurations"
reads as production; runtime reads as mock (LOW)

Parent §3.A "Known drift" says "5 spiders + 3 lightweight-system
configurations overlap on odds retrieval". Sub-agent 4 verified those 3
configs are mock-data generators publishing to Redis on a 60-second
loop — not production ingestion competitors. Parent scoping evidence
was correct at the count but under-specified on operational status.
Refinement folded into this audit; propose Cat F evidence plan or
xx99 §7 anchor updates address parent-doc language.

---

## 15. Known Technical Debt

**Q26 — What is technical debt?**

Severity classifications adjusted per Rigby SIGN cycle 1 Q5 fold —
debt #1 confirmed HIGH; debt #2 downgraded from HIGH to
architecture-decision-pending (not automatic debt unless normalization
is Cat A's contract to Cat B, which §2.1 confirms it is NOT); debt #6
upgraded from LOW to MEDIUM until mock-config leak-into-production
possibility is verified gated.

| # | Debt | file:line | Severity | Cost | Rationale |
|---|---|---|---|---|---|
| 1 | Silent choices-enum violation on `SpiderData.data_type` + `source_platform` writes for sports/prediction-market rows | `persistence/models.py:693-712, 641-663` + `core/tasks_financial.py:1770-1782` | **HIGH** (Rigby SIGN cycle 1 Q5 confirmed HIGH — "not runtime-breaking today, but a silent contract breach that can break tomorrow" — fragility multiplier across every consumer + analysis layer) | Low-Med | 2-line change per site to add enum values OR refactor to dedicated model. Blocks S1274 §14 Finding #6 resolution. Cat F posture decision determines direction. |
| 2 | No unified odds normalization service | grep-verified negative in `core/services/` | **ARCHITECTURE-DECISION-PENDING** (Rigby SIGN cycle 1 Q5 fold — downgraded from HIGH; per §2.1 Cat A contract statement, normalization is NOT part of Cat A's Cat B contract, so this is not automatic debt) | High (if adopted) | Each spider writes its own persistence path. Cat F posture decision determines direction: integration posture would want a `SportsOddsNormalizationService`; island posture would formalize "per-spider persistence by design" in §2.1 language. Neither posture is Cat A prescription. |
| 3 | `snapshot_odds_for_line_movement` dormant vs docstring | `core/tasks_financial.py:2140` + `core/celery.py:37-797` grep negative | MEDIUM | Low | Docstring implies 20-min beat schedule but no `PeriodicTask` or `core/celery.py` beat entry exists. Rigby SIGN cycle 1 Q8 fold: this is an "unimplemented expectation" (code + docstring imply schedule; no explicit spec-level guarantee) rather than a specification-vs-code violation. Fix: either add beat entry OR update docstring + document explicit trigger contract. |
| 4 | No retention policy on `OddsSnapshot` / `GameLineHistory` | `core/models_odds_history.py` + `core/tasks*.py` grep negative | MEDIUM | Low-Med | Add beat task to prune rows > N days. Not urgent because `snapshot_odds_for_line_movement` is dormant (issue #3) — but pairs with #3. Under production cadence, `OddsSnapshot` grows unbounded. |
| 5 | `SportsDataSpider` half-shipped persistence layer | `ai_core/spiders/sports_data_spider.py:317-334` | LOW-MED | Low | Sub-agent 4 finding: `fetch_and_store_data()` has async framework but DB write is a `logger.info` placeholder. Either complete or deprecate. |
| 6 | 3× `SportsOddsSpider` mock configs in parallel loop | `ai_core/spiders/lightweight_spider_system.py:330-332` + orchestrator 60s cycle | **MEDIUM** (Rigby SIGN cycle 1 Q5 fold — upgraded from LOW; only stays MEDIUM until leak-into-production possibility is verified gated) | Low | Confirm intent (test-only / production-fallback / prototype). If mock rows land indistinguishable from real ingestion output on `SpiderData` or the Redis stream that downstream consumers read, this is misleading-data risk. If test-only and gated by env flag, LOW is fine. Currently runs every 60s in production Redis without documented purpose — gating status UNKNOWN. |
| 7 | Docstring drift on Discord channel (`_impl_collect_sports_odds_intelligence`) | `core/tasks_financial.py:1817` | LOW | Trivial | 1-line docstring fix OR route change. Depends on intent. |
| 8 | Fixture / entity identity not resolved across spiders | grep verified negative for cross-referenced canonical model | MEDIUM (Rigby SIGN cycle 1 Q6 close runner-up to debt #1; upgrade to HIGH conditional on any xx99 intent for cross-book aggregation or cross-spider line-movement intelligence per Rigby SIGN cycle 1 Q7) | Med-High | TheOdds `event_id` and Kalshi `ticker` live in different namespaces on `SpiderData.structured_data`. Agents that read across both must reconcile in-code. Rigby SIGN cycle 1 Q8 fold called this out; Cat F evidence plan owns disposition. Rigby notes this causes "quiet analytic corruption rather than obvious failures" — invisible-failure mode. |
| 9 | No rate-limit / quota telemetry for The Odds API | `ai_core/spiders/specialized/theodds_spider.py:37-40` + `_make_request` circuit-breaker only | LOW-MED | Low-Med | Spider logs API usage per collection cycle (`spider.get_api_usage()` at `_impl_collect_sports_odds:1794`) but no persisted quota tracking, no `ingestion_quota_warning` event, no alert when N% threshold crossed. Under current cadence usage is ~3k/month (well under 20k cap), but under scaled ingestion this becomes load-bearing. |

### 15.1 4-item pre-brief mini-schema per debt item (D62 fold)

| Debt | (a) sports-only vs shared | (b) DBAO vs public | (c) integration (refactor/extend) | (d) island (isolation-additions) |
|---|---|---|---|---|
| #1 choices violations | shared model, sports-scoped rows | public persistence app | REFACTOR (extend enum or move to dedicated model) | full island needs dedicated `SportsOdds` + `PredictionMarket` models OR opt-out of `SpiderData` for sports |
| #2 no normalization service | sports-only | public core (would live in `core/services/`) | EXTEND (add service) | strong isolation improves if service is added inside a dedicated `dbao` module |
| #3 dormant snapshot task | sports-only | public core | EXTEND (add beat entry) | additive |
| #4 no retention | sports-only | public core | EXTEND (add cleanup task) | additive |
| #5 SportsDataSpider half-shipped | sports-only | writes public via Django ORM (in placeholder path) | REFACTOR OR DEPRECATE | additive if kept + isolated |
| #6 3-config mock loop | sports-only | Redis (transient) | EXTEND (gate by env) or DEPRECATE | additive |
| #7 Discord channel drift | sports-only content | public channel | trivial docstring fix | N/A |
| #8 fixture identity | shared identity concern | public | REFACTOR (canonical Game model) OR contract | either posture needs it |
| #9 quota telemetry | sports-only | writes public event / DB | EXTEND | additive |

---

## 16. Boundary Violations

**Q24 — What services violate boundaries?**

Cat A itself does not import cross-domain internals. But the surface
raises three boundary observations that Cat F evidence plan consumes:

1. **`SpiderData` is a shared cross-domain container** — Cat A writes
   into it alongside all other spiders. This is by design (single
   spider ingestion surface). But it means Cat B agents that filter
   by `data_type == 'sports_odds'` are running string-matched joins
   across a schema that Cat A can't enforce. Not a violation, but a
   contract-boundary weakness.
2. **CombatSportsSpider + HorseRacingSpider are Cat A → but produce
   intelligence content, not odds proper.** Cat A boundary is
   "ingestion + normalization". These two spiders sit uncomfortably on
   the edge — they collect sports-domain content (Reddit posts, MMA
   forums, racing RSS) but do not write `data_type='sports_odds'` rows.
   Their `data_type='combat_sports_intelligence'` and `'horse_racing'`
   rows are consumed as intelligence / narrative context by downstream
   agents. Chris ratified their inclusion in Cat A via parent §3.A —
   but a future Cat A → Cat D refactor might reassign them. Observation
   for Cat F evidence plan, not a Cat A violation.
3. **Kalshi is a cross-scope spider held to sports-scope only in this
   arc.** Kalshi's non-sports categories (elections, tech, weather,
   economics) are ingested by the same beat task — but per D60 anti-
   scope, Group 1500 only considers the sports slice. Cat A observation.

---

## 17. Duplicate or Overlapping Systems

**Q23 — What models overlap with other domains?** (reference S1274 §5)

- **`SpiderData` sports_odds rows** and **`OddsSnapshot` / `GameLineHistory`**
  are not duplicate models (different shape, different use case) but
  they overlap on **subject** — both persist odds data derived from
  TheOddsSpider. No FK, no reconciler, no shared idempotency layer.
  **Cat A explicit clarification per Rigby SIGN cycle 1 Q4 + Q9 fold:**
  `SpiderData` = semantic/log surface (agent-consumable via
  `data_type` filter + embedding-backed RAG); `OddsSnapshot` = UI
  read-model surface (line-movement chart queries); no canonicalizer
  exists today. Whether this dual-store shape is a defect or a
  design-consistent posture is a Cat F decision, not a Cat A
  prescription. Cat A's job is to name that the shape exists and
  characterize the join / dedup implications.
- **KalshiSpider `data_type='prediction_market'`** overlaps
  conceptually with sports odds (Kalshi has sports contracts) but is
  written to a different `data_type` string that Cat B agents' sports
  filters do not match. Under integration posture, prediction-market
  rows relevant to sports should be routed to `sports_odds` (or a
  unified event surface). Under island posture, Kalshi's sports slice
  stays separated. Observation.

---

## 18. Ownership Gaps

**Q25 — What ownership is unclear?**

- **Cat A code owners:** clwest is the de-facto contributor per Sub-agent 6
  `git log --format="%an"` sample (7-11 commits over 6 months across
  Cat A files depending on the file). No `CODEOWNERS` file exists at
  `/CODEOWNERS`, `.github/CODEOWNERS`, `docs/CODEOWNERS`, or
  `docs/OWNERSHIP.md`. Backup owner undefined.
- **`OddsSnapshot` + `GameLineHistory` schema owner:** implicit —
  clwest via task changes; no explicit data-owner assignment.
- **Discord `#boardroom` channel owner:** unknown. If channel is
  archived / renamed, `send_betting_digest` posts silently fail (`send_
  betting_digest` catches exceptions and logs warning without alert
  per Sub-agent 6). Chris (email `chris@donkeybetz.com`) implied by
  context but unconfirmed.
- **`SignalCluster.pattern_type` gap owner:** sports pattern would need
  to be added to a shared model; owner of that decision unclear.
  Deferred to Cat F evidence plan.

---

## 19. Recommended Future Research

**Q28 — What should be researched next?**

Ranked by architectural uncertainty × risk × unblocked flows. Rank
order updated per Rigby SIGN cycle 1 Q7 folds: enum resolution
promoted from MED to HIGH (tie with Cat F posture-evidence for #1-2);
fixture-identity conditionally HIGH under cross-book aggregation
intent; new item added — "Downstream consumer inventory".

1. **[HIGH] Category F posture-decision evidence plan (S1506).** The
   arc's load-bearing lens question. Cat A evidence in this doc lands
   cleanly on both sides. Cat F must consolidate and produce the
   evidence-plan brief owed to xx99 per D59.
2. **[HIGH — Rigby SIGN cycle 1 Q7 fold, promoted from MED]**
   **`SpiderData.data_type` + `source_platform` enum resolution.**
   Highest fragility multiplier in Cat A per Rigby cycle 1 Q6 — silent
   contract drift affects every consumer + analysis layer, and it is
   the most fixable per unit effort once scoped. Whether to extend the
   enums or move sports_odds / prediction_market to dedicated models.
   Cat F posture decision determines direction; after Chris picks
   posture, this is a bounded engineering task.
3. **[HIGH — Rigby SIGN cycle 1 Q7 fold, new item]** **Downstream
   consumer inventory.** What actually reads `SpiderData` sports_odds
   rows today vs what reads `OddsSnapshot`/`GameLineHistory` today?
   This is the missing evidence that resolves whether dual-store is
   intentional posture or accidental divergence (§17 open question).
   Should be produced before or alongside Cat F posture-decision brief
   to give Cat F a concrete "who breaks if we change X" table. Cat B
   P2 partially owns this via agent-consumer audit; Cat E P5 partially
   owns via frontend read-side. Cat F consolidates.
4. **[MED-HIGH conditional — Rigby SIGN cycle 1 Q7 fold]** **Fixture
   / entity identity resolution across spiders.** Rigby Q8 fold surface.
   Cat F evidence plan should consume Cat A's observation that TheOdds
   `event_id` and Kalshi `ticker` live in different namespaces with no
   reconciler. Upgrade to HIGH if xx99 intends any cross-book
   aggregation or cross-spider line-movement intelligence.
5. **[MED] `snapshot_odds_for_line_movement` scheduling decision.**
   Should this task be beat-scheduled per its docstring, or is the
   docstring wrong? Bounded question, low cost.
6. **[MED] Retention policy for `OddsSnapshot` + `GameLineHistory`.**
   Under production cadence, unbounded row growth. Pairs with (5).
7. **[LOW-MED] Cost / quota telemetry for The Odds API.** Add persisted
   quota tracking + `ingestion_quota_warning` event.
8. **[MEDIUM — upgraded per Rigby SIGN cycle 1 Q5 fold, previously LOW]**
   **Consolidate the 3× lightweight `SportsOddsSpider` mock configs
   into an explicit test-mode gate or deprecate.** Currently runs every
   60s in production Redis without documented purpose. Stays MEDIUM
   until leak-into-production possibility is verified gated.
9. **[LOW] `SportsDataSpider` half-shipped persistence.** Complete or
   deprecate.
10. **[LOW] `docs/topics/sports*.md` OR `docs/topics/betting*.md`
    topic-doc creation.** Sub-agent 5 confirmed no sports-scoped topic
    doc exists; this arc's xx99 canonical summary may recommend one.

**Not next in this arc:** implementation of any of the above. Research
first (this arc + xx99), Chris picks posture, then design-preparation
docs, then PRs.

---

## 20. Appendix

### 20.1 Files inspected (parent verifier-loop reads on load-bearing claims)

Beyond the 6 sub-agent file inventories (see their appendices), the
parent agent (Claude) directly verified the following on `main` HEAD
`c7dac6d9`:

- `persistence/models.py:611-780` — SpiderData model + `data_type` and
  `source_platform` choice enums.
- `core/models_odds_history.py:1-143` — full file (OddsSnapshot +
  GameLineHistory).
- `core/tasks_financial.py:1659-1810` — `_impl_collect_sports_odds` in full.
- `core/tasks_financial.py:2130-2270` — `_impl_snapshot_odds_for_line_movement`.
- `core/celery.py:775-797` — beat schedule visible slice (verified 4
  sports-related entries + confirmed absence of
  `snapshot_odds_for_line_movement`).
- `core/services/discord_notifications.py:36-1149` — channel constants
  + `send_betting_digest` + `_send_by_name` channel-name map.

### 20.2 Grep patterns and result counts

- `grep -rn "class.*Odds\|class.*Sports.*Spider" core/services/ ai_core/` — 5 matches (spiders + coordinator).
- `grep -rn "def.*normaliz.*odds\|class.*OddsNormaliz\|class.*Coordinator.*Odds" core/services/` — **0 matches** (proves normalization-service absence).
- `grep -rn "OddsSnapshot\|GameLineHistory" core/services/` — **0 matches** (service layer does not touch these models).
- `grep -rn "sports_odds" persistence/models.py` — **0 matches** (proves enum absence).
- `grep -rn "theodds" persistence/models.py` — **0 matches** (proves source_platform enum absence).
- `grep -rn "snapshot_odds_for_line_movement" core/celery.py` — **0 matches** (proves no beat entry).
- `grep -rn "retention\|cleanup" core/tasks*.py | grep -i "odds\|snapshot"` — 0 matches (proves no retention job).

### 20.3 Unresolved unknowns

- Operational status of `SportsDataSpider` (dormant / active fallback / deprecated?).
- Intent behind 3× `SportsOddsSpider` mock configs (test / prototype / fallback?).
- Discord channel drift root cause (docstring stale vs code mis-wired).
- Fixture-identity reconciliation across TheOdds `event_id` and Kalshi
  `ticker` — no cross-referenced canonical model found; whether agent-
  layer reconciliation exists is Cat B P2 scope.
- Whether `/ws/dbao/` is a deployed WebSocket namespace or only a
  test-file reference.

### 20.4 Conflicts between sources

- Sub-agent 1 initial claim: "no visible producer for OddsSnapshot"
  — **incorrect**. Parent verifier read `tasks_financial.py:2140-2270`
  and confirmed `_impl_snapshot_odds_for_line_movement` is the producer.
  Corrected in §4 + §7.2.
- Sub-agent 1 claim on `GameLineHistory` Meta.indexes — parent
  verifier confirmed no additional `Meta.indexes` beyond field-level
  `db_index=True`. Corrected in §4.2.
- Sub-agent 3 categorization of `collect-kalshi-prediction-markets` as
  Cat B — parent verifier confirmed Kalshi is in Cat A per parent
  scoping §3.A. Corrected in §3.1.

### 20.5 Verifier-loop history (SIGN fold notes)

**Rigby Full SIGN cycle 1** — 2026-07-01 on fresh isolation pin
`pa-a39069230ab64450` (minted via `session_tool.create_fresh` on arc
pin `pa-791b3db549a64e54`; D48 preemptive stability-probe gate applied
per S1405+S1406+S1499 3-arc pattern — stability probe returned "ready"
on first turn, no worker-instability observed on any of the 3
substantive SIGN batches; batches ran titles-only per Rigby SIGN
worker-instability recovery protocol).

**Cycle 1 verdict:** SIGN-with-edits at Medium-High confidence. Cycle 2
prediction (from Rigby): SIGN-clean at High confidence after the fold
edits below land — required changes are editorial / structural, not
new investigation.

**Cycle 1 folds landed at commit-time (before cycle 2 SIGN):**

- **F1 (Rigby Q2 fold — §13 maturity qualifier).** Maturity call
  changed from "WORKING at ingestion, PARTIAL at normalization" to
  "WORKING (fragile contract) at ingestion, PARTIAL at normalization"
  with the qualifier acknowledging runtime success ≠ schema-contract
  stability.
- **F2 (Rigby Q4 fold — §9 Q15 posture-decision reframe).**
  Integration-gap language ("MISSING") reframed to
  posture-decision-pending language throughout §9 Q15, §1 exec
  summary, and §17 Duplicate/Overlap. Cites S1274 §12.3 two-legitimate-
  postures precedent as the licensing rationale for the reframe.
- **F3 (Rigby Q4 + Q9 fold — §17 dual-store clarification).**
  `SpiderData` = semantic/log surface vs `OddsSnapshot` = UI read-model
  surface stated explicitly, with disposition ("defect vs
  design-consistent posture") delegated to Cat F.
- **F4 (Rigby Q5 fold — §15 debt table severity adjustments).**
  Debt #1 confirmed HIGH; Debt #2 reclassified from HIGH to
  ARCHITECTURE-DECISION-PENDING (per §2.1 Cat A does not contract
  normalization to Cat B); Debt #6 upgraded from LOW to MEDIUM until
  mock-config leak-into-production possibility is verified gated.
- **F5 (Rigby Q7 fold — §19 rank order + new item).** Enum resolution
  promoted from MED to HIGH (tie for #1-2 with Cat F posture-evidence);
  fixture-identity upgraded to conditional MED-HIGH under cross-book
  aggregation intent; new item added — "Downstream consumer inventory"
  — HIGH #3 (resolves dual-store intent-vs-accident question).
- **F6 (Rigby Q8 fold — §14.3 drift-vs-unimplemented-expectation).**
  "Missing beat entry" for `snapshot_odds_for_line_movement` reframed
  as "unimplemented expectation" (code + docstring imply schedule; no
  explicit spec-level guarantee) rather than a spec-vs-code violation.
- **F7 (Rigby Q9 fold — new §2.1 Cat A contract statement).** Added
  explicit "Cat A guarantees today" vs "Cat A explicitly does NOT
  guarantee" paragraph pair. Prevents this doc from being read as
  promising Cat B / Cat D / Cat F behavior it does not own. Consumers
  who need any of the "does NOT guarantee" behaviors depend on Cat F
  posture decision + follow-on design work.

**Cycle 2 SIGN** — Rigby Full SIGN cycle 2 SIGN-clean at High
confidence 2026-07-01. Cycle 1 prediction was accurate. Rigby's cycle 2
verdict:

- Overall confidence: **High**
- Most accurate part: **risk framing + contract clarity** — the §2.1
  Cat A contract statement (F7) combined with the "WORKING (fragile
  contract)" maturity call (F1) and the enum/choices issue held as
  top debt (F4/F5) makes the audit read operationally true and hard
  to misinterpret.
- Weakest part: **posture-decision surfaces** still depend on
  downstream evidence quality (even after the reframe) — the doc is
  correctly labeled "decision pending" but is inherently less
  conclusive than the ingestion/enum findings until the new
  "Downstream consumer inventory" (§19 #3) executes.
- Residual folds: **NONE required**. SIGN-clean for folding into
  `ARCHITECTURE_INDEX §1.31`. Remaining open items are explicitly
  tracked as future research / decision points, not unresolved
  ambiguity.
- Rigby cycle 2 note on cycle 1 folds: "F2/F3/F6 removed the main
  misclassification risk (defect vs intentional posture), and F4/F5
  aligned severity/rank so the doc's center of gravity matches the
  real fragility multipliers. That's exactly what was needed to move
  from Medium-High to High."

**Do-not-regress notes for PR + post-arc anchor updates:**

- Keep §2.1 Cat A contract statement (F7) intact — do not soften or
  remove the "explicitly does NOT guarantee" list.
- Keep posture-decision-pending framing throughout §9 Q15 + §17 —
  do not backslide to "MISSING integration" defect language.
- Preserve enum-resolution HIGH severity in §15 debt #1 + §19 rank
  #2 — do not downgrade in copy-editing.

**D48 preemptive stability-probe gate — 4th arm codification-ready.**
This SIGN cycle marks the 4th consecutive arc-close with clean stability
probe + zero worker-instability across multiple substantive SIGN
batches (S1405, S1406, S1499, S1501). Per Rigby cycle-1 feedback rule
`feedback_rigby_sign_worker_instability_recovery.md`: after S1501, D48
is CODIFICATION-READY for playbook v3 §15 addition. The pattern that
codifies: (a) mint fresh isolation pin, (b) stability probe with
ultra-short "confirm ready" message, (c) if probe returns clean,
proceed to titles-only batched SIGN 2-3 findings per prompt, (d) if
probe stalls or first substantive turn stalls, retire pin + mint
fresh + retry. xx99 §10 meta-methodology section owns the eventual
codification recommendation.

### 20.6 Sub-agent provenance

Six parallel Explore sub-agents launched by parent Claude S1501-P1 at
2026-07-01. Each sub-agent operated on `main` HEAD `c7dac6d9` under
scope `Category A only`. Sub-agent structured reports referenced but
not verbatim included (parent verifier-loop applied per §14).

- Sub-Agent 1: Models & Persistence
- Sub-Agent 2: Services & Runtime Flows (owned the load-bearing "no
  unified normalization" negative)
- Sub-Agent 3: APIs / Tools / Tasks / Commands (owned the load-bearing
  Discord channel drift + dormant snapshot task)
- Sub-Agent 4: Spider Ingestion Detail (owned the load-bearing
  `data_type='sports_odds'` enum-violation grep proof)
- Sub-Agent 5: Documentation & Prior Research (owned the topic-doc
  gap + docs-cascade freshness verification)
- Sub-Agent 6: Drift / Debt / Ownership / Maturity (owned the drift
  matrix + debt matrix + WORKING-→-PARTIAL maturity call)

### 20.7 Frontmatter provenance

Per playbook §6 frontmatter standard. See document header.

---
