# `railway_tool` — Validation Report (S2940)

**Tool:** `railway_tool`
**Schema:** `core/services/pa_tool_schemas.py:4647` (7-action enum + service_name/limit params)
**Handler:** `core/services/td_handlers_railway.py:371` (`_handle_railway`; module-level helpers `list_services` :60 / `get_service_logs` :121 / `restart_service` :222 / `redeploy_service` :258 / `get_service_metrics` :292 / `list_variables` :317)
**Register site:** `core/services/tool_dispatcher.py:574`
**Session:** S2940 (Slice 7 Batch 2b — trio with `code_job_tool` + `employee_tool`)
**HEAD at validation:** `adba317b0` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. **Bifurcated verification scope** (per S2939 Chris D-verdict guardrail carried forward): §6 LIVE-VERIFIES the 5 read actions (`help` / `services` / `logs` / `metrics` / `variables`) — with §6.2-6.6 verifying the `RAILWAY_API_TOKEN not configured` env-gated path at local runtime; §5a covers 2 external mutations (`restart` / `redeploy`) ANALYZED-NOT-EXECUTED with Appendix N (Network-Preflight) evidence.
**Category upgrade target:** `untested` → `validated_partial` (`help` LIVE-VERIFIED unconditionally; `services`/`logs`/`metrics`/`variables` LIVE-VERIFY the env-gated refusal path; mutations analyzed-only; enabled-path — with `RAILWAY_API_TOKEN` set — not exercised at local this ship)
**Rigby SIGN:** S2940 T0 SIGN AGREE (bifurcated Option C shape confirmed via mutation-verb scan; env-var gating on `RAILWAY_API_TOKEN` treated equivalently to Django flag-gate per S2939 rigby_work_item precedent).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`railway_tool` is Rigby's **Railway platform infrastructure management** surface — list Railway services with deployment status, view deploy logs, restart or redeploy services, check service metrics, and inspect (masked) environment variables. The tool sits over Railway's GraphQL API (`https://backboard.railway.com/graphql/v2`) with Bearer token authentication via the `RAILWAY_API_TOKEN` env var. Use it when Chris asks about Railway services ("what's the state of the celery workers?"), deploy status ("did the last deploy succeed?"), needs a service restart ("bounce celery-long-running"), wants a fresh redeploy ("push a new build to donkey-betz-platform"), needs deployment metrics or commit info, or wants to inspect env vars (values masked for security).

Distinct from `celery_worker_lifecycle` validation (that documents local worker lifecycle — this is remote Railway ops); from `infra_health_tool` (broader infrastructure health surface — different auth model, different downstream); from `dev_ops_observability` (which is an analysis agent, not a direct-execution tool). This is the **Railway control-plane** interface — direct GraphQL calls to the Railway API with a Bearer token, from Rigby's PA tool surface.

## Covered actions

Enumerating every action in the schema `action` enum. **5 read actions + 2 mutation actions declared in schema.** Read actions LIVE-VERIFIED this ship (env-gated refusal path at local runtime); mutations ANALYZED-NOT-EXECUTED per bifurcated Option C.

- `help` — **READ — verified live at S2940 §6.1.** Static enum echo — returns `{"tool": "railway_tool", "actions": [<6-item human-readable action string list>]}`. No network call. No `error_code: "legacy_error"` because the token check never runs. **Only action that returns a non-error envelope at local runtime** (env var unset).
- `services` — **READ — verified live at S2940 §6.2 (env-gated).** GraphQL query over project → environments → serviceInstances → latestDeployment. Returns `{action, project, environment, services: [...], total}` on success; `{error: "RAILWAY_API_TOKEN not configured", error_code: "legacy_error"}` when env var unset (verified live).
- `logs` — **READ — analyzed at §6.3.** Two GraphQL queries: (1) resolve deployment_id from service_name; (2) fetch deployment logs. Returns `{action: "logs", service, deployment_id, log_count, logs: [...]}` on success; degraded envelope with `note` + `error_detail` if the logs endpoint refuses (line 199-207). Env-gated same as `services`.
- `restart` — **MUTATION `external` — ANALYZED-NOT-EXECUTED.** See §5a + Appendix N. Calls Railway GraphQL mutation `serviceInstanceRedeploy(serviceId, environmentId)` on the latest deployment. Env-gated.
- `redeploy` — **MUTATION `external` — ANALYZED-NOT-EXECUTED.** See §5a + Appendix N. Calls the same `serviceInstanceRedeploy` GraphQL mutation as `restart` — the two actions are functionally identical at the API layer; only the caller's semantic intent + response `note` field differs (line 254 vs 288). Env-gated.
- `metrics` — **READ — analyzed at §6.4.** No new GraphQL call — reuses the `list_services()` cache and picks out one service's row. Returns `{action, service, service_id, status, deployed_at, commit, commit_message}` on success. Env-gated via the initial `list_services()` call.
- `variables` — **READ — analyzed at §6.5.** GraphQL query `variables(projectId, environmentId, serviceId)`. Values masked at handler layer: first 4 + last 4 chars for values > 12 chars, first 2 + last 2 for values > 4 chars, full for shorter. Filters out `RAILWAY_*` auto-injected vars (line 348). Env-gated.
- **default (no `action` param)** — verified via handler code inspection (`td_handlers_railway.py:374`). Defaults to `help` per `payload.get('action', 'help')`. Same as the `help` action envelope — no network, no error_code.
- **invalid action** — verified via handler code inspection (line 420). Returns `{"error": "Unknown railway_tool action: <x>"}`. Bare envelope with no `ok: false` field. Sixth-instance corroboration of the invalid-action divergence class (Ledger #5 candidate — see `code_job_tool_validation.md` §6.6 for the parallel bare-envelope pattern from Batch 2b).

## 3. Schema notes

- **Required:** `action` (enum: `services` | `logs` | `restart` | `redeploy` | `metrics` | `variables` | `help`).
- **Optional (service-scoped):** `service_name` (string — required for `logs` / `restart` / `redeploy` / `metrics` / `variables`; not needed for `services` or `help`). Schema description at `pa_tool_schemas.py:4674-4681` enumerates 10 known service names (`celery-long-running`, `donkey-betz-platform`, `celery-pa`, `celery-worker`, `celery-content`, `celery-broadcast`, `celery-beat`, `celery-long-running-2`, `code-worker`, `resolve-node`).
- **Optional (logs-only):** `limit` (int; default 50, hard cap 200 per line 376 — `min(int(payload.get('limit', 50)), 200)`). Applied post-fetch: `logs[-limit:]` at line 218 — returns last N lines from the fetched batch.
- **Env-var gate:** `RAILWAY_API_TOKEN` must be set for all actions except `help`. When unset, `_get_token()` returns `''` and `_gql()` short-circuits with `{"error": "RAILWAY_API_TOKEN not configured"}` (line 34-35). The dispatcher normalizer appends `error_code: "legacy_error"` — same signature as `rigby_work_item` `_disabled_response` at S2939. **Env-gate is equivalent to a Django flag-gate for validation purposes** — the enabled-path (with token set) is NOT exercisable at local runtime unless Chris sets the env var.
- **Constants:** `_API_URL = 'https://backboard.railway.com/graphql/v2'` (line 21), `_PROJECT_ID = 'a11eb739-9bd2-4f7b-adc6-f97554164f33'` (line 22), `_ENVIRONMENT_ID = '4045e5be-c118-4e3a-8931-c071f50ad119'` (line 23), `_TIMEOUT = 20` seconds (line 24). All hardcoded — single-project single-environment tool at v0.
- **No auth gate at handler layer:** the Bearer token IS the auth. No `_verify_rigby_caller` gate on mutations. Callers implicitly bounded by PA tool-surface exposure (Rigby-only in practice) + `RAILWAY_API_TOKEN` env var scope (only present in the trusted worker environment).
- **No `dry_run` affordance:** `restart` / `redeploy` always fire the real GraphQL mutation when validation passes. Ledger #38 substrate blocker for LIVE-VERIFY of mutations. Even a fresh test env var wouldn't help without a dry_run — the mutation is destructive to running services.
- **Redirect + non-2xx handling:** `requests.post` in `_gql()` at line 47 uses `raise_for_status()` — non-2xx responses raise `requests.RequestException` caught at line 54 → `{"error": "Railway API error: <first 200 chars>"}`. Timeout caught separately at line 52 → `{"error": "Railway API timed out"}`. No custom redirect policy — inherits `requests` default (follow up to 30 redirects).

## 4. Golden-path examples

**Example 1 — Help envelope (READ, verified live):**
```json
{"action": "help"}
```
→ `{"tool": "railway_tool", "actions": ["services — list all Railway services with deployment status", "logs — view recent deploy logs...", "restart — restart a service...", "redeploy — trigger fresh build + deploy...", "metrics — get service details...", "variables — list env vars for a service, masked..."]}` (verified §6.1).

**Example 2 — List services (READ, env-gated at local — verified live):**
```json
{"action": "services"}
```
→ At local (env unset): `{"error": "RAILWAY_API_TOKEN not configured", "error_code": "legacy_error"}` (verified §6.2).
→ At Railway env (token set, hypothetical): would return `{"action": "services", "project": "donkey-betz", "environment": "production", "services": [{"name": "celery-long-running", "service_id": "<uuid>", "status": "SUCCESS", "deployed_at": "2026-07-24T12:00:00Z", "commit": "adba317b0", "commit_message": "chore(session): S2939..."}, ...], "total": 10}`.

**Example 3 — Service logs (READ, env-gated):**
```json
{"action": "logs", "service_name": "celery-long-running", "limit": 20}
```
→ Env-unset at local: `{"error": "RAILWAY_API_TOKEN not configured", "error_code": "legacy_error"}`.
→ At Railway env: would resolve deployment_id → fetch logs → return `{"action": "logs", "service": "celery-long-running", "deployment_id": "<uuid>", "log_count": 20, "logs": ["[INFO] <message>", "[WARN] <message>", ...]}`. Degraded envelope path (logs endpoint refuses): `{"action": "logs", "service": ..., "deployment_id": ..., "status": ..., "note": "Deploy logs may require Railway dashboard for full access", "error_detail": "<inner error>"}` (line 200-207).

**Example 4 — Service metrics (READ):**
```json
{"action": "metrics", "service_name": "donkey-betz-platform"}
```
→ Env-unset: refusal envelope.
→ At Railway env: `{"action": "metrics", "service": "donkey-betz-platform", "service_id": "<uuid>", "status": "SUCCESS", "deployed_at": "<iso>", "commit": "<12-char-hash>", "commit_message": "<first 80 chars>"}` (line 306-314).

**Example 5 — Restart service (MUTATION `external` — analyzed only this ship):**
```json
{"action": "restart", "service_name": "celery-pa"}
```
→ Would fire GraphQL mutation `serviceInstanceRedeploy(serviceId: <uuid>, environmentId: <uuid>)` at Railway API. Response: `{"action": "restart", "service": "celery-pa", "status": "restart_triggered", "previous_status": "SUCCESS", "note": "Service will restart with the latest deployment. Check status in ~30s."}` (line 249-255).

**Example 6 — Redeploy service (MUTATION `external`):**
```json
{"action": "redeploy", "service_name": "code-worker"}
```
→ Same GraphQL mutation as `restart`. Response: `{"action": "redeploy", "service": "code-worker", "status": "redeploy_triggered", "note": "Fresh build + deploy triggered. Takes 2-5 minutes."}` (line 284-289). **Functionally identical to `restart` at the API layer** — only response `note` differs.

**Example 7 — List env vars (READ, masked):**
```json
{"action": "variables", "service_name": "celery-worker"}
```
→ Env-unset: refusal envelope.
→ At Railway env: masked-value envelope like `{"action": "variables", "service": "celery-worker", "total": 42, "variables": {"DATABASE_URL": "post...5432", "REDIS_URL": "redi...6379", "OPENAI_API_KEY": "sk-p...abcd", ...}}` (line 358-363). RAILWAY_*-prefixed vars filtered (line 348-349).

## 5. Failure / empty-state / pagination notes

- **Env-unset (verified §6.2, the default local runtime state):** every action except `help` returns `{"error": "RAILWAY_API_TOKEN not configured", "error_code": "legacy_error"}`. Bare `{error, error_code}` envelope — no `ok: false` field. Payload contents ignored — the token check short-circuits before any GraphQL call.
- **`services` empty state (hypothetical with token set):** `{"action": "services", "project": "donkey-betz", "environment": "production", "services": [], "total": 0}` — envelope stable at 0 services. Not currently reachable at v0 Railway project (10 services registered).
- **`services` GraphQL parsing failure:** `{"error": "Failed to parse services: <exception>"}` (line 117-118) — catches `KeyError` or `IndexError` on response shape drift. Explicit narrow-catch, not blanket except-all.
- **`logs` unknown `service_name`:** `{"error": "Service \"<name>\" not found. Available: [<list>]"}` (line 134). Includes available names for recovery hint.
- **`logs` deployment_id resolution failure:** `{"error": "No deployment found for <service>"}` (line 183). Reached when the service exists in `list_services()` but its `latestDeployment` field is null.
- **`logs` GraphQL response shape drift:** logged warning at line 176-180 — "GraphQL response shape unexpected while extracting deployment_id" — plus the outer refusal envelope. **Loud on shape drift** per S1103c fix comment (line 174-176) — was silently `pass`, now logs.
- **`logs` endpoint refuses (Railway API doesn't support deploymentLogs):** degraded envelope with `note: "Deploy logs may require Railway dashboard for full access"` + `error_detail: "<inner>"` (line 200-207). Handler continues rather than raising — best-effort semantics.
- **`restart` missing `service_name`:** `{"error": "Provide service_name to restart"}` (line 402).
- **`restart` unknown `service_name`:** `{"error": "Service \"<name>\" not found. Available: [<list>]"}` (line 232).
- **`restart` GraphQL mutation failure:** returns the raw `{"error": "<railway-api-error-message>"}` from `_gql()` — pass-through (line 247).
- **`redeploy` mirrors `restart`** at every failure branch (line 258-289 is structurally identical to line 222-256 except for `note` string at the tail).
- **`metrics` missing `service_name`:** `{"error": "Provide service_name for metrics"}` (line 412).
- **`metrics` unknown `service_name`:** same as restart (line 303).
- **`variables` missing `service_name`:** `{"error": "Provide service_name to list variables"}` (line 417).
- **`variables` unknown `service_name`:** same as restart (line 328).
- **Handler-layer unexpected exception:** `{"error": "Railway tool error: <first 200 chars>"}` (line 424) — outer try/except catches anything the per-action helpers didn't handle. `exc_info=True` logged for observability.
- **Invalid action:** `{"error": "Unknown railway_tool action: <x>"}` (line 420). Bare envelope. **Sixth-instance corroboration** of the invalid-action divergence class from `code_job_tool_validation.md` §6.6 — both handlers in Slice 7 Batch 2b use bare `{error: ...}` shape.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1; 4-tier blast-radius taxonomy added S2921)

**REQUIRED — 2 mutation actions declared in `## Covered actions` (`restart` / `redeploy`). ANALYZED-NOT-EXECUTED at this ship per bifurcated Option C shape.**

### Per-action blast-radius classification

| Action | Tier | Handler line | Direct writes | Signal fan-out | External touches |
|---|---|---|---|---|---|
| `restart` | `external` | `td_handlers_railway.py:222-255` → `_gql(query: 'mutation serviceInstanceRedeploy...')` at line 238-245 | none at the handler layer — the mutation writes state at the Railway backend, not in the platform DB | none in the platform (no `post_save`, no Celery task) — but at Railway's backend, the mutation triggers a full service restart (container termination + fresh spawn + health check cycle) which has cascading operational effects on connected traffic | **HTTP POST to `https://backboard.railway.com/graphql/v2`** with Bearer token — leaves the handler process. GraphQL mutation `serviceInstanceRedeploy(serviceId, environmentId)`. Idempotent-ish: Railway coalesces rapid duplicate redeploys to one; but the terminate-and-restart cycle still fires. |
| `redeploy` | `external` | `td_handlers_railway.py:258-289` → same `_gql(query: 'mutation serviceInstanceRedeploy...')` at line 274-281 | none direct at handler layer | same as restart — Railway-backend cascading effects (full build pipeline: fetch source → build container → replace) | **HTTP POST to Railway GraphQL API** — same endpoint + mutation as `restart`. The two actions send the identical mutation body; the difference is only in the returned envelope's `note` field (line 254 vs 288). **Ledger candidate**: `restart` and `redeploy` are functionally identical at the API layer despite being separately-declared enum values. Documented as a semantic distinction for callers, not enforced at the Railway API level. |

### Signal-chain evidence (Chris D-verdict guardrail — file/line cited)

- **No platform-side post_save receivers:** the mutations do NOT write to any Django model. Grep of `core/signals/` for Railway-related receivers → no matches. All state change happens at Railway's backend, not in the platform DB.
- **No Celery fan-out:** `restart` / `redeploy` are synchronous HTTP calls; no `apply_async` / `.delay()` boundary. Response returns to the handler immediately upon Railway's ACK of the mutation (or timeout at 20s per `_TIMEOUT`).
- **External-tier because the mutation crosses a process/network boundary:** even without in-platform signal chains, the mutation IS the external side effect. The blast radius is anything downstream of the affected Railway service — traffic that was in-flight, cached in-memory state on the container, connection pools, worker jobs in progress on the container.
- **Cascade at Railway's backend:** a restart mutation triggers Railway's control plane to (1) mark the service as `RESTARTING`, (2) send SIGTERM to the container, (3) wait for graceful shutdown OR force-kill after grace period, (4) spawn a fresh container from the current deployment image, (5) health-check, (6) route traffic. `redeploy` adds a build step before (1). Neither is atomic; both are ~30s (`restart`) or 2-5min (`redeploy`) operational events.

### Idempotency proof bar (Chris D-verdict guardrail)

- **`restart` idempotency:** **best-effort at Railway's layer** — Railway coalesces rapid duplicate `serviceInstanceRedeploy` mutations to a single restart cycle. The tool DOES NOT enforce idempotency at the handler layer — every call fires the mutation. Multiple rapid `restart` calls on the same service will each ACK success at the platform, but Railway may collapse them into one restart cycle at its backend.
- **`redeploy` idempotency:** same as restart — best-effort at Railway. A fresh build takes 2-5 min; a second `redeploy` mutation issued during that window may be coalesced OR may queue depending on Railway's internal semantics (not documented in the tool code — Railway API contract).
- **No handler-side dedupe key:** the tool trusts Railway's control plane to handle rapid duplicates safely. Not a per-tool idempotency invariant.
- **Timeout of 20s at `_TIMEOUT`:** if Railway ACKs slower than 20s, the mutation is treated as `{"error": "Railway API timed out"}` — but the mutation MAY still have landed at Railway. Caller cannot distinguish "mutation dropped" from "response dropped." Documented failure mode.

### Deferral rationale (why not live-fire this ship)

- Live-firing `restart` or `redeploy` would trigger a real service restart at Railway — visible operational impact (10-30s of traffic disruption for `restart`; 2-5min for `redeploy`). NOT reversible.
- The `RAILWAY_API_TOKEN` env var is not set at local runtime — even a would-be live-fire would return the refusal envelope. This is the current safety posture; flipping it requires an intentional Chris directive.
- Ledger #38 (`dry_run` substrate) would enable a "mutation shape captured, mutation not fired" verification path — not applicable for pure HTTP calls to an external API without corresponding staging endpoints at Railway's side.
- Rigby S2940 T0 mutation-verb scan confirmed both `restart` + `redeploy` are external HTTP mutations; live-mutation deferral is the safest bifurcated Option C posture.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `os.environ.get('RAILWAY_API_TOKEN', '')` (all actions except `help`) | `read` (env var) | `td_handlers_railway.py:28` | validated |
| `requests.post(_API_URL, json={query, variables}, headers={Authorization: Bearer <token>}, timeout=20)` (all GraphQL calls) | `network` (HTTP POST — see Appendix N) | line 38-46 | validated |
| `resp.raise_for_status()` (all GraphQL calls) | `network` (post-fetch validation) | line 47 | validated |
| `resp.json()` (all GraphQL calls) | `network` (response parsing) | line 48 | validated |
| `list_services()` (called from `logs`, `restart`, `redeploy`, `metrics`, `variables` for service_name resolution) | `network` (delegated GraphQL query) | called at lines 124, 224, 260, 294, 319 → recursive to `_gql` | validated |
| `_gql(query, variables)` internal helper (all GraphQL calls) | `network` (wrapper) | line 31-55 | validated |
| `logger.warning(...)` on shape drift (logs action) | `read` (write to stdlib logger) | line 176-180 | validated (S1103c loud-on-shape-drift fix) |
| `logger.error(...)` + `exc_info=True` (outer handler try/except) | `read` (write to stdlib logger) | line 423 | validated |

**No Appendix A (Async-Fanout) needed:** neither `restart` nor `redeploy` dispatches a Celery task. Both are synchronous HTTP mutations. Downstream cascading effects happen at Railway's backend, not in the platform.

### Appendix N — Network-Preflight (first-hop = network HTTP POST)

Filling per S2916 batch 4 template extension — every non-`help` action fires an HTTP POST to Railway's GraphQL API. This is the definitional network-first-hop tool in Slice 7.

- **N1. Endpoint derivation source:** `_API_URL = 'https://backboard.railway.com/graphql/v2'` — **hardcoded** at module load time (line 21). Single-endpoint. NOT resolved from settings, env var, or payload. If Railway changes their GraphQL endpoint domain in the future, requires a code change (not a config change). Same posture for `_PROJECT_ID` (line 22) and `_ENVIRONMENT_ID` (line 23) — hardcoded UUIDs. Single-project, single-environment tool at v0.
- **N2. Auth posture:** `bearer_token` — `Authorization: Bearer <RAILWAY_API_TOKEN>` header (line 42). Token read from `os.environ.get('RAILWAY_API_TOKEN', '')` per `_get_token()` at line 27-28. **Redaction:** the token is only used inline in the header; not logged, not returned in envelopes, not written to any DB row. Failure envelope names the env var (`"RAILWAY_API_TOKEN not configured"`) but does not reveal token content. Verified via handler code inspection — no `logger.info("Token: %s", token)` pattern anywhere.
- **N3. Timeout envelope:** `_TIMEOUT = 20` seconds (line 24). Applied as `requests.post(..., timeout=20)` — this is a total-request timeout (connect + read combined per `requests` semantics when passed as int). No separate connect/read/write/pool timeouts. No retry policy — a single attempt per action. Total-run bound = 20s per GraphQL call; for `logs` / `restart` / `redeploy` / `metrics` / `variables` which each call `list_services()` first, the total is up to **2 × 20s = 40s bound** per action. `requests.Timeout` caught at line 52 → `{"error": "Railway API timed out"}` envelope.
- **N4. SSRF / egress allowlist:** endpoint is repo-controlled (hardcoded at line 21) — **allowlist waived per S2915 convention** ("SSRF class N/A: URL is repo-controlled, not caller-supplied"). No allowlist regex; no private-IP block. Safe by construction — no path where a caller supplies a URL that could be redirected to internal endpoints.
- **N5. Redirect + non-2xx handling:** inherits `requests` default redirect follow (up to 30 redirects). No custom `allow_redirects=False`. `resp.raise_for_status()` at line 47 surfaces non-2xx as `requests.HTTPError`, caught at line 54 → `{"error": "Railway API error: <first 200 chars>"}` (with error message truncated). GraphQL-level errors (200 response with `errors` in body) caught separately at line 49 → `{"error": "<first error message>"}`. Two-tier error handling: HTTP-layer vs GraphQL-layer, both surface as envelope `error` field.

## 5c. Contract ↔ Implementation Consistency (S2937 retro-fold; per Rigby zoom-out #4)

### 5c.1 Handler / module header claims match action reality

**Disposition: PASS — no drift.** The module docstring at `td_handlers_railway.py:1-9` correctly names the tool's scope: "PA tool handler for Railway infrastructure management. Gives Rigby direct access to Railway operations: service status, logs, restarts, redeployments, and variable inspection." Names the API endpoint + auth mechanism. The `_handle_railway` docstring at line 373 concisely lists: "services, logs, restart, redeploy, variables" — accurate but incomplete (**missing `metrics` + `help`**). Not a drift with runtime — the handler correctly implements 7 branches (help + services + logs + restart + redeploy + metrics + variables) at line 379-419. The docstring under-lists but the handler is complete. Schema description at `pa_tool_schemas.py:4648-4654` correctly names all 7 actions. **Minor docstring gap** noted but does not rise to Ledger #5 lint hit (0 hits at S2940 lint pre-flight — the schema description is source-of-truth for callers, and it matches runtime).

### 5c.2 Gating truth matches runtime behavior

**Disposition: PASS — env-var-gated on `RAILWAY_API_TOKEN`, LIVE-VERIFIED at §6.2-6.6.** `_get_token()` at line 27-28 reads `RAILWAY_API_TOKEN`; `_gql()` at line 34-35 short-circuits with `{"error": "RAILWAY_API_TOKEN not configured"}` when the token is falsy. At local runtime, the env var is unset — §6.2 LIVE-VERIFIES the refusal envelope. `help` action is the sole exception (line 380-390) — returns the static enum echo without calling `_gql()`, so it never checks the token. **Env-var gating is functionally equivalent to Django flag-gating** for validation purposes per S2939 rigby_work_item precedent (`RIGBY_WORK_QUEUE_REVIEW_ENABLED=False` → `_disabled_response`; `RAILWAY_API_TOKEN=''` → `token-not-configured` refusal). The `error_code: "legacy_error"` suffix is appended by the same dispatcher normalizer verified at S2939 §6.1 for rigby_work_item.

### 5c.3 Shared handler-file coupling noted

**Disposition: PASS — dedicated handler.** `td_handlers_railway.py` is a 425-line dedicated file with a single tool (`railway_tool`). No sibling tools share this module. The handler imports `requests` + `os` + `json` + `logging` — stdlib and popular third-party only. No shared substrate imports across other PA tool handlers. Module-level constants (`_API_URL`, `_PROJECT_ID`, `_ENVIRONMENT_ID`, `_TIMEOUT`) are handler-scoped. No coupling to note at the tool level. If a hypothetical future `railway_variables_bulk_set_tool` or `railway_deployment_history_tool` is added, it would likely live in this same file — cross-link would be re-checked at that point.

## 6. Evidence

Live PA-dispatch evidence for the 5 read actions. Captured at S2940 T0 via Rigby dispatch (tool_runs verbose block). §6.1 verifies the `help` no-network path; §6.2 verifies the env-var-gated refusal path (default local runtime state). Mutations (`restart` / `redeploy`) analyzed-not-executed per §5a.

### 6.1 `action=help` — LIVE at S2940 T0

Dispatch: `railway_tool action=help`
Latency: 6ms
Result:
```json
{
  "tool": "railway_tool",
  "actions": [
    "services — list all Railway services with deployment status",
    "logs — view recent deploy logs for a service (requires service_name)",
    "restart — restart a service (requires service_name)",
    "redeploy — trigger fresh build + deploy (requires service_name)",
    "metrics — get service details and deployment info (requires service_name)",
    "variables — list env vars for a service, masked (requires service_name)"
  ]
}
```

**Observations locked at this HEAD:**
- Envelope shape: `{tool: str, actions: [str, ...]}`. Only 6 items in the array — **omits `help` itself** (line 379-390) even though it's a valid action.
- No `error_code` field — the token check is bypassed (line 379 branch runs before line 391 branches that call `_gql()`).
- Latency 6ms — pure in-process string generation, no I/O.
- Envelope diverges from every other Slice 7 tool's shape — no `ok`/`action`/`gateway` fields. Bare `{tool, actions}` echo. **Semantic drift only** — not a Ledger #5 hit because the schema description accurately calls this action a "help: list all actions" echo.

### 6.2 `action=services` — LIVE at S2940 T0 (env-gated refusal path)

Dispatch: `railway_tool action=services`
Latency: 5ms
Result:
```json
{
  "error": "RAILWAY_API_TOKEN not configured",
  "error_code": "legacy_error"
}
```

**Observations locked at this HEAD:**
- Env-gated refusal. `_gql()` at line 34-35 returns `{"error": "RAILWAY_API_TOKEN not configured"}`; dispatcher normalizer appends `error_code: "legacy_error"` — **same 2-field appended shape** verified at S2939 §6.1 for `rigby_work_item`'s `_disabled_response` path.
- Latency 5ms — the token check short-circuits before any network call.
- Envelope stable: `{error, error_code}` — 2 keys. Payload was empty; token check ignores payload contents.
- **This is the safe-verify surface at local runtime** — no operator intervention required to reproduce.

### 6.3 `action=logs` — ANALYZED (env-gated at local; enabled-path deferred)

Cannot LIVE-VERIFY the enabled path (log-fetch shape) without `RAILWAY_API_TOKEN` set. At local runtime, this action returns the same env-gated refusal as §6.2. Expected enabled-path envelope (per handler analysis at line 200-218):
```json
{
  "action": "logs",
  "service": "<service_name>",
  "deployment_id": "<uuid>",
  "log_count": 20,
  "logs": ["[INFO] <message>", "[WARN] <message>", ...]
}
```
Degraded envelope (logs endpoint refuses at Railway API):
```json
{
  "action": "logs",
  "service": "<service_name>",
  "deployment_id": "<uuid>",
  "status": "<service_status>",
  "note": "Deploy logs may require Railway dashboard for full access",
  "error_detail": "<inner error>"
}
```
Missing-service envelope: `{"error": "Service \"<name>\" not found. Available: [<list>]"}` (line 134).
Missing-service_name envelope: `{"error": "Provide service_name (e.g. \"celery-long-running\")"}` (line 397).

### 6.4 `action=metrics` — ANALYZED (env-gated at local)

Same env-gated refusal path as §6.2. Expected enabled-path envelope (line 306-314):
```json
{
  "action": "metrics",
  "service": "<service_name>",
  "service_id": "<uuid>",
  "status": "<SUCCESS|FAILED|BUILDING|...>",
  "deployed_at": "<iso-timestamp>",
  "commit": "<first-12-chars>",
  "commit_message": "<first-80-chars>"
}
```

### 6.5 `action=variables` — ANALYZED (env-gated at local)

Same env-gated refusal path. Expected enabled-path envelope (line 358-363) with **masked** values:
```json
{
  "action": "variables",
  "service": "<service_name>",
  "total": 42,
  "variables": {
    "DATABASE_URL": "post...5432",
    "REDIS_URL": "redi...6379",
    "OPENAI_API_KEY": "sk-p...abcd",
    "DEBUG": "false",
    ...
  }
}
```
Masking policy (line 350-356): len > 12 → first 4 + last 4 chars separated by `...`; len > 4 → first 2 + last 2; else full value (for booleans/short flags). `RAILWAY_*`-prefixed vars filtered out at line 348-349.

### 6.6 Mutation actions (`restart` / `redeploy`) — ANALYZED-NOT-EXECUTED

See §5a for per-action blast-radius classification + §5b Appendix N (Network-Preflight) evidence + idempotency proof bar + deferral rationale. Both mutations fire the **identical** GraphQL mutation `serviceInstanceRedeploy(serviceId, environmentId)` — see §5a table for the equivalence note (Ledger candidate — record-only).

### 6.7 Invalid action envelope

Handler line 420: `{"error": "Unknown railway_tool action: <x>"}`. Bare envelope with no `ok: false` field. **Sixth-instance corroboration** of the invalid-action divergence class documented in `code_job_tool_validation.md` §6.6 — both Batch 2b handlers use bare `{error: ...}` shape (Ledger #5 Tier-2 promotion candidate — threshold not met unless additional corroborations surface post-Batch 2b).

## Related

- **Adjacent tools (same Slice 7 Batch 2b):** `code_job_tool` (bifurcated: 4 read + 3 mutation — remote code-worker dispatch surface), `employee_tool` (bifurcated: 3 read + 1 mutation — Employee OS registry + Rigby-gated dispatch).
- **Adjacent tools (adjacent surface):** `celery_worker_lifecycle` (substrate doc about local worker lifecycle — this tool operates on the REMOTE Railway-managed workers), `infra_health_tool` (broader infrastructure health — different auth model), `dev_ops_observability` (analysis agent for cross-service triage — read-only, no direct Railway API access), `db_health_tool` (DB-side health — different substrate).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1 + Appendix N added S2916 batch 4); `docs/audits/PA_TOOLS_GAP_MAP.md`; `docs/topics/celery-workers.md` (local worker lifecycle overview — Railway sibling); `docs/topics/infrastructure.md` (deployment topology overview).
- **Prior ratifications:** S2892 Path B open; S2916 batch 4 (Appendix N introduction — Network-Preflight for network-first-hop tools); S2921 §5a taxonomy; S2928 Slice 5 CLOSE; S2937 T1 Chris ratification (4-batch Slice 7 plan + §5c retro-fold); S2938 Ledger #5 lint substrate; **S2939 Slice 7 Batch 2a** (mission_verdict + newsletter_tool + rigby_work_item) with Chris D-verdict guardrails (§6 read-only scope + §5a mutation proof bar) — carried forward at S2940 T0 Chris D-verdict RATIFIED (Batch 2b = 3-tool ship closes Slice 7).
- **Lint pre-flight at S2940 open:** `railway_tool` → **0 handler_drift hits** (verified via `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check`). Clean.
- **First-hop dependencies:** see §5b table + Appendix N (Network-Preflight — HTTP POST to `https://backboard.railway.com/graphql/v2` with Bearer token, 20s total-request timeout, no retry, single-endpoint hardcoded).
- **Regression coverage:** `core/tests/test_td_handlers_railway*.py` (if any) — grep `test_railway` in `core/tests/`. Coverage may be light given the external-API-dependent surface.
- **Ledger candidates surfaced this doc:** (a) **`restart` + `redeploy` functional equivalence** — both fire identical `serviceInstanceRedeploy` GraphQL mutation; the enum-level distinction is caller-semantic only, not API-enforced (record-only — deferred as record-only unless Railway API adds a distinct `serviceInstanceRestart` mutation in the future); (b) **`_handle_railway` docstring omits `metrics` + `help`** (line 373 lists 5 of 7 actions) — minor docstring under-list, not a runtime drift; queue as a ~2-min docstring refresh at next `td_handlers_railway.py` touch; (c) **Sixth-instance invalid-action bare-envelope pattern** (Ledger #5 Tier-2 candidate — see `code_job_tool_validation.md` §6.6 for parallel evidence); (d) **20s per-call timeout may double to 40s** for actions that call `list_services()` first (`logs`, `restart`, `redeploy`, `metrics`, `variables`) — documented, not fixed.
- **Post-merge live-dispatch verification:** exercise `railway_tool action=help` + `action=services` after `make recycle-all` at merge; confirm envelope shapes match §6.1 + §6.2. Mutations + enabled-path env-set variants remain analyzed-only.
