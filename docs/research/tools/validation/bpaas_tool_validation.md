# `bpaas_tool` — Validation Report (S2908)

**Tool:** `bpaas_tool`
**Schema:** `core/services/pa_tool_schemas.py:5432`
**Handler:** `core/services/td_handlers_agents.py:6268` (`_handle_bpaas`)
**Register site:** `core/services/tool_dispatcher.py:409`
**Session:** S2908 (Path B systematic sweep — Slice 2 batch 4 of `td_handlers_agents`, first mixed-tool-scoped-to-READ_ONLY-subset batch per Fold A shape-break commitment ratified at S2907 close)
**HEAD at validation:** `03ee92d5f`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; mutation actions explicitly excluded — see §5a).
**Rigby SIGN:** S2908 T1 SIGN (pending) — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Build Packet as a Service — the platform's surface for turning a structured "build packet" (client requirements + brand + constraints) into a live project (workspace + repos + preview env + magic link) or into an SOW / delivery checklist / proposal ("close pack"). Introspection actions (`get_schema`, `get_example`) expose the packet contract so downstream callers (agents, forms, docs) can generate valid packets without importing internal constants.

Use `get_schema` when a caller needs the current build-packet JSON schema definition. Use `get_example` when a caller needs a concrete, valid packet reference (Norman Handyman MVP). Mutation actions (`create_project`, `generate_close_pack`) are out of scope for this validation ship — see §5a.

## 2. Covered actions

**READ_ONLY actions covered only (2 of 4 total actions).** Mutation actions (2 excluded — see §5a Mutation containment for the named list, deferral rationale, and planned coverage slice) are out of scope for this ship.

- `get_schema` — **in scope this ship** — verified live via T1a harness. Returns `{success, action, schema}` with `schema` = `BUILD_PACKET_SCHEMA` constant from `core.services.bpaas.build_packet_schema`. Pure in-memory constant read.
- `get_example` — **in scope this ship** — verified live via T1a harness. Returns `{success, action, example}` with `example` = `NORMAN_HANDYMAN_EXAMPLE` constant. Pure in-memory constant read.
- `create_project` — **mutation — deferred to Slice 2 write batch** — see §5a. Classified `MUTATION` in `TOOL_ACTION_METADATA`; harness reports `expected_outcome=skipped_mutation`. Requires workspace + packet lifecycle scaffolding.
- `generate_close_pack` — **mutation — deferred to Slice 2 write batch** — see §5a. Classified `MUTATION` in `TOOL_ACTION_METADATA`; harness reports `expected_outcome=skipped_mutation`. Requires packet fixture.

## 3. Schema notes

- **Required:** `action` (enum: `create_project, generate_close_pack, get_schema, get_example`).
- **Conditional required (handler-enforced):**
  - `workspace_id` + `packet` for `create_project` — fail-loud (structured error envelope) when missing.
  - `packet` for `generate_close_pack` — fail-loud when missing.
- **No required args** for the two READ_ONLY actions (schema pure `action` requirement).
- **Structured error envelope (S2878 migration):** all handler-side failures return `{success: false, error_code, error, action}` — no `TOOL_EXCEPTION` raise-into-500 path. S2874 canonical shape.

## 4. Golden-path examples

**"What does a build packet look like structurally?"**

```
bpaas_tool  action=get_schema
```

**"Show me a working example packet:"**

```
bpaas_tool  action=get_example
```

## 5. Failure / empty-state / pagination notes

- **Structured error envelope** — all failure paths return `{success: false, error_code, error, action}` at HTTP 200. `error_code` values observed in handler: `missing_required_params`, `unknown_action`, `handler_exception`. See handler docstring lines 6275-6281 for S2878 rationale (dispatcher-layer `legacy_error` backfill eliminated).
- **`get_schema` / `get_example`** — no missing-arg path; both return the referenced constant unconditionally. No pagination; both are single-payload constant reads.
- **Unknown action** — returns `{success: false, error_code: 'unknown_action', error: <enum listing>, action}`.

## 5a. Mutation containment (per Rigby T0 SIGN edit — mandatory §5a)

- **Mutating actions excluded this ship:**
  - `create_project` — creates `ProjectWorkspace` + repos + preview env + magic link via `packet_service.create_project_from_packet`. Classified `MUTATION` in `TOOL_ACTION_METADATA` seed this ship.
  - `generate_close_pack` — generates SOW + delivery checklist + proposal via `packet_service.generate_close_pack`. Classified `MUTATION`.
- **Containment mechanism:** `TOOL_ACTION_METADATA` records (added this ship at `core/services/tool_action_metadata.py`) classify both mutations. T1a harness resolves safety class per-action via `resolve_safety()` (see `tool_action_metadata.py:354`) — safety classes `MUTATION` / `WRITE_GATED` / `IRREVERSIBLE` are skipped at dispatch (see `_handle_bpaas` outputs `expected_outcome=skipped_mutation` in harness artifact).
- **dependency_surface note:** `internal` — the mutations invoke `core.services.bpaas.packet_service` in-process; no external bridge or third-party API surface beyond what `packet_service` itself calls.
- **Deferral rationale:** first mixed-scoped batch (S2908 shape-break debut per Chris-ratified Fold A commitment from S2907 close). Mutation coverage requires paired lifecycle scaffolding (workspace substrate for `create_project`; packet fixture for `generate_close_pack`) — deferred to a dedicated mutation-coverage batch when Slice 2 write actions are swept together.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness bpaas_tool` at HEAD `03ee92d5f` (2026-07-23):

- **`get_schema` (6ms):** `response_shape_keys=[action, schema, success]`, `status_code=200`, `expected_outcome=success`. Clean structured envelope.
- **`get_example` (3ms):** `response_shape_keys=[action, example, success]`, `status_code=200`, `expected_outcome=success`. Clean structured envelope.
- **`create_project`:** `expected_outcome=skipped_mutation`, `input_profile=skipped_no_dispatch`. Correctly skipped per S2908 seed.
- **`generate_close_pack`:** `expected_outcome=skipped_mutation`, `input_profile=skipped_no_dispatch`. Correctly skipped per S2908 seed.

Artifact: `docs/audits/pa_tools/harness_output/bpaas_tool.json`.

### 6.2 Runtime-not-executed — this ship

- **`create_project`** — not exercised (MUTATION-skipped). Would create a real `ProjectWorkspace` row + associated substrate; needs paired workspace_id + valid packet fixture.
- **`generate_close_pack`** — not exercised (MUTATION-skipped). Would invoke `packet_service.generate_close_pack` with a valid packet; would produce SOW/checklist/proposal artifacts.
- **`get_schema` shape integrity** — not asserted against a JSON-schema validator this ship (harness only records response shape keys).
- **`get_example` shape integrity** — not asserted against `BUILD_PACKET_SCHEMA` this ship (would confirm the shipped example validates against the shipped schema — a fixture-integrity guarantee).

---

## Related

- **Ledger candidates surfaced this ship:** none new for `bpaas_tool` (structured error envelope is stable since S2878; harness dispatched cleanly with zero drift).
- **Substrate-arc contribution:** two more instances (get_schema, get_example) of clean `{action, X, success}` shape parity — same S2874 canonical envelope pattern as `orm_inspect_tool` and the S2905 revenue tracker family. No classification drift on the `success` branches (contrast `davinci_tool.health/jobs` + `obs_tool.health/status/last` this batch, which surface the S2907 orm_inspect classification-drift pattern).
- **Adjacent tools:** `davinci_tool`, `obs_tool`, `media_tool` (Slice 2 batch 4 peers this ship).
- **Substrate context:** T1b `Template version: v1` sweep variant. First mixed-scoped-to-READ_ONLY-subset ship per Fold A commitment; Rigby T0 SIGN AGREE-with-edits ratified 4-tool batch composition. §5a MUST-include rule adopted per Rigby T0 SIGN edit (template rule to be authored into `_TEMPLATE_per_tool_validation.md` at S2909 substrate follow-up if the pattern sustains).
- **Substrate build history:** S2874 (canonical structured-error-envelope shape); S2876 (breadcrumb telemetry that identified `bpaas_tool.generate_close_pack` as the only real production hit); S2878 (structured envelope migration for `bpaas_tool` — `test_s2878_bpaas_error_envelope.py`).
- **Metadata seed:** `TOOL_ACTION_METADATA` per-action records for all 4 actions added at `core/services/tool_action_metadata.py` this ship (Pattern C — no `TOOL_DEFAULTS` entry; per-action records are the safety source).
