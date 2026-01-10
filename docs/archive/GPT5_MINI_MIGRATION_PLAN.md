# GPT-5-mini Migration Plan

**Created:** November 30, 2025
**Completed:** November 30, 2025
**Purpose:** Update all GPT-4o and GPT-4o-mini calls to use GPT-5-mini with correct parameters
**Status:** ✅ COMPLETE - All 20 locations across 12 files updated

---

## Parameter Differences

### GPT-4o / GPT-4o-mini Parameters (OLD)
```python
response = client.chat.completions.create(
    model="gpt-4o",  # or "gpt-4o-mini"
    messages=[...],
    max_tokens=2000,        # OLD parameter name
    temperature=0.7,        # Supported
)
```

### GPT-5-mini Parameters (NEW - REQUIRED)
```python
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=2000,  # NEW parameter name (replaces max_tokens)
    reasoning_effort="medium",   # NEW GPT-5 specific parameter
    # NOTE: temperature is NOT supported by GPT-5-mini
)
```

### Key Changes Required
| Old Parameter | New Parameter | Notes |
|---------------|---------------|-------|
| `max_tokens=X` | `max_completion_tokens=X` | Required rename |
| `temperature=X` | REMOVE | GPT-5-mini doesn't support temperature |
| (none) | `reasoning_effort="medium"` | Add for GPT-5 reasoning capability |

---

## Files to Update

### Priority 1: Core Agents (4 files)

#### 1. `core/agents/base_agent.py` (Line 252)
```python
# BEFORE:
response = self.client.chat.completions.create(
    model="gpt-4o",  # Use GPT-4o for best tool use
    messages=messages,
    tools=self.tools if self.tools else None,
    tool_choice="auto" if self.tools else None,
    temperature=0.7,
    max_tokens=2000,
)

# AFTER:
response = self.client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    tools=self.tools if self.tools else None,
    tool_choice="auto" if self.tools else None,
    max_completion_tokens=2000,
    reasoning_effort="medium",
)
```

#### 2. `core/agents/personal_assistant_agent.py` (Line 497)
```python
# BEFORE:
response = self.client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    max_tokens=1500,
    temperature=0.7,
)

# AFTER:
response = self.client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=1500,
    reasoning_effort="medium",
)
```

#### 3. `core/agents/business/competitor_analysis_agent.py` (Line 532)
```python
# BEFORE:
response = self.client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": swot_prompt}],
    temperature=0.7,
    max_tokens=1500,
)

# AFTER:
response = self.client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": swot_prompt}],
    max_completion_tokens=1500,
    reasoning_effort="medium",
)
```

#### 4. `core/agents/business/customer_research_agent.py` (Line 637)
```python
# BEFORE:
response = self.client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": persona_prompt}],
    temperature=0.8,
    max_tokens=1000,
)

# AFTER:
response = self.client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": persona_prompt}],
    max_completion_tokens=1000,
    reasoning_effort="medium",
)
```

---

### Priority 2: Super Platform (2 locations in 1 file)

#### 5. `core/super_platform/coordinator.py` (Lines 403 and 598)
```python
# BEFORE (both locations):
response = self.openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    max_tokens=2000,
    temperature=0.7,
)

# AFTER:
response = self.openai_client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=2000,
    reasoning_effort="medium",
)
```

---

### Priority 3: Pipelines (2 locations in 1 file)

#### 6. `pipelines/services.py` (Lines 196 and 354)
```python
# BEFORE (line 196 - image prompts):
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    temperature=0.8,
    max_tokens=1000
)

# AFTER:
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=1000,
    reasoning_effort="medium",
)

# BEFORE (line 354 - video scripts):
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    temperature=0.7,
    max_tokens=800
)

# AFTER:
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=800,
    reasoning_effort="medium",
)
```

---

### Priority 4: Vision API (Special Case)

#### 7. `core/views_image.py` (Line 7964)
```python
# BEFORE:
response = client.chat.completions.create(
    model="gpt-4o",  # GPT-4 with vision
    messages=[...],  # Contains image content
    max_tokens=500
)

# AFTER:
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],  # Contains image content
    max_completion_tokens=500,
    reasoning_effort="medium",
)
```
**NOTE:** Verify GPT-5-mini supports vision/image content before updating.

---

### Priority 5: Celery Tasks (7 locations in 1 file)

#### 8. `core/tasks.py` (Lines 3623, 3686, 4022, 4041, 4248, 4429, 4553)
All using `gpt-4o-mini` with `max_tokens` and `temperature`:

```python
# BEFORE (all 7 locations):
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    max_tokens=XXX,
    temperature=X.X
)

# AFTER (all 7 locations):
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=XXX,
    reasoning_effort="medium",
)
```

Specific locations:
- Line 3623: Agent conversation (max_tokens=150)
- Line 3686: Conversation conclusion (max_tokens=100)
- Line 4022: Dream generation (max_tokens=200)
- Line 4041: Dream title (max_tokens=20)
- Line 4248: Hive mind exploration (max_tokens=800)
- Line 4429: Hive mind contributions (max_tokens=600)
- Line 4553: Hive mind synthesis (max_tokens=1500)

---

### Priority 6: Other Files (4 files)

#### 9. `core/models_unified_system.py` (Line 8023)
```python
# BEFORE:
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=200
)

# AFTER:
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": prompt}],
    max_completion_tokens=200,
    reasoning_effort="medium",
)
```

#### 10. `core/conversation_orchestrator.py` (Line 68)
```python
# BEFORE:
def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):

# AFTER:
def __init__(self, api_key: Optional[str] = None, model: str = "gpt-5-mini"):
```
**NOTE:** Also need to update any calls within this class that use temperature/max_tokens.

#### 11. `core/settings.py` (Line 32)
```python
# BEFORE:
"openai": os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),

# AFTER:
"openai": os.getenv("OPENAI_CHAT_MODEL", "gpt-5-mini"),
```

#### 12. `style_memory/style_extractor.py` (Line 312)
```python
# BEFORE:
response = self.openai_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    temperature=0.3,
    max_tokens=200
)

# AFTER:
response = self.openai_client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=200,
    reasoning_effort="low",  # Use low for simple extraction tasks
)
```

---

## Summary

| Priority | File | Locations | Model |
|----------|------|-----------|-------|
| 1 | core/agents/base_agent.py | 1 | gpt-4o |
| 1 | core/agents/personal_assistant_agent.py | 1 | gpt-4o |
| 1 | core/agents/business/competitor_analysis_agent.py | 1 | gpt-4o |
| 1 | core/agents/business/customer_research_agent.py | 1 | gpt-4o |
| 2 | core/super_platform/coordinator.py | 2 | gpt-4o |
| 3 | pipelines/services.py | 2 | gpt-4o |
| 4 | core/views_image.py | 1 | gpt-4o (vision) |
| 5 | core/tasks.py | 7 | gpt-4o-mini |
| 6 | core/models_unified_system.py | 1 | gpt-4o-mini |
| 6 | core/conversation_orchestrator.py | 1 | gpt-4o-mini |
| 6 | core/settings.py | 1 | gpt-4o-mini |
| 6 | style_memory/style_extractor.py | 1 | gpt-4o-mini |

**Total: 20 locations across 12 files**

---

## Execution Steps

1. **Backup**: Create git branch `feature/gpt5-mini-migration`
2. **Update Priority 1**: Core agents (4 files)
3. **Update Priority 2**: Super platform (1 file, 2 locations)
4. **Update Priority 3**: Pipelines (1 file, 2 locations)
5. **Update Priority 4**: Vision API (1 file) - verify vision support first
6. **Update Priority 5**: Celery tasks (1 file, 7 locations)
7. **Update Priority 6**: Other files (4 files)
8. **Test**: Run test suite to verify all calls work
9. **Verify**: Manual testing of key features

---

## Parameter Reference (from working gpt-5-mini calls)

From `intelligence/real_agents.py`:
```python
response = self.client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ],
    max_completion_tokens=2000,
    reasoning_effort="medium"
)
```

**Valid reasoning_effort values:**
- `"low"` - For simple, quick tasks
- `"medium"` - For standard tasks (recommended default)
- `"high"` - For complex reasoning tasks
