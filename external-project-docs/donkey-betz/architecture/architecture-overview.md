# Core Architecture Overview

## Overview
Donkey Betz is a sophisticated AI-powered business intelligence platform that transforms exercise into productive work time. Built on Django with a multi-layered architecture, it integrates 21+ specialized AI agents, real-time data processing, and advanced learning systems.

## Architecture

### System Topology
```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│                    WebSocket & REST API Layer                    │
├─────────────────────────────────────────────────────────────────┤
│                      Django Backend Core                         │
├──────────────┬───────────────┬──────────────┬──────────────────┤
│Agent Orchestra│ Memory Palace │Tool Orchestra│ Learning Systems │
├──────────────┼───────────────┼──────────────┼──────────────────┤
│    Teams     │Reality Engine │ API Gateway  │Symbolic Anchors  │
├──────────────┼───────────────┼──────────────┼──────────────────┤
│    Scouts    │  Embeddings   │50+ Services  │Pattern Learning  │
├──────────────┴───────────────┴──────────────┴──────────────────┤
│              PostgreSQL + pgvector + Redis + Celery             │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow
1. **Request Entry**: User request → WebSocket/REST API
2. **Context Injection**: Knowledge Base enriches request with user context
3. **Task Analysis**: Agent Orchestra analyzes and decomposes tasks
4. **Agent Assignment**: Tasks distributed to specialized agents/teams
5. **Memory Retrieval**: Memory Palace provides relevant context
6. **Processing**: Agents execute with tool access and memory
7. **Mythology Check**: Results validated for hallucinations
8. **Response Delivery**: Real-time updates via WebSocket

### Agent Orchestra → Teams → Scouts → Tasks Flow
```
User Request
    ↓
Agent Orchestra (Orchestrator)
    ↓
Team Formation (Based on Task Requirements)
    ├── Business Team (Strategy, Financial, Marketing Agents)
    ├── Technical Team (Universal Builder, Code Agents)
    ├── Research Team (News Scout, Stock Scout, Reddit Scout)
    └── Creative Team (Image, Content Creation Agents)
    ↓
Scout Deployment (Information Gathering)
    ├── Reddit Scout → Subreddit Analysis
    ├── Stock Scout → Market Intelligence
    ├── News Scout → Current Events
    └── API Scout → External Data
    ↓
Task Execution (Parallel Processing)
    ├── Task Dependencies Managed
    ├── Real-time Progress Updates
    ├── Inter-agent Communication
    └── Result Aggregation
    ↓
Memory Storage & Learning
```

## Current State
- **Active Agents**: 21+ specialized AI agents
- **API Integrations**: 50+ external services
- **LLM Providers**: OpenAI, Anthropic, Google, Ollama
- **Real-time Features**: WebSocket support via Django Channels
- **Background Processing**: Celery with Redis broker
- **Database**: PostgreSQL with pgvector extension

## Key Components

### Backend Structure
- **Django Apps**: 20+ modular applications
- **Core Services**: Authentication, Profiles, Analytics
- **AI Systems**: Agent Orchestra, Memory Palace, Learning Intelligence
- **Business Systems**: Universal Builder, Stock Intelligence
- **Support Systems**: Security, Notifications, Tool Management

### Frontend Architecture
- **Framework**: React with TypeScript
- **State Management**: Redux + RTK Query
- **Real-time**: WebSocket integration
- **UI Library**: Material-UI based components
- **Routing**: React Router v6

## API Endpoints

### Core APIs
- `/api/agent-orchestra/` - Agent management and task orchestration
- `/api/memory/` - Memory Palace operations
- `/api/ai-partner/` - Personal AI interactions
- `/api/tools/` - Tool Orchestra gateway
- `/api/prompting/` - Prompt template management
- `/api/mythology-lab/` - Mythology tracking
- `/api/scout-intel/` - Scout information gathering
- `/ws/agent-updates/` - WebSocket for real-time updates

## Database Models

### Core Relationships
```
User
 ├── UserProfile (1:1)
 ├── AgentInstance (1:N)
 ├── MemoryEntry (1:N)
 ├── Conversation (1:N)
 └── WorkoutSession (1:N)

AgentTemplate
 ├── AgentInstance (1:N)
 ├── TaskOrchestration (N:N)
 └── TeamMembership (N:N)

MemoryEntry
 ├── MemoryEmbedding (1:1)
 ├── MemoryChain (N:N)
 └── SymbolicAnchor (N:N)

TaskOrchestration
 ├── TaskExecution (1:N)
 ├── TaskDependency (self-referential)
 └── AgentAssignment (N:N)
```

## Integration Points

### Major System Connections
1. **Agent Orchestra ↔ Memory Palace**: Context retrieval for agent tasks
2. **Memory Palace ↔ Learning Intelligence**: Pattern extraction and learning
3. **Tool Orchestra ↔ All Systems**: Unified API access layer
4. **Mythology Lab ↔ Agent Responses**: Hallucination detection
5. **Knowledge Base ↔ Request Processing**: Context enrichment
6. **Security Framework ↔ All Endpoints**: Privacy and rate limiting

### External Integrations
- **Stock Data**: Polygon.io WebSocket streaming
- **Image Generation**: DALL-E 3, Stable Diffusion
- **Search**: Multiple search APIs
- **Social**: Reddit API for scout intelligence
- **Communication**: SendGrid, Twilio
- **Analytics**: Custom event tracking

## Known Issues
- Embedding status tracking inconsistencies in Memory Palace
- WebSocket connection stability under high load
- Memory deduplication performance with large datasets
- Agent response time variability with complex tasks

## Future Enhancements
- GraphQL API layer for more efficient data fetching
- Kubernetes deployment for better scalability
- Event sourcing for complete audit trails
- Federated learning across user agents
- Enhanced multi-modal capabilities
- Blockchain integration for achievement verification

## Code Examples

### Agent Creation
```python
# backend/agent_orchestra/agent_factory.py
def create_agent_instance(user, template_name, custom_config=None):
    template = AgentTemplate.objects.get(name=template_name)
    instance = AgentInstance.objects.create(
        user=user,
        template=template,
        custom_name=f"{user.username}'s {template.name}",
        config=custom_config or template.default_config
    )
    return instance
```

### Memory Retrieval
```python
# backend/memory/services/memory_search.py
def search_memories(user, query, limit=10):
    embeddings = get_embeddings(query)
    memories = MemoryEntry.objects.filter(
        user=user
    ).annotate(
        similarity=CosineDistance('embedding__vector', embeddings)
    ).order_by('similarity')[:limit]
    return memories
```

### Task Orchestration
```python
# backend/agent_orchestra/services/orchestration.py
async def orchestrate_task(user, task_description):
    task = TaskOrchestration.objects.create(
        user=user,
        description=task_description,
        status='analyzing'
    )
    
    # Analyze and decompose task
    subtasks = await analyze_task(task_description)
    
    # Assign agents
    for subtask in subtasks:
        agent = select_best_agent(subtask)
        TaskExecution.objects.create(
            task=task,
            agent=agent,
            subtask_description=subtask
        )
    
    # Execute in parallel
    await execute_task_async(task)
    return task
```