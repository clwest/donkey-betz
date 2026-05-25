<!-- DOC-POINTER-V2 (Session 1143) -->
> **Status:** Archived
> **Originally:** see header below for original date/session.
> **Last verified:** Session 1143 (2026-05-25)
> **Change reason:** GPT-5-mini migration complete. Guide preserved as historical context for the reasoning-model adoption decision.
> **Preserved because:** white-paper corpus / historical record.

# GPT-5 Reasoning Models: The Right Way to Power AI Agents

**Created:** October 2, 2025
**Purpose:** Comprehensive guide to properly using GPT-5 reasoning models for agent intelligence
**Status:** ✅ Production Implementation Guide

---

## 🎯 Executive Summary

**THE KEY INSIGHT:** Reasoning models ARE the right choice for AI agents - we just weren't using them correctly.

**What We Were Doing Wrong:**
- ❌ Using Chat Completions API instead of Responses API
- ❌ Passing unsupported parameters (temperature, top_p, logprobs)
- ❌ Not configuring reasoning effort or verbosity
- ❌ Using max_tokens instead of max_output_tokens
- ❌ Not passing chain of thought between turns

**What We Should Be Doing:**
- ✅ Use Responses API to leverage chain of thought
- ✅ Configure reasoning.effort based on task complexity
- ✅ Set text.verbosity to control output length
- ✅ Use max_output_tokens for token limits
- ✅ Pass previous_response_id for multi-turn conversations

---

## 📚 Understanding GPT-5 Model Family

### Model Variants

| Model | Best For | Pricing (per 1M tokens) | When to Use |
|-------|----------|------------------------|-------------|
| **gpt-5** | Complex reasoning, broad world knowledge, code-heavy or multi-step agentic tasks | $1.25 input / $10.00 output | Multi-step planning, complex analysis, deep reasoning |
| **gpt-5-mini** | Cost-optimized reasoning and chat; balances speed, cost, and capability | $0.25 input / $2.00 output | Most agent tasks, general intelligence |
| **gpt-5-nano** | High-throughput tasks, simple instruction-following or classification | $0.05 input / $0.40 output | High-volume simple tasks, classification |

### System Card Names vs API Names

| System Card Name | API Name | Type |
|-----------------|----------|------|
| gpt-5-thinking | gpt-5 | Reasoning model |
| gpt-5-thinking-mini | gpt-5-mini | Reasoning model |
| gpt-5-thinking-nano | gpt-5-nano | Reasoning model |
| gpt-5-main | gpt-5-chat-latest | Non-reasoning (ChatGPT) |

**CRITICAL:** All `-thinking` variants (gpt-5, gpt-5-mini, gpt-5-nano) are reasoning models!

---

## ⚡ Responses API vs Chat Completions API

### Why Responses API is Superior for Agents

The Responses API provides **chain of thought (CoT) passing** between turns, which results in:
- 🧠 **Improved intelligence** - Model has context of its previous reasoning
- 💰 **Fewer tokens generated** - Avoids re-reasoning over same problems
- 🎯 **Higher cache hit rates** - Better prompt caching efficiency
- ⚡ **Lower latency** - Faster responses due to cached reasoning

### Key Differences

#### Chat Completions API (OLD WAY - ❌ DON'T USE)

```python
response = await client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,  # ❌ NOT SUPPORTED - Will raise error!
    max_tokens=1000,  # ❌ Wrong parameter
)
```

#### Responses API (NEW WAY - ✅ USE THIS)

```python
response = await client.responses.create(
    model="gpt-5-mini",
    input=prompt,
    reasoning={"effort": "minimal"},  # ✅ Configure reasoning
    text={"verbosity": "low"},        # ✅ Control output length
    max_output_tokens=1000,           # ✅ Correct parameter
    previous_response_id=prev_id      # ✅ Pass chain of thought
)
```

---

## 🎛️ Configuration Parameters

### Reasoning Effort

Controls how many reasoning tokens the model generates before responding.

| Value | Use Case | Latency | Quality | Best For |
|-------|----------|---------|---------|----------|
| **minimal** | Fastest responses, very few reasoning tokens | Lowest | Good | Simple tasks, instruction following, classification |
| **low** | Quick responses, some reasoning | Low | Better | Most agent tasks, standard operations |
| **medium** | Balanced reasoning | Medium | Great | Complex tasks requiring thought |
| **high** | Deep reasoning | Highest | Best | Multi-step planning, coding, complex analysis |

**Default:** `medium`

### Text Verbosity

Controls how many output tokens are generated.

| Value | Output Length | Best For |
|-------|--------------|----------|
| **low** | Concise, short answers | SQL queries, simple code, brief responses |
| **medium** | Balanced explanations | Most tasks, standard responses |
| **high** | Thorough explanations | Documentation, detailed code with comments, teaching |

**Default:** `medium`

### Max Output Tokens

- Use `max_output_tokens` (not `max_tokens`)
- Controls the maximum length of the response
- Does not include reasoning tokens in the count

---

## 🚫 Unsupported Parameters

**IMPORTANT:** These parameters will RAISE AN ERROR with GPT-5 models:

❌ `temperature` - Not supported
❌ `top_p` - Not supported
❌ `logprobs` - Not supported

**Instead use:**
- `reasoning.effort` to control response variability
- `text.verbosity` to control output length

---

## 🛠️ Agent Task Configuration Patterns

### Pattern 1: Simple Agent Tasks (Classification, Extraction)

**Use:** `gpt-5-nano` with minimal reasoning

```python
response = await client.responses.create(
    model="gpt-5-nano",
    input=f"Extract key skills from this job description: {job_text}",
    reasoning={"effort": "minimal"},
    text={"verbosity": "low"},
    max_output_tokens=500
)
```

**Why:** Fast, cheap, accurate for well-defined tasks

---

### Pattern 2: Standard Agent Operations (Most Tasks)

**Use:** `gpt-5-mini` with low reasoning

```python
response = await client.responses.create(
    model="gpt-5-mini",
    input=f"Analyze this sports data and provide betting recommendations: {data}",
    reasoning={"effort": "low"},
    text={"verbosity": "medium"},
    max_output_tokens=1000
)
```

**Why:** Balanced cost, speed, and intelligence for typical agent work

---

### Pattern 3: Complex Planning & Coding (Multi-Step Tasks)

**Use:** `gpt-5-mini` or `gpt-5` with high reasoning

```python
response = await client.responses.create(
    model="gpt-5-mini",
    input=f"Create a multi-step plan to acquire clients for this service: {service_details}",
    reasoning={"effort": "high"},
    text={"verbosity": "medium"},
    max_output_tokens=2000
)
```

**Why:** Maximum intelligence for complex tasks requiring deep thought

---

### Pattern 4: Multi-Turn Conversations (With Context)

**Use:** Pass `previous_response_id` to maintain reasoning chain

```python
# First turn
response1 = await client.responses.create(
    model="gpt-5-mini",
    input="Analyze this market data...",
    reasoning={"effort": "medium"},
)

# Second turn - with context
response2 = await client.responses.create(
    model="gpt-5-mini",
    input="Now create a trading strategy based on that analysis",
    reasoning={"effort": "high"},
    previous_response_id=response1.id  # ✅ Passes chain of thought!
)
```

**Why:** Avoids re-reasoning, maintains context, faster and cheaper

---

## 📊 Migration Guide: What Changed

### Before (Incorrect Implementation)

```python
class OpenAIProvider(LLMProvider):
    async def generate(self, prompt: str, model: str = "gpt-5-mini",
                      temperature: float = 0.7, max_tokens: int = 1000,
                      **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,  # ❌ ERROR!
            max_tokens=max_tokens,    # ❌ Wrong parameter
            **kwargs
        )
        return response.choices[0].message.content
```

**Problems:**
1. Chat Completions API doesn't pass chain of thought
2. temperature not supported for GPT-5 (will error)
3. max_tokens should be max_output_tokens
4. No reasoning or verbosity configuration
5. Can't leverage previous reasoning

---

### After (Correct Implementation)

```python
class OpenAIProvider(LLMProvider):
    async def generate(self, prompt: str, model: str = "gpt-5-mini",
                      reasoning_effort: str = "low",
                      verbosity: str = "medium",
                      max_output_tokens: int = 1000,
                      previous_response_id: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:

        response = await self.client.responses.create(
            model=model,
            input=prompt,
            reasoning={"effort": reasoning_effort},
            text={"verbosity": verbosity},
            max_output_tokens=max_output_tokens,
            previous_response_id=previous_response_id,
            **kwargs
        )

        return {
            'content': response.output_text,
            'response_id': response.id,  # For next turn
            'usage': response.usage
        }
```

**Benefits:**
1. ✅ Uses Responses API for chain of thought
2. ✅ Configures reasoning effort appropriately
3. ✅ Controls verbosity for different tasks
4. ✅ Returns response_id for multi-turn context
5. ✅ No unsupported parameters

---

## 🎯 Task-Specific Recommendations

### Content Creation Agent
```python
model="gpt-5-mini"
reasoning={"effort": "medium"}
text={"verbosity": "high"}  # Want detailed, creative content
max_output_tokens=2000
```

### Job Search Agent
```python
model="gpt-5-mini"
reasoning={"effort": "low"}
text={"verbosity": "medium"}
max_output_tokens=1000
```

### Sports Betting Analysis Agent
```python
model="gpt-5-mini"
reasoning={"effort": "medium"}  # Need good analysis
text={"verbosity": "medium"}
max_output_tokens=1500
```

### Client Acquisition Agent
```python
model="gpt-5-mini"
reasoning={"effort": "high"}  # Complex multi-step planning
text={"verbosity": "medium"}
max_output_tokens=2000
```

### Simple Classification/Tagging
```python
model="gpt-5-nano"
reasoning={"effort": "minimal"}
text={"verbosity": "low"}
max_output_tokens=200
```

---

## 💡 Best Practices

### 1. Start with Lower Reasoning, Increase as Needed
```python
# Start here for most tasks
reasoning={"effort": "low"}

# If results aren't good enough, increase
reasoning={"effort": "medium"}

# For complex problems only
reasoning={"effort": "high"}
```

### 2. Match Verbosity to Task Type
```python
# Brief outputs (classifications, tags, short answers)
text={"verbosity": "low"}

# Standard responses (analysis, recommendations)
text={"verbosity": "medium"}

# Detailed explanations (documentation, teaching)
text={"verbosity": "high"}
```

### 3. Leverage Chain of Thought for Multi-Step Tasks
```python
# Step 1: Analysis
response1 = await client.responses.create(...)

# Step 2: Action (with previous reasoning)
response2 = await client.responses.create(
    previous_response_id=response1.id  # Reuses reasoning!
)
```

### 4. Choose the Right Model for the Job
```python
# High volume, simple tasks → gpt-5-nano
# Most agent tasks → gpt-5-mini
# Complex multi-step planning → gpt-5
```

### 5. Monitor Usage and Costs
```python
# Track usage from response
usage = response.usage
cost = calculate_cost(
    usage.input_tokens,
    usage.output_tokens,
    usage.reasoning_tokens  # Don't forget reasoning tokens!
)
```

---

## 📈 Performance Comparison

### Before Fix (Chat Completions with wrong params)
- ❌ Errors due to unsupported parameters
- ❌ No reasoning configuration
- ❌ Higher latency (re-reasoning every turn)
- ❌ Higher costs (wasted tokens)
- ❌ Lower quality (no chain of thought)

### After Fix (Responses API with proper config)
- ✅ No errors, proper parameter usage
- ✅ Optimized reasoning per task type
- ✅ Lower latency (cached reasoning)
- ✅ Lower costs (efficient token usage)
- ✅ Higher quality (chain of thought maintained)

---

## 🔧 Implementation Checklist

- [ ] Update OpenAIProvider to use Responses API
- [ ] Remove unsupported parameters (temperature, top_p, logprobs)
- [ ] Add reasoning.effort configuration per task type
- [ ] Add text.verbosity configuration per task type
- [ ] Change max_tokens to max_output_tokens
- [ ] Implement previous_response_id tracking for multi-turn
- [ ] Update agent task configurations with proper settings
- [ ] Update cost calculation to include reasoning_tokens
- [ ] Test with different task types and reasoning levels
- [ ] Monitor performance and adjust configurations

---

## 📚 Additional Resources

- [OpenAI GPT-5 Official Guide](https://platform.openai.com/docs/guides/latest-model)
- [GPT-5 Prompting Best Practices](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)
- [Responses API vs Chat Completions](https://platform.openai.com/docs/guides/migrate-to-responses)
- [GPT-5 System Card](https://openai.com/index/gpt-5-system-card/)

---

## 🎉 Conclusion

**Reasoning models ARE the right choice for AI agents** when used correctly:

1. **Use Responses API** - Leverage chain of thought
2. **Configure properly** - Set reasoning.effort and text.verbosity
3. **Choose right model** - nano/mini/full based on complexity
4. **Pass context** - Use previous_response_id for multi-turn
5. **Avoid unsupported params** - No temperature, top_p, logprobs

**Result:** More intelligent agents, lower costs, better performance! 🚀
