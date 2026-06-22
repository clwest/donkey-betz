# Session 1200 — Day-0 inference accuracy watch pre-flight + factory-entry instrumentation

**Status:** Closed clean. **1 PR merged on `main`** (#2439); Day-0 readiness done; runbook + instrumentation in place before the 2026-06-23 watch open.
**Date:** 2026-06-22
**Active conversation:** `pa-1ccc494ea00b4e77` (spun by Rigby at Session 1199 close — titled "Session 1200 — Watch Tracking + Phase 2 Gate (Plan C)").
**Prior session:** [`SESSION_1199_INFERENCE_STEP2_PROVENANCE_FLIP_AND_INFRA_CLEANUP.md`](./SESSION_1199_INFERENCE_STEP2_PROVENANCE_FLIP_AND_INFRA_CLEANUP.md).

## TL;DR

Day-0 of the inference accuracy watch shipped pre-flight + instrumentation. Day-0 verification surfaced a mechanism finding: `INFERENCE-MATCH` will fire rarely in normal production because BaseAgent's 3-source `initiative_id` resolution typically forwards initiative_id explicitly to the factory, short-circuiting inference. Rigby reframed the watch as **accuracy conditional on eligibility (C/B)** rather than raw volume. PR #2439 instrumented `deliverable_factory.create_deliverable` with a single structured entry log so A/B/C are observable directly from logs instead of via a noisy DB proxy. Runbook deliverable `cb9d8ae1-…` updated post-merge to reflect the log-based protocol.

## PRs shipped

| PR | Commit | Theme | Deliverable closed |
|---|---|---|---|
| **#2439** | `c147b224` | `deliverable_factory` entry-log instrumentation — single `[DELIVERABLE-FACTORY-ENTRY]` line at function entry, before any gate or DB work | — (Day-0 watch readiness) |

## Behavioral invariants — what's now true post-merge

- Every call to `deliverable_factory.create_deliverable` writes one structured `[DELIVERABLE-FACTORY-ENTRY]` line at INFO level on logger `core.services.deliverable_factory`, regardless of whether the call later passes or fails the quality gate, provenance check, or inference cascade.
- Fields are stable + snake_case: `agent`, `workspace`, `initiative_id_present`, `tool_context_initiative_id_present`, `initiative_source` (`explicit_kwarg|none`), `has_provenance`.
- The watch's denominator `A` is now observable directly via `grep '[DELIVERABLE-FACTORY-ENTRY]' celery*.log | wc -l`; the eligible-for-inference subset `B` is `grep ... | grep initiative_id_present=False | wc -l`. No DB query needed.
- The existing `[INFERENCE-MATCH] agent=... step=N reason=... confidence=...` emit (the `C` count) is unchanged.

## Rollback / disable levers

- **Full revert:** `git revert c147b224` (single-file 23-line addition; isolated).
- **Soften:** the new emit is wrapped in a non-raising path (tool_context lookup defensively `try/except`s), so an instrumentation regression cannot block a deliverable write. Worst case is the entry line is missing — no functional impact.
- **No per-callsite override needed** — emits unconditionally at factory entry.

## Mechanism findings (Day-0 verification record)

1. **Neither watch has a Celery beat entry.** Direct check via `PeriodicTask.objects.filter(name__iregex='inference|initiative.kind|default.only|report_init')` returned `[]`. Both the inference accuracy watch and the `default_only_projects` detector are **manual operator actions**. Runbook updated to reflect this.

2. **Session-boundary trap caught + corrected.** Workers at Session 1200 open had started `Sun Jun 21 20:03:32`, predating Session 1199 PR merges by ~4.5 hours. INFERENCE-MATCH count in `celery.log`: 0. Workers restarted at `Mon Jun 22 00:50:44` to load post-merge code before continuing.

3. **Step 2 isolated path proven** (in-process direct test, contextvar-only):
   - `infer_initiative_id` returns `step=2, confidence=0.95, reason=explicit_match` when `tool_context_scope` carries `initiative_id`.
   - Contextvar correctly resets outside scope.

4. **PR-D contract honest — no bypass.** Initial alarm on `parent_execution_id: None` was a false reading; the Deliverable model uses Session 843's generic-FK fields (`parent_object_type`, `parent_object_id`), not a literal `parent_execution_id` column. Raw DB query on the smoke deliverable `dfe90e26-…` confirmed `parent_object_type='agent_execution'` + `parent_object_id=<exec_id>` correctly populated. Phase 2 hard-reject flip on 2026-06-29 is safe to ship from this evidence.

5. **Step 2 is structurally rare-by-design.** ContentWriterAgent's deliverable path (`core/agents/content_writer_agent.py:846-848`) reads `context.initiative_id` and forwards as `expected_initiative_id`, short-circuiting inference. More universally, `core/agents/base_agent.py:4290-4294` does the same 3-source resolution (`explicit kwarg | exec_context | metadata`) for every agent that inherits from BaseAgent. Surface-area enumeration of top-11 deliverable-creating agents (last 30d) shows:

   | Agent | Δs (30d) | Step-2 eligible? |
   |---|---|---|
   | Rigby (PA) | 59 | Mixed — handler-dependent in `td_handlers_content.py` |
   | ResearchAgent | 55 | Yes if `context.initiative_id is None` |
   | ContentWriterAgent | 18 | Rarely (eager bypass) |
   | ClaudeCode | 11 | Yes if `context.initiative_id is None` |
   | NewsletterTool / COO / CTO / DevOps / Thinking / Editor / PA | 2-6 each | Mixed — see runbook deliverable §5 |

   Realistic Step-2 firing surface: operator/UI flows where outer tool-call payload sets `initiative_id` on the contextvar but the agent's exec_context is left without it. PR #2439's `tool_context_initiative_id_present` field lets us measure this subset directly.

6. **Bonus signal — ORPHAN-DELIVERABLE diagnostic** fires when ENTRY shows `initiative_id_present=False AND tool_context_initiative_id_present=False AND` no agent affinity match. Smoke deliverable `3ed7eebb-…` tripped this exactly as Plan C Phase 1 designed. Runbook §6 notes the optional `D = ORPHANs / B` ratio as a "post-cascade failure" signal.

## Day-0 protocol artifacts

- **Runbook deliverable:** `cb9d8ae1-008e-42e8-b222-3f598e6b665e` ("Inference Accuracy Watch — Operator Runbook (Session 1200)"). Authored as a 9-section stub by Claude, polished + finalized by Rigby; final length 8,728 chars; category Ops; tagged session-1200, runbook, inference-watch.
- **Smoke deliverables (post-PR #2439):**
  - `dfe90e26-54b8-474e-b010-6eb5b8d18e45` (ContentWriterAgent — proved Step-2 bypass via `expected_initiative_id` forward)
  - `3ed7eebb-75f2-4d72-9671-9ddb0fb1cb89` (Rigby `deliverable_tool.create` — proved entry log line + ORPHAN diagnostic)
- **Daily append target unchanged:** Deliverable `9ba58690-…` (DBZ workspace, linked to SPINE_1).

## Tools / config touched

- `tools/pa_local.sh` — `--conversation` flag pinned to `pa-1ccc494ea00b4e77` (Session 1200 thread). Prior pin `pa-ea12236c83eb4826` (Sessions 1196-1199) retired.

## 24h watch checklist (instrumentation)

```bash
# Confirm post-restart workers are on PR #2439 code
ps -eo pid,lstart | grep celery   # should be >= 2026-06-22 01:15:17
git log -1 --format='%h %ci' main | head -1   # expect c147b224 or later

# Day-1 baseline (run 2026-06-23 morning)
grep '\[DELIVERABLE-FACTORY-ENTRY\]' celery*.log | wc -l                                  # A
grep '\[DELIVERABLE-FACTORY-ENTRY\]' celery*.log | grep 'initiative_id_present=False' | wc -l  # B
grep '\[INFERENCE-MATCH\] agent=' celery*.log | wc -l                                     # C
grep '\[ORPHAN-DELIVERABLE\] code=missing_initiative_id' celery*.log | wc -l              # D (bonus)
```

Watch precision target per spec §5: C/B ≥ 80% precision per seed, evaluated daily.

## Carryover into Session 1201

| Item | Priority | Where it's defined |
|---|---|---|
| **Day-1 inference accuracy + default_only_projects watch appends** | **P1 (active 2026-06-23 → 2026-06-29)** | Append A/B/C/D + `report_initiative_kinds` output per runbook deliverable `cb9d8ae1-…` |
| **Day-8 watch aggregation + decision (2026-06-30)** | **P1 (time-gated)** | Per-seed decision: keep / tighten / pull. File as deliverable tagged `session-1198-watch-result` |
| **Plan C Phase 2 hard-reject flip (2026-06-29)** | **P1 (time-gated)** | After 7-day watch clean, replace Phase 1 diagnostic mark with `OrphanDeliverableError`. Now safer post-§6.2 Steps 1-3 + PR #2439 visibility |
| **Session 1196 7-day watch (2026-06-29)** | **P1 (time-gated)** | Re-run `backfill_initiative_workspace_links --json-only`; diff against 2026-06-22 baseline |
| **PR3 — Step 4 heuristics implementation** | P2 | After Day-8 watch decision (≥80% precision on Step 3 → unblock PR3) |
| **Production rollout: Sessions 1196-1200 cumulative** | **P0 (carryover, gated on Chris)** | Local-only until Chris flips |
| **Migration drift audit (Set A + Set B)** | P2/P3 | 4 unmigrated `Narrative*` models + 16 `AlterField` ops |
| **Initiative kind UI filter + affinity admin** | P3 | Frontend surface for Sessions 1197-1199 backend |

## Memory rules touched / surfaced

- `feedback_new_shared_task_needs_worker_restart` (case 3, session-boundary trap) — fired on Session 1200 open, workers restarted before Day-0 verification began.
- `feedback_corpus_walks_surface_mechanism_drift` — Day-0 Step-2 firing surface finding surfaced honestly via Rigby thread instead of quietly bridged.
- `feedback_factory_silent_none_footgun` — referenced in runbook §4 "failure modes" so operators don't confuse gate-rejected-silently with inference broken.
- `feedback_deliverable_tool_use_append_for_large_payloads` — runbook deliverable hit one `update` failure post-6kB; Rigby switched to `append` per the rule.

## Notes for Session 1201 open

- First PA call: confirm `service_context: local` via `platform_config_tool overview` (continues the pattern from Sessions 1196-1200).
- Day-1 watch begins. Append findings to deliverable `9ba58690-…` (DBZ workspace, linked to SPINE_1) using the runbook protocol from `cb9d8ae1-…`.
- Both time-gated 2026-06-29 items fire 7 days into Session 1201.
