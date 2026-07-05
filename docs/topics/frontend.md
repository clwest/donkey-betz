<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`../PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md) (sole authoritative counts per `DOC_LIFECYCLE.md` §2c). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Frontend & UI

React + TypeScript single-page application with 5 primary workspace tabs (Session 1100 refresh — was 9 in Session 969b before consolidation), collapsible sidebar, Command Center hub, and PA chat integration. Bundle: ~2,500 KB.

## Workspace Architecture

`WorkspacePageNew.tsx` orchestrates 5 primary tabs (`home`, `work`, `build`, `intelligence`, `system`) — sub-areas below are nested under these primary tabs.

**Post Session 1100 — 5 primary tabs:** `home`, `work`, `build`, `intelligence`, `system`. Each absorbs the prior 9-tab content as sub-areas below.

**Pre Session 1100 — 9 tab structure** (preserved here as the sub-area taxonomy; primary tabs above absorb these as sub-areas):

| Sub-area (legacy primary tab) | Sub-tabs | Purpose |
|-----|----------|---------|
| **Command Center** | "Now" hub + PA chat | 3-panel strip: Attention Queue, Active Work, System Pulse |
| **Content Studio** | Content, Blogs, Podcasts, Calendar, Dossiers, Voices, Files, Campaigns, Deliverables | Content creation and management |
| **Orchestration** | Monitor, Sessions, Execution | Agent orchestration and HiveMind sessions |
| **Intelligence** | Data Sources, Intelligence | Spider data and signal clusters |
| **Markets** | Predictions, Odds, Arbitrage | Market analysis and predictions |
| **Memory** | Palace, Learning, Evolution | Memory system and learning patterns |
| **Operations** | Reports, Audits, Experiments | Operational reports and audit results |
| **System** | Infrastructure, Orchestration, Triggers | Body systems health and Celery tasks |
| **Stocks** | Hub, Ticker Lookup, Overview, Briefs, Alerts, SEC, Predictions | Stock intelligence dashboard (Hub default) |

## Tab Normalization

`normalizeWorkspaceTab()` maps 18 legacy tab IDs to 9 canonical ones. `legacyTabToSubTab()` preserves sub-tab context during the mapping. Adapter components (SystemTab, DataIntelTab) handle merged tab logic.

## Route Structure

61 route definitions in App.tsx. Key routes:
- `/` — Command Center (home, PA chat)
- `/workspace` — 5-tab modular workspace (`home`, `work`, `build`, `intelligence`, `system`)
- `/stocks` — Stock Intelligence dashboard
- `/betting` — Betting Dashboard (9 tabs: Hub, Games, Top Plays, Sharp, Arbitrage, Watching, Odds, Wagers, Records). See Betting Dashboard section below.
- `/image-studio` — Image generation (DALL-E 3 / Flux, style picker, gallery)
- `/video-studio` — Video generation (RunwayML, text/image-to-video, async polling, gallery)
- `/documents` — Document management

## Command Center "Now" Hub

3-panel strip between header and PA chat:
- **Attention Queue** — HumanAttentionItems needing review
- **Active Work** — Currently running agent tasks
- **System Pulse** — Body system health summary

Each panel is clickable → navigates to relevant workspace tab.

## Intelligence Desks Panel (Session 1000)

Collapsible 4-card grid below Now Hub showing intelligence desk status:
- **Stocks** (green) | **Sports** (amber) | **Blockchain** (cyan) | **Narrative** (purple)
- Each card: icon, status badge (Ready/No Data), executive summary, agent count, timestamp
- "Run All Desks" button triggers on-demand `POST /api/home/trigger-desks/`
- Auto-expands when desks have fresh data
- While Away section shows "intel desks ready" pill (purple, Brain icon)

## PA Integration

**GlobalPADock:** Floating PA chat overlay, accessible from any page. Includes PAConversationSidebar overlay for conversation history.

Rigby chat uses `POST /api/pa/chat/` everywhere. Workspace-aware UI surfaces pass explicit workspace context into the shared assistant context store, and Rigby resolves `global` vs `workspace` mode from that explicit context rather than guessing from prompt text.

**CommandCenterPage:** Full-width PA chat with sidebar for conversation list.

**AssistantPage:** Dedicated PA page.

All three use the same async flow: dispatch task → poll status → display response.

## Page Telemetry

`usePageTracking()` hook fires fire-and-forget Redis counters via `POST /api/v1/telemetry/page-view/` on every page navigation.

## Betting Dashboard (`/betting` — Session 1012, refreshed Session 1100)

9 tabs with real data from TheOddsSpider, ESPN, PlacedWager, and MLPrediction models:

| Tab | Key Features |
|-----|-------------|
| **Hub** | Summary cards: total bets, win rate, pending, today's picks |
| **Overview** | Overall stats, sport breakdown |
| **Today's Games** | Live scores + ESPN period/clock/status_detail, expandable per-bookmaker odds comparison grid, quick-pick buttons |
| **Top Plays** | AI-generated top picks with confidence scores |
| **Sharp Action** | 13 sport filters (NFL, NBA, MLB, NHL, NCAAB, NCAAF, EPL, La Liga, Bundesliga, Serie A, MLS, Champions League, UFC). Redesigned signal cards: recommendation box ("Sharp money on: TEAM, Best value: bet at BOOK"), game time, stale line diffs with pts-off-market, sharp vs soft averages. LLM analysis rendered with markdown formatting. |
| **Arbitrage** | Detected arb opportunities with stake calculator (enter total stake, see per-leg amounts + guaranteed profit) |
| **Watching** | Tracked items with verification (won/lost/push/cancelled) |
| **Live Odds** | Full per-bookmaker odds grid with scores, LIVE/FINAL badges, period info |
| **Bankroll** | Real data from PlacedWager: total wagered, net P/L, ROI, at risk, win rate, wins/losses, avg bet, biggest win/loss, Kelly criterion |
| **My Wagers** | Wager list + "Log Wager" manual entry form (matchup, pick, odds, stake, sport, bookmaker, payout calculator) |
| **Markets** | Market data overview |
| **AI Record** | MLPrediction history deduped by game (latest prediction per game). By-sport accuracy breakdown (e.g., NCAAB W/L%), pending predictions list (no duplicates), confidence calibration score |

**Backend endpoints:** `core/views_odds_sports.py` — `get_todays_games()` merges ESPN scoreboards for live game details, `get_ai_track_record()` deduplicates by game_id via `Max('id')` per game.

## Key Frontend Patterns

- **Zustand stores:** paStore (conversations, sidebar state), workspaceStore (active tab/sub-tab)
- **Delegate pattern:** Content Studio sub-tabs use delegate components for Dossiers, Voices, Files
- **Workspace Files tab:** `FilesTab.tsx` now supports file preview, inline edit/save, and file history on the live workspace surface.
- **controlledSubTab prop:** 4 original tabs suppress inner navigation when parent drives sub-tab selection
- **Bundle optimization:** 2,253 KB (down from 3,062 KB, -26.5%)

## Contract-Surface Governance (Group 2200 arc close, S2299 2026-07-05)

Group 2200 Frontend (Contract-Surface Arc) closed at S2299 canonical summary. See [`../research/domains/frontend/2299_frontend_canonical_summary.md`](../research/domains/frontend/2299_frontend_canonical_summary.md) for full arc synthesis. Six acceptance criteria (S2200 §lens block post-Q3 SIGN STRENGTHEN fold) govern the frontend as a contract surface:

1. **Route contract** — Every route in App.tsx maps to owned page + layout with declared consumer contract. **PARTIAL** at S2299 close (route ownership map extractable but not durable contract source-of-truth).
2. **Envelope contract** — Every WebSocket consumer emits envelopes conforming to `ui.render_hint` shared schema. **UNMET** (0/40 conformance at HEAD; DEFERRED to Group 1700 Observability arc close per S2202 §20.6 Option (c) + Path A/B/C triad + escape hatch).
3. **API contract** — Frontend↔backend API calls enumerated + typed against single source of truth. **UNMET** (6.85% typed-response coverage in `api.ts` Coverage A / ~11.8% globally Coverage B; drf-spectacular INSTALLED but wired only in `sports/views.py` 16 `@extend_schema` decorators; DEFERRED to Group 2500 API arc close per S2203 §20.6).
4. **State contract** — Session-scoped state has declared persistence discipline per surface. **PARTIAL** (3 of 7 Zustand stores + 6 of 12 direct localStorage DECLARED per formalized 4-criteria rubric; Path A DECLARE `storageKeys.ts` registry + Path B EXTEND version+migrate to authStore + navigationStore both HIGH-confidence; Path D1/D2 workspace-persistence + focused-entity DEFERRED to Group 2600 PA).
5. **Component boundaries** — Component/page/layout boundaries visible + navigable; no god-component pathologies. **PARTIAL** (6 of 38 pages ≥1,500 LOC across ≥3 surfaces; Child E spin-out trigger MET at S2201; execution-sequence lead: CommandCenterPage 2,551 + AgentsPage 4,695 + BettingPage 3,023; R1 test framework parallel as safety track).
6. **Failure-mode discipline** — Loading / error states + error boundaries + auth-failure handling standardized + observable. **UNMET** (no error boundaries anywhere; silent-401 SYSTEMIC via `api.ts:48-56`; DEFERRED-DISTRIBUTED to Group 2400 Auth + Group 2500 API + post-arc T-slot).

## WebSocket Consumer Surface (Group 2200 S2202 arc close)

- **125 backend route entries** across `**/routing.py` files (per S2202 Explore Agent A1).
- **~50-60 unique consumer classes** after de-duplication.
- **8 frontend subscription sites** across ~5 unique endpoints (`useWebSocket` hook + `useSystemEvents:371-416` switch dispatch multiplexing 14 event types).
- **≈4% whole-frontend coverage ratio** (surface variance: PA 20% > Command-Center 12% > Workspace 4% > Betting 0%).
- **0/40 emit-site `ui.render_hint` envelope conformance rate** (S2099 §14.3.4 F16 UNCHANGED at HEAD).
- **5 confirmed MOCK-DATA consumers** (`/ws/dbao/` + `/ws/profile/` + `/ws/sports/` live-scores + `/ws/decision-command/` + `/ws/sports-betting/`) + 3 HYBRID + 2 EMPTY + 11 DEAD-CANDIDATE INTENT-NEUTRAL routes.
- **TokenAuthMiddlewareStack uniformly applied** 125/125 (no auth drift at Child B slice).

## REST API Contract Surface (Group 2200 S2203 arc close)

- **93 api-module exports** in `frontend/src/lib/api.ts` (4,194 LOC + 407-session churn Session 688 → Session 1095).
- **919 total API calls** in api.ts + **6.85% typed-response coverage** (Coverage A, api.ts only); **~11.8% globally** (Coverage B, 115/973 with cockpitApi.ts merged).
- **`cockpitApi.ts` typed island** 54 functions with 96% typed via `@/types/cockpit` — sole typed island (scoped to `/cockpit/*` ops-surface).
- **4 primary cross-cutter api-modules** (`humanApi` + `assistantApi` + `workspaceApi` + `contentApi`) span ≥2 major surfaces each.
- **drf-spectacular INSTALLED + PARTIAL-WIRED** — `requirements.txt` + `SPECTACULAR_SETTINGS` + `sports/views.py` 16 `@extend_schema` decorators; `core/*.py` 0 decorators.
- **silent-401 SYSTEMIC** via `api.ts:48-56` (~630 of ~1,300 gated call-sites at silent-401 risk per grep estimate hedged for wrapper duplicates).
- **18 verifier-confirmed DEAD-CANDIDATE api-modules** (~18-25 pending R3 full TSX sweep).

## Session-scoped State + Persistence Surface (Group 2200 S2204 arc close)

- **7 Zustand stores** (`authStore` + `navigationStore` + `paStore` + `workspaceStore` + `assistantContextStore` + `bodyStore` + `unifiedStore`).
- **3 Zustand persist stores** (`auth-storage` + `navigation-store` + `pa-dock-state`); paStore uniquely v3+migrate as exemplar.
- **12 direct localStorage keys** across 9 files (6 DECLARED / 6 ACCIDENTAL per formalized 4-criteria rubric: C1 constant / C2 typed accessor / C3 graceful fallback / C4 template disciplined).
- **0 sessionStorage** usage; **0 IndexedDB** usage.
- **1 cookie read** (`paStore.ts:241` reads `sessionid` for feedback POST).
- **1 in-memory ring buffer** (Session 968 X-UI-Scope request-log at `api.ts:3968-4051`, 200-entry cap, dev-only).
- **Naming convention drift**: 6 kebab-case + 3 snake_case + 3 camelCase across 12 direct keys (3 Zustand persist keys all kebab-case).
- **F5 F2 hazard site**: `workspaceStore.activeWorkspace` in-memory-only creates PA-context-loss on refresh — 144 consumer sites, 12 PA-side; borderline HIGH conditional on Group 2600 PA correctness disposition.
- **Falsifier verdict**: SURFACE-LOCAL + DOMAIN-SPECIFIC HYBRID — 14 of 15 persisted keys outside `/betting`; 0 of 15 inside; does NOT generalize whole-frontend.
