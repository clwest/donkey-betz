# Section 1: Core AI & Assistant Systems
**Agent Name: AI Core Reviewer**

## Scope Overview
This section covers the core AI and assistant functionality that powers the Donkey Betz platform's intelligent interactions.

### Primary Directories:
- `backend/ai_partner/` - Main AI assistant functionality
- `backend/ai_services/` - AI service integrations
- `backend/ai_evolution/` - AI learning/evolution systems
- `backend/learning_intelligence/` - Learning and adaptation systems

## Analysis Instructions for Claude Code Agent

### 1. Conversation Flow Architecture
**Investigate:**
- `backend/ai_partner/models/` - ConversationSession, Message models
- `backend/ai_partner/services/` - ConversationService implementation
- `backend/ai_partner/utils/conversation_flow.py` - Flow control logic

**Key Questions:**
- How are conversations initiated and maintained?
- What is the session lifecycle?
- How are conversation contexts preserved between messages?
- What happens when a conversation ends?

### 2. AI Response Generation
**Investigate:**
- `backend/ai_services/enhanced_ai_service.py` - Core AI service
- `backend/ai_services/multi_model_service.py` - Multi-model architecture
- `backend/ai_partner/services/intelligent_prompt_service.py` - Prompt generation

**Key Questions:**
- How are prompts constructed?
- Which AI models are supported (OpenAI, Anthropic, etc.)?
- How is model selection determined?
- What is the fallback strategy if a model fails?

### 3. Context Management
**Investigate:**
- `backend/ai_partner/utils/context_manager.py` - Context handling
- `backend/memory/services/conversation_memory_service.py` - Memory integration
- `backend/ukf_system/services/unified_memory_search.py` - Memory retrieval

**Key Questions:**
- How much conversation history is maintained?
- How is relevant context retrieved from memory?
- What determines context window size?
- How are tokens managed to stay within limits?

### 4. AI Evolution System
**Investigate:**
- `backend/ai_evolution/models/` - Evolution models
- `backend/ai_evolution/services/darwin_service.py` - Evolution logic
- `backend/ai_evolution/services/mutation_service.py` - Response mutations

**Key Questions:**
- What is the Darwin-Gödel Machine Evolution Framework?
- How are AI responses evolved and optimized?
- What fitness metrics are used?
- Is this system currently active in production?

### 5. Learning Intelligence
**Investigate:**
- `backend/learning_intelligence/services/` - Learning services
- `backend/learning_intelligence/models/` - Learning models
- `backend/api/ukf_memory/services/profile_service.py` - User profile learning

**Key Questions:**
- How does the system learn from user interactions?
- What user facts are extracted and stored?
- How is learning data used to improve responses?
- What privacy controls exist for learned data?

### 6. Service Integration Points
**Investigate:**
- `backend/ai_partner/api.py` - REST endpoints
- `backend/ai_partner/consumers.py` - WebSocket handlers
- `backend/ai_partner/signals.py` - Django signals

**Key Questions:**
- What are the main API endpoints?
- How do WebSocket connections work?
- What events trigger AI processing?
- How are async operations handled?

### 7. Error Handling & Resilience
**Investigate:**
- `backend/ai_services/circuit_breaker.py` - Circuit breaker pattern
- `backend/ai_services/error_handlers.py` - Error handling
- `backend/ai_partner/utils/retry_logic.py` - Retry mechanisms

**Key Questions:**
- What happens when AI services fail?
- How are rate limits handled?
- What fallback mechanisms exist?
- How are errors logged and monitored?

### 8. Performance Considerations
**Investigate:**
- `backend/ai_services/cache_service.py` - Caching layer
- `backend/ai_partner/utils/streaming_response.py` - Response streaming
- Database query patterns in models

**Key Questions:**
- What caching strategies are employed?
- How is response streaming implemented?
- What are the performance bottlenecks?
- How are large conversations handled?

## Critical Files to Review
1. `backend/ai_partner/services/code_assistant_service.py` - Code understanding capabilities
2. `backend/ai_services/enhanced_sync_executor.py` - Synchronous execution logic
3. `backend/ai_partner/models/conversation.py` - Core conversation model
4. `backend/ai_evolution/services/evolution_orchestrator.py` - Evolution coordination
5. `backend/learning_intelligence/services/fact_extractor.py` - User fact extraction

## Integration Dependencies
- Memory system (for context retrieval)
- Agent Orchestra (for specialized tasks)
- Security system (for data privacy)
- WebSocket infrastructure (for real-time responses)

## Expected Outputs from Analysis
1. Complete conversation flow diagram
2. AI model selection logic flowchart
3. Context management strategy documentation
4. Performance metrics and bottlenecks
5. Security considerations for AI interactions
6. List of all AI-related API endpoints
7. WebSocket message protocol documentation
8. Error handling strategy summary

## Special Considerations
- The Reality Engine phenomenon - AI generating plausible but fictional data
- The "350 deployments" myth that spread through the system
- Privacy implications of the learning system
- Token usage and cost optimization
- Multi-model failover strategies