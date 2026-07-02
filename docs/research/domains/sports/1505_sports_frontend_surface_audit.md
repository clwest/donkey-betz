---
title: "Sports Frontend Surface Architecture Audit"
status: draft
category: child_audit
subdomain_category: E
authority: "child-audit for Category E per parent §5 sequence + fifth sibling to apply the pre-brief mini-schema per D62 = (a) propagate upfront"
domain: sports
session: 1505
generated: 2026-07-02
last_verified: 2026-07-02
parent_doc: 1500_sports_domain_scoping.md
sibling_docs:
  - 1501_sports_odds_ingestion_normalization_audit.md
  - 1502_sports_prediction_analytics_agents_audit.md
  - 1503_sports_wager_tracking_outcome_verification_audit.md
  - 1504_sports_betting_content_pipeline_audit.md
verifier_loop: "Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence via fresh isolation pin pa-546de7ebe8c8b885 (retired at S1505 close). F1-F5 folds landed at commit-time: F1 §14.3 auth-drift wording tightening (no 401 surfacing + backend permission-floor inconsistency); F2 §15.5 elevated MED → HIGH structural debt (API contract source-of-truth); F3 §14.3 verified-in-repo anchors snippet; F4 §14.3 tab-consumer identification; F5 §14.1 MOCK-DATA-CONSUMER intent-neutrality nuance. D48 preemptive stability probe 8th arm clean (three consecutive fully-clean arms S1503+S1504+S1505). Cycle 2 SIGN-clean at High anticipated post-fold-land."
owner: claude-code-parent
---

# Sports Frontend Surface Architecture Audit

## 1. Executive Summary

This audit inventories **Category E — Frontend Sports Surface** of the Group 1500 Sports/DBAO/Intelligence research arc. Category E is the fifth child audit under parent §5 mission sequence; it consumes Category A/B/C/D backend surface findings and constrains Category F cross-domain integration posture criteria.

**Domain shape.** The sports frontend surface is a **single-page god-component** at `frontend/src/pages/BettingPage.tsx` (3,023 lines), routed at `/betting` (`frontend/src/App.tsx:89`), wrapped in `ProtectedRoute` (`App.tsx:47-59`), consuming three API clusters via `bettingApi` / `sportsHubApi` / `humanApi` from `frontend/src/lib/api.ts`. It renders **9 tabs** (Hub, Today's Games, Top Plays, Sharp Action, Arbitrage, Watching, Live Odds, My Wagers, Records) via a `tabs` array (`BettingPage.tsx:16-26`) and consumes ~20 REST endpoints across Categories A/B/C/D. There is **no WebSocket subscription** from BettingPage; all data refresh is **react-query polling** at 30-second (Live Odds) or 60-second (Games, Line Movement, Stats, Pipeline Status) cadence, with the majority of tabs fetching only on tab activation.

**Load-bearing findings for xx99 (S1599) via Cat F evidence plan (11):**

1. **CRITICAL architectural — `/ws/dbao/` broadcasts random mock data, not sports-derived state.** Parent §3.E flagged `/ws/dbao/` as "a DBAO metrics channel, not tab-scoped realtime." Verifier-loop confirms the broader problem: `core/new_pages_consumer.py:310-331` populates the payload via `random.randint()` + `random.uniform()` for every metric field (`data_points`, `active_queries`, `uptime`, `data_processed`, `avg_response`, `accuracy_rate`, `performance.{cpu,memory,disk,network}`). **New pattern class for the arc: MOCK-DATA-CONSUMER.** Distinct from S1504 §14.3 write-only-and-forgotten (real data written but not read). Here: no real data touched at all — the consumer synthesizes numbers server-side and streams them as if authentic. See §14.1.

2. **HIGH architectural — `markets` and `bankroll` DEAD-RENDER-PATH tabs.** The `BettingTab` TypeScript union at `BettingPage.tsx:14` declares 11 tab identifiers, but the visible `tabs` array at lines 16-26 renders only 9. Verifier-loop confirms `markets` and `bankroll` **are wired at the render layer** — conditional query hooks at lines 968 (`activeTab === 'bankroll'`) + 975 (`activeTab === 'markets'`) and conditional JSX blocks at lines 2080 (`activeTab === 'markets'`) + 2298 (`activeTab === 'bankroll'`) — but with no tab button, they are unreachable via UI navigation. **New pattern class: DEAD-RENDER-PATH** (fully coded feature branches with no user-facing entry point). Fifth distinguishing pattern shape after S1501 fragile-contract, S1502 armed-but-under-instrumented, S1503 armed-but-zero-fire, S1504 write-only-forgotten. See §14.2.

3. **HIGH operational — 2 AllowAny/IsAuthenticated permission drifts between frontend expectations and backend endpoints.** Frontend calls `bettingApi.liveOpportunities()` → `GET /v1/sports/live-opportunities/` (`core/urls.py:3085` → `live_betting_opportunities` at `views_odds_sports.py:579-580` `@permission_classes([IsAuthenticated])`) and `bettingApi.intelligence()` → `GET /v1/sports/betting-intelligence/` (`urls.py:3099` → `get_betting_intelligence` at `views_odds_sports.py:2055-2056` `@permission_classes([IsAuthenticated])`). All other Cat E-adjacent endpoints under `/v1/betting/*` + `/v1/sports/live-odds*` + `/v1/odds/*public` are `AllowAny` — pattern precedent under S1504 §3.3 + S1503 §14.7. **The Frontend has no client-side auth gate before these calls**, so anonymous session usage silently returns 401 on 2 of the 9 tabs. See §14.3.

4. **HIGH architectural — S1504 §14.3 `SportsBettingBrief` write-only-and-forgotten CONFIRMED at frontend AND at REST endpoint.** Verifier-loop of `get_betting_brief` (`core/views_odds_sports.py:3237-3265`) confirms the endpoint calls `SportsBettingCoordinator.generate_brief()` on-the-fly and returns the coordinator result verbatim — **the persisted `SportsBettingBrief` model is never read** by this endpoint or by any frontend consumer. S1504 §14.3 verdict holds: 2 writers + 0 readers at both persistence and consumption layers. See §14.4.

5. **HIGH architectural — Zero WebSocket subscription for BettingPage despite defined sports WS routes.** `sports/routing.py:7-11` registers `/ws/sports/`, `/ws/sports/odds/`, `/ws/sports/games/` consumers, but `frontend/src/pages/BettingPage.tsx` (3,023 lines) has zero `new WebSocket` / `useWebSocket` / `wss:` / `/ws/` references. Live Odds tab (30-second polling, `BettingPage.tsx:961`) misnamed as realtime. See §10.1 + §14.5.

6. **MED-HIGH POSTURE-DECISION-PENDING per S1502 F2 / S1503 §14.3 / S1504 F11 precedent — Zero Cat E → Signal Engine emission path.** BettingPage renders sharp-action + top-plays + arbitrage data flowing from Cat B agents through Cat D coordinator to the browser, but nothing publishes any of it to `SignalCluster`. F11 clarifier: no owning bridge implementation was located. Extends 4-arc consumer-side pattern (S1502 §14.3 + S1503 §14.3 + S1504 §14.5) to 5-arc pattern. See §10.2.

7. **MED architectural — BettingPage is the SOLE frontend sports data consumer (zero cross-domain leak).** Grep of `frontend/src/**` for `bettingApi` / `sportsHubApi` imports outside `pages/BettingPage.tsx` returns zero page-level consumers. `IntelligencePage`, `HubPage`, `CommandCenterPage`, `WorkspacePage` do not import sports data. Cross-domain leak surface = zero at frontend layer. This is a **positive isolation signal** for Category F island-vs-integrated posture evidence. See §9.3.

8. **MED operational — BettingPage.tsx = 3,023 lines god-component with 14 useQuery hooks + 17+ useState declarations + 5 inline sub-components + 11 inline TypeScript interfaces.** Frontend god-component threshold analog to backend 3,000-line service check per playbook §13 Agent 2. Rivals backend service complexity without the module-boundary discipline. See §15.1.

9. **HIGH per S1504 §15.12 F4-fold sibling precedent — Zero dedicated test coverage for BettingPage.tsx.** Grep of `frontend/**/*.test.{ts,tsx}` + `frontend/**/*.spec.{ts,tsx}` returns zero matches for BettingPage or bettingApi. Matches Cat D §15.12 F4-fold zero-test pattern that S1504 promoted MED-HIGH → HIGH. See §15.2.

10. **MED architectural — Zero client-side state persistence.** All state is React `useState` (no localStorage / sessionStorage / IndexedDB). Tab position + filters + expanded rows are lost on refresh. React Query caches API responses in memory only (cleared on reload). See §15.3.

11. **MED — No CODEOWNERS row for `frontend/src/pages/BettingPage.tsx`.** `.github/CODEOWNERS` search returns no path match; ownership is UNKNOWN. See §18.1.

**Maturity verdict per §13:** **PARTIAL (mixed — WORKING (real data + real UI) at read-side tabs (Hub, Today's Games, Sharp Action, Arbitrage, Live Odds, Wagers, Records via real REST endpoints); DEAD-RENDER-PATH at `markets` + `bankroll`; MOCK-DATA-CONSUMER at `/ws/dbao/` (any dashboard tab that subscribes reads mock data); AUTH-DRIFT at `live-opportunities` + `betting-intelligence` (silent 401); NO-REALTIME (polling-only across all 9 visible tabs))** — fifth distinguishing maturity shape after S1501 fragile-contract at ingestion, S1502 armed-but-under-instrumented, S1503 armed-but-zero-fire, S1504 mixed brief-generation + brief-persistence-forgotten + Discord-bypass HOT-PATH-CHOKE.

**Not implemented, not proposed.** This is a research audit per playbook §14 no-implementation rule. Findings feed S1506 (Cat F cross-domain integration lens + posture-decision evidence plan) and S1599 xx99 canonical summary.

---

## 2. Domain Purpose

**Q1 — What is this domain for?** The sports frontend surface renders sports betting data (odds, predictions, wagers, briefs) in the React web application, providing user access to the ingestion (Cat A), prediction (Cat B), wager tracking (Cat C), and content brief (Cat D) surfaces through a single-page dashboard at `/betting`.

**Q2 — What problem does it solve?** It converts backend sports betting data — otherwise reachable only via REST endpoints, Discord slash commands, or persisted database rows — into an interactive dashboard the operator (Chris) uses to browse odds, review AI-generated top plays, log wagers, verify outcomes, and audit AI model performance over time.

### 2.1 Cat E contract statement (Q1+Q2 tightened)

**Cat E guarantees to consumers (the operator viewing the dashboard):**

1. A single-page dashboard at `/betting` reachable only when authenticated (ProtectedRoute wrapper).
2. Nine visible tabs: Hub, Today's Games, Top Plays, Sharp Action, Arbitrage, Watching, Live Odds, My Wagers, Records.
3. Read-side data from Cat A (ingestion) + Cat B (predictions) + Cat C (wagers) + Cat D (briefs) surfaces via REST.
4. Write-side data to Cat C (wager placement / settlement / cancellation) via REST POST.
5. Automatic Django-token injection on every request (via axios interceptor at `frontend/src/lib/api.ts:27-40`).

**Cat E does NOT guarantee (verified via §14 drift matrix + explore agents):**

1. Any realtime WebSocket update — 100% polling; "Live Odds" is a 30-second poll.
2. Client-side state persistence — tab position lost on refresh (no localStorage).
3. Client-side auth gate — trusts the ProtectedRoute wrapper; no per-request check.
4. Client-side 401 handling for the 2 `IsAuthenticated`-drifted endpoints — silent failure.
5. Tab access to `markets` or `bankroll` code paths — coded but unreachable via UI (DEAD-RENDER-PATH).
6. Any subscription to `sports/routing.py` WS consumers (SportsConsumer / OddsConsumer / GamesConsumer).
7. Any subscription to `/ws/dbao/` (which broadcasts random mock data anyway — see §14.1).
8. Any read of persisted `SportsBettingBrief` model rows — brief endpoint computes on-the-fly.
9. Any `SignalCluster` emission from tab activity — no publish path.
10. Frontend-side rate limiting or backoff — react-query cadence is fixed per query key.
11. Test coverage — zero unit/integration tests targeting BettingPage or bettingApi.

These 11 non-guarantees are the load-bearing surface for Category F integration-posture criteria under D57. Any downstream design proposal that assumes any of them will drift.

---

## 3. Canonical Entry Points

**Q3 — What are the canonical entry points?**

### 3.1 Frontend route

| Route | File:line | Wrapper | Notes |
|---|---|---|---|
| `/betting` | `frontend/src/App.tsx:89` | `ProtectedRoute` (App.tsx:47-59) inside `Layout` (App.tsx:73) | Redirects to `/login` if `!isAuthenticated`. Sibling routes: `intelligence`, `content`, `settings`, `profile`, `legal`, `portfolio`, `stocks`, `government`, `admin`, `workspace`. |

### 3.2 Root component

| Component | File:line | Line count | Purpose |
|---|---|---|---|
| `BettingPage` | `frontend/src/pages/BettingPage.tsx:1-3023` | 3,023 | Single-page dashboard; renders all 9 tabs + 5 inline sub-components. |

### 3.3 Tab identifiers (11 declared, 9 rendered via nav)

**TypeScript union at `BettingPage.tsx:14`:**
```typescript
type BettingTab = 'hub' | 'games' | 'top_plays' | 'sharp' | 'arbitrage'
  | 'markets' | 'odds' | 'bankroll' | 'wagers' | 'watching' | 'records'
```

**Tabs array at `BettingPage.tsx:16-26` (rendered nav bar — 9 tabs):**

1. `hub` — "Hub"
2. `games` — "Today's Games"
3. `top_plays` — "Top Plays"
4. `sharp` — "Sharp Action"
5. `arbitrage` — "Arbitrage"
6. `watching` — "Watching"
7. `odds` — "Live Odds"
8. `wagers` — "My Wagers"
9. `records` — "Records"

**DEAD-RENDER-PATH tabs (declared in type + wired conditionally, but no nav button):**

- `markets` — query at `BettingPage.tsx:975` (`enabled: activeTab === 'markets'`) + render at `BettingPage.tsx:2080` (`{activeTab === 'markets' && (...)}`)
- `bankroll` — query at `BettingPage.tsx:968` (`enabled: activeTab === 'bankroll'`) + render at `BettingPage.tsx:2298` (`{activeTab === 'bankroll' && (() => {...})}`)

Reachable only by programmatic tab-state override (e.g., in a browser devtools React inspector) — no shipped code path sets `activeTab` to `markets` or `bankroll`. See §14.2.

### 3.4 API cluster imports

| Import | Line | Origin | Consumer scope |
|---|---|---|---|
| `bettingApi` | `BettingPage.tsx:3` | `frontend/src/lib/api.ts:1229-1276` | 20+ methods covering Cat A/B/C/D endpoints |
| `humanApi` | `BettingPage.tsx:3` | `frontend/src/lib/api.ts:1607-1665` | Watching + verify + human attention flow (Cat F human-in-the-loop) |
| `sportsHubApi` | `BettingPage.tsx:3` | `frontend/src/lib/api.ts:1279-1282` | Hub feed only (`/sports-hub/feed/`) |

---

## 4. Major Models

**Q4 — What are the major models?**

Cat E is a **frontend consumer surface with no persistence layer**. The models rendered are owned by sibling categories:

| Model | Owner | Consumed via | BettingPage tab |
|---|---|---|---|
| `SpiderData` / `LegacySpiderData` (data_type='sports_odds') | Cat A per S1501 §4 | `GET /sports-hub/feed/` (Hub feed) | Hub |
| `SportsGame` / `GameLineHistory` | Cat A per S1501 §4 | `GET /v1/betting/line-movement/` + `/v1/betting/movers/` + `/v1/betting/todays-games/` | Today's Games, Live Odds |
| `MLPrediction` | Cat B per S1502 §4 | `GET /v1/betting/track-record/` (dedup by game_id per S1502 F6) | Records |
| `SportsBettingCoordinator` output (in-memory) | Cat B per S1502 §5 | `GET /v1/betting/brief/` + `/v1/betting/sharp-action/` (coordinator run on-the-fly) | Top Plays, Sharp Action |
| `PlacedWager` / `PlacedWagerLeg` | Cat C per S1503 §4 (`core/models_betting.py:13` + `:108`) | `GET /v1/betting/wagers/` + POST/PUT wager mutations | My Wagers |
| `BettingStats` | Cat C per S1503 §4 | `GET /v1/betting/stats/` + `/v1/betting/recent/` | Hub (stats cards), always-enabled |
| `Bankroll` (state) | Cat C-adjacent (bankroll subsystem) | `GET /v1/odds/bankroll/` + `/v1/odds/bankroll/stats/` | DEAD-RENDER-PATH `bankroll` tab |
| `SportsBettingBrief` (persisted) | Cat D per S1504 §4 | **NEVER READ** by any frontend endpoint — see §14.4 | (none) |
| `HumanAttentionItem` (Cat F) | Cat C-adjacent per S1503 §14 | `GET /human/attention/` | Watching |

**Sibling-inheritance rule per playbook §9:** each model above is deep-audited by its sibling child; Cat E cites the owning audit and does not re-inventory.

### 4.1 Frontend TypeScript interfaces

BettingPage.tsx declares 10 inline interfaces (grep-verified per Explore Agent 1). Full list moved to §20.3.

**Pattern:** all interfaces are inline in BettingPage.tsx; no shared `frontend/src/types/betting.ts` module. Refactor candidate per §15.4.

### 4.2 Pre-brief mini-schema per surface (D62 = (a) propagate upfront, 5-sibling exemplar pattern)

**Applied per parent §5 D62 = (a) mini-schema propagation directive (Chris-ratified S1501 open).** Fifth sibling application after S1501 §4.6 + S1502 §4.8 + S1503 §4.4 + S1504 §4.4.

For each surface below, the 4-item mini-schema captures: (a) sports-only vs shared with mainline, (b) writes to sports-owned tables (DBAO schema) or mainline (public schema), (c) integration posture would require refactor or only extend, (d) island posture would require additional isolation guarantees.

| Surface | (a) Scope | (b) Table ownership | (c) Integration refactor cost | (d) Island isolation cost |
|---|---|---|---|---|
| `/betting` route (App.tsx:89) | Sports-only | N/A (frontend) | Zero — route is already isolated | Zero — already isolated |
| `BettingPage.tsx` | Sports-only | N/A | Zero — component is sports-only | HIGH — 3,023-line god-component would need split for testable isolation |
| `bettingApi` cluster (api.ts:1229-1276) | Sports-only | N/A (client) | LOW — could extract to per-Cat sub-clients | LOW |
| `sportsHubApi` (api.ts:1279-1282) | Sports-only (single method) | N/A | Zero | Zero |
| `humanApi` (api.ts:1607-1665) | **Shared with mainline** (used by CommandCenter, Boardroom, DecisionDetailModal per Explore Agent 4) | N/A | HIGH — humanApi refactor would touch non-sports pages | HIGH — Cat E use of humanApi is one caller of many |
| `ProtectedRoute` wrapper (App.tsx:47-59) | Shared with mainline (used by all authenticated routes) | Public schema (User/Token) | HIGH — would touch all routes | HIGH — global auth surface |
| `sports/routing.py` WS routes (unused by BettingPage) | Sports-only | N/A | LOW — routes exist but unwired | LOW |
| `/ws/dbao/` consumer (new_pages_consumer.py:18-479) | **Shared with mainline** (DBAO dashboard reads from same consumer) + MOCK-DATA-CONSUMER | N/A (in-memory random) | HIGH — consumer scope covers multiple product-lines | HIGH — mock-data pattern is a general dashboard demo pattern, not sports-scoped |
| `SportsBettingCoordinator` (called by REST endpoint synchronously per §7.1) | Sports-only | Public schema for reads | LOW | LOW |
| `SportsBettingBrief` writes (unread by frontend) | Sports-only | Public schema | LOW | LOW |

**Cross-sibling observation.** Cat E is the first sibling where **humanApi cross-domain sharing is load-bearing on the design-posture axis (d)**. S1501+S1502+S1503+S1504 all identified isolation surfaces as sports-only in the vast majority of cases. Cat E has 3 shared-with-mainline surfaces (`humanApi`, `ProtectedRoute`, `/ws/dbao/` consumer) that would require cross-domain refactor if the island posture is chosen. This raises the island-posture cost estimate above prior siblings and is a load-bearing observation for Category F.

---

## 5. Major Services

**Q5 — What are the major services?**

Cat E has **no dedicated service layer**; it is a frontend consumer. Services rendered belong to sibling categories. The primary indirect service reached is `SportsBettingCoordinator` (Cat B per S1502) via the brief and sharp-action REST endpoints.

### 5.1 Indirect service reach via REST endpoints

| Service | File:line | Reached via | BettingPage tab |
|---|---|---|---|
| `SportsBettingCoordinator.generate_brief()` | `core/services/sports_betting_coordinator.py:21` | `GET /v1/betting/brief/` → `views_odds_sports.py:3237-3265` | Top Plays |
| `SportsBettingCoordinator.get_sharp_action()` | `core/services/sports_betting_coordinator.py` (method presence per S1502 §5.1) | `GET /v1/betting/sharp-action/` → `views_odds_sports.py:3268-...` | Sharp Action |
| `SportsBettingCoordinator.get_arbitrage_opportunities()` | `core/services/sports_betting_coordinator.py` (method presence per S1502 §5.1) | `GET /v1/betting/arbitrage/scan/` → `views_odds_sports.py:431+` | Arbitrage |
| `BettingOutcomeVerifier` | `core/services/betting_outcome_verifier.py:21` per S1503 §5 | `POST /human/attention/{itemId}/verify/` (indirectly via Watching tab) | Watching |
| `SportsContentContextBuilder` | `core/services/sports_content_context.py:27` per S1504 §5.1 (F2 HOT-PATH-CHOKE-POINT reframe) | Reached transitively through brief-generation path | Top Plays |

### 5.2 Frontend "service" analogs

BettingPage relies on `@tanstack/react-query` (v5) for cache management + polling. No custom fetch layer service abstractions exist between `bettingApi` (thin wrapper) and useQuery hooks. This is a candidate for `useBettingData()` extraction per §19.1 #2.

---

## 6. Major APIs and Interfaces

**Q6 — What are the major APIs? (REST, WebSocket, PA tools)**

### 6.1 REST endpoints consumed by BettingPage

Inventory verified by Explore Agent 2 with cross-referenced `core/urls.py` mapping. All endpoints prefixed with `/api` (root prefix per Django URL config).

| Path | Method | View file:line | Permission | Cat owner | Frontend caller | Notes |
|---|---|---|---|---|---|---|
| `/api/v1/betting/stats/` | GET | `core/views_betting.py:382` | AllowAny | C | `bettingApi.stats()` | Always enabled; 60s refetch |
| `/api/v1/betting/recent/` | GET | `core/views_betting.py:425` | AllowAny | C | `bettingApi.recent()` | Hub-related |
| `/api/v1/betting/wagers/` | GET | `core/views_betting.py:128` | AllowAny | C | `bettingApi.wagers()` | My Wagers |
| `/api/v1/betting/wagers/<uuid>/` | GET | `core/views_betting.py:215` | AllowAny | C | (not called) | Detail endpoint unused |
| `/api/v1/betting/wagers/<uuid>/settle/` | POST | `core/views_betting.py:271` | AllowAny | C | `bettingApi.settleWager()` | Wager write path |
| `/api/v1/betting/wagers/<uuid>/cancel/` | DELETE | `core/views_betting.py:345` | AllowAny | C | `bettingApi.cancelWager()` | Wager write path |
| `/api/v1/betting/place/` | POST | `core/views_betting.py:19` | AllowAny | C | `bettingApi.placeBet()` | Wager write path |
| `/api/v1/betting/quick-pick/` | POST | `core/views_betting.py:482` | AllowAny | C | `bettingApi.quickPick()` | Wager write path |
| `/api/v1/betting/wager/` | POST | `core/views_odds_sports.py:2619` | **IsAuthenticated** | C | `bettingApi.logWager()` | Silent-drift risk if user session missing token — matches drift #3 in §14.3 |
| `/api/v1/betting/arbitrage/scan/` | GET | `core/views_odds_sports.py:431` | AllowAny | B | `bettingApi.arbitrageScan()` | Arbitrage tab |
| `/api/v1/odds/arbitrage/` | POST | `core/views_odds_sports.py:304` | AllowAny | B | `bettingApi.detectArbitrage()` | Arbitrage validation |
| `/api/v1/betting/line-movement/[gameId]` | GET | `core/views_odds_sports.py:2804` | AllowAny | A | `bettingApi.lineMovement()` | Live Odds tab (60s refetch) |
| `/api/v1/betting/movers/` | GET | `core/views_odds_sports.py:2930` | AllowAny | A | `bettingApi.movers()` | Live Odds tab support |
| `/api/v1/betting/futures/` | GET | `core/views_odds_sports.py:2418` | AllowAny | A | `bettingApi.futures()` | Futures markets |
| `/api/v1/betting/todays-games/` | GET | `core/views_odds_sports.py:3049` | AllowAny | A | `bettingApi.todaysGames()` | Today's Games tab (60s refetch) |
| `/api/v1/betting/brief/` | GET | `core/views_odds_sports.py:3237-3265` | AllowAny | D (**never reads persisted `SportsBettingBrief`** — §14.4) | `bettingApi.bettingBrief()` | Top Plays tab |
| `/api/v1/betting/sharp-action/` | GET | `core/views_odds_sports.py:3268-...` | AllowAny | D | `bettingApi.sharpAction()` | Sharp Action tab |
| `/api/v1/betting/track-record/` | GET | `core/views_odds_sports.py:3315-...` | AllowAny | B | `bettingApi.trackRecord()` | Records tab |
| `/api/v1/betting/pipeline-status/` | GET | `core/views_odds_sports.py:3524` | AllowAny | Cross-Cat (A+B+D freshness) | `bettingApi.pipelineStatus()` | 60s refetch when Records or Games tabs active |
| `/api/v1/sports/live-odds/` | GET | `core/views_odds_sports.py:1499-1500` | AllowAny | A | `bettingApi.liveOdds()` | Session 559 comment: "Public for Betting Dashboard UI" |
| `/api/v1/sports/live-odds-scores/` | GET | `core/views_odds_sports.py:1566-1567` | AllowAny | A | `bettingApi.liveOddsWithScores()` | Live Odds tab (**30s refetch** — `BettingPage.tsx:961`) |
| `/api/v1/sports/live-opportunities/` | GET | `core/views_odds_sports.py:579-580` | **IsAuthenticated** | B | `bettingApi.liveOpportunities()` | **AUTH DRIFT #1** — see §14.3 |
| `/api/v1/sports/betting-intelligence/` | GET | `core/views_odds_sports.py:2055-2056` | **IsAuthenticated** | B | `bettingApi.intelligence()` | **AUTH DRIFT #2** — see §14.3 |
| `/api/v1/odds/markets/` | GET | `core/views_odds_sports.py:683-684` | AllowAny | A | `bettingApi.markets()` | DEAD-RENDER-PATH `markets` tab consumer |
| `/api/v1/odds/bankroll/` | GET | `core/views_odds_sports.py:740-741` | AllowAny | C | `bettingApi.bankroll()` | DEAD-RENDER-PATH `bankroll` tab consumer |
| `/api/v1/odds/bankroll/stats/` | GET | `core/views_odds_sports.py:766-767` | AllowAny | C | `bettingApi.bankrollStats()` | DEAD-RENDER-PATH `bankroll` tab consumer |
| `/sports-hub/feed/` | GET | `core/views_spider_feed.py` (line UNKNOWN — Explore Agent 5 note) | (no explicit `@permission_classes`) | A | `sportsHubApi.getFeed()` | Hub tab news/injury feed |
| `/human/attention/` + variants | GET/POST | `core/views_autonomous_reasoning.py` (Explore Agent 2 note) | IsAuthenticated | C/F | `humanApi.attention()` + `.verify()` + `.decide()` | Watching tab + shared with CommandCenter/Boardroom |

**Endpoint count.** ~26 REST endpoints consumed by BettingPage (Explore Agent 2 counted 24 bettingApi methods + 5 humanApi + 1 sportsHubApi = 30 methods, with some methods calling the same endpoint with different params).

**AllowAny audit.** 20 of 47 betting/sports/odds view functions in `views_odds_sports.py` + `views_betting.py` carry `@permission_classes([AllowAny])` (Explore Agent 2 count). This is a **higher AllowAny rate than Cat D §3.3** (5-of-5 all-AllowAny at the Cat D scope) because Cat E consumes across all backend cats. Session-comment lineage: "Session 559: Public for Betting Dashboard UI" (`views_odds_sports.py:1500`), "Session 688: Allow public access for React frontend" (`views_odds_sports.py:684` + `:741` + `:767`). Frontend depends on this laxity — 2 endpoints (`live-opportunities` + `betting-intelligence`) still require auth and produce silent drift (§14.3).

### 6.2 WebSocket endpoints (defined but not consumed)

Verified via Explore Agent 3 + verifier-loop.

| WS Route | Consumer | Consumer file:line | Payload | Frontend subscription |
|---|---|---|---|---|
| `/ws/dbao/` | `NewPagesConsumer` | `core/new_pages_consumer.py:18` (route registered at `core/routing.py:369`) | `random.randint/uniform` mock metrics (see §14.1) | (not by BettingPage) |
| `/ws/dbao-dashboard/` | `NewPagesConsumer` | same as `/ws/dbao/` | same | (not by BettingPage) |
| `/ws/sports/` | `SportsConsumer` | `sports/consumers.py:14+` (route at `sports/routing.py:8`) | Sport updates group | **Zero subscribers from BettingPage** |
| `/ws/sports/odds/` | `OddsConsumer` | `sports/consumers.py` (route at `sports/routing.py:9`) | Live odds group | **Zero subscribers from BettingPage** |
| `/ws/sports/games/` | `GamesConsumer` | `sports/consumers.py` (route at `sports/routing.py:10`) | Games list group | **Zero subscribers from BettingPage** |

**Verdict:** No WS subscription from BettingPage.tsx. Grep of `frontend/src/pages/BettingPage.tsx` for `new WebSocket` / `useWebSocket` / `WEBSOCKET_URL` / `wss:` / `ws://` / `/ws/` returns zero matches (Explore Agent 3 + verifier). Live Odds "realtime" is misnamed — see §14.5.

### 6.3 PA tool coverage

**Grep of `core/services/pa_tool_schemas.py` for BettingPage-relevant tools:** existing PA tools reach betting data at the model layer (`Wager`, `MLPrediction`, `BettingStats`) but there is no dedicated `BettingPage.navigate_to_tab` or `betting_tool.get_dashboard_state` PA tool. Cat D §19.2 #10 flagged the same absence for brief-triggering; Cat E extends that observation to tab-level UI control. This means Rigby cannot script "show me the sharp action tab and describe what's on screen" — she must reach the underlying REST endpoints directly. Follow-on candidate per §19.1 #5.

### 6.4 Frontend polling cadence table

Verified per Explore Agent 3 + verifier-loop of `BettingPage.tsx:937-1032`.

| Tab | Query key | Endpoint | refetchInterval | Enabled |
|---|---|---|---|---|
| (always) | `betting-stats` | `bettingApi.stats()` | 60,000 ms | always |
| (always) | `betting-pipeline-status` | `bettingApi.pipelineStatus()` | 60,000 ms | `records` OR `games` |
| Hub | `hub-sports-news` | `sportsHubApi.getFeed('sports_news', 8)` | none (fetch on tab open) | `hub` |
| Hub | `hub-sports-injuries` | `sportsHubApi.getFeed('sports_injuries', 10)` | none | `hub` |
| Today's Games | `betting-todays-games` | `bettingApi.todaysGames(sport)` | 60,000 ms | `games` |
| Top Plays | `betting-brief` | `bettingApi.bettingBrief()` | none | `top_plays` |
| Sharp Action | `betting-sharp-action` | `bettingApi.sharpAction(sport)` | none | `sharp` |
| Arbitrage | `betting-arbitrage` | `bettingApi.arbitrageScan()` | none | `arbitrage` |
| Watching | `betting-watched-items` | (humanApi under the hood) | none | `watching` |
| Live Odds | `betting-live-odds` | `bettingApi.liveOddsWithScores()` | **30,000 ms** (`BettingPage.tsx:961`) | `odds` |
| Live Odds | `betting-line-movement` | `bettingApi.lineMovement()` | 60,000 ms | `odds` |
| My Wagers | `betting-wagers` | `bettingApi.wagers()` | none | always |
| Records | `betting-track-record` | `bettingApi.trackRecord(model)` | none | `records && recordsView === 'ai'` |
| DEAD-RENDER-PATH `bankroll` | `betting-bankroll` | `bettingApi.bankrollStats()` | none | `bankroll` (unreachable) |
| DEAD-RENDER-PATH `markets` | `betting-markets` | `bettingApi.markets()` | none | `markets` (unreachable) |

**Realtime verdict per tab:** All 9 visible tabs use polling or manual refetch — zero WS. "Live Odds" is a 30-second poll; the label is misleading. See §14.5.

---

## 7. Runtime Flows

**Q9 — What are the major runtime flows?**

### 7.1 Top Plays tab call-chain (F1 pattern replication from S1503+S1504 exemplars)

Per S1503 §14.1 F1-fold + S1504 §7.1 F1-fold pattern — explicit block for the highest-frequency read path.

```
User activates Top Plays tab in BettingPage
  → BettingPage.tsx activeTab state = 'top_plays'
  → useQuery({queryKey: ['betting-brief'], enabled: activeTab === 'top_plays'})
  → bettingApi.bettingBrief(sport?) (frontend/src/lib/api.ts:1229+)
    → axios.get('/api/v1/betting/brief/', {params: {sport?}})
      → request interceptor injects 'Authorization: Token <token>' header (api.ts:27-40)
      → HTTP GET /api/v1/betting/brief/
  → Django URL router (core/urls.py:XXX) matches → get_betting_brief
  → get_betting_brief (core/views_odds_sports.py:3237-3265)
    → @api_view(['GET']) @permission_classes([AllowAny])  # accepts anonymous
    → sport_key = request.GET.get('sport')
    → coordinator = SportsBettingCoordinator(sport_key=sport_key)  # per S1502 §5.1
    → brief = coordinator.generate_brief()  # in-memory computation
      → coordinator runs 4 market agents + assembles brief per S1502 §5 + S1504 §5
      → **NEVER READS OR WRITES SportsBettingBrief model** (verifier-loop verified)
    → Response({
        'success': True,
        'brief': {
          'generated_at': ...,
          'executive_summary': ...,
          'top_plays': [...],
          'agents_run': [...],
          'generation_time_seconds': ...
        }
      })
  ← HTTP 200 JSON payload
  ← axios returns response.data
  ← useQuery hook sets data
  → BettingPage renders top_plays block (`BettingPage.tsx:XXXX` — Top Plays render section)
```

**Load-bearing observations:**
- No cache — every tab activation triggers a fresh coordinator run (subject to react-query stale window).
- Persisted `SportsBettingBrief` writers exist (`core/tasks_content.py:3150` per S1504 §14.3 + `core/tasks.py:12187` per S1504 §14.3 second-writer via `run_all_desks_intelligence` F1 fold elevation) but this endpoint does not consult them.
- Every REST call to `/api/v1/betting/brief/` runs the full 4-agent coordinator synchronously. No SLO / performance budget documented for this endpoint. Explore Agent 2 saw `generation_time_seconds` field in payload — implicit self-instrumentation but not aggregated anywhere.

### 7.2 Live Odds tab realtime flow (30-second polling misnomer)

```
User activates Live Odds tab
  → activeTab = 'odds'
  → useQuery({queryKey: ['betting-live-odds'], refetchInterval: 30000, enabled: activeTab === 'odds'})
  → EVERY 30 SECONDS while tab active:
      bettingApi.liveOddsWithScores()
      → GET /api/v1/sports/live-odds-scores/ (views_odds_sports.py:1566-1567 AllowAny)
      → renders in Live Odds tab
```

**Load-bearing observation:** the tab is labeled "Live Odds" (`BettingPage.tsx:23`) but uses HTTP polling, not WS push. Even the more accurate 30-second cadence is a UI-latency-perception approximation, not true realtime. Any downstream design that assumes push-based updates will require reworking this tab or subscribing to `sports/routing.py:9` (`/ws/sports/odds/`).

### 7.3 Wager write flow (Cat C reach)

```
User submits wager form in My Wagers tab
  → onSubmit → bettingApi.placeBet(data)
  → POST /api/v1/betting/place/ (views_betting.py:19 AllowAny)
  → PlacedWager INSERT (core/models_betting.py:13) + PlacedWagerLeg rows (:108) if parlay
  → coordinator/verifier hooks per S1503 §5
```

**Load-bearing observation:** wager placement uses `AllowAny` — an anonymous user can theoretically POST a wager. The write is tied to a `user_id` field that may be nullable (per S1503 audit); confirmation deferred to Cat F (integration lens).

### 7.4 Watching → Verify flow (Cat F reach via humanApi)

```
User marks item as "Watching" in Live Odds or Arbitrage tab
  → (creates HumanAttentionItem via existing decision flow — precise trigger UNKNOWN in this audit)
User activates Watching tab → sees list of HumanAttentionItems with source_type=betting
User clicks Verify on outcome
  → humanApi.verify(itemId, outcome, profit, notes)
  → POST /human/attention/{itemId}/verify/ (IsAuthenticated)
  → BettingOutcomeVerifier per S1503 §5 hooks
```

**Load-bearing observation:** the Watching → Verify surface is where Cat F human-in-the-loop layer visibly touches sports data. `humanApi` is shared across CommandCenterPage, BoardroomTab, DecisionDetailModal (Explore Agent 4) — this is the only shared-with-mainline API surface in the BettingPage import list, and the only cross-domain frontend reach.

---

## 8. Data Ownership and Lifecycle

**Q16+Q17+Q18 — What data does it own / consume / produce?**

### 8.1 Data owned

**None.** Cat E has no persistence layer. The `activeTab` + filter + form state held in React `useState` is volatile (see §15.3).

### 8.2 Data consumed (from other cats)

| From | Via | For which tab |
|---|---|---|
| Cat A (odds ingestion) | 8 REST endpoints (`/live-odds*`, `/todays-games`, `/line-movement`, `/movers`, `/futures`, `/props`, `/markets`, `/sports-hub/feed/`) | Hub, Today's Games, Live Odds |
| Cat B (predictions + coordinator) | 5 REST endpoints (`/brief`, `/sharp-action`, `/arbitrage/scan`, `/arbitrage`, `/track-record`, `/live-opportunities` [AUTH DRIFT], `/betting-intelligence` [AUTH DRIFT]) | Top Plays, Sharp Action, Arbitrage, Records |
| Cat C (wagers + stats + bankroll) | 8 REST endpoints (`/stats`, `/recent`, `/wagers*`, `/place`, `/quick-pick`, `/wager`, `/bankroll*`) | Hub stats cards, My Wagers, DEAD-RENDER-PATH bankroll |
| Cat D (briefs) | `SportsBettingBrief` model **NEVER READ** — `/brief` endpoint bypasses persistence (§14.4) | Top Plays (via coordinator, not persistence) |
| Cat F (human-in-the-loop) | `humanApi.attention()` + `.verify()` + `.decide()` | Watching |

### 8.3 Data produced (to other cats)

| To | Via | Trigger |
|---|---|---|
| Cat C (PlacedWager row inserts) | POST `/v1/betting/place/`, `/v1/betting/quick-pick/`, `/v1/betting/wager/` | User submits wager form or Quick Pick |
| Cat C (wager settlement + cancellation) | POST `/v1/betting/wagers/{id}/settle/`, `.../cancel/` | User marks wager won/lost/cancelled |
| Cat F (HumanAttentionItem verification) | POST `/human/attention/{itemId}/verify/`, `/decide/` | User verifies watched item outcome |
| Signal Engine (`SignalCluster.pattern_type='sports_odds'`) | **No path** — see §10.2 + §14.6 | (never) |

### 8.4 Data lifecycle

**Frontend session lifecycle:**
- Tab position lives in `activeTab` React useState (cleared on refresh — see §15.3)
- React Query cache lives in memory (cleared on refresh)
- Auth token in localStorage via Zustand `useAuthStore` (per Explore Agent 1 — `frontend/src/lib/api.ts:29`)
- No IndexedDB / no service worker caching

---

## 9. Integrations With Other Domains

**Q14 + Q17 + Q18 + Q21 + Q22 — Integrations map**

### 9.1 Inbound consumers of Cat E surface

Cat E is a top-of-stack frontend consumer — nothing inbound consumes it. Its only "inbound" reach is the user (Chris) navigating in a browser.

### 9.2 Outbound dependencies

| Dep target | Cat | Interface | Verified path |
|---|---|---|---|
| Cat A (SpiderData / Games / Odds tables) | A | REST via `bettingApi` | S1501 §4 + §6.1 confirmed |
| Cat B (MLPrediction + SportsBettingCoordinator + 4 market agents) | B | REST via `bettingApi` | S1502 §4 + §5.1 + §6.1 confirmed |
| Cat C (Wagers + BettingStats + Bankroll) | C | REST via `bettingApi` (r/w) | S1503 §4 + §5 + §6.1 confirmed |
| Cat D (Briefs — indirectly via coordinator, never via persisted rows) | D | REST via `bettingApi.bettingBrief()` | §7.1 + §14.4 confirmed |
| Cat F (HumanAttentionItem verification) | F (via humanApi) | REST via `humanApi` | §7.4 confirmed |
| DBAO (schema/WS/env-var/header) | F (per parent §3.F) | **No frontend footprint** | Explore Agent 4 grep verified |

### 9.3 Cross-domain leak surface at frontend layer

**Verifier-loop of Explore Agent 4 claim.** Grep of `frontend/src/**` for `bettingApi` / `sportsHubApi` imports outside `pages/BettingPage.tsx` returned zero page-level consumers. `IntelligencePage`, `HubPage`, `CommandCenterPage`, `WorkspacePage` do not import sports data. Only `humanApi` is shared (used by `CommandCenterPage.tsx:929`, `BoardroomTab.tsx:108`, `DecisionDetailModal.tsx:87`, `unifiedStore.ts:177`) — but `humanApi` is Cat F human-in-the-loop, not sports-specific.

**Positive isolation signal for Cat F posture-decision.** BettingPage.tsx is the SOLE Cat E surface. This means island-posture cost on the frontend read axis is very low — the sports surface is already siloed from mainline React pages. Island cost is highest on the (d) shared-humanApi-surface axis noted in §4.2.

### 9.4 Delegations to other arcs

- **Cat F (S1506):** Category F cross-domain integration lens owns the DBAO product-line + Signal Engine emission absence + Memory Domain bridge posture-decision framing. Cat E provides evidence via §14.1 (MOCK-DATA-CONSUMER at `/ws/dbao/`) + §14.6 (Signal Engine emission absence at frontend read-out) + §14.5 (no WS subscription).
- **Memory Domain (Group 1300):** any user-side interaction learning (which tabs the user opens, which briefs the user marks helpful) is not captured or forwarded. See §14.8.

---

## 10. Event Flows

**Q19 + Q20 — What events emitted / should be emitted**

### 10.1 Events emitted from BettingPage.tsx (frontend)

**None.** The frontend does not emit domain events (no Redux/Zustand dispatch that broadcasts to backend, no telemetry beacon, no analytics event push).

### 10.2 Events NOT emitted (owed to Cat F evidence plan)

| Event class | What should emit | Current state | Precedent |
|---|---|---|---|
| `SignalCluster.pattern_type='sports_odds'` | Any user interaction with sharp/top-plays/arbitrage data | **No emission path exists** — grep of `frontend/src/**` + `core/services/**` for `SignalCluster.objects.create(pattern_type='sports_odds')` returns zero | S1502 §14.3 + S1503 §14.3 + S1504 §14.5 — 4-arc consumer-side pattern, Cat E extends to 5-arc |
| Learning-loop event to Memory Domain | Which briefs the user actually reads, which top plays get logged as wagers | **No emission path** | Memory Domain (S1300) not connected to sports frontend |
| Rigby PA notification for high-EV opportunities detected in Live Opportunities feed | PA tool trigger on arbitrage or high-EV pick | **No emission** — no PA tool listens for BettingPage user activity | Cat D §19.2 #10 — no PA tool for brief triggering; extends to Cat E |
| Frontend telemetry (tab open frequency, dwell time, refresh rate) | Would inform tab-consolidation decisions | **No emission** | — |

### 10.3 Frontend polling as event proxy

Because the frontend has no real event bus, the closest thing to "events" is react-query's polling. This is per-tab, per-query, and has no server-side registration — the backend cannot enumerate active frontend subscribers. This means "how many operators are watching Live Odds right now" is unanswerable server-side. See §14.7 + §15.6.

---

## 11. Existing Documentation

**Q10 — What existing documentation exists?**

| Doc | Coverage | Drift risk | Verifier-loop notes |
|---|---|---|---|
| `docs/topics/frontend.md:77-95` | "Betting Dashboard: 9 tabs" section | **HIGH DRIFT** per Explore Agent 5 — the section claims "9 tabs" but lists 12 names (Hub, Overview, Today's Games, Top Plays, Sharp, Arbitrage, Watching, Odds, Wagers, Records, Markets, AI Record) | Runtime shows 9 nav tabs + 2 DEAD-RENDER-PATH orphans = 11 declared. Neither the doc's 12-name nor the array's 9-nav shape matches perfectly; the doc appears to fold Bankroll and pre-consolidation naming into the same list |
| `docs/topics/frontend.md:38` | "Route: `/betting` → Betting Dashboard (9 tabs: …)" | LOW drift — 9-tab listing matches runtime | Confirmed against `BettingPage.tsx:16-26` |
| `docs/PLATFORM_INVENTORY.md:30` | "Frontend (React + Vite) — 61 routes in App.tsx, 5 workspace primary tabs, 9 betting dashboard tabs" | LOW drift | Runtime anchor confirmed |
| `docs/PLATFORM_INVENTORY.md:2039-2041` | Betting tabs array listed | LOW drift | Matches BettingPage.tsx:16-26 (the visible tabs) |
| `docs/handoffs/SESSION_1012_BETTING_TABS_POLISH.md:14-71` | Session 1012 handoff title claims "12 tabs" but body describes 9 | MEDIUM drift (editorial title error) | Phantom title count |
| `docs/handoffs/SESSION_1012_BETTING_TABS_POLISH.md:70` | "All 12 tabs overhauled" | MEDIUM drift | Same phantom count |
| `docs/handoffs/SESSION_1010_SPORTS_PREDICTIONS_AND_SYSTEM_CLEANUP.md:111` | "Removed isStockData conditional logic" | LOW drift | Confirms recent modification history |
| `docs/handoffs/SESSION_998B_BETTING_HUB_LIVE_SCORES.md` | Hub live scores build | LOW drift (name only inspected) | — |
| `docs/handoffs/SESSION_995_BETTING_OUTCOME_VERIFICATION.md` | Outcome verification | LOW drift | Backend feature; frontend may not touch |
| `docs/archive/handoffs-pre-800/SESSION_559_BETTING_DASHBOARD_UI.md` (and 560-563) | Historical BettingPage build | LOW drift (pre-history) | Predates S1012 overhaul |
| `docs/research/domains/sports/1500_sports_domain_scoping.md:431-449` | Parent §3.E Cat E scope | Matches; scope respected | — |
| `docs/research/domains/sports/1500_sports_domain_scoping.md:246-247` | Parent §2.5 evidence row: 1 route + 9 tabs | LOW drift | Confirmed |
| `docs/topics/` | No dedicated `betting*.md` or `sports*.md` topic doc | GAP | Coverage rides on `frontend.md` betting section only |
| `docs/narratives/` | No dedicated `FRONTEND.md` or sports frontend narrative | GAP | — |

**Doc-coverage summary.** Prior documentation covers Cat E at inventory level (tab counts + route) and at overhaul-history level (S1012 handoff). No prior doc covers the frontend → REST integration contract, WS-absence topology, or client-side auth trust surface. This audit is the first attempt.

---

## 12. Research Coverage

**Q11 + Q13 — Research coverage classification per playbook §12**

**Pre-S1505 state (post-S1500 parent scoping):** MODERATE.
- LIGHT inventory: `docs/topics/frontend.md` + `docs/PLATFORM_INVENTORY.md`.
- LIGHT scoping: `docs/research/domains/sports/1500_sports_domain_scoping.md §3.E`.
- LIGHT sibling context: S1501 + S1502 + S1503 + S1504 backend-side audits; each mentions but does not deep-audit frontend integration.

**Post-S1505 target:** DEEP.
- This audit is the first dedicated child audit for the sports frontend.
- 6 parallel Explore sub-agents (Agent 1 components, Agent 2 REST, Agent 3 WS, Agent 4 cross-domain, Agent 5 prior docs, Agent 6 drift/debt).
- Cross-linked to S1501-S1504 sibling audits per Anti-Duplication rule (§9).

**Post-S1599 xx99 target:** CANONICAL — after the Group 1500 canonical summary consolidates Cat E findings into the whole-domain posture-decision brief.

---

## 13. Architecture Maturity

**Q12 — Architecture maturity classification per playbook §12**

**Verdict:** **PARTIAL (mixed).**

### 13.1 Maturity breakdown per surface

| Surface | Maturity | Evidence |
|---|---|---|
| BettingPage.tsx (as god-component) | **WORKING** (functional but fragile — see §15.1) | Renders, fetches, mutates. No known crashes. But no tests + 3,023 lines + 17 useState = fragile. |
| 9 visible tabs (Hub, Games, Top Plays, Sharp, Arbitrage, Watching, Odds, Wagers, Records) | **WORKING** | Real REST endpoints, real data (Cat A/B/C reads + Cat C writes). |
| `markets` + `bankroll` DEAD-RENDER-PATH tabs | **EXPERIMENTAL** (coded but not reachable) | §14.2 — no nav button; only reachable via devtools |
| `/ws/dbao/` MOCK-DATA-CONSUMER | **EXPERIMENTAL** at best; misleading in practice | §14.1 — random.randint/uniform values |
| Auth drift on `live-opportunities` + `betting-intelligence` | **PARTIAL** — silent 401 for unauthenticated | §14.3 |
| Realtime (any tab) | **ABSENT** — polling only | §14.5 |
| Test coverage | **ABSENT** | §15.2 |
| Documentation | **PARTIAL** (drift-prone; frontend.md 12-vs-9-vs-11 phantom count) | §11 |

**Composite verdict:** **PARTIAL (mixed — WORKING at read-side tabs; DEAD-RENDER-PATH at markets/bankroll; MOCK-DATA-CONSUMER at /ws/dbao/; AUTH-DRIFT at 2 endpoints; NO-REALTIME across all tabs)**. Fifth distinguishing shape after S1501 fragile-contract-at-ingestion, S1502 armed-but-under-instrumented, S1503 armed-but-zero-fire, S1504 write-only-forgotten.

### 13.2 Why not STABLE

BettingPage has real data flowing through real endpoints and the operator (Chris) uses it — so it clears WORKING. It does not clear STABLE because:
1. Zero test coverage.
2. Two silent-drift permission mismatches (§14.3).
3. Two DEAD-RENDER-PATH tabs (§14.2).
4. Documentation drift (§11 topics/frontend.md 12-vs-9-vs-11).
5. `/ws/dbao/` MOCK-DATA-CONSUMER pattern present in the platform's WS namespace and reachable from other dashboards (if not this one) — architectural liability upstream.
6. 3,023-line god-component structure (§15.1) rivals backend service complexity.

### 13.3 Why not EXPERIMENTAL

The frontend renders real user-owned data (real Wager rows, real Cat B agent predictions, real Cat A odds) — the tab set has been shipped and used for months. This is functionally WORKING, not experimental.

---

## 14. Known Drift

**Q27 — What is drift?**

### 14.1 CRITICAL — `/ws/dbao/` MOCK-DATA-CONSUMER pattern

**Claim.** The `/ws/dbao/` WebSocket route (`core/routing.py:369`) is served by `NewPagesConsumer` (`core/new_pages_consumer.py:18-479`). Its `send_dbao_metrics` handler (`core/new_pages_consumer.py:310-331`) generates every metric field via `random.randint()` or `random.uniform()`:

```python
metrics = {
    'data_points': random.randint(2000000, 3000000),
    'active_queries': random.randint(300, 400),
    'uptime': random.uniform(98, 99.9),
    'data_processed': f'{random.uniform(1.5, 2.5):.1f}TB',
    'avg_response': f'{random.randint(30, 50)}ms',
    'accuracy_rate': random.uniform(85, 95),
    'performance': {
        'cpu': random.uniform(40, 70),
        'memory': random.uniform(50, 80),
        'disk': random.uniform(30, 60),
        'network': random.uniform(20, 50)
    }
}
```

**Verifier-loop confirmed** at read of `core/new_pages_consumer.py:310-331` (S1505 open, 2026-07-02).

**Why load-bearing for Cat E:** Parent §3.E called `/ws/dbao/` "a DBAO metrics channel, not tab-scoped realtime" — implying it exists as a plausible sports WS surface if wanted. The verifier-loop reveals a stronger claim: the consumer is a **mock-data placeholder**, not just off-scope. Any dashboard tab (Cat E or elsewhere) that subscribes reads randomized values that look like real data. This is not a "wrong channel" — it's a "channel that would mislead."

**New pattern class for the arc: MOCK-DATA-CONSUMER.** Distinct from:
- S1504 §14.3 WRITE-ONLY-AND-FORGOTTEN (real data written, never read).
- S1503 §14.1 ZERO-FIRE-BEAT (real task, real schedule, never fires).
- S1502 §14.4 PROVENANCE-STAMP-ABSENT (real writes but no owner tag).

Here: no real data is touched at any point. The consumer synthesizes numbers server-side, timestamps them (`timezone.now().isoformat()`), and pushes as WS messages that clients cannot distinguish from real data without reading source.

**Framing per F5 SIGN fold (Rigby cycle 1 batch 2 Q4 note).** The `/ws/dbao/` DBAO handler may be *intentionally* staged as a demo/placeholder for a non-sports dashboard surface (matching the S1502 F1 "armed but under-instrumented" precedent). The audit does not claim malicious intent. However, intent does not neutralize the risk: the consumer lives in a production WS namespace at a route that Cat E dashboards or Cat F integration paths might reasonably subscribe to, and the payload will pass any client-side "is this real" heuristic (it timestamps in the present, uses plausible numeric ranges, matches the message-type shape of the rest of the consumer's real-data handlers). This is an **operational-confusion / integration-signaling hazard**, not just an architectural anti-pattern.

**Severity:** CRITICAL architectural. The pattern is a documented anti-pattern (Chris's operator model requires real signal, not demo data — the platform's own value proposition per PLATFORM_WHAT_IT_IS is real signal from real spider network + real predictions). Whether the handler is intentional or accidental, the false-sense-of-coverage cost is the same.

**Cross-arc implications:** Category F owns the DBAO product-line materialization surface per parent §3.F. This finding raises the question "does DBAO carry any real state anywhere in the platform, or is it entirely a naming convention with no runtime data?" — a Category F evidence plan owed to xx99.

**Note (verifier-loop nuance):** the `send_dbao_metrics` handler is one of several handlers in `NewPagesConsumer` (`send_ai_nexus_status` at `new_pages_consumer.py:300` calls `self.get_real_nexus_status()` — real data path visible). The MOCK-DATA-CONSUMER classification applies specifically to the DBAO handler, not the whole consumer file. Other handlers may fetch real data.

### 14.2 HIGH — `markets` + `bankroll` DEAD-RENDER-PATH tabs

**Claim.** `BettingTab` TypeScript union at `BettingPage.tsx:14` declares 11 tab identifiers; the `tabs` array at lines 16-26 renders only 9 nav buttons; the remaining 2 (`markets` + `bankroll`) have wired query hooks (`BettingPage.tsx:968` + `:975`) and wired render conditionals (`BettingPage.tsx:2080` + `:2298`) but no nav button to activate.

**Verifier-loop confirmed** at read of BettingPage.tsx:16-26 + :968 + :975 + :2080 + :2298 (S1505 open).

**New pattern class: DEAD-RENDER-PATH.** Fully coded feature branches with no user-facing entry point. Distinguishing shape from S1501–S1504 sibling drift classes.

**Root cause hypothesis (SPECULATIVE — flag per playbook §14).** Session 1012 (S1012) "PR #1216 6 betting tabs refreshed" (per Explore Agent 5) may have removed `markets` + `bankroll` from the nav bar without cleaning up the type or the render conditionals. History confirmation via `git log --follow -p frontend/src/pages/BettingPage.tsx` is a follow-on candidate.

**Severity:** HIGH architectural — introduces cognitive overhead + refactor hazard. Any developer touching the tab set today may reintroduce nav for `markets` or `bankroll` without realizing the endpoints they consume still hit backend routes with 60-second staleness assumptions no one owns.

**Remediation options (research finding only, not implementation):**
- (a) Remove `markets` + `bankroll` from `BettingTab` union + delete conditional blocks + delete `bettingApi.markets()` + `bettingApi.bankroll()` + `bettingApi.bankrollStats()` if unused elsewhere.
- (b) Add nav buttons for `markets` + `bankroll` if they are intended future-visible tabs.

Neither is proposed here — this is a research audit. Follow-on candidate at §19.

### 14.3 HIGH — 2 permission-floor inconsistencies between frontend read-path expectations and backend IsAuthenticated decorators

**Claim.** Two REST endpoints called by `bettingApi` from BettingPage carry backend `@permission_classes([IsAuthenticated])` decorators, while all other Cat E-adjacent read-path endpoints under `/v1/betting/*` + `/v1/sports/live-odds*` + `/v1/odds/*public` carry `AllowAny`. The frontend caller code neither pre-gates the request nor surfaces the 401 to the user when it comes back:

| Frontend call | Consumed by tab | Backend view | View file:line | Backend permission |
|---|---|---|---|---|
| `bettingApi.liveOpportunities()` → `GET /api/v1/sports/live-opportunities/` | Not directly bound to a tab; called via cross-cutting react-query key. Historically fed Cat B agent output visible in Top Plays / Sharp Action / Arbitrage tabs per Explore Agent 2. (Precise tab consumer follow-on at §20.6.) | `live_betting_opportunities` | `core/views_odds_sports.py:581` (function def; `@permission_classes([IsAuthenticated])` decorator at line 580) | `IsAuthenticated` |
| `bettingApi.intelligence()` → `GET /api/v1/sports/betting-intelligence/` | Not directly bound to a tab; historically fed intelligence panels — precise tab consumer follow-on at §20.6. | `get_betting_intelligence` | `core/views_odds_sports.py:2057` (function def; `@permission_classes([IsAuthenticated])` decorator at line 2056) | `IsAuthenticated` |

**Verified-in-repo anchors (per F3 SIGN fold — Rigby Q9 recommendation #1).** Repo-tool verification during Rigby SIGN cycle 1 batch 3 confirmed:
- `core/views_odds_sports.py:580` `@permission_classes([IsAuthenticated])` decorator on `live_betting_opportunities` (function starts at 581).
- `core/views_odds_sports.py:2056` `@permission_classes([IsAuthenticated])` decorator on `get_betting_intelligence` (function starts at 2057).
- `core/urls.py:3085` maps `api/v1/sports/live-opportunities/` → `live_betting_opportunities`.
- `core/urls.py:3099` maps `api/v1/sports/betting-intelligence/` → `get_betting_intelligence`.

**Why load-bearing (per F1 SIGN fold — Rigby Q9 recommendation on tightening):**

Strictly speaking, the frontend does not "assume AllowAny" — it does not encode a permission assertion at all. The precise mechanic is:

- ProtectedRoute (`App.tsx:47-59`) redirects unauthenticated users to `/login`, so users reaching BettingPage are always authenticated in normal navigation.
- The axios interceptor (`api.ts:27-40`) injects the `Authorization: Token` header on each call IF `useAuthStore` has a token. If the token is missing (e.g., after silent expiry), the request fires without a token and hits the IsAuthenticated gate.
- `api.ts:48-56` (per Explore Agent 1) triggers logout on 401 **only for auth endpoints**; other 401s log a warning but do not surface UI error. **Silent failure at the caller.**
- Backend permission-floor inconsistency: the majority of Cat E read-path endpoints are AllowAny by explicit "Session 559: Public for Betting Dashboard UI" pattern (`views_odds_sports.py:1500`) + "Session 688: Allow public access for React frontend" pattern (`views_odds_sports.py:684`). These 2 endpoints are un-migrated to that pattern.

So the drift class is two-sided:
1. **Frontend side:** no 401 surfacing / no per-call auth gate — silent failure.
2. **Backend side:** permission-floor inconsistency with the platform's own "public read for dashboard" precedent.

Either side is a reasonable fix target. Cat F design-preparation should pick the canonical resolution (see §19.1 #3).

**Severity:** HIGH operational — silent 401 on 2 endpoints reachable from Top Plays / Sharp Action / Arbitrage tab families (per §6.1 Cat B ownership mapping); user sees blank data with no error indicator. Per Rigby Q6 "fix-first for correctness" nomination, this is the highest-severity finding for immediate user-facing impact — MOCK-DATA-CONSUMER (§14.1) is higher-severity for arc/governance interpretability risk.

**Remediation options:** either (a) migrate both endpoints to `AllowAny` (matches Session 559/688 "public read for dashboard" precedent + preserves anonymous preview access), or (b) add explicit auth check + UI error before frontend calls (matches ProtectedRoute assumption). Either is a Cat F design-preparation candidate.

**Cross-cat pattern:** matches S1503 §14.7 (all Cat C REST endpoints `AllowAny` regardless of auth-tier — the platform's read-side is permissive by design). Cat E extends observation: the permission floor is not uniform even inside a single dashboard.

### 14.4 HIGH — S1504 §14.3 SportsBettingBrief write-only-and-forgotten CONFIRMED at frontend AND REST endpoint

**Claim.** `get_betting_brief` at `core/views_odds_sports.py:3237-3265` calls `SportsBettingCoordinator.generate_brief()` and returns the coordinator result verbatim — **the persisted `SportsBettingBrief` model is never queried by this endpoint**. Grep of `frontend/src/**` for `SportsBettingBrief` returns zero matches. The 2 writers (`core/tasks_content.py:3150` + `core/tasks.py:12187` per S1504 §14.3) have zero readers at both persistence and consumption layers.

**Verifier-loop confirmed** at read of `views_odds_sports.py:3237-3265` (S1505 open).

**Severity:** HIGH architectural. S1504 verdict of write-only-and-forgotten is upheld and strengthened — not only is no consumer reading, but the REST endpoint that would obviously be the reader deliberately bypasses persistence. The persisted table is dead-weight state.

**Cross-cat pattern:** matches S1504 §14.3 owned finding; Cat E adds the frontend-and-REST-endpoint verification layer.

### 14.5 HIGH — Zero WebSocket subscription from BettingPage despite defined sports WS routes

**Claim.** `sports/routing.py:7-11` registers three WebSocket consumers (`SportsConsumer`, `OddsConsumer`, `GamesConsumer`) but `frontend/src/pages/BettingPage.tsx` never connects to any of them. All 9 visible tabs use react-query polling. Live Odds tab is misnamed — it uses 30-second polling (`BettingPage.tsx:961`), not WS push.

**Verifier-loop confirmed** at read of `sports/routing.py:7-11` + BettingPage.tsx:961 (S1505 open) + grep for WS patterns in BettingPage.tsx returned zero matches (Explore Agent 3).

**Severity:** HIGH architectural. The pattern extends the S1502+S1503+S1504 consumer-side realtime absence into Cat E: no arc-scope surface publishes or subscribes to sports realtime events despite the infrastructure being registered.

**Cross-cat pattern:** Category F integration lens should evaluate whether the sports WS routes are:
- (i) Placeholder infra staged for future use (like S1502 F1 "armed but under-instrumented"), or
- (ii) Legacy infra with an owner who left (like S1503 §14.1 zero-fire beat), or
- (iii) Genuinely dormant with no plan (delete candidate).

Follow-on candidate at §19.

### 14.6 MED — Zero Cat E → Signal Engine emission

**Claim.** BettingPage renders sharp-action + top-plays + arbitrage data flowing from Cat B agents through Cat D coordinator to the browser, but nothing publishes any of it to `SignalCluster`. Grep of `frontend/src/**` + `core/services/**` for `SignalCluster.objects.create(pattern_type='sports_odds')` returns zero.

**Verifier-loop confirmed** via Explore Agent 3 + Explore Agent 4 dual verification.

**Severity:** MED (POSTURE-DECISION-PENDING per S1502 F2 / S1503 §14.3 / S1504 F11 precedent).

**Cross-cat pattern:** extends 4-arc consumer-side pattern (S1502 §14.3 + S1503 §14.3 + S1504 §14.5) to 5-arc pattern. Signal Engine emission absence is now confirmed at ingestion (Cat A), prediction (Cat B), wager settlement (Cat C), content generation (Cat D), and frontend read-out (Cat E). Cat F evidence plan owes the arc-close synthesis to xx99 (S1599).

### 14.7 MED — Frontend polling has no server-side subscriber registration

**Claim.** react-query polling is client-side only. The backend cannot enumerate "how many operators are currently watching Live Odds tab" or apply rate-limiting per active tab.

**Verifier-loop:** confirmed — polling requests are indistinguishable from any other REST call server-side.

**Severity:** MED operational. Implication for Cat F: any island-posture decision that requires per-operator activity awareness cannot be met by the current architecture; upgrade path is (a) migrate to WS with backend-tracked channel groups (using existing `sports/routing.py` infrastructure) or (b) add explicit "I'm watching this now" beacon endpoints.

### 14.8 MED — Zero learning-loop path from BettingPage to Memory Domain (S1300)

**Claim.** No frontend beacon captures which tabs the user opens, which briefs the user marks helpful, which top plays get converted to wagers. Grep of `frontend/src/**` for Memory Domain (S1300) API surface reach returns zero.

**Verifier-loop:** confirmed — Explore Agent 4 grep result.

**Severity:** MED (POSTURE-DECISION-PENDING per S1502 F4 / S1503 §14.4 / S1504 F11 precedent).

**Cross-cat pattern:** extends Memory Domain bridge absence across Cat B, Cat C, Cat D, Cat E. Cat F evidence plan owed.

### 14.9 MED-LOW — Documentation drift on tab count (topics/frontend.md 12-vs-9 phantom)

**Claim.** `docs/topics/frontend.md:77-95` claims "Betting Dashboard: 9 tabs" but lists 12 tab names. `SESSION_1012` handoff title claims "12 tabs" but body describes 9. Runtime is 9 nav tabs + 2 DEAD-RENDER-PATH = 11 declared.

**Severity:** MED-LOW documentation drift. Editorial rather than runtime. Fold into follow-on `verify_doc_claims --only-drift` PR.

---

## 15. Known Technical Debt

**Q26 — What is technical debt?**

### 15.1 CRITICAL per S1504 §15.12 F4-fold sibling precedent — Zero test coverage for BettingPage.tsx

**Claim.** Grep of `frontend/**/*.test.{ts,tsx}` + `frontend/**/*.spec.{ts,tsx}` returns zero matches targeting `BettingPage` or `bettingApi` (Explore Agent 6 verified).

**Verifier-loop:** confirmed via Explore Agent 6 methodology.

**Severity:** HIGH (per S1504 §15.12 F4-fold precedent — Cat D promoted MED-HIGH → HIGH for zero-test-coverage as reliability-risk multiplier). Cat E is a 3,023-line god-component with 14 useQuery hooks + 17 useState declarations + 5 inline sub-components + 2 DEAD-RENDER-PATH tabs + 2 AUTH-DRIFT endpoints — zero test coverage on this surface is HIGH risk-multiplier for regression on any single-line change.

**Follow-on candidate at §19:** integration test suite targeting all 9 tabs + at minimum mock the 2 AUTH-DRIFT + 2 DEAD-RENDER-PATH corner cases.

### 15.2 HIGH — 3,023-line god-component

**Claim.** BettingPage.tsx = 3,023 lines verified via `wc -l` (S1505 open). Contents include:
- 5 inline sub-components (StatCard, WagerRow, ArbitrageCard, WatchedItemCard, PickDetailsDrawer)
- 14 useQuery hooks (Explore Agent 6 count)
- 17+ useState declarations
- 10 inline TypeScript interfaces
- 9 nav tab render blocks + 2 DEAD-RENDER-PATH conditional blocks

**Severity:** HIGH — rivals backend service complexity per playbook §13 Agent 2 threshold (3,000 lines for god-service check). Frontend has no analogous threshold in the playbook, but the shape is identical: single-file complexity that resists testing, refactoring, and code review.

**Remediation options (research finding only):**
- (a) Extract per-tab components: `HubTab.tsx`, `GamesTab.tsx`, ..., `RecordsTab.tsx` under `frontend/src/pages/betting/tabs/`.
- (b) Extract sub-components: `StatCard.tsx`, `WagerRow.tsx`, etc.
- (c) Extract types to `frontend/src/types/betting.ts`.
- (d) Extract useQuery hooks to `useBettingData()` per-domain: `useBettingStats()`, `useBettingWagers()`, etc.

Any refactor requires the test suite from §15.1 to land first.

### 15.3 MED — Zero client-side state persistence

**Claim.** All BettingPage state is React `useState`. Tab position + filters + expanded rows + form drafts are lost on refresh. Grep of `frontend/src/pages/BettingPage.tsx` for `localStorage` / `sessionStorage` / `IndexedDB` returns zero.

**Verifier-loop:** confirmed via Explore Agent 1 grep + verifier-loop.

**Severity:** MED operational — UX degradation. User loses tab position + all in-flight filter state on any page reload. React Query cache lives in memory only.

**Remediation options (research finding only):**
- (a) URL params for tab state: `/betting?tab=odds` — enables shareable links.
- (b) localStorage for filter state + expanded rows.
- (c) Zustand slice for BettingPage-scoped persistence.

### 15.4 MED — Inline TypeScript interfaces (no shared betting types module)

**Claim.** 10+ TypeScript interfaces declared inline in BettingPage.tsx (`StatCardProps`, `RecordBreakdown`, `SportStats`, `BettingStatsData`, `WagerLeg`, `WagerRowProps`, `ArbitrageCardProps`, `WatchedItem`, `WatchedItemCardProps`, `PickDetail`). No shared `frontend/src/types/betting.ts` module.

**Severity:** MED architectural — refactor brittleness; parallel evolution risk if any type is re-declared in another consumer.

### 15.5 HIGH (elevated per F2 SIGN fold — Rigby Q5 "structural debt behind auth-drift + payload-drift") — No API contract source-of-truth (no shared response types, no schema-generated clients)

**Claim.** `bettingApi` at `frontend/src/lib/api.ts:1229-1276` returns responses accessed via `.data` property with no exported response types. Explore Agent 1 confirmed. There is no zod / io-ts / OpenAPI-generated / TS-derived-from-DRF-serializer / handwritten shared types module targeting the betting REST surface.

**Reframe (Rigby SIGN cycle 1 Q5 fold).** Prior to this fold this was scoped as a MED cosmetic debt item at the Cat E level. Rigby elevated it to a **first-class structural debt class**: "no single source of truth for API schemas" is the parent cause behind:

1. **§14.3 AUTH-DRIFT.** Without schema-generated clients, permission-class drift between frontend expectation and backend decorator is invisible until 401 fires at runtime.
2. **§15.4 inline TypeScript interfaces.** Without a shared type module, each caller re-declares its own approximation of the response shape.
3. **§14.9 documentation drift on tab count.** Even the tab set is documented differently across `docs/topics/frontend.md` (12 names / "9 tabs" phantom), `PLATFORM_INVENTORY.md` (9 tabs), and the runtime type union (11 declared) because there is no single authoritative schema that both sides derive from.
4. **General fragility of the read-path.** If backend serializer shape changes (field rename, nested restructure, nullable field), frontend duck-type access silently drops the field with no compile-time error.

**Severity:** HIGH structural. This is the parent debt class behind several §14 drift findings + §15 debt findings + §11 documentation drift.

**Remediation options (research finding only):**
- (a) Adopt an OpenAPI generator against Django REST Framework's schema output, generate TypeScript client + response types at build time.
- (b) Adopt DRF-side zod schemas exported to frontend at build time.
- (c) Handwrite shared `frontend/src/types/api-sports.ts` module targeting all 20+ betting endpoints. Cheapest, most fragile.

Cat F design-preparation candidate. This is the most-leverage structural debt call in the audit.

### 15.6 MED — Minimal error handling + no error boundaries

**Claim.** Explore Agent 6 counted only 1 visible error state (`placeBetMutation.isError`). Most useQuery hooks fail silently. No React error boundary wraps BettingPage.

**Severity:** MED — unhandled promise rejection or query failure produces blank tabs with no user feedback.

---

## 16. Boundary Violations

**Q24 — What services violate boundaries?**

### 16.1 Frontend module boundaries — clean

Grep of BettingPage.tsx imports (Explore Agent 6): only `@/lib/api`, `@/lib/cn`, lucide-react icons, react-query, react. No cross-page imports (BettingPage does not import from `frontend/src/pages/*` siblings). No backend-domain imports.

**Verdict:** zero boundary violations at the frontend layer.

### 16.2 Shared humanApi surface

Slight coupling: `humanApi` is used by BettingPage, CommandCenterPage, BoardroomTab, DecisionDetailModal — sharing at the API-cluster level. This is not a violation per se (humanApi is a Cat F cross-cutting surface), but it means Cat E cannot evolve humanApi shape without touching non-sports consumers. Noted in §4.2 (d) island-cost axis.

---

## 17. Duplicate or Overlapping Systems

**Q23 — What models overlap with other domains?**

Cat E has no persistence layer, so model-overlap is not directly applicable. Overlapping consumption patterns:

| Overlap | Description | Severity |
|---|---|---|
| `bettingApi.stats()` vs `bettingApi.recent()` | Both read from `BettingStats` per Cat C; potentially duplicative | LOW (different views of same data) |
| `bettingApi.liveOdds()` vs `bettingApi.liveOddsWithScores()` | Two live-odds endpoints; frontend uses the latter (with ESPN score enrichment) at 30s cadence | LOW (`liveOdds` unused-in-tab per Explore Agent 3) |
| `SportsBettingBrief` (persisted) vs `SportsBettingCoordinator.generate_brief()` (in-memory) | The persisted model is written by Cat D but never read; the in-memory coordinator run is what serves frontend requests | HIGH — see §14.4 (write-only-forgotten, upheld at frontend + REST) |
| `bettingApi.watchedItems()` vs `humanApi.attention()` | Watching tab appears to use both patterns — precise routing UNKNOWN in this audit | UNKNOWN (follow-on) |

---

## 18. Ownership Gaps

**Q25 — What ownership is unclear?**

### 18.1 No CODEOWNERS row for BettingPage.tsx

Grep of `.github/CODEOWNERS` for `frontend/src/pages/BettingPage.tsx` returns no match (Explore Agent 6 confirmed).

**Verdict:** ownership is UNKNOWN. Implicit maintainer: Chris. This matches the platform-wide pattern (most files uncovered by CODEOWNERS).

### 18.2 No dedicated topic doc for betting frontend

`docs/topics/betting*.md` does not exist. Coverage rides on `docs/topics/frontend.md` general doc.

### 18.3 No frontend-side owner for AUTH-DRIFT resolution

The 2 AUTH-DRIFT endpoints (§14.3) sit on a boundary: backend view sets `@permission_classes([IsAuthenticated])`, frontend caller assumes AllowAny. Neither owner has clearly signed up for reconciliation. This is a Cat F design-preparation candidate.

### 18.4 No frontend-side owner for DEAD-RENDER-PATH cleanup

The 2 DEAD-RENDER-PATH tabs (§14.2) have no reason-comment or JIRA-linked ownership in the code. Root cause hypothesis (S1012 partial nav removal) is speculative.

---

## 19. Recommended Future Research

**Q28 — What should be researched next?**

Ranked by architectural uncertainty × risk × unblocked flows per playbook §19.

### 19.1 CRITICAL tier (dependency-ordered)

1. **[Cat F evidence plan owed to xx99] DBAO product-line footprint audit** — MOCK-DATA-CONSUMER at `/ws/dbao/` (§14.1) is the visible tip. Category F audit (S1506) must inventory all references to DBAO across backend + frontend + docs and answer: does DBAO carry any real data anywhere in the platform, or is it entirely a naming convention with no runtime state? This is load-bearing for xx99 posture-decision brief.

2. **[Cat F evidence plan owed to xx99] Cat E DEAD-RENDER-PATH root-cause investigation** — `markets` + `bankroll` tabs (§14.2). `git log --follow -p frontend/src/pages/BettingPage.tsx` to identify when nav buttons were removed. If removed intentionally, either restore nav or delete conditional blocks + type members. If removed accidentally, restore. Follow-on PR after xx99.

3. **[Cat F evidence plan owed to xx99] AUTH-DRIFT resolution proposal** — the 2 IsAuthenticated endpoints (§14.3) need a decision: migrate to AllowAny (matches Session 559/688 pattern) or add frontend auth-check + UI error. Cat F design-preparation candidate.

4. **[Cat F evidence plan owed to xx99] Cat E → Signal Engine emission bridge design** — §14.6 extends 4-arc pattern to 5-arc pattern. Whether SignalCluster.pattern_type='sports_odds' should carry frontend user activity is a Chris-gated posture decision.

5. **[Cat F evidence plan owed to xx99] Sports WS routes ownership** — §14.5 + §6.2. Are `/ws/sports/` + `/ws/sports/odds/` + `/ws/sports/games/` staged for future use, legacy with no owner, or delete candidates? Cat F design-preparation candidate.

### 19.2 HIGH tier

6. **BettingPage.tsx integration test suite** — §15.1. Zero test coverage on 3,023-line god-component with 2 DEAD-RENDER-PATH + 2 AUTH-DRIFT + 5 inline sub-components is the largest single reliability risk. Must land before any refactor per §15.2.

7. **BettingPage.tsx god-component split** — §15.2. Extract per-tab components + sub-components + types + custom useBettingData() hooks. Contingent on §19.2 #6.

8. **PA tool for BettingPage state** — §6.3. Add `betting_tool.get_dashboard_state` + `betting_tool.navigate_to_tab` so Rigby can reason about what's on-screen. Cat D §19.2 #10 pattern extended.

9. **Frontend polling-vs-WS decision** — §14.5 + §14.7 + §15.6. Should Live Odds tab move to WS push via existing `/ws/sports/odds/` route? Cat F design-preparation candidate.

### 19.3 MED tier

10. **Client-side state persistence spec** — §15.3. URL params for tab state + localStorage for filters. UX improvement.

11. **Response type module for betting API** — §15.5. Export TypeScript interfaces from api.ts or extract to `frontend/src/types/betting.ts`.

12. **Documentation drift fix for topics/frontend.md 12-vs-9-vs-11 phantom** — §14.9. Fold into `verify_doc_claims --only-drift` PR.

13. **Learning-loop bridge to Memory Domain (S1300)** — §14.8 extends 4-arc pattern to 5-arc pattern. Design-preparation candidate for what user-interaction telemetry should feed Memory Domain.

### 19.4 LOW tier

14. **Auth-drift silent-401 handling improvement** — §14.3. Even if the endpoint permission classes are the right answer, the frontend needs UI-visible error not silent warning.

15. **CODEOWNERS coverage for `frontend/src/pages/BettingPage.tsx`** — §18.1. Add an implicit-maintainer row.

---

## 20. Appendix

### 20.1 Files inspected

**Verifier-loop reads (parent-Claude direct reads):**
- `frontend/src/pages/BettingPage.tsx:1-100` + `:955-970` + `:2070-2080` + `:2288-2300`
- `frontend/src/App.tsx:85-95`
- `core/new_pages_consumer.py:300-350`
- `sports/routing.py:1-12`
- `core/views_odds_sports.py:3237-3270` + permission decorator index (`:52-3525`)

**Explore sub-agent read paths (aggregated):**
- Agent 1 (Components): `BettingPage.tsx`, `api.ts`, `App.tsx`, misc `frontend/src/components/*`
- Agent 2 (REST): `core/urls*.py`, `core/views_odds*.py`, `core/views_betting.py`, `frontend/src/lib/api.ts`
- Agent 3 (WS): `core/routing*.py`, `core/asgi*.py`, `core/consumers*.py`, `core/new_pages_consumer.py`, `sports/routing.py`, `sports/consumers.py`, `frontend/src/**/*.ts,tsx`
- Agent 4 (Cross-domain): `frontend/src/**` grep for `bettingApi`/`sportsHubApi`/`humanApi`/`dbao`; `core/views_odds_sports.py:3237` + `:3317`; `core/models_signal_intelligence.py`
- Agent 5 (Docs): `docs/topics/`, `docs/handoffs/`, `docs/research/domains/sports/`, `docs/PLATFORM_INVENTORY.md`, `docs/PLATFORM_WHAT_IT_IS.md`, `docs/archive/handoffs-pre-800/`
- Agent 6 (Drift/Debt): `BettingPage.tsx`, `api.ts`, `frontend/**/*.test.{ts,tsx}`, `.github/CODEOWNERS`

### 20.2 Grep patterns used

- `new WebSocket|useWebSocket|WEBSOCKET_URL|wss://|ws://|/ws/` (BettingPage WS check — zero matches)
- `localStorage|sessionStorage|IndexedDB` (BettingPage persistence check — zero matches)
- `activeTab === 'markets'|activeTab === 'bankroll'` (DEAD-RENDER-PATH verify — 4 matches at lines 968/975/2080/2298)
- `SignalCluster.objects.create.*pattern_type.*sports_odds` (Signal Engine emission check — zero matches)
- `SportsBettingBrief` in `frontend/src/**` (frontend read check — zero matches)
- `@permission_classes` in `core/views_odds_sports.py` (auth-drift audit — enumerated for all 47 endpoints)
- `dbao|DBAO` in `frontend/src/**` (DBAO frontend footprint — zero matches)

### 20.3 TypeScript interfaces inventoried in BettingPage.tsx

Per Explore Agent 1 (line numbers verified):
1. `BettingTab` union — line 14 (11 tab identifiers)
2. `StatCardProps` — line 28
3. `RecordBreakdown` — line 59
4. `SportStats` — line 65
5. `BettingStatsData` — line 73
6. `WagerLeg` — line 92
7. `WagerRowProps` — line 105
8. `ArbitrageCardProps` — line 260
9. `WatchedItem` — line 348
10. `WatchedItemCardProps` — line 369
11. `PickDetail` — line 574

### 20.4 Sub-components inline in BettingPage.tsx

Per Explore Agent 1:
- `StatCard` — line 36
- `WagerRow` — line 126
- `ArbitrageCard` — line 270
- `WatchedItemCard` — line ~400 (line UNKNOWN precisely per Explore Agent 1 note)
- `PickDetailsDrawer` — line 602

### 20.5 Verifier-loop corrections (pre-SIGN)

**Correction 1 (Agent 1 vs Agent 6 conflict):** Agent 1 said `markets` + `bankroll` are DEAD (no UI button). Agent 6 said the orphan-tab claim is REFUTED because they ARE rendered. Verifier-loop resolves: **both are correct in different ways**. The tabs ARE rendered conditionally (lines 968/975/2080/2298) but are NOT in the tabs array (line 16-26), so they are unreachable via UI. This is neither "orphan" nor "not-orphan" but a distinct pattern class: **DEAD-RENDER-PATH** — fully wired feature branches with no user-facing entry point. Folded into §14.2 with the new pattern class name.

**Correction 2 (Agent 3 payload analysis):** Agent 3 correctly identified the `send_dbao_metrics` handler as random.randint/uniform, but verifier-loop clarified nuance: the same `NewPagesConsumer` class has other handlers (`send_ai_nexus_status` at line 300) that call real-data getters. The MOCK-DATA-CONSUMER pattern applies to the DBAO handler specifically, not the whole consumer file. Folded into §14.1 note.

**Correction 3 (Agent 2 endpoint count):** Agent 2 counted "47 total betting/sports/odds endpoints" — this is the union of views_odds_sports.py + views_betting.py permission decorator grep matches. Not all 47 are consumed by BettingPage; the frontend-consumed subset is ~26 endpoints (Explore Agent 2 method count minus overloads). Folded into §6.1 endpoint count note.

**Correction 4 (Agent 5 tab-count phantoms):** Agent 5 identified drift in `docs/topics/frontend.md:77-95` claiming "9 tabs" while listing 12 names. Verifier-loop: the doc is drift-prone but the runtime state is 9 nav + 2 DEAD-RENDER-PATH = 11 declared. Cataloged in §14.9.

**Correction 5 (Agent 6 vs Agent 3 test-coverage evidence):** Agent 6 confirmed zero test files. Agent 3 did not audit tests. No conflict; verifier-loop confirms Agent 6 zero-test finding.

### 20.6 Unresolved unknowns

Per playbook §14 (UNKNOWN acceptable). Follow-on candidates:

1. `/api/v1/betting/pipeline-status/` view — precise file:line missing (Explore Agent 2 flagged `views_odds_sports.py:3524`). Cat ownership: cross-cat freshness aggregator per method name.
2. Watching tab data source — precise `humanApi.attention()` call vs Watching-specific endpoint UNKNOWN in this audit.
3. `sports_hub_feed` view function precise file:line (Explore Agent 5 flagged `core/views_spider_feed.py` no line).
4. WatchedItemCard sub-component precise line number (Explore Agent 1 note "line ~400").
5. `git log --follow -p frontend/src/pages/BettingPage.tsx` for DEAD-RENDER-PATH root cause (deferred to §19.1 #2).

### 20.7 Conflicts between sources (resolved)

- Agent 1 called `markets` + `bankroll` "orphan" (no button); Agent 6 called claim REFUTED (they ARE rendered). Verifier-loop resolved via DEAD-RENDER-PATH pattern class in §14.2.
- `docs/topics/frontend.md:77-95` "9 tabs, 12 names" phantom: runtime authority resolves via §14.2 + §14.9.

### 20.8 SIGN fold notes

**Rigby Full SIGN cycle 1** ran on fresh isolation pin `pa-546de7ebe8c8b885` at S1505 draft close, 2026-07-02.

**D48 preemptive stability probe — 8th arm.** Warmup ping delivered "READY" with clean tool runs (`cockpit_tool.worker_health` + `infra_health_tool.dependency_matrix` = 4 healthy workers + 7-of-7 healthy components). Extends S1405+S1406+S1499+S1501+S1502+S1503+S1504 7-arc D48 pattern to **8-arc pattern**. Cleanest arm alongside S1503 + S1504 (three consecutive fully-clean arms). CODIFICATION-READY at 8-arc threshold — xx99 (S1599) §10.2 owns eventual playbook v3 §15 codification recommendation with 8-arc evidence base.

**SIGN cycle 1 outcome.** SIGN-with-edits at High confidence. Cycle ran cleanly across 3 substantive SIGN batches (1 warmup + Q1-Q3 architectural + Q4-Q6 architectural + Q7-Q9 grep-verified). Zero worker-instability observed. **Confidence upgrade High** at batch 3 after Rigby grep-verified all load-bearing file:line claims (BettingPage.tsx line count, tabs declared/rendered, AUTH-DRIFT permission decorators, urls.py path mappings, SportsBettingBrief writers vs readers).

**F1-F5 folds applied at draft commit-time (Rigby cycle 1 batch 2-3):**

- **F1 — §14.3 wording tightening.** Reframed frontend side from "assumes AllowAny" to "no 401 surfacing / no per-call auth gate" and separately named the backend-side "permission-floor inconsistency." Two-sided drift class explicit. Rigby Q9 recommendation on canonicalization framing.

- **F2 — §15.5 elevation to HIGH structural debt class.** Renamed and promoted the "no frontend response types" MED item to "No API contract source-of-truth (no shared response types, no schema-generated clients)" as a HIGH first-class structural debt. Called out as the parent cause behind §14.3 AUTH-DRIFT, §15.4 inline interfaces, §14.9 tab-count doc drift, and general read-path fragility. Rigby Q5 elevation nomination.

- **F3 — §14.3 verified-in-repo anchors snippet.** Added a "Verified-in-repo anchors" subsection to §14.3 explicitly enumerating the 4 grep-verified anchor points from Rigby's Q8 pass (both permission decorators + both urls.py mappings). Rigby Q9 recommendation #1.

- **F4 — §14.3 tab-consumer identification.** Named `bettingApi.liveOpportunities()` and `bettingApi.intelligence()` as feeding Top Plays / Sharp Action / Arbitrage tab families (per §6.1 Cat B ownership mapping); flagged precise per-tab consumer identification as follow-on at §20.6. Rigby Q9 recommendation #3.

- **F5 — §14.1 MOCK-DATA-CONSUMER intentionality nuance.** Added intent-neutrality framing paragraph to §14.1: acknowledged that the `/ws/dbao/` handler may be intentionally staged as a demo/placeholder without weakening the CRITICAL classification. Reframed as "operational-confusion / integration-signaling hazard" per Rigby Q4 nuance while preserving CRITICAL severity.

**Do-not-regress notes for PR:** preserve §2.1 Cat E contract statement (5 guarantees + 11 non-guarantees) + preserve F1-F5 folds per §20.8 detailed enumeration.

**Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** — matches S1501 + S1502 + S1503 + S1504 cycle-1-predicts-cycle-2 pattern. Fresh SIGN pin `pa-546de7ebe8c8b885` retired at S1505 close via `session_tool.retire`.

---

**End of S1505 Cat E Sports Frontend Surface Audit (draft — SIGN cycle 1 SIGN-with-edits at High confidence — F1-F5 folds landed at commit-time)**
