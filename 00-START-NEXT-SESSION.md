# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-donkeyking-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation; use that if you don't want to remember the env vars. Current pinned conversation: `pa-9b82bcc72e1945ce` (set Session 1176 close, carrying into 1177; prior thread `pa-58c916edf96044cc` retired at health 25/100).

## READ THIS SECOND — PA "CONSUME-1-THEN-HANG" IS USUALLY DISK PRESSURE

Memory: `feedback_pa_hang_from_disk_pressure.md`. If the PA worker processes exactly one task and then goes silent, check `df -h /System/Volumes/Data` + `sysctl vm.swapusage` BEFORE deeper Celery debugging. Single-digit GiB free or swap < 2 GiB free → free disk first. Don't restart Docker — `unified-postgres` lives there.

## READ THIS THIRD (NEW Session 1160) — `git show` IS THE FIRST MOVE FOR MTIME MYSTERIES

If you see a cluster of doc mtimes within minutes of each other and wonder "what generated this?", run `git log --since="<timestamp - 1min>" --until="<timestamp + 1min>"` first. Session 1160's "May 25 09:36 batch" mystery resolved instantly via `git show 9d75f78f` — it was Chris's own Session 1143 PR #2197. Future similar questions should start with the git history before invoking Rigby's ops tools.

## READ THIS FOURTH (NEW Session 1161, broadened Session 1162) — WORKER `sys.modules` CACHE ⇒ RESTART

Two restart triggers, one fix. **(1)** Adding a new `@shared_task` to `core/tasks.py` is invisible to running celery workers until they restart — they cache the registered-task list at process import time. Beat dispatches succeed (picks up new `PeriodicTask` rows via `DatabaseScheduler` polling), but workers reject with `Received unregistered task of type '<dotted>'`. **(2)** More broadly (Session 1162 discovery): even when the `@shared_task` itself is unchanged, any helper module the task body imports is cached in the worker's `sys.modules` after first call. Modifying the imported module's code (e.g., a `Command` class the task calls) does NOT propagate to running workers. Both cases need the same restart. Fix: `pkill -9 -f celery; rm -f .celery*.pid; make celery`. Verify with `.venv/bin/celery -A core inspect registered | grep <task_name>` (case 1) or by dispatching a manual call and checking output (case 2). PR-description anti-pattern to avoid: "no `@shared_task` changes — workers don't need restart" — wrong for case 2.

## SOURCE OF TRUTH

Per Session 1144 PR #2208 (canon rebase) + Session 1146 PR #2216 (Runtime Evidence promotion) + Session 1158 (narratives layer) + Session 1159 (EDITING_GUARDRAILS) + Session 1160 (patents README + PR template):

1. **`docs/PLATFORM_INVENTORY.md`** — runtime/inventory anchor (sole authoritative counts per `DOC_LIFECYCLE §2c`).
2. **`docs/INDEX.md`** — doc corpus index (sole authoritative doc counts).
3. **`docs/PLATFORM_WHAT_IT_IS.md`** — narrative anchor. **NOT** a counts source.
4. **`docs/narratives/`** — 15 subsystem narratives (A–O). Operator-handbook layer.
5. **`docs/narratives/EDITING_GUARDRAILS.md`** — 7-rule editing contract + pre-PR checklist (Session 1160 add).
6. **`docs/patents/README.md`** — 4-workstream + disclosure → narrative cross-link map (Session 1160 add).
7. **`docs/case-studies/`** — historical case studies (Session 1160 added codex-audit + drift-reconciliation table).
8. **`docs/00-START-HERE/DOC_LIFECYCLE.md`** — constitution.
9. **`docs/AUDIT_INDEX.md`** — audit taxonomy.
10. **`docs/24_7_GLOBAL_AI_APP_ATLAS.md`** — strategy anchor.
11. **`docs/UDB_BEHAVIOR_LAYER.md`** — Rigby's voice + display rules + constraints.
12. **`docs/UDB_TRANSLATION_LAYER.md`** — audience contract + no-claims rule.
13. **`docs/specs/`** — engineering specs.
14. **Runtime Evidence (auto-generated)** — the 8 `docs/*_AUDIT.md` files. DOC-AUTOGEN per-subsystem runtime evidence. Regenerate with `build_*_audit` mgmt commands.
15. **Archive / handoff docs** — historical unless promoted by `docs/handoffs/CURRENT.md` or this file.

Live drift checks:
- `python manage.py verify_doc_claims --only-drift`
- `.venv/bin/context-kit doctor` — **expected floor: `10 OK / 2 warnings`**.
- `python scripts/verify_repo_guardrails.py`
- `python manage.py session_provenance --session N`
- `python manage.py build_docs_provenance` — regenerates `docs/_provenance.json`.
- The 8 `build_*_audit` commands — regenerate per-subsystem runtime evidence.

## PRE-COMMIT HOOK BLOCKS DIRECT COMMITS TO MAIN

Always feature-branch + PR. Topical prefix (`docs/`, `feat/`, `fix/`).

## COMMIT-MESSAGE HYGIENE RULE (Session 1144)

Every session-NNNN commit subject should include `session-NNNN`:

- `docs(session-NNNN): ...`
- `fix(session-NNNN): ...`
- `feat(session-NNNN-area): ...`

Sessions 1145–1160 ran 100% subject-tagged. Keep the streak.

## NARRATIVE-EDIT PR CHECKLIST (Session 1160)

`.github/PULL_REQUEST_TEMPLATE.md` includes a conditional "Narrative-edit checklist" that PR authors fill out when the PR modifies any file in `docs/narratives/`. The 7-item checkbox list maps 1:1 to `docs/narratives/EDITING_GUARDRAILS.md` rules. Required only when changes touch narratives.

Authoring rule of thumb: if the PR introduces a new rule/process, dogfood the rule on its own diff before opening. The `#2256 → #2257` loop (PR #2256 introduced EDITING_GUARDRAILS and still violated rules #1 + #5 in 5 places) is the cautionary tale captured both in the EDITING_GUARDRAILS source addendum and the Session 1159+1160 handoffs.

## ONE-COMMAND LAUNCH — the laptop fleet

```bash
cd ~/development/infra
make up                  # 7 Docker fleet apps on fleet-net
make all                 # up + u-d-b natively (daphne + celery)
make status              # what's running + URLs
```

Tested Session 1159 post-Mac-reboot: full stack restart from cold-boot in ~30 s. Clear stale pids first (`rm -f .celery*.pid .daphne.pid`) before `make all`.

## CANONICAL PA / WORKSPACE NOTES

- `POST /api/pa/chat/` is the canonical Rigby endpoint.
- **PA tool registration needs BOTH daphne AND celery restart.** `pkill -9 -f celery; rm -f .celery*.pid; make celery`.
- **search_docs originating_session filter cache:** `lru_cache(1)` per process. After `build_docs_provenance` regen, restart workers.
- **`process_pa_chat_task` uses `acks_late=False`** (Session 1159 PR #2255). Overrides the global `CELERY_TASK_ACKS_LATE=True` because the global setting + unstable macOS broker conn was producing tasks stuck in `unacked` for an hour.

---

## SESSION 1181 — CURRENT ENTRY POINT

### FIRST THING this session

**Session 1180 closed Pass B with 3 structural fixes merged + 6 cells closed.** PRs #2350/#2351/#2352 are live on main. The agent follow-up wake loop now has the architectural contract "lifecycle-bound, not connection/runtime-bound" enforced top-to-bottom. Two Phase 3 PRs + 1 separate finding queued (none blocking).

**Pinned conversation:** `pa-a5fecc400c0f4152` is still active and healthy. Used heavily Session 1180 (~15 Rigby tool calls). Run `session_tool health_check` early Session 1181 to see if rotation is due.

Close handoff: [`docs/handoffs/SESSION_1180_PASS_B_EXECUTION.md`](docs/handoffs/SESSION_1180_PASS_B_EXECUTION.md). Prior: [`docs/handoffs/SESSION_1179_PASS_B_MATRIX_DRAFTED.md`](docs/handoffs/SESSION_1179_PASS_B_MATRIX_DRAFTED.md), [`docs/handoffs/SESSION_1178_AGENT_AUTO_WAKE_PHASE2.md`](docs/handoffs/SESSION_1178_AGENT_AUTO_WAKE_PHASE2.md).

Standard FIRST THING checks:
1. Disk: `df -h /System/Volumes/Data`. Swap: `sysctl vm.swapusage`.
2. Through Rigby (canon: `tools/pa_local.sh`, pinned conv `pa-a5fecc400c0f4152`): `platform_config_tool overview` → confirm `service_context: local`.
3. `session_tool health_check` on `pa-a5fecc400c0f4152` — rotate if past 60/100.
4. Spot-check Session 1180 24h watch (see handoff §"24h watch checklist"):
   - Tail `celery-long-running.log | grep '\[auto_followup\]'` — `created` lines fire, `fail-open` absent
   - `SELECT COUNT(*) FROM core_agentfollowupsubscription WHERE state='armed' AND expires_at IS NULL AND created_at < NOW() - INTERVAL '6 hours'` — should be 0 (or <10)

### PRIORITY 1 — Phase 3 PRs from Pass B (pick by ROI)

The 3 fixes shipped Session 1180 closed the structural defects. Three follow-ups remain — all are UX/extender work, none block correctness. Order by ROI / Chris preference:

| PR | Scope | Effort | Why pick |
|---|---|---|---|
| **PR5** — populate `artifact_pointers` in fire helper | Extract `media_ids`/`deliverable_ids` from `execution_record.output_data` per-agent (`ImageAgent → output_data.metadata.images`, etc) + bubble click-through render | ~30 min backend + small frontend | Closes Cell 8 FAIL. Without it, image/media agent completions appear in bubbles with no link to the actual artifact — visible regression for users. |
| **PR4** — banner queue / toast stack for multi-agent fanout | `paStore.ts:350-356` — replace single `recentAgentCompletion` slot with a queue; head fades over ~6s, then next item shows | ~20 min frontend | Closes Cell 7 visual finding. Bubbles already persist correctly (Cell 7 PASS); this is purely live-banner UX. |
| **Finding #4** — threaded-worker SIGTERM revoke can't kill Python threads | `long_running` queue is `--pool=threads --concurrency=2`. Options: switch to `--pool=prefork` (test-impact analysis required), document the limitation, OR add a workaround `cancel_agent_execution` PA tool that updates DB + fires helper directly | ~variable depending on path chosen | Real-world cancel reliability concern. PA Cancel buttons are best-effort on this queue. |

Rigby's lean Session 1180 close: PR5 first (most user-visible), PR4 second (1 file frontend), Finding #4 third (needs scope discussion before implementation).

### PRIORITY 2 — Optional UX hardening (was deferred / now optional thanks to PR #2352)

These were originally planned as Pass B remediation PRs but became optional once PR #2352 made persistence execution-lifecycle-dependent:

| Item | Status | Justification |
|---|---|---|
| `GET /api/pa/conversations/<id>/completions?since=<ts>` replay endpoint | Optional | Original Cell 4 fix scope. Now optional because server-side persistence guarantees the row exists on history re-fetch. Would still improve "banner replay" UX. |
| WS connection-state UI per conversation | Optional | Original Cell 5 Run 2 finding. Now optional because missing-live-banner is recoverable from history. Would still help users understand when they'll miss the live notification. |
| JSON-expression partial unique index on `chat_conversations((metadata->>'execution_id'), conversation_id) WHERE metadata->>'kind'='agent_completion'` | Hardening | App-level idempotency from PR #2350 is the v1 path. DB-level constraint would belt-and-suspender. Deferred per Rigby ratification because of JSON expression-index portability concerns. |

### Carryover (still riding from Sessions 1171-1178)

PgBouncer follow-up verifications, narrative dedup, agent-name dim checks, retry-policy bulk migrations, `pg_stat_statements` on staging/prod, `capture_pa_acks_health_snapshot` slow-task investigation, COO consolidation deferreds. Plus Session 1178 deferred items: `auto_followup_skipped` traceability stamp, EditorAgent observability dashboard (C3 from #2343). Live handoffs: `docs/handoffs/SESSION_1171_*` through `SESSION_1180_*`.

---

## SESSION 1180 CLOSED — Pass B live execution + 3 structural fixes (2026-06-20)

**3 PRs merged.** Full handoff: [`docs/handoffs/SESSION_1180_PASS_B_EXECUTION.md`](docs/handoffs/SESSION_1180_PASS_B_EXECUTION.md).

| PR | Theme | SHA |
|---|---|---|
| **#2350** | `feat(session-1180-agent-wake)` — completion-bound auto-followup (`expires_at` nullable) + idempotent completion rows | `920cae05` |
| **#2351** | `fix(session-1180-agent-wake)` — cancel terminal must fire followup subscriptions | `cc3acef9` |
| **#2352** | `fix(session-1180-agent-wake)` — server-side completion-row persistence (decouple from WS consumer) | `a6659096` |

**Pass B matrix results (all 6 cells closed):**

| Cell | Theme | Result |
|---|---|---|
| **5** | Second-tab dedupe | PASS-with-caveat (TTL race fix verified; 2-consumer dedupe not reproducible from SPA UI) |
| **3** | Revoke/cancel terminal | FAIL → fixed (PR #2351) |
| **4** | Refresh-mid-run + WS reconnect | FAIL → fixed (PR #2352, subsumes planned replay endpoint) |
| **7** | Multi-agent fanout | PASS (banner-overwrite frontend finding queued as PR4) |
| **8** | Media-artifact agent | FAIL → queued (PR5) |
| **6** | Tab-not-focused | PASS-by-reference (PR #2352 architectural guarantee) |

**Behavioral invariants now load-bearing post-Session 1180:**
1. Auto-wake subs are execution-lifecycle-bound (`expires_at=NULL`); fire on terminal regardless of runtime
2. Explicit `schedule_followup(after_seconds=N)` keeps time-bounded delayed-reminder semantic
3. Completion row persistence is execution-lifecycle-dependent (server-side write in fire helper); consumer-side write is idempotent safety net
4. Cancel terminal fires the followup like every other terminal (`agent_router.py:1597`)
5. Idempotency per `(conversation_id, execution_id)` for completion rows (app-level)
6. Fire helper fail-open both directions (persist failure → still broadcast; broadcast failure → still persisted)

**Evidence log:** deliverable `ffa23f86-91bd-4a5f-8797-7c649643ad57` (grew 0 → ~10 KB across 7 appends).
**Source matrix:** deliverable `61247479-1976-4ba8-bc8a-ea67f66ead45`.

---

## SESSION 1179 CLOSED — Pass B matrix Cells 3-8 drafted in deliverable 61247479 (2026-06-20)

**0 PRs.** Full handoff: [`docs/handoffs/SESSION_1179_PASS_B_MATRIX_DRAFTED.md`](docs/handoffs/SESSION_1179_PASS_B_MATRIX_DRAFTED.md).

| Cell | Theme | Predicted finding (code:line) |
|---|---|---|
| **3** | Revoke/cancel terminal | `agent_router.py:1584-1597` — cancel path doesn't call `fire_agent_followup_subscriptions` (5 sites in `tasks_agents.py` do) |
| **4** | Refresh-mid-run + WS reconnect | Banner missed; no "fetch missed since" replay. Bubble persists via `/api/pa/conversations/<id>/` re-fetch |
| **5** | Second-tab dedupe | `consumers_pa_conversation.py:103-139` — `create_completion_row` is plain `.create()`, two consumers = two rows |
| **6** | Tab-not-focused | Persistence proof, no defect predicted |
| **7** | Multi-agent fanout (2→3) | `paStore.ts:350-356` — `recentAgentCompletion` single state slot, no banner queue |
| **8** | Media-artifact agent | `tasks_agents.py:133` — `artifact_pointers={}` hardcoded since PR-2a; never wired up |

Five of six cells have specific file:line code-walk references predicting their fail signature. Session 1180 = live execution + PASS/FAIL evidence collection (~1 hour, ~10 min/cell). Each predicted FAIL becomes a focused Phase 3 PR.

**Deliverable `61247479-1976-4ba8-bc8a-ea67f66ead45` grew from 13,171 → 33,138 chars across 7 `deliverable_tool append` calls (6 cells + Rigby's auto-summary footer).** `feedback_deliverable_tool_use_append_for_large_payloads` reaffirmed — `update` would have rejected at least Cells 4-8.

**Conversations:** `pa-9b82bcc72e1945ce` retired at 60/100 (~30 turns, ~15k tokens, 10 topics — `suggest_fresh` per `session_tool health_check`). Successor `pa-a5fecc400c0f4152` ("Session 1180 — Pass B matrix execution + evidence") created; `tools/pa_local.sh` updated.

---

## SESSION 1178 CLOSED — Phase 2 auto-wake LIVE + conv-ID recon closed + TTL hotfix shipped (2026-06-20)

**4 PRs merged.** Full handoff: [`docs/handoffs/SESSION_1178_AGENT_AUTO_WAKE_PHASE2.md`](docs/handoffs/SESSION_1178_AGENT_AUTO_WAKE_PHASE2.md).

| PR | Theme | SHA |
|---|---|---|
| **#2345** | `feat(session-1178-agent-wake)` — Phase 2 auto-wake (implicit follow-up subscription + per-call opt-out) | `9c5c944b` |
| **#2347** | `fix(session-1178-agent-wake)` — TTL bump 30s→60s + shared model constants (caught by live verify) | `039435fe` |
| **#2348** | `test(session-1178-agent-wake)` — cross-path invariant test (Phase 1 + 2 can't drift again) | `3185beb7` |
| **#2346** | `docs(session-1178)` — close handoff + 00-START-NEXT-SESSION.md reset | (this PR) |

**Source-only, no migrations.** Every PA-originated agent dispatch now auto-creates an armed `AgentFollowupSubscription` at `execute_agent_task` entry (60s TTL — bumped from 30s after live verify caught a 2-second race against ResearchAgent runtime). Rigby no longer has to call `schedule_followup` explicitly — the user gets the completion banner + Rigby-authored chat bubble by default. The explicit tool remains as an override (custom TTL up to `MAX_TTL_SECONDS = 600`).

**Dedupe is DB-guaranteed** via existing `unique_together = [('execution', 'conversation_id')]` on `AgentFollowupSubscription`. `get_or_create` is race-safe with explicit `schedule_followup` for free.

**Single source of truth for TTL contract** (post-PR-#2347 + #2348): `AgentFollowupSubscription.DEFAULT_TTL_SECONDS` (60) + `MAX_TTL_SECONDS` (600). Both Phase 1 explicit + Phase 2 implicit read from there. New CI test `test_default_after_seconds_matches_model_constant` fails if drift recurs.

**Ratified design card (Rigby sign-off Session 1178, with D2 overruled by reality):** D1=augment / **D2=60s default** (was 30s in original ratification) / D3=PA-only via conv_id NULL gate / D4=per-call opt-out (`auto_followup: false`) / D5=one banner per agent / D6=at `execute_agent_task` entry.

**Conv-ID divergence recon (Session 1175 open follow-up #1):** Closed as "wrapper hygiene, not a bug." Code walk through `process_pa_chat_task → UnifiedPAEntrypoint → run_agent → execute_agent_task → AgentFollowupSubscription` proved conv_id is invariant within a turn.

**Live verify trail (post-merge to main):**
- Execution `d7fc8c50` (pre-hotfix, TTL=30s) — caught the bug: sub expired 2s before completion, silent no-op.
- Execution `2b1892c1`, sub `92c8eed2` (post-hotfix, TTL=60s) — sub created 23:26:55, fired 23:27:25, ChatConversation row 588 persisted. Zero explicit `schedule_followup` calls.
- Execution `06f63afe` (opt-out path) — `auto_followup=false` flowed through PA schema → `_CONTEXT_PROMOTE_KEYS` → context. Zero subscriptions created. Silent skip.

**Carry-forward for Session 1179:** none required. Phase 2 is live and verified. Pick next thread per the priority list above.

**Conversations:** `pa-9b82bcc72e1945ce` healthy at close (85/100 in mid-session). Six exchanges across the session.

---

## SESSION 1177 CLOSED — Agent dispatch defense (F1 + F3 root causes closed) (2026-06-20)

**3 PRs merged.** Full handoff: [`docs/handoffs/SESSION_1177_AGENT_DISPATCH_DEFENSE.md`](docs/handoffs/SESSION_1177_AGENT_DISPATCH_DEFENSE.md).

| PR | Theme | SHA |
|---|---|---|
| **#2341** | `docs(session-1176)` — close handoff (carried over) | `fba55cc5` |
| **#2342** | `fix(session-1177)` — F1 root cause: surface LLM tool-call args parse failure as typed error | `e9967bc8` |
| **#2343** | `fix(session-1177)` — F3 root cause: EditorAgent dispatcher `content_provenance` + opt-in `strict_content_required` | `75993feb` |

**Item A (failed-banner visual) verified end-to-end:** manual-mutation pattern (Django shell `.update()` on a completed execution → set status=failed → schedule_followup → watch browser). First attempt → no banner because WS hadn't connected to the new conversation `pa-9b82bcc72e1945ce` yet. After `Cmd+Shift+R` → banner + chat bubble rendered correctly with status=failed and error message. **F4** (UI filters failed) and **F4b** (immediate-fire path lacks persistence) both falsified — both branches of the Session 1175 wake feature handle failure correctly.

**Scope B' (per-handler arg validation) investigated and skipped:** `_resolve_deliverable` at `td_handlers_agents.py:1644` and per-action `ValueError` raises already defend `deliverable_tool.update`/`create`/`append`/`detail`/`delete`/`export_pdf`. The only silent-fallback path that existed was the JSON parse swallow PR #2342 closed.

**Carry-forward diagnostic:** WS broadcasts to empty groups vanish silently — by design in Channels. If "where's the banner?" comes up again, first check WS connection state on the right conversation before deeper bisect.

**Conversations:** `pa-9b82bcc72e1945ce` still healthy at close — Session 1178 should reuse it unless Rigby flags otherwise.

---

## SESSION 1176 CLOSED — Agent dispatch + follow-up wake stress-test recon (2026-06-20)

**3 findings filed, 2 cells of the Pass B matrix verified end-to-end.** Full handoff: [`docs/handoffs/SESSION_1176_AGENT_DISPATCH_RECON_CLOSE.md`](docs/handoffs/SESSION_1176_AGENT_DISPATCH_RECON_CLOSE.md). Tracking deliverable: `61247479-1976-4ba8-bc8a-ea67f66ead45` (Local QA workspace, 10017 chars).

| What | Evidence |
|---|---|
| **Success path verified end-to-end** (backend → WS → AgentCompletionBanner) | 3 banner sightings in browser. Executions: `2935f7bb` (ResearchAgent), `660f9234` (EditorAgent unexpected success). |
| **Failed branch verified at backend** | `6e9e42ad` (EditorAgent failed 3.6s) → schedule_followup returned `mode=delivered_immediately, state=fired`. Visual deferred (F3). |
| **PR-1 conv_id gate verified working** | Non-PA execution `5c103be3` (ContentWriterAgent watchdog timeout) cleanly rejected: "Cannot subscribe: ... conversation_id is NULL." |

**Findings filed in deliverable:**
- **F1** — `deliverable_tool update` silent fallback to `action=list` above ~6-7kB content. Workaround: `append`. Bisect needed.
- **F2** — Non-PA-originated executions can't surface via follow-up (PR-1 gate, by-design coverage gap before any "Rigby will tell me when things break" user-facing claim).
- **F3** — EditorAgent non-deterministic on empty content. Same input, two runs: fail-loud (3.6s, correct) vs generation-fallback (17.7s, masks caller bugs). Exactly the failure mode `feedback_editor_fail_loud` memory warned about.

**Session-structure notes worth carrying:**
- `feedback_rigby_deliverable_content` pattern (Claude writes Cell 1, Rigby extends one-at-a-time with `update + detail` verify) worked cleanly for the matrix scaffold.
- `feedback_rigby_tool_verification` validated: Rigby's initial claim "`deliverable_tool update` is broken" was wrong (small-payload SCRATCH test proved otherwise) — the real bug is F1's size threshold.
- When Rigby is asked for "a deterministic failure," be specific about the mechanism in the prompt — left open, she once dispatched a success-path task by mistake.

**Conversations:** `pa-58c916edf96044cc` retired at health 25/100 (43 turns, ~21.5k tokens, 9 topics). Successor `pa-9b82bcc72e1945ce` ("Session 1177 — TBD") created via `session_tool create_fresh`; `tools/pa_local.sh` updated to pin it.

---

## SESSION 1169 CLOSED — Carryover queue close (B-C-E-A-D-1 stretch path, 2026-06-20)

**5 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1169_CARRYOVER_QUEUE_CLOSE.md`](docs/handoffs/SESSION_1169_CARRYOVER_QUEUE_CLOSE.md).

| PR | Theme | SHA |
|---|---|---|
| **#2316** | `feat` — **Item 2:** idempotent enforce-disabled for denylisted PeriodicTask rows on local | `d421d1de` |
| **#2317** | `fix` — **Item 3:** symmetric attach-aware lookup for id-based deliverable mutations (detail/save/unsave/append/delete/export_pdf) | `93e4e436` |
| **#2318** | `feat` — **Item F:** `agent_name` dim on `CeleryTaskEvent` + `top_consumers(group_by='agent')` | `1bc96909` |
| **#2319** | `fix` — **Item D:** decorator-side timeouts on `monitor_celery_health` + probe-decomposition operator note | `362960db` |
| **#2320** | `feat` — **Item 1:** `DeliverableGatedError` + `raise_on_gated` kwarg (Layer C Phase 1) | `a71b5a3e` |

**Session 1168 + 1167 carryover queue state after Session 1169:** all 5 items closed. Layer C completion (Phase 2 + Phase 3) and `capture_pa_acks_health_snapshot` probe decomposition queued as Session 1170 Priority 1 + 2.

**End-to-end verified post-merge:**
- PR #2316: live `add_critical_celery_tasks --dry-run` then real-run on a re-enabled denylist row — dry-run reported "Would disable 1", real run reported "Disabled 1" + DB confirmed `enabled=False`.
- PR #2317: 9 new tests + 8 regression pass; covers detail/save/unsave/append/delete for non-staff users + security regression (non-staff cannot touch other users' orphans).
- PR #2318: migration applied cleanly; live PA dispatch verified `group_by='agent'` returns populated `consumers` with `agent_name` keys (Session 1169 close).
- PR #2319: 4 new decorator-pin tests pass; `monitor_celery_health.queue == 'broadcast'`, `soft_time_limit == 60`, `time_limit == 90` verified.
- PR #2320: live PA `deliverable_tool.create(title='Smoke test from Session 1169 verification', content='anything short')` returned `reason_code='gate_2_smoke_pattern'` (NOT generic `'unknown_gate'`) — Layer C Phase 1's actual value visible end-to-end.

**New persistent artifacts:**
- `core/services/deliverable_factory.py:DeliverableGatedError` (typed exception class with `reason` / `reason_code` / `title` / `agent_name`)
- `core/services/deliverable_factory.py:_should_create_deliverable` (now returns 3-tuple including `reason_code`)
- `core/services/td_handlers_agents.py:_id_lookup_qs` (closure used across 7 id-based actions)
- `core/management/commands/add_critical_celery_tasks.py:_enforce_disabled_local` (new helper)
- `core/management/commands/add_critical_celery_tasks.py:_effective_local_deny_set` (extracted shared helper between filter + enforce)
- `core/models_celery_telemetry.py:CeleryTaskEvent.agent_name` (indexed CharField)
- `core/migrations/0355_session_1169_celerytaskevent_agent_name.py` (surgical migration)
- `core/celery_telemetry.py:_extract_agent_name` (4-key fallback helper)
- `core/services/top_consumers.py:compute_top_consumers(group_by=...)` (now accepts 'task' or 'agent')
- 5 new test files: `test_enforce_disabled_local.py` / `test_deliverable_orphan_mutations_symmetric.py` / `test_celery_telemetry_agent_extract.py` / `test_monitor_celery_health_timeouts.py` / `test_deliverable_factory_gated_exception.py`
- `docs/topics/celery-workers.md` — 3 new subsections (Wall-clock telemetry / Decorator-side timeouts / Agent dimension)
- `docs/handoffs/SESSION_1169_CARRYOVER_QUEUE_CLOSE.md`
- Tracking deliverable `b58b20b3` on chris-personal: schema-drift reconciliation backlog (Cluster A Narrative subsystem + Cluster B `CuratedSignalEntry.action_status` + Cluster C cosmetic AlterFields)

**Patterns captured in handoff "Session-level patterns worth noting":**
- `makemigrations` bundles every drift it sees — quarantine surgical migrations
- Decorator-side options matter even when beat options look right
- Timeouts alone don't bound monitor tasks that block in C-level calls
- Phased migrations beat single-PR sweeps when caller count is high

---

## SESSION 1168 CLOSED — chris-personal SHIP arc + B-C-E-A ops visibility (2026-06-20)

**5 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1168_BUGS_AND_OPS_VISIBILITY.md`](docs/handoffs/SESSION_1168_BUGS_AND_OPS_VISIBILITY.md).

| PR | Theme | SHA |
|---|---|---|
| **#2310** | `fix` — **Bug #1:** harden `deliverable_tool.create` against silent factory `None` gate-reject + pass `trigger_source=pa_tool` | `94b034b2` |
| **#2311** | `fix` — **Bug #2:** allow orphan deliverables to be attached to a workspace via `deliverable_tool.update` | `1e492404` |
| **#2312** | `feat` — **B + C:** `memory_pressure` rollup on `ops_tool.overview` + `cap_coverage_pct` on `ops_tool.memory_pressure` | `95822679` |
| **#2313** | `docs` — **E:** operator playbook snippet — monitor tasks in `top_consumers` = P1 reliability debt | `711f4e40` |
| **#2314** | `feat` — **A:** local-safe Celery beat schedule (chris-personal SHIP `7c332f0d`) | `bf84e415` |

**chris-personal Known Bugs Queue state after Session 1168:** all 3 SHIP items closed (Bug #1 + Bug #2 + Local-safe Beat).

**Post-merge one-time toggle (manual, not in any PR):** 5 already-enabled denylisted `PeriodicTask` rows on chris-personal local DB toggled `enabled=False` (the 6th, `scan-income-spider-orchestrator`, was already off). Rigby authorized as a safe-toggle (not a delete) — reversible via `update(enabled=True)`.

**End-to-end verified post-merge:**
- PR #2310: live PA smoke on both `deliverable_tool.create` and `content_tool.deliverable_create` — short content → ok=true with real id (Layer B working); smoke-test titles → structured `deliverable_gated` dict, no crash (Layer A working).
- PR #2311: live PA `deliverable_tool.update(id='810cc75c-...', workspace_id='33aa1e08-...')` against orphan — ok=true, `updated_fields: [tags, workspace]`; follow-up detail confirms `is_orphan: false`. Definitive attach test passed.
- PR #2312: 8 new tests + 4 regression all green.
- PR #2313: docs only — re-indexed via `build_docs_index`.
- PR #2314: live dry-run smoke confirmed the 6 prod-noise tasks under "Local-safe mode: skipped"; post-merge DB toggle verified all 6 rows `enabled=False`.

**New persistent artifacts:**
- `core/tests/test_deliverable_create_gated.py` (Bug #1 — 4 tests)
- `core/tests/test_deliverable_update_orphan_attach.py` (Bug #2 — 4 tests)
- `core/tests/test_ops_memory_pressure_rollup.py` (B + C — 8 tests)
- `core/tests/test_local_safe_beat_filter.py` (A — 11 tests)
- `core/services/td_handlers_ops.py:_ops_memory_pressure_rollup` (new helper)
- `core/management/commands/add_critical_celery_tasks.py:LOCAL_DENY_TASKS` + `_filter_local_safe` (new env-gated layer)
- `docs/topics/celery-workers.md` — new "Wall-clock telemetry" subsection + operator playbook snippet
- `docs/handoffs/SESSION_1168_BUGS_AND_OPS_VISIBILITY.md`

**New gotchas captured (queued for memory):**
- `payload.<field>` as both filter AND value = always a bug (Bug #2 pattern)
- Silent `None` return from a factory pre-disposes every caller to a `NoneType.X` crash (Bug #1 pattern)
- `make status` shows correct PIDs even when first health-probe path is wrong — `/admin/` HTTP 302 is the right liveness check, not `/api/health/`

---

## SESSION 1167 CLOSED — COO #5 + #7 close (2026-06-19)

**3 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1167_COO_BACKLOG_5_AND_7_CLOSE.md`](docs/handoffs/SESSION_1167_COO_BACKLOG_5_AND_7_CLOSE.md).

| PR | Theme | SHA |
|---|---|---|
| **#2304** | `docs` — fix 00-START FIRST THING date suffix to UTC (caught false-positive on session entry) | `4e9e08af` |
| **#2305** | **COO #5 (SHOULD):** worker memory telemetry + soft downshift signal — `core/services/memory_telemetry.py` + JSONL-as-state at `logs/worker_memory/` + `ops_tool.memory_pressure` + 40 tests | `d7f27218` |
| **#2306** | **COO #7 (SHOULD):** top wall-clock consumers ops endpoint — `core/services/top_consumers.py` with server-side `percentile_cont(0.95)` + `ops_tool.top_consumers` + 18 tests | `cc838c4e` |

**COO Backlog state after Session 1167:**

| Item | Tier | Closed in |
|---|---|---|
| #1 DB safety defaults | MUST | Session 1165 (#2295) |
| #2 Per-process Postgres `application_name` tagging | MUST | Session 1166 (#2301) |
| #3 Singleton locks + jitter | MUST | Session 1165 (#2296) |
| #5 Memory telemetry + automatic downshift | SHOULD | **Session 1167 (#2305)** |
| #6 Retry-storm prevention | MUST | Session 1165 (#2297) |
| #7 Top Consumers ops endpoint | SHOULD | **Session 1167 (#2306)** |
| #8 Queue depth + backlog age per queue | SHOULD | Session 1164 |

**All 4 MUSTs + all 3 SHOULDs from Rigby's June 14 corrected v1 closed. Backlog is complete.**

**End-to-end verified post-merge:**
- PR #2304: all 4 `date -u +%Y-%m-%d` occurrences land on the UTC-dated JSONL the cadence writer creates.
- PR #2305: first JSONL line written at `2026-06-20T02:05:02 UTC` with `schema_version=1` + `cadence_seconds=300` + `sustain_gating` block; 4 local workers sampled with correct `pool_kind` classification.
- PR #2306: PA-dispatch test of `ops_tool.top_consumers` returned populated schema-v1 payloads for `window=1h, limit=5` and `window=24h, limit=10` end-to-end through the PA path. Live smoke surfaced `capture_pa_acks_health_snapshot` at p95=1880s and `monitor_celery_health` at p95=1048s as top long-tail offenders.

**New persistent artifacts:**
- `core/services/memory_telemetry.py` (canonical sampler + sustain semantics)
- `core/services/top_consumers.py` (PG aggregator with server-side p95)
- `core/management/commands/worker_memory_health.py`
- `core.tasks.capture_worker_memory_snapshot` (`@singleton_task` cadence, broadcast queue)
- Beat schedule entry `worker-memory-capture` every 5 min
- `ops_tool.memory_pressure` + `ops_tool.top_consumers` actions
- `logs/worker_memory/YYYY-MM-DD.jsonl` UTC-dated rotation
- `docs/topics/celery-workers.md` — new "Memory telemetry" subsection
- 5 new test files, 58 tests total

**New gotchas captured:** none — both designs followed established Session 1164/1165/1166 patterns. The 00-START playbook UTC-vs-local nit was a one-off paper cut, fixed in #2304 with explanatory NOTE block.

---

## SESSION 1166 CLOSED — COO #2 + pa_acks_health item C (2026-06-19)

### FIRST THING (preserved for reference — Session 1167 sanity checks supersede this)

**Verify the Session 1166 PRs are still healthy on main + workers are running the new code.** Run `platform_config_tool overview` through Rigby; confirm `service_context: local`. PA conversation pinned in `tools/pa_local.sh`: `pa-f93d77e34f5d`.

**Disk check:** `df -h /System/Volumes/Data`. If < 10 GiB free, run cleanup playbook from `feedback_pa_hang_from_disk_pressure.md`.

**Session 1166 post-merge sanity check** — verify the two PRs are loaded + active:

```bash
# (1) PG_APPLICATION_NAME tagging is live — ≥80% of connections under dbz:* tags
.venv/bin/python manage.py dbshell -- -c "
SELECT application_name, count(*) FROM pg_stat_activity
WHERE datname='unified_donkey_betz' GROUP BY 1 ORDER BY 2 DESC;"
# Expect: dbz:web (daphne), dbz:celery-pa, dbz:celery-broadcast,
# dbz:celery-long-running, dbz:celery-worker, dbz:celery-beat dominate.
# A handful of unified_donkey_betz rows is fine (ad-hoc shells).

# (2) item C escalated_triggers field on every new JSONL line
tail -3 logs/pa_acks_health/$(date -u +%Y-%m-%d).jsonl | .venv/bin/python -c "
import json, sys
for i, line in enumerate(sys.stdin, start=1):
    d = json.loads(line)
    sg = d.get('sustain_gating', {})
    has_new = 'escalated_triggers' in sg
    print(f'  line {i}: status={d.get(\"status\")} has_escalated_triggers={has_new}')"
# Expect: every line has_escalated_triggers=True. If False, workers
# need restart: pkill -9 -f celery; rm -f .celery*.pid; make celery.

# (3) Procfile coverage verifier still passes
.venv/bin/python scripts/verify_repo_guardrails.py --inventory-advisory 2>&1 | grep -A 1 "Procfile PG_APPLICATION_NAME"
# Expect: "OK: every Procfile entry sets PG_APPLICATION_NAME=dbz:<role>."

# (4) Look for any warn_persist:* escalations in the past 24h
grep -o '"escalated_triggers":\[[^]]*\]' logs/pa_acks_health/$(date -u +%Y-%m-%d).jsonl | sort | uniq -c | sort -rn
# Expect: bulk under "escalated_triggers":[]. Any non-empty list is a
# real CRIT escalation worth investigating per the Session 1166 handoff.
# NOTE: the cadence task names files in UTC (core/tasks.py:12741 uses
# Django timezone.now().strftime — Django runs USE_TZ=True so this is
# UTC). Use `date -u` to match the writer; `date` alone returns local
# and points at yesterday's file during evening hours west of UTC.
```

If anything is missing → `pkill -9 -f celery; rm -f .celery*.pid; make celery`. Then re-run.

### (Session 1166-era priorities — superseded; preserved for context)

### PRIORITY 1 — COO Nervous System Backlog item #5 (Memory telemetry + automatic downshift)

**Source deliverable:** `1be2cf55-2ece-4ffa-8c2b-27b777ee54c7` ("Rigby: COO Nervous System Stabilization — 10-Item Implementation Backlog + Claude Code Session Order (Corrected v1)", workspace chris-personal). With Session 1166 closing #2, **all four MUSTs from Rigby's June 14 corrected v1 are now closed**. Item #5 is the highest-tier SHOULD remaining.

**Item #5 (Rigby's wording, deliverable §5):**
> SHOULD — Memory telemetry + automatic downshift
> Procfile caps memory per child (`--max-memory-per-child=150000`/etc.) — but we have NO visibility into how close we get to those caps before the kill fires. And no automatic concurrency downshift when a worker pool is consistently pressing the cap.
> Likely files: `core/celery.py`, `core/services/td_handlers_ops.py` (new ops surface), possibly a new `core/services/memory_telemetry.py`.
> Acceptance criteria: ops surface shows per-worker RSS + % of cap; sustained > 80% triggers a soft downshift signal (Procfile `--concurrency` not auto-edited, but a flag surfaces).

**Pre-implementation design needs Rigby pass first.** Three open questions:
1. **Where does memory telemetry live?** Celery `worker_init` + periodic `psutil.Process(...).memory_info()` sample → JSONL like pa_acks_health? Or extend the existing `cockpit_tool.queue_lengths`-style ops surface?
2. **What's the downshift signal surface?** A new `ops_tool.memory_pressure` rollup? A field on existing `ops_tool.overview`? PA tool action?
3. **Is the throttle "soft" (flag only) or "hard" (kill-and-restart-with-lower-concurrency)?** Per Rigby's spec the cap is the kill — this is observation + signal, not an auto-modifier.

Route all three through Rigby before code. Don't ship #5 + #7 in the same PR.

### PRIORITY 2 — COO Nervous System Backlog item #7 (Top Consumers ops endpoint)

**Item #7 (Rigby's wording, deliverable §7):**
> SHOULD — Top Consumers ops endpoint
> No quick way to find "which task is using the most DB connections / CPU / wall-time in the last 1h / 24h."
> Likely files: `core/services/td_handlers_ops.py`, possibly `core/services/cockpit_tool.py` if it folds in.

Naturally pairs with the queue_pressure surface Session 1164 added — could fold into a single ops snapshot (`ops_tool.overview` extension via reduce-from-cockpit pattern) rather than a separate gateway. **Per Session 1164 lesson: reduce, never re-classify, when consuming a sibling surface.**

Pre-implementation Rigby ask: separate `ops_tool.top_consumers` action OR roll into `ops_tool.overview`? My lean (un-ratified): separate action, because the "overview" surface is already getting busy and `top_consumers` is a list-rather-than-rollup shape that won't fit cleanly under reduce-and-summarize.

### Active items carrying forward (priority-of-attention)

#### Consolidation / deferred from Session 1165 (focused follow-on PRs)

- **Operator_edge lock consolidation** (`core/tasks_content.py:4216` + 6 release sites). Migrate the third ad-hoc `cache.add()` site to the canonical `singleton_lock` primitive from PR #2296.
- **`_circuit_breaker_check` step-3 lock consolidation.** Symmetric to operator_edge.
- **Agent-task family retry budgets.** Wire the `retry_policy` primitive from PR #2297 to the agent task family. Needs fingerprinting strategy first.
- **Bulk migration of ~5 linear/fixed countdown sites** (`core/tasks_agents.py` family) to `compute_retry_countdown` from PR #2297.

#### Aspirational follow-ons (from Sessions 1165 + 1166)

- **`pg_stat_statements` on staging/prod.** Installed locally in Session 1165.
- **`capture_pa_acks_health_snapshot` slow-task investigation.** 36-min max, 18-min avg suspicious. Now also a canary for the 60s `statement_timeout` from #2295.

### Consolidation / deferred from Session 1165 (focused follow-on PRs)

- **Operator_edge lock consolidation** (`core/tasks_content.py:4216` + 6 release sites). Migrate the third ad-hoc `cache.add()` site to the canonical `singleton_lock` primitive from PR #2296. Behavior-preserving but bigger blast radius — deferred from PR #2296.
- **`_circuit_breaker_check` step-3 lock consolidation.** Symmetric to operator_edge. Worth its own focused PR.
- **Agent-task family retry budgets.** Wire the `retry_policy` primitive from PR #2297 to the agent task family. Needs fingerprinting strategy first (`agent_name + user_id + workspace_id`) to avoid global suppression during transient incidents.
- **Bulk migration of ~5 linear/fixed countdown sites** (`core/tasks_agents.py` family) to `compute_retry_countdown` from PR #2297.

### Aspirational follow-ons (from Session 1165)

- **`pg_stat_statements` on staging/prod.** Installed locally in Session 1165 for the COO #1 threshold sniff. Same change to `postgresql.conf` (`shared_preload_libraries = 'pg_stat_statements'`) + `brew services restart postgresql@<v>` + `CREATE EXTENSION` would enable live p99-based threshold reviews in non-local environments.
- **`capture_pa_acks_health_snapshot` slow-task investigation.** Rigby flagged 36-min max, 18-min avg as suspicious for a "snapshot" workload (likely (a) heavy DB reads/scans, (b) slow external calls, (c) lock waits, or (d) telemetry/file I/O contention). Now also a canary for the new 60s `statement_timeout` — if it starts failing under the timeout, that's the symptom telling you what was slow.

### Carryover small follow-ons from Session 1163 (still queued)

1. **Legacy `SystemConfiguration(key='policy_arbitrator_snapshot')` row cleanup** — small migration to hard-delete the legacy row after one or more new-model cycles have been observed (single-PR scope).
2. **`cycle_id` joinability fix** — `_policy_policy_arbitrator` in `core.py:2658` accepts the run-cycle's `cycle_id` instead of generating its own (single-file edit; joins `FinalAppliedOverrides` against `AutopilotAction`).
3. **Opportunistic narrative §4 + §5 cleanup of stale `FinalAppliedOverrides` mentions** — wait for the next time someone touches those sections.

### Deferred infrastructure track (avoid during offline-CI window)

4. **`celery-beat-schedule` CONFLICT — detector tuning** (preferred) or 36-file token-pattern phrasing sweep (fallback).
5. **Pre-existing PeriodicTask drift** (Session 1163 added 1 entry).
6. **`exists_on_disk: false` flag** in `_provenance.json` — 326 dead paths. Schema bump v1 → v2.
7. **Beat-schedule the regens** — weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands.
8. **Fix `build_learning_bridge_audit.py` generator** — falsely flags "ABC unused".
9. **Redis pooling sweep** (~40 inline `redis.Redis.from_url(...)` sites) — mirror Session 1144 OpenAI/Anthropic factory pattern. Session 1165's two new services (`redis_lock.py` + `retry_policy.py`) intentionally avoided adding more inline clients.

### Chris-call-only carryovers (still parked)

10. **Decision Command backend cleanup** — 5 Python files (regressed feature).
11. **DaVinci route removal** — `core/views_davinci.py` still routed from `core/urls.py`.
12. **Mission refresh PR #2190** — preserved branch.

---

## SESSION 1166 CLOSED — COO #2 + pa_acks_health item C (2026-06-19)

**2 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1166_COO_2_AND_WARN_PERSIST_ESCALATION.md`](docs/handoffs/SESSION_1166_COO_2_AND_WARN_PERSIST_ESCALATION.md).

| PR | Theme | SHA |
|----|------|-----|
| **#2301** | **COO #2 (MUST):** per-process Postgres `application_name` tagging — `PG_APPLICATION_NAME=dbz:<role>` env var + 11 Procfile entries + Makefile + strict verifier + infrastructure.md note | `512c7922` |
| **#2302** | **pa_acks_health item C:** WARN-persist 2 snapshots → CRIT escalation — 3 new factory-style probes + `sustain_gating.escalated_triggers` field + 15 truth-table tests | `47de895c` |

**All four MUSTs from Rigby's June 14 corrected v1 COO Backlog now closed.** Only SHOULD-tier items remain. Item C closed the Session 1164 deferred work after ≥24h of new-schema telemetry confirmed the substrate was stable.

**End-to-end verified post-merge:**
- `pg_stat_activity` shows 6/6 process classes tagged (`dbz:web`, `dbz:celery-pa`, `dbz:celery-broadcast`, `dbz:celery-long-running`, `dbz:celery-worker`, `dbz:celery-beat`); ad-hoc shells correctly fall through to legacy `unified_donkey_betz` default.
- Cadence task post-restart wrote JSONL line at `2026-06-20T00:48:01` carrying the new `escalated_triggers=[]` field (healthy state).
- 52/52 pa_acks_health threshold tests pass; 30/30 verifier tests pass.

**New persistent artifacts:**
- `PG_APPLICATION_NAME` env var convention (`dbz:<role>`, regex-enforced via `scripts/verify_repo_guardrails.py`).
- `core/management/commands/pa_acks_health.py`: 3 new `_trips_warn_*` factory-style probes + `sustain_gating.escalated_triggers` field + warn-persist escalation in `_compute_status`.
- `docs/topics/infrastructure.md` "Postgres application_name tagging" subsection.

**New gotchas captured:** none — both designs followed established Session 1164/1165 patterns (factory-style probes + reduce/no-re-classify + primitives + opt-in apply list + backward-compatible signatures).

### Session 1165 CLOSED — COO Backlog triple-MUST close (#1, #3, #6) (2026-06-19)

**4 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1165_COO_BACKLOG_TRIPLE_MUST_CLOSE.md`](docs/handoffs/SESSION_1165_COO_BACKLOG_TRIPLE_MUST_CLOSE.md).

| PR | Theme | SHA |
|----|------|-----|
| **#2294** | `fix(session-1165)` — `pa_local.sh` wrapper repointed at chris's token (donkeyking user removed locally) | `053631c8` |
| **#2295** | **COO #1 (MUST):** DB safety defaults — `statement_timeout=60s` + `idle_in_transaction_session_timeout=60s` + task-boundary `close_old_connections()` | `43933cfe` |
| **#2296** | **COO #3 (MUST):** singleton-task stampede prevention (`core/services/redis_lock.py` + 9 task applies + 2 ad-hoc migrations) + hour=3/4 beat stagger | `65b37fc3` |
| **#2297** | **COO #6 (MUST):** retry-storm prevention (`core/services/retry_policy.py` + 4 task applies) | `f5a080b3` |

**Three MUSTs from Rigby's June 14 corrected-v1 COO Backlog closed end-to-end.** Numbers picked from real `pg_stat_statements` data (installed locally mid-session under Chris's explicit auth) — slowest observed query 2.4s → 60s `statement_timeout` = ~25× headroom. Two new canonical primitives shipped (`redis_lock.py` + `retry_policy.py`); both use Django cache (Redis under the hood) to sidestep the Session 1144 Redis-pooling-sweep backlog. Hour=4 :00 beat cluster went from 9 simultaneous tasks → 1.

**New persistent artifacts:**
- `core/services/redis_lock.py` (~165 lines + 12 tests in `core/tests/test_redis_lock.py`).
- `core/services/retry_policy.py` (~215 lines + 19 tests in `core/tests/test_retry_policy.py`).
- Combined: 31 tests, all pass via `SimpleTestCase` (no DB dependency).

**New gotchas captured:**
- **Decorators that catch exceptions collide with Celery's `Retry` machinery.** First-draft `@with_retry_policy` decorator was discarded for explicit helpers because `self.retry()` raises `celery.exceptions.Retry` (an `Exception` subclass), which a generic wrapper would re-catch and double-retry.
- **Stale wrapper tokens silently 401 on session entry.** Memory rule `feedback_pa_local_verify_ownership.md` predicted this exact failure mode.
- **`pg_stat_statements` is a multi-step install requiring Postgres restart.** Edit `postgresql.conf` → `brew services restart` → superuser `CREATE EXTENSION` → wait for stats. Local Homebrew `postgresql@15` is separate from Docker `unified-postgres`.

**Coverage gaps closed:**
1. COO Backlog item #1 (MUST: DB safety defaults) — closed end-to-end, 4-step acceptance smoke green.
2. COO Backlog item #3 (MUST: singleton locks + jitter) — closed end-to-end.
3. COO Backlog item #6 (MUST: retry-storm prevention) — closed end-to-end.
4. Local Postgres observability — `pg_stat_statements` now live locally.
5. `pa_local.sh` drift — wrapper repointed at chris's token.

### Session 1164 CLOSED — queue_pressure rollup + pa_acks_health threshold tuning (2026-06-19)

**3 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1164_QUEUE_PRESSURE_ROLLUP_AND_PA_ACKS_THRESHOLD_TUNING.md`](docs/handoffs/SESSION_1164_QUEUE_PRESSURE_ROLLUP_AND_PA_ACKS_THRESHOLD_TUNING.md).

| PR | Theme | SHA |
|---|---|---|
| **#2290** | `queue_pressure` rollup in `ops_tool.overview` — calls `cockpit_tool.queue_lengths` and reduces (no re-classification) | `e69aa5cf` |
| **#2291** | `_WARN_QUEUE_DEPTH` raised 1 → 5 + sustain-window for binary infra triggers (no_workers, depth_crit) | `0951222f` |
| **#2292** | Time-adjacency check (stale previous ≠ "consecutive") + `sustain_gating` observability field on every snapshot | `420ae6d7` |

**End-to-end verified post-merge + restart:** workers restarted with new code (`pkill -9 -f celery; rm -f .celery*.pid; make celery`); manual fire of `capture_pa_acks_health_snapshot` wrote a JSONL line at `2026-06-19T22:22:01` carrying the new `sustain_gating` block. Item C (WARN persists 2 snapshots → CRIT) now evaluable after ~24h of new-schema telemetry.

**New persistent artifacts:**
- `core/services/td_handlers_ops.py:_ops_queue_pressure_rollup` (cockpit-reducer for ops surface).
- `core/management/commands/pa_acks_health.py`: `_WARN_QUEUE_DEPTH=5`, `_EXPECTED_INTERVAL_SECONDS=1800`, `_SUSTAIN_ADJACENCY_FACTOR=2`, `_is_previous_adjacent`, `_trips_no_workers`, `_trips_depth_crit`, `_read_previous_snapshot`, `_compute_status(report, previous_report=None)`, `sustain_gating` block on every emitted report.
- `core/tests/test_ops_queue_pressure_rollup.py` (8 tests) + `core/tests/test_pa_acks_health_thresholds.py` (36 tests).

**Coverage gaps closed:**
1. Queue pressure visible in `ops_tool.overview` (operators no longer drill into cockpit for system-level health).
2. pa_acks_health no longer flips CRIT on transient infra dips (single-snapshot zero-workers or depth>=20 from a healthy state).
3. Scheduler-pause-then-restart no longer falsely triggers CRIT on the first post-restart snapshot (time-adjacency defense).
4. Sustain-decision provenance recorded on every snapshot — item C tuning has explicit adjacency evidence to work from.
5. **COO Nervous System Backlog item #8 (SHOULD) closed end-to-end.** Remaining MUSTs (#1, #3, #5, #6) + SHOULD (#7) carry forward.

**New gotchas captured:** none surfaced this session — the design contract (cockpit single-source-of-truth + JSONL-as-state for low-frequency observability) held cleanly through all three PRs. Rigby's pre-merge nit pattern (#2291 → #2292) worked well as scope-splitter.

### Session 1163 CLOSED — Disclosure L drift correction arc (C-style + B-style) (2026-05-26 → 2026-05-27)

**4 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1163_DISCLOSURE_L_DRIFT_CORRECTION_ARC.md`](docs/handoffs/SESSION_1163_DISCLOSURE_L_DRIFT_CORRECTION_ARC.md).

| PR | Theme | SHA |
|----|------|-----|
| **#2283** | Disclosure L §13 path-move addendum (classes moved `core.py` → `governance.py` + `experiment.py` per commit `fe94c928` 2026-03-09) | `9bf87f4e` |
| **#2284** | `latest_overrides_snapshot` C-style honest interim PA tool + Disclosure L §14 mechanism drift addendum + narrative §6.4 rewrite + row_updated_at nit-fix | `dad9ec84` |
| **#2285** | Narrative §6.4 tool-name drift fix — `ops_tool` → `autopilot_tool` (self-referential dogfood loop captured) | `b99bfa0c` |
| **#2286** | **B-style `FinalAppliedOverrides` per-cycle table** + idempotent backfill + time-travel `at` arg + 90-day Celery beat retention + Disclosure L §14.7 "B-style shipped" + narrative §6.4 lineage table | `636ed6c7` |

**End-to-end verified post-merge:** 2 autopilot cycles ran; `at='2026-05-27T22:05:56+00:00'` (between cycles) correctly returned the older row; no-`at` query correctly returned the newer row. Time-travel selection working against real data (14 knobs populated, real `backlog_governor_level` + `desk_allocation:*` + `goal_allocation:*` keys).

**New persistent artifacts:**
- `FinalAppliedOverrides` Django model + migration 0354 + 90-day retention task + beat schedule entry `purge-finaloverrides-90d` (daily 02:40 MST).
- `autopilot_tool action=latest_overrides_snapshot at='<ISO 8601>'` PA tool action.
- Disclosure L §13 + §14 + §14.7 addenda (§1–§12 byte-identical).
- Narrative §6.4 lineage table (Session 1162 framing → Session 1163 discovery → C-style → B-style).
- New feedback memory `feedback_corpus_walks_surface_mechanism_drift.md` + MEMORY.md index entry.

**Coverage gaps closed:**
1. Disclosure L §5 Component 4 mechanism drift — patent claimed `FinalAppliedOverrides.objects.create(...)` per-cycle; as-built was single-row `SystemConfiguration` overwrite. Now matches patent intent.
2. Narrative §6.4 invalid ORM recipe — corrected to live recipe against new model.
3. Operator ergonomics gap — `latest_overrides_snapshot` tool with `at` arg replaces ad-hoc ORM debugging recipe.
4. Disclosure L §10(g) "for time-series auditability" counsel call — de-escalated from "amendment-to-match-reality" to optional "amendment-to-strengthen."

**New gotchas captured:**
- `cycle_id` mismatch between cycle wrapper (`core.py:2658` generates own `_uuid.uuid4()`) + arbitrator-issued snapshot ID. Minor cleanup candidate; joinability across `FinalAppliedOverrides` ↔ `AutopilotAction` would benefit from shared cycle_id.
- Self-referential dogfood loop continues: PR #2284 introduced a tool surface and got the tool name wrong in its own docs (caught by Rigby's post-merge smoke test, fixed in PR #2285). Same family as Session 1159 #2256 → #2257. Future corrective PRs introducing tool surfaces should invoke the tool against their own docs before merge.

### Session 1162 CLOSED — Narrative triple + PA acks observation completion (2026-05-26)

**8 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1162_NARRATIVE_TRIPLE_AND_PA_ACKS_OBSERVATION_PHASE.md`](docs/handoffs/SESSION_1162_NARRATIVE_TRIPLE_AND_PA_ACKS_OBSERVATION_PHASE.md).

| PR | Theme | SHA |
|----|------|-----|
| **#2274** | `pa_acks_health` (PA-worker-set filter) — `is_pa_relevant` flag | `ffce1494` |
| **#2275** | `pa_acks_health` (Mountain time) — `generated_at_mt` alongside UTC | `25b2198a` |
| **#2276** | **`WORKSPACES_AND_SCOPING.md`** narrative (batch P, 484 lines) | `dc027f4f` |
| **#2277** | docs/INDEX.md regen post-workspace | `0cfaa767` |
| **#2278** | **`INITIATIVES_AND_LIFECYCLE.md`** narrative (batch Q, 724 lines) | `1ba017e3` |
| **#2279** | docs/INDEX.md regen post-initiative | `373148c7` |
| **#2280** | **`SELF_TUNING_AND_EXPERIMENTATION.md`** narrative (batch R, 606 lines, first patent-rooted) | `53879aef` |
| **#2281** | docs/INDEX.md regen post-self-tuning | `1670436d` |

**New persistent artifacts:** three new operator-handbook narratives (~1,814 lines combined) at `docs/narratives/`. Active doc count 904 → 907. New frontmatter pattern: `maps_to_patents` field for patent-rooted narratives.

**Coverage gaps closed:**
1. Workspace concept — scattered across 9 prior narratives, no canonical home → batch P.
2. Initiative entity + lifecycle + non-signal creation paths — companion to SIGNAL_INTELLIGENCE (signal arc) → batch Q.
3. Disclosure L self-tuning experimentation — Session 1161 carryover → batch R.

**Post-merge ops gotcha:** PRs #2274 + #2275 said "no `@shared_task` changes — workers don't need restart" but the worker `sys.modules` cache held the old `Command` class. Discovered when 12:30 CDT auto-fire wrote JSONL without new fields. Memory rule broadened (see READ THIS FOURTH above). Post-restart cadence is fully instrumented.

### Session 1161 CLOSED — PA acks_late watch instrumentation + 30-min cadence

**3 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1161_PA_ACKS_WATCH_INSTRUMENTATION_AND_CADENCE.md`](docs/handoffs/SESSION_1161_PA_ACKS_WATCH_INSTRUMENTATION_AND_CADENCE.md).

| PR | Theme | SHA |
|----|------|-----|
| **#2269** | `pa_acks_health` (A) — `oldest_queued` + `inflight_estimate` ack-behavior proxies | `7244dfdb` |
| **#2270** | `pa_acks_health` (B) — `per_worker` rollup + `worker_last_event_at` heartbeat on hang samples | `77bd18d8` |
| **#2271** | `pa_acks_health` cadence — `build_report()` refactor + every-30-min beat task + JSONL persistence | `6656f193` |

**New persistent artifacts:** new `@shared_task` `core.tasks.capture_pa_acks_health_snapshot`, new beat entry `pa-acks-health-capture` (every 30 min, queue=broadcast), per-day JSONL log at `logs/pa_acks_health/YYYY-MM-DD.jsonl` (gitignored).

**Post-merge ops:** workers restarted to register the new task; full path verified end-to-end (beat → broadcast worker → task → JSONL write). Beat picked up the new `PeriodicTask` row automatically via `DatabaseScheduler` polling — no beat restart needed.

### Session 1160 CLOSED — Session 1158-carryover queue clear + EDITING_GUARDRAILS operational

**8 PRs merged via bypass mode.** Full handoff: [`docs/handoffs/SESSION_1160_QUEUE_CLEAR_AND_GUARDRAILS_OPERATIONAL.md`](docs/handoffs/SESSION_1160_QUEUE_CLEAR_AND_GUARDRAILS_OPERATIONAL.md). Key PRs: #2259-#2264 (queue clear + EDITING_GUARDRAILS), #2266-#2267 (pa_acks_health scaffolding).

### Previous closed work still relevant for context

- **Session 1159** — PA acks_late fix + narrative B/C/D iterations + EDITING_GUARDRAILS contract. 3 PRs.
- **Session 1158** — 15 subsystem narratives shipped. Template v1-LOCKED. 8 PRs.

---

## 🚨 ACTIVE ISSUES carrying into Session 1167

### 1. GitHub Actions billing — still down

Same annotation as Sessions 1149-1166. Multi-day outage until Chris funds account.

**Self-merge protocol during outage** (Sessions 1149 + 1150 + 1158-1166 pattern):

For every PR, run local mirrors before push:
```bash
.venv/bin/python scripts/verify_repo_guardrails.py --inventory-advisory
.venv/bin/python tools/check_direct_llm_calls.py --root . --whitelist .ci/llm_whitelist.txt --warn-only
```

Self-merge with bypass requires:
1. Both local mirrors run.
2. Only failure is the pre-existing `celery-beat-schedule` CONFLICT.
3. Merge commit body documents the bypass with both `billing outage` and `pre-existing CONFLICT` named.
4. PR scope is documentation or low-risk verifier baselines (no production code changes).
5. Production-code changes need explicit per-PR Chris-authorization in-session (Session 1159 PR #2255 + Session 1163 PR #2286 + Session 1166 PRs #2301 / #2302 precedent).

### 2. `celery-beat-schedule` CONFLICT — detector signal pending

Session 1157 PR #2243 closed the code-level footgun. Context-kit CONFLICT signal still flags because its detector heuristic is keyword/path-based across ~36 files. Queued for Session 1164+.

### 3. PA `acks_late=False` observation phase — FULLY INSTRUMENTED + THRESHOLDS TUNED + STAMPEDE-LOCKED + WARN-PERSIST ESCALATION LIVE

Sessions 1161 + 1162 closed the instrumentation gap; Session 1164 PRs #2291 + #2292 closed the threshold-tuning portion. Session 1165 PR #2296 added `@singleton_task("capture-pa-acks-health-snapshot", ttl=300)` so the cadence task cannot self-stampede. **Session 1166 PR #2302 closed item C — WARN-persist 2 snapshots → CRIT escalation is now live in `_compute_status`.** The acks_late observation surface is feature-complete.

- `logs/pa_acks_health/YYYY-MM-DD.jsonl` grows by ~48 lines/day (`*/30` cadence).
- Each snapshot carries the full `sustain_gating` block: `previous_adjacent`, `expected_interval_seconds`, `adjacency_factor`, `gated_triggers` (suppression), and `escalated_triggers` (boost, Session 1166 NEW).
- WARN-level log line fires in celery-broadcast log whenever `status != OK`.

**Session 1166 close state (2026-06-19):** workers restarted twice (after PR #2301 and again after PR #2302). All four MUSTs from Rigby's June 14 corrected v1 backlog now closed. Item C live; any `warn_persist:*` label appearing in `escalated_triggers` is a CRIT escalation worth investigating per the handoff.

**What Session 1167 should check on entry:**
- `wc -l logs/pa_acks_health/$(date -u +%Y-%m-%d).jsonl` — confirm overnight cadence ran (file named in UTC).
- Tail a few JSONL lines and confirm each carries `escalated_triggers` (if any line lacks the field, the workers didn't restart post-#2302 and the new code is dormant — see Session 1167 FIRST THING above).
- `grep -o '"escalated_triggers":\[[^]]*\]' logs/pa_acks_health/$(date -u +%Y-%m-%d).jsonl | sort | uniq -c | sort -rn` — bulk should be empty lists; any non-empty list is a real warn-persist CRIT escalation.
- `grep "pa_acks_health" celery-broadcast.log | grep -v "succeeded\|received"` should be empty unless a status changed.
- `grep -i "retry_denied\|singleton_task" celery*.log` may surface budget exhaustion or stampede skips from PRs #2296 / #2297 — good observability signal, not necessarily a bug.

---

### Cross-session lessons (Sessions 1145–1165)

- **Recon before sweep.** Multiple back-to-back sessions where mid-recon findings flipped the PR plan.
- **Narratives become canon; topic docs get corrected to match** (1158).
- **`docs/*_AUDIT.md` files may be DOC-AUTOGEN** — check line 1 for marker before banner sweep (1146).
- **`build_*_audit` generators can lag reality** — fix the generator, not the output (1146).
- **Bypass-merging during a CI outage is workable IF disciplined** (1150).
- **"One mechanical batch then stop" applies even when batches are easy** (1150).
- **Cited-by-narrative is a triage signal** for the 778 not-HIGH handoffs (1158).
- **Disk + swap pressure mimics Celery bugs** — check disk first (1158).
- **`unified-postgres` lives in Docker** — don't `docker system prune` or restart Docker as a whole (1158).
- **EDITING_GUARDRAILS is load-bearing** for any narrative edit (1159).
- **Self-referential dogfood.** A guardrails-introducing PR can still violate its own rules — `#2256 → #2257` (1159). PR-template checklist closes the loop (1160).
- **Production-code bypass needs explicit per-PR Chris auth** (1159).
- **Stack restart playbook works in ~30 s** post-Mac-reboot (1159).
- **`git show` first for mtime mysteries** — before invoking ops tools, `git log --since/--until <timestamp>` resolves nearly every case (1160).
- **Symmetric cross-references prevent half-resolved navigation** — pair `maps_to_*` frontmatter with reverse "Related X" sections (1160).
- **Append-only edits are safer than restructure for high-trust documents** — PR #2263 added cross-link sections at the end of 6 narratives without touching milestone tables or vocabulary sections (1160).
- **Cadence wrappers belong in beat, not cron** (1161). `DatabaseScheduler` polls — adding a `PeriodicTask` row via `add_critical_celery_tasks` is the canonical path. Beat picks up new rows without restart.
- **New `@shared_task` decorators are invisible to running workers** (1161) until they restart. Generalized further Session 1162: *any module imported by a task body* is cached in `sys.modules` and needs the same restart even when the `@shared_task` is unchanged. Fix: `pkill -9 -f celery; rm -f .celery*.pid; make celery`.
- **"Stop and watch" is its own ship-able milestone** (1161). Three sequential PRs that move from "snapshot tool" to "cadenced observation surface" can complete a session arc without the analytics layer on top. Threshold tuning waits for the data.
- **NEW (1162)** **The narrative-triple shipping pattern works at scale.** Code survey → draft → split-paste Rigby review → apply fixes → merge ran cleanly three times in one session. PA chat payload limit (~24 KB) forces multi-message review for any narrative >~24 KB; workable, not blocking.
- **NEW (1162)** **Patent-rooted narratives are a viable corpus pattern.** Frontmatter `maps_to_patents` field creates bidirectional cross-links between frozen IP artifacts and current-state operator-handbook docs. Patent text stays frozen (Rigby's verdict: addendum-only, never inline rewrite); narrative stays current; path drift handled via the patent's addendum section, not by editing the narrative away from the disclosure.
- **NEW (1162)** **PR-description anti-pattern to avoid:** "no `@shared_task` changes — workers don't need restart." Wrong for the case where the PR modifies a module that a task body imports. Correct phrasing: "Modifies [Command class] imported by [task_name] task body — celery workers need restart for scheduled fires to pick up the change."
- **NEW (1162)** **Anti-duplication discipline against companion narratives works.** `INITIATIVES_AND_LIFECYCLE.md` §8 punted 7 things to `SIGNAL_INTELLIGENCE.md`. Rigby's verdict: "clean and correct, not over-claiming." Model for future companion narratives where two docs cover related arcs.
- **NEW (1162)** **Open Questions are a triage surface, not just gap markers.** Each §6 item should resolve to a Rigby-stated verdict ("deliberate" / "real gap" / "known operational risk" / "design decision"), not stay as "Rigby's call" indefinitely. Three narratives x 5 open questions each = 15 verdicts captured this session; this triage is part of the review pass, not separate.
- **NEW (1163)** **The corpus walk IS the deliverable.** Chris's in-session value statement after Session 1163's `FinalAppliedOverrides` mechanism-drift discovery: *"This is why it's so important for us to go through all of the /docs/ like we have been doing, that's how we surface these issues!!"* Saved as feedback memory `feedback_corpus_walks_surface_mechanism_drift.md`. When mid-recon finds a doc-says-X-but-code-does-Y mismatch, STOP and route options through Rigby. Don't quietly bridge gaps by implementing what the doc said. Honest pattern: ship the C-style honest-tool PR + frozen-artifact addendum + queue the B-style correct fix with design Qs named.
- **NEW (1163)** **C-style honest interim ≠ A-style fake.** A C-style PR ships an honest small surface that explicitly documents what it does NOT support (storage block with `mechanism` field naming the limitation). An A-style PR ships a tool that pretends to support something it doesn't (e.g., accepts a `time` arg but silently ignores it). Rigby's verdict: "A is unacceptable — implicitly lies." Always C, never A.
- **NEW (1163)** **Frozen-artifact addenda scale across multiple discoveries.** Disclosure L gained §13 + §14 + §14.7 in a single session without editing §1–§12 once. Future patent disclosures with similar drift can follow the same pattern: append §N.x subsections, never inline-edit the original body. Each subsection records the lineage from disclosure-time intent → as-built state → corrective fix.
- **NEW (1163)** **Self-referential dogfood loop continues — corrective PRs can introduce their own drift.** PR #2284 corrected the narrative §6.4 to be honest about `FinalAppliedOverrides` not existing, AND in the correction misnamed the tool namespace (`ops_tool` instead of `autopilot_tool`). Caught by Rigby's post-merge smoke test, fixed in PR #2285. Same family as Session 1159 #2256 → #2257. Rule extension to the 00-START dogfood line: *"if your PR introduces a tool surface, invoke the tool against your own docs before merge."*
- **NEW (1163)** **Hand-written migrations beat auto-generated when scope matters.** `makemigrations` produced a 606-line migration including unrelated `AlterField` ops across multiple subsystems. The focused hand-written one was 168 lines, only the new model + index + idempotent backfill. For scoped subsystem PRs, prefer hand-written migrations — the auto-generated version pulls in every subsystem's pending drift as scope-creep.
- **NEW (1163)** **Idempotent backfills are cheap insurance.** The Session 1163 migration's `if FinalAppliedOverrides.objects.exists(): return` check makes re-running the migration safe and turns the backfill into a one-shot no-op if rows already exist. Per Rigby: "Pick (b) backfill + (c) cleanup later" is the safe pattern — never leave a post-deploy data gap, never foreclose the rollback path. The legacy source row stays put until ≥ 1 new-model cycle is observed.
- **NEW (1164)** **Reduce, never re-classify, when consuming a sibling surface.** PR #2290 wires `ops_tool.overview` to call `cockpit_tool.queue_lengths` and project a rollup — thresholds live in cockpit's `_classify` only. The cost of duplicating thresholds for "one little ops field" is zero today and unbounded the moment someone tunes cockpit. Same pattern applies any time gateway A wants what gateway B already computes: proxy + reduce.
- **NEW (1164)** **JSONL-as-state is the right substrate for low-frequency observability.** PA acks_health sustain semantics needed prior state; the cadence task already wrote durable JSONL; introducing Redis for one-bit-of-state would have added a dependency to the very signal we're stabilizing. Rule of thumb: if the cadence is in minutes and the artifact is already a structured log, the log IS the state store.
- **NEW (1164)** **Distribution-first tuning beats vibes.** PR #2291 raised `_WARN_QUEUE_DEPTH` from 1 to 5 only after observing 331 consecutive snapshots at depth=0. The cutoff is still preemptive — but the direction (raise, not lower) was data-validated. The same data-walk decided NOT to touch `failures >= 3`: 12/12 real CRITs came from that trigger; sustain semantics would have masked the only signal doing work.
- **NEW (1164)** **Pre-merge nit-as-spec splits scope cleanly.** Rigby's two pre-merge nits on PR #2291 (log-tail order + time adjacency) acted as a scope-splitter: one was already correct (lex == chrono for date-prefixed filenames), one became PR #2292's entire scope. The nit format made the boundary easy to draw and kept #2291 from sprawling.
- **NEW (1164)** **Observability fields belong on the same artifact as the decision.** PR #2292 puts `sustain_gating` on every snapshot rather than in a separate audit log. Downstream tuning (item C: WARN-persist escalation) can read one file; ops dashboards see decision context next to outcome. If you find yourself drafting a new audit table for "why did this status fire?", check whether the field can live next to the status itself.
- **NEW (1164)** **Backward-compatible signatures + conservative defaults absorb mid-arc design changes.** `_compute_status(report, previous_report=None)` kept PR #2290's test factories working unchanged when #2291 added the second argument, and made first-run / no-prior-state cases safe by default (sustain triggers never fire when there's nothing to compare against). Same trick worked again when #2292 added adjacency: still backward-compatible, still safe-on-None, no test churn.
- **NEW (1165)** **"Data wins over vibes" pays off twice for threshold picks.** COO #1's 60s timeout was data-backed via `pg_stat_statements` (slowest observed 2.4s → 25× headroom). Same discipline let me pick `@singleton_task` TTLs from observed task durations (Session 1164 sniff) and `retry_policy` budget caps from observed failure patterns. Two new primitives shipped in one session with calibrated defaults; tuning surface visible from the start.
- **NEW (1165)** **Primitives + opt-in apply list is the right Phase 1 scope for stampede / retry-storm prevention.** PRs #2296 and #2297 both followed this shape: ship the canonical primitive + tests + apply to a hand-picked set, defer bulk migration. Reduces blast radius; gives ops a chance to spot regressions on a small set before fanning out. Operator_edge + circuit_breaker + agent-family migrations queued as focused follow-on PRs.
- **NEW (1165)** **Manual stagger beats `before_task_publish` jitter for v1.** Rigby's explicit verdict: deterministic manual rewrite over a clever invisible-modifier interceptor. Operator surprise + debugging complexity were the named tradeoffs. The manual stagger is also self-documenting in the beat_schedule definition itself.
- **NEW (1165)** **Drop one decorator's worth of magic when explicit helpers do the job.** First-draft `@with_retry_policy` decorator was discarded for `compute_retry_countdown` + `check_retry_budget`. Bug discovered during design: `self.retry()` raises `celery.exceptions.Retry` (an Exception subclass) which a wrapper's generic `except Exception` would catch and double-retry. Two helpers + explicit callsite usage keeps control flow transparent.
- **NEW (1165)** **Pre-implementation Rigby review at every MUST scope is the gating step.** Not just "is this a good idea" but "scope A vs B, storage backend, apply list, lock/budget semantics, error contracts." Single-session triple-MUST closes only work when the scope is locked before code. Without it, the apply-list arguments would have eaten the session.

---

## RECENT SESSION ARCS

- **Session 1166** — COO #2 (per-process Postgres `application_name` tagging) + pa_acks_health item C (WARN-persist → CRIT escalation). 2 PRs merged. All 4 MUSTs from June 14 corrected v1 COO Backlog now closed.
- **Session 1165** — COO Backlog triple-MUST close (#1 DB safety defaults + #3 singleton locks + jitter + #6 retry-storm prevention) + wrapper fix. 4 PRs merged. Two new canonical primitives shipped (`redis_lock.py` + `retry_policy.py`). `pg_stat_statements` installed locally.
- **Session 1164** — queue_pressure rollup in `ops_tool.overview` + pa_acks_health threshold tuning A+B + time-adjacency + sustain observability. 3 PRs merged. Closed COO Backlog item #8 (SHOULD) end-to-end.
- **Session 1163** — Disclosure L drift correction arc (path-move addendum + C-style honest tool + tool-name dogfood loop + B-style FinalAppliedOverrides per-cycle table). 4 PRs merged.
- **Session 1162** — narrative triple (workspace + initiative + self-tuning) + PA acks observation completion. 8 PRs merged.
- **Session 1161** — PA acks_late watch instrumentation + 30-min cadence. 3 PRs merged.
- **Session 1160** — 1158-carryover queue clear + EDITING_GUARDRAILS operational. 8 PRs merged.
- **Session 1159** — PA acks_late fix + narrative B/C/D iterations + EDITING_GUARDRAILS contract. 3 PRs merged.
- **Session 1158** — corpus-narrative program: 15 narratives + drift sweep + cited-handoff frontmatter + reports/patents recon. 8 PRs merged.
- **Session 1157** — celery-beat-schedule cleanup option A. 1 PR merged (bypass mode).
- **Session 1156** — P3.5 round 9 (FINAL) + P3.5 track CLOSE. 1 PR merged.
- **Session 1155** — P3.5 round 8. 1 PR merged.
- **Session 1154** — P3.5 round 7. 1 PR merged.
- **Session 1153** — P3.5 round 6. 1 PR merged.
- **Session 1152** — P3.5 round 5. 1 PR merged.
- **Session 1151** — P3.5 round 4. 1 PR merged.
- **Session 1150** — Session 1149 merge wave + P3.5 round 3. 4 PRs merged.
- **Session 1149** — SYSTEM_OWNER §3 rewrite + verify_doc_claims drift fixes. 3 PRs.
- **Earlier:** see `docs/handoffs/CURRENT.md`.
