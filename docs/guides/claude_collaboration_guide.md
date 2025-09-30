# 🤝 Claude Collaboration Guide
## Working Effectively with the Unified Donkey Betz Platform

**Last Updated**: September 30, 2025
**For**: Future Claude Code sessions
**Platform**: Unified AI Studio + DBAO (98.5% Reality Score)

---

## 📋 Table of Contents

1. [Core Mission](#core-mission)
2. [System Overview](#system-overview)
3. [Key Files & Don't-Break Lists](#key-files--dont-break-lists)
4. [Common Tasks](#common-tasks)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Reality Score Guidelines](#reality-score-guidelines)

---

## 🎯 Core Mission

### The Platform's Purpose
**Find immediate money-making opportunities where USER + AI work together**

#### What We're Building
- Content creation partnerships (blog posts, articles, copy)
- Freelance gig execution (data analysis, web scraping)
- Micro-task automation at scale
- Quick consulting/advisory services

#### What We're NOT Building
- ❌ Traditional job board
- ❌ Long-term employment matching
- ❌ "Apply and wait" workflows
- ❌ Career development tools

#### The User Experience
1. Spider finds opportunity: "Need 10 blog posts, $200 each"
2. AI analyzes: "Can we do this? Yes - Content Studio ready"
3. User reviews: "$2,000 for 10 posts? I'm in!"
4. USER + AI execute together:
   - AI generates drafts
   - User reviews, edits, adds personal touch
   - AI handles SEO, formatting
   - User submits & gets paid
5. Revenue tracked: $2,000 earned

---

## 🏗️ System Overview

### Current Reality Score: 98.5%

**What's Real and Working**:
- ✅ 139 AI agents (real OpenAI GPT-4 API)
- ✅ 25 legendary advisors (database-backed profiles)
- ✅ WebSocket broadcasting (real-time frontend updates)
- ✅ Partnership system (complete with ROI tracking)
- ✅ Learning loop (cross-domain pattern analysis)
- ✅ Spider network (5 platforms active)
- ✅ PostgreSQL database (89+ migrations)
- ✅ Redis cache (1,000+ keys active)

**What's Mock/Limited**:
- ⚠️ Some spider data (demo fallback when API limits reached)
- ⚠️ Payment processing (Stripe in test mode)
- ⚠️ Some ML models (demo predictions for sports betting)

---

## 📁 Key Files & Don't-Break Lists

### 🔴 CRITICAL - DO NOT BREAK

#### Partnership System (100% Reality)
```
core/models_partnership.py          # Partnership models (565 lines)
core/views_partnership.py           # Partnership views (413 lines)
core/templates/unified/
  ├── partnership_dashboard.html    # Main dashboard (480 lines)
  ├── start_partnership.html        # Project setup (320 lines)
  └── partnership_project_detail.html # Tracking (480 lines)
core/urls.py (lines 897-908)        # Partnership routes
```

**Status**: Fully tested, production-ready, 100% reality
**Learning Loop Integration**: YES (creates UserAgentLearning entries on completion)

#### Learning System (100% Reality)
```
core/models_unified_system.py      # UserAgentLearning, UnifiedBaseModel
core/unified_learning_pipeline.py  # Learning engine (1,247 lines)
core/learning_bridges/              # 5 learning bridges
  ├── advisor_feedback_bridge.py
  ├── opportunity_interaction_bridge.py
  ├── agent_execution_bridge.py
  ├── content_feedback_bridge.py
  └── prediction_learning_bridge.py
```

**Status**: Operational, 7,700 learning entries collected
**Integration Points**: Sports betting, partnerships, agent execution, opportunities

#### Spider System (75% Reality)
```
intelligence/income_spider_orchestrator.py  # Main orchestrator
intelligence/spider_decision_bridge.py      # Spider → Decision Command
intelligence/spider_opportunity_connector.py # Spider → Opportunities
intelligence/tasks.py (lines 1601-1673)     # Celery pipeline (FIXED)
```

**Status**: 5 platforms active, saving to database
**Fallback**: Uses mock data when API limits reached
**Celery**: Configured for hourly opportunity fetching

#### Agent System (100% Reality)
```
ai_core/agents/concrete_executor.py    # Agent execution + WebSocket broadcast
ai_core/agents/agent_executor.py       # Agent execution wrapper
ai_core/models.py                      # Agent model
core/unified_agent_performance.py      # Performance tracking
```

**Status**: 139 agents active, real GPT-4 execution
**WebSocket**: Broadcasts results to frontend in real-time
**Performance**: ~665 tokens per execution, < 2s response time

### 🟡 MODIFY WITH CAUTION

#### Views & APIs
```
core/views_analytics.py       # Analytics endpoints
core/views_opportunities.py   # Opportunity CRUD
core/views_revenue.py         # Revenue tracking
core/views_partnership.py     # Partnership CRUD (lines 1-413)
```

**Pattern**: All views follow Django REST patterns
**Auth**: All require authentication
**Returns**: JSON responses for API, template renders for pages

#### WebSocket Consumers
```
backend/consumers.py          # WebSocket routing
consciousness_consumer.py     # Consciousness stream
decision_command_consumer.py  # Decision Command WS
```

**Pattern**: Async consumers, Redis channel layer
**Broadcasting**: Group send for multiple clients
**Error Handling**: Try/except with logging

### 🟢 SAFE TO MODIFY

#### Templates
```
core/templates/unified/*.html  # Frontend templates
```

**Stack**: HTML + Tailwind CSS + Alpine.js
**Pattern**: Dark theme, purple/green gradients
**WebSocket**: All use consciousness stream connection

#### Static Files
```
static/css/
static/js/
```

**Pattern**: Modern ES6+ JavaScript
**Bundler**: None (direct imports)

---

## 🛠️ Common Tasks

### Task 1: Add New Agent

**Steps**:
1. Create agent class in `ai_core/agents/`
2. Register in database:
```python
from ai_core.models import Agent

Agent.objects.create(
    name='new_agent_name',
    agent_type='content_creator',  # or appropriate type
    description='What this agent does',
    is_active=True,
    capabilities={'skill1': 'expert', 'skill2': 'intermediate'}
)
```
3. Add to agent executor routing if needed
4. Test with diagnostic endpoint

**Don't**:
- Don't modify existing agent classes
- Don't change agent execution flow in `concrete_executor.py`
- Don't break WebSocket broadcasting

---

### Task 2: Add Learning Bridge

**Steps**:
1. Create bridge file in `core/learning_bridges/`
2. Follow pattern from existing bridges:
```python
from core.unified_learning_pipeline import UnifiedLearningPipeline

def process_new_data_type_learning(user, data):
    """Process learning from new data source"""
    pipeline = UnifiedLearningPipeline()

    # Create learning entry
    learning_entry = UserAgentLearning.objects.create(
        user=user,
        agent_name='RelevantAgent',
        learning_domain='new_domain',
        learning_source='new_source',
        learning_content={
            'context': {...},
            'outcomes': {...},
            'insights': {...}
        },
        confidence_score=0.75,
        validation_count=1
    )

    # Process through pipeline
    analysis = pipeline.analyze_user_patterns(user)

    return learning_entry
```
3. Wire up in appropriate views/consumers
4. Test learning entry creation
5. Verify pipeline processes new entries

**Don't**:
- Don't modify `UnifiedLearningPipeline` core logic
- Don't change existing bridge patterns
- Don't break cross-domain learning

---

### Task 3: Fix WebSocket Issues

**Diagnosis**:
```bash
# Check diagnostic dashboard
curl http://localhost:8000/api/diagnostics/ | jq '.websocket_consumers'

# Test WebSocket connection
# Visit: http://localhost:8000/diagnostics/websocket-test/
```

**Common Fixes**:

**1. Redis Timeout**:
```bash
redis-cli CONFIG SET timeout 0
redis-cli CONFIG SET tcp-keepalive 60
```

**2. Channel Capacity**:
```python
# ai_core/settings.py
CHANNEL_LAYERS = {
    'default': {
        'CONFIG': {
            'capacity': 1000,  # Increase if needed
            'expiry': 60,
        }
    }
}
```

**3. Stale Connections**:
```bash
redis-cli --scan --pattern "websocket:*:stale" | xargs redis-cli DEL
```

**Don't**:
- Don't modify consumer routing in `backend/routing.py`
- Don't change group naming patterns
- Don't break message format contracts

---

### Task 4: Add New Spider

**Steps**:
1. Create spider class in `intelligence/spiders/`
2. Follow pattern from existing spiders:
```python
class NewPlatformSpider:
    def __init__(self):
        self.platform_name = "NewPlatform"

    async def search_opportunities(self, profile):
        """Search for opportunities matching user profile"""
        # Implement search logic
        opportunities = []

        for result in search_results:
            opportunities.append({
                'title': result.title,
                'description': result.description,
                'compensation': result.pay,
                'url': result.link,
                'platform': self.platform_name,
                'posted_date': result.date,
                'requirements': result.requirements
            })

        return opportunities
```
3. Register in `income_spider_orchestrator.py`
4. Add to Celery task pipeline
5. Test with diagnostic endpoint

**Don't**:
- Don't break existing spider interfaces
- Don't modify spider opportunity connector
- Don't change database save logic in `tasks.py`

---

### Task 5: Update Frontend UI

**Pattern**:
```html
<!-- Dark card with gradient border -->
<div class="bg-black bg-opacity-30 border border-purple-500 border-opacity-20 rounded-lg p-6 hover:translate-y-[-3px] transition-all">
    <h3 class="text-2xl font-bold bg-gradient-to-r from-purple-400 to-green-400 bg-clip-text text-transparent">
        Title
    </h3>
    <p class="text-gray-300">Content</p>
</div>
```

**WebSocket Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/consciousness/');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.data && data.data.type === 'agent_result') {
        displayAgentResult(data.data);
    }
};
```

**Don't**:
- Don't change color scheme (purple/green gradient)
- Don't break WebSocket message handling
- Don't modify CSRF token setup

---

## ✨ Best Practices

### 1. Always Check Reality Score First
```bash
curl http://localhost:8000/api/diagnostics/ | jq '.summary.reality_score'
```
- Target: 80%+
- If < 80%, investigate errors before adding features

### 2. Test with Diagnostic Endpoints
- Use `/diagnostics/` dashboard for visual testing
- Use `/api/diagnostics/` for programmatic testing
- Test each component individually before integration

### 3. Follow Async/Sync Patterns
```python
# In async context (consumers, agent executors)
result = await async_function()

# In sync context (views, management commands)
import asyncio
result = asyncio.run(async_function())
```

### 4. Use Existing Patterns
- Don't reinvent database models (extend UnifiedBaseModel)
- Don't create new WebSocket routing (use existing consumers)
- Don't create new learning patterns (use existing bridges)

### 5. Document as You Go
- Update relevant docs in `/docs/`
- Add docstrings to new functions
- Update this guide if you discover new patterns

---

## 🐛 Troubleshooting

### Issue: "NoReverseMatch for 'url_name'"
**Cause**: URL name mismatch (hyphens vs underscores)
**Fix**: Check `core/urls.py` for exact name, use that in `redirect()`/`reverse()`

### Issue: "UserAgentLearning() got unexpected keyword arguments"
**Cause**: Using non-existent model fields
**Fix**:
```python
# Check actual model fields
from core.models_unified_system import UserAgentLearning
fields = [f.name for f in UserAgentLearning._meta.get_fields()]
print(fields)

# Use correct fields:
# - learning_content (JSONField - stores all structured data)
# - learning_source (str)
# - learning_domain (str)
# - confidence_score (float)
# - validation_count (int)
```

### Issue: "Spider system status: error"
**Cause**: Import error or API credentials missing
**Fix**: Check imports in `intelligence/tasks.py`, verify API keys

### Issue: WebSocket disconnects after 30s
**Cause**: Redis timeout or no keepalive
**Fix**: See "Task 3: Fix WebSocket Issues" above

### Issue: Agent execution returns empty result
**Cause**: OpenAI API key not configured or rate limit
**Fix**:
```bash
echo $OPENAI_API_KEY  # Should show key
# If empty: export OPENAI_API_KEY="sk-..."
```

---

## 📊 Reality Score Guidelines

### Reality Score Breakdown
- **0-20%**: Mostly mock data, basic structure only
- **20-40%**: Some real connections, many mocks
- **40-60%**: Mixed real and mock systems
- **60-80%**: Mostly real, some integration issues
- **80-100%**: Fully operational with real data

### Component Scores
- Spider System: 20 points (5 platforms active)
- Income Builder: 20 points (connected to spiders)
- Monetization Engine: 15 points (can record earnings)
- WebSocket: 15 points (real-time broadcasting)
- Redis: 10 points (1,000+ keys active)
- Database: 10 points (89+ migrations applied)
- Agent Registry: 10 points (139 agents active)

### Maintaining 95%+ Reality
1. **Keep All Systems Active**: No component should be "error" status
2. **Real Data Flows**: Spiders → Income Builder → Frontend (no breaks)
3. **Learning Loop Active**: UserAgentLearning entries created on user actions
4. **WebSocket Broadcasting**: Agent results reach frontend in < 200ms
5. **No Mock Fallbacks**: All spiders return real data (or graceful failure)

---

## 🎯 Success Criteria Checklist

Before considering a session complete:

- [ ] Reality Score >= 95%
- [ ] All diagnostic tests pass
- [ ] No error status in any component
- [ ] WebSocket connections stable (no disconnects)
- [ ] Agents execute with real AI (not mock responses)
- [ ] Spiders return real opportunities (from actual platforms)
- [ ] Learning loop creates entries on user actions
- [ ] Partnership system tracks real metrics
- [ ] Database queries return correct data
- [ ] Redis cache operational with good hit rate

---

## 📚 Related Documentation

- **Testing Guide**: `testing_guide.md` - How to test everything
- **Debugging Guide**: `debugging_guide.md` - Fix common issues
- **System Architecture**: `../architecture/system_design.md`
- **Learning System**: `../architecture/learning_system.md`
- **Partnership Model**: `../architecture/partnership_model.md`

---

## 💡 Final Thoughts

### The Platform Philosophy
This is a **human-AI partnership platform**, not a traditional job board. Every feature should enable USER + AI collaboration for immediate money-making.

### Code Quality > Speed
Take time to:
- Follow existing patterns
- Test thoroughly before claiming completion
- Update documentation
- Maintain reality score

### When in Doubt
1. Check diagnostic dashboard first
2. Read existing code for patterns
3. Test incrementally
4. Ask before breaking critical files

---

**Guide Version**: 2.0
**Consolidated From**: 18 session handoff letters (Sessions 4-40)
**Last Updated**: September 30, 2025
**Maintainer**: Unified Donkey Betz Team

**Good luck, future Claude! You've got this! 🚀**
