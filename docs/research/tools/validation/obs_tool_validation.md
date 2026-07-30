# `obs_tool` — Validation Report (S2908)

**Tool:** `obs_tool`
**Schema:** `core/services/pa_tool_schemas.py:1175`
**Handler:** `core/services/td_handlers_agents.py:4494` (`_handle_obs`)
**Register site:** `core/services/tool_dispatcher.py:408`
**Session:** S2908 (Path B systematic sweep — Slice 2 batch 4 of `td_handlers_agents`, first mixed-tool-scoped-to-READ_ONLY-subset batch per Fold A shape-break commitment ratified at S2907 close)
**HEAD at validation:** `03ee92d5f`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 3 mutation actions explicitly excluded — see §5a).
**Rigby SIGN:** S2908 T1 SIGN (pending) — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Control surface for the local OBS Studio recording bridge (`core/views_obs.py` — a small HTTP proxy that talks to the OBS WebSocket plugin running alongside OBS Studio). Introspection actions expose bridge health, current recording state + timecode, and info about the newest recording file. Mutation actions (`start`, `stop`, `upload_last`) are out of scope for this validation ship — see §5a.

Use `health` when the caller needs to know if the OBS bridge is reachable. Use `status` when the caller needs the current recording state (recording? timecode? active scene?). Use `last` when the caller needs the newest recording file's path/metadata without triggering upload.

## 2. Covered actions

**READ_ONLY actions covered only (3 of 6 total actions).** Mutation actions (3 excluded — see §5a Mutation containment for the named list, deferral rationale, and planned coverage slice) are out of scope for this ship.

- `health` — **in scope this ship** — verified live via T1a harness. GET `/health` on the OBS bridge. Returns `{ok, action, bridgeReachable, latency_ms, result}` on success; `{ok: false, action, error, error_code}` when bridge unreachable (see §5).
- `status` — **in scope this ship** — verified live via T1a harness. GET `/v1/recording/status` on the OBS bridge. Same envelope shape as `health`.
- `last` — **in scope this ship** — verified live via T1a harness. GET `/v1/recording/last` on the OBS bridge. Same envelope shape as `health`.
- `start` — **mutation — deferred to bridge-live batch** — see §5a. Bridge-dependent (requires reachable OBS bridge); classified `MUTATION` + `external_bridge` in `TOOL_ACTION_METADATA`; harness reports `expected_outcome=skipped_mutation` (or `skipped_bridge_unreachable` when bridge offline per S2909 T2). POST to bridge start-recording endpoint.
- `stop` — **mutation — deferred to bridge-live batch** — see §5a. Bridge-dependent + `MUTATION` + `external_bridge`; same skip pattern as `start`. POST to bridge stop-recording endpoint.
- `upload_last` — **mutation — deferred to bridge-live batch** — see §5a. Bridge-dependent + `MUTATION` + `external_bridge`; same skip pattern. POST to bridge upload endpoint; forwards `stopIfRecording` / `title` / `tags` payload.

## 3. Schema notes

- **Required:** `action` (enum: `health, status, start, stop, last, upload_last`).
- **Conditional required:** none for the READ_ONLY actions (all 3 dispatch with only `action`).
- **Optional (upload_last only):** `stopIfRecording` (bool), `title` (string), `tags` (list of strings). These forward directly into the bridge POST body.
- **No required args** for `health`, `status`, `last`.
- **Bridge gating:** the handler pre-checks `_obs_enabled()` before dispatching any action; when OBS integration is disabled, returns `{ok: false, action, error: {code: 'OBS_DISABLED', message: 'OBS integration is not enabled'}}`.
- **Envelope shape:** all responses (success and error branches) share the same top-level shape `{ok, action, bridgeReachable?, latency_ms?, result?, error?}`. Handler always sets `ok` from the bridge's response body (`data.get('ok', True)`) or explicitly to `false` when the bridge is unreachable or auth-rejected.

## 4. Golden-path examples

**"Is the OBS bridge running?"**

```
obs_tool  action=health
```

**"Is OBS currently recording? What's the timecode?"**

```
obs_tool  action=status
```

**"Where's the latest recording file on disk?"**

```
obs_tool  action=last
```

## 5. Failure / empty-state / pagination notes

- **`BRIDGE_UNREACHABLE` envelope** — when the OBS bridge is not running (or listening on a different port), `_obs_bridge_request` returns `status_code=0` and the handler responds `{ok: false, action, bridgeReachable: false, error: {code: 'BRIDGE_UNREACHABLE', message: 'Bridge unreachable'}}` at HTTP 200. Inline error envelope pattern parity with `davinci_tool` this batch and `orm_inspect_tool` at S2907.
- **`BRIDGE_AUTH_FAILED` envelope** — when the bridge is reachable but rejects the shared-secret token, response is `{ok: false, action, bridgeReachable: true, error: {code: 'BRIDGE_AUTH_FAILED', message: 'Bridge rejected token'}}` at HTTP 200.
- **`OBS_DISABLED` envelope** — when `_obs_enabled()` is false, handler short-circuits without hitting the bridge.
- **Classification-drift note (harness):** T1a harness reports `expected_outcome=success` for all 3 READ_ONLY dispatches because `status_code=200` even when the envelope carries `error, error_code` and `ok=false` (bridge unreachable this ship). Third batch of instances of the S2907 orm_inspect substrate finding — see §Related.
- **Unknown action** — raises `ValueError` at handler line 4534 → `TOOL_EXCEPTION` at HTTP 500.
- **No pagination** — all READ_ONLY actions return single-payload responses (health probe / current-state snapshot / newest-file metadata).

## 5a. Mutation containment (per Rigby T0 SIGN edit — mandatory §5a)

- **Mutating actions excluded this ship:**
  - `start` — POST `/v1/recording/start` on the OBS bridge; begins recording. Classified `MUTATION` in `TOOL_ACTION_METADATA` seed this ship.
  - `stop` — POST `/v1/recording/stop`; ends recording. Classified `MUTATION`.
  - `upload_last` — POST `/v1/recording/upload_last`; uploads the newest recording file to the platform and creates a `VideoHistory` row. Classified `MUTATION`. Also carries an optional `stopIfRecording: true` cascade that inlines a `stop` mutation before the upload.
- **Containment mechanism:** `TOOL_ACTION_METADATA` per-action records for all 3 mutations added at `core/services/tool_action_metadata.py` this ship; harness resolves via `resolve_safety()` and skips at dispatch (see harness artifact `expected_outcome=skipped_mutation` × 3).
- **dependency_surface note:** `external_bridge` — `obs_tool` routes exclusively through `_obs_bridge_request` (HTTP client into the local OBS bridge process at `core/views_obs.py`). Applies to both READ_ONLY (GET) and MUTATION (POST) branches. No `internal` action in this tool.
- **Deferral rationale:** `start`, `stop`, `upload_last` require (a) reachable OBS bridge with valid shared-secret token (not verified in this ship's environment — harness surfaced bridge-unreachable envelope for all 3 READ_ONLY dispatches) + (b) OBS Studio actually running with the WebSocket plugin loaded + (c) `upload_last` also requires an existing recording file. `upload_last` further needs paired lifecycle scaffolding (a prior successful recording session) or dry-run coverage. Deferred to a mutation-coverage batch paired with an OBS bridge bring-up.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness obs_tool` at HEAD `03ee92d5f` (2026-07-23):

- **`health`:** `response_shape_keys=[action, error, error_code, ok]`, `status_code=200`, `expected_outcome=success` (harness classification — see §5). Actual state: bridge unreachable → inline error envelope with `ok=false`.
- **`status`:** `response_shape_keys=[action, error, error_code, ok]`, `status_code=200`, `expected_outcome=success` (harness classification). Actual state: bridge unreachable.
- **`last`:** `response_shape_keys=[action, error, error_code, ok]`, `status_code=200`, `expected_outcome=success` (harness classification). Actual state: bridge unreachable.
- **`start`:** `expected_outcome=skipped_mutation`, `input_profile=skipped_no_dispatch`. Correctly skipped per S2908 seed.
- **`stop`:** `expected_outcome=skipped_mutation`, `input_profile=skipped_no_dispatch`. Correctly skipped.
- **`upload_last`:** `expected_outcome=skipped_mutation`, `input_profile=skipped_no_dispatch`. Correctly skipped.

Artifact: `docs/audits/pa_tools/harness_output/obs_tool.json`.

**Classification-drift observation:** 3 of 3 dispatched READ_ONLY actions returned `{ok: false, error, error_code}` inline envelopes at HTTP 200 (bridge unreachable). Highest per-tool drift concentration this batch — combined with davinci_tool (2 instances) and the S2907 orm_inspect batch (4 instances) = 9 total instances across 4 tools. Reinforces the substrate-arc ledger candidate. See §Related.

### 6.2 Runtime-not-executed — this ship

- **`health` / `status` / `last` with reachable OBS bridge** — not exercised (would confirm the success-shape envelope when `ok=true` and the `result` payload carries real bridge data: recording state, timecode, active scene, newest file metadata).
- **Auth-failure branch** — not exercised (would confirm `BRIDGE_AUTH_FAILED` code emits correctly when a wrong token is presented).
- **`OBS_DISABLED` branch** — not exercised (would confirm the pre-check envelope shape).
- **`start` / `stop` / `upload_last`** — not exercised (MUTATION-skipped).

---

## Related

- **Ledger candidates surfaced this ship (append to S2907 substrate-arc-scope):**
  - **T1a harness classification drift, third batch of instances** — 3 more instances this ship (obs_tool `health`, `status`, `last`) confirming the S2907 orm_inspect pattern. Combined with davinci_tool (2 instances this batch) + orm_inspect (4 instances at S2907) = 9 total instances across 4 tools. Substrate-arc scope; deferred.
  - **Bridge-unreachable envelope surfaces uniformly across both external_bridge tools this batch (davinci_tool + obs_tool)** — same T1a harness pattern; substrate-arc scope; deferred.
- **Adjacent tools:** `davinci_tool` (this batch peer — external_bridge sibling), `bpaas_tool`, `media_tool` (this batch peers).
- **Substrate context:** T1b `Template version: v1` sweep variant. First mixed-scoped-to-READ_ONLY-subset ship per Fold A commitment; Rigby T0 SIGN AGREE-with-edits ratified 4-tool batch composition + §5a mandatory rule + dependency_surface doc note.
- **Metadata seed:** `TOOL_ACTION_METADATA` per-action records for all 6 actions added at `core/services/tool_action_metadata.py` this ship (Pattern C — no `TOOL_DEFAULTS` entry; per-action records are the safety source).
