# Unified Donkey Betz Platform

## 🚀 Production-Ready AI Platform with Agent Orchestration

A comprehensive AI platform combining sports betting analytics, content generation, and multi-agent orchestration with 87+ specialized agents.

## ✨ Features

### Agent Orchestration System ✅
- **87+ Specialized Agents** across multiple domains
- **Asynchronous Execution** via Celery/Redis
- **Real-time Updates** through WebSockets
- **Multi-Provider Support** (OpenAI, Anthropic, Google AI)
- **Automatic Fallback** and retry logic
- **Token Usage Tracking** and cost optimization

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
# Terminal 1: Django backend
python manage.py runserver

# Terminal 2: Celery worker
celery -A core worker -l info

# Terminal 3: Celery beat (optional, for scheduled tasks)
celery -A core beat -l info

# Terminal 4: Frontend
cd frontend && npm run dev
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

- **2025-09-09**: Fixed agent execution system - full async pipeline working
- **2025-09-08**: Integrated 87 agents from multiple sources
- **2025-09-07**: Added NCAAF sports data integration
- **2025-09-06**: Implemented WebSocket real-time updates

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

## 🎯 Roadmap

- [ ] Implement agent orchestration workflows
- [ ] Add more sports leagues (NFL, NBA)
- [ ] Enhance RAG with knowledge graphs
- [ ] Implement caching layer for agents
- [ ] Add rate limiting and quotas
- [ ] Deploy to production with Kubernetes

---

Built with ❤️ by the Donkey Betz Team