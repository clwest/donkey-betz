# 🧪 Unified Donkey Betz - Testing Guide

**Last Updated**: September 30, 2025
**Platform**: Unified AI Studio + DBAO
**Reality Score**: 98.5%

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [System Testing](#system-testing)
3. [Partnership System Testing](#partnership-system-testing)
4. [Agent Testing](#agent-testing)
5. [WebSocket Testing](#websocket-testing)
6. [Database Verification](#database-verification)
7. [Known Issues](#known-issues)

---

## 🚀 Quick Start

### Prerequisites
```bash
# Ensure services are running
make stop && make start

# Or manually:
redis-server
python manage.py runserver
```

### Access Points
- **Main Dashboard**: http://localhost:8000/
- **Diagnostic Dashboard**: http://localhost:8000/diagnostics/
- **Partnership Dashboard**: http://localhost:8000/partnership/dashboard/
- **WebSocket Test**: http://localhost:8000/diagnostics/websocket-test/

---

## 🔧 System Testing

### 1. Diagnostic Dashboard Test

**URL**: `http://localhost:8000/diagnostics/`

**What to Verify**:
- Reality Score displays (target: 80%+)
- All systems show status (active/error)
- No critical errors present
- Recommendations section populated if needed

**Score Breakdown**:
- Spider System: 20/20 points ✅
- Income Builder: 20/20 points ✅
- Monetization Engine: 15/15 points ✅
- WebSocket: 15/15 points ✅
- Redis: 10/10 points ✅
- Database: 10/10 points ✅
- Agent Registry: 10/10 points ✅

**Test Actions**:
1. Click "Refresh All" - Should show all systems
2. Click "Test Spiders" - Should find opportunities
3. Click "Test Income Builder" - Should process opportunities
4. Click "Test WS Message" - Should receive response

**Expected Results**:
- ✅ Reality Score > 80%
- ✅ Spider System: "active"
- ✅ Income Builder: "connected_to_spiders: true"
- ✅ WebSocket: "Connected"
- ✅ No critical errors

---

### 2. Spider System Test

**Endpoint**: `POST http://localhost:8000/api/diagnostics/test-spiders/`

**Request Body**:
```json
{
  "profile": {
    "skills": ["Python", "Django", "React"],
    "skill_level": "intermediate",
    "available_hours": 20
  }
}
```

**Expected Response**:
```json
{
  "success": true,
  "opportunities_found": 15,
  "data": {
    "opportunities": [...],
    "platforms": ["Toptal", "Guru", "Flexjobs", "RemoteOK", "PeoplePerHour"],
    "timestamp": "2025-09-30T..."
  }
}
```

**What to Verify**:
- ✅ 5 platforms active
- ✅ Opportunities found > 0
- ✅ Real opportunity data returned
- ✅ Response time < 3 seconds

---

### 3. Income Builder Test

**Endpoint**: `POST http://localhost:8000/api/diagnostics/test-income-builder/`

**Request Body**:
```json
{
  "skills": ["Python", "Django"],
  "skill_level": "intermediate",
  "available_hours": 20
}
```

**Expected Response**:
```json
{
  "success": true,
  "opportunities_found": 10,
  "data": [...]
}
```

**What to Verify**:
- ✅ Connection to spider network
- ✅ Opportunities processed correctly
- ✅ Integration with monetization
- ✅ No import path errors

---

## 🤝 Partnership System Testing

### Test 1: View Partnership Dashboard

**URL**: `/partnership/dashboard/`

**What to Check**:

#### Header
- 🤝 Title: "Partnership Dashboard"
- Subtitle: "Track your human-AI collaboration and prove the value"

#### Key Metrics (6 cards)
1. **Total Earned**: Sum of completed partnership payments
2. **Effective Rate**: Total earned ÷ Human time spent
3. **Time Saved**: Total AI contribution hours
4. **Efficiency**: Speed multiplier (AI+Human time ÷ Human time)
5. **AI Contribution**: Average AI work percentage
6. **Projects**: Completed + active counts

#### Visual Style
- Dark background with purple/green gradient
- Metric cards with hover lift effect
- Values in gradient text (purple → green)

**Expected Data**:
- At least 1 completed project (if seeded)
- ~10 opportunities listed
- Metrics showing actual calculations

---

### Test 2: Start Partnership Flow

**URL**: Click "Start Partnership" from dashboard

**Steps**:
1. Navigate to `/partnership/dashboard/`
2. Click "Start Partnership" on any opportunity
3. Verify partnership preview displays:
   - AI Contribution percentage
   - Human Contribution percentage
   - Time Savings estimate
   - Efficiency multiplier
4. Edit project name (optional)
5. Select project type from dropdown
6. Click "🚀 Start Partnership"

**Expected Result**:
- ✅ Redirects to project detail page
- ✅ Project created with status 'planning'
- ✅ No errors in console

**Common Issues**:
- URL name mismatch → Verify `partnership-project-detail` (with hyphens)
- CSRF token missing → Check `<meta name="csrf-token">` exists

---

### Test 3: Add Contributions

**URL**: `/partnership/project/{project_id}/`

#### Add AI Contribution
**Form Fields**:
- Agent Name: "ContentGeneratorAgent"
- Task: "Draft initial blog post outline"
- Time Saved: 2.5 hours
- Output Summary: "Created structured 1500-word outline with SEO keywords"

**Expected**:
- ✅ Page reloads showing new contribution
- ✅ Contribution card appears in left column
- ✅ Timestamp displayed
- ✅ ROI metrics section now visible

#### Add Human Contribution
**Form Fields**:
- Task: "Review and refine AI draft"
- Time Spent: 1.0 hours
- Value Added: "Edited for voice, added personal anecdotes, fact-checked claims"

**Expected**:
- ✅ Page reloads showing new contribution
- ✅ Contribution card appears in right column
- ✅ ROI metrics update with new calculations

---

### Test 4: View ROI Metrics

**After adding contributions, verify**:

**4 ROI Metrics Display**:
1. **Time Saved**: Total AI hours
2. **Efficiency**: (AI time + Human time) ÷ Human time
3. **Effective Rate**: Payment ÷ Human time
4. **AI Contribution**: AI hours ÷ Total hours × 100

**Calculation Examples**:
- AI time: 3.5h, Human time: 1.0h, Payment: $500
- Time Saved: 3.5h ✅
- Efficiency: 4.5x ✅
- Effective Rate: $500/hr ✅
- AI Contribution: 78% ✅

---

### Test 5: Complete Partnership

**Steps**:
1. Scroll to "Complete Project" section
2. Enter payment amount (e.g., $500.00)
3. Click "Complete Partnership"
4. Confirm in dialog

**Expected Results**:
- ✅ Success message displays
- ✅ Redirects to dashboard
- ✅ Project appears in "Completed Projects"
- ✅ Dashboard metrics updated
- ✅ Learning entry created in database

**Verify Learning Loop**:
```bash
python manage.py shell << 'EOF'
from core.models_unified_system import UserAgentLearning
learning = UserAgentLearning.objects.filter(learning_domain='partnership_success').last()
if learning:
    print('✅ Learning entry created!')
    print(f'Agent: {learning.agent_name}')
    print(f'Source: {learning.learning_source}')
    print(f'Confidence: {learning.confidence_score}')
else:
    print('❌ No learning entry found')
EOF
```

---

## 🤖 Agent Testing

### Test Real Agent Execution

**Test Script**: Create `test_real_agents.py`

```python
from ai_core.agents.agent_executor import AgentExecutor
from ai_core.models import Agent
import asyncio

async def test_agent():
    # Get content creator agent
    agent = Agent.objects.get(name='content_creator')
    executor = AgentExecutor()

    # Execute real task
    result = await executor.execute_agent(
        agent=agent,
        task={
            'task_description': 'Write a short blog intro about AI',
            'context': {}
        }
    )

    print(f"✅ Agent executed: {result['success']}")
    print(f"📊 Tokens used: {result['ai_stats']['tokens_used']}")
    print(f"📝 Output: {result['result'][:200]}...")

asyncio.run(test_agent())
```

**Expected Output**:
```
✅ Agent executed: True
📊 Tokens used: ~665
📝 Output: [Real AI-generated content]
```

---

### Test Agent Database

**Verification Query**:
```python
from ai_core.models import Agent
from legendary_advisors.models import LegendaryAdvisor

# Check agents
agent_count = Agent.objects.filter(is_active=True).count()
print(f"✅ {agent_count} Active Agents")

# Check advisors
advisor_count = LegendaryAdvisor.objects.filter(is_active=True).count()
print(f"✅ {advisor_count} Legendary Advisors")
```

**Expected**:
- ✅ 139+ Active Agents
- ✅ 25 Legendary Advisors

---

## 🌐 WebSocket Testing

### Manual WebSocket Test

**URL**: `http://localhost:8000/diagnostics/websocket-test/`

**Test Actions**:
1. Click "Connect" button
2. Verify status shows "Connected"
3. Send test message: `{"action": "test", "data": "hello"}`
4. Verify response received
5. Click "Disconnect"
6. Verify status shows "Disconnected"

**Expected Behavior**:
- ✅ Connection established < 1 second
- ✅ Messages sent/received in real-time
- ✅ No disconnections during test
- ✅ Clean disconnect when requested

---

### WebSocket Integration Test

**Test Agent Result Broadcasting**:

```javascript
// Browser console test
const ws = new WebSocket('ws://localhost:8000/ws/consciousness/');

ws.onopen = () => {
    console.log('✅ Connected');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.data && data.data.type === 'agent_result') {
        console.log('🤖 Agent Result:', data.data);
    }
};
```

**Expected**:
- ✅ Connection opens successfully
- ✅ Receives agent results when agents execute
- ✅ Data includes: agent_name, task, result, execution_time

---

## 💾 Database Verification

### PostgreSQL Health Check

```bash
python manage.py shell << 'EOF'
from django.db import connection

with connection.cursor() as cursor:
    # Check tables exist
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print(f"✅ {len(tables)} tables in database")

    # Check migrations
    cursor.execute("SELECT COUNT(*) FROM django_migrations")
    migration_count = cursor.fetchone()[0]
    print(f"✅ {migration_count} migrations applied")

    # Check key models
    cursor.execute("SELECT COUNT(*) FROM core_agent")
    agents = cursor.fetchone()[0]
    print(f"✅ {agents} agents registered")
EOF
```

**Expected Output**:
```
✅ 50+ tables in database
✅ 89+ migrations applied
✅ 139+ agents registered
```

---

### Redis Health Check

```bash
python manage.py shell << 'EOF'
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# Test connection
pong = r.ping()
print(f"✅ Redis connection: {pong}")

# Check keys
key_count = r.dbsize()
print(f"✅ Redis keys: {key_count}")

# Check memory
info = r.info('memory')
memory_used = info['used_memory_human']
print(f"✅ Memory used: {memory_used}")
EOF
```

**Expected Output**:
```
✅ Redis connection: True
✅ Redis keys: 1000+
✅ Memory used: 2-5 MB
```

---

## 🐛 Known Issues

### Issue 1: No Opportunities Display

**Symptom**: Empty state shows "No Partnership Opportunities Yet"

**Possible Causes**:
- No opportunities in database
- None have `collaboration_feasibility` >= 'high'
- User filter mismatch

**Fix**:
```python
# Create test opportunity
from core.models_unified_system import Opportunity

Opportunity.objects.create(
    user=request.user,
    title="Test Opportunity",
    description="Test partnership opportunity",
    collaboration_feasibility='ideal',
    potential_revenue=500.00
)
```

---

### Issue 2: Metrics Show $0

**Symptom**: Dashboard shows $0 total earned

**Cause**: No completed partnerships yet

**Expected Behavior**: After completing first partnership, metrics update

---

### Issue 3: WebSocket Disconnects

**Symptom**: WebSocket connection drops after 30 seconds

**Possible Causes**:
- Redis timeout too short
- No keepalive configured
- Channel capacity exceeded

**Fix**:
```python
# ai_core/settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
            "capacity": 1000,  # Increase capacity
            "expiry": 60,      # Keep messages for 60 seconds
        },
    },
}
```

---

### Issue 4: Agent Execution Fails

**Symptom**: Agent returns error or no result

**Possible Causes**:
- OpenAI API key not configured
- Rate limit exceeded
- Async/sync context mismatch

**Debug Steps**:
1. Check API key: `echo $OPENAI_API_KEY`
2. Check logs: Look for OpenAI error messages
3. Verify agent is active: `Agent.objects.get(name='agent_name').is_active`

---

## ✅ Success Criteria Checklist

After completing all tests, verify:

- [ ] Diagnostic dashboard shows Reality Score > 80%
- [ ] All spider platforms return data
- [ ] Income Builder connected to spiders
- [ ] Partnership dashboard displays correctly
- [ ] Can start new partnerships
- [ ] Can add AI and human contributions
- [ ] ROI metrics calculate correctly
- [ ] Can complete partnerships successfully
- [ ] Learning entries created in database
- [ ] WebSocket connections stable
- [ ] Agents execute with real AI
- [ ] Database queries return correct data
- [ ] Redis cache operational

---

## 📚 Related Documentation

- **Debugging Guide**: `debugging_guide.md` (see diagnostic endpoints)
- **Architecture**: `../architecture/system_design.md`
- **Partnership System**: `../architecture/partnership_model.md`
- **Learning System**: `../architecture/learning_system.md`

---

## 🔗 Quick Reference

| What You Want | Where To Look | What To Check |
|--------------|---------------|---------------|
| System health | `/diagnostics/` | Reality Score > 80% |
| Test spiders | Dashboard → Test Spiders | opportunities_found > 0 |
| Test WebSocket | `/diagnostics/websocket-test/` | Connection status |
| Check partnerships | `/partnership/dashboard/` | Metrics populated |
| Verify database | Django shell | Model counts correct |
| Check Redis | Redis CLI | `PING` → `PONG` |

---

**Testing Guide Complete**
**Version**: 1.0
**Last Updated**: September 30, 2025
**Maintainer**: Unified Donkey Betz Team
