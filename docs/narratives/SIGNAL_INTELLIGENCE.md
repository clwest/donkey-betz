---
title: "Signal Intelligence — narrative pilot (batch C)"
status: draft (batch C of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1 (Rigby, Session 1158)
companion_docs:
  - docs/topics/spider-network.md
  - docs/topics/initiative-pipeline.md
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/narratives/CONTENT_PIPELINE.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: HIGH (anchored to topics docs + named handoff files + PLATFORM_INVENTORY)
provenance_note: Batch C narrative. Covers the full signal chain — spiders → SpiderData → SignalCluster → AutoTopic → HiveMindSession → Initiative → 5-stage pipeline → Deliverable. Companion to AGENTS_AND_AUTONOMY (which produces work) and CONTENT_PIPELINE (which decides what to publish). This doc covers where work *comes from*. Counts anchored to PLATFORM_INVENTORY 2026-05-25 (git HEAD d513cd7f). Uncertainty labelled inline.
---

# Signal Intelligence

> Third companion narrative. The agent doc covered *what runs*;
> the content-pipeline doc covered *what the platform decides to
> publish*. This doc covers *where work comes from* — the path
> from raw spider data through clustering, topic generation, and
> initiative creation into the 5-stage execution pipeline. The
> shape is one long pipeline; the milestones are the points where
> the pipeline gained discipline, gained discipline, gained
> discipline.

---

## 1. What this is

The Signal Intelligence pipeline turns the open internet into the
platform's work queue. Spiders crawl sources across a couple
dozen categories (news, financial, tech, legal, education,
social, sports, weather, etc.); current counts are in
`PLATFORM_INVENTORY.md` (as-of 2026-05-25: 80 working spiders).
Their output lands in `SpiderData` rows with embeddings and
relevance scores. A scheduled job (`scan_spider_opportunities`)
aggregates the most recent window of data into `SignalCluster`
rows by topic and keyword — see the beat schedule entry for the
current cadence (as-of 2026-05-25: every 30 min, 72-h window).
Clusters above a minimum size become `AutoTopic` rows with
rationale and suggested agents. Topics that survive a
quality gate trigger a `HiveMindSession` — a multi-agent
conversation — which can produce an `Initiative`: a tracked
project with five execution stages and structured action items.
Initiatives that pass the 5-stage pipeline become Deliverables.

The pipeline is the platform's answer to "what should we even be
working on?". Without it, agents would only act when a human
typed a request. With it, the platform proposes its own work
based on what the world is actually doing — and then guards
against drowning in noise via circuit breakers, deduplication,
quality gates, and a TRIAGE intake before anything reaches the
active pipeline.

This doc is a chain narrative: each step exists because the
previous step exists, and each step's failure modes are the
reasons the next step's guards were added.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **Spider** | A collector. 80 are registered in `ai_core/spiders/spider_registry.py`. Each spider has a name, a category, a `Spider` class, a priority (1 or 2), and an HTTP method (RSS / API / JSON / Playwright). Output is normalized into `SpiderData` rows. ~1.14M `SpiderItemHash` rows record what was seen and when. |
| **`SpiderData`** | The raw collection row in `core.models_unified_system`. Carries `spider_name`, `source_url`, `data_type`, `raw_data` (JSON), `processed_data` (JSON), `relevance_score` (0–100), `insights` (JSON list), `embedding` (1536-dim pgvector), `item_embeddings`, `is_processed`, `is_actionable`. The `data_type` field is constrained to a fixed vocabulary (opportunity, job_posting, market_data, competitor_info, trend_data, news, research, etc.) — invented types like `market_alert` or `breaking_news` do not exist and will not match queries. **Common failure:** queries for `data_type='market_alert'` silently return empty; use `market_data` or `news` instead. Treat the `data_type` enum/CHOICES in code as canonical. |
| **`SignalCluster`** | The aggregated grouping. `SignalAggregationService.aggregate_signals()` extracts keywords/topics from the last 72h of `SpiderData`, groups by topic (primary) or keywords (secondary), filters clusters below `MIN_CLUSTER_SIZE=3`, and computes three metrics: strength, confidence, novelty. |
| **Strength / confidence / novelty** | Cluster metrics, each 0–1. Current weighting (as-of 2026-05-25): **strength** = signal count + source diversity + relevance (roughly 40/40/20); **confidence** scales with distinct source count (needs ≥ 2 sources to clear ~0.3); **novelty** decays over ~24h based on average signal age. The exact weights and formulas live in `SignalAggregationService.aggregate_signals()` — treat the function as canonical, not these ratios. Together they decide whether a cluster is worth promoting to a topic. |
| **Pattern types** | Currently 10 enumerated in `PATTERN_TYPE_CHOICES`. As-of 2026-05-25: demand_spike, trend_emergence, sentiment_shift, opportunity_window, knowledge_gap, competitive_signal, market_movement, skill_demand, content_gap, user_need. **Drift procedure:** if the topic doc / older audit says "7 pattern types," treat `PATTERN_TYPE_CHOICES` as canonical. Enum in code wins; docs mentioning 7 are stale. |
| **`AutoTopic`** | A promoted cluster. `generate_auto_topics()` reads clusters, applies a topic-name filter (Session 1010 — stopwords stripped: "new", "now", "how to", "want", "need", etc.; comma separator instead of "and"; falls back to cluster name when no meaningful keywords remain), and produces an AutoTopic row with rationale and suggested agents. |
| **`HiveMindSession`** | A multi-agent conversation triggered by an AutoTopic. Linked to the topic via FK + to the signal cluster via FK. Auto-selects relevant agents via `AgentRouter`. The discussion output is the basis for an initiative if the quality gate (Session 994) is passed. |
| **`Initiative`** | A tracked project. Carries `current_stage` (1–5), `purpose` (one of 5: revenue, stability, learning, expansion, maintenance), `program` (one of 10), `execution_track` (fast vs institutional), `owner` (human FK) or `owner_agent` (CharField), priority fields, and impact/urgency/confidence/revenue scores. |
| **5-stage pipeline** | Research Brief → Prototype Plan → Evaluation Protocol → Technical Design → Pilot Execution. The "Fast Track" stops at Stage 2 awaiting founder decision; the "Institutional Track" runs all five with approval gates at 2/3/4 and content-flag triggers (external_data, user_data, public_publishing, legal_compliance, financial, irreversible). |
| **TRIAGE status (Session 994)** | The intake state. Auto-created initiatives start in TRIAGE, not ACTIVE. The PA promotes TRIAGE → ACTIVE via `update_status`. Prevents auto-generated initiatives from polluting the active pipeline. |
| **Circuit breaker (Sessions 884, 994, 1020)** | Backlog throttle. When ACTIVE + TRIAGE initiatives with `last_activity_at IS NULL` exceed `INITIATIVE_BACKLOG_THRESHOLD`, new initiative creation is blocked. Enforced at all 6 creation paths. Cached 60s. **Drift procedure:** the env var is canonical; the topic doc references both 20 and 50 in different contexts. Before concluding "breaker too sensitive" or "breaker too loose," check the runtime value, not this prose. |
| **Similarity dedup (Session 1020)** | `find_similar_initiative()` in `initiative_circuit_breaker.py`. Jaccard keyword similarity at threshold 0.6. Pre-creation check on every path. Prevents the same topic from getting an initiative per agent run. |
| **Quality gate (Session 994)** | Pre-creation filter in `ConversationInitiativePipeline._quality_gate()`. Four rules: reject 2+ explore-pattern topics; require action verb in decision summary; require 1000+ char conversation; single-pattern explore check on topic prefix. |
| **`InitiativeActionItem`** | Structured task extracted from `=== DecisionSummary ===` sections in HiveMind conversation conclusions (Session 902). Carries status, priority, timeline (parsed from text like "Week 0-1"), agent + user assignment, dependencies (M2M to other items). |
| **Priority scoring** | `priority_score = impact_score × 0.4 + urgency × 0.2 + confidence × 0.2 + revenue_potential × 0.2`. Levels: critical ≥ 0.8, high ≥ 0.6, medium ≥ 0.4, low < 0.4. |
| **Semantic spider search (Session 1024)** | `SpiderIntelligenceService.search_spider_data()` uses pgvector `CosineDistance` KNN as primary mechanism. Constants: `SEMANTIC_TOP_K=50`, `SEMANTIC_MIN_SIMILARITY=0.25`. Falls back to keyword matching only when embeddings unavailable. `backfill_spider_embeddings` runs every 10 min in batches of 500; ~85% of `SpiderData` rows are embedded. HNSW index name: `spiderdata_embedding_hnsw_idx`. |
| **`_gather_initiative_research()` (Session 1021)** | Pre-stage research function. Queries `SpiderData`, `SignalCluster`, `AgentConversations`, and `Deliverables` for real data before calling `TechnicalDocumentAgent`. Closed the "agent makes up stage documents" class of bugs. |
| **`PROGRAM_OWNER_MAP` (Session 996)** | Auto-ownership mapping. content_pipeline → ContentStrategyAgent, growth_intelligence → MarketIntelligenceAgent, monetization → OpportunityScoringAgent, platform_health → SystemIntelligenceAgent, ai_capabilities → ThinkingAgent, infrastructure → DevOpsAgent, research/experiments → ResearchAgent. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Foundation — spider network + SpiderData** *(early sessions, Inferred)* | 80 spiders registered across ~18–41 categories (RSS, JSON, API, Playwright). Each writes to `SpiderData` rows with relevance scores, raw + processed JSON, and a constrained `data_type` enum. Default `data_type = 'research'`. The platform now has eyes on the open web. | The platform needed a continuous, structured feed of what the world was doing. Without it, all agent work would be triggered by humans typing requests. | 80 working spiders; ~1.14M `SpiderItemHash` rows tracked; structured data flowing into the unified data model. | **Active** — spider registry is still the canonical entry; the data_type vocabulary is enforced; 80 working / 0 placeholder per PLATFORM_INVENTORY 2026-05-25. | `docs/topics/spider-network.md`; `ai_core/spiders/spider_registry.py`; `docs/PLATFORM_INVENTORY.md` "Spiders" section |
| **Session 900 — signal intelligence provenance chain** | Full chain wired: `SpiderData` (72h) → `SignalAggregationService.aggregate_signals()` → `SignalCluster` (with strength/confidence/novelty) → `generate_auto_topics()` → `AutoTopic` (rationale + suggested agents) → `trigger_signal_driven_conversation()` → `HiveMindSession` (with `signal_cluster` FK + `auto_topic` FK) → `Initiative` (with full provenance). 10 pattern types enumerated. `scan_spider_opportunities` Celery task runs every 30 min. | The spider network was producing data, but nothing was *consuming* it autonomously. Without a path from raw spider items to platform action, the platform was reactive only. Session 900 made the signal chain a first-class autonomous primitive: the platform now proposes work to itself. | Every Initiative carries provenance — you can trace any active project back to the cluster, the topic, the conversation, and the spider items that justified it. `=== DecisionSummary ===` extraction makes the conversation's output structured. | **Active** — the chain is the canonical path from raw data to platform work; provenance FKs are still load-bearing. | `docs/topics/initiative-pipeline.md` §"Signal Intelligence (Session 900)"; `core/services/signal_aggregation_service.py`; `core/models_unified_system.py` (SignalCluster, AutoTopic) |
| **Sessions 884, 994, 1010, 1020 — guardrails (circuit breaker + quality gate + dedup + TRIAGE)** | (884) `INITIATIVE_BACKLOG_THRESHOLD` env-configurable circuit breaker; initial threshold 50. (994) TRIAGE intake state; quality gate (no 2+ explore-pattern topics; require action verb; require 1000+ char; explore-prefix check); activity tracking via `update_activity()`; flow_metrics tool. (1010) Topic quality gate — stopwords filtered in `_generate_topic_name()`; clusters with all-stopword keywords skipped entirely. Circuit breaker counts include TRIAGE (not just ACTIVE) for dedup. (1020) `find_similar_initiative()` with Jaccard keyword similarity at 0.6 threshold enforced at ALL 6 creation paths: `InitiativeIntegrationService`, `ConversationInitiativePipeline`, `HiveMindExecutionPipeline`, `DecisionExtractor`, `AgentDream.promote_to_initiative()`, `create_initiative_from_deliverables()`. | The signal chain was working too well — it was creating an initiative every time a topic surfaced again, the active pipeline was getting choked, and "explore the trending topic" topics were polluting the queue with shapeless work. Four separate guards were needed: a hard backlog limit, a quality bar to keep junk from entering, an intake state to separate raw triage from active work, and a similarity check to stop near-duplicates. | The active pipeline is now bounded — when the backlog exceeds the threshold, creation is blocked at the source, and dedup catches near-duplicates before they enter. TRIAGE gives the PA an explicit promotion step. Active + TRIAGE initiative counts are cached 60s; flow_metrics surfaces creation rate, backlog, stage distribution, and circuit-breaker status. | **Active** — all four guards are in production; backlog threshold lives in env (default 50, sometimes documented as 20). | `docs/topics/initiative-pipeline.md` §"Circuit Breaker (Session 884/994)", §"Quality Gate (Session 994)", §"TRIAGE Status (Session 994)"; `core/services/initiative_circuit_breaker.py` |
| **Sessions 902, 928, 996 — initiatives become tractable (action items + conversations + ownership)** | (902) `InitiativeActionItem` extracted from `=== DecisionSummary ===` sections. Status (pending/in_progress/completed/blocked/cancelled), priority (critical/high/medium/low), timeline parsed from text ("Week 0-1" → due_date), agent + user assignment, dependencies (M2M). Methods `start()`, `complete()`, `block(reason)`; properties `is_overdue`, `days_until_due`. (928) "Discuss with Agents" button creates `HiveMindSession` FK'd to initiative; injects full context (origin, stages, action items, signals). (996) Ownership: `owner` (human FK) or `owner_agent` (CharField). `PROGRAM_OWNER_MAP` auto-assigns by program (content_pipeline → ContentStrategyAgent, growth_intelligence → MarketIntelligenceAgent, etc.). PA commands: "show my initiatives", "unowned initiatives", "who owns [X]?", "assign [X] to [Agent]". | An initiative existed but wasn't yet a *plan*. There was no structured action breakdown, no way to revisit the conversation that justified it, no notion of who was supposed to be working on it. Three sessions filled the three gaps: action items make the plan structured; conversations make the rationale revisitable; ownership makes accountability assignable. | Initiatives now carry structured action items with timelines and dependencies; the PA can filter by owner and re-trigger conversations; auto-assignment rules cover the common case. | **Active** — all three are part of the standard initiative shape. | `docs/topics/initiative-pipeline.md` §"Action Item Tracking (Session 902)", §"Initiative Conversations (Session 928)", §"Ownership (Session 996)" |
| **Session 1021 — stage pipeline integrity (3 systemic bugs)** | Three bugs found and fixed in `advance_initiative_pipeline`. (PR #1250) **DRAFT stages silently skipped** — pipeline only matched `PENDING` stages without docs; after Session 1020 created docs for Stage 2+, DRAFT-status stages with existing documents were never approved. Fixed by adding DRAFT+document detection path. (PR #1251) **Future stage document generation** — the `range(1, 6)` loop generated documents for *any* pending stage regardless of whether prior stages were approved. Caused "rubber-stamping" where 4 stages got approved in 10 minutes with zero work. Fixed by anchoring to `init.current_stage` with prior-stage approval check. (PR #1252) **Garbage document content** — all Stage 1 and Stage 2 documents contained prompt-parrot output or random blog summaries. Root cause: `TechnicalDocumentAgent` called without `topic` or `research_context`, and has no tools to do research. Fixed by adding `_gather_initiative_research()` that queries `SpiderData`, `SignalCluster`, `AgentConversations`, and `Deliverables` for real data before calling the agent. | The pipeline could move stages forward but couldn't move them forward *with substance*. Three independent failure modes had been quietly producing garbage at scale. None were "the model is bad" — all three were "we asked the model to do something with no inputs and accepted what came out". | Pipeline now: (1) only processes `init.current_stage`; (2) verifies prior stage is `APPROVED`; (3) gathers real system data via keyword search before calling the agent; (4) injects real data into the task prompt with anti-hallucination instructions; (5) passes `topic` + `research_context` to agent context. Three separate PRs (#1250 / #1251 / #1252) — one bug each. | **Active** — `_gather_initiative_research()` is now the standard pre-stage call. | `docs/topics/initiative-pipeline.md` §"Stage Pipeline Integrity (Session 1021)"; PRs #1250 / #1251 / #1252 |
| **Session 1024 — semantic search migration** | `SpiderIntelligenceService.search_spider_data()` rewritten to use pgvector `CosineDistance` KNN as primary search. Constants: `SEMANTIC_TOP_K=50`, `SEMANTIC_MIN_SIMILARITY=0.25`. Backfill task (`backfill_spider_embeddings`, every 10 min, batch 500) walking unembedded rows. HNSW index named `spiderdata_embedding_hnsw_idx`. Model: OpenAI `text-embedding-3-small`, 1536 dims. ~85% of `SpiderData` rows have embeddings. | Keyword matching was producing high-relevance false positives — a HuggingFace page that mentioned "blockchain" once in a tag scored `relevance=1.0` for blockchain queries. Semantic similarity fixes the class of bug at the root (matching on *meaning*, not on string presence). | Search quality on real queries improved at the root; keyword matching remains as a fallback when pgvector or embeddings are unavailable. The embedding backfill task keeps coverage near-real-time. | **Active** — semantic KNN is the primary path; the keyword fallback is the second-best path, not the default. | `docs/topics/spider-network.md` §"Embeddings & Semantic Search (Session 1024)"; `core/services/spider_intelligence_service.py` |
| **Sessions 995, 998B, 1010, 1012 — sports-specific signal depth** | (995, 998B) `TheOddsSpider.fetch_scores(sport_key, days_from=3)` from `/v4/sports/{sport}/scores` — completed + in-progress games (Session 998B added live games; previously filtered out). Returns same `event_id` as odds data for direct joining. Consumed by `BettingOutcomeVerifier` for wager settlement and arbitrage verification. (1010) `GamePredictor._store_predictions()` auto-creates League → Team → Game → MLPrediction chain. Twenty-one `SPORT_KEY_LEAGUE` mappings (NFL, NCAAF, NBA, NCAAB, MLB, NHL, EPL, La Liga, Bundesliga, Serie A, Ligue 1, MLS, Champions League, Europa League, Liga MX, UFC/MMA, Boxing, etc.). Predictions > 14 days in future filtered out. `SharpActionDetector` classifies signals HOT (≥ 30 divergence) / WARM (≥ 15). (1012) `get_todays_games()` ESPN merge — fuzzy team-name substring match, adds period/clock/status_detail; AI track record dedup via `Max('id')` per `game_id` to prevent inflated W/L stats. | The sports domain has the platform's tightest verifiable feedback loop (a bet either wins or it doesn't). It needed its own deep signal-intelligence path: live game state, score settlement, prediction persistence, dedup of repeated predictions, and structured advice generation. Four sessions built that out. | The sports signal chain is end-to-end: spider gathers odds + scores, `GamePredictor` persists structured predictions, `SharpActionDetector` flags HOT/WARM divergence, the frontend merges live ESPN state, dedup keeps W/L stats accurate. | **Active** — `TheOddsSpider`, `GamePredictor`, `SharpActionDetector` are all in current routing. Session 998B's odds-consensus path was superseded by Session 1010's persistent `MLPrediction` records. | `docs/topics/spider-network.md` §"TheOddsSpider Score Fetching", §"Sports Prediction Persistence (Session 1010)", §"Today's Games ESPN Merge (Session 1012)", §"AI Track Record Dedup (Session 1012)" |
| **Session 1033 — dead state fix + first initiatives EVER completed** | All 3 ACTIVE initiatives were permanently stuck at Stage 2 with `status=IN_REVIEW` but *no document*. `advance_initiative_pipeline` only processed `PENDING`/`DRAFT` stages; `IN_REVIEW` without a document was an unrecoverable dead state. PR #1307 fixed two things at once: (1) extended the eligibility check to include `IN_REVIEW` + no-document — `if not stage or (stage.status in ('PENDING', 'DRAFT', 'IN_REVIEW') and not stage.document_id)`. (2) Rewrote `_get_next_task_for_agent()` which was referencing nonexistent fields (`InitiativeStage.assigned_agent` doesn't exist; `InitiativeStage.description` doesn't exist; `Initiative.title` should be `name`; status lowercase vs uppercase; wrong import path) — now queries PENDING stages with no document plus a PublishGate-backlog fallback. After the fix and a one-time data reset on Railway (reset 3 stuck IN_REVIEW records to PENDING), `advance_initiative_pipeline` was triggered manually. | The pipeline could create initiatives, deduplicate them, structure them, gather real research for them — but it had never actually finished one. The dead-state plus the broken next-task function were the last two barriers. | **Three initiatives completed the full 5-stage pipeline for the first time, ~3 minutes each** (each stage generated a real document via TechnicalDocumentAgent in ~45s using spider data + embeddings). Post-Session 1033 status: 3 COMPLETED / 0 ACTIVE / 17 TRIAGE. | **Active** — both fixes are in production. The IN_REVIEW eligibility path is now the standard. | `docs/topics/initiative-pipeline.md` §"Dead State Fix & First Completions (Session 1033)"; PR #1307 |

---

## 4. What came of it

### Wins

- **The platform proposes its own work.** The signal chain
  (Session 900) means the platform's queue is not gated on a
  human typing a request. Spider data continuously becomes
  clusters, topics, conversations, and initiatives.
- **Provenance is complete.** Every active initiative can be
  traced back through FKs to the HiveMind conversation, the
  AutoTopic with rationale, the SignalCluster with metrics, and
  the original SpiderData items.
- **Guardrails actually guard.** The circuit breaker + quality
  gate + similarity dedup + TRIAGE intake are enforced at *all
  six* creation paths. There is no "side door" to active
  initiatives that bypasses the guards.
- **Search is semantic.** pgvector cosine KNN replaced keyword
  matching as the primary search mechanism (Session 1024).
  False-positive relevance on "blockchain" tags is closed at
  the root.
- **Stage documents are grounded.** Session 1021 closed the
  "agent makes up stage content" class of bug by gathering real
  research first. The pipeline now passes `topic` and
  `research_context` explicitly.
- **The pipeline actually completes.** Session 1033 was the
  first time initiatives went through the full 5-stage pipeline
  with real documents — three completed in ~3 minutes each.
- **The sports domain has end-to-end verification.** The Odds →
  Scores → Verifier loop (995 / 998B) plus persistent
  predictions (1010) gives the platform a domain where claims
  can be settled against reality.

### Tradeoffs

- **Fast Track stalls at Stage 2 by design.** All initiatives
  default to `execution_speed='fast'`, and `can_auto_progress`
  returns `False` when `execution_speed=='fast' AND
  current_stage >= 2`. The result is "apparent gaps in the
  Activity Feed" — Celery runs every 10 min and finds nothing
  eligible. This is the *intended* behavior (founder gate at
  Stage 2) but is easy to mistake for a stuck pipeline.
- **Pattern-type count drift.** The spider-network topic doc
  still says "7 pattern types"; the canonical enum in
  `PATTERN_TYPE_CHOICES` has 10. Use the enum, not the topic
  doc, for code work.
- **Backlog threshold is documented inconsistently.** The
  initiative-pipeline topic doc references 20 (topic-quality
  gate context) and 50 (env default) in different places. The
  env var name `INITIATIVE_BACKLOG_THRESHOLD` is authoritative;
  the actual current value is whichever env wins at runtime.
- **Embedding coverage is ~85%.** The backfill task runs every
  10 min in batches of 500, so coverage is constantly chasing.
  Queries against unembedded items fall back to keyword
  matching silently — search behavior can vary depending on
  which rows happen to be embedded yet.
- **The 5-stage pipeline is heavy.** A full institutional run
  is five LLM-driven document generations plus approval gates
  at 2/3/4. Most current initiative work is Fast Track only —
  the institutional path exists but is not the common case.
- **TRIAGE has no automatic promotion.** Auto-created
  initiatives land in TRIAGE; only the PA's `update_status`
  call promotes them. If the PA isn't run, TRIAGE backs up.
  This is by design, but it means autonomous work generation
  requires a regular PA pass to materialize.

### Follow-on systems enabled

- **The agent system (`AGENTS_AND_AUTONOMY.md`)** depends on
  the signal chain for autonomy — agents that "wake up" from
  signal-driven conversations rather than from user requests
  trace through this pipeline.
- **The content pipeline (`CONTENT_PIPELINE.md`)** consumes
  `SpiderData` + active `SignalCluster` directly when building
  ClaimsPacks. Stale or low-quality clusters here become
  stale or low-quality content there.
- **The PA's `initiative_tool`** depends on the structured
  fields added across this arc (action items, ownership,
  flow_metrics, TRIAGE status).
- **The 5-stage Deliverable contract** — including the
  `publish_intent` enum (Session 1095, covered in
  `CONTENT_PIPELINE.md` milestone 8) — is built on top of this
  pipeline's output.

---

## 5. Current state snapshot

> Source for counts: `PLATFORM_INVENTORY.md` snapshot
> 2026-05-25 (git HEAD `d513cd7f`).

**Population.** 80 spiders registered, 80 working, 0 placeholder.
Top categories by count: tech=8, news=8, financial=7, legal=6,
education=4, content=3, community=3, startups=2, innovation=2,
design=2. Spiders needing API keys (per topic doc): SEC Edgar,
Bluesky, Discord, Spotify, YouTube.

**Spider output.** `SpiderData` rows in `core.models_unified_system`,
~1.14M `SpiderItemHash` rows tracked. Embedding coverage ~85% via
`text-embedding-3-small` (1536 dim) with HNSW index. Backfill task
every 10 min, batch 500.

**Signal aggregation.** `scan_spider_opportunities` Celery task
every 30 min. Window: last 72h of `SpiderData`. Min cluster size:
3. Cluster metrics: strength = sig_count·0.4 + source_div·0.4 +
relevance·0.2; confidence = source_count/4 (needs ≥ 2 for > 0.3);
novelty decays over 24h.

**Pattern types (canonical, 10).** demand_spike, trend_emergence,
sentiment_shift, opportunity_window, knowledge_gap,
competitive_signal, market_movement, skill_demand, content_gap,
user_need.

**Topic generation.** `_generate_topic_name()` strips stopwords
("new", "now", "how to", "want", "need", etc.); clusters with all
stopword keywords are skipped entirely; comma separator for
multi-keyword topics; falls back to cluster name when no
meaningful keywords remain.

**Quality gate (pre-initiative).** Four rules: reject 2+
explore-pattern topics; require action verb in decision summary;
require 1000+ char conversation; single-pattern explore check on
topic prefix.

**Circuit breaker (initiative creation).** Backlog = ACTIVE +
TRIAGE with `last_activity_at IS NULL`, cached 60s. Threshold:
`INITIATIVE_BACKLOG_THRESHOLD` env (default 50; topic doc
references 20 in topic-gate context). Enforced at all 6 creation
paths: `InitiativeIntegrationService.get_or_create_initiative()`,
`ConversationInitiativePipeline.process()`,
`HiveMindExecutionPipeline`,
`DecisionExtractor.auto_link_initiative_for_decision()`,
`AgentDream.promote_to_initiative()`,
`create_initiative_from_deliverables()`. Similarity dedup
(Jaccard, threshold 0.6).

**Initiative shape.** `current_stage` 1–5, `purpose` (revenue /
stability / learning / expansion / maintenance), `program` (10
programs), `execution_track` (fast | institutional), `owner` (FK)
or `owner_agent` (CharField), priority score = impact×0.4 +
urgency×0.2 + confidence×0.2 + revenue×0.2. Levels: critical
≥ 0.8, high ≥ 0.6, medium ≥ 0.4, low < 0.4.

**Execution tracks.**
- **Fast Track:** Stages 1–2 only; auto-progression *stops* at
  Stage 2 (`can_auto_progress` returns False when
  `execution_speed=='fast' AND current_stage >= 2`). Default for
  all new initiatives.
- **Institutional Track:** All 5 stages; approval gates at 2/3/4.
  Triggered by content flags (external_data, user_data,
  public_publishing, legal_compliance, financial, irreversible).

**Stage pipeline behavior (post-Session 1021).** Pipeline only
processes `init.current_stage` (no scan-ahead); verifies prior
stage is `APPROVED`; gathers real data via
`_gather_initiative_research()` querying SpiderData /
SignalCluster / AgentConversations / Deliverables; passes `topic`
+ `research_context` to agent context.

**Action items.** Extracted from `=== DecisionSummary ===`
sections. Fields: status, priority, timeline (parsed from
"Week 0-1" → due_date), agent + user assignment, M2M
dependencies. Methods: `start()`, `complete()`, `block(reason)`.

**PA initiative tool actions.** list, stats, details,
action_items, flow_metrics, update_status, advance,
complete_action_item, assign_owner.

**Where to look when something stops working.**
- No new initiatives in days → check `scan_spider_opportunities`
  beat (every 30 min); check spider data freshness (72h window);
  check circuit-breaker status via `initiative_tool flow_metrics`.
- Initiative stuck at Stage 2 → almost always Fast Track stall.
  Check `execution_speed`; the PA's "advance" action or a
  manual change to institutional unblocks it.
- Stage documents look like prompt parrots → pre-Session-1021
  state; check whether `_gather_initiative_research()` is being
  called. Should never happen on current code.
- Spider search returns junk → check embedding coverage for the
  topic domain; verify the query embedded; semantic threshold is
  0.25, top_k 50.
- Backlog growing without new active work → TRIAGE backlog. PA
  needs to promote `update_status` TRIAGE → ACTIVE.
- Duplicate-looking initiatives created → similarity dedup is
  Jaccard 0.6; if the threshold is being missed, the source
  keywords may have drifted enough to evade the check. Check
  `find_similar_initiative()` debug output.
- Sports predictions inflated W/L → AI track record dedup uses
  `Max('id')` per `game_id`; check the dedup query is actually
  being applied to whichever route is rendering the stats.

---

## 6. Open questions / unknown outcomes

- **What's the actual current `INITIATIVE_BACKLOG_THRESHOLD`?**
  *Known:* the env var is the authoritative source; topic doc
  references both 20 and 50 in different contexts. *Unknown:*
  the runtime value in current production. `os.environ.get(...)`
  or `SystemConfiguration` query would answer this. Worth
  documenting once.
- **Pattern-type drift.** *Known:* the topic doc references "7
  pattern types"; the canonical enum has 10
  (competitive_signal, market_movement, user_need added). The
  three additions are not session-cited in the topic doc.
  *Unknown:* which session added them. A `git log -S
  "competitive_signal"` against `PATTERN_TYPE_CHOICES` would
  surface it. Worth folding into the next topic-doc refresh.
- **Embedding coverage trajectory.** *Known:* ~85% per the
  topic doc. *Unknown:* whether coverage is climbing, holding,
  or losing ground to new spider data. The backfill task
  metrics would say.
- **TRIAGE drainage rate.** *Known:* TRIAGE is the intake state;
  only PA `update_status` promotes. Post-Session 1033 status was
  0 ACTIVE / 17 TRIAGE. *Unknown:* current count and whether
  TRIAGE is being worked through or accumulating. `flow_metrics`
  would answer.
- **5-stage institutional-track usage.** *Known:* Fast Track is
  the default; institutional triggers on content flags. *Unknown:*
  what percentage of initiatives have ever run institutional all
  the way to Stage 5. Session 1033 cited three Fast-Track
  completions; no institutional completions are recorded in the
  corpus this narrative covered.
- **`_gather_initiative_research()` quality.** *Known:* Session
  1021 added the function with keyword search over SpiderData /
  SignalCluster / AgentConversations / Deliverables. *Inferred:*
  it could probably benefit from the same semantic-KNN treatment
  Session 1024 applied to spider search. *Unknown:* whether
  there's an open ticket for this or whether it's been working
  well enough that nobody's asked.
- **Sports signal chain — is `BettingOutcomeVerifier` running on
  schedule?** *Known:* the verifier consumes
  `TheOddsSpider.fetch_scores()` output for wager settlement.
  *Unknown:* current cadence and last-run timestamp.
- **Similarity dedup at 0.6 — is the threshold right?** *Known:*
  Jaccard 0.6 on keyword sets. *Unknown:* false-positive vs
  false-negative rate in current production. Periodic audit of
  "near-misses" (keyword sets just below 0.6 that got separate
  initiatives) would inform whether to raise or lower.

---

## 7. Source index

### Primary doc sources

- `docs/topics/spider-network.md` — current-state topic doc for
  spiders + signal aggregation. Most session citations originate
  there.
- `docs/topics/initiative-pipeline.md` — current-state topic doc
  for the 5-stage pipeline. Covers Sessions 900–1033 in the
  initiative arc.
- `docs/PLATFORM_INVENTORY.md` — runtime-derived inventory; the
  authoritative source for spider counts (80 working, 0
  placeholder) and category distribution.
- `docs/narratives/AGENTS_AND_AUTONOMY.md` — companion narrative;
  cross-refs on autonomy and agent invocation paths.
- `docs/narratives/CONTENT_PIPELINE.md` — companion narrative;
  cross-refs on how ClaimsPack consumes SpiderData + active
  SignalCluster, and on the `publish_intent` enum (Session
  1095) layered on top of this pipeline's output.

### Named session handoffs cited above

- Session 900 — signal-intelligence provenance chain (referenced
  in `docs/topics/initiative-pipeline.md`; specific handoff file
  searchable as `SESSION_900_*`).
- `docs/handoffs/SESSION_900` series — signal chain.
- Session 902 — action item tracking (`InitiativeActionItem`).
- Session 928 — initiative conversations ("Discuss with
  Agents").
- Session 884 + 994 — circuit breaker, quality gate, TRIAGE,
  activity tracking, PA flow_metrics.
- Session 995 + 998B — `TheOddsSpider.fetch_scores()`.
- Session 996 — initiative ownership +
  `PROGRAM_OWNER_MAP`.
- Session 1010 — sports prediction persistence + topic quality
  gate (stopwords).
- Session 1012 — ESPN merge + AI track record dedup.
- Session 1020 — similarity dedup (Jaccard 0.6) added to all 6
  creation paths.
- Session 1021 — stage pipeline integrity (PRs #1250 / #1251 /
  #1252).
- Session 1024 — semantic search migration (pgvector cosine
  KNN).
- Session 1033 — dead state fix + first initiatives EVER
  completed (PR #1307).

### Code anchors

- `ai_core/spiders/spider_registry.py` — Spider registry (80
  spiders, categories, priorities).
- `core.models_unified_system` — `SpiderData`, `SignalCluster`,
  `AutoTopic`, `HiveMindSession`, `Initiative`,
  `InitiativeStage`, `InitiativeActionItem`.
- `core/services/signal_aggregation_service.py` — clustering +
  topic generation.
- `core/services/spider_intelligence_service.py` — semantic
  KNN search (Session 1024).
- `core/services/initiative_circuit_breaker.py` — circuit
  breaker + similarity dedup.
- `core/services/initiative_integration_service.py` — auto-
  ownership rules (`PROGRAM_OWNER_MAP`).
- `core/agents/markets/game_predictor.py` — `GamePredictor`
  (`SPORT_KEY_LEAGUE` mappings).
- `core/agents/markets/sharp_action_detector.py` —
  `SharpActionDetector` HOT/WARM classification.
- `core/tasks.py` — `scan_spider_opportunities`,
  `backfill_spider_embeddings`, `advance_initiative_pipeline`.

### Verification commands

- `python manage.py generate_platform_inventory` — regenerate
  the inventory anchor.
- `python manage.py verify_doc_claims --only-drift` — list
  which claims drift from runtime (Session 1099 verifier).
- `python manage.py build_docs_index` — refresh `docs/INDEX.md`
  + `_index.json` after any doc edit.

---

## 8. Canonical sources (for future editors)

> **Reading this doc for ops decisions?** Treat code and config as
> canonical, not prose. The narrative captures *why* the pipeline
> is the shape it is; runtime captures *what it is now*.

| Question | Canonical source (code/config wins over prose) |
|---|---|
| Spider count / categories | `docs/PLATFORM_INVENTORY.md` + `ai_core/spiders/spider_registry.py` |
| Pattern type values | `PATTERN_TYPE_CHOICES` enum in code (10 as-of 2026-05-25) |
| `data_type` vocabulary | Field CHOICES on `SpiderData` model |
| `INITIATIVE_BACKLOG_THRESHOLD` runtime value | Env var (NOT this prose — both 20 and 50 appear in docs) |
| Beat cadence (every 30 min, every 10 min, etc.) | `PeriodicTask` rows + `core/celery.py` schedule entries |
| Similarity dedup threshold (0.6) | Constant in `initiative_circuit_breaker.py` |
| `SEMANTIC_TOP_K`, `SEMANTIC_MIN_SIMILARITY` | Constants in `spider_intelligence_service.py` |
| Embedding model + dims (1536) | Provider registry config |
| Embedding coverage % | Live query (cited number is as-of snapshot) |

If you spot drift between this doc and code/config, **code wins**
and this doc should be corrected. See
[`docs/narratives/EDITING_GUARDRAILS.md`](EDITING_GUARDRAILS.md)
for the editing contract.

