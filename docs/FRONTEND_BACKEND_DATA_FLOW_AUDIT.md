# Frontend-Backend Data Flow Audit

**Created:** Session 754 - January 14, 2026
**Purpose:** Complete mapping of every frontend component to its backend data source
**Status:** Living Document - Update as changes are made

---

## Quick Stats

| Metric | Count | Status |
|--------|-------|--------|
| **Frontend Pages** | 42 | All have code |
| **API Endpoints** | 200+ | Defined in lib/api.ts |
| **Endpoints with UI** | ~160 | 80% connected |
| **Endpoints WITHOUT UI** | ~40 | 20% orphaned |
| **Database Models** | 364+ | Most connected |
| **Models WITHOUT UI** | 2 critical | MemoryConnection, ClusterEvolution |
| **Data Display Coverage** | 60-85% | Varies by page |
| **WebSocket Channels** | 2 active | Dashboard, Conversations |

---

## Page-by-Page Data Flow Map

### 1. DashboardPage.tsx
**Location:** `frontend/src/pages/DashboardPage.tsx`
**Data Coverage:** ~80%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Ecosystem Stats | `GET /ecosystem/stats/` | views_ecosystem.py | Multiple | ✅ Live |
| Live Feed | `GET /ecosystem/live-feed/` | views_ecosystem.py | Activity | ✅ Live |
| Recent Activity | `GET /recent-activity/` | services/recent_activity.py | AgentDream, AgentConversation, Decision | ✅ Live |
| Network Graph | `GET /v1/research/network-graph/` | views_research.py | Agent connections | ✅ Live |
| Agent Cycle Button | `POST /v1/agents/force-cycle/` | views_agents.py | Agent | ✅ Live |
| Body Health Cards | `GET /body/vitals/` | services/body_vitals.py | Health metrics | ✅ Live |

**WebSocket:** `/dashboard` - Real-time activity updates
**Missing:** Network edge strength metrics, clustering coefficients

---

### 2. AgentsPage.tsx
**Location:** `frontend/src/pages/AgentsPage.tsx` (3,437 lines)
**Data Coverage:** ~70%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Agent List | `GET /v1/agents/comprehensive/` | views_agents.py | Agent | ✅ Live |
| Agent Channels | `GET /v1/agents/channels/` | views_agent_ecosystem.py | AgentChannel | ✅ Live |
| Dreams Gallery | `GET /agent-dreams/` | views_agent_learning.py | AgentDream | ✅ Live |
| Conversations | `GET /agent-conversations/` | views_agent_learning.py | AgentConversation | ✅ Live |
| Decisions | `GET /boardroom/decisions/` | intelligence_api.py | Decision | ✅ Live |
| Execution History | `GET /v1/agents/execution-history/` | views_agents.py | AgentExecution | ✅ Live |
| Orchestrations | `GET /v1/agents/orchestrations/` | views_workflow_engine.py | AgentOrchestration | ✅ Live |

**Missing:** Agent tool assignments, template usage, monitoring metrics

---

### 3. MemoryPalacePage.tsx
**Location:** `frontend/src/pages/MemoryPalacePage.tsx`
**Data Coverage:** ~40% (Session 753 gap)

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Overview | `GET /memory-palace/` | views_memory_palace.py | Memory | ✅ Live |
| Agent Memories | `GET /memory-palace/agent/{id}/memories/` | views_memory_palace.py | Memory | ✅ Live |
| Memory Rooms | `GET /memory-palace/agent/{id}/rooms/` | views_memory_palace.py | MemoryRoom | ✅ Live |
| Memory Clusters | `GET /memory-clusters/agent/{id}/` | views_memory_palace.py | MemoryCluster | ✅ Live |
| Memory Connections | `GET /memory-palace/memory/{id}/connections/` | views_memory_palace.py | MemoryConnection | ❌ NO UI |
| Cluster Evolution | `GET /memory-clusters/evolution/{id}/` | views_memory_palace.py | ClusterEvolution | ❌ NO UI |

**Critical Gap:** MemoryConnection and ClusterEvolution have endpoints but NO frontend display

---

### 4. IntelligencePage.tsx
**Location:** `frontend/src/pages/IntelligencePage.tsx`
**Data Coverage:** ~65%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Opportunities | `GET /opportunities/` | views_intelligence_api.py | Opportunity | ✅ Live |
| Predictions | `GET /v1/intelligence/predictions/` | intelligence_api.py | AgentPrediction | ⚠️ Deprecated |
| Pilot Gates | `GET /pilot-gates/` | views_pilot_approval.py | PilotGate | ✅ Live |
| Pilot Dashboard | `GET /pilots/dashboard/` | views_pilot_approval.py | Pilot | ✅ Live |
| Experiments | `GET /pilot-experiments/` | views_pilot_approval.py | Experiment | ✅ Live |

**Missing:** Opportunity score breakdown, Pilot execution metrics, Prediction confidence intervals

---

### 5. HumanPage.tsx
**Location:** `frontend/src/pages/HumanPage.tsx`
**Data Coverage:** ~70% (Session 746 enhanced)

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Attention Items | `GET /human/attention/` | views_human_interface.py | AttentionItem | ✅ Live |
| Attention Stats | `GET /human/attention/stats/` | views_human_interface.py | AttentionItem | ✅ Live |
| Decision History | `GET /human/attention/` (decisions) | views_human_interface.py | HumanDecision | ✅ Live |
| Control Panel | `GET /human/control/` | views_human_interface.py | HumanControl | ✅ Live |
| Preferences | `GET /human/preferences/` | views_human_interface.py | HumanPreference | ✅ Live |
| Arbitrage Watching | `GET /v1/betting/arbitrage/scan/` | views_betting.py | ArbitrageOpportunity | ✅ Live |

**Missing:** Decision reasoning details (options_considered, chosen_option)

---

### 6. BettingPage.tsx
**Location:** `frontend/src/pages/BettingPage.tsx`
**Data Coverage:** ~75% (Session 746 enhanced)

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Betting Stats | `GET /v1/betting/stats/` | views_betting.py | Bet, Wager | ✅ Live |
| Recent Wagers | `GET /v1/betting/wagers/` | views_betting.py | Wager | ✅ Live |
| Live Odds | `GET /v1/sports/live-odds/` | views_betting.py | LiveOdds | ✅ Live |
| Arbitrage Scan | `GET /v1/betting/arbitrage/scan/` | views_betting.py | ArbitrageOpportunity | ✅ Live |
| Wager Legs | (nested in wagers) | views_betting.py | WagerLeg | ✅ Live |
| Watching Tab | `GET /v1/betting/watching/` | views_betting.py | WatchedOpportunity | ✅ Live |

---

### 7. BodyHealthPage.tsx
**Location:** `frontend/src/pages/BodyHealthPage.tsx`
**Data Coverage:** 100% (Sessions 701-724)

| System | API Endpoint | Backend Service | Status |
|--------|--------------|-----------------|--------|
| HEART | `GET /heart/status/` | services/heart.py | ✅ Live |
| LUNGS | `GET /lungs/status/` | services/lungs.py | ✅ Live |
| CIRCULATORY | `GET /circulatory/status/` | services/circulatory.py | ✅ Live |
| SPINE | `GET /spine/status/` | services/spine.py | ✅ Live |
| IMMUNE | `GET /immune/status/` | services/immune.py | ✅ Live |
| DIGESTIVE | `GET /digestive/status/` | services/digestive.py | ✅ Live |
| MUSCULAR | `GET /muscular/status/` | services/muscular.py | ✅ Live |
| BRAIN | `GET /brain/status/` | services/brain.py | ✅ Live |
| SKIN | `GET /skin/status/` | services/skin.py | ✅ Live |

---

### 8. SpiderIntegrationPage.tsx
**Location:** `frontend/src/pages/SpiderIntegrationPage.tsx` (~450 lines, Session 718)
**Data Coverage:** ~85%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Network Overview | `GET /spider-dashboard/network/` | views_spider_integration.py | Spider config | ✅ Live |
| Dashboard Stats | `GET /spider-intelligence/dashboard-stats/` | views_spider_integration.py | SpiderExecution | ✅ Live |
| Registry | `GET /spider-intelligence/registry/` | views_spider_integration.py | Spider classes | ✅ Live |
| Health Summary | `GET /spider-health/summary/` | views_spider_integration.py | SpiderExecution | ✅ Live |
| Execution Logs | `GET /spider-health/executions/` | views_spider_integration.py | SpiderExecution | ✅ Live |
| Data Feed | `GET /spider-intelligence/feed/` | views_spider_integration.py | SpiderData | ✅ Live |
| Run Spider | `POST /spider-health/run/{name}/` | views_spider_integration.py | SpiderExecution | ✅ Live |

---

### 9. TimeTravelPage.tsx
**Location:** `frontend/src/pages/TimeTravelPage.tsx` (Session 750 fixed)
**Data Coverage:** ~80%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Overview | `GET /time-travel/` | views_time_travel.py | TimeTravelSession | ✅ Live |
| Session Detail | `GET /time-travel/session/{id}/` | views_time_travel.py | TimeTravelSession | ✅ Live |
| Decisions | nested in session | views_time_travel.py | Decision | ✅ Live |
| Bookmarks | `GET /time-travel/bookmarks/` | views_time_travel.py | Bookmark | ✅ Live |
| Flagged Decisions | `GET /time-travel/flagged/` | views_time_travel.py | Decision | ✅ Live |
| Agent Sessions | `GET /time-travel/agent/{id}/sessions/` | views_time_travel.py | TimeTravelSession | ✅ Live |
| Simulate | `POST /time-travel/agent/{id}/simulate/` | views_time_travel.py | Simulation | ✅ Live |

---

### 10. EvolutionPage.tsx
**Location:** `frontend/src/pages/EvolutionPage.tsx` (Session 716)
**Data Coverage:** ~85%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Overview | `GET /agent-evolution/` | views_agent_learning.py | AgentEvolution | ✅ Live |
| Agent Detail | `GET /agent-evolution/agent/{id}/` | views_agent_learning.py | AgentEvolution | ✅ Live |
| Leaderboard | `GET /agent-evolution/leaderboard/` | views_agent_learning.py | AgentEvolution | ✅ Live |
| Abilities | `GET /agent-evolution/abilities/` | views_agent_learning.py | Ability | ✅ Live |
| XP Gains | `GET /agent-evolution/xp-gains/` | views_agent_learning.py | XPGain | ✅ Live |

---

### ~~11. AgentMoodPage.tsx~~ — Removed Session 1009

All `/api/agent-mood/` endpoints and `views_agent_mood.py` deleted in orphan cleanup. Frontend page is a legacy redirect.

---

### 12. TimeCapsulePage.tsx
**Location:** `frontend/src/pages/TimeCapsulePage.tsx` (Session 749)
**Data Coverage:** ~85%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Overview | `GET /time-capsules/` | views_time_capsules.py | TimeCapsule | ✅ Live |
| Agent Capsules | `GET /time-capsules/agent/{id}/` | views_time_capsules.py | TimeCapsule | ✅ Live |
| Capsule Detail | `GET /time-capsules/{id}/` | views_time_capsules.py | TimeCapsule | ✅ Live |
| Ready to Reveal | `GET /time-capsules/ready-to-reveal/` | views_time_capsules.py | TimeCapsule | ✅ Live |
| Generate | `POST /time-capsules/generate/` | views_time_capsules.py | TimeCapsule | ✅ Live |

---

### 13. NeuralOrchestraPage.tsx
**Location:** `frontend/src/pages/NeuralOrchestraPage.tsx` (Session 716)
**Data Coverage:** ~75%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Ecosystem Feed | `GET /neural-orchestra/ecosystem/live-feed/` | views_neural_orchestra.py | Activity | ✅ Live |
| Agent Stats | `GET /neural-orchestra/agents/stats/` | views_neural_orchestra.py | Agent | ✅ Live |
| Learning Status | `GET /neural-orchestra/learning/status/` | views_neural_orchestra.py | LearningMetric | ✅ Live |
| Learning Feed | `GET /neural-orchestra/learning/feed/` | views_neural_orchestra.py | LearningEvent | ✅ Live |
| Health | `GET /neural-orchestra/health/` | views_neural_orchestra.py | SystemHealth | ✅ Live |

---

### 14. ConversationContractPage.tsx
**Location:** `frontend/src/pages/ConversationContractPage.tsx` (Session 717)
**Data Coverage:** ~80%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Overview | `GET /conversation-contract/overview/` | views_agent_learning.py | ConversationContract | ✅ Live |
| Detail | `GET /conversation-contract/{id}/` | views_agent_learning.py | ConversationContract | ✅ Live |

---

### 15. HiveMindPage.tsx
**Location:** `frontend/src/pages/HiveMindPage.tsx`
**Data Coverage:** ~80%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Sessions | `GET /hive-mind/sessions/` | views_ai_ecosystem.py | HiveMindSession | ✅ Live |
| Session Detail | `GET /hive-mind/session/{id}/` | views_ai_ecosystem.py | HiveMindSession | ✅ Live |
| Start Session | `POST /hive-mind/start/` | views_ai_ecosystem.py | HiveMindSession | ✅ Live |
| Agents | `GET /hive-mind/agents/` | views_ai_ecosystem.py | Agent | ✅ Live |

---

### 16. RelationshipsPage.tsx
**Location:** `frontend/src/pages/RelationshipsPage.tsx` (Session 716)
**Data Coverage:** ~80%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Overview | `GET /agent-relationships/` | views_agent_learning.py | AgentRelationship | ✅ Live |
| Agent Relationships | `GET /agent-relationships/agent/{id}/` | views_agent_learning.py | AgentRelationship | ✅ Live |
| Alliances | `GET /agent-relationships/alliances/{id}/` | views_agent_learning.py | Alliance | ✅ Live |
| Create | `POST /agent-relationships/create/` | views_agent_learning.py | AgentRelationship | ✅ Live |

---

### 17. AdvisorsPage.tsx
**Location:** `frontend/src/pages/AdvisorsPage.tsx` (Session 716)
**Data Coverage:** ~70%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| List | `GET /v1/advisors/list/` | views_advisor_api.py | Advisor | ✅ Live |
| Detail | `GET /v1/advisors/{id}/` | views_advisor_api.py | Advisor | ✅ Live |
| Consult | `POST /v1/advisors/consult/` | views_advisor_api.py | AdvisorConsultation | ✅ Live |

---

### 18. WorkspacePage.tsx
**Location:** `frontend/src/pages/WorkspacePage.tsx` (Session 695)
**Data Coverage:** ~90%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| List | `GET /workspaces/` | views_workspace.py | Workspace | ✅ Live |
| Detail | `GET /workspaces/{id}/` | views_workspace.py | Workspace | ✅ Live |
| Files | `GET /workspaces/{id}/files/` | views_workspace.py | WorkspaceFile | ✅ Live |
| Operations | `GET /workspaces/{id}/operations/` | views_workspace.py | WorkspaceOperation | ✅ Live |
| Git Status | `GET /workspaces/{id}/git-status/` | views_workspace.py | Git data | ✅ Live |
| Rollback | `POST /workspace-operations/{id}/rollback/` | views_workspace.py | WorkspaceOperation | ✅ Live |

---

### 19. LLMRoutingPage.tsx
**Location:** `frontend/src/pages/LLMRoutingPage.tsx` (Session 699-700)
**Data Coverage:** ~95%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Status | `GET /v1/llm-routing/status/` | services/llm_router.py | LLMProvider | ✅ Live |
| Providers | `GET /v1/llm-routing/providers/` | services/llm_router.py | LLMProvider | ✅ Live |
| Models | `GET /v1/llm-routing/models/` | services/llm_router.py | LLMModel | ✅ Live |
| Agent Configs | `GET /v1/llm-routing/agent-configs/` | services/llm_router.py | AgentLLMConfig | ✅ Live |
| Logs | `GET /v1/llm-routing/logs/` | services/llm_router.py | LLMCallLog | ✅ Live |
| Cost Analytics | `GET /v1/llm-routing/cost-analytics/` | services/llm_router.py | LLMCallLog | ✅ Live |

---

### 20. ContentChannelsPage.tsx
**Location:** `frontend/src/pages/ContentChannelsPage.tsx` (Session 741)
**Data Coverage:** ~85%

| Component | API Endpoint | Backend View | Database Model | Status |
|-----------|--------------|--------------|----------------|--------|
| Channels | `GET /content-channels/` | views_content.py | ContentChannel | ✅ Live |
| Channel Detail | `GET /content-channels/{id}/` | views_content.py | ContentChannel | ✅ Live |
| Episodes | nested in channel | views_content.py | Episode | ✅ Live |
| Episode Detail | `GET /content-channels/episode/{id}/` | views_content.py | Episode | ✅ Live |

---

## Critical Data Gaps

### Database Models with NO Frontend UI

| Model | Fields | API Endpoint | Priority |
|-------|--------|--------------|----------|
| **MemoryConnection** | source_memory, target_memory, connection_type, strength, created_by_agent | `/memory-palace/memory/{id}/connections/` | HIGH |
| **ClusterEvolution** | cluster, snapshot_date, member_count, centroid_shift, new_memories, lost_memories | `/memory-clusters/evolution/{id}/` | HIGH |

### API Endpoints with NO Frontend Calls

| Endpoint Group | Count | Reason |
|----------------|-------|--------|
| Agent Tools | 5 | Tool management UI missing |
| Agent Templates | 5 | Template UI missing |
| Agent Monitoring | 5 | Monitoring dashboard missing |
| Agent Stats (detailed) | 3 | Aggregated in other views |

### Hidden Fields per Model

| Model | Hidden Fields | Impact |
|-------|---------------|--------|
| Decision | options_considered[], chosen_option, reasoning | Can't see decision logic |
| Opportunity | confidence_score, impact_potential, market_size | Can't evaluate opportunities |
| Memory | embedding_vector[], semantic_tags[], source_links[] | Limited search/filter |
| Pilot | success_rate, execution_time, resource_usage | Can't evaluate performance |
| AgentContribution | tokens_used, execution_time_seconds, user_rating | Can't measure agent efficiency |

---

## WebSocket Real-Time Connections

| WebSocket Path | Used By | Purpose | Status |
|----------------|---------|---------|--------|
| `/dashboard` | DashboardPage.tsx | Live activity updates | ✅ Active |
| `/ws/agent-conversations/` | AgentSocialPage.tsx | Conversation updates | ✅ Active |
| System Events Hook | Multiple pages | Agent execution, body status, dreams | ✅ Active |

### Pages Missing Real-Time Updates

- MemoryPalacePage - No WebSocket for memory changes
- TimeTravelPage - No WebSocket for decision updates
- EvolutionPage - No WebSocket for XP gains
- IntelligencePage - No WebSocket for opportunity updates

---

## Data Flow Verification Checklist

For each page, verify:

- [ ] All API endpoints return real data (not mock)
- [ ] All displayed fields match database schema
- [ ] All actions (create/update/delete) work correctly
- [ ] Error states are handled gracefully
- [ ] Loading states show during fetch
- [ ] Empty states display when no data
- [ ] Pagination works if implemented
- [ ] Filters/search work correctly
- [ ] Real-time updates work (if WebSocket exists)

---

## Session History

| Session | Changes |
|---------|---------|
| 754 | Created this audit document, fixed AgentContribution tracking |
| 753 | Identified Memory Palace data gaps (~60% hidden) |
| 752 | Fixed Live Feed AgentContribution staleness |
| 751 | Fixed Conversation auth, Neural Orchestra feed |
| 750 | Fixed Time Travel frontend/backend signatures |
| 749 | Fixed Mood Page CRUD, Time Capsules tokens |
| 746 | Enhanced Human/Betting/Dashboard data display (60% → 85%) |
| 745 | Added Watch & Verify, arbitrage paper trading |
| 744 | Completed Integration Roadmap (95% integration) |

---

## Next Steps

1. **Implement MemoryConnection UI** - Create relationship graph visualization
2. **Implement ClusterEvolution UI** - Add evolution timeline
3. **Add Decision Reasoning Display** - Show options_considered in decisions
4. **Create Agent Tool Management UI** - Tool assignment interface
5. **Add Real-Time to More Pages** - WebSocket for Memory, Evolution, Intelligence
