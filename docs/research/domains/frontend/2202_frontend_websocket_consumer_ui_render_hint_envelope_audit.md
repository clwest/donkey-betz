---
title: "Group 2200 — Cat B — WebSocket Consumer Surface + `ui.render_hint` Envelope Audit (S2202 P2)"
status: draft (post-Rigby-SIGN-cycle-1 SIGN-with-edits at HIGH confidence via dedicated SIGN pin pa-e786b77eb4c842b2 retired via session_tool.retire; 19 folds landed pre-commit-gate; awaiting Chris close-card ratification)
session: 2202
child_slot: P2_cat_b
domain_slug: frontend
research_group: 2200
mission_type: child_audit
date: 2026-07-05
arc_pin: pa-f7fd5016600f4513
head_commit_at_open: 82570a90
authority: |
  P2 child audit under Group 2200 Frontend (Contract-Surface arc). Scope
  inherited verbatim from parent scoping §5 Child B block
  (`2200_frontend_domain_scoping.md`) + parent §7.1 leak-vector guardrails
  + S2200 §5 Child B Rigby SIGN cycle 1 folds (Q1 per-surface reporting +
  Q5 B1/B2 sub-axes + Q10 timebox + sampling + Q2/Q6.6 T0/Gate =
  decision + measurement gate NOT implementation gate).

  This doc is RESEARCH AUDIT only. It captures a **static snapshot** of the
  backend WebSocket consumer surface + frontend subscription map + envelope
  conformance rate at HEAD `82570a90` on `main` (2026-07-05, LOCAL
  environment). It enumerates the WebSocket consumer registry across
  `core/routing.py`, `sports/routing.py`, `intelligence/routing.py`,
  `ai_core/routing.py`, `ai_core/intelligence/routing.py` (**125 route
  entries** — significantly larger than parent scoping §5 Child B estimate
  of "~33+" — flagged for reconciliation at xx99), maps each to its
  frontend subscriber(s) via `useWebSocket` hook (**8 subscription sites
  across 7 files**), classifies MOCK-DATA / REAL / HYBRID / EMPTY /
  candidate DEAD posture across the registry, measures `ui.render_hint`
  envelope conformance rate (**0/40 emit sites — 0% conformance**), and
  delivers POSTURE-DECISION evidence toward the enforcement-locus
  recommendation (registration-time vs runtime vs defer) per §20.6.

  Explicit non-scope per parent §7 + §7.1 leak-vector guardrails:
  - Does NOT propose a new envelope schema — the S2003 §10.3.4 D4 spec
    is the target contract; envelope-authorship is out-of-arc regardless
    of measured adoption rate.
  - Does NOT wire enforcement — T0/Gate at Child B = decision + measurement
    gate, NOT implementation gate (per S2200 §5 D8).
  - Does NOT propose auth-session model changes (Group 2400 guardrail);
    WS auth-wrapper hygiene is symptomatic + descriptive only.
  - Does NOT propose PA behavioral spec for PA-adjacent consumers
    (Group 2600 guardrail); PA WS surface is treated as an inventory row
    only.
  - Does NOT design an API contract source-of-truth — that IS Child C
    (S2203) scope; observed WS payload shapes are inventoried only insofar
    as they inform envelope conformance measurement.
  - Does NOT audit persistent-state discipline for `usePageTracking()`
    fire-and-forget Redis counters — S2200 §5 Q6 CLEAN fold routed non-WS
    FE→BE emissions to Child D S2204 (persistence side-effect surface).
  - Does NOT audit the mobile app (Group 2300).
  - Does NOT delete DEAD-CONSUMER candidates; cleanup is post-arc T-slot.

  Load-bearing inheritance chain re-attested at S2202 open:
  - PLATFORM_INVENTORY §Frontend row (61 routes, 5 workspace tabs, 9
    betting tabs) — verified 2026-07-02 against runtime; **no WS
    consumer count line exists in inventory — flagged for xx99
    inventory-augmentation.**
  - S1505 §14.1 F5 MOCK-DATA-CONSUMER `/ws/dbao/` — re-verified UNCHANGED
    at HEAD `82570a90` (see §14 F1); `send_dbao_metrics` still emits
    `random.randint()` / `random.uniform()` payloads at
    `core/new_pages_consumer.py:310-331`.
  - S1505 §14.5 zero-WS-subscription for 3 sports routes — re-verified
    UNCHANGED at HEAD `82570a90` (see §14 F2); `BettingPage.tsx` still
    zero `useWebSocket` / `new WebSocket` / `wss:` / `/ws/` references.
  - S2003 §10.3.4 D4 `ui.render_hint` envelope contract (design-canonical,
    runtime-unenforced) — Child B measures adoption rate, does not design
    schema.
  - S2099 §14.3.4 F16 "envelope absent + unenforced" — re-verified
    SYSTEMIC at HEAD `82570a90` (see §14 F3); 0/40 emit sites conform.
  - S2104 §17.3 + §20.1 retrieval-surface counter operator-surface —
    Group 1700 cross-arc coordination flag preserved (see §9 + §20.6
    Enforcement-locus Option (c) rationale).
  - S2201 §14 F2 PENDING-CHILD-B-CONFIRMATION — resolved this session:
    surface-local sports-specific hypothesis **REJECTED**; zero-WS-
    subscription pattern **generalizes SYSTEMICally** across all major
    surfaces (see §14 F2 resolution).
  - S2200 §5 Child B per-surface reporting constraint (Q1 STRENGTHEN
    fold) — findings reported per major surface (workspace / betting /
    command-center / PA / other) in addition to axis-level rollup.
  - S2200 §5 Child B timebox + sampling rule (Q10 STRENGTHEN fold) —
    1-session timebox honored via **6 parallel Explore sub-agents** per
    playbook §13 (A1-A6 dispatched in single batch 2026-07-05).
  - S2200 §5 Child B D8 T0/Gate = decision + measurement gate NOT
    implementation gate — honored: this doc measures conformance +
    recommends enforcement locus; does not author schema or wire
    validators.
verifier_loop: |
  Pre-draft verifier-loop (per playbook §14 + parent §5 SESSION READY
  CHECK) executed 2026-07-05 at HEAD `82570a90`:
  1. Consumer registry reconciliation — Agent A1 counted **125 route
     entries** across 5 routing modules vs parent scoping §5 Child B
     estimate of "~33+ consumer classes." Delta hypothesis: parent
     estimate was **route-normalized to unique consumer classes**
     (~50-60 unique classes after de-duping shared consumers like
     `AgentProgressConsumer` used in 6 routes, `NeuralOrchestraConsumer`
     across 3 file implementations); Agent A1 counted **all route
     registrations** including aliases + bridge fallbacks + duplicate
     mappings. Neither count is "wrong" — they measure different things.
     Flagged as §14 observation + §20.5 conflict; recommend xx99 to
     canonicalize (route entries vs unique consumer classes vs unique
     consumer files) + augment PLATFORM_INVENTORY with WS section.
  2. `core/new_pages_consumer.py:310-331` — `send_dbao_metrics` handler
     re-read at HEAD `82570a90`; UNCHANGED from S1505 §14.1 baseline
     (random.randint/uniform payload synthesis). F1 CRITICAL confirmed.
  3. `frontend/src/hooks/useWebSocket.ts:1-100` — hook re-read at HEAD
     `82570a90`; `reconnectAttempts=5`, `reconnectInterval=3000ms`,
     `autoConnect=true`, token via query-param `?token=<token>` (line
     56), dev-mode hardcoded `localhost:8000` (line 55). Raw JSON
     `JSON.parse(event.data)` at line 98 — no envelope validation.
  4. `frontend/src/hooks/useWebSocket.ts:371-416` — `useSystemEvents`
     wrapper re-read; multiplexes 14 event types via switch on
     `event.type` string discriminator. Zero `ui.render_hint` extraction.
  5. `useWebSocket` FE call-site count — Agent A2 confirmed **8 sites
     across 7 files** (CommandCenterPage `/pa/conversations/{id}`,
     AgentsPage ×3 (/agent-updates + /learning-feed + /system-events),
     IntelligencePage `/system-events`, WorkspacePageNew
     `/system-events`, Layout `/system-events`, HeartWidget
     `/dashboard`).
  6. `ui.render_hint` conformance grep — Agent A4 re-verified S2099
     F16 finding: **0/40 emit sites emit envelope-conforming payloads**;
     zero `render_hint|render.hint|ui_render_hint` matches in
     `core/consumers*.py` or `frontend/src/`. Payload shape is bare
     `{type, data, timestamp}` across all inspected consumers.
  7. Repo state at S2202 open: `main @ 82570a90`; working tree clean
     except pre-existing drift on auto-generated `docs/INDEX.md` +
     `docs/_provenance.json` (regen-owed post-cascade) + `.claude/scratch/`
     untracked.
  8. Arc pin `pa-f7fd5016600f4513` verified ACTIVE via
     `platform_config_tool overview` (service_context: local; arc-pin
     acknowledged as active-not-fresh) at S2202 open — TENTH formal arc
     pin under Research OS, preserved through S2201 close per playbook
     §16 arc-standard behavior.
  9. S2201 F2 hypothesis — Child A ambiguous (non-sports pages DO
     subscribe to WS; sports zero-subscribes). Child B empirical
     measurement: 8 FE subscription sites reach **≈5 unique endpoints**
     (`/pa/conversations/{id}`, `/agent-updates`, `/learning-feed`,
     `/system-events`, `/dashboard`) vs 125 BE-registered route
     entries. Coverage ratio ≈ 4% (5/125). **F2 SYSTEMIC** — see §14 F2.
  10. Prior-arc envelope inheritance — S2003 P3 §10.3.4 D4 spec
      re-read; S2099 §14.3.4 F16 verifier grep re-run at HEAD
      `82570a90` — matches historical baseline (zero adoption).
  11. Sports frontend — `frontend/src/pages/BettingPage.tsx` re-grepped
      for `useWebSocket|new WebSocket|wss:|/ws/` — zero matches
      confirmed. S1505 §14.5 UNCHANGED.
  12. CODEOWNERS existence check — no file at repo root or
      `.github/CODEOWNERS` — S2201 §18.1 F4 baseline UNCHANGED (see
      §18.1).
owner: claude (drafted S2202; Rigby SIGN cycle 1 folds will land pre-commit)
---

# Session 2202 — Group 2200 Cat B — WebSocket Consumer Surface + `ui.render_hint` Envelope Audit

> **Static snapshot.** This audit captures the backend WebSocket consumer
> surface + frontend subscription map + `ui.render_hint` envelope
> conformance rate at HEAD `82570a90` on `main` (2026-07-05, LOCAL). It
> is a photograph, not a mechanism explainer. Route + page + layout +
> component patterns is Child A (S2201, shipped). API contract source-of-
> truth is Child C (S2203). Session-scoped state + persistence discipline
> is Child D (S2204). This document delivers what parent §5 Child B
> required: (a) consumer registry (125 route entries counted; ~50-60
> unique classes); (b) frontend subscription map (8 sites across 7
> files); (c) DEAD-CONSUMER inventory (11 candidates flagged); (d)
> MOCK-DATA-CONSUMER inventory (5 confirmed MOCK + 3 HYBRID + 2 EMPTY);
> (e) `ui.render_hint` envelope conformance rate (0/40 = 0% — S2099
> F16 UNCHANGED); (f) POSTURE-DECISION evidence plan §20.6 owed to xx99
> on enforcement-locus recommendation (registration-time vs runtime vs
> defer).

## 1. Executive Summary

**Contract-surface posture — one-sentence answer to the Child B slice of
the central lens question:** The frontend WebSocket consumer surface at
HEAD `82570a90` is an **accreted subscription mesh with mock-data ghosts
and near-zero envelope discipline** — 125 backend route entries feed a
frontend that subscribes to only ~4% of them via a hand-coded
`event.type` string-dispatch pattern that has zero adoption of the
S2003 §10.3.4 D4 `ui.render_hint` envelope contract.

**Central Child B finding — S2201 F2 PENDING-CHILD-B-CONFIRMATION
resolved SYSTEMIC.** Per the S2200 §5 Child B empirical test axis (FE
subscribers per surface ÷ BE consumers per surface), **all four major
surfaces show the zero-WS-subscription pattern generalizing far beyond
sports:**

| Surface | FE subscription sites | BE route entries (Agent A1 count) | Coverage ratio |
|---|---|---|---|
| Workspace | 1 (WorkspacePageNew via `/system-events`) | ~28 workspace-scoped routes | ≈4% |
| Betting | 0 (BettingPage zero-subscribes) | 4 sports/betting routes (3 sports + 1 arbitrage) | 0% |
| Command-Center | 3 (CommandCenterPage `/pa/conversations`, Layout `/system-events`, IntelligencePage `/system-events`) | ~26 command-center-scoped routes | ≈12% |
| PA / Agents | 3 (AgentsPage ×3) | ~15 PA/agents-scoped routes | ≈20% |
| Other / global | 1 (HeartWidget `/dashboard`) | ~52 remainder | ≈2% |
| **Whole frontend** | **8 sites / ~5 unique endpoints** | **125 route entries** | **≈4%** |

**F2 verdict: SYSTEMIC (with surface variance).** Not surface-local.
Sports zero-subscription (S1505 §14.5) is the *loudest* case, not the
outlier; every surface shows a massive gap between backend consumers
registered and frontend subscribers. **Variance nuance (Rigby SIGN
cycle 1 Q8 STRENGTHEN 2026-07-05 fold):** SYSTEMIC deficiency (all
surfaces <25%) with uneven remediation progress — PA highest at ≈20%,
Betting worst at 0%; ≈5× spread across surfaces indicates SYSTEMIC
under-subscription is the load-bearing pattern while PA-first
subscription investment is real. **Denominator contract (Q9 CLEAN +
micro-fold 2026-07-05):** B1 subscription-completeness measurement
uses **route entries** as the denominator (FE-URL-construction endpoint
set — 125 registered); B2 envelope-conformance measurement uses
**unique consumer classes** as the denominator (enforcement-target set
— ~50-60 unique after de-dup). The two axes canonically use different
denominators; readers should not conflate 125 (routes) with ~40 (emit
sites) with ~50-60 (classes).

**Per-event-type coverage nuance (Rigby SIGN cycle 1 Q6 STRENGTHEN
2026-07-05 fold):** `/system-events` counts as 1 route in the coverage
table but multiplexes **14 event types** via `useSystemEvents:371-416`
switch dispatch. Coverage-per-event-type is a secondary metric —
Layout listens for `onPilotStarted` / `onPilotCompleted` /
`onGateBecameCritical` / `onAgentExecutionComplete`; AgentsPage listens
for `onDreamGenerated` / `onLevelUp` / `onAgentExecutionComplete` /
`onAgentExecutionFailed`; overlap is real. Coverage-per-type varies
independently from coverage-per-route. **Verdict unchanged; confidence
increased.**

**Layout surface-attribution nuance (Rigby SIGN cycle 1 Q7 STRENGTHEN
2026-07-05 fold):** `Layout.tsx:45` `/system-events` subscription wraps
**all `ProtectedRoute` children**. Under the rule "global wrappers
contribute to every surface they gate," the coverage-per-surface table
should attribute Layout's subscription as surface-global exposure
across workspace + betting + command-center + PA in addition to
"Other / global." This bumps every surface's minimum FE-subscription
count by 1 for the multiplexed `onPilotStarted` /
`onGateBecameCritical` / `onAgentExecutionComplete` handler paths.
Verdict unchanged (F2 SYSTEMIC still holds even with attribution
credit); confidence increased.

**Central Child B finding — S2099 §14.3.4 F16 `ui.render_hint`
envelope UNCHANGED at HEAD `82570a90`.** 0/40 measured emit sites
conform to the D4 envelope contract. Zero `render_hint|ui.render_hint|
ui_render_hint` matches across `core/consumers*.py` or `frontend/src/`.
Backend emits bare `{type, data, timestamp}` payloads; frontend consumes
via hand-coded `event.type` string dispatch through the `useSystemEvents`
wrapper. Neither side instantiates D4 discipline.

**Central Child B finding — MOCK-DATA-CONSUMER pattern class extended
beyond S1505 §14.1 single-endpoint baseline.** 5 confirmed MOCK
consumers at HEAD `82570a90`:

- `/ws/dbao/` → `NewPagesConsumer.send_dbao_metrics` (UNCHANGED from S1505 §14.1)
- `/ws/profile/` → `NewPagesConsumer.send_profile_data` (same file, same pattern class)
- `/ws/sports/` (live-scores handler) → `SportsConsumer` random.randint scores
- `/ws/decision-command/` → `DecisionCommandConsumer` random agent assignment
- `/ws/sports-betting/` → `SportsBettingConsumer` random.uniform confidence values

Plus 3 HYBRID consumers (real ORM + decorative random), 2 EMPTY
consumers (`GenericWebSocketConsumer`, `TestEchoConsumer`), and 11
DEAD-CANDIDATE / INTENT-NEUTRAL routes (registered with zero
grep-visible FE subscriber; see intent-neutrality Interpretation rule
below). **Pattern-class recurrence framing (Rigby SIGN cycle 1 Q4
STRENGTHEN 2026-07-05 fold):** the MOCK-DATA-CONSUMER pattern class
**recurs across ≥5 WebSocket product surfaces spanning 3 consumer
modules** (`core/new_pages_consumer.py`, `core/sports_consumer.py`,
`core/decision_command_consumer.py`, `sports_betting/consumers.py`) —
indicating the pattern is **not sports-only**. We do not claim all WS
consumers are mock-backed; the claim is specifically that mock-data
emission has multi-surface recurrence, not surface-local containment.

**Central Child B finding — subscription-boundary + envelope-conformance
both indicate accreted mesh + governance-declared-but-unenforced.** The
D4 envelope contract exists at spec but has zero runtime implementation;
the FE subscription surface is inconsistent in shape and coverage across
surfaces. Neither is failing catastrophically — the platform's WebSocket
substrate delivers messages reliably — but the contract-surface posture
answer is **PARTIAL + LIGHT** at design-vs-runtime coherence.

**POSTURE-DECISION recommendation (Child B slice, HIGH confidence
pending Rigby SIGN cycle 1):**

> **§20.6 recommendation:** Adopt **Option (c) DEFER envelope
> enforcement** to post-Group 1700 Observability arc close. Stage a T2
> R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT T-slot in Group 1700 T-slot
> queue with explicit scope: (a) retrofit ~40 BE emit sites to wrap
> `send_json` / `group_send` in envelope helper; (b) retrofit ≥5 FE
> subscription hooks to validate envelope on receive; (c) add CI lint
> for post-envelope emit sites. Rationale: D4 envelope adoption is
> load-bearing on Group 1700 authority-provenance + observability
> maturity gates (S2104 §17.3 / §20.1 cross-arc coordination). Enforcing
> in isolation risks double-retrofit post-Group 1700 closure. Joint
> decision unifies retention policy + enforcement locus. Options (a)
> registration-time + (b) runtime documented as alternatives if
> Group 1700 close date slips past S2299 xx99. Chris D-gate at S2299
> close.

**Cross-arc evidence flags (owed to xx99):**
- **Group 1700 Observability** — S2104 §17.3 / §20.1 retrieval-surface
  counter operator-surface handoff PRESERVED; envelope enforcement locus
  decision joins Group 1700's authority-provenance decision (see §9 + §20.6).
- **Group 2400 Auth** — TokenAuthMiddlewareStack uniformly applied
  across all 125 routes (Agent A1); subscription-time auth wrap is
  consistent. **NO drift found at Child B slice.** Cross-arc handoff:
  Group 2400 owns per-message auth (post-connection revocation, token
  refresh mid-session) which is out of Child B scope.
- **Group 2500 API** — Message routing convention (`event.type` string
  dispatch) parallels REST-API pattern gaps documented at S1505 §15.5;
  cross-arc handoff: Group 2500 API owns whether a single message
  contract source-of-truth should span REST + WS (envelope schema
  candidate).
- **Group 2600 PA** — PA-adjacent consumers: PA chat surface uses
  Celery async polling (`GET /api/pa/chat/status/<task_id>/`) at
  CommandCenterPage in addition to `/pa/conversations/{id}` WS
  subscription. **Parallel real-time delivery mechanism for same
  domain.** Cross-arc handoff: Group 2600 owns WS-vs-polling
  consolidation decision (see §17 T3 + §20.6 rationale).

### Interpretation rule — DEAD / MOCK candidate framing (Rigby SIGN cycle 1 Q3 CLEAN + Q15 STRENGTHEN 2026-07-05 fold)

> **All F# findings classified as DEAD-CANDIDATE / MOCK-DATA / INTENT-
> UNKNOWN are candidates until maintainer intent + usage proof; do NOT
> treat as removal-ready by default.** Removal requires: (a) no
> imports, (b) no routing references, (c) no runtime logs, (d)
> maintainer confirmation. This rule generalizes S2201 F1 CLEAN +
> micro-fold + F3/F4 STRENGTHEN + single-operator-caveat pattern to
> Child B and applies across F1 (MOCK-DATA), F6 (DEAD-CANDIDATE), and
> §14 §15 §16 §17 §18 §19 sections wherever candidate/preliminary
> language appears. Post-arc T-slot execution honors this rule via
> the maintainer-decision gate table (see §19 meta-recommendation).

## 2. Domain Purpose

**What is the WebSocket consumer surface + `ui.render_hint` envelope for?**

The WebSocket consumer surface is the **real-time state fanout substrate**
between backend services (Celery tasks, view handlers, orchestration
runners) and frontend components (React pages, hooks, layout wrappers).
It exists to deliver events that would be too latency-sensitive to
express through the REST API polling loop: agent execution progress,
tool-call ticker updates, pilot state transitions, dream generation,
level-up notifications, gate criticality changes, body-status changes,
file-modification signals, and PA conversation deltas.

The `ui.render_hint` envelope is a **cross-substrate composition
contract** defined by S2003 §10.3.4 D4 for the intentional-dual-emission
pattern where a state change is both authoritative-on-EventBus AND
display-fanout-on-WebSocket. The envelope schema:

```json
{
  "type": "ui.render_hint",
  "event_id": "<canonical event UUID>",
  "source_canonical": "eventbus",
  "display": { "/* non-authoritative UI-only fields */" }
}
```

The mandatory `type: "ui.render_hint"` discriminator + `event_id`
foreign-key + `source_canonical` provenance-tag + `display` fields exist
to prevent the anti-pattern: "browser receives a WebSocket message,
mutates persistent state based on it, without EventBus canonical peer."
D4 is **the** governance seam between the display-only WebSocket
substrate and the authoritative EventBus substrate.

**Central lens question, Child B slice:** *Do the frontend WebSocket
consumers form a governed envelope surface, or an accreted subscription
mesh with mock-data ghosts?*

**Child B slice answer (see §14 rollup):** ACCRETED SUBSCRIPTION MESH
with mock-data ghosts (5 MOCK + 3 HYBRID consumers) and governance
declared but unenforced (D4 envelope 0/40 conformance). Subscription
coverage ≈4% (8 FE sites reach ~5 unique endpoints out of 125
registered BE routes). Contract-surface posture: **PARTIAL** at
subscription completeness; **UNMET** at envelope discipline.

## 3. Canonical Entry Points

**Backend WebSocket routing entry points:**

- `core/asgi.py:14-33` — ASGI ProtocolTypeRouter dispatches HTTP to
  Django + WebSocket to URLRouter; WebSocket URLRouter wrapped with
  `TokenAuthMiddlewareStack` from `core/ws_auth_middleware.py`.
- `core/routing.py:1-500` — main WebSocket URL patterns (111 route
  entries); extends satellite routing modules via `.extend()` calls at
  lines 189 + 192.
- `sports/routing.py:1-11` — sports WS routing (3 entries; only 3
  `AsyncJsonWebsocketConsumer` subclasses in the platform).
- `intelligence/routing.py:1-12` — intelligence WS routing (3 entries).
- `ai_core/routing.py:1-14` — ai_core WS routing (3 entries; note:
  routes prefixed with `ws/` not `^ws/` — regex-anchor drift observed).
- `ai_core/intelligence/routing.py:1-14` — ai_core.intelligence WS
  routing (5 entries).

**Backend consumer class definitions (representative):**

- `core/consumers_base.py:1-3200` — foundational consumer classes;
  reused across 20+ routing entries (AgentProgressConsumer,
  DashboardConsumer, OrchestrationConsumer, etc.).
- `core/new_pages_consumer.py:18-500` — `NewPagesConsumer` handling
  `/ws/ai-nexus/` + `/ws/dbao/` + `/ws/dbao-dashboard/` + `/ws/profile/`;
  contains F1 MOCK-DATA at lines 310-331 (`send_dbao_metrics`) + 333-355
  (`send_profile_data`).
- `core/unified_hub.py:24-500` — `UnifiedWebSocketHub` used for 12
  routes as a bridge fallback pattern.
- `core/orchestra_consumers.py:33-800` — `NeuralOrchestraConsumer` (v2
  live-implementation, 3 duplicate registrations).
- `sports/consumers.py:14-900` — 3 `AsyncJsonWebsocketConsumer`
  subclasses (SportsConsumer, OddsConsumer, GamesConsumer).
- `intelligence/consumers.py:30-1200` — `IncomeBuilderConsumer` +
  `RevenueIncomeConsumer`.

**Frontend WebSocket entry points:**

- `frontend/src/hooks/useWebSocket.ts:1-188` — canonical `useWebSocket`
  hook; single `new WebSocket()` call at line 81; reconnect policy
  `reconnectAttempts=5`, `reconnectInterval=3000ms`; token via query-
  param `?token=<token>`; dev-mode host `localhost:8000` (line 55).
- `frontend/src/hooks/useWebSocket.ts:371-416` — `useSystemEvents`
  wrapper multiplexes 14 event types via switch on `event.type`.
- `frontend/src/pages/CommandCenterPage.tsx:683` — subscribes
  `/pa/conversations/{activeConversationId}` (dynamic route).
- `frontend/src/pages/AgentsPage.tsx:696` + `:918` + `:928` — 3
  subscription sites (`/system-events`, `/agent-updates`,
  `/learning-feed`).
- `frontend/src/pages/IntelligencePage.tsx:313` — `/system-events`.
- `frontend/src/pages/WorkspacePageNew.tsx:866` — `/system-events`.
- `frontend/src/components/layout/Layout.tsx:45` — global
  `/system-events` subscription.
- `frontend/src/components/HeartWidget.tsx:239` — `/dashboard`
  fallback poll.

## 4. Major Models

**Backend consumer base classes:**

| Base | Instance count (route registrations) | File:line |
|---|---|---|
| `AsyncWebsocketConsumer` (Channels stdlib) | 122 route registrations | Standard Django Channels base |
| `AsyncJsonWebsocketConsumer` (Channels stdlib) | 3 route registrations (sports only) | `sports/consumers.py` |
| `SafeWebSocketMixin` (u-d-b) | inherited by ~40 consumers | `core/consumers_base.py` (early lines) |
| `ProductionWebSocketMixin` (u-d-b) | inherited by `ProductionRevenueConsumer` + variants | `core/production_websocket.py:1-307` |

**No shared envelope model class exists.** The `ui.render_hint`
envelope has no Python dataclass, Pydantic model, or TypedDict
representation anywhere in the codebase. Payloads are constructed
inline as raw dicts at each `send_json` / `group_send` / `send()`
call site.

**Frontend message shape (observed, not declared):**

`frontend/src/hooks/useWebSocket.ts:270-340` declares typed interfaces
for `SystemEvent`, `AgentExecutionEvent`, `PilotEvent`, `DreamEvent`,
`HiveMindEvent` — but these are FE-side type assertions, not
BE-shared contracts. There is no shared source-of-truth between BE
consumer emit payloads and FE handler types; drift is entirely
absorbed by TypeScript's structural typing tolerance.

## 5. Major Services

**Backend WebSocket-adjacent services (representative):**

| Service | Role | File |
|---|---|---|
| `TokenAuthMiddlewareStack` | Query-param + session auth for WS handshake | `core/ws_auth_middleware.py` |
| `ChannelLayer` (Redis) | Group broadcast fanout | Django Channels stdlib + `settings.py` CHANNEL_LAYERS |
| `AgentProgressConsumer.broadcast_progress()` | Fanout agent execution progress | `core/consumers_base.py:74-171` |
| `RigbyToolTicker` producer path | Emits `rigby.tool.started` + `rigby.tool.completed` | `core/consumers_pa_conversation.py:175-345` |
| `SafeWebSocketMixin` | Connection lifecycle + error containment | `core/consumers_base.py` (early lines) |
| `UnifiedWebSocketHub` | Bridge / fallback consumer for 12 routes | `core/unified_hub.py:24-500` |

**Frontend hooks + subscription surface:**

| Hook / component | Role | File:line |
|---|---|---|
| `useWebSocket` | Canonical WS subscription primitive (reconnect + auth + callback) | `frontend/src/hooks/useWebSocket.ts:24-188` |
| `useSystemEvents` | Typed multiplexer over `/system-events` | `frontend/src/hooks/useWebSocket.ts:371-416` |
| `useAuthStore` | Provides token for WS query-param | `frontend/src/stores/authStore.ts` |
| `unifiedStore` | Global state refresh on WS system events | `frontend/src/stores/unifiedStore.ts` |
| `queryClient` (React Query) | Cache invalidation on WS messages | `@tanstack/react-query` |

**No envelope-validation service exists on either side.** There is no
`envelope_helper.send_render_hint()` on the backend or
`validateRenderHint()` on the frontend. Every emit + receive is
raw-dict.

## 6. Major APIs and Interfaces

**WebSocket route registry — summary counts (Agent A1 enumeration):**

| Routing module | Route entries |
|---|---|
| `core/routing.py` | 111 |
| `sports/routing.py` | 3 (all `AsyncJsonWebsocketConsumer`) |
| `intelligence/routing.py` | 3 |
| `ai_core/routing.py` | 3 (regex-anchor drift: `ws/` not `^ws/`) |
| `ai_core/intelligence/routing.py` | 5 |
| **Total** | **125** |

**Duplicate + bridge patterns observed:**

- `AgentProgressConsumer` — 6 routing entries (`/ws/activity/`, `/ws/agents/`, `/ws/agent-progress/`, `/ws/agent-progress/<instance_id>/`, `/ws/agent-updates/`, and an additional alias).
- `NeuralOrchestraConsumer` — 3 separate class implementations across `core/orchestra_consumers.py:33`, `core/consumers_base.py:2711`, `ai_core/intelligence/consumers.py:505` (naming collision — different implementations).
- `UnifiedWebSocketHub` — 12 routing entries as fallback / bridge (`/ws/decision-command/`, `/ws/control-center/`, `/ws/bridge/*`, etc.).
- `PlatformUnificationConsumer` — 11 routing entries under `core/platform_unification_orchestrator.py:1103` (candidate DEAD, see §14 F5).

**Unique consumer classes (approx, after de-dup):** ~50-60 unique
class implementations across the 125 route registrations. Parent
scoping §5 Child B estimate of "~33+" is closer to a lower-bound
consumer-file count than an accurate class or route count. Reconcile
at xx99 (§20.5).

**Frontend subscription endpoints (Agent A2 enumeration):**

| Endpoint (route path after `/ws` prefix) | Subscriber components | Surface |
|---|---|---|
| `/pa/conversations/{id}` | CommandCenterPage:683 | Command-Center |
| `/agent-updates` | AgentsPage:918 | PA / Agents |
| `/learning-feed` | AgentsPage:928 | PA / Agents |
| `/system-events` | AgentsPage:696, IntelligencePage:313, WorkspacePageNew:866, Layout:45 | 4 pages (global + 3 surface-local) |
| `/dashboard` | HeartWidget:239 | Global fallback |

**5 unique endpoints reach 8 subscription sites. Frontend covers ≈4% of
the 125 BE-registered route entries.**

## 7. Runtime Flows

**Canonical emit path (BE → FE):**

1. Backend service (Celery task, view, orchestration runner) calls
   `channel_layer.group_send(group_name, {"type": "<event_type>", ...})`.
2. Django Channels routes to the consumer class registered for the group.
3. Consumer's `event_type_handler` (matched by Channels' method-lookup
   pattern) receives + calls `self.send_json(...)` or `self.send(...)`.
4. WebSocket frame ships to any client with an open subscription.

**No envelope wrap step exists.** The payload arrives at the FE as
whatever dict was passed to `send_json` — commonly `{type, data,
timestamp}` (see `core/new_pages_consumer.py:326-331` for the
`/ws/dbao/` pattern) or `{type, agent_name, status, message, timestamp,
data}` (see `core/consumers_base.py` `AgentProgressConsumer`).

**Canonical receive path (FE):**

1. `useWebSocket` hook (line 81) opens `new WebSocket(url)`.
2. `onmessage` handler (line 95-104) `JSON.parse(event.data)` — accepts
   any shape.
3. `callbacksRef.current.onMessage?.(data)` — passes to component's
   registered handler.
4. Component checks `event.type === '<literal_string>'` and dispatches.
5. Zero envelope validation. Zero version check. Zero `render_hint`
   extraction. Zero `source_canonical` provenance check.

**RigbyToolTicker flow (representative envelope-adjacent path):**

`CommandCenterPage.tsx:707` checks `event.type === 'rigby.tool.started'`
+ presence of `trace_id`, `tool_call_id`, `tool_name` — this is the
closest thing in the codebase to envelope shape enforcement, but it is
**component-local** and does NOT reference D4's `ui.render_hint`
envelope schema. It's a hand-coded contract between one BE producer
(`core/consumers_pa_conversation.py`) and one FE consumer
(`CommandCenterPage.tsx`).

## 8. Data Ownership and Lifecycle

**Consumer lifecycle:**

- **Connect** — `TokenAuthMiddlewareStack` authenticates via query-
  param `?token=<token>` OR session cookie. Consumer's `async
  connect()` runs; typically joins a Channels group (e.g., `group_name
  = f"agent_progress_{user_id}"`).
- **Receive** — client-to-server messages (rare — most consumers are
  broadcast-only) route through `receive_json` / `receive`.
- **Emit** — server-to-client via `send_json` / `send`; typically
  triggered by `channel_layer.group_send` from an external service.
- **Disconnect** — `async disconnect()` cleans up group memberships.

**Message ownership:** No consumer owns a persistent message record.
Messages are ephemeral — if the client is not connected at emit time,
the message is lost. No dead-letter queue at the WS layer. This is
intentional per the S2003 D4 "display-only" contract — the
authoritative record lives on EventBus (or ORM); WS is a display
fanout.

**MOCK-DATA lifecycle:** MOCK consumers emit synthetic payloads at
either connect-time (e.g., `send_profile_data` at `NewPagesConsumer`)
or periodic-loop (e.g., `send_dbao_metrics` in a
`asyncio.create_task` loop). No persistence. Random values on every
emit.

## 9. Integrations With Other Domains

| Domain / Group | Integration point | Coupling type | Notes |
|---|---|---|---|
| **Group 1700 Observability** | S2104 §17.3 / §20.1 retrieval-surface counter operator-surface | Cross-arc handoff (envelope enforcement decision) | Load-bearing on Group 1700 authority-provenance decision (Path A: WS is display-only mirror → strict envelope; Path B: WS is co-canonical → loose envelope). Blocks §20.6 Option (a) / (b). |
| **Group 2400 Auth** | `TokenAuthMiddlewareStack` uniformly applied 125/125 routes | Symptomatic + descriptive only | **No drift found in connection auth wrapper** (125/125 TokenAuthMiddlewareStack); **per-message auth / mid-session token revocation / token refresh NOT evaluated** (Rigby SIGN cycle 1 Q14 STRENGTHEN 2026-07-05 fold — sampling-scope hedge). Out of Child B scope. |
| **Group 2500 API** | Payload shape `event.type` string dispatch parallels REST-endpoint pattern gaps (S1505 §15.5) | Cross-arc dependency (single-source-of-truth) | Group 2500 owns whether one message contract SoT should span REST + WS (envelope schema candidate). |
| **Group 2600 PA** | PA chat uses BOTH `/pa/conversations/{id}` WS subscription AND Celery polling at `/api/pa/chat/status/<task_id>/` | Parallel-delivery-mechanism duplicate | See §17 T3. Group 2600 owns consolidation decision post-arc. |
| **Group 2100 RAG (closed)** | S2099 F16 `ui.render_hint` envelope absent — Child B re-verifies UNCHANGED at HEAD `82570a90` | Inheritance | Child B does NOT re-open S2099 F16; measurement carries forward. |
| **Group 2000+ Event / Integration (closed)** | S2003 §10.3.4 D4 defines envelope contract; S2003 §10.5 cross-substrate composition register | Inheritance | D4 is the target contract; envelope-authorship out-of-arc. |
| **Group 1500 Sports (closed)** | S1505 §14.1 F5 MOCK-DATA `/ws/dbao/` + §14.5 zero-WS-subscription | Inheritance + generalization | Both patterns generalize beyond sports (see §14 F1 + F2). |
| **Group 1300 Memory** | LearningFeedConsumer feeds AgentsPage `/learning-feed` | Downstream consumer | Learning-event stream is one of the two non-`/system-events` FE subscriptions that carry semantic content. |

## 10. Event Flows

**Observed emit-side payload shapes (representative sample of ~40
emit sites — Agent A4 enumeration):**

| Emit site | Payload shape | Envelope-conformant? |
|---|---|---|
| `core/new_pages_consumer.py:326-331` (`/ws/dbao/`) | `{type: 'dbao_metrics', data: {...}, timestamp}` | NO |
| `core/new_pages_consumer.py:354-360` (`/ws/profile/`) | `{type: 'profile_data', data: {...}, timestamp}` | NO |
| `core/consumers_base.py:74-171` (AgentProgressConsumer) | `{type: 'agent_status'\|'agent_execution'\|..., agent_name, status, message, timestamp, data}` | NO |
| `core/consumers_pa_conversation.py:*` (RigbyToolTicker path) | `{type: 'rigby.tool.started'\|'rigby.tool.completed', trace_id, tool_call_id, tool_name, agent_name, ...}` | NO (component-local contract, not D4) |
| `core/consumers_sports.py:*` (SportsUpdatesConsumer) | `{type: 'odds_updated'\|'league_updated', ...}` | NO |
| `core/websocket_bridge.py:1-*` | `{type: 'broadcast_update', ...}` | NO |
| `core/views_personal_assistant.py:*` | `{type: 'message.created', ...}` | NO |
| ...38 other emit sites... | Bare `{type: <string>, ...}` shape | NO |

**Envelope conformance rate: 0/40 = 0%.**

**Observed receive-side handler shapes (FE, all 8 sites):**

Every FE handler discriminates on `event.type` (or `event.data.type`,
or `event.message?.type`) as a string. Zero handlers check for
`event.type === 'ui.render_hint'`. Zero handlers extract
`event.event_id` or `event.source_canonical`. Zero handlers read
`event.display`.

**FE handler pattern-class inventory:**

| Pattern | Example | Site |
|---|---|---|
| Component-local switch on typed event | `useSystemEvents` switch on 14 types | `useWebSocket.ts:371-416` |
| Component-local guard on discriminator | `if (event.type === 'rigby.tool.started' && event.trace_id ...)` | `CommandCenterPage.tsx:707` |
| Type-filter noise removal | `if (msgType === 'connection_established' \|\| msgType === 'pong') return` | `AgentsPage.tsx:922` |
| Bulk message with typed body | `if (msg.type === 'learning_activity') { render feed_items[] }` | `AgentsPage.tsx:938` |
| Field-specific check | `if (msg.type === 'heartbeat') { health_score }` | `HeartWidget.tsx:242-247` |

**None of these instantiate the D4 `ui.render_hint` envelope.** They
are all hand-coded contracts between one BE producer and one FE
consumer — the mesh pattern.

## 11. Existing Documentation

| Document | Coverage of WS + envelope |
|---|---|
| `docs/topics/frontend.md` | Mentions WS integration at PA chat layer; zero envelope coverage; no consumer registry (stale-warned) |
| `docs/topics/agent-system.md` | Agent execution routing + context injection; zero WS consumer surface documented |
| `docs/topics/personal-assistant.md` | PA agentic loop + Celery polling at `/api/pa/chat/status/<task_id>/`; **zero WS surface documented** despite `/pa/conversations/{id}` WS subscription existing at CommandCenterPage:683 |
| `docs/PLATFORM_INVENTORY.md` (2026-07-02) | Master inventory; **zero WebSocket-count line** in inventory (§14 observation flag) |
| `docs/EVENT_SYSTEM_INVENTORY.md` (Session 1250) | 57 WebSocket consumer classes catalogued as infrastructure; zero envelope inventory |
| `docs/research/domains/event_integration_architecture/2002_*.md` | First formal `ui.render_hint` mention (§10.3.4); design-contract only |
| `docs/research/domains/event_integration_architecture/2003_*.md` | Second formal mention: intentional-dual-emission carries envelope mandatory binding + MUST NOT anti-pattern (§10.3.4 D4) |
| `docs/research/domains/event_integration_architecture/2099_*.md` | §4 F16 `ui.render_hint` envelope absent + unenforced (Group 2000+ arc-close) |
| `docs/research/domains/sports/1505_*.md` | §14.1 F5 MOCK-DATA `/ws/dbao/`; §14.5 zero-WS-subscription for 3 sports routes (baseline) |
| `docs/research/domains/frontend/2200_*.md` | Parent scoping §5 Child B block; §7.1 leak-vector guardrails |
| `docs/research/domains/frontend/2201_*.md` | Child A §14 F2 PENDING-CHILD-B-CONFIRMATION baseline (resolved this session as SYSTEMIC — see §14 F2) |

**§11 Summary:** `ui.render_hint` envelope is design-complete (S2002 +
S2003) but **runtime envelope conformance is completely undocumented
outside the S2099 F16 finding**. WebSocket consumer registry is
catalogued only as infrastructure count (57 consumers per EVENT_
SYSTEM_INVENTORY §2.6) with drift vs Agent A1's 125-route enumeration
this session. PLATFORM_INVENTORY has NO WebSocket-count section —
augmentation owed to xx99 (§20.6 rec).

## 12. Research Coverage

Per playbook §12 classification (LIGHT / MODERATE / DEEP / CANONICAL):

| Research dimension | Classification | Evidence |
|---|---|---|
| **Envelope design contract** (S2002 §7-§17 + S2003 §10.3.4) | **CANONICAL** | S2002 P2 + S2003 P3 design-contract shipped complete; inheritance chain documented |
| **Event-emission gap catalog** (S1806 six-plane taxonomy) | **DEEP** | S1806 + S2001 + S2002 §17 consumer registry |
| **WebSocket consumer registry** (BE) | **LIGHT (until this session)** | 170+ raw routing patterns visible; zero prior audit of route ↔ consumer mapping. This session establishes 125-route enumeration as first audit-level artifact — bumps to **MODERATE** at close. |
| **`useWebSocket` hook implementation** | **LIGHT** | Hook code visible; zero prior audit of which pages call it, envelope handling at reception, error propagation. S2201 enumerated 7 subscriber pages (superseded by A2's more precise 8-site / 7-file measurement this session) |
| **Message envelope conformance** (`ui.render_hint`) | **LIGHT** | S2099 F16 flagged "absent + unenforced"; zero rate audit. This session establishes **0/40 = 0% conformance** as first empirical measurement |
| **Consumer ↔ page mapping** | **LIGHT** | No prior registry linking BE consumer classes to FE subscribing components. This session establishes preliminary cross-join (Agent A3 + A2) |
| **Ownership + governance** | **LIGHT** | S2201 §18.1 F4 CODEOWNERS absent (inherited unchanged this session) |

**§12 Summary:** Envelope design CANONICAL; consumer registry
LIGHT→MODERATE (this session); envelope conformance measurement LIGHT
(this session establishes baseline 0/40); consumer↔page mapping LIGHT
(this session establishes baseline cross-join). **Child B closes at
MODERATE research coverage** — the first empirical audit of BE registry
+ FE subscription + envelope conformance as a single measurement bundle.

## 13. Architecture Maturity

| Component | Maturity | Justification |
|---|---|---|
| **BE consumer surface** | **EXPERIMENTAL** | 125 route entries + ~50-60 consumer classes. Zero envelope conformance. F1 MOCK-DATA generalizes across 5 confirmed sites. 11 candidate DEAD routes. Backend produces + delivers messages reliably, but contract enforcement + reliability governance is unverified. |
| **`useWebSocket` hook (FE)** | **WORKING** | Hook is functional: connection lifecycle, reconnect logic (5 attempts / 3s), token auth, callback injection. 8 subscription sites reliably deliver messages. **Limitation:** zero envelope-validation logic; payloads accepted as-is. |
| **`ui.render_hint` envelope** | **PARTIAL** | Design-contract complete (S2002 + S2003). **Zero runtime enforcement:** no producer-side envelope serializer; no consumer-side envelope deserializer or validation gate; no version negotiation; 0/40 conformance measured this session. |
| **Sports WS routes ↔ FE binding** | **DEAD** | 3 routes registered (sports/routing.py:8-11); BettingPage.tsx zero-subscribes; uses 30s polling instead (S1505 §14.5 UNCHANGED). No dormant intention signal. |
| **PA polling ↔ WS parallel** | **PARTIAL** | PA chat uses BOTH `/pa/conversations/{id}` WS AND Celery polling at `/api/pa/chat/status/<task_id>/`. Real-time delivery works via both mechanisms; no clarity on canonical assignment. |

**Composite maturity at contract surface: PARTIAL** — message delivery
works reliably; contract governance is design-canonical but
runtime-unenforced; MOCK-DATA + DEAD-CONSUMER patterns generalize
across surfaces.

## 14. Known Drift

**F1 — MOCK-DATA-CONSUMER pattern class recurs across 5 sites (multi-
surface recurrence; baseline S1505 §14.1 UNCHANGED at `/ws/dbao/` +
new sites identified)**

- **Type:** mock-data-endpoint
- **Severity:** **HIGH (baseline); CRITICAL on user-visible surfaces —
  DBAO dashboards, Betting (Sports Hub / Sports Betting), Decision-
  Command if it drives live ops** (Rigby SIGN cycle 1 Q1 STRENGTHEN
  2026-07-05 fold — mirrors S2201 F1/F3 precedent). Severity rule:
  MOCK-DATA severity scales with user-visibility, money-path, and
  reliability-critical exposure — not by presence of `random.*` calls
  alone.
- **Evidence:**
  - `core/new_pages_consumer.py:310-331` — `send_dbao_metrics`
    (`random.randint` + `random.uniform` payload synthesis) UNCHANGED
    from S1505 §14.1 baseline
  - `core/new_pages_consumer.py:333-355` — `send_profile_data` (same
    file, same pattern class): applications, revenue, success_rate,
    active_projects via `random.randint` / `random.uniform`
  - `core/sports_consumer.py:157-187` — SportsConsumer live-scores
    `random.randint(14, 35)` for home/away scores, `random.choice(['Q1',
    'Q2', 'Q3', 'Q4'])`
  - `core/decision_command_consumer.py:135-306` — DecisionCommandConsumer
    `decision_score = job.get('match_score', 50) + random.randint(10,
    30)` + agent assignment `f'Agent-{random.randint(1, 150)}'`
  - `sports_betting/consumers.py:123-213` — SportsBettingConsumer
    `bet_id`, `confidence`, `recommended_bet` all synthesized via
    `random.randint` / `random.uniform` / `random.choice`
- **Surface:** DBAO Dashboard, Profile page, Betting (Sports Hub +
  Sports Betting), Command-Center (Decision Command)
- **Verdict:** MOCK-DATA-CONSUMER is not surface-local to sports — it
  **recurs across ≥5 WebSocket product surfaces spanning 3 consumer
  modules** (Rigby SIGN cycle 1 Q4 STRENGTHEN 2026-07-05 fold —
  scoped-recurrence framing, not "system-wide"). Pattern class is not
  sports-only. Removal + remediation gated by intent-neutrality
  Interpretation rule (see §2 preamble) — post-arc maintainer-
  decision batch.

**F2 — Zero-WS-subscription pattern generalizes SYSTEMICally
(resolves S2201 F2 PENDING-CHILD-B-CONFIRMATION)**

- **Type:** subscription-completeness-gap
- **Severity:** HIGH (per-surface variance; not CRITICAL because
  message delivery via subscribed surfaces is reliable)
- **Evidence:**
  - `frontend/src/pages/BettingPage.tsx` — zero `useWebSocket` / `new
    WebSocket` / `wss:` / `/ws/` grep matches (S1505 §14.5 UNCHANGED)
  - Agent A1 enumeration: 125 BE-registered route entries
  - Agent A2 enumeration: 8 FE subscription sites reaching ≈5 unique
    endpoints
  - Coverage ratio ≈ 4% (5/125)
  - Per-surface breakdown:
    - Workspace: 1 FE site / ~28 BE routes ≈ 4%
    - Betting: 0 FE sites / 4 BE routes = 0%
    - Command-Center: 3 FE sites / ~26 BE routes ≈ 12%
    - PA / Agents: 3 FE sites / ~15 BE routes ≈ 20%
    - Other / global: 1 FE site / ~52 BE routes ≈ 2%
- **Surface:** All major surfaces
- **Verdict:** S2201 F2 hypothesis (surface-local sports-specific)
  **REJECTED**; pattern generalizes **SYSTEMICally with surface
  variance** (Rigby SIGN cycle 1 Q8 STRENGTHEN 2026-07-05 fold —
  SYSTEMIC deficiency across all surfaces <25%; ≈5× spread PA at 20%
  vs Workspace at 4% vs Betting at 0% is real variance, not noise).
  Sports zero-subscription is the loudest case, not the outlier.
- **Sampling completeness note (Rigby SIGN cycle 1 Q10 STRENGTHEN
  2026-07-05 fold):** grep sample covered `useWebSocket|new WebSocket|
  wss:|ws:` across `frontend/src` + `useSystemEvents` wrapper
  entrypoints + `useWebSocket.ts:81` single-`new WebSocket()`-source
  trace. Blind spots minimized: no alternate FE subscribers discovered
  outside the canonical hook + wrapper path. If a future audit finds
  FE subscribers via non-`useWebSocket` paths (e.g., a wrapper that
  hides the underlying subscription), coverage numerator increases —
  verdict may reclassify from SYSTEMIC to MIXED. Cycle-2 trigger
  candidate.

**F3 — `ui.render_hint` envelope 0/40 conformance rate (S2099 F16
UNCHANGED)**

- **Type:** envelope-conformance-absent
- **Severity:** HIGH
- **Evidence:**
  - S2003 §10.3.4 D4 spec defines envelope: `type: "ui.render_hint"`,
    `event_id`, `source_canonical`, `display`
  - Agent A4 grep: zero matches for `render_hint|ui.render_hint|
    ui_render_hint` in `core/consumers*.py` or `frontend/src/`
  - 40/40 sampled emit sites emit bare `{type: <string>, ...}` shape
  - Sampling scope: complete enumeration across `core/consumers*.py` +
    `core/views*.py` + `core/*_bridge.py` + `core/command_center*.py`
    with `channel_layer.group_send` call sites (~40 sites)
- **Surface:** All 40 sampled emit sites across 7 surfaces
  (Betting Dashboard, Agent Orchestration, Command Center, Intelligence
  Desks, PA, Content Studio, Workspace)
- **Verdict:** S2099 §14.3.4 F16 baseline confirmed UNCHANGED at HEAD
  `82570a90`. **Primary metric: 0/40 consumer emit-site classes = 0%
  conformance.** **Secondary metric (Rigby SIGN cycle 1 Q2 STRENGTHEN
  2026-07-05 fold):** each consumer typically carries 3-5 `send_json` /
  `group_send` callsites; estimated true send_json-callsite denominator
  is **~100+**, yielding the same 0/N=0% verdict at higher confidence
  (all measured emit paths bare-`{type, data, timestamp}`; zero
  `render_hint|ui.render_hint|ui_render_hint` matches at either
  denominator).

**F4 — Producer-side envelope serializer absent (F3 mechanism)**

- **Type:** missing-serializer
- **Severity:** HIGH
- **Evidence:** No `envelope_helper.py` / `render_hint_serializer.py`
  in `core/services/` or `core/serializers*.py`. Every `send_json` /
  `group_send` constructs payload inline. No wrapper enforces D4.
- **Surface:** All BE producers
- **Verdict:** Serializer-absence is the mechanical explanation for F3.

**F5 — Consumer-side envelope deserializer + validation absent (F3
mechanism)**

- **Type:** missing-validator
- **Severity:** HIGH
- **Evidence:** `frontend/src/hooks/useWebSocket.ts:98-104` —
  `JSON.parse(event.data)` accepts any structure; zero schema
  validation; zero version checking; zero `render_hint` extraction.
  `useSystemEvents:371-416` switch dispatches on `event.type` string
  only.
- **Surface:** All 8 FE subscription sites
- **Verdict:** Validator-absence is the FE-side mechanical explanation
  for F3.

**F6 — DEAD-CANDIDATE / INTENT-NEUTRAL inventory (11 sites)**

- **Type:** dead-candidate / intent-neutral
- **Severity:** **MEDIUM** with delete-proof gate (Rigby SIGN cycle 1
  Q3 CLEAN + micro-fold 2026-07-05): MEDIUM applies only if delete-
  proof triad holds — (a) no imports, (b) no routing references
  outside the flagged entry, (c) no runtime logs of hits. Absent
  delete-proof, downgrade to **LOW-until-confirmed**. Post-arc
  maintainer-decision gate (see §19 meta-recommendation) determines
  removal-vs-keep verdict.
- **Evidence (Agent A3 grep-negative flags — preliminary, pending
  maintainer confirmation):**
  - `/ws/knowledge-discovery/` — PlatformUnificationConsumer
  - `/ws/expert-consultation-updates/` — PlatformUnificationConsumer
  - `/ws/semantic-search/` — PlatformUnificationConsumer
  - `/ws/content-monetization-tracker/` — PlatformUnificationConsumer
  - `/ws/revenue-pipeline-monitor/` — PlatformUnificationConsumer
  - `/ws/spider-content-feed/` — PlatformUnificationConsumer
  - `/ws/advisor-content-streams/` — PlatformUnificationConsumer
  - `/ws/truth-dashboard/` — RealityCheckConsumer
  - `/ws/system-monitor/` — RealityCheckConsumer
  - `/ws/reality-check/` — RealityCheckConsumer
  - `/ws/diagnostic/` — UnifiedWebSocketHub
  - `/ws/opportunities/` — UnifiedWebSocketHub
  - `/ws/bridge/*` — Various (UnifiedWebSocketHub / ProductionRevenueConsumer)
- **Surface:** Distributed
- **Verdict:** 11-13 candidate DEAD routes flagged for maintainer
  confirmation. Cleanup is post-arc T-slot (§15 T3).

**F7 — Regex-anchor drift in `ai_core/routing.py`**

- **Type:** convention-drift
- **Severity:** LOW
- **Evidence:** `ai_core/routing.py:12-14` — routes prefixed `ws/`
  (no `^` anchor); rest of platform uses `^ws/`
- **Surface:** `ai_core/routing.py` only
- **Verdict:** Cosmetic drift; may cause partial-match false positives
  under specific URLRouter conditions. Post-arc cleanup.

**F8 — Observation: PLATFORM_INVENTORY has no WebSocket-count section**

- **Type:** inventory-augmentation-owed
- **Severity:** N/A (observation, not drift per §14 semantics)
- **Evidence:** `docs/PLATFORM_INVENTORY.md` §Frontend + §Runtime rows
  do not enumerate WebSocket route/consumer counts
- **Surface:** Inventory doc
- **Verdict:** Augment inventory at xx99 close — add WS section with
  route entries (125) + unique consumer classes (~50-60) + FE
  subscription sites (8) + envelope conformance rate (0/40).

## 15. Known Technical Debt

**T1 — Envelope serializer + validator framework not implemented (F3/F4/F5 mechanism)**

- **Type:** infrastructure-gap
- **Severity:** HIGH
- **Owner:** Post-arc (candidate Group 1700 Observability per §20.6
  Option (c) rationale; alternative Group 2500 API)
- **Notes:** Required before enforcement possible. Frames scope for
  post-arc T-slot.

**T2 — R.EVENTS.UI-RENDER-HINT-ENVELOPE-RETROFIT T-slot (§20.6
Option (c) commit)**

- **Type:** post-arc-retrofit
- **Severity:** HIGH
- **Owner:** Group 1700 Observability (staged; blocked pending Group
  1700 authority-provenance decision per S2104 §17.3)
- **Notes:** Scope: (a) retrofit ~40 BE emit sites; (b) retrofit ≥5 FE
  subscription hooks; (c) add CI lint. See §20.6.

**T3 — Sports WS routes ownership + deletion candidate**

- **Type:** cleanup-debt
- **Severity:** MEDIUM
- **Owner:** Post-arc
- **Notes:** S1505 §14.5 established zero-subscriber; S2201 inherited;
  Child B re-confirmed UNCHANGED. Decision pending: remove or
  implement real sports WS emission. Currently orphaned.

**T4 — `/ws/dbao/` + `/ws/profile/` MOCK-DATA handler intent
clarification**

- **Type:** intentionality-clarity
- **Severity:** MEDIUM
- **Owner:** Post-arc
- **Notes:** Handlers use random.randint/uniform. Intent unclear:
  intentional demo/dev-only OR obsolete. `new_pages_consumer.py.backup`
  file exists without explanation. Post-arc decision: remove or
  document as intentional staging layer.

**T5 — Route ↔ Consumer registry durable source-of-truth**

- **Type:** governance-debt
- **Severity:** MEDIUM
- **Owner:** xx99 canonical summary + post-arc T-slot
- **Notes:** 125 route entries + ~50-60 consumer classes live
  distributed across 5 routing modules + 50+ consumer files. This
  audit is the first artifact enumerating them; durable registry
  file (e.g., `docs/topics/websocket-registry.md` or
  PLATFORM_INVENTORY §WebSocket section) owed post-arc.

**T6 — PA polling ↔ WebSocket unification decision**

- **Type:** architecture-seam
- **Severity:** MEDIUM
- **Owner:** **Joint Group 2500 API + Group 2600 PA** (Rigby SIGN
  cycle 1 Q13 STRENGTHEN 2026-07-05 fold — transport choice touches
  API design + PA UX/ops semantics; lead = whichever group owns the
  status endpoint contract). Post-arc cross-arc handoff.
- **Notes:** PA chat uses both async Celery polling
  (`/api/pa/chat/status/<task_id>/`) AND WS (`/pa/conversations/{id}`).
  Decision pending: migrate PA fully to WS (enables real-time +
  envelope conformance) OR document polling-only + WS-supplement
  posture.

**T7 — Version negotiation for `ui.render_hint` envelope
`schema_version` field**

- **Type:** schema-evolution
- **Severity:** LOW
- **Owner:** Post-arc (tied to T1 + T2)
- **Notes:** S2002 D1 adopted schema_version semver policy; runtime
  enum-change + backward-compat + consumer fail-open semantics owed by
  post-arc implementation.

**T8 — Regex-anchor cleanup for `ai_core/routing.py` (F7)**

- **Type:** convention-drift-cleanup
- **Severity:** LOW
- **Owner:** Post-arc
- **Notes:** Cosmetic; normalize `ws/` to `^ws/`.

**T9 — Candidate DEAD-CONSUMER cleanup (F6)**

- **Type:** cleanup-debt
- **Severity:** MEDIUM
- **Owner:** Post-arc (maintainer confirmation gate)
- **Notes:** 11-13 candidate routes flagged. Verify intent before
  removal (Rigby SIGN cycle 1 candidate — intent-neutrality framing).

## 16. Boundary Violations

| Violation | Location | Severity | Notes |
|---|---|---|---|
| **FE consumer accepts raw payloads without type-narrowing to BE schema** | `frontend/src/hooks/useWebSocket.ts:98-104` — `JSON.parse(event.data)` accepts any structure | MEDIUM | Symptomatic of F5; latent risk if BE producer changes shape without FE awareness |
| **Consumer emitting model data without serializer** | S2003 §10.3.4 prohibits raw model instances + unmigrated schema fields. `NewPagesConsumer` emits MOCK-DATA (accidentally compliant — random data). Unknown if any real producer violates. Zero serializer framework exists. | MEDIUM | Latent risk; F4 mechanism |
| **EventBus ↔ WebSocket dual-emission overlap unaudited** | S2003 §10.5 6-substrate composition register; Child B does NOT enumerate which producers emit to both — that is S2099 §4 T-slot post-arc | MEDIUM | Deferred per §7 anti-scope |
| **Version mismatch risk (schema_version field absent)** | S2002 §7 declares semver `schema_version` per-event; `useWebSocket.ts` zero version extraction | MEDIUM | Symptomatic of F5 |

**§16 Summary:** 4 boundary violations. All symptomatic of F3/F4/F5
mechanism. No critical violations; all mitigated by post-arc envelope
framework (T1 + T2).

## 17. Duplicate or Overlapping Systems

| Overlap | Pattern | Severity | Status |
|---|---|---|---|
| **PA chat: WebSocket + Celery polling parallel** | CommandCenterPage uses BOTH `/pa/conversations/{id}` WS AND `GET /api/pa/chat/status/<task_id>/` polling. Same domain, parallel real-time mechanisms. | MEDIUM | T6 deferred (Group 2600 PA) |
| **EventBus ↔ WebSocket ↔ CeleryTaskEvent semantic overlap** | S2003 §10.5 + S2099 §4 identify overlap; zero per-site audit at Child B (post-arc scope). | MEDIUM | S2099 T-slot (R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER) |
| **Sports routes: WS registered + polling used** | sports/routing.py registers 3 routes; BettingPage.tsx uses 30s polling instead. Parallel + neither canonical. | MEDIUM | T3 |
| **`NeuralOrchestraConsumer` 3 parallel implementations** | `core/orchestra_consumers.py:33`, `core/consumers_base.py:2711`, `ai_core/intelligence/consumers.py:505` — same name, different implementations. Naming-collision + likely stale-duplicate. | MEDIUM | Post-arc cleanup candidate; Rigby SIGN cycle 1 candidate for intent-neutrality framing |
| **`UnifiedWebSocketHub` fallback bridging** | 12 routes bridge through `UnifiedWebSocketHub` including `/ws/bridge/*` — parallel to direct-consumer routes for same domains (`/ws/decision-command/` vs `/ws/bridge/decision/`). | LOW | Intentional bridge pattern; document if not already |

**§17 Summary:** 5 overlapping system pairs. PA polling+WS duplicate;
EventBus/WS/CeleryTaskEvent semantic overlap (S2099 T-slot);
sports routes orphaned; NeuralOrchestraConsumer naming-collision;
UnifiedWebSocketHub bridge pattern. **Consolidation owed post-arc**
(T3, T6 + naming-collision cleanup).

## 18. Ownership Gaps

**F18.1 — CODEOWNERS file absent (S2201 §18.1 F4 UNCHANGED)**

- **Type:** ownership-drift
- **Severity:** HIGH (single-operator caveat per S2201 F4 fold —
  CRITICAL if second contributor joins)
- **Evidence:** No file at repo root or `.github/CODEOWNERS`
- **Surface:** `useWebSocket.ts`, all consumer files, all routing.py
  modules — UNKNOWN ownership at code-review time
- **Verdict:** Inherited from S2201 §18.1 F4; unchanged this session

**F18.2 — Consumer file session-annotation coverage**

- **Type:** governance-hygiene
- **Severity:** MEDIUM
- **Evidence:** Sample check: `core/new_pages_consumer.py` — no
  session-annotation header; `core/consumers_base.py` — mixed. Zero
  systematic audit of "which consumer was authored in which session,
  who owned it."
- **Surface:** All 50+ consumer files
- **Verdict:** Consistent with S2201 §18.1 F5 pattern — session-
  annotation coverage is sparse across FE + BE both

**F18.3 — Route registry ownership**

- **Type:** governance-debt
- **Severity:** MEDIUM
- **Evidence:** 125 route entries + 5 routing modules; no durable
  ownership map. This audit is the first artifact enumerating them.
- **Surface:** Route registry surface
- **Verdict:** T5 (durable registry) owed post-arc

**F18.4 — Envelope contract ownership**

- **Type:** governance-clarity-owed
- **Severity:** MEDIUM
- **Evidence:** S2003 P3 designed D4 envelope; implementation
  ownership TBD (candidate: Group 1700 Observability + Group 2500 API
  joint decision per §20.6 rationale)
- **Surface:** Envelope enforcement locus decision
- **Verdict:** Cross-arc handoff; Chris D-gate at S2299 close

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows (per
playbook §11.2 §19 shape).

### Meta-recommendation — Post-arc maintainer-decision batch (Rigby SIGN cycle 1 Q18 FOLD 2026-07-05)

R2 (DEAD-candidate cleanup) + R3 (MOCK-DATA intent) + R7
(NeuralOrchestraConsumer naming-collision) + R8 (regex-anchor cleanup)
share a common gate: **maintainer intent + delete-proof required
before removal / rewrite**. Bundle these into a single post-arc
"Maintainer-decision batch" T-slot rather than 4 independent
research items.

**Gating table:**

| Item | Needs maintainer signoff before action | Research can proceed autonomously (audit / spec / measure) |
|---|---|---|
| R2 DEAD-CANDIDATE removal | ✅ Yes — delete-proof + intent | Verification grep + runtime-log audit ✅ |
| R3 MOCK-DATA intent classification | ✅ Yes — intent (demo / obsolete / half-migrated) | Site inventory + `random.*` usage catalog ✅ |
| R7 NeuralOrchestraConsumer naming-collision | ✅ Yes — which impl is canonical? | 3-impl diff + call-site tally ✅ |
| R8 regex-anchor cleanup | ⚠️ Only if runtime behavior changes | Grep + normalize ✅ |
| **R1 Envelope enforcement locus** | ❌ (Group 1700 owns; not maintainer) | ✅ Full spec-prep + measurement + option-space |
| **R4 Route ↔ Consumer registry** | ❌ | ✅ Artifact draft + PLATFORM_INVENTORY augmentation |
| **R5 PA WS↔polling** | ❌ (Group 2500+2600 owns; not maintainer) | ✅ Cross-arc handoff draft |
| **R6 CODEOWNERS + governance** | ❌ (Chris + platform-owner decision) | ✅ Governance-debt inventory |
| **R9 CI lint (post T1/T2)** | ❌ | ✅ Blocked on T1+T2 completion |



**R1 — Envelope enforcement locus decision (BLOCKED pending Group 1700
Observability close)**

- **Rationale:** F3 + F4 + F5 mechanism gap. §20.6 Option (c) DEFER
  chosen. Group 1700's authority-provenance decision (Path A: WS
  display-only mirror → strict envelope; Path B: WS co-canonical →
  loose envelope) determines viable enforcement locus.
- **Owner:** Group 1700 xx99 close + joint decision with u-d-b arc
  team

**R2 — DEAD-CONSUMER intent confirmation + removal-vs-keep decision**

- **Rationale:** F6 flagged 11-13 candidate DEAD routes preliminary;
  maintainer confirmation required before removal (Rigby SIGN cycle 1
  intent-neutrality framing candidate)
- **Owner:** Post-arc T-slot (T9)

**R3 — MOCK-DATA-CONSUMER intent audit (5 confirmed sites)**

- **Rationale:** F1 pattern class generalizes. Each of 5 MOCK sites
  needs intent classification: intentional demo/dev-only vs obsolete
  vs half-migrated. Intent decides removal vs documentation.
- **Owner:** Post-arc T-slot (T4)

**R4 — Route ↔ Consumer registry durable artifact + PLATFORM_INVENTORY
augmentation**

- **Rationale:** F8 observation + T5 debt. 125-route enumeration
  should live in durable registry, not just audit doc. PLATFORM_
  INVENTORY augmentation with WS section.
- **Owner:** xx99 anchor-update batch

**R5 — PA WebSocket ↔ polling consolidation decision**

- **Rationale:** T6 architecture seam. Group 2600 PA arc owns.
- **Owner:** Group 2600 PA arc

**R6 — Consumer class ownership + CODEOWNERS establishment**

- **Rationale:** F18.1 + F18.2 + F18.3 governance debt cluster.
  Cross-arc systemic — not Child B-specific.
- **Owner:** Whole-platform governance layer post-arc

**R7 — `NeuralOrchestraConsumer` naming-collision cleanup**

- **Rationale:** §17 finding. 3 parallel implementations under same
  name.
- **Owner:** Post-arc cleanup

**R8 — Regex-anchor cleanup in `ai_core/routing.py`**

- **Rationale:** F7 + T8 cosmetic drift.
- **Owner:** Post-arc

**R9 — Envelope conformance tracking metric + CI lint (post-T1/T2
prerequisite)**

- **Rationale:** Once T1 serializer framework exists + T2 retrofit
  scoped, CI lint prevents regression on new emit sites.
- **Owner:** Post-arc (tied to T1 + T2)

## 20. Appendix

### 20.1 Files inspected

**Backend routing + consumers:**

- `core/asgi.py` (33 LOC — ProtocolTypeRouter + TokenAuthMiddlewareStack)
- `core/routing.py` (~500 LOC — 111 route entries)
- `sports/routing.py` (~11 LOC — 3 entries)
- `intelligence/routing.py` (~12 LOC — 3 entries)
- `ai_core/routing.py` (~14 LOC — 3 entries)
- `ai_core/intelligence/routing.py` (~14 LOC — 5 entries)
- `core/consumers_base.py` (3,200+ LOC — sampled at key line-ranges
  per Agent A1 registry)
- `core/new_pages_consumer.py` (~500 LOC — full read for F1 MOCK-DATA
  confirmation)
- `core/unified_hub.py` (~500 LOC — sampled for bridge pattern)
- `core/orchestra_consumers.py` (~800 LOC — sampled for NeuralOrchestra
  duplicate)
- `sports/consumers.py` (~900 LOC — sampled for 3 AsyncJson consumers
  + F1 SportsConsumer MOCK)
- `intelligence/consumers.py` (~1,200 LOC — sampled for IncomeBuilder
  + RevenueIncome)
- `core/decision_command_consumer.py` (~350 LOC — F1 MOCK confirmation)
- `sports_betting/consumers.py` (~250 LOC — F1 MOCK confirmation)
- `core/platform_unification_orchestrator.py` (~1,150 LOC — sampled for
  candidate DEAD F6)
- `core/ws_auth_middleware.py` (sampled — auth-wrap pattern)

**Frontend hooks + subscribers:**

- `frontend/src/hooks/useWebSocket.ts` (188 LOC — full read; hook +
  useSystemEvents wrapper)
- `frontend/src/pages/CommandCenterPage.tsx` (sampled at line 683 + 707
  RigbyToolTicker path)
- `frontend/src/pages/AgentsPage.tsx` (sampled at lines 696, 918, 928,
  922, 938)
- `frontend/src/pages/IntelligencePage.tsx` (sampled at line 313)
- `frontend/src/pages/WorkspacePageNew.tsx` (sampled at line 866)
- `frontend/src/components/layout/Layout.tsx` (sampled at line 45)
- `frontend/src/components/HeartWidget.tsx` (sampled at line 239 + 242)
- `frontend/src/pages/BettingPage.tsx` (grep-only — zero WS matches
  confirmed at line count ~3,023)

### 20.2 Docs inspected

- `docs/PLATFORM_WHAT_IT_IS.md` (narrative anchor)
- `docs/PLATFORM_INVENTORY.md` §Frontend + §Runtime (runtime anchor)
- `docs/topics/frontend.md` (subsystem doc, stale-warned)
- `docs/topics/agent-system.md`
- `docs/topics/personal-assistant.md`
- `docs/EVENT_SYSTEM_INVENTORY.md`
- `docs/UDB_BEHAVIOR_LAYER.md` (envelope references)
- `docs/UDB_TRANSLATION_LAYER.md`
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 template + §13
  6-Explore-agent pattern + §14 verifier-loop
- `docs/research/domains/frontend/2200_frontend_domain_scoping.md`
  (parent scoping)
- `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md`
  (Child A shipped — F2 baseline)
- `docs/research/domains/event_integration_architecture/2002_*.md`
  (D4 envelope first mention)
- `docs/research/domains/event_integration_architecture/2003_*.md`
  (D4 envelope canonical spec §10.3.4)
- `docs/research/domains/event_integration_architecture/2099_*.md`
  (F16 envelope absent + unenforced — Group 2000+ arc-close)
- `docs/research/domains/sports/1505_sports_frontend_surface_audit.md`
  (§14.1 F5 MOCK + §14.5 zero-WS-subscription)
- `docs/research/domains/observability/2104_*.md` (S2104 §17.3 + §20.1
  cross-arc coordination)

### 20.3 Grep patterns used

- `re_path\(|path\(` in `**/routing.py` (BE registry enumeration)
- `AsyncJsonWebsocketConsumer|AsyncWebsocketConsumer` in `**/*.py`
  (consumer class enumeration)
- `useWebSocket|useSystemEvents|new WebSocket|wss:|ws:` in
  `frontend/src` (FE subscription enumeration)
- `render_hint|ui\.render_hint|ui_render_hint` in `**/*.py` +
  `frontend/src` (envelope conformance measurement — 0 matches)
- `channel_layer\.group_send|self\.send_json|self\.send\(` in
  `core/consumers*.py` (emit-site enumeration for F3 sampling)
- `random\.randint|random\.uniform|random\.choice` in consumer files
  (F1 MOCK-DATA classification)
- `TokenAuthMiddlewareStack|AuthMiddlewareStack` in `core/*.py`
  (auth-wrap uniformity confirmation)
- `WebSocket|websocket|WS` in `docs/topics/*.md` (doc-coverage
  inventory)
- `Session \d+` in consumer files (§18.2 session-annotation coverage
  sample)
- `CODEOWNERS` at repo root (F18.1 absence confirmation)

### 20.4 Unresolved unknowns

- Per-emit-site EventBus-canonical-peer status — deferred to S2099
  T-slot (R.EVENTS.COMPOSITION-CONTRACT-CONSISTENCY-REGISTER); Child B
  does not audit which of ~40 emit sites have canonical EventBus
  peer emission.
- DEAD-CONSUMER intent per candidate — maintainer confirmation required
  before removal (F6 preliminary status).
- MOCK-DATA-CONSUMER intent per site — intentional demo vs obsolete
  vs half-migrated classification (F1 T4 debt).
- Group 1700 Observability arc runtime cadence — §20.6 Option (c)
  DEFER hinges on Group 1700 xx99 close; if slip past S2299, revisit.
- Envelope schema evolution semantics (`schema_version` field) —
  T7 deferred pending T1 serializer framework.
- Direct-Redis-pub/sub bypass of WS surface — if any BE code bypasses
  channel_layer + emits Redis pub/sub direct, that shape is not
  audited here; not surfaced by grep sample.

### 20.5 Conflicts between sources

- **Parent scoping §5 Child B "~33+" vs Agent A1 125 route entries.**
  See §14 F8 + §6. Delta hypothesis: parent estimate was route-
  normalized to unique consumer classes / files (~50-60 unique classes
  after de-dup + shared consumers); Agent A1 counted all route
  registrations including duplicates, bridges, aliases. Neither
  "wrong" — different measurement. Recommend xx99 canonicalize.
- **EVENT_SYSTEM_INVENTORY §2.6 "57 WebSocket consumer classes" vs
  Agent A1 125 route entries + ~50-60 unique classes.** Cross-check
  needed: is EVENT_SYSTEM_INVENTORY §2.6 counting unique consumer
  files or unique consumer classes? Reconcile at xx99.
- **A3 candidate DEAD-CONSUMER flag on `/ws/reality-check/` +
  `/ws/truth-dashboard/` + `/ws/system-monitor/` vs S2003 §10.5 6-
  substrate composition register.** These may be observability-adjacent
  surfaces staged for future Group 1700 integration; require
  maintainer confirmation before treating as DEAD.

### 20.6 POSTURE-DECISION evidence plan owed to xx99

Per S2200 §5 Child B delegation — enforcement-locus recommendation
for `ui.render_hint` envelope.

**Evidence gathered by Child B:**

| Sub-axis | Contract-level verdict | Evidence pointer |
|---|---|---|
| BE consumer registry | EXPERIMENTAL (125 routes; MOCK-DATA generalizes; 11 candidate DEAD) | §6 + §14 F1 + F6 |
| FE subscription coverage | LIGHT (8 sites reach ≈5 endpoints out of 125 = ≈4% coverage) | §6 + §14 F2 |
| Envelope conformance | UNMET (0/40 = 0%; S2099 F16 UNCHANGED) | §14 F3 |
| Envelope infrastructure | UNMET (no serializer + no validator + no version negotiation) | §14 F4 + F5 |
| Auth wrap | STABLE (TokenAuthMiddlewareStack uniformly 125/125) | §3 + §9 |
| Documentation coverage | LIGHT (topics/frontend.md WS mention only; zero envelope coverage; PLATFORM_INVENTORY has no WS section) | §11 |
| Ownership | LIGHT (CODEOWNERS absent; session-annotation sparse; 125 routes distributed) | §18 |

**Child B recommendation to xx99 (Rigby SIGN cycle 1 SIGN-with-edits
at HIGH confidence — committed action + option space; final A/B/C
outcome not committed):**

> **§20.6 Option (c) DEFER envelope enforcement** to post-Group 1700
> Observability arc close. Stage T2 R.EVENTS.UI-RENDER-HINT-ENVELOPE-
> RETROFIT in Group 1700 T-slot with explicit scope:
> (a) retrofit ~40 BE emit sites to wrap `send_json` / `group_send`
>     with envelope helper enforcing `type: "ui.render_hint"`,
>     `event_id`, `source_canonical`, `display`
> (b) retrofit ≥5 FE subscription hooks to validate envelope on receive
> (c) add CI lint (grep + schema validator) for post-envelope emit sites
>
> **Escape hatch (Rigby SIGN cycle 1 Q11 STRENGTHEN 2026-07-05 fold —
> prevents indefinite deferral):** if Group 1700 does not close by
> S2299 xx99 (Group 2200 close), re-evaluate Path A/B/C in the
> S2299 canonical summary; alternatively, open a targeted
> follow-on-arc T-slot with a hard revisit date. Deferral is not open-
> ended — it is bounded by Group 1700 xx99 close cadence.
>
> **Rationale:** D4 envelope adoption is load-bearing on Group 1700
> authority-provenance + observability maturity gates (S2104 §17.3 /
> §20.1 cross-arc coordination). Group 1700 must decide Path A vs
> Path B vs Path C (see below) before enforcement locus (registration-
> time vs runtime) can be safely chosen. Enforcing in isolation risks
> double-retrofit post-Group 1700 closure.
>
> **Path triad (Rigby SIGN cycle 1 Q12 STRENGTHEN 2026-07-05 fold —
> Path C added; decision axis = "does this message mutate authoritative
> state?"):**
>
> - **Path A — WS is display-only mirror.** Strict envelope enforcement
>   for all WS messages; every emit wrapped, every consumer validated.
>   Coherent with S2003 D4 "display-only" framing.
> - **Path B — WS is co-canonical for real-time UI state.** Loose
>   envelope; dual-emission policy allows both authoritative + display
>   fields; lint check for governance-adjacent flows only.
> - **Path C — Envelope mandatory for integrity-critical / governance /
>   money / state-changing flows; optional for purely visual signals**
>   (heartbeats, presence, tickers, animations). Enforcement locus
>   varies per-emit-site by the "authoritative-state-mutation?" axis.
>   Path C is the middle ground; may be Group 1700's natural
>   preference if authority-provenance is bounded by class of message,
>   not by transport.
>
> **Option (a) registration-time** documented as alternative if
> Group 1700 close date slips past S2299 xx99: metaclass or decorator
> on `AsyncWebsocketConsumer` subclasses binds envelope contract at
> class-definition load; lint check catches new non-compliant
> `group_send` sites. Blast radius: 122 consumer classes. Rollback
> LOW (warning-mode) or MEDIUM (blocking). Example non-authoritative
> shape only — not an authoring commitment.
>
> **Option (b) runtime** documented as alternative if Path A commits
> to strict envelope + Group 1700 requires per-message validation:
> wrap `channel_layer.group_send` or `AsyncWebsocketConsumer.
> send_json` in helper that validates envelope shape every emission.
> Blast radius: ~40 emit sites + wrapper. Rollback HIGH if strict
> mode. Example non-authoritative shape only — not an authoring
> commitment.
>
> **Recommendation-strength: HIGH confidence in the committed action**
> (deferral to Group 1700 is the correct governance sequencing) **+
> Group 1700 is the correct owner of the enforcement-locus decision.**
> Confidence is NOT claimed on final Path A/B/C outcome — the triad
> is the option space we hand to Group 1700; xx99 close does not
> pre-commit to a specific path. Multi-axis corroboration from 6
> Explore agents + F3 UNCHANGED at 0/40 conformance + S2104 §17.3
> cross-arc dependency + prior-arc F16 alignment (Rigby SIGN cycle 1
> Q17 STRENGTHEN 2026-07-05 fold — commit-strength framing). Chris
> D-gate at S2299 close.

**Cross-arc evidence flags (owed to xx99):**

- Group 1700 Observability — envelope enforcement locus decision joins
  authority-provenance decision (§9 + §20.6)
- Group 2400 Auth — TokenAuthMiddlewareStack uniformly applied
  125/125; NO drift found at Child B slice; per-message auth (post-
  connection revocation, token refresh) out of scope
- Group 2500 API — payload shape `event.type` string dispatch
  parallels REST-endpoint pattern gaps (S1505 §15.5); single message
  contract SoT candidate for envelope schema
- Group 2600 PA — WS-vs-polling consolidation decision (§17 + T6)

### 20.7 Rigby SIGN fold notes

**Rigby SIGN cycle 1 result: SIGN-with-edits at HIGH confidence** via
dedicated fresh SIGN isolation pin `pa-e786b77eb4c842b2` (minted at
draft-complete via `session_tool.create_fresh` per playbook §15
SIGN-isolation discipline; retired at cycle close via
`session_tool.retire`). **4 batches × 5 questions = 20 total Q; 19
folds landed pre-commit-gate.** Cycle 2 NOT required per Rigby cycle-1
HIGH confidence + all folds landable.

**Cadence per feedback_rigby_sign_worker_instability_recovery** —
4×5 batching per 20-section audit shape (THIRTEENTH-consecutive
formal SIGN cycle under Research OS after S1301+S1401+S1501+S1601+
S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201 + S2200 parent
scoping = this is the 15th SIGN cycle in the arc-parent-with-children
pattern).

**MC-4 codification note (Rigby SIGN cycle 1 Q19 STRENGTHEN
2026-07-05 fold — codification-language conditionality):** S2202
constitutes candidate evidence for MC-4 template-application count
extension **12 → 13 consecutive**. **Codification framing is
CONDITIONAL** pending Chris ratification / final wording at S2299
canonical summary close per playbook §11.2 template evolution
discipline. This session does NOT unilaterally codify the extension;
it registers the 13-consecutive evidence with Chris-gated ratification
path preserved.

**19 folds by batch:**

- **Batch 1 (Q1-Q5): framing + severity calibration.**
  - **Q1 STRENGTHEN** — §14 F1 MOCK-DATA severity reframed **CRITICAL
    → HIGH baseline + CRITICAL for user-visible surfaces** (DBAO
    dashboards, Betting, Decision-Command live ops). Severity rule
    added: scales with user-visibility / money-path / reliability-
    critical exposure, not by `random.*` presence alone. Mirrors
    S2201 F1/F3 precedent.
  - **Q2 STRENGTHEN** — §14 F3 envelope conformance rate reframed:
    **primary 0/40 consumer classes = 0% conformance**; **secondary
    ~0/100+ send_json callsite denominator** yields same 0% verdict
    at higher confidence. Prevents undercount / handwave.
  - **Q3 CLEAN + micro-fold** — §14 F6 severity kept MEDIUM with
    **delete-proof gate** (no imports + no routes + no runtime logs
    triad); downgrade to LOW-until-confirmed absent delete-proof.
    DEAD-CANDIDATE / INTENT-NEUTRAL language.
  - **Q4 STRENGTHEN** — §1 + §14 F1 MOCK-DATA generalization language
    reframed **"generalizes system-wide" → "recurs across ≥5 WebSocket
    product surfaces spanning 3 consumer modules"** (multi-surface
    recurrence, not system-wide). Not claiming all WS consumers are
    mock-backed.
  - **Q5 CLEAN** — §14 F8 PLATFORM_INVENTORY-no-WS-count kept as
    **observation** (inventory sectioning = scope choice, not error);
    optional enhancement candidate, not drift finding. Mirrors S2201
    F1 route-count-delta precedent.
- **Batch 2 (Q6-Q10): falsifier + coverage-math + F2 verdict.**
  - **Q6 STRENGTHEN** — §1 coverage table + §14 F2 augmented with
    **per-event-type coverage nuance** for `/system-events`
    multiplexer (1 route, 14 event types). Verdict unchanged;
    confidence increased.
  - **Q7 STRENGTHEN** — §1 coverage table + §14 F2 augmented with
    **Layout surface-global attribution rule** ("global wrappers
    contribute to every surface they gate"). Layout's `/system-events`
    subscription bumps every surface's minimum count by 1. Verdict
    unchanged; confidence increased.
  - **Q8 STRENGTHEN** — §1 + §14 F2 verdict reframed **"SYSTEMIC" →
    "SYSTEMIC (with surface variance)"** — SYSTEMIC deficiency across
    all surfaces <25% is primary; ≈5× spread (PA 20% vs Betting 0%)
    is real variance nuance, not noise.
  - **Q9 CLEAN + micro-fold** — §1 Denominator contract box added:
    **B1 subscription-completeness → routes (125); B2 envelope-
    conformance → unique consumer classes (~50-60); F3 emit-site
    sampling → consumer classes with `group_send` (40)**. Prevents
    reader conflation.
  - **Q10 STRENGTHEN** — §14 F2 sampling completeness note added
    covering `useSystemEvents` wrapper + `useWebSocket.ts:81`
    single-`new WebSocket()`-source trace. Blind-spot minimized;
    cycle-2 trigger candidate if future audit finds alternate
    subscribers.
- **Batch 3 (Q11-Q15): cross-arc + POSTURE-DECISION defense.**
  - **Q11 STRENGTHEN** — §20.6 DEFER escape hatch added: if Group
    1700 does not close by S2299 xx99, re-evaluate Path A/B/C in
    canonical summary or open targeted follow-on-arc T-slot. Bounded
    deferral.
  - **Q12 STRENGTHEN** — §20.6 **Path triad established: Path A
    (WS display-only mirror → strict envelope) + Path B (WS
    co-canonical → loose envelope) + Path C (envelope mandatory for
    integrity/governance/money/state-changing flows; optional for
    purely visual signals)**. Decision axis: "does this message mutate
    authoritative state?" Path C added as middle-ground option.
  - **Q13 STRENGTHEN** — §17 T6 owner reframed **Group 2600 PA →
    joint Group 2500 API + Group 2600 PA**; lead = whichever owns the
    status endpoint contract. Cross-cutting transport-choice + PA
    UX/ops seam.
  - **Q14 STRENGTHEN** — §9 Group 2400 Auth "NO drift found"
    hedged: **"No drift found in connection auth wrapper (125/125
    TokenAuthMiddlewareStack); per-message auth / mid-session token
    revocation / token refresh NOT evaluated."** Mirrors S2201 Q8
    STRENGTHEN sampling-scope-hedge pattern.
  - **Q15 STRENGTHEN** — §2 preamble Interpretation rule box added:
    DEAD/MOCK/INTENT-UNKNOWN findings are **candidates until
    maintainer intent + usage proof**; do not treat as removal-ready
    by default. Generalizes S2201 F1 CLEAN + micro-fold pattern to
    Child B. Reduces per-finding hedge repetition.
- **Batch 4 (Q16-Q20): anti-scope + POSTURE + verdict.**
  - **Q16 CLEAN** — Anti-scope §7 adherence confirmed: verbs stay
    recommend / propose / evaluate (not implement / change /
    refactor); §20.6 Option (a) + (b) shape sketches labeled
    "example non-authoritative shape only — not an authoring
    commitment."
  - **Q17 STRENGTHEN** — §20.6 commit-strength framing added:
    **HIGH confidence in the committed action (deferral to Group 1700
    is correct governance sequencing) + Group 1700 is the correct
    owner**; NOT claiming HIGH confidence on final Path A/B/C outcome.
    Triad is the option space handed to Group 1700; xx99 does not
    pre-commit specific path.
  - **Q18 FOLD** — §19 meta-recommendation added: **Post-arc
    maintainer-decision batch** bundles R2 + R3 + R7 + R8 (DEAD +
    MOCK + naming-collision + regex cleanup) into one governance
    gate; R1 + R4 + R5 + R6 + R9 remain active-research tracks.
    Gating table added distinguishing "needs maintainer signoff"
    vs "research can proceed autonomously."
  - **Q19 STRENGTHEN** — §20.7 codification-language framing: MC-4
    template-application evidence extension 12 → 13 registered as
    **candidate**; final codification wording CONDITIONAL pending
    Chris ratification at S2299 canonical summary close.
  - **Q20 verdict** — **SIGN-with-edits at HIGH confidence.** Minimum
    edits pre-commit-gate: Q1/Q2/Q4/Q6/Q7/Q8/Q10/Q11/Q12/Q13/Q14/Q15/
    Q17/Q18/Q19 folds landed via targeted edits above. Q3/Q5/Q9/Q16
    micro-folds absorbed inline. Critical residuals: none blocking
    SIGN. Cycle 2 trigger candidates: (a) discovery of significant
    FE subscriber paths outside current grep scope (Q10 fails),
    (b) evidence that `/system-events` per-type coverage materially
    alters SYSTEMIC conclusion (Q6/Q8 revisit), (c) new requirement
    doc proving inventory MUST include WS counts (Q5 reclassify to
    drift). Confidence rationale: issues were calibration + rubric-
    math + scope-guarding + cross-arc-handoff-ownership, not
    foundational errors.

**SIGN pin retirement:** SIGN isolation pin `pa-e786b77eb4c842b2`
retired at cycle close via `session_tool.retire` per playbook §15
SIGN-isolation discipline + `feedback_session_tool_retire_works`.
