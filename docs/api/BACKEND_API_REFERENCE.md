# 🔌 Backend API Reference for UI Fresh Start

**Purpose**: Comprehensive reference of existing and needed backend APIs
**Status**: 📋 Reference Guide
**Last Updated**: October 2, 2025

---

## 📋 Overview

The backend has **many existing APIs**, but they're scattered across multiple files. This document catalogs what exists, what's useful for the new UI, and what needs to be created.

---

## 🗂️ API Categories

### 1. **Agent APIs** ✅ (Exists)
### 2. **Advisor APIs** ⚠️ (Partial - needs enhancement)
### 3. **Spider APIs** ✅ (Exists)
### 4. **Opportunity APIs** ✅ (Exists)
### 5. **Learning APIs** ✅ (Exists)
### 6. **Revenue APIs** ✅ (Exists)
### 7. **Authentication APIs** ✅ (Exists)
### 8. **WebSocket Consumers** ⚠️ (Many exist, need consolidation)

---

## 🤖 Agent APIs

### Existing APIs:

#### **Execute Agent**
```python
# File: core/views.py
@login_required
def execute_agent(request):
    """Execute an agent with given parameters"""
    # POST: {agent_name, task_description, context}
    # Returns: {execution_id, status, result}
```

**URL**: `/api/agent/execute/`
**Method**: POST
**Auth**: Required
**Status**: ✅ Works

#### **List Agent Executions**
```python
# File: core/views.py
@login_required
def agent_executions_list(request):
    """List all agent executions for user"""
    # GET: Returns list of executions
```

**URL**: `/api/agent/executions/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works

#### **List All Agents**
```python
# File: core/views_agent_dashboard.py
@login_required
def all_agents_list(request):
    """List all available agents"""
    # GET: Returns list of agents with metadata
```

**URL**: `/api/agents/list/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works

#### **Get Agent Details**
**Status**: ❌ NEEDS CREATION

```python
# To be created in: core/views_unified_v2.py
@login_required
def api_agent_detail(request, agent_id):
    """Get detailed information about a specific agent"""
    try:
        agent = Agent.objects.get(id=agent_id)

        # Get agent execution history
        executions = AgentExecution.objects.filter(
            agent_name=agent.name,
            user=request.user
        ).order_by('-created_at')[:10]

        # Get agent learning stats
        learning_stats = UserAgentLearning.objects.filter(
            agent_name=agent.name,
            user=request.user
        ).aggregate(
            avg_confidence=Avg('confidence_score'),
            total_records=Count('id')
        )

        return JsonResponse({
            'agent': {
                'id': str(agent.id),
                'name': agent.name,
                'description': agent.description,
                'category': agent.category.name if agent.category else None,
            },
            'executions': [{
                'id': str(e.id),
                'status': e.status,
                'created_at': e.created_at.isoformat(),
            } for e in executions],
            'learning': learning_stats,
        })
    except Agent.DoesNotExist:
        return JsonResponse({'error': 'Agent not found'}, status=404)
```

**URL**: `/api/agents/<agent_id>/` ← TO CREATE
**Method**: GET
**Auth**: Required

---

## 👔 Advisor APIs

### Existing APIs:

#### **Advisor Insights**
```python
# File: core/views_dashboard_stats.py
@login_required
def advisor_insights(request):
    """Get insights from advisors"""
    # GET: Returns advisor insights
```

**URL**: `/api/advisor/insights/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works (but minimal data)

### APIs to Create:

#### **List All Advisors**
**Status**: ❌ NEEDS CREATION

```python
# To be created in: core/views_unified_v2.py
@login_required
def api_advisors_list(request):
    """List all 25 legendary advisors"""
    try:
        advisors = Advisor.objects.all()

        advisor_list = [{
            'id': str(advisor.id),
            'name': advisor.name,
            'domain': advisor.domain,
            'expertise': advisor.expertise,
            'track_record': advisor.track_record,
            'avatar_url': advisor.avatar_url,
        } for advisor in advisors]

        return JsonResponse({
            'advisors': advisor_list,
            'total': len(advisor_list)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

**URL**: `/api/advisors/list/` ← TO CREATE
**Method**: GET
**Auth**: Required

#### **Consult Advisor**
**Status**: ❌ NEEDS CREATION

```python
# To be created in: core/views_unified_v2.py
@login_required
def api_consult_advisor(request):
    """Request consultation from an advisor"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        advisor_id = data.get('advisor_id')
        question = data.get('question')

        advisor = Advisor.objects.get(id=advisor_id)

        # Generate advisor response using AI
        from ai_core.advisors.advisor_engine import AdvisorEngine
        engine = AdvisorEngine()
        response = engine.consult(advisor, question, user=request.user)

        # Log consultation
        AdvisorInsight.objects.create(
            advisor=advisor,
            user=request.user,
            insight_type='consultation',
            content=response,
            context={'question': question}
        )

        return JsonResponse({
            'advisor': advisor.name,
            'response': response,
            'timestamp': timezone.now().isoformat()
        })
    except Advisor.DoesNotExist:
        return JsonResponse({'error': 'Advisor not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

**URL**: `/api/advisors/consult/` ← TO CREATE
**Method**: POST
**Auth**: Required

---

## 🕷️ Spider APIs

### Existing APIs:

#### **Execute Spider**
```python
# File: core/views_spider_dashboard.py
@login_required
def execute_spider(request):
    """Execute a spider to collect data"""
    # POST: {spider_name, targets}
```

**URL**: `/api/spider/execute/`
**Method**: POST
**Auth**: Required
**Status**: ✅ Works

#### **Spider Network Data**
```python
# File: core/views_spider_dashboard.py
@login_required
def spider_network_data(request):
    """Get spider network status"""
    # GET: Returns spider network stats
```

**URL**: `/api/spider/network/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works

#### **Spider Activity Feed**
```python
# File: core/views_spider_dashboard.py
@login_required
def spider_activity_feed(request):
    """Get recent spider activity"""
    # GET: Returns activity feed
```

**URL**: `/api/spider/activity/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works

#### **Get Spider Items**
```python
# File: core/views_spider_data.py
@login_required
def get_spider_items(request):
    """Get items collected by spiders"""
    # GET: ?spider_type=financial&limit=10
```

**URL**: `/api/spider/items/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works

---

## 💰 Opportunity APIs

### Existing APIs:

#### **Get Opportunities (Aggregated)**
```python
# File: ai_core/api/opportunity_aggregator.py
@login_required
def get_opportunities(request):
    """Get aggregated opportunities from all sources"""
    # GET: Returns opportunities
```

**URL**: `/api/opportunities/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works

#### **Get Actionable Opportunities**
```python
# File: ai_core/api/opportunity_aggregator.py
@login_required
def get_actionable(request):
    """Get actionable opportunities ready for user"""
    # GET: Returns filtered opportunities
```

**URL**: `/api/opportunities/actionable/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works

#### **Income Builder Analysis**
```python
# File: core/intelligence_api.py
@login_required
def income_builder_analysis(request):
    """Analyze opportunities and create action plan"""
    # POST: {user_profile, goals}
```

**URL**: `/api/income/analyze/`
**Method**: POST
**Auth**: Required
**Status**: ✅ Works

---

## 🧠 Learning APIs

### Existing APIs:

#### **Agent Learning Data**
```python
# File: core/views_agent_dashboard.py
@login_required
def agent_learning_data(request):
    """Get agent learning statistics"""
    # GET: Returns learning data
```

**URL**: `/api/learning/agents/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works

#### **Get Learning Status**
```python
# File: core/views_learning_path.py
@login_required
def get_overall_learning_status(request):
    """Get overall learning status for user"""
    # GET: Returns learning summary
```

**URL**: `/api/learning/status/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works

### APIs to Create:

#### **User Learning Stats**
**Status**: ❌ NEEDS CREATION

```python
# To be created in: core/views_unified_v2.py
@login_required
def api_learning_stats(request):
    """Get comprehensive learning stats for user"""
    try:
        user = request.user

        # Get learning records
        learning_records = UserAgentLearning.objects.filter(user=user)

        # Calculate stats
        stats = {
            'total_records': learning_records.count(),
            'avg_confidence': learning_records.aggregate(
                Avg('confidence_score')
            )['confidence_score__avg'] or 0,
            'domains': learning_records.values('learning_domain').annotate(
                count=Count('id'),
                avg_conf=Avg('confidence_score')
            ).order_by('-avg_conf'),
            'top_agents': learning_records.values('agent_name').annotate(
                avg_conf=Avg('confidence_score')
            ).order_by('-avg_conf')[:10],
            'recent': learning_records.order_by('-created_at')[:20].values(
                'agent_name', 'learning_domain', 'confidence_score', 'created_at'
            )
        }

        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

**URL**: `/api/learning/stats/` ← TO CREATE
**Method**: GET
**Auth**: Required

---

## 💵 Revenue APIs

### Existing APIs:

#### **Track Revenue**
```python
# File: core/intelligence_api.py
@login_required
def track_revenue(request):
    """Track revenue from opportunities"""
    # POST: {source, amount, opportunity_id}
```

**URL**: `/api/revenue/track/`
**Method**: POST
**Auth**: Required
**Status**: ✅ Works

#### **Monetization Opportunities**
```python
# File: core/intelligence_api.py
@login_required
def monetization_opportunities(request):
    """Get monetization opportunities"""
    # GET: Returns monetization options
```

**URL**: `/api/monetization/opportunities/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works

---

## 🔐 Authentication APIs

### Existing APIs:

#### **Login**
```python
# File: core/auth_views.py or core/auth_views_enhanced.py
def login_view(request):
    """User login"""
    # POST: {username, password}
```

**URL**: `/login/` or `/auth/login/`
**Method**: POST
**Status**: ✅ Works

#### **Logout**
```python
# File: core/auth_views.py
@login_required
def logout_view(request):
    """User logout"""
    # POST or GET
```

**URL**: `/logout/`
**Method**: POST/GET
**Auth**: Required
**Status**: ✅ Works

#### **Current User**
```python
# File: core/auth_views.py
@login_required
def current_user(request):
    """Get current user info"""
    # GET: Returns user data
```

**URL**: `/api/user/current/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works

#### **User Profile**
```python
# File: core/auth_views.py
@login_required
def user_profile(request):
    """Get user profile"""
    # GET: Returns profile data
```

**URL**: `/api/user/profile/`
**Method**: GET
**Auth**: Required
**Status**: ✅ Works

---

## 🔌 WebSocket Consumers

### Existing Consumers:

#### **PersonalAssistantConsumer**
**File**: `core/personal_assistant_consumer.py`
**Route**: `/ws/personal-assistant/`
**Status**: ✅ Exists (needs auth enhancement)
**Purpose**: Personal assistant chat

#### **DecisionCommandConsumer**
**File**: `core/decision_command_consumer.py`
**Route**: `/ws/decision-command/`
**Status**: ✅ Exists
**Purpose**: Decision command real-time updates

#### **RevenueDashboardConsumer**
**File**: `core/revenue_dashboard_consumer.py`
**Route**: `/ws/revenue-dashboard/`
**Status**: ✅ Exists
**Purpose**: Revenue tracking updates

#### **RevenueOpportunitiesConsumer**
**File**: `core/revenue_opportunities_consumer.py`
**Route**: `/ws/revenue-opportunities/`
**Status**: ✅ Exists
**Purpose**: Opportunity feed updates

#### **LearningDashboardConsumer**
**File**: `core/learning_dashboard_consumer.py`
**Route**: `/ws/learning-dashboard/`
**Status**: ✅ Exists
**Purpose**: Learning progress updates

#### **ControlCenterConsumer**
**File**: `core/control_center_consumer.py`
**Route**: `/ws/control-center/`
**Status**: ✅ Exists
**Purpose**: System control updates

#### **SportsConsumer**
**File**: `core/sports_consumer.py`
**Route**: `/ws/sports/`
**Status**: ✅ Exists
**Purpose**: Sports betting updates

### Consumers to Create:

#### **DashboardConsumer**
**Status**: ❌ NEEDS CREATION

```python
# To be created in: core/consumers_unified.py
class DashboardConsumer(AuthenticatedConsumer):
    """WebSocket consumer for main dashboard real-time updates"""

    async def send_initial_data(self):
        """Send initial dashboard data"""
        stats = await self.get_dashboard_stats()

        await self.send(text_data=json.dumps({
            'type': 'dashboard_stats',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        return {
            'agents_total': Agent.objects.count(),
            'advisors_total': Advisor.objects.count(),
            'executions_total': AgentExecution.objects.filter(user=self.user).count(),
            'executions_today': AgentExecution.objects.filter(
                user=self.user,
                created_at__date=timezone.now().date()
            ).count(),
            'opportunities_total': OpportunityTracking.objects.count(),
            'spider_data_items': SpiderData.objects.count(),
            'learning_records': UserAgentLearning.objects.filter(user=self.user).count(),
        }

    async def handle_refresh(self, data):
        """Handle refresh request"""
        await self.send_initial_data()

    # Method to send updates from other parts of system
    async def dashboard_update(self, event):
        """Send dashboard update"""
        await self.send(text_data=json.dumps(event))
```

**Route**: `/ws/dashboard/` ← TO CREATE

#### **AgentMarketplaceConsumer**
**Status**: ❌ NEEDS CREATION

```python
# To be created in: core/consumers_unified.py
class AgentMarketplaceConsumer(AuthenticatedConsumer):
    """WebSocket consumer for agent marketplace real-time updates"""

    async def send_initial_data(self):
        """Send initial agent list"""
        agents = await self.get_agents()

        await self.send(text_data=json.dumps({
            'type': 'agent_list',
            'agents': agents,
            'total': len(agents),
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_agents(self):
        """Get list of agents"""
        agents = Agent.objects.all()

        return [{
            'id': str(agent.id),
            'name': agent.name,
            'description': agent.description,
            'category': agent.category.name if agent.category else 'Uncategorized',
        } for agent in agents]

    async def handle_execute_agent(self, data):
        """Handle agent execution request"""
        agent_name = data.get('agent_name')

        # Execute agent asynchronously
        result = await self.execute_agent(agent_name)

        await self.send(text_data=json.dumps({
            'type': 'execution_result',
            'agent_name': agent_name,
            'result': result,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def execute_agent(self, agent_name):
        """Execute agent"""
        from ai_core.agents.universal_agent_loader import UniversalAgentLoader

        loader = UniversalAgentLoader()
        result = loader.execute_agent(agent_name, user=self.user)

        return result
```

**Route**: `/ws/agents/` ← TO CREATE

#### **AdvisorCouncilConsumer**
**Status**: ❌ NEEDS CREATION

```python
# To be created in: core/consumers_unified.py
class AdvisorCouncilConsumer(AuthenticatedConsumer):
    """WebSocket consumer for advisor council real-time updates"""

    async def send_initial_data(self):
        """Send initial advisor list"""
        advisors = await self.get_advisors()

        await self.send(text_data=json.dumps({
            'type': 'advisor_list',
            'advisors': advisors,
            'total': len(advisors),
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_advisors(self):
        """Get list of advisors"""
        advisors = Advisor.objects.all()

        return [{
            'id': str(advisor.id),
            'name': advisor.name,
            'domain': advisor.domain,
            'expertise': advisor.expertise,
        } for advisor in advisors]

    async def handle_consult(self, data):
        """Handle consultation request"""
        advisor_id = data.get('advisor_id')
        question = data.get('question')

        # Process consultation
        response = await self.consult_advisor(advisor_id, question)

        await self.send(text_data=json.dumps({
            'type': 'consultation_response',
            'advisor_id': advisor_id,
            'response': response,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def consult_advisor(self, advisor_id, question):
        """Consult advisor"""
        from ai_core.advisors.advisor_engine import AdvisorEngine

        advisor = Advisor.objects.get(id=advisor_id)
        engine = AdvisorEngine()
        response = engine.consult(advisor, question, user=self.user)

        return response
```

**Route**: `/ws/advisors/` ← TO CREATE

#### **IntelligenceHubConsumer**
**Status**: ❌ NEEDS CREATION

```python
# To be created in: core/consumers_unified.py
class IntelligenceHubConsumer(AuthenticatedConsumer):
    """WebSocket consumer for intelligence hub real-time updates"""

    async def send_initial_data(self):
        """Send initial intelligence data"""
        data = await self.get_intelligence_data()

        await self.send(text_data=json.dumps({
            'type': 'intelligence_data',
            'data': data,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_intelligence_data(self):
        """Get intelligence hub data"""
        return {
            'spiders_total': 45,  # From spider registry
            'spider_data_items': SpiderData.objects.count(),
            'opportunities': OpportunityTracking.objects.count(),
            'recent_data': list(SpiderData.objects.order_by('-created_at')[:20].values(
                'spider_type', 'data_type', 'created_at'
            ))
        }

    async def handle_deploy_spider(self, data):
        """Handle spider deployment request"""
        spider_name = data.get('spider_name')

        # Deploy spider
        result = await self.deploy_spider(spider_name)

        await self.send(text_data=json.dumps({
            'type': 'spider_deployed',
            'spider_name': spider_name,
            'result': result,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def deploy_spider(self, spider_name):
        """Deploy spider"""
        from ai_core.spiders.spider_army_orchestrator import SpiderArmyOrchestrator

        orchestrator = SpiderArmyOrchestrator()
        result = orchestrator.deploy_spider(spider_name)

        return result
```

**Route**: `/ws/intelligence/` ← TO CREATE

---

## 📋 API Summary

### ✅ What Exists and Works:
- Agent execution API
- Agent execution list API
- Agent list API
- Spider execution API
- Spider network data API
- Opportunity APIs (multiple)
- Learning APIs (basic)
- Revenue tracking API
- Authentication APIs
- Multiple WebSocket consumers (need consolidation)

### ❌ What Needs to be Created:
- Agent detail API (`/api/agents/<id>/`)
- Advisors list API (`/api/advisors/list/`)
- Advisor consult API (`/api/advisors/consult/`)
- Learning stats API (`/api/learning/stats/`)
- Dashboard WebSocket consumer
- Agent Marketplace WebSocket consumer
- Advisor Council WebSocket consumer
- Intelligence Hub WebSocket consumer

### ⚠️ What Needs Enhancement:
- PersonalAssistantConsumer (add authentication)
- Existing consumers (consolidate & add auth)
- User profile APIs (add more detail)

---

## 🚀 Implementation Plan

### Phase 1: Core APIs (Day 1)
1. Create `views_unified_v2.py` with:
   - `api_agent_detail()`
   - `api_advisors_list()`
   - `api_learning_stats()`

2. Create `consumers_unified.py` with:
   - `DashboardConsumer`
   - Base authenticated consumer class

### Phase 2: Agent & Advisor APIs (Day 2)
1. Create advisor consult API
2. Create AgentMarketplaceConsumer
3. Create AdvisorCouncilConsumer

### Phase 3: Intelligence APIs (Day 3)
1. Create IntelligenceHubConsumer
2. Enhance spider APIs if needed
3. Add opportunity filtering APIs

### Phase 4: Testing & Integration (Day 4-5)
1. Test all APIs with authentication
2. Test all WebSocket consumers
3. Integrate with frontend
4. Load testing

---

## 🧪 API Testing Commands

### Test Agent List:
```bash
curl -X GET http://localhost:8000/api/agents/list/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

### Test Agent Execution:
```bash
curl -X POST http://localhost:8000/api/agent/execute/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "market-analyst", "task": "Analyze markets"}'
```

### Test WebSocket Connection:
```javascript
// In browser console (logged in)
const ws = new WebSocket('ws://localhost:8000/ws/dashboard/');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
ws.onerror = (e) => console.error('Error:', e);
```

---

## 📚 Related Documentation

- Authentication Guide: `docs/guides/AUTHENTICATION_INTEGRATION_GUIDE.md`
- UI Fresh Start Plan: `docs/00-START-SESSION-22-UI-FRESH-START.md`

---

**Status**: 📋 REFERENCE COMPLETE

**Key Takeaway**: Most APIs exist but need consolidation and enhancement. Focus on creating clean, authenticated wrappers in `views_unified_v2.py` and `consumers_unified.py`.
