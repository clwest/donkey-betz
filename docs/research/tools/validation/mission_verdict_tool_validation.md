# `mission_verdict` — Validation Report (S2939)

**Tool:** `mission_verdict`
**Schema:** `core/services/pa_tool_schemas.py:5867` (3-action enum + 4 optional params)
**Handler:** `core/services/td_handlers_employee.py:434` (`_handle_mission_verdict`; shared module — sibling tool `employee_tool` at :100 lands in Batch 2b)
**Register site:** `core/services/tool_dispatcher.py:643`
**Session:** S2939 (Slice 7 Batch 2a — trio with `newsletter_tool` + `rigby_work_item`)
**HEAD at validation:** `acca1f4e2` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. **All-mutation tool** — no read actions exist, so §6 LIVE-VERIFIED does not apply; §5a ANALYZED-NOT-EXECUTED covers all 3 actions with signal-chain evidence. Live mutation verification deferred pending handler-layer `dry_run` affordance (Ledger #38).
**Category upgrade target:** `untested` → `validated_partial` (all actions analyzed-only — no live-verify surface possible without mutation)
**Rigby SIGN:** S2939 T0 SIGN AGREE-WITH-EDITS Q3 (mutation-only mission_verdict OK; code-cite the 2 post_save receivers rather than hard-claim). Both edits incorporated inline. Chris D-verdict at T0 RATIFIED with two guardrails baked in (§6 read-only scope sentence + §5a mutation proof bar cited).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`mission_verdict` is Rigby's **certification surface for a MissionRun** — after inspecting a mission's evidence (OpsRunEvents, LLMCallEvents, ToolCallRecords), Rigby emits one of three verdicts: `certify` (passed), `reject` (failed), or `defer` (partial). The tool writes exactly one `OpsRunEvent(label='verdict_issued:<verdict>')` and flips `OpsRun.status` from `running` to the terminal value. Use it when Chris asks "certify this mission", "the docs cascade run looks good — approve it", "reject mission `<uuid>`, the LLM claim doesn't match the code", or when Rigby is closing out a Documentation Manager / Platform Auditor / Chief of Staff daily mission after evidence review.

Distinct from `employee_tool action=run_now` (dispatches a new mission; verdict lands here after evidence review); from `employee_tool action=evidence_for_mission` (read-only evidence dump — the input to the verdict decision); from `ops_tool` (per-subsystem SLO reads, not mission certification). This tool is the **terminal write** in the Employee OS lifecycle — running → certified/rejected/deferred — and is the only PA-surface path that can flip a MissionRun's terminal status.

## Covered actions

Enumerating every action in the schema `action` enum. **0 read actions**; **3 mutation actions ANALYZED-NOT-EXECUTED** per Option C batch shape (§5a below).

- `certify` — **ANALYZED-NOT-EXECUTED — MUTATION `cascading`** — see §5a. Maps to `VERDICT_CERTIFIED` (`_ACTION_TO_VERDICT` at `td_handlers_employee.py:60`). Writes one `OpsRunEvent(label='verdict_issued:certified', event_type='step_pass')` + flips `OpsRun.status` from `running` → `passed` (via `emit_mission_verdict` at `core/employees/mission_verdict.py:63`).
- `reject` — **ANALYZED-NOT-EXECUTED — MUTATION `cascading`** — see §5a. Maps to `VERDICT_REJECTED`. Writes `verdict_issued:rejected` (event_type=`step_fail`) + flips `OpsRun.status` → `failed`.
- `defer` — **ANALYZED-NOT-EXECUTED — MUTATION `cascading`** — see §5a. Maps to `VERDICT_DEFERRED`. Writes `verdict_issued:deferred` (event_type=`info`) + flips `OpsRun.status` → `partial`.
- **default (no `action` param)** — verified via handler code inspection (`td_handlers_employee.py:452`). Empty/missing `action` returns `{"ok": False, "error": "Unknown mission_verdict action ''; valid: ['certify', 'defer', 'reject']", "valid_actions": [...]}`. **No implicit default** — differs from newsletter_tool (defaults to `list_issues`) and rigby_work_item (defaults to `list`). Load-bearing: prevents accidental verdict emission.
- **invalid action** — verified via handler code inspection (`td_handlers_employee.py:453-461`). Non-raising in-envelope error `{"ok": False, "error": "...", "valid_actions": [...]}`. Same in-envelope pattern as recent_activity_tool + rigby_shift_brief_tool (Ledger #5 consistency lint candidate — third-instance corroboration at S2939).

## 3. Schema notes

- **Required:** `action` (enum: `certify` | `reject` | `defer`). Note the schema declares only `action` in `required[]`; `mission_id` is a runtime hard-require (handler line 479-484) but not schema-enforced. **Minor schema/handler drift** — schema description says "Use after you have inspected the mission's evidence" but doesn't hint that `mission_id` is mandatory. Callers who omit `mission_id` get `{"ok": False, "error": "Missing required arg 'mission_id'."}` from the handler.
- **Optional:** `mission_id` (UUID string — handler-required, schema-optional; see above); `confidence` (float 0.0–1.0; clamped in `emit_mission_verdict` line 98-104; non-numeric raises `ValueError`); `evidence_refs` (list of pointer strings, e.g. `["llm_call:<uuid>", "deliverable:<uuid>"]` — passed through into `OpsRunEvent.detail` as-is); `notes` (free-form string, default `""`).
- **`issued_by` is server-set:** handler forces `issued_by=RIGBY.handle` (line 494) regardless of caller. Callers cannot spoof the emitter identity via payload.
- **Auth gate:** v0 channel gate at `td_handlers_employee.py:466` — `_verify_rigby_caller(user_id)` requires the resolved username == `RIGBY.runs_as_username` (currently `"chris"`). Fails return `TOOL_PERMISSION_DENIED` with `auth_gate` field describing the v0 limitation (channel gate, not speaker gate — Chris-typing and Rigby-as-LLM both pass because they share user_id). Module docstring at `td_handlers_employee.py:14-26` is explicit about this.
- **No `dry_run` affordance:** every non-empty valid dispatch mutates. Ledger #38 substrate design session queued to add a `dry_run` mode across batch-2 mutations (blog_tool + feedback_tool + this tool + newsletter_tool + rigby_work_item), which would unblock §6 LIVE-VERIFIED for all-mutation tools.

## 4. Golden-path examples

**Example 1 — Certify a completed docs_cascade mission:**
```json
{"action": "certify", "mission_id": "<mission-uuid>", "confidence": 0.95, "notes": "Docs cascade evidence reviewed — 3 handoffs mirrored, 00-START refreshed, verifier zero drift."}
```
→ `{"ok": true, "action": "certify", "mission_id": "<uuid>", "verdict": "certified", "issued_by": "rigby", "confidence": 0.95, "event_id": "<uuid>", "event_created": true, "previous_status": "running", "current_status": "passed", "status_changed": true}` — per `emit_mission_verdict` return shape at `core/employees/mission_verdict.py:164-175`.

**Example 2 — Reject with evidence pointers:**
```json
{"action": "reject", "mission_id": "<mission-uuid>", "confidence": 0.85, "evidence_refs": ["llm_call:<uuid>", "deliverable:<uuid>"], "notes": "Claim about 4 handoffs written contradicts filesystem (only 2 present)."}
```
→ Same envelope shape; `verdict="rejected"`, `current_status="failed"`.

**Example 3 — Defer (needs re-run):**
```json
{"action": "defer", "mission_id": "<mission-uuid>", "notes": "Partial output — worker OOM at step 3, retry after infra fix."}
```
→ `verdict="deferred"`, `current_status="partial"`.

**Example 4 — Idempotent re-emit (same verdict twice):**
```json
{"action": "certify", "mission_id": "<mission-uuid>"}   // second call
```
→ `{"ok": true, ..., "event_created": false, "status_changed": false, "previous_status": "passed", "current_status": "passed"}` — event row is reused via `get_or_create(run=..., label=..., defaults=...)` at `mission_verdict.py:133-140`; status flip guarded by `if mission_run.status == "running"` at line 148.

## 5. Failure / empty-state / pagination notes

- **Unknown verdict action:** in-envelope error `{"ok": False, "error": "Unknown mission_verdict action '<x>'; valid: ['certify', 'defer', 'reject']", "valid_actions": [...]}`. Non-raising (`ok:false`).
- **Auth gate failure (non-Rigby caller):** `{"ok": False, "error": "...", "error_code": "TOOL_PERMISSION_DENIED", "auth_gate": "v0 gate: caller user_id must resolve to username='chris'..."}`. Non-raising.
- **Missing `mission_id`:** `{"ok": False, "error": "Missing required arg 'mission_id'."}`. Non-raising.
- **Unknown `mission_id`:** `emit_mission_verdict` raises `ValueError("No MissionRun (OpsRun domain='mission') with id=<x>.")` at `mission_verdict.py:111-114`; handler catches at line 496-500 and returns `{"ok": False, "error": "..."}`. Non-raising to caller.
- **Non-numeric `confidence`:** `emit_mission_verdict` raises `ValueError("confidence must be a number 0.0-1.0; got <x>.")` at line 102-104; handler catches → in-envelope error. Non-raising.
- **`confidence` outside 0.0–1.0:** silently clamped (line 100 `max(0.0, min(1.0, float(...)))`). Callers passing 2.5 get 1.0 without warning.
- **Idempotency across re-invocation:** second call with same `(mission_id, verdict)` returns `event_created=False` (existing row re-used). Second call with a DIFFERENT verdict on an already-terminal mission returns `event_created=True` (new row appended) but `status_changed=False` (`previous_status == current_status` — terminal statuses are preserved). This means a verdict timeline CAN accumulate multiple `verdict_issued:*` rows if callers change their minds, but the mission's authoritative status stays with the first non-`running` value.
- **No pagination / no rate limits.** Single-mission, single-verdict, per-call semantics.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1; 4-tier blast-radius taxonomy added S2921)

**REQUIRED — 3 mutation actions declared in `## Covered actions` (certify / reject / defer). ANALYZED-NOT-EXECUTED at this ship per Chris D-verdict guardrail. Live mutation verification deferred pending handler-layer `dry_run` affordance (Ledger #38).**

### Per-action blast-radius classification

| Action | Tier | Handler line | Direct writes | Signal fan-out | External touches |
|---|---|---|---|---|---|
| `certify` | `cascading` | `td_handlers_employee.py:487-495` → `mission_verdict.py:132-161` | `OpsRunEvent.get_or_create` (1 row, idempotent) + `OpsRun.save(update_fields=['status','finished_at','summary'])` (1 row, only if `status == 'running'`) | **2 receivers on OpsRunEvent.post_save** — see §5a "Signal-chain evidence" below | none direct; broadcast receiver hops to Channels group_send (WebSocket fan-out) via `emit_system_event_sync` |
| `reject` | `cascading` | same handler path | same writes (`event_type='step_fail'`) | same 2 receivers | same broadcast + potential HAI escalation |
| `defer` | `cascading` | same handler path | same writes (`event_type='info'`) | same 2 receivers; **HAI receiver escalates on 'deferred' verdict** per `mission_verdict_attention_signals.py:68` (label check + verdict-in-escalate-set) | same broadcast + guaranteed HAI escalation |

All 3 actions classified `cascading` (not `spreading`): the OpsRunEvent `post_save` receiver chain triggers ORM-observer effects (WebSocket broadcast) and downstream HAI (Human Attention Item) creation for `deferred` + `rejected` verdicts. `contained` and `spreading` tiers are ruled out because the signal chain leaves the OpsRunEvent table.

### Signal-chain evidence (Chris D-verdict guardrail — file/line cited)

1. **Broadcast receiver:** `core/signals/mission_verdict_signals.py:56` `broadcast_mission_verdict(sender, instance, created, **kwargs)` — `post_save` receiver on `OpsRunEvent`, wired at `mission_verdict_signals.py:101-105` via `post_save.connect(broadcast_mission_verdict, sender=OpsRunEvent, dispatch_uid=...)`. Fires only when: `created=True` AND `label.startswith('verdict_issued:')` AND `run.domain == 'mission'` (defensive filters at lines 68-82). On match: schedules `_broadcast_verdict(...)` via `transaction.on_commit(...)` at line 88-90 → calls `emit_system_event_sync("mission_verdict", {...})` at line 40-48 → Channels group_send to WebSocket subscribers. **Rollback-safe** (on_commit means aborted transactions don't emit).
2. **HAI escalation receiver:** `core/signals/mission_verdict_attention_signals.py:68` `escalate_mission_verdict_to_hai(sender, instance, created, **kwargs)` — second `post_save` receiver on `OpsRunEvent`. Escalate set per module init log: `['deferred', 'rejected']` (deferred + rejected verdicts create Human Attention Items; certified does not).
3. **Coexistence proof:** `core/tests/test_mission_verdict_attention.py:155` — regression test `"Both broadcast + HAI receivers fire on the same OpsRunEvent row"` confirms both receivers wire independently and fire on the same event write. Zero receiver-ordering assumption.

### Idempotency proof bar (Chris D-verdict guardrail)

- **Row-level idempotency:** `OpsRunEvent.objects.get_or_create(run=mission_run, label=label, defaults={...})` at `mission_verdict.py:133-140` — unique (run_id, label) pair guarantees exactly one row per `(mission_id, verdict)`. Repeat calls return `created=False`.
- **Status-flip idempotency:** `if mission_run.status == "running"` guard at `mission_verdict.py:148` prevents terminal-status overwrite. Once a mission is `passed`/`failed`/`partial`, subsequent verdicts append event rows but do NOT re-flip status.
- **Idempotency on receiver side:** `broadcast_mission_verdict` guard `if not created: return` at line 68-69 short-circuits on UPDATEs. Only fresh INSERTs emit WebSocket broadcasts. HAI receiver has an analogous guard.

### Deferral rationale (why not live-fire this ship)

- Live-firing `certify` on a real mission would irreversibly flip its status and enqueue a Channels broadcast + potential HAI. No safe test mission is available (all existing missions are either terminal or actively running).
- Handler-layer `dry_run` affordance (Ledger #38) would let §6 LIVE-VERIFIED cover the "returns the shape it would write" contract without side effects. Rigby S2939 zoom-out AGREE-WITH-EDITS: keep §6 stubbed for now; force Ledger #38 only if a hidden-side-effect surprise surfaces in Batch 2b or 2c.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `_verify_rigby_caller` | `read` (auth check — ORM read `UserModel.objects.get(id=user_id)`) | `td_handlers_employee.py:466` → `td_handlers_employee.py:629-672` | validated |
| `emit_mission_verdict` | `db_write` (delegates to helper — 1 event row + 1 mission row) | `td_handlers_employee.py:488` → `core/employees/mission_verdict.py:63` | validated (`test_mission_verdict.py` + `test_mission_verdict_broadcast.py` + `test_mission_verdict_attention.py`) |
| `RIGBY.handle` | `read` (constant string, employee registry lookup) | `td_handlers_employee.py:494` → `core/employees/jobs.py` `_EMPLOYEES_BY_HANDLE['rigby']` | validated |
| OpsRunEvent `post_save` (indirect) | `dispatch` (signal fan-out — 2 receivers) | fires on `mission_verdict.py:133` INSERT | §5a "Signal-chain evidence" |

**No Appendix N (Network-Preflight) needed:** first-hop `_broadcast_verdict` uses `emit_system_event_sync` → Channels layer → in-process group_send. No HTTP; no external network.

**No Appendix A (Async-Fanout) needed:** signal chain is `transaction.on_commit(...)` (sync callback, not Celery `apply_async`). Broadcast lands on Channels' worker layer but is not a Celery task dispatch.

## 5c. Contract ↔ Implementation Consistency (S2937 retro-fold; per Rigby zoom-out #4)

### 5c.1 Handler / module header claims match action reality

**Disposition: PASS with one minor drift note.** Module docstring (`td_handlers_employee.py:1-26`) accurately describes: two tools (employee_tool + mission_verdict), the v0 auth-gate limitation, and the Rigby-only gate contract. Handler docstring (line 441-451) accurately names 3 actions (certify/reject/defer), writes one OpsRunEvent, flips OpsRun.status, idempotency guarantees. Schema description (`pa_tool_schemas.py:5868-5876`) matches: names all 3 actions, correctly describes idempotency, correctly cites `TOOL_PERMISSION_DENIED` on gate fail. **Minor drift:** schema description doesn't mention that `mission_id` is required (schema declares only `action` in `required[]`, and description text doesn't emphasize the runtime requirement). Not a Ledger candidate — surface at §Related for future schema tightening.

Ledger #5 lint pre-flight at S2939 open: **0 handler_drift hits on `mission_verdict`** (verified via `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check`). Consistent with PASS disposition.

### 5c.2 Gating truth matches runtime behavior

**Disposition: PASS — auth-gated (not flag-gated).** No Django settings flag; the gate is the v0 `_verify_rigby_caller` check. Doc-level PASS because the gate is honest about its limitation (module docstring lines 14-26 explicitly note the channel-vs-speaker gap). No `disabled_response` shape to LIVE-VERIFY at this ship — the gate returns `{ok: False, error: ..., error_code: TOOL_PERMISSION_DENIED}` when a non-Rigby user_id hits it, but exercising that path requires a non-Rigby user_id and does not mutate state (safe to LIVE-VERIFY at post-merge if desired; deferred this ship).

### 5c.3 Shared handler-file coupling noted

**Disposition: SHARED MODULE — cross-link required.** `td_handlers_employee.py` hosts two tools:
- `employee_tool` (handler at `_handle_employee_tool` line 100 — read-only: describe / run_now / status / evidence_for_mission)
- `mission_verdict` (this doc — mutation-only: certify / reject / defer)

Coupling: both tools share the `_ACTION_TO_VERDICT` constant (line 60-64), the `_verify_rigby_caller` helper (line 629), the `_wait_for_terminal_mission` polling helper (line 512), and the `_RUN_NOW_TASKS` registry (line 569). `employee_tool` validation doc will land in **Slice 7 Batch 2b** and MUST reference this doc for the shared-helper cross-link. Future edits to any of those shared symbols require a joint sweep of both docs.

## 6. Evidence

**LIVE-VERIFIED applies only to strictly read-only actions executed in a non-mutating way; all mutations remain §5a ANALYZED-NOT-EXECUTED.** (Chris D-verdict guardrail; sentence lifted verbatim per S2939 T0 ratification.)

`mission_verdict` has **0 read actions** — every action in the schema `action` enum is a mutation. Therefore §6 has no LIVE-VERIFY subsections at this ship. All action-behavior evidence is in §5a (blast-radius classification + signal-chain code-cite + idempotency proof) + §5b (first-hop dependency proof) + §5c (contract-vs-impl consistency).

Post-merge live-dispatch verification per PLAYBOOK-7.4.4: exercise `mission_verdict action=<invalid>` (in-envelope error path — no mutation) after `make recycle-all` at merge; confirm the error envelope matches §5 shape (`ok:false`, `error:"Unknown mission_verdict action..."`, `valid_actions:[...]`). This is the closest "safe verify" available for a tool with no read actions.

## Related

- **Adjacent tools (same Slice 7 Batch 2a):** `newsletter_tool` (4-mut/3-read bifurcated), `rigby_work_item` (5-action, flag-gated, auto-flagged by Ledger #5 lint). All three ship §5a ANALYZED-NOT-EXECUTED for mutations.
- **Adjacent tools (same handler module — Batch 2b):** `employee_tool` (describe/run_now/status/evidence_for_mission — read-only; ships next batch with cross-link back to this doc).
- **Adjacent tools (verdict-adjacent):** `employee_tool action=run_now` dispatches missions whose verdicts this tool emits; `employee_tool action=evidence_for_mission` returns the evidence Rigby reviews before calling this tool.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1 + §5c retro-fold added S2937); `docs/audits/PA_TOOLS_GAP_MAP.md`.
- **Prior ratifications:** S2892 Path B open; S2907 T0 Fold E; S2921 §5a taxonomy; S2928 Slice 5 CLOSE; S2936 Slice 6 CLOSE (bifurcated Option C shape precedent for mutation-heavy tools); S2937 T1 Chris ratification (4-batch Slice 7 plan + §5c retro-fold); **S2938 Ledger #5 lint promoted to substrate — this batch is the first live-in-force pre-flight consumer**; S2939 T0 Chris D-verdict RATIFIED with two guardrails (§6 scope sentence + §5a mutation proof bar).
- **Lint pre-flight at S2939 open:** `mission_verdict` → 0 `handler_drift_*` hits (verified via `--gap-only --emit-gap-json --check`).
- **First-hop dependencies:** none externally-network-facing. See §5b table. Signal-chain fan-out documented in §5a.
- **Regression coverage:** `core/tests/test_mission_verdict.py` (idempotency + auth gate + verdict-status mapping); `core/tests/test_mission_verdict_broadcast.py` (broadcast receiver behavior); `core/tests/test_mission_verdict_attention.py` (HAI escalation receiver, incl. line 155 "both receivers fire" invariant).
- **Ledger candidates surfaced this doc:** none new. Minor `mission_id` schema-description drift noted at §5c.1 (record-only, not a Ledger). Ledger #38 (`dry_run` substrate) remains the blocker for LIVE-VERIFY on mutation tools — this doc is one more corroboration.
- **Post-merge live-dispatch verification:** exercise `mission_verdict action=<invalid>` after `make recycle-all` at merge; confirm in-envelope error shape.
