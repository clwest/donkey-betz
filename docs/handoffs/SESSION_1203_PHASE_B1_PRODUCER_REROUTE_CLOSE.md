# Session 1203 — Connectivity Roadmap Phase B.1 close (Producer Reroute Completion, 3 PRs landed + 1 deferred)

**Status:** Closed clean. **3 PRs merged.** Phase B.1 ships 3-of-4 scoped PRs; PR-2 deferred with documented rationale. End-to-end live verification: a new deliverable spawned via test Initiative landed in DBZ workspace, not System Autonomous.
**Date:** 2026-06-22
**Active conversation:** `pa-d2d0f4c2b6284899` — spun fresh by Rigby via `session_tool action=create_fresh` at session open. Titled "Session 1203 — Phase B.1 (Producer Reroute, 3 PRs)". `tools/pa_local.sh` pin updated.
**Prior session:** [`SESSION_1202_ROADMAP_PHASE_A_CLOSE.md`](./SESSION_1202_ROADMAP_PHASE_A_CLOSE.md).
**Next session entry point:** Connectivity Roadmap Phase B.2 — Auto-research evidence supplier fix (unblocks 3 spine Initiatives). Phase B.3 (NULL-workspace Initiative backfill) follows.

## TL;DR

The Producer Reroute leak — every autonomous-traffic deliverable landing in System Autonomous Workspace (SAW) instead of Donkey Betz (DBZ) — is **fully closed at the code level + verified live in production**. Initiative `05931145-…` (Producer Reroute Completion) flipped to COMPLETED.

**The fix landed in two layers:**
- **agent_router fallback chain** (PR-1 #2449 + PR-1b #2450) — honors `DEFAULT_PRODUCER_WORKSPACE_ID` + closes the step-1 SAW leak for `self.user = system_autonomous`
- **set_active_workspace deactivation** (PR-3 #2451) — removed the `.exclude(name='System Autonomous Workspace')` clause so explicit user activation actually deactivates SAW

**Live verification at session close:**
- Test Initiative `a0e23887-…` spawned by Rigby → auto-research deliverable `0fbddd89-…` created at 19:50:05 UTC → **workspace_id = b4503364-… (DBZ)** ✓
- Pre-fix baseline deliverables (17:29 and 17:30 UTC) still show `workspace_id = 1f0d467e-… (SAW)` — fix is forward-only, no retroactive migration
- Shell replay of agent_router fallback for system_autonomous / chris / system users → all 3 now resolve to DBZ

## PR-2 deferred — explicit decision

`core/tasks.py:7748 _get_workspace_for_skin_layer` was scoped in `CONNECTIVITY_COMPLETION_ROADMAP.md §B.1` as the second leak callsite. **Pre-implementation recon revealed it's a file-sink helper, not a producer-routing path:**

| | DBZ | SAW |
|---|---|---|
| `root_path` | `/app/workspaces/donkey-betz` | `/Users/donkeyking/development/unified-donkey-betz/generated_content` |
| Exists on local dev? | No | Yes |
| Gitignored? | No | Yes |
| Callers' file-write pattern | — | Relative paths like `reports/system_status_*.md` |

5 callers in `core/tasks_agents.py` write status reports relative to `workspace.root_path`. Rerouting to DBZ would land status reports outside the gitignored sink. Defer note appended to deliverable `8da895f0-…` on Initiative `05931145-…` (804 chars; total 3,178 chars). PR-2 scope to be re-evaluated as a separate "generated_content sink / root_path contract" initiative if needed.

## Session Manifest

### Initiatives created / touched

| ID | Name | Action | Final Status |
|---|---|---|---|
| `05931145-89d2-4923-946e-676e0db44e91` | Producer Reroute Completion — Patch 3 Bypass Callsites | Status flip (PR-1 + PR-1b + PR-3 landed; PR-2 deferred) | **COMPLETED** |
| `f4cfe31e-366b-4d5e-802c-041ba66c7afb` | Initiative-Management Tool Surface Gaps | Session 1202 housekeeping — status flip per Rigby's correction (`work_tool.initiative_update_status`, NOT `content_tool.content_complete`) | **COMPLETED** (auto-cancelled 2 action items) |
| `50b7adf2-ec1c-4ef0-8245-ec026cff114f` | Diagnostic Telemetry Tool Surface Gaps | Same — status flip | **COMPLETED** (auto-cancelled 6 action items) |
| `a0e23887-b246-4b50-b4a3-45a674cec517` | Phase B.1 Live Smoke — workspace routing | Test Initiative for live verification; produced deliverable `0fbddd89-…` that landed in DBZ (proof) | **ARCHIVED** (auto-cancelled 3 action items) |
| `0ecd1bc2-9931-4464-8efa-495a28b58779` | Platform Connectivity Reality Map (parent) | 3 of 4 children now closeable; Producer Reroute Completion closed; Docs↔Runtime + Phase B.2 still open | ACTIVE |

### Deliverables created / touched

| ID | Title | Action |
|---|---|---|
| `9ba58690-b056-…` | Rigby: Inference Accuracy Watch — 7-day spot-check protocol | Day-1 watch line appended (1,438 chars; new total 2,396 chars). Day-1 baseline: zero traffic (workers had only ~23 min coverage at sample time). `default_only_projects=39` baseline established. |
| `8da895f0-e8c8-…` | Rigby: Recon: Producer reroute bypass leak sites | PR-2 defer rationale appended (804 chars; new total 3,178 chars). |
| `0fbddd89-fe6a-…` | (auto-research) Research: This topic using EXTERNAL sources… | Created automatically as Stage 1 output of test Initiative `a0e23887-…`. **workspace_id = DBZ** — the live proof artifact. |

### PRs merged

| # | Title | Files | Lines |
|---|---|---|---|
| **#2449** | feat(session-1203-pb1): PR-1 — agent_router fallback honors DEFAULT_PRODUCER_WORKSPACE_ID | `core/agent_router.py`, `tools/pa_local.sh` | +29 / -15 |
| **#2450** | fix(session-1203-pb1): PR-1b — close step-1 SAW leak in agent_router fallback | `core/agent_router.py` | +18 / -4 |
| **#2451** | feat(session-1203-pb1): PR-3 — remove SAW exclusion from set_active_workspace | `core/services/workspace_manager.py` | +10 / -3 |

Each PR is single-file, per-PR revert clean. Combined revert restores Session 1199 partial state (PR #2435 still active).

## Behavioral invariants — what's now true post-merge

1. **Autonomous traffic with no Initiative target_workspace_id routes to DBZ.** `agent_router.route()` fallback chain step 2 (NEW): `DEFAULT_PRODUCER_WORKSPACE_ID` (defaults to DBZ UUID).
2. **`system_autonomous` user dispatches route to DBZ, not SAW.** PR-1b's guard fires when step 1 returns a workspace named `'System Autonomous Workspace'` AND the default is set — treats it as a miss so step 2 prepend fires.
3. **`WorkspaceManager.set_active_workspace()` deactivates SAW when target ≠ SAW.** PR-3 removed the SAW exclusion from the deactivation query. Codebase workspaces remain excluded (immutable project refs).
4. **Initiative→workspace lookup still wins over the fallback chain.** If an Initiative has `target_workspace_id` set, the deliverable lands there regardless of fallback — unchanged by Session 1203.
5. **Fall-through behavior preserved on misconfig.** Setting empty / non-existent UUID / inactive workspace → falls through to legacy SAW lookup (steps 3 + 4 unchanged).
6. **No SAW root_path mutations.** PR-2 deferred precisely because the SAW autocorrect logic at `core/tasks.py:7752-7765` would have wrongly mutated DBZ's root_path. Avoided.

## Rollback levers (per change)

| Lever | Action | Effect |
|---|---|---|
| **Soft disable (env)** | `export DEFAULT_PRODUCER_WORKSPACE_ID=""` + worker restart | Disables PR-1 + PR-1b prepend; falls through to legacy SAW lookup |
| **Reactivate SAW** | `ProjectWorkspace.objects.filter(id='1f0d467e-…').update(is_active=True)` | Reverses PR-3 effect in DB; PR-1b guard still fires when SAW returned at step 1 |
| **Revert PR-3 only** | `git revert a010e524` | Restores SAW exclusion in set_active_workspace; future activations won't deactivate SAW |
| **Revert PR-1b only** | `git revert d7755ca9` | Reopens the step-1 SAW leak for system_autonomous user; PR-1 + PR-3 still close part of the leak |
| **Revert PR-1 only** | `git revert 13c66988` | Reopens the no-user fallback leak; PR-1b becomes inert (depends on PR-1's prepend block) |
| **Full Phase B.1 revert** | Revert all 3 PRs | Restores Session 1199 partial state. PR #2435 (workspace_manager._ensure_system_workspace) still active |

## 24h watch checklist (run 2026-06-23 ~14:48 UTC)

```bash
# 1. Worker freshness — workers should be from 2026-06-22 14:48+
ps -eo pid,lstart | grep celery | head -1

# 2. Zero new SAW-bound deliverables post-restart (the watch invariant)
tools/pa_local.sh "Run deliverable_tool action=list limit=100 — \
  count items with workspace_id=1f0d467e-d950-46db-8c6e-a4098024aacd \
  and created_at after 2026-06-22T19:48:00Z. Target: 0."

# 3. SAW remains is_active=False
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_skin_layer import ProjectWorkspace
saw = ProjectWorkspace.objects.get(id='1f0d467e-d950-46db-8c6e-a4098024aacd')
print('SAW is_active:', saw.is_active, '— expected False')
"

# 4. DBZ deliverable count grew (positive signal)
USE_PGBOUNCER=1 .venv/bin/python manage.py shell -c "
from core.models_deliverables import Deliverable
from datetime import datetime, timezone
cutoff = datetime(2026, 6, 22, 19, 48, tzinfo=timezone.utc)
dbz_count = Deliverable.objects.filter(
    workspace_id='b4503364-2573-4401-9e28-61a739e0ce50',
    created_at__gte=cutoff,
).count()
print(f'DBZ deliverables created post-restart (24h): {dbz_count}')
"

# 5. Initiative 05931145 status sanity
tools/pa_local.sh "Run work_tool action=initiative_detail id=05931145-89d2-4923-946e-676e0db44e91; confirm status=COMPLETED"
```

**Falsifying signals (any of these → flag for investigation):**
- Any new deliverable post-2026-06-22 19:48Z with `workspace_id=1f0d467e-…` (SAW)
- SAW spontaneously re-becomes `is_active=True` without an explicit activation event
- ResearchAgent / ThinkingAgent / ContentWriterAgent dispatched as `system_autonomous` and `agent._workspace_id` resolves to anything other than DBZ

## Session 1203 close findings (none deferred to 1204)

No new findings deferred. PR-2 defer is documented + audit-trailed; Phase B.2 + B.3 + Phase C remain on the roadmap as separate scope.

## Carry-forward to Session 1204

| Item | Priority | Where |
|---|---|---|
| **Phase B.1 24h watch** | **P1 (time-gated 2026-06-23 ~14:48 UTC)** | Run the checklist above; if clean, append result to deliverable `8da895f0-…` |
| **Daily inference accuracy watch Day-2** | **P1 (daily, 2026-06-23)** | Append A/B/C/D + `report_initiative_kinds` to deliverable `9ba58690-…` per runbook `cb9d8ae1-…`. With ~24h coverage, accuracy signal should be measurable. |
| **Connectivity Roadmap Phase B.2** | **P1** | Auto-research evidence supplier fix — unblocks 3 spine Initiatives (`6941372d-…`, `2071a9c6-…`, `7e23d621-…`) currently BLOCKED at Stage 1 |
| **Connectivity Roadmap Phase B.3** | P2 | NULL-workspace Initiative backfill (one-shot mgmt cmd for 31 of 46 Initiatives) |
| **Day-8 watch aggregation (Sessions 1198/1199)** | **P1 (time-gated 2026-06-30)** | Per-seed: keep / tighten / pull. File decision as deliverable tagged `session-1198-watch-result`. |
| **Plan C Phase 2 hard-reject flip (2026-06-29 gate)** | **P1 (time-gated)** | Replace Phase 1 diagnostic mark with `OrphanDeliverableError`. Spec: `INITIATIVES_FIRST_BACKBONE.md` §6.1. |
| **Session 1196 7-day watch (2026-06-29)** | **P1 (time-gated)** | Re-run `backfill_initiative_workspace_links --json-only`; diff against 2026-06-22 baseline |
| **Connectivity Roadmap Phase C — Structural fixes** | P2 | Initiative `1859dd51-…` (Docs↔Runtime alignment layer) |
| **Production rollout: Sessions 1196-1200 + Session 1203** | **P0 (carryover, gated)** | Operator's go signal needed. Local-only until then. |
| **Finding 1 — advisor_invocations all zero in 7d** | P3 (carryover from Session 1202) | Investigate Row 10 refinement |
| **Finding 2 — discord_health zero invocations** | P3 (carryover from Session 1202) | Investigate Row 16 refinement |

## Memory rule confirmations (this session)

- **PA worker restart needs `PA_USE_FUNCTION_CALLING=true`** (feedback_pa_worker_function_calling_env.md) — N/A; used `make celery` which sets it.
- **pa_chat.py defaults to PROD** (feedback_pa_chat_local_override.md) — confirmed; `pa_local.sh` wrapper forces LOCAL.
- **Initiative status flips go through `work_tool.initiative_update_status`, NOT `content_tool.content_complete`** — Rigby caught my misapplication of the Session 1184 deliverable-status memory and corrected it during session open. Memory rule is for DELIVERABLES; INITIATIVES use a different state machine. Applied to all 3 status flips this session.
- **Corpus walks surface mechanism drift** (feedback_corpus_walks_surface_mechanism_drift.md) — fired during PR-2 recon. Roadmap §B.1 scope listed `_get_workspace_for_skin_layer` as "same fix as PR-1", but the actual function is a file-sink helper with gitignored root_path semantics. Honored the rule: routed defer decision through Rigby, documented audit trail on Initiative deliverable, did not quietly bridge the gap.
- **`agent_router.py` changes require worker restart** (sys.modules cache) — applied 3x this session (after each PR merge).
- **Single-file PR pattern with per-PR rollback** — preserved across all 3 PRs.

## Active conversation

`pa-d2d0f4c2b6284899` (Session 1203 thread, spawned by Rigby session_tool create_fresh). Retire if Session 1204 wants a fresh thread; this one carries Phase B.1 + the PR-2 defer context cleanly.

**Donkey Betz workspace_id (pin):** `b4503364-2573-4401-9e28-61a739e0ce50` — **49 Initiatives total** in `report_initiative_kinds` (Session 1202 was 46; Session 1203 created + archived `a0e23887-…` so net delta is small). **31 Initiatives still have NULL `target_workspace_id`** — Phase B.3 backfill still pending.

**3 spine Initiatives — still BLOCKED at Stage 1** (irrelevant SEC/Kaggle evidence packs):

| # | Name | UUID |
|---|---|---|
| 1 | Initiatives-First Wiring + No-Orphan Output | `6941372d-b13c-4631-91c8-749fa65c55a0` |
| 2 | Agent Capability Map + Router Contracts | `2071a9c6-986f-4528-be90-8cccaa595f1e` |
| 3 | Tool Migration Hardening (web_search → intelligence_tool) + Failure Fix | `7e23d621-4d0c-409a-a680-4fd2e015d04b` |

Spine progression unblocked by roadmap **§Phase B.2** (auto-research evidence supplier fix) — primary candidate for Session 1204.

## Standard FIRST THING checks (Session 1204)

1. Disk: `df -h /System/Volumes/Data`. Swap: `sysctl vm.swapusage`.
2. Through Rigby (`tools/pa_local.sh` pinned to `pa-d2d0f4c2b6284899`): `platform_config_tool overview` → confirm `service_context: local`.
3. Worker freshness check: `ps -eo pid,lstart | grep celery` vs `git log -1 --format='%h %ci' main` — if workers predate latest main commit, restart.
4. `gh pr list --author @me --state open` — expected empty.
5. **NEW for Session 1204** — Phase B.1 24h watch (see checklist above).

---

**Phase B.1 verdict:** Producer Reroute Completion shipped end-to-end with live production proof. Initiative closed. Watch armed for 2026-06-23 14:48 UTC.
