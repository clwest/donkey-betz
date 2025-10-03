# 🚀 START HERE - Session 27: GPT-5 Agent Migration

**Mission:** Migrate all agents to proper GPT-5 Responses API configuration
**Status:** Core infrastructure complete ✅, ready to implement across agents
**Time Estimate:** 2-3 hours

---

## ⚡ Quick Start (5 minutes)

### 1. Read the Handoff Letter
📖 **`docs/letters/LETTER_TO_FUTURE_CLAUDE_SESSION_27.md`**

This has EVERYTHING you need including:
- What Session 26 accomplished
- Exact steps to follow
- Configuration patterns for each agent type
- Common pitfalls to avoid

### 2. Understand What Changed

**Session 26 discovered:** Reasoning models ARE perfect for agents - we just weren't using them correctly!

**The Fix:**
- ❌ **Before:** Chat Completions API with unsupported parameters (errors!)
- ✅ **After:** Responses API with proper reasoning configuration (works!)

### 3. Your Mission

**Migrate agents from incorrect Chat Completions to proper Responses API usage.**

---

## 📋 Step-by-Step Plan

### Phase 1: Validate Test Script (5 min)
```bash
# Run this first to confirm everything works
python scripts/test_gpt5_reasoning.py

# You should see:
# ✅ All 4 tests pass
# ✅ Real AI responses
# ✅ No errors
# ✅ Cost tracking working
```

### Phase 2: Update Key Agents (1 hour)

**Priority Order:**

1. **ContentCreator** (`ai_core/agents/real_content_creator.py`)
   - Lines to update: 62, 136, 202
   - Config: `gpt-5-mini`, `reasoning_effort="medium"`, `verbosity="high"`

2. **JobExecutor** (`ai_core/agents/real_job_executor.py`)
   - Lines to update: 119, 183, 262, 331, 391
   - Config: `gpt-5-mini`, `reasoning_effort="low"`, `verbosity="medium"`

3. **ProposalEngine** (`ai_core/agents/ai_proposal_engine.py`)
   - Lines to update: 184, 337, 436
   - Config: `gpt-5-mini`, `reasoning_effort="high"`, `verbosity="medium"`

### Phase 3: Update Remaining Agents (1 hour)

- [ ] `real_work_delivery_engine.py` (11 calls)
- [ ] `job_application_orchestrator.py` (1 call)
- [ ] `real_client_acquisition.py` (1 call)
- [ ] `automated_job_bot.py` (check if needed)

### Phase 4: Test & Validate (30 min)

```bash
# Test each updated agent
python scripts/test_agent_execution.py ContentCreator
python scripts/test_agent_execution.py JobExecutor
python scripts/test_agent_execution.py ProposalEngine
```

---

## 🔧 Migration Pattern

### Find OpenAI Calls
```bash
grep -r "chat.completions.create" ai_core/agents/
```

### Replace Pattern

**OLD CODE (❌ Remove this):**
```python
from openai import AsyncOpenAI
client = AsyncOpenAI()

response = await client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": my_prompt}],
    temperature=0.7,  # Error!
    max_tokens=1000
)
result = response.choices[0].message.content
```

**NEW CODE (✅ Use this):**
```python
from ai_core.agents.agent_llm_integration import agent_llm_integration

result = await agent_llm_integration.generate_for_agent(
    agent_name="YourAgentName",
    prompt=my_prompt,
    model="gpt-5-mini",           # nano/mini/full
    reasoning_effort="low",        # minimal/low/medium/high
    verbosity="medium",            # low/medium/high
    max_output_tokens=1000
)

if result['success']:
    response_text = result['response']
else:
    logger.error(f"LLM error: {result.get('error')}")
```

---

## 🎯 Configuration Quick Reference

| Agent Type | Model | Reasoning | Verbosity | Max Tokens |
|-----------|-------|-----------|-----------|------------|
| Content Creation | gpt-5-mini | medium | high | 2000 |
| Job Search | gpt-5-mini | low | medium | 1000 |
| Sports Analysis | gpt-5-mini | medium | medium | 1500 |
| Client Acquisition | gpt-5-mini | high | medium | 2000 |
| Proposals | gpt-5-mini | high | medium | 2000 |
| Trading | gpt-5-mini | medium | low | 800 |
| Classification | gpt-5-nano | minimal | low | 200 |

**Full details:** `docs/architecture/GPT5_AGENT_CONFIGURATION_PATTERNS.md`

---

## 📚 Documentation Available

All the information you need:

1. **Technical Guide:** `docs/architecture/GPT5_REASONING_MODELS_GUIDE.md`
2. **Config Patterns:** `docs/architecture/GPT5_AGENT_CONFIGURATION_PATTERNS.md`
3. **Handoff Letter:** `docs/letters/LETTER_TO_FUTURE_CLAUDE_SESSION_27.md`
4. **Test Script:** `scripts/test_gpt5_reasoning.py`

---

## ✅ Success Criteria

By session end, you should have:

- [ ] All agents using Responses API (no Chat Completions)
- [ ] No "unsupported parameter" errors
- [ ] Real AI responses from all agents
- [ ] Accurate cost tracking
- [ ] All tests passing

---

## 🚨 Common Pitfalls

1. **Don't mix old and new** - Fully migrate each agent
2. **Check response format** - Dict not string now
3. **Handle errors** - Always check `result['success']`
4. **Import correctly** - Use `agent_llm_integration`

---

## 💡 Pro Tip

**Start here:** `ai_core/agents/real_content_creator.py` line 62

**Reference:** `docs/architecture/GPT5_AGENT_CONFIGURATION_PATTERNS.md` (has all the patterns!)

---

## 🎉 What You're Implementing

A properly architected GPT-5 reasoning system that:
- Uses Responses API correctly
- Configures reasoning per task complexity
- Tracks costs accurately
- Supports chain of thought
- Produces intelligent AI responses

**The hard work is done - now just migrate the agents!** 🚀

---

**Next Step:** Open `docs/letters/LETTER_TO_FUTURE_CLAUDE_SESSION_27.md` and read the full handoff.
