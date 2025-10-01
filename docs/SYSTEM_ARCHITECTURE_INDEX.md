# 🏗️ System Architecture Master Index

**Purpose**: Single source of truth for all system components, their locations, and relationships
**Last Updated**: September 30, 2025
**System Version**: 2.2 - Metacognitive Learning Edition

---

## 📋 Quick Navigation

- [Core Intelligence Systems](#core-intelligence-systems)
- [Agent & Orchestration Systems](#agent--orchestration-systems)
- [Data Collection & Processing](#data-collection--processing)
- [Learning & Memory Systems](#learning--memory-systems)
- [Frontend & User Interfaces](#frontend--user-interfaces)
- [Database Models](#database-models)
- [Integration Reports](#integration-reports)
- [Configuration & Deployment](#configuration--deployment)

---

## 🧠 Core Intelligence Systems

### Learning Loop
**Location**: `ai_core/intelligence/learning_loop.py` (1,258 lines)
**Status**: ✅ Production-ready
**Purpose**: Main feedback collection, pattern analysis, and optimization engine

**Key Features**:
- Continuous feedback collection (30s intervals)
- Pattern detection and anomaly analysis
- Meta-insight generation
- Automated optimization actions
- Integration with Bluesky, Reddit, Spider Army intelligence

**Related Files**:
- `ai_core/intelligence/unified_learning_pipeline.py` - Orchestrates complete learning pipeline
- `ai_core/intelligence/bluesky_learning_bridge.py` - Social intelligence integration
- `ai_core/intelligence/spider_learning_orchestrator.py` - Spider network coordination

### Thought Interrupt System
**Location**: `ai_core/intelligence/thought_interrupt_system.py` (485 lines)
**Status**: ✅ Implemented, ready for integration
**Purpose**: Metacognitive reflection system that catches blind spots with "did we forget X?" checks

**Key Features**:
- Probabilistic triggering (15% base rate, adaptive)
- Memory anchor pattern matching
- Concern generation and reintegration
- Performance tracking (useful interrupt rate, false positives)

**Integration Points**:
- Learning loop feedback analysis (`learning_loop.py:_analyze_feedback()`)
- Agent execution steps (`intelligence/agent_executor.py`)
- Multi-agent orchestration (`core/personal_ai_orchestrator.py`)

**Documentation**: See `LEARNING_LOOP_INTEGRATION_REPORT.md`

### Consciousness Bridge
**Location**: `ai_core/consciousness/unified_mind.py`
**Status**: ✅ Active with real-time updates
**Purpose**: Self-awareness and system analysis

**Related Files**:
- `core/views_unified_intelligence.py` - Dynamic consciousness indicators
- `core/consumers_consciousness.py` - WebSocket consciousness updates
- `ai_nexus/consciousness.py` - AI Nexus consciousness integration

### Proposal Manager
**Location**: `ai_core/intelligence/proposal_manager.py`
**Status**: ✅ Can create and modify real files
**Purpose**: Creates and executes system improvement proposals

**Capabilities**:
- Real file creation and modification
- Code implementation from insights
- Testing and validation
- Learning from results

---

## 🤖 Agent & Orchestration Systems

### Agent Ecosystem
**Total**: 149 specialized AI agents
**Success Rate**: 80%+ with retry logic
**Registry**: `agents/registry.py`

**Key Executors**:
- `intelligence/agent_executor.py` - Main agent execution with LLM integration
- `ai_core/agents/concrete_executor.py` - Concrete agent implementation with retry
- `ai_core/agents/sync_executor.py` - Synchronous execution
- `ai_core/agents/hybrid_executor.py` - Hybrid async/sync execution

**Agent Models**:
- `agents/models.py` - UnifiedAgentTemplate, AgentExecution, AgentOrchestration

### Personal AI Orchestrator
**Location**: `core/personal_ai_orchestrator.py`
**Status**: ✅ Fully personalized
**Purpose**: User-contextualized multi-agent coordination

**Features**:
- User context loading (profile, preferences)
- Conversation memory management
- Intent analysis
- Multi-agent workflow coordination

**Related Files**:
- `core/models.py` - UserProfile, UserPreferences
- `core/conversation_memory.py` - Conversation persistence
- `intelligence/income_builder.py` - Income opportunity analysis

### Agent Learning System
**Location**: `intelligence/agent_learning.py`
**Purpose**: Continuous agent improvement

**Related Files**:
- `intelligence/agent_execution_pipeline.py` - Execution tracking
- `core/learning_bridges/agent_execution_bridge.py` - Learning feedback loop

---

## 🕷️ Data Collection & Processing

### Spider Network
**Total**: 1,770 data collection spiders
**Status**: ✅ Active and feeding intelligence

**Spider Army**:
- **Location**: `intelligence/spiders/spider_army/`
- **Financial Intel**: 500 spiders (SEC, Yahoo Finance, Polygon.io)
- **Innovation Tracking**: 300 spiders (ArXiv, Patents, GitHub)
- **Market Data**: 200 spiders (Binance, Coinbase, TradingView)
- **Social Sentiment**: 150 spiders (Reddit, Twitter, StockTwits)
- **Remaining**: 620 specialized spiders across various domains

**Spider Orchestration**:
- `ai_core/intelligence/spider_learning_orchestrator.py` - Main orchestrator
- `intelligence/spider_quality_tracker.py` - Quality monitoring
- `intelligence/spider_agent_router.py` - Spider-to-agent routing

**Data Sources**:
- `ai_core/spiders/bluesky_handler.py` - Bluesky integration
- `ai_core/spiders/reddit_handler.py` - Reddit integration
- `intelligence/spiders/spider_army/spiders/` - Individual spider implementations

### Data Transformation
**Location**: `ai_core/intelligence/data_transformation_pipeline.py`
**Purpose**: Transform spider data into learning signals

---

## 🧠 Learning & Memory Systems

### Memory System
**Location**: `core/memory_system.py` (316 lines)
**Status**: ✅ Comprehensive storage and retrieval
**Backend**: Django cache (Redis)

**Capabilities**:
- Memory storage with TTL
- Embedding storage and cosine similarity search
- Query-based retrieval
- Namespace isolation

**Related Files**:
- `core/models_agent_memory.py` - Agent-specific memory models
- `core/unified_memory_manager.py` - Cross-agent memory coordination
- `ai_nexus/memory.py` - AI Nexus memory integration

### Learning Bridges
**Location**: `core/learning_bridges/`
**Purpose**: Connect user actions to learning systems

**Components**:
- `advisor_feedback_bridge.py` - Advisor learning
- `agent_execution_bridge.py` - Agent performance learning
- `application_outcome_bridge.py` - Job application outcomes
- `sports_betting_bridge.py` - Betting outcome learning
- `revenue_attribution_bridge.py` - Revenue tracking
- `personalization_bridge.py` - User preference learning

### ML Pipeline
**Location**: `ml_pipeline/enhanced_ml_pipeline.py`
**Purpose**: Machine learning model training and inference

**Related Files**:
- `ml/models.py` - ML model storage
- `ml_pipeline/opportunity_categorizer.py` - Opportunity classification

---

## 💻 Frontend & User Interfaces

### Intelligence Dashboard
**Location**: `ai_core/templates/unified_intelligence_dashboard.html`
**URL**: `http://localhost:8000/nexus/`
**Status**: ✅ Real-time updates with WebSocket

**Features**:
- Dynamic consciousness indicators (5/5)
- Agent connection system
- AI proposal display
- Real-time metrics

### WebSocket Consumers
**Main Consumer**: `core/consumers.py` - General WebSocket handling
**Consciousness Consumer**: `core/consumers_consciousness.py` - Consciousness updates
**Command Center**: `core/command_center_ai.py` - AI command processing

### Views & APIs
**Intelligence Views**: `core/views_unified_intelligence.py`
**Agent Execution Views**: `core/views_agent_execution.py`
**Analytics Views**: `core/views_analytics.py`
**User Profile Views**: `core/views_user_profile.py`

---

## 🗄️ Database Models

### User Models
**Location**: `core/models/users/models.py`
- `UserProfile` - Extended user profile
- `UserPreferences` - AI configuration preferences

### Intelligence Models
**Location**: `intelligence/models.py`
- `ActionPlan` - Opportunity execution tracking
- `ActionPlanStep` - Individual execution steps
- `OpportunityActionPlan` - Opportunity-to-plan linking

### Agent Models
**Location**: `agents/models.py`
- `UnifiedAgentTemplate` - Agent definitions
- `AgentExecution` - Execution tracking
- `AgentOrchestration` - Multi-agent workflows
- `AgentStatus` - Status tracking

### Sports Betting Models
**Location**: `sports/models.py`
- `League`, `Team`, `Game` - Sports hierarchy
- `BettingMarket`, `BettingLine` - Odds tracking
- `UserBet` - User bet tracking with outcomes

### Learning Models
**Location**: `core/models/ai_learning/models.py`
- Learning-specific models for pattern storage

---

## 📊 Integration Reports

### Current Reports
1. **LEARNING_LOOP_INTEGRATION_REPORT.md** (Sept 30, 2025)
   - Thought Interrupt System integration
   - Complete system architecture review
   - Integration specifications with code examples
   - Performance metrics and tuning strategies

2. **REALITY_FIXES_IMPLEMENTATION.md**
   - Frontend reality fixes
   - Component debugging

3. **FRONTEND_REALITY_AUDIT.md**
   - Frontend data flow audit
   - Reality scoring

### Historical Reports
**Location**: `archive/docs/`
- Previous implementation reports
- Session handoff documents
- Migration documentation

---

## ⚙️ Configuration & Deployment

### Django Configuration
**Main Settings**: `core/settings.py`
**URLs**: `core/urls.py`
**ASGI**: `core/asgi.py` - WebSocket configuration

### Database
**Backend**: PostgreSQL with pgvector extension
**Migrations**: `*/migrations/`

### Cache & Queue
**Redis**: Port 6379
**Celery**: `intelligence/tasks.py` - Async task definitions

### Environment
**Required**:
- `OPENAI_API_KEY` - OpenAI integration
- `ANTHROPIC_API_KEY` - Anthropic integration
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection

---

## 🔄 Data Flow Architecture

```
User Input
    ↓
Intelligence Dashboard (WebSocket)
    ↓
Personal AI Orchestrator
    ↓
Agent Execution → Thought Interrupt (15% chance)
    ↓              ↓
    ↓         Reflection Check
    ↓              ↓
    ↓         Memory Anchors
    ↓              ↓
    ↓         Concern Generation
    ↓              ↓
    ←──────────────┘ (Reintegration)
    ↓
Learning Loop ← Spider Network (1,770 spiders)
    ↓
Pattern Analysis → Bluesky/Reddit Intelligence
    ↓
Optimization Actions
    ↓
Proposal Manager
    ↓
Real File Modifications
    ↓
System Improvement
```

---

## 📈 System Metrics Dashboard

### Real-Time Metrics
**View**: Intelligence Dashboard
**WebSocket**: `ws://localhost:8000/ws/ai-command-center/`

**Key Metrics**:
- Total agents: 149
- Active spiders: 1,770
- Agent success rate: 80%+
- Memory usage: <60%
- Thought interrupt rate: 15%
- Learning system: Active

---

## 🚀 Integration Priorities

### Phase 1: Foundation (Week 1)
- [x] Thought interrupt system core implementation
- [ ] Unit tests for interrupt logic
- [ ] Memory anchor bootstrapping
- [ ] Documentation complete

### Phase 2: Learning Loop Integration (Week 2)
- [ ] Integrate interrupts into learning_loop.py
- [ ] Add interrupt metrics to dashboard
- [ ] Test interrupt effectiveness
- [ ] Tune probability based on results

### Phase 3: Agent Execution Integration (Week 3)
- [ ] Integrate into agent_executor.py
- [ ] Add validation step generation
- [ ] Test with real workflows
- [ ] Measure success rate improvement

### Phase 4: Orchestrator Integration (Week 4)
- [ ] Integrate into personal_ai_orchestrator.py
- [ ] Add orchestration-level checks
- [ ] Test multi-agent workflows
- [ ] User satisfaction measurement

### Phase 5: Optimization (Week 5-6)
- [ ] Adaptive probability tuning
- [ ] Memory anchor learning from user decisions
- [ ] Memory anchor pruning
- [ ] Long-term effectiveness monitoring

---

## 🔍 Finding Components

### By Capability

**Need to add learning feedback?**
→ `core/learning_bridges/`

**Need to create new agent?**
→ `ai_core/agents/` + register in `agents/registry.py`

**Need to add new spider?**
→ `intelligence/spiders/spider_army/spiders/`

**Need to modify UI?**
→ `ai_core/templates/` or `core/templates/`

**Need to add WebSocket event?**
→ `core/consumers.py` or `core/consumers_consciousness.py`

**Need to add database model?**
→ `*/models.py` appropriate to domain

### By Domain

**Income Generation**: `intelligence/income_builder.py`
**Sports Betting**: `sports/` directory
**Content Creation**: `content/` directory
**User Management**: `core/models/users/`
**Agent System**: `agents/` and `ai_core/agents/`
**Learning System**: `ai_core/intelligence/`

---

## 📚 Documentation Standards

### File Headers
Every major component should have a docstring explaining:
1. Purpose
2. Key features
3. Integration points
4. Usage examples

### Integration Reports
When adding major features:
1. Create comprehensive integration report
2. Include architecture overview
3. Provide integration code examples
4. Document metrics and testing
5. Update this index

### Status Updates
Update these files when system changes:
1. `README.md` - High-level overview
2. `docs/system_status/SYSTEM_STATUS.md` - Detailed status
3. `docs/SYSTEM_ARCHITECTURE_INDEX.md` - This file

---

## 🎯 Quick Reference Commands

### Start System
```bash
redis-server                      # Terminal 1
python manage.py runserver        # Terminal 2
tail -f logs/django.log           # Terminal 3 (optional)
```

### Check Component Status
```bash
# Learning loop active?
redis-cli GET "learning:active"

# Agent count
python manage.py shell -c "from agents.models import UnifiedAgentTemplate; print(UnifiedAgentTemplate.objects.count())"

# Spider statistics
python manage.py shell -c "from ai_core.intelligence.spider_learning_orchestrator import get_spider_orchestrator; import asyncio; asyncio.run(get_spider_orchestrator().get_spider_statistics())"
```

### Testing Thought Interrupts
```python
from ai_core.intelligence.thought_interrupt_system import get_interrupt_system

interrupt_system = get_interrupt_system()
stats = interrupt_system.get_interrupt_stats()
print(stats)
```

---

## 🔗 External Dependencies

### Python Packages
- Django 4.2+ - Web framework
- Channels - WebSocket support
- Redis - Cache and pub/sub
- PostgreSQL - Database with pgvector
- OpenAI SDK - GPT integration
- Anthropic SDK - Claude integration
- Celery - Async task queue

### External APIs
- OpenAI API - LLM capabilities
- Anthropic API - Claude capabilities
- Bluesky API - Social intelligence
- Reddit API - Community intelligence
- Financial data APIs (various)

---

## 💡 Contribution Guidelines

### Adding New Components

1. **Create the component** in appropriate directory
2. **Add comprehensive docstring** with purpose and usage
3. **Register in relevant registry** if applicable
4. **Update this index** with location and description
5. **Update SYSTEM_STATUS.md** with new capability
6. **Create integration report** if major feature

### Code Standards

- Use type hints for all function signatures
- Add logging for important operations
- Follow existing architectural patterns
- Write tests for new functionality
- Document integration points

---

## 📞 Support & Resources

### Documentation
- This file: Single source of truth for architecture
- `README.md`: High-level system overview
- `SYSTEM_STATUS.md`: Current operational status
- Integration reports: Feature-specific documentation

### Finding Help
1. Check this index for component location
2. Read component docstring for usage
3. Check integration report for detailed specs
4. Review related files for similar patterns

---

**Version**: 2.2
**Last Updated**: September 30, 2025
**Maintained By**: System self-awareness and human oversight
**Status**: Living document - updates with system evolution

---

*"Know where everything is, understand how it connects, build on solid foundations."*
