# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2953 CLOSED. Agent Capability Drift Scanner SHIPPED (PR #3547, HEAD `5b5e4a283`) as ratified S2953 first-slice. Single-codepath per Rigby SIGN spec: (a) `python manage.py scan_agent_capability_drift` mgmt cmd, (b) 9-test Django wrapper, (c) Rigby-callable `agent_capability_drift_tool` (actions: scan/summary). Three invariants: AGENT_MAP↔Agent DB row, user-callable exposure completeness (enum+mapping+dispatcher), recent-execution evidence for `supported` tier (default 30d). Exception allowlist `capabilities_exceptions.yaml` at repo root with tier semantics (`supported`/`internal-only`/`legacy`/`rerouted`/`experimental`) + TTL. Live-verified post-merge via Rigby: 83 AGENT_MAP / 92 Agent DB / 59 enum / 1 exception loaded → 77 active findings, 2 suppressed (CodeGeneratorAgent seed). This terminal session shipped **3 PRs** total (#3545 pre-A1 fixes + #3546 S2952 close + #3547 drift scanner) and executed **2 full close cascades**. **S2954 first-action = open Golden Evals arc** — Rigby zoom-out Q4 elevated this as the third capability-substrate leg before A1 Phase 1 code opens.

**Refreshed 2026-07-25 (S2953 close).** Gap-map headline: `100 validated_full / 0 untested` (unchanged — capability substrate work, not PA-tools sweep).

**PRs shipped this session (in-terminal, both S2952 close-out + S2953 open+close):**
- u-d-b PR **#3545** — S2952 pre-A1 capability triage: brainstorm honesty + MarketIntel routing + agent_job_status pending UX (3 files, +129/-8).
- u-d-b PR **#3546** — S2952 close cascade — handoff + 00-START refresh + wrapper pin bump (3 files, +163/-56).
- u-d-b PR **#3547** — S2953 agent capability drift scanner (8 files, +927/-3, 9 new regression tests).

**Twin mirrors shipped this session (six total):**
- S2952 fixes content mirror: `24b5e6c1-f6d6-4b11-b470-117f3a14182a`
- S2952 fixes ratification envelope: `e625e0f5-a3a8-4f7d-9cdf-1484b802f679`
- S2953 plan-pivot content mirror: `7d795c28-c053-492f-ad05-00b27d335c82`
- S2953 plan-pivot ratification envelope: `cf20e3e4-b45e-40e2-b551-c7def5db7056`
- S2953 drift scanner ship content mirror: `65b5552b-a449-43d2-bb5e-55a7487a094d`
- S2953 drift scanner ship ratification envelope: `bd206890-8e52-4337-a4c3-9ad02a2a9bcb`

**Files shipped this session (S2953 slice):**
- **NEW** `core/services/agent_capability_drift.py` — shared audit service (3 invariants + classifier).
- **NEW** `capabilities_exceptions.yaml` — YAML allowlist at repo root.
- **NEW** `core/management/commands/scan_agent_capability_drift.py` — CLI wrapper.
- **NEW** `core/tests/test_agent_capability_drift.py` — 9 tests (all green).
- **MODIFIED** `core/services/pa_tool_schemas.py` — `agent_capability_drift_tool` schema.
- **MODIFIED** `core/services/tool_dispatcher.py` — handler registration (162→163).
- **MODIFIED** `core/services/td_handlers_agents.py` — `_handle_agent_capability_drift` method.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- Recycled after PR #3547 merge (`make celery-recycle`).
- Rigby `agent_capability_drift_tool` returned: 83 AGENT_MAP / 92 DB / 59 enum / 1 exception → 77 active findings, 2 suppressed. `has_active_failures: false, has_active_warnings: true` — soft-warn posture verified.

**Governance:** plan pivot ratified `yes+A`; Drift Scanner ship ratified "Path A". Golden Evals arc opens at S2954 first-action (Chris ratified option a: 'after Scanner + before Phase 1').

**Rigby Tool Gap Ledger:**
- **NEW** — Router-level rerouting has no queryable structure; blocks drift scanner invariant 4 ("rerouted must be labeled"). Design task.
- **NEW** — Capability Manifest not yet built; Rigby's field spec captured in this doc under "Capability Manifest — build spec". Parallel-track deliverable during A1 Phase 1.
- **RE-HIT (6th time this terminal session)** — `deliverable_tool.create` diagnostic-flag bug on `initiative_phase_doc` (S2909 Ledger #16). All content mirrors ORM-cleared this session.

Full session context: `docs/handoffs/SESSION_2953_DRIFT_SCANNER.md`.

---

## S2954 open sequence

**S2954 first-action = open Golden Evals arc** (Rigby zoom-out Q4 elevate, Chris ratified `yes+A`).

### Universal open sequence

1. **Live-verify S2953 drift scanner still healthy:**
   - `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect same totals shape (83/92/59/1 → 77+2). Numbers drift as agents run/get added; only the SHAPE matters.
   - `python manage.py scan_agent_capability_drift --json | jq .totals` — same numbers from CLI path.
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 0 untested`.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2954 pin (retired at S2953 close cascade).
4. **Open Golden Evals arc** — see arc-open scope below.

### Golden Evals arc — S2954 open scope

**Motivation (Rigby zoom-out Q4):** *"the product you're actually selling is auditable reliability, which ultimately requires scenario-based evidence, not only structural mapping."* Drift Scanner tells you agents exist + are exposed + have executed. It does NOT tell you they work on real customer inputs. Golden Evals closes that gap.

**Arc structure (estimated 3-5 sessions minimum):**

1. **S2954 — Tier-1 agent list ratification** — Chris + Rigby define the smallest set of agents whose reliability we'd stake a paying customer engagement on. Candidates from execution-history: SportsOddsAnalyst (408 exec), ArbitrageDetector (379), PredictionMarketAnalyst (376), Rigby (285), ResearchAgent (159), COOAgent (67), etc. But Tier-1 for A1 Reliability Audit wedge may differ from usage volume — target buyer is Platform/ML/SRE + Security/compliance, which suggests: Rigby (dogfooding proof), ResearchAgent, ContentWriterAgent, TrendAnalysisAgent, MarketIntelligenceAgent, ThinkingAgent. Ratify at S2954 open.
2. **S2955+ — Canonical prompt authoring** — 5-20 prompts per Tier-1 agent covering happy path + typical failure modes (data unavailable, tool timeout, bad input, ambiguous request). Store as YAML at `evals/tier1/<agent>.yaml`.
3. **S2956+ — Expected output validators** — JSON Schema or Pydantic model per prompt. Accept/reject criteria explicit.
4. **S2957 — Regression harness** — `python manage.py run_golden_evals` runs the suite on demand; nightly beat task runs it on schedule; results stored in a `GoldenEvalRun` table with pass/fail + drift-over-time.
5. **After arc close — A1 Phase 1 first-slice** opens with Capability Manifest parallel-track.

### Capability Manifest — build spec (parallel-track from A1 Phase 1 start)

Substrate: single canonical JSON "capabilities index" that renders to (a) internal operator UI, (b) customer-facing audit report sections, (c) CI policy inputs. NOT a doc-per-agent — one JSON, multiple views.

**Fields per agent** (Rigby SIGN-refined):
- description
- tools called
- data dependencies (DB tables, spider sources, external APIs)
- typical latency
- last-30d success rate
- output-shape sample
- **invocation contract** — required inputs (what happens if omitted) + optional inputs + happy-path example call
- **evidence pointers** — last_success_at, last_failure_at + top failure signatures, sanitized sample outputs with execution IDs
- **cost + budget posture** — p50/p95 tokens; workspace freeze/downgrade behavior + fallback model
- **reliability tier + support status** — `supported` / `legacy` / `rerouted` / `experimental`; SLO target
- **safety / data-handling class** — data sensitivity, outbound network usage, mutation capability
- **Key distinction across ALL agents:** "exists in code" vs "callable by users" vs "has recent evidence of working"

### A1 Phase 1 still ahead (after Golden Evals arc closes)

Chris's 4 open questions from scoping deliverable `7870eca9` still gate opening Phase 1 code:

1. **Minimum evidence standard** we promise? (run IDs + failure signature samples vs metrics only)
2. **Default turnaround SLA** we can consistently hit without heroics?
3. Sell as **agent-system audit** (end-to-end) or **toolchain reliability audit** (tools/contracts) first?
4. **Legal posture** for handling customer logs (retention window, deletion guarantee, allowed data types)?

### Deferred queue (updated at S2953 close)

**S2953 additions:**
- **Drift scanner invariant 4 (rerouted-must-be-labeled)** — requires `AgentRerouteEntry`-style queryable model. Small design task.
- **Curate `capabilities_exceptions.yaml`** — 77 active findings at HEAD `5b5e4a283`. Walk through each; either tier-classify or fix (add missing enum entry / exercise the agent). Good candidate for parallel work during Golden Evals arc authoring.
- **Fix run_agent dispatch-response agent-name echo** — dispatch response echoes the resolved agent name; ensure it always echoes the mapping-canonical CamelCase, not the input string. Minor cleanup, from S2952 handoff.

**S2952 carry-forward:**
- Schema/handler drift scanner (Rigby zoom-out elevate — separate from S2953's agent-drift scanner; this one is for PA tool schema↔handler contract).
- `agent_job_status` design gap harder fix (reserve `AgentExecution` row synchronously at dispatch).

**Signal-dispatch queue (from S2951 close, carry forward):**
- **(A11)** 6th signal-dispatch rule (`sentiment_shift` or `market_movement`) — no volume evidence gathered yet.
- **(NEW-6)** Fair-share round-robin scanning in `scan_and_dispatch()` — flagged as `future_trigger` (2 sessions).
- **(NEW-7)** Persist `per_rule_diagnostics` per `scan_run_id`.
- **(NEW-8)** Per-pattern effectiveness attribution for reused agents.

**Long-standing (from S2951 close, carry forward):**
- **(D)** Docs restructuring arc — Chris-ratified, still queued.
- **(B)** Slice 5-hardening — 3-4 executable invariants deferred at S2928.
- **(E)** Tier 2 lint promotion — envelope-JSON top-level-key parse.
- **(H)** generate_newsletter dry_run default flip.
- **(I)** bulk_archive statuses autofill robustness — 2nd trigger at S2945.
- **Envelope enhancement** (record-only S2942) — `verify_hint` + `would_write_count` for dry_run.
- **Close-ceremony ledger-flip checklist** (meta-fix, record-only S2942).
- **Deliverable v1 template retrofit** (record-only S2943).

---

## What's forbidden at S2954 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2953 new forbidden entries:** none.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2953 additions to the deferred queue:**
- Drift scanner invariant 4 (rerouted-must-be-labeled) — see above.
- `capabilities_exceptions.yaml` curation — see above.

**S2952 additions (carry forward):**
- Schema/handler drift scanner (PA tool contract) — separate from S2953's agent-drift scanner.
- `agent_job_status` design gap harder fix.
- Dispatch-response agent-name echo cleanup.

**S2951 additions (carry forward):**
- `MarketIntelligenceCoordinator` rename — cosmetic only after S2952 routing fix.
- `brainstorm_tool.create` real panel implementation.
- CompetitorAnalysisAgent spider sources (LangSmith/Langfuse/Helicone/Arize).

**Long-standing (carry forward from S2951):**
- Fair-share round-robin scanning.
- Persist per_rule_diagnostics in audit table.
- Advanced paste-UUID fallback for cluster picker.
- Server-side search + pagination on `/eligible/`.
- Z1/Z2/Z4 signal-dispatch UI polish (Rigby S2947 zoom-outs).
- Rank + cap + paginate follow-ups (Rigby S2946).
- Per-pattern-type diversity floors.
- Ledger candidates (S2945/2944/2943/2942 backlog).
- Docs restructuring arc (Chris-ratified S2800).
- W2 #1 / #2b / #2c pending Chris re-slate.
- LLMCallLog field splits.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953 Drift Scanner) are adjacent-domain net-new engineering, not sweep work.

**Total remaining sweep tools: 0.**

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses separate budget lane/cap; must NOT consume A1 shipping spend.
2. **Evidence tag:** All A4 artifacts labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up constrained to fixed timebox + fixed send count (3-5 total intros).
6. **No bespoke follow-ups.**

---

## For fuller context (S2846 → S2953)

See:
- **S2953 handoff (current):** `docs/handoffs/SESSION_2953_DRIFT_SCANNER.md`
- **S2953 shipped code:**
  - `core/services/agent_capability_drift.py` — scanner service
  - `capabilities_exceptions.yaml` — allowlist
  - `core/management/commands/scan_agent_capability_drift.py` — CLI
  - `core/services/pa_tool_schemas.py` — `agent_capability_drift_tool` schema (end of PA_TOOL_SCHEMAS)
  - `core/services/td_handlers_agents.py:6713-6764` — `_handle_agent_capability_drift`
  - `core/services/tool_dispatcher.py:406-408` — handler registration
  - `core/tests/test_agent_capability_drift.py` — 9 tests
- **S2952 handoff:** `docs/handoffs/SESSION_2952_PRE_A1_CAPABILITY_FIXES.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
