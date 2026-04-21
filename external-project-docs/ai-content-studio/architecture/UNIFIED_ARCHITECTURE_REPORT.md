# Unified Architecture Plan: AI Content Studio + DBAO Integration

## Executive Summary

This report analyzes the merger of **AI Content Studio** (Django + React/React Native content platform) with **Donkey Betz Agent Orchestra (DBAO)** (Agent orchestration + sports betting system). Both systems have complementary but overlapping functionality that requires careful unification to avoid conflicts while maximizing synergies.

## Current State Analysis

### AI Content Studio (Port 8001)
- **Backend**: Django 4.2+ with DRF, PostgreSQL + pgvector
- **Frontend**: React Web App (port 8080) + React Native Mobile (port 8081)  
- **Key Features**: Content generation, voice studio, memory system, style learning
- **Agent System**: Basic enhanced assistant with execution capabilities
- **WebSocket**: Assistant communication (`/ws/assistant/`, `/ws/agents/`)
- **API Auth**: Token-based authentication

### DBAO (Port 8000)  
- **Backend**: Django with advanced agent orchestration
- **Key Features**: Multi-agent coordination, sports betting analysis, RAG diagnostics
- **Agent System**: Sophisticated orchestration with communication protocols
- **WebSocket**: Multiple consumers (`/ws/agents/`, `/ws/dashboard/`, `/ws/sports/`, `/ws/unified/`)
- **API Architecture**: RESTful with comprehensive retry/error handling

## Identified Overlaps and Conflicts

### 1. Agent Systems Overlap
| Feature | AI Content Studio | DBAO | Resolution |
|---------|-------------------|------|------------|
| Agent Communication | Basic message passing | Advanced protocol with priorities | **Adopt DBAO protocol** |
| Agent Registration | Manual agent profiles | Automatic capability discovery | **Merge both approaches** |
| Execution Tracking | Session-based storage | Comprehensive metrics | **Use DBAO metrics + sessions** |
| Memory Integration | Conversation memory only | Multi-agent memory sharing | **Unify memory systems** |

### 2. WebSocket Routing Conflicts
| Route | AI Content Studio | DBAO | Resolution |
|-------|-------------------|------|------------|
| `/ws/assistant/` | Assistant chat | Assistant + ping/pong | **Merge consumers** |
| `/ws/agents/` | Basic agent updates | Agent execution updates | **Use DBAO implementation** |
| `/ws/dashboard/` | Not present | Dashboard real-time data | **Keep DBAO route** |
| `/ws/sports/` | Not present | Sports betting updates | **Keep DBAO route** |

### 3. API Endpoint Conflicts
- Both systems have `/api/agents/` endpoints with different schemas
- Authentication mechanisms differ (simple token vs comprehensive auth)
- Error handling patterns vary significantly

## Proposed Unified Architecture

```
                         UNIFIED AI CONTENT STUDIO + DBAO
                                    (Port 8001)
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
            ┌───────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
            │   React Web  │    │    Django   │    │React Native │
            │   (Port 8080)│    │   Backend   │    │(Port 8081)  │
            └──────────────┘    └─────────────┘    └─────────────┘
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        │
                    ┌───────────────────▼───────────────────┐
                    │          UNIFIED SERVICE LAYER         │
                    │  ┌─────────────────────────────────┐  │
                    │  │     Agent Orchestra Manager      │  │
                    │  │   (Enhanced from DBAO + ACS)    │  │
                    │  └─────────────────────────────────┘  │
                    │  ┌─────────────────────────────────┐  │
                    │  │    Communication Protocol       │  │
                    │  │  (DBAO Enhanced + ACS Memory)   │  │
                    │  └─────────────────────────────────┘  │
                    │  ┌─────────────────────────────────┐  │
                    │  │      Memory Gateway             │  │
                    │  │   (Unified ACS + DBAO Memory)   │  │
                    │  └─────────────────────────────────┘  │
                    └────────────────────────────────────────┘
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            │                           │                           │
    ┌───────▼───────┐        ┌─────────▼─────────┐        ┌───────▼───────┐
    │Content Gen    │        │  Agent Orchestra  │        │Sports Betting │
    │• Image/Video  │        │• Multi-agent      │        │• Live data    │
    │• Blog/Social  │        │• Task routing     │        │• Kelly calc   │
    │• Voice/eBook  │        │• Workflow mgmt    │        │• Arbitrage    │
    └───────────────┘        └───────────────────┘        └───────────────┘
```

## WebSocket Unification Strategy

### Consolidated WebSocket Routes (Port 8001)
```
/ws/assistant/          -> Enhanced with DBAO ping/pong + ACS chat
/ws/agents/             -> DBAO agent execution + ACS memory integration  
/ws/dashboard/          -> DBAO dashboard + ACS analytics
/ws/sports/             -> DBAO sports betting (preserved)
/ws/unified/            -> Combined updates for mobile app
```

### Route Migration Plan
1. **Preserve DBAO WebSocket infrastructure** (superior implementation)
2. **Integrate ACS memory/session context** into DBAO consumers
3. **Add authentication bridge** for seamless user experience
4. **Implement gradual migration** with feature flags

## API Endpoint Consolidation

### Unified API Schema (Port 8001)
```
/api/v1/
├── agents/
│   ├── templates/              # DBAO agent templates
│   ├── instances/              # DBAO execution instances  
│   ├── execute/                # Enhanced with ACS content generation
│   ├── suggest/                # DBAO routing + ACS preferences
│   └── orchestrate/            # DBAO workflows + ACS memory
├── content/                    # ACS content generation (preserved)
│   ├── generate/
│   ├── batch/
│   └── transform/
├── assistant/                  # Enhanced ACS assistant
│   ├── chat/                   # Integration with DBAO agents
│   ├── enhanced-execute/       # Bridge to DBAO orchestration
│   └── capabilities/
├── sports/                     # DBAO sports betting (preserved)
│   ├── leagues/
│   ├── games/
│   └── markets/
└── betting/                    # DBAO betting analysis (preserved)
    ├── analyze/
    ├── live/
    └── arbitrage/
```

## Implementation Checklist

### Phase 1: Foundation & Safety (Week 1)
- [ ] **Backup both systems** completely
- [ ] **Set up unified development environment** with both ports accessible
- [ ] **Create feature flags** for gradual migration control
- [ ] **Implement health checks** for both systems during transition
- [ ] **Test React Native compatibility** with unified backend

### Phase 2: Agent System Unification (Week 2) 
- [ ] **Integrate DBAO communication protocol** into ACS
- [ ] **Merge agent registration systems** (auto-discovery + profiles)
- [ ] **Unify memory systems** (DBAO sharing + ACS personal memory)
- [ ] **Bridge enhanced assistant** to DBAO orchestration
- [ ] **Test agent execution** with content generation workflows

### Phase 3: WebSocket Consolidation (Week 3)
- [ ] **Migrate WebSocket consumers** from port 8000 to 8001
- [ ] **Implement authentication bridge** for seamless user experience  
- [ ] **Add React Native WebSocket support** for sports/betting features
- [ ] **Test real-time updates** across all client applications
- [ ] **Implement connection fallback strategies**

### Phase 4: API Integration (Week 4)
- [ ] **Consolidate API endpoints** under `/api/v1/` structure
- [ ] **Implement unified error handling** (DBAO patterns)
- [ ] **Add comprehensive logging** and monitoring
- [ ] **Update frontend API clients** to use unified endpoints
- [ ] **Test cross-system workflows** (content → betting analysis)

### Phase 5: Testing & Optimization (Week 5)
- [ ] **Comprehensive integration testing** of all systems
- [ ] **Performance optimization** (database queries, WebSocket efficiency)
- [ ] **Mobile app testing** with unified backend
- [ ] **Load testing** with concurrent users
- [ ] **Security audit** of unified authentication

### Phase 6: Production Deployment (Week 6)
- [ ] **Gradual rollout** with feature flag controls
- [ ] **Monitor system performance** and user experience
- [ ] **Database migration** scripts for production
- [ ] **Rollback procedures** if issues arise
- [ ] **Documentation updates** for unified system

## Risk Assessment & Mitigation

### High Risk Areas
1. **WebSocket conflicts** between React Native and new routes
   - **Mitigation**: Comprehensive testing on iOS/Android devices
   - **Rollback**: Keep original WebSocket routes during transition

2. **Database conflicts** between PostgreSQL schemas
   - **Mitigation**: Use separate schemas with cross-references
   - **Rollback**: Database backup/restore procedures

3. **Authentication disruption** for existing users
   - **Mitigation**: Token migration strategy with backward compatibility
   - **Rollback**: Preserve original auth endpoints during transition

### Medium Risk Areas  
1. **Performance degradation** from increased system complexity
   - **Mitigation**: Load testing and performance monitoring
   - **Solution**: Optimize database queries and caching

2. **Mobile app breakage** from API changes
   - **Mitigation**: API versioning and gradual migration
   - **Solution**: Comprehensive mobile testing

## Configuration Templates

### Unified Django Settings
```python
# /Users/donkeyking/development/ai-content-studio/backend/core/settings.py

INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth', 
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'corsheaders', 
    'channels',
    'django_celery_beat',
    'django_celery_results',
    
    # AI Content Studio apps (preserved)
    'content',
    'assistant',
    'memory',
    'integrations',
    
    # DBAO apps (integrated)
    'agents',
    'api',
    'odds_calculator', 
    'ws',
    'betting_tools.apps.BettingToolsConfig',
    'monitoring.apps.MonitoringConfig',
    'apps.odds',
    'apps.sports.apps.SportsConfig',
]

# Unified WebSocket configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.environ.get('REDIS_HOST', '127.0.0.1'), 6379)],
        },
    },
}

# Unified CORS configuration
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',    # React dev
    'http://localhost:8080',    # React web app  
    'http://localhost:8081',    # React Native mobile
]

# Agent Orchestra configuration (enhanced)
AGENT_ORCHESTRA = {
    'MAX_CONCURRENT_AGENTS': 15,  # Increased for content + betting
    'DEFAULT_TIMEOUT': 300,
    'ROUTING_CONFIDENCE_THRESHOLD': 0.85,
    'ENABLE_MEMORY_SYSTEM': True,  # Enable ACS memory integration
    'ENABLE_CONTENT_GENERATION': True,  # Enable ACS content features
    'ENABLE_SPORTS_BETTING': True,  # Enable DBAO sports features
}
```

### Unified WebSocket Routing
```python
# /Users/donkeyking/development/ai-content-studio/backend/assistant/routing.py

from django.urls import re_path
from . import consumers
from .consumers_agents import AgentsConsumer
# Import DBAO consumers
from api.websocket_consumers import DashboardConsumer
from apps.sports.consumers import SportsConsumer, GeneralSportsConsumer

websocket_urlpatterns = [
    # Enhanced assistant (ACS + DBAO)
    re_path(r'ws/assistant/$', consumers.EnhancedAssistantConsumer.as_asgi()),
    
    # Agent orchestration (DBAO primary)
    re_path(r'ws/agents/$', AgentsConsumer.as_asgi()),
    
    # Dashboard (DBAO)
    re_path(r'ws/dashboard/$', DashboardConsumer.as_asgi()),
    
    # Sports betting (DBAO) 
    re_path(r'ws/sports/$', SportsConsumer.as_asgi()),
    
    # Unified updates for mobile (DBAO)
    re_path(r'ws/unified/$', GeneralSportsConsumer.as_asgi()),
]
```

## Test Verification Script

```bash
#!/bin/bash
# /Users/donkeyking/development/ai-content-studio/unified_system_test.sh

echo "🧪 Unified System Verification Test"
echo "====================================="

# Test React Web App
echo "1. Testing React Web App (port 8080)..."
curl -s http://localhost:8080/health || echo "❌ React Web App not accessible"

# Test React Native compatibility  
echo "2. Testing unified backend API..."
curl -s -H "Authorization: Token <redacted-993f8273-2026-04-20>" \
     http://localhost:8001/api/health/ || echo "❌ Backend API not accessible"

# Test agent orchestration
echo "3. Testing agent orchestration..."
curl -s -X POST \
     -H "Authorization: Token <redacted-993f8273-2026-04-20>" \
     -H "Content-Type: application/json" \
     -d '{"agent_type":"research","task_description":"Test task"}' \
     http://localhost:8001/api/agents/execute/ || echo "❌ Agent execution failed"

# Test sports betting integration
echo "4. Testing sports betting..."
curl -s -H "Authorization: Token <redacted-993f8273-2026-04-20>" \
     http://localhost:8001/api/sports/leagues/ || echo "❌ Sports API not accessible"

# Test WebSocket connections
echo "5. Testing WebSocket connectivity..."
# Note: WebSocket testing requires a WebSocket client tool
echo "   Manual test required for WebSocket routes"

echo "====================================="
echo "✅ Unified system verification complete"
```

## Next Steps

1. **Begin with Phase 1** (Foundation & Safety) immediately
2. **Set up development environment** with both systems running
3. **Create detailed migration scripts** for database integration  
4. **Plan React Native testing strategy** for sports betting features
5. **Establish rollback procedures** for each phase

This unified architecture plan provides a comprehensive roadmap for merging both systems while maintaining stability and functionality. The phased approach ensures minimal disruption to existing users while maximizing the benefits of both platforms.