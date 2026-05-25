# Session 707: MUSCULAR SYSTEM - Agent Work Execution Monitoring

**Date:** January 6, 2026
**Focus:** 7th Body System - Agent work execution and performance monitoring
**Status:** COMPLETE

## Overview

The MUSCULAR SYSTEM is the 7th body system component, monitoring agent work execution and performance. It tracks "strength" (success rate), "fatigue" (high load), and "strain" (errors) across agent muscle groups.

## Human Body Metaphor

| Muscle Concept | Technical Equivalent |
|----------------|---------------------|
| Muscles | Agent categories (Creation, Research, Strategy, etc.) |
| Muscle Fibers | Individual agents within category |
| Flexing | Agent task execution |
| Strength | Execution success rate & performance |
| Fatigue | High execution load, slow response times |
| Strain | Error rate, failed executions |
| Recovery | Time since last execution |
| Muscle Memory | Agent learning from past executions |

## Files Created (5)

| File | Lines | Purpose |
|------|-------|---------|
| `core/models_muscular.py` | ~260 | MuscleGroup, MuscularPulse, MuscleStatus models |
| `core/services/muscular.py` | ~550 | MuscularSystemService singleton |
| `core/views_muscular.py` | ~280 | 8 API endpoints |
| `core/management/commands/muscular_check.py` | ~420 | CLI command |
| `core/migrations/0153_session_707_muscular_system.py` | ~250 | Migration + 10 default groups |

## Files Modified (5)

| File | Changes |
|------|---------|
| `core/urls.py` | Added 8 MUSCULAR API routes |
| `core/tasks.py` | Added `check_muscular` Celery task |
| `core/celery.py` | Added Beat schedule (every 90 seconds) |
| `core/admin.py` | Registered 3 MUSCULAR admin classes |
| `core/auth_middleware.py` | Added 7 MUSCULAR endpoints to PUBLIC_PATHS |

## Database Models

### 1. MuscleGroup - Configuration
- 10 categories: creation, research, strategy, development, blockchain, stocks, executive, narrative, orchestration, markets
- Configurable thresholds: target_success_rate, max_avg_execution_time_ms, max_fatigue_level, max_daily_executions
- Agent assignment via `agent_names` JSONField

### 2. MuscularPulse - Time-Series Records
- Overall metrics: strength_score, overall_status
- Execution metrics: total_executions_24h, success_rate_24h, avg_execution_time_ms
- Load metrics: active_agents, fatigued_agents, strained_agents
- Issues: weak_muscles, overworked_muscles

### 3. MuscleStatus - Current State Cache
- Per-group cached status
- Real-time metrics: strength_score, fatigue_level, strain_level

## API Endpoints (8)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/muscular/flex/` | GET | Run full muscular check |
| `/api/muscular/status/` | GET | Get cached muscular status |
| `/api/muscular/groups/` | GET | List all muscle groups |
| `/api/muscular/groups/<id>/` | GET | Get specific group status |
| `/api/muscular/weak/` | GET | Get weak muscles (low success) |
| `/api/muscular/overworked/` | GET | Get overworked muscles |
| `/api/muscular/history/` | GET | Get muscular pulse history |
| `/api/muscular/is-strong/` | GET | Quick alive check |

## CLI Command

```bash
python manage.py muscular_check                    # Full muscular check
python manage.py muscular_check --json             # JSON output
python manage.py muscular_check --groups           # List all muscle groups
python manage.py muscular_check --weak             # Show weak muscles only
python manage.py muscular_check --overworked       # Show overworked muscles
python manage.py muscular_check --watch            # Continuous (90s interval)
python manage.py muscular_check --history          # Show pulse history
python manage.py muscular_check --group creation   # Check specific group
```

## Status Levels

| Strength Score | Status | Emoji | Meaning |
|----------------|--------|-------|---------|
| 80-100% | `strong` | 💪 | High success rate, normal load |
| 60-79% | `fit` | 🏃 | Good performance, manageable load |
| 40-59% | `fatigued` | 😓 | High load, slower responses |
| 20-39% | `strained` | 🥵 | High error rate, needs attention |
| 0-19% | `paralyzed` | 🦽 | No activity or all failing |

## 10 Default Muscle Groups

| Group Name | Category | Critical | Agents |
|------------|----------|----------|--------|
| Creation Muscles | creation | No | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent |
| Research Muscles | research | Yes | ResearchAgent |
| Strategy Muscles | strategy | No | ContentStrategyAgent, BrandIdentityAgent, SEOOptimizerAgent, SocialMediaAgent |
| Development Muscles | development | Yes | CodeGeneratorAgent, FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent |
| Blockchain Muscles | blockchain | No | BlockchainAuditCoordinator + team |
| Stock Analysis Muscles | stocks | Yes | StockAuditCoordinator + team |
| Executive Muscles | executive | No | CTOAgent, COOAgent, CreativeDirectorAgent, MeetingCoordinatorAgent |
| Narrative Muscles | narrative | No | NarrativeDriftCoordinator + team |
| Orchestration Muscles | orchestration | Yes | WorkflowAgent, OpportunityPipelineAgent, ContentExecutorAgent |
| Market Muscles | markets | No | PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector |

## Celery Integration

- Task: `core.tasks.check_muscular`
- Schedule: Every 90 seconds
- Queue: broadcast
- Expires: 85 seconds

## Human Body Architecture (7 Systems)

| Body Part | Component | Purpose | Session |
|-----------|-----------|---------|---------|
| HEART | HeartMonitorService | Health monitoring | 701 |
| LUNGS | LungsCapacityService | Resource/budget management | 702 |
| CIRCULATORY | CirculatorySystemService | Data flow monitoring | 703 |
| SPINE | SpineRouterService | Central API routing | 704 |
| IMMUNE | ImmuneSystemService | Security & threat detection | 705 |
| DIGESTIVE | DigestiveSystemService | Data ingestion & processing | 706 |
| **MUSCULAR** | **MuscularSystemService** | **Agent work execution** | **707** |

## Verification

```bash
# Verify muscle groups created
python manage.py shell -c "from core.models_muscular import MuscleGroup; print(MuscleGroup.objects.count())"
# Expected: 10

# Run muscular check
python manage.py muscular_check

# Test API (after server restart)
curl http://localhost:8000/api/muscular/status/
```

## Notes

- Server needs restart for auth_middleware changes to take effect
- Initial status shows "PARALYZED" because most agents haven't executed recently
- As agents execute tasks, the strength score will improve
- Integrates with AgentExecution model for real execution data
