---
title: "Group 2600 PA Domain Taxonomy Proposal (Phase 0)"
status: active
authority: research
version: v1
session_id: 2600
date_opened: 2026-07-06
date_ratified: 2026-07-06
arc: Research Group 2600 (PA — Cross-Arc Handoff Bundle Consuming CF-2600-PA + CF-D6 + F-B-HIGH-3 + Workspace-Context Authz + REST↔WS T7 Joint Dual-Owner)
domain_slug: pa
research_group: 2600
child_slot: parent
head_sha: 76342fd5 (post-S2599 merge)
companion_anchors:
  - docs/CLAUDE.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/PLATFORM_INVENTORY.md
  - docs/topics/personal-assistant.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md
related:
  - docs/research/domains/api/2599_api_canonical_summary.md   # DIRECT PREDECESSOR (Group 2500 API xx99 close)
  - docs/research/domains/api/2500_api_domain_scoping.md      # PARENT-SCOPING TEMPLATE MODEL
  - docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md  # CF-2600-PA ORIGIN (Cat A)
  - docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md  # CF-D6 ORIGIN (Cat D)
  - docs/research/domains/auth/2499_auth_canonical_summary.md  # PRIOR-PRIOR ARC CLOSE MODEL
  - docs/research/domains/auth/2402_auth_permission_floor_uniformity_audit.md  # F-B-HIGH-3 ORIGIN
verifier_loop: |
  v1 (2026-07-06, S2600 arc-open):
  Drafted after S2599 xx99 close under fully-installed Research OS.
  Group 2500 API arc CLOSED at S2599 xx99 (2026-07-06) with canonical
  verdict: "MECHANISM working at file-precision + DECLARATION SoT
  absent or non-uniform across all four contract axes; majority
  IMPLICIT-INHERITANCE with ISLAND-DECLARATION pockets and ZERO
  cross-transport SoT; gap is design-plane governance, not runtime
  failure." T3 Group 2600 PA queued in S2599 §8.2 T-slot queue,
  consuming 4 CF-* handed forward from S2501-S2504.

  This parent scoping doc drafted per playbook §11.1 template
  (SEVENTH-consecutive parent-with-children arc under Research OS;
  Groups 1900 + 2000+ + 2100 + 2200 + 2400 + 2500 six prior). Q1-Q4
  shape card written 2026-07-06 turn 2; routed to Rigby SIGN-preview
  via arc pin pa-c17a8d7e0660413b turn 3; SIGN-preview verdict MEDIUM
  confidence with 9 folds; Chris "agree all" 2026-07-06 ratified all
  9 folds wholesale. Folds baked into §3 taxonomy (F1 Cat B hard
  boundary + F2 Cat C 2-subtrack split), §5 central lens (F3 binary +
  layer-choice rewrite), §5.3 acceptance criteria (F4 measurability +
  F5 F-B-HIGH-3 closure + F6 dial-back), §7 anti-scope (F7 +2 items),
  §3 Cat A framing (F8 minimum-island-declaration baseline), §2.5
  evidence gaps (F9 U6/U7 explicit labeling).

  Rigby SIGN cycle 1 pending on full parent scoping doc via dedicated
  fresh SIGN isolation pin per playbook §15 (TWENTY-THIRD consecutive
  dedicated fresh SIGN pin candidate at close after S1399/S1499/
  S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/
  S2403/S2404/S2499/S2500/S2501/S2502/S2503/S2504/S2599 twenty-two
  prior).

  Status remains draft until Chris ratifies at SIGN cycle 1 close.
owner: claude (drafted S2600 v1 with 9 pre-drafting shape-card folds; Rigby SIGN cycle 1 pending)
---

# Group 2600 PA Domain Taxonomy Proposal (Phase 0)

> **Positioning.** T3 arc per S2599 §8.2 T-slot queue. Direct successor to Group 2500 API (closed S2599 xx99 2026-07-06). Consumes 4 CF-* originated in S2501-S2504 (CF-2600-PA + CF-D6 + F-B-HIGH-3 preserved + PA endpoint DECLARATION side). PARENT-WITH-4-CHILDREN candidate (SEVENTH-consecutive extension of MC-4 pattern).
>
> **Positioning boundary.** Group 2600 PA owns the **contract-shape** of the PA subsystem's API surface (REST endpoints + WS channels + workspace-context authorization at the boundary). Group 2600 does NOT own PA behavior mutations (prompt engineering / model selection / context reasoning) or PA-adjacent subsystem redesign (memory persistence / agent registry). See §7 anti-scope for the ten explicit walls.

---

## 1. Why Phase 0

Phase 0 pressure-tests the subdomain taxonomy for completeness across the four coordination flags handed forward from Group 2400 Auth + Group 2500 API + the outstanding S2402 F-B-HIGH-3 workspace-membership evidence. Without Phase 0:

1. **Scope-magnet risk.** "PA" as a domain is diffuse — it can attract prompt-engineering, memory-persistence, agent-registry, provider-routing, and voice-generation scope creep, none of which are contract-shape work. Phase 0 fixes the wall.
2. **Handoff-bundle risk.** CF-D6 declared REST↔WS T7 joint DUAL-OWNED by Group 2500 + Group 2600. Without an explicit ownership boundary at Phase 0, the dual-owner arrangement collapses into either duplicate audit or coverage gap.
3. **Decision-orthogonality risk.** S2504 §88 established the discipline that decision-spaces stay orthogonal unless explicit coupling evidence surfaces. Group 2600 has at least three orthogonal Chris-D-verdict axes (PA endpoint SoT declaration + workspace authz declaration + REST↔WS T7 strictness); conflating them at parent-level would forfeit the discipline the arc inherits.
4. **MC-4 pattern extension.** Groups 1900 + 2000+ + 2100 + 2200 + 2400 + 2500 have delivered SIX-consecutive parent-with-4-children arcs under the Research OS. Group 2600 is the seventh candidate; Phase 0 verifies the 4-child arithmetic applies here (see §4).
5. **Evidence-gap discipline.** U6 (WS envelope-schema type) + U7 (paStore field-list completeness) from S2599 §6 are EVIDENCE GAPS, not decision inputs. Phase 0 labels them as such so no downstream decision anchors on unverified assumptions (per F9 fold Chris-ratified 2026-07-06).

Runtime target: **6 sessions** (parent + 4 children + xx99 close). Runtime cap: **8 sessions** if Cat A endpoint contract-SoT decomposition requires split — see §4.3.

---

## 2. What existing inventory already tells us

### 2.1 PA subsystem runtime shape at HEAD (76342fd5)

Baseline extracted from PLATFORM_INVENTORY.md HEAD `e617af59` and CLAUDE.md canonical entry-point declaration:

| Dimension | Value | Source |
|---|---|---|
| PA canonical REST entry point | `POST /api/pa/chat/` | CLAUDE.md — "Canonical PA route: `POST /api/pa/chat/`" |
| PA compat REST entry points | `/api/assistant/chat/` + `/api/v1/assistant/chat/` | CLAUDE.md — "compatibility-only" |
| PA-path endpoints sampled by Cat A | 10 (chat + status + context + preferences + voice + learning + attention + 3 compat) | 2501_api_backend_contract_sot_design_prep_audit.md:600-613 |
| PA-path @extend_schema decorators at HEAD | **0** (of 10 sampled) | 2501_api_backend_contract_sot_design_prep_audit.md:615-619 |
| PA-path @permission_classes DEFAULT | `[IsAuthenticated]` | core/views_personal_assistant.py:31-32 |
| PA-path serializers | NONE (hand-constructed dict responses) | 2501 §3.PA-path evidence |
| PA agentic loop entry | `UnifiedPAEntrypoint.process_message` | CLAUDE.md + core/services/unified_pa_entrypoint.py |
| PA tool schemas registered | 113 | PLATFORM_INVENTORY.md — "PA Tools" |
| PA tool handlers registered | 156 | PLATFORM_INVENTORY.md — "PA Tools" |
| PA enrichment services | 8 | PLATFORM_INVENTORY.md — "PA Tools" |
| WORKSPACE_AWARE_AGENTS constant | 20 agents | core/epa_handlers_tools.py:191-217 |
| PA async task queue | dedicated `pa` Celery queue | CLAUDE.md + PLATFORM_INVENTORY.md |
| PA WS channels (PA-related subset of platform 120) | UNKNOWN at HEAD — inventory in Cat D opening | Evidence gap (see §2.5) |

### 2.2 Contract-SoT status inherited from Group 2500 API xx99 verdict

S2599 canonical verdict states: *"MECHANISM working at file-precision + DECLARATION SoT absent or non-uniform across all four contract axes (backend schema + consumer typing + error envelope + permission-floor + WS message contract); majority IMPLICIT-INHERITANCE with ISLAND-DECLARATION pockets and ZERO cross-transport SoT; gap is design-plane governance, not runtime failure."* (2599_api_canonical_summary.md:39)

Group 2600 PA inherits this as **upstream constraint**, not re-litigation:
- PA endpoints inhabit the 1,857-of-1,864 undecorated denominator (2501 §3 evidence). No PA-specific @extend_schema mitigates this at HEAD.
- The 4-shape 401 heterogeneity (Family A/B/C/D per Cat C S2503 canonical taxonomy) applies at PA endpoints since PA reuses DRF permission dispatch (Family A `{"detail": ...}` shape) but ALSO uses hand-constructed `{"success": True, "data": {...}}` envelope shape on 200 responses (2501 §3 evidence — not a 401 case but relevant to Cat B PA-client contract typing).
- The 803-scale consumer call-site pattern applies to PA-related consumers (assistantApi + paStore + `pa_chat.py` CLI wrapper), which are candidates for typed-island exemplar per S2599 AU-1 cockpitApi.ts 96%-typed precedent.

### 2.3 Coordination flags handed forward (4 CF-* + 1 F- preserved)

| CF-* | Origin | Handoff evidence | Ownership at Group 2600 |
|---|---|---|---|
| **CF-2600-PA** | S2501 Cat A (Backend Contract SoT design-prep) | `/api/pa/chat/` + `/api/assistant/*` endpoints declare 0 @extend_schema at HEAD; workspace-context authz declared implicitly via `permission_classes = [IsAuthenticated]` at `core/views_personal_assistant.py:32` | **SOLE OWNER — Cat A (S2601)** |
| **CF-D6** | S2504 Cat D (Permission-Floor Registry + REST↔WS T7 Joint) | REST↔WS T7 joint contract SoT DUAL-OWNED Group 2500 API + Group 2600 PA; 120 WS routes + 87 Consumer classes + 0% envelope conformance at HEAD; Secondary stakeholders: Group 1700 Observability + Group 2300 Mobile | **DUAL OWNER — Cat D (S2604)** (Group 2500 side owned by S2504 arc-close design-prep; Group 2600 side owned by S2604 PA-slice application) |
| **F-B-HIGH-3** | S2402 (Auth Permission-Floor Uniformity) → preserved through S2504 | Workspace-membership enforced INSIDE `execute_with_workspace()` method only; NO HTTP/DRF permission-class layer check declares workspace requirement; WORKSPACE_AWARE_AGENTS dispatcher at `core/epa_handlers_tools.py:341` routes to `execute_with_workspace()` where the membership check lives | **SOLE OWNER — Cat C sub-track C1 (S2603)** |
| **CF-C2** (partial) | S2503 Cat C (Error/Refresh/Logout Contracts) | session_tool.retire policy on user logout coupled to α/β/γ verdict — PA conversation retention window is the PA-specific slice | **SOLE OWNER — Cat C sub-track C2 (S2603)** |

### 2.4 Prior-arc contextual signals

- **S2400 Auth arc** (closed S2499) established F-B-HIGH-3 workspace-membership implicit-gate as high-severity finding; NOT closed at S2499 because the enforcement decision was ADR-scope rather than Group 2400 mechanism scope.
- **S2500 API arc** (closed S2599) added S2504 §14 evidence explicitly listing PA workspace-context handoff to Group 2600 (2504 §14 lines 804-806).
- **S1300 Memory arc** owns MEMORY.md auto-memory governance; PA memory persistence is out of scope here (see §7 anti-scope #3).

### 2.5 Evidence gaps requiring confirmation at Cat B S2602 opening (F9 fold)

Per Chris-ratified F9 fold 2026-07-06, U6 + U7 from S2599 §6 are **evidence gaps**, not decision inputs. Both require inventory confirmation at Cat B S2602 opening turn 1 before any Cat B verdict-space is enumerated:

- **U6 (WS envelope-schema type UNKNOWN):** Cat B S2602 must inventory PA-related WS channels (subset of platform 120) + sample envelope shape on chat-response streaming + task-status broadcast + async-audio-url delivery. Decision-space (TypedDict / Protocol / BaseModel) cannot be enumerated pre-inventory.
- **U7 (paStore field-list completeness UNKNOWN):** Cat B S2602 must dump paStore full field list (currently observed: 3-of-9 syncUser fields wiped at logout per S2503 CF-C3; remaining 6 fields intent-preserved OR cleanup-debt UNKNOWN). Decision-space (retain vs cleanup vs typed-declaration) cannot be enumerated pre-inventory.

**No Cat B option enumeration until inventory confirms U6/U7** (F10a fold — SIGN cycle 1 Q2 explicit guardrail per Rigby 2026-07-06). If Cat B opening reveals materially different shape than expected, parent scoping §3.B revises.

### 2.6 Central lens question (Q2 shape card + F3 + F10 folds applied — two-lens split)

Per Chris-ratified F10 fold 2026-07-06 (SIGN cycle 1 Q2), the central lens splits into two labeled sub-lenses to prevent overload. §2.6.A is a hard constraint inherited from Group 2500 verdict; §2.6.B is the Group 2600 delta-decision question.

**2.6.A — Baseline inheritance constraint (hard):**

> *"PA inherits the Group 2500 API-layer verdict — 'IMPLICIT-INHERITANCE with ISLAND-DECLARATION pockets and ZERO cross-transport SoT' (S2599 canonical verdict 2026-07-06) — unless explicitly overridden with justification + compensating controls."*

This is not a decision-space; it is a constraint. Group 2600 does not re-litigate Group 2500 verdict; Group 2600 works within it or overrides it explicitly with rationale trace.

**2.6.B — Group 2600 PA delta-decision question:**

> *"Given /api/pa/chat/ is the CLAUDE.md canonical operator entry point, does PA warrant **stricter contract declaration** than the Group 2500 baseline — and if so, at which boundary layer: (i) REST OpenAPI spec (drf-spectacular decorator retrofit), (ii) WS envelope schema (TypedDict / Protocol / BaseModel), (iii) permission-class gate (WorkspaceMember DRF class or middleware path-list), or (iv) handler-internal contract (documented compensating controls per F5)?"*

**Delta axes.** The four delta-decision candidates are ORTHOGONAL unless coupling evidence surfaces per S2504 §88 discipline. Each Cat A / Cat B / Cat C / Cat D verdict resolves ONE axis; xx99 close ratifies the combined delta.

**Evidence-gap gating (F9+F10a):** No Group 2600 delta decision anchors on U6 (WS envelope-schema type) or U7 (paStore field-list completeness) pre-verification. Cat B S2602 opening turn 1 closes both evidence gaps before Cat B (and by extension Cat D's WS envelope Path A choice) enumerates option space.

---

## 3. Candidate subdomain taxonomy

### A — P1 Cat A (S2601): PA endpoint contract SoT declaration design-prep

**Mission.** Declare the disposition of PA-path REST endpoints on the contract SoT axis. Answer: does each PA endpoint retrofit @extend_schema + typed serializer + APIResponseEnvelope conformance (Path A), declare typed shape via APIResponseEnvelope only without @extend_schema (Path B), or defer to Group 2500 platform-wide retrofit with documented minimum-island-declaration on `/api/pa/chat/` as CLAUDE.md canonical operator entry point (Path C+island)?

**Scope.** Ten PA-path endpoints minimum (extendable during Cat A opening):
- `POST /api/pa/chat/` — CLAUDE.md canonical entry; `core/views_personal_assistant.py:33-99`
- `GET /api/pa/chat/status/<str:task_id>/` — async result polling
- `GET /api/pa/context/` — assistant context extraction
- `POST /api/assistant/chat/` (compat) — routes through `assistant_chat_bypass`
- `GET /api/assistant/context/` — compat context read
- `GET /api/assistant/preferences/` — user preferences fetch
- `POST /api/assistant/voice/` — voice-to-assistant transcription entry
- `GET /api/assistant/learning/` — learning summary
- `POST /api/assistant/attention/unified/` — unified attention read
- `GET /api/v1/assistant/context/` (compat) — v1 compatibility route

**Chris-D-verdict axes.**
- **Path A** — drf-spectacular decorator retrofit on all PA-path endpoints (target ≥90% coverage per AC#1 measurability threshold — F4 fold).
- **Path B** — typed serializer + APIResponseEnvelope conformance only; no @extend_schema declaration.
- **Path C+island (F8 baseline)** — defer to Group 2500 platform-wide retrofit BUT declare **minimum PA-island declaration** on `/api/pa/chat/` (CLAUDE.md canonical entry) — at least documented OpenAPI operationId + request/response schema — even if broader PA-path defers. Path C without island-minimum requires explicit Chris-D-verdict override at S2699 xx99 close.

**Findings inheritance.**
- S2501 §3 PA-path evidence (0/10 @extend_schema; hand-constructed dict responses; DRF DEFAULT `[IsAuthenticated]` permission dispatch).
- S2599 §5.3 401 shape-family taxonomy Family A/B/C/D — applicable to PA endpoint 401 shape (Family A DRF `{"detail"}` observed for `/api/pa/chat/` unauthenticated).

**Cross-arc coordination.**
- Group 2500 platform-wide retrofit disposition (Path A/B/C selection at Cat A S2501 verdict) is upstream input; PA cannot ratify Path A if Group 2500 Path C-defer applies platform-wide.
- Group 2400 Auth Cat A trust-boundary decisions preserved (no PA-specific fleet-signature or token-rotation policy re-litigation).

**Blast radius baseline.** 10-endpoint minimum PA-path slice. Estimated 15-20 endpoints total after Cat A opening inventory (includes Discord bot @app_commands wrappers if they proxy through `/api/pa/*` — see §7 anti-scope #5 for Discord walling).

**F8 baseline codification.** Cat A opening turn 1 MUST inventory whether `/api/pa/chat/` already has any documented OpenAPI operationId or schema declaration outside `@extend_schema` (e.g., docstring-based introspection, external OpenAPI YAML). If NONE exists, Path C-pure is the strictly-worse option relative to Path C+island.

### B — P2 Cat B (S2602): PA-client contract surface design-prep

**Mission.** Enumerate the PA-client consumer contract surface and its typed-vs-SHAPE-BLIND disposition. Declare whether typed assistantApi.ts island is warranted (analog to cockpitApi.ts 96%-typed exemplar per S2502) and resolve paStore field-list completeness (U7).

**Scope (F1 hard boundary fold).** Cat B scope is **contract typing + field-list completeness ONLY**. Three consumer surfaces:
- `frontend/src/lib/api.ts` — assistantApi module (subset of 93 apiModule / 4,194 LOC file per S2202)
- `frontend/src/stores/paStore.ts` (or equivalent) — paStore field list resolution
- `tools/pa_chat.py` — CLI wrapper 3-way chat message envelope contract

**Explicit exclusions per F1 fold.**
- NO UI/UX behavior changes (message rendering, tool-run display, streaming UX).
- NO state management refactors (Zustand slice consolidation, useEffect discipline).
- NO frontend build/bundling changes.
- NO frontend testing framework decisions.

**Chris-D-verdict axes.**
- **(a)** Typed assistantApi.ts island — treat PA-client surface as typed exemplar (analog to cockpitApi.ts 96%-typed island); typed interfaces published for chat request/response + task-status + context + preferences.
- **(b)** SHAPE-BLIND flow-through preserved — PA-client surface stays untyped consistent with 7.36% platform-wide typed rate per S2502 baseline; no Group 2600 typing pass.
- **(c)** Hybrid — typed for PA-response envelope shape (success/error boundary) but SHAPE-BLIND for message payload (streaming tokens + tool-run objects + audio_url).

**Findings inheritance.**
- S2502 §Cat B typed rate 63/856 = 7.36% platform baseline + cockpitApi.ts 96%-typed island exemplar.
- S2504 §Cat D SHAPE-BLIND interceptor pattern applicable to PA-client 401 handling.

**Cross-arc coordination.**
- Group 2500 Cat B S2502 verdict on 18 DEAD-CANDIDATE apiModules cleanup — if PA modules included in DEAD-CANDIDATE list, Cat B S2602 handles cleanup verdict independently (or defers).

**Blast radius baseline.** assistantApi module estimated 5-15 apiModule entries within api.ts + paStore field list ~9 fields (per S2503 CF-C3 partial evidence) + pa_chat.py CLI wrapper ~5-8 message-shape fields.

**Evidence gap opening turn 1 (F9).** Inventory paStore full field list + PA-related WS channel envelope sample BEFORE decision-space enumeration.

### C — P3 Cat C (S2603): PA workspace-context authz + session lifecycle (2 sub-tracks per F2 fold)

Per Chris-ratified F2 fold 2026-07-06, Cat C splits into **two parallel decision tables** with independent verdict rows:

#### C1 — Workspace-context authz declaration policy

**Mission.** Close F-B-HIGH-3 workspace-membership implicit-gate. Declare where workspace-context authorization is enforced (HTTP permission-class layer / middleware path-list gate / handler-internal implicit) and ratify F-B-HIGH-3 closure condition per F5 fold.

**Scope.**
- WORKSPACE_AWARE_AGENTS at `core/epa_handlers_tools.py:191-217` (20 agents).
- `execute_with_workspace()` internal membership check (referenced at S2504 §Cat D line 341).
- PA-path endpoints that read/write workspace-scoped data (`/api/pa/chat/` message dispatch, `/api/pa/context/` workspace-scoped context).

**Chris-D-verdict axes (F5 closure-condition fold).**
- **Path A** — Retrofit `WorkspaceMember` DRF permission class at PA endpoints; membership enforced pre-handler at HTTP layer.
- **Path B** — Declare workspace requirement at middleware path-list gate layer (analog to S2504 §Cat D 285-entry path-list gate mechanism).
- **Path C+compensating (F5 fold)** — Handler-internal implicit-gate PRESERVED with documented compensating controls: (i) audit-log hook fires per workspace-scoped dispatch; (ii) explicit ADR documents policy; (iii) `docs/topics/pa.md` declares workspace-enforcement location for discoverability. **Path C-pure (implicit-gate remains WITHOUT compensating controls) is NOT a valid ratification — F5 fold blocks paper-victory.**

**Findings inheritance.**
- S2402 F-B-HIGH-3 workspace-membership implicit gate.
- S2504 §14 evidence of implicit-only declaration at HTTP + DRF permission-class layer.

**Cross-arc coordination.**
- Group 2500 Cat D §Cat D (a)/(b)/(c) permission-floor decision-space — Group 2600 Cat C1 is a Path A/B/C selection ORTHOGONAL to Group 2500 Cat D unless coupling evidence surfaces per S2504 §88 orthogonality discipline.

**Blast radius baseline.** 20 WORKSPACE_AWARE_AGENTS + at least 3 PA-path endpoints touching workspace-scoped data. Compensating-controls scope (Path C+compensating) = 1 audit-log hook + 1 ADR + 1 documentation section.

#### C2 — PA session-lifecycle policy

**Mission.** Declare PA-specific session-lifecycle policy: `session_tool.retire` disposition on user logout + PA conversation retention window. Couple to Group 2400 Cat C α/β/γ verdict OR declare PA-specific override.

**Scope.**
- `session_tool.retire` behavior on PA conversation pin closure (verified working per S1301 memory rule `feedback_session_tool_retire_works.md`).
- PA conversation retention window (arc-pin lifecycle vs user-session lifecycle vs storage-key TTL).
- CF-C2 handoff scope — Group 2400 Cat C α/β/γ session-lifecycle verdict applied to PA slice.

**Chris-D-verdict axes.**
- **α** — Adopt Group 2400 Cat C α session-lifecycle verdict (short-lifetime bearer + short retention window) unchanged at PA layer.
- **β** — Adopt Group 2400 Cat C β verdict (refresh-token + medium retention) unchanged at PA layer.
- **γ** — Adopt Group 2400 Cat C γ verdict (long-lifetime session + long retention) unchanged at PA layer.
- **PA-override** — Declare PA-specific override (e.g., arc-pin lifetime decoupled from user session per playbook §16 arc-standard behavior). Requires explicit Chris-D-verdict + rationale trace at S2699 xx99 close.

**Findings inheritance.**
- S2503 CF-C2 lifecycle handoff.
- S1301 `feedback_session_tool_retire_works.md` memory rule (retire action verified working — no rebuild).
- MEMORY.md `feedback_no_parallel_research_arcs.md` (arc-pin discipline).

**Cross-arc coordination.**
- Group 2400 Cat C α/β/γ verdict is upstream input; Cat C2 cannot ratify PA-override without stating the departure from Group 2400 verdict.

**Blast radius baseline.** 1 session_tool action verdict + 1 retention-window policy + PA arc-pin lifecycle stanza in `docs/topics/pa.md`.

### D — P4 Cat D (S2604): PA REST↔WS T7 joint contract SoT (dual-owner PA side)

**Mission.** Ratify PA WS message-contract strictness at the REST↔WS T7 joint. Group 2600 side of CF-D6 dual-owner arrangement (Group 2500 side owned by S2504 arc-close design-prep). Apply Group 2500 Cat D γ mechanism-nesting decision at PA layer.

**Scope.** PA-related WS channels (subset of platform 120 total per S2504 baseline):
- Chat-response streaming (token-by-token delivery from PA agent loop).
- Task-status broadcast (async PA task completion + tool-run updates).
- Async-audio-url delivery (voice-response TTS URL push).
- Any PA-related consumer classes among the 87 platform total (Cat D S2604 opening inventory).

**Chris-D-verdict axes.**
- **Path A** — Typed WS envelope schema at all PA-related consumers (TypedDict / Protocol / BaseModel — U6 evidence-gap resolution required first at Cat B opening).
- **Path B** — Envelope declared at CONNECT handshake only; message-shape SoT-declared but non-enforced (island-declaration on connect, SHAPE-BLIND on message payload).
- **Path C** — WS message-contract SoT-declared for all PA-related channels; streaming exception carve-out for chat-response (streaming tokens explicitly non-conformant + documented).

**Findings inheritance.**
- S2504 CF-D6 REST↔WS T7 joint framing.
- S2504 §Cat D γ mechanism decision (typed-error envelope α/β/γ γ = mechanism nesting).
- S2599 §3 4-plane consolidated shape — permission-floor + REST↔WS plane.

**Cross-arc coordination.**
- Group 2500 Cat D S2504 verdict on Path A/B/C REST↔WS strictness is upstream input.
- Group 1700 Observability (secondary stakeholder) — envelope-shape telemetry + per-endpoint compliance metrics inherit from Cat D verdict.
- Group 2300 Mobile (parallel arc, secondary stakeholder) — client interception at mobile PA client inherits from Cat D verdict.

**Blast radius baseline.** PA-related WS channels estimated 5-10 (subset of 120 total). Consumer classes touching PA data estimated 3-7 (subset of 87 total). Consumer-class conformance at HEAD: 0% (part of the 0/40 envelope conformance figure per S2504 baseline).

### Explicit non-candidates

The following adjacent-domain surfaces are OUT-OF-SCOPE at Group 2600 parent (delegated to other arcs or ADRs):

- **PA behavior mutations** — Prompt engineering, model routing (OpenAI vs Anthropic vs Together vs Ollama vs DeepSeek vs Gemini per PLATFORM_INVENTORY.md 6 providers), context reasoning depth, tool selection logic. Scope = PA subsystem docs (`docs/topics/personal-assistant.md`) + service-layer refactors elsewhere.
- **PA memory persistence (auto-memory MEMORY.md governance)** — Group 1300 Memory arc scope.
- **PA agent-registry mutations** — WORKSPACE_AWARE_AGENTS list content changes (adding/removing agents from workspace-aware dispatcher) = agent-system scope. Group 2600 declares enforcement policy at API layer; list membership is separate.
- **Discord bot PA surface** — 48 slash + 48 prefix commands in `discord_bot.py` (per PLATFORM_INVENTORY.md 96 total @*.command decorators). Adjacent domain; Group 1900 Advisor + Discord scope. If Discord commands proxy through `/api/pa/*` endpoints, the endpoint disposition is Group 2600 Cat A scope but the Discord-side handler is not.
- **Fleet HMAC PA signature (cross-repo mentorforge/character-os PA federation)** — Group 2400 Cat A preserved.
- **PA token / auth token rotation policy** — PA_API_TOKEN + TEST_AUTH_TOKEN handling belongs to Group 2400 Auth scope.

### §3.5 PA-adjacent probes disposition (F6 dial-back applied)

Per Chris-ratified F6 fold 2026-07-06, PA-adjacent probes REDUCED to 3 contract-shaping probes only:

| Probe | Disposition | Cat | Rationale |
|---|---|---|---|
| `/pa/chat/` streaming semantics | IN-SCOPE | Cat A + Cat D | Chunked-transfer / SSE / WS-only decision shapes REST↔WS T7 verdict + informs Cat A schema declaration (streaming vs non-streaming response type differs). |
| Task-status polling contract at `/pa/chat/status/<id>/` | IN-SCOPE | Cat A | Polling shape (2xx response body vs 202 Accepted vs long-poll vs WS push) is a contract-declaration axis. |
| WS channel authentication handshake | IN-SCOPE | Cat D | TokenAuthMiddlewareStack behavior at PA-related WS channels — per S2504 §Cat D 285-entry path-list gate parallel. |
| **DROPPED (F6 fold):** Rate-limiting per `/pa/chat/` | NON-CANDIDATE | — | Operational policy adjacent to Group 1700 Observability + Group 2400 Auth governance. Not currently a known defect. Would swamp contract-SoT scope. |
| **DROPPED (§7 anti-scope):** LLM provider routing at PA layer | NON-CANDIDATE | — | Behavior scope; anti-scope #9 per F7 fold. |

---

## 4. Parent-vs-single recommendation

### 4.1 Recommendation

**PARENT-WITH-4-CHILDREN**, matching S2400 Auth (Groups 2401-2404 + xx99) and S2500 API (Groups 2501-2504 + xx99) precedents.

### 4.2 Arithmetic verification (prior 4-child arcs — 6 consecutive)

| Arc | Group | Children | Runtime target | Runtime actual | Outcome |
|---|---|---|---|---|---|
| S1900 | Attention | 4 (S1901-S1904) | 6 sessions | 6 (100%) | MC-4 CODIFICATION-CONFIRMED |
| S2000+ | Sports | 4 (S2001-S2004) | 6 sessions | 6 (100%) | MC-4 CODIFICATION extended |
| S2100 | Governance | 4 (S2101-S2104) | 6 sessions | 6 (100%) | MC-4 CODIFICATION extended |
| S2200 | Frontend | 4 (S2201-S2204) | 6 sessions | 6 (100%) | MC-4 CODIFICATION extended |
| S2400 | Auth | 4 (S2401-S2404) | 6 sessions | 6 (100%) | MC-4 CODIFICATION extended |
| S2500 | API | 4 (S2501-S2504) | 6 sessions | 6 (100%) | MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails extended |
| **S2600 (this)** | **PA** | **4 (S2601-S2604)** | **6 sessions** | (TBD) | **SEVENTH-consecutive candidate** |

Runtime cap: 8 sessions if Cat A endpoint contract-SoT decomposition splits mid-arc (e.g., separate PA-canonical `/api/pa/chat/` island decision from broader PA-path defer decision) — see §4.3.

### 4.3 Rationale — Options considered

**Option A (2-child): REJECTED.** Cat A (endpoint SoT) + Cat B/C/D bundled. Rejected because bundling C (workspace authz + session lifecycle) with B (client contract) or D (WS T7) conflates decision-orthogonal axes (per S2504 §88 discipline: authz enforcement vs client typing vs WS strictness are independent decisions unless coupling evidence surfaces).

**Option B (3-child): REJECTED.** Cat A + Cat B/C bundled + Cat D. Rejected because C1 (workspace authz F-B-HIGH-3) and C2 (session lifecycle CF-C2) are distinct maturity gradients that F2 fold explicitly separates as parallel sub-tracks — bundling them with Cat B loses that discipline.

**Option C (4-child): RECOMMENDED — this proposal.** A + B + C (with 2 parallel sub-tracks internally) + D. Cat C internal split into C1/C2 preserves 4-child arithmetic (six-consecutive MC-4 pattern) while honoring F2 fold requirement. C1 and C2 are folded INSIDE Cat C rather than being separate arc children — Cat C S2603 delivers two parallel decision tables in one audit.

**Option D (5-child, C-split externally): REJECTED.** Would split C1 and C2 into separate children (S2603 authz + S2604 session-lifecycle + shifting Cat D to S2605). Rejected because (i) breaks MC-4 arithmetic (would establish MC-5 without precedent), (ii) C1 and C2 have shared evidence base and can be audited in a single session with two output tables, (iii) 5-child arcs risk exceeding runtime cap.

### 4.4 Runtime target vs cap

Runtime target: **6 sessions** — parent (S2600) + 4 children (S2601-S2604) + xx99 close (S2699).

Runtime cap: **8 sessions** — trigger conditions:
1. Cat A opening inventory reveals >20 PA-path endpoints requiring individual Path A/B/C+island disposition — split Cat A into S2601a (canonical `/api/pa/chat/` + F8 island-minimum decision) + S2601b (broader PA-path Path C-defer verdict).
2. Cat D opening reveals >10 PA-related WS channels with distinct envelope-shape variations — split Cat D into S2604a (chat-response streaming exception) + S2604b (task-status + async-audio-url).

Cap trigger reported at Cat A/D opening turn 1 with explicit rationale + Rigby SIGN pre-approval before mid-arc split.

---

## 5. Child mission sequence (Chris-locked pending SIGN cycle 1 close)

Sequence: **S2601 → S2602 → S2603 → S2604 → S2699 xx99**

Ordering rationale (decision-order strict; evidence-collection parallel permitted per F13 SIGN cycle 1 fold):

- **S2601 (Cat A) precedes S2602 (Cat B)** — PA endpoint contract-SoT disposition is upstream input for PA-client typed-shape decision. If Cat A ratifies Path C+island (defer with minimum-island), Cat B typed-island exemplar decision inherits a different baseline than if Cat A ratifies Path A (full retrofit).
- **S2602 (Cat B) precedes S2603 (Cat C)** — paStore field-list resolution (Cat B U7 evidence gap closure) is upstream input for C2 session-lifecycle retention window (which paStore fields wipe on retire vs persist across sessions).
- **S2603 (Cat C) precedes S2604 (Cat D)** — Workspace-context authz declaration (C1) is upstream input for Cat D WS channel authentication handshake (Path A permission-class retrofit for HTTP layer sets precedent for WS-layer parallel decision per S2504 285-entry path-list gate mechanism).
- **S2604 (Cat D) terminal before xx99** — REST↔WS T7 joint dual-owner Group 2600 side depends on all upstream Cat A/B/C verdicts.

**F13 SIGN cycle 1 fold — parallel evidence-collection permitted (option enumeration remains sequential):** Evidence-collection for Cat B (U6 WS envelope sample + U7 paStore field-list dump) and Cat D (PA-related WS channel inventory + Consumer class inventory) MAY begin in parallel with Cat A opening turn 1, provided:
- No Cat B or Cat D option-space enumeration begins until Cat A verdict lands (decision-order strict).
- Evidence-collection reports are inventory-only artifacts (endpoint / channel / field lists), not analysis or verdict-space enumeration.
- Rigby SIGN cycle 1 per-child pin remains dedicated (arc pin `pa-c17a8d7e0660413b` reserved for arc-thread continuity only).

Rationale: Evidence-gathering is orthogonal to decision-space; parallelizing inventory saves ~1 turn per child × 2 children = ~2 turns arc-wide without violating decision-orthogonality or ordering discipline.

### 5.1 Child mission table

| Session | Child | Focus | Blast radius | Inheritance |
|---|---|---|---|---|
| S2601 | P1 Cat A | PA endpoint contract SoT declaration design-prep (Path A/B/C+island per F8) | 10+ PA-path endpoints minimum; extendable to 15-20 after opening inventory | S2501 §3 PA-path evidence + S2599 §3 4-plane / §5.3 Family A/B/C/D 401 taxonomy |
| S2602 | P2 Cat B | PA-client contract surface design-prep (a/b/c) — F1 hard boundary (contract-typing + field-list ONLY); U6+U7 evidence-gap closure turn 1 | assistantApi (~5-15 apiModule entries) + paStore (~9 fields per S2503 evidence) + pa_chat.py CLI wrapper | S2502 Cat B cockpitApi 96%-typed island exemplar + 7.36% platform baseline + S2504 SHAPE-BLIND interceptor pattern |
| S2603 | P3 Cat C | (C1) Workspace-context authz declaration Path A/B/C+compensating (F5 closure) + (C2) PA session-lifecycle α/β/γ/PA-override | (C1) 20 WORKSPACE_AWARE_AGENTS + 3+ PA-path endpoints; (C2) session_tool.retire + retention window + PA arc-pin lifecycle | S2402 F-B-HIGH-3 + S2504 §14 workspace evidence + S2503 CF-C2 + S1301 `feedback_session_tool_retire_works.md` |
| S2604 | P4 Cat D | PA REST↔WS T7 joint contract SoT (dual-owner PA side) — Path A/B/C strictness at PA WS channels + Cat D γ mechanism nesting applied at PA layer | 5-10 PA-related WS channels (subset of 120) + 3-7 PA-related Consumer classes (subset of 87); 0% envelope conformance at HEAD | S2504 CF-D6 + §Cat D γ decision + S2599 §3 4-plane permission-floor+REST↔WS plane |
| S2699 | xx99 canonical summary | Playbook §11.3 12-section template THIRTEENTH-consecutive application + §11.3 §10 5-subsection meta-methodology template THIRTEENTH-consecutive application (adopted S1399; unbroken S1399→S2699 candidate) | Full arc synthesis of 4 children + Chris-D-verdicts + AU-* anchor-update recs + T4 Group 1700 Observability handoff bundle | All 4 children + S2599 predecessor verdict inheritance |

### 5.2 SIGN cadence

Each of S2601-S2604 + S2699 runs Rigby SIGN cycle 1 via **dedicated fresh SIGN isolation pin** per playbook §15 SIGN-isolation discipline. Arc pin `pa-c17a8d7e0660413b` reserved for arc-thread continuity + parent-scoping shape-card SIGN-preview (already done 2026-07-06 turn 3 — see §8 fold record).

### 5.3 Acceptance criteria (8 items, F4+F5+F6 shape-card folds + F11+F12 SIGN cycle 1 folds applied)

Group 2600 PA arc close (S2699 xx99) delivers:

1. **PA endpoint contract-SoT declaration disposition per-endpoint recorded (F4 measurability + F11 denominator fold).** Denominator = **all PA-path endpoints in the declared slice** (minimum 10, maximum N = all discovered at Cat A S2601 opening inventory). ≥90% of endpoints in the denominator have EITHER (a) OpenAPI operationId + request/response schema declared, OR (b) documented defer-to-Group-2500 with target session identified. Zero endpoints "unknown/undecided" post-close. **Deliverable: one-page PA-path endpoint inventory table (method + path + view + file:line + disposition column) at Cat A S2601 close — used to compute the % + verify denominator.**
2. **REST↔WS T7 joint strictness at PA layer ratified.** Path A/B/C selection for PA WS message-contract; explicit Group 2500 Cat D γ mechanism-nesting acknowledgment (couple / decouple / preserve orthogonal).
3. **Workspace-context authz declaration policy ratified (F5 fold closure condition).** F-B-HIGH-3 closure: workspace-membership MUST be enforceable pre-handler at boundary (Path A permission-class OR Path B middleware path-list gate) OR explicitly waived with documented compensating controls (audit-log hook + policy ADR + `docs/topics/pa.md` documentation section) if Path C+compensating ratified. Path C-pure without compensating controls IS NOT a valid ratification.
4. **PA-client contract shape ratified.** Typed assistantApi.ts island vs SHAPE-BLIND vs hybrid + paStore field-list completeness U7 resolution (retained fields explicitly listed + cleanup fields explicitly listed).
5. **PA session-lifecycle contract disposition.** session_tool.retire policy on user logout coupled to Group 2400 Cat C α/β/γ verdict OR PA-specific override declared with rationale trace. PA conversation retention window explicitly stated.
6. **PA-adjacent probes disposition table established (F6 dial-back applied).** 3 contract-shaping probes only: (i) `/pa/chat/` streaming semantics, (ii) task-status polling contract, (iii) WS channel authentication handshake. Rate-limiting DROPPED per F6.
7. **Scoped PA-slice manifest + repeatable coverage measurement SPEC.** Commands + report schema + acceptance thresholds; spec only, NOT shipped script (mirrors S2500 AC#7 discipline). SIGN cycle 1 explicit AGREE-KEEP-BINDING per Rigby 2026-07-06: relaxing to shipped script would invite scope creep and break tested S1899-S2500 cadence discipline.
8. **REST↔WS T7 cross-transport consistency check (F12 new AC).** For each of the 3 §3.5 probed semantics (streaming semantics + task-status polling + WS channel authentication handshake), Group 2600 close produces an explicit request/response/envelope sketch AND a stated consistency rule across REST↔WS (even if the consistency rule is "defer-to-Group-2500 for both transports"). Prevents T7 hand-wavy close where REST side reports "declared" and WS side reports "declared" without evidence they agree on shape.

---

## 6. Parked candidate issues

Numbered list of out-of-scope but candidate future investigations. Post-arc T-slot follow-up queue candidates.

- **P-1** PA voice/TTS contract (`/api/assistant/voice/` + audio_url delivery + PROVIDER routing at TTS layer) — voice-specific contract-SoT decisions parked; deferable to voice-domain ADR post-arc.
- **P-2** PA telemetry envelope at Group 1700 Observability handoff — how PA emits per-request telemetry (tool_runs list format, LLMCallEvent shape, latency histograms). Adjacent to Group 1700 T4 arc.
- **P-3** PA 3-way chat consumer surface at frontend Chat UI (message rendering + tool-runs display + streaming UX) — NON-CANDIDATE at Cat B per F1 fold hard boundary; behavior scope for frontend team.
- **P-4** PA async task lifecycle at Celery layer (dedicated `pa` queue + task-status polling contract + `AgentExecution.input_data['context']['auto_followup']` semantics per MEMORY `feedback_auto_followup_false_suppresses_banner.md`) — task-status contract IN-SCOPE at Cat A; broader queue-layer decisions parked.
- **P-5** PA multi-tenancy at cross-repo Fleet federation (mentorforge/character-os PA federation) — Group 2400 Cat A preserved; cross-repo PA contract decisions deferable to federation-specific arc.
- **P-6** PA prompt engineering / system prompt content design — behavior scope, parked indefinitely at Group 2600 (may not become an arc; owned by PA subsystem docs).
- **P-7** PA memory persistence architecture (auto-memory MEMORY.md schema + retention + embedding pipeline) — Group 1300 Memory arc scope; not reopened at Group 2600.
- **P-8** LLM provider routing at PA layer (OpenAI vs Anthropic vs Together vs Ollama vs DeepSeek vs Gemini) — anti-scope #9 per F7 fold. Parked as future PA-operational ADR if load-bearing.
- **P-9** Agent timeout tuning + retry policy — anti-scope #10 per F7 fold. Parked as future PA-ops ADR if load-bearing.
- **P-10** Discord bot PA surface (48 slash + 48 prefix commands) — anti-scope #5 per §7. Delegated to Group 1900 Advisor scope.
- **P-11** PA content-scoring / signal-aggregation contract emission (per SignalCluster pattern types + PA-driven signals) — adjacent Group 2100 governance / Group 1600 content scope.

---

## 7. Anti-scope (10 items — F7 fold added #9 + #10)

Explicit OUT-OF-SCOPE items with rationale. Adjacent-domain ownership preserved.

1. **PA internal message-generation behavior mutations** — Prompt engineering, tool selection logic, context reasoning depth, output format. Group 2600 owns API contract SHAPE only; behavior is scope of PA subsystem docs + service-layer refactors elsewhere.
2. **PA prompt engineering / system prompt content** — Deliberately excluded; ADR-scope elsewhere. Any PA-behavior-relevant prompt changes remain outside Group 2600.
3. **PA memory persistence architecture** — Auto-memory MEMORY.md governance, retention, embedding pipeline. Group 1300 Memory arc scope.
4. **PA agent-registry mutations** — WORKSPACE_AWARE_AGENTS list content changes (adding/removing agents from workspace-aware dispatcher). Group 2600 declares enforcement policy at API layer; list membership is agent-system scope.
5. **Discord bot PA surface** — 48 slash + 48 prefix commands in `discord_bot.py`. Adjacent domain; Group 1900 Advisor + Discord scope.
6. **Content Studio PA endpoints (if any)** — Group 1600 Content scope.
7. **Fleet HMAC PA signature (cross-repo mentorforge/character-os federation)** — Group 2400 Cat A preserved.
8. **PA token / auth token rotation policy** — PA_API_TOKEN + TEST_AUTH_TOKEN handling. Group 2400 Auth scope.
9. **LLM provider/model policy decisions (F7 fold — Rigby SIGN-preview)** — OpenAI vs Anthropic vs Together vs Ollama vs DeepSeek vs Gemini routing decisions. Belongs to PA subsystem operational governance, not contract-SoT scope.
10. **Agent timeout tuning + retry policy (F7 fold — Rigby SIGN-preview)** — PA agent hard-limit, task-retry semantics, watchdog thresholds. Group 2400 operations + Group 1700 Observability scope, not Group 2600 contract-SoT scope.

---

## 8. Decisions recorded

### 8.1 Q1-Q4 shape card ratified (Chris "agree all" 2026-07-06)

| Q | Decision | Ratifier | Date | Rationale |
|---|---|---|---|---|
| Q1 | Option C: 4-child taxonomy (Cat A / Cat B / Cat C with 2 parallel sub-tracks / Cat D) | Chris | 2026-07-06 | Rejected Option A (2-child, conflates endpoint SoT with workspace authz) + Option B (3-child, conflates C1 authz declaration with C2 session lifecycle per F2 fold) + Option D (5-child, breaks MC-4 arithmetic without precedent). |
| Q2 | Central lens split into two sub-lenses per F10 SIGN cycle 1 fold: **§2.6.A baseline inheritance constraint** ("PA inherits Group 2500 verdict unless explicitly overridden with justification + compensating controls") + **§2.6.B PA delta-decision** ("Given /api/pa/chat/ is CLAUDE.md canonical entry, does PA warrant stricter contract declaration than baseline — and if so at which boundary layer?"). Original F3 fold single-binary rewrite superseded by F10 two-lens split. §2.5 evidence-gap framing preserved (F9). Explicit "no Cat B option enumeration until U6/U7 confirmed" guardrail added (F10a). | Chris | 2026-07-06 (F3 shape-card) + pending SIGN-close (F10 SIGN cycle 1) | Rigby SIGN cycle 1 STRENGTHEN Q2 verdict: F3 folded lens still overloaded post-fold; split into two labeled sub-lenses (constraint + delta-decision) demotes CLAUDE.md-canonical clause from lens body to delta-input. HIGH confidence. |
| Q3 | 8 acceptance criteria — 7 shape-card items (F4+F5+F6 folds) + AC#8 T7 cross-transport consistency check added per F12 SIGN cycle 1 fold. AC#1 denominator tightened per F11 fold: denominator = "all PA-path endpoints in the declared slice (min 10, max N=all discovered)" + require one-page PA-path endpoint inventory table deliverable at Cat A S2601 close. F13 fold added §5.1 ordering rationale — parallel evidence-collection permitted for Cat B+D (inventory-only, no option enumeration) while decision-order stays A→B→C→D. AC#7 spec-only discipline explicit AGREE-KEEP-BINDING per Rigby verdict. | Chris | 2026-07-06 (F4/F5/F6 shape-card) + pending SIGN-close (F11/F12/F13 SIGN cycle 1) | Rigby SIGN cycle 1 STRENGTHEN Q3 verdict: AC set close to xx99-verifiable; AC#1 90% needed explicit denominator + sampling; T7 needed explicit cross-transport consistency check; ordering fine but parallel evidence-collection saves ~2 turns arc-wide; AC#7 relax would break tested S1899-S2500 discipline. HIGH confidence. |
| Q4 | 10 anti-scope items (F7 added #9 + #10) | Chris | 2026-07-06 | Original 8-item list well-calibrated per Rigby SIGN-preview; F7 added explicit walls on LLM provider/model policy decisions (#9) + agent timeout tuning (#10). |

### 8.2 Rigby SIGN-preview fold record (9 folds Chris-ratified)

Shape-card SIGN-preview routed 2026-07-06 via arc pin `pa-c17a8d7e0660413b` turn 3. Rigby verdict: **MEDIUM confidence** with 7 explicit folds + 2 maturity-flag folds. All 9 folds Chris "agree all" ratified same session.

| Fold | Q | Direction | Adoption |
|---|---|---|---|
| F1 | Q1 Cat B | STRENGTHEN hard boundary: contract-typing + field-list completeness ONLY; exclude UI/UX behavior + state-mgmt refactors | ✅ Baked into §3.B scope + §3.B explicit-exclusions |
| F2 | Q1 Cat C | STRENGTHEN split into C1 (authz declaration) + C2 (session lifecycle) as parallel sub-tracks inside Cat C | ✅ Baked into §3.C1 + §3.C2 |
| F3 | Q2 | STRENGTHEN rewrite to single binary + single layer-choice; U6/U7 to evidence gaps | ✅ Baked into §5 central lens + §2.5 evidence gaps |
| F4 | Q3 AC#1 | STRENGTHEN measurability: ≥90% + 0 unknown post-close | ✅ Baked into §5.3 AC#1 |
| F5 | Q3 AC#3 | STRENGTHEN F-B-HIGH-3 closure: pre-handler enforcement OR compensating controls; blocks paper-victory | ✅ Baked into §5.3 AC#3 + §3.C1 Path C+compensating axis |
| F6 | Q3 AC#6 | DIAL-BACK probes to 3 contract-shaping only; drop rate-limiting | ✅ Baked into §5.3 AC#6 + §3.5 disposition table |
| F7 | Q4 | STRENGTHEN +2 anti-scope items (LLM provider/model policy + agent timeout tuning) | ✅ Baked into §7 items #9 + #10 |
| F8 | Cat A maturity | UNDERSTATED — CLAUDE.md canonical entry `/api/pa/chat/` warrants Path C+island baseline (minimum PA-island declaration) instead of pure Path C-defer | ✅ Baked into §3.A Path C+island axis + §3.A F8 baseline codification |
| F9 | U6/U7 maturity | OVERSTATED — label as evidence gaps requiring Cat B S2602 opening inventory, not decision inputs | ✅ Baked into §2.5 evidence gaps section + §3.B evidence-gap opening turn 1 note |

### 8.2b SIGN cycle 1 fold record (4 folds Rigby-strengthened + pending Chris ratification)

Full parent scoping doc routed 2026-07-06 to dedicated fresh SIGN isolation pin `pa-499cc1897b0d4a3e` (TWENTY-THIRD consecutive dedicated fresh SIGN pin candidate at close after twenty-two prior). Rigby SIGN cycle 1 verdict: **HIGH confidence** with 4 explicit STRENGTHEN folds across Q2+Q3 (Q1+Q4 AGREE with no folds).

| Fold | Q | Direction | Adoption |
|---|---|---|---|
| F10 | Q2 | STRENGTHEN split central lens into §2.6.A baseline inheritance constraint + §2.6.B PA delta-decision (demotes CLAUDE.md-canonical clause to delta-input) | ✅ Baked into §2.6 new subsection + §8.1 Q2 row |
| F10a | Q2 | STRENGTHEN §2.5 guardrail: "No Cat B option enumeration until inventory confirms U6/U7" | ✅ Baked into §2.5 last-paragraph + §2.6 evidence-gap gating note |
| F11 | Q3 AC#1 | STRENGTHEN denominator definition + one-page inventory table deliverable at Cat A S2601 close | ✅ Baked into §5.3 AC#1 |
| F12 | Q3 new AC#8 | STRENGTHEN add T7 cross-transport consistency check AC — request/response/envelope sketch + consistency rule for 3 §3.5 probes | ✅ Baked into §5.3 AC#8 (new item) |
| F13 | Q3 §5.1 ordering | STRENGTHEN permit parallel evidence-collection for Cat B+D (inventory-only, no option enumeration) while decision-order A→B→C→D preserved | ✅ Baked into §5.1 ordering-rationale block + explicit F13-conditions clause |
| — | Q3 AC#7 | AGREE-KEEP-BINDING explicit — "spec only, not shipped script" discipline preserved; relax would break S1899-S2500 tested cadence | ✅ Baked into §5.3 AC#7 explicit-AGREE annotation |

**Q1 (§3 taxonomy):** AGREE — no fold. Cleanly preserves decision-orthogonality per S2504 §88 discipline.
**Q4 (§7 anti-scope + §6 parked + §4 runtime cap):** AGREE — no fold. Anti-scope correctly fences off two biggest entropy magnets (F7 provider/model + timeout tuning); runtime cap 6-target/8-cap consistent with tested pattern.

### 8.3 Structural decisions

- **Runtime target: 6 sessions.** MC-4 pattern SEVENTH-consecutive candidate.
- **Runtime cap: 8 sessions.** Trigger conditions in §4.4.
- **Arc pin: `pa-c17a8d7e0660413b`** (created 2026-07-06 turn 1; `tools/pa_local.sh:348` rotated at S2600 open).
- **Retired pin: `pa-a03b111768464b3f`** (Group 2500 API arc pin; retired at S2599 xx99 close 2026-07-06 per playbook §16).
- **Delegated arcs handoff table populated at S2699 xx99:** T4 Group 1700 Observability + T5 Group 2300 Mobile + T6 Group 1600 Content queued in §8.2 T-slot queue at S2599 xx99 close.
- **Playbook template lineage:** §11.1 SEVENTH-consecutive parent-with-children application (S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2500 eleven-prior overall; SEVENTH-consecutive-in-parent-with-4-children track per Groups 1900+2000++2100+2200+2400+2500 six prior).

### 8.4 Pending decisions (routed to Rigby SIGN cycle 1)

- Full parent scoping doc routed to Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin (playbook §15 discipline).
- SIGN cycle 1 verdict + fold record + confidence-level to be recorded at §8.5 after SIGN close.
- Chris ratification of full parent scoping doc + status flip `draft → active` per playbook §16 draft-first workflow.

### 8.5 Rigby SIGN cycle 1 record

- **Dedicated SIGN pin ID:** `pa-499cc1897b0d4a3e` (created 2026-07-06 via `session_tool action=create_fresh title='Group 2600 PA parent scoping SIGN cycle 1 (S2600 close)'`).
- **SIGN batch structure:** Single-batch × 4-Q cadence per S1899-S2500 EIGHT-consecutive tested pattern (NINTH-consecutive-in-parent-scoping application candidate).
- **SIGN verdict per Q:**
  - Q1 (§3 taxonomy): **AGREE** — no folds.
  - Q2 (§5→§2.6 central lens): **STRENGTHEN** — F10 two-lens split + F10a evidence-gap guardrail (2 folds).
  - Q3 (§5.3 AC + §5.2 cadence + §5.1 ordering): **STRENGTHEN** — F11 AC#1 denominator + F12 new AC#8 T7 consistency + F13 parallel evidence-collection permission (3 folds). AC#7 explicit AGREE-KEEP-BINDING (spec-only discipline preserved).
  - Q4 (§7 anti-scope + §6 parked + §4 runtime cap): **AGREE** — no folds.
- **Overall confidence:** **HIGH**.
- **Fold adoption:** All 4 STRENGTHEN folds baked in-place; §8.2b SIGN cycle 1 fold record documents each with §-anchor.
- **SIGN pin retirement:** Pending at S2600 close via `session_tool.retire force=true` — TWENTY-THIRD consecutive dedicated fresh SIGN pin retirement in Research OS candidate after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500/S2501/S2502/S2503/S2504/S2599 twenty-two prior.
- **Chris ratification card:** Pending presentation post-fold — "commit it" candidate at S2600 close. On ratification, frontmatter `status: draft` → `status: active` per playbook §16 draft-first workflow.

---

## 9. Next step

On Chris ratification of this parent scoping doc at S2600 close (SIGN cycle 1 + "commit it" wholesale-or-partial):

1. **Status flip:** frontmatter `status: draft` → `status: active`.
2. **`00-START-NEXT-SESSION.md` overwrite:** S2601 P1 Cat A priorities loaded — PA endpoint contract SoT declaration design-prep opening turn 1 protocol (inventory PA-path endpoints + Path A/B/C+island axes enumeration + F8 baseline codification verification).
3. **`OPEN_ARCS.md` update:** Group 2600 PA row transitions `not-started` → `in-progress`; S2601 Cat A registered as first child.
4. **Docs cascade:** 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync --embed`) + `build_docs_provenance` per MEMORY `feedback_cascade_pr_must_include_embed_step`.
5. **Handoff:** `docs/handoffs/SESSION_2600_PA_PARENT_SCOPING.md` (post-close artifact per playbook §16 handoff discipline).
6. **S2601 opening command:** `Continue research group 2600: S2601` or `Continue research group 2600: P1 Cat A endpoint contract SoT`.

---

## Appendix — Frontmatter provenance

**Session:** S2600 (arc-open 2026-07-06). **Session ID:** 2600. **Domain slug:** pa. **Research group:** 2600. **Child slot:** parent.

**Repo state at draft-open:**
- **Branch:** main
- **HEAD SHA:** 76342fd5 (S2599 merge)
- **Untracked:** `.claude/scratch/` only (Claude Code scratch)

**Load-bearing input documents read (via Explore sub-agent extract 2026-07-06 turn 2):**
- `docs/research/domains/api/2599_api_canonical_summary.md` — DIRECT PREDECESSOR (Group 2500 API xx99 close)
- `docs/research/domains/api/2500_api_domain_scoping.md` — PARENT-SCOPING TEMPLATE MODEL
- `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` — CF-2600-PA ORIGIN (Cat A)
- `docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md` — CF-D6 ORIGIN (Cat D)
- `docs/research/domains/auth/2499_auth_canonical_summary.md` — PRIOR-PRIOR ARC CLOSE MODEL
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.1 parent scoping template + §21 short-command vocabulary

**Wrapper rotation record (2026-07-06 turn 1):**
- Fresh arc pin minted via `session_tool action=create_fresh title='Group 2600 PA arc pin (S2600 open)'` → `pa-c17a8d7e0660413b`.
- `tools/pa_local.sh:348` rotated from retired `pa-a03b111768464b3f` (Group 2500 API arc pin retired at S2599 xx99 close per playbook §16) → `pa-c17a8d7e0660413b`.
- `tools/pa_local.sh` header ledger updated with S2600-open stanza per S2000/S2100/S2200/S2400/S2500 documentation pattern.
- Health check: `platform_config_tool overview` on new arc pin returned `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` (2026-07-06 turn 2).

**Shape card SIGN-preview record (2026-07-06 turn 3):**
- Routed via arc pin `pa-c17a8d7e0660413b` (single-batch × 4-Q preview cadence per S1899-S2500 EIGHT-consecutive tested pattern).
- Rigby verdict: MEDIUM confidence with 9 folds (7 Q-specific + 2 maturity-flag).
- Chris "agree all" 2026-07-06 ratified all 9 folds wholesale.
- 9 folds baked into §2.5 + §3.A + §3.B + §3.C1 + §3.C2 + §3.D + §5 central lens + §5.3 AC + §7 anti-scope + §8.2 fold record before full parent scoping draft opened.

**Draft record:** v1 drafted 2026-07-06 turn 4 by Claude Code (parent) after shape-card ratification. Status remains `draft` until Chris ratifies at SIGN cycle 1 close.

**Companion doc structural precedent:** Follows `docs/research/domains/api/2500_api_domain_scoping.md` structure (§1-§9 + Appendix) with 4-child variant matching S2400 Auth + S2500 API precedents.
