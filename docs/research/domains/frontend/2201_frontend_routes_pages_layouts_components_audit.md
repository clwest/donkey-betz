---
title: "Group 2200 — Cat A — Routes + Pages + Layouts + Component Patterns Audit (S2201 P1)"
status: active (post-Rigby SIGN cycle 1 SIGN-with-edits at HIGH confidence via dedicated SIGN pin pa-8d60e999e01c40e4 retired via session_tool.retire updated_count=5; 19 folds landed pre-commit-gate; Chris "agree all" 2026-07-05 ratified 5-item close card wholesale — 19 folds accepted + POSTURE-DECISION WORKING+MEDIUM committed + Child E via path-b fold-into-S2299 xx99 + arc-cascade sequence + commit-gate approval)
session: 2201
child_slot: P1_cat_a
domain_slug: frontend
research_group: 2200
mission_type: child_audit
date: 2026-07-05
arc_pin: pa-f7fd5016600f4513
head_commit_at_open: 04ee0964
authority: |
  P1 child audit under Group 2200 Frontend (Contract-Surface arc). Scope
  inherited verbatim from parent scoping §5 Child A block
  (`2200_frontend_domain_scoping.md`) + §3 Candidate subdomain A + parent
  §7.1 leak-vector guardrails.

  This doc is RESEARCH AUDIT only. It captures a **static snapshot** of the
  frontend route + page + layout + component surface at HEAD `04ee0964` on
  `main` (2026-07-05, LOCAL environment). It enumerates the routes in
  `frontend/src/App.tsx` (Explore Agent 1 counted 59 distinct `<Route>`
  entries vs the PLATFORM_INVENTORY §Frontend claim of 61 — flagged for
  reconciliation at xx99), maps each to its owned page component + layout
  parent + auth-wrapper posture + primary data-source contract,
  identifies god-components (12 pages >1,000 LOC; 6 pages >1,500 LOC),
  audits legacy tab / normalization deletion candidates, and delivers
  POSTURE-DECISION evidence toward the "STABLE + DEEP" 32-domain row 18
  pressure test.

  Explicit non-scope per parent §7 + §7.1 leak-vector guardrails:
  - Does NOT design or refactor any god-component (§7 "No god-component
    refactor"); a subdivision cost estimate is in-scope, subdivision
    execution is not.
  - Does NOT enumerate WebSocket consumer surface — that IS Child B
    (S2202) scope. Page-level `useWebSocket` presence is noted only
    insofar as it feeds F2 falsifier criterion (Agent 5 §14.5).
  - Does NOT design an API contract source-of-truth — that IS Child C
    (S2203) scope; observed API calls at page-level are inventoried
    only insofar as they inform route-ownership contracts.
  - Does NOT audit persistent-state discipline — that IS Child D
    (S2204) scope; page-level `localStorage`/`sessionStorage` presence
    is noted for F1 evidence only.
  - Does NOT propose auth-session model changes (Group 2400 guardrail);
    auth-wrapper hygiene is symptomatic + descriptive only.
  - Does NOT propose PA behavioral spec for GlobalPADock (Group 2600
    guardrail); PA UI structure is treated as a render surface only.
  - Does NOT audit the mobile app (Group 2300).

  Load-bearing inheritance chain re-attested at S2201 open:
  - PLATFORM_INVENTORY §Frontend row (61 routes, 5 workspace tabs, 9
    betting tabs) — verified 2026-07-02 against runtime; **route-count
    delta flagged: audit count = 59, PLATFORM_INVENTORY = 61 — see §14
    drift row + §20.5 conflict entry.**
  - S1505 §14.1 MOCK-DATA-CONSUMER `/ws/dbao/` + §14.2 DEAD-RENDER-PATH
    `markets`/`bankroll` + §14.3 AUTH-DRIFT + §14.5 zero-WS-subscription
    + §15.4 3,023-line `BettingPage.tsx` god-component — Child A's
    4-falsifier test (S2200 §2.4) returned **SYSTEMIC verdict** (F1 fails
    ~65% violation rate outside sports; F2 partial surface-local; F3
    passes domain-specific for Signal Engine; F4 fails — non-betting
    surfaces show identical patterns). See §14.1-§14.4 + §20.6.
  - S2200 §5 Child A per-surface reporting constraint (Q1 STRENGTHEN
    fold) — findings reported per major surface (workspace / betting /
    command-center / PA / other) in addition to axis-level rollup.
  - S2200 §5 Child A timebox + sampling rule (Q10 STRENGTHEN fold) —
    1-session timebox honored via **6 parallel Explore sub-agents** per
    playbook §13 (Agents 1-6 dispatched in single batch 2026-07-05).
  - S2200 §5 Child A Child E spin-out trigger (Q4 STRENGTHEN fold) —
    trigger **MET**: 6 pages >1,500 LOC across ≥3 major surfaces
    (standalone / command-center / betting). See §15.2 + §19 R3.
    Spin-out decision Chris-gated at S2201 close.
verifier_loop: |
  Pre-draft verifier-loop (per playbook §14 + parent §5 SESSION READY
  CHECK) executed 2026-07-05 at HEAD `04ee0964`:
  1. Route count reconciliation — Explore Agent 1 counted 59 distinct
     `<Route path=` entries in App.tsx (App.tsx:64-149) vs
     PLATFORM_INVENTORY §Frontend row claim of 61. Delta hypothesis:
     inventory generator may count nested/parent Route wrappers
     differently. Flagged as §14 drift + §20.5 conflict; recommend
     inventory regen + xx99 reconciliation.
  2. `frontend/src/pages/workspace/types.ts:9-14` — 5 primary tabs
     enumerated (home, work, build, intelligence, system); confirms
     PLATFORM_INVENTORY claim.
  3. `wc -l` sweep of `frontend/src/pages/*.tsx` — 6 pages >1,500 LOC
     confirmed by Agent 2 with god-component metrics: AgentsPage 4695
     (24 useQuery+useMutation / 26 useState / 24+ inline TS
     interfaces), IntelligencePage 3546 (23/10/12+), BettingPage 3023
     (22/18/11+ vs S1505 §15.4 baseline of 14/17/11), CommandCenterPage
     2551 (28/19/12+), VideoStudioPage 1930 (20/38/6+),
     StockIntelligencePage 1575 (10/16/3+). 12 pages >1,000 LOC total.
  4. `frontend/src/lib/api.ts + apiClient.ts + cockpitApi.ts` —
     API-module layer at `frontend/src/lib/` (Agent 6 verified 93 api
     definitions in api.ts; zero exported TypeScript types — deferred
     to Child C S2203).
  5. `frontend/src/stores/*` — 7 Zustand stores (assistantContextStore,
     authStore, bodyStore, navigationStore, paStore, unifiedStore,
     workspaceStore). Deferred to Child D S2204.
  6. `frontend/src/hooks/*` — 5 hooks (cockpitQueries, useFocusMode,
     usePageTracking, usePanelStatus, useWebSocket). `usePageTracking`
     invoked in Layout:14 (Agent 3); `useWebSocket` used by 7 pages
     (Agent 5 for F2 evidence).
  7. Repo state at S2201 open: `main @ 04ee0964`; working tree clean
     except `.claude/scratch/` untracked.
  8. Arc pin `pa-f7fd5016600f4513` verified ACTIVE via
     `platform_config_tool overview` (service_context: local;
     health_check score=100 recommendation=continue) at S2201 open.
  9. `normalizeWorkspaceTab()` function NOT FOUND (Agent 4) — parent
     scoping §5 Child A deliverable (e) referenced it; confirmed
     already superseded by inline `legacyTabMapping` object in
     WorkspacePageNew.tsx:159-196 + `resolveFromUrl` at
     WorkspacePageNew.tsx:791-816. §14 drift entry.
  10. Test coverage sweep — 0 `*.test.tsx` or `*.spec.tsx` files under
      `frontend/src/pages/**` (Agent 6). §15.1 CRITICAL debt.
  11. CODEOWNERS existence check — no file at repo root or
      `.github/CODEOWNERS` (Agent 6). §18.1 CRITICAL ownership gap.
owner: claude (drafted S2201; Rigby SIGN cycle 1 folds land pre-commit)
---

# Session 2201 — Group 2200 Cat A — Routes + Pages + Layouts + Component Patterns Audit

> **Static snapshot.** This audit captures the frontend route + page + layout
> + component surface at HEAD `04ee0964` on `main` (2026-07-05, LOCAL). It
> is a photograph, not a mechanism explainer. WebSocket consumer surface
> is Child B (S2202). API contract source-of-truth is Child C (S2203).
> State + persistence discipline is Child D (S2204). This document
> delivers what parent §5 Child A required: (a) route ownership map (61
> claimed → 59 counted); (b) god-component inventory (12 pages >1,000
> LOC; 6 pages >1,500 LOC) + subdivision cost estimate + prioritized
> candidate list; (c) layout parent audit + duplication signals; (d)
> auth-wrapper hygiene + drift patterns; (e) legacy tab / normalization
> deletion candidates; (f) POSTURE-DECISION evidence plan §20.6 owed to
> xx99 on the "STABLE + DEEP" (32-domain row 18) contract-level
> pressure test.

## 1. Executive Summary

**Contract-surface posture — one-sentence answer to the Child A slice of
the central lens question:** The frontend at HEAD `04ee0964` is
**structurally healthy at the route + auth-wrapper + layout boundary**
(single `ProtectedRoute` wrapper, single `Layout.tsx`, clean public/
private split, deliberate cockpit consolidation) but **structurally
under-specified at the page-component + consumer-contract boundary** —
no route-ownership map exists, no page ↔ route consumer contract is
declared, and page-component complexity has generalized into 6 confirmed
god-components >1,500 LOC across ≥3 surfaces.

**Central Child A finding — S1505 hypothesis is CONFIRMED SYSTEMIC (with
sampling caveat).** Per the S2200 §2.4 four-falsifier framing, three of
the four criteria resolve against sports-outlier / surface-local /
domain-specific downgrade paths. **F1 evidence — non-betting
violation-index** (Rigby SIGN cycle 1 Q6 STRENGTHEN 2026-07-05 fold —
composite %-rate replaced with per-axis rubric to avoid mixed-denominator
arithmetic): test coverage = 0% of `frontend/src/pages/**` files carry
`*.test.tsx`; god-components = 6 of 38 pages ≥1,500 LOC (16%); state
persistence = 4 of ~80 page-adjacent surfaces use `localStorage`/
`sessionStorage` (~5% adopted); typed API contracts = 0 of 93 api-module
definitions in `frontend/src/lib/api.ts` carry exported TS types (0%
adopted). **F1 fails on 4 of 4 sampled axes** — sports-outlier downgrade
path is closed. **F4 evidence — non-betting surfaces show identical
patterns** in god-components + zero-test + zero-persistence + no-typed-
API (Q8 STRENGTHEN fold — "no evidence found in sampled surfaces" hedge
applied throughout §14-§15; systemic verdict scoped to what the audit
sampled). Only F2 (WebSocket subscription-completeness) resolves as
**PENDING-CHILD-B-CONFIRMATION** — Child A page-level evidence shows
non-sports pages subscribe to WS (CommandCenter, WorkspacePageNew,
AgentsPage, IntelligencePage) while sports registers 3 routes with zero
frontend subscriber (S1505 §14.5), but envelope-conformance rate + full
subscriber matrix is Child B (S2202) scope (Q7 STRENGTHEN fold). Only F3
(zero Signal Engine emission) resolves as domain-specific (backend
architecture concern, not frontend-visible). **S1505 §14 findings
graduate from single-route slice to whole-frontend governance concerns**
— xx99 elevates urgency accordingly.

**Contract-surface acceptance criteria (S2200 §lens block; Child A
scores the 3 criteria in scope):**

| Criterion | Status | Evidence |
|---|---|---|
| 1 — Every route maps to owned page + layout with declared consumer contract | **PARTIAL** (Q9 FOLD 2026-07-05) | Route ownership map DOES exist implicitly in `frontend/src/App.tsx:64-149` (path → component with line refs); this audit's §3 extracts it as a durable artifact for the first time. What is UNMET is the **declared, durable contract source-of-truth** (typed route registry, per-route owner metadata, typed consumer-contract schema). The map is extractable; the contract is not. |
| 5 — Component/page/layout boundaries visible + navigable; no god-component pathologies | **PARTIAL** (Q10 FOLD 2026-07-05) | 6 of 38 pages ≥1,500 LOC (16%); 32 pages below threshold. Contract-surface hardening requires *no* critical-path god-components in the aggregate — so the criterion is violated in aggregate, but per-page discipline is not uniform failure. S1505 §15.4 BettingPage pattern generalizes; Child E spin-out trigger MET. |
| 6 — Failure-mode + boundary behavior standardized + observable | **UNMET** | No error boundaries anywhere; `frontend/src/lib/api.ts:48-56` catches 401 globally only for auth-endpoints; no per-page loading/error-state discipline; S1505 §14.3 silent-401 pattern generalizes (per-arc handoff to Group 2400 Auth for session-model resolution). |

**POSTURE-DECISION §20.6 preliminary evidence toward S1273 32-domain
row 18 "STABLE + DEEP":** **downgrade candidate to WORKING + PARTIAL
(or PARTIAL + LIGHT)**. Route-composition + Layout are STABLE; page
components + component patterns are WORKING; contract discipline is
PARTIAL-to-UNMET. Final POSTURE-DECISION resolution deferred to S2299
canonical summary after S2202-S2204 close, per parent §5 Child A
delegation.

**Five headline findings:**

- **F1 — Route inventory delta (§14.1)** — Audit counts 59 `<Route>`
  entries; PLATFORM_INVENTORY §Frontend row claims 61. Delta hypothesis:
  inventory-generator semantics for "route" differ from Child A's
  distinct `path=` counter (may include nested/parent Route wrappers or
  `Navigate` element instances). **Class: `observation` — inventory
  semantics delta, NOT `drift`** (Rigby SIGN cycle 1 Q1 CLEAN with
  micro-fold — the system has not regressed against a stable spec; the
  two counters define "route" differently). Reconcile at xx99. Severity:
  LOW.
- **F2 — God-component pathology generalizes to 6 pages >1,500 LOC
  across ≥3 top-level product surfaces (§15.2)** — AgentsPage 4,695 LOC
  (Agents/AI surface), IntelligencePage 3,546 LOC (Command-Center),
  BettingPage 3,023 LOC (Betting; S1505 baseline), CommandCenterPage
  2,551 LOC (Command-Center), VideoStudioPage 1,930 LOC (Content-Studio),
  StockIntelligencePage 1,575 LOC (Command-Center). Additional evidence
  (Q12 CLEAN fold — intra-route tab components; supplement not trigger-
  critical): 3 workspace tabs >2,500 LOC (InitiativesTab 3,277,
  ContentStudioTab 3,167, OrchestrationTab 2,985). **Child E spin-out
  trigger MET on page-level alone** per S2200 §5 Q4 STRENGTHEN (≥3
  god-components across ≥2 top-level product surfaces; met at ≥3
  surfaces). Severity: **HIGH baseline; CRITICAL for CommandCenterPage +
  BettingPage** where blast-radius + churn + high-coupling profile
  amplifies risk (Q2 STRENGTHEN — severity scales by blast radius +
  churn + defect history, not by LOC alone).
- **F3 — Zero test coverage across `frontend/src/pages/**` (§15.1)** —
  0 `*.test.tsx` files. Universalizes S1505 §15.1 CRITICAL debt from
  single-route to whole-frontend. **Severity: HIGH baseline; CRITICAL
  for specific surfaces** (payments / auth / billing / betting / ledger-
  like flows — BillingPage, BettingPage, `/portfolio`, `/wager*`
  endpoints, `/api/v1/odds/bankroll*`) where regression-catch-rate risk
  is amplified (Rigby SIGN cycle 1 Q3 STRENGTHEN — CRITICAL platform-
  wide would over-severe a single-operator solo-build context; team-
  throughput-collapse dimension is not load-bearing here).
- **F4 — CODEOWNERS file absent + 22/38 pages lack session-annotation
  ownership trail (§18.1 + §14.4)** — no repo-root `CODEOWNERS`, no
  `.github/CODEOWNERS`. **Severity: HIGH with single-operator caveat**
  (Rigby SIGN cycle 1 Q4 STRENGTHEN — becomes CRITICAL the moment a
  second contributor exists; today it is future-scale hardening debt
  rather than active governance failure). Generalizes S1505 §14.11
  no-CODEOWNERS finding from single-route to whole-frontend.
- **F5 — Legacy sub-tab enum + `legacyTabMapping` object are load-bearing
  backward-compat surface (§14.2)** — 19 legacy sub-tab values in
  `WorkspaceTab` type + 25 mappings in `legacyTabMapping` at
  WorkspacePageNew.tsx:159-196 are RISKY to delete (all still map to
  active primary+sub routes via URL auto-redirect at
  WorkspacePageNew.tsx:791-816). `normalizeWorkspaceTab()` NOT FOUND —
  already superseded, though parent scoping §5 Child A referenced it.
  **Class: `legacy_compatibility_debt` (Rigby SIGN cycle 1 Q5 CLEAN with
  micro-fold — not `drift`; the surface works as intended, but carries
  maintenance burden + hidden coupling + future migration hazard).**
  Severity: MED.

**S1505 4-falsifier verdict:** **SYSTEMIC** — F1 fails (non-betting
violation rate >60% across 5 axes), F4 fails (non-betting surfaces show
identical patterns). Only F2 (WebSocket subscription-completeness)
holds sports-surface-local; only F3 (Signal Engine emission absence)
holds domain-specific. Governance urgency at xx99 elevates
accordingly.

## 2. Domain Purpose

**Q1 — What is this Child A audit for? (one-sentence purpose):**
Enumerate the frontend's route + page + layout + component surface at
static snapshot, testing whether the "STABLE + DEEP" 32-domain row 18
posture holds at the contract-surface boundary, and whether S1505
single-route findings generalize.

**Q2 — What problem does it solve? (business / platform problem):**
Prior arcs (Groups 1300-2100) touched the frontend only as downstream
consumer; no arc has enumerated route ownership, layout parent, or
consumer contract. This audit closes the whole-frontend visibility gap
on the structural axis (routes → pages → layouts → components) so that
S2202-S2204 can measure envelope / API / state discipline against a
grounded inventory rather than sampling assumptions.

## 3. Canonical Entry Points

Per playbook §9 Q3 with file:line.

**Root route table — App.tsx:**
- `frontend/src/App.tsx:64-149` — 59 distinct `<Route>` entries
  (delta vs PLATFORM_INVENTORY §Frontend row of 61 — see §14.1).
- `frontend/src/App.tsx:47-59` — `ProtectedRoute` component (single
  auth-wrapper for all authenticated routes).
- `frontend/src/App.tsx:69-129` — parent `Route path="/"` nesting
  wrapping 50+ authenticated child routes inside
  `<ProtectedRoute><Layout /></ProtectedRoute>`.
- `frontend/src/App.tsx:134-149` — 16 `/cockpit/*` legacy redirects
  (Phase 1 UI consolidation per line 131-132 comment).

**Root layout:**
- `frontend/src/components/layout/Layout.tsx` (76 LOC) — Root frame
  for all authenticated routes; owns system-event bridge (Session
  715) + `usePageTracking` telemetry (Session 971b) + `GlobalPADock`
  visibility gate (hidden on `path="/"` per Session 948).
- `frontend/src/components/layout/Header.tsx` (62 LOC) — Dynamic page
  title, search input, attention badge, notification bell.
- `frontend/src/components/layout/Sidebar.tsx` (366 LOC) — 14-item
  primary nav + 4 collapsible reference items; collapse state
  persisted to localStorage.

**Route ownership map — 59 rows (surface-grouped):**

*Public unauthenticated (4 routes, no auth wrapper by design):*

| Path | Page | Line | Data-source contract |
|---|---|---|---|
| `/login` | LoginPage | 64 | authApi via useAuthStore |
| `/vip/accept` | VipAcceptPage | 65 | useSearchParams(token) + authApi |
| `/r/:token` | ReviewPortalPage | 66 | useParams(token) + reviewPortalApi |
| `/operator-edge` | OperatorEdgePage | 67 | useSearchParams(config) |

*Root + navigation redirects under `path="/"` (4 routes):*

| Path | Component | Line | Redirect target / consumer |
|---|---|---|---|
| `/` (index) | CommandCenterPage | 78 | 28 useQuery hooks + PA sidebar orchestration + multi-api consumer |
| `/assistant` | Navigate → `/` | 79 | Session 931 unified command center |
| `/human` | Navigate → `/` | 80 | Session 931 unified command center |
| `/dashboard` | Navigate → `/` | 82 | Session 1083 Rigby hidden-routes audit |

*Workspace surface (5 routes + 2 redirects):*

| Path | Component | Line | Layout | Notes |
|---|---|---|---|---|
| `/workspace` | WorkspacePageNew | 95 | Layout | 1,260 LOC; 5-tab enum + sub-tabs; imports 8 cockpit pages |
| `/workspace/new` | WorkspaceCreatePage | 106 | Layout | wizard |
| `/workspace/:workspaceId` | WorkspaceDashboardPage | 107 | Layout | 848 LOC; uses useParams |
| `/boardroom` | Navigate → `/workspace?tab=boardroom` | 99 | — | Session 1067 |
| `/governance` | Navigate → `/workspace?tab=system` | 100 | — | Session 1067 |
| `/platform` | Navigate → `/workspace` | 96 | — | legacy consolidation |

*Betting surface (1 route):*

| Path | Component | Line | LOC | Notes |
|---|---|---|---|---|
| `/betting` | BettingPage | 89 | 3,023 | S1505 baseline; 9 tabs + 2 DEAD-RENDER-PATH orphans |

*Command Center / Intelligence surface (5 routes):*

| Path | Component | Line | LOC | Notes |
|---|---|---|---|---|
| `/` (index) | CommandCenterPage | 78 | 2,551 | god-component (see §15.2) |
| `/intelligence` | IntelligencePage | 85 | 3,546 | god-component |
| `/stocks` | StockIntelligencePage | 92 | 1,575 | god-component |
| `/analytics` | AnalyticsDashboardPage | 115 | 725 | — |
| `/docs-index` | DocsIndexPage | 116 | 469 | — |

*AI / Agent / Advisor surface (9 routes):*

| Path | Component | Line | LOC | Notes |
|---|---|---|---|---|
| `/agents` | AgentsPage | 84 | 4,695 | god-component (largest) |
| `/admin` | AdminPage | 94 | 1,175 | oversized |
| `/neural-orchestra` | NeuralOrchestraPage | 111 | 1,125 | oversized |
| `/mythology-lab` | MythologyLabPage | 113 | 1,227 | oversized |
| `/conversation-contract` | ConversationContractPage | 112 | 1,085 | oversized |
| `/advisors` | AdvisorsPage | 110 | 445 | — |
| `/demo` | DemoHomePage | 83 | 352 | — |
| `/how-it-works` | HowItWorksPage | 127 | ~350 | — |
| `/executor` | ExecutorPage | 128 | 477 | — |

*Content / Studio surface (5 routes):*

| Path | Component | Line | LOC |
|---|---|---|---|
| `/content` | ContentPage | 86 | 728 |
| `/image-studio` | ImageStudioPage | 124 | 687 |
| `/video-studio` | VideoStudioPage | 125 | 1,930 (god-component) |
| `/documents` | DocumentsPage | 123 | 1,270 (oversized) |
| `/media` | MediaPage | 126 | ~150 (stub) |

*Content library standalone (4 routes):*

| Path | Component | Line | LOC |
|---|---|---|---|
| `/deliverables` | DeliverablesPage | 120 | 346 |
| `/projects` | ProjectsPage | 121 | ~300 |
| `/projects/:projectId` | ProjectHubPage | 122 | 380 |
| `/blog/:blogId` | BlogViewerPage | 117 | 433 |

*Productivity + admin surface (7 routes):*

| Path | Component | Line | LOC |
|---|---|---|---|
| `/profile` | ProfilePage | 88 | 493 |
| `/settings` | SettingsPage | 87 | 851 |
| `/inbox` | InboxPage | 103 | 368 |
| `/billing` | BillingPage | 114 | 678 |
| `/portfolio` | PortfolioPage | 91 | 763 |
| `/legal` | LegalPage | 90 | 439 |
| `/government` | GovernmentPage | 93 | 896 |

*Cockpit legacy redirect surface (16 routes — no auth wrapper at
route level, but destination is protected):*

| Path pattern | Redirect target | Line |
|---|---|---|
| `/cockpit/incidents/*` | `/workspace?tab=system&sub=incidents` | 134 |
| `/cockpit/alerts` | `/workspace?tab=system&sub=alerts` | 135 |
| `/cockpit/autopilot` | `/workspace?tab=system&sub=autopilot` | 136 |
| `/cockpit/cost` | `/workspace?tab=system&sub=cost` | 137 |
| `/cockpit/queues` | `/workspace?tab=system&sub=queues` | 138 |
| `/cockpit/ops*` | `/workspace?tab=system&sub=ops` | 139 |
| `/cockpit/errors/*` | `/workspace?tab=system&sub=ops` | 140 |
| `/cockpit/runs/*` | `/workspace?tab=system&sub=ops` | 141 |
| `/cockpit/library` | `/workspace?tab=work&sub=deliverables` | 142 |
| `/cockpit/agents` | `/workspace?tab=system&sub=ops` | 143 |
| `/cockpit/learning` | `/workspace?tab=intelligence&sub=knowledge` | 144 |
| `/cockpit/config` | `/workspace?tab=system&sub=config` | 145 |
| `/cockpit/audit` | `/workspace?tab=system&sub=audit` | 146 |
| `/cockpit/approvals` | `/workspace?tab=system&sub=boardroom` | 147 |
| `/cockpit/inbox` | `/workspace?tab=home` | 148 |
| `/cockpit/*` (catch-all) | `/workspace` | 149 |

## 4. Major Models

Frontend has no Django ORM models. Interpreted per playbook §9 Q4 as
**typed data shapes + inline TypeScript interfaces per route/page**.

- **Route model:** `Route` from `react-router-dom` — 59 instances
  declared inline in App.tsx (no shared route-config source of truth;
  see §15.3).
- **Workspace tab model:** `frontend/src/pages/workspace/types.ts:9-35`
  — `WorkspaceTab` union type (5 primary + 19 legacy sub-tab values
  retained for backward-compat URL routing). Plus `TabConfig`,
  `SubTabConfig`, `Workspace`, `WorkspaceOperation`, `WorkspaceContext`
  interfaces at same file.
- **Page-level inline TS interfaces:** god-components declare inline
  interfaces at page scope — AgentsPage 24+ interfaces,
  IntelligencePage 12+, BettingPage 11+ (S1505 §15.4 baseline
  confirmed), CommandCenterPage 12+, NeuralOrchestraPage 10+,
  ConversationContractPage 11+. **Systemic pattern**: no shared page
  types module; every god-component re-declares its data shapes.

## 5. Major Services

Frontend has no Django services. Interpreted per playbook §9 Q5 as
**stores + hooks + api-module layer**.

- **Zustand stores** (`frontend/src/stores/`, 7 files) —
  `authStore.ts`, `paStore.ts`, `bodyStore.ts`, `navigationStore.ts`,
  `unifiedStore.ts`, `workspaceStore.ts`, `assistantContextStore.ts`.
  State-persistence discipline is Child D S2204 scope; Child A notes
  only ownership map.
- **Hooks** (`frontend/src/hooks/`, 5 files) — `cockpitQueries.ts`,
  `useFocusMode.ts`, `usePageTracking.ts` (invoked in Layout:14 per
  Session 971b), `usePanelStatus.ts`, `useWebSocket.ts` (used by 7
  pages per Agent 5 §14.5 evidence).
- **API-module layer** (`frontend/src/lib/`, 3 files) — `api.ts`
  (93 api-module definitions per Agent 6 — no exported TS types),
  `apiClient.ts` (axios/fetch client + global 401 handling at
  api.ts:48-56 — only surfaces logout for auth endpoints), and
  `cockpitApi.ts`. Full api-module inventory is Child C S2203 scope.

## 6. Major APIs and Interfaces

Per playbook §9 Q6, frontend-side interfaces = React component prop
contracts + consumed backend endpoints.

**Component prop contracts:** No shared prop-contract source of truth.
Layout (App.tsx:73) accepts no props; ProtectedRoute accepts `children`
(App.tsx:47). Individual pages accept no props (all state managed
internally via stores + hooks).

**Consumed backend endpoints (page-level):** Each page inlines its
API consumption via `@/lib/api` imports. Full endpoint inventory
deferred to Child C S2203. Notable page-level consumer contracts:

- **`/` (CommandCenterPage):** 28 useQuery/useMutation hooks;
  consumes assistantApi, contentApi, userLearningApi, bodyApi,
  humanApi, homeApi, agentsApi, orchestrationApi (multi-api
  consumer).
- **`/agents` (AgentsPage):** 24 useQuery/useMutation hooks;
  consumes agentsApi, orchestrationApi; subscribes to
  agent-execution WebSocket.
- **`/betting` (BettingPage):** 22 useQuery/useMutation hooks
  (S1505 baseline 14 useQuery — delta hypothesis: additional
  mutations included in current count); consumes bettingApi,
  sportsBettingApi; **zero WebSocket subscription** per S1505
  §14.5.
- **`/intelligence` (IntelligencePage):** 23 useQuery/useMutation
  hooks; consumes intelligenceApi + subscribes to intelligence
  desk WS updates.

## 7. Runtime Flows

Per playbook §9 Q9. Page render flow at static snapshot:

**Authenticated route render flow:**
1. Browser navigates to `/<path>`.
2. React Router matches path against 59 `<Route>` entries in
   App.tsx:64-149.
3. If path is nested under `path="/"` (App.tsx:69-129):
   - `ProtectedRoute` wrapper (App.tsx:47-59) checks
     `useAuthStore.isAuthenticated`.
   - If false: `<Navigate to="/login" replace />`.
   - If true: renders `<Layout />` + calls
     `usePAStore.syncUser(user?.id)` (clears conversations on
     user-switch).
4. `Layout.tsx` renders:
   - `DemoModeBanner` (line 55) + `GlobalAlertBanner` (line 57).
   - `Sidebar` (line 59) — collapse state from localStorage.
   - `Header` (line 64) — dynamic title from `pageTitles` static
     map at Header:7.
   - `<main>` → `<Outlet />` (React Router's child-route render
     point).
   - `GlobalPADock` (line 73) — hidden when `location.pathname
     === '/'` (Layout:20; CommandCenter has built-in chat).
5. `usePageTracking()` hook (Layout:14) fires page-view telemetry.
6. `useSystemEvents()` hook (Layout:45) wires WebSocket
   subscriptions to unified store mutations
   (`onPilotStarted`, `onPilotCompleted`, `onGateBecameCritical`,
   `onAgentExecutionComplete`).
7. Page component renders inside `<Outlet />`.

**Cockpit legacy redirect flow (16 routes at App.tsx:134-149):**
1. Browser navigates to `/cockpit/<path>`.
2. Route matches top-level (NOT nested under path="/") → NO auth
   wrapper at route level.
3. `<Navigate to="/workspace?tab=X&sub=Y" replace />` fires.
4. Browser navigates to `/workspace` → protected route → auth
   check → Layout + WorkspacePageNew renders with query params
   parsed via `resolveFromUrl` (WorkspacePageNew.tsx:791-816) +
   `legacyTabMapping` (WorkspacePageNew.tsx:159-196).

**Public route render flow (4 routes at App.tsx:64-67):**
1. Browser navigates to `/login` / `/vip/accept` / `/r/:token`
   / `/operator-edge`.
2. Route matches top-level; NO auth wrapper.
3. Page renders standalone (no Layout, no Sidebar, no Header).

## 8. Data Ownership and Lifecycle

Per playbook §9 Q16-Q18. Child A owns route + page + layout +
component structure; data ownership is downstream of Child C S2203
(API contract) + Child D S2204 (state persistence).

**Frontend owns:** route registry (App.tsx), page components
(frontend/src/pages/**), layout components (frontend/src/components/
layout/**), workspace tab configuration (WorkspaceTab enum +
legacyTabMapping).

**Frontend consumes:** all backend endpoints via api-modules in
`frontend/src/lib/` (93 definitions per Agent 6). Consumer contracts
inlined at page level; no typed schema (Child C S2203 scope).

**Frontend produces:** page-view telemetry via `usePageTracking()`
POST to `/api/v1/telemetry/page-view/` (per topics/frontend.md §Page
Telemetry); no other frontend-authored data emission. Zero frontend
emission to Signal Engine (per Agent 5 F3).

## 9. Integrations With Other Domains

Per playbook §9 Q14 + Q17 + Q18 + Q21 + Q22. Table format.

Child A's integration axis is **inbound route-consumer bindings** —
which backend domains each route consumes. Full API surface + WS
consumer inventory + envelope discipline is Child B (S2202) + Child C
(S2203) scope.

| Route surface | Inbound backend domains | Integration strength (per S1274 vocab) |
|---|---|---|
| `/` CommandCenterPage | PA + HumanAttention + BodyGovernance + Agents + Content + Intelligence + Learning + Signals | **STRONG** — 28 useQuery hooks; multi-api consumer; per S1505 pattern also OVERCOUPLED at page-component level |
| `/betting` BettingPage | Sports odds + Wagers + BettingBrief + WagerRecord | **STRONG at REST**; **WEAK at WS** (S1505 §14.5 zero-WS-subscription) |
| `/agents` AgentsPage | Agents + Orchestration + Learning + AgentExecution WS | **STRONG** with real-time WS subscription |
| `/intelligence` IntelligencePage | Signals + Pilots + Predictions + Spiders + Income + Governance | **STRONG** with WS |
| `/stocks` StockIntelligencePage | Stocks + Ticker + Briefs + Alerts + SEC + Predictions | **STRONG at REST**; **UNKNOWN at WS** (defer to Child B S2202) |
| `/workspace` WorkspacePageNew | Workspace + Operations + all workspace sub-tab domains (Content, Boardroom, DataIntel, Knowledge, Voices, Campaigns, ConceptForge, Consciousness, Learning, Career, Evaluation, Files, Ops, Git, Triggers) | **STRONG** — 31 workspace tab modules per Agent 3; imports 8 cockpit pages |
| `/content` ContentPage + all content-library standalone routes | Content + Blogs + Deliverables + Projects + Documents + Media | **STRONG** but standalone (not workspace-nested); duplicate-surface risk with workspace ContentStudioTab (§17.1) |
| `/advisors` + `/neural-orchestra` + `/mythology-lab` + `/conversation-contract` | Advisors + Orchestration + Memory + Learning + Conversation | **STRONG at REST**; UNKNOWN at WS |
| Public routes | Auth (via authApi only) | **N/A** (public) |

**Missing integrations at Child A scope:** no cross-page state sharing;
no shared route ↔ page ↔ layout contract; no explicit feature-boundary
isolation (any page can import from any store / hook / api-module
without gates).

## 10. Event Flows

Per playbook §9 Q19-Q20.

**Events Child A surface emits:**
- `POST /api/v1/telemetry/page-view/` on route change (via
  `usePageTracking()` at Layout:14, Session 971b).
- No other frontend-authored events.
- **Zero Signal Engine emission** across all frontend surfaces (Agent
  5 F3) — this is domain-specific to Signal Engine backend
  architecture, NOT a Child A drift.

**Events Child A surface should emit (gaps):**
- Route-navigation events for user-behavior telemetry beyond page-view
  (deferred to Group 1800 HumanAttention scope, not Group 2200).
- Error-boundary catch events — no error boundaries exist (§15.4).

**Events Child A surface consumes (WebSocket bridging via
`useSystemEvents` in Layout:45):**
- `onPilotStarted`, `onPilotCompleted`, `onGateBecameCritical`,
  `onAgentExecutionComplete` — wired to unified store fetchers
  (fetchAttentionStats, fetchRunningPilots, fetchCriticalGates,
  fetchTopOpportunities). This is Layout-scoped; per-page WS
  consumers are Child B (S2202) territory.

## 11. Existing Documentation

Per playbook §9 Q10.

| Doc | Anchor | Freshness | Coverage |
|---|---|---|---|
| `docs/topics/frontend.md` | narrative anchor (stale-warned) | DOC-POINTER-V1 stale banner | Covers 5-tab workspace, Command Center, Now Hub, Intelligence Desks Panel, PA GlobalPADock, page telemetry, betting dashboard. **Missing:** route ownership map, god-component inventory, envelope discipline, state persistence, API contract SoT. |
| `docs/PLATFORM_INVENTORY.md` §Frontend | runtime anchor | fresh (2026-07-02) | 61 routes / 5 workspace tabs / 9 betting tabs — count delta of 61 vs Child A count of 59 flagged §14.1. |
| `docs/PLATFORM_WHAT_IT_IS.md` | narrative anchor | 2026-06-30 last review | Frontend covered in narrative body. |
| `docs/research/platform_architecture_inventory.md` row 18 | S1273 32-domain map | 2026-06-27 | "STABLE + DEEP" posture claim — Child A pressure-tests. §20.6. |
| `docs/research/domains/sports/1505_sports_frontend_surface_audit.md` | S1505 audit | active | Single-route slice (`/betting`); §14 findings graduated to whole-frontend at Child A per 4-falsifier test. |

Session-annotation trail via import comments in App.tsx covers 9 sessions
(825, 931, 1012, 1035, 1067, 1078, 1083, 1100, 1240). 22 of 38
imported pages carry zero session comment (§18.2).

## 12. Research Coverage

Per playbook §9 Q11 + §12 classification.

**Frontend research library entries in ARCHITECTURE_INDEX §1 (pre-Group
2200):**
- S1505 Cat E Sports Frontend Surface (`/betting` slice only).
- S1101 5-tab consolidation (workspace-only research; not routes).
- S931 Command Center unification (implementation session; not audit).
- Miscellaneous frontend touch-ups in Groups 1300-2100 as downstream
  consumer references.

**Research Coverage classification (§12):** **LIGHT** — only one prior
dedicated audit (S1505, single-route). Group 2200 arc-open confirms
Child A is the first whole-frontend research artifact on the
route/page/layout axis.

## 13. Architecture Maturity

Per playbook §9 Q12-Q13 + §12 classification.

| Sub-axis | Classification | Evidence |
|---|---|---|
| Route composition | **STABLE** | 59 routes, single auth-wrapper, deliberate cockpit consolidation (Sessions 971b/1035/1078/1083/1240 trail visible in App.tsx). Consistent naming. |
| Page components | **WORKING** | 38 page files; functional but 6 god-components >1,500 LOC (§15.2); zero test coverage (§15.1). Not STABLE at component-boundary discipline. |
| Layout system | **STABLE** | Single Layout.tsx (76 LOC), single Header/Sidebar. Clean separation: Layout owns frame + system-event bridge only; auth deferred to ProtectedRoute; PA state deferred to paStore; workspace state deferred to workspaceStore. Zero cross-cutting dependencies. |
| Component patterns | **WORKING** | Two import patterns split (@/ alias for cross-page, relative for workspace-internal — Agent 6). Predictable within each scope. |
| **Composite verdict** | **WORKING** | Route + Layout are STABLE; pages + components are WORKING; contract-level discipline is PARTIAL-to-UNMET (§1 acceptance criteria). |

**Pressure-test vs S1273 row 18 "STABLE + DEEP":** **DOWNGRADE
candidate.** Route + Layout meet STABLE; pages + components meet
WORKING; audit coverage was LIGHT before this audit (research coverage
per §12 = LIGHT, not DEEP). Recommendation for xx99: **downgrade
posture to WORKING + MEDIUM** (or PARTIAL + MEDIUM if xx99 weighs
component + contract discipline more heavily than route + layout).
Final resolution deferred to S2299 canonical summary after
S2202-S2204 complete the 4-axis picture.

## 14. Known Drift

Per playbook §9 Q27 with evidence.

### 14.1 Route count delta — PLATFORM_INVENTORY §Frontend claims 61; audit counts 59
**Claim.** PLATFORM_INVENTORY §Frontend row (2026-07-02) says "61 routes
in App.tsx"; Agent 1 counted 59 distinct `<Route path=` entries at
`frontend/src/App.tsx:64-149`.
**Evidence.** Grep + line-by-line inspection of App.tsx.
**Severity.** LOW.
**Class.** `observation` (Rigby SIGN cycle 1 Q1 CLEAN with micro-fold —
inventory semantics delta, NOT `drift`; the two counters define "route"
differently, and the system has not regressed against a stable spec).
**Hypothesis.** Inventory generator may count nested/parent Route
wrappers (`<Route path="/">` line 70 wrapping child index route) or
`<Navigate>` element instances differently than `<Route path=`
declarations. Reconcile via `python manage.py
generate_platform_inventory` at xx99 + verify the generator's counting
function on both sides.

### 14.2 Legacy sub-tab enum is load-bearing; `normalizeWorkspaceTab()` NOT FOUND
**Claim.** Parent scoping §5 Child A deliverable (e) referenced
`normalizeWorkspaceTab()` as an audit target; function does NOT exist
at HEAD `04ee0964` per Agent 4 grep.
**Evidence.** Superseded by inline `legacyTabMapping` object at
WorkspacePageNew.tsx:159-196 (25 entries) + `resolveFromUrl` local
function at WorkspacePageNew.tsx:791-816. `normalizePlatformTab()` also
NOT FOUND (deleted per Session 1240 cascade per types.ts:37-38
comment; no ghost references remain).
**Severity.** MED.
**Class.** `legacy_compatibility_debt` (Rigby SIGN cycle 1 Q5 CLEAN with
micro-fold — the 19 legacy sub-tab values + `legacyTabMapping` object
work as intended as backward-compat URL routing; the debt is maintenance
burden + hidden coupling + future migration hazard, NOT active `drift`.
Parent-scoping's reference to the deleted `normalizeWorkspaceTab()` is a
minor doc drift to correct at xx99).
**Recommendation.** Correct parent-scoping doc at xx99 to reference
`legacyTabMapping` + `resolveFromUrl` rather than the deleted
`normalizeWorkspaceTab()`. Deliberate retirement project owed to
post-arc T-slot (§19 R5-adjacent).

### 14.3 Cockpit redirect two-stage auth (MINOR-DRIFT)
**Claim.** 16 `/cockpit/*` routes at App.tsx:134-149 are NOT wrapped by
ProtectedRoute at the route level; they Navigate to protected targets
under `/workspace?tab=X&sub=Y`. Unauthenticated users see a momentary
unprotected redirect before the second-stage protection kicks in.
**Evidence.** App.tsx:134-149.
**Severity.** LOW (no security bypass — final destination is
protected).
**Class.** `drift` (deviates from single-auth-boundary pattern).
**Recommendation.** T-slot decision at xx99: (i) wrap `/cockpit/*` in
`ProtectedRoute` for single-boundary discipline, OR (ii) explicitly
document as Phase 1 legacy behavior, OR (iii) retire cockpit routes
entirely after inbound-link audit.

### 14.4 Session-annotation drift — 22/38 pages carry no session comment
**Claim.** Session annotations exist in 16/38 imported pages; 22
lack any session trail (DeliverablesPage, OperatorEdgePage,
VipAcceptPage, ReviewPortalPage, ImageStudioPage, VideoStudioPage,
BettingPage itself, StockIntelligencePage, ExecutorPage, LegalPage,
GovernmentPage, InboxPage, MediaPage, MythologyLabPage,
AnalyticsDashboardPage, DocsIndexPage, BlogViewerPage,
NeuralOrchestraPage, ConversationContractPage, PortfolioPage,
LoginPage, ProfilePage).
**Evidence.** Agent 6 § R2 grep of page-file headers.
**Severity.** MED.
**Class.** `ownership_gap` (folded into §18.2).
**Recommendation.** Session-annotation retrofit T-slot post-arc.

### 14.5 Layout hardcodes `/` for GlobalPADock visibility (LOW-fragility)
**Claim.** `Layout.tsx:20` sets `hideGlobalDock = location.pathname
=== '/'`. If future routes become "/" equivalents (nested / matrix /
alternate command-center location), dock hiding breaks.
**Evidence.** Layout.tsx:20.
**Severity.** LOW.
**Class.** `drift` (fragility — coupling to specific route rather
than an explicit context flag).
**Recommendation (option-space; concrete implementation deferred to
Group 2600 PA per Rigby SIGN cycle 1 Q16 STRENGTHEN fold).** Preferred
resolution shapes: (i) route metadata (declare `hidePADock` on the route
config), (ii) layout-level feature flag / context (`usePADockVisibility`
context provider consumed by Layout), (iii) centralized visibility policy
managed by paStore. Group 2600 PA arc owns the concrete mechanism
choice; Child A observes the fragility + records the option-space only.

### 14.6 Doc drift — `topics/frontend.md` §Betting Dashboard 9-tab claim vs 11 declared (handoff note)
**Claim.** Documented in S1505 §14.9. Doc drift persists at S2201
open (per topics/frontend.md stale-warning banner).
**Evidence.** S1505 §14.9 cited.
**Severity.** LOW.
**Class.** `drift` (doc-vs-code).
**Framing (Rigby SIGN cycle 1 Q19 CLEAN with micro-fold — handoff note,
not core audit finding).** Tracked by doc-cascade + verify_doc_claims
discipline. Included here as cross-reference only for xx99 handoff
completeness; does not inflate Child A's "frontend quality" narrative.
**Cross-arc.** Handled by doc-cascade + verify_doc_claims discipline,
not Group 2200 fix scope.

## 15. Known Technical Debt

Per playbook §9 Q26 with severity + class.

### 15.1 Zero test coverage across `frontend/src/pages/**`
**Claim.** 0 `*.test.tsx` or `*.spec.tsx` files under
`frontend/src/pages/**` at HEAD `04ee0964`.
**Evidence.** Agent 6 glob + Agent 5 F4 confirmation.
**Severity.** **HIGH baseline; CRITICAL for specific surfaces** (Rigby
SIGN cycle 1 Q3 STRENGTHEN 2026-07-05 fold — CRITICAL platform-wide is
over-severe for a single-operator solo-build context; team-throughput-
collapse dimension is not load-bearing). Generalizes S1505 §15.1
(CRITICAL per S1504 §15.12 F4-fold precedent for zero-test as
reliability-risk multiplier) from single-route to whole-frontend as
**HIGH baseline + CRITICAL for payments / auth / billing / betting /
ledger-like flows** (BillingPage, BettingPage, `/portfolio`, `/wager*`
endpoints, `/api/v1/odds/bankroll*`) where regression-catch-rate risk is
amplified.
**Class.** `technical_debt` (testing_debt).
**Follow-on.** §19 R1 — integration-test framework establishment
T-slot; per-god-component test suite prerequisite before any
subdivision.

### 15.2 God-component pathology generalizes to 6 pages >1,500 LOC + 3 workspace tabs >2,500 LOC
**Claim.** Frontend god-component inventory:

| Page | LOC | useQuery+useMutation | useState | Surface | Class |
|---|---|---|---|---|---|
| AgentsPage.tsx | 4,695 | 24 | 26 | AI/Agent | **god (>1,500)** |
| IntelligencePage.tsx | 3,546 | 23 | 10 | Command-Center | **god** |
| BettingPage.tsx | 3,023 | 22 | 18 | Betting | **god** (S1505 baseline) |
| CommandCenterPage.tsx | 2,551 | 28 | 19 | Command-Center | **god** |
| VideoStudioPage.tsx | 1,930 | 20 | 38 | Content-Studio | **god** |
| StockIntelligencePage.tsx | 1,575 | 10 | 16 | Command-Center | **god** |
| DocumentsPage.tsx | 1,270 | 13 | 18 | Workspace-adjacent | oversized (1,000-1,500) |
| WorkspacePageNew.tsx | 1,260 | 10 | 12 | Workspace | oversized |
| MythologyLabPage.tsx | 1,227 | 10 | 5 | AI/Advisor | oversized |
| AdminPage.tsx | 1,175 | 14 | 3 | Admin | oversized |
| NeuralOrchestraPage.tsx | 1,125 | 10 | 3 | AI/Advisor | oversized |
| ConversationContractPage.tsx | 1,085 | 7 | 11 | AI/Advisor | oversized |

**Surface attribution (Rigby SIGN cycle 1 Q11 STRENGTHEN 2026-07-05 fold
— surface = top-level product area; multiple pages within one product
surface count as loci within that surface, not separate surfaces):** 4
top-level product surfaces represented — **Agents/AI** (AgentsPage),
**Command-Center** (IntelligencePage + CommandCenterPage +
StockIntelligencePage as 3 loci within one surface), **Betting**
(BettingPage), **Content-Studio** (VideoStudioPage). S2200 §5 Q4
STRENGTHEN threshold (≥3 god-components across ≥2 top-level product
surfaces) is met at 6 pages across 4 surfaces.

**Additional evidence — intra-route tab components (Rigby SIGN cycle 1
Q12 CLEAN 2026-07-05 fold — supplement not trigger-critical):**
InitiativesTab 3,277 LOC, ContentStudioTab 3,167 LOC, OrchestrationTab
2,985 LOC. These are god-sized components rendered inside
`WorkspacePageNew`'s tab tree, not standalone routes; Child E trigger is
met on page-level alone without them.

**Evidence.** `wc -l` sweep + Agent 2 per-file grep for useQuery /
useMutation / useState / inline-component / inline-interface counts.
**Severity.** **HIGH baseline; CRITICAL for CommandCenterPage +
BettingPage** where blast-radius + churn + high-coupling profile
amplifies risk (Rigby SIGN cycle 1 Q2 STRENGTHEN fold — severity scales
by blast radius + churn + defect history, not by LOC alone).
**Class.** `technical_debt` (component_debt).
**Follow-on.** §19 R2 — subdivision cost estimate; Child E spin-out
decision Chris-gated at S2201 close.

### 15.3 No shared route-config source of truth
**Claim.** 59 routes hardcoded in App.tsx:64-149; no `routes.config.
ts`, no route registry, no data-driven redirect table.
**Evidence.** App.tsx inspection.
**Severity.** MED.
**Class.** `technical_debt` (architecture_debt).
**Follow-on.** T-slot: extract routes to config module; deferred to
Group 2500 API/routing arc coordination.

### 15.4 No error boundaries anywhere in the frontend
**Claim.** Frontend has no `<ErrorBoundary>` component or usage;
`react-error-boundary` not in dependency tree.
**Evidence.** Agent 5 §14.6 evidence + Agent 6 §R3 grep confirmation.
**Severity.** MED-HIGH per S1505 §15.6 precedent.
**Class.** `technical_debt` (failure-mode discipline gap).
**Follow-on.** §19 R6 — establish error-boundary framework + per-page
convention.

### 15.5 Silent 401 as frontend default behavior at `frontend/src/lib/api.ts:48-56` (cross-arc dependency)
**Claim.** Observed default behavior in frontend API wrapper: global 401
handler catches only auth-endpoints for logout; all other 401s log a
warning but do NOT surface to UI. Symptom that Universalizes S1505
§14.3 silent-401 pattern.
**Evidence.** Agent 5 §14.6 API contract audit; `api.ts:48-56`.
**Severity.** **HIGH at frontend-symptom scope; systemic-severity
classification pending Group 2400 Auth spec** (Rigby SIGN cycle 1 Q13
STRENGTHEN 2026-07-05 fold — Child A observes the symptom + default
behavior, does not declare the root cause; the "systemic" framing
depends on Group 2400 session-contract decisions).
**Class.** `technical_debt` (failure-mode discipline at frontend layer).
**Follow-on.** Cross-arc dependency handoff to Group 2400 Auth
(session model) + Group 2500 API (typed responses) — Child A cannot
resolve without out-of-scope work.

### 15.6 Legacy `WorkspacePage` alias + orphan cockpit pages
**Claim.** App.tsx:19 imports `WorkspacePage` from
`@/pages/WorkspacePageNew` — alias suggests a prior `WorkspacePage.tsx`
that Agent 6 did not find at HEAD. And 8 cockpit pages
(`frontend/src/pages/cockpit/*`) are imported by WorkspacePageNew but
NOT routed as standalone `/cockpit/*` routes (they render as tab
content).
**Evidence.** App.tsx:19 + WorkspacePageNew.tsx:60-67 + App.tsx:44-45
preservation comment.
**Severity.** LOW.
**Class.** `technical_debt` (cleanup_debt / naming drift).
**Follow-on.** T-slot: rename `WorkspacePage` alias or delete legacy
`WorkspacePage.tsx` if it exists; document cockpit-page preservation
posture (Phase 1 UI consolidation intent).

### 15.7 CockpitLayout is dead code
**Claim.** `frontend/src/components/cockpit/CockpitLayout.tsx` (67
LOC) mirrors Layout.tsx but is never rendered — all `/cockpit/*` routes
Navigate to protected workspace targets.
**Evidence.** Agent 3 §R3 signal 2.
**Severity.** LOW.
**Class.** `dead_code`.
**Follow-on.** T-slot: delete CockpitLayout.tsx + CockpitSidebar.tsx;
preserve pages/cockpit/ if restore-path planned.

## 16. Boundary Violations

Per playbook §9 Q24.

### 16.1 WorkspacePageNew imports cockpit pages directly (no adapter interface)
**Evidence.** WorkspacePageNew.tsx:60-67 imports 8 cockpit pages as
full React components. No declared boundary or type contract between
workspace and cockpit surfaces.
**Severity.** MED.
**Class.** `boundary_violation`.
**Recommendation.** T-slot: define cockpit-to-workspace adapter
interface OR complete cockpit page deletion.

### 16.2 Layout hardcodes route path for PA visibility
**Evidence.** Layout.tsx:20 (`location.pathname === '/'`). Couples
layout render to specific path rather than route-aware context or
PA-disable flag.
**Severity.** LOW.
**Class.** `boundary_violation` (route-coupling).
**Recommendation.** Add explicit PA-disable context; fold into §14.5
drift entry.

### 16.3 No validated feature-boundary isolation
**Evidence.** Pages import freely from `@/stores`, `@/components`,
`@/lib` with no feature-prefix or gate. No `/features/*` directory.
Cross-feature leakage possible but not systematically observed.
**Severity.** LOW.
**Class.** `boundary_violation` (documentation-gap).
**Recommendation.** T-slot: propose feature-boundary convention.

## 17. Duplicate or Overlapping Systems

Per playbook §9 Q23.

### 17.1 Content standalone routes vs workspace ContentStudioTab
**Overlap.** `/content` (ContentPage 728 LOC), `/deliverables`
(DeliverablesPage 346 LOC), `/projects`, `/documents`, `/image-studio`,
`/video-studio`, `/media` are standalone content-surface routes; also
present as sub-tabs inside workspace ContentStudioTab
(WorkspacePageNew.tsx:60-67 imports). Two entry points for the same
domain surface.
**Verdict.** DUPLICATE (partial — standalone routes may have distinct
UX from workspace-embedded surfaces; needs product decision).
**Follow-on.** T-slot at xx99 — decide canonical entry point per
content-surface sub-domain.

### 17.2 Command-center PA-adjacent surfaces — PARTIAL-DUPLICATE / intentional multi-locus
**Overlap.** CommandCenterPage (`/`) + GlobalPADock (Layout overlay) +
PAConversationSidebar (reused component). Multiple PA render loci + a
shared sub-component.
**Verdict.** **PARTIAL-DUPLICATE / intentional multi-locus** (Rigby SIGN
cycle 1 Q15 FOLD 2026-07-05 — "DIFFERENT-CONCERNS" undersells the
structural reality that there are multiple PA render loci + a reused
sidebar component, which is exactly the kind of duplication/consistency
risk a contract-surface audit should surface). Two (or more) intentional
render surfaces plus a shared sub-component; GlobalPADock explicitly
hidden on `/` to avoid dual-chat confusion (Layout.tsx:20).
**Follow-on.** **Group 2600 PA arc decides consolidation vs deliberate
redundancy.** Document current intent in `topics/frontend.md` §PA
Integration as cross-arc coordination flag.

### 17.3 WorkspacePage alias + WorkspacePageNew filename
**Overlap.** App.tsx:19 `import WorkspacePage from
'@/pages/WorkspacePageNew'`. Naming drift.
**Verdict.** DUPLICATE (naming-only; refactor candidate).
**Follow-on.** §15.6.

### 17.4 CockpitLayout vs Layout
**Overlap.** Two frame components with similar structure; CockpitLayout
is unreachable orphan.
**Verdict.** DUPLICATE (CockpitLayout is dead code).
**Follow-on.** §15.7.

### 17.5 Route redirect surface overlap
**Overlap.** `/assistant`, `/human`, `/dashboard` all redirect to `/`
(3 legacy redirect routes for one canonical destination). `/boardroom`,
`/governance`, `/platform` redirect to `/workspace?...` variants.
**Verdict.** INTENTIONAL (legacy consolidation history preserved via
redirect).
**Follow-on.** T-slot at xx99 — retirement decision after inbound-link
audit.

## 18. Ownership Gaps

Per playbook §9 Q25.

### 18.1 No CODEOWNERS file (HIGH with single-operator caveat)
**Claim.** `CODEOWNERS`, `.github/CODEOWNERS`, `docs/CODEOWNERS` all
missing at repo root and standard locations.
**Evidence.** Agent 6 bash find + grep.
**Severity.** **HIGH with single-operator caveat** (Rigby SIGN cycle 1
Q4 STRENGTHEN 2026-07-05 fold — CRITICAL platform-wide is over-severe
for a single-operator solo build; this is future-scale hardening debt
that becomes CRITICAL the moment a second contributor exists).
**Class.** `ownership_gap`.
**Impact.** No per-file ownership trail. Universalizes S1505 §14.11
BettingPage-scoped no-CODEOWNERS finding.
**Follow-on.** §19 R4 — establish CODEOWNERS T-slot post-arc.

### 18.2 22/38 imported pages lack session-annotation trail
**Claim.** See §14.4. 22 pages carry no session comment; no handoff
record.
**Severity.** MED.
**Class.** `ownership_gap`.
**Follow-on.** T-slot — session-annotation retrofit sweep.

### 18.3 Cockpit pages orphaned (imported but unroute-able)
**Claim.** 8 cockpit pages preserved for potential restore per App.tsx:
44-45 comment; no explicit deprecation marker in files themselves; no
migration guide linking old cockpit paths to new workspace tabs.
**Evidence.** Agent 6 §R6.
**Severity.** MED.
**Class.** `ownership_gap` (deprecation-posture unclear).
**Follow-on.** T-slot — explicit `DEPRECATED` markers or deletion.

## 19. Recommended Future Research

Per playbook §9 Q28. Ranked by architectural uncertainty × risk ×
unblocked flows.

### R1 — Frontend test-framework establishment (HIGH priority; in parallel to R2)
**Rationale.** §15.1 zero-test-coverage is HIGH baseline + CRITICAL for
payments / auth / billing / betting flows. Framework choice
(Vitest+RTL, Playwright, etc.) is a Group 2200 T-slot; per-god-
component test suites are prerequisite to any deep subdivision (Rigby
SIGN cycle 1 Q18 STRENGTHEN 2026-07-05 fold — R1 runs in parallel to
R2 as the gating safety track: do not attempt deep refactors of
spun-out modules until minimal test harness exists for the affected
surface).
**Owner.** Post-arc T-slot; parallel to R2.

### R2 — Child E component-pattern deep dive (Chris-gated at S2201 close; execution-sequence lead)
**Rationale.** S2200 §5 Q4 STRENGTHEN Child E spin-out trigger **MET**
(6 pages >1,500 LOC across ≥3 top-level product surfaces). Subdivision
cost estimate (prioritized): (1) CommandCenterPage 2,551 LOC XL —
PA/command-loop critical, coupling to chat + async jobs + voice +
cockpit re-hosts; (2) AgentsPage 4,695 LOC XL — 7 tabs + 7 modals +
WebSocket agent updates; (3) BettingPage 3,023 LOC XL — 11 tabs +
real-time odds + arbitrage logic (S1505 baseline). **Execution
ordering (Rigby SIGN cycle 1 Q18 STRENGTHEN fold): R2 leads R1 in
execution sequence** — spin-out enables Chris to feel incremental
velocity gains immediately in the solo dev-loop; R1 runs in parallel
as the gating safety track. Do not attempt deep refactors of spun-out
modules until minimal test harness exists.
**Owner.** Chris D-gate at S2201 close.

### R3 — Route ownership map extraction to config source of truth
**Rationale.** §15.3. Extract 59 routes from App.tsx into
`frontend/src/routes.config.ts` (or similar). Coordinates with
potential Group 2500 API arc + Group 2400 Auth arc for route-level
permission-floor declarations.
**Owner.** Post-arc T-slot; coordinate with Group 2400/2500 timing.

### R4 — CODEOWNERS establishment
**Rationale.** §18.1 CRITICAL. Universalizes S1505 §14.11 finding.
Prerequisite for any ownership-based tooling (auto-review, notification
routing, deprecation posture).
**Owner.** Post-arc T-slot.

### R5 — Cockpit route retirement decision (Chris-gated)
**Rationale.** §14.3 two-stage auth + §17.4 CockpitLayout dead code +
§18.3 orphaned pages. Requires external inbound-link audit before
deletion.
**Owner.** T-slot at xx99.

### R6 — Error-boundary framework establishment
**Rationale.** §15.4 no error boundaries + §15.5 silent 401 systemic.
Requires cross-arc coordination with Group 2400 Auth (session model)
+ Group 2500 API (typed responses).
**Owner.** Post-arc T-slot; cross-arc.

### R7 — Session-annotation retrofit for 22 unlabeled pages
**Rationale.** §14.4 + §18.2. Modest scope; recoverable via git-log
per file.
**Owner.** Post-arc T-slot.

### R8 — PLATFORM_INVENTORY route-count reconciliation
**Rationale.** §14.1. 61 vs 59. Regen inventory + verify generator
semantics.
**Owner.** xx99 close cascade.

### R9 — Parent-scoping doc correction — replace `normalizeWorkspaceTab()` reference
**Rationale.** §14.2. Function already deleted; parent scoping §5
Child A deliverable (e) should reference `legacyTabMapping` +
`resolveFromUrl` instead.
**Owner.** xx99 correction or Chris D-gate.

## 20. Appendix

### 20.1 Files inspected

**Route + layout:**
- `frontend/src/App.tsx` (155 LOC — 59 Route entries + ProtectedRoute
  wrapper)
- `frontend/src/components/layout/Layout.tsx` (76 LOC)
- `frontend/src/components/layout/Sidebar.tsx` (366 LOC)
- `frontend/src/components/layout/Header.tsx` (62 LOC)
- `frontend/src/components/cockpit/CockpitLayout.tsx` (67 LOC — dead
  code per §15.7)

**Pages:**
- All 38 files under `frontend/src/pages/` referenced by App.tsx import
  block (lines 5-42) — sampled at line-count level for all; deep read
  for the 6 god-components + 6 oversized pages.

**Workspace types + tabs:**
- `frontend/src/pages/workspace/types.ts` (144 LOC)
- `frontend/src/pages/workspace/tabs/*` (31 modules; Agent 2 line-count
  sweep — InitiativesTab 3,277, ContentStudioTab 3,167,
  OrchestrationTab 2,985 identified as tab-level god-components)
- `frontend/src/pages/workspace/components/*` (subordinate components)

**Stores + hooks + api-modules (ownership map only — deep audit
deferred to S2203/S2204):**
- `frontend/src/stores/*` (7 files)
- `frontend/src/hooks/*` (5 files)
- `frontend/src/lib/api.ts` + `apiClient.ts` + `cockpitApi.ts`

### 20.2 Docs inspected

- `docs/PLATFORM_WHAT_IT_IS.md` (narrative anchor)
- `docs/PLATFORM_INVENTORY.md` §Frontend row (runtime anchor)
- `docs/topics/frontend.md` (subsystem doc, stale-warned)
- `docs/research/platform_architecture_inventory.md` row 18 (S1273
  "STABLE + DEEP" claim under pressure test)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section child
  template + §9 28-canonical questions + §12 classification + §13
  6-Explore-agent pattern + §14 verifier-loop
- `docs/research/domains/frontend/2200_frontend_domain_scoping.md`
  (S2200 parent scoping)
- `docs/research/domains/sports/1505_sports_frontend_surface_audit.md`
  (S1505 4-falsifier test target)
- `docs/research/domains/rag_document_loading/2101_*.md` (§11.2
  exemplar shape)

### 20.3 Grep patterns used

- `<Route path=` (route enumeration in App.tsx)
- `useQuery|useMutation` (per-page complexity metric)
- `useState` (per-page complexity metric)
- `useWebSocket|new WebSocket|wss:|ws:` (WS-subscription F2 evidence)
- `SignalCluster|signal_aggregation` (F3 Signal Engine emission)
- `localStorage|sessionStorage|IndexedDB` (state persistence sample
  for F4)
- `bettingApi|humanApi|sportsHubApi` (api-module distribution)
- `normalizeWorkspaceTab|normalizePlatformTab|LEGACY_TO_PLATFORM`
  (legacy normalization ghost check)
- `CODEOWNERS` (ownership gap check)
- `Session \d+` (session-annotation trail per page)
- `wc -l frontend/src/pages/*.tsx` (line-count sweep)

### 20.4 Unresolved unknowns

- Full API call-site inventory per page — deferred to Child C S2203.
- Full WebSocket consumer subscription map — deferred to Child B
  S2202.
- Per-page localStorage / sessionStorage inventory + persistence
  discipline — deferred to Child D S2204.
- External inbound-link status for 16 `/cockpit/*` redirect routes —
  requires external analytics.
- Query-parameter conventions for CommandCenterPage /
  ReviewPortalPage / OperatorEdgePage — Agent 1 §R3 flagged as
  UNKNOWN pending Child C S2203 detail.

### 20.5 Conflicts between sources

- **PLATFORM_INVENTORY 61 vs Agent 1 count 59.** See §14.1.
  Recommendation: regen inventory at xx99 close.
- **S1505 §15.4 BettingPage metrics (14 useQuery / 17 useState) vs
  Agent 2 metrics (22 useQuery+useMutation / 18 useState).** Delta
  hypothesis: S1505 counted `useQuery` only; Agent 2 counted
  `useQuery + useMutation` combined. Non-conflicting; different
  counter shape.
- **Parent scoping §5 Child A deliverable (e) `normalizeWorkspaceTab`
  reference vs Agent 4 grep finding function does NOT exist.** See
  §14.2. Reconcile at xx99.

### 20.6 POSTURE-DECISION evidence plan owed to xx99

Per S2200 §5 Child A delegation — pressure-test "STABLE + DEEP" (S1273
32-domain row 18) at contract level.

**Evidence gathered by Child A:**

| Sub-axis | Contract-level verdict | Evidence pointer |
|---|---|---|
| Route composition | STABLE-at-render (59 routes; single wrapper); UNMET-at-contract (no ownership-map source of truth) | §3 + §15.3 |
| Layout system | STABLE-at-render; STABLE-at-contract (single Layout; clean separation) | §3 + §13 |
| Page components | WORKING-at-render (functional but debt-heavy); PARTIAL-at-contract (6 god-components; zero tests) | §15.2 + §15.1 |
| Component patterns | WORKING-at-render (two-pattern split); PARTIAL-at-contract (no shared types; no error boundaries; silent 401 systemic) | §15.4 + §15.5 |
| Auth-wrapper | STABLE-at-render; MINOR-DRIFT (16 cockpit two-stage) | §14.3 + Agent 1 R2 |
| Documentation coverage | LIGHT (topics/frontend.md stale-warned; PLATFORM_INVENTORY count delta) | §11 + §12 |
| Test coverage | LIGHT / UNMET (CRITICAL — 0 test files) | §15.1 |
| Ownership | LIGHT (no CODEOWNERS; 22/38 pages no session trail) | §18.1 + §18.2 |

**Child A recommendation to xx99 (Rigby SIGN cycle 1 Q17 FOLD 2026-07-05
— committed to single posture per playbook §14 verifier discipline):**

> **DOWNGRADE S1273 32-domain row 18 posture from "STABLE + DEEP" to
> "WORKING + MEDIUM"** — weighted toward route + layout stability
> (§13 STABLE at both sub-axes) while acknowledging that contract
> surface (tests + typed API + boundaries + ownership) clearly blocks
> STABLE at the whole-frontend anchor level. PARTIAL + LIGHT was
> deemed too pessimistic given the audit's own evidence of functional
> routing + layout structure.
> Recommendation-strength: **HIGH confidence** (multi-axis
> corroboration from 6 Explore agents + 4-falsifier test SYSTEMIC
> verdict + Rigby SIGN cycle 1 SIGN-with-edits at HIGH confidence).
> Chris D-gate at S2299 close.

**Cross-arc evidence flags (owed to xx99):**
- Group 2400 Auth — silent 401 systemic (§15.5); MINOR two-stage
  cockpit drift (§14.3)
- Group 2500 API — no typed API contract source of truth (Agent 5 F1
  finding, S1505 §15.5 generalized); no error boundaries (§15.4)
- Group 2600 PA — GlobalPADock visibility route-coupling (§14.5);
  PA-adjacent 3-surface documentation gap (§17.2)
- Group 1300 Memory / 1600 Content / 1800 HumanAttention — content
  standalone-vs-workspace surface overlap (§17.1); render-authority
  split framing per S2200 §7.1 (workspace tab handoff already
  designed)

### 20.7 Rigby SIGN fold notes

**Rigby SIGN cycle 1 result: SIGN-with-edits at HIGH confidence** via
dedicated fresh SIGN isolation pin `pa-8d60e999e01c40e4` (minted at
draft-complete via `session_tool.create_fresh` per playbook §15
SIGN-isolation discipline; will retire at cycle close via
`session_tool.retire`). **4 batches × 5 questions = 20 total Q; 19
folds landed pre-commit-gate.** Cycle 2 NOT required per Rigby cycle-1
HIGH confidence + all folds landable.

**Cadence per feedback_rigby_sign_worker_instability_recovery** — 4×5
batching per historical 20-section audit shape (TENTH-consecutive
formal SIGN cycle under Research OS after S1301+S1401+S1501+S1601+
S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104 + S2200 parent scoping
= this is the 14th SIGN cycle in the arc-parent-with-children pattern).

**19 folds by batch:**

- **Batch 1 (Q1-Q5): framing + severity calibration.**
  - **Q1 CLEAN + micro-fold** — §14.1 F1 route-count delta reclassified
    `observation` (inventory semantics delta), NOT `drift`.
  - **Q2 STRENGTHEN** — §15.2 F2 god-component severity tightened:
    severity scales by blast radius + churn + defect history, not by LOC
    alone. HIGH baseline; CRITICAL for CommandCenterPage + BettingPage.
  - **Q3 STRENGTHEN** — §15.1 F3 zero-test-coverage downgraded CRITICAL
    → HIGH baseline + CRITICAL for payments / auth / billing / betting /
    ledger-like surfaces. Single-operator caveat added.
  - **Q4 STRENGTHEN** — §18.1 F4 CODEOWNERS-absent downgraded CRITICAL
    → HIGH with single-operator caveat.
  - **Q5 CLEAN + micro-fold** — §14.2 F5 legacy sub-tab enum
    reclassified `legacy_compatibility_debt`, NOT `drift`.
- **Batch 2 (Q6-Q10): 4-falsifier + criteria scoring.**
  - **Q6 STRENGTHEN** — §1 F1 composite %-rate replaced with per-axis
    rubric (denominators independent: test files vs pages vs api-
    modules); labeled as "violation-index" not "violation rate."
  - **Q7 STRENGTHEN** — §1 F2 tagged **PENDING-CHILD-B-CONFIRMATION**
    with explicit Child A vs Child B scope statement.
  - **Q8 STRENGTHEN** — §1 F4 SYSTEMIC verdict hedged with "no evidence
    found in sampled surfaces" language; sampling scope acknowledged.
  - **Q9 FOLD** — §1 Criterion 1 UNMET → **PARTIAL** (route ownership
    map exists in App.tsx; what is UNMET is the declared durable
    contract source-of-truth).
  - **Q10 FOLD** — §1 Criterion 5 UNMET → **PARTIAL** (6 of 38 pages
    god-components; 32 below threshold — criterion violated in aggregate
    but not uniform failure).
- **Batch 3 (Q11-Q15): Child E + cross-arc coordination.**
  - **Q11 STRENGTHEN** — §15.2 surface attribution reframed: surface =
    top-level product area; 3 Command-Center pages counted as multiple
    loci within one surface, not 3 separate surfaces. Trigger MET across
    4 top-level product surfaces.
  - **Q12 CLEAN** — §15.2 workspace tab god-components labeled "intra-
    route tab components" as supplement not trigger-critical; Child E
    trigger met on page-level alone.
  - **Q13 STRENGTHEN** — §15.5 silent-401 severity reframed: HIGH at
    frontend-symptom scope; systemic-severity classification pending
    Group 2400 Auth spec. Language softened from "systemic default" to
    "frontend default behavior + cross-arc dependency."
  - **Q14 STRENGTHEN** — no new §14 drift entry for API types;
    dependency note added inline; Child C S2203 owns the full audit.
  - **Q15 FOLD** — §17.2 PA-adjacent overlap reframed from
    DIFFERENT-CONCERNS to **PARTIAL-DUPLICATE / intentional multi-locus**
    with Group 2600 PA consolidation-decision handoff.
- **Batch 4 (Q16-Q20): anti-scope + posture + verdict.**
  - **Q16 STRENGTHEN** — §14.5 GlobalPADock recommendation reframed as
    option-space (route metadata / layout-level feature flag /
    centralized visibility policy); concrete PA implementation deferred
    to Group 2600.
  - **Q17 FOLD** — §20.6 POSTURE-DECISION committed to single
    recommendation: **WORKING + MEDIUM** (route + layout STABLE; contract
    surface blocks whole-frontend STABLE; PARTIAL + LIGHT deemed too
    pessimistic).
  - **Q18 STRENGTHEN** — §19 R1/R2 ordering: R2 leads execution
    sequence; R1 parallel gating safety track. Deep refactors deferred
    until minimal test harness exists.
  - **Q19 CLEAN + micro-fold** — §14.6 betting-tab-count doc drift
    labeled "handoff note, not core audit finding"; tracked by
    doc-cascade + verify_doc_claims discipline.
  - **Q20 verdict** — **SIGN-with-edits at HIGH confidence.** Minimum
    edits pre-commit-gate: Q1/Q2/Q3/Q4/Q5/Q6/Q7/Q8/Q9/Q10/Q11/Q13/Q15/Q17/
    Q18 folds landed via targeted edits above. Q12/Q14/Q16/Q19 micro-
    folds absorbed inline. Critical residuals: none blocking SIGN.
    Confidence rationale: issues were calibration + rubric-math + scope-
    guarding, not foundational errors.
