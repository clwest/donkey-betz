# Detailed Investigation: Agent-Prompt Task Mismatch

## Problem Statement
Agents are focused on their tasks but the actual execution doesn't match the user's prompt/intent. There's a disconnect between what users ask for and what agents deliver.

## Investigation Steps

### Step 1: Agent Prompt Analysis
**Objective**: Understand how user prompts are interpreted

1. **Initial Prompt Reception**
   ```
   File: backend/agent_orchestra/api.py
   Endpoint: /api/agent-orchestra/deploy/
   
   Trace:
   - How is the user's prompt received?
   - What preprocessing occurs?
   - Is the prompt modified before agent selection?
   ```

2. **Agent Selection Logic**
   ```
   File: backend/agent_orchestra/services/orchestration_service.py
   Method: select_agent() or determine_agent()
   
   Questions:
   - How is the appropriate agent chosen?
   - Is it keyword-based or AI-based?
   - Can multiple agents be selected?
   ```

### Step 2: Agent System Prompts
**Objective**: Analyze each agent's instructions

1. **Extract All Agent System Prompts**
   ```
   For each agent in backend/agent_orchestra/agents/:
   - business_strategy_agent.py
   - market_research_agent.py
   - technical_implementation_agent.py
   etc.
   
   Look for:
   - SYSTEM_PROMPT constant
   - get_system_prompt() method
   - prompt templates
   ```

2. **Prompt Rigidity Analysis**
   ```
   Questions per agent:
   - How specific are the instructions?
   - Is there flexibility for user intent?
   - Are agents over-constrained?
   ```

### Step 3: User Prompt Integration

1. **Prompt Combination Logic**
   ```
   File: backend/agent_orchestra/services/prompt_engineering.py
   Or search for: "combine_prompts", "merge_prompts"
   
   Investigate:
   - How is user prompt merged with system prompt?
   - Is user intent preserved?
   - What's the prompt hierarchy?
   ```

2. **Context Loss Points**
   ```
   Trace the prompt through:
   1. API endpoint reception
   2. Orchestration service
   3. Agent factory
   4. Individual agent
   5. Tool executor
   
   Where does the original intent get lost?
   ```

### Step 4: Tool Parameter Mapping

1. **Tool Selection**
   ```
   File: backend/agent_orchestra/services/tool_service.py
   
   Questions:
   - How do agents choose tools?
   - Is tool selection flexible?
   - Are tools hardcoded per agent?
   ```

2. **Parameter Extraction**
   ```
   File: backend/agent_orchestra/utils/tool_mapper.py
   
   Investigate:
   - How are parameters extracted from prompts?
   - What happens with ambiguous parameters?
   - Error handling for missing params?
   ```

### Step 5: Execution Pattern Analysis

1. **Sync Executor Deep Dive**
   ```
   File: backend/agent_orchestra/services/enhanced_sync_executor.py
   
   Key methods:
   - execute()
   - execute_tool()
   - process_tool_result()
   
   Questions:
   - Is there prompt reinterpretation?
   - How are tool results used?
   - Can agents adapt mid-execution?
   ```

2. **Agent Decision Trees**
   ```
   For each agent, map:
   - Input types accepted
   - Decision points
   - Output formats
   - Hardcoded behaviors
   ```

## Specific Investigation Queries

### Query 1: Find All Agent Prompts
```bash
# Find system prompts
find backend/agent_orchestra/agents -name "*.py" -exec grep -l "SYSTEM_PROMPT\|system_prompt" {} \;

# Extract prompt content
for file in backend/agent_orchestra/agents/*.py; do
    echo "=== $file ==="
    grep -A 20 "SYSTEM_PROMPT\|get_system_prompt" "$file"
done
```

### Query 2: Trace Prompt Flow
```python
# Add logging to trace prompt transformation
# In orchestration_service.py
import logging
logger = logging.getLogger(__name__)

def process_request(self, user_prompt):
    logger.info(f"Original prompt: {user_prompt}")
    # ... existing code ...
    logger.info(f"Modified prompt: {modified_prompt}")
    logger.info(f"Selected agent: {agent_name}")
```

### Query 3: Agent Flexibility Analysis
```bash
# Search for conditional logic in agents
grep -r "if.*prompt\|if.*user\|if.*request" backend/agent_orchestra/agents/ --include="*.py"

# Find adaptability patterns
grep -r "adapt\|adjust\|modify.*behavior" backend/agent_orchestra/ --include="*.py"
```

## Test Scenarios

### Test 1: Ambiguous Requests
```
User: "Help me with my business"
Expected: Clarification questions
Actual: [Document what happens]

User: "Analyze the market"
Expected: "Which market?"
Actual: [Document what happens]
```

### Test 2: Multi-Intent Requests
```
User: "Create a business plan and analyze competitors"
Expected: Multiple agents collaborate
Actual: [Document what happens]
```

### Test 3: Out-of-Scope Requests
```
User: "Write me a poem"
To Business Strategy Agent
Expected: Graceful redirect or decline
Actual: [Document what happens]
```

## Common Mismatch Patterns

### Pattern 1: Over-Specific Agents
```
Symptom: Agent ignores user nuance
Cause: System prompt too restrictive
Example: Market Research Agent only researches pre-defined markets
```

### Pattern 2: Parameter Assumptions
```
Symptom: Agent uses default values instead of asking
Cause: Missing parameter validation
Example: Financial Agent assumes USD currency
```

### Pattern 3: Template Rigidity
```
Symptom: All outputs follow exact same structure
Cause: Hardcoded output templates
Example: Business plans always have 10 sections
```

## Key Files for Deep Analysis

1. **Orchestration Logic**
   - `backend/agent_orchestra/services/orchestration_service.py`
   - `backend/agent_orchestra/services/agent_selector.py`

2. **Agent Definitions**
   - All files in `backend/agent_orchestra/agents/`
   - Focus on `get_system_prompt()` methods

3. **Execution Flow**
   - `backend/agent_orchestra/services/enhanced_sync_executor.py`
   - `backend/agent_orchestra/services/enhanced_agent_service.py`

## Improvement Recommendations

### Quick Fixes
1. Add prompt flexibility instructions to each agent
2. Implement clarification questions for ambiguous requests
3. Add user intent preservation in prompt engineering

### Medium-term Fixes
1. Implement dynamic agent selection based on AI analysis
2. Add prompt adaptation based on conversation context
3. Create feedback loop for agent responses

### Long-term Solutions
1. Implement learning from user corrections
2. Create adaptive agent behaviors
3. Build intent recognition system