# Session 1186 — PR-C Bucket 4 (Celery Tasks) Close

**Status:** 1 PR shipped (#2376, open + 3/3 CI green at session close).
**Date:** 2026-06-21
**Pinned conversation:** `pa-10df024c0bd8` (forensic-validation + bucket-3/4 design recon thread).
**Driving artifact:** [`docs/specs/deliverable_creation_paths.md`](../specs/deliverable_creation_paths.md) § Celery tasks.
**Prior session:** [`SESSION_1185_PROVENANCE_CALLER_SWEEP.md`](./SESSION_1185_PROVENANCE_CALLER_SWEEP.md) (PR-C buckets 1, 2, 3A, 3B-1, 3B-2, 5 + F1 + F2 — 8 PRs).

## TL;DR

Closed the final PR-C bucket (3 celery task callsites: `tasks_content.py:244` + `tasks_initiatives.py:2149` + `tasks_initiatives.py:2770`). Shipped as PR #2376 with 10 new tests; 21 total provenance tests pass when run alongside the prior PR-A + PR-B suites.

Mid-session, a structural finding broke the original design and was routed through Rigby instead of silently bridged: both initiative tasks already create TWO Deliverables per stage (internal agent save + external task save with different tags/FKs). Threading a single execution_id through both would collapse them via the factory's dedupe-by-(parent_object_type, parent_object_id) and silently lose the Initiative-shaped row. Rigby's pick (**B.2**): provenance the EXTERNAL save only via a NEW receipt distinct from the agent's internal execution. Helper `_create_initiative_external_execution_receipt` in `tasks_initiatives.py` covers B + C; A uses factory synthesis only.

Two follow-up deliverables filed in Local QA via Rigby (B.1 unify-deliverables long-term fix + PR-D contract flip 24h watch).

## PR shipped

| # | PR | Theme | LoC | CI |
|---|---|---|---|---|
| 1 | [#2376](https://github.com/clwest/donkey-betz-platform/pull/2376) | **PR-C bucket 4** — 3 celery task callsites (A direct synthesis + B/C external receipt) | +463 / -1 (+10 tests) | ✅ 3/3 green |

## What landed

### Callsite A — `core/tasks_content.py:244` (VideoContentPackAgent)

`_impl_generate_video_content_pack_task` is a direct OpenAI call (gpt-5-mini); `'VideoContentPackAgent'` is a descriptive label only — no Agent class is invoked. Added `metadata={'trigger_source': 'direct', 'celery_task_name': ..., 'video_id': ..., 'user_id': ..., 'language': ..., 'llm_model': 'gpt-5-mini', 'transcript_id': ...}` to the existing `create_deliverable` call. Factory synthesizes a receipt because `'direct'` is in `_PA_DIRECT_TRIGGERS`.

### Callsites B + C — `core/tasks_initiatives.py` (B: 2149, C: 2770)

Shared helper `_create_initiative_external_execution_receipt(agent_name, initiative, stage_num, stage_label, celery_task_name, content, self_blog_id, extra_input=None)` at the top of `tasks_initiatives.py`. Creates an `AgentExecution` row with:

- `status='completed'`
- `owner_agent=<agent_name>`
- `parent_object_type='initiative'`, `parent_object_id=initiative.id`
- `input_data['source']='initiative_pipeline_task_external_save'`
- `input_data['execution_kind']='orchestration_stage'`
- `input_data['celery_task_name']=...`
- `output_data={'kind': 'deliverable_receipt', 'summary': content[:500]}`

Returns receipt execution_id (str) or `None` on failure (caller falls through to factory's WARN bucket — pipeline does not block).

Both callsites pass the returned id as `parent_execution_id` + `parent_object_type='agent_execution'` to `create_deliverable`.

## Why B.2 (not B.1) — design call summary

Mid-implementation finding: both initiative tasks already create TWO Deliverables per stage.

| | Internal agent save (l. 588 of technical_document_agent.py) | External task save (l. 2149 / 2770) |
|---|---|---|
| title | doc_title (agent-computed) | doc_title (task-computed) |
| category | `Development` | `Initiative — Stage N` |
| tags | `[doc_type, stage-N, topic[:30]]` | `[initiative, stage-N, program]` |
| initiative FK | — | `initiative=init` |
| self_blog FK | — | `self_blog=blog` |
| workspace FK | resolved from agent context | `init.workspace` |

The Initiatives UI keys on the external row's `category` + `initiative` FK. Threading one execution_id through both saves would dedupe them via `deliverable_factory.py:509-530`, with the second call returning the first and the idempotent upsert NOT carrying over the second call's tags/FKs.

**Options surfaced to Rigby:**
- **B.1** — drop external save, thread initiative context into agent's internal save (one deliverable per stage, right shape). Long-term right answer.
- **B.2** — provenance external save only, distinct receipt. Two rows persist. Tight scope, no behavior change beyond external row now having a provenance link.
- **B.3** — both saves get provenance + new factory flag to bypass dedupe. New escape hatch.

**Pick:** B.2 for this PR + file B.1 as a follow-up. Same hazard applies to callsite C (router-mediated path also has internal+external save).

## Open invariants now load-bearing post-1186

1. **`tasks_content.py:244` deliverables carry synthesized provenance** via `trigger_source='direct'` + factory synthesis. Metadata carries celery context for audit.
2. **`tasks_initiatives.py:2149` + `:2770` external deliverables carry receipt-based provenance** distinct from the agent's internal execution. Receipt has `parent_object_type='initiative'` + `input_data['source']='initiative_pipeline_task_external_save'`. Receipt is queryable by initiative FK.
3. **`_create_initiative_external_execution_receipt` is the canonical helper** for any future initiative-pipeline callsite that needs external-save provenance.
4. **Receipt creation is defensive** — failure returns `None`, caller falls through to factory's WARN bucket. Pipeline does not block.
5. **Two deliverables per stage is still reality** (B.1 follow-up tracks the unification).

## What's still open (Session 1187)

### Tracked as Local QA deliverables (filed via Rigby this session)

| Deliverable ID | Title | Priority | Sketch |
|---|---|---|---|
| `48b73b04-373a-4d25-b263-9925c7c1a084` | **B.1** — Unify Initiative-stage deliverables (follow-on to PR #2376) | P3 | Thread initiative + stage + workspace context into agent's internal `_save_to_deliverable` so it produces the Initiative-shaped row. Drop external save. AC1-AC4 in deliverable. |
| `9d9db48a-4819-4e2b-9548-998c0fe2f8f5` | **PR-D contract flip** — 24h WARN-volume watch after PR #2376 merge | P2 | After 24h with zero non-agent WARNs, flip factory from `logger.warning(...)` to `raise DeliverableProvenanceMissingError(...)`. AC1-AC4 in deliverable. Gates the final factory contract change. |

### Spec doc consolidation PR (mechanical, post-merge)

After PR #2376 + the 8 Session 1185 PRs all merge:
- `docs/specs/deliverable_creation_paths.md` Coverage summary table: move all PR-C bucket rows from ⚠️ WARN → 🟡 synthesized (or ✅ wired for the threaded ones). Status header bump to Session 1186.
- Tests count update across the file.

### Inventory refresh PR (still open from Session 1183 close)

`verify_doc_claims --only-drift` still reports 2 high drifts on `core/management/commands/load_all_agents_advisors.py` and `PLATFORM_INVENTORY.md` is now 12+ sessions stale. Mechanical.

### Carryover

PgBouncer follow-up verifications, narrative dedup, agent-name dim checks, retry-policy bulk migrations, `pg_stat_statements` on staging/prod, `capture_pa_acks_health_snapshot` slow-task investigation, COO consolidation deferreds. Live handoffs: `docs/handoffs/SESSION_1171_*` through `SESSION_1185_*`.

## Post-merge worker restart

| PR | Worker restart? | Reason |
|---|---|---|
| #2376 bucket 4 | **YES** | both `tasks_content.py` and `tasks_initiatives.py` are imported by celery worker task bodies (`generate_video_content_pack_task`, `run_initiative_pipeline_task`, `generate_initiative_stage_document`) |

```bash
pkill -9 -f celery; rm -f .celery*.pid; make celery
```

If Session 1185 PRs (#2367-#2374) also merge in the same window, one restart covers all of them.

## Smoke verification (post-merge)

On `pa-10df024c0bd8`:

1. **Callsite A:** dispatch `generate_video_content_pack_task` with a real transcript → `deliverable_tool.detail` shows `provenance.synthesized=true, trigger_source='direct', origin_execution_synthesized=true`; metadata carries `celery_task_name`, `video_id`, `llm_model`.
2. **Callsite B:** trigger an initiative stage advance via `run_initiative_pipeline_task` → external Deliverable shows `parent_object_type='agent_execution', synthesized=false, trigger_source='agent_execution'`; receipt `input_data['source']='initiative_pipeline_task_external_save'`, `celery_task_name='run_initiative_pipeline_task'`; AgentExecution receipt's `parent_object_type='initiative'`.
3. **Callsite C:** dispatch `generate_initiative_stage_document` (via the InitiativeStageGenerator path) → same shape as B but `celery_task_name='generate_initiative_stage_document'`, `agent_invoked=<config['agent']>`.

## Memory updates

No new memories added this session. Existing rules applied throughout:
- `feedback_rigby_comms.md` — every design call routed through pa-10df024c0bd8
- `feedback_corpus_walks_surface_mechanism_drift.md` — surfaced the B.2-vs-B.1 dedupe finding to Rigby instead of silently bridging
- `feedback_factory_silent_none_footgun.md` — helper raises typed exception logged + returns None for fall-through
- `feedback_new_shared_task_needs_worker_restart.md` — flagged in PR description

## Watch checklist for Session 1187 first 30 minutes

1. Disk + swap (per `00-START` READ THIS SECOND): `df -h /System/Volumes/Data`, `sysctl vm.swapusage`.
2. `tools/pa_local.sh "platform_config_tool overview"` → confirm `service_context: local`.
3. `session_tool health_check` on `pa-10df024c0bd8` → at 75/100 at Session 1186 close; will likely rotate to a fresh thread for Session 1187.
4. `gh pr list --author @me --state open` → check how many of the 9 PRs from Sessions 1185-1186 (#2367-#2376) merged.
5. If any merged: `pkill -9 -f celery; rm -f .celery*.pid; make celery`.
6. Decide next direction: PR-D 24h watch (if all 9 PRs merged + 24h elapsed), B.1 unify-deliverables work, spec doc consolidation, inventory refresh, or any new priority.

## Stats

- 1 PR opened (#2376), 3/3 CI checks green
- +463 / -1 LoC (3 files: 2 task files + 1 new test file)
- 10 new tests, 21 total in the provenance program now passing
- 1 design-call round-trip via Rigby (B.2 vs B.1 dedupe finding)
- 2 follow-up deliverables filed in Local QA workspace
- Session 1185 PRs (#2367-#2374) all still open at Session 1186 close
