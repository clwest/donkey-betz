# Session 2886 — td_handlers_core.py criticality-first error-envelope migration (Slate B pivot)

**Date:** 2026-07-22
**Session pin (retired at close):** `pa-35b93928b15f4a9c` (labeled `s2886-open`; minted at S2885 close per `session_lifecycle close --label s2886-open`)
**Prior pin retired at S2885 close (not this session):** `pa-42342895674d4878`
**Slate label:** S2886 — `td_handlers_core.py` criticality-first (messaging + remember + session, 17 sites) — **first criticality-first slate after S2885-close pivot**
**PRs:** #3396 (`64ea19d1d`) + `<docs cascade>` at close
**Combined regression:** 100/100 pass across S2879 → S2886 + `test_zoom_out_tool_2780` (S2879 14 + S2880 5 + S2881 6 + S2882 12 + S2883 10 + S2884 8 + S2885 13 + **S2886 17** + zoom_out 15)

---

## S2886 open — four stacked infra faults, all legacy `/development/` bleed

S2885 close deferred the `/development/` deletion decision to S2886 open. S2886 opened by discovering that Chris had already removed `/Users/donkeyking/development/unified-donkey-betz/` between sessions — but four stacked infra faults from long-running processes still bound to the deleted path blocked normal work until resolved.

### Root cause: four faults, single origin

1. **Redis MISCONF (RDB write disabled).** `redis-server` (PID 5417, started Thu 2026-05-04) held `cwd=/Users/donkeyking/development/unified-donkey-betz` — a now-unlinked inode (105512755). `config get dir` returned blank; `bgsave` returned `err` immediately. Every write hit MISCONF and celery task enqueue stalled. **Mitigation:** `redis-cli config set stop-writes-on-bgsave-error no` (writes unblocked, RDB persistence still degraded). **Clean fix (deferred to S2886 close):** `pkill redis-server && redis-server --daemonize yes` from `/Donkey_Betz/` cwd.

2. **Celery worker startup fail (`nohup: .venv/bin/celery: No such file or directory`).** `make celery` reported `✓` but nohup silently failed because 157 `.venv/bin/*` scripts had shebangs pointing at `/Users/donkeyking/development/unified-donkey-betz/.venv/bin/python` (nonexistent). **Fix:** bulk `sed -i.bak` rewrite of shebangs to `/Users/donkeyking/Donkey_Betz/unified-donkey-betz/.venv/bin/python`, then `rm .venv/bin/*.bak`, then `make celery`.

3. **Daphne interpreter mismatch (task enqueue KeyError `'core.tasks.process_pa_chat_task'`).** Daphne PID 16615 was running with the Python interpreter binary at `/Users/donkeyking/development/unified-donkey-betz/.venv/bin/python` (the process image was already loaded — the shebang fix from (2) didn't help a running process). Daphne's celery task registry lookup returned KeyError on enqueue. **Fix:** `kill 16615 && make start` from `/Donkey_Betz/`.

4. **Legacy checkout directory removal (already done by Chris between sessions).** Pre-check at S2886 open confirmed `/Users/donkeyking/development/unified-donkey-betz/` no longer exists. Parent `/Users/donkeyking/development/` untouched (51 other projects intact). Redis process still holds phantom cwd fd → deferred restart per (1).

**Verification at S2886 recovery:** direct `curl POST /api/pa/chat/` → HTTP 200 `{"success":true, "task_id": "..."}`. PA dispatch → Rigby SIGN with substantive tool_runs.

**Trigger-count for `/development/` bleed pattern:**
- S2885 (1st): orphan Daphne from `/development/` held `:8000`
- S2886 (2nd/3rd/4th): Redis cwd + Celery shebangs + Daphne interpreter

**Chris D-verdict (S2886 open):** deletion had already happened; parent `/development/` is intentional (character-os, mentorforge, ai-content-studio, and 48 other projects live there).

---

## Shipped

### PR #3396 `64ea19d1d` — S2886 slate (2 files, +510/-17)

- **`core/services/td_handlers_core.py`** (+42/-17) — new local `_handler_error` helper at module top (adopter #6 for the S2879 shape, **meeting Rigby's 6-adopter gate for `td_error.py` extraction**). Migrated 17 sites across 3 handlers (see migration diff table below).
- **`core/tests/test_s2886_core_error_envelope.py`** (NEW, 468 lines) — 17 test rows exercising the full `ToolDispatcher.execute_sync` path via `messaging_tool`, `remember_tool`, and `session_tool`. Reuses S2879 `_assert_migrated_envelope` helper. Uses `TransactionTestCase` for remember + messaging classes (S2885 Fold 1 2nd trigger — real User fixture required for sender/user_id lookup after unauth gate clears).

### Migration diff — 17 sites × 4 codes × 3 handlers × 3 dispatched tools

| Handler | Site | Prior return shape | New `error_code` | Helper | Dispatched tool |
|---|---|---|---|---|---|
| `_handle_messaging` | core.py:3844 | `{'error': 'Authentication required for messaging'}` | `permission_denied` | `_handler_error` | `messaging_tool` |
| `_handle_messaging` | core.py:3849 | `{'error': 'User not found'}` | `not_found` | `_handler_error` | `messaging_tool` |
| `_handle_messaging` | core.py:3875 | `{'error': 'recipient_username is required'}` | `invalid_params` | `_handler_error` | `messaging_tool` (action=`send_message`) |
| `_handle_messaging` | core.py:3877 | `{'error': 'message is required'}` | `invalid_params` | `_handler_error` | `messaging_tool` (action=`send_message`) |
| `_handle_messaging` | core.py:3979 | `{'error': 'thread_id is required'}` | `invalid_params` | `_handler_error` | `messaging_tool` (action=`get_thread`) |
| `_handle_messaging` | core.py:3986 | `{'error': 'Thread not found or access denied'}` | `not_found` (dual-semantic preserved per SIGN F2 — splitting would leak thread existence to non-participants) | `_handler_error` | `messaging_tool` (action=`get_thread`) |
| `_handle_messaging` | core.py:4018 | `{'error': f'Unknown messaging_tool action: {action}. Valid: ...'}` | `unknown_action` | `_handler_error` | `messaging_tool` |
| `_handle_remember` | core.py:2224 | `{'error': 'User context required for memory operations'}` | `permission_denied` | `_handler_error` | `remember_tool` |
| `_handle_remember` | core.py:2230 | `{'error': 'content is required for save action'}` | `invalid_params` | `_handler_error` | `remember_tool` (action=`save`) |
| `_handle_remember` | core.py:2331 | `{'error': 'memory_id required for delete action'}` | `invalid_params` | `_handler_error` | `remember_tool` (action=`delete`) |
| `_handle_remember` | core.py:2345 | `{'error': 'query required for search action'}` | `invalid_params` | `_handler_error` | `remember_tool` (action=`search`) |
| `_handle_remember` | core.py:2365 | `{'error': f'Unknown action: {action}'}` | `unknown_action` | `_handler_error` | `remember_tool` |
| `_handle_session` | core.py:4031 | `{'error': 'No conversation_id provided and no current conversation context.'}` | `invalid_params` | `_handler_error` | `session_tool` (action=`health_check`) |
| `_handle_session` | core.py:4206 | `{'error': 'session_tool.retire requires conversation_id.'}` | `invalid_params` | `_handler_error` | `session_tool` (action=`retire`) |
| `_handle_session` | core.py:4311 | `{'error': 'session_tool.set_active requires conversation_id.'}` | `invalid_params` | `_handler_error` | `session_tool` (action=`set_active`) |
| `_handle_session` | core.py:4347 | `{'error': 'session_tool.seed requires conversation_id.'}` | `invalid_params` | `_handler_error` | `session_tool` (action=`seed`) |
| `_handle_session` | core.py:4389 | `{'error': f'Unknown session_tool action: {action}. Valid: ...'}` | `unknown_action` | `_handler_error` | `session_tool` |

**Post-S2886 handler-file population:** `core.py` 73 → **56** (17 migrated). Remaining sub-population 163 → **146** across 4 files (`core.py=56`, `gateway.py=57`, `railway.py=18`, `codejobs.py=15`).

**Taxonomy tally:** 2× `permission_denied`, 2× `not_found`, 10× `invalid_params`, 3× `unknown_action`. All 17 sites map cleanly to the existing 5-code taxonomy — no `internal_error`, no broad-except, no new codes.

---

## Rigby SIGN cycle (pre-code Q1 criticality map)

Rigby ran 5 `repo_tool.read_file` invocations at HEAD `706cfb2a5` (L3820-4080 messaging, L4080-4391 session, L2130-2390 remember, S2885 handoff full body) to independently verify the 17-site routing map before AGREE. `tool_runs` were substantive per `feedback_verify_rigby_tool_runs_before_trusting_sign`.

**Verdicts:**

- **F1 AGREE** — Slate B lean (messaging + remember + session, 17 sites, core.py) matches Rigby's criticality read. Tool-grounded reasons: hard auth gate at L3843-L3844; hard user lookup at L3847-L3849; hard auth gate at L2223-L2225; hard write via `DirectMessage.create` (L3905-L3933), `UserMemoryContext.create/delete` (L2274-L2286, L2328-L2339), and session_active bulk flip (L4188+).

- **F2 PRESERVE** — L3986 stays single `not_found` branch. Splitting into `not_found` (missing thread) vs `permission_denied` (non-participant access) would be a **behavior change** and create an **enumeration oracle** (leaks whether threads exist to non-participants). Test asserts the dual-semantic message text (`'Thread not found or access denied'` includes `'access denied'` substring) to lock the semantics contract.

- **Q3 zoom-out (2 substantive concerns):**
  - **Concern A: `MESSAGING_SEND_DISABLED` pseudo-code** at L3862 (settings-flag guard on `send_message`) already emits `error_code='MESSAGING_SEND_DISABLED'`. Decision: leave the pseudo-code intact (out of the 5-code taxonomy but structurally compatible with the envelope shape). Not touched in this slate.
  - **Concern B: TransactionTestCase prediction.** Rigby predicted Slate B would re-trigger S2885 Fold 1 because remember + session are true write-paths requiring User fixtures visible to `ToolDispatcher.execute_sync`'s fresh asyncio event loop. **Materialized.** `RememberToolMigratedEnvelopeTests` and `MessagingToolMigratedEnvelopeTests` both use `TransactionTestCase`. **2nd trigger — Playbook amendment candidate at S2887/S2888.**

- **Q4 FOLLOW-ON** — Ledger #13 (`td_error.py` extraction) opens as **S2887 tiny centralization PR**, not folded into this slate. Rationale: Slate B is already carrying "first cut into core.py" risk; keeping extraction separate preserves bisectability. Adopter count now **6/6** (ops + governance + agents + newsletter + content + core) — **extraction gate MET**.

- **Q5 LIFT DEFERRED `rm -rf`** — Chris confirmed at S2886 open that `/Users/donkeyking/development/unified-donkey-betz/` had already been deleted. Rigby's 4-trigger corroboration ratified the pattern; deletion decision retroactively validated.

---

## Folds observed (S2885 fold carries — both at 2nd trigger, Playbook amendment candidates)

### Fold 1 — TransactionTestCase for dispatcher-DB tests (2nd trigger)

**S2885 (1st trigger):** `DeliverableInitiativeLinkMigratedEnvelopeTests` + `ContentToolMigratedEnvelopeTests` required `TransactionTestCase` because `ToolDispatcher.execute_sync` spins up a fresh asyncio event loop — the handler's ORM queries land on a Django connection that doesn't see the test's wrapping transaction. `setUp`-created fixtures (Deliverable, User) invisible under plain `TestCase`.

**S2886 (2nd trigger):** Same pattern re-fires in `RememberToolMigratedEnvelopeTests` + `MessagingToolMigratedEnvelopeTests`. Both require a real User row for sender/user_id lookup after the L2224/L3844 unauth gates clear. Test file docstring captures this inline.

**Playbook amendment candidate:** promote "use `TransactionTestCase` for dispatcher-path handler tests that require DB-visible fixtures" to a formal PLAYBOOK rule (candidate slot: PLAYBOOK-6.10.11 or PLAYBOOK-7.4.5). Ratify at S2887 or S2888 SIGN cycle.

### Fold 2 — Shared-taxonomy branch fortification (2nd trigger)

**S2885 (1st trigger):** L182 + L190 both return `not_found` — test at L190 was false-passing before fortification because "missing Initiative → not_found" reached "missing Deliverable → not_found" branch when fixture visibility regressed. Fortified by asserting `'Initiative' in result['error']`.

**S2886 (2nd trigger):**
- `_handle_remember` L2230/L2331/L2345 all return `invalid_params` — differentiated by `action` field (`save`/`delete`/`search`). `_assert_migrated_envelope` is already action-aware, so this is caught automatically.
- `_handle_messaging` L3849 + L3986 both return `not_found` — differentiated by `action` (any-action-vs-`get_thread`) AND by fortified message body substring assertions (`'User' in error` for L3849; `'Thread' in error` + `'access denied' in error` for L3986).

**Playbook amendment candidate:** promote "when multiple branches within a single handler return the same taxonomy code, always assert either the `action` field or a message-body substring to disambiguate" as an EXTENDS to PLAYBOOK-6.10.9 (fold-authoring evidence admission) or a fresh sibling rule.

---

## Ledger #13 — `td_error.py` extraction arc trigger

**Adopter count trajectory:**
- Post-S2879 (initial ratification): 1 (`td_handlers_ops.py`)
- Post-S2880: 1 (same file)
- Post-S2881: 1 (same file)
- Post-S2882: 1 (same file — permission_denied 5th-code follow-on stayed in ops)
- Post-S2883: 2 (+ `td_handlers_governance.py`)
- Post-S2884: 4 (+ `td_handlers_agents.py`, `td_handlers_newsletter.py`)
- Post-S2885: 5 (+ `td_handlers_content.py`)
- **Post-S2886: 6** (+ `td_handlers_core.py`) — **Rigby's 6-adopter gate MET**

**S2887 first-action (queued):** open the extraction arc as a tiny centralization PR. Move `_handler_error` from 6 file-local copies to a single `core/services/td_error.py` module; update the 6 files' import blocks; verify no test regression (100/100 → 100/100). Expected diff: +30/-90 across 7 files.

---

## Session infra artifacts

### Persistent config change

- `.venv/bin/*` — 157 scripts had shebangs rewritten from `/Users/donkeyking/development/unified-donkey-betz/.venv/bin/python` → `/Users/donkeyking/Donkey_Betz/unified-donkey-betz/.venv/bin/python`. Not tracked in git (venv is `.gitignore`d) but persistent to disk.
- Redis `stop-writes-on-bgsave-error` toggled from `yes` → `no` at runtime (not persisted; will revert on redis-server restart at S2886 close).

### Deferred to S2886 close

- **Redis clean restart** — clears the phantom cwd fd, re-enables normal RDB persistence semantics, and reverts `stop-writes-on-bgsave-error` to default. Chris authorized at mid-session; deferred to end-of-session to avoid mid-slate worker disruption.

### Not shipped as code

- Rigby Tool Gap Ledger entry for the 4-trigger `/development/` bleed pattern to be appended at close (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`).

---

## Twin canonical mirrors (per `feedback_twin_deliverable_at_every_ratification` + `feedback_rigby_writes_workspace_deliverables`)

- **Content mirror:** S2886 slate substrate → workspace `b4503364-2573-4401-9e28-61a739e0ce50` (Donkey Betz), category `initiative_phase_doc`
- **Ratification envelope:** S2886 SIGN F1/F2 AGREE + Q3-Q5 verdicts + Chris D-verdict → workspace `b4503364-2573-4401-9e28-61a739e0ce50`, category `governance`, deliverable_type `ratification_record`

Both authored by Rigby at S2886 close per `feedback_rigby_writes_workspace_deliverables`.

---

## What ships in the docs cascade

- This handoff (`docs/handoffs/SESSION_2886_CORE_CRITICALITY_FIRST_ERROR_ENVELOPE.md`)
- `00-START-NEXT-SESSION.md` refresh — S2887 first-action = `td_error.py` extraction arc
- `tools/pa_local.sh` wrapper pin bump — `pa-35b93928b15f4a9c` → S2887 mint via `session_lifecycle close --label s2887-open`
- `docs/INDEX.md` refresh (auto-generated, `python manage.py build_docs_index`)

---

## Next session (S2887) — extraction arc

**First-action:** Open Rigby SIGN with the extraction plan:
1. New file `core/services/td_error.py` containing the canonical `_handler_error` helper (copy of the shape at S2886).
2. Update 6 adopter files' import blocks: `from core.services.td_error import _handler_error`.
3. Remove 6 file-local `_handler_error` copies (28 lines × 6 files = ~168 lines removed).
4. Verify 100/100 regression suite still passes.
5. Rigby SIGN: any concerns about circular imports, ordering, or naming (e.g., `td_error.py` vs `td_handler_error.py`)?

**Expected diff:** ~30 lines added (new file + 6 imports), ~168 lines removed (6 file-local copies). Net = ~-140 lines. Single PR, single review.

**Playbook amendment cycle (parallel):** promote Fold 1 (TransactionTestCase discipline) + Fold 2 (shared-taxonomy branch fortification) as candidate rules for the next MINOR amendment. Both are at 2nd trigger.
