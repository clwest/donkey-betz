# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2965 CLOSED. Golden Evals validator harness **PR-2a (executors + runners + --execute + SIA dogfood) shipped**. PR #3571 merged at HEAD `38ee09602` (+1,550 / -66 across 10 files). JSON Schema executor + fault-injection selector parser (canon_v2 Item 5) + universal acceptance-criteria runners (`required_fields_present` + `assistant_response_length_gte_N`) + SIA canonicalizer + `AgentExecutionAdapter.build_context()` full + `ChatConversationAdapter.build_context()` full with evidence-source labeling + `--execute` mgmt cmd flag + `EvalRunContext.evidence_source` / `ledger_health` extension all landed. End-to-end dogfood — `python manage.py run_golden_evals --execute --slice system_intelligence_agent --prompt sia_happy_02_severity_filtered_critical` returns `[PASS]` with 3 correctly-INCONCLUSIVE unknown predicates; `GoldenEvalRun` row persistence verified. **S2965 T1 SIGN raw-ORM verification surfaced two platform-integrity findings — Rigby Tool Gap Ledger #20 (`ToolCallRecord.trace_id` NULL on 100% of 5,430 rows) + #21 (PA→ToolCallRecord write silent regression 2026-06-19, 35d)**. Chris D-verdict via terminal ratified Option A (split into PR-2a this session / PR-2b next / separate fix arc for #20+#21) — **9 consecutive terminal ratifications S2957→S2965**. **S2966 first-action = PR-2b (Rigby-specific `no_fabricated_*` acceptance runners + slice 8 dogfood + Celery-dispatch path for full substrate-row round-trip + per-agent canonicalizers for slices 2-7).**

**Golden Evals arc status:**

| Session | Phase | Ship | HEAD |
|---------|-------|------|------|
| S2954 | arc open | Tier-1 list + Day-1 scope | (arc-open doc) |
| S2955-S2962 | Tier-1 spec-authoring (8/8) | 8 canon_v1 YAMLs | `6bf8d9a81` (S2962) |
| S2963 | arc close | canon_v2 ratification (6 items) | `882626d8f` |
| S2964 | harness PR-1 (foundation) | allowlist + EvalRunContext scaffold + skeleton adapters + mgmt cmd + `GoldenEvalRun` model | `137410e86` |
| **S2965** | **harness PR-2a (executors + runners + --execute)** | **JSON Schema executor + fault-injection parser + universal runners + SIA canonicalizer + full adapter build-out + `--execute` flag + SIA end-to-end dogfood** | **`38ee09602`** |
| S2966 (next) | harness PR-2b | Rigby-specific runners + slice 8 dogfood + Celery-dispatch path + canonicalizers slices 2-7 | TBD |
| S2967+ | nightly beat + drift dashboard | scheduled runs + pass-rate telemetry | TBD |

**Canon_v2 items — code landing status:**

| Item | Ratified S2963 | Shipped as code at S2964 PR-1 | Shipped as code at S2965 PR-2a | Deferred to S2966 PR-2b |
|------|----------------|--------------------------------|--------------------------------|-------------------------|
| 1 — `orm_inspect_tool` allowlist | ✅ | ✅ | — | — |
| 2 — source stratification | ✅ | ✅ (helper) | ✅ (adapter enforcement + safety net) | — |
| 3 — opt-in `latency_ms` evidence class | ✅ | ✅ (dataclass field) | ✅ (adapter opt-in path exercised) | — |
| 4 — receipt-contamination predicate | ✅ | ✅ (helper) | ✅ (adapter enforcement + safety net) | — |
| 5 — fault-injection selector convention | ✅ | ⏭ | ✅ (parser rejects handler-registry keys) | Runtime injection loop |
| 6 — `EvalRunContext` shape | ✅ | ✅ (dataclass + validation) | ✅ (extended with `evidence_source` + `ledger_health`; both adapters full build-out) | — |

**PRs shipped this session (S2965):**
- u-d-b PR **#3571** — S2965 PR-2a Golden Evals harness executors + runners + --execute + SIA dogfood (+1,550 / -66).
- u-d-b PR **#TBD** — S2965 close cascade (handoff + this 00-START refresh + wrapper pin bump).

**Post-merge:** `make recycle-all` executed per PLAYBOOK-7.4.4 (workers advanced to sha=`38ee09602420`).

**Governance:** Rigby T1 pre-code SIGN = 5 tool_run verifications + 5 questions (Q1 REVISE semantic / Q2 REVISE F-BLOCKING extended by raw-ORM to Ledger #20+#21 / Q3 REVISE finalized_at rule / Q4 AGREE adapters-first / Q5 REVISE scope split). Claude fold-back turn with raw-ORM verification. Rigby A2 REVISE → `evidence_source` + `ledger_health` fields shipped. Rigby A3 pushback → framed Ledger #20+#21 as platform integrity incident. Chris D-verdict via terminal after plain-English framing (per `feedback_plain_english_decision_framing_for_chris`).

**Rigby Tool Gap Ledger:**
- **Ledger #20 NEW** — `ToolCallRecord.trace_id` NULL on 100% of 5,430 rows. Canonical join key in `rigby_agent.yaml canonical_field_mapping` §evidence_pointers unusable. Blocks PR-2b Rigby fabrication predicates. Fix in separate arc.
- **Ledger #21 NEW** — PA→ToolCallRecord write silent regression 2026-06-19 → present (35d). All-time PA rows = 907, last-30d = 0. Root cause: WARNING-swallow at `tool_dispatcher.py:1043` + likely `conversation_id` UUID field-type mismatch. Fix in separate arc.
- **Ledger #17 — no change** (Chris used Rigby-relayed terminal path; **9 consecutive terminal ratifications S2957→S2965**).
- **Ledger #19 — no change** (allowlist landed at S2964; still discharged).
- **New candidate — Rigby outbound-messaging gap:** Rigby has no PA tool to post proactively into a Chris-visible Chat UI thread; only responds in the thread she was called from. This is the *reverse* of Ledger #17 (Chat UI response-relay). Surfaced S2965 T2 when Claude asked her to relay D-verdict framing. One trigger; watch for second.

Full session context: `docs/handoffs/SESSION_2965_GOLDEN_EVALS_HARNESS_PR2A.md`.

---

## S2966 open sequence

**S2966 first-action = PR-2b (Rigby-specific acceptance runners + slice 8 dogfood + Celery-dispatch path + canonicalizers slices 2-7).**

### PR-2b scope

1. **Celery-dispatch mode for `--execute`** — solve the S2965 known limitation (direct `.execute()` bypasses AgentExecution row write). Options: (a) route dispatch through `dispatch_agent.delay(...)` Celery task + poll for completion, (b) two-phase: instantiate `AgentExecution` row explicitly with `parent_execution_id=None + trigger_source='golden_evals_harness'`, then invoke `.execute()` inside its `time_travel_session` context. Pick whichever preserves canonical write-side behavior.

2. **Rigby-specific `no_fabricated_*` acceptance runners** (per `rigby_agent.yaml:252-266`):
   - `no_fabricated_tool_runs` — gated on `ledger_health=OK` else INCONCLUSIVE.
   - `no_fabricated_deliverable_ids` — regex-validate UUID format + existence-check when ToolCallRecord for `deliverable_tool` present in context.
   - `no_fabricated_workspace_or_user_context` — gated on workspace membership check.
   - `no_fabricated_conversation_history` — gated on same-conversation_id turn history.
   - `detects_and_surfaces_tool_runs_empty_vs_claimed` — combines evidence-gate + rubber-stamp detection.
   - All must return INCONCLUSIVE when `ledger_health != OK` (Rigby A2 REVISE gating convention).

3. **Per-agent canonicalizers for slices 2-7** — Research / DevOps / Workflow / Legal / Content / Competitor. Each slice's `canonical_field_mapping` block defines the derivation rule; write one canonicalizer per named rule.

4. **Slice 8 (Rigby) dogfood** — first `ChatConversation`-substrate real dispatch. Route through `UnifiedPAEntrypoint.process_message(message)` async. Because Ledger #20+#21 aren't fixed, expect widespread INCONCLUSIVE verdicts on Rigby-specific predicates — the harness should print INCONCLUSIVE counts prominently in the summary so the substrate gap is visible.

5. **`one_of` branch dispatcher** — evaluates `≤2` branches with per-branch `why` strings per S2963 canon_v2. Ships as a runner-registry entry.

### Universal open sequence (unchanged)

1. **Live-verify S2953 drift scanner:** `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect shape (83/92/59/1 → 77 active).
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --check` — confirm gap-map headline (`100 full / 2 untested` last observed at S2963).
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2966 pin (retired at S2965 close cascade).
4. **Read S2965 handoff + PR-2a shipped code:** `docs/handoffs/SESSION_2965_GOLDEN_EVALS_HARNESS_PR2A.md` + `core/services/golden_evals/` (executors + fault_injection + runners + canonicalizers + adapters full build-out) + `core/management/commands/run_golden_evals.py`.
5. **Read canon_v2 doc if not already loaded:** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md` (190 lines).
6. **Verify Rigby Tool Gap Ledger:** deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` — Ledger #20 + #21 entries appended at S2965 close.

### S2966 scope note

**In scope for S2966 PR-2b:** Celery-dispatch mode + Rigby-specific runners + canonicalizers 2-7 + slice 8 dogfood + one_of branch dispatcher. **Estimated 1-2 sessions** (same size as PR-2a).

**Out of scope for S2966:** Ledger #20 + #21 code fixes (separate arc). Nightly beat task + pass-rate drift dashboard (S2967+). WorkflowOrchestrationAgent wrapper key-name mismatch (F1 from S2958). Latent migration drift remediation.

### Capability Manifest — build spec (parallel-track from A1 Phase 1 start)

_(unchanged — see prior S2953 close snapshots; not part of Golden Evals arc)_

### A1 Phase 1 still ahead (after harness + drift dashboard land)

Chris's 4 open questions from scoping deliverable `7870eca9` still gate Phase 1 code:

1. **Minimum evidence standard** we promise? (run IDs + failure signature samples vs metrics only)
2. **Default turnaround SLA** we can consistently hit without heroics?
3. Sell as **agent-system audit** (end-to-end) or **toolchain reliability audit** (tools/contracts) first?
4. **Legal posture** for handling customer logs (retention window, deletion guarantee, allowed data types)?

### Deferred queue (updated at S2965 close)

**S2965 additions:**
- **PR-2b (next session):** Rigby-specific fabrication runners + slice 8 dogfood + Celery-dispatch mode + slices 2-7 canonicalizers + one_of dispatcher.
- **Separate arc (later):** Ledger #20 + #21 code fixes — populate `trace_id` at ToolCallRecord write sites, investigate + fix silent PA write regression, migrate `ToolCallRecord.conversation_id` field type or add UUID coerce helper.
- **PR-2a limitation:** direct `.execute()` bypasses Celery AgentExecution row write — adapter falls back to in-memory context. PR-2b solves.
- **Rigby outbound-messaging gap** — new ledger candidate (one trigger, watching for second).

**Carry forward from S2964:**
- Latent migration drift (Narrative* / HAIDispatchLog AlterField pile).
- `claude_code_tool` stdout / duration_ms capture gap (Probe 3 caveat from S2964).
- Complex-boolean-in-canon-doc misread pattern (one trigger observed).

**Carry forward from S2963:**
- Fold P2 / S1 / U1 / P1 / V1 / U2 — all DISCHARGED as canon_v2 Items 1/2/3/4/5/6 at S2963 arc-close.

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

## What's forbidden at S2965 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2965 new forbidden entries:** none.

Canon_v2 forbid (fault-injection selectors) is now **actively enforced in code** at `core/services/golden_evals/fault_injection.py:parse_selector` — bare identifiers or non-importable dotted paths raise `FaultInjectionSelectorError` at load time.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2965 additions to the deferred queue:** (see above §Deferred queue).

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

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953) + Golden Evals arc (S2954-**S2965**) are adjacent-domain net-new engineering + arc substrate, not sweep work.

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

## For fuller context (S2846 → S2965)

See:
- **S2965 handoff (current):** `docs/handoffs/SESSION_2965_GOLDEN_EVALS_HARNESS_PR2A.md`
- **S2965 shipped code:**
  - `core/services/golden_evals/` — canonicalizers.py + executors.py + fault_injection.py + runners.py + context.py (extended) + adapters/{agent_execution,chat_conversation}.py (extended)
  - `core/management/commands/run_golden_evals.py` (extended with `--execute` mode)
  - `core/models_golden_evals.py` (extended with `evidence_source` + `ledger_health`)
  - `core/migrations/0396_s2965_golden_eval_evidence_source_ledger_health.py`
- **S2964 handoff:** `docs/handoffs/SESSION_2964_GOLDEN_EVALS_HARNESS_PR1.md`
- **S2964 shipped code:**
  - `core/models_golden_evals.py` (GoldenEvalRun)
  - `core/services/golden_evals/` (package: context + adapters + loader — extended at S2965)
  - `core/management/commands/run_golden_evals.py` — extended at S2965
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
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`) — updated at S2965 with #20 + #21.
- **Ledger #17 (S2957):** `db316865-d08c-4cc1-9d8e-cfac249e8c89` — Chat UI response-relay gap (unchanged this session)
- **Chat UI relay design task (S2957):** `f3f140f9-87bf-488b-8757-eab5d8058f45`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
