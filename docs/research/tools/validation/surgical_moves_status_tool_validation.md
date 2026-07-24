# `surgical_moves_status_tool` — Validation Report (S2935)

**Tool:** `surgical_moves_status_tool`
**Schema:** `core/services/pa_tool_schemas.py:666` (1 param declared: `verbose` — NOT honored by handler; see §3 drift)
**Handler:** `core/services/td_handlers_content.py:3875` (`_handle_surgical_moves_status`)
**Register site:** `core/services/tool_dispatcher.py:476`
**Session:** S2935 (Slice 6 batch 1 — quartet with `execution_history_tool` (§6 primary anchor) + `learning_patterns_tool` + `recent_activity_tool`)
**HEAD at validation:** `54f74adde` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape) + **schema-realignment edit bundled in same PR** (declare `action=summary|detailed` + `hours` + `session_id` in schema to match handler; deprecate `verbose` as unhandled). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2935 T0 SIGN AGREE (tool-grounded — handler line 3875-3974 verified pure-read on `DeliberationSession` + `DeliberationTurn` + `ContractRecord`). Q4(c) surfaced schema-under-describes-handler drift as Ledger candidate + schema-fix-in-PR (Chris ratified).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`surgical_moves_status_tool` surfaces **DeliberationSession telemetry** — the "surgical moves" pipeline that runs multi-agent debates over specific content decisions (e.g., "publish, revise, or kill this blog post"). Returns session status, contract counts (synthesis contracts), turn counts, evidence stats (sources, claims, contradictions, internal_refs), and decision verdicts. Use it when Chris asks "surgical moves status", "what deliberations happened", "did that content-decision session complete", or "what did the deliberator decide about post X".

Distinct from `execution_history_tool` (agent executions — DeliberationSessions are separate rows and separate lifecycle); from `recent_activity_tool`'s `sections.conversations` (which surfaces HiveMindSession, a different subsystem entirely); from `content_verification_tool` if one exists elsewhere. This tool is the deliberation-pipeline health check.

## Covered actions

The **schema does NOT declare an `action` param** (declares only `verbose` boolean, which the handler ignores), but the handler DOES accept `action` (line 3896). This is the primary drift addressed in this ship's bundled schema fix. Under handler behavior:

- `summary` — **in scope this ship — verified live.** Default action. Returns recent DeliberationSessions with per-session key stats. `limit=5` (line 3900). Envelope: `{action, hours_back, total_sessions, runs[]}`.
- `detailed` — **in scope this ship — verified via handler code (not exercised live).** Same shape but `limit=20` (line 3900). Envelope identical to `summary`; only the item count differs.
- **default (no `action` param)** — **in scope this ship — verified live.** Defaults to `summary` per `payload.get('action', 'summary')` at line 3896.
- **invalid action** — **NOT gated.** Same as `recent_activity_tool` — no `else` branch that raises `ValueError`. Any string flows through as `limit=20` (since only `summary` matches `if action == 'summary'` at line 3900). Divergence from `execution_history_tool` / `learning_patterns_tool`. Documented in §5.

## 3. Schema notes

- **Required:** none.
- **Optional (per schema):** `verbose` (boolean) — **NOT HONORED by handler.**
- **Optional (per handler, missing from schema):** `action` (`summary` / `detailed`); `hours` (int, default **24**); `session_id` (UUID string; when passed, returns only that specific session instead of the recent window).
- **Drift severity:** the largest of the batch. Schema declares one wrong param + omits three real ones. Callers can't discover from the schema how to filter by session_id, change action, or adjust the time window. **This ship declares `action` + `hours` + `session_id` in the schema** to match handler behavior. `verbose` is kept for backward-compat (silently ignored; documented as unhandled).
- **`session_id` short-circuits time window:** if passed, `hours` is ignored and the handler queries exactly `DeliberationSession.objects.filter(id=session_id)` (line 3915-3916). Result may still be empty if the session doesn't exist.
- **`limit` behavior:** hardcoded to `5` for `summary`, `20` for `detailed`. Not caller-configurable via a schema param.
- **Per-session heavy work:** for EACH session in the result set, the handler runs 2 additional queries (`DeliberationTurn.filter(session=s)` + `ContractRecord.filter(session=s)`) + iterates all contracts to compute `data_size` via `json.dumps(cdata)` (line 3931-3937). N+1 pattern; not a bug at limit=5-20 but worth noting for larger callers.
- **ImportError guard:** if `core.models_deliberation` imports fail (e.g., subsystem disabled), the handler returns `{'action': <action>, 'error': 'Deliberation models not available'}` at line 3908-3912. Tool never crashes on missing dependency.
- **Top-level exception guard:** any exception in the loop returns a full-envelope response with `error: str(e)` at line 3966-3974 — the tool always returns a well-shaped envelope, never raises to caller.

## 4. Golden-path examples

**Example 1 — "Surgical moves status?" (default):**
```json
{}
```
→ `{"action":"summary", "hours_back":24, "total_sessions":5, "runs":[{session_id, objective, status, created_at, turn_count, contract_count, contracts:[{type, data_size}], decision_verdict, evidence_stats:{sources, claims, contradictions, internal_refs}}...]}`

**Example 2 — Wider window with more items:**
```json
{"action": "detailed", "hours": 168}
```
→ Same envelope; up to 20 sessions from last 7 days.

**Example 3 — Specific session lookup:**
```json
{"session_id": "<uuid>"}
```
→ `{"action":"summary", "hours_back":24, "total_sessions":1, "runs":[{...1 row for that session...}]}`. Note `action` defaults to `summary` — the `session_id` doesn't override action selection.

## 5. Failure / empty-state / pagination notes

- **Empty state (no sessions in window):** returns `{"action":<action>, "hours_back":<n>, "total_sessions":0, "runs":[]}`. Never `null`.
- **`session_id` not found:** returns `{"action":<action>, "hours_back":<n>, "total_sessions":0, "runs":[]}` — SAME shape as empty-window. No "not found" indicator; caller must check `total_sessions=0` and infer.
- **`decision_verdict` nullable:** if a session has no `execution` contract (i.e., deliberation didn't reach a decision), `decision_verdict` is `null`. If the execution contract exists but has no `chosen_path` or `decision` key, still `null`. **Observed in S2935 evidence** — all 5 recent sessions had `decision_verdict=null` because none had an `execution` contract yet (only `synthesis` contracts). This is a data-condition observation, not a bug.
- **`decision_verdict` truncated at 200 chars:** if the verdict is a longer string, it's truncated at line 3941 — no truncation indicator surfaced.
- **`objective` truncated at 120 chars:** if the DeliberationSession's `objective` is longer, it's truncated at line 3945 — no indicator.
- **Deliberation subsystem missing:** `ImportError` on `core.models_deliberation` returns `{'action': <action>, 'error': 'Deliberation models not available'}` (line 3908-3912). This is the ONLY branch that surfaces a top-level `error` key.
- **Invalid action NOT gated:** same as `recent_activity_tool`. Any string flows through as `limit=20`. Divergence from `execution_history_tool` / `learning_patterns_tool` which `raise ValueError`. Ledger candidate for consistency work.
- **Contract data_size computed via `json.dumps`:** per-contract serialization cost — for sessions with large contract payloads (~5-7KB observed in evidence), this is inexpensive but scales linearly with contract count.
- **Pagination:** none. Callers wanting more items switch to `action=detailed` (5 → 20) or query by specific `session_id`.

## 6. Evidence

Live PA-dispatch evidence, S2935 T0 (HEAD `54f74adde`, 2026-07-24). All exercises via `surgical_moves_status_tool` handler at `td_handlers_content.py:3875`.

### 6.1 `action=summary` (default `hours=24`)

Envelope: `{action:"summary", hours_back:24, total_sessions:5, runs:[5 items]}`. Observed:
- All 5 sessions had objective `"Decide whether to publish, revise, or kill this blog post"` (auto-generated deliberation for the blog pipeline).
- All 5 had `status='completed'`, `turn_count=4`, `contract_count=1`, single `synthesis` contract with `data_size` 5755–6752 bytes.
- All 5 had `decision_verdict=null` — no execution contract yet (documented in §5).
- `evidence_stats`: `sources=1` uniformly; `claims=0`; `contradictions=1–3`; `internal_refs=0`.

**Empty-state contract clean; realistic session structure surfaced.**

### 6.2 `action=detailed hours=168`

**Not exercised live** (Rigby wrapper output-size cap in the T0 batch). Handler code (line 3900) confirms `limit=20` for any non-`summary` action; envelope shape identical to `summary`.

### 6.3 Default action (`{}` payload)

**Not exercised as a separate call**; handler line 3896 confirms default = `summary` via `payload.get('action', 'summary')`. Consistent with §6.1.

### 6.4 `session_id` short-circuit

**Not exercised live**; handler line 3915-3916 confirms `session_id` bypasses the time-window filter. Caller-observable via `total_sessions=1` (or 0 if not found) with the specified session id in `runs[]`.

### 6.5 Silent-ignore behavior for `verbose`

**Not exercised via failing dispatch**; handler line 3896-3900 confirms `verbose` is never read from payload. Callers passing `verbose=true` see no effect (the closest analog is `action=detailed`, which changes `limit` behavior). Primary evidence for the schema-fix rationale.

## Related

- **Adjacent tools (same Slice 6 batch 1):** `execution_history_tool` (agent-executions — DeliberationSessions are separate lifecycle rows); `learning_patterns_tool` (orthogonal); `recent_activity_tool`'s `sections.conversations` (HiveMindSession — DIFFERENT subsystem from DeliberationSession, easy confusion point).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`; `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 6 pre-batch-1 = 6 untested, this row marked `no_required` lint pre-fix).
- **Prior ratifications:** S2892 Path B open; S2907 T0 Fold E; S2921 §5a taxonomy; S2928 Slice 5 CLOSE.
- **First-hop dependencies:** none — pure ORM read from `DeliberationSession` + `DeliberationTurn` + `ContractRecord` tables. §5b Appendix N/A not applicable.
- **Ledger row (opened this ship, shared with `recent_activity_tool`):** schema-under-describes-handler drift — schema declares `verbose` only (unhandled); handler uses `action` + `hours` + `session_id`. Same-class instance to `recent_activity_tool` fix — both bundled in same PR.
- **Ledger row (deferred, shared with `recent_activity_tool`):** invalid-action non-gating divergence from `execution_history_tool` / `learning_patterns_tool` — no `raise ValueError` for unknown actions. Cross-Slice-6 consistency candidate.
- **Post-merge live-dispatch verification:** exercise `surgical_moves_status_tool action=detailed hours=168` after `make recycle-all` at merge; confirm `limit=20` behavior visible in `runs[]` count.
