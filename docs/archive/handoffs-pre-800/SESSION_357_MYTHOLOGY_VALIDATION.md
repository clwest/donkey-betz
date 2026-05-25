# Session 357: Mythology Validation + Learning Cycle Fix

**Date:** December 5, 2025
**Status:** COMPLETE - Mythology validated + Learning cycle fixed

---

## Summary

1. Added mythology validation to prevent agents from hallucinating unrealistic claims when communicating with each other
2. Fixed Live Agent Learning Activity not updating - expanded knowledge types and improved duplicate detection

---

## What Was Done

### 1. Agent Conversations - Mythology Validation Added
**File:** `core/tasks.py` (line 3875-3877)
**Task:** `run_agent_conversation`

```python
content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

# Session 356: Validate output for mythology violations
# Prevents agents from hallucinating unrealistic claims to each other
content = validate_agent_output(current_speaker.name, content)
```

### 2. Agent Dreams - Intentionally NOT Validated
**File:** `core/tasks.py` (line 4679-4682)
**Task:** `generate_agent_dreams`

```python
# Session 356 NOTE: Dreams are intentionally NOT mythology-validated
# Dreams are meant to be creative, imaginative, and speculative
# (what-if scenarios, predictions, wild thoughts, mashups)
# Mythology validation would restrict their creative nature
```

### 3. Hive Mind Sessions - Already Validated (Session 356)
**File:** `core/tasks.py` (line ~5085)
**Task:** `run_hive_mind_session`

Mythology validation was added in Session 356 for Hive Mind contributions.

---

## Mythology Validation Coverage

| Feature | Validated? | Reason |
|---------|------------|--------|
| **Hive Mind** | Yes | Problem-solving should be grounded in reality |
| **Conversations** | Yes | Agent discussions should be factual |
| **Dreams** | No | Intentionally creative/imaginative/speculative |

---

## Helper Function

The `validate_agent_output()` function at line 21 of `core/tasks.py`:

```python
def validate_agent_output(agent_name: str, output: str) -> str:
    """
    Session 356: Validate and correct agent output for mythology violations.

    This ensures agents don't hallucinate unrealistic claims when communicating
    with each other (Hive Mind, Conversations, Dreams).

    Args:
        agent_name: Name of the agent producing the output
        output: The LLM-generated output to validate

    Returns:
        Corrected output (or original if no violations)
    """
    try:
        from ai_core.agents.mythology_validator import mythology_enforcer
        result = mythology_enforcer.enforce(agent_name, output)

        if result.get('mythology_corrected'):
            logger.warning(f"[MYTHOLOGY] {agent_name} output corrected: {result.get('violations', 0)} violations")
            return result.get('result', output)

        return output
    except Exception as e:
        logger.warning(f"[MYTHOLOGY] Validation failed for {agent_name}: {e}")
        return output  # Return original if validation fails
```

---

## Why Dreams Are Exempt

Dreams have specific dream types that are inherently speculative:
- `creative_idea` - Novel concepts and innovations
- `what_if` - Hypothetical scenarios
- `mashup` - Cross-domain combinations
- `prediction` - Future trend predictions
- `improvement` - Enhancement ideas
- `observation` - Pattern recognition
- `wild_thought` - Unconventional ideas

Applying mythology validation would suppress the creative, imaginative nature of these outputs - defeating their purpose.

---

## Files Changed

| File | Changes |
|------|---------|
| `core/tasks.py` | Mythology validation in `run_agent_conversation`, exemption in `generate_agent_dreams`, expanded knowledge types, improved duplicate detection |
| `ai_core/templates/ai_image_studio.html` | Fixed duplicate "Total Agents" cards - changed second to "Hive Sessions" |

---

## Phase 2: Learning Cycle Fix

### Problem
Live Agent Learning Activity was not updating - last activity shown was 10+ hours ago despite the learning cycle running.

### Root Causes
1. **Restrictive knowledge types**: Only 2-3 types per connection (out of 10+ available)
2. **Crude duplicate detection**: Used 30-char prefix matching which blocked too many transfers

### Fixes Applied

#### 1. Expanded Default Knowledge Types
**File:** `core/tasks.py` (line 2883-2891)

From 3 types to 10:
- `trend`, `opportunity`, `market`, `user_behavior`, `content_idea`
- `tool_discovery`, `pricing`, `research`, `insight`, `strategy`

#### 2. Improved Duplicate Detection
**File:** `core/tasks.py` (line 2893-2910)

- Full title matching instead of 30-char prefix
- Strips `[Learned]` prefixes before comparing
- Uses exact match OR `[Learned]` version match

#### 3. Updated All 37 Connections
All `AgentLearningConnection` records updated to share all 10 knowledge types.

### Result
- 12+ new knowledge transfers generated in testing
- Learning activity now shows fresh data

---

## Testing

To verify mythology validation is working:

1. **Check logs for mythology corrections:**
```bash
grep -i "mythology" celery.log | tail -20
```

2. **Trigger a conversation:**
```bash
curl -X POST http://localhost:8000/api/agent-conversations/trigger/
```

3. **Trigger a Hive Mind session:**
```bash
curl -X POST http://localhost:8000/api/hive-mind/sessions/trigger/
```

---

## Related Sessions

- **Session 355:** Mythology integration for agents
- **Session 356:** Agents Tab complete, Hive Mind mythology validation added
- **Session 357:** Conversations mythology validation, Dreams exemption

---

## Next Steps

1. Monitor logs for mythology corrections in production
2. Consider adding metrics for correction frequency
3. Review if any other agent-to-agent paths need validation
