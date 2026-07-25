# SESSION 2966 — Golden Evals Harness PR-2b

**Status:** CLOSED
**HEAD at close:** `76710a425` (PR #3573 merged)
**Arc:** Golden Evals (S2954+ open, canon_v2 ratified S2963, harness PR-1 S2964, PR-2a S2965)
**Chris D-verdict:** 2026-07-25 (terminal — **10 consecutive terminal ratifications** S2957→S2966)

---

## What shipped

PR #3573 — **Golden Evals validator harness PR-2b**, +1,596 / -175 lines across 3 files.

Closes the S2965 PR-2a known limitation (direct `agent.execute()` bypassed AgentExecution row write path) and adds the Rigby-specific fabrication predicate surface + first `ChatConversation`-substrate real dogfood. `python manage.py run_golden_evals --execute --slice rigby_agent --prompt rigby_happy_07_platform_verification_ping_railway` now dispatches Rigby via the canonical PA task write path, adapts the resulting `ChatConversation` row into an `EvalRunContext`, canonicalizes the response, validates predicates (with ledger-health gating), and persists a fully-populated `GoldenEvalRun` row.

### Files landed

* `core/services/golden_evals/runners.py` (+655 lines) — 6 Rigby-specific predicates (`no_fabricated_tool_runs` / `no_fabricated_deliverable_ids` / `no_fabricated_workspace_or_user_context` / `no_fabricated_conversation_history` / `detects_and_surfaces_tool_runs_empty_vs_claimed` / `no_unsupported_claims`) + `one_of` branch dispatcher + `substrate_row` kwarg + governing-principle module docstring ("maximum signal with degraded labels").
* `core/services/golden_evals/canonicalizers.py` (+598 lines) — 7 new per-agent canonicalizers (Research / DevOps / Workflow / Legal / Content / Competitor / Rigby). Each mirrors its slice YAML `canonical_field_mapping` derivation_rule verbatim so authoring drift shows up as a canonicalizer divergence.
* `core/management/commands/run_golden_evals.py` (+518 lines) — `AgentRouter.route()` dispatch pathway + marker-based row resolver (`input_data.context._golden_evals_run_id`) + `ChatConversation` dispatch branch (`process_pa_chat_task.apply().get()`) + shared `_validate_and_wrap` + `_SynthesizedChatRow` fallback.

### End-to-end dogfood verified

Three `--execute` runs across three substrate/agent pairings:

```
# SIA (AgentExecution) — S2965 primary_row_id gap CLOSED
run_id=b3972a7c-e095-422a-8d85-346a3db0e707
[PASS] sia_happy_02_severity_filtered_critical
GoldenEvalRun row: passed=True primary_row_id='4cd44d35-a9f6-4e07-ab26-8399b1c29090'
  evidence_source=agent_execution_native ledger_health=ok
  finalized_at=2026-07-25T19:28:52.371608+00:00 latency_ms=19023
  evidence_ledger_refs count=1

# Rigby (ChatConversation) — first slice 8 real dogfood
run_id=c7744461-a0c0-4920-8d52-34805707789b
[PASS] rigby_happy_07_platform_verification_ping_railway
GoldenEvalRun row: passed=True primary_row_id='4652'
  evidence_source=metadata_cache ledger_health=unavailable
  finalized_at=2026-07-25T19:29:45.789215+00:00
  evidence_ledger_refs count=2
ChatConversation row 4652: source=web platform=web
  user_message length=10 assistant_response length=282
  intent=system_overview tool_calls count=1 tool_results count=1
  response_time_ms=10409

# Research (AgentExecution) — multi-agent router path smoke
run_id=4f30d46d-949b-49d4-8018-a7505194c318
[PASS] research_bad_01_empty_task
```

Plus a full dry-run across all 8 slices / 109 prompts: zero regressions.

### Test coverage (live smoke via `--execute` + shell)

| Component | Coverage |
|---|---|
| runners.REGISTRY (7 named + parametric + one_of) | Loaded + smoke-tested |
| canonicalizers.REGISTRY (8 agents) | Loaded + smoke-tested with fake AgentResults |
| AgentRouter.route() dispatch (SIA, Research) | 2/2 end-to-end PASS |
| process_pa_chat_task.apply() dispatch (Rigby) | 1/1 end-to-end PASS with real ChatConversation write |
| Ledger-gating behavior (`no_fabricated_tool_runs` under unhealthy ledger) | INCONCLUSIVE returned, not FAIL — matches Rigby A2 REVISE |
| one_of aggregation (any-pass / all-inconclusive / mixed-fail) | 3/3 paths exercised |
| Full dry-run (8 slices / 109 prompts) | 109/109 rows written, 0 errors |

Total live smoke coverage: **12/12** verifications.

---

## Governance

### T1 pre-code SIGN (Rigby)

* **10 tool_run verifications** (repo_tool git_info, class search, def route read, mgmt cmd read × 2, runners read × 2, canonicalizers.REGISTRY read).
* **D1 dispatch pathway:** Claude discovered a third option (C = `AgentRouter.route()`) beyond the two 00-START-listed options (A Celery / B two-phase). Rigby SIGN **AGREE C** with required tweak: marker MUST go in raw context dict (persisted at `input_data['context']` per `agent_router.py:2832-2838`).
* **D2 slice 8 dispatch:** Rigby SIGN **B** (HTTP client) with C (inline replicate) as fallback. Claude then discovered a third option — `process_pa_chat_task.apply().get()` synchronous variant — which delivers B's canonical write-path coverage with C's zero-external-dep footprint. Shipped that variant.
* **D3 predicate signature:** **AGREE (a)** add `substrate_row: Any = None` kwarg.
* **D4 one_of aggregation:** **AGREE** aggregation rules with REVISE nuance — mixed FAIL + INCONCLUSIVE with no PASS resolves to FAIL (not INCONCLUSIVE).
* **D5 ledger gating:** **AGREE 3 non-gated** + **AGREE (b) partial-downgrade** for `no_fabricated_deliverable_ids`.
* **Zoom-out ratification:** governing principle = maximum signal with degraded labels over maximum correctness. Rationale: keeps regressions visible during infra churn instead of masking under perpetual inconclusive counts.

### T2 post-code SIGN (Rigby)

* **10 tool_run verifications** — orm_inspect of SIA row (owner_agent=SystemIntelligenceAgent + `_golden_evals_run_id=b3972a7c` marker present in input_data.context) + orm_inspect of ChatConversation row 4652 + read canonicalizers.REGISTRY (8 entries confirmed) + read runners.REGISTRY (7 named entries confirmed) + db_health_tool.verify_table on `core_golden_eval_run` (112 rows).
* All factual claims verified.

### Chris D-verdict

Ratified `Yes` via terminal after plain-English framing (Q1 "do we lose anything?" / Q2 "is it more work later?" per `feedback_plain_english_decision_framing_for_chris`). **10 consecutive terminal ratifications** S2957→S2966.

---

## Rigby Tool Gap Ledger

* **#20 — no change** (`ToolCallRecord.trace_id` NULL on 100% of rows). Fix in separate arc.
* **#21 — no change** (PA→ToolCallRecord write silent regression 2026-06-19+). Fix in separate arc.
* **#17 — no change** (Chris terminal path continues; 10 consecutive terminal ratifications S2957→S2966).
* **#19 — no change** (allowlist landed S2964; still discharged).
* **Rigby outbound-messaging gap candidate** — retriggered this session when Claude routed "Chris D-verdict framing" to Rigby via PA chat; Rigby doesn't relay to Chris Chat UI. Claude moved framing to terminal output. **Second trigger observed** (first at S2965 T2 close). Promoted from candidate to logged ledger entry candidate → next session should append.

---

## Deferred to S2967+

### S2966 additions

* **Named per-slice predicates** — SIA-specific (`tool_call_get_system_attention_invoked` etc.), Rigby-slice-specific (`assistant_response_contains_all_10_named_articles` etc.), and other agent-specific predicates return INCONCLUSIVE. Deferred to per-slice PRs after this shape ships.
* **S2965 known limitation CLOSED** — `primary_row_id` populated end-to-end via AgentRouter dispatch.
* **Rigby outbound-messaging gap** — second trigger observed; log to ledger next session.

### Carry forward from S2965

* **Separate arc** — Ledger #20 + #21 code fixes (populate `trace_id` at ToolCallRecord write sites + investigate PA write regression).

### Carry forward from S2964

* Latent migration drift (Narrative* / HAIDispatchLog).
* Complex-boolean-in-canon-doc misread pattern (one trigger observed).

### Long-standing (unchanged)

Docs restructuring arc / Slice 5-hardening / Tier 2 lint promotion / paste-UUID fallback / server-side search `/eligible/` / Z1/Z2/Z4 UI polish / rank+cap+paginate / per-pattern diversity floors / W2 items / LLMCallLog field splits / bulk workspace_budget_tool / C4/C5/C6 character-os follow-ons.

---

## Post-merge

* `make recycle-all` executed per PLAYBOOK-7.4.4 (workers advanced to sha=`76710a425…`).

## Full artifact pointers

* **Handoff (this doc):** `docs/handoffs/SESSION_2966_GOLDEN_EVALS_HARNESS_PR2B.md`
* **PR-2b shipped code:** `core/services/golden_evals/runners.py` (655 new lines) / `core/services/golden_evals/canonicalizers.py` (598 new lines) / `core/management/commands/run_golden_evals.py` (518 new lines).
* **S2965 handoff (immediate predecessor):** `docs/handoffs/SESSION_2965_GOLDEN_EVALS_HARNESS_PR2A.md`
* **Canon_v2 doc (unchanged):** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md`
* **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`) — no delta this session (Ledger #20+#21 fixes deferred to separate arc).
* **Wrapper pin bumped at close:** `tools/pa_local.sh` line 563 — new pin from `session_lifecycle close --label s2966-golden-evals-pr2b`.
