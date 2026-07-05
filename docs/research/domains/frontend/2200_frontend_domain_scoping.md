---
title: "Frontend Domain Scoping (Group 2200 — The Contract-Surface Arc)"
session: 2200
status: active (formal S2200 arc-open 2026-07-05 post-S2199 Group 2100 close; Chris D-override at S2199 close "agree all + (6)=(a) Group 2200 Frontend" 2026-07-05 ratified Frontend over any playbook §22 default queue lean, per post-S2099 project memory queue ranking: 2200 Frontend / 2300 Mobile / 2400 Auth / 2500 API / 2600 PA)
arc: Research Group 2200 (Frontend — Contract-Surface framing, Chris + Claude conceptual)
category: research (playbook §11.1 parent-scoping template NINTH application)
authors: Claude Code (S2200 arc-open draft 2026-07-05; Chris scope-shape card ratification "agree all" 2026-07-05 locked 4-children + central lens; Rigby SIGN cycle 1 pending)
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                                # runtime counts (Frontend row at §Frontend)
  - docs/PLATFORM_WHAT_IT_IS.md                                               # narrative anchor
  - docs/topics/frontend.md                                                   # subsystem doc pointer (stale-warned)
  - docs/research/platform_architecture_inventory.md                          # S1273 32-domain map row 18 (STABLE + DEEP)
  - docs/research/platform/cross_domain_integration_audit.md                  # S1274 cross-domain integration baseline
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                 # process contract §11.1 NINTH application
  - docs/research/OPEN_ARCS.md                                                # arc manifest (Group 2200 In-progress row at open)
  - frontend/src/App.tsx                                                      # 61 <Route> entries
  - frontend/src/pages/workspace/types.ts                                     # 5 workspace primary tabs enum
  - frontend/src/pages/BettingPage.tsx                                        # 9 betting tabs + 3,023-line god-component (S1505 §15.4)
  - frontend/src/pages/CommandCenterPage.tsx                                  # Command Center + PA chat integration
  - frontend/src/pages/WorkspacePageNew.tsx                                   # 5-tab modular workspace
delegated_from:
  - Group 1500 Sports S1505 §14.1 (`/ws/dbao/` MOCK-DATA-CONSUMER pattern), §14.3 (auth-drift two-sided framing), §14.5 (zero WebSocket subscription despite 3 sports routes registered), §15.5 (MED→HIGH "no API contract source-of-truth"), §15.4 (3,023-line `BettingPage.tsx` god-component)
  - Group 2000+ S2003 §10.3.4 D4 (`ui.render_hint` envelope unadopted across HAI consumer-side; frontend-facing rendering hint disciplined but not enforced)
  - Group 2000+ S2004 §14.6 (Cat F CONSOLIDATION `humanApi` cross-domain sharing at design-posture axis (d))
  - Group 2100 RAG S2099 §14.3.4 (`ui.render_hint` unenforced counter-surface)
  - Group 2100 RAG S2103 P3 §7 (retrieval authority framework — frontend surface for authority-conflict rendering pending T-slot)
  - Group 2100 RAG S2104 P4 §17.3 §20.1 (retrieval-surface counter operator-surface — Group 1700 cross-arc coordination flag)
delegates_to:
  - (arc-close will populate)
lens: >
  Central lens question (Chris-locked "agree all" 2026-07-05):
  "Is the frontend a governed contract surface with disciplined data
  flow, or an accreted UI mesh where routes / consumers / state / API
  calls have grown without a shared boundary policy?"
playbook_application: §11.1 20-section parent-scoping template NINTH application per S2199 canonical summary handoff line 100 (prior applications across arcs Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100 per exemplar chain; the S2100 parent scoping frontmatter noted itself as EIGHTH §11.1 application, implying one of the prior arcs skipped §11.1 template — specific skipped-arc identification is out-of-scope for S2200 open and can be resolved at S2299 close if load-bearing); §14 verifier-loop REQUIRED CODIFICATION-CONFIRMED discipline applied pre-draft; §15 SIGN cycle 1 REQUIRED at parent scoping — routed via dedicated fresh isolation pin `pa-7e056489aecf4b7e` (NOT arc pin `pa-f7fd5016600f4513`) per playbook §15 SIGN-isolation discipline; §16 arc pin: `pa-f7fd5016600f4513` ACTIVE at S2200 open per TENTH formal arc (Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100 prior = 9 arcs); prior `pa-18b095bb7c4740be` retired at S2199 close (Group 2100 RAG — retired=true via session_tool.retire per playbook §16 arc-close discipline)
arc_open_provenance:
  - Chris D-override at S2199 close 2026-07-05 ratified Group 2200 = Frontend via "agree all + (6)=(a) Group 2200 Frontend" over post-S2099 draft queue (2200 Frontend / 2300 Mobile / 2400 Auth / 2500 API / 2600 PA per project_2100_plus_queue_ranking.md draft)
  - S2200 parent scoping shape-card presented to Chris 2026-07-05 with (a) 4-children lean folding P5 component/page/layout patterns into C1 route+page inventory + (b) central lens question draft; Chris "agree all" 2026-07-05 ratified 4-children + central lens verbatim
  - Arc pin `pa-f7fd5016600f4513` minted at S2200 open via `session_tool.create_fresh` — TENTH formal arc pin (health_check score=100 recommendation=continue turn_count=1 at open)
  - `tools/pa_local.sh:225` rotated to new pin + header ledger updated with S2199 retirement (pa-18b095bb7c4740be) + S2200 open (pa-f7fd5016600f4513) stanzas per S1900/S2000/S2100 documentation pattern
  - Draft written 2026-07-05 post-scope-card ratification; Rigby SIGN cycle 1 REQUIRED pre-commit per playbook §15
---

# Group 2200 — Frontend Domain Scoping (The Contract-Surface Arc)

> **ACTIVE.** Formal S2200 arc-open executed 2026-07-05 post-S2199 Group 2100
> RAG / Document Loading (Knowledge Loop) canonical summary close per Chris
> D-override ratification "agree all + (6)=(a) Group 2200 Frontend"
> 2026-07-05. Group 2200 arc pin `pa-f7fd5016600f4513` minted at open via
> `session_tool.create_fresh`. Rigby SIGN cycle 1 REQUIRED on this parent
> scoping per playbook §15.

> **Central lens question (Chris-locked "agree all" 2026-07-05):**
>
> *"Is the frontend a governed contract surface with disciplined data
> flow, or an accreted UI mesh where routes / consumers / state / API
> calls have grown without a shared boundary policy?"*
>
> **Contract-surface acceptance criteria** (Rigby SIGN cycle 1 Q3
> STRENGTHEN 2026-07-05 folded 6th criterion — failure-mode /
> boundary behavior discipline; original 5 preserved verbatim):
> 1. Every route in `App.tsx` maps to an owned page + layout with a
>    declared consumer contract (props / hooks / API surface)
> 2. Every WebSocket consumer emits envelopes conforming to a shared
>    schema (`ui.render_hint` envelope adoption)
> 3. Frontend↔backend API calls are enumerated + typed against a
>    single source of truth (S1505 §15.5 debt closed)
> 4. Session-scoped state has a declared persistence discipline
>    (localStorage / sessionStorage / server-round-tripped) per surface
> 5. Component / page / layout boundaries are visible + navigable —
>    no god-component pathologies (S1505 §15.4 `BettingPage.tsx`
>    3,023-line pattern extinct)
> 6. Failure-mode + boundary behavior is disciplined and consistent —
>    loading / error states, error boundaries, and auth-failure
>    handling (e.g., "silent 401" per S1505 §14.4) are standardized
>    and observable (SIGN Q3 Option A fold; the doc's C output
>    §5 explicitly measures "silent-401 discipline rate")

> **Arc frame (Chris + Claude *conceptual* framing, NOT inherited canonical
> doctrine):** Group 2200 is framed as the **Contract-Surface arc**.
>
> The proposed conceptual framing:
> - **Group 1500 Sports Cat E S1505 = surface-level UI audit** —
>   documented that BettingPage is 3,023 lines with 2 DEAD-RENDER-PATH
>   tabs + MOCK-DATA-CONSUMER on `/ws/dbao/` + AUTH-DRIFT
> - **Group 2000+ S2003 §10.3.4 D4 + S2099 §14.3.4 = envelope adoption
>   gap** — HAI event consumer-side lacks `ui.render_hint` envelope
>   enforcement
> - **Group 2200 = whole-frontend contract lens (proposed)** — is
>   the frontend one governed surface with disciplined data flow, or
>   accreted mesh?
>
> **Contract-surface rubric (parent scoping proposal — Rigby SIGN cycle 1
> Q1 pressure test):**
> - **Route Contract** = every route owns a page + layout + declared
>   consumer surface
> - **Envelope Contract** = every consumer emits schema-conformant
>   render hints
> - **API Contract** = every backend call has a typed source-of-truth
> - **State Contract** = every persistent surface declares its
>   persistence discipline
>
> Not just component cleanup. The framing is: *does the frontend behave
> as one contract surface, or has it grown without a shared boundary
> policy that would let a future edit be safe?*

> **Conceptual model (Chris + Claude proposal 2026-07-05):**
>
> ```
> Routes  → Pages → Layouts → Components  (structural axis)
>    │        │        │           │
>    ▼        ▼        ▼           ▼
> State  ←  API  ←  Envelope  ←  Consumer  (data-flow axis)
> ```
>
> - **Structural axis** — how the URL maps to visible UI
> - **Data-flow axis** — how data crosses the backend↔frontend boundary
>   and threads through consumers → envelopes → API → state
> - **Contract Surface** — where a shared boundary policy applies to
>   BOTH axes so that a future edit knows what it can and can't change

---

## 1. Why Phase 0

The frontend has never been the subject of a dedicated research arc under
the Research OS (Groups 1300-2100). It has been *touched* by prior arcs
but always as a downstream consumer:

- **Group 1500 Sports S1505** audited Cat E Sports Frontend Surface —
  scope was `/betting` route + `BettingPage.tsx` only. Findings
  documented: MOCK-DATA-CONSUMER `/ws/dbao/`, DEAD-RENDER-PATH
  markets/bankroll tabs, AUTH-DRIFT at 2 endpoints, zero WebSocket
  subscription despite 3 routes registered, 3,023-line god-component,
  zero test coverage, zero client-side state persistence, no
  CODEOWNERS. Verdict: PARTIAL / mixed. But the audit was ONE route
  slice; no cross-route pattern claim was made.
- **Group 2000+ S2003 §10.3.4 D4 + S2099 §14.3.4** flagged
  `ui.render_hint` envelope discipline as spec-complete but
  runtime-unenforced across the HAI event consumer-side. The frontend
  consumers exist; the envelope contract does not gate what they
  render.
- **Group 2100 RAG S2103 §7 + S2104 §17.3 §20.1** flagged
  retrieval-surface counter operator-surface + retrieval authority
  conflict rendering as pending T-slot work. Frontend surface implicated
  but not audited.

**Three converging signals** across the prior 9 arcs suggest the
frontend has drift the individual arcs could see but not diagnose
whole-cloth:

1. **Route sprawl.** PLATFORM_INVENTORY confirms 61 routes in
   `App.tsx`. No arc has enumerated route ownership, layout parent,
   or consumer contract. S1505 documented ONE route (`/betting`); the
   other 60 are un-audited under this lens.
2. **Consumer surface sprawl.** ~33+ WebSocket consumer classes are
   registered in various `routing.py` files across `core/`,
   `sports/`, `intelligence/`, `discord/`, etc. Whether the frontend
   *subscribes* to them, *reads* them, or *ignores* them (S1505
   §14.5 zero-subscription-despite-3-routes) is unknown at the
   whole-frontend level.
3. **State + API discipline drift.** S1505 §15.5 elevated "no API
   contract source-of-truth" from MED to HIGH structural debt as a
   *parent cause* behind AUTH-DRIFT + read-path fragility. S1505
   §15.4 documented zero client-side state persistence. Both
   findings were single-route; whether the pattern holds across the
   60 other routes is undetermined.

**The Phase 0 question** this arc answers: *Is the frontend already a
governed contract surface (in which case documenting the contract
suffices), or has it accreted without a shared boundary policy (in
which case the arc's output is a POSTURE-DECISION brief on how to
introduce one)?*

**What Phase 0 does NOT do:**
- Fix any of the findings. The arc is research + design-preparation
  only.
- Refactor `BettingPage.tsx` or any god-component.
- Introduce a new frontend framework or migrate to Next.js.
- Design the mobile app (Group 2300).
- Design auth (Group 2400).
- Design the backend API contract (Group 2500).

---

## 2. What existing inventory already tells us

Inputs pre-arc-open (context-kit runtime anchors + prior arc findings):

### 2.1 Runtime anchor (PLATFORM_INVENTORY §Frontend, 2026-07-02)

| Surface | Count | Source |
|---|---|---|
| App.tsx `<Route>` entries | **61** | `frontend/src/App.tsx` |
| Workspace primary tabs | **5** | `frontend/src/pages/workspace/types.ts` (home, work, build, intelligence, system) |
| Betting dashboard tabs | **9** | `frontend/src/pages/BettingPage.tsx` (hub, games, top_plays, sharp, arbitrage, watching, odds, wagers, records) |

### 2.2 32-domain map (S1273 platform_architecture_inventory row 18)

> **Frontend / Workspace UI** — React + Vite; 61 routes; 5-tab
> workspace (S1100); Command Center "Now" Hub (S931). **Maturity:
> STABLE. Depth: DEEP.**

The STABLE + DEEP posture claim needs pressure-testing. S1505 §14.5
found `/ws/dbao/` MOCK-DATA-CONSUMER — the surface *renders* stably
but is *disconnected* from real data. STABLE-at-render does not
imply STABLE-at-contract. This is a load-bearing Rigby SIGN pressure
question.

### 2.3 Narrative anchor (docs/topics/frontend.md — stale-warned)

`docs/topics/frontend.md:1` carries the DOC-POINTER-V1 stale warning
banner. The doc names: 5 workspace tabs post-S1100 (was 9), 61
routes, Command Center Now Hub (3-panel strip), Intelligence Desks
Panel (S1000, 4-card grid), PA integration (`GlobalPADock`
floating overlay + `CommandCenterPage` + `AssistantPage`), page
telemetry (`usePageTracking` hook + `POST
/api/v1/telemetry/page-view/`), Betting Dashboard (9 tabs). No
mention of: WebSocket subscription hygiene, state persistence
discipline, API contract source-of-truth, `ui.render_hint` envelope
adoption.

### 2.4 S1505 Cat E findings (Group 1500 Sports) — HYPOTHESIS status

**Rigby SIGN cycle 1 Q8 STRENGTHEN 2026-07-05 fold — S1505 supplies
*prior evidence* that contract drift exists; Cycle 1 Child audits
will test whether this drift is (i) sports-domain outlier, (ii)
surface-localized, or (iii) systemic.** The 11 load-bearing
single-route findings below are treated as a HYPOTHESIS to be
falsified or generalized, NOT as inherited findings.

**Falsifier criteria (Child audits must apply):**
- If non-betting surfaces show <20% of routes violating
  route/envelope/API/state contracts → treat S1505 as
  **sports-outlier** and downgrade governance urgency at xx99.
- If B1 subscription-completeness holds outside sports but breaks
  in sports only → classify as **surface-local** (`/betting` and
  `/ws/dbao/`).
- If the "zero Signal Engine emission" pattern (Sports → Signal
  Engine 5-arc pattern per S1505 §14.8) does NOT appear on other
  routes → tag as **domain-specific**.
- If none of the above thresholds are met AND non-betting surfaces
  show similar patterns → S1505 findings are **systemic** and
  Group 2200 xx99 elevates them to whole-frontend governance
  concerns.

Load-bearing single-route findings (`/betting` + `BettingPage.tsx`
scope only):

| Finding | Severity | Class |
|---|---|---|
| `/ws/dbao/` MOCK-DATA-CONSUMER | CRITICAL | New pattern class |
| `markets` + `bankroll` DEAD-RENDER-PATH | HIGH | New pattern class |
| 2 permission-floor inconsistencies (silent 401 on Top Plays / Sharp Action / Arbitrage) | HIGH | Auth |
| SportsBettingBrief write-only-forgotten (§14.3) | HIGH | Data flow |
| Zero WebSocket subscription despite 3 sports routes | HIGH | Consumer surface |
| Zero Cat E → Signal Engine emission (5-arc pattern) | MED-HIGH | Cross-domain |
| 3,023-line god-component | MED | Component boundaries |
| Zero test coverage | HIGH | Test hygiene |
| Zero client-side state persistence | MED | State |
| No CODEOWNERS | MED | Ownership |
| "No API contract source-of-truth" (§15.5 MED→HIGH) | HIGH | API contract |

**Question this arc must answer:** Do these 11 findings generalize
to the other 60 routes, or is `/betting` an outlier?

### 2.5 S2003 + S2099 ui.render_hint envelope findings

`ui.render_hint` envelope was declared as consumer-side render
discipline for HAI event consumers but never enforced. S2099 §14.3.4
carried the finding forward as an unenforced counter-surface. The
frontend consumers *exist* (workspace tabs, Command Center panels,
betting tabs); they *render* HAI events (attention queue, active
work, system pulse per topics/frontend.md §Command Center); the
envelope contract is defined but the frontend does not gate on it.

### 2.6 Cross-domain integration audit (S1274 baseline)

The S1274 audit inventoried the platform's 32 domains + cross-domain
integrations. Row 18 (Frontend / Workspace UI) has cross-domain
consumer paths INTO these upstream domains: Personal Assistant
(chat), HumanAttention (Now Hub), Advisors (Boardroom tab), Content
(Content Studio sub-area), Spider Network (Data Sources),
Intelligence (signal clusters), Sports (BettingPage), Stocks (Hub +
Ticker Lookup + …), Memory (Palace/Learning/Evolution), Body
Systems (System Infrastructure), Discord (limited surface). **The
consumer-set is broad**, but the audit did not measure whether the
frontend enforces contracts on any of those inbound flows.

---

## 3. Candidate subdomain taxonomy

Four child audit slots (Chris-locked "agree all" 2026-07-05), each
targeting one of the four contract-surface rubric axes.

### A — Routes + Pages + Layouts + Component Patterns (S2201 P1)

**Scope.** Enumerate every route in `frontend/src/App.tsx` (61
entries). For each route: identify owned page component + layout
parent + protection wrapper (auth / role) + primary props + data
sources consumed. Identify god-components (>1,000 lines) + name
their internal tab / section structure. Identify duplicate route
patterns (e.g., legacy tab IDs mapped via `normalizeWorkspaceTab()`).

**Central question the audit answers.** *Does every route own its
own page + layout under a shared boundary policy, or has route
composition accreted?*

**Load-bearing signals from prior arcs:**
- S1505 §15.4 documented `BettingPage.tsx` at 3,023 lines with 9
  internal tabs, 2 DEAD-RENDER-PATH.
- topics/frontend.md documents 5-tab workspace + Command Center +
  Now Hub + Intelligence Desks Panel + PA GlobalPADock overlay +
  9-tab betting dashboard. No visible hierarchy governance.
- PLATFORM_INVENTORY row confirms 61 routes but not
  page↔route ownership map.

**Expected output.** 20-section audit doc + POSTURE-DECISION evidence
plan owed to xx99 on: (a) route ownership map (61 rows), (b)
god-component inventory + subdivision cost estimate, (c) layout
parent audit + duplication signals, (d) auth-wrapper hygiene (which
routes are inside `ProtectedRoute`), (e) legacy tab / normalization
paths + deletion candidates.

**Delegates from.** S1505 §15.4 god-component finding; S1273 32-domain
map row 18 STABLE + DEEP posture claim (pressure-test candidate).

### B — WebSocket Consumer Surface + ui.render_hint Envelope (S2202 P2)

**Scope.** Enumerate every WebSocket consumer class registered under
`*/routing.py` (~33+ classes across `core/`, `sports/`,
`intelligence/`, `discord/`, and app-level routing). For each:
identify frontend subscription status (does any React component
`useWebSocket` this route?), envelope schema (does the emit conform
to `ui.render_hint` envelope?), backpressure discipline
(reconnection policy + heartbeat + auth), and MOCK-DATA vs REAL-DATA
posture (S1505 §14.1 `/ws/dbao/` MOCK-DATA-CONSUMER pattern
class).

**Central question the audit answers.** *Do the frontend WebSocket
consumers form a governed envelope surface, or an accreted
subscription mesh with mock-data ghosts?*

**Load-bearing signals from prior arcs:**
- S1505 §14.5 "Zero WebSocket subscription despite 3 sports routes"
  — Cat E frontend does not subscribe to `/ws/sports/*` routes it
  owns.
- S1505 §14.1 `/ws/dbao/` MOCK-DATA-CONSUMER — the consumer emits
  hardcoded fake data.
- S2003 §10.3.4 D4 + S2099 §14.3.4 `ui.render_hint` unenforced —
  envelope contract exists but consumer-side does not gate.
- S2104 §17.3 §20.1 retrieval-surface counter operator-surface —
  frontend WebSocket surface implicated in Group 1700 cross-arc
  coordination.

**Expected output.** 20-section audit doc + POSTURE-DECISION evidence
plan owed to xx99 on: (a) consumer registry (33+ rows), (b)
frontend subscription map (which consumers have React
subscribers), (c) envelope conformance rate (`ui.render_hint` gated
vs ungated), (d) MOCK-DATA-CONSUMER inventory + deletion candidates,
(e) DEAD-CONSUMER inventory (registered backend consumer with zero
frontend subscribers).

**Delegates from.** S1505 §14.1 §14.5; S2003 D4; S2099 §14.3.4;
S2104 §17.3 §20.1.

### C — Frontend↔Backend API Contract + Boundary Discipline (S2203 P3)

**Scope.** Enumerate every backend API call the frontend makes
(REST + WebSocket-initiated). For each: identify calling site
(component + hook + api-module path), typed contract source (or
absence thereof), error handling discipline (silent 401 vs
observable), auth attach method (cookie vs header vs Bearer), and
cross-app-boundary flags (`humanApi` cross-domain sharing per S2004
§14.6 Cat F design-posture axis (d)).

**Central question the audit answers.** *Is the frontend↔backend
API surface a typed contract with a single source of truth, or has
the "no API contract source-of-truth" pattern (S1505 §15.5 MED→HIGH)
generalized across the 61-route surface?*

**Load-bearing signals from prior arcs:**
- S1505 §15.5 "no API contract source-of-truth" MED→HIGH structural
  debt with 4-way parent cause claim (parent behind §14.3 +
  §15.4 + §14.9 + read-path fragility). Single-route scope; needs
  whole-frontend pressure test.
- S1505 §14.3 AUTH-DRIFT two-sided framing.
- S2004 §14.6 Cat F CONSOLIDATION `humanApi` cross-domain sharing.
- topics/frontend.md documents `bettingApi`, `sportsHubApi`,
  `humanApi` as shared Cat F surface but no whole-frontend
  api-module inventory.

**Expected output.** 20-section audit doc + POSTURE-DECISION evidence
plan owed to xx99 on: (a) api-module inventory (bettingApi,
sportsHubApi, humanApi, +N others), (b) typed-contract-source
inventory (which api-module has TS types generated from OpenAPI or
similar), (c) AUTH-DRIFT pattern rate across api-modules, (d)
cross-app-boundary sharing map (which api-module is consumed by
which page), (e) silent-401 vs observable-error discipline rate.

**Delegates from.** S1505 §14.3 §15.5; S2004 §14.6. Cross-arc
coordination flag for future Group 2500 API arc.

### D — Session-scoped State Management + Persistence Discipline (S2204 P4)

**Scope.** Enumerate every persistent state surface the frontend
carries (localStorage, sessionStorage, IndexedDB, cookie,
in-memory-only Zustand/Context stores, server-round-tripped
state). For each: identify persistence discipline (declared vs
accidental), scope (per-user, per-workspace, per-conversation), key
namespace + collision surface, and PA integration (workspace
context store per topics/frontend.md §PA Integration).

**Central question the audit answers.** *Does session-scoped state
have a declared persistence discipline per surface, or does the
"zero client-side state persistence" pattern (S1505 §14.10)
generalize with silent variance across surfaces?*

**Load-bearing signals from prior arcs:**
- S1505 documented zero client-side state persistence at
  `BettingPage.tsx` — 3,023-line component with no persisted
  filter / tab / pagination state.
- topics/frontend.md §PA Integration documents "shared assistant
  context store" with workspace-context resolver but no persistence
  discipline stated.
- topics/frontend.md §Page Telemetry documents fire-and-forget
  Redis counters via `usePageTracking()` hook — a persistent
  side-effect surface counted separately from state.

**Expected output.** 20-section audit doc + POSTURE-DECISION evidence
plan owed to xx99 on: (a) persistent-state-surface inventory (all
localStorage / sessionStorage / IndexedDB / cookie keys touched), (b)
declared-vs-accidental discipline rate, (c) key-namespace collision
audit, (d) PA workspace-context resolver persistence audit, (e)
cross-surface state coupling (does BettingPage state leak into
Command Center or vice versa?).

**Delegates from.** S1505 §14.10. Cross-arc coordination flag for
Group 2600 PA arc.

### Explicit non-candidates

Deliberately EXCLUDED from Group 2200 scope:

- **Mobile app frontend.** Row 19 of the 32-domain map (Mobile App;
  Expo scaffolding; PARTIAL; LIGHT). Deferred to Group 2300 Mobile
  per post-S2099 project memory queue ranking.
- **Auth session + permission model.** Row 22 (Auth / Permissions).
  AUTH-DRIFT observed at consumer sites in C above; the underlying
  auth session + permission model is Group 2400 Auth scope.
- **Backend API design + contract source-of-truth *authoring*.**
  C audit documents the FE side of the "no source of truth" debt;
  fixing it requires backend API design + BE-side typed schema. That
  is Group 2500 API scope.
- **PA chat surface behavior + tool call rendering.** GlobalPADock +
  CommandCenterPage + AssistantPage all render PA responses. The
  behavior + tool-call rendering discipline is Group 2600 PA scope.
- **Discord bot frontend.** No Discord-frontend surface exists on
  the web app; the Discord bot is its own frontend (row 20). Out of
  scope.
- **Fixing findings.** Every audit surfaces findings; none of them
  are fixed inside Group 2200. Findings graduate to T-slot
  post-arc queue at xx99 close.
- **Framework migration.** No Next.js / SSR / Turbopack proposal.
  The React + Vite stack is the baseline the arc audits, not the
  target it proposes to migrate to.

---

## 4. Parent-vs-single recommendation

**Recommendation: PARENT-WITH-4-CHILDREN.**

The 4-axis contract-surface rubric maps 1:1 to 4 child audits.
Attempting the arc as a single audit doc would either:

1. **Ship a shallow scan** across all 4 axes with no
   POSTURE-DECISION evidence plans per axis (defeats the arc
   purpose), OR
2. **Ship one axis deep** and defer the other 3 (equivalent to
   picking one of A/B/C/D as a Group 2200 standalone arc and
   punting the remaining 3 to Group 2201-3 arcs, which the
   Research OS §16 arc-numbering discipline would then treat as
   separate arcs — a bureaucratic mismatch).

**Comparison to prior parent-with-4-children arcs:**

| Arc | Children | Runtime target | Actual |
|---|---|---|---|
| Group 1600 Content | 6 (P1-P6) | 8 sessions | 8 shipped |
| Group 1700 Observability | 6 (P1-P6) | 8 sessions | 8 shipped |
| Group 1800 HumanAttention | 6 (P1-P6) | 8 sessions | 8 shipped |
| Group 1900 Authority Enforcement | 4 (P1+P2+P3+P4/Cat F CONSOLIDATION) | 6 sessions | 6 shipped |
| Group 2000+ Event / Integration | 4 (P1+P2+P3+P4/Cat F CONSOLIDATION) | 6 sessions | 6 shipped |
| Group 2100 RAG | 4 (P1+P2+P3+P4) | 6 sessions | 6 shipped |
| **Group 2200 Frontend (proposal)** | **4 (A+B+C+D)** | **6 sessions** | pending |

**Rigby SIGN cycle 1 Q11 FOLD 2026-07-05 — arithmetic correction.**
The comparison table above shows THREE prior parent-with-4-children
arcs (1900 + 2000+ + 2100), making Group 2200 the **FOURTH-consecutive
parent-with-4-children arc**, not the fifth (S2200 open draft
mis-counted "5th" — the START-HERE doc claim traced to a stale
count baseline; the table is the source of truth). This triggers
**MC-4 4th-arc confirmation**, not the 5th-arc dial-back removal —
the S2199 Q3 STRENGTHEN dial-back ("confidence increased after 4
consecutive parent-with-4-children arcs, but full generalization
remains contingent on one additional confirming arc or a materially
different stress condition") means Group 2200 EXTENDS the
consecutive-count from 3 → 4 at Group 2200 close but DOES NOT
resolve the dial-back trigger; that resolution now requires a
Group 2300+ arc as the 5th confirming arc.

**Runtime target: 6 sessions.**
- S2200 parent scoping (this doc, 1 session)
- S2201 Child A — Routes + Pages + Layouts + Component Patterns (1 session)
- S2202 Child B — WebSocket Consumer Surface + ui.render_hint Envelope (1 session)
- S2203 Child C — Frontend↔Backend API Contract + Boundary Discipline (1 session)
- S2204 Child D — Session-scoped State Management + Persistence Discipline (1 session)
- S2299 xx99 canonical summary (1 session)

**Timebox + sampling rule (Rigby SIGN cycle 1 Q10 STRENGTHEN
2026-07-05 fold — carries runtime discipline while surface sizes
are materially larger than prior 4-child arcs: Child A audits 61
routes, Child C enumerates all api-modules, Child D enumerates all
persistent-state surfaces).** Each child is **timeboxed to 1
session**; where full enumeration threatens runtime, the child may
(i) ship a complete registry skeleton (all rows enumerated at
metadata level) + (ii) apply a documented sampling strategy for
deep inspection (e.g., "audit 10 of 61 routes deeply, tag remaining
51 as skeleton-only pending Child A follow-up or T-slot"), while
still meeting the acceptance criteria evidence needs.

**Runtime cap: 8 sessions** if any child requires a follow-up
audit (per S1904 Cat F CONSOLIDATION precedent). Second-session
escalation requires explicit Chris ratification per playbook §16.

---

## 5. Child mission sequence (Chris-locked "agree all" 2026-07-05)

Sequential execution per playbook §16 arc-standard behavior +
MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails (Group 2200 =
5th-arc extension trigger; single arc pin `pa-f7fd5016600f4513`
retained across all 6 sessions; retired via `session_tool.retire`
at S2299 close per playbook §16 arc-close discipline).

**Per-surface reporting constraint (Rigby SIGN cycle 1 Q1
STRENGTHEN 2026-07-05 fold — carrying forward the 4-axis parent
frame while preventing cross-surface averaging).** Each child audit
MUST report findings **per major surface** (workspace / betting /
command-center / PA) *in addition to* axis-level rollups. Rationale:
S1505 was a single-route slice (`/betting`); its findings surfaced
MOCK-DATA-CONSUMER + DEAD-RENDER-PATH + AUTH-DRIFT patterns that
would be washed out by axis-only reporting across all 61 routes.
Child audits therefore ship two views — the axis-level rollup
(governs the contract rubric) + the per-surface slice (surfaces
variance the rubric would hide). This preserves the 4-axis parent
lens while preventing the "axis abstraction washes out surface
reality" failure mode.

### S2201 — Child A: Routes + Pages + Layouts + Component Patterns

**Load-bearing input:** PLATFORM_INVENTORY §Frontend row (61 routes);
S1505 §15.4 `BettingPage.tsx` god-component; topics/frontend.md
§Route Structure + §Workspace Architecture + §Betting Dashboard.

**Load-bearing output:** Route ownership map (61 rows) + god-component
inventory + layout parent audit + auth-wrapper hygiene + legacy tab
/ normalization deletion candidates.

**Delegates.** POSTURE-DECISION evidence plan §20.6 owed to xx99 on
whether "STABLE + DEEP" (32-domain row 18) posture holds at contract
level.

**Child E spin-out trigger (Rigby SIGN cycle 1 Q4 STRENGTHEN
2026-07-05 fold — carrying forward the 4-child shape while giving
Child A a disciplined escalation path if the god-component pathology
generalizes).** Child E (component-pattern deep dive) is **not**
planned; it is triggered ONLY if Child A finds ≥3 god-components
above threshold (>1,500 LOC OR cyclomatic-complexity proxy signal
per S1505 §15.4 methodology) across ≥2 major surfaces (workspace /
betting / command-center / PA). Otherwise, `BettingPage.tsx` remains
the load-bearing exemplar within Child A's inventory + subdivision
cost estimate. Spin-out decision Chris-gated at S2201 close.

### S2202 — Child B: WebSocket Consumer Surface + ui.render_hint Envelope

**Load-bearing input:** All `*/routing.py` files (~33+ consumer
classes registered); S1505 §14.1 §14.5; S2003 §10.3.4 D4; S2099
§14.3.4; S2104 §17.3 §20.1.

**Load-bearing output (Rigby SIGN cycle 1 Q5 STRENGTHEN 2026-07-05
fold — sub-axes named B1/B2 to expose the orthogonal concerns while
keeping the one-child shape):**
- **B1 — Subscription surface:** consumer registry (33+ rows) +
  frontend subscription map (are we subscribed?) + DEAD-CONSUMER
  inventory (registered backend consumer with zero frontend
  subscribers) + MOCK-DATA-CONSUMER inventory (S1505 §14.1 pattern
  class).
- **B2 — Envelope surface:** `ui.render_hint` envelope conformance
  rate + enforcement-locus recommendation (registration-time vs
  runtime vs defer) — is what we receive conformant?

The two sub-axes are orthogonal (a subscribed consumer can emit
non-conformant envelopes; an unsubscribed consumer's envelope
conformance is moot); both sub-axes are required for the Child B
T0/Gate measurement bundle per D8.

**Delegates.** POSTURE-DECISION evidence plan §20.6 owed to xx99 on
whether `ui.render_hint` envelope should be enforced at consumer
registration time vs runtime vs left unenforced.

### S2203 — Child C: Frontend↔Backend API Contract + Boundary Discipline

**Load-bearing input:** All api-modules under `frontend/src/api/*` +
component-level fetch/axios call sites; S1505 §14.3 §15.5; S2004
§14.6.

**Load-bearing output:** api-module inventory + typed-contract-source
inventory + AUTH-DRIFT pattern rate + cross-app-boundary sharing
map + silent-401 discipline rate.

**Delegates.** POSTURE-DECISION evidence plan §20.6 owed to xx99 on
whether the "no API contract source-of-truth" S1505 §15.5 debt
generalizes across all api-modules or is `/betting`-specific;
cross-arc coordination flag to future Group 2500 API arc.

### S2204 — Child D: Session-scoped State Management + Persistence Discipline

**Load-bearing input:** All localStorage / sessionStorage / cookie /
IndexedDB / Zustand-context-store touchpoints; PA workspace-context
resolver per topics/frontend.md §PA Integration; S1505 §14.10.

**Load-bearing output:** Persistent-state-surface inventory +
declared-vs-accidental discipline rate + key-namespace collision
audit + PA workspace-context resolver persistence audit +
cross-surface state coupling map.

**Delegates.** POSTURE-DECISION evidence plan §20.6 owed to xx99 on
whether per-surface persistence discipline should be introduced as a
frontend convention or handled at backend/PA layer; cross-arc
coordination flag to future Group 2600 PA arc.

### S2299 — xx99 Canonical Summary

**Load-bearing input:** All 4 child audits + S2200 parent scoping.

**Load-bearing output:** 12-section playbook §11.3 canonical summary
+ §10 meta-methodology retrospective (TENTH application after S1399
first + S1499 second + S1599 third + S1699 fourth + S1799 fifth +
S1899 sixth + S1999 seventh + S2099 eighth + S2199 ninth); MC-4
CODIFICATION-CONFIRMED 5th-arc extension trigger (S2199 dial-back
resolves at Group 2200 close per Q3 STRENGTHEN fold).

**Runtime target: 1 session** per canonical-summary shape.

---

## 6. Parked candidate issues

Issues surfaced during parent scoping that are not blocking S2200
arc-open but should be flagged in xx99:

- **Q6.1 — Should god-component subdivision be included as a
  POSTURE-DECISION evidence plan output in Child A?** Current lean
  (§3 Child A): yes, subdivision cost estimate + prioritized
  candidate list. Rigby SIGN cycle 1 pressure candidate.
- **Q6.2 — Should DEAD-RENDER-PATH be a new pattern class in Child
  A (following S1505 §14.2 introduction)?** Current lean: yes,
  extend the pattern-class taxonomy started in S1505 Cat E across
  Child A route inventory. This is Rigby SIGN cycle 1 Q4 pressure
  candidate.
- **Q6.3 — Is the "no CODEOWNERS" pattern (S1505 §14.11) worth
  auditing across the frontend as a cross-child concern rather than
  a single-child concern?** Current lean: fold into Child A §20.6
  ownership audit; do not create a separate child.
- **Q6.4 — Should page-telemetry `usePageTracking()` (fire-and-forget
  Redis counter) be audited under Child B (consumer surface) or
  Child D (persistence)?** Current lean: Child D (side-effect
  persistence surface, not envelope consumer). **Rigby SIGN cycle 1
  Q6 CLEAN 2026-07-05 + optional micro-fold:** Child B remains
  WS/envelope-only; non-WS FE→BE emissions (page-telemetry POSTs,
  fire-and-forget REST counters) are treated as persistence
  side-effects under Child D. Broadening Child B to "any FE→BE
  emission surface" would ripple into scope creep and disrupt the
  4-children shape Chris-ratified.
- **Q6.5 — Does the arc need a Category F (CONSOLIDATION) child
  following S1904 + S2004 + S2104 3-arc pattern?** Current lean:
  DEFER decision to xx99. If S2201-S2204 surface enough cross-child
  patterns to justify CONSOLIDATION, S2299 can propose it and Chris
  can ratify or reject. If not, the arc closes at 6 sessions per
  runtime target.
- **Q6.6 — Should the `ui.render_hint` envelope adoption gap
  (S2003 D4 + S2099 §14.3.4) surface as a T0/Gate at Child B or as
  a T1 post-arc T-slot?** Current lean: T0/Gate — the envelope
  contract predates Group 2200 and its adoption is a live
  cross-arc concern; T0/Gate framing aligns with S1900 R.EVENTS
  discipline. **Rigby SIGN cycle 1 Q2 STRENGTHEN 2026-07-05 fold —
  gate semantics clarified:** T0/Gate at Child B = **must produce**
  (a) consumer registry + (b) subscription map + (c) envelope
  conformance measurement rate + (d) recommendation on enforcement
  locus (registration-time vs runtime vs defer). T0/Gate is a
  **decision + measurement gate**, NOT an **implementation gate** —
  no envelope schema authorship + no enforcement wiring during the
  arc, per §7 anti-scope ("No new envelope schema", "No fixes").
  This aligns T0/Gate with the arc's research-only posture while
  keeping the constraint operationally coherent.

---

## 7. Anti-scope

**Governing principle (Rigby SIGN cycle 1 Q7 STRENGTHEN 2026-07-05
fold — preamble tightening).** This arc is **contract-surface
governance**, not cross-domain product design. Where the frontend
touches other domains, Child audits record *interfaces* and emit
*handoff flags* only. Authorship of other-group specs (BE canonical
API shapes, auth session model, PA behavior redesign) is out-of-arc
regardless of how directly the FE touches those surfaces.

Explicit anti-scope declarations to prevent scope creep during
child audits:

- **No fixes.** All 4 child audits are read-only research +
  design-preparation. Zero PRs merged during S2201-S2204 targeting
  the findings surfaced.
- **No god-component refactor.** Child A can propose a subdivision
  cost estimate + candidate list; it does NOT refactor
  `BettingPage.tsx` or any component.
- **No new envelope schema.** Child B measures adoption of the
  EXISTING `ui.render_hint` envelope; it does NOT propose a new
  schema or extend the existing one.
- **No new API contract source-of-truth.** Child C measures the
  absence of a source-of-truth; the design of one is Group 2500 API
  scope.
- **No new state persistence framework.** Child D measures the
  discipline gap; the design of a shared persistence framework
  (Zustand-with-persistence, jotai, react-query cache, etc.) is
  post-arc T-slot.
- **No framework migration proposal.** React + Vite remains the
  baseline; migration to Next.js / Remix / Turbopack is not on the
  Group 2200 table.
- **No mobile app.** Row 19 stays deferred to Group 2300.
- **No PA behavior audit.** Group 2600 PA scope.
- **No auth session model.** Group 2400 Auth scope.
- **No backend API design.** Group 2500 API scope.

### 7.1 Scope guardrails by leak vector (Rigby SIGN cycle 1 Q7 STRENGTHEN 2026-07-05 fold)

Concrete per-leak-vector guardrails covering the five risk vectors
between Group 2200 and adjacent arcs:

- **Child C → Group 2500 API guardrail.** We may *inventory FE
  call-sites* (paths, verbs, headers, params) but MUST NOT propose
  or define canonical API shapes. Any "should be" API contract
  belongs to Group 2500. Output is *evidence only* + a handoff note.
- **Child C → Group 2400 Auth guardrail.** We may record *symptoms*
  (401 patterns, auth drift behavior as observed in FE) but MUST
  NOT infer or specify the auth/session model (token refresh,
  cookie strategy, identity lifecycle, permission floor). Any auth
  model narrative is Group 2400.
- **Child A/D → Group 2600 PA guardrail.** PA UI components +
  workspace-context resolver persistence are treated as **render
  surfaces only**: structure, boundaries, state ownership. NO
  behavioral product spec for PA features, NO UX redesign
  proposals. Product behavior belongs to Group 2600.
- **Child A/B/D → Group 1300 Memory + 1600 Content + 1800
  HumanAttention render-authority split** (Rigby SIGN cycle 1 Q9
  STRENGTHEN co-fold). Group 2200 owns **render-surface contracts**
  (routes, state boundaries, envelope discipline, typed calls).
  Domain groups own **semantic authority** (what memory means,
  what content is ready, what HAI decisions are eligible). Child
  audits document the render surface + hand off semantic authority
  questions to the owning domain arc. Explicit render-authority
  handoff flags to emit at Child A/B/D:
    - **G1300 Memory** — memory palace / learning / evolution
      render surface (per topics/frontend.md §Workspace Architecture
      row 6); render-shape is Group 2200, semantic-shape is Group
      1300.
    - **G1600 Content** — Content Studio sub-area (Content, Blogs,
      Podcasts, Calendar, Dossiers, Voices, Files, Campaigns,
      Deliverables); render-shape is Group 2200, publish/deliverable
      lifecycle is Group 1600.
    - **G1800 HumanAttention** — Now Hub Attention Queue + Active
      Work + System Pulse panels + Boardroom decision surface;
      render-shape is Group 2200, envelope adoption gap is D8
      T0/Gate at Child B, but decision eligibility + auto-approve/
      escalate semantics remain Group 1800.
- **Group 2300 Mobile.** Out-of-tree; excluded. Expo scaffolding
  (row 19) is Group 2300 scope; no mobile-adjacent audit output
  during Group 2200 children.

---

## 8. Decisions recorded (Chris-locked "agree all" 2026-07-05)

**D1.** Group 2200 = Frontend arc per Chris D-override at S2199
close 2026-07-05 ("agree all + (6)=(a) Group 2200 Frontend").
Post-S2099 project memory queue ranking (2200 Frontend / 2300
Mobile / 2400 Auth / 2500 API / 2600 PA) partially advanced —
2200 Frontend now In-progress, 2300-2600 still queued.

**D2.** Central lens question (verbatim Chris-locked 2026-07-05):
*"Is the frontend a governed contract surface with disciplined data
flow, or an accreted UI mesh where routes / consumers / state / API
calls have grown without a shared boundary policy?"*

**D3.** 4-children shape (Chris-locked "agree all" 2026-07-05):
- Child A — Routes + Pages + Layouts + Component Patterns
- Child B — WebSocket Consumer Surface + ui.render_hint Envelope
- Child C — Frontend↔Backend API Contract + Boundary Discipline
- Child D — Session-scoped State Management + Persistence Discipline

Component/page/layout patterns folded into A (not split as C5) per
scope-shape card option (a).

**D4.** Runtime target: 6 sessions (S2200 parent + S2201-4 children +
S2299 xx99). Runtime cap: 8 sessions (only invoked with explicit
Chris ratification per playbook §16).

**D5.** Arc pin: `pa-f7fd5016600f4513` retained across all 6
sessions per playbook §16 arc-standard behavior + MC-4
CODIFICATION-CONFIRMED with 5th-arc extension confirmation candidate.

**D6.** MC-4 4th-arc confirmation (Rigby SIGN cycle 1 Q11 FOLD
2026-07-05 arithmetic correction — original draft claimed 5th-arc
extension; §4 table shows 3 prior 4-child arcs (1900 + 2000+ +
2100), making Group 2200 the FOURTH-consecutive, not fifth).
Group 2200 EXTENDS the MC-4 CODIFICATION-CONFIRMED consecutive-count
from 3 → 4 at Group 2200 close. S2199 Q3 STRENGTHEN dial-back
resolution ("contingent on 5th arc or materially different stress
condition") does NOT resolve at Group 2200 close — that resolution
now requires a Group 2300+ arc as the 5th confirming arc. Chris
"agree all" 2026-07-05 was against the 5th-arc framing in the
scope-shape card; the FOLD downgrades to 4th-arc confirmation per
table arithmetic — surfaced to Chris in the close-card for
ratification adjustment.

**D7.** Anti-scope declarations §7 Chris-ratified via "agree all" —
no fixes, no god-component refactor, no new envelope schema, no new
API source-of-truth, no new state framework, no framework
migration, no mobile / PA / Auth / API cross-arc scope leaks.

**D8.** ui.render_hint envelope adoption gap (Q6.6): T0/Gate at
Child B **as a decision + measurement gate** (NOT an implementation
gate) per Rigby SIGN cycle 1 Q2 STRENGTHEN 2026-07-05 fold. Child B
T0/Gate requires **both B1 + B2 sub-axis measurements** per Q5
STRENGTHEN 2026-07-05 fold: B1 = consumer registry + frontend
subscription map + DEAD-CONSUMER + MOCK-DATA-CONSUMER inventory; B2
= envelope conformance rate + enforcement-locus recommendation. No
envelope schema authorship or enforcement wiring during the arc per
§7 anti-scope. Chris-ratifiable at S2202 close if enforcement-locus
recommendation shifts.

**D9.** Cat F CONSOLIDATION deferral (Q6.5): DEFER decision to xx99.
Chris-ratified via "agree all" (default lean accepted).

**D10.** Parent scoping SIGN routing per playbook §15: dedicated
fresh isolation pin (NOT arc pin `pa-f7fd5016600f4513`) minted at
draft-complete for Rigby SIGN cycle 1. Batching per
feedback_rigby_sign_worker_instability_recovery: 4 batches × 3-Q
cadence = 12 total questions to preempt worker instability.

---

## 9. Next step

**S2200 (this session) — parent scoping ratification + arc-open
cascade:**

1. ✅ Mechanical arc-open (verified `service_context: local` + minted
   fresh arc pin `pa-f7fd5016600f4513` + rotated `tools/pa_local.sh`
   + end-to-end ping through new pin confirmed).
2. ✅ Scope-shape card ratified by Chris "agree all" 2026-07-05
   (4-children + central lens question verbatim).
3. ✅ Parent scoping doc drafted (this doc, `status: active` on
   draft ship — status flips to `active-post-Rigby-SIGN` after
   fold; `active-post-Chris-ratification` after commit-gate).
4. **→** Route Rigby SIGN cycle 1 on this parent scoping via
   dedicated fresh isolation pin. 4-batch × 3-Q cadence per
   feedback_rigby_sign_worker_instability_recovery. Q1-Q12
   candidates below.
5. **→** Fold STRENGTHEN / CLEAN / REJECT verdicts pre-commit.
6. **→** Chris close-card ratification (6-item shape following
   S2199 pattern: seam framing + child sequence + T-slot queue
   + meta-methodology milestone updates + arc-close cascade
   sequence + implicit MC-4 5th-arc extension acceptance).
7. **→** Arc-open cascade: OPEN_ARCS §In-progress row for Group
   2200 + §Recent reconciliations entry; ARCHITECTURE_INDEX v76 →
   v77 with §1.80 registration + §3 domain map row 18 arc-frame
   note + §8 timeline S2200 row; 00-START-NEXT-SESSION.md
   overwrite with S2201 first-child priorities; SESSION_2200
   handoff; 4-step docs cascade per
   feedback_docs_cascade_at_every_close.

**S2201 (next session) — Child A: Routes + Pages + Layouts + Component
Patterns:**

Per playbook §11.2 20-section audit template. Six parallel Explore
sub-agents per playbook §13 + parent-Claude verifier-loop per §14.
Load-bearing output: 61-row route ownership map + god-component
inventory + layout parent audit + auth-wrapper hygiene + legacy tab
deletion candidates. POSTURE-DECISION evidence plan §20.6 owed to
xx99 on "STABLE + DEEP" 32-domain-row-18 posture pressure test.

**Rigby SIGN cycle 1 Q1-Q12 pressure test candidates for this doc:**

*Batch 1 (Q1-Q3): Framing + rubric*
- **Q1** — Is the Contract-Surface framing (§4 rubric axes) valid
  as a whole-frontend organizing lens, or should the frontend be
  audited per-surface (workspace / betting / command-center) rather
  than per-axis?
- **Q2** — Does the `ui.render_hint` envelope T0/Gate framing
  (Q6.6 + D8) survive scrutiny, or is it T1 post-arc T-slot?
- **Q3** — Do the 5 contract-surface acceptance criteria (§lens
  block) enumerate correctly, or is there a hidden 6th (e.g.,
  test coverage floor, CODEOWNERS discipline, accessibility
  baseline)?

*Batch 2 (Q4-Q6): Child scope*
- **Q4** — Is folding P5 component/page/layout patterns into
  Child A defensible (option (a) of the scope-shape card), or
  does the 3,023-line `BettingPage.tsx` pathology warrant a
  dedicated Child E?
- **Q5** — Does Child B (WebSocket + envelope) merge two
  distinguishable concerns that should split (subscription
  discipline vs envelope discipline)?
- **Q6** — Does Child D (state + persistence) cover fire-and-forget
  page-telemetry (Q6.4) or should that be Child B (side-effect
  emission surface)?

*Batch 3 (Q7-Q9): Anti-scope + cross-arc*
- **Q7** — Are §7 anti-scope declarations tight enough to prevent
  scope leaks into Group 2300 Mobile / 2400 Auth / 2500 API /
  2600 PA during S2201-S2204?
- **Q8** — Do the S1505 §14 findings generalize claim (§2.4 + §3
  Child A/B/C/D load-bearing signals) survive Rigby's grep-verify
  against `/betting` outlier hypothesis?
- **Q9** — Does the cross-arc coordination flag map (Group 1700
  observability + Group 2500 API + Group 2600 PA) cover all
  cross-arc handoffs, or are there missed dependencies?

*Batch 4 (Q10-Q12): Verdict + provenance*
- **Q10** — Is the runtime target 6 sessions defensible per prior
  parent-with-4-children arc precedent (1900/2000+/2100 all
  6/6), or is Frontend materially different (higher variance)?
- **Q11** — Does the MC-4 5th-arc extension trigger framing (D6)
  correctly apply per S2199 Q3 dial-back, or is Group 2200 not
  the trigger arc because of scope divergence from prior
  parent-with-4-children arcs (all backend-facing)?
- **Q12** — Overall parent-scoping verdict: SIGN-clean / SIGN-with-
  edits / REJECT? If SIGN-with-edits, minimum edits to land
  before commit-gate?

---

## Appendix — Frontmatter provenance

**Arc pin lineage.**

`pa-f7fd5016600f4513` (Group 2200 Frontend — TENTH formal arc pin
under Research OS after Groups 1300/1400/1500/1600/1700/1800/1900/
2000+/2100 prior). Minted at S2200 open via
`session_tool.create_fresh` per playbook §16 arc-open fresh-thread
discipline. Health check at open: score=100, recommendation=continue,
turn_count=1, estimated_tokens=500, topics=[workspace].

**Retirements at S2200 open:**
`pa-18b095bb7c4740be` (Group 2100 RAG / Document Loading — Knowledge
Loop arc pin; NINTH formal arc; NINTH formal arc-pin retirement in
Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099).
Retired via `session_tool.retire` at S2199 close per playbook §16
arc-close discipline.

**Prior 8 arc-pin retirements (ledger preserved at `tools/pa_local.sh`
header):** S1399 pa-aa54193f240f4846 (Memory) + S1499 (Revenue) +
S1599 (Sports) + S1699 pa-f52acf3f8d394faa (Content) + S1799
pa-e7fbacc996b34b44 (Observability) + S1899 pa-ae5931ea706b4537
(HumanAttention) + S1999 pa-2bd1613ce2bd4a9c (Authority Enforcement) +
S2099 pa-dd7e973617da464d (Event / Integration Architecture) + S2199
pa-18b095bb7c4740be (RAG / Document Loading).

**Meta-methodology milestone state at S2200 open (per S2199 close
§12.5):**
- **MC-1** — CODIFICATION-CONFIRMED (arc-pin single-thread discipline)
- **MC-2** — CODIFICATION-CONFIRMED (D48 preemptive stability probe
  gate; 41 arms as of S2199 close; Group 2200 extends 41 → 42+ at
  S2200 SIGN cycle 1 open)
- **MC-3** — CODIFICATION-CONFIRMED (F18 test-gap durable-at-3-arcs;
  9 confirmations as of S2199 close)
- **MC-4** — CODIFICATION-CONFIRMED WITH SCOPE GUARDRAILS
  (parent-with-4-children arc-pin routing; extended to 3 consecutive
  arcs at S2199 close per §4 table arithmetic — 1900 + 2000+ + 2100;
  the S2199 close-card claim of "4 consecutive" traced to a stale
  count baseline per Rigby SIGN cycle 1 Q11 FOLD 2026-07-05
  correction. Group 2200 extends the consecutive-count from 3 → 4
  at Group 2200 close. S2199 Q3 STRENGTHEN dial-back resolution
  ("contingent on 5th arc or materially different stress condition")
  now requires a Group 2300+ arc as the 5th confirming arc — does
  NOT resolve at Group 2200 close.)
- **MC-5** — CODIFICATION-CONFIRMED (Cat F CONSOLIDATION scaling;
  12 sub-slot demonstrations as of S2199 close)
- **MC-6** — CODIFICATION-READY (S2099 promotion; awaiting Chris
  ratification at future xx99)
- **MC-7** — CANDIDATE (S2199 close addition; live-incident capture
  pending second-arc trigger per §20 two-triggers rule)
- **MC-8** — CANDIDATE (S2199 close addition; 4-label taxonomy
  pending second-arc trigger)
- **MC-9** — CANDIDATE (S2199 close addition; N_observed vs
  N_evidence_items separation pending second-arc trigger)
- **MC-10** — CANDIDATE (S2199 close addition; SIGN 4×5 cadence
  pending second-arc trigger)

**Session context at open.**
- Repo state: `main @ 268dbe26` (S2199 canonical summary + arc-close
  cascade commit); working tree clean except `.claude/scratch/`
  untracked; no uncommitted changes.
- Prior handoff: `docs/handoffs/SESSION_2199_RAG_DOCUMENT_LOADING_CANONICAL_SUMMARY.md`.
- Next handoff (this session close): `docs/handoffs/SESSION_2200_FRONTEND_DOMAIN_SCOPING.md`.
- CLAUDE.md subsystem docs pointer for Frontend: `docs/topics/frontend.md`
  (stale-warned per DOC-POINTER-V1 banner).
- 32-domain map row: 18 (Frontend / Workspace UI) — maturity STABLE,
  depth DEEP, pending Group 2200 pressure-test.

---
