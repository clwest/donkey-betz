# SESSION 2958 — Golden Evals Tier-1 slice 4: WorkflowOrchestrationAgent YAML

**Date:** 2026-07-25
**Session:** S2958
**Arc:** Golden Evals (S2954+ open)
**Slice:** 4 of 8 Tier-1 YAMLs
**HEAD at slice merge:** `e2b7e92c2`
**HEAD at close (post-cascade):** filled at close cascade merge
**PR shipped:** [#3557](https://github.com/clwest/donkey-betz-platform/pull/3557)

---

## What shipped

`evals/tier1/workflow_orchestration_agent.yaml` — 801 lines, 13 prompts, fourth canon_version=1 file.

**Coverage:** 5 happy path + 2 each tool_timeout / data_unavailable / ambiguous_input / bad_input.

**Substrate reference:** `evals/tier1/devops_agent.yaml` @ `98ba0e06b` (S2957 slice 3 canon).

**Agent under test:**
- Wrapper: `core/agents/workflow_orchestration_agent.py` (580 lines).
- Legacy: `core/services/workflow_orchestration_agent.py` (5,437 lines).
- Class attribute: `tools = []` — NO LLM function-calling; workflows are programmatic dispatch through 18 hardcoded WORKFLOWS templates.
- Coordinator timeout: 480s (8 min) ThreadPoolExecutor bound at wrapper line 54.

---

## DB grounding

Via Rigby ORM T1 SIGN (2026-07-25):

| Claim | Value | Query |
|---|---|---|
| 30d execs (calendar-30d bound) | 9 (7 pass / 2 fail) | `owner_agent=WorkflowOrchestrationAgent, created_at>=2026-06-25T00:00:00Z` |
| All-time execs | 9 (7 pass / 2 fail) | `owner_agent=WorkflowOrchestrationAgent` — 30d covers 100% of all-time |
| 30d distinct task-string patterns | ~4 patterns | client-side inspection: sanity smokes + 3 morning_brief smoke variants |
| All-time real failures | 2 (both same failure mode) | `error_message__gt=''` |
| Failed rows integrity | 7 completed rows all have `error_message=''` (empty string, not null) | CLAIM 5 |

Both failures = same Celery watchdog kill on morning_brief smoke tests (2026-06-25). Modeled as `workflow_timeout_01_watchdog_kill`.

---

## Honest coverage limits (called out in YAML header)

1. **Thinnest traffic of arc** — 9 30d executions vs SIA 37 / ResearchAgent 37 / DevOpsAgent 13. Every prompt below is either a singleton or from an all-smoke-traffic sample.
2. **Shape mismatch** — declared purpose = execute 18 creative + research workflow templates. But 30d traffic is 100% smoke (sanity + morning_brief smoke variants). Zero production traffic on the creative workflows the agent's core value is built around. Happy paths cover BOTH shapes: real observed traffic (`workflow_happy_01` sanity + `workflow_happy_02` morning_brief + `workflow_happy_03` self-description) AND constructed real-purpose prompts (`workflow_happy_04` explicit business_research + `workflow_happy_05` explicit creative-workflow logo dispatch).
3. **Failure sample = 2** — both same task-string pattern (morning_brief smoke) AND same failure mode (60-min Celery watchdog kill). Zero variety.
4. **New agent shape** — `tools = []` (no LLM function calling). Different from SIA/Research/DevOps which use LLM function-calling. Evidence must come from `data.step_results`, `data.image_ids`, `data.video_ids`, `data.project_created`, and side-effect artifacts (Project rows + Deliverable rows). Codified in `canonical_field_mapping.evidence_pointers` cascade.

---

## Live wrapper bug found at authoring (TRANSITIONAL)

**Symptom:** legacy `_compile_final_result` at `core/services/workflow_orchestration_agent.py:5341` emits key `'steps'` (list of per-step result dicts); wrapper at `core/agents/workflow_orchestration_agent.py:315` reads `legacy_result.get('step_results', [])`. Result: `AgentResult.data.step_results` is `[]` on every happy path even though the underlying execution produced a full step trace.

**Disposition per Rigby S2958 T2:** YAML ships in TRANSITIONAL shape — `canonical_field_mapping.evidence_pointers` explicitly cascades past tier 1 so validators do not hard-assert `step_results` populated on happy paths. A code-fix PR canonicalizing on one key is expected in a follow-up slice. Once the fix lands, v1.1 revision of this YAML REMOVES the fallback mapping rather than layering aliases.

**Why not fix in this PR:** spec-file scope; code fix is a separate concern that touches wrapper + potentially legacy method contract. Fold not blocking arc velocity.

---

## Rigby SIGN cycle T1→T3

**T1 (tool-grounded)** — all 5 claims TOOL-GROUNDED PASS via `orm_inspect_tool` (5 real tool_runs, not rubber-stamp). CLAIM 5 (empty-string vs null semantic on completed rows) confirms the `error_message__gt=''` filter contract that Research/DevOps YAMLs also carry.

**T2 (zoom-out)** — 6 folds surfaced per S2771/S2782 discipline.

**T3 (fold dispositions):**

| Fold | Concern | Disposition |
|---|---|---|
| F1 | Wrapper key-name mismatch (`steps` emitted, `step_results` read) | **FOLDED IN-PR** — TRANSITIONAL marking + explicit "canonicalize on one key, remove fallback in v1.1" language in header + mapping block. Follow-up code-fix PR expected. |
| F2 | "NEW AGENT SHAPE" framing (tools=[] as distinct shape) | **DEFERRED as coverage-note** — Rigby: "No tool calls" is behavioral, not schema. canon_version bumps should track schema/contract changes in result envelopes, not tool-usage patterns. Stay canon_v1. |
| F3 | evidence_pointers cascading 6 tiers with DB row inspection | **FOLDED IN-PR** — tiers 1-5 marked IN-PROCESS; tier 6 (DB row inspection) reclassified as INTEGRATION EVIDENCE non-blocking for Tier-1 validators. |
| Fold A | Arc-substrate: Tier-1 must-have-tool_runs global rule | **DEFERRED to S2962 arc-close** — substrate-level policy: "Tier 1 requires tool-grounded verification when tool_runs exist; otherwise require deterministic artifact fields + provenance pointers." |
| Fold B | Timeout `error_message` exact-string coupling brittleness (`workflow_timeout_02`) | **FOLDED IN-PR** — pattern relaxed from `"timed out after 480s"` → `"timed out"`; `data.timeout=True` codified as stable discriminator; notes updated. |
| Fold C | Ambig vs bad_input remediation posture separation | **NEXT-SLICE-FOLD** — ambig should require clarifying question; bad_input should require rejection + example fix. Tracked for S2959+ authoring. |

**Rigby residual #2 (T3 pass — non-blocking but real):** "at least one of (2,3,4,5) MUST be non-empty" could accidentally fail Deliverable-only workflows (morning_brief / business_research / etc.) that populate NONE of tiers 2-5. **FIXED IN-PR** — added TIER-1 IN-PROCESS EVIDENCE REQUIREMENT per-workflow-shape block explicitly carving out the transitional exception for Deliverable-only workflows until wrapper fix restores tier 1.

**All in-PR folds resolved. Claude+Rigby agreed before Chris D-verdict route.**

---

## Chris D-verdict

**Yes** via TERMINAL 2026-07-25 (`yes ship it`). **NOT** a Chat UI relay — Chris responded directly in the terminal session where the ratification ask was presented. Ledger #17 observation count unchanged at 4 (didn't fire this session; terminal path worked cleanly).

---

## Twin mirrors (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)

| # | Purpose | ID | Notes |
|---|---|---|---|
| OP 1 | Content mirror | `d05172f0-2660-41d7-9354-d56bf2a8dbac` | `initiative_phase_doc`, `category=governance`. Ledger #16 re-hit **11th cumulative** — sticky-cleared via `deliverable_tool.clear_diagnostic`. |
| OP 2 | Ratification envelope | `e519e7a9-934b-40a1-b074-e114ce576733` | `ratification_record`, `category=governance`. Diagnostic clean on create. |

---

## Rigby Tool Gap Ledger updates (Donkey Betz workspace, ledger `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`)

- **Ledger #16** (deliverable_tool.create diagnostic-flag bug on `initiative_phase_doc`): **11th cumulative re-hit** on the S2958 content mirror. Sticky-cleared via `deliverable_tool.clear_diagnostic`. Consistent behavior across 11 sessions — recipe is stable, but the underlying substrate bug remains for engineering-side fix.
- **Ledger #17** (Chat UI response-relay gap): **NO NEW OBSERVATION** this session — Chris responded via TERMINAL directly (`yes ship it`), bypassing Chat UI relay entirely. Ledger #17 count remains at 4. Interesting datapoint: terminal ratification IS a viable low-friction path when Chris is present at the terminal; Chat UI relay gap only bites when Chris returns to Chat UI after Claude has moved on. Not blocking; design task `f3f140f9-87bf-488b-8757-eab5d8058f45` still valid for the Chat-UI-only path.

---

## Golden Evals arc progress (updated at S2958 close)

**Tier-1 YAMLs — 4 of 8 shipped:**
- ✅ **S2955 slice 1 — SystemIntelligenceAgent** (PR #3551) — SHIPPED. canon_version=1 substrate frozen.
- ✅ **S2956 slice 2 — ResearchAgent** (PR #3553) — SHIPPED. Substrate validated on open-world/LLM-synthesis shape.
- ✅ **S2957 slice 3 — DevOpsAgent** (PR #3555) — SHIPPED. Substrate validated on dual-path advisory-vs-config-gen shape; service-level selector fold codified.
- ✅ **S2958 slice 4 — WorkflowOrchestrationAgent** (PR #3557) — SHIPPED. Substrate validated on no-LLM-tool-calls programmatic-dispatch shape; transitional wrapper-bug fold pattern codified; per-workflow-shape evidence cascade codified.
- ⏭ **S2959 slice 5 — LegalDocDrafterAgent** — NEXT (agent at `core/agents/legal/legal_doc_drafter_agent.py:474`).
- **S2960 slice 6 — ContentWriterAgent.**
- **S2961 slice 7 — CompetitorAnalysisAgent.**
- **S2962 slice 8 — PersonalAssistant (Rigby)** + arc-close review (canon uniformity across all 8 YAMLs; canon_version=2 open discussion; deferred folds A/F2 folded in).

**After all 8 Tier-1 YAMLs shipped:**
- **S2963** — Validators (JSON Schema execution + Pydantic model runners consuming `canonical_field_mapping` + `expected_output_shape` + `acceptance_criteria`).
- **S2964** — Harness (`run_golden_evals` mgmt cmd + `GoldenEvalRun` table + nightly beat task).
- **Follow-up code-fix PR** for the wrapper key-name mismatch (F1 from this slice) — canonicalize legacy `_compile_final_result` and wrapper on one key; then v1.1 revision of `workflow_orchestration_agent.yaml` to tighten assertions.

---

## Substrate frozen at canon_version=1 (unchanged; must apply to remaining Tier-1 YAMLs)

1. `schema_version: 1` + `canon_version: 1` at file top.
2. `canonical_field_mapping` block declaring `mapping_source: native|derived` per canon field with named derivation rules.
3. `fault_injection` uses effect-based contract (`component` + `fault.{type, params}`) with `python.{...}` as backend-adapter appendix; portable beyond Python-mock. Prefer service-level selectors (`core.agents.*` / `core.services.*`) per S2957 fold.
4. `one_of` acceptance-criteria capped at ≤2 branches with mandatory `why` string per branch.

**S2958 additions to canon (informative, non-breaking):**
- **Per-workflow-shape evidence-tier requirements** — for agents where different execution shapes produce different evidence sets (creative vs Deliverable-only vs conceptual vs self-description), the `canonical_field_mapping.evidence_pointers` block MAY carve per-shape rules rather than a single hard requirement. Documented shape in this file's mapping block.
- **INTEGRATION EVIDENCE tier distinction** — out-of-band DB row inspection is NOT in Tier-1 validator scope; belongs to a separate integration/side-effect verification suite.
- **TRANSITIONAL marking pattern** — when a YAML documents a fold that requires code follow-up, use the "TRANSITIONAL — code-fix PR expected" phrasing so it doesn't calcify.

---

## Reference implementations (in order of canon fidelity)

- `evals/tier1/system_intelligence_agent.yaml` — canon_version=1 original (463 lines, autonomous single-prompt, closed-world).
- `evals/tier1/research_agent.yaml` — human-diverse open-world (523 lines, includes `error_message` empty-vs-null semantic note).
- `evals/tier1/devops_agent.yaml` — dual-path advisory-vs-config-gen (612 lines, thin-traffic honesty pattern + service-level selector fold).
- `evals/tier1/workflow_orchestration_agent.yaml` — no-LLM-tool-calls programmatic dispatch (801 lines, per-workflow-shape evidence cascade + transitional wrapper-bug pattern).

---

## Files touched this session

- **NEW** `evals/tier1/workflow_orchestration_agent.yaml` — 801 lines.

Close-cascade PR adds:
- **NEW** `docs/handoffs/SESSION_2958_GOLDEN_EVALS_SLICE_4_WORKFLOW_YAML.md` — this file.
- **MODIFIED** `00-START-NEXT-SESSION.md` — S2959 open sequence.
- **MODIFIED** `tools/pa_local.sh` — wrapper pin bump to freshly-minted S2959 conversation pin.

---

## Post-merge disposition

**No `make celery-recycle` required** — PR #3557 is spec-only (YAML config, no code). Per PLAYBOOK-7.4.4, `make celery-recycle` applies to code-shipping PRs.
