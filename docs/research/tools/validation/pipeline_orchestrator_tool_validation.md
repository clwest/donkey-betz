# `pipeline_orchestrator_tool` — Validation Report (S2911)

**Tool:** `pipeline_orchestrator_tool`
**Schema:** `core/services/pa_tool_schemas.py:167`
**Handler:** `core/services/td_handlers_agents.py:1558` (`_handle_pipeline_orchestrator`)
**Register site:** `core/services/tool_dispatcher.py` (via `AgentHandlersMixin`)
**Session:** S2911 (Path B systematic sweep — Slice 2 batch 6a of `td_handlers_agents`)
**HEAD at validation:** `5d79d8431` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (single READ_ONLY action, fully exercised).
**Rigby SIGN:** S2911 T0 SIGN AGREE-with-edits (batch 6a shape ratified). S2911 T1 SIGN AGREE (Q2 handler-line-1603 unknown-action raise verified; simplest tool in batch).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Report Initiative pipeline status — how many initiatives sit in each of the 5 stages, aggregate status breakdown, and active-initiative count. Answers "what's in the initiative pipeline?" and "how many stage-1/2/3/4/5 initiatives do we have?".

Distinct from `initiatives_tool` (which surfaces per-initiative detail + drives stage advancement) — `pipeline_orchestrator_tool` is a **status-only stub** (per handler docstring, Session 933 audit note). It surfaces aggregate counts from the `Initiative` model; actual pipeline orchestration happens elsewhere (Celery tasks + the initiative 5-stage advancement pipeline). Rigby should pick this tool when the question is "what's the pipeline distribution?" and pick `initiatives_tool` for per-initiative work.

## Covered actions

**All READ_ONLY actions covered (1 of 1 total actions).**

- `status` — **in scope this ship** — verified live via T1a harness (`status_code=200`, `expected_outcome=success`, 24 ms). Returns `{action, pipeline, initiatives_total, initiatives_active, by_stage, by_status}` — full aggregate over the `Initiative` model.

## 3. Schema notes

- **Required:** `action` (enum: `status` — single-value enum).
- **No optional params.**
- **Handler default:** `action` defaults to `'status'` if omitted (handler line 1575) — but schema enforces required.

## 4. Golden-path examples

**"What's the initiative pipeline status?"**

```
pipeline_orchestrator_tool  action=status
```

Response:

```
{
  "action": "status",
  "pipeline": "operational",
  "initiatives_total": <int>,
  "initiatives_active": <int>,      # current_stage<5 AND status='ACTIVE'
  "by_stage": {                     # note: Initiative.current_stage is int 1-5
    "stage_1": <int>,
    "stage_2": <int>,
    "stage_3": <int>,
    "stage_4": <int>,
    "stage_5": <int>
  },
  "by_status": {                    # Initiative.status uses UPPERCASE values
    "ACTIVE": <int>,
    "COMPLETED": <int>,
    ...
  }
}
```

## 5. Failure / empty-state / pagination notes

- **Empty pipeline (no initiatives)** — returns full shape with all counts zero; `by_stage` still has `stage_1` through `stage_5` keys with `0` values; `by_status` is empty dict `{}`.
- **Non-`status` action** — raises `ValueError(f'Unknown action: {action}')` at handler line 1603 → `TOOL_EXCEPTION`. Schema-level enum enforcement prevents this in practice.
- **`pipeline` field** — hardcoded `'operational'`. Not a probe of pipeline health; this is a status label, not a health signal. Callers wanting pipeline-health should route through `dev-ops-observability` agent or `ops_tool`.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness pipeline_orchestrator_tool` at HEAD `5d79d8431` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `status` | `success` | 200 | 24 ms | `action, by_stage, by_status, initiatives_active, initiatives_total, pipeline` |

Artifact: `docs/audits/pa_tools/harness_output/pipeline_orchestrator_tool.json`.

**Envelope-shape observation:** clean single-action tool. No mutation surface. No bridge dependency. All shape keys stable per Session 933 audit.

### 6.2 Runtime-not-executed — this ship

- **`status` with populated Initiative corpus** — response keys were verified live, but stage/status counts were not asserted against known-populated data. The current inventory (94 enabled + 5 disabled PeriodicTasks; unrelated but comparable substrate size) suggests a modest but non-empty Initiative table.
- **`pipeline` field always returns `'operational'`** — value not exercised against a "degraded" or "failed" scenario. Handler has no branch for anything other than the hardcoded string. Callers seeking pipeline-health need a different tool.

---

## Related

- **Ledger candidates surfaced this ship:** none new. Clean single-action READ_ONLY tool with stable envelope shape. Handler docstring already documents the "status-only stub" limitation (Session 933 audit).
- **Adjacent tools:**
  - `initiatives_tool` — per-initiative detail + stage advancement (the actual pipeline-work surface).
  - `ops_tool` — pipeline-adjacent ops-console surfaces (recycles, gates, celery-task events).
  - `dev-ops-observability` agent — cross-service health triage (for the actual "is the pipeline healthy?" question).
- **Substrate context:** third tool in Slice 2 batch 6a. Simplest tool in the batch (single R action; peer to `web_search` / `web_fetch_tool` / other actionless-or-single-action tools from prior batches). Full-category upgrade (not partial, since no mutation actions exist).
- **Metadata seed:** 1 per-action `TOOL_ACTION_METADATA` record at `core/services/tool_action_metadata.py` this ship (Pattern C — per-action, chosen for batch-uniformity even though a `TOOL_DEFAULTS` entry would also have worked for this single-R-action tool).
