# Session 1185 — Provenance Caller Sweep + Forensic Follow-Ons (PR-C)

**Status:** 8 PRs shipped (open + CI-green at session close). Bucket 4 (3 celery task callsites) deferred to Session 1186.
**Date:** 2026-06-21
**Pinned conversation:** `pa-10df024c0bd8` (forensic-validation thread; bucket-3 design recon also lives here)
**Driving artifact:** [`docs/specs/deliverable_creation_paths.md`](../specs/deliverable_creation_paths.md) — the ~17 non-agent caller sweep map.
**Prior session:** [`SESSION_1184_DELIVERABLE_PROVENANCE_LINKAGE.md`](./SESSION_1184_DELIVERABLE_PROVENANCE_LINKAGE.md) (PR #2362 — factory synthesis + PR-A) + [`SESSION_1184_PR_B_BASEAGENT_PROVENANCE_WIRING.md`](./SESSION_1184_PR_B_BASEAGENT_PROVENANCE_WIRING.md) (PR #2364 — BaseAgent root-cause).

## TL;DR

Took both Session 1184 forensic follow-ons (F1 ContentWriterAgent diagnostic_mode + F2 execution_history_tool reverse-link) plus 5 of the 6 PR-C sweep buckets to PR-ready state in a single session. **8 PRs queued for Chris's merge.** Only bucket 4 (3 celery task callsites needing per-task `AgentExecution` rows) remains.

Bucket 3B surfaced a structural finding: two conversation pipelines were silently in the `legacy_no_provenance` bucket (set `Deliverable.parent_object_type='conversation'` which the read helper doesn't recognize). Grep confirmed zero downstream readers — risk-free flip. Now use the Session 843 `AgentExecution(parent_object_type='conversation')` pattern as the intermediate hop.

## PRs shipped

| # | PR | Theme | LoC | CI at close |
|---|---|---|---|---|
| 1 | [#2367](https://github.com/clwest/donkey-betz-platform/pull/2367) | **F2** — `execution_history_tool` reverse-link to deliverables | +174 (+4 tests) | ✅ green |
| 2 | [#2368](https://github.com/clwest/donkey-betz-platform/pull/2368) | **PR-C bucket 1** — 5 mgmt commands opt into synthesis | +109 (+4 tests) | ✅ green |
| 3 | [#2369](https://github.com/clwest/donkey-betz-platform/pull/2369) | **F1** — ContentWriterAgent `diagnostic_mode` bypass | +290 (+7 tests) | ✅ green |
| 4 | [#2370](https://github.com/clwest/donkey-betz-platform/pull/2370) | **PR-C bucket 2** — 4 web views opt into synthesis | +187 (+7 tests) | ✅ green |
| 5 | [#2371](https://github.com/clwest/donkey-betz-platform/pull/2371) | **PR-C bucket 3A** — 3 service helpers + envelope audit | +178 (+6 tests) | ✅ green |
| 6 | [#2372](https://github.com/clwest/donkey-betz-platform/pull/2372) | **PR-C bucket 3B-1** — conversation pipelines thread orchestration AgentExecution | +387 (+6 tests) | ✅ green |
| 7 | [#2373](https://github.com/clwest/donkey-betz-platform/pull/2373) | **PR-C bucket 3B-2** — per-stage AgentExecution rows in workspace pipeline runner | +283 (+5 tests) | ⏳ CI in flight |
| 8 | [#2374](https://github.com/clwest/donkey-betz-platform/pull/2374) | **PR-C bucket 5** — competitor_comparison_tool opt-in + append_service audit | +128 (+4 tests) | ⏳ CI in flight |

**Tests added across all 8 PRs: 43** (4 + 4 + 7 + 7 + 6 + 6 + 5 + 4). 100% pass when run alongside the existing 4 PR-A provenance + 7 PR-B BaseAgent suites (~54 total tests in the provenance program now). Zero adjacent regressions.

## Open invariants now load-bearing post-1185

1. **Deliverables from PR-C-sweep callsites get real `parent_object_id`** pointing at an `AgentExecution` (either synthesized via factory or pre-created at the orchestration site). The read helper surfaces them as non-legacy.
2. **`AgentExecution.input_data.execution_kind`** is a new soft contract for orchestration receipts (`'orchestration'`, `'orchestration_stage'`). Use this when introspecting why an execution exists.
3. **Conversation→Deliverable chain is now 2-hop** (Deliverable → AgentExecution → Conversation) via Session 843 fields on AgentExecution. Legacy 1-hop (Deliverable.parent='conversation') is no longer written; existing rows stay in the legacy bucket (grep confirmed no downstream readers).
4. **Workspace pipeline runner produces N AgentExecution rows per N-stage run**, each `parent_object_type='pipeline_run'`. Per-stage attribution lets F2 reverse-link surface deliverables produced by each stage execution.
5. **F1 `diagnostic_mode=True` bypasses the full content production pipeline** — task spec rendered verbatim, no LLM. Deterministic forensic dispatches.
6. **`auto_followup=False` on agent tool calls suppresses completion banners** (unchanged from Session 1184; still load-bearing).

## What's still open (Session 1186)

### Bucket 4 — Celery tasks (3 callsites)

Per [`docs/specs/deliverable_creation_paths.md`](../specs/deliverable_creation_paths.md) § Celery tasks:

| Callsite | Agent | Notes |
|---|---|---|
| `core/tasks_content.py:244` | `VideoContentPackAgent` | Has Celery task context but no AgentExecution row. Either (a) thread execution_id from task args, or (b) create AgentExecution at task start |
| `core/tasks_initiatives.py:2149` | `TechnicalDocumentAgent` | In initiative stage flow — has Initiative + stage_num context. Best: create AgentExecution per stage and pass its id |
| `core/tasks_initiatives.py:2770` | `InitiativePipeline` | Same pattern as above |

**Design call needed per-callsite** (similar to bucket 3B recon). Each task has different inputs — VideoContentPack runs from task args; TechnicalDocument is inside an initiative-stage flow with existing Initiative context. Recommend Rigby check-in on pa-10df024c0bd8 before implementing.

### Housekeeping (mechanical, after bucket 4)

- **Spec doc consolidation PR** — `docs/specs/deliverable_creation_paths.md` Coverage summary section: move all PR-C bucket rows from ⚠️ WARN → 🟡 synthesized (or ✅ wired for the threaded ones). Status header bumped to Session 1186. Tests count update.
- **Inventory refresh PR** — `python manage.py generate_platform_inventory --write` + fix the 2 high drifts in `core/management/commands/load_all_agents_advisors.py` (persona_agent_count expected=155 → actual after Session 1166-1170 dim restructure, total_agent_count_claim expected=238 → AGENT_MAP + Agent total).
- **PR-D contract flip** — after PR-C buckets 1-5 all merge + 24h WARN-volume watch confirms zero remaining non-agent WARNs, flip factory contract from `logger.warning(...)` to `raise DeliverableProvenanceMissingError(...)`. Per Rigby's PR-A close: 24h cooldown between PR-C completion and PR-D flip.

### Backlog (low priority, surfaced this session)

- **Pre-existing bug in `workspace_pipeline_runner._save_stage_deliverable`** — no guard against `create_deliverable()` returning None (quality-gate rejection causes `AttributeError: 'NoneType' object has no attribute 'id'`). Not introduced by 3B-2. Easy 1-line fix if it bites; leaving for whoever steps on it.
- **Legacy `Deliverable(parent_object_type='conversation')` rows** — pre-bucket-3B-1 deliverables stay in legacy_no_provenance bucket. No downstream readers found, so they're effectively orphaned data already. Backfill ticket only if a consumer surfaces.

## Post-merge worker restart matrix

Each PR's description includes whether worker restart is required. Quick map:

| PR | Worker restart? | Reason |
|---|---|---|
| #2367 F2 | YES | `td_handlers_content.py` imported by PA task body |
| #2368 bucket 1 | No | Mgmt commands run via `python manage.py`, not workers |
| #2369 F1 | YES | `content_writer_agent.py` imported by PA task body |
| #2370 bucket 2 | No | Daphne-served view handlers (standard daphne restart on deploy) |
| #2371 bucket 3A | YES | `mission_control_executor.py` + `implementation_executor.py` run in workers |
| #2372 bucket 3B-1 | YES | Both conversation pipelines run in workers |
| #2373 bucket 3B-2 | YES | `workspace_pipeline_runner.py` runs in `execute_pipeline_run_task` |
| #2374 bucket 5 | YES | `td_handlers_core.py` imported by PA task body |

**Standard restart**: `pkill -9 -f celery; rm -f .celery*.pid; make celery` after each YES-restart merge (or batch all merges → single restart).

## Smoke verification (post-merge across all 8 PRs)

After all 8 PRs land + worker restart, run on pa-10df024c0bd8:

1. **F1**: `content_writer_agent` dispatch with `context={diagnostic_mode: true}` + nonce in task → produced deliverable contains nonce verbatim
2. **F2**: `execution_history_tool action=detail id=<exec_uuid>` → response includes `deliverables` field
3. **Bucket 1**: invoke `register_external_repo` → `deliverable_tool.detail` shows `provenance.synthesized=true, trigger_source='direct'`
4. **Bucket 2**: PATCH workspace brief → same shape with `trigger_source='user_request'`
5. **Bucket 3A**: dispatch an Implementation workflow → workflow deliverable shows `synthesized=true, trigger_source='direct'`
6. **Bucket 3B-1**: trigger conversation→initiative pipeline → deliverable shows `synthesized=false, trigger_source='agent_execution', origin_execution_id=<orchestration receipt>`, AgentExecution row has `parent_object_type='conversation'`
7. **Bucket 3B-2**: run a 5-stage workspace pipeline → 5 stage executions created with `parent_object_type='pipeline_run'`; each stage deliverable's provenance points at its stage execution
8. **Bucket 5**: `competitor_comparison_tool action=export_markdown` → deliverable shows `synthesized=true, trigger_source='pa_tool'`

## Memory updates

No new memories added this session. Existing rules applied throughout:
- `feedback_rigby_comms.md` — every design call routed through pa-10df024c0bd8
- `feedback_triage_decision_card_pattern.md` — used for "agree all" sweep order
- `feedback_factory_silent_none_footgun.md` — informed defensive try/except in 3B-1/3B-2 orchestration paths
- `feedback_new_shared_task_needs_worker_restart.md` — flagged in every PR's post-merge section

## Watch checklist for Session 1186 first 30 minutes

1. Disk + swap (per `00-START` READ THIS SECOND): `df -h /System/Volumes/Data`, `sysctl vm.swapusage`
2. `tools/pa_local.sh "platform_config_tool overview"` → confirm `service_context: local`
3. `session_tool health_check` on `pa-10df024c0bd8` → rotate to fresh Session 1186 thread if past 60/100
4. `gh pr list --author @me --state open` → confirm 8 PRs visible (or how many merged since session close)
5. If PRs merged: `pkill -9 -f celery; rm -f .celery*.pid; make celery` per the restart matrix above
6. **For bucket 4 design call**: dispatch Rigby with the 3 callsite specs + ask for per-task design (thread vs synthesize vs per-stage AgentExecution like 3B-2 used)
