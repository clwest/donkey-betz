---
title: "Frontend — narrative (batch G)"
status: draft (batch G of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158)
companion_docs:
  - docs/topics/frontend.md
  - docs/narratives/PERSONAL_ASSISTANT.md
  - docs/narratives/CONTENT_PIPELINE.md
  - docs/narratives/SIGNAL_INTELLIGENCE.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: HIGH (anchored to topic doc + PLATFORM_INVENTORY + named handoff filenames)
provenance_note: The frontend is the only narrative whose audience contradiction is structural — written for an operator who cannot access UI, about the UI. Covered with that in mind: what surfaces exist, what they show, what the user can do, and how state flows from backend to screen. Counts anchored to PLATFORM_INVENTORY 2026-05-25 (git HEAD d513cd7f). 61 routes; 5 primary workspace tabs (post Session 1100 consolidation, was 9); 9 betting dashboard tabs.
---

# Frontend

> Written for an operator who cannot see the UI. The point is
> to let you reason about what users are looking at without
> actually opening the browser — useful when debugging "the
> user says X is missing from the dashboard," or planning a
> backend change that needs a UI surface, or just
> understanding why a route exists.

---

## 1. What this is

The frontend is a React + TypeScript single-page application
served from `/`. It uses Vite, Tailwind, and shadcn/ui. The
bundle is ~2,253 KB (down from 3,062 KB after Session 1100's
consolidation). 61 routes are wired in `App.tsx`. The primary
work surface is `/workspace` — a five-tab modular page
introduced in Session 1100 to replace the prior nine-tab layout
(which itself had been the consolidation of 18 legacy tab IDs).

The two surfaces a casual user spends most time on:

- **Command Center (`/`)** — the home page. A "Now" hub showing
  three live panels (Attention Queue, Active Work, System
  Pulse) above a full-width Rigby chat. Optionally collapses
  the Intelligence Desks panel (Session 1000) into a four-card
  grid.
- **Workspace (`/workspace`)** — five primary tabs (`home`,
  `work`, `build`, `intelligence`, `system`). Each tab carries
  the prior nine-tab content as sub-tabs.

Less-default but heavily used:

- **Betting Dashboard (`/betting`)** — 9 tabs of real sports
  data, predictions, sharp-action signals, arbitrage, and
  bankroll tracking. The vertical with the tightest
  feedback loop because bets either settle or don't.
- **Stocks Dashboard (`/stocks`)** — Hub default; ticker
  lookup, briefs, alerts, SEC filings, predictions.
- **Studios (`/image-studio`, `/video-studio`)** — media
  generation with async polling.

State flows backend → frontend via the standard PA async path:
the frontend posts to an endpoint that returns a `task_id`,
polls status every 2 s, renders the result when the Celery
task completes. Zustand stores hold ephemeral UI state
(conversation list, active tab, sub-tab). A page-tracking hook
fires Redis counters on every navigation.

This narrative is operator-grade: it should let you answer
"where in the UI does X surface?" or "what backend endpoint
feeds Y panel?" without scrolling through 700-line React
components.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **`App.tsx`** | The router. 61 `<Route>` entries per PLATFORM_INVENTORY 2026-05-25. Adding a new top-level surface = adding a route here. |
| **`WorkspacePageNew.tsx`** | The five-tab orchestrator. Owns the `home / work / build / intelligence / system` tab state and renders the appropriate inner component. Post Session 1100 consolidation. |
| **5 primary workspace tabs** | `home`, `work`, `build`, `intelligence`, `system`. Each one has 1–9 sub-tabs nested below. The mapping table is in `docs/topics/frontend.md`. |
| **9 → 5 consolidation (Session 1100)** | The previous workspace shape (post-Session-969b) had 9 primary tabs (Command Center / Content Studio / Orchestration / Intelligence / Markets / Memory / Operations / System / Stocks). Session 1100 collapsed these into 5 primary tabs and kept the prior tabs as sub-areas. |
| **`normalizeWorkspaceTab()`** | The legacy-mapper. 18 legacy tab IDs → 9 canonical IDs (and post-1100, 9 → 5 sub-area routes). Existed to keep deep links alive across UI reorganizations. |
| **`legacyTabToSubTab()`** | Companion to the above. Preserves sub-tab context when a legacy URL is normalized. |
| **Command Center "Now" Hub** | Three-panel strip between header and PA chat on `/`. Attention Queue (HumanAttentionItems), Active Work (running agent tasks), System Pulse (body system health summary). Each panel is clickable and navigates to the relevant workspace tab. |
| **Intelligence Desks Panel (Session 1000)** | Collapsible four-card grid below the Now Hub. Stocks (green), Sports (amber), Blockchain (cyan), Narrative (purple). Each card shows status badge, executive summary, agent count, timestamp. "Run All Desks" button → `POST /api/home/trigger-desks/`. |
| **`GlobalPADock`** | The floating PA chat overlay accessible from any page. Carries `PAConversationSidebar` for history. The standard "talk to Rigby from anywhere" surface. |
| **`CommandCenterPage`** | Full-width PA chat on `/`. Same async flow as GlobalPADock but takes the whole viewport. |
| **`AssistantPage`** | Dedicated PA page for when the user wants an assistant-only view (not the dashboard + chat combination). |
| **PA async flow** | `POST /api/pa/chat/` → returns `{task_id}` → frontend polls `GET /api/pa/chat/status/<task_id>/` every 2 s → renders response. Same flow for all three PA surfaces. Covered in narrative D. |
| **Workspace context store** | Zustand store carrying `workspace_id`, `AssistantProfile.workspace`, and other explicit workspace context. Per narrative D, Rigby's workspace mode resolves from this store; it never infers workspace scope from prompt text. |
| **`usePageTracking()`** | Hook on every page navigation. Fires `POST /api/v1/telemetry/page-view/` to Redis counters. Fire-and-forget — does not block render. |
| **Zustand stores** | `paStore` (conversations + sidebar state), `workspaceStore` (active tab + sub-tab). Plus per-surface stores for ephemeral UI state. |
| **`FilesTab.tsx`** | The workspace Files sub-tab. Supports preview, inline edit / save, and file history. The most operator-useful surface for "what did the agent actually write?" |
| **Delegate pattern** | Content Studio sub-tabs (Dossiers, Voices, Files) use delegate components rather than rendering inline. Keeps `WorkspacePageNew.tsx` from growing past ~700 lines. |
| **`controlledSubTab` prop** | Used by 4 original tabs to suppress inner navigation when the parent drives sub-tab selection. The fix that made deep links to sub-tabs work after consolidation. |
| **Betting Dashboard tabs (9)** | Hub / Overview / Today's Games / Top Plays / Sharp Action / Arbitrage / Watching / Live Odds / Bankroll / My Wagers / Markets / AI Record. Real data from TheOddsSpider, ESPN, `PlacedWager`, `MLPrediction`. |
| **Bundle size** | 2,253 KB current (per topic doc). Down from 3,062 KB pre-Session-1100 (−26.5 %). |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Foundation — React + TypeScript SPA** *(early sessions, Inferred)* | React + TypeScript + Vite + Tailwind + shadcn/ui scaffold. Initial App.tsx with a smaller route set. PA chat existed as a basic component. Zustand stores introduced early as the ephemeral state pattern. | The platform needed a frontend that could iterate faster than a Django template stack. SPA shape lets the same backend serve different surfaces (workspace, betting, stocks, studios) without per-page server rendering. | Initial workspace shape: a single page with embedded panels. Routes added per feature. Lots of inline state in components. | **Active** — the SPA shape is unchanged; only its organization has been refactored. | `frontend/src/App.tsx`; `frontend/package.json`; Vite + Tailwind config |
| **Session 969b — workspace 9-tab structure** | Workspace consolidated into 9 primary tabs (Command Center / Content Studio / Orchestration / Intelligence / Markets / Memory / Operations / System / Stocks). `normalizeWorkspaceTab()` introduced to map 18 legacy tab IDs to the 9 canonical ones. `legacyTabToSubTab()` preserved sub-tab context. The "stable URL shape that survives reorganization" pattern was established here. | The frontend had been growing organically — every feature added either a new top-level tab or a new modal, and deep links were silently broken whenever something moved. The 9-tab structure was a deliberate consolidation. | Workspace had a single named shape; backend changes that needed UI could pick a tab without inventing a new top-level surface. | **Superseded by Session 1100** for primary structure; `normalizeWorkspaceTab()` lives on as the legacy compatibility layer. | `docs/handoffs/SESSION_969b_PA_LIVE_TELEMETRY.md` (related); topic doc §"Workspace Architecture" reference to "9 in Session 969b before consolidation" |
| **Session 1000 — Intelligence Desks Panel** | Collapsible four-card grid below the Now Hub (Stocks / Sports / Blockchain / Narrative). Each card: icon, status badge (Ready / No Data), executive summary, agent count, timestamp. "Run All Desks" button posts to `POST /api/home/trigger-desks/`. Auto-expands when desks have fresh data. While-Away section shows an "intel desks ready" pill (purple, Brain icon). | The four Intelligence Desks (covered in narrative A milestone 5) existed as backend coordinators but had no on-demand surface in the UI. The panel made the desks one-click-runnable and surfaced their freshness state. | Users can see at-a-glance which desks have fresh data and trigger them without going through a separate page. Cross-ref to narrative A's footgun: desks are on-demand only — no scheduled run. | **Active** — the panel is on Command Center; the trigger endpoint is the only documented way to run desks. | `docs/handoffs/SESSION_1000_INTELLIGENCE_DESKS.md`; topic doc §"Intelligence Desks Panel (Session 1000)" |
| **Session 1012 — Betting Dashboard initial** | `/betting` route shipped with multiple tabs of sports data. Hub, Overview, Today's Games (live scores + period/clock/status_detail from ESPN merge — covered in narrative C milestone 7), Top Plays, Sharp Action (signal cards with HOT/WARM divergence, sharp vs soft averages), Arbitrage with stake calculator, Watching with verification, Live Odds per-bookmaker grid, Bankroll, My Wagers, Markets, AI Record. AI Record dedupes by `Max('id')` per `game_id` to prevent inflated W/L stats — the dedup fix from narrative C milestone 7. | The platform's tightest verifiable feedback loop is sports (bets settle in days, not months). It needed a UI that reflected the structured data the signal pipeline was producing — predictions, sharp signals, arbitrage opportunities, settled wagers. | Sports vertical has its own first-class dashboard. The structured data from `GamePredictor` / `SharpActionDetector` / `BettingOutcomeVerifier` becomes a directly-usable view. | **Active** — the dashboard is the main sports surface. Session 1100 refreshed parts of it (sharp action card redesign, additional tabs). | `docs/topics/frontend.md` §"Betting Dashboard"; `frontend/src/pages/BettingDashboardPage.tsx`; backend `core/views_odds_sports.py` |
| **Session 1100 — 9→5 tab consolidation + Betting refresh + AI Record dedup** | Workspace primary tabs collapsed from 9 to 5: `home`, `work`, `build`, `intelligence`, `system`. The 9 tabs became sub-areas under the 5. `controlledSubTab` prop introduced on 4 of the original tabs to suppress inner navigation when the parent drives sub-tab selection (the fix that made deep links survive consolidation). Betting Dashboard refreshed: Sharp Action redesigned with new signal cards (recommendation box "Sharp money on: TEAM, Best value: bet at BOOK", game time, stale line diffs with pts-off-market, sharp vs soft averages); 13 sport filters in Sharp tab; LLM analysis rendered with markdown formatting; AI Record deduplicates by game (latest prediction per game) via `Max('id')` per `game_id`. Bundle reduced 3,062 → 2,253 KB (−26.5 %). | The 9-tab structure had grown too wide for the screen on smaller displays; users were getting lost between primary tabs and sub-tabs. The 5-tab consolidation kept all the content but reduced the top-level decision space. Betting Dashboard's signal cards were dense; the redesign made the recommendation explicit instead of inferred from the data. AI Record was silently inflating W/L stats when predictions ran multiple times per game. | Workspace shape is more navigable; the 5 primary tabs each cover a focused purpose. Bundle is 26.5 % smaller. Sharp Action cards are operator-readable at a glance. AI Record W/L stats are correct. | **Active** — 5-tab workspace is the current shape. | `docs/topics/frontend.md` §"Workspace Architecture", §"Tab Normalization", §"Betting Dashboard"; topic doc Session 1100 references |
| **Workspace `FilesTab.tsx` enhancement** *(date Unknown — confirmed live in topic doc)* | `FilesTab.tsx` gained file preview, inline edit / save, and file history on the live workspace surface. The most operator-useful surface for "what did the agent actually write?" — replaces having to SSH or use a separate file viewer to inspect agent outputs. | Workspace-aware agents (covered in narrative A milestone 2) write files; users had no in-UI way to inspect, edit, or revert them. FilesTab closed the loop. | Operators can see, edit, and roll back agent file output without leaving the workspace. The audit-trail of writes is visible. | **Active.** Date of original ship is Unknown in the corpus surveyed. | `docs/topics/frontend.md` §"Key Frontend Patterns" — FilesTab note; `frontend/src/pages/workspace/tabs/FilesTab.tsx` |
| **PA integration evolution — GlobalPADock + CommandCenterPage + AssistantPage** *(Inferred, gradual through Sessions 969b → 1100)* | Three distinct PA surfaces emerged: `GlobalPADock` (floating overlay from any page), `CommandCenterPage` (full-width PA chat on `/`), `AssistantPage` (dedicated PA-only page). All three use the same async flow (`POST /api/pa/chat/` → poll status → render). Workspace-aware UI surfaces pass explicit workspace context into the shared assistant context store. Rigby resolves `global` vs `workspace` mode from explicit context, never from prompt text. | The PA needed multiple presentation modes: a quick-access overlay from any page, a focused chat on Command Center, and a full-page mode for deep work. All three pointed at the same Celery-backed async pipeline; only the presentation differed. The workspace-context discipline (no inference from prompt text) is enforced at the store layer, not the message. | Users can talk to Rigby from any surface; workspace scope is propagated correctly via the store. Cross-ref narrative D milestone "scopes" — the discipline lives here on the frontend side. | **Active** — all three surfaces are in production. | `docs/topics/frontend.md` §"PA Integration"; cross-ref `docs/narratives/PERSONAL_ASSISTANT.md` § 2 "global vs workspace modes" |
| **Page telemetry hook** *(date Unknown — confirmed in topic doc)* | `usePageTracking()` hook fires `POST /api/v1/telemetry/page-view/` on every page navigation. Fire-and-forget — does not block render. Backend writes to Redis counters. | The platform had no visibility into which UI surfaces users actually used. Some routes might be dead code; some might be the bulk of traffic. The hook closed the gap. | Per-route navigation counts are visible. Used informally to decide which surfaces deserve attention. | **Active.** Originating session not found in the corpus surveyed. | `docs/topics/frontend.md` §"Page Telemetry"; `frontend/src/hooks/usePageTracking.ts` |

---

## 4. What came of it

### Wins

- **Stable URL shape.** `normalizeWorkspaceTab()` +
  `legacyTabToSubTab()` keep deep links alive across two
  major reorganizations (18 → 9 → 5). Users who bookmarked
  pages from a year ago still land somewhere reasonable.
- **5-tab workspace is navigable.** The 9-tab version was
  wide; 5 with sub-tabs is the right tradeoff.
- **PA is available everywhere.** Three surfaces
  (GlobalPADock, CommandCenterPage, AssistantPage) feed the
  same async pipeline. No "where do I find Rigby?" question.
- **Workspace scope is explicit.** The Zustand store carries
  `workspace_id`; Rigby resolves mode from it. No
  inference-from-text footgun (cross-ref narrative D).
- **Betting Dashboard reflects the verifiable loop.** Real
  predictions, real settlements, real W/L stats (dedup fixed
  Session 1100). Sharp Action cards are operator-readable.
- **Page telemetry exists.** Per-route counts make "is this
  surface used?" answerable.
- **Bundle size matters.** 26.5 % reduction in Session
  1100 — paid attention to it explicitly. Most SPAs don't.
- **`FilesTab.tsx`** closes the workspace agent-output
  loop. Preview / edit / history all in one tab.

### Tradeoffs

- **18-legacy → 9-canonical → 5-primary is two layers of
  remapping.** A new developer reading the routing logic
  needs to understand both `normalizeWorkspaceTab()` and the
  9→5 sub-area mapping. Documentation lives in the topic
  doc but the mappings themselves are in code.
- **Workspace tab content lives in delegate components.**
  Content Studio's Dossiers / Voices / Files use delegates
  rather than rendering inline. Easier to reason about per-
  component, harder to discover "where is this rendered?"
  from a code-search standpoint.
- **`controlledSubTab` prop is opt-in.** 4 tabs use it. If a
  new tab is added without it, deep links to its sub-tabs
  may break. Convention, not enforcement.
- **Bundle is still 2,253 KB.** Down from 3,062 but not
  small. Code-splitting opportunities probably exist; no
  measured analysis in the corpus.
- **The frontend is the only surface without a `topic doc`
  drift checker.** Topic docs for backend subsystems are
  scanned by `verify_doc_claims` for drift against runtime;
  the frontend's tab counts and route counts drift more
  easily because there's no equivalent verifier walking the
  React tree.
- **Page telemetry is fire-and-forget to Redis counters.**
  No retention policy documented; counters could blow over
  time, and there's no schema for what's collected.
- **Async PA polling at 2 s creates network chatter.** Fine
  for desktop with good connectivity; weaker mobile users
  may experience polling overhead. No exponential backoff
  documented.

### Follow-on systems enabled

- **PA integration** (narrative D) — the three frontend
  surfaces are the consumers of `/api/pa/chat/`. The async
  polling pattern is the documented contract.
- **Betting Dashboard** (narrative C milestone 7) is the
  vertical-slice consumer of the signal pipeline's sports
  arm. AI Record dedup is the same fix in both backend and
  frontend.
- **`FilesTab.tsx`** is the consumer of the workspace-aware
  agents in narrative A milestone 2. Without FilesTab, the
  audit trail is invisible to users.
- **Intelligence Desks Panel** (Session 1000) is the UI
  trigger for the desks defined in narrative A milestone 5.
  The "Run All Desks" button is the only way to fire desks
  given that none are scheduled.

---

## 5. Current state snapshot

> Source for counts: `PLATFORM_INVENTORY.md` snapshot
> 2026-05-25 (git HEAD `d513cd7f`). 61 routes in App.tsx; 5
> primary workspace tabs; 9 betting dashboard tabs.

**Routes (61).** Top-level surfaces enumerated in `App.tsx`.
Key routes:
- `/` — Command Center (Now Hub + PA chat + Intelligence
  Desks Panel)
- `/workspace` — 5-tab modular workspace (home / work /
  build / intelligence / system)
- `/stocks` — Stocks dashboard (Hub default)
- `/betting` — Betting Dashboard (9 tabs)
- `/image-studio`, `/video-studio` — media generation
- `/documents` — Document management
- Plus ~55 other routes for specific surfaces.

**Workspace tabs (5).** `home`, `work`, `build`,
`intelligence`, `system`. Each has 1–9 sub-tabs nested.

**Betting Dashboard tabs (9).** Hub / Overview / Today's
Games / Top Plays / Sharp Action / Arbitrage / Watching /
Live Odds / Bankroll / My Wagers / Markets / AI Record. (List
in topic doc includes 12 named tabs across the dashboard
ecosystem; PLATFORM_INVENTORY counts 9 primary.)

**Command Center "Now" Hub (3 panels).** Attention Queue,
Active Work, System Pulse. Each clickable, navigates to
related workspace tab.

**Intelligence Desks Panel (Session 1000).** 4 cards (Stocks
green, Sports amber, Blockchain cyan, Narrative purple). "Run
All Desks" → `POST /api/home/trigger-desks/`.

**PA integration (3 surfaces).** `GlobalPADock` (overlay),
`CommandCenterPage` (full-width on `/`), `AssistantPage`
(dedicated). All use `POST /api/pa/chat/` → poll status every
2 s.

**Workspace context.** Zustand store carries `workspace_id` /
`AssistantProfile.workspace`. Rigby resolves global vs
workspace mode from store, never from prompt text (cross-ref
narrative D § 2).

**Page tracking.** `usePageTracking()` fires `POST
/api/v1/telemetry/page-view/` on every navigation; Redis
counters; fire-and-forget.

**Zustand stores.** `paStore` (conversations + sidebar),
`workspaceStore` (active tab + sub-tab), plus per-surface
ephemeral state.

**Tab normalization.** `normalizeWorkspaceTab()` maps 18
legacy tab IDs to 9 canonical ones; `legacyTabToSubTab()`
preserves sub-tab context. Adapter components (SystemTab,
DataIntelTab) handle merged tab logic.

**Bundle.** 2,253 KB (post Session 1100 consolidation, −26.5
% from 3,062 KB).

**Where to look when something stops working.**
- User says "X disappeared from the dashboard" → check if X
  moved to a sub-tab in the 9→5 consolidation; check legacy
  URL mapping in `normalizeWorkspaceTab()`.
- PA chat doesn't respond → check the three async surfaces
  share the same flow; one breaking usually means a backend
  issue (cross-ref narrative D § 5 troubleshooting).
- Sharp Action recommendations look wrong → check signal
  card data binding; the recommendation box is computed
  client-side from the sharp/soft averages — backend
  contract is `core/views_odds_sports.py`.
- AI Record W/L looks inflated → confirm dedup is applied;
  Session 1100 fix uses `Max('id')` per `game_id`.
- New tab doesn't deep-link → likely missing `controlledSubTab`
  prop; check the 4 tabs that use it as the convention.
- Workspace mode resolved incorrectly → frontend isn't
  passing `workspace_id` in the context store; check the
  workspace-aware UI surface code (narrative D § 6 covers
  the back half of this trace).
- Page-view counts missing in Redis → `usePageTracking()`
  hook removed from a page, or telemetry endpoint failing
  silently.

---

## 6. Open questions / unknown outcomes

- **When was `FilesTab.tsx` shipped with preview / edit /
  history?** *Known:* it's live per topic doc. *Unknown:*
  the originating session. A `git log` on
  `frontend/src/pages/workspace/tabs/FilesTab.tsx` would
  surface it.
- **When was `usePageTracking()` introduced?** *Known:* it
  exists and fires on every page nav. *Unknown:* the
  session of origin and the retention policy on the Redis
  counters.
- **Telemetry data shape and retention.** *Known:* fire-and-
  forget to Redis counters. *Unknown:* the schema (what
  fields are captured), the retention TTL on the counters,
  and whether anyone consumes the data for analysis.
- **`controlledSubTab` adoption rate.** *Known:* 4 tabs use
  it. *Unknown:* whether new tabs added since Session 1100
  follow the convention. A grep would resolve.
- **Bundle composition.** *Known:* 2,253 KB current.
  *Unknown:* what the top weight contributors are. No
  bundle analysis in the corpus.
- **Tab count drift.** *Known:* topic doc claims 9 betting
  tabs, but the dashboard tab table enumerates 12.
  *Unknown:* whether PLATFORM_INVENTORY's "9" reflects
  primary tabs vs total tabs.
- **Async polling backoff.** *Known:* PA poll is fixed at 2
  s. *Unknown:* whether mobile users have reported the
  polling cost; no exponential backoff is in the docs.
- **Frontend drift verifier.** *Known:* `verify_doc_claims`
  catches backend topic-doc drift. *Unknown:* whether any
  equivalent exists for the frontend (route counts, tab
  counts). Likely no — operationally this is why frontend
  counts drift more.

---

## 7. Source index

### Primary doc sources

- `docs/topics/frontend.md` — current-state topic doc; the
  closest companion.
- `docs/PLATFORM_INVENTORY.md` — 61 routes, 5 primary tabs,
  9 betting tabs.
- `docs/narratives/PERSONAL_ASSISTANT.md` — PA async flow,
  workspace context store, three PA surfaces.
- `docs/narratives/CONTENT_PIPELINE.md` — Betting tab
  consumes ContentWriterAgent-adjacent infrastructure;
  Sharp Action cards display content the signal pipeline
  produced.
- `docs/narratives/SIGNAL_INTELLIGENCE.md` — Betting
  Dashboard consumes `MLPrediction`, `PlacedWager`,
  `SharpActionDetector` signals.

### Named session handoffs cited above

- `docs/handoffs/SESSION_1000_INTELLIGENCE_DESKS.md` —
  Intelligence Desks Panel.
- Session 969b — workspace 9-tab structure (topic doc
  reference). Related handoff:
  `docs/handoffs/SESSION_969b_PA_LIVE_TELEMETRY.md`.
- Session 1012 — Betting Dashboard initial (topic doc
  reference; specific handoff filename in `docs/handoffs/`).
- Session 1100 — 9→5 consolidation + Betting refresh + AI
  Record dedup (topic doc reference).

### Code anchors

- `frontend/src/App.tsx` — 61 routes.
- `frontend/src/pages/WorkspacePageNew.tsx` — 5-tab
  orchestrator.
- `frontend/src/pages/CommandCenterPage.tsx` — Now Hub + PA
  chat.
- `frontend/src/pages/BettingDashboardPage.tsx` — sports
  dashboard.
- `frontend/src/pages/workspace/tabs/FilesTab.tsx` —
  workspace files with preview/edit/history.
- `frontend/src/stores/paStore.ts`,
  `frontend/src/stores/workspaceStore.ts` — Zustand state.
- `frontend/src/hooks/usePageTracking.ts` — telemetry hook.
- Backend `core/views_odds_sports.py` — Betting Dashboard
  endpoints.

### Verification commands

- `python manage.py generate_platform_inventory` —
  regenerate inventory for current route + tab counts.
- `git log -S "FilesTab" --oneline` — surface FilesTab
  ship session (open question § 6).
- `git log -S "usePageTracking" --oneline` — surface
  telemetry hook origin.
