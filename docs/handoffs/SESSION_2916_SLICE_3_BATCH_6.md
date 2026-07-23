# Session 2916 — Slice 3 batch 6 (network trio + §5b Appendix N Network-Preflight)

**Session:** S2916
**Date:** 2026-07-23
**Closed at HEAD:** `a56accd86` (post batch 6 merge; wrapper bumps to next-session pin at close)
**Wrapper pin at open:** `pa-43e10ef28cae4122` (bumps to next-session pin at close via `session_lifecycle close`)
**Session cumulative:** 1 batch shipped × 3 tools = **3 tools closed** in Slice 3; sweep at **20/22 core surface** (was 17). Remaining 2: async duo (`studio_tool` + `workflow_run_tool`) for batch 7.

---

## READ THIS FIRST

S2916 shipped **Slice 3 batch 6** (3 tools: `fleet_health` + `signal_studio_judge_stats` + `http_smoke_test`) — the **network trio** — applying the S2915 §5b first-hop dependency proof shape to the network-preflight test pattern and introducing **§5b Appendix N (Network-Preflight)** per Rigby S2916 T0 SIGN Q2 verdict.

**Rigby T0 SIGN cycle (2 turns, 8 tool-grounded probes turn 1 + Appendix N template drafted turn 2, zero rubber-stamp).** All 4 verdicts AGREE-with-edits:
- **Q1 composition** — ship all 3 together. Rigby's tool-probe caught two initial framing errors: (1) my "HMAC signing path via mgmt command" claim on `fleet_health` was WRONG — Rigby's grep for `HMAC` returned zero matches; `probe_fleet` at `fleet_health_rollup.py:88` is plain `urllib.request.urlopen` with NO signing. Validation doc corrected to `authless_by_design`. (2) `http_smoke_test` writes `OpsRun` + `OpsRunEvent` rows on every dispatch via `OpsRunTracker.__enter__` / `_emit` / `__exit__` — MUTATION at the DB layer, NOT READ_ONLY, per Rigby's tightening rule: **safety class tracks DB side effects, not semantic intent.**
- **Q2 §5b shape** — extend §5b with a **Network-Preflight appendix (Appendix N)** with 5 declared fields (N1 endpoint derivation source / N2 auth posture / N3 timeout envelope / N4 SSRF / egress allowlist / N5 redirect + non-2xx handling). Rigby drafted the copy/pasteable template in SIGN turn 2; applied uniformly across the 3 validation docs.
- **Q3 safety class** — READ_ONLY at the tool level for `fleet_health` + `signal_studio_judge_stats` (no ORM writes); MUTATION at the tool level for `http_smoke_test` (OpsRunTracker persists rows unconditionally). Rejects introducing a new `NETWORK_READ` safety class (enum bloat pressure per Rigby); network dependency captured cleanly in Appendix N.
- **Q4 zoom-out (Fold candidate)** — standardized appendices (Network-Preflight now + Async-Fanout at batch 7 for the async duo) prevent §5b "notes-field creep" into unreviewable policy surface. Rigby-Tool-Gap Ledger row #38 (future-trigger classification; 2nd adoption at batch 7 promotes to Fold-candidate evaluation at next Slice close). Stays within D6 moratorium — extending existing §5b shape, not schema-bumping.

**Post-merge live verify clean (per PLAYBOOK-7.4.4).** After `make recycle-all` at sha=`a56accd865cc`:
- `fleet_health` — LIVE dispatch (14ms), returned `overall_status: 'degraded'` with 7 UNREACHABLE rows (Connection refused on ports 8002-8008 — fleet not running locally; expected structured shape).
- `signal_studio_judge_stats` — LIVE dispatch (14ms), returned exact structured-failure envelope documented in §5: `{ok: False, error: 'signal-studio unreachable at http://localhost:8007: [Errno 61] Connection refused', days: 1, error_code: 'legacy_error'}`.
- `http_smoke_test` — NOT dispatched (correct). Rigby code-verified `TOOL_DEFAULTS['http_smoke_test'].default_safety_class == 'MUTATION'` at `tool_action_metadata.py:450`. BLOCKED verdict backed by file+line evidence.

**Ledger candidate from post-merge verify:** `signal_studio_judge_stats` returned an extra `error_code: 'legacy_error'` field in the failure envelope that's not documented in §5 or Appendix N. Likely harness-side envelope normalization (not handler-emitted) — non-blocking, forward-carry.

## PRs shipped this session

- u-d-b PR [#3462](https://github.com/clwest/donkey-betz-platform/pull/3462) — Slice 3 batch 6 (network trio + §5b Appendix N), merged at `a56accd86`.
- u-d-b PR `<TBD>` — S2916 close cascade (handoff + 00-START refresh + wrapper pin bump).

## Batch shipped

### Batch 6 (PR #3462) — network trio + §5b Appendix N (Network-Preflight)

- **`fleet_health`** — actionless READ_ONLY (single execution path). Fleet `/api/health` rollup via shared `probe_fleet` from `fleet_health_rollup` mgmt command (single source of truth for probe logic — tool and CLI never drift).
  - **In scope:** `<default>` (sole execution path).
  - Appendix N: multi-endpoint (fleet), `authless_by_design` (no HMAC per Rigby grep — CORRECTED from initial framing), single `timeout_s` default 3.0s no retries, no SSRF allowlist (URL source is repo-controlled `config/external_repos/*.json`), `urllib` default redirects + structured HTTPError/URLError handling.
  - **Live post-merge:** 14ms, `overall_status: 'degraded'`, 7 UNREACHABLE apps (fleet not running locally).
  - T1a harness: 0 dispatched (actionless shape).

- **`signal_studio_judge_stats`** — actionless READ_ONLY (single execution path). Single-endpoint `httpx.Client.get` against `{SIGNAL_STUDIO_API_URL}/api/judge-stats?days=N`.
  - **In scope:** `<default>` (sole execution path).
  - Appendix N: single-endpoint (env-var-driven URL), `authless_by_design` per handler docstring, split `httpx.Timeout(connect=5, read=10, write=5, pool=5)` no retries, no SSRF allowlist (env var trusted by construction), `httpx` default redirects + structured `{ok: False, error, status_code}` envelope.
  - **Live post-merge:** 14ms, `{ok: False, error: 'signal-studio unreachable', days: 1}` (signal-studio not running locally — expected structured shape).
  - T1a harness: 0 dispatched (actionless shape).
  - **Post-merge Ledger candidate:** `error_code: 'legacy_error'` field appeared in the failure envelope but is not documented in §5 or Appendix N. Likely harness-side envelope normalization; forward-carry.

- **`http_smoke_test`** — actionless MUTATION (single execution path with `suite` discriminator). Multi-step HTTP smoke with `OpsRunTracker` DB observability wrap.
  - **Out of scope this ship — MUTATION correctly gated by harness** — every dispatch writes at least 1 `OpsRun` + 2 `OpsRunEvent` rows via `OpsRunTracker.__enter__` / `_emit` / `__exit__` even on payload validation failure.
  - Appendix N: multi-endpoint (per-step from suite or user), `bearer_token` via `_resolve_auth_token` (local DRF Token ORM read OR PA_API_TOKEN env), per-step timeout clamped to 20s + 1MB response cap + no retries, SSRF allowlist `^(localhost|127.0.0.1|*.railway.app)$` + private-IP block, `urllib` default redirects + `HTTPError` captured + auth headers redacted.
  - **Third actionless-MUTATION `TOOL_DEFAULTS` entry** after S2910 `legal_doc_drafter_agent` + S2915 `research_and_create_tool` — **triggers the S2915 forward-carry "actionless side-effecting chain" pattern-naming evaluation** at next Slice close.
  - **Live post-merge:** NOT dispatched (correctly BLOCKED — Rigby verified via `tool_action_metadata.py:450` code read).
  - T1a harness: 0 dispatched (actionless shape + MUTATION default classifies for `skipped_mutation` on hypothetical dispatch attempt).

## Sweep progress (post-S2916)

- Slice 1 (`td_handlers_ops`): UNCHANGED.
- Slice 2 (`td_handlers_agents`): CLOSED at S2912.
- Slice 3 (`td_handlers_core`): **20/22 shipped; 2 remaining.** Batch 6 ships the network trio; the async duo (`studio_tool` + `workflow_run_tool`) remains for batch 7.
- Slice 4 (`td_handlers_gateway`): queued.
- Slice 5 (`tool_dispatcher`): queued.

- **Total corpus untested:** 52 → **49** (batch 6 flipped 3 untested → 2 full + 1 partial).
- **Gap map:** 43 full + 11 partial + 49 untested (validation-doc counts; auto-classifier `category` column in `docs/audits/PA_TOOLS_GAP_MAP.md` remains `untested` for actionless tools per S2915 precedent — validation docs are the truth, classifier is a hint).
- Session cumulative pace: 3 tools / 1 batch / 1 session (with in-depth 2-turn SIGN + post-merge live verify).

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

- PR #3462 recycled clean at `sha=a56accd865cc`: 5 fresh workers (default + pa + long_running + broadcast + code_jobs), zero surviving old PIDs.
- Live verify dispatches (documented above) at HEAD `a56accd86`.

## Ledger candidates raised this session

**NEW S2916 batch 6 Ledger candidates:**

- **Row #38 — §5b needs standardized appendices (Network-Preflight + Async-Fanout).** Rigby Q4 Fold candidate. Prevents notes-field creep into unreviewable policy surface. Classification: **future-trigger.** 1st adoption this batch (Network-Preflight); 2nd adoption at batch 7 (async duo → Async-Fanout appendix) promotes to Fold-candidate evaluation at next Slice close.

- **Third actionless-MUTATION `TOOL_DEFAULTS` entry** (`http_smoke_test` after S2910 `legal_doc_drafter_agent` + S2915 `research_and_create_tool`). **3rd instance — triggers the S2915 forward-carry "actionless side-effecting chain" pattern-naming evaluation** at next Slice close. Shape: single-execution-path tool that unconditionally performs I/O with persistent side effect on every dispatch, classified at tool level not per-action.

- **Observability-tracker as unconditional MUTATION vector.** `OpsRunTracker.__enter__` writes an `OpsRun` row BEFORE the wrapped operation even executes. Any PA tool wrapping in `OpsRunTracker` inherits MUTATION classification regardless of the wrapped operation's own safety class. **1st instance** — watch for 2nd during batches 6-7 or Slice 4-5.

- **Post-merge undocumented envelope field.** `signal_studio_judge_stats` returned `error_code: 'legacy_error'` in the failure envelope during post-merge live verify — not documented in §5 or Appendix N. Likely harness-side envelope normalization applied at the entrypoint (not handler-emitted). **1st instance** — watch for other undocumented envelope-level fields during batch 7 live verify.

- **Rigby T0 SIGN turn-1 catch: HMAC-claim without grep verification.** My initial framing described `fleet_health` as "HMAC signing path via mgmt command" — Rigby's grep for `HMAC` returned zero matches in the codebase. Corroboration: verify-before-claim discipline for cross-file architecture claims (subclass of `feedback_verify_at_raw_orm_before_trusting_tool_no_data`). **1st instance in sweep** — watch during batches 6-7 for other cross-file architecture claims not grep-verified before SIGN routing.

## Forward-carry from prior sessions (unchanged unless noted)

- S2914 batch 4 candidate — "hidden network/LLM in read-shaped gateway" pattern: 2 instances (S2913 `conversation_tool.search` + S2914 `intelligence_tool.search`). **Not corroborated at batch 6** (network trio is explicitly network-classed, not hidden). Watch batch 7 async duo for asymmetric Celery-task hidden cost.
- S2915 batch 5 candidate — "opaque callee trust-downgrade pattern": watch discipline. Batch 6 recorded 0 new opaques (all first-hop callees were read this batch — `probe_fleet` + `OpsRunTracker` + `run_smoke_test` + `_resolve_auth_token` all enumerated with firm evidence). Good sign; §5c "revisit trigger" discipline introduced in batch 6 (kept as rule inside §5b per Rigby SIGN turn-2 pushback, not new section).
- S2915 batch 5 candidate — `NEXT_HEADING_RE` breaks parity on `###` subsections: 2 instances (S2914 + S2915). **Not corroborated at batch 6** (all 3 batch 6 docs use ### subsections only under §5b/Appendix N, which are AFTER `## Covered actions` — no `###` under Covered actions in any of the 3 docs). Third instance would trigger parser fix evaluation.

## Environmental state at close

- HEAD: `a56accd86` after PR #3462 squash-merge.
- Workers: fresh at sha=`a56accd865cc` per `make recycle-all` post-merge (5 workers + beat + daphne).
- Wrapper pin at close: `pa-43e10ef28cae4122` (will bump to next-session pin via `session_lifecycle close --label s2916-slice-3-batch-6`).
- Test guards: 76 passed across metadata seed + gap-map + harness precheck + soft-error + in-class classifier. Preexisting failure in `test_pa_tool_schema_drift` unchanged (8 tools with declared-but-unhandled schema actions; none in batch 6).
- Local truth: `make recycle-all` succeeded; live dispatches (fleet_health + signal_studio_judge_stats) returned expected shapes. No production observation window per `feedback_local_truth_no_production`.

## For fuller S2916 context

- S2916 T0 SIGN cycle (turn 1 + turn 2): `ChatConversation` rows in conversation `pa-43e10ef28cae4122` (last 2 turns).
- Batch 6 per-tool validation docs: `docs/research/tools/validation/{fleet_health,signal_studio_judge_stats,http_smoke_test}_validation.md`.
- Metadata seed: `core/services/tool_action_metadata.py:386-473` (Slice 3 batch 6 comment block + 3 TOOL_DEFAULTS entries).
- Harness output: `docs/audits/pa_tools/harness_output/{fleet_health,signal_studio_judge_stats,http_smoke_test,summary}.json`.
- PR: [#3462](https://github.com/clwest/donkey-betz-platform/pull/3462).
