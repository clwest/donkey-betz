# Session 1098 Addendum — Cancel Token + CI Lint Trilogy

**Appends to:** `SESSION_1098_LLM_TELEMETRY_AND_EDITOR_REROUTE.md`

**Additional PRs landed after the primary handoff was written:**

| PR | Title | Merge method | Branch (deleted) |
|----|-------|--------------|------------------|
| [#2007](https://github.com/clwest/donkey-betz-platform/pull/2007) | feat(ci): direct-LLM-SDK lint — staged warn-only rollout | squash | `feature/llm-sdk-direct-call-lint` |
| [#2008](https://github.com/clwest/donkey-betz-platform/pull/2008) | feat(cancel): cooperative cancel_token end-to-end | merge commit | `feature/cancel-token-end-to-end` |
| [#2009](https://github.com/clwest/donkey-betz-platform/pull/2009) | feat(cancel): nested-dispatch cancel propagation via parent/root lineage | merge commit | `feature/parent-execution-cancel-propagation` |

**Merge commits on `main`:** `057b1d96` · `e4eba1db` · `edcde748`

## TL;DR (3-bullet executive summary)

- **What changed:** Every LLM call now goes through a single wrapper with per-call
  telemetry + cooperative cancellation, cancel signals propagate from parent
  executions to every child dispatch at the next checkpoint, and a CI lint
  (warn-only) now catches direct-SDK bypasses with a tiered remediation roadmap.
- **Why it matters:** Rigby's boardroom-dispatch hangs — 50-minute stuck runs
  that burned tokens after the wall-clock timeout fired — now have a clean
  cancellation path that reaches in-flight LLM calls, marks executions with a
  distinct `cancelled` status (not `failed`), and records *where* cancellation
  was observed. Plus we have a per-call audit trail for every LLM call.
- **What to watch:** `LLMCallEvent` ingestion rate climbing as agents adopt the
  wrapper; `deliverable_routed_fallback_count` (should stay near zero);
  `[editor-reroute]` log count; any `ancestor walk exceeded depth cap` WARNINGS
  in cancel_registry (indicates malformed lineage data).

## Migrations

| Migration | Kind | Rollback | Notes |
|-----------|------|----------|-------|
| `0334_llmcallevent` | Additive (CreateModel + 3 indexes) | Drop table | Empty at ship time |
| `0335_agentexecution_cancelled_status` | AlterField on status choices | Revert choices list | Choices-only change; no data touched |
| `0336_agentexecution_parent_root_lineage` | AddField ×2 (nullable UUIDField, db_indexed) | Drop columns | Old rows NULL; new rows populated by router |

**No backfills. No destructive data migrations. Safe to roll back.**

## Rollback plan

| Layer | How to disable without redeploying |
|-------|-----------------------------------|
| **CI lint** | Edit `.github/workflows/check-llm-sdk.yml` — the job already uses `--warn-only`. Remove the workflow file or add `if: false` to disable entirely. |
| **CancelToken** | Purely additive — agents call `_check_cancel()` voluntarily; the wrapper's registry check no-ops when `execution_id` isn't in the registry. To hard-disable: short-circuit `core/services/cancel_registry.is_execution_cancelled` to return `False` unconditionally. |
| **Lineage** | Additive fields; `parent_execution_id=NULL` behaves exactly like pre-PR-4 code. No action needed to "disable." |

## Code surfaces added

```
core/services/cancel_registry.py              NEW   Redis + in-memory cancel registry, ancestor walk
core/services/llm_call_wrapper.py             MOD   _check_cancel() integration (span + async)
core/agents/base_agent.py                     MOD   _check_cancel(checkpoint_name) helper
core/agent_router.py                          MOD   LLMCallCancelled handler → status='cancelled'
                                                    _create_execution_record(parent_execution_id=...)
core/views_agent_execution.py                 MOD   POST /cancel/ + GET /cancel-state/
core/urls.py                                  MOD   Two URL routes
core/models_unified_system.py                 MOD   parent_execution_id + root_execution_id fields
                                                    status choices += 'cancelled'
core/migrations/0334_llmcallevent.py          NEW   PR #1999
core/migrations/0335_agentexecution_...       NEW   PR #2008 (cancelled status)
core/migrations/0336_agentexecution_...       NEW   PR #2009 (lineage fields)
core/tests/test_llm_call_wrapper.py           NEW   21 tests
core/tests/test_editor_synthesis_reroute.py   NEW   19 tests
core/tests/test_deliverable_initiative_...    NEW   8 tests
core/tests/test_cancel_token_e2e.py           NEW   18 tests
core/tests/test_cancel_ancestor_propagation   NEW   9 tests
tools/check_direct_llm_calls.py               NEW   CI lint checker
.ci/llm_whitelist.txt                         NEW   99-entry tiered remediation list
.github/workflows/check-llm-sdk.yml           NEW   GitHub Action (warn-only)
docs/plans/SESSION_1098_FIX_B_FULL_TICKET.md  NEW   B-full plan (task #9 / future sprint)
```

**Total: 75 new tests, 3 migrations, 4 new services, 2 new API endpoints.**

## Next session pickup

See the primary handoff (`SESSION_1098_LLM_TELEMETRY_AND_EDITOR_REROUTE.md`)
for the "queued follow-ups" table. Short list:

1. **CI lint enforce-mode flip** — once the 99-entry whitelist is shrunk
   to ~10, remove `--warn-only` from `.github/workflows/check-llm-sdk.yml`.
2. **Per-agent wrapper adoption** — migrate the top-5 hotspots from
   PR #1999's PR body (content_writer, tasks_initiatives,
   market_intelligence, code_review, devops).
3. **B-full schema** — see `docs/plans/SESSION_1098_FIX_B_FULL_TICKET.md`.
   Separate sprint; not blocked by current work.
4. **Per-agent cancel checkpoints** — each agent's `execute()` gains
   strategic `self._check_cancel("step-N")` calls. PR #2008 shipped the
   machinery; adoption is incremental.
