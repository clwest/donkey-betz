# Detailed Investigation: AI Assistant "Life-like Flow" Issues

## Problem Statement
The AI Assistant lacks natural, life-like conversation flow. Responses may feel robotic, disconnected, or fail to maintain conversational context properly.

## Investigation Steps

### Step 1: Trace a Complete Conversation Flow
**Objective**: Follow a single message from input to response

1. **Start at WebSocket Entry Point**
   ```
   File: backend/ai_partner/consumers.py
   Method: ChatConsumer.receive()
   
   Questions:
   - How is the message parsed?
   - What validation occurs?
   - How is user authentication verified?
   ```

2. **Message Processing Pipeline**
   ```
   File: backend/ai_partner/services/conversation_service.py
   Method: process_message()
   
   Trace:
   - How is conversation history loaded?
   - What's the context window size?
   - Are previous messages truncated?
   ```

3. **Context Building**
   ```
   File: backend/ai_partner/utils/context_manager.py
   
   Investigate:
   - How many previous messages are included?
   - Is memory retrieval happening here?
   - What metadata is preserved?
   ```

### Step 2: Analyze Prompt Construction
**Objective**: Understand how prompts are built

1. **System Prompt Analysis**
   ```
   File: backend/ai_partner/services/intelligent_prompt_service.py
   Method: build_system_prompt()
   
   Extract:
   - The exact system prompt template
   - Personality instructions
   - Behavioral guidelines
   ```

2. **Dynamic Context Injection**
   ```
   Search for: "format_prompt", "build_prompt", "construct_prompt"
   
   Questions:
   - Is user profile data injected?
   - Are recent memories included?
   - Is there conversation style adaptation?
   ```

### Step 3: Memory Integration Analysis
**Objective**: How memories affect conversation

1. **Memory Retrieval During Conversation**
   ```
   File: backend/ukf_system/services/unified_memory_search.py
   Called from: conversation_service.py
   
   Debug:
   - Log what memories are retrieved
   - Check relevance scoring
   - Verify memory is actually used in prompts
   ```

2. **Memory Usage in Responses**
   ```
   Search pattern: "memory" in backend/ai_partner/
   
   Questions:
   - Are memories just retrieved or actually integrated?
   - How are memories formatted in the prompt?
   - Is there a feedback loop?
   ```

### Step 4: Response Generation Issues

1. **Model Configuration**
   ```
   File: backend/ai_services/enhanced_ai_service.py
   
   Check:
   - Temperature settings
   - Max tokens
   - System message content
   - Any hardcoded response patterns
   ```

2. **Response Post-Processing**
   ```
   Search for: "process_response", "format_response"
   
   Look for:
   - Response cleaning/filtering
   - Template application
   - Truncation logic
   ```

### Step 5: Conversation State Management

1. **Session Handling**
   ```
   File: backend/ai_partner/models/conversation.py
   Model: ConversationSession
   
   Investigate:
   - How long are sessions maintained?
   - What state is preserved between messages?
   - Are there session timeouts?
   ```

2. **Message Threading**
   ```
   Check database schema for:
   - message ordering
   - conversation branching
   - context inheritance
   ```

## Specific Code Queries

### Query 1: Find All Prompt Templates
```bash
grep -r "You are" backend/ai_partner/ --include="*.py"
grep -r "personality\|persona" backend/ai_partner/ --include="*.py"
grep -r "system.*prompt" backend/ai_partner/ --include="*.py"
```

### Query 2: Trace Context Window
```python
# In Django shell
from ai_partner.services.conversation_service import ConversationService
# Check the actual context window size
print(ConversationService.CONTEXT_WINDOW_SIZE)
```

### Query 3: Memory Integration Points
```bash
grep -r "unified_memory_search\|memory.*retrieve" backend/ai_partner/ --include="*.py"
```

## Testing Methodology

### Test 1: Context Preservation
1. Start a conversation about topic A
2. Switch to topic B
3. Reference topic A again
4. Check if the assistant remembers context

### Test 2: Personality Consistency
1. Ask the same question in different conversations
2. Compare response styles
3. Look for personality drift

### Test 3: Memory Utilization
1. Create a specific memory
2. Ask about that topic
3. Check if memory influences response

## Key Files to Examine in Detail

1. **Conversation Flow**
   - `backend/ai_partner/services/conversation_service.py`
   - `backend/ai_partner/utils/context_manager.py`
   - `backend/ai_partner/consumers.py`

2. **Prompt Engineering**
   - `backend/ai_partner/services/intelligent_prompt_service.py`
   - `backend/ai_partner/prompts/` (if directory exists)

3. **Response Generation**
   - `backend/ai_services/enhanced_ai_service.py`
   - `backend/ai_services/multi_model_service.py`

## Expected Findings

1. **Likely Issues**
   - Static system prompts without personality
   - Limited conversation history in context
   - Memory retrieval but poor integration
   - No conversation style learning

2. **Quick Fixes**
   - Increase context window
   - Improve system prompt
   - Add personality parameters
   - Better memory formatting

3. **Deeper Issues**
   - Need for conversation style learning
   - Lack of emotional context tracking
   - Missing conversational cues handling