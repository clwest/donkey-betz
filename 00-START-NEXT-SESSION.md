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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation; use that if you don't want to remember the env vars. **Current pinned conversation: `pa-85960cfecf5e42d5`** (Rigby created fresh at Session 1258 open via `session_tool.create_fresh` at Chris's explicit directive — NOT score-driven; the prior pin `pa-e8999a1793f04e23` was at 85/continue when rotated). Title: "Session 1258 — open + priority menu (PR 3.3 / receipts gap / Tue 06:30 first-fire)". `service_context: local` confirmed via `platform_config_tool overview` at S1258 open. Carry-forward seeded via PR #2707 fix (starter_prompt echoes carry_forward_summary verbatim) covering S1257 Chief of Staff close + full S1258 priority menu. Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — PA "CONSUME-1-THEN-HANG" IS USUALLY DISK PRESSURE

Memory: `feedback_pa_hang_from_disk_pressure.md`. If the PA worker processes exactly one task and then goes silent, check `df -h /System/Volumes/Data` + `sysctl vm.swapusage` BEFORE deeper Celery debugging. Single-digit GiB free or swap < 2 GiB free → free disk first. Don't restart Docker — `unified-postgres` lives there.

## READ THIS THIRD (NEW Session 1160) — `git show` IS THE FIRST MOVE FOR MTIME MYSTERIES

If you see a cluster of doc mtimes within minutes of each other and wonder "what generated this?", run `git log --since="<timestamp - 1min>" --until="<timestamp + 1min>"` first. Session 1160's "May 25 09:36 batch" mystery resolved instantly via `git show 9d75f78f` — it was Chris's own Session 1143 PR #2197. Future similar questions should start with the git history before invoking Rigby's ops tools.

## READ THIS FIFTH (NEW Session 1184) — MANUAL PA WORKER RESTART NEEDS `PA_USE_FUNCTION_CALLING=true`

Memory: `feedback_pa_worker_function_calling_env.md`. `make celery` sets it; ad-hoc `nohup celery -A core worker ...` does NOT. Without it, the worker drops to keyword routing — and `source=claude-code` messages (every `pa_chat.py` call) short-circuit to `claude_code_coordination` intent which has NO `elif` branch in routing. Rigby returns text-only "I don't have tool access" responses that look like model refusal but are the system never offering tools. **Symptom:** `/tmp/celery-pa.log` shows `[PA_TASK_SUMMARY] ... tools=none tool_calls=0` every turn. **Fix:** always use `make celery`. If you must restart one worker by hand, include `PA_USE_FUNCTION_CALLING=true` in env. Session 1184 lost ~30 min on this.

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


## SESSION CLOSE — DOCS-TO-RIGBY CASCADE CHECKLIST (NEW Session 1234)

When a session edits any meaningful `.md` files in `docs/`, the close should run the **full 4-step cascade** below — `build_docs_index` alone does NOT make doc edits searchable by Rigby. Memory: `feedback_docs_pipeline_4_step_cascade.md`.

| Step | Command | What it does |
|---|---|---|
| 1 | `python manage.py build_docs_index` | Refresh `docs/INDEX.md` + `docs/_index.json` (file listing only) |
| 2 | `python manage.py build_rag_corpus` | Regenerate `.rag/corpus.jsonl` for local Ollama Q&A + `search_docs` PA tool local path |
| 3 | `python manage.py sync_docs_index_to_documents` | Push index entries to `content.models.Document` rows |
| 4 | `python manage.py sync_docs_index_to_documents --embed` | Generate `DocumentEmbedding` rows in `unified_embeddings` pgvector table — **this is what production `core.rag_integration` searches against** |

**Why this matters:** Session 1234 close discovered prod corpus was 12d stale + 1820 docs had never been pushed to the `Document` table. No auto-trigger exists (no git hook, no beat task, no filesystem watcher). The pre-1234 memory rule was misleading — said docs "get embedded and injected" but only step 1 ran.

**Cost / time:** Trivial cost (~$0.05 for ~1800 docs at `text-embedding-3-small`), but step 4 is **30-45 min serial** for a full backfill from cold start. Incremental updates after a delta-changed session are seconds-to-minutes.

**Verification:**
```python
from content.models import Document, DocumentEmbedding
print('Document.objects.count():', Document.objects.count())
print('DocumentEmbedding.objects.count():', DocumentEmbedding.objects.count())
print('Latest update:', Document.objects.order_by('-updated_at').first().updated_at)
```
Latest update should reflect today's date. DocumentEmbedding count should have grown by ~5 × docs_changed.

**P1 candidate for a future beat task:** `core.tasks.refresh_docs_corpus` that hashes `docs/_index.json` daily and re-runs steps 2-4 on delta. Would eliminate the manual cascade.

---


## SESSION 1263 — CURRENT ENTRY POINT

### SESSION 1262 CLOSED — Claude Code task receipt reliability fixed (S1257 P1 gap closed)

**Session window:** 2026-06-30 (continuation of S1259-1261 single-day arc, same Rigby conversation `pa-85960cfecf5e42d5`).
**Full handoff:** [`SESSION_1262_CLAUDE_CODE_TASK_RECEIPT_RELIABILITY.md`](docs/handoffs/SESSION_1262_CLAUDE_CODE_TASK_RECEIPT_RELIABILITY.md).

**TL;DR:** The receipts-gap that re-surfaced in S1261 (Rigby's recursive `claude_code_tool` silently vanished) is closed. PR #2752 makes `claude_code_engineer_task` write an `AgentExecution` row at task entry + wire the existing S1174 follow-up wake stack + makes `_post_to_conversation` fail-loud. Five recent dispatches that silently vanished (task_ids 9d601010, 068ee853, bf7ca961, 18734082, f8a4d3c2) are now diagnosable. Discovery → Rigby Phase 1 SIGN → implementation → 10 new tests + 224 regression tests → 3 live dispatches → Rigby Phase 4 SIGN → admin-merge → post-merge prod-verified, all one session.

**Session 1262 PR (admin-merged):**

| PR | Type | Scope | Merge SHA |
|---|---|---|---|
| [#2752](https://github.com/clwest/donkey-betz-platform/pull/2752) | fix | claude_code_engineer_task writes AgentExecution + fail-loud post-back; 3 files, +769/-31 (most additions are docstrings + tests) | `5e30143e` |

**Headline outcomes:**

- **Five recent silent disappearances are now diagnosable.** Every claude_code_tool dispatch writes an AgentExecution row with `input_data.celery_task_id`, persists the result envelope on `output_data`, and arms the S1174 follow-up wake. Rigby's PA conversation receives a completion banner automatically via the consumer-side auto-followup ChatConversation row.
- **Six new greppable log markers** for diagnostics: `[CLAUDE_CODE_EXECUTION_CREATED]` INFO, `[CLAUDE_CODE_POSTBACK_DROPPED]` ERROR, `[CLAUDE_CODE_POSTBACK_FAILED]` ERROR, `[CLAUDE_CODE_AGENT_DUP]` WARN, `[CLAUDE_CODE_FOLLOWUP_WIRE_FAILED]` WARN, `[CLAUDE_CODE_NO_AGENT_ROW]` WARN.
- **Live verification across 4 dispatches:** happy-path round 1 + round 2 (with `fire_agent_followup_subscriptions` added) + intentional failure path (`conversation_id=None`) + post-merge prod verification.
- **Zero architectural changes.** Reuses canonical `AgentExecution` + S1174 PR-2a stack. No new models, no new tables, no new PA tools, no JobContract/MissionRunner edits. `claude_code_tool` response shape preserved verbatim.

**Key lesson — two-step follow-up wiring:** `create_implicit_followup_subscription` ALONE arms the subscription but leaves it `state=armed` forever if no signal handler fires it. The canonical `_impl_execute_agent_task` calls `fire_agent_followup_subscriptions` AFTER terminal-state-save. Round 1 of verification missed the second call (sub stayed armed, banner didn't appear). Adding the explicit fire call fixed it (round 2: sub transitioned to `fired`, Rigby got the auto-banner).

### FIRST THING Session 1263

#### Priority 0 — 24h watch on new claude_code log markers (per Rigby SIGN suggestion)

Not a blocker; hygiene. Rigby's Phase 4 SIGN suggested: *"Post-merge, I'd only recommend a quick watch on logs for the new markers for ~24h to confirm no unexpected volume."*

Run periodically through tomorrow:
```bash
grep -hE 'CLAUDE_CODE_(POSTBACK_DROPPED|POSTBACK_FAILED|AGENT_DUP|FOLLOWUP_WIRE_FAILED|NO_AGENT_ROW)' ./celery*.log | tail -30
```

Expect mostly `[CLAUDE_CODE_AGENT_DUP]` WARN on every dispatch (until Priority 1 lands). Any unexpected `[CLAUDE_CODE_POSTBACK_FAILED]` or `[CLAUDE_CODE_FOLLOWUP_WIRE_FAILED]` lines should be investigated.

#### Priority 1 — Consolidate duplicate `claude-code` Agent rows (hygiene PR)

Surfaced by S1262 `[CLAUDE_CODE_AGENT_DUP]` WARN: BOTH `claude-code` and `ClaudeCode` Agent rows exist in DB (active, agent_type=tool_direct). The S1262 resolver picks `claude-code` deterministically, but the dup is noisy.

**Smallest fix:** decide which name is canonical (recommend `claude-code` based on td_handlers convention), data-migration the duplicate's `AgentExecution` FK references onto the keeper, then delete the duplicate. ~10-line PR.

#### Priority 2 — Pre-existing SLO breaches (NEW in S1260; still open)

`ops_tool action=overview window=30d` reports two breaches that are NOT Employee OS specific but compound with employee growth:

- **`agent_timeout_rate` 0.024284** vs target 0.002 (**12× over** — 28 timeouts / 1153 agent calls / 30d)
- **`celery_task_success_rate` 0.998825** vs target 0.999 (marginally under — 53 failures / 45,104 tasks / 30d)

Investigate root causes. Likely candidates: specific agent timeouts, specific worker memory pressure, network instability.

#### Priority 3 — MissionRunner `authority_check_fn` preflight hook (warn-mode)

Recommended by S1260 Architecture Planning doc (P4); deferred from S1261. `JobContract.authority` dict + `prohibited_actions` tuple have zero runtime readers today. At N=3 employees this is tolerable; at N=20 it would be malpractice.

**Smallest fix:** add optional `authority_check_fn` parameter to MissionRunner.__init__, call once at preflight (before any steps), log violations as `OpsRunEvent(label="authority_violation_observed")` but don't block. Two-PR arc: (1) param + no-op default; (2) wire warn-mode validator reading `JobContract.prohibited_actions`. Enforce-mode flip is a separate later PR after 2 weeks of clean warn-mode telemetry on N≥4 employees.

#### Priority 4 — Read-only Employee/Mission HTTP API

S1260 P5: 5 endpoints over existing model + `core/employees/status.py`:
- `GET /api/employees/`
- `GET /api/employees/<handle>/`
- `GET /api/employees/<handle>/jobs/<job_key>/status/`
- `GET /api/missions/<id>/`
- `GET /api/missions/<id>/evidence/`

~250 LOC Django views + serializers + tests. Removes LLM dependency for routine status reads. UI deferred until endpoint usage patterns inform page design.

#### Priority 5 — Hygiene: orphan route in `CELERY_TASK_ROUTES`

Pre-existing test failure: `test_every_route_pattern_matches_a_registered_task` reports `content.*` orphan pattern. Not introduced by any S1259-1262 PR. Either remove the pattern from `core/settings.py` or restore the missing `@shared_task`. ~10-line PR.

#### Priority 6 — Hygiene: refresh CLAUDE.md autoblock + agent taxonomy drift

`refresh_doc_inventory_blocks --check` reports CLAUDE.md + AGENTS.md autoblocks WOULD UPDATE (pre-existing drift). `verify_doc_claims --only-drift` reports CLAUDE.md agent taxonomy line says "8 rerouted, 1 blocked" but actual is "9 rerouted, 0 blocked" (CodeGeneratorAgent reclassified) and SERVICES.md file count drift (103 → 362). Combined into one ~15-line hygiene PR.

#### Priority 7 — Employee #4

**Architecturally ready.** Per S1261 close:
- MissionRunner contract stable (S1259-1262 confirm)
- Beat migration pattern documented (PR #2747 + migration 0373)
- Test scaffold reusable (3 existing examples follow consistent structure)
- Confidence + dedupe + workspace policy disappears from per-employee surface
- claude_code_tool receipts gap closed — Rigby-led verifications now reliable
- Estimated cost: 1,990-2,790 LOC, 9-14 hours

**No technical blockers. Awaiting Chris's call on which employee.**

#### Priority 8 — Carryover backlog

| Item | Source | Severity |
|---|---|---|
| `_persist_to_summary` 2/3 dup consolidation | S1261 deferred | low — abstraction cost ≈ duplication cost at N=2; reconsider at N=4 |
| `_resolve_chris_user` generalization in morning_brief | S1261 deferred | low — 1/3 jobs needs User instance; defer to N≥2 |
| `sync_celery_beat` orphan-handler revert trap (code fix) | S1258 mitigated via migration 0373 | medium — process documentation only; bug still in `sync_celery_beat.py:137-140` |
| PA tool surface gaps — no celery_inspect_tool, evidence_for_mission needs default-to-latest | S1258 verification | low |
| `RIGBY.primary_chat_id` contract constant still stale (env override active; cosmetic) | S1252 carryover | low |
| `Deliverable.create` defaults-to-completed upstream fix | S1252 carryover | low — workaround via `set_status` is reliable |

**~~ Priority 1 from S1262 (claude_code_tool task receipts gap) ~~** — **CLOSED PR #2752.**

---

## SESSION 1262 — PRIOR ENTRY POINT (preserved for context)

### SESSIONS 1259-1261 CLOSED — Employee OS v1 production-validated; Phase 2 foundation block shipped

**Session window:** 2026-06-30 (three sessions, single calendar day, single Rigby conversation `pa-85960cfecf5e42d5`).

**Full handoffs:**
- [`SESSION_1259_FIRST_FIRE_VERIFICATION.md`](docs/handoffs/SESSION_1259_FIRST_FIRE_VERIFICATION.md)
- [`SESSION_1260_EMPLOYEE_OS_PHASE_2_PLANNING_AND_DISCOVERABILITY.md`](docs/handoffs/SESSION_1260_EMPLOYEE_OS_PHASE_2_PLANNING_AND_DISCOVERABILITY.md)
- [`SESSION_1261_EMPLOYEE_OS_FOUNDATION_HARDENING.md`](docs/handoffs/SESSION_1261_EMPLOYEE_OS_FOUNDATION_HARDENING.md)

**TL;DR:**
1. **S1259:** Tuesday 06:30 docs-manager + 07:00 morning_brief both fired clean under MissionRunner-backed tasks. verdict=certified on both. PR #2747 cutover (legacy `core.tasks.generate_morning_brief_daily` → `chief_of_staff_morning_brief_run`) confirmed live in production. Zero escalations.
2. **S1260:** Architecture Planning doc produced (9 sections covering authority enforcement, employee manager UX, docs discoverability, tech debt, Employee #4 readiness, scalability). PR-γ shipped: 4 surgical doc edits made Employee OS discoverable from CLAUDE.md + PLATFORM_WHAT_IT_IS.md (previously 0 mentions in any anchor doc). New `docs/topics/employee-os.md` orientation pointer.
3. **S1261:** Foundation hardening. Independent verification corrected the S1260 audit — `MissionRunnerConfig` ALREADY had defaults for the constants the audit proposed putting in `JobContract`. PR #2750 deleted 12 redundant constants + 12 redundant kwargs across 3 jobs without expanding `JobContract` or touching `MissionRunner`.

**Session 1259-1261 PRs (both admin-merged):**

| PR | Type | Scope | Merge SHA |
|---|---|---|---|
| [#2749](https://github.com/clwest/donkey-betz-platform/pull/2749) | docs (S1260) | Employee OS discoverability rows in CLAUDE.md + PLATFORM_WHAT_IT_IS.md + new topics file; 4 files, +121/-17 | `e4414c96` |
| [#2750](https://github.com/clwest/donkey-betz-platform/pull/2750) | refactor (S1261) | Delete per-job constants/kwargs duplication covered by MissionRunnerConfig defaults; centralize workspace name; 7 files, +131/-77 | `918bbbe5` |

**Headline outcomes:**

- **Employee OS v1 is fully production-validated.** All 3 jobs (docs_manager + platform_audit + morning_brief) run end-to-end through MissionRunner with full audit trail. First-fires verified clean.
- **MissionRunner is now frozen infrastructure.** Zero edits across PR #2749 + #2750.
- **`JobContract` dataclass unchanged.** Zero new fields. Per S1252 PR 1 frozen-dataclass contract.
- **Employee OS now discoverable.** A fresh Claude/Rigby session orienting from CLAUDE.md can find Employee OS in 4 separate table rows; PLATFORM_WHAT_IT_IS.md has Layer 3.5 + 5 glossary entries.
- **Per-employee boilerplate reduced.** Employee #4 no longer writes 4 constants + 5 kwargs that match runner defaults — confidence/dedupe/workspace policy decisions disappear from the per-employee surface.
- **Verifier-loop pattern caught the S1260 wrong-fix recommendation** before any code was written. Saved a useless `JobContract` expansion.

### FIRST THING Session 1262

#### Priority 0 — Pre-existing SLO breaches (NEW, surfaced during S1260 runtime evidence sweep)

`ops_tool action=overview window=30d` reports two breaches that are NOT Employee OS specific but compound with employee growth:

- **`agent_timeout_rate` 0.024284** vs target 0.002 (**12× over** — 28 timeouts / 1153 agent calls / 30d)
- **`celery_task_success_rate` 0.998825** vs target 0.999 (marginally under — 53 failures / 45,104 tasks / 30d)

Investigate root causes. Likely candidates: specific agent timeouts, specific worker memory pressure, network instability. **Not a blocker for Employee #4**, but worth understanding before scaling employee count further.

#### Priority 1 — `claude_code_tool` task receipts + post-back reliability (carryover from S1257, re-surfaced S1261)

**Re-confirmed in S1261:** When Rigby dispatched a recursive `claude_code_tool` to verify PR #2750, the task_id returned but the post-back would not have arrived (no `AgentExecution` row, silent post-back failure, no Chat UI receipt). Worked around by sending receipts directly. The gap surfaces during Rigby-led verification flows — every time. Project memory: [`project_employee_os_ux_gap_task_receipts.md`](../../.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/project_employee_os_ux_gap_task_receipts.md).

**Severity:** medium. Until fixed, default to **local verification + receipts pushed via the same PA conversation** for Rigby-dispatched `claude_code_tool` work.

#### Priority 2 — MissionRunner `authority_check_fn` preflight hook (warn-mode)

Recommended by S1260 Architecture Planning doc (P4 in that PR sequence; deferred from S1261). `JobContract.authority` dict + `prohibited_actions` tuple have zero runtime readers today. At N=3 employees this is tolerable; at N=20 it would be malpractice.

**Smallest fix:** add optional `authority_check_fn` parameter to MissionRunner.__init__, call once at preflight (before any steps), log violations as `OpsRunEvent(label="authority_violation_observed")` but don't block. Two-PR arc: (1) param + no-op default; (2) wire warn-mode validator reading `JobContract.prohibited_actions`. Enforce-mode flip is a separate later PR after 2 weeks of clean warn-mode telemetry on N≥4 employees.

#### Priority 3 — Read-only Employee/Mission HTTP API

S1260 P5: 5 endpoints over existing model + `core/employees/status.py`:
- `GET /api/employees/`
- `GET /api/employees/<handle>/`
- `GET /api/employees/<handle>/jobs/<job_key>/status/`
- `GET /api/missions/<id>/`
- `GET /api/missions/<id>/evidence/`

~250 LOC Django views + serializers + tests. Removes LLM dependency for routine status reads. UI deferred until endpoint usage patterns inform page design.

#### Priority 4 — Hygiene: orphan route in `CELERY_TASK_ROUTES`

Pre-existing test failure: `test_every_route_pattern_matches_a_registered_task` reports `content.*` orphan pattern. Not introduced by any S1259-1261 PR. Either remove the pattern from `core/settings.py` or restore the missing `@shared_task`. ~10-line PR.

#### Priority 5 — Hygiene: refresh CLAUDE.md autoblock + agent taxonomy drift

`refresh_doc_inventory_blocks --check` reports CLAUDE.md + AGENTS.md autoblocks WOULD UPDATE (pre-existing drift). `verify_doc_claims --only-drift` reports CLAUDE.md agent taxonomy line says "8 rerouted, 1 blocked" but actual is "9 rerouted, 0 blocked" (CodeGeneratorAgent reclassified) and SERVICES.md file count drift (103 → 362). Combined into one ~15-line hygiene PR.

#### Priority 6 — Employee #4

**Architecturally ready.** Per S1261 close:
- MissionRunner contract stable (S1259-1261 confirm)
- Beat migration pattern documented (PR #2747 + migration 0373)
- Test scaffold reusable (3 existing examples follow consistent structure)
- Confidence + dedupe + workspace policy disappears from per-employee surface
- Estimated cost: 1,990-2,790 LOC (down from S1260 estimate of 2,000-2,800), 9-14 hours
- Domain logic dominates cost — pick an employee whose domain is well-understood first

**No technical blockers. Awaiting Chris's call on which employee is next.**

#### Priority 7 — Carryover backlog

| Item | Source | Severity |
|---|---|---|
| `_persist_to_summary` 2/3 dup consolidation | S1261 deferred | low — abstraction cost ≈ duplication cost at N=2; reconsider at N=4 |
| `_resolve_chris_user` generalization in morning_brief | S1261 deferred | low — 1/3 jobs needs User instance; defer to N≥2 |
| `sync_celery_beat` orphan-handler revert trap (code fix) | S1258 mitigated via migration 0373 | medium — process documentation only; bug still in `sync_celery_beat.py:137-140` |
| PA tool surface gaps — no celery_inspect_tool, evidence_for_mission needs default-to-latest | S1258 verification | low |
| `RIGBY.primary_chat_id` contract constant still stale (env override active; cosmetic) | S1252 carryover | low |
| `Deliverable.create` defaults-to-completed upstream fix | S1252 carryover | low — workaround via `set_status` is reliable |

---

## SESSION 1259 — PRIOR ENTRY POINT (preserved for context)

### SESSION 1258 CLOSED — PR 3.3 Morning Brief beat migration shipped + verified

**Session window:** 2026-06-29 (single-day session, S1257 → S1258 same calendar day).
**Full handoff:** [`SESSION_1258_EMPLOYEE_OS_PR_3_3_MORNING_BRIEF_BEAT_MIGRATION.md`](docs/handoffs/SESSION_1258_EMPLOYEE_OS_PR_3_3_MORNING_BRIEF_BEAT_MIGRATION.md).
**Companion spec:** [`docs/MORNING_BRIEF_SPEC.md`](docs/MORNING_BRIEF_SPEC.md) (v1, ratified S1232).

**TL;DR:** Daily 07:00 Denver Morning Brief now executes through the MissionRunner-backed Chief of Staff job. Beat row `generate-morning-brief-daily` kept its name + cadence + queue; only the `task` field flipped to `chief_of_staff_morning_brief_run`. Legacy `core.tasks.generate_morning_brief_daily` body deleted. **All 3 Employee OS jobs (docs_manager + platform_audit + morning_brief) now run end-to-end through MissionRunner.**

**Session 1258 PR (admin-merged):**

| PR | Type | Scope | Merge SHA |
|---|---|---|---|
| [#2747](https://github.com/clwest/donkey-betz-platform/pull/2747) | feat | PR 3.3 — Morning Brief beat migration to MissionRunner-backed Chief of Staff task; 8 files, +327/-516 | `eef22ed5` |

**Headline outcomes:**

- **All 14 verification requirements satisfied** (12 by tool, 2 N/A pending tomorrow's first fire).
- **Discovery → implementation → verification → merge → post-merge probe** all in one session. Discovery `cc4c0641-…` Rigby SIGN'd; verification `96cb6656-…` Rigby SIGN clean after §13.5 closure.
- **Critical bug caught during local verification** — the discovery §7 `sync_celery_beat` analysis was wrong on Python instance semantics. The orphan handler does `pt.save()` on a stale instance, which would silently revert the flip + disable the row. Fixed by adding migration `0373_session_1258_flip_morning_brief_beat_task.py` that flips the row BEFORE `sync_celery_beat` runs in the Procfile release sequence. **Lesson worth saving:** discovery analyses that depend on Python identity semantics across DB queries need end-to-end real-DB verification before being treated as authoritative.
- **Test churn:** 7 legacy tests deleted (covered the deleted task body), 2 classes inverted, 1 renamed, 5 new regression tests added. Net coverage preserved by `test_chief_of_staff_routine` + `test_employees_chief_of_staff`.
- **PA tool surface gaps surfaced** during Rigby verification: no `celery_inspect_tool`, `employee_tool evidence_for_mission` requires explicit `mission_id`. Both filed as out-of-scope follow-up tickets; not PR 3.3 blockers.

### FIRST THING Session 1259

#### Priority 0 — Live first-fire watch (TUE 2026-06-30, two fires same morning)

The morning_brief beat fires at **07:00 MDT = 13:00 UTC** on the NEW MissionRunner-backed task `chief_of_staff_morning_brief_run`. Docs-manager fires earlier at **06:30 MDT = 12:30 UTC** (carryover from S1257). Both first-fire watches in one morning.

**Morning brief first-fire verification (13:00 UTC):**
```python
from core.models import CeleryTaskEvent
from core.models_ops_runs import OpsRun
from core.models_deliverables import Deliverable
from datetime import date

today = date(2026, 6, 30)

# 1. CeleryTaskEvent fired on the NEW task name?
ev = CeleryTaskEvent.objects.filter(
    task_name='chief_of_staff_morning_brief_run',
    started_at__date=today,
).order_by('-started_at').first()
assert ev is not None, 'No fire on new task name'
print(f'  task_id={ev.task_id} status={ev.status} duration={ev.duration_seconds}s')

# 2. Mission row created via MissionRunner?
run = OpsRun.objects.filter(
    domain='mission', run_kind='morning_brief',
    started_at__date=today,
).order_by('-started_at').first()
assert run is not None, 'No OpsRun mission row'
print(f'  run.id={run.id} status={run.status} verdict={run.verdict}')
print(f'  summary keys: {list((run.summary or {}).keys())}')

# 3. Brief Deliverable in Morning Brief workspace?
deliv = Deliverable.objects.filter(
    user__username='chris', category='Morning Brief',
    created_at__date=today,
).order_by('-created_at').first()
assert deliv is not None, 'No brief Deliverable'
print(f'  deliv.id={deliv.id} content_len={len(deliv.content)}')

# 4. Sanity-grep for legacy task name (must be absent)
legacy = CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
    started_at__date=today,
).count()
assert legacy == 0, f'Legacy task fired {legacy} times on {today}'
```

**Existing verification script also works** — `python scripts/verify/verify_morning_brief_2026_06_27.py --date 2026-06-30` accepts both legacy + new task names via the S1258 PR 3.3 `Q()` update.

**If first-fire passes cleanly:** morning_brief arc closes. Combined with the docs-manager arc closing (if 06:30 fire also passes), the Employee OS trilogy is fully verified end-to-end in production.

**If first-fire fails:** root-cause via `[CHIEF_OF_STAFF_BRIEF_FAILED]` log line (it's a fail-loud raise, so CeleryTaskEvent.status='FAILURE' + an escalation Deliverable should both exist). The mission row will have `verdict='failure'` or similar.

#### Priority 1 — Employee OS UX/infrastructure gap: `claude_code_tool` task receipts + post-back reliability

**Carried forward from S1257 → S1258 → S1259.** Project memory: [`project_employee_os_ux_gap_task_receipts.md`](../../.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/project_employee_os_ux_gap_task_receipts.md).

The `claude_code_tool` → `claude_code_engineer_task` → `code_jobs` queue chain has three connected gaps (no `AgentExecution` row, silent post-back failure, no Chat UI receipt) + the `code_jobs` worker sandboxing issue. Full PR recommendation in the S1257 close section archived below.

**Severity:** medium. Until fixed, default to **local verification** for any Rigby-dispatched `claude_code_tool` task whose result Chris needs to see.

#### Priority 2 — PA tool surface gaps (NEW, surfaced during S1258 verification)

Two gaps Rigby flagged during PR 3.3 verification probes. Both independent backlog items:

1. **No `celery_inspect_tool` in PA surface.** Probe 2 (worker task registry inspection) had to be run via direct `.venv/bin/celery -A core inspect registered` CLI by Claude. Adding `celery_inspect_tool action=registered filter=…` would close the gap for future Rigby-led verifications.
2. **`employee_tool evidence_for_mission` requires explicit `mission_id`** — no default-to-latest. With no mission yet, the probe returns `Missing required arg 'mission_id'` rather than an empty result shape. A default-to-latest-mission-for-this-employee+job would be more useful for verification UX.

#### Priority 3 — Carryover from S1258 → S1259

| Item | Source | Severity |
|---|---|---|
| `claude_code_tool` task receipt / post-back / sandbox UX fix | S1257 verification incident | medium |
| Authority enforcement (JobContract.authority is policy, not enforced) | S1254 §3 | medium |
| PA tool surface gaps — no celery_inspect; evidence_for_mission needs default-to-latest | S1258 verification | low |
| `RIGBY.primary_chat_id` contract constant still stale (env override active; cosmetic) | S1252 carryover | low |
| Pre-existing failing test `test_every_route_pattern_matches_a_registered_task` (orphan `content.*` route) | S1253 #2733 PR description | low |
| `Deliverable.create` defaults-to-completed upstream fix | S1252 carryover | low |

**Do not begin Employee #4 work** until both Tuesday first-fire watches close cleanly.

---

## SESSION 1258 — PRIOR ENTRY POINT (preserved for context)

### SESSION 1257 CLOSED — Chief of Staff (Employee #3) landed end-to-end

**Session window:** 2026-06-29 (continuation of S1256 MissionRunner extraction arc).
**Full handoff:** [`SESSION_1257_EMPLOYEE_OS_PR_3_1_PR_3_2_CHIEF_OF_STAFF_LANDED.md`](docs/handoffs/SESSION_1257_EMPLOYEE_OS_PR_3_1_PR_3_2_CHIEF_OF_STAFF_LANDED.md).
**Companion spec:** [`docs/MORNING_BRIEF_SPEC.md`](docs/MORNING_BRIEF_SPEC.md) (v1, ratified S1232).

**TL;DR:** Shipped the third AI employee — Chief of Staff — through MissionRunner. The existing morning_brief workflow runs unchanged inside one MissionRunner step (wrap-as-single-step). **MissionRunner production caller count: 2 → 3** (docs_manager + platform_audit + morning_brief).

**Session 1257 PRs (both admin-merged):**

| PR | Type | Scope | Merge SHA |
|---|---|---|---|
| [#2744](https://github.com/clwest/donkey-betz-platform/pull/2744) | feat | PR 3.1 — register Chief of Staff as Employee #3 (contract + registry only) | `dc534924` |
| [#2745](https://github.com/clwest/donkey-betz-platform/pull/2745) | feat | PR 3.2 — Chief of Staff Morning Brief task runner via MissionRunner | `0c8c66a4` |

**Headline outcomes:**

- **3 employees registered** (Rigby, Platform Auditor, Chief of Staff). **3 jobs** (`docs_manager`, `platform_audit`, `morning_brief`). **3 production MissionRunner callers** (asserted by AST scan).
- **336/336 PR 3.2 gauntlet pass in 33s.** Real-DB PostgreSQL via `--keepdb`. `WorkflowOrchestrationAgent.execute` mocked at the import surface.
- **Both Rigby SIGN-WITH-EDITS locks applied** from discovery (deliverable `2983377c-…`): (1) no workflow internal touches — `brief_chars` derived postflight via single ORM read of `Deliverable.content`; (2) scalar-only `OpsRun.summary` — 9 scalar fields, no envelope persistence.
- **CoS-specific fail-loud Celery wrapper:** re-raises `RuntimeError` on `result.ok=False` (differs from Platform Auditor's wrapper, matches legacy S1234 D1 behavior).
- **No MissionRunner public contract changes.** No workflow internal modifications. No beat row flip yet (PR 3.3 scope) — landed in S1258 PR #2747.

---

## SESSION 1255 — PRIOR ENTRY POINT (preserved for context)

### SESSION 1254 CLOSED — Employee OS Foundation (5 PRs shipped)

**Session window:** 2026-06-29 Monday morning → afternoon (~7h).
**Full handoff:** [`SESSION_1254_EMPLOYEE_OS_FOUNDATION.md`](docs/handoffs/SESSION_1254_EMPLOYEE_OS_FOUNDATION.md).
**Canonical primitives doc:** [`docs/EMPLOYEE_OS_PRIMITIVES.md`](docs/EMPLOYEE_OS_PRIMITIVES.md) (NEW — read before any Employee OS work).

**TL;DR:** Documentation Manager went from "broken first beat fire" at session open to "registered + read API + shift-report DM + generalized comms + canonical Employee OS primitives doc" at close. Chris's architectural conclusion: **the platform already contains the majority of the Employee Operating System. Documentation Manager is proof #1, not the architecture.** The largest remaining gap is no longer communications — it is extracting the reusable employee lifecycle (PR-B: MissionRunner) and proving it with Employee #2.

**Session 1254 PRs (all admin-merged given Anthropic billing CI gap):**

| PR | Type | Scope | Merge SHA |
|---|---|---|---|
| [#2733](https://github.com/clwest/donkey-betz-platform/pull/2733) | fix | Register `rigby_documentation_manager_daily` for worker boot (`app.conf.imports`) | `475bbe5f` |
| [#2734](https://github.com/clwest/donkey-betz-platform/pull/2734) | feat | `employee_tool action=status` + `evidence_for_mission` (read-only) | `7e5209b5` |
| [#2735](https://github.com/clwest/donkey-betz-platform/pull/2735) | feat | Documentation Manager shift-report DM into `/inbox` | `771023df` |
| [#2736](https://github.com/clwest/donkey-betz-platform/pull/2736) | feat | Generalize shift-report comms + `EMPLOYEE_OS_PRIMITIVES.md` | `4b941a68` |
| [#2737](https://github.com/clwest/donkey-betz-platform/pull/2737) | docs | Session 1254 close handoff | _(this commit)_ |

**Headline outcomes:**

- **All 4 substantive PRs Rigby-SIGNed before merge** via the plan-route-amend pattern.
- **59 new tests; 190/190 in 3.9s on real PostgreSQL** across the employee suite at session close.
- **Documentation Manager is live end-to-end:** beat schedule registered, worker dispatch verified, status + evidence read APIs returning correct shapes for both the worker-path success (`02480a34-…`) and the failure-injection (`eab1accc-…`), shift-report DM landing in the persistent inbox thread `d24e5e7a-…`.
- **Comms is now employee-agnostic:** `post_shift_report(employee, job, mission, …)` accepts any AIEmployee+JobContract pair; docs-specific config is in `core/employees/comms_docs_manager.py`.
- **First untouched beat fire:** Tue 2026-06-30 06:30 MDT = 12:30 UTC.

### FIRST THING Session 1255

**Do not** start any new architecture before re-reading [`docs/EMPLOYEE_OS_PRIMITIVES.md`](docs/EMPLOYEE_OS_PRIMITIVES.md). The anti-duplication matrix names every "do not build" model (`EmployeeMessage`, `ApprovalQueue`, `TrustScore`, `MissionRun`, `EmployeeNotification`, `EmployeeHistory`, `EmployeeStatus`) — if you find yourself wanting one of those, you've missed the canonical primitive.

#### Priority 0 — Tuesday 06:30 first untouched beat fire watch

When Tue 2026-06-30 06:30 MDT (12:30 UTC) hits, verify that the now-registered task runs end-to-end on its own:

```python
from core.models_ops_runs import OpsRun, OpsRunEvent
from core.models_messaging import DirectMessage
from datetime import datetime, timezone as dt_tz
lo = datetime(2026, 6, 30, 12, 29, tzinfo=dt_tz.utc)
hi = datetime(2026, 6, 30, 12, 35, tzinfo=dt_tz.utc)
run = OpsRun.objects.filter(
    domain='mission', run_kind='docs_cascade',
    started_at__gte=lo, started_at__lte=hi,
).order_by('-started_at').first()
assert run is not None, 'Tue 06:30 beat fire produced no OpsRun'
assert run.triggered_by == 'beat'
# Shift-report DM should be created too:
dm = DirectMessage.objects.filter(metadata__mission_id=str(run.id)).first()
assert dm is not None, 'Tue 06:30 mission produced no shift-report DM'
print(f'  run.id={run.id}  status={run.status}  verdict={(run.summary or {}).get("verdict")}')
print(f'  DM.id={dm.id}  body={dm.body[:80]}')
```

If anything fails: the registration hotfix (#2733) shape or the shift-report wiring is broken; read `celery.log` for `unregistered task` errors and check `_existing_mission_for_today` against the run's UTC vs. local timezone semantics.

#### Priority 1 — PR-B: MissionRunner extraction

**Recommended next architectural milestone** per the S1254 handoff §4.

**Goal:** extract the reusable employee lifecycle from
`core/tasks_documentation_manager.py` into a `MissionRunner` class
that owns mission creation, OpsRun lifecycle, step event emission,
summary accumulation, verdict emission, idempotency, escalation
hooks, and shift-report dispatch. Documentation Manager becomes the
first MissionRunner implementation.

**Hard rules:**

- **No new `MissionRun` model.** `OpsRun(domain='mission')` IS the MissionRun. EMPLOYEE_OS_PRIMITIVES.md §2 names this explicitly.
- **No new `EmployeeAuditLog`.** Reuse OpsRunEvent + DeliverableEvent + LLMCallEvent + ToolCallRecord.
- **No new PA tool.** `employee_tool` covers describe / run_now / status / evidence_for_mission.
- **MissionRunner does NOT own:** LLM execution, step semantics, business logic. Those stay in the job module.
- **Behavior preserved exactly** — every existing docs-manager test must pass through the extracted runner.

**Concrete shape (working sketch from S1254 §4 — Rigby sign-off required before code):**

```python
class MissionRunner:
    def __init__(self, *, employee, job_contract, shift_report_fn):
        ...

    def run(self, *, step_fns: Sequence[Callable]) -> MissionRunResult:
        """
        Execute steps in order, recording OpsRunEvent boundaries.
        On step failure, halt + emit rejected verdict + call shift_report_fn.
        On all-steps-pass, emit certified verdict + call shift_report_fn.
        Returns a normalized result; never raises.
        """
```

**Process (mirror S1254's Rigby-SIGN cadence):**

1. Open a discovery deliverable through Rigby identifying every distinct piece of `tasks_documentation_manager.py` that belongs to "lifecycle" vs. "job semantics."
2. Route the proposed `MissionRunner` API + extraction plan through Rigby for SIGN-WITH-EDITS before any code.
3. Implement as a refactor PR (no behavior change). All existing tests must pass.
4. Open a second PR that re-derives the docs-cascade flow through the runner (no behavior change but proves the seam).

#### Priority 2 — Employee #2 implementation (after PR-B lands)

Per S1254 §5. **Candidates:** StockAuditCoordinator, COOAgent.

**Goal:** prove a second employee reuses the lifecycle with only:
1. New `AIEmployee` + `JobContract` in `core/employees/jobs.py`
2. New `core/tasks_<job>.py` (registered in `app.conf.imports` — see S1253 #2733 lesson)
3. Job-specific step functions
4. Optionally a thin `core/employees/comms_<job>.py` if a tuned body template is needed

If Employee #2 needs any new model, PA tool, queue, or admin UI — **stop and re-read `EMPLOYEE_OS_PRIMITIVES.md` §2 + §4**.

#### Priority 3 — Carryover and watch items

| Item | Source | Severity |
|---|---|---|
| ~~PR 1.3 candidate: replace docs-cascade closure-capture with `PostflightContext`~~ — **RESOLVED** by PR 1.3 (Session 1256). See Tracked Seam Debt block below for historical context. | PR #2739 → PR 1.3 | resolved |
| Authority enforcement (JobContract.authority is policy, not enforced) | S1254 §3 | medium |
| Notification channel abstraction (push + WebSocket "DM arrived" event) | PR #2735 §"What's NOT" | low |
| Mobile messaging screen | PR-4 discovery report | low |
| `RIGBY.primary_chat_id` contract constant still points at stale `pa-3901b70e61934df7` (env override active; cosmetic) | S1252 carryover | low |
| `auto-archive-stale-deliverables` interaction with publish_candidate escalation deliverables (window may eat them prematurely) | S1252 carryover | low |
| Pre-existing failing test `test_every_route_pattern_matches_a_registered_task` (orphan `content.*` route) | S1253 #2733 PR description | low |
| `Deliverable.create` defaults-to-completed upstream fix | S1252 carryover | low |
| `feedback_docs_pipeline_4_step_cascade.md` memory rule update — point at the new daily-read surface (`employee_tool action=status` + shift-report DM) | S1254 deferred | low |

#### Tracked seam debt — PR 1.3 candidate (RESOLVED)

> **Status: RESOLVED in PR 1.3 (Session 1256).** The block below is
> preserved for historical context — it explains why the closure-
> capture pattern appeared in PR 1.2 and what PR 1.3 replaced it with.
> If `PostflightContext` ever grows additional fields, refer back to
> the "Intended PR 1.3 API" section to keep the original constraints
> in view.

**Replace Documentation Manager closure-capture workaround with
MissionRunner postflight context carrying the mission row.**

**Why this exists.** PR #2739 (Session 1256 PR 1.2) migrated the
Documentation Manager onto MissionRunner. MissionRunner's
`postflight_fn(passed, summary_acc)` signature does **not** receive
the mission row. The docs cascade needs the mission row in postflight
to emit two custom timeline events the runner can't emit on its own:

- `step_5_drift_observed` (singular info event on success)
- `step_5_skipped` (singular info event on failure)

PR 1.2 worked around this **without modifying MissionRunner's public
contract** by stashing the mission inside a `_make_mission_capturing_step`
wrapper into a per-runner `mission_holder` dict that the postflight
closure reads. The workaround has fail-loud guards (postflight raises
`RuntimeError` if the holder is empty; step wrapper raises if mission
is `None`) and per-runner isolation tests, but it's still a workaround.

**Intended API shape (PR 1.3).** Replace the closure dance with an
explicit context object:

```python
@dataclass(frozen=True)
class PostflightContext:
    mission: OpsRun          # the mission row, populated by the runner
    passed: bool             # final cascade-step outcome
    summary_acc: dict        # mutable accumulator (caller may mutate)

# MissionRunner constructor signature evolves:
postflight_fn: Optional[Callable[[PostflightContext], None]] = None

# Backwards compatibility: detect 2-arg vs 1-arg via inspect.signature
# at constructor time. 2-arg callers (today's shape) get a shim that
# unpacks (passed, summary_acc) from the context. New callers receive
# the context directly. This lets PR 1.3 land without forcing every
# job to migrate in lockstep.
```

**Acceptance for the follow-up PR:**
- New `PostflightContext` dataclass in `core/employees/mission_runner.py`
- `postflight_fn` accepts either the new 1-arg shape or the legacy
  2-arg shape (detected via `inspect.signature`)
- `core/jobs/docs_cascade.py` migrates: postflight reads
  `ctx.mission` instead of `mission_holder.get("mission")`
- `_make_mission_capturing_step` deleted; `mission_holder` deleted
- Same tests in `test_docs_manager_migration.py::EventLabelOrderPreservationTests`
  still pass verbatim
- `test_docs_manager_migration.py::ClosureCaptureSafetyTests` is
  renamed and updated to test the new context shape
- MissionRunner gains a 1-2 line contract test that PostflightContext
  is passed and that the legacy 2-arg signature still works

**Where the workaround lives today (so PR 1.3 knows the surface):**
- `core/jobs/docs_cascade.py:583-606` — `_make_mission_capturing_step` wrapper
- `core/jobs/docs_cascade.py:626-668` — `_make_postflight` factory + fail-loud guard
- `core/jobs/docs_cascade.py:735` — `mission_holder` allocation in `build_docs_manager_runner()`
- `core/tests/test_docs_manager_migration.py::ClosureCaptureSafetyTests` — 5 safety tests covering the workaround
- `core/employees/mission_runner.py` — **unchanged in PR 1.2**; PR 1.3 modifies the runner

#### What NOT to do

- **Don't introduce new core models** for any of: `EmployeeMessage`, `ApprovalQueue`, `TrustScore`, `MissionRun`, `EmployeeNotification`, `EmployeeHistory`, `EmployeeStatus`. The anti-duplication matrix in `EMPLOYEE_OS_PRIMITIVES.md` §2 names each substitute.
- **Don't invent new PA tools per employee.** `employee_tool` is the canonical surface.
- **Don't persist trust math.** Trust ratio + status are derived on read by `employee_tool action=status`. Persisting them makes policy changes (e.g., changing the under-review threshold from 3 to 5) impossible without backfill.
- **Don't flip the Session 1250 flags** (`RIGBY_EVENT_INTAKE_ENABLED` et al.) yet. The "stop building toward a richer pipeline" rule still applies.
- **Don't restart all celery workers** unless something is actually broken. PA worker needed restart this session for the schema enum change; that's the only kind of trigger.
- **Don't `rm` `docs/INDEX.md`** if it shows up uncommitted — it's auto-regenerated cascade output and the daily beat run regenerates it.
- **Don't enable `MESSAGING_TOOL_ALLOW_SEND`** without an explicit reason; free-form LLM outbound messaging is OFF by design in v0.

---

## SESSION 1251 — PRIOR ENTRY POINT (preserved for context)

### SESSION 1250 CLOSED — 11 PRs shipped + Session 1251 opens with capability audit

**Session window:** 2026-06-28 Sunday (~all day, multiple PA arcs).
**Full audit handoff:** [`SESSION_1251_CAPABILITY_AUDIT.md`](docs/handoffs/SESSION_1251_CAPABILITY_AUDIT.md).
**Pipeline handoffs:** [`SESSION_1250_PR10_LOCAL_INTAKE_EXERCISE.md`](docs/handoffs/SESSION_1250_PR10_LOCAL_INTAKE_EXERCISE.md) + [`SESSION_1250_PR11_LOCAL_WORK_QUEUE_EXERCISE.md`](docs/handoffs/SESSION_1250_PR11_LOCAL_WORK_QUEUE_EXERCISE.md).

**TL;DR — Session 1250:** Built the full Rigby Event Intake → Mission Delegation pipeline across 11 PRs (#2716 → #2726). All four runtime flags default OFF. Net production behavior change: zero. Locally exercised through Stage 2 (intake → MissionRun → RigbyWorkItem). All 199 tests green. **Pipeline is code-complete, production-dormant.**

**Session 1250 PRs (all admin-merged given Anthropic billing CI gap):**

| PR | Type | Scope | Tests |
|---|---|---|---|
| [#2716](https://github.com/clwest/donkey-betz-platform/pull/2716) | docs | Event inventory | — |
| [#2717](https://github.com/clwest/donkey-betz-platform/pull/2717) | feat | platform_event_view (read API) | 30 |
| [#2718](https://github.com/clwest/donkey-betz-platform/pull/2718) | feat | OpsRun MissionRun fields | 20 |
| [#2719](https://github.com/clwest/donkey-betz-platform/pull/2719) | feat | rigby_event_intake dry-run task | 38 |
| [#2720](https://github.com/clwest/donkey-betz-platform/pull/2720) | feat | DeliverableEvent subscriber | 13 |
| [#2721](https://github.com/clwest/donkey-betz-platform/pull/2721) | feat | RigbyWorkItem internal queue | 18 |
| [#2722](https://github.com/clwest/donkey-betz-platform/pull/2722) | feat | Work-queue review tools | 30 |
| [#2723](https://github.com/clwest/donkey-betz-platform/pull/2723) | feat | Mission Delegation | 25 |
| [#2724](https://github.com/clwest/donkey-betz-platform/pull/2724) | feat | Local observation harness | 25 |
| [#2725](https://github.com/clwest/donkey-betz-platform/pull/2725) | docs | PR 10 intake exercise handoff | — |
| [#2726](https://github.com/clwest/donkey-betz-platform/pull/2726) | docs | PR 11 work queue exercise handoff | — |

**Headline outcomes:**

- **199 tests across the PR 2-9 pipeline**, all green in 7.73s on real PostgreSQL.
- **Four feature flags, all default OFF:** `RIGBY_EVENT_INTAKE_ENABLED`, `RIGBY_INTERNAL_WORK_QUEUE_ENABLED`, `RIGBY_WORK_QUEUE_REVIEW_ENABLED`, `RIGBY_DELEGATION_ENABLED`. Composes to net-zero production change.
- **Local Stage 1 + Stage 2 exercises** verified the pipeline end-to-end. 3 transitions → 3 MissionRuns + 2 RigbyWorkItems exactly as specified.
- **Capability audit** (Session 1251) concluded: the platform is over-served for current operator habits. Recommendation: stop building toward a richer pipeline. Start handing Rigby existing daily jobs.

### FIRST THING Session 1251

**Do not** open the next pipeline-stage PR. The recommendation from the Session 1251 capability audit is:

> Transition from infrastructure construction to operational capability.

**PR 12 — Rigby's Morning Brief** is the first operating-capability job Rigby owns.

#### Objective (PR 12)

Give Rigby her first recurring operational job — a daily concise operating brief for Chris.

The brief should answer:
- What changed since yesterday?
- Is the platform healthy?
- Are workers / queues / costs / alerts okay?
- Is the active session healthy?
- Do we need a fresh session?
- Are there new audit findings?
- Are any queues stuck?
- What should Chris focus on first today?

#### Architectural rules (hard)

- **No new infrastructure** unless discovery proves a small wrapper is required.
- **Use existing tools only.** Bundle: `context-kit orient` (or equivalent), `session_tool.health_check`, `ops_digest_tool.generate`, `cockpit_tool.worker_health`, `platform_config_tool` (feature flags), `audit_tool.findings`, `cockpit_tool.queue_lengths`, `cost_telemetry_tool` summary if cheap, `recent_activity_tool` if useful.
- **No new models. No new event system. No new agent orchestration. No LLM-heavy output. No human notification system beyond posting/saving the brief where Rigby already operates. No automatic PR creation. No automatic delegation.**

#### Implementation sequence

- **PR 12A** — `rigby_morning_brief` tool or management command, **manually runnable**. Discovery-led — confirm which existing tools should be bundled before writing code. Output format must be short (executive-summary first, readable in under 60 seconds), structured as:
  1. Today's top priority
  2. Platform health
  3. Active risks
  4. What changed
  5. What not to work on
  6. Suggested next action

- **PR 12B** — schedule daily beat **only after manual validation in PR 12A.**

#### First-move discovery (before any code)

Before writing PR 12A code, the session should answer:

1. Which existing tools cover each of the 7 questions the brief should answer?
2. Where should the brief be saved/posted? (PA conversation? deliverable? both?)
3. Should it start as a PA tool (Rigby invokes from chat) or a management command (operator invokes from shell)?
4. What's the exact bundled payload shape?
5. What does the "under 60 seconds to read" output look like?

The audit handoff §4 (top-20 opportunities) and §5 (recommendation) frame the answer.

#### Acceptance criteria (PR 12A)

To be confirmed during discovery, but starting hypothesis:

1. Single command/tool invocation produces the brief in < 5 seconds.
2. Brief output is < 1200 characters in the human-readable view.
3. Reuses ≥ 5 existing PA tools; introduces ≤ 50 lines of new code.
4. No new model, no migration, no new feature flag.
5. Side-effect-free (read-only) — does not mutate state.
6. Has at least one real-DB integration test that calls it end-to-end and asserts the 6-section output structure.
7. Handles the "all four S1250 flags OFF" case gracefully (most fields populated; queue-related fields show "queue disabled").

#### Reading order for Session 1251 open

1. This `00-START-NEXT-SESSION.md`.
2. `docs/handoffs/SESSION_1251_CAPABILITY_AUDIT.md` — full audit.
3. `docs/EVENT_SYSTEM_INVENTORY.md` §16 + §17 + §18 — what the harness + Stage 1 + Stage 2 exercises proved.
4. PR 12 discovery (run before any code).

---

### SESSION 1249 CLOSED — P1 morning_brief verified green; parity menu (a) + (b) shipped end-to-end

**Session window:** 2026-06-28 Sunday morning CDT (~3h).
**Full handoff:** [`SESSION_1249_P1_GREEN_PLUS_PARITY_MENU_AB_SHIPPED.md`](docs/handoffs/SESSION_1249_P1_GREEN_PLUS_PARITY_MENU_AB_SHIPPED.md).

**TL;DR:** Executed the S1248-named local↔prod parity menu top-2. P2(b) wrapper-trap fix + P2(a) server `/api/db-health-rpc/` + P2(a) client `env='prod'` selector all shipped + admin-merged + live-verified end-to-end. Loopback round-trip (client → local server, acting as 'prod') returned real DB result tagged `env='prod'` in 289ms with every expected field present. P3 char-training retirement is now technically unblockable — needs only `PA_DB_HEALTH_RPC_TOKEN` set in Railway prod env to flip the capability live.

**PRs shipped (3, all admin-merged given Anthropic billing CI gap):**

| PR | SHA | Subject | Net | Merge SHA |
|---|---|---|---|---|
| [#2712](https://github.com/clwest/donkey-betz-platform/pull/2712) | `f74b76c5` | `pa_chat.py` default flipped to local + `--env prod` opt-in | +124/-2 + commit metadata | `77bbdec8` |
| [#2713](https://github.com/clwest/donkey-betz-platform/pull/2713) | `b5af4202` | server `/api/db-health-rpc/` endpoint + middleware exemption | +355/-0 | `1a8c2c6c` |
| [#2714](https://github.com/clwest/donkey-betz-platform/pull/2714) | `ee44d848` | client `db_health_tool env='prod'` selector + schema | +430/-0 | `3fce425b` |

**Headline outcomes:**

- **Wrapper-trap closed.** Bare `python tools/pa_chat.py "msg"` now hits LOCAL. `--env prod` opts in with stderr warning. Memory rule `feedback_pa_chat_local_override.md` updated to reflect post-fix state.
- **Cross-env prod-query capability shipped.** Local Rigby can now (when Railway prod env var is set) call `db_health_tool action=verify_table table_name=<x> env=prod` and get a real answer programmatically.
- **34 new tests added** across 3 PRs, all green. No regression on existing tests post-`_handle_db_health` refactor.
- **P1 morning_brief 2026-06-28 verified green** at S1249 open via runbook deliverable `421eeaca-…`. All 6 assertions pass.

### FIRST THING Session 1250

#### Priority 0 — Pin health check

`pa-e8999a1793f04e23` (S1249 pin). Estimated ~14-16 turns at S1249 close — light. Run `session_tool action=health_check conversation_id=pa-e8999a1793f04e23` at S1250 open. PR #2707 + #2709 fixes mean rotation is one tool call away if `suggest_fresh` returns; carry-forward auto-seeds via `create_fresh starter_prompt`.

#### Priority 1 — Decide P2 menu (c)/(d) vs P3 char-training

**Branch point depends on whether Chris has flipped the prod env var:**

**Path A — Chris has set `PA_DB_HEALTH_RPC_TOKEN` on Railway prod:**
- **P3 char-training retirement** becomes the high-value pick. First action:
  - Export `PA_DB_HEALTH_RPC_URL=https://donkey-betz-platform-production.up.railway.app/api/db-health-rpc/` + `PA_DB_HEALTH_RPC_CLIENT_TOKEN=<same value Chris set on prod>` in local shell.
  - `make restart` (PA worker reloads with vars).
  - Ask Rigby: `db_health_tool action=verify_table table_name=core_fleetservicekey env=prod` — answers the gating P3 question programmatically.
  - Then sequence the reachability map in deliverable `c5ea2f61-…` (16 CharacterModel-importing files, risk-graded LOW/MED/HIGH).

**Path B — No prod env var change yet:**
- **P2(d) `make env-diff` mgmt cmd** — substantive work that doesn't depend on prod-side prereqs. Reads local config + Railway API + diffs. ~2h estimated.
- OR **P2(c) env-parity probe beat task** — daily canned health checks across both envs. Land it dormant, activate when (a) is live in prod.
- OR audit-domain pick (P6).

#### Priority 2 — Token follow-up PR (deferred from #2712)

Tiny PR to split `PA_API_TOKEN` ambiguity (`.env` value is prod). Options:
- Add `PA_LOCAL_TOKEN` env var convention + `_get_token()` env-aware resolution.
- OR strict: require `PA_API_TOKEN` to match `--env` choice (warn if mismatch).

Estimated ~30 lines + tests. Closes the remaining half of the wrapper-trap.

#### Priority 3 — Pre-existing carryover tail

- Finding 3 (workspace_tool counter decoupling) — investigate `core/models_workspace*.py` + `core/services/workspace_*.py` for `total_files_written` increment paths
- Section 5B verification — grep `autopilot_tool.drift_scan` and `diagnostics_tool.schema_handler_diff` to verify they exist + work
- `pa-2bb73c969fd24802` 26→29 turn growth despite rotation — find what's still writing to the retired thread
- Smoke-harness mode inconsistency (Session 1231 F5, LOW-MEDIUM)
- Smoke-probe tagging for AgentExecution (Session 1231 F1 / R2 REC-2)
- Promote `scripts/smoke_all_agents.py` → mgmt cmd (Session 1231 F6)
- Audit `5318da3e-…` §R2 amendment (Session 1231 F3, P3)
- Engineer workspace staleness (Session 1230 F3, MEDIUM)
- Fleet-smoke wall-clock timeouts (Session 1231 F2 / R2 REC-3, LOW)
- 80 spiders audit (last Session 1205)
- 30 advisors audit (last Session 1208)
- 9 body systems audit
- 144 Discord commands audit
- 7 fleet sibling apps at localhost:8002-8008
- Workspace leak watch (`cf708a2e-…`) "real fix" investigation
- P5 S1115 #12 deferred list re-audit (~2026-07-13 telemetry-valid window)
- Anthropic credit refill at https://console.anthropic.com/billing — all 3 S1249 PRs admin-merged because lint CI didn't run

#### Priority Last — Whatever Chris wants

S1249 was a productive 3-PR Sunday morning. The local↔prod parity theme moved from "named" to "half-shipped end-to-end." Choice point at S1250 is the prod-env-var question above: if Chris flipped it, P3 char-training unblock is the obvious next pick.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**

- Delete the 9 dormant agent class files (deferred since Session 1222)
- Tier 3 from P2 deliverable `7ae61cf7-…`
- The 11 AUDIT_FINDINGS.md #12 deferred-by-policy tasks (each needs Chris green-light per #12 protocol)

---

### SESSION 1248 CLOSED — P2a + P2b shipped, P2c deferred, local↔prod parity named as a theme

**Session window:** 2026-06-27 Saturday late-evening CDT (continuous from S1247 close).
**Full handoff:** [`SESSION_1248_P2A_P2B_SHIPPED_PLUS_LOCAL_PROD_PARITY_THEME_NAMED.md`](docs/handoffs/SESSION_1248_P2A_P2B_SHIPPED_PLUS_LOCAL_PROD_PARITY_THEME_NAMED.md).

**TL;DR:** S1247 PA tool gap audit top-3 sprint executed cleanly — P2a + P2b shipped + live-verified, P2c routed through Rigby + deferred (her pick C; second-choice B). Late-session reframe: Chris named **local↔prod parity** as the deeper pattern behind multiple recent friction points and asked whether it's solvable. Recorded position: full parity is the wrong goal, but observability + parity-detection gaps are solvable in pieces. Concrete leverage points captured in the handoff for S1249+ to pick from.

**PRs shipped (both admin-merged given Anthropic billing CI gap):**

| PR | SHA | Subject | Net | Merge SHA |
|---|---|---|---|---|
| [#2709](https://github.com/clwest/donkey-betz-platform/pull/2709) | `cf7b2693` | session_tool retire/set_active/seed + dispatcher gate | +637/-4 | `761d68d6` |
| [#2710](https://github.com/clwest/donkey-betz-platform/pull/2710) | `458d375f` | deliverable_tool.create status echo + return_detail opt-in | +227/-1 | `c4532362` |

**Headline outcomes:**

- **Closes ~$3.60/day stale-thread dispatch waste audit** — S1212 deliverable `777d9cd8-…` AC-1/AC-2/AC-3 all structurally satisfied. Conversation_action_dispatcher now session_active-gated; LLM-supplied `retire`/`set_active`/`seed` actions exposed to Rigby.
- **Closes verify-then-set_status round-trip** — `feedback_deliverable_create_defaults_to_completed.md` root cause closed by PR #2710's top-level `status` echo. `return_detail=true` opt-in covers the verbose case.
- **Both PRs live-verified via Rigby post-bounce + ORM cross-checked.** Verifier-loop held: every Rigby-reported field confirmed against ORM. Step-4 currently-bound gate proved no-row-leakage (14/14 rows still active after blocked retire attempt).
- **PA tool gap audit deliverable `6b5570c2-…` top-3 sprint:** 2 of 3 SHIPPED (P2a, P2b); 1 DEFERRED (P2c) per Rigby pick.
- **New session theme named:** local↔prod parity (see § "S1249 priority queue" below).

### FIRST THING Session 1249

#### Priority 0 — Pin health check

`pa-3901b70e61934df7` (S1247 pin, continued through S1248). Estimated 22-26 turns at S1248 close. Run `session_tool action=health_check conversation_id=pa-3901b70e61934df7` at S1249 open — Finding 1 fix from PR #2707 means the explicit conversation_id is honored. If `suggest_fresh` returns or score drops below 60, rotate via `session_tool.create_fresh` + edit `tools/pa_local.sh` line 70.

#### Priority 1 — 06-28 morning_brief CUMULATIVE verification (TIME-BOUND, ~13:00 UTC Sunday = 07:00 MDT)

**Use Rigby's runbook deliverable `421eeaca-fab8-4753-bd11-33a9b831ee96`** — pre-staged with the full Python verification block, pre-flight checklist, post-fire scrub regexes, and the cf708a2e workspace leak watch. Unchanged from S1247/S1248 carryover.

Quick-recall summary of the verification block (canonical version is in the deliverable):

```python
from core.models import CeleryTaskEvent
from core.models_deliverables import Deliverable
from datetime import date
import re

today = date(2026, 6, 28)

ev = CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
    started_at__date=today,
).order_by('-started_at').first()
assert ev and ev.status == 'SUCCESS'

d = Deliverable.objects.filter(
    user__username='chris', category='Morning Brief',
    created_at__date=today,
).order_by('-created_at').first()
assert d
assert not str(d.workspace.id).startswith('cf708a2e'), "cf708a2e leak regression"

c = d.content
bare = len(re.findall(r'(?<!\[)\bMUSCULAR\b(?!\])', c))
assert bare == 0
absolute_hits = re.findall(r'by\s+\d{1,2}:\d{2}\s+(AM|PM)\s+(MDT|MST)', c, re.IGNORECASE)
assert not absolute_hits

from core.models import LegacySpiderData
assert LegacySpiderData.objects.count() >= 8170
```

#### Priority 2 — Pick from the local↔prod parity leverage menu (NEW theme, S1248 named)

Late-session S1248 Chris reframe + recorded position: full parity is NOT the right goal (prod has real data/traffic by design), but observability + parity-detection gaps are solvable in pieces. Concrete leverage points, biggest payoff first — pick one:

(a) **P2c-B (RPC prod-side endpoint)** — single source for "is X populated in prod?" questions. Rigby's S1248 recommended target shape. One PR with prod-side `/api/db-health-rpc/` view + auth check + local-side `db_health_tool` env=prod selector that calls it. Unblocks P3 (FleetServiceKey question) programmatically. Estimated 2 natural PRs (server + client) totaling ~150 lines.

(b) **Wrapper-trap cleanup** — `pa_chat.py` defaulting to prod URL is the #1 footgun. This session alone Chris/Claude were bitten twice. Flip default to local, require explicit `--env prod` for prod calls. Tiny PR (~20 lines + a test that asserts defaults).

(c) **Env-parity probe** — daily beat task runs the same 5-7 canned health checks on both envs (depends on P2c-B), surfaces drift as a deliverable.

(d) **`make env-diff` mgmt cmd** — diffs config keys / migrations applied / Celery task list / PeriodicTask counts across local↔prod. Run when something feels off.

**What NOT to do:** seed prod data locally; write "prod-shape" tests pretending prod runtime state from local fixtures; try to make local Postgres identical to prod.

#### Priority 3 — content/char-training full retirement (UNBLOCKABLE via P2)

**Source of truth:** deliverable `c5ea2f61-…` reachability map (8,921 chars after S1247 deferral note). 16 CharacterModel-importing files grep-verified against current tree.

Unblock paths (any of):
- Chris runs `railway run python -c "from core.models import FleetServiceKey; print(FleetServiceKey.objects.count())"` and reports back
- Ship P2c-B above, then use the new tool to query prod programmatically
- Prod-side Rigby session (if accessible) runs the query

Once unblocked, sequence shortest-tail-first per the map. Risk-graded LOW (5 one-off tests + `content/character_training.py` dead code) / MED (`core/views_character_training.py` + URL routes at `core/urls.py:2920+`) / HIGH (`CharacterModel` table drop).

#### Priority 4 — Workspace leak watch (cf708a2e-…) "real fix" investigation

S1230 F2 / S1245 / S1246 F-bonus carryover. Active workspace at S1248 close: Donkey Betz (`b4503364-…`), NOT cf708a2e. Behavioral policy question (what should auto-re-pin look like?) + code change in `core/services/workspace_*.py`. Defer until pattern returns OR Chris wants to debate the auto-re-pin policy.

#### Priority 5 — S1115 #12 deferred list re-audit (~2026-07-13)

Re-run `audit_celery_zero_fire --days 30` once 30d telemetry accumulates for the first telemetry-valid zero-fire census. The S1246 P4 `--include-direct-calls` axis (PR #2694) provides per-task `direct=N` columns to radically reduce false positives.

#### Priority 6 — Pick next audit domain

Remaining menu after S1247 gap audit (PA tools) closed:
1. **Spider pipeline health** — 80 spiders / 41 categories / 1.14M SpiderItemHash rows.
2. **RAG / citation integrity** — search_docs corpus, retrieval gates, citation source verification.
3. **24/7 advisor system** — 30 functional advisors. Last full audit Session 1208.

#### Priority N — Pre-existing carryover tail

- Finding 3 (workspace_tool counter decoupling) — investigate `core/models_workspace*.py` + `core/services/workspace_*.py` for `total_files_written` increment paths
- Section 5B verification — grep `autopilot_tool.drift_scan` and `diagnostics_tool.schema_handler_diff` to verify they exist + work
- `pa-2bb73c969fd24802` 26→29 turn growth despite rotation — find what's still writing to the retired thread
- Smoke-harness mode inconsistency (Session 1231 F5, LOW-MEDIUM)
- Smoke-probe tagging for AgentExecution (Session 1231 F1 / R2 REC-2)
- Promote `scripts/smoke_all_agents.py` → mgmt cmd (Session 1231 F6)
- Audit `5318da3e-…` §R2 amendment (Session 1231 F3, P3)
- Engineer workspace staleness (Session 1230 F3, MEDIUM)
- Fleet-smoke wall-clock timeouts (Session 1231 F2 / R2 REC-3, LOW)
- 80 spiders audit (last Session 1205)
- 30 advisors audit (last Session 1208)
- 9 body systems audit
- 144 Discord commands audit
- 7 fleet sibling apps at localhost:8002-8008
- Local FleetServiceKey count=0 (S1246 carryover — P2c-B or Chris manual check resolves)
- Anthropic credit refill at https://console.anthropic.com/billing — both #2709 and #2710 admin-merged because lint CI didn't run

#### Priority Last — Whatever Chris wants

S1248 was a productive 2-PR night that also surfaced a useful framing (local↔prod parity theme). P1 morning_brief verification is the one time-bound item for S1249. P2a/P2b throwaway artifacts (`pa-4b3f8a171a7b417c` test thread + 2 deliverables `60407d89-…` ready / `007e5a3c-…` completed in Donkey Betz) are discardable cleanup if you want zero noise — totally optional.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**

- Delete the 9 dormant agent class files (deferred since Session 1222)
- Tier 3 from P2 deliverable `7ae61cf7-…`
- The 11 AUDIT_FINDINGS.md #12 deferred-by-policy tasks (each needs Chris green-light per #12 protocol)

---

### SESSION 1247 CLOSED — PA tool gap audit + 2 findings fixed + P2 deferred

**Session window:** 2026-06-27 Saturday evening CDT.
**Full handoff:** [`SESSION_1247_PA_TOOL_GAP_AUDIT_PLUS_2_FINDINGS_FIXED_AND_P2_DEFERRED.md`](docs/handoffs/SESSION_1247_PA_TOOL_GAP_AUDIT_PLUS_2_FINDINGS_FIXED_AND_P2_DEFERRED.md).

**TL;DR:** S1247 opened on the S1246 carryover priority queue. P2 (content/char-training retirement) blocked early on a clarifying question Chris didn't have — `FleetServiceKey.count == 0` locally could be prod-only / dormant / never provisioned. Mid-session pivot: Chris asked us to audit all PA tools for gaps Rigby has hit. Self-report + Claude cross-check surfaced two fixable bugs on the session_tool surface. Those landed as PR #2707, were verified live via Rigby after a PA worker bounce.

**PR shipped (1, admin-merged):**

| PR | SHA | Subject | Net | Merge SHA |
|---|---|---|---|---|
| [#2707](https://github.com/clwest/donkey-betz-platform/pull/2707) | `e298a817` | session_tool conversation_id + create_fresh starter_prompt | +217/-29 | `b5d44430` |

**Deliverables produced (3, all Donkey Betz `b4503364-…`, all `status=ready`):**

| Deliverable | Purpose |
|---|---|
| `6103e35c-9914-4028-82cb-2866169d580e` | S1247 PA tool surface findings (3 bugs filed; 2 of 3 FIXED via #2707) |
| `6b5570c2-42e7-4580-b4ef-c768b67967c6` | S1247 PA tool gap audit (Rigby self-report + Claude cross-check, 15,174 chars) |
| `c5ea2f61-be21-4211-abd5-30d7c99983f7` | P2 retirement reachability map (appended deferral note, 8,921 chars) |

**Headline outcomes:**
- **2 of 3 PA tool findings actually FIXED + verified live (post-merge + worker bounce):**
  - Finding 1: `session_tool.health_check` honors explicit `conversation_id` (was unconditional override at `unified_pa_entrypoint.py:1765`)
  - Finding 2: `session_tool.create_fresh` uses `carry_forward_summary` as `starter_prompt` (handler was reading never-assigned `self._current_conversation_id`)
- **P2 deferred** — FleetServiceKey blocker documented in deliverable `c5ea2f61-…`. 16-file CharacterModel reachability map grep-verified against current tree.
- **Wrapper pin rotated** — `pa-2bb73c969fd24802` (S1246, 60/suggest_fresh) → `pa-3901b70e61934df7` (S1247 fresh).
- **PA worker bounced** — PID 21175 → 23545, new code picked up, both fixes verified via Rigby's tool surface.

**Open finding queue at S1247 close:**
- Finding 3 (workspace_tool `total_files_written: 0` despite `total_operations: 1429`) — deferred
- PA tool gap audit top-3 implementation sprint (deliverable `6b5570c2-…`)
- `00-START-NEXT-SESSION.md` lines 17-18 stale local-trap doc reference — superseded by today's update but a final audit pass may surface other stale refs
- `pa-2bb73c969fd24802` retired-thread turn growth (26→29 despite rotation) — minor follow-up
- Section 5B verification of `autopilot_tool.drift_scan` + `diagnostics_tool.schema_handler_diff` (deliverable `6b5570c2-…`)
- CI billing — 3 lint checks on PR #2707 didn't actually run because of GitHub Actions billing failure (Anthropic credit refill still pending). PR admin-merged anyway per the S1246 pattern.

### FIRST THING Session 1248

#### Priority 0 — Conversation health check

`pa-3901b70e61934df7` (S1247 pin) had light usage tonight — probably still green. Run `session_tool.health_check conversation_id=pa-3901b70e61934df7` at S1248 open. Now that the Finding 1 fix is live, the explicit `conversation_id` arg will be honored — no need to swap the wrapper pin to verify health on a specific thread.

#### Priority 1 — 06-28 morning_brief CUMULATIVE verification (TIME-BOUND, ~13:00 UTC Sunday = 07:00 MDT)

**Use Rigby's runbook deliverable `421eeaca-fab8-4753-bd11-33a9b831ee96`** — pre-staged with the full Python verification block, pre-flight checklist (celery worker / beat alive / long_running queue depth = 0), post-fire scrub regexes, and the cf708a2e workspace leak watch.

Quick-recall summary of the verification block (canonical version is in the deliverable):

```python
from core.models import CeleryTaskEvent
from core.models_deliverables import Deliverable
from datetime import date
import re

today = date(2026, 6, 28)

ev = CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
    started_at__date=today,
).order_by('-started_at').first()
assert ev and ev.status == 'SUCCESS'

d = Deliverable.objects.filter(
    user__username='chris', category='Morning Brief',
    created_at__date=today,
).order_by('-created_at').first()
assert d
assert not str(d.workspace.id).startswith('cf708a2e'), "cf708a2e leak regression"

c = d.content
bare = len(re.findall(r'(?<!\[)\bMUSCULAR\b(?!\])', c))
assert bare == 0
absolute_hits = re.findall(r'by\s+\d{1,2}:\d{2}\s+(AM|PM)\s+(MDT|MST)', c, re.IGNORECASE)
assert not absolute_hits

from core.models import LegacySpiderData
assert LegacySpiderData.objects.count() >= 8170
```

#### Priority 2 — PA tool gap audit implementation sprint (NEW — chosen from S1247 deliverable `6b5570c2-…`)

The S1247 gap audit produced a top-3 prioritized list. Cleanest order:

(a) **`session_tool` retire/set_active/seed actions** — smallest blast radius, biggest immediate ergonomic win. Closes Session 1212 `~$3.60/day waste` carryover on retired-thread dispatches. Single tool surface, three coherent additions. `session_tool.retire(conversation_id=…)` + `session_tool.set_active(conversation_id=…)` + a hardened `seed` action that can't return empty. Implementation file: `core/services/td_handlers_core.py` (around lines 3727-3866 for the existing actions). Schema: `core/services/pa_tool_schemas.py:4673-4717`.

(b) **`deliverable_tool.create return_detail` option** — lowest implementation cost of the three. Add an optional `return_detail=True` arg to the create handler that triggers a follow-up `detail` lookup before returning. Eliminates the verify-then-`set_status` round-trip pattern documented in `feedback_deliverable_create_defaults_to_completed.md`.

(c) **`db_health_tool` env selector OR new `prod_db_query_tool`** — biggest design Q (auth + allowlist + read-only enforcement). Recommend route options through Rigby BEFORE coding so the diff lands on a decision she's signed off on. Unblocks P3 (below) and every future "dormant locally vs live in prod?" check.

#### Priority 3 — content/char-training full retirement (DEFERRED, unblock cycle depends on P2c)

**Source of truth:** deliverable `c5ea2f61-…` reachability map (8,921 chars after S1247 deferral note). 16 CharacterModel-importing files grep-verified against current tree.

Unblock condition: prod-side FleetServiceKey verification. Either Rigby prod-side chat, Chris-mediated confirmation, OR (more general) shipping P2c above and using the new prod_db_query_tool to resolve the question programmatically.

Once unblocked, sequence shortest-tail-first per the map. Risk-graded LOW (5 one-off tests + `content/character_training.py` dead code) / MED (`core/views_character_training.py` + URL routes at `core/urls.py:2920+`) / HIGH (`CharacterModel` table drop).

#### Priority 4 — Workspace leak watch (cf708a2e-…) "real fix"

S1230 F2 / S1245 / S1246 F-bonus. At S1247 close the active workspace is Donkey Betz (`b4503364-…`), NOT cf708a2e-… — so this is not currently misbehaving. The "real fix" is a behavioral policy question (what should auto-re-pin look like?) plus a code change in `core/services/workspace_*.py`. Defer until the pattern returns OR until Chris wants to debate the auto-re-pin policy.

#### Priority 5 — S1115 #12 deferred list re-audit (~2026-07-13)

Re-run `audit_celery_zero_fire --days 30` once 30d telemetry accumulates for the first telemetry-valid zero-fire census. The S1246 P4 `--include-direct-calls` axis (PR #2694) means per-task `direct=N` columns are now available — should radically reduce false positives.

#### Priority 6 — Pick next audit domain

S1245 menu (PA tools audit completed via S1247 gap audit deliverable `6b5570c2-…` — strike from list):
1. **Spider pipeline health** — 80 spiders / 41 categories / 1.14M SpiderItemHash rows.
2. **RAG / citation integrity** — search_docs corpus, retrieval gates, citation source verification.
3. **24/7 advisor system** — 30 functional advisors. Last full audit Session 1208.

#### Priority N — Pre-existing carryover tail

- Finding 3 (workspace_tool counter decoupling) — investigate `core/models_workspace*.py` + `core/services/workspace_*.py` for `total_files_written` increment paths
- Section 5B verification — grep `autopilot_tool.drift_scan` and `diagnostics_tool.schema_handler_diff` to verify they exist + work before requesting a new schema/handler diff tool
- `pa-2bb73c969fd24802` 26→29 turn growth despite rotation — find what's still writing to the retired thread
- Smoke-harness mode inconsistency (Session 1231 F5, LOW-MEDIUM)
- Smoke-probe tagging for AgentExecution (Session 1231 F1 / R2 REC-2)
- Promote `scripts/smoke_all_agents.py` → mgmt cmd (Session 1231 F6)
- Audit `5318da3e-…` §R2 amendment (Session 1231 F3, P3)
- Engineer workspace staleness (Session 1230 F3, MEDIUM)
- Fleet-smoke wall-clock timeouts (Session 1231 F2 / R2 REC-3, LOW)
- 80 spiders audit (last Session 1205)
- 30 advisors audit (last Session 1208)
- 9 body systems audit
- 144 Discord commands audit
- 7 fleet sibling apps at localhost:8002-8008
- Local FleetServiceKey count=0 (S1246 carryover — still unanswered)

#### Priority Last — Whatever Chris wants

S1247 was a paperwork-heavy session that produced 1 small PR + 3 deliverables. P1 morning_brief verification is the only time-bound item for S1248. P2a (session_tool retire/set_active/seed) is the cleanest non-time-bound starting move. After P1 + P2, S1248 is wide open.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222)
- Tier 3 from P2 deliverable `7ae61cf7-…`
- The 11 AUDIT_FINDINGS.md #12 deferred-by-policy tasks (each needs Chris green-light per #12 protocol)

---

### SESSION 1246 CLOSED IN TWO PARTS

**Part 1 (morning/early evening) — S1245 carryover + content/ retirement Celery surface + fleet verification.** 7 PRs (#2692-#2695). Full handoff: [`SESSION_1246_S1245_BONUS_FINDINGS_CLOSED_PLUS_AUDIT_AXIS_PLUS_CONTENT_TASK_RETIREMENT_PLUS_FLEET_VERIFICATION.md`](docs/handoffs/SESSION_1246_S1245_BONUS_FINDINGS_CLOSED_PLUS_AUDIT_AXIS_PLUS_CONTENT_TASK_RETIREMENT_PLUS_FLEET_VERIFICATION.md).

**Part 2 (evening/late night) — 31-tab workspace audit + 6 lane fixes + 3 BROKEN tabs.** 8 more PRs (#2696-#2705). Full handoff: [`SESSION_1246_PART_2_WORKSPACE_TAB_AUDIT_AND_SLO_REMEDIATION.md`](docs/handoffs/SESSION_1246_PART_2_WORKSPACE_TAB_AUDIT_AND_SLO_REMEDIATION.md).

**Day total: 15 PRs merged + 4 ORM data fixes + 5 deliverables produced + 31 tabs audited + 3 BROKEN tabs fixed + 2 SLOs cleared/recovering.**

### Part 1 summary (unchanged from earlier close)

Session 1246 executed the S1245 P3/P4 carryover punch list + the S1246 P2 content/ retirement product-Q. Mid-session pivot to fleet-caller verification surfaced by Chris's "we might be deleting things we need because we didn't document the fleet apps properly" prompt — caught a documentation-gap risk before merging the deletion PRs. All 3 PRs cleared safe via Rigby runtime + Claude cross-repo ORM evidence and admin-merged at 22:53 UTC.

**PRs shipped (all admin-merged):**

| PR | SHA | Subject | Net | Merge SHA |
|---|---|---|---|---|
| [#2692](https://github.com/clwest/donkey-betz-platform/pull/2692) | `fbc77b81` | celery telemetry task_name + remove ghost task whitelist | +20/-5 | `57071592` |
| [#2693](https://github.com/clwest/donkey-betz-platform/pull/2693) | `cc9ab2c1` | delete dormant content/ char-training Celery tasks | +5/-211 | `1f1edabe` |
| [#2694](https://github.com/clwest/donkey-betz-platform/pull/2694) | `48e135e9` | audit_celery_zero_fire --include-direct-calls axis | +163/-1 | `660c6b5e` |

**Deliverables produced (both Donkey Betz workspace, b4503364-…, status=ready):**

| Deliverable | Purpose |
|---|---|
| `421eeaca-fab8-4753-bd11-33a9b831ee96` | S1246 P1 — 06-28 morning_brief verification runbook (3,479 chars) |
| `c5ea2f61-be21-4211-abd5-30d7c99983f7` | S1247 plan — content/ char-training full retirement reachability map (7,067 chars after fleet addendum) |

**Headline outcomes:**
- **S1245 P3.1 telemetry repr bug FIXED.** Shared `_extract_task_name(task, sender)` helper applied to all 3 Celery signal handlers (prerun, postrun, failure). 6/6 smoke cases incl. S1245 bug repro.
- **S1245 P3.2 ghost task RESOLVED.** `core.tasks.check_system_health` was never defined (`git log -S "def check_system_health" -- core/tasks.py` → zero hits); removed from PA's ALLOWED_TASKS whitelist. Stale QUEUED rows age out per `CELERY_TASK_EVENT_RETENTION_DAYS` (30d).
- **S1246 P2 surgical retirement SHIPPED.** Whole-file delete of `content/tasks.py` (3 dormant tasks) + `task_routes` entry removed. CharacterModel + 16-file chain queued for S1247 retirement plan.
- **S1246 P4 5th axis SHIPPED.** `audit_celery_zero_fire --include-direct-calls` automates the S1245 probe blind-spot manual step. Caught the exact blind-spot case in smoke (1 hit for `intelligence.tasks.process_pending_action_plans` in `core/celery.py:629`).
- **Fleet caller verification CLEAN.** 0 callers across 7 fleet repos + character-os + infra; 0 local FleetServiceKey rows ever; 0 authenticated FleetPAChatAuditRow matches ever; 0 FleetArtifact mentions of any of the 4 task names.

**Memory rule added:** `feedback_fleet_caller_verification_before_celery_deletes.md` — 3-axis sweep (cross-repo grep + Rigby runtime + ORM probe) before any Celery deletion PR merge; local-DB-only verdict has known prod blind spot.

**Subfinding queued for S1247 (workspace leak watch):**
`cf708a2e-…` (Session 1231 E2E sandbox) is still the active workspace despite S1230 F2 / S1245 flagging — rotation rule isn't auto-firing. Filed as S1246 F-bonus in the runbook deliverable.

### Part 2 summary

After Part 1 closed, Chris asked: *"Before we call it a night, do you and Rigby feel up to going through each tab in the workspace, verify it's real data and if it's actually working as intended?"* He noted *"if we have a high quality audit it might reshape the way we are running things like the test running in the morning."*

That framing was right. 8 PRs followed.

**PRs shipped in Part 2:**

| PR | Subject | Lane |
|---|---|---|
| [#2696](https://github.com/clwest/donkey-betz-platform/pull/2696) | Deliverables tab grouped view (recency + category accordions) | UI request |
| [#2697](https://github.com/clwest/donkey-betz-platform/pull/2697) | Move Deliverables work surface to top of tab | UI request (#2696 follow-up) |
| [#2698](https://github.com/clwest/donkey-betz-platform/pull/2698) | http_smoke_test auto-detect environment | PA tool gap |
| [#2699](https://github.com/clwest/donkey-betz-platform/pull/2699) | OperationsTab WorkspaceOperation import | BROKEN tab fix |
| [#2700](https://github.com/clwest/donkey-betz-platform/pull/2700) | FilesTab WorkspaceContext FK | BROKEN tab fix |
| [#2701](https://github.com/clwest/donkey-betz-platform/pull/2701) | PublishGate operational title patterns | F1 (publish_ready SLO) |
| [#2702](https://github.com/clwest/donkey-betz-platform/pull/2702) | http_smoke_test local auth | H (smoke_test auth) |
| [#2703](https://github.com/clwest/donkey-betz-platform/pull/2703) | base_agent intelligence_tool handler + telemetry hygiene | L (pa_tool SLO) |
| [#2704](https://github.com/clwest/donkey-betz-platform/pull/2704) | Sports agents no_data success pattern | K (45.7% agent success) |
| [#2705](https://github.com/clwest/donkey-betz-platform/pull/2705) | env-aware effective_root_path | G (broader root_path) |

**ORM data fixes (Part 2):**
- Donkey Betz `root_path` translated to local codebase
- 3 stuck SelfBlog test fixtures archived (F2)
- Catalyst blog archived (Chris decision)
- CodeGeneratorAgent unblocked (15-day Railway-specific block cleared)

**3 SLO breaches at Part 2 close:**
- `publish_ready_age_p95` — ✅ CLEARED (backlog=0 after Catalyst archive)
- `pa_tool_success_rate` — 🔄 Self-recovering (post-#2703 + 24h window roll)
- `celery_task_success_rate` — 🔄 Self-recovering (spider stale-worker failures rolling out)

**S1247 audit deliverable:** `1c3e63ec-0f30-425a-ad31-328e3de71e5f` — `S1247 workspace tab audit — RUNTIME VERIFICATION` (~14,000+ chars). 31 tabs catalogued + classified. All 3 BROKEN tabs fixed. 6 P1 untested-runtime tabs closed.

**Memory rules added in Part 2:**
- `feedback_stop_putting_chris_to_bed.md` — session-end summaries are status reports, not bedtime suggestions

**Chris-side carryover into Session 1247:**
- Anthropic credit refill at https://console.anthropic.com/billing — still failing CI billing
- All 15 day-PRs admin-merged
- 06-28 morning_brief CUMULATIVE verification time-bound to ~13:00 UTC Sunday = 07:00 MDT (now de-risked further by today's audit fixes)
- **Local fleet integration appears dormant** (0 active FleetServiceKey rows). Clarifying Q: are fleet keys prod-only? Worth answering before the S1247 model-layer retirement PR.

### FIRST THING Session 1247

#### Priority 0 — Conversation health check

`pa-2bb73c969fd24802` was at 100/continue/1 turn at S1246 mid-session pull, then accumulated turns through the multi-ask + content sweep + fleet verification round. Re-check health at S1247 open via `session_tool.health_check`. Likely still green (single coherent topic); fresh-start only if score drops below 60.

#### Priority 1 — 06-28 morning_brief CUMULATIVE verification (TIME-BOUND, ~13:00 UTC Sunday = 07:00 MDT)

**Use Rigby's runbook deliverable `421eeaca-fab8-4753-bd11-33a9b831ee96`** — pre-staged with the full Python verification block, pre-flight checklist (celery worker / beat alive / long_running queue depth = 0), post-fire scrub regexes, and the cf708a2e workspace leak watch.

Quick-recall summary of the verification block (canonical version is in the deliverable):

```python
from core.models import CeleryTaskEvent
from core.models_deliverables import Deliverable
from datetime import date
import re

today = date(2026, 6, 28)

ev = CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
    started_at__date=today,
).order_by('-started_at').first()
assert ev and ev.status == 'SUCCESS'

d = Deliverable.objects.filter(
    user__username='chris', category='Morning Brief',
    created_at__date=today,
).order_by('-created_at').first()
assert d
assert not str(d.workspace.id).startswith('cf708a2e'), "cf708a2e leak regression"

c = d.content
bare = len(re.findall(r'(?<!\[)\bMUSCULAR\b(?!\])', c))
assert bare == 0
absolute_hits = re.findall(r'by\s+\d{1,2}:\d{2}\s+(AM|PM)\s+(MDT|MST)', c, re.IGNORECASE)
assert not absolute_hits

from core.models import LegacySpiderData
assert LegacySpiderData.objects.count() >= 8170
```

#### Priority 2 — content/ char-training full retirement (the big one)

**Source of truth:** deliverable `c5ea2f61-…` — Rigby's S1247 reachability map (7,067 chars). It enumerates the 16 CharacterModel-importing files + URL wiring (live at `/api/characters/…`) + agent registration + fleet caller verification addendum.

**Before deleting anything:**
1. Ask Chris the open clarifying Q — is local FleetServiceKey count=0 because (a) keys are prod-only, (b) fleet went dormant locally, or (c) keys were never provisioned here? If (a), the runtime evidence in S1246's 3-axis sweep doesn't fully cover prod — need a Rigby prod-side check before any model-layer deletion.
2. Re-confirm with Rigby that the 2 training agents (`CharacterTrainingAgent`, `TrainedCreationAgent`) have ONLY fleet-smoke no-op executions (no real training runs). S1246 finding: their entire AgentExecution history was "Fleet smoke: return one-sentence receipt of capability."
3. Run `python manage.py audit_celery_zero_fire --include-direct-calls` (S1246 P4 axis, now merged) — confirm no surprise direct callers for the 2 agents' workflow tasks.

**Retirement scope (sequenced shortest-tail-first per the map):**
- Remove `core/views_character_training.py` URL patterns from `core/urls.py` (around line 2920+) — verify with a 404 smoke test
- Remove `core/views_character_training.py` import block from `core/urls.py` (around line 1312)
- Delete `core/views_character_training.py` itself
- Delete `core/views_image_helpers.py` import block + any view that requires CharacterModel
- Audit `core/epa_handlers_tools.py` for the CharacterModel import + remove dependent handlers
- Remove `CharacterTrainingAgent` + `TrainedCreationAgent` registrations + delete the agent class files
- Audit `ai_core/agents/brand_style_agent.py` for the CharacterModel reference (verify it's a soft reference, not a hard import)
- Delete `content/character_training.py`
- Delete `content/models.py CharacterModel` + run a forward-migration that drops the table (BackwardsCompatibility: leave 0014 forward-migration intact for audit history; new 03XX migration handles the drop)
- Delete 5 `tests/one-off/test_*character*.py` + `test_trained_*.py` files
- Decision deliverable update: set deliverable `c5ea2f61-…` status to `completed` when shipped

**Risk classification (per Rigby's map):**
- LOW — `tests/one-off/*`, `content/character_training.py` (only callers are the 3 deleted tasks)
- MED — `core/views_character_training.py` + URL patterns (live route surface; need to verify with curl/browser before pulling)
- HIGH — `CharacterModel` itself (Django migration, table drop)

#### Priority 3 — Workspace leak watch (S1246 F-bonus)

`cf708a2e-…` was active for the entire S1246 session despite S1230 F2 / S1245 having flagged it. Rotation rule isn't auto-firing. Two paths:

(a) **Quick fix** — Rigby explicit set: `workspace_tool action=set_active id=b4503364-2573-4401-9e28-61a739e0ce50`. Confirm it sticks. Single PA call, 2 min.

(b) **Real fix** — investigate why `cf708a2e-…` keeps re-activating. Check the rotation rule in `core/services/workspace_*.py` (whatever controls active-workspace state). Maybe write a beat task that re-pins to Donkey Betz if active workspace name contains "E2E" or "sandbox" or is older than N days.

Worth checking handoffs `SESSION_1230_*` + `SESSION_1231_*` for the original F2/F3 framing.

#### Priority 4 — S1115 #12 deferred list re-audit

Re-run `audit_celery_zero_fire --days 30` once 30d telemetry accumulates (~2026-07-13) for the first telemetry-valid zero-fire census. The S1246 P4 axis means the per-task `direct=N` column is now available — should radically reduce false positives.

#### Priority 5 — Pick next audit domain

S1245 menu (1 down: PA tools audit deferred again; rest unchanged):
1. **PA tools audit** — 109 schemas + 152 handlers + 8 enrichment services. Canonical protocol. Likely surfaces schema↔handler orphans + wrong-import patterns. 1-2 hr.
2. **Spider pipeline health** — 80 spiders / 41 categories / 1.14M SpiderItemHash rows.
3. **RAG / citation integrity** — search_docs corpus, retrieval gates, citation source verification.
4. **24/7 advisor system** — 30 functional advisors. Last full audit Session 1208.

#### Priority N — Pre-existing carryover tail

- Smoke-harness mode inconsistency (Session 1231 F5, LOW-MEDIUM)
- Smoke-probe tagging for AgentExecution (Session 1231 F1 / R2 REC-2)
- Promote `scripts/smoke_all_agents.py` → mgmt cmd (Session 1231 F6)
- Audit `5318da3e-…` §R2 amendment (Session 1231 F3, P3)
- Engineer workspace staleness (Session 1230 F3, MEDIUM)
- Meeting-context leak shape watch (Session 1230 F2 → now also S1246 F-bonus, see P3 above)
- Fleet-smoke wall-clock timeouts (Session 1231 F2 / R2 REC-3, LOW)
- 80 spiders audit (last Session 1205)
- 30 advisors audit (last Session 1208)
- 9 body systems audit
- 144 Discord commands audit
- 7 fleet sibling apps at localhost:8002-8008
- Local FleetServiceKey count=0 (S1246 carryover — answer prod-side first)

#### Priority Last — Whatever Chris wants

S1246 was a 3-PR execution + mid-session fleet pivot session. P1 morning_brief verification is the only time-bound item for S1247. Content/ retirement is the most actionable non-time-bound item. After P1 + P2, S1247 is wide open.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222)
- Tier 3 from P2 deliverable `7ae61cf7-…`
- The 11 AUDIT_FINDINGS.md #12 deferred-by-policy tasks (each needs Chris green-light per #12 protocol)

---

### SESSION 1245 CLOSED — P2 Celery connectivity audit + AUDIT_FINDINGS.md #12 framework re-validated + new `audit_celery_zero_fire` mgmt cmd

Full handoff: [`SESSION_1245_P2_CELERY_CONNECTIVITY_AUDIT_PLUS_AUDIT_FINDINGS_12_VALIDATION.md`](docs/handoffs/SESSION_1245_P2_CELERY_CONNECTIVITY_AUDIT_PLUS_AUDIT_FINDINGS_12_VALIDATION.md).

Session 1245 ran P2 from the S1244 close menu — telemetry-based dead-task analysis (S1244 Celery audit deferred-followup). Initial probe surfaced 14 "disconnected" Celery tasks; verify-before-delete sweep showed 11 of 14 were already documented as deferred-by-policy in `AUDIT_FINDINGS.md` §12 (S1115 audit). The audit's actual value was preventing a wrong deletion PR + re-validating the S1115 framework.

**PR shipped:**

| PR | Subject | Net |
|---|---|---|
| (new this session) | `core/management/commands/audit_celery_zero_fire.py` — runtime telemetry probe + KNOWN_DEFERRED filter | +210 |

**Audit deliverable:** `24ade5c4-7562-4905-80a1-bb901d0549d7` (Donkey Betz workspace, status=ready, 6,900 chars)

**Headline findings:**
- **Beat schedule health: PERFECT (90/90 enabled PeriodicTask rows fired in 14d window).** S1244 queue-parity canary is working.
- **Of 14 "disconnected" candidates:** 11 already in `AUDIT_FINDINGS.md` §12 deferred list, 1 probe false positive (direct-Python-caller blind spot), 2 net-new (`content/` character-training dormancy).
- **2 bonus telemetry findings:** repr bug (`task_name=str(task_obj)` instead of `task.name`), ghost task `core.tasks.check_system_health`.
- **0 tasks deleted** — verify-before-delete intervened.

**Memory rule added:** `feedback_audit_findings_12_canonical_celery_deferred_list.md` — cross-ref #12 before any Celery deletion + zero-fire telemetry horizon caveats.

**Chris-side carryover into Session 1246:**
- Anthropic credit refill at https://console.anthropic.com/billing — still failing CI billing
- S1245 PR pending admin-merge

### FIRST THING Session 1246

#### Priority 0 — Conversation health check
**Active conversation pinned in `tools/pa_local.sh`: `pa-2bb73c969fd24802`** ("S1246 — Morning Brief CUMULATIVE Verification (P1) + Follow-ups"). Rigby created it fresh at S1245 close (her own decision after self-noting topic spread widened from 2 → 4 across S1245). It's seeded with carry-forward summary: PR #2690 (`85598c28`), deliverable `24ade5c4-…` (ready, 6,900 chars, DBZ workspace), S1115 cross-ref policy, beat 90/90, S1246 menu. Previous conv `pa-1cb4915546654c78` was 95/continue/13 turns at wrap — safe but rotated proactively for crisp P1 thread.

#### Priority 1 — 06-28 morning_brief CUMULATIVE verification (TIME-BOUND, ~13:00 UTC Sunday = 07:00 MDT)

Validates 7+ PRs cumulatively from S1242-S1245 production paths.

```python
from core.models import CeleryTaskEvent
from core.models_deliverables import Deliverable
from datetime import date
import re

today = date(2026, 6, 28)

ev = CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
    started_at__date=today,
).order_by('-started_at').first()
assert ev and ev.status == 'SUCCESS'

d = Deliverable.objects.filter(
    user__username='chris', category='Morning Brief',
    created_at__date=today,
).order_by('-created_at').first()
assert d
assert not str(d.workspace.id).startswith('cf708a2e'), "cf708a2e leak regression"

c = d.content
bare = len(re.findall(r'(?<!\[)\bMUSCULAR\b(?!\])', c))
assert bare == 0
absolute_hits = re.findall(r'by\s+\d{1,2}:\d{2}\s+(AM|PM)\s+(MDT|MST)', c, re.IGNORECASE)
assert not absolute_hits

from core.models import LegacySpiderData
assert LegacySpiderData.objects.count() >= 8170
```

#### Priority 2 — Content/ subsystem retirement product-Q

S1245 found the entire content/ character-training subsystem dormant:
- `CharacterModel.objects.count()` = 0
- All 3 training tasks (poll_pending_trainings, check_single_training, cleanup_stale_trainings): 0 telemetry events ever
- Subsystem originated Session 175 (Replicate character training poller)

**Ask Chris:** is this subsystem retired? If yes, ship a deletion PR removing the 3 tasks + `content/models.py CharacterModel` + `content/character_training.py` + the 0014 migration. If unsure, leave dormant per memory rule.

#### Priority 3 — Bonus telemetry findings trace

Two findings filed in S1245 for S1246 trace:
1. **Telemetry repr bug** — find where `CeleryTaskEvent` writer is doing `task_name=str(task_obj)` instead of `task_name=task.name`. Sample row: `<@task: core.tasks.cleanup_stale_agent_executions of unified_donkey_betz_core at 0x10b8d91d0>`. Grep for `CeleryTaskEvent.objects.create` + check `task_name=` kwarg shape.
2. **Ghost task `core.tasks.check_system_health`** — fires recorded but task not in `current_app.tasks`. Likely renamed/deleted with leftover writer. `git log -S "check_system_health"` + check for renames.

#### Priority 4 — Add 5th axis to `audit_celery_zero_fire`

Direct Python call detection — the S1245 probe blind spot. Add an option that for each "uncategorized zero-fire" task runs `rg "\b<short>\s*\("` excluding def-sites + wrapper sites, and reports hit count. Either as a new `--include-direct-calls` flag or always-on column.

#### Priority 5 — Pick next audit domain

S1244's recommended menu still applies (1 down: PA tools / spiders / RAG / 24/7 advisors). Plus:
- Re-run `audit_celery_zero_fire` once 30d telemetry accumulates (~2026-07-13) for the first telemetry-valid zero-fire census.

#### Priority N — Pre-existing carryover tail (unchanged)

- Smoke-harness mode inconsistency (Session 1231 F5, LOW-MEDIUM)
- Smoke-probe tagging for AgentExecution (Session 1231 F1 / R2 REC-2)
- Promote `scripts/smoke_all_agents.py` → mgmt cmd (Session 1231 F6)
- Audit `5318da3e-…` §R2 amendment (Session 1231 F3, P3)
- Engineer workspace staleness (Session 1230 F3, MEDIUM)
- Meeting-context leak shape watch (Session 1230 F2, LOW — `cf708a2e` workspace still active; Rigby briefly mis-assigned the S1245 deliverable to it)
- Fleet-smoke wall-clock timeouts (Session 1231 F2 / R2 REC-3, LOW)
- 80 spiders audit (last Session 1205)
- 30 advisors audit (last Session 1208)
- 9 body systems audit
- 144 Discord commands audit
- 7 fleet sibling apps at localhost:8002-8008

#### Priority Last — Whatever Chris wants

S1245 was a methodology-validation session. The S1115 audit framework holds. The probe is hardened. Next session is wide open — content/ retirement Q is the most actionable single item.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222)
- Tier 3 from P2 deliverable `7ae61cf7-…`
- The 11 AUDIT_FINDINGS.md #12 deferred-by-policy tasks (each needs Chris green-light per #12 protocol)

---

### SESSION 1244 CLOSED — Cat 2 cross-app duplicates 9 → 0 + Cat 6 Finding 6.X CLOSED + Celery wiring audit (3 findings) + 2 regression canaries

Full handoff: [`SESSION_1244_CAT_2_FULLY_CLOSED_PLUS_CELERY_AUDIT_PLUS_2_REGRESSION_CANARIES.md`](docs/handoffs/SESSION_1244_CAT_2_FULLY_CLOSED_PLUS_CELERY_AUDIT_PLUS_2_REGRESSION_CANARIES.md).

Session 1244 was a continuous arc from S1243 close. Locked in the audit wins + pushed two adjacent domains to closure.

**PRs shipped this session (all admin-merged via `--admin --merge`):**

| PR | SHA | Subject | Net |
|---|---|---|---|
| [#2684](https://github.com/clwest/donkey-betz-platform/pull/2684) | `c3f80f69` | Cat 2 dormant cleanup batch (3 deletes + 3 renames) | +294/-326 |
| [#2685](https://github.com/clwest/donkey-betz-platform/pull/2685) | `7893e654` | rename core.AgentChannel + agents.AgentExecution — Cat 2 9 → 0 | +411/-316 |
| [#2686](https://github.com/clwest/donkey-betz-platform/pull/2686) | `00b10160` | Cat 2 regression canary + Cat 6 Finding 6.X resolution | +75/-629 |
| [#2687](https://github.com/clwest/donkey-betz-platform/pull/2687) | `a7a5e6d1` | Celery queue parity audit + regression canary (sports fix) | +128/-1 |
| [#2688](https://github.com/clwest/donkey-betz-platform/pull/2688) | `f84c2bf1` | remove 7 orphan task_routes patterns + extend canary | +75/-11 |

**Cat 2 audit FINAL state: 9 → 0 cross-app duplicates.** All 10 inventory items resolved via combination of renames + deletes across S1243 + S1244.

**Cat 6 Finding 6.X CLOSED-FINAL.** Live `/api/intelligence/agents/status/<id>/` endpoint repaired (was 500-ing on every call); dead `ai_core/spiders/integration.py` file deleted (625 lines, zero live importers).

**Celery wiring audit (3 findings shipped + 1 deferred):**
- Queue parity gap fixed (sports queue local consumer)
- 7 orphan task_routes patterns removed
- Dead-task analysis deferred to telemetry approach (static analysis hit >50% false positives due to delegation wrappers)

**2 regression canaries locked in via Django tests:**
- `core/tests/test_no_cross_app_model_duplicates.py` — Cat 2 zero-state
- `core/tests/test_celery_queue_parity.py` — Procfile↔Makefile↔task_routes parity (4 assertions)

**Audit-method protocol validated 9× this session.** Canonical pattern documented in handoff.

**Audit deliverables current state:**
- Cat 1 Stillborn `2d7ea39f-…` → 43,761 chars (active findings)
- Cat 2 Phantom `86870fdd-…` → **33,516 chars** (CLOSED-FINAL + Celery audit close block)
- Cat 6 Wrong-scope `7c05145d-…` → 5,393 chars (CLOSED-FINAL, Finding 6.X both subitems)
- Decision: PaMessageFeedback `2fda8b3e-…` → status=completed

**Active PA conversation:** `pa-1cb4915546654c78` — score 100/continue, 6 turns, 1 topic at S1244 close. No rotation needed. `tools/pa_local.sh` unchanged.

**Worker state at S1244 close:**
- Daphne restarted 4 times mid-session — running latest code
- Celery NOT currently running locally (no `make celery` this session). Run before exercising celery-routed tasks locally.

**Chris-side carryover into Session 1245:**
- Anthropic credit refill at https://console.anthropic.com/billing — still failing CI billing
- All 6 S1244 PRs admin-merged via `--admin --merge`
- 06-28 morning_brief verification time-bound to ~13:00 UTC Sunday

### FIRST THING Session 1245

#### Priority 0 — Conversation health check
`pa-1cb4915546654c78` was at 100/continue, 6 turns at S1244 close. Re-check at S1245 open.

#### Priority 1 — 06-28 morning_brief CUMULATIVE verification (TIME-BOUND, ~13:00 UTC Sunday = 07:00 MDT)

Validates 6 PRs cumulatively from S1242 + S1243 production paths (S1244's PRs are model renames + Celery tweaks — no direct morning_brief involvement but will exercise indirectly via spider data writes and agent execution tracking).

```python
from core.models import CeleryTaskEvent
from core.models_deliverables import Deliverable
from datetime import date
import re

today = date(2026, 6, 28)

ev = CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
    started_at__date=today,
).order_by('-started_at').first()
assert ev and ev.status == 'SUCCESS'

d = Deliverable.objects.filter(
    user__username='chris', category='Morning Brief',
    created_at__date=today,
).order_by('-created_at').first()
assert d
assert not str(d.workspace.id).startswith('cf708a2e'), "cf708a2e leak regression"

c = d.content
bare = len(re.findall(r'(?<!\[)\bMUSCULAR\b(?!\])', c))
assert bare == 0
absolute_hits = re.findall(r'by\s+\d{1,2}:\d{2}\s+(AM|PM)\s+(MDT|MST)', c, re.IGNORECASE)
assert not absolute_hits

# S1244 sanity — LegacySpiderData rows preserved
from core.models import LegacySpiderData
assert LegacySpiderData.objects.count() >= 8170
```

#### Priority 2 — Dead-task analysis (telemetry-based redo)

Per S1244 Celery audit deferred-followup. Static analysis hit >50% false positives. Switch to telemetry:

```python
from core.models import CeleryTaskEvent
from datetime import timedelta
from django.utils import timezone

cutoff = timezone.now() - timedelta(days=30)
all_seen = set(
    CeleryTaskEvent.objects.filter(started_at__gte=cutoff)
    .values_list('task_name', flat=True).distinct()
)

# After importing all 23 task modules (see test_celery_queue_parity.py setUp)
from celery import current_app
registered = {t for t in current_app.tasks.keys() if not t.startswith('celery.')}
zero_fire = registered - all_seen
print(f'Zero-fire-in-30-days tasks: {len(zero_fire)}')
```

Per-task: check if it's a delegation wrapper (`def X(): return _impl_X()`) — if yes, `_impl` may have callers. If not, candidate for cleanup.

#### Priority 3 — Pick next audit domain

Rigby's recommended S1245 menu:
1. **PA tools audit** (recommended first) — 109 schemas + 152 handlers + 8 enrichment services. Same canonical protocol. Likely surfaces schema↔handler orphans + wrong-import patterns. 1-2 hr investment.
2. **Spider pipeline health** — 80 spiders / 41 categories / 1.14M SpiderItemHash rows.
3. **RAG / citation integrity** — search_docs corpus, retrieval gates, citation source verification.
4. **24/7 advisor system** — 30 functional advisors. Last full audit Session 1208.

#### Priority N — Pre-existing carryover tail (unchanged)

- Smoke-harness mode inconsistency (Session 1231 F5, LOW-MEDIUM)
- Smoke-probe tagging for AgentExecution (Session 1231 F1 / R2 REC-2)
- Promote `scripts/smoke_all_agents.py` → mgmt cmd (Session 1231 F6)
- Audit `5318da3e-…` §R2 amendment (Session 1231 F3, P3)
- Engineer workspace staleness (Session 1230 F3, MEDIUM)
- Meeting-context leak shape watch (Session 1230 F2, LOW)
- Fleet-smoke wall-clock timeouts (Session 1231 F2 / R2 REC-3, LOW)
- 80 spiders audit (last Session 1205)
- 30 advisors audit (last Session 1208)
- 9 body systems audit
- 144 Discord commands audit
- 7 fleet sibling apps at localhost:8002-8008

#### Priority Last — Whatever Chris wants

Sessions 1226-1244 totaled ~85 PRs across 19 sessions. S1244 closed major audit loops. S1245 menu is wide open — telemetry-based dead-task analysis OR new audit domain OR whatever feels right.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222)
- Tier 3 from P2 deliverable `7ae61cf7-…`

---

### SESSION 1243 CLOSED — audit-method validated 4×, 4 PRs shipped, full Cat 2 cross-app duplicate inventory enumerated

Full handoff: [`SESSION_1243_AUDIT_METHOD_4X_VALIDATED_FOUR_PRS_PLUS_CROSS_APP_INVENTORY.md`](docs/handoffs/SESSION_1243_AUDIT_METHOD_4X_VALIDATED_FOUR_PRS_PLUS_CROSS_APP_INVENTORY.md).

Session 1243 opened on P0 health check + P2 audit-method correction from S1242 close. The audit method itself became the headline. Four PRs shipped — each validated the protocol on a different shape of cross-app collision (shadowing, stillborn-endpoint, true cross-app duplicate, mixed-live-data dual-table). Session closed with the complete Cat 2 cross-app duplicate inventory enumerated (9 names total, finite and regenerable) and 3 of 9 resolved.

**PRs shipped this session (all admin-merged via `--admin --merge`):**

| PR | Subject | Merge | Net |
|---|---|---|---|
| [#2679](https://github.com/clwest/donkey-betz-platform/pull/2679) | refactor(session-1243): tombstone shadowed core/models.py (24 dead classes) | `f3dbcebe` | +52 / -2,684 |
| [#2680](https://github.com/clwest/donkey-betz-platform/pull/2680) | feat(session-1243): rebuild PaMessageFeedback (stillborn since S1085) | `a686d602` | +293 / -26 |
| [#2681](https://github.com/clwest/donkey-betz-platform/pull/2681) | refactor(session-1243): rename intelligence.AgentExecution → ActionPlanExecution | `92c20677` | +49 / -11 |
| [#2682](https://github.com/clwest/donkey-betz-platform/pull/2682) | refactor(session-1243): rename core.SpiderData → core.LegacySpiderData (D1 clean-cut, 115 files) | `f2de87f5` | +789 / -746 |

**Cat 2 cross-app duplicate progress: 3 of 9 resolved.** Six dormant duplicates remain (all 0 rows, low risk batch cleanup candidates): AgentLearningSession, AgentRecommendation, GeneratedProject, LearningInsight, MLModelVersion, WorkflowExecution. Plus 1 deferred-product-Q (core ↔ agents AgentExecution rich-surface).

**Audit-method canonicalized (validated 4×):** `apps.get_models()` filtered by `__name__` + AST file classification (core_only / persistence_only / both / no_import) + row-count + writer-trace. Documented in handoff.

**Audit deliverables current state:**
- Cat 1 — Stillborn Surfaces `2d7ea39f-…` → **43,761 chars** (Finding 1.6 added + 1.4 reclassified)
- Cat 2 — Phantom Dependencies `86870fdd-…` → **25,132 chars** (Finding 2.3 complete inventory + 3 closures)
- Cat 6 — Wrong-scope/persona `7c05145d-…` → **3,585 chars** (Finding 6.X 2 wrong-import bugs)
- Decision: PaMessageFeedback `2fda8b3e-…` → status=completed (REBUILD shipped via #2680)

**Active PA conversation:** `pa-1cb4915546654c78` — created at S1243 close per Rigby's `suggest_fresh` (pa-634b8fef344d4af2 ended at 45/34 turns). Carry-forward seeded explicitly via pa_chat follow-up. Baseline 100/continue at S1244 open. `tools/pa_local.sh` updated to pin the new conversation.

**Worker state at S1243 close:**
- Daphne restarted mid-session after PR #2680 (PaMessageFeedback rebuild). NOT restarted after PR #2682 (LegacySpiderData rename). Local daphne is on pre-#2682 cache.
- Celery not currently running locally.
- **Chris should run** `pkill -9 -f celery; rm -f .celery*.pid; make stop; make start; make celery` before exercising any local code paths overnight.

**Chris-side carryover into Session 1244:**
- Anthropic credit refill at https://console.anthropic.com/billing — still failing CI billing
- All 4 S1243 PRs admin-merged via `--admin --merge`
- Daphne + celery restart before bed (see Worker state)

### FIRST THING Session 1244

#### Priority 0 — Conversation health check
`pa-1cb4915546654c78` was at 100/continue + 1 turn at S1243 close. Re-check at S1244 open.

#### Priority 1 — 06-28 morning_brief CUMULATIVE verification (TIME-BOUND, ~13:00 UTC Sunday = 07:00 MDT)

Validates **6 PRs cumulatively**: #2672 + #2674 (S1242) AND #2679 + #2680 + #2681 + #2682 (S1243). Verification block:

```python
from core.models import CeleryTaskEvent
from core.models_deliverables import Deliverable
from datetime import date
import re

today = date(2026, 6, 28)

ev = CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
    started_at__date=today,
).order_by('-started_at').first()
assert ev and ev.status == 'SUCCESS'

d = Deliverable.objects.filter(
    user__username='chris', category='Morning Brief',
    created_at__date=today,
).order_by('-created_at').first()
assert d
assert not str(d.workspace.id).startswith('cf708a2e'), "cf708a2e leak regression"

c = d.content

# PR #2672 MUSCULAR broaden
bare = len(re.findall(r'(?<!\[)\bMUSCULAR\b(?!\])', c))
assert bare == 0, f"MUSCULAR regression: {bare}"

# PR #2674 Path C markdown (no absolute clocks in markdown)
absolute_hits = re.findall(r'by\s+\d{1,2}:\d{2}\s+(AM|PM)\s+(MDT|MST)', c, re.IGNORECASE)
assert not absolute_hits, f"Absolute clock in markdown: {absolute_hits}"

# S1243 sanity — LegacySpiderData rows preserved
from core.models import LegacySpiderData
assert LegacySpiderData.objects.count() >= 8170, "Row loss in #2682 RenameModel"
```

#### Priority 2 — Cat 2 dormant cleanup batch

6 remaining cross-app duplicates from Finding 2.3 inventory, all 0 rows so low data risk:

| Class | Variant A | Variant B |
|---|---|---|
| AgentLearningSession | `core.models.ai_learning.models` | `ai_core.intelligence.models` |
| AgentRecommendation | `core.models_agent_memory` | `coleadership.models` |
| GeneratedProject | `core.models.projects.models` | `ai_opportunities.models` |
| LearningInsight | `core.models.ai_learning.models` | `ai_core.intelligence.models` |
| MLModelVersion | `core.models_unified_system` | `ml.models` |
| WorkflowExecution | `core.models_unified_system` | `content.models` |

Apply the canonical investigation protocol per-class. Batch dormant-only renames into a single PR. Same shape as #2681 — RenameModel is data-safe at 0 rows.

#### Priority 3 — Cat 6 Finding 6.X reachability check

Two wrong-import endpoint bugs surfaced by PR #2681:
- `ai_core/spiders/integration.py:142` — `.create(template=..., input_data=..., priority=...)` with kwargs that don't exist on `ActionPlanExecution`
- `intelligence/views_agent_integration.py:315-322` — accesses `.result`, `.started_at`, `.completed_at`, `.error_message` fields that don't exist

Determine reachability. If unreachable → cleanup PR. If reachable → fix import to `from core.models.agents_registry import AgentExecution`.

#### Priority 4 — Open product Q

`core.AgentExecution` (canonical, 984 live rows) ↔ `agents.AgentExecution` (39-col rich-execution surface, 0 rows). Was the agents-app rich-execution surface abandoned, staged, or accidentally unwired? Determines migrate-vs-leave.

#### Priority N — Pre-existing carryover tail (unchanged)

- Smoke-harness mode inconsistency (Session 1231 F5, LOW-MEDIUM)
- Smoke-probe tagging for AgentExecution (Session 1231 F1 / R2 REC-2)
- Promote `scripts/smoke_all_agents.py` → mgmt cmd (Session 1231 F6)
- Audit `5318da3e-…` §R2 amendment (Session 1231 F3, P3)
- Engineer workspace staleness (Session 1230 F3, MEDIUM)
- Meeting-context leak shape watch (Session 1230 F2, LOW)
- Fleet-smoke wall-clock timeouts (Session 1231 F2 / R2 REC-3, LOW)
- 80 spiders audit (last Session 1205)
- 30 advisors audit (last Session 1208)
- 9 body systems audit
- 144 Discord commands audit
- 7 fleet sibling apps at localhost:8002-8008

#### Priority Last — Whatever Chris wants

Sessions 1226-1243 totaled ~82 PRs across 18 sessions. S1243's headline was audit-method canonicalization (validated 4×); the natural S1244 arc is "drain the 6-item Cat 2 dormant queue using the canonical protocol."

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222)
- Tier 3 from P2 deliverable `7ae61cf7-…`

---

### SESSION 1242 CLOSED — Path C + Cat 5 audit + audit-method correction via core/models.py shadowing discovery (6 PRs, 6 audit deliverables advanced)

Full handoff: [`SESSION_1242_PATH_C_STRUCTURED_DECISION_CARD_PLUS_DELETION_REGRET_AUDIT.md`](docs/handoffs/SESSION_1242_PATH_C_STRUCTURED_DECISION_CARD_PLUS_DELETION_REGRET_AUDIT.md).

Session 1242 opened on the S1241 P1 06-27 cumulative morning_brief verification (time-bound). Brief fired SUCCESS at 13:00:02 UTC, deliverable landed correctly (`7ba30cc0-…`, NOT cf708a2e leak — PR #2653 holds). Content surfaced **2 Sub-step D regression candidates** that became this session's work:

1. **MUSCULAR jargon leak (PR #2658 scope gap)** — 4 bare mentions slipped past the 2-literal humanizer in TL;DR / Lane 1 / Where-to-verify / Decision 1 body. Shipped **PR #2672** (broaden humanizer to tolerant regex + apply at `_execute_decision_card_synthesis_step` which read `lane_1_text` raw). 25 tests green; production verification on the 06-27 content showed 4 bare → 0 bare + 4 tagged `[MUSCULAR]`, count preserved.

2. **MDT absent (PR #2655 dead-letter)** — 0 MDT/MST anywhere because LLM emits relative deadlines ("within 48h") instead of absolute. Started to mark `_denver_tz` as dead code. **Chris invoked NEW memory rule:** `feedback_verify_before_deleting_dead_code.md` — *"code that looks dead may be staged for an unbuilt connection."* 6-step verify-before-delete surfaced `MORNING_BRIEF_SPEC.md:228` as planned consumer (structured `decision_card[{..., next_step_timebox}]` deferred since S1233 B.1). Routed Path A/B/C triage to Rigby; she picked **(C) Hybrid** — markdown stays RELATIVE per audience-fit; structured form ships absolute TZ-aware. Chris ratified. Shipped **PR #2674 (Path C)** — single LLM call emits markdown + ```json fence, 2 new helpers (parser + structured validator), 33 new tests, MORNING_BRIEF_SPEC.md updated. `_denver_tz` rescued from dead code, now feeds structured form's ISO offset.

**PRs shipped this session (all admin-merged via `--admin --merge`):**

| PR | Subject | Merge | Net | Tests |
|---|---|---|---|---|
| [#2672](https://github.com/clwest/donkey-betz-platform/pull/2672) | fix(session-1242): broaden MUSCULAR humanizer + apply at decision_card_synthesis | `74845aee` | +145 / -10 | 6 new (25 total green) |
| [#2673](https://github.com/clwest/donkey-betz-platform/pull/2673) | docs(session-1241): close handoff + S1242 entry-point | `41fa0d15` | +290 / -69 | (docs) |
| [#2674](https://github.com/clwest/donkey-betz-platform/pull/2674) | feat(session-1242): Path C — structured decision_card with next_step_timebox | `b7252f3c` | +908 / -30 | 33 new (69 total green) |
| [#2675](https://github.com/clwest/donkey-betz-platform/pull/2675) | docs(session-1242): close handoff + S1243 entry-point (morning close) | `390ff776` | +419 / -69 | (docs) |
| [#2676](https://github.com/clwest/donkey-betz-platform/pull/2676) | docs(session-1242): mark generate_agent_dreams as user-triggered, not scheduled | `801da251` | +1 / -1 | (docs) |
| [#2677](https://github.com/clwest/donkey-betz-platform/pull/2677) | refactor(session-1242): remove shadowed AgentLearningSession from core/models.py | `5affd2cc` | +18 / -30 | 69 green (no regression) |

**THE BIG DISCOVERY (afternoon):** `core/models.py` is shadowed by the `core/models/` package. Python loads the package, not the file. All 25 class definitions in `core/models.py` are dead Python text — Django registers zero of them. `apps.get_model()` always returns the package class. PR #2677 surgically removed 1 class (no migration needed); 24 remain. Filed as Cat 2 Finding 2.1 candidate. This invalidates my earlier "duplicate model" classification protocol — every such finding now requires `apps.get_model()` resolution check before classification past CANDIDATE.

**Chris's product-question that reframed the audit method:** *"Are we deleting features that were never added or are we deleting features that are working in other ways and these are just duplicates that need to be removed?"* — surfaced 3 distinct deletion categories (1: Never-completed / 2: Duplicate-old-not-removed / 3: Works-but-not-exercised). Applied to all 4 pending findings; Finding 1.3 Dreams flipped from "stillborn" → Cat 3 (works, just user-triggered) — closed via PR #2676 doc cleanup + smoke test (0 → 3 AgentDream rows). Finding 1.5 legacy AgentLearningSession confirmed Cat 2 via shadowing → closed via PR #2677. Classification protocol now part of the audit method.

**Audit deliverables advanced this session (Donkey Betz workspace `b4503364-…`):**

| Doc | UUID | Δ |
|---|---|---|
| MASTER INDEX | `dfd2a073-da10-433e-90fe-1fc69a3c716a` | S1242 log entry + summary table (5,741 → 8,306 chars) |
| Cat 1 — Stillborn Surfaces | `2d7ea39f-3bf0-447c-8c89-33210fc0d18b` | Finding 1.1 promoted **DUAL-SOURCED → RUNTIME-CHECKED**; Findings 1.2-1.5 finalized; cross-finding pattern named (10,898 → 29,887 chars) |
| Cat 1 — Stillborn Surfaces (afternoon) | `2d7ea39f-…` | + Finding 1.3 smoke-test result + revised classification (DISPROVEN as stillborn, Cat 3 works-but-not-exercised); 29,778 → 34,599 chars |
| **Cat 2 — Phantom Dependencies (NEW finding)** | `86870fdd-e8d8-48d3-9760-4bea75ec10e3` | **NEW Finding 2.1 candidate** — `core/models.py` shadowed by `core/models/` package; 24 remaining dead-text classes; per-class verify-before-delete + `apps.get_model()` resolution check protocol established (883 → 8,348 chars) |
| Cat 4 — Doc↔Code Drift | `0836042d-3a97-4d60-b9c8-11ea8d7f9884` | NEW **Finding 4.3 candidate** — search_docs provenance filter excludes ~85% of pre-filter matches (5,269 → 8,167 chars) |
| Cat 5 — Deletion Regret | `7ad80aaf-2025-419d-8590-8897ab2e6ee2` | **3 new findings** (5.1 ml_intelligence.ml_service + 5.2 ml_revenue_pipeline + 5.3 batch_tag_documents) + Rigby Lens B (1,081 → 21,005 chars) |
| Path C deliverable (NEW) | `19b45ea0-0831-43e8-aa43-038cf9c2e705` | Created mid-session, full design spec + Rigby Q1-Q4 + SHIPPED addendum (0 → 17,830 chars) |

**Cross-finding pattern named (S1242):** writers exist but produce 0 rows in production via 3 flavors — (1) writer chain has no callers, (2) writer fires but short-circuits before persist, (3) writer is feature-flagged for paths not exercised locally. Mirrors Cat 5's silent-fallback pattern across archived modules. Pattern is bidirectional with the deletion-regret rule.

**New memory rule logged:** [`feedback_verify_before_deleting_dead_code.md`](~/.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_verify_before_deleting_dead_code.md). 6-step verify checklist (grep callers + stringified refs + `docs/` + recent handoffs + audit deliverables via Rigby + originating PR intent). First real use shipped Path C instead of destructive cleanup.

**Active conversation:** `pa-634b8fef344d4af2` — started S1242 at 75/continue with 10 turns; added ~16-20 turns covering all 3 PRs + audit work + Lens B + Path C design + shipment summary. Likely 50-65 range now. **Rotation at S1243 open is a real consideration.**

**Worker state:** Both PR #2672 and PR #2674 modify `core/services/workflow_orchestration_agent.py` (no new `@shared_task`, no PeriodicTask changes). **A worker restart isn't strictly required by the @shared_task registry, BUT** per `feedback_router_heartbeat_not_dead.md` companion + sys.modules cache rule, modifying agent module code requires worker restart for the new code to actually fire. **CHRIS MUST run `pkill -9 -f celery; rm -f .celery*.pid; make celery` before going to bed tonight, otherwise tomorrow's 06-28 fire uses the OLD code paths** and neither PR's behavior shows up in verification.

**Chris-side carryover into Session 1243:**
- Anthropic credit refill at https://console.anthropic.com/billing
- CI billing still failing — all 3 S1242 PRs admin-merged via `--admin --merge`
- **CRITICAL: celery restart needed tonight** (see Worker state above) — without it, 06-28 brief fires with pre-PR-#2672 + pre-PR-#2674 code

### FIRST THING Session 1243

#### Priority 0 — Conversation health + rotation decision

`pa-634b8fef344d4af2` quick `session_tool action=health_check`. Started S1242 at 75/continue with 10 turns; added ~16-20 turns this session covering all 3 PR arcs + Cat 5 audit + Lens B + Path C design + shipment summary. Likely 50-65 range now.

**Decision tree:**
- If score ≥ 70 AND topic_count ≤ 7 → **continue** (no rotation needed)
- If score < 70 OR topic_count > 7 → **rotate with carry-forward summary** including:
  - 3 S1242 PR merge commits (`74845aee` / `41fa0d15` / `b7252f3c`)
  - 5 audit deliverable UUIDs + char counts
  - Cross-finding pattern: "writers exist but 0 rows / 3 flavors"
  - `feedback_verify_before_deleting_dead_code.md` rule + first real use producing Path C
  - 06-28 brief verification window pending
  - Cat 5 v1 heuristic gaps (class/function-level imports, Celery task strings, settings.py keys — deferred to deeper-audit follow-up)

#### Priority 1 — 06-28 morning_brief 4th-fire cumulative verification (TIME-BOUND 07:00 MDT Sun = 13:00 UTC)

**Cumulative verification window for BOTH PR #2672 (MUSCULAR broaden) AND PR #2674 (Path C structured form).** Run this block:

```python
from core.models import CeleryTaskEvent
from core.models_deliverables import Deliverable
from datetime import date
import re

today = date(2026, 6, 28)

# 1. Brief fired?
ev = CeleryTaskEvent.objects.filter(
    task_name='core.tasks.generate_morning_brief_daily',
    started_at__date=today,
).order_by('-started_at').first()
assert ev and ev.status == 'SUCCESS', f"Brief did not fire or failed: {ev}"

# 2. Deliverable landed?
d = Deliverable.objects.filter(
    user__username='chris', category='Morning Brief',
    created_at__date=today,
).order_by('-created_at').first()
assert d, "No Morning Brief deliverable for 2026-06-28"
assert not str(d.workspace.id).startswith('cf708a2e'), "cf708a2e leak regression"

c = d.content

# 3. PR #2672 MUSCULAR broaden verification
bare = len(re.findall(r'(?<!\[)\bMUSCULAR\b(?!\])', c))
assert bare == 0, f"MUSCULAR regression: {bare} bare mentions (expected 0)"

# 4. PR #2674 Path C markdown verification (no absolute clocks in markdown)
absolute_hits = re.findall(r'by\s+\d{1,2}:\d{2}\s+(AM|PM)\s+(MDT|MST)', c, re.IGNORECASE)
assert not absolute_hits, f"Absolute clock format in markdown: {absolute_hits}"
```

Also pull the Path C log line from the Celery task logs:
```bash
grep "Session 1242 Path C: decision_cards" /tmp/celery.log | tail -3
```
Expected: `count=X, non_null_timebox=Y, parse_issue=False, structured_issues=0`. If `parse_issue=True` or `structured_issues>0`, gpt-5-mini's JSON adherence is the issue — consider the 2-pass repair fallback (Rigby's bonus suggestion deferred for v0).

**If verification fails:**
- MUSCULAR regression → file Cat 1 finding (different escape pattern). Do NOT broaden the regex further without identifying the new pipeline path.
- Absolute clock in markdown → Path C prompt needs stronger negative instruction OR gpt-5-mini is ignoring the rule.
- Brief did not fire OR worker still on old code → run `pkill -9 -f celery; rm -f .celery*.pid; make celery` (this is the bedtime-restart Chris may have skipped).

#### Priority 2 — Audit method correction (shadowing) + verification discipline upgrade

**Framing per Rigby's S1242 close ratification:** the `core/models.py` shadowing discovery means our "duplicate model" classification protocol was wrong. Before any more cleanup PRs, recalibrate the audit instrument. Rigby's ratified ordering (a) → (c) → (b):

##### (a) Re-verify Finding 1.4 Channels with `apps.get_model()` resolution check — FIRST EXECUTABLE STEP

S1242 Finding 1.4 classified `core.AgentChannel` vs `agents.AgentChannel` as Cat 2 duplicates without doing the `apps.get_model()` check that revealed Finding 1.5's actual mechanism (shadowing, not duplication). Run the same check + reclassify:

```python
from django.apps import apps
for m in apps.get_models():
    if m.__name__ == 'AgentChannel':
        print(f'  {m._meta.app_label}.{m.__name__} | module={m.__module__} | table={m._meta.db_table}')
from core.models import AgentChannel as A
print(f'core.models.AgentChannel → module={A.__module__} table={A._meta.db_table}')
```

If only one is Django-registered → likely shadowing (same as 1.5). If both are registered → real duplicate (Cat 2 with split consumers + 8 importers to migrate). Update Finding 1.4 classification before any cleanup PR. ~20 min.

##### (c) Per-class shadowing scan on `core/models.py`

Per Cat 2 Finding 2.1's pseudocode in deliverable `86870fdd-…`: for each of 24 remaining classes in `core/models.py`, classify into SAFE_DUPLICATE / LOST_CANDIDATE / AMBIGUOUS. Produces an enumerated verified list ready for batch-cleanup PRs (or surfaces classes that need product Qs before delete). ~1-2 hr scan + ~15 min triage with results.

##### (b) Cat 5 micro-fix (only after (a)+(c) land)

Cat 5 findings 5.1 / 5.2 / 5.3 are all small Cat 1 fixes — but DEFER until method correction lands. Rigby's rationale: *"Cat 5 fixes are tempting and small, but the shadowing discovery just proved we can't trust surface-level 'duplicate model' intuition without the model registry check."*

##### (d) Other options (lower priority unless circumstances change)

- Rigby docs-side passes for Cat 1 Findings 1.2 / 1.4 (1.3 closed; 1.5 mostly closed) — pending Lens B
- Investigate Finding 4.3 (search_docs provenance filter) — if real, weakens "no docs evidence found" verdicts on multiple findings
- Deeper Cat 5 audit scan — broaden v1 module-name heuristic to class/function imports + Celery task strings + settings keys

#### Priority 3 — Pre-existing carryover tail (unchanged)

- Rigby's memory store cap (S1239 close) — deferred to its own session
- 80 spiders audit (last Session 1205)
- 30 advisors audit (last Session 1208)
- 9 body systems audit
- 144 Discord commands audit
- 7 fleet sibling apps at localhost:8002-8008
- Smoke-harness mode inconsistency (Session 1231 F5, LOW-MEDIUM) — one-line fix
- Smoke-probe tagging for AgentExecution (Session 1231 F1 / R2 REC-2, MEDIUM)
- Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents` (Session 1231 F6, LOW)
- Audit `5318da3e-…` §R2 amendment (Session 1231 F3, P3)
- Engineer workspace staleness (Session 1230 F3, MEDIUM)
- Meeting-context leak shape watch (Session 1230 F2, LOW)
- Fleet-smoke wall-clock timeouts (Session 1231 F2 / R2 REC-3, LOW)

#### Priority N — CI billing fix (Chris-side, outstanding since Session 1223)

#### Priority N+1 — Anthropic A/B (gated on credit refill)

#### Priority Last — Whatever Chris wants

Sessions 1226-1241 totaled ~78 PRs + 1 no-code audit foundation session. S1242 natural arc is Cat 1 expansion + Cat 5 kickoff. Method validated by Finding 1.1 worked specimen — apply same verifier-loop discipline to every future finding.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222)
- Tier 3 from P2 deliverable `7ae61cf7-…`

---

### SESSION 1239 CLOSED — PA tools audit clean + morning_brief local dogfood, 2 PRs

Full handoff: [`SESSION_1239_PA_TOOLS_AUDIT_CLEAN_PLUS_MORNING_BRIEF_LOCAL_DOGFOOD.md`](docs/handoffs/SESSION_1239_PA_TOOLS_AUDIT_CLEAN_PLUS_MORNING_BRIEF_LOCAL_DOGFOOD.md).

Session 1239 was audit-then-act. Verified PA tools surface (Audit #5, Δ=43 from inventory) ran clean — 109 schemas / 152 handlers / 108 matched; the 1 schema orphan (`run_agent`) + 44 handler orphans are by-design (umbrella schema + agent-name dispatches). Rigby's `tool_migration_report` confirmed all 14 REMOVED_TOOL_ALIASES entries silent in 24h. One real cleanup (`web_search` was dual-exposed) folded into PR-1; bonus regression bug found + fixed (`intelligence_tool action=search source=web` was dropping `limit`). PR-2 flipped `generate-morning-brief-daily` to fire on local per Chris's directive + unstuck 6 stale tests from Session 1205's `run-spider-network` removal.

**Session 1239 PRs:**

| PR | Subject | Net | Tests |
|---|---|---|---|
| [#2660](https://github.com/clwest/donkey-betz-platform/pull/2660) (PR-1) | web_search alias cleanup + intelligence_tool.search limit passthrough | +57 / -3 | 3 new (16 green) |
| [#2661](https://github.com/clwest/donkey-betz-platform/pull/2661) (PR-2) | generate-morning-brief-daily local dogfood + unstuck Session-1205 stale beat-filter tests | +51 / -28 | 1 flipped + 6 unstuck (20 green) |

**Operational invariants added Session 1239:**
- `intelligence_tool action=search source=web limit=N` honors N (was silently capping at 5)
- `REMOVED_TOOL_ALIASES` and `web_search` schema/handler no longer contradict; cleanup audits won't flag this again
- `generate-morning-brief-daily` enabled on local (`make celery` restart required to pick up) — 07:00 Denver daily fire
- Beat-filter lock-in tests track current denylist (gate restored — future denylist changes require explicit test touch)

**Active conversation at S1239 close:** `pa-a2443db2e43a42dc` — added ~6 turns this session (audit-only). Should still be 90-100. Per S1237/S1238 close notes, Rigby's recommendation is "rotate before next substantial design+execution arc." **S1240 begins Sub-step E (Mon-Fri dogfood loop) which IS a new arc — rotation should be considered at S1240 open.**

**Worker state:** No new `@shared_task` Session 1239. PR-2 adds an enabled `PeriodicTask` row — Chris should run `pkill -9 -f celery; rm -f .celery*.pid; make celery` before going to bed tonight if he wants the 07:00 Denver fire tomorrow (06-27).

**Chris-side carryover into Session 1240:**
- Anthropic credit refill at https://console.anthropic.com/billing
- CI billing still failing — both Session 1239 PRs admin-merged via `--admin`

### FIRST THING Session 1240 (Saturday morning 2026-06-27)

#### Priority 0 — Conversation health check (+ rotation candidate)

`pa-a2443db2e43a42dc` — re-check via `session_tool action=health_check`. Should be 90-100. **Rotation recommended** — Session 1240 starts Sub-step E (new design+execution arc).

#### Priority 1 — 06-27 cumulative verification (TIME-BOUND, FIRST thing Saturday morning)

The cumulative window for both Sub-step D (Session 1238 polish PRs) AND Sub-step E kickoff (Session 1239 local dogfood flip).

- **`refresh_docs_corpus` 2nd scheduled fire verify (2026-06-27 10:00 UTC MDT = 04:00 Denver)** — expected skip path.
- **morning_brief 3rd-fire verify (2026-06-27 13:00 UTC = 07:00 MDT)** — first fire with all 6 Session 1238 Sub-step D PRs cumulatively live. **NOT** the "first-ever local fire" — PR-2 sanity-check on 06-26 evening surfaced that the PeriodicTask row was already `enabled=True` with `total_run_count=2` (`last_run_at=2026-06-26 13:00:00 UTC`). `LOCAL_DENY_TASKS` was a paper defense for this task: `_filter_local_safe` blocks new materialization but `_enforce_disabled_local` only runs on `add_critical_celery_tasks` invocation, so the existing-enabled row had been firing all along. PR-2 ratified what was happening. Verification block:
  ```python
  # 1. Did it fire?
  from core.models import CeleryTaskEvent
  from datetime import date
  ev = CeleryTaskEvent.objects.filter(
      task_name='core.tasks.generate_morning_brief_daily',
      started_at__date=date(2026, 6, 27),
  ).order_by('-started_at').first()
  assert ev and ev.status == 'SUCCESS', f"Brief did not fire or failed: {ev}"

  # 2. Did the deliverable land in the right workspace?
  from core.models_deliverables import Deliverable
  d = Deliverable.objects.filter(
      user__username='chris',
      category='Morning Brief',
      created_at__date=date(2026, 6, 27),
  ).first()
  assert d, "No morning brief deliverable for 2026-06-27"
  # Should NOT land in the cf708a2e leak workspace (PR #2653 holds)

  # 3. Sub-step D invariants in content
  content = d.content
  # Decision Cards end with periods, show "MDT" not "MST", all 4 fields (PR #2655)
  # Lane 1 warnings tagged "Evidence confidence: low" when self-check refutes (PR #2656)
  # Lane 4 3-block fallback if no odds (PR #2657)
  # Lane 3 coverage map if no-signal (PR #2658)
  # Body-system jargon humanized (PR #2658)
  ```
- **COO daily diagnostic (2026-06-27 13:30 UTC)** — deliverable should land in MB workspace, NOT cf708a2e.

#### Priority 2 — Re-ask Rigby for audience-fit verdict on the 06-27 LOCAL brief

Sub-step D PRs (all 6 cumulatively live for the first time tomorrow) should land Rigby's overall 66/100 → 80s. Yesterday's 06-26 read earned 66/100 with NONE of the Sub-step D PRs merged yet — tomorrow is the first apples-to-apples follow-up. If still flagging Decision-Card incompleteness or Lane self-reference issues, surface diff against today's specific defect shapes.

#### Priority 3 — Sub-step E (Mon-Fri dogfood) kickoff

If verification clean → Sub-step E starts. Chris reads daily, captures qualitative verdict, each newly-surfaced polish item becomes a focused PR. Same rhythm that produced Session 1238's 6 polish PRs but now driven by real cumulative content quality, not Rigby's one-time audit.

#### Priority 4 — Remaining audit candidates (Chris discretion)

PA tools audit closed Session 1239. Still untouched:

- **Rigby's memory store cap** (NEW Session 1239 close discovery — defer to own session, NOT S1240) — Rigby flagged at S1239 close that her memory store is "over capacity" and she's self-pruning low-signal "shipped/deploy" memories to make room. Worth a focused session (S1241+) to surface: cap size, current memory count, eviction policy, whether the pruning rule is intentional or stop-gap. Not blocking morning_brief or Sub-step E — she's working around it.
- **80 spiders** — last full audit Session 1205 Capability Audit Layer 3. Likely fresh drift since `run-spider-network` re-enabled.
- **30 advisors** — last audit Session 1208 (`docs/ADVISOR_AUDIT.md`).
- **9 body systems** — `BodyCoordinator` autonomic reflex layer, last touched Sub-step D.
- **144 Discord commands** — `docs/DISCORD_AUDIT.md`, 25 Cog classes.
- **61 frontend routes** — last sanity-check pre-Workspace tab redesign.
- **7 fleet sibling apps** at localhost:8002-8008 — Session 1233 carryover.

#### Priority N — Pre-existing carryover tail

Unchanged across many sessions:

- **Smoke-harness mode inconsistency** (Session 1231 F5, LOW-MEDIUM) — one-line fix.
- **Smoke-probe tagging for AgentExecution** (Session 1231 F1 / R2 REC-2, MEDIUM).
- **Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents`** (Session 1231 F6, LOW).
- **Audit `5318da3e-…` §R2 amendment** (Session 1231 F3, P3).
- **Engineer workspace staleness** (Session 1230 F3, MEDIUM).
- **Meeting-context leak shape watch** (Session 1230 F2, LOW).
- **Fleet-smoke wall-clock timeouts** (Session 1231 F2 / R2 REC-3, LOW).

#### Priority N+1 — CI billing fix (Chris-side, outstanding since Session 1223)

#### Priority N+2 — Anthropic A/B (gated on credit refill)

#### Priority Last — Whatever Chris wants

Sessions 1226-1239 totaled ~73 PRs. Sub-step E starting tomorrow is the headline. Daily morning brief reads + ordered polish PRs = the natural Sub-step E rhythm.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222).
- Tier 3 from P2 deliverable `7ae61cf7-…`.

---

### SESSION 1238 CLOSED — morning_brief Sub-step D complete + cf708a2e leak fix, 6 PRs

Full handoff: [`SESSION_1238_MORNING_BRIEF_SUB_STEP_D_COMPLETE.md`](docs/handoffs/SESSION_1238_MORNING_BRIEF_SUB_STEP_D_COMPLETE.md).

Session 1238 closed the daily-CoS Sub-step D polish phase end-to-end via 6 PRs (+1,702 / -12 net production lines, 75 new tests). Plus the cf708a2e leak surfaced during P1.b drill (separate from Sub-step D, adjacent fix).

**Session 1238 PRs:**

| PR | Subject | Net | Tests |
|---|---|---|---|
| [#2653](https://github.com/clwest/donkey-betz-platform/pull/2653) (A) | `scheduled_diagnostic_runner` workspace_resolver | +368 / -1 | 10 |
| [#2654](https://github.com/clwest/donkey-betz-platform/pull/2654) (B) | 00-START Operator Edge timestamp correction | +6 / -6 | (doc) |
| [#2655](https://github.com/clwest/donkey-betz-platform/pull/2655) (1) | Decision Card validator + truncation guard + dynamic TZ | +391 / -5 | 11 |
| [#2656](https://github.com/clwest/donkey-betz-platform/pull/2656) (2) | Lane 1 self-referential health alarm filter | +317 / -0 | 12 |
| [#2657](https://github.com/clwest/donkey-betz-platform/pull/2657) (3) | Lane 4 odds-missing fallback | +298 / -0 | 13 |
| [#2658](https://github.com/clwest/donkey-betz-platform/pull/2658) (4) | Lane 3 adaptive + MUSCULAR plain-English | +322 / -0 | 19 |

**Rigby's 06-26 audience-fit verdict (overall 66/100)** drove the polish PR list. All 6 prioritized items landed in priority order. Tomorrow's 06-27 morning_brief fire is the cumulative verification window.

**Operational invariants added Session 1238:**
- `scheduled_diagnostic_runner` workspace priority chain: env_var → resolver → None (COO/CTO/Trend auto-target chris's MB workspace)
- Decision Cards: dynamic Denver TZ, 6000 token budget, post-render validator catches truncation + missing fields
- Lane 1 health alarms: contradiction-aware via 30min recheck against AgentExecution + CeleryTaskEvent
- Lane 3: deterministic coverage-map fallback when no-signal
- Lane 4: 3-block fallback when odds data missing
- Body-system jargon: humanized in operator-facing text

**Active conversation at S1238 close:** `pa-a2443db2e43a42dc` — health 100/100, ~24 turns added. Still healthy but approaching the rotation point Rigby flagged at S1237 ("rotate before next substantial design+execution arc"). **Re-check at S1239 open + consider rotation if score < 90 or topic count > 7.**

**Worker state:** No new `@shared_task` Session 1238. No restart needed.

**Chris-side carryover into Session 1239:**
- Anthropic credit refill at https://console.anthropic.com/billing
- CI billing still failing — all 6 Session 1238 PRs admin-merged via `--admin`

### FIRST THING Session 1239

#### Priority 0 — Conversation health check

`pa-a2443db2e43a42dc` — re-check via `session_tool action=health_check`. Should be 90-100 (Sub-step D execution kept conv tightly scoped). Per Rigby's prior recommendation, **rotate if next session starts a substantially new arc** (e.g., post-Sub-step-D feature work). Continue if just monitoring tomorrow's brief.

#### Priority 1 — 06-27 cumulative verification (TIME-BOUND)

The primary purpose of Session 1239 — verify all 6 Session 1238 PRs land cleanly in tomorrow's morning_brief fire.

- **`refresh_docs_corpus` 2nd scheduled fire (2026-06-27 10:00 UTC MDT = 04:00 Denver)** — expected: skip path (took < 1s, `index_changed=False`, `unembedded_before=0`). If cascade re-runs, debug what changed.
- **morning_brief 3rd-fire verify (2026-06-27 13:00 UTC = 07:00 MDT)** — the cumulative verification window. Expected checks:
  ```python
  from core.models_deliverables import Deliverable
  from datetime import date
  qs = Deliverable.objects.filter(user__username='chris', created_at__date=date(2026, 6, 27))
  # Expected: all in MB workspace 19807888-…; NONE in cf708a2e (PR-A held)
  d = Deliverable.objects.filter(category='Morning Brief', created_at__date=date(2026, 6, 27)).first()
  # Read d.content:
  # - Decision Cards end with periods, show "MDT" not "MST", all 4 fields per decision (PR-1)
  # - Lane 1 warnings tagged "Evidence confidence: low — auto-downgraded" when self-check refutes (PR-2)
  # - Lane 4 ships 3-block fallback if no odds (PR-3)
  # - Lane 3 ships coverage map if no-signal (PR-4a)
  # - Body-system jargon humanized (PR-4b)
  ```
- **COO daily diagnostic (2026-06-27 13:30 UTC)** — deliverable should land in MB workspace, NOT cf708a2e (PR-A).
- **Operator Edge 06:00 UTC** — prod fire only; ignore on local (LOCAL_DENY_TASKS).

#### Priority 2 — Re-ask Rigby for audience-fit verdict on the 06-27 brief

Sub-step D PRs should land Rigby's overall 66/100 score into the 80s. If she's still flagging Decision-Card incompleteness or Lane self-reference issues, surface the diff against today's specific defect shapes (token usage, validation_issues field, self-check trigger logs).

#### Priority 3 — Brief read by Chris + any newly-surfaced polish items

If Sub-step D is fully validated → Sub-step E (Mon-Fri dogfood). Chris reads daily, flags any remaining issues, each becomes a focused PR.

If new polish items surface → cycle (read → Rigby verdict → ordered fix PRs) — same pattern as Session 1238.

#### Priority 4+ — Pre-existing carryover tail

Unchanged across many sessions:

- **Smoke-harness mode inconsistency** (Session 1231 F5, LOW-MEDIUM) — one-line fix.
- **Smoke-probe tagging for AgentExecution** (Session 1231 F1 / R2 REC-2, MEDIUM).
- **Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents`** (Session 1231 F6, LOW).
- **Audit `5318da3e-…` §R2 amendment** (Session 1231 F3, P3).
- **Engineer workspace staleness** (Session 1230 F3, MEDIUM).
- **Meeting-context leak shape watch** (Session 1230 F2, LOW).
- **Fleet-smoke wall-clock timeouts** (Session 1231 F2 / R2 REC-3, LOW).

#### Priority N — CI billing fix (Chris-side, still outstanding since Session 1223)

#### Priority N+1 — Anthropic A/B (gated on credit refill)

#### Priority Last — Whatever Chris wants

Sessions 1226-1238 totaled ~71 PRs. Sub-step E (Mon-Fri dogfood) is unlocked now that Sub-step D landed. Daily morning brief reads + ordered polish PRs = the natural Sub-step E rhythm.

**Possible re-ignites (Chris-discretion only):**
- **Fleet sibling apps build-out** — 7 apps at localhost:8002-8008.
- Audit #5 (PA tool schemas vs handlers — Δ=43).
- `scan-spider-opportunities` resume.
- Outreach tone tweak nice-to-haves.
- **Extend `verify_doc_claims` registration coverage** to the other 472 unwatched docs.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222).
- Tier 3 from P2 deliverable `7ae61cf7-…`.

---

### SESSION 1237 CLOSED — P5#3 audit bonus carryovers close, 3 PRs (-1,558 net lines)

Full handoff: [`SESSION_1237_AUDIT_BONUS_CARRYOVERS_CLOSE.md`](docs/handoffs/SESSION_1237_AUDIT_BONUS_CARRYOVERS_CLOSE.md).

Session 1237 closed all 3 bonus carryovers surfaced during the Session 1235-1236 P5#3 drift-sweep audit. Pure execution session — no design debate, no new audit scope.

**Session 1237 PRs:**

| PR | Subject | Lines |
|---|---|---|
| [#2649](https://github.com/clwest/donkey-betz-platform/pull/2649) | P2.a — `search_personal_memories_api` decorator-kwarg fix | +140 / -3 |
| [#2650](https://github.com/clwest/donkey-betz-platform/pull/2650) | P2.c — `dashboard/at_a_glance.py` delete (scope-corrected mid-execution) | +75 / -415 |
| [#2651](https://github.com/clwest/donkey-betz-platform/pull/2651) | P2.b — `core/views.py` shadowed delete | +105 / -1,460 |

**Notable findings:**

- **P2.c scope correction:** original framing was "update the error-pattern map" (assumed live tooling). Triple-grep showed 0 importers anywhere — same orphan pattern as `intelligence/core.py`. Routed pivot through Chris → delete. Bonus value: the deleted map's suggested fix for the `ai_unified_platform does not exist` error was wrong even when written (it pointed at `sed`-renaming a string that doesn't exist in `ai_core/settings.py`).
- **P2.b shadowing audit:** systematic set-diff of function names between `core/views.py` and `core/views/main.py` returned empty in both directions — 100% duplication. The shadowing dates back to Session 728's package conversion (per `__init__.py` comment). The file was kept as dead artifact for unknown reasons. 1,457 lines removed; 0 production behavior change (URL resolver still loads 1797 patterns).

**Audit grand-total stats (Sessions 1235 → 1237 combined):**
- 17 PRs total (14 formal audit + 3 bonus carryovers)
- ~5,000+ lines of dead code removed
- ~100+ regression-guard tests written
- 0 real bug patterns in production code

**Operational invariants (added Session 1237):**
- `search_personal_memories_api` accepts decorator `user_id=` kwarg cleanly
- `dashboard/at_a_glance.py` deleted; zero refs anywhere
- `core/views.py` deleted; package re-export chain preserves all import paths
- Set-diff parity (`comm -23 / -13`) is the canonical evidence pattern for any future "is this duplicate file a shadow?" audit work

**Active conversation at S1237 close:** `pa-a2443db2e43a42dc` — was 100/100 at S1237 open; added ~6 turns. Should still be 95-100. Re-check at S1238 open.

**Worker state:** No new `@shared_task` added Session 1237. No restart needed.

**Still Chris-side carryover into Session 1238:**
- Anthropic credit refill at https://console.anthropic.com/billing
- CI billing still failing — all 3 Session 1237 PRs admin-merged via `--admin`

### FIRST THING Session 1238

#### Priority 0 — Conversation health check

`pa-a2443db2e43a42dc` — health re-check via `session_tool action=health_check`. Should be 95-100 (small additive turns through bounded P2 execution work).

#### Priority 1 — Calendar checks (TIME-BOUND, 2026-06-26 — should be DUE by S1238 open if opening morning)

These are time-bound. Clear FIRST on session open.

- **`refresh_docs_corpus` first scheduled fire verify (2026-06-26 10:00 UTC MDT = 04:00 Denver)** — Session 1235 PR #2634's first-ever scheduled run. Expected: skip path (corpus fully embedded). Verify:
  ```python
  from core.models import CeleryTaskEvent
  from datetime import date
  ev = CeleryTaskEvent.objects.filter(
      task_name='core.tasks.refresh_docs_corpus',
      started_at__date=date(2026, 6, 26),
  ).order_by('-started_at').first()
  print('status:', ev.status, 'took:', ev.duration_ms, 'result:', ev.result)
  ```
- **morning_brief 2nd-fire verification (2026-06-26 13:00 UTC = 07:00 MDT)** — first scheduled fire with Session 1234 D3/D4/D5/D6 live. Verify lane intermediates land in MB workspace `19807888-…`, NOT cf708a2e.
- **Operator Edge newsletter Friday-1 dry-run check (2026-06-26 06:00 UTC = 00:00 MDT)** — Session 1228 carryover. NOTE: Operator Edge is in `LOCAL_DENY_TASKS` (`add_critical_celery_tasks.py:65`) so it's `enabled=False` on local; this verification is prod-only via Railway logs. Crontab is `hour=6, minute=0, day_of_week=friday` (corrected Session 1238 PR-B — prior carryover entries said 12:00 UTC which was inaccurate to source).

#### Priority 2 — Brief read + Sub-step D (if morning_brief 2nd fire produced real content)

If 06-26 morning_brief produced a real Deliverable: Chris reads → Rigby pulls audience-fit verdict → polish PRs.

#### Priority 3 — Pre-existing carryover tail

Unchanged from Sessions 1235-1237:

- **Smoke-harness mode inconsistency** (Session 1231 F5, LOW-MEDIUM) — one-line fix.
- **Smoke-probe tagging for AgentExecution** (Session 1231 F1 / R2 REC-2, MEDIUM).
- **Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents`** (Session 1231 F6, LOW).
- **Audit `5318da3e-…` §R2 amendment** (Session 1231 F3, P3) — `deliverable_tool action=append`.
- **Engineer workspace staleness** (Session 1230 F3, MEDIUM).
- **Meeting-context leak shape watch** (Session 1230 F2, LOW).
- **Fleet-smoke wall-clock timeouts** (Session 1231 F2 / R2 REC-3, LOW).

#### Priority N — CI billing fix (Chris-side, still outstanding since Session 1223)

#### Priority N+1 — Anthropic A/B (gated on credit refill)

When Anthropic credits return: run the Session 1229 Step 5 line-count task on the Anthropic path.

#### Priority Last — Whatever Chris wants

Sessions 1226-1237 totaled ~65 PRs. Daily-CoS arc Sub-step D awaits Chris's brief read on 06-26 + onward.

**Possible re-ignites (Chris-discretion only):**
- **Fleet sibling apps build-out** — 7 apps at localhost:8002-8008. No work since 1224.
- Audit #5 (PA tool schemas vs handlers — Δ=43).
- `scan-spider-opportunities` resume.
- Outreach tone tweak nice-to-haves.
- **Extend `verify_doc_claims` registration coverage** to the other 472 unwatched docs.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222).
- Tier 3 from P2 deliverable `7ae61cf7-…`.

---

### SESSION 1236 CLOSED — P5#3 drift-sweep audit COMPLETE, 5 PRs

Full handoff: [`SESSION_1236_P5_3_AUDIT_COMPLETE_TRANCHE_1_THROUGH_4.md`](docs/handoffs/SESSION_1236_P5_3_AUDIT_COMPLETE_TRANCHE_1_THROUGH_4.md).

Session 1236 closed the full P5#3 drift-sweep audit across 4 tranches. Combined with Session 1235's Tranche 1 PRs #1-#6, the audit shipped **14 PRs total** spanning ~19 files affected, ~3,000+ lines of dead code removed, ~90+ regression-guard tests written.

**Audit deliverable** `feed2d81-ee2f-44c0-8f17-816591d2a3ff` marked `completed` via `content_tool action=content_complete`.

**Session 1236 PRs:**

| PR | Subject | Tranche |
|---|---|---|
| [#2643](https://github.com/clwest/donkey-betz-platform/pull/2643) | delete orphan personal-knowledge feature (-489 lines) | T1 PR #7 final |
| [#2644](https://github.com/clwest/donkey-betz-platform/pull/2644) | rotate pa_local.sh pin → `pa-a2443db2e43a42dc` | infra |
| [#2645](https://github.com/clwest/donkey-betz-platform/pull/2645) | `clean_mythologies` retire cleanup step | T2 PR #1 |
| [#2646](https://github.com/clwest/donkey-betz-platform/pull/2646) | delete 5 dead one-shot scripts (-1,624 lines) | T3 bulk |
| [#2647](https://github.com/clwest/donkey-betz-platform/pull/2647) | delete 6 dead zombie unit tests (-1,110 lines) | T4 bulk |

**Final audit verification:** sharper grep for real bug patterns (`psycopg2.connect` / `database='ai_unified_platform'` / `FROM unified_embeddings` / `INTO unified_embeddings`) across entire repo returns 8 file hits — all are intentional source-guard `assertNotIn(...)` text in test files OR retirement-rationale docstrings. **0 real bug patterns in production code.**

**Notable decisions:**
- **PR #2643 (orphan personal-knowledge delete):** Chris's evidence `"I do remember when we started that, but I honestly forgot all about doing it lol"` met the deletion threshold. Pushed back on my over-engineered 410-Gone-with-deprecation-logging framing — _"theres a lot of things we haven't used in 30 days lol"_ — honest deletion was right.
- **Conv rotation mid-session:** Per Rigby's own P0 health-check recommendation (75/100, "rotate before Tranche 2/3/4 implementation"). `pa-0f08fc48ec914917` → `pa-a2443db2e43a42dc`. Carry-forward seeded with audit scope + Tranche 1 close summary.

**Operational invariants (added Session 1236):**
- Zero `psycopg2.connect` calls remain in production code (all retired/deleted)
- Zero `FROM unified_embeddings` / `INTO unified_embeddings` queries remain in production code
- `clean_mythologies` mgmt cmd runs cleanly with `[RETIRED]` notice + zero counts

**Active conversation at S1236 close:** `pa-a2443db2e43a42dc` — health re-check at S1237 open is mandatory.

**Worker state:** No new `@shared_task` added Session 1236. No restart needed.

**Still Chris-side carryover into Session 1237:**
- Anthropic credit refill at https://console.anthropic.com/billing
- CI billing still failing — all 5 Session 1236 PRs admin-merged via `--admin`

### FIRST THING Session 1237

#### Priority 0 — Conversation health check

`pa-a2443db2e43a42dc` was fresh at Session 1236 mid-session start; added ~10 turns through Tranche 2/3/4 execution + close. Likely 90-95/100 (fresh + bounded execution work, no design debate). Run `session_tool action=health_check` to confirm before any other PA work.

#### Priority 1 — Calendar checks (TIME-BOUND, 2026-06-26)

These are time-bound. Clear FIRST on session open.

- **`refresh_docs_corpus` first scheduled fire verify (2026-06-26 10:00 UTC MDT = 04:00 Denver)** — Session 1235 PR #2634's first-ever scheduled run. Expected: skip path (corpus fully embedded). Verify:
  ```python
  from core.models import CeleryTaskEvent
  from datetime import date
  ev = CeleryTaskEvent.objects.filter(
      task_name='core.tasks.refresh_docs_corpus',
      started_at__date=date(2026, 6, 26),
  ).order_by('-started_at').first()
  print('status:', ev.status, 'took:', ev.duration_ms, 'result:', ev.result)
  # Expected: SUCCESS, took < 1s, result includes index_changed=False, unembedded_before=0
  ```
- **morning_brief 2nd-fire verification (2026-06-26 13:00 UTC = 07:00 MDT)** — first scheduled fire with Session 1234 D3/D4/D5/D6 live. Verify lane intermediates land in MB workspace `19807888-…`, NOT cf708a2e.
- **Operator Edge newsletter Friday-1 dry-run check (2026-06-26 12:00 UTC)** — Session 1228 carryover.

#### Priority 2 — Bonus carryovers surfaced during the P5#3 audit (Session 1235-1236)

These are out-of-DoD-scope discoveries from the audit work; each is a focused single-PR opportunity.

1. **`search_personal_memories_api` latent decorator-kwarg bug** — `@require_personal_memory_access` passes `user_id=` kwarg; function signature is `def view(request):`. One-line `**kwargs` fix (same pattern Session 1235 PR #2639 applied to two sibling functions). Lowest-risk pickup.
2. **`core/views.py` shadowed dead code audit** — Python package resolution makes `core/views/` (package) win over `core/views.py` (module). Likely substantial deletion candidate (potentially thousands of lines) after verifying every function is also in `core/views/main.py`. Medium-risk; needs systematic function-by-function audit.
3. **`dashboard/at_a_glance.py` error log analyzer** — references the dead-DB error pattern with an outdated suggested fix ("rename `ai_unified_platform` → `unified_donkey_betz`"). Real fix is the ORM pivot pattern. Update the analyzer's error-pattern map. Low-risk meta-tooling cleanup.

#### Priority 3 — Brief read + Sub-step D (if morning_brief 2nd fire produced real content)

If 06-26 morning_brief produced a real Deliverable: Chris reads → Rigby pulls audience-fit verdict → polish PRs.

#### Priority 4+ — Pre-existing carryover tail

Unchanged from Session 1235-1236:

- **Smoke-harness mode inconsistency** (Session 1231 F5, LOW-MEDIUM) — one-line fix.
- **Smoke-probe tagging for AgentExecution** (Session 1231 F1 / R2 REC-2, MEDIUM).
- **Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents`** (Session 1231 F6, LOW).
- **Audit `5318da3e-…` §R2 amendment** (Session 1231 F3, P3) — `deliverable_tool action=append`.
- **Engineer workspace staleness** (Session 1230 F3, MEDIUM).
- **Meeting-context leak shape watch** (Session 1230 F2, LOW).
- **Fleet-smoke wall-clock timeouts** (Session 1231 F2 / R2 REC-3, LOW).

#### Priority N — CI billing fix (Chris-side, still outstanding since Session 1223)

#### Priority N+1 — Anthropic A/B (gated on credit refill)

When Anthropic credits return: run the Session 1229 Step 5 line-count task on the Anthropic path (`unset CLAUDE_CODE_ENGINE_PROVIDER`) and confirm no clarification stall.

#### Priority Last — Whatever Chris wants

Sessions 1226-1236 totaled ~62 PRs. Daily-CoS arc Sub-step D awaits Chris's brief read on 06-26 + onward.

**Possible re-ignites (Chris-discretion only):**
- **Fleet sibling apps build-out** — 7 apps at localhost:8002-8008. No work since 1224.
- Audit #5 (PA tool schemas vs handlers — Δ=43).
- `scan-spider-opportunities` resume.
- Outreach tone tweak nice-to-haves.
- **Extend `verify_doc_claims` registration coverage** to the other 472 unwatched docs.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222).
- Tier 3 from P2 deliverable `7ae61cf7-…`.

---

### SESSION 1235 CLOSED — 9 PRs across two arcs (carryover-close + P5#3 audit Tranche 1)

Full handoff: [`SESSION_1235_CARRYOVER_CLOSE_PLUS_P5_3_DRIFT_SWEEP_TRANCHE_1.md`](docs/handoffs/SESSION_1235_CARRYOVER_CLOSE_PLUS_P5_3_DRIFT_SWEEP_TRANCHE_1.md).

**Arc A — P-series carryover close, 3 PRs:**

| PR | Closes | What |
|---|---|---|
| [#2633](https://github.com/clwest/donkey-betz-platform/pull/2633) | P4 | `BACKEND_INVENTORY` services count drift 167 → 354 + verifier baseline refresh. Closed the only active `verify_doc_claims --only-drift` hit. |
| [#2634](https://github.com/clwest/donkey-betz-platform/pull/2634) | P5#2 | `refresh_docs_corpus` daily beat task @ 04:00 Denver. Hash-delta + unembedded-count secondary trigger. NOT in LOCAL_DENY. 9 tests. First scheduled fire: 2026-06-26 10:00 UTC MDT. Smoke-verified live (fire 1 cascade → 3 embed dispatches; fire 2 skip path 0.28s). |
| [#2635](https://github.com/clwest/donkey-betz-platform/pull/2635) | P5#1 | `extracted_metadata` clobber root cause — merge-not-overwrite at 4 sites + sync update self-heal path + migration 0047 backfilled 3 victims. 2729 → 2732 scope-keyed docs corpus rows. |

**Arc B — P5#3 audit Tranche 1, 6 PRs:** (Chris invoked the queued Session 1236 audit early; Tranche 1 executed end-to-end)

| PR | What |
|---|---|
| [#2636](https://github.com/clwest/donkey-betz-platform/pull/2636) | T1.1 — `dashboard/views.py` + `dashboard/real_time_monitor.py` pivot to `DocumentEmbedding` ORM. Removed misleading hardcoded fallbacks (`67922`, `265174`). 11 tests. |
| [#2637](https://github.com/clwest/donkey-betz-platform/pull/2637) | T1.2 — `core/conversation_memory.py` pivot to canonical `core.models.ConversationMemory` Django model (which had the exact right shape, sitting in `models.py` the whole time). 19 tests. |
| [#2638](https://github.com/clwest/donkey-betz-platform/pull/2638) | T1.3 — `personal_knowledge_list` deprecation in BOTH `core/views.py` AND `core/views/main.py` (the file/package shadowing bug surfaced mid-PR). 9 tests. |
| [#2639](https://github.com/clwest/donkey-betz-platform/pull/2639) | T1.4 — `personal_memory_stats` + `delete_personal_memory` pivot to live `UserEmbedding` ORM (same model D21 PR #2631 validated). 11 tests. Latent decorator-kwarg bug fixed in passing. |
| [#2640](https://github.com/clwest/donkey-betz-platform/pull/2640) | T1.5 — `codebase_awareness.py` retire-to-no-op facade. Eliminated import-time `psycopg2.connect()` to dead `ai_unified_platform` DB. 18 tests. Mgmt command `ingest_codebase` smoke-verified clean. |
| [#2641](https://github.com/clwest/donkey-betz-platform/pull/2641) | T1.6 — `intelligence/core.py` deletion (-889 lines). Truly dead — zero callers, dead-DB target, heavy unconditional deps. Rigby-approved per overwhelming evidence. 2 regression-guard tests. |

**Three major findings surfaced mid-session:**

1. **Audit scope correction (29 → ~6 production files)** — sharper grep (only real bug shapes: `psycopg2.connect`, `database='ai_unified_platform'`, `FROM unified_embeddings`) showed many of the original 29 matches were references to the legitimate `UnifiedEmbedding` Django model + dict key names + docstring mentions. True remaining real-bug surface (post-Tranche 1): 1 deferred file + 1 mgmt cmd + 2 scripts + 6 dead unit tests.
2. **`core/views.py` is shadowed dead code** — Python package resolution makes `core/views/` (package) win over `core/views.py` (module). The 7 dead-substrate refs in `core/views.py` are all in shadowed copies; live function is at `core/views/main.py:1048`. Session 1236 follow-up: audit if the whole file is deletable.
3. **`codebase_awareness` was firing dead-DB connect AT IMPORT TIME** — every import triggered a dead-DB attempt that was silently caught. The mgmt command's "✅ success with zero stats" was wrong-by-construction since file creation.

**Audit deliverable:** `feed2d81-ee2f-44c0-8f17-816591d2a3ff` ("P5#3 drift sweep — eradicate unified_embeddings/ai_unified_platform legacy surfaces"). 4 tranches. Tranche 1 = 6 of 6 named live-wired surfaces closed (PR #2641 closes it except the deferred `views_knowledge.py`).

**Operational invariants (post-Session 1235):**
1. `refresh_docs_corpus` beat task runs daily 04:00 Denver, hash-delta gated, self-healing on partial step-4 failures.
2. Doc-claim verifier drift = 0 (was 1 medium at session open).
3. 2,732 / 2,732 docs corpus rows have `scope='docs_index'`.
4. Dashboard endpoints + personal memory endpoints read live ORM (no hardcoded fallbacks, no dead-substrate hits).
5. `codebase_awareness` singleton no longer fires DB at import time.
6. `intelligence/core.py` is deleted; regression-guard tests prevent restoration.

**Active conversation:** `pa-0f08fc48ec914917` — continues from Session 1234. ~30+ turns added across Session 1235. **Health check at Session 1236 open is mandatory** (not done at this close).

**Worker state:** Restart post-PR #2634 merge (new `@shared_task`) — verified 5 workers + beat picked up `refresh_docs_corpus`. No further restarts needed for PRs #2635-#2641.

**Still Chris-side carryover into Session 1236:**
- **Anthropic credit refill** at https://console.anthropic.com/billing
- **CI billing** still failing — all 9 Session 1235 PRs admin-merged via `--admin`

### FIRST THING Session 1236

#### Priority 0 — Conversation health check (TIME-BOUND, do FIRST)

`pa-0f08fc48ec914917` has ~30+ turns added this session. Ask Rigby to score the conv + recommend continue / rotate before any other PA work. Use `tools/pa_local.sh "Session 1236 open — please do a self-health check on this conv and recommend continue vs rotate"`.

#### Priority 1 — Calendar checks (2026-06-26 — TIME-BOUND, clear early)

- **`refresh_docs_corpus` first scheduled fire (2026-06-26 10:00 UTC MDT = 04:00 Denver)** — Session 1235 PR #2634's first-ever scheduled run. Expected: skip path (corpus fully embedded as of Session 1234 close + Session 1235 sync). Verify:
  ```python
  from core.models import CeleryTaskEvent
  from datetime import date
  ev = CeleryTaskEvent.objects.filter(
      task_name='core.tasks.refresh_docs_corpus',
      started_at__date=date(2026, 6, 26),
  ).order_by('-started_at').first()
  print('status:', ev.status, 'took:', ev.duration_ms, 'result:', ev.result)
  # Expected: SUCCESS, took < 1s, result includes index_changed=False, unembedded_before=0
  ```
- **morning_brief 2nd-fire verification (2026-06-26 13:00 UTC = 07:00 MDT)** — first scheduled fire with Session 1234 D3/D4/D5/D6 live. Verify lane intermediates land in MB workspace `19807888-…`, NOT cf708a2e. (Same check as carried forward in Session 1235 start-here.)
- **Operator Edge newsletter Friday-1 dry-run check (2026-06-26 12:00 UTC)** — Session 1228 carryover.

#### Priority 2 — Session 1236 audit arc continuation (highest-value next work)

Audit deliverable `feed2d81-ee2f-44c0-8f17-816591d2a3ff`. Tranche 1 (6 PRs) closed in Session 1235. Remaining:

**Tranche 1 PR #7 (deferred) — `core/views_knowledge.py`**
- Three URL-wired endpoints (`/api/v1/personal-knowledge/{upload,delete,stats}/`). Same dead substrate.
- **Blocking decision needs Chris's caller evidence:** any live frontend / mobile / Discord clients hitting these endpoints in the last 30 days?
- If zero callers → delete (or 410 Gone). If used → pivot with new `UserEmbedding.content_type='personal_knowledge'` CHOICES value + migration.
- Coupled with `personal_knowledge_list` (Session 1235 PR #2638 already deprecated this read endpoint to honest empty).

**Tranche 2 — mgmt cmds**
- `mythology/management/commands/clean_mythologies.py` (6 `FROM unified_embeddings` queries) — likely retire/delete pattern like codebase_awareness.

**Tranche 3 — scripts**
- `scripts/backfill_embeddings.py`, `scripts/upload_unified_docs.py`, 3 verification scripts in `scripts/verification/`. Per Rigby's earlier classification: probable deletion candidates (one-off scripts that fail today).

**Tranche 4 — dead pre-existing unit tests**
- 6 files in `tests/unit/`: `test_code_embeddings`, `test_code_rag`, `test_embeddings_rag`, `test_embeddings_working`, `test_encryption_migration`, `test_rag_direct`, `test_rag_with_existing_embeddings`. Delete or rewrite to exercise the live `DocumentEmbedding`/`UserEmbedding` substrates.

#### Priority 3 — Bonus carry-overs surfaced during Session 1235

- **`search_personal_memories_api` latent decorator-kwarg bug** — same `TypeError: unexpected keyword argument 'user_id'` shape PR #2639 fixed in two sibling functions. One-line `**kwargs` fix.
- **`core/views.py` shadowed dead code audit** — Python package resolution makes the whole `core/views.py` unreachable in production. Likely deletion candidate after verifying every function is also in `core/views/main.py`. Substantial diff (-thousands of lines).
- **`dashboard/at_a_glance.py` error log analyzer** — references the dead-DB error pattern with an outdated suggested fix ("rename `ai_unified_platform` → `unified_donkey_betz`"). Real fix is the ORM pivot pattern. Update the analyzer's error pattern map.

#### Priority 4 — Brief read + Sub-step D (if morning_brief 2nd fire produced real content)

If 06-26 morning_brief produced a real Deliverable: Chris reads → Rigby pulls audience-fit verdict → polish PRs.

#### Priority 5+ — Pre-existing carryover tail

Unchanged from Session 1235 carryover (which itself carried from Session 1234's "what didn't get touched" list):

- **Smoke-harness mode inconsistency** (Session 1231 F5, LOW-MEDIUM) — one-line fix.
- **Smoke-probe tagging for AgentExecution** (Session 1231 F1 / R2 REC-2, MEDIUM).
- **Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents`** (Session 1231 F6, LOW).
- **Audit `5318da3e-…` §R2 amendment** (Session 1231 F3, P3) — `deliverable_tool action=append`.
- **Engineer workspace staleness** (Session 1230 F3, MEDIUM).
- **Meeting-context leak shape watch** (Session 1230 F2, LOW).
- **Fleet-smoke wall-clock timeouts** (Session 1231 F2 / R2 REC-3, LOW).

#### Priority N — CI billing fix (Chris-side, still outstanding since Session 1223)

#### Priority N+1 — Anthropic A/B (gated on credit refill)

When Anthropic credits return: run the Session 1229 Step 5 line-count task on the Anthropic path (`unset CLAUDE_CODE_ENGINE_PROVIDER`) and confirm no clarification stall. If clean, lift the retry contract up out of the OpenAI-only branch.

#### Priority Last — Whatever Chris wants

Sessions 1226-1235 totaled ~57 PRs. Daily-CoS arc Sub-step D awaits Chris's brief read on 06-26 + onward.

**Possible re-ignites (Chris-discretion only):**
- **Fleet sibling apps build-out** — 7 apps at localhost:8002-8008. No work since 1224.
- Audit #5 (PA tool schemas vs handlers — Δ=43) — non-blocking long-tail.
- `scan-spider-opportunities` resume.
- Outreach tone tweak nice-to-haves (Rigby's Session 1225 review).
- **Extend `verify_doc_claims` registration coverage** to the other 472 unwatched docs.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222).
- Tier 3 from P2 deliverable `7ae61cf7-…`.

---

### SESSION 1234 CLOSED — THREE ARCS, 22 PRs

Same UTC day, three distinct arcs. All three handoffs are load-bearing for Session 1235 context.

**Arc 1: Morning Brief first-fire fixes (D1→D8), 7 PRs** — full handoff [`SESSION_1234_FIRST_FIRE_FIXES_PLUS_DRIFT_FRAMING.md`](docs/handoffs/SESSION_1234_FIRST_FIRE_FIXES_PLUS_DRIFT_FRAMING.md). Driven by the 2026-06-25 13:00 UTC morning_brief first-fire — three independent bugs surfaced from the deliverable corpus in workspace `cf708a2e-…` (Session 1231 E2E): lane intermediates leaking to wrong workspace, agent_router missing workflow-name signal, ResearchAgent saving 8 duplicates on iteration storms. D1/D2 fail-loud arc landed before Chris's deliverable sweep request; D3/D4/D5/D6 closed the boundaries; D7 verified-holding note; D8 structural snapshot framing on 6 load-bearing docs.

**Arc 2: Docs-corpus retrieval (D9→D16), 9 PRs** — full handoff [`SESSION_1234_DOCS_CORPUS_ARC_D9_THROUGH_D16.md`](docs/handoffs/SESSION_1234_DOCS_CORPUS_ARC_D9_THROUGH_D16.md). Triggered by Chris's question *"how is Rigby updated when we do things like update the docs?"*. Found prod doc corpus was 12 days stale + 1820 docs had never been synced. D9 wrote type-aware enrichment on the sync path; D10 backfilled 2,729 existing rows; D11 exposed filter axes on `kb_tool action=documents`; D12 pivoted dead `core.rag_integration.search_embeddings` to populated `DocumentEmbedding`; D13 added `kb_tool action=semantic_search` (Rigby's first real semantic-search PA tool action); D14 guarded the `min_session=0` LLM-autofill bug; D15 lowered `similarity_threshold` default 0.6 → 0.4 to match text-embedding-3-small's actual band; **D16 caught the actual 0-results bug**: broad try/except was swallowing `Cannot filter a sliced queryset` TypeError from a classmethod that ended `[:limit]`. Smoking-gun verification: Rigby's call returns 10 chunks matching the direct-ORM check exactly. 39 docs pinned, 15+ document_class values, ~28k DocumentEmbedding chunks (backfill still ramping the long-tail at session close).

| PR | What |
|---|---|
| #2606-#2615 (D1-D8) | Morning Brief arc (see Arc 1 handoff) |
| **#2617** | `docs(session-1234): session-close docs cascade checklist + corrected memory rule` — 4-step cascade lock |
| **#2618** (D9) | sync writes type-aware retrieval enrichment to Document |
| **#2619** (D10) | backfill mgmt command + applied to 2,729 existing rows |
| **#2620** (D11) | kb_tool documents action filter axes |
| **#2621** (D12) | rag_integration.search_embeddings pivot to populated table |
| **#2622** (D13) | kb_tool action=semantic_search (pgvector + filters) |
| **#2623** (D14) | min_session=0 LLM-autofill guard |
| **#2624** (D15) | similarity_threshold default 0.6 → 0.4 |
| **#2625** (D16) | **filter-before-slice — the real fix for 0-result bug** |

**Two new auto-memory feedback rules added at close:** `feedback_docs_pipeline_4_step_cascade.md` + `feedback_test_real_db_for_queryset_semantics.md` (the D16 lesson — MagicMock'd querysets don't enforce Django's slicing/filtering rules; integration tests are mandatory for retrieval/search code).

| PR | What |
|---|---|
| **#2606** | `fix(session-1234): morning_brief D1 fail-loud — lane_4 error capture + beat task raises`. D1 of 3-PR fail-loud arc. Lane 4 handler always populates `error` field on falsy `result.success`; beat task `generate_morning_brief_daily` raises `RuntimeError` instead of swallowing. Per memory `feedback_fail_loud_first_then_root_cause_then_telemetry`. |
| **#2607** | `fix(session-1234): morning_brief D2 — gtm slot → COOAgent + lane_4 non-critical + sentinel`. D2 root-cause #1. Remapped `gtm_pipeline_health` slot from OpportunityPipelineAgent (per-row contract) to COOAgent (daily-summary contract). Sentinel + non_critical allowlist pattern per memory `feedback_workflow_step_sentinel_plus_noncritical_pattern`. |
| **#2608** | `fix(session-1234): D2.fix — create_morning_brief_deliverable uses self.user, not context dict`. D2 root-cause #2. `context['user']` is a profile DICT (lane prompt injection); `Deliverable.user` is a FK. Switched to `getattr(self, 'user', None)`. Per memory `feedback_context_user_is_profile_dict_not_user_instance`. |
| **#2609** | `fix(session-1234): D2.telemetry — beat task reads result['steps'] not 'step_results'`. D2 telemetry-only PR. `WorkflowOrchestrationAgent._compile_final_result` uses key `'steps'`; beat task fixed to extract per-step telemetry by name. Per memory `feedback_workflow_result_steps_not_step_results`. |
| **#2610** | `fix(session-1234): D3 — morning_brief lanes thread workspace_id to delegates`. New `_resolve_workflow_target_workspace_id(workflow)` helper. `execute()` writes `context['workspace_id']` BEFORE the step loop; router downstream injects to delegate `agent._workspace_id`. Pre-fix: 5 lane intermediates landed in cf708a2e-… (debug workspace) instead of MB workspace 19807888-…. 5 new tests. |
| **#2611** | `fix(session-1234): D4 — agent_router intercepts workflow dispatches`. Router-level intercept before keyword overrides. Triggers on `WORKFLOWS['<name>']` task pattern OR `context['workflow_name']` set. Reroutes to WorkflowOrchestrationAgent + mirrors `workflow_name` → `context['workflow']`. Closes DevOpsAgent's flagged "ran business_research instead of morning_brief" routing bug. 10 new tests across 3 classes. |
| **#2612** | `fix(session-1234): D5 — ResearchAgent skips duplicate same-day same-workspace saves`. Pre-save dup check via `_find_recent_duplicate_deliverable(title, window_minutes=60)`. `[RESEARCH_DUP_SKIPPED]` structured log on match; save short-circuits. Per-workspace + per-agent_name scoping; fail-open. Catches 8-deliverable storm pattern from 06-25 00:58 → 05:23 UTC. 10 new tests. |
| **#2613** | `fix(session-1234): D6 — DevOpsAgent skips duplicate same-day same-workspace saves`. Mirror of D5 after Rigby's `deliverable_tool action=duplicates` surfaced DevOpsAgent as 2nd-highest iteration storm (4 smokes 02:48 → 05:25 UTC). Same shape; deliberately NOT extracted to BaseAgent yet (per "three similar lines is better than premature abstraction"). 10 new tests. |
| **#2614** | `docs(session-1234): D7 — leak-gate verified-holding note in deliverable_factory`. Docs-only. Title-corruption sweep found leak gate (Session 1226 P3) fully closed: 0 net-new leaks on 06-25; last leak 06-24 13:34. Added verified-holding paragraph to `TEMPLATE_LEAK_TITLE_TOKENS` doc block. |
| **#2615** | `docs(session-1234): D8 — structural snapshot framing on 6 load-bearing docs`. Explore-agent audited 8 load-bearing docs (ARCHITECTURE / AGENTS / SERVICES / SPIDERS / DATABASE_MODEL_REFERENCE / API_PATH_POLICY / DISCORD_INTEGRATION / CAPABILITIES). 7/8 already had DOC-POINTER-V1; DATABASE_MODEL_REFERENCE was the gap. CAPABILITIES.md already had the per-section "Historical snapshot" pattern (was the model). This PR: added missing banner + extended snapshot framing to 5 others. Zero counts changed by design — Chris picked option 3 (structural framing) over option 1 (surgical count refresh). |

**ORM action (not a PR):** 36 historical leak-victim Deliverables bulk-archived via `.update(status='archived')` in one transaction. Scope: title matches any of 7 `TEMPLATE_LEAK_TITLE_TOKENS` patterns AND created before 06-25 00:00 UTC AND status ∉ `{archived, completed}` AND `agent_name != 'Rigby'`. Preserves 1 intentional Rigby gate-smoke + 1 already-completed COO row. Verified pre/post: 36 expected, 36 updated, 0 leak victims remain un-archived.

**Operational invariants (post-D6 + worker restart at 14:23 local):**
1. Lane intermediates land in MB workspace `19807888-…`, not cf708a2e.
2. Any `WORKFLOWS['<name>']` task or `context['workflow_name']` reroutes to WorkflowOrchestrationAgent regardless of caller.
3. ResearchAgent + DevOpsAgent same-title same-workspace duplicate saves within 60min are skipped + `[*_DUP_SKIPPED]` logged.
4. Title-leak gate verified holding 1d stale at close.
5. Load-bearing doc body-text counts are framed as historical snapshots; D8 makes the snapshot framing explicit in 6 docs.

**Active conversation:** `pa-0f08fc48ec914917` — Rigby fresh-started mid-session at Chris's direction (replaced `pa-91cf6bbce1d6406e`). Session 1234 added ~5 turns. Health check at close: **score 100/100, continue, no rotation**. Carries forward.

**Worker state:** Celery workers restarted at 14:23 local after D3/D4/D5/D6 merges. D7 + D8 were docs-only and did not need restart.

**Doc-claim drift verifier at close:** 1 drift (medium) — pre-existing `BACKEND_INVENTORY.md` services count. NOT introduced this session; carryover (out of scope for D8 by design).

**Docs index regenerated at close:** 2729 documents indexed.

**Arc 3: Broad-except sweep (D17→D21), 5 PRs** — full handoff [`SESSION_1234_BROAD_EXCEPT_SWEEP_D17_THROUGH_D21.md`](docs/handoffs/SESSION_1234_BROAD_EXCEPT_SWEEP_D17_THROUGH_D21.md). Triggered by D16's discovery that broad `except Exception → return []` was hiding `Cannot filter a sliced queryset` TypeError as "no results." Audit revealed the same anti-pattern at 17 additional sites across 4 more files + 1 fully-broken function. D17 narrowed `scoped_retrieval` (8 sites); D18 narrowed `knowledge_first_router` (6 sites) + 2-way cross-file invariant; D19 narrowed `knowledge_similarity` (1 site) + 3-way invariant; D20 selective-narrowed `views_rag_embeddings` (2 helper sites of 20 — the 18 HTTP endpoints correctly stay broad to preserve API contract) + 4-way invariant; D21 fully rewrote `search_personal_memories` (was connecting to a non-existent database) + matched D17-D20 allowlist shape. **17 broad-except sites narrowed + 1 full function rewrite, all under a single `(DatabaseError, ConnectionError, OSError)` allowlist locked by 4-way pairwise + transitive cross-file invariant tests.**

| PR | What |
|---|---|
| **#2627** (D17) | scoped_retrieval narrow-except (8 sites) |
| **#2628** (D18) | knowledge_first_router narrow-except (6 sites) + 2-way invariant |
| **#2629** (D19) | knowledge_similarity narrow-except (1 site) + 3-way invariant |
| **#2630** (D20) | views_rag_embeddings selective narrow-except (2 of 20) + 4-way invariant; helper-vs-endpoint discriminator codified |
| **#2631** (D21) | search_personal_memories full rewrite (pivot from dead `unified_embeddings` table to `UserEmbedding` ORM) + narrow except matching D17-D20 shape |

**Docs cascade backfill completed** during this arc — the `sync_docs_index_to_documents --embed` task that started at second-arc midpoint reached `Embedded 1810/1819 documents... Embedding complete!` shortly before close. **All 2,732 Documents now embedded (36,854 chunks, 100% coverage)**. The 12-day-stale + 1820-missing corpus state from session open is fully resolved.

**Active conversation:** `pa-0f08fc48ec914917` — continues across all three arcs. **No rotation at any close** (Rigby's verdict: score 100/100 continue). Carries forward into Session 1235.

**Workers restarted multiple times** during the arcs: 14:23 (post-D6), 15:13 (post-D11), 15:17 (post-D13), 15:42 (post-D14), 16:08 (post-D15), 16:14 (post-D16). D17-D21 didn't touch PA-imported task modules so no further restart needed.

**Doc-claim drift verifier at close (all three arcs):** 1 drift (medium) — pre-existing `BACKEND_INVENTORY.md` services count. Same drift at every close; out of scope.

**Still Chris-side carryover into Session 1235:**
- **Anthropic credit refill** at https://console.anthropic.com/billing.
- **CI billing** still failing — all 22 Session 1234 PRs admin-merged via `--admin`.

### FIRST THING Session 1235

#### Priority 1 — Calendar checks (2026-06-26)

These are time-bound; clear FIRST on session open.

- **morning_brief 2nd-fire verification (2026-06-26 13:00 UTC = 07:00 MDT)** — first scheduled fire with D3/D4/D5/D6 live. The Session 1234 close-of-arc proof. Verify ALL lane intermediates land in MB workspace, NOT cf708a2e.

  ```python
  from core.models_skin_layer import ProjectWorkspace
  from core.models_deliverables import Deliverable
  from core.models import CeleryTaskEvent
  from datetime import date

  # 1. Beat fire SUCCESS
  ev = CeleryTaskEvent.objects.filter(
      task_name='core.tasks.generate_morning_brief_daily',
      started_at__date=date(2026, 6, 26),
  ).order_by('-started_at').first()
  print('beat status:', ev.status, 'err:', ev.error_message or '-')

  # 2. MB workspace exists
  mb = ProjectWorkspace.objects.get(user__username='chris', name='Morning Brief')

  # 3. All today's chris-owned deliverables land in MB workspace
  qs = Deliverable.objects.filter(user__username='chris', created_at__date=date(2026, 6, 26))
  ws_breakdown = {}
  for d in qs:
      ws_breakdown.setdefault(str(d.workspace_id), 0)
      ws_breakdown[str(d.workspace_id)] += 1
  print('today\'s deliverables by workspace:', ws_breakdown)
  # Expected: all under str(mb.id); none under cf708a2e-8c87-4a13-abfd-fbd34d8e4ee2
  ```

- **Operator Edge newsletter Friday-1 dry-run check (2026-06-26 12:00 UTC)** — Session 1228 carryover. Verify `PeriodicTask.last_run_at` reflects 06-26 12:00 UTC + deliverable created with `status='ready'` or `'preview'`. After 06-26 + 07-03 both pass, flip kwargs to `{'dry_run': False}`.

- **Glance check from Session 1234** (de-scoped during the bug-fix arc): outreach beat first-fire 06-25 13:30 UTC + COOAgent P2 verify same window. Both likely fired during Session 1234; just check `CeleryTaskEvent` for 06-25 success.

#### Priority 2 — Read the brief

If the 06-26 first-fire produced a real Deliverable: **Chris reads the brief**. Rigby provides audience-fit verdict.

Once Chris has read 1-2 briefs:
- Rigby pulls an audience-fit verdict.
- Chris flags specific polish items.
- Each polish item → focused PR.

#### Priority 3 — Sub-step D execution

After Priority 2 surfaces scope, ship the polish PRs. Single small PRs preferred over big rewrites (per Rigby's primitives + opt-in apply-list pattern).

#### Priority 4 — `BACKEND_INVENTORY.md` services count drift refresh

The only currently-active `verify_doc_claims --only-drift` hit. Doc says 167 services; actual 354. One-line PR: update the inventory file's services line. Or regenerate via the inventory command if one exists for that doc. Cheap, closes the drift.

#### Priority 5 — Docs-corpus arc follow-ups (NEW from Session 1234 D9-D16)

All four items closed during Session 1235 (2026-06-25):

- **~~Narrow `search_embeddings` broad `except Exception`~~** — closed by Session 1234 D17-D21 arc (PRs #2627-#2631), narrow-except sweep across 5 files + 4-way invariant lock.
- **~~Fix or retire `search_personal_memories`~~** — **closed by D21 PR #2631** (full rewrite, pivot to `UserEmbedding` ORM, 16 tests). Session 1235 verification surfaced a broader finding: **29 files still reference the dead `unified_embeddings`/`ai_unified_platform` legacy surface** (4 are LIVE-WIRED: `core/views_knowledge.py`, `core/conversation_memory.py`, `core/views.py` embedding-stats block, `dashboard/views.py`). Queued as Session 1236 audit arc (see below).
- **~~Fix the TextProcessor extracted_metadata clobber root cause~~** — closed by Session 1235 PR #2635 (merge-not-overwrite at 4 sites + sync update self-heal path + migration 0047 backfilled 3 LOCAL victims, 2729→2732 scope-keyed).
- **~~Build `core.tasks.refresh_docs_corpus` beat task~~** — closed by Session 1235 PR #2634 (4:00 AM Denver, hash-delta + unembedded-secondary trigger, NOT in LOCAL_DENY, 9 tests). First scheduled fire: 2026-06-26 10:00 UTC MDT.

#### Priority 5.5 — Session 1236 audit arc carry-over (NEW from Session 1235 close)

**Audit name:** *P5#3 drift sweep — eradicate `unified_embeddings`/`ai_unified_platform` legacy surfaces (29 files).*

**Definition of done:** No dead DB/table references remain in production code paths. Remaining references must be in archived scripts/tests only, or deleted.

**Tranche 1 (live-wired, must fix, ship as 4 separate PRs):**
1. `core/views_knowledge.py` — wired in `core/urls.py` at `/api/v1/personal-knowledge/{upload,delete,stats}/`. Silent-empty failure today.
2. `core/conversation_memory.py` — imported by `core/views.py:1094` + `core/views/main.py:925`. Chat-path risk.
3. `core/views.py` embedding-stats block (lines ~1229-1340). API correctness.
4. `dashboard/views.py` + `dashboard/at_a_glance.py` + `dashboard/real_time_monitor.py` embedding counts. UI correctness.

For each PR: require ≥1 "real data" test proving it's not silently returning `[]` anymore.

**Tranche 2 (mgmt cmds, scripts, tests, lower urgency):** `build_rag_corpus.py`, `clean_mythologies.py`, `scripts/{backfill_embeddings,upload_unified_docs}.py`, 3 verification scripts, 8 dead-pattern unit tests.

**Rigby's Session 1236 action:** classify each of the 29 files into {live-wired / live-imported utility / dashboard-only / scripts-mgmt / tests}; produce inventory before Claude opens any PR.

#### Priority 6+ — Pre-existing carryover tail

Unchanged from Session 1234's "what didn't get touched" list:

- **Smoke-harness mode inconsistency** (Session 1231 F5, LOW-MEDIUM) — one-line fix.
- **Smoke-probe tagging for AgentExecution** (Session 1231 F1 / R2 REC-2, MEDIUM).
- **Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents`** (Session 1231 F6, LOW).
- **Audit `5318da3e-…` §R2 amendment** (Session 1231 F3, P3) — `deliverable_tool action=append`.
- **Engineer workspace staleness** (Session 1230 F3, MEDIUM).
- **Meeting-context leak shape watch** (Session 1230 F2, LOW) — still LOW; no recurrence at Session 1234 close.
- **Fleet-smoke wall-clock timeouts** (Session 1231 F2 / R2 REC-3, LOW) — subsumed by smoke-probe filtering.

#### Priority N — CI billing fix (Chris-side, still outstanding)

Carryover from 1223 → 1234.

#### Priority N+1 — Anthropic A/B (gated on credit refill)

When Anthropic credits return: run the same Session 1229 Step 5 line-count task on the Anthropic path (`unset CLAUDE_CODE_ENGINE_PROVIDER`) and confirm no clarification stall. If clean, lift the retry contract up out of the OpenAI-only branch.

#### Priority Last — Whatever Chris wants

Sessions 1226-1234 totaled ~48 PRs across platform hardening + daily-CoS Sub-steps A-C + first-fire fix arc + load-bearing doc framing. Daily-CoS arc Sub-step D awaits Chris's brief read on 06-26 + onward.

**Possible re-ignites (Chris-discretion only):**
- **Fleet sibling apps build-out** — 7 apps at localhost:8002-8008. No work since 1224.
- Audit #5 (PA tool schemas vs handlers — Δ=43) — non-blocking long-tail.
- `scan-spider-opportunities` resume.
- Outreach tone tweak nice-to-haves (Rigby's Session 1225 review).
- **Extend `verify_doc_claims` registration coverage** to the other 472 unwatched docs — the 8 load-bearing got D8 structural framing but most of the doc corpus remains undrift-checked. Slower compound payoff.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222).
- Tier 3 from P2 deliverable `7ae61cf7-…`.

### SESSION 1233 CLOSED — Daily-CoS arc build-out: B.1 → B.1.fix → B.1 smoke verify → B.2 → C, 5 PRs

Full handoff: [`SESSION_1233_DAILY_COS_ARC_BUILD_OUT.md`](docs/handoffs/SESSION_1233_DAILY_COS_ARC_BUILD_OUT.md). Five-PR session closing daily-CoS arc Sub-steps **B.1**, **B.2**, and **C** end-to-end. The morning_brief workflow now runs all 8 steps (rotation_slot_resolve → 4 lanes → decision_card_synthesis → strategic_synthesis morning_brief mode → create_morning_brief_deliverable), produces a real markdown brief, persists into a per-user "Morning Brief" workspace via `_get_or_create_morning_brief_workspace`, and fires daily on Celery beat at `crontab(hour=7, minute=0)` Denver. Sub-step D (polish after Chris's first reads) and E (Mon-Fri dogfood) unlock once Railway produces the first scheduled brief.

| PR | What |
|---|---|
| **#2599** | `feat(session-1233): morning_brief plumbing + Lane 4 slot-driven + decision card + deliverable handler (B.1)`. Three new workflow-internal handlers (lane_4_rotating_focus / decision_card_synthesis / create_morning_brief_deliverable). Strategic_synthesis extended with morning_brief mode reading lane keys + decision_card_text → final brief markdown. _update_context lane plumbing. v0 template Steps 4/5/7 flipped from placeholders to internal handler names. 25 new tests / 25 green. |
| **#2600** | `fix(session-1233): AGENT_MAP fallback acronym alias map (B.1 follow-on)`. Bug surfaced by first B.1 smoke: `coo_agent → CooAgent` not in AGENT_MAP (actual `COOAgent`). New `_AGENT_MAP_SNAKE_ALIASES` covering 4 acronym agents (COO/CTO/SEOOptimizer/AISeriesWorkflow). 6 new tests including source-level audit. Smoking-gun verification of the alias driving the second smoke run's Step 2 success. |
| **#2601** | `docs(session-1233): B.1 + B.1.fix smoke verification evidence`. Evidence doc capturing the smoke that drove PR #2600. Steps 1-3 verified green; Step 4 hung on macOS `mutex.cc:452` (Abseil ML model loading deadlock — environment, not code). `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` didn't help (different system). Steps 5-7 wait on Railway first-fire. |
| **#2602** | `feat(session-1233): rotation_slot_resolve pre-step + override chain (B.2)`. New Step 1 pre-step + priority chain (caller-forced → incident → revenue → signal → calendar → weekday default). Friday alternates via ISO week parity. Tue's `competitor_wedge` deferred. `_get_now_utc()` test seam. Template now 8 steps. 21 new tests / 59/59 green. |
| **#2603** | `feat(session-1233): workspace materialization + daily beat task (Sub-step C)`. `_get_or_create_morning_brief_workspace(user)` idempotent per-user. Deliverable persists with `workspace=workspace`. New `core.tasks.generate_morning_brief_daily(user_id, dry_run)` shared task. Beat schedule at `crontab(hour=7, minute=0)` Denver. Added to `LOCAL_DENY_TASKS` — Railway-only fires. 12 new tests / 71/71 green. |

**Operational invariants (post-#2603 merge):**
1. morning_brief workflow runs end-to-end via Celery dispatch.
2. Persistent "Morning Brief" workspace bootstraps on first fire (per-user, idempotent).
3. Daily Celery beat task at 7:00 AM Denver (Railway-only via LOCAL_DENY_TASKS guard).
4. Telemetry shape locked: task return includes success / workflow / deliverable_id / rotation_slot / lane_4_slot_used / date / user_id / dry_run.
5. Source-level guards (`MorningBriefBeatScheduleRegistrationTests`) sentinel the beat entry + LOCAL_DENY membership.

**Active conversation:** `pa-91cf6bbce1d6406e` — continues from Session 1230 close. Session 1233 added ~25 turns. Mid-session health check: score 75/100, recommendation `continue`. **Likely near rotation threshold given cumulative ~53 turns / ~22k tokens across 1231→1233 — re-check at Session 1234 open.**

**Worker state:** Celery workers restarted at session close per memory rule `feedback_new_shared_task_needs_worker_restart` (PR #2603 added new `@shared_task`). Verified `core.tasks.generate_morning_brief_daily` registered via `celery -A core inspect registered`.

**Still Chris-side carryover into Session 1234:**
- **Anthropic credit refill** at https://console.anthropic.com/billing.
- **CI billing** still failing — all 5 Session 1233 PRs admin-merged.

### FIRST THING Session 1234

#### Priority 1 — Calendar checks (FOUR DUE TODAY OR DAY-AFTER-TOMORROW)

These are time-bound; clear FIRST on session open.

- **morning_brief first-fire verification (2026-06-25 13:00 UTC = 07:00 MDT)** — NEW from Session 1233 PR #2603 merge. The first scheduled `generate_morning_brief_daily` Railway fire. Verify:
  ```python
  CeleryTaskEvent.objects.filter(
      task_name='core.tasks.generate_morning_brief_daily',
  ).order_by('-started_at').first()
  # Expected: SUCCESS, result['success']=True, result['deliverable_id'] non-null,
  # result['rotation_slot'] populated (likely 'ai_infra_deep_dive' for Monday)

  Deliverable.objects.filter(
      user__username='chris', category='Morning Brief',
  ).order_by('-created_at').first()
  # Expected: today's brief, workspace.name='Morning Brief',
  # status='ready', content non-empty markdown

  ProjectWorkspace.objects.filter(
      user__username='chris', name='Morning Brief',
  ).first()
  # Expected: exists post-first-fire, materialized via get_or_create
  ```
- **Outreach beat first-fire verification (2026-06-25 13:30 UTC)** — Session 1228 carryover, P3 across 1230 → 1233. Verify:
  ```python
  CeleryTaskEvent.objects.filter(
      task_name='core.tasks.generate_outreach_drafts_daily',
  ).order_by('-started_at').first()
  # Expected: SUCCESS dated 2026-06-25

  OutreachDraft.objects.filter(
      lead_source='opportunity_outreach_seed',
      created_at__date='2026-06-25',
  ).count()
  # Expected: 1-5
  ```
- **COOAgent P2 behavioral verify (2026-06-25 13:30 UTC, same window)** — Session 1231 P2 close-out. Expect zero `'files_generated'` KeyError on the scheduled daily diagnostic. Run:
  ```python
  AgentExecution.objects.filter(
      agent__name='COOAgent',
      task__icontains='daily COO operations diagnostic',
      created_at__gte='2026-06-25',
  ).order_by('-created_at').first()
  # Expected: status='completed', error_message empty
  ```
- **Operator Edge newsletter Friday-1 dry-run check (2026-06-26 12:00 UTC)** — Session 1228 carryover. Verify `PeriodicTask.last_run_at` reflects 06-26 12:00 UTC + new deliverable created with `status='ready'` or `'preview'` (no auto-publish). After 06-26 + 07-03 both pass, flip kwargs to `{'dry_run': False}`.

#### Priority 2 — morning_brief first-fire READ + Sub-step D scope (NEW)

If the 2026-06-25 first-fire produced a real Deliverable: **Chris reads the brief**. This is the gating input for Sub-step D's polish scope.

Once Chris has read 1-2 briefs:
- Rigby pulls an audience-fit verdict (her "is this readable as a morning brief" review per Session 1233 open ask).
- Chris flags specific polish items (likely candidates: TL;DR length, Decision Card placement, lane-section caps, link formatting, archive sidebar).
- Each polish item → focused PR. Single PRs preferred over big rewrites (per Rigby's primitives + opt-in apply-list pattern from Session 1165).

#### Priority 3 — Sub-step D execution (NEW)

After Priority 2 surfaces the scope, ship the polish PRs. Likely shape per Session 1233 close-out plan: 1-3 PRs depending on the depth of Chris's feedback. If format works out-of-the-box, D collapses into one tight PR and Sub-step E (Mon-Fri dogfood) starts immediately.

#### Priority 4 — Smoke-harness mode inconsistency (CARRYOVER — Session 1231 F5, LOW-MEDIUM)

`core/services/smoke_dispatch.py:39-42` `SMOKE_MODES = {'receipt_only', 'fleet_smoke'}`, but the media-block bypass at `core/tasks_agents.py:2180-2183` only triggers for `mode == 'receipt_only'`. Result: 5 media agents (AudioAgent, ImageEditingAgent, ThreeDAgent, VideoAgent, VideoEditingAgent) silently dropped when dispatched with `mode='fleet_smoke'`. One-line fix: add `or context.get('mode') == 'fleet_smoke'` to the `_receipt_only_ctx` predicate.

#### Priority 5 — Smoke-probe tagging for `AgentExecution` (CARRYOVER — Session 1231 F1 / R2 REC-2, MEDIUM)

Without this, future audits will keep flagging healthy smoke-heavy agents as broken. The R2 deliverable `df33d12d-…` spec'd two implementation options:
- **(a) Add `is_smoke_test: bool` field to `AgentExecution`**, set by dispatcher when task matches substring patterns or `context.smoke=True`. Migration + dispatcher edit + audit-tool consumer updates.
- **(b) Compute at query time** — `execution_history_tool.stats` accepts `include_smoke=False` default and filters via substring matcher. Cheaper; no schema migration.

Substring patterns: `'urc v0.1 fleet smoke'`, `'smoke:'`, `'smoke_test:'`, `'force failure'`, `'expected error'`, `'deliberately request'`, `'deliberately review'`, `'fleet smoke'`, `'smoke test'`.

#### Priority 6 — Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents` (CARRYOVER — Session 1231 F6, LOW)

Currently standalone script. Promote to mgmt command for standard invocation; lets the harness fire from Celery beat for periodic fleet health checks.

#### Priority 7 — Audit `5318da3e-…` §R2 amendment (CARRYOVER — Session 1231 F3, P3)

Append §R2 footnote (or §6.2 sub-section) pointing to deliverable `df33d12d-…`: "Verifier-loop Session 1231 found all 27 R2 rows were smoke probes; no agent code change warranted; recommendation re-framed as metric-quality fix (REC-2)." Trivial via `deliverable_tool action=append`.

#### Priority 8 — Engineer workspace staleness (CARRYOVER — Session 1230 F3, MEDIUM)

Engineer's `/tmp/engineer-workspace/` git clone goes stale. Options: (a) `git pull` to `_ensure_git_repo` if behind upstream, (b) manual `claude_code_tool action=refresh_workspace` opt-in, (c) document as known limitation.

#### Priority 9 — Meeting-context leak shape watch (CARRYOVER — Session 1230 F2, LOW)

Spotted on COOAgent + CTOAgent: `"<Label> Analysis: As a participant in a technical meeting about ..."`. Different prompt template from diagnostic family. One-off so far. Wait to see if it recurs as a cluster.

#### Priority 10 — Fleet-smoke wall-clock timeouts (CARRYOVER — Session 1231 F2 / R2 REC-3, LOW)

3 Workflow rows hit `60min no-heartbeat` or `1200s wall-clock` on full-fleet smokes. Mostly subsumed by Priority 5 (smoke filtering would exclude these too).

#### Priority 11 — CI billing fix (Chris-side, still outstanding)

Carryover from 1223 → 1224 → 1225 → 1226 → 1227 → 1228 → 1229 → 1230 → 1231 → 1232 → 1233.

#### Priority 12 — Anthropic A/B (gated on credit refill)

When Anthropic credits return: run the same Session 1229 Step 5 line-count task on the Anthropic path (`unset CLAUDE_CODE_ENGINE_PROVIDER`) and confirm no clarification stall. If clean, lift the retry contract up out of the OpenAI-only branch.

#### Priority 13 — Whatever Chris wants

Sessions 1226-1233 totaled 41 PRs across platform hardening + the first product wedge build-out. Daily-CoS arc Sub-steps A-C complete; D and E unlock once first-fire produces a Deliverable.

**Possible re-ignites (Chris-discretion only):**
- **Fleet sibling apps build-out** — 7 apps at localhost:8002-8008. No work since 1224.
- Audit #5 (PA tool schemas vs handlers — Δ=43) — non-blocking long-tail.
- `scan-spider-opportunities` resume.
- Outreach tone tweak nice-to-haves (Rigby's Session 1225 review).

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222).
- Tier 3 from P2 deliverable `7ae61cf7-…`.

### SESSION 1232 CLOSED — Daily-CoS arc Sub-step A close + Sub-step B start (v0 workflow template), 2 PRs

Full handoff: [`SESSION_1232_DAILY_COS_ARC_SUB_STEP_A_CLOSE.md`](docs/handoffs/SESSION_1232_DAILY_COS_ARC_SUB_STEP_A_CLOSE.md). Two-PR session executing Session 1231's "FIRST THING Session 1232" Priority 0 (start the daily-CoS product arc). **Sub-step A closed end-to-end** — Rigby consulted on topic mix (pushed back on the daily sports/Kalshi/tickers candidates → counter-proposed 4-lane structure with rotation + override triggers), drafted v1 spec (4 lanes: Platform Readiness + Build Focus + Competitive change-only + Rotating Market + Decision Card synthesis), Chris ratified via "agree all" on a 7-question decision card, doc committed in PR #2596. **Sub-step B started** — v0 `WORKFLOWS['morning_brief']` template added in PR #2597 (7 steps matching spec § "Workflow template skeleton") + 10 contract tests locking v0 shape against the spec. 10/10 new + 6/6 adjacent F4 tests green. v0 is a shape stub — full per-step input plumbing (`rotation_slot_resolve` pre-step + slot-resolved Lane 4 dispatch + override-trigger inputs) lands in Session 1233 Sub-step B follow-on. Both PRs awaiting CI/admin merge (Chris-side CI billing carryover).

| PR | What |
|---|---|
| **#2596** | `docs(session-1232): MORNING_BRIEF_SPEC v1 active — daily-CoS Sub-step A close`. `docs/MORNING_BRIEF_SPEC.md` (270 lines, status `active`, ratified `2026-06-24` by Chris via "agree all"). Captures: 4 lanes + Decision Card + rotation schedule (Mon=AI-infra / Tue=Competitor-deepen / Wed=Tickers / Thu=GTM / Fri=Sports↔Kalshi alternating) + override priority (Incident → Revenue → Signal → Calendar) + per-lane output shape + source agents/feeds + 7-step workflow skeleton + scheduling (13:00 UTC / 07:00 MDT) + Definition of Done. `docs/INDEX.md` regenerated in same PR. |
| **#2597** | `feat(session-1232): WORKFLOWS['morning_brief'] v0 template (Sub-step B start)`. v0 workflow template in `core/services/workflow_orchestration_agent.py:WORKFLOWS['morning_brief']` (7 steps: lane_1_platform_readiness → system_intelligence_agent / lane_2_build_focus → coo_agent / lane_3_competitive_landscape → trend_analysis_agent / lane_4_rotating_focus → research_agent (v0 default for Mon AI-infra slot) / decision_card_synthesis → coo_agent / strategic_synthesis → strategic_synthesis (uses PR #2592 internal handler) / create_deliverable → create_project_from_research). `'morning_brief'` added to `AVAILABLE_WORKFLOWS`. New `core/tests/test_morning_brief_workflow_template.py` — 10 contract tests. 10/10 new + 6/6 adjacent F4 tests (`test_workflow_orchestration_agent_map_fallback`) green. |

**Acceptance criteria from Session 1231 "FIRST THING Session 1232" Priority 0 — all met:**
- [x] `docs/MORNING_BRIEF_SPEC.md` exists, lists 4 lanes + per-topic prompts + output shape, Chris-ratified
- [x] Rigby consulted on topic selection (verifier-loop pattern — her topic-mix rework drove the rotation+overrides structure)
- [x] At least one `morning_brief` workflow template draft exists (v0 in PR #2597)
- [x] Followup F-tags for Sub-steps B-completion / C / D / E rolled into Session 1233 priorities (see Priority 2 below)

**Operational invariants (post-merge — once #2596 + #2597 land):**
1. **Canonical spec exists.** `docs/MORNING_BRIEF_SPEC.md` is the single source of truth for the daily-CoS brief shape.
2. **`morning_brief` is a registered workflow.** Present in `AVAILABLE_WORKFLOWS` + `WORKFLOWS` dict; runner can dispatch its 7 steps via existing AGENT_MAP fallback + internal handlers.
3. **v0 contract tests sentinel the shape.** Any drift (step rename, agent swap, count change) requires updating BOTH spec doc AND test expectations in the same PR.

No behavioral invariants ship this session — v0 workflow template is parsed-and-dispatchable but isn't scheduled yet (Sub-step C) and Lane 4 slot resolution + override-trigger plumbing aren't wired yet (Sub-step B follow-on).

**Active conversation:** `pa-91cf6bbce1d6406e` — continues from Session 1231 close. Session 1232 added 18 turns. `session_tool health_check` at close: score 75/100 / recommendation=continue / 18 turns / ~9k tokens / 3.7h. No rotation triggered. Continues into Session 1233 on this thread.

**Still Chris-side carryover into Session 1233:**
- **Anthropic credit refill** at https://console.anthropic.com/billing. One-liner Makefile revert (`unset CLAUDE_CODE_ENGINE_PROVIDER`) when credits land.
- **CI billing** still failing — both Session 1232 PRs (#2596 + #2597) will need admin-merge if CI is still failing.

### FIRST THING Session 1233

#### Priority 1 — Calendar checks (THREE DUE THIS SESSION, ALL TODAY/TOMORROW)

These are time-bound and the first thing to clear on session open.

- **Outreach beat first-fire verification (2026-06-25 13:30 UTC)** — Session 1228 carryover, P3 in Sessions 1230 → 1232. Verify:
  ```python
  CeleryTaskEvent.objects.filter(
      task_name='core.tasks.generate_outreach_drafts_daily'
  ).order_by('-started_at').first()
  # Expected: SUCCESS dated 2026-06-25
  OutreachDraft.objects.filter(
      lead_source='opportunity_outreach_seed',
      created_at__date='2026-06-25',
  ).count()
  # Expected: 1-5
  ```
- **P2 behavioral verify (2026-06-25 13:30 UTC, same window as outreach)** — first scheduled COOAgent daily diagnostic after PR #2586 merge. Expect zero `'files_generated'` errors going forward. Run:
  ```python
  AgentExecution.objects.filter(
      agent__name='COOAgent',
      task__icontains='daily COO operations diagnostic',
      created_at__gte='2026-06-25',
  ).order_by('-created_at').first()
  # Expected: status='completed', error_message empty
  ```
- **Operator Edge newsletter Friday-1 dry-run check (2026-06-26 12:00 UTC)** — Session 1228 carryover. Verify `PeriodicTask.last_run_at` reflects 06-26 12:00 UTC + new deliverable created with `status='ready'` or `'preview'` (no auto-publish). After 06-26 + 07-03 both pass, flip kwargs to `{'dry_run': False}`.

#### Priority 2 — Daily-CoS arc Sub-step B follow-on (NEW — Session 1232 Sub-step B completion, HIGH)

PR #2597 shipped a v0 template stub. Sub-step B follow-on wires it into a runnable workflow against the full spec:

1. **`rotation_slot_resolve` pre-step** — pure-logic step that computes `rotation_slot` from weekday + override triggers. Either add as Step 0 in the workflow runner OR as an internal handler the runner invokes before Step 4. Reads: current weekday (UTC), incident flag (from Lane 1 result), revenue flag (from `governance_tool.inbox` + meeting calendar), signal flag (from signal aggregation threshold check), calendar flag (from known-events table). Writes: `rotation_slot` enum string.
2. **Slot-resolved Lane 4 dispatch** — change Step 4's agent from the static `research_agent` (v0 default) to a slot-resolved dispatch per spec § "Source (agents + feeds), by slot." Five paths: sports_edge_scan → `sharp_action_detector`; prediction_markets → `prediction_market_analyst`; ticker_catalyst_watch → `stock_analyst_agent`/`market_intelligence_coordinator`; gtm_pipeline → `opportunity_pipeline_agent`; ai_infra_deep_dive → `research_agent`/`trend_analysis_agent`. Override triggers can replace the scheduled slot per the priority order.
3. **Per-step input/write key plumbing** — spec annotates each step's input keys (`window_hours`, `timeframe_hours`, `competitor_shortlist`, `rotation_slot`, `override_triggers`, etc.) and write keys (`lane_N_text`, `lane_N_findings`, `decision_card`, `morning_brief_markdown`, etc.). Wire those into the workflow runner's context-passing so downstream steps can read upstream outputs.
4. **End-to-end smoke** — dispatch one full `morning_brief` run on a chosen weekday slot (e.g., Mon AI-infra) and verify the final deliverable contains all 4 lanes + Decision Card + correct `content_type='morning_brief'` tag + lands in a workspace.
5. **Test additions** — extend `test_morning_brief_workflow_template.py` with input/write key contract tests + a slot-resolution smoke test that mocks the override flags and asserts the right agent is dispatched.

After Sub-step B follow-on lands, the workflow is fully runnable; Sub-step C just adds the scheduler + workspace.

#### Priority 3 — Daily-CoS arc Sub-step C (NEW — schedule + workspace, MEDIUM)

Once Sub-step B follow-on is green:

1. **Create persistent "Morning Brief" workspace** — one workspace, deliverables accumulate over time so Chris can scroll back. Capture the UUID in a tracking deliverable or in the spec doc.
2. **Add `PeriodicTask` row** — `generate-morning-brief-daily` at `crontab(hour=13, minute=0)` UTC during DST (07:00 Denver MDT during summer; flip to `hour=14` during MST). Use the standard explicit-UTC pattern. Session 1228 PRs #2569/#2570 are the TZ trap reference — don't get tripped by the Celery DST behavior.
3. **First-fire verify** — morning after merge, confirm `CeleryTaskEvent` shows SUCCESS + new deliverable in the workspace with the expected 4-lane + decision-card structure.

If Sub-step C lands in Session 1233 (same session as Sub-step B follow-on), Chris's first scheduled morning brief lands the morning after, 2026-06-27 13:00 UTC.

#### Priority 4 — Smoke-harness mode inconsistency (CARRYOVER — Session 1231 F5, LOW-MEDIUM)

`core/services/smoke_dispatch.py:39-42` `SMOKE_MODES = {'receipt_only', 'fleet_smoke'}`, but the media-block bypass at `core/tasks_agents.py:2180-2183` only triggers for `mode == 'receipt_only'`. Result: 5 media agents (AudioAgent, ImageEditingAgent, ThreeDAgent, VideoAgent, VideoEditingAgent) silently dropped when dispatched with `mode='fleet_smoke'`. Re-dispatching with `mode='receipt_only'` produces clean PASSes.

One-line fix: add `or context.get('mode') == 'fleet_smoke'` to the `_receipt_only_ctx` predicate at line 2180-2183. Closes the silent-drop class for fleet-smoke media dispatches.

#### Priority 5 — Smoke-probe tagging for `AgentExecution` (CARRYOVER — Session 1231 F1 / R2 REC-2, MEDIUM)

Without this, future audits will keep flagging healthy smoke-heavy agents as broken — exactly what triggered R2 in audit `5318da3e-…`. The R2 deliverable `df33d12d-…` spec'd two implementation options:
- **(a) Add `is_smoke_test: bool` field to `AgentExecution`**, set by the dispatcher when task matches the substring patterns or `context.smoke=True` is explicit. Cleanest; needs migration + dispatcher edit + audit-tool consumer updates.
- **(b) Compute at query time** — let `execution_history_tool.stats` accept `include_smoke=False` default and filter at metric calc with the same substring matcher. Cheaper; no schema migration.

Pick one + one focused PR. Substring patterns to detect smoke probes: `'urc v0.1 fleet smoke'`, `'smoke:'`, `'smoke_test:'`, `'force failure'`, `'expected error'`, `'deliberately request'`, `'deliberately review'`, `'fleet smoke'`, `'smoke test'`. Also `context.smoke=True` when present.

#### Priority 6 — Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents` (CARRYOVER — Session 1231 F6, LOW)

Currently a standalone script in `scripts/`. Promote to a Django management command for the standard invocation pattern; lets the harness be called from Celery beat for periodic fleet health checks. Same logic, just move + register.

#### Priority 7 — Audit `5318da3e-…` §R2 amendment (CARRYOVER — Session 1231 F3, P3)

Append a brief §R2 footnote (or §6.2 sub-section) pointing to deliverable `df33d12d-…` for the verifier-loop reframe: "Verifier-loop Session 1231 found all 27 R2 rows were smoke probes; no agent code change warranted; recommendation re-framed as metric-quality fix (REC-2)." Trivial via `deliverable_tool action=append` (now correctly bumps `updated_at` post-PR #2585). Mirrors how Session 1230 P2 appended §4.8 to `e2964e4a-…`.

#### Priority 8 — Engineer workspace staleness (CARRYOVER — Session 1230 F3, MEDIUM)

Engineer's `/tmp/engineer-workspace/` git clone is stale (Session 1231 P4 verify `38c2424b-…` couldn't find `build_semantic_research_title` shipped the same day). Options:
- Add `git pull` to `_ensure_git_repo` if behind upstream (small per-dispatch overhead), or
- Add a manual `claude_code_tool action=refresh_workspace` if Rigby should opt in, or
- Document the staleness as a known limitation and have Rigby pass file context explicitly.

Not blocking; small focused PR when bandwidth allows.

#### Priority 9 — Meeting-context leak shape watch (CARRYOVER — Session 1230 F2, LOW)

Spotted on COOAgent + CTOAgent: `"<Label> Analysis: As a participant in a technical meeting about ..."`. Different prompt template from the diagnostic family. One-off so far (not in any duplicates cluster). Don't add markers preemptively — wait to see if it recurs as a cluster, then one entry in `_PROMPT_BODY_MARKERS` closes it.

#### Priority 10 — Fleet-smoke wall-clock timeouts (CARRYOVER — Session 1231 F2 / R2 REC-3, LOW)

3 Workflow rows hit `60min no-heartbeat` or `1200s wall-clock` on full-fleet smokes (~88 agents). Either (a) raise wall-clock for known-smoke workflow dispatches, (b) split fleet smokes into chunks, (c) accept the timeout and stop counting it against the agent. Lower priority — observability not behavior. Most-likely subsumed by Priority 5 (smoke filtering would exclude these too).

#### Priority 11 — CI billing fix (Chris-side, still outstanding)

Carryover from 1223 → 1224 → 1225 → 1226 → 1227 → 1228 → 1229 → 1230 → 1231 → 1232. Both Session 1232 PRs (#2596 + #2597) awaiting admin-merge.

#### Priority 12 — Anthropic A/B (gated on credit refill)

When Anthropic credits return: run the same Session 1229 Step 5 line-count task on the Anthropic path (`unset CLAUDE_CODE_ENGINE_PROVIDER`) and confirm no clarification stall. If Anthropic path is clean with the new `ANSWER_SYSTEM_PROMPT`, lift the retry contract up out of the OpenAI-only branch so both paths get the same safety net.

#### Priority 13 — Whatever Chris wants

Sessions 1226-1232 totaled 36 PRs across platform hardening + the first concrete product wedge (daily-CoS arc). The platform is at **68/68 = 100% production-healthy** across dispatch + workflow-completion contracts. The first product wedge has a ratified spec + v0 workflow template. Next 1-2 sessions should ship Sub-steps B-completion + C so Chris gets his first scheduled morning brief landing the morning after.

**Possible re-ignites (Chris-discretion only):**
- **Fleet sibling apps build-out** — 7 apps at localhost:8002-8008. No work across 1224-1232.
- Audit #5 (PA tool schemas vs handlers — Δ=43) — non-blocking long-tail.
- `scan-spider-opportunities` resume.
- Outreach tone tweak nice-to-haves (Rigby's Session 1225 review).

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222).
- Tier 3 from P2 deliverable `7ae61cf7-…`.

### SESSION 1231 CLOSED — Agent error-pattern investigation arc + full 83-agent fleet smoke + F4/F7/F8 close (P3 + P2 + R2 + P4 + F4 + F7 + F8), 9 PRs

Full handoff: [`SESSION_1231_AGENT_ERROR_PATTERN_INVESTIGATION.md`](docs/handoffs/SESSION_1231_AGENT_ERROR_PATTERN_INVESTIGATION.md). The arc framing from the prior session's Recommended Session 1231 plan ("bundle P2 + R2 + P3 as one agent error-pattern investigation") held end-to-end. **C (P3) shipped first** to make the audit trail honest for the investigation that followed: `deliverable_tool.append` + `update` content-mutation branches were silencing Django's `auto_now=True` on `updated_at` by omitting the field from `update_fields`. **A (P2) shipped next** with the real bug: `core/agents/base_agent.py:5482` did `write_result['files_generated']` via bare dict access in the `elif partial_failure` branch of `execute_with_workspace` — the key only exists in early-return shapes; the all-files-failed shape (Shape B) omits it. The deliverable was getting produced 117ms before the crash, so the daily COO diagnostic looked like a silent failure. **B (R2) closed as no code change** after verifier-loop ORM pull revealed all 18/18 CodeReview + 9/9 Workflow failures over 30d were smoke probes — every one had `task` containing `'fleet smoke'` / `'smoke:'` / `'force failure'` / `'expected error'`. The audit's success_rate metric is noise-contaminated, not the agents. **D (P4) shipped last** in response to Chris's follow-on question "can Rigby trigger each of the Agents and get an output from them?" — built a one-shot full-AGENT_MAP coverage harness (`scripts/smoke_all_agents.py`) that dispatched all 83 entries; surfaced exactly one true production-broken agent (`BookmakerAgent.__init__()` accepted no kwargs but the router calls `agent_class(user=self.user)`). Effective fleet health post-fix: **67 of 68 verifiable production-healthy = 98.5%**.

| PR | What |
|---|---|
| **#2585** | `fix(session-1231): deliverable_tool.append + update content-mutations bump updated_at (P3)`. Three content-mutating branches in `core/services/td_handlers_agents.py` now extend `update_fields` with `'updated_at'`: dedicated `append` action (line 2293), `update`'s `append`/`prepend` sub-mode (line 2122), `update`'s `content` replace sub-mode (line 2129). New `test_deliverable_tool_append_updated_at.py` — 5 tests + source-level guard sentinel. 5/5 new + 24/24 adjacent green. Closes tracking deliv `61f4312b-…`. |
| **#2586** | `fix(session-1231): COOAgent scheduled 'files_generated' KeyError (P2)`. `base_agent.py:5482` bare access raised KeyError on the `elif partial_failure` branch because `_write_files_to_workspace` Shape B (main path) omits `'files_generated'`. Fix computes `total_attempted = total_written + total_failed` from existing Shape B fields. Added `test_all_files_failed_does_not_raise_key_error` + source-level guard `test_partial_failure_path_uses_safe_getters`. 3/3 in `test_base_agent_workspace_write_visibility.py` green. **Behavioral verify window: next scheduled fire 2026-06-25 13:30 UTC.** Closes Session 1230 F1. |
| **#2587** | `docs(session-1231): close handoff + Session 1232 start-here` (first revision — before P4 + full 83-agent smoke landed). The same handoff and start-here doc were updated in-place by the second close pass after #2588. |
| **#2588** | `fix(session-1231): BookmakerAgent constructor accepts user= kwarg + full-AGENT_MAP smoke harness (P4)`. `bookmaker_agent.py:259` — `__init__(self)` → `__init__(self, user=None, **kwargs)`. BookmakerAgent uses `LearningMixin` only (no `BaseAgent` inheritance), so its constructor accepted zero kwargs and crashed on every router dispatch. 4 new tests in `test_bookmaker_agent_constructor.py` (4/4 green). Also bundles `scripts/smoke_all_agents.py` — the one-shot full-AGENT_MAP coverage harness that surfaced the bug. 15-min wall-clock cap; tabulates per-agent status/runtime/error/has_deliverable. |
| **#2589** | `docs(session-1231): handoff + start-here update with PR #2588 + full 83-agent smoke results`. Second close-doc pass after #2588 landed. |
| **#2590** | `fix(session-1231): WorkflowOrchestrationAgent AGENT_MAP fallback for snake_case step names (F4)`. `workflow_orchestration_agent.py:1278+` — replaced catch-all `else` in `_execute_step()` with AGENT_MAP fallback that converts snake_case → PascalCase and dispatches via `AgentRouter.route()`. Unblocks 3 named-AGENT_MAP step names referenced in built-in templates. 6 new tests + source-level guard for internal-handler precedence. 6/6 green. **Post-fix verification (`d9b71e4a`):** ran 148s through steps 1-3 of `business_research` template successfully (vs pre-fix 4s abort at step 1). Aborted at step 4 with the new explicit error format — surfaces F7 (`strategic_synthesis` references non-existent `StrategicSynthesis` agent). Required local celery restart to load new code (per memory rule `feedback_new_shared_task_needs_worker_restart`). |
| **#2591** | `docs(session-1231): handoff + start-here update with PR #2590 F4 close + F7 new`. Third close-doc pass. |
| **#2592** | `fix(session-1231): strategic_synthesis workflow step handler (F7)`. Promoted `strategic_synthesis` from missing-agent to dedicated workflow-internal handler. Reads 10 prior-step context keys, builds synthesis prompt, calls gpt-5-mini at 4000 max_completion_tokens. Graceful empty-context no-op for smoke case. 7 new tests + 1 updated F4 test. 13/13 green. Post-merge verification ran all 4 steps successfully then surfaced F8 (pre-existing latent bug). |
| **#2593** | `fix(session-1231): _compile_final_result None-defense for project_created (F8)`. `(context.get('project_created') or {}).get(...)` at lines 3486 + 3548. Pre-existing latent bug: line 1129 inits `'project_created': None`; `.get(key, default)` returns default only when key is ABSENT, not when present-with-None. Latent since the init; only fired when F7 unblocked the first workflows to reach `_compile_final_result(success=True)` without `create_project_from_research`. 1 new test. 14/14 green. **End-to-end verification (`c5224af7`): WorkflowOrchestrationAgent receipt_only smoke now `status=completed` in 149.6s, zero error.** |

**Full-AGENT_MAP fleet smoke results (`smoke_id=9321b9a13397`):**
- 67 PASS (52 initial + 4 first repoll + 6 second repoll + 5 `mode=receipt_only` re-dispatch)
- 5 FAIL — R1 cascade (odds API credits, Chris-side)
- 1 FAIL — BookmakerAgent (FIXED by #2588)
- 1 FAIL → PASS — WorkflowOrchestrationAgent fully closed by #2590 (F4 case-sensitivity) + #2592 (F7 strategic_synthesis handler) + #2593 (F8 _compile_final_result None-defense). End-to-end verification: `status=completed` in 149.6s, zero error. Pre-fix: failed at step 1 in 4s. Post-#2590: failed at step 4 in 148s. Post-#2592: failed at compile in 155s. Post-#2593: **completed in 149.6s.**
- 8 FAIL — legit shape rejections (CodeReview/DecisionEnforcer/Distribution/Editor/OpportunityPipeline/TalkingCharacter/TechnicalDocument/VoiceCritic — agents correctly refused smoke tasks shaped inappropriately for them)
- 1 BY-DESIGN — CodeGeneratorAgent (disabled on Railway since Session 1031 via `AgentControlEntry`)
- **Net production-healthy: 67/68 = 98.5% post-#2588 → 68/68 = 100% dispatch contract post-#2590 → 68/68 = 100% workflow-completion contract post-#2593.** Zero production-broken agents remain in AGENT_MAP.

**Smoke-harness mode inconsistency surfaced as bonus finding:** 5 media agents silently dropped when dispatched with `mode='fleet_smoke'` because `core/tasks_agents.py:2180-2183` only bypasses the media-spend guard for `mode='receipt_only'`. Adding `fleet_smoke` to the bypass condition is followup F5.

**Deliverables (in-session):**
- **create + append + content_complete `df33d12d-…`** ("Audit / Agent Error Patterns") — R2 verification deliverable. First create attempt hit `gate_2_smoke_pattern` (title contained "smoke"); retitled `"claude-code: R2 Findings — CodeReviewAgent & WorkflowAgent 30-day failure review"`. 476-char stub by Rigby; 8,653-char body appended by Claude via `ToolDispatcher._handle_deliverables`; status flipped via `content_tool action=content_complete`. Final 9,131 chars.

**Diagnostic ORM pulls (verifier-loop input):**
- **CodeReviewAgent 30d**: 23 total / 18 failed / 5 completed. All 18 failures share error `'No code inspection or review completed'`. Tasks classified → **18/18 are smoke probes**.
- **WorkflowAgent 30d**: 11 total / 9 failed / 2 completed. 5 distinct error messages (timeouts + partial-completions). Tasks classified → **9/9 are full-fleet smoke tests** (6 partial-completed include `CodeReviewAgent` as a failing child — same smoke probes counted at the CodeReview row level, dispatched via the fleet harness).

**Bonus finding:** the R2 deliverable's own 8.7kB append was dispatched from the P2-branch checkout (off main, not P3), so it ran on the pre-P3 code path. `updated_at` on `df33d12d-…` is stuck at `2026-06-24T23:00:28.586862+00:00` despite the 9,131-char body — live evidence of the very bug PR #2585 closes. Future appends (post-#2585 merge) bump correctly.

**Operational invariants (post-merge):**
1. `deliverable_tool.append` + `update` content mutations bump `updated_at`. Source-level guards in `test_deliverable_tool_append_updated_at.py` lock the wiring.
2. No more bare `write_result['files_generated']` access on the workspace-write partial-failure path. Source-level guard `test_partial_failure_path_uses_safe_getters` asserts the pattern is absent.
3. CodeReviewAgent + WorkflowAgent are healthy. No production failures in 30d. The audit's 21.7% / 18.2% success rates are smoke-probe noise.

**Active conversation:** `pa-91cf6bbce1d6406e` — continues from Session 1230 close. Session 1231 added ~10 turns. No rotation triggered. Continues into Session 1232.

**Still Chris-side carryover into Session 1232:**
- **Anthropic credit refill** at https://console.anthropic.com/billing. One-liner Makefile revert (`unset CLAUDE_CODE_ENGINE_PROVIDER`) when credits land.
- **CI billing** still failing — both Session 1231 PRs admin-merged.

### FIRST THING Session 1232

#### Priority 0 — START the daily-CoS product arc (NEW — first concrete product wedge for Donkey Betz)

**Strategic shift surfaced at Session 1231 close:** Chris asked "what IS Donkey Betz?" — and the honest answer was "as technology: a real multi-agent platform; as product: undefined." The platform is at 68/68 production-healthy after today's 10 PRs, but the question "which Donkey Betz am I building?" had no answer in the corpus. Chris picked the closest-to-shipping framing: **Daily decision-support / chief-of-staff for solo operators (user 1 = Chris)**.

**One-sentence product pitch:** *"Ask Rigby any strategic question or operational ask. She dispatches the right multi-agent workflow and lands a cited deliverable in your workspace within ~3 minutes. Every morning, a standing brief on your active topics is waiting before you sit down."*

**Why this is the closest-to-product framing:** every piece exists + just got verified end-to-end today (Session 1231 PR #2592/#2593 closed the business_research workflow; `cf708a2e-…` workspace + 5 cited deliverables proves the on-demand path works). Only thing missing is a *standing* brief — a daily flow Chris reads with coffee.

**Arc plan (spans Sessions 1232 → 1235):**

##### Sub-step A (Session 1232 — DO FIRST) — Define standing brief topics with Rigby (~20 min conversation)

Chris and Rigby pick 3-5 topics Chris actually wants briefed every morning. Candidates (Rigby helps refine):

- Donkey Betz competitive landscape (who shipped what overnight in AI agent / autonomous ops platform space)
- AI agent infrastructure space (new frameworks, funding, big releases)
- One-or-two of: sports betting market, prediction markets (Kalshi), specific tickers (NVDA / AMD / etc.), specific founders/companies Chris is tracking
- Internal: any platform broken-state to fix before the day starts (daily diagnostics + body systems + smoke results)

**Output:** a `docs/MORNING_BRIEF_SPEC.md` (or equivalent) naming the 3-5 topics + the prompt per topic + the desired output shape per topic (TL;DR + 3-5 bullets + 1 "act on this" recommendation). Rigby drafts; Chris ratifies.

##### Sub-step B (Session 1232 or 1233) — Build `morning_brief` workflow template

New entry in `WorkflowOrchestrationAgent.WORKFLOWS` named `morning_brief`. One step per Chris-approved topic from Sub-step A. Each step dispatches the appropriate agent (Research + TrendAnalysis + CompetitorAnalysis for external topics; ops_tool / execution_history_tool / system audits for internal). Final step uses the new F7 `strategic_synthesis` handler to produce the consolidated brief.

**Output:** new workflow template + 1 test asserting it runs end-to-end and produces a deliverable with the 3-5 sections.

##### Sub-step C (Session 1233) — Schedule + workspace

- Create persistent "Morning Brief" workspace (one workspace, deliverables accumulate over time — Chris scrolls back through past days)
- Add `PeriodicTask` row: `generate-morning-brief-daily` at **13:00 UTC** (07:00 Denver MDT during summer; switch to 14:00 UTC during MST). Use the standard `crontab(hour=<UTC hour>, minute=0)` pattern. Watch out for the same TZ trap Session 1228 PRs #2569/#2570 fixed.
- Verify first fire (next morning after merge).

##### Sub-step D (Session 1234) — Polish the deliverable shape

After Chris reads the first 1-2 briefs: tweak the output template. Likely needs: tighter TL;DR (≤3 sentences total at the top), clearer "what to do today" action items, links to underlying spider data sources, archive of past briefs sidebar.

##### Sub-step E (Session 1235) — First-week dogfood + iterate

Chris reads Mon-Fri. After 5 days of real read, decide: does the format work? do the topics fit? right cadence? Iterate.

**Definition of done for "Donkey Betz is a product":** Chris reads the morning brief 4 of 5 weekday mornings of one full week without needing to ask Rigby for any topic-specific dispatches separately. At that point we have user 1, daily active usage, and a product pitch that's empirically true.

**Acceptance criteria for Session 1232 Priority 0 specifically:**
- [ ] `docs/MORNING_BRIEF_SPEC.md` exists, lists 3-5 topics + per-topic prompts + output shape, Chris-ratified
- [ ] Rigby has been consulted on topic selection (verifier-loop pattern — her input on what's most useful for Chris's actual day)
- [ ] At least one `morning_brief` workflow template draft exists (even if not yet wired end-to-end)
- [ ] Followup F-tags assigned for Sub-steps B-E so they land on subsequent sessions' priority queues

If Sub-step A reveals the topics are obvious + Sub-step B fits in the same session, ship a v1 `morning_brief` template that runs end-to-end on a chosen topic set. Otherwise scope to Sub-step A only and let B-E carry into 1233-1235.

#### Priority 1 — Calendar checks (BOTH DUE THIS SESSION OR NEXT)

These are time-bound; clear first on session open.

- **Outreach beat first-fire verification (2026-06-25 13:30 UTC)** — Session 1228 carryover, P3 in Sessions 1230-1231. Verify:
  ```python
  CeleryTaskEvent.objects.filter(
      task_name='core.tasks.generate_outreach_drafts_daily'
  ).order_by('-started_at').first()
  # Expected: SUCCESS dated 2026-06-25
  OutreachDraft.objects.filter(
      lead_source='opportunity_outreach_seed',
      created_at__date='2026-06-25',
  ).count()
  # Expected: 1-5
  ```
- **P2 behavioral verify (2026-06-25 13:30 UTC, same window as outreach)** — first scheduled COOAgent daily diagnostic after PR #2586 merge. Expect zero `'files_generated'` errors going forward. Run:
  ```python
  AgentExecution.objects.filter(
      agent__name='COOAgent',
      task__icontains='daily COO operations diagnostic',
      created_at__gte='2026-06-25',
  ).order_by('-created_at').first()
  # Expected: status='completed', error_message empty
  ```
- **Operator Edge newsletter Friday-1 dry-run check (2026-06-26 12:00 UTC)** — Session 1228 carryover. Verify `PeriodicTask.last_run_at` reflects 06-26 12:00 UTC + new deliverable created with `status='ready'` or `'preview'` (no auto-publish). After 06-26 + 07-03 both pass, flip kwargs to `{'dry_run': False}`.

#### Priority 2 — Smoke-harness mode inconsistency (NEW — Session 1231 F5, LOW-MEDIUM)

`core/services/smoke_dispatch.py:39-42` `SMOKE_MODES = {'receipt_only', 'fleet_smoke'}`, but the media-block bypass at `core/tasks_agents.py:2180-2183` only triggers for `mode == 'receipt_only'`. Result: 5 media agents (AudioAgent, ImageEditingAgent, ThreeDAgent, VideoAgent, VideoEditingAgent) silently dropped when dispatched with `mode='fleet_smoke'`. Re-dispatching with `mode='receipt_only'` produces clean PASSes.

One-line fix: add `or context.get('mode') == 'fleet_smoke'` to the `_receipt_only_ctx` predicate at line 2180-2183. Closes the silent-drop class for fleet-smoke media dispatches.

#### Priority 3 — Smoke-probe tagging for `AgentExecution` (NEW — Session 1231 F1 / R2 REC-2, MEDIUM)

Without this, future audits will keep flagging healthy smoke-heavy agents as broken — exactly what triggered R2 in the audit `5318da3e-…`. The R2 deliverable `df33d12d-…` spec'd two implementation options:
- **(a) Add `is_smoke_test: bool` field to `AgentExecution`**, set by the dispatcher when task matches the substring patterns or `context.smoke=True` is explicit. Cleanest; needs migration + dispatcher edit + audit-tool consumer updates.
- **(b) Compute at query time** — let `execution_history_tool.stats` accept `include_smoke=False` default and filter at metric calc with the same substring matcher. Cheaper; no schema migration.

Pick one + one focused PR. Substring patterns to detect smoke probes: `'urc v0.1 fleet smoke'`, `'smoke:'`, `'smoke_test:'`, `'force failure'`, `'expected error'`, `'deliberately request'`, `'deliberately review'`, `'fleet smoke'`, `'smoke test'`. Also `context.smoke=True` when present.

#### Priority 4 — Promote `scripts/smoke_all_agents.py` → `manage.py smoke_all_agents` (NEW — Session 1231 F6, LOW)

Currently a standalone script in `scripts/`. Promote to a Django management command for the standard invocation pattern; lets the harness be called from Celery beat for periodic fleet health checks. Same logic, just move + register.

#### Priority 5 — Audit `5318da3e-…` §R2 amendment (NEW — Session 1231 F3, P3)

Append a brief §R2 footnote (or §6.2 sub-section) pointing to deliverable `df33d12d-…` for the verifier-loop reframe: "Verifier-loop Session 1231 found all 27 R2 rows were smoke probes; no agent code change warranted; recommendation re-framed as metric-quality fix (REC-2)." Trivial via `deliverable_tool action=append` (now correctly bumps `updated_at` post-#2585). Mirrors how Session 1230 P2 appended §4.8 to `e2964e4a-…`.

#### Priority 6 — Engineer workspace staleness (CARRYOVER — Session 1230 F3, MEDIUM)

Carried from Session 1230. Engineer's `/tmp/engineer-workspace/` git clone is stale (P4 verify `38c2424b-…` couldn't find `build_semantic_research_title` shipped the same day). Options:
- Add `git pull` to `_ensure_git_repo` if behind upstream (small per-dispatch overhead), or
- Add a manual `claude_code_tool action=refresh_workspace` if Rigby should opt in, or
- Document the staleness as a known limitation and have Rigby pass file context explicitly.

Not blocking; small focused PR when bandwidth allows.

#### Priority 7 — Meeting-context leak shape (CARRYOVER — Session 1230 F2, LOW)

Spotted on COOAgent + CTOAgent: `"<Label> Analysis: As a participant in a technical meeting about ..."`. Different prompt template from the diagnostic family. One-off so far (not in any duplicates cluster). Don't add markers preemptively — wait to see if it recurs as a cluster, then one entry in `_PROMPT_BODY_MARKERS` closes it.

#### Priority 8 — Fleet-smoke wall-clock timeouts (NEW — Session 1231 F2 / R2 REC-3, LOW)

3 Workflow rows hit `60min no-heartbeat` or `1200s wall-clock` on full-fleet smokes (~88 agents). Either (a) raise wall-clock for known-smoke workflow dispatches, (b) split fleet smokes into chunks, (c) accept the timeout and stop counting it against the agent. Lower priority — observability not behavior. Most-likely subsumed by Priority 3 (smoke filtering would exclude these too).

#### Priority 9 — CI billing fix (Chris-side, still outstanding)

Carryover from 1223 → 1224 → 1225 → 1226 → 1227 → 1228 → 1229 → 1230 → 1231. All Session 1231 PRs admin-merged.

#### Priority 10 — Anthropic A/B (gated on credit refill)

When Anthropic credits return: run the same Session 1229 Step 5 line-count task on the Anthropic path (`unset CLAUDE_CODE_ENGINE_PROVIDER`) and confirm no clarification stall. If Anthropic path is clean with the new `ANSWER_SYSTEM_PROMPT`, lift the retry contract up out of the OpenAI-only branch so both paths get the same safety net.

#### Priority 11 — Whatever Chris wants

Sessions 1226-1231 totaled 34 PRs of platform hardening. The `deliverable_tool` surface is feature-complete + audit-trail honest; diagnostic-family title leak class is closed; engineer behavioral-delta class is closed; COOAgent KeyError class is closed; R2 closed with no code change; F3 amendment outstanding; BookmakerAgent constructor closed; WorkflowOrchestrationAgent F4 + F7 + F8 all closed with end-to-end `status=completed` verification; full fleet smoke verified **68/68 = 100% production-healthy** across both the dispatch contract AND the workflow-completion contract.

**Possible re-ignites (Chris-discretion only):**
- **Fleet sibling apps build-out** — 7 apps at localhost:8002-8008. No work across 1224-1231.
- Audit #5 (PA tool schemas vs handlers — Δ=43) — non-blocking long-tail.
- `scan-spider-opportunities` resume.
- Outreach tone tweak nice-to-haves (Rigby's Session 1225 review).

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files (deferred since Session 1222).
- Tier 3 from P2 deliverable `7ae61cf7-…`.

### SESSION 1230 CLOSED — Diagnostic-family leak close + audit §4.8 F3 amendment + engineer request-mode contract, 4 PRs

Full handoff: [`SESSION_1230_DIAGNOSTIC_LEAK_CLOSE_PLUS_ENGINEER_REQUEST_MODE.md`](docs/handoffs/SESSION_1230_DIAGNOSTIC_LEAK_CLOSE_PLUS_ENGINEER_REQUEST_MODE.md). Two recursion classes closed in one session. **Class 1 — diagnostic-family title leak:** P1 (#2580) wired COOAgent + extended `_PROMPT_BODY_MARKERS` to catch the shared `"You are running the daily X diagnostic. The threshold gate has tripped"` opener (covers `coo_daily.py` / `cto_daily.py` / `trend_analysis_daily.py`). P1b (#2581) wired the three sibling callsites (CTOAgent + TrendAnalysisAgent ×2 + TrendBreakDetectorAgent) with a source-level guard test (`test_diagnostic_family_semantic_title_wiring.py`) that locks the wiring against future regressions. **Class 2 — Engineer OpenAI behavioral delta:** P4 (#2582) split the single SYSTEM_PROMPT into `ANSWER_SYSTEM_PROMPT` + `CHANGE_SYSTEM_PROMPT`, added `request_mode='auto'|'answer'|'change'` kwarg + verb-heuristic dispatcher, and added a clarification-stall retry contract (single retry with hardened preamble; if retry stalls, envelope flips to `status='contract_failure'`). P2 appended a §4.8 amendment to audit deliverable `e2964e4a-…` reframing F3's "blocked default filter" symptom as the real cause: GPT-5.2 autofilling `has_initiative=False` over the old `is not None` gate (closed by Session 1227 PR #2562). Plus one tracking deliverable filed for a `deliverable_tool.append` audit-trail gap.

| PR | What |
|---|---|
| **#2580** | `fix(session-1230): COOAgent semantic title — close prompt-body leak (P1)`. COOAgent `_save_to_deliverable` callsite swaps `f"COO Analysis: {task[:80]}"` for `build_semantic_research_title(task, prefix='COO Analysis')`. Helper markers extended with `'You are running the daily'` + `'The threshold gate has tripped'` (covers all 3 diagnostic prompts). 11 new tests (clean COO tasks, exact audit cluster regression, CTO + Trend sibling shapes, edge cases). 50/50 OK. |
| **#2581** | `fix(session-1230): COO siblings semantic title — close prompt-body leak family (P1b)`. Wires the three remaining sibling callsites: `cto_agent.py:321`, `trend_analysis_agent.py:498` + `:541`, `trend_break_detector_agent.py:799`. New `test_diagnostic_family_semantic_title_wiring.py` source-level guard (3 contract tests: import present, helper called with correct prefix, no `title=f"<Label>: {task[:N]}"` leak pattern; regex scoped to `title=` kwarg so `_thinking()` `reasoning=` log strings aren't flagged). 53/53 OK. |
| **#2582** | `fix(session-1230): engineer request_mode + clarification-stall contract (P4)`. Two-prompt split + `request_mode` plumbed through `pa_tool_schemas.py` → `td_handlers_codejobs.py` → `tasks.py` → `claude_code_engineer.py`. Heuristic uses 18 `_CHANGE_VERBS` (clause-boundary regex, case-insensitive); 8 `_CLARIFICATION_STALL_MARKERS` for the retry contract. Retry contract is OpenAI-path-only until Anthropic credits return + A/B is done. 24 new tests. 32/32 OK. |

**Deliverable updates (in-session):**
- **append `e2964e4a-…`** (Audit) — §4.8 F3 amendment, 2,518 chars, ORM-verified seam at offset 26,472.
- **create `61f4312b-…`** (Platform Bugs) — tracking deliverable for `deliverable_tool.append` updated_at gap (severity P3).

**Rigby live verification at session close** (4 dispatches via `claude_code_tool`):
- `fcdbd982-…` (P1 verify, COO) — new deliverable `461eeb7c-…` titled `"COO Analysis: Brief — 2026-06-24"`. Old leaked rows: 5 / last 7d; new shape: 1. ✓
- `a609214b-…` (P1b verify, CTO) — new deliverable `863d776b-…` titled `"CTO Analysis: Brief — 2026-06-24"`. ✓
- `ea9a89aa-…` (P4 verify, smoking gun, `request_mode=auto`) — heuristic resolved `auto → answer`, direct structured response, zero clarification stall, retry contract did not fire. ✓
- `7e6c267e-…` (P4 verify, `request_mode=change`) — planning response with explicit followup offers; NO branch, NO PR, NO `write_file` invoked. Change-mode contract held. ✓

**Operational invariants (post-merge):**
1. Diagnostic-family title leak class is closed. COO/CTO/Trend/TrendBreak all use `build_semantic_research_title(prefix=…)`. New scheduled fires produce `"<Label>: Brief — YYYY-MM-DD"` (Step-7 capitalization in `_clean_deliverable_title` renders `brief` → `Brief`).
2. Source-level guard test (`test_diagnostic_family_semantic_title_wiring.py`) sentinels the wiring — any future revert to the `f"<Label>: {task[:N]}"` shape fails the test.
3. `claude_code_tool` accepts `request_mode='auto'|'answer'|'change'`. Default `'auto'` resolves via verb heuristic; explicit caller value bypasses; unknown values warn + fall back. Worker log: `[ClaudeEngineer] dispatch: requested_mode=<X> resolved_mode=<Y>`. Response envelope echoes `mode`.
4. Answer-mode clarification-stall triggers single retry with hardened preamble. If retry also stalls, envelope flips to `status='contract_failure'`. Change-mode tasks never trigger retry.

**Active conversation rotated at Session 1230 close:** `pa-4086552cdc9840e9` → **`pa-91cf6bbce1d6406e`** (titled "Session 1231 — Fresh thread (carry-forward from pa-4086552cdc9840e9)"). Old conv carried Sessions 1229 → 1230 — closed at 38 turns / 19k tokens / 2.5h / `suggest_fresh` score 45. New conv seeded with: Session 1230 close (4 PRs + agent audit deliverable `5318da3e-…`), R1 reclassification (SportsOddsAnalyst cascade = upstream odds-API credit-exhaustion, not platform bug), Session 1231 priority queue, tool-surface gap (30d aggregate not in `execution_history_tool.stats`). Wrapper updated; ownership verified `conversation_owner_match: true`.

**Agent System Audit deliverable (Session 1230 close):** `5318da3e-5ac1-43af-9160-d7505ff7c428` in Donkey Betz workspace, 33,786 chars, status `completed`. Six sections + R1 amendment. Authoring shape: Claude wrote §1, §2.1, §3, §4, §5, §6 from direct ORM; Rigby contributed §2 (24h baseline + tool-surface gap callout) since `execution_history_tool.stats` is 24h-only. Key findings: 16 healthy agents + 6 medium-specific healthy + 3 cascade-broken (SportsOddsAnalyst family — credits issue) + 3 other-broken (CodeReview/Workflow/OpportunityPipeline) + 12 silently-failing-invisible (PredictionMarketAnalyst + LegalDocDrafter etc.) + 2 quality-concern + 32 dormant + 7 alias-duplicates. Audit R2 (CodeReview/Workflow error_message investigation) + R3 (wire silently-failing-invisible class to `_save_to_deliverable`) are platform-side load-bearing recommendations for Session 1231+.

**Still Chris-side carryover into Session 1231:**
- **Anthropic credit refill** at https://console.anthropic.com/billing. One-liner Makefile revert (`unset CLAUDE_CODE_ENGINE_PROVIDER`) when credits land. Once active, A/B the Session 1229 line-count task on claude-sonnet-4 vs the Session 1230 fix on gpt-5-mini; if Anthropic-path is clean, lift the retry contract up out of the OpenAI-only branch.
- **CI billing** still failing — all 4 Session 1230 PRs admin-merged.

### FIRST THING Session 1231

#### Priority 1 — Calendar checks (BOTH DUE THIS SESSION OR NEXT)

These are time-bound and the first thing to clear on session open.

- **Outreach beat first-fire verification (2026-06-25 13:30 UTC)** — Session 1228 carryover, P3 in Session 1230. Verify:
  ```python
  CeleryTaskEvent.objects.filter(
      task_name='core.tasks.generate_outreach_drafts_daily'
  ).order_by('-started_at').first()
  # Expected: SUCCESS dated 2026-06-25
  OutreachDraft.objects.filter(
      lead_source='opportunity_outreach_seed',
      created_at__date='2026-06-25',
  ).count()
  # Expected: 1-5
  ```
- **Operator Edge newsletter Friday-1 dry-run check (2026-06-26 12:00 UTC)** — Session 1228 carryover, P3 in Session 1230. Verify `PeriodicTask.last_run_at` reflects 06-26 12:00 UTC + new deliverable created with `status='ready'` or `'preview'` (no auto-publish). After 06-26 + 07-03 both pass, flip kwargs to `{'dry_run': False}`.

#### Priority 2 — COOAgent scheduled `'files_generated'` KeyError (NEW — Session 1230 F1, HIGH)

Pre-existing bug surfaced during P1 live verification. Today's scheduled 13:30 UTC COO dispatch (`f2ecd6f9-…`) failed with `error_message="'files_generated'"`. Manual dispatch via Rigby (`fcdbd982-…`) succeeded — so the bug is specific to the scheduled path, not the agent body itself. Likely in `scheduled_diagnostic_runner.py` (which dispatches all three daily diagnostics) or the COOAgent's output-data envelope handling on the scheduled-runner code path.

Daily diagnostic is currently silently failing on the scheduled path while manual dispatches work. Worth a focused investigation. Diagnostic checklist:
- Read `scheduled_diagnostic_runner.py` for the dispatch shape that breaks vs. PA tool dispatch that works.
- Compare `AgentExecution.input_data` between failed scheduled (`f2ecd6f9`) vs successful manual (`fcdbd982`) dispatches.
- KeyError on `'files_generated'` suggests envelope mismatch — probably an expected key missing from the response dict, or a code path expecting the engineer-style envelope from a non-engineer dispatcher.

#### Priority 3 — `deliverable_tool.append` audit-trail gap (NEW — Session 1230 F4, P3)

Tracking deliverable `61f4312b-…` filed. `append` mutates `content` + `content_length` but does NOT bump `updated_at`. One-line fix in the `append` handler in `td_handlers_*`: `save(update_fields=['content', 'content_length', 'updated_at'])`. Same pattern check needed on `prepend` and any other content-mutating actions. Low blast radius — small focused PR.

#### Priority 4 — Engineer workspace staleness (NEW — Session 1230 F3, MEDIUM)

Engineer's `/tmp/engineer-workspace/` git clone is stale. P4 verification dispatch `38c2424b-…` (build_semantic_research_title docstring lookup) returned "not found" — but the function was shipped today in #2573 and lives at `core/services/deliverable_factory.py:249`. Either:
- Add `git pull` to `_ensure_git_repo` if behind upstream (small per-dispatch overhead), or
- Add a manual `claude_code_tool action=refresh_workspace` if Rigby should opt in, or
- Document the staleness as a known limitation and have Rigby pass file context explicitly.

Not blocking the contract — P4 fix works regardless of content correctness. But surfaces as a separate bug class worth a small PR.

#### Priority 5 — Meeting-context leak shape (NEW — Session 1230 F2, LOW)

Spotted on both COOAgent + CTOAgent: `"<Label> Analysis: As a participant in a technical meeting about \"AC-3 smoke control: empty context"`. Different prompt template family from the diagnostic one. One-off so far (not in any duplicates cluster). Don't add markers preemptively — wait to see if it recurs as a cluster, then one entry in `_PROMPT_BODY_MARKERS` closes it.

#### Priority 6 — CI billing fix (Chris-side, still outstanding)

Carryover from 1223 → 1224 → 1225 → 1226 → 1227 → 1228 → 1229 → 1230. All Session 1230 PRs admin-merged.

#### Priority 7 — Anthropic A/B (gated on credit refill)

When Anthropic credits return: run the same Session 1229 Step 5 line-count task on the Anthropic path (`unset CLAUDE_CODE_ENGINE_PROVIDER`) and confirm no clarification stall. If Anthropic path is clean with the new `ANSWER_SYSTEM_PROMPT`, lift the retry contract up out of the OpenAI-only branch so both paths get the same safety net.

#### Priority 8 — Whatever Chris wants

Sessions 1226-1230 totaled 27 PRs of platform hardening + tool-surface additions + verification + two recursion-class closes. The `deliverable_tool` surface is feature-complete for the audit §4.6 items; the diagnostic-family title leak class is closed (helper + markers + 4 agents wired + source-level guard); the engineer behavioral-delta class is closed (mode split + heuristic + retry contract); the F3 amendment is appended; Rigby's tool surface continues to be exercised every session.

**Possible re-ignites (Chris-discretion only):**
- **Fleet sibling apps build-out** — 7 apps at localhost:8002-8008. No work across 1224-1230.
- Audit #5 (PA tool schemas vs handlers — Δ=43) — non-blocking long-tail.
- `scan-spider-opportunities` resume.
- Outreach tone tweak nice-to-haves (Rigby's Session 1225 review).

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files
- Tier 3 from P2 deliverable `7ae61cf7-…`

### SESSION 1228 CLOSED — LLM-autofill class sweep PR-A + PR-B + outreach/newsletter beat TZ fixes, 4 PRs

Full handoff: [`SESSION_1228_AUTOFILL_SWEEP_PLUS_BEAT_TZ_FIXES.md`](docs/handoffs/SESSION_1228_AUTOFILL_SWEEP_PLUS_BEAT_TZ_FIXES.md). Session opened on Session 1227's Priority 1 (LLM-autofill class-of-bug sweep). Initial grep surfaced ~80 candidate sites; Rigby's triage split into PR-A (semantic safety: write-mode gating + filter overwrites) and PR-B (silent-truncation: int=0 autofill over non-zero defaults). New shared helper `core/services/td_autofill_safety.py` captures the canonical defenses. 49+14=63 new tests; full sweep 72/72 OK; Rigby live verification clean. Mid-session pivot to P2 (outreach beat first-fire verification) revealed the beat **never fired today** — root cause: Session 1225 PR #2548's `crontab(hour=13, minute=30)` was written with a UTC comment but Celery resolved it as Denver-local (`30 13 America/Denver` = 19:30 UTC, six hours late). The **same misinterpretation existed in `generate-operator-edge-newsletter`** (Session 1228 P3 calendar item). Both fixed.

| PR | What |
|---|---|
| **#2567** | Autofill sweep PR-A — new `td_autofill_safety` module; Tier 1 belt-and-suspenders mutation gates on 6 sites (`deliverable_tool.cleanup`, `content_tool.bulk_archive`, `initiative_tool.cleanup_action_items` / `bulk_cleanup` / `bulk_auto_assign`, `autopilot_tool.security_containment_plan`); Tier 2 update-field safety on 4 sites (`list_routes auth_required`, newsletter `manual_fields`, `initiative.create` extras, `task_manager.update description`). 49 new tests. Also fixed a pre-existing schema-vs-handler `dry_run` default mismatch on the two `initiative_tool` bulk actions. |
| **#2571** (re-opened from **#2568**) | Autofill sweep PR-B — falsy-or-default pattern on ~33 `int(payload.get('X', N))` sites across 5 handler files. Highest-risk: `max_runtime_seconds` (autofilled 0 = silent zero-second timeout), `max_chars` (autofilled 0 = empty body), `priority_rank` (autofilled 0 = accidental top-rank), 21 `hours`/`days` lookback params in ops. Source-level sweep guard test catches future reverts. 14 new tests. **#2568 was auto-closed when PR-A's admin-merge deleted its base branch; rebased onto main + re-opened as #2571.** |
| **#2569** | Outreach beat TZ fix — `crontab(hour=13, minute=30)` → `crontab(hour=7, minute=30)`. Now resolves to 7:30 AM Denver = 13:30 UTC during MDT. PeriodicTask row updated via `sync_celery_beat --apply`. |
| **#2570** | Newsletter beat TZ fix — same class. `crontab(hour=13, minute=0, day_of_week='friday')` → `crontab(hour=6, minute=0, day_of_week='friday')`. Friday 06-26 dry-run check now fires at **12:00 UTC** instead of 19:00 UTC. `dry_run=True` kwarg unchanged. |

**Rigby live verification at session close** (full Tool Runs blocks captured in handoff §"Arcs 1+2+3+4"):
- `deliverable_tool action=cleanup` (autofill scenario `dry_run=False`): result stays `dry_run=true`, NO writes triggered. ✓
- `platform_config_tool list_routes auth_required=False`: count matches baseline (no filter), explicit `'false'` string returns 0 public routes. ✓
- `autopilot_tool value_events_report days=0`: returns 744 events (default 7d window) — matches no-arg baseline. ✓

**Operational invariants (post-merge):**
1. No PA tool handler silently flips to write-mode on autofilled `dry_run=False` alone. Belt-and-suspenders requires both `dry_run` falsy AND `confirm=true`.
2. No PA tool handler with `is not None` optional bool filter fires on Python `False` autofill. Use `coerce_optional_bool` from the new shared helper.
3. No PA tool handler returns silent zero from autofilled int=0 over non-zero default. The 33 known offenders all use `int(payload.get('X') or N)`.
4. `generate-outreach-drafts-daily` and `generate-operator-edge-newsletter` PeriodicTask rows are correctly scheduled for Denver-morning slots.

**Active conversation:** `pa-08bdd7c9b348415a` — carried from Session 1226 → 1227 → 1228 with no rotation. Continues into 1229.

**Still Chris-side carryover into Session 1229:**
- **Anthropic credit refill** (https://console.anthropic.com/billing). OpenAI fallback (#2556) continues to function fine; verified during Session 1228 — no observable degradation.
- **CI billing** still failing — all 4 Session 1228 PRs admin-merged.
- **Session 1227's 4 deliverable_tool PRs (#2562-#2566) remain open.** They were Chris's prior work and were not part of Session 1228's authorization. PR #2562 in particular gates the audit deliverable `e2964e4a-…` F3 amendment.

### FIRST THING Session 1229

Two calendar-driven items land first; both validate Session 1228's beat-TZ fixes.

#### Priority 1 — Outreach beat first-fire verification (CALENDAR — 2026-06-25 13:30 UTC)

Tomorrow's first clean fire window. PR #2569 corrected the TZ; the `QueuePreservingScheduler` picks up the updated crontab without beat restart. Verify:
- `CeleryTaskEvent.objects.filter(task_name='core.tasks.generate_outreach_drafts_daily').order_by('-started_at').first()` returns a SUCCESS row dated 2026-06-25.
- `OutreachDraft.objects.filter(lead_source='opportunity_outreach_seed', created_at__date='2026-06-25').count()` is 1–5 (not 0).
- Browser smoke at `/workspace?tab=work&sub=outreach` shows new drafts.

If the count is 0 even with a SUCCESS row, the generator skipped all opps (uncontactable, or daily-cap accounting leak — `DAILY_GENERATE_CAP=5` is enforced inside the generator). If no SUCCESS row at all, the beat scheduler may need a forced reload — `pkill -9 -f "celery -A core beat"; rm -f .celery-beat.pid; make celery`.

#### Priority 2 — Operator Edge newsletter Friday-1 dry-run check (CALENDAR — 2026-06-26 12:00 UTC)

PR #2570 changed the fire time from 19:00 UTC → 12:00 UTC. First Friday of the 2-Friday burn-in. Verify:
- `PeriodicTask.objects.filter(name='generate-operator-edge-newsletter').first().last_run_at` reflects 06-26 12:00 UTC.
- New deliverable created with `status='ready'` or `'preview'` (no auto-publish — kwargs still `{'dry_run': True}`).
- `CeleryTaskEvent` SUCCESS row for `core.tasks.generate_operator_edge_newsletter`.

After 06-26 + 07-03 both pass, flip kwargs to `{'dry_run': False}` to promote to live publishing.

#### Priority 3 — Audit deliverable `e2964e4a-…` F3 amendment

Gated on Session 1227 PR1 (#2562) merge. The audit's F3 finding ("default filter hides `blocked`/most-`archived`, 148 of 300 workspace rows invisible") was the correct *symptom* but the wrong *cause* — Session 1227 PR1's diagnostic log showed the actual culprit was GPT-5.2 autofilling `has_initiative=False` over the old `is not None` gate. Append a brief addendum to the F3 section noting the real cause + reference PR #2562. Trivial via `deliverable_tool action=update` once PR1 lands.

#### Priority 4 — Audit §4.4 P1 upstream `research_agent.py:1103` semantic title fix (S-M)

Carryover from Sessions 1226 → 1227 → 1228. The token gates in `TEMPLATE_LEAK_TITLE_TOKENS` are reactive whack-a-mole. The upstream `title=f"Research: {task[:100]}"` truncation is the source. Generate semantic titles + date/run-id suffix instead.

Session 1227 PR2's `duplicates` action surfaced the prompt-leak clusters are still the heaviest duplicates in DBZ (count=20 / last_7d=16 on the top cluster). They will keep accumulating until this upstream fix lands.

#### Priority 5 — CI billing fix (Chris-side, still outstanding)

Carryover from 1223 → 1224 → 1225 → 1226 → 1227 → 1228. All Session 1228 PRs admin-merged.

#### Priority 6 — Watchdog #5 24-48h re-run (optional drift confirmation)

Carryover from Session 1223. By Session 1229, well past the Tier 1+2 merge window — should be fully drift-clean. Optional.

#### Priority 7 — Outreach tone tweak nice-to-haves (Rigby's Session 1225 review)

3 minor prompt edges Rigby flagged in 1225; deferred until a wider draft sample (10+ generates) reveals which actually matter. Same trio carries.

#### Priority 8 — Whatever Chris wants

Genuinely open. The Session 1228 work closed a recurrence class (autofill) plus a calendar-blocking bug (beat TZ). Sessions 1226-1228 totaled 16 PRs of platform hardening; the surface is in a healthy spot.

**Possible re-ignites (Chris-discretion only):**
- **Fleet sibling apps build-out** — 7 apps at localhost:8002-8008. Credits restored 1224. No app work yet across 1224/1225/1226/1227/1228.
- Audit #5 (PA tool schemas vs handlers — Δ=43) — non-blocking long-tail.
- `scan-spider-opportunities` resume.
- Session 1227's 4 PRs (#2562-#2566) admin-merge if Chris wants the deliverable_tool surface additions live on main.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files
- Tier 3 from P2 deliverable `7ae61cf7-…`

### SESSION 1226 CLOSED — Rigby platform-access unblocking + claude_code_tool wiring repair + verifier-loop deliverables audit, 12 PRs

Full handoff: [`SESSION_1226_RIGBY_PLATFORM_ACCESS_UNBLOCKING.md`](docs/handoffs/SESSION_1226_RIGBY_PLATFORM_ACCESS_UNBLOCKING.md). Session opened pointed at Session 1225 carryover but Chris pivoted mid-session: "the more she can access the platform and the agents, the better the platform will perform." Five PRs in the Tier A unblocking arc, three more in a deep investigation that root-caused the multi-session `claude_code_tool` dispatch failure as a three-layer wiring break (queue topology → macOS pool → conversation_id wiring), THEN a verifier-loop deliverables audit (Rigby + Claude, deliverable `e2964e4a-…`) that surfaced + shipped fixes for an active prompt-leak + agent-name fragmentation. 12 PRs total. Audit produced 26,465 chars across 4 verified parts. New memory rule `feedback_verifier_loop_pattern.md` codifies the workflow shape.

| PR | What |
|---|---|
| **#2550** | `session_tool action=whoami` — closes ownership-verification gap. 6 tests. |
| **#2551** | `deliverable_tool.list has_initiative` filter + `initiative_id` schema fix. 6 tests. |
| **#2552** | Local `code_jobs` worker added to `make celery`. Closes claude_code_tool silent-queue-forever symptom. |
| **#2553** | `code_jobs` worker `--pool=solo` on macOS (prefork SIGSEGVed). |
| **#2554** | `_build_tool_payload` injects `conversation_id` by default. Closes autonomous-engineer post-back wiring. |
| **#2555** | Original session close handoff v1 (covered #2550–#2554). |
| **#2556** | `claude_code_engineer` OpenAI fallback (`CLAUDE_CODE_ENGINE_PROVIDER=openai` routes through gpt-5-mini). Temporary workaround until Anthropic credits land. |
| **#2557** | Audit P0 — added `'this topic using external sources'` to `TEMPLATE_LEAK_TITLE_TOKENS`. Stops 28-per-week ResearchAgent bleed. |
| **#2558** | `pa_local.sh` pin rotation `pa-77bbcd97a625424d` → `pa-08bdd7c9b348415a`. |
| **#2559** | Migration 0365 — canonicalizes 18 rows (1 rigby→Rigby + 17 ClaudeCode→claude-code). Audit F2 history fix. |
| **#2560** | Write-time canonicalization in `deliverable_factory.create_deliverable`. Audit §4.4 P1 enforcement bullet. Lockstep-asserted against migration 0365. |
| **#TBD** | Session close handoff v2 + this start-here rewrite. |

**Audit findings shipped from `e2964e4a-…`:**
- F1 (P0) — New prompt-leak pattern Gate 4 was missing (Cluster #1, 32 rows / 28 in last 7 days, ResearchAgent). Closed by #2557.
- F2 (P1) — Agent identity fragmentation (`Rigby`/`rigby` + `ClaudeCode`/`claude-code`, claude-code ranks #14 → #4 after normalization). Closed end-to-end by #2559 (history) + #2560 (enforcement).
- F3 (deferred to §4.6 backlog) — Tool-layer default filter hides 148 of 300 workspace rows (entire `blocked` status). See Session 1227 P1 below.
- F4 (meta-constraint recorded) — Tokens must be substrings of first ~100 chars of leaked task because of `task[:100]` truncation at research_agent.py:1103.

**Active conversation:** `pa-08bdd7c9b348415a` — rotated mid-session via #2558 after `pa-77bbcd97a625424d` crossed ~28 turns during the audit arc. Owner verified via `session_tool.whoami` (PR #2550): `conversation_owner_match: true`.

**Still Chris-side carryover into Session 1227:**
- **Anthropic credit refill** at https://console.anthropic.com/billing. OpenAI fallback (#2556) keeps autonomous engineer functional until credits land. Once filled: `unset CLAUDE_CODE_ENGINE_PROVIDER` + `pkill -9 -f celery; rm -f .celery*.pid; make celery` reverts to Claude Sonnet 4 path with zero code change.
- **CI billing** still failing — all 12 Session 1226 PRs admin-merged.

### FIRST THING Session 1227

The audit's §4.6 tool-surface backlog is the natural Session 1227 lead (it's the single largest piece of deferred work and converts future audits from ORM archaeology to one-tool-call workflows). Calendar-driven items ride along.

#### Priority 1 — Audit §4.6 tool-surface additions (the lead item, M-L)

Make this kind of audit a tool call, not ORM archaeology. From deliverable `e2964e4a-…` §4.6, in priority order:

1. **`deliverable_tool.list show_all=true` flag** OR remove the default `blocked`/most-`archived` filter — closes F3 (148 of 300 workspace rows hidden today). Smallest ship + biggest accuracy win.
2. **`deliverable_tool.stats full_by_agent=true`** to return the full long-tail (35 distinct values), not top-10. Lets future Rigby audits skip the ORM detour.
3. **`deliverable_tool.duplicates` first-class action** returning `(title, count, first_created_at, last_created_at, last_7d_count, agent_name_distribution, status_distribution)`. Turns Part 3 of this audit into one call.
4. **`deliverable_tool.set_status` action** — un-blocks Rigby's ability to flip away from premature `completed`. No tool currently exists for this.
5. **(Optional) `deliverable_tool.normalize` action** with `dry_run=true` preview — automates future alias-map sweeps.

Effort estimate: each is S individually, but consider grouping (1)+(2) in one PR, (3) in its own, (4) in its own, (5) deferred unless mood strikes.

#### Priority 2 — Outreach daily beat first-fire verification (CALENDAR-PAST — 2026-06-24 13:30 UTC)

PR #2548 (Session 1225) materialized the beat task. First fire was scheduled for 2026-06-24 13:30 UTC, **already past** by Session 1227 open. Verify:
- `CeleryTaskEvent.objects.filter(task_name='core.tasks.generate_outreach_drafts_daily').order_by('-started_at').first()` returns a SUCCESS row
- `OutreachDraft.objects.filter(lead_source='opportunity_outreach_seed', created_at__date='2026-06-24').count()` is 1-5 (not 0)
- Browser smoke at `/workspace?tab=work&sub=outreach` shows new drafts

The outreach generator uses OpenAI/gpt-5-mini (separate from claude_code_engineer's Anthropic dependency), so Anthropic credit state doesn't gate the outreach pipeline. If anything looks off, check the deterministic fallback skeleton fired.

#### Priority 3 — Anthropic credit refill + claude_code_tool revert from OpenAI workaround

Session 1226 closed the wiring chain (#2552/#2553/#2554) AND shipped an OpenAI fallback (#2556) that's currently active. When credits refill at https://console.anthropic.com/billing:

1. `unset CLAUDE_CODE_ENGINE_PROVIDER`
2. `pkill -9 -f celery; rm -f .celery*.pid; make celery`
3. Have Rigby retry `claude_code_tool` with a trivial task; confirm `provider` field is `'anthropic'` (or absent) in the result envelope, no `error 400`, message lands in chat.

The OpenAI fallback is cost-positive but Sonnet 4 is the higher-quality default; flip back once credits allow.

#### Priority 4 — Operator Edge newsletter Friday-1 dry-run check (CALENDAR-DRIVEN — Friday 2026-06-26)

Carried from Sessions 1222 → 1225 → 1226. First Friday post-PR-#2530-merge is **2026-06-26**. Verify the run produced ready/preview state output (no auto-publish). After 2 successful Fridays (06-26 + 07-03), flip kwargs to `{'dry_run': false}`.

#### Priority 5 — Audit §4.4 P1 upstream research_agent.py:1103 fix

Audit recorded: token gates are reactive Whack-A-Mole (the token list now has 5 entries; the upstream bug is one). Stop `title=f"Research: {task[:100]}"` from copying prompt headers verbatim. Generate semantic titles + date/run-id suffix instead. This is what Session 1224 deferred and Session 1226 surfaced again. Worth a focused S-M slice once §4.6 above ships (because §4.6 makes future audits cheaper to confirm the fix held).

#### Priority 6 — CI billing fix (Chris-side, still outstanding)

Carryover from 1223 → 1224 → 1225 → 1226. All Session 1226 PRs admin-merged. When green, normal PR flow returns.

#### Priority 7 — Watchdog #5 24-48h re-run (optional drift confirmation)

Carryover from Session 1223. By Session 1227 this window is ~4 days past Tier 1+2 merge — should be fully drift-clean. Optional confirmation.

#### Priority 8 — Outreach tone tweak nice-to-haves (Rigby's Session 1225 review)

3 minor prompt edges Rigby flagged:
- `ai_automation` Johnson Controls: "(happy-path)" qualifier
- `ai_automation` Ministry of Housing: "and what tools touch it" expansion
- `consulting` Swoon: name concrete inputs

Deferred until a wider draft sample reveals which actually matter.

#### Priority 9 — Whatever Chris wants

Genuinely open. Outreach mature (8 PRs across 1224 + 1225). Hygiene closed. Token budgets aligned. Inbox + beat task functional. Tier A Rigby unblocking shipped. Audit `e2964e4a-…` available as a reference for the verifier-loop pattern Session 1227 may want to re-use.

**Possible re-ignites (Chris-discretion only):**
- **Fleet sibling apps build-out** — 7 apps at localhost:8002-8008. Credits restored 1224. No app work yet across 1224/1225/1226.
- Audit #5 (PA tool schemas vs handlers — Δ=43) — non-blocking long-tail.
- Delete the 9 dormant agent class files (NOT recommended unless re-prioritized).
- `scan-spider-opportunities` resume.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files
- `scan-spider-opportunities` resume
- Tier 3 from P2 deliverable `7ae61cf7-…`

### SESSION 1225 CLOSED — outreach prompt envelope + anti-scrape sanitizer + conversation rotation + daily beat task, 5 PRs

Full handoff: [`SESSION_1225_OUTREACH_REFINEMENT_AND_CONVERSATION_ROTATION.md`](docs/handoffs/SESSION_1225_OUTREACH_REFINEMENT_AND_CONVERSATION_ROTATION.md). Rigby-driven refinement arc on the outreach pipeline shipped in Session 1224 — hard-bound the SYSTEM_PROMPT to a specific per-offer delivery envelope, added an anti-scrape sanitizer to strip RemoteOK PROLIFIC/tag markers before they reach the LLM, rotated the PA conversation after `session_tool.health_check` returned `suggest_fresh` at 39 turns, then closed the Option B daily beat task that had been deferred from Session 1224.

| PR | What |
|---|---|
| **#2544** | Outreach prompt envelope — `OpportunityDraftGenerator.SYSTEM_PROMPT` hard-bound to per-offer delivery scope (ai_automation = 1-day thin-slice prototype with explicit exclusions; consulting = roadmap doc only; content_engine = signal audit + sample pipeline). TONE / GLOBAL / PER-OFFER sections; forbidden-phrase list named; every body ends with scoping question on its own line. Fallback skeleton updated to match (`_FALLBACK_QUESTIONS`). |
| **#2545** | Anti-scrape sanitizer — `_sanitize_lead_text` module helper strips 3 conservative recruiter-board patterns (RemoteOK PROLIFIC/tag clause, bare base64 hashtags, bare `tag <base64>` remnants). Applied at `build_prompt_payload` + draft persistence. Legitimate prose preserved. +6 tests, 23/23 pass. |
| **#2546** | `pa_local.sh` pin rotation: `pa-17e0fa71fd25470a` → `pa-77bbcd97a625424d`. Old pin carried Sessions 1223 → 1224 → first half of 1225 (8 PRs across two sessions). New conversation seeded with full 1224 + 1225 carry-forward; score 100/100 on first health check. |
| **#2547** | Original session close handoff + 00-START-NEXT-SESSION.md rewrite for Session 1226. |
| **#2548** | Outreach drafts daily beat task. New `@shared_task generate_outreach_drafts_daily` + `crontab(hour=13, minute=30)` UTC = 7:30 AM MDT. PeriodicTask materialized + workers restarted + task registered. First fire: 2026-06-24 at 13:30 UTC. |
| **#TBD** | Handoff update appending #2548 to the ledger + 1226 start-here refresh. |

**Final outreach inbox state:** 5 clean drafts, all real LLM, envelope holding, zero scrape-marker leakage. Daily cap 5/5 hit until UTC reset.

**Active conversation rotated:** `pa-17e0fa71fd25470a` → **`pa-77bbcd97a625424d`** (Session 1225 — outreach refinement + ops carryover from 1224). Wrapper updated; ownership implicitly verified by reachability with chris's token.

### FIRST THING Session 1226

The queue has one calendar-driven item:

#### Priority 1 — Operator Edge newsletter Friday-1 dry-run check (CALENDAR-DRIVEN — Friday 2026-06-26)

PR #2530 (Session 1222) re-enabled `generate-operator-edge-newsletter` with `dry_run=True`. First Friday post-merge is **2026-06-26** (3 days from Session 1225 close). Verify the run produced ready/preview state output (no auto-publish). After 2 successful Fridays (06-26 + 07-03), flip kwargs to `{'dry_run': false}` to promote to live.

**Calendar check at session open** — if today is Friday or later, run the verification first. If still pre-Friday, push to whatever lane Chris picks.

#### Priority 2 — Outreach daily beat first-fire watch (CALENDAR-DRIVEN — 2026-06-24 13:30 UTC)

PR #2548 (Session 1225 close) materialized the daily beat task. First fire: **2026-06-24 at 13:30 UTC** (= 7:30 AM MDT on Tuesday, ~9.5 hours after Session 1225 close).

Post-fire verification:
- `CeleryTaskEvent.objects.filter(task_name='core.tasks.generate_outreach_drafts_daily').order_by('-started_at').first()` returns a `SUCCESS` row
- `OutreachDraft.objects.filter(lead_source='opportunity_outreach_seed', created_at__date='2026-06-24').count()` is 1-5 (not 0). Zero = task ran but generator skipped (all opps uncontactable, or daily cap accounting bug). Investigate before next cycle.
- Browser smoke at `/workspace?tab=work&sub=outreach` shows new drafts in the inbox with no manual trigger.

If any check is yellow/red, the rollback is simple: `PeriodicTask.objects.filter(name='generate-outreach-drafts-daily').update(enabled=False)`. Keeps the row, stops firing, no code revert.

#### Priority 3 — Wiring investigations Rigby filed in Session 1225 (low urgency, real friction)

Both are tool-surface gaps Rigby surfaced this session:
- **`claude_code_tool` dispatch doesn't reach Claude Code session** — task ID `0077cd79-…` never landed; Chris had to forward manually for PR #2544 to ship. Investigation: posting into wrong conversation_id? disabled by governor? not integrated to Claude Code's session bus at all?
- **`whoami` / `conversation.owner` endpoint missing** — `conversation_tool.get` schema doesn't expose owner. Can't verify chris-ownership of a fresh conversation through tools. Implicit-by-reachability works but isn't durable.

Both are small ops adds once investigated. Defer to a quiet session.

#### Priority 4 — CI billing fix (Chris-side, still outstanding)

Carryover from 1223 + 1224. GitHub Actions billing still failing — all Session 1225 PRs admin-merged. **Until billing is restored at https://github.com/settings/billing, future PR merges still need `--admin`.** When green, normal PR flow returns.

#### Priority 5 — Watchdog #5 24-48h re-run (optional drift confirmation)

Carryover from 1223. `ops_tool action=failure_signatures window=24h` ~24-48h post Tier 1+2 merge should naturally drift away from `TIMEOUT_WATCHDOG_CLEANUP_*` signatures as pre-merge zombies age out. By Session 1226 this window is ~3 days past — should be fully drift-clean. Optional confirmation; not a blocker.

#### Priority 6 — Outreach tone tweak nice-to-haves (Rigby's draft-by-draft notes)

Rigby flagged 3 minor prompt edges in her tone review:
- `ai_automation` Johnson Controls draft: add "(happy-path)" qualifier to "prototype slice"
- `ai_automation` Ministry of Housing draft: extend the checkpoint question with "and what tools touch it"
- `consulting` Swoon draft: name concrete inputs ("brief interview + review 2-3 sample assets")

These are LLM-output-edge observations. **Defer until a wider draft sample (10+ generates across multiple opps) reveals which actually matter** — chasing single-sample prompt tweaks is the wrong end of the optimization curve.

#### Priority 7 — Upstream `research_agent.py:1103` sanitizer (gated on hygiene audit)

PR #2539 catches the `BINDING DIRECTIVE` leak at the factory layer with structured logging. If Rigby's daily audit (`deliverable_tool search query='BINDING DIRECTIVE' status=ready`) shows zero new hits over 7 days post-1224-merge, the upstream sanitizer stays deferred. If hits appear, ship the upstream fix.

#### Priority 8 — Whatever Chris wants

Genuinely open. Outreach pipeline is mature (8 PRs across 1224 + 1225). Hygiene closed. Token budgets aligned. Inbox functional with real LLM content.

**Possible re-ignites (Chris-discretion only):**
- **Fleet sibling apps build-out** — 7 apps at localhost:8002-8008. Credits restored Session 1224, no time spent on apps in either 1224 or 1225. Pickup unblock: booting the apps + per-app `/api/health` verification.
- Audit #5 (PA tool schemas vs handlers — Δ=43) — non-blocking long-tail.
- Delete the 9 dormant agent class files (NOT recommended unless re-prioritized).
- `scan-spider-opportunities` resume (Session 1222 B2 Mode B chose curate-now).

**Active conversation:** `pa-77bbcd97a625424d` — rotated mid-Session 1225 after the previous pin hit `suggest_fresh` at 39 turns. Fresh score 100/100. Health-check at ~30+ turns or if a heavy multi-PR session looks likely.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Delete the 9 dormant agent class files
- `scan-spider-opportunities` resume
- Tier 3 from P2 deliverable `7ae61cf7-…` (factory-level wrap)

### SESSION 1224 CLOSED — outreach pipeline E2E + hygiene initiative + token budget sweep, 5 PRs

Full handoff: [`SESSION_1224_OUTREACH_PIPELINE_AND_TOKEN_BUDGET_SWEEP.md`](docs/handoffs/SESSION_1224_OUTREACH_PIPELINE_AND_TOKEN_BUDGET_SWEEP.md). Full vertical slice (backend + REST + UI + tests + browser-smoke + real LLM content) for Option B outreach drafts; hygiene initiative `d8d6c0b2-…` closed same-session via gates 4 + 5 at the deliverable factory; cross-cutting `max_completion_tokens` floor sweep after live LLM probe surfaced the silent empty-content bug across 11 sites.

| PR | What |
|---|---|
| **#2539** | Deliverables hygiene — Gate 4 (`gate_4_template_leak`) + Gate 5 (`gate_5_no_relevance`) at `_should_create_deliverable`. 12 unit tests. Closes initiative `d8d6c0b2-…`. |
| **#2540** | Opportunity → OutreachDraft pipeline + Inbox UI (Option B). New `OpportunityDraftGenerator` service, 5 REST endpoints under `/api/cockpit/outreach/*`, new `tab=work&sub=outreach` Workspace surface. 14 unit tests. Tracking deliverable `329165f4-…`. |
| **#2541** | Hotfix: spider-ingested opps use `metadata.url`/`metadata.company` (not `metadata.contact_email`/`metadata.company_name`). Field-name fan-out across contactability gate, prompt payload, and draft persistence. 17/17 tests. |
| **#2542** | `gpt-5-mini max_completion_tokens` floor sweep — 11 sites bumped to 4000 after live probe showed `finish_reason='length'`, `reasoning_tokens=800`, `content=None`. New memory rule `feedback_gpt5_max_completion_tokens_floor.md`. |
| **#TBD** | Session close handoff + this start-here rewrite. |

**Both pre-Session-1224 initiatives closed:** outreach tracking deliverable `329165f4-…` flipped to `completed`; hygiene initiative `d8d6c0b2-…` flipped to `COMPLETED`. Browser smoke produced 5 real LLM-personalized email drafts in the inbox with non-empty content.

### SESSION 1223 CLOSED — audit sweep (15/15) + watchdog burn-in GREEN, 5 PRs

Full handoff: [`SESSION_1223_AUDIT_SWEEP_AND_WATCHDOG_GREEN.md`](docs/handoffs/SESSION_1223_AUDIT_SWEEP_AND_WATCHDOG_GREEN.md). Session 1217 self-directed audit deliverable `bec077ed-…` fully closed (15/15) + Session 1221 watchdog/timeout arc declared green after 5-check burn-in. **No fresh urgent items entering Session 1224.**

| PR | Audit | What |
|---|---|---|
| **#2534** | #8 | Seed baseline drift — Path B (accept Agent.objects=89 as canonical). Loader docstring lie fixed (139 tuples ≠ "149 specialized agents"). New `TestSeedPersonaInvariance` class. |
| **#2535** | #9 | `docs/PLATFORM_WHAT_IT_IS.md` refresh — frontmatter 1141→1223 + count corrections + new "OpenAI hardening — Sessions 1214-1216 + 1221" subsection. |
| **#2536** | #4 | `CRITICAL_PATH_HUB` markers on 4 hub files + new PR-template "Critical-path hub change checklist" + `docs/CRITICAL_PATH_HUBS.md` registry doc. |
| **#2537** | #10 | Atlas TL;DR #6 + Tier 5 intro narrowed per `fleet_health`/`paid_interest_status` runtime evidence (7/7 sibling apps `UNREACHABLE`). Rigby drafted language. |
| **#2538** | — | Session close handoff + this start-here rewrite. |

**Watchdog/timeout arc — declared GREEN.** 5-check burn-in (~3h post-merge of #2519+#2520, local-only): zombie thread rate empty; `LLMCallEvent` stuck rows = 0; `cleanup-stuck-llm-calls` beat firing 10/10 SUCCESS; Tier 1 timeout firing count = 0 across all 4 worker logs; `failure_signatures` 24h yellow-on-literal (pre-merge zombie history dominating window) but green with context. Chris called it green.

### Audit closure summary (Session 1217 deliverable `bec077ed-…`)

**Closed: 15/15** ✅ (full sweep — first time the audit is fully closed since deliverable creation).

Original Chris-picks 1A + 1B + 2 + 3 + A1 + C1 + #3 + B2 + #6 + #7 + bonus dispatcher-trim drift + **Session 1223 same-session sweep of the final tail: #8 (PR #2534) + #9 (PR #2535) + #4 (PR #2536) + #10 (PR #2537)**.

### SESSION 1222 CLOSED (v2 — audit revisit arc) — C1 + #3 + B2 from Rigby's top-3 lean shipped same-session

Full handoff: [`SESSION_1222_V2_AUDIT_REVISIT_CLOSE.md`](docs/handoffs/SESSION_1222_V2_AUDIT_REVISIT_CLOSE.md). Same session as the v1 carryover-queue close — Chris asked us to revisit the original Session 1217 audit deliverable (`bec077ed-…`, 15 findings) after the queue cleared. Rigby's gap analysis + my PR-ledger cross-check produced 8 still-open findings. Chris agree-all'd Rigby's top-3 leverage picks.

| PR | What | Audit finding |
|---|---|---|
| **#2527** | Opportunity pipeline scope clarification (label-only, 3 sites) | C1 |
| **#2528** | `scope='mine'|'all'` param on `opportunity_manager_tool` + owner_breakdown when scope=all | C1 |
| **#2529** | `check-llm-sdk.yml` flipped to enforce (migrated 2 runtime sites, whitelisted 4 operator-only) | #3 |
| **#2530** | Migration 0364 — annotate 4 keep-disabled beat tasks + re-enable `generate-operator-edge-newsletter` w/ `dry_run=True` | B2 |
| **(this PR)** | Session 1222 v2 close handoff + this start-here rewrite | — |

**Both CI checks now in enforce mode:** `check-reasoning-contract.yml` (Session 1222 P3 / PR #2525) + `check-llm-sdk.yml` (this arc / PR #2529).

**Headline finding from C1:** the "2,631 vs 47 inconsistency" was a labeling problem, not a data problem. 2,584 Opportunity rows owned by the `system` user (spider-ingested freelance listings, all <30d) + 47 owned by `chris` (curated subset). Both queries correct; tool surfaces now make scope visible.

**Headline finding from B2:** 5 disabled beat tasks classified per Chris's picks. 4 keep-disabled with operator-readable reason. `generate-operator-edge-newsletter` re-enabled with `dry_run=True` for 2-Friday burn-in then flip to live.

### FIRST THING Session 1223 — pick from the deprioritized audit tail or the watchdog observation window

Two threads worth picking up. Both are quick wins; Rigby's lean is on #6+#7 (S+S) as the natural next quick win after the v2 arc.

#### Priority 1 — Production observation window for Session 1221 Tier 1 + Tier 2 (carryover from v1 close)

Tier 1 (PR #2519) added a total-request bound on `BaseAgent._call_openai`; Tier 2 (PR #2520) added the `LLMCallEvent` cleanup watchdog. Both merged earlier in Session 1222. Real signal needs 24-48h+ of production traffic — by Session 1223 there should be enough data.

The 5 specific checks documented in the v1 close:
1. **Zombie thread rate** — `ops_tool action=zombie_thread_rate hours=48` should still be mostly empty
2. **`LLMCallEvent` stuck STARTED population** — `LLMCallEvent.objects.filter(status='STARTED', started_at__lt=now-10min).count()` should be zero
3. **`cleanup-stuck-llm-calls` beat task firing** — `CeleryTaskEvent` should show runs every 10 min, all SUCCESS
4. **Tier 1 timeout firing rate** — grep PA worker logs for `[base_agent._call_openai] OpenAI total-request timeout`
5. **`ops_tool.failure_signatures window=24h`** — top signatures should not be dominated by `error_type='timeout'` with `watchdog_cleanup`

If any of the 5 are red, queue a Session 1223 fix PR. If all green, the watchdog/timeout story is fully closed.

#### Priority 2 — #6 + #7 docs drift (S+S quick win, Rigby's lean for "small but real")

The Session 1217 audit findings:
- **#6** — `verify_doc_claims --only-drift` shows SERVICES counts drift
- **#7** — Documented 182 management commands vs actual 194 (+12 undocumented)

Both are quick reconciliations:
1. Run `python manage.py verify_doc_claims --only-drift` to see the current drift state.
2. For #6: regenerate the SERVICES count and update the relevant doc.
3. For #7: regenerate the management-command audit (`python manage.py build_management_command_audit` or similar) and either document or delete the 12 undocumented commands.

Both fit as a single PR or two small PRs. ~S+S total effort.

#### Priority 3 — #4 critical hub markers / gates (M)

Audit #4 — reliability work. Flag critical-path files so PRs touching them require extra review. Concrete shape: extend the existing GitHub PR template + add a CODEOWNERS or path-pattern gate. Not blocking but raises the safety bar.

#### Priority 4 — #8 seed baseline drift (M)

`load_all_agents_advisors.py` expectation mismatch — 155 expected agents vs 89 Agent table + 83 AGENT_MAP routable. Re-run seed in a controlled env; update the seed script or drift checker.

#### Priority 5 — #9/#10 narrative + Atlas staleness (M)

`docs/PLATFORM_WHAT_IT_IS.md` frontmatter last reviewed Session 1141 (now 81 sessions behind). `docs/24_7_GLOBAL_AI_APP_ATLAS.md` Phase 1 fleet-integration claims wider than runtime. Refresh + reconcile.

**Active conversation:** `pa-58737666f25741dc` — carried through Sessions 1217-1222.

**Not in audit / deferred / NOT TOUCH:**
- Tier 3 from P2 deliverable (factory-level wrap) — defer per the deliverable
- `scan-spider-opportunities` resume (B2 Mode B chose curate-now)
- Delete the 9 dormant agent class files (per Rigby's keep-for-future recommendation)

### SESSION 1222 CLOSED (v1 — carryover-clear arc) — B2 + 9-class trim + reasoning-contract enforce, 4 PRs

Full handoff: [`SESSION_1222_CARRYOVER_QUEUE_CLEAR.md`](docs/handoffs/SESSION_1222_CARRYOVER_QUEUE_CLEAR.md). All 4 deferred items from Sessions 1216-1218 closed.

| PR | What | Carryover from |
|---|---|---|
| **#2522** | Remove OpenAIProvider class (verification: zero rows all-time across all real_* agents + concrete_executor; zero callers of attached methods) | Session 1217 PR #2507 (B2) |
| **#2523** | Trim 4 zero-exec names from content_studio list + 3 from ops timeout config (Cat A+B) | Session 1218 P2 |
| **#2524** | Drop 3 dormant gateway dispatch actions: `content_tool.sharp_action`, `content_tool.line_movements`, `studio_tool.generate_talking_video` (Cat C). Also removed the 2 unified_pa_entrypoint formatters with their Session-1075-drift sync/async shape mismatch. | Session 1218 P2 |
| **#2525** | Promote `check-reasoning-contract.yml` from `--warn-only` to enforce. Zero violations on main pre-flip. | Session 1216 Phase E |
| **(this PR)** | Session 1222 close handoff + this start-here. | — |

Net delta: **~200 lines removed** from main.

**Tool-surface change visible to users:** the 3 dropped gateway actions no longer appear in `studio_tool` / `content_tool` schemas. The surviving talking-video entry point is `studio_tool.create_talking_video` (different pipeline, generates image + video in one step).

### FIRST THING Session 1223 — production observation window + light-touch carryovers

The watchdog/timeout investigation arc closed in Session 1221; the carryover queue cleared in Session 1222. Session 1223 has no urgent fresh blocker. The natural priority is the observation window for the Session 1221 watchdog fixes (Tier 1 + Tier 2) since real signal needs the burn-in.

#### Priority 1 — Production observation window for Tier 1 + Tier 2 (Session 1221)

Tier 1 (PR #2519) added a total-request bound on `BaseAgent._call_openai`; Tier 2 (PR #2520) added the `LLMCallEvent` cleanup watchdog. Both merged ~2h before Session 1222 opened. Real signal needs 24-48h+ of production traffic.

**Check at start of Session 1223** (pull via `ops_tool` + direct DB queries):

1. **Zombie thread rate** — `ops_tool action=zombie_thread_rate hours=48` should still return mostly-empty `by_agent: {}`. Spikes (>5/hour for any single agent) signal structural hang. **Baseline pre-merge:** ~2 watchdog kills/day across all workers.

2. **LLMCallEvent stuck STARTED population** — direct query `LLMCallEvent.objects.filter(status='STARTED', started_at__lt=now-10min).count()`. **Baseline pre-merge:** 2 stuck rows held 16h and 96h. **Post-Tier-2 target:** zero stuck rows past 10 min (the cleanup watchdog should sweep them).

3. **`cleanup-stuck-llm-calls` beat task firing** — check `CeleryTaskEvent.objects.filter(task_name='core.tasks.cleanup_stale_llm_calls').order_by('-started_at')[:10]` — should see runs every 10 min, all SUCCESS.

4. **Tier 1 timeout firing rate** — grep PA worker logs for `[base_agent._call_openai] OpenAI total-request timeout`. Should be rare or zero. Spikes signal Tier 1 cap is too tight for the agent's actual LLM call duration.

5. **`ops_tool.failure_signatures window=24h`** — top signatures should not be dominated by `error_type='timeout'` with `watchdog_cleanup` in the message. If they are, Tier 2 is sweeping faster than agents can complete.

If any of the 5 checks are red, queue a Session 1223 fix PR. If all green, the watchdog/timeout story is fully closed and the next priority is whichever queue Chris wants to lead with.

#### Priority 2 — Verify the `check-reasoning-contract.yml` enforce flip didn't introduce false positives

First 24-48h of PR CI runs are the canary. Check `gh pr list --state merged --limit 20` for any merged PRs that touched `**/*.py` and verify their `check-reasoning-contract` job passed. False positives → revert to `--warn-only` (single-line PR) and investigate the checker.

**Rollback lever:** re-add `--warn-only` flag at `.github/workflows/check-reasoning-contract.yml:43`. Single-line revert.

#### Priority 3 — Tier 3 from P2 deliverable `7ae61cf7-…` (defer unless observation surfaces leakage)

Wrap the `openai_client_factory` clients at construction time with the same total-request bound that Tier 1 applies per-callsite. Heavier contract change. Defer unless Tier 1 + Tier 2 leakage to non-BaseAgent paths becomes a measurable production issue.

#### Priority 4 — Delete the 9 dormant agent class files (deferred from Session 1222 P2 close)

Per Rigby's recommendation in P2, the 9 agent classes (`SharpActionDetector`, `LineMovementAnalyzer`, `TalkingCharacterAgent`, `ContrarianAgent`, `PerformanceAnalystAgent`, `VoiceCriticAgent`, `ContentDiversityOrchestrator`, `ResolveAgent`, `WhaleWatcherAgent`) stay in `core/agents/` for future re-enable. Pre-flight grep for imports of each class first — they may still be referenced from registries or routing tables. Lower priority than the observation window.

#### Priority 5 — Whatever Chris wants

The deferred queue from Sessions 1216-1218 is empty. Session 1219-1221 watchdog/timeout work is in observation. Session 1222 closed. No fresh urgent items in the start-here.

**Active conversation:** `pa-58737666f25741dc` — carried through Sessions 1217-1222.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Doc-vs-runtime drift triage (audit findings #6/#7/#8)
- Critical-path hub markers (audit finding #4)
- Atlas fleet positioning + narrative staleness (#9/#10)
- Beat schedule disabled tasks classification (Rigby's A4)
- Revenue pipeline aggregation audit (Rigby's C5)

### SESSION 1221 CLOSED — Tier 1 + Tier 2 from 7ae61cf7 shipped same-session

Full handoff: [`SESSION_1221_TIER_1_PLUS_TIER_2_FROM_7AE61CF7.md`](docs/handoffs/SESSION_1221_TIER_1_PLUS_TIER_2_FROM_7AE61CF7.md). Both fixes from the Session 1220 P2 deliverable shipped end-to-end. PeriodicTask materialized + workers restarted + new task verified registered.

| PR | Tier | What |
|---|---|---|
| **#2519** | 1 | Total-request bound on `BaseAgent._call_openai`. New `_run_openai_create_with_total_cap` helper. Cap = `max(180, llm_timeout * 2.5)`. Closes the httpx per-chunk loophole at source for ~80 agents. 6 smoke tests. |
| **#2520** | 2 | `LLMCallEvent` cleanup watchdog. New `cleanup_stale_llm_calls` beat task (10-min cadence, broadcast queue, threshold 10 min). Catches zombies from non-BaseAgent paths via `ops_tool.failure_signatures`. 7 smoke tests. |
| **(this PR)** | — | Session 1221 close handoff + this start-here. |

**Defense-layer story is now end-to-end:** Tier 1 stops the leak at source, Tier 2 catches escapees, the early-save lands the AgentExecution row, the `task_failure` bridge catches Celery failures, the zombie-thread monitor surfaces structural-hang spikes, the original cleanup watchdog is the SIGKILL safety net.

### FIRST THING Session 1222 — carryovers (no fresh blocker)

The watchdog/timeout story closed cleanly this session. Session 1222 priorities are the queue of carryovers from earlier sessions — Chris picks which to lead with.

#### Priority 1 — B2 follow-on for OpenAIProvider (deferred since Session 1217 PR #2507)

Full removal of the `OpenAIProvider` class in `ai_core/agents/agent_llm_integration.py` + the `openai` branch in `AgentLLMIntegration.generate_for_agent`. Requires first proving the `real_*` agent paths are no longer exercised in production. Session 1214 handoff note: "the live path appears to use `AsyncLLMAdapter` directly."

**Verification approach:**
1. Query `AgentExecution.objects.filter(agent__name__in=['RealContentCreator','RealJobExecutor','RealWorkDeliveryEngine','RealClientAcquisition','AIProposalEngine','FreelanceJobAnalyzer'])` for any rows in the last 30d.
2. Cross-reference with `LLMCallEvent.agent_name` for those same agent names.
3. If both are empty → safe to delete. Open PR removing the class + the branch + the `real_*` files.
4. If non-empty → understand the path before deleting. May need a separate session to refactor away from `OpenAIProvider`.

Estimated PR size: ~80 LoC delete + smoke test removal. Single PR.

#### Priority 2 — Trim remaining 9 zero-exec gateway-referenced classes (deferred since Session 1218 P2)

The 9 zero-exec agent classes that stayed in the Session 1218 dispatcher trim because they're still referenced by gateway code:
- `td_handlers_content.py:4160, 4175, 4513`: `ContentDiversityOrchestrator`, `ContrarianAgent`, `LineMovementAnalyzer`, `PerformanceAnalystAgent`, `SharpActionDetector`, `VoiceCriticAgent`
- `td_handlers_ops.py:3472, 3477`: `ResolveAgent`, `TalkingCharacterAgent`, `WhaleWatcherAgent`

Per-site decision per gateway dispatch — replace with a different agent, drop the gateway feature entirely, or upgrade the agent to actually be used. Bigger scope than Session 1218 P2 — likely needs 3-9 small PRs or one umbrella refactor.

#### Priority 3 — Promote `check-reasoning-contract.yml` to enforce mode (P2 carryover from Session 1216)

Currently ships `--warn-only`. Phase C+D close left zero violations on main. Flip to error mode once a clean CI run is verified post Tier 1 + Tier 2 merges.

```yaml
# .github/workflows/check-reasoning-contract.yml
# Change `--warn-only` to nothing, set continue-on-error: false.
```

Estimated PR size: 2-line workflow change + verification run. Single PR.

#### Priority 4 — Tier 3 from P2 deliverable (defer)

Wrap the openai_client_factory clients' `chat.completions.create` at construction time with the same total-request bound. Mirror of the Session 1216 Phase E `reasoning_guard` surgery. Defers because Tier 1 + Tier 2 should be sufficient for the dominant code path — only ship Tier 3 if leakage to non-BaseAgent paths becomes a measurable problem post-merge.

#### Priority 5 — Production observation window for the watchdog fixes

Pre-merge state: 15 watchdog-killed AgentExecution rows last 7d, 2 stuck STARTED LLMCallEvent rows held 16-96h.

Post-merge target: zero new stuck LLMCallEvent rows past 10 min, watchdog-kill rate down by ≥80%.

Recommended check at start of Session 1222: pull the rates via `ops_tool` and compare against the deliverable `7ae61cf7-…` baselines.

**Active conversation:** `pa-58737666f25741dc` — carried through Sessions 1217-1221.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Doc-vs-runtime drift triage (audit findings #6/#7/#8)
- Critical-path hub markers (audit finding #4)
- Atlas fleet positioning + narrative staleness (#9/#10)
- Beat schedule disabled tasks classification (Rigby's A4)
- Revenue pipeline aggregation audit (Rigby's C5)

### SESSION 1220 CLOSED — Zombie monitor (P1) + two detector fixes + OpenAI httpx investigation (P2)

Full handoff: [`SESSION_1220_ZOMBIE_MONITOR_PLUS_HTTPX_INVESTIGATION.md`](docs/handoffs/SESSION_1220_ZOMBIE_MONITOR_PLUS_HTTPX_INVESTIGATION.md). 3 code PRs + 1 docs close + 1 investigation deliverable.

| PR | What |
|---|---|
| **#2515** | P1 — Zombie-thread monitor. New `core/services/zombie_thread_monitor.py` + `ops_tool.zombie_thread_rate` action. Wired into both `_FuturesTimeout` catch sites. 11 smoke tests. |
| **#2516** | Redactor fix — phone regex was matching bare 10-digit YYYYMMDDHH timestamps. Surfaced by P1 live test. 4 new regression tests. |
| **#2517** | Detector guard — Session 1199's silent-fallback regex flagged legit tool-result echoes. New `_should_trigger_silent_fallback(text, tool_runs)` helper. 7 new tests. |
| **(this PR)** | Session 1220 close handoff + this start-here rewrite. |

**P2 investigation deliverable** (closes the open question from Session 1219 P3):

| ID | Title | Final size |
|---|---|---|
| `7ae61cf7-…` | Session 1220 P2 — OpenAI httpx read-timeout bypass investigation | **7,499 chars** |

**P2 headline finding:** `httpx.Timeout(read=90s)` is **per-chunk**, not **total request**. GPT-5.x reasoning models stream slowly enough to never trip it. Runtime evidence in `LLMCallEvent`: 102.7s and 90.9s calls completed SUCCESS (would have raised if `read=90` were a total bound) + 2 stuck STARTED rows held open 16h and 96h. One stuck row's `execution_id` matches a Session 1219 P3 watchdog-killed `AgentExecution` — proof the LLM call kept running for hours after the ThreadPoolExecutor wall-clock raised.

### FIRST THING Session 1221 — Tier 1 + Tier 2 from P2 deliverable

#### Priority 1 — Tier 1 from P2 deliverable: total-request bound on `_call_openai`

Wrap `core/agents/base_agent.py:_call_openai` (~line 2589, the `self.client.chat.completions.create(**create_kwargs)` call) in a thread-pool future with a total cap.

**Suggested cap:** `max(180, self.llm_timeout * 2.5)` seconds. For AudioAgent (`llm_timeout=60s`), that's 180s — well below the agent's 300s wall-clock, so the agent has time to handle the failure cleanly. For ContentWriterAgent (`llm_timeout=180s`), that's 450s — still safely below the 600s wall-clock.

**Approach:**

```python
import concurrent.futures as _cf
def _call_openai(self, prompt, ...):
    ...
    cap = max(180.0, getattr(self, 'llm_timeout', 60.0) * 2.5)
    with _cf.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(self.client.chat.completions.create, **create_kwargs)
        try:
            response = future.result(timeout=cap)
        except _cf.TimeoutError:
            raise TimeoutError(
                f"OpenAI total-request timeout after {cap}s in {self.name}"
            )
    ...
```

**Important nuance:** the underlying httpx request will keep running (same zombie-thread mechanic as Phase 3 cf80d413). But the *caller* returns cleanly to the dispatcher, which writes the failed status via Session 1219 PR #2513's early-save path. The zombie thread eventually returns when the OpenAI server finishes or the connection drops at OS level. `--max-tasks-per-child` recycling still provides the floor.

**Smoke test scope:** mock `self.client.chat.completions.create` to sleep > cap, verify `TimeoutError` raises and the message names the cap value.

Single call site change covers ~80 agents that route through `BaseAgent`. Independent agents that don't inherit from `BaseAgent` would still need their own wrap — that's a follow-on PR if any are found.

#### Priority 2 — Tier 2 from P2 deliverable: `LLMCallEvent` cleanup watchdog

Mirror of `core/tasks_agents.py:_impl_cleanup_stale_agent_executions`. Scan `LLMCallEvent` rows where `status='STARTED'` and `started_at < now - T` (suggested T=600s = 10 min). Mark them `status='FAILED'` with `error_type='timeout'` and `error_message='watchdog_cleanup'`.

**Implementation point:** add as a new `@shared_task` next to the existing cleanup task. Add to `core/celery.py:app.conf.beat_schedule` to run every 30 min (mirror of the existing watchdog cadence). Use `add_critical_celery_tasks` to materialize the PeriodicTask row.

**Why this helps:** `ops_tool.failure_signatures` already aggregates by `error_type`. Once stuck LLMCallEvent rows are marked timeout, the existing aggregator surfaces them without dashboard work. Lets us verify Tier 1 is reducing the stuck-row population over time.

**Smoke test scope:** insert a stuck LLMCallEvent row with `started_at = now - 700s`, run the cleanup task, verify the row flips to FAILED.

#### Priority 3 — B2 follow-on for OpenAIProvider (deferred since Session 1217 PR #2507)

Full removal of `OpenAIProvider` class + `openai` branch in `generate_for_agent`. Requires first proving the `real_*` agent paths are no longer exercised in production. Check `AgentExecution` rows for `real_content_creator`, `real_job_executor`, `real_work_delivery_engine`, `real_client_acquisition`, `ai_proposal_engine`, `freelance_job_analyzer`, `concrete_executor` agent names + cross-ref with the Session 1214 handoff note.

#### Priority 4 — Trim remaining 9 zero-exec gateway-referenced classes (deferred since Session 1218 P2)

`ContentDiversityOrchestrator`, `ContrarianAgent`, `LineMovementAnalyzer`, `PerformanceAnalystAgent`, `SharpActionDetector`, `VoiceCriticAgent`, `ResolveAgent`, `TalkingCharacterAgent`, `WhaleWatcherAgent`. Per-site decision per gateway dispatch.

#### Priority 5 — Promote `check-reasoning-contract.yml` to enforce mode (P2 carryover from Session 1216)

Currently `--warn-only`. Verify zero violations on main, then flip.

**Active conversation:** `pa-58737666f25741dc` — carried through Sessions 1217-1220.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Doc-vs-runtime drift triage (audit findings #6/#7/#8)
- Critical-path hub markers (audit finding #4)
- Atlas fleet positioning + narrative staleness (#9/#10)
- Beat schedule disabled tasks classification (Rigby's A4)
- Revenue pipeline aggregation audit (Rigby's C5)

### SESSION 1219 CLOSED — Watchdog fix 3-phase ship: bridge + early-save + zombie-thread investigation, all 3 phases shipped same-day

Full handoff: [`SESSION_1219_WATCHDOG_FIX_3_PHASE_SHIP.md`](docs/handoffs/SESSION_1219_WATCHDOG_FIX_3_PHASE_SHIP.md). Chris specified a 3-phase fix plan; executed exactly to spec.

| PR | Phase | What |
|---|---|---|
| **#2512** | 1 | `task_failure` → `AgentExecution` bridge in `core/celery_telemetry.py`. Catches `SoftTimeLimitExceeded` / generic exception paths. 5 smoke tests. |
| **#2513** | 2 | Wall-clock-timeout early-save in both `_FuturesTimeout` handlers (`tasks_agents.py` + `agent_router.py`). Renamed `timeout_source='agent_wall_clock'` for attribution clarity. 3 lock-in tests. |
| **(this PR)** | — | Session 1219 close handoff + Session 1220 start-here. |

**Phase 3 investigation deliverable:**

| ID | Title | Final size |
|---|---|---|
| `cf80d413-1f35-44a9-9763-6bc5f3a93916` | Session 1219 P3 — Zombie agent thread investigation | **7,289 chars** |

**Three timeout-source attributions now distinguished:** `agent_wall_clock` (Celery-task path), `router_wall_clock` (direct router path), `watchdog_cleanup` (beat task swept stale row).

**Phase 3 finding:** `ThreadPoolExecutor.shutdown(wait=False)` doesn't kill the agent thread — Python has no API for it. Worker recycling via `--max-tasks-per-child` is the only cleanup. Empirical zombie rate ~2/day. Recommended Option D (monitor + status quo) over heavier alternatives (per-task subprocess, signal-based kill, cooperative cancellation). Phases 1 + 2 already close the visible symptom (orphaned DB rows).

**Open question deferred:** Why doesn't the OpenAI httpx 90s read timeout catch the zombie BEFORE the 300s+ wall-clock fires for short-budget agents like AudioAgent?

### FIRST THING Session 1220 — open items from Session 1219 P3 + carryovers

#### Priority 1 — Ship the zombie-thread monitor (Phase 3 Option D)

Small ~10 LoC + ops_tool integration recommended in deliverable `cf80d413-…`. At both `_FuturesTimeout` catch sites (`tasks_agents.py:2425` + `agent_router.py:1551`), increment a per-worker, per-hour counter via Django cache:

```python
from django.core.cache import cache
zombie_key = f'zombie_threads:{agent_name}:{datetime.utcnow().strftime("%Y%m%d%H")}'
cache.incr(zombie_key, 1)
```

Then expose `ops_tool.zombie_thread_rate` returning a per-hour breakdown for the last N hours. Alert on >5 zombies/hour for any single agent — that's a structural-hang signal (upstream LLM provider degraded, spider source down, etc.).

#### Priority 2 — Investigate OpenAI httpx timeout bypass (open question from Phase 3)

If `core/services/openai_client_factory.py` correctly sets `read=90s, connect=20s, write=60s, pool=60s` and the OpenAI call respects them, AudioAgent's `_wall_timeout=300s` should never fire — the agent body would have already raised `APITimeoutError` cleanly. The fact that AudioAgent ran 4000s+ before being caught suggests the OpenAI call itself was bypassing its httpx timeout.

**Hypotheses:**
1. **httpx `pool=60s` wait queue** — the pool timeout only catches "no connection available" cases, not "stuck on existing connection."
2. **Response streaming hung mid-body** — the `read=90s` deadline only applies between chunks, so a stream that delivers a single byte every 89s would never time out.
3. **Connection-pool exhaustion at the OpenAI httpx client level** — held connections from previous zombies prevent new ones.

Pull the OpenAI client's TCP/HTTP timeline for a few zombie-killed AudioAgent runs (Wireshark / `tcpdump` if production-accessible, else strace the worker process). Or: add per-call elapsed timing inside `base_agent._call_openai` and check for outliers above the configured read timeout.

#### Priority 3 — B2 follow-on for OpenAIProvider (deferred since Session 1217 PR #2507)

Full removal of the `OpenAIProvider` class + `openai` branch in `generate_for_agent`. Requires first proving the `real_*` agent paths are no longer exercised in production. Session 1214 handoff note: "the live path appears to use `AsyncLLMAdapter` directly." Verify by checking `AgentExecution` rows for `real_content_creator`, `real_job_executor`, `real_work_delivery_engine`, `real_client_acquisition`, `ai_proposal_engine`, `freelance_job_analyzer`, `concrete_executor` agent names + cross-ref with the spec.

#### Priority 4 — Trim the remaining 9 zero-exec gateway-referenced classes (deferred since Session 1218 P2)

The 9 zero-exec classes that stayed in Session 1218 PR #2510 because they're still dispatched by gateway code:
- `ContentDiversityOrchestrator`, `ContrarianAgent`, `LineMovementAnalyzer`, `PerformanceAnalystAgent`, `SharpActionDetector`, `VoiceCriticAgent` (called from `td_handlers_content.py:4160, 4175, 4513`)
- `ResolveAgent`, `TalkingCharacterAgent`, `WhaleWatcherAgent` (called from `td_handlers_ops.py:3472,3477` + `td_handlers_core.py:1009`)

Refactor the gateway dispatch sites first. Per-site decision: replace with a different agent, drop the gateway feature entirely, or upgrade the agent to actually be used.

#### Priority 5 — Promote `check-reasoning-contract.yml` to enforce mode (P2 carryover from Session 1216)

Currently ships `--warn-only`. Phase C+D close left zero violations on main. Flip to error mode once a clean run is verified post Phase 1 + 2 watchdog merges.

**Active conversation:** `pa-58737666f25741dc` — same thread carried through Sessions 1217 / 1218 / 1219. Continue here unless you want a fresh thread.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Doc-vs-runtime drift triage (audit findings #6/#7/#8)
- Critical-path hub markers (audit finding #4)
- Atlas fleet positioning + narrative staleness (#9/#10)
- Beat schedule disabled tasks classification (Rigby's A4)
- Revenue pipeline aggregation audit (Rigby's C5)

### SESSION 1218 CLOSED — Watchdog investigation + dead-weight trim, both shipped in one session

Full handoff: [`SESSION_1218_WATCHDOG_INVESTIGATION_AND_DEAD_WEIGHT_TRIM.md`](docs/handoffs/SESSION_1218_WATCHDOG_INVESTIGATION_AND_DEAD_WEIGHT_TRIM.md). Chris reordered Session 1218 priorities (P3 → P2). Both items shipped.

| PR | What |
|---|---|
| **#2509** | INDEX.md regen after Session 1217 PR merges |
| **#2510** | P2 — Trim 22 zero-execution agents from PA dispatcher. `run_agent` enum 80 → 58, handler count 174 → 152. Zero functional impact. |
| **(this PR)** | Session 1218 close handoff + this start-here rewrite |

**Investigation deliverable populated:**

| ID | Title | Final size |
|---|---|---|
| `6b00c112-…` | Session 1218 P3 — Watchdog 3600s timeout root-cause investigation | **7,325 chars** |

**Headline findings:**
1. **"3600s watchdog timeout" is NOT a single timeout.** It's the cleanup-watchdog beat tick (~30 min) catching `AgentExecution` rows whose 60-min staleness threshold has been exceeded. Empirical data (last 7d): 15 watchdog-killed rows, agent elapsed times exceed each agent's wall-clock timeout by 6-13× — wall-clock didn't fire for any of them.
2. **The leak path:** `SoftTimeLimitExceeded` (3600s) and SIGKILL (3900s) bypass the normal `_FuturesTimeout` cleanup in `tasks_agents.py:2425`. The Celery `task_failure` signal updates `CeleryTaskEvent` but never touches `AgentExecution` — leaving rows orphaned until watchdog cleanup.
3. **Recommended fix (documented, not shipped):** Add a `task_failure.connect` handler in `core/celery_telemetry.py` that marks AgentExecution rows associated with the failed Celery task_id as failed. ~30 line PR + smoke test. See deliverable `6b00c112-…` for full code stub.
4. **Dead-weight trim:** original audit said 31 zero-exec classes; pre-flight grep found 9 still referenced by gateway code (`td_handlers_content.py`, `td_handlers_ops.py`, `td_handlers_core.py`). **22 truly safe → trimmed.**

### FIRST THING Session 1219 — open items from Session 1218

#### Priority 1 — Ship the `task_failure.connect` watchdog fix (P3 follow-on)

Lead deliverable for context: `6b00c112-5fa9-4414-acf2-6d1b05cd9a1f` (Session 1218 P3 investigation). The recommended fix is a small surgical PR (~30 lines + smoke test):

```python
# core/celery_telemetry.py
@task_failure.connect
def on_agent_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    """Mark AgentExecution rows associated with the failed Celery task as failed.
    Closes the gap where Celery hard/soft time-limits leave rows in 'in_progress'."""
    try:
        rows = AgentExecution.objects.filter(
            status__in=('running', 'in_progress'),
            input_data__celery_task_id=str(task_id),
        )
        rows.update(
            status='failed',
            error_message=f'Celery task failed: {type(exception).__name__}: {str(exception)[:200]}',
            completed_at=timezone.now(),
        )
    except Exception:
        logger.exception(f"[celery_telemetry] AgentExecution failover for {task_id} failed")
```

**Smoke test scope:** dispatch a task that raises a known exception (or triggers SoftTimeLimitExceeded), assert the AgentExecution row flips to status='failed' with the expected error_message format.

**Caveats:**
- Won't catch true SIGKILL cases (those are an unsolvable artifact of Celery's hard time_limit). But will catch all `SoftTimeLimitExceeded` cases and most `worker_lost` cases.
- Doesn't address the deeper question of *why* per-agent wall-clock timeouts (`_future.result(timeout=300s)` for AudioAgent) don't fire when the agent runs 4000s. That's a separate investigation — defer.

#### Priority 2 — B2 follow-on for OpenAIProvider (deferred from Session 1217 PR #2507)

Full removal of the `OpenAIProvider` class + `openai` branch in `generate_for_agent`. Requires first proving the `real_*` agent paths are no longer exercised in production. Session 1214 handoff note: "the live path appears to use `AsyncLLMAdapter` directly." Verify by checking `AgentExecution` rows for `real_content_creator`, `real_job_executor`, `real_work_delivery_engine`, `real_client_acquisition`, `ai_proposal_engine`, `freelance_job_analyzer`, `concrete_executor` agent names + cross-ref with the spec.

#### Priority 3 — Trim the remaining 9 zero-exec gateway-referenced classes

The 9 zero-exec classes that stayed in (Session 1218 P2 PR #2510 left them) because they're still dispatched by gateway code:
- `ContentDiversityOrchestrator`, `ContrarianAgent`, `LineMovementAnalyzer`, `PerformanceAnalystAgent`, `SharpActionDetector`, `VoiceCriticAgent` (called from `td_handlers_content.py:4160, 4175, 4513`)
- `ResolveAgent`, `TalkingCharacterAgent`, `WhaleWatcherAgent` (called from `td_handlers_ops.py:3472,3477` + `td_handlers_core.py:1009`)

To remove them safely, refactor the gateway dispatch sites first. Bigger scope than Session 1218 P2 — needs per-site decision: replace with a different agent, drop the gateway feature entirely, or upgrade the agent to actually be used.

#### Priority 4 — Investigate wall-clock-timeout non-firing (P3 deferred deeper question)

Why do `_future.result(timeout=300s)` for AudioAgent (and similar for SystemIntelligenceAgent at 600s, ContentWriterAgent at 600s) not fire when the agent runs 4000s+? The ThreadPoolExecutor + future.result interaction with Celery's SoftTimeLimitExceeded signal is the suspected mechanism but needs analysis. Possibly: Celery raises SoftTimeLimitExceeded INTO the main thread while the agent body is in the worker thread; the main thread might catch + ignore it; the wall-clock timeout never gets a chance to fire because `_future.result(timeout=...)` has already raised.

**Active conversation:** `pa-58737666f25741dc` — same thread carried through Sessions 1217-prep + 1217-execution + 1218. Continue here for Session 1219 unless you want a fresh thread.

**Not on Chris's pick — DO NOT touch unless explicitly re-prioritized:**
- Promote `check-reasoning-contract.yml` to enforce mode (P2 carryover from Session 1216)
- Doc-vs-runtime drift triage (audit findings #6/#7/#8)
- Critical-path hub markers (audit finding #4)
- Atlas fleet positioning + narrative staleness (#9/#10)
- Beat schedule disabled tasks classification (Rigby's A4)
- Revenue pipeline aggregation audit (Rigby's C5)

### SESSION 1216 CLOSED — OpenAI caller alignment Phase E complete + SPEC CLOSED: 2 PRs merged, runtime guard + AST-based CI lint, catalog final at 17.1KB

Full handoff: [`SESSION_1216_OPENAI_CALLER_ALIGNMENT_PHASE_E.md`](docs/handoffs/SESSION_1216_OPENAI_CALLER_ALIGNMENT_PHASE_E.md). **2 PRs merged.** Phase E closes the OpenAI caller alignment spec deliverable `2b9aa447-…` (status flipped to `completed`).

| PR | Commit | What |
|---|---|---|
| **#2499** | `899a8c7c` | Phase E PR #1 — runtime guard in `core/services/openai_client_factory.py`. New public API: `apply_reasoning_guard()` + `ReasoningGuardViolation` + `_install_reasoning_guard()`. Factory-returned clients have `chat.completions.create` wrapped at construction. Env-gated `OPENAI_REASONING_GUARD={warn,strip,error}`, default `warn`. Trigger: `"gpt-5"` substring in model. Forbidden: max_tokens / temperature / top_p / frequency_penalty / presence_penalty. 13 unit tests pass. |
| **#2500** | `9297864b` | Phase E PR #2 — AST-based `tools/check_reasoning_contract.py` + `.github/workflows/check-reasoning-contract.yml` + 10 unit tests. AST parsing avoids docstring false positives. Ships `--warn-only` since Phase C+D close left zero violations on main. **CLOSES spec deliverable 2b9aa447-….** |

**Three-session OpenAI alignment arc final ledger (1214 + 1215 + 1216, all 2026-06-23): 15 PRs merged (12 work + 3 docs closes). ~30 call sites aligned to gpt-5-mini reasoning contract. Async factory + runtime guard + CI lint shipped. Catalog deliverable bb775acb-… pinned at 17.1KB.**

### SESSION 1215 CLOSED — OpenAI caller alignment Phase C+D complete: 3 PRs merged, double round-trip bug fixed, 3 endpoints unbroken, catalog at 16.1KB

Full handoff: [`SESSION_1215_OPENAI_CALLER_ALIGNMENT_PHASE_CD.md`](docs/handoffs/SESSION_1215_OPENAI_CALLER_ALIGNMENT_PHASE_CD.md). **3 PRs merged.** Phase C+D active scope closed in single arc (same day as Session 1214 close — Chris pushed straight into Phase C from 1214 closeout).

| PR | Commit | What |
|---|---|---|
| **#2495** | `0ec005ca` | Phase C+D: `content/ai_providers.py` `OpenAIProvider.generate_content` — collapsed broken gpt-5-mini + gpt-5 branches into single check, gpt-5.x path passes only `max_completion_tokens`, removed exception-driven retry-with-different-params. **Eliminates 1 wasted API round-trip per gpt-5.x call** on the primary content path. -54/+23 LoC. |
| **#2496** | `143cf89d` | Phase C+D: `core/views_ai_learning_api.py` — 3 Django view handlers (baseline_knowledge, learning_insights, personalized_synthesis) fixed. All were silently 500ing on gpt-5-mini (OPENAI_CONFIG default) when SDK rejected `temperature=` + `max_tokens=`. |
| **#2497** | `526cc025` | Phase D: `agents/executors/base_executor.py` `BaseExecutor.call_openai_api` — conditional temperature strip. Already Phase C compliant (max_completion_tokens correct); now only forwards `temperature=` when model is non-gpt-5.x. Preserves sampling control for non-reasoning callers. |

**Major scoping correction this session:** raw `\bmax_tokens\s*=` grep returns 158 matches across 77 files, **but** `LLMRequest.max_tokens` in `core/services/llm_provider_registry.py:55` is correctly abstracted — `_call_responses_api:237` maps to `max_output_tokens` for gpt-5.x, `_call_chat_api:296` passes through for non-reasoning. Most of those 158 matches are NOT Phase C/D targets. After cross-referencing with direct `chat.completions.create(... max_tokens=...)` and excluding archive/tests/scripts, **6 active files** remained. Per-file audit found only **3 actually broken** — the other 3 were already correct (Sessions 56, 876 prior fixes) or conditional_ok_default (ragtest.py LLM_MODEL env).

**Catalog deliverable `bb775acb-…` ("OpenAI Call Site Catalog — Session 1214"):** Pinned, Platform Capability Audit category. Grew from 10.9KB → 16.1KB this session. Added: Phase C scope refinement note, 3 PR entries (#8/9/10), 1 provenance entry (#11) bundling the 3 already-aligned files + ragtest.py conditional case.

**Spec deliverable `2b9aa447-…` status:** Phase A+B+C+D complete. Phase E remains. Still `accepted` for Session 1216+.

### FIRST THING Session 1216 — Phase E: CI lint + runtime guard

**P1 lead:** Final phase of spec deliverable `2b9aa447-c0c9-4ff3-8483-f92257eb0fcb`. Phase A-D done; Phase E is opt-in CI infrastructure + runtime guard.

**Rigby's drafted AC (verbatim in `SESSION_1215_OPENAI_CALLER_ALIGNMENT_PHASE_CD.md` §"Phase E queued"):**

- **(a) Env var `OPENAI_REASONING_GUARD={warn,strip,error}`** — warn (default, log only), strip (remove forbidden kwargs + log), error (raise before SDK call). Empty/missing → warn.
- **(b) Forbidden params for reasoning models:** `max_tokens`, `temperature`, `top_p`, `frequency_penalty`, `presence_penalty`. Allowed: `max_completion_tokens`, `reasoning_effort`, `verbosity`, etc.
- **(c) Model gating:** model string contains substring `"gpt-5"`. o1/o3 explicitly out of Phase E scope.
- **(d) CI lint:** sibling to `tools/check_direct_llm_calls.py`. Exclusions: LLMRequest abstraction, non-OpenAI providers, tests/scripts/archive.
- **(e) Shipped when:** runtime guard centralized in `openai_client_factory.py` (or shared helper), warn/strip/error modes all behave correctly on synthetic violations, CI lint passes on main + fails on intentionally-introduced violations, no behavior change for non-gpt-5 models.

**Lean for kickoff:**
1. Implement runtime guard in `core/services/openai_client_factory.py` (or new sibling helper) — wrap `client.chat.completions.create` invocations with kwarg inspection.
2. Default `OPENAI_REASONING_GUARD=warn` — burn in 24h, review log volume.
3. Ship CI lint as separate PR — should pass cleanly on main given Phase A-D close.
4. Escalate to `strip` once warn-volume is 0.
5. Optional: `error` mode after a week of `strip` clean.

**Active conversation:** `pa-e37fe30dc7b941a6` continues. Phase E may benefit from a fresh thread to keep system-prompt context lean — call.

**Carryover follow-ups (defer to Session 1217+ unless quick win):**
- **`OpenAIProvider.generate()` brokenness** (Session 1214 finding, P2) — `agent_llm_integration.py:43-108` references undefined `messages` at L90. Unreachable in prod; delete vs fix.
- **`content/ai_providers.py:114` bare-with-kwargs `openai.OpenAI(...)`** — has explicit timeout (not 600s footgun) but doesn't use factory. Phase B follow-on.
- **`agent_llm_integration.py` `AsyncLLMAdapter.chat()` indirect dispatch path** (Session 1214 finding) — actual production LLM call surface; investigate Phase E enforcement coverage.
- **Stale-thread dispatcher** (`777d9cd8-…`, P2) — ~$3.60/day savings.
- **System prompt + tool schema size reduction** (P2) — non-smoke conversational turns still 35-68K tokens.

### SESSION 1214 CLOSED — OpenAI caller alignment Phase A+B complete: 22-of-21 sites cleared, async factory shipped, catalog deliverable live (8 PRs merged)

Full handoff: [`SESSION_1214_OPENAI_CALLER_ALIGNMENT_PHASES_A_B.md`](docs/handoffs/SESSION_1214_OPENAI_CALLER_ALIGNMENT_PHASES_A_B.md). **8 PRs merged.** Phase A archive + 6 Phase B callsite PRs + 1 async factory infra PR. Catalog deliverable `bb775acb-…` created in Donkey Betz workspace (category Platform Capability Audit, pinned, 10.9KB final).

| PR | Commit | What |
|---|---|---|
| **#2486** | `98297ab3` | Phase A: archived `ai_core/MAKE_MONEY_NOW_WITH_APIS.py` → `archive/old_experiments/` (pre-platform gpt-3.5-turbo demo, never live-imported). |
| **#2487** | `97aca26e` | Phase B: `intelligence/real_agents.py:21` `BaseAgent.__init__` factory swap. Propagates to 9 subclasses. |
| **#2488** | `cc5a18b4` | Phase B: `intelligence/agent_execution_pipeline.py` 3 sites (module cache + ContentCreator + dynamic RegistryAgent). |
| **#2489** | — | Phase B: `intelligence/agent_factory.py` 2 sites (fallback BaseAgent + UnifiedAgentFactory). |
| **#2490** | — | Phase B infra: `get_async_openai_client()` factory variant. Separate `_ASYNC_CLIENT_CACHE` + lock. Same contract (20/90/60/60s timeouts, 2 retries, forbidden kwargs, RuntimeError-on-no-key). |
| **#2491** | — | Phase B: removed 11 vestigial `AsyncOpenAI()` from `real_work_delivery_engine.py` — `client` never invoked; actual dispatch flows through `agent_llm_integration.generate_for_agent`. |
| **#2492** | — | Phase B: removed 4 vestigial `AsyncOpenAI()` from `ai_proposal_engine.py` (3) + `real_client_acquisition.py` (1) — same dead-code pattern. |
| **#2493** | — | Phase B closing: `agent_llm_integration.py:38` `OpenAIProvider.__init__` central swap to `get_async_openai_client(api_key=...)`. Dropped stale openai-v0.x `openai.api_key` module mutation. +1 expanded scope target. |

**Catalog deliverable `bb775acb-5805-4561-901f-497d2db2add9` ("OpenAI Call Site Catalog — Session 1214"):** pinned in Donkey Betz workspace, category Platform Capability Audit. Final 10,871 chars. Contains overview + methodology + verified counts + 5-phase plan + 7 per-callsite/PR entries logged on every PR close. Schema per Rigby: `file:line | model | client pattern | params | what it does | reasoning_contract: {ok | needs_max_completion_tokens | needs_temp_strip | needs_both | moot_removed | moot_archived | unknown | pre_existing_bug} | migration: <PR # + summary>`. Keep updated as Phase C/D/E land.

**Spec deliverable `2b9aa447-…` status:** Phase A+B complete. Phase C/D/E remain. Still `accepted` for Session 1215+.

**Pre-existing bug surfaced (NOT fixed Session 1214, Phase C/D follow-on):** `ai_core/agents/agent_llm_integration.py:43-108` — `OpenAIProvider.generate()` references undefined `messages` variable at L90 (would NameError if invoked) + accesses `.output_text`/`.id`/`.usage` on a string. Effectively unreachable in production (dispatch routes through `AsyncLLMAdapter` directly). Rigby's recommendation: delete (if truly unused) or fix + add a tiny unit smoke. Defer to Session 1215+.

### FIRST THING Session 1215 — Phase C: max_tokens → max_completion_tokens per-callsite audit

**P1 lead:** Continue Session 1214's spec deliverable `2b9aa447-c0c9-4ff3-8483-f92257eb0fcb`. Phase A+B done; Phase C is the next mechanical scope.

**Why this scope:** gpt-5.x reasoning models (gpt-5, gpt-5-mini, gpt-5-nano) reject `max_tokens=`; the contract is `max_completion_tokens=`. Raw grep of `\bmax_tokens\s*=` returns **158 matches across 77 files** (active + archive). After filtering archive/ + tests/ + function signatures, expected real Phase C target is ~30-50 actual call kwargs across ~15-20 files. Per-site review required — no bulk sed (function defs vs call kwargs vs config dicts).

**Phase C method (proposed):**
1. **Re-grep** to refresh authoritative count on main @ post-#2493 HEAD.
2. **Filter** to active call kwargs (exclude function signatures, exclude archive/, exclude tests/).
3. **Group** by file. Each file becomes its own PR (smaller blast radius, per Session 1214 Phase B pattern).
4. **Per-site review** — if model is gpt-5.x, migrate. If non-reasoning, leave or document.
5. **Catalog entry per PR** to `bb775acb-…` using the schema.

**Active conversation:** `pa-e37fe30dc7b941a6` — Session 1214 thread. Rigby has full Phase A+B context. Spin a fresh thread for Session 1215 if you want a clean slate; otherwise continue.

**Carryover follow-ups (defer to Session 1216+ unless quick win):**
- **Stale-thread dispatcher** (`777d9cd8-…`, P2) — ~$3.60/day savings, lean A (per-conversation `session_closed` flag).
- **Continue URC adoption to next 3 agents** (Session 1211 carryover, P1) — 4 of ~10 done. Pattern stable.
- **System prompt + tool schema size reduction** (P2) — non-smoke conversational turns still 35-68K tokens.
- **`OpenAIProvider.generate()` brokenness** (P2, Session 1214 finding) — delete vs fix-and-smoke.

### SESSION 1213 CLOSED — Smoke context minimization shipped, AC-4 verified live, 31× context shrink on the worst-case agent (1 PR merged)

Full handoff: [`SESSION_1213_SMOKE_CONTEXT_MINIMIZATION.md`](docs/handoffs/SESSION_1213_SMOKE_CONTEXT_MINIMIZATION.md). **1 PR merged.** Single-arc cost-reduction PR, closes Session 1212 spec deliverable `afe36715-…`.

| PR | Commit | What |
|---|---|---|
| **#2483** | `3670cede` | `core/services/smoke_dispatch.py` (+146 new) defines `SMOKE_CONTEXT_KEYS = {mode, smoke_id, receipt_only, user_id, conversation_id, workspace_id, auto_followup}` allowlist + `SMOKE_MODES = {receipt_only, fleet_smoke}` (outbound_pack intentionally NOT gated — CampaignOrchestratorAgent needs payload). Wrap at `tool_dispatcher.py:_handle_agent_tool:1196` right before `execute_agent_task.apply_async` (single PA-initiated agent dispatch choke point). `SMOKE_CONTEXT_BYTE_CAP = 200`B evaluated post-strip — soft cap in strip/warn (log-only), hard cap in error (raises `SmokeContextViolation`). Env var `SMOKE_CONTEXT_ENFORCEMENT_MODE ∈ {warn, strip, error}`, default strip. `smoke → smoke_id` alias rewrite. 18/18 unit tests green. Admin-merged through GitHub Actions billing block (same pattern as Session 1211 #2479). |

**Drift surfaced + resolved in-session:** spec named the seam as "Rigby's cockpit / execution_history dispatch path" — but `cockpit_tool` dispatches Celery tasks (not agents) and `execution_history_tool` is read-only. Real choke point is one location at `_handle_agent_tool:1196`. Pivoted there in coordination with Rigby; documented in handoff §"What shipped".

**Live AC-4 evidence (validation smoke `session-1213-live-validate-2483`):** 3 agents (CodeReview + Research + ContentWriter) dispatched receipt_only post-merge. All 3 AgentExecution rows show allowlist-only context @ 210B (vs Session 1209 baseline `a14d4c7c` ContentWriterAgent @ 6572B = **31× shrink** on the same agent class). celery-pa.log shows 3 INFO `[smoke_dispatch] stripped_keys=['research']` + 3 WARNING soft-cap-over events. The 10B over-cap is chris's UUID-shaped `user_id` (expected, not a regression — int user_id flows would be ~140B).

**Deliverables updated:**
- `afe36715-721c-400f-b36f-4b9717467b66` — status: `accepted → completed` via `content_tool.content_complete`
- `1a8cde69-8f40-45d2-b841-4e88f76c9d7f` — runbook appended (+2033 chars) with minimal-context contract (AC-3)

**Post-merge gotcha (cleared):** worker restart at 11:22-11:23 MDT (post-`3670cede`) — `smoke_dispatch.py` is imported by `tool_dispatcher.py` which is imported by celery task bodies. All 4 workers + beat alive on fresh PIDs (verified via `ps -eo lstart`).

### Also fires this session

**24h watches** — time-gated priorities. Four fire today (2026-06-24):

| Watch | Fires (MDT) | Fires (UTC) | Checklist |
|---|---|---|---|
| **Session 1209 (URC)** | ~07:10 MDT | ~13:10 UTC | [§"24h watch checklist" in 1209 handoff](docs/handoffs/SESSION_1209_URC_V01_ENVELOPE_AND_ROUTER_PATH.md) |
| **Session 1210 (Phase B)** | ~08:48 MDT | ~14:48 UTC | [§"24h watch checklist" in 1210 handoff](docs/handoffs/SESSION_1210_PHASE_B_RECEIPT_ONLY_CODEREVIEWAGENT.md). Invariants A1-A4. |
| **Session 1211 (Phase B extension)** | ~09:20 MDT | ~15:20 UTC | [§"24h watch checklist" in 1211 handoff](docs/handoffs/SESSION_1211_PHASE_B_EXTENSION_THREE_AGENTS.md). Invariants B1-B4. |
| **Session 1213 (smoke context min)** | ~10:30 MDT | ~16:30 UTC | [§"24h watch checklist" in 1213 handoff](docs/handoffs/SESSION_1213_SMOKE_CONTEXT_MINIMIZATION.md). Invariants A1-A4. |

Then pick from the priority table below.

### SESSION 1211 CLOSED — URC v0.1 Phase B extension to 3 more agents + media gate hotfix (2 PRs merged)

Full handoff: [`SESSION_1211_PHASE_B_EXTENSION_THREE_AGENTS.md`](docs/handoffs/SESSION_1211_PHASE_B_EXTENSION_THREE_AGENTS.md). **2 PRs merged.** Phase B now covers 4 agents total (CodeReviewAgent from Session 1210 + 3 new). AC-2 verified live on all 4 receipt_only rows; AC-3 verified via pattern proof + MeetingCoordinator control; AC-4 addendum extension filed (+2059 chars; deliverable `6f09233c-…` now 16800 chars).

| PR | Commit | What |
|---|---|---|
| **#2478** | `94376083` | Phase B adoption on VideoEditingAgent, ImageEditingAgent, MeetingCoordinatorAgent. Each gets `_is_receipt_only_mode(context)` helper + early-return branch before any side effect (LLM, spider intel, `time_travel_session`). One consolidated parametrized test file (`test_phase_b_receipt_only_adopters.py`, 33 tests, 11 per agent). |
| **#2479** | `c4d55b31` | **Hotfix.** Session 1036's `_is_media_task_blocked` gate at `tasks_agents.py:2079` rejected Video/Image receipt_only dispatches before Phase B could fire. 2-line context check bypasses the gate when receipt_only; helper stays pure. Admin-merged because GitHub Actions billing block prevented CI from running (NOT a code failure — diagnosis matched celery log fingerprint exactly). |

**AC-2 evidence (DB-verified, 4 rows):** VideoEditingAgent `e69da447` (skipped, 2452ms), ImageEditingAgent `7ce2c54b` (skipped, 1081ms), MeetingCoordinatorAgent `dcba5633` (skipped, 9914ms) + `74512a1c` (skipped, 1290ms). All sub-10s confirms early-return fires before any LLM/IO.

**AC-3 evidence:** MeetingCoordinatorAgent control `cb24ed13` → `run_status='success'` on empty context (normal path executed). Phase B is purely additive at the agent level; the contract is identical across all 3 adopters (proven by parametrized unit tests). Video/Image controls skipped — would just re-test the dispatcher gate bypass, which the receipt_only rows already proved.

**Drift finding closed in-session:** the media gate had a receipt_only blind spot (gate rationale = save spend; receipt_only short-circuits before spend). Hotfix #2479 surgically adds context-aware bypass. Gate-audit P2 follow-up filed for other pre-execute guards.

**Post-merge gotchas (cleared):** worker restarts at 10:08 MDT (post-#2478) AND 10:20 MDT (post-#2479) — both required because `tasks_agents.py` + the 3 new agent files are all celery-task-imported.

### SESSION 1210 CLOSED — URC v0.1 Phase B: receipt_only mode for CodeReviewAgent (1 PR merged)

Full handoff: [`SESSION_1210_PHASE_B_RECEIPT_ONLY_CODEREVIEWAGENT.md`](docs/handoffs/SESSION_1210_PHASE_B_RECEIPT_ONLY_CODEREVIEWAGENT.md). **1 PR merged.** AC-1, AC-2, AC-3, AC-4 all verified live via 2-dispatch validation smoke.

| PR | Commit | What |
|---|---|---|
| **#2476** | `4d0040af` | Phase B — `_is_receipt_only_mode(context)` static helper + early-return branch at top of `CodeReviewAgent.execute()` (before `time_travel_session` opens). Two recognized signals: `context['mode']=='receipt_only'` (primary) + `context['receipt_only'] is True` (forward-compat). Receipt shape: `data={skipped:True, status:'skipped', mode:'receipt_only', message:...}`. 14 unit tests (detector ×7, execute ×5, URC integration ×2). |

**Smoke evidence:** receipt_only run `d0281cc8-477b-4099-aa21-10ad5439abfc` → `run_status='skipped'`, `data.skipped=True`, no tool_calls, no warnings, URC envelope fully populated (latency_ms=3616). Control run `042a8c0e-3b08-4a42-aea4-d997bde72253` → `run_status='success'`, 303 lines of python reviewed (normal path untouched).

**AC-4 addendum:** Rigby filed +2601 chars on URC spec deliverable `6f09233c-…` capturing (a) Phase B definition (first agent-level integration; A+C are runner-level), (b) classification rule (`data['skipped'] is True` is the load-bearing Q1 marker), (c) schema nuance (`status='skipped'` is receipt-schema-valid but not sufficient on its own), (d) reference impl pointer `core/agents/code_review_agent.py:286-316`.

**Drift surfaced + resolved in-session:** Spec text in `00-START` line 127 implied `data={'status': 'skipped'}` alone would trigger `run_status='skipped'` — Q1 predicate at `urc_envelope.py:50` actually requires `data['skipped'] is True`. Option A reconciliation per Rigby (`pa-e37fe30dc7b941a6`): agent emits both keys; URC core unchanged.

**Post-merge gotcha (cleared):** worker restart required at 09:47 MDT (post-`4d0040af`) — `code_review_agent.py` is imported by `tasks_agents._impl_execute_agent_task` body. All 4 workers + beat alive on fresh PIDs.

### SESSION 1209 CLOSED — Universal Receipt Contract (URC v0.1) envelope + router-path coverage (2 PRs merged)

Full handoff: [`SESSION_1209_URC_V01_ENVELOPE_AND_ROUTER_PATH.md`](docs/handoffs/SESSION_1209_URC_V01_ENVELOPE_AND_ROUTER_PATH.md). **2 PRs merged.** Fleet smoke validated 52/52 URC envelope coverage post-fix (vs 0/21 router-path baseline).

| PR | Commit | What |
|---|---|---|
| **#2473** | `3d95aea9` | Phase A+C URC v0.1 inline at `tasks_agents.execute_agent_task` writeback. Every celery-task-dispatched agent emits the 8-key envelope. ContentWriterAgent under `mode=receipt_only` flips to `contract_violation`. 39 unit tests. Includes context-kit headline strong-token fix in 00-START line 122 (re-triggered by Session 1208's close commit `8295ccca`). |
| **#2474** | `7669a249` | Extracted URC helpers to `core/services/urc_envelope.py` (single source of truth). Refactored `tasks_agents.py` to use shared module. Added `enrich_output_data()` call to `agent_router._complete_execution` + raw context propagation to `input_data['context']`. 20 additional unit tests (59 total). Closes router-path coverage gap. |

**Spec deliverable:** `6f09233c-c984-4303-87c4-e67b94390030` on Initiative `29154d73-…` (Platform Capability Audit). Q1-Q5 design locks captured verbatim in §6.

**Smoke evidence deliverable:** `1a8cde69-8f40-45d2-b841-4e88f76c9d7f` (Rigby; DBZ; Platform Diagnostics; pinned). Post-router-patch fleet smoke results — 52/52 URC envelope coverage, 39 success / 12 error / 1 contract_violation, all expected.

**Post-merge gotcha (cleared):** worker restart required for both PRs (tasks_agents.py + agent_router.py both imported by celery task body). Done in-session at 00:09 MDT post-#2474.

### SESSION 1208 CLOSED — CampaignOrchestrator outbound-pack hardening ($2k Automation Sprint) (1 PR merged)

Full handoff: [`SESSION_1208_CAMPAIGN_ORCHESTRATOR_OUTBOUND_PACK_HARDENING.md`](docs/handoffs/SESSION_1208_CAMPAIGN_ORCHESTRATOR_OUTBOUND_PACK_HARDENING.md). **1 PR merged (#2471, 2 commits).** All 5 acceptance criteria verified across 2 live smokes before merge.

Single-arc session executing Rigby's full §1-§6 spec from deliverable `ecddb62d-…`. `CampaignOrchestratorAgent.execute()` now short-circuits into a hardened path when `context['mode']=='outbound_pack'` OR a narrow keyword trigger matches (`"outbound pack"` OR (`"$2k"` AND `"automation sprint"` AND outbound-ish token from cold/dm/email/outreach)). Hardened path: generate JSON → validate (§4) → retry up to 2× → render markdown → save ONE Deliverable. Legacy 5-phase pipeline (research/strategy/creation) untouched.

| Commit | What |
|---|---|
| **`3b877a4d`** | Initial implementation (854 lines). New private methods: `_is_outbound_pack_request`, `_execute_outbound_pack`, `_run_outbound_hooks`, `_call_openai_json` (JSON-mode helper using `response_format={'type':'json_object'}` on gpt-5-mini), `_build_outbound_prompt` (3-attempt schedule: normal → +errors → +inline JSON skeleton), `_outbound_pack_skeleton`, `_validate_outbound_pack` (§4 hard rules + soft length warnings + §4.2 no-drift scan), `_collect_outbound_message_strings` (drift scan scoped to message content only — not metadata), `_render_outbound_pack_markdown` (§5 body shape). Short-circuit in `execute()` outside legacy `time_travel_session`. |
| **`1ff25732`** | Rigby's PR-review gate fixes: title locked deterministically via `_format_outbound_pack_title()` constant (LLM's `offer.name` no longer bleeds into title/H1); validator tightened to exact-match `offer.name == OUTBOUND_PACK_OFFER_NAME` (LLM smoke had returned compound `"Automation Sprint — $2k Automation Sprint"`); `attempts_used` lifted to top-level `output_data` (same convention as PR #2469's `deliverable_id`/`warnings` — emitted only when set, kept at `data.attempts_used` for backcompat); `.gitignore` for `.obsidian/`. |

**Smoke evidence:** Deliverable `a37a0c52-3c58-4e05-9f8e-7d410ae45464` (post-fix re-smoke) — title exactly `CampaignOrchestratorAgent: Outbound Pack — $2k Automation Sprint — 2026-06-22` (the agent-prefix is factory-level, affects all agents — documented as cosmetic follow-up). Body H1 `# Outbound Pack — $2k Automation Sprint — 2026-06-22`. `output_data['attempts_used']=2` lifted to top-level. Plus deliverable `6907bc78-…` (initial smoke, kept as audit baseline).

### SESSION 1207 CLOSED — MIC auto-deliverable + output_data hardening (3 PRs merged)

Full handoff: [`SESSION_1207_MIC_AUTO_DELIVERABLE_AND_OUTPUT_DATA_HARDENING.md`](docs/handoffs/SESSION_1207_MIC_AUTO_DELIVERABLE_AND_OUTPUT_DATA_HARDENING.md). **3 PRs merged.** Wakeup-Week-driven session: Rigby surfaced that MIC ran successfully but produced no Deliverable; the brief was stranded in `AgentExecution.output_data`. Closed that gap.

| PR | What |
|---|---|
| **#2467** | MIC auto-creates exactly 1 Deliverable per successful brief gen. Spec: workspace=DBZ, category=`Market Intelligence`, title=`Market Intel Brief — YYYY-MM-DD`, sensitivity=`internal`, body=provenance markdown + executive summary + structured sections. Includes hook isolation (`_record_learning_outcome` + `_create_execution_memory` in both success and failure branches wrapped in try/except so post-result-construction failures can't flip `result.success`). |
| **#2468** | `pa_local.sh` thread pin update — from Rigby's auto-spawned `pa-b2a99ff5b0ee47a6` to Chris's preferred `pa-33088358df304016`. Pure dev ergonomics. |
| **#2469** | Lifts `deliverable_id` + `warnings` from `result.data` to top-level `output_data` in `tasks_agents.execute_agent_task` writeback. Establishes structured warnings convention: `{type: <stable_key>, message: <str>}`. Stable keys: `deliverable_persist_failed`, `deliverable_gated`. Other agents can adopt the same shape. |

**Smoke evidence:** First-ever MIC auto-deliverable `758be167-f9c9-4e03-822d-516a7449f675` landed in DBZ (kept as audit baseline).

### FIRST THING Session 1208

**CampaignOrchestrator delegation hardening** — outbound pack generation for the **$2k Automation Sprint** offer, hardened with JSON schema validation + retry + single combined Deliverable.

Full spec is preserved as deliverable **`ecddb62d-ab01-4b3b-83c4-2601670395d3`** ("Rigby: CampaignOrchestrator delegation hardening — outbound pack spec") on Initiative `29154d73-…`. Read it FIRST — Rigby spec'd §1 (scope), §2 (AC-1 through AC-5), §3 (outbound pack JSON schema with `offer` + `segments[]` + `global` blocks), §4 (validation rules + retry semantics: 2 retries with corrective instructions), §5 (deliverable body shape), §6 (additional notes). ~10KB body.

Acceptance criteria summary (full versions in the deliverable):
- **AC-1:** ONE combined Deliverable per successful run (workspace=DBZ, category=`Outbound`, sensitivity=`internal`, title=`Outbound Pack — $2k Automation Sprint — YYYY-MM-DD`).
- **AC-2:** Strict JSON schema enforced — no drift into blogs/thumbnails.
- **AC-3:** Validation + retry semantics — 2 retries with corrective prompts; mark failure (no deliverable) after 3 total attempts fail.
- **AC-4:** Provenance block in body + no regression on `output_data.message` / `result_preview`.
- **AC-5:** Short + long variants for every message type (opener + follow-ups + objections + breakup).

Two segments: `smb_founder` + `agency_owner`. Each segment carries `initial_outreach`, `follow_up_1`, `follow_up_2`, `breakup`, `objection_handling[]`, `cta`.

**Approach hint** (not in deliverable, learned from Session 1207 MIC pattern):
- Wrap the structured-output LLM call in a validate-then-retry loop in the agent's `execute()`.
- Use `_save_to_deliverable` (gets PR #2465 guardrail + PR #2464 BLOCKED + dedup for free).
- Set `result.data['deliverable_id']` + `result.data['warnings']` per the convention in PR #2469.
- Hook isolation pattern from PR #2467 — wrap learning hooks in try/except so they can't flip `result.success`.

### SESSION 1206 CLOSED — Layer 1 telemetry + Wakeup Week cascade (5 PRs merged)

Full handoff: [`SESSION_1206_LAYER1_TELEMETRY_BASEAGENT_RUN.md`](docs/handoffs/SESSION_1206_LAYER1_TELEMETRY_BASEAGENT_RUN.md). **5 PRs merged.** All live-verified before merge.

| PR | Arc | What |
|---|---|---|
| **#2461** | Telemetry | `BaseAgent.run()` concrete wrapper + 7 bypass-callsite migrations. Closes finding `65f1299f-…`. |
| **#2462** | TheOdds | Loud-failure pattern — emit `fetch_failure` row when API auth dies, no more lying `api_status` rows with fake `sports_fetched: 48`. Closes finding `2de3d8d6-…` (root cause: billing-lapsed key, code now signals honest outage). |
| **#2463** | Finding B1 | `tasks_agents.execute_agent_task` writes BOTH canonical `{message, result_preview, data, error, tool_calls}` AND legacy `{content, metadata}` shapes — Rigby's `execution_history_tool` now reads non-empty preview for text-output agents. |
| **#2464** | Finding B3 | BLOCKED detector tightened to structural markers only (`**BLOCKED ON:**`, `[BLOCKED]`, line-anchored). Stops false-positive rejection of prose mentioning BLOCKED as an enum value. Case-sensitive. |
| **#2465** | Finding B2 | Workspace_id validation guardrail at `create_deliverable` entry. Hallucinated UUID → WARN with structured audit fields + fallback to user.active_workspace. Stops FK-violation artifact loss. Root cause filed as P0 `96b6a72a-…`. |

**Mid-session pivot from sketch:** PR #2461 (the planned work) unblocked Rigby's Wakeup Week, which immediately surfaced 4 downstream bugs the telemetry made visible. Arc B (TheOdds) and Arc C (Findings B1/B2/B3) were all dispatched, scoped with Rigby, shipped, and merged in the same session — without the Layer 1 fix they would have stayed invisible.

**Post-merge gotcha:** workers MUST restart after each merge of celery-task-imported code (`tasks_agents.py`, `tasks_financial.py`, `deliverable_factory.py`). All 5 PRs touched such code; workers restarted last at 20:43 MDT post all-5-merged. Daphne untouched.

### FIRST THING Session 1207

Pick from the prioritized table below. The natural Session 1206 extensions:

1. **CI lint rule (`180f4e9f-…`)** — block `\.execute\(` outside `core/agents/`. Allowlist: `core/agents/`, tests, `core/agent_execution_wrapper.py`, `ai_core/agents/sync_executor.py`. Implementation candidates: pre-commit hook / ruff custom rule / `scripts/verify_repo_guardrails.py` extension / dedicated `manage.py` command in CI. Small PR.
2. **Verify Layer 1 dashboard `7d221aa4-…` flips** — after PR #2461 lands AND workers restart AND the next `_impl_market_intelligence_scan` beat fires (every 2h), sports agents should transition UNTESTED → CONFIRMED WORKING. Re-run the dashboard refresh and confirm.
3. **Phase B.1 24h watch fires ~14:48 UTC** — checklist in `SESSION_1203_PHASE_B1_PRODUCER_REROUTE_CLOSE.md` §"24h watch checklist". Invariant: zero new deliverables with `workspace_id=1f0d467e-…` (SAW) created after 2026-06-22 19:48 UTC.
4. **Session 1206 24h watch fires ~23:35 UTC** — checklist in `SESSION_1206_LAYER1_TELEMETRY_BASEAGENT_RUN.md` §"24h watch checklist". Invariant: 3 sports agents land rows per beat cycle, no duplicate writes, no telemetry-write WARN spam.
5. **Daily inference accuracy + `default_only_projects` watches** — Day-3 protocol per runbook `cb9d8ae1-…`.

### SESSION 1204 CLOSED — Phase B.2 close (drift gate + Stage 1 prompt fixed; 20 stale docs unblocked; 4 briefs regenerated) (2026-06-22)

Full handoff: [`SESSION_1204_PHASE_B2_DRIFT_QUALITY_FIX_CLOSE.md`](docs/handoffs/SESSION_1204_PHASE_B2_DRIFT_QUALITY_FIX_CLOSE.md). **2 PRs merged** (#2453 drift threshold + #2454 Stage 1 prompt). **20 stale Stage-1 docs auto-unblocked** (BLOCKED → DRAFT with audit notes). **4 spine/MLB Stage 1 briefs regenerated to 100% quality score.**

The roadmap's framing ("SEC/Kaggle evidence packs") was wrong at the surface but right at a deeper layer. Recon revealed three nested gates:
1. **Drift threshold mis-calibration** (FIXED via PR #2453) — 29 of 33 Stage-1 rows BLOCKED on structural format mismatch
2. **Stage 1 prompt forced "BLOCKED:" + external-only research** (FIXED via PR #2454) — internal-architecture topics had no honest path; replaced with "Unknowns / Verification Plan" section
3. **Action-item completion gate** (Session 1205 follow-up) — Stage 1's action items block Stage 2 progression; design tension since Stage 1 items are typically deferred-to-later-stages

**Plus a 4th finding**: evidence cards delivered to ResearchAgent are mostly empty / off-topic (MLB brief revealed [E1]-[E10] all "(no content)"). The roadmap's original intuition was correct at this deeper layer — filed as Session 1205 follow-up.

### SESSION 1203 CLOSED — Phase B.1 close (Producer Reroute Completion, 3 PRs landed + 1 deferred) (2026-06-22)

Full handoff: [`SESSION_1203_PHASE_B1_PRODUCER_REROUTE_CLOSE.md`](docs/handoffs/SESSION_1203_PHASE_B1_PRODUCER_REROUTE_CLOSE.md). **3 PRs merged.** Producer Reroute leak fully closed at code level + verified live in production — test Initiative `a0e23887-…` spawned auto-research deliverable `0fbddd89-…` at 19:50 UTC which landed in DBZ (`b4503364-…`), not SAW (`1f0d467e-…`). PR-2 deferred with documented rationale (file-sink helper, not producer-routing path).

| Initiative | UUID | Status |
|---|---|---|
| **Producer Reroute Completion** | `05931145-89d2-4923-946e-676e0db44e91` | **COMPLETED** (Session 1203) |
| **Initiative-Management Tool Surface Gaps** | `f4cfe31e-366b-4d5e-802c-041ba66c7afb` | **COMPLETED** (housekeeping) |
| **Diagnostic Telemetry Tool Surface Gaps** | `50b7adf2-ec1c-4ef0-8245-ec026cff114f` | **COMPLETED** (housekeeping) |
| **Platform Connectivity Reality Map** (parent) | `0ecd1bc2-9931-4464-8efa-495a28b58779` | ACTIVE — 3 of 4 children closed; Docs↔Runtime + Phase B.2 still open |
| Docs ↔ Runtime Alignment Layer | `1859dd51-ce3b-4689-bd4b-42d9de5793d8` | ACTIVE — Phase C |

**Net result:** Phase B.1 done. Every autonomous-traffic dispatch now routes to DBZ (`b4503364-…`) instead of SAW (`1f0d467e-…`). SAW is `is_active=False`. PR-1 (#2449) + PR-1b (#2450) + PR-3 (#2451) merged. PR-2 deferred as separate "generated_content sink / root_path contract" scope.

### Phase B.1 24h watch — fires 2026-06-23 ~14:48 UTC

Full checklist in handoff §"24h watch checklist". Headline invariant: **zero new deliverables with `workspace_id=1f0d467e-…` (SAW) created after 2026-06-22 19:48 UTC**.

```bash
# Quick check
tools/pa_local.sh "Run deliverable_tool action=list limit=100 — count items with workspace_id=1f0d467e-d950-46db-8c6e-a4098024aacd and created_at after 2026-06-22T19:48:00Z. Target: 0."

# SAW state
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_skin_layer import ProjectWorkspace
saw = ProjectWorkspace.objects.get(id='1f0d467e-d950-46db-8c6e-a4098024aacd')
print('SAW is_active:', saw.is_active, '— expected False')
"
```

### Session 1204 FIRST THING (historical — superseded by Session 1206 above)

**Revenue-surface recon** + **Phase B.1 24h watch** + **Daily inference accuracy watch Day-2**. Note: revenue-recon was paused in Session 1205 by operator directive ("we are not going to be working in production until we figure out how to get everything connected") in favor of the tiered audit + producer chain resurrection.

```bash
# A — total create_deliverable calls (denominator)
grep '\[DELIVERABLE-FACTORY-ENTRY\]' celery*.log | wc -l

# B — eligible-for-inference subset (initiative_id=None at factory entry)
grep '\[DELIVERABLE-FACTORY-ENTRY\]' celery*.log | grep 'initiative_id_present=False' | wc -l

# C — actual inference matches
grep '\[INFERENCE-MATCH\] agent=' celery*.log | wc -l

# D — post-cascade failures (orphan diagnostic)
grep '\[ORPHAN-DELIVERABLE\] code=missing_initiative_id' celery*.log | wc -l

# C/B = accuracy signal (target ≥80% precision per seed)
# Step breakdown
grep '\[INFERENCE-MATCH\] agent=' celery*.log | grep -oE 'step=[0-9]+' | sort | uniq -c

# Spot-check 5-10 events
grep '\[INFERENCE-MATCH\] agent=' celery*.log | tail -10

# default_only_projects detector
USE_PGBOUNCER=1 .venv/bin/python manage.py report_initiative_kinds
```

Full daily protocol: runbook deliverable `cb9d8ae1-008e-42e8-b222-3f598e6b665e`. Day 8 (2026-06-30) decision lands as follow-up deliverable tagged `session-1198-watch-result`.

Day-1 (Session 1203) baseline established: zero traffic (~23 min coverage only post-restart); `default_only_projects=39`.

### Time-gated watches active 2026-06-23

| Watch | Cadence | Target |
|---|---|---|
| **Inference accuracy** (Sessions 1198/1199) | Daily 5-10 spot-checks | ≥80% precision per seed |
| **`default_only_projects` detector** (Session 1197) | Daily `report_initiative_kinds` | New project Initiatives don't accumulate without explicit classification |

### Time-gated watches firing 2026-06-29

| Watch | Trigger |
|---|---|
| **Plan C 7-day watch + Phase 2 hard-reject flip** | Re-run `backfill_deliverable_initiative_links`; flip to `OrphanDeliverableError` if clean. §6.2 Step 2+3 now sit in front of reject point — flip is safer than pre-Session-1199. |
| **Session 1196 7-day watch** | Re-run `backfill_initiative_workspace_links`; diff against 2026-06-22 baseline. |

### Active conversation

`pa-e37fe30dc7b941a6` — Rigby's `session_tool create_fresh` at Session 1209 open. Carries URC v0.1 design Q1-Q5 lock + Session 1209 fleet smoke `1a8cde69-…` + Phase B AC-4 addendum spanning 4 adopters (Sessions 1210-1211) + Session 1212 PA spend audit findings. Pinned in `tools/pa_local.sh`. **Lean for Session 1213: continue on this thread if pickup is one of the two filed follow-ups (smoke context minimization OR stale-thread audit); spin fresh if pivoting away from URC/cost work.** Prior threads retired: `pa-2d74e36cc3a04787` (Session 1208 + URC design — design-anchor record), `pa-33088358df304016` (Session 1207 MIC + spec handoff), `pa-b2a99ff5b0ee47a6` (Rigby's auto-spawned Session 1207 — superseded mid-session), `pa-234a75abfe374695` (Session 1206 Layer 1 Telemetry), `pa-76aa5b61d0764d11` (Session 1205 evidence-card pipeline), `pa-1871b37227054254` (Session 1204 Phase B.2), `pa-d2d0f4c2b6284899` (Session 1203 Phase B.1), `pa-123b7d48f01043eb` (Session 1202 Phase A.2). **The stale-thread audit deliverable `777d9cd8-…` proposes these retired threads stop accepting autonomous dispatches** — implementation in Session 1213 will close that leak.

**Donkey Betz workspace_id (pin):** `b4503364-2573-4401-9e28-61a739e0ce50` — **50 Initiatives total** (Session 1204 was 50; net +1 from Session 1205's `29154d73-…` Platform Capability Audit Initiative). **31 Initiatives still have NULL `target_workspace_id`** — backfill remains scheduled in roadmap §Phase B.3.

### Session 1205 Capability Audit Initiative

`29154d73-06a5-4630-abb4-3412cbdca5c5` — Platform Capability Audit (Tiered Pass: Agents / Tools / Spiders / Learning). Child of Reality Map `0ecd1bc2-…`, workspace=DBZ, kind=investigation. **15 deliverables** (10 end-of-Session-1205; +1 Session 1206 lint-rule `180f4e9f-…`; +1 Session 1206 Arc C `96b6a72a-…` workspace_id hallucination P0; +1 Session 1207 close `ecddb62d-…` CampaignOrchestrator hardening spec — implemented in full by Session 1208 PR #2471; +1 Session 1209 URC v0.1 spec `6f09233c-…` — implemented in full by Session 1209 PR #2473 + #2474; +1 Session 1209 fleet smoke evidence `1a8cde69-…`):

| ID | Type | Title |
|---|---|---|
| `7d221aa4-…` | Dashboard | Layer 1 — Agent Capability Map (83 agents) |
| `bb1e0a98-…` | Dashboard | Layer 2 — PA Tools + Dispatcher Handlers (109 schemas + 174 handlers) |
| `6a200985-…` | Dashboard | Layer 3 — Spider Network (80 spiders) |
| `dc970d99-…` | Dashboard | Layer 4 — Learning Bridges (8 bridges) |
| `6869fa55-…` | Deep-dive | Sports Betting Agents — wired but unscheduled (RESOLVED PR #2457) |
| `65f1299f-…` | Finding | Telemetry blind spot — direct-constructor agent paths bypass AgentExecution (**RESOLVED PR #2461**) |
| `180f4e9f-…` | **Follow-up** | **Lint rule: block `\.execute\(` outside `core/agents/`** (Session 1207 P1) |
| `2de3d8d6-…` | Finding | theodds spider returns 0 events |
| `ed6a8f28-…` | Finding | SportsOddsAnalyst caller bug — None context |
| `ea561389-…` | Finding | First Producer→Data Win (Kalshi) + memory spike warning |
| `a4928480-…` | Finding | Makefile bug: make celery silently skips beat startup (RESOLVED PR #2459) |
| `ecddb62d-…` | Spec | CampaignOrchestrator outbound-pack hardening spec (RESOLVED Session 1208 PR #2471) |
| `6f09233c-…` | Spec | URC v0.1 §1-§6 spec (RESOLVED Session 1209 PR #2473 + PR #2474) |
| `1a8cde69-…` | Diagnostic | Fleet Smoke Report — URC v0.1 Post-Router-Patch (Session 1209) — 52/52 envelope coverage |

**3 spine Initiatives — still BLOCKED at Stage 1 (irrelevant SEC/Kaggle evidence packs):**

| # | Name | UUID |
|---|---|---|
| 1 | Initiatives-First Wiring + No-Orphan Output | `6941372d-b13c-4631-91c8-749fa65c55a0` |
| 2 | Agent Capability Map + Router Contracts | `2071a9c6-986f-4528-be90-8cccaa595f1e` |
| 3 | Tool Migration Hardening (web_search → intelligence_tool) + Failure Fix | `7e23d621-4d0c-409a-a680-4fd2e015d04b` |

Spine progression unblocked by roadmap §Phase B.2 (auto-research evidence supplier fix).

### Pick this session

| Item | Priority | Where it's defined |
|---|---|---|
| ~~**Smoke context minimization spec impl**~~ | ✅ **Closed Session 1213** | PR #2483 (`3670cede`) — `core/services/smoke_dispatch.py`. Deliverable `afe36715-…` status=completed. AC-4 verified live: 6572B → 210B = **31× shrink** on the ContentWriterAgent worst-case class. Handoff: [`SESSION_1213_SMOKE_CONTEXT_MINIMIZATION.md`](docs/handoffs/SESSION_1213_SMOKE_CONTEXT_MINIMIZATION.md). |
| **System prompt + tool schema size reduction** | **P2 (NEW Session 1213 finding)** | Smoke-context fix shaved smoke-turn cost; non-smoke conversational turns are still 35-68K tokens because the system prompt carries 109 tool schemas + full conversation history. Far larger savings potential. Scoped follow-up: spec which schemas can be lazy-loaded based on user intent. No deliverable filed yet — would need a P2 deliverable + spec round before code. |
| **`outbound_pack` size cap (not allowlist)** | **P3 (NEW Session 1213)** | If outbound_pack ever spikes spend, add a size cap (e.g., 50KB max) rather than an allowlist, since CampaignOrchestrator legitimately needs payload. |
| **Stale-thread dispatcher audit + fix** | **P2 (Session 1212 NEW)** | Deliverable `777d9cd8-5526-4acf-a167-374c05e6e425`. `conversation_action_dispatcher` fires 24 of 41 24h follow-ups on retired threads (~$3.60/day burned). Three fix options listed; lean A (per-conversation `session_closed` flag on `ChatConversation`). ACs: AC-1 dispatcher skips 4 currently-retired threads, AC-2 active thread unaffected, AC-3 24h watch shows zero on retired set. |
| **Continue Phase B adoption to next 3 context-dependent agents** | **P1 (Session 1211 carryover)** | 4 of ~10 candidates now adopted (CodeReview + Video + Image + MeetingCoordinator). Pattern is fixed (`_is_receipt_only_mode` static helper + early-return + dual-key receipt). Next picks pulled from Session 1209 fleet smoke `1a8cde69-…` "error" rows. ACs mirror Phase B. ~90 min for a bundle of 3. |
| **Gate-audit P2 follow-up: receipt_only blind spots in pre-execute guards** | **P2 (Session 1211 Rigby surfaced)** | Hotfix #2479 fixed the media gate. Audit other pre-execute guards in `_impl_execute_agent_task` (`tasks_agents.py:2061+`): `_circuit_breaker_check` (line 2093), `_BLOCKED_AGENTS` (line 2065), any task-shape gates, allowlists/denylists. Decide per-guard whether receipt_only should bypass. Scope guideline: "ensure receipt_only can always reach agent `execute()` unless agent is explicitly disabled." |
| **Session 1211 Phase B extension 24h watch (arms ~09:20 MDT / ~15:20 UTC 2026-06-24)** | **P1 (time-gated)** | Checklist in [`SESSION_1211`](docs/handoffs/SESSION_1211_PHASE_B_EXTENSION_THREE_AGENTS.md) §"24h watch checklist". Invariants B1-B4: receipt_only → skipped on all 4 adopters; zero false-positive skipped from non-receipt callers; normal-mode reaches existing flow; media gate still fires on non-receipt non-generative tasks (bypass is narrow). |
| **Session 1210 Phase B 24h watch (arms ~08:48 MDT / ~14:48 UTC 2026-06-24)** | **P1 (time-gated)** | Checklist in [`SESSION_1210`](docs/handoffs/SESSION_1210_PHASE_B_RECEIPT_ONLY_CODEREVIEWAGENT.md) §"24h watch checklist". Invariants A1-A4: receipt_only → skipped; zero false-positive skipped from non-receipt callers; normal-mode rows produce `data.results`+`tool_calls`; `warnings=[]` on receipt_only rows. |
| **GitHub Actions billing block resolution** | **P1 (operational, Chris-owned)** | Hotfix #2479 was admin-merged because CI runs were rejected with "recent account payments have failed or your spending limit needs to be increased." Future PRs need this resolved at the GitHub billing layer to avoid admin-bypass dependency. |
| **Session 1209 URC 24h watch (fires ~07:10 MDT / ~13:10 UTC 2026-06-24)** | **P1 (time-gated)** | Checklist in [`SESSION_1209`](docs/handoffs/SESSION_1209_URC_V01_ENVELOPE_AND_ROUTER_PATH.md) §"24h watch checklist". Invariants: URC envelope coverage 100% on new rows; run_status distribution sane; **zero spurious contract_violations on non-receipt_only callers** (the key new-feature invariant); warnings list shape consistent. |
| **Standardize "skipped" semantics across agents (Session 1210 Rigby add)** | **P2 (defer)** | Decide whether future receipt_only agents must emit BOTH `data.skipped=True` AND `data.status='skipped'` (current Phase B pattern), or whether URC should expand its Q1 predicate to accept `data.status == 'skipped'`. Current pattern is safe; defer until ≥3 agents have adopted to see whether the dual-key requirement is friction. |
| **Other writeback callsites adopt URC** | **P2 (Session 1209 follow-up)** | ~10 sites: `core/agent_execution_wrapper.py:93`, `ai_core/agents/sync_executor.py:109`, `core/services/content_executor.py:255`, `core/services/executor_registry.py:394`, `core/services/agent_collaboration.py:339`, `core/team_workflow_engine.py:494,517`, `core/services/collective_intelligence.py:1425`, `core/tasks_media.py:192`, `core/tasks_agents.py:706,2278`. The two paths patched (execute_agent_task + agent_router._complete_execution) cover Rigby's fleet smoke surfaces; the rest are narrower use cases. Use `core.services.urc_envelope.enrich_output_data()`. |
| **Expose `parent_execution_id` filter in `ops_tool execution_search`** | **P2 (Session 1209 follow-up — Rigby surfaced)** | Rigby's fleet-smoke aggregation hit a tool gap — couldn't query "all AgentExecutions spawned by parent X". Session 1098 PR #4 added `parent_execution_id` + `root_execution_id` model fields; just need to surface them in the tool. ~30min PR. |
| ~~**Smoke context minimization convention**~~ | ✅ **Closed Session 1213** (was P3 Session 1209 idea, upgraded to P2 spec in Session 1212, shipped Session 1213). See above. |
| **Promote `attempts_used` to canonical top-level on router-path writeback** | **P1 (Session 1208 carryover)** | PR #2469 + PR #2471 lifted it for `execute_agent_task`. The router-path canonical-shape writeback at `agent_router.py:1611` doesn't lift it. Small mirror — same convention. |
| **Session 1207 MIC 24h watch (already fired ~03:50 UTC)** | **P1 (time-gated, verify result)** | Checklist in [`SESSION_1207`](docs/handoffs/SESSION_1207_MIC_AUTO_DELIVERABLE_AND_OUTPUT_DATA_HARDENING.md) §"24h watch checklist". Invariants: every successful MIC run lands a Deliverable (ratio = 1.0), no per-execution duplicates, `output_data.warnings` always list shape. |
| **Session 1208 Outbound-pack 24h watch (fires ~22:45 MDT / ~04:45 UTC 2026-06-24)** | **P1 (time-gated)** | Checklist in [`SESSION_1208`](docs/handoffs/SESSION_1208_CAMPAIGN_ORCHESTRATOR_OUTBOUND_PACK_HARDENING.md) §"24h watch checklist". Invariants: every successful outbound run lands ONE Deliverable, no double-writes, `warnings` shape consistent, drift-keyword false-positive rate stays at 0 on metadata-only mentions. |
| **Title normalization at factory level** | **P1 (Session 1208 cosmetic follow-up)** | Both MIC + Outbound deliverables show `<AgentName>: ` auto-prefix from `deliverable_factory._clean_deliverable_title`. Worth one cross-agent factory PR (e.g. a `preserve_title=True` kwarg on `_save_to_deliverable` → `create_deliverable` that skips the cleaner) rather than per-agent workarounds. Rigby's stamp: "If we ever want to remove it globally, that's a separate platform-wide title policy decision." |
| **Beat schedule for periodic outbound-pack generation** | **P2 (Session 1208 follow-up)** | Spec says "2 flagship outbound packs per week". Currently the path is only invocable on-demand (context['mode']='outbound_pack' or keyword trigger). Worth adding `PeriodicTask` via `add_critical_celery_tasks` if the cadence becomes desired. |
| **Workspace_id hallucination root-cause trace** | **P0 (Session 1206 Arc C unfinished)** | Deliverable `96b6a72a-…`. Mitigated by PR #2465 guardrail; root cause open. Suspected call chain: PA tool → tool_dispatcher → tasks_agents → agent_router → create_deliverable. Grep `pa_tool_schemas` + `tool_dispatcher` for `workspace_id` parameters where LLM might pick the value. Verification metric: B2 guardrail WARN volume should drop to zero in 24h post-fix. |
| **CI lint rule: block `\.execute\(` outside `core/agents/`** | **P1 (Session 1206 follow-up)** | Deliverable `180f4e9f-…`. Allowlist: `core/agents/`, tests, `core/agent_execution_wrapper.py`, `ai_core/agents/sync_executor.py`. Prevents future direct-constructor bypasses of `BaseAgent.run()`. |
| **Layer 1 dashboard refresh** | **P1 (post Session 1206)** | After workers restart + next `_impl_market_intelligence_scan` beat (every 2h), refresh `7d221aa4-…` to flip sports agents from UNTESTED → CONFIRMED WORKING. Layer 2/4 dashboards also need refresh — Wakeup Week dispatches have now generated real evidence including the first MIC deliverable. |
| **Wakeup Week scoreboard update** | **P1 (immediate — Rigby ongoing)** | Rigby's tracking dispatches across sessions. Session 1207 added: MIC produces real deliverables (smoke evidence `758be167-…`). |
| **Session 1206 24h watch (fires 2026-06-23 ~23:35 UTC)** | **P1 (time-gated)** | Run checklist in `SESSION_1206_LAYER1_TELEMETRY_BASEAGENT_RUN.md` §"24h watch checklist". Invariants: 3 sports agents land rows per beat, no double-writes, no telemetry WARN spam. Add: B2 guardrail WARN count (should be present if hallucinations continue; zero after root-cause fix). |
| **TheOdds API key renewal** | **P2 (Chris-owned, billing-gated)** | Renew at the-odds-api.com, update `.env` `THE_ODDS_API_KEY`, restart workers. Spider's loud-failure pattern (PR #2462) makes the outage honest in the meantime. |
| **Warnings convention adoption across other agents** | **P3 (Session 1207 follow-up)** | PR #2469 established `result.data['warnings'] = [{type, message}, ...]` for MIC. Pattern is generalizable — sub-agent dispatch failures in coordinators, LLM hallucination warnings, cache miss / stale-data warnings. Worth a Session 1209+ pass. |
| **Phase B.1 24h watch (fires 2026-06-23 14:48 UTC)** | **P1 (time-gated)** | Run checklist in `SESSION_1203_PHASE_B1_PRODUCER_REROUTE_CLOSE.md` §"24h watch checklist". Headline invariant: zero new deliverables with `workspace_id=1f0d467e-…` (SAW) created after 2026-06-22 19:48 UTC. |
| **Spider freshness watch (Session 1205 add)** | **P1 (24h)** | Verify run-spider-network keeps firing every 30 min; SpiderData rows with last_emit < 1h should be 60+. If 0, beat is dead — see finding `a4928480-…` remediation. |
| **Daily watch Day-3 (inference accuracy + default-only-projects)** | **P1 (daily, 2026-06-23)** | Append A/B/C/D + `report_initiative_kinds` to deliverable `9ba58690-…`. |
| **B.2 follow-up: action-item gate relaxation for Stage 1 only** | P2 | `core/services/initiative_auto_progression.py:484-509`. Allow Stage 1 → Stage 2 progression even if Stage 1 action items are incomplete. |
| **B.2 follow-up: beat schedule entry for process_initiative_auto_progression** | P2 | Service exists with documented "every 10 min" cadence, but no `PeriodicTask` row. Use the PR #2457/2458 pattern. |
| **Memory spike pattern investigation** | **P2 (Session 1205 finding)** | Finding `ea561389-…`. run_spider_network 444MB, collect_kalshi 345MB. Pattern: external-API fetch + bulk DB insert. Likely BeautifulSoup buffering or non-batched bulk_create. Worth a deep-dive once telemetry fix lands. |
| **Serper failure instrumentation** | P2 | Add explicit logging: `serper_failed status=… falling_back_to=ddgs`. Surfaces the 60% intelligence_tool failure rate (Layer 2 BROKEN finding). |
| **ContentWriterAgent 64% success rate deep-dive** | P2 | Only BROKEN agent in Layer 1 with significant 30d traffic. 9 done / 5 failed. Worth understanding what fails. |
| **`intelligence_tool` 60% success rate fix** | P2 | Layer 2 BROKEN finding + Spine 3 (Tool Migration Hardening) work. |
| **theodds spider 0-events investigation** | P3 | Finding `2de3d8d6-…`. May just be off-season / time-of-day filter; verify API key + spider implementation. |
| **SportsOddsAnalyst None-context wiring** | P3 (cleanup) | Finding `ed6a8f28-…`. 10-line fix to pass `context={}` instead of None at 3 callsites. |
| **Connectivity Roadmap Phase B.3 — NULL-workspace Initiative backfill (mgmt cmd)** | P2 | Roadmap §B.3. One-shot mgmt cmd for 31 of 46 Initiatives still NULL after Session 1196 backfill. Per-row resolution: parent inherit → creator user_workspace → default DBZ. |
| **Day-8 watch aggregation + decision (2026-06-30)** | **P1 (time-gated)** | Per-seed: keep / tighten / pull. File decision as deliverable tagged `session-1198-watch-result`. |
| **Plan C Phase 2 hard-reject flip (2026-06-29 gate)** | **P1 (time-gated)** | After 7-day watch is clean, replace Phase 1 diagnostic mark with `OrphanDeliverableError`. Spec: `INITIATIVES_FIRST_BACKBONE.md` §6.1. |
| **Session 1196 7-day watch (2026-06-29)** | **P1 (time-gated)** | Re-run `backfill_initiative_workspace_links --json-only`; diff against 2026-06-22 baseline. |
| **Finding 1 — advisor_invocations all zero in 7d** | **P3 (Session 1202 carryover)** | Investigate Row 10 refinement. Step 1: compare `set(Advisor.name)` vs `set(AgentExecution.objects.values_list('agent__name', flat=True))`. File as deliverable under Reality Map parent. |
| **Finding 2 — discord_health zero invocations** | **P3 (Session 1202 carryover)** | `ps -ef | grep discord`; `grep -i discord celery*.log`. If bot is up but not writing CeleryTaskEvent, `discord_health` needs a different data source. File as deliverable under Reality Map parent. |
| **Connectivity Roadmap Phase C — Structural fixes (close-session manifest + orient enhancement)** | P3 | Initiative `1859dd51-…`. Roadmap §C |
| **Phase B.1 PR-2 — re-scope as "generated_content sink / root_path contract" initiative** | P3 (optional) | Deferred Session 1203. See defer note on deliverable `8da895f0-…`. Only ship if a real consumer requires status reports landing in DBZ. |
| **PR3 — Step 4 heuristics implementation** | P2 | After Day 8 watch decision (≥80% precision on Step 3 → unblock PR3). |
| **Production rollout: Sessions 1196-1200 + Session 1203 cumulative** | **P0 (carryover, gated)** | Operator's go signal needed. Local-only until then. |

### Session 1205 close findings

10 audit deliverables filed on Initiative `29154d73-…` (Platform Capability Audit). 4 layer dashboards (Agents/Tools/Spiders/Bridges) + 6 deep-dive findings. The dashboards are the trust trail — each row is a checklist item; deep-dives become verification stamps.

Key Session 1206 inputs from the audit:
- **3 BROKEN tools/agents flagged**: `intelligence_tool` (60% sr), `messaging_tool` (69% sr), `ContentWriterAgent` (64% sr)
- **56 UNTESTED agents** (was DEAD before reframe) — many are likely just "wired but no scheduled trigger" — same pattern PR #2457 fixed for sports
- **Telemetry blind spots** (Layers 1, 2, 4 flat in dashboard) — fixed by Session 1206 P1
- **Memory spike pattern** on producer tasks (run_spider_network 444MB, kalshi 345MB)

### Session 1204 close findings

All 3 follow-ups (action-item gate, beat schedule, evidence-card pipeline) filed in the table above with concrete code pointers. Plus the revenue-recon work as P1 entry point.

### Session 1203 close findings

None deferred to Session 1204. PR-2 defer is documented + audit-trailed on deliverable `8da895f0-…`. Phase B.2 + B.3 + Phase C remain on the roadmap as separate scope.

### Project-clustering recon scope (Session 1194 P1) — SHIPPED Session 1197

The 8-cluster recon (expanded to 9 + 2 split-pairs = 11 rows) shipped via Session 1197 PRs #2416-#2422. Each cluster now has an Initiative row with explicit `kind` classification.

| Original Cluster | Resolution |
|---|---|
| 1. Session 1171 ML Queue + Auth Middleware Triage | Existing `077ff8b4` (ARCHIVED), kind=project |
| 2. Session 1184 Provenance Linkage | NEW Initiative, kind=project, status=COMPLETED |
| 3. Session 1187/1188/1189 Spider Context Utilization | **Split** into 3a (Recon, kind=investigation, COMPLETED) + 3b (Retune, kind=project, TRIAGE) |
| 4. Session 1192 Workspace Consolidation Follow-ups | NEW Initiative, kind=spec_backlog |
| 5. COO Operations Diagnostics | NEW Initiative, kind=recurring_artifact |
| 6. Orchestration Control Plane Mapping | NEW Initiative, kind=investigation |
| 7. Track Business News in June 2026 | NEW Initiative, kind=recurring_artifact |
| 8. MLB Run Line Desk v1 | Existing `997fb39b` (ACTIVE), kind=project |
| 9. Weekend Digest Autopilot | **Split** into 9a (Build/Ship, kind=project) + 9b (Issue Production, kind=recurring_artifact) |

Design memo: [`INITIATIVES_FIRST_BACKBONE.md`](docs/specs/INITIATIVES_FIRST_BACKBONE.md) §6.4. Full apply outcome + rollback levers: [`SESSION_1197_INITIATIVE_KIND_CLASSIFICATION.md`](docs/handoffs/SESSION_1197_INITIATIVE_KIND_CLASSIFICATION.md).

### Workspace consolidation — CLOSED Session 1192 + Session 1193

All shelf-tagged: 27 `shelf:content`, 74 `shelf:platform`, 14 tooltest (excluded). Real-untagged: 49 (48 Research + 3 Newsletter remainder). Initiative state pre-1201: ACTIVE=2, TRIAGE=12, COMPLETED=7, ARCHIVED=9. System Autonomous left active intentionally per Rigby's option C.

**Producer reroute regression — now actively scoped Session 1201 (was `780a8d15-…`):** Session 1199 fix to `_ensure_system_workspace` was partial. 3 other callsites (`agent_router.py:1083`, `tasks.py:7748`, `workspace_manager.py:1906`) still bypass `DEFAULT_PRODUCER_WORKSPACE_ID`. Initiative `05931145-…` (Producer Reroute Completion, ACTIVE, project) holds the fix scope. Spec: `docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md` §B.1.

### Initiative-tick 24h watch playbook

PR #2392 merged 2026-06-21 ~19:48 UTC. 24h elapses ~2026-06-22 19:48 UTC.

**Verification commands:**
```bash
# Summary lines from the last 24h
grep "INITIATIVE-TICK" celery.log | tail -50

# Steady-state check (refreshed should drift to 0)
grep "INITIATIVE-TICK" celery.log | tail -10 | awk -F'refreshed=' '{print $2}' | awk '{print $1}'

# No NULL rows remaining
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_document_registry import Initiative
print('null_count:', Initiative.objects.filter(last_activity_at__isnull=True).count())
"

# No singleton_task skips (would mean tick runs >300s)
grep "singleton_task.*initiative-activity-tick" celery.log
```

**Rollback levers (if needed):**
- Disable: `PeriodicTask.objects.filter(name='initiative-activity-tick').update(enabled=False)`
- Per-call no-op: pass `hard_cap=0`
- Full revert: `git revert eeac179a`

### 7d AC watches that start 2026-06-28

Session 1188 + 1189 PRs ship measurable AC backed by Item 1's `AgentExecution.input_data['spider_context']` blob. Query pattern:

```python
AgentExecution.objects.filter(
    owner_agent__iexact='<AgentName>',
    created_at__gte=now - timedelta(days=7),
    input_data__spider_context__has_data_by_category__<bucket>=True,
).count()
```

**Per-PR AC summary:**

- **#2380/#2382 (Session 1188):** ImageAgent — `design`/`visual_trends`/`video` present in `categories_queried` with ≥1 `has_data=True`; ResearchAgent — `ai_ml`+`business` present with ≥1 `True` against `ai_ml`; ThinkingAgent — ≥3 dispatches with spider context built, ≥1 `True`.
- **#2386 PR-3A:** legacy substring-matched agents (e.g., `ImageEditingAgent`, `WhaleWatcherAgent`) show alias divergence — `creative`/`crypto` in `requested_categories` but resolved counterparts in `resolved_categories`.
- **#2388 PR-3B:** `ai_ml` shows in `has_data_by_category` for the 19 specced agents with ≥1 `True` across dev/strategy/content tier. `remote_work` for job/career. `legislation` for legal/cto/coo. `content` for content_writer/topic_miner. `cybersecurity` for security-mapped agents (alias-divergence proof).

### Carryover from Session 1186/1187/1188/1190 *(reconciled Session 1201 against runtime — see roadmap §C.2)*

| Deliverable ID | Title | Runtime Status | Notes |
|---|---|---|---|
| `48b73b04-373a-4d25-b263-9925c7c1a084` | **B.1** — Unify Initiative-stage deliverables | ✅ `completed` | Closed per runtime; docs lag corrected Session 1201 |
| `9d9db48a-4819-4e2b-9548-998c0fe2f8f5` | **PR-D contract flip** — 24h WARN-volume watch | ✅ `completed` | Closed per runtime; docs lag corrected Session 1201 |
| `88952c54-a4a4-47e8-9fe1-85b3d747be03` | Session 1187 Utilization Recon — Master Tracking | `blocked` | Runtime shows blocked, not partial. Re-investigate or close. |
| `9a00667b-2206-4f25-8813-a42faf463439` | **BUG** — DM system regression | ✅ `completed` | Closed per runtime; docs lag corrected Session 1201 |
| `b8ca4f5c-2b3c-4095-ab3b-329e02b98c9e` | Session 1189 PR-3B retune list | ✅ `completed` | Reference only; shipped via #2388 |
| `13032820-1f36-4a1c-8843-6a9d53653405` | Missing PA tools — SpiderData aggregation entry | ✅ `completed` | Shipped as `spider_data_aggregation_tool` v1 (#2387) |

### Standard FIRST THING checks

1. Disk: `df -h /System/Volumes/Data`. Swap: `sysctl vm.swapusage`.
2. Through Rigby (`tools/pa_local.sh` is pinned to the current thread): `platform_config_tool overview` → confirm `service_context: local`.
3. **Worker freshness check (Session 1200 added):** `ps -eo pid,lstart | grep celery` vs `git log -1 --format='%h %ci' main` — if workers predate latest main commit, restart via `pkill -9 -f 'celery -A core'; rm -f .celery*.pid; make celery` before any verification work.
4. `gh pr list --author @me --state open` — expected empty (stale carryover PRs from April/May are unrelated).

### Stacked-PR footgun reminder (still active)

`gh pr merge --delete-branch` on a parent PR **auto-closes child PRs unrecoverably** when their base branch is deleted. `gh pr reopen` fails. Workaround: retarget child PR's base to `main` BEFORE merging the parent (`gh pr edit <child> --base main`). Session 1188 hit this with #2381 → had to open fresh #2382.

### `Agents count claims` CONFLICT — RESOLVED Session 1198

PR #2424 cleared the long-standing CONFLICT that was forcing `--admin` bypass on every PR. Root cause: one Session 1187 historical-context line in `00-START-NEXT-SESSION.md` had `"(in-code, 51 agents)"` on a line containing "Headline finding:" — context-kit's `Headline` strong-token propagated total-dimension classification to the parenthetical 51, producing canonical totals `{83, 51}` → CONFLICT. Fix was truncating the stale historical session blocks (preserved in `docs/handoffs/`). CI now runs clean without `--admin`.

Memory: [`feedback_context_kit_headline_propagates_total.md`](.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_context_kit_headline_propagates_total.md) for the gotcha + canonical-doc cleanliness rule.

---

## Historical session blocks

Sessions 1182-1195 close-out blocks lived here through Session 1197. Removed in Session 1198 close to keep this working file lean — full text preserved in `docs/handoffs/SESSION_NNNN_*.md`. The Session 1196 + 1197 closes referenced from this file's body link directly to their handoffs.

Run `ls docs/handoffs/SESSION_*.md | sort -V | tail -20` to see the recent close list.
