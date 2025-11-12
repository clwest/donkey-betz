# 🤖 Agent-to-Agent Communication Architecture
**Session 81 - Phase 2: Agent Orchestration Implementation**

**Date:** November 11, 2025
**Status:** ✅ Design Complete - Ready for Implementation
**Purpose:** Enable specialized agents to query each other and maintain domain-specific state

---

## 🎯 Problem Statement

**Current Issue:**
- Personal Assistant (GPT-5-mini) handles 40+ functions directly
- GPT-5-mini inconsistently extracts context from conversation history
- Audio generation works, but "Add speech to video" fails because GPT-5-mini can't reliably extract audio URLs

**User's Question:**
> "We have already built a pretty major network of Agents haven't we, is it possible to use the agents to address different sections and have the main Assistant just hand off to the assistants?"

**Solution:**
Transform from monolithic function calling to specialized agent orchestration.

---

## 🏗️ Architecture Overview

### Current Architecture (Function Calling)
```
User → Personal Assistant (GPT-5-mini) → 40+ Functions → Backend APIs
                       ↓
            Conversation History (Last 6 messages)
                       ↓
         GPT-5-mini tries to extract context (unreliable)
```

### Target Architecture (Agent Orchestration)
```
User → Personal Assistant (Router) → Specialized Agents → Backend APIs
                                          ↓
                                    Agent State (Redis)
                                          ↓
                              Agent Query Protocol
                                          ↓
                        Agents query each other for data
```

---

## 📦 Existing Infrastructure (Already Built!)

### 1. Agent Communication (`intelligence/agent_communication.py`)
**What Exists:**
- `AgentCommunication` class with WebSocket messaging
- `send_message(from_agent, to_agent, message)` - agent-to-agent messaging
- `broadcast_to_orchestration()` - message all agents in orchestration
- `AgentChannel` model - communication channels with message history
- Message tracking in metadata

**What We'll Use:**
- Foundation for agent query protocol
- Message passing infrastructure

---

### 2. Shared Memory System (`intelligence/shared_memory.py`)
**What Exists:**
- Redis-based shared memory (db=2, 30-day TTL)
- `store_memory(entity_type, entity_id, memory_type, content)` - store any memory
- `retrieve_memory(entity_type, entity_id, memory_type)` - retrieve memories
- `share_context(entity_type, entity_id, context)` - share current context (1-hour TTL)
- `get_global_context()` - aggregated context from all entities
- `AgentMemoryInterface` - convenience interface for agents

**What We'll Use:**
- AudioAgent stores "most_recent_audio_url" in shared memory
- VideoAgent queries AudioAgent's shared memory
- Perfect for domain-specific state!

---

### 3. Agent Orchestrator (`intelligence/agent_orchestrator.py`)
**What Exists:**
- `AgentOrchestrator` class
- `select_agents_for_task()` - choose best agents based on capabilities
- `execute_multi_agent()` - parallel/sequential/hierarchical execution
- `route_task_to_specialist()` - route to single best agent
- AgentExecution tracking

**What We'll Use:**
- Task routing logic
- Agent selection based on capabilities

---

### 4. Agent Models (`agents/models.py`)
**What Exists:**
- `UnifiedAgentTemplate` - agent definitions with capabilities, routing_keywords, specialization
- `AgentExecution` - tracks execution status, results, token usage
- `AgentOrchestration` - coordinates multi-agent workflows
- `AgentChannel` - communication channels
- Performance metrics tracking

**What We'll Use:**
- Create AudioAgent and VideoAgent as UnifiedAgentTemplate instances
- Use AgentExecution to track agent operations

---

## 🆕 What We Need to Build

### 1. Agent Query Protocol (`intelligence/agent_query_protocol.py`) - NEW
**Purpose:** Enable synchronous agent-to-agent queries

**Interface:**
```python
class AgentQueryProtocol:
    """
    Enable agents to query each other for specific data.
    Built on top of existing AgentCommunication.
    """

    def query_agent(
        self,
        from_agent: UnifiedAgentTemplate,
        to_agent: UnifiedAgentTemplate,
        query_type: str,
        parameters: Dict = None
    ) -> Dict[str, Any]:
        """
        Query another agent for specific data.

        Args:
            from_agent: Querying agent
            to_agent: Agent to query
            query_type: Type of query ('get_most_recent', 'get_by_id', etc.)
            parameters: Query parameters

        Returns:
            Query result
        """

    def register_query_handler(
        self,
        agent: UnifiedAgentTemplate,
        query_type: str,
        handler: Callable
    ):
        """
        Register a handler for a specific query type.

        Example:
            audio_agent.register_query_handler(
                'get_most_recent',
                lambda: audio_agent.get_most_recent_audio()
            )
        """
```

**Implementation Strategy:**
- Build on existing `AgentCommunication.send_message()`
- Use Redis for synchronous request/response pattern
- Query handlers stored in agent's metadata
- Timeout after 5 seconds if no response

---

### 2. Audio Agent (`agents/audio_agent.py`) - NEW
**Purpose:** Manage audio generation state and operations

**Core Functionality:**
```python
class AudioAgent(UnifiedAgentTemplate):
    """
    Specialized agent for audio generation.
    Maintains state of generated audio files.
    """

    def __init__(self):
        self.memory = AgentMemoryInterface(agent_id='audio_agent')
        self.name = 'AudioAgent'
        self.specialization = 'audio_generation'
        self.capabilities = ['text_to_speech', 'text_to_sound', 'voice_dubbing']

    def generate_speech(self, user, text: str, voice: str = 'Rachel'):
        """Generate speech and store result in memory"""
        # Call existing backend
        result = runway_provider.text_to_speech(text=text, voice=voice)

        # Store in agent memory
        self.memory.remember('most_recent_audio', {
            'audio_url': result.get('audio_url'),
            'task_id': result.get('task_id'),
            'type': 'speech',
            'text': text,
            'voice': voice,
            'timestamp': timezone.now().isoformat()
        })

        return result

    def get_most_recent_audio(self) -> Dict:
        """Query handler: return most recent audio"""
        return self.memory.recall('most_recent_audio')

    def get_audio_by_task_id(self, task_id: str) -> Dict:
        """Query handler: return specific audio by task_id"""
        return self.memory.recall(f'audio_task_{task_id}')
```

**State Storage:**
- Uses existing `AgentMemoryInterface` (Redis)
- Memory keys: `shared_memory:agent:audio_agent:most_recent_audio`
- 30-day TTL (from shared_memory.py)

---

### 3. Video Agent (`agents/video_agent.py`) - NEW
**Purpose:** Manage video operations and query AudioAgent

**Core Functionality:**
```python
class VideoAgent(UnifiedAgentTemplate):
    """
    Specialized agent for video operations.
    Can query AudioAgent for audio files.
    """

    def __init__(self):
        self.memory = AgentMemoryInterface(agent_id='video_agent')
        self.query = AgentQueryProtocol()
        self.name = 'VideoAgent'
        self.specialization = 'video_operations'
        self.capabilities = ['add_music_to_video', 'color_grade', 'text_overlay']

    def add_music_to_video(
        self,
        user,
        video_selection: str = 'last',
        audio_url: str = None,
        audio_volume: float = 0.3
    ):
        """
        Add audio to video.
        If audio_url not provided, query AudioAgent for most recent.
        """

        # If no audio_url provided, query AudioAgent
        if not audio_url:
            logger.info("🔍 Video Agent querying Audio Agent for recent audio...")

            # Get AudioAgent instance
            audio_agent = UnifiedAgentTemplate.objects.get(name='AudioAgent')

            # Query for most recent audio
            audio_data = self.query.query_agent(
                from_agent=self,
                to_agent=audio_agent,
                query_type='get_most_recent',
                timeout=5
            )

            if audio_data and audio_data.get('audio_url'):
                audio_url = audio_data['audio_url']
                logger.info(f"✅ Video Agent received audio URL: {audio_url}")
            else:
                return {
                    'success': False,
                    'error': 'No recent audio found. Please generate audio first.'
                }

        # Call DaVinci backend with audio_url
        result = add_music_to_video_backend(
            user=user,
            video_selection=video_selection,
            audio_url=audio_url,
            audio_volume=audio_volume
        )

        return result
```

**Agent Query Flow:**
```
User: "Add speech to my last video"
    ↓
Personal Assistant routes to VideoAgent
    ↓
VideoAgent.add_music_to_video(audio_url=None)
    ↓
VideoAgent queries AudioAgent: "get_most_recent"
    ↓
AudioAgent returns: {'audio_url': 'https://...', 'type': 'speech'}
    ↓
VideoAgent calls backend with audio_url
    ↓
DaVinci mixes audio with video
```

---

### 4. Personal Assistant Router (`core/views_image.py` modifications) - MODIFIED
**Purpose:** Route to specialized agents instead of executing functions directly

**Current Pattern:**
```python
def assistant_chat(request):
    # Call OpenAI with 40+ function definitions
    tools = get_all_ai_assistant_tools()  # 40+ functions

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=conversation[-6:],
        tools=tools
    )

    # Execute function directly
    if tool_name == 'generate_speech':
        result = _execute_generate_speech(user, parameters)
```

**New Pattern:**
```python
def assistant_chat(request):
    # Slim router - fewer tools, more routing
    tools = get_routing_tools()  # Just 5-10 high-level tools

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=conversation[-6:],
        tools=tools
    )

    # Route to specialized agent
    if tool_name == 'generate_speech':
        # Get AudioAgent
        audio_agent = UnifiedAgentTemplate.objects.get(name='AudioAgent')

        # Execute via agent
        agent_executor = AgentExecutor()
        result = audio_agent.generate_speech(user, parameters)

    elif tool_name == 'add_music_to_video':
        # Get VideoAgent
        video_agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')

        # VideoAgent will query AudioAgent if needed
        result = video_agent.add_music_to_video(user, parameters)
```

---

## 🔄 Data Flow Example: Audio → Video

### Current Flow (BROKEN):
```
1. User: "Generate speech saying welcome"
2. Personal Assistant calls generate_speech
3. Audio generates → stored in conversation history
4. User: "Add that speech to my last video"
5. Personal Assistant calls add_music_to_video(audio_url=???)
6. ❌ GPT-5-mini fails to extract audio_url from conversation
```

### New Flow (WORKS):
```
1. User: "Generate speech saying welcome"
2. Personal Assistant routes to AudioAgent
3. AudioAgent.generate_speech()
   ├─ Calls runway_provider.text_to_speech()
   └─ Stores in memory: agent:audio_agent:most_recent_audio
4. User: "Add that speech to my last video"
5. Personal Assistant routes to VideoAgent
6. VideoAgent.add_music_to_video(audio_url=None)
7. VideoAgent queries AudioAgent.get_most_recent_audio()
8. AudioAgent returns: {'audio_url': 'https://...'}
9. VideoAgent calls DaVinci backend with audio_url
10. ✅ Audio mixed with video successfully!
```

---

## 📊 Implementation Phases

### Phase 1: Agent Query Protocol (30 minutes)
- [ ] Create `intelligence/agent_query_protocol.py`
- [ ] Implement `query_agent()` method
- [ ] Implement `register_query_handler()` method
- [ ] Use Redis for request/response pattern
- [ ] Add timeout handling (5 seconds)

### Phase 2: Audio Agent (45 minutes)
- [ ] Create `agents/audio_agent.py`
- [ ] Extend UnifiedAgentTemplate
- [ ] Implement `generate_speech()` with state storage
- [ ] Implement `generate_sound_effect()` with state storage
- [ ] Register query handlers for `get_most_recent`
- [ ] Test memory storage/retrieval

### Phase 3: Video Agent (45 minutes)
- [ ] Create `agents/video_agent.py`
- [ ] Extend UnifiedAgentTemplate
- [ ] Implement `add_music_to_video()` with AudioAgent query
- [ ] Implement other video operations
- [ ] Test agent-to-agent queries

### Phase 4: Personal Assistant Router (45 minutes)
- [ ] Modify `core/views_image.py`
- [ ] Change from direct function execution to agent routing
- [ ] Create agent registry lookup
- [ ] Update tool definitions (reduce to routing tools)
- [ ] Test routing logic

### Phase 5: End-to-End Testing (30 minutes)
- [ ] Test: Generate speech → check memory
- [ ] Test: Query AudioAgent → verify response
- [ ] Test: Add music to video → verify agent query
- [ ] Test: Complete workflow without audio_url parameter
- [ ] Verify DaVinci receives correct audio_url

**Total Estimated Time:** 2.5-3 hours (1-2 sessions)

---

## 🎯 Success Criteria

### ✅ Agent Communication Working When:
- [ ] AudioAgent stores generated audio URLs in memory
- [ ] VideoAgent can query AudioAgent and receive data
- [ ] "Add speech to video" works WITHOUT explicit audio_url parameter
- [ ] Personal Assistant routes to specialized agents correctly
- [ ] Agent query protocol has <5 second response time

### ✅ User Experience Success:
- [ ] User generates audio → sees completion message
- [ ] User says "Add to video" → system auto-finds audio
- [ ] No need to manually provide URLs
- [ ] Natural conversation flow maintained

---

## 💡 Benefits of This Architecture

### 1. **Solves GPT-5-mini Limitation**
- No longer relies on AI to extract context
- Agents maintain their own state explicitly
- Reliable data passing between operations

### 2. **Leverages Existing Infrastructure**
- Uses AgentMemoryInterface (already built)
- Uses AgentCommunication (already built)
- Uses UnifiedAgentTemplate (already built)
- Minimal new code required

### 3. **Scalable**
- Easy to add new specialized agents
- Image Agent, 3D Agent, Character Agent, etc.
- Each agent maintains domain-specific state
- Personal Assistant becomes slim router

### 4. **Stateful**
- Agents remember their outputs
- Agents can query each other for data
- Enables complex multi-step workflows
- Foundation for agent collaboration

---

## 🔧 Technical Details

### Redis Keys Structure:
```
shared_memory:agent:audio_agent:most_recent_audio
shared_memory:agent:audio_agent:audio_task_abc123
shared_memory:agent:video_agent:most_recent_video
shared_memory:agent:video_agent:video_task_xyz789
```

### Query Protocol Pattern:
```python
# VideoAgent queries AudioAgent
query_result = query_protocol.query_agent(
    from_agent=video_agent,
    to_agent=audio_agent,
    query_type='get_most_recent'
)

# Behind the scenes:
# 1. Creates temporary Redis key: query:request:{uuid}
# 2. Sends message to AudioAgent via AgentCommunication
# 3. AudioAgent handler executes and stores result in Redis
# 4. VideoAgent polls Redis key for response (max 5 seconds)
# 5. Returns result to VideoAgent
```

### Agent Registration:
```python
# AudioAgent registers itself on startup
audio_agent = UnifiedAgentTemplate.objects.create(
    name='AudioAgent',
    display_name='Audio Generation Agent',
    specialization='audio_generation',
    capabilities=['text_to_speech', 'text_to_sound', 'voice_dubbing'],
    routing_keywords=['audio', 'speech', 'sound', 'voice', 'music'],
    system_prompt='You are a specialized audio generation agent...',
    is_active=True
)
```

---

## 🚀 Next Steps

**Immediate Action:** Start with Phase 1 (Agent Query Protocol)

**Why This Order:**
1. Query protocol is the foundation for agent communication
2. Can test query protocol in isolation before building agents
3. AudioAgent and VideoAgent depend on query protocol
4. Personal Assistant router is last (depends on all agents existing)

**Ready to begin implementation!**

---

**Status:** ✅ Design Complete
**Next:** Implement Agent Query Protocol (`intelligence/agent_query_protocol.py`)
**Estimated Time:** 30 minutes for query protocol implementation

---

*Generated: Session 81 - November 11, 2025*
*Architecture: Agent Orchestration with Specialized Agents*
