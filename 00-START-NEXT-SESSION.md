# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2955 CLOSED. Golden Evals arc-slice 1 shipped: `evals/tier1/system_intelligence_agent.yaml` (PR #3551, HEAD `d2acf9c92`). 463 lines, 13 prompts, all 5 fault-injection categories covered (5 happy + 2 each of tool_timeout / data_unavailable / ambiguous_input / bad_input). DB-grounded on real production data — Rigby ORM T1 verified 37 30d executions matching `owner_agent="SystemIntelligenceAgent"` at `created_at >= 2026-06-25T00:00:00Z`; two observed real failure modes (OpenAI `"Connection error."` + 60-min Celery timeout) each get a dedicated test. Establishes `evals/` tree at repo root. Chris D-verdict `yes` on TWO decisions via Chat UI 2026-07-25: (1) ship YAML as PR #3551, (2) freeze substrate precedent at `canon_version=1` for the remaining 7 Tier-1 YAMLs. **S2956 first-action = author `evals/tier1/research_agent.yaml`** — 2nd Tier-1 slice per arc plan; ResearchAgent has 37 30d exec / 121 all-time / 26 distinct prompts (much richer human traffic than SIA's single autonomous prompt).

**Arc-precedent substrate frozen at canon_version=1** (must apply to all remaining Tier-1 YAMLs):
1. `schema_version: 1` + `canon_version: 1` at file top.
2. `canonical_field_mapping` block declaring `mapping_source: native|derived` per canon field with named derivation rules — S2956 validators MUST consult, never invent mappings.
3. `fault_injection` uses effect-based contract (`component` + `fault.{type, params}`) with `python.{...}` as backend-adapter appendix — portable beyond Python-mock.
4. `one_of` acceptance-criteria capped at ≤2 branches with mandatory `why` string per branch.

Reference implementation: `evals/tier1/system_intelligence_agent.yaml` — every subsequent Tier-1 YAML mirrors this shape.

**Refreshed 2026-07-25 (S2955 close).** Gap-map headline: `100 validated_full / 2 untested` — the 2 are `agent_capability_drift_tool` (S2953-shipped) + `agent_job_status` (S2952-shipped), both untested-by-design at ship time. Unchanged from S2954 close (this session shipped a spec file only, no PA tool changes).

**PRs shipped this session (S2955):**
- u-d-b PR **#3551** — S2955 Golden Evals Tier-1 slice 1: SystemIntelligenceAgent YAML (1 file, +463/-0, spec-only).
- u-d-b PR **#TBD** — S2955 close cascade (handoff + this 00-START refresh + wrapper pin bump).

**Twin mirrors shipped this session (S2955 slice):**
- S2955 slice 1 content mirror: `1f90340e-8001-4632-ba1a-ead249074721` (Donkey Betz workspace, `initiative_phase_doc`, `category='governance'`, diagnostic ORM-cleared per Ledger #16 re-hit — 8th cumulative).
- S2955 slice 1 ratification envelope: `0c73707c-6a05-43f8-a33d-abca3f000d20` (Donkey Betz workspace, `ratification_record`, `category='governance'`, diagnostic clean on create).

Full S2954 arc-open mirror IDs preserved in `docs/handoffs/SESSION_2954_GOLDEN_EVALS_ARC_OPEN.md`.

**Files shipped this session (S2955 slice):**
- **NEW** `evals/tier1/system_intelligence_agent.yaml` — first Tier-1 canonical prompt suite (463 lines, 13 prompts).

**Post-merge:** PR #3551 was spec-only (YAML config, no code), no worker impact → no `make celery-recycle` required (PLAYBOOK-7.4.4 applies to code-shipping PRs).

**Governance:** Rigby SIGN cycle T1→T3. T1 tool-grounded (`orm_inspect_tool.count_by` + `filter` on AgentExecution) — F-BLOCKING on volume-count mismatch (33 vs 37; reconciled to 37 as authoritative full-30d bound). T2 zoom-out WARN on 4 arc-precedent risks — all 4 folded pre-ship. T3 PASS.

**Rigby Tool Gap Ledger:**
- **RE-HIT (Ledger #16, 8th time cumulative)** — `deliverable_tool.create` diagnostic-flag bug on `initiative_phase_doc`. S2955 content mirror flagged; ORM-cleared.
- **Ledger #16 sub-observation** — ORM-clear recipe attempts 5 fields (status/code/notes/detected_at/resolved_at), but only 2 (`diagnostic_status`, `diagnostic_code`) exist on current `Deliverable` model; recipe should be updated to reflect current model shape.
- **Ledger #17 candidate — SECOND observation** (was 1st at S2954). Rigby Chat UI does NOT relay Chris's ratification responses back to Claude terminal. Chris relayed manually again. Second consistent observation; promote from candidate to full ledger row at next opportunity.

Full session context: `docs/handoffs/SESSION_2955_GOLDEN_EVALS_SLICE_1_SIA_YAML.md`.

---

## S2956 open sequence

**S2956 first-action = author `evals/tier1/research_agent.yaml`** — 2nd Tier-1 slice. ResearchAgent volume snapshot: 37 30d exec, 121 all-time, **26 distinct prompts in 30d** (much richer human-input diversity than SIA's single autonomous prompt — allows real sampling of ambiguous/bad inputs from production traffic).

### Universal open sequence

1. **Live-verify S2953 drift scanner still healthy:**
   - `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect shape (83/92/59/1 → 77+2 or drifted numbers with same shape).
   - `python manage.py scan_agent_capability_drift --json | jq .totals` — same from CLI.
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 2 untested`. The 2 untested (`agent_capability_drift_tool`, `agent_job_status`) are expected.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2956 pin (retired at S2955 close cascade).
4. **Read the arc-precedent substrate** at `evals/tier1/system_intelligence_agent.yaml` (canon_version=1 reference implementation) BEFORE authoring the new file — every subsequent Tier-1 YAML mirrors this shape (schema_version + canon_version + canonical_field_mapping + effect-based fault_injection + one_of ≤2-with-why).
5. **Open S2956 slice** — see scope below.

### S2956 arc-slice scope: ResearchAgent YAML

**Target file:** `evals/tier1/research_agent.yaml`.

**Substrate-freeze reference:** `evals/tier1/system_intelligence_agent.yaml` at HEAD `d2acf9c92` is the canon_version=1 reference implementation. Mirror all 4 substrate patterns:
1. `schema_version: 1` + `canon_version: 1`.
2. `canonical_field_mapping` with per-field `mapping_source: native|derived` + named derivation rules. ResearchAgent output shape differs from SIA — derivation rules will be `research_v1_*` prefixed.
3. `fault_injection` effect-based (`component` + `fault.{type, params}` + `python.{...}` adapter).
4. `one_of` acceptance-criteria capped at ≤2 branches with mandatory `why` strings.

**Coverage target:** 5–20 prompts across all 5 fault-injection categories. ResearchAgent's 30d distinct-prompt diversity (26) is rich enough to sample real happy-path and ambiguous inputs directly — pull them via `orm_inspect_tool.filter` on `AgentExecution` where `owner_agent="ResearchAgent"`, `created_at__gte="2026-06-25T00:00:00Z"`.

**Sample ResearchAgent 30d prompts observed at S2955 close:**
- "Research the latest AI trends" (bare, general)
- "Research trends and audience preferences for a 3-episode educational series on..." (initiative-scoped, verbose)
- "Initiative <uuid> stage 1 (Research Brief) external deliverable receipt" (initiative-bound, structured)
- Directive-bound prompts with "BINDING DIRECTIVE" preamble

**Out of scope for S2956:** validator code (JSON Schema executors, Pydantic model runners) and `run_golden_evals` mgmt cmd. Those come after all 8 Tier-1 YAMLs are shipped.

**Estimated 1 session** for this slice.

### Golden Evals arc structure (updated at S2955 close)

**Tier-1 YAMLs — 1 of 8 shipped:**
- ✅ **S2955 slice 1 — SystemIntelligenceAgent** (PR #3551, HEAD `d2acf9c92`) — SHIPPED. canon_version=1 substrate frozen.
- ⏭ **S2956 slice 2 — ResearchAgent** — NEXT.
- **S2957 slice 3 — DevOpsAgent.**
- **S2958 slice 4 — WorkflowOrchestrationAgent.**
- **S2959 slice 5 — LegalDocDrafterAgent.**
- **S2960 slice 6 — ContentWriterAgent.**
- **S2961 slice 7 — CompetitorAnalysisAgent.**
- **S2962 slice 8 — PersonalAssistant (Rigby).**

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

### Deferred queue (updated at S2955 close)

**S2955 additions:**
- **Ledger #17 promotion from candidate to full row** — Chat UI relay gap now has 2 consistent observations (S2954 + S2955). Next hit promotes to full ledger row + design task for Rigby response-relay wiring.
- **Ledger #16 ORM-clear recipe drift** — established recipe attempts to clear 5 diagnostic_* fields on `Deliverable`, but only 2 exist on the current model (`diagnostic_status`, `diagnostic_code`). Update recipe (in `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic.md`) to match current model shape.
- **Bound-annotation discipline for volume claims in YAML headers** — S2955 T1 F-BLOCK arose from `now - timedelta(days=30)` bound producing 33 vs full-30d producing 37. Consider making calendar-30d the canonical bound across all Tier-1 YAML volume snapshots + drift-scanner + audit tools.

**S2954 additions (carry forward):**
- **Rigby Chat UI response-relay gap** (Ledger #17 candidate → now 2 observations, see promotion above).
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

## What's forbidden at S2955 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2954 new forbidden entries:** none.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2954 additions to the deferred queue:**
- Rigby Chat UI response-relay gap (Ledger #17 candidate).
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

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953 Drift Scanner) + Golden Evals arc-open (S2954) are adjacent-domain net-new engineering + arc substrate, not sweep work.

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

## For fuller context (S2846 → S2955)

See:
- **S2955 handoff (current):** `docs/handoffs/SESSION_2955_GOLDEN_EVALS_SLICE_1_SIA_YAML.md`
- **S2955 shipped code:** `evals/tier1/system_intelligence_agent.yaml` (canon_version=1 reference implementation for Tier-1 YAMLs, 463 lines, 13 prompts)
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
