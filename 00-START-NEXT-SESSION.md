# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2964 CLOSED. Golden Evals validator harness **PR-1 (foundation) shipped**. PR #3569 merged at HEAD `137410e86` (+921 lines / 12 files). Canon_v2 Item 1 landed as code (`_MODEL_POLICIES` 14 → 16 with `ChatConversation` + `ToolCallRecord`; **Ledger #19 discharged**); `EvalRunContext` dataclass + `KNOWN_SUBSTRATES` constants (canon_v2 Item 6 + Rigby's S2964 T1 Q5 zoom-out guardrail); two-substrate adapter abstraction proven end-to-end (slice 8 → `ChatConversationAdapter`, slices 1-7 → `AgentExecutionAdapter`, 91+18=109 prompts persist into new `GoldenEvalRun` model via `run_golden_evals` mgmt cmd); canon_v2 Items 2 + 4 shipped as named canon-documented helpers (`filter_to_buyer_facing_sources()` + `exclude_synthesized_pa_receipts()`). Rigby T1 pre-code SIGN 5 tool_runs joint-agreed on package location + model app + allowlist + skeleton-only scope; Q5 REVISE folded (`KNOWN_SUBSTRATES` constants + receipt filter as named function). Post-merge dogfood verified allowlist live (Probe 1 returned real ChatConversation rows; Probe 2 count_by returned 5,426 ToolCallRecord rows across 21 distinct agent_names — **surprise: Rigby PA turns record as `agent_name='PersonalAssistant'` not `'Rigby'`**; PR-2 `ChatConversationAdapter.build_context()` must join `agent_name IN ('Rigby', 'PersonalAssistant')`). Chris D-verdict via Rigby-relayed terminal path 2026-07-25 — **8 consecutive terminal ratifications** S2957→S2964. **S2965 first-action = PR-2 (executors + Pydantic acceptance runners + fault-injection parser + full adapter build-out + `--execute` flag).**

**Golden Evals arc status:**

| Session | Phase | Ship | HEAD |
|---------|-------|------|------|
| S2954 | arc open | Tier-1 list + Day-1 scope | (arc-open doc) |
| S2955-S2962 | Tier-1 spec-authoring (8/8) | 8 canon_v1 YAMLs | `6bf8d9a81` (S2962) |
| S2963 | arc close | canon_v2 ratification (6 items) | `882626d8f` |
| **S2964** | **harness PR-1 (foundation)** | **allowlist + EvalRunContext scaffold + skeleton adapters + mgmt cmd + `GoldenEvalRun` model** | **`137410e86`** |
| S2965 (next) | harness PR-2 | executors + acceptance runners + fault-injection parser + `--execute` | TBD |
| S2966+ | nightly beat + drift dashboard | scheduled runs + pass-rate telemetry | TBD |

**Canon_v2 items — code landing status:**

| Item | Ratified S2963 | Shipped as code at S2964 PR-1 | Deferred to S2965 PR-2 |
|------|----------------|--------------------------------|-------------------------|
| 1 — `orm_inspect_tool` allowlist | ✅ | ✅ (14→16 models, live-verified) | — |
| 2 — source stratification | ✅ | ✅ (`filter_to_buyer_facing_sources()` helper) | — |
| 3 — opt-in `latency_ms` evidence class | ✅ | ✅ (`EvalRunContext.latency_ms: int \| None`) | — |
| 4 — receipt-contamination predicate | ✅ | ✅ (`exclude_synthesized_pa_receipts()` helper) | — |
| 5 — fault-injection selector convention | ✅ | ⏭ | Parser at PR-2 |
| 6 — `EvalRunContext` shape | ✅ | ✅ (dataclass + `__post_init__` validation) | Adapters get full `build_context()` at PR-2 |

**PRs shipped this session (S2964):**
- u-d-b PR **#3569** — S2964 PR-1 Golden Evals harness foundation (+921 lines / 12 files).
- u-d-b PR **#TBD** — S2964 close cascade (handoff + this 00-START refresh + wrapper pin bump).

**Post-merge:** `make recycle-all` executed per PLAYBOOK-7.4.4 (workers advanced to sha=137410e8612e).

**Governance:** Rigby SIGN discipline held. T1 pre-code SIGN = 5 tool_runs joint-agreement on 5 questions (Q1/Q2/Q4 AGREE; Q3 REVISE minor; Q5 REVISE structural). T2 post-code = 3 live dogfood tool_runs (probe 1/2/3) + one surprise finding (`PersonalAssistant` vs `Rigby` agent_name in `ToolCallRecord`). Chris D-verdict via Rigby proxy after joint agreement — proceed with close + include Probe 3 caveat in handoff (both done).

**Rigby Tool Gap Ledger:**
- **Ledger #19 DISCHARGED** — canon_v2 Item 1 code landed in PR #3569 (`ChatConversation` + `ToolCallRecord` in `_MODEL_POLICIES` at `td_handlers_agents.py:820-870`). Live-verified via Rigby probes.
- **Ledger #16 — no change this session** (no deliverable-create ratification path exercised).
- **Ledger #17 — no change** (Chris used Rigby-relayed terminal path; **8 consecutive terminal ratifications S2957→S2964**).
- **Candidate — `claude_code_tool` stdout/duration_ms capture gap** (Probe 3 caveat; may promote to Ledger #NN if PR-2 wants `claude_code_tool` as the harness dispatch surface at S2965).

Full session context: `docs/handoffs/SESSION_2964_GOLDEN_EVALS_HARNESS_PR1.md`.

---

## S2965 open sequence

**S2965 first-action = PR-2 (executors + acceptance runners + fault-injection parser + full adapter build-out).**

### PR-2 scope

1. **JSON Schema executor** — validate agent responses against `expected_output_shape` blocks in each YAML slice. Reject with structured failure_reasons on shape mismatch. Depends on `jsonschema` library (verify present in `requirements.txt`).

2. **Pydantic acceptance-criteria runners** — starter set covering the 8 shipped slices:
   - **Universal:** `required_fields_present`, `no_unsupported_claims`, `assistant_response_length_gte_N` (parametric).
   - **Rigby-specific** (per `rigby_agent.yaml:252-266`): `no_fabricated_tool_runs`, `no_fabricated_deliverable_ids`, `no_fabricated_workspace_or_user_context`, `no_fabricated_conversation_history`, `detects_and_surfaces_tool_runs_empty_vs_claimed`.
   - **Domain-sensitivity predicates** per Content/Competitor/Legal slices (5-7 predicates each).
   - **`one_of` branch dispatcher** — evaluates ≤2 branches with per-branch `why` strings.

3. **Fault-injection selector parser (canon_v2 Item 5)** — deterministic resolver for `module.Class.method` + `module.function`. Errors loudly on handler-registry keys per canon Item 5 forbid.

4. **`AgentExecutionAdapter` + `ChatConversationAdapter` full `build_context()` build-out:**
   - **AgentExecution:** read row by PK, apply `exclude_synthesized_pa_receipts()` at query time (per canon_v2 Item 4), join `ToolCallRecord` + `LLMCallLog` via `trace_id`, derive `finalized_at` from `completed_at` + `status`, populate opt-in `latency_ms` from `execution_time_ms`.
   - **ChatConversation:** read row by PK, apply `filter_to_buyer_facing_sources()` at query time (per canon_v2 Item 2), join `ToolCallRecord` via `trace_id` + `created_at` window with **`agent_name IN ('Rigby', 'PersonalAssistant')`** (per S2964 dogfood surprise §4), derive `finalized_at` from `response_time_ms` populated + `assistant_response` non-empty, populate opt-in `latency_ms` from `response_time_ms` (canon_v2 Item 3 opt-in — YAML must declare).

5. **`--execute` flag** — remove `--dry-run` default; add explicit `--execute` that actually invokes the agent-under-test and evaluates acceptance criteria. Skeleton `--dry-run` remains available for infra debug.

6. **Substrate row execution** — Golden Evals harness needs a way to dispatch each YAML prompt through the actual agent path. For AgentExecution slices: call `dispatch_agent(agent_name, task, context)`. For ChatConversation (Rigby): call `UnifiedPAEntrypoint.process_message(message)`. Both must populate the substrate row the adapter later observes.

### Universal open sequence (unchanged)

1. **Live-verify S2953 drift scanner:** `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect shape (83/92/59/1 → 77 active).
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --check` — confirm gap-map headline (`100 full / 2 untested` last observed at S2963).
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2965 pin (retired at S2964 close cascade).
4. **Read canon_v2 doc if not already loaded:** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` (190 lines) + S2964 handoff `docs/handoffs/SESSION_2964_GOLDEN_EVALS_HARNESS_PR1.md`.
5. **Read the harness foundation:** `core/services/golden_evals/` package (context.py + adapters/ + loader.py) + `core/models_golden_evals.py` + `core/management/commands/run_golden_evals.py`.
6. **Read agent dispatch reference:** `core/agent_router.py` (for AgentExecution slice dispatch) + `core/services/unified_pa_entrypoint.py` (for ChatConversation slice dispatch).

### S2965 scope note

**In scope for S2965 PR-2:** executor + acceptance runners + fault-injection parser + full adapter build-out + `--execute` flag + first real dispatch of one slice end-to-end (dogfood slice 8 first per S2964 recommendation carried forward).

**Out of scope for S2965:** nightly beat task + pass-rate drift dashboard (S2966+). WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (F1 from S2958). Latent migration drift remediation (surfaced at S2964 §5 — Narrative* / HAIDispatchLog).

**Estimated 1-2 sessions for PR-2 close.**

### Capability Manifest — build spec (parallel-track from A1 Phase 1 start)

_(unchanged — see prior S2953 close snapshots; not part of Golden Evals arc)_

### A1 Phase 1 still ahead (after harness + drift dashboard land)

Chris's 4 open questions from scoping deliverable `7870eca9` still gate Phase 1 code:

1. **Minimum evidence standard** we promise? (run IDs + failure signature samples vs metrics only)
2. **Default turnaround SLA** we can consistently hit without heroics?
3. Sell as **agent-system audit** (end-to-end) or **toolchain reliability audit** (tools/contracts) first?
4. **Legal posture** for handling customer logs (retention window, deletion guarantee, allowed data types)?

### Deferred queue (updated at S2964 close)

**S2964 additions:**
- **Latent migration drift** (Narrative*, `HAIDispatchLog` AlterField pile) surfaced at S2964 makemigrations. Bounded 0395 to `GoldenEvalRun` only; drift remediation belongs to its own PR. Any session.
- **`claude_code_tool` stdout / duration_ms capture gap** (Probe 3 caveat). Ledger candidate; promote if PR-2 depends on `claude_code_tool` as harness dispatch surface.
- **`ChatConversationAdapter` agent_name filter must include `'PersonalAssistant'`** (dogfood §4 surprise). Actionable at PR-2 build-out.
- **Complex-boolean-in-canon-doc misread pattern** (Rigby T2 De Morgan slip at S2963 T2) — one trigger observed. Watch for second occurrence at S2965+ before codifying as canon guidance.

**Carry forward from S2963:**
- Fold P2 / S1 / U1 / P1 / V1 / U2 — all DISCHARGED as canon_v2 Items 1/2/3/4/5/6 at S2963 arc-close.
- Content-append-vs-final content discrepancy (Ledger candidate, carried from S2962).

**Carry forward from S2961/S2960/S2959/S2958/S2957/S2956/S2955/S2954/S2953/S2952/S2951:**
_(unchanged — see S2963 close snapshot)_

**Long-standing (carry forward):**
- Docs restructuring arc (Chris-ratified S2800).
- Slice 5-hardening executable invariants.
- Tier 2 lint promotion.
- Advanced paste-UUID fallback for cluster picker.
- Server-side search + pagination on `/eligible/`.
- Z1/Z2/Z4 signal-dispatch UI polish.
- Rank + cap + paginate follow-ups.
- Per-pattern-type diversity floors.
- Ledger candidates backlog.
- W2 #1 / #2b / #2c pending Chris re-slate.
- LLMCallLog field splits.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os follow-ons.

---

## What's forbidden at S2964 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2964 new forbidden entries:** none.

Canon_v2 adds one new forbid ratified at S2963 (fault-injection selectors MUST NOT use handler-registry keys as canonical without adapter layer, per canon_v2 Item 5). **S2965 PR-2 fault-injection parser must enforce this at load time.**

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2964 additions to the deferred queue:** (see above §Deferred queue).

**Long-standing:**
- Docs restructuring arc (Chris-ratified S2800).
- Slice 5-hardening executable invariants.
- Tier 2 lint promotion.
- Advanced paste-UUID fallback for cluster picker.
- Server-side search + pagination on `/eligible/`.
- Z1/Z2/Z4 signal-dispatch UI polish.
- Rank + cap + paginate follow-ups.
- Per-pattern-type diversity floors.
- Ledger candidates backlog.
- W2 #1 / #2b / #2c pending Chris re-slate.
- LLMCallLog field splits.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953) + Golden Evals arc (S2954-**S2964**) are adjacent-domain net-new engineering + arc substrate, not sweep work.

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

## For fuller context (S2846 → S2964)

See:
- **S2964 handoff (current):** `docs/handoffs/SESSION_2964_GOLDEN_EVALS_HARNESS_PR1.md`
- **S2964 shipped code:**
  - `core/models_golden_evals.py` (GoldenEvalRun)
  - `core/services/golden_evals/` (package: context + adapters + loader)
  - `core/management/commands/run_golden_evals.py`
  - `core/services/td_handlers_agents.py:820-870` (canon_v2 Item 1 allowlist additions)
- **S2963 handoff:** `docs/handoffs/SESSION_2963_GOLDEN_EVALS_ARC_CLOSE_CANON_V2.md`
- **S2963 canon_v2 ratification doc:** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` (190 lines)
- **S2962 handoff:** `docs/handoffs/SESSION_2962_GOLDEN_EVALS_SLICE_8_RIGBY_YAML.md`
- **S2962 shipped code:** `evals/tier1/rigby_agent.yaml` (1,628 lines, 18 prompts, eighth canon_version=1 reference / FIRST non-AgentExecution substrate)
- **S2961 handoff:** `docs/handoffs/SESSION_2961_GOLDEN_EVALS_SLICE_7_COMPETITOR_YAML.md`
- **S2961 shipped code:** `evals/tier1/competitor_analysis_agent.yaml` (1232 lines)
- **S2960 handoff:** `docs/handoffs/SESSION_2960_GOLDEN_EVALS_SLICE_6_CONTENT_YAML.md`
- **S2960 shipped code:** `evals/tier1/content_writer_agent.yaml` (950 lines)
- **S2959 handoff:** `docs/handoffs/SESSION_2959_GOLDEN_EVALS_SLICE_5_LEGAL_YAML.md`
- **S2959 shipped code:** `evals/tier1/legal_doc_drafter_agent.yaml` (794 lines)
- **S2958 handoff:** `docs/handoffs/SESSION_2958_GOLDEN_EVALS_SLICE_4_WORKFLOW_YAML.md`
- **S2958 shipped code:** `evals/tier1/workflow_orchestration_agent.yaml` (801 lines)
- **S2957 handoff:** `docs/handoffs/SESSION_2957_GOLDEN_EVALS_SLICE_3_DEVOPS_YAML.md`
- **S2957 shipped code:** `evals/tier1/devops_agent.yaml` (612 lines)
- **S2956 handoff:** `docs/handoffs/SESSION_2956_GOLDEN_EVALS_SLICE_2_RESEARCH_YAML.md`
- **S2956 shipped code:** `evals/tier1/research_agent.yaml` (523 lines)
- **S2955 handoff:** `docs/handoffs/SESSION_2955_GOLDEN_EVALS_SLICE_1_SIA_YAML.md`
- **S2955 shipped code:** `evals/tier1/system_intelligence_agent.yaml` (canon_version=1 original reference, 463 lines)
- **S2954 arc-open handoff:** `docs/handoffs/SESSION_2954_GOLDEN_EVALS_ARC_OPEN.md`
- **S2954 arc-open scoping doc:** `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md` (95 lines)
- **S2953 handoff:** `docs/handoffs/SESSION_2953_DRIFT_SCANNER.md`
- **S2952 handoff:** `docs/handoffs/SESSION_2952_PRE_A1_CAPABILITY_FIXES.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Ledger #17 (S2957):** `db316865-d08c-4cc1-9d8e-cfac249e8c89` — Chat UI response-relay gap (unchanged this session)
- **Chat UI relay design task (S2957):** `f3f140f9-87bf-488b-8757-eab5d8058f45`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
