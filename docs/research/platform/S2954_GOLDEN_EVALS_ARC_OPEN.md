# S2954 — Golden Evals arc open (Tier-1 ratified + Day-1 fault-injection scope)

**Session:** 2954
**Ratified:** 2026-07-25 (Chris `yes` via Chat UI after joint Claude+Rigby recommendation)
**Arc parent:** Golden Evals (third capability-substrate leg — sits between S2953 Agent Capability Drift Scanner and A1 Reliability Audit Phase 1 code)
**HEAD at open:** `ee3bcf4c9`

---

## 1. Motivation

S2953's Agent Capability Drift Scanner establishes that agents **exist in code**, are **exposed via `run_agent` enum + mapping + dispatcher**, and have **recent execution evidence**. What it does NOT establish is that agents actually **work on real customer inputs under real conditions**.

The A1 Reliability Audit wedge sells "auditable reliability" to Platform/ML/SRE + Security/compliance buyers. Those buyers judge correctness under evidence + failure, not completion under sunny-day inputs. Golden Evals closes the gap the Drift Scanner leaves open.

Framed by Rigby's S2953 zoom-out Q4: *"the product you're actually selling is auditable reliability, which ultimately requires scenario-based evidence, not only structural mapping."*

## 2. Tier-1 agent list (RATIFIED)

Chris ratified via Chat UI 2026-07-25 after joint Claude+Rigby agreement. 8 agents — the smallest set whose reliability we'd stake a paying customer engagement on.

| # | Agent | Why included | What proves reliable |
|---|-------|--------------|----------------------|
| 1 | `SystemIntelligenceAgent` | Platform-truth queries (health/ops status); has meaningful 30d volume with decent completion | Always tool-grounded (no guessing); stable output schema; graceful degradation when deps fail |
| 2 | `ResearchAgent` | Core to audits/investigations buyers pay for | Evidence-first outputs with citations; explicit uncertainty; correct behavior under empty/partial retrieval |
| 3 | `DevOpsAgent` | Maps directly to SRE workflows (diagnose, propose remediations, safe posture) | Dry-run-first, rollback-aware plans; validates assumptions against tools/logs; correct failure classification |
| 4 | `WorkflowOrchestrationAgent` | Customer confidence depends on end-to-end orchestration, not single-shot prose — the "agentic glue" | Multi-step runs complete with correct tool routing, retries/partial recovery, clear state transitions |
| 5 | `LegalDocDrafterAgent` | Compliance-adjacent deliverables are buyer-relevant and easy to evaluate against checklists | Template completeness (required clauses/defs); variable hygiene; jurisdiction placeholders; no missing terms |
| 6 | `ContentWriterAgent` | Buyers will request postmortems / runbooks / audit memos — needs consistent structured writing | Hits required sections; ties claims to tool outputs; rejects unsupported assertions |
| 7 | `CompetitorAnalysisAgent` | Due-diligence-style analysis; forces disciplined reasoning and sourcing | "No unsupported claims" enforcement + explicit evidence inventory (or "insufficient evidence") |
| 8 | `PersonalAssistant` (Rigby) | She IS the interface a buyer experiences; must be dependable in routing + refusals | Correct tool selection every time for system-truth queries; strong anti-hallucination and escalation behavior |

### Explicitly EXCLUDED despite top-4 30d volume

Per 30d `AgentExecution` count query at HEAD `ee3bcf4c9`:

| Agent | 30d exec | Reason for exclusion |
|-------|---------:|----------------------|
| `PredictionMarketAnalyst` | 342 | Sports/prediction-narrow for A1 Platform/SRE+compliance buyer; keep Tier-2 as "pipeline scale proof" |
| `SportsOddsAnalyst` | 332 | Same — sports-vertical, wrong buyer for this wedge |
| Agent `0cfe523f...` (ArbitrageDetector cluster) | 307 | Same — sports/betting narrow |
| `Rigby` (as agent-row `d924862f`) | 227 | Already in Tier-1 as `PersonalAssistant` — this row is her operator-interface lane, not a separately-sellable capability unit |

## 3. Arc-scope commitment: Day-1 fault injection (RATIFIED)

Rigby's SIGN cycle zoom-out flagged the "sunny-day-only theatre" failure mode: ship 40+ prompts and validators against happy-path inputs, get a green suite, and buyers still have no real confidence because the suite never tests what actually breaks in production.

**Ratified commitment:** each Tier-1 agent's golden eval suite covers, from S2955 first-authored prompts onward:

- (a) **Happy path** — canonical input, expected output shape.
- (b) **Tool timeout** — downstream dependency exceeds latency budget; agent must handle without crashing or fabricating.
- (c) **Data unavailable** — KB empty / spider stale / API 5xx; agent must respond with explicit uncertainty or refusal, not confident invention.
- (d) **Ambiguous input** — under-specified request; agent must ask a clarifying question or narrow the scope, not guess.
- (e) **Bad/malformed input** — schema-violating or nonsensical payload; agent must reject cleanly.

**Reliability contract required in every validator:** required output fields present; citation/evidence pointers present where the class demands it; uncertainty markers present when applicable; refusal behavior correct when applicable.

**Why Day-1 and not phase-2:** adding a 9th–15th Tier-1 later is cheap (same harness reused). Adding fault-injection retroactively to sunny-day validators is expensive (rewrite the acceptance criteria for every prompt). Doing it Day-1 is the cheaper path.

## 4. Arc structure (next slices — S2955+)

Per 00-START S2954 arc-open scope:

- **S2955+** — Canonical prompt authoring. 5–20 prompts per Tier-1 agent, covering the 5 categories above. Stored as YAML at `evals/tier1/<agent>.yaml`.
- **S2956+** — Expected-output validators. JSON Schema or Pydantic model per prompt. Accept/reject criteria explicit.
- **S2957** — Regression harness. `python manage.py run_golden_evals` runs the suite on demand; nightly beat task on schedule; results in a `GoldenEvalRun` table with pass/fail + drift-over-time.
- **After arc close** — A1 Phase 1 first-slice opens with Capability Manifest parallel-track.

Estimated 3–5 sessions minimum for the arc.

## 5. Rigby SIGN cycle

**Turn 1** — Rigby ran real tool queries (`orm_inspect_tool count_by AgentExecution`) to refresh 30d counts against HEAD `ee3bcf4c9` (superseded the S2953 snapshot counts in 00-START). `tool_runs` populated — grounded, not rubber-stamping.

**Turn 2** — Rigby delivered narrative Tier-1 proposal + zoom-out concern. **Verdict: WARN** (not F-BLOCKING) — the list is sound but the arc becomes theatre without Day-1 fault injection + reliability contract.

**Reconciliation:** Claude verified all 8 Tier-1 names resolve in `core/agent_router.py` AGENT_MAP (both `WorkflowAgent` and `WorkflowOrchestrationAgent` exist; Rigby correctly picked the orchestration variant as the "agentic glue"). Fault-injection commitment folded into arc scope as Day-1 requirement (not deferred), which addresses Rigby's WARN.

**Chris D-verdict:** `yes` (Chat UI, 2026-07-25). Ratifies Tier-1 list + Day-1 fault-injection scope.

## 6. Deferred / open

- **Chris's 4 A1 Phase 1 gating questions** (from scoping deliverable `7870eca9`) still open. Not blockers for the Golden Evals arc, but block Phase 1 code open after arc close:
  1. Minimum evidence standard we promise (run IDs + failure signatures vs metrics only)?
  2. Default turnaround SLA hittable without heroics?
  3. Sell as agent-system audit (end-to-end) or toolchain reliability audit (tools/contracts) first?
  4. Legal posture for customer logs (retention, deletion guarantee, allowed data types)?
- **Capability Manifest build spec** (00-START §Capability Manifest) — parallel-track deliverable during A1 Phase 1, not part of Golden Evals arc.
- **Tier-2 agent list** — sports-vertical agents (PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector) sit in Tier-2 as "pipeline scale proof"; not certified for A1 wedge but not written off either. Revisit when a sports-audience wedge opens.

## 7. Limitations

- Tier-1 count reasoning was volume+capability-class heuristic, not statistical. If a Tier-1 agent turns out to be nearly-unused at production time (LegalDocDrafter 30d = 0 today, DevOps = 11), we'll still hold it in the suite because coverage-class matters more than volume for the A1 buyer — but expect noisy pass-rate metrics for low-volume agents.
- Gap-map drift observed at session-open: 00-START asserted `100 validated_full / 0 untested`, actual is `100/2` (the 2 are `agent_capability_drift_tool` + `agent_job_status`, both S2953/S2952-shipped and untested-by-design at that time). Not S2954-introduced; correction folded into S2954 close.
- Rigby dropped the Chat-UI response relay after Chris ratified — she echoed his `yes` back to him but didn't route it back to me verbatim. Rigby Tool Gap Ledger candidate; logged at S2954 close.
