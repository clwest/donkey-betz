# Unified Donkey Betz Platform

## 🚀 Production-Ready AI Intelligence Amplifier

A comprehensive AI platform combining sports betting analytics, content generation, multi-agent orchestration with 150 specialized agents, and **revolutionary AI Income Builder for users starting from $0**.

## ✨ Features

### 🤖 Agent Orchestration System ✅
- **150 Specialized Agents** across multiple domains
- **25+ Expert Advisors** with real track records
- **Multi-Agent Workflows** with parallel execution
- **Real-time Collaboration** visualization
- **Asynchronous Execution** via Celery/Redis
- **WebSocket Live Updates** for all components
- **Multi-Provider Support** (OpenAI, Anthropic, Google AI)
- **ML Pipeline** for pattern recognition and learning

### 💰 AI Income Builder (NEW!) ✅
- **Start from $0** - No investment required
- **8 Income Streams** including:
  - Content Writing ($500-$3000/mo)
  - Prompt Engineering ($1000-$5000/mo)
  - AI Automation ($800-$4000/mo)
  - Digital Products ($300-$2000/mo)
  - AI Tutoring ($600-$3000/mo)
  - Social Media Management ($500-$2500/mo)
- **Personalized Matching** based on skills
- **Success Path Timeline** with weekly milestones
- **Earnings Projections** up to 1 year

### Sports Betting Intelligence
- **NCAAF Data Integration** with real-time odds
- **Kelly Criterion Calculator** for optimal bet sizing
- **Market Analysis** and arbitrage detection
- **WebSocket Live Updates** for odds changes

### Content Generation System
- **Multi-format Support** (articles, scripts, social)
- **RAG-enhanced Generation** with pgvector
- **Version Control** for content iterations
- **Automated Workflows** with templates

### Infrastructure
- **Django 5.x** backend with async support
- **React 18** frontend with TypeScript
- **PostgreSQL** with pgvector for embeddings
- **Redis** for caching and Celery broker
- **WebSockets** via Django Channels
- **Docker** containerization ready

## 🛠️ Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+ with pgvector
- Redis 6+
- Node.js 18+

### Installation

1. **Clone and setup environment**
```bash
git clone https://github.com/your-repo/unified-donkey-betz.git
cd unified-donkey-betz
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

4. **Setup database**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

5. **Start services**
```bash
# Quick start - all services with one command:
make unified-dev

# Or start services individually:
# Terminal 1: Django backend with WebSockets (port 8000)
python manage.py runserver

# Terminal 2: Celery worker
celery -A core worker -l info

# Terminal 3: Celery beat (optional, for scheduled tasks)
celery -A core beat -l info

# Terminal 4: Frontend (port 3000)
cd frontend && npm run dev

# Stop all services:
make unified-stop
```

## 🎮 Usage

### Agent Execution

Execute agents programmatically:
```python
from agents.models import UnifiedAgentTemplate, AgentExecution
from agents.tasks import execute_agent

# Find an agent
agent = UnifiedAgentTemplate.objects.get(name="research-agent")

# Create execution
execution = AgentExecution.objects.create(
    template=agent,
    task_description="Research latest AI trends",
    input_data={"topic": "LLMs"}
)

# Trigger async execution
execute_agent.delay(execution_id=execution.execution_id)
```

### API Endpoints

- `POST /api/agents/execute/` - Execute an agent
- `GET /api/agents/` - List available agents
- `GET /api/agents/executions/` - View execution history
- `GET /ws/assistant/` - WebSocket for real-time updates

### Testing

Run the test suite:
```bash
# Test agent execution
python test_agent_execution.py

# Run Django tests
python manage.py test

# Frontend tests
cd frontend && npm test
```

## 📊 Monitoring

### Celery Monitoring with Flower
```bash
celery -A core flower --port=5555
# Visit http://localhost:5555
```

### Database Status
```bash
python manage.py dbshell
\dt  # List tables
SELECT COUNT(*) FROM agents_agentexecution;  # Check executions
```

## 🏗️ Architecture

```
unified-donkey-betz/
├── core/               # Core Django app
├── agents/            # Agent orchestration system
├── sports/            # Sports betting analytics
├── content/           # Content generation
├── frontend/          # React frontend
├── mobile/            # React Native app
└── docker/            # Docker configs
```

## 🔧 Configuration

### Required Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Redis
REDIS_URL=redis://localhost:6379

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 📈 Performance

- **Agent Execution**: ~6.5s average (simple tasks)
- **Concurrent Executions**: Unlimited (Celery workers)
- **WebSocket Latency**: <100ms
- **Token Usage**: 400-600 tokens/simple query

## 🐛 Troubleshooting

### Agents not executing?
1. Check Redis: `redis-cli ping`
2. Verify Celery: `celery -A core inspect active`
3. Check logs: `tail -f celery.log`
4. Verify API keys in `.env`

### WebSocket connection issues?
1. Check Daphne is running
2. Verify CORS settings
3. Check browser console for errors

## 📝 Recent Updates

- **2025-09-14**: Priority 5 & 6 Complete! AI Income Builder, Neural Orchestra, Control Center
- **2025-09-19**: All 150 agents operational with complete integration
- **2025-09-13**: Implemented 102 agents, 25+ advisors, ML pipeline integration
- **2025-09-12**: Added multi-agent workflow orchestration and testing suite
- **2025-09-11**: Created learning loop with feedback incorporation
- **2025-09-10**: Built performance monitoring dashboard
- **2025-09-09**: Fixed agent execution system - full async pipeline working
- **2025-09-08**: Integrated 87 agents from multiple sources

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Documentation: `/docs`
- Issues: GitHub Issues
- API Docs: `/api/docs`

## 🎯 Recent Achievements

### Phase 3: ML Pipeline ✅
- **Pattern Recognition Model**: MLX-optimized sports-to-crypto correlation analysis
- **User Behavior Learning**: Personalized decision confidence calibration
- **Cross-Domain Transfer Learning**: Options IV → Sports betting value detection
- **Apple Silicon Optimization**: Native M3 support with 8GB memory allocation

### Phase 4: Advisor Network ✅
- **25+ Expert Advisors** deployed across 4 domains:
  - 8 Sports Betting Experts (NBA, NFL, MLB specialists)
  - 7 Crypto Analysts (DeFi, NFT, trading experts)
  - 5 Options Traders (volatility, gamma, theta specialists)
  - 5 Real Estate Specialists (commercial, residential experts)
- **Collaborative Decision System**: Weighted consensus with verification
- **Real-time Track Record**: Dynamic performance monitoring

### Phase 5: Orchestration & Testing ✅
- **Multi-Agent Workflows**: Complex task orchestration with parallel execution
- **End-to-End Testing Suite**: Comprehensive integration and performance tests
- **Performance Monitoring**: Real-time dashboard with metrics and alerts
- **Learning Loop**: Continuous improvement through feedback incorporation

### Phase 6: UI/UX Enhancements ✅
- **Decision Command Center**: AI Income Builder for $0 start with 8 income streams
- **Neural Orchestra**: Real-time visualization of agent-advisor collaboration
- **Control Center**: Unified monitoring, analytics, and AI insights dashboard
- **WebSocket Integration**: Live updates across all components

## 🔮 Next Steps

### Priority 7: Production Deployment
- [ ] Security hardening and penetration testing
- [ ] Load balancing and auto-scaling
- [ ] CI/CD pipeline with automated testing
- [ ] Production monitoring with Prometheus/Grafana

### Priority 8: Advanced Features
- [ ] Mobile app deployment (React Native)
- [ ] Advanced portfolio optimization
- [ ] Cross-platform synchronization
- [ ] Enterprise API with rate limiting

---

Built with ❤️ by the Donkey Betz Team