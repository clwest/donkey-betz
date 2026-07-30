# `davinci_tool` — Validation Report (S2908)

**Tool:** `davinci_tool`
**Schema:** `core/services/pa_tool_schemas.py:1135`
**Handler:** `core/services/td_handlers_agents.py:4435` (`_handle_davinci`)
**Register site:** `core/services/tool_dispatcher.py:407`
**Session:** S2908 (Path B systematic sweep — Slice 2 batch 4 of `td_handlers_agents`, first mixed-tool-scoped-to-READ_ONLY-subset batch per Fold A shape-break commitment ratified at S2907 close)
**HEAD at validation:** `03ee92d5f`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; mutation action explicitly excluded — see §5a).
**Rigby SIGN:** S2908 T1 SIGN (pending) — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Control surface for the DaVinci Resolve rendering + color-grading node (`resolve_node/` — a local HTTP service the PA calls via `ResolveNodeClient`). Introspection actions expose bridge health, render-job status/result URLs, active job listings, and the color-grade preset catalog. Rendering itself (`render`) is the mutation surface and is out of scope for this validation ship — see §5a.

Use `health` when the caller needs to know if the resolve_node service is reachable. Use `jobs` to list all render jobs currently tracked by the node. Use `status` + `result` (both need `job_id`) to check progress + fetch the finished-render download URL. Use `grades` to enumerate the trend-matched color grade presets available.

## 2. Covered actions

**READ_ONLY actions covered only (5 of 6 total actions).** Mutation action (1 excluded — see §5a Mutation containment for the named action, deferral rationale, and planned coverage slice) is out of scope for this ship.

- `health` — **in scope this ship** — verified live via T1a harness. Returns `{action, ...}` with `ResolveNodeClient.health_check()` payload. When the node is unreachable, response envelope carries `error` + `error_code` at HTTP 200 (see §5 classification-drift note).
- `status` — **in scope this ship** — verified live via T1a harness error path (requires `job_id`). Raises `ValueError` when `job_id` missing → dispatcher wraps as `TOOL_EXCEPTION` at HTTP 500.
- `result` — **in scope this ship** — verified live via T1a harness error path (requires `job_id`). Same fail-loud pattern as `status`.
- `jobs` — **in scope this ship** — verified live via T1a harness. Returns `{action, jobs, ...}` with `ResolveNodeClient.list_jobs()` payload. Same classification-drift pattern as `health` when node unreachable.
- `grades` — **in scope this ship** — verified live via T1a harness. Returns `{action, count, grades}` — enumerates `COLOR_GRADE_PRESETS` constant from `resolve_node.color_grades`. Pure in-memory constant read, dispatched independently of node reachability.
- `render` — **mutation — deferred to bridge-live batch** — see §5a. Bridge-dependent (requires reachable resolve_node); classified `MUTATION` + `external_bridge` in `TOOL_ACTION_METADATA`; harness reports `expected_outcome=skipped_mutation` (or `skipped_bridge_unreachable` when node offline per S2909 T2). Submits a render job to the resolve_node bridge.

## 3. Schema notes

- **Required:** `action` (enum: `health, render, status, result, jobs, grades`).
- **Conditional required (handler-enforced):**
  - `clip_paths` for `render` — fail-loud via `ValueError` when missing.
  - `job_id` for `status` + `result` — fail-loud via `ValueError` when missing.
- **Optional:** `template` (enum: `default_mp4, high_quality` — default `default_mp4`), `timeline_name` (string), `color_grade` (preset name).
- **No required args** for `health`, `jobs`, `grades`.
- **Error handling:** the READ_ONLY branches use different envelope shapes:
  - `grades` returns a pure success shape `{action, count, grades}` — no error envelope wrapper.
  - `health` + `jobs` return `{action, ..., error, error_code}` when the underlying `ResolveNodeClient` HTTP call fails (bridge unreachable) — inline error envelope at HTTP 200.
  - `status` + `result` fail via `ValueError` (dispatcher-wrapped `TOOL_EXCEPTION` at HTTP 500).

## 4. Golden-path examples

**"Is the render node online?"**

```
davinci_tool  action=health
```

**"What jobs are running right now?"**

```
davinci_tool  action=jobs
```

**"What color grade presets can I apply?"**

```
davinci_tool  action=grades
```

**"How far along is job X?"**

```
davinci_tool  action=status  job_id=<uuid>
```

**"Where can I download job X's output?"**

```
davinci_tool  action=result  job_id=<uuid>
```

## 5. Failure / empty-state / pagination notes

- **`health` / `jobs` inline error envelope (bridge unreachable):** when `resolve_node/` is not running locally, `ResolveNodeClient.health_check()` and `list_jobs()` return `{ok: false, error, error_code}` and the handler merges those into the response shape `{action, error, error_code, status/jobs}` at HTTP 200. Envelope pattern parity with `obs_tool` (this batch) and `orm_inspect_tool` (S2907).
- **Classification-drift note (harness):** the T1a harness's status_code-only outcome classifier reports `expected_outcome=success` for `health` + `jobs` responses that actually carry `error, error_code` keys — same S2907 orm_inspect substrate finding surfaces here. See §Related.
- **`status` / `result` fail-loud on missing `job_id`:** raises `ValueError` — dispatcher wraps as `TOOL_EXCEPTION` at HTTP 500. Fail-loud pattern distinct from `health` / `jobs` inline-envelope pattern (this shape inconsistency is inherited from `ResolveNodeClient` error surfacing, not a handler defect).
- **`grades` never errors** — enumerates in-memory `COLOR_GRADE_PRESETS` dict; guaranteed clean success shape.
- **Unknown action** — raises `ValueError` → `TOOL_EXCEPTION` at HTTP 500.
- **No pagination** — `jobs` and `grades` return full enumerations (both bounded by underlying data cardinality; not enum-capped in the handler).

## 5a. Mutation containment (per Rigby T0 SIGN edit — mandatory §5a)

- **Mutating action excluded this ship:**
  - `render` — starts an asynchronous render job on the external DaVinci Resolve system via `ResolveNodeClient.start_render(clip_paths, template, timeline_name)`. Classified `MUTATION` in `TOOL_ACTION_METADATA` seed this ship.
- **Containment mechanism:** `TOOL_ACTION_METADATA` per-action record with `safety_class='MUTATION'` this ship; harness resolves via `resolve_safety()` and skips at dispatch (see harness artifact `expected_outcome=skipped_mutation`).
- **dependency_surface note:** `external_bridge` — `davinci_tool` routes exclusively through `ResolveNodeClient` (HTTP client into the local `resolve_node/` service). Includes the READ_ONLY branches (health, status, result, jobs — bridge-mediated) as well as the excluded `render` mutation. Only `grades` is `internal` (constant-only read; no bridge call).
- **Deferral rationale:** `render` requires (a) reachable `resolve_node/` bridge (not verified in this ship's environment — health branch surfaced bridge-unreachable envelope at harness time) + (b) real `clip_paths` fixtures + (c) render-time budget (async job creation with subsequent status polling). Deferred to a mutation-coverage batch paired with a resolve_node/ bring-up.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness davinci_tool` at HEAD `03ee92d5f` (2026-07-23):

- **`health` (7ms):** `response_shape_keys=[action, error, error_code, status]`, `status_code=200`, `expected_outcome=success` (harness classification — see §5). Actual state: bridge unreachable → inline error envelope.
- **`status` (6ms):** `response_shape_keys=[]`, `status_code=500`, `expected_outcome=error_captured`, `notes=error_code=TOOL_EXCEPTION; msg=job_id required for status action`. Correct fail-loud.
- **`result` (2ms):** `response_shape_keys=[]`, `status_code=500`, `expected_outcome=error_captured`, `notes=error_code=TOOL_EXCEPTION; msg=job_id required for result action`. Correct fail-loud.
- **`jobs` (5ms):** `response_shape_keys=[action, error, error_code, jobs]`, `status_code=200`, `expected_outcome=success` (harness classification). Actual state: bridge unreachable → inline error envelope with `jobs` key present but likely empty/null.
- **`grades` (4ms):** `response_shape_keys=[action, count, grades]`, `status_code=200`, `expected_outcome=success`. Clean shape — no bridge dependency.
- **`render`:** `expected_outcome=skipped_mutation`, `input_profile=skipped_no_dispatch`. Correctly skipped per S2908 seed.

Artifact: `docs/audits/pa_tools/harness_output/davinci_tool.json`.

**Classification-drift observation:** 2 of 5 dispatched READ_ONLY actions (`health`, `jobs`) return inline `{error, error_code}` envelopes at HTTP 200 — the S2907 orm_inspect classification-drift pattern surfaces again. Combined with 3 obs_tool instances this batch = 5 new drift instances this ship (adds to the 4 orm_inspect instances at S2907). Reinforces the substrate-arc ledger candidate. See §Related.

### 6.2 Runtime-not-executed — this ship

- **`health` / `jobs` with reachable bridge** — not exercised (would confirm the success-shape envelope when `ok=true` and the `status/jobs` payloads carry real data).
- **`status` / `result` with a real `job_id`** — not exercised (would confirm the ResolveNodeClient status/result payload shape end-to-end).
- **`grades` shape drift check** — not asserted against `COLOR_GRADE_PRESETS` schema.
- **`render`** — not exercised (MUTATION-skipped).

---

## Related

- **Ledger candidates surfaced this ship (append to S2907 substrate-arc-scope):**
  - **T1a harness classification drift, second batch of instances** — 5 more instances this ship (davinci_tool `health` + `jobs`; obs_tool `health` + `status` + `last`) confirming the S2907 orm_inspect pattern (`status_code=200` + `{ok:false, error, error_code}` inline envelope misclassified as `success`). Cumulative: 9 instances across 4 tools (orm_inspect × 4, davinci × 2, obs × 3). Substrate-arc scope; deferred.
  - **Bridge-unreachable-during-harness detection gap** — davinci_tool `health` + obs_tool `health` both dispatched at HTTP 200 with `error` in the envelope because the underlying local bridge (`resolve_node/`, OBS bridge) was not running. Harness has no bridge-availability precheck; classification drift compounds this. Substrate-arc scope; deferred.
- **Adjacent tools:** `obs_tool` (this batch peer — external_bridge sibling), `bpaas_tool`, `media_tool` (this batch peers).
- **Substrate context:** T1b `Template version: v1` sweep variant. First mixed-scoped-to-READ_ONLY-subset ship per Fold A commitment; Rigby T0 SIGN AGREE-with-edits ratified 4-tool batch composition + §5a mandatory rule + dependency_surface doc note.
- **Metadata seed:** `TOOL_ACTION_METADATA` per-action records for all 6 actions added at `core/services/tool_action_metadata.py` this ship (Pattern C — no `TOOL_DEFAULTS` entry; per-action records are the safety source).
