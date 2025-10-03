# 🎭 Agent Orchestra System

## 📋 Overview
The Agent Orchestra is an AI-powered business creation and analysis platform that coordinates multiple specialized agents to generate comprehensive business plans, technical architectures, and market strategies.

## 🚀 Recent Updates (July 1, 2025)

### ✨ New Features
- **Orchestration Rerun**: Users can now rerun canceled, failed, or completed orchestrations
- **GPT-4.1-nano Migration**: 33% cost reduction with improved performance
- **Enhanced Management**: Improved deletion and error handling

### 🔧 Bug Fixes
- Fixed orchestration deletion restrictions
- Improved cascade delete handling
- Better error messages and validation

## 🎯 Key Features

### 🤖 21 Specialized AI Agents
1. **Core Business Agents**
   - Business Strategy Agent
   - Technical Architecture Agent
   - Marketing Strategy Agent
   - Financial Planning Agent

2. **Industry Specialists**
   - SaaS Business Agent
   - E-commerce Specialist
   - Professional Services Agent
   - Startup Accelerator Agent

3. **Research & Intelligence**
   - Reddit Scout Agent (trend analysis)
   - Market Intelligence Agent
   - Competitive Analysis Agent
   - Industry Research Agent

4. **Technical & Creative**
   - Universal Builder Agent (complete codebases)
   - Content Creation Agent
   - Brand Strategy Agent
   - Legal Analysis Agent

5. **Financial Intelligence**
   - Venture Capital Agent
   - Financial Modeling Agent
   - Investment Analysis Agent
   - Revenue Optimization Agent

6. **Advanced Analytics**
   - Performance Analytics Agent
   - Self-Development Agent (codebase analysis)

### 🔄 Orchestration Lifecycle
1. **Planning** - Task analysis and agent assignment
2. **Deploying** - Agent initialization and setup
3. **Executing** - Parallel agent execution with real AI
4. **Aggregating** - Result compilation and synthesis
5. **Completed** - Final deliverables and reporting

## 🛠️ Core Components

### Models (`models.py`)
- **TaskOrchestration**: Main orchestration management
- **AgentInstance**: Individual agent execution tracking
- **AgentTemplate**: Agent type definitions and capabilities
- **AgentResult**: Output and deliverable storage
- **AgentCommunication**: Inter-agent messaging

### Orchestrator (`orchestrator.py`)
```python
from agent_orchestra.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator(user)
result = await orchestrator.execute_complex_task(
    "Create business plan for AI fitness app"
)
```

### Task Management (`tasks.py`)
- Celery-based async execution
- Progress tracking and monitoring
- Error handling and recovery
- Notification systems (Email, Telegram)

## 🌐 API Endpoints

### Main Operations
```http
# Create orchestration
POST /api/agent-orchestra/orchestrations/

# List orchestrations
GET /api/agent-orchestra/orchestrations/

# Get orchestration details
GET /api/agent-orchestra/orchestrations/{id}/

# Cancel orchestration
POST /api/agent-orchestra/orchestrations/{id}/cancel/

# ✨ NEW: Rerun orchestration
POST /api/agent-orchestra/orchestrations/{id}/rerun/

# Delete orchestration
DELETE /api/agent-orchestra/orchestrations/{id}/
```

### Export & Management
```http
# Export as PDF
GET /api/agent-orchestra/orchestrations/{id}/export_pdf/

# Export as CSV
GET /api/agent-orchestra/orchestrations/{id}/export_csv/

# Export as JSON
GET /api/agent-orchestra/orchestrations/{id}/export_json/

# Rate orchestration
POST /api/agent-orchestra/orchestrations/{id}/rate/

# Archive/favorite
POST /api/agent-orchestra/orchestrations/{id}/archive/
POST /api/agent-orchestra/orchestrations/{id}/favorite/
```

## 🔧 Management Commands

### Agent Management
```bash
# Create agent templates
python manage.py create_agent_templates

# Create specialized agents
python manage.py create_saas_specialization
python manage.py create_ecommerce_specialization
python manage.py create_financial_agents

# Fix stuck agents
python manage.py fix_stuck_agents
```

### Progress Simulation
```bash
# Simulate agent progress
python manage.py simulate_agent_progress

# Continuous simulation
python manage.py simulate_agent_progress --continuous --interval 30

# Run progress script
./run_agent_progress.sh
```

### Monitoring & Testing
```bash
# Monitor orchestrations
python manage.py monitor_orchestrations

# Test agent execution
python manage.py test_agent_execution

# Test real AI execution
python manage.py test_real_ai_execution
```

### Reddit Scout
```bash
# Deploy Reddit Scout
python manage.py scout_reddit_startups

# Create Reddit Scout template
python manage.py create_reddit_scout_template
```

## 🎯 Usage Examples

### Creating an Orchestration
```python
from agent_orchestra.models import TaskOrchestration
from agent_orchestra.orchestrator import AgentOrchestrator

# Via API
orchestration = TaskOrchestration.objects.create(
    user=request.user,
    master_task="Create business plan for AI-powered fitness app",
    email_requested=True,
    email_address="founder@startup.com"
)

# Via Orchestrator
orchestrator = AgentOrchestrator(user)
result = await orchestrator.execute_complex_task(
    "Analyze market opportunity for blockchain voting system"
)
```

### Rerunning an Orchestration
```python
# Via API call
curl -X POST http://localhost:8000/api/agent-orchestra/orchestrations/113/rerun/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# Response
{
  "status": "Orchestration rerun started",
  "new_orchestration_id": 116,
  "original_orchestration_id": 113,
  "agents_cloned": 4
}
```

### Monitoring Progress
```python
# Check orchestration status
orchestration = TaskOrchestration.objects.get(id=123)
print(f"Status: {orchestration.overall_status}")
print(f"Progress: {orchestration.completion_percentage}%")

# Check agent statuses
for agent in orchestration.agents.all():
    print(f"{agent.template.name}: {agent.current_status} ({agent.progress_percentage}%)")
```

## 🔍 Advanced Features

### Self-Development Agent
- Analyzes codebase structure and patterns
- Identifies improvement opportunities
- Generates implementation suggestions
- Supports 22+ file types (Python, JS, Dart, etc.)

### Financial Intelligence
- Real market data integration (14 premium APIs)
- 3-year financial projections
- Valuation models and unit economics
- Investment analysis and recommendations

### Universal Builder
- Complete codebase generation
- 43 professional visual styles
- Multi-platform deployment (Web, Mobile, Desktop)
- Industry-specific templates

### Reddit Scout
- Real-time trend analysis across 5 startup subreddits
- Opportunity identification and scoring
- Market validation insights
- Competitor analysis

## 📊 Performance & Analytics

### Cost Optimization (July 1, 2025)
- **GPT-4.1-nano Migration**: 33% cost reduction
- **Input Tokens**: $0.10/M (was $0.15/M)
- **Output Tokens**: $0.40/M (was $0.60/M)
- **Context Window**: 1M tokens (improved from 128K)

### Execution Metrics
- **Average Orchestration Time**: 15-30 minutes
- **Agent Success Rate**: 95%+
- **User Satisfaction**: 8.5/10 average rating
- **Export Formats**: PDF, CSV, JSON, Email

### Real-Time Features
- WebSocket progress updates
- Live agent status monitoring
- Instant notification delivery
- Collaborative workspace sharing

## 🔧 Development & Debugging

### Local Development
```bash
# Start Celery worker
celery -A server worker -l info --concurrency=4

# Start Redis
redis-server

# Run development server
python manage.py runserver

# Monitor logs
tail -f celery.log
```

### Testing
```bash
# Run agent orchestra tests
python manage.py test agent_orchestra

# Test specific orchestration
python test_orchestration.py

# Test Reddit Scout
python test_reddit_scout.py
```

### Common Issues & Solutions

#### Agent Stuck in "Initializing"
```bash
python manage.py fix_stuck_agents
# or
python manage.py fix_stuck_agents --complete-all
```

#### WebSocket Authentication
```python
# Ensure JWT token in headers
headers = [
    (b'authorization', f'Bearer {token}'.encode()),
]
```

#### Orchestration Deletion Issues
```bash
# Force delete with cascade cleanup
python manage.py fix_orchestration_delete
```

## 🚀 Future Roadmap

### Planned Features
1. **Real-time Collaboration** - Multi-user orchestrations
2. **Advanced Analytics** - Performance dashboards
3. **Integration Hub** - Third-party service connections
4. **Custom Agents** - User-defined agent templates
5. **Workflow Automation** - Triggered orchestrations

### Performance Improvements
1. **Caching Layer** - Redis-based result caching
2. **Parallel Execution** - Enhanced multi-agent processing
3. **Smart Routing** - Intelligent model selection
4. **Result Streaming** - Real-time result delivery

---

## 📝 Documentation

- **API Documentation**: `/backend/AGENT_ORCHESTRA_API.md`
- **Progress Tracking**: `/CURRENT_STATE/active-tasks.md`
- **Recent Fixes**: `/CURRENT_STATE/recent-fixes.md`
- **Overall Progress**: `/backend/PROGRESS.md`

## 🤝 Contributing

1. Follow the existing code patterns and agent templates
2. Update documentation when adding new features
3. Test all changes with real orchestrations
4. Update version numbers and changelogs
5. Ensure proper error handling and logging

---

**Last Updated**: July 1, 2025  
**Version**: 2.1.0  
**Status**: Production Ready ✅