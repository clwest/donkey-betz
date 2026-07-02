---
title: "S1500 Sports/DBAO/Intelligence — Parent Architecture Scoping (Group 1500 mission plan)"
status: active (parent — all Chris decisions locked 2026-07-01: D56 D57 D58 D59 D60 D61 via one "agree all + D-6=(a)" ratification round; governance decision `81d7467e-add6-420f-aee9-60b67d7867e8` acted; Rigby pre-ratification pressure-test folded into §3/§10/§12 wording; Rigby Light SIGN cycle 1 SIGN-with-edits at 0.74 confidence → 9 surgical folds landed at commit-time (Q1 Category D boundary clarification; Q2 §4 explicit "which evidence needs children" list; Q3 §5 pre-brief mini-schema artifact; Q4 `sports_intelligence` flag ownership P6 not xx99; Q5 §7 bankroll/staking anti-scope; Q6 §10 wording "unchanged sectional structure and intent" over "no additions no refinements"; Q7 §12.4 tightened to "3 of 4 including scope-confusion-prevented OR cleaner-arc-close"; Q8 §12.5 fixture/entity identity resolution lifecycle stage added; Q10 §10.2 softened "partial architectural isolation" over "island posture partially adopted"); Q9 4 anchor cites re-verified (`tasks_financial.py:1815`, `views.py:44`, `celery.py:783,788` corrected from 784, `test_websockets.py:51`) — cycle 2 expected SIGN-clean at 0.78 confidence per Rigby cycle 1 verdict; Phase 0 F.i/F.ii/F.iii methodology applied with unchanged sectional structure and intent per D58 second application after S1400 first application)
authority: parent-doc for Group 1500 research arc + SECOND application of Chris's Phase 0 3-step methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria) — D58 keeps methodology unchanged to preserve v3 promotion trigger integrity per S1400 D29 two-triggers rule; promotion at Group 1500 xx99 close if arc closes clean per playbook §20
category: parent_scoping
session: 1500
date: 2026-07-01
decisions_locked: 2026-07-01 (D56 D57 D58 D59 D60 D61 via "agree all + D-6=(a)" ratification round; governance decision 81d7467e-add6-420f-aee9-60b67d7867e8 marked `acted`)
domain_slug: sports
research_group: 1500
authors: Claude Code (Chris directed via short command "start research group 1500")
supersedes: none
related:
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                             # process (S1274 v1 → v2 S1276) — §11.1 template applied here for the second time
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                    # OS (S1278) — arc-open contract §8
  - docs/research/OPEN_ARCS.md                                            # arc manifest — Group 1400 → Group 1500 handoff
  - docs/research/platform_architecture_inventory.md §3.10                # Sports Intelligence / Betting Pipeline (S1273 v2 row)
  - docs/research/platform/cross_domain_integration_audit.md §3.10        # Sports/DBAO ↔ Signal/Content pipeline break — HIGH severity (S1274)
  - docs/research/platform/cross_domain_integration_audit.md §12.3        # Product/Architecture Decision Point (P1) — island vs integrated postures with explicit success criteria for BOTH (S1274 v2 Rigby cycle 2 reframe)
  - docs/research/platform/cross_domain_integration_audit.md §14 line 1469 # Finding #6 — sports_odds not a SignalCluster data_type HIGH (S1274)
  - docs/research/domains/memory/1300_memory_domain_scoping.md            # parent-with-children exemplar (S1300)
  - docs/research/domains/memory/1399_memory_canonical_summary.md         # first formal xx99 canonical summary (S1399)
  - docs/research/domains/revenue/1400_revenue_domain_scoping.md          # first application of Phase 0 F.i/F.ii/F.iii methodology (S1400) — trigger 1 of two-triggers rule
  - docs/research/domains/revenue/1499_revenue_canonical_summary.md       # second xx99 canonical summary + second application of §11.3 §10 template (S1499)
  - docs/PLATFORM_INVENTORY.md                                            # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                                           # narrative anchor
scope: Phase 0 domain-definition — decide whether Group 1500 is a single canonical audit or a parent-with-children research arc; produce candidate subdomain taxonomy grounded in verified runtime surface; propose child mission sequence for Chris to lock; frame (do NOT decide) the S1274 §12.3 island-vs-integrated posture decision point as the arc's load-bearing lens question owed to xx99 canonical summary as evidence plan, not recommendation
non_goals:
  - the audit itself (that begins after Chris picks parent-vs-single + locks §5 sequence)
  - answering the 28 playbook canonical questions (that is the audit's job)
  - resolving S1274 §12.3 island-vs-integrated posture selection at Phase 0 (that requires child evidence sweeps per D59 refinement; posture decision framing + evidence plan only — Chris gates actual selection post-arc after xx99 evidence lands)
  - any implementation proposal (this is scoping, not architecture design)
  - non-sports Intelligence scope (stock intelligence, legislation intelligence, narrative intelligence — bounded out per D60)
  - mobile-app / React-Native betting-app scope beyond FK boundaries to core sports models (defer to relevant child if surfaces)
  - external companion project scope (`BILLING_MONETIZATION_SYSTEM.md` from ai-content-studio treated as design context, not runtime — matches S1400 pattern)
  - Odds API vendor selection (product decision, not architecture)
delegates_to:
  - S1300 Memory Domain (learning-loop path for sports signals into Memory arc — Category F sub-question if promoted)
owner: claude (Chris directed at S1500 open via short command "start research group 1500")
verifier_loop: Rigby Light SIGN cycle 1 SIGN-with-edits at 0.74 confidence 2026-07-01 → 9 folds landed (Q1-Q10 surgical; no taxonomy break) → cycle 2 SIGN-clean at 0.83 confidence 2026-07-01 (higher than Rigby's cycle 1 prediction of 0.78; two "do not regress" notes for PR: keep §10.2 softened language + preserve corrected `celery.py:783` anchor cite)
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/platform_architecture_inventory.md
  - docs/research/platform/cross_domain_integration_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
---

# Session 1500 — Sports/DBAO/Intelligence Domain Taxonomy Proposal (Phase 0)

> **What this doc is.** A scoping deliverable produced *before* any
> Sports domain audit begins. Chris typed the short command "start
> research group 1500" at S1500 open — the D56 launch verdict per
> `00-START-NEXT-SESSION.md` Path B (playbook §22 next-arc queue
> default). This doc opens the arc by (a) recording the six
> Chris-ratified verdicts D56-D61, (b) demonstrating from verified
> runtime evidence that Sports is much larger than S1273 §3.10
> captured — a 5-model, 4-service, 5-spider, 6-task, 9-tab UI
> surface with a discrete PostgreSQL schema (`dbao`) and its own
> WebSocket namespace (`/ws/dbao/`), (c) proposing a candidate
> subdomain taxonomy Chris can inspect and edit, and (d) framing
> the S1274 §12.3 "island vs integrated" posture decision point as
> the arc's load-bearing lens question — with **posture decision
> framing + evidence plan** as the deliverable owed to xx99, NOT
> posture recommendation (D59 refinement folded from Rigby's
> pre-ratification pressure-test).
>
> **What this doc is not.** The audit itself. A design proposal.
> A recommendation about *how* Sports should work. Not a posture
> selection between integration and island — that decision is
> Chris-gated per S1274 §12.3 and requires child evidence sweeps
> that have not yet run. Every claim below cites either an
> existing research doc (S1273 / S1274 / S1300 / S1399 / S1400 /
> S1499) or a verified file:line at the current `main` HEAD
> (f7704586).

---

## 1. Why Phase 0

The Group 1400 Revenue arc closed at S1499 as the second successful
parent-with-children application (following Group 1300 Memory closed
at S1399). Both prior arcs opened with Phase 0 scoping doctrine:
Group 1300 established the pattern (S1300 parent scoping →
5-child arc → S1399 canonical summary); Group 1400 refined it by
applying Chris's Phase 0 F.i/F.ii/F.iii 3-step methodology (D29
Chris-locked at S1400 close) as a first empirical application
proposed for playbook v3 §11.1 template addition on the two-triggers
rule.

The playbook §22 domain queue row for Group 1500 is:

> **1500** — Sports / DBAO / Intelligence — §3.10 — LIGHT coverage
> — Resolves platform's biggest structural question (island vs
> integrated per S1274 §12.3).

The label carries three coordinated nouns ("Sports / DBAO /
Intelligence") — the same signal that predicted parent-with-children
shape for Groups 1300 ("Memory / Knowledge / Embeddings") and 1400
("Revenue / Outreach / Engagement"). Whether that pattern-match
holds — and if so, what the correct subdomain decomposition is — is
the first-order Phase 0 question.

There is a **second-order** Phase 0 question specific to Group 1500
that Group 1400 did not carry: S1274 §12.3 (as reframed at Rigby
cycle 2) explicitly names Sports/DBAO ↔ AI Studio as a
**product/architecture decision point** (not a defect) with **two
legitimate postures — integration and island — each with its own
success criteria**. That decision point is currently the
platform's biggest structural question per S1274 §12.3 preamble +
playbook §22 priority rationale. Phase 0 must decide how to route
that question through the arc: does xx99 owe an evidence-based
posture recommendation, or does xx99 owe a posture decision framing
+ evidence plan that leaves the actual selection to Chris in a
post-arc T-slot?

D59 answers the latter: **Phase 0 frames the posture question and
specifies the evidence plan; children gather the evidence; xx99
consolidates the evidence into a Chris-gated decision brief; Chris
picks the posture in a post-arc ADR**. This preserves Phase 0's
scoping-only discipline (playbook §8 rule: parent is not a design
proposal) and preserves Group 1500's status as an unchanged second
application of the F.i/F.ii/F.iii methodology (D58) so the v3
promotion trigger stays clean per D29 (Rigby's cycle-1 caution
folded).

The playbook (S1274 §2 rule 3) explicitly permits and encourages
this shape:

> If the domain is bigger than expected, splitting into sub-groups
> is fine. Do not force a single session to cover a multi-subsystem
> domain.

The load-bearing questions for Phase 0:

1. **Is Sports one domain, or a parent capability composed of
   several subdomains that each warrant their own child audit?**
2. **What does the posture-decision evidence plan look like for
   Group 1500 xx99 to consolidate — and which children own which
   pieces of evidence?**

---

## 2. What existing inventory already tells us

Four research artifacts already say something material about the
Sports/DBAO/Intelligence surface. Each is cited, not restated,
per playbook §7.

### 2.1 S1273 §3.10 — Sports Intelligence / Betting Pipeline (LIGHT)

`docs/research/platform_architecture_inventory.md:2809` records:

> §3.10 sports pipeline break: `sports_odds` not a valid
> SignalCluster data_type — structural question "island vs
> integrated?" unresolved.

The S1273 row was rated **LIGHT coverage** in the S1273 §5.10
coverage matrix — meaning the surface was identified but not deeply
inventoried by the S1273 sweep. This is the ground state Phase 0
inherits.

### 2.2 S1274 §3.10 + §14 Finding #6 (HIGH) — Sports/DBAO ↔ Signal/Content Pipeline Break

`docs/research/platform/cross_domain_integration_audit.md:1469`:

> Finding #6 (HIGH): Sports/DBAO ↔ Signal/Content pipeline break —
> `sports_odds` not a SignalCluster data_type; structural question
> "island vs integrated?" unresolved; unblocks Sports ↔ AI Studio
> Integration Sketch (S1273 §9 #4).

Concrete gap: sports odds data collected by 5 spiders lands as
`SpiderData` rows with `data_type='sports_odds'`, but Signal Engine
(`core/models_signal_intelligence.py:75-86`) declares 10 canonical
`SignalCluster.pattern_type` values (`demand_spike`,
`trend_emergence`, `sentiment_shift`, `opportunity_window`,
`knowledge_gap`, `competitive_signal`, `market_movement`,
`skill_demand`, `content_gap`, `user_need`) — none of which include
sports. The `sports_odds` string is valid on legacy `SpiderData` but
invalid as a `SignalCluster` classification path. This blocks the
current cross-domain flow.

### 2.3 S1274 §12.3 — Product/Architecture Decision Point (P1)

`docs/research/platform/cross_domain_integration_audit.md:1561-1597`:

> Reframed S1274 v2 per Rigby SIGN — v1 framed this as a
> "structural question" implying a defect. Rigby's correction:
> it's a decision point with two legitimate postures, each with
> explicit success criteria. Research should enumerate the
> criteria, not presume the answer.

Two postures with success criteria:

1. **Integration posture** — sports outcomes flow into signal
   clustering, initiative auto-creation, content deliberation.
   Success criteria owed: what integrations MUST exist; what
   performance / cost / correctness bars; what content types
   become enabled.
2. **Island posture** — sports intentionally stays isolated (own
   queue, own models, own agent pool, own PA tools). Success
   criteria owed: what boundaries MUST stay hard; what content /
   insight is explicitly out of scope; what operational invariants
   must the island preserve.

Deliverable owed by any Group 1500 arc that touches this: both
postures documented with explicit success criteria + failure modes
+ operational cost estimate. **Chris gates the actual selection.**

This is not novel work for Group 1500 to invent — it is scope
already assigned to a P1 mission by S1274. Group 1500's job at
Phase 0 is to (a) decide which children carry which pieces of the
posture evidence + (b) confirm xx99 owns the consolidation into a
Chris-gated decision brief.

### 2.4 S1273 §9 #4 — Sports/DBAO ↔ AI Studio Integration Sketch (Mission #4)

`docs/research/ARCHITECTURE_INDEX.md:31,2029,2763-2774` — cross-arc
reference to the S1273 recommended mission #4:

> Sports/DBAO ↔ AI Studio Integration Sketch — P1 research doc;
> DBAO stack operationally-separate from AI Studio.

This confirms Group 1500's mandate to answer at what level Sports/
DBAO integrates with the mainline platform. Two prior research
artifacts (S1273 §9 #4 and S1274 §12.3) independently name the
same question. That is independent evidence that Group 1500 must
carry it.

### 2.5 Verified runtime evidence (this session's Explore sweeps)

Independent evidence gathered at S1500 open via two Explore
sub-agents against `main` HEAD f7704586:

**Sports betting subsystem (verified surface):**

| Component | Count | Anchor |
|---|---|---|
| Django models | 5 | `core/models_betting.py:13,108,163` + `core/models_odds_history.py:15,82` |
| Services | 4 | `core/services/sports_betting_coordinator.py:21` + `core/services/betting_outcome_verifier.py:21` + `core/services/sports_content_context.py:27` + `ai_core/spiders/sports_data_spider.py:18` |
| Spiders | 5 | `ai_core/spiders/specialized/theodds_spider.py:33` + `ai_core/spiders/specialized/kalshi_spider.py:28` + `ai_core/spiders/specialized/combat_sports_spider.py:30` + `ai_core/spiders/specialized/horse_racing_spider.py:18` + `ai_core/spiders/sports_data_spider.py:18` |
| Agents (`core/agents/markets/`) | 4 | `sports_odds_analyst.py`, `game_predictor.py`, `sharp_action_detector.py`, `arbitrage_detector.py` |
| Celery tasks (user-defined) | 6 | `core/tasks.py:6094,6098,6102,6114,6122,6188` |
| Beat schedule entries | 2 confirmed | `core/celery.py:783` (`generate_daily_betting_brief` @ 07:00 MT) + `:788` (`collect_sports_odds_intelligence` @ 30-min) |
| Frontend route | 1 | `App.tsx:89` → `/betting` → `BettingPage.tsx` |
| Frontend tabs | 9 | `BettingPage.tsx:16-26` — Hub / Today's Games / Top Plays / Sharp Action / Arbitrage / Watching / Live Odds / My Wagers / Records |
| Discord commands | 2 | `core/services/discord_bot.py:1108` (`/odds`) + `:1404` (`/bankroll`) |
| Body-system integration | 0 | verified NONE in `core/services/heart.py`, `lungs.py`, `circulatory.py` |
| WebSocket channel (sports-scoped) | 1 | `/ws/dbao/` (per `tests/one-off/test_websockets.py:51` — realtime metrics namespace) |

**DBAO codename evidence (per D61):**

| Surface | Anchor | Interpretation |
|---|---|---|
| PostgreSQL schema | `docs/audit-2026/12-infrastructure.md:51` — multi-schema `studio, public, dbao, shared` | DBAO = separate PostgreSQL schema (not a mounted Django app) |
| WebSocket namespace | `tests/one-off/test_websockets.py:51` — `ws://localhost:8000/ws/dbao/` | DBAO = realtime metrics WebSocket namespace |
| Env-var namespace | `tests/frontend/test_all_fixed.html:101` — `VITE_DBAO_API_URL` | DBAO = frontend API prefix (test-only reference; not committed prod config) |
| HTTP client header | `tests/frontend/test_betting_api.html:81` — `X-DBAO-Client: Test-Client` | DBAO = HTTP client identification (test-only reference) |
| Django app label | NONE FOUND | DBAO is **NOT** a Django app (no `dbao/` folder, no `apps.py` entry) |
| Frontend route | NONE FOUND | DBAO is **NOT** an App.tsx route |
| Mounted URL prefix | NONE FOUND | DBAO is **NOT** a `/api/dbao/` prefix on `main` HEAD |

**Interpretation confirmed at D61:** DBAO = product-line codename
for the sports betting analytics ops product surface, materialized
as (a) a discrete PostgreSQL schema, (b) a WebSocket namespace for
realtime metrics, and (c) an implicit frontend/test-tooling
naming convention. NOT a mounted app or a first-class Django
service.

**Intelligence layer evidence:**

| Surface | Anchor | Sports-Scoped? |
|---|---|---|
| `intelligence/realtime_engine.py` | referenced from `intelligence/views.py:15` | Domain-agnostic (not sports-only) |
| `intelligence/revenue_tracking_bridge.py:29` | `RevenueRecord` model | Cross-domain (not sports-only) |
| `intelligence/views.py:44` | `'sports_intelligence': True` feature flag | Sports-scoped indicator (flag; not a distinct pipeline) |
| `core/tasks_financial.py:1815,1824` | `_impl_collect_sports_odds_intelligence` — posts to Discord `#market-intelligence` | Sports-scoped intelligence pipeline (thin — one function) |
| Learning bridge into Memory (S1300) | NONE FOUND | UNKNOWN — no explicit sports-signal → Memory arc bridge documented |
| Topic doc `docs/topics/sports*.md` | NONE FOUND | NONE (no `betting*.md`, `intelligence*.md`; only `stock-intelligence.md` exists which is non-sports scope) |

Interpretation: Intelligence is a domain-agnostic realtime engine
with a `sports_intelligence` feature flag hook + one concrete
sports-scoped Celery task path. NOT a distinct sports intelligence
pipeline — more accurately, "sports metadata routed through a
shared intelligence surface."

### 2.6 What this evidence tells us

Four load-bearing facts emerge:

1. **Sports surface is larger than S1273 §3.10 captured.** The
   LIGHT rating reflected S1273 sweep depth, not actual surface
   size. Real surface is 5 models across 2 files + 4 services +
   5 spiders + 4 market agents + 6 Celery tasks + 9-tab UI +
   discrete DB schema. Comparable magnitude to Group 1400
   Revenue's real surface after S1400 discovery.

2. **DBAO is a materialized codename with 4 concrete artifacts**
   (schema, WebSocket namespace, env-var namespace, HTTP header) —
   not just a naming convention. This gives Category F (below) a
   concrete anchor set.

3. **Intelligence is a shared surface with a thin sports
   integration.** One feature flag + one Celery task path is not a
   sports-specific intelligence pipeline. If Group 1500 treats it
   as one, we scope-drag stock/legislation/narrative intelligence
   in per Rigby's warning. D60 bounds this out.

4. **The Signal Engine integration gap is confirmed at the code
   level** (`sports_odds` not in `SignalCluster.pattern_type`).
   This is not speculative — it is a runtime constraint that
   Category F must confront in the posture-decision evidence
   plan.

---

## 3. Candidate subdomain taxonomy

Six subdomain categories are candidates for child audits under
Group 1500. Each row lists the primary systems in scope, the
inventory anchor, and drift already flagged. Rigby's D60 anti-
scope constraint (Intelligence bounded to sports-scope only) is
enforced in Categories D and F specifically.

### A — Odds Ingestion & Normalization

- **Systems:** `TheOddsSpider`
  (`ai_core/spiders/specialized/theodds_spider.py:33`),
  `KalshiSpider` (prediction markets;
  `ai_core/spiders/specialized/kalshi_spider.py:28`),
  `CombatSportsSpider`
  (`ai_core/spiders/specialized/combat_sports_spider.py:30`),
  `HorseRacingSpider`
  (`ai_core/spiders/specialized/horse_racing_spider.py:18`),
  `SportsDataSpider` (ESPN + The Odds API;
  `ai_core/spiders/sports_data_spider.py:18`), 3× SportsOddsSpider
  configurations in
  `ai_core/spiders/lightweight_spider_system.py:330-332`,
  `OddsSnapshot` model (`core/models_odds_history.py:15`),
  `GameLineHistory` model (`core/models_odds_history.py:82`),
  Celery tasks `collect_sports_odds`
  (`core/tasks.py:6094`), `collect_sports_odds_intelligence`
  (`core/tasks.py:6098`; beat @ 30-min via `core/celery.py:788`),
  `snapshot_odds_for_line_movement` (`core/tasks.py:6114`).
- **Anchor:** S1273 §3.10 primary surface; S1274 §14 Finding #6
  data-lineage side.
- **Known drift:** 5 spiders + 3 lightweight-system configurations
  overlap on odds retrieval; no unified normalization service
  identified in this sweep; `SpiderData.data_type='sports_odds'`
  used but not a valid `SignalCluster.pattern_type`.
- **Boundary:** ends at persisted odds data + line-movement
  history. Consumers (agents, predictions, betting content) are
  Categories B–D scope.

### B — Prediction / Analytics Agents

- **Systems:** `core/agents/markets/sports_odds_analyst.py`,
  `game_predictor.py`, `sharp_action_detector.py`,
  `arbitrage_detector.py`, plus `SportsBettingCoordinator`
  service (`core/services/sports_betting_coordinator.py:21`)
  which orchestrates the 4 agents + generates unified
  daily/nightly briefs.
- **Anchor:** S1273 §3.10 analytics layer; S1274 §14 Finding #6
  agent-consumer side.
- **Known drift:** all 4 agents filter `data_type == 'sports_odds'`
  from `SpiderData` (per Explore sweep) — direct-consume pattern,
  no intermediate signal aggregation surface; agent training
  pipelines (if any) not surfaced by this sweep; unknown whether
  agents write outputs to `MLPrediction` or hand off directly.
- **Boundary:** reads Category A data → produces predictions /
  arbitrage / sharp-action signals. Consumer of predictions
  (betting content, UI, wager tracking) is C, D, E scope.

### C — Wager Tracking & Outcome Verification

- **Systems:** `PlacedWager` model
  (`core/models_betting.py:13`), `PlacedWagerLeg` model
  (`core/models_betting.py:108`; multi-leg parlay support),
  `BettingStats` model (`core/models_betting.py:163`; W/L, ROI,
  streaks aggregated per user/sport), `BettingOutcomeVerifier`
  service (`core/services/betting_outcome_verifier.py:21`),
  Celery task `verify_betting_outcomes`
  (`core/tasks.py:6122`), Discord `/bankroll` command
  (`core/services/discord_bot.py:1404`).
- **Anchor:** S1273 §3.10 user-facing layer; connects to
  Category F posture-evidence path via `MLPrediction` /
  `BettingOutcomeVerifier` learning bridge question.
- **Known drift:** `BettingOutcomeVerifier` settles outcomes but
  the S1273 §3.10 flag notes outcomes do not feed initiatives or
  signal scoring — this is a load-bearing gap for the integration
  posture (Category F evidence).
- **Boundary:** user-side records of bets placed, outcome
  settlement against `OddsSnapshot`/API-confirmed scores, stats
  aggregation. Feedback into predictions / signals is out-of-scope
  here (Category F).

### D — Betting Content Pipeline

- **Systems:** `SportsContentContextBuilder`
  (`core/services/sports_content_context.py:27`), Celery task
  `generate_daily_betting_brief` (`core/tasks.py:6188`; beat @
  07:00 MT via `core/celery.py:783`), Celery task
  `daily_betting_digest` (`core/tasks.py:6102`), Discord `/odds`
  command (`core/services/discord_bot.py:1108`), sports-scoped
  intelligence hook `_impl_collect_sports_odds_intelligence`
  (`core/tasks_financial.py:1815,1824`) posting to Discord
  `#market-intelligence`.
- **Anchor:** S1273 §3.10 content-generation layer; connects to
  wider content-pipeline arc (Group 1600 if Chris opens it) via
  reader/writer contract.
- **Known drift:** `SportsContentContextBuilder` builds context
  from live odds + platform performance + value bets + analyst
  memory — but the consumer surface (blog vs Discord vs UI) and
  the delimiter between "content" and "brief" is not clearly
  captured in current docs; `generate_daily_betting_brief` has an
  MT-tz assumption embedded in its beat schedule that should be
  named in the audit.
- **Boundary:** sports data + platform performance → generated
  content (blog copy, Discord posts, briefs). Content pipeline
  arc dependencies (deliberation, PublishGate, etc.) are out of
  scope here (delegated to Group 1600 boundary). **Scope
  clarification (Rigby SIGN cycle 1 Q1 fold):** Category D
  covers sports *output surfaces* (brief / digest / Discord)
  specifically; the shared intelligence engine
  (`intelligence/realtime_engine.py`) remains out-of-scope per
  D60 — only the sports-scoped hook
  (`_impl_collect_sports_odds_intelligence` posting to Discord
  `#market-intelligence`) is in.

### E — Frontend Sports Surface

- **Systems:** `/betting` route (`frontend/src/App.tsx:89`),
  `BettingPage.tsx` 9-tab layout
  (`frontend/src/pages/BettingPage.tsx:16-26`) — Hub, Today's
  Games, Top Plays, Sharp Action, Arbitrage, Watching, Live Odds,
  My Wagers, Records — plus API integration to Categories A–D.
- **Anchor:** S1273 §3.10 UX layer; S1273 §12 frontend row (61
  routes autoblock counts `/betting` as 1 of 61 App.tsx routes).
- **Known drift:** no dedicated betting WebSocket channel found
  in this sweep (`/ws/dbao/` is a DBAO metrics channel, not tab-
  scoped realtime); tab-level realtime update behavior is
  unknown; interaction contract with Categories A/B/C not
  audited.
- **Boundary:** user-facing UI + interaction with wagers / odds /
  predictions. Backend surfaces are A/B/C/D scope; frontend
  system-wide UX conventions (workspace tabs, Command Center)
  are out of scope here.

### F — Cross-Domain Integration Lens & Posture Decision Framing

- **Systems:** DBAO product-line materialization surface
  (PostgreSQL `dbao` schema, `/ws/dbao/` WebSocket namespace,
  `VITE_DBAO_API_URL` env-var namespace, `X-DBAO-Client` header
  convention — per §2.5 evidence table),
  `intelligence/realtime_engine.py`, `intelligence/views.py:44`
  `sports_intelligence` feature flag,
  `_impl_collect_sports_odds_intelligence` Discord bridge,
  Signal Engine integration gap (`sports_odds` not a
  `SignalCluster.pattern_type` — S1274 §14 Finding #6), Memory
  Domain (S1300) learning-loop path (UNKNOWN — no bridge
  surfaced), `MLPrediction` / `BettingOutcomeVerifier` feedback
  gap.
- **Anchor:** S1273 §9 #4 (Sports/DBAO ↔ AI Studio Integration
  Sketch); S1274 §12.3 (Product/Architecture Decision Point P1);
  S1274 §14 Finding #6 (Signal/Content pipeline break).
- **Known drift:** THE load-bearing posture-decision surface for
  the arc. All prior findings converge here. This is the
  category that owns the posture-decision **evidence plan** owed
  to xx99 per D59.
- **Boundary:** cross-domain integration surfaces + posture-
  decision framing / evidence plan / criteria enumeration.
  **Explicitly not:** posture selection (Chris-gated per S1274
  §12.3, post-arc after xx99 evidence consolidation).

### Explicit non-candidates

The following surfaces are **not** Group 1500 scope even under
the parent shape:

- **Mobile-app / React-Native betting-app scope beyond FK
  boundaries** to core sports models. If mobile-app surfaces
  during Category E audit, it is FLAG only; deep audit is out of
  scope. Rationale: mobile-app is a separate deployment target
  with its own arc when Chris opens it.

- **Odds API vendor selection** (which of TheOddsAPI / Kalshi /
  ESPN / etc. is canonical). Product decision, not architecture.
  Vendor comparison research is not this arc's job.

- **Betting UX design or workflow proposals.** Category E audits
  the surface as it exists; design proposals for improving it
  belong to a post-arc design-preparation session.

- **Non-sports Intelligence** (stock intelligence, legislation
  intelligence, narrative intelligence). D60 bounds Intelligence
  to sports-scope only. If a child audit surfaces non-sports
  intelligence entanglement, FLAG for parked-candidate follow-on
  (parent arc for the shared intelligence surface).

- **BILLING_MONETIZATION_SYSTEM.md external companion project
  (ai-content-studio).** Treat as design context only, not as
  runtime surface. Matches S1400 anti-scope pattern.

- **Body-system integration.** Explore sweep confirms zero
  sports references in heart.py / lungs.py / circulatory.py.
  If the arc surfaces a body-system tie in a future audit, it
  is a FLAG for follow-on; the parent excludes it from candidate
  categories.

- **General signal aggregation / SignalCluster refactoring**
  beyond documenting the `sports_odds` gap. If Category F
  evidence surfaces need for `SignalCluster.pattern_type`
  expansion, it is a **finding + recommendation** for xx99, not
  an implementation proposal.

- **General learning-loop / Memory Domain refactoring** beyond
  documenting whether/where sports signals should feed the
  Memory arc. Delegates to S1300.

---

## 4. Parent-vs-single recommendation

**Verdict: parent-with-children (D57 Chris-locked 2026-07-01).**

Evidence for parent-with-children:

1. **Surface size.** 5 models across 2 files + 4 services + 5
   spiders + 4 market agents + 6 Celery tasks + 9-tab UI +
   discrete PostgreSQL schema + WebSocket namespace. Comparable
   to Group 1400 Revenue's real surface after S1400 discovery.
   No single audit session can cover this at fidelity.

2. **Multiple S1273 rows implied.** S1273 §3.10 is the primary
   row but S1273 §9 #4 (Sports/DBAO ↔ AI Studio Integration
   Sketch as mission #4) and S1274 §12.3 (P1 decision point)
   both name the same domain from different angles. Playbook §8
   "when to skip parent" rule 1 fails (`Domain maps to exactly
   one S1273 §3.N row`).

3. **Cross-domain lens is central.** Category F is not
   optional — it is the load-bearing posture-decision surface
   named by two prior research artifacts. Playbook §8 "single
   audit" rule 3 fails (`All 28 audit questions can be answered
   from one evidence sweep`) because the posture question
   requires evidence from Categories A/B/C/D/E to synthesize.
   **Specifically, the posture-decision brief cannot exist
   without: Category A normalization realities (does the odds
   ingestion path already assume island-shape schemas or is it
   integration-ready?); Category B agent output surfaces (do
   the 4 market agents write to shared `MLPrediction` /
   `SignalCluster` surfaces or private tables?); Category C
   outcome→feedback loop (does `BettingOutcomeVerifier` route
   outcomes back to `MLPrediction` / signals or does the loop
   terminate at wager settlement?); Category D content-vs-
   intelligence delimiter (are sports briefs consumed by
   mainline content pipeline or Discord-only?); Category E
   frontend WebSocket topology (is `/ws/dbao/` sports-only or
   shared with mainline realtime?).** Each of these is a Chris-
   gated success-criterion input; none of them can be
   synthesized from a single audit sweep. Rigby SIGN cycle 1 Q2
   fold.

4. **Multi-noun label with materialized codename.** Playbook §22
   heuristic: three coordinated nouns predicts parent shape.
   Groups 1300 and 1400 both confirmed. DBAO is not a rhetorical
   codename — it is materialized as 4 concrete artifacts
   (schema, WebSocket, env-var, header), giving Category F a
   real scope surface.

Evidence against parent-with-children (considered and rejected):

- **Body-system linkage is zero.** Sports could be argued as an
  "isolated island" that a single audit can capture. Rejected
  because the island-ness is itself the load-bearing question —
  Category F cannot presume its answer; it must gather evidence
  to frame the posture decision.

- **`docs/topics/` has no sports/betting doc.** Could argue this
  makes Sports "greenfield-ish" — one comprehensive audit could
  produce the missing topic doc. Rejected because the runtime
  surface is not greenfield: it is 5 models + 4 services + 5
  spiders + 4 agents + 6 Celery tasks + 9-tab UI + DBAO schema
  in production today. The absence of a topic doc reflects
  documentation drift, not runtime absence.

**Parent-with-children shape adopted.** Child mission sequence
locked at §5.

---

## 5. Child mission sequence (Chris-locked 2026-07-01 via D57 arc-shape verdict)

| Slot | Planned session | Child title | Category | Priority rationale |
|---|---|---|---|---|
| P1 | S1501 | Sports Odds Ingestion & Normalization Audit | A | Foundation — no downstream audit is grounded without knowing what data lands and how it is normalized. Spider surface = 5 spiders + 3 lightweight configs; two persistence models. |
| P2 | S1502 | Sports Prediction & Analytics Agents Audit | B | Depends on P1 data surface. 4 market agents + coordinator service. Direct-consume pattern from `SpiderData` is a load-bearing observation for Category F posture evidence. |
| P3 | S1503 | Wager Tracking & Outcome Verification Audit | C | Parallel-safe with P1/P2 (user-facing surface). Includes the `BettingOutcomeVerifier` outcome→feedback gap flag that feeds Category F evidence. |
| P4 | S1504 | Sports Betting Content Pipeline Audit | D | Depends on P1+P2+P3 data + prediction surfaces. Betting brief + digest generation + Discord `/odds` + intelligence bridge. Constrains Category F content-integration posture criteria. |
| P5 | S1505 | Sports Frontend Surface Audit | E | Consumes P1/P2/P3/P4 outputs. 9-tab BettingPage audit + realtime channel investigation + interaction contract with backend surfaces. |
| P6 | S1506 | Cross-Domain Integration Lens & Posture Decision Framing Audit | F | Load-bearing lens; runs LAST because it consumes P1–P5 findings to build the posture-decision evidence plan owed to xx99 per D59. |
| P7 | S1599 | **xx99 canonical summary** | — | Consumes P1–P6 outputs + resolves contradictions + produces the Chris-gated posture-decision brief (evidence-consolidation, NOT posture selection per D59). Applies playbook §11.3 §10 meta-methodology (third application after S1399 + S1499). |

**Ordering rationale.** Foundation → consumers → integration lens.
Category A (data ingestion) is the necessary foundation for every
downstream audit. B and C are largely parallel-safe (B is analytics
consumer, C is user-facing consumer). D depends on A+B+C data
surfaces. E depends on A–D backend surfaces. F runs last because
it consumes A–E findings to frame the posture-decision evidence
plan — running F earlier would either invent evidence or defer
the framing to xx99 (both anti-patterns).

**Sibling-inheritance rule** (per playbook §9 anti-duplication):
if P2 already inventoried `SpiderData.data_type='sports_odds'`
under agent-consumer lens, P3 cites P2's inventory rather than
restating. xx99 (S1599) reconciles child-level disagreements per
§11.3 template.

**Anti-scope for §5 sequence itself.** Do NOT parallelize P1 and
P2 speculatively; P2 needs P1's data-surface inventory as
citation source. Chris can revisit sequence at any child's open
if evidence warrants a swap.

**Pre-brief artifact for posture-decision criteria consistency
(Rigby SIGN cycle 1 Q3 fold).** Because Category F (P6) runs
LAST and consumes P1–P5 evidence for the posture-decision
brief, there is a real risk that P1–P5 children collect
posture-relevant evidence in inconsistent shapes (schema drift
between siblings), forcing xx99 (S1599) to renormalize before
consolidating. To prevent this: **at P1 open, child authors
must capture posture-relevant evidence using a shared mini-
schema — for each surface inventoried (model / service /
spider / agent / task / UI / WebSocket / schema), note (a)
whether the surface is sports-only or shared with mainline,
(b) whether it writes to sports-owned tables (DBAO schema) or
mainline tables (public schema), (c) whether integration
posture would require refactoring the surface or only extending
it, (d) whether island posture would require additional
isolation guarantees (own queue / auth / observability).** This
mini-schema is consumed by P6 F for evidence-plan drafting;
xx99 consolidates. Cost: 4-item annotation per surface per
child audit — bounded work. Chris ratifies at P1 open if fold
should propagate to P1–P5 upfront or if P6 F extracts
retroactively.

---

## 6. Parked candidate issues

Issues surfaced during Phase 0 that are NOT resolved here — parked
for the appropriate child audit or xx99 to address:

- **P1 (Category A) parked:** unified odds normalization service —
  does one exist as a canonical surface consuming all 5 spiders,
  or does each spider write its own `SpiderData` rows with
  `sports_odds` classification? Evidence at Phase 0 does not
  distinguish. Owed to P1.

- **P1/P2 parked:** whether agents (`sports_odds_analyst`,
  `game_predictor`, etc.) write to `MLPrediction` or hand off
  directly to `SportsBettingCoordinator`. Direct-consume pattern
  observed via `filter data_type == 'sports_odds'` but write
  surface not inventoried. Owed to P2.

- **P3 parked:** `BettingOutcomeVerifier` → `MLPrediction`
  feedback path — does outcome data flow back to the prediction
  agents for learning? Load-bearing for Category F integration
  posture. Owed to P3.

- **P4 parked:** `generate_daily_betting_brief` MT-tz beat
  assumption — audit whether MT is deliberate (user is in MT tz)
  or historical drift. Owed to P4.

- **P4/P5 parked:** the `docs/topics/sports*.md` / `betting*.md`
  gap — xx99 recommends creating a canonical topic doc, but
  content sourcing (from P4 + P5 audits) is the input. Owed to
  xx99 with P4/P5 as evidence sources.

- **P5 parked:** BettingPage 9-tab realtime channel — is any tab
  fed by WebSocket, and if not, is polling the intent or is a
  channel missing? Owed to P5.

- **P6 parked (load-bearing):** Signal Engine `sports_odds` gap
  (S1274 §14 Finding #6) — Category F evidence gathers what an
  integration posture would require (adding `sports_odds` as a
  `SignalCluster.pattern_type` or adopting an intermediate
  aggregation surface). xx99 consolidates into the Chris-gated
  posture brief.

- **P6 parked:** Memory Domain (S1300) learning-loop path — is
  there a bridge that routes sports outcomes into `AgentMemory`
  or `AgentKnowledgeSource`? UNKNOWN at Phase 0. Category F
  investigates for the integration posture evidence + delegates
  to S1300 if a design-preparation follow-on is warranted.

- **P6 parked:** `MLPrediction` / prediction-vs-outcome delta as
  a signal source. If integration posture is picked, this is a
  candidate `SignalCluster` input. Category F frames the
  criterion.

- **xx99 parked:** DBAO codename shape — is DBAO a product-line
  codename intended to become its own mounted app / URL prefix
  / Django app label at some future point, or is it a permanent
  materialization at the schema+WebSocket level? Chris-lock
  candidate for post-arc T-slot.

- **P6 parked (Rigby SIGN cycle 1 Q4 fold — reassigned from
  xx99):** whether the `sports_intelligence: True` feature flag
  in `intelligence/views.py:44` should be documented in
  `docs/topics/` as a first-class capability or is transitional.
  **Owned by P6 investigation; escalated to xx99 for
  documentation-anchor recommendation** (P6 does the
  investigation, xx99 lands the topic-doc recommendation).
  Rationale: the flag lives in the cross-domain integration
  lens boundary Category F already owns; xx99 is the wrong
  layer to investigate a code-level feature flag.

- **Delegated to S1300:** if Category F evidence surfaces need
  for a sports→Memory arc learning bridge, that design work
  belongs to Group 1300 follow-on (post-S1399 xx99), not
  Group 1500. S1500 xx99 flags + delegates.

- **Delegated to Group 1600 (Content / Deliverables /
  Publishing, if Chris opens it):** if Category D audit surfaces
  a canonical delimiter between betting content vs betting brief
  vs Discord digest, the reconciliation is content-pipeline
  scope, not sports scope. S1500 xx99 flags + delegates.

---

## 7. Anti-scope

Beyond §3 explicit non-candidates and §6 parked items, the
following are hard exclusions from Group 1500 under any child
audit:

1. **Implementation work.** No PRs, no migrations, no runtime
   code changes. Playbook §21 STAGE 0 rule.

2. **Posture selection.** Chris gates the integration-vs-island
   selection per S1274 §12.3 + D59. Group 1500 arc ends at
   evidence-consolidation brief; the ADR that picks the posture
   is a post-arc artifact.

3. **Design proposals for how Sports should work.** Parent doc
   authority is `parent-doc`, not `design-preparation`. Children
   audit; xx99 synthesizes; ADR (post-arc) designs.

4. **Cross-domain audits of non-sports surfaces.** Even if a
   category audit surfaces a non-sports drift observation, the
   sweep stops at "flag + delegate to relevant arc." Do not
   re-audit S1300 (Memory), Group 1400 (Revenue), Signal Engine,
   PublishGate, etc.

5. **Odds API vendor evaluation.** Product decision, not
   architecture.

6. **Deep audit of mobile-app / React-Native betting app.**
   FK-boundary reference only; no per-screen audit.

7. **Non-sports intelligence surface.** D60 bounds Intelligence
   to sports-scope only. If shared intelligence surface entangles
   sports with stock/legislation/narrative, FLAG only.

8. **Runtime primitives research** (Ops Autopilot, MissionRunner
   internals, etc.). Delegated to Groups 1900+ if Chris opens
   them.

9. **Bankroll / staking strategy optimization research** (Rigby
   SIGN cycle 1 Q5 fold). Any research into optimal wager
   sizing, Kelly criterion tuning, bankroll-management
   strategy, or ROI-maximization algorithms. Common Sports
   scope-trap: this creeps in as "analytics" but is product /
   quantitative-strategy work, not architecture scoping.
   Category B may inventory whether such logic exists at code
   level (as a surface fact), but any deeper research on WHAT
   the strategy should BE is out of scope for Group 1500.

---

## 8. Decisions recorded (Chris-locked 2026-07-01)

Single "agree all + D-6=(a)" ratification round via governance
decision `81d7467e-add6-420f-aee9-60b67d7867e8` (action `approve` /
status `acted`). All six verdicts land 2026-07-01. Numbering
continues from S1499 D55 sequence per playbook §16.

| ID | Verdict | Wording |
|---|---|---|
| D56 | Domain slug | `sports` (folder: `docs/research/domains/sports/`) |
| D57 | Arc shape | Parent-with-children (child sequence P1–P6 + xx99 P7 per §5) |
| D58 | Phase 0 methodology | F.i / F.ii / F.iii applied UNCHANGED — preserves v3 promotion trigger integrity per S1400 D29 two-triggers rule (Rigby caution 1 folded) |
| D59 | Load-bearing question | Taxonomy + **posture decision framing + evidence plan** (NOT posture recommendation at Phase 0; Rigby refinement folded from pre-ratification pressure-test) |
| D60 | Anti-scope | As §7 proposed; Intelligence bounded to sports-scope only (no stock/legislation/narrative scope-drag per Rigby scope-magnet warning) |
| D61 | DBAO definition | Option (a) — "Donkey Betz Analytics Ops" product-line codename |

**Provenance trail:** governance_tool `decision_create` action id
`81d7467e-add6-420f-aee9-60b67d7867e8` (title: "Group 1500 Phase 0
(Sports/DBAO/Intelligence) — Chris ratification D-1..D-6",
urgency: high) → governance_tool `decision_decide` action
(decision: approve, new_status: acted).

**Delegation record:** Category F may FLAG delegation to Group
1300 Memory arc for learning-loop path research; xx99 owns the
formal delegation cross-link. No mid-arc delegation decisions
required.

---

## 9. Next step

**Recommended P1 open:** `Continue research group 1500: Category
A — Sports Odds Ingestion & Normalization`. First child audit.

Session flow at P1 open:

1. Load this parent doc as parent context.
2. Read playbook §9 (28 canonical questions) + §11.2 (child
   audit 20-section template).
3. Launch 6 parallel Explore sub-agents per §13 evidence sweep
   for Category A scope only.
4. Synthesize per §11.2 template. Answer all 28 canonical
   questions (§9) — cite, reference, or `UNKNOWN`.
5. Route to Rigby per §15 (fresh SIGN isolation pin; D48
   preemptive stability-probe gate per S1405+S1406+S1499
   3-arc-confirmed pattern; titles-only batched SIGN 2-3
   findings per prompt for large audits).
6. Fold SIGN-with-edits into P1 doc.
7. Return summary to Chris per playbook §24.

**Parallel option (evidence permits):** if Chris prefers to
open Category B in parallel session to P1 (playbook §22 permits
label-independence but this arc's §5.5 sibling-inheritance rule
recommends sequential P1→P2), decision is Chris's.

**Not next:** Category F (P6). It runs LAST per §5 ordering
rationale.

---

## 10. Phase 0 F.i — Domain Definition (Chris methodology second application 2026-07-01)

Chris's Phase 0 3-step framework (Chris-directed at S1400,
D29-locked as playbook v3 §11.1 promotion candidate on the
two-triggers rule) applied here for the second time. Per D58,
methodology applied with **unchanged sectional structure and
intent** — domain-specific content differs as expected (Sports
substance is not Revenue substance), but the F.i / F.ii / F.iii
scaffold, question counts, and deliverable shapes match the
S1400 first application exactly — so that Group 1500 counts as
a clean second application per the two-triggers rule. Wording
refined per Rigby SIGN cycle 1 Q6 fold to protect the v3
promotion trigger claim from strict-reader interpretation that
"no additions, no refinements" would over-constrain (domain-
adaptation is expected; structural preservation is what
counts). If S1500 xx99 closes with the methodology unchanged
in structure/intent AND having produced discriminative-value
evidence per §12.4 criterion (stricter than "ran twice";
Rigby caution 1), promotion to playbook v3 §11.1 template
becomes trigger-eligible.

**F.i answers "What IS this domain?"** — a single-sentence
definition that any future reader can pin to, plus the boundary
conditions that determine what's in vs out.

### 10.1 Domain definition (Chris-lockable)

**Sports (Group 1500) is the platform's betting-analytics
product-line — the set of runtime surfaces that ingest sports
odds and outcomes, run predictions and arbitrage / sharp-action
analytics against them, track user wagers and their settlement,
generate sports betting content (briefs / digests / Discord
posts), and expose the results through a 9-tab betting dashboard
— materialized under the DBAO product-line codename (D61) as a
discrete PostgreSQL schema + realtime WebSocket namespace.**

Boundary conditions:

- **IN scope:** the 5 models + 4 services + 5 spiders + 4 market
  agents + 6 Celery tasks + 9-tab UI + DBAO schema + `/ws/dbao/`
  channel + 2 Discord commands + `sports_intelligence` feature
  flag + sports-scoped intelligence Celery task per §2.5
  evidence table.

- **OUT of scope:** everything §3 non-candidates + §7 anti-scope
  names. Special emphasis: non-sports intelligence surface
  (D60), Odds API vendor selection, posture selection (D59),
  mobile-app deep audit.

- **Boundary conditions requiring evidence to sharpen (owed to
  children):** whether the intelligence surface (`realtime_engine`
  + `sports_intelligence` flag) sits INSIDE or OUTSIDE the
  Sports domain proper — Phase 0 places it inside (Category F
  scope + D60 bounding) but Category F evidence may re-argue.

### 10.2 Runtime shape confirmation

The domain definition above is grounded in verified evidence
(§2.5). Two facts that pin it:

1. **Sports has its own PostgreSQL schema (`dbao`).** No other
   platform domain has this pattern per current audit-2026
   evidence (`docs/audit-2026/12-infrastructure.md:51` lists
   `studio, public, dbao, shared` as the four schemas). This is
   architectural isolation at the storage layer.

2. **Sports has its own WebSocket namespace (`/ws/dbao/`).**
   Verified via `tests/one-off/test_websockets.py:51`. No other
   platform domain has a same-shape dedicated namespace per
   this sweep.

Together these two facts materialize DBAO as more than a
codename — they make Sports architecturally distinct at the
storage + realtime layer. This is the first-order **evidence of
partial architectural isolation** at the runtime level (Rigby
SIGN cycle 1 Q10 fold — softened from "island posture already
partially adopted" to avoid over-reading two artifacts as a
whole-posture claim; storage + realtime isolation is confirmed
but deploy / queue / service / auth boundary isolation remains
Category F evidence). Category F posture-decision evidence plan
(§12) must confront this asymmetry: an integration posture asks
"should the storage/realtime isolation be relaxed?"; an island
posture asks "should the isolation be formalized and extended
across deploy / queue / service / auth layers as well?"

### 10.3 What F.i does NOT try to answer

- **Whether island or integration posture is correct.** D59
  routes this to xx99 evidence-plan owed to Chris, not to Phase
  0 recommendation.

- **Whether DBAO should become a mounted Django app.** Parked to
  §6 xx99-slot.

- **How the shared intelligence surface interacts with
  domain-specific intelligence.** Bounded out by D60; delegated
  to a shared-intelligence parent arc if Chris opens one.

- **Whether the 5-spider ingestion path should be consolidated
  into fewer spiders or a unified normalization service.**
  Product/architecture decision, not F.i scope.

---

## 11. Phase 0 F.ii — Existing Knowledge Inventory (Chris methodology second application 2026-07-01)

**F.ii answers "What do we already know about this domain?"** —
the inventory of prior research findings + docs + runtime
evidence + anchor-referenced facts that a fresh reader inherits.

### 11.1 Prior research findings already assigned to Sports

| Finding | Source | Assignment to child |
|---|---|---|
| Sports pipeline break — `sports_odds` not a valid `SignalCluster` data_type (HIGH) | S1274 §14 Finding #6 | Category F (evidence + criterion for integration posture) |
| Sports/DBAO ↔ AI Studio Integration Sketch as P1 mission #4 | S1273 §9 #4 | Category F (posture decision framing) |
| Sports/DBAO ↔ AI Studio Product/Architecture Decision Point (P1) with two-posture success criteria | S1274 §12.3 | Category F (evidence plan owed to xx99) |
| Sports Intelligence / Betting Pipeline row LIGHT coverage | S1273 §3.10 | All children (LIGHT rating is why the arc exists) |
| DBAO product-line codename D61 | S1500 D61 (this doc) | Category F (materialization evidence) |
| Zero body-system integration | S1500 §2.5 (this doc) | Categories A–E (framing constraint) |

### 11.2 Docs corpus state (S1500 open snapshot)

| Doc slot | Status |
|---|---|
| `docs/topics/sports*.md` | DOES NOT EXIST |
| `docs/topics/betting*.md` | DOES NOT EXIST |
| `docs/topics/intelligence*.md` | DOES NOT EXIST |
| `docs/topics/stock-intelligence.md` | EXISTS (non-sports scope) |
| `docs/PLATFORM_INVENTORY.md` §26 SignalCluster pattern types | 10 types listed; `sports_odds` NOT among them (confirms S1274 §14 Finding #6) |
| `docs/PLATFORM_INVENTORY.md` §12 Frontend | `/betting` route counted as 1 of 61 App.tsx routes; 9-tab BettingPage referenced |
| `docs/audit-2026/12-infrastructure.md:51` | Documents the `dbao` schema as part of multi-schema PostgreSQL setup |
| `docs/research/ARCHITECTURE_INDEX.md §5.14` | Sports / DBAO ↔ AI Studio Integration Sketch entry references P1 research doc + operationally-separate DBAO stack |

**Documentation gap.** Sports lacks a canonical topic doc despite
having a real runtime surface. xx99 recommendation candidate:
create `docs/topics/sports-betting.md` after P4/P5 land.

### 11.3 Runtime evidence anchors already captured (this doc §2.5)

The §2.5 evidence tables are the F.ii inventory. Every category
audit inherits them as the baseline; children add depth via
28-question sweeps.

**Rule:** if a child audit disagrees with a §2.5 entry, the
child's finding wins (child sweeps are deeper); xx99 reconciles.
§2.5 is scoping evidence, not audit evidence.

### 11.4 What F.ii does NOT try to answer

- **Any of the 28 canonical questions in depth.** Child scope.

- **The maturity classification (STABLE / PARTIAL / EXPERIMENTAL)
  per subdomain.** Child scope; xx99 consolidates.

- **The complete integration surface graph.** Only the load-
  bearing points captured; children extend.

- **Any drift comparison against `PLATFORM_WHAT_IT_IS.md`
  narrative.** Deferred to xx99 §7 anchor-update recommendations.

---

## 12. Phase 0 F.iii — Success Criteria (Chris methodology second application 2026-07-01)

**F.iii answers "What does 'the arc closed cleanly' look like?"** —
the concrete deliverables and quality bars that xx99 must produce
before Chris ratifies arc closure per playbook §17.

Per D59 (Rigby-refined), Group 1500 F.iii differs from Group 1400
F.iii in one specific way: **xx99 owes evidence-consolidated
posture-decision framing + Chris-gated decision brief, NOT
posture recommendation**. The rest of the F.iii shape matches
S1400.

### 12.1 Arc-close deliverables (owed to xx99 canonical summary)

1. **All 6 child audits closed** with playbook §11.2 20-section
   template + all 28 canonical questions answered (cite,
   reference, or `UNKNOWN`) + Rigby SIGN-with-edits folded.

2. **Cross-cutting patterns identified** per playbook §11.3 §5 —
   findings that recur across ≥2 children with severity flag
   (e.g., a provenance-stamping gap surfacing in P1 + P4).

3. **xx99 §5 posture-decision evidence brief** — the load-bearing
   deliverable per D59. Structure:
   - Integration posture success criteria (from S1274 §12.3
     baseline + P1–P6 evidence). Concrete list.
   - Island posture success criteria (from S1274 §12.3 baseline +
     P1–P6 evidence). Concrete list.
   - Evidence FOR each posture drawn from child audits (cite
     P1–P6 §N.M per criterion).
   - Evidence AGAINST each posture drawn from child audits.
   - Operational cost estimate for each posture (rough — P1 vs
     P0 grade acceptable; refine post-arc).
   - Failure-modes-if-criteria-not-met table per posture.
   - **Explicit "Chris-gated selection" tag** on the brief —
     xx99 does NOT pick.

4. **Consolidated domain shape map** per playbook §11.3 §2 —
   single map covering all six categories + DBAO materialization
   surface + intelligence-flag boundary.

5. **Resolved contradictions** per playbook §11.3 §3 — where P1
   and P2 disagreed (or P4 and P5, etc.), the canonical answer +
   rationale.

6. **Anchor-update recommendations** per playbook §11.3 §5:
   - Concrete edits to `PLATFORM_INVENTORY.md` §3.10 (subdivide
     if warranted; refine LIGHT rating).
   - Concrete edits to `PLATFORM_WHAT_IT_IS.md` (Sports narrative
     addition if the arc reveals a canonical framing).
   - Concrete `docs/topics/sports-betting.md` proposal.
   - `ARCHITECTURE_INDEX.md` §1.N registrations for each child +
     xx99 + §3 domain map + §5 gap + §7 decision matrix + §8
     timeline + §9 roadmap.

7. **Follow-on research queue** per playbook §11.3 §7 — post-arc
   T1–T10 unified tier structure (matching S1499 T1–T10 shape).
   Categories:
   - **T1 (highest):** post-arc ADR for posture selection (Chris-
     gated), any P1-critical umbrella ADRs.
   - **T2:** design-preparation follow-ons (posture-tied).
   - **T3:** Employee OS follow-ons if the arc surfaces
     runtime-owner questions (D55-analog).
   - **T4:** cleanup PRs from F1 / F4-CANDIDATE observations.
   - **T5:** optional / low-priority.

8. **Cross-arc delegation cross-links** to S1300 (Memory —
   learning-loop path) + Group 1600 (Content — if opened).

9. **Change log of the arc** per playbook §11.3 §8 — which
   children shipped, in what order, what Rigby SIGN verdict,
   what edits folded.

10. **Playbook §11.3 §10 meta-methodology section** — third
    application of the "What This Research Taught Us About How
    to Do Research" template (after S1399 first, S1499 second).
    Per Chris directive S1399 close 2026-07-01, every xx99
    carries this section. Content: 10.1 what worked, 10.2
    codify-to-playbook-v3 candidates (with §20 two-triggers
    threshold check), 10.3 anti-patterns to avoid, 10.4
    playbook itself suggestions, 10.5 xx99 template
    suggestions (optional).

### 12.2 Quality bars (xx99 clean-close criteria)

Per playbook §17 graduation criteria + Group 1400 arc-close
precedent:

- **No child audit ships with `UNKNOWN` on a load-bearing 28-Q
  question without a Rigby cycle.** Cheap `UNKNOWN` is allowed
  per §14 (edge cases); load-bearing `UNKNOWN` must be
  Rigby-pressure-tested.

- **All Rigby SIGN cycles folded.** No FLAG-EDIT or must-fix
  outstanding at xx99 open.

- **Zero merge-blocking drift** in autoblock-refreshed anchors
  after S1599 PR merge.

- **Docs cascade complete** per `feedback_docs_cascade_at_every_
  close.md` (build_docs_index → build_rag_corpus →
  sync_docs_index_to_documents → embed_documents --all-unembedded +
  build_docs_provenance).

- **xx99 §5 posture-decision brief has explicit "Chris-gated
  selection" tag.** No posture recommendation smuggled in via
  hedged phrasing.

- **Playbook v3 §11.1 template promotion decision (D29 trigger 2
  check).** If methodology applied unchanged AND arc closed
  clean AND artifact prevented confusion / reduced rework, xx99
  §10.2 flags v3 §11.1 template addition as ready for playbook
  v3 promotion session.

### 12.3 Rigby caution folds (from pre-ratification pressure-test)

Rigby's cycle-1 cautions folded here:

- **Caution 1 (repeatability + discriminative value for
  promotion):** xx99 §10.2 must explicitly demonstrate that the
  Phase 0 F.i/F.ii/F.iii methodology *produced discriminative
  value* — i.e., prevented a scope confusion / reduced rework /
  produced a cleaner close than a mechanical single audit would
  have. §12.4 defines what "discriminative value" looks like
  concrete for this arc.

- **Caution 2 (not over-loading Phase 0 with posture selection):**
  D59 folded. Phase 0 frames the posture question and specifies
  the evidence plan; children gather the evidence; xx99
  consolidates; Chris picks in a post-arc ADR.

- **Caution 3 (Intelligence scope-magnet):** D60 folded.
  Non-sports intelligence bounded out throughout §3, §6, §7,
  §10.1.

### 12.4 Discriminative-value criterion for playbook v3 §11.1 promotion

Per Rigby caution 1, xx99 §10.2 must present concrete evidence
that the F.i/F.ii/F.iii methodology produced discriminative
value for Group 1500. Candidate evidence types:

- **Scope confusion prevented.** Evidence: Phase 0 §3
  non-candidates + §7 anti-scope caught a category that a
  mechanical single-audit shape would have merged into scope
  (e.g., non-sports intelligence per D60; Odds API vendor
  selection per §7).

- **Rework reduced.** Evidence: Phase 0 §11.4 F.ii "what F.ii
  does NOT try to answer" prevented a child from re-inventorying
  a surface xx99 would have to consolidate anyway.

- **Cleaner arc close.** Evidence: Phase 0 §12 F.iii success
  criteria matched what xx99 actually produced without post-hoc
  criteria adjustment.

- **Chris-lock efficiency.** Evidence: single "agree all + D-6"
  ratification round versus multi-round negotiation. S1500 hit
  this bar (§8).

If xx99 §10.2 cannot demonstrate at least 3 of these 4 evidence
types concretely, **including at least one of (Scope confusion
prevented) OR (Cleaner arc close)** (Rigby SIGN cycle 1 Q7
fold — prevents promotion passing on softer points alone),
promotion should NOT trigger even if methodology was applied
unchanged. This bar is stricter than "it ran twice" — matches
Rigby caution 1 fold plus Q7 loophole closure.

### 12.5 Group-1500-specific F.iii artifact requirement

Per playbook precedent (S1400 §12.5 established this pattern),
Group 1500 F.iii carries one arc-specific concrete deliverable:

**§12.5 artifact: Sports Domain Lifecycle Traceability Table.**
xx99 produces a single-row-per-lifecycle-stage table showing:
odds ingestion → **fixture / entity identity resolution** (team
↔ league ↔ event IDs, start-time / timezone canonicalization,
"same game" deduplication — added per Rigby SIGN cycle 1 Q8
fold; common silent-failure surface in sports stacks between
ingestion and normalization; may resolve to UNKNOWN if children
don't surface a dedicated resolution layer) → normalization →
prediction → user wager → outcome verification → learning-loop
feedback → signal aggregation gap. For each stage: current
owner (agent/service/model), file:line anchor, integration-
posture requirement, island-posture requirement, evidence
citation from P1–P6 audits.

This table is the concrete artifact that makes the posture-
decision brief legible to Chris in one view. Rigby cycle 2 at
S1400 established the pattern (S1400 §12.5 Revenue Lifecycle
Traceability Table); Group 1500 replicates for Sports.

### 12.6 What F.iii does NOT try to answer

- **Whether the arc will close cleanly.** F.iii sets the bar;
  execution against the bar is child + xx99 scope.

- **Whether posture will resolve to integration or island.**
  D59 routes to Chris post-arc.

- **Whether playbook v3 §11.1 promotion actually triggers.** xx99
  §10.2 makes the call using §12.4 criterion; playbook v3
  promotion session ratifies.

---

## Appendix — Frontmatter provenance

**Source-of-truth chain for this doc.**

- **Playbook §11.1 template applied verbatim.** Sections §1–§9
  match template exactly (with §5 renamed "Child mission
  sequence" per S1400 precedent). §10–§12 additions per Chris's
  Phase 0 F.i/F.ii/F.iii methodology directive (S1400 D29;
  Group 1500 D58 applies UNCHANGED for two-triggers rule).

- **Ratified decisions D56–D61.** Governance decision
  `81d7467e-add6-420f-aee9-60b67d7867e8` — `decision_create`
  action + `decision_decide` action (approve → status acted) via
  Rigby PA tool surface on fresh S1500 arc pin
  `pa-791b3db549a64e54` (minted this session via
  `session_tool.create_fresh`). Retired Group 1400 arc pin
  `pa-34d43795e1b24bd3` updated at `tools/pa_local.sh:128`.

- **Runtime evidence sources.** All §2.5 evidence table entries
  verified against `main` HEAD f7704586 via two parallel Explore
  sub-agent sweeps executed at S1500 open (sports subsystem
  inventory + DBAO/intelligence inventory). Every file:line cite
  survives a repeat grep at commit time.

- **Rigby pre-ratification pressure-test folded.** 4 refinements
  landed:
  1. D-4 wording refined from "posture recommendation as
     explicit deliverable" to "posture decision framing +
     evidence plan" (D59 final).
  2. Rigby caution 1 (repeatability + discriminative value)
     folded into §12.4 explicit criterion.
  3. Rigby caution 2 (over-loading Phase 0) folded into D59 +
     §12.6 boundary.
  4. Rigby caution 3 (Intelligence scope-magnet) folded into
     D60 + §3 non-candidates + §7 anti-scope + §10.1 boundary.

- **Companion anchors.** Frontmatter lists 5 anchors per playbook
  §23 anchor discipline rule.

- **Verifier loop.** `pending-SIGN` — fresh isolation pin owed
  after this doc lands + Rigby pre-SIGN pressure-test round.

- **Path B chosen at session open.** Chris typed "start research
  group 1500" per 00-START-NEXT-SESSION.md line 69 Path B.
  Confirmed at S1500 open with heads-up note: parallel Claude
  Code session at earlier attempt was cleanly aborted before
  landing partial 1500 doc; S1500 has sole focus per memory rule
  `feedback_no_parallel_research_arcs.md`.

**Session count.** S1500 handoff numbering aligns with Chris's
arc-numbering convention: S1500 (arc open) → S1501–S1506 (P1–P6
children) → S1599 (xx99 canonical summary). S1507–S1598 skipped
by intent per arc-numbering discipline.

---

**End of S1500 parent scoping doc.** Session close artifacts:
this doc + `OPEN_ARCS.md` Group 1500 row (In-progress) +
`ARCHITECTURE_INDEX.md` §1.N + §8 timeline row + version bump
preamble + handoff `SESSION_1500_SPORTS_ARC_OPEN.md`.
