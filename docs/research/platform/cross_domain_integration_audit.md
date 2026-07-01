---
title: "Cross-Domain Integration Audit — how domains connect, fail to connect, overlap, and violate boundaries"
status: draft
authority: research
session_added: 1274
last_verified: 2026-07-01
companion_anchors:
  - docs/research/platform_architecture_inventory.md   # 32-domain map (S1273 — parent)
  - docs/research/ARCHITECTURE_INDEX.md                # library navigation (v5)
  - docs/PLATFORM_INVENTORY.md                          # runtime counts anchor
  - docs/EVENT_SYSTEM_INVENTORY.md                     # 14+ event models catalogue
  - docs/EMPLOYEE_OS_PRIMITIVES.md                     # anti-duplication matrix
  - docs/AUDIT_FINDINGS.md                             # Celery deferred list
  - docs/research/governance_authority_evolution.md    # 4 governance planes
  - docs/research/actor_identity_attribution_architecture.md # 19 identity concepts
verifier_loop: |
  v2 (2026-07-01, S1274): Rigby SIGN-with-edits folded from fresh
  isolation pin `pa-7442a2e2665bd18e` (Medium confidence). Rigby
  independently grepped the codebase and caught two factual errors
  in v1: (1) **EventBus was mis-classified as "dormant."** Rigby
  found 5 publisher wrapper functions
  (`core/services/event_bus.py:539,559,596,619,643`) + at least one
  active caller (`core/services/scoring_dispatcher.py:21-40,282,480`
  → `publish_opportunity_scored_event`) + 3 consumer tasks
  (`core/tasks.py:4726,4760,4794` — `process_event_bus_scoring_queue`
  / `_validation_queue` / `_analytics_queue`) + queue routing
  (`core/settings.py:1315-1317,1579` → `broadcast` queue). Correct
  classification: "partially implemented, weakly adopted,
  unverified end-to-end." Not binary dormant.
  (2) **Direct OpenAI imports list was incomplete.** Rigby found 9
  files, ~15+ import sites (not 6 as v1 stated): `core/tasks_initiatives.py`
  (4 sites — 580, 1075, 1328, 1626), `core/tasks_conversations.py`
  (5 sites — 69, 1089, 1982, 2188, 2649), `core/services/ai_project_builder.py`
  (3 sites — 334, 410, 485), `core/agents/autonomous_content_studio_coordinator.py:733`,
  `core/services/unified_intelligence_search.py:85`,
  `core/services/discord_bot.py:7230,7713`,
  `core/models_unified_system.py:11795`, `core/views_time_capsules.py:601`,
  `core/tasks_content.py:834`. Original v1 sample was 6 files —
  wrong. Full sweep updated in §4.2 + §7.5.1 + risk matrix.
  Folded edits: (a) §1 exec summary rephrased EventBus finding
  from "dormant" to "partially implemented, weakly adopted"; (b)
  §2.8 EventBus row upgraded UNKNOWN → WEAK with cite; (c) §6.2
  rewritten as the concrete producer/consumer registry using
  Rigby-verified evidence; (d) §7.5.1 OpenAI list updated to 9
  files; (e) §11 risk matrix EventBus row updated CRITICAL → HIGH;
  (f) §12.3 Sports/AI Studio reframed as "product/architecture
  decision point with success criteria" (not "presumed defect");
  (g) §7 boundary violations re-ranked into "violates runtime
  policy/auditability" vs "just messy" buckets; (h) §12
  identity/actor attribution promoted from novel §12.4 to a
  cross-domain prerequisite spanning every write path (not just
  inter-employee dispatch). Two clarifications folded:
  Sports/DBAO framing sharpened, boundary-violation ranking
  clarified.
  v1 draft (2026-07-01, S1274): six parallel Explore sub-agents
  produced independent sweeps (imports/deps, model overlap, event
  flows, service boundary violations, ownership/extraction
  readiness, research-library cross-check). Parent (Claude)
  synthesized into 13-section integration audit. Every finding
  grounded in file:line cites OR flagged UNKNOWN/SPECULATIVE per
  mission-spec rules. Meta-check (Agent 6) drove scope discipline
  — this doc does NOT re-inventory the 22 attribution surfaces
  (S1271), 64-row collaboration primitives (S1268), 33-incident
  historical catalog (S1272), 4 governance planes (S1269), or
  32-domain map (S1273). Composes integration analysis across
  those existing inventories.
owner: claude (drafted S1274; Rigby SIGN-with-edits folded S1274; parallel-sweep evidence via 6 Explore sub-agents)
---

# Cross-Domain Integration Audit

> **What this is.** The **integration analysis** counterpart to
> `platform_architecture_inventory.md` (S1273). The inventory
> answered: "What domains exist?" This audit answers: "How do those
> domains connect, fail to connect, overlap, duplicate each other,
> or violate boundaries?"
>
> **What this is not.** Another domain inventory. A rewrite proposal.
> An implementation plan. An ADR (architecture decision record). All
> findings are evidence-first; unknowns are called out explicitly;
> speculative claims are flagged.
>
> **How to read.** §2 (Integration Map) gives the STRONG/WEAK/MISSING
> classification of every domain-to-domain pair. §3–§10 drill into
> each dimension. §11 is the risk matrix. §12 lists next research.
> §13 is the appendix (evidence trail, unknowns, conflicts).

---

## 1. Executive Summary

Six parallel Explore sub-agents surveyed the 32-domain platform for
integration failures at six dimensions: (1) missing cross-domain
connections, (2) overcoupled/leaky boundaries, (3) duplicate/overlap
data models, (4) missing event flows, (5) service-level boundary
violations, (6) dependency traps + extraction readiness + ownership.

**Biggest integration gaps.**

1. **EventBus is partially implemented, weakly adopted, and
   unverified end-to-end** (revised S1274 v2 per Rigby review —
   v1 mis-classified as "dormant"). Infrastructure at
   `core/services/event_bus.py:21-30`: 8 Redis Streams + 1 DLQ
   defined; 3 consumer groups registered; **5 publisher wrapper
   functions exist** at `event_bus.py:539,559,596,619,643`; **at
   least one active caller confirmed** —
   `core/services/scoring_dispatcher.py:21-40,282,480` publishes
   `EventStream.OPPORTUNITY_SCORED` after realtime + batch scoring;
   **3 consumer tasks defined** in `core/tasks.py:4726,4760,4794`
   (`process_event_bus_scoring_queue`, `_validation_queue`,
   `_analytics_queue`) + `get_event_bus_stats` at line 4874; queue
   routing at `core/settings.py:1315-1317,1579` → `broadcast`
   queue. What's missing is not the wiring — it's (a) system-level
   contract (what events are guaranteed, who owns them, what
   downstream effects must occur), (b) adoption rate across the
   other 4 streams (SPIDER_DATA, VALIDATION_REQUIRED /_DECIDED,
   OUTCOME_RECORDED — publisher wrappers exist but caller sweep
   incomplete), (c) end-to-end verification that produced events
   actually flow through consumers and generate observed platform
   effects in production. This is a coverage + observability +
   adoption problem, not a binary "off" state.
2. **9 missing event flows** cross critical domain boundaries.
   Most severe: mission completion → dashboard (Frontend polls
   every 15s instead of receiving push), deliverable-ready →
   notification (Web Push / Discord / inbox), critical failure
   cluster → HAI, LLM cost overrun → auto-freeze, spider drought
   → Platform Auditor.
3. **Sports/DBAO ↔ AI Studio pipeline gap** persists from S1273
   §3.10 — `sports_odds` is not a valid `SignalCluster` data_type;
   MLPrediction/PlacedWager do not feed initiatives or
   deliberation; BettingOutcomeVerifier outcomes are not flowed
   back to signal scoring. **Rigby S1274 correction:** frame this
   as a **product/architecture decision point** ("intentional
   island vs missing integration") with explicit success criteria
   for each posture — not as a presumed defect. See §12.3.

**Biggest boundary violations.**

1. **`discord_bot.py` is an 11,677-line god-service** with 96
   commands + 25 Cog classes + rate limiting + permission checks +
   voice streaming + Discord embeds all in one file (S1273 §3.20
   already flagged; this audit confirms scope of cross-domain
   reach).
2. **6+ files import `openai` directly** instead of
   `core/services/openai_client_factory.py` (memory-rule violation):
   `core/tasks.py:6961`, `core/views_image_gallery.py:23`,
   `core/views_image_generate.py`, `core/tasks_content.py`,
   `core/tasks_media.py` (4× occurrences), `core/channel_orchestrator.py`.
3. **`core/views_analytics.py:39-202`** does day-by-day ORM
   aggregation across Opportunity + Application + Revenue + AgentExecution
   models directly in the view layer — heavy business logic that
   belongs in an `AnalyticsService`.

**Intentional overlaps vs risky.**

- **Intentional (evidence-based):** 3-model execution audit trail
  (`AgentExecution` / `OpsRun` / `CeleryTaskEvent` — S1250 PR 3
  domain field enforces separation); 3-model per-call telemetry
  (`ToolCallRecord` / `LLMCallEvent` / `OpsRunEvent` — different
  grains, S861/S1098 docstrings cite rationale); 4-model
  content-artifact split (`Deliverable` / `SelfBlog` /
  `ExtractedArtifact` / `Document` — S819/S814/S555/S179 rationale
  documented); learning-bridge signal handlers (`revenue_
  attribution_bridge` and family — deliberate ABC pattern per
  S1115).
- **Risky (worth research):** 5+ memory stores (`AgentKnowledgeSource`
  / `AgentMemory` / `UserAgentLearning` / `ConversationMemory` /
  `MemoryPromotionService` auto-save) with unclear consolidation
  contract; three notification systems (Web Push / Expo / Discord)
  with no unified audit; two orchestration paths (Celery chain vs
  MissionRunner step loop) with no composition guarantee — S1268 F2
  says "do NOT mix" but does not detail what breaks if mixed.
- **Speculative or unknown:** `Initiative` vs `ActionPlan` vs
  `Dream` overlap needs S1274 clarification (Agent 2 flagged
  MEDIUM-HIGH consolidation risk); precedence between
  `GovernanceState`, `KillSwitch`, and `JobContract.authority` is
  implicit (S1269 §1 F3).

**Most isolated domains.**

- **`core/employees/mission_runner.py`** — intentionally imports
  nothing from `core.agents`, `core.services.tool_dispatcher`, or
  `intelligence` at module load. Callers inject step functions;
  MissionRunner is agnostic. HIGH extraction readiness (per Agent
  5).
- **`sports/` app** — self-contained models + dedicated queue; but
  isolation is a *failed integration*, not a virtue (S1273 §3.10
  gap).
- **`advisors/registry.py`** — in-memory only; no persistence; no
  API; injected as PA context. Isolated but ephemeral.

**Most tangled domains.**

- **PA (Rigby)** — 8-service enrichment pipeline; 152 tool handlers
  spanning 9 mixin sets; hub-and-spoke connection to every domain.
  Extraction is a "gateway refactor" (Agent 5), not an isolated
  extraction.
- **Governance** — 4 planes exist and don't compose (S1269 §1); 35
  runtime gates but zero enforcement readers for authority /
  KillSwitch. Rigby S1273 verdict quoted as "biggest architectural
  risk" — this audit confirms the entanglement is at contract level
  (not just missing wiring — the four planes were never designed to
  compose).
- **Observability** — 5 parallel execution telemetry layers
  (`CeleryTaskEvent`, `LLMCallEvent`, `AgentExecution`,
  `ToolCallRecord`, `OpsRunEvent`) plus 14+ event-shaped models
  (per `docs/EVENT_SYSTEM_INVENTORY.md`), all firing in parallel,
  no central intake, `RIGBY_EVENT_INTAKE_ENABLED=False` default.

**What should be researched next.** Ranked in §12. Top 3:

1. **EventBus Producer/Consumer Map (P0).** Non-negotiable — S1273
   §5 flagged this as blocking; S1274 audit confirms it *is* the
   single biggest observable integration gap.
2. **Notification Unification Study (P1).** Trace one signal event
   (arbitrage alert / deliverable ready / critical failure) through
   Web Push + Expo + Discord + Inbox + HumanAttentionItem to
   document delivery-guarantee differences and same-user
   triple-delivery risk.
3. **Sports ↔ AI Studio Integration Sketch (P1).** Whether sports
   outcomes should flow into signal clustering / initiative
   creation / deliberation, or whether the isolation is intentional
   (island architecture). This resolves S1273's biggest structural
   question.

---

## 2. Integration Map

Domain-to-domain connections classified across all 32 domains from
S1273 §2. Format below is the **connection type** per pair, not per
domain. Only connections where at least one direction is intentional
are shown; the absence of a row means no connection is expected.

**Legend.** STRONG = wired, tested, observed in production.
WEAK = wired but feature-flagged, opt-in, or minimal consumers.
MISSING = producer exists, consumer expected, no consumer found.
OVERCOUPLED = connection exists but crosses boundaries unsafely.
UNKNOWN = producer/consumer pairing not traced.

### 2.1 Cognition & Agents (domains 1–7)

| Source | Target | Class | Evidence |
|---|---|---|---|
| PA (1) | Traditional Agents (2) | STRONG | `run_agent` meta-tool via `AGENT_MAP` (`agent_router.py`) |
| PA (1) | AgentRouter (3) | STRONG | UnifiedPAEntrypoint dispatches via router |
| PA (1) | Boardroom/Advisors (6) | STRONG | `AdvisorContextBuilder` enrichment (Agent 2 confirmed) |
| PA (1) | LLM Providers (7) | STRONG | Via `openai_client_factory` + `anthropic_client_factory` |
| PA (1) | Employee OS (4) | WEAK | `employee_tool` read surface (describe / run_now / status); no live inter-employee messaging (S1268 F4) |
| PA (1) | Claude Code (5) | WEAK | 3-way conversation pattern; Claude Code responds autonomously to PA messages; no reverse dispatch |
| Traditional Agents (2) | AgentRouter (3) | STRONG | Router routes to `AGENT_MAP` entries |
| Traditional Agents (2) | LLM Providers (7) | STRONG | Via factories; **but 6+ files bypass factory** (Agent 4) → OVERCOUPLED |
| Traditional Agents (2) | Boardroom/Advisors (6) | MISSING | Advisors are prompt-context only; no reverse learning from advisor consultation → AgentLearning update (Agent 3) |
| Employee OS (4) | Traditional Agents (2) | WEAK | MissionRunner is agnostic; some employee jobs call agents but pattern is per-job |
| Employee OS (4) | Employee OS (4) inter-employee | MISSING | S1268 §5 documents; first candidate (Auditor → Chief of Staff) not built |

### 2.2 Data Ingestion & Intelligence (domains 8–10, 30)

| Source | Target | Class | Evidence |
|---|---|---|---|
| Spider Framework (8) | Signal Engine (9) | STRONG | `signal_aggregation_service.py` reads `LegacySpiderData`; entity-token v1 clustering (S1139) |
| Spider Framework (8) | Content Pipeline (11) | STRONG | ClaimsPack builder reads spider data (72h window) |
| Spider Framework (8) | Memory/Knowledge (13) | STRONG | `AgentKnowledgeSource` populated from spider data via LearningBridge |
| Spider Framework (8) | Revenue Pipeline (32) | STRONG | Opportunity scoring reads from spider results (via `intelligence/spider_decision_bridge.py`) |
| Spider Framework (8) | Sports/DBAO (10) | STRONG | TheOddsSpider is a spider — feeds sports pipeline |
| Signal Engine (9) | Initiative Pipeline (12) | WEAK | AutoTopic → Initiative auto-creation is UNCERTAIN (S1268 §10 Q2; S1273 §3.12 marked UNKNOWN) |
| Signal Engine (9) | HumanAttention (16) | MISSING | No pattern-strength threshold consumer (Agent 3 §2.9); high-confidence patterns don't auto-escalate |
| Sports/DBAO (10) | Signal Engine (9) | MISSING | `sports_odds` is not a valid `SignalCluster` data_type track (S1273 §3.10) |
| Sports/DBAO (10) | Content Pipeline (11) | MISSING | Sports predictions do NOT auto-create Initiatives or Deliverables |
| Sports/DBAO (10) | Revenue Pipeline (32) | MISSING | Betting outcomes not fed to opportunity attribution |
| Body Systems (30) | Governance (23) | MISSING | Body Coordinator reads 9 systems but emits no autonomic actions (side-effect-free, S1273 §3.30 drift) |
| Body Systems (30) | HumanAttention (16) | MISSING | HeartBeat rows accumulated; no consumer; no HAI on IMMUNE/DIGESTIVE degradation |

### 2.3 Content & Workflow (domains 11–12)

| Source | Target | Class | Evidence |
|---|---|---|---|
| Content Pipeline (11) | Deliverable (11 self) | STRONG | Deliberation runner writes SelfBlog; PublishGate enforces intent |
| Content Pipeline (11) | Initiative Pipeline (12) | STRONG | conversation_initiative_pipeline.py bridges (Agent 4 flagged as acceptable intentional coupling) |
| Content Pipeline (11) | Inbox (17) | MISSING | Deliverable status → notification (Web Push / Discord / inbox) — no wire (Agent 3 §2.2) |
| Content Pipeline (11) | PA (Rigby intake, 1) | WEAK | DeliverableEvent → rigby_event_intake gated by `RIGBY_EVENT_INTAKE_ENABLED=False` (Agent 3 §3.1) |
| Initiative Pipeline (12) | Content Pipeline (11) | STRONG | Initiative advance calls content_ideas_agent (Agent 5 evidence) |
| Initiative Pipeline (12) | Deliverable (11) | STRONG | 24h age gate → auto-progress stages 4/5 |
| Initiative Pipeline (12) | Frontend Dashboard (18) | WEAK | Frontend polls `/api/home/active-work/`; no push |

### 2.4 Revenue Pipeline (domain 32)

| Source | Target | Class | Evidence |
|---|---|---|---|
| Spider (8) → Opportunity | Revenue Pipeline (32) | STRONG | `intelligence/spider_decision_bridge.py`; `OpportunityScoringAgent` |
| Revenue Pipeline (32) | Initiative Pipeline (12) | MISSING | No revenue-threshold → auto-Initiative trigger (Agent 3 §2.6) |
| Revenue Pipeline (32) | Observability (25) | STRONG | `ImpactEvent` records revenue (`ops_autopilot/impact.py:375+`) |
| Revenue Pipeline (32) | Inbox (17) | MISSING | Outreach outbound channel is UNKNOWN (Agent 2 §10 flag; S1273 §10.3) |
| Revenue Pipeline (32) | HumanAttention (16) | MISSING | No auto-HAI when opportunity requires human approval (Agent 3 §2.6) |

### 2.5 Knowledge & Memory (domains 13–15)

| Source | Target | Class | Evidence |
|---|---|---|---|
| Documentation (15) | RAG (14) | STRONG | 4-step cascade: build_docs_index → build_rag_corpus → sync_docs_index_to_documents → embed_documents (memory rule) |
| RAG (14) | PA (1) | STRONG | `search_docs` PA tool + `kb_tool` |
| RAG (14) | Traditional Agents (2) | STRONG | `_get_relevant_knowledge_for_task` in BaseAgent context injection |
| Memory (13) | PA (1) | STRONG | AgentMemory injected via StrategicMemoryService |
| Memory (13) | Traditional Agents (2) | STRONG | 14-day freshness window in `ConversationOrchestrator` |
| HumanAttention (16) | Memory (13) | STRONG | FeedbackProcessor → AgentLearning + LearningInsight (Agent 3 §2.7 — only round-trip w/ learning) |
| Memory (13) | UserAgentLearning (13) | OVERCOUPLED | `HumanPreference.topic_weights / source_weights` set in memory but NEVER SAVED (S1269 F5, confirmed Agent 3) |

### 2.6 Human Interface (domains 16–21)

| Source | Target | Class | Evidence |
|---|---|---|---|
| HumanAttention (16) | Memory (13) | STRONG | Round-trip learning (see §2.5) |
| HumanAttention (16) | Governance (23) | WEAK | Read-only; HAI consumes governance state but does not gate governance mode changes |
| Inbox (17) | Frontend (18) | STRONG | REST + WebSocket for message threads |
| Inbox (17) | Discord (20) | WEAK | discord_notifications.py exists; implementation UNKNOWN |
| Inbox (17) | Mobile (19) | UNKNOWN | Expo push wired at model level; UI unknown |
| Inbox (17) | Web Push | WEAK | Push notification service exists; no `DeliverableEvent → send_arb_alert` wiring found |
| Frontend (18) | PA (1) | STRONG | POST /api/pa/chat/ + 2s polling |
| Frontend (18) | WebSocket consumers | STRONG | 51 WebSocket routes wired |
| Mobile (19) | Everything | UNKNOWN | Models exist; UI + wiring unknown |
| Discord Bot (20) | Traditional Agents (2) | STRONG | 96 commands invoke agents; separate from PA chat surface |
| Discord Bot (20) | PA (1) | STRONG | `/ask` command routes to PA |
| Discord Bot (20) | Everything | OVERCOUPLED | Single 11,677-line file crosses 5+ domain slices (Agent 4) |
| Voice/Avatar (21) | Content Pipeline (11) | STRONG | ElevenLabs TTS for voiceover; Runway image-to-video |
| Voice/Avatar (21) | PA (1) | STRONG | ElevenLabs TTS for PA chat replies |

### 2.7 API + Ops (domains 22–28)

| Source | Target | Class | Evidence |
|---|---|---|---|
| API Layer (22) | Everything | STRONG | 1,857 URL patterns; 51 WebSocket consumers route to all domains |
| Governance (23) | Autonomy consumers | STRONG (partial) | 4 active consumers of freeze/safe_mode: spiders / signal aggregation / workspace pipelines / LLM enforcer (Agent 3 §4.6 confirmed) |
| Governance (23) | KillSwitch consumers | MISSING | KillSwitch write path exists; **zero dispatch enforcement consumers** (S1269 F2, confirmed) |
| Governance (23) | JobContract.authority consumers | MISSING | Authority observed via `_emit_authority_contract_event`; **not enforced** (S1269 F1, confirmed) |
| Governance (23) | PA (1) | MISSING | No warning-context injection into PA on budget-freeze active (Agent 3 §2.5) |
| Automation/Celery (24) | Everything | STRONG | 414 tasks route to 8 queues; observed via CeleryTaskEvent |
| Automation/Celery (24) | Observability (25) | STRONG | task_prerun/postrun/failure signals → CeleryTaskEvent |
| Observability (25) | Governance (23) | MISSING | LLM cost overrun not fed to auto-freeze (Agent 3 §2.11); failure-rate spike not fed to any autonomic reaction |
| Observability (25) | HumanAttention (16) | MISSING | No failure-cluster aggregator → HAI (Agent 3 §2.3) |
| Observability (25) | PA / Rigby intake | WEAK | DeliverableEvent → rigby_event_intake gated (default OFF) |
| Auth (27) | Everything | STRONG (with unsafe edges) | Token auth + staff/reviewer gates work; **VIP demo prompt-only + Fleet permissive fallback** are known holes (S1273 §3.27) |

### 2.8 Event Bus (domain 31)

*Corrected S1274 v2 per Rigby SIGN review. v1's binary "dormant"
classification was wrong; Rigby found real publishers + consumers.*

| Source | Target | Class | Evidence |
|---|---|---|---|
| `EventStream.OPPORTUNITY_SCORED` | `scoring_workers` group + `process_event_bus_scoring_queue` (`tasks.py:4726`) | WEAK | Publisher: `event_bus.py:559:publish_opportunity_scored_event`; caller: `scoring_dispatcher.py:21-40,282,480`; consumer task defined |
| `EventStream.SPIDER_DATA` | (consumer TBD — needs caller sweep) | UNKNOWN | Publisher wrapper: `event_bus.py:539:publish_spider_data_event`; call sites not exhaustively traced |
| `EventStream.VALIDATION_REQUIRED` | `validation_workers` group + `process_event_bus_validation_queue` (`tasks.py:4760`) | UNKNOWN | Publisher wrapper: `event_bus.py:596:publish_validation_required_event`; call sites not exhaustively traced |
| `EventStream.VALIDATION_DECIDED` | (consumer TBD) | UNKNOWN | Publisher wrapper: `event_bus.py:619:publish_validation_decided_event`; call sites not exhaustively traced |
| `EventStream.OUTCOME_RECORDED` | `analytics_workers` group + `process_event_bus_analytics_queue` (`tasks.py:4794`) | UNKNOWN | Publisher wrapper: `event_bus.py:643:publish_outcome_recorded_event`; call sites not exhaustively traced |
| `EventStream.SYSTEM_ALERT` | (consumer TBD) | UNKNOWN | `event_bus.py:686:publish_system_alert_event` function defined; call sites UNKNOWN |
| `EventStream.MODEL_TRAINED` | (consumer TBD) | UNKNOWN | Not verified in this pass |
| EventBus DLQ (`mi:dead_letter`) | Cleanup task | MISSING | No cleanup task found; `get_event_bus_stats` (`tasks.py:4874`) reads DLQ length but no consumer |

**Corrected finding.** The EventBus is **partially implemented,
weakly adopted, and unverified end-to-end** — not "dormant." The
producer/consumer contract is incomplete: 1 of 8 streams has
confirmed active publisher + consumer wiring; the other 7 have
publisher wrappers defined but caller sweep is incomplete and
consumer-side observability is absent. The missing work is a
**contract + adoption + verification study**, not a "wire it up
from scratch" mission.

---

## 3. Missing Connections

Detailed findings for domains that should talk but do not. Ordered
by severity.

### 3.1 Mission Completion → Frontend Dashboard (HIGH)

- **Source:** Employee OS (§3.4 in S1273). `MissionRunner.run()` →
  `emit_mission_verdict()` → OpsRunEvent(label='verdict_issued:certified')
  written to `core/models_ops_runs.py`. File:line:
  `core/employees/mission_runner.py:1530-1570`.
- **Target:** Frontend Command Center "Now" Hub → Active Work panel.
- **Missing connection:** No WebSocket broadcast on OpsRunEvent
  post_save. No Celery task dispatched on verdict_issued.
- **Why:** Users must see mission completion in the Active Work
  panel; today Frontend polls `/api/home/active-work/` every 15s
  (Agent 3 §2.1).
- **Current workaround:** Polling — up to 15s delay after mission
  completion.
- **Risk:** HIGH for time-sensitive missions; MEDIUM in general.
- **Evidence trail:** OpsRunEvent row persistent; no WS send in
  grep; no Celery consumer of verdict_issued events.

### 3.2 Deliverable Ready → Notification (HIGH)

- **Source:** Content Pipeline (§3.11). `Deliverable.status='ready'`
  → post_save signal writes `DeliverableEvent(event_type=
  'status_transition', direction='up')`
  (`core/signals/deliverable_status_signals.py:94`).
- **Target:** Web Push + Discord + Inbox + HumanAttentionItem.
- **Missing connection:** No handler reads DeliverableEvent and
  fans out to notification systems.
- **Why:** User must be informed proactively that their deliverable
  is ready; today they must open Workspace tab → "work" →
  "deliverables" and see it (Agent 3 §2.2).
- **Current workaround:**
  - `RIGBY_EVENT_INTAKE_ENABLED` feature flag (default OFF).
  - Even if ON, downstream handler doesn't call notification
    services — enqueues `rigby_event_intake` task which writes
    `RigbyWorkItem` (Agent 3 §3.1 flags this as unverified consumer).
  - Manual polling of Workspace UI.
- **Risk:** MEDIUM-HIGH.
- **Evidence:** DeliverableEvent row present; no notification wiring
  found in grep.

### 3.3 Critical Failure Cluster → HumanAttentionItem (HIGH)

- **Source:** Observability (§3.25). `CeleryTaskEvent(status='FAILURE')`
  rows accumulate; `OpsRunEvent(event_type='step_fail')` writes;
  `LLMCallEvent(error_type=*)` writes.
- **Target:** HumanAttention (§3.16). Should auto-create
  `HumanAttentionItem(urgency='critical', source_type='failure_cluster')`
  when a threshold is crossed (e.g., 50 failures / 5-min window).
- **Missing connection:** No aggregator service. Body Coordinator
  reads system states but emits no autonomic HAI (S1273 §3.30 drift
  confirmed by Agent 3).
- **Why:** Cascade failures (DB pool exhaustion, worker OOM,
  broker congestion) should page a human when they cross a
  threshold. Today, Platform Auditor runs daily — cluster failures
  may go 10+ minutes unnoticed (Agent 3 §2.3).
- **Risk:** MEDIUM (data-loss-adjacent; may amplify silent failures).
- **Speculative flag on threshold values** — no established SLO.

### 3.4 LLM Cost Overrun → Governance Budget Freeze (HIGH)

- **Source:** Observability (§3.25). `LLMCallEvent(tokens_in,
  tokens_out, model, provider)` rows accumulate per call
  (`llm_call_wrapper.py:195`).
- **Target:** Governance (§3.23). `GovernanceState(mode='freeze')`
  should auto-trigger when window cost exceeds daily budget.
- **Missing connection:**
  - `LLMCallEvent.cost_usd` field is **missing** (S1273 §3.26 drift
    confirmed — "External Integrations: no external API cost
    tracking").
  - No aggregator sums LLM cost by window.
  - No auto-freeze trigger reads that aggregate.
- **Why:** A reasoning-model call loop can silently cost $500+
  before an operator notices (Agent 3 §2.11).
- **Risk:** HIGH (unmitigated financial exposure).
- **Current workaround:** Manual operator intervention on
  `governance_tool.set_mode('freeze')`.

### 3.5 Spider Drought → Platform Auditor Alert (MEDIUM-HIGH)

- **Source:** Spider Framework (§3.8).
  `SpiderExecutionLog(status='error'|'timeout')` rows accumulate;
  `LegacySpiderData` inserts stop happening.
- **Target:** Employee OS Platform Auditor employee (§3.4).
  Should auto-escalate when spider network has near-zero returns
  over a threshold window.
- **Missing connection:** `core/services/diagnostics/trend_analysis_daily.py`
  may check spider volume, but delivery to Platform Auditor's
  runtime is UNKNOWN. No SpiderDrought event model exists.
- **Why:** Spider network outage might not surface for 24h until
  daily Trend task runs (Agent 3 §2.4).
- **Risk:** MEDIUM-HIGH (data pipeline invisibility).
- **Evidence trail:** SpiderExecutionLog rows; no aggregator for
  "spiders with zero results in 30-min window."

### 3.6 Budget Freeze → PA Tool Dispatch Warning (MEDIUM)

- **Source:** Governance (§3.23). Operator or auto-trigger sets
  `GovernanceState(mode='freeze')` via `governance_tool.set_mode()`.
- **Target:** PA (§3.1) enrichment context injection. Should inject
  a "budget freeze active" warning into every PA tool response so
  the user knows why tools may return degraded results.
- **Missing connection:** `LLMEnforcer` blocks non-critical LLM
  calls when `budget_freeze_active=true`, but returns an empty
  response with no message. Users experience silent tool failure
  (Agent 3 §2.5).
- **Why:** Silent failure erodes user trust in the platform.
- **Risk:** MEDIUM.
- **Evidence:** `core/llm_enforcer.py:200-260` reads
  `budget_freeze_active` but does not push warning message; PA
  context builder has no `governance_state_notice` enricher.

### 3.7 Revenue Opportunity → Initiative Suggestion (MEDIUM)

- **Source:** Revenue Pipeline (§3.32).
  `ImpactEvent(type='revenue', value_usd > threshold)` or
  high-confidence `OpportunityScoringAgent` result.
- **Target:** Initiative Pipeline (§3.12). Should auto-create a
  strategic Initiative when a high-value revenue opportunity is
  detected.
- **Missing connection:** No revenue-threshold trigger. No
  `OpportunityScoringAgent` result subscriber that creates
  Initiative. AutoTopic → Initiative path exists one-way but
  reverse (Opportunity → Initiative) is UNKNOWN (Agent 3 §2.6).
- **Why:** High-value signals may be lost without follow-up (Agent
  3 §2.6).
- **Risk:** MEDIUM (revenue leakage).
- **Speculative** on the threshold value — SLO not established.

### 3.8 Signal Pattern Threshold → HumanAttentionItem (MEDIUM)

- **Source:** Signal Engine (§3.9).
  `SignalCluster(pattern_strength > 0.9)` written.
- **Target:** HumanAttention (§3.16). Should auto-create
  `HumanAttentionItem(urgency='high', source_type='signal_pattern')`.
- **Missing connection:** SignalCuratorService routes to AutoTopic
  but has no pattern-strength threshold gate for auto-HAI (Agent 3
  §2.9).
- **Why:** Critical signal patterns (fraud detection, trend spike)
  may not auto-escalate.
- **Risk:** MEDIUM.
- **Speculative** on threshold — S1139 clusterer scores exist but
  no auto-HAI mapping.

### 3.9 Spider Dedup Collision → Data Quality Alert (MEDIUM)

- **Source:** Spider Framework (§3.8). `LegacySpiderData.dedup_hash`
  unique constraint fires (or collision detected).
- **Target:** HumanAttention (§3.16) or Ops Autopilot's Trend
  diagnostic.
- **Missing connection:** No `SpiderDedupCollisionEvent` model. No
  alerting service. Collisions are silently skipped or overwritten
  (Agent 3 §2.10).
- **Why:** Data quality drift (e.g., spider returning stale cache)
  invisible until downstream analysis.
- **Risk:** MEDIUM (data quality invisibility).
- **Speculative** — dedup strategy details UNKNOWN without deeper
  read of `LegacySpiderData` collision logic.

### 3.10 Advisor Consultation → AgentLearning (LOW)

- **Source:** Boardroom/Advisors (§3.6). Advisor consultation
  happens via prompt-context injection only (not callable).
- **Target:** Memory (§3.13). AgentLearning would benefit from
  advisor consultation feedback.
- **Missing connection:** Advisors don't emit consultation events;
  no learning bridge.
- **Why:** Advisor guidance is one-way (context injection); no
  learning from advice quality (Agent 3 §2.12).
- **Risk:** LOW (advisors not intended as full agents per S1268 F3).

### 3.11 Published Content → Analytics Tracking (MEDIUM)

- **Source:** Content Pipeline (§3.11).
  `DeliverableEvent(direction='up', to='published')`.
- **Target:** Analytics Service (missing today).
- **Missing connection:** Frontend `usePageTracking()` fires
  telemetry to Redis (fire-and-forget); no persistent
  `AnalyticsEvent` model correlates published deliverable with
  downstream traffic (Agent 3 §2.8).
- **Why:** Content performance metrics not persistent.
- **Risk:** MEDIUM (performance measurement invisibility).
- **Evidence:** `core/models_unified_system.py:19761` defines
  `ConversionEvent` but writer path unverified (Agent 3 §7).

---

## 4. Overcoupled Domains

Detailed findings for domains that talk too much or cross boundaries
unsafely. Ordered by severity.

### 4.1 `discord_bot.py` — 11,677 lines / 25 Cog classes / 96 commands (HIGH)

- **Offending module:** `core/services/discord_bot.py`.
- **Crossed boundaries:** Discord bot dispatch + rate limiting +
  permission checks + LLM calls + opportunity listing + application
  tracking + voice channel streaming + agent invocation +
  workflow execution — all in one file.
- **Why it matters:** Single-file monolith makes changes risky,
  testing hard, and blast radius huge. Agent 4 ranked this as top
  god-service.
- **Acceptable legacy vs debt:** DEBT. Refactor candidate. S1273
  §3.20 also flagged.
- **Speculative on severity:** HIGH from maintenance angle;
  LOW-MEDIUM operationally (works today).

### 4.2 Direct `openai` Imports Bypassing Factory (MEDIUM, memory-rule violation)

*Updated S1274 v2 per Rigby grep. v1 listed 6 files; Rigby found
9 files with ~15+ import sites.*

- **Offending modules (9 files, ~15+ sites confirmed by
  independent grep):**
  - `core/tasks_initiatives.py` — 4 sites (lines 580, 1075, 1328,
    1626)
  - `core/tasks_conversations.py` — 5 sites (lines 69, 1089, 1982,
    2188, 2649)
  - `core/services/ai_project_builder.py` — 3 sites (lines 334,
    410, 485)
  - `core/services/discord_bot.py` — 2 sites (lines 7230, 7713)
  - `core/tasks_content.py:834`
  - `core/agents/autonomous_content_studio_coordinator.py:733`
  - `core/services/unified_intelligence_search.py:85`
  - `core/models_unified_system.py:11795`
  - `core/views_time_capsules.py:601`
- **Additional sites from Agent 4 sweep, unverified in Rigby
  grep** (may include duplicates of above):
  - `core/tasks.py:6961` (`_generate_checklist_documentation`)
  - `core/views_image_gallery.py:23`
  - `core/views_image_generate.py`
  - `core/tasks_media.py` (4× occurrences)
  - `core/channel_orchestrator.py`
- **Crossed boundary:** LLM Provider Registry (§3.7). Memory rule
  `feedback_openai_client_factory.md` explicitly requires
  `get_openai_client()` for unified timeout/retry/cost tracking.
- **Why it matters:** Cost tracking gap (LLM cost visibility
  missing platform-wide), inconsistent timeouts (600s default), no
  central retry policy.
- **Acceptable legacy vs debt:** DEBT. Global search-and-replace
  candidate. A future audit should reconcile the two sweeps
  (Rigby's 9-file exact-cite list vs Agent 4's broader 6-file list)
  and produce one canonical enforcement pass.

### 4.3 `views_analytics.py` — Heavy ORM Aggregation in View Layer (MEDIUM)

- **Offending module:** `core/views_analytics.py:39-202`.
- **Crossed boundary:** View → Multiple domain models
  (Opportunity + Application + Revenue + AgentExecution) with N+1
  query loops.
- **Why it matters:** Business logic (day-by-day metrics computation)
  belongs in `AnalyticsService`; view should validate → call service
  → serialize.
- **Acceptable legacy vs debt:** DEBT. Refactor via extraction.

### 4.4 `views_content.py` — Direct ContentGeneration DB Writes (MEDIUM)

- **Offending module:** `core/views_content.py:100-164`.
- **Crossed boundary:** View → ContentGeneration state machine
  (PROCESSING → PROCESSED).
- **Why it matters:** State transitions belong in
  `ContentGenerationService`, not view logic.
- **Acceptable legacy vs debt:** DEBT. Small refactor.

### 4.5 `HumanPreference.topic_weights / source_weights` — Set but Never Saved (MEDIUM)

- **Offending module:** `core/models_human_interface.py:268-358`
  + `core/services/human_attention_lifecycle.py:200+`.
- **Crossed boundary:** In-memory mutation vs persistence.
  `update_learned_stats()` modifies fields locally; **never calls
  `.save()`**.
- **Why it matters:** Learned user preferences don't persist across
  service restarts; Redis loss → learning reset.
- **Acceptable legacy vs debt:** DEBT (documented as S1269 F5;
  confirmed by Agent 3 §2.7).
- **Severity:** MEDIUM — feature-incomplete rather than dangerous.

### 4.6 `conversation_initiative_pipeline.py` — Multi-Domain Bridge (LOW — INTENTIONAL)

- **Module:** `core/services/conversation_initiative_pipeline.py:30-155`.
- **Crosses:** Conversation → Initiative → Deliverable → Tasks.
- **Why it matters:** Cross-domain orchestrator.
- **Acceptable legacy vs debt:** ACCEPTABLE. This is an
  intentional bridge service with clear boundaries + graceful
  degradation via try/except on each step. Similar shape to
  `content_deliberation_runner.py` (Agent 4 confirmed).

### 4.7 `content_deliberation_runner.py` — Multi-Step Pipeline (LOW — INTENTIONAL)

- **Module:** `core/services/content_deliberation_runner.py:1-150`.
- **Crosses:** ClaimsPack + ContentWriter + Blog + DeliberationSession
  (4 domains).
- **Why it matters:** Central orchestrator for content deliberation
  pipeline.
- **Acceptable legacy vs debt:** ACCEPTABLE. Try/except per step
  supports graceful degradation. Well-scoped orchestrator.

### 4.8 Learning-Bridge Signal Handlers (LOW — INTENTIONAL)

- **Modules:** `core/learning_bridges/revenue_attribution_bridge.py:22-28`,
  `core/signals/document_processing_signals.py`.
- **Crosses:** Revenue → UserAgentLearning; Document → NarrativeShift.
- **Why it matters:** Deliberate ABC pattern per S1115 migration
  (`LearningBridge` base class).
- **Acceptable legacy vs debt:** ACCEPTABLE. Documented pattern,
  migration path exists.

### 4.9 `unified_pa_entrypoint.py` — 7,613 lines (MEDIUM — GATEWAY)

- **Module:** `core/services/unified_pa_entrypoint.py`.
- **Crosses:** Every domain (hub-and-spoke by design).
- **Why it matters:** PA is the platform's master orchestrator;
  size is expected but every function is a coupling risk.
- **Acceptable legacy vs debt:** ACCEPTABLE (gateway role) but
  worth extracting sub-services (MemoryInjectionService,
  ConversationStitchingService) per Agent 4 recommendation.

---

## 5. Duplicate / Overlapping Models

Detailed model overlap analysis. S1273 §5 already enumerated 8
duplicate/overlapping categories; this section adds the
**integration lens** — what breaks or works if the overlap is
resolved.

### 5.1 Execution Audit Trails (3 models — INTENTIONAL, MEDIUM risk)

- **Models:** `intelligence.AgentExecution` (`intelligence/models.py:587`)
  + `core.AgentExecution` (`core/models_unified_system.py:882` —
  DEPRECATED) + `OpsRun`/`OpsRunEvent` (`core/models_ops_runs.py:11,91`)
  + `CeleryTaskEvent` (`core/models_celery_telemetry.py:17`).
- **Shared concept:** Tracking "what executed and what happened."
- **Real difference:**
  - `intelligence.AgentExecution` — action-plan step execution
    scoped to `ActionPlan`.
  - `core.AgentExecution` — DEPRECATED (Session 287 redirect to
    intelligence variant); still has FK-based trace correlation.
  - `OpsRun`/`OpsRunEvent` — event-log architecture; S1250 PR 3
    added `domain` field to enforce ops vs mission separation.
  - `CeleryTaskEvent` — Celery-signal-driven; one row per task
    invocation.
- **Overlap risk:** MEDIUM. Intentional separation but three-model
  coordination adds query complexity. Deprecation of
  `core.AgentExecution` in progress (Agent 2).
- **What breaks if merged:** OpsRun domain field prevents ops-vs-
  mission overload; CeleryTaskEvent uses Celery signals not SDK
  wrappers; intelligence variant is ActionPlan-scoped.
  Consolidation would require: unified `domain` semantics, SDK
  wrapper for Celery, ActionPlan-scoped subclass.

### 5.2 Per-Call Telemetry (3 models — INTENTIONAL, LOW risk)

- **Models:** `ToolCallRecord` (`core/models_tool_calls.py:19` —
  S861 gap-fill) + `LLMCallEvent`
  (`core/models_llm_telemetry.py:30` — S1098 wrapper sink) +
  `OpsRunEvent` (per-step generic).
- **Real difference:** Grain (tool call / LLM call / ops step) +
  retention policy (LLMCallEvent survives AgentExecution cleanup,
  ToolCallRecord is FK-based, OpsRunEvent is domain-scoped).
- **Overlap risk:** LOW. Clear boundaries; each has explicit
  docstring rationale.
- **Integration implication:** Any cross-domain trace needs to
  correlate across all three via `execution_id` / `trace_id`.
  No unified trace-ID system found in grep.

### 5.3 Content Artifacts (4 models — INTENTIONAL, LOW risk)

- **Models:** `Deliverable` (`core/models_deliverables.py:1`) +
  `SelfBlog` (`core/models_unified_system.py:20611`) +
  `ExtractedArtifact` (`core/models_conversation_artifacts.py:22`) +
  `Document` (`content/models.py`).
- **Real difference:**
  - `Deliverable` — agent-authored envelope for marketplace
    (S819).
  - `SelfBlog` — system-authored meta-content (S814, S833, S862).
  - `ExtractedArtifact` — proposals from agent chat (S261
    explicit naming to avoid collision).
  - `Document` — generic RAG sink (S179, pgvector).
- **Overlap risk:** LOW. All 4 have session-note rationale
  documented.
- **Integration implication:** Cross-domain "content" queries
  (e.g., "all published outputs by agent X") need to UNION across
  these tables — no unified view exists.

### 5.4 Messaging / Attention (4 models — LOW-MEDIUM risk, precedence unclear)

- **Models:** `DirectMessage` + `MessageThread`
  (`core/models_messaging.py:21,99`) + `HumanAttentionItem`
  (`core/models_human_interface.py:20`) + `NotificationLog`
  + `PushSubscription`.
- **Real difference:**
  - `DirectMessage` — async conversation, user reads at leisure.
  - `HumanAttentionItem` — blocking review with urgency + status
    machine.
  - `NotificationLog` — push delivery audit.
  - `PushSubscription` — device binding.
- **Overlap risk:** LOW-MEDIUM. Clear semantic separation but no
  documented rule for "when does a push create an HAI?" (Agent 2
  flagged as SPECULATIVE).
- **Integration implication:** Three notification systems (Web
  Push / Expo / Discord) + Inbox + HAI = same user can receive
  the same alert 4-5 times through different channels. S1273
  §5.2 already flagged this; the integration audit confirms no
  deduplication service exists.

### 5.5 Identity Concepts (3-model core + 3-role vocabulary — INTENTIONAL, LOW risk)

- **Models:** `Agent` (`core/models_unified_system.py:378`) +
  `AIEmployee` (`core/employees/jobs.py:74` — frozen dataclass) +
  `AssistantProfile` (`core/models_assistant_profile.py:90`) +
  `AdvisorProfile` (`advisors/registry.py:75` — in-memory).
- **Real difference:** Different layers of the stack — DB catalog
  (Agent), frozen policy (AIEmployee), per-user config
  (AssistantProfile), in-memory advisor registry (AdvisorProfile).
- **Cross-reference:** S1271 catalogued 19 identity concepts + 22
  attribution surfaces. Do NOT re-do that analysis (per Agent 6
  pitfall #1).
- **Overlap risk:** LOW. Intentional layering per S1252.
- **Integration implication (novel for S1274):** For any
  cross-domain flow that crosses actor boundaries (e.g., Employee
  A → Employee B messaging), the actor identity in the message
  must specify all three roles from S1271 F11
  (executor_actor / sponsor_actor / principal_user). Neither
  `Agent`, `AIEmployee`, nor `AssistantProfile` alone carries this;
  the 3-role vocabulary composes across them.

### 5.6 Planning / Work Items (3 models — MEDIUM-HIGH risk, needs clarification)

- **Models:** `Initiative` (`core/models_document_registry.py:37`)
  + `ActionPlan` (`intelligence/models.py:16`) + `WorkspaceTrigger`
  (`core/models_skin_layer.py:798`).
- **`Dream`:** NOT FOUND as top-level class; only found in FK
  relationships (`DreamImplementation`, `DreamFeedbackPreference`,
  `DreamExploration`, `AgentDream` referenced in SelfBlog).
  **UNKNOWN whether Dream model exists.**
- **Real difference:**
  - `Initiative` — strategic portfolio work with 5-stage lifecycle,
    revenue_potential.
  - `ActionPlan` — tactical execution with steps + progress.
  - `WorkspaceTrigger` — event-reaction automation.
- **Overlap risk:** MEDIUM-HIGH (Agent 2 verdict). Strategic vs
  tactical distinction is intentional but blurred at the
  Initiative-4-stage-auto-progress boundary.
- **Integration implication (novel):** S1268 §10 Q2 flagged
  "AutoTopic → Initiative auto-creation" as UNCERTAIN; S1273 §3.12
  confirmed. If Initiative and ActionPlan have similar-but-different
  workflows, and one auto-creates from AutoTopic while the other
  doesn't, the platform may double-track work items.
- **Speculative:** Dream model may be under-implemented or
  aspirational.

### 5.7 Spider Data (4-model layering — INTENTIONAL, LOW risk)

- **Models:** `LegacySpiderData` + `SpiderExecutionLog` +
  `SpiderDataAnnotation` + `SpiderItemHash`.
- **Real difference:** Data + execution telemetry + agent annotation
  + dedup hash. Clean 4-layer separation.
- **Overlap risk:** LOW.
- **Integration implication:** No integration debt.

### 5.8 Memory / Documents / Embeddings (5+ models — MEDIUM risk)

- **Models:** `AgentMemory` + `AgentKnowledgeSource` +
  `UserAgentLearning` + `ConversationMemory` + `Document` +
  `DocumentEmbedding`.
- **Cross-reference:** S1273 §3.13 already inventoried. Do NOT
  re-inventory.
- **Overlap risk:** MEDIUM (Agent 2). Different scopes (agent
  global, agent per-user, generic RAG) but embedding strategy
  unclear.
- **Integration implication (novel):** Two RAG lanes (`rag_integration.py`
  pgvector vs `rag.py` keyword local Ollama) — no documented
  call-time selector. If cross-domain retrieval crosses lane
  boundaries (e.g., an agent uses `rag_integration` while the
  local dev CLI uses `rag`), results diverge.
- **Missing data-consistency contract:** if `AgentMemory` learns
  something and `AgentKnowledgeSource` has an older version,
  which one wins at retrieval time? No documented resolution rule.

### 5.9 Governance Surfaces (4 models across 4 planes — OVERCOUPLED, MEDIUM risk, S1269 canonical)

- **Models:** `GovernanceState` + `KillSwitch` + `SystemConfiguration`
  budget flags + `JobContract.authority` dict.
- **Cross-reference:** S1269 §2 canonical — do NOT re-map.
- **Integration implication (novel):** **Precedence order is
  implicit.** If a JobContract says EXECUTE for docs_write, and
  GovernanceState is `freeze`, and KillSwitch targets `publishing`,
  and Budget freeze is active — which wins? What error message
  does the operator get? Agent 2 flagged this as speculative +
  MEDIUM risk.
- **Blocker note:** Symbol Mapping Option Selection (STAGE 3 per
  ARCHITECTURE_INDEX §9) is prerequisite to any composition
  research.

### 5.10 Outreach / Engagement / Meeting / Close (4 models — INTENTIONAL TIGHT COUPLING, LOW risk)

- **Models:** `OutreachDraft` + `EngagementEvent` + `Meeting` +
  `ClosePack`.
- **Cross-reference:** S1273 §3.32 added this domain post-Rigby
  S1273 review.
- **Real difference:** Pipeline stages (each FKs to predecessor).
  Intentional choreography.
- **Overlap risk:** LOW.
- **Integration implication (novel):** Risk is not merging — it's
  **orphaned records**. If ClosePack created without Meeting FK,
  pipeline broken. If Meeting exists without EngagementEvent
  trigger, orphaned. No integrity task audits this.

---

## 6. Event Flow Gaps

Detailed findings for events that should exist or flow but
currently do not. §3 covered specific missing connections; this
section maps the **broader event-flow topology**.

### 6.1 Producer / Consumer Registry for Existing Event Models

Agent 3 traced write/read sites for each live event model
(`docs/EVENT_SYSTEM_INVENTORY.md` §1 "Live, wired" list):

| Event Model | Producer(s) | Consumer(s) | Cross-Domain? |
|---|---|---|---|
| `CeleryTaskEvent` | `celery_telemetry.py:74,115,177` (signal handlers) | `views_diagnostics.py:828+`, `td_handlers_ops.celery_task_history` | NO — all consumers in Observability domain |
| `LLMCallEvent` | `llm_call_wrapper.py:195` | `employees/status.py:461`, `rigby_delegation_signals.py:102` | WEAK — read by Employee OS shift reports only |
| `ImpactEvent` | `ops_autopilot/impact.py:375,431,488` + `tool_dispatcher.py:1020` | `ops_autopilot/impact.py:582+,951+` (same domain rollups) | NO |
| `DeliverableEvent` | `deliverable_status_signals.py:94` | `coo_daily.py:474+` (rework gate), `views_deliverables.py:832` (UI), `rigby_event_intake` (gated by feature flag, default OFF) | WEAK (opt-in Rigby intake) |
| `OpsRunEvent` | `mission_runner.py:1530-1570` via `emit_mission_verdict()` | `employees/status.py:422` (shift report) | NO — Employee OS internal |
| `TriggerEvent` | UNKNOWN — `trigger_signals.py:26` writes adjacent WorkspaceTrigger but explicit `TriggerEvent.objects.create()` not found | `process_trigger_events` Celery task | UNKNOWN (writer unverified) |
| `FleetEvent` | `fleet_events.py:71:emit_event()` | `views_fleet_events.py:159` (SSE only) | NO — external SSE stream only |

**Load-bearing observation:** Only two event models have
cross-domain consumers today — DeliverableEvent (weak, opt-in) and
CeleryTaskEvent (single-domain read). Every other event model is
either single-domain audit or has zero cross-domain reader.

### 6.2 EventBus Streams (§3.31) — Producer / Consumer Registry

**Corrected S1274 v2 per Rigby SIGN review.** v1 concluded
"wiring completely dormant." Wrong. Rigby found real publishers +
consumers by direct grep. Corrected registry below.

Infrastructure at `core/services/event_bus.py:21-30`: 8 streams,
1 DLQ, 3 consumer groups (`scoring_workers`, `validation_workers`,
`analytics_workers` — lines 119-135), claim-stale beat at
`event_bus.py:393-449`.

**Publisher wrapper functions (all defined at `event_bus.py`):**

| Line | Function | Stream |
|---|---|---|
| 539 | `publish_spider_data_event` | `SPIDER_DATA` |
| 559 | `publish_opportunity_scored_event` | `OPPORTUNITY_SCORED` |
| 596 | `publish_validation_required_event` | `VALIDATION_REQUIRED` |
| 619 | `publish_validation_decided_event` | `VALIDATION_DECIDED` |
| 643 | `publish_outcome_recorded_event` | `OUTCOME_RECORDED` |
| 686 | `publish_system_alert_event` | `SYSTEM_ALERT` |

**Consumer tasks (all in `core/tasks.py`):**

| Line | Task | Stream / Group |
|---|---|---|
| 4726 | `process_event_bus_scoring_queue` | `scoring_workers` |
| 4760 | `process_event_bus_validation_queue` | `validation_workers` |
| 4794 | `process_event_bus_analytics_queue` | `analytics_workers` |
| 4874 | `get_event_bus_stats` | reads DLQ + stream lengths |
| 4883 | (imports `get_event_bus()` — infrastructure entry) | — |

All 4 consumer tasks routed to `broadcast` queue per
`core/settings.py:1315-1317,1579`.

**Confirmed producer → consumer chain (1 verified end-to-end):**

```
scoring_dispatcher._score_realtime()  [core/services/scoring_dispatcher.py:262+]
  → _publish_scoring_event(spider_data, result, 'realtime', latency_ms)
     [scoring_dispatcher.py:21-40]
  → publish_opportunity_scored_event(opportunity_id, spider_data_id, ml_score, rule_score, hybrid_score, confidence)
     [event_bus.py:559]
  → bus.publish(stream=EventStream.OPPORTUNITY_SCORED, ...)
  → Redis Stream: OPPORTUNITY_SCORED
  → scoring_workers consumer group
  → process_event_bus_scoring_queue()  [core/tasks.py:4726]
     (broadcast queue)
```

Same call pattern at `scoring_dispatcher.py:480` (batch mode).

**Other publisher wrappers exist but caller sweep is incomplete:**

- `publish_spider_data_event` — spider tasks likely call this;
  not exhaustively traced in this audit.
- `publish_validation_required_event` — HITL validation flow;
  `core/services/hitl_validation.py:24` imports from event_bus.
- `publish_validation_decided_event` — human decision recording
  path; caller UNKNOWN.
- `publish_outcome_recorded_event` — BettingOutcomeVerifier +
  Impact tracking; caller sweep incomplete.
- `publish_system_alert_event` — governance/health alerts; caller
  UNKNOWN.

**Consumer-side handler bodies** (what `process_event_bus_*_queue`
tasks actually DO with events) — not fully traced in this audit.
Read of `core/tasks.py:4726-4834` would resolve.

**Missing:**

- **System-level contract.** For each stream: what events are
  guaranteed to fire? Who owns the schema? What downstream
  effects must occur when an event is consumed? What SLA on
  consumer processing latency?
- **Adoption sweep.** For each of the 5 publisher wrappers,
  enumerate call sites. Some (OPPORTUNITY_SCORED) have confirmed
  callers; the other 4 have unverified adoption.
- **DLQ cleanup task.** `mi:dead_letter` accumulates; no
  scheduled cleanup found.
- **End-to-end observability.** No metric confirming that events
  produced actually generate observed platform effects
  downstream (e.g., "10 opportunity scores were published this
  hour; 10 were consumed and generated N validation events").

**Corrected verdict:** Infrastructure mature; wiring **partially
adopted** (1 of 8 streams verified end-to-end;  others have
publisher wrappers but unverified callers); consumer-side
observability weak; system-level contract undefined. This is a
coverage + verification + contract-definition problem, not a
build-from-scratch problem.

### 6.3 Weak Event Flows (Opt-in / Feature-Flagged / Minimal Consumers)

- **`RIGBY_EVENT_INTAKE_ENABLED` (default OFF).** DeliverableEvent
  → `rigby_event_intake` task → `RigbyWorkItem` row. Consumer of
  `RigbyWorkItem` (what turns it into PA conversation or HAI)
  UNKNOWN.
- **WorkspaceTrigger → beat wakeup.** Rows created; no explicit
  task processes them found. `workspace_autopilot_conductor.py`
  location UNCONFIRMED (Agent 3 §3.2 flag).
- **AgentFollowupSubscription banner suppression.** If
  `auto_followup=False` at dispatch time, banner silently
  suppressed (S1273 memory rule
  `feedback_auto_followup_false_suppresses_banner.md`). No metrics
  on completion rate.
- **Body systems → dashboard/alerts.** HeartBeat rows accumulated
  every 10 min; no consumer found (Agent 3 §3.4).

### 6.4 Fire-and-Forget Events (No Persistent Audit)

- **Page telemetry** — `POST /api/v1/telemetry/page-view/` → Redis
  counter, transient.
- **Agent status broadcasts** (`/ws/agent-execution/`) — WebSocket
  only; no persistent audit.
- **Decision command stream** (`/ws/decisions/`) —
  HumanFeedbackRecord persistent; broadcast is delivery only.

### 6.5 Missing Event Schemas (Novel S1274 Contribution)

Building on Agent 3 §7 table, these event models don't exist but
should for cross-domain integration to work:

| Missing Event | Producer Domain | Consumer Domain | Rationale |
|---|---|---|---|
| `MissionCompletionBroadcast` | Employee OS (4) | Frontend (18), Observability (25) | Push instead of 15s polling |
| `NotificationEvent` (unified wrapper) | Content Pipeline (11), Signal Engine (9), HumanAttention (16) | Web Push (17), Expo (19), Discord (20), Inbox (17) | Deduplication + unified audit |
| `FailureClusterEvent` | Observability (25) | HumanAttention (16), Governance (23) | Aggregator over CeleryTaskEvent failure rate |
| `LLMCostOverrunEvent` | Observability (25) | Governance (23) | Auto-freeze on window cost > threshold |
| `SpiderDroughtEvent` | Spider Framework (8) | Employee OS Platform Auditor (4), HumanAttention (16) | Silent spider detection |
| `OpportunityEscalationEvent` | Revenue Pipeline (32) | Initiative Pipeline (12) | Revenue > threshold → auto-Initiative |
| `PatternCriticalityEvent` | Signal Engine (9) | HumanAttention (16) | pattern_strength > 0.9 → auto-HAI |
| `DataQualityDedupEvent` | Spider Framework (8) | Observability (25), HumanAttention (16) | Dedup collision alert |
| `AnalyticsEvent` (persistent) | Frontend (18) | Content Pipeline (11) | Published content ↔ view attribution |

---

## 7. Boundary Violations

Detailed findings from Agent 4 sweep, grouped by violation class.

**Rigby S1274 re-ranking (v2):** all findings in this section
sort into two categories that matter for prioritization:

- **Bucket A — "violates runtime policy/auditability."** The
  code makes it harder to enforce a documented policy or produces
  audit gaps. These are load-bearing and worth research/fix
  attention. Members: §7.5.1 (direct OpenAI imports — memory-rule
  violation + cost-tracking audit gap), §7.4.1 + §7.4.2
  (multi-domain orchestrators — acceptable *if* graceful
  degradation holds; policy-adjacent because they own
  trans-domain state transitions), §7.7 (learning bridges —
  auditability contract is documented via ABC).
- **Bucket B — "just messy."** The code is structurally awkward
  but doesn't violate any policy or lose audit trail. Members:
  §7.1 (thin handler wrappers), §7.2 (view-layer business
  logic), §7.3.2 (utility functions in tasks.py), §7.8 (tool
  dispatcher — actually clean, not messy).
- **Special case: §7.6 god-services.** `discord_bot.py` (11,677
  lines) is Bucket A (blast radius on any change is a runtime
  risk); `unified_pa_entrypoint.py` (7,613 lines) is Bucket B
  (hub-and-spoke by design; large but focused).

This re-ranking is Rigby's substantive edit — original v1 sorted
by "severity" (LOW/MEDIUM/HIGH) alone, which conflated "big blast
radius" with "hard to change safely." The buckets separate the
two concerns.

### 7.1 Class 1 — Tool Handlers Doing Orchestration Logic

- **§7.1.1** — `td_handlers_content.py:118-160` links Deliverable to
  Initiative directly (thin wrapper). MEDIUM severity, acceptable.
- **§7.1.2** — `td_handlers_ops.py:96-127` chunk filtering in
  `_filter_chunks_by_originating_session` (S1145). LOW severity,
  acceptable as query-side logic.

### 7.2 Class 2 — Views Doing Business Logic

- **§7.2.1** — `views_analytics.py:39-202` day-by-day ORM loop
  across Opportunity + Application + Revenue + AgentExecution.
  MEDIUM. **Refactor candidate** — extract `AnalyticsService`.
- **§7.2.2** — `views_content.py:100-164` direct ContentGeneration
  writes with state machine. MEDIUM. **Refactor candidate** —
  extract `ContentGenerationService`.

### 7.3 Class 3 — Tasks Doing Domain Logic

- **§7.3.1** — `tasks.py:6961` direct `from openai import OpenAI`
  bypasses factory. MEDIUM. **Global search-and-replace fix.**
- **§7.3.2** — `tasks.py:129-161` discourse marker extraction. LOW
  severity, acceptable as utility function.

### 7.4 Class 4 — Services Reaching Into Other Domain Models

- **§7.4.1** — `conversation_initiative_pipeline.py:30-155`
  cross-domain bridge. MEDIUM but ACCEPTABLE (intentional).
- **§7.4.2** — `content_deliberation_runner.py:1-150` multi-stage
  orchestration. MEDIUM but ACCEPTABLE (graceful degradation via
  try/except).

### 7.5 Class 5 — Agents / Modules Bypassing Shared Primitives

- **§7.5.1** — Multiple direct `openai` imports. **Two independent
  sweeps** (Agent 4 + Rigby SIGN grep) together identified 9+
  files with ~15+ import sites. See §4.2 for the reconciled list.
  MEDIUM severity + memory-rule violation. **Global fix candidate.**

### 7.6 Class 6 — God-Services (Top 5 by Line Count + Cross-Domain Imports)

| Rank | Service | Lines | Cross-Domain Imports | Verdict |
|---|---|---|---|---|
| 1 | `discord_bot.py` | 11,677 | 5+ (ops, content, agents, analytics, voice) | HIGH — urgent refactor candidate |
| 2 | `unified_pa_entrypoint.py` | 7,613 | 8+ (hub-and-spoke by design) | MEDIUM — acceptable for critical path; extract sub-services |
| 3 | `td_handlers_ops.py` | 6,290 | 4+ (search, redis, docs, analytics) | MEDIUM — modularized via mixin; acceptable |
| 4 | `workflow_orchestration_agent.py` | 5,424 | 6+ | MEDIUM |
| 5 | `td_handlers_content.py` | 4,890 | 3+ | MEDIUM — modularized via mixin |

### 7.7 Class 7 — Direct Signal-Handler Model-to-Model Reach

- **`revenue_attribution_bridge.py:22-28`** — Revenue post_save →
  UserAgentLearning. INTENTIONAL learning bridge (S1115 ABC
  pattern). ACCEPTABLE.
- **`document_processing_signals.py`** — Content → NarrativeShift.
  Similar pattern. ACCEPTABLE.

### 7.8 Class 8 — Tool Dispatcher Assessment

- **`tool_dispatcher.py`** (1,267 lines) — LOW severity. Clean
  dispatcher pattern. Well-factored per Agent 4 review. Minor
  concern: handler mixins imported at module load; could be lazy.

---

## 8. Circular Dependencies and Dependency Traps

Findings from Agent 1 sweep. **Headline: no runtime cycles
detected.** The codebase has mature cycle-prevention via lazy
imports, TYPE_CHECKING guards, and defensive try/except patterns.

### 8.1 Lazy-Import Patterns (40+ Sites, All Documented, All INTENTIONAL)

Cataloged in Agent 1 §2.1. Key files:

- `ai_core/intelligence/bluesky_learning_bridge.py:47-52` — lazy
  agent-class loading.
- `ai_core/agents/concrete_executor.py:18-46` — documented "avoid
  circular deps + import issues in agent loading."
- `core/services/spider_intelligence.py:92` — LegacySpiderData
  model lazy load.
- `core/consumers_unified_v2.py:112` — UnifiedPA lazy load.
- `core/services/signal_aggregation_service.py:775-777` —
  fleet_events + fleet_signals lazy.
- `agents/__init__.py:33,120,130` — S728 lazy loading during
  Django app startup.
- 23+ service files defer task imports to function-body scope
  (`from core.tasks import X` inside handlers).

**Classification:** HARMLESS. Standard Celery pattern.

### 8.2 TYPE_CHECKING Guards (12 sites)

- `core/models_voice_marketplace.py:14-21`
- `core/models_ai_series.py:21-28`
- `core/models_pipeline_feedback.py:19-25`
- `core/models_content_pipeline.py:17-24`
- `core/models_autonomous_studio.py:28-35`
- `core/services/platform_config.py:23-28`
- `agents/__init__.py:31,157`

**Classification:** BEST PRACTICE. Zero runtime cost.

### 8.3 Try/Except ImportError (30+ sites)

Primarily used for optional-dependency graceful degradation (ML
libraries, specialized spiders, external integrations). Agent 1
found no evidence of these guards masking real cycles.

### 8.4 Bidirectional Reach-Through — Managed

- **Services ↔ Tasks:** Services import tasks inside function
  bodies; tasks import services at module load only from
  non-conflicting domains (redis, codejobs). NO CYCLE.
- **Agents ↔ Intelligence:** `base_agent.py:3541` lazy-loads
  `intelligence.hallucination_publisher`; intelligence writes
  models but doesn't dispatch to agents at module load. MANAGED.
- **Core ↔ Intelligence:** Bidirectional but 30+ intelligence→core
  imports are model-only; core→intelligence is deferred to function
  bodies or lazy-loaded. MANAGED.

### 8.5 Runtime-Level Cycle Risks (Not Import-Level)

**These are NOT import cycles but runtime call cycles.**

- **`delegate_to_specialist` tool — no depth limit / cycle
  detection.** S1273 §3.2 flagged theoretical infinite loop.
  Agent 6 confirmed: "max_depth=3 is only guard" — no formal
  cycle detection. If A delegates to B, B delegates to C, C
  delegates to A, would the depth cap catch it? UNKNOWN — depth
  is per-branch, not global.
- **Learning loop convergence.** Human decides → ML learns →
  agent injects learned prefs → next decision. If learning
  changes agent behavior such that human decisions flip, does
  the loop **converge or oscillate**? No convergence proof; no
  observability on flip rate.
- **Celery queue dependencies.** If `pa` queue awaits result from
  `code_jobs` queue, and `code_jobs` posts back to `pa`, and both
  queues back up, distributed deadlock is possible. No formal DAG
  of queue-to-queue dependencies exists in docs.

### 8.6 Historical References (RESOLVED)

Docs in `docs/archive/` mention circular import issues from
Sessions 100 / 400 / 728, all resolved. Current codebase has no
active architectural warnings about circular deps.

### 8.7 Dependency Documentation Gap

Agent 1 recommends (Research Only — not implementation):

- No explicit `docs/IMPORT_ARCHITECTURE.md` describing canonical
  unidirectional rules (agents → services → models).
- No pre-commit hook flagging new `from core.agents import X`
  entries in `core/services/` (which would create new debt).
- No pre-commit hook flagging new `from openai import OpenAI`
  entries anywhere (which violates memory rule).

---

## 9. Candidate Service Boundaries

Extraction readiness per candidate. **Research-only — do not
recommend extraction yet.** Ranked from most to least ready.

### 9.1 Employee OS — HIGH readiness

- **Separation readiness:** HIGH. Frozen dataclasses (jobs.py),
  standard `MissionRunner` orchestrator, dedicated task modules.
  `mission_runner.py` imports NOTHING from agents, PA, spiders,
  intelligence (Agent 1 confirmed).
- **Dependency count:** LOW-MODERATE — models only (OpsRun,
  Deliverable, MessageThread) + service factories.
- **Data ownership:** CLEAR. OpsRun / OpsRunEvent / Deliverable /
  DirectMessage / MessageThread all documented.
- **API boundary:** CLEAR. PA tool `employee_tool`
  (describe/run_now/status/evidence_for_mission); per-job beat
  entries.
- **Operational independence:** HIGH. Dedicated Celery tasks per
  employee; separate migration lanes.
- **Why extraction would be plausible:** Nearly self-contained.
  Extraction = move `core/employees/` to separate package + update
  imports.
- **Why extraction is still premature:** Employee OS is still
  stabilizing — Platform Auditor + Chief of Staff are recent
  additions (S1257/S1258); beat wiring in progress.
- **Speculative:** Ready in 1-2 cycles.

### 9.2 Publishing (Content Pipeline) — MEDIUM-HIGH readiness

- **Separation readiness:** MEDIUM. Clear 5-step deliberation flow;
  `content_deliberation_runner.py` (3,275 lines) is orchestrator.
- **Dependency count:** HIGH — agents, signal engine, human
  attention, initiative pipeline.
- **Data ownership:** CLEAR. SelfBlog + Deliverable + PublishGate
  logic.
- **API boundary:** DEFINED. `content_tool` PA tool.
- **Operational independence:** PARTIAL. `content` Celery queue
  exists.
- **Why premature:** Initiative pipeline coupling; signal-claim
  bridge missing; reviewer role model-level enforcement absent
  (Agent 5).

### 9.3 Memory / RAG — MEDIUM readiness

- **Separation readiness:** MEDIUM-HIGH. Two lanes
  (`rag_integration.py` prod + `rag.py` local) + centralized
  `EmbeddingService`.
- **Dependency count:** HIGH — every agent consumes memory/RAG.
- **API boundary:** DEFINED. `search_embeddings()` /
  `get_rag_context()`.
- **Operational independence:** PARTIAL. No dedicated queue; no
  embedding refresh beat.
- **Why premature:** Two RAG lanes create decision debt (no
  documented call-time selector). Extraction requires observability
  dedup audit first (S1273 §5.13 gap).

### 9.4 Spider Framework — MEDIUM readiness

- **Separation readiness:** MEDIUM. 173 spider files across 41
  categories; `spider_registry` stable interface.
- **Dependency count:** MODERATE-HIGH. Consumed by agents, signal
  engine, content pipeline, PA context.
- **Data ownership:** UNCLEAR. `LegacySpiderData` shared with
  signal engine.
- **API boundary:** DEFINED (`spider_registry.query`).
- **Operational independence:** PARTIAL. No dedicated queue.
- **Why premature:** Sports/DBAO integration gap must be resolved
  first (S1273 §3.10; S1274 §3.x); extraction would orphan sports
  spider data.

### 9.5 Sports Intelligence — MEDIUM readiness

- **Separation readiness:** MEDIUM. Sports app is self-contained
  Django app + dedicated queue.
- **Dependency count:** MODERATE.
- **Data ownership:** CLEAR.
- **API boundary:** UNCLEAR — no documented sports API endpoint.
- **Operational independence:** PARTIAL. Dedicated `sports` queue.
- **Why blocked:** S1273 §3.10 says pipeline to signals /
  initiatives / deliverables is "not wired." Extraction bakes
  isolation without deciding if isolation is intentional.

### 9.6 Revenue / Outreach Pipeline — LOW readiness

- **Separation readiness:** LOW-MEDIUM. Newest domain (S1273 v2
  added). Models + orchestrator + 3 agents exist.
- **Dependency count:** MODERATE — spiders + agents + governance.
- **Data ownership:** CLEAR (5+ dedicated models).
- **API boundary:** PARTIAL — orchestrator class exists; no HTTP
  endpoint traced; PA tool UNKNOWN.
- **Operational independence:** NONE — no beat, no dedicated
  queue.
- **Why premature:** Domain is research-stage. 5 load-bearing
  UNKNOWNs from S1273 §10.3 (opportunity model location, outbound
  channel, close-pack trigger, etc.).

### 9.7 Observability — LOW readiness

- **Separation readiness:** MEDIUM-LOW. 5+ parallel telemetry
  layers; 14+ event models.
- **Dependency count:** VERY HIGH — every task, every agent, every
  tool call emits.
- **Data ownership:** SCATTERED. No single schema owner.
- **API boundary:** UNCLEAR. No unified observability API.
- **Operational independence:** NONE. Fire-and-forget synchronous.
- **Why blocked:** Cross-cutting concern, not isolatable. S1273
  §5.13 identified "Observability Deduplication Audit" as
  prerequisite research. Extraction would export a duplicated
  event model, creating debt.

### 9.8 Governance — BLOCKED

- **Separation readiness:** LOW. Architecturally fragmented
  (4 planes, S1269).
- **Dependency count:** VERY HIGH — every decision point calls a
  gate.
- **Data ownership:** SCATTERED.
- **API boundary:** PARTIAL — asymmetric (observation-only surfaces
  + write-only KillSwitch).
- **Operational independence:** NONE.
- **Why blocked:** S1273 identifies as "biggest architectural
  risk." Extraction requires: (1) unifying 4 planes, (2) building
  Symbol Mapping (STAGE 3 per ARCHITECTURE_INDEX §9), (3) moving
  from observation-only to enforcement. This is 2-3 research
  cycles away.

### 9.9 PA / Rigby — DEPENDS ON OTHER DOMAINS FIRST

- **Separation readiness:** MEDIUM-HIGH internally, but hub-and-
  spoke connection to every domain.
- **Dependency count:** VERY HIGH (master orchestrator).
- **Data ownership:** CLEAR for PA-specific data.
- **API boundary:** CLEAR (`POST /api/pa/chat/` + PA tool schemas).
- **Operational independence:** PARTIAL (`pa` queue exists).
- **Why "depends":** Extraction is a "gateway refactor" (Agent 5).
  Requires converting all in-process calls to RPC. Not isolated
  extraction. Do not attempt until 5+ domains are stable +
  extracted first.

### 9.10 Ranking Summary

| Candidate | Readiness | Blocker | Cycles to Ready |
|---|---|---|---|
| Employee OS | HIGH | Still stabilizing | 1-2 |
| Publishing (Content) | MED-HIGH | Initiative coupling + reviewer role | 2-3 |
| Memory / RAG | MED | Observability dedup audit + RAG lane selector | 2-3 |
| Spider Framework | MED | Sports integration gap | 2-3 |
| Sports Intelligence | MED | Signal-wiring decision | 2-3 |
| Revenue Pipeline | LOW | 5 load-bearing UNKNOWNs + workflow research | 3-4 |
| Observability | LOW | Cross-cutting; dedup audit prerequisite | 3-4 |
| Governance | BLOCKED | Symbol Mapping + plane composition | 4+ |
| PA / Rigby | DEPENDS | Depends on other extractions first | Last |

---

## 10. Ownership Gaps

Detailed findings from Agent 5 sweep. **6 CLEAR, 19 PARTIALLY-
CLEAR, 7 UNCLEAR/UNKNOWN.**

### 10.1 CLEAR Ownership (6 domains)

- **§3.1 PA / Rigby** — Rigby (JobContract owner) + Claude Code
  (autonomous responder).
- **§3.4 Employee OS + MissionRunner** — Rigby (docs) + Platform
  Auditor + Chief of Staff (JobContracts) + Claude Code (PR ownership).
- **§3.15 Documentation / Research System** — Rigby runs 4-step
  cascade daily; Claude Code owns edits.
- **§3.18 Frontend / Workspace UI** — Chris (design) + Claude Code
  (implementation via PR).
- **§3.24 Automation / Celery** — Canonical source in `core/celery.py`;
  Claude Code owns changes; PlatformAuditor inspects.
- **§3.28 Configuration / Deployment** — Railway deploy + Makefile;
  Claude Code owns changes.

### 10.2 UNCLEAR / UNKNOWN Ownership (7 domains) — Highest Risk

- **§3.6 Boardroom / Advisors.** In-memory state only; no
  persistence; no documented advisor definition owner. Ownership
  of the 30 advisor profiles: UNKNOWN.
- **§3.19 Mobile App.** Models exist; UI unknown; no documented
  owner for what "mobile" means as a product.
- **§3.21 Voice / Avatar Surfaces.** HeyGen F2F is a stub; no
  named owner for completion.
- **§3.23 Governance / Authority.** Fragmented across 4 planes.
  No single owner for enforcement design. Chris owns policy;
  runtime enforcement has no owner.
- **§3.30 Body Systems + BodyCoordinator.** 9 systems scanned every
  10 min; HeartBeat rows accumulated; **no reader/consumer
  identified.** Who owns each system implementation? Diffuse.
- **§3.31 Event Bus / Streams.** Producer/consumer map absent; no
  named owner for wiring.
- **§3.32 Revenue / Outreach / Engagement Pipeline.** Pipeline
  agents lack JobContracts. Opportunity flow orchestration owner
  UNKNOWN.

### 10.3 PARTIALLY-CLEAR (19 domains)

Documented in Agent 5 sweep §Part 1 table. Common pattern:
domain has code that works, but no explicit "who fixes this when
it breaks" documented anywhere.

### 10.4 Ownership Gap Integration Risks

- **§3.6 Advisors:** If no one persists advisor metrics, and
  service restarts happen, all satisfaction ratings + consultation
  history lost. Silent data loss.
- **§3.23 Governance:** If no one owns enforcement design, four
  planes stay non-composed. Every new decision point wonders which
  plane to call.
- **§3.30 Body Systems:** If no one reads HeartBeat rows, the
  9-system scan is theater — data accumulates without insight.
- **§3.31 Event Bus:** If no one owns wiring, all downstream
  event-based integrations stall.

---

## 11. Cross-Domain Risk Matrix

Every finding across §3–§10, one row per finding. Types match
mission spec exactly.

| # | Finding | Domains | Type | Severity | Evidence | Risk | Recommended Research |
|---|---|---|---|---|---|---|---|
| 1 | EventBus partial adoption + missing contract | 31 → all | missing_connection | HIGH (revised S1274 v2 per Rigby — from CRITICAL; 5 publisher wrappers exist + 3 consumer tasks + 1 verified end-to-end chain) | `event_bus.py:539,559,596,619,643,686`; `tasks.py:4726,4760,4794,4874`; verified caller `scoring_dispatcher.py:21-40,282,480` → OPPORTUNITY_SCORED | Silent event-based integrations for 4-7 of 8 streams; adoption + contract undefined | EventBus Adoption + Contract Verification (P0) |
| 2 | Mission completion → Frontend dashboard | 4 → 18 | missing_connection | HIGH | OpsRunEvent persistent; no WS send | 15s polling delay; time-sensitive UX gap | Mission Completion Broadcast |
| 3 | Deliverable ready → Notification (Web Push / Discord / Inbox) | 11 → 17,20 | missing_connection | HIGH | DeliverableEvent row; no fan-out handler | Silent delivery; user must poll | Notification Unification Study |
| 4 | Critical failure cluster → HumanAttentionItem | 25 → 16 | missing_connection | HIGH | CeleryTaskEvent failures; no aggregator | Cascade failures unnoticed 10+ min | Failure Cluster Aggregator design |
| 5 | LLM cost overrun → Governance auto-freeze | 25 → 23 | missing_connection | HIGH | LLMCallEvent.cost_usd missing | Runaway spend $500+ silent | LLM Provider Failover + Cost Sketch (S1273 §9 #9) |
| 6 | Sports/DBAO ↔ Signal/Content pipeline break | 10 → 9,11,12 | missing_connection | HIGH | `sports_odds` not a SignalCluster data_type | Structural question ("island vs integrated?") unresolved | Sports ↔ AI Studio Integration Sketch (S1273 §9 #4) |
| 7 | Spider drought → Platform Auditor | 8 → 4 | missing_connection | MEDIUM-HIGH | No SpiderDrought event; no aggregator | Data pipeline outage invisible 24h | Spider Health SLO design |
| 8 | Budget freeze → PA tool dispatch warning | 23 → 1 | missing_connection | MEDIUM | LLMEnforcer returns empty; no warning | Silent tool failure; erosion of trust | Governance context injection |
| 9 | Revenue opportunity → Initiative auto-create | 32 → 12 | missing_connection | MEDIUM | ImpactEvent recorded; no trigger | High-value signals lost to followup | Opportunity Escalation Event design |
| 10 | Signal pattern threshold → HAI | 9 → 16 | missing_connection | MEDIUM | SignalCluster stored; no pattern-strength gate | Critical patterns unescalated | Pattern Criticality Event design |
| 11 | Published content → Analytics tracking | 11 → 18 | missing_connection | MEDIUM | Frontend Redis counter transient; no persistent AnalyticsEvent | Content performance invisible | Analytics Event schema design |
| 12 | Advisor consultation → AgentLearning | 6 → 13 | missing_connection | LOW | Advisors prompt-context only | No learning from advisor guidance | (accept — advisors not full agents per S1268 F3) |
| 13 | `discord_bot.py` god-service | 20 → all | overcoupling | HIGH | 11,677 lines; 25 Cog classes; 96 commands | Maintenance risk; blast radius | Refactor plan (research-only) |
| 14 | Direct `openai` imports bypass factory | 2,11,20 → 7 | overcoupling | MEDIUM | 6+ files listed in §7.5.1 | Cost tracking gap; no unified timeout/retry | Global sweep + pre-commit hook (research only) |
| 15 | `views_analytics.py` heavy business logic | 22 → 12,32,25 | boundary_violation | MEDIUM | day-by-day ORM loop across 4 domain models | Business logic outside service layer | AnalyticsService extraction |
| 16 | `views_content.py` direct DB writes | 22 → 11 | boundary_violation | MEDIUM | ContentGeneration state machine in view | State transitions outside service | ContentGenerationService extraction |
| 17 | `HumanPreference.topic_weights` never saved | 16 → 13 | boundary_violation | MEDIUM | S1269 F5; confirmed | Learning reset on restart | Learning persistence audit |
| 18 | Multiple orchestration paths (Celery vs MissionRunner) | 4,24 → all | duplicate_model | MEDIUM | S1268 F2 canonical | No composition guarantee; "do not mix" | Cross-Orchestration Contract sketch |
| 19 | 5+ memory stores + 2 RAG lanes | 13,14 → all | duplicate_model | MEDIUM | S1273 §5.4; Agent 2 §8 | Data-consistency contract missing; call-time selector missing | Memory Resolution + RAG Selector research |
| 20 | 3 notification systems + Inbox + HAI (5 delivery paths) | 17,19,20,16 → all | duplicate_model | MEDIUM | S1273 §5.2; Agent 3 §4.2 | Same user could receive same alert 4-5× | Notification Unification Study |
| 21 | 4 governance planes don't compose | 23 → all | duplicate_model | HIGH | S1269 §1 canonical | Precedence order implicit; "biggest architectural risk" per Rigby | Governance Plane Composition (S1273 §9 blocked by Symbol Mapping) |
| 22 | 5 execution telemetry layers | 25 → all | duplicate_model | MEDIUM | S1273 §5.7 | Query complexity; unclear dedup | Observability Deduplication Audit (S1273 §9 #3) |
| 23 | 19 actor identity concepts | 4,2,6,13 → all | duplicate_model | MEDIUM | S1271 canonical (do not re-do) | Enforcement-grade attribution requires 3-role vocab (F11) | Identity Resolution for Inter-Employee Dispatch (novel S1274 contribution) |
| 24 | 3 independent agent dispatch systems | 3,24 → all | duplicate_model | MEDIUM | S1029 audit; S1273 §5.8 | Disabling one doesn't stop others | Agent Dispatch Convergence sketch |
| 25 | Initiative vs ActionPlan vs Dream overlap | 12 → all | duplicate_model | MEDIUM-HIGH | Agent 2 §6 flagged as HIGH risk; Dream model UNKNOWN | Double-tracking of work items | Planning Model Consolidation Study |
| 26 | Precedence GovernanceState vs KillSwitch vs JobContract.authority | 23 → all | overcoupling | MEDIUM | S1269 §1 F3 | Which wins? Error message opaque | Blocked by STAGE 3 Symbol Mapping |
| 27 | `delegate_to_specialist` no cycle detection | 2,3 → all | circular_dependency | MEDIUM | S1268 §3.2; S1273 §3.2 confirmed | Theoretical infinite loop; max_depth=3 per-branch | Cycle detection + circuit breaker sketch |
| 28 | Learning loop convergence unknown | 13,16 → all | circular_dependency | LOW-MEDIUM | Agent 3 §2.7 speculative | Feedback loop could oscillate | Convergence proof / observability |
| 29 | Celery queue-to-queue dependencies undocumented | 24 → all | circular_dependency | UNKNOWN | No DAG in docs | Distributed deadlock risk | Queue Dependency Map |
| 30 | Boardroom / Advisors — no persistence contract | 6 → 13 | unclear_owner | HIGH | in-memory only; no docs owner | Silent metric loss on restart | Advisor Persistence Contract (S1273 §9 #7) |
| 31 | Mobile App — scope unclear | 19 → all | unclear_owner | HIGH | UI unknown; ownership unnamed | Mobile scope drift | Mobile scope determination |
| 32 | Voice/Avatar — HeyGen F2F stub | 21 → 1 | unclear_owner | MEDIUM | F2F.1 stub; F2F.3 planned | Roadmap unclear | Avatar Roadmap Consolidation |
| 33 | Governance runtime enforcement — no owner | 23 → all | unclear_owner | HIGH | Chris owns policy; enforcement runtime has no owner | Four planes stay non-composed | Blocked by Authority Enforcement Design Space + Symbol Mapping |
| 34 | Body Systems — no reader/consumer | 30 → all | unclear_owner | MEDIUM | HeartBeat accumulated; no reader | Data theater; no insight | Body Systems Purpose Audit |
| 35 | Event Bus — no wiring owner | 31 → all | unclear_owner | HIGH | No named owner for producer/consumer map | Silent stall | Producer/Consumer Map (P0) |
| 36 | Revenue Pipeline — no runtime owner | 32 → all | unclear_owner | HIGH | Pipeline agents lack JobContracts; no beat | Domain research-stage without owner | Revenue Pipeline Canonical Architecture (S1273 §5.12) |
| 37 | Employee OS extraction readiness | 4 → self | extraction_candidate | (informational) | Nearly self-contained | Ready in 1-2 cycles | Extraction Readiness Study (future) |
| 38 | Publishing extraction readiness | 11 → self | extraction_candidate | (informational) | Coupled to initiatives + reviewer role | 2-3 cycles | Extraction Readiness Study (future) |
| 39 | Memory/RAG extraction readiness | 13,14 → self | extraction_candidate | (informational) | Two RAG lanes ambiguous | 2-3 cycles | RAG Lane Selector research |

---

## 12. Recommended Next Research

Ranked by architectural uncertainty × risk × unblocked flows.
Focus is **integration**, not domain inventory. Each mission is
research-only.

### 12.1 EventBus Adoption + Contract Verification (P0 — non-negotiable)

*Renamed S1274 v2 per Rigby SIGN — v1 called this "Producer/Consumer
Map" and assumed the wiring was dormant. Corrected scope below.*

- **Why:** EventBus has real publishers + consumers wired for at
  least 1 of 8 streams (OPPORTUNITY_SCORED end-to-end; see §6.2).
  What's missing is: (a) adoption sweep across the other 7 streams
  — how many publisher wrappers have callers? which consumer tasks
  actually process events? (b) system-level contract per stream —
  what events are guaranteed, who owns the schema, what SLA on
  consumer latency? (c) end-to-end observability — do produced
  events generate observed platform effects, or do events reach
  the stream and stop?
- **Scope:** For each of 8 named streams + DLQ, enumerate:
  1. Actual publisher call sites (extend the 1 known
     OPPORTUNITY_SCORED chain to the other 7 streams).
  2. Consumer task body inspection (`process_event_bus_scoring_queue`,
     `_validation_queue`, `_analytics_queue` at `tasks.py:4726-4834`)
     — what do they DO with events?
  3. Consumer-group configuration (how many streams does each of
     the 3 groups subscribe to?).
  4. Message schemas per stream + versioning.
  5. DLQ cleanup responsibility.
  6. Relationship to CeleryTaskEvent / LLMCallEvent / OpsRunEvent
     (are streams a parallel highway or intended replacement?).
- **Deliverable:** Adoption matrix (streams × publisher-callers ×
  consumer-actions) + gap analysis + one recommended decision path
  per stream (keep, deprecate, or wire more callers).
- **Unblocks:** All missing event flows in §3, §6.5 event schemas.
- **Verification anchor for future audits:** the corrected §6.2
  producer/consumer registry now provides the entry points for a
  future audit to extend.

### 12.2 Notification Unification Study (P0 — high user impact)

- **Why:** 5 delivery paths (Web Push + Expo + Discord + Inbox +
  HAI) with no dedup; same user could receive 4-5 copies of one
  alert. S1273 §5.2 flagged; this audit confirmed no unification
  service.
- **Scope:** Trace one signal event (arbitrage alert / deliverable
  ready / critical failure) through each path. Document
  delivery-guarantee differences, rate-limiting strategy per system,
  audit gap. Propose unification design space (single event bus,
  separate paths with dedup service, etc.).
- **Deliverable:** Delivery-guarantee matrix + failure scenario
  traces + design space (options, not selection).
- **Unblocks:** All missing notification flows in §3.

### 12.3 Sports/DBAO ↔ AI Studio: Product/Architecture Decision Point (P1)

*Reframed S1274 v2 per Rigby SIGN — v1 framed this as a "structural
question" implying a defect. Rigby's correction: it's a decision
point with two legitimate postures, each with explicit success
criteria. Research should enumerate the criteria, not presume the
answer.*

- **Why:** S1273 §3.10 documented the gap: `sports_odds` is not a
  valid `SignalCluster` data_type; MLPrediction/PlacedWager don't
  feed initiatives; BettingOutcomeVerifier outcomes don't flow
  back to signal scoring. But **whether that gap is a defect or
  an intentional island is a product-architecture call** — not a
  research finding. This mission enumerates the two postures with
  criteria.
- **Scope:** Two branches to evaluate:
  1. **Integration posture** — sports outcomes flow into signal
     clustering, initiative auto-creation, content deliberation.
     Success criteria: what integrations MUST exist for this to
     count as "integrated"? What performance / cost / correctness
     bars does the composed system need to hit? What content
     types are enabled that don't exist today?
  2. **Island posture** — sports intentionally stays isolated (own
     queue, own models, own agent pool, own PA tools). Success
     criteria: what boundaries MUST stay hard? What content /
     insight is EXPLICITLY out of scope? What operational
     invariants must the island preserve (independent scaling, no
     cross-contamination, etc.)?
- **Deliverable:** Both postures documented with explicit success
  criteria + failure modes if the criteria aren't met + operational
  cost estimate for each posture. **Chris gates the actual
  selection.** Rigby's frame: "not a presumed defect — a decision
  point with criteria for either answer."
- **Unblocks:** Content-pipeline decisions for sports content;
  betting-related deliberation surface design; sports spider
  extraction; whether cross-domain telemetry aggregation should
  include sports.

### 12.4 Identity / Actor Attribution Carriage Across Cross-Domain Write Paths (P0-companion — promoted S1274 v2 per Rigby SIGN)

*Promoted S1274 v2 per Rigby SIGN — v1 scoped this narrowly to
inter-employee dispatch. Rigby's correction: identity/actor
attribution carriage is a **hidden prerequisite for making any
cross-domain integration canonical** — not just Employee OS
messaging. Without it you cannot reliably enforce policy, trace
causality, or do ROI attribution on ANY multi-domain write path.*

- **Why:** S1271 catalogued 19 identity concepts + 22 attribution
  surfaces + F11 3-role vocabulary (executor_actor /
  sponsor_actor / principal_user), but **no downstream research
  answers "what actor identity does a cross-domain message
  carry?"** for the platform's real write paths: (a) agent →
  deliverable creation, (b) employee mission → deliverable /
  DirectMessage, (c) PA tool → any DB write, (d) autopilot /
  governance decision → runtime state change, (e) inter-employee
  dispatch (S1268 §10). All 5 of these have implicit or absent
  actor carriage today.
- **Scope:** For each of the 5 cross-domain write paths above,
  trace: which of the 3 roles is populated at the write moment;
  what verification each role enables downstream; how the message
  carries identity across the S1271 F6 drop-boundaries
  (HTTP→Celery, MissionRunner→Step.fn, Signal→Handler); what
  breaks (in audit, in enforcement, in ROI attribution) if the
  wrong role is populated or an ambiguous CharField is used.
- **Deliverable:** Cross-write-path identity carriage design space
  — one section per write path, with the 3-role vocabulary
  mapped and gaps flagged. Explicit statement of which paths
  cannot enforce policy today.
- **Unblocks:** (a) First inter-employee dispatch (S1268 §10 P0
  recommendation); (b) Authority enforcement design (STAGE 3+ per
  ARCHITECTURE_INDEX §9); (c) Cross-domain ROI attribution
  (currently only ImpactEvent + ImpactEvent-consumers can
  attribute, and only within revenue); (d) Trans-domain audit
  chain (evidence_for_mission style queries) working reliably
  across every write path, not just Employee OS missions.
- **Elevated priority:** Rigby's read is that this is a P0
  companion to §12.1 EventBus, not a P1 — every cross-domain
  event that flows across a boundary loses actor identity without
  a carriage contract. Fixing EventBus adoption without also
  defining identity carriage would produce a well-observed event
  stream where causality still can't be traced.

### 12.5 Governance Plane Composition Research (P2 — depends on Symbol Mapping)

- **Why:** 4 planes don't compose; precedence order implicit; Rigby
  S1273 called this "biggest architectural risk." **BLOCKED** by
  STAGE 3 Symbol Mapping Option Selection Design (per
  ARCHITECTURE_INDEX §9 roadmap).
- **Scope:** After STAGE 3 lands, research: given a specific mapping
  choice, how do autonomy + authority + budget + human governance
  planes compose? What's the precedence order? What error message
  does the operator see when planes conflict?
- **Deliverable:** Composition design space; concrete scenarios
  (freeze active + high-authority action; budget freeze + priority
  execution; etc.).
- **Unblocks:** Governance runtime enforcement design; cross-plane
  reasoning.

### 12.6 Observability Deduplication Audit (P2 — cost/benefit)

- **Why:** S1273 §5.13 flagged 5 parallel execution telemetry
  layers; this audit confirmed. Consolidation cost/benefit
  unstudied.
- **Scope:** Trace a single "agent executes tool → LLM call →
  writes deliverable" scenario through all 5 layers + 14+ event
  models. Identify overlap. Estimate deprecation cost per layer.
- **Deliverable:** Trace log + deduplication cost matrix +
  recommended consolidation path.

### 12.7 Additional S1274-Novel Missions (P3 — lower priority)

- **Cycle Detection + Circuit Breaker Sketch.** For
  `delegate_to_specialist` (research whether depth-per-branch is
  sufficient; propose cycle detection design).
- **Celery Queue Dependency DAG.** Enumerate queue-to-queue
  dependencies; identify potential distributed deadlocks.
- **Learning Loop Convergence Study.** For HAI → AgentLearning
  → agent behavior → next HAI feedback loop.
- **Cross-Orchestration Contract Sketch.** For Celery chain vs
  MissionRunner step loop — what breaks if mixed?
- **Planning Model Consolidation Study.** Initiative vs ActionPlan
  vs Dream — clarify Dream model status; propose consolidation
  path.

---

## 13. Appendix

### 13.1 Files inspected (partial)

Full evidence trail in sub-agent transcripts. Key files cited in
§3–§10 (spot-checked by parent, not exhaustive):

- `core/services/event_bus.py:21-30,119-135,393-449,686`
- `core/services/tool_dispatcher.py:1-700+`
- `core/services/unified_pa_entrypoint.py:1-100+`
- `core/services/llm_call_wrapper.py:195`
- `core/services/signal_aggregation_service.py:33-1161,775-777`
- `core/services/content_deliberation_runner.py:1-150`
- `core/services/opportunity_pipeline_orchestrator.py:30-200`
- `core/services/conversation_initiative_pipeline.py:30-155`
- `core/services/ops_autopilot/impact.py:375+,431+,488+,582+,951+`
- `core/services/ops_autopilot/governance.py:2159-2529`
- `core/services/human_attention_lifecycle.py:36-728`
- `core/services/body_coordinator.py:110-300+`
- `core/services/body_vitals.py`
- `core/services/discord_bot.py:1-11677`
- `core/services/rigby_event_intake.py:600`
- `core/services/llm_enforcer.py:200-260`
- `core/agent_router.py:1-250`
- `core/agents/base_agent.py:3541,749` (lazy import sites)
- `core/employees/mission_runner.py:1530-1570,835-900`
- `core/employees/jobs.py:73-162`
- `core/employees/comms.py:228-367`
- `core/employees/status.py:422,461`
- `core/celery_telemetry.py:74,115,177`
- `core/models_governance.py:17-189`
- `core/models_human_interface.py:20-227,230-266,268-358`
- `core/models_ops_runs.py:11-50,52-117`
- `core/models_celery_telemetry.py:17-100`
- `core/models_llm_telemetry.py:30-100`
- `core/models_tool_calls.py:19`
- `core/models_messaging.py:21-141`
- `core/models_deliverables.py:1`
- `core/models_outreach.py:18`
- `core/models_engagement.py:18`
- `core/models_meeting.py:18`
- `core/models_close_pack.py:20`
- `core/models_heart.py:HeartBeat`
- `core/models_unified_system.py:521,882,1017-1116,3691,3796,3845,3912,10787,19761,20611`
- `core/models_conversation_artifacts.py:22`
- `core/models_signal_intelligence.py:29`
- `core/signals/deliverable_status_signals.py:47,71,94`
- `core/signals/trigger_signals.py:26`
- `core/models_feedback_processing.py:122-180,216-330`
- `core/tasks.py:6961`
- `core/views_content.py:100-164`
- `core/views_analytics.py:39-202`
- `core/views_image_gallery.py:23`
- `core/views_image_generate.py`
- `core/tasks_content.py`
- `core/tasks_media.py`
- `core/channel_orchestrator.py`
- `core/learning_bridges/revenue_attribution_bridge.py:22-28`
- `core/signals/document_processing_signals.py`
- `intelligence/models.py:16,587`
- `intelligence/spider_decision_bridge.py`
- `intelligence/revenue_integration.py`
- `intelligence/tasks.py:11-12`
- `ai_core/spiders/spider_registry.py`
- `ai_core/agents/concrete_executor.py:18-46`
- `ai_core/intelligence/bluesky_learning_bridge.py:47-52`
- `sports/models.py`
- `content/models.py`
- `advisors/registry.py:75-154`
- `agents/__init__.py:31,33,120,130,157`

### 13.2 Docs inspected

- `docs/research/platform_architecture_inventory.md` (S1273 —
  parent doc; do not re-audit its 32-domain map)
- `docs/research/ARCHITECTURE_INDEX.md` (v5)
- `docs/research/governance_authority_evolution.md` (S1269 — do
  not re-map 4 planes)
- `docs/research/symbol_mapping_architecture.md` (S1270)
- `docs/research/actor_identity_attribution_architecture.md`
  (S1271 — do not re-inventory 22 attribution surfaces)
- `docs/research/authority_enforcement_design_space.md` (S1272 —
  do not re-do 33-incident catalog)
- `docs/research/employee_os_communication_substrate_audit.md`
  (S1268 — cited in §3.1 for inter-employee messaging candidate)
- `docs/research/employee_os_collaboration_patterns.md` (S1268 —
  do not re-audit 64-row inventory)
- `docs/EMPLOYEE_OS_PRIMITIVES.md` (canonical primitives + anti-
  duplication matrix)
- `docs/PLATFORM_INVENTORY.md` (runtime anchor; counts source)
- `docs/EVENT_SYSTEM_INVENTORY.md` (14+ event model catalog)
- `docs/AUDIT_FINDINGS.md` (Celery deferred list)
- `docs/topics/agent-system.md`, `.../content-pipeline.md`,
  `.../celery-workers.md`, `.../spider-network.md`,
  `.../body-systems.md`, `.../infrastructure.md`

### 13.3 Grep / search patterns used

- Circular imports: `noqa: circular`, `avoid circular`, `TYPE_CHECKING`,
  `importlib.import_module`, `import.*inside function`.
- Cross-domain reach: `from core.agents`, `from intelligence`,
  `from sports`, `from ai_core`, `from advisors`.
- Event flows: `.objects.create`, `.save\(\)`, `post_save`,
  `pre_save`, `@receiver`, `EventBus.*publish`.
- God-services: `wc -l` on `core/services/*.py`, `core/tasks*.py`,
  `core/views*.py`, sorted descending.
- Memory-rule violations: `from openai import OpenAI`, bare
  `Anthropic\(\)`, `import openai`.
- Boundary violations: view files with `.objects.filter` +
  `.aggregate` + loops; tasks with substantive body logic;
  services with cross-domain model writes.

### 13.4 Unresolved unknowns

- **§6.2** — EventBus `.publish()` call sites: were the 8 streams
  ever wired in prod? Historical git log spot-check needed.
- **§3.6** — Advisor exact count (25+ code vs 30 inventory).
- **§5.6** — Dream model status: aspirational vs implemented vs
  deprecated? Not resolved.
- **§3.3** — TriggerEvent writer path (signal handler adjacent to
  WorkspaceTrigger but not confirmed).
- **§3.4** — workspace_autopilot_conductor.py location (referenced
  but not verified).
- **§3.32** — Opportunity model exact location + schema (multiple
  candidates: `models_unified_system.py` + `persistence/models.py`).
- **§3.32** — Outbound channel service for outreach (email? API?
  something else?).
- **§3.32** — Close-pack conversion trigger (auto vs human-in-loop).
- **§4.6** — Precedence order across 4 governance planes.
- **§5.4** — Data-consistency rule when memory stores diverge.
- **§6.3** — RigbyWorkItem downstream handler (does anyone read
  it once written by rigby_event_intake?).
- **§8.5** — Learning loop convergence behavior (oscillation
  possible?).

### 13.5 Conflicts between sources

- **Agent 2 vs Agent 5 on Dream model:** Agent 2 said "NOT FOUND
  as top-level class"; Agent 5 flagged as "under-specified."
  Resolution: UNKNOWN, flagged in §5.6 + §13.4.
- **Agent 3 vs Agent 6 on Rigby event intake severity:** Agent 3
  §3.1 marks as WEAK (opt-in, feature-flagged); Agent 6 notes
  "no research doc explains architectural reason it's OFF by
  default." Both true; folded as complementary.

### 13.6 Verifier-loop corrections

**S1274 v2 (2026-07-01) — Rigby SIGN-with-edits folded.** Fresh
isolation pin `pa-7442a2e2665bd18e` (not the shared S1270+ arc
pin, per context-crossing guardrail). Rigby's structured verdict:

- **Overall confidence:** Medium.
- **Most important finding:** Sports/DBAO ↔ AI Studio decision
  point (not the EventBus map). Because the sports isolation is
  a **decision** and until it's resolved, cross-domain event
  design has an ambiguous target.
- **Most dangerous integration gap:** EventBus, but for the
  correct reason — not "dormant," but adopted for ~1 of 8
  streams with no system-level contract.
- **Most understated concern:** Identity/actor attribution
  carriage across every cross-domain write path (v1 scoped this
  narrowly to inter-employee dispatch; Rigby promoted it).
- **What Claude got wrong:** framed EventBus as "dormant" in a
  binary way. Actual state is "partially implemented, weakly
  adopted, unverified end-to-end."
- **Verdict:** SIGN-with-edits.

**Rigby's verification method.** Direct grep of the codebase:

1. `event_bus` → found 9 files with actual references (not just
   test mocks): `core/tasks.py`, `core/settings.py`,
   `core/services/event_bus.py`, `core/services/event_handlers.py`,
   `core/services/hitl_validation.py`,
   `core/services/scoring_dispatcher.py`,
   `core/services/platform_event_view.py`,
   `core/views_agent_extras.py`, `core/tests/test_platform_event_view.py`.
2. `def publish_` in `event_bus.py` → found 5 publisher wrapper
   functions (lines 539, 559, 596, 619, 643).
3. `_publish_scoring_event` → found active caller at
   `scoring_dispatcher.py:21-40,282,480`.
4. `import openai` → found 9 files (not 6), ~15+ import sites.
5. Read `tasks.py:4726-4820` → confirmed 3 consumer tasks
   (`process_event_bus_scoring_queue`, `_validation_queue`,
   `_analytics_queue`) plus `get_event_bus_stats`.

**Folded edits (S1274 v2):**

1. Frontmatter `verifier_loop` bumped to v2 with fold summary +
   preserved v1 note.
2. §1 Executive Summary — EventBus finding rewritten from
   "dormant" to "partially implemented, weakly adopted,
   unverified end-to-end" with 8-line evidence citation.
3. §1 Executive Summary — Sports/DBAO gap explicitly reframed
   as "product/architecture decision point" not "presumed
   defect."
4. §2.8 Integration Map — EventBus row rebuilt as 8-row table
   with each stream's publisher wrapper + consumer task + class
   (WEAK for OPPORTUNITY_SCORED; UNKNOWN for others).
5. §4.2 Overcoupled Domains — OpenAI import list updated to 9
   files / 15+ sites (Rigby's exact-cite list + Agent 4's
   broader list preserved, reconciliation flagged).
6. §6.2 EventBus registry — completely rewritten. Removed
   "dormant" verdict; added 6-row publisher table + 5-row
   consumer table + verified end-to-end chain diagram +
   missing-work list.
7. §7 header — added Rigby-style re-ranking into Bucket A
   ("violates runtime policy/auditability") vs Bucket B
   ("just messy") with per-finding mapping.
8. §7.5.1 — cross-referenced to §4.2 corrected list.
9. §11 Risk Matrix — row #1 EventBus severity CRITICAL → HIGH
   with evidence citation; recommendation renamed
   "Adoption + Contract Verification."
10. §12.1 — renamed "Producer/Consumer Map" → "Adoption +
    Contract Verification"; scope rewritten around adoption
    sweep + system-level contract + end-to-end observability.
11. §12.3 — reframed "structural question" → "product/
    architecture decision point" with explicit success
    criteria for BOTH integration and island postures. Chris-
    gated selection.
12. §12.4 — promoted "Identity Resolution for Inter-Employee
    Dispatch" from a narrow P1 mission to a P0-companion
    scoped across 5 cross-domain write paths (agent →
    deliverable; employee mission → DM; PA tool → DB;
    autopilot → runtime; inter-employee dispatch). Rigby's
    framing: hidden prerequisite for making any integration
    canonical.

**Not folded (accepted as-is):**

- Rigby's implied ask to reconcile the 6-file (Agent 4) vs
  9-file (Rigby grep) OpenAI import lists into ONE canonical
  list — flagged in §4.2 as a follow-up audit item; not
  executed in-line because the two sweeps used different
  patterns and a proper reconciliation would need a fresh
  grep with a canonical pattern. Deferred.

### 13.7 Meta-notes on scope discipline (from Agent 6 sweep)

Per Agent 6 pitfall list, this audit deliberately did NOT:

1. Re-inventory the 22 attribution surfaces from S1271 §3 —
   cited instead in §5.5 and §12.4.
2. Re-audit the 64-row collaboration primitives inventory from
   S1268 §2.1 — cited in §3.1 and §12.4.
3. Re-do the 33-incident historical failure catalog from S1272 §8
   — referenced in §12.5.
4. Re-map the 4 governance planes from S1269 §2 — cited in §5.9
   and §12.5.
5. Re-trace the two orchestration paths (Celery vs MissionRunner)
   from S1268 §5 — cited in §5.7 as duplicate_model and §12.7
   as cross-orchestration contract sketch.

Novel S1274 contributions (per Agent 6 §Top 5 novel findings):

1. §6.2 EventBus producer/consumer registry (the biggest missing
   piece).
2. §3 nine detailed missing-connection scenarios traced
   end-to-end.
3. §5–§6 duplicate-model integration lens (what breaks/works if
   resolved).
4. §11 unified cross-domain risk matrix with type + severity per
   finding.
5. §12.4 Identity Resolution for Inter-Employee Dispatch (novel
   composition question).

---

**End of draft. Status: research / draft — Rigby SIGN-with-edits
folded S1274 v2 via isolation pin `pa-7442a2e2665bd18e`
(Medium confidence). Not committed unless Chris explicitly asks.**
