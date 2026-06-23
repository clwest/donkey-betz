# Session 1209 — Universal Receipt Contract (URC v0.1) envelope + router-path coverage

**Status:** Both PRs merged. Fleet smoke verified 52/52 URC envelope coverage live (vs 0/21 router-path baseline). Rigby filed the smoke report; Session 1209 closes clean.
**Date:** 2026-06-23 (extended past midnight UTC from Session 1208 close)
**Active conversation:** `pa-61c7b47d201d4591` — Rigby's `session_tool create_fresh` at Session 1209 open. Pinned in `tools/pa_local.sh`. Prior thread `pa-2d74e36cc3a04787` (Session 1208 + URC design discussion + Fleet Smoke Report `c5ccf3b1-…`) retired as the design-anchor record.
**Prior session:** [`SESSION_1208_CAMPAIGN_ORCHESTRATOR_OUTBOUND_PACK_HARDENING.md`](./SESSION_1208_CAMPAIGN_ORCHESTRATOR_OUTBOUND_PACK_HARDENING.md).
**Next session entry point:** Session 1210 — natural candidates listed in §"Open follow-ups" below. 24h watches: Session 1207 MIC (already fired ~03:50 UTC), Session 1208 Outbound (fires ~04:45 UTC this session), Session 1209 URC (arms ~13:10 UTC 2026-06-24).

## TL;DR

Shipped **Universal Receipt Contract (URC) v0.1** — runner-level enforcement of a uniform `output_data` envelope across every agent execution. Spec deliverable `6f09233c-c984-4303-87c4-e67b94390030` on Initiative `29154d73-…` (Platform Capability Audit) defines §1-§6 contract; Q1-Q5 locked on `pa-61c7b47d201d4591`.

**Two PRs (#2473 + #2474), 4 implementation commits + 1 doc-fix commit, all five live-verified at each step:**

- **PR #2473** (Phase A+C inline at `tasks_agents.execute_agent_task` writeback): every celery-task-dispatched agent emits URC envelope; ContentWriterAgent under `mode=receipt_only` correctly flips to `contract_violation`. 39 unit tests.
- **PR #2474** (extracted helpers to shared module + extended to router path): WorkflowAgent's sub-dispatches (which go through `agent_router._complete_execution` synchronously) now emit the same envelope. + raw context propagation to `input_data['context']` so Phase C predicate works on both paths. 20 additional unit tests (59 total).

**Fleet smoke post-merge:** 52/52 rows with full URC envelope (vs 0/21 on the router path pre-fix). 39 success, 12 error, 1 contract_violation — distribution matches expectations.

## Session Manifest

### PRs merged

| # | Title | Commits (squashed) | Files | Verified |
|---|---|---|---|---|
| **#2473** | feat(session-1209-urc): Universal Receipt Contract v0.1 envelope + receipt_only contract_violation | `16fc964e` (pa_local.sh repin) + `3ec5634d` (URC impl + 39 tests) + `f637f90c` (Rigby review nits) + `b3ce6014` + `ac8835d2` (00-START context-kit headline trap fix) | `core/tasks_agents.py` (+131), `core/tests/test_urc_v01_envelope.py` (+253), `tools/pa_local.sh` (+10/-7), `00-START-NEXT-SESSION.md` (-1/+1) | ✅ live x3 (TopicMinerAgent `6584ebb8-…` success; ContentWriterAgent `a14d4c7c-…` receipt_only → contract_violation; CodeReviewAgent `ca48e3fe-…` success post-restart) — squash merged as `3d95aea9` |
| **#2474** | fix(session-1209-urc): extend URC v0.1 envelope to agent_router synchronous dispatch path | `d855d6da` (extraction + router patch + context propagation + 20 tests) | `core/services/urc_envelope.py` (+192 new), `core/agent_router.py` (+80/-2), `core/tasks_agents.py` (+47/-123 refactor), `core/tests/test_urc_envelope_module.py` (+343 new) | ✅ live x2 (TopicMinerAgent `014bf944-…` router-path success; TopicMinerAgent `4e8c59d8-…` router-path receipt_only → contract_violation) + ✅ fleet smoke 52/52 URC envelope coverage — squash merged as `7669a249` |

### Deliverables filed / touched

| ID | Action | Note |
|---|---|---|
| `6f09233c-c984-4303-87c4-e67b94390030` | **NEW (spec)** | URC v0.1 §1-§6 spec (12,136 chars). Created via Rigby `deliverable_tool action=create` + 3 appends (auto-split for tool payload limits). Q1-Q5 locked verbatim in §6. Linked to Initiative `29154d73-…`. Pattern follows ecddb62d-… precedent (Session 1208 CampaignOrchestrator spec). |
| `1a8cde69-8f40-45d2-b841-4e88f76c9d7f` | **NEW (smoke evidence)** | Rigby-filed post-router-patch fleet smoke report. Category `Platform Diagnostics`, pinned. 52/52 URC envelope coverage; 39 success / 12 error / 1 contract_violation; ContentWriterAgent receipt_only correctly classified; CodeReviewAgent ×4 stay 'error' as expected. |
| `c5ccf3b1-…` | **CONSUMED (Session 1208 baseline)** | Original fleet smoke report that surfaced the need for URC enforcement. Status remains as filed; the report's "receipt-only compliance is not enforceable by prompt alone" finding is now closed by PRs #2473 + #2474. |

Initiative `29154d73-…` (Platform Capability Audit) holds both the spec and the smoke evidence on `kind=investigation` rows.

## Behavioral invariants — what's now true post-merge

1. **Every AgentExecution row created by either dispatch path lands a uniform top-level URC envelope.** The 8 required keys are present on success, error, timeout, skipped, and contract_violation outcomes:
   - `agent_name: str` — always set
   - `run_status: str` — one of `{success, error, timeout, skipped, contract_violation}` per §4 precedence
   - `latency_ms: int|None` — mirrors `execution_time_ms`
   - `error_signature: str|None` — null on success/skipped; normalized first-line (UUIDs/long-hex masked, ≤80 chars) on error/timeout; synthetic `'RECEIPT_CONTRACT_VIOLATION: <predicate>'` on contract_violation
   - `error_message: str|None` — null on success/skipped; populated otherwise
   - `artifacts: list[obj]` — minimal v0 list of `{type, id}` mirrors of explicit `deliverable_id`; empty list when no artifacts
   - `warnings: list[obj]` — always a list; extends PR #2469 convention with optional `meta`
   - `completed_at: str` (ISO) — set at writeback time

   `started_at: str` (ISO) is optional — emitted only when the agent's path called `execution_record.start_execution()`. Many agents never do; absence is documented behavior, not a bug.

2. **`run_status` precedence is enforced in this exact order:** `skipped > timeout > error > contract_violation > success`. Q5 defensive lock: non-empty `result.error` forces `'error'` regardless of `success` bool. Real crashes cannot be masked by contract failures.

3. **Phase C: receipt_only contract violation classification.** When `AgentExecution.input_data['context']['mode'] == 'receipt_only'` AND the agent's raw payload (`result.data` / `output_data['data']`) fails the v0 receipt schema (dict + `status ∈ {ok, skipped, error}` + conditional `message`), the runner sets `run_status='contract_violation'` and appends a warning `{type:'RECEIPT_CONTRACT_VIOLATION', message:<reason>, meta:{predicate:<which_check_failed>}}`. The agent's underlying `success` bool is unchanged on the AgentResult.

4. **Both writeback paths emit the envelope:**
   - `core/tasks_agents.py::_impl_execute_agent_task` (celery-task path) — covers PA tool dispatches, Rigby's `run_agent`, Celery beat tasks
   - `core/agent_router.py::_complete_execution` (synchronous path) — covers `AgentRouter.route()` callers including WorkflowAgent's sub-dispatches

5. **Helpers live in `core/services/urc_envelope.py` — single source of truth.** Pure functions, no Django imports, no I/O. Exposes `compute_run_status(success, error, data, input_context)` (primitive args) and `enrich_output_data(base_output, **kwargs)` (mutates + returns).

6. **Backcompat is total.** All legacy `output_data` keys (`content`, `metadata`, `message`, `result_preview`, `data`, `error`, `tool_calls`, plus PR #2469's `deliverable_id`/`warnings` + PR #2471's `attempts_used` top-level lifts) are preserved alongside the URC keys. Additive only — every existing reader continues to work.

7. **Raw caller context is now stored on router-path execution rows.** `agent_router._create_execution_record` writes the original context dict to `input_data['context']` (in addition to the existing Session 758 observability summary at `input_data['context_injected']`). Required for Phase C predicate; aligns router path with celery task path's convention.

8. **`run_status='contract_violation'` only fires when explicitly asked.** Callers MUST set `context['mode']='receipt_only'` for the check to run. Normal-mode dispatches receive `run_status='success'` even when their payload happens to lack a `status` field. No false positives observed in the fleet smoke (0 unexpected contract_violations on the 39 non-receipt_only rows).

9. **`tools/pa_local.sh` points at `pa-61c7b47d201d4591`.** Future Claude Code sessions land in Rigby's Session 1209 thread by default. Previous pin `pa-2d74e36cc3a04787` (Session 1208 + URC design) retired.

## Rollback levers (per change)

| Lever | Action | Effect |
|---|---|---|
| **Disable URC enrichment entirely (both paths)** | Comment out the `_urc_enrich_output_data(...)` call in `_impl_execute_agent_task` writeback AND the `_urc_enrich(...)` call in `agent_router._complete_execution`. | All output_data writebacks revert to pre-Session-1209 shapes. URC consumers see absent keys; legacy readers unaffected. |
| **Disable router-path enrichment only** | Comment out the import+call block at `core/agent_router.py::_complete_execution` (lines 2929+ marked `Session 1209 follow-up`). | tasks_agents path continues to emit URC; router path reverts to canonical-only. Used if router-path classification produces unexpected results. |
| **Disable contract_violation classification (keep envelope)** | In `core/services/urc_envelope.py::compute_run_status`, change the `input_context.get('mode') == 'receipt_only'` check to always return `False` for the contract_violation branch. | URC envelope still emitted; receipt_only check becomes a no-op. All previously-contract-violation rows become 'success' instead. |
| **Force-revert context propagation** | Remove the `if isinstance(context, dict) and context: input_data['context'] = context` block from `agent_router._create_execution_record` and remove the `context=context` kwarg at L1437. | Router-path Phase C stops working (no context to read). Phase A envelope still emitted. |
| **Revert thread pin** | Edit `tools/pa_local.sh` `--conversation` flag to a prior value (e.g. `pa-2d74e36cc3a04787`). | Local PA wrapper routes elsewhere. Pure dev-side change. |
| **Full hard revert** | `git revert 7669a249^..7669a249 3d95aea9^..3d95aea9` on a hotfix branch + PR. | Removes URC v0.1 entirely. ~800 LoC restored to pre-Session-1209 state. |

## Post-merge gotchas

- **Workers MUST restart after the merges.** Both PRs modify `core/tasks_agents.py` AND `core/agent_router.py`; both are imported by Celery task bodies. Per `feedback_new_shared_task_needs_worker_restart.md` case 2, the running workers' `sys.modules` cache holds the pre-merge versions even though `@shared_task` itself didn't change. Done in-session: workers restarted twice (00:24 MDT post-#2473; 00:34 MDT post-#2474; final restart 00:09 MDT after PR #2474 squash-merge). **For next session: check `ps -eo pid,lstart | grep celery` against `git log -1 main` and restart if workers predate the latest tasks_agents.py / agent_router.py touch.**

- **Pre-existing Pyright diagnostics in `core/agent_router.py` and `core/tasks_agents.py` are untouched.** All diagnostics flagged during the session (started_at/teacher_agent_id/error_traceback/etc.) predate Session 1209 work — they're Django attribute resolution issues, not real bugs.

- **`input_data['context'].research` bloat on router-path receipt_only smokes.** Rigby's tool path attaches the full URC spec body (~6KB) as `context['research']` when dispatching smokes. Not a URC bug, but it inflates execution records. Phase 3 follow-up on Rigby's side — she'll define a minimal "smoke context" convention (just `mode` + tiny `smoke_id`) to avoid leaking long text into downstream logs.

- **`context-kit verify` strong-token trap re-triggered by Session 1208 close commit.** The line `Report headline: 36 agents succeeded / 7 "failed"` in 00-START-NEXT-SESSION.md (added by `8295ccca`) was the same Session 1198 trap — `Headline` token propagating total-dimension classification to `36`. Fix landed as two commits in PR #2473 (rephrase + remove the trap word entirely). Memory rule: `feedback_context_kit_headline_propagates_total.md`. Watch for this pattern in future close commits.

- **Phase B is the natural Session 1210 entry point.** CodeReviewAgent ×4 stay `run_status='error'` until the `mode=receipt_only` capability ping is added at the agent layer. Separate PR per spec §7.

## 24h watch checklist (fires ~13:10 UTC 2026-06-24 / ~07:10 MDT)

Invariants to verify (URC envelope stability + zero misclassification):

1. **Every agent run on both writeback paths emits the full URC envelope.** Pre-fix baseline: 0/21 on router path. Post-fix: 52/52 immediately after merge. 24h check: pull all `AgentExecution` rows from the last 24h, count those with all 8 URC keys present.
2. **`run_status` distribution is sane.** Expect majority `success` + some `error` (from real failures) + minimal `contract_violation` (only when callers deliberately pass `mode=receipt_only`).
3. **Zero spurious contract_violations on non-receipt_only callers.** This was the key post-fix invariant from the fleet smoke. A regression here would indicate someone broke the receipt_only predicate scoping.
4. **`warnings` list shape stays consistent.** Always a list; structured `{type, message, meta?}` entries.

```bash
# Invariant 1: URC envelope coverage on all rows in last 24h
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentExecution as AE
from django.utils import timezone
from datetime import timedelta
cutoff = timezone.now() - timedelta(hours=24)
required_urc = {'agent_name','run_status','latency_ms','error_signature','error_message','artifacts','warnings','completed_at'}
rows = AE.objects.filter(created_at__gte=cutoff, status__in=['completed','failed'])
total = rows.count()
complete = sum(1 for e in rows if required_urc.issubset((e.output_data or {}).keys()))
print(f'URC envelope coverage 24h: {complete}/{total} ({100*complete/total if total else 0:.1f}%)')
print('Target: 100% (or near-100% — old rows from before Session 1209 merge are exempt)')
"

# Invariant 2: run_status distribution
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentExecution as AE
from django.utils import timezone
from datetime import timedelta
from collections import Counter
cutoff = timezone.now() - timedelta(hours=24)
dist = Counter()
for e in AE.objects.filter(created_at__gte=cutoff, status__in=['completed','failed']):
    dist[(e.output_data or {}).get('run_status', '__none__')] += 1
for s, n in dist.most_common():
    print(f'  {s}: {n}')
"

# Invariant 3: zero contract_violations on non-receipt_only callers
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentExecution as AE
from django.utils import timezone
from datetime import timedelta
cutoff = timezone.now() - timedelta(hours=24)
bad = []
for e in AE.objects.filter(created_at__gte=cutoff):
    od = e.output_data or {}
    if od.get('run_status') != 'contract_violation': continue
    ctx = (e.input_data or {}).get('context') if isinstance(e.input_data, dict) else None
    mode = ctx.get('mode') if isinstance(ctx, dict) else None
    if mode != 'receipt_only':
        bad.append((e.agent.name, str(e.id)[:8], mode))
if bad:
    print('REGRESSION: contract_violation on non-receipt_only:')
    for n, i, m in bad: print(f'  {n} {i} mode={m}')
else:
    print('OK: no spurious contract_violations.')
"

# Invariant 4: warnings list shape
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentExecution as AE
from django.utils import timezone
from datetime import timedelta
cutoff = timezone.now() - timedelta(hours=24)
bad_shape = []
for e in AE.objects.filter(created_at__gte=cutoff, status__in=['completed','failed'])[:200]:
    od = e.output_data or {}
    w = od.get('warnings')
    if not isinstance(w, list):
        bad_shape.append((e.agent.name, str(e.id)[:8], type(w).__name__))
if bad_shape:
    print('REGRESSION: non-list warnings:')
    for n, i, t in bad_shape: print(f'  {n} {i} type={t}')
else:
    print('OK: all warnings are list-shaped.')
"
```

## Open follow-ups (deferred to Session 1210 or later)

- **P0 (Phase B, planned)** — `mode=receipt_only` capability ping for CodeReviewAgent + other context-dependent agents as fleet smoke reveals. Separate PR per spec §7. Should be small: each agent needs to handle a `context.mode=='receipt_only'` branch that returns `result.data={status: 'ok'/'skipped'/'error', message?: '…'}` instead of its normal output.
- **P1 (Phase 3, on Rigby's side)** — define a minimal "smoke context" convention (e.g. `context.mode` only + tiny `context.smoke_id`) for her future fleet smokes. Avoids inflating execution records or leaking long text into downstream logs. Rigby flagged in pa-61c7b47d201d4591.
- **P2 — Other writeback callsites adopt URC.** The wider audit found ~10 sites: `core/agent_execution_wrapper.py:93`, `ai_core/agents/sync_executor.py:109`, `core/services/content_executor.py:255`, `core/services/executor_registry.py:394`, `core/services/agent_collaboration.py:339`, `core/team_workflow_engine.py:494,517`, `core/services/collective_intelligence.py:1425`, `core/tasks_media.py:192`, `core/tasks_agents.py:706,2278` (orchestration runner + skipped-dedup early-exit). The two paths patched (tasks_agents.execute_agent_task + agent_router._complete_execution) cover Rigby's fleet smoke surfaces; the rest are narrower use cases that can adopt URC as they're touched. Filed as a Session 1210 candidate.
- **P2 — Expose `parent_execution_id` filter in `execution_search` / `execution_history_tool`.** Rigby's fleet-smoke aggregation hit a gap — couldn't easily query "all AgentExecutions spawned by parent X". Currently no filter exposed. Session 1098 PR #4 added `parent_execution_id` + `root_execution_id` fields to the model; just need to surface them in the tool. ~30min PR.
- **P3 — Phase B follow-up: exception-class capture for `error_signature`.** Currently string-only normalization (Q4 lock). Could capture `exc.__class__.__name__` at agent_router exception sites and pipe through `result.error_class` for better error grouping. Adds an `AgentResult.error_class: Optional[str]` field. Defer until there's a concrete need.
- **P3 — `started_at` is consistently null in observed rows.** Many agents never call `execution_record.start_execution()`. Spec §3 marks it optional, but worth a follow-up to wire it up in `_impl_execute_agent_task` / `agent_router._create_execution_record` for better latency observability.

### Carryover from prior sessions still valid for Session 1210

- **P0** workspace_id hallucination root-cause trace (deliverable `96b6a72a-…`) — guardrail in place via Session 1206 PR #2465; root cause still unidentified.
- **P1** CI lint rule blocking `\.execute\(` outside `core/agents/` (deliverable `180f4e9f-…`).
- **P1** Title normalization at deliverable_factory level (Session 1208 carryover — affects MIC + Outbound + future agents).
- **P1** Promote `attempts_used` to canonical top-level `output_data` key on the BARE legacy writeback (Session 1208 carryover — PR #2469 + PR #2471 covered this for `execute_agent_task`, but the router-path canonical-shape writeback at agent_router.py:1611 needs the same lift).
- **P2** Beat schedule for periodic outbound-pack generation (Session 1208 carryover).
- **P2** TheOdds API key renewal (Chris-owned, billing-gated).

Full priority table lives in [`00-START-NEXT-SESSION.md`](../../00-START-NEXT-SESSION.md) §"Pick this session".

## Design decisions captured in-session

Rigby's design pings on `pa-2d74e36cc3a04787` (URC v0.1 spec discussion, Sessions 1208→1209 boundary) and `pa-61c7b47d201d4591` (Session 1209 implementation + review-gate stamps) locked five design points + two mid-session adjustments.

### Q1 — `_is_skipped` detector (Rigby answer: data-key marker)

`result.success is True AND isinstance(result.data, dict) AND result.data.get('skipped') is True`. No AgentResult schema change in v0.1. AgentResult.skip_reason structured field deferred to Phase B if needed.

### Q2 — `_is_timeout` detector (Rigby answer: string-match for v0)

`result.success is False AND result.error AND 'wall-clock timeout' in result.error`. Matches the wall-clock-timeout string set at `tasks_agents.py:L2474`. Cheap, reversible. Phase B can add `AgentResult.is_timeout: bool` if string-matching proves fragile.

### Q3 — v0 receipt schema (Rigby answer: minimal — dict + status only)

Receipt = `dict` with key `status ∈ {ok, skipped, error}`. Conditional: when `status == 'error'`, requires non-empty `message: str`. **Does NOT require `timestamp`** in v0.1. Per-agent specialization deferred to Phase B once we know which agents actually adopt `receipt_only`.

### Q4 — `error_signature` class prefix (Rigby answer: defer)

v0.1 uses string-only normalization at writeback time. Exception class info is lost by the time we get to writeback (we have `result.error` string only, not the original exception object). Phase B follow-up: capture `exc.__class__.__name__` at agent_router exception sites and pipe through `result.error_class`. Adds an AgentResult field; deferred to keep Phase A additive.

### Q5 — `success=True` + non-empty `error` defensive lock (Rigby answer: defensive, with one tweak)

Non-empty `result.error` forces `run_status='error'` regardless of `success` bool. Real crashes cannot be masked by contract failures. **Rigby tweak:** the precedence pseudocode should explicitly show this — the `error` branch fires whenever `result.error` is non-empty, not just on `not result.success`. Baked into the implementation: `if (not success) or bool(error): return ('error', None)`.

### Mid-session: router-path coverage gap (PR #2474 trigger)

PR #2473's Phase A was implemented inline at `tasks_agents.execute_agent_task` writeback. Post-merge fleet smoke surfaced 21/21 sub-agent rows missing the envelope — WorkflowAgent's sub-dispatches go through `AgentRouter.route()` → `_complete_execution` synchronously, not through the celery task path. Resolved by extracting helpers to `core/services/urc_envelope.py` and adding `enrich_output_data()` calls to both writebacks. Chris's call: "go with A" (refactored extraction over narrow router-only fix).

### Mid-session: raw context propagation gap (PR #2474 second change)

Phase C predicate needs `input_data['context']['mode']`. The router-direct path only stored an observability summary at `input_data['context_injected']` (Session 758 convention) — never the raw context. Required passing `context=context` through `_create_execution_record` and stashing it at `input_data['context']`, matching the celery task path's convention.

## Closeout state

- **Active conversation pinned to `pa-61c7b47d201d4591`** (Session 1209) via `tools/pa_local.sh`. Worth deciding at Session 1210 open whether to spin a fresh thread (Phase B is a discrete arc — likely yes) or continue here if the next work extends URC.
- **Workers** restarted post-merge — PIDs 9239-9278 fresh after `7669a249`. Watching ongoing dispatches.
- **24h watch** for URC stability arms ~13:10 UTC 2026-06-24 — checklist in this handoff.
- **Session 1207 MIC 24h watch** fires ~03:50 UTC tonight (already past in some timezones); Session 1208 Outbound 24h watch fires ~04:45 UTC 2026-06-24.
- **Donkey Betz workspace_id pin** still `b4503364-2573-4401-9e28-61a739e0ce50`. Initiative `29154d73-…` (Platform Capability Audit) now has 14 deliverables (was 13 end-of-1208; +URC spec `6f09233c-…`; +smoke evidence `1a8cde69-…`; -1 because spec was technically added Session 1209 not 1208).
