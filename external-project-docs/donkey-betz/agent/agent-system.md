# Agent System

## Overview
The Agent System in Donkey Betz is a sophisticated multi-agent orchestration framework that coordinates 21+ specialized AI agents to accomplish complex tasks. It features dynamic agent creation, continuous learning, team collaboration, and heterogeneous LLM support.

## Architecture

### Core Components
- **AgentTemplate**: Base configurations for different agent types
- **AgentInstance**: Active agents assigned to specific tasks
- **TaskOrchestration**: Multi-agent workflow management
- **AgentFactory**: Dynamic agent creation system
- **Learning Intelligence**: Continuous improvement framework
- **Communication Layer**: Inter-agent messaging and collaboration

### Agent Hierarchy
```
Base Agent Framework
    ├── Technical Agents (6 specializations)
    ├── Business Agents (4 specializations)
    ├── Creative Agents (4 specializations)
    ├── Financial Agents (4 specializations)
    ├── Legal Agents (4 specializations)
    ├── Communication Agents (4 specializations)
    ├── Research Agents (4 specializations)
    ├── Career Agents (4 specializations)
    └── Specialized Agents (5+ unique agents)
```

## Current State
- **Active Agent Types**: 21+ base agents
- **Custom Agents**: User-created specialized agents
- **Learning Stages**: unseen → exposed → acquired → reinforced
- **Performance Improvement**: 30-50% through adaptive learning
- **Team Configurations**: Homogeneous and heterogeneous teams
- **LLM Providers**: OpenAI, Anthropic, Google, Meta, Ollama

## Key Components

### Base Agents vs Custom Agents

#### Base Agents (21+ Specialized)
1. **Technical Domain**
   - Technical Agent (backend, frontend, database, devops, security, ml_engineering)
   - Universal Builder Agent (business code generation)
   - Self-Development Agent (autonomous codebase improvement)

2. **Business Domain**
   - Business Agent (strategy, operations, sales, product)
   - Financial Agent (modeling, investment, accounting, fundraising)
   - Business Builder Agent (business plan generation)

3. **Creative & Content**
   - Creative Agent (design, content, multimedia, innovation)
   - Content Agent (writing, social, technical, seo)
   - Brand Guidelines Agent (brand consistency)

4. **Research & Intelligence**
   - Research Agent (market, academic, industry, user)
   - Reddit Scout Agent (idea discovery)
   - Stock Analysis Agents (market analysis)

5. **Support Functions**
   - Legal Agent (contracts, IP, corporate, employment)
   - Communication Agent (pr, internal, executive, customer)
   - Career Agent (job_search, interview, development, transition)
   - Security Validator Agent (security assessment)

#### Custom Agents
- User-created with specific configurations
- Custom system prompts and behavior rules
- Personalized communication styles
- Domain-specific expertise
- Private or public visibility

### Agent Creation Process

#### Dynamic Factory Pattern
```python
# Agent creation flow
1. User Request Analysis
2. Parent Agent Selection
3. Specialization Determination
4. Configuration Generation
5. Instance Creation
6. Tool Assignment
7. Memory Integration
```

#### Configuration Options
- **Communication Style**: professional, friendly, creative, analytical, supportive
- **Tone**: formal, casual, enthusiastic, calm, direct
- **Approach**: detailed, concise, step-by-step, examples-focused
- **Focus Areas**: custom domain expertise
- **System Prompt**: behavioral instructions

### Agent Capabilities and Permissions

#### Universal Capabilities
- Memory Palace access for context
- Universal Knowledge Format (2,200+ documents)
- Mythology Lab hallucination protection
- Learning framework integration
- Multi-LLM provider access
- Research API integration

#### Tool Access Matrix
| Tool | Technical | Business | Creative | Research | Legal |
|------|-----------|----------|----------|----------|-------|
| code_executor | ✓ | - | - | - | - |
| web_search | ✓ | ✓ | ✓ | ✓ | ✓ |
| document_generator | ✓ | ✓ | ✓ | ✓ | ✓ |
| image_creator | - | - | ✓ | - | - |
| data_analyzer | ✓ | ✓ | - | ✓ | - |
| api_call | ✓ | ✓ | ✓ | ✓ | ✓ |

#### Permission Levels
- **requires_approval**: High-impact operations
- **max_concurrent_instances**: Resource limits
- **allowed_agents**: Tool access restrictions
- **user_scoped**: Privacy protection

### Agent Learning Mechanisms

#### Learning Intelligence Integration
1. **Performance Tracking**
   - Task success/failure rates
   - Execution time metrics
   - Token efficiency
   - Tool effectiveness

2. **Concept Mastery**
   - Learning stages progression
   - Confidence scoring (0.0-1.0)
   - Adaptation frequency tracking
   - Knowledge retention via symbolic anchors

3. **Continuous Improvement**
   - Pattern identification from successes
   - Failure analysis and correction
   - Performance-based routing optimization
   - Automated prompt refinement

#### Self-Evolution Service
```python
# Learning cycle
1. Execute Task → 2. Analyze Performance → 3. Extract Patterns
       ↑                                            ↓
       ← 5. Apply Improvements ← 4. Update Strategy
```

## API Endpoints

### Core Operations
- `POST /api/agent-orchestra/execute/` - Execute multi-agent task
- `GET /api/agent-orchestra/templates/` - List agent templates
- `GET /api/agent-orchestra/agents/available/` - Available agents
- `GET /api/agent-orchestra/agent-types/` - Agent type information

### Orchestration Management
- `GET /api/agent-orchestra/orchestrations/` - List orchestrations
- `GET /api/agent-orchestra/orchestration/{id}/status/` - Task status
- `GET /api/agent-orchestra/orchestration/{id}/timeline/` - Execution timeline
- `POST /api/agent-orchestra/orchestration/{id}/cancel/` - Cancel task

### Custom Agents
- `GET/POST /api/agent-orchestra/custom-agents/agents/` - CRUD operations
- `GET /api/agent-orchestra/custom-agents/templates/` - Templates
- `POST /api/agent-orchestra/custom-agents/conversations/` - Track usage
- `POST /api/agent-orchestra/custom-agents/feedback/` - Submit feedback

### Specialized Endpoints
- `POST /api/agent-orchestra/self-development/analyze/` - Code analysis
- `POST /api/agent-orchestra/reddit-scout/deploy/` - Reddit scouting
- `POST /api/agent-orchestra/stocks/analyze/` - Stock analysis
- `POST /api/agent-orchestra/security/validate/` - Security checks

## Database Models

### Core Agent Models
```python
AgentTemplate
    ├── name (CharField)
    ├── specializations (JSONField)
    ├── capabilities (JSONField)
    ├── default_config (JSONField)
    └── tools (ManyToMany → AgentTool)

AgentInstance
    ├── user (ForeignKey → User)
    ├── template (ForeignKey → AgentTemplate)
    ├── custom_name (CharField)
    ├── config (JSONField)
    ├── learning_stage (CharField)
    └── performance_metrics (JSONField)

CustomAgent
    ├── user (ForeignKey → User)
    ├── name (CharField)
    ├── system_prompt (TextField)
    ├── communication_style (CharField)
    ├── is_public (BooleanField)
    └── usage_stats (JSONField)
```

## Integration Points

### Internal Systems
- **Memory Palace**: Context retrieval and storage
- **Learning Intelligence**: Performance improvement
- **Tool Orchestra**: External API access
- **Mythology Lab**: Response validation
- **Knowledge Base**: Domain expertise

### External Integrations
- **LLM Providers**: Multi-provider support with failover
- **Search APIs**: Web search capabilities
- **Image Generation**: DALL-E, Stable Diffusion
- **Code Execution**: Sandboxed environments
- **Communication**: Email, messaging APIs

## Known Issues
- Agent selection optimization needs improvement for edge cases
- Learning transfer between similar agents is limited
- Team coordination overhead for simple tasks
- Custom agent validation could be more robust

## Future Enhancements
- Visual agent workflow designer
- Agent marketplace for sharing custom agents
- Advanced team formation algorithms
- Cross-user agent learning (privacy-preserved)
- Real-time agent performance dashboard
- Natural language agent creation
- Agent version control and rollback

## Code Examples

### Creating a Custom Agent
```python
# POST /api/agent-orchestra/custom-agents/agents/
{
    "name": "Startup Advisor",
    "description": "Expert in early-stage startup strategy",
    "communication_style": "supportive",
    "tone": "enthusiastic",
    "approach": "examples-focused",
    "domains": ["startups", "strategy", "fundraising"],
    "system_prompt": "You are an experienced startup advisor...",
    "is_public": false
}
```

### Executing a Multi-Agent Task
```python
# POST /api/agent-orchestra/execute/
{
    "master_task": "Create a mobile app business plan",
    "personal_ai_context": {
        "goals": ["Launch successful app"],
        "experience": ["Product management"],
        "preferences": ["Lean methodology"]
    },
    "required_agents": ["Business Agent", "Technical Agent", "Financial Agent"]
}
```

### Monitoring Agent Learning
```python
# GET /api/agent-orchestra/agent/{id}/learning-stats/
{
    "agent_id": "tech-agent-123",
    "learning_stage": "reinforced",
    "confidence_score": 0.92,
    "total_tasks": 156,
    "success_rate": 0.94,
    "average_execution_time": 12.3,
    "concept_mastery": {
        "react_optimization": 0.95,
        "api_design": 0.88,
        "database_design": 0.91
    }
}
```