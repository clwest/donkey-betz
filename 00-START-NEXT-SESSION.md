# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2956 CLOSED. Golden Evals arc-slice 2 shipped: `evals/tier1/research_agent.yaml` (PR #3553, HEAD `c8815cd38`). 523 lines, 13 prompts, all 5 fault-injection categories covered (5 happy + 2 each of tool_timeout / data_unavailable / ambiguous_input / bad_input). First slice authored under S2955-frozen `canon_version=1` substrate; validates the substrate holds cleanly on an agent with a very different shape (open-world research + LLM synthesis + iterative search + evidence-cited output vs SIA's closed-world platform-health with tool-grounded item counts). DB-grounded on ResearchAgent 30d production traffic — Claude ORM T0 verified 37 30d executions (`owner_agent="ResearchAgent"`, `created_at >= 2026-06-25T00:00:00Z`) → Rigby T1 tool-grounded PASS reconfirmed (36 completed + 1 failed / 121 all-time / 26 distinct 30d prompts). Top-frequency task `"Research market trends and industry landscape"` (12/37 = 32.4%, autonomous) covered as `research_happy_02_market_trends_autonomous`. One observed all-time failure mode (Celery 60-min watchdog kill) gets dedicated test `research_timeout_01_watchdog_kill`. Chris D-verdict `yes` via Chat UI 2026-07-25 (manual relay — Ledger #17 3rd observation, promote-to-full-ledger-row queued for S2957). **S2957 first-action = author `evals/tier1/devops_agent.yaml`** — 3rd Tier-1 slice per arc plan; DevOpsAgent volume snapshot at S2956 close: 13 30d exec / 25 all-time / 13 distinct 30d tasks (much thinner traffic than SIA or ResearchAgent — call out honest limits in the header).

**Arc-precedent substrate frozen at canon_version=1** (unchanged from S2955; must apply to all remaining Tier-1 YAMLs):
1. `schema_version: 1` + `canon_version: 1` at file top.
2. `canonical_field_mapping` block declaring `mapping_source: native|derived` per canon field with named derivation rules — S2963 validators MUST consult, never invent mappings.
3. `fault_injection` uses effect-based contract (`component` + `fault.{type, params}`) with `python.{...}` as backend-adapter appendix — portable beyond Python-mock.
4. `one_of` acceptance-criteria capped at ≤2 branches with mandatory `why` string per branch.

Reference implementations (in order of canon fidelity):
- `evals/tier1/system_intelligence_agent.yaml` — original canon_version=1 reference (463 lines, autonomous single-prompt shape).
- `evals/tier1/research_agent.yaml` — second reference (523 lines, human-diverse 26-prompt shape, includes verifier note about Django empty-string vs NULL semantic on `AgentExecution.error_message`).

**Refreshed 2026-07-25 (S2956 close).** Gap-map headline unchanged: `100 validated_full / 2 untested` — the 2 are `agent_capability_drift_tool` (S2953-shipped) + `agent_job_status` (S2952-shipped), both untested-by-design at ship time. This session shipped a spec file only, no PA tool changes.

**PRs shipped this session (S2956):**
- u-d-b PR **#3553** — S2956 Golden Evals Tier-1 slice 2: ResearchAgent YAML (1 file, +523/-0, spec-only).
- u-d-b PR **#TBD** — S2956 close cascade (handoff + this 00-START refresh + wrapper pin bump).

**Twin mirrors shipped this session (S2956 slice):**
- S2956 slice 2 content mirror: `a6fa0fa4-23c9-4959-946c-d471c12d24a1` (Donkey Betz workspace, `initiative_phase_doc`, `category='governance'`, Ledger #16 re-hit 9th cumulative, sticky-cleared via `deliverable_tool.clear_diagnostic`).
- S2956 slice 2 ratification envelope: `8f98a793-942d-40bb-8639-580295023bbf` (Donkey Betz workspace, `ratification_record`, `category='governance'`, diagnostic clean on create).

Full S2955 slice-1 mirror IDs preserved in `docs/handoffs/SESSION_2955_GOLDEN_EVALS_SLICE_1_SIA_YAML.md`.

**Files shipped this session (S2956 slice):**
- **NEW** `evals/tier1/research_agent.yaml` — second Tier-1 canonical prompt suite (523 lines, 13 prompts).

**Post-merge:** PR #3553 was spec-only (YAML config, no code), no worker impact → no `make celery-recycle` required (PLAYBOOK-7.4.4 applies to code-shipping PRs).

**Governance:** Rigby SIGN cycle T1→T3. T1 tool-grounded PASS (`orm_inspect_tool.count_by` + `filter` on `AgentExecution`) — all 4 volume claims match DB reality. T2 zoom-out surfaced 6 folds — all disposed appropriately (1 folded in-PR: non-null vs non-empty `error_message` verifier note in YAML header; 2 disagreed-with-evidence: one_of cap already matches ratified ≤2 canon + 12/37 highest-volume task already covered by `research_happy_02`; 1 deferred future-trigger: `health_status` derivation over-degrade concern for canon_version=2; 2 tracked to arc-close S2962: canon uniformity + SIA comment drift). T3 PASS on every fold disposition.

**Rigby Tool Gap Ledger:**
- **RE-HIT (Ledger #16, 9th time cumulative)** — `deliverable_tool.create` diagnostic-flag bug on `initiative_phase_doc`. S2956 content mirror flagged `missing_initiative_id`; sticky-cleared via `deliverable_tool.clear_diagnostic`.
- **Ledger #16 sub-observation (S2956)** — from Rigby's PA surface, `orm_inspect_tool` is read-only. The ORM-clear recipe documented in `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic.md` assumes direct Claude ORM access. When routed via Rigby, the equivalent is `deliverable_tool.clear_diagnostic` (sticky-cleared sentinel). Recipe should be updated to reflect both routes; drift note carries forward.
- **Ledger #17 candidate — THIRD observation** (S2954 → S2955 → S2956). Rigby Chat UI does NOT relay Chris's ratification responses back to Claude terminal. Chris relayed manually again. Third consistent observation across 3 sessions — **PROMOTE to full ledger row at S2957 first opportunity** + open design task for Rigby Chat UI response-relay wiring.
- **Ledger candidate — orm_inspect_tool distinct-count guardrail** — group-by on text fields (e.g., `task`) rejected as "expensive/unbounded". For ResearchAgent with 37 30d rows this was easy to work around (full sample + client-side dedupe); for agents with >200 30d executions this pattern won't scale. Consider a `distinct_values_capped` action or a `hash_distinct` shortcut.

Full session context: `docs/handoffs/SESSION_2956_GOLDEN_EVALS_SLICE_2_RESEARCH_YAML.md`.

---

## S2957 open sequence

**S2957 first-action = author `evals/tier1/devops_agent.yaml`** — 3rd Tier-1 slice. DevOpsAgent volume snapshot at S2956 close (Claude ORM verified 2026-07-25): 13 30d exec, 25 all-time, 13 distinct 30d tasks. Much thinner traffic than SIA (37) or ResearchAgent (37/26 distinct) — the YAML header should honestly call out the thinner sample and lean more heavily on constructed fault-injection cases from DevOpsAgent's known dependency graph.

### Universal open sequence

1. **Live-verify S2953 drift scanner still healthy:**
   - `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect shape (83/92/59/1 → 77+2 or drifted numbers with same shape).
   - `python manage.py scan_agent_capability_drift --json | jq .totals` — same from CLI.
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 2 untested`. The 2 untested (`agent_capability_drift_tool`, `agent_job_status`) are expected.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2957 pin (retired at S2956 close cascade).
4. **Read both arc-precedent substrate references BEFORE authoring:**
   - `evals/tier1/system_intelligence_agent.yaml` (canon_version=1 original reference, autonomous single-prompt).
   - `evals/tier1/research_agent.yaml` (second reference, human-diverse 26-prompt, plus verifier note about `error_message` semantic).
5. **Open S2957 slice** — see scope below.

### S2957 arc-slice scope: DevOpsAgent YAML

**Target file:** `evals/tier1/devops_agent.yaml`.

**Substrate-freeze reference:** `evals/tier1/research_agent.yaml` at HEAD `c8815cd38` OR `evals/tier1/system_intelligence_agent.yaml` at HEAD `d2acf9c92` — both canon_version=1. Mirror all 4 substrate patterns.

**Coverage target:** 5–20 prompts across all 5 fault-injection categories. DevOpsAgent's 30d distinct-prompt diversity (13) is thin — pull all 13 real prompts via `orm_inspect_tool.filter` on `AgentExecution` where `owner_agent="DevOpsAgent"`, `created_at__gte="2026-06-25T00:00:00Z"` and select the most representative 5 for happy-path coverage.

**Volume header hygiene:**
- Use full-calendar-30d bound (`created_at >= 2026-06-25T00:00:00Z`), not `now - timedelta(days=30)` — matches SIA + ResearchAgent precedent.
- Distinguish non-null vs non-empty `error_message` explicitly in the failure count claim (verifier note from ResearchAgent YAML applies universally).
- Honestly call out the thinner sample (13 30d vs SIA's 37 and ResearchAgent's 37) as a coverage limitation.

**Out of scope for S2957:** validator code (JSON Schema executors, Pydantic model runners) and `run_golden_evals` mgmt cmd. Those come after all 8 Tier-1 YAMLs are shipped.

**Estimated 1 session** for this slice.

### Golden Evals arc structure (updated at S2956 close)

**Tier-1 YAMLs — 2 of 8 shipped:**
- ✅ **S2955 slice 1 — SystemIntelligenceAgent** (PR #3551, HEAD `d2acf9c92`) — SHIPPED. canon_version=1 substrate frozen.
- ✅ **S2956 slice 2 — ResearchAgent** (PR #3553, HEAD `c8815cd38`) — SHIPPED. Substrate validated on open-world/LLM-synthesis shape.
- ⏭ **S2957 slice 3 — DevOpsAgent** — NEXT.
- **S2958 slice 4 — WorkflowOrchestrationAgent.**
- **S2959 slice 5 — LegalDocDrafterAgent.**
- **S2960 slice 6 — ContentWriterAgent.**
- **S2961 slice 7 — CompetitorAnalysisAgent.**
- **S2962 slice 8 — PersonalAssistant (Rigby)** + arc-close review (canon uniformity across all 8 YAMLs; potential canon_version=2 open discussion).

**After all 8 Tier-1 YAMLs shipped:**
- **S2963** — Validators (JSON Schema execution + Pydantic model runners consuming `canonical_field_mapping` + `expected_output_shape` + `acceptance_criteria`).
- **S2964** — Harness (`run_golden_evals` mgmt cmd + `GoldenEvalRun` table + nightly beat task).
- **After arc close** — A1 Phase 1 first-slice opens (Chris's 4 gating questions still block; see below).

_Note: session numbers above are ESTIMATED linear progression assuming 1 slice per session. Actual session numbers may drift if a slice takes >1 session or if a non-arc session interleaves._

### Capability Manifest — build spec (parallel-track from A1 Phase 1 start)

_(unchanged — see prior S2953 close snapshots; not part of Golden Evals arc)_

### A1 Phase 1 still ahead (after Golden Evals arc closes)

Chris's 4 open questions from scoping deliverable `7870eca9` still gate Phase 1 code:

1. **Minimum evidence standard** we promise? (run IDs + failure signature samples vs metrics only)
2. **Default turnaround SLA** we can consistently hit without heroics?
3. Sell as **agent-system audit** (end-to-end) or **toolchain reliability audit** (tools/contracts) first?
4. **Legal posture** for handling customer logs (retention window, deletion guarantee, allowed data types)?

### Deferred queue (updated at S2956 close)

**S2956 additions:**
- **Ledger #17 PROMOTE TO FULL ROW** — Chat UI relay gap now has 3 consistent observations (S2954 candidate → S2955 2nd → S2956 3rd). First S2957 action: promote to full Ledger row + open design task for Rigby Chat UI response-relay wiring so ratification responses land in the terminal automatically.
- **Ledger #16 recipe drift (dual-route)** — recipe should document both routes: (a) direct Claude ORM (set diagnostic_* fields to None), (b) via Rigby PA (`deliverable_tool.clear_diagnostic` sticky-cleared sentinel). Update `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic.md`.
- **`orm_inspect_tool` distinct-count guardrail** — group-by on text fields rejected as "expensive/unbounded". Won't scale for agents with >200 30d executions. Consider `distinct_values_capped` action or `hash_distinct` shortcut.
- **Fold #5 (S2956 T2) — `health_status` derivation over-degrade for open-world agents** — UNKNOWN→degraded may over-penalize research/analysis agents where uncertainty is expected. Track for `canon_version=2` arc-close discussion at S2962. Would need to separate "contract completeness" from "agent health".
- **Fold #6b (S2956 T2) — Tier-1 canon uniformity review** — comment-vs-usage mismatches across YAMLs (e.g., SIA header comment says one_of ≤3 but usage is ≤2). Track for arc-close review at S2962.

**S2955 additions (carry forward):**
- **Ledger #16 ORM-clear recipe drift** (subsumed by dual-route note above).
- **Bound-annotation discipline for volume claims in YAML headers** — S2955 T1 F-BLOCK arose from `now - timedelta(days=30)` bound producing 33 vs full-30d producing 37. Consider making calendar-30d the canonical bound across all Tier-1 YAML volume snapshots + drift-scanner + audit tools.

**S2954 additions (carry forward):**
- **00-START validated-full gap-map lint sync** — consider CI check that the 00-START headline pulls from `build_pa_tool_audit` live rather than manual editing.

**S2953 additions (carry forward):**
- Drift scanner invariant 4 (rerouted-must-be-labeled) — requires `AgentRerouteEntry`-style queryable model.
- Curate `capabilities_exceptions.yaml` — 77 active findings at HEAD `9f25abdb1`. Walk each; tier-classify or fix.
- Fix run_agent dispatch-response agent-name echo (from S2952) — echo mapping-canonical CamelCase, not input string.

**S2952 carry-forward:**
- Schema/handler drift scanner (PA tool contract — separate from S2953's agent drift scanner).
- `agent_job_status` design gap harder fix (reserve `AgentExecution` row synchronously at dispatch).

**Signal-dispatch queue (from S2951, carry forward):**
- **(A11)** 6th signal-dispatch rule (`sentiment_shift` or `market_movement`) — no volume evidence yet.
- **(NEW-6)** Fair-share round-robin scanning in `scan_and_dispatch()`.
- **(NEW-7)** Persist `per_rule_diagnostics` per `scan_run_id`.
- **(NEW-8)** Per-pattern effectiveness attribution for reused agents.

**Long-standing (carry forward from S2951):**
- **(D)** Docs restructuring arc — Chris-ratified S2800, still queued.
- **(B)** Slice 5-hardening — 3-4 executable invariants deferred at S2928.
- **(E)** Tier 2 lint promotion — envelope-JSON top-level-key parse.
- **(H)** generate_newsletter dry_run default flip.
- **(I)** bulk_archive statuses autofill robustness — 2nd trigger at S2945.
- **Envelope enhancement** (record-only S2942) — `verify_hint` + `would_write_count` for dry_run.
- **Close-ceremony ledger-flip checklist** (meta-fix, record-only S2942).
- **Deliverable v1 template retrofit** (record-only S2943).

---

## What's forbidden at S2956 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2956 new forbidden entries:** none.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2956 additions to the deferred queue:**
- Ledger #17 full-row promotion + design task (first S2957 action, then queued).
- `health_status` derivation refactor for open-world agents (canon_version=2 discussion at S2962).
- Tier-1 canon uniformity review (arc-close review at S2962).

**S2954 additions (carry forward):**
- Rigby Chat UI response-relay gap (now Ledger #17 3rd observation, promote at S2957).
- 00-START validated-full gap-map lint sync.

**S2953 additions (carry forward):**
- Drift scanner invariant 4 (rerouted-must-be-labeled).
- `capabilities_exceptions.yaml` curation.

**S2952 additions (carry forward):**
- Schema/handler drift scanner (PA tool contract).
- `agent_job_status` design gap harder fix.
- Dispatch-response agent-name echo cleanup.

**S2951 additions (carry forward):**
- `MarketIntelligenceCoordinator` rename — cosmetic only.
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

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953 Drift Scanner) + Golden Evals arc-open + slice work (S2954-S2956) are adjacent-domain net-new engineering + arc substrate, not sweep work.

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

## For fuller context (S2846 → S2956)

See:
- **S2956 handoff (current):** `docs/handoffs/SESSION_2956_GOLDEN_EVALS_SLICE_2_RESEARCH_YAML.md`
- **S2956 shipped code:** `evals/tier1/research_agent.yaml` (523 lines, 13 prompts, second canon_version=1 reference)
- **S2955 handoff:** `docs/handoffs/SESSION_2955_GOLDEN_EVALS_SLICE_1_SIA_YAML.md`
- **S2955 shipped code:** `evals/tier1/system_intelligence_agent.yaml` (canon_version=1 original reference, 463 lines, 13 prompts)
- **S2954 arc-open handoff:** `docs/handoffs/SESSION_2954_GOLDEN_EVALS_ARC_OPEN.md`
- **S2954 arc-open scoping doc:** `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md` (95 lines)
- **S2953 handoff:** `docs/handoffs/SESSION_2953_DRIFT_SCANNER.md`
- **S2953 shipped code:**
  - `core/services/agent_capability_drift.py` — scanner service
  - `capabilities_exceptions.yaml` — allowlist
  - `core/management/commands/scan_agent_capability_drift.py` — CLI
  - `core/services/pa_tool_schemas.py` — `agent_capability_drift_tool` schema
  - `core/services/td_handlers_agents.py:6713-6764` — `_handle_agent_capability_drift`
  - `core/services/tool_dispatcher.py:406-408` — handler registration
  - `core/tests/test_agent_capability_drift.py` — 9 tests
- **S2952 handoff:** `docs/handoffs/SESSION_2952_PRE_A1_CAPABILITY_FIXES.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
