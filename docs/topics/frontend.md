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
