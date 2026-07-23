# `platform_awareness_tool` — Validation Report (S2913)

**Tool:** `platform_awareness_tool`
**Schema:** `core/services/pa_tool_schemas.py:1492`
**Handler:** `core/services/td_handlers_core.py:823` (`_handle_platform_awareness`)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2913 (Path B systematic sweep — Slice 3 batch 1 of `td_handlers_core`, first mixed-safety scoped-to-READ_ONLY-subset ship of the slice)
**HEAD at validation:** `cff587f50` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 1 MUTATION action `verify_deploy` explicitly excluded — see §5a).
**Rigby SIGN:** S2913 T0 SIGN AGREE-with-edits (batch 1 composition + scoped-to-READ_ONLY subset shape ratified per Q1 (c)→(b) actionless-first; Q2 bridge-suspect scan confirmed `verify_deploy` uses HTTP via `run_verification` — excluded from opener). S2913 T1 SIGN AGREE-with-edits (V1 side-effect-free scan clean + V2 explicit-action-pinning applied + V3 Concern C 1st-instance forward-carry note per GAP_MAP `actions_not_mentioned_in_description` flag).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Enumerate platform capabilities: UI routes, studios, feature-flag capabilities, PA tool registry, and deploy verification. Answers "what pages exist?", "what features are available?", "list mutation endpoints for a given route", "list all PA tools", and (admin-only) "verify the deploy against a live URL."

Distinct from `platform_config_tool` (runtime configuration snapshot — provider keys, env vars, feature-flag values) and `db_health_tool` (DB migration + schema introspection). `platform_awareness_tool` reads the *shape* of the platform (routes, capabilities, tool schemas), not the runtime configuration or database health.

## Covered actions

**READ_ONLY actions covered only (6 of 7 total actions).** 1 MUTATION action (`verify_deploy` — excluded — see §5a) is out of scope for this ship.

- `get_manifest` — **in scope this ship** — verified live via T1a harness (`status_code=200`, `expected_outcome=success`, 8 ms). Returns the full manifest via `core.views_app_manifest.get_manifest_data(user)` / `_load_manifest()` — RBAC-filtered when `user_id` present.
- `list_routes` — **in scope this ship** — verified live via T1a harness (`success`, 3 ms). Returns filtered `manifest.routes` slice with optional `category` + `auth_required` filters.
- `check_route` — **in scope this ship** — verified live via T1a harness (`success`, 2 ms). Empty-string `path` misses; returns `{exists, path}`.
- `system_overview` — **in scope this ship** — verified live via T1a harness (`success`, 2 ms). Returns aggregate route+studio+capability counts + `build_sha`.
- `list_api_dependencies` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Optional `path` filter + `writes_only` filter for mutation endpoints only.
- `tool_registry` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Returns registered PA tool names + descriptions + action enums via `_summarize_tool_schemas`.
- `verify_deploy` — **mutation — deferred to future MUTATION-coverage batch** — see §5a

## 3. Schema notes

- **Required:** `action` (enum: `get_manifest, list_routes, check_route, system_overview, verify_deploy, list_api_dependencies, tool_registry`).
- **Conditional required (handler-enforced, per action):**
  - `path` for `check_route` (empty string always misses cleanly; no fail-loud).
  - Caller must be `is_superuser or is_staff` for `verify_deploy` — otherwise returns `{'error': 'Admin access required for deploy verification'}`.
- **Optional filters (`list_routes`):** `category` (enum: `command, studio, intelligence, domain, reference, admin, auth`) + `auth_required` (`bool | string`). `auth_required` handling uses `coerce_optional_bool` per Session 1228 PR-A to defend against LLM-autofill `False` (a truthy Python `False` is treated as omission; the string `'false'` is treated as public-only filter).
- **Optional filters (`list_api_dependencies`):** `path` (route to filter by) + `writes_only` (bool; mutation endpoints only).
- **Schema description drift note** — GAP_MAP flags this tool as `actions_not_mentioned_in_description` (schema `description` field does not enumerate the 7 actions; the `action` enum + inline sub-description handle the discoverability). 1st instance of Concern C forward-carry per Rigby T1 SIGN V3. Not blocking this ship.

## 4. Golden-path examples

**"What pages does the platform have?"**

```
platform_awareness_tool  action=list_routes
```

**"Give me a summary of everything the platform can do:"**

```
platform_awareness_tool  action=system_overview
```

**"Does this route exist?"**

```
platform_awareness_tool  action=check_route  path=/governance
```

**"What are all the PA tools?"**

```
platform_awareness_tool  action=tool_registry
```

## 5. Failure / empty-state / pagination notes

- **`check_route` with empty or unknown `path`** — returns `{exists: False, path}`. Consistent shape; no fail-loud.
- **`list_routes` with no matching filter** — returns `{count: 0, routes: []}`. Consistent shape.
- **`list_routes` with `auth_required` Python `False`** — treated as LLM-autofill and IGNORED (not a public-only filter). Explicit `'false'` string opts into public-only per Session 1228 PR-A.
- **`verify_deploy` without admin gate** — returns `{'error': 'Admin access required for deploy verification'}`. Inline `{error}` envelope (not raise). No HTTP fired.
- **Unknown action** — returns `{'error': f'Unknown action: {action}'}` at handler line 947. Inline `{error}` envelope, not raise.
- **Bare user (no `user_id`)** — falls back to unfiltered manifest via `_load_manifest()` (skips RBAC filtering).

## 5a. Mutation containment (per Rigby T0 SIGN Q2 — bridge scan)

- **Mutating actions excluded this ship:**
  - `verify_deploy` — invokes `core.views_deploy_verify.run_verification(base_url, token=<Token>)` which fires HTTP requests against `DEPLOY_BASE_URL` (default: production Railway URL). Admin-gated at the handler (returns error dict if caller is not `is_superuser or is_staff`). Classified `MUTATION` in `TOOL_ACTION_METADATA` seed this ship. Not classified `IRREVERSIBLE` because it's a read-side HTTP probe against a live service — no persistent state written, but the outbound HTTP + admin-token exchange is a real network side effect.
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` record with `safety_class='MUTATION'` at `tool_action_metadata.py`; harness `resolve_safety()` skips at dispatch (`expected_outcome=skipped_mutation` — verified in artifact §6.1).
- **dependency_surface note:** `external HTTP` — direct request to `DEPLOY_BASE_URL`, not through the S2909 bridge/HMAC fleet gateway. If exercised in a future batch, treat as network-dependent read with structured error envelopes (see `run_verification` return shape); does NOT require S2909 bridge preflight per Rigby T0 Q2(b) verdict.
- **Deferral rationale:** live HTTP + admin-token dependency + tolerance for cross-service state. Doc-only sweep cannot exercise safely. Deferred to a future MUTATION-coverage batch that pairs with a `dry_run` / network-preflight harness pattern.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness platform_awareness_tool` at HEAD `cff587f50` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `get_manifest` | `success` | 200 | 8 ms | `api_dependencies, build_sha, build_timestamp, capabilities, env, route_count, routes, studios` |
| `list_routes` | `success` | 200 | 3 ms | `count, routes` |
| `check_route` | `success` | 200 | 2 ms | `exists, path` |
| `system_overview` | `success` | 200 | 2 ms | `api_dependency_routes, api_dependency_total_endpoints, build_sha, capabilities, capability_count, route_count, routes_by_category, studio_count, studios` |
| `verify_deploy` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `list_api_dependencies` | `success` | 200 | ~1 ms | `route_count, routes` |
| `tool_registry` | `success` | 200 | ~1 ms | `action, tools, count` |

Artifact: `docs/audits/pa_tools/harness_output/platform_awareness_tool.json` — 6 READ_ONLY dispatched + 1 MUTATION skipped.

**Envelope-shape observation:** all 6 READ_ONLY actions return clean success at HTTP 200. `verify_deploy` cleanly metadata-skipped without any handler invocation. No inline `{ok: false}` envelope drift observed on the READ_ONLY subset. No `bridge` field on metadata — pure in-process manifest + Django model reads, no bridge preflight needed.

### 6.2 Runtime-not-executed — this ship

- **`list_routes` with populated `auth_required='false'` string** — not exercised (would confirm public-only filter passes coerce_optional_bool).
- **`list_api_dependencies` with `writes_only=True`** — not exercised (would confirm mutation-endpoint filter shape).
- **`verify_deploy`** — MUTATION-skipped (see §5a). Full HTTP verification path against a live Railway URL requires admin session + real deployment, not achievable in doc-only sweep.

---

## Related

- **Ledger candidates surfaced this ship:**
  - **Concern C 1st instance (schema↔doc drift on core tools)**: GAP_MAP flags `actions_not_mentioned_in_description` — schema `description` at `pa_tool_schemas.py:1493-1498` does not enumerate the 7 actions; the enum + inline sub-description at `:1509-1517` handles discoverability. Per Rigby T1 V3 — forward-carry note only; promote to slice-level fold candidate at 2nd instance in Slice 3.
- **Adjacent tools:**
  - `platform_config_tool` — runtime configuration snapshot (batch 1 peer); complements this tool's platform-shape read.
  - `db_health_tool` — DB migration + schema introspection; different concern from route/capability introspection.
  - `signal_studio_judge_stats` — signal-studio LLM-judge readback via HTTP (excluded from batch 1 per Rigby T0 Q1 (b) actionless-first + no-network policy).
- **Substrate context:** first mixed-safety tool in Slice 3 batch 1. Peers: `paid_interest_status` (actionless, TOOL_DEFAULTS shape), `persona_tool` (2 actions, per-action shape), `platform_config_tool` (5 actions, per-action shape). All 4 tools no-HTTP-on-selected-action, no-Celery, no-writes; sibling MUTATION actions excluded via per-action `TOOL_ACTION_METADATA` records.
- **Metadata seed:** 7 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (mirrors S2911 batch 6a `opportunity_manager_tool` per-action shape; no `TOOL_DEFAULTS` entry). Batch-uniform per-action pattern chosen per Rigby T1 V2 explicit-action-pinning directive — does NOT rely on default-action-safe invariant to defend against future default drift.
- **Session provenance:** Session 1069 base + Session 1228 PR-A `coerce_optional_bool` autofill guard for `auth_required`.
