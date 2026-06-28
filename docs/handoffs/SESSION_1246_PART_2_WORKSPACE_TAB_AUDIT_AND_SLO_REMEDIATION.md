# Session 1246 — Part 2 — Workspace tab audit + SLO remediation arc

**Session window:** 2026-06-27 Saturday evening into 06-28 early morning CDT/MDT (continuous from S1246 Part 1 close).

**Theme:** What started as "close S1246 cleanly" turned into a full-platform audit when Chris asked late evening: *"Before we call it a night, do you and Rigby feel up to going through each tab in the workspace, verify it's real data and if it's actually working as intended?"* The audit reshaped the night — 31 tabs catalogued + classified, 3 BROKEN tabs fixed, 6 P1 untested-runtime closures via PA tool surface fixes, 6 lane-fix PRs across audit findings, 1 SLO breach cleared via product decision (Catalyst blog archived). Part 1's earlier close handoff (`SESSION_1246_S1245_BONUS_FINDINGS_CLOSED_PLUS_AUDIT_AXIS_PLUS_CONTENT_TASK_RETIREMENT_PLUS_FLEET_VERIFICATION.md`) covers the first 7 PRs of the day; this Part 2 covers the audit arc from PR #2696 through PR #2705.

---

## TL;DR

- **8 PRs shipped + admin-merged** (all `session-1246-` subject-tagged): #2696, #2697, #2698, #2699, #2700, #2701, #2702, #2703, #2704, #2705. _(Day total across both parts: 15 PRs)_
- **4 ORM data fixes**: Donkey Betz workspace `root_path` translated to local codebase; 3 stuck SelfBlog test fixtures archived; Catalyst blog archived; CodeGeneratorAgent unblocked.
- **5 deliverables produced** (all Donkey Betz workspace `b4503364-…`, all `status=ready`):
  - `dac45b4f-…` — S1247 workspace tab audit plan
  - `6b32c13b-…` — S1247 pilot Deliverables tab audit
  - `1c3e63ec-…` — **S1247 workspace tab audit RUNTIME VERIFICATION** (~14,000+ chars after all wave additions + final closure section)
  - `421eeaca-…` — S1246 P1 morning_brief verification runbook (still valid for 06-28 13:00 UTC tomorrow)
  - `c5ea2f61-…` — S1247 content/ char-training full retirement reachability map (from Part 1)
- **31 tabs audited.** Verdicts: 13 Real & Working, 4 Real but UX issues, 5 Mixed/partial, 5 Dormant/Empty-Real, 1 Mock, 3 BROKEN-then-FIXED.
- **3 SLO breaches at session close** — 1 fully cleared, 2 self-recovering as 24h window rolls forward.
- **2 memory rules added.**

### Net stats

- **8 PRs** in this Part 2 (15 across the full day)
- **5 deliverables** in flight at close, 4 created in Part 2
- **31 tab files audited** via parallel Explore agent + Rigby runtime verification
- **6 lanes closed** (audit lanes F/G/H/I/K/L + the 3 BROKEN tabs)
- **2 memory rules added** in Part 2

---

## What shipped — Part 2 PRs

| PR | SHA | Subject | Lane |
|---|---|---|---|
| [#2696](https://github.com/clwest/donkey-betz-platform/pull/2696) | `dd2ac722` | Deliverables tab — grouped view with recency + category accordions | UI request |
| [#2697](https://github.com/clwest/donkey-betz-platform/pull/2697) | `68a5d947` | move Deliverables work surface to top of tab | UI request (Chris feedback on #2696) |
| [#2698](https://github.com/clwest/donkey-betz-platform/pull/2698) | `e67c2a18` | http_smoke_test auto-detects environment from RAILWAY_ENVIRONMENT | PA tool fix #1 |
| [#2699](https://github.com/clwest/donkey-betz-platform/pull/2699) | `(merge SHA)` | import WorkspaceOperation where workspace_tool uses it | OperationsTab BROKEN |
| [#2700](https://github.com/clwest/donkey-betz-platform/pull/2700) | `(merge SHA)` | route WorkspaceContext serialization through .workspace FK | FilesTab BROKEN |
| [#2701](https://github.com/clwest/donkey-betz-platform/pull/2701) | `(merge SHA)` | expand PublishGate operational-title patterns for test/QA artifacts | F1 (publish_ready_age_p95) |
| [#2702](https://github.com/clwest/donkey-betz-platform/pull/2702) | `(merge SHA)` | http_smoke_test resolves local auth token from chris user | H (smoke_test auth) |
| [#2703](https://github.com/clwest/donkey-betz-platform/pull/2703) | `(merge SHA)` | base_agent intelligence_tool handler + tool-call telemetry hygiene | L (pa_tool_success_rate) |
| [#2704](https://github.com/clwest/donkey-betz-platform/pull/2704) | `(merge SHA)` | 3 sports agents — empty upstream is no_data, not failure | K (45.7% agent success) |
| [#2705](https://github.com/clwest/donkey-betz-platform/pull/2705) | `(merge SHA)` | env-aware effective_root_path on ProjectWorkspace | G (broader root_path) |

---

## The audit arc (the spine of Part 2)

Chris's framing at 18:55 MDT: *"…if we have a high quality audit it might reshape the way we are running things like the test running in the morning."*

That framing turned out to be exactly right. The audit didn't just produce verdicts — it surfaced 6 distinct platform-state issues that drove the rest of the night's PRs.

### Methodology

- **Code-side inventory**: dispatched an `Explore` agent to bulk-read all 31 `.tsx` files in `frontend/src/pages/workspace/tabs/`, produce a per-tab card with endpoints + mutations + WebSocket usage + hardcoded-data smells + suspicion classification. Output included a cross-cutting patterns section.
- **Runtime verification (4-wave then 2 corrections)**: Rigby took the inventory and worked through it in 4 waves by priority — Daily operator loop, External-effect pipelines, Intelligence/Knowledge, Ops/Admin — using PA tools to hit endpoints + classify responses. Waves 5+6 ran corrections after blocker fixes.
- **Split discipline**: Claude = source-code reads + identified mock/hardcoded + traced handlers. Rigby = runtime endpoint verification + DB ORM probes + write-action tests. Each verified the other.

### Final tab classifications

| Bucket | Tabs | Count |
|---|---|---|
| **Real & Working** | DeliverablesTab, WorkTab, InitiativesTab, OutreachInboxTab, OpsConsoleTab, BoardroomTab, KnowledgeTab, IntelligenceTab (desks), DataSourcesTab, GovernanceTab, OperationsTab (post-fix), GitTab (post-fix), FilesTab (post-fix) | 13 |
| **Real but UX issues** | HomeTab (post #2697), Deliverables (covered via the grouped-view + reorder PRs) | counted under above |
| **Mixed / partial — auth needed for full verification** | ContentStudioTab (podcasts all fleet smoke), AIConsciousnessTab (agent-conversations empty), OrchestrationTab (deliberation real, agent monitoring real), InfrastructureTab (WS untested), WorkspaceOverviewTab | 5 |
| **Dormant / Empty-Real** | CampaignTab, VoiceMarketplaceTab, ClosePackViewer, ConceptForgeTab, BuildPacketWizard, DataIntelTab (post-Wave 5), Stage3EvaluationTab (post-Wave 5), ToolCallAnalyticsTab (post Wave 6 — Real with 3,869 records actually), TriggersTab (post-correction) | 5+ |
| **Mock** | AppTab | 1 |
| **BROKEN → FIXED** | OperationsTab (#2699), FilesTab (#2700), GitTab (ORM root_path) | 3 |

### Cross-cutting findings from the audit

1. **Dormancy / no-op-receipt pattern** across 6 surfaces — features exist but only fleet-smoke traffic flows through them: CharacterTrainingAgent + TrainedCreationAgent (S1245 finding), Podcasts pipeline (10/10 episodes are fleet-smoke), VoiceMarketplace (0 voices), CampaignTab (0 campaigns), ConceptForge (0 runs), ClosePack (0 close packs).
2. **PA tool coverage gap** for UI-routed `/api/*` endpoints (Wave 3 + 5 untested-runtime spike). Caused by `http_smoke_test` defaulting to prod Railway URL even when running local — fixed via #2698 (env auto-detect) + #2702 (local auth token). After both fixes, Rigby has full /api/* coverage without per-endpoint PA tools.
3. **3 active SLO breaches** surfaced during audit: `publish_ready_age_p95 = 357.9h`, `pa_tool_success_rate = 81.25%`, `celery_task_success_rate = 98.55%`. All three got direct remediation PRs (#2701 + #2703 + #2704 respectively).
4. **CodeGeneratorAgent blocked 15 days** with Railway-sandbox-specific reason that never re-evaluated. ORM unblocked + reason updated.
5. **Workspace root_path Railway-shape pattern** — 8 of 10 workspaces have `/app/workspaces/...` paths that don't exist locally. Translator property + workspace_manager updates shipped (#2705).
6. **OrchestrationTab agent_monitoring dashboard at 45.7% success rate** — probe revealed entire failure block was 2 sports agents (SportsOddsAnalyst 13/13, ArbitrageDetector 12/12) bouncing on empty upstream data. Surfaced as success-not-failure pattern (#2704).

---

## Lane closures

| Lane | What it caught | What we shipped |
|---|---|---|
| **F1** | PublishGate's `OPERATIONAL_TITLE_PATTERNS` only matched bracketed admin prefixes; test fixtures like `BLOGTOOL_E2E_v1`, `Verify Your Blog Tool Lifecycle`, `Platform QA Pass 1` slipped through and ended up `approved + publish_ready=True` for 175-358h. | #2701: added 9 patterns for BlogTool / Verify Your / Platform QA Pass N / E2E / smoke / Test Run / Integration test / Regression check / trailing `verification`. 12/12 operational caught, 7/7 non-operational pass. |
| **F2** | 3 stuck test-fixture SelfBlogs (BLOGTOOL_E2E_v1, Verify Your Blog Tool Lifecycle, Platform QA Pass 1) + 1 real-topic stuck (Autonomous Catalyst Tracking). | ORM archive of 3 test fixtures + Chris-decision archive of Catalyst → `publish_ready_age_p95` cleared from 357.9h → 0.0h on next snapshot. |
| **G** | 8 of 10 workspaces have Railway-shape `/app/workspaces/<slug>` paths → FilesTab + GitTab + workspace_manager 'path not found'. | #2705: env-aware `effective_root_path` property; translates stored prod paths to local when `WORKSPACE_BASE_DIR` env var is set + target dir exists. Falls back gracefully. |
| **H** | `http_smoke_test` was sending the prod `.env` `PA_API_TOKEN` to local Django → 401 on every auth-gated endpoint. Blocked 9 endpoints from runtime verification. | #2702: `_resolve_auth_token(environment)` resolves chris's DRF token for local; `LOCAL_PA_API_TOKEN` env var as explicit override; preserves prod behavior. 4/4 smoke cases pass. |
| **I** | CodeGeneratorAgent blocked since 2026-06-12 with reason "No codebase access in Railway sandbox" — never re-evaluated. Locally Chris HAS fs access. | ORM unblock with updated reason flagging re-block needed if redeployed to no-fs sandbox. `blocked_now=[]`. |
| **K** | OrchestrationTab agent monitoring at 45.7% success rate. Probe: 25/25 failures were 2 sports agents bouncing on empty upstream odds data, marking themselves `success=False`. | #2704: 3 markets agents (SportsOddsAnalyst, ArbitrageDetector, PredictionMarketAnalyst preemptive) surface empty upstream as `success=True` with `data={'status': 'no_data', 'reason': '...'}`. |
| **L** | `pa_tool_success_rate = 81.25%` (26/32). Probe: 6/6 failures were `ResearchAgent → intelligence_tool` with empty `error_message`. | #2703 (2 bugs):  (a) `base_agent._execute_tool_call` had no `intelligence_tool` handler — migration off `web_search` (Session 1183) updated ResearchAgent but never the dispatcher. Added handler mapping `intelligence_tool action=search source=web` → WebSearchTool. (b) Telemetry hygiene: the `finally`-block `_record_tool_call` never passed `error_message` or `error_type` — every failure recorded with empty fields. Now extracts from result dict + classifies as `NotImplemented` vs `ToolExecutionError`. |

---

## SLO state at session close

| SLO | Target | Current at close | Trajectory |
|---|---|---|---|
| `publish_ready_age_p95` | ≤72h | 0.0h on next snapshot (backlog=0) | ✅ CLEARED via F1+F2+Catalyst-archive |
| `pa_tool_success_rate` | ≥99.9% | 81.25% (26/32) | 🔄 Recovering as 24h window rolls past today's 6 intelligence_tool failures + #2703 prevents recurrence |
| `celery_task_success_rate` | ≥99.9% | 98.55% (3406/3456) | 🔄 Recovering as spider_data stale-worker failures roll out of window (root cause was fixed by celery bounces today, not a code fix) |

All 3 self-recover or are already cleared. No active SLO action required for S1247.

---

## ORM data fixes (not code, but worth recording)

| Fix | Before | After | Why |
|---|---|---|---|
| Donkey Betz workspace `root_path` | `/app/workspaces/donkey-betz` (Railway shape) | `/Users/donkeyking/development/unified-donkey-betz` (actual local codebase) | FilesTab + GitTab were 'path not found'. PR #2705 generalizes the pattern via env-aware translator; this fix is the one-time correction for the workspace Chris uses daily. |
| 3 stuck SelfBlog test fixtures | `status='approved', publish_ready=True` (175-358h old) | `status='archived', publish_ready=False` | F2 — drag was test fixtures, not real content. PR #2701 prevents future ones. |
| Catalyst blog | `status='approved', publish_ready=True` (338h old) | `status='archived', publish_ready=False` | Chris decision — real topic but stale content. Cleared `publish_ready_age_p95` SLO to 0.0h. |
| CodeGeneratorAgent `AgentControlEntry` | `status='blocked', reason='No codebase access in Railway sandbox'` | `status='enabled', reason='S1247 audit lane I: unblocked for local execution; original block was Railway-sandbox-specific. Re-block if redeployed to a no-fs sandbox.'` | 15-day-old Railway-specific block never re-evaluated. Local env has fs access. |

---

## Memory rules added (Part 2)

1. **`feedback_stop_putting_chris_to_bed.md`** — Don't end sessions with "go to sleep" / "sleep well" / paternalistic suggestions. Chris flagged: *"It's only 7pm lol you and Rigby are trying to put me to bed like an infant lmao."* Session-end summaries are status reports, not bedtime suggestions. Time-bound items get flagged with actual deadline, not "so we should stop now." Override: Chris self-calls it.

2. **`feedback_fleet_caller_verification_before_celery_deletes.md`** (added in Part 1, called out here for completeness) — 3-axis fleet caller sweep before any Celery deletion PR.

---

## What's still open going into S1247

| Item | Status | Notes |
|---|---|---|
| **P1 morning_brief CUMULATIVE verification** for 06-28 ~13:00 UTC tomorrow | Time-bound | Use deliverable `421eeaca-…` (runbook). Today's PRs cleared 3 of the audit-found platform issues that could've affected it. Verification block in start-here. |
| `pa_tool_success_rate` SLO 81.25% | Self-recovering | #2703 prevents recurrence + 24h window rolls past failures. Should clear by 06-28 evening. |
| `celery_task_success_rate` SLO 98.55% | Self-recovering | Stale-worker failures clear out of window. Should clear similarly. |
| **CharacterModel + 16-file dependency chain** | Plan deliverable ready (`c5ea2f61-…` from Part 1) | S1247 P2 candidate — full content/ char-training subsystem retirement per Rigby's reachability map. |
| **Catalyst blog archived but worth re-reading** | Decided | Real-topic, 1,034 words — could be salvaged as starting point for fresh content if Chris ever wants. |
| **Local FleetServiceKey=0 + dormant fleet locally** | Carryover question | Part 1 finding. Open Q for prod: are fleet keys prod-only? Dormant? Never provisioned here? Worth resolving before any model-layer content/ retirement work. |
| **5 dormant feature surfaces** (CampaignTab/VoiceMarketplace/ConceptForge/ClosePack/BuildPacketWizard) | Product decisions | All have working backend + UI but zero/no-op traffic. Not bugs — pending Chris call on whether they're scaffolded-ahead, abandoned, or prod-only. |
| **3 SLO breaches recovering naturally** | No action | Will be visible in S1247 ops_tool checks; don't chase unless they stick. |

---

## S1247 entry hints (also in `00-START-NEXT-SESSION.md`)

- **P0**: conversation health check on `pa-2bb73c969fd24802` (likely fresh-start needed after this session's volume)
- **P1**: 06-28 morning_brief CUMULATIVE verification at ~13:00 UTC. Runbook is `421eeaca-…`. Now de-risked further by today's audit fixes.
- **P2**: ship the content/ char-training full retirement using deliverable `c5ea2f61-…`. Resolve the fleet-keys-on-prod question first.
- **P3**: cf708a2e workspace leak rotation fix (carryover from Part 1).
- **P4**: re-run `audit_celery_zero_fire --include-direct-calls --days 30` once telemetry accumulates ~2026-07-13.

---

## What this session was actually about

If you read this handoff in 3 months and want the headline: **Chris asked for a tab-by-tab audit. The audit's deliverable wasn't the 31 verdicts — it was the 6 leverage fixes the audit surfaced.** Most platform audits stop at "documented what's there." This one chased every cross-cutting finding to a shipped PR. That's why the day's PR count tripled from the planned S1246 close (4 PRs) to the actual close (15 PRs). Worth replicating when the platform is in a steady-state phase and we want to surface what's actually load-bearing.
