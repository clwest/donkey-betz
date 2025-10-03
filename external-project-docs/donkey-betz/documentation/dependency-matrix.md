# System Dependency Matrix - Donkey Betz Platform

## Overview
This matrix maps dependencies between all 8 major systems, showing what each system depends on and what depends on it. Critical broken dependencies are highlighted.

## Dependency Matrix

| System | Depends On | Used By | Critical Dependencies | Status |
|--------|------------|---------|----------------------|--------|
| **A: AI Agents & Orchestra** | • Memory System (C) ❌<br>• External APIs (E) ❌<br>• Infrastructure (G) ✅<br>• Security (H) ⚠️ | • Dashboard (F)<br>• Business Intel (D)<br>• Content Pipeline (B) | • UKF Memory Access ❌<br>• External API Bridge ❌<br>• Celery Tasks ✅ | 🔴 Critical |
| **B: Content Pipeline** | • AI Agents (A) ⚠️<br>• External APIs (E) ⚠️<br>• Infrastructure (G) ✅<br>• Security (H) ✅ | • Dashboard (F)<br>• Business Intel (D) | • AI Generation APIs ⚠️<br>• DaVinci Resolve ❌<br>• YouTube OAuth ⚠️ | 🟡 Partial |
| **C: Memory & Knowledge** | • Infrastructure (G) ✅<br>• External APIs (E) ✅ | • AI Agents (A) ❌<br>• Dashboard (F) ⚠️ | • OpenAI Embeddings ✅<br>• PostgreSQL+pgvector ✅<br>• Redis Cache ✅ | 🔴 Critical |
| **D: Business Intelligence** | • AI Agents (A) ❌<br>• External APIs (E) ❌<br>• Memory System (C) ❌<br>• Infrastructure (G) ✅ | • Dashboard (F) | • Stock APIs ❌<br>• Reddit API ❌<br>• Agent Orchestra ❌ | 🔴 Critical |
| **E: External Integrations** | • Infrastructure (G) ✅<br>• Security (H) ✅ | • AI Agents (A) ❌<br>• Content Pipeline (B) ⚠️<br>• Business Intel (D) ❌ | • API Keys ✅<br>• Network Access ✅<br>• Async Runtime ✅ | 🟡 Isolated |
| **F: Dashboard & UI** | • All Systems (A-H)<br>• WebSocket (G) ✅<br>• APIs ⚠️ | • End Users | • Real Data Sources ❌<br>• WebSocket Events ✅<br>• Authentication ⚠️ | 🟡 Partial |
| **G: Infrastructure** | • None (Foundation) | • All Systems (A-H) | • PostgreSQL ✅<br>• Redis ✅<br>• Celery ✅<br>• Django ✅ | 🟢 Good |
| **H: Security & Compliance** | • Infrastructure (G) ✅ | • All Systems (A-H) | • Django Auth ✅<br>• JWT Library ✅<br>• Encryption ✅ | 🟡 Partial |

## Critical Dependency Breakdowns

### 1. Agent → Memory System (COMPLETE FAILURE)
```
Dependency Chain:
AI Agents (A) → Memory System (C) → Knowledge Retrieval

Breakpoint: AgentTemplate models have no UKF integration
Impact: 0% of agents can access 3,678 UKF entries + 32,000 legacy memories
Fix Required: Update all 74 agent templates with memory service
```

### 2. Agents → External APIs (COMPLETE FAILURE)
```
Dependency Chain:
AI Agents (A) → External Integration (E) → 25+ APIs

Breakpoint: Import errors in tool implementations
Impact: Agents promise stock/news/data access but have none
Fix Required: Implement proper API client imports and error handling
```

### 3. Business Intelligence → Everything (CASCADING FAILURE)
```
Dependency Chain:
Business Intel (D) → Agents (A) → APIs (E) → Data

Breakpoints: 
- Event loop error in orchestrator
- No agent access to APIs
- Mock data fallbacks

Impact: Entire BI system non-functional despite UI
Fix Required: Async/await boundary repair + API integration
```

### 4. Dashboard → Real Data (TRUST FAILURE)
```
Dependency Chain:
Dashboard (F) → All Systems → Actual Data

Breakpoint: Systems return mock data, dashboard displays as real
Impact: Users see fake $125,432 portfolios
Fix Required: Data source verification + "Demo Mode" indicators
```

## Shared Resource Dependencies

### PostgreSQL Database
| Dependent System | Usage | Status | Issues |
|-----------------|-------|--------|--------|
| All Systems | Primary data store | ✅ Working | None |
| Memory System | pgvector embeddings | ✅ Working | 28% missing embeddings |
| Infrastructure | Connection pooling | ✅ Working | None |

### Redis Cache/Queue
| Dependent System | Usage | Status | Issues |
|-----------------|-------|--------|--------|
| Infrastructure | Celery broker | ✅ Working | None |
| Dashboard | Widget cache | ✅ Working | No invalidation |
| Memory System | Search cache | ✅ Working | None |
| WebSocket | Channel layer | ✅ Working | Underutilized |

### External API Keys (40+)
| Dependent System | APIs Needed | Status | Issues |
|-----------------|------------|--------|--------|
| AI Agents | OpenAI, Anthropic, Google | ✅ Configured | ❌ Not accessible to agents |
| Business Intel | Polygon, Reddit, News | ✅ Configured | ❌ Not used |
| Content Pipeline | Runway, ClipDrop, Replicate | ⚠️ Limited | Credits running low |
| External Integration | All 25+ APIs | ✅ Configured | ❌ Isolated from agents |

## Dependency Health Analysis

### Healthy Dependencies (Working as Designed)
1. **All → Infrastructure**: Every system successfully uses Redis, PostgreSQL, Celery
2. **All → Security**: Authentication and authorization properly integrated
3. **Infrastructure → None**: Correctly has no dependencies (foundation layer)

### Broken Dependencies (Complete Failures)
1. **Agents → Memory**: 0% integration despite design
2. **Agents → External APIs**: Import failures prevent access
3. **Business Intel → Agents**: Event loop prevents execution
4. **Dashboard → Real Data**: Shows mock data as real

### Partial Dependencies (Degraded Function)
1. **Content Pipeline → External APIs**: Works with credits, fails without
2. **Dashboard → All Systems**: Gets data but often mock
3. **Security → All Systems**: Works except in DEBUG mode

## Circular Dependencies

### Identified Circular Dependencies:
1. **None Found**: Architecture properly layered

### Potential Circular Risks:
1. **Agents ↔ Memory**: If memory starts depending on agents for organization
2. **Dashboard ↔ Business Intel**: If BI starts updating dashboard directly

## Missing Dependencies

### Critical Missing Dependencies:
1. **Event Bus**: No system-wide event propagation
2. **Service Discovery**: Hardcoded service locations  
3. **Circuit Breakers**: No fallback for failed dependencies
4. **Health Checks**: No automated dependency monitoring

## Dependency Version Analysis

### Python Package Dependencies:
```
Critical Versions:
- Django: 4.2.x (LTS) ✅
- Celery: 5.3.x ✅
- Redis: 5.0.x ✅  
- PostgreSQL: 15.x ✅
- pgvector: 0.2.x ✅

AI/ML Dependencies:
- openai: 1.x ✅
- anthropic: 0.x ✅
- langchain: 0.1.x ⚠️ (rapid changes)
```

### JavaScript Dependencies:
```
Frontend Framework:
- React: 18.x ✅
- TypeScript: 5.x ✅
- Vite: 5.x ✅

State Management:
- Zustand: 4.x ✅
- React Query: 5.x ✅
```

## Deployment Dependencies

### Missing Deployment Dependencies:
1. **Docker Compose**: Present but incomplete
2. **Kubernetes**: No configs found
3. **Terraform**: No infrastructure as code
4. **CI/CD**: No pipeline configuration

### Runtime Dependencies:
1. **Environment Variables**: 40+ required
2. **File Storage**: Local or S3 required
3. **Background Workers**: Celery required
4. **WebSocket Server**: Daphne/Channels required

## Recommendations

### Priority 1: Fix Critical Dependencies
1. **Connect Agents → Memory System**
   - Update agent templates
   - Add memory service to context
   - Test with pilot agents

2. **Connect Agents → External APIs**
   - Fix import errors
   - Add proper error handling
   - Create fallback strategies

3. **Fix Business Intelligence → Agents**
   - Resolve event loop issues
   - Test async boundaries
   - Remove mock fallbacks

### Priority 2: Add Missing Dependencies
1. **Implement Circuit Breakers**
   - Prevent cascade failures
   - Graceful degradation
   - User notifications

2. **Add Health Monitoring**
   - Dependency status checks
   - Automated alerts
   - Dashboard indicators

3. **Create Event Bus**
   - System-wide propagation
   - Loose coupling
   - Better scalability

### Priority 3: Document Dependencies
1. **Create Dependency Graph**
   - Visual representation
   - Update with changes
   - Part of onboarding

2. **Version Lock File**
   - Exact versions
   - Security updates
   - Compatibility matrix

## Dependency Risk Score

| Risk Level | Count | Examples |
|------------|-------|----------|
| 🔴 **Critical** | 4 | Agent→Memory, Agent→APIs, BI→Agents, Dashboard→Data |
| 🟡 **High** | 3 | Pipeline→APIs, Security→DEBUG, Memory→Embeddings |
| 🟢 **Low** | 5 | All→Infrastructure, All→Security, DB dependencies |

**Overall Platform Dependency Health: 33% - Critical Issues**

The platform's dependency structure is well-designed but poorly implemented, with critical connections completely broken between major systems.