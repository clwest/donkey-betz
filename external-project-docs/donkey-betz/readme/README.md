# Agent Orchestra 🤖🎼

A standalone AI agent orchestration system extracted from the donkey_betz project. Agent Orchestra provides intelligent routing to specialized AI agents with real-time progress tracking and WebSocket communication.

## ✨ Features

- **🎯 Intelligent Routing**: 91.6% confidence routing to the most appropriate agent
- **🔄 Real-time Progress**: WebSocket-powered live updates during agent execution
- **⚡ 10 Specialized Agents**: Research, Business, Content, Technical, Creative, Marketing, Financial, Communication, Legal, and Career
- **🌐 Multi-Agent Orchestration**: Complex tasks handled by sequential agent coordination
- **🚀 Easy Deployment**: Docker-compose setup with `make dev` command
- **📊 WebSocket Dashboard**: Live monitoring of agent performance and system health

## 🏗️ Architecture

```
agent-orchestra/
├── backend/           # Django + Celery + Channels
│   ├── agents/        # Core agent system
│   ├── api/           # REST API + WebSocket consumers  
│   ├── core/          # Django settings
│   └── integrations/  # AI providers (OpenAI, Anthropic)
├── frontend/          # Vanilla JS + Tailwind CSS
│   ├── index.html     # Main application
│   └── demo.html      # Interactive demos
├── docker-compose.yml # Container orchestration
└── Makefile          # Development commands
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Redis 6.0+
- Docker & Docker Compose (optional)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd donkey-betz-agent-orchestra
make setup
```

### 2. Configure API Keys
```bash
cp .env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here
```

### 3. Start Development
```bash
make dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/api/v1/
- **Admin**: http://localhost:8000/admin/
- **Demos**: http://localhost:3000/demo.html

## 🎯 Agent Specializations

| Agent | Specialization | Key Capabilities |
|-------|----------------|------------------|
| 🔍 **Research** | Market Analysis | Market sizing, competitor research, trend identification |
| 📊 **Business** | Strategy & Finance | Business plans, financial modeling, go-to-market strategy |
| ✍️ **Content** | Content Creation | Blog posts, documentation, marketing copy, SEO content |
| 💻 **Technical** | Engineering | Code review, architecture design, API documentation |
| 🎨 **Creative** | Design & Branding | Brand identity, creative campaigns, visual concepts |
| 📈 **Marketing** | Growth & Campaigns | Marketing strategy, customer acquisition, analytics |
| 💰 **Financial** | Financial Analysis | Investment analysis, budgeting, financial reporting |
| 📢 **Communication** | PR & Messaging | Press releases, stakeholder communication, crisis management |
| ⚖️ **Legal** | Compliance | Contract review, regulatory guidance, risk assessment |
| 💼 **Career** | Professional Development | Resume optimization, interview prep, career planning |

## 🌐 API Endpoints

### Core Endpoints
- `POST /api/v1/execute/` - Execute single agent task
- `POST /api/v1/orchestrate/` - Multi-agent orchestration
- `POST /api/v1/suggest/` - Get agent suggestions
- `GET /api/v1/agents/` - List available agents
- `GET /api/v1/instances/{id}/` - Agent execution status

### Betting Odds API
- `POST /api/odds/convert` - Convert between odds formats (American, Decimal, Fractional)
- `POST /api/odds/kelly` - Calculate Kelly criterion for optimal bet sizing

### WebSocket Endpoints
- `ws://localhost:8000/ws/agent-progress/` - Real-time progress updates
- `ws://localhost:8000/ws/dashboard/` - System-wide metrics

## 🐳 Docker Deployment

### Development with Docker
```bash
make docker-dev
```

### Production Deployment
```bash
# Set production environment variables
export OPENAI_API_KEY=your-key
export ANTHROPIC_API_KEY=your-key

# Deploy with Docker
make deploy
```

## 🧪 Example Usage

### Single Agent Execution
```javascript
// Execute research task
const response = await fetch('/api/v1/execute/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    task_description: "Research the market for AI writing tools"
  })
});
```

### Multi-Agent Orchestration
```javascript
// Execute complex business task
const response = await fetch('/api/v1/orchestrate/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    task_description: "Launch strategy for productivity app",
    agent_sequence: ["research", "business", "marketing", "communication"]
  })
});
```

### WebSocket Progress Tracking
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/agent-progress/');
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Agent progress:', data);
};
```

## 📊 Demo Scenarios

The application includes interactive demos showcasing:

1. **Market Research Analysis** - Comprehensive market sizing and competitor analysis
2. **SaaS Business Planning** - Complete business plan with financial projections
3. **Multi-Agent Product Launch** - End-to-end launch strategy using 4 agents
4. **Financial Modeling** - Revenue projections and unit economics
5. **Competitor Intelligence** - Deep competitive landscape analysis

Access demos at: http://localhost:3000/demo.html

## 🔧 Development Commands

```bash
make help          # Show all available commands
make dev           # Start development servers
make test          # Run tests
make migrate       # Database migrations
make clean         # Clean temporary files
make docker-build  # Build Docker images
make status        # Check system status
```

## 🏛️ System Components

### Backend (Django)
- **Models**: Agent templates, instances, orchestrations
- **Routing**: Intelligent agent selection with 91.6% accuracy
- **Executors**: Async agent execution with progress tracking
- **WebSockets**: Real-time communication via Django Channels

### Frontend (Vanilla JS)
- **Progressive Web App**: Works offline, mobile-responsive
- **Real-time UI**: WebSocket integration for live updates  
- **Demo System**: Interactive examples and use cases
- **No Framework Dependencies**: Pure JavaScript + Tailwind CSS

### AI Integration
- **OpenAI**: GPT-4 support with streaming responses
- **Anthropic**: Claude integration for complex reasoning
- **Mock Provider**: Development and testing without API keys
- **Extensible**: Easy to add new AI providers

## ⚙️ Configuration

### Environment Variables
```bash
# Core Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# AI Providers
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Redis & Celery
REDIS_URL=redis://localhost:6379/0

# Agent Orchestra Settings  
AGENT_ORCHESTRA_MAX_CONCURRENT=10
AGENT_ORCHESTRA_TIMEOUT=300
AGENT_ORCHESTRA_ROUTING_THRESHOLD=0.916
```

### Database
- **Development**: SQLite (included)
- **Production**: PostgreSQL recommended
- **Migrations**: Automatic with `make migrate`

## 🔍 Monitoring & Debugging

### Health Check
```bash
curl http://localhost:8000/api/v1/health/
```

### System Status
```bash
make status  # Check all components
```

### Logs
```bash
make logs    # View recent logs
```

## 🚧 Limitations (MVP)

This is a simplified extraction focused on core functionality:

1. **Authentication**: Basic token auth (not production-ready)
2. **Memory System**: Simplified stub (not the full 267K memory system)
3. **Database**: SQLite default (PostgreSQL for production)
4. **Tests**: Limited test coverage (5-10 essential tests)
5. **UI**: Simple interface (not the full dashboard)

## 📊 Betting Odds API

### Odds Conversion
Convert between American, Decimal, and Fractional odds formats.

**Endpoint:** `POST /api/odds/convert`

**Request:**
```json
{
  "input_format": "american",
  "value": 150,
  "output_format": "decimal"  // optional, returns all if omitted
}
```

**Response:**
```json
{
  "decimal": 2.5,
  "american": 150,
  "fractional": "3/2",
  "implied_probability": 0.4,
  "notes": []
}
```

### Kelly Criterion Calculation
Calculate optimal bet sizing using the Kelly Criterion.

**Endpoint:** `POST /api/odds/kelly`

**Request:**
```json
{
  "odds_format": "american",
  "odds_value": 110,
  "win_probability": 0.58,
  "bankroll": 4000,
  "fractional_kelly": 0.5,  // optional, default 0.5
  "use_agent": false        // optional, enables agent delegation
}
```

**Response:**
```json
{
  "decimal_odds": 2.1,
  "implied_probability": 0.4762,
  "full_kelly_fraction": 0.1982,
  "recommended_fraction": 0.0991,
  "stake_full_kelly": 792.8,
  "stake_recommended": 396.4,
  "sanity": {
    "ev": 0.2180,
    "warnings": []
  },
  "delegated": false
}
```

### Environment Variables
- `ODDS_AGENT_DELEGATION=true` - Enable optional agent delegation for calculations

### Example Usage with cURL
```bash
# Convert odds
curl -X POST http://localhost:8000/api/odds/convert \
  -H "Content-Type: application/json" \
  -d '{"input_format": "american", "value": 150}'

# Calculate Kelly sizing
curl -X POST http://localhost:8000/api/odds/kelly \
  -H "Content-Type: application/json" \
  -d '{"odds_format": "american", "odds_value": 110, "win_probability": 0.58, "bankroll": 4000}'
```

## 🛣️ Roadmap

- [ ] Enhanced authentication and user management
- [ ] Full memory system integration
- [ ] Advanced analytics and reporting
- [ ] Plugin system for custom agents
- [ ] Multi-tenancy support
- [ ] Enterprise deployment guides

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Extracted from the donkey_betz project
- Built with Django, Celery, Channels, and Redis
- UI powered by Tailwind CSS and vanilla JavaScript
- AI integration via OpenAI and Anthropic APIs

---

**Agent Orchestra** - Orchestrating AI agents for complex business tasks 🎼🤖