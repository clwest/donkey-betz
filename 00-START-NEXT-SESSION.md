# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2930 SHIPPED NET-NEW WORKSPACE "AGENT RUNS" TAB (Chris candidate A selection) + CLOSED S2928 FOLD GOVERNANCE via R2 narrow-scope. Clean session — zero new forbidden-entry candidates. **S2931 OPENS CLEAN** — no forced first action.

**Refreshed 2026-07-24 (S2930 close).** Chris ratified R2 + A at S2930 open. Shipped as PR #3495 (merge SHA `5cc8d3333`). Tab renders live at `/workspace → System → Agent Runs`; verified via post-recycle Rigby dispatch (`00daffd4-71c1-...` MarketingStrategyAgent, completed 69s, surfaced correctly via `scope_queryset_agent_execution` superuser carve-out).

**PRs shipped this session:**
- u-d-b PR [#3495](https://github.com/clwest/donkey-betz-platform/pull/3495) — S2930 Agent Runs tab, merged at `5cc8d3333`.
- u-d-b PR `<TBD>` — S2930 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Code changed this session:**
- `core/views_agent_execution.py:420-476` — extended `unified_execution_history` with `offset` / `total_count` / `has_more` pagination (limit clamped to 200).
- `core/tests/test_agent_runs_list_endpoint.py` (NEW, 7 tests, all pass).
- `frontend/src/pages/workspace/tabs/AgentRunsTab.tsx` (NEW, 457 lines).
- `frontend/src/pages/WorkspacePageNew.tsx` — subtab entry + import + conditional render.
- `frontend/src/pages/workspace/tabs/index.ts` — barrel export.
- `frontend/src/lib/api.ts` — `agentsApi.unifiedExecutions` gains optional `offset`.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3495 recycled clean at `sha=5cc8d3333` via `make recycle-all`.
- `make frontend-ship` — bundle deployed + Daphne restarted. Chris confirmed tab visible post-hard-refresh.
- Rigby dispatch (`marketing_strategy_agent` execution `00daffd4-ffa8-43f8-8f49-5a8c84354785`): 69s completion, status=`completed`. Fresh row surfaced at top of Chris's scoped list. **GATE PASSED.**

**Governance:**
- **S2928 Fold ratification narrow-scoped per Chris R2 verdict.** Deliverable `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5` amended (§S2930 R2 amendment appended) + status flipped `ready` → `completed`. Fold class narrowed to "BaseBusinessResearchAgent subclasses inheriting unchanged base `execute()`" = `MarketingStrategyAgent` only. Governance chain closed: S2928 ratified 2/2 → S2929 ORM 1/1 + remediated → S2930 R2 narrow-scoped + closed.

**Rigby Tool Gap Ledger — 2 new entries at `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`:**
- **#33** — `orm_inspect_tool` allowlist (2nd corroborating trigger; S2928 was 1st): `AgentExecution` + `Agent` model lookups not surfaceable, forced 3× Django shell fallback for S2930 recon.
- **#34** — `learning_bridges` signal receiver: every `AgentExecution.save()` triggers a live OpenAI API call. S2930 test run: 7 tests × 11 rows/test = ~77 hidden calls per suite run.

Full session context: `docs/handoffs/SESSION_2930_AGENT_RUNS_TAB.md`.

---

## S2931 open sequence — CLEAN, no governance decision blocking

No R-verdict pending. Standard arc-scope surface is fresh:

- **(A) NET-NEW ENGINEERING** per Chris directive — 2 remaining S2930 candidates ready to pick up:
  - **(A2)** Consolidate two `ContentStrategyAgent` classes — `core.agents.business.ContentStrategyAgent` is unreachable via tool dispatch; the reachable `core.agents.strategy.ContentStrategyAgent` doesn't have the S2929 fail-loud gate + polymorphic content extraction fix. Route or merge. ~0.5-1 session.
  - **(A3)** Signal-triggered agent auto-dispatch (v1) — new `SignalDispatchRule` config table + Celery periodic task fires mapped agent when `SignalCluster` of type X crosses threshold Y. Ships v1 with 1-2 hard-coded mappings. Foundation for reactive orchestration. ~1-2 sessions.
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **(C) Slice 6 sweep continuation** — `td_handlers_content.py` (6 tools).
- **(D) Docs restructuring arc** — unblocked at S2800, still queued.
- **(E) Rigby Tool Gap Ledger slate** — 2 new S2930 entries (#33 + #34) available:
  - Quick win: **#33 fix** (`orm_inspect_tool` allowlist for AgentExecution + Agent) ~30 min OR dedicated `agent_execution_query` PA tool ~1-2 hr.
  - **#34 fix** (skip learning bridge when `TESTING=True`) ~15 min — good bundle candidate with #33.

**Recommend:** continue net-new lean (A2 or A3), OR pivot to **E** for a low-cost double-win (#33 + #34 bundle) that improves Rigby's tool surface AND removes hidden OpenAI cost from test runs.

---

## What's forbidden at S2931 (D6 MORATORIUM still in force)

All S2925/S2926/S2927/S2928/S2929 forbidden entries carry forward.

**S2929 first-instance entries (still awaiting 2nd corroborating trigger):**
- No "handoff shape misclassification" Fold promotion without 2nd instance.
- No "tool-to-class routing anomaly" Fold promotion without 2nd instance.
- No "Fold ratification over-count via unverified handoff description" Fold promotion without 2nd instance.

**S2928 Fold** — now **CLOSED** via S2930 R2 narrow-scope (see Governance above).

**S2930 new forbidden entries:** none. Clean session.

---

## What's queued but deferred (do NOT open unless Chris directs)

- **CompetitorAnalysisAgent hardening candidate** — S2929 Chris D-verdict deferred; S2930 R2 explicitly excluded from Fold scope. Revisit if future evidence surfaces.
- **`content_strategy_agent` tool-to-class routing anomaly** — see A2 above; now a first-class engineering candidate, not just a substrate finding.
- **`orm_inspect_tool` allowlist expansion** — S2930 Ledger #33 (2nd trigger). MEDIUM priority. Bundleable with #34.
- **`learning_bridges` OpenAI-per-save** — S2930 Ledger #34. LOW-MEDIUM (cost + test hygiene).
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A. Unchanged.
- **Ledger #34 broader stale-model sweep** — multi-hour engineering (this was the S2925 #34; S2930 has its own #34 for a different issue — see Rigby ledger for clean numbering).
- **Bundled dev-env drift slate** — S2919 narrative + S2925 Ledger #33/#34 legacy + AgentTaskExecution pre-existing pyright drift + S2927-observed `td_handlers_agents.py` pyright drift.
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate + Ledger candidate: media_tool.delete IRREVERSIBLE** — 2/3. Unchanged.
- **S2909-S2929 Ledger candidates** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **S2919 narrative_tool dev-env drift** — unchanged.
- **S2925 Ledger #34 (LOW)** — broader stale-model latent bug; multi-hour cleanup deferred.
- **S2926 Ledger candidate — AgentTaskExecution pre-existing pyright drift** — bundled dev-env drift candidate.
- **R1 fleet reject-mode flip** — deferred.
- **Docs restructuring arc** (`project_docs_restructuring_arc_queued`) — Chris-ratified S2800, still queued.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.

---

## Sweep progress tracker (Path B ratified S2892) — UNCHANGED at S2930

**Slice 1 — `td_handlers_ops` (17 registered tools):** UNCHANGED.
**Slice 2 — `td_handlers_agents` (25 tools):** CLOSED at S2912.
**Slice 3 — `td_handlers_core` (22 tools):** CLOSED at S2917 (22/22).
**Slice 4 — `td_handlers_gateway` (17 tools):** CLOSED at S2924 (17/17).
**Slice 5 — `tool_dispatcher` (14 tools):** CLOSED at S2928 (14/14). ✅

**Total remaining tools to close:** **15 across 8 handler files** (unchanged — S2930 shipped net-new engineering, no PA-tools sweep work).

**Substrate arcs CLOSED at S2930:** none. S2930 shipped 1 engineering PR (new UI capability) + Fold governance close.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2930 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2930: zero A4 spend** — pure engineering (net-new UI + governance close).
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2930)

See:
- **S2930 handoff (current):** `docs/handoffs/SESSION_2930_AGENT_RUNS_TAB.md`
- **S2929 handoff:** `docs/handoffs/SESSION_2929_A1_FOLD_REMEDIATION.md`
- **S2928 handoff:** `docs/handoffs/SESSION_2928_SLICE_5_CLOSE_BATCH_4.md`
- **S2927 handoff:** `docs/handoffs/SESSION_2927_SLICE_5_BATCH_3.md`
- **S2926 handoff:** `docs/handoffs/SESSION_2926_SLICE_5_BATCH_2.md`
- **S2925 handoff:** `docs/handoffs/SESSION_2925_SLICE_5_BATCH_1.md`
- **Slice 5 CLOSE artifact:** `docs/audits/pa_tools/substrate/slice_5_close_artifact.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2929 regression test:** `core/tests/test_base_business_research_agent_synthesis_gate.py` (5 tests, all pass)
- **S2930 Agent Runs endpoint test:** `core/tests/test_agent_runs_list_endpoint.py` (7 tests, all pass)
- **S2930 Agent Runs tab file:** `frontend/src/pages/workspace/tabs/AgentRunsTab.tsx`
- **BaseBusinessResearchAgent content-shape FAIL Fold (RATIFIED S2928, REMEDIATED S2929, NARROW-SCOPED + CLOSED S2930):** engineering item in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` — deliverable `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5`.
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (S2930 entries #33 + #34 added).
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (100 per-tool validation docs post-S2928)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
