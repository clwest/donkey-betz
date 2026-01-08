# UI-Backend Connection Map

**Created:** Session 309
**Updated:** Session 731 (RAG/Embedding System Audit)
**Purpose:** Map what's connected, what exists but isn't connected, and opportunities for integration

---

## Executive Summary

The platform has **excellent coverage** - most UI components are properly wired to backend APIs:

| Category | UI Components | Backend APIs | Connection Status |
|----------|---------------|--------------|-------------------|
| Sci-Fi Features | 15 features | 84 endpoints | **95% Connected** |
| Spider Intelligence | 4 tabs | 8 endpoints | **100% Connected** |
| Agent Learning | 3 views | 10 endpoints | **100% Connected** |
| Clean Agents | 11 agents | Router active | **100% Connected** |
| Deprecated Agents | 14 agents | Learning hooks | **100% Connected** |
| Memory Clusters | 1 tab | 10 endpoints | **100% Connected** |
| **RAG/Documents** | **None** | **6 endpoints** | **0% Connected** |

---

## 1. FULLY CONNECTED (Working End-to-End)

### Spider Intelligence Panel
| UI Component | Backend API | Status |
|--------------|-------------|--------|
| Trending Tab | `/api/spider-intelligence/trends/` | CONNECTED |
| Markets Tab | `/api/spider-intelligence/market/` | CONNECTED |
| Opportunities Tab | `/api/spider-intelligence/jobs/` | CONNECTED |
| Spiders Tab | `/api/spider-intelligence/summary/` | CONNECTED |
| Topic Filtering | Query params `?topic=ai` | CONNECTED |

### Agent Dreams (Session 247)
| UI Component | Backend API | Status |
|--------------|-------------|--------|
| Dream Journal | `/api/agent-dreams/` | CONNECTED |
| Trigger Dream | `/api/agent-dreams/trigger/` | CONNECTED |
| React to Dream | `/api/agent-dreams/{id}/react/` | CONNECTED |
| Mark Shown | `/api/agent-dreams/mark-shown/` | CONNECTED |

### Agent Mood System (Session 253)
| UI Component | Backend API | Status |
|--------------|-------------|--------|
| Mood Overview | `/api/agent-mood/` | CONNECTED |
| Set Mood | `/api/agent-mood/agent/{id}/set/` | CONNECTED |
| Mood Grid Display | `/api/agent-mood/` | CONNECTED |

### Agent Evolution (Session 254)
| UI Component | Backend API | Status |
|--------------|-------------|--------|
| Evolution Overview | `/api/agent-evolution/` | CONNECTED |
| XP Leaderboard | `/api/agent-evolution/leaderboard/` | CONNECTED |
| Initialize Evolution | `/api/agent-evolution/initialize/` | CONNECTED |

### Hive Mind (Session 248-250)
| UI Component | Backend API | Status |
|--------------|-------------|--------|
| Preview Agents | `/api/hive-mind/preview/` | CONNECTED |
| Start Session | `/api/hive-mind/start/` | CONNECTED |
| Session Details | `/api/hive-mind/session/{id}/` | CONNECTED |
| Session History | `/api/hive-mind/sessions/` | CONNECTED |

### Time Travel Debugging (Session 255)
| UI Component | Backend API | Status |
|--------------|-------------|--------|
| Overview | `/api/time-travel/` | CONNECTED |
| Agent Sessions | `/api/time-travel/agent/{id}/sessions/` | CONNECTED |
| Session Details | `/api/time-travel/session/{id}/` | CONNECTED |
| Simulate | `/api/time-travel/agent/{id}/simulate/` | CONNECTED |

### Memory Palace (Session 251-252)
| UI Component | Backend API | Status |
|--------------|-------------|--------|
| Overview | `/api/memory-palace/` | CONNECTED |
| Agent Rooms | `/api/memory-palace/agent/{id}/rooms/` | CONNECTED |
| Room Memories | `/api/memory-palace/room/{id}/memories/` | CONNECTED |
| Memory Details | `/api/memory-palace/memory/{id}/` | CONNECTED |
| Search | `/api/memory-palace/search/` | CONNECTED |
| Create Memory | `/api/memory-palace/create/` | CONNECTED |

### Predictions/Prophecies (Session 258)
| UI Component | Backend API | Status |
|--------------|-------------|--------|
| Overview | `/api/predictions/` | CONNECTED |
| Agent Predictions | `/api/predictions/agent/{id}/` | CONNECTED |
| Verify Prediction | `/api/predictions/{id}/verify/` | CONNECTED |
| Upvote | `/api/predictions/{id}/upvote/` | CONNECTED |
| Leaderboard | `/api/predictions/leaderboard/` | CONNECTED |
| Generate from Dreams | `/api/predictions/generate-from-dreams/` | CONNECTED |

### Agent Learning (Sessions 305-309)
| UI Component | Backend API | Status |
|--------------|-------------|--------|
| Activity Feed | `/api/agent-learning/activity/` | CONNECTED |
| Stats | `/api/agent-learning/stats/` | CONNECTED |
| All Preferences | `/api/agent-learning/all-preferences/` | CONNECTED |
| Agent Context | `/api/agent-learning/context/{name}/` | CONNECTED |
| Share Knowledge | `/api/agent-learning/share/{name}/` | CONNECTED |

### Memory Clusters (Session 718)
| UI Component | Backend API | Status |
|--------------|-------------|--------|
| Overview | `/api/memory-clusters/` | CONNECTED |
| Agent Clusters | `/api/memory-clusters/agent/{id}/` | CONNECTED |
| Cluster Detail | `/api/memory-clusters/cluster/{id}/` | CONNECTED |
| Visualization | `/api/memory-clusters/visualization/` | CONNECTED |
| Generate All | `/api/memory-clusters/generate-all/` | CONNECTED |
| Add Memory | `/api/memory-clusters/cluster/{id}/add-memory/` | CONNECTED |
| Remove Memory | `/api/memory-clusters/cluster/{id}/memory/{id}/` | CONNECTED |
| Evolution | `/api/memory-clusters/evolution/{id}/` | CONNECTED |
| Find Similar | `/api/memory-clusters/find-similar/` | CONNECTED |
| Embedding Coverage | `/api/spider-health/embedding-coverage/` | CONNECTED |

**Frontend:** MemoryPalacePage.tsx (Clusters tab), SpiderIntegrationPage.tsx

---

## 2. WEBSOCKET CONNECTIONS (Real-Time)

### Active WebSocket Channels
| UI Usage | WebSocket Route | Consumer | Status |
|----------|-----------------|----------|--------|
| Agent Activity | `ws/activity/` | AgentProgressConsumer | CONNECTED |
| Agent Conversations | `ws/agent-conversations/` | AgentConversationConsumer | CONNECTED |
| Hive Mind | `ws/hive-mind/` | HiveMindConsumer | CONNECTED |
| Spider Updates | `ws/spider-updates/` | SpiderWebSocketConsumer | CONNECTED |
| Analytics | `ws/analytics/` | (Consumer exists) | CONNECTED |
| Revenue Dashboard | `ws/revenue/` | RevenueDashboardConsumer | CONNECTED |

### Autonomous Learning Client
- **File:** `/static/js/autonomous-learning-client.js`
- **WebSocket:** `ws/personal-assistant/`
- **Status:** CONNECTED - Real-time learning insights

---

## 3. NOT CONNECTED (Backend Exists, No Frontend)

### RAG/Document Embedding System (Session 731 Audit)

**Status:** Backend fully functional with 7,239 document embeddings, but NO frontend UI.

| Backend API | Purpose | Priority | Frontend Needed |
|-------------|---------|----------|-----------------|
| `/api/v1/rag/upload-document/` | Upload documents for RAG processing | **HIGH** | File upload with drag-and-drop |
| `/api/v1/rag/semantic-search/` | Semantic search across documents | **HIGH** | Search interface with results |
| `/api/v1/rag/generate/` | Generate responses with RAG context | **HIGH** | Chat/query interface |
| `/api/v1/rag/stats/` | Get embedding statistics | MEDIUM | Stats dashboard |
| `/api/v1/rag/advanced-query/` | Multi-collection search | MEDIUM | Advanced search filters |
| `/api/v1/rag/optimize/` | Optimize embedding storage | LOW | Admin action button |
| `/api/v1/rag/collections/` | Manage knowledge collections | MEDIUM | Collection list/create UI |
| `/api/v1/rag/documents/` | List/manage documents | MEDIUM | Document list with actions |

**Recommended Frontend Implementation:**

1. Add to `frontend/src/lib/api.ts`:
```typescript
export const ragApi = {
  uploadDocument: (file: File, options?: { collection_id?: string }) =>
    api.postForm('/v1/rag/upload-document/', { file, ...options }),
  semanticSearch: (query: string, options?: { limit?: number, threshold?: number }) =>
    api.post('/v1/rag/semantic-search/', { query, ...options }),
  generate: (query: string, options?: { max_context_chunks?: number }) =>
    api.post('/v1/rag/generate/', { query, ...options }),
  stats: () => api.get('/v1/rag/stats/'),
  listCollections: () => api.get('/v1/rag/collections/'),
  listDocuments: () => api.get('/v1/rag/documents/'),
};
```

2. Create `DocumentsPage.tsx` with:
   - Document upload with drag-and-drop
   - Processing status indicator
   - Semantic search interface
   - Collection management
   - Document list with delete actions
   - Embedding statistics display

**Effort:** Medium - Backend complete, needs frontend page

---

## 4. OPPORTUNITIES FOR ENHANCEMENT

### A. Learning Infrastructure Display (Session 309)
The learning hooks we just verified in Session 309 are creating:
- `AgentKnowledgeSource` records (10+ in database)
- `AgentMemory` records (5+ with embeddings)

**Opportunity:** Add a dedicated UI section to visualize:
- Knowledge shared between agents (who shared what with whom)
- Memory creation timeline
- Cross-agent knowledge flow diagram

**Effort:** Medium (UI already has agent learning tab, just needs enhancement)

### B. Clean Architecture Agents Visibility
11 clean architecture agents exist in `core/agents/`:
- ImageAgent, VideoAgent, AudioAgent, ThreeDAgent
- ResearchAgent, PersonalAssistantAgent
- ImageEditingAgent
- Business: CompetitorAnalysisAgent, CustomerResearchAgent
- Executive: CTOAgent, COOAgent
- Strategy: ContentStrategyAgent, etc.

**Opportunity:** The Agents Overview tab could show:
- Which agents are "clean architecture" vs "deprecated"
- Agent capabilities and tools
- Real-time routing decisions

**Effort:** Low (data exists, needs UI display)

### C. Knowledge Sharing Network Visualization
The learning mixins enable knowledge flow:
```
TrendAnalysis → ContentStrategy → SEO → BrandIdentity
```

**Opportunity:** Create a network graph showing:
- Which agents share knowledge with which
- Volume of knowledge shared
- Most valuable knowledge sources

**Effort:** Medium (needs d3.js or similar for visualization)

### D. Revenue/Opportunity Pipeline
Backend has complete revenue tracking but UI display may be limited:
- `OpportunityAgent` scoring
- Revenue attribution
- Outcome tracking

**Opportunity:** Enhance Revenue Dashboard with:
- Agent contribution to revenue
- Opportunity-to-revenue conversion tracking
- Learning impact on revenue

**Effort:** Medium

### E. Agent Personalities in UI (Session 256)
MBTI-style personalities are implemented but could be more prominent:

**Opportunity:**
- Show personality type on agent cards
- Personality-based agent recommendations
- Compatibility scores in team formation

**Effort:** Low (backend complete, UI enhancement)

---

## 5. MINOR DISCONNECTIONS TO FIX

### A. Memory Cluster Visualization Canvas
- **UI:** Canvas element exists for visualization
- **Backend:** API returns cluster data
- **Issue:** Visualization logic may need d3.js integration

### B. Time Travel Replay Animation
- **UI:** Timeline exists
- **Backend:** Decision points stored
- **Issue:** Smooth animation/replay could be enhanced

### C. Agent Rivalry/Alliance Display
- **UI:** Mentioned in intelligence tab
- **Backend:** Models exist but may need dedicated API
- **Status:** Partially implemented

---

## 6. RECOMMENDED PRIORITIES

### High Priority (Quick Wins)
1. **RAG/Document Management UI** - Backend complete with 7,239 embeddings, needs frontend (Session 731)
2. **Add Knowledge Flow Display** - Show the Session 309 learning data in UI
3. **Clean vs Deprecated Agent Badge** - Visual indicator on agent cards
4. **Personality Display on Agent Cards** - Already in DB, just display

### Medium Priority (Good ROI)
5. **Knowledge Network Graph** - Visualize agent-to-agent knowledge sharing
6. **Revenue Attribution Display** - Show which agents drive revenue
7. **Memory Timeline View** - Chronological view of agent memories

### Lower Priority (Nice to Have)
8. **Advanced Time Travel Animations** - Smoother replay
9. **3D Memory Palace Visualization** - More immersive UI
10. **Real-time Collaboration Enhancements** - Multi-user features

---

## 7. ARCHITECTURE SUMMARY

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (UI)                           │
├─────────────────────────────────────────────────────────────┤
│ ai_image_studio.html (57,661 lines)                        │
│ ├── 18 Primary Tabs                                         │
│ ├── Agent Panel (6 sub-tabs with 15 sci-fi features)       │
│ ├── Intelligence Panel (4 sub-tabs, 70 spiders)            │
│ └── partials/js/ (30,617 lines of feature modules)         │
├─────────────────────────────────────────────────────────────┤
│                     API LAYER                                │
├─────────────────────────────────────────────────────────────┤
│ 84+ REST API endpoints                                      │
│ 30+ WebSocket routes                                        │
│ ├── views_spider_intelligence.py (8 endpoints)             │
│ ├── views_agent_mood.py (9 endpoints)                       │
│ ├── views_agent_evolution.py (9 endpoints)                  │
│ ├── views_memory_palace.py (12 endpoints)                   │
│ ├── views_hive_mind.py (5 endpoints)                        │
│ ├── views_time_travel.py (16 endpoints)                     │
│ ├── views_predictions.py (9 endpoints)                      │
│ └── views_agent_learning.py (10 endpoints)                  │
├─────────────────────────────────────────────────────────────┤
│                     AGENT LAYER                              │
├─────────────────────────────────────────────────────────────┤
│ Clean Architecture (11 agents in core/agents/)              │
│ ├── Image, Video, Audio, 3D, Research                       │
│ ├── PersonalAssistant, ImageEditing                         │
│ ├── Business: CompetitorAnalysis, CustomerResearch          │
│ └── Executive: CTO, COO                                     │
│                                                              │
│ Deprecated with Learning (14 agents in agents/_deprecated/) │
│ ├── Session 305-308: All wired with learning hooks         │
│ └── Knowledge sharing + Memory creation verified            │
│                                                              │
│ Standalone (3 agents)                                        │
│ └── Bookmaker, Creation, OpportunityPipelineOrchestrator   │
├─────────────────────────────────────────────────────────────┤
│                     DATA LAYER                               │
├─────────────────────────────────────────────────────────────┤
│ models_unified_system.py                                    │
│ ├── Agent, AgentKnowledgeSource, AgentMemory               │
│ ├── AgentMood, AgentEvolution, AgentDream                  │
│ ├── MemoryPalaceRoom, MemoryCluster                        │
│ ├── HiveMindSession, HiveMindContribution                  │
│ ├── AgentSession, DecisionPoint (Time Travel)              │
│ └── PredictionStats (Prophecies)                            │
│                                                              │
│ Spider Data: 70 spiders, 3,000+ entries                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. NEXT STEPS

1. **Choose enhancement priority** - Which opportunities to tackle first
2. **Create specific tasks** - Break down chosen enhancements
3. **Implement incrementally** - Start with quick wins
4. **Verify connections** - Test each enhancement end-to-end

---

**Status:** Platform is 95%+ connected. Main gap is RAG/Document UI (Session 731). Most work would be enhancements rather than fixes.
