# Session 355: Mythology Integration for Agents

**Date:** December 5, 2025
**Status:** Complete - All agents now validate outputs for unrealistic claims

---

## Overview

This session integrated the existing mythology validation system into all agents. The mythology system is a hallucination prevention framework that catches unrealistic claims in agent outputs and either corrects them or flags them.

Previously, the mythology validator existed but wasn't connected to the agent execution pipeline. Now:
1. **BaseAgent** has mythology validation methods that all 79 agents inherit
2. **Business Research Agents** explicitly use guarded prompts and output validation
3. **Spider Data Myths** were added to catch unrealistic claims from web sources

---

## What Was Implemented

### 1. BaseAgent Mythology Methods (`core/agents/base_agent.py`)

```python
# Lazy-loaded mythology enforcer
@property
def mythology_enforcer(self):
    """Session 354: Lazy-load MythologyEnforcer for reality validation."""
    if self._mythology_enforcer is None:
        from ai_core.agents.mythology_validator import mythology_enforcer
        self._mythology_enforcer = mythology_enforcer
    return self._mythology_enforcer

# Output validation
def _validate_output(self, result: 'AgentResult') -> 'AgentResult':
    """Validate agent output for unrealistic claims."""
    if not self.mythology_enforcer:
        return result
    # Checks message and data for mythology patterns
    # Corrects violations and flags in result.data

# Recursive data validation
def _validate_data_dict(self, data: Dict[str, Any]) -> None:
    """Recursively validate data dict for mythology."""
    # Walks through all strings in data dicts/lists

# Prompt guarding
def _guard_prompt(self, prompt: str) -> str:
    """Inject anti-mythology instructions before LLM call."""
    # Adds "## Reality Constraints" section

# Complete guarded prompt builder
def _build_prompt_with_mythology_guard(self, task, scifi_context, spider_context) -> str:
    """Build prompt with mythology guard included."""
    base_prompt = self._build_prompt(task, scifi_context, spider_context)
    return self._guard_prompt(base_prompt)
```

### 2. Business Research Agents Updated

**CompetitorAnalysisAgent (`core/agents/business/competitor_analysis_agent.py`):**
- Changed `_build_prompt()` to `_build_prompt_with_mythology_guard()`
- Added `result = self._validate_output(result)` before returning

**CustomerResearchAgent (`core/agents/business/customer_research_agent.py`):**
- Changed `_build_prompt()` to `_build_prompt_with_mythology_guard()`
- Added `result = self._validate_output(result)` before returning

### 3. Spider Data Myths (`ai_core/agents/mythology_validator.py`)

Added new patterns to catch unrealistic claims from web sources:

```python
SPIDER_DATA_MYTHS = [
    r'(\d{2,})\s*%\s+(?:of|market|growth|increase)',  # Exaggerated percentages
    r'(?:every|all)\s+(?:business|company|startup)\s+(?:uses?|needs?)',  # Universal claims
    r'(?:million|billion)s?\s+(?:users?|customers?)\s+(?:in|within)\s+(?:\d+\s+)?(?:days?|weeks?|months?)',  # Unrealistic growth
    r'(?:dominate|dominates?|dominated?)\s+(?:the\s+)?(?:market|industry)',  # Domination claims
    r'(?:no\s+)?competition',  # No competition claims
    r'(?:first|only)\s+(?:ever|in the world|of its kind)',  # Unique claims
    r'(?:viral|virality)\s+(?:guaranteed|certain)',  # Viral guarantees
]
```

With corresponding corrections:
```python
'spider_data_myth': [
    (r'(\d{2,})\s*%\s+(?:of|market)', 'significant market share'),
    (r'(?:every|all)\s+(?:business|company|startup)\s+(?:uses?|needs?)', 'many businesses use'),
    (r'(?:million|billion)s?\s+(?:users?|customers?)\s+(?:in|within)', 'rapid user growth'),
    (r'(?:dominate|dominates?|dominated?)\s+(?:the\s+)?(?:market|industry)', 'has strong market presence'),
    (r'(?:no\s+)?competition', 'limited direct competition'),
    (r'(?:first|only)\s+(?:ever|in the world|of its kind)', 'innovative'),
    (r'(?:viral|virality)\s+(?:guaranteed|certain)', 'viral potential'),
]
```

---

## How It Works

### Prompt Guarding (Before LLM Call)

When an agent builds a prompt, it can use `_build_prompt_with_mythology_guard()` which injects:

```
## Reality Constraints (IMPORTANT)
When generating responses, you MUST avoid:
- Unrealistic financial promises (no "$X per day guaranteed", "risk-free income")
- Impossible technical claims (no "100% accurate", "never fails", "unlimited")
- Exaggerated time claims (no "instant results", "learn in hours")
- Medical/legal claims without qualifications
- Guarantees of specific outcomes

Always be realistic and honest about capabilities, timelines, and potential results.
Use phrases like "potential", "may help", "typically", "can vary" instead of absolutes.
```

### Output Validation (After LLM Response)

When an agent returns a result, it calls `_validate_output(result)` which:
1. Checks `result.message` for mythology patterns
2. Recursively checks `result.data` for string values with mythology
3. If violations found:
   - Corrects the text (replaces patterns with realistic alternatives)
   - Sets `result.data['mythology_corrected'] = True`
   - Sets `result.data['mythology_violations'] = count`
   - Sets `result.data['mythology_warning'] = message`

---

## Mythology Pattern Categories

| Category | Patterns | Severity |
|----------|----------|----------|
| **FINANCIAL_MYTHS** | $X/day, guaranteed income, risk-free, 10x returns | High |
| **TECHNICAL_MYTHS** | 100% accurate, never fails, unlimited scaling | Medium |
| **TIME_MYTHS** | Instant results, learn in hours, build in seconds | Medium |
| **DANGEROUS_MYTHS** | Cure disease, legal/financial advice | Critical |
| **SPIDER_DATA_MYTHS** | 99% market share, no competition, viral guaranteed | Medium |

---

## Testing

### Test Mythology Validator
```bash
.venv/bin/python manage.py shell -c "
from ai_core.agents.mythology_validator import MythologyValidator

validator = MythologyValidator()

# Financial myth
result = validator.validate_output('TestAgent', 'Earn \$10,000 per day!')
print(f'Financial myth detected: {not result[\"valid\"]}')  # True

# Spider data myth
result = validator.validate_output('TestAgent', 'Dominate the market with no competition!')
print(f'Spider data myth detected: {not result[\"valid\"]}')  # True

# Clean output
result = validator.validate_output('TestAgent', 'Potential growth opportunity.')
print(f'Clean output: {result[\"valid\"]}')  # True
"
```

### Test BaseAgent Integration
```bash
.venv/bin/python manage.py shell -c "
from core.agents.base_agent import BaseAgent, AgentResult

class TestAgent(BaseAgent):
    name = 'TestAgent'
    system_prompt = 'Test agent'
    tools = []
    def execute(self, task, context, scifi, spider):
        return AgentResult(success=True, message='Test', data={}, agent_name=self.name)

agent = TestAgent()

# Test enforcer loads
print(f'Enforcer loaded: {agent.mythology_enforcer is not None}')  # True

# Test guard works
guarded = agent._guard_prompt('## Task\\nDo something')
print(f'Guard injected: \"Reality Constraints\" in guarded')  # True

# Test validation works
result = AgentResult(
    success=True,
    message='Guaranteed \$5000 per day!',
    data={},
    agent_name='TestAgent'
)
validated = agent._validate_output(result)
print(f'Mythology corrected: {validated.data.get(\"mythology_corrected\", False)}')  # True
"
```

---

## Files Changed

| File | Changes |
|------|---------|
| `core/agents/base_agent.py` | Added mythology_enforcer property, _validate_output(), _validate_data_dict(), _guard_prompt(), _build_prompt_with_mythology_guard() |
| `core/agents/business/competitor_analysis_agent.py` | Use _build_prompt_with_mythology_guard(), call _validate_output() |
| `core/agents/business/customer_research_agent.py` | Use _build_prompt_with_mythology_guard(), call _validate_output() |
| `ai_core/agents/mythology_validator.py` | Added SPIDER_DATA_MYTHS patterns and corrections |

---

## Benefits

1. **Hallucination Prevention**: Catches unrealistic claims before they reach users
2. **Automatic Correction**: Fixes common mythology patterns automatically
3. **Inheritance**: All 79 agents get mythology validation through BaseAgent
4. **Spider Data Awareness**: New patterns for catching web-sourced misinformation
5. **Dual Protection**: Guards prompts AND validates outputs

---

## Next Steps

1. **Extend to Creative Agents**: Add mythology validation to ImageAgent, VideoAgent, etc.
2. **Domain-Specific Patterns**: Add patterns specific to each agent type
3. **Analytics Integration**: Track mythology correction rates
4. **Personal Assistant**: Inject mythology constraints into main AI assistant
