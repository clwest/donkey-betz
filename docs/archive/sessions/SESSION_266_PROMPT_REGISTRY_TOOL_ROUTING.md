# Session 266: Central Prompt Registry + Tool Routing Fix

**Date:** November 28, 2025
**Status:** In Progress (Testing Pending)
**Focus:** Centralize all prompts + Fix tool routing issues

---

## Overview

Session 266 created a central prompt registry and fixed tool routing issues where:
1. Consultative questions incorrectly triggered `workflow_orchestration_agent`
2. Simple creation requests called wrong agents

---

## What Was Built

### 1. Central Prompt Registry (`core/prompts/`)

Created a single location for all prompts to make them easy to find and modify:

```
core/prompts/
  __init__.py          # Exports all prompts
  registry.py          # Main system prompts
  tool_descriptions.py # Tool descriptions (when to use each tool)
  agents/              # Agent-specific prompts (future)
```

#### Key Exports:
- `PERSONAL_ASSISTANT_PROMPT` - Main AI assistant system prompt
- `TOOL_DESCRIPTIONS` - Dict of tool name -> description
- `PARAM_DESCRIPTIONS` - Dict of parameter descriptions
- `get_tool_description(name)` - Helper to get a tool's description
- `get_param_description(tool, param)` - Helper to get param description

### 2. Question Detection Logic

Added question detection in `personal_ai_assistant_enhanced.py` to prevent questions from forcing tool calls:

```python
question_indicators = [
    'what style', 'which style', 'best style', 'what works best',
    'what would work', 'what should i', 'what do you recommend',
    'what colors', 'which colors', 'what fonts', 'which fonts',
    'ideas for', 'suggestions for', 'recommend for',
    'how should', 'how would', 'how do i',
    'what are trending', 'what is trending', "what's trending",
    'advice on', 'advice for', 'help me decide', 'help me choose',
]

is_question = any(q in message.lower() for q in question_indicators)

if is_question:
    is_operation = False  # Don't force tool calls for questions
```

### 3. Tool Ordering

Reordered tools in `tool_definitions.py` to prioritize common tools:

```python
return [
    _get_image_generation_agent_definition(),    # FIRST - most common
    _get_image_editing_agent_definition(),
    _get_video_generation_agent_definition(),
    _get_audio_generation_agent_definition(),
    _get_three_d_generation_agent_definition(),
    _get_video_editing_agent_definition(),
    _get_character_training_agent_definition(),
    _get_coleadership_agent_definition(),
    _get_talking_character_agent_definition(),
    _get_web_search_definition(),
    _get_create_brand_video_definition(),
    _get_create_project_from_research_definition(),
    _get_strategic_review_definition(),
    _get_workflow_orchestration_agent_definition(),  # LAST - only for packages
]
```

### 4. Enhanced Tool Descriptions

Updated `tool_descriptions.py` with clearer guidance:

**image_generation_agent:**
- Added explicit LOGOS section
- Added examples: "Create a cyberpunk logo" -> image_generation_agent
- Added DO NOT USE FOR section

**video_generation_agent:**
- Added DO NOT USE FOR LOGOS section
- Clarified it's for moving/animated content only

---

## Files Modified

| File | Changes |
|------|---------|
| `core/prompts/__init__.py` | Created - exports all prompts |
| `core/prompts/registry.py` | Created - PERSONAL_ASSISTANT_PROMPT with tool rules |
| `core/prompts/tool_descriptions.py` | Created - TOOL_DESCRIPTIONS dict |
| `core/personal_ai_assistant_enhanced.py` | Added question detection logic |
| `core/assistant/tool_definitions.py` | Reordered tools |
| `CLAUDE.md` | Added Session 266 info and Prompt Registry section |
| `00-START-NEXT-SESSION.md` | Complete handoff document |

---

## Testing Status

| Test | Expected | Status |
|------|----------|--------|
| "What style works best for a tech startup logo?" | Conversational answer | **PASSED** |
| "Create a cyberpunk logo for my tech startup" | `image_generation_agent` | **PENDING** |
| "Make 3 minimalist logos" | `image_generation_agent` | **PENDING** |
| "Research and create 3 logos" | `workflow_orchestration_agent` | **PENDING** |

---

## Technical Details

### The Problem

The `is_operation` flag in `personal_ai_assistant_enhanced.py` was matching keywords like "logo" and forcing `tool_choice: {mode: "required"}`, which meant GPT HAD to call a tool even for questions.

### The Solution

1. **Question Detection**: Check for question patterns BEFORE setting `is_operation`
2. **Tool Order**: Put `image_generation_agent` first in the list
3. **Clear Descriptions**: Make tool descriptions explicit about what each handles

### Key Insight

GPT selects tools based on:
1. Tool order (earlier = higher priority)
2. Description keyword matching
3. `tool_choice` mode (required vs auto)

---

## Next Steps (Session 267)

1. Test "Create a cyberpunk logo" - should call `image_generation_agent`
2. If still calling wrong agent, further refine `tool_descriptions.py`
3. Consider hardcoding routing for "logo" keyword if needed

---

## Architecture Diagram

```
User Message
     |
     v
EnhancedPersonalAIAssistant.process_message()
     |
     +---> is_operation? (checks for create/make/generate)
     +---> is_question? (checks for what/which/how)
     |
     v
if is_question: is_operation = False
     |
     v
if is_operation:
     +---> tool_choice: {mode: "required"}  # Forces tool call
else:
     +---> tool_choice: {mode: "auto"}      # GPT can answer without tool
     |
     v
GPT sees tool_definitions list (ORDER MATTERS!)
     |
     v
GPT picks tool based on description matching
     |
     v
Tool executed and result returned
```

---

## Lessons Learned

1. **Tool order matters** - GPT tends to prefer earlier tools
2. **Questions need special handling** - Keyword matching isn't enough
3. **Descriptions are mini-prompts** - They guide GPT's tool selection
4. **Centralized prompts are essential** - Easy to find and modify
