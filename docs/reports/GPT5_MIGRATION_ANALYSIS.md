<!-- DOC-POINTER-V2 (Session 1143) -->
> **Status:** Archived
> **Originally:** see header below for original date/session.
> **Last verified:** Session 1143 (2026-05-25)
> **Change reason:** GPT-5-mini migration complete (Session 1143 Phase 4, Chris Q4=Y). PA now runs GPT-5.2 function calling per topics/personal-assistant.md.
> **Preserved because:** white-paper corpus / historical record.

# GPT-5-mini Migration Analysis
**Date:** November 18, 2025 - Session 129
**Purpose:** Comprehensive analysis of GPT-5-mini implementation requirements
**Status:** 🔍 Analysis Complete - Ready for Implementation

---

## 📊 Executive Summary

**Current State:**
- ❌ Using `gpt-4o-mini` with **Chat Completions API**
- ❌ Using unsupported parameters (`temperature`, `max_tokens`)
- ❌ Not leveraging GPT-5 reasoning capabilities
- ❌ Missing chain-of-thought passing between turns

**Target State:**
- ✅ Use `gpt-5-mini` with **Responses API**
- ✅ Proper parameters (`reasoning.effort`, `text.verbosity`, `max_output_tokens`)
- ✅ Leverage chain of thought for better intelligence
- ✅ Lower costs and faster responses

**Impact:**
- **285 total references** to GPT models across codebase
- **20+ files** need updates
- **1 CRITICAL file:** `core/llm_enforcer.py` (powers all AI operations)

---

## 🎯 Why This Matters

### The Problem with Current Implementation

**File:** `core/llm_enforcer.py` (Line 254-271)

```python
# Session 129: REVERTED to gpt-4o-mini (gpt-5-mini caused issues)
params = {
    'model': "gpt-4o-mini",  # ❌ Using old model
    'messages': [...],
    'max_tokens': max_tokens,   # ❌ Wrong parameter for GPT-5
    'temperature': temperature  # ❌ NOT SUPPORTED by GPT-5!
}

response = self.openai_client.chat.completions.create(**params)  # ❌ Wrong API!
```

**Why it "caused issues":**
1. GPT-5 models **don't support** `temperature` parameter → raises error
2. Using **Chat Completions API** instead of **Responses API** → no chain of thought
3. Using `max_tokens` instead of `max_output_tokens`
4. Missing `reasoning.effort` and `text.verbosity` configuration

**The comment says "gpt-5-mini caused issues" but the REAL issue was using it INCORRECTLY!**

---

## 📚 What the Documentation Says

**Source:** `docs/architecture/GPT5_REASONING_MODELS_GUIDE.md` (439 lines)

### Correct Implementation for GPT-5-mini:

```python
# ✅ CORRECT WAY - Responses API
response = await client.responses.create(
    model="gpt-5-mini",
    input=prompt,
    reasoning={"effort": "low"},        # NEW: Configure reasoning
    text={"verbosity": "medium"},       # NEW: Control output length
    max_output_tokens=1000,             # CHANGED: Was max_tokens
    previous_response_id=prev_id       # NEW: Chain of thought
)
```

### Key Differences:

| What's Wrong Now | What It Should Be |
|------------------|-------------------|
| `chat.completions.create()` | `responses.create()` |
| `temperature=0.7` | `reasoning={"effort": "low"}` |
| `max_tokens=500` | `max_output_tokens=500` |
| No chain of thought | `previous_response_id` for multi-turn |
| `messages=[...]` | `input=prompt` (simpler) |

### Benefits of Correct Implementation:

1. **Better Intelligence** - Chain of thought maintained across turns
2. **Lower Costs** - Avoids re-reasoning, better caching
3. **Faster Responses** - Cached reasoning reduces latency
4. **No Errors** - Proper parameter usage
5. **Configurable** - Fine-tune reasoning per task type

---

## 🔍 Codebase Analysis

### Critical Files (MUST UPDATE):

#### 1. **`core/llm_enforcer.py`** - THE MOST IMPORTANT FILE
**Lines affected:** 6 references
**Priority:** 🔴 **CRITICAL** - Powers ALL AI operations

**Current Issues:**
- Line 256: `'model': "gpt-4o-mini"` → Should be `"gpt-5-mini"`
- Line 261: `'max_tokens': max_tokens` → Should be `max_output_tokens`
- Line 262: `'temperature': temperature` → Should be `reasoning={"effort": ...}`
- Line 271: `chat.completions.create()` → Should be `responses.create()`

**Impact:** This file powers:
- Personal AI Assistant
- All agent LLM calls
- GPT function calling
- Every AI interaction in the platform

**Current API:** Chat Completions (❌ Wrong)
**Target API:** Responses API (✅ Correct)

---

#### 2. **`content/ai_providers.py`**
**Lines affected:** 15 references
**Priority:** 🟡 High - Provides AI to multiple systems

**Likely changes needed:**
- Model name updates
- API parameter updates
- May need Responses API migration

---

#### 3. **`core/views_multi_llm.py`**
**Lines affected:** 13 references
**Priority:** 🟡 High - Multi-LLM routing

---

#### 4. **`config/api_settings.py`**
**Lines affected:** 11 references
**Priority:** 🟢 Medium - Configuration defaults

---

### Agent Files (Individual Updates):

| File | References | Priority |
|------|-----------|----------|
| `agents/cto_agent.py` | 6 | 🟢 Medium |
| `agents/meeting_coordinator_agent.py` | 4 | 🟢 Medium |
| `ai_core/agents/agent_llm_integration.py` | 6 | 🟢 Medium |
| `ai_core/agents/real_work_delivery_engine.py` | 11 | 🟡 High |
| `intelligence/real_agents.py` | 9 | 🟢 Medium |

**Total Agent Files:** ~15 files
**Strategy:** Update after core migration is stable

---

## 📋 Migration Plan

### Phase 1: Core Infrastructure (CRITICAL)
**Estimated Time:** 2-3 hours
**Files:** 1 file
**Impact:** Fixes ALL AI operations

1. **Update `core/llm_enforcer.py`:**
   - [ ] Change from `chat.completions.create()` to `responses.create()`
   - [ ] Update model from `gpt-4o-mini` to `gpt-5-mini`
   - [ ] Remove `temperature` parameter
   - [ ] Add `reasoning={"effort": "low"}` (default for Personal Assistant)
   - [ ] Add `text={"verbosity": "medium"}`
   - [ ] Change `max_tokens` to `max_output_tokens`
   - [ ] Update response parsing (different structure)
   - [ ] Add support for `previous_response_id` (chain of thought)
   - [ ] Update cost calculation (include reasoning_tokens)

2. **Test Core Functionality:**
   - [ ] Test AI Assistant chat
   - [ ] Test GPT function calling
   - [ ] Test 3D conversion tool
   - [ ] Test image editing tools
   - [ ] Verify no errors with new parameters

---

### Phase 2: AI Providers & Multi-LLM (HIGH PRIORITY)
**Estimated Time:** 2-3 hours
**Files:** 3 files
**Impact:** Fixes provider abstraction layer

3. **Update `content/ai_providers.py`** (15 references)
4. **Update `core/views_multi_llm.py`** (13 references)
5. **Update `config/api_settings.py`** (11 references)

---

### Phase 3: Agent Files (MEDIUM PRIORITY)
**Estimated Time:** 2-4 hours
**Files:** ~15 files
**Impact:** Ensures all agents use correct model

6. **Update agent LLM integration files**
7. **Update individual agent files**
8. **Update management commands**

---

### Phase 4: Verification & Optimization (LOW PRIORITY)
**Estimated Time:** 1-2 hours
**Files:** All
**Impact:** Fine-tuning and optimization

9. **Tune reasoning.effort per task type:**
   - Personal Assistant: `low` (fast responses)
   - Complex analysis: `medium`
   - Multi-step planning: `high`

10. **Tune text.verbosity per use case:**
    - Tool calling: `low` (brief confirmations)
    - Explanations: `medium`
    - Documentation: `high`

11. **Implement multi-turn context:**
    - Store response IDs
    - Pass `previous_response_id` for follow-up questions

---

## 🎯 Phase 1 Implementation Details

### Current Code (llm_enforcer.py):

```python
def _call_openai(self, prompt: str, max_tokens: int, temperature: float,
                task_type: str, tools: Optional[List[Dict]] = None,
                context: str = "") -> Dict[str, Any]:

    # Build messages
    system_msg = context if context else system_messages.get(task_type, ...)
    user_message = f"{prompt}{output_instruction}"

    # ❌ WRONG: Chat Completions API with unsupported params
    params = {
        'model': "gpt-4o-mini",        # ❌ Old model
        'messages': [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_message}
        ],
        'max_tokens': max_tokens,      # ❌ Wrong parameter
        'temperature': temperature     # ❌ NOT SUPPORTED!
    }

    if tools:
        params['tools'] = tools
        params['tool_choice'] = "auto"

    response = self.openai_client.chat.completions.create(**params)

    # Parse response
    message = response.choices[0].message
    return {
        'content': message.content,
        'tool_calls': message.tool_calls if hasattr(message, 'tool_calls') else None,
        ...
    }
```

---

### Target Code (Responses API):

```python
def _call_openai(self, prompt: str, max_output_tokens: int = 1000,
                reasoning_effort: str = "low", verbosity: str = "medium",
                task_type: str = "general", tools: Optional[List[Dict]] = None,
                context: str = "", previous_response_id: Optional[str] = None
                ) -> Dict[str, Any]:

    # Build system prompt
    system_msg = context if context else system_messages.get(task_type, ...)

    # Combine system context and user prompt for input
    full_input = f"{system_msg}\n\nUser request: {prompt}"

    # ✅ CORRECT: Responses API with proper params
    params = {
        'model': "gpt-5-mini",                    # ✅ Reasoning model
        'input': full_input,                      # ✅ Combined input
        'reasoning': {"effort": reasoning_effort},  # ✅ Configurable reasoning
        'text': {"verbosity": verbosity},         # ✅ Control output length
        'max_output_tokens': max_output_tokens,   # ✅ Correct parameter
    }

    # Add chain of thought if available
    if previous_response_id:
        params['previous_response_id'] = previous_response_id

    # Tool calling with Responses API
    if tools:
        # NOTE: Responses API handles tools differently
        # May need to use different approach or wait for tool support
        # For now, focus on non-tool calls first
        pass

    response = self.openai_client.responses.create(**params)

    # Parse Responses API response (different structure)
    return {
        'content': response.output_text,          # ✅ Different field
        'response_id': response.id,               # ✅ For chain of thought
        'reasoning_tokens': response.usage.reasoning_tokens if response.usage else 0,
        'output_tokens': response.usage.output_tokens if response.usage else 0,
        'input_tokens': response.usage.input_tokens if response.usage else 0,
        'cost': self._calculate_cost_gpt5(response.usage) if response.usage else 0
    }
```

---

## ⚠️ CRITICAL BLOCKER DISCOVERED!

**Issue:** The Responses API **may not support tool calling yet!**

From the documentation search, I didn't find clear evidence that `responses.create()` supports the `tools` parameter.

**Two Options:**

### Option A: Hybrid Approach (RECOMMENDED)
- Use **Responses API** for general AI assistant chat (better intelligence)
- Use **Chat Completions API** for tool calling (known to work)
- Detect when tools are provided and route appropriately

```python
if tools:
    # Use Chat Completions for tool calling (current working method)
    return self._call_with_tools_chat_completions(...)
else:
    # Use Responses API for better intelligence
    return self._call_with_responses_api(...)
```

### Option B: Wait for Tool Support
- Keep Chat Completions API for now
- Just upgrade model from `gpt-4o-mini` to `gpt-5-mini`
- Remove `temperature` parameter
- Add reasoning/verbosity when Responses API supports tools

---

## 🎯 Recommended Immediate Action

**Given the tool calling blocker, here's what we should do NOW:**

### Step 1: Minimal GPT-5-mini Migration (Chat Completions)
**File:** `core/llm_enforcer.py`
**Changes:** 3 lines
**Time:** 10 minutes
**Risk:** Low

```python
# Line 256: Change model
'model': "gpt-5-mini",  # Was: gpt-4o-mini

# Line 262: REMOVE temperature (causes errors with GPT-5)
# temperature parameter REMOVED

# Line 261: Keep max_tokens for now (Chat Completions supports it)
# max_tokens stays the same
```

**Result:**
- ✅ Using GPT-5-mini (better model)
- ✅ No parameter errors
- ✅ Tool calling still works
- ✅ Better intelligence than gpt-4o-mini

**Downside:**
- ❌ Not using Responses API (no chain of thought)
- ❌ Can't configure reasoning.effort
- ❌ Missing some cost optimizations

---

### Step 2: Improve System Prompt (Option 2)
**File:** `core/personal_ai_assistant_enhanced.py`
**Changes:** Update system prompt to enforce tool usage
**Time:** 30 minutes
**Risk:** Low

Add to system prompt:
```
CRITICAL: When tools are available that can fulfill the user's request,
you MUST call the appropriate tool. DO NOT respond with text saying you
will do something - actually call the tool function to execute the task.

Example:
- User: "Convert image 25 to 3D"
- WRONG: "I'll convert that image to 3D for you! ✅"
- RIGHT: Call convert_to_3d(image_id="25")
```

---

## 📊 Summary of Work Required

### Immediate (Phase 1):
1. **Update `core/llm_enforcer.py`** (10 min)
   - Change model to `gpt-5-mini`
   - Remove `temperature` parameter
   - Keep Chat Completions API (tool calling works)

2. **Improve system prompt** (30 min)
   - Add explicit tool usage instructions
   - Enforce function calling over text responses

### Future (Phases 2-4):
3. **Migrate to Responses API** when tool support available
4. **Update all agent files** to use gpt-5-mini
5. **Fine-tune reasoning.effort** per task type
6. **Implement chain of thought** for multi-turn conversations

---

## 🎯 Decision Required from User

**Question:** Which approach do you want to take?

**Option A (RECOMMENDED):** Minimal migration now
- ✅ Quick (40 minutes total)
- ✅ Low risk
- ✅ Fixes immediate tool calling issue
- ✅ Gets us on GPT-5-mini
- ❌ Not using full Responses API features

**Option B:** Full Responses API migration
- ✅ Uses best practices from docs
- ✅ Chain of thought benefits
- ❌ May break tool calling
- ❌ Higher risk
- ❌ More time (4-6 hours)

**Option C:** Hybrid approach
- ✅ Best of both worlds
- ✅ Responses API for chat, Chat Completions for tools
- ❌ More complex code
- ❌ Medium time (2-3 hours)

---

**What would you like me to do?**
