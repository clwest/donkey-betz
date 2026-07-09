---
title: "Integration Readiness Matrix — what already exists but is not yet functioning together as one platform"
status: draft (S2734 baseline; awaiting Rigby SIGN + Chris ratification)
authority: research
session_added: 2734
last_verified: 2026-07-09
campaign: platform_integration_engineering_campaign
head_sha: 56df8159
companion_anchors:
  - docs/research/platform/cross_domain_integration_audit.md    # v6 baseline (S1274 + §14.2–§14.18)
  - docs/research/platform_architecture_inventory.md            # 32-domain S1273 map
  - docs/PLATFORM_INVENTORY.md                                  # runtime counts (2026-07-05 snapshot)
  - docs/research/ARCHITECTURE_INDEX.md                         # library navigation
  - docs/EVENT_SYSTEM_INVENTORY.md                              # 14+ event models catalog
  - docs/EMPLOYEE_OS_PRIMITIVES.md                              # anti-duplication matrix
  - docs/research/OPEN_ARCS.md                                  # arc queue
verifier_loop: |
  Draft 1 (2026-07-09, S2734): campaign-open output for the Platform
  Integration Engineering Campaign per Chris directive. Composes the
  Cross-Domain Integration Audit v6 (all 12 §14 arc-close entries) +
  the 11 domain canonical summaries (Memory 1399 → PA 2699) + the 2
  implementation-arc closes (I-0100 in-flight per OPEN_ARCS; I-0200
  closed via ADR-0004 PROVISIONAL) + independent grep verification
  at HEAD 56df8159. Rigby SIGN dispatched on fresh pin
  pa-d80d3164add848dd; 5 claims verified (EventBus PARTIALLY-
  CONFIRMED; DeliverableEvent notification-fanout STALE — model IS
  queried by ops_autopilot / diagnostics / gateway even without a
  post_save receiver; enforce_authority_mode CONFIRMED absent;
  mission-verdict WS + failure-cluster aggregator verified by
  Claude's grep — no consumers found). Claim status is evidence-
  cited or explicitly flagged UNKNOWN. No new architecture proposed.
  No implementation begun.
owner: claude (drafted S2734; Rigby dispatch pa-d80d3164add848dd)
---

# Integration Readiness Matrix

> **What this is.** The output artifact of the Platform Integration
> Engineering Campaign that Chris opened at S2734. It answers one
> question at repository scope: **what parts of Donkey Betz already
> exist but are not yet functioning together as one platform?**
>
> Every claim is repository-backed. Nothing is speculated. Where
> a question can't be answered from the code at HEAD, the row says
> UNKNOWN and names the smallest investigation that would close it.
>
> **What this is not.** An implementation plan. An ADR. A rewrite
> proposal. A domain inventory (that's `platform_architecture_
> inventory.md`). A cross-domain audit (that's `cross_domain_
> integration_audit.md`). This composes those inputs into a
> readiness matrix so the platform's next engineering move is
> visible without re-reading 6 000 lines of research.

---

## 1. Methodology

Six inputs feed the matrix:

1. **Cross-Domain Integration Audit v6** (`cross_domain_integration_audit.md`) — 15-finding S1274 baseline + 12 arc-close refresh entries (§14.2–§14.18). Every §14 subsection was read in full.
2. **11 domain canonical summaries** — Memory (1399), Revenue (1499), Sports (1599), Content (1699), Observability (1799), HumanAttention (1899), Authority Enforcement (1999), Event/Integration Architecture (2099), RAG/Document Loading (2199), Frontend (2299), Auth (2499), API (2599), PA (2699). Referenced via audit §14 folds — not re-read line-by-line to keep this matrix bounded.
3. **`PLATFORM_INVENTORY.md`** — runtime counts as of 2026-07-05 snapshot (83 agents in AGENT_MAP, 80 spiders, 415 Celery tasks, 92 enabled Periodic tasks, 113 PA tool schemas, 585 concrete models, 96 Discord commands, 9 body systems, 6 LLM providers).
4. **Independent grep at HEAD 56df8159** — verified 8 load-bearing audit claims via ripgrep against the current tree; corrections folded inline.
5. **Rigby SIGN dispatch** — fresh pin `pa-d80d3164add848dd` (30th consecutive fresh SIGN pin per §14.16 close discipline). One correction folded (DeliverableEvent has query-side consumers even though it has no post_save receiver — audit "zero consumer" claim STALE at HEAD).
6. **`OPEN_ARCS.md`** — 11 research arcs closed 2026-07-01 → 2026-07-06 (Memory through PA); 2 implementation arcs (I-0100 in flight per OPEN_ARCS §In-progress at S2700 open; I-0200 closed 2026-07-07 via ADR-0004 PROVISIONAL); T4 Group 1700 Observability arc queued NEXT.

### Column definitions

Each row has 9 columns:

| Column | Values | Meaning |
|---|---|---|
| **Research** | Y / P / N | Y = canonical summary xx99 closed for this domain; P = partial coverage from adjacent arc; N = no arc has touched it |
| **Architecture** | Y / P / N | Y = ADR ratified OR design-complete class (Authority §14.10, Event §14.11, RAG §14.12 all closed with this class); P = design-prep only; N = no design document |
| **Implementation** | Y / P / N | Y = feature implemented and observable at HEAD; P = partial (some code lands, other pieces missing or flag-gated); N = not built |
| **Integrated** | Y / P / N | Y = cross-domain consumers actively read what this domain produces; P = weak / flag-gated / minimal; N = producer exists, no cross-domain consumer |
| **Operational** | Y / P / N | Y = beat schedule / worker / signal handler fires in production and is observable via `CeleryTaskEvent` or equivalent; P = flag-gated or fire-and-forget; N = latent (code exists, never fires) |
| **Verified** | Y / P / N | Y = grep/ORM evidence at HEAD 56df8159; P = partially verified; N = claim carried forward from research without HEAD-side verification |
| **Blocking Deps** | domain names | Which unresolved gaps must land before this row can flip to Y across all columns |
| **Recommended next step** | Research / ADR / Wire / Verify / None | The **smallest useful action** — not the largest ambition. `None` means the domain is already well-integrated for its current scope |
| **Evidence** | file:line + doc anchor | Where a reader can independently confirm |

**Reading rule.** A row where `Research=Y / Architecture=Y / Implementation=P / Integrated=N` is the most valuable kind — it means the platform *already knows* how to close the gap, the pieces exist, and only the wire-up is missing. §5 leverage sequences pick from that bucket.

---

## 2. Integration Readiness Matrix

Organized by the 32-domain map from `platform_architecture_inventory.md` (S1273) grouped into 8 architectural super-domains. Domains not touched by any arc are listed at §2.9 with unchanged v2 baseline classification.

### 2.1 Cognition & agent layer

| Domain | Research | Architecture | Implementation | Integrated | Operational | Verified | Blocking deps | Recommended next step | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| PA (Rigby) subsystem | Y (S2699) | P (5 Chris D-verdict axes open) | Y (mechanism operational per §14.16 canonical verdict) | Y | Y | Y | Cat C2 α/β/γ auth cascade; envelope-shape telemetry (T4) | **Research** — T4 Group 1700 Observability arc to consume Cat D §10.4 telemetry emit-signature bundle | `core/services/unified_pa_entrypoint.py` (7,613 lines); `core/services/tool_dispatcher.py` (1,267 lines); audit §14.16; PA-internal 4-plane pairwise coupling matrix at §14.16 |
| Traditional agents (AGENT_MAP) | Y (S1274 §2.1) | Y | Y | Y | Y | Y | None (in-scope) | **None** — agent dispatch to LLM providers is STRONG per audit; only concern is §7.5.1 direct `openai` imports (see 2.7) | `core/agent_router.py`; 83 agents per PLATFORM_INVENTORY; `core/agents/base_agent.py` (5,575 lines) |
| Employee OS + MissionRunner | Y (S1254 foundational; refined in §14.9/§14.10) | Y | Y (3 employees: Docs Manager, Platform Auditor, Chief of Staff) | P (workflow lands as `OpsRun(domain='mission')` + `OpsRunEvent`; verdict does not broadcast) | Y | Y | Frontend WS broadcast on `verdict_issued` (§3.1) | **Wire** — WS push on `emit_mission_verdict()` post_save to eliminate 15s polling window | `core/employees/mission_runner.py:1530-1570`; `core/employees/mission_verdict.py:63`; `core/models_ops_runs.py`; audit §3.1 |
| Boardroom / Advisors | P (S1274 §2.1; §14 does not refresh) | N | Y (30 functional-domain advisors) | P (prompt-context injection only) | Y | Y | Persistence contract (§10.2) | **Research** — advisor persistence contract (S1273 §9 #7 owed research) | `advisors/registry.py:75` (in-memory only); audit §10.2 §3.10 |
| Claude Code (autonomous responder) | N | N | Y (3-way conversation pattern with PA) | Y (STRONG per §2.1) | Y | Y | None | **None** — pattern is stable; no cross-domain gap flagged in any arc | `core/services/claude_code_tool.py` (dispatched via `claude_code_tool` PA tool) |

### 2.2 Data ingestion & intelligence

| Domain | Research | Architecture | Implementation | Integrated | Operational | Verified | Blocking deps | Recommended next step | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| Spider framework (80 spiders / 41 categories) | Y (S1273 §3.8; touched by every arc) | Y | Y | Y | Y | Y | Spider-drought event (§3.5); dedup-collision alerting (§3.9) | **Wire** — `SpiderDroughtEvent` producer for Platform Auditor; drought detection today runs daily → 24h invisibility window | `core/services/spider_registry.py`; `LegacySpiderData` + `SpiderExecutionLog`; audit §3.5, §3.9 |
| Signal Engine + AutoTopic | Y (touched by every arc) | Y | Y | P | Y | Y | Pattern-strength → HAI threshold (§3.8) | **Wire** — `PatternCriticalityEvent` producer for pattern_strength > 0.9 → auto-HAI | `core/services/signal_aggregation_service.py`; `SignalCluster` model; audit §3.8 |
| Sports / DBAO | Y (S1599 four-axis compound maturity) | P (T1 R.SPORTS.POSTURE Chris-gated) | P (Cat E DBAO codename unmaterialized; verify_betting_outcomes + daily_betting_digest zero-fire beat) | N (island by intent per POSTURE-PENDING) | P | Y | Chris D-verdict on integration-vs-island posture (§12.3) | **ADR** — T1 R.SPORTS.POSTURE + T1 R.DBAO.CODENAME (Chris) | audit §14.4; `sports_odds` is not a valid `SignalCluster` data_type; `BettingOutcomeVerifier` ↔ `MLPrediction` decoupled |
| Body Systems (9) + BodyCoordinator | P (S1273 §3.30 drift acknowledged) | N | Y (9 systems scanned every 10 min) | P (HeartBeat has 6 readers at HEAD — status display + Discord alert only; no HAI escalation) | Y | Y (grep 2026-07-09) | HAI escalation on IMMUNE/DIGESTIVE degradation | **Wire** — `HeartBeat`-degradation → `HumanAttentionItem(urgency='high', source_type='system_degradation')` | `core/services/heart.py:705` reads heartbeats for Discord alert path; `core/views_heart.py:78` reads for status display; audit §2.2 finding partially STALE (readers exist — HAI producer missing) |

### 2.3 Content & workflow

| Domain | Research | Architecture | Implementation | Integrated | Operational | Verified | Blocking deps | Recommended next step | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| Content Pipeline (deliberation runner) | Y (S1699) | P (4 Chris D-verdict axes D65a–D65e open) | Y | P (Content ↔ Signal STRONG; Content → Inbox notification MISSING; post-publish correction ABSENT across 3 rails) | P (`auto_publish_approved_blogs` beat MISSING at HEAD despite 5 docs claiming daily 6 AM) | Y | 4 D65 posture ADRs; `auto_publish_approved_blogs` beat wiring | **ADR** — D65a/b/c/e (Chris) OR **Wire** the missing beat (immediate; independent of D65 posture) | audit §14.5; `core/services/content_deliberation_runner.py` (3,275 lines); `ClaimsPack`, `PublishGate` (SelfBlog-only) |
| Deliverables | Y (touched by S1699 + §14.5 F.C1/C2) | P | Y | P — see below | Y | Y | Notification fanout consumers on `DeliverableEvent` | **Wire** — `DeliverableEvent(direction='up', to='ready')` post_save → notification service | `core/models_deliverables.py`; `core/signals/deliverable_status_signals.py:94,205`; `DeliverableEvent` HAS query-side readers (S2734 correction — audit stale) but ZERO `sender=DeliverableEvent` receivers at HEAD |
| Initiative Pipeline (5-stage) | P (touched by S1699 + §14.5) | Y | Y | P (Initiative ↔ Content STRONG; `Revenue → Initiative` MISSING) | Y | Y | `OpportunityEscalationEvent` producer | **Wire** — revenue-threshold → auto-Initiative creation (audit §3.7) | `core/services/conversation_initiative_pipeline.py:30-155`; audit §3.7, §14.3 |
| Revenue / Outreach / Engagement / Close | Y (S1499) | P (5 Chris-gated ADRs T1–T5 + T8 open) | P (Cat F freelance orphaned; 20-writer convergence on `Opportunity` with no write-authority contract) | N (no outreach delivery — MISSING all channels: email + LinkedIn + Rigby-DM + in-app) | P (`_impl_run_freelance_opportunity_scout` UNGUARDED 5-phantom-field writer at `tasks_ops.py:2239-2251`) | Y | 5-way T-slot ADR bundle; sibling JobContracts (Revenue Employee + Income/Jobs Employee — D55) | **ADR** — sibling JobContracts + outreach delivery ADR (Chris) | audit §14.3; S1499 §7.4 D55; `core/services/ops_autopilot/impact.py::MultiTouchAttributor._attribute_event:1233-1290` |
| Newsletter | P (surfaced in §14.5 as CRITICAL EXPERIMENTAL) | N | P (dry_run parked >4mo; live-send infrastructure ABSENT) | N | N | Y | Newsletter live-send ADR | **ADR / research** — decide whether Newsletter is post-D65 dependency or its own posture | audit §14.5; S1604 §14 T.15.C2 |

### 2.4 Knowledge & memory

| Domain | Research | Architecture | Implementation | Integrated | Operational | Verified | Blocking deps | Recommended next step | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| Memory (7-flavor catalog Cat A–H) | Y (S1399) | Y | Y (per-flavor) | P (`AgentMemory.create_memory` write-authority MISSING — no user FK gate, no rate limit, no audit; `MemoryPromotionService` auto-saves every PA turn) | Y | Y | Write-authority framework ADR (T10 HIGH) | **ADR** — Memory write-authority framework | audit §14.2; S1302 §15 T10 |
| RAG (2 lanes) | Y (S2199 spec-complete/execution-pending) | Y (ADR-0004 PROVISIONAL, 2026-07-07) | P — LOCAL `core.rag` vs PROD `core.rag_integration`; no runtime selector | P (`search_docs` hardcodes LOCAL; `kb_tool semantic_search` hardcodes PROD; PA turn does NOT auto-invoke either) | P | Y | 19 T-slot follow-on queue distributed (T22/T13 T0/Gate) | **Wire** — T-slot execution PRs per ADR-0004 §4.1 dependency structure | audit §14.12; `docs/research/implementation/rag_corpus_substrate_maturity/I-020099_*.md`; ADR-0004 PROVISIONAL |
| Documentation cascade (4-step) | Y | Y | Y | Y | Y | Y | None | **None** — cascade is documented, embedded, and drift-verifiable via `verify_doc_claims` | 4-step cascade rule in memory; `python manage.py build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `embed_documents` |
| Embeddings + Vector search (pgvector) | Y (touched via S2199) | Y | Y | Y | Y | Y | None | **None** — HNSW index + `DocumentEmbedding` well-owned | `DocumentEmbedding` model; `pgvector` extension; `EmbeddingService` |

### 2.5 Human interface

| Domain | Research | Architecture | Implementation | Integrated | Operational | Verified | Blocking deps | Recommended next step | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| HumanAttention (HAI) | Y (S1899) | P (D80 4-option posture open) | Y (22 creation sites at HEAD; grep 2026-07-09) | P — see six-plane learning-surface fragmentation | Y | Y | 6 T0/Gate ADRs + 47 total post-arc items; F7 CRITICAL 4-break-point compound learning-loop | **Wire** — failure-cluster aggregator → HAI (audit §3.3); pattern-criticality → HAI (audit §3.8); revenue-opportunity → HAI (audit §14.3 F.D1) | audit §14.9; F7 CRITICAL compound learning-loop; grep confirms 22 `HumanAttentionItem.objects.create` files at HEAD |
| Notifications (5 delivery paths) | P (§12.2 owed) | N | Y (Web Push + Expo + Discord + Inbox + HAI all exist) | N (no unification service; same alert can reach same user 4-5×) | Y | Y | Unification design space (§12.2) | **Research** — Notification Unification Study (P0 per §12.2 in audit v6) | `PushSubscription`, `NotificationLog`; audit §5.4, §12.2 |
| Inbox / Messaging | P (§14 does not refresh) | N | Y (`DirectMessage` + `MessageThread`) | P (Inbox ↔ Frontend STRONG; Inbox ↔ Discord WEAK; Inbox ↔ Mobile UNKNOWN) | Y | Y | Deliverable → Inbox fanout | **Wire** — `DeliverableEvent(status='ready')` → Inbox message with deliverable link | `core/models_messaging.py:21,99`; audit §2.6 |
| Discord bot (25 Cogs / 96 commands) | Y (S1273 §3.20) | N (refactor candidate) | Y (11,677-line god-service) | Y | Y | Y | Refactor plan | **Research** — refactor plan (LOW priority; works today; blast radius on change is a runtime risk per §7.6) | `core/services/discord_bot.py`; audit §4.1, §7.6 |
| Voice / Avatar (ElevenLabs + Runway + HeyGen F2F) | P | P (HeyGen F2F.1 stub; F2F.3 planned) | P | P (STRONG for TTS/voiceover; F2F stub) | Y | Y | Avatar roadmap ADR (§10.2) | **Research** — Avatar Roadmap Consolidation | `core/services/discord_bot.py` (TTS integration); `Voice/Avatar` domain 21 in S1273 §3.21 |
| Frontend (61 routes / 5-tab workspace) | Y (S2299) | Y | Y | P — "accreted UI mesh with declared-but-unenforced contracts" | Y | Y | 4-axis handoff bundle (silent-401 + logout cleanup + session lifecycle + permission floor) DISCHARGED at S2499 Auth close (see 2.7) | **Wire** — post-Auth-close Group 2500 API + 2600 PA T1 items | audit §14.13; S2299 §5.1 canonical verdict |
| Mobile (Expo) | N (Group 2300 Mobile NOT STARTED) | N | P (models exist; UI + wiring unknown) | UNKNOWN | UNKNOWN | N | Group 2300 Mobile arc | **Research** — open Group 2300 Mobile arc (per §14.17 queue — parallel or T4-adjacent) | audit §10.2 §14.17 |

### 2.6 API + ops layer

| Domain | Research | Architecture | Implementation | Integrated | Operational | Verified | Blocking deps | Recommended next step | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| API layer (1,857 URL patterns / 51 WS consumers) | Y (S2599) | P (3-quadrant + 1 nesting POSTURE-PENDING) | Y | P — mechanism operational; contract SoT partial across 4 planes (Cat A backend declaration + Cat B consumer + Cat C session lifecycle + Cat D permission-floor / REST↔WS) | Y | Y | 4 GREENFIELD governance layers; 285-entry path-list gate registry OVERCOUPLED; SHAPE-BLIND interceptor at `api.ts:43-62` | **ADR** — Cat A Path A/B/C strictness (drf-spectacular wire-up); permission-floor governance (Cat B c) | audit §14.15; `core/auth_middleware.py:94-561` 285-entry registry; S2504 §14.3 |
| Authentication / Session | Y (S2499) | P (4-axis P0-A/B/C parallel Chris D-verdict) | Y | P — "ACCRETION with declared-but-unenforced contracts" | Y | Y | 14 co-equal P0-A/B/C items; silent-401 SYSTEMIC (~630/1300 call-sites); Sidebar logout doesn't revoke backend token; `enforce_authority_mode` field ABSENT at HEAD (grep 2026-07-09) | **ADR + Wire** — F-D-SIDEBAR-1 (immediate one-file fix in `Sidebar.tsx:356`); F-D-CALL-1 803-scale silent-401 remediation (ADR gated) | audit §14.14; grep 2026-07-09 confirms `enforce_authority_mode` = zero hits |
| Governance (4 planes) | Y (S1999 authority arc + S1269 baseline) | Y (design-complete via S1999 17 decisions ratified) | P — runtime-scaffolding class; only Boundary 5 warn-mode event fires; 6 KillSwitch reads all management/audit — zero enforcement dispatch (grep 2026-07-09) | N (KillSwitch write path exists; no enforcement consumer); N (JobContract.authority observed but not enforced) | P (warn-mode fires 13 events / 5 days / 4 employee_handles at S1902 close) | Y | R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS + R.AUTHORITY.ACTOR-KWARGS-CELERY + R.AUTHORITY.ACTOR-STEP-CONTEXT | **Wire** — add `enforce_authority_mode` model field per T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS then activate KillSwitch dispatch reader (P3 D94 reader spec) | audit §14.10; `core/services/ops_autopilot/governance.py:2192` proves the only KillSwitch reader is a status-dict populator, not an enforcement consumer |
| Automation / Celery (415 tasks / 92 enabled beats) | Y | Y | Y | Y | Y | Y | Sports zero-fire beat pair (`verify_betting_outcomes` + `daily_betting_digest` — CRITICAL); `auto_publish_approved_blogs` beat MISSING | **Wire** — restore 3 missing beat entries with pre-restore idempotency gate for `_settle_wager()` | `core/celery.py` beat schedule; PLATFORM_INVENTORY (92 enabled + 5 disabled); audit §14.4 §14.5 |
| Observability (5 telemetry layers) | Y (S1799) | P (D74 6-axis correlation-spine posture open) | P (retention INCONSISTENT — only 1/14 event models have date-based purge; Cat D `ToolCallRecord` 100% NULL `trace_id`) | Y (writers) / P (consumers at best partially-wired) | Y | Y | R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.OBSERVABILITY.D74-SPINE-POSTURE (paired T0/Gate) | **ADR** — Chris D-verdict on D74 spine posture (blocks 9 T1 items downstream) | audit §14.8; S1704 F1 100% NULL trace_id |
| Event Bus (8 streams / 1 DLQ / 3 consumer groups) | Y (S2099 design-complete) | Y | P — 3 of 8 streams have confirmed callers at HEAD (grep 2026-07-09) — up from S1274 v2 baseline of 1 | P (design-complete runtime-scaffolding; T1 composition-consistency register + HAI dual-emission + spider-data substrate + F.PER-USER-AUTHORITY emission wiring all pending) | P | Y | 2 T0/Gate (canonical-seam CONSUMED + Fleet-Events INTENTIONAL SIDECAR RATIFIED); 7 T1 (composition register #1 strict closure pre-req) | **Wire** — T1 items in the S2099-ratified order: #1 composition register → #2 HAI dual-emission (parallel-executable) → #3 spider-data substrate consolidation | audit §14.11; grep 2026-07-09 shows `publish_validation_required_event` + `publish_validation_decided_event` now have callers (`hitl_validation.py`) alongside `publish_opportunity_scored_event` (`scoring_dispatcher.py`); SPIDER_DATA / OUTCOME_RECORDED / SYSTEM_ALERT still zero non-definition callers |
| Tool Dispatcher (156 handlers / 113 schemas / 8 enrichment services) | Y (S2699 §14.16 4-plane consolidated shape) | Y | Y | Y | Y | Y | Envelope-shape telemetry ABSENT at HEAD (0 shape-version fields across 3 canonical PA WS message classes) | **Wire** — T4 Group 1700 Observability handoff bundle | `core/services/tool_dispatcher.py` (1,267 lines); `core/services/pa_tool_schemas.py`; audit §14.16 |
| Analytics | N (§3.11 partial only) | N | P (`ConversionEvent` at `core/models_unified_system.py:19761` defined but writer path unverified; Frontend `usePageTracking()` is fire-and-forget Redis) | N (no persistent `AnalyticsEvent` correlates published deliverable with downstream traffic) | N | Y (grep) | Analytics event schema design | **Research** — `AnalyticsEvent` schema + producer/consumer contract | audit §3.11, §6.5 |

### 2.7 Cross-cutting concerns

| Domain | Research | Architecture | Implementation | Integrated | Operational | Verified | Blocking deps | Recommended next step | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| LLM provider factory usage | Y | Y | P — 9 files / ~15+ sites bypass `openai_client_factory` (S1274 §7.5.1 Rigby grep) | Y | Y | Y | Global sweep + pre-commit hook | **Wire** — global sweep to route through factory + pre-commit hook to block new violations | audit §4.2, §7.5.1; memory rule `feedback_openai_client_factory.md` |
| Actor / Identity attribution (3-role vocab: executor / sponsor / principal_user) | Y (S1271 canonical) | N | P (19 concepts + 22 attribution surfaces exist; 5 cross-domain write paths lack carriage contract) | N | Y | Y | Cross-write-path identity carriage design (P0-companion per §12.4) | **Research** — Cross-Domain Identity Carriage (audit §12.4 P0-companion) | audit §12.4 elevated; S1271 catalogue |
| Notification unification | P | N | Y (5 delivery paths) | N | Y | Y | Unification service design | **Research** — Notification Unification Study (§12.2) | audit §12.2 |
| Provenance | Y (via docs cascade + `doc_claim_verification`) | Y | Y | Y | Y | Y | None | **None** — `_provenance.json` fresh at S2732 close; `verify_doc_claims --only-drift` operational | `core/services/doc_claim_verification.py` (Session 1099); `docs/_provenance.json` |
| Workspace model | Y (S2699 F-B-HIGH-3 STRONG counterexample) | Y | Y | Y (P1↔P3(C1) NESTED per PA pairwise matrix) | Y | Y | None (in-scope) | **None** — `ProjectWorkspace.user` OneToOneField + `execute_with_workspace()` at `base_agent.py:5355` fails-closed at write boundary | audit §14.16 F-B-HIGH-3; `core/agents/base_agent.py:5355`; `core/services/workspace_manager.py:1697` |
| Canonical-authority routing | Y (S1250 domain field enforcement) | Y | Y | Y | Y | Y | None | **None** — `OpsRun.domain` field enforces ops vs mission separation per S1250 PR 3 | `core/models_ops_runs.py` |

### 2.8 Frontier work — currently under implementation

| Domain | Research | Architecture | Implementation | Integrated | Operational | Verified | Blocking deps | Recommended next step | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| Arc I-0100 (Observability Correlation Spine + Mission Evidence Substrate) | Y | P (Stage 1 exit-gate cleared per OPEN_ARCS S2700) | P (in flight per OPEN_ARCS §In-progress; ADR-B + ADR-A + ADR-C tracks) | P | P | UNKNOWN (arc in flight — mid-implementation) | Chris ratification on 8 folds F1–F8; §14 audit-refresh gap noted at I-0200 close | **Verify** — check current I-0100 stage state via `context-kit orient` / OPEN_ARCS at next session open | OPEN_ARCS.md §In-progress; audit §14.18 notes I-0100 close bundle (PR #2976) did NOT append a §14 entry — backfill deferred |
| Arc I-0200 (RAG Corpus Substrate Maturity) | Y | Y (ADR-0004 accepted PROVISIONAL 2026-07-07) | Y (docs-only implementation; no runtime code changed) | Y (via ADR-0004 substrate spec) | N (execution-pending; T-slot execution PRs blocked on prior T-slots) | Y | `IB-2199-BOR-01` BLOCKED_ON_RESEARCH per ADR-0004 §4.2 | **Research** — BOR-01 discharge is now a first-class implementation-arc prerequisite for any ADR-0004 successor | audit §14.18; ADR-0004 §3.1, §4.1, §4.2 |

### 2.9 Domains with unchanged v2 baseline (§14.17 does not refresh)

Per audit §14.17 (v5 update 2026-07-06): these domain pairs have not been touched by any arc since S1274 v2 baseline. They retain v2 classification unchanged. Listed here for completeness; **NOT candidates for the leverage sequences in §3** because their readiness is not evidence-refreshed.

| Domain | v2 classification | v2 anchor |
|---|---|---|
| Body Systems ↔ * (broader integration surface) | MEDIUM readiness; UNCLEAR ownership | audit §2.2 §10.2 |
| Advisors persistence | LOW-MEDIUM; in-memory only | audit §10.2 §3.10 |
| Inbox fanout (beyond DeliverableEvent) | UNKNOWN | audit §2.6 |
| Web Push wiring detail | WEAK | audit §2.6 |
| Mobile Expo push UI | UNKNOWN | audit §2.6 |

---

## 3. Highest-leverage integration sequences

**Optimizing criterion.** Not "which domain has the most missing pieces" — that biases toward large scope. Instead, **which pair-connection unlocks the most other rows in the matrix once wired**. Effort × leverage × existing-scaffolding readiness.

Each sequence names: (1) the two systems being connected, (2) the specific wiring change, (3) what other rows the connection unblocks, (4) rough effort classification (S = small = <1 day; M = medium = 1–5 days; L = large = >5 days), (5) blocking prerequisite if any.

### 3.1 Sequence L1 — Wire `emit_mission_verdict()` → Frontend WebSocket broadcast (**effort S, leverage HIGH**)

- **Connect.** Employee OS mission completion (`OpsRunEvent(label='verdict_issued:*')` written per `mission_runner.py:1530-1570`) → Frontend Active-Work panel via WebSocket push.
- **Why leverage is high.** Employee OS runs the Documentation Manager, Platform Auditor, and Chief of Staff every day. Every mission Chris kicks off ends with a 15-second polling window on Frontend before Active Work reflects the verdict. The write path exists (`OpsRunEvent`), the tests exist (11 test files reference `verdict_issued`), the frontend WS infrastructure exists (51 WS routes per PLATFORM_INVENTORY). **The single missing edge is a `channel_layer.group_send` on `OpsRunEvent.post_save` where label starts `verdict_issued:`.**
- **What this unlocks in the matrix.** Row 2.1 Employee OS flips from `Integrated=P → Y`. Precedent for the same pattern on `DeliverableEvent` (3.2 below). Removes the polling anti-pattern from Frontend before Group 2300 Mobile opens with the same requirement.
- **Blocking prerequisite.** None. Runtime-owner well-owned (§10.1).
- **Blast radius.** LOW. Additive receiver on an existing model; no schema change.

### 3.2 Sequence L2 — Wire `DeliverableEvent(status='ready')` → Notification fanout (**effort M, leverage HIGHEST**)

- **Connect.** Content Pipeline's `DeliverableEvent` post_save → a single fanout service that gates: Web Push (if user opted in), Discord (if channel configured), Inbox (`DirectMessage` create), HAI (if requires human decision).
- **Why leverage is highest.** This is the P0 mission from audit §12.2 (Notification Unification Study), and the raw materials exist:
  - Publisher exists — `core/signals/deliverable_status_signals.py:94,205`.
  - Consumers exist for query-side reads (`ops_autopilot/impact.py`, `diagnostics/coo_daily.py`, `td_handlers_gateway.py`, `views_deliverables.py`, `employees/status.py`) — the S2734 correction to audit §3.2's "zero consumer" claim.
  - The 5 delivery channels exist (Web Push + Expo + Discord + Inbox + HAI).
  - What's missing is **one service that dedups + fans out**, not five services.
- **What this unlocks in the matrix.** Row 2.3 Deliverables flips `Integrated: P → Y`. Row 2.5 Inbox flips `Integrated: P → Y`. Row 2.5 Notifications flips `Integrated: N → P`. Row 2.5 HumanAttention gains a producer for `Deliverable → HAI (approval required)`. Sets the pattern for Sequence L4 (Failure-Cluster → HAI).
- **Blocking prerequisite.** Cross-Domain Identity Carriage (§12.4 P0-companion) *should* be resolved first per Rigby's S1274 v2 fold — otherwise the notification loses actor identity crossing the S1271 F6 drop-boundary (HTTP → Celery → Signal → Handler). **Ship without it and the notification works; ship without it and cross-domain ROI attribution stays broken.**
- **Blast radius.** MEDIUM. New service + 5 channel adapters + dedup contract. But each channel adapter is a leaf, testable in isolation.

### 3.3 Sequence L3 — Wire `enforce_authority_mode` field → activate KillSwitch enforcement dispatch (**effort M, leverage HIGH**)

- **Connect.** Add the `enforce_authority_mode` model field (currently ABSENT at HEAD per grep 2026-07-09) → wire the missing `KillSwitch` enforcement dispatch reader (P3 D94 reader spec from S1999) → point the reader at agent / task / view boundaries.
- **Why leverage is high.** Governance is design-complete (S1999 ratified 17 decisions across 5 successive "agree all" rounds). What's missing is the runtime binding. Zero enforcement dispatch consumers exist today (grep 2026-07-09 confirms `governance.py:2192` is a status-dict populator, not an enforcement gate). Once the field lands and the reader activates, 4 governance planes stop drifting into non-composed state and the platform gains its first "biggest architectural risk" mitigation per Rigby S1273.
- **What this unlocks in the matrix.** Row 2.6 Governance flips `Implementation: P → Y` and `Integrated: N → P`. Row 2.6 Authority Enforcement's 20-item T-tier queue starts unblocking. Row 2.7 Cross-Domain Identity Carriage becomes evaluable (governance can consume actor identity carriage now).
- **Blocking prerequisite.** R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS (S1999 T1 highest-priority per F5 severity). Chris-gated per governance authority evolution doc.
- **Blast radius.** MEDIUM-HIGH. Adds a runtime gate that today's code has been shipping without. Fail-open should be the initial default; fail-closed post-observation window.

### 3.4 Sequence L4 — Wire failure-cluster aggregator → HAI producer (**effort S, leverage MEDIUM**)

- **Connect.** Add an aggregator over `CeleryTaskEvent(status='FAILURE')` (already existing telemetry) → threshold gate (50 failures / 5-min window is the audit §3.3 speculative default) → `HumanAttentionItem.objects.create(urgency='critical', source_type='failure_cluster')`.
- **Why leverage is medium.** Cascade failures today go 10+ min unnoticed (audit §3.3). The producer exists — `CeleryTaskEvent` write side is STRONG per Observability §14.8. The consumer surface exists — 22 HAI creation sites at HEAD (grep 2026-07-09). What's missing is the aggregator threshold + one new HAI producer. **This is the pattern proof-of-concept that L5 (LLM cost overrun → auto-freeze) reuses.**
- **What this unlocks in the matrix.** Row 2.5 HumanAttention gains a critical producer. Row 2.6 Observability gets one cross-domain consumer for the first time (§6.1 confirmed: only DeliverableEvent has cross-domain today). Sets the pattern for Body-Systems → HAI (2.2) using the same aggregator + threshold shape.
- **Blocking prerequisite.** SLO threshold is speculative — Chris ratification (or a 1-week observation window) on the 50/5-min threshold.
- **Blast radius.** LOW. Read-only over existing telemetry; write into existing HAI model.

### 3.5 Sequence L5 — Add `LLMCallEvent.cost_usd` field → wire LLM cost overrun → Governance auto-freeze (**effort M, leverage HIGH**)

- **Connect.** `LLMCallEvent` write path (from `llm_call_wrapper.py:195`) already fires per call; the `cost_usd` field is MISSING (audit §3.4). Adding it costs a migration + one `_estimate_cost()` call at wrapper. Then aggregator sums cost by window → `GovernanceState.set_mode('freeze')` on threshold breach.
- **Why leverage is high.** Runaway spend of $500+ is silent today (audit §3.4). This is the platform's most-obvious financial-risk gap. And it uses the same aggregator pattern as Sequence L4 — one implementation pattern, two consumers.
- **What this unlocks.** Row 2.6 Governance gains its first auto-freeze producer. Row 2.6 Observability gains cost-tracking as a first-class column. §7.5.1 direct `openai` import sweep becomes actionable (all callers must route through factory to emit `LLMCallEvent` with cost).
- **Blocking prerequisite.** L3 (`enforce_authority_mode` runtime binding) OR ship without governance auto-freeze and use the cost signal as an operator warning first, then gate.
- **Blast radius.** MEDIUM. New model field + new field on emitter + new aggregator + new governance-mode transition path.

### 3.6 Sequence ordering — do L1 → L2 → L4 in that order

- **L1 first (small, contained).** Establishes the WS-push-on-post_save pattern. Frontend gets its first push instead of poll for a domain other than Chat.
- **L2 second (medium, highest leverage).** Reuses L1's pattern-precedent and unlocks 4 downstream rows. Do NOT ship without at least a stub of Cross-Domain Identity Carriage (§12.4) or the notification loses actor identity across the drop-boundary — set the expectation up front.
- **L4 third (small, medium leverage).** Introduces the aggregator + threshold + HAI shape that L5 reuses. Body-Systems → HAI in 2.2 follows immediately with the same shape.
- **L3 and L5 are separate ADR tracks.** Do NOT parallelize with L1/L2/L4 unless Chris explicitly funds a second track. L3 is Chris-gated per R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS and dedicates governance enforcement design. L5 depends on migration + a cost model + operator ratification on freeze thresholds.

**Alternative sequence if Cross-Domain Identity Carriage is prioritized first.** Do §12.4 identity-carriage research → resolve then do L1 → L2. This produces well-attributed notifications from day 1 at cost of ~1 arc of research delay.

---

## 4. What NOT to prioritize first

Explicitly, so scope discipline holds:

- **Sports/DBAO integration.** POSTURE-PENDING per audit §14.4. Not a defect — a Chris-gated architectural decision. Do not wire it before T1 R.SPORTS.POSTURE + T1 R.DBAO.CODENAME ADRs land. Extracting the sports island prematurely would bake island posture without deciding it.
- **Governance plane composition (4 planes → one).** BLOCKED on STAGE 3 Symbol Mapping Option Selection per ARCHITECTURE_INDEX §9. 2–3 research cycles away.
- **`discord_bot.py` refactor.** Works today. Blast radius on any change is a runtime risk (§14.15 v5 fold note augments §7). Refactor plan is research-only.
- **PA / Rigby extraction.** Gateway refactor (§9.9) that requires converting in-process calls to RPC. Every other extraction candidate must be stable first.
- **Employee OS extraction.** Ready-adjacent (§9.1 HIGH readiness) but stabilization still landing (Platform Auditor + Chief of Staff recent additions per S1257/S1258 + beat wiring in progress). Extract at 1–2 cycles' notice, not now.

---

## 5. Open questions requiring Chris D-verdict (research owed, not implementation)

Six items are Chris-gated *before* any of §3's sequences can complete at full scope:

1. **§14.14 4-axis P0-A/B/C parallel Chris D-verdict** — the Auth arc closed with 14 co-equal P0 items across silent-401 remediation + token lifecycle + endpoint-specific. Chris ratification sequences these.
2. **§14.5 D65a–D65e Content posture** — 4 orthogonal Chris-gated ADRs on Deliverable canonicalization + PublishGate canonicalization + Lifecycle transition ownership + Rigby PA-tool centralization.
3. **§14.4 T1 R.SPORTS.POSTURE + T1 R.DBAO.CODENAME** — integration vs island; materialize / demote / archive DBAO.
4. **§14.8 R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.OBSERVABILITY.D74-SPINE-POSTURE** — paired T0/Gate; blocks 9 T1 items.
5. **§14.3 Revenue T1–T8 ADR bundle** — parallel-schema + outreach delivery + HAI interlock + write-authority + state-machine completion.
6. **§14.9 D80 4-option HumanAttention posture** — F7 CRITICAL constraint framing.

Sequences L1, L2, L4 in §3 explicitly avoid depending on any of these six. That's the point — they are the leverage moves that produce value without waiting for constitutional ADRs.

---

## 6. Appendix — evidence trail for verified-at-HEAD claims

Rows carry `Verified=Y` where independent grep at HEAD 56df8159 (2026-07-09) confirmed the claim. The specific evidence:

| Row | HEAD verification | Anchor |
|---|---|---|
| §2.1 Employee OS Integrated=P (no WS on verdict) | Grep 2026-07-09: all `emit_mission_verdict` references are in `mission_runner.py`, `mission_verdict.py`, `td_handlers_employee.py`, `jobs/bug_triage.py`, and tests. Zero WS/channel_layer references. | `core/employees/mission_runner.py:1530-1570` |
| §2.2 Body Systems Integrated=P (HeartBeat readers exist — HAI producer missing) | Grep 2026-07-09: 6 HeartBeat readers at HEAD (`services/heart.py:705`, `views_heart.py:78`, `tasks.py:5655`, `agents/content_writer_agent.py:544`, `td_handlers_ops.py:3883,4982,5008`); `services/heart.py:690` calls `discord.send_system_alert()` on degradation — not HAI. | `core/services/heart.py:690-707` |
| §2.3 Deliverables Integrated=P (query-side readers exist; no post_save receiver) | Grep 2026-07-09 + Rigby verification pa-d80d3164add848dd: `sender=DeliverableEvent` = 0 receivers; `DeliverableEvent.objects.*` = 8+ non-test files (`ops_autopilot/impact.py`, `diagnostics/coo_daily.py`, `td_handlers_gateway.py`, `views_deliverables.py`, `employees/status.py`, etc.). **Audit §3.2 "zero consumer" claim STALE at HEAD.** | Rigby SIGN pa-d80d3164add848dd |
| §2.6 Authentication `enforce_authority_mode` ABSENT | Grep 2026-07-09: zero `.py` matches; only docs / handoffs mention the name. | Rigby SIGN pa-d80d3164add848dd |
| §2.6 Governance zero-enforcement-dispatch KillSwitch consumers | Grep 2026-07-09: `KillSwitch.objects.*` returns 6 lines total in 2 files (`ops_autopilot/governance.py` and `intelligence.py`). `governance.py:2192` reads active kill switches to populate a status dict (returned by `get_governance_status()`); other reads are cleanup of expired switches. Zero enforcement dispatch. | `core/services/ops_autopilot/governance.py:2192` |
| §2.6 Event Bus 3-of-8 streams have callers at HEAD | Grep 2026-07-09: `publish_opportunity_scored_event` caller confirmed at `scoring_dispatcher.py:21-40,282,480`; `publish_validation_required_event` + `publish_validation_decided_event` callers at `hitl_validation.py`; SPIDER_DATA + OUTCOME_RECORDED + SYSTEM_ALERT + MODEL_TRAINED zero non-definition callers. **Adoption improved from S1274 v2 baseline (1-of-8) but 5 streams still lack publishers.** | Rigby SIGN pa-d80d3164add848dd + Claude grep 2026-07-09 |

---

**End of draft. Status: research / draft — S2734 Claude authorship;
Rigby SIGN dispatched via fresh pin pa-d80d3164add848dd (5 claims
verified, 1 correction folded to §2.3 Deliverables row). Chris
ratification pending. No implementation begun. §14 refresh of
cross_domain_integration_audit.md not yet appended for this
campaign-output artifact (owed to a follow-up close doc, not this
draft).**
