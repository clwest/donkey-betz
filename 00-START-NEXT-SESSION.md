# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=19f3b711b2b1995255c5cc0e4182e085423c6557 \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm the response includes `service_context: local`.** Don't trust conversation IDs to tell you which instance — the same IDs can exist on both prod and local with different histories.

---

**Date:** April 16, 2026 (end of Session 1092)
**Previous session handoff:** [`docs/handoffs/SESSION_1092_GOVERNANCE_NOISE_AND_AGENT_PERSISTENCE.md`](docs/handoffs/SESSION_1092_GOVERNANCE_NOISE_AND_AGENT_PERSISTENCE.md)
**Previous session PA conversation (LOCAL):** `pa-3966231ba0d140e7` — Chris creates a new one each session, so ask him for the new ID before your first Rigby message.
**Status:** 11 PRs merged (#1972–#1981) covering governance noise reduction, full Rigby→Agent→Deliverable canary loop closure, and platform reliability (~9.7% → projected ~4% failure rate). Canary v8 step 1 was in flight at session boundary — verify first thing.

---

## SESSION 1089 — What Was Accomplished (7 PRs: #1938–#1944)

| PR | Title | Impact |
|----|-------|--------|
| **#1938** | Governor activation + noise cleanup | 43 beat tasks disabled, daily budgets set, work_tool schema fix |
| **#1939** | build_feature timeout fix | 90s→300s per-request timeout (PA tool SLO) |
| **#1940** | Spider search raw_data fix | 0-result bug fixed — now searches actual content |
| **#1941** | Governor gate on bypass paths | 4 dispatch paths (autopilot, status, research, content) now gated. Fixed $25 overnight spend. |
| **#1942** | PlatformContextService + CTOAgent | New service (8 methods + snapshot), CTO grounded with real tools |
| **#1943** | Workspace multi-active fix | Activation now deactivates others properly |
| **#1944** | COOAgent grounding | 3 hardcoded stubs → 3 PCS-backed real tools |

### Key infrastructure built:
- **PlatformContextService** (`core/services/platform_context_service.py`) — 8 methods querying real DB data. Any agent can call it.
- **Beat Governor** — live with `BEAT_GOVERNOR_ENABLED=true`, 5 missions, daily budgets
- **Spider search** — now returns real results across all 73 active spiders

---

## SESSION 1090 — What Was Accomplished (12 PRs: #1946–#1961)

| PR | Title | Impact |
|----|-------|--------|
| **#1946** | ContentWriter error propagation + AISeriesWorkflow timeout caps | Real errors visible, zombie executions eliminated |
| **#1947** | Demo Autonomy Mode + EditorAgent brief fallback | 15-agent allowlist, 30/hr cap |
| **#1948** | Demo mode banner + runbook + API | UI banner, `/api/system/demo-status/` |
| **#1949** | PA payload context promotion | workspace_id/content_type/tone flow to agents |
| **#1950-#1956** | EditorAgent + ContentWriter workspace plumbing (7 PRs) | Workspace content injection, active workspace fallback, blog exclusion |
| **#1951** | MetricsActionTrigger governor gate + Redis cooldown | Stopped hourly SystemIntelligence spam |
| **#1957** | Demo runbook v2 — correct agent roles | SystemIntelligenceAgent for status |
| **#1958-#1961** | PlatformAuditAgent output quality (4 PRs) | Prose output, gpt-5.2, fallback formatter |

### Key accomplishments:
- **Demo Autonomy Mode** — `DEMO_MODE=true` gates all agents to 15-item allowlist
- **"A Platform That Knows Itself"** narrative validated — 5 agents producing real ops artifacts
- **Agent role corrections** — right agent for each job (Writer writes, Editor QAs, SystemIntel synthesizes)
- **14 real issues found by agents** — fix list created for Session 1091
- **Full dry run passed** — PlatformAudit(20s) + CTO(32s) + COO(35s) + SystemIntel(61s) + ContentWriter(173s)

---

## SESSION 1092 — What Was Accomplished (11 PRs: #1972–#1981)

| PR | Title | Impact |
|----|-------|--------|
| **#1972** | Governance noise gates (StockAudit + Fed Alert) | Killed top 3 critical attention items + Fed Alert spam cluster |
| **#1973** | `deliverable_tool.detail` workspace fields | `is_orphan` was always `true` because detail dropped `workspace_id`. workspace-flow-canary unblocked |
| **#1974** | `run_agent` schema `workspace_id` param | Rigby can target workspaces structurally — closes the agent dispatch loop |
| **#1975** | ResearchAgent keyword extraction (3 layered bugs) | Real research instead of "alex anal balanced based" garbage queries |
| **#1976** | ContentStrategyAgent else-branch persistence | Conversational replies now persist (was silently dropping) |
| **#1977** | ContentStrategyAgent content serialization | Tool_calls branch no longer fails 300-char gate |
| **#1978** | Shared BaseAgent renderer + 10-agent migration | `_render_agent_output_markdown` covers VideoAgent, AudioAgent, ImageEditingAgent, etc. — systemic MESSAGE-ONLY fix |
| **#1979** | EditorAgent dispatcher fallback | 8/9 EditorAgent fails recovered. **Editor only edits — fail-loud preserved** (Chris's framing) |
| **#1980** | ThinkingAgent `re` shadowing | UnboundLocalError from in-function `import re` shadowing module-level. One-line removal |
| **#1981** | `AgentControlEntry.blocked_at` hygiene + backfill | CTOAgent forensics unblocked. `save()` override + management command |

### Key infrastructure built / changed:
- **`core/services/editor_dispatch_helpers.py`** — shared `gather_workspace_content_for_editor()`. Used by both PA tool dispatch AND conversation action dispatch (was missing from the latter).
- **`BaseAgent._render_agent_output_markdown(...)`** — generic content renderer that always produces >300 chars for non-trivial output. Replaces 10 agents' broken `content=result.message` pattern.
- **`AgentControlEntry.save()` override** — auto-populates `blocked_at` on transition non-blocked → blocked. Plus backfill management command for legacy rows.
- **Expanded STOPWORDS in `search_strategy_service.py`** — 40+ instruction-meta words filtered.
- **`tune_fed_alert_triggers` management command** — idempotent. Apply on Railway after deploy.
- **`backfill_agent_control_blocked_at` management command** — idempotent. Apply on Railway after deploy.

### CTOAgent diagnostic primitive validated (queued for Session 1093):
CTOAgent queries live `AgentExecution` data and produces accurate platform analyses. Verified within 2% on totals, success_rate, top-N agents. Chris: *"if these are real issues this might be the best way to address them."* Operationalize as scheduled diagnostic in Session 1093.

### Platform failure rate trajectory:
9.7% → ~6.5% (AudioAgent block aging out) → ~5.1% (post #1979) → ~4.4% (post #1980) → **~4% projected steady-state** (60% reduction from session start)

### Tests added:
8 new test files / ~50 tests, all passing. Full regression sweep clean.

### Patterns learned worth carrying forward:
- **EditorAgent fail-loud principle**: caller-side fixes only. Don't mask caller bugs at the agent layer.
- **SAFE vs TRUE_BUG audit refinement**: pattern-grepping flags candidates; live runtime check confirms. (10 of 23 MESSAGE-ONLY were actually broken; 13 were fine.)
- **In-function imports shadow module-level imports** for the whole function — even in never-taken branches. Watch for `UnboundLocalError` on a name that's already imported at the top.
- **CTOAgent as scheduled diagnostic primitive** — agent that synthesizes from live DB is accurate and actionable.

---

## SESSION 1091 — What Was Accomplished (7 PRs: #1963–#1969)

| PR | Title | Impact |
|----|-------|--------|
| **#1963** | Router wall-clock + heartbeat hardening | Closes the direct-router-bypass class of timeouts. Shared `core/services/agent_timeouts.py`. Heartbeat thread survives 3 transient DB errors instead of dying on first. |
| **#1964** | build_feature timeout + gpt-5.2 | All 6 prior 24h PA-tool failures were APITimeoutError at ~271s. Bumped read to 600s, migrated to gpt-5.2. |
| **#1965** | Close orphan paths + workspace_id observability | Three smoking guns closed: deliverable_tool list now exposes workspace_id/workspace__name/is_orphan, clone_deliverable inherits workspace + initiative, factory routes fallback to per-user "Unassigned" sentinel bucket. **Orphan rate now zero by construction.** |
| **#1966** | PA schema orphans param + version-hash fix | `orphans=true` filter now in PA tool schema. Schema-version hash now includes parameter shape (was tool-names only) — schema changes auto-reload. |
| **#1967** | UI workspace badges + Unassigned triage marker | Deliverables cards render workspace badge (red/amber/blue per state). WorkspaceSelectorModal sorts Unassigned to top with amber styling + "Triage" label. REST serializer extended to match. |
| **#1968** | Alias workspace__name → workspace_name | Cross-channel field-name parity (PA tool used Django ORM .values double-underscore key, REST used dict-style). One-line alias in `_sanitize_deliverable`, backwards compatible. |
| **#1969** | Per-workspace stats breakdown + UI card | Adds `by_workspace`/`orphan_count`/`unassigned_count` to both REST stats and PA tool stats. New "Workspace Breakdown" card in DeliverablesTab. Distinct metrics for orphan (regression alarm) vs unassigned (informational). |

### Key infrastructure built / changed:
- **`core/services/agent_timeouts.py`** — single source of truth for per-agent timeouts. `tasks_agents` and `agent_router` both import `get_agent_timeout()`.
- **Unassigned sentinel workspace** — `_get_or_create_unassigned_workspace_id(user)` lazy-creates per-user `ProjectWorkspace` named `"Unassigned"` with `allow_autonomous_writes=True`. Orphans stop being possible.
- **`router_wall_clock` failure signature class** — replaces `TIMEOUT_WATCHDOG_CLEANUP_*` for direct router callers. If a watchdog signature appears on a fresh execution, that means a dispatch path is bypassing both Celery wrapper AND router — investigate.
- **Schema-version hash now includes parameters** — adding/changing PA tool params correctly bumps `SCHEMA_VERSION` and triggers `_get_live_tool_schemas` to reload without process restart.

### Deliverables saved (Donkey Betz workspace):
- `ac87f650` — Session 1091 Follow-ups (six grooming-ready tickets)
- `b71f14a4` — Deploy Broadcast (cutoff timestamp + agent-context guidance)
- `a4b00a82` — SOP v1: Executability Verification Checklist (5-test pass/fail)
- `0f018ec8` — UI Visibility Audit (closed with full Sprint A → A.5 → B → soak verification)

---

## SESSION 1093 — PRIORITIES

### 1. Verify canary v8 (in-flight from Session 1092)
ResearchAgent step 1 dispatched at 2026-04-17 01:28:57 UTC, execution_id `18f7a2eb-07e4-4c99-917c-bc567e4d385b`. Verify it completed cleanly and a deliverable landed in workspace-flow-canary (`af61c625-2cf1-4e70-82b2-d44e301f897e`). Then dispatch **Step 2 EditorAgent without content/blog_id in context** to prove the dispatcher-side workspace gather (#1979) auto-injects Step 1's deliverable. Acceptance: both deliverables status=ready, content_len>300, EditorAgent's content references ResearchAgent's findings.

### 2. Operationalize CTOAgent as scheduled diagnostic (Chris's request)
Wire CTOAgent as a daily Celery beat task. Agent already produces accurate platform analyses from live data (verified Session 1092 — within 2% on totals/success_rate/top-N). Files to touch: `core/tasks.py` (new beat task), use `execute_agent_task.delay`, post output to governance inbox via `attention_bridge` as `daily_reliability_report` attention item. Anomaly thresholds: only post when failure_rate >X% or top-N failure count exceeds Y. Don't spam — daily cadence + threshold-gated.

### 3. Apply migrations + tune commands on Railway after auto-deploy lands
Both pending until prod parity verified:
- `python manage.py tune_fed_alert_triggers` (Session 1092 #1972)
- `python manage.py backfill_agent_control_blocked_at` (Session 1092 #1981)

### 4. Carryforward from Session 1092 (small follow-ups, ~30 min each)
- VoiceCriticAgent: `content` parameter not in PA tool schema — GPT-5.2 strips it. Add to schema (mirror #1974 pattern).
- `code_review_agent` PA tool registration gap — not in tool_dispatcher's `register()` calls.
- `base_agent.py:4100` accesses `deliverable.id` even when create_deliverable returned None — add None-check.
- ThinkingAgent: if post-#1980 the `AgentResult` UnboundLocalError surfaces (was masked by `re` firing first), apply same one-line fix template.

### 5. Verify Railway prod parity (Session 1091 carryforward — STILL OPEN)
Auto-deploy was stuck on April 13 build at end of Session 1091 and end of Session 1092. Both sessions' PR merges aren't on prod yet. Manual investigation in Railway dashboard needed: failed/queued/cancelled builds, GitHub→Railway webhook status, trial/billing.

### 6. Verify Railway/prod migration parity
Local has 41 unapplied migrations from 0292+ through 0331. Run `db_health_tool.migrations` on Railway, compare. Document local-only-state via "no fake on prod" policy note if same backlog.

### 7. Address Session 1091 follow-ups (carryforward, medium priority)
From deliverable `ac87f650`:
- Audit LLM client construction for explicit request timeouts (fail fast at socket layer)
- Decompose `build_feature` into per-component subtasks (~1 day)
- Governor budget gate for FullStackDeveloperAgent (block monster-prompt patterns)
- Build `tool_calls_tool.list_failures` PA tool (avoid Django shell round-trips)

### 8. Carryforward from Session 1090 (still open)
- DEBUG=False on Railway (P0 verify)
- AudioAgent ElevenLabs quota refresh (Chris business decision)
- OpportunityPipelineAgent circuit breaker investigation
- CodeGeneratorAgent stale block (1051.6h) — autopilot keeps surfacing it; either add TTL or unblock
- content.0046 migration unapplied

### 9. Demo recording (deferred from Session 1090/1091)
Demo runbook: `docs/playbooks/DEMO_HAPPY_PATH.md`. Workspace: `demo-testing`. Pre-conditions for Session 1091 are now satisfied (timeout SLO closing, build_feature failures resolved). Session 1092 added more polish (governance inbox quieter, agent persistence stable).

### 10. Patent Portfolio + Brand Strategy (carryover, no progress this session)
Top candidate: "Governed Autonomy Control Plane." Governance-layer patent needs full write-up. Workspace: "Patent Portfolio — 2026 Refresh" (deactivated, data preserved).

---

## OBSOLETE — SESSION 1092 PRIORITIES (now archived in handoff)

### 1. Verify Railway prod parity (post-soak)
Run the SOP v1 checklist (deliverable `a4b00a82`) against Railway prod URLs. The 7 PRs merged staggered between 20:21 UTC and 21:36 UTC; Railway auto-deploy should have settled by next session start. Specifically confirm:
- `deliverable_tool.list` returns `workspace_id`, `workspace_name`, `workspace__name`, `is_orphan` per row
- `deliverable_tool.list(orphans=true)` accepts the new param and returns expected count
- `deliverable_tool.stats` returns `by_workspace`, `workspace_orphans`, `workspace_unassigned`
- 24h SLOs trending green as the pre-merge zombie executions age out
- New `TIMEOUT_ROUTER_WALL_CLOCK_*` signature class registers (and `TIMEOUT_WATCHDOG_CLEANUP_*` rate drops to ~0)

### 2. Verify Railway/prod migration parity (Session 1091 follow-up #1)
Local has 41 unapplied migrations from 0292+ through 0331 (`outreach_draft`, `close_pack`, `engagement_event`, `meeting`, `kill_switch`, `code_runner`, `vip_invite`, `llmcalllog_trace_id`, etc.). Run `db_health_tool.migrations` on Railway, compare. If prod has the same backlog, file separate remediation. If prod is current, document the local-only nature in a "no fake on prod" policy note.

### 3. Address Session 1091 follow-ups (medium priority, not blocking)
From deliverable `ac87f650`:
- Audit LLM client construction for explicit request timeouts (fail fast at socket layer)
- Decompose `build_feature` into per-component subtasks (~1 day)
- Governor budget gate for FullStackDeveloperAgent (block monster-prompt patterns)
- Build `tool_calls_tool.list_failures` PA tool (avoid Django shell round-trips)

### 4. Carryforward from Session 1090 (still open)
Most of these are addressed or queued via above; remaining real blockers:
- **DEBUG=True on production** — must be False for Railway (carryover P0; verify in `.env` on Railway)
- **AudioAgent blocked** (ElevenLabs quota exhausted) — needs quota refresh or alternate provider
- **OpportunityPipelineAgent** circuit breaker tripped — needs investigation
- **CodeGeneratorAgent** stale block (1051.6h) — autopilot keeps surfacing it; either add TTL or unblock
- **content.0046 migration** unapplied (one of the 41 above)

### 5. Demo recording (deferred from Session 1090)
Demo runbook: `docs/playbooks/DEMO_HAPPY_PATH.md`. Workspace: `demo-testing`. Pre-conditions for Session 1091 are now satisfied (timeout SLO closing, build_feature failures resolved).

### 6. Patent Portfolio (carryover, no progress this session)
Fresh audit done (post-governance, pre-Session-1091). Top candidate: "Governed Autonomy Control Plane." Governance-layer patent needs full write-up. Workspace: "Patent Portfolio — 2026 Refresh" (deactivated, data preserved).

### 7. Brand & Business Strategy (carryover, no progress this session)
Platform is a "governed intelligence OS" — not GPT wrapper, not betting app. Business model open: Intelligence-as-a-Service (fastest revenue), Governed Agent Platform (CrewAI killer), Vertical SaaS (pick a market once pull is found).

---

## AGENT STATUS SNAPSHOT (from full audit)

### Top Performers (demo-ready)
| Agent | 24h Runs | Success | Notes |
|-------|----------|---------|-------|
| ResearchAgent | 121 | 87% | Workhorse — spider + web search |
| CompetitorAnalysisAgent | 56 | 98% | Spider-grounded |
| ImageAgent | 36 | 100% | Real API |
| OpportunityScoringAgent | 28 | 100% | Real SpiderData scoring |
| ContentStrategyAgent | 24 | 100% | Strategy synthesis |
| TrendAnalysisAgent | 16 | 100% | Real intelligence_service |
| CTOAgent | 6 | 100% | NOW grounded via PCS |
| COOAgent | 4 | 100% | NOW grounded via PCS |

### Needs Fixing
- ContentWriterAgent: 64% (fix before video)
- AISeriesWorkflowAgent: 43% (fix before video)
- AudioAgent: 0% (blocked — ElevenLabs quota)
- OpportunityPipelineAgent: circuit breaker tripped

### Never Executed (10 agents)
EditorAgent, PlatformAuditAgent, PromptEngineeringAgent (keep — add triggers), BookmakerAgent, DistributionAgent, GamePredictor, LineMovementAnalyzer, SharpActionDetector, TalkingCharacterAgent, VoiceCriticAgent (disable for now)

### Blocked
- AudioAgent: ElevenLabs quota exhausted
- CodeGeneratorAgent: No codebase access in Railway sandbox

---

## GOVERNOR STATE

- **BEAT_GOVERNOR_ENABLED=true** (in .env, loaded by workers)
- **PRIORITY_ROUTER_ENABLED=true** (in .env)
- **5 active missions:**
  1. Platform Operations (unlimited)
  2. Content & Creative (8/day)
  3. Intelligence & Research (15/day)
  4. Revenue & Compliance (5/day)
  5. Agent Data Grounding: Facts Not Fiction (50/day, 72h TTL)
- **262 enabled beat tasks** (43 disabled — noise tasks)
- **Trigger sources bypassing governor:** `user_chat`, `user`, `pa_tool`, `direct`
- **Trigger sources gated:** `schedule`, `workspace_autopilot`, everything else

---

## ENVIRONMENT STATE

```bash
# Start stack
make start && make celery

# Talk to LOCAL Rigby
PA_API_URL=http://localhost:8000 PA_API_TOKEN=19f3b711b2b1995255c5cc0e4182e085423c6557 \
  .venv/bin/python tools/pa_chat.py "message" --conversation <new_session_id>

# Verify governor
BEAT_GOVERNOR_ENABLED=true .venv/bin/python manage.py shell -c "
from core.services.priority.governor import should_dispatch, _governor_enabled
print('Governor:', _governor_enabled())
"
```

---

## KNOWN GOTCHAS (carried forward)

- All OpenAI clients must use `get_openai_client()` factory. Forbidden kwargs: `timeout`, `max_retries`.
- All Anthropic clients must use `get_anthropic_client()` factory.
- `models_unified_system.py` uses lazy inline factory imports (deliberate — avoids circular import).
- Pre-commit hook blocks direct commits to `main` — always create feature branch + PR.
- `SKIP_NLP_MODELS=1` is load-bearing on macOS (Makefile celery target sets it).
- DO NOT query `TaskResult` — use `CeleryTaskEvent` from `core.models_celery_telemetry`.
- ML imports MUST be lazy (inside methods) — module-level loads ~800MB into Celery parent.
- `workspace_autopilot` trigger source is governor-gated (not in user_triggers bypass set).

---

**Always coordinate with Rigby first. She has the full context from Session 1089.**
