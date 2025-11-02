# Donkey Betz Agent Orchestra

A Django-based AI agent orchestration system for sports betting analytics and business intelligence.

## Project Structure

```
donkey-betz-agent-orchestra/
├── backend/                 # Django backend
│   ├── agents/             # Agent orchestration system
│   ├── api/                # REST API endpoints
│   ├── core/               # Django settings and configuration
│   ├── integrations/       # AI provider integrations (OpenAI, Anthropic)
│   ├── odds_calculator/    # Betting odds calculations
│   └── manage.py           # Django management
├── run_agent.py            # CLI tool for running agents
└── venv/                   # Python virtual environment
```

## Available Agents

The system includes 10 specialized AI agents:

- **Business Agent** - Business plans, strategies, financial projections
- **Research Agent** - Market analysis, competitive research, data analysis  
- **Content Agent** - Blog posts, marketing copy, documentation
- **Technical Agent** - Architecture reviews, system design, code analysis
- **Marketing Agent** - Campaigns, growth strategies, positioning
- **Financial Agent** - Financial analysis, budgeting, ROI calculations
- **Legal Agent** - Compliance analysis, risk assessment
- **Creative Agent** - Design concepts, branding, creative direction
- **Career Agent** - Resume reviews, career planning, skill development
- **Communication Agent** - Messaging, presentations, stakeholder communications

## Quick Start

### Run Django Server
```bash
cd backend
python manage.py runserver
```

### Execute Agents via CLI
```bash
# Run any agent with a task
python run_agent.py <agent_type> "<task_description>"

# Examples:
python run_agent.py business "Create a marketing plan for a fitness app"
python run_agent.py research "Analyze the electric vehicle market trends"
python run_agent.py content "Write a blog post about remote work productivity"
python run_agent.py financial "Calculate ROI for a sports betting platform"
```

### View Agent Results
```bash
# Check recent agent executions
python backend/manage.py shell -c "
from agents.models import AgentInstance
for i in AgentInstance.objects.all()[:5]:
    print(f'{i.template.name}: {i.status} - {i.task_description[:50]}...')
"
```

## AI Provider Configuration

### Using Mock Provider (Default)
The system runs with a mock AI provider by default, generating realistic content without API costs.

### Using Real AI Providers
Set environment variables for real AI integration:

```bash
# OpenAI
export OPENAI_API_KEY="REDACTED"

# Anthropic Claude
export ANTHROPIC_API_KEY="REDACTED"
```

## Agent Architecture

### Agent Templates
Pre-configured agent specifications in database with:
- Specialization areas and capabilities
- System prompts and personality traits
- LLM provider and model configuration
- Performance metrics and routing keywords

### Agent Instances
Individual executions tracking:
- Task descriptions and context
- Execution progress and results
- Token usage and cost estimation
- Success/failure states

### Agent Orchestration
Complex multi-agent workflows with:
- Sequential agent execution
- Result passing between agents
- Real-time WebSocket updates
- Comprehensive logging and metrics

## Sports Betting Integration

### Odds Calculator
- Line movement analysis
- Arbitrage opportunity detection  
- Expected value calculations
- Kelly Criterion bet sizing

### Sports Analytics
- Team/player performance analysis
- Injury impact assessment
- Weather factor analysis
- Sharp money detection

## Development Commands

### Database
```bash
python backend/manage.py migrate
python backend/manage.py shell
```

### Agent Management
```bash
# Initialize agent templates
python backend/manage.py init_agents

# Run specific agent
python run_agent.py research "task description here"
```

### Testing
```bash
# Test agent execution
python backend/manage.py shell -c "
from agents.models import AgentTemplate
from agents.executor import AgentExecutor
# Test execution code here
"
```

## API Endpoints

- `/api/agents/` - List available agents
- `/api/agents/execute/` - Execute agent with task
- `/api/orchestrations/` - Multi-agent workflows
- `/api/results/` - Agent execution results

## WebSocket Support

Real-time agent execution updates via WebSocket connections for:
- Progress monitoring
- Result streaming  
- Error notifications
- Multi-agent orchestration status

## Environment Variables

```bash
DJANGO_SECRET_KEY="your-secret-key"
OPENAI_API_KEY="REDACTED"      # Optional
ANTHROPIC_API_KEY="REDACTED" # Optional
DEBUG=True                             # Development only
```

## Notes

- Agents use mock AI provider by default (no API keys required)
- Real AI integration requires OpenAI or Anthropic API keys
- All agent executions are logged in the database
- WebSocket support enables real-time monitoring
- System designed for sports betting analytics but applicable to any domain