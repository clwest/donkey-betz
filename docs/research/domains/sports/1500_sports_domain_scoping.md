---
title: "S1500 Sports / DBAO — Parent Architecture Scoping (Group 1500 mission plan)"
status: draft
authority: parent-doc
session_added: 1500
research_group: 1500
child_slot: P0
domain_slug: sports
date: 2026-07-01
last_verified: 2026-07-01
supersedes: none
related:
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                      # process (S1276 v2)
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md             # OS (S1279 v2.1)
  - docs/research/platform_architecture_inventory.md               # runtime map (S1273)
  - docs/research/platform/cross_domain_integration_audit.md       # integration lens (S1274)
  - docs/research/OPEN_ARCS.md                                     # arc manifest
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                     # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                                    # narrative anchor
  - docs/research/platform_architecture_inventory.md               # §3.10 Sports/Odds/DBAO row (S1273)
  - docs/research/platform/cross_domain_integration_audit.md       # §12.3 decision point + §7.2 missing edges (S1274)
dependencies_on: []
delegates_to:
  - group: 1400
    slug: revenue
    scope: sportsbook affiliate / referral revenue attribution and betting-outcome→ImpactEvent wiring — Group 1400 Revenue arc territory; Group 1500 P2 cites the boundary but does NOT audit revenue attribution paths.
  - group: 1600
    slug: content
    scope: sports content generation quality + betting-related deliberation surface design — Group 1600 Content arc territory; reachable ONLY IF a downstream design-preparation arc picks Integration posture. Group 1500 P2 flags the edge; Group 1600 owns content-side evidence.
delegated_from: []
verifier_loop: |
  v1 (2026-07-01, S1500): parent scoping drafted at Group 1500 open per
  Chris's short command "start research group 1500" running in parallel
  with a separate Claude Code session running Group 1400 Revenue on the
  same repo checkout. No parallel-arc contamination — this doc touches
  only `docs/research/domains/sports/` (new subdirectory) and does not
  write to shared state files (OPEN_ARCS.md, 00-START-NEXT-SESSION.md,
  tools/pa_local.sh) until inter-arc coordination with Chris resolves.
  Evidence base:
    (a) S1274 §12.3 Sports/DBAO ↔ AI Studio decision point (Rigby-
        corrected framing: "not a presumed defect — a decision point
        with two legitimate postures + criteria for either answer").
    (b) S1274 §7.2 row 6 (missing edges Sports→Signal / Sports→Content /
        Sports→Revenue).
    (c) S1273 §3.10 Sports / Odds / Betting Intelligence (DBAO)
        inventory row — WORKING maturity, LIGHT research coverage,
        "no dedicated sports intelligence doc" flagged.
    (d) S1274 §9.5 Sports Intelligence MEDIUM service-extraction
        readiness (self-contained today).
    (e) S1273 §3.18 Frontend / §3.20 Discord / §3.22 API surfacing
        for Category D user-facing sports surfaces (no dedicated
        S1273 row for sports UI cluster).
  Status: draft — awaiting Chris ratification of D1/D2/D3 open
  decisions (§8), pin coordination with parallel 1400 Claude,
  and light Rigby SIGN routing per playbook §15 parent-scoping row.
owner: claude (Chris directed at S1500 open via short command; running in parallel with a separate Claude Code session on Group 1400)
---

# Session 1500 — Sports / DBAO Domain Scoping (Phase 0)

---

## RESUME NOTES (paused 2026-07-01 — Group 1400 must close first)

**Why paused.** Chris opened Group 1500 in parallel with a separate Claude
Code session already running Group 1400 Revenue on the same repo checkout.
After the 1500 parent scoping doc landed, Chris called off the parallel-arc
experiment: "it doesn't look like it's a good idea to run multiple researches
at a time." Feedback memory `feedback_no_parallel_research_arcs.md` captures
the anti-pattern and its evidence. Group 1500 resumes after Group 1400 closes
(canonical summary S1499 merged to `main`).

**What is done.**

- Parent scoping doc §1-§10 drafted end-to-end (this file, 613 lines).
- Verdict: parent-with-children, compact 4-session arc (S1500 parent +
  S1501 subsystem baseline audit + S1502 boundary evidence audit + S1599
  canonical summary).
- Framing constraint locked to S1274 §12.3 Rigby correction (no posture
  presumption — evidence only in children; two-posture success criteria
  matrix in S1599; posture selection is downstream design-preparation arc).
- Delegations to Group 1400 Revenue (affiliate revenue attribution) +
  Group 1600 Content (content quality) declared in frontmatter.
- Anti-scope §7 covers posture selection, external-integrations territory,
  affiliate revenue, content quality, Symbol-Mapping-blocked governance,
  implementation PRs, model proposals.
- Six candidate finding areas parked in §6 as P1/P2 audit input
  (GameLineHistory dead-storage question, MLPrediction heuristic opacity,
  SportsContentContext wiring status, BettingPage tab-count drift, Discord
  sports command inventory completeness).
- Branch `docs/session-1500-sports-research-group` created off `main` at
  commit `4b3719d4`. Only new file in the diff — parallel 1400 Claude's
  uncommitted `tools/pa_local.sh` rotation left untouched.

**What is NOT done (pending future session).**

1. **Chris ratification of §8.1 proposed defaults** (5 recorded decisions:
   parent-with-children verdict, Rigby §12.3 framing constraint, 4-session
   arc rhythm, revenue delegation, content delegation).
2. **Chris resolution of §8.2 open decisions D1–D5**:
   - D1 Category D user-facing surfaces routing (fold into P1 vs spin off
     vs delegate — proposed default: fold into P1 with dedicated §N).
   - D2 F6 blocked-status handling (document as blocked in P2 vs drop from
     scope vs Symbol-Mapping-dependent arc — proposed default: document as
     blocked).
   - D3 S1599 posture-criteria enumeration scope (enumerate criteria
     without recommending vs defer entirely — proposed default: enumerate,
     no recommendation).
   - D4 Group 1500 arc pin mint (needs Rigby `session_tool.create_fresh`
     after Group 1400 closes; do NOT rotate `tools/pa_local.sh` — use
     `pa_chat.py --conversation <group-1500-pin>` directly).
   - D5 Rigby SIGN routing for this parent doc (light SIGN per playbook
     §15 parent-scoping row — route on a fresh isolation pin, fold edits,
     bump `status` frontmatter from `draft` to `active`).
3. **Shared-state file updates** (deferred to avoid parallel-arc contention):
   - Move Group 1500 row from Not started → In-progress on
     `docs/research/OPEN_ARCS.md` + add 2026-XX-XX S1500 open reconciliation
     note.
   - Update `00-START-NEXT-SESSION.md` to point at S1501 as the next
     Group 1500 session.
   - Add ARCHITECTURE_INDEX §1.N row for Group 1500 (bump version).
4. **PR / merge to `main`** — no PR opened; branch is a committed draft
   only.

**How to resume.**

1. Verify Group 1400 has closed (canonical summary S1499 merged; OPEN_ARCS
   shows Group 1400 in Closed section; `tools/pa_local.sh` header rotated
   past the 1400 arc pin).
2. `git checkout docs/session-1500-sports-research-group` — the branch
   is preserved with this doc committed.
3. Rebase on `main` to pick up post-1400 state:
   `git fetch origin && git rebase origin/main`. Resolve conflicts if
   Group 1400's changes touched anything in `docs/research/` (unlikely
   for the parent doc but possible for peripheral files).
4. Read the RESUME NOTES section (this one) + §5 (child mission sequence)
   + §8 (decisions) + §6 (parked candidates) — this is the entire arc plan.
5. Ask Chris to ratify §8.1 defaults + resolve D1-D5 open decisions.
6. Have Rigby `session_tool.create_fresh` mint the Group 1500 arc pin.
   Title: "Session 1500 — Sports research group (kickoff)". Do NOT rotate
   `tools/pa_local.sh`; use `pa_chat.py --conversation <pin>` directly for
   all Group 1500 sessions.
7. Route the parent doc to Rigby for light SIGN per playbook §15 on the
   Group 1500 pin's fresh SIGN isolation pin.
8. Fold edits → flip `status: draft` → `status: active` → open PR.
9. After Chris commit-gates the parent PR: OPEN_ARCS + START-NEXT +
   ARCHITECTURE_INDEX updates same-commit or immediate follow-on per
   playbook §16. Then S1501 opens per playbook §11.2 20-section audit
   template.

**Key references.**

- **This doc:** `docs/research/domains/sports/1500_sports_domain_scoping.md`
- **S1274 §12.3** (`docs/research/platform/cross_domain_integration_audit.md:1561-1598`)
  — the load-bearing framing constraint (Rigby-corrected: decision point,
  not defect).
- **S1273 §3.10** (`docs/research/platform_architecture_inventory.md:872-959`)
  — the primary Sports/DBAO inventory row + drift bullets that seeded §6
  parked candidates.
- **S1274 §7.2 row 6** — the three MISSING edges (Sports→Signal / Content /
  Revenue) that Category E audits.
- **S1274 §9.5** (`cross_domain_integration_audit.md:1310-1320`) — MEDIUM
  service-extraction readiness signal informing island-posture feasibility.
- **Playbook §11.1 parent-scoping template** — the structural rubric this
  doc follows.
- **S1300 exemplar** — `docs/research/domains/memory/1300_memory_domain_scoping.md`
  — the parent-doc structural template used as reference.
- **Feedback memory** — `feedback_no_parallel_research_arcs.md` — why this
  arc paused.

---

> **What this doc is.** A scoping deliverable produced *before* any
> domain audit begins. Per playbook §11.1 parent-scoping template, it
> answers whether Group 1500 should be single-audit or
> parent-with-children, locks the child mission sequence, names the
> anti-scope, and cross-links delegations. Chris ratifies the recorded
> decisions before any child audit launches.
>
> **What this doc is not.** The audit itself. A posture recommendation.
> An implementation proposal. Per S1274 §12.3's Rigby-corrected framing,
> this doc explicitly does NOT presume "island vs integrated" is a
> defect — it treats it as a decision point with two legitimate
> postures, each with success criteria to be enumerated by the child
> audits.

---

## 1. Why Phase 0

The Group 1500 range name is *Sports / DBAO / Intelligence*, seeded in
`00-START-NEXT-SESSION.md` and `docs/research/OPEN_ARCS.md` "Not
started" queue with rationale *"Structural question: island vs
integrated (S1274 §12.3)."* That rationale is the load-bearing framing
for Phase 0: the arc must decide whether Sports/DBAO is one bounded
subsystem to audit end-to-end, or a parent capability composed of a
WORKING internal core (odds ingestion, prediction, settlement) plus a
distinct set of **cross-boundary edges** (Sports↔Signal/Content/
Revenue/Deliberation) that constitute an unresolved product/
architecture decision point.

**Rigby-corrected framing (S1274 v2 §12.3, post-SIGN).** The v1
integration audit called this a "structural question" implying a
defect. Rigby's correction is critical for how Group 1500 scopes:

> It's a decision point with two legitimate postures, each with
> explicit success criteria. Research should enumerate the criteria,
> not presume the answer.

Group 1500 inherits this constraint end-to-end. **No child audit will
recommend a posture.** The canonical summary (§5 P3 below) enumerates
posture success criteria; a downstream design-preparation arc consumes
those criteria and recommends; Chris ratifies via ADR.

The playbook §2 rule 3 explicitly permits multi-subsystem sub-grouping:

> If the domain is bigger than expected, splitting into sub-groups is
> fine. Do not force a single session to cover a multi-subsystem
> domain.

Sports/DBAO qualifies. Section 4 lays out the parent-vs-single
evidence.

---

## 2. What existing inventory already tells us

The S1273 platform inventory has **one primary row** for Sports/DBAO
plus **three adjacent rows** where sports surfaces appear alongside
other domains, and **three missing-edge rows** flagged by S1274.

### 2.1 Primary inventory anchor

| S1273 Row | Title | Coverage | Maturity |
|-----------|-------|----------|----------|
| §3.10 | Sports / Odds / Betting Intelligence (DBAO) | LIGHT–MODERATE | WORKING |

S1273 §3.10 (`platform_architecture_inventory.md:872-959`) documents
the subsystem: TheOddsSpider (40+ bookmakers × 60+ sport keys),
GamePredictor (LLM-analyzed prediction from odds consensus), MLPrediction
(auto-created via SPORT_KEY_LEAGUE mapping, S1010/S1012 dedup),
BettingOutcomeVerifier, SharpActionDetector, ArbitrageDetector,
League/Team/Game (sports app), PlacedWager/PlacedWagerLeg
(`core/models_betting.py`), GameLineHistory
(`core/models_odds_history.py`), SportsContentContext,
SportsBettingCoordinator, and REST endpoints under `/api/odds-sports/*`.
Row explicitly notes: *"No dedicated sports intelligence doc"* and
*"sports_odds is not a valid SignalCluster data_type track; sports
predictions do NOT auto-create Initiatives; betting outcomes NOT fed to
deliberation."*

### 2.2 Adjacent inventory rows where sports surfaces appear

| S1273 Row | Sports surface | What lives there today |
|-----------|----------------|-------------------------|
| §3.8 | Spider Framework | TheOddsSpider + CombatSportsSpider concrete classes |
| §3.18 | Frontend / Workspace UI | `frontend/src/pages/BettingPage.tsx` → `/betting` 9-tab dashboard (odds today / sharp action / AI record / arbitrage / bankroll / bet placement / etc.) |
| §3.20 | Discord Bot | Sports commands `/predictions`, `/odds`, `/arb`, `/bankroll`, `/bet` inside the 11,676-line `core/services/discord_bot.py` |
| §3.22 | API Layer | `POST /api/odds-sports/convert-odds/`, `POST /api/odds-sports/expected-value/`, `GET /api/odds-sports/todays-games/`, `POST /api/odds-sports/kelly-criterion/`, `GET /api/odds-sports/ai-track-record/` |
| §3.26 | External Integrations | Odds providers, Alpha Vantage, Polygon.io, SEC (via tasks) |

Category D (user-facing sports surfaces) has no dedicated inventory
row of its own — it lives scattered across §3.18/§3.20/§3.22. That is
independent evidence for either (i) a first-inventory-landing child
audit or (ii) folding user surfaces into the P1 subsystem audit with a
dedicated §N landing the missing row. See §8 D1 for the open decision.

### 2.3 Missing-edge rows flagged by S1274 §7.2

The S1274 cross-domain integration audit registers three MISSING edges
originating from Sports/DBAO (row 10 in its §7.2 relationship matrix,
`cross_domain_integration_audit.md:265-270`):

| Source | Target | Status | S1274 finding |
|--------|--------|--------|---------------|
| Sports/DBAO (10) | Signal Engine (9) | MISSING | `sports_odds` is not a valid `SignalCluster.data_type` track (S1273 §3.10) |
| Sports/DBAO (10) | Content Pipeline (11) | MISSING | Sports predictions do NOT auto-create Initiatives or Deliverables |
| Sports/DBAO (10) | Revenue Pipeline (32) | MISSING | Betting outcomes not fed to opportunity attribution |

S1274 §12.3 escalated these into the decision-point framing:

> Whether that gap is a defect or an intentional island is a
> product-architecture call — not a research finding. This mission
> enumerates the two postures with criteria.

That framing IS Group 1500's scope. Section 3 lays out the taxonomy
that lets the arc address both postures without presuming either.

### 2.4 Service-extraction readiness signal

S1274 §9.5 ranks Sports Intelligence at **MEDIUM** service-extraction
readiness (`cross_domain_integration_audit.md:1310-1320`), noting the
Sports app is self-contained today. That readiness signal is
independent evidence that the island posture is technically viable —
not that it is preferred. Section 3 categorizes island-invariant
questions as Category F to be audited under Group 1500 P2.

---

## 3. Candidate subdomain taxonomy

Six categories are candidates for the arc's scope. Each row lists
primary systems in scope, the S1273 anchor row (if any), and drift
already flagged.

### A — Odds Ingestion + Real-time Intelligence

- **Systems:** `ai_core/spiders/specialized/theodds_spider.py:TheOddsSpider`
  (line 193 `fetch_data`, line 200+ `fetch_scores`), `SharpActionDetector`,
  `ArbitrageDetector`, `GameLineHistory` (`core/models_odds_history.py:82`,
  bookmaker-level odds time-series).
- **Anchor:** S1273 §3.10 (primary).
- **Known drift:** S995→S998B `fetch_scores()` refactor (returns
  completed + in-progress); S1012 dedup fix (Max('id') per game_id);
  `GameLineHistory` tracked but not actively queried in any service
  (S1273 §3.10 debt bullet).

### B — Prediction + Settlement (Agents + ML)

- **Systems:** `core/agents/markets/game_predictor.py:GamePredictor.execute()`
  (line 67 LLM-analyzed prediction from odds consensus; line 114+
  `_store_predictions`), `MLPrediction` model (auto-created via
  SPORT_KEY_LEAGUE 21-key mapping, fallback SPORT_PREFIX_MAP, filters
  games >14 days out), `core/services/betting_outcome_verifier.py:BettingOutcomeVerifier.settle_wagers()`,
  `SportsOddsAnalyst` agent.
- **Anchor:** S1273 §3.10 (primary).
- **Known drift:** LLM-scored confidence quality unaudited; MLPrediction
  auto-create heuristics (`SPORT_KEY_LEAGUE` vs `SPORT_PREFIX_MAP`
  fallback) mostly opaque.

### C — Wager Persistence + User Actions

- **Systems:** `core/models_betting.py:PlacedWager` (line 13 — stake,
  American odds, potential_payout, status
  pending/won/lost/push/cancelled; `calculate_payout()`, `settle(won,
  push)`), `PlacedWagerLeg` (line 108 — parlay legs, market_type
  h2h/spreads/totals/props/futures), `SportsBettingCoordinator` service,
  `POST /api/odds-sports/kelly-criterion/`,
  `GET /api/odds-sports/ai-track-record/` (S1012 dedup).
- **Anchor:** S1273 §3.10 (primary).
- **Known drift:** PlacedWager settlement could be async but currently
  synchronous (S1273 §3.10 debt bullet).

### D — User-Facing Surfaces (no dedicated S1273 §3 row)

- **Systems:** `frontend/src/pages/BettingPage.tsx` → `/betting` 9-tab
  dashboard (S1273 §3.18 documented tab count; PLATFORM_INVENTORY
  autoblock cites "9 betting tabs" — cross-check for drift in P1 or
  P2); Discord commands `/predictions`, `/odds`, `/arb`, `/bankroll`,
  `/bet` inside `core/services/discord_bot.py`; REST layer
  `/api/odds-sports/*` (5 endpoints); `core/views_odds_sports.py`
  (`convert_odds`, `calculate_expected_value`, `get_todays_games`).
- **Anchor:** none in S1273 §3.10 directly. Scattered across §3.18
  (frontend), §3.20 (Discord), §3.22 (API). No unified "sports surfaces"
  row.
- **Known drift:** BettingPage tab-count claim in PLATFORM_INVENTORY
  autoblock vs `BettingPage.tsx` actual — spot-check needed (S1273 §3.18
  named). "9 betting tabs" language appears in autoblock but tab count
  drift is a known Frontend arc concern.
- **Gap:** this category has NO inventory row of its own. See §8 D1 for
  the open decision on whether P1 lands a §3.N row here or delegates to
  a Frontend arc.

### E — Cross-boundary Integration Edges (§12.3 DECISION POINT)

- **Systems:** the four edges flagged by S1274 §7.2 + §12.3:
  1. Sports→SignalCluster (`sports_odds` not in `SignalCluster.data_type`
     tracks; S1273 §3.9 signal engine.
  2. Sports→Content Pipeline / Initiative (predictions do NOT
     auto-create Initiatives or Deliverables — S1273 §3.10 debt).
  3. Sports→Revenue Pipeline (betting outcomes not fed to opportunity
     attribution — S1274 §7.2 row 6).
  4. Sports↔Content Deliberation (SportsContentContext exists per S1273
     §3.10 but wiring into ContentDeliberationRunner status UNKNOWN —
     child audit resolves).
  Plus one cross-cutting scoping question:
  5. Should cross-domain telemetry aggregation (5-layer execution
     telemetry per S1273 §5.13, §3.25) include sports?
- **Anchor:** S1274 §7.2 row 6 + §12.3.
- **Framing constraint (from §12.3 Rigby correction):** every edge in
  E is EVIDENCE ONLY under Group 1500. For each edge, the P2 audit
  cites present-or-missing state (file:line for missing claims to
  prove they are actually missing, not just under-searched). No
  posture recommendation.
- **§12.3 Deliverable input:** for Integration posture, what
  integrations MUST exist to count as "integrated"? What
  performance/cost/correctness bars must the composed system hit? What
  content types are enabled that don't exist today? These questions get
  their evidence base in P2; their formal criteria enumeration in the
  S1599 canonical summary.

### F — Island Operational Invariants (the flip side of E)

- **Systems:** the boundaries that MUST stay hard IF the downstream
  arc picks Island posture per §12.3:
  1. Independent Celery queue (currently mixed with default worker per
     `Procfile` / `Makefile` — invariant candidate).
  2. Independent agent pool (GamePredictor, ArbitrageDetector,
     SportsOddsAnalyst live in AGENT_MAP alongside all others — no
     isolation today).
  3. Independent PA tool surface (currently unified — no sports-only
     tool namespace).
  4. Independent scaling boundary + no cross-contamination invariant.
  5. Independent embedding cadence (if sports has its own knowledge
     store).
  6. Independent governance plane composition (§3.23) — likely
     BLOCKED by Symbol Mapping per S1274 §12.5. Audit documents
     blocked-status only.
- **Anchor:** no direct S1273 §3.10 row for isolation invariants;
  touches §3.24 (Celery), §3.2 (Agent System), §3.23 (Governance).
- **Framing constraint (from §12.3 Rigby correction):** same as E.
  Every invariant in F is EVIDENCE ONLY. For each invariant, cite
  present state; no recommendation.
- **§12.3 Deliverable input:** for Island posture, what boundaries MUST
  stay hard? What content/insight is EXPLICITLY out of scope? What
  operational invariants must the island preserve? Evidence base in
  P2; formal criteria enumeration in S1599.

### Explicit non-candidates

- **Odds provider API contracts / vendor selection.** Belongs to S1273
  §3.26 External Integrations. Out of Group 1500.
- **Sportsbook affiliate / referral revenue.** Belongs to Group 1400
  Revenue arc (running in parallel with Group 1500). Cross-linked via
  `delegates_to` frontmatter; P2 flags the edge but does not audit it.
- **Sports content generation quality itself.** Belongs to Group 1600
  Content arc. Reachable only IF a downstream design-preparation arc
  picks Integration posture. P2 flags the edge; content-side evidence
  is Group 1600's job.
- **Symbol-Mapping-blocked governance composition.** Per S1274 §12.5,
  Governance Plane Composition is BLOCKED by Symbol Mapping
  ADR/design. F6 documents blocked-status only; does not attempt
  composition analysis.
- **Combat sports / non-traditional-sports adjacent spiders.** Only
  TheOddsSpider is in Group 1500 P1 scope; CombatSportsSpider and
  peers are out of scope unless a child audit surfaces a shared
  boundary concern.

---

## 4. Parent-vs-single recommendation

**Recommendation: parent-with-children.**

Evidence for parent-with-children:

1. **Two clearly separable evidence lines.** Categories A+B+C+D form
   the WORKING subsystem baseline (what exists today, well-inventoried
   in S1273 §3.10 but with no dedicated doc). Categories E+F form the
   §12.3 decision-point evidence base. Merging them into a single audit
   would either sacrifice fidelity to §3.10 (the subsystem baseline) or
   fidelity to §12.3's two-posture framing.
2. **Category D has no §3 inventory row.** A child audit is the right
   vehicle to either land the row or delegate cleanly to a Frontend
   arc. Buried inside a single audit, the row-landing question gets
   lost.
3. **§12.3 explicit deliverable requires an artifact that
   consolidates cross-category evidence.** The two-posture success-
   criteria matrix per §12.3 is a canonical-summary deliverable, not a
   subsystem-audit deliverable. That triggers the xx99 slot per
   playbook §10.
4. **S1273 §3.10 explicitly flags "No dedicated sports intelligence
   doc" as a gap.** Filling that gap is a distinct deliverable from
   answering §12.3. A single audit that tries to do both will either
   under-invest in the baseline (weakening the §3.N anchor) or under-
   invest in the decision-point evidence (weakening the arc's §12.3
   contribution).
5. **Playbook §2 rule 3 explicitly permits sub-grouping** when a
   domain is bigger than the row suggests.

Evidence for single-audit (weaker):

1. Sports/DBAO is documented as **self-contained** (S1274 §9.5
   MEDIUM extraction readiness). A single audit could reasonably cover
   the WORKING core.
2. Category E "missing edges" analysis without a companion Category F
   "island invariants" analysis is coherent by itself if the arc
   presumes an integration verdict.

The Rigby-corrected §12.3 framing invalidates argument (2) — we
CANNOT presume an integration verdict. Argument (1) is real but only
covers 4 of the 6 categories. Verdict stands.

**Verdict: parent-with-children.**

---

## 5. Child mission sequence (proposed — Chris ratification pending)

Group 1500 is scoped to a **compact 4-session arc**:
parent + 2 audit children + canonical summary. Rationale: Group
1300 Memory needed 5 audit children because Memory decomposed into 5
distinct semantic categories with independent evidence lines. Sports
decomposes cleanly into 2 lines (subsystem baseline vs decision-point
evidence). Right-sizing the arc respects playbook §17 graduation
discipline and avoids the "runaway parent-with-children" anti-pattern.

| Slot | Session ID | Child audit | Priority rationale |
|------|-----------|-------------|-------------------|
| P0 | S1500 | **Parent** — this doc (Phase 0 taxonomy + arc plan) | Foundation |
| P1 | S1501 | **Sports/DBAO Subsystem Baseline Audit** (Categories A + B + C + D) | Fills the "no dedicated sports intelligence doc" gap flagged in S1273 §3.10. Lands the load-bearing subsystem picture: what odds ingestion / prediction / settlement / user-facing surfaces exist, with what durability + confidence + telemetry contracts. Playbook §11.2 20-section audit. Includes new §N sections landing Category D missing inventory row (or delegating). |
| P2 | S1502 | **Sports/DBAO Boundary Evidence Audit** (Categories E + F) | Per §12.3 Rigby correction, this is EVIDENCE ONLY. For each edge in E (Sports→Signal / Content / Revenue / Deliberation + cross-domain telemetry aggregation scope): cite present-or-missing state with file:line — proving MISSING claims rather than assuming them. For each invariant in F (independent queue / agent pool / PA tool surface / scaling / embedding cadence / governance): cite present state. Explicitly no posture recommendation. Playbook §11.2 20-section audit. |
| P3 | **S1599** | **Group 1500 Canonical Summary** (playbook §11.3) | Cross-cutting synthesis of P1+P2 findings; consolidated sports subsystem shape; **two-posture success criteria matrix** per §12.3 explicit deliverable (Integration posture criteria in one table, Island posture criteria in another, side-by-side with operational cost estimates and failure modes for each); follow-on queue explicitly naming the downstream design-preparation arc as the next phase; anchor-update recommendations for `PLATFORM_INVENTORY.md` §3.10 (subsystem doc gap filled) + §3.18/§3.20/§3.22 (Category D row-landing outcome). §10 meta-methodology retrofit per S1399 close directive (memory rule `feedback_xx99_meta_methodology_section.md`). |
| Delegated | — | **Sportsbook affiliate / referral revenue attribution** | Delegated to Group 1400 Revenue arc (parallel Claude Code session at S1500 open). Cross-linked via `delegates_to` frontmatter. P2 flags the edge; no attribution audit. |
| Delegated | — | **Sports content generation quality** | Delegated to Group 1600 Content arc. Reachable IF downstream design-prep arc picks Integration posture. Cross-linked via `delegates_to` frontmatter. |

**Arc rhythm.** Group 1500 spans **S1500 → S1502 + S1599** = four
sessions total (one parent + 2 child audits + 1 canonical summary).
This matches the "compact arc" shape and is deliberately more
efficient than Group 1300's 7-session arc — Sports has a smaller
decomposition surface.

**S1599 canonical summary rationale.** Chris directive at S1399 close
(memory rule `feedback_xx99_meta_methodology_section.md`, 2026-07-01):
every xx99 canonical summary includes §10 "What This Research Taught
Us About How to Do Research" per playbook §11.3 v3. S1599 inherits
this requirement — five subsections per the memory rule. S1599 is
bounded work: consumes P1+P2 outputs, produces the §12.3 two-posture
success-criteria matrix + anchor-update recommendations + follow-on
queue naming the downstream design-preparation arc. It does NOT
re-open scope, does NOT recommend a posture, does NOT run parallel
Explore sweeps (per playbook §13 note: sweeps are for audit children,
not canonical summaries).

---

## 6. Parked candidate issues (for future child audits)

Placed here to prevent Phase 0 from re-scoping downstream, and to seed
P1/P2 input without prescribing findings.

### 6.1 GameLineHistory dead-storage question (P1 Category A input)

**Evidence.** S1273 §3.10 technical debt bullet:
*"GameLineHistory tracked but not actively queried in any service."*

**Audit question for P1.** Is `GameLineHistory`
(`core/models_odds_history.py:82`) truly orphan (no queryset consumer
in any service, view, task, or agent)? Or is it consumed by
SharpActionDetector for odds divergence detection but the S1273 note
was incomplete? Per memory rule
`feedback_verify_before_deleting_dead_code.md`, this is a CANDIDATE
finding — the P1 audit must run owner-model-qualified consumer
enumeration before declaring the field orphan.

### 6.2 MLPrediction auto-create heuristic opacity (P1 Category B input)

**Evidence.** S1273 §3.10:
*"S1010: auto-created via SPORT_KEY_LEAGUE mapping (21 keys), fallback
SPORT_PREFIX_MAP; filters >14 days out; S1012 dedup by Max('id') per
game_id."*

**Audit question for P1.** What guarantees MLPrediction row quality?
What happens when SPORT_KEY_LEAGUE misses (fallback SPORT_PREFIX_MAP —
under what conditions does that fire and what confidence is assigned)?
What is the observed distribution of `MLPrediction.confidence` per
sport_key, and what does that imply about prediction utility?

### 6.3 SportsContentContext wiring status (P2 Category E input)

**Evidence.** S1273 §3.10 lists `SportsContentContext` as a service but
does not specify what consumes it. S1274 §12.3 lists
"betting-related deliberation surface design" as UNBLOCKS work — implying
the current wiring is either non-existent or unclear.

**Audit question for P2.** Grep every callsite of
`SportsContentContext`. Which ones are consumers (feed to
ContentDeliberationRunner or ClaimsPackBuilder)? Which ones are dead?
This is the first evidence step for the Sports↔Content Deliberation
edge — cannot presume MISSING without a proper enumeration.

### 6.4 BettingPage.tsx tab count drift (P1 Category D input)

**Evidence.** S1273 §3.18 notes 9-tab betting dashboard; PLATFORM_INVENTORY
autoblock cites the same count. S1273 §3.18 also flags this as a known
tab-count drift concern in the frontend.

**Audit question for P1.** Verify the current tab count in
`frontend/src/pages/BettingPage.tsx` matches the inventory autoblock's
claim. If drift found, propose the anchor-update recommendation
(single file:line count vs autoblock claim + regeneration path).

### 6.5 Discord sports command inventory (P1 Category D input)

**Evidence.** S1273 §3.20 catalogues 96 Discord commands in
`core/services/discord_bot.py` (11,676 lines) but only names 5 sports
commands (`/predictions`, `/odds`, `/arb`, `/bankroll`, `/bet`). It is
unclear whether that list is exhaustive.

**Audit question for P1.** Enumerate every Cog + command inside
`discord_bot.py` that is sports-adjacent. Is the S1273 list correct?
Are there sports-adjacent commands scoped to non-sports Cogs?

---

## 7. Anti-scope for Research Group 1500

Explicitly out of scope for the entire Group 1500 (even under
parent-with-children):

- **Posture selection.** Group 1500 is pure research + evidence. Per
  playbook §3 phase discipline, the two-posture success-criteria
  matrix is a research-authority deliverable (canonical summary).
  Choosing Integration vs Island is downstream — a separate
  design-preparation arc consumes S1599's criteria and recommends;
  Chris ratifies via ADR.
- **Odds provider API contracts / vendor evaluation.** S1273 §3.26
  External Integrations territory.
- **Sportsbook affiliate / referral revenue attribution.** Group 1400
  Revenue arc territory. Cross-linked via `delegates_to`. P2 flags the
  edge; no attribution audit.
- **Sports content generation quality.** Group 1600 Content arc
  territory. Cross-linked via `delegates_to`. Reachable only if a
  downstream arc picks Integration posture.
- **Symbol-Mapping-blocked governance composition.** F6 documents
  blocked-status only; does not attempt composition analysis. Per
  S1274 §12.5.
- **Implementation PRs.** Everything Group 1500 produces is design
  research. No `sports/` or `core/models_betting.py` diffs.
- **New MLPrediction / PlacedWager model proposals.** Requires
  separate PR after audit lands, gated by `EMPLOYEE_OS_PRIMITIVES.md`
  anti-duplication matrix.
- **Combat sports / non-traditional-sports adjacent spiders.** Only
  TheOddsSpider is in P1 scope.

---

## 8. Decisions recorded + open decisions

### 8.1 Decisions recorded (Chris ratification pending — proposed defaults below)

| # | Decision | Proposed verdict | Rationale |
|---|----------|------------------|-----------|
| 1 | Parent-vs-single | **A. Parent-with-children** | §4 evidence + §12.3 requires two-artifact structure (subsystem baseline + boundary evidence + canonical-summary criteria matrix). |
| 2 | Framing constraint | **Adopt Rigby §12.3 correction** — no posture presumption. Every child audit is evidence-only. | Preserves Rigby SIGN v2 fold; prevents research-for-its-own-sake per OS §1.5. |
| 3 | Arc rhythm | **4 sessions (S1500 parent + S1501 P1 + S1502 P2 + S1599 summary)** | Right-sized decomposition. Sports has fewer independent semantic axes than Memory (Group 1300 = 7 sessions). |
| 4 | Delegation — Revenue attribution | **Delegate to Group 1400 Revenue** (parallel arc) | Business scope belongs to Revenue's territory; parallel arc naturally consumes it. |
| 5 | Delegation — Content quality | **Delegate to Group 1600 Content** | Content quality is downstream and reachable only IF integration posture selected. |

### 8.2 Open decisions gating child launches (Chris resolves)

- **D1** — **Category D user-facing surfaces routing.** Fold Category D
  into P1 subsystem audit (default lean — one child audit lands the
  §3.N row as a new section), OR spin D off as its own child (P1.5 —
  adds a session but keeps subsystem-baseline audit tighter), OR
  delegate D fully to a Frontend arc (does not exist yet; would defer
  category D indefinitely).
  - **Default lean:** fold into P1 with dedicated §N for row-landing.
- **D2** — **F6 blocked-status handling.** Category F6 governance-plane
  composition is BLOCKED per S1274 §12.5 (Symbol Mapping unbuilt).
  Include as "documented as blocked" evidence in P2 (default lean), OR
  drop from Group 1500 scope entirely, OR spin off into a
  Symbol-Mapping-dependent arc.
  - **Default lean:** document as blocked evidence in P2.
- **D3** — **S1599 posture-criteria enumeration scope.** Per §12.3
  explicit deliverable, the criteria matrix is a research-authority
  deliverable (playbook §3, §6 metadata table). Enumerate criteria in
  S1599 without recommending posture (default lean — preserves phase
  discipline), OR skip criteria enumeration in S1599 and defer entirely
  to the downstream design-prep arc, OR blur the phase boundary and
  recommend posture in S1599 (VIOLATES playbook §3 rule 5).
  - **Default lean:** enumerate criteria; NO posture recommendation.
- **D4** — **Group 1500 arc pin.** New pin required for Group 1500.
  Propose short title "Session 1500 — Sports research group
  (kickoff)". Coordination note: the parallel Group 1400 Claude has
  already minted `pa-34d43795e1b24bd3` and rotated
  `tools/pa_local.sh` line 128 to that pin. Group 1500 must NOT
  overwrite the wrapper — use `pa_chat.py --conversation <group-1500-pin>`
  directly for all Group 1500 sessions.
- **D5** — **Rigby SIGN routing for this parent doc.** Playbook §15
  parent-scoping row calls for light SIGN. Route ONLY the child
  mission sequence + parent-vs-single verdict + anti-scope to Rigby on
  a fresh isolation pin. Do NOT ask Rigby to redesign the taxonomy.

---

## 9. Next step

After Chris ratifies (or amends) decisions §8.1 + resolves open
decisions §8.2, this doc's `status` frontmatter field flips from
`draft` to `active`. The child mission sequence table §5 is committed
as the arc plan.

The immediate next step is:

1. Route this parent doc to Rigby for light SIGN per playbook §15 on
   a fresh isolation pin (D5).
2. Fold Rigby's edits (if any) into `draft`.
3. Chris commit-gates the parent doc PR.
4. Update `docs/research/OPEN_ARCS.md` (move Group 1500 from Not
   started → In-progress; add 2026-07-01 S1500 open reconciliation
   note); coordinate with Group 1400 Claude on the same file since
   both arcs will be writing to it in short succession.
5. Update `00-START-NEXT-SESSION.md` to point at S1501 as the next
   Group 1500 session; coordinate with Group 1400 Claude.
6. Add ARCHITECTURE_INDEX row for Group 1500 (bump v18 → v19); the
   version bump policy per playbook §16 is same-commit as the parent
   PR merge.
7. Mint Group 1500 arc pin (D4) — do NOT rotate `tools/pa_local.sh`;
   use `--conversation` directly.

After Chris commit-gates + merges the parent PR:

8. S1501 opens per playbook §11.2 20-section audit template + §13
   6-parallel-Explore sweep.

---

## 10. Frontmatter provenance note

Per playbook §6 required-fields table, this doc carries all required
`parent-doc` fields: `title`, `status`, `authority`, `session_added`,
`research_group`, `child_slot: P0`, `domain_slug: sports`, `date`,
`last_verified`, `supersedes`, `related`, `companion_anchors`,
`dependencies_on` (empty — Group 1500 is independent), `delegates_to`
(Group 1400 Revenue + Group 1600 Content), `delegated_from` (empty),
`verifier_loop`, `owner`.

Per playbook §7 cross-reference policy, every count claim cites the
inventory autoblock (`PLATFORM_INVENTORY.md`) or the primary S1273 §3
row. Every code claim cites `path:line` or explicit UNKNOWN. No
duplicated content — all references, no restatement. Companion anchors
declared for load-bearing dependencies. Related links declared for
peer connections in the arc + immediate cross-arc predecessors.
