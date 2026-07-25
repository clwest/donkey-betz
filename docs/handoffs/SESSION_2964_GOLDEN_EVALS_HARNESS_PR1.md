# Session 2964 — Golden Evals validator harness PR-1 (foundation)

**Session:** 2964
**Closed:** 2026-07-25 (Chris `Proceed with close` via Rigby after joint Claude+Rigby PR-shape agreement)
**Arc:** Golden Evals (S2954 open → S2963 arc-close ratified canon_v2 → **S2964 harness code opens**)
**HEAD at open:** `882626d8f`
**HEAD at close (this session's merged code):** `137410e86`

---

## 1. What this session shipped

**One PR merged:**

- u-d-b **PR #3569** — `feat(s2964): Golden Evals validator harness — canon_v2 Item 1 allowlist + EvalRunContext scaffold`. 12 files / **+921 lines**. Squash-merged with `--admin` per memory rule (CI billing blocked).

**Session goal:** open the S2963-arc-close-ratified validator harness with the smallest reviewable slice that (a) lands canon_v2 Item 1 as executable code so Rigby's own eval substrate is inspectable via her tool surface, and (b) proves the two-substrate abstraction (canon_v2 Item 6) actually normalizes across `AgentExecution` and `ChatConversation` slices without executor logic in the way.

### Files added (10 new)

1. `core/models_golden_evals.py` — `GoldenEvalRun` model (satellite in `core`, parallel to `models_tool_calls.py` precedent). Mirrors `EvalRunContext` shape 1:1.
2. `core/migrations/0395_s2964_golden_eval_run.py` — bounded migration (see §5 for scope note).
3. `core/services/golden_evals/__init__.py` — package marker + shortcut exports.
4. `core/services/golden_evals/context.py` — `EvalRunContext` dataclass + `KNOWN_SUBSTRATES` constants + validation.
5. `core/services/golden_evals/adapters/__init__.py` — `ADAPTER_REGISTRY` mapping.
6. `core/services/golden_evals/adapters/base.py` — abstract `SubstrateAdapter` ABC with subclass validation.
7. `core/services/golden_evals/adapters/agent_execution.py` — `AgentExecutionAdapter` + `exclude_synthesized_pa_receipts()` canon_v2 Item 4 helper.
8. `core/services/golden_evals/adapters/chat_conversation.py` — `ChatConversationAdapter` + `filter_to_buyer_facing_sources()` canon_v2 Item 2 helper.
9. `core/services/golden_evals/loader.py` — YAML discovery + parse + substrate-type validation at load time.
10. `core/management/commands/run_golden_evals.py` — mgmt cmd (dry-run default).

### Files modified (2)

- `core/services/td_handlers_agents.py` — canon_v2 Item 1 code: `_MODEL_POLICIES` **14 → 16 models** (`ChatConversation` + `ToolCallRecord`).
- `core/models/__init__.py` — register `GoldenEvalRun` for Django app discovery.

## 2. Canon_v2 bindings actually shipped as code

| canon_v2 Item | Shape at S2963 | Landed at S2964 PR-1 |
|---|---|---|
| 1 — `orm_inspect_tool` allowlist | Code, this session | ✅ 14 → 16 models (`ChatConversation`, `ToolCallRecord`). Verified live post-merge via Rigby probes. |
| 2 — source stratification | Doc-only + adapter default | ✅ `filter_to_buyer_facing_sources()` named function in `ChatConversationAdapter`; default `('web', 'pa')` matches `rigby_agent.yaml:78`. |
| 3 — opt-in `latency_ms` evidence class | Doc-only + `EvalRunContext.latency_ms` field | ✅ `EvalRunContext.latency_ms: int \| None` with docstring semantics. Adapters populate opt-in; no universal promotion. |
| 4 — receipt-contamination predicate | Doc-only + harness utility | ✅ `exclude_synthesized_pa_receipts()` named function in `AgentExecutionAdapter` module. Docstring cites S2963 ratification. |
| 5 — fault-injection selector convention | Doc-only + parser at S2964 | ⏭ Deferred to PR-2 (fault-injection parser not yet needed for dry-run skeleton). |
| 6 — `EvalRunContext` shape | Doc-only + Python API at S2964 | ✅ `EvalRunContext` dataclass with `__post_init__` validation against `KNOWN_SUBSTRATES`. Both adapters yield this shape. |

**Zoom-out guardrail from Rigby S2964 T1 SIGN Q5 (not a canon_v2 item, but same-PR guardrail):** substrate identity is expressed as `SUBSTRATE_AGENT_EXECUTION` + `SUBSTRATE_CHAT_CONVERSATION` module-level constants, never as ad-hoc strings. YAML loader validates against `KNOWN_SUBSTRATES` at load time; `EvalRunContext.__post_init__` re-validates; `GoldenEvalRun.substrate_type` writes route through the same constants. Adding a new substrate requires (a) constant, (b) adapter, (c) registry entry — all three enforced by import-time errors.

## 3. What verified live (post-merge, post-recycle)

Recycle: `make recycle-all` post-merge (per PLAYBOOK-7.4.4). Emitted `[emit_recycle_event] clean recycle recorded (sha=137410e8612e, surviving=none)`.

Rigby dogfood dispatches (3 tool_runs, tool-grounded):

**Probe 1 — `orm_inspect_tool` on `ChatConversation`:** PASS. Returned 3 real rows filtered to `source__in=['web', 'pa']`, `order_by=-created_at`. Latest row id=4638 from 2026-07-25 17:39 UTC. **Canon_v2 Item 1 half A verified live.**

**Probe 2 — `orm_inspect_tool` on `ToolCallRecord`:** PASS mechanically (`ok: true`, `action: filter`, no allowlist error) but 0 rows returned for `where.agent_name='Rigby'`. Follow-up `count_by` on the same model returned **5,426 rows / 21 distinct `agent_name` values**. **Canon_v2 Item 1 half B verified live.** See §4 for the naming surprise.

**Probe 3 — `run_golden_evals --slice rigby_agent` via `claude_code_tool`:** Dispatched OK (task_id `71ba5189-a5d8-48e6-9e27-d5ba7c968265`, execution_id `418a3840-0eeb-46ad-b677-9915d5092b93`). Completed 46s later (`created_at 18:17:56` → `completed_at 18:18:42`) with no error. **Caveat (per Rigby SIGN):** `agent_job_status` returned `duration_ms: null` + `output_preview: null` — task completion is observable but the harness stdout was not captured through the async worker's Claude Code dispatch path. Also: `claude_code_tool` is `request_mode='answer'`, so it dispatches a Claude Code agent that plans/answers rather than executing the shell command directly — the mgmt cmd's actual harness output was not the goal here. **Local Python subprocess run (§4 below) is the authoritative end-to-end verification.**

Local end-to-end (pre-commit sanity, pre-recycle):

- Migration `0395_s2964_golden_eval_run` applied cleanly (Django reported `Applying core.0395_s2964_golden_eval_run... OK` on top of 0394).
- `python manage.py run_golden_evals` discovered **all 8 Tier-1 slices**: 91 AgentExecution prompts (13 × 7) + 18 ChatConversation prompts (slice 8, rigby_agent) = **109 total**.
- **Slice 8 (`rigby_agent.yaml`) correctly routed to `ChatConversationAdapter`**; other 7 routed to `AgentExecutionAdapter`. Two-substrate abstraction verified without executor logic.
- **109 `GoldenEvalRun` rows persisted** with `substrate_type` + `prompt_id` + shared `run_id`, `passed=NULL` (skeleton dispatch). Rows deleted before commit; post-merge dogfood didn't reproduce them because the async worker used `claude_code_tool`, not direct shell dispatch (see Probe 3 caveat).

## 4. Surprises + gotchas surfaced

**`agent_name='PersonalAssistant'`, not `'Rigby'`, in `ToolCallRecord`.** `orm_inspect_tool action=count_by field=agent_name model=ToolCallRecord limit=20` returned:

```
ResearchAgent: 2730
PersonalAssistant: 907   ← ← Rigby PA turns land here
TrendAnalysisAgent: 435
COOAgent: 247
MarketAnomalyDetectorAgent: 99
CompetitorAnalysisAgent: 93
(15 more)
```

The `rigby_agent.yaml` header line 383-385 anticipated this ("agent_name identifies which agent invoked the tool — for Rigby turns this is typically 'Rigby' or 'PersonalAssistant', but may be an internal sub-agent name if Rigby delegated"). **PR-2 impact:** `ChatConversationAdapter.build_context()` must join `ToolCallRecord` rows with `agent_name IN ('Rigby', 'PersonalAssistant')` — a single-name filter will miss ~90% of the evidence.

**`agent_job_status` reports null duration/preview after clean completion.** Probe 3's Celery task reported `completed_at` populated + no `error_message` but `duration_ms=null` + `output_preview=null`. Two possibilities: (a) `claude_code_tool` doesn't wire stdout capture into the execution record; (b) `duration_ms` is only derived from a specific event path we skipped. **PR-2 impact:** if the harness will run inside the async worker (as Golden Evals nightly-beat needs), stdout capture + duration derivation need to work end-to-end. Log to Rigby Tool Gap Ledger as a candidate; may or may not be Ledger-worthy depending on whether `claude_code_tool` is the intended dispatch surface for `run_golden_evals` at S2965.

**Latent migration drift.** `python manage.py makemigrations core --name s2964_golden_eval_run` auto-bundled unrelated changes for `Narrative*`, `NarrativeAlert`, `NarrativeEvidence`, `NarrativeShift`, and dozens of `HAIDispatchLog` `AlterField` operations. Migration 0395 was rewritten by hand to include only the `GoldenEvalRun` `CreateModel` + 3 `AddIndex` ops. **The latent drift is a real repo-hygiene finding but out of scope for PR-1**; belongs in its own remediation PR (add to deferred queue).

## 5. Rigby SIGN cycle

**T1 pre-code SIGN (5 tool_runs, tool-grounded):** Rigby verified my proposed PR-1 shape via `repo_tool.read_file` on `td_handlers_agents.py`, `models/conversations/models.py`, `models_tool_calls.py`; `repo_tool.search` on model class definitions; and `search_docs` on canon_v2 references. Per-question verdicts:

| Q | Verdict | Notes |
|---|---|---|
| Q1 — Package location (`core/services/golden_evals/` vs new app) | AGREE | Minimizes wiring surface for PR-1 foundation. |
| Q2 — `GoldenEvalRun` app assignment | AGREE | `ToolCallRecord` precedent verified via file read + `db_table='core_tool_call_record'`. |
| Q3 — Allowlist `expensive_text_fields` | REVISE (minor) | My choices confirmed correct via field reads; optional `session_title` note not adopted (CharField(200), low risk). |
| Q4 — PR-1 scope size (skeleton vs skeleton+executor) | AGREE | Skeleton-only makes dogfood crisp; executor bundled in makes correctness debug entangled. |
| Q5 — ZOOM-OUT (per S2771 rule) | REVISE (structural) | **Substrate-type stringly-typed coupling is the #1 architectural risk.** Recommended canonical constant set. Also: keep receipt-contamination as a named function with canon_v2 Item 4 docstring pointer even in PR-1, to prevent "helpful refactor" drift in S2965+. |

**Both Q5 REVISE recommendations folded into PR-1** — `KNOWN_SUBSTRATES` constants at `context.py` + `SUBSTRATE_*` module-level constants; `exclude_synthesized_pa_receipts()` + `filter_to_buyer_facing_sources()` as named canon-documented functions. Zero rubber-stamp signal.

**T2 post-code:** Rigby dogfood dispatches (Probes 1/2/3 above) + naming-surprise verification via `count_by` + close-readiness confirmation.

**Chris D-verdict:** `Proceed with close` via Rigby (2026-07-25, terminal-route summary → Rigby-relayed approval). Chris added one refinement: include the Probe 3 caveat explicitly in this handoff. Done in §3.

## 6. What's next — S2965 open

**First-action = PR-2 (executors + acceptance runners + fault-injection parser).** Scope:

1. **JSON Schema executor** — validate agent responses against `expected_output_shape` blocks in each YAML slice.
2. **Pydantic acceptance-criteria runners** — starter set:
   - `required_fields_present` (universal)
   - `no_unsupported_claims` (universal)
   - `no_fabricated_tool_runs` + `no_fabricated_deliverable_ids` + `no_fabricated_workspace_or_user_context` + `no_fabricated_conversation_history` (Rigby-specific per rigby_agent.yaml §252-259)
   - `assistant_response_length_gte_N` (parametric)
   - `one_of` branch dispatcher
3. **Fault-injection selector parser (canon_v2 Item 5)** — deterministic resolver for `module.Class.method` + `module.function`. Errors loudly on handler-registry keys per canon forbid.
4. **`AgentExecutionAdapter` + `ChatConversationAdapter` full build-out** — replace skeleton `build_context()` with real substrate reads that:
   - Apply `exclude_synthesized_pa_receipts()` on AgentExecution.
   - Apply `filter_to_buyer_facing_sources()` on ChatConversation.
   - Join `ToolCallRecord` rows via `trace_id` + `created_at` window with `agent_name IN ('Rigby', 'PersonalAssistant')` for ChatConversation adapter (per §4 surprise).
   - Derive `finalized_at` from substrate-specific semantics (AgentExecution.completed_at + status; ChatConversation.response_time_ms populated + assistant_response non-empty).
5. **Real dispatch flag** — `--execute` (or removing `--dry-run` default) so the harness actually invokes the agent-under-test and evaluates.

**Estimated 1-2 sessions for PR-2.** Then S2966+ handles nightly beat + pass-rate drift dashboard.

## 7. Deferred queue additions this session

- **Latent migration drift** (Narrative*, HAIDispatchLog AlterField pile). Out of scope for PR-1; needs its own remediation PR.
- **`claude_code_tool` stdout / duration_ms capture gap** (Probe 3 caveat). May promote to Ledger #NN if PR-2 wants `claude_code_tool` as the harness dispatch surface.
- **`ChatConversationAdapter.build_context()` must handle `agent_name IN ('Rigby', 'PersonalAssistant')`** — actionable, tracked in §6 Item 4.

## 8. Pointers

- **PR:** https://github.com/clwest/donkey-betz-platform/pull/3569
- **Merged SHA:** `137410e86` on `main`
- **Canon_v2 ratification doc:** `docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md`
- **Slice 8 substrate reference:** `evals/tier1/rigby_agent.yaml`
- **Prior handoff:** `docs/handoffs/SESSION_2963_GOLDEN_EVALS_ARC_CLOSE_CANON_V2.md`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **Ledger #19 (this session's discharge):** RATIFIED as canon_v2 Item 1, code landed in PR #3569.
