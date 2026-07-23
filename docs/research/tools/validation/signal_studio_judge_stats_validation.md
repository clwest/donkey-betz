# `signal_studio_judge_stats` — Validation Report (S2916)

**Tool:** `signal_studio_judge_stats`
**Schema:** `core/services/pa_tool_schemas.py:961`
**Handler:** `core/services/td_handlers_core.py:209` (`_handle_signal_studio_judge_stats`)
**Register site:** `core/services/tool_dispatcher.py:450`
**Session:** S2916 (Path B systematic sweep — Slice 3 batch 6 of `td_handlers_core`)
**HEAD at validation:** `8dc6f0648` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated (full)` (actionless READ_ONLY handler; single execution path fully documented; §5b first-hop dependency proof + Appendix N Network-Preflight grounds the classification).
**Rigby SIGN:** S2916 T0 SIGN AGREE-with-edits — batch 6 network trio. Sibling of `fleet_health` (also authless) but with a single env-var-driven URL (no fleet enumeration). Q3 verdict: READ_ONLY at the tool level (no ORM writes; direct `httpx` GET only).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Calls signal-studio's `/api/judge-stats?days=N` endpoint and returns the LLM auto-summarizer judge breakdown — counts of clusters accepted (summarized) vs rejected as incoherent, with `rejection_rate` broken down by `cluster_method` + `pattern_type`. Answers "how is the entity-token clusterer doing?" / "did the clustering-quality change land?" without shelling into `docker exec signal_studio_api`.

Distinct from `fleet_health` (fleet-wide rollup, not single-app stats), from `http_smoke_test` (multi-step HTTP smoke test with DB observability), and from `paid_interest_status` (demand-gate readback — related fleet app, different endpoint).

## Covered actions

**Actionless handler.** No `action` param — the tool exposes one execution path. Documented as READ_ONLY per `TOOL_DEFAULTS['signal_studio_judge_stats']`; every dispatch inherits READ_ONLY (see §5b + Appendix N).

- `<default>` (the sole execution path) — **in scope this ship** — verified via T1a harness at HEAD `8dc6f0648` (harness output: `actions: []` + `schema_action_count: 0`, expected shape for actionless tool). Runs a single `httpx.Client.get()` against `{SIGNAL_STUDIO_API_URL}/api/judge-stats?days={days}` and returns the JSON body wrapped in an `{ok, ...}` envelope. Read-only network probe; no ORM writes.

## 3. Schema notes

- **Required:** none. All parameters optional.
- **Optional filters:**
  - `days` (int; default 7; enforced range 1..90 at the endpoint; handler-side clamp `max(1, min(days, 90))` at `td_handlers_core.py:247`).
- **No `action` enum** — schema exposes no `action` field.
- **Handler-side days coercion (Session 1228 PR-B):** `days = int(days_raw) if days_raw else 7` at `td_handlers_core.py:240-244`. Falsy (0, None, '') coerces to 7 (avoids the pre-1228 silent floor-to-1 bug when GPT-5.2 autofilled `days=0` on optional int params).
- **Handler-side URL derivation:** `base = os.environ.get('SIGNAL_STUDIO_API_URL', 'http://localhost:8007').rstrip('/')`; `url = f'{base}/api/judge-stats?days={days}'` at `td_handlers_core.py:249-252`. On fleet-net Docker: set `SIGNAL_STUDIO_API_URL=http://signal_studio_api:8007`.

## 4. Golden-path examples

**"How is the clusterer doing this week?"**

```
signal_studio_judge_stats
```

**"Just today's signal — is it noisy?"**

```
signal_studio_judge_stats  days=1
```

**"30-day view for slower-moving categories."**

```
signal_studio_judge_stats  days=30
```

## 5. Failure / empty-state / pagination notes

- **signal-studio unreachable (`httpx.HTTPError`):** returns `{ok: False, error: f'signal-studio unreachable at {base}: {e}', days}` at `td_handlers_core.py:257-262`. Covers connection refused, DNS failure, TLS failure, timeout.
- **signal-studio returns non-200:** returns `{ok: False, error: f'signal-studio /api/judge-stats HTTP {status_code}: {text[:200]}', status_code, days}` at `td_handlers_core.py:264-270`.
- **signal-studio returns non-JSON:** returns `{ok: False, error: f'signal-studio response not JSON: {e}', status_code, days}` at `td_handlers_core.py:271-279`.
- **Success:** returns `{ok: True, **data}` — merges the endpoint's JSON at the top level of the envelope at `td_handlers_core.py:280`.
- **Days out of range (before clamp):** handler clamps to 1..90 silently at `td_handlers_core.py:247`; the endpoint's own 422-if-out-of-range is bypassed to keep the PA loop snappy.

## 5a. Mutation containment / gateway allowlist

**N/A this ship.** No mutation actions declared — single execution path is a pure network GET. No ORM writes, no Celery dispatch, no LLM call, no file writes.

## 5b. First-hop dependency proof (S2915 shape + Appendix N)

**Batch 5 introduced §5b (first-hop dependency proof).** Batch 6 extends §5b with **Appendix N (Network-Preflight)** for tools whose first-hop is the network per Rigby S2916 T0 SIGN Q2 verdict.

Verdict scheme (see `task_breakdown_tool_validation.md` §5b for legend): `read` / `network` / `llm` / `db_write` / `db_delete` / `dispatch` / `opaque`.

### Path: `<default>` (single execution path)

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `os.environ.get('SIGNAL_STUDIO_API_URL', 'http://localhost:8007')` | read | `td_handlers_core.py:249-251` | firm — env-var read with default; no I/O |
| `httpx.Client(timeout=httpx.Timeout(...))` context manager | read | `td_handlers_core.py:255` | firm — client constructor; connection pool initialized in-process |
| `client.get(url)` | network | `td_handlers_core.py:256` | firm — single HTTP GET; no auth headers; no retries |
| `resp.json()` | read | `td_handlers_core.py:272` | firm — deserialize; may raise ValueError → caught → `ok: False` envelope |

**No-hidden-cost verdict:** ✓ single network GET; no delegated helpers; no transitive ORM/dispatch/LLM. Safety class tracks DB side effects (per S2916 T0 SIGN Q3 verdict); this tool has none → READ_ONLY.

### Appendix N — Network-Preflight (First-hop = Network)

**Introduced at S2916 batch 6 per Rigby T0 SIGN Q2 verdict.**

| Field | Declaration | Evidence (file:line) | Notes / constraints |
|---|---|---|---|
| **N1. Endpoint derivation source** | Single-endpoint. Base URL from `SIGNAL_STUDIO_API_URL` env var (default `http://localhost:8007`), rstrip'd; path is hardcoded `/api/judge-stats`; query string `?days={days}` with `days` from user payload clamped 1..90. | `td_handlers_core.py:249-252` | On fleet-net Docker, set `SIGNAL_STUDIO_API_URL=http://signal_studio_api:8007`. Path is NOT user-controllable. |
| **N2. Auth posture** | `authless_by_design`. Handler docstring at `td_handlers_core.py:214-219` explicitly states: "signal-studio is auth-less by design so no fleet HMAC signing is needed; we just GET over the configured base URL." No auth headers, no signing, no tokens. | `td_handlers_core.py:214-219, 256` | Endpoint is intentionally public by signal-studio design. |
| **N3. Timeout envelope** | Split envelope: `httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)`. **No retry policy** — one shot per invocation. | `td_handlers_core.py:255` | Read is generous (10s) because judge-stats query may aggregate weeks of clusters. |
| **N4. SSRF / egress allowlist** | `none` at the tool boundary. URL source is env var (operator-controlled at deploy time), not user input. `days` parameter is validated as int + clamped — cannot inject URL. | `td_handlers_core.py:240-252` | Env var is trusted by construction; if operator sets malicious value, that's a deployment concern, not a tool-level SSRF risk. |
| **N5. Redirect + non‑2xx handling** | Redirect: `httpx.Client` default follows redirects. Non-2xx: returned as `{ok: False, error, status_code}` — not raised. `httpx.HTTPError` (connection/timeout/TLS): caught → `{ok: False, error}` envelope. JSON parse failure: caught → `{ok: False, error}` envelope. Never raises to caller. | `td_handlers_core.py:257-279` | Errors surface as structured envelope with `ok: False` — the PA loop can distinguish success from failure without try/except at the caller. |

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness signal_studio_judge_stats` at HEAD `8dc6f0648`:

Harness output: `actions: []` + `schema_action_count: 0`. Expected shape for actionless tool. `TOOL_DEFAULTS['signal_studio_judge_stats']` classifies any dispatch as READ_ONLY.

Artifact: `docs/audits/pa_tools/harness_output/signal_studio_judge_stats.json`.

### 6.2 Runtime-not-executed — this ship

None on the doc-only ship. Live PA dispatch will be exercised at post-merge verify per PLAYBOOK-7.4.4 — pure READ_ONLY tool with no side effects, safe to invoke live. Expected behavior on local dev without signal-studio running: `ok: False` envelope with connection-refused error, demonstrating the tool's structured-failure path.

---

## Related

- **Adjacent tools:**
  - `fleet_health` (Slice 3 batch 6 sibling) — fleet-wide rollup, not single-app stats.
  - `http_smoke_test` (Slice 3 batch 6 sibling) — multi-step HTTP smoke test with DB observability via OpsRunTracker.
  - `paid_interest_status` (Slice 3 batch 1) — signal-studio demand-gate readback; related fleet app, different endpoint.
- **Substrate context:** batch 6 (network trio) applies the S2915 §5b first-hop dependency proof shape to network-preflight tools and introduces **Appendix N (Network-Preflight)**. This tool is the batch 6 "clean single-endpoint" case — no fleet enumeration (unlike `fleet_health`), no auth chain (unlike `http_smoke_test`), no DB side effect. Anchors the appendix's `single-endpoint` variant.
- **Metadata seed:** 1 `TOOL_DEFAULTS['signal_studio_judge_stats']` entry at `core/services/tool_action_metadata.py` this ship — actionless-uniform READ_ONLY classification.
- **Session provenance:** Session 1140 (`_handle_signal_studio_judge_stats` first ratified) + Session 1228 PR-B (falsy-`days` coercion fix at handler line 240-244).
- **Ledger candidates raised this batch (signal_studio_judge_stats-specific):** none. Tool is intentionally the batch 6 "cleanest network-read" case.
