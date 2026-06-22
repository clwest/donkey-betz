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

## SESSION 1198 — CURRENT ENTRY POINT

### SESSION 1197 CLOSED — Initiative kind enum + Projects-in-Workspace layer: 7 PRs landed (2026-06-22)

Full handoff: [`SESSION_1197_INITIATIVE_KIND_CLASSIFICATION.md`](docs/handoffs/SESSION_1197_INITIATIVE_KIND_CLASSIFICATION.md). **7 PRs opened against `main`** (all retargeted directly — no stacking footgun). Reviving the Session 1193 cluster-recon insight that had been parked DEFERRED-pending-backbone (backbone shipped Sessions 1194-1196).

| PR | Theme |
|---|---|
| **#2416** | Migration 0362 — `Initiative.kind` enum (4 choices, default=project, db_indexed) + `related_initiatives` JSONField (default=list) |
| **#2417** | `apply_initiative_kind_classification` mgmt cmd — 11-row SPEC, idempotent `--dry-run` / `--apply`, two-pass split-pair linker |
| **#2418** | `report_initiative_kinds` mgmt cmd — cross-tab + heuristic flags |
| **#2419** | §6.4 added to `INITIATIVES_FIRST_BACKBONE.md` + AC11-14 + provenance |
| **#2420** | 14-case regression suite |
| **#2421** | `docs/INDEX.md` rebuild |
| **#2422** | Close-out additions: idempotency rule + "safe placeholder" sentence + `default_only_projects` detector + AC15 + test #15 |

**Net result:** 11 Initiative rows in Donkey Betz workspace carry intentional `kind` classification (5 project / 3 recurring_artifact / 2 investigation / 1 spec_backlog). Status remains lifecycle axis; kind names the work shape. Status orthogonality preserved — apply cmd does NOT touch status on existing rows.

### FIRST THING Session 1198

**Merge the 7 PRs.** All target `main` directly. Earliest-first (#2416 → ... → #2422) is cleanest but no PR hard-depends on a prior merge — each rebases cleanly. Then re-run the local verification commands to confirm idempotency post-merge:

```bash
# Step 1 — confirm migration applied + kind field present
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
django.setup()
from core.models_document_registry import Initiative
print('Kind choices:', [c[0] for c in Initiative.Kind.choices])
"

# Step 2 — confirm 11-row classification still in place (re-apply should be no-op)
python manage.py apply_initiative_kind_classification --apply --workspace-id b4503364-2573-4401-9e28-61a739e0ce50

# Step 3 — confirm default-only detector signals the 3 spine Initiatives (real long-arc projects, kind=project is correct)
python manage.py report_initiative_kinds --workspace-id b4503364-2573-4401-9e28-61a739e0ce50 --json-only | jq '.default_only_projects'
```

Production rollout (if/when Chris flips local-only off): same playbook — apply cmd is idempotent + safe to run; no worker restart needed (no new `@shared_task` in this session).

### 24h watch — starts 2026-06-23 (NEW, time-gated)

Re-run `report_initiative_kinds --workspace-id <DBZ>` daily for 1 week. Confirm `default_only_projects` count stays bounded — if new project rows appear that weren't in the SPEC, that's a callsite filing project Initiatives without classification → candidate for enforcement Phase 2.

### Active conversation

`pa-ea12236c83eb4826` (Session 1197 close). Rigby will likely recommend spinning fresh given Session 1198's focus is on watches + Phase 2 design + carryover.

**Donkey Betz workspace_id (pin):** `b4503364-2573-4401-9e28-61a739e0ce50` — **42 Initiatives total** (was 34 — added 8 via Session 1197 SPEC), 11 in DBZ workspace, kind dist: project=5 / recurring_artifact=3 / investigation=2 / spec_backlog=1.

**3 spine Initiatives — persisted + bound to Donkey Betz (still ACTIVE, kind=project):**

| # | Name | UUID |
|---|---|---|
| 1 | Initiatives-First Wiring + No-Orphan Output | `6941372d-b13c-4631-91c8-749fa65c55a0` |
| 2 | Agent Capability Map + Router Contracts | `2071a9c6-986f-4528-be90-8cccaa595f1e` |
| 3 | Tool Migration Hardening (web_search → intelligence_tool) + Failure Fix | `7e23d621-4d0c-409a-a680-4fd2e015d04b` |

All 3 still BLOCKED at Stage 1 (irrelevant SEC/Kaggle evidence packs). Stage progression is a separate workstream.

### Pick this session

| Item | Priority | Where it's defined |
|---|---|---|
| **Merge Session 1197 PRs + verify** | **P0** | 7 PRs at #2416-#2422. All on `main`. Verification commands in FIRST THING above. |
| **Production rollout: Session 1196 `backfill_initiative_workspace_links --apply`** | **P0 (carryover)** | Operator runs in prod + restarts celery workers. Locks production baseline matching local. Playbook in [`SESSION_1196_INITIATIVE_DIAGNOSTIC_CONTRACT.md`](docs/handoffs/SESSION_1196_INITIATIVE_DIAGNOSTIC_CONTRACT.md) §"Production rollout playbook". |
| **Plan C 7-day watch + Phase 2 hard-reject decision** | **P1 (time-gated)** | Start **2026-06-29**. Re-run `backfill_deliverable_initiative_links --workspace-id b4503364-… --json-only`; diff totals against the 2026-06-22 baseline. If missing-initiative count trends down + sweep archive rate matches create rate → flip Phase 2 hard-reject (`OrphanDeliverableError` on `initiative_id=None`). Spec: `INITIATIVES_FIRST_BACKBONE.md` §6.1. |
| **Session 1196 7-day watch** | **P1 (time-gated)** | Start **2026-06-29**. Re-run `backfill_initiative_workspace_links --json-only` and diff against 2026-06-22 baseline. Confirm archived count up, candidate_for_flag at 0, already_diagnostic decreasing for non-terminal rows. |
| **Session 1197 `default_only_projects` 24h watch** | **P1 (time-gated, NEW)** | Start **2026-06-23**. Daily `report_initiative_kinds` re-run; confirm new project Initiatives aren't filed without classification. |
| **§6.2 Phase 2 inference design** | P2 | Rigby's option ranking (least-risk first): (1) agent→initiative affinity map; (2) tool-context propagation; (3) heuristics. Top orphan creators give the input list: Rigby=33, ResearchAgent=24, ClaudeCode=11, ContentWriterAgent=9. **Newly informed by Session 1197** — defaults + kind enum give a richer signal shape than pre-1197 design assumed. |
| **`load_all_agents_advisors` baseline fix (155 → 87)** | P2 | Pre-existing `Agents count claims` CONFLICT keeping main's `Repo Guardrails` CI red. Admin-bypass currently required on every PR. Either fix the seed script to actually load all 148 declared agents, OR update the expected baseline to match runtime. |
| **Local test DB infra** | P2 | pgbouncer transaction pool can't proxy `CREATE DATABASE`, blocks `manage.py test` for every `core/tests/*` file. Re-surfaced again in Session 1197 PRs #2420 + #2422. Add `DJANGO_TEST_DATABASE_URL` support, OR document the docker-compose path. |
| **Migration drift audit (Session 1196 parked)** | P2/P3 | Set A: 4 unmigrated Narrative* models in `models_narrative_drift.py`. Set B: 16 AlterField ops on AgentExecution/CuratedSignalEntry/FinalAppliedOverrides/FleetPaChatAuditRow. Session 1197 PR #2416 trimmed these from auto-output — they remain unaddressed. |
| **PA LLM iteration cap silent failure** | P2 | Carryover from Session 1193 (`c2bac9c0-…`). `core/services/unified_pa_entrypoint.py:1298` `max_iterations=8`. |
| **Producer reroute** | P2 | Carryover from Session 1192 (`780a8d15-…`). `_ensure_system_workspace` auto-recreates. |
| **PR-D contract flip** | P2 | Carryover from Session 1194 (`9d9db48a-…`). 24h WARN-volume gate elapsed 2026-06-22. |
| **Workspace UI filter by kind** | P3 | Vertical-slice step 6 from Session 1197 decision card. Parked once kind enum beds in. Touches frontend `WorkspacePageNew.tsx` + adds `?kind=<value>` query param to `work_tool initiative_list`. |

**Pick-this-session items below this line are still-relevant Session 1192/1193 carryover items — same as last session:**

| Item | Priority | Where it's defined |
|---|---|---|
| **Plan C — backfill mgmt command** | _shipped Session 1195 PR #2407_ | `INITIATIVES_FIRST_BACKBONE.md` §3.C.1. |
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

## Historical session blocks

Sessions 1182-1195 close-out blocks lived here through Session 1197. Removed in Session 1198 close to keep this working file lean — full text preserved in `docs/handoffs/SESSION_NNNN_*.md`. The Session 1196 + 1197 closes referenced from this file's body link directly to their handoffs.

Run `ls docs/handoffs/SESSION_*.md | sort -V | tail -20` to see the recent close list.
