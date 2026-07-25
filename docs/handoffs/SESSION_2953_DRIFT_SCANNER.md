# SESSION 2953 — Agent Capability Drift Scanner (Plan Pivot Ratified + First Slice Shipped)

**Date:** 2026-07-25
**Status:** CLOSED — PR #3547 merged, workers recycled, drift scanner live-verified via Rigby.
**HEAD at close:** `5b5e4a283`
**Merge commit:** squash `5b5e4a283` (PR #3547)
**Twin mirrors (this session):**
- **S2953 plan pivot** — Content mirror `7d795c28-c053-492f-ad05-00b27d335c82` (Donkey Betz workspace, `initiative_phase_doc`, diagnostic cleared via ORM — Ledger #16 re-hit 5th time); Ratification envelope `cf20e3e4-b45e-40e2-b551-c7def5db7056` (Architecture & Research workspace, `ratification_record`, `category='governance'`, diagnostic already null).
- **S2953 drift scanner ship** — Content mirror `65b5552b-a449-43d2-bb5e-55a7487a094d` (Donkey Betz workspace, `initiative_phase_doc`, diagnostic cleared via ORM — Ledger #16 re-hit 6th time this terminal session); Ratification envelope `bd206890-8e52-4337-a4c3-9ad02a2a9bcb` (Architecture & Research workspace, `ratification_record`, `category='governance'`, diagnostic already null).

---

## What shipped

**S2953** — Session opened as a mid-terminal continuation of S2952. Chris asked the fundamental capability question, honest evidence-based answer surfaced significant substrate gaps, Rigby SIGN + joint recommendation + Chris D-verdict pivoted S2953's first-action from A1 Phase 1 → Drift Scanner. Drift Scanner shipped as PR #3547 with the S2953 plan pivot 00-START refresh bundled in.

### Session shape

1. **Opened as S2952 close-out follow-up** — Chris asked *"Do we know exactly what Agents we have and exactly what they are capable of doing and exactly what Rigby is capable of having the Agents do?"*
2. **Honest evidence-based answer** (numbers ORM-verified live):
   - 83 in `AgentRouter.AGENT_MAP` / 92 Agent DB rows / 59 in `run_agent` enum
   - Only **31 agents with any execution evidence in last 7d** (later refined to 38 in last 30d)
   - **Zero machine-readable capability manifest**
   - **Zero coverage test** asserting AGENT_MAP ↔ enum ↔ mapping ↔ Agent row ↔ recent-execution invariants — exactly why S2952's MarketIntel silent-no-op wasn't caught
3. **Two-proposal recommendation to Chris:** Capability Manifest + Drift Scanner before opening A1 Phase 1 code.
4. **Chris ratified routing to Rigby SIGN.** Rigby returned AGREE on both with important field expansions AND elevated a THIRD leg I had underweighted: **scenario coverage / Golden Evals** — *"the product you're actually selling is auditable reliability, which ultimately requires scenario-based evidence, not only structural mapping."*
5. **Joint Claude+Rigby recommendation to Chris:** Drift Scanner FIRST (S2953, 1 session) → Golden Evals arc S2954+ (3-5 sessions min) → A1 Phase 1 with Manifest parallel. Chris ratified `yes+A` (Golden Evals opens after Scanner, before Phase 1).
6. **Drift Scanner implementation** — single-codepath (mgmt cmd + Django tests + Rigby audit tool) per Rigby's SIGN-refined spec. 9 tests green. Live-verify post-merge showed Rigby-callable surface returning correct totals (77 active findings, 2 suppressed).

## PRs shipped this session

- u-d-b PR **#3547** — S2953 agent capability drift scanner (8 files, +927/-3, 9 new tests green).

## Files shipped this session

- **NEW** `core/services/agent_capability_drift.py` — shared audit service; 3 invariants; findings always emitted + classifier routes exempt tiers to `suppressed_findings` for transparent audit reports.
- **NEW** `capabilities_exceptions.yaml` — YAML allowlist at repo root with tier + reason + optional TTL; seed entry for `CodeGeneratorAgent` (blocked since S1031).
- **NEW** `core/management/commands/scan_agent_capability_drift.py` — CLI wrapper (`--json`, `--fail-on-drift`, `--recent-window-days`).
- **NEW** `core/tests/test_agent_capability_drift.py` — 9 tests: scanner smoke, allowlist suppression behavior, YAML normalization, PA handler contract.
- **MODIFIED** `core/services/pa_tool_schemas.py` (+40) — new `agent_capability_drift_tool` schema (actions: scan/summary; optional recent_window_days + invariant filter).
- **MODIFIED** `core/services/tool_dispatcher.py` (+3) — register `agent_capability_drift_tool` handler.
- **MODIFIED** `core/services/td_handlers_agents.py` (+45) — `_handle_agent_capability_drift` method routes through the same scanner service.
- **MODIFIED** `00-START-NEXT-SESSION.md` — S2953+ sequence + Drift Scanner + Manifest build specs + twin-mirror IDs.

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

Recycled after PR #3547 merge (`make celery-recycle`). Verified via Rigby:

- `agent_capability_drift_tool` with `action='summary'` returned:
  - `agent_map_entries: 83`, `agent_db_rows: 92`, `run_agent_enum_entries: 59`, `exceptions_loaded: 1`
  - `active_findings: 77`, `suppressed_findings: 2`
  - `has_active_failures: false`, `has_active_warnings: true`
- CodeGeneratorAgent seed exception correctly suppressed on both invariant 2 (exposure completeness) and invariant 3 (recent execution) — confirming the tier-routing works end-to-end.

## Governance

- **Plan pivot ratified** — S2953 first-action moved from A1 Phase 1 → Drift Scanner (per Chris yes+A). Twin mirrors for the pivot were created earlier in the session: `7d795c28` + `cf20e3e4`.
- **Drift Scanner ship ratified** — Chris "Path A" on the close cascade. Twin mirrors dispatched in close cascade.

## Rigby Tool Gap Ledger updates

- **NEW** — Router-level rerouting has no queryable structure. `_apply_task_routing_override` inside `execute_agent_task` performs the reroute at dispatch time but there's no `AgentRerouteEntry`-like model to inspect. Blocks drift scanner invariant 4 ("rerouted must be labeled"). Small design task.
- **NEW** — Capability Manifest is not yet built. Rigby's SIGN-refined field spec (invocation contract, evidence pointers, cost/budget posture, reliability tier, safety class) is in `00-START-NEXT-SESSION.md` under "Capability Manifest — build spec." Parallel-track deliverable during A1 Phase 1.
- **RE-HIT (5th time this terminal session)** — `deliverable_tool.create` diagnostic-flag bug on `initiative_phase_doc` (S2909 Ledger #16). Both S2953 content mirrors flagged; both cleared via ORM.

## Cross-session sweep tally

This terminal session shipped **3 PRs**: #3545 (S2952 pre-A1 capability fixes) + #3546 (S2952 close cascade) + #3547 (S2953 drift scanner). Two full close cascades executed (S2952 + S2953). Wrapper pin rotated twice: `pa-717acd2509014b97` → `pa-eca2a60d039541ac` → (S2954 pin filled at close).

## Next session (S2954) opens

**S2954 first-action = open Golden Evals arc.** Rigby zoom-out elevated this as the third leg beyond Drift Scanner + Capability Manifest.

**Golden Evals arc scope (initial, Chris to refine):**
- Define Tier-1 (sellable-in-A1-audit) agent list — the smallest set of agents whose reliability we'd stake a customer engagement on.
- For each Tier-1 agent: 5–20 canonical prompts covering happy path + typical failure modes.
- For each prompt: expected output schema (JSON Schema or Pydantic model) + accept/reject validators.
- Regression tracking harness: run the eval suite on demand + on schedule; store pass/fail + drift over time.
- Estimated 3–5 sessions minimum.

**Once Golden Evals arc closes:** A1 Phase 1 first-slice implementation opens with Capability Manifest as parallel-track deliverable. Chris's 4 open questions from scoping deliverable `7870eca9` still gate Phase 1 code.

**Also queued (S2953 additions to deferred queue):**
- Drift scanner invariant 4 (rerouted-must-be-labeled) — requires `AgentRerouteEntry`-style model or equivalent queryable structure.
- Capability Manifest full build (parallel-track during A1 Phase 1).
- Curate `capabilities_exceptions.yaml` — 77 findings at HEAD; walk through and either tier-classify (internal-only/legacy/rerouted/experimental) or fix (add missing enum entry / exercise the agent).

## For fuller context (S2846 → S2953)

See:
- **S2953 handoff (current):** `docs/handoffs/SESSION_2953_DRIFT_SCANNER.md`
- **S2953 shipped code:**
  - `core/services/agent_capability_drift.py` — scanner service (3 invariants + classifier)
  - `capabilities_exceptions.yaml` — allowlist (tier semantics documented in header)
  - `core/management/commands/scan_agent_capability_drift.py` — CLI
  - `core/services/pa_tool_schemas.py` — `agent_capability_drift_tool` schema (end of PA_TOOL_SCHEMAS list)
  - `core/services/td_handlers_agents.py:6713-6764` — `_handle_agent_capability_drift`
  - `core/services/tool_dispatcher.py:406-408` — handler registration
  - `core/tests/test_agent_capability_drift.py` — 9 tests
- **S2953 plan pivot ratification:** `cf20e3e4-b45e-40e2-b551-c7def5db7056`
- **S2953 plan pivot content mirror:** `7d795c28-c053-492f-ad05-00b27d335c82`
- **S2952 handoff:** `docs/handoffs/SESSION_2952_PRE_A1_CAPABILITY_FIXES.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
