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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation; use that if you don't want to remember the env vars. Current pinned conversation: `pa-a60842917d36` (spun mid-Session 1184 after `pa-f4644aa2fd1b` hit a tool-refusal loop caused by a missing `PA_USE_FUNCTION_CALLING=true` env var on a manual PA worker restart — see READ THIS FIFTH below).

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

## SESSION 1195 — CURRENT ENTRY POINT

### SESSION 1194 CLOSED — Initiatives-First Backbone pivot + Plans A + B shipped (2026-06-21)

Full handoff: [`SESSION_1194_INITIATIVES_FIRST_BACKBONE_PIVOT.md`](docs/handoffs/SESSION_1194_INITIATIVES_FIRST_BACKBONE_PIVOT.md). **3 PRs shipped**, AC1+AC2+AC3+AC4 of `INITIATIVES_FIRST_BACKBONE.md` closed.

| PR | Theme | Status |
|---|---|---|
| **#2397** | docs/spec — Initiatives-First Backbone pivot + deferred clustering pointer | merge-ready |
| **#2398** | Plan A — close audit gap (field shape + workspace_id filter + `audit_deliverable_endpoints` mgmt cmd) | merge-ready (stacked on #2397 conceptually; targets main) |
| **#2399** | Plan B — read-path initiative linkage + paginated `initiative_deliverables` action | merge-ready (stacked on #2398 — retarget to `main` before merging #2398) |

**Spec (operating contract for this and future sessions):** [`docs/specs/INITIATIVES_FIRST_BACKBONE.md`](docs/specs/INITIATIVES_FIRST_BACKBONE.md). Deferred clustering pointer: [`docs/specs/DELIVERABLE_CLUSTERING_DEFERRED.md`](docs/specs/DELIVERABLE_CLUSTERING_DEFERRED.md).

**3 spine Initiatives — persisted + bound to Donkey Betz:**

| # | Name | UUID |
|---|---|---|
| 1 | Initiatives-First Wiring + No-Orphan Output | `6941372d-b13c-4631-91c8-749fa65c55a0` |
| 2 | Agent Capability Map + Router Contracts | `2071a9c6-986f-4528-be90-8cccaa595f1e` |
| 3 | Tool Migration Hardening (web_search → intelligence_tool) + Failure Fix | `7e23d621-4d0c-409a-a680-4fd2e015d04b` |

`target_workspace_id` backfilled to Donkey Betz (`b4503364-…`) at session close for all 3 (Rigby's `initiative_create` write path doesn't yet require/infer it — Plan C side-quest).

### FIRST THING Session 1195

**Stacked-PR check.** Before merging anything, retarget #2399 base to `main` (its base is currently the #2398 branch — auto-close footgun per Session 1188 #2381 incident, memory `feedback_stacked_pr_base_deletion_footgun.md`):

```bash
gh pr edit 2399 --base main
```

Then merge order: **#2397 → #2398 → #2399**.

After merges, **Plan C is the P1**. Read `INITIATIVES_FIRST_BACKBONE.md` §3.C end-to-end. §6.1 (Phase 1 mark-diagnostic + `[ORPHAN-DELIVERABLE]` log → Phase 2 hard-reject after 7d zero-emission window) is **already ratified Session 1194**. §6.2 (inference rule for missing `initiative_id`) is **open** — decide once the backfill mgmt command runs against real Donkey Betz data.

**Active conversation:** `pa-e11847db632a4ee8` is the healthy Session 1194 thread with full backbone context loaded. Reuse OR spin a fresh thread depending on whether you want clean canvas for Plan C.

**Donkey Betz workspace_id (pin):** `b4503364-2573-4401-9e28-61a739e0ce50` — 164 deliverables. All 3 spine Initiatives bound here.

### Pick this session

| Item | Priority | Where it's defined |
|---|---|---|
| **Plan C — write-path enforcement (Phase 1)** | **P1** | `INITIATIVES_FIRST_BACKBONE.md` §3.C. `create_deliverable()` accepts-and-marks `publish_intent=diagnostic` + emits `[ORPHAN-DELIVERABLE]` log when no initiative resolves. AC5a. |
| **Plan C — backfill mgmt command** | **P1** | `INITIATIVES_FIRST_BACKBONE.md` §3.C.1. `backfill_deliverable_initiative_links --workspace <uuid> --dry-run/--apply` — walks recent deliverables, proposes initiative attachments, reports attached/unmatched/ambiguous counts. AC6. |
| **Plan C side-quest — `initiative_create` requires target_workspace_id** | P2 | Carry-over from Session 1194 spine-Initiative diagnostic. Fold into Plan C since both are write-path enforcement. |
| **Plan D — governor gating** | P2 | `INITIATIVES_FIRST_BACKBONE.md` §3.D. Scheduler skips dispatch when no ACTIVE Initiative matches; `[GOVERNOR-SKIP]` log. AC7. Can land in parallel with Plan C. |
| **Tool Migration Hardening (Initiative 3)** | P2 | §4.3 + Initiative `7e23d621-…`. `web_search` → `intelligence_tool.search` audit + gateway retry/backoff. ~50% failure rate to investigate. AC9-AC10. |
| **AC8 round-trip traceability test** | P3 | §4.1 of the spec. Small unit-test follow-up. |
| **Plan C Phase 2 hard-reject flip** | DEFERRED-7d | After Phase 1 ships, watch `grep '\[ORPHAN-DELIVERABLE\]' celery.log` for trailing 7d window. Zero emissions → flip to hard `OrphanDeliverableError`. AC5b/c. |
| **Project-clustering recon** | DEFERRED | `DELIVERABLE_CLUSTERING_DEFERRED.md`. Revive after backbone AC5+AC6 pass. |
| **Initiative-tick 24h watch** | P1 (time-gated) | Start 2026-06-22 19:48 UTC (24h after PR #2392 merge). Grep `celery.log` for `[INITIATIVE-TICK]`. Confirm steady-state drift to 0. Playbook below. |
| **7d AC watches** | P1 (time-gated) | Start 2026-06-28. Per-PR AC tables in #2380/#2382/#2385/#2386/#2387/#2388. |
| **PA LLM iteration cap silent failure** | **P2** | Session 1193 follow-up. Deliverable `c2bac9c0-...`. Real engineering. `core/services/unified_pa_entrypoint.py:1298` `max_iterations=8` leaves 7 effective tool-call iterations. On forced-text final iteration, LLM emits unexecuted tool-call JSON as text body. Silent failure mode that bit us mid-Session-1193 on tagging-heavy turns. Two-part fix: raise cap to 12 + detect tool-call JSON in final-iteration text. |
| **Producer reroute** | P2 | Session 1192 follow-up. Deliverable `780a8d15-...`. `core/services/workspace_manager.py:1728-1773`. Three fix shapes documented. |
| **Initiative populate redesign** | P2 | Session 1192 follow-up. Deliverable `ae5251f1-...`. **Directly connected to this session's project-clustering recon.** Two fix shapes documented (TRIAGE candidates / Collections/Folders entity). |
| **PR-D contract flip** | P2 | Deliverable `9d9db48a-...`. 24h WARN-volume gate elapsed 2026-06-22 16:00. Run the grep at AC1; if clean, open PR-D. |
| **COO Backlog #4 prefetch normalization** | P3 | Session 1193 follow-up. Deliverable `e17950d8-...`. Per-worker `--prefetch-multiplier=1` in Procfile for long_running/content/code. |
| **COO Backlog #9 tool-call telemetry rollup** | P3 | Session 1193 follow-up. Deliverable `bebd6794-...`. Mirror Session 1167 #7 (`top_consumers.py`) pattern for tools. |
| **deliverable_tool tooling improvements** | P3 | Session 1192 follow-up. Deliverable `c942274b-...`. `tags_add`/`tags_remove`/`bulk_update_workspace` actions. |
| **Research category tagging** | P3 | 48 items still untouched per Chris's "do last with Claude" pick. Strategic batch — same `shelf:content` vs `shelf:platform` split pattern + likely creates Research-subdomain tags. Could fold into project-clustering recon if research items group by topic. |
| **Newsletter remainder** | P3 | 3 items still untagged (vs the original 13). Trivial cleanup if it falls out of project-clustering. |
| **C-trace remediation #1, #4 (Session 1187)** | P2 (structural) | Larger blast radius — needs design call with Rigby. |
| **Adjacent C-trace investigations** | P3 (small) | (a) MarketingStrategyAgent only agent inheriting execute() — likely broken. (b) AgentExecution.owner_agent empty ~75%. (c) huggingface SpiderItemHash item_title='Unknown'. |
| **DM-system bug** | P3 | Deliverable `9a00667b-...`. |
| **Dedicated inventory-refresh PR** | P3 | Reconcile `Agents count claims` CONFLICT. |
| **Daily detector for workspace regressions** | P3 | Rigby's Session 1192 suggestion. Lightweight beat task. |

### Project-clustering recon scope (Session 1194 P1)

Sample of 8 visible clusters from Session 1193 close — needs full enumeration this session:

1. **Session 1171 — ML Queue + Auth Middleware Triage** (4 deliverables, PR #2328)
2. **Session 1184 — Provenance Linkage** (5+ deliverables, PRs #2362/#2364/#2365)
3. **Session 1187/1188/1189 — Spider Context Utilization** (6 Axis recon + 4 PRs + retune list)
4. **Session 1192 — Workspace Consolidation Follow-ups** (4 P2/P3 deliverables)
5. **COO Operations Diagnostics** (5 daily COO Analysis runs — should be ONE recurring artifact)
6. **Orchestration Control Plane Mapping** (CTO ×3 + DevOps ×4 + COO ×1 + Research ×3 = 11 parallel runs on the SAME investigation)
7. **Track Business News in June 2026** (3-4 ContentWriterAgent blog variants)
8. **MLB Run Line Desk v1** (product spec — real Initiative-shape)

4 natural relationship patterns:
- Time-bounded engineering projects (Session NNNN themes)
- Recurring artifacts (daily diagnostics, weekend digests)
- Investigation workstreams (1 question → N parallel agent answers)
- Product specs that need execution (MLB Run Line, Revenue Desk, Weekend Digest)

### Workspace consolidation — CLOSED Session 1192 + Session 1193

All shelf-tagged: 27 `shelf:content`, 74 `shelf:platform`, 14 tooltest (excluded). Real-untagged: 49 (48 Research + 3 Newsletter remainder). Initiative state: ACTIVE=2, TRIAGE=12, COMPLETED=7, ARCHIVED=9 (down from 11 ACTIVE before Session 1192 zombie cleanup). System Autonomous left active intentionally per Rigby's option C.

**Known regression vector (still filed, not yet shipped):** `core/services/workspace_manager.py:1739` `_ensure_system_workspace` auto-recreates. See `780a8d15-...`.

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

### Carryover from Session 1186/1187/1188/1190

| Deliverable ID | Title | Priority | Status |
|---|---|---|---|
| `48b73b04-373a-4d25-b263-9925c7c1a084` | **B.1** — Unify Initiative-stage deliverables (follow-on to PR #2376) | P3 | Pending |
| `9d9db48a-4819-4e2b-9548-998c0fe2f8f5` | **PR-D contract flip** — 24h WARN-volume watch after PR #2376 merge | P2 | 24h elapsed 2026-06-22 16:00. If grep is clean, PR-D is ready. |
| `88952c54-a4a4-47e8-9fe1-85b3d747be03` | Session 1187 Utilization Recon — Master Tracking | — | C-trace #3 fully closed across Sessions 1188+1189. #1, #2, #4 still open per table above. |
| `9a00667b-2206-4f25-8813-a42faf463439` | **BUG** — DM system: missing reply delivery + no UI notifier + thread collapsing | P3 | Three symptoms + two Rigby diagnostic leads. Defer fix; flip to P1 only if Chris escalates. |
| `b8ca4f5c-2b3c-4095-ab3b-329e02b98c9e` | Session 1189 PR-3B retune list | — | Shipped via #2388. Reference doc for the 19-agent ai_ml rollout + 5-bucket map. |
| `13032820-1f36-4a1c-8843-6a9d53653405` | Missing PA tools — SpiderData aggregation entry | — | CLOSED — built and shipped as `spider_data_aggregation_tool` v1 (#2387). |

### Standard FIRST THING checks

1. Disk: `df -h /System/Volumes/Data`. Swap: `sysctl vm.swapusage`.
2. Through Rigby (use `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-chris-token>` explicitly — `tools/pa_local.sh` is pinned to a stale conv): `platform_config_tool overview` → confirm `service_context: local`.
3. **Use Rigby's pre-spun fresh thread `pa-e11847db632a4ee8`** ("Session 1194 — Project-clustering recon (Donkey Betz deliverables)"). Chris explicitly asked for fresh threads on BOTH sides for this session. Don't reuse `pa-89b8f02deccc4f17`.
4. `gh pr list --author @me --state open` — expected empty.

### Stacked-PR footgun reminder (still active)

`gh pr merge --delete-branch` on a parent PR **auto-closes child PRs unrecoverably** when their base branch is deleted. `gh pr reopen` fails. Workaround: retarget child PR's base to `main` BEFORE merging the parent (`gh pr edit <child> --base main`). Session 1188 hit this with #2381 → had to open fresh #2382.

### Pre-existing CONFLICT — `--admin` bypass still required

`context-kit verify` `Agents count claims` CONFLICT still on main. Strict mode Repo Guardrails fails on every PR until reconciled. Chris approved blanket `--admin` bypass for code-only PRs. Worth a dedicated inventory-refresh PR if anyone has the bandwidth.

---

## SESSION 1193 CLOSED — Deliverable tagging + COO Backlog audit + project-clustering insight (2026-06-21)

**0 PRs — data-layer ops + audit + filings.** Full handoff: [`SESSION_1193_DELIVERABLE_TAGGING_AND_PROJECT_CLUSTERING_INSIGHT.md`](docs/handoffs/SESSION_1193_DELIVERABLE_TAGGING_AND_PROJECT_CLUSTERING_INSIGHT.md).

**Tagging:** ~107 deliverables tagged. Final shelf coverage on Donkey Betz (164 total): 27 `shelf:content`, 74 `shelf:platform`, 14 tooltest (excluded), 49 untagged (48 Research + 3 Newsletter remainder).

**7 new deliverables filed in Donkey Betz:**

| ID | Title | Priority |
|---|---|---|
| `c2bac9c0` | PA LLM iteration cap — raise from 7 + surface silent fallback | **P2** |
| `c942274b` | deliverable_tool tooling improvements (tags_add/remove + bulk) | P3 |
| `b47a76b4` | COO Backlog spot-check audit — items #3-9 | audit |
| `e17950d8` | COO Backlog #4 — Prefetch normalization | P3 |
| `bebd6794` | COO Backlog #9 — Tool-call telemetry rollup | P3 |

Plus 780a8d15 and ae5251f1 carried from Session 1192.

**Bug surfaced:** PA LLM iteration cap silent failure pattern. On forced-text final iteration, LLM emits tool-call JSON in response body — zero writes land but user sees what looks like a response. Captured fully in c2bac9c0 deliverable.

**Chris's late-session insight (queued for Session 1194):** flat-deliverable model isn't capturing project clusters. 8 obvious clusters identified. Both sides start fresh threads. See Session 1193 handoff §"Chris's late-session insight" for the 4 natural relationship patterns.

**Two precedents locked:**
1. Shelf taxonomy split: `shelf:content` for content artifacts, `shelf:platform` for engineering/diagnostics, tooltests get `tooltest`+`test_artifact` and NO shelf.
2. Bundle pattern for cap-aware tagging: Rigby fetches details → emits APPLY-BATCH list → Claude ORM-applies. Avoids per-turn cap.

---

## SESSION 1192 CLOSED — Workspace consolidation Steps 4-7 closed (2026-06-21)

**0 PRs — data-layer ops only. 156 deliverables consolidated into Donkey Betz. 1 follow-up filed.** Full handoff: [`SESSION_1192_WORKSPACE_CONSOLIDATION_CLOSE.md`](docs/handoffs/SESSION_1192_WORKSPACE_CONSOLIDATION_CLOSE.md).

**Migration breakdown:**
- 16 items via Rigby (chris-personal batches 1-3 + 1 newsletter tag + 4 content_reject) before hitting tool-call-per-turn cap
- 122 items via direct Django ORM (25 chris-personal + 65 Local QA + 6 small-ws + 29 System Autonomous + 2 NULL orphans)

**Final state — all 6 Step 7 checks PASS:**
- Donkey Betz: **156** (was 29 pre-session)
- All 6 drained workspaces: count=0 + is_active=False
- Active workspaces: Donkey Betz + System Autonomous only
- Orphans: 0 | NULL workspace_id: 0
- initiative_id preservation: 68 with FK, 88 without (none stripped)

**Key precedent established (Session 1192):** triage decisions (status) are independent of workspace decisions. `content_tool action=content_reject` only changes status; it does NOT move workspace. For "delete" intent, need both `content_reject` AND `deliverable_tool.update workspace_id=<target>`. Hard-delete is NOT exposed in the toolset.

**Filed follow-ups (both in Donkey Betz):**
- `780a8d15-9ca0-4d91-970f-6934a24fc08d` — Producer-reroute fix for `_ensure_system_workspace` regression vector. P2.
- `ae5251f1-4863-4319-9c82-a82b6cfc52c2` — Initiative populate redesign (TRIAGE candidates + Collections/Folders option). P2. Filed after Chris paused on the UI "create initiatives from deliverables" button.

**Post-close Initiative cleanup (same session):** Chris asked what the populate button does. Code trace + preview showed it'd create 11 ACTIVE category-bucket Initiatives, conflicting with the canonical project semantic. Routed to Rigby; her recon found 9 existing "Auto-populated From N X" zombie Initiatives. **Archived all 9** via ORM. Final Initiative status totals: ACTIVE=2, TRIAGE=12, COMPLETED=7, ARCHIVED=9 (was 0).

**Two memory candidates** (non-blocking, assess at session-end review):
1. Bulk operations: ORM > per-item dispatch when N>10. Plan ORM migration path upfront for drain ops of 100+ items.
2. Daily detector for workspace regressions: lightweight beat task flagging deliverables landing in System Autonomous / NULL workspace_id, until producer reroute lands.

**Pinned conversation:** `pa-55d90b2a34524bf9` (Session 1190+1191+1192 thread; rotate for Session 1193).

---

## SESSION 1191 CLOSED — Initiative system lifecycle fix: cheap staleness sweep + auto-populate bootstrap (2026-06-21)

**1 PR merged + Initiative system P1 closed + 3 memories saved.** Full handoff: [`SESSION_1191_INITIATIVE_ACTIVITY_TICK.md`](docs/handoffs/SESSION_1191_INITIATIVE_ACTIVITY_TICK.md).

| PR | Commit | Theme |
|---|---|---|
| **#2392** | `eeac179a` | `feat(session-1191-initiative-activity-tick)` — Two-layer fix for Initiative.last_activity_at=null. (1) populate_initiatives_api bootstrap via update_activity(reason='auto_populate_create'). (2) New `_impl_initiative_activity_tick` — no-LLM, no-side-effects beat task crontab(*/30), aggregates max(initiative.updated_at, action_items.updated_at, deliverables.updated_at) with strict GT-only writes, hard cap 100, @singleton_task(ttl=300), max_retries=0. Backfill mgmt command for historical NULL rows (idempotent, --dry-run). 9 unit tests. Preserves §6.4 invariant. |

**Live proof (local DB, pre-merge + post-merge):**
- Backfill: 11 NULL rows → set to created_at.
- Manual `.delay()` after make celery restart: `examined=30 refreshed=14 skipped_no_signal=0` in 100ms.
- Spot-check `f9eb535f-...` (Auto-populated From 11 Newsletter Deliverables): NULL → 2026-06-21 10:05:00 (max cheap signal).
- All 9 unit tests passing under USE_PGBOUNCER=0 path (PgBouncer transaction pool can't create test DBs).

**Three memories saved + indexed in MEMORY.md:**
1. `feedback_invariant_check_first.md` — when something "isn't running," check if it's supposed to before fixing forward.
2. `feedback_two_layer_root_cause_rule.md` — fix both cold-born + no-driver halves, or label cosmetic-only.
3. `feedback_cheap_staleness_aggregator_pattern.md` — reusable 8-step shape for any parent.last_activity_at field.

**Two notes for next session:**
1. The 30-min beat tick is now live. 24h watch starts 2026-06-22 ~19:48 UTC (see playbook above).
2. The §6.4 invariant from Session 1162 is intact — `advance_initiative_pipeline` is still on-demand only. If a future session wants to revisit that decision, it's a separate design call (option C from this session's fix-shape triage card).

**Pinned conversation:** `pa-55d90b2a34524bf9` (Session 1190+1191 thread, healthy at pause).

---

## SESSION 1190 CLOSED PARTIAL — Scrubber UUID fix + workspace consolidation kicked off + Initiative confirmed broken (2026-06-21)

**1 PR merged + workspace consolidation Steps 1-3 done + 3 priority deliverables triaged + Initiative recon complete.** Full handoff: [`SESSION_1190_PARTIAL_WORKSPACE_CONSOLIDATION_AND_SCRUBBER_FIX.md`](docs/handoffs/SESSION_1190_PARTIAL_WORKSPACE_CONSOLIDATION_AND_SCRUBBER_FIX.md).

| PR | Commit | Theme |
|---|---|---|
| **#2390** | `680aa5d4` | `fix(session-1190-scrubber)` — protect UUIDs from CC regex false-positive. New `_UUID_PATTERN` + mask/restore in `scrub()`. 18 tests. Resolved un-addressable Agent-Testing workspace UUID (`59af4248-70b9-4472-8062-810452446698` now intact). |

**Workspace consolidation status (7-step plan, ratified mid-session):**

| # | Step | Status |
|---|---|---|
| 1 | Scrubber UUID fix | ✅ shipped (#2390) |
| 2 | Create "Donkey Betz" workspace | ✅ created (`b4503364-...`) |
| 3 | Inventory refresh | ✅ done (~77 candidates) |
| 4 | Triage priority deliverables | ◐ 3 of ~74 done |
| 5 | Migrate survivors | ◐ 2 of ~74 migrated |
| 6 | Deactivate other workspaces | ⏳ Session 1191 |
| 7 | Post-migration verification | ⏳ Session 1191 |

**3 priority deliverables triaged:**
- `644877f1-...` COO Operator Report → **CLOSED** as superseded by 10-item backlog
- `3973c817-...` Known Bugs queue → **MIGRATED** to Donkey Betz + appended Session 1184 PR #2362 resolution note for item #2
- `1be2cf55-...` COO 10-item Backlog → **MIGRATED** to Donkey Betz + appended file:line verification notes for items #1, #2, #10

**Spot-check evidence cited in append notes** (live grep):
- #1 DB safety defaults: `core/settings.py:264-292` (statement_timeout + idle_in_transaction_session_timeout, Session 1165 comment)
- #2 PG application_name tagging: Procfile lines 16-33 (all 11 processes tagged, Session 1166 comment)
- #10 Provenance receipt: `core/services/deliverable_provenance.py` + `deliverable_factory.py` + `td_handlers_agents.py`

**Initiative system recon (Chris's other P1 ask):** confirmed broken in observable ways. 30 records exist, 11 ACTIVE / 12 TRIAGE / 7 COMPLETED. Most stuck at `current_stage=1`, `last_activity_at: null`. Pattern: auto-populated from N deliverables but never advanced. Failure mode: lifecycle engine isn't wiring stage advancement / action-item coupling / event-driven updates into the work loop. Targeted fix PR scope for Session 1191.

**Workspace-system finding:** `deliverable_tool action=update workspace_id=<new>` is the move verb. End-to-end verified on 2 migrations. `updated_fields: ["tags", "workspace"]` confirms persistence.

**Two course corrections worth preserving** (memory candidates):
1. Workspace-name assumptions are unreliable. Claude assumed `chris-personal` = scratch; Chris corrected — contains real strategic specs (MLB Run Line Desk, COO Operator Report, Revenue Desk + Product Velocity Desk charter, Agent Validation Plan, etc.).
2. Regex false-positives from structure collisions. CC regex `\b\d{4}-\d{4}-\d{4}-\d{4}\b` matched UUID digit-tails. Lookbehind/lookahead tweaks don't help at tail position. Fix pattern: detect protected entities first, mask with placeholders, run scrub, restore.

**Pinned conversation:** `pa-55d90b2a34524bf9` (Session 1190 thread, healthy at pause). Donkey Betz workspace_id: `b4503364-2573-4401-9e28-61a739e0ce50`.

---

## SESSION 1189 CLOSED — Spider context end-to-end: 4 PRs merged (AC + alias + tool + rollout) (2026-06-21)

**4 PRs merged, all `--admin` bypass on pre-existing CONFLICT.** Full handoff: [`SESSION_1189_SPIDER_CONTEXT_AC_VOCABULARY_TOOL_AND_ROLLOUT.md`](docs/handoffs/SESSION_1189_SPIDER_CONTEXT_AC_VOCABULARY_TOOL_AND_ROLLOUT.md).

| Item | PR | Commit | Theme |
|---|---|---|---|
| 1 — AC instrumentation | [#2385](https://github.com/clwest/donkey-betz-platform/pull/2385) | `403f836e` | Persist `spider_context` blob on `AgentExecution.input_data` with per-category breakdowns + `build_ms`. New helper `agent_router.build_spider_context_ac_blob`. |
| 2 — PR-3A alias layer | [#2386](https://github.com/clwest/donkey-betz-platform/pull/2386) | `b6d80ff4` | `CATEGORY_ALIASES` + `KNOWN_DATA_TYPES` + `_normalize_categories`. `categories_requested` vs `categories_queried` divergence threaded through AC blob. |
| 3 — SpiderData aggregation PA tool v1 | [#2387](https://github.com/clwest/donkey-betz-platform/pull/2387) | `29a5968f` | `spider_data_aggregation_tool` registered in dispatcher + pa_tool_schemas. Pure `aggregate_spider_data()` + dispatcher handler. Smoke-tested live by Rigby (83ms/20ms). |
| 4 — PR-3B retune | [#2388](https://github.com/clwest/donkey-betz-platform/pull/2388) | `fb9b8539` | `security` → `cybersecurity` alias. `ai_ml` added to 19 agent mappings. 5 high-supply bucket rollouts (remote_work/training/legislation/prediction_markets/content). |

**Sequence pushback (Rigby vs Chris's tool-first intuition) won the day.** Chris leaned tool-first; Rigby pushed back that AC-first sequencing makes 7d watches verifiable AND lets PR-3A ship immediately without new tools. Sequence ratified as 1→3→2→4. By the time Item 3 landed, Items 1+2 were already merged and Rigby drove Item 4 recon end-to-end through the new tool — zero Django shell scripts this session.

**Collaboration shape:** every item routed scope through Rigby first per scope rule. She owned recon (call-chain audits, supply queries, mapping inventories), API design call for Item 3, agent-by-agent retune list for Item 4 (deliverable `b8ca4f5c-...`), security alias decision. Claude owned code edits, tests, branches, PRs, worker restart between Items 3 and 4, presenting design decisions at C-style pause points.

**Capabilities now live:**
1. AC observability — every dispatch records the spider_context blob; AC watches ORM-queryable
2. Vocabulary bridge — creative/crypto/sports/security all auto-expand to real data_type values
3. First-class supply recon via `spider_data_aggregation_tool` PA tool
4. ai_ml now consumed by 19 agents (was 1); 5 buckets rolled out; prediction_market finally gets its own bucket

**New memory candidates** (capture at next session-end review):
1. Rigby pushes back on sequencing — listen. When two reasonable orderings exist, her counter often refines the choice.
2. First-class observability fields make AC trivial. Item 1's requested-vs-resolved divergence wasn't just observability — it was a contract for Item 4's AC.
3. Tool-handler pattern: pure function + dispatcher entry point. Item 3 separated `aggregate_spider_data()` (pure, testable) from the dispatcher handler. Unused interface args (tool_name/user_id) belong in the signature — don't underscore-rename.

---

## SESSION 1188 CLOSED — Spider context Hot-agent wiring: 2 PRs merged (PR-1 explicit keys + PR-2 vocabulary retune) + PR-3 spec filed (2026-06-21)

**2 PRs merged, both `--admin` bypass on pre-existing CONFLICT (Chris-approved blanket).** Full handoff: [`SESSION_1188_SPIDER_CONTEXT_VOCABULARY_RECON_AND_RETUNE.md`](docs/handoffs/SESSION_1188_SPIDER_CONTEXT_VOCABULARY_RECON_AND_RETUNE.md).

| PR | Commit | Theme |
|---|---|---|
| **#2380** (PR-1) | `6691d408` | `feat(session-1188-spider-context)` — explicit `imageagent`/`researchagent`/`thinkingagent` keys in `AGENT_SPIDER_MAPPINGS`. ThinkingAgent moved off `default` fallback to `['tech','news','science','financial']`; Image/Research mirror substring outcomes (no functional change). |
| **#2382** (PR-2) | `ab9274e3` | `feat(session-1188-spider-context)` — retunes `imageagent` → `['design','visual_trends','video','tech','entertainment']` (drops dead `'creative'` which had 0 actionable in 30d); `researchagent` adds `'ai_ml'` (364 actionable) + `'business'` (92). **Replaces #2381** which auto-closed when its base branch was deleted on PR-1 merge. |

**Headline finding:** AGENT_SPIDER_MAPPINGS vocabulary doesn't match real `SpiderData.data_type` values. `'creative'`, `'crypto'`, `'sports'` are dead keys (zero supply); `'ai_ml'` (364 actionable/30d, 2nd-largest tech-adjacent bucket) wasn't referenced by any agent. PR-2 fixed ImageAgent+ResearchAgent; broader fix lives in PR-3 spec deliverable `a48e1164-edc6-49d8-bc70-135bedb614a9` (Session 1189 pickup).

**Collaboration shape:** every recon routed to Rigby first per scope rule (`feedback_rigby_scope.md`). She owned PR-prep mapping audit + 30d telemetry baselines + AC drafting + scope-call decisions + Chris direct message on CI bypass. Tool gap (SpiderData category aggregation) surfaced and filed (appended +2491 chars to deliverable `13032820-...`) — not silently bridged. Claude owned code edits + one-off Django shell execution (where Rigby tools genuinely lacked the capability) + PR opening + admin merge.

**New memory candidates** (capture at next session-end review):
1. PR stacking + base-branch deletion footgun (`gh pr merge --delete-branch` on parent auto-closes child unrecoverably; retarget child to main first).
2. Substring-matching dicts hide "missing" entries (`SpiderContextBuilder._get_agent_categories` uses `if pattern in agent_lower` — check matching mechanism before concluding entry is missing).
3. Vocabulary mismatch between mapping dicts and runtime data (mapping uses semantic names; read path queries by runtime `data_type` values — they drift).

---

## SESSION 1187 CLOSED — Utilization Recon: 7 deliverables filed in Local QA, 3 spider→agent wiring break points found, 0 code changes (2026-06-21)

**Strategic pivot session.** No PRs. Recon-only per Chris's scope: *"go through all of the Agents, right now we have them but they aren't really doing anything. We also need to verify that the spiders are actually pulling in data to feed the system."* Full handoff: [`SESSION_1187_UTILIZATION_RECON.md`](docs/handoffs/SESSION_1187_UTILIZATION_RECON.md).

**Headline finding:** the framing was inverted. Agents are dormant (56/83 = 0 dispatches in 30d, only 9 Hot, 0 Warm). Spiders are cranking (198,678 items/30d across 78 spiders). The break is in the wiring layer — `SpiderContextBuilder.AGENT_SPIDER_MAPPINGS` (in-code, 51 agents) is the actual driver but doesn't route any huggingface/ai_ml data to any agent; the parallel `AgentSpiderConnection` table (DB, 55 rows) is dead code in the read path; the category vocabulary doesn't bridge between the two sources. **Confirmed at runtime: 0 of 92 recent dispatches reference huggingface despite 331 fully-embedded SpiderData rows being available.**

**7 deliverables in Local QA workspace** (master + 5 axes + missing-tools list) with per-axis AC checklists + verifier commands. Master: `88952c54-a4a4-47e8-9fe1-85b3d747be03`. Same alignment-with-reality contract as `verify_doc_claims` for docs.

**Collaboration shape:** Rigby surfaced a real blocker (6 missing PA tools to do the recon herself); Chris instructed *"If Rigby doesn't have tools she needs make notes of them so we can build them later"*; Claude ran SQL via Django ORM as the hybrid X path, Rigby's role contracted to scope-confirmation + create-deliverable. Filed missing-tools list as separate deliverable `13032820-...` with proposed signatures + build order.

**Two mid-session structural drift findings, both surfaced via `feedback_corpus_walks_surface_mechanism_drift.md`** instead of silently bridged:
- `AgentExecution.owner_agent` is empty in ~75% of local rows; had to re-query by `agent.name` FK
- `SpiderContextBuilder.AGENT_SPIDER_MAPPINGS` (in-code) is the actual driver, not `AgentSpiderConnection` (DB) which was assumed to be the source of truth

**Remediation work explicitly deferred per Chris's scope.** 4-item action queue (unify wiring / bridge vocabulary / register missing agents / audit orphan spiders) lives in C deliverable for Session 1188 pickup.

---

## SESSION 1186 CLOSED — PR-C bucket 4 (final celery-task callsites) shipped as PR #2376 + 2 follow-up deliverables filed (2026-06-21)

**1 PR shipped, 3/3 CI green at close.** Closes the FINAL PR-C bucket from `docs/specs/deliverable_creation_paths.md` § Celery tasks. Full handoff: [`SESSION_1186_PR_C_BUCKET_4_CELERY_TASKS.md`](docs/handoffs/SESSION_1186_PR_C_BUCKET_4_CELERY_TASKS.md).

| PR | Commit | Theme |
|---|---|---|
| **#2376** | `00641c70` | `feat(session-1186-pr-c-bucket-4)` — 3 celery task callsites get provenance (A direct synthesis + B/C external receipt via `_create_initiative_external_execution_receipt` helper). +463 LoC, +10 tests. |

**Design call routed through Rigby on pa-10df024c0bd8** (one round-trip): both initiative pipeline tasks already create TWO Deliverables per stage (internal agent save + external task save with different tags/FKs). Threading one execution_id through both would collapse them via the factory's dedupe-by-(parent_object_type, parent_object_id) and silently lose the Initiative-shaped row. Rigby's pick: **B.2 — provenance the EXTERNAL save only via a NEW receipt distinct from the agent's internal execution**. Two follow-ups filed in Local QA (B.1 unify long-term + PR-D 24h watch — see entry block above).

**21 total provenance tests pass** when run alongside the PR-A (#2362) + PR-B (#2364) suites: 4 PR-A + 7 PR-B + 10 bucket-4.

---

## SESSION 1185 CLOSED — 8 PRs shipped (F1+F2 forensic follow-ons + 5 of 6 PR-C sweep buckets) (2026-06-21)

**8 PRs shipped (#2367-#2374), all CI-green at close.** Took both Session 1184 forensic follow-ons (F1 ContentWriterAgent diagnostic_mode + F2 execution_history_tool reverse-link) plus 5 of the 6 PR-C sweep buckets to PR-ready state in a single session. Bucket 4 (3 celery task callsites) deferred to Session 1186 (now closed via PR #2376). Full handoff: [`SESSION_1185_PROVENANCE_CALLER_SWEEP.md`](docs/handoffs/SESSION_1185_PROVENANCE_CALLER_SWEEP.md).

| # | PR | Theme | LoC | Tests |
|---|---|---|---|---|
| 1 | [#2367](https://github.com/clwest/donkey-betz-platform/pull/2367) | F2 execution_history_tool reverse-link to deliverables | +174 | +4 |
| 2 | [#2368](https://github.com/clwest/donkey-betz-platform/pull/2368) | PR-C bucket 1 — 5 mgmt commands opt into synthesis | +109 | +4 |
| 3 | [#2369](https://github.com/clwest/donkey-betz-platform/pull/2369) | F1 ContentWriterAgent `diagnostic_mode` bypass | +290 | +7 |
| 4 | [#2370](https://github.com/clwest/donkey-betz-platform/pull/2370) | PR-C bucket 2 — 4 web views opt into synthesis | +187 | +7 |
| 5 | [#2371](https://github.com/clwest/donkey-betz-platform/pull/2371) | PR-C bucket 3A — 3 service helpers + envelope audit | +178 | +6 |
| 6 | [#2372](https://github.com/clwest/donkey-betz-platform/pull/2372) | PR-C bucket 3B-1 — conversation pipelines thread orchestration AgentExecution | +387 | +6 |
| 7 | [#2373](https://github.com/clwest/donkey-betz-platform/pull/2373) | PR-C bucket 3B-2 — per-stage AgentExecution rows in workspace pipeline runner | +283 | +5 |
| 8 | [#2374](https://github.com/clwest/donkey-betz-platform/pull/2374) | PR-C bucket 5 — competitor_comparison_tool opt-in + append_service audit | +128 | +4 |

**Structural finding in bucket 3B-1**: 2 conversation pipelines were silently in legacy_no_provenance bucket (set `Deliverable.parent_object_type='conversation'` which read helper didn't recognize). Grep confirmed zero downstream readers — risk-free flip. Now uses Session 843 `AgentExecution(parent_object_type='conversation')` pattern as intermediate hop.

---

## SESSION 1184 CLOSED — Deliverable → Execution provenance (3 PRs merged) + Section 6 forensic verification + 4 memories + 2 follow-on tickets (2026-06-20/21)

**3 PRs merged + 1 ops finding + 4 new memories + 2 forensic follow-on tickets.** Closes Rigby's deliverable `e4f4e12f` (flipped to `completed` via `content_tool action=content_complete` — see new memory). Full handoffs: [`SESSION_1184_DELIVERABLE_PROVENANCE_LINKAGE.md`](docs/handoffs/SESSION_1184_DELIVERABLE_PROVENANCE_LINKAGE.md) (PR-A) + [`SESSION_1184_PR_B_BASEAGENT_PROVENANCE_WIRING.md`](docs/handoffs/SESSION_1184_PR_B_BASEAGENT_PROVENANCE_WIRING.md) (PR-B).

| PR | Commit | Theme | Verified |
|---|---|---|---|
| **#2362** (PR-A) | `ce5aeb3a` | `feat(session-1184)` — factory synthesizes `AgentExecution` receipt for PA-direct creates; new `build_provenance_block` helper; normalized `provenance` block on `deliverable_tool.detail`; zero schema | 4/4 unit tests + live Rigby invocation on `pa-a60842917d36` shows `origin_execution_id`, `trigger_source=pa_tool`, `synthesized=true`, `legacy_no_provenance=false` |
| **#2364** (PR-B) | `5555b8c6` | `feat(session-1184-pr-b)` — root-cause fix: `base_agent.py:4266` was reading `_current_execution_id` (nothing sets it) instead of `_execution_context['execution_id']` (router writes it). Plus router hoist for workspace path. Plus WARN caller-fingerprint for PR-C triage. Plus §1 enumeration table | 7/7 new tests + 48 deliverable-suite total clean; ~80 BaseAgent agents now wired in one line |
| **#2365** (PR-C) | `2903f5e2` | `fix(session-1184)` — ContentWriterAgent `content_type` alias normalizer (14 misnomers) + PA tool schema enum constraint. Unblocked Rigby's forensic validation run that died on `Unknown content type: deliverable` | 5/5 unit tests + live Rigby re-dispatch on `pa-10df024c0bd8` post-merge succeeded |

**Section 6 forensic validation (Rigby, post-merge on `pa-10df024c0bd8`):** Steps A, B, C, G all PASS — provenance mechanism firing live in production traffic. Step D + Step F FAIL — filed as F1 + F2 follow-on deliverables (see Session 1184 forensic follow-ons table above). Forensic report deliverable: `cee21256-576a-443c-a614-a2d697fe6aa1`.

**Per Rigby's design Qs (all ratified):** reuse Session 843 fields not new schema (Q1A) / synthesize AgentExecution for PA-direct (Q2A) / derive tool_calls via trace_id pivot — no new FK (Q3C) / soft-enforce now, hard-required later (Q4C) / read-via-tool sufficient — UI optional (Q5).

**Deliverable e4f4e12f status:** flipped to `completed` via `content_tool action=content_complete` (NOT `deliverable_tool action=update` — see [`feedback_deliverable_status_via_content_complete.md`](../../../.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_deliverable_status_via_content_complete.md)). Closing note appended via `action=append` (2295 chars) with PR links + AC table + Phase 3 (PR-C/D) follow-ons.

**Bonus debug — PA worker FC env regression:** manual PA worker restart without `PA_USE_FUNCTION_CALLING=true` env caused 30-min "Rigby refusal loop" mid-session. `make celery` sets the var; ad-hoc `nohup celery ...` does not. Without it, source=claude-code messages fall through keyword routing with no `claude_code_coordination` branch → no tools dispatched → text-only refusals. Saved as [`feedback_pa_worker_function_calling_env.md`](../../../.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_pa_worker_function_calling_env.md); `tools/pa_local.sh` doc-block warns future-me; READ THIS FIFTH section above flags it at session open.

**New memories (3):**
- `feedback_pa_worker_function_calling_env.md` — manual restart needs `PA_USE_FUNCTION_CALLING=true`
- `feedback_deliverable_status_via_content_complete.md` — status transitions use `content_tool` not `deliverable_tool.update`
- (carry from PR description) Caller fingerprint pattern in soft-enforce WARNs for fast sweep triage

---

## SESSION 1183 CLOSED — Celery beat ownership doc fix breaks CI bypass cycle + worker restart unblocks PR #2357 (2026-06-20)

**1 docs PR shipped (CI green without `--admin` bypass).** Full handoff: [`docs/handoffs/SESSION_1183_CELERY_BEAT_OWNERSHIP_AND_WORKER_RESTART.md`](docs/handoffs/SESSION_1183_CELERY_BEAT_OWNERSHIP_AND_WORKER_RESTART.md).

| PR | Theme | SHA | Verified |
|---|---|---|---|
| **#2359** | `docs(session-1183)` — reframe Celery beat schedule as split-owned to clear context-kit CONFLICT | _(pending squash-merge)_ | `context-kit verify` VERIFIED; CI Repo Guardrails PASS 1m5s; **no `--admin` bypass** (first such PR since Session 1180) |

Two surgical edits to `docs/ARCHITECTURE.md:680` and `docs/topics/active-module-ownership-map.md:242` removed the verifier's `doc_exclusive_celery_claim` trigger words ("only" near "celery.py") and positively asserted the four-source split-ownership model the verifier already supports (primary static / runtime store / bridge / routing-config). ~24 lines, single-revert safe.

**Worker restart ops cleanup:** PR #2357 (Session 1182 server-side persist fix) merged at 21:07 local AFTER workers had been restarted at 20:42 — running workers were on pre-fix code via `sys.modules` cache. Standard `pkill -9 -f celery; rm -f .celery*.pid; make celery` performed; 4 nodes back via inspect ping; baseline clean (0 fail-opens since restart). **Tomorrow's 24h watch is the first that actually tests PR #2357.**

**Known issue carried into Session 1184:** Platform inventory stale (`d3493510` vs current HEAD) → 2 high drifts on `load_all_agents_advisors.py` (Agent table 155 → 84 rows from Sessions 1166-1170 agent dim restructure). CI carves this out via `--inventory-advisory`. Worth a dedicated inventory-refresh PR — see Session 1184 first 10-minute item.

---

## SESSION 1182 CLOSED — 24h-watch finding → server-side persist user attribution fix (2026-06-20)

**1 PR merged.** Full handoff: [`docs/handoffs/SESSION_1182_SERVER_PERSIST_USER_ID.md`](docs/handoffs/SESSION_1182_SERVER_PERSIST_USER_ID.md).

| PR | Theme | SHA | Verified |
|---|---|---|---|
| **#2357** | `fix(session-1182-server-persist)` — resolve user attribution in fire helper + tighten `create_completion_row` contract | `51fdfe55` | 18/18 tests green; chat_conversations row 661 proves consumer-side fallback was carrying the path pre-fix |

24h watch surfaced a real regression in PR #2352's server-side persist path: `IntegrityError: null user_id` on PA-originated ImageAgent dispatches → fail-open silently swallowed it. UX wasn't broken (consumer-side safety net wrote the row), but the architectural intent of PR #2352 ("decouple completion persistence from WS consumer") was half-broken.

Fix: 3-part patch — `_resolve_completion_user` helper (execution.user → conv-owner lookup → fail-closed), distinct `persist_skipped_missing_user` log key (not mislabeled fail-open), `AnonymousCompletionRowError(ValueError)` raised early in `create_completion_row` instead of silent None fallback. No migration. Single-revert safe.

**New behavioral invariant:** Server-side persistence is fail-closed when ownership can't be resolved; WS consumer still persists for live sockets. The "no consumer + missing attribution" case is explicitly logged via `persist_skipped_missing_user` and skipped.

**Known issue carried into Session 1183:** Pre-existing `Repo Guardrails` CI failure (`Celery beat schedule ownership` CONFLICT) — NOT caused by #2357, present on main since at least Session 1181. Merge required `--admin` bypass. Triage as Session 1183 first 10-minute item.

---

## SESSION 1181 CLOSED — Phase 3 queue drained: artifact_pointers extractor + banner queue (2026-06-20)

**2 PRs merged.** Full handoff: [`docs/handoffs/SESSION_1181_PHASE3_BANNER_QUEUE_AND_ARTIFACTS.md`](docs/handoffs/SESSION_1181_PHASE3_BANNER_QUEUE_AND_ARTIFACTS.md).

| PR | Theme | SHA | Verified live |
|---|---|---|---|
| **#2354** | `fix(session-1181-agent-wake)` — populate `artifact_pointers` in fire helper from `execution.output_data` | `f2eeadfc` | ImageAgent dispatch → `media_ids` populated end-to-end in result_payload + chat_conversations + bubble text |
| **#2355** | `fix(session-1181-agent-wake)` — banner queue for multi-agent fanout (replaces single slot) | `5eb05dde` | 2x ImageAgent in one Rigby turn → 2 stacked toasts in browser ("yes saw both stacked") |

Both PRs are downstream applications of the lifecycle-bound contract from Session 1180. No new architectural decisions, no migrations, both revert-safe.

**Phase 3 queue post-Session-1181:** only Finding #4 (threaded-revoke limitation) remains. Deferred until pain.

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
