---
session: 1704
status: closed (Group 1700 Cat D ToolCallRecord child audit LANDED — FOURTH child under Group 1700 per parent D72 P4 slot; audit doc landed `status: active` post-fold; Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence on arc pin `pa-e7fbacc996b34b44` — fresh SIGN isolation pin `pa-f7417e6ac21d4f23` minted per playbook §15 but routed-around by `tools/pa_local.sh:128` wrapper hard-code (S1600/S1700/S1701/S1702/S1703 precedent: arc pin doubles as SIGN pin); fresh SIGN pin retired at S1704 close per §16 (`updated_count=1, retired=true`); F1-F4 folds landed pre-commit; D48 preemptive stability-probe gate 21st arm HOLDING CLEAN — 16-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+S1703+S1704 CONFIRMED per single-batch-4-question criterion; ARCHITECTURE_INDEX v46 → v47 with §1.50 S1704 registration + §8 timeline S1704 row + line-6 v47 preamble; OPEN_ARCS Group 1700 In-progress row current-child updated S1703 → S1704; arc pin retained through Group 1700 close at S1799; next session: S1705 Cat E OpsRunEvent per D72 P5 slot)
date: 2026-07-03
arc: Research Group 1700 (Observability / Telemetry / SLOs) — Cat D ToolCallRecord child audit; FOURTH child session under Group 1700 per D72 P4 slot
category: research (playbook §11.2 child audit template + §13 six-parallel-Explore + §14 verifier-loop + §15 SIGN cycle 1)
head_commit_before: 410a43ab (main; post-S1703 arc-open merge + RAG cascade refresh)
head_commit_after: (this commit)
authors: Claude Code (Chris directed via short command "Start research group 1704")
---

# Session 1704 — Group 1700 Cat D ToolCallRecord Child Audit

> **Fourth child audit under Group 1700 (Observability arc).** Playbook §11.2 20-section template FOURTH application under Group 1700 arc (first was S1701 Cat A CeleryTaskEvent; second was S1702 Cat B LLMCallEvent; third was S1703 Cat C AgentExecution). 6-parallel-Explore sweep + parent-Claude verifier-loop applied both pre-Explore and post-Explore. Rigby SIGN cycle 1 delivered SIGN-with-edits at Medium-High confidence via single-batch 4-question pattern (D48 21st arm HOLDING CLEAN — 16-consecutive-fully-clean-arms sub-pattern confirmed).

## What shipped

### 1. Audit doc

- **`docs/research/domains/observability/1704_observability_cat_d_tool_call_record_audit.md`** (NEW; ~1050 lines post-fold)
- `status: active` after Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence
- `authority: child-audit`, `category: child_audit`, `session: 1704`, `child_slot: P4`, `domain_slug: observability`, `research_group: 1700`
- Applies playbook §11.2 20-section child audit template + §13 6-parallel-Explore + §14 verifier-loop discipline (both pre-Explore and post-Explore)

### 2. Rigby SIGN cycle 1 folds (F1-F4, all landed pre-commit)

- **F1 (Medium) — §1.1 F9 + §9.2 spine bottom-line wording tightened** — Replaced "negative evidence on all four options equally" with "blocks all options; actively broken for Option B today (100% NULL trace_id)" plus explicit distinction between Cat D's Option B posture (broken-not-blocked) vs Option A posture (incomplete-not-broken). Also added spine-lift decomposition note that Option B's smaller schema lift does NOT reduce coordination lift below Option A's.
- **F2 (Low) — §14 drift severity escalation + new drift row** — D7 (`tool_call_id` HYPOTHESIS refuted) escalated MEDIUM → HIGH per Rigby's rationale "upstream references to non-existent Cat D correlation columns directly misguide cross-cat dedup work — more dangerous than doc omissions." New drift row **D9 (HIGH)** added for the parent §3.B accounting-rule column-set citation (execution_id + trace_id + tool_call_id when Cat D has ZERO schema-enforceable) — companion drift.
- **F3 (Low) — §1.1 F9 + §9.2 spine-lift decomposition** — Explicit "schema lift vs coordination lift" decomposition for Option B. Column-exists-and-is-indexed advantage preserved as evidence, but coordination lift (three-writer trace_id thread-through + dispatcher UUID format overhaul + PA loop pa-N-hex→UUID transform) is called out as equivalent to Option A's cost.
- **F4 (Low) — §19 R2 gating-prerequisite addendum** — R2 (F1 trace_id write coverage repair) explicitly marked as the **gating prerequisite** for any Option B posture evaluation ("If xx99 wants to keep Option B viable, R2 is the immediate gate before any posture comparison can be meaningfully evaluated"). Distinguishes R1 (xx99 posture decision) from R2 (F1 repair) in dependency order.

### 3. Nine load-bearing findings (§1.1 Executive Summary)

- **F1 (CRITICAL, §17)** — 100% NULL trace_id at 4144 rows at HEAD (ORM-verified 2026-07-03). Three writer paths all hardcode trace_id=None: dispatcher at `tool_dispatcher.py:961` (comment: "dispatcher trace_id 'td-N-hex' isn't a UUID"), S970 wrapper at `base_agent.py:451-459` doesn't thread trace_id, BaseAgent default's inline recorder at `base_agent.py:3302-3310` also doesn't. Kills S1703 F9 Option B (trace_id spine) at runtime + kills `deliverable_provenance.py:105` chain empirically for every deliverable.
- **F2 (HIGH, §17)** — ToolCallRecord has NO `execution_id` + NO `tool_call_id` + NO `call_id` + NO `celery_task_id` + NO `task_id` columns. Only correlation candidates are `trace_id` (F1 empty), `conversation_id` (21.9% populated, PA subset), `agent_name` (semantic string match, 39 distinct values). Confirms S1702 F9 + S1703 F6 accounting-rule enforceability gap from Cat D side.
- **F3 (MEDIUM, verifier-loop corrected, §14+§17)** — Pre-Explore prior "31 unwrapped agents write ZERO rows" was OVERSTATED. Post-Explore verifier correction: 31 AGENT_MAP agents inherit BaseAgent's default `_execute_tool_call` at :3168-3316 — the default has its OWN `finally`-block writer at :3302 (S1085 pattern tagged at :3188 — "Record built-in tool calls (wrapper only catches subclass overrides)"). Empirically 29 of 31 base-inherited agents show 0 rows at HEAD — an idle/pure-LLM-agent distribution, NOT a coverage-mechanism bug.
- **F4 (MEDIUM, §17)** — `analyze_pa_tool_patterns` (`core/tasks.py:12375` → `tasks_agents.py:6124`) + `aggregate_tool_call_stats` (`core/tasks.py:8282` → `tasks_ops.py:3325-3386`) both DEFINED as `@shared_task`, both queue-routed via settings.py:1294 + :1580, but NEITHER in `core/celery.py` beat schedule NOR present in `PeriodicTask` table (0 matches). Consequence: PAToolInsight=0 rows + ToolCallAggregate=0 rows at HEAD. WRITE-ONLY-FORGOTTEN pattern from Group 1500 F.B3 reproduces here.
- **F5 (MEDIUM, §15)** — No date-based retention for any of the three Cat D tables. Cat A precedent (`CELERY_TASK_EVENT_RETENTION_DAYS`) exists; Cat B has watchdog but no retention (S1702 F4 HIGH); Cat D has neither. 4144 rows over 20 days extrapolates to ~73k rows/year at current cadence — bounded but unaudited for burst behavior.
- **F6 (POSITIVE differentiator vs S1703 F4, §7+§9)** — PA path DOES write 907 ToolCallRecord rows (22% of total) via `ToolDispatcher.execute(agent_name='PersonalAssistant', conversation_id=…, pa_trace_id=…)` invoked from `unified_pa_entrypoint.py:1830+`. **Material Cat D vs Cat C difference**: S1703 F4 (CRITICAL) reported Cat C zero PA coverage; Cat D has partial PA coverage via the dispatcher. All 907 PA rows still have `trace_id=NULL` per F1, and `conversation_id` populated only on this subset.
- **F7 (LOW, §17)** — Two dead-writer methods verified via zero-caller grep: (a) `unified_pa_entrypoint._record_tool_call:2096-2140` docstring at :2111-2117 explicitly marks DEPRECATED per S1115 finding 17 closure; (b) `BaseAgent._execute_and_record_tool_call:3317-3371` (S861 explicit-trace_id path) — grep across `core/` returned only definition + docstring reference; all agent subclasses call `self._execute_tool_call(tool_name, arguments)` directly. Both retained per `feedback_verify_before_deleting_dead_code.md` memory rule.
- **F8 (LOW, §14+§17)** — No Django admin registration for ToolCallRecord / ToolCallAggregate / PAToolInsight (grep `core/admin*.py` → 0 matches). Analog to Cat C T-11 (S1703 §15).
- **F9 (D74 axis contribution, §9)** — Cat D **blocks all four spine-posture options** unless a primitive is populated at write time. Cat D is **actively broken for Option B today** (trace_id column exists + indexed but 100% NULL empirically — any trace_id-based join is dead-on-arrival). Cat D is **incomplete-not-broken for Option A** (execution_id column absent — schema absence rather than runtime failure). Options C/D inherit the same prerequisite. Option B has smallest schema lift (column exists + indexed) but the coordination lift is equivalent to Option A's (dispatcher UUID generation + wrapper trace_id threading + PA loop pa-N-hex→UUID transform). This is the load-bearing Cat D evidence for the xx99 posture decision.

### 4. Rigby CONFIRM verdicts (no folds required beyond F1-F4)

- **Q1 coverage-completeness High** — F1-F9 correctly scoped to Cat D boundary per parent §3.D; no split/merge needed; no missing CRITICAL/HIGH finding at HEAD; F9 correctly kept as D74-axis contribution rather than separate system bug.
- **Q2 drift-severity Medium-High** — D7 REFUTED tool_call_id hypothesis framing correct; escalation to HIGH landed via F2 fold + companion D9 added.
- **Q3 D74 axis correctness Medium-High** — Core conclusion right (Cat D provides strongly negative evidence on Option B as currently implemented); wording tightening only (landed via F1 fold).
- **Q4 R1-R12 ranking + xx99 scope discipline Medium-High** — R1/R2/R4/R5 ordering defensible; R3 dark-pipeline reactivation stays in Cat D scope (own tiered pipeline, not Group 1900 territory); R2 gating flag added via F4 fold.

### 5. Nine ORM-verified evidence points (§20.4)

- ToolCallRecord total rows: **4144**.
- `trace_id NOT NULL: 0 (0.0%)` — F1 evidence.
- `conversation_id NOT NULL: 907 (21.9%)` — F6 evidence + writer-path artifact.
- Distinct `agent_name` values: **39** in 4144 rows.
- Top 10 agent_name: `ResearchAgent (2389)`, `PersonalAssistant (907)`, `TrendAnalysisAgent (193)`, `COOAgent (112)`, `CustomerResearchAgent (60)`, `CompetitorAnalysisAgent (59)`, `MarketMovementMonitorAgent (54)`, `MarketAnomalyDetectorAgent (49)`, `StockAnalystAgent (41)`, `InstitutionalWatcherAgent (28)`.
- Top 10 tool_name: `intelligence_tool (1266)`, `web_search (975)`, `spider_query (695)`, `deliverable_tool (160)`, `repo_tool (116)`, `ops_tool (79)`, `delegate_to_specialist (66)`, `get_operations_snapshot (50)`, `spider_status_tool (50)`, `blog_tool (41)`.
- Success/Failed: **3579 / 565** (13.6% failure rate).
- ToolCallAggregate total rows: **0** — F4 evidence.
- PAToolInsight total rows: **0** — F4 evidence.
- Base-inherited (31 agents) with ANY ToolCallRecord rows: **2 of 31** (`TopicMinerAgent=10`, `AutonomousContentStudioCoordinator=1`) — F3 evidence.
- Beat schedule entries for `analyze_pa_tool_patterns` / `aggregate_tool_call_stats` / `tool_call` / `ToolCall`: **0** — F4 evidence.
- Oldest row: **2026-06-13 00:27:02 UTC**; Newest: **2026-07-03 13:32:13 UTC** (20 days of data, ~200 rows/day).

### 6. Arc-close artifacts

- **`docs/research/ARCHITECTURE_INDEX.md`** — v46 → v47 with §1.50 S1704 registration + §8 timeline S1704 row + line-6 v47 preamble.
- **`docs/research/OPEN_ARCS.md`** — Group 1700 In-progress row current-child updated S1703 → S1704 + line-6 preamble bumped.
- **`00-START-NEXT-SESSION.md`** — overwritten with S1705 Cat E OpsRunEvent next-mission spec per D72 P5 slot.

### 7. Session mechanics

- **Arc pin:** `pa-e7fbacc996b34b44` (Group 1700 arc pin; retained through Group 1700 close at S1799).
- **S1703 retire owed at S1704 open:** Retired at S1704 open — `pa-f1a30b7ed5bb4042` (unused SIGN pin from S1703). Result: `retired=true, updated_count=1`.
- **Fresh SIGN isolation pin for S1704:** `pa-f7417e6ac21d4f23` (minted per playbook §15; routed-around by `tools/pa_local.sh:128` hard-code — retired at S1704 close per §16 with `updated_count=1, retired=true`).
- **Local verified:** `service_context: local` confirmed via `platform_config_tool overview` (D48 21st arm start).
- **Single-batch 4-question SIGN pattern held clean** — **16-consecutive-fully-clean-arms sub-pattern** S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+S1703+S1704 CONFIRMED. Codification-ready-STRENGTHENED-EVEN-FURTHER for playbook v3 §15.

### 8. Post-arc queued items (Cat D-scope additions to xx99 tranche)

- **From S1704 §19:** R1 (HIGH, load-bearing for xx99) F9 D74 axis posture decision + R2 (HIGH) F1 trace_id write coverage repair — gating prerequisite for Option B posture + R3 (HIGH) F4 mining + aggregation pipeline reactivation (Cat D-internal scope) + R4 (MEDIUM) F2 schema-level correlation columns (execution_id + tool_call_id) + R5 (MEDIUM) F5 retention policy + R6 (MEDIUM) F3 base-inherited-agent activity audit + R7 (MEDIUM) F6 conversation_id backfill + R8 (MEDIUM) T-7 PA history tool + R9-R12 LOW.
- **From S1704 §14:** D1 LOW parent §3.D 74-agent count drift + D2 MEDIUM agent-system.md :107-113 S970 coverage-claim omits Flow 2/3 + D3 MEDIUM personal-assistant.md omits F6 PA path coverage + D4 LOW PLATFORM_INVENTORY no per-model row count + D5 LOW PLATFORM_WHAT_IT_IS narrative-thin + D7 HIGH parent §5 `tool_call_id` HYPOTHESIS refuted + D8 LOW PAToolInsight docstring dedup contract not schema-enforced + D9 HIGH parent §3.B accounting-rule column-set citation (execution_id + trace_id + tool_call_id) — all owed to xx99 anchor-update PR.
- **From S1704 §20.5:** UNK-1 non-BaseAgent overrides production status + UNK-2 NotImplemented error_type genuinely eliminated vs retention-window-invisible + UNK-3 480MB spike note currency + UNK-4 pa_tool_learning_enricher.py existence + UNK-5 out-of-band task triggers.

## Next session

**S1705 Cat E OpsRunEvent child audit per D72 P5 slot** — inherits F4 WRITE-ONLY-FORGOTTEN pattern extended to MissionRunner aggregation surface (does MissionRunner + Ops Autopilot have same beat-schedule-absent pattern for OpsRunEvent aggregation surface?) + F1 100% NULL trace_id extends to Employee OS `evidence_for_mission` join at `docs/topics/employee-os.md:64-65` (same trace_id semantic-join failure predicted from Cat E side) + OpsRun `mission_id` spine candidate per parent §5 F5 correlation-primitive table + MissionRunner does NOT thread tool telemetry through OpsRunEvent per Cat D E4 finding + WRITE-ONLY-FORGOTTEN mirror detection per Group 1500 §14.3 precedent. Cat E depends on P1 + P2 + P3 + P4 evidence per parent §5 sequence — inherits full arc context. See `00-START-NEXT-SESSION.md`.
