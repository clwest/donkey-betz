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

**Date:** April 16, 2026 (end of Session 1090)
**Previous session handoff:** [`docs/handoffs/SESSION_1090_DEMO_READINESS.md`](docs/handoffs/SESSION_1090_DEMO_READINESS.md)
**Previous session PA conversation (LOCAL):** `pa-697ab48e2ffc` — Chris creates a new one each session, so ask him for the new ID before your first Rigby message.
**Status:** Demo readiness validated. 12 PRs shipped. 5 agents producing real artifacts. Fix list created by agents for Session 1091.

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

## SESSION 1091 — PRIORITIES

### 1. Work Through Agent-Generated Fix List (P0 first)
The agents found 14 real issues. Fix list is in demo-testing workspace as a deliverable.

**P0 — Fix Before Demo Recording:**
- Agent timeout rate 1.9% vs 0.2% SLO — top offenders need timeout ladder
- DEBUG=True on production — must be False for Railway
- PlatformAuditAgent model/schema mismatch in audit queries

**P1 — Fix This Week:**
- 87 pending action items, all unowned
- 155 ACTIVE / 83 TRIAGE / 11 COMPLETED initiatives (WIP sprawl)
- 315 stale suggestions >7 days
- 130 gates active 74 days
- AudioAgent blocked (ElevenLabs quota)
- OpportunityPipelineAgent circuit breaker tripped
- 1 unapplied migration (content.0046)

**P2 — Next Sprint:**
- 3 missing API keys (DeepSeek, Replicate, TheOdds)
- Feature flags unset
- No standardized failure taxonomy
- ResearchAgent volume amplifying dependency instability

### 2. Clean End-to-End Demo Run
After P0 fixes, run the full 7-step demo sequence and verify all artifacts are clean.

### 3. Record the Video
Demo runbook: `docs/playbooks/DEMO_HAPPY_PATH.md`
Workspace: demo-testing (active)
- A "Demo Autonomy Mode" allowlist (NEEDS BUILD)

### 5. Patent Portfolio
- Fresh audit done (post-governance), 3 deliverables saved under initiative
- Top candidate: "Governed Autonomy Control Plane"
- Governance layer patent candidate needs full write-up
- Workspace: "Patent Portfolio — 2026 Refresh" (deactivated, data preserved)

### 6. Brand & Business Strategy
Chris wants to think beyond sports betting. The platform is a "governed intelligence OS" — not a GPT wrapper, not a betting app. The business model discussion is open:
- Intelligence-as-a-Service (fastest to revenue)
- Governed Agent Platform (platform play — CrewAI killer)
- Vertical SaaS (pick a market once we find pull)

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
