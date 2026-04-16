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

**Date:** April 16, 2026 (end of Session 1089)
**Previous session handoff:** [`docs/handoffs/SESSION_1089_GOVERNOR_AND_GROUNDING.md`](docs/handoffs/SESSION_1089_GOVERNOR_AND_GROUNDING.md)
**Previous session PA conversation (LOCAL):** `pa-cfc4198046a3` — Chris creates a new one each session, so ask him for the new ID before your first Rigby message.
**Status:** Governor live, agent grounding in progress, demo video prep underway.

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

## SESSION 1090 — PRIORITIES

### 1. Fix ContentWriterAgent (64% success rate) — CRITICAL FOR VIDEO
The content pipeline is the most visible product feature. 4 of 11 runs failed. Common causes: missing topic, citation enforcement failure, model timeouts. Fix: enforce "must have sources or claims pack" — otherwise generate draft-only (not counted as failure).

### 2. Fix AISeriesWorkflowAgent (43% success rate)
3 of 7 runs failed. Inspect failure signatures in AgentExecution, add input validation guards. If inputs are missing, skip gracefully with reason instead of failing.

### 3. Wire EditorAgent + PlatformAuditAgent (never executed)
Both are high-value for the demo narrative but have never run. Add at least one intentional trigger each so they have real artifacts before filming.

### 4. Demo Video Prep — "Cross-Domain Incident Room"
Concept: Rigby detects a real signal, traces cross-domain impact (tech → regulation → markets → hiring), makes a governed decision, ships an artifact. All live on camera.

Required for demo:
- Spider search working (DONE)
- Governor visible (DONE)
- Agent dispatch + completion (DONE)
- CTO/COO briefs grounded (DONE)
- ContentWriterAgent reliable (NEEDS FIX)
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
