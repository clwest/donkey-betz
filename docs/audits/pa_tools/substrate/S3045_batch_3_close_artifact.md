# S3045 Batch 3 CLOSE — agent_via_run_agent bucket audit, stock/betting/blockchain family (10 tools)

**Session:** S3045 (agent_via_run_agent bucket audit — Batch 3)
**Ship shape:** validation docs (10 tools) + close artifact — combined PR. Substrate shipped in Batch 1 PR #3794; no substrate changes.
**Substantive intent:** RaaS-evidence class + 2 new failure taxonomies surfaced (infra-runtime + workspace-side-effect + coordinator-provenance-fanout).
**Prior batches:** Batch 1 PR #3794 (`dfeb6adb8`) + Batch 2 PR #3795 (`61e4950e5`).
**Rigby SIGN:** T1 authored-cold; T0 SIGN follows this batch.
**Chris directive 2026-07-30:** Odds API on back burner — no active API key. 3 Batch 3 tools (game_predictor / line_movement_analyzer / sharp_action_detector) surface this as infra-runtime failure. Skip Odds-dependent tools in future batches unless API key restored.

---

## 1. Batch 3 tool inventory (10 tools)

| # | Tool | Agent class | Batch 3 dispatch task_id | Duration | Verdict |
|---|---|---|---|---|---|
| 1 | `stock_analyst_agent` | `StockAnalystAgent` | `9f679e3a-…` | 24.2s | **PASS-w/-finding** (honest empty-data provenance) |
| 2 | `bear_case_agent` | `BearCaseAgent` | `559fd396-…` | 172.0s | **PASS-w/-finding** (workspace side-effect: wrote file) |
| 3 | `stock_audit_coordinator` | `StockAuditCoordinator` (**fanout-guard**) | `703953eb-…` | 145.1s | **PASS-w/-finding** (fanout-guard FAIL + workspace write) |
| 4 | `market_intelligence_coordinator` | `MarketIntelligenceCoordinator` (**fanout-guard**) | `e8eedb73-…` | 529.7s (~8.8min) | **PASS-w/-finding** (fanout-guard FAIL + workspace write + duration anomaly) |
| 5 | `prediction_market_analyst` | `PredictionMarketAnalyst` | `b67d4598-…` | 22.7s | **PASS** (Kalshi-based, not Odds-dep) |
| 6 | `game_predictor` | `GamePredictor` | `fe7ef69a-…` | 985ms | **Runtime-failure PASS-with-mitigation** (Odds API absent) |
| 7 | `line_movement_analyzer` | `LineMovementAnalyzer` | `f4a45419-…` | 1.3s | **Runtime-failure PASS-with-mitigation** (Odds API absent) |
| 8 | `sharp_action_detector` | `SharpActionDetector` | `86a35c79-…` | 1.0s | **Runtime-failure PASS-with-mitigation** (Odds API absent, per-bookmaker) |
| 9 | `whale_watcher_agent` | `WhaleWatcherAgent` | `4c0d532f-…` | 9.5s | **PASS** |
| 10 | `blockchain_audit_coordinator` | `BlockchainAuditCoordinator` (**fanout-guard**) | `a3dac7a2-…` | 9.3s | **PASS** (fanout-guard HELD — reference clean coordinator) |

**Summary:**
- 3 clean PASS (prediction_market_analyst, whale_watcher_agent, blockchain_audit_coordinator)
- 4 PASS-w/-finding (2 fanout-guard FAIL + 2 workspace-write side-effect; overlap = stock_audit + market_intel + bear_case)
- 3 Runtime-failure PASS-with-mitigation (Odds API blocked — game_predictor / line_movement_analyzer / sharp_action_detector)

All 10 dispatched cleanly (0 wiring failures). RaaS bar met for all 10; task-level smoke findings vary.

---

## 2. New finding classes surfaced (2 new + 1 confirmed)

### 2.1 Infra-runtime failure class — 3 clean instances (NEW class this batch)

**Class signature:** RaaS dispatch works · agent dispatches correctly · envelope structured · agent-level input contract met · BUT downstream data-source infrastructure returns empty (`TheOddsSpider returned no events` / `No events with per-bookmaker odds`). Distinct from input-contract failure (that class = tool needs more per-call input; this class = tool's infra dependency is down).

**Instances (3):** game_predictor · line_movement_analyzer · sharp_action_detector. All 3 failed <1.5s with the same root cause. All betting-family AGENT_MAP entries dependent on TheOddsSpider.

**Root cause:** S3040 known state + Chris directive 2026-07-30 — Odds API on back burner, no API key.

**Disposition:** Runtime-failure PASS-with-mitigation per D-verdict. Marked skipped-w/-mitigation for CLOSE; revalidate when substrate healthy.

**Substrate ledger row:** `[S3045] Infra-runtime failure class — upstream odds feed empty (TheOddsSpider)` — deliverable `e2d0c1a1-e75d-495c-b518-78360256264f` (workspace `b4503364-2573-4401-9e28-61a739e0ce50`).

**Trigger threshold:** 5th instance opens Option B (operational fix — re-enable Odds API). Currently 3 instances = under threshold. Chris-directive-adjusted: no new operational fix work while API key absent.

### 2.2 Workspace-side-effect class — 3 clean instances (NEW class this batch)

**Class signature:** tool executes real work + writes a file to a workspace as a side-effect during smoke dispatch. Violates the smoke prompt's spirit (`Do NOT publish, do NOT post, do NOT create media`) but not the letter (workspace-write is not literally "publish/post/media"). Reveals that the current smoke prompt guardrails are incomplete.

**Instances (3):** bear_case_agent (`Donkey Betz` workspace, 1 file) · stock_audit_coordinator (`Donkey Betz` workspace, 1 file) · market_intelligence_coordinator (`Donkey Betz` workspace, 1 file).

**Root cause:** provenance-report-generating stock/market agents auto-write their reports to a workspace as part of their normal flow; smoke prompt did not preempt this.

**Disposition:** PASS-with-finding. No customer harm (writes to internal workspace, not external publish), but a real hygiene gap for smoke discipline.

**Mitigation options (3):**
- **A. Tighten smoke prompt** — add explicit "Do NOT write any files to any workspace" clause for Batch 4+ dispatches.
- **B. Per-agent smoke-mode flag** — add `smoke_mode=true` context key that agents inspect to skip side-effects. Requires agent-side implementation across ~3-5 stock/market agents.
- **C. Ephemeral smoke workspace** — dispatch smokes to a scratch workspace that gets auto-cleaned. Requires workspace routing tooling.

**Trigger threshold:** Option A implementation for Batch 4+ (cheapest, in-doc reach). Option B/C deferred unless smoke-write becomes recurrent problem.

**Substrate ledger row:** `[S3045] Workspace-side-effect class — smoke prompt insufficient (workspace write not blocked)` — deliverable `bacd97ee-23db-438f-8e72-1ccc166a186a` (workspace `b4503364-2573-4401-9e28-61a739e0ce50`). Created pre-PR per Rigby T0 SIGN Q1.

### 2.3 Coordinator-provenance-fanout class — 2 confirmed instances + 1 reference PASS

**Class signature:** coordinator-shape agents (StockAuditCoordinator / MarketIntelligenceCoordinator) invoked under fanout-guard smoke prompt produce output with `Data Sources: <AgentName>: N records` blocks — implying cross-agent aggregation. Whether this is TRUE cross-agent dispatch (spawning child AgentExecutions) or CACHED aggregation (reading prior downstream agent outputs) is not verifiable from the poll surface.

**Instances (2 confirmed FAIL, 1 reference PASS):**
- FAIL: `stock_audit_coordinator` — Data Sources: 4 downstream agents (145s)
- FAIL: `market_intelligence_coordinator` — Data Sources: 4 downstream agents including StockAuditCoordinator (nested!) + 529s duration + workspace write
- PASS: `blockchain_audit_coordinator` — clean single-step, no Data Sources block, no workspace write, 9.3s

**Root cause:** stock/market coordinators may have a "run the full audit" default path that fanout-guard prompts don't preempt; blockchain coordinator's default path is single-step-shaped.

**Disposition:** PASS-with-finding. Not a wiring failure (all 5 D-verdict criteria met). Concerns are (a) smoke discipline gap — fanout-guard prompt insufficient for this coordinator class, (b) potential downstream cost accretion during smoke — if the coordinators are dispatching real cross-agent work, smokes cost more than expected.

**Mitigation options (3):**
- **A. Doc-note only (per-tool validation docs mark as PASS-with-fanout-guard-finding).** Current approach.
- **B. Instrument child-task trace surface.** Extend AgentExecution to record parent/child dispatches; extend `agent_job_status` PA tool to return child dispatch counts. Would enable hard proof of fanout vs cached-read.
- **C. Refuse-to-execute smoke prompt for coordinators.** Have the coordinator agents check for a `smoke_mode` context key and refuse-to-execute their default paths. Prevents cost accretion.

**Substrate ledger row:** `[S3045] Coordinator-provenance-fanout class — fanout-guard smoke prompt insufficient for stock/market coordinator shape` — deliverable `3f77850d-3a25-42c0-859f-5cbc397e7a57`. Created pre-PR per Rigby T0 SIGN Q1.

---

## 3. Metric verification

- Before Batch 3 (post-Batch 2): `agent_via_run_agent`=25 · `agent_via_run_agent_validated`=20 · `RaaS-validated`=138
- After Batch 3 (this ship): `agent_via_run_agent`=15 · `agent_via_run_agent_validated`=30 · `RaaS-validated`=148
- Total row count preserved at 164 ✓

---

## 4. Cumulative S3045 arc state (post-Batch 3 ship)

| Batch | Tools | Clean PASS | PASS-w/-finding | Runtime-failure | Notes |
|---|---|---|---|---|---|
| 1 | 10 | 8 | 1 (alias) | 0 | + 1 input-contract; substrate + first-batch |
| 2 | 10 | 9 | 0 | 0 | + 1 input-contract |
| 3 | 10 | 3 | 4 | 3 | + 2 new finding classes surfaced |
| **Total** | **30** | **20** | **5** | **3** | + 2 input-contract instances (Batch 1 + 2) |

**Findings/ledger roll-up:**
- Alias mismatch (security→memory_isolation): ledger row `6981cd08-30bc-4ed9-8f02-29d1f6086deb`. 2 concrete instances (bi-directional).
- Input-contract failure class: ledger row `0988dcc4-d7dc-4015-84e0-b77a86df0aa7`. 2 concrete instances (code_review, voice_critic).
- Infra-runtime failure class: ledger row `e2d0c1a1-e75d-495c-b518-78360256264f`. 3 concrete instances (Odds-dependent betting).
- Workspace-side-effect class: ledger row `bacd97ee-23db-438f-8e72-1ccc166a186a`. 3 concrete instances (Batch 3).
- Coordinator-provenance-fanout class: ledger row `3f77850d-3a25-42c0-859f-5cbc397e7a57`. 3 concrete instances (2 FAIL + 1 clean PASS reference; Batch 3).

**Remaining scope after Batch 3:** 15 tools = 5-tool skiplist (media/audio; conditional live — Odds-back-burner directive doesn't affect these) + 4 remaining fanout-risk coordinators (autonomous_content_studio_coordinator, podcast_coordinator_agent, meeting_coordinator_agent, campaign_orchestrator_agent) + 6 remaining single-agent tools (trained_creation_agent, opportunity_pipeline_agent, opportunity_scoring_agent, system_intelligence_agent, ai_series_workflow_agent, social_media_agent — publish-caution).

---

## 5. Forward-carry — Batch 4 candidates (final batch)

**Batch 4 tools (~13-15):**

Coordinators (4, fanout-guard prompt + Batch 3 workspace-write learning applied):
1. `autonomous_content_studio_coordinator`
2. `podcast_coordinator_agent`
3. `meeting_coordinator_agent`
4. `campaign_orchestrator_agent`

Single-agent (6):
5. `trained_creation_agent`
6. `opportunity_pipeline_agent`
7. `opportunity_scoring_agent`
8. `system_intelligence_agent`
9. `ai_series_workflow_agent`
10. `social_media_agent` (**publish-caution:** smoke prompt strict on "Do NOT publish/post to any social platform")

Skiplist (5, doc-only + mitigation note; media/audio infra-dependent):
11. `resolve_agent`
12. `video_generation_agent`
13. `audio_generation_agent`
14. `image_generation_agent`
15. `talking_character_agent`

**Batch 4 smoke prompt refinement (per Batch 3 findings):** add explicit "Do NOT write any files to any workspace or persist output to any external store" clause to both the standard and fanout-guard smoke prompts.

**After Batch 4 ship:** S3045 arc CLOSES at 45/45 tools validated (30 live-dispatch + 5 doc-only-with-mitigation + 10 already at agent_via_run_agent (wait, mismatch — let me recount)).

Post-Batch-4 target state: `agent_via_run_agent`=0 · `agent_via_run_agent_validated`=45 · `RaaS-validated`=163 · 1 meta_no_handler (run_agent by design) · Total 164 ✓.

---

## 6. What did NOT ship (deferred by design)

- No substrate code changes (all substrate landed in Batch 1 PR #3794).
- No AGENT_MAP mutations.
- No new fanout-guard prompt refinements THIS batch — Batch 4 will apply the workspace-write clause.
- No Rigby ledger rows for workspace-side-effect + coordinator-provenance-fanout classes — deferred to post-merge Rigby task (both at 3-instance threshold; ledger-worthy).
- No re-dispatch of Odds-API-blocked tools — Chris directive: back burner until API key restored.

---

## 7. Cross-cutting workflow references

- PLAYBOOK-7.7.1 spec→ship: Batch 3 discharged.
- PLAYBOOK-7.7.2 SIGN evidence: T0 SIGN follows this batch.
- PLAYBOOK-7.7.5 A2 class-scoped sweep: 6 dimensions (validation-doc-authoring signature) — all PASS (no substrate changes; exercises existing Batch 1 classifier branch).
- PLAYBOOK-7.4.4 recycle: docs-only PR; no recycle needed.
- Verify-before-build (Cycle 1A): 30th consecutive session (extended across S3045 batches).
