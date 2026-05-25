# Session 315: Agent Conversations Fix + Live System Stats

**Date:** December 2, 2025
**Focus:** Fix empty Agent Conversations + inject real-time system statistics

---

## Problems Solved

### 1. Empty Conversation Content
Agent Conversations were completing with proper structure but **empty message content**:
```javascript
messages: [
  { agent: "ContentExecutor", content: "", sequence: 1 },
  { agent: "CustomerResearchAgent", content: "", sequence: 2 },
  // ... all empty
]
```

### 2. Rate Limiter Crash
Health check was crashing with:
```
AttributeError: 'RedisCache' object has no attribute 'ttl'
```

### 3. Inaccurate System References
Agents were referencing placeholder numbers ("70 spiders", "22 agents") instead of actual system state.

---

## Root Causes

### 1. Wrong API + Low Token Limit
`conversation_orchestrator.py` was using:
```python
# BROKEN - chat.completions with Responses API params
response = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": prompt}],
    max_completion_tokens=250,  # Too low!
    reasoning_effort="medium",  # Wrong API!
)
content = response.choices[0].message.content
```

**Problem:** GPT-5 reasoning models allocate `max_output_tokens` for BOTH reasoning tokens AND text output. With only 250 tokens, all were consumed by internal reasoning, leaving nothing for visible text.

### 2. Django Cache API
Django's `RedisCache` doesn't have a `.ttl()` method - that's a Redis-specific method.

### 3. No Live System Data
Prompts had no access to actual database counts.

---

## Solutions Implemented

### 1. GPT-5 Responses API Migration
```python
# FIXED - Proper Responses API with adequate tokens
response = self.client.responses.create(
    model=self.model,
    input=prompt,
    reasoning={"effort": "medium"},
    text={"verbosity": "medium"},
    max_output_tokens=1000,  # Normal turns
    # max_output_tokens=2000 for final turn with DecisionSummary
)
content = response.output_text.strip() if response.output_text else ""
```

### 2. Rate Limiter Fix
```python
# Before: cache.ttl(cache_key) - crashes
# After: Use fixed 60 second default
ttl = 60
```

### 3. Live System Stats Injection (Session 315 Feature!)
Added `_get_live_system_stats()` and `_format_system_context()` methods that query:
- Spider count from `SpiderRegistry`
- Agent count from `Agent.objects`
- Memory count from `AgentMemory.objects`
- Knowledge sources from `AgentKnowledgeSource.objects`
- Spider data records from `SpiderData.objects`
- Opportunities, A/B tests, conversations, learning events

Agents now receive this context in every prompt:
```
=== LIVE PLATFORM STATISTICS (Real-Time Data) ===
• Spider Network: 74 active spiders across 20 categories
• Agent Ecosystem: 36 active agents (196 total)
• Memory Palace: 48 memories stored
• Knowledge Base: 44 knowledge sources
• Spider Data: 1,234 total records (56 in last 24h)
• Opportunities Tracked: 15
• A/B Tests: 3
• Agent Conversations: 12
• Learning Events: 89

USE THESE EXACT NUMBERS when discussing platform capabilities.
===================================================
```

---

## Files Modified

| File | Changes |
|------|---------|
| `core/conversation_orchestrator.py` | GPT-5 Responses API, higher token limits, live stats injection |
| `core/rate_limiter.py` | Fixed `cache.ttl()` to use fixed 60s default |

---

## Technical Details

### Token Allocation for Reasoning Models
GPT-5 reasoning models (gpt-5, gpt-5-mini, gpt-5-nano) use `max_output_tokens` differently:
- **Standard models:** All tokens go to visible output
- **Reasoning models:** Tokens split between internal reasoning + visible output

**Solution:** Set higher limits (1000-2000) to ensure room for both.

### Responses API Parameters
```python
response = client.responses.create(
    model="gpt-5-mini",
    input=prompt,                      # Not "messages"
    reasoning={"effort": "medium"},    # minimal/low/medium/high
    text={"verbosity": "medium"},      # low/medium/high
    max_output_tokens=1000,            # Not "max_tokens"
)
result = response.output_text          # Not response.choices[0].message.content
```

---

## Demo Impact

Agent Conversations are now **incredible for demos**:
1. Real content with substantive discussion
2. Constructive tension between agents
3. **Accurate system statistics** - agents discuss the ACTUAL infrastructure
4. DecisionSummary with actionable insights

Example conversation excerpt:
> "With our 74 spiders feeding data across 20 categories and 36 active agents processing insights, the bottleneck appears to be..."

---

## Testing

```bash
# Start servers
make start && make celery

# Access Agent Conversations
open http://localhost:8000/ai-studio/
# Navigate to Agents > Social > Start Conversation
```

---

## Related Documentation

- `docs/architecture/GPT5_REASONING_MODELS_GUIDE.md` - Full API reference
- `docs/handoffs/SESSION_314_GPT5_API_MIGRATION.md` - Previous migration work

---

## Summary

Session 315 fixed Agent Conversations from showing empty content to generating substantive, platform-grounded discussions with **real-time system statistics**. Agents now reference actual spider counts (74), agent counts (36), memory counts, and other live metrics instead of placeholders.
