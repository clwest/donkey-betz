---
title: "Group 2600 PA Cat B Audit — PA-Client Contract Surface Design-Prep"
status: active
authority: research
version: v1
session_id: 2602
date_opened: 2026-07-06
date_ratified: 2026-07-06
arc: Research Group 2600 (PA — Cross-Arc Handoff Bundle Consuming CF-2600-PA + CF-D6 + F-B-HIGH-3 + Workspace-Context Authz + REST↔WS T7 Joint Dual-Owner PA Side) — S2602 P2 Cat B PA-client contract surface design-prep child audit
domain_slug: pa
research_group: 2600
child_slot: P2 Cat B
head_sha: 7ddd8ce6 (post-S2600 merge PR #2929)
companion_anchors:
  - docs/CLAUDE.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/PLATFORM_INVENTORY.md
  - docs/topics/personal-assistant.md
  - docs/topics/frontend.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
related:
  - docs/research/domains/pa/2600_pa_domain_scoping.md                              # DIRECT PARENT (P0)
  - docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md  # SIBLING PRIOR-CHILD (P1 Cat A)
  - docs/research/domains/api/2502_api_frontend_client_architecture_design_prep_audit.md # PARENT-ARC PREDECESSOR (Cat B typed-baseline)
  - docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md  # PREDECESSOR (assistantApi cross-cutter)
  - docs/research/domains/api/2599_api_canonical_summary.md                         # Group 2500 API canonical verdict inheritance
verifier_loop: |
  v1 (2026-07-06, S2602 arc-open):
  Cat B PA-client contract surface design-prep drafted after S2600 parent
  scoping closed + S2601 Cat A closed. Shape card 4-Q routed to Rigby
  SIGN-preview via arc pin pa-c17a8d7e0660413b turn 3 — HIGH confidence
  with 8 folds (F-B1 through F-B8). Chris "agree all" 2026-07-06 ratified
  all 8 folds wholesale pre-drafting. Folds baked into §3 (F-B1 grep-locked
  region markers), §2 (F-B2 lens rewrite), §5.3 AC-B1/B2/B4 (F-B3/B4/B5),
  §5.3 AC-B6 (F-B6 evidence-only phrasing), §16 (F-B7 single-sentence
  F-B-HIGH-3 attribution), §7 (F-B8 Cat-B-9 no-types-file-moves).

  Six-parallel-Explore sweep dispatched at S2602 open turn 4 per playbook
  §13. Agent 3 (APIs) owned U6+U7 evidence-gap closure turn 1 + assistantApi
  surface enumeration + tools/pa_chat.py 3-way envelope contract. Agents 1
  (Models) + 2 (Services) + 4 (Integrations) + 5 (Documentation) + 6
  (Verification) contributed complementary evidence.

  Parent-Claude verifier-loop applied pre-draft per playbook §14 discipline
  + S2601 5-corrections precedent. Seven corrections landed:
  (1) apiModule count = 93 at HEAD (Agent 6 claim of 94 REFUTED via direct
      `^export const \w+Api\s*=` grep returning exactly 93).
  (2) assistantApi export block at api.ts:1147-1230 (81 LOC region;
      F-B1 grep-locked start/end anchors verified — start `export const
      assistantApi = {` at line 1147; end `}` at line 1230).
  (3) assistantApi method count = 20 (matches Agent 3 table; Agent 6 claim
      of 11 REFUTED via direct enumeration of 20 method entries).
  (4) assistantApi typed-generic count = 5 (Agent 3 text said 4 but table
      showed 5; direct grep `api\.\w+<` in region 1147-1230 = 5 matches).
      Reconciled to 5 per direct verification.
  (5) assistantApi typed rate = 5/20 = 25% per F-B5 denominator methodology
      (denominator = exported assistantApi methods explicit list, NOT
      "subset of 93 apiModule / 856 method-invocation platform denominator").
      EXCEEDS platform 7.36% baseline by ~3.4x (evidence-only observation
      per Cat B boundary discipline — NOT a "should retrofit" verdict).
  (6) Silent-401 interceptor: `error.response?.status === 401` check at
      api.ts:48 (matches S2502 §3.2 exactly); Agent 2 reported broader
      block 43-62 which is the surrounding response-interceptor scope.
      Both framings correct; interceptor block spans 43-62, status check
      is at line 48.
  (7) paStore.ts LOC = 449 (Agent 1 said 434; Agent 3 said 450 — direct
      wc -l at HEAD = 449). Reconciled.

  Six additional evidence findings warrant explicit disclosure at draft:
  (a) frontend/src/types/ contains ONLY cockpit.ts at HEAD (`ls
      frontend/src/types/*` returns 1 file — NEGATIVE on pa.ts existence;
      structural prerequisite (1) per F-B6 fold NEGATIVE at HEAD).
  (b) frontend/src/hooks/ typed-island hooks: ONLY cockpitQueries.ts at
      HEAD (`ls frontend/src/hooks/*Queries*` returns 1 file — NEGATIVE
      on paQueries.ts existence; structural prerequisite (2) per F-B6
      fold NEGATIVE at HEAD).
  (c) assistantApi imports shared `api` axios instance from api.ts line
      1147 region (structural prerequisite (3) per F-B6 fold POSITIVE at
      HEAD).
  (d) WS canonical PA-client message-class evidence at
      frontend/src/pages/CommandCenterPage.tsx:682-764 reveals THREE
      observed classes: (i) message.created (chat-response streaming),
      (ii) agent.completed (task-status broadcast), (iii)
      rigby.tool.started + rigby.tool.completed (tool-ticker lifecycle
      events per Session 1172). **Not observed at WS layer:
      async-audio-url**. F-B3 fold's third canonical class label
      ("async-audio-url delivery") requires re-labeling: audio_url is
      embedded in the REST `/api/pa/chat/status/<task_id>/` poll response
      as a field of the completed-task envelope, NOT delivered via WS
      channel. Cat B records this as an evidence finding + re-labels
      third canonical class to "rigby.tool.* lifecycle events" at U6
      inventory (§6.2).
  (e) personal-assistant.md doc line 13 still claims "104 OpenAI
      function-calling tool schemas" (S2601 §14.2 confirmed drift;
      unchanged at HEAD). Runtime authoritative = 113 per
      PLATFORM_INVENTORY autoblock. Cat B records observation; §19.3
      MEDIUM follow-on for docs cascade.
  (f) personal-assistant.md doc line 26 references "PAResponse" (which
      EXISTS per S2601 §14.1 verifier correction) but does NOT declare
      that PAResponse is Python-internal-only + NOT propagated to REST
      or client boundary. Documentation gap (not drift); Cat B records
      §19.3 MEDIUM follow-on.

  Rigby SIGN cycle 1 CLOSED 2026-07-06 via dedicated fresh SIGN pin
  pa-760b68d6e48d4448 (TWENTY-SIXTH consecutive dedicated fresh SIGN pin
  retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/
  S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500/
  S2501/S2502/S2503/S2504/S2599/S2600/S2601-Pin-1/S2601-Pin-2 twenty-five
  prior + 26th; SINGLE-PIN close pattern per S1899-S2500 EIGHT-consecutive
  tested pattern — 2-pin recovery from S2601 NOT required at Cat B).
  Preemptive 2-batch × 2-Q SIGN batching per
  feedback_rigby_sign_worker_instability_recovery.md (doc size 10,689 words
  above 4k-word inline-prompt threshold). Batch 1 (Q1+Q2) verdict: HIGH
  confidence with F-B9 STRENGTHEN (add explicit Cat-B-1 through Cat-B-9
  enumerated anti-scope list to §16.4 for ID stability). Batch 2 (Q3+Q4)
  verdict: HIGH confidence with F-B10 STRENGTHEN (rephrase §19.2 item #6
  to boundary-neutral evidence follow-on — drops "MIGRATE from REST-
  embedded to WS-broadcast" language that edges into Cat D option-space).
  Chris "agree all" 2026-07-06 ratified both F-B9 + F-B10 folds
  wholesale. Cycle 2 NOT required per S2601 precedent (only STRENGTHEN
  folds, no CRITICAL / NEW CONCERN). Both folds baked in-place at §16.4
  (F-B9 new subsection) + §19.2 item #6 rewrite (F-B10). Frontmatter
  status flipped `draft` → `active` per Chris ratification.
owner: claude (drafted S2602 v1 with 8 pre-drafting shape-card folds + 7
  verifier-loop corrections + 2 SIGN cycle 1 STRENGTHEN folds — F-B9 +
  F-B10; TWENTY-SECOND-consecutive playbook §11.2 20-section child-audit
  template application after S1301/S1401/S1501/S1601/S1701/S1801/S1901/
  S2001/S2101/S2102/S2103/S2104/S2201/S2202/S2203/S2204/S2401/S2402/
  S2403/S2404/S2501/S2601 twenty-one prior)
---

# Group 2600 PA Cat B Audit — PA-Client Contract Surface Design-Prep

> **Cat B boundary discipline.** This audit collects EVIDENCE for the
> Chris-D-verdict on **PA-client contract surface** — specifically the
> Path (a) typed assistantApi.ts island / (b) SHAPE-BLIND flow-through
> preserved / (c) hybrid typed-response-envelope with SHAPE-BLIND
> message-payload / (d) hybrid variants. Cat B **does NOT** recommend
> a Path. Cat B does NOT retrofit typed generics onto assistantApi. Cat
> B does NOT enumerate WS envelope Path A/B/C option space (Cat D
> S2604 scope). Cat B does NOT ratify F-B-HIGH-3 closure (Cat C1 S2603
> scope). Cat B does NOT propose UI/UX behavior changes, state-mgmt
> refactors, frontend build/bundling changes, frontend testing
> framework decisions (F1 fold hard boundary). Cat B does NOT create
> new types/ folder or file moves — even creating `types/pa.ts` is a
> change; Cat B **observes only** (F-B8 fold micro-anti-scope). Everything
> in this document is EVIDENCE. Nothing is DIRECTIVE.
>
> **Denominator lock (F-B5).** PA-client denominator = **explicit list
> of 20 exported assistantApi methods** at `frontend/src/lib/api.ts:1147-1230`
> (F-B1 grep-locked region markers). Denominator is NOT "subset of 93
> apiModule / 856 method-invocation platform denominator" — that
> phrasing was rejected pre-drafting per F-B5 SIGN-preview fold.
>
> **Evidence-gap closure turn 1 discipline (F-B3, F-B4).** This audit
> closes U6 (PA-client-consumed WS envelope inventory, capped to 3
> canonical message classes) + U7 (paStore field-list dump with 0
> UNKNOWN field names allowed — UNKNOWN allowed only for intent/
> disposition) at Cat B opening turn 1 per F9+F10a inheritance from
> parent §2.5. NO Cat B option-space enumeration was performed pre-U6/U7
> confirmation.

## 1. Executive Summary

PA-client Contract Surface at HEAD `7ddd8ce6` presents a **THREE-SURFACE ASYMMETRIC TYPING SHAPE**: (a) `frontend/src/lib/api.ts` `assistantApi` object-literal export at lines 1147-1230 declares **20 methods with 5 typed-generic invocations = 25% typed rate** (`api.\w+<T>()`) — materially ABOVE the platform 7.36% baseline (S2502) at **~3.4x**; (b) `frontend/src/stores/paStore.ts` (449 LOC) declares **16 fields via Zustand persist(v3) with `pa-dock-state` localStorage key + partialize(7 fields) + syncUser cross-user wipe(5 fields)**; and (c) `tools/pa_chat.py` (500 LOC) declares the **3-way async task envelope contract INFORMALLY via untyped dict literals only** — no dataclasses / TypedDicts / Pydantic models. Each surface has a distinct declaration mechanism and grade; no unified source-of-truth surface joins them.

**Structural prerequisites for cockpitApi-analog exemplar (F-B6 evidence-only assessment): 1 of 3 PRESENT at HEAD.** (i) `frontend/src/types/pa.ts` — **NEGATIVE** (dir contains ONLY `cockpit.ts` per S2502 §4.3 baseline UNCHANGED). (ii) `frontend/src/hooks/paQueries.ts` — **NEGATIVE** (dir contains ONLY `cockpitQueries.ts` per S2502 §3.4 baseline UNCHANGED). (iii) shared `api` axios instance import at assistantApi region — **POSITIVE** (`export const assistantApi = { ... api.get(...) / api.post(...) ... }` at api.ts:1147+).

**U6 evidence-gap closure turn 1 (F-B3 client-consumed WS scope clamp).** PA-client subscribes to **1 primary WS channel** at `frontend/src/pages/CommandCenterPage.tsx:682-764` — `ws://{host}/ws/pa/conversations/<activeConversationId>/?token=...`. Three canonical PA-client message classes observed (F-B3 fold cap enforced): (i) `message.created` = chat-response streaming (untyped `data as {message: {...}}` parse); (ii) `agent.completed` = task-status broadcast (untyped parse of `{execution_id, agent_name, status, completed_at, error_signature?, artifact_pointers?}`); (iii) `rigby.tool.started` + `rigby.tool.completed` = tool-ticker lifecycle events (Session 1172 seed; untyped parse of `{trace_id, seq, tool_call_id, tool_name, started_at, latency_ms?, status?}`). **F-B3 label re-alignment (verifier-loop pre-draft correction).** F-B3 fold's third canonical class ("async-audio-url delivery") **does NOT appear at WS layer** at HEAD — `audio_url` is embedded in the REST `/api/pa/chat/status/<task_id>/` poll response as a field of the completed-task envelope, NOT delivered via WS. Cat B re-labels third WS canonical class as `rigby.tool.*` lifecycle events + records async-audio-url as REST-embedded (§6.2). **All 3 WS classes: envelope grade = `observed-JSON-only` (untyped `data as {...}` parse at CommandCenterPage.tsx:686); NO TypedDict / Protocol / BaseModel / TypeScript interface declared at consumer.** Cat B provides evidence baseline; Cat D S2604 owns WS envelope Path A/B/C verdict.

**U7 evidence-gap closure turn 1 (F-B4 0-UNKNOWN-field-names closure discipline).** paStore full field list at HEAD: **16 fields** — `userId`, `isDockOpen`, `isDockMinimized`, `messages`, `currentInput`, `currentPage`, `activeConversationId`, `conversations`, `isSidebarOpen`, `conversationsLoading`, `activeTool`, `recentTool`, `seenSeqs`, `recentAgentCompletion`, `agentCompletionQueue`, `seenCompletions`. Zero UNKNOWN field names per F-B4 fold discipline. Persist(v3) partialize retains 7 fields (`userId`, `isDockOpen`, `isDockMinimized`, `messages` last-50, `currentInput`, `activeConversationId`, `isSidebarOpen`); memory-only for 9 fields; syncUser cross-user wipe hits 5 fields (`messages`, `activeConversationId`, `conversations`, `currentInput`, `conversationsLoading`). Intent-disposition per field: 2 UNKNOWN (`isDockOpen`, `isDockMinimized` — dock-state on-cross-user or on-logout intent UNCONFIRMED; NOT explicitly wiped by syncUser; NOT explicitly wiped by authStore.logout) with **pointer → Cat C2 S2603 verdict** per F-B4 discipline (§8.4). 14 fields intent-confirmed.

**Assistant API cross-cutter distribution at HEAD.** 22 direct `assistantApi.\*` invocations across 5 consumer files (`CommandCenterPage.tsx` 10 hits + `GlobalPADock.tsx` 4 hits + `paStore.ts` 3 hits + `AttentionWidget.tsx` 3 hits + `GovernmentPage.tsx` 2 hits) at HEAD via direct grep. NOTE: S2203's 132 cross-cutter figure was **4-cross-cutter aggregate** (humanApi + assistantApi + workspaceApi + contentApi combined) across 24 files, **NOT assistantApi alone**. Cat B methodology corrects the S2203 miscite.

**3 parallel chat endpoints — client-side call distribution (S2601 §17 inheritance).** Client-side calls only **2 of 3** endpoints: `/api/pa/chat/` (via `assistantApi.paChat` at api.ts:1155) + `/api/assistant/chat/` (via `assistantApi.chat` at api.ts:1150). **Endpoint `/api/v1/assistant/chat/` is NOT called from the frontend client at HEAD** (Agent 4 + Agent 6 verified via grep `frontend/src` — zero direct callers). Legacy `/api/assistant/chat/` marked as "old hardcoded prompt from views_image.py" (deprecated) per api.ts inline comment line 1149.

**Cat B evidence-only eligibility per consumer surface (a/b/c/d axes per Cat A §6.2 S2 boundary discipline).**

| Consumer surface | (a) Typed island eligible | (b) SHAPE-BLIND preserved | (c) Hybrid (envelope + payload) | (d) UNKNOWN |
|---|---|---|---|---|
| `frontend/src/lib/api.ts` assistantApi | ELIGIBLE (5/20 methods already typed; +15 methods candidate for retrofit) | ELIGIBLE (current state; 75% untyped) | ELIGIBLE (5 typed methods are envelope-typed with inline interfaces) | — |
| `frontend/src/stores/paStore.ts` | ELIGIBLE (16 fields inline-declared inline; retrofit to typed types/pa.ts possible) | ELIGIBLE (current state; inline `interface Message`, `interface ConversationSummary`, etc. at 24-77) | ELIGIBLE (message-shape currently inline-typed; retention/persistence contract remains SHAPE-BLIND) | — |
| `tools/pa_chat.py` | ELIGIBLE (Python TypedDict / Pydantic model overlay possible on request/response envelopes) | ELIGIBLE (current state; 100% untyped dict literals) | ELIGIBLE (envelope typed via TypedDict; payload content field untyped) | — |

Cat B records eligibility ONLY; Path selection is Chris-D-verdict at S2699 xx99. Zero UNKNOWN per surface per F-B4 analog discipline.

**Cat A boundary evidence inheritance (S2601 §16.1 F-B-HIGH-3 attribution — single sentence per F-B7 fold).** Workspace-membership implicit-gate at `core/agents/base_agent.py:5355 execute_with_workspace()` is Cat C1 S2603 scope; Cat B contract-typing decision-space is INDEPENDENT of F-B-HIGH-3 closure per S2504 §88 orthogonality.

**What comes next.** S2603 Cat C receives Cat B U7 paStore field-list dump for C2 session-lifecycle retention window decision (which paStore fields wipe-on-retire vs persist-across-sessions). S2604 Cat D receives Cat B U6 WS envelope inventory for Path A/B/C WS envelope-strictness Chris-D-verdict decision-space. S2699 xx99 synthesizes Cat B eligibility categorization + Cat A §6.1 F11 canonical inventory + Cat C1 F-B-HIGH-3 closure + Cat D T7 REST↔WS consistency check into the combined Group 2600 PA delta-decision Chris-D-verdict.

## 2. Domain Purpose

**Playbook §9 canonical Q1-Q2 — What is this domain?**

The PA-Client Contract Surface is the **consumption-side substrate** of the PA subsystem's contract mechanism — the mechanism by which three consumer surfaces (frontend UI via assistantApi + paStore, plus CLI tooling via tools/pa_chat.py) interpret PA-REST + PA-WS response shapes and populate application state.

**Cat B lens (F-B2 fold rewrite — evidence-only, deferred to Chris-D-verdict at S2699 xx99):**

> *"For each PA-client surface (assistantApi in `frontend/src/lib/api.ts`, paStore in `frontend/src/stores/paStore.ts`, `tools/pa_chat.py`), what contract-shape artifacts exist at HEAD (types/interfaces, runtime validators, discriminated unions, envelope parsing, explicit field lists), and what volatility drivers exist (streaming token chunks, tool-run objects, async URLs, dock-state persistence) that would affect typed-island feasibility — without selecting Path (a) typed / (b) SHAPE-BLIND / (c) hybrid / (d) UNKNOWN in Cat B?"*

Delta axes ORTHOGONAL per S2504 §88 discipline unless coupling evidence surfaces.

**Cat B boundary — what Cat B owns:** the CONSUMPTION side at the CLIENT layer. Cat B owns questions of the shape "does each PA-client consumer surface DECLARE X (typed shape / field list / envelope contract) as an artifact at HEAD?" Cat B does NOT own questions of the shape "does each PA-path REST endpoint DECLARE X to consumers?" (Cat A P1 owns, closed S2601), "does the workspace-authorization contract PROPAGATE?" (Cat C1 P3 owns), "does the session-lifecycle contract COUPLE to Group 2400 verdict?" (Cat C2 P3 owns), "does the WS message-contract PARALLEL the REST-contract?" (Cat D P4 owns).

**Cat B domain purpose scope discipline** (per playbook §5 phase discipline research-only + design-prep + F1 fold hard boundary + F-B8 fold no-file-moves + Cat A §20.7 F9 micro-anti-scope precedent):

- Cat B collects evidence for future Chris-D-verdicts on Path (a)/(b)/(c)/(d).
- Cat B does NOT recommend, decide, or author.
- Cat B does NOT retrofit typed generics.
- Cat B does NOT create new `types/pa.ts` OR `hooks/paQueries.ts` files.
- Cat B does NOT modify api.ts, paStore.ts, or tools/pa_chat.py.
- Cat B does NOT propose UI/UX behavior changes, Zustand slice consolidations, build/bundling changes, or testing framework decisions (F1 fold).

Everything below is EVIDENCE. Nothing below is DIRECTIVE.

## 3. Canonical Entry Points

**Playbook §9 canonical Q3 — Where does the domain enter the system?**

### 3.1 PA-Client canonical consumer surfaces at HEAD `7ddd8ce6`

Three consumer surfaces per parent §3.B + F1 fold hard boundary:

| Surface | File | LOC | Type | F-B1 grep-locked region markers |
|---|---|---|---|---|
| assistantApi module | `frontend/src/lib/api.ts` | 4194 (whole file) | TypeScript object-literal export | Start: `^export const assistantApi = \{` at api.ts:1147; End: matching `}` at api.ts:1230; region span = **84 lines** (F-B1 grep-locked anchors verified via parent-Claude verifier-loop) |
| paStore | `frontend/src/stores/paStore.ts` | 449 | Zustand `create` with `persist` middleware v3 | Full file (module-scope entry) |
| tools/pa_chat.py CLI wrapper | `tools/pa_chat.py` | 500 | Python module with `chat()` public function | Full file (module-scope entry) |

**File LOC counts verified at HEAD `7ddd8ce6`** via `wc -l`: api.ts=4194, cockpitApi.ts=513, apiClient.ts=29, cockpit.ts=820, cockpitQueries.ts=485, paStore.ts=449, pa_chat.py=500 (F-B5 denominator lock lineage).

### 3.2 assistantApi region markers (F-B1 grep-locked start/end anchors)

**Start marker:** `^export const assistantApi = \{` at `frontend/src/lib/api.ts:1147`.
**End marker:** first bare `}` at column 0 immediately preceding the next `^export const \w+Api\s*=` declaration.
**Region span:** api.ts:1147-1230 = 84 lines.
**Denominator (F-B5):** 20 exported assistantApi methods (explicit list at §6.1).

**Companion cross-cutter apiModules confirmed at HEAD** (S2203 §14 4-cross-cutter finding):
- `humanApi` (api.ts:1607)
- `workspaceApi` (api.ts:1695)
- `contentApi` (api.ts:895)
- `assistantApi` (api.ts:1147)

Total apiModule exports in api.ts at HEAD: **93** (F-B5 denominator lock — direct grep `^export const \w+Api\s*=` returns exactly 93; S2502 baseline UNCHANGED). Agent 6's claim of 94 apiModule exports REFUTED via parent-Claude verifier-loop direct-grep.

### 3.3 paStore module-scope entry

**Store creator:** `usePAStore` at paStore.ts (`create<PAStore>()(persist(...))` pattern).
**Storage backend:** localStorage via Zustand persist middleware.
**Storage key:** `'pa-dock-state'`.
**Persist version:** v3 (with migration from v<2 and v<3).
**Partialize scope:** 7 of 16 fields (see §4.1 for full field list).

**paStore-adjacent stores** — companion PA-client stores at HEAD (Agent 1 evidence):
- `assistantContextStore` at `frontend/src/stores/assistantContextStore.ts:1-29` — Zustand no-persist; carries `FocusedEntity` (`type: deliverable|initiative|action_item|attention|file`) passed to PA chat payload as `context.focused_entity`.
- `workspaceStore` at `frontend/src/stores/workspaceStore.ts:1-28` — Zustand no-persist; active workspace ID + name.
- `authStore` at `frontend/src/stores/authStore.ts:1-53` — Zustand + persist under `'auth-storage'` key; token/user/isAuth.
- **No dedicated `chatStore` OR `messagesStore` at HEAD** (Agent 1 verified).

### 3.4 tools/pa_chat.py module-scope entry

**Public function:** `chat(message, conversation_id=None, context=None)` at pa_chat.py:178.
**HTTP layer:** `urllib.request` stdlib (verified via file-read; no `requests` / `httpx` import).
**Envelope contract:** POST to `/api/pa/chat/` returns `{task_id}`, poll `/api/pa/chat/status/<task_id>/` at `POLL_INTERVAL=3s` up to `POLL_TIMEOUT=300s`.
**Auth:** `PA_API_TOKEN` env var → `Authorization: Token <token>` header.

## 4. Major Models

**Playbook §9 canonical Q4-Q5 — What are the major models + how do they relate?**

**Cat B boundary: PA-client-declared TypeScript interfaces / inline dataclasses as contract-CONSUMPTION artifacts** (not PA persistence models themselves — those are Cat A boundary, closed at S2601 §4).

### 4.1 paStore field-list dump (U7 evidence-gap closure turn 1 per F-B4 fold)

Full paStore field inventory at HEAD `7ddd8ce6`. **Zero UNKNOWN field names per F-B4 fold discipline; UNKNOWN allowed ONLY for intent/disposition with explicit pointer.**

| # | Field | Type | Initial value | Persisted? | Partialize? | syncUser wipe? | Intent | Pointer |
|---|---|---|---|---|---|---|---|---|
| 1 | `userId` | `number \| null` | `null` | localStorage | ✅ | ✅ (replaced) | user-scoping | — |
| 2 | `isDockOpen` | `boolean` | `false` | localStorage | ✅ | ❌ NOT wiped | UNKNOWN intent | **→ Cat C2 S2603** |
| 3 | `isDockMinimized` | `boolean` | `false` | localStorage | ✅ | ❌ NOT wiped | UNKNOWN intent | **→ Cat C2 S2603** |
| 4 | `messages` | `Message[]` | `[]` | localStorage (last-50 slice) | ✅ | ✅ wiped | chat-history retention | Cat C2 session-lifecycle input |
| 5 | `currentInput` | `string` | `''` | localStorage | ✅ | ✅ wiped | draft-input preservation | Cat C2 session-lifecycle input |
| 6 | `currentPage` | `string` | `'/'` | memory-only | ❌ | ❌ (ephemeral) | route-context tracking | — |
| 7 | `activeConversationId` | `string \| null` | `null` | localStorage | ✅ | ✅ wiped | active-conversation ref | Cat C2 session-lifecycle input |
| 8 | `conversations` | `ConversationSummary[]` | `[]` | memory-only | ❌ | ✅ wiped | sidebar-list cache | Cat C2 session-lifecycle input |
| 9 | `isSidebarOpen` | `boolean` | `false` | localStorage | ✅ | ❌ NOT wiped | UI-state persistence | intent-preserved (UI ergonomics) |
| 10 | `conversationsLoading` | `boolean` | `false` | memory-only | ❌ | ✅ wiped | loading-flag | intent-preserved (async ergonomics) |
| 11 | `activeTool` | `ToolTickerEvent \| null` | `null` | memory-only | ❌ | ❌ (ephemeral) | live-tool-lifecycle display (Session 1172) | intent-preserved (WS-driven live) |
| 12 | `recentTool` | `ToolTickerEvent \| null` | `null` | memory-only | ❌ | ❌ (ephemeral) | tool-fade display (2.5s TTL) | intent-preserved (WS-driven live) |
| 13 | `seenSeqs` | `Record<string, number[]>` | `{}` | memory-only | ❌ | ❌ (ephemeral) | WS message-seq dedup | intent-preserved (WS-driven live) |
| 14 | `recentAgentCompletion` | `AgentCompletionEvent \| null` | `null` | memory-only | ❌ | ❌ (ephemeral) | banner display (6s TTL; Session 1175/1181) | intent-preserved (WS-driven live) |
| 15 | `agentCompletionQueue` | `AgentCompletionEvent[]` | `[]` | memory-only | ❌ | ❌ (ephemeral) | multi-agent fanout | intent-preserved (WS-driven live) |
| 16 | `seenCompletions` | `string[]` | `[]` | memory-only | ❌ | ❌ (ephemeral) | completion dedup | intent-preserved (WS-driven live) |

**Totals:**
- Field count = **16** (F-B4 fold: 0 UNKNOWN field names).
- localStorage-persisted = **7** (via partialize: userId, isDockOpen, isDockMinimized, messages, currentInput, activeConversationId, isSidebarOpen).
- Memory-only = **9**.
- syncUser cross-user wipes = **5** (messages, activeConversationId, conversations, currentInput, conversationsLoading).
- **Intent UNKNOWN with Cat C2 pointer = 2** (`isDockOpen`, `isDockMinimized` — dock-state on-cross-user or on-logout intent UNCONFIRMED at HEAD; NOT wiped by syncUser; NOT wiped by authStore.logout).

**S2503 CF-C3 baseline reconciliation.** S2503 CF-C3 declared "3-of-9 syncUser fields wiped at logout." Direct evidence at HEAD: **5 fields explicitly wiped by `syncUser` cross-user hook** (messages, activeConversationId, conversations, currentInput, conversationsLoading). The "9 syncUser fields" baseline appears to reflect the pre-consolidation store size; current paStore has 16 fields, and syncUser wipes 5. Cat B records the discrepancy without asserting cause (per Cat A §14 drift-observation discipline).

### 4.2 assistantApi TypeScript interfaces at HEAD

Inline / co-located interfaces in `frontend/src/lib/api.ts` that model PA-boundary shape:

| Interface | api.ts line | Fields | Consumer |
|---|---|---|---|
| `ToolRun` | 1085 | `tool`, `ok`, `latency_ms`, `error_code?`, `error_message?` | Used by UnifiedPAResponse.tool_runs |
| `UnifiedPAResponse` | 1093 | `success`, `content`, `trace_id`, `tool_runs: ToolRun[]`, `audio_url`, `intent`, `routed_to`, `profile_completeness`, `latency_ms`, `error?`, `conversation_id?` | `assistantApi.paChat` typed-generic response |
| `PAChatAsyncResponse` | 1105 (approx — declared inline near paChat) | `success`, `task_id`, `status: 'processing'` | `assistantApi.paChat` typed-generic response (async return) |
| `PAChatStatusResponse` | 1115 | `success`, `status: 'processing'\|'completed'\|'failed'`, `content?`, `trace_id?`, `tool_runs?`, `audio_url?`, `intent?`, `routed_to?`, `profile_completeness?`, `latency_ms?`, `error?`, `conversation_id?` | `assistantApi.paChatStatus` typed-generic response |
| `ConversationSummary` | 1131 (approx) | conversation list metadata | `assistantApi.listConversations` inline-generic response |
| `ConversationMessage` | 1139 (approx) | per-message shape | `assistantApi.getConversation` inline-generic response |

**Observations (evidence-only):**
- 6 TypeScript interfaces co-located in api.ts modeling assistantApi consumer shape.
- Interfaces mirror backend `PAResponse` dataclass at `core/services/unified_pa_entrypoint.py:194` (S2601 §14.1 verified EXISTS). Field name parity is strong (`content`, `trace_id`, `tool_runs`, `audio_url`, `intent`, `routed_to`, `profile_completeness`, `latency_ms`, `error`) but no shared schema source-of-truth binds them.
- **Manual synchronization risk (evidence-only observation).** If backend `PAResponse` dataclass adds/renames a field, client `UnifiedPAResponse` interface will diverge silently. Cat B records observation; DEBT severity is Chris-D-verdict scope at S2699 xx99.

### 4.3 paStore-inline interfaces at HEAD

Inline TypeScript interfaces in `frontend/src/stores/paStore.ts`:

| Interface | paStore.ts line | Fields |
|---|---|---|
| `Message` | 24-33 | `id`, `role`, `content`, `created_at`, `async_jobs?`, `feedback?`, `source?` |
| `ConversationSummary` | 35-41 | metadata: `id`, `title`, `updated_at`, `is_active`, etc. |
| `AsyncJob` | 14-22 | `task_id`, `agent`, `status`, timing |
| `ToolTickerEvent` | 49-57 | `trace_id`, `seq`, `tool_call_id`, `tool_name`, `started_at`, `latency_ms?`, `status?` (Session 1172 seed) |
| `AgentCompletionEvent` | 69-77 | `execution_id`, `agent_name`, `status`, `completed_at`, `error_signature?`, `artifact_pointers?` (Session 1175/1181 seed) |

**Observations (evidence-only):**
- Duplicate `ConversationSummary` declaration: appears in BOTH `paStore.ts:35-41` AND `api.ts:1131` (approx). Cat B records observation; consolidation is post-verdict implementation scope per F-B8 no-file-moves discipline.
- All paStore inline interfaces are **memory-only** (Zustand store type only; not exported for cross-file typing).
- **`frontend/src/types/pa.ts` DOES NOT EXIST at HEAD** (`ls frontend/src/types/*` returns only `cockpit.ts`; S2502 §4.3 baseline UNCHANGED).

### 4.4 tools/pa_chat.py dataclass/model surface

Direct file inspection (Agent 3 Part E evidence): **ZERO TypedDict / Protocol / BaseModel / dataclass** at pa_chat.py. All request/response envelopes are **untyped `dict[str, Any]` literals** with shape documented in inline comments only (lines 101-120 request payload; lines 149-175 response parsing).

**Observations (evidence-only):**
- pa_chat.py is 100% untyped Python (no `mypy` type annotations for envelope shapes).
- Envelope contract lives in **inline documentation only** (docstring lines 1-10 + comments at construct sites).
- No importable envelope Type surface (e.g., `from tools.pa_chat import PAChatRequest`) exists at HEAD.
- Test consumer at `tests/test_pa_chat_defaults.py:19` imports `from tools import pa_chat` (module-level) but does NOT import a typed envelope surface (Agent 4 evidence).

## 5. Major Services

**Playbook §9 canonical Q4-Q5 — What are the major services?**

**Cat B boundary: PA-CLIENT-side envelope-parsing / interceptor / shape-normalization services only.** Backend PA services (UnifiedPAEntrypoint / ToolDispatcher / PAResponse construction / enrichment) are Cat A boundary, closed S2601 §5.

### 5.1 api.ts interceptor stack (S2502 §3.2 baseline re-verified)

Per Agent 2 Part 1 evidence + parent-Claude verifier-loop reconciliation:

| Interceptor | api.ts line range | Purpose |
|---|---|---|
| Auth (request) | 27-40 | Attaches `Authorization: Token <token>` from `useAuthStore.getState().token`. **NO PA-endpoint-specific branching**; applies uniformly to all requests. |
| Silent-401 (response) | 43-62 | Response interceptor; status-check at line 48 (`error.response?.status === 401`). Whitelist substring: `/auth/` + `/login/` (line 50). Non-whitelist 401s `Promise.reject(error)` (line 60). **NO PA-endpoint-specific branching**. |
| Session-968 request-log (request) | 3990-4006 | Stamps `metadata: {requestId, startTime}`; reads `X-UI-Scope` header; MAX_LOG=200 circular buffer. |
| Session-968 request-log (response) | 4009-4035 | Updates entry status + duration; notifies subscribers. |

**Interceptor scope observations (evidence-only, Cat B boundary):**
- No PA-endpoint URL-substring branching at any interceptor. PA-REST requests are treated uniformly with all other apiModule requests.
- Silent-401 whitelist substring pattern (`/auth/` + `/login/`) at api.ts:50 means non-auth 401s at `/api/pa/*` are `Promise.reject(error)` — component-level handling deferred (line 57-58 comment: "component can handle it").
- **NO envelope-shape normalization** across the 4 401-shape families (Cat C S2503 taxonomy: DRF `{"detail"}` + APIResponseEnvelope + bare `{"success": False, ...}` + hand-constructed). All 401s rejected uniformly.
- **NO runtime validator** (no zod / io-ts / superstruct / valibot / yup / arktype / typebox in `frontend/package.json`; verified via Agent 2 Part 2). All PA responses parsed via TypeScript type assertion / generic inference only.

### 5.2 apiClient.ts X-UI-Scope helper (S2502 §3.5 baseline unchanged)

Per Agent 2 Part 5 evidence:
- LOC = 29 (S2502 baseline unchanged).
- Exports: `scopedGet<T>(url, scope, config?)` at apiClient.ts:8-17; `scopedPost<T>(url, data, scope, config?)` at apiClient.ts:19-29.
- Both inject `'X-UI-Scope': scope` header.
- Both reuse shared `api` axios instance (`import { api } from './api'` at apiClient.ts:3).
- **NO independent HTTP client** (no `axios.create()` override).
- **NO PA-scoped headers** — X-UI-Scope is generic UI-scoped request-log filtering.

### 5.3 cockpitApi.ts typed-island reference exemplar (S2502 §3.4 baseline re-verified)

Per Agent 2 Part 6 + Agent 6 evidence at HEAD:
- LOC = 513 (S2502 unchanged).
- Exported functions = 54.
- Typed-generic invocations = 52 (`api.\w+<T>()`).
- Typed rate = **52/54 = 96%** (S2502 unchanged).
- Imports types from `@/types/cockpit` at cockpitApi.ts:2 (44 types imported per S2502 baseline; unchanged).
- Imports shared `api` from `./api` at cockpitApi.ts:1.
- **Envelope normalization exception at cockpitApi.ts:66-68** — `/v1/agents/execution/{id}/` unwraps nested `data?.data?.execution` with comment "Backend wraps in {success, data: {execution: {...}}}" (Agent 2 evidence). NO runtime validation of unwrapping.

### 5.4 tools/pa_chat.py service surface

Per Agent 3 Part E evidence:
- `chat(message, conversation_id, context)` at pa_chat.py:178 — public entry.
- `send_message(message, conversation_id, context)` at pa_chat.py:101 — HTTP POST to `/api/pa/chat/`.
- `poll_result(task_id)` at pa_chat.py:149 — HTTP GET to `/api/pa/chat/status/<task_id>/` with polling.
- Error-handling: `urllib.error.HTTPError` caught; returns `(json_parsed, e.code)` tuple.
- **NO envelope shape validation** — all responses parsed via `json.loads()` then dict-key access.
- **NO retry policy** except polling loop for task-completion.

## 6. Major APIs and Interfaces

**Playbook §9 canonical Q6 — What are the major APIs?**

### 6.1 assistantApi canonical method inventory (F-B5 denominator lock — explicit list)

**F-B5 discipline (SIGN-preview fold):** Cat B denominator is the **explicit list of exported assistantApi methods** at `frontend/src/lib/api.ts:1147-1230`, NOT "subset of 93 apiModule / 856 method-invocation platform denominator." F-B1 fold provides grep-locked region markers (start `^export const assistantApi = \{` at line 1147; end matching `}` at line 1230).

**Denominator (F-B5 lock):** **20 assistantApi methods.**

| # | Method | api.ts line | HTTP verb | Backend endpoint (Cat A §6.1 row) | Typed generic `<T>` | Typed T name |
|---|---|---|---|---|---|---|
| 1 | `chat` | 1150 | POST | `/api/assistant/chat/` (Cat A row 3) | ❌ NO | — |
| 2 | `paChat` | 1155 | POST | `/api/pa/chat/` (Cat A row 16) | ✅ YES | `PAChatAsyncResponse` |
| 3 | `paChatStatus` | 1159 | GET | `/api/pa/chat/status/<task_id>/` (Cat A row 17) | ✅ YES | `PAChatStatusResponse` |
| 4 | `getPAContext` | 1163 | GET | `/api/pa/context/` (Cat A row 19) | ❌ NO | — |
| 5 | `listConversations` | 1166 | GET | `/api/pa/conversations/` (Cat A row 20) | ✅ YES | inline `{ success, conversations: ConversationSummary[] }` |
| 6 | `getConversation` | 1169 | GET | `/api/pa/conversations/<id>/` (Cat A row 22) | ✅ YES | inline conversation-detail shape |
| 7 | `createConversation` | 1174 | POST | `/api/pa/conversations/new/` (Cat A row 21) | ✅ YES | inline `{ success, conversation_id: string }` |
| 8 | `transcribe` | 1178 | POST (FormData) | `/api/assistant/transcribe/` (Cat A row 4) | ❌ NO | — |
| 9 | `voiceChat` | 1185 | POST (FormData) | `/api/assistant/voice/` (Cat A row 5) | ❌ NO | — |
| 10 | `speak` | 1194 | POST | `/api/tts/speak/` (NOT in Cat A F11 — TTS domain adjacent) | ❌ NO | — |
| 11 | `getContext` | 1198 | GET | `/api/assistant/context/` (Cat A row 7) | ❌ NO | — |
| 12 | `getLearning` | 1199 | GET | `/api/assistant/learning/` (Cat A row 8) | ❌ NO | — |
| 13 | `getPreferences` | 1200 | GET | `/api/assistant/preferences/` (Cat A row 6) | ❌ NO | — |
| 14 | `getAttentionItems` | 1201 | GET | `/api/assistant/attention-items/` (Cat A row 13) | ❌ NO | — |
| 15 | `getTaskProgress` | 1202 | GET | `/api/assistant/task-progress/` (Cat A row 9) | ❌ NO | — |
| 16 | `getActivityFeed` | 1205 | GET | `/api/pa/activity/?hours=<n>` (Cat A row 25) | ❌ NO | — |
| 17 | `getUnifiedAttention` | 1208 | GET | `/api/assistant/attention/unified/` (Cat A row 14) | ❌ NO | — |
| 18 | `getAttentionStats` | 1221 | GET | `/api/assistant/attention/stats/` (Cat A row 15) | ❌ NO | — |
| 19 | `feedback` | 1224 | POST | `/api/assistant/feedback/` (Cat A row 11) | ❌ NO | — |
| 20 | `reset` | 1226 | POST | `/api/assistant/reset/` (Cat A row 12) | ❌ NO | — |

**Denominator = 20 methods.** Typed-generic count = **5**. Typed-generic rate = **5/20 = 25%** per F-B5 methodology.

**Baseline comparison (evidence-only, Cat B boundary):**
- Platform typed rate (S2502): **7.36%** (63/856 within api.ts).
- assistantApi typed rate: **25%** (5/20 within F-B5 explicit denominator).
- **assistantApi EXCEEDS platform baseline by ~3.4x.** Cat B records observation; no verdict on "should retrofit to 100%" per Cat A §6.2 S2 anti-verdict discipline inheritance.

**Backend endpoint coverage (Cat A §6.1 cross-reference):**
- assistantApi covers 16 of Cat A's 34 F11 canonical PA-path endpoints via 1:1 mapping (rows 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 25 = 19 rows referenced above; some methods hit multiple Cat A rows).
- Cat A rows NOT covered by assistantApi at HEAD: rows 1 (`/api/v1/assistant/context/` compat), 2 (`/api/v1/assistant/chat/` legacy), 10 (`/api/assistant/bypass/` alias), 18 (`/api/pa/feedback/` PaMessageFeedback), 23 (`/api/pa/conversations/<id>/message/`), 24 (`/api/pa/conversations/<id>/messages/`), 26 (`/api/pa/conversations/<id>/health/`), 27 (`/api/pa/boardroom/maintenance/`), 28-30 (F2F voice_session/{create,speak,end}/), 31-34 (dev/minimal routes UNKNOWN).
- Cat B observation (evidence-only): assistantApi coverage of PA-path REST surface = **~47% direct** (16/34 rows); remaining 18 endpoints either lack a client wrapper OR live in a different consumer surface (paStore CRUD helpers OR direct-fetch calls OR dev-only routes).

### 6.2 U6 WS envelope inventory turn 1 (F-B3 client-consumed scope clamp)

**F-B3 discipline (SIGN-preview fold):** U6 WS envelope inventory is limited to PA-client-consumed WS channels ONLY (subset of platform 120 WS routes per S2504 baseline); capped to 3 canonical PA-client message classes. Platform-wide WS enumeration is Cat D S2604 scope, NOT Cat B. NO strictness recommendation language per Cat B boundary discipline.

**PA-client WS subscription site at HEAD.** One primary subscription at `frontend/src/pages/CommandCenterPage.tsx:682-764`:

| Attribute | Value |
|---|---|
| Consumer file:line | `frontend/src/pages/CommandCenterPage.tsx:682-764` |
| WS channel URL | `ws://{host}/ws/pa/conversations/<activeConversationId>/?token=<auth-token>` |
| Subscription hook | `useWebSocket(wsEndpoint, { autoConnect, onMessage })` at line 683 |
| Auth mechanism | Token passed as URL query param (`?token=<auth-token>`) |
| Reconnection policy | Exponential backoff (3s interval, max 5 attempts) via `useWebSocket` at `hooks/useWebSocket.ts:24-58` (Agent 4 evidence) |
| Message parse | `data as { type: string, ... }` — untyped TypeScript assertion at line 686 |

**Three canonical PA-client message classes** (F-B3 fold cap enforced):

| # | Class label (Cat B renaming for F-B3 clarity) | Event `type` string(s) | Observed envelope shape | Envelope grade | Cat B observation |
|---|---|---|---|---|---|
| 1 | **chat-response streaming** | `message.created` | `{ type: 'message.created', message: { id, role, content, source, tools_used, timestamp } }` | `observed-JSON-only` (no `interface WSMessageCreated` declared at consumer; parsed via `data as {message: {...}}`) | Cat B evidence only |
| 2 | **task-status broadcast** | `agent.completed` | `{ type: 'agent.completed', execution_id, agent_name, status, completed_at, error_signature?, artifact_pointers?, timestamp? }` | `observed-JSON-only` (no `interface WSAgentCompleted` declared at consumer) | Cat B evidence only |
| 3 | **rigby.tool.* lifecycle** (F-B3 fold third-class renamed from "async-audio-url delivery" per verifier-loop pre-draft correction — audio_url is REST-embedded, NOT WS-delivered) | `rigby.tool.started` + `rigby.tool.completed` | `{ type: 'rigby.tool.{started\|completed}', trace_id, seq, tool_call_id, tool_name, started_at, latency_ms?, status? }` | `observed-JSON-only` (Session 1172 seed; ToolTickerEvent inline interface at paStore.ts:49-57 exists but NOT bound to WS parse at consumer) | Cat B evidence only |

**F-B3 fold third-canonical-class re-labeling (verifier-loop pre-draft correction).** The shape-card SIGN-preview F-B3 fold cited "async-audio-url delivery" as the third canonical PA-client WS message class. Six-parallel-Explore evidence at HEAD reveals **`audio_url` is NOT a WS-delivered message class**. Instead:
- `audio_url` appears as a **field of the REST `/api/pa/chat/status/<task_id>/` poll response envelope** (see `PAChatStatusResponse` interface at api.ts:1115 field list).
- The three actual WS message classes observed at consumer are `message.created` + `agent.completed` + `rigby.tool.{started,completed}`.
- Cat B re-labels the third canonical class as **"rigby.tool.* lifecycle events"** and records async-audio-url as **REST-embedded** at §6.3.

**Cat D S2604 handoff evidence baseline.** All 3 observed WS canonical message classes have envelope grade `observed-JSON-only` at HEAD — no `interface WSMessage*` declared at consumer, no runtime validator. This is Cat B evidence baseline; Path A (typed) / Path B (island connect-only) / Path C (SoT + streaming carve-out) verdict is Cat D S2604 scope per parent §3.D.

### 6.3 REST-embedded async-audio-url observation (F-B3 relabel — REST not WS)

`audio_url` field appears at:
- `frontend/src/lib/api.ts:1115` — `PAChatStatusResponse.audio_url?` optional field on REST poll response.
- Backend origin: `PAResponse.audio_url` field at `core/services/unified_pa_entrypoint.py:194` (S2601 §5 baseline).
- **Not delivered via WS channel** at HEAD; delivered via `/api/pa/chat/status/<task_id>/` poll response body when task completes.

Cat B observation (evidence-only): The "async-audio-url" delivery channel is **REST-embedded polling**, not WS-broadcast. Cat B records this as a boundary-neutral finding for future Cat D S2604 WS Path A/B/C decision + any post-verdict "should audio_url be WS-broadcast for lower latency?" investigation.

### 6.4 tools/pa_chat.py 3-way envelope contract (S2601 §7.1 flow inheritance)

Per Agent 3 Part E evidence:

**Request shape sent to `/api/pa/chat/`** (pa_chat.py:101-120 — `send_message` function):

```python
{
    "message": <str>,                        # required
    "context": {                             # merged with source/platform
        "source": <str>,                     # e.g., "claude-code"
        "platform": <str>,                   # e.g., "cli"
        **<user-supplied context dict>       # arbitrary merge
    },
    "source": <str>,                         # e.g., "claude-code"
    "platform": <str>,                       # e.g., "cli"
    "conversation_id": <str>                 # optional; omitted if None
}
```

**Response shape parsed from `/api/pa/chat/status/<task_id>/`** (pa_chat.py:149-175 — `poll_result` function):

```python
{
    "success": <bool>,                       # required
    "status": "processing" | "completed" | "failed",  # required
    "content": <str>,                        # optional (present on completed)
    "trace_id": <str>,                       # optional
    "tool_runs": [                           # optional
        {"tool": <str>, "ok": <bool>, "latency_ms": <int>, ...}
    ],
    "audio_url": <str> | null,               # optional (REST-embedded per §6.3)
    "intent": <str> | null,                  # optional
    "routed_to": <str> | null,               # optional
    "profile_completeness": <int>,           # optional (0-100)
    "latency_ms": <int>,                     # optional
    "error": <str>,                          # optional (present on failed)
    "conversation_id": <str>                 # optional
}
```

**Envelope contract observations (evidence-only, Cat B boundary):**
- No TypedDict / Protocol / BaseModel / dataclass at HEAD. All shapes parsed via untyped dict-key access.
- Envelope-shape parity with backend `PAResponse` dataclass at `core/services/unified_pa_entrypoint.py:194` (S2601 §5.1 baseline) is STRONG — same 13 fields observed.
- Envelope-shape parity with TypeScript `PAChatStatusResponse` at api.ts:1115 is STRONG — same 12 fields (missing conversation_id in one direction possible).
- **NO shared source-of-truth surface** binds pa_chat.py + api.ts + PAResponse. Three parallel declarations exist; drift is possible if backend renames field without updating pa_chat.py + api.ts in lockstep.

### 6.5 cockpitApi 96%-typed exemplar structural prerequisites (F-B6 fold — evidence-only "structural prerequisites present?" phrasing)

**F-B6 discipline (SIGN-preview fold):** Phrase applicability as "structural prerequisites present?" NOT "should we do it?" — evidence-only preservation.

| # | Prerequisite | Status at HEAD `7ddd8ce6` | Evidence |
|---|---|---|---|
| 1 | Does `frontend/src/types/pa.ts` exist? | **NEGATIVE** | `ls frontend/src/types/*` returns exactly 1 file: `cockpit.ts` (parent-Claude verifier-loop). S2502 §4.3 baseline UNCHANGED. |
| 2 | Does `frontend/src/hooks/paQueries.ts` (or similar) exist? | **NEGATIVE** | `ls frontend/src/hooks/*Queries*` returns exactly 1 file: `cockpitQueries.ts` (parent-Claude verifier-loop). S2502 §3.4 baseline UNCHANGED. |
| 3 | Does assistantApi import shared `api` axios instance from api.ts? | **POSITIVE** | assistantApi block at api.ts:1147-1230 uses `api.get(...)` / `api.post(...)` throughout (parent-Claude verifier-loop). Analog to cockpitApi.ts:1 import pattern (S2502 §3.4). |

**Structural prerequisite count at HEAD = 1 of 3 present.** Cat B records observation; assistantApi surface **DOES NOT satisfy the cockpitApi "sole exception across entire frontend API layer" pattern at HEAD** on structural grounds (2 of 3 prerequisites NEGATIVE). Path (a) typed-island retrofit would require creating `types/pa.ts` + `hooks/paQueries.ts` sibling artifacts. Cat B does NOT propose the retrofit per F-B8 no-file-moves discipline. Chris-D-verdict on Path (a) selection AND on prerequisite-file creation deferred to S2699 xx99.

## 7. Runtime Flows

**Playbook §9 canonical Q9 — What are the major runtime flows?**

**Cat B boundary: CLIENT-SIDE runtime flows only.** Backend PA agentic-loop flow is Cat A boundary, closed S2601 §7.

### 7.1 Frontend PA chat runtime flow (assistantApi.paChat + paChatStatus + WS supplement)

Client-side 8-step flow (Agent 3 + Agent 4 evidence):

1. **User submits message** — `CommandCenterPage.tsx:*` (compose-and-submit UI).
2. **`assistantApi.paChat(message, options)` invoked** — HTTP POST to `/api/pa/chat/` with `PAChatAsyncResponse` typed generic (api.ts:1155).
3. **HTTP 200 response** — `{ success: true, task_id: <uuid>, status: "processing" }` parsed via typed generic.
4. **Client stores task_id + starts polling** — `assistantApi.paChatStatus(task_id)` invoked at N-second interval (client-side polling loop; polling interval not centralized).
5. **HTTP 200 status response** — `PAChatStatusResponse` typed generic. Parsing branches:
   - `status: "processing"` → continue polling.
   - `status: "completed"` → extract `content`, `tool_runs`, `audio_url`, `trace_id`, etc.
   - `status: "failed"` → surface `error` to UI.
6. **paStore.addPAMessage(message)** — dispatches to `paStore` message queue.
7. **WS supplementary events** — during polling, WS channel `/ws/pa/conversations/<activeConversationId>/` broadcasts (Agent 3 Part B):
   - `message.created` — assistant/user message insert (dedup via `seenSeqs` field).
   - `agent.completed` — task-status supplementary broadcast.
   - `rigby.tool.started` + `rigby.tool.completed` — tool-ticker updates (populates `activeTool` + `recentTool`).
8. **UI renders response** — `RigbyToolTicker` (tool ticker), `AgentCompletionBanner` (agent completion), message list.

**Cat B observation:** REST polling + WS broadcast are **PARALLEL delivery channels** for overlapping information (task completion is both `PAChatStatusResponse.status = "completed"` REST + `agent.completed` WS event). Client-side dedup exists via `seenSeqs` field for message.created + `seenCompletions` field for agent.completed. **NO client-side reconciliation logic between REST status result and WS agent.completed event** at HEAD (both fire; UI treats them additively; Session 1175/1181 pattern seed).

### 7.2 tools/pa_chat.py CLI 3-step flow (S2601 §7.1 inheritance)

Per Agent 3 Part E evidence:

1. **User invokes** — `python tools/pa_chat.py "message" --tools --conversation <id>`.
2. **`chat()` at pa_chat.py:178** — invokes `send_message()` at pa_chat.py:101 (HTTP POST to `/api/pa/chat/`) — returns `(task_id, http_code)`.
3. **`poll_result(task_id)` at pa_chat.py:149** — HTTP GET `/api/pa/chat/status/<task_id>/` every `POLL_INTERVAL=3s` up to `POLL_TIMEOUT=300s`. Returns `(dict, None)` on completed, `(None, error)` on failed/timeout.

**Cat B observation:** CLI wrapper **DOES NOT subscribe to WS** — polling-only. Tool-run visibility for `--tools` flag comes from `PAChatStatusResponse.tool_runs` field on completion, not from `rigby.tool.*` WS events.

## 8. Data Ownership and Lifecycle

**Playbook §9 canonical Q16-Q18 — What data does PA-client own / consume / produce?**

**Cat B boundary: CLIENT-SIDE data ownership + lifecycle only.**

### 8.1 PA-client data owned

- paStore Zustand-managed 16 fields (§4.1) — client state; localStorage-persisted for 7 fields; memory-only for 9 fields.
- assistantContextStore.FocusedEntity — client state; ephemeral; passed to PA chat payload as `context.focused_entity`.
- assistantApi request-config metadata (Session 968 request-log 200-entry circular buffer at api.ts:3990-4048).

### 8.2 PA-client data consumed

- PA-REST response bodies (via assistantApi typed-generic + untyped calls).
- PA-WS message payloads (via useWebSocket hook + JSON parse).
- User auth token (via `useAuthStore.getState().token` at api.ts:27+ Auth interceptor).
- User workspace ID (via `workspaceStore.getState().workspaceId` at some assistantApi call-sites).

### 8.3 PA-client data produced

- HTTP POST request bodies at api.ts:1150+ (chat + paChat + createConversation + transcribe + voiceChat + speak + feedback + reset).
- WS messages: **NONE at HEAD** — PA-client is receive-only on WS channel; no outbound WS publish observed at CommandCenterPage.tsx or elsewhere in PA-client surface.
- localStorage writes: `pa-dock-state` key (7 partialized paStore fields) + `auth-storage` key (authStore).
- Session-968 request-log circular buffer (memory-only; MAX_LOG=200 at api.ts:4002).

### 8.4 Retention / lifecycle policies at HEAD

Per Agent 1 + Agent 3 evidence:

| Data class | Lifecycle | Wipe trigger |
|---|---|---|
| `pa-dock-state` localStorage | Persistent until user manually clears storage OR persist version migration | Version 3 migration on load (clears if v<3 detected); syncUser wipes 5 fields on user_id change; **NO wipe on `authStore.logout()`** (Agent 1 + Agent 4 evidence) |
| `messages` field (last-50 slice) | localStorage (7-slot partialize); last-50 truncation at write time | syncUser (on user_id change) |
| Ephemeral WS state (activeTool, recentTool, seenSeqs, recentAgentCompletion, agentCompletionQueue, seenCompletions) | Memory-only; NOT persisted | Component unmount / page refresh |
| Session-968 request-log | Memory-only circular buffer | 200-entry cap OR page refresh |
| `useWebSocket` reconnection state | Memory-only | Component unmount OR max reconnect attempts (5) reached |

**Cat B observation (evidence-only, → Cat C2 S2603 pointer for 2 UNKNOWN intent fields):**
- `authStore.logout()` at authStore.ts:1-53 (Agent 1 evidence) clears token/user/isAuth but does NOT trigger explicit `localStorage.removeItem('pa-dock-state')` OR `usePAStore.getState().reset()`.
- 2 paStore fields (`isDockOpen`, `isDockMinimized`) survive logout in localStorage. Intent = **UNKNOWN**; Cat C2 S2603 owns retention-window verdict.
- `messages` field survives logout in localStorage (last-50 slice); intent = **chat-history retention**; Cat C2 S2603 session-lifecycle input.

## 9. Integrations With Other Domains

**Playbook §9 canonical Q14 + Q17 + Q18 + Q21 + Q22 — Integrations.**

Per Agent 4 evidence + parent-Claude verifier-loop cross-check:

| Domain | Mechanism | File:line origin | Cat B evidence |
|---|---|---|---|
| **Auth** | `useAuthStore.getState().token` in Auth interceptor | api.ts:27-40 (Auth); authStore.ts:1-53 (store) | Token attachment uniform across all api.* calls; no PA-endpoint branching |
| **Workspace** | `workspaceStore.getState().workspaceId` in call sites; passed as `workspace_id` payload field | workspaceStore.ts:1-28 (store); scattered call-site inclusion | Workspace context passed to PA chat via `options.workspace_id`; handler-internal `execute_with_workspace()` at `core/agents/base_agent.py:5355` enforces membership (Cat C1 S2603 scope) |
| **Assistant Context** | `assistantContextStore.getState().focused` in call sites; passed as `context.focused_entity` | assistantContextStore.ts:1-29 (store) | FocusedEntity type = deliverable / initiative / action_item / attention / file |
| **PA-REST** | 20 assistantApi methods → 16 of 34 Cat A F11 endpoints | api.ts:1147-1230 | Direct mapping in §6.1 |
| **PA-WS** | `useWebSocket` subscription to `/ws/pa/conversations/<id>/` | hooks/useWebSocket.ts:24-58; CommandCenterPage.tsx:682-764 | 3 canonical message classes (§6.2) |
| **CLI (tools/pa_chat.py)** | HTTP-only; no WS subscription | pa_chat.py:1-500 | 3-way envelope contract §6.4 |
| **Discord** | NOT INTEGRATED at PA-client layer | N/A | Anti-scope #5 preserved; verified: no Discord webhook adapter at PA-client surface |
| **Content** | assistantApi hits `/api/assistant/*` + `/api/pa/*`; NOT `/api/content/*` | N/A | Anti-scope #6 preserved |

**Integration boundary observation (evidence-only):** PA-client integrations are **layered, not orchestrated at api.ts**. Auth token, workspace_id, focused_entity are collected from 3 separate Zustand stores at call-site (component layer or paStore layer); assistantApi is dumb-pass-through. NO client-side integration orchestration service exists (analog to backend UnifiedPAEntrypoint).

## 10. Event Flows

**Playbook §9 canonical Q19-Q20 — What events emitted / should be emitted?**

**Cat B boundary: CLIENT-SIDE event flows only.**

### 10.1 PA-client events currently observed

- **UI events (React):** message submit, dock open/close/minimize, sidebar toggle, tool-ticker fade, agent-completion banner dismiss.
- **paStore events (Zustand actions):** `addPAMessage`, `handleToolStarted`, `handleToolCompleted`, `handleAgentCompleted`, `setActiveConversation`, `syncUser`, `openDock`, `closeDock`, etc. (Agent 3 evidence).
- **WS events consumed** (§6.2): `message.created`, `agent.completed`, `rigby.tool.started`, `rigby.tool.completed`.
- **REST events consumed** (§6.4): `paChatStatus` polling — completed / processing / failed status transitions.
- **Session-968 request-log events**: request-start, request-complete (Agent 2 evidence).

### 10.2 PA-client events that could be emitted (evidence for §19)

- **Envelope-parse failure telemetry** — NO client-side event fires when `PAChatStatusResponse.tool_runs` field is missing or malformed. Silent typing hole.
- **Silent-401 telemetry** — NO client-side event fires when Silent-401 interceptor swallows a non-whitelist 401 (S1505 §14.3 F3 pattern; whitelist substring `/auth/` + `/login/` at api.ts:50). Debt Cat C S2503 scope.

## 11. Existing Documentation

**Playbook §9 canonical Q10-Q11 — Existing documentation + prior research.**

Per Agent 5 evidence:

| Doc | File:line | Cat B coverage |
|---|---|---|
| `docs/topics/personal-assistant.md` | 1-148 | Describes agentic loop + tool schemas + async processing; **does NOT declare assistantApi methods** OR paStore field list OR WS envelope shapes. Line 13 claim "104 OpenAI function-calling tool schemas" is DRIFT (runtime authoritative = 113; S2601 §14.2 drift confirmed unchanged) |
| `docs/topics/frontend.md` | 61-71 (PA integration) + 131-132 (cockpit exemplar) | PA integration described but assistantApi methods NOT enumerated; assistantApi listed as 1 of 4 cross-cutters at line 132; cockpitApi 96%-typed exemplar declared at line 131 (assistantApi NOT declared as typed) |
| `docs/PLATFORM_WHAT_IT_IS.md` | 188-228 (PA subsystem) | PA narrative; **no client-side surface mention**; line 192 claim "109 tool schemas" and line 219 diagram claim "101 tool schemas" — INTERNAL CONTRADICTION AND DRIFT (S2601 §14.2 caught 104 in personal-assistant.md; runtime authoritative = 113) |
| `docs/PLATFORM_INVENTORY.md` | 143 (autoblock) | Authoritative "113 tool schemas + 156 handlers + 8 enrichment services" — Cat A verified |
| `CLAUDE.md` | 7-36 (Rigby coord), 94-104 (async processing), 212 (canonical route) | Line 34 declares `POST /api/pa/chat/` canonical + `/api/assistant/chat/` + `/api/v1/assistant/chat/` compat; NO client-side envelope contract declared |
| `docs/research/domains/pa/2600_pa_domain_scoping.md` | full | DIRECT PARENT — §3.B Cat B scope + §5.3 AC + §2.5 U6/U7 gaps + §2.6 lens |
| `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` | full | SIBLING PRIOR-CHILD — §6.1 F11 canonical inventory + §7.2 streaming-negative + §14 verifier corrections |
| `docs/research/domains/api/2502_api_frontend_client_architecture_design_prep_audit.md` | full | PARENT-ARC PREDECESSOR — cockpitApi 96%-typed exemplar + 7.36% platform typed rate + 93 apiModule |
| `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` | full | PREDECESSOR — assistantApi cross-cutter finding (1 of 4 cross-cutters) |
| `docs/research/domains/api/2599_api_canonical_summary.md` | full | Group 2500 canonical verdict — §2.6.A hard constraint inheritance |
| `tools/pa_chat.py` (inline docstring) | 1-10 | 3-way usage documentation (talk to Rigby / store-only / watch); envelope shape NOT declared in docstring |

## 12. Research Coverage

**Playbook §12 classification.**

**PA-CLIENT CONTRACT SURFACE research coverage at S2602 close: MODERATE-DEEP (upgrading toward DEEP as Group 2600 arc closes).**

Evidence:
- Prior Group 2500 arc S2502 provides DEEP baseline on api.ts consumer architecture at platform level.
- Prior Group 2200 arc S2203 provides DEEP baseline on assistantApi cross-cutter role.
- This audit (S2602) contributes DEEP evidence for PA-client-specific contract-typing + field-list + WS-envelope inventory.
- Cat C1 + Cat C2 (S2603) + Cat D (S2604) will complete Group 2600 arc — expected DEEP at arc close.

## 13. Architecture Maturity

**Playbook §12 classification.**

**PA-CLIENT CONTRACT SURFACE architecture maturity at HEAD `7ddd8ce6`: PARTIAL.**

Rationale (evidence-only per Cat B boundary):
- **PARTIAL best-fit:** assistantApi has **partial** typed-generic adoption (5/20 = 25%, up from platform 7.36% baseline); paStore has inline TypeScript typing for 16 fields but NO cross-file `types/pa.ts`; tools/pa_chat.py has ZERO typed envelope surface. Two of three surfaces have partial declaration; third has none.
- **Distinction from EXPERIMENTAL:** PA-client is NOT experimental — it is production-load-bearing (Rigby coord flow per CLAUDE.md; primary chat surface). Runtime is stable.
- **Distinction from WORKING:** WORKING would require observable declaration surface with source-of-truth binding. 2 of 3 structural prerequisites for cockpitApi-analog pattern NEGATIVE at HEAD.

**Distinguish from MECHANISM-layer maturity:** PA-client MECHANISM (WS subscription + REST polling + Zustand persist + interceptor stack + auth injection) is WORKING or STABLE — that's a different question owned by S2502 baseline + `docs/topics/frontend.md`. Cat B owns DECLARATION-layer classification only.

## 14. Known Drift

**Playbook §9 canonical Q27 — Drift.**

### 14.1 Drift resolved by verifier-loop pre-draft (7 corrections, cross-Agent reconciliation)

Recorded in frontmatter `verifier_loop` field. Reproduced here for §-anchor:

1. **apiModule count** = 93 at HEAD (Agent 6 claim of 94 REFUTED via direct `^export const \w+Api\s*=` grep).
2. **assistantApi region markers** = api.ts:1147-1230 (F-B1 grep-locked start/end anchors verified).
3. **assistantApi method count** = 20 (Agent 3 table matches; Agent 6 claim of 11 REFUTED).
4. **assistantApi typed-generic count** = 5 (Agent 3 text said 4, table showed 5 — direct grep confirms 5).
5. **assistantApi typed rate** = 5/20 = **25%** per F-B5 methodology.
6. **Silent-401 status check** at api.ts:48 (S2502 baseline confirmed); interceptor block spans 43-62.
7. **paStore.ts LOC** = 449 (Agent 1 said 434; Agent 3 said 450 — direct wc -l confirms 449).

### 14.2 Drift confirmed at HEAD (Cat B evidence)

- **`docs/topics/personal-assistant.md:13` claim "104 OpenAI function-calling tool schemas"** — DRIFT preserved from S2601 §14.2; runtime authoritative = 113 per PLATFORM_INVENTORY. Severity MEDIUM. Cat B records; §19.3 MEDIUM follow-on for docs cascade.
- **`docs/PLATFORM_WHAT_IT_IS.md:192` claim "109 tool schemas" AND :219 diagram claim "101 tool schemas"** — INTERNAL CONTRADICTION AND DRIFT. Both diverge from runtime 113. Severity MEDIUM. Cat B records; §19.3 MEDIUM follow-on. **NEW DRIFT NOT PREVIOUSLY LOGGED in Cat A** (S2601 §14.2 caught 104 in personal-assistant.md only; PLATFORM_WHAT_IT_IS variants surfaced at Cat B).
- **assistantApi typed-response contract for interfaces `UnifiedPAResponse` / `PAChatAsyncResponse` / `PAChatStatusResponse`** — Documentation gap (not drift): interfaces exist at api.ts:1085+ but no `docs/topics/personal-assistant.md` or `docs/topics/frontend.md` reference. Severity LOW; §19.3 MEDIUM follow-on.
- **pa_chat.py 3-way envelope contract undocumented outside file** — Documentation gap (not drift): envelope shape lives in inline comments at pa_chat.py:101-175; no external doc reference. Severity LOW; §19.3 MEDIUM follow-on.

### 14.3 Drift observation from Agent 6 verify_doc_claims run

Per Agent 6 evidence: `verify_doc_claims` at HEAD reports 73 total claims across 34 docs; **ZERO PA-CLIENT claims registered**. Declaration-layer drift detection for PA-client is UNMONITORED at HEAD. Cat A §14.3 caught same class of gap for REST-boundary. Cat B records + §19.3 follow-on: register PA-client contract-shape claims for future drift detection.

## 15. Known Technical Debt

**Playbook §9 canonical Q26 — Technical debt.**

### 15.1 Contract-typing debt (Cat B boundary scope)

- **DEBT-B-1:** 15/20 assistantApi methods untyped (75% remaining at platform baseline 7.36%). Cat B records; owner Chris-D-verdict at S2699 xx99 (Path (a) full retrofit / Path (b) SHAPE-BLIND preserved / Path (c) hybrid).
- **DEBT-B-2:** `frontend/src/types/pa.ts` DOES NOT EXIST. Prerequisite for cockpitApi-analog exemplar (F-B6 fold prerequisite #1). Severity LOW-MEDIUM if Path (b) ratified; MEDIUM-HIGH if Path (a) ratified.
- **DEBT-B-3:** `frontend/src/hooks/paQueries.ts` DOES NOT EXIST. Prerequisite #2. Severity mirrors DEBT-B-2.
- **DEBT-B-4:** paStore.ts has 16 inline interfaces + duplicates `ConversationSummary` with api.ts:1131. NO cross-file type consolidation. Severity LOW; owner post-verdict cleanup.
- **DEBT-B-5:** tools/pa_chat.py has ZERO typed envelope (100% untyped dict). Severity MEDIUM if Path (a) ratified with tools/ scope; owner Chris-D-verdict at S2699 xx99.
- **DEBT-B-6:** 3 WS canonical message classes at HEAD have envelope grade `observed-JSON-only` — NO TypedDict / interface / runtime validator. Cat D S2604 scope; Cat B records evidence baseline only.
- **DEBT-B-7:** No source-of-truth binding between backend `PAResponse` dataclass + frontend `UnifiedPAResponse` interface + `tools/pa_chat.py` response envelope. Three parallel declarations. Silent drift possible if backend renames field. Severity MEDIUM; owner Chris-D-verdict at S2699 xx99 (SHAPE-BLIND accepts drift; typed-island requires shared schema mechanism e.g., codegen from OpenAPI or drf-spectacular).

### 15.2 Cross-arc coordination debt (adjacent to Cat B)

- **F-B-HIGH-3** workspace-membership implicit-gate — Cat A §16.1 records; Cat C1 S2603 owns closure. **Cat B does not re-litigate per F-B7 fold single-sentence discipline.**
- **CF-C2** session-lifecycle handoff — Cat C2 S2603 owns. Cat B U7 field-list dump provides input (2 UNKNOWN intent fields → Cat C2 pointer).
- **CF-D6** REST↔WS T7 joint contract SoT — Cat D S2604 owns. Cat B U6 WS envelope inventory provides input.

## 16. Boundary Violations

**Playbook §9 canonical Q24 — Boundary violations.**

### 16.1 F-B-HIGH-3 workspace-membership implicit-gate (Cat A §16.1 inheritance — single sentence per F-B7 fold)

**Attribution:** Workspace-membership implicit-gate at `core/agents/base_agent.py:5355 execute_with_workspace()` is Cat C1 S2603 scope; Cat B contract-typing decision-space is INDEPENDENT of F-B-HIGH-3 closure per S2504 §88 orthogonality.

### 16.2 PA-adjacent boundary preservation (anti-scope verification)

Verifier confirmed at HEAD:
- **Anti-scope #5 (Discord bot PA proxy):** NOT VIOLATED — assistantApi does NOT call Discord webhook adapters (Agent 4 evidence: no Discord adapter under `frontend/src/*`).
- **Anti-scope #6 (Content Studio PA endpoints):** NOT VIOLATED — assistantApi hits `/api/assistant/*` + `/api/pa/*`; NOT `/api/content/*`.
- **Anti-scope #7 (Fleet HMAC PA signature):** NOT VIOLATED — client does NOT emit `X-Fleet-Signature` header (that's cross-repo fleet-federation surface; frontend runs same-origin auth).

### 16.3 F1 fold hard-boundary preservation at Cat B draft (F-B8 no-file-moves discipline)

Cat B draft compliance verified:
- Cat B did NOT propose UI/UX behavior changes.
- Cat B did NOT propose Zustand slice consolidation.
- Cat B did NOT propose frontend build/bundling changes.
- Cat B did NOT propose frontend testing framework decisions.
- Cat B did NOT propose creating `types/pa.ts` OR `hooks/paQueries.ts` files (F-B8 fold).
- Cat B did NOT retrofit typed generics onto assistantApi.
- Cat B did NOT enumerate WS envelope Path A/B/C option space (Cat D S2604 owned).
- Cat B did NOT ratify F-B-HIGH-3 closure (Cat C1 S2603 owned per F-B7 fold).

### 16.4 Cat-B micro-anti-scope enumeration (F-B9 fold — explicit ID-stable list)

**F-B9 discipline (SIGN cycle 1 fold Chris-ratified 2026-07-06):** Cat B micro-anti-scope items get **explicit ID-stable enumeration** (Cat-B-1 through Cat-B-9) even though the underlying negatives are also asserted in §2 domain-purpose bullets + §16.3 F1-fold checklist + top-of-doc boundary block. Explicit ID list prevents downstream slippage and provides referenceable anchors for S2603/S2604/S2699 sibling audits.

Cat B inherits parent §7 anti-scope items #1-#10 unchanged (LLM provider/model policy + agent timeout tuning + memory persistence + Discord bot PA proxy + Content Studio PA + Fleet HMAC PA signature + PA token / auth token rotation + agent-registry mutations + prompt engineering + PA behavior mutations). Additional Cat-B-specific micro-anti-scope:

- **Cat-B-1** — Cat B does NOT propose UI/UX behavior changes for message rendering, tool-run display, streaming UX, dock open/close animations, sidebar interactions, or any other user-facing UX (F1 fold explicit).
- **Cat-B-2** — Cat B does NOT propose Zustand slice consolidation, useEffect discipline refactors, or any state-management restructuring (F1 fold explicit).
- **Cat-B-3** — Cat B does NOT propose frontend build/bundling changes (Vite config / dependency updates / bundler swaps / etc.) (F1 fold explicit).
- **Cat-B-4** — Cat B does NOT propose frontend testing framework decisions (Vitest coverage / RTL adoption / E2E strategy / etc.) (F1 fold explicit).
- **Cat-B-5** — Cat B collects EVIDENCE only; Chris-D-verdict on Path (a) typed / (b) SHAPE-BLIND / (c) hybrid / (d) UNKNOWN deferred to S2699 xx99 (Cat A §20.7 boundary discipline inheritance).
- **Cat-B-6** — Cat B does NOT retrofit typed generics onto assistantApi surface (evidence-only; retrofit is post-verdict implementation scope).
- **Cat-B-7** — Cat B does NOT ratify F-B-HIGH-3 closure (Cat C1 S2603 owned per parent §3.C1 + S2601 §16.1 attribution + F-B7 single-sentence discipline).
- **Cat-B-8** — Cat B does NOT enumerate WS envelope Path A/B/C option space (Cat D S2604 owned per parent §3.D).
- **Cat-B-9** — Cat B does NOT create new shared `frontend/src/types/pa.ts` file, NEW `frontend/src/hooks/paQueries.ts` file, or any other Cat-B-scope file moves / creations / relocations (F-B8 fold explicit; even creating a placeholder `types/pa.ts` is a change; Cat B observes only).

## 17. Duplicate or Overlapping Systems

**Playbook §9 canonical Q23 — Duplicate/overlapping systems.**

- **3 parallel chat endpoints (S2601 §17 inheritance)** — client-side call distribution UPDATED at Cat B:
  - `/api/pa/chat/` — called via `assistantApi.paChat` (api.ts:1155) — **DOMINANT async path** (typed via `PAChatAsyncResponse`).
  - `/api/assistant/chat/` — called via `assistantApi.chat` (api.ts:1150) — **LEGACY sync path** (untyped; api.ts:1149 inline comment "old hardcoded prompt from views_image.py"; effectively deprecated).
  - `/api/v1/assistant/chat/` — **NOT CALLED FROM FRONTEND CLIENT AT HEAD** (Agent 4 + Agent 6 verified). Cat B evidence extends Cat A §17 finding: v1 legacy endpoint is DEAD-CODE from client perspective.
- **`ConversationSummary` duplicate declaration** — paStore.ts:35-41 + api.ts:1131 (approx). Cat B records; consolidation is post-verdict scope per F-B8 no-file-moves discipline.
- **REST + WS parallel delivery for task completion** — `PAChatStatusResponse.status="completed"` (REST polling) + `agent.completed` (WS event) fire in parallel per §7.1. Cat B records observation; NO client-side reconciliation logic at HEAD (both trigger UI additively via dedup via `seenCompletions`).

## 18. Ownership Gaps

**Playbook §9 canonical Q25 — Ownership gaps.**

Per Agent 5 + CODEOWNERS cross-check:

**PA-client code paths NOT explicitly listed in CODEOWNERS:**
- `frontend/src/lib/api.ts` — falls to default `* @clwest`
- `frontend/src/lib/cockpitApi.ts` — UNASSIGNED per CODEOWNERS lines 8-13 explicit deferral to S2600+ (S2502 §14 F7 + F8 baseline preserved at HEAD)
- `frontend/src/lib/apiClient.ts` — UNASSIGNED per same
- `frontend/src/hooks/*` — UNASSIGNED per same
- `frontend/src/types/*` — UNASSIGNED per same
- `frontend/src/stores/paStore.ts` — falls to default
- `frontend/src/pages/CommandCenterPage.tsx` — falls to default
- `frontend/src/components/GlobalPADock.tsx` — falls to default
- `tools/pa_chat.py` — falls to default

**PA doc paths EXPLICITLY listed:**
- `/docs/topics/ @clwest` (includes personal-assistant.md + frontend.md)
- `/docs/PLATFORM_INVENTORY.md @clwest` (PA counts anchor)

**Ownership-gap observation (evidence-only):** PA-client code ownership is via default fallback per Cat A §18 baseline. Cat B records; **S2699 xx99 anchor-update recommendation candidate:** PA-client-slice CODEOWNERS discipline (analog to Group 2500 API-slice CODEOWNERS refinement pending at S2599 close residuals; Cat A §18 baseline preserved).

## 19. Recommended Future Research

**Playbook §9 canonical Q28 — What should be researched next?**

Cat B DOES NOT recommend implementation. Cat B recommends **evidence-collection follow-ons** ranked by architectural uncertainty × risk × unblocked flows:

### 19.1 CRITICAL — Blocks Chris-D-verdict at S2699 xx99

1. **Cat C2 S2603 owns 2-of-16 UNKNOWN intent fields at paStore** (`isDockOpen`, `isDockMinimized` — dock-state persistence intent on logout / cross-user UNCONFIRMED at HEAD; NOT wiped by syncUser; NOT wiped by authStore.logout). C2 verdict blocks Cat B U7 field-list closure completion (F-B4 fold: UNKNOWN dispositions allowed with pointer; final resolution downstream).
2. **Cat D S2604 owns WS envelope Path A/B/C verdict** on 3 canonical PA-client message classes (§6.2 evidence baseline: `observed-JSON-only` for all 3). Cat B provides evidence; D verdict blocks Group 2600 arc close on WS side.

### 19.2 HIGH — Enables Chris-D-verdict at S2699 xx99

3. **`types/pa.ts` file creation decision at Path (a) ratification** — F-B6 fold prerequisite #1 NEGATIVE at HEAD. If Chris ratifies Path (a) typed assistantApi.ts island at xx99, S2701+ session drafts creation of `frontend/src/types/pa.ts` + population from `PAResponse` dataclass + supporting interfaces + import into assistantApi region + typed-generic retrofit for 15 untyped methods.
4. **`hooks/paQueries.ts` file creation decision at Path (a) ratification** — F-B6 fold prerequisite #2 NEGATIVE at HEAD. Same conditional as (3).
5. **Backend↔frontend schema source-of-truth binding decision (DEBT-B-7)** — Chris-D-verdict at xx99 on: (i) drf-spectacular codegen (blocked by Group 2500 platform-wide wire-up), (ii) hand-maintained mirror with drift-detection CI check, (iii) SHAPE-BLIND accept-drift explicitly.
6. **Cat D S2604 evidence follow-on (F-B10 fold — boundary-neutral rephrase per SIGN cycle 1 STRENGTHEN 2026-07-06):** verify whether any WS path currently carries `audio_url` (expected NEGATIVE per Cat B §6.3 — audio_url is REST-embedded in PAChatStatusResponse only at HEAD) and, if negative, record as evidence for xx99 contract-binding discussion. This is boundary-neutral EVIDENCE COLLECTION scope for Cat D; F-B10 SIGN cycle 1 STRENGTHEN preserved Cat B evidence-only discipline by dropping the "MIGRATE from REST-embedded to WS-broadcast" language that edged into Cat D option-space enumeration.

### 19.3 MEDIUM — Post-arc follow-on

7. **`docs/topics/personal-assistant.md` line 13 drift fix** — 104 → 113 tool schemas (S2601 §14.2 + Cat B §14.2 preserved).
8. **`docs/PLATFORM_WHAT_IT_IS.md` line 192 + line 219 drift fix + internal-contradiction resolution** — 109 vs 101 vs runtime 113. NEW drift surfaced at Cat B §14.2.
9. **assistantApi + paStore + pa_chat.py client-envelope documentation section in `docs/topics/personal-assistant.md`** — Documentation gap (not drift); §14.2 records.
10. **PA-client contract-shape claims registration in `core/services/doc_claim_verification.py`** — `verify_doc_claims` has ZERO PA-CLIENT claims at HEAD (§14.3). Analog to Cat A §14.3 gap. Post-arc follow-on candidate.
11. **PA-client-slice CODEOWNERS discipline** — analog to Group 2500 API-slice pending at S2599 close residuals (§18).
12. **assistantApi coverage of PA-path REST endpoints (~47% direct = 16/34 at HEAD per §6.1)** — 18 Cat A F11 endpoints lack assistantApi wrappers OR live in different consumer surface. Cat B records; audit whether uncovered endpoints have alternative consumer paths OR are dead-client-code.
13. **paStore.ts + api.ts `ConversationSummary` duplicate consolidation** (§17).
14. **`frontend/src/hooks/useWebSocket.ts` typed WS envelope wrapping** — if Path A typed WS envelope ratified at Cat D S2604, useWebSocket hook receives typed generics; Cat B records evidence baseline for Cat D input.

## 20. Appendix

### 20.1 Files inspected

Absolute paths + relevant line ranges:

- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/lib/api.ts` — 4194 LOC total; assistantApi region 1147-1230; Auth interceptor 27-40; Silent-401 interceptor 43-62 (status check line 48); Session-968 request-log interceptors 3990-4048; UnifiedPAResponse interface 1093; PAChatAsyncResponse ~1105; PAChatStatusResponse 1115; ConversationSummary ~1131; ToolRun 1085
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/lib/cockpitApi.ts` — 513 LOC; 54 exported functions; 52 typed-generic; nested envelope-unwrap at line 66-68
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/lib/apiClient.ts` — 29 LOC; scopedGet 8-17; scopedPost 19-29
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/types/cockpit.ts` — 820 LOC; 104 exported types
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/hooks/cockpitQueries.ts` — 485 LOC; 42 React Query hooks (S2502 baseline)
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/hooks/useWebSocket.ts` — 24-58 hook factory; exponential backoff reconnection
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/stores/paStore.ts` — 449 LOC; store 79-149; initial state 156-179; syncUser 182-194; store creators 79+; selectors 436-449; inline interfaces 14-77; persist config 395-432
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/stores/authStore.ts` — 1-53; token/user/isAuth; `'auth-storage'` persist key
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/stores/workspaceStore.ts` — 1-28; workspace context; no-persist
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/stores/assistantContextStore.ts` — 1-29; FocusedEntity; no-persist
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/pages/CommandCenterPage.tsx` — 682-764 WS subscription block; 653-666 paStore selectors; 855-1182 React Query hooks + async mutations
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/pages/GovernmentPage.tsx` — 2 assistantApi direct calls
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/components/GlobalPADock.tsx` — 4 assistantApi direct calls; line 104 paStore destructure
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/components/RigbyToolTicker.tsx` — 17, 22, 35 paStore selectors
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/components/AgentCompletionBanner.tsx` — 20, 35, 85 paStore selectors
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/components/PAConversationSidebar.tsx` — 13, 41
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/components/platform/AttentionWidget.tsx` — 3 assistantApi direct calls
- `/Users/donkeyking/development/unified-donkey-betz/frontend/src/App.tsx` — 49 syncUser call
- `/Users/donkeyking/development/unified-donkey-betz/tools/pa_chat.py` — 500 LOC total; chat 178; send_message 101; poll_result 149; POLL_INTERVAL/POLL_TIMEOUT 44
- `/Users/donkeyking/development/unified-donkey-betz/tests/test_pa_chat_defaults.py` — 19 (`from tools import pa_chat`)
- `/Users/donkeyking/development/unified-donkey-betz/CODEOWNERS` (48 lines) — S2502 §14 F7/F8 UNASSIGNED cockpitApi/apiClient/hooks/types preserved at HEAD
- `/Users/donkeyking/development/unified-donkey-betz/frontend/package.json` — verified NO runtime validator (no zod/io-ts/superstruct/valibot/yup/arktype/typebox)

### 20.2 Docs inspected

- `docs/topics/personal-assistant.md` (1-148; line 13 drift; line 26 documentation gap)
- `docs/topics/frontend.md` (61-71 PA integration; 131-132 cockpit exemplar + assistantApi cross-cutter)
- `docs/PLATFORM_WHAT_IT_IS.md` (188-228; line 192 drift; line 219 diagram drift)
- `docs/PLATFORM_INVENTORY.md` (143 autoblock; authoritative 113/156/8)
- `CLAUDE.md` (7-36, 94-104, 212, 223)
- `docs/research/domains/pa/2600_pa_domain_scoping.md` (full — DIRECT PARENT)
- `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` (full — SIBLING PRIOR-CHILD)
- `docs/research/domains/api/2502_api_frontend_client_architecture_design_prep_audit.md` (full — PARENT-ARC PREDECESSOR)
- `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` (full — PREDECESSOR)
- `docs/research/domains/api/2599_api_canonical_summary.md` (full — Group 2500 canonical verdict)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template; §13 Explore contract; §14 verifier-loop; §15 SIGN discipline; §21 short-command vocabulary)
- `MEMORY.md` (feedback rules cited: `feedback_rigby_sign_worker_instability_recovery.md`, `feedback_verifier_loop_pattern.md`, `feedback_cascade_pr_must_include_embed_step.md`, `feedback_docs_cascade_at_every_close.md`)

### 20.3 Grep patterns used

- `^export const \w+Api\s*=` in frontend/src/lib/api.ts (verifier: apiModule denominator; = 93 at HEAD)
- `^export const assistantApi = \{` in api.ts (verifier: F-B1 grep-locked start marker; line 1147)
- `api\.\w+<` in region api.ts:1147-1230 (verifier: typed-generic count in assistantApi; = 5)
- `api\.(get|post|put|delete|patch)\s*<?\s*(` in region api.ts:1147-1230 (verifier: assistantApi invocation denominator)
- `error\.response\?\.status === 401` in api.ts (verifier: Silent-401 status check location; = line 48)
- `assistantApi\.` across frontend/src excluding api.ts (verifier: 22 direct call-sites in 5 files)
- `paStore\.|usePAStore\(` across frontend/src (verifier: 40+ consumer references)
- `from tools\.pa_chat|python tools/pa_chat\.py` across repo (verifier: 1 test file import + shell wrapper reference)
- `104 (schemas|OpenAI|function-calling)|113 (schemas|OpenAI|function-calling)|109 tool schemas` in docs/topics/ + docs/PLATFORM_WHAT_IT_IS.md (verifier: doc-drift chain)

### 20.4 Unresolved unknowns

Per F-B4 fold — target 0 UNKNOWN on paStore field NAMES achieved; UNKNOWN allowed on intent/disposition only:

1. **paStore `isDockOpen` intent on logout / cross-user** — Cat C2 S2603 verdict scope.
2. **paStore `isDockMinimized` intent on logout / cross-user** — Cat C2 S2603 verdict scope.
3. **`ConversationSummary` duplicate consolidation intent** — post-verdict cleanup scope at S2701+ if Path (a) ratified.
4. **Whether `audio_url` should MIGRATE from REST-embedded to WS-broadcast** — Cat D S2604 investigation scope OR post-arc follow-on ADR.
5. **assistantApi coverage of the 18 Cat A F11 endpoints not covered by assistantApi at HEAD** — §19.3 MEDIUM follow-on.
6. **Whether backend `PAResponse` dataclass renames could silently drift frontend `UnifiedPAResponse` interface** — DEBT-B-7 evidence-only observation; Chris-D-verdict scope on SoT binding mechanism.

### 20.5 Conflicts between sources

**Conflict logging criterion (S4 SIGN cycle 1 fold inheritance from Cat A §20.5):** Items logged only when sources disagree on a **binary existence claim**, a **denominator/count**, or a **def-site/ownership trace** that changes Cat B measurements. Minor wording differences or out-of-scope hypotheses NOT logged as conflicts.

- **Agent 6 (94 apiModule) vs Agent 3 + parent-Claude verifier (93):** Reconciled to 93 via direct `^export const \w+Api\s*=` grep at HEAD.
- **Agent 3 method count text (20) vs Agent 3 method count table (20) vs Agent 6 (11):** Reconciled to 20 via direct enumeration of api.ts:1147-1230 method entries.
- **Agent 3 typed-generic count text (4) vs Agent 3 table (5) vs parent-Claude verifier grep (5):** Reconciled to 5.
- **Agent 1 paStore LOC (434) vs Agent 3 paStore LOC (450) vs parent-Claude wc -l (449):** Reconciled to 449.
- **Agent 4 assistantApi 22 direct calls (5 files) vs S2203 132 assistantApi calls (24 files):** Reconciled — S2203 132 figure is 4-cross-cutter aggregate (humanApi + assistantApi + workspaceApi + contentApi); assistantApi alone at HEAD = 22 direct calls. S2203 wording ambiguity, not drift.
- **F-B3 fold "async-audio-url delivery" (third canonical WS class) vs evidence at HEAD (audio_url is REST-embedded, NOT WS-delivered):** Reconciled — Cat B verifier-loop pre-draft re-labels third canonical class to `rigby.tool.* lifecycle events` per §6.2 and records async-audio-url as REST-embedded per §6.3.

### 20.6 Verifier-loop corrections summary

Recorded in frontmatter `verifier_loop` field. Seven pre-draft corrections:
1. apiModule count = 93 (Agent 6 wrong).
2. assistantApi region markers verified (F-B1 grep-locked).
3. assistantApi method count = 20 (Agent 6 wrong).
4. assistantApi typed-generic count = 5 (Agent 3 text wrong).
5. assistantApi typed rate = 25% per F-B5.
6. Silent-401 status check at api.ts:48; interceptor block 43-62.
7. paStore.ts LOC = 449 (Agent 1 + Agent 3 both slightly wrong).

Plus one **substantive evidence re-label** during verifier-loop:
- F-B3 fold third-canonical-WS-class relabel: "async-audio-url delivery" → "rigby.tool.* lifecycle events" per §6.2 evidence; async-audio-url recorded as REST-embedded at §6.3.

### 20.7 Cat B boundary discipline confirmed

- Cat B collected CLIENT-SIDE CONSUMPTION-side evidence only.
- Cat B did NOT recommend Path (a)/(b)/(c)/(d) verdict.
- Cat B did NOT author typed-generic retrofit code.
- Cat B did NOT create new types/pa.ts OR hooks/paQueries.ts files (F-B8 fold).
- Cat B did NOT enumerate WS envelope Path A/B/C option space (Cat D S2604 owned).
- Cat B did NOT ratify F-B-HIGH-3 closure (Cat C1 S2603 owned per F-B7 fold single-sentence discipline).
- Cat B did NOT propose UI/UX behavior changes, state-mgmt refactors, build/bundling changes, testing framework decisions (F1 fold hard boundary).
- Path (a)/(b)/(c)/(d) Chris-D-verdict deferred to S2699 xx99 close after all 4 children contribute evidence.

### 20.8 SIGN cycle 1 fold record

Full audit doc routed to Rigby SIGN cycle 1 via **dedicated fresh SIGN isolation pin `pa-760b68d6e48d4448`** (TWENTY-SIXTH consecutive dedicated fresh SIGN pin retirement in Research OS after twenty-five prior). Preemptive 2-batch × 2-Q batching per `feedback_rigby_sign_worker_instability_recovery.md` given doc size (10,689 words above 4k-word inline-prompt threshold). Single-pin close pattern per S1899-S2500 EIGHT-consecutive tested pattern; 2-pin recovery from S2601 NOT required at Cat B.

**Pin ID:** `pa-760b68d6e48d4448` (created 2026-07-06 via `session_tool action=create_fresh title='Group 2600 PA Cat B SIGN cycle 1 (S2602 close)'`).

**SIGN batch structure:**
- **Batch 1 (Q1 + Q2)** — Q1 Cat B lens + F-B1..F-B8 fold adoption verification (§16.3 checklist + §7 anti-scope + F-B5 denominator + F-B7 single-sentence); Q2 U6 + U7 evidence-gap closure + F-B3 relabel ratification.
- **Batch 2 (Q3 + Q4)** — Q3 evidence quality across §6 APIs + §7 Runtime Flows + §8 Data Ownership + F-B5 denominator lock; Q4 §14 drift + §15 debt + §16 boundary + §17 duplicates + §18 ownership + §19 follow-on completeness + boundary discipline.

**Verdict per Q:**
- **Q1 (Cat B boundary discipline + F-B1..F-B8 adoption):** AGREE with 1 STRENGTHEN (F-B9). Verified: (a) evidence-only discipline preserved throughout; (b) F-B1 through F-B8 baked into §-anchors; (c) §16.1 single-sentence F-B-HIGH-3 attribution; (d) §16.3 8-negatives checklist; (f) F-B5 denominator = 20 methods preserved. STRENGTHEN (F-B9): add explicit "Cat-B-1 through Cat-B-9" enumerated anti-scope list to dedicated §16.4 subsection for ID stability (the 8 negatives currently live in 4 different places but aren't listed under those IDs).
- **Q2 (U6+U7 evidence-gap closure + F-B3 relabel):** AGREE on all 6 sub-items (a-f). Verified: U6 clamp to 1 PA-client channel + 3 canonical classes + observed-JSON-only + Cat D handoff; F-B3 relabel evidence-driven + boundary-neutral (async-audio-url → rigby.tool.* lifecycle); U7 closure 16 fields + 0 UNKNOWN names + 2 UNKNOWN intent → Cat C2; syncUser wipe discrepancy recorded without asserting cause; §6.4 pa_chat.py envelope contract + ZERO typed dataclasses; §6.5 F-B6 "structural prerequisites present?" phrasing.
- **Q3 (evidence quality §6+§7+§8):** AGREE on all 9 sub-items (a-i). Verified: F-B5 20-method inventory table with per-method typed+backend mapping; 16/34 Cat A coverage observation-only; F-B3 3-canonical-WS-classes preserved; §6.3 REST-embedded audio_url observation preserves Cat D input; §6.4 5-field request + 12-field response sketch; §6.5 1-of-3 prerequisites; §7.1 8-step client flow + REST↔WS parallel delivery; §7.2 CLI 3-step polling-only; §8.1-8.4 data owned/consumed/produced + retention + F-B4 UNKNOWN intent pointer.
- **Q4 (§14 drift + §15 debt + §16 boundary + §17 duplicates + §18 ownership + §19 follow-on + boundary discipline):** AGREE on 9-of-10 sub-items with 1 STRENGTHEN (F-B10 at §19.2 item #6). Verified: §14.1 7 verifier corrections + §14.2 3 confirmed drifts + §14.3 verify_doc_claims 0 PA-CLIENT claims; §15.1 DEBT-B-1..B-7 + severity + owner deferred; §15.2 cross-arc coordination debts as observations; §16.1 single-sentence attribution; §16.2 3 anti-scope NOT-VIOLATED; §16.3 8-negatives checklist; §17 v1-endpoint-DEAD-CODE + ConversationSummary duplicate + REST+WS parallel; §18 CODEOWNERS lines 8-13 deferral; §19.1 2 CRITICAL + §19.2 4 HIGH + §19.3 8 MEDIUM follow-on completeness; §20 appendix trace. STRENGTHEN (F-B10): rephrase §19.2 item #6 to boundary-neutral evidence follow-on (drops "MIGRATE from REST-embedded to WS-broadcast" language that edged into Cat D option-space; rephrased to "Cat D S2604: verify whether any WS path currently carries audio_url (expected negative per §6.3) and, if negative, record as evidence for xx99 contract-binding discussion").

**Overall confidence:** **HIGH** (both batches).

**Fold adoption (Chris "agree all" 2026-07-06 ratification):**
- **F-B9** — STRENGTHEN adopted; §16.4 new subsection added with explicit Cat-B-1 through Cat-B-9 enumerated anti-scope list.
- **F-B10** — STRENGTHEN adopted; §19.2 item #6 rewritten to boundary-neutral phrasing per Rigby SIGN cycle 1 suggestion.

**Cycle 2 assessment:** NOT REQUIRED per S2601 precedent. Only STRENGTHEN folds; no CRITICAL / NEW CONCERN verdicts. Rigby SIGN cycle 1 explicit "cycle 2 candidacy: YES (strong candidate)" annotation was framed as tested-pattern-template-continuation eligibility (analog to S1899-S2500 consecutive cadence tracking), not as gating requirement for cycle 2 at Cat B.

**Rigby SIGN cycle 1 pin retirement:** `pa-760b68d6e48d4448` retired at S2602 close via `session_tool.retire force=true` per `feedback_session_tool_retire_works.md` memory rule. TWENTY-SIXTH consecutive dedicated fresh SIGN pin retirement in Research OS.

**Arc pin preserved through S2602 close:** `pa-c17a8d7e0660413b` remains unchanged; rotates only at Group 2600 arc close at S2699 xx99 per playbook §16 arc-standard behavior.

**Playbook lineage:** TWENTY-SECOND-consecutive playbook §11.2 20-section child-audit template application after S1301/S1401/S1501/S1601/S1701/S1801/S1901/S2001/S2101/S2102/S2103/S2104/S2201/S2202/S2203/S2204/S2401/S2402/S2403/S2404/S2501/S2601 twenty-one prior.
