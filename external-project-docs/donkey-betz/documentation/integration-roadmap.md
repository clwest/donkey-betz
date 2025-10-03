# Integration Fix Roadmap - Donkey Betz Platform

## Overview
This roadmap provides a prioritized, actionable plan to fix the critical integration failures identified across the Donkey Betz platform. Fixes are organized by priority, complexity, and dependencies.

## Priority Framework

- 🔴 **P0 - Critical**: Platform unusable or legal risk
- 🟡 **P1 - High**: Major features broken
- 🟢 **P2 - Medium**: Degraded experience
- ⚪ **P3 - Low**: Nice to have

## Phase 1: Emergency Fixes (Week 1)

### 🔴 P0: Remove Security Bypasses
**Time**: 1 day
**Complexity**: Low
**Risk**: High if not done

```python
# 1. Update server/permissions.py
class UnrestrictedInDebugMode(BasePermission):
    def has_permission(self, request, view):
        # Remove automatic bypass
        if settings.DEBUG and settings.EXPLICIT_DEBUG_BYPASS:
            logger.warning(f"Debug bypass used by {request.user}")
            # Add to audit log
        return super().has_permission(request, view)

# 2. Add to settings
EXPLICIT_DEBUG_BYPASS = env.bool('ALLOW_DEBUG_BYPASS', False)
```

**Testing**:
- Verify all endpoints require auth in DEBUG mode
- Check WebSocket authentication enforced
- Audit log captures bypass attempts

### 🔴 P0: Add Mock Data Indicators
**Time**: 2 days
**Complexity**: Low
**Risk**: Legal liability if not done

```typescript
// 1. Create mock indicator component
const MockDataBadge: React.FC = () => (
  <Badge color="warning" className="mock-indicator">
    Demo Data
  </Badge>
);

// 2. Update all data displays
{data.isMock && <MockDataBadge />}

// 3. Add to API responses
return {
  data: mockData,
  _meta: {
    isMock: true,
    reason: "External API unavailable",
    timestamp: new Date()
  }
}
```

**Testing**:
- All mock data clearly labeled
- No financial data shown without indicator
- User notification when viewing mock data

### 🔴 P0: Secure JWT Storage
**Time**: 1 day
**Complexity**: Medium
**Risk**: High (XSS vulnerability)

```typescript
// 1. Move from localStorage to httpOnly cookies
// auth.service.ts
async login(credentials) {
  const response = await api.post('/auth/login', credentials, {
    withCredentials: true  // Include cookies
  });
  // Don't store token in localStorage
}

// 2. Update backend to set httpOnly cookie
response.set_cookie(
    'authToken',
    token,
    httponly=True,
    secure=True,
    samesite='strict'
)
```

**Testing**:
- Verify tokens not accessible via JavaScript
- Confirm auth still works across requests
- Test CSRF protection

## Phase 2: Core Integration Fixes (Weeks 2-3)

### 🔴 P0: Connect Agents to Memory System
**Time**: 1 week
**Complexity**: High
**Risk**: Medium

```python
# 1. Update agent template base class
class EnhancedAgentTemplate(AgentTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory_service = UnifiedMemoryService(self.user_id)
    
    async def get_context(self, query):
        # Search UKF for relevant memories
        memories = await self.memory_service.search_memories(
            query=query,
            agent_name=self.name,
            limit=10
        )
        return self._format_memories(memories)

# 2. Update all 74 agent templates
class BusinessAgent(EnhancedAgentTemplate):
    async def process(self, message):
        context = await self.get_context(message)
        # Include context in prompt
        
# 3. Create migration script
python manage.py migrate_agents_to_ukf
```

**Testing**:
- Verify agents retrieve relevant memories
- Check memory search performance
- Validate context quality improvement

### 🔴 P0: Fix Agent External API Access
**Time**: 3 days
**Complexity**: Medium
**Risk**: Low

```python
# 1. Fix import paths in tools
# agent_orchestra/tools/stock_tools.py
from agent_orchestra.services.polygon import PolygonStocksService
from agent_orchestra.services.alpha_vantage import AlphaVantageService

class StockAnalysisTool:
    def __init__(self):
        self.polygon = PolygonStocksService()
        self.alpha_vantage = AlphaVantageService()
        
    async def get_quote(self, ticker):
        try:
            return await self.polygon.get_real_time_quote(ticker)
        except Exception as e:
            logger.error(f"Polygon failed: {e}")
            # Try fallback
            return await self.alpha_vantage.get_quote(ticker)

# 2. Add to agent context
tools = [
    StockAnalysisTool(),
    NewsAnalysisTool(),
    RedditScoutTool()
]
```

**Testing**:
- Test each external API integration
- Verify fallback mechanisms work
- Check rate limiting compliance

### 🟡 P1: Fix Business Intelligence Event Loop
**Time**: 3 days
**Complexity**: High
**Risk**: Medium

```python
# 1. Fix async/sync boundary in orchestrator
# agent_orchestra/orchestrator.py
class TaskOrchestrator:
    async def deploy_agents(self, orchestration):
        # Create new event loop for thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run agent tasks
            tasks = []
            for agent in orchestration.agents.all():
                task = asyncio.create_task(
                    self._run_agent(agent)
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            return results
        finally:
            loop.close()

# 2. Update Celery task
@shared_task
def execute_orchestration(orchestration_id):
    orchestration = TaskOrchestration.objects.get(id=orchestration_id)
    
    # Use sync_to_async for Django ORM
    from asgiref.sync import async_to_sync
    results = async_to_sync(orchestrator.deploy_agents)(orchestration)
```

**Testing**:
- Deploy stock scout successfully
- Verify Reddit scout works
- Check task completion tracking

## Phase 3: Data Flow Restoration (Weeks 4-5)

### 🟡 P1: Connect Dashboard to Real Data
**Time**: 1 week
**Complexity**: Medium
**Risk**: Low

```typescript
// 1. Update dashboard service to use real endpoints
// services/dashboard.service.ts
class DashboardService {
  async getWidgetData(widgetId: string): Promise<WidgetData> {
    const endpoints = {
      'mission-control': '/api/dashboard/system-health/',
      'stock-intelligence': '/api/bi/portfolio-summary/',
      'agent-orchestra': '/api/agents/active-summary/'
    };
    
    const response = await api.get(endpoints[widgetId]);
    
    // Add data validation
    if (!response.data || Object.keys(response.data).length === 0) {
      return {
        ...FALLBACK_DATA[widgetId],
        _meta: {
          isFallback: true,
          reason: 'No data available'
        }
      };
    }
    
    return response.data;
  }
}

// 2. Update widgets to show data state
{data._meta?.isFallback && (
  <Alert>
    Using fallback data: {data._meta.reason}
  </Alert>
)}
```

**Testing**:
- Each widget shows real data when available
- Fallback clearly indicated
- No mock financial data

### 🟡 P1: Complete Content Pipeline Integration
**Time**: 1 week
**Complexity**: High
**Risk**: Medium

```python
# 1. Implement pipeline automation
class PipelineAutomation:
    async def process_stage(self, pipeline, stage):
        if stage.stage_type == 'obs_recording':
            await self.handle_obs_complete(pipeline, stage)
        elif stage.stage_type == 'ai_enhancement':
            await self.handle_ai_enhancement(pipeline, stage)
        elif stage.stage_type == 'davinci_edit':
            await self.handle_davinci_edit(pipeline, stage)
            
    async def handle_obs_complete(self, pipeline, stage):
        # Auto-trigger next stage
        next_stage = await self.get_next_stage(stage)
        if next_stage:
            await self.transition_to_stage(pipeline, next_stage)

# 2. Fix DaVinci connection
# First, document that DaVinci API requires Studio version
# Then implement proper error handling
class DaVinciService:
    def connect(self):
        if not self.check_davinci_running():
            raise DaVinciNotRunningError(
                "DaVinci Resolve Studio must be running"
            )
```

**Testing**:
- Pipeline progresses automatically
- Each stage transition logged
- Errors clearly reported

## Phase 4: Memory System Consolidation (Weeks 6-7)

### 🟡 P1: Generate Missing Embeddings
**Time**: 2 days
**Complexity**: Low
**Risk**: Low

```python
# 1. Create embedding generation script
# management/commands/generate_missing_embeddings.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        missing = UnifiedMemoryEntry.objects.filter(
            embedding__isnull=True
        )
        
        self.stdout.write(f"Found {missing.count()} missing embeddings")
        
        for entry in missing.iterator(chunk_size=100):
            try:
                embedding = generate_embedding(entry.content_text)
                entry.embedding = embedding
                entry.save()
            except Exception as e:
                self.stderr.write(f"Failed {entry.id}: {e}")

# 2. Run with rate limiting
python manage.py generate_missing_embeddings --batch-size=100 --delay=1
```

**Testing**:
- Verify embeddings generated
- Check search quality improves
- Monitor API costs

### 🟢 P2: Create HNSW Indexes
**Time**: 1 day
**Complexity**: Low
**Risk**: Low

```sql
-- Create HNSW index for fast similarity search
CREATE INDEX ukf_embedding_hnsw_idx ON unified_memory_entries 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Analyze performance
EXPLAIN ANALYZE
SELECT id, content_text, 
       embedding <=> %s as distance
FROM unified_memory_entries
ORDER BY distance
LIMIT 10;
```

**Testing**:
- Search time < 100ms
- Correct results returned
- Index size reasonable

## Phase 5: Infrastructure Hardening (Week 8)

### 🟢 P2: Implement Circuit Breakers
**Time**: 1 week
**Complexity**: Medium
**Risk**: Low

```python
# 1. Create circuit breaker decorator
from functools import wraps
import time

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.is_open:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.is_open = False
                    self.failure_count = 0
                else:
                    raise CircuitOpenError("Circuit breaker is open")
            
            try:
                result = await func(*args, **kwargs)
                self.failure_count = 0
                return result
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.is_open = True
                    logger.error(f"Circuit breaker opened for {func.__name__}")
                
                raise
        
        return wrapper

# 2. Apply to external services
@CircuitBreaker(failure_threshold=3, recovery_timeout=30)
async def call_polygon_api(ticker):
    return await polygon_service.get_quote(ticker)
```

**Testing**:
- Circuit opens after failures
- Recovers after timeout
- Fallback behavior correct

### 🟢 P2: Add Health Monitoring
**Time**: 3 days
**Complexity**: Medium
**Risk**: Low

```python
# 1. Create health check endpoint
# api/views/health.py
class SystemHealthView(APIView):
    async def get(self, request):
        checks = {
            'database': await self.check_database(),
            'redis': await self.check_redis(),
            'celery': await self.check_celery(),
            'external_apis': await self.check_apis(),
            'memory_system': await self.check_memory()
        }
        
        overall_health = all(check['healthy'] for check in checks.values())
        
        return Response({
            'healthy': overall_health,
            'checks': checks,
            'timestamp': timezone.now()
        })
    
    async def check_database(self):
        try:
            await sync_to_async(User.objects.first)()
            return {'healthy': True, 'latency': 0.01}
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
```

**Testing**:
- All health checks return correct status
- Dashboard displays real health
- Alerts trigger on failures

## Phase 6: Documentation & Testing (Week 9-10)

### 🟢 P2: Create Integration Tests
**Time**: 1 week
**Complexity**: Medium
**Risk**: Low

```python
# tests/test_integrations.py
class AgentMemoryIntegrationTest(TestCase):
    async def test_agent_retrieves_memories(self):
        # Create test memories
        memory = await UnifiedMemoryEntry.objects.create(
            content_text="Test stock analysis method",
            user=self.user
        )
        
        # Create agent
        agent = BusinessAgent(user_id=self.user.id)
        
        # Test memory retrieval
        context = await agent.get_context("stock analysis")
        
        self.assertIn(memory.content_text, context)
        
class APIIntegrationTest(TestCase):
    @mock.patch('polygon.get_quote')
    async def test_fallback_behavior(self, mock_polygon):
        mock_polygon.side_effect = Exception("API Down")
        
        tool = StockAnalysisTool()
        result = await tool.get_quote("AAPL")
        
        # Should fallback to Alpha Vantage
        self.assertIsNotNone(result)
        self.assertEqual(result['source'], 'alpha_vantage')
```

## Success Metrics

### Week 1 Success Criteria
- [ ] No auth bypass in DEBUG mode
- [ ] All mock data clearly labeled
- [ ] JWT tokens in httpOnly cookies

### Week 3 Success Criteria
- [ ] Agents retrieve memories successfully
- [ ] External APIs accessible to agents
- [ ] Stock scout deploys without errors

### Week 5 Success Criteria
- [ ] Dashboard shows real data
- [ ] Content pipeline automated
- [ ] <100ms memory search

### Week 7 Success Criteria
- [ ] All embeddings generated
- [ ] Memory systems consolidated
- [ ] Circuit breakers protecting APIs

### Week 10 Success Criteria
- [ ] 80%+ integration test coverage
- [ ] All P0 and P1 issues resolved
- [ ] Platform fully integrated

## Resource Requirements

### Team Composition
- 2 Senior Backend Engineers
- 1 Senior Frontend Engineer
- 1 DevOps Engineer
- 1 QA Engineer

### Infrastructure Needs
- Staging environment matching production
- Load testing infrastructure
- Monitoring tools (Datadog/New Relic)

### Budget Estimates
- API costs for embedding generation: ~$500
- Monitoring tools: $500/month
- Additional Redis cache: $200/month

## Risk Mitigation

### Technical Risks
1. **Data Loss**: Full backups before changes
2. **Performance Degradation**: Load test each phase
3. **Breaking Changes**: Feature flags for rollback

### Business Risks
1. **User Impact**: Communicate changes clearly
2. **Downtime**: Deploy during low-traffic windows
3. **Data Accuracy**: Audit trail for all changes

## Conclusion

This roadmap transforms the Donkey Betz platform from a collection of isolated systems into a truly integrated platform. By following this prioritized approach, the platform can achieve its original vision while maintaining stability and user trust.

**Estimated Total Time**: 10 weeks
**Estimated Cost**: $50,000 (team + infrastructure)
**Expected Outcome**: Fully integrated, production-ready platform