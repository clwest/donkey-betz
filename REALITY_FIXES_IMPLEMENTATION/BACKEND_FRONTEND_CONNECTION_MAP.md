# 🔌 Backend → Frontend Connection Map
**Generated:** September 28, 2025
**Purpose:** Complete mapping of data flow from backend to frontend
**Status:** DISCOVERY COMPLETE - TESTING NEEDED

---

## 🎯 Executive Summary

The system uses **Django templates with heavy inline JavaScript** and **extensive WebSocket connections** for real-time updates. This is NOT a React SPA - it's a Django server-rendered application with WebSocket-powered real-time features.

**Key Discovery:** 60+ WebSocket endpoints configured, but many templates hardcode `localhost:8000` instead of dynamic URLs!

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL → Django Models → Views/Consumers → Templates   │
│                              ↓                               │
│                      WebSocket Consumers                     │
│                              ↓                               │
├─────────────────────────────────────────────────────────────┤
│                         FRONTEND                             │
│  Django Templates + Inline JS → WebSocket connections        │
│                              ↓                               │
│                    Real-time UI Updates                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📡 WebSocket Connection Map

### Critical WebSocket Routes (60+ total!)

| Endpoint | Consumer | Purpose | Used By |
|----------|----------|---------|---------|
| `/ws/consciousness/` | ConsciousnessConsumer | Self-awareness updates | AI Nexus |
| `/ws/command-center/` | CommandCenterAIConsumer | Command center AI | Command Center |
| `/ws/decision-command/` | DecisionCommandConsumer | Decision execution | Decision Command |
| `/ws/revenue-dashboard/` | RevenueDashboardConsumer | Revenue updates | Revenue Dashboard |
| `/ws/agent-monitor/` | AgentMonitorConsumer | 152 agent monitoring | Agent Monitor |
| `/ws/income-builder/` | UnifiedWebSocketHub | Income opportunities | Income Builder |
| `/ws/neural-orchestra/` | NeuralOrchestraConsumer | Agent visualization | Neural Orchestra |
| `/ws/build-activity/` | RealAgentOrchestraConsumer | Build progress | AI Production Hub |
| `/ws/ai-training/` | AITrainingConsumer | Training updates | AI Training |
| `/ws/spider-updates/` | SpiderWebSocketConsumer | Spider network | Spider Dashboard |
| `/ws/freelance/` | FreelanceConsumer | Freelance opportunities | Freelance Hub |
| `/ws/agent-platform/` | AgentPlatformConsumer | Agent work platform | Agent Platform |
| `/ws/deliverables/` | DeliverablesConsumer | Deliverable tracking | Deliverables |
| `/ws/autonomous-system/` | AutonomousSystemConsumer | 30-day autonomous run | Autonomous System |

### Platform Unification WebSockets

| Endpoint | Purpose |
|----------|---------|
| `/ws/platform-orchestrator/` | Platform unification control |
| `/ws/content-intelligence-pipeline/` | Content-intelligence flow |
| `/ws/agent-content-factory/` | Agent content generation |
| `/ws/revenue-pipeline-monitor/` | Revenue pipeline tracking |

---

## 🌐 HTTP API Endpoints

### Core APIs (from urls.py)

| Endpoint | View/Handler | Purpose |
|----------|--------------|---------|
| `/api/agents/test-status/` | agent_testing | Agent test status |
| `/api/diagnostics/` | diagnostics | System diagnostics |
| `/api/intelligence/` | intelligence_api | Intelligence data |
| `/api/v1/content/documents/` | content API | Document management |
| `/api/learning/stats/` | learning stats | Learning statistics |
| `/api/projects/` | project management | Project CRUD |
| `/api/consciousness/data/` | consciousness data | Consciousness metrics |
| `/api/income-builder/opportunities/` | income opportunities | Job opportunities |
| `/api/sports/predictions/` | sports predictions | Sports betting |
| `/api/agents/list/` | agent registry | List all agents |
| `/api/revenue/summary/` | revenue summary | Revenue tracking |

---

## 📄 Template → Backend Connections

### Key Templates and Their Data Sources

| Template | View Function | WebSocket Connections | API Calls |
|----------|---------------|----------------------|-----------|
| `ai_nexus.html` | Direct render | `/ws/consciousness/`, `/ws/command-center/` | Multiple fetch() |
| `command_center.html` | `views_command_center.command_center` | `/ws/command-center/` | `/api/intelligence/` |
| `consciousness_dashboard.html` | `views_consciousness.consciousness_dashboard` | `/ws/consciousness/` | `/api/consciousness/data/` |
| `content_studio.html` | Direct render | None found | `/api/v1/content/documents/` |
| `ai_production_hub.html` | Direct render | `/ws/build-activity/` | `/api/projects/`, `/api/learning/stats/` |
| `diagnostic_dashboard.html` | `views_diagnostics.diagnostic_dashboard` | `/ws/decision-command/` (hardcoded!) | `/api/diagnostics/` |

---

## 🚨 Critical Issues Found

### 1. Hardcoded WebSocket URLs
```javascript
// In diagnostic_dashboard.html:
ws = new WebSocket('ws://localhost:8000/ws/decision-command/');
// PROBLEM: Won't work in production!
```

**Should be:**
```javascript
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
ws = new WebSocket(`${protocol}//${window.location.host}/ws/decision-command/`);
```

### 2. Missing WebSocket Connections
Several components have consumers but no frontend connections:
- Income Builder (has consumer, no template WebSocket)
- Revenue Dashboard (has consumer, needs verification)
- Decision Command (hardcoded localhost)

### 3. Duplicate/Conflicting Routes
Multiple intelligence modules creating confusion:
- `/intelligence/` (directory)
- `/ai_core/intelligence/` (directory)
- Similar duplicate for `/agents/`

---

## 📊 Data Flow Pipelines

### 1. Opportunity Pipeline
```
Spiders → Spider Items DB → Opportunity Aggregator → WebSocket → Income Builder UI
         ↓
    Spider Consumer → `/ws/spider-updates/` → Frontend Updates
```

### 2. Revenue Pipeline
```
Revenue Events → Revenue Model → RevenueDashboardConsumer → `/ws/revenue-dashboard/` → Dashboard UI
                ↓
          Redis Cache → Optimized delivery
```

### 3. Agent Activity Pipeline
```
Agent Execution → Agent Monitor → `/ws/agent-monitor/` → Neural Orchestra Visualization
                ↓
          Activity Feed → Real-time updates
```

### 4. Decision Command Pipeline
```
User Input → DecisionCommandConsumer → AIIncomeBuilder → Opportunities
           ↓
     WebSocket Response → UI Update (BROKEN - hardcoded localhost!)
```

---

## 🔧 WebSocket Consumer Analysis

### Key Consumer Files

| File | Consumers | Status |
|------|-----------|--------|
| `core/consumers.py` | Multiple base consumers | ✅ Active |
| `core/consumers_consciousness.py` | ConsciousnessConsumer | ✅ Active |
| `core/agent_monitor_consumer.py` | AgentMonitorConsumer | ✅ Active |
| `core/decision_command_consumer.py` | DecisionCommandConsumer | ⚠️ Needs frontend fix |
| `core/revenue_dashboard_consumer.py` | RevenueDashboardConsumer | ❓ Needs verification |
| `core/agent_platform_consumer.py` | AgentPlatformConsumer | ✅ Active |
| `core/unified_hub.py` | UnifiedWebSocketHub | ✅ Base class |
| `ai_core/api/spider_websocket.py` | SpiderWebSocketConsumer | ✅ Active |

---

## 🎯 Component Status Check

| Component | Backend Ready | WebSocket Config | Frontend Connected | Status |
|-----------|--------------|------------------|-------------------|--------|
| **Income Builder** | ✅ | ✅ `/ws/income-builder/` | ❌ No WS in template | 🔴 Disconnected |
| **Revenue Dashboard** | ✅ | ✅ `/ws/revenue-dashboard/` | ❓ Needs verification | 🟡 Unknown |
| **Decision Command** | ✅ | ✅ `/ws/decision-command/` | ⚠️ Hardcoded localhost | 🟡 Broken |
| **Neural Orchestra** | ✅ | ✅ `/ws/neural-orchestra/` | ❓ Needs verification | 🟡 Unknown |
| **Command Center** | ✅ | ✅ `/ws/command-center/` | ✅ Connected | 🟢 Working |
| **AI Nexus** | ✅ | ✅ Multiple | ✅ Connected | 🟢 Working |
| **Consciousness** | ✅ | ✅ `/ws/consciousness/` | ✅ Connected | 🟢 Working |

---

## 🔄 Authentication & Session Flow

1. **Django Sessions**: Primary auth mechanism
2. **WebSocket Auth**: Uses Django session cookies
3. **API Auth**: Session-based (no tokens found)
4. **CSRF Protection**: Enabled for POST requests

---

## 📝 Next Steps Required

### Immediate Fixes Needed:

1. **Fix Hardcoded WebSocket URLs**
   - File: `ai_core/templates/diagnostic_dashboard.html`
   - Change: `ws://localhost:8000` → dynamic URL

2. **Connect Income Builder WebSocket**
   - Template needs WebSocket connection
   - Consumer exists but unused

3. **Verify Revenue Dashboard Connection**
   - Check if WebSocket actually connects
   - Test real-time updates

4. **Test Decision Command Flow**
   - Fix hardcoded URL first
   - Verify AIIncomeBuilder integration

5. **Document Missing Connections**
   - Several templates have no clear data source
   - Need to trace view context data

---

## 🚀 Quick Test Commands

```bash
# 1. Start the server
python manage.py runserver

# 2. Test WebSocket connections (in browser console)
const ws = new WebSocket('ws://localhost:8000/ws/consciousness/');
ws.onmessage = (e) => console.log('Received:', JSON.parse(e.data));

# 3. Check channel layer
python manage.py shell
>>> from channels.layers import get_channel_layer
>>> channel_layer = get_channel_layer()
>>> print(channel_layer)
```

---

## 🎬 Testing Plan

1. **Start server and visit each component**
2. **Open browser DevTools Network tab**
3. **Check for WebSocket connections**
4. **Verify data flow for each pipeline**
5. **Fix broken connections**
6. **Document actual vs expected behavior**

---

*This map represents the current state of backend-frontend connections. Testing phase will reveal actual functionality.*