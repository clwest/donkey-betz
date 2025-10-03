# Move That Ass - Project Review Framework

## Project Overview
**Project Path**: `/Users/donkeyking/development/move_that_ass`  
**Review Date Started**: [Current Date]  
**Primary Challenge**: Connecting multiple components built over the past year

---

## 1. Modular Review Approach

### Module Inventory Checklist
- [ ] List all major modules/components
- [ ] Identify module dependencies
- [ ] Document module purposes
- [ ] Note integration points

### Module Template
```
Module Name: [NAME]
Purpose: [What it does]
Dependencies: [What it needs]
Exports/Provides: [What other modules use from this]
Key Files: [Main files to review]
Review Status: [ ] Not Started [ ] In Progress [ ] Complete
Notes: 
```

### Your Modules:

#### Backend Django Apps:
1. **Module**: `accounts`
   - Purpose: User authentication, registration, JWT tokens
   - Dependencies: Django auth, allauth, rest_framework_simplejwt
   - Review Status: [ ]

2. **Module**: `agent_orchestra`
   - Purpose: AI agent orchestration system with 21 specialized agents
   - Dependencies: ai_services, celery, OpenAI/Anthropic APIs
   - Review Status: [ ]

3. **Module**: `ai_partner`
   - Purpose: Personal AI life partner with conversation memory
   - Dependencies: memory, prompts, ai_services
   - Review Status: [ ]

4. **Module**: `ai_services`
   - Purpose: Unified LLM interface (OpenAI, Anthropic, Google, etc.)
   - Dependencies: Multiple API keys, external AI services
   - Review Status: [ ]

5. **Module**: `content`
   - Purpose: Asset management, document handling, content creation
   - Dependencies: storage backends (S3/local), image processing
   - Review Status: [ ]

6. **Module**: `memory`
   - Purpose: Memory Palace system with pgvector for semantic search
   - Dependencies: PostgreSQL with pgvector extension
   - Review Status: [ ]

7. **Module**: `learning_intelligence`
   - Purpose: Phase 5 - Agent learning and concept evolution
   - Dependencies: memory, agent_orchestra
   - Review Status: [ ]

8. **Module**: `universal_builder`
   - Purpose: Dynamic content generation system
   - Dependencies: ai_services, content
   - Review Status: [ ]

9. **Module**: `walking_companion`
   - Purpose: Context-aware AI companion for fitness activities
   - Dependencies: ai_partner, movement
   - Review Status: [ ]

10. **Module**: `media_studio`
    - Purpose: Media generation (images, videos) via AI
    - Dependencies: Stability AI, Runway, Replicate APIs
    - Review Status: [ ]

11. **Module**: `ml_models`
    - Purpose: Machine learning models and predictions
    - Dependencies: TensorFlow, scikit-learn
    - Review Status: [ ]

12. **Module**: `vision`
    - Purpose: Computer vision and image analysis
    - Dependencies: OpenCV, ML models
    - Review Status: [ ]

#### Frontend Components:
13. **Module**: `donkey-betz-frontend` (React/Vite)
    - Purpose: Main web UI for business platform
    - Dependencies: React, TypeScript, Tailwind CSS
    - Review Status: [ ]

14. **Module**: `momentum_flutter`
    - Purpose: Mobile app (Flutter)
    - Dependencies: Flutter SDK, Dart
    - Review Status: [ ]

15. **Module**: `momentum_react`
    - Purpose: Alternative React frontend
    - Dependencies: React, Node.js
    - Review Status: [ ]

#### Infrastructure:
16. **Module**: `backend/server`
    - Purpose: Django settings, URLs, ASGI/WSGI config
    - Dependencies: Django, Channels, Celery
    - Review Status: [ ]

17. **Module**: `nginx`
    - Purpose: Reverse proxy and static file serving
    - Dependencies: Docker, SSL certificates
    - Review Status: [ ]

18. **Module**: `deploy`
    - Purpose: Deployment configurations and scripts
    - Dependencies: Docker, docker-compose
    - Review Status: [ ]

---

## 2. Project Overview Document

### System Architecture
```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                   │
├─────────────────┬────────────────┬─────────────────┬──────────────────┤
│   React Web UI  │  Flutter Mobile │  Platform       │   Firebase       │
│  (Vite + TS)    │     (Dart)      │  Selector       │   (Auth/Host)    │
└────────┬────────┴───────┬────────┴────────┬────────┴──────────┬───────┘
         │                │                  │                   │
         └────────────────┴──────────────────┴───────────────────┘
                                    │
                           ┌────────▼────────┐
                           │   Nginx Proxy   │
                           │  (Port 80/443)  │
                           └────────┬────────┘
                                    │
┌───────────────────────────────────┼────────────────────────────────────┐
│                           BACKEND LAYER                                 │
├────────────────────────────────────┴────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐     ┌──────────────────┐    ┌─────────────────┐ │
│  │  Django REST    │     │   WebSocket      │    │   Static Files  │ │
│  │  Framework      │────▶│   (Channels)     │    │   (WhiteNoise)  │ │
│  │  (Port 8000)    │     │   Real-time      │    └─────────────────┘ │
│  └────────┬────────┘     └──────────────────┘                        │
│           │                                                            │
│  ┌────────▼─────────────────────────────────────────────────┐        │
│  │                    Django Applications                     │        │
│  ├─────────────┬──────────────┬─────────────┬───────────────┤        │
│  │   Accounts  │ Agent        │ AI Partner  │  Learning     │        │
│  │   (Auth)    │ Orchestra    │ (Personal)  │ Intelligence  │        │
│  ├─────────────┼──────────────┼─────────────┼───────────────┤        │
│  │   Memory    │ Universal    │  Content    │  Media        │        │
│  │   Palace    │ Builder      │ Management  │  Studio       │        │
│  ├─────────────┼──────────────┼─────────────┼───────────────┤        │
│  │  Walking    │    Vision    │ ML Models   │  AI Services  │        │
│  │  Companion  │              │             │  (Interface)  │        │
│  └─────────────┴──────────────┴─────────────┴───────────────┘        │
│                                                                        │
└────────┬──────────────────┬─────────────────┬──────────────┬─────────┘
         │                  │                 │              │
┌────────▼────────┐ ┌───────▼──────┐ ┌───────▼──────┐ ┌────▼─────┐
│   PostgreSQL    │ │    Redis     │ │   Celery     │ │  Celery  │
│   + pgvector    │ │  (Cache &    │ │   Worker     │ │   Beat   │
│   (Primary DB)  │ │   Broker)    │ │  (Tasks)     │ │ (Sched)  │
└─────────────────┘ └──────────────┘ └──────────────┘ └──────────┘
                                              │
                                    ┌─────────▼─────────┐
                                    │  EXTERNAL APIs    │
                                    ├───────────────────┤
                                    │ • OpenAI          │
                                    │ • Anthropic       │
                                    │ • Google Gemini   │
                                    │ • Stability AI    │
                                    │ • Alpha Vantage   │
                                    │ • Reddit API      │
                                    │ • 20+ others      │
                                    └───────────────────┘
```

### Configuration & Environment

#### Required Services
- **PostgreSQL 15+** with pgvector extension
- **Redis 7+** for caching and Celery broker
- **Python 3.11+** for backend
- **Node.js 18+** for frontend build
- **Docker** (optional but recommended)

#### Key Environment Variables
```bash
# Core Django Settings
SECRET_KEY=<django-secret-key>
DEBUG=True/False
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# AI Service Keys (Required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
STABILITY_KEY=sk-...

# AI Service Keys (Optional)
GOOGLE_API_KEY=
GROQ_API_KEY=
DEEPSEEK_API_KEY=

# Financial APIs
ALPHA_VANTAGE_API_KEY=
POLYGON_API_KEY=

# Social APIs
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=

# Storage Configuration
USE_S3_STORAGE=false
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

#### Deployment Architecture
- **Production**: Docker Compose with Nginx, Gunicorn, Celery workers
- **Development**: Direct Django runserver with local services
- **Database**: PostgreSQL with pgvector for semantic search
- **Cache**: Redis for session storage and Celery tasks
- **File Storage**: Local filesystem or S3-compatible storage

### Performance Considerations
- **API Rate Limits**: Most external APIs have rate limits
- **Celery Workers**: Scale based on agent workload
- **Database Connections**: Connection pooling configured
- **Memory Usage**: pgvector indexes can be memory-intensive
- **Response Time**: WebSocket for real-time, REST for standard 

### Key Components - Detailed

#### 1. **Agent Orchestra System** 
- **Purpose**: Central AI orchestration system managing 21 specialized agents
- **Key Agents**:
  - Reddit Scout: Discovers business opportunities from Reddit
  - Stock Scout: Financial market analysis
  - Business Plan Agent: Automated business plan generation
  - Market Analysis Agent: Industry and competitor research
  - Content Creation Agents: Various content generation specialists
- **Integration Points**: AI Services, Memory Palace, Content Management
- **Critical Files**: 
  - `/backend/agent_orchestra/models.py` - Core data models
  - `/backend/agent_orchestra/tasks.py` - Celery task definitions
  - `/backend/agent_orchestra/agents/` - Individual agent implementations

#### 2. **Memory Palace System**
- **Purpose**: Advanced memory and search system with semantic understanding
- **Features**:
  - Vector embeddings using pgvector
  - <200ms retrieval performance
  - Cross-conversation search
  - Concept linking and evolution
- **Integration Points**: PostgreSQL with pgvector, AI Services for embeddings
- **Critical Files**:
  - `/backend/memory/models.py` - Memory models
  - `/backend/memory/vector_search.py` - Semantic search implementation

#### 3. **AI Services Layer**
- **Purpose**: Unified interface for multiple AI providers
- **Supported Providers**:
  - OpenAI (GPT-4, DALL-E)
  - Anthropic (Claude)
  - Google (Gemini)
  - Groq, DeepSeek, Ollama
  - Stability AI, Runway (media)
- **Features**: Provider failover, cost optimization, response caching
- **Critical Files**:
  - `/backend/ai_services/llm_interface.py` - Unified LLM interface
  - `/backend/ai_services/providers/` - Individual provider implementations

#### 4. **Universal Builder**
- **Purpose**: Dynamic content generation across multiple formats
- **Capabilities**:
  - Business plans, reports, presentations
  - Marketing materials
  - Technical documentation
  - Multi-format export (PDF, DOCX, HTML)
- **Integration Points**: AI Services, Content Management, Media Studio

#### 5. **Authentication & User System**
- **Purpose**: Multi-platform authentication and user management
- **Features**:
  - JWT token authentication
  - Social login support
  - Role-based permissions
  - Cross-platform session management
- **Integration Points**: Django auth, Firebase (optional), Frontend apps

### Data Flow

#### Primary User Journey: AI Agent Task Execution
```
User Request → React Frontend → Django REST API → Authentication
    │                                    │
    └──────────────────────────────────▶ Agent Orchestra
                                              │
                                              ├─→ Task Queue (Celery/Redis)
                                              │        │
                                              │        ├─→ Agent Selection
                                              │        ├─→ Context Gathering (Memory)
                                              │        ├─→ AI Service Calls
                                              │        └─→ Result Processing
                                              │
                                              └─→ WebSocket Updates → Frontend
```

#### Memory System Flow
```
User Conversation → AI Partner → Memory Creation
                        │              │
                        │              ├─→ Text Processing
                        │              ├─→ Embedding Generation (AI Service)
                        │              ├─→ Vector Storage (pgvector)
                        │              └─→ Relationship Mapping
                        │
                        └─→ Memory Retrieval
                                 │
                                 ├─→ Semantic Search
                                 ├─→ Context Building
                                 └─→ Response Enhancement
```

#### Business Plan Generation Flow
```
Reddit Idea Approved → Business Plan Agent Triggered
                              │
                              ├─→ Market Research Agent
                              ├─→ Financial Analysis Agent  
                              ├─→ Content Creation Agent
                              └─→ Universal Builder
                                        │
                                        ├─→ Template Selection
                                        ├─→ Content Assembly
                                        ├─→ Media Generation
                                        └─→ Export (PDF/DOCX)
```

### Current System State & Challenges

#### Working Features (95% Functional)
- ✅ 21 AI Agents operational
- ✅ Reddit Scout discovering opportunities
- ✅ Business plan generation
- ✅ Memory Palace with semantic search
- ✅ Real-time WebSocket updates
- ✅ Multi-provider AI integration
- ✅ Asset management system

#### Known Integration Challenges
1. **Authentication Complexity**
   - Multiple auth systems (Django, JWT, Firebase)
   - Token refresh issues between platforms
   - Session management across frontends

2. **Agent Task Coordination**
   - Agents sometimes use outdated context (fixed with date injection)
   - Task timeout handling (30-minute timeout implemented)
   - Inter-agent communication patterns

3. **Frontend-Backend Sync**
   - API endpoint inconsistencies (`/api/api/` double prefix)
   - TypeScript type mismatches
   - WebSocket authentication flow

4. **Performance Bottlenecks**
   - pgvector index rebuilding on large datasets
   - API rate limiting from external services
   - Celery task queue backlogs

5. **Data Consistency**
   - Cross-module data updates
   - Cache invalidation strategies
   - Transaction boundaries in async tasks

#### Recent Fixes Applied
- ✅ Agent stuck at 19:30 issue (timeout added)
- ✅ Reddit Scout auto-creation disabled
- ✅ Bulk actions for Reddit Ideas
- ✅ Agent date context (now using 2025)
- ✅ API endpoint normalization

### Quick Start Commands
```bash
# Backend Development
cd backend
source .venv/bin/activate
make migrate
make run-backend

# Frontend Development
cd donkey-betz-frontend
npm install
npm run dev

# Full Stack with Docker
docker-compose -f docker-compose.prod.yml up

# Run Tests
make test-backend
make test-frontend

# Common Tasks
python manage.py createsuperuser
python manage.py shell
celery -A server worker -l info
```

### Integration Point Template
```
Integration: [Component A] ←→ [Component B]
Type: [ ] REST API [ ] Direct Call [ ] Message Queue [ ] Database [ ] File System
Protocol/Format: 
Authentication: 
Error Handling: 
```

### Your Integration Points:
1. **Integration**: Frontend (React) ←→ Backend (Django)
   - Type: REST API + WebSockets
   - Protocol: HTTP/HTTPS, JWT authentication
   - Issues/Concerns: CORS configuration, token refresh, WebSocket auth

2. **Integration**: Backend ←→ PostgreSQL
   - Type: Database connection via Django ORM
   - Protocol: PostgreSQL wire protocol
   - Issues/Concerns: Connection pooling, pgvector extension setup

3. **Integration**: Backend ←→ Redis
   - Type: Cache + Message broker
   - Protocol: Redis protocol
   - Issues/Concerns: Memory limits, persistence configuration

4. **Integration**: Django ←→ Celery Workers
   - Type: Task queue via Redis
   - Protocol: Redis as message broker
   - Issues/Concerns: Task timeouts, worker scaling, result backend

5. **Integration**: AI Services ←→ External APIs
   - Type: REST API calls
   - Protocol: HTTPS with API keys
   - Issues/Concerns: Rate limits, API costs, error handling

6. **Integration**: Agent Orchestra ←→ Multiple Modules
   - Type: Internal Django app communication
   - Protocol: Python function calls, Django signals
   - Issues/Concerns: Circular dependencies, data consistency

7. **Integration**: Memory System ←→ pgvector
   - Type: Vector similarity search
   - Protocol: PostgreSQL extensions
   - Issues/Concerns: Index performance, embedding generation

8. **Integration**: Frontend ←→ Firebase
   - Type: Authentication/hosting
   - Protocol: Firebase SDK
   - Issues/Concerns: Auth synchronization with Django

9. **Integration**: Media Services ←→ Storage
   - Type: File storage (S3 or local)
   - Protocol: AWS SDK or filesystem
   - Issues/Concerns: Large file handling, CDN setup 

---

## 4. Tiered Review Strategy

### Level 1: Architecture Review
- [ ] Overall structure makes sense
- [ ] No circular dependencies
- [ ] Clear separation of concerns
- [ ] Scalability considerations

**Questions for AI Review**:
1. Is the architecture pattern appropriate for this use case?
2. Are there any obvious bottlenecks?
3. Missing components?

### Level 2: Module Implementation
**Module**: ________________
- [ ] Code quality
- [ ] Error handling
- [ ] Performance
- [ ] Security

**Module**: ________________
- [ ] Code quality
- [ ] Error handling
- [ ] Performance
- [ ] Security

### Level 3: Complex Areas
**Area 1**: ________________
- Complexity reason: 
- Specific concerns: 

**Area 2**: ________________
- Complexity reason: 
- Specific concerns: 

### Level 4: Integration Testing
- [ ] Integration tests exist
- [ ] Coverage of critical paths
- [ ] Error scenarios tested
- [ ] Performance under load

---

## 5. Project Map

### Directory Structure
```
move_that_ass/
├── backend/                    # Django backend application
│   ├── accounts/              # User auth & management
│   ├── agent_orchestra/       # 21 AI agents system
│   ├── ai_partner/           # Personal AI companion
│   ├── ai_services/          # Unified AI provider interface
│   ├── content/              # Asset & document management
│   ├── memory/               # Memory Palace with pgvector
│   ├── learning_intelligence/ # Agent learning system
│   ├── universal_builder/    # Dynamic content generation
│   ├── walking_companion/    # Fitness AI companion
│   ├── media_studio/         # AI media generation
│   ├── ml_models/            # Machine learning models
│   ├── vision/               # Computer vision
│   ├── server/               # Django config & settings
│   └── tests/                # Backend test suite
├── frontend/                  # Frontend applications
│   ├── momentum_flutter/     # Mobile app (Flutter)
│   ├── momentum_react/       # Alternative React UI
│   └── platform-selector/    # Platform switching
├── donkey-betz-frontend/     # Main React web UI
│   ├── src/                  # React source code
│   └── public/               # Static assets
├── deploy/                   # Deployment configs
├── nginx/                    # Web server config
├── scripts/                  # Utility scripts
└── docs/                     # Documentation
```

### Connection Matrix
| Component | Connects To | Via | Purpose |
|-----------|------------|-----|---------|
| React Frontend | Django Backend | REST API | User interactions |
| Django Backend | PostgreSQL | ORM | Data persistence |
| Django Backend | Redis | django-redis | Caching & queues |
| Celery Workers | Redis | Broker | Async task processing |
| Agent Orchestra | AI Services | Python calls | AI orchestration |
| AI Services | OpenAI/Anthropic | HTTPS | LLM completions |
| Memory System | pgvector | SQL | Semantic search |
| Media Studio | Stability/Runway | HTTPS | Media generation |
| Frontend | WebSocket | Channels | Real-time updates |
| Universal Builder | Content | Django models | Content management |

---

## 6. Review by Concern

### Security Review Checklist
- [ ] Authentication mechanisms
- [ ] Authorization/permissions
- [ ] Input validation
- [ ] Sensitive data handling
- [ ] API security
- [ ] Dependencies vulnerabilities

### Performance Review Checklist
- [ ] Database query optimization
- [ ] Caching strategy
- [ ] Resource usage
- [ ] Concurrent request handling
- [ ] Memory leaks
- [ ] Load testing results

### Error Handling Review
- [ ] Consistent error formats
- [ ] Proper error propagation
- [ ] User-friendly messages
- [ ] Logging strategy
- [ ] Recovery mechanisms

### Database Review
- [ ] Schema design
- [ ] Indexing strategy
- [ ] Query performance
- [ ] Data integrity
- [ ] Backup/recovery

### API Design Review
- [ ] RESTful principles
- [ ] Consistent naming
- [ ] Versioning strategy
- [ ] Documentation
- [ ] Rate limiting

---

## Next Steps

### Immediate Actions
1. Fill out the Module Inventory section
2. Create basic architecture diagram
3. List main integration points

### For Our Next Session
- Bring specific integration challenges
- Have code snippets ready for problem areas
- Prepare questions about specific modules

### Progress Tracking
- [ ] Step 1: Module breakdown complete
- [ ] Step 2: Overview document complete
- [ ] Step 3: Integration points mapped
- [ ] Step 4: First module reviewed
- [ ] Step 5: Project map created
- [ ] Step 6: First concern area reviewed

---

## Notes Section
[Add any additional notes, concerns, or discoveries here]

---

## AI Review Log
| Date | Module/Area | Issues Found | Status |
|------|-------------|--------------|--------|
| | | | |
| | | | |

