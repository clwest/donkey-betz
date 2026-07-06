---
title: "PA Endpoint Contract Source-of-Truth Design-Prep Audit (Group 2600 P1 Cat A)"
session: 2601
status: active (S2601 P1 Cat A PA Endpoint Contract SoT Design-Prep — child audit CLOSED post-Chris "agree all" ratification 2026-07-06. Playbook §11.2 20-section child-audit template TWENTY-FIRST-consecutive application after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402+S2403+S2404+S2501 twenty prior. Shape-card SIGN-preview via arc pin `pa-c17a8d7e0660413b` returned Rigby overall confidence HIGH with 9 folds (F1-F9); Chris "agree all" 2026-07-06 ratified all 9 folds wholesale pre-drafting. Rigby SIGN cycle 1 on full audit doc via 2-pin recovery pattern per `feedback_rigby_sign_worker_instability_recovery.md`: (a) dedicated fresh SIGN isolation pin `pa-ad162d8af36c4985` (TWENTY-FOURTH consecutive dedicated fresh SIGN pin retirement in Research OS after 23 prior) captured Q1+Q2+Q3+partial-Q4 substantive verdicts across Batch 1 (Q1+Q2) + Batch 2 (Q3+Q4) 2-batch cadence for 8729-word doc per feedback batching threshold; hit turn-3 worker instability at close-summary prompt; retired at 5 updated rows; (b) recovery pin `pa-767dddd95cb24099` (TWENTY-FIFTH consecutive dedicated fresh SIGN pin retirement candidate) ultra-short-ping first + titles-only close per feedback recovery playbook; captured Q4 close verdict + overall MEDIUM confidence + cycle 2 candidacy suggestion; retired at 3 updated rows. Parent-Claude verifier-loop applied as compensating quality gate per feedback recovery clause: 2 recovery-pin-suggested Q4 folds (Q4.3 remediation ladder + Q4.4 verification harness) REJECTED as Cat A boundary violations (evidence-only discipline). Net: 7 substantive folds (S1-S7) captured with clear fold text from well-contextualized Pin 1; Chris "agree all" 2026-07-06 ratified all 7 folds wholesale. Cycle 2 NOT required. Arc pin `pa-c17a8d7e0660413b` PRESERVED through S2601 per playbook §16 arc-standard behavior.)
arc: Research Group 2600 (PA — Cross-Arc Handoff Bundle Consuming CF-2600-PA + CF-D6 + F-B-HIGH-3 + Workspace-Context Authz + REST↔WS T7 Joint Dual-Owner) — S2601 P1 Cat A PA Endpoint Contract SoT Design-Prep child audit
category: research (playbook §11.2 20-section child-audit template TWENTY-FIRST-consecutive application)
authors: Claude Code (S2601 P1 Cat A draft 2026-07-06 at HEAD `7ddd8ce6`; parent-Claude verifier-loop applied per playbook §14 pre-draft on 6-Explore-agent sub-agent claims — 5 corrections landed pre-draft); Rigby SIGN cycle 1 PENDING via dedicated fresh SIGN isolation pin per playbook §15; Chris "commit it" ratification PENDING
verifier_loop: >
  Parent-Claude verifier-loop applied per playbook §14 on 6-Explore-agent
  sub-agent claims pre-draft. Five verifier corrections landed pre-draft:

  1. **PAResponse class EXISTS.** Explore Agent 5 (Documentation) reported
     the PAResponse class referenced in docs/topics/personal-assistant.md
     "does not exist" (labeled CRITICAL drift). Parent-Claude verifier
     grepped `^class PAResponse` and found the class at
     `core/services/unified_pa_entrypoint.py:194` as a `@dataclass`.
     Explore Agent 2 (Services) correctly identified it. Verifier
     correction: PAResponse EXISTS; §14 drift item is invalidated.

  2. **PA tool schema count = 113 (not 119).** Explore Agent 3 (APIs)
     reported 119 tool schemas via `grep -c '"name":'` on
     `core/services/pa_tool_schemas.py`. Parent-Claude verifier ran a
     Python regex counting top-level dict entries in `PA_TOOL_SCHEMAS`
     list; the `"name":` grep bloated to 119 by matching nested schema
     property definitions (e.g., parameters with a "name" key). Actual
     top-level schema count matches PLATFORM_INVENTORY.md claim of 113
     schemas (verified via `docs/PLATFORM_INVENTORY.md` autoblock line
     18). Explore Agent 6 correctly reported 113 matches actual.

  3. **PA-path URL denominator = 34 (not 27).** Explore Agent 3 reported
     27 endpoints via URL grep. Parent-Claude verifier found:
     (a) 27 single-line `path()` matches for `api/pa/|api/assistant/|api/v1/assistant/` prefixes at `core/urls.py` lines 2485-2524;
     (b) 3 multi-line `path()` calls for F2F voice-session endpoints
     (`api/pa/voice_session/` + `.../<uuid:session_id>/speak/` + `.../end/`)
     at lines ~2526-2540 that the single-line grep missed;
     (c) 4 dev/minimal routes at lines 4900-4903 (`api/assistant/dev/chat/`,
     `api/assistant/dev/context/`, `api/assistant/minimal/chat/`,
     `api/assistant/minimal/context/`) that Agent 3 partially captured
     (dev/minimal noted but count not aggregated).
     **Corrected denominator: 27 + 3 F2F + 4 dev/minimal = 34 PA-path URL
     patterns at HEAD `7ddd8ce6`.**

  4. **`assistant_context` view import origin partially UNKNOWN.**
     Explore Agent 3 reported `assistant_context` (referenced at
     `core/urls.py:2485` for `/api/v1/assistant/context/`) view import
     not found in expected view files. Parent-Claude verifier grepped
     `^(def|async def) assistant_context\b` across `core/*.py` — 0
     matches. Import statement located at `core/urls.py:1005`:
     `from core.views import (..., assistant_context, ...)`. The view is
     imported from the `core.views` package (aggregator or legacy
     module); the `def` site is inside that package but not surfaced by
     top-level `core/*.py` grep. **Recorded as UNKNOWN with next-step
     pointer per shape-card F5 fold** (Cat B or Cat A follow-up: trace
     the `core.views` package aggregator).

  5. **Enrichment services = 8 (not 3).** Explore Agent 2 reported "3
     confirmed" enrichment services by counting `*Enricher`/`*Service`
     class definitions. Explore Agent 6 reported 8 in
     `INTENT_ENRICHMENT_MAP` (advisor, blog_performance, domain_context,
     intelligence_enricher, platform_briefing, proactive_intelligence,
     spider_trends, strategic_memory). Parent-Claude verifier grepped
     `INTENT_ENRICHMENT_MAP` dict at
     `core/services/unified_pa_entrypoint.py:244` and found 31 unique
     tokens (including intent categories + service names + tool
     namespaces). PLATFORM_INVENTORY.md canonical claim is **8
     enrichment services** — Agent 6 correct; Agent 2 undercounted by
     confusing `*Enricher` class-file count with enrichment service
     registry count.

  Additional verifier confirmations (all sub-agent claims verified
  accurate at HEAD): (a) `drf_spectacular` NOT in `INSTALLED_APPS` at
  `core/settings.py:161-215` (grep returned 0 matches — inherited from
  S2501 confirmed at HEAD `7ddd8ce6`); (b) 0 `@extend_schema`
  decorators across all 5 PA-related view files
  (views_personal_assistant.py + views_assistant_bypass.py +
  views_f2f.py + views_image_tools.py + views_image_misc.py); (c)
  `/api/pa/chat/` docstring at `core/views_personal_assistant.py:267-289`
  contains structured Request/Response body examples but NO OpenAPI
  operationId + NO drf-spectacular markup + NO external YAML —
  **F8 baseline codification NEGATIVE at HEAD; Path C-pure strictly-
  worse than Path C+island evidence recorded**; (d) no OpenAPI YAML
  file with `paths:` key found outside `.github/workflows/*.yml` CI
  templates.

  Verifier discipline aligned with S2501 §14.6 four-pre-draft-correction
  pattern. Cat A boundary discipline preserved — evidence-only; no
  verdict recommendations on Path A/B/C+island.
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                          # runtime counts anchor — 113 PA tool schemas + 156 handlers + 8 enrichment services + 1,864 URL patterns
  - docs/PLATFORM_WHAT_IT_IS.md                                         # narrative anchor — PA subsystem narrative
  - docs/topics/personal-assistant.md                                   # PA subsystem topic doc — DRIFT: PAResponse existence resolved (§14.1 verifier correction)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                           # process contract §11.2 TWENTY-FIRST application
  - docs/research/domains/pa/2600_pa_domain_scoping.md                  # DIRECT PARENT — §3.A Cat A scope + §5.1 F13 clause + §5.3 AC + §2.6.A/B lens + §7 anti-scope
  - docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md  # PARENT-ARC PREDECESSOR — Cat A REST-boundary discipline template + 3-co-existing-401-shapes evidence + @extend_schema decorator-inert baseline
  - docs/research/domains/api/2599_api_canonical_summary.md             # Group 2500 API canonical verdict — inherited as §2.6.A hard constraint
  - docs/research/domains/auth/2402_auth_permission_floor_uniformity_audit.md  # F-B-HIGH-3 workspace-membership implicit-gate origin — forwarded to S2603 Cat C1
  - core/views_personal_assistant.py                                    # 20+ PA/assistant view function definitions; @permission_classes[IsAuthenticated] uniformly declared
  - core/urls.py                                                        # 34 PA-path URL registrations (single-line + multi-line + dev/minimal blocks)
  - core/services/unified_pa_entrypoint.py:194                          # PAResponse dataclass definition (invalidates docs/topics/personal-assistant.md drift claim)
  - core/services/pa_tool_schemas.py                                    # 113 PA tool schemas (SCHEMA_VERSION versioning; no external export)
  - core/services/tool_dispatcher.py                                    # 156 tool handlers registered
  - core/epa_handlers_tools.py:191-217                                  # WORKSPACE_AWARE_AGENTS constant (20 agents)
  - core/agents/base_agent.py:5355                                      # execute_with_workspace() — F-B-HIGH-3 implicit-gate location (Cat C1 handoff)
  - core/settings.py:161-215, 1600-1605                                 # INSTALLED_APPS (drf_spectacular ABSENT) + SPECTACULAR_SETTINGS 4-key config (INERT)
  - CODEOWNERS                                                          # PA code paths fall to default `* @clwest` (S2499 AU-D5 baseline)
delegated_from:
  - Group 2600 S2600 §3.A Cat A mission — "PA endpoint contract SoT declaration disposition per-endpoint recorded (Path A / Path B / Path C+island per F8 baseline)"
  - Group 2500 S2501 Cat A boundary discipline template — REST-boundary evidence-only + verdict-neutrality on Path A/B/C
  - Group 2500 S2599 API canonical verdict — IMPLICIT-INHERITANCE + ISLAND-DECLARATION pockets + ZERO cross-transport SoT (baseline inheritance)
delegates_to:
  - S2699 xx99 Group 2600 canonical summary — Cat A REST-boundary evidence for arc-seam ratification + Path A/B/C+island Chris-D-verdict
  - S2602 P2 Cat B PA-client contract surface — Cat A boundary evidence for assistantApi.ts + paStore + tools/pa_chat.py consumer typing decision (F1 hard boundary preserved)
  - S2603 P3 Cat C1 workspace-context authz — Cat A observation of F-B-HIGH-3 implicit-gate at HTTP boundary (permission_classes = [IsAuthenticated] uniformly; workspace-membership check INTERNAL only) + S2603 owns Path A/B/C+compensating verdict
  - S2604 P4 Cat D REST↔WS T7 joint — Cat A REST-side contract shape evidence for cross-transport consistency check (AC#8 F12 fold)
lens: >
  Cat A boundary lens question (Chris-ratified per shape-card F3 fold
  2026-07-06 — REST evidence-only wording):

  "For each PA-path REST endpoint at HEAD, what contract declaration
  artifacts exist today at the REST boundary (OpenAPI operationId,
  request schema, response schema(s), documented error response shape
  if present, and any explicit authz/permission annotation if present)
  — and if missing, is the absence due to (a) no drf-spectacular
  wiring, (b) serializer-less view patterns, or (c) intentional
  defer-to-Group-2500 baseline?"

  Cat A boundary evidence-only: Cat A collects DECLARATION evidence
  (what the backend REST layer declares to schema consumers) without
  recommending Path A/B/C+island verdict, without authoring
  @extend_schema retrofit, and without picking typed-client codegen
  framework (§7 anti-scope #7 template inheritance from S2501; §7 F9
  micro-anti-scope "no endpoint behavior changes / no refactors").
  Verdict on Path A / Path B / Path C+island is a Chris-D-verdict-
  request at S2699 xx99 close after all 4 children have contributed
  evidence.
playbook_application: §11.2 20-section child-audit template TWENTY-FIRST-consecutive application per S2600 §5.1 child mission sequence; §13 six-parallel-Explore-agent sweep contract applied at S2601 open — 6 Explore agents dispatched with self-contained briefs (Models + Persistence / Services + Runtime Flows / APIs + Tools + Tasks + Commands / Integrations + Cross-Domain / Documentation + Prior Research / Drift + Debt + Ownership + Maturity); §14 parent-Claude verifier-loop applied pre-draft — 5 corrections landed pre-draft; §15 SIGN cycle 1 REQUIRED at child-audit stage per playbook §15 stage-scoped routing — routed via dedicated fresh SIGN isolation pin (NOT arc pin `pa-c17a8d7e0660413b`) per playbook §15 SIGN-isolation discipline (TWENTY-FOURTH consecutive dedicated fresh SIGN pin candidate under Research OS after 23 prior); §16 arc pin `pa-c17a8d7e0660413b` PRESERVED through S2601 per playbook §16 arc-standard behavior (no retirement until S2699 xx99 close)
---

# PA Endpoint Contract Source-of-Truth Design-Prep Audit (Group 2600 P1 Cat A)

> **DRAFT.** S2601 P1 Cat A child audit drafted 2026-07-06 (HEAD `7ddd8ce6`). 6-parallel-Explore-agent sweep + parent-Claude verifier-loop per playbook §14 (5 pre-draft corrections) + Rigby SIGN-preview HIGH confidence with 9 folds (Chris "agree all" 2026-07-06 ratified). Rigby SIGN cycle 1 on full audit doc via dedicated fresh SIGN isolation pin PENDING. Arc pin `pa-c17a8d7e0660413b` PRESERVED through S2601. TWENTY-FIRST-consecutive playbook §11.2 20-section child-audit template application.

> **Cat A boundary discipline paramount.** Cat A collects EVIDENCE for future Chris-D-verdicts on Path A / Path B / Path C+island (per parent §3.A + F8 baseline codification). Cat A does NOT recommend verdicts; Cat A does NOT author @extend_schema retrofit code; Cat A does NOT pick typed-client codegen framework (§7 anti-scope #7 S2501 template inheritance; F9 fold micro-anti-scope "no endpoint behavior changes / no refactors").

> **Denominator lock (F11 fold).** F11 canonical artifact — one-page PA-path endpoint inventory table at §6 — used to compute AC-A1 ≥90% coverage + verify denominator. AC-A2 declares §6 table as **canonical artifact; later sessions (Cat B/C/D + S2699 xx99) must not re-inventory** (F7 fold).

## 1. Executive Summary

PA Endpoint Contract SoT layer at HEAD `7ddd8ce6` is **UNIFORMLY UNDECLARED at the REST boundary** — 34 PA-path URL patterns (denominator locked per F11 fold at §6) span three prefixes `/api/pa/*` + `/api/assistant/*` + `/api/v1/assistant/*` + dev/minimal variants; **0 of 34 declare `@extend_schema` decorators**; **0 declare OpenAPI operationId outside `@extend_schema`**; **0 have external OpenAPI YAML alignment**. `drf_spectacular` is pip-installed (`requirements.txt`) and `SPECTACULAR_SETTINGS` is 4-key-configured (`core/settings.py:1600-1605`), but drf-spectacular is **NOT registered in `INSTALLED_APPS`** (verified against `core/settings.py:161-215`) and **no `SpectacularAPIView` URL route is registered** — inheriting the Group 2500 platform-wide DECLARATOR-INERT baseline (S2501 §1).

**F8 baseline codification NEGATIVE (evidence).** Cat A opening turn 1 verifier check confirmed `/api/pa/chat/` (CLAUDE.md canonical operator entry point at `core/views_personal_assistant.py:267`) has: (a) structured Request/Response body examples in the docstring (lines 267-289) — human-readable but NOT machine-consumable by any OpenAPI generator, (b) NO drf-spectacular decorator, (c) NO external OpenAPI YAML declaration (grep across `**/*.yaml|yml` outside `.github/workflows` returned zero `paths:` keys anywhere in the repo), (d) NO custom `bpaas_schema`-style hand-emitted OpenAPI endpoint. **Boundary-neutral implication (S1 SIGN cycle 1 fold):** any future Chris-D-verdict that selects "Path C-pure" would **explicitly accept** that the CLAUDE.md canonical PA entry point remains without a machine-consumable REST-boundary contract declaration at HEAD; a "Path C+island" verdict would instead require a minimum PA-island declaration for `/api/pa/chat/`. Cat A records the evidence and the implication **without recommending a choice**.

**Response envelope shape at PA-path.** All PA endpoints use **hand-constructed `Response()` dicts** — no ModelSerializer coverage (except `PaMessageFeedback` used at `/api/pa/feedback/`). Canonical success shape is `{"success": True, "data": {...}}` or `{"success": True, "<key>": ...}` (with variant across 20+ endpoint files). Canonical failure shape splits into: (a) DRF default `{"detail": ...}` on 401 (implicit inheritance through `IsAuthenticated`), (b) bare `Response({"success": False, "error": "..."}, status=...)` — inheriting S2501 verifier-confirmed 3-co-existing 401 shapes (DRF default + APIResponseEnvelope + bare Response). **`APIResponseEnvelope` (from `core/api_responses.py`) is NOT used at any PA-path endpoint** (verified via grep across 5 PA view files). PA-path 401 shape family is Family A (DRF default) uniformly, inheriting Group 2500 Cat C S2503 4-family taxonomy.

**Permission-floor at REST boundary.** All 34 PA-path endpoints declare `@permission_classes([IsAuthenticated])` OR inherit the DRF DEFAULT (`REST_FRAMEWORK[DEFAULT_PERMISSION_CLASSES] = [IsAuthenticated]` at `core/settings.py:645-669`). **NO explicit `WorkspaceMember` DRF class enforcement at HTTP boundary** for any PA-path endpoint. Workspace-membership authorization is **INSIDE the handler** at `core/agents/base_agent.py:5355 execute_with_workspace()` — the F-B-HIGH-3 implicit-gate location. Cat A records this as boundary observation; **verdict on Path A permission-class retrofit / Path B middleware path-list gate / Path C+compensating handler-internal is Cat C1 S2603 scope**, not Cat A.

**REST↔WS T7 cross-transport strictness.** Cat A REST-side records: `/api/pa/chat/` returns task_id (async task-based, NOT streaming); Client polls `/api/pa/chat/status/<task_id>/` for completion. NO SSE, NO chunked-transfer-encoding, NO WebSocket at any PA-REST endpoint. This is Cat A boundary evidence for AC#8 (F12 T7 cross-transport consistency check) — Cat D S2604 owns WS-side. REST-side statement: PA REST is **task-based async with polling contract**, not **streaming async**. Design consequence: Railway proxy timeout avoidance (POST returns fast; Celery worker processes in background; polling GET returns 200 for both processing + completed).

**Biggest Cat-A-boundary evidence items (§19 recommends future research — Chris-D-verdict-request at S2699 xx99):**

1. **drf-spectacular app-registration + URL-routing wire-up is a prerequisite dependency** for any future Path A adoption at PA-path (inherited from Group 2500). [S1 SIGN cycle 1 fold — dependency framing, not gating recommendation.]
2. **`/api/pa/chat/` F8 baseline NEGATIVE** — Path C-pure strictly-worse than Path C+island at CLAUDE.md canonical entry point.
3. **F-B-HIGH-3 workspace-membership implicit-gate** location confirmed at `core/agents/base_agent.py:5355`. Cat A records boundary; Cat C1 S2603 owns closure-condition verdict (Path A/B/C+compensating per F5 parent fold).
4. **PA response envelope hand-construction** — 0 serializer coverage (except PaMessageFeedback) + 0 APIResponseEnvelope adoption + no typed shape declaration surface at HEAD.

**What comes next.** S2602 Cat B receives Cat A REST-boundary evidence for PA-client contract shape decision (assistantApi.ts + paStore + tools/pa_chat.py — Cat B scope preserved per F1 hard boundary fold). S2603 Cat C receives Cat A workspace-authz enforcement location evidence for C1 closure verdict + Cat A response envelope evidence for C2 session-lifecycle envelope decision. S2604 Cat D receives Cat A REST-side task-based-async pattern for AC#8 T7 cross-transport consistency check.

## 2. Domain Purpose

**Playbook §9 canonical Q1-Q2 — What is this domain?**

The PA (Personal Assistant) Endpoint Contract SoT layer is the **declaration-side substrate** of the PA subsystem's REST API surface — the mechanism by which the PA subsystem tells (a) frontend consumers (assistantApi + paStore in `frontend/src/`), (b) CLI/tooling consumers (`tools/pa_chat.py`), (c) research/audit consumers (this arc), (d) potential fleet-federation consumers (cross-repo mentorforge/character-os per Group 2400 Cat A anti-scope preservation), what shapes it accepts (request bodies + query parameters + path parameters + auth headers) and what shapes it returns (typed success responses + typed error envelopes + per-endpoint auth requirements).

At HEAD `7ddd8ce6`, the layer is **UNIFORMLY UNDECLARED at the REST boundary** per §1 evidence — 34 endpoints × 0 `@extend_schema` × 0 OpenAPI operationId × NO external YAML × NO APIResponseEnvelope adoption.

**Cat A boundary — what Cat A owns:** the DECLARATION side at the REST layer. Cat A owns questions of the shape "does each PA-path endpoint DECLARE X to consumers?" Cat A does NOT own questions of the shape "does the frontend CONSUME X correctly?" (Cat B P2 owns), "does the workspace-authorization contract PROPAGATE?" (Cat C1 P3 owns), "does the session-lifecycle contract COUPLE to Group 2400 verdict?" (Cat C2 P3 owns), "does the WS message-contract PARALLEL the REST-contract?" (Cat D P4 owns).

**Domain purpose scope discipline (per playbook §5 phase discipline research-only + design-prep; F9 fold micro-anti-scope):** Cat A collects evidence for future Chris-D-verdicts. Cat A does NOT recommend, decide, or author. Cat A does NOT change endpoint behavior. Cat A does NOT add or remove decorators. Everything below is EVIDENCE. Nothing below is DIRECTIVE.

## 3. Canonical Entry Points

**Playbook §9 canonical Q3 — Where does the domain enter the system?**

### 3.1 PA canonical REST entry points at HEAD `7ddd8ce6`

Three URL prefixes registered in `core/urls.py`:

| Prefix | Purpose | Line-range at core/urls.py | Count |
|---|---|---|---|
| `/api/pa/*` | Canonical PA prefix (CLAUDE.md canonical route) | 2508-2540 (block A) | 12 |
| `/api/assistant/*` | Compat prefix | 2490-2506 + 2500 bypass alias + 4900-4903 dev/minimal | 18 |
| `/api/v1/assistant/*` | Legacy v1 compat prefix | 2485-2486 | 2 |
| Also `/api/pa/voice_session/*` (F2F voice, multi-line path()) | Parent §6 parked candidate P-1 | 2526-2540 (block A F2F sub-block) | 3 (subset of `/api/pa/*` prefix — counted separately below) |
| **Total denominator (F11 lock)** | | | **34** |

**Full inventory table at §6.**

### 3.2 drf-spectacular infrastructure state at HEAD

Inherited baseline from S2501 §3.1 (verified at HEAD `7ddd8ce6`):

| Entry Point | Location | State |
|---|---|---|
| Python package | `drf-spectacular==0.28.0` | INSTALLED (`requirements.txt`) |
| Settings block | `SPECTACULAR_SETTINGS = {...}` | 4 keys — TITLE, DESCRIPTION, VERSION, `SERVE_INCLUDE_SCHEMA=False` (`core/settings.py:1600-1605`) |
| INSTALLED_APPS registration | `'drf_spectacular'` in `INSTALLED_APPS` | **ABSENT** (grep returned 0 matches at `core/settings.py:161-215`) |
| URL route | `SpectacularAPIView` / `SpectacularSwaggerView` / `SpectacularRedocView` | **ABSENT** (grep returned 0 matches across `core/urls.py`) |
| Management command | `python manage.py spectacular` | UNKNOWN COMMAND (inherited S2501 evidence) |

**Consequence at PA-path:** the DECORATOR-INERT baseline from S2501 applies to PA-path endpoints — even if `@extend_schema` were retrofitted onto PA views, the decorator would remain inert at the runtime schema-generation layer without wire-up prerequisite closure at Group 2500 platform scope.

### 3.3 F8 baseline codification test at `/api/pa/chat/` (Chris CLAUDE.md canonical entry)

Cat A opening turn 1 verifier check per F8 fold (shape-card ratification 2026-07-06 wholesale) — check whether `/api/pa/chat/` has ANY documented OpenAPI presence outside `@extend_schema`:

| Check | Result | Evidence |
|---|---|---|
| Docstring OpenAPI operationId annotation | NEGATIVE | `core/views_personal_assistant.py:267-289` docstring contains Request/Response body examples but no `operationId:` or drf-yasg markup |
| External OpenAPI YAML alignment | NEGATIVE | `find . -name "*.yaml" -o -name "*.yml" | xargs grep -l "paths:"` returned only `.github/workflows/*.yml` CI templates; no repo-level API YAML |
| Custom `bpaas_schema`-style hand-emitted endpoint | NEGATIVE | Grep for `bpaas_schema|schema_endpoint` in `core/urls.py` returned only `path('api/bpaas/schema/', bpaas_schema, ...)` (custom bet-agent schema, not PA-path) |
| `@extend_schema` decorator on `unified_pa_chat` | NEGATIVE | 0 `@extend_schema` across `core/views_personal_assistant.py` (verified 2026-07-06) |

**F8 verdict: NEGATIVE at HEAD.** Path C-pure (defer platform-wide without PA-island) is strictly-worse relative to Path C+island (defer platform-wide but declare minimum PA-island on `/api/pa/chat/`) for the S2699 xx99 Chris-D-verdict. Cat A records this evidence; Cat A does NOT recommend verdict per boundary discipline.

## 4. Major Models

**Playbook §9 canonical Q4-Q5 — What are the major models + how do they relate?**

**Cat A boundary: DRF Serializer / model-binding inventory as contract DECLARATION artifacts** (not PA persistence models themselves — those are inventoried in `docs/topics/personal-assistant.md` + Group 1300 Memory arc for auto-memory + parent scoping §2.1 baseline).

### 4.1 Serializer coverage at PA-path endpoints

Per Explore Agent 1 (Models + Persistence) + Agent 3 (APIs) cross-verified evidence:

| Serializer class | File:line | Model | Used by PA endpoint |
|---|---|---|---|
| `PaMessageFeedback` | `core/serializers_*.py` (referenced at `/api/pa/feedback/` line 751) | `PaMessageFeedback` | `POST /api/pa/feedback/` (line 2510) |

**Cat A boundary observation:** 1 serializer across 34 PA-path endpoints = **~2.9% serializer coverage rate at HEAD**. This is materially LOWER than Group 2500 platform-wide 91/563 = ~16.2% model → serializer rate per S2501 §4.2 — PA subsystem has undercovered serializer declaration.

### 4.2 PA-owned persistence models (contract-declaration-relevant subset)

Full PA persistence inventory is out of Cat A scope (belongs to `docs/topics/personal-assistant.md` + parent scoping §2.1). Cat A records only models whose fields are exposed at REST-boundary response bodies:

| Model | File:line | REST-exposed via | Contract-declaration state |
|---|---|---|---|
| `ChatConversation` | `core/models/conversations/models.py:59` | `GET /api/pa/conversations/`, `/<conv_id>/`, `/<conv_id>/messages/` | Field-shape declared via view code hand-construction; NO ModelSerializer binding |
| `ConversationMemory` | `core/models/conversations/models.py:19` | Indirect via `/api/pa/chat/` message flow | Not directly REST-exposed; internal to agentic loop |
| `AgentFollowupSubscription` | `core/models_unified_system.py:1017` | Indirect via task-status polling | Not directly REST-exposed; internal to async coordination |
| `AgentExecution` | `core/models_unified_system.py:882` | Indirect via ToolCallRecord telemetry (S1115) | Not directly REST-exposed at PA-path |
| `PaMessageFeedback` | `core/serializers_*.py` (referenced) | `POST /api/pa/feedback/` | **ONLY PA model with ModelSerializer binding** |
| `FleetPAChatAuditRow` | `core/models/fleet.py:570` | Not REST-exposed (internal audit) | Not applicable at PA-path REST boundary |

**Cat A boundary observation:** REST-exposed PA models (ChatConversation) have NO declared ModelSerializer binding. Response shape is hand-constructed via view code inline dict building at `list_pa_conversations`, `get_pa_conversation`, `pa_conversation_messages` — no declaration artifact for schema consumers.

## 5. Major Services

**Playbook §9 canonical Q4-Q5 — What are the major services?**

**Cat A boundary: services participating in REST response construction, not PA behavior services.**

Per Explore Agent 2 (Services) + parent-Claude verifier-corrected 8-service enrichment count.

**Unit-of-measure note (S3 SIGN cycle 1 fold — verifier clarification):** In this audit, "enrichment services = 8" is counted by **runtime registry entries** in `INTENT_ENRICHMENT_MAP` at `core/services/unified_pa_entrypoint.py:244` (declaration/mechanism-adjacent evidence), NOT by counting `*Enricher` class definitions or files. Agent 2's "3 confirmed" reflects a class/file-count lens and is not the unit used for Cat A evidence. This unit-of-measure discipline applies wherever Cat A cites integration-registry or dispatch-registry counts.


| Service | File:line | Role at REST-boundary |
|---|---|---|
| `UnifiedPAEntrypoint` | `core/services/unified_pa_entrypoint.py:216` | Main PA orchestrator invoked from `/api/pa/chat/` (async via Celery). Owns response construction of `PAResponse` dataclass (line 194). |
| `ToolDispatcher` | `core/services/tool_dispatcher.py:194` | 156 tool handlers via mixin delegation. Executes LLM function-calling directives. `ToolResult` dataclass carries latency + trace_id + structured error. |
| `PAResponse` | `core/services/unified_pa_entrypoint.py:194` (dataclass) | **Verified EXISTS** (verifier correction against Agent 5 CRITICAL drift claim). Fields: content, trace_id, tool_runs, audio_url, intent, routed_to, profile_completeness, latency_ms, error, tool_call_metadata, tool_result_data, response_id, lane. |
| `AnthropicClientFactory` | `core/services/anthropic_client_factory.py:53` | Provider factory with 20/90/60/60s connect/read/write/pool timeouts (per MEMORY `feedback_anthropic_client_factory.md`). |
| `OpenAIClientFactory` | `core/services/openai_client_factory.py` | Provider factory + gpt-5.x reasoning-contract guard (per MEMORY `feedback_openai_client_factory.md` + `feedback_gpt5_max_completion_tokens_floor.md`). |
| `FleetSignatureAuthentication` | `core/services/fleet_auth_drf.py:153` | Auth mixin: verifies X-Fleet-Signature; sets `request.fleet_identity`; returns None (side-effect only). Runs FIRST in PA endpoint auth chain. |
| Enrichment services (8 total per `INTENT_ENRICHMENT_MAP` at `core/services/unified_pa_entrypoint.py:244`) | Various | `advisor` / `blog_performance` / `domain_context` / `intelligence_enricher` / `platform_briefing` / `proactive_intelligence` / `spider_trends` / `strategic_memory` — intent-triggered; inject payload into PA context pre-LLM-call. |

**Cat A boundary observation:** `PAResponse` dataclass is the internal typed shape, but NEVER referenced at REST-boundary declaration surface (no OpenAPI schema binding; no serializer). The type information is present at PA layer but does NOT propagate to schema consumers — Cat B S2602 owns the client-side reconstruction decision.

## 6. Major APIs and Interfaces — F11 Canonical Endpoint Inventory (AC-A2 canonical artifact)

**Playbook §9 canonical Q6 — What are the major APIs?**

**AC-A2 discipline (F7 fold):** This table is the **canonical artifact** for Group 2600 PA arc. Later sessions (Cat B S2602 / Cat C S2603 / Cat D S2604 / S2699 xx99) must NOT re-inventory PA-path endpoints — cite this table.

**Denominator (F11 lock):** 34 PA-path URL patterns at HEAD `7ddd8ce6`.

**Epistemic grade note (S5 SIGN cycle 1 fold):** "Envelope shape" cells in the §6.1 table are **code-derived observed JSON shapes** (hand-constructed dicts), NOT schema-declared artifacts (no serializers / no OpenAPI). Cells marked with observed literals reflect what the view code emits at HEAD; they are evidence at the "inferred-from-code" epistemic grade, not the "declared-via-schema" grade. This distinction is Cat A boundary discipline: observed heterogeneity is evidence; consistency-across-endpoints as declaration is UNKNOWN pre-Path A/B verdict.

### 6.1 F11 Canonical PA-Path Endpoint Inventory Table

| # | Method | Path | View | View file:line | URL file:line | `@extend_schema` | Serializer | permission_classes | Envelope shape | 401 shape | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | GET | `/api/v1/assistant/context/` | `assistant_context` | `core.views/__init__.py?` (aggregator) — **UNKNOWN def site** | `core/urls.py:2485` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "context": {...}}` (inferred) | DRF default `{"detail"}` | v1 compat; view def-site UNKNOWN (verifier next-step: trace `core.views` package aggregator) |
| 2 | POST | `/api/v1/assistant/chat/` | `assistant_chat` | `core/views_image_tools.py:60` | `core/urls.py:2486` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "response": "..."}` | DRF default | v1 legacy GPT-5 chat endpoint |
| 3 | POST | `/api/assistant/chat/` | `assistant_chat_bypass` | `core/views_assistant_bypass.py:34` | `core/urls.py:2490` | ABSENT | hand-dict | IsAuthenticated | `{"success": True/False, "response": "..."/"error": "..."}` | bare dict (401 if not authed) | Compat endpoint; bypasses Django session/cache; uses UnifiedPAEntrypoint |
| 4 | POST | `/api/assistant/transcribe/` | `transcribe_audio` | `core/views_image_misc.py:3973` | `core/urls.py:2491` | ABSENT | hand-dict | IsAuthenticated | `{"text": "..."}` | bare dict | S64: Whisper API transcription |
| 5 | POST | `/api/assistant/voice/` | `voice_to_assistant` | `core/views_personal_assistant.py:1014` | `core/urls.py:2492` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "response": "..."}` | DRF default | S113: Voice input MVP; STT then PA dispatch |
| 6 | GET | `/api/assistant/preferences/` | `get_user_preferences_api` | `core/views_image_misc.py:2470` | `core/urls.py:2494` | ABSENT | hand-dict | IsAuthenticated (implicit) | `{"has_history": bool, "favorite_workflow": {...}, "favorite_styles": [...]}` | bare dict | Workflow personalization data |
| 7 | GET | `/api/assistant/context/` | `get_assistant_context` | `core/views_personal_assistant.py:132` | `core/urls.py:2495` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "context": {...}}` | DRF default | Compat context read |
| 8 | GET | `/api/assistant/learning/` | `get_learning_summary` | `core/views_personal_assistant.py:225` | `core/urls.py:2496` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "learning": {...}}` | DRF default | Learning summary + insights |
| 9 | GET | `/api/assistant/task-progress/` | `get_task_progress` | `core/views_assistant_bypass.py:226` | `core/urls.py:2497` | ABSENT | hand-dict | IsAuthenticated (implicit) | `{"task": {...} | null}` | bare dict (401 if not authed) | Task progress polling; plain JSON not DRF |
| 10 | POST | `/api/assistant/bypass/` | `assistant_chat_bypass` (alias) | `core/views_assistant_bypass.py:34` | `core/urls.py:2500` | ABSENT | hand-dict | IsAuthenticated | Same as row 3 | Same as row 3 | **Alias route** (same view as row 3); double-count denominator |
| 11 | POST | `/api/assistant/feedback/` | `provide_feedback` | `core/views_personal_assistant.py:921` | `core/urls.py:2501` | ABSENT | hand-dict | IsAuthenticated | `{"success": True}` | DRF default | Feedback on assistant responses |
| 12 | POST | `/api/assistant/reset/` | `reset_assistant` | `core/views_personal_assistant.py:978` | `core/urls.py:2502` | ABSENT | hand-dict | IsAuthenticated | `{"success": True}` | DRF default | Reset assistant state/memory |
| 13 | GET | `/api/assistant/attention-items/` | `get_attention_items` | `core/views_personal_assistant.py:1318` | `core/urls.py:2503` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "items": [...]}` | DRF default | S574: Items requiring user attention |
| 14 | GET | `/api/assistant/attention/unified/` | `get_unified_attention` | `core/views_personal_assistant.py:1411` | `core/urls.py:2505` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "attention": {...}}` | DRF default | S932: Combines system + human attention |
| 15 | GET | `/api/assistant/attention/stats/` | `get_attention_stats` | `core/views_personal_assistant.py:1484` | `core/urls.py:2506` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "stats": {...}}` | DRF default | Attention aggregation |
| 16 | POST | `/api/pa/chat/` | `unified_pa_chat` | `core/views_personal_assistant.py:267` | `core/urls.py:2508` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "task_id": "<uuid>", "status": "processing"}` | DRF default | **CANONICAL PA ENTRY** (CLAUDE.md); async task dispatch to `pa` Celery queue; task-status polling contract; S932/S974b |
| 17 | GET | `/api/pa/chat/status/<str:task_id>/` | `pa_chat_status` | `core/views_personal_assistant.py:785` | `core/urls.py:2509` | ABSENT | N/A | IsAuthenticated | `{"success": T/F, "status": "completed|failed|processing", **task_result}` | bare dict | Celery AsyncResult polling; PENDING → fail (stop polling) |
| 18 | POST | `/api/pa/feedback/` | `pa_message_feedback` | `core/views_personal_assistant.py:744` | `core/urls.py:2510` | ABSENT | **`PaMessageFeedback`** | IsAuthenticated | `{"success": True, "id": "...", "rating": ±1}` | bare dict | **ONLY PA endpoint with ModelSerializer**; S1085/S1243 |
| 19 | GET | `/api/pa/context/` | `unified_pa_context` | `core/views_personal_assistant.py:832` | `core/urls.py:2511` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "user": {...}, "system_stats": {...}, "available_tools": [...]}` | DRF default | S932: PA context for next message |
| 20 | GET | `/api/pa/conversations/` | `list_pa_conversations` | `core/views_personal_assistant.py:1522` | `core/urls.py:2513` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "conversations": [...], "total": N}` | DRF default | S974: Lists PA conversation sessions |
| 21 | POST | `/api/pa/conversations/new/` | `create_pa_conversation` | `core/views_personal_assistant.py:1688` | `core/urls.py:2514` | ABSENT | N/A | IsAuthenticated | `{"success": True, "conversation_id": "pa-..."}` | DRF default | S974: Generates conversation_id (no DB row) |
| 22 | GET | `/api/pa/conversations/<str:conversation_id>/` | `get_pa_conversation` | `core/views_personal_assistant.py:1591` | `core/urls.py:2515` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "conversation_id": "...", "title": "...", "messages": [...]}` | DRF default | S974: Loads all messages |
| 23 | POST | `/api/pa/conversations/<str:conversation_id>/message/` | `pa_conversation_post_message` | `core/views_personal_assistant.py:521` | `core/urls.py:2517` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "id": "..."}` | DRF default | 3-way chat: store-only unless trigger_pa=true; WS broadcast |
| 24 | GET | `/api/pa/conversations/<str:conversation_id>/messages/` | `pa_conversation_messages` | `core/views_personal_assistant.py:630` | `core/urls.py:2518` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "conversation_id": "...", "messages": [...], "count": N}` | DRF default | CLI watch mode; incremental ?after=<msg_id> |
| 25 | GET | `/api/pa/activity/` | `pa_activity_feed` | `core/views_personal_assistant.py:688` | `core/urls.py:2520` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "total_calls": N, "tool_breakdown": {...}, "recent_calls": [...]}` | DRF default | Rigby accountability feed (ToolCallRecord source) |
| 26 | GET | `/api/pa/conversations/<str:conversation_id>/health/` | `session_health` | `core/views_personal_assistant.py:1715` | `core/urls.py:2522` | ABSENT | hand-dict | IsAuthenticated | `{"success": True, "score": 0-100, "recommendation": "...", "reasons": [...]}` | DRF default | Session health freshness score |
| 27 | POST | `/api/pa/boardroom/maintenance/` | `trigger_boardroom_maintenance` | `core/views_personal_assistant.py:1737` | `core/urls.py:2524` | ABSENT | hand-dict | IsAuthenticated (staff only) | `{"success": True, "total_processed": N, "details": {...}}` | DRF default (403 if not staff) | S977: Staff-only boardroom cleanup |
| 28 | POST | `/api/pa/voice_session/` | `f2f_create_voice_session` | `core/views_f2f.py:121` | `core/urls.py:2526-2530` (multi-line) | ABSENT | hand-dict | IsAuthenticated | `{"session_id": UUID, "offer": WebRTC SDP, ...}` | `{"error_code": "F2F_*", "message": ...}` | S1118 F2F.2: F2F session allocation (WebRTC offer) |
| 29 | POST | `/api/pa/voice_session/<uuid:session_id>/speak/` | `f2f_speak_voice_session` | `core/views_f2f.py:193` | `core/urls.py:2531-2535` (multi-line) | ABSENT | hand-dict | IsAuthenticated | `{"session_id": UUID, "chars_spoken": N, "cost_cents": N}` | `{"error_code": "F2F_CAP_EXCEEDED_*|F2F_SESSION_NOT_ACTIVE", ...}` | S1118: 402 on cap trip; 410 on terminal |
| 30 | POST | `/api/pa/voice_session/<uuid:session_id>/end/` | `f2f_end_voice_session` | `core/views_f2f.py:256` | `core/urls.py:2536-2540` (multi-line) | ABSENT | hand-dict | IsAuthenticated | `{"session_id": UUID, "status": "...", "total_chars_spoken": N, "total_cost_cents": N}` | `{"error_code": "F2F_SESSION_NOT_FOUND", ...}` | S1118: Idempotent teardown |
| 31 | POST | `/api/assistant/dev/chat/` | `chat_with_assistant_dev` | `core/views_personal_assistant_dev.py:?` (dev module) | `core/urls.py:4900` | ABSENT | hand-dict | UNKNOWN (dev variant) | UNKNOWN | UNKNOWN | Dev route; module `core/views_personal_assistant_dev.py` exists (imported line 1096) but view file:line UNKNOWN — verifier next-step |
| 32 | GET | `/api/assistant/dev/context/` | `get_assistant_context_dev` | `core/views_personal_assistant_dev.py:?` | `core/urls.py:4901` | ABSENT | hand-dict | UNKNOWN | UNKNOWN | UNKNOWN | Dev route (paired with row 31) |
| 33 | POST | `/api/assistant/minimal/chat/` | `chat_minimal_dev` | `core/views_personal_assistant_dev.py:?` | `core/urls.py:4902` | ABSENT | hand-dict | UNKNOWN | UNKNOWN | UNKNOWN | Minimal dev route |
| 34 | GET | `/api/assistant/minimal/context/` | `context_minimal_dev` | `core/views_personal_assistant_dev.py:?` | `core/urls.py:4903` | ABSENT | hand-dict | UNKNOWN | UNKNOWN | UNKNOWN | Minimal dev route (paired with row 33) |

**Denominator = 34.** Coverage rate for `@extend_schema` = **0/34 = 0.00%**. Coverage rate for ModelSerializer = **1/34 = ~2.9%** (PaMessageFeedback only). Coverage rate for OpenAPI operationId outside `@extend_schema` = **0/34 = 0.00%** (F8 baseline).

### 6.2 Per-endpoint disposition column (AC-A1 measurability)

**Boundary note (S2 SIGN cycle 1 fold — anti-verdict):** The "Path A / Path B / Path C+island" labels below are **evidence-only eligibility categories** computed strictly from declaration artifacts at HEAD, NOT a recommendation and NOT a closure decision. An endpoint being "Path B eligible" means it satisfies the observed declaration criteria for that path at HEAD; it does NOT mean Cat A endorses Path B for that endpoint. Chris-D-verdict on Path A/B/C+island is S2699 xx99 scope after all 4 children contribute evidence.

Per AC-A1 (F5 fold — tightened UNKNOWN with next-step pointer + target 0 UNKNOWN on existence-of-declaration):

| Category | Count | Percentage | Rationale |
|---|---|---|---|
| Path A eligible (retrofit-ready pending drf-spectacular wire-up) | 0 | 0% | 0 endpoints declare `@extend_schema` at HEAD |
| Path B eligible (typed serializer + APIResponseEnvelope conformance without decorator) | 1 | 2.9% | `POST /api/pa/feedback/` has PaMessageFeedback serializer but does NOT use APIResponseEnvelope |
| Path C+island (defer + minimum PA-island on `/api/pa/chat/`) | 33 | 97.1% | All except row 18 (feedback); requires F8 baseline codification decision at S2699 xx99 |
| UNKNOWN (existence-of-declaration) | 0 | 0% | AC-A1 target achieved — every endpoint categorized |
| UNKNOWN (view def-site trace) | 5 | 14.7% | Rows 1 (assistant_context aggregator), 31-34 (dev/minimal variants). **Next-step pointer:** S2602 Cat B opening turn 1 or Cat A follow-up trace of `core/views_personal_assistant_dev.py` + `core.views` package aggregator. UNKNOWN on def-site is non-HEAD runtime; existence-of-declaration is 0 UNKNOWN. |

**AC-A1 measurability = 100% categorized (0 UNKNOWN on existence-of-declaration).** ≥90% threshold met with margin. AC-A2 canonical artifact = §6.1 table.

### 6.3 PA tool schemas + handlers (adjacent to REST-boundary)

Verifier-corrected counts (Explore Agent 3 grep artifact reconciled):
- **PA_TOOL_SCHEMAS list at `core/services/pa_tool_schemas.py`: 113 schemas** (matches PLATFORM_INVENTORY.md autoblock line 18).
- **ToolDispatcher registered handlers at `core/services/tool_dispatcher.py:194+`: 156 handlers** (matches PLATFORM_INVENTORY.md; Agent 6 confirmed via `ToolDispatcher: Registered 156 tool handlers` log line).
- **Schema versioning:** `SCHEMA_VERSION` at `pa_tool_schemas.py:19` — for live-reload detection only. No external schema.json export mechanism observed (evidence gap; §14 drift).

### 6.4 PA Celery tasks (`pa` queue)

- `process_pa_chat_task` — dispatched from `core/views_personal_assistant.py:462`; runs UnifiedPAEntrypoint agentic loop async; time_limit=300s, soft_limit=280s.
- `rebuild_pa_context_task` — `core/tasks.py:11919` (bind=True); rebuilds PA context caches with lock-based stampede prevention.
- `expire_stale_followup_subscriptions` — `core/tasks.py:13444`; beat-scheduled cleanup for AgentFollowupSubscription rows.

### 6.5 PA management commands

- `build_pa_tool_audit` — cross-checks schemas vs handlers; generates `/docs/PA_TOOL_AUDIT.md`.
- `pa_acks_health` — Celery `pa` queue health snapshot (S1160+).
- `setup_pa_service_account` — PA identity provisioning.
- `migrate_pa_identity` — legacy identity migration.

### 6.6 Discord bot @app_commands proxy boundary

Per Explore Agent 3 + Agent 4 confirmation: **NO Discord bot `@app_commands.command` wrappers proxy through `/api/pa/*` endpoints** at HEAD. Discord bot operates as sibling PA-adjacent subsystem; boundary preserved per parent §7 anti-scope #5.

## 7. Runtime Flows

**Playbook §9 canonical Q9 — What are the major runtime flows?**

**Cat A boundary: REST-boundary flow contract, not internal PA agentic-loop behavior.**

### 7.1 `/api/pa/chat/` async task-based flow (10-step)

Verifier-corrected from Explore Agent 2 (with §6 table cross-reference):

1. **HTTP POST `/api/pa/chat/`** — Client sends message body. Auth chain: FleetSignatureAuthentication (side-effect only) + SessionAuthentication + TokenAuthentication; `@permission_classes([IsAuthenticated])`.
2. **Request validation** — `unified_pa_chat` at `core/views_personal_assistant.py:267` validates message (non-empty, ≤8000 chars). Applies VIP scope + fleet routing block per S1129.
3. **Fleet auth audit (S1132 warn-only)** — If X-Fleet-Signature present, verify + record `FleetPAChatAuditRow`.
4. **Celery task dispatch** — `process_pa_chat_task.delay(...)` to `pa` queue (async). Returns HTTP 200 immediately with `{"success": True, "task_id": "<uuid>", "status": "processing"}`.
5. **Celery worker: UnifiedPAEntrypoint init** — `core/tasks_misc.py:4757-4758` creates `UnifiedPAEntrypoint(user, conversation_id=...)`.
6. **PA agentic loop** — `UnifiedPAEntrypoint.process_message()` at `core/services/unified_pa_entrypoint.py:552`. Runs LLM function-calling iterations with tool dispatch (ITERATION_CAP guardrail). Enrichment services (8 per INTENT_ENRICHMENT_MAP) injected pre-LLM.
7. **Response construction** — Returns `PAResponse` dataclass (fields: content, trace_id, tool_runs, audio_url, intent, routed_to, profile_completeness, latency_ms, error, tool_call_metadata, tool_result_data, response_id, lane).
8. **Celery worker: Persist to DB** — `ChatConversation` row stored with metadata (trace_id, intent, routed_to, tool_calls, tool_results, source, lane).
9. **Client polls `/api/pa/chat/status/<task_id>/`** — `pa_chat_status` at line 785. Reads Celery AsyncResult via Redis backend.
10. **Status response** — `{"success": True, "status": "completed", **task_result}` (200) OR `{"success": False, "status": "failed", "error": "..."}` (200) OR `{"success": True, "status": "processing"}` (200) OR 500 on exception.

### 7.2 Streaming semantics (Cat A §3.5 parent probe evidence)

**CONFIRMED NEGATIVE** at all PA-REST endpoints:
- No SSE (Server-Sent Events).
- No chunked-transfer-encoding.
- No WebSocket at any PA-REST endpoint (WS is Cat D S2604 scope for separate PA-related WS channels).
- All PA responses are complete, buffered JSON via DRF `Response()` or plain JSON via `assistant_chat_bypass`.
- `/api/pa/chat/` is **task-based async with polling contract**, NOT streaming async.

**Evidence for AC#8 T7 cross-transport consistency check (F12 fold):** REST-side statement is "task-based async; NO streaming." Cat D S2604 owns WS-side statement. S2699 xx99 synthesizes cross-transport consistency rule.

### 7.3 Response envelope shape flow at PA-path

Response construction sites at `core/views_personal_assistant.py`:

| Location | Shape | HTTP Status | Comment |
|---|---|---|---|
| line 489-493 | `{"success": True, "task_id": "...", "status": "processing"}` | 200 | `/api/pa/chat/` task_id return |
| line 799-803 | `{"success": True, "status": "completed", **task_result}` | 200 | Task complete + unpacked PAResponse |
| line 805-809 | `{"success": False, "status": "failed", "error": "..."}` | 200 | Task failed (200 status per polling contract) |
| line 814-818 | `{"success": False, "status": "failed", "error": "Task not found or result expired..."}` | 200 | PENDING → fail (S1076 pattern) |
| line 820-823 | `{"success": True, "status": "processing"}` | 200 | Still processing |
| line 827 | `{"success": False, "error": "..."}` | 500 | Exception during status check |

**Critical envelope invariant across all PA-REST:** `{"success": bool, ...}` shape uniformly (not `APIResponseEnvelope` shape at any PA-path endpoint). This diverges from `APIResponseEnvelope.success/error()` shape declared at `core/api_responses.py:53-98` (9 usages platform-wide per S2501 §14 — **zero adopted at PA-path**).

## 8. Data Ownership and Lifecycle

**Playbook §9 canonical Q16-Q18 — What data does PA own / consume / produce?**

**Cat A boundary: data exposed via REST-boundary contract, not internal persistence.**

### 8.1 PA REST-boundary data owned

- ChatConversation rows (owned by PA; readable via `/api/pa/conversations/*`)
- PaMessageFeedback rows (owned by PA; writable via `/api/pa/feedback/`)
- PA tool schemas (owned by PA; NOT REST-exposed — internal to PA agentic loop)

### 8.2 PA REST-boundary data consumed

- User profile (read from Auth-owned models via `IsAuthenticated` chain)
- Workspace context (read from Workspace-owned models via `execute_with_workspace()` handler-internal check — F-B-HIGH-3 implicit-gate location)
- Agent registry (read from Agent System via AGENT_MAP dispatch)

### 8.3 PA REST-boundary data produced

- ChatConversation persistence (write to Memory-adjacent tables)
- ToolCallRecord telemetry (write to observability layer via S1115 dispatcher pattern)
- FleetPAChatAuditRow (write to fleet audit table per S1132 warn-only)
- AgentFollowupSubscription (write to async coordination table per S1174 PR-2a)

### 8.4 Retention / lifecycle policies

- `AgentFollowupSubscription` DEFAULT_TTL_SECONDS=60, MAX_TTL_SECONDS=600 (line 1064-1065). Beat cleanup at `expire_stale_followup_subscriptions` (`core/tasks.py:13444`).
- `ChatConversation` — no explicit TTL; lifetime indefinite unless archived (session_active flag).
- `FleetPAChatAuditRow` — no explicit TTL; warn-only audit (S1132).
- **Cat A boundary observation:** no retention-window declaration surface at REST-boundary. Cat C2 S2603 owns session-lifecycle contract disposition.

## 9. Integrations With Other Domains

**Playbook §9 canonical Q14 + Q17 + Q18 + Q21 + Q22 — Integrations.**

Per Explore Agent 4 verifier-cross-checked evidence:

| Domain | Mechanism | File:line origin | Strength | Cat A boundary evidence |
|---|---|---|---|---|
| Agent System | Function dispatch via AGENT_MAP + WORKSPACE_AWARE_AGENTS (20 agents) | `core/agent_router.py:320`; `core/epa_handlers_tools.py:191-217` | STRONG | REST layer surfaces `available_tools` list at `/api/pa/context/`; internal dispatch is not REST-boundary |
| Auth | DRF `IsAuthenticated` DEFAULT + FleetSignatureAuthentication side-effect | `core/views_personal_assistant.py:31-32, 255-266`; `core/services/fleet_auth_drf.py` | STRONG | All 34 PA-path endpoints declare `IsAuthenticated`; NO explicit `WorkspaceMember` at REST boundary |
| Workspace | `execute_with_workspace()` handler-internal check | `core/agents/base_agent.py:5355` | **WEAK (F-B-HIGH-3 implicit-gate)** | No HTTP/DRF layer enforcement; Cat C1 S2603 owns Path A/B/C+compensating verdict |
| Memory | UnifiedMemoryManager integration + auto-memory fallback | `core/epa_handlers_tools.py:21-25`; `core/services/unified_pa_entrypoint.py:697-718` | STRONG | Not REST-boundary-relevant (internal to agentic loop) |
| Content | NOT FOUND (anti-scope #6 boundary preserved) | N/A | UNKNOWN | Verified: no `content` domain imports in PA views |
| Discord | NOT FOUND (anti-scope #5 boundary preserved) | N/A | UNKNOWN | Verified: no `@app_commands` wrappers proxy through `/api/pa/*` |
| Frontend consumers | assistantApi + paStore + tools/pa_chat.py CLI | UNKNOWN (U6/U7 evidence gaps preserved to S2602 opening) | WEAK/UNKNOWN | 7.36% platform-wide typed rate; PA-path 0 `@extend_schema`; consumer typing decision is Cat B S2602 scope (F1 hard boundary) |

**F13 parallel evidence-collection permitted (parent §5.1 fold):** Cat B (U6 WS envelope + U7 paStore) + Cat D (PA-related WS channels + Consumer classes) MAY inventory in parallel with S2601 close. Inventory-only; no option enumeration until Cat A verdict at S2699 xx99.

## 10. Event Flows

**Playbook §9 canonical Q19-Q20 — What events emitted / should be emitted?**

**Cat A boundary: REST-boundary event contracts, not internal PA event bus.**

### 10.1 PA REST-boundary events currently declared

- `ToolCallRecord` telemetry emission via S1115 dispatcher pattern (indirect; observable via `/api/pa/activity/`).
- `FleetPAChatAuditRow` emission on `/api/pa/chat/` per-call (S1132 warn-only; not REST-boundary-visible directly).
- WebSocket broadcast via `pa_conversation_post_message` (`core/views_personal_assistant.py:521`) for 3-way chat sync — cross-domain boundary to Cat D S2604 WS-side scope.

### 10.2 PA REST-boundary events that SHOULD be emitted (evidence for §19)

- Per-request contract-declaration compliance metric (analog to Group 1700 Observability handoff). Currently 0 endpoints emit compliance signal.
- Per-endpoint response-envelope shape telemetry (would surface `APIResponseEnvelope` adoption gap).

## 11. Existing Documentation

**Playbook §9 canonical Q10-Q11 — Existing documentation + prior research.**

Per Explore Agent 5 (Documentation) cross-verified:

| Doc | File:line | Owner class | PA contract-declaration coverage |
|---|---|---|---|
| `docs/topics/personal-assistant.md` | 1-148 | narrative | CANONICAL PA topic doc; describes agentic loop + tool schemas + enrichment services; **does NOT declare endpoint contract SoT** (F11 canonical artifact §6 fills this gap) |
| `docs/PLATFORM_WHAT_IT_IS.md` | 188-225 | narrative | PA subsystem anchor point; inventory table (113 tools + 8 enrichment + 20 WORKSPACE_AWARE_AGENTS) |
| `docs/PLATFORM_INVENTORY.md` | 18, 42, 888-896, 1277, 1380, 1632-1633 | runtime | Authoritative PA inventory counts |
| `CLAUDE.md` | 7-36, 94-104, 212, 223 | narrative | PA operational anchor; **canonical route declaration `POST /api/pa/chat/` (F8 baseline evidence)** |
| `docs/research/domains/pa/2600_pa_domain_scoping.md` | full | research | DIRECT PARENT — §2.6.A/B lens + §3.A Cat A scope + §5.3 AC |
| `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` | full | research | PARENT-ARC PREDECESSOR — Cat A boundary template + 3-co-existing-401-shapes evidence |
| `docs/research/domains/api/2599_api_canonical_summary.md` | full | research | Group 2500 API canonical verdict — §2.6.A hard constraint |

## 12. Research Coverage

**Playbook §12 classification.**

**PA CONTRACT-DECLARATION LAYER research coverage at S2601 close: MODERATE (upgrading toward DEEP as Group 2600 arc closes).**

Evidence:
- `docs/topics/personal-assistant.md` describes PA MECHANISM + TOOL SCHEMA INTERNAL STRUCTURE in DEEP depth; DECLARATION LAYER at MODERATE.
- Prior Group 2500 arc (S2501 Cat A + S2504 Cat D) provides adjacent DEEP evidence.
- This audit (S2601) contributes DEEP evidence for REST-boundary declaration.
- Cat B (S2602) + Cat C (S2603) + Cat D (S2604) will complete Group 2600 arc — expected DEEP at arc close.

## 13. Architecture Maturity

**Playbook §12 classification.**

**PA CONTRACT-DECLARATION LAYER architecture maturity at HEAD `7ddd8ce6`: EXPERIMENTAL.**

Rationale (evidence-only per Cat A boundary):
- **EXPERIMENTAL best-fit:** PA CONTRACT declaration exists at MULTIPLE DISJOINT LAYERS — tool schemas internally valid (mechanism-layer functional); REST endpoints uniformly undecorated (declaration-layer inert); middleware gates implicit at handler-internal only (workspace-authz-layer implicit); enrichment services hardcoded not exported (integration-layer opaque). These layers are NOT unified into a single source-of-truth surface.
- **Distinction from PARTIAL:** PARTIAL would mean "infrastructure + some decoration"; EXPERIMENTAL means "working at runtime but declaration fragmented across incompatible surfaces."
- **Not WORKING:** would require observable declaration surface. 0/34 `@extend_schema` at REST-boundary blocks WORKING classification for DECLARATION.

**Distinguish from MECHANISM-layer maturity:** PA MECHANISM (agentic loop + tool dispatch + enrichment + async coordination) is WORKING or STABLE — that's a different question owned by parent scoping §2 baseline + `docs/topics/personal-assistant.md`. Cat A owns DECLARATION-layer classification only.

## 14. Known Drift

**Playbook §9 canonical Q27 — Drift.**

### 14.1 Drift resolved by verifier-loop pre-draft

- **PAResponse class existence drift (Agent 5 CRITICAL claim):** Agent 5 reported `PAResponse` class "does not exist" and labeled `docs/topics/personal-assistant.md` reference to it CRITICAL drift. **Verifier correction:** `class PAResponse` at `core/services/unified_pa_entrypoint.py:194` (dataclass). Doc reference is ACCURATE; NO drift.

### 14.2 Drift confirmed at HEAD

- **Tool schema count in `docs/topics/personal-assistant.md`:** doc claims "104 OpenAI function-calling tool schemas" at line 6 (2026-05-25 snapshot). Actual at HEAD `7ddd8ce6`: **113 schemas** (PLATFORM_INVENTORY.md autoblock line 18). Drift = +9 schemas (accumulation since 2026-05-25). Severity MEDIUM (doc carries explicit drift warning + PLATFORM_INVENTORY authority deference).
- **Handler count in `docs/topics/personal-assistant.md`:** doc claims "169 registered handlers"; PLATFORM_INVENTORY says 156. Drift = -13 handlers. Severity MEDIUM.
- **Enrichment services count in Agent 2 report:** Agent 2 reported "3 confirmed" enrichment services; PLATFORM_INVENTORY says 8 in INTENT_ENRICHMENT_MAP. Verifier confirmed 8 (per Agent 6 correct enumeration). Not drift in doc; drift in Agent 2 interpretation.
- **Response envelope declaration:** `docs/topics/personal-assistant.md` line 26 references "return PAResponse" — PAResponse EXISTS (§14.1 resolution) but the docs section does NOT declare that PAResponse is a Python-internal dataclass NOT propagated to REST-boundary schema. Documentation gap (not drift): PAResponse propagation to REST layer is UNDOCUMENTED.

### 14.3 Drift observation from Agent 6 verify_doc_claims run

- `verify_doc_claims` at HEAD `7ddd8ce6` reports NO DRIFT on PA claims (all registered claim rows MATCHED OK). This is a positive signal for MECHANISM-layer accuracy; DECLARATION-layer drift is not yet in the verifier registry (S2699 xx99 anchor-update recommendation candidate).

## 15. Known Technical Debt

**Playbook §9 canonical Q26 — Technical debt.**

### 15.1 Contract-declaration debt (Cat A boundary scope)

- **DEBT-1:** 34/34 endpoints undecorated at REST boundary. Path A retrofit blocked by drf-spectacular platform-wide wire-up prerequisite (S2501 Cat A evidence). Severity HIGH; owner deferred to Group 2500 platform-wide retrofit + Group 2600 PA-island declaration decision.
- **DEBT-2:** 1/34 endpoints have ModelSerializer coverage (`PaMessageFeedback`). 33/34 hand-construct response dicts. Severity MEDIUM; owner deferred to Cat B S2602 client-side typed decision or Path A/B retrofit.
- **DEBT-3:** 0/34 endpoints adopt `APIResponseEnvelope` at PA-path (envelope declared at `core/api_responses.py:53-98` with 9 usages elsewhere in platform). Severity MEDIUM; consistency debt with the "island exemplar" pattern from Group 2500 S2599.
- **DEBT-4:** `/api/pa/chat/` docstring at `core/views_personal_assistant.py:267-289` contains structured Request/Response examples — human-readable but NOT machine-consumable. Severity LOW; F8 baseline codification NEGATIVE. Path C+island would require converting this to OpenAPI operationId + response schema at minimum.
- **DEBT-5:** `assistant_context` view def-site UNKNOWN (row 1 in §6 table); `core.views` package aggregator not surfaced by top-level grep. Severity LOW; documentation-navigation debt.

### 15.2 Cross-arc coordination debt (adjacent to Cat A)

- **F-B-HIGH-3** workspace-membership implicit-gate at handler-internal only (see §16.1). Cat A records boundary; Cat C1 S2603 owns closure.
- **CF-D6** REST↔WS T7 joint permission-floor + envelope alignment. Cat A records REST-side (task-based async, NO streaming); Cat D S2604 owns WS-side.

## 16. Boundary Violations

**Playbook §9 canonical Q24 — Boundary violations.**

### 16.1 F-B-HIGH-3 workspace-membership implicit-gate (from S2402 preserved)

**Location:** `core/agents/base_agent.py:5355 execute_with_workspace()` — workspace-membership check is INSIDE the handler method only.

**HTTP boundary state at PA-path (34/34 endpoints):**
- `@permission_classes([IsAuthenticated])` at all 34 endpoints (verified via §6.1 inventory).
- **NO explicit `WorkspaceMember` DRF class enforcement.**
- **NO middleware path-list gate** for PA-path (auth_middleware PUBLIC_PATHS ≠ PA-path; PA-path is authenticated but workspace-context is not middleware-gated).

**Classification:** Not a violation per se (implicit-gate is working at RUNTIME per S2402 finding). But contract-DECLARATION at REST boundary DOES NOT declare workspace-membership requirement. Cat A records evidence; **Cat C1 S2603 owns Path A/B/C+compensating verdict per parent §3.C1 + F5 fold closure discipline.** Per Cat C1 F5 fold ownership: Path C-pure without compensating controls is NOT a valid ratification. **Cat A records this Cat-C1-owned constraint as boundary evidence (S7 SIGN cycle 1 fold — attribution clarification); Cat A does not itself pronounce the constraint** — the constraint is Cat C1's to enforce at S2603 closure.

### 16.2 PA-adjacent boundary preservation (anti-scope verification)

Verifier confirmed at HEAD:
- **Anti-scope #5 (Discord bot PA proxy):** NOT VIOLATED — 0 `@app_commands.command` proxy through `/api/pa/*`.
- **Anti-scope #6 (Content Studio PA endpoints):** NOT VIOLATED — no content-domain imports in PA views.
- **Anti-scope #7 (Fleet HMAC PA signature):** FleetSignatureAuthentication is read-only (verifies X-Fleet-Signature header, returns None). NO cross-repo HMAC-write observed at PA-path. Boundary preserved.

## 17. Duplicate or Overlapping Systems

**Playbook §9 canonical Q23 — Duplicate/overlapping systems.**

- **`/api/pa/chat/` + `/api/assistant/chat/` + `/api/v1/assistant/chat/`** — three parallel chat entrypoints. CLAUDE.md declares `/api/pa/chat/` canonical + `/api/assistant/chat/` + `/api/v1/assistant/chat/` as "compatibility-only." **Contract SoT DUPLICATION observed:** three endpoints share overlapping request/response shape but declare it independently (all hand-constructed). **Observation (S6 SIGN cycle 1 fold — Cat A boundary framing):** 3× parallel chat endpoints share overlapping request/response shape; any future Path A/B retrofit would cover 3 declaration surfaces — an observation Cat A records for downstream verdict-space enumeration at S2699 xx99. Cat A does NOT elevate DEBT-2 severity; severity assessment is Chris-D-verdict scope.
- **`/api/assistant/bypass/` alias** — same view (`assistant_chat_bypass`) as `/api/assistant/chat/` at row 3. Deliberate alias; not duplicate.
- **`/api/assistant/dev/*` + `/api/assistant/minimal/*`** — 4 dev/minimal routes at lines 4900-4903. Purpose UNKNOWN (evidence gap; view def-site UNKNOWN). Candidate DEAD-CODE per Group 2500 Cat B S2502 DEAD-CANDIDATE pattern; verifier next-step for Cat B S2602 opening.

## 18. Ownership Gaps

**Playbook §9 canonical Q25 — Ownership gaps.**

Per Explore Agent 6 (CODEOWNERS analysis):

**PA code paths NOT explicitly listed in CODEOWNERS:**
- `core/views_personal_assistant.py` — falls to default `* @clwest`
- `core/services/unified_pa_entrypoint.py` — falls to default
- `core/services/pa_tool_schemas.py` — falls to default
- `core/services/tool_dispatcher.py` — falls to default
- `core/services/pa_intelligence_enricher.py` — falls to default
- `core/services/pa_tool_learning_enricher.py` — falls to default
- `core/services/pa_learning_insights.py` — falls to default
- `core/services/fleet_auth_drf.py` — falls to default
- `core/views_f2f.py` — falls to default
- `core/views_assistant_bypass.py` — falls to default

**PA doc paths EXPLICITLY listed:**
- `/docs/topics/ @clwest` (includes personal-assistant.md)
- `/docs/PLATFORM_INVENTORY.md @clwest` (PA counts anchor)

**Ownership-gap observation:** PA code ownership is via default fallback per S2499 AU-D5 baseline (established at Group 2400 Auth close). Cat A records; **S2699 xx99 anchor-update recommendation candidate:** PA-slice CODEOWNERS discipline (analog to Group 2500 API-slice CODEOWNERS refinement carried in S2599 close residuals).

## 19. Recommended Future Research

**Playbook §9 canonical Q28 — What should be researched next?**

Cat A DOES NOT recommend implementation. Cat A recommends **evidence-collection follow-ons** ranked by architectural uncertainty × risk × unblocked flows:

### 19.1 CRITICAL — Blocks Chris-D-verdict at S2699 xx99

1. **Cat B S2602 evidence-collection on assistantApi + paStore + tools/pa_chat.py consumer typing.** U6 (WS envelope schema) + U7 (paStore field-list) inventory turn 1 — parent §2.5 evidence gaps. F13 fold permits parallel with Cat A close.
2. **Cat C1 S2603 verdict on F-B-HIGH-3 closure (Path A / Path B / Path C+compensating per F5 fold).** Cat A boundary evidence confirmed handler-internal check at `core/agents/base_agent.py:5355`; C1 owns Chris-D-verdict.

### 19.2 HIGH — Enables Chris-D-verdict at S2699 xx99

3. **`/api/pa/chat/` F8 baseline codification decision at Path C+island.** If Chris ratifies Path C+island at xx99, S2701+ session drafts minimum PA-island declaration for CLAUDE.md canonical entry (OpenAPI operationId + request/response schema at least).
4. **Response envelope shape unification decision.** All 33 hand-constructed vs 1 PaMessageFeedback serializer vs 9 platform-wide APIResponseEnvelope adoption points. Chris-D-verdict at xx99 sets direction.

### 19.3 MEDIUM — Post-arc follow-on

5. **`assistant_context` view def-site trace.** UNKNOWN aggregator location (`core.views` package); trace for row 1 §6 table completion.
6. **Dev/minimal routes (rows 31-34) purpose + DEAD-CODE candidacy assessment.** Cat B S2602 opening or dedicated maintainer-decision batch.
7. **PA-slice CODEOWNERS refinement.** Analog to Group 2500 API-slice discipline pending at S2599 close residuals.
8. **PA tool schema external export mechanism.** SCHEMA_VERSION exists for live-reload; publication/deployment strategy UNKNOWN.

## 20. Appendix

### 20.1 Files inspected

Absolute paths + relevant line ranges:

- `/Users/donkeyking/development/unified-donkey-betz/core/urls.py` — lines 1005 (assistant_context import), 2485-2540 (PA endpoint block A + F2F), 4900-4903 (dev/minimal block B)
- `/Users/donkeyking/development/unified-donkey-betz/core/views_personal_assistant.py` — 20+ view function definitions (lines 33, 132, 225, 267, 521, 630, 688, 744, 785, 832, 921, 978, 1014, 1318, 1411, 1484, 1522, 1591, 1688, 1715, 1737)
- `/Users/donkeyking/development/unified-donkey-betz/core/views_assistant_bypass.py:34, 226`
- `/Users/donkeyking/development/unified-donkey-betz/core/views_image_tools.py:60`
- `/Users/donkeyking/development/unified-donkey-betz/core/views_image_misc.py:2470, 3973`
- `/Users/donkeyking/development/unified-donkey-betz/core/views_f2f.py:121, 193, 256`
- `/Users/donkeyking/development/unified-donkey-betz/core/services/unified_pa_entrypoint.py:194 (PAResponse), 216, 244 (INTENT_ENRICHMENT_MAP), 552, 697-718, 1371`
- `/Users/donkeyking/development/unified-donkey-betz/core/services/pa_tool_schemas.py:19 (SCHEMA_VERSION), 24-5058 (PA_TOOL_SCHEMAS 113 entries)`
- `/Users/donkeyking/development/unified-donkey-betz/core/services/tool_dispatcher.py:194+` (156 handler registration)
- `/Users/donkeyking/development/unified-donkey-betz/core/epa_handlers_tools.py:191-217 (WORKSPACE_AWARE_AGENTS), 341, 3873-3907`
- `/Users/donkeyking/development/unified-donkey-betz/core/agents/base_agent.py:5355-5425` (execute_with_workspace F-B-HIGH-3)
- `/Users/donkeyking/development/unified-donkey-betz/core/settings.py:161-215 (INSTALLED_APPS), 645-669 (REST_FRAMEWORK), 1600-1605 (SPECTACULAR_SETTINGS)`
- `/Users/donkeyking/development/unified-donkey-betz/core/api_responses.py:53-98` (APIResponseEnvelope)
- `/Users/donkeyking/development/unified-donkey-betz/core/tasks.py:11919 (rebuild_pa_context_task), 13444 (expire_stale_followup_subscriptions)`
- `/Users/donkeyking/development/unified-donkey-betz/core/tasks_misc.py:4703-4850` (process_pa_chat_task)
- `/Users/donkeyking/development/unified-donkey-betz/core/models/conversations/models.py:19 (ConversationMemory), 59 (ChatConversation)`
- `/Users/donkeyking/development/unified-donkey-betz/core/models_unified_system.py:882 (AgentExecution), 1017 (AgentFollowupSubscription)`
- `/Users/donkeyking/development/unified-donkey-betz/core/models/fleet.py:570` (FleetPAChatAuditRow)
- `/Users/donkeyking/development/unified-donkey-betz/CODEOWNERS`
- `/Users/donkeyking/development/unified-donkey-betz/requirements.txt` (drf-spectacular==0.28.0)

### 20.2 Docs inspected

- `docs/topics/personal-assistant.md` (1-148)
- `docs/PLATFORM_WHAT_IT_IS.md` (188-225)
- `docs/PLATFORM_INVENTORY.md` (autoblock lines 18, 42, 888-896, 1277, 1380, 1632-1633)
- `CLAUDE.md` (7-36, 94-104, 212, 223)
- `docs/research/domains/pa/2600_pa_domain_scoping.md` (full — DIRECT PARENT)
- `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` (full — PARENT-ARC PREDECESSOR)
- `docs/research/domains/api/2599_api_canonical_summary.md` (full — Group 2500 canonical verdict)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template, §13 Explore contract, §14 verifier-loop, §15 SIGN discipline)
- `docs/AUDIT_FINDINGS.md` (finding #17 line 59 — ToolCallRecord telemetry closed S1115)

### 20.3 Grep patterns used

- `^class PAResponse` (verifier: PAResponse existence)
- `"name":` in `core/services/pa_tool_schemas.py` (verifier: tool schema count — bloated by nested keys)
- `path\(['\"]api/(pa|assistant|v1/assistant)/` in `core/urls.py` (verifier: URL denominator — single-line matches only)
- `^\s*path\(` in URL block 2485-2545 (verifier: multi-line path() detection)
- `^(def|async def) assistant_context\b` (verifier: UNKNOWN def-site trace)
- `INTENT_ENRICHMENT_MAP` regex extraction (verifier: 8 enrichment services)
- `drf_spectacular|SpectacularAPIView` in `core/settings.py + core/urls.py` (verifier: DECORATOR-INERT baseline)
- `@extend_schema` across 5 PA view files (verifier: 0/34 decorator count)

### 20.4 Unresolved unknowns

Per AC-A1 F5 fold — target 0 UNKNOWN on existence-of-declaration achieved; UNKNOWN allowed on non-HEAD runtime behaviors:

1. `assistant_context` view def-site inside `core.views` package aggregator (row 1 §6 table). Next-step pointer: Cat B S2602 or dedicated follow-up trace.
2. `assistant_chat` view — imported at `core/urls.py:1300` in a batch; def-site verified at `core/views_image_tools.py:60` per Agent 3.
3. Dev/minimal routes (rows 31-34) def-site inside `core/views_personal_assistant_dev.py` — imported at `core/urls.py:1096` inside conditional `try:` block. Purpose UNKNOWN. Next-step pointer: Cat B S2602 opening or maintainer-decision batch.
4. PA tool schema external export mechanism (SCHEMA_VERSION versioning; publication strategy UNKNOWN).
5. PA_TOOL_AUDIT.md generation status (referenced but file existence UNKNOWN at repo scan).

### 20.5 Conflicts between sources

**Conflict logging criterion (S4 SIGN cycle 1 fold):** Items logged only when sources disagree on a **binary existence claim**, a **denominator/count**, or a **def-site/ownership trace** that changes Cat A measurements (AC-A1/AC-A2). Minor wording differences or out-of-scope hypotheses NOT logged as conflicts.

- **Agent 3 (119 tools) vs Agent 6 (113 tools) vs PLATFORM_INVENTORY (113):** Reconciled to 113 per Python regex extraction of top-level dict entries in `PA_TOOL_SCHEMAS` list.
- **Agent 2 (3 enrichment services) vs Agent 6 (8 enrichment services) vs PLATFORM_INVENTORY (8):** Reconciled to 8 per INTENT_ENRICHMENT_MAP canonical enumeration (advisor, blog_performance, domain_context, intelligence_enricher, platform_briefing, proactive_intelligence, spider_trends, strategic_memory).
- **Agent 3 (27 endpoints) vs verifier (34 endpoints):** Reconciled to 34 (27 single-line + 3 F2F multi-line + 4 dev/minimal).
- **Agent 5 (PAResponse does not exist — CRITICAL drift) vs Agent 2 (PAResponse EXISTS at line 194):** Reconciled to EXISTS per file-read verification at `core/services/unified_pa_entrypoint.py:194`.

### 20.6 Verifier-loop corrections summary

Recorded in frontmatter `verifier_loop` field. Five pre-draft corrections:
1. PAResponse class EXISTS (Agent 5 wrong).
2. PA tool schemas = 113 (Agent 3 grep bloated to 119).
3. PA-path URL denominator = 34 (Agent 3 undercount 27 by missing multi-line + dev/minimal).
4. `assistant_context` view def-site UNKNOWN (recorded with next-step pointer).
5. Enrichment services = 8 (Agent 2 undercount 3 by confusing `*Enricher` classes with registry).

### 20.7 Cat A boundary discipline confirmed

- Cat A collected DECLARATION-side REST-boundary evidence only.
- Cat A did NOT recommend Path A/B/C+island verdict.
- Cat A did NOT author @extend_schema retrofit code.
- Cat A did NOT pick typed-client codegen framework.
- Cat A did NOT change endpoint behavior (F9 fold micro-anti-scope).
- Path A/B/C+island Chris-D-verdict deferred to S2699 xx99 close after all 4 children contribute evidence.

### 20.8 SIGN cycle 1 fold record

Full audit doc routed to Rigby SIGN cycle 1 via **2-pin recovery pattern** per `feedback_rigby_sign_worker_instability_recovery.md` (doc size 8729 words above 4k-word inline-prompt threshold; batched into 2-batch × 2-Q cadence).

**Pin 1 (`pa-ad162d8af36c4985`):** TWENTY-FOURTH consecutive dedicated fresh SIGN pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500/S2501/S2502/S2503/S2504/S2599/S2600 twenty-three prior. Batch 1 (Q1+Q2) + Batch 2 (Q3+Q4) substantive verdicts captured. Hit turn-3 worker instability at close-summary prompt (matches feedback pattern — 2 substantive turns + tool-payload accumulation on 8k+ word doc). Retired via `session_tool.retire force=true` at 5 updated rows.

**Pin 2 (`pa-767dddd95cb24099`):** TWENTY-FIFTH consecutive dedicated fresh SIGN pin retirement candidate. Recovery per feedback playbook: ultra-short-ping first + titles-only close. Q4 close + overall MEDIUM + cycle 2 candidacy captured. Retired at 3 updated rows.

**Verdict per Q (Pin 1 rich-context):**
- **Q1** (Cat A boundary discipline): STRENGTHEN. Fold S1 — §1 F8 span rewrite to boundary-neutral implication + §1 bullet (1) "blocks Path A" → "prerequisite dependency."
- **Q2** (F11 canonical inventory + AC-A1 measurability + F8 codification): STRENGTHEN. Fold S2 — §6.2 anti-verdict boundary note at top of section. Fold S5 — §6.1 epistemic grade note (observed vs declared cells).
- **Q3** (verifier-loop rigor + evidence-density): STRENGTHEN. Fold S3 — §5 unit-of-measure note (registry entries vs class count). Fold S4 — §20.5 conflict logging criterion.
- **Q4** (anti-scope + sibling-cat delegation + F9 micro-anti-scope): STRENGTHEN. Fold S6 — §17 DEBT-2 elevation softened to observation. Fold S7 — §16.1 Path-C-pure hard-constraint attribution to Cat C1 F5 fold.

**Recovery Pin 2 rejected suggestions (parent-Claude verifier-loop compensating quality gate):**
- Q4.3 (remediation ladder + exit criteria) — Cat A boundary violation (evidence-only; remediation is S2699 xx99 Chris-D-verdict scope).
- Q4.4 (verification harness for Path-C-pure constraint) — Cat A boundary violation (verification-harness design is post-verdict implementation scope).

**Net folds Chris-ratified:** 7 folds S1-S7 baked in-place. Cycle 2 NOT required (Q1-Q3 binding; Q4 substantive folds S6+S7 suffice; Q4.3/Q4.4 parked as "boundary-questions-not-evidence-questions" per `feedback_verifier_loop_pattern`).

**Overall confidence at close:** HIGH-adjacent on captured content (Pin 1 rich-context); Pin 2 recovery gave MEDIUM per short-context reading. Parent-Claude verifier-loop applied as compensating quality gate per feedback recovery clause. Chris "agree all" 2026-07-06 ratified all 7 folds wholesale — status flipped `draft` → `active` per playbook §16 draft-first workflow.
