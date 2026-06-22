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


## SESSION 1202 — CURRENT ENTRY POINT

### SESSION 1201 CLOSED — Platform Connectivity Reality Map recon: 16 rows + 4 child Initiatives + completion roadmap (2026-06-22)

Full handoff: [`SESSION_1201_CONNECTIVITY_RECON_16_ROWS.md`](docs/handoffs/SESSION_1201_CONNECTIVITY_RECON_16_ROWS.md). **0 PRs merged** (recon-only session). **1 parent Initiative + 4 child Initiatives + 15 deliverables** created in DBZ; all bidirectionally linked. **Completion roadmap shipped:** [`docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md`](docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md) — sequences 6-8 sessions of fix work.

| Initiative | UUID | Kind | Holds |
|---|---|---|---|
| **Platform Connectivity Reality Map** (parent) | `0ecd1bc2-9931-4464-8efa-495a28b58779` | investigation | 16-row drift map; spawned_from Spine 1 |
| Producer Reroute Completion | `05931145-89d2-4923-946e-676e0db44e91` | project | 3 leak-site patches (agent_router, SKIN helper, activate_workspace) |
| Initiative-Management Tool Surface Gaps | `f4cfe31e-366b-4d5e-802c-041ba66c7afb` | project | `work_tool.initiative_update` + `work_tool.initiative_link` |
| Docs ↔ Runtime Alignment Layer | `1859dd51-ce3b-4689-bd4b-42d9de5793d8` | recurring_artifact | Close-session manifest + orient enhancement |
| Diagnostic Telemetry Tool Surface Gaps | `50b7adf2-ec1c-4ef0-8245-ec026cff114f` | project | 7 missing diagnostic PA tool actions |

**Net result:** Chris's question "are agents + tools + learning + spiders + body systems actually wired together?" produced a 16-row drift map. Major findings: (1) Producer reroute Session 1199 fix was partial — 3 callsites still leak; (2) 67% of all Initiatives (31/46) have NULL `target_workspace_id`; (3) Initiative pipeline Stage 1 auto-research is broken since ≥2026-06-14 — every spawn BLOCKS on irrelevant SEC/Kaggle evidence; (4) Tool-surface gaps are 2-class (initiative-management + diagnostic-telemetry); (5) `108 vs 173` schema/handler framing in PLATFORM_INVENTORY creates false drift signal. All fix arcs sequenced in the roadmap.

### FIRST THING Session 1202

**Daily inference accuracy watch Day-1 (2026-06-23 — independent of Reality Map work).** Append A/B/C/D + `report_initiative_kinds` to deliverable `9ba58690-…` (DBZ workspace, linked to SPINE_1) per the runbook protocol at `cb9d8ae1-…`.

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

`pa-1ccc494ea00b4e77` — continued across Sessions 1200 + 1201 (titled "Session 1200 — Watch Tracking + Phase 2 Gate (Plan C)"; can stay on this thread for Session 1202 or spin fresh — your call). `tools/pa_local.sh` is already pinned. Prior thread `pa-ea12236c83eb4826` (Sessions 1197+1198+1199) is retired.

**Donkey Betz workspace_id (pin):** `b4503364-2573-4401-9e28-61a739e0ce50` — **46 Initiatives total** post-Session 1201 (was 42; +4 Reality Map children created), **15 in DBZ workspace** (was 11), kind dist: project=8 / recurring_artifact=4 / investigation=3 / spec_backlog=1. **2 AgentInitiativeAffinity rows** (unchanged). **31 Initiatives still have NULL `target_workspace_id`** — backfill scheduled in roadmap §Phase B.3.

**3 spine Initiatives — persisted + bound to Donkey Betz (still ACTIVE, kind=project):**

| # | Name | UUID |
|---|---|---|
| 1 | Initiatives-First Wiring + No-Orphan Output | `6941372d-b13c-4631-91c8-749fa65c55a0` |
| 2 | Agent Capability Map + Router Contracts | `2071a9c6-986f-4528-be90-8cccaa595f1e` |
| 3 | Tool Migration Hardening (web_search → intelligence_tool) + Failure Fix | `7e23d621-4d0c-409a-a680-4fd2e015d04b` |

All 3 still BLOCKED at Stage 1 (irrelevant SEC/Kaggle evidence packs). **Spine 1 now has `spawns` → Reality Map `0ecd1bc2-…` linkage** (Reality Map is connectivity validation of Spine 1's scope). Spine progression unblocked by roadmap §Phase B.2 (auto-research evidence supplier fix).

### Pick this session

| Item | Priority | Where it's defined |
|---|---|---|
| **Daily watch appends (inference accuracy + default-only-projects)** | **P1 (daily, active 2026-06-23)** | Append A/B/C/D + `report_initiative_kinds` to deliverable `9ba58690-…`. Protocol: runbook `cb9d8ae1-…`. |
| **Connectivity Roadmap Phase A.1 — `work_tool.initiative_update` + `initiative_link`** | **P1 (Reality Map fix arc)** | Unblocks operator from Claude ORM bypass. Initiative `f4cfe31e-…`. Spec: `docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md` §A.1 |
| **Connectivity Roadmap Phase A.2 — 7 `diagnostics_tool` actions** | **P1 (Reality Map fix arc)** | Unblocks 6 of 8 telemetry-blocked rows. Initiative `50b7adf2-…`. Roadmap §A.2 |
| **Day-8 watch aggregation + decision (2026-06-30)** | **P1 (time-gated)** | Per-seed: keep / tighten / pull. File decision as deliverable tagged `session-1198-watch-result`. |
| **Plan C Phase 2 hard-reject flip (2026-06-29 gate)** | **P1 (time-gated)** | After 7-day watch is clean, replace Phase 1 diagnostic mark with `OrphanDeliverableError`. Spec: `INITIATIVES_FIRST_BACKBONE.md` §6.1. |
| **Session 1196 7-day watch (2026-06-29)** | **P1 (time-gated)** | Re-run `backfill_initiative_workspace_links --json-only`; diff against 2026-06-22 baseline. |
| **Connectivity Roadmap Phase B.1 — Producer Reroute Completion (3 PRs)** | P2 | Initiative `05931145-…`. Roadmap §B.1 |
| **Connectivity Roadmap Phase B.2 — Auto-research evidence supplier fix** | P2 | Roadmap §B.2 (unblocks 3 spine Initiatives) |
| **Connectivity Roadmap Phase B.3 — NULL-workspace Initiative backfill (mgmt cmd)** | P2 | Roadmap §B.3 (one-shot data fix for 31 Initiatives) |
| **Connectivity Roadmap Phase C — Structural fixes (close-session manifest + orient enhancement)** | P3 | Initiative `1859dd51-…`. Roadmap §C |
| **PR3 — Step 4 heuristics implementation** | P2 | After Day 8 watch decision (≥80% precision on Step 3 → unblock PR3). |
| **Production rollout: Session 1196-1200 cumulative** | **P0 (carryover, gated)** | Operator's go signal needed. Local-only until then. |

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
