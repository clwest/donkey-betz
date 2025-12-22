# Agent 1.5: Celery Tasks Discovery

**Date:** December 21, 2025
**Status:** Complete
**Total Tasks Discovered:** 156 @shared_task functions, 114 scheduled tasks

---

## Summary

Discovered a massive background task infrastructure:
- **156 Celery tasks** defined in `core/tasks.py`
- **114 Celery Beat scheduled tasks** in `core/celery.py`
- Covers all autonomous features of the platform

---

## 1. Celery Beat Schedule Categories

### Spider Network (6 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `run-spider-network` | Every 15 min | Execute spider network |
| `backfill-spider-embeddings` | Every 10 min | Create spider embeddings |
| `process-spider-data-automatic` | Every 5 min | Process spider data |
| `warm-up-spiders` | Every 4 hours | Warm up spider network |
| `recalculate-spider-priorities` | Every 6 hours | Update priorities |
| `collect-real-opportunities` | Every 15 min | Collect opportunities |

### Agent Learning (15 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `agent-learning-cycle` | Every 10 min | Knowledge sharing |
| `agent-think-synthesize` | Every 30 min | Synthesize insights |
| `update-agent-effectiveness` | Daily 5:30 AM | Update effectiveness |
| `broadcast-learning-status` | Every 60s | Real-time updates |
| `embed-daily-agent-learning` | Daily 2 AM | Daily embeddings |
| `embed-agent-activity` | Every 30 min | Activity embeddings |
| `agent-conversation-cycle` | Every 30 min | Agent-to-agent chat |
| `multi-agent-panel-cycle` | Every hour | Panel discussions |
| `backfill-memory-embeddings` | Every 30 min | Memory embeddings |
| `sync-project-knowledge` | Every 30 min | Project knowledge |
| `collect-training-data-daily` | Daily 1 AM | Training data |
| `collect-training-data-weekly-full` | Weekly Sun 2:30 AM | Full refresh |
| `auto-promote-decisions` | Every 30 min | Promote decisions |
| `auto-resolve-knowledge-gaps` | Every 6 hours | Fill knowledge gaps |
| `broadcast-conversation-status` | Every 2 min | Broadcast convos |

### Agent Dreams (4 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `agent-dream-cycle` | Every 15 min | Generate dreams |
| `broadcast-dream-journal` | Every 3 min | Show dreams |
| `dream-productization-cycle` | Every 20 min | Score dreams |
| `dream-implementation-cycle` | Every 15 min | Process dreams |
| `dream-execution-cycle` | Every 20 min | Execute dreams |

### Agent Mood System (2 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `check-mood-expirations` | Every 5 min | Reset expired moods |
| `apply-mood-rules` | Every 10 min | Apply mood rules |

### Agent Relationships (3 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `evolve-agent-relationships` | Every 30 min | Evolve relationships |
| `update-alliance-strengths` | Every hour | Update alliances |
| `broadcast-relationship-status` | Every 2 min | Broadcast status |

### Agent Evolution (3 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `process-agent-activity-xp` | Every 15 min | Process XP |
| `check-level-milestones` | Every hour | Check milestones |
| `broadcast-evolution-status` | Every 2 min | Broadcast evolution |

### Opportunity System (8 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `score-opportunities-hourly` | Every hour :15 | Score opportunities |
| `expire-old-opportunities` | Daily 4:30 AM | Expire old opps |
| `generate-opportunity-report` | Daily 8 AM | Daily report |
| `weekly-opportunity-digest` | Weekly Sun 10 AM | Weekly digest |
| `proactive-opportunity-alerts` | Every 30 min | Alert users |
| `personalized-opportunity-alerts` | Every hour :15 | Personalized alerts |
| `check-sec-filings-alert` | Every 5 min (market hours) | SEC filings |
| `autonomous-intelligence-loop` | Every 15 min | Intelligence loop |

### Learning System (6 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `daily-learning-pipeline` | Daily 5 AM | Daily pipeline |
| `discover-success-patterns` | Every 6 hours | Find patterns |
| `generate-user-insights` | Every 4 hours | User insights |
| `update-learning-profiles` | Daily 6 AM | Update profiles |
| `project-learning-cycle` | Daily 6 AM | Project learning |
| `sync-pipeline-to-collective` | Every 6 hours | Pipeline to CI |

### Proactive System (6 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `proactive-system-check` | Every 2 hours | System check |
| `check-all-alerts` | Every 30 min | Check alerts |
| `generate-smart-suggestions` | Every 8 hours | Smart suggestions |
| `execute-scheduled-automations` | Every hour | Execute automations |
| `send-pending-notifications` | Every 5 min | Send notifications |
| `cleanup-old-notifications` | Daily 3:30 AM | Cleanup |

### Autonomous Content Studio (3 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `run_autonomous_content_studio` | Every 4 hours | Main loop |
| `generate_content_for_channel` | On-demand | Channel content |
| `track_content_performance` | Daily 8 PM | Performance tracking |

### ML & Prediction (5 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `check-retraining-needed` | Daily 3 AM | Check retraining |
| `retrain-all-models-weekly` | Weekly Sun 2 AM | Retrain models |
| `cleanup-old-model-files` | Weekly Mon 1 AM | Cleanup |
| `evaluate-completed-predictions` | Every hour | Evaluate predictions |
| `generate-accuracy-report` | Daily 9 AM | Accuracy report |

### Sports Betting (4 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `settle-user-bets` | Every 15 min | Settle bets |
| `cleanup-old-predictions` | Weekly Mon 3 AM | Cleanup |

### Maintenance (5 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `clean-stale-data` | Daily 2 AM | Clean stale data |
| `cleanup-opportunities-daily` | Daily 3 AM | Cleanup opps |
| `expire-old-suggestions` | Daily 4 AM | Expire suggestions |
| `update-agent-performance` | Daily 4 AM | Update performance |
| `record-style-evolution` | Daily 12:30 AM | Style evolution |

### Stock & Blockchain Audit (4 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `stock-audit-cycle` | Every 30 min (market hours) | Stock monitoring |
| `blockchain-audit-cycle` | Every hour | Blockchain monitoring |
| `daily-intelligence-digest` | Daily 8 AM | Daily digest |

### Miscellaneous (8 tasks)
| Task | Schedule | Purpose |
|------|----------|---------|
| `poll-pending-3d-models` | Every 30 sec | 3D model polling |
| `sync-shared-memory` | Every 10 min | Shared memory |
| `refresh-ai-opportunities` | Every 30 min | AI opportunities |
| `sync-revenue-metrics` | Every hour | Revenue metrics |
| `fetch-opportunities-hourly` | Every hour | Fetch opps |

---

## 2. Task Categories in core/tasks.py (156 tasks)

### Spider Tasks (~20 tasks)
- `run_spider_network` - Execute all spiders
- `backfill_spider_embeddings` - Create embeddings
- `fetch_spider_data` - Fetch from spider
- `process_spider_data_automatic` - Auto-process data
- Various spider-specific tasks

### Agent Learning Tasks (~25 tasks)
- `run_agent_learning_cycle` - Learning cycle
- `agent_think_and_synthesize` - Synthesize knowledge
- `share_knowledge_between_agents` - Knowledge sharing
- `embed_agent_activity` - Activity embeddings
- `run_agent_conversation` - Agent conversations
- `run_multi_agent_conversation` - Panel discussions
- Various conversation/learning tasks

### Agent Dreams Tasks (~10 tasks)
- `generate_agent_dreams` - Generate dreams
- `score_and_promote_dreams` - Score dreams
- `process_approved_dreams` - Process approved
- `execute_dream_implementations` - Execute dreams
- Broadcast tasks

### Sci-Fi Feature Tasks (~20 tasks)
- Mood system tasks
- Relationship tasks
- Evolution tasks
- Memory palace tasks
- Time travel tasks

### Opportunity Tasks (~15 tasks)
- `score_opportunities_from_spider_data` - Score opps
- `expire_old_opportunities` - Expire old
- `generate_weekly_opportunity_digest` - Weekly digest
- Alert/notification tasks

### Proactive System Tasks (~10 tasks)
- `run_proactive_system_check` - System check
- `check_all_alerts` - Check alerts
- `generate_smart_suggestions` - Suggestions
- Notification tasks

### Autonomous Content Studio Tasks (~5 tasks)
- `run_autonomous_content_studio` - Main loop
- `generate_content_for_channel` - Generate content
- `track_content_performance` - Track performance

### ML Tasks (~10 tasks)
- Model training tasks
- Prediction evaluation tasks
- Scoring tasks

### Discord Tasks (~5 tasks)
- `send_proactive_opportunity_alerts` - Alerts
- `send_personalized_opportunity_alerts` - Personalized
- Discord notification helpers

### Maintenance Tasks (~10 tasks)
- Cleanup tasks
- Expiration tasks
- Data processing tasks

### Autonomous Intelligence Loop (~5 tasks)
- `run_autonomous_intelligence_loop` - Main loop
- `run_daily_intelligence_digest` - Daily digest
- `check_sec_filings_alert` - SEC alerts

---

## 3. Task Frequency Summary

| Frequency | Count |
|-----------|-------|
| Every 30 seconds | 1 |
| Every 1-2 minutes | 4 |
| Every 3 minutes | 1 |
| Every 5 minutes | 5 |
| Every 10 minutes | 4 |
| Every 15 minutes | 10 |
| Every 20 minutes | 2 |
| Every 30 minutes | 12 |
| Every hour | 15 |
| Every 2 hours | 2 |
| Every 4 hours | 3 |
| Every 6 hours | 5 |
| Every 8 hours | 1 |
| Daily | 20 |
| Weekly | 4 |
| **TOTAL** | **84 unique intervals** |

---

## 4. Task Infrastructure Files

| File | Purpose | Size |
|------|---------|------|
| `core/tasks.py` | Main task definitions | ~12,000 lines |
| `core/celery.py` | Beat schedule + config | ~800 lines |
| `ai_core/tasks.py` | AI-specific tasks | ~200 lines |
| `intelligence/tasks.py` | Intelligence tasks | ~500 lines |
| `agents/tasks.py` | Agent tasks | ~300 lines |
| `agents/tasks_enhanced.py` | Enhanced agent tasks | ~200 lines |
| `sports/tasks.py` | Sports betting tasks | ~300 lines |
| `ml/tasks.py` | ML training tasks | ~200 lines |

---

## 5. Gaps Identified

### P0 - Critical
1. **No task monitoring dashboard** - 114 scheduled tasks with no visibility
2. **Potential task overlap** - Some similar tasks may be duplicated

### P1 - High
3. **High frequency tasks** - 4 tasks running every 1-2 minutes (resource intensive)
4. **core/tasks.py too large** - 12,000 lines in single file

### P2 - Medium
5. **No task retry policies** - Some tasks lack max_retries
6. **Missing task documentation** - Purpose unclear for some tasks

---

## 6. Task Dependencies

### Discord Notifications Used By:
- Agent dreams
- Agent conversations
- Opportunity alerts
- SEC filings
- System status

### Learning Loop Dependencies:
```
Spider Network
    → Spider Embeddings
    → Opportunity Scoring
    → Agent Knowledge
    → Collective Intelligence
    → Agent Dreams
    → Dream Implementation
```

### Autonomous Intelligence Loop Flow:
```
run_autonomous_intelligence_loop (every 15 min)
    → Check SEC filings
    → Score opportunities
    → Generate alerts
    → Run agent learning
    → Update knowledge
```

---

*Generated by Agent 1.5: Celery Tasks Discovery*
