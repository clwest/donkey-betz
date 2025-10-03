# Component Dependencies Map

## 🔗 Core Component Dependencies

### 1. Agent System
**Location**: `backend/agent_orchestra/`
**Dependencies**:
- OpenAI API (required)
- Celery + Redis (for async execution)
- Django models & PostgreSQL
- Memory system (for context)
- Tool system (for capabilities)

**Can run standalone**: ❌ No (needs memory & tools)

### 2. Memory System
**Location**: `backend/shared_memory/`, `backend/memory/`
**Dependencies**:
- PostgreSQL with pgvector extension
- OpenAI embeddings API
- Redis for caching

**Can run standalone**: ✅ Yes (core storage layer)

### 3. Content Creation
**Location**: `backend/content/`
**Dependencies**:
- OpenAI API (text generation)
- DALL-E API (image generation)
- Agent system (for orchestration)
- Memory system (for context)

**Can run standalone**: ⚠️ Partial (better with agents & memory)

### 4. Tool System
**Location**: `backend/tool_orchestra/`
**Dependencies**:
- External API keys (various services)
- Agent system (for execution context)

**Can run standalone**: ❌ No (needs agents to use tools)

### 5. Prompting System
**Location**: `backend/prompts/`, `backend/voice_and_prompting/`
**Dependencies**:
- Memory system (for optimization)
- Agent system (for execution)

**Can run standalone**: ⚠️ Partial (better integrated)

### 6. Mythology (Validation)
**Location**: `backend/mythology/`
**Dependencies**:
- Content system (to validate)
- Memory system (for patterns)

**Can run standalone**: ❌ No (needs content to validate)

## 🏗️ Integration Architecture

```
┌─────────────────────────────────────────┐
│           Content Studio API            │
│         (Main Orchestrator)              │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┬───────────┬───────────┐
    ▼                 ▼           ▼           ▼
┌────────┐      ┌────────┐  ┌────────┐  ┌────────┐
│Prompting│      │ Agents │  │ Memory │  │ Tools  │
└────┬────┘      └────┬───┘  └────┬───┘  └───┬────┘
     │                │            │           │
     └────────────────┴────────────┴───────────┘
                      │
                ┌─────▼─────┐
                │  Content   │
                │ Generation │
                └─────┬─────┘
                      │
                ┌─────▼─────┐
                │ Mythology  │
                │ Validation │
                └───────────┘
```

## 📦 Minimal Dependencies for MVP

### Required Python Packages
```python
# Core (must have)
django==4.2.0
openai==1.0.0
celery==5.3.0
redis==5.0.0
psycopg2-binary==2.9.0
pgvector==0.2.0  # KEEP IT! Your competitive advantage
numpy==1.24.0    # Required for vector operations

# Storage
djangorestframework==3.14.0

# Nice to have (can remove for MVP)
# stripe==5.0.0    # Add when monetizing
```

### External Services
```yaml
Required:
  - OpenAI API key ($20/month minimum)
  - PostgreSQL database (local or free tier)
  - Redis (local or free tier)

Optional for MVP:
  - Stripe (when ready to charge)
  - Email service (can use console backend)
  - File storage (can use local)
```

## 🔄 Extraction Order

### Phase 1: Core Foundation
1. **Memory System** - Simplify to basic text storage
2. **Agent System** - Single agent type only
3. **Prompting** - Basic optimization only

### Phase 2: Value Creation  
1. **Content Creation** - Text and images only
2. **Tools** - 3-5 essential tools only
3. **Mythology** - Basic quality checks

### Phase 3: Integration
1. Wire everything together
2. Single API endpoint
3. Simple UI

## 🚫 Components to SKIP for MVP

### Completely Remove
- ❌ Campaign Manager
- ❌ Trading Intelligence
- ❌ Voice Journals
- ❌ Enterprise Auth
- ❌ System Intelligence
- ❌ Analytics Platform
- ❌ Business Intelligence
- ❌ Security Testing
- ❌ Advanced WebSocket features
- ❌ Multi-tenant support

### Simplify Drastically
- ⚠️ Authentication → Simple JWT
- ⚠️ Permissions → Single user type
- ⚠️ Agent types → One universal agent
- ⚠️ Memory search → Text matching only
- ⚠️ Tools → Hardcode 3-5 tools
- ⚠️ UI → Single page

## 💉 Dependency Injection Pattern

```python
# How to wire components together simply

class ContentStudio:
    def __init__(self):
        # Minimal initialization
        self.memory = SimpleMemoryService()
        self.agent = SimpleAgentService()
        self.content = SimpleContentService()
        
    def create(self, prompt):
        # Simple flow
        context = self.memory.search(prompt)
        enhanced = self.agent.enhance(prompt, context)
        result = self.content.generate(enhanced)
        self.memory.store(result)
        return result

# That's it! No complex dependency injection needed
```

## 🎯 Success Criteria

A component is ready for extraction when:
- ✅ Can run with minimal dependencies
- ✅ Has clear input/output interface
- ✅ Doesn't require 10+ other systems
- ✅ Can be understood in 30 minutes
- ✅ Has obvious value to users

## 📊 Complexity Reduction

| Component | Current Files | MVP Files | Reduction |
|-----------|--------------|-----------|-----------|
| Agents | 50+ | 5 | 90% |
| Memory | 30+ | 3 | 90% |
| Content | 40+ | 4 | 90% |
| Tools | 20+ | 2 | 90% |
| Prompting | 15+ | 2 | 87% |
| Mythology | 10+ | 1 | 90% |
| **Total** | **165+** | **17** | **90%** |

## 🔑 Key Insight

**The power isn't in the individual components, but in their integration.**

Focus on:
1. Simple, clean interfaces between components
2. One-way data flow
3. Minimal coupling
4. Clear responsibilities
5. Graceful degradation

The goal: **From 165+ files to 17 files that actually work.**