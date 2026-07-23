# `fleet_health` — Validation Report (S2916)

**Tool:** `fleet_health`
**Schema:** `core/services/pa_tool_schemas.py:873`
**Handler:** `core/services/td_handlers_core.py:159` (`_handle_fleet_health`)
**Register site:** `core/services/tool_dispatcher.py:438`
**Session:** S2916 (Path B systematic sweep — Slice 3 batch 6 of `td_handlers_core`)
**HEAD at validation:** `8dc6f0648` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated (full)` (actionless READ_ONLY handler; single execution path fully documented; §5b first-hop dependency proof + Appendix N Network-Preflight grounds the classification).
**Rigby SIGN:** S2916 T0 SIGN AGREE-with-edits — batch 6 network trio. Q1 verdict: ship 3 network tools together. Q2 verdict: extend §5b with a **Network-Preflight appendix (Appendix N)** for tools whose first-hop is the network. Q3 verdict: READ_ONLY at the tool level (no ORM writes at any hop). Q4 Fold candidate: standardized appendices prevent §5b "notes-field creep" (future-trigger — batch 7 async duo introduces `Async-Fanout` sibling appendix).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Read-only rollup of every Dockerized fleet app's `/api/health` endpoint. Answers "what's broken in the fleet right now?" or "is mentorforge up?" without shelling into Docker. Delegates to the shared `probe_fleet(...)` function used by the `fleet_health_rollup` management command, so tool + CLI never drift.

Distinct from `paid_interest_status` (single-app demand-gate readback, not fleet-wide health), from `signal_studio_judge_stats` (single-app judge stats over HTTP), and from `http_smoke_test` (multi-step HTTP smoke test with DB observability via OpsRunTracker — this tool is a lightweight one-shot probe with no observability side effect).

## Covered actions

**Actionless handler.** No `action` param — the tool exposes one execution path. Documented as READ_ONLY per `TOOL_DEFAULTS['fleet_health']`; every dispatch inherits READ_ONLY (see §5b + Appendix N).

- `<default>` (the sole execution path) — **in scope this ship** — verified via T1a harness at HEAD `8dc6f0648` (harness output: `actions: []` + `schema_action_count: 0`, expected shape for actionless tool). Runs `probe_fleet(repo_filter, timeout_s)` and optionally filters healthy apps out when `include_healthy=False`. Read-only rollup; no ORM writes.

## 3. Schema notes

- **Required:** none. All parameters optional.
- **Optional filters:**
  - `repo` (str; single-repo probe by slug — e.g. `'mentorforge'`; omit for full-fleet probe).
  - `timeout_seconds` (number; per-app HTTP timeout; default `DEFAULT_TIMEOUT_S = 3.0` at `fleet_health_rollup.py:37`).
  - `include_healthy` (bool; default `True`; when `False`, only degraded/unreachable apps returned — concise output for status pings).
- **No `action` enum** — schema exposes no `action` field. Handler treats the tool as single-purpose.
- **Handler-side default coercion:** `timeout_s = float(payload.get('timeout_seconds') or DEFAULT_TIMEOUT_S)` at `td_handlers_core.py:180`. Falsy values (0, None, '') fall back to `DEFAULT_TIMEOUT_S = 3.0`.

## 4. Golden-path examples

**"Is the fleet healthy right now?"**

```
fleet_health
```

**"Just show me what's broken."**

```
fleet_health  include_healthy=false
```

**"Is mentorforge up?"**

```
fleet_health  repo=mentorforge
```

**"Slow-probe the fleet with a 10-second timeout."**

```
fleet_health  timeout_seconds=10
```

## 5. Failure / empty-state / pagination notes

- **No Docker-enabled fleet apps configured:** `probe_fleet` returns `{overall_status: 'empty', apps: [], probed_count: 0, healthy_count: 0}` — clean empty shape. The mgmt command exits with code 2 for this case; the PA tool just returns the payload.
- **Single repo not found (`repo` provided, no matching config):** `_load_fleet_configs` returns empty list (filter drops non-matching slugs at `fleet_health_rollup.py:52-53`); same empty shape as above with `probed_count: 0`.
- **Config JSON invalid:** `_load_fleet_configs` appends `{'_load_error': f'invalid JSON: {e}'}` at `fleet_health_rollup.py:56-58`; `_probe_one` returns `{status: 'CONFIG_ERROR', ok: False}` at `fleet_health_rollup.py:68-72`.
- **Config missing `docker.base_urls.api_url`:** `_probe_one` returns `{status: 'NO_API_URL', ok: False, detail: 'docker.base_urls.api_url missing'}` at `fleet_health_rollup.py:78-83`.
- **App unreachable (URLError / TimeoutError):** returns `{status: 'UNREACHABLE', ok: False, detail: f'{type}: {reason}', latency_ms, url}` at `fleet_health_rollup.py:94-100`.
- **App reachable but wrong status:** returns `{status: 'UNHEALTHY', ok: False, detail: f'HTTP {code} (expected {expected})'}` at `fleet_health_rollup.py:102-108`. `expected` is per-app `docker.healthchecks.api.expect_status` list (default `[200]`).
- **`include_healthy=False` filter:** post-probe filter at `td_handlers_core.py:184-185` drops healthy apps from the `apps` array but leaves the top-level `probed_count` + `healthy_count` intact so the caller still sees the totals.

## 5a. Mutation containment / gateway allowlist

**N/A this ship.** No mutation actions declared — single execution path is a pure network-read rollup. No ORM writes, no Celery dispatch, no LLM call, no file writes. Config file reads (`config/external_repos/*.json`) are in-repo trusted reads.

## 5b. First-hop dependency proof (S2915 shape + Appendix N)

**Batch 5 introduced §5b (first-hop dependency proof).** Batch 6 extends §5b with **Appendix N (Network-Preflight)** for tools whose first-hop is the network per Rigby S2916 T0 SIGN Q2 verdict — network callees deserve declared endpoint / auth / timeout / SSRF / redirect fields to prevent grep-hunt review cost.

Verdict scheme (see `task_breakdown_tool_validation.md` §5b for legend): `read` / `network` / `llm` / `db_write` / `db_delete` / `dispatch` / `opaque`.

### Path: `<default>` (single execution path)

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `probe_fleet(repo_filter, timeout_s)` | network | `td_handlers_core.py:183` | firm — implementation read this batch (`fleet_health_rollup.py:111-142`); enumerates `_load_fleet_configs` → `_probe_one` per config; no ORM writes, no dispatch |
| `_load_fleet_configs(repo_filter)` (transitive via `probe_fleet`) | read | `fleet_health_rollup.py:40-63` | firm — reads `config/external_repos/*.json` from repo filesystem via `Path(settings.BASE_DIR)`; no HTTP, no ORM |
| `_probe_one(slug, cfg, timeout_s)` (transitive via `probe_fleet`) | network | `fleet_health_rollup.py:66-108` | firm — one `urllib.request.urlopen(url, timeout=timeout_s)` per probed app; catches HTTPError/URLError/TimeoutError; no ORM writes |
| List comprehension filter `[a for a in result['apps'] if not a['ok']]` when `include_healthy=False` | read | `td_handlers_core.py:184-185` | firm — pure in-memory list filter on the probe result |

**No-hidden-cost verdict:** ✓ all first-hop deps enumerated. `probe_fleet` and its two helpers were read this batch — no hidden ORM write, no hidden dispatch, no LLM call. Safety class tracks DB side effects (per S2916 T0 SIGN Q3 verdict); this tool has none → READ_ONLY.

### Appendix N — Network-Preflight (First-hop = Network)

**Introduced at S2916 batch 6 per Rigby T0 SIGN Q2 verdict.** Declared for every tool whose first-hop is `network` to make failure modes and blast radius reviewable without grep-hunting. See Rigby's template response in the S2916 T0 SIGN turn 2 record.

| Field | Declaration | Evidence (file:line) | Notes / constraints |
|---|---|---|---|
| **N1. Endpoint derivation source** | Multi-endpoint (fleet). Enumerates every `config/external_repos/*.json` with `docker.enabled=true`; URL = `docker.base_urls.api_url.rstrip('/') + docker.healthchecks.api.path` (default path `/api/health`). Optional `repo` slug narrows to one entry. | `fleet_health_rollup.py:40-63, 73-84` | Config files are in-repo trusted source. URL joined by rstrip + concat; `expect_status` list also read from `docker.healthchecks.api.expect_status` (default `[200]`). |
| **N2. Auth posture** | `authless_by_design`. `urllib.request.urlopen(url, timeout=timeout_s)` with NO auth headers, NO signing, NO tokens. Confirmed by Rigby S2916 T0 SIGN Q1 tool-probe (grep for `HMAC` in codebase returned 0 matches). Fleet endpoints are treated as internal-network trusted probes. | `fleet_health_rollup.py:88` | Do NOT describe as "HMAC-signed" — that would be inaccurate. |
| **N3. Timeout envelope** | Single `timeout_s` (no split connect/read/write/pool with `urllib`). Default `DEFAULT_TIMEOUT_S = 3.0`. Falsy user input coerced to default at handler layer. **No retry policy** — one shot per app. | `fleet_health_rollup.py:37, 88; td_handlers_core.py:180` | User can override via `timeout_seconds` parameter. On timeout: `TimeoutError` caught → `UNREACHABLE` status row. |
| **N4. SSRF / egress allowlist** | `none` at the tool boundary. Config files (`config/external_repos/*.json`) are in-repo trusted; URLs are constructed from those, not from user input. `repo` parameter is a slug filter — it selects from the config allowlist, it cannot inject a URL. | `fleet_health_rollup.py:40-63` | No explicit allowlist regex needed because URL source is repo-controlled config. If someone commits a malicious `docker.base_urls.api_url` to the repo, that's a supply-chain concern, not an SSRF concern. |
| **N5. Redirect + non‑2xx handling** | Redirect: `urllib` default follows redirects. Non-2xx: `HTTPError` caught → status code checked against `expect_status` list → row marked `UNHEALTHY` with detail `HTTP {code} (expected {expected})`. `URLError` / `TimeoutError` → row marked `UNREACHABLE`. Never raises to caller — always returns structured row. | `fleet_health_rollup.py:91-108` | Errors don't break the rollup — degraded apps surface as `ok: False` rows and drive `overall_status: 'degraded'`. |

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness fleet_health` at HEAD `8dc6f0648`:

Harness output: `actions: []` + `schema_action_count: 0`. Expected shape for actionless tool — the harness has no per-action dispatch loop. `TOOL_DEFAULTS['fleet_health']` classifies any dispatch as READ_ONLY; the harness would allow dispatch, but the "0 READ_ONLY dispatched" line in `summary.json` is the expected shape for an actionless-READ_ONLY tool (registry/audit signal, not a dispatch counter).

Artifact: `docs/audits/pa_tools/harness_output/fleet_health.json`.

### 6.2 Runtime-not-executed — this ship

None on the doc-only ship. Live PA dispatch of `fleet_health` will be exercised at post-merge verify per PLAYBOOK-7.4.4 (recycle-after-merge) — it's a pure READ_ONLY tool with no side effects, safe to invoke live.

---

## Related

- **Adjacent tools:**
  - `paid_interest_status` (Slice 3 batch 1) — single-app demand-gate readback, not fleet-wide health.
  - `signal_studio_judge_stats` (Slice 3 batch 6 sibling) — single-app judge stats over HTTP.
  - `http_smoke_test` (Slice 3 batch 6 sibling) — multi-step HTTP smoke test with DB observability via OpsRunTracker.
  - `ops_tool` (Slice 1) — worker-level status snapshot + git-head diagnostics, not fleet HTTP.
- **Substrate context:** batch 6 (network trio) applies the S2915 §5b first-hop dependency proof shape to network-preflight tools and introduces **Appendix N (Network-Preflight)** as the standardized declaration for endpoint / auth / timeout / SSRF / redirect fields. Motivates the S2916 Q4 Fold candidate for standardized appendices.
- **Metadata seed:** 1 `TOOL_DEFAULTS['fleet_health']` entry at `core/services/tool_action_metadata.py` this ship — actionless-uniform READ_ONLY classification.
- **Session provenance:** Session 1126 (`_handle_fleet_health` first ratified).
- **Ledger candidates raised this batch (fleet_health-specific):** none. `fleet_health` is intentionally the "boring first" in batch 6 — pure network read, no auth complexity, no DB side effect — to anchor the batch and demonstrate the new Appendix N shape on a low-risk tool before applying it to `http_smoke_test` (mutation-classified) + `signal_studio_judge_stats` (env-var-driven URL).
