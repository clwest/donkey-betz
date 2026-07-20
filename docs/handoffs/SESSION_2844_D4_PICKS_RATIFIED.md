# Session 2844 — D4-A/B/C Picks Ratified · SignalCluster Semantic-Query Fix Shipped

**Session:** S2844 (opened 2026-07-20; closed same day)
**Prior session:** S2843 — D4 decomposition ratified with refinement (§12 of `S2841_PRESSURE_TEST_ADDENDUM.md`)
**Companion addendum entry:** §13 of `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`
**Git HEAD at open:** `3cc325135`
**Playbook version:** v0.8.0 (unchanged)
**Status:** ✅ RATIFIED (Chris D-verdicts inline in §3)

---

## 1. What S2844 opened on

Per `00-START-NEXT-SESSION.md` at S2843 close: S2844 opens on the three D4 picks against the ratified §12 architecture. D6 discovery moratorium in force.

Ratified D4 architecture (from §12):
- **D4-A** — Execution Wedge (pick ONE from A1/A2/A3/A4; A4 requires paired product per §12.3 refinement)
- **D4-B** — Ledger Bet Gate (YES / NO; default YES if wedge is A1 or A2)
- **D4-C** — Foundry Phase 2C Trigger (RUN / DEFER)

## 2. SIGN cycle

**Turn 1 — Claude preliminary D4-A pick:** A2 (CharacterOS to first paying customer). Rationale drew on §5 SA + CA + §6.7 OPP-7 evidence + three pressure-test concerns.

**Turn 2 — Rigby independent SIGN (task `545c23e0-7330-420f-a8b4-c84df72be08f`; conversation `pa-4a5f86ef64c24366`):** DISAGREE with A2; alternative A4+A1. Non-empty tool_runs verified (8+ real tool calls including kb_tool + deliverable_tool). Rigby surfaced decisive evidence Claude had missed:

- **Atlas parking rule against A2 as framed** — `docs/24_7_GLOBAL_AI_APP_ATLAS.md#48`: *"If a paying customer says 'I'd pay you $50/mo extra to have Rigby with a face,' **then** the Character OS merge unparks. Not before."*
- **A1 cost-attribution blocker quantified** — `docs/narratives/STRATEGY_247_GLOBAL_AI.md#24`: *"4 ✗ rows in COST_SURVIVAL_AUDIT… must be fixed before external SaaS launch… per-workspace cost attribution isn't done."* Makes D4-B = YES a hard prerequisite for A1, not a preference.
- **A3 activation gate explicit** — `docs/handoffs/SESSION_1499_REVENUE_CANONICAL_SUMMARY_ARC_CLOSE.md#21`.

**Turn 3 — Claude accepted evidence; joint recommendation A4+A1** with F-BLOCKING question to Chris: *"Do you have — or can you name in the next 2–4 weeks — one plausible A4 customer prospect who would sign a $10–100k engagement?"*

**Turn 4 — Chris pushback (reframe):** *"can you and Rigby use Donkey Betz help me get customers? With everything you guys have access to in Donkey Betz what can be done to help me?"* — flipped GTM from external assumption to testable platform capability.

**Turn 5 — Capability probe dispatched (task `a3c1399b-3d76-42cd-87c0-1196a2242ec7`):** Three-probe test against A4 / A1 / A2-narrow. Non-empty tool_runs verified (8+ tool calls: `spider_status_tool.search` × 6 + `intelligence_tool.signal_clusters` × 3).

**Turn 5 result — probe empty across all three wedges:**
- A4 spider search (techcrunch, venturebeat, hackernews): 0 rows
- A1 remoteok returned 10 rows but labor-market signal (hiring assistants), not buyer signal
- A2 SMB probe: 0 rows
- SignalCluster endpoint returned generic unrelated clusters (Christopher Nolan, Iran, Kalshi parlays, Ethereum) for all three probes regardless of query

**Turn 6 — Rigby's zoom-out identified the load-bearing question:** was the SignalCluster empty result (a) indexing gap, (b) entity-extraction gap, or (c) API-contract bug returning wrong slice? (c) is fastest to fix.

**Turn 7 — Chris D-verdicts:**
- D4-A = A4 (Governance Consulting #1) **paired with A1** (Rigby standalone SaaS) per §12.3 refinement rule
- D4-B = YES (Ledger Bet fold; per-workspace cost attribution folded into wedge weeks 1-2)
- D4-C = DEFER (Foundry Phase 2C)
- Run SignalCluster diagnostic in parallel with A4 scoping preparation

**Turn 8 — Diagnostic executed:** confirmed Rigby's option (c). `td_handlers_core.py:3457-3475` ignored every filter parameter and returned the N most recent clusters regardless of query. Schema at `pa_tool_schemas.py:3425` advertised `query` only for `search/legislation_*` actions — signal_clusters was silently no-op'd.

**Turn 9 — Fix shipped and same-session second bug caught:** Initial handler patch added `query / pattern_type / min_confidence / source / window_hours` filters + schema advertised the new params. First verification returned 0 rows across all six probe calls. Root cause: GPT-5.2 auto-injected `source="kb"` from the shared `search`-action schema default, and the handler's `source_breakdown__has_key='kb'` filter zeroed everything out (real sources are spider names — `kalshi`, `techcrunch`, `variety`, `adzuna` — never literal `"kb"`). Second patch guards the source filter against search-context enum values (`kb`, `spider`, `web`).

**Turn 10 — Fix verified via direct ORM probe:**
- `query='remote contract'` + `source='kb'` (ignored) → 8 real clusters returned including *"Contract, Remote skill demand"*
- `pattern_type='opportunity_window'` → 4 clusters
- `min_confidence=0.7` → 20 high-confidence clusters

## 3. Chris D-verdicts (verbatim)

> pair with A1, defer D4-C, run the diagnostic

> yes, D4-B YES and run the fix

## 4. Ratified D4 picks (final)

### D4-A: A4 + A1

**Primary wedge (A4):** Governance Consulting engagement #1
- Target customer: mid-size AI startups / enterprise AI ops teams
- Motion: consulting engagement
- Price: $10–100k per engagement
- Time-to-revenue: 4–8 weeks

**Paired compounding product (A1) per §12.3 rule:** Rigby standalone SaaS
- Target customer: solopreneurs
- Motion: subscription SaaS
- Price: $30/mo
- Time-to-revenue: 6–10 weeks (extended by Ledger Bet fold)

**Sequencing note:** §12.4 explicitly defers execution sequencing between A4 and A1 (concurrent / sequential / gated) to subsequent planning. It is NOT a D4-A commitment. Chris accepted the customer-acquisition capability gap on A4 with the plan to work leadgen substrate alongside first-engagement scoping.

### D4-B: YES

Ledger Bet fold activated. Per Rigby's cited blocker (`docs/narratives/STRATEGY_247_GLOBAL_AI.md#24`), A1 external SaaS launch requires per-workspace cost attribution (`LLMCallLog.workspace` FK + per-workspace cost cap + OpsRun/OpsRunEvent/ToolCallRecord as public API + Ledger export). Ledger Bet becomes A1's weeks 1–2 substrate.

### D4-C: DEFER

Foundry Phase 2C does not directly accelerate A4 consulting engagements within the same month. Re-gated at next natural trigger (first revenue event OR when A4 case study demands multi-tenant platform).

## 5. Same-session code shipped

**Files modified:**
- `core/services/td_handlers_core.py` (signal_clusters handler at line 3456; added ~40 lines of filter logic + source-filter guard)
- `core/services/pa_tool_schemas.py` (intelligence_tool schema; extended `query` description + added `pattern_type` / `min_confidence` / `window_hours` params + updated signal_clusters action description)

**Filters added to signal_clusters action:**
- `query` — icontains match on `name` + `keywords` JSONField (multi-term OR)
- `pattern_type` — exact enum filter (10 valid values)
- `min_confidence` — `confidence__gte`
- `source` — spider name via `source_breakdown__has_key` (guards against search-context enums `kb`/`spider`/`web`)
- `window_hours` — `detected_at__gte = now - window_hours` (accepts either `window_hours` or `hours`)

**Response shape extended:** each cluster now includes `keywords` (first 5) + `source_breakdown` so callers can see WHY a cluster matched. Response also echoes `filters_applied` for transparency.

**Two same-session bug catches:**
1. Initial handler shipped without source-injection guard → caught by re-probe returning empty on non-empty underlying data
2. Root cause traced to GPT-5.2 schema-default auto-fill on shared `source` param → patched via enum-value guard

**Recycle:** `make recycle-all` run twice this session (once per patch) per PLAYBOOK-7.4.4.

## 6. Honest finding: SignalCluster data content is separate gap

The interface fix works. Underlying SignalCluster data does NOT contain AI-agent / governance / solopreneur / SMB relevant clusters. The 54 clusters in the last 168h are:
- Sports betting (Kalshi, TheOdds parlays)
- News (Iran, Trump, Nolan-film press)
- Job market (generic remote-work skill demand from Adzuna, WeWorkRemotely, RemoteOK)
- Tech miscellany (Kickstarter + ProductHunt topics, SpaceX)

The spiders feeding cluster aggregation don't include the AI-community sources (github, devto, hackernews-AI-tagged, medium-AI-tagged, producthunt-AI-tagged). Building the AI-source SIGNAL cluster pipeline is a separate 3–5 day project deferred until A4/A1 wedge execution needs it.

For A4+A1 leadgen today, the wired substrate is:
- Direct `spider_status_tool.search` on relevant spider data
- `kb_tool` for named prospect research
- `deliverable_tool` for outreach + engagement collateral drafting
- Chief-of-Staff Employee OS job for outreach workflow orchestration

## 7. What S2845 opens on

**Primary: A4 engagement #1 scoping** — prospect list, engagement structure, outreach mechanism, per-engagement pricing frameworks.

**Concurrent: A1 Ledger Bet weeks 1–2** — `LLMCallLog.workspace` FK + per-workspace cost cap + Ledger export scaffolding. Sequencing (concurrent vs staged) is a S2845-open planning decision.

**Forbidden at S2845 (D6 moratorium still in force):**
- No new strategic discovery arcs
- No portfolio expansion
- No new evaluation frameworks
- No reopening D4 architecture or picks
- No layer-boundary design arcs

## 8. Provenance

- **SIGN cycles:** two (D4-A pick SIGN task `545c23e0-7330-420f-a8b4-c84df72be08f`; capability probe task `a3c1399b-3d76-42cd-87c0-1196a2242ec7`; verification task `2b277e9d-16ef-432d-a5dd-a353be2813bb`)
- **Session pin:** `pa-4a5f86ef64c24366` (minted at S2844 open via atomic close from `pa-c31c6a2dd90d4307`; retired at S2844 close)
- **Git HEAD at open:** `3cc325135`
- **Playbook version:** v0.8.0 (no amendment)
- **Chris D-verdicts:** captured verbatim in §3
- **Workspace mirrors:** content mirror + ratification envelope to be Rigby-authored in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` per `feedback_rigby_writes_workspace_deliverables`

## 9. What this session did NOT do

- Did NOT reopen D4 architecture (§12 stays canonical; §13 records the picks)
- Did NOT introduce new evaluation dimensions (SA + CA remain the codified additions)
- Did NOT amend the Playbook (v0.8.0 unchanged)
- Did NOT expand the opportunity portfolio
- Did NOT build the AI-source SignalCluster pipeline (deferred until A4/A1 needs it)
- Did NOT scope the A4 engagement #1 (deferred to S2845)

---

*End of S2844 handoff. Ratified 2026-07-20 by Chris. Canonical companion to §12 (D4 architecture) + §13 (D4 picks) of `S2841_PRESSURE_TEST_ADDENDUM.md`.*
