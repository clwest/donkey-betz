# Session 3038 — S8 instrumentation + A3 error-type classifier shipped

**Closed:** 2026-07-29
**HEAD at close:** filled at cascade merge (post-`80ac66499`)
**Session shape:** Two-PR remediation slate from the S3037 Reliability Audit backlog — S8 (WEDGE-BLOCKING cheap win) + A3 (quick governance improvement). Fresh session opener; Chris picked S8 first, sliced A3 in mid-session.

---

## What shipped

### Two shipped PRs

**PR #3770 (`a29085b38`) — `feat(s3038-s8): instrument deliverable_tool.create for persistence-gap isolation`.** 1 file, +55/-0. Adds paired `[PA_DELIVERABLES_INTENT]` (handler entry, all actions) + `[PA_DELIVERABLES_ENVELOPE]` (all 5 create-branch exits) log lines sharing `trace_id` with the existing `[PA_TASK_SUMMARY]` from `unified_pa_entrypoint`. Discharges S3037 audit remediation item S8 (Rigby persistence-gap 3rd trigger, wedge-blocking).

**PR #3771 (`80ac66499`) — `feat(s3038-a3): auto-classify LLMCallLog.error_type from error_message`.** 4 files, +287/-0. Three pieces: `core/services/llm_error_classifier.py` (11-pattern regex classifier), `LLMCallLog.save()` pre-persist hook (respects caller intent, fail-open on classifier exception), `manage.py backfill_llm_error_types [--apply] [--limit N]` (idempotent historical backfill). Discharges S3037 audit remediation item A3 (silent-monitoring gap: 305 failed rows in 90d with empty `error_type`).

### S8 diagnostic finding — pre-instrumentation ORM sweep

ORM sweep of the S3037 audit window (2026-07-29 20:00–22:00 UTC) confirmed **zero `pa_deliverables_tool` source rows** — the deliverable-tool handler was never invoked from the failing S3037 dispatches. Combined with 4 in-session synthetic dispatches that all persisted cleanly (min-scope 1-iter / weaker prompt 4-iter / audit-style 5-iter / heavy-synthesis 9-iter), the evidence points to the failure living **upstream of `_handle_deliverables`** — most likely PA loop / LLM synthesis / prompt convergence rather than the handler itself. The instrumentation catches whichever class fires next time so the diagnosis is definitive on repeat.

### A3 backfill — 305 rows classified

`manage.py backfill_llm_error_types --apply` classified 305/305 rows as `connection_error` (matches empirical distribution from the pre-shipping `orm_inspect_tool.count_by` probe). Post-backfill: zero rows remain with `error_message` set and `error_type` empty.

### Rigby Tool Gap Ledger — S8 discharge appended

`5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` in Donkey Betz workspace received an S8 discharge note (1,478 chars appended via `deliverable_tool.append`). Third trigger status flipped `open → mitigated`. The append itself also live-tested the new INTENT log on the `append` action (envelope is create-specific by design).

---

## Session-shape observations

1. **Same dispatch that failed at S3037 succeeded 4/4 this session.** The variable was prompt shape — S3038 dispatches all included explicit `MUST call deliverable_tool.create with args X` framing, or at minimum a clear terminal persistence step. Dispatch 2 used weaker "save your findings" language and still converged. If S3037 dispatches had less-explicit terminal steps, prompt-convergence is the confirmed cause.
2. **Rigby corrected my instruction shape.** I asked her to `deliverable_tool.update` with an `append` parameter; she recognized the correct surface is `deliverable_tool.append` and applied intent correctly. Good example of Rigby-executes-with-judgment (per `feedback_claude_directs_rigby_then_verifies`).
3. **A3 classifier surprise: everything was `connection_error`.** 305/305 rows in 90d empirical data. Not a bad thing — it means the 10 other patterns in the classifier are dormant, waiting for their first real match. `unknown_error` fallback is the tripwire for widening the pattern table.

---

## Remediation backlog remaining (from S3037 Step 6 deliverable `c3cad098-…`)

Shipped S3037: A1, A2, S4, A6, S5. Shipped S3038: **S8, A3**. **Remaining 3 items:**

- **S7** (~1 session, CRITICAL) — Root-cause `ThinkingAgent` 67% async failure. Instrument each ORM call site in `.think()`; consider `sync_to_async` at ORM boundary. **Chris directive: S3039 first action.**
- **S9** (~1 session, HIGH) — Wire downgrade/fallback logic to populate `was_downgraded` / `was_fallback` / `was_auto_selected` on `LLMCallLog`. S2853 shipping claim not empirically visible in 30d/39,971-call sample.
- **D10** (multi-session, DEFERRABLE) — Historical `LLMCallLog.workspace` backfill for 34,049 NULL rows (85.2% of 30d). Reporting quality, not runtime correctness.

Also carried:
- **A6 Phase 2** — root-cause the underlying `lane_1_platform_readiness` bug now that Phase 1 (PR #3767) surfaces the real exception. Waiting for next morning_brief failure to fire with new error surface.

---

## Rigby SIGN this session

None — direct Claude-execute-and-verify shape per `feedback_claude_directs_rigby_then_verifies` fallback for remediation items with Chris-ratified direction and unambiguous design. Precedent from S2988 / S3037. Rigby dispatched 5× this session (S8 spec fetch + 4 synthetic dispatches + 1 ledger update); all succeeded and cross-referenced cleanly via the new instrumentation.

---

## Playbook rule exercise

- **PLAYBOOK-7.7.1** (spec→ship contract) — 2 Flow B spec→ship cycles (PR #3770 S8, PR #3771 A3). Spec = audit remediation-backlog items.
- **PLAYBOOK-7.4.4** (recycle after merge) — `make recycle-all` executed after each of #3770, #3771; events recorded in `logs/recycle_events.jsonl` (sha=a29085b38ba4, sha=80ac6649965a).
- **PLAYBOOK-7.7.3** (Chris-facing decision framing) — session-opener recommendation, mid-session A3 slide-in ask, close-cascade routing all used plain-English framing.
- **Cycle 1A verify-before-build** — 23rd consecutive session. S8: verified existing handler shape at `_handle_deliverables:2602` before adding instrumentation. A3: verified no existing signal on LLMCallLog before choosing `save()` override; verified existing `backfill_*` naming convention before creating the command.

---

## Files touched

**S8 (PR #3770):**
- `core/services/td_handlers_agents.py` (+55/-0) — INTENT log at handler entry + ENVELOPE log at 5 create-branch exits.

**A3 (PR #3771):**
- `core/services/llm_error_classifier.py` (+60, new) — regex classifier.
- `core/models_llm_routing.py` (+15/-0) — `LLMCallLog.save()` hook.
- `core/management/commands/backfill_llm_error_types.py` (+65, new) — backfill command.
- `core/tests/test_s3038_llm_error_classifier.py` (+147, new) — 16-test suite.

---

## Deliverables touched (Donkey Betz workspace `b4503364-…`)

| Deliverable | Change |
|---|---|
| `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Rigby Tool Gap Ledger) | S8 discharge note appended (1,478 chars) — 3rd trigger flipped `open → mitigated` |
| `69bd578f-1bec-46fc-8b10-b8810f582b5a` | S8 dispatch 1 (min-scope smoke, 1 iter) — validates instrumentation baseline |
| `2322e963-095c-4bd5-9147-91d91380cab7` | S8 dispatch 2 (weaker prompt, 4 iter) — validates convergence without "MUST" language |
| `ccbf3de6-3b60-4044-a87e-fa35fd559be3` | S8 dispatch 4 (audit-style, 5 iter) — validates exploration → persist path |
| `f3e7dffb-6724-4582-96a9-3541192d98f2` | S8 dispatch 5 (heavy-synthesis 9 iter, S3037 shape) — reproduction attempt (converged; the S3037 failure did NOT reproduce with explicit persistence prompting) |

---

## Wrapper pin note

Active PA conversation pin at S3038 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**S3039 first action:** S7 (ThinkingAgent 67% async failure root-cause). ~1 session estimate. Instrument each ORM call site in `.think()`; look for `SynchronousOnlyOperation` in an async context — likely a missing `sync_to_async` at an ORM boundary.
