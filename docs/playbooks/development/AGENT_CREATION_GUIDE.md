# Agent Creation Guide

**Category:** Development
**Last Updated:** January 24, 2026
**Owner:** FullStackDeveloperAgent

---

## Overview

This playbook guides you through creating a new agent for the Donkey Betz platform. All agents inherit from `BaseAgent` and integrate with the collective intelligence system.

---

## Prerequisites

- [ ] Agent purpose clearly defined
- [ ] Agent doesn't duplicate existing functionality
- [ ] Target LLM model selected
- [ ] Tools/capabilities identified
- [ ] Router category determined

---

## Agent Architecture

```
BaseAgent
├── TimeTravelMixin (state snapshots)
├── Learning hooks (collective intelligence)
├── Memory creation (agent memories)
├── Workspace integration (SKIN layer)
└── Tool execution
```

---

## Step-by-Step Guide

### Step 1: Create Agent File

**Location:** `core/agents/your_agent.py`

```python
"""
YourAgent - Brief description of what this agent does.

Session: XXX
"""

from core.agents.base_agent import BaseAgent
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class YourAgent(BaseAgent):
    """
    Detailed description of the agent's purpose and capabilities.

    Tools:
        - tool_one: Description of tool one
        - tool_two: Description of tool two

    Example:
        agent = YourAgent()
        result = await agent.execute("your task here")
    """

    def __init__(self):
        super().__init__(
            name="YourAgent",
            description="Brief description for routing",
            capabilities=[
                "capability_one",
                "capability_two",
            ],
            # Optional: specify LLM model
            # model_id="gpt-4o"
        )

        # Register tools
        self.tools = {
            'tool_one': self._tool_one,
            'tool_two': self._tool_two,
        }

    async def execute(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main execution method.

        Args:
            task: The task description
            context: Optional context dictionary

        Returns:
            Dict with execution results
        """
        context = context or {}

        try:
            # 1. Analyze task
            analysis = await self._analyze_task(task)

            # 2. Execute appropriate tool
            tool_name = analysis.get('recommended_tool', 'tool_one')
            tool_fn = self.tools.get(tool_name)

            if tool_fn:
                result = await tool_fn(task, context)
            else:
                result = await self._default_execution(task, context)

            # 3. Create memory of execution
            await self._create_execution_memory(task, result)

            return {
                'success': True,
                'output': result,
                'tool_used': tool_name,
            }

        except Exception as e:
            logger.exception(f"YourAgent execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    async def _tool_one(self, task: str, context: Dict) -> Any:
        """Implementation of tool one."""
        # Your tool logic here
        pass

    async def _tool_two(self, task: str, context: Dict) -> Any:
        """Implementation of tool two."""
        # Your tool logic here
        pass

    async def _analyze_task(self, task: str) -> Dict[str, Any]:
        """Analyze task to determine best approach."""
        # Use LLM to analyze task
        response = await self._call_llm(
            f"Analyze this task and recommend which tool to use: {task}"
        )
        return {'recommended_tool': 'tool_one'}  # Parse response

    async def _create_execution_memory(self, task: str, result: Any) -> None:
        """Create memory of this execution for learning."""
        # Memory creation logic inherited from BaseAgent
        pass
```

### Step 2: Register in Agent Router

**File:** `core/agent_router.py`

```python
# Add import
from core.agents.your_agent import YourAgent

# Add to AGENT_DEFINITIONS
AGENT_DEFINITIONS = {
    # ... existing agents ...

    'YourAgent': {
        'class': YourAgent,
        'category': 'your_category',
        'keywords': ['keyword1', 'keyword2', 'keyword3'],
        'description': 'Brief description for routing',
    },
}
```

### Step 3: Create Database Entry

```bash
python manage.py shell
```

```python
from core.models_unified_system import Agent

Agent.objects.create(
    name='YourAgent',
    slug='your-agent',
    agent_type='your_category',
    description='Full description',
    is_active=True,
    capabilities=['capability_one', 'capability_two'],
)
```

### Step 4: Configure LLM Routing

**File:** `core/models_llm_routing.py`

```python
# Add configuration
AgentModelConfig.objects.create(
    agent_name='YourAgent',
    model_id='gpt-4o',  # or appropriate model
    temperature=0.7,
    max_tokens=4000,
    priority=1,
    is_active=True,
)
```

### Step 5: Add Tool Definitions (if PA integration)

**File:** `core/assistant/tool_definitions.py`

```python
# Add tool schema
YOUR_AGENT_TOOL = {
    "type": "function",
    "function": {
        "name": "your_agent_task",
        "description": "What this tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task to execute"
                }
            },
            "required": ["task"]
        }
    }
}
```

---

## Testing Your Agent

### Unit Tests

**File:** `tests/test_your_agent.py`

```python
import pytest
from core.agents.your_agent import YourAgent


@pytest.mark.asyncio
async def test_agent_initialization():
    agent = YourAgent()
    assert agent.name == 'YourAgent'
    assert len(agent.tools) >= 1


@pytest.mark.asyncio
async def test_agent_execution():
    agent = YourAgent()
    result = await agent.execute("test task")
    assert 'success' in result
```

### Manual Testing

```bash
python manage.py shell
```

```python
import asyncio
from core.agents.your_agent import YourAgent

agent = YourAgent()
result = asyncio.run(agent.execute("your test task"))
print(result)
```

---

## Checklist

### Code Quality
- [ ] Inherits from BaseAgent
- [ ] Has docstrings for class and methods
- [ ] Includes type hints
- [ ] Has proper error handling
- [ ] Logs important events

### Integration
- [ ] Registered in agent_router.py
- [ ] Database entry created
- [ ] LLM config created
- [ ] Tool definitions added (if needed)

### Testing
- [ ] Unit tests pass
- [ ] Manual testing completed
- [ ] Integration test with PA works

### Documentation
- [ ] Agent documented in AGENTS.md
- [ ] Tools documented
- [ ] Example usage provided

---

## Common Patterns

### LLM Call Pattern
```python
response = await self._call_llm(
    prompt,
    system_message="You are a helpful assistant...",
    temperature=0.7,
    max_tokens=2000,
)
```

### Workspace Write Pattern
```python
from core.services.skin import SkinService

skin = SkinService()
result = await skin.write_file(
    workspace_id=workspace_id,
    file_path="path/to/file.py",
    content="file content",
    agent_name=self.name,
    description="What was written",
)
```

### Memory Creation Pattern
```python
from core.models import AgentMemory

AgentMemory.objects.create(
    agent_name=self.name,
    memory_type='execution',
    content=f"Executed: {task}",
    importance=0.7,
    safety_class='candidate',
)
```

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-24 | 1.0 | Initial playbook |
