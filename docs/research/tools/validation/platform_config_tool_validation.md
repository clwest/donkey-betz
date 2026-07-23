# `platform_config_tool` — Validation Report (S2913)

**Tool:** `platform_config_tool`
**Schema:** `core/services/pa_tool_schemas.py:2064`
**Handler:** `core/services/td_handlers_core.py:1274` (`_handle_platform_config`)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2913 (Path B systematic sweep — Slice 3 batch 1 of `td_handlers_core`)
**HEAD at validation:** `cff587f50` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 1 MUTATION action `web_config` explicitly excluded — see §5a).
**Rigby SIGN:** S2913 T0 SIGN AGREE-with-edits (batch 1 composition ratified; Q2 bridge-suspect scan confirmed `web_config` uses direct HTTP via urllib — excluded from opener). S2913 T1 SIGN AGREE-with-edits (V1 side-effect-free scan clean + V2 explicit `action="overview"` pinning applied + V3 Concern C 2nd instance forward-carry note per GAP_MAP `actions_not_mentioned_in_description` flag — first was `platform_awareness_tool` in this same batch).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Inspect runtime platform configuration: Django settings snapshot, active LLM provider keys (masked), environment variables (secrets masked), feature-flag values, and cross-service config comparison via HTTP to the web service. Answers "what provider is active?", "what environment am I actually in?", "are my env vars set?", "what feature flags are turned on?", and — via the excluded `web_config` action — "does the celery-pa service match the web service's config?"

Distinct from `platform_awareness_tool` (which enumerates the *shape* of the platform — routes, capabilities, tool schemas) and `db_health_tool` (DB migration + schema introspection). `platform_config_tool` reads the *runtime configuration state* — Django settings + `os.environ` + provider-key presence.

## Covered actions

**READ_ONLY actions covered only (4 of 5 total actions).** 1 MUTATION action (`web_config` — excluded — see §5a) is out of scope for this ship.

- `overview` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Returns default settings summary — `service_context, platform, debug, allowed_hosts, default_llm_provider, database_engine, database_name, redis_url (masked), celery_broker (masked), cors_allow_all, csrf_trusted_origins, frontend_url, backend_url, railway_environment, railway_service`.
- `llm_providers` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Returns `{action, default_provider, providers}` — 6 providers (OpenAI + Anthropic + Together AI + DeepSeek + Gemini + Ollama) with `configured` flag + masked key prefix.
- `env_vars` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Returns full `os.environ` enumeration with secrets masked (KEY/SECRET/TOKEN/PASSWORD/CREDENTIAL/DSN/DATABASE_URL/REDIS_URL/BROKER_URL patterns); skips noisy system prefixes (`__`, `npm_`, `LESS_`, `LS_`).
- `feature_flags` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Returns `{action, flags}` — 7 explicit flag attrs (`LUNGS_ENFORCE_HARD_LIMIT, CELERY_TASK_EVENT_RETENTION_DAYS, LLM_CALL_LOG_RETENTION_DAYS, BODY_THROTTLE_MAX_DELAY_SECONDS, CONTENT_AUTO_PUBLISH, SPIDER_ENABLED, DREAM_ENABLED`).
- `web_config` — **mutation — deferred to future MUTATION-coverage batch** — see §5a

## 3. Schema notes

- **No `required` field.** Schema at `pa_tool_schemas.py:2072-2087` has `properties.action` but no `required` array — action defaults to `'overview'` when omitted (handler line 1288: `payload.get('action', 'overview')`).
- **Optional:** `action` (enum: `overview, llm_providers, env_vars, feature_flags, web_config`).
- **Schema description drift note** — GAP_MAP flags this tool as `no_required, actions_not_mentioned_in_description`. Schema `description` at `pa_tool_schemas.py:2065-2071` does not enumerate the 5 actions; the enum + inline sub-description at `:2077-2085` handles discoverability. 2nd instance of Concern C forward-carry per Rigby T1 SIGN V3 (1st was `platform_awareness_tool` this batch). Per feedback_zoom_out_ask_per_rigby_sign classification: at 2 instances within Slice 3 batch 1, promote to slice-level fold candidate for evaluation at Slice 3 close — do NOT open substrate arc mid-slice (D6 moratorium).
- **`_mask()` helper** (handler-local closure at `:1295-1303`) — treats presence of any secret pattern in the KEY as a match; masks value to first 8 chars + `'...'` (or `'***'` if value < 8 chars).

## 4. Golden-path examples

**"What environment am I actually running in?"**

```
platform_config_tool  action=overview
```

**"Which LLM providers are configured?"**

```
platform_config_tool  action=llm_providers
```

**"Show me all env vars (secrets masked):"**

```
platform_config_tool  action=env_vars
```

**"What feature flags are turned on?"**

```
platform_config_tool  action=feature_flags
```

## 5. Failure / empty-state / pagination notes

- **Bare payload (no action)** — defaults to `overview` per handler line 1288. Returns clean overview response.
- **Unknown action** — returns `{'error': f'Unknown platform_config action: {action}'}` at handler line 1438. Inline `{error}` envelope, not raise.
- **Missing env var** — `overview` uses `os.environ.get('RAILWAY_SERVICE_NAME', 'local')` and `os.environ.get('RAILWAY_ENVIRONMENT', 'local')` — unset vars return the `'local'` default without failure.
- **Missing provider key** — `llm_providers` reports `{configured: False, key_prefix: 'not set'}` — no fail-loud, presence-only signal.
- **Zero secret-pattern match on env_vars** — `_mask()` returns the value unchanged; keys without secret patterns pass through verbatim.
- **`web_config` HTTP failure** — inline `{error, note}` envelope from the outer `except Exception` at handler lines 1341-1342 + 1351-1352. Does not raise.

## 5a. Mutation containment (per Rigby T0 SIGN Q2 — bridge scan)

- **Mutating actions excluded this ship:**
  - `web_config` — fires 2 `urllib.request.urlopen` calls (5s timeout each) to `WEB_SERVICE_URL` — default: production Railway URL. Endpoint 1: `/api/v1/health/` for health-check comparison; endpoint 2: `/api/internal/config-snapshot/` for config comparison. Classified `MUTATION` in `TOOL_ACTION_METADATA` seed this ship. Not classified `IRREVERSIBLE` because it's a read-side HTTP probe against a live service — no persistent state written, but the outbound HTTP is a real network side effect that can fail-loud when the web service is unreachable or when the `config-snapshot` endpoint is undeployed.
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` record with `safety_class='MUTATION'` at `tool_action_metadata.py`; harness `resolve_safety()` skips at dispatch (`expected_outcome=skipped_mutation`).
- **dependency_surface note:** `external HTTP` — direct request to `WEB_SERVICE_URL`, not through the S2909 bridge/HMAC fleet gateway. If exercised in a future batch, treat as network-dependent read with structured error envelopes (see the double `try/except` shape at handler lines 1334-1352); does NOT require S2909 bridge preflight per Rigby T0 Q2(b) verdict.
- **Deferral rationale:** live HTTP + cross-service state read + tolerance for stale/undeployed target endpoint. Doc-only sweep cannot exercise cleanly. Deferred to a future MUTATION-coverage batch (mirrors `platform_awareness_tool.verify_deploy` §5a in this same batch).

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness platform_config_tool` at HEAD `cff587f50` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `overview` | `success` | 200 | 1 ms | `service_context, platform, debug, allowed_hosts, default_llm_provider, database_engine, database_name, redis_url, celery_broker, cors_allow_all, csrf_trusted_origins, frontend_url, backend_url, railway_environment, railway_service` |
| `llm_providers` | `success` | 200 | ~1 ms | `action, default_provider, providers` |
| `env_vars` | `success` | 200 | ~1 ms | `action, count, variables` |
| `feature_flags` | `success` | 200 | ~1 ms | `action, flags` |
| `web_config` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |

Artifact: `docs/audits/pa_tools/harness_output/platform_config_tool.json` — 4 READ_ONLY dispatched + 1 MUTATION skipped.

**Envelope-shape observation:** all 4 READ_ONLY actions return clean success at HTTP 200. `web_config` cleanly metadata-skipped without handler invocation (no HTTP fired). Secret masking exercised at test time — the local `_mask()` helper covers all 9 secret patterns; verbatim key values only surface on non-matching keys. No inline `{ok: false}` envelope drift on READ_ONLY subset.

### 6.2 Runtime-not-executed — this ship

- **`env_vars` shape on a Railway-populated environment** — not exercised against a real Railway service (test ran locally); the `service_context` field would show the real service name.
- **`web_config`** — MUTATION-skipped (see §5a). Full HTTP-based cross-service compare not exercised.

---

## Related

- **Ledger candidates surfaced this ship:**
  - **Concern C 2nd instance (schema↔doc drift on core tools)**: 2nd occurrence in Slice 3 batch 1 (1st was `platform_awareness_tool`). Per Rigby T0 SIGN Q4 Concern C classification — this batch now hits the "2nd instance" threshold for slice-level fold candidate promotion. **Fold candidate scope:** "core tools have chronic schema/doc divergence; the `action` enum + inline sub-description carry the discoverability, but the top-level tool description doesn't enumerate actions." **Trigger evaluated at Slice 3 close, NOT mid-slice** (D6 moratorium; no substrate arc opens). Promotion path: if the pattern persists across ≥3 core tools by Slice 3 close, propose an "action-enum appendix" or auto-doc extract as a future substrate arc via explicit Chris directive.
- **Adjacent tools:**
  - `platform_awareness_tool` (batch 1 peer) — enumerates platform shape (routes/capabilities/tool schemas); complements this tool's runtime configuration read.
  - `db_health_tool` — DB migration + schema introspection; different concern from Django settings + env var introspection. `db_health_tool` also has an HTTP-via-`_delegate_remote_db_health` path (excluded from batch 1 per Rigby T0 Q1 (b) actionless-first + no-network policy).
  - `fleet_health` — probes each fleet app's `/api/health` via `probe_fleet`; different concern from runtime configuration.
- **Substrate context:** batch 1 peer of `paid_interest_status` (actionless, TOOL_DEFAULTS), `platform_awareness_tool` (7 actions, per-action), `persona_tool` (2 actions, per-action). All 4 tools no-network on selected actions, no-Celery, no-writes.
- **Metadata seed:** 5 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (mirrors S2911 batch 6a shape; no `TOOL_DEFAULTS` entry). Batch-uniform per-action pattern per Rigby T1 V2 explicit-action-pinning directive.
- **Session 1069 provenance:** the platform-config introspection framing + `_mask()` helper + Railway environment framing are all Session 1069 arc.
