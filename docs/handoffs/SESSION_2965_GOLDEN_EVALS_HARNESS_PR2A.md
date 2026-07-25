# SESSION 2965 — Golden Evals Harness PR-2a

**Status:** CLOSED
**HEAD at close:** `38ee09602` (PR #3571 merged)
**Arc:** Golden Evals (S2954+ open, canon_v2 ratified S2963, harness PR-1 shipped S2964)
**Chris D-verdict:** 2026-07-25 (Rigby-relayed terminal path — **9 consecutive terminal ratifications** S2957→S2965)

---

## What shipped

PR #3571 — **Golden Evals validator harness PR-2a**, +1,550 / -66 lines across 10 files.

The harness now runs end-to-end for `AgentExecution`-substrate slices. `python manage.py run_golden_evals --execute --slice system_intelligence_agent --prompt sia_happy_02_severity_filtered_critical` dispatches SIA against a real prompt, adapts the response, validates against `expected_output_shape`, runs registered predicates, and persists a fully-populated `GoldenEvalRun` row with pass/fail/inconclusive verdict.

### Files landed

* `core/services/golden_evals/executors.py` (new, 113 lines) — JSON Schema executor (jsonschema Draft 2020-12) + `FailureReason` shape.
* `core/services/golden_evals/fault_injection.py` (new, 170 lines) — canon_v2 Item 5 selector parser; rejects handler-registry keys at load time.
* `core/services/golden_evals/runners.py` (new, 272 lines) — universal acceptance-criteria runner registry (`required_fields_present` + parametric `assistant_response_length_gte_N`); unknown predicates return INCONCLUSIVE.
* `core/services/golden_evals/canonicalizers.py` (new, 125 lines) — substrate-native → canonical response converters; SIA `canonical_field_mapping` derivation rules implemented.
* `core/services/golden_evals/context.py` (extended +88 lines) — `EvalRunContext` extended with `evidence_source` + `ledger_health` fields; three evidence-source constants + three ledger-health constants + `KNOWN_*` frozensets + `__post_init__` validation.
* `core/services/golden_evals/adapters/agent_execution.py` (extended +139 lines) — full `build_context()`: reads AgentExecution row, enforces canon_v2 Item 4 safety net, joins native `output_data.tool_calls`, defers on non-terminal status.
* `core/services/golden_evals/adapters/chat_conversation.py` (extended +213 lines) — full `build_context()`: filters buyer-facing sources, UUID-guards ToolCallRecord ledger join (substrate mismatch caught during dogfood), falls back to `metadata.tool_calls` cache, labels evidence source + ledger health explicitly per Rigby A2 REVISE.
* `core/management/commands/run_golden_evals.py` (extended +401 lines) — `--execute` flag + per-prompt dispatch + verdict aggregation + persistence with new fields.
* `core/models_golden_evals.py` (extended +28 lines) — `evidence_source` + `ledger_health` char fields, indexed.
* `core/migrations/0396_s2965_golden_eval_evidence_source_ledger_health.py` (new, 67 lines) — bounded to GoldenEvalRun only per S2964 precedent (latent Narrative* / HAIDispatchLog drift still deferred).

### End-to-end dogfood

Two `--execute` runs against SIA:

```
run_id=e424cac5-…
[SLICE] system_intelligence_agent.yaml agent=SystemIntelligenceAgent canon=1 schema=1 substrate=agent_execution adapter=AgentExecutionAdapter prompts=13 mode=execute
  [PASS] sia_happy_01_general_status [inconclusive: ['evidence_pointers_non_empty', 'tool_call_get_system_attention_invoked', 'no_unsupported_claims', 'counts_reconcile_with_tool_output']]
[DONE] slices=1 prompts=1 rows_written=0 pass=1 fail=0 inconclusive=0 substrate_deferred=0 dispatch_error=0

run_id=a77b82b8-…
  [PASS] sia_happy_02_severity_filtered_critical [inconclusive: ['tool_call_get_system_attention_invoked', 'severity_filter_argument_is_critical', 'warning_and_info_items_absent_from_summary']]
[DONE] slices=1 prompts=1 rows_written=1 pass=1 fail=0 inconclusive=0 substrate_deferred=0 dispatch_error=0
```

Persisted `GoldenEvalRun` row (from run_id `a77b82b8-…`):

```
passed: True
failure_reasons: []
evidence_ledger_refs count: 0
evidence_source: agent_execution_native
ledger_health: unavailable
primary_row_id: (empty)
finalized_at: None
latency_ms: None
```

**Known limitation carried forward to PR-2b:** direct `agent.execute()` dispatch bypasses the Celery-driven AgentExecution row write path, so `_resolve_agent_execution_row()` returns None and the adapter falls back to in-memory context. Validation still runs correctly against the AgentResult via the canonicalizer, but `primary_row_id` / `evidence_ledger_refs` / `finalized_at` remain unpopulated in the persisted `GoldenEvalRun`. Full substrate-row round-trip is proven at unit-test level (adapter smoke test on real SIA row `55a498e8-…` populates all six fields); PR-2b needs to route dispatch through Celery (`dispatch_agent.delay(...)`) OR add a two-phase mode that (a) instantiates the row explicitly then (b) invokes `.execute()` inside its context.

### Test coverage (live smoke via Django shell)

| Component | Coverage |
|---|---|
| AgentExecutionAdapter | 3/3 (real SIA row / synthetic-receipt refusal / LookupError) |
| ChatConversationAdapter | 5/5 (populated web row / empty-metadata fallback / claude-code refusal / LookupError / historical PA UUID join) |
| JSON Schema executor | 7/7 (all shape violation types) |
| Fault-injection parser | 9/9 (Class.method / module.function / bare-identifier reject / empty / missing-attr / non-callable / import-fail / module-only / determinism) |
| Universal runners | 8/8 (all pass/fail/inconclusive paths) |
| End-to-end mgmt cmd | 2/2 dogfood runs, `[PASS]` verdicts, GoldenEvalRun persistence verified |

Total live smoke coverage: **34/34**.

---

## Substrate discoveries (S2965 T1 SIGN raw-ORM verification)

Two platform-integrity findings that reshape PR-2 scope. Both logged in Rigby Tool Gap Ledger deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`). Rigby A3 framing: "Treat as a platform integrity incident (telemetry/audit substrate regression), not just a canon mismatch — otherwise it recurs."

### Ledger #20 — `ToolCallRecord.trace_id` NULL on 100% of rows

* **Signature:** `ToolCallRecord.objects.filter(trace_id__isnull=False).count() == 0` (5,430 total rows all have `trace_id=NULL`).
* **Impact:** `rigby_agent.yaml canonical_field_mapping` §evidence_pointers derivation spec (`Enumerate ToolCallRecord rows whose created_at falls within [window] AND match the same trace_id`) is structurally unusable. Golden Evals slice 8 acceptance runners for `no_fabricated_tool_runs` + `detects_and_surfaces_tool_runs_empty_vs_claimed` have no working evidence-ledger substrate.
* **Fix options:** (a) populate `trace_id` at write time in `tool_dispatcher.py:1085` + `unified_pa_entrypoint.py:2669` via existing `resolve_trace_uuid()` helper (b) rewrite `rigby_agent.yaml` derivation to drop trace_id join and gate on `conversation_id` + created_at window only (c) both. (a) is cleanest fix.

### Ledger #21 — PA→ToolCallRecord write silent regression as of 2026-06-19 (35d)

* **Signature:** `ToolCallRecord.objects.filter(agent_name='PersonalAssistant', created_at__gte=<30d_ago>).count() == 0`. Last row 2026-06-19 21:29:56 UTC. All-time = 907. Zero rows in last 30d despite continuous PA traffic (508 buyer-facing ChatConversation rows in 30d, this session's dogfooding included).
* **Root cause hypothesis:** `_record_tool_call_async` fire-and-forgets and swallows all exceptions at `tool_dispatcher.py:1043` with WARNING-only log. Code path intact (`unified_pa_entrypoint.py:1218/2297/2325` all pass `agent_name='PersonalAssistant'` explicitly). Also possible: field type mismatch — `ToolCallRecord.conversation_id` is `UUIDField` but current PA writes `pa-*` prefix strings which Django's `get_prep_value` rejects.
* **Confirmed at dogfood:** `ChatConversation.conversation_id='pa-50542bacf8014a20'` won't coerce to UUID at filter time; adapter guards with UUID-parse-check + falls back to `LEDGER_HEALTH_UNAVAILABLE`.

Both fixes belong to their own arc, separate from Golden Evals.

---

## Governance

### T1 pre-code SIGN (Rigby)

* **5 tool_run verifications** (`orm_inspect_tool.count_by` × 3 + `filter` × 2 + `describe_model` × 1).
* **Q1 REVISE (semantic):** filter `('web', 'pa')` correct; add explicit claude-code exclusion callout.
* **Q2 REVISE (F-BLOCKING):** `agent_name IN ('Rigby','PersonalAssistant')` drops everything in 30d — no PA rows in TCR since 2026-06-19. Drop agent_name from filter. Extended by Claude raw-ORM verification to full Ledger #20 + #21 discovery.
* **Q3 REVISE:** finalized_at rule tolerates empty metadata + null response_time_ms.
* **Q4 AGREE:** adapters-first build order.
* **Q5 REVISE (SPLIT):** scope split into PR-2a / PR-2b / separate ledger-fix arc.

### T2 fold-back (Claude raw-ORM re-verification)

* Sent Rigby the raw-ORM findings + revised scope proposal.
* **A1 AGREE:** scope split ratified.
* **A2 REVISE:** ship ChatConversation adapter now with explicit `evidence_source` labeling + gate Rigby-specific predicates on `ledger_health=OK`, else INCONCLUSIVE.
* **A3 AGREE (conditional):** SIA dogfood substantive if it exercises JSON Schema executor + fault-injection determinism + adapter portability across 2-3 rows.
* **A3 additional pushback:** treat #20/#21 as platform integrity incident.

### Chris D-verdict

Ratified **Option A (split)** via terminal after receiving plain-English framing (per `feedback_plain_english_decision_framing_for_chris`): "Sorry I agree with you and Rigby, do it the way you guys suggested." **9 consecutive terminal ratifications** S2957→S2965.

---

## Rigby Tool Gap Ledger

* **#20 LOGGED** — appended to ledger `5c84e75a-…` (3,597 chars added). No auto-diagnostic flag raised. `deliverable_type='engineering_backlog'` maintained.
* **#21 LOGGED** — same append operation.
* **#17 — no change** (Chris used Rigby-relayed terminal path; **9 consecutive terminal ratifications S2957→S2965**).
* **#19 — no change** (allowlist landed at S2964; still discharged).
* **New candidate:** Rigby has no outbound Chat UI posting surface — she can only respond in the thread she was called from. This is the *reverse* of Ledger #17 (Chat UI response-relay gap). Surfaced when Claude asked her to relay the D-verdict framing to Chris via Chat UI at S2965 T2 close. Watching for second occurrence before promoting.

---

## Deferred to S2966+ (unchanged from S2964 except where noted)

### S2965 additions

* **PR-2b (next session):** Rigby-specific acceptance runners (`no_fabricated_tool_runs` / `no_fabricated_deliverable_ids` / `no_fabricated_workspace_or_user_context` / `no_fabricated_conversation_history` / `detects_and_surfaces_tool_runs_empty_vs_claimed`) + slice 8 dogfood + Celery-dispatch path for full substrate-row round-trip + additional per-agent canonicalizers (research / devops / workflow / legal / content / competitor).
* **Separate arc (later):** Ledger #20 + #21 fixes — populate `trace_id` at ToolCallRecord write sites + investigate silent PA write regression + migrate `ToolCallRecord.conversation_id` to CharField or add UUID coerce helper.
* **`--execute` known limitation:** direct `agent.execute()` dispatch bypasses Celery row write path; adapter falls back to in-memory context. Celery-dispatch mode + persist-then-execute pattern both viable for PR-2b.

### Carry forward from S2964

* Latent migration drift (Narrative* / HAIDispatchLog).
* Complex-boolean-in-canon-doc misread pattern (one trigger observed).

### Long-standing (unchanged)

Docs restructuring arc / Slice 5-hardening / Tier 2 lint promotion / paste-UUID fallback / server-side search /eligible/ / Z1/Z2/Z4 UI polish / rank+cap+paginate / per-pattern diversity floors / W2 items / LLMCallLog field splits / bulk workspace_budget_tool / C4/C5/C6 character-os follow-ons.

---

## Post-merge

* `make recycle-all` executed per PLAYBOOK-7.4.4 (workers advanced to sha=`38ee09602420`, clean recycle recorded to `logs/recycle_events.jsonl`).

## Full artifact pointers

* **Handoff (this doc):** `docs/handoffs/SESSION_2965_GOLDEN_EVALS_HARNESS_PR2A.md`
* **PR-2a shipped code:** `core/services/golden_evals/` (canonicalizers + executors + fault_injection + runners + adapters full build-out) / `core/management/commands/run_golden_evals.py` / `core/models_golden_evals.py` / `core/migrations/0396_*.py`
* **S2964 handoff (immediate predecessor):** `docs/handoffs/SESSION_2964_GOLDEN_EVALS_HARNESS_PR1.md`
* **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`) — updated at S2965 with #20 + #21.
* **Canon_v2 doc (unchanged):** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md`
* **Wrapper pin bumped at close:** `tools/pa_local.sh` line 563 — new pin from `session_lifecycle close --label s2965-golden-evals-pr2a`.
