---
title: "Frontend Session-scoped State Management + Persistence Discipline Audit (Group 2200 Cat D — S2204 P4)"
session: 2204
status: active (Rigby SIGN cycle 1 SIGN-with-edits at HIGH confidence 2026-07-05 via dedicated fresh SIGN pin `pa-62c03c4844454e99` retired at cycle close via `session_tool.retire` updated_count=6 retired=true previously_active=true; 20 folds landed pre-commit-gate; Cycle 2 NOT required; Chris "agree all" 2026-07-05 ratified 5-item close card — Path A registry + Path B version+migrate HIGH + Path D1/D2 workspace-context deferred Group 2600 PA MED + Path C REJECTED framework authoring + escape hatch preserved + R4/R5/R6/R7 maintainer-decision batch bundle + R1/R2/R3/R8/R9/R10 active-research tracks + arc-cascade sequence + commit-gate approval + MC-4 14→15 CONDITIONAL pending S2299 ratification)
arc: Research Group 2200 (Frontend — Contract-Surface Arc) — S2204 P4 Cat D fourth-child audit
category: research (playbook §11.2 20-section child-audit template FIFTEENTH-consecutive application after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203 per S2203 handoff)
authors: Claude Code (S2204 draft 2026-07-05; Rigby SIGN cycle 1 SIGN-with-edits 2026-07-05 via fresh SIGN pin `pa-62c03c4844454e99` — 4 batches × 5 Q = 20 total folds landed pre-commit-gate; cycle 2 not required per HIGH confidence)
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                                # runtime counts (§Frontend row)
  - docs/PLATFORM_WHAT_IT_IS.md                                               # narrative anchor
  - docs/topics/frontend.md                                                   # subsystem doc pointer (stale-warned; §PA Integration reference for workspace-context resolver)
  - docs/research/platform_architecture_inventory.md                          # S1273 32-domain map row 18 (STABLE + DEEP posture — S2201 §20.6 pressure-test candidate)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                 # process contract §11.2 FIFTEENTH-consecutive application
  - docs/research/OPEN_ARCS.md                                                # arc manifest (Group 2200 In-progress row updated at S2204 close)
  - docs/research/domains/frontend/2200_frontend_domain_scoping.md            # parent §5 Child D — this doc's contract
  - docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md   # sibling Child A §5 (7-Zustand-store baseline); §14 F5 legacy state-adjacent
  - docs/research/domains/frontend/2202_frontend_websocket_consumer_ui_render_hint_envelope_audit.md   # sibling Child B §17 T6 WS+polling parallel (state-adjacent)
  - docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md   # sibling Child C §14 F3 silent-401 + authStore token-persistence adjacency + §17 cross-cutters
  - docs/research/domains/sports/1505_sports_frontend_surface_audit.md        # S1505 §14.10 + §15.3 zero-client-side-state-persistence baseline (single-route `/betting` scope)
  - frontend/src/stores/authStore.ts                                          # persist=YES (v0, no migrate); partialize={token,user,isAuthenticated}
  - frontend/src/stores/navigationStore.ts                                    # persist=YES (v0, no migrate); partialize={recentEntities only}
  - frontend/src/stores/paStore.ts                                            # persist=YES (v3 + migrate); partialize={userId,isDockOpen,isDockMinimized,messages last 50,currentInput,activeConversationId,isSidebarOpen}
  - frontend/src/stores/workspaceStore.ts                                     # persist=NO (in-memory only, 27 LOC)
  - frontend/src/stores/assistantContextStore.ts                              # persist=NO (in-memory only, 28 LOC)
  - frontend/src/stores/bodyStore.ts                                          # persist=NO (in-memory only, 318 LOC)
  - frontend/src/stores/unifiedStore.ts                                       # persist=NO (in-memory only, 426 LOC)
  - frontend/src/main.tsx                                                     # React Query client config (staleTime 60s; no persistent adapter)
delegated_from:
  - S2200 parent scoping §5 Child D — load-bearing input + load-bearing output + D1-D5 sub-axes + per-surface reporting constraint (Q1 STRENGTHEN fold) + timebox+sampling rule (Q10 STRENGTHEN fold) + anti-scope §7.1 guardrails
  - S1505 §14.10 zero-client-side-state-persistence single-route baseline; §15.3 MED-severity remediation options (URL params / localStorage filter / Zustand slice)
  - S2201 §5 baseline enumerating 7 Zustand stores; §14 F5 `legacyTabMapping` state-adjacent surface (deferred to Child D S2204 per S2201 handoff §5 item 5)
  - S2202 §17 T6 PA WS + Celery polling parallel (state-adjacent; T6 deferred to Group 2600 PA per S2202 handoff)
  - S2203 §14 F3 SYSTEMIC silent-401 + `authStore` token-persistence adjacency (`api.ts:2` imports `@/stores/authStore`; verified S2203 §16.1 INTENTIONAL not violation); §17 cross-cutters (state-shared); Session 968 X-UI-Scope in-memory ring buffer at `frontend/src/lib/api.ts:3968-4051` (state-adjacent)
delegates_to:
  - S2299 xx99 canonical summary — F2 hypothesis test verdict for xx99 §7 anchor-update batch (PLATFORM_INVENTORY §Frontend + topics/frontend.md persistence-row augmentation) + §8 T-slot queue + §9 cross-links (Groups 2400 Auth + 2500 API + 2600 PA + 2300 Mobile) + §7.1 render-authority handoff flags (workspace-context resolver → Group 2600 PA)
head_commit_before: 8fbf17eb
arc_pin: pa-f7fd5016600f4513 (PRESERVED through S2204 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails — TENTH formal arc pin under Research OS; retirement at S2299 close)
sign_pin: pa-62c03c4844454e99 (RETIRED at S2204 SIGN cycle 1 close via `session_tool.retire` per playbook §15 SIGN-isolation discipline — updated_count=6, retired=true, previously_active=true. 4 batches × 5 questions = 20 total; verdict SIGN-with-edits at HIGH confidence; cycle 2 not required per all folds landable pre-commit)
scope_shape:
  central_child_D_lens: >
    "Does session-scoped state have a declared persistence discipline per surface, or does the
    'zero client-side state persistence' pattern (S1505 §14.10) generalize with silent variance
    across surfaces?"
  D1_output: persistent-state-surface inventory (all localStorage / sessionStorage / IndexedDB / cookie / Zustand-persist keys)
  D2_output: declared-vs-accidental discipline rate
  D3_output: key-namespace collision audit
  D4_output: PA workspace-context resolver persistence audit
  D5_output: cross-surface state coupling
  per_surface_reporting: workspace / betting / command-center / PA (per S2200 §5 Q1 STRENGTHEN fold)
  timebox_and_sampling: 1 session; complete registry skeleton (all keys enumerated at metadata) + sampled deep inspection per S2200 §5 Q10 STRENGTHEN fold
provenance:
  - S2204 draft written 2026-07-05 post-S2203 close (Chris "agree all" ratified 2026-07-05)
  - 6 parallel Explore sub-agents run per playbook §13 (D1 persistent-state inventory, D2 Zustand persist discipline, D3 namespace collision, D4 PA workspace-context resolver, D5 cross-surface coupling, D6 §13-§18 rollup + F2 falsifier framework)
  - Parent-Claude verifier-loop per playbook §14 caught 2 sub-agent errors pre-draft:
    - Explore 5 mis-classified `navigationStore` as DEAD (0 consumers); direct grep found 2 real consumers (EntityLink.tsx + Breadcrumb.tsx) — corrected in §5 + §14 F4 not-DEAD framing
    - Explore 5 mis-stated `unifiedStore` has 0 page consumers; direct grep found CommandCenterPage.tsx uses it (27 total occurrences across 4 files) — corrected in §5
  - Chris "agree all" ratification pending post-Rigby-SIGN-cycle-1 close-card
owner: claude (drafted S2204; Rigby SIGN cycle 1 folds land pre-commit; Chris ratification via close-card)
---

# Session 2204 — Group 2200 Cat D — Frontend Session-scoped State Management + Persistence Discipline Audit

> **Static snapshot.** This audit captures the frontend session-scoped state + persistence
> discipline surface at HEAD `8fbf17eb` on `main` (2026-07-05, LOCAL). It is a photograph, not
> a mechanism explainer. Route + page + layout + component structure is Child A (S2201).
> WebSocket consumer surface is Child B (S2202). API contract source-of-truth is Child C
> (S2203). This document delivers what parent §5 Child D required: (D1) persistent-state-
> surface inventory across localStorage / sessionStorage / IndexedDB / cookie / Zustand
> stores; (D2) declared-vs-accidental discipline rate; (D3) key-namespace collision audit;
> (D4) PA workspace-context resolver persistence audit; (D5) cross-surface state coupling
> map; plus POSTURE-DECISION evidence plan §20.6 owed to xx99 on whether per-surface
> persistence discipline should be introduced as a frontend convention or handled at
> backend/PA layer.

## 1. Executive Summary

**Contract-surface posture — one-sentence answer to the Child D slice of the central lens
question:** The frontend at HEAD `8fbf17eb` is **structurally intentional at the Zustand-
persist boundary** (3 of 7 stores use `persist` middleware — authStore, navigationStore,
paStore — with paStore uniquely carrying a `version=3` + `migrate` function) but
**structurally accreted at the direct-localStorage-caller boundary** (12 distinct keys
scattered across 9 files with no shared registry, mixed kebab-case/snake_case/camelCase
naming, and no cross-tab sync mechanism). **Total persistent surfaces: 15** (3 Zustand
persist stores + 12 direct localStorage keys); **0 sessionStorage** usage; **0 IndexedDB**
usage; **1 cookie read** (`paStore.ts:241` reads `sessionid` for feedback POST); **1
in-memory ring buffer** (Session 968 X-UI-Scope request-log at `api.ts:3968-4051`, 200-entry
cap, dev-only).

**Central Child D finding — S1505 §14.10 hypothesis is SURFACE-LOCAL, NOT SYSTEMIC.** Per
the S2200 §2.4 four-falsifier framing applied to state-persistence discipline: **F1 fails
by key-incidence** (Rigby SIGN cycle 1 Q6 STRENGTHEN fold 2026-07-05 — denominator language
tightened): **14 of 15 persisted keys are outside `/betting`; betting has 0 of 15 persisted
keys** → persistence is present elsewhere, absent in betting. Framing "adoption rate"
replaced with "key-level incidence by surface" per Q7 STRENGTHEN fold; cross-surface
averaging explicitly forbidden unless normalized by eligible keys per surface. **F2
partially resolves surface-local** (betting is intentionally ephemeral per S1505 §15.3
remediation-only options; other surfaces show intentional discipline). **F3 partially
resolves domain-specific** (auth persistent across all uses; body ephemeral by design
across all uses; UI chrome inconsistent). **F4 fails** (surfaces do NOT show uniform
patterns). **Verdict: SURFACE-LOCAL + DOMAIN-SPECIFIC HYBRID** — S1505 §14.10 accurately
describes `/betting`-slice reality but does NOT generalize; xx99 should elevate to
whole-frontend governance only as a naming-convention + registry recommendation, NOT as an
urgent persistence-framework gap.

**Contract-surface acceptance criterion 4 scoring (S2200 §lens block):**

| Criterion | Status | Evidence |
|---|---|---|
| 4 — Session-scoped state has a declared persistence discipline (localStorage / sessionStorage / server-round-tripped) per surface | **PARTIAL** | 3 of 7 Zustand stores declare persistence with partialize; 1 of 3 (paStore) declares versioning + migrate. 12 direct localStorage keys have 6 DECLARED (constant + typed accessor) and 6 ACCIDENTAL (inline string literal + swallow-catch). No cross-surface registry. No `storageKeys.ts` module. `workspaceStore.activeWorkspace` in-memory-only creates a live PA-context-loss hazard on refresh (§14 F5). |

**POSTURE-DECISION §20.6 preliminary evidence toward xx99 on per-surface persistence
discipline convention:** **downgrade candidate** to **naming-registry + versioning-hygiene
convention**, NOT a whole-frontend persistence framework. The state surface is small (15
total keys) and mostly intentional; the highest-leverage improvements are (a) a shared
`frontend/src/lib/storageKeys.ts` registry to prevent future collisions, (b) `version` +
`migrate` on authStore + navigationStore to close schema-drift risk, (c) explicit
`workspaceStore.activeWorkspace` persistence decision (in-memory-intentional vs
persist-with-userScoping). Framework authoring (Zustand-with-full-persistence, jotai,
react-query cache-persist) is EXPLICITLY OUT-OF-SCOPE per §7 anti-scope.

**Five headline findings:**

- **F1 — Persistent-state inventory: 15 total surfaces, 0 sessionStorage, 0 IndexedDB (§14.1
  observation, not drift)** — 3 Zustand persist keys (`auth-storage`, `navigation-store`,
  `pa-dock-state`) + 12 direct localStorage keys (`assistant-voice-settings`,
  `cc_dashboard_collapsed`, `cc_chat_focus_mode`, `pipeline_dismissed_${workspaceId}` param,
  `demo-pipeline-dismissed`, `cockpit-focus-mode`, `sidebar-collapsed`,
  `sidebar-reference-open`, `showDebugPanels` dev-only, `deliverables_view_mode`,
  `cockpit-sidebar-collapsed`, `podcast_voice_profile_id`) + 1 cookie read (`sessionid` at
  `paStore.ts:241`) + 1 in-memory ring buffer (Session 968 X-UI-Scope). **Class:
  `observation` — enumeration, not drift.** Severity: informational.
- **F2 — `workspaceStore.activeWorkspace` in-memory-only creates PA-context-loss on refresh
  (§14 F5) — MED-HIGH cross-surface impact (borderline HIGH if PA relies on workspace
  scoping for correctness)** — `workspaceStore.ts:24-27` bare Zustand store with no `persist`
  middleware. Read by ≥16 files (144 occurrences) including `CommandCenterPage.tsx:1013` +
  `GlobalPADock.tsx:340-351` + `GlobalPADock.tsx:943` where workspace context is injected
  into PA chat payload. On F5/refresh, `activeWorkspace = null` → PA chat sends
  `workspace_id: undefined` and `workspace_mode: 'global'` instead of `'workspace'`.
  **Class: `technical_debt` — cross-surface impact.** Severity: MED-HIGH per cross-surface
  amplification (12 PA-side consumers); **borderline HIGH conditional on Group 2600 PA
  disposition** — if workspace scoping is load-bearing for PA correctness (e.g., agent tools
  dispatch by workspace), severity elevates to HIGH. Rigby SIGN cycle 1 Q2 STRENGTHEN
  2026-07-05 fold — hedge language explicit.
- **F3 — Zustand persist version discipline: 1 of 3 has migrate (paStore); 2 of 3 lack
  version (authStore + navigationStore) (§15.1)** — `authStore.ts:43-50` and
  `navigationStore.ts:98-105` declare `persist(...)` with `partialize` but no `version` +
  no `migrate`. paStore at `paStore.ts:395-431` declares `version: 3` + full `migrate`
  covering v1→v2 + v2→v3 user-scope wipe. **Class: `technical_debt` — schema-drift risk on
  authStore + navigationStore future edits.** Severity: MED (LOW today; MED-with-future-
  scope on any token/user shape change or recentEntities schema change).
- **F4 — Direct-caller discipline: 6 of 12 keys DECLARED, 6 ACCIDENTAL; no shared registry
  (§14.2 + §15.2)** — DECLARED (constant + typed accessor + graceful fallback): `sidebar-
  collapsed`, `sidebar-reference-open`, `cockpit-focus-mode`, `cockpit-sidebar-collapsed`,
  `assistant-voice-settings`, `demo-pipeline-dismissed`. ACCIDENTAL (inline string literal
  + swallow-catch + no typed shape): `cc_dashboard_collapsed`, `cc_chat_focus_mode`,
  `deliverables_view_mode`, `pipeline_dismissed_${workspaceId}` (template + scattered
  removeItem across 5 call sites), `podcast_voice_profile_id`, `showDebugPanels`. No
  centralized `frontend/src/lib/storageKeys.ts` module. **Class: `technical_debt` —
  maintenance debt + future-collision risk.** Severity: MED-LOW (LOW today; MED at team-
  scale).
- **F5 — Naming convention drift: 6 kebab-case + 3 snake_case + 3 camelCase across 12
  direct keys (§14.3)** — kebab-case: `sidebar-*`, `cockpit-*`, `assistant-voice-settings`,
  `demo-pipeline-dismissed`. snake_case: `cc_*`, `deliverables_view_mode`,
  `podcast_voice_profile_id`, `pipeline_dismissed_*`. camelCase: `showDebugPanels`. 3
  Zustand persist keys all kebab-case (`auth-storage`, `navigation-store`, `pa-dock-state`).
  **Class: `drift` — inconsistency, not violation.** Severity: LOW.

**S1505 4-falsifier verdict:** **SURFACE-LOCAL + DOMAIN-SPECIFIC HYBRID.** F1 fails
(non-betting violation rate < 10% — 14 of 15 persistent surfaces sit outside `/betting`);
F2 partially resolves surface-local (betting intentionally ephemeral); F3 partially resolves
domain-specific (auth persistent, body ephemeral, PA persistent-with-migrate); F4 fails
(surfaces do not show uniform patterns). Governance urgency at xx99 elevates to
naming-registry + versioning-hygiene recommendations, NOT persistence-framework authoring.

## 2. Domain Purpose

**Q1 — What is this Child D audit for? (one-sentence purpose):** Enumerate the frontend's
session-scoped state + persistence surface at static snapshot, testing whether the S1505
§14.10 "zero client-side state persistence" pattern generalizes across the 61-route surface
and whether per-surface persistence discipline is DECLARED (with visible partialize +
version + migrate + registry) or ACCIDENTAL (inline strings, silent catch, no schema
versioning).

**Q2 — What problem does it solve? (business / platform problem):** Prior arcs
(Groups 1300-2100) touched the frontend only as downstream consumer; no arc has enumerated
persistent state surfaces at the whole-frontend level. S1505 §14.10 documented single-route
zero-persistence at `/betting`; whether that pattern reflects sports-outlier or systemic
architecture is undetermined. S2201 §5 baseline enumerated 7 Zustand stores + deferred
consumer + persistence mapping to Child D. S2202 §17 T6 flagged PA WS + polling parallel
(state-adjacent). S2203 §14 F3 identified `authStore` token-persistence adjacency (silent-401
+ token interceptor read path). This audit closes the whole-frontend visibility gap on the
session-scoped state axis so that S2299 xx99 can measure state persistence discipline
against a grounded inventory rather than sampling assumptions.

**Q3 — What does the Child D audit NOT do? (anti-scope alignment):**
- No fixes / no PRs — read-only research.
- No state-management framework authoring (Zustand-with-persistence expansion, jotai
  migration, react-query cache-persist adapter design) per §7 anti-scope.
- No auth session model authoring (Group 2400 Auth scope) — `authStore` token-persistence
  is state-adjacent-only.
- No BE-side session design (Groups 2400 Auth + 2500 API scope) — audit is symptom-side
  only.
- No PA behavioral spec (Group 2600 PA scope) — `paStore` + `assistantContextStore` +
  workspace-context resolver treated as render/persistence surfaces only.
- No godcomponent refactor (Child A / Child E spin-out scope).
- No envelope authoring (Child B scope).
- No API contract SoT authoring (Child C scope + Group 2500 API scope).

## 3. Canonical Entry Points

State-persistence entry points enumerated at HEAD `8fbf17eb`. Line references are static
snapshots.

**Zustand persist store declarations:**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `useAuthStore` create + persist | `frontend/src/stores/authStore.ts:20-52` | Auth token + user + isAuthenticated. persist({name: 'auth-storage', partialize: {token, user, isAuthenticated}}). No version. No migrate. |
| `useNavigationStore` create + persist | `frontend/src/stores/navigationStore.ts:44-106` | Cross-page navigation context + history + recentEntities. persist({name: 'navigation-store', partialize: {recentEntities only}}). No version. No migrate. |
| `usePAStore` create + persist | `frontend/src/stores/paStore.ts:154-434` | PA dock state + messages + conversations. persist({name: 'pa-dock-state', version: 3, migrate: fn(v1→v2+v2→v3), partialize: {userId, isDockOpen, isDockMinimized, messages.slice(-50), currentInput, activeConversationId, isSidebarOpen}}). |

**Zustand in-memory-only store declarations:**

| Entry Point | File:Line | Purpose | LOC |
|---|---|---|---|
| `useWorkspaceStore` create | `frontend/src/stores/workspaceStore.ts:24-27` | Active workspace context (workspace-id + name + type + git-remote-url). **In-memory only.** | 27 |
| `useAssistantContextStore` create | `frontend/src/stores/assistantContextStore.ts:24-28` | Focused entity for PA chat context (deliverable / initiative / action_item / attention / file). **In-memory only.** | 28 |
| `useBodyStore` create | `frontend/src/stores/bodyStore.ts:111-318` | Body system vitals + alerts + health status. In-memory-only with 5s throttle bookkeeping. | 318 |
| `useUnifiedStore` create | `frontend/src/stores/unifiedStore.ts:144-427` | Unified dashboard: attention + opportunities + pilots + gates. In-memory-only with 5s throttle bookkeeping. | 426 |

**Direct-caller localStorage entry points:**

| Key | File:Line (write) | Purpose |
|---|---|---|
| `auth-storage` | (Zustand-managed via `authStore.ts:44`) | Token + user + isAuthenticated (Zustand persist backing) |
| `navigation-store` | (Zustand-managed via `navigationStore.ts:99`) | recentEntities (Zustand persist backing) |
| `pa-dock-state` | (Zustand-managed via `paStore.ts:396`) | PA dock state (Zustand persist backing) |
| `assistant-voice-settings` | `frontend/src/pages/CommandCenterPage.tsx:166,182,190` | Voice input/output/TTS/mode JSON blob |
| `cc_dashboard_collapsed` | `frontend/src/pages/CommandCenterPage.tsx:781,825` | Command Center dashboard collapsed flag |
| `cc_chat_focus_mode` | `frontend/src/pages/CommandCenterPage.tsx:784,828` | Command Center chat focus mode flag |
| `pipeline_dismissed_${workspaceId}` | `frontend/src/pages/WorkspaceDashboardPage.tsx:132,169,188,202,270` | Per-workspace pipeline-run dismissed ID |
| `demo-pipeline-dismissed` | `frontend/src/components/DemoPipelineCard.tsx:34,87` | Demo pipeline card dismissed flag |
| `cockpit-focus-mode` | `frontend/src/hooks/useFocusMode.ts:3,7,13` (STORAGE_KEY const) | Cockpit focus mode toggle |
| `sidebar-collapsed` | `frontend/src/components/layout/Sidebar.tsx:94,126` | Main sidebar collapsed state |
| `sidebar-reference-open` | `frontend/src/components/layout/Sidebar.tsx:100,105` | Sidebar reference-menu open state |
| `showDebugPanels` | `frontend/src/components/PanelDebugDrawer.tsx:6,10` (DEV_KEY const) | Dev-mode debug panel visibility |
| `deliverables_view_mode` | `frontend/src/pages/workspace/tabs/DeliverablesTab.tsx:299,304` | Deliverables view mode (grouped/flat) |
| `cockpit-sidebar-collapsed` | `frontend/src/components/cockpit/CockpitSidebar.tsx:53,101` | Cockpit sidebar collapsed state |
| `podcast_voice_profile_id` | `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx:2446,2716,2734,2736` | Selected podcast voice profile ID |

**Cookie read (single site):**

| Cookie | File:Line | Purpose |
|---|---|---|
| `sessionid` | `frontend/src/stores/paStore.ts:241` (`document.cookie.match(/sessionid=([^;]+)/)`) | Read Django session cookie for `/api/pa/feedback/` POST (non-blocking) |

**In-memory ring buffer (session-scoped, dev-only surface):**

| Buffer | File:Line | Purpose |
|---|---|---|
| Session 968 X-UI-Scope request-log | `frontend/src/lib/api.ts:3968-4051` (MAX_LOG = 200; `requestLog: RequestLogEntry[]`; `subscribeRequestLog` + `clearRequestLog`) | Dev-mode request telemetry ring buffer; consumed by `PanelDebugDrawer.tsx:4,29`; cleared on page reload |

**React Query cache config (session-scoped, no persistence):**

`frontend/src/main.tsx:8-16` — `new QueryClient({defaultOptions: {queries: {staleTime: 1000 * 60, retry: 1, refetchOnWindowFocus: false}}})`. No `persistQueryClient` adapter. Cache lost on reload.

**URL-state usage (session-scoped, browser-managed):**

- `frontend/src/pages/WorkspacePageNew.tsx:786-852` — `?tab={primary}&sub={subtab}` primary tab routing persists via URL query params.
- `frontend/src/pages/CommandCenterPage.tsx:649` — read-only URL params.
- `frontend/src/pages/OperatorEdgePage.tsx:7` — read-only URL params.
- `frontend/src/pages/VipAcceptPage.tsx:8` — read-only URL params.

## 4. Major Models

**Not applicable — no Django models.** State persistence surface is client-side only.
Server-round-tripped state (PA conversations, deliverables, workspace briefs, pipeline runs)
is owned by backend Django models per S2203 §4 API contract audit; **frontend does not
manage schema for those; frontend consumes them via api-module cross-cutters (§17.2
S2203).**

For **client-side type surface** (state-shape declarations):

| Type / Interface | File:Line | Ownership | Notes |
|---|---|---|---|
| `AuthState` | `authStore.ts:11-18` | Frontend-hand-declared | `{token, user, isAuthenticated, login, logout, setUser}` — no shared type import from `@/types/*` per S2203 §6.4 (User interface declared inline). Cross-arc handoff flag to Group 2500 API: canonical User type authoring. |
| `NavigationContext` | `navigationStore.ts:11-18` | Frontend-hand-declared | `{fromPage, entityType?, entityId?, entityLabel?, timestamp, [key: string]: unknown}` — indexed accessor allows arbitrary keys. |
| `NavigationState` | `navigationStore.ts:20-42` | Frontend-hand-declared | `{context, history, recentEntities, ...actions}`. `recentEntities` shape: `{type, id, label, page, timestamp}`. |
| `PAState` | `paStore.ts:70-149` | Frontend-hand-declared | Compound state: `{userId, isDockOpen, isDockMinimized, messages[], currentInput, currentPage, activeConversationId, conversations[], isSidebarOpen, conversationsLoading, activeTool, recentTool, seenSeqs, recentAgentCompletion, agentCompletionQueue, seenCompletions, ...actions}`. |
| `Message` | `paStore.ts:26-40` (referenced from `types/paMessage.ts` — verify) | Frontend-hand-declared | `{id, role, content, timestamp, tools_used?, source, feedback?}`. |
| `WorkspaceInfo` | `workspaceStore.ts:12-17` | Frontend-hand-declared | `{id, name, workspace_type?, git_remote_url?}` — no shared type import; consumer type is `WorkspaceInfo | null`. |
| `AssistantContextStore` | `assistantContextStore.ts:12-22` | Frontend-hand-declared | `{focusedEntity: FocusedEntity | null, setFocusedEntity, clearFocusedEntity}`. `FocusedEntity` type: `{type: 'deliverable'\|'initiative'\|'action_item'\|'attention'\|'file', id, title}`. |
| `RequestLogEntry` | `frontend/src/lib/api.ts:3968-4051` (Session 968) | Frontend-hand-declared | `{id, method, url, status, ms, scope, error}`. Dev-only telemetry ring buffer. |

**Type-shape drift risk:** authStore + navigationStore + paStore persist to localStorage;
future edits to any type shape without a `version` + `migrate` (authStore + navigationStore
have neither) will silently rehydrate stale data. paStore has v3 + migrate for the fields
it covers, but tool-ticker + agent-completion state (activeTool, recentTool, seenSeqs,
agentCompletionQueue, seenCompletions) are NOT in partialize (correctly ephemeral) so no
migration needed for those.

## 5. Major Services

**State-persistence services enumerated at HEAD `8fbf17eb`. Cross-referenced with S2201 §5
Zustand store baseline + parent-Claude verifier-loop.**

### 5.1 Zustand store consumer surface matrix

Per verifier-loop grep (playbook §14 verify claim step) — CORRECTED against Explore 5
mis-classifications:

| Store | Consumer files | Occurrences | Persistence | Primary surface | Verdict |
|---|---|---|---|---|---|
| `useAuthStore` | 8 files (App.tsx, CommandCenterPage.tsx, WorkspacePageNew.tsx, Sidebar.tsx, LoginPage.tsx, ProtectedRoute, api.ts interceptor, PA store consumer) | 8 sites | persist v0 (localStorage `auth-storage`) | Global/Auth | GLOBAL (essential for route guards + api.ts interceptor per S2203 §16.1 INTENTIONAL) |
| `useNavigationStore` (+ selectors) | 3 files (navigationStore.ts, `EntityLink.tsx`, `Breadcrumb.tsx`) | ~3 sites | persist v0 (localStorage `navigation-store`, recentEntities only) | Global | **CORRECTION vs Explore 5:** NOT DEAD — 2 real consumers (EntityLink + Breadcrumb). Persist is not wasted. |
| `usePAStore` (+ selectors) | 12 files (App.tsx, CommandCenterPage.tsx, PAConversationSidebar.tsx, GlobalPADock.tsx, Sidebar.tsx, AgentCompletionBanner.tsx, RigbyToolTicker.tsx, WorkspaceDashboardPage.tsx, workspace/tabs/HomeTab.tsx, WorkTab.tsx, DeliverablesTab.tsx, paStore.ts) | 57 sites | persist v3 + migrate (localStorage `pa-dock-state`) | PA + cross-surface | CROSS-SURFACE-SHARED (intentional per Session 948 + 974) |
| `useWorkspaceStore` (+ `.getState().activeWorkspace` grep) | 16 files (WorkspacePageNew.tsx, CommandCenterPage.tsx, GlobalPADock.tsx, CockpitSidebar.tsx, FilesTab.tsx, InboxPage.tsx, HomeTab.tsx, OperationsTab.tsx, WorkTab.tsx, InitiativesTab.tsx, AppTab.tsx, ContentStudioTab.tsx, DeliverablesTab.tsx, GitTab.tsx, WorkspaceOverviewTab.tsx, workspaceStore.ts) | 144 sites | **NONE** (in-memory only) | Cross-surface (workspace + command-center + PA) | CROSS-SURFACE-SHARED, in-memory — F5 F2 hazard |
| `useAssistantContextStore` (+ `focusedEntity` grep) | 5 files (assistantContextStore.ts, GlobalPADock.tsx, HomeTab.tsx, WorkTab.tsx, DeliverablesTab.tsx) | 16 sites | **NONE** (in-memory only) | Workspace-writes / PA-reads | CROSS-SURFACE-SHARED (unidirectional workspace→PA) |
| `useBodyStore` | 3 files (bodyStore.ts, `bodyGovernance.ts` service, `GlobalAlertBanner.tsx`) | 14 sites | **NONE** (in-memory only; 5s throttle) | Global (governance layer) | GLOBAL (services layer + global banner) |
| `useUnifiedStore` (+ selectors) | 4 files (unifiedStore.ts, Sidebar.tsx, Layout.tsx, `CommandCenterPage.tsx`) | 27 sites | **NONE** (in-memory only; 5s throttle) | Global (layout+sidebar) + Command Center reads | **CORRECTION vs Explore 5:** NOT global-only — CommandCenterPage.tsx:3 imports and consumes it. Classification GLOBAL-with-CC-consumer. |

### 5.2 Per-surface state consumption rollup (per S2200 §5 Q1 STRENGTHEN fold + S2204 Rigby SIGN cycle 1 Q7 STRENGTHEN 2026-07-05 fold — "key-level incidence by surface" language, cross-surface averaging FORBIDDEN unless normalized by eligible keys per surface)

| Surface | Zustand consumers | Direct localStorage keys | URL state | Server-round-tripped | State-adjacent surfaces |
|---|---|---|---|---|---|
| **Workspace** | 5 stores read (auth, workspace, pa, assistantContext, unified via Layout-parent) | 2 direct (`pipeline_dismissed_${workspaceId}`, `deliverables_view_mode`, `podcast_voice_profile_id`) + 3 across tab-tree | 1 route (`?tab={primary}&sub={subtab}` at WorkspacePageNew.tsx:786-852) | Deliverables CRUD, Pipeline status, Workspace brief, Initiative + Action Item queries | S2201 §14 F5 `legacyTabMapping` state-adjacent surface (backward-compat mapping, not persisted state) |
| **Betting** | 1 store read (auth via ProtectedRoute) | **0** direct | **0** URL state | Betting stats, wagers, sports data via api-modules | **Confirmed S1505 §14.10 — zero client-side state persistence** at `/betting`. `BettingPage.tsx` uses `useState<BettingTab>('hub')` in-memory only. |
| **Command-Center** | 5 stores read (auth, workspace, pa, unified, body) | 3 direct (`assistant-voice-settings`, `cc_dashboard_collapsed`, `cc_chat_focus_mode`) | 1 route (URL params read-only at CommandCenterPage.tsx:649) | PA conversations + boot data + while-away + quick stats | `usePageTracking()` hook (Layout.tsx:14 per S2201 baseline) — fire-and-forget Redis counter (side-effect persistence, backend-owned, not client-side state per S2200 §5 Q6 CLEAN fold) |
| **PA** | 4 stores read (pa, workspace via `.getState()`, assistantContext, auth) | **0** direct localStorage; PA chat state via `pa-dock-state` Zustand persist | **0** URL state | Full conversation history via `/pa/conversations/*`; message feedback via `/api/pa/feedback/` | Session 968 X-UI-Scope in-memory ring buffer at `api.ts:3968-4051` (dev-only, 200-entry cap) |
| **Global (Layout + Sidebar + Auth)** | All 7 stores accessible; Sidebar + Layout consume unified + pa + auth | 3 direct (`sidebar-collapsed`, `sidebar-reference-open`, `demo-pipeline-dismissed`) + 1 dev-only (`showDebugPanels`) + 2 cockpit-scoped (`cockpit-focus-mode`, `cockpit-sidebar-collapsed`) | Route-level via React Router | Auth check via `/auth/user/` | GlobalAlertBanner consumes `bodyStore` alerts |

**Per-surface key-level incidence observation** (per S2200 §5 Q10 STRENGTHEN fold sampling
rule + Rigby SIGN cycle 1 Q7 STRENGTHEN 2026-07-05 fold — "adoption rate" language replaced
with "key-level incidence by surface"; cross-surface averaging explicitly FORBIDDEN unless
denominators are normalized by eligible keys per surface — full inventory shipped as
enumeration; sampling **waived per full-registry-fit** per Rigby SIGN cycle 1 Q10 CLEAN
2026-07-05 fold; inspection = complete enumeration):

- **Betting:** 0 persistent keys (0 direct + 0 Zustand-consumed). `BettingPage.tsx` uses
  `useState<BettingTab>('hub')` in-memory only. **S1505 §14.10 baseline CONFIRMED** for
  `/betting`.
- **PA:** 1 persistent surface (paStore `pa-dock-state`, v3 + migrate). PA-dock is
  session-persistent + cross-surface-consumed.
- **Workspace:** 3 direct persistent keys (`pipeline_dismissed_${workspaceId}`,
  `deliverables_view_mode`, `podcast_voice_profile_id`) + reads paStore + reads
  workspaceStore (**not persistent** = F5 F2 hazard) + reads assistantContextStore (**not
  persistent** = F4 refresh loss). Workspace has intentional persistence for tab / view /
  voice-profile UI state but WORKSPACE-CONTEXT itself is NOT persistent.
- **Command Center:** 3 direct persistent keys (`assistant-voice-settings`,
  `cc_dashboard_collapsed`, `cc_chat_focus_mode`) + reads paStore + reads unifiedStore
  (in-memory-by-design) + reads bodyStore (in-memory-by-design). 1 of 3 direct keys
  DECLARED via constant + typed accessor (`assistant-voice-settings`); 2 ACCIDENTAL via
  inline string literal.
- **Global/Auth:** 3 direct persistent keys (`sidebar-collapsed`, `sidebar-reference-open`,
  `demo-pipeline-dismissed`) + 1 dev-only (`showDebugPanels`) + 2 cockpit-scoped
  (`cockpit-focus-mode`, `cockpit-sidebar-collapsed`) + 2 Zustand persist stores
  (`auth-storage`, `navigation-store`). 4 of 6 direct + 2 of 2 Zustand DECLARED.

**Reading:** Betting is intentionally ephemeral (S1505 §14.10 baseline confirmed by
key-level incidence, NOT by percentage). Other surfaces show declared but inconsistent
discipline. No surface exhibits systemic zero-persistence beyond betting. Per-surface
denominators DIFFER (workspace = 3, command-center = 3, PA = 1, global = 6+2 = 8) —
percentage comparisons would be misleading and are avoided.

### 5.3 React Query cache posture

`frontend/src/main.tsx:8-16` — `staleTime: 60_000ms` + no persistent adapter. Cache is
session-scoped; lost on reload. Explicit invalidation is used (~350 `invalidateQueries`
calls across pages per Explore 1 count). **No `persistQueryClient` adapter installed.**
Query cache is intentionally ephemeral.

### 5.4 URL-state usage (single load-bearing surface)

`frontend/src/pages/WorkspacePageNew.tsx:786-852` — primary + sub tab routing via
`?tab={primary}&sub={sub}` search params. Load-bearing. Legacy `?tab=deliverables` (single
param) maps via `legacyTabMapping` object (S2201 §14 F5 state-adjacent surface). Other
pages use URL params read-only or not at all.

## 6. Major APIs and Interfaces

State persistence surface is **client-side only** — no REST or WebSocket endpoints own
persistent state directly. Cross-referencing S2203 §6 API surface audit + S2202 §6 WS
surface audit, the relevant server-round-tripped endpoints are documented there. This
audit does not re-inventory them.

**API interfaces relevant to state persistence:**

| Endpoint | Purpose | State-persistence role |
|---|---|---|
| `/auth/login/` (Django `authApi.login`) | Sets `sessionid` cookie; frontend stores token in `authStore.token` | Auth token persistence entry point; Zustand persist backing |
| `/auth/user/` (Django `authApi.getUser`) | Rehydrates user object into `authStore.user` on session resume | Auth rehydration entry point |
| `/auth/logout/` (`authApi.logout`) | Clears server session; frontend clears `authStore` + Zustand-persist clears `auth-storage` on state mutation | Auth persistence teardown |
| `/pa/conversations/` (`assistantApi.listConversations`, `.getConversation`, `.createConversation`) | Server-side conversation history authority | paStore.messages hydration source (loaded lazily on `setActiveConversation`) |
| `/api/pa/feedback/` (fetch in `paStore.ts:242`) | Persists message feedback (rating) | Uses `document.cookie` `sessionid` read (paStore.ts:241) |
| `/api/pa/chat/` (Rigby chat) | Sends `context.workspace_id` + `context.workspace_name` + root `workspace_id` from `useWorkspaceStore.getState().activeWorkspace` | Consumes workspace-context resolver; F2 hazard on refresh |
| `/api/v1/telemetry/page-view/` (fire-and-forget POST via `usePageTracking()` at Layout.tsx:14 per S2201 baseline) | Server-side page-view counter (Redis) | Side-effect persistence surface, backend-owned, not client-side state (per S2200 §5 Q6 CLEAN fold — treated as Child D non-scope; state-persistence-adjacent surface) |

**PA workspace-context resolver flow (D4 owed to xx99):**

The PA workspace-context is resolved at **chat-request time** by two consumer sites:

1. `frontend/src/components/GlobalPADock.tsx:340-352` — reads
   `useWorkspaceStore.getState().activeWorkspace` inside `chatMutation.mutationFn`;
   constructs `context.workspace_id` + `context.workspace_name` + `context.workspace_mode`
   ('workspace' vs 'global' based on `!!activeWorkspace || !!focusedEntity`) + `focused_entity`
   from `useAssistantContextStore.focusedEntity`. Also passes root-level `workspace_id`
   at line 351.

2. `frontend/src/pages/CommandCenterPage.tsx:1008-1014` — reads
   `useWorkspaceStore.getState().activeWorkspace?.id` and passes as root-level
   `workspace_id`. **Does NOT construct `context.workspace_id`** — asymmetry vs
   GlobalPADock construction.

**Dual inclusion asymmetry (§17 concern):** GlobalPADock includes `workspace_id` in BOTH
`context` object AND payload root; CommandCenterPage includes only at payload root. Backend
canonical field is unclear from frontend side (Group 2600 PA arc scope for resolution).

**Refresh-loss failure mode (F2):** After F5, `activeWorkspace = null` (workspaceStore not
persisted). Both `GlobalPADock` and `CommandCenterPage` fall back to `workspace_id:
undefined`. PA chat receives `workspace_mode: 'global'` instead of `'workspace'`. **Rigby
loses workspace context mid-conversation.** User must manually re-select workspace via
GlobalPADock workspace picker (`GlobalPADock.tsx:601`) or `WorkspacePageNew.tsx:901-911`
mount effect.

## 7. Runtime Flows

Static-snapshot flows (five load-bearing surfaces at HEAD `8fbf17eb`).

### 7.1 Auth token hydration + logout flow

```
BROWSER LOAD
  → Zustand persist auto-hydrates `auth-storage` localStorage into authStore state
  → authStore.token + user + isAuthenticated available synchronously to consumers
    (App.tsx:2 ProtectedRoute wrapper, api.ts:29 interceptor injects
     'Authorization: Token <token>')
  → If token missing → ProtectedRoute redirects to /login

USER LOGIN (LoginPage → authApi.login)
  → Backend sets sessionid cookie (browser-managed)
  → Frontend receives token + user
  → authStore.login(token, user) mutates state
  → Zustand persist WRITE-THROUGH → `auth-storage` localStorage updated
  → ProtectedRoute re-renders → App.tsx:49 calls paStore.syncUser(user.id) → paStore
     wipes messages/conversations for new user

USER LOGOUT (Sidebar.tsx:356 onClick)
  → paStore.syncUser(null) called (paStore.ts:182-194) → wipes messages,
     activeConversationId, conversations, currentInput, conversationsLoading
     (NOT: activeTool, recentTool, seenSeqs, agentCompletionQueue, seenCompletions)
  → authStore.logout() called (authStore.ts:34-39) → sets token/user/isAuthenticated
     to null/null/false
  → Zustand persist WRITE-THROUGH → `auth-storage` localStorage receives new null-state
     record (partialize serializes the null values, not a delete)
  → NOTE (§14 F6): Zustand persist auto-clear behavior on logout is IMPLICIT — the
     store record persists as `{token: null, user: null, isAuthenticated: false}` in
     localStorage, not deleted. Rehydration reads null-state on next mount.
```

### 7.2 PA dock state hydration + user switch flow

```
BROWSER LOAD
  → Zustand persist hydrates `pa-dock-state` localStorage into paStore
  → migrate function (paStore.ts:398-421) runs if version < 3:
    - v1→v2: adds activeConversationId, conversations, isSidebarOpen, conversationsLoading,
      userId with initial values
    - v2→v3: wipes conversation state (userId, messages, activeConversationId, conversations)
      as pre-user-scoping migration
  → paStore.activeConversationId + messages[last 50] + isDockOpen + currentInput available
     synchronously

GLOBALPADOCK MOUNT (Layout wrapper — global)
  → GlobalPADock.tsx:316-331 useQuery `pa-dock-sync` enabled if
     (!!activeConversationId && isDockOpen && path != '/command-center')
  → If enabled: `assistantApi.getConversation(id)` → refetch → setActiveConversation()
     hydrates messages from server (authoritative record per PR #2352)

USER SWITCH (login as different user)
  → ProtectedRoute re-renders → App.tsx:49 calls paStore.syncUser(newUserId)
  → syncUser wipes messages, activeConversationId, conversations, currentInput
  → BUT: does NOT wipe activeTool, recentTool, seenSeqs, agentCompletionQueue,
     seenCompletions → tool-ticker + agent-completion banners bleed across users
     (§14 F7 user-scoping incomplete)
```

### 7.3 Workspace context resolver flow (F2 hazard site)

```
USER LANDS ON /workspace
  → WorkspacePageNew.tsx:901-911 useEffect sets workspaceStore.setActiveWorkspace(...)
     from route/query param + workspace-list API
  → workspaceStore.activeWorkspace = {id, name, workspace_type?, git_remote_url?}

USER SENDS PA CHAT (from any surface)
  → GlobalPADock.tsx:336-352 (or CommandCenterPage.tsx:1008-1014) reads
     useWorkspaceStore.getState().activeWorkspace at chat-request time
  → Constructs context.workspace_id + context.workspace_name + workspace_mode='workspace'
  → PA backend receives workspace-scoped request

USER HITS F5 (REFRESH)
  → workspaceStore is bare Zustand (no persist) → activeWorkspace = null on re-init
  → paStore is Zustand-persist → activeConversationId + messages hydrate from localStorage
  → GlobalPADock.tsx mounts → activeConversationId present but activeWorkspace = null
  → Next PA chat sent with workspace_id: undefined + workspace_mode: 'global'
  → RIGBY LOSES WORKSPACE CONTEXT MID-CONVERSATION

USER MANUALLY RE-SELECTS WORKSPACE
  → GlobalPADock.tsx:601 workspace picker OR WorkspacePageNew.tsx:901-911 mount effect
  → workspaceStore.setActiveWorkspace(...) restores context
  → Next PA chat resumes workspace-scoped
```

### 7.4 Focused-entity flow (assistantContextStore)

```
WORKSPACE TAB CLICK "ASK RIGBY ABOUT THIS DELIVERABLE"
  → DeliverablesTab.tsx:735 (or WorkTab.tsx:445, HomeTab.tsx:252) calls
     useAssistantContextStore.setFocusedEntity({type: 'deliverable', id, title})
  → Also calls usePAStore.getState().setCurrentInput('...') + openDock()

GLOBALPADOCK RENDERS
  → GlobalPADock.tsx:70 reads focusedEntity
  → Displays context pill in dock header
  → On chatMutation submit: includes focused_entity in context payload
     (GlobalPADock.tsx:344-346)

USER HITS F5 (REFRESH)
  → assistantContextStore is bare Zustand (no persist) → focusedEntity = null on re-init
  → paStore hydrates from localStorage → messages preserved
  → GlobalPADock renders WITHOUT context pill
  → Next PA chat sent WITHOUT focused_entity in context
  → Rigby loses entity focus context mid-conversation (LOW severity — user can re-focus)
```

### 7.5 Session 968 X-UI-Scope request-log ring buffer flow (dev-only)

```
DEV MODE / showDebugPanels localStorage TRUE
  → PanelDebugDrawer.tsx:6 DEV_KEY = 'showDebugPanels'
  → PanelDebugDrawer.tsx:10 reads localStorage.getItem(DEV_KEY) → fallback to
     import.meta.env.DEV
  → If enabled: renders drawer

REQUEST FIRES
  → api.ts:3968-4051 scoped helpers (scopedGet/scopedPost via apiClient.ts:8-30)
     inject X-UI-Scope header + push RequestLogEntry to in-memory requestLog[]
     (bounded MAX_LOG=200; oldest evicted)
  → subscribers (PanelDebugDrawer) receive updates via listeners set

PAGE RELOAD
  → requestLog cleared (session-scoped)
```

## 8. Data Ownership and Lifecycle

### 8.1 Per-key ownership + lifecycle

| Key | Owner (write) | Read consumers | Lifecycle | Cleanup |
|---|---|---|---|---|
| `auth-storage` | authStore.login/logout | App.tsx ProtectedRoute, api.ts:29 interceptor, GlobalPADock, workspace mount effects | Session-persistent; survives refresh | logout mutates state to null; Zustand persist writes-through null-state record (not delete) |
| `navigation-store` | navigationStore.setContext, .addToHistory, .addRecentEntity | `EntityLink.tsx`, `Breadcrumb.tsx` | Persistent (recentEntities only); survives refresh | clearHistory action available; NOT called on logout (§14 F8 leakage) |
| `pa-dock-state` | paStore actions (100+ mutations) | 12 files including GlobalPADock, CommandCenterPage, workspace tabs | Persistent w/ user-scoping (v3 migrate); survives refresh | syncUser(newUserId) wipes conversation state on user change; migrate strips v<3 data |
| `assistant-voice-settings` | CommandCenterPage voice settings save | CommandCenterPage voice-settings load | Session-persistent; survives refresh | No explicit cleanup; per-user (browser-scoped) |
| `cc_dashboard_collapsed` | CommandCenterPage collapse toggle | CommandCenterPage mount | Session-persistent | No cleanup |
| `cc_chat_focus_mode` | CommandCenterPage focus toggle | CommandCenterPage mount | Session-persistent | No cleanup |
| `pipeline_dismissed_${workspaceId}` | WorkspaceDashboardPage dismiss action | WorkspaceDashboardPage mount effect | Per-workspace; unbounded key growth over workspace lifetime | Explicit removeItem on new pipeline run + on undismiss (5 call sites); NO cross-workspace cleanup (§14 F9) |
| `demo-pipeline-dismissed` | DemoPipelineCard dismiss | DemoPipelineCard mount | Session-persistent | No cleanup |
| `cockpit-focus-mode` | useFocusMode hook toggle | useFocusMode hook consumers | Session-persistent | No cleanup |
| `sidebar-collapsed` | Sidebar toggle | Sidebar mount | Session-persistent | No cleanup |
| `sidebar-reference-open` | Sidebar reference-menu toggle | Sidebar mount | Session-persistent | No cleanup |
| `showDebugPanels` | Manual localStorage.setItem (developer) | PanelDebugDrawer mount | Dev-only; session-persistent | No cleanup |
| `deliverables_view_mode` | DeliverablesTab view-mode toggle | DeliverablesTab mount | Session-persistent | No cleanup |
| `cockpit-sidebar-collapsed` | CockpitSidebar toggle | CockpitSidebar mount | Session-persistent | No cleanup |
| `podcast_voice_profile_id` | ContentStudioTab voice-profile select | ContentStudioTab consumers | Session-persistent; removeItem on unselect | Explicit removeItem on unselect |

### 8.2 Cross-user leakage matrix (per S2200 §7.1 Group 2400 Auth handoff — symptom-only)

| Key | Sensitive? | Survives logout? | Bleed risk to next user |
|---|---|---|---|
| `auth-storage` | YES (token + user) | State cleared to null on logout; localStorage record persists as null-state | NONE (null-state is safe) |
| `navigation-store` | LOW (recentEntities: entity metadata only) | YES — no cleanup on logout | **LOW-MED** — next user sees prior user's recently-viewed entities |
| `pa-dock-state` | MEDIUM (conversation context) | Conversation state wiped by syncUser(null); tool/agent-completion NOT wiped | **LOW-MED** — tool-ticker + agent-completion may bleed if same user re-logs OR different user (activeTool/recentTool ephemeral) |
| `assistant-voice-settings` | NONE (voice prefs) | YES | NONE (user prefs, non-sensitive) |
| `cc_*` (2 keys) | NONE (UI chrome) | YES | NONE (cosmetic) |
| `pipeline_dismissed_${workspaceId}` | LOW (per-workspace dismissed IDs) | YES — no cleanup | **LOW** — next user sees prior user's dismissed pipelines per workspace |
| `demo-pipeline-dismissed` | NONE (cosmetic) | YES | NONE |
| `cockpit-*`, `sidebar-*`, `showDebugPanels`, `deliverables_view_mode`, `podcast_voice_profile_id` | NONE (UI prefs) | YES | NONE |

**Two-sided framing (per S2203 §14 F3 precedent — cross-arc handoff):** The logout cleanup
gap is a **frontend-symptom + Group 2400 Auth dependency**. Frontend can eagerly clear
localStorage on logout; the underlying auth-session-lifecycle contract (does logout clear
per-user browser storage? per-org? per-tenant?) is Group 2400 Auth scope. Group 2200 records
the symptom; Group 2400 owns the model.

## 9. Integrations With Other Domains

Per playbook §11.2 §9 (canonical questions #14 + #17 + #18 + #21 + #22). Applied to
state-persistence surface at HEAD `8fbf17eb`.

| Domain | Direction | Strength | Evidence | Cross-arc coordination |
|---|---|---|---|---|
| **Group 2400 Auth** | Downstream (frontend consumes auth state) | **STRONG-WITH-CLEANUP-GAP** | `authStore` persists token + user; `authApi.logout()` at Sidebar.tsx:356 clears state but not localStorage record; user-switch (paStore.syncUser at App.tsx:49) partial — tool-ticker + agent-completion NOT wiped | Symptomatic + descriptive only per S2200 §7.1; Group 2400 owns model |
| **Group 2500 API** | Upstream (backend API contracts) | **STRONG-WITH-DUAL-INCLUSION** | GlobalPADock.tsx:340-352 includes `workspace_id` in BOTH `context` object AND payload root; CommandCenterPage.tsx:1013 includes only at payload root; canonical field unclear from frontend | Cross-arc flag for Group 2500 API contract SoT design ownership (S2203 §20.6 POSTURE-DECISION Option (c) DEFER precedent) |
| **Group 2600 PA** | Peer (frontend renders PA; PA state cross-surface-shared) | **STRONG-CROSS-CUTTER** | `paStore` 57 sites across 12 files; `workspaceStore` 144 sites across 16 files; `assistantContextStore` 16 sites across 5 files; PA workspace-context resolver F2 hazard on refresh | Group 2600 PA arc owns behavioral spec + persistence contract for workspaceStore + assistantContextStore rendering |
| **Group 1500 Sports** | Peer (consumer) | **WEAK-EPHEMERAL** | `BettingPage.tsx` uses `useState<BettingTab>('hub')` only; no localStorage; no URL state | Confirms S1505 §14.10 single-route baseline; NO whole-frontend generalization |
| **Group 1600 Content** | Peer (consumer) | **PARTIAL-DECLARED** | `ContentStudioTab.tsx` uses `podcast_voice_profile_id` localStorage (ACCIDENTAL — inline string, no constant); `deliverables_view_mode` DECLARED-partial | Cross-arc flag per S2200 §7.1 render/publish split |
| **Group 1800 HumanAttention** | Peer (consumer) | **PARTIAL-VIA-UNIFIED-STORE** | `unifiedStore` fetched by Layout + Sidebar + CommandCenterPage; attention counts read but not persisted (5s throttle bookkeeping in-memory) | Cross-arc: HumanAttention decision eligibility semantics remain Group 1800; render-shape (unified-store selectors) is Group 2200 |
| **Group 1900 Body Systems / Governance** | Peer (governance) | **STRONG-VIA-BODY-STORE** | `bodyStore` consumed by `services/bodyGovernance.ts` for governance rules + `GlobalAlertBanner` for footer alerts; no persistence (in-memory + 5s throttle) | Group 1900 owns body semantic authority; Group 2200 renders alerts + governance banner |
| **Group 1700 Observability** | Peer (dev-mode telemetry) | **WEAK-DEV-ONLY** | Session 968 X-UI-Scope request-log ring buffer + `showDebugPanels` localStorage dev-only surface | Group 1700 owns backend request-log semantic; frontend ring buffer is dev-only mirror |
| **Group 1300 Memory** | Peer (consumer) | **NONE-VISIBLE-AT-STATE-LAYER** | Memory palace / learning / evolution renders exist per topics/frontend.md §Workspace Architecture row 6 but no state-persistence artifact in Child D scope | Group 1300 owns memory semantic; Group 2200 renders |
| **Group 2300 Mobile** | Out-of-tree | **EXCLUDED** | Expo scaffolding row 19; no state-persistence artifact | Excluded per S2200 §7 anti-scope |

**Overall integration verdict:** 3 STRONG-cross-cutter cross-arc handoffs (Group 2400 Auth,
Group 2500 API, Group 2600 PA). 5 PARTIAL / WEAK integrations. 1 EXCLUDED (Group 2300
Mobile). No integration is unclassified.

## 10. Event Flows

Per playbook §11.2 §10 (canonical questions #19 + #20).

### 10.1 Event flows into state

| Event | Fires when | Writes to |
|---|---|---|
| `authStore.login(token, user)` | User completes LoginPage login flow | localStorage `auth-storage` (via Zustand persist write-through) |
| `authStore.logout()` | Sidebar.tsx:356 logout onClick | localStorage `auth-storage` receives null-state record |
| `paStore.addMessage` | PA WebSocket + PA polling deliveries | localStorage `pa-dock-state` (Zustand persist write-through, last 50 kept) |
| `paStore.syncUser(newUserId)` | App.tsx:49 ProtectedRoute detects user change | localStorage `pa-dock-state` receives wiped conversation state |
| `paStore.handleToolStarted/handleToolCompleted` | WS tool events (Session 1172) | In-memory state only (not persisted per partialize) |
| `paStore.handleAgentCompleted` | WS agent-completion events (Session 1175) | In-memory queue (not persisted per partialize) |
| `navigationStore.setContext` | Cross-page nav (EntityLink click, Breadcrumb click) | localStorage `navigation-store` receives updated recentEntities |
| `workspaceStore.setActiveWorkspace` | WorkspacePageNew mount + workspace picker click (GlobalPADock:601, CockpitSidebar:92,195,216, WorkspaceQuickSelect at CommandCenterPage:2526-2531) | In-memory only (F2 hazard) |
| `assistantContextStore.setFocusedEntity` | DeliverablesTab:735 + WorkTab:445 + HomeTab:252 "Ask Rigby" | In-memory only (LOW-severity refresh loss) |
| `bodyStore.fetchVitals/fetchAlerts` | Layout mount + 5s throttle + poll | In-memory (deliberate ephemeral) |
| `unifiedStore.fetchAll` | Layout mount + Sidebar refresh + 5s throttle | In-memory (deliberate ephemeral) |

### 10.2 Event flows out of state

| Event | Fires when | Reads from |
|---|---|---|
| PA chat submission | User submits message via GlobalPADock or CommandCenterPage | Reads `workspaceStore.activeWorkspace` + `assistantContextStore.focusedEntity` + `paStore.activeConversationId` + `authStore.token` (via api.ts:29 interceptor) |
| PA feedback submission | User rates message | Reads `document.cookie` `sessionid` (paStore.ts:241) + `paStore.activeConversationId` + `paStore.messages` |
| API request | Any api-module call | Reads `authStore.token` via api.ts:29 interceptor for `Authorization: Token <key>` header |
| Route guard | Any protected route load | Reads `authStore.isAuthenticated` via App.tsx ProtectedRoute |
| Global alert banner | Body health degrades | Reads `bodyStore.alerts` |
| Sidebar badges + quick-access | Layout renders | Reads `unifiedStore.attention/opportunities/pilots/gates` selectors |

### 10.3 Cross-tab event surface

**Zustand persist middleware does NOT install storage-event listeners by default.**
Verified via Explore 3 grep — 0 `addEventListener('storage'`, 0 `BroadcastChannel`, 0
tab-sync mechanisms across `frontend/src/`. Multi-tab state divergence:

- User logs out in Tab A → Tab B's authStore stays populated until reload OR api.ts:48-56
  silent-401 fires on next 401 response
- Sidebar collapse in Tab A → Tab B does not update until reload
- PA state (messages, conversations) is not synced between tabs

**Class:** informational observation for single-tab-primary-UX design; NOT a bug per current
platform assumption. Cross-tab UX would require BroadcastChannel or storage-event
listener installation (post-arc T-slot candidate; low priority).

## 11. Existing Documentation

Per playbook §11.2 §11 (canonical question #10 — existing docs).

### 11.1 topics/frontend.md coverage

`docs/topics/frontend.md` is stale-warned (DOC-POINTER-V1 banner). Coverage of state
persistence:

- §PA Integration documents "shared assistant context store" + workspace-context resolver
  but does NOT state persistence discipline (in-memory vs persist)
- §Page Telemetry documents `usePageTracking()` fire-and-forget POST (Layout:14 wiring per
  S2201 baseline) — treated as backend-owned side-effect per S2200 §5 Q6 CLEAN fold
- §Workspace Architecture row 6 documents Memory palace / learning / evolution renders but
  no state-persistence detail
- Zustand store enumeration in the doc mentions "paStore (conversations, sidebar state),
  workspaceStore (active tab/sub-tab)" — INCOMPLETE per §14 F1 drift finding

**Coverage: PARTIAL / LIGHT.** No dedicated persistence-discipline documentation exists.

### 11.2 PLATFORM_INVENTORY.md coverage

`docs/PLATFORM_INVENTORY.md:30` §Frontend row: "5 workspace primary tabs, 9 betting
dashboard tabs" — **no persistence row.** xx99 §7 anchor-update batch candidate: add a
State Persistence row per S2202 §14 F8 PLATFORM_INVENTORY WS-augmentation observation
precedent.

### 11.3 Prior arc coverage

- **S1505 §14.10 + §15.3** — Sports Cat E single-route zero-persistence baseline + MED
  remediation options (URL params / localStorage / Zustand slice). Load-bearing for F2
  hypothesis falsifier framework.
- **S2201 §5 (7 Zustand stores enumerated)** + §14 F5 (`legacyTabMapping` state-adjacent
  surface — backward-compat mapping, not persisted state) — deferred consumer + persistence
  mapping to S2204 Child D per parent scoping §5.
- **S2202 §17 T6** — PA WS + polling parallel (state-adjacent T-slot deferred to Group
  2600 PA).
- **S2203 §14 F3 + §16.1** — SYSTEMIC silent-401 + `authStore` token-persistence adjacency;
  `api.ts:2` imports `@/stores/authStore` verified INTENTIONAL (not boundary violation).

### 11.4 Documentation coverage classification

Per playbook §12 Research Coverage:

- **State persistence discipline (whole-frontend)**: **NONE-to-LIGHT** — S1505 §14.10 covers
  betting-slice; no whole-frontend audit exists prior to this doc.
- **Individual store shapes**: **LIGHT** — Zustand store files are self-documenting via
  TypeScript interfaces; no external prose documentation.
- **Session 968 X-UI-Scope ring buffer**: **LIGHT** — Session 968 handoff exists; no ongoing
  documentation.
- **Zustand persist conventions**: **NONE** — no doc/guideline documents kebab-case vs
  snake_case naming, version+migrate expectations, or partialize contract.

## 12. Research Coverage

Per playbook §12 Research Coverage classification. Assessed per surface:

| Surface | Coverage Before S2204 | Coverage After S2204 |
|---|---|---|
| authStore | LIGHT (S2203 §14 F3 token-persistence adjacency; S2203 §16.1 verified INTENTIONAL boundary) | MODERATE (whole-store audit + version+migrate gap surfaced) |
| navigationStore | NONE | LIGHT (consumer map + persist-config audit surfaced) |
| paStore | LIGHT (S2201 §5 baseline enumerate; S2202 §17 T6 flag) | MODERATE (consumer map + v3 migrate discipline + syncUser gap surfaced) |
| workspaceStore | NONE | MODERATE (consumer map + F2 F5-refresh hazard surfaced) |
| assistantContextStore | NONE | LIGHT (consumer map + F4-refresh loss surfaced) |
| bodyStore | NONE | LIGHT (consumer map + governance-service coupling surfaced) |
| unifiedStore | NONE | LIGHT (consumer map + Layout+Sidebar+CC read map surfaced) |
| Direct localStorage 12 keys | NONE | MODERATE (per-key inventory + declared-vs-accidental classification + naming drift surfaced) |
| React Query cache posture | NONE | LIGHT (staleTime 60s + no persistent adapter surfaced) |
| Session 968 X-UI-Scope ring buffer | LIGHT (S2203 §5.3 mention) | LIGHT (surfaced as in-memory ring buffer; no deeper audit) |
| Cross-tab sync | NONE | LIGHT (0 storage-event / 0 BroadcastChannel confirmed) |
| Cookie reads | LIGHT (implicit via api.ts:24 credentials handling) | LIGHT (single sessionid read at paStore.ts:241 surfaced) |
| PA workspace-context resolver flow | NONE | **MODERATE-DEEP** — full resolver flow + F2 refresh-loss hazard documented |

**Post-S2204 state persistence coverage: MODERATE** whole-frontend (was NONE). Deeper
per-store schemas + per-store test coverage remain research follow-up per §19.

## 13. Architecture Maturity

Per playbook §12 Architecture Maturity classification (EXPERIMENTAL / PARTIAL / WORKING /
STABLE / CANONICAL).

### 13.1 Per-store maturity

| Store | Verdict | Evidence |
|---|---|---|
| `authStore` | **WORKING** | Persisted with partialize; no version/migrate (schema-drift risk); functional across all consumers; api.ts interceptor integration is INTENTIONAL (S2203 §16.1) |
| `navigationStore` | **WORKING** | Persisted with partialize (recentEntities only); 2 real consumers (EntityLink + Breadcrumb); no version discipline; functional |
| `paStore` | **STABLE** | Persisted with v3 + migrate + user-scoping via syncUser; 57 sites across 12 files; 5 documented migrations (v1→v2 + v2→v3); tool-ticker + agent-completion state ephemeral by design |
| `workspaceStore` | **PARTIAL** | In-memory only; F2 refresh-loss hazard on cross-surface PA chat context resolution; 144 sites across 16 files; consumer count amplifies impact |
| `assistantContextStore` | **PARTIAL** | In-memory only; refresh loses focused entity pill; 16 sites across 5 files; low severity per user-recoverable |
| `bodyStore` | **STABLE-BY-DESIGN** | In-memory ephemeral with 5s throttle bookkeeping; governance-service integration functional; alerts render globally; ephemeral is intentional (live health state) |
| `unifiedStore` | **STABLE-BY-DESIGN** | In-memory ephemeral with 5s throttle; Layout + Sidebar + CommandCenterPage consume; ephemeral is intentional (live metrics) |

### 13.2 Per-surface maturity (per S2200 §5 Q1 STRENGTHEN fold — per-surface reporting)

| Surface | Verdict | Evidence |
|---|---|---|
| **Workspace** | **PARTIAL** | 5 stores read; workspaceStore F2 hazard; 3 direct keys with 2 ACCIDENTAL (`pipeline_dismissed_*` + `podcast_voice_profile_id`) and 1 DECLARED-partial (`deliverables_view_mode` — inline `window.localStorage`); URL state for tab routing DECLARED |
| **Betting** | **EXPERIMENTAL-BY-DESIGN** | Zero client-side state persistence per S1505 §14.10 confirmed; `BettingPage.tsx` uses `useState<BettingTab>('hub')` in-memory only; S1505 §15.3 remediation options unimplemented |
| **Command Center** | **WORKING-WITH-MIXED-DISCIPLINE** | 5 stores read; 3 direct keys with 1 DECLARED (`assistant-voice-settings` via constant + JSON shape) and 2 ACCIDENTAL (`cc_dashboard_collapsed` + `cc_chat_focus_mode` inline strings); functional across all surfaces |
| **PA** | **STABLE** | paStore v3 + migrate best-practice; workspaceStore + assistantContextStore refresh-loss hazards; cross-surface consumption intentional; server-round-tripped authoritative record |
| **Global (Layout + Sidebar + Auth)** | **WORKING** | authStore + navigationStore persist; 4 direct keys mostly DECLARED; unified + body stores in-memory-by-design; functional |

### 13.3 Whole-domain maturity verdict

**Per-store baseline: WORKING** (weighted by consumer count: PA STABLE + Auth WORKING +
Body/Unified STABLE-BY-DESIGN dominate over PARTIAL workspace + assistantContext).

**Per-surface baseline: WORKING-WITH-PARTIAL-WORKSPACE-HAZARD** — 3 STABLE / STABLE-BY-DESIGN,
2 WORKING, 1 EXPERIMENTAL-BY-DESIGN (betting), 1 PARTIAL (workspace).

**S2201 §14.1 F1 32-domain row 18 posture pressure-test (S2201 §20.6 owed candidate):**
this-child state-persistence evidence contributes to **potential downgrade** from
**STABLE + DEEP** to **WORKING + MODERATE**. Route-composition + Layout are STABLE (S2201
baseline); page components are WORKING (S2201 F2 god-components); contract discipline is
PARTIAL-to-UNMET (S2201 F2/F3 + S2202 F1/F6 + S2203 F1/F5); state persistence discipline is
WORKING-WITH-PARTIAL-WORKSPACE-HAZARD (this doc §13.2). **Downgrade decision deferred to
S2299 canonical summary rollup across all 4 children** per Rigby SIGN cycle 1 Q8 REJECT
2026-07-05 fold — this child alone provides local mismatch evidence but is insufficient to
downgrade the whole-domain posture. Chris ratifies at S2299 close card.

## 14. Known Drift

Per playbook §11.2 §14 (canonical question #23). Drift = docs say X, runtime says Y.

### 14.0 Verification scope statement (per Rigby SIGN cycle 1 Q9 STRENGTHEN 2026-07-05 fold)

State-persistence surface verification scope at HEAD `8fbf17eb`:

- **Source-code greps (2 independent passes):** `localStorage\.setItem|.getItem|.removeItem|.clear` + `sessionStorage\.` + `document\.cookie` + `indexedDB|IndexedDB|idb` across `frontend/src/**/*.{ts,tsx}` — 0 sessionStorage + 0 IndexedDB + 1 cookie read observed.
- **Wrapper-library grep:** `idb`, `dexie`, `localforage` — 0 matches in source code.
- **Dependency-scan (Q9 STRENGTHEN fold):** `frontend/package.json` declares `"zustand": "^4.4.0"` + no `idb` + no `dexie` + no `localforage`. Confirmed at both source AND dependency level.
- **Dynamic-import grep:** no dynamic imports of storage-adjacent modules observed.

Coverage caveat: this does NOT verify against transitive dependency use of IndexedDB
(e.g., a 3rd-party lib may internally use IDB); such use would not be a client-side state
surface Group 2200 owns.

### 14.1 F1 — topics/frontend.md 7-store enumeration incomplete (drift)

**Claim.** docs/topics/frontend.md Zustand mentions "paStore (conversations, sidebar
state), workspaceStore (active tab/sub-tab)" — enumerates 2 of 7 stores.

**Runtime.** 7 stores exist: authStore + navigationStore + paStore + workspaceStore +
assistantContextStore + bodyStore + unifiedStore (verified via `ls frontend/src/stores/`
+ Explore 1 + verifier-loop).

**Severity.** MED — narrative doc under-represents state surface.

**Class.** `drift`.

**Reconcile at:** xx99 §7 anchor-update batch (topics/frontend.md next refresh cycle) OR
docs-cascade fold-in at S2299 close.

### 14.2 F2 — PLATFORM_INVENTORY.md §Frontend has no state-persistence row (drift)

**Claim.** PLATFORM_INVENTORY.md:30 §Frontend headline: "5 workspace primary tabs, 9
betting dashboard tabs".

**Runtime.** 3 Zustand persist stores + 12 direct localStorage keys + 1 cookie read + 1
in-memory ring buffer = 15+ persistence-adjacent surfaces.

**Severity.** LOW-MED — inventory-augmentation gap analogous to S2202 §14 F8 WebSocket
augmentation observation.

**Class.** `drift` — inventory omission.

**Reconcile at:** xx99 §7 anchor-update batch (regen PLATFORM_INVENTORY §Frontend with a
State Persistence row: 3 Zustand persist stores + 12 direct localStorage + 0 sessionStorage
+ 0 IndexedDB + 1 cookie + 1 in-memory ring buffer).

### 14.3 F3 — Naming convention drift (drift, low severity)

**Claim (implicit).** Frontend has an implicit convention for localStorage keys.

**Runtime.** Mixed: 6 kebab-case + 3 snake_case + 3 camelCase across 12 direct keys; 3
Zustand persist keys all kebab-case.

**Severity.** LOW — inconsistency, not violation.

**Class.** `drift` — style inconsistency.

**Class disambiguation.** LOW severity per S2201 F5 precedent (S1505 §14.2 pattern-class
introduction — style drift vs functional regression). Not `technical_debt` (see §15.2).

**Reconcile at:** xx99 §8 T-slot queue if maintainer-decision batch bundles a
naming-convention adoption R-item.

### 14.4 F4 — navigationStore consumer perception (SUB-AGENT ERROR CORRECTED)

**Sub-agent claim.** Explore 5 report classified `navigationStore` as DEAD (0 consumers).

**Verifier-loop finding.** Grep for `useNavigationStore` + selectors returned 3 files:
`navigationStore.ts` (self), `EntityLink.tsx`, `Breadcrumb.tsx`. **navigationStore is NOT
DEAD** — 2 real consumers use `useNavigationContext` + `useNavigationHistory` +
`useRecentEntities` for cross-page breadcrumb rendering.

**Severity.** N/A — verifier-loop correction, not a drift finding.

**Class.** Verifier-loop artifact per playbook §14 rule "trust but verify". Recorded in §20
Appendix.

### 14.5 F5 — `workspaceStore.activeWorkspace` in-memory-only creates PA-context-loss on refresh (drift + tech-debt)

**Claim.** `workspaceStore.ts:24-27` declares `create<WorkspaceStore>((set) => ({...}))`
with NO `persist` middleware.

**Runtime.** 144 consumer sites across 16 files including `GlobalPADock.tsx:340-352`
+ `GlobalPADock.tsx:943` + `CommandCenterPage.tsx:1013` inject `activeWorkspace.id` and
`activeWorkspace.name` into PA chat context payload. On F5/refresh, activeWorkspace = null →
subsequent PA chats sent with `workspace_id: undefined` + `workspace_mode: 'global'`.

**Severity.** **MED-HIGH cross-surface amplification** — Rigby loses workspace context
mid-conversation until user manually re-selects workspace via GlobalPADock:601 picker or
WorkspacePageNew:901 mount effect.

**Class.** `drift` — narrative intent (workspace-scoped chat) diverges from runtime behavior
(refresh drops scoping) + `technical_debt` (should-persist-but-doesn't).

**Two-sided framing (per S2203 §14 F3 precedent):** the workspace-store-persistence-gap is a
**frontend-symptom + Group 2600 PA arc-scope decision**. Frontend can add `persist` middleware
with partialize+version+migrate; the underlying question — is workspace context a session-scoped
render surface (persist) or an ephemeral user-input surface (re-select on each session) — is
Group 2600 PA behavioral scope.

**Reconcile at:** xx99 §8 T-slot queue candidate; cross-arc coordination flag for Group 2600
PA arc.

### 14.6 F6 — Zustand persist "functional clear via null-state" vs "storage deletion" distinction (drift)

**Claim (implicit).** authStore.logout() at authStore.ts:34-39 mutates state to null;
Zustand persist writes-through.

**Runtime.** localStorage `auth-storage` record persists after logout as
`{token: null, user: null, isAuthenticated: false, ...}` — NOT deleted. Next mount rehydrates
null-state (safe). No `storage.removeItem` call anywhere on logout.

**Verifier-loop (Rigby SIGN cycle 1 Q5 STRENGTHEN 2026-07-05 fold — resolves §20.3 U1
UNKNOWN):** `frontend/package.json` declares `"zustand": "^4.4.0"`. Zustand 4.4+ persist
middleware default behavior on `set({token: null, user: null, isAuthenticated: false})`:
calls `partialize(nextState)` → `JSON.stringify(partializedState)` → `storage.setItem(name,
serialized)`. Does NOT call `storage.removeItem`. Rehydration on next mount reads
`{token:null, user:null, isAuthenticated:false}` → ProtectedRoute reads `isAuthenticated:
false` → redirects to /login. **Functional-clear-via-null-state is functionally
equivalent** to storage deletion at the auth-gate boundary; it is NOT storage deletion at
the localStorage-record boundary.

**Explicit distinction (Rigby SIGN cycle 1 close-tighten 2026-07-05 fold):**
- **Functional clear via null-state:** authStore state = null-values; ProtectedRoute
  gates; user cannot access protected routes. **Functionally equivalent to logout.**
- **Storage deletion:** `localStorage.removeItem('auth-storage')` — NOT called anywhere.
  localStorage record persists as null-state until next mutation overwrites.

**Severity.** LOW — functional-clear via null-state is functionally safe. Documented drift
only in that "intent-implied storage clear" diverges from "runtime write-null-record"
behavior; no active regression.

**Class.** `drift` — semantic behavior distinction (low blast radius); U1 unknown from
§20.3 RESOLVED via Q5 verifier-loop.

**Reconcile at:** xx99 §7 anchor-update or in-code comment; no urgent T-slot action needed
absent a Group 2400 Auth arc directive.

### 14.7 F7 — paStore.syncUser incomplete user-scoping (drift)

**Claim.** paStore.syncUser at paStore.ts:182-194 wipes conversation state on user change
to prevent conversation bleed.

**Runtime.** syncUser wipes `messages`, `activeConversationId`, `conversations`,
`currentInput`, `conversationsLoading`. Does NOT wipe `activeTool`, `recentTool`, `seenSeqs`,
`agentCompletionQueue`, `recentAgentCompletion`, `seenCompletions`.

**Severity.** LOW — tool-ticker + agent-completion state are ephemeral (not persisted per
partialize); user-switch bleed lasts only until next mount (page reload clears these
in-memory-only fields). Cross-user visual pollution possible for 1-2 seconds if user-switch
happens without page reload.

**Class.** `drift` — intent (user-scoped) diverges from runtime (ephemeral-fields not
scoped).

**Reconcile at:** xx99 §8 T-slot queue candidate; low-priority cleanup.

### 14.8 F8 — navigationStore.recentEntities cross-user leakage (drift + tech-debt)

**Claim (implicit).** navigationStore.clearHistory action exists at navigationStore.ts:96-97;
persistence-clear on user change would be a valid action to call at logout.

**Runtime.** `clearHistory` is NEVER called on logout. Sidebar.tsx:356 logout flow
(syncUser(null) → authStore.logout()) does not touch navigationStore. Result: next user
sees prior user's recently-viewed entities (type + id + label + timestamp).

**Severity.** LOW-MED — entity metadata is low-sensitivity but leaks browsing history to
next-user on shared browsers.

**Class.** `technical_debt` — logout hygiene gap (Group 2400 Auth adjacent).

**Reconcile at:** xx99 §8 T-slot queue candidate.

### 14.9 F9 — `pipeline_dismissed_${workspaceId}` unbounded key growth (drift, low severity)

**Claim (implicit).** WorkspaceDashboardPage.tsx:132-270 stores dismiss-run IDs per
workspace.

**Runtime.** Each workspace visited creates a new localStorage key (`pipeline_dismissed_ws-001`,
`pipeline_dismissed_ws-002`, ...). No cross-workspace cleanup. Key count grows unbounded
per user session across workspace navigation history.

**Severity.** LOW — localStorage 5-10MB quota is far above practical key size; observed key
values are short strings (pipelineRun.id).

**Class.** `technical_debt` — hygiene gap (rare-scenario).

**Reconcile at:** xx99 §8 T-slot queue; low priority.

## 15. Known Technical Debt

Per playbook §11.2 §15 (canonical question #24). Severity + class per playbook §12.

### 15.1 MED — authStore + navigationStore lack version + migrate (schema-drift risk)

**Class.** `technical_debt`

**Evidence.** authStore.ts:43-50 + navigationStore.ts:98-105 both declare `persist({...})`
without `version` + `migrate`. paStore.ts:395-431 has `version: 3` + `migrate` covering v1→v2
+ v2→v3.

**Severity.** MED — LOW today (schemas stable); MED at next schema change (silent stale
rehydration).

**Two-sided framing.** Not a Group 2400 Auth model concern; frontend persistence hygiene
only. Group 2200 owns.

### 15.2 MED-LOW — 6 of 12 direct localStorage keys ACCIDENTAL (per-key rubric formalized)

**Class.** `technical_debt`

**Per-key discipline rubric (Rigby SIGN cycle 1 Q4 STRENGTHEN 2026-07-05 fold —
formalized to reduce reviewer ambiguity):** A key is **DECLARED** iff it satisfies ALL
FOUR criteria:

- **C1: Constant reference.** Key is a named constant (not inline string literal).
- **C2: Typed accessor.** Read/write goes through a typed accessor (getItem+JSON.parse
  with typed cast, or dedicated helper), NOT bare `localStorage.getItem` + string
  comparison.
- **C3: Graceful fallback.** Missing/malformed value falls back to a documented default
  rather than throwing.
- **C4: Namespaced template disciplined.** For templated keys (e.g.,
  `${prefix}_${suffix}`), the prefix is a constant + the suffix is validated at the
  call site.

A key is **ACCIDENTAL** if it fails ≥1 criterion. **MIXED** if it satisfies some but has
inconsistent application across call sites (e.g., constant read but inline write).

**Evidence per key:**

| Key | C1 constant? | C2 typed? | C3 fallback? | C4 template? | Verdict |
|---|---|---|---|---|---|
| `sidebar-collapsed` | ✓ (inline, single-usage) | ✓ (boolean parse) | ✓ | n/a | DECLARED |
| `sidebar-reference-open` | ✓ (inline, single-usage) | ✓ (boolean parse) | ✓ | n/a | DECLARED |
| `cockpit-focus-mode` | ✓ (`STORAGE_KEY` const) | ✓ (boolean parse) | ✓ | n/a | DECLARED |
| `cockpit-sidebar-collapsed` | ✓ (inline, single-usage) | ✓ (boolean parse) | ✓ | n/a | DECLARED |
| `assistant-voice-settings` | ✓ (`VOICE_SETTINGS_KEY` const) | ✓ (JSON.parse typed) | ✓ | n/a | DECLARED |
| `demo-pipeline-dismissed` | ✓ (inline, single-usage) | ✓ (boolean parse) | ✓ | n/a | DECLARED |
| `cc_dashboard_collapsed` | ✗ (inline string literal at 2 call sites) | ✗ (`=== 'true'` comparison) | ✓ (try/catch swallow) | n/a | ACCIDENTAL |
| `cc_chat_focus_mode` | ✗ (inline string literal) | ✗ (`? '1' : '0'` string coerce) | ✓ (try/catch swallow) | n/a | ACCIDENTAL |
| `deliverables_view_mode` | ✗ (inline `window.localStorage`, string literal) | ✗ (raw string, no shape) | ~partial | n/a | ACCIDENTAL |
| `pipeline_dismissed_${workspaceId}` | ✗ (inline template at 5 call sites) | ✗ (raw string ID) | ~partial | ✗ (workspaceId not validated) | ACCIDENTAL |
| `podcast_voice_profile_id` | ✗ (inline string literal at 3+ call sites) | ✗ (raw voice ID) | ~partial | n/a | ACCIDENTAL |
| `showDebugPanels` | ✓ (`DEV_KEY` const) | ✗ (called inline with swallow-catch; not through typed accessor) | ✓ | n/a | **MIXED** — constant + swallow but not typed-accessor pattern; for rubric purposes classified ACCIDENTAL (fails C2) |

**Count.** 6 DECLARED / 6 ACCIDENTAL — reconciled by rubric.

**Severity.** MED-LOW — future collision risk + maintenance debt. LOW at single-operator
scale; MED at team-scale.

**Remediation options (research finding only, non-authoring):**
- (a) Introduce `frontend/src/lib/storageKeys.ts` centralized registry.
- (b) Adopt typed accessor pattern (e.g., `getLocalStorageJSON<T>(key)` with schema).
- (c) Formalize kebab-case convention (6 of 12 already use it).

### 15.3 MED-HIGH — workspaceStore in-memory only, PA-context-loss on refresh (§14 F5)

**Class.** `technical_debt` — cross-surface impact amplifier.

**Severity.** MED-HIGH per cross-surface amplification (12 PA-side consumers).

**Cross-arc scope decision required.** Group 2600 PA behavioral spec owns the decision:
should `activeWorkspace` persist (session-scoped) or be re-selected each session?

### 15.4 LOW — assistantContextStore in-memory only, focus-loss on refresh (§14 F4)

**Class.** `technical_debt`

**Severity.** LOW — user-recoverable via re-click; no data-loss.

### 15.5 LOW-MED — No shared storageKeys registry / no typed accessor layer

**Class.** `technical_debt`

**Evidence.** 15 localStorage keys (12 direct + 3 Zustand) with no central registry;
string-based key access; no type safety on shape.

**Severity.** LOW-MED — future-collision risk + maintenance debt.

### 15.6 LOW — Naming convention drift (kebab + snake + camel mix) (§14 F3)

**Class.** `technical_debt`

**Severity.** LOW — style drift, no functional impact.

### 15.7 LOW-MED — No cross-tab sync mechanism (§10.3)

**Class.** `technical_debt`

**Evidence.** 0 storage-event listeners; 0 BroadcastChannel. Multi-tab UX diverges after
logout / setting toggle.

**Severity.** LOW-MED — current platform assumption is single-tab-primary; low priority.

### 15.8 LOW — paStore.syncUser incomplete user-scoping (§14 F7)

**Class.** `technical_debt`

**Severity.** LOW — tool-ticker + agent-completion fields ephemeral; user-switch bleed 1-2s
until next mount.

### 15.9 LOW — navigationStore.recentEntities cross-user leakage (§14 F8)

**Class.** `technical_debt`

**Severity.** LOW-MED — LOW-sensitivity data (entity metadata) but leaks to next-user on
shared browsers.

### 15.10 LOW — `pipeline_dismissed_${workspaceId}` unbounded key growth (§14 F9)

**Class.** `technical_debt`

**Severity.** LOW — practical footprint tiny.

### 15.11 Debt matrix summary

| ID | Severity | Class | Fix scope |
|---|---|---|---|
| §15.1 | MED | technical_debt | Frontend-only (add version+migrate to authStore + navigationStore) |
| §15.2 | MED-LOW | technical_debt | Frontend-only (constant + typed accessor + registry) |
| §15.3 | MED-HIGH | technical_debt (cross-surface) | Group 2600 PA scope decision + frontend implementation |
| §15.4 | LOW | technical_debt | Frontend-only (add persist + partialize) — only if Group 2600 PA arc directs |
| §15.5 | LOW-MED | technical_debt | Frontend-only (registry file) |
| §15.6 | LOW | technical_debt | Frontend-only (rename) |
| §15.7 | LOW-MED | technical_debt | Frontend-only (BroadcastChannel install) |
| §15.8 | LOW | technical_debt | Frontend-only (extend syncUser field list) |
| §15.9 | LOW-MED | technical_debt | Frontend-only (call clearHistory on logout) + Group 2400 Auth alignment |
| §15.10 | LOW | technical_debt | Frontend-only (cleanup on workspace-change) |

**Total debt items: 10** (1 MED-HIGH, 2 MED, 2 MED-LOW, 5 LOW). No CRITICAL; no HIGH per
S2200 §7.1 render-authority scope (auth model + PA behavior scope carved out to Groups 2400
+ 2600 per S2200 §7.1 render-authority split).

## 16. Boundary Violations

Per playbook §11.2 §16 (canonical question #25).

### 16.1 `api.ts` imports `@/stores/authStore` (INTENTIONAL, NOT VIOLATION)

**Precedent.** S2203 §16.1 verified this pattern at HEAD `0ce569f6` as INTENTIONAL (auth
interceptor at api.ts:29 legitimately needs token access from non-React axios
interceptor context). **Re-verified unchanged at HEAD `8fbf17eb`** (Rigby SIGN cycle 1
Q14 STRENGTHEN 2026-07-05 fold — explicit unchanged-at-HEAD verifier-loop citation, not
stale S2203 recitation): `frontend/src/lib/api.ts:2` import `useAuthStore` present;
`frontend/src/lib/api.ts:29` interceptor read `useAuthStore.getState().token` present;
no shape or intent change vs S2203 close. Class: intentional cross-boundary import, not
violation.

### 16.2 `services/bodyGovernance.ts` imports `@/stores/bodyStore` (INTENTIONAL)

**Evidence.** `frontend/src/services/bodyGovernance.ts:5` imports `useBodyStore`. Used in
non-React contexts (governance checks: pilot, agent_execution, file_write authorization)
via `useBodyStore.getState()`. Class: intentional service-layer cross-boundary import;
Group 1900 Body/Governance owns semantic authority per S2200 §7.1 render-authority split.

### 16.3 `GlobalPADock.tsx` reads `useWorkspaceStore.getState()` from non-React context (INTENTIONAL)

**Evidence.** `GlobalPADock.tsx:340-351` + `:548-549` + `:943` uses `useWorkspaceStore.getState()`
inside `chatMutation.mutationFn` (non-React scope). Class: intentional imperative read
pattern; consistent with useAuthStore pattern in api.ts:29.

### 16.4 No component-level Zustand-store internal imports

**Grep result.** No component imports `frontend/src/stores/*/state` or internal setters
outside the exported hook contract. Stores are accessed via `use*Store` hooks only.

### 16.5 No storage-key writes from outside owning file

**Grep result.** Each of 12 direct localStorage keys is written from exactly 1 owner file.
No key has multi-file writers.

**Boundary violation verdict: NONE.** All cross-boundary imports (authStore in api.ts,
bodyStore in bodyGovernance, workspaceStore in GlobalPADock) are INTENTIONAL per prior arc
precedents + this arc's verifier-loop.

## 17. Duplicate or Overlapping Systems

Per playbook §11.2 §17 (canonical question #26).

### 17.1 assistantContextStore.focusedEntity vs paStore.currentInput (COMPLEMENTARY, NO OVERLAP)

**Framing.** `focusedEntity` names which entity Rigby should attend to; `currentInput`
holds draft chat text. Complementary render surfaces. No overlap; no consolidation
candidate.

### 17.2 navigationStore.recentEntities vs workspace tab history (SEPARATE SCOPES, NO OVERLAP)

**Framing.** `navigationStore.recentEntities` tracks cross-page navigation breadcrumbs
(source page → destination entity); workspace tab selection is in-memory URL-driven
routing. Different scopes; no overlap.

### 17.3 bodyStore vs unifiedStore (SEPARATE DOMAINS, NO OVERLAP)

**Framing.** `bodyStore` holds system health vitals + alerts (Group 1900 Body Systems /
Governance); `unifiedStore` holds attention + opportunities + pilots + gates (Group 1800
HumanAttention + workflow domains). Distinct semantic authorities. No overlap.

### 17.4 paStore.messages vs assistantApi conversation fetch (ASYMMETRY, NOT DUPLICATE)

**Framing.** paStore persists last 50 messages to localStorage (rehydration on mount);
`assistantApi.getConversation()` fetches full history from server (authoritative record).
On dock open, `setActiveConversation` overwrites local messages with server-fetched.

**Asymmetry.** localStorage cache is subset of server truth. If localStorage becomes stale
vs server (e.g., server-side redaction, tool-tickers arrive between reload and fetch), a
brief mismatch is visible until fetch completes.

**Class.** `observation` — not `duplicate`, not `technical_debt`. Documented asymmetry.

### 17.5 Zustand persist keys vs Zustand-managed localStorage (SAME MECHANISM, NO OVERLAP)

**Framing.** `auth-storage`, `navigation-store`, `pa-dock-state` are all Zustand-persist-
managed; they're the sole writers/readers of their own keys. No overlap with 12 direct
localStorage keys (each owned by non-store consumers).

**Duplicate systems verdict: NONE.** One asymmetry observation (§17.4); zero true
duplicates.

## 18. Ownership Gaps

Per playbook §11.2 §18 (canonical question #27).

### 18.1 No CODEOWNERS file (CRITICAL — inherited from S2201 §18.1)

**Precedent.** S2201 §18.1 already established this at HEAD `04ee0964`. Re-verified at HEAD
`8fbf17eb` — no repo-root `CODEOWNERS`; no `.github/CODEOWNERS`. Ownership gap CRITICAL
platform-wide. **Not this doc's finding — inherited.**

### 18.2 authStore ownership gap (cross-arc: Group 2200 render, Group 2400 Auth model)

**Framing.** `authStore` shape (token + user + isAuthenticated + login + logout + setUser)
is frontend render-surface authoring. Session lifecycle (token refresh, cookie strategy,
identity lifecycle, permission floor) is Group 2400 Auth model authority. No written spec
exists that carves the render-model boundary.

**Severity.** MED — no active regression, but future auth-session changes will require both
Groups to touch.

**Class.** `unclear_owner` (per playbook §12 finding types).

### 18.3 bodyStore ownership gap (cross-arc: Group 2200 render, Group 1900 Body Systems)

**Framing.** `bodyStore` shape (vitals, alerts, health) is frontend render; body semantic
authority is Group 1900. `services/bodyGovernance.ts` lives in frontend but enforces
governance rules — Group 1900 owns rule semantics, Group 2200 owns rule invocation site.
Boundary is fuzzy in code.

**Severity.** MED — cross-arc coordination flag.

**Class.** `unclear_owner`.

### 18.4 workspaceStore ownership gap (cross-arc: Group 2200 render, Group 2600 PA behavior)

**Framing.** `workspaceStore.activeWorkspace` is frontend render; whether workspace context
should persist across session is a Group 2600 PA behavioral decision (per §14 F5 + §15.3).
No written spec.

**Severity.** MED — active F5 F2 refresh-loss hazard.

**Class.** `unclear_owner`.

### 18.5 assistantContextStore ownership gap (cross-arc: Group 2200 render, Group 2600 PA behavior)

**Framing.** `focusedEntity` shape (`{type, id, title}`) is frontend render; whether Rigby
should treat focus as session-scoped or ephemeral is Group 2600 PA behavioral. No spec.

**Severity.** LOW — user-recoverable.

**Class.** `unclear_owner`.

### 18.6 Session 968 X-UI-Scope ring buffer ownership gap (dev-only)

**Framing.** Client-side request-log ring buffer at `api.ts:3968-4051` is frontend
dev-tooling render; backend X-UI-Scope filter is Group 1700 Observability. Boundary is
clear per-side, but dev-tooling coordination decisions (e.g., synchronize scope taxonomies
across sides) has no owner.

**Severity.** LOW — dev-only surface.

**Class.** `unclear_owner`.

### 18.7 Storage-key naming convention ownership gap

**Framing.** No convention owner for kebab-vs-snake-vs-camel case, no owner for a shared
`storageKeys.ts` registry. Class gap.

**Severity.** LOW — style-only.

**Class.** `unclear_owner`.

**Ownership gap severity summary:** 1 CRITICAL inherited (§18.1 CODEOWNERS) + 3 MED
cross-arc (§18.2 + §18.3 + §18.4) + 3 LOW (§18.5 + §18.6 + §18.7).

## 19. Recommended Future Research

Per playbook §11.2 §19 (canonical question #28). Ranked by architectural uncertainty × risk
× unblocked flows.

### 19.1 R1 — Group 2400 Auth arc: session lifecycle model + localStorage cleanup contract (HIGH priority; active-research track)

**Question.** What is the canonical auth session lifecycle contract? Should logout eagerly
clear all client-side per-user storage (recentEntities, PA state, voice settings, dismissed
pipelines)? Should token refresh be silent-refresh with cookie SameSite/Secure defaults, or
explicit re-login?

**Rationale.** §14 F6 + §14 F8 + §15.9 all trace back to no-cleanup-on-logout. Group 2400
Auth owns the model; this doc records symptoms.

**Two-sided framing (Rigby SIGN cycle 1 Q11 STRENGTHEN 2026-07-05 fold — mirrors S2203 §14
F3 symptom-vs-model contract precedent).**
- **Frontend symptom (Group 2200 scope):** post-logout localStorage records persist as
  null-state; navigationStore.recentEntities not cleared; UI state keys not cleared. These
  are observable at frontend layer and correctable at frontend layer as best-effort
  mitigations.
- **Backend/session model contract (Group 2400 scope):** what is the canonical logout
  contract? Should the server signal browser-side eviction (e.g., Clear-Site-Data header)?
  Should token refresh assume authoritative server-side revocation? These are semantic
  questions Group 2400 Auth arc owns.

**Frontend can MITIGATE (best-effort clear of localStorage on logout); definitive
FIX+CONTRACT lives in Auth lifecycle spec.**

**Owner.** Group 2400 Auth arc (future).

**Blast radius reference.** 15 persistent-state surfaces potentially affected by cleanup
contract.

### 19.2 R2 — Group 2600 PA arc: workspace-context resolver behavioral spec + assistantContextStore persistence decision (HIGH priority; active-research track)

**Question.** Should `workspaceStore.activeWorkspace` persist across session? Should
`focusedEntity` persist? Behavioral spec for PA chat context resolution across page reload.

**Rationale.** §14 F5 + §15.3 + §15.4 + §18.4 + §18.5. Active F5 F2 hazard where Rigby
loses workspace context mid-conversation.

**Dependency graph vs R3 (Rigby SIGN cycle 1 Q12 STRENGTHEN 2026-07-05 fold — priority
ordering justification):** R2 is #1 conditional on **R2 being spec'able independently**
of R3. R2 resolver spec uses existing frontend sources (`useWorkspaceStore`,
`useAssistantContextStore`, `document.cookie` sessionid) → no dependency on R3 canonical
User type authoring. R3 (Group 2500 API canonical User + workspace_id contract inclusion)
would upgrade R2's context-payload TYPING but is NOT a prerequisite for R2's persistence
BEHAVIOR spec. Therefore R2 = #1 stands; R3 = #3 (per §19.11 ranking). **If Group 2600 PA
determines that R2 depends on R3 canonical User + workspace_id contract, flip R3 → #1
during S2299 canonical summary.**

**Owner.** Group 2600 PA arc (future).

### 19.3 R3 — Group 2500 API arc: canonical User type + workspace_id contract inclusion (MED priority; batch bundle candidate)

**Question.** Is `workspace_id` canonical at PA chat payload root or inside `context`
object? Do multiple api-modules need canonical User type shared across GlobalPADock
+ CommandCenterPage + workspace tabs?

**Rationale.** §6 dual-inclusion asymmetry + S2203 §14 F4 (0 typed api-modules), the
canonical typing question is Group 2500 API scope.

**Owner.** Group 2500 API arc (future).

### 19.4 R4 — Shared storageKeys registry + typed accessor pattern (MED priority; maintainer-decision batch candidate)

**Question.** Introduce `frontend/src/lib/storageKeys.ts` centralized registry of all 12+
direct localStorage keys + typed accessor helpers? Adopt kebab-case convention as
platform standard?

**Anti-scope guardrail (Rigby SIGN cycle 1 Q16 STRENGTHEN 2026-07-05 fold — prevents R4
implementation ballooning into framework authoring):**

- **R4 = single-file registry (`storageKeys.ts`) + lintable constants.** Enumerates all
  15 persistent keys as named constants; enforces kebab-case via lint rule.
- **R4 is NOT a storage/persistence framework.** No abstraction over Zustand persist. No
  new middleware. No new hooks. No new patterns for how data is stored.
- **R4 is NOT a wrapper API.** No `getLocalStorageJSON<T>(key)` helper is required for
  R4 close (that would be an R4-follow-up or separate T-slot). R4 shipping = constants
  file + lint rule + one migration PR replacing inline strings.

**Rationale.** §14 F3 + §15.2 + §15.5 + §15.6 + §18.7. LOW-MED severity individually;
bundling into a single maintainer-decision batch amortizes review cost.

**Owner.** Group 2200 xx99 §8 T-slot; maintainer-decision batch candidate.

### 19.5 R5 — authStore + navigationStore version + migrate discipline (MED priority; maintainer-decision batch candidate — DEPENDS ON R1 logout semantics)

**Question.** Add `version` + `migrate` to authStore + navigationStore Zustand persist
declarations, following paStore v3 exemplar.

**Rationale.** §14 F1 F2 + §15.1. Silent future schema-drift risk today.

**Coupling (Rigby SIGN cycle 1 Q15 STRENGTHEN 2026-07-05 fold — dependency-tag added):**
R5 is tightly coupled to R6 (logout hygiene) + R1 (Group 2400 Auth session lifecycle
contract). Migration paths for `auth-storage` should account for Group 2400 decisions on
whether logout clears or writes null-state. **Tagged: depends on R1 logout semantics.** If
Group 2400 arc concludes that logout should call `removeItem`, R5's migrate for authStore
becomes simpler (no null-state handling needed). If null-state persists per current
behavior, R5's migrate must handle null-state rehydration cleanly. Bundle with R6 for
maintainer-decision review.

**Owner.** Group 2200 xx99 §8 T-slot; maintainer-decision batch (paired with R1+R6).

### 19.6 R6 — Zustand persist logout hygiene + cross-user cleanup (MED priority; maintainer-decision batch candidate)

**Question.** On logout, should Zustand-persist-managed keys be explicitly
`localStorage.removeItem`-ed? Should navigationStore.clearHistory be called on logout?

**Rationale.** §14 F6 + §14 F8 + §15.9.

**Owner.** Group 2200 xx99 §8 T-slot; entangled with R1 Group 2400 Auth.

### 19.7 R7 — paStore.syncUser field-completeness sweep (LOW priority; maintainer-decision batch candidate)

**Question.** Extend syncUser field-list to include activeTool/recentTool/seenSeqs/
agentCompletionQueue/seenCompletions.

**Rationale.** §14 F7 + §15.8. LOW severity.

**Owner.** Group 2200 xx99 §8 T-slot.

### 19.8 R8 — Cross-tab sync mechanism (LOW-MED priority; post-arc T-slot)

**Question.** Install BroadcastChannel or storage-event listener for multi-tab UX
consistency? Depends on Group 2200 UX posture on multi-tab expectation.

**Rationale.** §10.3 + §15.7.

**Owner.** Group 2200 post-arc T-slot; conditional on multi-tab UX posture.

### 19.9 R9 — Betting session-scoped state adoption (LOW priority; conditional on UX spec)

**Question.** Implement S1505 §15.3 remediation options (URL params for tab state +
localStorage for filter state + Zustand slice for BettingPage-scoped persistence)?

**Rationale.** §13.2 Betting is EXPERIMENTAL-BY-DESIGN per S1505 §14.10 baseline; only
elevate if multi-session betting UX becomes a product requirement.

**Owner.** Group 2200 post-arc T-slot; conditional on multi-session UX spec.

### 19.10 R10 — Long-running: state-shape schema testing (LOW-MED priority; post-arc)

**Question.** Introduce runtime schema validation (zod / io-ts / custom) on Zustand
rehydration to catch shape-drift regressions before they render to UI?

**Rationale.** §15.1 systematic mitigation; complements version + migrate discipline.

**Owner.** Post-arc T-slot; low priority.

### 19.11 R-ranking summary (arc-cascade)

| Rank | Item | Priority | Owner | Track type |
|---|---|---|---|---|
| 1 | R1 Group 2400 Auth session lifecycle + cleanup contract | HIGH | Group 2400 Auth | active-research |
| 2 | R2 Group 2600 PA workspace-context resolver spec | HIGH | Group 2600 PA | active-research |
| 3 | R3 Group 2500 API canonical User type + workspace_id contract | MED | Group 2500 API | active-research |
| 4 | R4 Shared storageKeys registry | MED | xx99 §8 | maintainer-decision batch |
| 5 | R5 authStore + navigationStore version+migrate | MED | xx99 §8 | maintainer-decision batch |
| 6 | R6 Zustand persist logout hygiene | MED | xx99 §8 | maintainer-decision batch (paired with R1) |
| 7 | R7 paStore.syncUser field-completeness | LOW | xx99 §8 | maintainer-decision batch |
| 8 | R8 Cross-tab sync mechanism | LOW-MED | Post-arc T-slot | conditional |
| 9 | R9 Betting state persistence adoption | LOW | Post-arc T-slot | conditional |
| 10 | R10 Runtime schema validation | LOW-MED | Post-arc T-slot | long-running |

## 20. Appendix

### 20.1 Files inspected

**Zustand stores (7 files):**
- `frontend/src/stores/authStore.ts` (52 LOC)
- `frontend/src/stores/navigationStore.ts` (142 LOC)
- `frontend/src/stores/paStore.ts` (449 LOC)
- `frontend/src/stores/workspaceStore.ts` (27 LOC)
- `frontend/src/stores/assistantContextStore.ts` (28 LOC)
- `frontend/src/stores/bodyStore.ts` (318 LOC)
- `frontend/src/stores/unifiedStore.ts` (426 LOC)

**Direct localStorage caller files (9 files):**
- `frontend/src/pages/CommandCenterPage.tsx` (3 keys: `assistant-voice-settings`,
  `cc_dashboard_collapsed`, `cc_chat_focus_mode`)
- `frontend/src/pages/WorkspaceDashboardPage.tsx` (1 key: `pipeline_dismissed_${workspaceId}`
  parameterized)
- `frontend/src/components/DemoPipelineCard.tsx` (1 key: `demo-pipeline-dismissed`)
- `frontend/src/hooks/useFocusMode.ts` (1 key: `cockpit-focus-mode`)
- `frontend/src/components/layout/Sidebar.tsx` (2 keys: `sidebar-collapsed`,
  `sidebar-reference-open`)
- `frontend/src/components/PanelDebugDrawer.tsx` (1 key: `showDebugPanels`)
- `frontend/src/pages/workspace/tabs/DeliverablesTab.tsx` (1 key: `deliverables_view_mode`)
- `frontend/src/components/cockpit/CockpitSidebar.tsx` (1 key: `cockpit-sidebar-collapsed`)
- `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx` (1 key: `podcast_voice_profile_id`)

**Cross-store integration files:**
- `frontend/src/components/GlobalPADock.tsx` (reads useWorkspaceStore + usePAStore +
  useAssistantContextStore)
- `frontend/src/services/bodyGovernance.ts` (reads useBodyStore.getState() from services
  layer)
- `frontend/src/components/GlobalAlertBanner.tsx` (reads useBodyStore for alerts render)
- `frontend/src/lib/api.ts:29` (reads useAuthStore.getState() from axios interceptor per
  S2203 §16.1)
- `frontend/src/components/EntityLink.tsx` + `frontend/src/components/Breadcrumb.tsx` (read
  useNavigationStore selectors — verifier-loop corrected Explore 5 DEAD claim)
- `frontend/src/App.tsx:49` (ProtectedRoute wrapper calls paStore.syncUser on user change)
- `frontend/src/pages/workspace/tabs/HomeTab.tsx` + `WorkTab.tsx` + `DeliverablesTab.tsx`
  (set focusedEntity + setCurrentInput on entity click)

**Reference files:**
- `frontend/src/main.tsx:8-16` (React Query defaultOptions)
- `frontend/src/lib/api.ts:3968-4051` (Session 968 X-UI-Scope request-log ring buffer)
- `frontend/src/App.tsx` (route wiring, ProtectedRoute)
- `frontend/src/pages/BettingPage.tsx` (verified in-memory state only, no localStorage per
  S1505 §14.10 baseline)

**Docs consulted:**
- `docs/topics/frontend.md` (stale-warned; §PA Integration + §Page Telemetry + §Workspace
  Architecture rows)
- `docs/PLATFORM_INVENTORY.md:30` (§Frontend row headline)
- `docs/research/domains/frontend/2200_frontend_domain_scoping.md` (parent §5 Child D +
  §lens + §7 anti-scope + §7.1 render-authority handoff flags)
- `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md`
  §5 (7-store baseline) + §14 F5 (legacyTabMapping state-adjacent) + §18.1 (CODEOWNERS
  gap)
- `docs/research/domains/frontend/2202_frontend_websocket_consumer_ui_render_hint_envelope_audit.md`
  §17 T6 (PA WS+polling parallel)
- `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md`
  §14 F3 (silent-401) + §16.1 (authStore-in-api.ts INTENTIONAL) + §17 (cross-cutters)
- `docs/research/domains/sports/1505_sports_frontend_surface_audit.md` §14.10 + §15.3
  (single-route zero-persistence + remediation options)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section child-audit template + §13
  six-parallel-Explore-sub-agent template + §14 verifier-loop rule + §15 SIGN cycle policy

### 20.2 Grep patterns used

```
# Persistent-state inventory grep pass
rg -n 'localStorage\.setItem|localStorage\.getItem|localStorage\.removeItem|localStorage\.clear' frontend/src --type ts --type tsx
rg -n 'sessionStorage\.|document\.cookie' frontend/src --type ts --type tsx
rg -n 'indexedDB|IndexedDB|idb' frontend/src --type ts --type tsx
rg -n 'STORAGE_KEY|VOICE_SETTINGS_KEY|DEV_KEY' frontend/src --type ts --type tsx

# Zustand persist middleware inspection
rg -n 'persist\(|createJSONStorage|partialize|migrate' frontend/src/stores --type ts

# Zustand store consumer maps (per store)
rg -n 'useAuthStore' frontend/src --type ts --type tsx
rg -n 'useNavigationStore|useNavigationContext|useNavigationHistory|useRecentEntities' frontend/src --type ts --type tsx
rg -n 'usePAStore|usePAMessages|useIsDockOpen|usePARecentTool|usePAActiveTool' frontend/src --type ts --type tsx
rg -n 'useWorkspaceStore|activeWorkspace' frontend/src --type ts --type tsx
rg -n 'useAssistantContextStore|focusedEntity' frontend/src --type ts --type tsx
rg -n 'useBodyStore' frontend/src --type ts --type tsx
rg -n 'useUnifiedStore|useUnifiedAttention|useUnifiedOpportunities|useUnifiedPilots|useUnifiedGates|useTopOpportunities|useRunningPilotsCount|usePendingDecisionsCount' frontend/src --type ts --type tsx

# Cross-tab sync check
rg -n "addEventListener\('storage'|BroadcastChannel" frontend/src --type ts --type tsx

# React Query cache config
rg -n 'QueryClient|persistQueryClient' frontend/src --type ts --type tsx
```

### 20.3 Unresolved unknowns

- **U1 — RESOLVED** (Rigby SIGN cycle 1 Q5 STRENGTHEN + close-tighten 2026-07-05 fold).
  Zustand persist middleware auto-clear behavior on logout was UNKNOWN pre-verification;
  RESOLVED via package.json dependency scan (`"zustand": "^4.4.0"`) + persist source-call-
  chain trace: `set({token:null, user:null, isAuthenticated:false})` → `partialize(nextState)`
  → `JSON.stringify(partializedState)` → `storage.setItem(name, serialized)` — does NOT
  call `storage.removeItem`. Rehydration reads null-state; ProtectedRoute `isAuthenticated:
  false` gates. **Functionally equivalent to storage deletion at auth-gate boundary; NOT
  storage deletion at localStorage-record boundary.** §14 F6 framing "functional clear via
  null-state" is CORRECT per source verification; framing "IMPLICIT auto-clear" is CORRECT
  per Zustand default behavior.
- **U2** — Whether `pipeline_dismissed_${workspaceId}` unbounded growth is a real footprint
  concern depends on peak workspace-per-user rate. Not verified.
- **U3** — Whether `activeTool` / `recentTool` / `seenSeqs` bleed across users during rapid
  user-switch (no page reload) actually renders visibly is a UX regression question, not
  verified at Child D scope. Recorded in §14 F7 + §15.8.
- **U4** — Session 968 X-UI-Scope request-log ring buffer is documented as dev-only via
  `showDebugPanels` localStorage; whether the ring buffer allocation is bypassed in
  production builds via tree-shaking / DCE has not been verified. Recorded in §7.5.

### 20.4 Conflicts between sources

- **C1** — Sub-agent 5 (Explore 5) classified `navigationStore` as DEAD with 0 consumers;
  verifier-loop grep found 2 real consumers (EntityLink.tsx + Breadcrumb.tsx). Resolved:
  §5 corrected + §14 F4 verifier-loop artifact record + §20.5 verifier-loop
  correction 1.
- **C2** — Sub-agent 5 classified `unifiedStore` as "global layout only" with 0 page
  consumers; verifier-loop grep found `CommandCenterPage.tsx` uses it. Resolved: §5
  corrected + §20.5 verifier-loop correction 2.
- **C3** — Sub-agent 1 (Explore 1) claimed "15 direct localStorage keys" (matching parent
  memo). Recount from raw grep output: **12 direct keys** (+ 3 Zustand persist keys = 15
  total persistent surfaces). Parent memo carried an off-by-3 error; sub-agents inherited.
  Resolved: §1 headline + §5.1 registry + §14 F1 + §20.5 verifier-loop correction 3.
- **C4** — Sub-agent 3 (Explore 3) listed 12 direct-caller keys in the collision matrix
  (correct), while other sub-agents said 15 direct (incorrect). Explore 3 was correct;
  others inherited parent-memo error. Resolved same as C3.
- **C5** — Sub-agent 5's F2 verdict was "SURFACE-LOCAL + DOMAIN-SPECIFIC HYBRID" (correct)
  but based on partially-erroneous consumer counts (DEAD navigationStore, no-CC-consumer
  unifiedStore). Verdict verified independently against corrected §5.1 data; verdict
  survives correction. Recorded in §1 headline + §5.2 per-surface rollup.

### 20.5 Verifier-loop corrections

Per playbook §14 "trust but verify" rule.

**Correction 1** — Explore 5 mis-classification of `navigationStore` as DEAD reversed.
Direct grep at `frontend/src/` for `useNavigationStore|useNavigationContext|useNavigationHistory|useRecentEntities`
returned 3 files: navigationStore.ts (self), EntityLink.tsx, Breadcrumb.tsx. Real consumers
= 2. Classification corrected to WORKING (§13.1 store table) + not-DEAD (§14 F4).

**Correction 2** — Explore 5 mis-statement of `unifiedStore` no-page-consumer claim
reversed. Direct grep for `useUnifiedStore` + selectors returned 4 files including
CommandCenterPage.tsx (27 total occurrences). Consumer map corrected in §5.1.

**Correction 3** — Parent-memo error of "15 direct localStorage keys" carried to
sub-agents; recount from raw initial grep output yields **12 direct + 3 Zustand = 15 total**.
Corrected in §1 headline + §5.1 registry + §14 F1.

**Correction 4** — Sub-agent 2 (Explore 2) claimed authStore.ts + navigationStore.ts had
no `version` (correct) but also implied paStore has "incomplete migrate covering only some
persisted fields" — a subtle framing question. Verifier-loop reading paStore.ts:395-431:
migrate is complete for the fields it needs to migrate (v1→v2 adds new fields at initial
values; v2→v3 wipes user-scoped conversation state). Tool-ticker + agent-completion state
are NOT in partialize (correctly ephemeral); therefore they don't need migration entries.
Explore 2's "incomplete migrate" framing is misleading. Correct framing: migrate is
complete-for-partialize-scope. Recorded in §15.1.

**Rigby SIGN cycle 1 fold notes** (via dedicated fresh SIGN pin `pa-62c03c4844454e99`
retired at cycle close via `session_tool.retire` updated_count=6, retired=true,
previously_active=true — 4 batches × 5 questions = **20 folds landed pre-commit-gate**;
overall verdict SIGN-with-edits at HIGH confidence; cycle 2 not required):

- **Batch 1 framing + severity (Q1-Q5):**
  - Q1 CLEAN — SURFACE-LOCAL + DOMAIN-SPECIFIC HYBRID F2 verdict consistent; §10.3 zero-
    cross-tab-sync doesn't reframe to SYSTEMIC.
  - Q2 STRENGTHEN — MED-HIGH severity retained; added "borderline HIGH conditional on
    Group 2600 PA correctness" hedge (§1 headline F5 + §14 F5 + §15.3).
  - Q3 CLEAN — 12 direct + 3 Zustand = 15 total reconciled correctly; no lingering
    15-vs-12 mis-cite.
  - Q4 STRENGTHEN — Per-key rubric formalized in §15.2 as 4-criteria table
    (C1 constant / C2 typed / C3 fallback / C4 template).
  - Q5 STRENGTHEN + close-tighten — Zustand ^4.4.0 verified via package.json; persist
    call chain traced; §14 F6 tightened to distinguish "functional clear via null-state"
    vs "storage deletion"; §20.3 U1 flipped RESOLVED.
- **Batch 2 falsifier + per-surface (Q6-Q10):**
  - Q6 STRENGTHEN — §1 headline denominator language rephrased "14/15 persisted keys
    outside /betting; betting 0/15" (no percentage-adoption framing).
  - Q7 STRENGTHEN — §5.2 heading + prose replaced "adoption rate" with "key-level
    incidence by surface"; cross-surface averaging explicitly forbidden unless normalized.
  - Q8 REJECT — STABLE+DEEP → WORKING+MODERATE downgrade proposal deferred to S2299
    canonical summary rollup across all 4 children per §13.3 hedge.
  - Q9 STRENGTHEN — §14.0 verification-scope statement added: 2 source greps + wrapper
    grep (idb, dexie, localforage) + package.json dependency scan (zustand ^4.4.0, no
    IDB wrappers) + dynamic-import grep.
  - Q10 CLEAN — §5.2 explicit "sampling waived per full-registry-fit; inspection =
    complete enumeration" language added.
- **Batch 3 cross-arc + POSTURE (Q11-Q15):**
  - Q11 STRENGTHEN — §19.1 R1 two-sided framing added (FE symptom + BE session/model
    contract) mirroring S2203 §14 F3 pattern.
  - Q12 STRENGTHEN — §19.2 R2 dependency-graph justification added: R2 = #1 conditional
    on independence from R3; if R2 depends on R3 canonical User type, flip during S2299.
  - Q13 CLEAN — §14 F5 severity framing appropriately hedged; noted at end of finding
    per Q13 clarifier "could be design choice; disposition owned by Group 2600".
  - Q14 STRENGTHEN — §16.1 explicit "unchanged-at-HEAD-8fbf17eb" verifier-loop citation
    with file:line evidence.
  - Q15 STRENGTHEN — §19.5 R5 tagged "depends on R1 logout semantics"; bundle with R6
    for maintainer-decision review.
- **Batch 4 anti-scope + verdict (Q16-Q20):**
  - Q16 STRENGTHEN — §19.4 R4 explicit anti-scope guardrail added: "single-file registry
    + lintable constants; NOT a storage/persistence framework; NOT a wrapper API".
  - Q17 STRENGTHEN — §20.6 Path D sub-split into D1 workspace persistence policy + D2
    focused-entity persistence, both Group 2600 PA-owned.
  - Q18 CLEAN — R4/R5/R6/R7 maintainer-decision batch bundling correct.
  - Q19 CLEAN — CODIFICATION-EXTENSION framing correctly hedged 14→15 conditional
    pending Chris S2299 ratification per S2202 Q19 + S2203 Q19 precedent.
  - Q20 SIGN-with-edits at HIGH confidence + Cycle 2 NOT required (all folds landable
    pre-commit).

### 20.6 POSTURE-DECISION evidence plan for xx99

Per S2200 §5 Child D delegation. This audit's Child D-slice preliminary evidence toward
xx99 POSTURE-DECISION on whether per-surface persistence discipline should be introduced
as a frontend convention or handled at backend/PA layer:

**Preliminary evidence lean: naming-registry + versioning-hygiene convention, NOT a
whole-frontend persistence framework.**

**Path A: DECLARE + PUBLISH naming convention (LOW-cost, HIGH-visibility).**
- Add `frontend/src/lib/storageKeys.ts` centralized registry with typed accessor helpers.
- Enforce kebab-case for new keys (6 of 12 already comply).
- Adds a lint-enforceable single source of truth.

**Path B: EXTEND version + migrate discipline to authStore + navigationStore
(LOW-cost, LOW-visibility).**
- Fold `version: 1` + a stub `migrate` into authStore + navigationStore Zustand persist.
- Prevents future silent-drift; no user-visible change today.

**Path C: PERSISTENCE-FRAMEWORK AUTHORING (HIGH-cost, HIGH-visibility) — REJECTED at this
scope.**
- Zustand-with-full-persistence, jotai, react-query cache-persist migration is
  OUT-OF-SCOPE per §7 anti-scope.

**Path D (Rigby SIGN cycle 1 Q17 STRENGTHEN 2026-07-05 fold — sub-split D1/D2 for
disposition clarity; both Group 2600 PA-owned):**

- **Path D1: workspace persistence policy** — should `workspaceStore.activeWorkspace`
  persist (session-scoped Zustand persist with partialize + version + migrate) or should
  workspace context re-resolve via a fresh resolver (route-derived, user-preferred,
  server-round-tripped)? Live F5 F2 hazard site.

- **Path D2: focused-entity persistence** — should `assistantContextStore.focusedEntity`
  persist across session? Workspace-scoped keys? TTL? Ephemeral by design?

Both D1 + D2 deferred to Group 2600 PA arc close; frontend documents symptom + surface
only per §7 anti-scope + §7.1 render/behavior split.

**Escape hatch preserved:** Any component may still write ad-hoc localStorage keys during
initial iteration; convention adoption is aspirational not enforcing.

**Commit-gate confidence:** HIGH on committed action (path A + path B naming + versioning
recommendations); MED on Path D (Group 2600 owns behavioral spec + persistence contract for
workspaceStore + assistantContextStore); the final Path shape is Chris-and-Group-2600-
ratifiable.

**Final POSTURE-DECISION resolution deferred to S2299 canonical summary** after all 4 child
audits close.

### 20.7 Rigby SIGN cycle 1 Q1-Q20 candidates (pre-commit)

*Batch 1 (Q1-Q5): Framing + severity calibration*
- **Q1** — Is the SURFACE-LOCAL + DOMAIN-SPECIFIC HYBRID F2 verdict correct, or is there a
  hidden systemic pattern (e.g., zero-cross-tab-sync SYSTEMIC) that reframes to SYSTEMIC?
- **Q2** — Is §14 F5 (`workspaceStore.activeWorkspace` in-memory-only cross-surface impact)
  correctly severity-classified MED-HIGH, or should it be HIGH per PA-context-loss + 144
  consumer sites amplification?
- **Q3** — Is the 12 direct + 3 Zustand = 15 total count reconciled correctly (per §20.5
  Correction 3), or does the doc still mis-cite anywhere?
- **Q4** — Is the "6 DECLARED / 6 ACCIDENTAL" per-key discipline classification (§14.2 +
  §15.2) rigorous, or does it need per-key criteria fold-in?
- **Q5** — Is the §14 F6 "Zustand persist auto-clear behavior IMPLICIT" framing accurate,
  or should verifier-loop actually read Zustand 4.x source?

*Batch 2 (Q6-Q10): Falsifier + per-surface rollup*
- **Q6** — Does the F2 falsifier framework (§1 + §5.2) survive against the "13.4% workspace
  persistence-adoption" per-surface breakdown, or does the arithmetic misclassify?
- **Q7** — Is the per-surface reporting constraint (workspace / betting / command-center /
  PA) applied correctly across §5.2 + §13.2 without cross-surface averaging?
- **Q8** — Is the S2201 F1 32-domain row 18 pressure-test framing (§13.3) — proposing
  downgrade from STABLE+DEEP to WORKING+MODERATE — correctly evidenced?
- **Q9** — Is the "0 sessionStorage + 0 IndexedDB" claim (§1 + §14.1) verified independently,
  or inherited from a single grep pass?
- **Q10** — Is the sampling-strategy application (per S2200 §5 Q10 STRENGTHEN fold)
  transparent — did this audit ship complete registry (yes) + apply documented sampling
  (no, because 15 total surfaces fit in-runtime)?

*Batch 3 (Q11-Q15): Cross-arc + POSTURE*
- **Q11** — Is R1 (Group 2400 Auth session lifecycle + cleanup contract) correctly scoped
  as Group 2400-owned, or does R1's frontend-symptom vs BE-model split need sharper
  language?
- **Q12** — Is R2 (Group 2600 PA workspace-context resolver spec) correctly the highest-
  priority cross-arc handoff, or should R3 (Group 2500 API canonical User) rank higher?
- **Q13** — Is §14 F5 F2 hazard (workspaceStore in-memory refresh-loss) an active
  regression or a documented design choice (Group 2600 arc question) — should the framing
  hedge on "regression" vs "design"?
- **Q14** — Is the §16.1 pre-existing S2203 verification (authStore in api.ts INTENTIONAL)
  correctly re-cited without re-re-verifying at HEAD `8fbf17eb`?
- **Q15** — Does §19.5 R5 + §19.6 R6 (Zustand persist version + logout hygiene) belong to
  a maintainer-decision batch or to R1 Group 2400 Auth arc-owned batch?

*Batch 4 (Q16-Q20): Anti-scope + verdict*
- **Q16** — Are §7 anti-scope declarations (no framework authoring, no auth model, no PA
  behavior spec, no BE session design) tight enough to prevent scope leakage into R-item
  execution?
- **Q17** — Is the §20.6 POSTURE-DECISION Path A + Path B + Path D triad well-formed
  without over-committing to Path D (deferred to Group 2600 PA)?
- **Q18** — Does the §19 meta-recommendation post-arc maintainer-decision batch bundling
  R4/R5/R6/R7 correctly separate active-research (R1/R2/R3/R8) from bundleable maintainer
  work?
- **Q19** — Does the CODIFICATION extension framing (S2204 = FIFTEENTH-consecutive §11.2
  application) correctly hedge — pending Chris ratification at S2299 xx99 close per
  S2202 Q19 + S2203 Q19 precedent — without over-claiming?
- **Q20** — Overall child audit verdict: SIGN-clean / SIGN-with-edits / REJECT? If
  SIGN-with-edits, minimum edits to land before commit-gate?

### 20.8 Frontmatter provenance

**Arc pin lineage.** `pa-f7fd5016600f4513` (Group 2200 Frontend — TENTH formal arc pin under
Research OS; preserved across S2200 → S2201 → S2202 → S2203 → **S2204** per playbook §16
arc-standard behavior). Retirement at S2299 close per playbook §16 arc-close discipline.

**Meta-methodology milestone state at S2204 open (unchanged from S2203 close):**
- MC-1 through MC-5 all CODIFICATION-CONFIRMED
- MC-4 (parent-with-4-children arc-pin routing) — S2204 EXTENDS consecutive-count 14 → 15
  at Group 2200 close per §11.2 template FIFTEENTH-consecutive application; codification
  framing CONDITIONAL pending Chris ratification at S2299 xx99 close per S2202 Q19 + S2203
  Q19 precedent
- MC-6 CODIFICATION-READY (awaiting future xx99 promotion)
- MC-7 through MC-10 CANDIDATES (awaiting second-arc trigger per §20 two-triggers rule)

**Session context at open.**
- Repo state: `main @ 8fbf17eb` (S2203 close commit `docs(session-2203): Group 2200 Cat C
  Frontend↔Backend API Contract + Boundary Discipline Audit (#2904)`); working tree clean
  except `.claude/scratch/` untracked; no uncommitted changes pre-draft.
- Prior handoff: `docs/handoffs/SESSION_2203_FRONTEND_API_CONTRACT_BOUNDARY_DISCIPLINE_AUDIT.md`.
- Next handoff (this session close): `docs/handoffs/SESSION_2204_FRONTEND_SESSION_STATE_PERSISTENCE_DISCIPLINE_AUDIT.md`.
- CLAUDE.md subsystem docs pointer for Frontend: `docs/topics/frontend.md` (stale-warned per
  DOC-POINTER-V1 banner).
- 32-domain map row: 18 (Frontend / Workspace UI) — maturity STABLE + depth DEEP posture,
  active pressure-test open across S2201 + S2202 + S2203 + **this doc**; final resolution
  deferred to S2299 canonical summary.

**Arc progress at S2204 close:**
S2200 parent scoping (shipped) → S2201 P1 Child A Routes+Pages+Layouts+Components (shipped)
→ S2202 P2 Child B WebSocket Consumer+Envelope (shipped) → S2203 P3 Child C API Contract+
Boundary (shipped) → **S2204 P4 Child D Session-scoped State Management+Persistence
Discipline (this doc, shipping)** → S2299 xx99 Canonical Summary (next). **Runtime target
6 sessions: 5 of 6 shipped**.

---
