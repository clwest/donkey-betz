---
title: "Cross-Domain Integration Audit — how domains connect, fail to connect, overlap, and violate boundaries"
status: draft (S1274 baseline preserved; post-arc refresh log at §14; v4 appended 2026-07-05)
authority: research
session_added: 1274
last_verified: 2026-07-05
companion_anchors:
  - docs/research/platform_architecture_inventory.md   # 32-domain map (S1273 — parent)
  - docs/research/ARCHITECTURE_INDEX.md                # library navigation (v88 as of S2499)
  - docs/PLATFORM_INVENTORY.md                          # runtime counts anchor
  - docs/EVENT_SYSTEM_INVENTORY.md                     # 14+ event models catalogue
  - docs/EMPLOYEE_OS_PRIMITIVES.md                     # anti-duplication matrix
  - docs/AUDIT_FINDINGS.md                             # Celery deferred list
  - docs/research/governance_authority_evolution.md    # 4 governance planes
  - docs/research/actor_identity_attribution_architecture.md # 19 identity concepts
  - docs/research/domains/memory/1399_memory_canonical_summary.md   # Group 1300 close (S1399, 2026-07-01)
  - docs/research/domains/revenue/1499_revenue_canonical_summary.md # Group 1400 close (S1499, 2026-07-01)
  - docs/research/domains/sports/1599_sports_canonical_summary.md   # Group 1500 close (S1599, 2026-07-02)
  - docs/research/domains/content/1699_content_canonical_summary.md # Group 1600 close (S1699, 2026-07-02)
  - docs/research/domains/observability/1799_observability_canonical_summary.md   # Group 1700 close (S1799, 2026-07-03)
  - docs/research/domains/human_attention/1899_human_attention_canonical_summary.md # Group 1800 close (S1899, 2026-07-04)
  - docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md # Group 1900 close (S1999, 2026-07-04)
  - docs/research/domains/event_integration_architecture/2099_event_integration_architecture_canonical_summary.md # Group 2000+ close (S2099, 2026-07-04)
  - docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md # Group 2100 close (S2199, 2026-07-04)
  - docs/research/domains/frontend/2299_frontend_canonical_summary.md # Group 2200 close (S2299, 2026-07-05)
  - docs/research/domains/auth/2499_auth_canonical_summary.md # Group 2400 close (S2499, 2026-07-05)
verifier_loop: |
  v4 (2026-07-05, post-Group-1700/1800/1900/2000+/2100/2200/2400 arc closes):
  append-only refresh EXTENDING v3 §14 ledger for 7 additional arc
  closes without modifying v3 body or v2 baseline §1-§13. New
  §14.8 through §14.14 subsections capture per-arc deltas (v2
  baseline refinements + NEW cross-domain connections + POSTURE-
  PENDING). §14.1 arcs-closed table extended with 7 new rows.
  §14.6 cross-arc pattern crystallizations extended: CX-P1
  runtime-owner MISSING now 3-of-11 unresolved (Revenue + Sports +
  HumanAttention un-owned; Content UNK-F3 open; Memory + Observability
  + Authority + Event + RAG + Frontend + Auth well-owned OR
  ownership out-of-scope); CX-P4 POSTURE-PENDING as arc-close
  disposition now confirmed at 7 arcs (Sports + Content + Revenue +
  Observability D74 + Authority + Event + Auth); CX-P6 parallel-
  schema drift extended to 3 of 11 closed arcs (Revenue + Sports +
  Observability D74-B dedup unresolved). NEW CX-P7
  declared-but-unenforced-contract pattern (Frontend + Auth
  independently — canonical seam statement across BOTH arcs);
  scope-bounded auth-failure-handling codification candidate CONFIRMED
  at two-trigger threshold (Cat C 92.9% + Cat D 89.5% silent-degrade
  class). NEW CX-P8 monotonically-increasing SIGN confidence across
  child audits within a single arc (Group 2400 Auth Cat A 0.74 →
  Cat B 0.80 → Cat C 0.82 → Cat D 0.85 → xx99 0.88); pattern-
  candidate — method matures across children within an arc. §14.7
  refresh gaps updated: Group 2300 Mobile / 2500 API / 2600 PA
  arcs remain NOT-STARTED; T2 Group 2500 API is the T2 NEXT arc
  per S2299 §8.2 + S2499 §8.4. v2 rows in §2, §3, §4, §5, §6, §11
  remain NOT edited in place; v3 §14.2-§14.7 preserved verbatim;
  readers cross-reference §14.8-§14.14 for latest verdict on any
  domain touched by the 7 new arcs. Playbook §14.5 research
  boundary preserved (no ADRs authored here; only refresh
  bookkeeping).
  v3 (2026-07-03, post-Group-1300/1400/1500/1600 arc closes):
  refresh-log addition WITHOUT modifying v2 body. Reason: v2 §2
  STRONG/WEAK/MISSING/OVERCOUPLED classifications carry Rigby
  SIGN-with-edits ratification from S1274; four subsequent
  research groups (S1300 Memory, S1400 Revenue, S1500 Sports,
  S1600 Content) closed canonical summaries during 2026-07-01 →
  2026-07-02 and produced file:line evidence that CONFIRMS,
  REFINES, or ADDS to the v2 baseline. Preservation discipline:
  new §14 "Post-S1274 Arc-Close Refresh Log" records the deltas
  as an append-only ledger; v2 rows in §2, §3, §4, §5, §6, §11
  are NOT edited in place; readers cross-reference §14 for the
  latest verdict on any specific pair. Playbook §14.5 research
  boundary preserved (no ADRs authored here; only refresh
  bookkeeping). Post-arc anchor-updates from S1399 §7 + S1499
  §7 + S1599 §7 + S1699 §7 that target THIS doc are consumed at
  §14; anchor-updates targeting other docs (INDEX v-bumps,
  platform_architecture_inventory.md subdivisions, new topic
  docs) remain owned by their respective canonical summaries and
  are not folded here.
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

## 14. Post-S1274 Arc-Close Refresh Log (2026-07-03)

### 14.0 What this section is

An **append-only ledger** of cross-domain findings produced by
research arcs that closed AFTER the S1274 v2 baseline was ratified.
Four groups closed 2026-07-01 → 2026-07-02: Group 1300 Memory
(S1399), Group 1400 Revenue (S1499), Group 1500 Sports (S1599),
Group 1600 Content (S1699). Each produced a canonical summary with
file:line-cited evidence directly relevant to this doc.

**What this section is NOT.** A rewrite of §2 tables. An
overwriting of Rigby's S1274 v2 folds. A new §13-style parallel-
Explore sweep. An ADR. All claims cite source-audit `SNNNN §NN.N`
anchors; no new file:line evidence is introduced beyond what the
arcs already established.

**Source scope for §14 (v3 fold F5).** §14 consumes **arc-produced
evidence relevant to S1274 baseline touchpoints** — not "§7 anchor-
update recommendations targeting this doc" as a general framing.
Cross-checked at v3 SIGN: of the four arcs' `§7 Anchor-Update
Recommendations` sections, exactly **one entry** explicitly targets
`cross_domain_integration_audit.md` — the S1499 §7.1.6 "Revenue →
Inbox MISSING" broadening to "Revenue → any outbound channel
MISSING" (consumed at §14.3). All other §14 material is arc file:line
evidence that clarifies, extends, or adds to baseline touchpoints
without being an explicit anchor-update recommendation directed at
this doc.

**Verdict vocabulary:**

- **CONFIRMED** — v2 baseline classification upheld by arc
  evidence with new file:line cite.
- **REFINED** — v2 baseline classification broadened, narrowed,
  or reframed by arc evidence (severity/scope shift preserved).
- **NEW** — cross-domain connection or pattern not present in
  the S1274 15-finding baseline.
- **POSTURE-PENDING (overlay tag — v3 fold F8)** — a governance-
  gated verdict overlay tag that can attach to any of
  STRONG/WEAK/MISSING/OVERCOUPLED/UNKNOWN. **It encodes decision
  state, not wiring state — orthogonal to the baseline
  classes.** When POSTURE-PENDING appears, it implies **ADR owed
  (Chris-gated)** as a distinct prerequisite from
  audit/verification. §14 uses this overlay in composite labels
  like `MISSING + POSTURE-PENDING (remedy)` where the wiring
  classification and the governance-gate are both stated. Do
  NOT read POSTURE-PENDING as a 5th peer classification value.

### 14.1 Arcs closed since S1274 v2

| Arc | Close session | Canonical summary | Close date | Refresh subsection |
|-----|---------------|-------------------|-----------|-------------------|
| Group 1300 Memory | S1399 | `docs/research/domains/memory/1399_memory_canonical_summary.md` | 2026-07-01 | §14.2 |
| Group 1400 Revenue | S1499 | `docs/research/domains/revenue/1499_revenue_canonical_summary.md` | 2026-07-01 | §14.3 |
| Group 1500 Sports | S1599 | `docs/research/domains/sports/1599_sports_canonical_summary.md` | 2026-07-02 | §14.4 |
| Group 1600 Content | S1699 | `docs/research/domains/content/1699_content_canonical_summary.md` | 2026-07-02 | §14.5 |
| Group 1700 Observability | S1799 | `docs/research/domains/observability/1799_observability_canonical_summary.md` | 2026-07-03 | §14.8 |
| Group 1800 HumanAttention | S1899 | `docs/research/domains/human_attention/1899_human_attention_canonical_summary.md` | 2026-07-04 | §14.9 |
| Group 1900 Authority Enforcement | S1999 | `docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md` | 2026-07-04 | §14.10 |
| Group 2000+ Event / Integration Architecture | S2099 | `docs/research/domains/event_integration_architecture/2099_event_integration_architecture_canonical_summary.md` | 2026-07-04 | §14.11 |
| Group 2100 RAG / Document Loading | S2199 | `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md` | 2026-07-04 | §14.12 |
| Group 2200 Frontend (Contract-Surface) | S2299 | `docs/research/domains/frontend/2299_frontend_canonical_summary.md` | 2026-07-05 | §14.13 |
| Group 2400 Auth (Session Lifecycle + Permission Floor + Silent-401) | S2499 | `docs/research/domains/auth/2499_auth_canonical_summary.md` | 2026-07-05 | §14.14 |

Cross-arc pattern crystallizations at §14.6 (updated at v4 with CX-P7 + CX-P8; CX-P1/P4/P6 extended). Refresh gaps at §14.7 (v4 update: Group 2300 Mobile / 2500 API / 2600 PA remain NOT-STARTED; T2 Group 2500 API is next per S2299 §8.2 + S2499 §8.4).

### 14.2 Group 1300 Memory arc (S1399, closed 2026-07-01)

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S1399 verdict | Source anchor |
|-----------|-------------------|---------------|---------------|
| §2.5 Memory (13) → UserAgentLearning (13) | OVERCOUPLED (S1269 F5) | **CONFIRMED** — arc produced full evidence chain; still MEDIUM | S1305 §14 D3/D4 |
| §5.8 Memory / Documents / Embeddings (5+ models — MEDIUM risk) | Data-consistency contract missing | **REFINED to 7 flavors named Cat A–H** (Semantic Knowledge / Personal-Adaptive / Agent Working / RAG Retrieval / Documentation Corpus / Conversational-Thread / Mission Memory delegated / Runtime Correctness). Cat F Conversational/Thread Memory + Cat H Runtime Memory Correctness are FIRST-INVENTORY LANDINGS not present in v2. | S1399 §3.1; S1303 §4; S1305 §14 D1-D10 |
| §11 risk #19 (5+ memory stores) | MEDIUM (S1273 §5.4; Agent 2 §8) | **RESOLVED to arc synthesis** — Group 1300 delivered the store map + 4 arc-wide patterns (F1 provenance-filter drift; F2 orphan-write; F3 Redis-only durability + LRU staleness; F4 CANDIDATE discipline methodology) | S1399 §4 |

**NEW cross-domain connections not on v2 baseline:**

- **Redis 4-DB topology, not 3.** DB 1 Django cache; DB 2 Celery broker; DB 3 Celery results; **DB 5 `AgentLearningService`** raw redis client at `agent_learning_service.py:145` — invisible to Django `cache.clear()`. Doc-drift owed to `docs/topics/infrastructure.md` (3 → 4 DBs). Source: S1305 §14 D8/D9; consolidated at S1399 §3.2.
- **Two RAG lanes, no runtime selector.** LOCAL `core.rag.top_k` on `.rag/corpus.jsonl` vs PROD `core.rag_integration.search_embeddings` via `DocumentEmbedding` + HNSW. `search_docs` hardcodes LOCAL; `kb_tool semantic_search` hardcodes PROD. **PA turn does NOT auto-invoke either lane** (retrieval is tool-call-only). Source: S1301 §7.1; S1399 §3.4.
- **`AgentMemory.create_memory` write-authority MISSING.** No user FK gate, no rate limiting, no audit of who created what. `MemoryPromotionService` auto-saves on every PA turn. **Highest-severity debt item in the Memory arc (T10 HIGH).** Source: S1302 §15 T10; S1399 §6.4. Post-arc write-authority framework ADR queued.
- **`AgentLearningService` within-process consistency gap.** `save_memory:476` writes Redis but never clears the in-process `_user_memories` dict; same-process `get_user_memory:415` short-circuits to dict and returns pre-save entry. Source: S1305 §14 D4.

**POSTURE-PENDING:**

- Turn-context → RAG enrichment: intentional-separation vs drift decision (S1304 §19 R5). Symmetry gap with `BaseAgent._get_relevant_knowledge_for_task` (agents get auto-enrichment; PA does not).

### 14.3 Group 1400 Revenue arc (S1499, closed 2026-07-01)

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S1499 verdict | Source anchor |
|-----------|-------------------|---------------|---------------|
| §2.4 Revenue Pipeline (32) → Initiative Pipeline (12) | MISSING (Agent 3 §2.6) | **CONFIRMED** — no `Opportunity → Initiative` code path exists | S1401 + S1405; S1499 §5.1 row 4 |
| §2.4 Revenue Pipeline (32) → Observability (25) | STRONG via `ImpactEvent` at `ops_autopilot/impact.py:375+` | **REFINED (evidence pointer corrected)** — attribution algorithm at `core/services/ops_autopilot/impact.py::MultiTouchAttributor._attribute_event:1233-1290` (70% last-touch / 30% assist); parent scoping doc named wrong file | S1405 §14 F.E6 |
| §2.4 Revenue Pipeline (32) → Inbox (17) | MISSING; outbound channel UNKNOWN (S1273 §10.3) | **REFINED (broadened)** — "Revenue → any outbound channel MISSING," not just Inbox. Grep-negative at HEAD `beda00e5` for `send_outreach\|dispatch_outreach\|deliver_outreach\|outreach.send` + `sendgrid\|postmark\|mailgun\|smtplib\|EMAIL_BACKEND` (0 mainline hits). Scope now spans email + LinkedIn + Rigby-DM + in-app — **no channel exists at all**. | S1402 §14 F.B1; S1499 §7.1.6 |
| §2.4 Revenue Pipeline (32) → HumanAttention (16) | MISSING (Agent 3 §2.6) | **CONFIRMED arc-wide** — zero HAI writers from Meeting/ClosePack/CloseTheDealEngine/ClosePackAutonomyEngine (arc-wide 0.07% ops_autopilot, 2 rows of 3061). Approval gates procedural-at-operator-judgment only, not schema-enforced. | S1404 §14 F.D1; S1499 §5.1 row 6 |
| §11 risk #36 (Revenue Pipeline no runtime owner HIGH) | HIGH; Pipeline agents lack JobContracts; no beat | **RESOLVED (proposed)** — UNANIMOUS across all 6 children. D55 (ii) resolution: **two sibling JobContracts** — Revenue Employee (Cat A/B/C/D/E) + Income/Jobs Employee (Cat F, gated on T4 dormancy disposition). Employee OS 1200s arc owns implementation. | S1499 §4.5, §7.4; D55 |

**NEW cross-domain connections not on v2 baseline:**

- **Learning-bridge fires on core `Revenue` only, not intelligence `RevenueRecord`.** `revenue_attribution_bridge.py:227` writes `UserAgentLearning` on core Revenue rows; intelligence `RevenueRecord`/`RevenueSource`/`ProposalTracker` orphaned from the bridge. **Dual-schema drift F.E3 CONFIRMED HIGH.** Chris/Rigby architectural decision required — missing bridge vs intentional source-of-truth hierarchy. Source: S1405 §14 F.E3; S1499 §3.3, §6.4.
- **Cat F Freelance/Gig lane orphaned from `ImpactEvent` → learning chain entirely.** Zero `ImpactEvent` writes from any of 10 Cat F files (grep-negative). Freelance lifecycle → revenue → attribution → learning chain completely severed. Source: S1406 §14 F.F6; S1499 §4.4.
- **20-writer convergence on `Opportunity` mainline with zero canonical write-authority contract.** Dominant `spider_decision_bridge.py` at 2630 rows (99.96%); 19 non-dominant writers UNCLASSIFIED (tests / migrations / dead code / legitimate alternate ingestion). Consolidates F.A1 dual-representation + F.E3 dual-schema into single parallel-schema umbrella. Source: S1406 §14 F.F2; S1499 §3.3, §5.2.
- **`_impl_run_freelance_opportunity_scout` UNGUARDED 5-phantom-field writer.** At `core/tasks_ops.py:2239-2251` — runtime `FieldError` guaranteed if invoked. Task not beat-scheduled locally; PROD status UNKNOWN. Source: S1406 §14 F.F1.

**POSTURE-PENDING:**

- T1 parallel-schema + source-of-truth ADR (Revenue schema vs realtime intelligence_engine).
- T5 outreach delivery ADR (SendGrid/Postmark/SES/Mailgun/LinkedIn/Rigby-DM).
- T6 HumanAttention interlock ADR (ship-to-go-live prerequisite).
- T7 write-authority + routing-authority framework ADR (8-site F2 remediation).
- T8 state-machine completion ADR (16 declared / 6 reachable across `Meeting`/`ClosePack`/`OpportunityRevenue`/`OpportunityOutcome`).

**Content ↔ Revenue delivery gap** (2-of-2 pattern, cross-linked to §14.5): `OutreachDraft` + Newsletter both content-generation-only ZERO outbound at HEAD. See §14.5 Content perspective.

### 14.4 Group 1500 Sports arc (S1599, closed 2026-07-02)

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S1599 verdict | Source anchor |
|-----------|-------------------|---------------|---------------|
| §2.2 Sports/DBAO (10) → Signal Engine (9) | MISSING — `sports_odds` is not a valid `SignalCluster` data_type track (S1273 §3.10) | **MISSING + POSTURE-PENDING (remedy)** — wiring class MISSING is confirmed; 6-arc consumer-side pattern COMPLETED (P11) extends S1274 §14 finding #6 with zero `SignalCluster` emit from any of 5 market agents + coordinator (Cat B), wager settlement (Cat C), betting content pipeline (Cat D), frontend (Cat E), Cat F. **Remedy is Chris-gated** — extend enum vs build sports-native aggregator (T1 R.SPORTS.POSTURE). See §14.0 POSTURE-PENDING overlay-tag definition. | S1502 §14.3; S1503 §14.3; S1504 §14; S1505 §14.6; S1506 §14; S1599 §4 P11 |
| §2.2 Sports/DBAO (10) → Revenue Pipeline (32) | MISSING — Betting outcomes not fed to opportunity attribution | **CONFIRMED** — no bridge exists at HEAD; posture-tied to T1 R.SPORTS.POSTURE | S1599 §9 |
| §14 finding #6 (SignalCluster pattern_type) | HIGH — Sports cascade absent | **CONFIRMED and extended to 6-arc pattern** as above | S1599 §4 P11 |

**NEW cross-domain connections not on v2 baseline:**

- **`BettingOutcomeVerifier` ↔ `MLPrediction` DECOUPLED-VERIFICATION-SYSTEMS (CRITICAL).** Two independent verification pipelines run without cross-reference; zero FK, zero method call, zero shared join. **Retrain loop cannot close.** Prediction correctness is set by a separate task `evaluate_ml_predictions` at `core/tasks.py:6192`. Source: S1506 §14.2 F.F2; S1599 §4 P2. **Within-Sports connection MISSING** — this is a cross-service boundary within the same domain that behaves like a cross-domain gap.
- **Sports → Memory PARTIAL bridge (5-arc pattern).** `SportsBettingLearningBridge.record_wager_outcome()` at `core/learning_bridges/sports_betting_bridge.py:532, 606` writes `AgentMemory` + `UserAgentLearning` for **2 of 4 market agents**; zero `AgentKnowledgeSource` writes. Extends S1274 baseline row 305 (HumanAttention → Memory STRONG) with a Sports-specific partial coverage. Source: S1506 §14.6 F.F6; S1599 §4 P12.
- **DBAO codename NAMING-CONVENTION-WITHOUT-MATERIALIZATION (CRITICAL).** 6 declared artifacts (schema + 2 WS routes + env-vars + header) with **zero runtime state** and 2 unimplemented handler stubs. `docs/research/domains/sports/1500_sports_domain_scoping.md` §3.10 first surfaced; S1506 §14.1 F.F1 confirmed. Chris-gated ADR post-arc — materialize / demote / archive. Source: S1506 §14.1; S1599 §5.7 D61 parked.
- **`/ws/dbao/` + `/ws/dbao-dashboard/` MOCK-DATA-CONSUMER (CRITICAL).** `NewPagesConsumer.send_dbao_metrics` at `core/new_pages_consumer.py:310-331` synthesizes every metric field via `random.randint()` + `random.uniform()`; passes client-side authenticity heuristics. Source: S1505 §14.1 F.E1; S1506 §14.7. **Boundary violation** — belongs at §7 alongside asymmetric-auth patterns.
- **`RealtimeIntelligenceEngine` SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION (HIGH).** Cross-domain loops named as cross-domain in code + docs but populated with hardcoded demo data. Source: S1506 §14.9 F.F5.
- **`sports_intelligence: True` DECLARED-FEATURE-FLAG-GATES-NOTHING (HIGH).** Hardcoded literal reported as capability but consulted nowhere at runtime. Source: S1506 §14.4 F.F3.
- **Discord HOT-PATH-CHOKE bypass (HIGH).** `/odds` + `/futures` + `/slip` Discord commands instantiate `TheOddsSpider` directly instead of routing through `SportsBettingCoordinator`. Boundary violation — belongs at §7 Class 5 (Agents/Modules Bypassing Shared Primitives). Source: S1504 §14; S1506 §14.5.
- **`verify_betting_outcomes` beat ZERO-FIRE (CRITICAL).** Neither task variant (`core.tasks.verify_betting_outcomes` OR `sports.tasks.verify_betting_outcomes`) has a `PeriodicTask` row or `core/celery.py` beat entry. Rigby ORM probe returns zero `CeleryTaskEvent` firings for both variants over 30d. **Pre-restore-beat idempotency gate required BEFORE beat restoration** (`_settle_wager()` lacks `select_for_update()` + `@transaction.atomic()`). Source: S1503 §14.1 + §15.14.
- **`daily_betting_digest` beat ZERO-FIRE (CRITICAL).** Same class as `verify_betting_outcomes`; docstring claims "8 AM MST daily"; no beat entry; `CeleryTaskEvent` 30d = 0. Source: S1504 §14.1 F.D1.
- **Fixture / entity identity unresolved (P13 2-arc pattern).** TheOdds `event_id` vs Kalshi `ticker` vs `sports.models.Game.external_id` live in different namespaces; no reconciler; `Game.get_or_create(external_id=event_id)` creates duplicates when the same fixture is referenced by different vendor IDs. Source: S1501 §14.2; S1502 §15 debt #12.
- **`SportsBettingBrief` WRITE-ONLY-FORGOTTEN (HIGH).** 2 writers (Cat D shim + Session 1000 pipeline); 0 readers. REST endpoint `get_betting_brief` at `core/views_odds_sports.py:3237` computes on-the-fly via `SportsBettingCoordinator.generate_brief()`, never reads persisted model. Cross-arc: also flagged by Cat D of the Content arc (see §14.5). Source: S1504 §14.3 F.D3; S1505 §14.4.

**Four-axis compound maturity shape.** Sports domain maturity is not one category but four compound axes: (1) DBAO product-line materialization — NAMING-CONVENTION-WITHOUT-MATERIALIZATION; (2) Intelligence surface — DECLARED-FEATURE-FLAG-GATES-NOTHING at flag layer + LATENT-ZERO-FIRE at engine layer + DOMAIN-NEUTRAL at REST/frontend layer; (3) Discord sports surface — HOT-PATH-CHOKE-BYPASS at read commands + WORKING at write commands + DUAL-COORDINATOR-BYPASS at periodic digest; (4) Cross-domain feedback — DECOUPLED-VERIFICATION-SYSTEMS + PARTIAL-LEARNING-BRIDGE + zero SignalCluster emission. Source: S1599 §1, §3.5.

**POSTURE-PENDING:**

- T1 R.SPORTS.POSTURE Chris-gated ADR (integration vs island) — blocks T2 `SignalCluster` shim vs sports-native aggregator; blocks T2 Discord surface refactor; blocks T3 Memory arc learning-bridge upgrade.
- T1 R.DBAO.CODENAME Chris-gated ADR — materialize / demote / archive.
- T2 `SportsBettingBrief` consumer-or-remove ADR (posture-tied).

### 14.5 Group 1600 Content arc (S1699, closed 2026-07-02)

**Content ↔ 7 cross-domain surfaces (S1699 §3 consolidated map + Cat F §20 evidence plan). This is the Content perspective on cross-domain integration and complements the domain-outward classifications in v2 §2.**

| Content ↔ Target | Verdict | Anchor |
|------------------|---------|--------|
| Content → Signal Engine | **WORKING consumer.** `ClaimsPackBuilder` consumes `SignalCluster` (active) + `LegacySpiderData` (72h window) + `DocumentEmbedding` (cosine similarity) as three-source assembly. | S1601 §7, §14; S1699 §3 |
| Content → Sports | **PARTIAL.** `SportsContentContextBuilder` HOT-PATH-CHOKE-BYPASS (Discord fast path bypasses); `SportsBettingBrief` WRITE-ONLY-FORGOTTEN cross-confirmed with §14.4. | S1504 §5.1; S1504 §14.3; S1699 §3, §4.1 |
| Content → Revenue | **EXPERIMENTAL (2-of-2 ZERO outbound).** `OutreachDraft` + Newsletter both content-generation-only ZERO outbound at HEAD. See cross-arc pattern in §14.6. | S1699 §4.1; cross-links S1402 F.B1 (see §14.3) |
| Content → Memory | **INPUT STABLE; PIPELINE-SIDE OUTPUT ABSENT (PA-tool feedback bridge PARTIAL).** `_record_content_feedback` at `td_handlers_content.py:184` (8 call sites) writes operator feedback to `AgentMemory`; pipeline-side verdict → memory bridge does NOT close. `ContentLearningLoopBridge` PARTIAL not ABSENT (F6 fold correction). | S1606 §9.4; S1699 §3, §4.5, §5.7 Contradiction 1 |
| Content → Discord | **PARTIAL (fire-and-forget).** Discord broadcast rail has ZERO gate integration; no retract path (immutable-once-broadcast). | S1604 §14; S1699 §3 |
| Content → Frontend | **INTEGRATED API + ISLAND auth.** 2 adapters at HEAD (blogsApi + deliverablesApi; `newsletterApi` NOT present per F1 Cat F self-caught grep 0-hit correction); REST + Frontend auth boundary asymmetric-CRITICAL. | S1606 §1.1; S1699 §5.7 Contradiction 4 |
| Content → Employee OS | **PARTIAL governance layer (Documentation Manager overlap).** UNK-F3 open: whether a Content Employee analog to D55 is warranted or whether the Documentation Manager `JobContract` on RIGBY already covers Content-adjacent authority. | S1699 §6.1 UNK-F3, §9.1 |

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S1699 verdict | Source anchor |
|-----------|-------------------|---------------|---------------|
| §2.3 Content Pipeline (11) → Inbox (17) | MISSING — Deliverable status → notification (Agent 3 §2.2) | **CONFIRMED and extended.** Post-publish correction structurally ABSENT across all 3 rails (Discord broadcast fire-and-forget; Newsletter dry_run parked >4mo with ZERO live-send infrastructure; Frontend approve/publish has no un-approve or retract). | S1604 §14 T.15.C1/T.15.C2; S1699 §4.3 |
| §2.3 Content Pipeline (11) → PA (1) via Rigby intake | WEAK — `DeliverableEvent → rigby_event_intake` gated by `RIGBY_EVENT_INTAKE_ENABLED=False` (Agent 3 §3.1) | **REFINED** — 4-tool Cat E surface (`content_tool` + `deliverable_tool` + `content_review_panel` + `newsletter_tool`) is WORKING with tactical split, but REST + Frontend surfaces carry ZERO auth decorator CRITICAL asymmetric-auth-boundary. | S1605 §14 T.15.E2, T.15.E3; S1699 §3 |

**NEW cross-domain connections not on v2 baseline:**

- **`auto_publish_approved_blogs` beat MISSING at HEAD despite 5 doc sources claiming "daily 6 AM."** RUNTIME-CONFIRMED via `ops_tool.celery_task_history` (30d = 0 events) + `scheduled_tasks_tool` (0 filtered). **Beat NEVER FIRES.** 5 doc PRs owed at Content arc §7.4 (topic doc + narrative + `AUDIT_FINDINGS.md` + CLAUDE.md autoblock + prior handoffs). `S1604 D.14.C5` audit-trail gap MOOT because beat never fires. Cross-arc CORRECTION pattern (S1605 F1 → S1606 F8 → S1699 §5.7 Contradiction 5). Source: S1605 §14 T.15.E4; S1606 §14 F8; S1699 §5.7 Contradiction 5.
- **Post-publish correction structurally ABSENT arc-wide.** Zero retract / errata / unpublish paths at HEAD across all publish surfaces. If integration posture D65c selected, this is P1 multi-quarter `ContentLifecycleEngine` remediation; if island posture selected, per-rail ADR required. Source: S1604 §14 T.15.C1; S1699 §4.3.
- **Newsletter live-send infrastructure ABSENT (CRITICAL).** dry_run parked >4mo; EXPERIMENTAL. Source: S1604 §14 T.15.C2; S1699 §3.
- **Triple-gate composition contract MISSING (HIGH).** PublishGate is SelfBlog-only at HEAD; no unified gate that composes Deliverable + variant + rail. Source: S1604 §14; S1699 §4.
- **Silent-partial-source failure at Cat A pipeline (HIGH).** Three try/except blocks in `ClaimsPackBuilder` swallow source failures independently; pipeline continues degraded without a degraded-status contract to consumers. Source: S1601 §14 F2; S1699 §4.2.
- **RAG workspace-scoping CRITICAL (riskiest Content arc finding).** Absent at HEAD. Source: S1601 §14 F4; S1699 §1.
- **`SportsBettingBrief` + `BlockchainAuditBrief` — UNFINISHED-ORPHAN Deliverable variants (CRITICAL).** Confirms §14.4 finding from Content side; cross-arc handoff T1.h `SportsBettingBrief` consumer-or-remove ADR re-scope. Source: S1603 §1; S1699 §9.

**POSTURE-PENDING (four orthogonal Chris-gated ADRs, D65a-D65e):**

- **D65a Deliverable canonicalization** — container-level integration vs island (SelfBlog factory adoption complete vs 5 structural-island variants preserved).
- **D65b PublishGate canonicalization** — gate-level SelfBlog-only extendable to variants vs per-variant gates.
- **D65c Lifecycle transition ownership** — orchestrator-level unified `ContentLifecycleEngine` vs per-rail correction.
- **D65e Rigby PA-tool + enforcement centralization** — cross-boundary UnifiedContentAuthLayer vs per-surface auth ADR.

### 14.6 Cross-arc pattern crystallizations

Patterns visible only from the multi-arc vantage that this refresh
section provides. Each cites the arc-anchors where it was
independently surfaced.

**CX-P1 — Runtime-owner MISSING pattern.** S1274 §14 finding #36
identified this for Revenue (HIGH). Group 1400 confirmed
**UNANIMOUS 6/6** and proposed D55 two-sibling JobContract
resolution. Group 1300 Memory arc did NOT hit this pattern (Memory
scope has clear ownership per surface). Group 1500 Sports arc has
NO JobContract for the sports domain either (Cat F §5.4) —
extending the pattern to a second unresolved domain. Group 1600
Content arc UNK-F3 preserves the question of whether Content
needs a JobContract or the Documentation Manager on RIGBY covers.
**Consolidated status: 2 of 4 closed arcs identify runtime-owner
MISSING as a load-bearing gap (Revenue + Sports); 1 open
(Content); 1 well-owned (Memory).** Anchor: S1499 §4.5; S1599
§5.4; S1699 §6.1 UNK-F3.

**CX-P2 (single-arc / cross-domain artifact) — Write-only-forgotten
variants.** *(cross-domain within a single arc; promote to full CX
once corroborated by a second arc — v3 fold F6 scope-honest
rename.)* Same pattern class recurred across Deliverable variants
(SportsBettingBrief 2 writers 0 readers + BlockchainAuditBrief
same shape) with an identical remediation shape: "consumer-or-
remove ADR." The two variants span Sports-adjacent and Content-
adjacent domains but were surfaced within a single arc (Group 1600
Content Cat D), not independently across two arcs — the honest
scope is "cross-domain artifact discovered inside one arc." Content
arc §9 T1.h explicitly delegates `SportsBettingBrief` consumer-or-
remove decision back to Sports arc T2 post-arc slate, posture-tied
to Sports T1 R.SPORTS.POSTURE. Anchor: S1504 §14.3; S1505 §14.4;
S1603 §1; S1699 §9.

**CX-P3 — ZERO outbound delivery pattern class.** Content arc §4.1
identifies 2-of-2 at Content ↔ Revenue level: `OutreachDraft` +
Newsletter both content-generation-only ZERO outbound at HEAD.
Root cause traces to S1402 F.B1 (Revenue arc) — pattern predates
Group 1600. UNK-F2 preserves the open question of whether the
pattern class unifies to 3-of-3 (with `BlockchainAuditBrief` from
Sports-adjacent) OR represents three separate delivery domains.
**Consolidated status:** Content arc §5.7 Contradiction 2 F3 fold
resolved to 2-of-2 for this doc's purposes; unification decision
Chris-gated post-arc. Anchor: S1402 §14 F.B1; S1699 §4.1, §5.7
Contradiction 2.

**CX-P4 — POSTURE-PENDING as an arc-close disposition (overlay-tag
framing per v3 fold F8).** Sports arc closed with T1 R.SPORTS.POSTURE
+ T1 R.DBAO.CODENAME un-resolved BY DESIGN (Cat F consolidates
evidence; Chris ADR resolves post-arc). Content arc closed with 4
orthogonal Chris-gated posture axes (D65a/b/c/e) un-resolved BY
DESIGN. Revenue arc closed with T1 parallel-schema + T4 income-lane
dormancy (latter resolved (b) dormant-planned at S1499). Memory arc
did NOT surface a posture-pending axis. **Consolidated status:
POSTURE-PENDING is now a recognized close disposition, distinct
from CANDIDATE (unverified evidence) — but it does NOT compete with
the v2 baseline classes (STRONG/WEAK/MISSING/OVERCOUPLED/UNKNOWN).**
POSTURE-PENDING encodes *decision state* (governance-gate); the v2
baseline classes encode *wiring state*. The two axes are orthogonal:
a connection can be MISSING + POSTURE-PENDING (Sports → Signal
Engine at §14.4), WEAK + POSTURE-PENDING (a hypothetical partially-
wired-pending-ADR case), etc. A future v4 §2 refresh would surface
POSTURE-PENDING as an **overlay tag column** alongside the existing
classification column, not as a replacement value. Do NOT read
POSTURE-PENDING as a 5th peer classification — that framing was
removed in v3. Anchor: §14.0 vocabulary; S1599 D59 posture-decision
framing; S1699 D65a/b/c/e four-axis handoff.

**CX-P5 — Meta-methodology §10 template propagation.** All 4
arcs applied the playbook §11.3 §10 "What This Research Taught
Us About How to Do Research" section (S1399 first; S1499 second;
S1599 third; S1699 fourth). Distinct from cross-domain
connections but load-bearing for how future arcs will be run
against the surfaces this doc catalogs. Playbook v3 candidate
patterns MET across arcs: F1/F4-CANDIDATE discipline; sibling-
inheritance hypothesis-correction; docs cascade at every close;
meta-methodology §10 as canonical-summary requirement; D48
stability-probe gate + warmup-ping (11-consecutive-clean-arms
sub-pattern at S1699 close). Sub-pattern (per v3 fold, adjacent
to CX-P5): **candidate-state discipline (F1/F4) propagates
across arcs as a gating mechanism for claims** — claims stay
CANDIDATE until owner-model-qualified consumer inventory lands;
this discipline is visible in Memory + Revenue arcs and is a
methodology property, not a system-crystallization property.
Anchor: S1399 §10.2; S1499 §10.2; S1599 §10.2; S1699 §10.2.

**CX-P6 — Parallel-schema drift (mainline vs intelligence/demo
planes) (NEW, v3 fold F7).** Multiple arcs surfaced the same
architectural class: **two schemas or two representations of the
same conceptual entity exist in parallel with no declared source-
of-truth hierarchy or bridge**. This is not "schema drift" in the
narrow sense — it is **parallel-plane representation drift**
(mainline vs intelligence / demo / realtime plane), which produces
a false "integrated" posture at read-side while data flows silently
diverge. Independently confirmed at 2 arcs minimum:

- **Revenue arc S1499:** core `Revenue`/`OpportunityRevenue`/`OpportunityOutcome`
  (mainline Django) vs intelligence `RevenueRecord`/`RevenueSource`/`ProposalTracker`
  — `revenue_attribution_bridge.py:227` fires on core `Revenue` only;
  intelligence-side orphaned. F.E3 CONFIRMED HIGH. Umbrella track
  T1 R.E3 ADR post-arc. Anchor: S1405 §14 F.E3; S1499 §3.3.
- **Revenue arc S1499 (Discovery lane variant):** mainline Django
  `Opportunity` (persistent) vs `intelligence_engine.get_current_opportunities()`
  (in-memory realtime, 5 consumer sites at `OpportunityScannerConsumer`).
  Sync contract UNKNOWN. F.A1 CONFIRMED HIGH. Same class as above;
  operational implications differ (cache staleness, WebSocket read
  semantics). Anchor: S1401 §14 F.A1; S1499 §3.3.
- **Sports arc S1599:** intelligence-vs-mainline drift throughout
  Cat F — `RealtimeIntelligenceEngine` SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION
  (cross-domain loops named as cross-domain in code/docs but populated
  with hardcoded demo data); `/ws/dbao/` + `/ws/dbao-dashboard/`
  MOCK-DATA-CONSUMER (synthesizes every metric field via
  `random.randint()` + `random.uniform()`); DBAO codename
  NAMING-CONVENTION-WITHOUT-MATERIALIZATION (6 declared artifacts
  + zero runtime state). **Sports arc four-axis compound maturity
  frames this as its own axis (Intelligence surface — DECLARED-
  FEATURE-FLAG-GATES-NOTHING at flag layer + LATENT-ZERO-FIRE at
  engine layer + DOMAIN-NEUTRAL at REST/frontend layer).** Anchor:
  S1506 §14.1, §14.7, §14.9; S1599 §3.5 four-axis synthesis.

**Consolidated status: 2 of 4 closed arcs surface this pattern
class independently, with same root cause (no declared source-of-
truth hierarchy) but different operational surfaces (persistence
divergence vs realtime representation divergence vs demo-vs-live
plane split).** Umbrella track: post-arc design-preparation ADR
should decide reconciliation policy per axis (integration =
missing bridge; island = intentional plane separation with
explicit contract). Cross-references: Revenue T1 R.E3 + Revenue
T1 R.A1 + Sports T1 R.SPORTS.POSTURE + Sports T1 R.DBAO.CODENAME
all feed this decision.

**v4 fold note (2026-07-05, post-Group-1700-through-2400 closes).**
CX-P1 extends to 11 closed arcs analysis: **3 of 11 unresolved runtime-owner
gaps** (Revenue + Sports + HumanAttention un-owned; Content UNK-F3 open;
Memory + Observability + Authority + Event + RAG + Frontend + Auth
well-owned OR ownership out-of-scope). Frontend arc §4.1 no-CODEOWNERS
+ LIGHT-ownership finding (S2201 F4) extends the pattern to a **static
governance layer** distinct from runtime dispatch ownership. Auth arc
F-D-OWN-1 CODEOWNERS absent + F-D-OWN-2 CI test-harness absent are
classified as governance NON-silent-degrade class (see CX-P7 below) —
same underlying pattern, different classification lens. **CX-P4 confirmed
at 7 arcs** now (Sports + Content + Revenue + Observability D74 + HAI
D80 + Authority + Event + RAG post-arc T-slots + Auth Cat B a/b/c +
Cat C α/β/γ + Cat D α/β/γ × 2). POSTURE-PENDING is stable close-
disposition class. **CX-P6 parallel-schema drift extends to 3+ arcs**
(Revenue F.E3 + F.A1 + Sports Cat F + Observability D74-B DEEP-WIRED-BUT-
DEDUP-UNRESOLVED for LLM-telemetry duplication). Still not 4+ arcs;
umbrella track un-resolved at Group 2400 close. **CX-P5 meta-methodology
§10 template propagation extends to 11 canonical summaries** (S1399 through
S2499 without exception; ELEVENTH-consecutive at S2499 close).

**CX-P7 — Declared-but-unenforced contract pattern (NEW at v4).** Two
arcs independently converged on canonical seam statements describing
the same architectural posture: **a mechanism declares a contract but
the runtime does not enforce it.** Group 2200 Frontend §5.1: "accreted
UI mesh with declared-but-unenforced contracts — structurally healthy
at the routing/auth-wrapper/layout/Zustand-persist boundary but
structurally under-specified at the page-component/consumer-contract/
API-typing/state-discipline boundary." Group 2400 Auth §1: "ACCRETION
with declared-but-unenforced contracts. Mechanisms generally work at
file-precision in the sampled surfaces; contract silently violated
across all four contract axes examined." **Same architectural posture,
different domains, independent framings.** Instances span both arcs:

- **Frontend arc:** drf-spectacular is sports-wired but not platform-wide;
  Zustand persist is 3-of-7-stores-adopted; `ui.render_hint` envelope is
  0-of-40-conformant; error boundaries are 0-adopted.
- **Auth arc Cat A:** VIP demo declares read-only for `vip_demo_viewer`
  role (prompt-only injection) but PA has no runtime gate on write ops;
  FleetSignatureAuthentication declares HMAC signature check but
  permissive fallback silently passes unverified callers.
- **Auth arc Cat B:** DRF default TokenAuthentication declares
  IsAuthenticated inheritance for ~80-90% of endpoints implicitly, but
  rate UNOBSERVABLE (no registry + no CI test-harness); STAFF_REQUIRED_PATHS
  declares 3 gated paths but 2 of 3 are phantom entries.
- **Auth arc Cat C:** VIPInvite.account_expires_at (14d) declared as
  field in model + returned in response body but NEVER checked at
  runtime (declared-fictional class introduced by Cat C).
- **Auth arc Cat D:** api.ts:47 inline comment declares "Only redirect
  to login for explicit auth endpoints / Other 401s should be handled
  by the component" — implying component-level handling — but 0 typed
  AxiosError catches + 0 error boundaries + ~99% silent-swallow rate
  means the "handled by the component" contract is NOT enforced;
  Sidebar.tsx:356 declares logout via authStore.logout() but does NOT
  call authApi.logout() — declares logout without backend revoke.

**Consolidated status: 2 of 11 closed arcs surface this pattern class
independently, framed via canonical seam statements at both arc closes.**
Two-trigger threshold met per playbook §20 codification rule; scope-
bounded promotion candidate. Umbrella track: **Group 2500 API arc
opening will re-test the pattern class** — does the pattern extend to
backend API contract SoT, or does it stay bounded to Frontend + Auth?
The two-sided FE-symptom-vs-BE-model discipline of Cat B ROOT CAUSE +
Cat D SYMPTOM (§14.14) suggests the pattern is not solely a frontend
artifact. Anchor: S2299 §5.1; S2499 §1; S2499 §4.1 (Cat D + xx99
6-cross-cutting-patterns).

**CX-P8 — Silent-degrade-vs-explicit-failure ambiguity codification
candidate (NEW at v4).** Cat C Group 2400 Auth (S2403) surfaced 13-of-14
findings as silent-degrade class (92.9%) as playbook §20 codification
TRIGGER #1. Cat D Group 2400 Auth (S2404) surfaced 17-of-19 findings
as silent-degrade class (89.5%) as TRIGGER #2. Both above threshold;
two-trigger requirement met. **Tightened scope-bounded codification
(xx99 Rigby SIGN Q3 fold):** promote to playbook v3 candidate focused
on **auth failure handling (401/403/refresh/logout) with explicit UX +
telemetry requirements** — NOT general silent-degrade-anywhere
codification. **Conditional promotion rule:** general codification if
a 3rd trigger surfaces in a non-auth plane (Groups 2500 API / 2600 PA
/ 1700 Observability). Anchor: S2403 §14 silent-degrade rate + S2404
§14.1 silent-degrade rate + S2499 §10.2 codification claim.

**CX-P9 — Monotonically-increasing SIGN confidence across child audits
within a single arc (NEW-CANDIDATE at v4; pending 2nd arc for confirmation).**
Group 2400 Auth arc exhibited monotonically-increasing Rigby SIGN
confidence across children: Cat A 0.74 → Cat B ~0.80 → Cat C ~0.82 →
Cat D ~0.80-0.85 → xx99 ~0.88. Evidence that the arc's method matured
across children. Pattern-candidate — waiting for a future arc to
independently exhibit monotonicity. If confirmed, playbook v3 note
about arc-open-vs-arc-close method-drift discipline could crystallize.
Not yet strong enough for codification. Anchor: S2401-S2499 SIGN
confidence ledger; S2499 §11 arc change log.

**CX-P10 — Design-complete + runtime-scaffolding verdict class as
close disposition (NEW at v4).** Three arcs closed with the same
verdict class: **specification consolidated + Chris-ratified via multiple
"agree all" rounds; runtime binding not yet wired.** Group 1900 Authority
Enforcement (S1999) — 17 design decisions ratified; only Boundary 5
warn-mode observation event fires; enforce_authority_mode field ABSENT
at HEAD. Group 2000+ Event/Integration Architecture (S2099) —
design-complete, runtime-scaffolding, closure-gated on 4 T1 items.
Group 2100 RAG/Document Loading (S2199) — design-governed corpus
substrate spec-complete via P3, evidence-supported via P4, execution-
pending. **Consolidated status: 3 of 11 closed arcs close with
design-complete/runtime-scaffolding class**, distinct from CX-P4
POSTURE-PENDING (governance-gate un-resolution). Design-complete
encodes *specification state* (Chris-ratified); POSTURE-PENDING encodes
*decision state* (Chris ADR needed to select from options). The two
classes are orthogonal. Anchor: S1999 §1; S2099 §1; S2199 §1.

### 14.7 Refresh gaps and future arc coverage

**What §14 does NOT refresh (v4 update 2026-07-05).**

- Domain pairs where no arc has closed since S1274 AND no arc from
  the v3/v4 refresh has touched them: Body Systems ↔ *; Advisors
  persistence; Inbox fanout; Web Push wiring; Mobile Expo push UI.
  These retain v2 classifications unchanged. **NEW at v4:** HumanAttention
  ↔ Governance surface refined at §14.9 + §14.10 (Group 1800 + Group
  1900 both closed since v3).
- Cross-domain connections involving domains with active but
  unclosed arcs. As of 2026-07-05: **NONE currently in-progress**
  (Group 2400 Auth closed at S2499 2026-07-05; T2 Group 2500 API is
  the T2 NEXT queued arc per S2299 §8.2 + S2499 §8.4 but has not
  opened yet). When Group 2500 API opens + closes, §14.15 (new
  subsection) will add API-side refinements.
- Boundary violations at §7 refined by arc evidence. **NEW at v4:**
  Frontend arc §4.4 DEAD-CANDIDATE/MOCK-DATA/INTENT-NEUTRAL pattern
  class recurrence at §14.13 + Auth arc F-D-BYPASS-1 79 raw fetch
  interceptor-bypass + F-D-SIDEBAR-1 backend-token-not-revoked
  boundary at §14.14 all worth §7 augmentation. These are noted in
  §14 but §7 itself is preserved from v2 per append-only discipline.
- §11 risk matrix additions. **NEW at v4:** Auth arc P0 rank-1
  co-equal batch (14 items with Cat D Rigby Q15 fold tiered ordering
  P0-A/B/C) is not slotted into v2 §11 numbered ranking. Silent-401
  SYSTEMIC + 803-consumer-call-site surface would rank at top of a
  re-ranked §11. A future v5 refresh could integrate §14.8-§14.14
  findings into re-ranked §11.

**What the queue looks like (v4 update 2026-07-05).** Per
`docs/research/OPEN_ARCS.md`:

- Group 1700 Observability / Telemetry / SLOs — **CLOSED at S1799
  2026-07-03; §14.8 delivered.**
- Group 1800 HumanAttention / Feedback / Learning — **CLOSED at
  S1899 2026-07-04; §14.9 delivered.**
- Group 1900 Authority Enforcement — **CLOSED at S1999 2026-07-04;
  §14.10 delivered.**
- Group 2000+ Event / Integration Architecture — **CLOSED at S2099
  2026-07-04; §14.11 delivered.**
- Group 2100 RAG / Document Loading — **CLOSED at S2199 2026-07-04;
  §14.12 delivered.**
- Group 2200 Frontend (Contract-Surface) — **CLOSED at S2299
  2026-07-05; §14.13 delivered.**
- Group 2400 Auth — **CLOSED at S2499 2026-07-05; §14.14 delivered.**
- Group 2300 Mobile — NOT STARTED. Post-S2099 project memory queue
  ranking placed after Auth per Chris D-override at S2199 close.
  Will re-audit Mobile Expo push UI + MobilePushToken.revoked_at
  cascade + mobile-side 401-handling parity (Auth CF-D4 delegation).
- Group 2500 API — **NOT STARTED; T2 NEXT** per S2299 §8.2 + S2499
  §8.4. Chris-gated open. Will consume Group 2400 4-axis handoff
  bundle (refresh endpoint + logout envelope + Clear-Site-Data +
  typed-error-envelope Cat D α/β/γ + per-endpoint permission registry
  Cat B c) + F-B-HIGH-1 phantom cleanup + F-B-HIGH-4 auth_views_enhanced.py
  fixes + drf-spectacular retrofit (S2203 F1).
- Group 2600 PA — NOT STARTED; T3 queued after Group 2500 close.
  Will consume Group 2400 CF-D2 delegation (session_tool.retire
  cascade on user logout + workspace-context authz + PA-chat 401 UX
  design + paStore field-list completeness).

**Cross-arc delegated items owed to future arcs (per canonical
summaries §9; v4 update 2026-07-05).**

- **Group 1700 Observability** — CLOSED at S1799; delegations RECEIVED
  documented at §14.8. Post-Group-1700-close delegations to §14 tracker:
  Cat D + Group 2400 CF-D3 umbrella roll-up (silent-401 rate telemetry
  + `authHandling: 'suppress_redirect'` telemetry + 503-fork asymmetry
  smoke-test coverage).
- **Employee OS 1200s arc** — Cat G Mission Memory (Memory delegation);
  Revenue Employee + Income/Jobs Employee JobContracts (Revenue T2/T3);
  Content Employee analog decision (Content UNK-F3); Group 1900 Authority
  Enforcement 3 T1 items (R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS + R.AUTHORITY.ACTOR-KWARGS-CELERY
  + R.AUTHORITY.ACTOR-STEP-CONTEXT runtime landing). Group 2000+ Event
  Architecture T1 R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER + T2
  R.EVENTS.EMPLOYEE-OS-EVENTBUS-CANONICAL-ADOPTION.
- **Group 2500 API (T2 NEXT)** — will consume: Group 2400 4-axis handoff
  bundle (refresh + envelope + CSD + typed-error + registry); Group 2200
  T1 contract SoT + drf-spectacular platform-wide extension + REST↔WS
  T7; Group 1400 Revenue T1 parallel-schema ADR (F.A1 + F.E3); Group
  1500 Sports T1 R.SPORTS.POSTURE + R.DBAO.CODENAME ADRs (integration
  vs island); Group 1600 Content D65e Rigby PA-tool + enforcement
  centralization axis.
- **Group 2600 PA (T3)** — will consume: Group 2400 CF-D2 delegation
  (session_tool.retire cascade + workspace-context authz + PA-chat 401
  UX + paStore); Group 2200 T1 workspace-context resolver + persistence
  contract + WS↔polling consolidation.
- **Group 2300 Mobile (parallel)** — will consume: Group 2400 CF-D4
  delegation (parallel silent-401 audit + MobilePushToken.revoked_at
  cascade + 401-handling parity between web + mobile).

### 14.8 Group 1700 Observability arc (S1799, closed 2026-07-03)

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S1799 verdict | Source anchor |
|-----------|-------------------|---------------|---------------|
| §2.8 EventBus (v2 fold: UNKNOWN → WEAK "partially implemented, weakly adopted") | WEAK per Rigby SIGN cycle 1 | **REFINED to six-plane producer/consumer/correlation graph** with three cross-cutting axes: correlation-spine + retention + consumer-partial-wiring. Six categories evaluated (Cat A CeleryTaskEvent + Cat B LLMCallEvent + Cat C AgentExecution + Cat D ToolCallRecord + Cat E OpsRun+OpsRunEvent + Cat F Adjacent). Every writer discipline intact (26 boundary candidates → 26 LEGITIMATE); every consumer surface at-best partially-wired. | S1799 §1 + §3 + §4 |
| §11 EventBus row (v2 fold: CRITICAL → HIGH) | HIGH | **CONFIRMED as HIGH baseline + retention posture UNBOUNDED-at-writer-side** (only Cat A + FleetEvent have date-based purge — 1/14 event models). Correlation-spine posture LATENT-at-cross-cat-correlation-spine per S1704 F1 100% NULL trace_id. | S1799 §1 D74 six-axis + §14.5.4 |

**NEW cross-domain connections not on v2 baseline:**

- **D74 six-axis correlation-spine framing.** Observability delivered a first-of-kind arc-lens question: "which single identifier does the platform's correlation spine hang on?" — answered with negative evidence on all four candidate options (task_id VERIFIED / execution_id REVISED / trace_id PARTIALLY REVISED / tool_call_id REFUTED / mission_id CONFIRMED). Source: S1799 §5 D74 six-axis + F5 correlation-primitive HYPOTHESIS box.
- **Retention pattern INCONSISTENT arc-wide.** Only Cat A CeleryTaskEvent + 1/14 event models (FleetEvent) have date-based purge; 12/14 models UNBOUNDED at write side. Cross-cutting axis; blocks D74 posture selection. Source: S1799 §1 axis F + T0/Gate R.OBSERVABILITY.RETENTION-UNIFIED-ADR (paired with D74 spine posture per S1706 Rigby SIGN F2 fold).
- **Cat A + Cat B + Cat C observed-writer discipline vs Cat D actively-broken consumer.** S1704 F1 identified ToolCallRecord as 100% NULL trace_id at write side; no cross-cat consumer can join to spine. Source: S1704 F1; S1799 §1 axis D.
- **PA path coverage gap at AgentExecution.** S1703 F1+F2+D4 three-class landmine reframe: PA-invoked agents skip AgentExecution writes because PA tool dispatch bypasses the `dispatch_agent` code path. Source: S1703 F1; S1799 §1 axis C.
- **Cat E flag-gated design-intent.** OpsRun + OpsRunEvent LATENT-VIABLE-BUT-FLAG-GATED — code exists + tables exist, but capability is gated behind `MISSION_RUNNER_ENABLED` disabled at HEAD. Source: S1705 F1; S1799 §1 axis E.

**POSTURE-PENDING (two paired T0/Gate ADRs):**

- **R.OBSERVABILITY.RETENTION-UNIFIED-ADR** — spans A-F retention policy; must be first-class field in D74 spine ADR regardless of posture (paired per Rigby SIGN F2 fold).
- **R.OBSERVABILITY.D74-SPINE-POSTURE** — selects A/B/C/D axis-cell for the correlation-spine. Nine T1 items depend.

**Cross-arc delegation IN (§9):** 4 aggregated delegations INHERITED from Groups 1300 Memory + 1400 Revenue + 1500 Sports + 1600 Content per S1699 §9 delegation table. Group 1700 acts as observability-side consumer for zero-fire beat detection (Sports Cat C+D), orphan-write telemetry (Revenue F2), MOCK-DATA-CONSUMER detection (Sports Cat E), EventBus adoption for Memory Cat F + Revenue T5 streams.

**Cross-arc delegation OUT (§9):** Group 1900 Event Architecture receives F.c 14-model catalog + F.e PERMEABLE terminology + Cat E producer-only role. Group 1300 Memory receives Cat C execution_id downstream `UserAgentLearning` alignment. Group 1400 Revenue receives R.A2 LLMCallEvent scoring-rate probe unblock.

### 14.9 Group 1800 HumanAttention / Feedback / Learning arc (S1899, closed 2026-07-04)

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S1899 verdict | Source anchor |
|-----------|-------------------|---------------|---------------|
| §2.6 HumanAttention (16) → Memory (13) | STRONG per Agent 4 §5.2 | **REFINED to six-plane learning-surface fragmentation:** Plane 1 human-mediated canonical (FeedbackProcessor → AgentLearning + LearningInsight LIVE) + Plane 2 autonomous canonical (9 LearningBridges → UserAgentLearning 22+ sites LIVE, 100% autonomous zero HAI touches) + Plane 3 external intelligence (Reddit LIVE-on-demand + Bluesky NEAR-DORMANT, NOT LearningBridge ABC inheritors) + Plane 4 user-interaction ephemeral (AgentLearningService LIVE 13 callers Redis-only) + Plane 5 unscheduled async (AgentLearningEngine DEFINED-BUT-UNSCHEDULED Redis pubsub zero publishers) + Plane 6 unused ORM-tree (PersistentLearningEngine DEFINED-BUT-UNUSED zero imports). **No shared source_kind provenance tag; no cross-plane query surface.** | S1899 §1 six-plane + F7 CRITICAL compound learning-loop |
| §2.6 HumanAttention → * (many pairs; Agent 4 §5.6) | Multiple STRONG/WEAK | **CONFIRMED with F7 CRITICAL compound learning-loop false-confidence pattern** across FOUR break-points durable across arc (S1801 D5 + S1804 F4 + S1805 F4 + S1806 arc-close): FeedbackProcessor post_save does NOT invoke update_learned_stats; auto-approve bypasses record_decision; source_weights excluded from save update_fields; record_verification emits nothing. | S1899 §1 F7 |

**NEW cross-domain connections not on v2 baseline:**

- **F3 HIGH IMMEDIATE CORRECTNESS — silent import-path-dependent collisions on 2 duplicate-FILE class-name pairs.** BoardroomLearningService × 2 files + UnifiedLearningPipeline × 2 files. Same class name, different files, silently importable depending on Python import order. Source: S1899 §14 F3.
- **Six-plane fragmentation vs one-planeness of v2 §2.6 baseline.** v2 treated HumanAttention → Memory as one STRONG pair; Group 1800 arc surfaced six distinct write-planes with different durability, ownership, provenance, and query surfaces. Source: S1899 §1 §3 six-plane; extends v2 §2.6 with per-plane classification.
- **Cross-arc delegation OUT.** Group 1300 Memory receives source_kind enum + AgentLearning schema-change ADR joint (T0/Gate). Group 1400 Revenue receives Revenue Opportunity → HAI MISSING gap (extends §14.3 F.D1). Group 1500 Sports receives verify-beat T-slot + two-task-variant reconciliation + AgentLearningSystem ownership U3. Group 1600 Content receives PALearningInsightsService + PAToolLearningEnricher discoverability. Group 1700 Observability receives Failure Cluster → HAI CRITICAL + retention-unified ADR bundle. Group 1900 Event Architecture receives source_kind enum + six-plane event-emission gap + HAI event candidates (T0/Gate handoff).

**POSTURE-PENDING (D80 four-option posture-decision brief):**

- **D80 four-option posture-decision** with F7 CRITICAL constraint framing + "with-assumptions-pending-fix" recommendation OR defer-post-T0/Gate safe default (Rigby SIGN Q3 fold #3 — both Chris-gated; xx99 did NOT select). 6 T0/Gate ADRs, 12 T1, 14 T2, 15 T3 = 47 total post-arc items.

### 14.10 Group 1900 Authority Enforcement arc (S1999, closed 2026-07-04)

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S1999 verdict | Source anchor |
|-----------|-------------------|---------------|---------------|
| §2.7 Governance / Authority (multiple pairs) | STRONG/WEAK per Agent 4 | **REFINED to per-plane separation-boundary posture register (P4 first-class deliverable):** 5 PERMEABLE-BROKEN (Memory + Content + HAI + Employee OS + API) + 2 STRUCTURAL-DROP (Sports + Discord) + 1 CLEAN (Frontend); **0 STABLE, 0 CANONICAL**. Governance authority evolution doc + 4-plane framing preserved as design-preparation input to this arc. | S1999 §17.1 per-plane register |
| §11 governance rows | Multiple HIGH/MEDIUM | **RESOLVED into 17 discrete design decisions across P1/P2/P3/P4** via 4 successive "agree all" rounds (S1902 D-gate + S1903 Q-resolutions + S1903 SIGN folds + S1904 all-findings) plus S1999 xx99 close (FIFTH-consecutive). Runtime state at HEAD: **only Boundary 5 warn-mode observation event fires** (13 events / 5 days / 4 employee_handles at S1902 close); AuthorityLevel enum has 1 runtime consumer (level_counts accumulator at `mission_runner.py:863-874`); 6 KillSwitch reads all management/audit/cleanup ZERO enforcement dispatch. **Verdict: design-complete, runtime-scaffolding.** | S1999 §1 |

**NEW cross-domain connections not on v2 baseline:**

- **Design-complete vs runtime-scaffolding as arc-close verdict class.** First arc to distinguish "specification consolidated + Chris-ratified" from "runtime binding not yet wired." Feed-forward pattern for Group 2000+ + Group 2100 (both closed with same class of verdict).
- **`enforce_authority_mode` field ABSENT at HEAD.** P4 §14.3.3 direct grep verified. Field does not exist yet; enforcement dispatch would require adding it via T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS.
- **`signal_aggregation_service.py:211` cross-plane read UNDOCUMENTED.** Direct authority-plane read from signal-aggregation service without documented interface. Delegated to Memory arc (T3 R.MEMORY.SIGNAL-AGG-AUTHORITY-COUPLING-DOC).
- **Cross-arc delegation OUT.** Employee OS receives 3 T1 items (R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS + R.AUTHORITY.ACTOR-KWARGS-CELERY + R.AUTHORITY.ACTOR-STEP-CONTEXT runtime landing). Group 1600 Content receives T1 R.CONTENT.PUBLISHGATE-AUTHORITY-COMPOSITION. Group 1700 Observability receives authority-audit event retention posture pairing. Group 2000+ Event Architecture receives F.SYMBOL-MAPPING-STATUS-VERIFICATION + F.PER-USER-AUTHORITY-MECHANISM + R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES.

**POSTURE-PENDING:**

- **T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS** highest-priority per F5 severity — blocks enforcement dispatch expansion.
- **T2 R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION** with P3 D94 reader spec.
- **T2 R.AUTHORITY.AUTO-APPROVE-FREEZE-GATE** elevated per P4 F4.
- 20-item T-tier queue distributed across 7 arcs + §8.4.1 dependency/blocker map.

### 14.11 Group 2000+ Event / Integration Architecture arc (S2099, closed 2026-07-04)

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S2099 verdict | Source anchor |
|-----------|-------------------|---------------|---------------|
| §2.8 EventBus (WEAK "partially implemented, weakly adopted") | WEAK per Rigby v2 fold | **REFINED to substrate landscape with 6 named intra-application substrates + 1 INTENTIONAL SIDECAR (Fleet Events per Chris D-verdict S2004) + 1 deprecated `redis.publish()` drift.** | S2099 §3.1 |
| §11 EventBus row (HIGH) | HIGH | **CONFIRMED as design-complete, runtime-scaffolding, closure-gated on 4 T1 items:** composition-consistency register + HAI dual-emission wiring + spider-data substrate consolidation + F.PER-USER-AUTHORITY emission wiring. Register is strict closure pre-req for HAI + spider-data + F.PER-USER-AUTHORITY per Q1a SIGN fold. | S2099 §1 + T1 ordering |

**NEW cross-domain connections not on v2 baseline:**

- **10-plane distribution seam-posture:** 2 PERMEABLE-BROKEN (Memory + Content) + 2 PARTIAL (Sports + API) + 3 WORKING (Observability + Authority Enforcement + Employee OS) + 1 EXPERIMENTAL (HAI) + 1 STRUCTURAL-DROP (Discord) + 1 CLEAN-delegated (Frontend); **0 STABLE, 0 CANONICAL.** Extends Authority §17.1 per-plane register to event/integration plane. Source: S2099 §5.1-§5.2.
- **Fleet Events INTENTIONAL SIDECAR** — Chris D-verdict S2004 ratified Fleet Events NOT-canonical-EventBus; classified as intentional sidecar with dedicated §13.1.5 sidecar subtable in EVENT_SYSTEM_INVENTORY. First arc to classify a substrate as intentional-sidecar (distinct from drift/DEAD/MOCK).
- **§10 meta-methodology promotions.** MC-3 (F18 test-gap durable-at-3 arcs) CODIFICATION-CONFIRMED. MC-4 (arc-pin routing durability) CODIFICATION-CONFIRMED — guardrails retained but generalized in applicability. MC-5 (§11.2 20-section child template) CODIFICATION-CONFIRMED extended 15 → 18. MC-6 (Cat F CONSOLIDATION pattern) CODIFICATION-CONFIRMED. **F5 HYPOTHESIS DISPROVE evidence-rollup heuristic codification-confirmed** — cross-arc tally 1 pass / 7 disprove durable-at-seven; DISPROVE-dominant pattern is CANONICAL per Q11 SIGN STRENGTHEN.
- **Cross-arc delegation OUT (10 arcs).** Delegations to Groups 1300/1500/1600/1700/1800/1900 + Employee OS + API + Discord + Frontend distributed. Group 1300 Memory receives F13 Fleet Events receiver post-classification + T3 R.MEMORY.WRITER-PLANE-EVENT-EMISSION-DOC. Group 1700 Observability receives T1 F15b DLQ reader + T2 R.EVENTS.OBSERVABILITY-SYSTEM-ALERT-EMISSION. Group 1800 HAI receives T1 R.EVENTS.HAI-DUAL-EMISSION-WIRING (highest T1 priority per F5 severity). Group 1900 Authority receives T1 R.EVENTS.PER-USER-AUTHORITY-EMISSION-WIRING (three-event contract).

**POSTURE-PENDING:**

- 2 T0/Gate (R.EVENTS.CANONICAL-SEAM-STATEMENT CONSUMED + R.EVENTS.FLEET-EVENTS-CLASSIFICATION-ADR RATIFIED as option (3) INTENTIONAL SIDECAR).
- 7 T1 (T1 ordering per Q10 SIGN STRENGTHEN: #1 composition-consistency register strict closure pre-req + #2 HAI dual-emission wiring parallel-executable + #3 spider-data substrate consolidation + #4 per-user-authority + #5 authority.violation-event-schema + #6 content deliverable-event emission wiring + #7 DLQ correctness closure F14+F15).

### 14.12 Group 2100 RAG / Document Loading (Knowledge Loop) arc (S2199, closed 2026-07-04)

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S2199 verdict | Source anchor |
|-----------|-------------------|---------------|---------------|
| §2.5 Memory / Documents / Embeddings (RAG lane) | v2 §14.2 refined "Two RAG lanes, no runtime selector" | **REFINED to design-governed corpus substrate — spec-complete via P3, evidence-supported via P4, execution-pending via post-arc T-slots** — in transition toward runtime-governed institutional knowledge layer along maturity gradient passive → spec-complete → execution-complete. | S2199 §1 |
| §11 risk #19 (5+ memory stores) — RESOLVED at Group 1300 per §14.2 | v2 §14.2 fold | **EXTENDED to RAG corpus governance framing** — Group 2100 delivered spec for retrieval authority + governance framework layered on top of the corpus substrate; execution pending. | S2199 §1 spec-complete/execution-pending |

**NEW cross-domain connections not on v2 baseline:**

- **RAG corpus as design-governed substrate.** First arc to frame a substrate as spec-governed + evidence-supported + execution-pending in three-stage maturity gradient. Extends design-complete/runtime-scaffolding class from Authority + Event arcs to Knowledge Loop arc.
- **§14 6-doc-arc structure applied to Knowledge Loop.** S2100 parent + S2101 P1 Corpus State + S2102 P2 Ingestion Pipeline + S2103 P3 Retrieval Authority Framework + Governance Design + S2104 P4 Behavior Substrate Structured Observation + Integration + S2199 xx99 canonical summary. **F5 correlation-primitive HYPOTHESIS box** discipline first-application from Observability MC-3 template (F5 DISPROVE dominant pattern preserved at S2199).
- **Cross-arc delegation OUT.** 2 flags post-Q19 shrink 3→2: (i) cascade lifecycle-event architecture co-execution with Group 2000+; (ii) retrieval-surface counter operator-surface with Group 1700.
- **19 T-slot follow-on queue** distributed as 2 T0/Gate (T22 Track B + T13 Track A) + 6 T1 + 9 T2 + 2 T3.

**POSTURE-PENDING:**

- T0/Gate T22 Track B + T13 Track A.
- 6 T1 items — T18/T19/T21/T26a/T27/T-D2100.11.

### 14.13 Group 2200 Frontend (Contract-Surface Arc) (S2299, closed 2026-07-05)

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S2299 verdict | Source anchor |
|-----------|-------------------|---------------|---------------|
| §2.9 Frontend → * (multiple) | Various STRONG/WEAK; Content → Frontend REFINED at §14.5 | **REFINED to canonical seam statement (verbatim from S2299 §5.1 post-Rigby SIGN Q1 fold):** "The frontend at HEAD `294512e3` is an *accreted UI mesh with declared-but-unenforced contracts — structurally healthy at the routing/auth-wrapper/layout/Zustand-persist boundary but structurally under-specified at the page-component/consumer-contract/API-typing/state-discipline boundary — where three of four contract-surface axes examined by this arc (component-boundary + envelope + API-typing) generalize as SYSTEMIC deficiencies with surface variance across the examined child surfaces, one axis (state persistence) is SURFACE-LOCAL + DOMAIN-SPECIFIC HYBRID confined to `/betting`, and the fix path is wiring the design-latent contract infrastructure (partially scaffolded; unevenly wired) through cross-arc coordination with Group 2400 Auth + Group 2500 API + Group 2600 PA + Group 1700 Observability — not framework migration."* | S2299 §5.1 |
| §7 boundary violations (v2) | Multiple | **CONFIRMED and EXTENDED with S2201 §14.3 cockpit two-stage MINOR-DRIFT (frontend-side session-lifecycle ambiguity symptom) + S2201 §15.5 silent-401 SYSTEMIC + S2202 F1 MOCK-DATA-CONSUMER multi-surface + S2202 F3 envelope-conformance 0/40 primary + S2203 §14 F1 SoT-ABSENT-at-platform-scale + F3 silent-401 SYSTEMIC ~630/1300 call-sites at risk + F3.5 whitelist BRITTLE.** These are frontend-side symptoms feeding four-axis T1 handoff bundle to Group 2400 Auth. | S2299 §8.2 T1 handoff |

**NEW cross-domain connections not on v2 baseline:**

- **Four-axis T1 handoff bundle owed to Group 2400 Auth.** silent-401 + logout cleanup + session lifecycle + permission-floor uniformity. Two-sided FE-symptom-vs-BE-model framing per S2203 §14 F3 + S2204 §19.1 R1 mirror. Discharged in full at Group 2400 close (see §14.14).
- **Six §4 cross-cutting patterns:** §4.1 no-CODEOWNERS + LIGHT-ownership across all 4 children (extends CX-P1 to Frontend arc) + §4.2 silent-failure defaults across P1+P2+P3 + §4.3 untyped/uncontracted defaults across P2+P3+P4 (design-latent infrastructure exists but unwired) + §4.4 DEAD-CANDIDATE/MOCK-DATA/INTENT-NEUTRAL pattern class recurrence across P2+P3 + §4.5 god-file/god-component ≥1,500 LOC threshold generalizes across UI+infrastructure layers + §4.6 cross-arc DEFER-with-escape-hatch pattern 3-within-arc + §4.7 Context propagation fragility workspace-identity + global-dock-coupling + §4.8 Anchor + inventory drift docs-and-inventories-lag-reality.
- **CODEOWNERS absent + LIGHT-ownership pattern.** Extends CX-P1 runtime-owner MISSING to Frontend surface with F4 finding.
- **Cross-arc delegation OUT (4 flags, no shrink; distinct integration surfaces):** (i) silent-401 + logout cleanup contract with Group 2400 Auth (T1); (ii) contract SoT + drf-spectacular extension with Group 2500 API (T1); (iii) workspace-context resolver + persistence contract with Group 2600 PA (T1); (iv) envelope enforcement locus + Session 968 X-UI-Scope ring buffer ownership with Group 1700 Observability (T1).

**POSTURE-PENDING (§7 anti-scope preserved from arc scope — no fixes, no framework migration):**

- ~38 T-slot follow-on queue four-track structure. **T1 cross-arc handoffs (4 items)** distributed to Group 2400 Auth + Group 2500 API + Group 2600 PA + Group 1700 Observability. **Maintainer-decision batch (5 items)** — CODEOWNERS + DEAD-CANDIDATE consolidated cleanup + api.ts extraction + storageKeys registry + cockpitApi ownership. **T2 post-arc T-slot (10 items) + T3 conditional post-arc (4 items).**

### 14.14 Group 2400 Auth (Session Lifecycle + Permission Floor + Silent-401 Resolution) arc (S2499, closed 2026-07-05)

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S2499 verdict | Source anchor |
|-----------|-------------------|---------------|---------------|
| §2.9 Frontend → Auth / Session Auth boundary | STRONG per Agent 4 §5.7 | **REFINED to canonical verdict on central lens question (Chris-locked at S2400 open):** *"Is the platform's auth model a contract... or an accretion of per-surface defaults whose failures are silently swallowed?"* **VERDICT: "ACCRETION with declared-but-unenforced contracts"** (Rigby SIGN Q1 fold tightening: "mechanisms generally work at file-precision in the sampled surfaces"). Pattern is not scattered defects — it is one architectural posture surfacing consistently at every axis the arc looked at. | S2499 §1 |
| §7 boundary violations (v2) | Multiple | **CONFIRMED and EXTENDED with 4 layers of contract mesh:** Cat A trust boundaries declared without runtime enforcement (VIP demo prompt-only + Fleet permissive fallback + PURGE_SECRET hardcoded fallback + WebSocket middleware DEAD in ASGI stack) + Cat B permission floors implicit at ~80-90% ESTIMATE inheritance rate + Cat C session lifecycle contract undeclared across 14/15 client-side persistence surfaces (6.7% declared cleanup rate) + zero Clear-Site-Data emission + no refresh endpoint + VIPInvite account_expires_at declared-fictional + Cat D frontend caller ~99% silent-swallow rate across 803 consumer call-sites (57 direct + 667 useQuery/useMutation + 79 raw fetch bypass) with zero typed AxiosError catches and zero error boundaries. | S2499 §3 consolidated shape + §14 numerical summary |

**NEW cross-domain connections not on v2 baseline:**

- **Four-axis contract mesh:** identity-attach + authorization floor + session lifecycle plane + frontend caller surface. Each layer works mechanically; each layer silently violates its contract at boundary. Pattern generalizes across whole auth stack.
- **803-consumer-call-site classification by inheritance-path** — 57 direct + 667 hook + 79 raw fetch; 724 interceptor-routed (90.2%) + 79 bypass (9.8%); ~99% silent-swallow rate at HEAD.
- **Sidebar logout does NOT revoke backend token (F-D-SIDEBAR-1 NEW HIGH FINDING).** `frontend/src/components/layout/Sidebar.tsx:356` clears authStore + syncUser(null) + Zustand persist localStorage clear, but does NOT invoke `authApi.logout()`. Backend `authtoken_token` DB row never deleted via sidebar path. Combined with F-C-REFRESH-1 (no refresh endpoint) + Cat A F-DEC-1 (no expiry): attacker-valid window on leaked token = indefinite. Cross-domain: Auth ↔ Frontend integration + Sidebar UI ↔ backend logout endpoint. Source: S2404 §16 F-D-SIDEBAR-1; S2499 §3.
- **PA-chat 401 silent-swallow (F-D-PA-1 HIGH per Rigby Q10 fold — escalated MED→HIGH).** `/pa/chat/`, `/pa/chat/status/`, `/pa/conversations/` endpoints do NOT match whitelist substring; 401 mid-conversation = silent reject = agent-hang UX. PA is control-plane per CLAUDE.md workflow rules. Cross-domain: Auth ↔ PA integration. Source: S2404 §14 F-D-PA-1.
- **Three three-option decision spaces enumerated for Chris D-verdict:** Cat B (a)/(b)/(c) permission-floor + Cat C (α)/(β)/(γ) session-lifecycle + Cat D α/β/γ × 2 typed-error-envelope + whitelist-replacement. Cat D Rigby Q6 fold reconciled γ (mechanism) with Cat C β (UX policy) as nested composition — γ = RQ error callback + top-level ErrorBoundary + Cat C β "explicit re-login" as message/UX policy nested inside γ.
- **F-C-VIP-1 risk-gate constraint preserved through xx99.** Shipping any α/β/γ envelope UX must NOT surface time-based expiry semantics until F-C-VIP-1 (VIPInvite.account_expires_at 14d not enforced at runtime) resolves. Copy guidance per Cat D Rigby Q9 fold: use "Sign-in required" / "Authentication required" / "Please sign in again" (no time-based claim) until F-C-VIP-1 resolves post-arc.
- **26 cross-arc coordination flags roll up into 7 delegate arcs** (T2 Group 2500 API NEXT + T3 Group 2600 PA + T4 Group 1700 Observability umbrella + T5 Group 2300 Mobile + Group 2200 R6 error-boundary framework BLOCKING PREREQUISITE for option-γ + Group 1900 KillSwitch preservation + Group 2400 internal). Single-tracking-unit discipline for delegate arcs receiving ≥3 upstream flags (Cat C Q11 fold + Cat D CF-D3).

**POSTURE-PENDING:**

- **P0-A platform-wide:** F-D-CALL-1 803-scale silent-401 remediation + F-D-BYPASS-1 79-raw-fetch bypass + F-D-ENVELOPE-1 typed-error-envelope + F-D-BOUNDARY-1 error-boundary framework establishment (S2299 §8.3 R6 BLOCKING PREREQUISITE for option-γ).
- **P0-B token lifecycle:** F-D-SIDEBAR-1 backend-token-revoke fix + F-C-REFRESH-1 refresh discipline + F-C-VIP-1 VIPInvite.account_expires_at ENFORCEMENT (risk-gate prerequisite for α/β/γ) + F-C-CSD-1 Clear-Site-Data emission + F-C-STORE-1 15-surface × logout-cleanup declared contract.
- **P0-C endpoint-specific:** F-CRIT-1 PURGE_SECRET + F-BND-4a bet-placement unauth + F-B-CRIT-1 permission-floor ~80-90% + F-B-CRIT-2 silent-401 SYSTEMIC + F-D-WHITELIST-1 whitelist replacement.
- Co-equal contract preserved per Cat A/B/C precedent; tiers surface blast-radius truth for implementation sequencing.

**Q20 fold codification candidate CONFIRMED at two-trigger threshold.** Silent-degrade-vs-explicit-failure ambiguity — Cat C TRIGGER #1 (13-of-14 findings silent-degrade class = 92.9%) + Cat D TRIGGER #2 (17-of-19 findings silent-degrade class = 89.5%; 2 non-silent-degrade findings both governance class: F-D-OWN-1 CODEOWNERS + F-D-OWN-2 CI test-harness per Cat D Rigby Q5 fold). Both above §20 codification threshold. **Tightened codification claim (scope-bounded):** promote to playbook v3 candidate focused on **auth failure handling (401/403/refresh/logout) with explicit UX + telemetry requirements** — NOT general silent-degrade-anywhere codification. **Conditional promotion rule (xx99 Rigby SIGN Q3 fold):** general codification blocked pending 3rd trigger in non-auth plane (Groups 2500 API / 2600 PA / 1700 Observability).

**MC-4 5th confirming arc RESOLVED at xx99 close.** Group 2400 Auth 4-child structure completes MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails across-5-consecutive-arcs (1900 + 2000+ + 2100 + 2200 + 2400). **Resolution is methodological, not platform-state** per xx99 Rigby SIGN Q2 fold — codification-confirmed with scope guardrails + full-stack stress test in Auth PASSED, NOT "platform auth fixed." **MC-14 CANDIDATE preserved** at 5-arc-stages threshold with proposed §16 threshold rule for playbook v3 (5 arc-stages = provisional-confirmed; codification-confirmation requires 1 additional non-adjacent domain OR 2 more groups).

### 14.15 Group 2500 API arc (S2599, closed 2026-07-06)

**Backfill entry (v5 append-only 2026-07-06).** Group 2500 API closed at S2599 canonical summary 2026-07-06 (post-Group 2400 close). This §14.15 subsection lands the missed §14 refresh at S2699 close per Rigby SIGN cycle 1 APPROVED WITH REFINEMENTS 2026-07-06 (dedicated fresh SIGN isolation pin `pa-db34dc63aa9e4023` — TWENTIETH-consecutive-adjacent SIGN pin retirement — routing classification options per Chris directive before write). All wiring-state labels reflect 5 Rigby SIGN refinements Chris "agree all" 2026-07-06 ratified wholesale.

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S2599 verdict | Wiring state (per Rigby SIGN) | Source anchor |
|-----------|-------------------|---------------|-------------------------------|---------------|
| §2.9 Frontend → Backend API surface | STRONG per Agent 4 §5.7 | **REFINED to 4-layered domain shape** (BACKEND DECLARATION plane Cat A + WIRE CONTRACT plane Cat C + CONSUMER DECLARATION plane Cat B + PERMISSION-FLOOR + REST↔WS plane Cat D). Canonical verdict: "majority IMPLICIT-INHERITANCE with ISLAND-DECLARATION pockets and ZERO cross-transport SoT." | **WEAK + POSTURE-PENDING** (Rigby SIGN refinement #1 — the same paragraph asserts implicit inheritance + shape-blind consumer + zero cross-transport SoT; not STRONG wiring, functioning mechanism with inconsistent contract/SoT) | S2599 §1, §3 |
| §11 API row | Multiple HIGH/MEDIUM | **REFINED with 3 decision-space quadrants + 1 established Cat D γ ⊃ Cat C β nesting** (typed-error-envelope γ mechanism nests Cat C session-lifecycle β UX policy inside γ default handler) | **POSTURE-PENDING overlay on top of mixed WEAK/MISSING** — quadrants are decision-space, not wiring-state; underlying wiring is mixed (WEAK/STRONG-adjacent mechanism + explicitly greenfield governance/SoT MISSING) | S2599 §1, §2 |

**NEW cross-domain connections not on v2 baseline (wiring-state per Rigby SIGN):**

- **4-shape 401 heterogeneity end-to-end pipeline (Cat A → Cat B → 803-site consumer).** Cat A emission (Family A/B/C/D per Cat A §14.6 F6) → Cat B SHAPE-BLIND interceptor (`api.ts:43-62` reads status + URL substring, not body) → 803-site consumer flow (57 direct + 667 hook + 79 raw fetch bypass; Cat B §14 F3 + F5 + Cat D §14 F-D-CALL-1 preserves). Design-order sequencing: any envelope-shape SoT selection requiring consumer discrimination requires SHAPE-BLIND replacement to land first (or simultaneously). **Wiring-state: WEAK** — works but shape-blind at choke point, blocking any envelope SoT strategy without replacement. **Verdict: NEW** cross-plane pipeline, not local defect. Source: S2599 §4.2.
- **285-entry path-list gate registry short-circuiting DRF at `core/auth_middleware.py:94-561`** (265 PUBLIC + 6 other lists including STAFF_REQUIRED + REVIEWER_BLOCKED + OPTIONAL_AUTH + PUBLIC_PATHS_EXACT + REVIEWER_ALLOWED). Middleware evaluates FIRST + short-circuits DRF dispatch → source of F-B-HIGH-2 dead-code inversion at `/api/v1/betting/place/`. **Wiring-state: OVERCOUPLED** (Rigby SIGN refinement #3 — pre-DRF short-circuit + huge enumerated registry = tight coupling + high blast radius + dead-code inversion behavior). **Verdict: NEW** cross-domain auth gate mechanism, not just another endpoint permission issue. Source: S2504 §14.3; S2599 §3.
- **838 explicit `@permission_classes` decorator sites + 74 class-attr sites across 126 files.** Route-indexed 838/1,856 = 49% decoration-site density (NOT explicit-permission coverage rate per Cat D §1.1 D1-D6 canonical denominator contract — Rigby xx99 SIGN Q1 STRENGTHEN fold prevents quote-mining). **Wiring-state: WEAK** — high decoration density ≠ governed permission floor / SoT; evidences fragmentation and manual scatter (potentially misleading if mistaken as "coverage"). **Verdict: NEW** inventory-scale signal. Source: S2504 §14.1; S2599 §3.1.
- **`FleetCapabilityRequired.for_capability(*path)` MECHANISM PRIMITIVE at `core/services/fleet_auth_drf.py:215-263`.** Viable exemplar for per-endpoint permission-floor governance. **Wiring-state: STRONG (local exemplar) / WEAK (system-level)** — encoded as "STRONG-EXEMPLAR but does not upgrade the overall domain." **Verdict: NEW** concrete primitive enabling governance, but not the governance itself (F-D-REGISTRY-1 GREENFIELD at HEAD). Source: S2504 §14.3 + §4.3.
- **4 GREENFIELD governance layers:** Cat B (c) permission-floor + Cat D whitelist-replacement γ + Cat D REST↔WS T7 joint + F-D-WSENVELOPE-1 (0/40 WS envelope conformance across 87 Consumer classes per Cat D §14.2). **Wiring-state: MISSING + POSTURE-PENDING** (Rigby SIGN refinement #2 — labeled greenfield with 0/40 conformance = missing wiring; governance/SoT pieces explicitly greenfield). **Verdict: NEW**. Source: S2599 §4.3.
- **REST↔WS T7 joint dual-owned Group 2500 API + Group 2600 PA (CF-D6).** 120 WS routes (drift -5 from S2202 baseline 125) + 87 Consumer classes + 100% TokenAuthMiddlewareStack routing + 0/40 envelope conformance at REST-adjacent WS layer. **Wiring-state: OVERCOUPLED (structure) + WEAK (conformance/SoT)** (Rigby SIGN refinement #4 — weak because 0/40 envelope conformance + no SoT across transports; overcoupled because dual-owner joint increases coordination cost/blast radius; explicitly avoids "delivered = STRONG" framing). **Verdict: REFINED** — CF-D6 already exists as §14.14 handoff-flag; §14.15 extends/connects, doesn't invent. Source: S2504 §14.2 + CF-D6; S2599 §3, §9.
- **Cross-cutting patterns (§4.1-§4.4 all four in-arc):** §4.1 declared-but-unenforced contract (4-child; all four planes exhibit "declared in code/docs/schema without runtime enforcement at consumption") + §4.2 SHAPE-BLIND consumer surface (Cat B + Cat C + Cat D end-to-end pipeline) + §4.3 greenfield governance layers (2 GREENFIELD + 1 EXPERIMENTAL per Cat D §13) + §4.4 fragmentation across parallel layers (Cat A F6 + Cat C F1 + Cat C F6 + Cat C F2 + Cat D F-D-4LAYERSPLIT-1). **These are pattern abstractions, not wiring touchpoints — kept as NEW arc patterns with POSTURE-PENDING framing, not baseline wiring labels.** **Verdict: NEW** arc-level crystallizations. Source: S2599 §4.

**POSTURE-PENDING (3 decision-space quadrants + 1 established nesting per S2599 §1):**

- **Quadrant I (backend DECLARATION):** Cat A Path A/B/C strictness (Full drf-spectacular + codegen / Money-path-only / Mixed) + drf-spectacular wire-up decision (INSTALLED_APPS + URL routes + management command).
- **Quadrant II (consumer DECLARATION):** Cat B (a)/(b)/(c) long-term governance + SHAPE-BLIND interceptor replacement decision.
- **Quadrant III (error / lifecycle CONTRACT):** Cat C α/β/γ session-lifecycle + envelope SoT + refresh-endpoint necessity + Clear-Site-Data emission locus + F-C-VIP-1 4-option enforcement rubric.
- **Quadrant IV (permission-floor + REST↔WS T7):** Cat B (a)/(b)/(c) permission-floor + Cat D typed-error-envelope α/β/γ + Cat D whitelist-replacement α/β/γ + REST↔WS T7 Path A/B/C strictness.
- **Nesting established (Cat D §9.1 Q12):** Cat D typed-error-envelope γ = mechanism ⊃ Cat C session-lifecycle β = UX policy nested inside γ default handler. All other pairings ORTHOGONAL unless xx99 explicitly couples.

**Cross-arc pattern crystallizations extending §14.6 (CX-P7 + CX-P8 CANDIDATE per Rigby SIGN cycle 1):**

- **CX-P7 CANDIDATE (NEW at Group 2500) — "Declared-but-unenforced contract" as recurrent arc-close class across all 4 planes.** Cat A F1 SoT-ABSENT + Cat C F3 refresh-endpoint ABSENT + Cat C F7 F-C-VIP-1 + Cat D F-D-REGISTRY-1 + Cat D F-D-WSENVELOPE-1. **Wiring-state tendency: WEAK/MISSING** (pattern-level; describing systemic failure to enforce contracts). **Recognition threshold met: 5 evidence points in one arc.** **CX-P elevation call: NOT elevated at cycle 1** — Rigby SIGN Q3 fold — awaits second-arc explicit evidence enumeration (Group 2600 PA §14.16 partially confirms but F-B-HIGH-3 STRONG counterexample complicates dominance claim). Source: S2599 §4.1.
- **CX-P8 CANDIDATE (NEW at Group 2500) — "SHAPE-BLIND consumer surface end-to-end pipeline."** 4-shape 401 heterogeneity (Cat A emission) → SHAPE-BLIND interceptor (Cat B attach) → 803-scale consumer flow (Cat D propagation) = single end-to-end pattern. **Wiring-state: WEAK** (mechanism present; contract/SoT blocked). **CX-P elevation call: NOT elevated at cycle 1** — Rigby SIGN Q3 fold — awaits second-arc explicit shape-blind choke + propagation demonstration at comparable scale before promoting from domain-local to cross-domain. Source: S2599 §4.2.
- **CX-P4 extension (POSTURE-PENDING as arc-close disposition).** 3 quadrants + 1 established nesting is a specific case of POSTURE-PENDING as arc-close disposition (extends §14.6 CX-P4). Group 2500 preserves the pattern with quadrant structure + nesting-couple. **Verdict: CONFIRMED as extension** of CX-P4 closure disposition format. Source: S2599 §1.

**Cross-arc delegations OUT (per S2599 §9):**

- **Group 2600 PA (T3 NEXT)** — CF-D6 REST↔WS T7 joint dual-owner PA side + CF-2600-PA REST endpoint DECLARATION side + F-B-HIGH-3 workspace-membership implicit-gate (S2402 preserved) + CF-C2 (S2503) session-lifecycle handoff. **DISCHARGED at Group 2600 close S2699 xx99 2026-07-06 — see §14.16.**
- **Group 1700 Observability (T4)** — envelope-shape telemetry emit-signature + per-Consumer conformance metrics + REST↔WS parallel-delivery reconciliation-layer ownership candidate.
- **Group 2300 Mobile (parallel arc)** — CF-D4 parallel silent-401 audit + MobilePushToken.revoked_at cascade + 401-handling parity between web + mobile.
- **Group 1600 Content (secondary)** — CF-C8 envelope shape variability from Cat C S2503.

---

### 14.16 Group 2600 PA arc (S2699, closed 2026-07-06)

**Baseline touchpoints refined.**

| v2 anchor | v2 classification | S2699 verdict | Wiring state (per Rigby SIGN) | Source anchor |
|-----------|-------------------|---------------|-------------------------------|---------------|
| §2 PA subsystem → * (multiple) | Various STRONG/WEAK/MISSING per Agent 4 | **REFINED to 4-plane consolidated shape:** PLANE 1 REST BOUNDARY (Cat A 34 endpoints per F11 canonical + 3 parallel `/chat/` REST) + PLANE 2 CLIENT SURFACE (Cat B 3 consumer surfaces: assistantApi 20 methods 25% typed + paStore 16 fields + tools/pa_chat.py 100% untyped + 3 canonical WS message classes `observed-JSON-only`) + PLANE 3 IDENTITY WORKSPACE-CONTEXT SESSION-LIFECYCLE (Cat C C1 + C2 sub-tracks + Group 2400 α/β/γ DEFERRED cascade) + PLANE 4 REST↔WS T7 JOINT (Cat D 5 URL patterns / 4 distinct Consumer classes / F-D2 canonical envelope-declaration matrix). Canonical arc-close verdict (§1): *"PA subsystem MECHANISM is OPERATIONAL across all four contract planes; DECLARATION/SoT is consistently partial/implicit across all four planes — arc-close diagnosis is design-plane governance + compensating-controls policy, NOT systemic runtime failure."* | **WEAK (mechanism operational) + POSTURE-PENDING (SoT/decl explicitness + governance completion pending)** — encoded as "operational across planes; declaration/SoT partial/implicit across planes." | S2699 §1, §3 |
| Cat A F-B-HIGH-3 workspace-membership implicit-gate (S2402 preserved; propagated in S2699 §4.5) | STRONG-adjacent per S2402 §14.2 | **VERDICT-READY at Cat C1 closure** (Chris D-verdict-request 5-way at S2699 §11 ratification card). Semantics: user-owns-workspace via `ProjectWorkspace.user` OneToOneField (NOT junction table); fails-closed at `_write_files_to_workspace()` on active-workspace resolution + user-ownership check; enforcement point at handler-internal `execute_with_workspace()` at `core/agents/base_agent.py:5355` → `WorkspaceManager.get_active_workspace()` at `workspace_manager.py:1697`. | **STRONG / CONFIRMED** (Rigby SIGN refinement #5 — fails-closed write-boundary enforcement; kept explicitly STRONG as COUNTEREXAMPLE inside broader WEAK/implicit SoT framing). | S2699 §4.5 F-B-HIGH-3 propagation; Cat C §7.2 fails-closed clarifier |
| §14.14 CF-D6 REST↔WS T7 joint (dual-owned Group 2500 API + Group 2600 PA) | STRUCTURAL-DUAL-OWNER framing at Group 2400 close | **DUAL-OWNER PA side DELIVERED by Cat D S2604** — 3 canonical PA-client WS message classes at `observed-JSON-only` grade (F-D2 canonical envelope-declaration matrix per AC-D2 canonical artifact) + §7.4 T7 cross-transport consistency rule (both REST + WS non-streaming per F-D1 fold VC-5; parallel-delivery reconciliation gap UNOWNED at HEAD). | **OVERCOUPLED (structure) + WEAK (conformance/SoT)** (Rigby SIGN refinement #4 applied to §14.16 — PA side "delivered" adds artifacts but joint remains overcoupled dual-owner with incomplete envelope conformance SoT; explicitly avoids "delivered = STRONG"). | S2699 §3, §9 |

**PA-internal 4-plane pairwise coupling matrix (per Rigby SIGN Q2 answer):**

Interpretation: for each plane-pair within Cat B canonical 4-plane structure, classify relationship as ORTHOGONAL / NESTED (mechanism ⊃ policy — structured coupling, not OVERCOUPLED) / COUPLED / OVERCOUPLED / UNKNOWN.

| # | Pair | Classification | Rationale |
|---|------|----------------|-----------|
| 1 | P1 REST boundary ↔ P2 client surface | **WEAK coupling** | Works, but consumer surfaces partially implicit / hetero |
| 2 | P1 REST boundary ↔ P3 identity/workspace/lifecycle | **NESTED (mechanism ⊃ policy)** | REST auth/workspace resolution mechanism contains identity/workspace policy enforcement (supports STRONG F-B-HIGH-3) |
| 3 | P1 REST boundary ↔ P4 REST↔WS T7 joint | **WEAK / POSTURE-PENDING** | REST↔WS alignment incomplete; envelope/conformance not canonical |
| 4 | P2 client surface ↔ P3 identity/workspace/lifecycle | **WEAK coupling** | Client behavior depends on session/workspace context, but SoT is partial/implicit |
| 5 | P2 client surface ↔ P4 REST↔WS T7 joint | **WEAK / POSTURE-PENDING** | WS client classes exist but not at canonical envelope contract |
| 6 | P3 identity/workspace/lifecycle ↔ P4 REST↔WS T7 joint | **WEAK** | Identity/lifecycle semantics extend into WS path; contract not uniformly enforced |
| 7 | P3(C1 workspace-context) ↔ P1 REST | **STRONG** | Enforced at write boundary (F-B-HIGH-3 STRONG counterexample) |
| 8 | P3(C2 session-lifecycle) ↔ P1 REST | **WEAK / POSTURE-PENDING** | Policy/mechanism separation exists but SoT incomplete |
| 9 | P3(C1 workspace-context) ↔ P2 client | **WEAK** | Client context resolution partially implicit |
| 10 | P3(C2 session-lifecycle) ↔ P2 client | **WEAK** | Client session behavior not governed by single SoT |
| 11 | P4 (CF-D6 joint) ↔ Group 2500 API Cat D (cross-arc) | **OVERCOUPLED** | Structural dual-owner joint; shared contract surface with incomplete conformance |

**NEW cross-domain connections not on v2 baseline (per PA integration matrix + Rigby SIGN wiring-state per pair):**

| Domain pair | Wiring state | Verdict | Rationale |
|---|---|---|---|
| **PA → Auth (Group 2400)** | **STRONG (mechanism) + POSTURE-PENDING (α/β/γ + Cat C2 lifecycle)** | REFINED | Mechanism working (DRF auth chain + FleetSignatureAuthentication + TokenAuthMiddleware + PA WS `close(4001)` EXPLICIT stronger than platform silent-degrade default per OBS-D-1 intentional divergence at Cat D §15.2). Cat C2 α/β/γ upstream verdict DEFERRED per Group 2400 xx99. F-B-HIGH-3 attribution propagation across 4-child chain: Cat A observes → Cat B single-sentence → Cat C1 OWNS closure → Cat D §9.3 orthogonal-at-HEAD coupling axis. |
| **PA → API (Group 2500) baseline inheritance + PA-specific delta** | **WEAK (baseline inheritance) + PARTIAL (PA-specific delta)** | CONFIRMED baseline + REFINED delta | Baseline inheritance per parent §2.6.A hard constraint from S2599. PA-specific delta: F5-analog HARD-INVALID / NON-SELECTABLE for Path C-pure at Cat C1 (F5+F-C7) + Cat D (F-D1 F5-analog + F-D-B1-4 + F-D-B2-6) — stricter than Group 2500 baseline. Cat A F8 baseline codification NEGATIVE at `/api/pa/chat/` (soft F5-analog: Path C-pure strictly-worse). |
| **PA → Observability (Group 1700) — T4 PRIMARY handoff** | **MISSING + POSTURE-PENDING** | NEW | Envelope-shape telemetry ABSENT at HEAD (0 shape-version fields across 3 canonical PA-client WS message classes). Cat D §10.4 AC-D8 telemetry emit-signature candidates + per-Consumer conformance metrics + REST↔WS parallel-delivery reconciliation-layer ownership (DEBT-D-4 HIGH) + audit-log hook signature spec (Cat C DEBT-C1-4 SINGLE MOST IMPORTANT per Rigby SIGN Batch 2 Q3(e)). Downgraded WEAK→MISSING per Rigby SIGN refinement #2 (GREENFIELD governance layer = MISSING). |
| **PA → Frontend (Group 2200)** | **WEAK (payload) + PARTIAL (cleanup)** | REFINED | workspaceStore + paStore + assistantApi paChat integrated (payload path); Cat B §4.1 F-B4 U7 paStore 16-field dump reveals 2 UNKNOWN intent fields (`isDockOpen`, `isDockMinimized`) → Cat C2 verdict-scope. 5 syncUser-wiped + 7 persisted + 2 UNKNOWN intent. |
| **PA → Workspace + Agent-Registry** | **STRONG** | CONFIRMED | `execute_with_workspace()` at `core/agents/base_agent.py:5355` + `WorkspaceManager.get_active_workspace()` at `workspace_manager.py:1697` + WORKSPACE_AWARE_AGENTS dispatcher at `core/epa_handlers_tools.py:3873-3922` (20 agents). Handler-internal implicit-gate. This is a P1↔P3(C1) coupling row and F-B-HIGH-3 STRONG counterexample per Rigby SIGN refinement #5. |
| **PA → Mobile (Group 2300, parallel arc, secondary stakeholder)** | **WEAK** | NEW | CF-C4 MobilePushToken.revoked_at NOT set at PA logout (Cat C DEBT-C2-8 + S2403 §9.2 CF-C4 preserved). PA WS mobile client interception UNKNOWN — no mobile-specific PA WS client evidence at HEAD (Cat D §9.1). |
| **PA → Discord** | **ORTHOGONAL** | CONFIRMED | Anti-scope #5 preserved; 4-child verified 0 discord-adjacent PA state touches. |
| **PA → Content (Group 1600, secondary stakeholder)** | **ORTHOGONAL + F-C4 coupling axis** | REFINED | Anti-scope #6 preserved at REST/client layers. F-C4 coupling: PA-produced content lifecycle inheritance from Cat C2 retention verdict — Deliverable + Blog + DocumentEmbedding + ToolCallRecord = retention-impact surfaces. |
| **PA → Fleet-Federation** | **MISSING** | NEW | FleetSignatureAuthentication conveys NO workspace_id at HEAD (Cat C §9.1 boundary gap; anti-scope #7 preserved). |
| **PA → Memory (Group 1300)** | **ADJACENT** | REFINED | F-C4 fold coupling axis: PA-produced DocumentEmbedding retention lifecycle inherits from Group 1300 embedding-layer retention decisions. |
| **REST↔WS T7 joint (dual-owner PA side per CF-D6)** | **OVERCOUPLED (structure) + WEAK (conformance/SoT)** | REFINED | Rigby SIGN refinement #4 applied. Cat D §7.4 T7 cross-transport consistency rule delivered (both REST + WS non-streaming; parallel-delivery reconciliation-layer UNOWNED at HEAD → §9.1a cross-arc ownership decision). |

**POSTURE-PENDING (5 Chris-D-verdict axes at S2699 §11 ratification card):**

- **Cat A** Path A/B/C+island — F8 baseline codification NEGATIVE at `/api/pa/chat/` (soft F5-analog: Path C-pure strictly-worse).
- **Cat B** (a) typed assistantApi.ts island / (b) SHAPE-BLIND preserved / (c) hybrid / (d) defer-no-decision (per Rigby SIGN Q3 tightening — "UNKNOWN" reworded to "defer/no decision").
- **Cat C1** Path A (WorkspaceMember DRF class — requires class CREATION) / Path B (7th middleware path-list constant — boundary gate by path list, NOT membership per Rigby Q3 clarifier) / Path C+compensating (audit-log hook + ADR + docs section — DEBT-C1-4 SINGLE MOST IMPORTANT) — **Path C-pure HARD-INVALID per F5+F-C7** (F5-analog closure discipline).
- **Cat C2** α/β/γ/PA-override (arc-pin lifetime decoupled) / defer+constraints (F-C1 fold) — Group 2400 α/β/γ DEFERRED cascade risk per §14.14.
- **Cat D** Path A (typed WS envelope) / Path B (CONNECT handshake only) / Path C+observability-compensation (SoT-declared + envelope-shape telemetry + shape-version fields per Group 1700 T4 handoff) — **Path C-pure HARD-INVALID / NON-SELECTABLE per F-D1 F5-analog + F-D-B1-4 + F-D-B2-6**.
- **Cross-arc ownership decision (§9.1a):** REST↔WS reconciliation-layer ownership options — (i) reopen at Group 2500 API arc as post-close residual / (ii) Group 2600 post-verdict follow-on requiring dedicated design-prep session / (iii) split telemetry T4 + reconciliation separate T-slot. Relocated to §9 per FOLD-B2-§11-2 (out of §11 ratification card).

**Cross-arc pattern crystallizations extending §14.6 (CX-P7 + CX-P8 second-arc confirmation-pending; CX-P9/P10/P11 NEW CANDIDATE):**

- **CX-P7 CANDIDATE — second-arc confirmation-pending.** "Declared-but-unenforced contract" recurs at PA-slice scope across all 4 planes (Cat A 0/34 `@extend_schema` + Cat B 3 WS classes `observed-JSON-only` + Cat C1 workspace-authz implicit-gate + Cat D F-D-WSENVELOPE-1 PA-slice preservation). **CX-P elevation call: NOT elevated at Group 2600 despite two-arc trigger threshold met — Rigby SIGN Q3 fold caution:** PA F-B-HIGH-3 STRONG counterexample within PA scope complicates dominance claim; promotion condition requires ≥3-5 explicit enforcement-missing points across ≥2 planes (not just implicit/partial) plus explicit second-arc evidence enumeration.
- **CX-P8 CANDIDATE — second-arc confirmation-pending.** "SHAPE-BLIND consumer surface end-to-end pipeline" recurs at PA-slice scope (Cat A hand-constructed dict responses → Cat B 25% typed rate assistantApi + 100% untyped pa_chat.py → Cat D 3 WS classes `observed-JSON-only` + 0 shape-version fields). **CX-P elevation call: NOT elevated at Group 2600 — Rigby SIGN Q3 fold caution:** PA case needs explicit shape-blind choke + propagation demonstration at comparable scale before promoting from domain-local to cross-domain.
- **CX-P9 CANDIDATE (NEW at Group 2600) — "F5-analog HARD-INVALID / NON-SELECTABLE closure discipline."** Cat C1 F5+F-C7 + Cat D F-D1 F5-analog + F-D-B1-4 + F-D-B2-6 parallel structural discipline preventing paper-victory Path C-pure ratification. Emerged from within Group 2600 arc. **Wiring-state at pattern level: methodology/closure-format (analogous to CX-P4 posture-pending overlay).** Single-arc trigger; awaits second arc.
- **CX-P10 CANDIDATE (NEW at Group 2600) — "Compensating-controls pattern as arc's closure criterion."** Cat C1 Path C+compensating (audit-log hook + ADR + docs section) + Cat D Path C+observability-compensation (envelope-shape telemetry + shape-version fields) parallel structural discipline. Emerged within Group 2600. Single-arc trigger.
- **CX-P11 CANDIDATE (NEW at Group 2600) — "Entrypoint multiplicity + legacy compat routes → contract fragmentation."** 3 parallel `/chat/` REST endpoints (Cat A §17) + v1 legacy DEAD-CODE from client (Cat B §17) + 4 WS Consumer classes / 5 URL patterns + PersonalAssistantConsumer naming collision (Cat D §17.1). Cross-plane driver of §4.1 fragmentation. **Mechanism explanation:** multiple entrypoints create multiple schema surfaces; absent a single declared SoT + enforcement, drift becomes the default. Single-arc trigger.
- **CX-P4 extension:** 5-way parallel Chris-D-verdict axes + F5-analog HARD-INVALID annotations per axis = extension of POSTURE-PENDING as arc-close disposition (§14.6). Group 2600 adds F5-analog hard-invalidation dimension not present in Groups 1500/1600/1700/1800/1900/2000+/2100/2200/2400/2500. **Verdict: CONFIRMED as extension** — Group 2600 preserves POSTURE-PENDING pattern class with F5-analog closure-discipline overlay.

**Cross-arc delegation OUT (per S2699 §9):**

- **T4 Group 1700 Observability (PRIMARY handoff — telemetry-scoped after F-S2699-Q4-3 split)** — envelope-shape telemetry emit-signature (Cat D §10.4 AC-D8 canonical candidates: `pa.ws.envelope.conformance.grade` + `pa.ws.unauthorized_connect.count` extends S2504 §7.4 measurement-handoff canonical + `pa.ws.emit.latency_histogram` + `pa.ws.agent_completed.reconciliation_delta`) + per-Consumer conformance metrics for 4 PA-related Consumers at HEAD + `doc_claim_verification` PA-slice claim registration hooks (AU-DCV-1) + audit-log hook signature + emit-point observability plane (Cat C DEBT-C1-4 SINGLE MOST IMPORTANT).
- **§9.1a REST↔WS reconciliation-layer ownership** — cross-arc ownership decision options (i)/(ii)/(iii) — labeled "cross-arc ownership decision (not purely T4)."
- **T5 Group 2300 Mobile (parallel arc, secondary stakeholder)** — CF-C4 MobilePushToken.revoked_at lifecycle at PA logout + PA WS mobile client interception UNKNOWN.
- **T6 Group 1600 Content (secondary stakeholder)** — CF-C8 fold F-C4 retention-impact surfaces (Deliverable + Blog + DocumentEmbedding + ToolCallRecord) — PA-produced content lifecycle inheritance from Cat C2 verdict.
- **Group 2400 xx99 (if reopened)** — PA-slice α/β/γ application evidence.
- **Group 1300 Memory** — F-C4 fold coupling axis: PA-produced DocumentEmbedding retention lifecycle inheritance from Group 1300 embedding-layer retention decisions.
- **Group 2500 API S2599 (baseline inheritance)** — per parent §2.6.A hard constraint; Group 2600 arc does NOT re-litigate; xx99 records adoption + PA-specific delta.

---

### 14.17 Refresh gaps and future arc coverage (v5 update, appended 2026-07-06)

**Append-only per Rigby SIGN Q4 discipline** — do NOT edit §14.7 in place; §14.17 lands as new subsection preserving §14.7 v3/v4 preserved state. §14.7 queue snapshot is FROZEN at v4; §14.17 is authoritative post-Group-2500-and-2600-close.

**What §14 does NOT refresh (v5 update 2026-07-06).**

- Domain pairs where no arc has closed since S1274 AND no arc from the v3/v4/v5 refresh has touched them: Body Systems ↔ *; Advisors persistence; Inbox fanout; Web Push wiring; Mobile Expo push UI. These retain v2 classifications unchanged. **NEW at v5:** PA ↔ Fleet-Federation MISSING flagged at §14.16 (FleetSignatureAuthentication conveys NO workspace_id) — added to §14 domain-pair refinements but not a v2 baseline pair per se.
- Cross-domain connections involving domains with active but unclosed arcs. **As of 2026-07-06: NONE currently in-progress** (Group 2600 PA closed at S2699 2026-07-06; T4 Group 1700 Observability is the NEXT queued arc per S2699 §9.1 telemetry-scoped PRIMARY handoff bundle but has not opened yet). When Group 1700 opens + closes, §14.18 (new subsection) will add observability-side refinements.
- Boundary violations at §7 refined by arc evidence. **NEW at v5:** Cat D §14.3 285-entry path-list gate registry OVERCOUPLED framing + F-B-HIGH-3 STRONG counterexample within broader WEAK/implicit SoT framing (Rigby SIGN refinement #5) both worth §7 augmentation. Noted in §14 but §7 preserved from v2 per append-only discipline.
- §11 risk matrix additions. **NEW at v5:** Group 2500 API 3-quadrant + 1 nesting POSTURE-PENDING framing + Group 2600 PA 5-way Chris-D-verdict axes with F5-analog HARD-INVALID annotations both not slotted into v2 §11 numbered ranking. A future v6 refresh could integrate §14.8-§14.16 findings into re-ranked §11.

**What the queue looks like (v5 update 2026-07-06).** Per `docs/research/OPEN_ARCS.md`:

- Group 1700 Observability / Telemetry / SLOs — **CLOSED at S1799 2026-07-03; §14.8 delivered.**
- Group 1800 HumanAttention / Feedback / Learning — **CLOSED at S1899 2026-07-04; §14.9 delivered.**
- Group 1900 Authority Enforcement — **CLOSED at S1999 2026-07-04; §14.10 delivered.**
- Group 2000+ Event / Integration Architecture — **CLOSED at S2099 2026-07-04; §14.11 delivered.**
- Group 2100 RAG / Document Loading — **CLOSED at S2199 2026-07-04; §14.12 delivered.**
- Group 2200 Frontend (Contract-Surface) — **CLOSED at S2299 2026-07-05; §14.13 delivered.**
- Group 2400 Auth — **CLOSED at S2499 2026-07-05; §14.14 delivered.**
- Group 2500 API — **CLOSED at S2599 2026-07-06; §14.15 delivered at v5 backfill 2026-07-06.**
- Group 2600 PA — **CLOSED at S2699 2026-07-06; §14.16 delivered at v5 2026-07-06.**
- Group 2300 Mobile — NOT STARTED. Post-Group-2500-and-2600-close, mobile is next non-parallel candidate OR parallel arc with T4 Group 1700 Observability per S2699 §9.2 secondary-stakeholder framing.
- **T4 Group 1700 Observability — NOT STARTED; NEXT per S2699 §9.1** telemetry-scoped PRIMARY handoff bundle from Group 2600 PA close. **Arc pin ACTIVE:** `pa-44a6eb70d8814e34` (minted at S2699 close; `tools/pa_local.sh:361` rotated 2026-07-06 per playbook §16 arc-close protocol). Will consume: Cat D §10.4 AC-D8 telemetry emit-signature candidates + Cat C §15.1 DEBT-C1-4 audit-log hook design-spec requirement + §9.1a REST↔WS reconciliation-layer ownership decision options (i)/(ii)/(iii).

**Cross-arc pattern CX-P elevation status (v5 update 2026-07-06).**

- **CX-P7 CANDIDATE ("Declared-but-unenforced contract")** — surfaced at Group 2500 + Group 2600. **NOT ELEVATED at v5** per Rigby SIGN Q3 fold — PA F-B-HIGH-3 STRONG counterexample complicates dominance claim; promotion condition = ≥3-5 explicit enforcement-missing points across ≥2 planes (not just implicit/partial) plus explicit third-arc evidence enumeration. Watching Group 1700 Observability + Group 2300 Mobile arc closes for confirmation.
- **CX-P8 CANDIDATE ("SHAPE-BLIND consumer surface pipeline")** — surfaced at Group 2500 + partially at Group 2600. **NOT ELEVATED at v5** per Rigby SIGN Q3 fold — PA case needs explicit shape-blind choke + propagation demonstration at comparable scale (Group 2500's 803-site consumer flow is the reference). Watching Group 1700 Observability + Group 2300 Mobile.
- **CX-P9 CANDIDATE (NEW at Group 2600) — "F5-analog HARD-INVALID / NON-SELECTABLE closure discipline"** — single-arc trigger. Watching next parent-with-4-children arc for parallel structural discipline emergence.
- **CX-P10 CANDIDATE (NEW at Group 2600) — "Compensating-controls pattern as arc's closure criterion"** — single-arc trigger. Watching next arc for structural pattern replication.
- **CX-P11 CANDIDATE (NEW at Group 2600) — "Entrypoint multiplicity + legacy compat routes → contract fragmentation"** — single-arc trigger. Watching next arc for cross-domain entrypoint fragmentation recurrence.
- **CX-P4 extension (POSTURE-PENDING with F5-analog closure-discipline overlay)** — CONFIRMED at Group 2600. Group 2600 adds F5-analog hard-invalidation dimension to POSTURE-PENDING pattern class.

**Cross-arc delegated items owed to future arcs (per canonical summaries §9; v5 update 2026-07-06).**

- **Group 1700 Observability (T4 NEXT)** — will consume: Group 2600 PA S2699 §9.1 telemetry-scoped PRIMARY handoff (envelope-shape telemetry + per-Consumer conformance + `doc_claim_verification` PA-slice registration + audit-log hook) + §9.1a REST↔WS reconciliation-layer ownership decision. Group 2500 API S2599 §7.4 measurement-handoff canonical (WS unauthorized-connect metric) already partially discharged; Group 1700 T4 extends. Group 2400 Auth Cat D + Group 2400 CF-D3 umbrella roll-up already CONSUMED at Group 1700 close (§14.8).
- **Group 2300 Mobile (parallel)** — will consume: Group 2400 CF-D4 delegation (parallel silent-401 audit + MobilePushToken.revoked_at cascade + 401-handling parity between web + mobile) + Group 2600 CF-C4 preserved (MobilePushToken lifecycle at PA logout) + PA WS mobile client interception UNKNOWN.
- **Group 1600 Content (secondary stakeholder for both Group 2500 + Group 2600)** — CF-C8 fold F-C4 retention-impact surfaces (Deliverable + Blog + DocumentEmbedding + ToolCallRecord) — PA-produced content lifecycle inheritance from Cat C2 verdict.
- **Group 2400 (if reopened)** — PA-slice α/β/γ application evidence + F-B-HIGH-3 STRONG counterexample framing from PA arc.
- **Group 1300 Memory** — PA-produced DocumentEmbedding retention lifecycle F-C4 coupling axis.

---

**End of draft. Status: research / draft — S1274 v2 Rigby SIGN-
with-edits fold preserved via isolation pin `pa-7442a2e2665bd18e`
(Medium confidence); v3 post-arc-close refresh log appended at §14
on 2026-07-03 (append-only; S1274 baseline §1–§13 unmodified); v4
append-only refresh extending §14 with §14.8-§14.14 for Groups
1700/1800/1900/2000+/2100/2200/2400 arc closes on 2026-07-05
(append-only; v2 baseline + v3 §14.2-§14.7 preserved verbatim);
v5 append-only refresh extending §14 with §14.15 backfill for
Group 2500 API arc close 2026-07-06 + §14.16 for Group 2600 PA
arc close 2026-07-06 + §14.17 refresh gaps queue update 2026-07-06
(append-only; v2 baseline + v3 §14.2-§14.7 + v4 §14.8-§14.14
preserved verbatim; 5 Rigby SIGN refinements Chris "agree all"
2026-07-06 ratified via dedicated SIGN pin `pa-db34dc63aa9e4023`
30th consecutive dedicated fresh SIGN pin retirement candidate).**

