# `http_smoke_test` — Validation Report (S2916)

**Tool:** `http_smoke_test`
**Schema:** `core/services/pa_tool_schemas.py:2142`
**Handler:** `core/services/td_handlers_core.py:1884` (`_handle_http_smoke_test`)
**Register site:** `core/services/tool_dispatcher.py:503`
**Session:** S2916 (Path B systematic sweep — Slice 3 batch 6 of `td_handlers_core`)
**HEAD at validation:** `8dc6f0648` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (actionless MUTATION-classed handler; write path via `OpsRunTracker` documented + gated by harness; §5b + Appendix N ground the classification).
**Rigby SIGN:** S2916 T0 SIGN AGREE-with-edits — batch 6 network trio. Rigby's Q1 tool-probe catch: **`OpsRunTracker.__enter__` writes an `OpsRun` row and `_emit` writes `OpsRunEvent` rows** — so this tool is a MUTATION at the DB layer even though the "main intent" is network preflight. Adopts Rigby's tightening rule: **safety class tracks DB side effects, not semantic intent.**
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Run HTTP smoke tests against platform API endpoints (Railway prod or local). Verifies endpoints return correct status codes + response shapes. Supports 5 built-in suites (`cockpit_health` / `cockpit_incidents_crud` / `pa_tools_smoke` / `auth_regression` / `deploy_verify`) + custom step definitions with variable capture. Every dispatch is wrapped in an `OpsRunTracker` context manager that persists an `OpsRun` row + one `OpsRunEvent` per step for observability.

Distinct from `fleet_health` (fleet `/api/health` rollup — one-shot per app, no DB observability), from `signal_studio_judge_stats` (single-endpoint stats query, no assertions), from `web_search` (external Serper search, not endpoint verification), and from `web_fetch_tool` (single-URL fetch, not assertion-driven verification).

## Covered actions

**Actionless handler.** No `action` param — the tool exposes one execution path with a `suite` discriminator (5 built-in) OR custom `steps` payload. Documented as MUTATION per `TOOL_DEFAULTS['http_smoke_test']`; every dispatch inherits MUTATION because every dispatch persists `OpsRun` + `OpsRunEvent` rows via `OpsRunTracker` (see §5a + §5b).

- `<default>` (the sole execution path; `suite` selects built-in, `steps` provides custom) — **out of scope this ship — MUTATION correctly gated by harness** — see §5a + §5b. Every invocation opens an `OpsRunTracker(f'Smoke: {suite}', 'smoke_test', 'pa_tool')` context manager, which creates an `OpsRun` row on `__enter__` and one `OpsRunEvent` per step. Not exercised live per D6 moratorium on new mutation-class execution during READ_ONLY sweep. Harness reports `skipped_mutation`.

## 3. Schema notes

- **Required:** none. Handler validates that either `suite` or `steps` resolves to a non-empty step list; returns `{ok: False, error}` otherwise.
- **Optional filters:**
  - `suite` (str; enum: `cockpit_health` / `cockpit_incidents_crud` / `pa_tools_smoke` / `auth_regression` / `deploy_verify`; defaults to `'default'` at handler line 1895 which then fails through `run_smoke_test` if neither `suite` nor `steps` is set).
  - `environment` (str; enum: `railway_prod` / `local`; auto-detects from `RAILWAY_ENVIRONMENT` env var when omitted per Session 1246).
  - `steps` (list[dict]; custom test steps — ignored if `suite` is set; max 50 steps per `MAX_STEPS`).
  - `fail_fast` (bool; default `True`).
  - `return_body` (bool; default `False`).
  - `max_body_bytes` (int; default 50_000; capped at 250_000).
- **No `action` enum** — schema exposes no `action` field. Suite/steps discriminator is not a safety-class differentiator.
- **Handler-side observability wrap:** `with OpsRunTracker(...) as tracker: result = tracker.step(suite, lambda: run_smoke_test(payload))` at `td_handlers_core.py:1896-1898`. `result['ops_run_id'] = tracker.ops_run_id` appended at line 1901.

## 4. Golden-path examples

**"Run the cockpit health smoke suite against prod."** (HYPOTHETICAL — MUTATION gated this batch)

```
# http_smoke_test  suite=cockpit_health  environment=railway_prod
# ↑ Creates OpsRun row + 18 OpsRunEvent rows. Deferred.
```

**"Verify PA tools endpoints locally."** (HYPOTHETICAL — MUTATION gated this batch)

```
# http_smoke_test  suite=pa_tools_smoke  environment=local
# ↑ Creates OpsRun row + 14 OpsRunEvent rows. Deferred.
```

**"Run the deploy verify suite right after promoting a build."** (HYPOTHETICAL — MUTATION gated this batch)

```
# http_smoke_test  suite=deploy_verify
# ↑ Creates OpsRun row + 5 OpsRunEvent rows. Deferred.
```

## 5. Failure / empty-state / pagination notes

- **Unknown suite name:** `run_smoke_test` returns `{ok: False, error: f'Unknown suite: {suite_name}. Available: [...]'}` at `http_smoke_test.py:911-914`. Handler still wraps in OpsRunTracker → OpsRun row created with `status='failed'` after context exit.
- **Neither `suite` nor `steps` provided:** returns `{ok: False, error: 'No suite or steps provided'}` at `http_smoke_test.py:918-919`. OpsRun row still created (MUTATION always fires on `__enter__`).
- **Too many steps (>50):** returns `{ok: False, error: f'Too many steps: {len(steps)} (max {MAX_STEPS})'}` at `http_smoke_test.py:922-923`.
- **Host not in allowlist (`ALLOWED_HOSTS_RE`):** `_validate_domain` returns `False` at `http_smoke_test.py:126-140`; step marked `ok: False` with error.
- **Private IP (except localhost):** `_validate_domain` blocks via `ipaddress.ip_address(hostname).is_private` at `http_smoke_test.py:130-137`.
- **Step timeout (>20s):** `timeout_s = min(timeout_ms / 1000, 20)` at `http_smoke_test.py:247`; caps at 20s regardless of step config.
- **HTTPError on step:** caught at `http_smoke_test.py:280-289`; status code + response preview captured; step's `ok` depends on assertion outcomes.
- **Any other exception:** caught at `http_smoke_test.py:290-293`; step marked `ok: False` with `error: f'{type}: {exc}'`.
- **Assertion failure:** step `ok: False` at `http_smoke_test.py:298-301`; `fail_fast` (default True) short-circuits the run.
- **Variable capture on non-dict/list body:** capture silently skipped at `http_smoke_test.py:307-314`.
- **OpsRunTracker exception during context:** `__exit__` marks `run.status='failed'` and emits a `step_fail` event at `ops_run_tracker.py:51-55`.

## 5a. Mutation containment / gateway allowlist

**Every dispatch is a mutation surface (unconditional).** The single execution path performs three DB writes on every invocation:

1. **`OpsRun.objects.create(title, run_type, triggered_by, status='running')`** — always fires on `OpsRunTracker.__enter__` at `ops_run_tracker.py:32-42`. **Even if the payload is invalid** (unknown suite / no steps / too many steps), the OpsRun row is created BEFORE `run_smoke_test` is called.
2. **`OpsRunEvent.objects.create(...)`** — one per step (start + pass/fail) at `ops_run_tracker.py:95-106`. `run_smoke_test` calls `tracker.step(...)` at `td_handlers_core.py:1897`, which emits `step_start` + `step_pass`/`step_fail`.
3. **`self.run.save(update_fields=['status', 'finished_at', 'event_count', 'fail_count', 'summary'])`** — fires on `__exit__` at `ops_run_tracker.py:64` to finalize the run.

**Containment mechanism (audit metadata):** classified `MUTATION` via `TOOL_DEFAULTS['http_smoke_test']` (uniform tool-level default; every dispatch inherits MUTATION). Third actionless-MUTATION `TOOL_DEFAULTS` entry after `legal_doc_drafter_agent` (S2910) + `research_and_create_tool` (S2915) — 3rd instance triggers the "actionless side-effecting chain" pattern-naming evaluation queued in `00-START-NEXT-SESSION.md` S2915 Ledger candidates section. T1a harness respects the classification via `skipped_mutation`.

**Containment mechanism (runtime):** none at the handler layer. Per S2914 batch 4 doc-fix PR #3458, `TOOL_ACTION_METADATA` classification is **descriptive audit metadata**, not a runtime enforcement gate. Live PA runtime WILL dispatch this tool and create OpsRun + OpsRunEvent rows on every invocation.

**Deferral rationale for live-exercise:** every invocation writes at least 1 OpsRun row + 2 OpsRunEvent rows (start + pass/fail) even for the smallest suite. `cockpit_health` (18 checks) writes ~37 rows per run. Not appropriate to burn on a doc-only sweep session. First-live-exercise deferred to a dedicated post-deploy session where the OpsRun observability rows are the point of the invocation.

**Boilerplate (Rigby S2916 T0 SIGN Q3 tightening rule):** _This tool's safety_class reflects **DB side effects**, not semantic intent; network behavior is documented in Appendix N (Network-Preflight)._

## 5b. First-hop dependency proof (S2915 shape + Appendix N)

**Batch 5 introduced §5b (first-hop dependency proof).** Batch 6 extends §5b with **Appendix N (Network-Preflight)** for tools whose first-hop is the network per Rigby S2916 T0 SIGN Q2 verdict.

Verdict scheme (see `task_breakdown_tool_validation.md` §5b for legend): `read` / `network` / `llm` / `db_write` / `db_delete` / `dispatch` / `opaque`.

### Path: `<default>` (single execution path)

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `OpsRunTracker('Smoke: {suite}', 'smoke_test', 'pa_tool')` context manager | db_write | `td_handlers_core.py:1896` | firm — implementation read this batch (`ops_run_tracker.py:21-108`); creates `OpsRun` row on `__enter__`, emits `OpsRunEvent` rows via `_emit`, saves `OpsRun` on `__exit__` |
| `OpsRun.objects.create(title, run_type, triggered_by, status='running')` (transitive via `__enter__`) | db_write | `ops_run_tracker.py:32-42` | firm — always fires on context entry, before `run_smoke_test` executes |
| `OpsRunEvent.objects.create(run, event_type, label, detail)` (transitive via `_emit`, called by `step`) | db_write | `ops_run_tracker.py:95-106` | firm — one per step start + one per step pass/fail |
| `self.run.save(update_fields=[...])` (transitive via `__exit__`) | db_write | `ops_run_tracker.py:64` | firm — finalizes OpsRun status/counters |
| `tracker.step(suite, lambda: run_smoke_test(payload))` | dispatch (in-process) | `td_handlers_core.py:1897` | firm — calls `run_smoke_test`; `dispatch` here is in-process function call inside step-tracked lambda, not Celery |
| `run_smoke_test(payload)` (transitive via `tracker.step`) | network | `http_smoke_test.py:878-1001` | firm — implementation read this batch; sequences `urllib.request.urlopen(req, timeout=timeout_s)` per step; SSRF allowlist enforced by `_validate_domain` |
| `_resolve_auth_token(environment)` (transitive via `run_smoke_test`) | read | `http_smoke_test.py:112-124` | firm — reads local DRF User token (from ORM when `environment='local'`) OR `PA_API_TOKEN` env var (when `environment='railway_prod'`). The DRF-User-token path is a User + Token ORM read, no write. |
| `urllib.request.urlopen(req, timeout=timeout_s)` (transitive per step) | network | `http_smoke_test.py:260-263` | firm — one HTTP call per step; `MAX_STEPS=50`; `MAX_RESPONSE_BYTES=1MB`; default timeout 20s per step |

**No-hidden-cost verdict:** ✗ at DB layer — cannot claim no hidden cost; every dispatch persists OpsRun + OpsRunEvent rows unconditionally (even on payload-validation failure). ✓ at network + LLM layer — no LLM calls; network hops are SSRF-allowlisted and bounded (≤50 steps, ≤20s each, ≤1MB response). Safety class is MUTATION at the tool level per Rigby's tightening rule: safety class tracks DB side effects, not semantic intent.

**No-additional-hidden-cost check:** the declared callees fully account for the handler body. `OpsRunTracker.step` also captures exceptions and returns `{ok: False, error}` at `ops_run_tracker.py:74-80` without raising — meaning `run_smoke_test` failures do NOT leak past the tracker to the handler. Handler always returns the tracker's `result` dict + `ops_run_id`.

### Appendix N — Network-Preflight (First-hop = Network)

**Introduced at S2916 batch 6 per Rigby T0 SIGN Q2 verdict.**

| Field | Declaration | Evidence (file:line) | Notes / constraints |
|---|---|---|---|
| **N1. Endpoint derivation source** | Multi-endpoint (per-step). Base URL from `_resolve_base_url(environment)` — for `railway_prod` = `https://donkey-betz-production.up.railway.app` (or equivalent) sourced from settings; for `local` = `http://localhost:8000`. Path per step from suite definition or user `steps` payload. 5 built-in suites at `http_smoke_test.py:315-872`. | `http_smoke_test.py:75-102, 894, 918` | Custom steps allowed; each step declares `method` + `path` (+ optional `body`, `assert`, `capture`). `MAX_STEPS=50`. |
| **N2. Auth posture** | `bearer_token` via `_resolve_auth_token(environment)`. When `environment='local'`: uses local DRF User `Token` from ORM (read-only lookup). When `environment='railway_prod'`: uses `PA_API_TOKEN` env var. Auth headers redacted from result output. | `http_smoke_test.py:104-124` | Auth token NEVER surfaces in the tool result — `run_smoke_test` redacts auth headers before returning. Session 1247 P1 fix: auto-detects environment to avoid hitting Railway edge from local PA calls. |
| **N3. Timeout envelope** | Per-step: `timeout_s = min(timeout_ms / 1000, 20)` — clamped to 20s regardless of `timeout_ms` declared in the step (`DEFAULT_TIMEOUT_MS = 20_000`). `MAX_RESPONSE_BYTES = 1_048_576` (1 MB) cap on response body read. **No retry policy** — one shot per step. | `http_smoke_test.py:36-38, 247` | Total run time bounded by `MAX_STEPS × 20s = 1000s` worst-case, though `fail_fast=True` (default) short-circuits on first failure. |
| **N4. SSRF / egress allowlist** | `allowlist + block_private_ips`. `ALLOWED_HOSTS_RE = ^(localhost\|127\.0\.0\.1\|[\w.-]+\.railway\.app)$` (case-insensitive). Plus `_validate_domain` blocks any resolved hostname that parses as a private IP via `ipaddress.ip_address(hostname).is_private` (except `localhost` / `127.0.0.1`). | `http_smoke_test.py:39-41, 126-140` | Allowlist is intentionally narrow — no arbitrary internet fetch. Custom steps can only hit localhost or `*.railway.app`. |
| **N5. Redirect + non‑2xx handling** | Redirect: `urllib` default follows redirects. Non-2xx: `HTTPError` caught → status_code + response_preview captured; step's `ok` depends on assertion outcomes (not on the status_code alone). Any other exception: step marked `ok: False` with error string; `fail_fast=True` (default) short-circuits the run. Auth headers redacted from `result['request_headers']` before returning. | `http_smoke_test.py:280-301` | Assertions (`{check: 'status', expected: 200}` etc.) drive pass/fail — a step can succeed with a non-2xx response if the assertion expected that code (e.g., 401 for auth regression). |

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness http_smoke_test` at HEAD `8dc6f0648`:

Harness output: `actions: []` + `schema_action_count: 0`. Expected shape for actionless tool. `TOOL_DEFAULTS['http_smoke_test']` classifies any dispatch as MUTATION; harness would report `skipped_mutation` for a hypothetical dispatch attempt.

Artifact: `docs/audits/pa_tools/harness_output/http_smoke_test.json`.

### 6.2 Runtime-not-executed — this ship

- **Single execution path (implicit)** — MUTATION classification applied at tool level; live exercise deferred per §5a rationale (every invocation writes OpsRun + OpsRunEvent rows). No `dry_run` fast-path exists at the handler layer (would need OpsRunTracker to accept a `record: bool = True` flag; not proposed this batch per D6 moratorium on `dry_run` infrastructure arcs).

---

## Related

- **Adjacent tools:**
  - `fleet_health` (Slice 3 batch 6 sibling) — fleet-wide `/api/health` rollup, no DB observability.
  - `signal_studio_judge_stats` (Slice 3 batch 6 sibling) — single-endpoint stats, no assertions, no DB observability.
  - `web_search` (Slice 2 batch 2) — external Serper search, not endpoint verification.
  - `web_fetch_tool` (Slice 2 batch 2b) — single-URL fetch, not assertion-driven.
  - `ops_tool` (Slice 1) — reads existing OpsRun rows; this tool creates them.
- **Substrate context:** batch 6 (network trio) applies the S2915 §5b first-hop dependency proof shape to network-preflight tools and introduces **Appendix N (Network-Preflight)**. This tool is the batch 6 shape-break — the only MUTATION-classed tool in the trio, because `OpsRunTracker` writes DB rows on every invocation regardless of network outcome. Motivates Rigby's tightening rule: safety class tracks DB side effects, not semantic intent.
- **Metadata seed:** 1 `TOOL_DEFAULTS['http_smoke_test']` entry at `core/services/tool_action_metadata.py` this ship — actionless-uniform MUTATION classification.
- **Session provenance:** Session 1247 (`_handle_http_smoke_test` + `run_smoke_test` first ratified; environment auto-detection landed same session per Session 1246-1247 P1 fix).
- **Ledger candidates raised this batch (http_smoke_test-specific):**
  - **Third actionless-MUTATION `TOOL_DEFAULTS` entry** — after `legal_doc_drafter_agent` (S2910) + `research_and_create_tool` (S2915). **3rd instance triggers the "actionless side-effecting chain" pattern-naming evaluation** queued in S2915 forward-carry Ledger candidates. Pattern shape: single-execution-path tool that unconditionally performs I/O with persistent side effect on every dispatch, classified at tool level not per-action.
  - **Observability-tracker as unconditional MUTATION vector.** `OpsRunTracker.__enter__` writes an `OpsRun` row before the wrapped operation even executes. Any PA tool wrapping in `OpsRunTracker` inherits MUTATION classification regardless of the wrapped operation's own safety class. **Forward-carry:** if a 2nd PA tool wraps in `OpsRunTracker` and it appears in a future sweep batch, evaluate whether "observability-wrapper as MUTATION source" warrants explicit naming vs the tool-level MUTATION classification we're using here.
  - **`dry_run` add-flag pattern** — S2912 §5a mitigation note (deferred) applies: this tool would benefit from an `OpsRunTracker(record=False)` opt-out to enable safe live-exercise. Not proposed this batch per D6 moratorium.
