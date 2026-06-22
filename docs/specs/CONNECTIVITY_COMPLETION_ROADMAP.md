---
title: "Connectivity Completion Roadmap — sequenced plan to close Reality Map drift"
status: active
session_authored: 1201
generated: 2026-06-22
parent_initiative: 0ecd1bc2-9931-4464-8efa-495a28b58779
companion_docs:
  - INITIATIVES_FIRST_BACKBONE.md
  - ../handoffs/SESSION_1201_CONNECTIVITY_RECON_16_ROWS.md
estimated_sessions: 6-8
---

# Connectivity Completion Roadmap

> Sequencing plan to close the 16-row Reality Map drift surfaced in Session 1201. Holds four child Initiatives' fix scope in dependency order, plus follow-on row cleanup and spine-Initiative unblocking. Goal: every Reality Map row has a terminal classification (flowing / dry+shipped-fix / missing+decision) and zero new System Autonomous leaks within 6-8 sessions.

## Sequencing principles

1. **Unblock auditing first** — diagnostic tools before audit-finding fixes. Otherwise we keep ORM-bypassing the operator surface.
2. **Stop live drift before backlog** — current-production leaks before historical cleanup.
3. **Structural before episodic** — close-session manifest + orient enhancement before content fixes (prevents re-introduction of drift).

## Phase A — Unblock auditing (Sessions 1202-1203)

### A.1 — Initiative-Management Tools (`f4cfe31e-…`)

**Why first.** Operator currently can't bind a workspace to an Initiative or link Initiatives bidirectionally without a Claude ORM bypass. Every new Initiative needs this dance.

**Scope (2 new PA tool actions):**
- `work_tool action=initiative_update` — params: `id`, `target_workspace_id?`, `description?`, `tags?`. Idempotent. Permission-checked.
- `work_tool action=initiative_link` — params: `parent_id`, `child_id`, `relation` (`spawns`|`spawned_from`), `note?`. Writes BOTH sides. Idempotent per `INITIATIVES_FIRST_BACKBONE.md` §6.4 rule.

**AC:**
- Rigby can spawn an Initiative + bind workspace + create bidirectional link without calling Claude
- Re-running update with same value = no-op
- Reject invalid `relation` values with clear error
- `[INITIATIVE-DIAGNOSTIC-CLEARED]` signal still fires on workspace transitions

**Files:**
- `core/services/work_tool.py` (or wherever `work_tool` actions live)
- `core/services/pa_tool_schemas.py` (extend `work_tool` schema entry)
- Tests: `core/tests/test_initiative_management_tools.py`

### A.2 — Diagnostic Telemetry Tools (`50b7adf2-…`)

**Why second.** 6 of 8 Phase 2 rows blocked or partial on missing telemetry surface. Without these, future audits replicate Session 1201's "blocked-by-tooling" pattern.

**Scope (7 new actions, can ship in any order; each is small):**

| Action | Surfaces |
|---|---|
| `diagnostics_tool action=advisor_invocations` | Per-advisor N-day invocation count from AgentExecution log |
| `diagnostics_tool action=schema_handler_diff` | Programmatic version of Session 1201's manual check; flags real gaps vs gateway-pattern-by-design |
| `diagnostics_tool action=learning_bridge_writes` | Per-bridge 30d row count attributable to each signal handler |
| `diagnostics_tool action=provider_calls` | Per-LLM-provider call count over N days |
| `diagnostics_tool action=beat_schedule_health` | Sorted `PeriodicTask` by `last_run_at`, flagged stale + zero-runs (handles pagination) |
| `diagnostics_tool action=workspace_metrics` | Per-workspace last_activity + deliverable_count + is_active + allow_autonomous_writes |
| `diagnostics_tool action=discord_health` | Bot uptime + 7d invocation counts + error rate |

**AC:**
- Each action returns structured JSON (Rigby-consumable)
- No new DB tables — query existing data
- Results paginated where applicable
- All 7 are addable to `pa_tool_schemas.py` so the PA's LLM can invoke them

## Phase B — Stop live drift (Sessions 1203-1204)

### B.1 — Producer Reroute Completion (`05931145-…`)

**Why.** Every new Initiative spawn today leaks auto-research deliverables to System Autonomous Workspace. Observed live mid-session; pattern goes back to at least 2026-06-14.

**Scope (3 PRs):**
1. **PR-1** — `core/agent_router.py:1078-1084`: replace the name-lookup fallback with `DEFAULT_PRODUCER_WORKSPACE_ID` honor (same pattern as Session 1199 PR #2435 applied to `_ensure_system_workspace`)
2. **PR-2** — `core/tasks.py:7748` (`_get_workspace_for_skin_layer`): same fix
3. **PR-3** — `core/services/workspace_manager.py:1906`: either remove System Autonomous exclusion from deactivation, OR make the exclusion conditional on settings flag

**AC:**
- New Initiative spawned via Rigby → deliverable lands in DBZ (not System Autonomous)
- 7-day watch (post-merge): zero new `Research: This topic using EXTERNAL sources...` deliverables in System Autonomous Workspace
- Existing System Autonomous deliverables stay put — no destructive migration

**Rollback:** Each PR is single-file. Per-PR revert is clean. Combined revert restores Session 1199 partial state.

### B.2 — Row 9 Auto-Research Evidence Supplier (extends `05931145-…` or new child)

**Why.** Stage 1 of every Initiative gets BLOCKED on SEC/Kaggle evidence packs. This is the upstream cause of why the Initiative pipeline produces nothing useful — the 3 spine Initiatives have been stuck at Stage 1 for multiple sessions.

**Scope:**
- Locate Stage 1 dispatcher (likely `core/services/content_deliberation_runner.py` or a related task in `core/tasks_initiatives.py`)
- Find evidence-supplier — where do "evidence cards" come from? Why is SEC/Kaggle the default regardless of Initiative topic?
- Decide fix:
  - **(a)** Match evidence pack to Initiative topic (requires topic→evidence mapping)
  - **(b)** Skip Stage 1 auto-research when no relevant evidence available (BLOCKED → DEFERRED with clear reason)
  - **(c)** Make Stage 1 opt-in via Initiative metadata flag

**Lean:** (b) is the lowest-blast-radius fix. (a) is the highest-value but needs evidence cataloging work.

**AC:**
- Initiatives spawned post-fix get Stage 1 evidence matched to their topic, OR cleanly skip Stage 1 with a clear reason
- The 3 spine Initiatives become un-blockable (one-shot remediation: re-dispatch Stage 1 once fix lands)

### B.3 — NULL-Workspace Initiative Backfill (one-time data fix)

**Why.** 31 of 46 Initiatives (67%) in the DB have `target_workspace_id=NULL`. The producer-reroute leak created an Initiative-side equivalent: spawn-without-workspace. Without backfill, all 31 stay orphaned even after B.1 fixes future spawns.

**Scope:**
- One-shot mgmt cmd: `python manage.py backfill_initiative_workspace_assignments --dry-run` → `--apply`
- Per-row resolution order:
  1. If `parent_initiative` (via `related_initiatives` `spawned_from`) has a `target_workspace_id`, inherit it
  2. Else: creator's user_workspace
  3. Else: default to DBZ (`b4503364-…`)
- Emit `[INITIATIVE-BACKFILL] id=X new_ws=Y reason=Z` per row

**AC:**
- After apply: 0 Initiatives with `target_workspace_id=NULL`
- Audit deliverable lists per-row decision rationale + reverse-rollback recipe

## Phase C — Structural fixes (Sessions 1204-1205)

### C.1 — Docs ↔ Runtime Alignment Layer (`1859dd51-…`)

**Why.** Prevents Session 1201's "docs vs runtime drift" from recurring every session.

**Scope (2 changes):**

1. **Handoff template patch.** Add a mandatory "Session Manifest" section to the handoff template:
   ```markdown
   ## Session Manifest

   ### Initiatives created / touched
   | ID | Name | Status | Workspace |

   ### Deliverables created / touched
   | ID | Title | Initiative | Tags |
   ```
   New handoff PRs without this section fail pre-commit lint (`scripts/verify_repo_guardrails.py` adds a check).

2. **`context-kit orient` enhancement.** Add a "RUNTIME WORK STATE" block alongside the existing anchor previews:
   - Lists active Initiatives in DBZ (kind + status)
   - Lists last 7d deliverables (title + initiative)
   - Cross-flags any UUID in the latest handoff but NOT in runtime (and vice versa)
   - ≤40 lines total

**AC:**
- New handoffs include Session Manifest; lint enforces it
- `context-kit orient` shows runtime state inline with doc anchors
- Stale-handoff UUID detection produces zero false positives on a baseline of last 5 handoffs

### C.2 — Start-Here status reconciliation

**Why.** `00-START-NEXT-SESSION.md` has 4 carryover items showing "Pending" while runtime says "completed":
- `48b73b04-…` B.1 Unify Initiative-stage
- `9d9db48a-…` PR-D contract flip
- `9a00667b-…` DM system bug
- `88952c54-…` Session 1187 utilization recon (docs say partial, runtime says blocked)

**Scope.** Edit `00-START-NEXT-SESSION.md` carryover section to reflect current runtime status. Mark obsolete items as ✅ closed. (Trivial — needs to happen before Session 1202.)

### C.3 — PLATFORM_INVENTORY false-drift correction

**Why.** "108 schemas + 173 handlers" comparison framing creates a phantom drift signal (Row 11 finding). The counts compare different layers by design.

**Scope.** Update `PLATFORM_INVENTORY.md` to clarify the gateway pattern:
> 108 LLM-facing PA tool schemas. 173 dispatcher handlers: 107 directly mapped to schemas; 66 reachable via `run_agent` meta-tool gateway; 1 schema (`run_agent`) is the gateway meta-tool itself (special-cased in `core/services/unified_pa_entrypoint.py:1687`).

Also re-run `python manage.py refresh_doc_inventory_blocks` to refresh the live-counts autoblock with the new note.

## Phase D — Re-audit with new tools (Sessions 1205-1207)

Now that Phase A diagnostic tools exist, re-run the blocked rows for terminal classification.

### D.1 — Row 12 (LLM Providers, completed audit)
Use `diagnostics_tool action=provider_calls` → enumerate 7d calls per provider. Flag any with 0. Per provider decide: remove from registry, OR activate.

### D.2 — Row 13 (Learning Bridges, completed audit)
Use `diagnostics_tool action=learning_bridge_writes` → per-bridge 30d writes. Identify dead bridges (registered, never writes). Either fix the signal wiring or remove the bridge.

### D.3 — Row 14 (Beat schedule, completed audit)
Use `diagnostics_tool action=beat_schedule_health` → sorted stale + zero-runs. Per task decide: enable / disable / delete.

### D.4 — Row 16 (Discord bot, completed audit)
Use `diagnostics_tool action=discord_health` → uptime + invocation counts. Decide if the bot is a real usage surface or dead weight (and whether the 96 commands need pruning).

### D.5 — Row 5 (Learning loop) cleanup
Three known fixes from Row 5 deliverable `23edb2a4-…`:
1. Expand `UserAgentLearning.get_or_create` writers to top execution-volume agents (ResearchAgent, TrendAnalysisAgent, EditorAgent)
2. Audit Learning Bridges (use D.2 output to inform — which are read-only vs writer)
3. Add shadow-mode threshold logging at `combined >= 0.5` to measure what WOULD have been used

### D.6 — Row 6 (Body Coordinator) — 1-line fix
Add `PeriodicTask` rows via `add_critical_celery_tasks` mgmt cmd:
- `core.tasks.coordinate_body` — 60s interval (matches `_impl_coordinate_body` docstring intent)
- `core.tasks.check_muscular` / `check_brain` / `check_skin` / `check_nervous` / `check_digestion` / `immune_scan` — 5-15min cadence each

**Caveat:** Confirm response logic still matches current platform shape before enabling autonomic throttling. The historical absence may be intentional (currently disabled = currently safe; flipping it on triggers behavior that may misfire on stale heuristics).

### D.7 — Row 10 (25 Advisors) docs correction
**Decision required:**
- **Option A:** Update CLAUDE.md + PLATFORM_INVENTORY to reflect actual 25 real-person names (matches code + data)
- **Option B:** Migrate data to functional names + update `ADVISOR_DOMAIN_SPIDERS` keys + retroactively rename rows

**Lean:** Option A unless legal/IP concerns require Option B.

Regardless: regenerate `docs/ADVISOR_AUDIT.md` via `python manage.py build_advisor_audit` (DOC-AUTOGEN per memory rule).

## Phase E — Spine forward progress (open-ended)

Once Phase B.2 fixes the evidence supplier:

### E.1 — Spine 1 unblock + advance
Initiative `6941372d-…` Initiatives-First Wiring + No-Orphan Output — currently BLOCKED at Stage 1. Once auto-research evidence supplier fixed, re-dispatch Stage 1 → walk Stages 2-5.

### E.2 — Spine 2 + 3 advance
- `2071a9c6-…` Agent Capability Map + Router Contracts
- `7e23d621-…` Tool Migration Hardening (web_search → intelligence_tool) + Failure Fix

Same Stage 1 re-dispatch pattern. Then separate workstreams to implement each spine's actual scope.

These are separate workstreams from the Reality Map but unblocked by the Phase B.2 fix.

## Cross-cutting items

### Memory rules added during Session 1201

- **Gateway pattern false drift:** schema↔handler counts compare different layers; `run_agent` is a meta-tool special-cased in `unified_pa_entrypoint.py:1687`. Don't treat the count delta as a gap.
- **System Autonomous Workspace must stay deactivated when DBZ is target:** Producer Reroute fix (Phase B.1) should land before any rule change here.
- **Initiative spawn without target_workspace_id is a smell:** until A.1 ships, always set workspace at create-time or patch via ORM immediately. After A.1, use `work_tool action=initiative_update`.

### Validation checkpoints

| After phase | Verification |
|---|---|
| A | Operator can spawn + bind + link Initiatives entirely via Rigby tools; all 6 telemetry-blocked rows have working diagnostic actions |
| B | 7-day watch: 0 new System Autonomous deliverables; 0 NULL-workspace Initiatives |
| C | `context-kit orient` shows runtime state inline with doc anchors; new handoffs include Session Manifest; start-here carryover matches runtime |
| D | All 16 Reality Map rows have terminal classifications (flowing / dry+fix-shipped / missing+decision-made); no row remains "blocked on tooling" |
| E | At least 1 spine Initiative walks past Stage 1; visible forward progress on the "Initiatives-First" backbone |

### Effort estimate

| Phase | Sessions | Notes |
|---|---|---|
| A | 1-2 | Tools are scoped; no deep recon needed |
| B | 1-2 | 3 small PRs + 1 mgmt cmd + 1 medium-touch on Stage 1 |
| C | 1 | Mostly docs + template patches |
| D | 2-3 | Per-row decisions + fixes, parallelizable |
| E | open | Depends on each spine's scope |

**Total: 6-8 sessions to full close.**

## Decision points requiring operator (Chris) input

1. **Row 10 advisors:** Option A (correct docs to data) or Option B (migrate data to functional)?
2. **Row 6 body coordinator:** Enable autonomous tick now, or audit response logic first?
3. **Phase ordering preferences:** Strictly A → B → C → D → E, or interleave (e.g., B.1 while A.2 in flight)?
4. **Spine Initiatives:** Address opportunistically when Phase E becomes possible, or actively plan as separate workstreams?

## Provenance

- Drafted Session 1201 close (2026-06-22) by Claude in collaboration with Rigby.
- Based on the 16-row Reality Map drift inventory + 4 child Initiative fix scopes filed during Session 1201.
- Parent: Platform Connectivity Reality Map Initiative `0ecd1bc2-9931-4464-8efa-495a28b58779` (spawned_from Spine 1).
- Sequencing logic: unblock auditing → stop live drift → structural fixes → re-audit with new tools → spine progress.
