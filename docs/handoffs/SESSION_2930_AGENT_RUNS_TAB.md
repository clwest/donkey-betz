# Session 2930 — Agent Runs Tab (net-new engineering) + S2928 Fold narrow-scope close

**Date:** 2026-07-24
**Merge SHA:** `5cc8d3333` (PR #3495)
**Type:** Net-new engineering (candidate A per S2930 arc-scope surface, Chris-selected)
**Governance:** S2928 Fold ratification narrow-scoped per Chris R2 verdict (see §3)

---

## 1. What shipped

New Workspace tab surfacing `AgentExecution` history so every agent dispatch leaves a findable receipt. Replaces the prior workflow of dispatching via Rigby, capturing the `execution_id` verbally, then dropping to Django shell to find the row later.

**Location:** `/workspace` → System → **Agent Runs** (subtab between Autopilot and Cost).

**Behavior:**
- Paginated table (25/page): agent name, status badge, task preview, when, duration, cost.
- Filter by agent name (icontains) + status (dropdown).
- Row click → side panel with full task, input_data, output_data, error_message, related memory.
- React Query auto-refetch every 30s + `keepPreviousData` for smooth paging.

---

## 2. Code changed

### Backend (`core/`)

* `views_agent_execution.py:420-476` — extended `unified_execution_history` (S760 endpoint) with `offset`/`total_count`/`has_more`. `limit` clamped to 200. **No new endpoint or URL** — reused existing `execution_detail` for row expansion.
* `tests/test_agent_runs_list_endpoint.py` — NEW, 7 tests (pagination, scoping, superuser null-user carve-out via `scope_queryset_agent_execution`, agent+status filters, ordering). All pass.

### Frontend (`frontend/src/`)

* `pages/workspace/tabs/AgentRunsTab.tsx` — NEW, 457 lines.
* `pages/WorkspacePageNew.tsx` — import + subtab entry (`{ id: 'agent-runs', label: 'Agent Runs', icon: Bot }` after Autopilot) + conditional render.
* `pages/workspace/tabs/index.ts` — barrel export.
* `lib/api.ts` — `agentsApi.unifiedExecutions` gains optional `offset` param.

### Scope calls made

* **W1 (no workspace filter)** — `AgentExecution` has no workspace FK; showing all Chris's runs globally per single-user pre-prod operating context. Deferred workspace-scoping to future session if it matters.
* **Reuse over rewrite** — extended the existing endpoint (5 new lines) instead of writing a new one, per Cycle 1A verify-before-build.

---

## 3. R2 governance close — S2928 Fold narrow-scoped

**Chris D-verdict (S2930 open):** R2 (re-scope Fold class), not R1 (de-ratify) or R3 (defer).

**Amendment appended to deliverable `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5`:**
- Fold class narrowed to: BaseBusinessResearchAgent subclasses inheriting unchanged base `execute()`.
- Real membership: `MarketingStrategyAgent` only (1 instance, remediated at PR #3493 `1465df616`).
- Not in scope: `CompetitorAnalysisAgent` (no verified current FAIL — S2929 recon superseded S2926 finding).
- Deliverable `status` flipped to `completed`.

Governance chain: S2928 ratified 2/2 → S2929 ORM-verified 1/1 + remediated → S2930 R2 narrow-scoped + closed.

---

## 4. Post-merge verify (per PLAYBOOK-7.4.4)

* `gh pr merge --admin --squash --delete-branch 3495` — merged at `5cc8d3333`.
* `make recycle-all` — clean recycle recorded (`sha=5cc8d3333982, surviving=none`).
* `make frontend-ship` — bundle deployed + Daphne restarted. Chris hard-refreshed and confirmed tab renders.
* Live dispatch via Rigby (`marketing_strategy_agent`, execution `00daffd4-ffa8-43f8-8f49-5a8c84354785`) — completed in 69s. Fresh row surfaced at top of Chris's scoped list via `scope_queryset_agent_execution`. **GATE PASSED.**

Wait-for-completion honored per `feedback_wait_for_agent_completions_before_close_cascade` — agent finished before close cascade began.

---

## 5. Rigby Tool Gap Ledger — 2 new entries

Added to deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`:

* **#33 — `orm_inspect_tool` (2nd corroborating trigger; S2928 was 1st):** `AgentExecution` + `Agent` model lookups not in allowlist. S2930 Explore agent aimed recon at `AgentTaskExecution` (0 rows) missing the live model `core.AgentExecution` (2,326 rows). Direct ORM verification caught the misdirection but required 3 separate Django shell invocations. Fix candidates: allowlist expansion (~30 min) OR dedicated `agent_execution_query` PA tool (~1–2 hr).
* **#34 — `learning_bridges` signal receiver:** Every `AgentExecution.save()` triggers a live OpenAI API call via `agent_execution_bridge`. S2930 test run: 7 tests × 11 rows/test = ~77 hidden OpenAI calls just to set up fixtures. Fix candidates: skip bridge when `TESTING=True` (~15 min), shared disable decorator (~30 min), or async Celery task guarded by settings (~1–2 hr).

---

## 6. First-instance findings (require corroborating trigger before promotion)

**No new 1st-instance forbidden-entry candidates this session** — S2930 was a clean net-new engineering session with no substrate-boundary drift observed.

S2929 open forbidden entries carry forward unchanged (handoff shape misclassification, tool-to-class routing anomaly, Fold ratification over-count).

---

## 7. Non-issues flagged

* Ledger #34 (learning-bridge OpenAI-per-save) is a real cost + correctness concern worth investigating separately — surfaced ONLY because my test suite created many fixture rows, not because of the tab or endpoint changes.
* Frontend `LucideIcon → ComponentType` type mismatch on `primaryTabs.icon` array is pre-existing, cosmetic, and affects every peer subtab; my one added line matches the peer pattern.

---

## 8. S2931 opens with (clean slate — no forced first action)

No governance decision blocking the next session. Standard S2930 open surface still valid:

- **(A) NET-NEW ENGINEERING** per Chris directive — remaining candidates from S2930 open: (2) consolidate two `ContentStrategyAgent` classes; (3) signal-triggered agent auto-dispatch v1.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(C) Slice 6 sweep continuation** — `td_handlers_content.py` (6 tools).
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.
- **(E) Rigby Tool Gap Ledger slate** — 2 new S2930 entries (#33 + #34) available for immediate work.

Recommend continuing net-new lean (A candidate 2 or 3), or pivot to E if Chris wants to cash in a quick fix from the ledger.

---

## Cross-refs

* **PR:** [#3495](https://github.com/clwest/donkey-betz-platform/pull/3495) `5cc8d3333`
* **Tab file:** `frontend/src/pages/workspace/tabs/AgentRunsTab.tsx`
* **Endpoint:** `core/views_agent_execution.py:408-476` (`GET /api/v1/agents/unified-executions/`)
* **Detail endpoint (reused):** `core/views_agent_execution.py:472` (`GET /api/v1/agents/execution/<id>/`)
* **Tests:** `core/tests/test_agent_runs_list_endpoint.py`
* **Fold ratification (narrow-scoped, closed):** deliverable `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5`
* **Ledger:** deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entries #33, #34)
