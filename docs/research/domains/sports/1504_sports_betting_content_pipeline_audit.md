---
title: "Category D — Sports Betting Content Pipeline Audit"
slug: 1504_sports_betting_content_pipeline_audit
domain: sports
subdomain_category: D
category: child_audit
authority: child-audit for Category D per Group 1500 parent §5 mission sequence P4 slot + fourth sibling to apply the pre-brief mini-schema per D62 = (a) propagate upfront
status: active
generated: 2026-07-02
session: 1504
arc: Research Group 1500 (Sports / DBAO / Intelligence)
parent_doc: 1500_sports_domain_scoping.md
sibling_docs:
  - 1501_sports_odds_ingestion_normalization_audit.md
  - 1502_sports_prediction_analytics_agents_audit.md
  - 1503_sports_wager_tracking_outcome_verification_audit.md
last_verified: 2026-07-02
verifier_loop:
  - "S1504 v1 — parent-Claude synthesis of 6 parallel Explore sub-agents (Models/Persistence, Services/RuntimeFlows, APIs+Tools+Tasks+Commands, Integrations+CrossDomain, Docs+PriorResearch, Drift+Debt+Ownership+Maturity) per playbook §13."
  - "S1504 v1 pre-SIGN — parent-Claude verifier-loop landed 5 spot-checks: (a) `SportsBettingBrief` model definition VERIFIED at `core/models_unified_system.py:18394` (sub-agent 3 was wrong that no model definition existed); (b) `SportsBettingBrief` writer sites VERIFIED = 2 — `core/tasks_content.py:3150` (Cat D `_impl_generate_daily_betting_brief`) + `core/tasks.py:12187` (Session 1000 `run_all_desks_intelligence` multi-desk pipeline); (c) `SportsBettingBrief.objects.filter/get/all` reader sites VERIFIED = 0 — Finding 2 write-only-and-forgotten pattern CONFIRMED; (d) `SportsContentContextBuilder` invocation chain VERIFIED — called via `get_sports_content_context()` at `core/services/domain_content_context.py:189-190` by `DomainContentContextBuilder._get_sports_context()`, which is itself instantiated by `content_review_panel_v2.py:198` + `content_review_panel.py:82-85` + `unified_pa_entrypoint.py:476-480` — NOT dead code, but transitively coupled via DomainContentContextBuilder consumers; (e) REST endpoint `get_betting_brief` at `core/views_odds_sports.py:3237` VERIFIED — `@permission_classes([AllowAny])` + calls `SportsBettingCoordinator(sport_key=sport_key).generate_brief()` DIRECTLY (never reads the persisted `SportsBettingBrief` model)."
  - "Rigby ORM probe BEFORE draft integration on 3 Cat D task beat states via Group 1500 arc pin `pa-791b3db549a64e54` (S1503-first-applied pattern replicated here as second application) — CRITICAL §14.1 classification for `daily_betting_digest` evidence-doubled BEFORE SIGN routing (0 fires in 30d confirmed AND grep of `core/celery.py` for `daily_betting_digest` returns 0 beat entries AND grep of `docs/AUDIT_FINDINGS.md` §12 canonical deferred-by-policy list returns 0 matches — all three axes met per S1503 §14.1 pattern)."
  - "Rigby Full SIGN cycle 1 SIGN-with-edits at Medium-High confidence via fresh isolation pin `pa-af2bf7f2d1a0ef61` (retired at S1504 close via `session_tool.retire`) — D48 preemptive stability-probe gate 7th arm CLEAN (matches S1503 6th-arm cleanest arm pattern); 4 substantive SIGN turns (warmup + batch 1 + batch 1 re-request for verdict text + batch 2 + batch 3); F1-F11 folds landed at commit-time per §20.8 detailed enumeration. Cycle 2 SIGN-clean at High confidence anticipated post-fold-land."
provenance:
  parent_scoping: docs/research/domains/sports/1500_sports_domain_scoping.md
  sibling_p1_audit: docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md
  sibling_p2_audit: docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md
  sibling_p3_audit: docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md
  arc_index: docs/research/ARCHITECTURE_INDEX.md
  playbook: docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
subdomain_map:
  category: D
  slot: P4
  scope_paths:
    - core/services/sports_content_context.py
    - core/services/sports_betting_coordinator.py
    - core/tasks.py:6188 (shim)
    - core/tasks_content.py:3103 (impl)
    - core/tasks.py:6102 (digest shim)
    - core/tasks_financial.py:1907 (digest impl)
    - core/tasks_financial.py:1815 (intelligence hook impl)
    - core/services/discord_bot.py:1108 (/odds command)
    - core/views_odds_sports.py:3237 (get_betting_brief REST)
    - core/models_unified_system.py:18394 (SportsBettingBrief)
  beat_entries_verified:
    - "generate-daily-betting-brief @ 07:00 MT daily (core/celery.py:782-786)"
    - "collect-sports-odds-intelligence @ every 30 min (core/celery.py:787-791)"
    - "daily_betting_digest: NO BEAT ENTRY (Finding 1 CRITICAL — zero-fire)"
d62_mini_schema_applied: true
d62_scope: "Fourth sibling to apply the pre-brief mini-schema per D62 = (a) propagate upfront (Chris-ratified S1501 open); embedded at §4.4 (models), §5.6 (services), §6.6 (external surfaces), §8.6 (data owned), §15.16 (debt items)."
---

# Category D — Sports Betting Content Pipeline Audit

## 1. Executive Summary

Category D covers the sports betting **content generation and output surfaces** — the runtime path from ingested odds + analytics-agent outputs to Discord posts, betting briefs, and downstream content consumption. Five surfaces in scope per parent §3.D: `SportsContentContextBuilder` service, `generate_daily_betting_brief` Celery task + beat, `daily_betting_digest` Celery task, Discord `/odds` slash command, and the sports-scoped intelligence hook `_impl_collect_sports_odds_intelligence` posting to Discord `#market-intelligence`.

Cat D **consumes Cat A (odds ingestion) + Cat B (analytics agents) + Cat C (wager stats)** and **produces content that terminates at Discord or in the write-only `SportsBettingBrief` table**. There is no downstream reader of Cat D persistence and no feedback loop from Cat D output back to Cat A/B/C surfaces.

**Ten load-bearing findings** below feed the Cat F posture-decision evidence plan (P6 — S1506 audit) and the xx99 canonical summary (S1599); each finding names either a concrete remediation surface (CRITICAL / HIGH operational) or a POSTURE-DECISION-PENDING architectural question for Chris-gated integration-vs-island selection. Findings F10-F13 landed as edits from Rigby Full SIGN cycle 1 (SIGN-with-edits at Medium-High confidence) — severity re-ranks embedded per §14 + §15 + §19 (F1 fold Rigby SIGN cycle 1 batch 3 Q8):

1. **CRITICAL operational — `daily_betting_digest` unscheduled AND zero-fire.** Grep of `core/celery.py` for `daily_betting_digest` returns zero beat entries. Grep of `docs/AUDIT_FINDINGS.md` §12 canonical deferred-by-policy list returns zero matches. Rigby ORM probe on arc pin `pa-791b3db549a64e54` returned `count = 0` for 30d `CeleryTaskEvent` filter on `core.tasks.daily_betting_digest`. Docstring at `core/tasks_financial.py:1912` claims "Scheduled to run at 8 AM MST daily" — phantom behavior. **This is the S1503 §14.1 pattern replicated in Cat D scope** (`verify_betting_outcomes` had the same 3-axis signature). S1244 PR #2687 fixed sports-queue parity but did NOT create beat entries for the digest.

2. **CRITICAL architectural — `SportsBettingBrief` model is write-only-and-forgotten.** Two write sites — `core/tasks_content.py:3150` (Cat D daily brief) + `core/tasks.py:12187` (Session 1000 `run_all_desks_intelligence` multi-desk pipeline) — persist rows daily since Session 1003 (2026-02-14 migration `0242_session_1003_desk_intelligence_briefs.py`). Grep of `SportsBettingBrief.objects.filter | get | all` returns zero reader sites. **REST endpoint `get_betting_brief` at `core/views_odds_sports.py:3237` (`AllowAny`) calls `SportsBettingCoordinator.generate_brief()` DIRECTLY**, ignoring the persisted model entirely — cache TTL is 6h per Session 1003 comment at `core/models_unified_system.py:18399` but the DB persistence path was designed to survive cache expiry and now has no consumer. Two writers, zero readers. Estimated growth ~1–2 rows/day × ~500 days = ~500–1000 rows currently, no retention policy.

3. **HIGH POSTURE-DECISION-PENDING (per S1502 F3 / S1503 F9 precedent) — Zero Cat D → Cat B outcome-feedback loop.** Cat D briefs contain predictions, arbitrage opportunities, sharp-action alerts, and top plays; Cat B agents (GamePredictor, SportsOddsAnalyst, ArbitrageDetector, LineMovementAnalyzer, SharpActionDetector) produce them stateless-per-call via `SportsBettingCoordinator._run_*()` methods (`core/services/sports_betting_coordinator.py:99-187`). No back-path routes brief accuracy or top-play performance back to agent context for calibration. Whether this is missing integration or intentional posture is a Cat F question. Default posture statement following F9 in S1503: **bridge owns learning writes; brief-generation surface does not own learning writes**.

4. **HIGH POSTURE-DECISION-PENDING (per S1502 F2 / S1503 §14.3 precedent) — Zero Cat D → Signal Engine emission.** Cat D top plays + sharp signals + arbitrage opportunities are NOT written to `SignalCluster` — extends the S1274 §14 Finding #6 `sports_odds` gap from consumer side. Signals live only in Discord embeds + brief JSON blobs.

5. **MED operational (F6 fold Rigby SIGN cycle 1 batch 2 Q5 — demoted from HIGH) — `generate_daily_betting_brief` docstring cadence drift.** Docstring at `core/tasks_content.py:3110` claims "Runs twice daily (morning + evening) for pre-game analysis." Actual beat schedule at `core/celery.py:783-786` fires once daily at `crontab(hour=7, minute=0)` in Denver time (`CELERY_TIMEZONE = America/Denver` verified at `core/settings.py:807`). Rigby ORM probe confirmed once-daily firing pattern across 30d: 5 SUCCESS events at 13:00 UTC = 07:00 MT (2026-06-30, 2026-07-01, 2026-07-02 all daily). Docstring claim is stale. **F6 demote rationale (Rigby batch 2 Q5):** "less risky than 'doesn't run / duplicates / no tests / no consumers.'" — reprioritizes remediation ordering.

6. **MED-HIGH operational + architectural — Cross-domain writer bridge to `SportsBettingBrief` via `run_all_desks_intelligence` without dedup (F1 fold Rigby SIGN cycle 1 batch 1 — elevated framing).** Session 1000 multi-desk pipeline `run_all_desks_intelligence` (`core/tasks.py:12086`) is a **cross-domain writer bridge** into Cat D's canonical persistence surface — its Sports desk (Desk 2 of 4, alongside Stocks/Blockchain/Narrative) calls `SportsBettingCoordinator.generate_brief()` at `core/tasks.py:12180+` and writes rows to `SportsBettingBrief` at `core/tasks.py:12187` from OUTSIDE the Cat D beat schedule. Cat D shim `_impl_generate_daily_betting_brief` (`core/tasks_content.py:3150`) writes daily at 07:00 MT via `generate-daily-betting-brief` beat. Both writers target the same table without dedup: no `get_or_create` on `brief_date`, no unique constraint on the model at `core/models_unified_system.py:18394`, so duplicate rows for the same date are possible depending on how often `run_all_desks_intelligence` fires (beat state of that task NOT audited this session — flagged as follow-on §19.2 #7 per Rigby batch 1 F2 elevation). **Ownership contested:** Cat D owns daily brief, Session 1000 pipeline owns multi-desk brief, same target table + same coordinator dependency.

7. **MED architectural — Discord `/odds` and `_impl_collect_sports_odds_intelligence` + `_impl_daily_betting_digest` all BYPASS `SportsContentContextBuilder`.** Three of the five Cat D surfaces read `TheOddsSpider` (and `KalshiSpider` for digest) directly via `.fetch_data()` / `.get_upcoming_events()` — no involvement of the platform-authored context builder. `SportsContentContextBuilder` is invoked ONLY by the blog/content-generation path through `DomainContentContextBuilder._get_sports_context()` (`core/services/domain_content_context.py:189-190`), which is consumed by `content_review_panel_v2.py`, `content_review_panel.py`, and PA lazy-load. This means the sports "content" pipeline actually has **two disconnected content generation surfaces**: (a) Discord/digest fast path using spider data directly, (b) blog/content slow path using the context builder. The delimiter between them is not documented (parent §3.D known-drift flag).

8. **MED POSTURE-DECISION-PENDING (per S1502 F4 precedent) — Zero Cat D → Memory Domain (S1300) bridge.** `SportsContentContextBuilder.get_value_bet_context()` (`core/services/sports_content_context.py:238`) reads `AgentExecution` rows filtered by SportsOddsAnalyst context for value-bet insights, but there is no bridge to `AgentMemory` or `UserAgentLearning` for cross-domain agent learning. Cat D briefs / digests / /odds outputs do not feed into any learning surface. Extends S1503 §14 pattern.

9. **HIGH operational (F4 fold Rigby SIGN cycle 1 batch 2 Q5 — promoted from MED-HIGH; further promoted to CRITICAL tier in §19 per F8 fold batch 3 Q7) — Zero dedicated test coverage as reliability-risk multiplier.** `core/tests/` and `sports/tests/` grep for `SportsContentContextBuilder`, `generate_daily_betting_brief`, `daily_betting_digest`, `SportsBettingBrief`, `sports_betting_coordinator` returns 1 marginal match (`core/tests/test_priority_enforcement.py` mentions `SportsBettingCoordinator` for priority-check side-effect, not Cat D behavior). No behavioral tests for brief generation call-chain, no tests for `_impl_daily_betting_digest`, no tests for `/odds` command, no tests for context-builder invocation. Matches S1503 §15.6 pattern. **F4 promote rationale (Rigby batch 2 Q5):** "Given this domain is mostly schedules + Discord hooks, lack of even minimal smoke tests is a primary reliability risk multiplier." — reprioritized as CRITICAL-tier future-research per §19.1.

10. **MED operational — No PA tool for triggering brief / digest / manual regeneration.** grep of `core/services/pa_tool_schemas.py` + `core/services/tool_dispatcher.py` + `core/epa_handlers_*.py` for `generate_daily_betting_brief` / `daily_betting_digest` / `SportsBettingBrief` / `SportsContentContextBuilder` returns zero. Cat D surfaces are beat-only or Discord-user-only; there is no operator surgical tool (matches S1503 §15.11 debt finding + extends it to Cat D).

**Cat D maturity verdict** (per §13 hybrid-verdict shape extending S1503 pattern; F9 fold Rigby SIGN cycle 1 batch 3 Q8 — tightened maturity labels to distinguish beat/fire-verified vs untested runtime): **PARTIAL (mixed maturity — WORKING (beat + 30d fire evidence confirmed) at brief-generation; PRESENT + SCHEDULED (runtime not verified beyond Celery SUCCESS counts) at intelligence-hook + `/odds`; BROKEN/DORMANT at digest; WRITE-ONLY-FORGOTTEN at brief-persistence; HOT-PATH-CHOKE-POINT for content/PA at `SportsContentContextBuilder` — but bypassed by Cat D Discord fast path)** — the fourth distinguishing maturity shape in the arc after S1501 "WORKING (fragile contract) at ingestion, PARTIAL at normalization", S1502 "PARTIAL (armed but under-instrumented)", and S1503 "PARTIAL (armed but zero-fire)". **F9 fold rationale (Rigby batch 3 Q8):** the earlier "WORKING at `/odds` + intelligence-hook" was overclaim — Celery SUCCESS counts prove the task fired but do NOT prove semantic correctness of Discord posts / user interactions; runtime confirmation is a follow-on operational instrumentation task (§19 addition).

Recommended future research: 17 items ranked by architectural uncertainty × risk × unblocked flows (see §19). CRITICAL tier (F8 fold Rigby SIGN cycle 1 batch 3 Q7 — reordered): (1) digest beat remediation, (2) digest idempotency PRE-RESTORE-BEAT GATE (F5 fold — promoted from MED-HIGH per Rigby batch 2 Q5: "once you flip the beat back on, non-idempotency becomes the next highest-risk failure mode (spam/dup posts)"), (3) zero test coverage as reliability multiplier (F4 fold — promoted from MED-HIGH), (4) SportsBettingBrief consumer-or-remove decision, (5) two-writer dedup — all as PRE-Cat-F-EVIDENCE gates.

## 2. Domain Purpose

**#1 What is this domain for?** Cat D is the runtime path that transforms ingested sports odds (Cat A) + analytics-agent outputs (Cat B) + wager-tracking statistics (Cat C) into user-facing content — Discord embeds, betting briefs, morning digests, and (via the shared `SportsContentContextBuilder`) blog-prompt context for sports/betting topics.

**#2 What problem does it solve?** Sports betting content that lacks real platform experience reads like generic sports journalism instead of insights from a platform that tracks real odds, places real bets, and analyzes real line movements (Session 891 problem statement at `core/services/sports_content_context.py:5-12`). Cat D bridges the analytics-heavy Cat B outputs and raw Cat A odds into legible content surfaces (Discord + blog) that carry the platform's actual betting record + agent perspectives.

### 2.1 Cat D contract statement

Category D **guarantees** the following user-facing behaviors when its surfaces are healthy:

1. `generate_daily_betting_brief` fires once daily at 07:00 MT via `generate-daily-betting-brief` beat entry (`core/celery.py:782-786`), invokes `SportsBettingCoordinator.generate_brief()` (`core/services/sports_betting_coordinator.py:21`), and persists the result to `SportsBettingBrief` (`core/models_unified_system.py:18394`) + `LegacySpiderData` (`core/models_unified_system.py:3691`) with `spider_name='betting_coordinator'`.
2. `collect_sports_odds_intelligence` fires every 30 minutes via `collect-sports-odds-intelligence` beat entry (`core/celery.py:787-791`) and posts a formatted sports-odds intelligence message to Discord `#boardroom` (per `DiscordNotificationService.send_betting_digest()` at `core/services/discord_notifications.py:2053` hardcoded `CHANNEL_BOARDROOM` target).
3. Discord `/odds` slash command (`core/services/discord_bot.py:1108`) returns a live sports-odds embed on user invocation with sport/show/limit filters.
4. REST endpoint `GET /api/v1/betting/brief/` (`core/urls.py:3127` → `core/views_odds_sports.py:3237`) returns a freshly generated brief on every request (does NOT read persisted `SportsBettingBrief` rows) with `AllowAny` permission.
5. `SportsContentContextBuilder` provides sports/betting context (live odds via `TheOddsSpider`, platform betting performance via `PlacedWager` + `BettingStats`, value-bet context via `AgentExecution`, sports-advisor perspective via `Advisor`) to blog-content generation when invoked through `DomainContentContextBuilder._get_sports_context()`.

Category D does **NOT** guarantee (constraint statement for Cat F posture-decision framing at xx99):

1. `daily_betting_digest` does not fire on any schedule (Finding 1 CRITICAL — Rigby probe 0 fires in 30d; no beat entry). Docstring at `core/tasks_financial.py:1912` claims "8 AM MST daily" but there is no `PeriodicTask` row and no `core/celery.py` beat entry.
2. `SportsBettingBrief` persistence has no consumer beyond the model row itself (Finding 2 CRITICAL — write-only-and-forgotten pattern; two writers, zero readers).
3. No idempotency or dedup guarantee on `SportsBettingBrief.brief_date` (no unique constraint; the two writer paths can race on the same date).
4. No back-path from Cat D brief output to Cat B agent context (Finding 3 POSTURE-DECISION-PENDING).
5. No `SignalCluster` emission for top plays / sharp signals / arbitrage (Finding 4 POSTURE-DECISION-PENDING — extends S1274 §14 Finding #6).
6. No coupling between Discord fast path (`/odds`, digest, intelligence hook) and the `SportsContentContextBuilder` slow path — sports content has two disconnected generation surfaces (Finding 7).
7. No test coverage for any Cat D behavior (Finding 9).
8. No PA operator tool for triggering brief / digest / manual regeneration (Finding 10).
9. No retention policy on `SportsBettingBrief` — rows accumulate indefinitely with no purge task or TTL field (Finding 2 secondary implication).
10. No integration with `AgentMemory` / `UserAgentLearning` for cross-domain learning (Finding 8 POSTURE-DECISION-PENDING).

## 3. Canonical Entry Points

### 3.1 Write entry points — 2 persistence surfaces

1. **`_impl_generate_daily_betting_brief`** (`core/tasks_content.py:3103`) — orchestrator + persistence, invoked by beat.
   - Writes: `SportsBettingBrief` (`core/tasks_content.py:3150`) + `LegacySpiderData` with `spider_name='betting_coordinator'` (`core/tasks_content.py:3131`) + safety-net `MLPrediction` via `GamePredictor._store_predictions()` (`core/tasks_content.py:3178`).
   - Retry: bind=True, max_retries=1, default_retry_delay=300 (`core/tasks.py:6187`); Session 1165 COO #6 budget-gated exponential backoff at line 3193-3207.

2. **`_run_desks_inner` inside `run_all_desks_intelligence`** (`core/tasks.py:12086`) — Session 1000 multi-desk pipeline (Stocks + Sports + Blockchain + Narrative desks).
   - Writes: `SportsBettingBrief` (`core/tasks.py:12187`) via same `SportsBettingCoordinator.generate_brief()` call as Cat D shim.
   - Retry: no explicit retry policy — soft_time_limit=1800, time_limit=1860; failures caught + logged.
   - **Second writer path** — verified via parent-Claude grep; not exclusive to Cat D.

### 3.2 Beat-fired output entry points — 2 registered + 1 UNSCHEDULED

1. **`core.tasks.generate_daily_betting_brief`** — beat entry `generate-daily-betting-brief` at `core/celery.py:782-786` (`crontab(hour=7, minute=0)`, queue=`default`, expires=3600). Comment: "7:00 AM MT daily — MLB Run Line Desk spec 46332cee". Rigby ORM verified 5 SUCCESS fires in 30d retention (all at 13:00 UTC = 07:00 MT).
2. **`core.tasks.collect_sports_odds_intelligence`** — beat entry `collect-sports-odds-intelligence` at `core/celery.py:787-791` (`crontab(minute='*/30')`, queue=`long_running`, expires=1800). Rigby ORM verified 5 SUCCESS fires in retention window on 2026-07-02 (14:30, 15:00, 15:30) consistent with 30-min cadence.
3. **`core.tasks.daily_betting_digest`** — **UNSCHEDULED**. No beat entry in `core/celery.py` for `daily-betting-digest`. Grep verified. Rigby ORM probe returned 0 fires in 30d. Only routing: `core/settings.py:1563` → `sports` queue. Task shim at `core/tasks.py:6102` names it `core.tasks.daily_betting_digest`. **Finding 1 CRITICAL** — see §14.1.

### 3.3 REST endpoints — 5 endpoints in `core/urls.py:3126-3130`

All 5 registered at `core/urls.py:3126-3130` + defined in `core/views_odds_sports.py:3051-3550`. All 5 use `@api_view(['GET'])` + `@permission_classes([AllowAny])` — matches S1503 §14.7 REST auth pattern (uniform `AllowAny`).

| Route | View function | Line | Cat D relevance |
|---|---|---|---|
| `/api/v1/betting/brief/` | `get_betting_brief` | 3237 | **PRIMARY Cat D REST surface** — calls `SportsBettingCoordinator.generate_brief()` directly, does NOT read `SportsBettingBrief` (Finding 2 evidence) |
| `/api/v1/betting/todays-games/` | `get_todays_games` | 3051 | Cat D-adjacent — reads live odds |
| `/api/v1/betting/sharp-action/` | `get_sharp_action` | 3270 | Cat B surface (SharpActionDetector direct call), NOT Cat D |
| `/api/v1/betting/track-record/` | `get_ai_track_record` | 3317 | Cat C surface (reads platform bet stats), NOT Cat D |
| `/api/v1/betting/pipeline-status/` | `get_pipeline_status` | 3526 | Cat D-adjacent — reports Cat D task health |

Load-bearing: `get_betting_brief` (Finding 2 evidence) — REST reads Cat D coordinator output live, never touches persisted table.

### 3.4 PA tool actions — ZERO

Grep of `core/services/pa_tool_schemas.py` + `core/services/tool_dispatcher.py` + `core/epa_handlers_*.py` for `generate_daily_betting_brief` / `daily_betting_digest` / `SportsBettingBrief` / `SportsContentContextBuilder` / `sports_content_context` returns zero. **No PA operator surface for triggering, regenerating, or querying Cat D artifacts.** Matches S1503 §15.11 pattern (Cat C also had no PA surgical tool).

### 3.5 Discord commands — 1 slash + 2 scheduled digest posts + 1 intelligence hook

| Surface | Location | Trigger | Discord channel | Cat D scope |
|---|---|---|---|---|
| `/odds` slash command | `core/services/discord_bot.py:1108` | User invocation | Interaction reply (ephemeral or in-channel) | **YES — primary user-facing surface** |
| `_impl_daily_betting_digest` | `core/tasks_financial.py:1907` | **UNSCHEDULED (Finding 1)** | `CHANNEL_BOARDROOM` via `send_betting_digest()` | **YES — dormant surface** |
| `_impl_collect_sports_odds_intelligence` | `core/tasks_financial.py:1815` | `crontab(minute='*/30')` | `CHANNEL_BOARDROOM` via `send_betting_digest()` | **YES — the "market intelligence" surface** |
| `send_betting_digest` service method | `core/services/discord_notifications.py:2053` | Called by digest + intelligence hook | `CHANNEL_BOARDROOM` (hardcoded per S1501 §1 Finding 5) | Cat D-owned service method — shared between two upstreams |

**Docstring drift inherited from S1501 §1 Finding 5**: `_impl_collect_sports_odds_intelligence` docstring at `core/tasks_financial.py:1817` describes posting to `#market-intelligence`, but `send_betting_digest()` hardcodes `CHANNEL_BOARDROOM`. Parent-Claude grep-verified: only one channel constant used. **Finding: docstring-channel-name-drift** carries forward as `MED` operational item (§14.6).

### 3.6 WebSocket consumers — zero

Grep of `core/consumers*.py` + `core/routing.py` for `sports_content`, `betting_brief`, `betting_digest`, `betting_odds` returns zero. Cat D is beat + Discord + REST + blog-context, not realtime WS. Matches Cat E parent §3.E note ("no dedicated betting WebSocket channel found").

### 3.7 Management commands — zero

Grep of `core/management/commands/` for `betting`, `betting_brief`, `betting_digest`, `sports_content`, `SportsBettingBrief` returns zero. **No operator surgical tools** for manual brief triggering, digest dispatch, brief-model purge, or content-generation reruns. Matches S1503 §15.11 debt pattern (Cat C had the same gap).

## 4. Major Models

Cat D touches ~10 models but owns only 1 with clear exclusive-writer semantics — and even that ownership is contested by the Session 1000 multi-desk pipeline.

### 4.1 `SportsBettingBrief` — `core/models_unified_system.py:18394`

Session 1003 addition (migration `0242_session_1003_desk_intelligence_briefs.py:52`, 2026-02-14). UUID PK, `brief_date` (DateField, no unique constraint), `sport_filter` (CharField default `''`), `executive_summary` (TextField), five JSONField blobs (`predictions`, `arbitrage_opportunities`, `sharp_action_alerts`, `line_movements`, `top_plays`), `agents_run` (JSONField list), `errors` (JSONField list), `generation_time_seconds` (FloatField), `generated_at` (auto_now_add). Two indexes on `-brief_date` + `-generated_at`.

- **Writer sites (2):**
  1. `_impl_generate_daily_betting_brief` (`core/tasks_content.py:3150`) — Cat D daily brief path
  2. `_run_desks_inner` inside `run_all_desks_intelligence` (`core/tasks.py:12187`) — Session 1000 multi-desk pipeline
- **Reader sites (0):** verified by parent-Claude grep `SportsBettingBrief.objects.filter | get | all | count` — zero matches outside model definition + admin registration. **F1 write-only-and-forgotten pattern CONFIRMED** (Finding 2).
- **No unique constraint on `brief_date`** — two writer paths can produce parallel rows on the same date without dedup.
- **No FK to `User` / `Agent` / `Signal`** — pure JSON blob store with no relational scaffolding.
- **No retention policy** — no cleanup task, no TTL field, no purge management command.

### 4.2 `LegacySpiderData` — `core/models_unified_system.py:3691` (shared mainline model — Cat B/C bridge surface, F3 fold Rigby SIGN cycle 1 batch 1)

Legacy generic spider-output container used by 100+ files across all data_type values. Cat D writes rows with `spider_name='betting_coordinator'` + `source_url='internal://sports-betting-brief'` + `data_type='sports_odds'` (`core/tasks_content.py:3131`). **Rows are indistinguishable from Cat A theodds spider rows** by table structure alone (`data_type='sports_odds'` is used for both) — Cat D rows differ only by `spider_name='betting_coordinator'` sentinel value. Read sites include `core/views_spider_intelligence.py:1618`, `core/tasks_misc.py:2504` (DiscordNotificationService generic reader), `core/learning_bridges/spider_data_bridge.py:334` (learning system sampler) — but none specifically consume the Cat D `betting_coordinator` sentinel.

**F3 fold elevation (Rigby SIGN cycle 1 batch 1):** this shared-table pattern is a **meaningful Cat B/C bridge surface risk** — under integration posture the shared bucket lets downstream learning bridges see Cat D writes intermixed with Cat A raw spider data (silent cross-domain data mixing); under island posture the pattern is a **REFACTOR-required blocker** (Cat D rows need to be isolatable via source-tag column or dedicated model). The `spider_name='betting_coordinator'` sentinel is fragile — no schema-level uniqueness or ownership metadata. Impact on Cat F posture-decision: both postures require explicit disambiguation before Cat D can be declared island-clean OR integration-safe.

### 4.3 Read-only models Cat D consumes

| Model | Location | Reader | Read purpose |
|---|---|---|---|
| `PlacedWager` + `PlacedWagerLeg` | `core/models_betting.py:13, 108` (Cat C-owned per S1503) | `SportsContentContextBuilder.get_platform_betting_stats()` (`core/services/sports_content_context.py:166+`) | Recent wagers + sport-stats aggregates for content-authenticity injection |
| `BettingStats` | `core/models_betting.py:163` (Cat C-owned per S1503) | `SportsContentContextBuilder.get_platform_betting_stats()` (line 212) | Platform ROI + win-rate + streaks |
| `AgentExecution` | `core/models_unified_system.py:882` | `SportsContentContextBuilder.get_value_bet_context()` (line 235-260 area) | SportsOddsAnalyst historical insights |
| `Advisor` | `core/models_unified_system.py` | `SportsContentContextBuilder.get_sports_advisor_context()` (line 266+) | Sports-advisor perspective queried by expertise keywords |
| `MLPrediction` | `sports/models.py` (Cat B-owned per S1502) | `_impl_generate_daily_betting_brief` safety-net read (`core/tasks_content.py:3169`) | Count today's predictions to trigger safety-net storage |

### 4.4 4-item pre-brief mini-schema per model (D62 fold — fourth-sibling application)

Chris-ratified S1501 open: "at P1 open, child authors must capture posture-relevant evidence using a shared mini-schema." Fourth sibling to apply upfront per S1501 §4.6 + S1502 §4.8 + S1503 §4.4. Schema per surface: (a) sports-only vs shared, (b) DBAO schema vs public, (c) integration posture would require refactoring vs extending, (d) island posture would require additional isolation guarantees.

| Model | (a) sports-only vs shared | (b) DBAO vs public schema | (c) integration posture — refactor vs extend | (d) island posture — isolation guarantees needed |
|---|---|---|---|---|
| `SportsBettingBrief` | Sports-only | Public schema (`app_label='core'`) | **EXTEND** — add `user_id` FK for personalized briefs, `signal_id` FK for signal-provenance, unique constraint on `brief_date + sport_filter`; possibly add `source` field to disambiguate Cat D vs Session 1000 writer paths (Finding 6) | **NONE new** — already isolated (no inbound FK); but need retention policy + at-least-one-consumer or explicit "artifact-only, no consumer" documentation |
| `LegacySpiderData` (Cat D rows) | Shared (used by 100+ files across all data_type values) | Public schema | **REFACTOR** — Cat D rows share table + `data_type='sports_odds'` bucket with Cat A theodds spider rows; integration would require either (i) migrating to a Cat-D-owned model, or (ii) adding `source_type` / `origin_surface` field for disambiguation | **REFACTOR** — under island posture would want to isolate Cat D rows from Cat A rows via separate model or partition |
| `PlacedWager` / `PlacedWagerLeg` | Sports-only (Cat C-owned) | Public schema | **EXTEND** — Cat D consumes read-only for content context; integration posture would let brief queries stay read-only | **NONE** — Cat C read-only pattern already isolates Cat D from write concerns |
| `BettingStats` | Sports-only (Cat C-owned) | Public schema | **EXTEND** — read-only pattern preserves | **NONE** — same isolation logic |
| `AgentExecution` | Shared (mainline platform model) | Public schema | **EXTEND** — read-only pattern preserves | **NONE** — Cat D reads only |
| `Advisor` | Shared (mainline platform model) | Public schema | **EXTEND** — read-only pattern preserves | **NONE** — Cat D reads only |
| `MLPrediction` | Sports-only (Cat B-owned) | Public schema (sports app) | **EXTEND** — safety-net write pattern preserves; integration would formalize a bridge | **REFACTOR** — under island posture would need explicit contract for Cat D fallback-write path (currently defensive/undocumented) |

### 4.5 Migration lineage (parent-Claude verified)

| Model | Creation Migration | Session | Date |
|---|---|---|---|
| `SportsBettingBrief` | `core/migrations/0242_session_1003_desk_intelligence_briefs.py:52` | 1003 | 2026-02-14 |
| `LegacySpiderData` | early core migration (`0015+`, renamed S1243 per S1502 audit citation) | — | pre-2026 |
| `PlacedWager` / `PlacedWagerLeg` / `BettingStats` | `core/migrations/0128_session_563_bet_tracking.py` | 563 | pre-2026 |
| `MLPrediction` | `sports/migrations/` (Cat B scope) | — | pre-2026 |
| `AgentExecution` / `Advisor` | early core migrations | — | pre-2026 |

## 5. Major Services

### 5.1 `SportsContentContextBuilder` — `core/services/sports_content_context.py:27` (411 lines)

The platform-authored sports/betting content context builder. Session 891 origin. Owns 4 keyword lists (`SPORTS_KEYWORDS`, `BETTING_KEYWORDS`, plus 2 more for topic detection). Instance methods:

- `build_sports_context(topic, content="", include_odds=True, include_platform_stats=True, include_value_bets=True, include_advisor=True) -> str` — top-level builder returning formatted context string ~2000 chars for LLM prompt injection.
- `get_live_odds_context(topic)` — lazy-loads `TheOddsSpider`, fetches upcoming games (24h window), formats.
- `get_platform_betting_stats()` — reads `PlacedWager` + `BettingStats` for W/L record, ROI, streaks.
- `get_value_bet_context()` — reads `AgentExecution` filtered by SportsOddsAnalyst context.
- `get_sports_advisor_context(topic)` — reads `Advisor` by expertise keywords.
- Topic detection helpers: `is_sports_topic(topic, content)` + `is_betting_topic(topic, content)`.

Module-level factory functions at lines 369, 394, 404 create singleton `_sports_context_builder` instance on first call.

**Invocation chain (verified):**

```
sports_content_context.get_sports_content_context(topic)
  ↑ called at core/services/domain_content_context.py:189-190
    (inside DomainContentContextBuilder._get_sports_context())
  ↑ DomainContentContextBuilder instantiated at:
    - core/services/content_review_panel_v2.py:198  ← FIRST-CLASS DOWNSTREAM CONSUMER
    - core/services/content_review_panel.py:82-85    ← FIRST-CLASS DOWNSTREAM CONSUMER
    - core/services/unified_pa_entrypoint.py:476-480 ← PA hot-path (first-class consumer)
    - core/services/domain_content_context.py:580, 595, 610 (module-level singleton getter)
```

**Load-bearing observation (F2 fold Rigby SIGN cycle 1 batch 1 — reframed from TRANSITIVELY-COUPLED):** Cat D fast-path surfaces (`_impl_daily_betting_digest`, `_impl_collect_sports_odds_intelligence`, Discord `/odds`) do NOT call this builder. They read `TheOddsSpider` directly. Meanwhile the builder is **effectively a choke-point + likely hot-path for the content-review + blog + PA** subsystem — content_review_panel_v2 + content_review_panel + unified_pa_entrypoint are all first-class downstream consumers (not indirect / off-orbit as the initial "TRANSITIVELY-COUPLED" framing implied). This means Cat D has TWO distinct content-generation paths with divergent maturity: **HOT-PATH-CHOKE-POINT** for content/PA (SportsContentContextBuilder → DomainContentContextBuilder → content_review_panel + PA), **BYPASSED** by Discord fast path (Finding 7). Under integration posture the choke-point + bypass pair is a debt (single content shape across paths); under island posture the divergence is intentional but must be explicitly documented.

### 5.2 `SportsBettingCoordinator` — `core/services/sports_betting_coordinator.py:21` (~290 lines)

Cat B analytics agent orchestrator. Called by:
- `_impl_generate_daily_betting_brief` (`core/tasks_content.py:3117`) — Cat D scope, primary call site
- `run_all_desks_intelligence` "Sports desk" (`core/tasks.py:12086` area) — Session 1000 pipeline
- `get_betting_brief` REST view (`core/views_odds_sports.py:3249`) — REST live-generation path

Method: `generate_brief() -> Dict[str, Any]` orchestrating 5 Cat B agents sequentially:
- `GamePredictor.execute()` via `_run_game_predictor()`
- `SportsOddsAnalyst.run()` via `_run_odds_analyst()` (S1502 flagged the `.run()` vs `.execute()` asymmetry as HIGH operational risk — S1502 §1 Finding 3 / §14.x)
- `ArbitrageDetector.execute()` via `_run_arbitrage_detector()`
- `LineMovementAnalyzer.execute()` via `_run_line_movement_analyzer()`
- `SharpActionDetector.execute()` via `_run_sharp_action_detector()`

Each agent invocation wrapped in try/except; failure appended to `brief['errors']` list; brief still returns.

Return dict shape: `{agents_run, predictions, arbitrage, line_movements, sharp_action, executive_summary, top_plays, generation_time_seconds, errors, generated_at}`.

**Cat B-boundary note:** the coordinator itself is Cat B scope per S1502 §5 audit; Cat D consumes its output. The Cat D shim `_impl_generate_daily_betting_brief` handles the persistence + safety-net-fallback layer around the coordinator's return dict.

### 5.3 `DiscordNotificationService.send_betting_digest()` — `core/services/discord_notifications.py:2053` (2,319-line file)

Called by:
- `_impl_daily_betting_digest` (`core/tasks_financial.py:2022`) — Cat D digest (dormant)
- `_impl_collect_sports_odds_intelligence` (`core/tasks_financial.py:1880`) — Cat D intelligence hook

Method signature: `send_betting_digest(title: str, prediction_markets: List[dict], sports_events: List[dict], tossups: List[dict], heavy_favorites: List[dict], high_volume: List[dict]) -> bool`. Posts to hardcoded `CHANNEL_BOARDROOM` constant (S1501 §1 Finding 5 evidence). Purple embed color (`0x9B59B6`), footer "AI Studio Betting Intelligence | Session 558".

### 5.4 Additional call chain surfaces (Cat C sibling inheritance — S1503 §5.4 F1 addendum)

S1503 §5.4 F1-fold flagged three "additional Cat C read surfaces" as in-scope for Cat D. Parent-Claude verified deep-audit at Cat D:

- **`core/services/sports_content_context.py`** — the primary Cat D service (§5.1 above). Reads Cat C `PlacedWager` + `BettingStats` at lines 166-212 area. Read-only from Cat C perspective.
- **`core/views_odds_sports.py` (`get_betting_brief` at line 3237)** — Cat D REST surface. Does NOT read Cat C directly; calls `SportsBettingCoordinator.generate_brief()`. Read path to Cat C flows through the coordinator (Cat B).
- **`core/services/td_handlers_content.py`** — content-generation PA tool handler layer. Parent-Claude grep does not surface direct Cat D imports in this file for the Cat D scope surfaces; the file is content-domain PA dispatch, adjacent but not Cat D-owning.

### 5.5 God-service check

| File | Line count | Cat D relevance | God-service? |
|---|---|---|---|
| `core/services/sports_content_context.py` | 411 | Cat D-owned service | No |
| `core/services/sports_betting_coordinator.py` | 290 | Cat B-owned, Cat D calls it | No |
| `core/services/discord_notifications.py` | 2,319 | Cat D calls `send_betting_digest()` | Below 3000-line threshold |
| `core/services/discord_bot.py` | ~11,676 | Cat D `/odds` command lives here | **YES — god-service** (matches `docs/PLATFORM_INVENTORY.md` autoblock) |
| `core/tasks_financial.py` | ~2,300+ | Cat D `_impl_daily_betting_digest` + `_impl_collect_sports_odds_intelligence` | Borderline; not exclusively Cat D |
| `core/tasks_content.py` | ~3,200+ | Cat D `_impl_generate_daily_betting_brief` | God-service (crosses threshold) |

Note: `discord_bot.py` at 11,676 lines is a known platform-wide god-service (all 48 slash commands + 25 Cog classes). Not a Cat D-specific finding.

### 5.6 4-item pre-brief mini-schema per service (D62 fold)

| Service | (a) sports-only vs shared | (b) DBAO vs public | (c) integration — refactor vs extend | (d) island — isolation guarantees needed |
|---|---|---|---|---|
| `SportsContentContextBuilder` | Sports-only surface but shared invocation (blog + PA + content-review) | Public — no DBAO scoping | **EXTEND** — currently invoked only through DomainContentContextBuilder; integration posture would extend to Discord fast path (Finding 7) | **NONE** — already lives in mainline `core/services/`; island posture would need explicit "Discord fast path bypass is intentional" documentation |
| `SportsBettingCoordinator` | Sports-only | Public | **EXTEND** — 3 callers (Cat D shim, Session 1000 desk, REST); integration would formalize caller-shape | **NONE** — already sports-scoped |
| `DiscordNotificationService.send_betting_digest` | Sports-only method on shared service | Public | **EXTEND** — hardcoded `CHANNEL_BOARDROOM` is a fragile contract; integration would add channel parameter | **REFACTOR** — under island posture, sports channel might move to `#betting-only` isolation |
| Discord `/odds` command | Sports-only | N/A (no persistence) | **EXTEND** — read-only spider consumer | **NONE** |
| `_impl_daily_betting_digest` | Sports-only (dormant) | N/A (Discord-only) | **REFACTOR** — must land beat entry before integration posture is coherent | **REFACTOR** — dormant surface is orthogonal to posture selection until it's live |

## 6. Major APIs and Interfaces

### 6.1 REST endpoints — 5 endpoints (details §3.3)

All at `/api/v1/betting/*` prefix, all `AllowAny`, all `GET`-only. Cat D-owned surface: `get_betting_brief` (Finding 2 evidence: live-generation path bypasses persisted model). Cat B/C-owned surfaces: `get_sharp_action`, `get_ai_track_record`.

### 6.2 PA tools — ZERO (§3.4 evidence)

No `intelligence_tool` / `content_tool` / new-tool action for Cat D surfaces. Matches S1503 §15.11 pattern (Cat C also had no PA surgical tool for verify/recalc/bankroll). Extends the gap to Cat D content-generation trigger + digest dispatch + brief-model query.

### 6.3 Celery task surface — 3 shim tasks

| Shim task | Impl location | Beat entry | Beat cadence | Runtime fires (30d) | Docstring cadence claim | Drift? |
|---|---|---|---|---|---|---|
| `core.tasks.generate_daily_betting_brief` | `core/tasks_content.py:3103` | `core/celery.py:782-786` | `crontab(hour=7, minute=0)` (07:00 MT) | 5 SUCCESS fires (Rigby probe) | "Runs twice daily (morning + evening)" (`core/tasks_content.py:3110`) | **YES — HIGH per §14.2**: docstring says 2×/day, actual is 1×/day |
| `core.tasks.daily_betting_digest` | `core/tasks_financial.py:1907` | **NO BEAT ENTRY** | N/A | **0 fires** (Rigby probe) | "Scheduled to run at 8 AM MST daily" (`core/tasks_financial.py:1912`) | **YES — CRITICAL per §14.1**: docstring claims schedule that doesn't exist |
| `core.tasks.collect_sports_odds_intelligence` | `core/tasks_financial.py:1815` | `core/celery.py:787-791` | `crontab(minute='*/30')` (every 30 min) | 5+ SUCCESS fires (Rigby probe consistent with 30-min cadence) | Docstring line 1817 says "Post trending sports odds to Discord `#market-intelligence`" (channel-name drift only, no cadence claim) | Channel-name docstring drift (§14.6 MED) |

Grep of `docs/AUDIT_FINDINGS.md` §12 canonical deferred-by-policy list for all 3 task names returned zero matches — **none are intentionally deferred**.

### 6.4 Discord command surface — 4 surfaces (§3.5)

Slash: `/odds`. Scheduled: `_impl_collect_sports_odds_intelligence` (every 30 min). Dormant: `_impl_daily_betting_digest`. Shared service method: `send_betting_digest()`.

### 6.5 WebSocket surface — zero (§3.6)

### 6.6 4-item pre-brief mini-schema per external surface (D62 fold)

| Surface | (a) sports-only vs shared | (b) DBAO vs public schema | (c) integration posture — refactor vs extend | (d) island posture — isolation guarantees needed |
|---|---|---|---|---|
| `/api/v1/betting/brief/` REST | Sports-only route prefix | Public schema | **EXTEND** — path prefix `/api/v1/betting/` is already sports-scoped; add `IsAuthenticated` for personalized briefs | **NONE** — already isolated by URL prefix |
| `generate-daily-betting-brief` beat | Sports-only | Public — `default` queue | **EXTEND** — could move to `sports` queue but requires Procfile + Makefile parity per S1244 fix | **REFACTOR** — under island posture would move to dedicated `sports` queue |
| `collect-sports-odds-intelligence` beat | Sports-only | Public — `long_running` queue | **EXTEND** — already on shared long_running queue | Same as above |
| `daily_betting_digest` beat | Sports-only (would-be, dormant) | Public — `sports` queue (per settings.py:1563 routing, but zero fires because no beat entry) | **REFACTOR** — must land beat entry first | **REFACTOR** — must restore firing before posture is coherent |
| Discord `/odds` slash command | Sports-only | N/A | **EXTEND** — read-only spider consumer | **NONE** |
| `send_betting_digest` → `CHANNEL_BOARDROOM` | Sports-only content, shared channel | Public Discord | **REFACTOR** — hardcoded channel is a fragile contract | **REFACTOR** — under island posture would move to `#betting-only` |

## 7. Runtime Flows

### 7.1 EXPLICIT call-chain — `generate_daily_betting_brief` (S1502 §7.1 / S1503 §7.1 F1-fold pattern applied)

```
Celery beat @ 07:00 America/Denver (crontab(hour=7, minute=0))
  ↓  (core/celery.py:782-786 — 'generate-daily-betting-brief' entry)
  ↓  (CELERY_TIMEZONE = America/Denver at core/settings.py:807)
core.tasks.generate_daily_betting_brief() [shim]
  ↓  @shared_task(bind=True, max_retries=1, default_retry_delay=300, queue='default')
  ↓  (core/tasks.py:6187-6190)
_impl_generate_daily_betting_brief(self)
  ↓  (core/tasks_content.py:3103)
  │
  ├─ 1. SportsBettingCoordinator().generate_brief()  [SYNCHRONOUS]
  │       ↓  (core/services/sports_betting_coordinator.py:21)
  │       ├─ _run_game_predictor()          → GamePredictor.execute()
  │       ├─ _run_odds_analyst()             → SportsOddsAnalyst.run()    ⚠️ .run() vs .execute() asymmetry (S1502 §1 Finding 3)
  │       ├─ _run_arbitrage_detector()       → ArbitrageDetector.execute()
  │       ├─ _run_line_movement_analyzer()   → LineMovementAnalyzer.execute()
  │       └─ _run_sharp_action_detector()    → SharpActionDetector.execute()
  │       ↓  each wrapped in try/except; failure → brief['errors'].append
  │       ↓
  │       returns brief = {agents_run, predictions, arbitrage, line_movements, sharp_action, executive_summary, top_plays, generation_time_seconds, errors, generated_at}
  │
  ├─ 2. LegacySpiderData.objects.create()  [SYNCHRONOUS write #1]
  │       ↓  (core/tasks_content.py:3131)
  │       spider_name='betting_coordinator', source_url='internal://sports-betting-brief',
  │       data_type='sports_odds', raw_data=brief, embedding_text=executive_summary[:2000]
  │
  ├─ 3. SportsBettingBrief.objects.create()  [SYNCHRONOUS write #2]
  │       ↓  (core/tasks_content.py:3150)
  │       brief_date=timezone.now().date(), executive_summary=(brief['executive_summary'] or '')[:500],
  │       predictions/arbitrage_opportunities/sharp_action_alerts/line_movements/top_plays/agents_run/errors=brief[key],
  │       generation_time_seconds=elapsed
  │       ⚠️  NO reader consumes this row (Finding 2 CRITICAL)
  │
  ├─ 4. MLPrediction safety-net check  [SYNCHRONOUS conditional]
  │       ↓  (core/tasks_content.py:3168-3181)
  │       today_count = MLPrediction.objects.filter(created_at__date=today).count()
  │       IF today_count == 0 AND brief['predictions']['predictions'] non-empty:
  │         GamePredictor()._store_predictions(pred_list, {})  # safety-net Cat B write
  │
  └─ 5. return {status, agents_run, top_plays_count, generation_time}

ON EXCEPTION (line 3190):
  → Session 1165 COO #6 budget-gated exponential backoff retry
  → check_retry_budget("generate_daily_betting_brief", window=3600, max_retries=5)
  → if allowed: self.retry(countdown=compute_retry_countdown(retries, base=120))
```

**Synchronous boundaries:** All within a single Celery task worker. No async/await. Agent runs block sequentially. DB writes happen before task return.

**Load-bearing observation:** This task NEVER posts to Discord. Discord posting is Cat D fast path (`_impl_daily_betting_digest` + `_impl_collect_sports_odds_intelligence`), separate task tree.

### 7.2 `run_all_desks_intelligence` — Session 1000 multi-desk pipeline (secondary Cat D writer)

`core/tasks.py:12086-12200` area. Fires as a separate top-level task orchestrating 4 desks: Stocks (`MarketIntelligenceCoordinator`), Sports (`SportsBettingCoordinator.generate_brief()`), Blockchain (`BlockchainAuditCoordinator.execute()`), Narrative (`NarrativeDriftCoordinator.execute()`). Each desk result is cached (6h TTL) AND persisted to its per-desk model. **Session 1005 fix note at line 12184** ("Persist to DB so briefs survive cache TTL") indicates the persistence path was intentional — but no downstream reader consumes `SportsBettingBrief` rows.

**Beat state of `run_all_desks_intelligence` NOT audited in this session — flagged as follow-on parent-Claude verification** (was it Session 1000 that shipped the beat entry? Or is it also dormant? Would confirm Finding 6 severity).

### 7.3 `_impl_daily_betting_digest` flow (dormant surface — Finding 1)

Would fire (if beat existed) → `KalshiSpider().fetch_data()` + `TheOddsSpider().fetch_data()` → filter + group + rank → `DiscordNotificationService().send_betting_digest(...)` → `CHANNEL_BOARDROOM`. Zero DB persistence. Currently unscheduled — no beat entry in `core/celery.py`, Rigby ORM 0 fires in 30d.

### 7.4 `_impl_collect_sports_odds_intelligence` flow (every 30 min — WORKING)

Fires → `TheOddsSpider().get_upcoming_events(hours=24)` → group by sport → build message lines → `send_betting_digest()` → `CHANNEL_BOARDROOM`. Zero DB persistence. Confirmed WORKING via Rigby ORM (5 SUCCESS fires in retention window at 30-min intervals).

### 7.5 Discord `/odds` flow (user-invoked — WORKING)

User invokes `/odds [sport] [show] [limit]` → `interaction.response.defer()` → `@sync_to_async get_odds_data()` → `TheOddsSpider().fetch_data(max_results=100, max_priority=2)` → sport-map filter (`nfl→'NFL'` etc. at `core/services/discord_bot.py:1141-1147`) → show filter (tossups 45-55%, favorites ≥65%) → sort by `commence_time` → slice → build `discord.Embed` with per-event field → `interaction.followup.send(embed)`. Zero DB persistence.

### 7.6 `SportsContentContextBuilder` invocation flow (blog/content slow path — separate from Cat D fast path)

`get_sports_content_context(topic)` called at `core/services/domain_content_context.py:189-190` by `DomainContentContextBuilder._get_sports_context()`, which is instantiated by three consumer surfaces:
- `content_review_panel_v2.py:198` — content review pipeline
- `content_review_panel.py:82-85` — legacy content review pipeline
- `unified_pa_entrypoint.py:476-480` — PA lazy-load for content-generation queries

Returns formatted context string ~2000 chars for LLM prompt injection at blog generation time. **This is a completely separate content-generation path from the Discord fast path** (Finding 7).

## 8. Data Ownership and Lifecycle

### 8.1 Owned data (writes to Cat D-exclusive models)

`SportsBettingBrief` is the closest to Cat D-exclusive, but ownership is contested by `run_all_desks_intelligence` (Session 1000 multi-desk pipeline). Both writers use `.objects.create()` on the same table without dedup logic. **Cat D shares ownership** — not exclusive.

### 8.2 Consumed data (reads from outside Cat D)

- Cat A: `SpiderData` + `LegacySpiderData` (theodds rows via spider fetches), `TheOddsSpider` API via lazy service, `KalshiSpider` API via lazy service.
- Cat B: `SportsBettingCoordinator.generate_brief()` return dict; `MLPrediction` count-query for safety-net trigger.
- Cat C: `PlacedWager` + `PlacedWagerLeg` + `BettingStats` (read-only via `SportsContentContextBuilder`).
- Platform: `AgentExecution`, `Advisor`.

### 8.3 Produced data (writes to outside Cat D)

- **Fallback / safety-net:** `MLPrediction` via `GamePredictor._store_predictions()` at `core/tasks_content.py:3178` — defensive write when Cat B primary path (GamePredictor.execute() internal store) fails.
- **Shared:** `LegacySpiderData` rows with `spider_name='betting_coordinator'` sentinel (Cat A rows use different `spider_name` values).

### 8.4 Not produced (grep-verified absences — load-bearing for Cat F)

- **`SignalCluster` — zero writes.** Cat D top-plays / sharp signals / arbitrage opportunities do NOT emit to `SignalCluster`. Extends S1274 §14 Finding #6 (sports_odds not a `SignalCluster.pattern_type`) to Cat D content output. **Finding 4 POSTURE-DECISION-PENDING**.
- **`AgentMemory` / `UserAgentLearning` — zero writes.** Cat D briefs do NOT feed into Memory Domain (S1300) surfaces. **Finding 8 POSTURE-DECISION-PENDING**.
- **`Deliverable` / `ClaimsPack` / `PublishGate` / `SelfBlog` — zero writes.** Cat D does NOT emit into the mainline content-pipeline persistence layer. Brief output stays in `SportsBettingBrief` + Discord.
- **No back-writes to Cat A/B agent state.** Cat D consumes but does not update Cat A ingestion cadence or Cat B agent context.

### 8.5 Lifecycle policies

- **`SportsBettingBrief`:** no cleanup task, no TTL field, no retention policy. Rows accumulate indefinitely since Session 1003 addition (2026-02-14). Estimated growth: 1-2 rows/day × ~500 days = ~500-1000 rows currently. Low-volume table but poor ops hygiene. **Finding 2 secondary implication**.
- **`LegacySpiderData` Cat D rows:** subject to whatever platform-wide retention applies to `LegacySpiderData` — not Cat D-specific.
- **Discord posts:** ephemeral (retention subject to Discord platform).
- **REST responses:** stateless, no persistence.

### 8.6 4-item pre-brief mini-schema per data owned / consumed (D62 fold)

Applied to §8.1-8.3 owned + produced data surfaces (schema for consumed data covered in §4.4). Fourth-sibling application.

| Data | (a) sports-only vs shared | (b) DBAO vs public | (c) integration — refactor vs extend | (d) island — isolation guarantees needed |
|---|---|---|---|---|
| `SportsBettingBrief` rows | Sports-only | Public | **EXTEND** — add `source` column to distinguish Cat D vs Session 1000 writers; add retention TTL | **NONE** new — but retention policy required regardless of posture |
| `LegacySpiderData` rows with `spider_name='betting_coordinator'` | Shared table, sports-only sentinel | Public | **REFACTOR** — Cat D rows share table with Cat A rows; integration would require source-tag column or dedicated model | **REFACTOR** — under island posture would extract to Cat-D-owned model |
| Safety-net `MLPrediction` writes | Sports-only | Public (sports app) | **EXTEND** — formalize the Cat D → Cat B fallback contract | **REFACTOR** — under island posture would need explicit safety-net documentation |
| Discord `CHANNEL_BOARDROOM` posts (digest + intelligence hook) | Sports content on shared channel | External Discord | **REFACTOR** — hardcoded channel is fragile | **REFACTOR** — under island posture would move to `#betting-only` |

## 9. Integrations With Other Domains

Table format per playbook §11.2 §9 requirements. Extends S1502 §9 + S1503 §9 patterns.

| Direction | Domain | Surface | Contract | Direction of dependency | Load-bearing? |
|---|---|---|---|---|---|
| Inbound (Cat D reads) | Cat A (Odds Ingestion) | `TheOddsSpider.fetch_data()`, `TheOddsSpider.get_upcoming_events()` | Direct instantiation via lazy import | Cat D → Cat A (unmediated) | YES — every Cat D surface reads Cat A |
| Inbound | Cat A | `KalshiSpider.fetch_data()` | Direct instantiation via lazy import | Cat D → Cat A | YES — digest surface only |
| Inbound | Cat B (Analytics Agents) | `SportsBettingCoordinator.generate_brief()` orchestration return | dict payload | Cat D → Cat B (mediated via coordinator) | YES — brief generation depends on 5 agents |
| Inbound | Cat B | `MLPrediction.objects.filter(created_at__date=today).count()` | Read query | Cat D → Cat B | YES — safety-net trigger |
| Inbound | Cat C (Wager Tracking) | `PlacedWager` + `PlacedWagerLeg` + `BettingStats` reads | Read queries via context builder | Cat D → Cat C (read-only) | Medium — content-authenticity injection |
| Inbound | Platform | `AgentExecution`, `Advisor` | Read queries via context builder | Cat D → Platform | Medium — content context |
| Outbound (Cat D writes) | Cat B | Safety-net `MLPrediction` via `GamePredictor._store_predictions()` | Defensive fallback | Cat D → Cat B (rare path) | Medium — undocumented contract |
| Outbound | Discord | `CHANNEL_BOARDROOM` via `send_betting_digest()` | Fire-and-forget notification | Cat D → Discord | YES — 30-min beat + dormant digest |
| Outbound | Discord | User interaction reply for `/odds` command | ephemeral Discord embed | User → Cat D (pull) | YES — user-facing |
| Outbound | Signal Engine | **NONE** — no `SignalCluster.objects.create()` calls from Cat D surfaces | UNKNOWN — POSTURE-DECISION-PENDING (Finding 4) | Missing bridge | LOAD-BEARING per S1274 §14 Finding #6 |
| Outbound | Memory Domain (S1300) | **NONE** — no `AgentMemory` / `UserAgentLearning` writes | UNKNOWN — POSTURE-DECISION-PENDING (Finding 8) | Missing bridge | LOAD-BEARING per S1502 F4 precedent |
| Outbound | Content Pipeline (Group 1600 if opened) | **NONE** — no `SelfBlog` / `ClaimsPack` / `Deliverable` writes | UNKNOWN — Group 1600 delegates | Missing bridge (deliberate?) | Parked per parent §6.5 |

Extending S1502 §9 outbound + inbound; extending S1503 §9 outbound. No direct Cat D ↔ Cat C write-path (both read from same Cat A + write to Discord).

## 10. Event Flows

### 10.1 Events emitted (verified via code)

- **Django ORM `post_save` signals** on `SportsBettingBrief.objects.create()` and `LegacySpiderData.objects.create()` fire per Django default; no explicit signal receivers registered for `SportsBettingBrief` in Cat D scope (parent-Claude grep on `@receiver.*SportsBettingBrief` returns zero).
- **Discord webhook fires** on every `send_betting_digest()` call (via `_impl_daily_betting_digest` when live + `_impl_collect_sports_odds_intelligence` at 30-min cadence + `/odds` user replies).
- **Celery task lifecycle events** (`CeleryTaskEvent` rows via `task_prerun` / `task_postrun` — S1244+ instrumentation) fire for all beat-scheduled Cat D tasks. Rigby ORM confirmed 5 SUCCESS rows for `generate_daily_betting_brief`, 5+ for `collect_sports_odds_intelligence`, 0 for `daily_betting_digest`.

### 10.2 Events SHOULD Cat D emit (integration posture) — POSTURE-DECISION-PENDING

- `SignalCluster` rows with `pattern_type='sports_odds'` (or new sports-specific pattern types) for top plays, sharp-action alerts, arbitrage opportunities — currently NOT emitted (S1274 §14 Finding #6, extended by Finding 4).
- `AgentMemory` write-back after brief consumption (integration posture) — currently NOT emitted (Finding 8).
- `ContentDeliberation` / `PublishGate` events for briefs that should route through mainline content pipeline — parked per parent §6.5 (Group 1600 boundary).

### 10.3 Events SHOULD Cat D emit (island posture)

- Explicit "no signal emission" documentation in Cat D topic doc (owed to xx99).
- Explicit dedicated `#betting` Discord channel isolation (currently shares `#boardroom`).
- Explicit "brief-only, no downstream consumer" contract for `SportsBettingBrief`.

## 11. Existing Documentation

### 11.1 Topic docs — NONE

Grep of `docs/topics/` for `sports_content`, `betting_brief`, `betting_digest`, `sports-betting`, `SportsContentContextBuilder`, `SportsBettingBrief`, `SportsBettingCoordinator` returns zero. No `docs/topics/sports*.md` or `docs/topics/betting*.md` exists. Parent §6.5 flags this as a gap owed to xx99: "xx99 recommends creating a canonical topic doc, but content sourcing (from P4 + P5 audits) is the input." **Owed to xx99 (S1599 §7.4)**.

### 11.2 Narrative docs — NONE

Grep of `docs/PLATFORM_WHAT_IT_IS.md` + `docs/PLATFORM_INVENTORY.md` + `docs/ARCHITECTURE.md` + `docs/AGENTS.md` + `docs/SERVICES.md` for Cat D surface names returns zero direct mentions. `docs/topics/agent-system.md` mentions the 5 Cat B market agents (GamePredictor, SportsOddsAnalyst, ArbitrageDetector, LineMovementAnalyzer, SharpActionDetector) but not the Cat D wrappers.

### 11.3 Prior research library

- **S1273 §3.10** Sports Intelligence / Betting Pipeline row — LIGHT coverage; enumerates surface generically without Cat D-specific breakdown.
- **S1274 §12.3 Product/Architecture Decision Point (P1)** — frames island-vs-integration posture with explicit success criteria; Cat D content-integration is a load-bearing criterion.
- **S1274 §14 Finding #6** (HIGH) — Sports/DBAO ↔ Signal/Content pipeline break; extends to Cat D consumer side via Finding 4.
- **S1273 §9 #4** Sports ↔ AI Studio Integration Sketch mission — parent for Group 1500.
- **`docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md`** — Cat A audit; §1 Finding 5 (LOW) flags `_impl_collect_sports_odds_intelligence` docstring channel-name drift (`#market-intelligence` vs `CHANNEL_BOARDROOM`); §10 parked "betting brief / digest — SportsContentContextBuilder reads live odds through TheOddsSpider re-invocation OR via SpiderData — Cat D audit will clarify."
- **`docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md`** — Cat B audit; §2.1 Cat B contract statement lists "Outbound (Cat B ↔ Cat D Content Pipeline — S1504 scope) — Brief dict from SportsBettingCoordinator.generate_brief() feeds _impl_generate_daily_betting_brief"; §7.1 F1-fold call-chain block is direct precedent for §7.1 above.
- **`docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md`** — Cat C audit; §5.4 F1-fold flags 3 "additional Cat C read surfaces" as in Cat D scope — deep-audited here (§5.4).
- **`docs/AUDIT_FINDINGS.md` §12** canonical Celery deferred-by-policy list — parent-Claude grep verified `generate_daily_betting_brief`, `daily_betting_digest`, `collect_sports_odds_intelligence` are all absent — none intentionally deferred.
- **`docs/CELERY_AUDIT.md`** — canonical Celery inventory referenced by S1503 for Cat C `verify_betting_outcomes` classification.

### 11.4 Session handoffs

- **Session 558** (alleged origin — no handoff found in current archive): `_impl_daily_betting_digest`, `_impl_collect_sports_odds_intelligence`, `/odds` command docstrings all cite.
- **Session 891** (alleged origin): `SportsContentContextBuilder` docstring cites.
- **Session 995B** (alleged origin): `_impl_generate_daily_betting_brief` docstring cites.
- **Session 1003** — `docs/handoffs/SESSION_1003_PIPELINE_COMPLETION.md`: Session 1003 added `SportsBettingBrief` model + `run_all_desks_intelligence` multi-desk pipeline.
- **Session 1005** — noted as fix for key mismatches (arbitrage, sharp_action) + None guards in `SportsBettingBrief.objects.create()` call.
- **Session 1205** — `docs/handoffs/SESSION_1205_EVIDENCE_PIPELINE_PLUS_CAPABILITY_AUDIT.md`: **PR #2457 shipped beat schedule entries** for 4 sports producers including `generate-daily-betting-brief` + `collect-sports-odds-intelligence`. First documented beat-schedule landing for Cat D. Did NOT include `daily_betting_digest` beat.
- **Session 1206** — flagged SportsOddsAnalyst `.run()` vs `.execute()` telemetry blind-spot (S1502 §1 Finding 3 evidence).
- **Session 1244** — `SESSION_1244_CAT_2_FULLY_CLOSED_...`: sports-queue Procfile↔Makefile parity fix. Did NOT restore `daily_betting_digest` beat entry.
- **Session 1500** — `docs/research/domains/sports/1500_sports_domain_scoping.md`: parent scoping; §3.D flags MT-tz assumption + consumer-surface delimiter drift; §5 mission sequence locks P4 = S1504.
- **Session 1501/1502/1503** — sibling audits; extensive Cat D-preparatory evidence.

## 12. Research Coverage

Per playbook §12 scale (NONE / LIGHT / MODERATE / DEEP / CANONICAL):

**Cat D research coverage at S1504 open: LIGHT.**

Evidence:
- S1273 §3.10 rates LIGHT and does not decompose Cat D specifically.
- Zero topic docs (§11.1).
- Zero narrative doc mentions (§11.2).
- S1274 flags integration gap (Finding #6) but does not audit Cat D surface-by-surface.
- Sibling audits (S1501/S1502/S1503) reference Cat D as downstream consumer, parked for S1504.
- No completed audit doc for Cat D until this session.

**Cat D research coverage after S1504 close (this doc): MODERATE.**

Evidence: this audit inventories 5 surfaces + 10 findings + 4 D62 mini-schema tables. Full contract statement §2.1. Explicit call-chain block §7.1. Rank-ordered future-research queue §19. Fits playbook §12 MODERATE definition ("at least one focused doc or meaningful canonical documentation exists").

Promotion to DEEP or CANONICAL awaits xx99 (S1599) synthesis + any follow-on design-preparation for Cat D remediation PRs.

## 13. Architecture Maturity

Per playbook §12 scale (EXPERIMENTAL / PARTIAL / WORKING / STABLE / CANONICAL):

**Cat D maturity verdict: PARTIAL (mixed maturity — WORKING (beat + fire evidence confirmed) at brief-generation; PRESENT + SCHEDULED (runtime not verified beyond Celery SUCCESS counts) at intelligence-hook + `/odds`; BROKEN/DORMANT at digest; WRITE-ONLY-FORGOTTEN at brief-persistence; HOT-PATH-CHOKE-POINT for content/PA at `SportsContentContextBuilder` — but bypassed by Cat D Discord fast path)** (F9 fold Rigby SIGN cycle 1 batch 3 Q8 — tightened maturity labels).

Fourth distinguishing maturity shape in the arc:
- S1501 Cat A: "WORKING (fragile contract) at ingestion, PARTIAL at normalization"
- S1502 Cat B: "PARTIAL (armed but under-instrumented)"
- S1503 Cat C: "PARTIAL (armed but zero-fire)"
- **S1504 Cat D: "PARTIAL (mixed — WORKING at 3 of 5 surfaces, BROKEN at digest, WRITE-ONLY-FORGOTTEN at persistence, TRANSITIVELY-COUPLED at context-builder)"**

Component-by-component:

| Surface | Maturity | Evidence |
|---|---|---|
| `generate_daily_betting_brief` task | WORKING (beat + 30d fire evidence confirmed) | Beat live at 07:00 MT, 5 SUCCESS fires in 30d, brief persisted, retry policy wired |
| `_impl_collect_sports_odds_intelligence` | PRESENT + SCHEDULED (runtime not verified beyond Celery SUCCESS counts) — F9 fold | Beat live every 30 min, 5+ SUCCESS fires; Discord posting semantic correctness NOT verified (Celery success ≠ Discord webhook success ≠ correct payload) |
| Discord `/odds` slash command | PRESENT + SCHEDULED (runtime not verified) — F9 fold | Command registered, filters implemented, embed formatting present; no telemetry on user interaction success, no reachability probe |
| `daily_betting_digest` task | BROKEN/DORMANT | No beat entry, 0 fires in 30d, docstring claims schedule that doesn't exist (Finding 1 CRITICAL) |
| `SportsBettingBrief` model + REST endpoint | WRITE-ONLY-FORGOTTEN | 2 writers, 0 readers; REST endpoint bypasses persisted model (Finding 2 CRITICAL) |
| `SportsContentContextBuilder` service | HOT-PATH-CHOKE-POINT for content/PA, BYPASSED by Cat D Discord fast path (F2 fold — reframed from TRANSITIVELY-COUPLED) | First-class downstream consumers: content_review_panel_v2 + content_review_panel + PA lazy-load; Cat D fast path (`/odds`, digest, intelligence-hook) does NOT invoke it |
| `send_betting_digest` service method | WORKING (fragile) — Discord webhook reachability not probed | Hardcoded channel; called by two upstreams (one dormant, one live) |

**Sibling pattern replication:**

Which S1503 patterns replicate to Cat D:
- §14.1 CRITICAL beat-schedule zero-fire pattern (`verify_betting_outcomes` → `daily_betting_digest`) — YES (Finding 1)
- §14.2 outcome-feedback loop missing — YES (Finding 3, adapted to Cat D → Cat B)
- §14.3 Signal Engine emission missing — YES (Finding 4)
- §14.4 dual task variants — NO (Cat D has only one `daily_betting_digest`, not two)
- §14.5 dual aggregation surface — PARTIAL (SportsBettingBrief has two writers; not two models like `Bankroll` vs `BettingStats`)
- §14.7 REST `AllowAny` uniform — YES (all 5 `/api/v1/betting/*` endpoints)
- §15.6 zero test coverage — YES (Finding 9)
- §15.11 no PA surgical tool — YES (Finding 10)

Which S1503 patterns do NOT replicate:
- §2.1 Cat C contract "9 non-guarantees" — Cat D has 10 non-guarantees (§2.1 above)
- §14.4 dual task definitions — Cat D has single-definition tasks
- §15.12 fixture identity across bookmakers — Cat A/B scope, not Cat D

## 14. Known Drift

### 14.1 CRITICAL — `daily_betting_digest` unscheduled AND zero-fire (S1503 §14.1 analog)

**3-axis probe results:**

- **Axis 1 (grep `core/celery.py`):** zero beat entries for `daily_betting_digest` or `daily-betting-digest`. Parent-Claude verified.
- **Axis 2 (grep `docs/AUDIT_FINDINGS.md` §12):** zero matches — NOT on canonical deferred-by-policy list.
- **Axis 3 (Rigby ORM probe on arc pin `pa-791b3db549a64e54`):** `PeriodicTask.objects.count() = 0` for `task_name='core.tasks.daily_betting_digest'`. `CeleryTaskEvent.objects.filter(30d, task_name='core.tasks.daily_betting_digest').count() = 0`.

**Docstring at `core/tasks_financial.py:1911-1913`:**
```
Session 558: Morning briefing combining prediction markets and sports odds.
Scheduled to run at 8 AM MST daily.
```

**Runtime reality:** No beat entry, no PeriodicTask row, zero fires in 30d. Docstring claims phantom schedule.

**Provenance chain:** Task defined Session 558 (per docstring) → task registered as `core.tasks.daily_betting_digest` → routed to `sports` queue at `core/settings.py:1563` → **no beat entry ever landed**. S1244 fixed sports-queue parity but did not create a beat entry (only fixed local worker consumption). S1205 shipped beat entries for 4 producer tasks (generate/collect variants) but omitted digest.

**Severity CRITICAL** — matches S1503 §14.1 4-criteria classification exactly:
- Beat entry MISSING: ✓
- NOT on §12 deferred list: ✓
- Zero fires in 30d: ✓
- Docstring claims schedule that doesn't exist: ✓

**Independent Rigby ORM probe evidence-doubled BEFORE draft integration** (S1503 pattern replicated). Verifier-loop tool chain applied per S1503 §14.1 codification-candidate.

**Cat F implication:** Load-bearing for posture-decision brief. Both postures require the digest to either land beat entry or be documented as intentionally-deferred (add to §12). Currently it is neither.

### 14.2 MED (F6 fold Rigby SIGN cycle 1 batch 2 Q5 — demoted from HIGH) — `generate_daily_betting_brief` docstring "twice daily" vs runtime once-daily

**Docstring at `core/tasks_content.py:3110`:**
```
Runs twice daily (morning + evening) for pre-game analysis.
```

**Runtime reality:** `crontab(hour=7, minute=0)` at `core/celery.py:784` — once daily at 07:00 MT (Denver time). Rigby ORM 5 SUCCESS fires all at 13:00 UTC = 07:00 MT (2026-06-30, 2026-07-01, 2026-07-02 daily). No evening run.

**Assessment:** Docstring intent (2×/day) vs actual cadence (1×/day) mismatch. Either the docstring is stale (evening run was removed or never landed) or the second fire is unimplemented.

**Severity MED (F6 fold demote — Rigby batch 2 Q5 rationale: "less risky than 'doesn't run / duplicates / no tests / no consumers'")** — load-bearing for operational expectations. Users expecting evening brief will not receive one, but the primary daily brief still ships.

**Remediation options (not implementation — audit only):**
- Update docstring to reflect once-daily cadence
- OR add second beat entry for evening cron
- Chris-gated decision at post-arc PR

### 14.3 HIGH — `SportsBettingBrief` write-only-and-forgotten pattern (Finding 2 evidence)

**Writer sites:** 2 (verified §4.1).
**Reader sites:** 0 (verified via grep on `.objects.filter | get | all | count`).
**REST endpoint bypass:** `get_betting_brief` at `core/views_odds_sports.py:3237` calls `SportsBettingCoordinator.generate_brief()` DIRECTLY — never reads persisted model.

**Session 1003 model docstring at `core/models_unified_system.py:18398-18400`:**
```
Before this model, SportsBettingCoordinator.generate_brief() output was
only stored in a 6-hour cache that expired. This model persists briefs
for historical analysis and learning.
```

**Runtime reality:** Neither "historical analysis" nor "learning" consumer exists. Model is a shadow-write artifact.

**Severity HIGH-architectural** — this is a persistence pattern that suggests either (a) the consumer was planned but never built, or (b) the consumer was removed but the writer path was left in place. Either way, it costs 1-2 rows/day since Session 1003 with no reader.

### 14.4 HIGH POSTURE-DECISION-PENDING — Zero Cat D → Cat B outcome-feedback loop

Cat D briefs contain predictions + arbitrage opportunities + sharp-action alerts + top plays. Cat B agents produce them stateless per call. **No back-path** from brief accuracy / top-play performance to Cat B agent context for calibration.

Grep evidence:
- Zero references to `SportsBettingBrief.objects.filter` in any Cat B agent (`GamePredictor`, `SportsOddsAnalyst`, etc.).
- Zero `AgentMemory` writes from Cat D surfaces.
- `SportsBettingLearningBridge` service does NOT exist (parent-Claude grep verified — matches Sub-agent 4 UNKNOWN).

**F9 fold precedent from S1503:** "bridge owns learning writes; brief-generation surface does not own learning writes." Applied to Cat D: **default posture — bridge owns Cat D → Cat B calibration writes; Cat D primary surface (brief generation) does not own the loop-close**.

**F11 fold Rigby SIGN cycle 1 batch 3 Q8 — no owning bridge implementation was located:** Grep verified — no `SportsBettingLearningBridge` service exists; no bridge implementation was located for this integration point. The POSTURE-DECISION-PENDING label is decision-pending BECAUSE no bridge implementation has been built (not because bridge is intentionally delegated with evidence). Rigby batch 2 Q4: "reads as 'not built / not wired,' not 'intentionally delegated with evidence.'"

**Cat F implication:** Load-bearing evidence for posture-decision brief. Integration posture requires new bridge (SportsBettingLearningBridge or similar). Island posture requires explicit documentation of "no calibration loop by design."

### 14.5 HIGH POSTURE-DECISION-PENDING — Zero Cat D → Signal Engine emission

**Grep evidence:** Zero `SignalCluster.objects.create()` calls in `core/services/sports_content_context.py`, `core/services/sports_betting_coordinator.py`, `core/tasks_content.py` (Cat D scope), `core/tasks_financial.py` Cat D functions, `core/services/discord_bot.py` `/odds` command area.

**Anchor:** S1274 §14 Finding #6 (HIGH) — `sports_odds` not a `SignalCluster.pattern_type`. Consumer side (Cat D) extends the gap.

Cat D signals live only in:
- Discord embeds (`send_betting_digest` output, ephemeral)
- `SportsBettingBrief` JSONField blobs (write-only)
- `LegacySpiderData.raw_data` blob with `spider_name='betting_coordinator'` sentinel

**F11 fold Rigby SIGN cycle 1 batch 3 Q8 — no owning bridge implementation was located:** Grep verified — no signal-emission bridge exists that publishes Cat D top-plays / arbitrage / sharp-action to `SignalCluster`. The POSTURE-DECISION-PENDING framing is decision-pending because no bridge implementation has been built. Rigby batch 2 Q4 pressure-test rationale: "could be intentional separation, but currently unproven — audit doesn't show an owning bridge that actually emits on Cat D events."

**Cat F implication:** Same evidence-plan contribution as Finding 4 (POSTURE-DECISION-PENDING). Extends the Cat B / Cat C `sports_odds` gap into Cat D consumer side.

### 14.6 MED — `_impl_collect_sports_odds_intelligence` docstring channel-name drift (S1501 §1 Finding 5 inheritance)

**Docstring at `core/tasks_financial.py:1817`:**
```
Post trending sports odds to Discord #market-intelligence.
```

**Runtime reality:** `send_betting_digest()` hardcodes `CHANNEL_BOARDROOM` (parent-Claude verified). Same channel used by both digest + intelligence hook + brief posts. There is no `#market-intelligence` channel routing in the current code path.

**Severity MED** — documentation drift; operational impact low (posts still land somewhere). Inherited from S1501 §1 Finding 5.

### 14.7 MED — REST endpoints uniformly `AllowAny` (S1503 §14.7 pattern)

All 5 `/api/v1/betting/*` endpoints use `@permission_classes([AllowAny])`. No throttling, no authentication requirement. Matches S1503 §14.7 pattern across sibling audits — arc-wide REST auth uniformity for the betting surface. Not Cat D-specific finding; documented for arc-close inheritance to xx99.

### 14.8 LOW — `send_betting_digest` service method has fragile channel contract

Hardcoded `CHANNEL_BOARDROOM` — no channel parameter override, no config-driven channel selection. If Discord workspace re-topology moves the boardroom channel ID, every Cat D Discord post breaks silently. Low operational risk; would trip on infrastructure change only.

## 15. Known Technical Debt

Ranked by severity. Extends S1503 §15 pattern.

### 15.1 CRITICAL — Beat schedule missing for `daily_betting_digest` (see §14.1)

Add `daily-betting-digest` entry to `core/celery.py` beat_schedule OR add explicit deferral rationale to `docs/AUDIT_FINDINGS.md` §12. Pre-remediation gate: verify no docstring drift on other tasks in Cat D scope first.

### 15.2 CRITICAL — `SportsBettingBrief` consumer-or-remove decision (see §14.3)

Either (a) build a reader consumer (dashboard / API / PA tool that queries persisted briefs), or (b) remove the persistence path and document "brief output is Discord + REST ephemeral only." Currently 2 writers + 0 readers is dead-weight state. Compounding-risk: if Session 1000 also fires, deduplication logic missing.

### 15.3 MED (F6 fold Rigby SIGN cycle 1 batch 2 Q5 — demoted from HIGH) — Docstring cadence drift on `generate_daily_betting_brief` (see §14.2)

Update docstring to reflect once-daily cadence, OR add second beat entry for evening cron. Chris-gated at post-arc PR. F6 demote rationale: "less risky than 'doesn't run / duplicates / no tests / no consumers.'"

### 15.4 MED-HIGH — Two `SportsBettingBrief` writer paths without deduplication

Cat D shim (`_impl_generate_daily_betting_brief`) + Session 1000 multi-desk (`run_all_desks_intelligence`) both create rows on the same table without unique constraint on `brief_date`. Add either (a) `get_or_create` semantics with unique constraint, or (b) `source` column disambiguating Cat D vs Session 1000 writers. Compounding with §15.2 — until the consumer decision is made, duplicate rows accumulate.

### 15.5 CRITICAL (F5 fold Rigby SIGN cycle 1 batch 2 Q5 — promoted from MED-HIGH; matches S1503 §15.14 F7 fold pattern PRE-RESTORE-BEAT GATE) — `_impl_daily_betting_digest` idempotency + replay safety

When beat entry is restored (§15.1 remediation), digest must be idempotent + replay-safe. The task reads spider data + posts to Discord — no DB persistence means no natural idempotency guard. If the beat fires twice on the same morning, the Discord channel receives duplicate digests. Add task-level lock or `send_betting_digest` receipt check before beat restoration.

**Pre-restore-beat gate** — matches S1503 §15.14 F7 fold pattern (idempotency + replay-safety must land BEFORE beat restoration).

**F5 promote rationale (Rigby batch 2 Q5):** "Once you flip the beat back on, non-idempotency becomes the next highest-risk failure mode (spam/dup posts)." This is a CRITICAL tier PRE-RESTORE-BEAT gate — cannot land §15.1 (digest beat) without landing §15.5 first.

### 15.6 MED-HIGH — Absent Cat D → Cat B outcome-feedback loop (see §14.4)

POSTURE-DECISION-PENDING. Either build learning bridge or explicit document "no calibration loop by design."

### 15.7 MED — Absent Cat D → Signal Engine emission (see §14.5)

POSTURE-DECISION-PENDING. Load-bearing for Cat F evidence plan.

### 15.8 MED — `SportsBettingBrief` retention policy absent

No cleanup task, no TTL. Rows accumulate since Session 1003 (2026-02-14). Even at 1-2 rows/day the low-volume table is a growing operational blind spot. Add retention policy (default: 90d retain, purge older).

### 15.9 MED — Discord fast path bypasses `SportsContentContextBuilder` (see Finding 7)

Two disconnected content-generation surfaces. Consolidate under `SportsContentContextBuilder` OR document "Discord fast path uses direct spider reads by design." Chris-gated at post-arc PR.

### 15.10 MED — Absent Cat D → Memory Domain (S1300) bridge (see §14.4 sibling)

POSTURE-DECISION-PENDING per Finding 8.

### 15.11 MED — No PA operator surgical tool for Cat D triggers (Finding 10)

Add PA tool actions:
- Trigger brief regeneration (analogous to Cat C `intelligence_tool` extensions)
- Trigger digest dispatch (post-remediation of §15.1)
- Query `SportsBettingBrief` history (post-remediation of §15.2)

Matches S1503 §15.11 pattern.

### 15.12 CRITICAL (F4 fold Rigby SIGN cycle 1 batch 2 Q5 — promoted from MED-HIGH; matches "reliability multiplier" framing) — Zero test coverage for Cat D behavior (Finding 9)

Add:
- `test_sports_content_context.py` — cover `is_sports_topic`, `is_betting_topic`, `build_sports_context` with mock spider data
- `test_generate_daily_betting_brief.py` — cover coordinator invocation + persistence + safety-net trigger
- `test_daily_betting_digest.py` — cover digest generation (once §15.1 remediates)
- Minimal integration test for `/odds` command
- Regression test for `SportsBettingBrief` dedup once §15.4 lands

**F4 promote rationale (Rigby batch 2 Q5):** "Given this domain is mostly schedules + Discord hooks, lack of even minimal smoke tests is a primary reliability risk multiplier." Test coverage sits above SportsBettingBrief consumer-or-remove in the CRITICAL tier ordering per Rigby batch 3 Q7 F3 fold — "should sit above 'consumer-or-remove' if you want production-read pressure."

### 15.13 MED — Docstring channel-name drift `#market-intelligence` vs `CHANNEL_BOARDROOM` (see §14.6)

Update `_impl_collect_sports_odds_intelligence` docstring (`core/tasks_financial.py:1817`) to reflect actual `CHANNEL_BOARDROOM` target OR add channel routing that honors the docstring intent.

### 15.14 MED-LOW — Fragile channel constant contract (see §14.8)

Add channel parameter to `send_betting_digest()` OR document CHANNEL_BOARDROOM as the intended shared channel and add config-driven override for env-specific routing.

### 15.15 LOW — Docstring session lineage stale across Cat D surfaces

Session 558 → 891 → 995B → 1003 sessions cited in various Cat D docstrings; no consolidated ownership tag. Low priority; document owner at post-arc topic-doc landing.

### 15.16 4-item pre-brief mini-schema per debt item (D62 fold)

Fourth-sibling application. Applied selectively to the CRITICAL + HIGH tier where posture-decision-relevance is highest.

| Debt Item | (a) sports-only vs shared | (b) DBAO vs public | (c) integration — refactor vs extend | (d) island — isolation guarantees needed |
|---|---|---|---|---|
| 15.1 daily_betting_digest beat missing | Sports-only | Public — needs `sports` queue routing (already at settings.py:1563) | **EXTEND** — add beat entry + verify Procfile/Makefile parity (S1244 lesson) | **NONE** new — dormant state is orthogonal |
| 15.2 SportsBettingBrief consumer-or-remove | Sports-only | Public | **REFACTOR** — under integration, add reader (dashboard/PA/API); under island, remove writer path | **REFACTOR** — under island, explicitly delete persistence path |
| 15.3 generate_daily_betting_brief docstring | Sports-only | N/A (docs only) | **EXTEND** — update docstring OR add evening beat | **NONE** |
| 15.4 two writer paths dedup | Sports-only | Public | **REFACTOR** — add unique constraint or `source` column | **REFACTOR** — under island, ensure only one writer per date |
| 15.5 digest idempotency (pre-restore-beat gate) | Sports-only | Public | **EXTEND** — add task-level lock or receipt check | **NONE** — orthogonal to posture |
| 15.6 Cat D → Cat B outcome-feedback | Sports-only bridge (would be) | Public | **REFACTOR** — new bridge service required | **REFACTOR** — explicit documentation of "no loop by design" |
| 15.7 Cat D → Signal Engine emission | Sports-only bridge (would be) | Public | **REFACTOR** — add `sports_odds` to `SignalCluster.pattern_type` enum + writer | **REFACTOR** — explicit "no signal emission" documentation |
| 15.8 SportsBettingBrief retention | Sports-only | Public | **EXTEND** — add cleanup task | **EXTEND** — retention policy required regardless of posture |

## 16. Boundary Violations

- **Cat B ↔ Cat D coordination via mixed-method-name asymmetry (S1502 §1 Finding 3 inheritance):** `SportsBettingCoordinator._run_odds_analyst()` calls `.run()` on SportsOddsAnalyst; other 4 agents called via `.execute()`. Cat D `_impl_generate_daily_betting_brief` inherits the risk — if the coordinator's mixed asymmetry drops SportsOddsAnalyst's `AgentExecution` telemetry, Cat D brief output has a silent Cat B blindspot. Not Cat D-caused; Cat D-inherited.
- **Cat D `run_all_desks_intelligence` (Session 1000) crosses domain boundaries** — the multi-desk pipeline includes Sports desk (Cat D scope), Blockchain desk (out-of-scope), Stocks desk (S1273 §3.11 scope), Narrative desk (out-of-scope). The shared task is not Cat D-owned; it is a platform-wide desk orchestrator that Cat D shares ownership of the Sports desk persistence with.
- **`SportsContentContextBuilder` invocation chain crosses into blog/content pipeline** — the service lives in Cat D surface list but its consumers are `content_review_panel*.py` + PA. This means Cat D scope leaks into content-pipeline scope (potential Group 1600 boundary if opened). Parent §6.5 flags this as "Delegated to Group 1600 (Content / Deliverables / Publishing, if Chris opens it)."

## 17. Duplicate or Overlapping Systems

- **`SportsBettingBrief` model has two writer paths** — Cat D shim + Session 1000 pipeline (see Finding 6 / §15.4). Overlap without dedup.
- **`send_betting_digest` service method has two upstream callers** — one dormant (digest), one live (intelligence hook). Both write to same channel (`CHANNEL_BOARDROOM`).
- **Discord fast path vs blog slow path** — `_impl_daily_betting_digest` + `_impl_collect_sports_odds_intelligence` + `/odds` command read `TheOddsSpider` directly; `SportsContentContextBuilder` reads `TheOddsSpider` via lazy service with much richer context (platform betting stats + agent memory + advisor). Two content-generation paths, one lightweight (Discord) + one heavyweight (blog), NOT unified (Finding 7 / §15.9).
- **REST `get_betting_brief` vs persisted `SportsBettingBrief`** — REST live-generates via coordinator; persisted model has 2 daily writes; neither knows about the other. Effectively duplicate coordinator invocations on request time + beat time + Session 1000 desk time (up to 3 coordinator calls/day producing 3 brief outputs, only 2 of which persist).

## 18. Ownership Gaps

Per §9 Q25 (ownership clarity):

| Surface | Original owner (session origin) | Current owner (2026-07-02) | Ownership clarity |
|---|---|---|---|
| `SportsContentContextBuilder` | Session 891 | UNKNOWN — no `@owner` tag; consumers are content-review + PA | AMBIGUOUS |
| `generate_daily_betting_brief` | Session 995B | UNKNOWN — beat comment cites "MLB Run Line Desk spec 46332cee" | AMBIGUOUS — spec citation without owner tag |
| `daily_betting_digest` | Session 558 | UNKNOWN — likely orphaned since zero-fire | LIKELY ORPHANED |
| Discord `/odds` command | Session 558 | UNKNOWN | AMBIGUOUS |
| `_impl_collect_sports_odds_intelligence` | Session 558 | UNKNOWN | AMBIGUOUS |
| `SportsBettingBrief` model | Session 1003 | UNKNOWN — 2 writers (Cat D + Session 1000) share the table | CONTESTED |
| `send_betting_digest` service method | Session 558 | UNKNOWN | AMBIGUOUS |

**Cat D has no clear surface owner.** Ownership is inherited across sessions (558 → 891 → 995B → 1003 → 1205 → 1244) but not consolidated. Owed to xx99 (S1599) ownership resolution — Group 1400 xx99 established Employee OS ownership resolution precedent per S1499 §5 (post-arc phase inheritance).

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows. Extends S1503 §19 ordering pattern; applies F10 CRITICAL-tier reorganization from S1503 (CRITICAL #1 + #2 must land BEFORE downstream work).

### 19.1 CRITICAL priority (blocks Cat F evidence plan + Cat D production readiness) — F10 pattern applied + F8 fold Rigby SIGN cycle 1 batch 3 Q7 CRITICAL tier reordered

1. **`daily_betting_digest` beat-schedule remediation OR explicit deferral** (§14.1 / §15.1). Either land beat entry OR add to `docs/AUDIT_FINDINGS.md` §12 canonical deferred list with rationale. Pre-gate for #2. **Cannot land #1 without landing idempotency-safety hardening (#2) first per §15.5 F7 fold**.

2. **`_impl_daily_betting_digest` idempotency + replay safety** (§15.5). Task-level lock or receipt check must land BEFORE beat restoration. Session 1503 §15.14 F7 fold pattern applied. F5 fold Rigby batch 2 Q5 rationale: "Once you flip the beat back on, non-idempotency becomes the next highest-risk failure mode (spam/dup posts)."

3. **Zero test coverage as reliability-risk multiplier** (§14 Finding 9 + §15.12) — F4 fold PROMOTED to CRITICAL per Rigby SIGN cycle 1 batch 2 Q5 + batch 3 Q7 F3. Rationale: "Given this domain is mostly schedules + Discord hooks, lack of even minimal smoke tests is a primary reliability risk multiplier." Sits above consumer-or-remove decision because tests unlock verification of the CRITICAL Finding 1 + 2 remediations. Add `test_sports_content_context.py`, `test_generate_daily_betting_brief.py`, `test_daily_betting_digest.py`, minimal `/odds` integration test.

4. **`SportsBettingBrief` consumer-or-remove decision** (§14.3 / §15.2). Two writers + zero readers is dead state. Either build reader consumer OR remove writer path. Chris-gated. Compounding-risk with #5 dedup. F8 fold Rigby batch 3 Q7 F4 rationale: "Still critical for correctness/clarity, but less immediate than tests if you're restoring digest."

5. **Two writer paths dedup** (§15.4). Cat D + Session 1000 write to same table without unique constraint. Add unique index OR `source` column disambiguation. Downstream of #4 (schema decisions follow from consumer-or-remove verdict). F8 fold Rigby batch 3 Q7 F5 rationale: "Correct dependency ordering (decision → schema/unique/dedup)."

### 19.2 HIGH priority (blocks WORKING-tier promotion + informs CRITICAL work)

6. **Cat D → Cat B outcome-feedback loop posture decision** (§14.4 / §15.6). Load-bearing for Cat F evidence plan. Extends S1502 F3 / S1503 F9 precedents. Bridge-owned learning writes preferred as default posture pending Chris ratification. **F11 fold Rigby batch 3 Q8: no owning bridge implementation was located — decision-pending posture-choice, not intentional-delegation-with-evidence.**

7. **Operational cadence study** — verify `run_all_desks_intelligence` beat state + fire cadence to determine actual `SportsBettingBrief` write volume from Session 1000 path (F1 fold Rigby batch 1 elevation). Not audited this session; enumerated as follow-on. Verifies whether Finding 6 dedup risk is theoretical or actively producing duplicate rows.

8. **`/odds` + intelligence-hook runtime confirmation instrumentation** (F9 fold Rigby batch 3 Q8 addition). Celery SUCCESS counts do NOT prove Discord posts reached target channel with correct payload. Add: (a) Discord webhook receipt telemetry; (b) `/odds` command interaction success telemetry; (c) alerting on repeated Celery SUCCESS + Discord-side error. Unlocks WORKING-tier maturity promotion.

### 19.3 MED priority (unblocks island-posture path + operator ergonomics)

9. **`generate_daily_betting_brief` docstring cadence resolution** (§14.2 / §15.3) — F6 fold demoted from HIGH to MED. Docstring says 2×/day, runtime is 1×/day. Update docs OR add evening cron. Chris-gated. Reprioritized behind CRITICAL + HIGH tiers.

10. **`SportsBettingBrief` retention policy** (§15.8). Add cleanup task (default 90d retain) regardless of posture selection.

11. **PA operator tooling** (§15.11). Add PA tool actions for brief regen / digest dispatch / brief history query. Matches S1503 §15.11 pattern.

12. **Discord fast path vs `SportsContentContextBuilder` consolidation** (§15.9). Either unify content-generation paths OR document deliberate separation. F2 fold reframe: this is now bridge-choice between the two content-generation paths (HOT-PATH-CHOKE-POINT for content/PA vs BYPASSED for Discord), not just documentation gap.

13. **Timezone correctness on `SportsBettingBrief.brief_date`** — model uses `timezone.now().date()` at `core/tasks_content.py:3151`; CELERY_TIMEZONE = America/Denver means date rolls at midnight MT. Verify no drift with UTC-based downstream queries. Adjacent to S1503 §15.13 timezone-correctness debt.

### 19.4 MED-LOW priority (unblocks integration-posture path)

14. **Cat D → Signal Engine emission bridge** (§14.5 / §15.7). Requires S1274 §14 Finding #6 remediation (add `sports_odds` to `SignalCluster.pattern_type`) as pre-gate. Integration posture only. **F11 fold Rigby batch 3 Q8: no owning bridge implementation was located — POSTURE-DECISION-PENDING because bridge not built.**

15. **Cat D → Memory Domain (S1300) bridge** (§14.4 sibling / §15.10). Requires S1300 canonical summary + explicit sports learning-loop design. Integration posture only. Rigby batch 2 Q4 F3: "plausibly intentional separation (centralized memory writes), but still decision-pending."

16. **Content pipeline reconciliation with Group 1600** — if Chris opens Group 1600 (Content / Deliverables / Publishing), reconcile Cat D briefs vs mainline content pipeline (ClaimsPack / PublishGate / SelfBlog / Deliverable). Delegated per parent §6.5.

### 19.5 LOW priority

17. **Docstring lineage consolidation** (§15.15). Add `@owner` tags per Cat D surface.

18. **Channel constant contract hardening** (§15.14). Config-driven CHANNEL_BOARDROOM override.

19. **Docstring channel-name drift** (§14.6 / §15.13). Correct `#market-intelligence` mention in `_impl_collect_sports_odds_intelligence`.

## 20. Appendix

### 20.1 Files inspected

**Cat D scope surfaces (parent §3.D):**
- `core/services/sports_content_context.py` (411 lines)
- `core/tasks_content.py:3103-3208` (_impl_generate_daily_betting_brief)
- `core/tasks_financial.py:1815-1902` (_impl_collect_sports_odds_intelligence)
- `core/tasks_financial.py:1907-2048` (_impl_daily_betting_digest)
- `core/services/discord_bot.py:1108-1220` (/odds slash command)
- `core/tasks.py:6085-6210` area (Cat D task shims)
- `core/tasks.py:12086-12210` area (run_all_desks_intelligence Sports desk)
- `core/celery.py:770-797` (beat_schedule Cat D entries)
- `core/settings.py:735, 807, 1563` (TIME_ZONE + CELERY_TIMEZONE + sports queue routing)

**Cat D adjacent surfaces:**
- `core/services/sports_betting_coordinator.py` (~290 lines — Cat B-owned, Cat D calls)
- `core/services/discord_notifications.py:2053+` (Cat D-owned method on shared service)
- `core/services/domain_content_context.py:186-191, 580-610` (SportsContentContextBuilder consumer)
- `core/services/content_review_panel_v2.py:196-199` (DomainContentContextBuilder consumer #1)
- `core/services/content_review_panel.py:82-85` (DomainContentContextBuilder consumer #2)
- `core/services/unified_pa_entrypoint.py:476-482` (DomainContentContextBuilder PA lazy-load)
- `core/views_odds_sports.py:3237-3266` (get_betting_brief REST)
- `core/urls.py:3126-3130` (Cat D REST route registrations)
- `core/models_unified_system.py:18394-18428` (SportsBettingBrief model)
- `core/models_unified_system.py:3691` (LegacySpiderData shared model)

**Docs inspected (parent-Claude):**
- `docs/research/domains/sports/1500_sports_domain_scoping.md` (parent)
- `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md` (sibling P1)
- `docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md` (sibling P2)
- `docs/research/domains/sports/1503_sports_wager_tracking_outcome_verification_audit.md` (sibling P3)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§9, §11.2, §13, §14, §15, §16)
- `docs/research/ARCHITECTURE_INDEX.md` (§1.33 S1503 row precedent)
- `docs/handoffs/SESSION_1503_SPORTS_CAT_C_AUDIT.md` (immediate predecessor)
- `docs/AUDIT_FINDINGS.md` §12 canonical deferred-by-policy list
- `docs/topics/agent-system.md` (5 Cat B agents inventoried; zero Cat D mentions)

### 20.2 Explore sub-agent evidence sweep

Six parallel Explore sub-agents launched per playbook §13:

1. **Sub-agent 1 (Models + Persistence)** — inventory of `SportsBettingBrief`, `LegacySpiderData`, `PlacedWager/Leg/BettingStats`, `MLPrediction`, `OddsSnapshot`, `GameLineHistory`, `AgentExecution`, `Agent`, `Advisor` per Cat D read/write scope. Migration lineage. D62 mini-schemas per model.
2. **Sub-agent 2 (Services + Runtime Flows)** — `SportsBettingCoordinator` (290 lines), `DiscordNotificationService` (2319 lines), `SportsContentContextBuilder` (411 lines), lazy imports, god-service check, invocation flows, blog vs Discord vs DB path delimiter.
3. **Sub-agent 3 (APIs + Tools + Tasks + Commands)** — REST endpoints, PA tools (zero), Celery task beat states, Discord surfaces, WebSocket (zero), management commands (zero).
4. **Sub-agent 4 (Integrations + Cross-Domain)** — inbound consumers (zero for SportsBettingBrief), outbound dependencies to Cat A/B/C/Discord, missing bridges (Cat D → Cat B outcome, Cat D → Signal Engine, Cat D → Memory), Cat F evidence contribution.
5. **Sub-agent 5 (Docs + Prior Research)** — zero topic docs, zero narrative doc mentions, prior research inheritance from S1273 §3.10 + S1274 §14 Finding #6, sibling audit references.
6. **Sub-agent 6 (Drift + Debt + Ownership + Maturity)** — 3-axis drift probe on Cat D tasks, debt matrix ranked, ownership per §9 Q25, maturity hybrid verdict.

**Sub-agent errors caught pre-SIGN via parent-Claude verifier-loop (§20.4):**
- Sub-agent 1 overclaimed "SportsBettingBrief is Cat D-exclusive" — parent-Claude grep verified TWO writer paths (Cat D + Session 1000 run_all_desks_intelligence). Correction folded into Finding 6 + §15.4.
- Sub-agent 3 claimed "SportsBettingBrief model definition not found via grep" — parent-Claude verified model at `core/models_unified_system.py:18394`. Correction: model exists; §4.1 documents.
- Sub-agent 6 marked SportsContentContextBuilder invocation as UNKNOWN — parent-Claude grep resolved: 3 consumer surfaces via DomainContentContextBuilder (§7.6). Downgraded from UNKNOWN to TRANSITIVELY-COUPLED.

### 20.3 Grep patterns used

**Parent-Claude verifier-loop grep patterns (post-sub-agent, pre-SIGN):**
- `SportsBettingBrief` in `**/*.py` — verified model definition + write sites + zero reader sites
- `get_sports_content_context|SportsContentContextBuilder|DomainContentContextBuilder` in `**/*.py` — verified invocation chain
- `get_betting_brief|betting/brief|get_todays_games|get_sharp_action|get_ai_track_record|get_pipeline_status` in `**/*.py` — verified REST endpoint registrations
- `SportsBettingBrief|sports_content_context|betting_brief|betting_digest|sports_betting_coordinator|SportsBettingCoordinator` in `**/tests/**/*.py` — verified test coverage gap (1 marginal file)
- `purge|cleanup|retention|delete.*SportsBettingBrief` — verified no retention policy

**Sub-agent grep patterns (per each sub-agent's brief):**
- Model inventory greps per sub-agent 1
- Service invocation greps per sub-agent 2
- Beat entry + AUDIT_FINDINGS §12 greps per sub-agent 3
- Integration reads/writes greps per sub-agent 4
- Doc / topic / narrative greps per sub-agent 5
- Docstring cadence + drift greps per sub-agent 6

### 20.4 Verifier-loop corrections (§14 evidence rule)

Per playbook §14 "trust but verify" pattern applied at parent-Claude synthesis layer BEFORE Rigby SIGN routing:

1. **Correction 1:** SportsBettingBrief writer count — sub-agent 1 said "exclusive"; parent-Claude grep found 2 writers. Folded into Finding 6 + §15.4.
2. **Correction 2:** SportsBettingBrief model existence — sub-agent 3 said "no model definition found"; parent-Claude verified at `core/models_unified_system.py:18394`. Folded into §4.1.
3. **Correction 3:** SportsContentContextBuilder invocation state — sub-agent 6 marked UNKNOWN; parent-Claude resolved via grep (3 consumer surfaces through DomainContentContextBuilder). Folded into §5.1 + §7.6.
4. **Correction 4:** `get_betting_brief` REST behavior — sub-agents 3 + 4 disagreed on whether it reads from model or re-invokes coordinator. Parent-Claude Read at `core/views_odds_sports.py:3235-3266` verified: coordinator direct-call, model bypassed. Folded into Finding 2 + §3.3.

### 20.5 Rigby ORM probe log — CRITICAL classification evidence-doubled BEFORE SIGN (S1503 pattern replicated)

Cat D applies S1503-first-applied Rigby-ORM-probe-BEFORE-draft-integration pattern as **second application** across the arc. Probes ran on Group 1500 arc pin `pa-791b3db549a64e54` before drafting §14.1 CRITICAL classification.

**Probe 1: `generate_daily_betting_brief` (parent §3.D claimed beat @ 07:00 MT):**
- Rigby ORM: `ops_tool.celery_task_history(task_name='core.tasks.generate_daily_betting_brief', days=30)` → `count=5`, events at `2026-06-30T13:00`, `2026-07-01T13:04`, `2026-07-02T13:00` UTC (= 07:00 MT).
- Verdict: **Beat CONFIRMED live**. Cadence matches crontab(hour=7, minute=0). Docstring "twice daily" NOT matched by runtime (Finding 5 / §14.2 HIGH).

**Probe 2: `daily_betting_digest` (parent §3.D listed in Cat D scope; no beat claim):**
- Rigby ORM: `ops_tool.celery_task_history(task_name='core.tasks.daily_betting_digest', days=30)` → `count=0`, `events=[]`.
- Parent-Claude complementary grep of `core/celery.py`: zero beat entries for `daily_betting_digest`.
- Parent-Claude complementary grep of `docs/AUDIT_FINDINGS.md` §12: zero matches — NOT on canonical deferred list.
- Verdict: **CRITICAL zero-fire pattern CONFIRMED** — matches S1503 §14.1 4-criteria classification exactly. Docstring at `core/tasks_financial.py:1912` claims "8 AM MST daily" = phantom.

**Probe 3: `collect_sports_odds_intelligence` (parent §3.D listed it):**
- Rigby ORM: `ops_tool.celery_task_history(task_name='core.tasks.collect_sports_odds_intelligence', days=30)` → `count=5`, events at `2026-07-02T14:30`, `15:00`, `15:30` UTC (consistent with 30-min cadence).
- Parent-Claude complementary grep of `core/celery.py`: beat entry `collect-sports-odds-intelligence` at line 787-791, `crontab(minute='*/30')`.
- Verdict: **Beat CONFIRMED live**. Cadence matches crontab. Docstring channel-name drift (`#market-intelligence` vs actual `CHANNEL_BOARDROOM`) is separate LOW/MED finding (§14.6 / §15.13).

**Second application of S1503-codification-candidate pattern:** parent-Claude Rigby-ORM-probe-BEFORE-SIGN. S1503 first applied for §14.1 CRITICAL. S1504 second application on the same Group 1500 arc pin. Pattern candidate for playbook v3 §14 evidence-rules addition — 2-arc evidence base at S1504 close; would strengthen to 3-arc evidence base at S1505 open if applied to Cat E surfaces (though Cat E has less beat-schedule scope).

### 20.6 Unresolved unknowns

1. **`run_all_desks_intelligence` beat state** — not audited this session. Presumed active per Session 1000 docstring but Cat D-scope audit does not confirm 30d fire cadence. Follow-on parent-Claude verification recommended (§19.2 #7).
2. **`_impl_daily_betting_digest` intent** — was it deliberately unscheduled at some past session (§14.1 §12 deferred rationale exists somewhere)? Or was the beat entry never landed? git blame + handoff archaeology would resolve, but out-of-scope for this session per playbook §14 no-implementation rule.
3. **SportsOddsAnalyst `.run()` vs `.execute()` asymmetry runtime impact on Cat D briefs** — S1502 §1 Finding 3 flagged this Cat B risk; Cat D inherits the silent-blindspot risk when the coordinator's mixed asymmetry drops AgentExecution telemetry. Not re-audited here; Cat B scope.
4. **Actual LLM provider identity for coordinator's per-agent LLM calls** — Cat B scope per S1502 §5.2.
5. **Whether `SportsContentContextBuilder` invocation via `DomainContentContextBuilder._get_sports_context()` actually reaches the content-generation surfaces** — invocation chain is proven at code level; runtime invocation frequency not measured (would require ContentReviewPanel + PA runtime telemetry).

### 20.7 Conflicts between sources

- **Sub-agent 1 vs parent-Claude on SportsBettingBrief ownership:** sub-agent 1 said Cat D-exclusive; parent-Claude verified TWO writer paths. Parent-Claude wins per §14 direct-source-verification rule.
- **Sub-agent 3 vs parent-Claude on SportsBettingBrief model existence:** sub-agent 3 said "not found"; parent-Claude verified at `core/models_unified_system.py:18394`. Parent-Claude wins.
- **Sub-agent 2 vs sub-agent 6 on SportsContentContextBuilder invocation:** sub-agent 2 said "called via ContentWriterAgent at line 486-509"; sub-agent 6 marked UNKNOWN. Parent-Claude verified: invocation flows through `DomainContentContextBuilder._get_sports_context()` at `core/services/domain_content_context.py:189-190`, consumed by `content_review_panel*.py` + PA — NOT directly through ContentWriterAgent line 486-509 as sub-agent 2 claimed. Sub-agent 2's specific citation was wrong; the invocation chain is real but through different consumers.
- **S1502 §7.1 F1-fold call-chain block for `generate_daily_betting_brief`** — Cat B version terminates at "brief dict return at line 96 to caller"; Cat D version extends the chain through persistence + safety-net (§7.1 above). Both consistent; Cat D extends.
- **Docstring `#market-intelligence` (`_impl_collect_sports_odds_intelligence` at `core/tasks_financial.py:1817`) vs runtime `CHANNEL_BOARDROOM`** — verified via `send_betting_digest()` implementation. Docstring wins on intent claim (channel name in docstring) but runtime wins on where posts actually land (`CHANNEL_BOARDROOM`). Finding tracked at §14.6 / §15.13.

### 20.8 Rigby SIGN fold notes — cycle 1 SIGN-with-edits at Medium-High confidence

**Fresh SIGN isolation pin:** `pa-af2bf7f2d1a0ef61` (retired at S1504 close via `session_tool.retire` per playbook §15 + memory rule).

**D48 preemptive stability-probe gate 7th arm result:** CLEAN. Warmup ping returned `cockpit_tool.worker_health` = 4 workers online, 0 active tasks, mixed pool composition (2 solo pool concurrency=1 + 2 thread pool concurrency=2). Zero worker-instability observed across all 4 substantive SIGN turns (batch 1 + batch 1 re-request + batch 2 + batch 3). Matches S1503 6th-arm cleanest arm pattern — 7th arm reinforces the 6-arc pattern → CODIFICATION-READY at 7-arc evidence base. Recommended for xx99 (S1599) §10.2 playbook v3 §15 codification.

**Full SIGN cycle 1 verdict verbatim (Rigby response to Q9):**

```
Cycle 1 close — Final: SIGN-with-edits, Medium-High confidence.
```

**Full SIGN cycle 1 pressure-test summary (Rigby responses across Q1-Q9):**

- Q1 (missed parts): 5 findings — REST endpoint accounted for (F1 not missed); `run_all_desks_intelligence` writer some underweight (F2); no additional read-surfaces (F3 not missed); content-review + PA as first-class downstream consumer slightly underweight (F4); LegacySpiderData emission worth elevating (F5).
- Q2 (overstated maturity): PARTIAL — `/odds` + intelligence-hook "working" claims are more "present/untested" without runtime proof beyond static pointers / Celery SUCCESS counts.
- Q3 (understated maturity): PARTIAL — SportsContentContextBuilder label fair for Cat D fast path but understated for content/PA subsystem where it's a choke-point + likely hot-path.
- Q4 (intentional vs missing integration): all 3 POSTURE-DECISION-PENDING findings correctly framed — "reads as 'not built / not wired,' not 'intentionally delegated with evidence.'" Memory Domain is "plausibly intentional but decision-pending."
- Q5 (debt ranking): CRITICAL Finding 1 correctly CRITICAL; Finding 2 borderline CRITICAL but defensible; PROMOTE zero test coverage → CRITICAL (reliability multiplier); PROMOTE digest idempotency PRE-RESTORE-BEAT → CRITICAL; DEMOTE docstring cadence drift → MED.
- Q6 (riskiest): #1 CRITICAL Finding 1 (digest zero-fire) — guaranteed "nothing happens" failure on promised surface; #2 CRITICAL Finding 2 (write-only-forgotten SportsBettingBrief); POSTURE-DECISION-PENDING = strategic risk not immediate reliability.
- Q7 (§19 CRITICAL tier reorder): (1) digest beat + (2) idempotency PRE-RESTORE + (3) test coverage + (4) consumer-or-remove + (5) two-writer dedup.
- Q8 (what Claude got wrong): 3 items — (F6) "owed to xx99" placeholder feel; (F7) `/odds` + intelligence-hook labeled WORKING without runtime proof; (F8) posture findings need "no owning bridge implementation was located" clarifier.
- Q9 (must change before canonical): SIGN-with-edits, Medium-High. 5 specific edits: tighten maturity labels; reorder §19 CRITICAL tier; replace "owed to xx99" language; add "no bridge located" to posture findings.

**F1-F11 folds landed at commit-time:**

- **F1 (Q1 batch 1)** — §1 Finding 6 executive summary reframed to elevate `run_all_desks_intelligence` as cross-domain writer bridge (not just "same target table"); §7.2 heading gained cross-domain writer bridge framing.
- **F2 (Q1 batch 1)** — §5.1 SportsContentContextBuilder invocation chain "Load-bearing observation" reframed from TRANSITIVELY-COUPLED to HOT-PATH-CHOKE-POINT for content/PA subsystem + BYPASSED by Cat D Discord fast path; three consumer surfaces (content_review_panel_v2, content_review_panel, unified_pa_entrypoint) marked FIRST-CLASS DOWNSTREAM CONSUMER.
- **F3 (Q1 batch 1)** — §4.2 LegacySpiderData shared-table pattern elevated with "meaningful Cat B/C bridge surface risk" + "REFACTOR-required blocker under island posture" language + Cat F posture-decision impact.
- **F4 (Q5 batch 2)** — §1 Finding 9 zero test coverage promoted from MED-HIGH → HIGH in executive summary + §15.12 promoted → CRITICAL + §19.1 #3 added to CRITICAL tier per "reliability multiplier" framing.
- **F5 (Q5 batch 2)** — §15.5 digest idempotency PRE-RESTORE-BEAT gate promoted from MED-HIGH → CRITICAL + §19.1 #2 sequence-gate before §19.1 #1 remediation.
- **F6 (Q5 batch 2)** — §1 Finding 5 + §14.2 + §15.3 docstring cadence drift demoted from HIGH → MED across all three sites + §19.3 #9 reprioritized behind CRITICAL + HIGH tiers.
- **F7 (Q6 batch 2)** — §1 executive-summary risk ordering strengthened: Finding 1 top-risk, Finding 2 close-second, POSTURE-DECISION-PENDING as strategic-not-immediate risk.
- **F8 (Q7 batch 3)** — §19.1 CRITICAL tier reordered to 5 items in correct dependency ordering: (1) digest beat + (2) idempotency + (3) test coverage + (4) consumer-or-remove + (5) two-writer dedup.
- **F9 (Q8 batch 3)** — §13 maturity verdict + §1 exec summary maturity verdict + §13.2 table refined to distinguish WORKING (fire-verified) from PRESENT + SCHEDULED (runtime not verified beyond Celery SUCCESS counts) for `/odds` + intelligence-hook; §19.2 #8 new operational instrumentation task added.
- **F10 (Q8 batch 3)** — §1 executive-summary "Ten load-bearing findings owed to xx99 (S1599) via Cat F evidence plan" opening rewritten to name concrete handoff target: "feed the Cat F posture-decision evidence plan (P6 — S1506 audit) and the xx99 canonical summary (S1599)" — removes placeholder feel.
- **F11 (Q8 batch 3)** — §14.4 + §14.5 both gained "no owning bridge implementation was located" clarifier per Rigby batch 2 Q4 rationale: "reads as 'not built / not wired,' not 'intentionally delegated with evidence.'" Additional callouts in §19.2 #6 + §19.4 #14 + §19.4 #15.

**Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** — pattern-consistent with S1501 + S1502 + S1503 cycle-1-predict-cycle-2 accuracy.

**Do-not-regress notes for post-fold PR:**

- Preserve §2.1 Cat D contract statement (10-item non-guarantee list) — do NOT backslide to "MISSING integration" defect language on POSTURE-DECISION-PENDING items.
- Preserve F1 fold `run_all_desks_intelligence` cross-domain writer bridge framing at §1 Finding 6 + §7.2 + §16 + §17 — do NOT backslide to "same target table" flat language.
- Preserve F2 fold SportsContentContextBuilder HOT-PATH-CHOKE-POINT framing at §5.1 + §7.6 + §13.2 — do NOT backslide to TRANSITIVELY-COUPLED (implies indirect / off-orbit).
- Preserve F3 fold LegacySpiderData shared-table Cat B/C bridge surface risk at §4.2 — do NOT drop the island-posture REFACTOR blocker language.
- Preserve F4 fold zero test coverage CRITICAL tier position at §19.1 #3 (above SportsBettingBrief consumer-or-remove) — do NOT let CRITICAL #3 land below CRITICAL #4/5.
- Preserve F5 fold digest idempotency as PRE-RESTORE-BEAT GATE ordering at §19.1 #2 — cannot land #1 (digest beat) without landing #2 (idempotency) first.
- Preserve F6 fold docstring cadence MED demotion at all three sites (§1 Finding 5, §14.2, §15.3, §19.3 #9) — do NOT re-elevate to HIGH.
- Preserve F8 fold §19.1 CRITICAL tier 5-item dependency ordering.
- Preserve F9 fold WORKING (fire-verified) vs PRESENT + SCHEDULED (runtime not verified) distinction at §13 + §1 maturity verdict — Celery SUCCESS counts are NOT semantic-correctness evidence.
- Preserve F11 fold "no owning bridge implementation was located" clarifier at §14.4 + §14.5 + §19.2 #6 + §19.4 #14/15 — do NOT re-frame POSTURE-DECISION-PENDING as "intentional delegation with evidence" when the bridge is NOT built.
- Preserve F10 fold concrete handoff-target language at §1 executive summary opening — do NOT re-introduce "owed to xx99" placeholder framing.

---

**End of Category D audit. 20-section child template complete. 4-item D62 pre-brief mini-schema applied per surface at §4.4, §5.6, §6.6, §8.6, §15.16 per fourth-sibling upfront-propagation pattern. Rank-order Cat F evidence contribution at §19. Rigby Full SIGN routing next per §15 stage table with D48 preemptive stability-probe gate.**
