<!-- DOC-POINTER-V2 (Session 1143) -->
> **Status:** Archived
> **Originally:** see header below for original date/session.
> **Last verified:** Session 1143 (2026-05-25)
> **Change reason:** GPT-5-mini migration complete. Configuration patterns may have shifted; refer to current code in core/agents/.
> **Preserved because:** white-paper corpus / historical record.

# GPT-5 Agent Configuration Patterns

**Purpose:** Quick reference for configuring each agent type with optimal GPT-5 reasoning settings
**Date:** October 2, 2025

---

## 🎯 Configuration Format

```python
result = await agent_llm_integration.generate_for_agent(
    agent_name="AgentName",
    prompt="Your prompt here",
    model="gpt-5-mini",              # gpt-5, gpt-5-mini, or gpt-5-nano
    reasoning_effort="low",          # minimal, low, medium, high
    verbosity="medium",              # low, medium, high
    max_output_tokens=1000,
    previous_response_id=None        # For multi-turn conversations
)
```

---

## 📋 Agent Type Configurations

### 1. Content Creation Agents

**Examples:** Blog Writer, Social Media Creator, Video Script Generator

```python
# Configuration
model = "gpt-5-mini"
reasoning_effort = "medium"     # Need creativity and structure
verbosity = "high"              # Want detailed, rich content
max_output_tokens = 2000        # Longer outputs for content

# Use case: Generate blog post
result = await agent_llm_integration.generate_for_agent(
    agent_name="ContentCreator",
    prompt=f"Write a comprehensive blog post about {topic}",
    model=model,
    reasoning_effort=reasoning_effort,
    verbosity=verbosity,
    max_output_tokens=max_output_tokens
)
```

**Why:** Creative content benefits from medium reasoning to structure ideas well, and high verbosity for detailed output.

---

### 2. Job Search & Application Agents

**Examples:** Job Finder, Resume Tailor, Application Tracker

```python
# Configuration
model = "gpt-5-mini"
reasoning_effort = "low"        # Straightforward matching tasks
verbosity = "medium"            # Clear, concise responses
max_output_tokens = 1000

# Use case: Analyze job fit
result = await agent_llm_integration.generate_for_agent(
    agent_name="JobSearchAgent",
    prompt=f"Analyze job fit for: {job_description}\nUser skills: {skills}",
    model=model,
    reasoning_effort=reasoning_effort,
    verbosity=verbosity,
    max_output_tokens=max_output_tokens
)
```

**Why:** Job matching is relatively straightforward - low reasoning is sufficient, medium verbosity gives clear explanations.

---

### 3. Sports Betting Analysis Agents

**Examples:** Odds Analyzer, Bet Recommender, Performance Predictor

```python
# Configuration
model = "gpt-5-mini"
reasoning_effort = "medium"     # Need analytical thinking
verbosity = "medium"            # Clear analysis with reasoning
max_output_tokens = 1500

# Use case: Analyze betting opportunity
result = await agent_llm_integration.generate_for_agent(
    agent_name="BettingAnalyzer",
    prompt=f"Analyze this matchup and recommend bets: {game_data}",
    model=model,
    reasoning_effort=reasoning_effort,
    verbosity=verbosity,
    max_output_tokens=max_output_tokens
)
```

**Why:** Sports analysis requires moderate reasoning to evaluate stats and trends, medium verbosity for clear recommendations.

---

### 4. Client Acquisition & Proposal Agents

**Examples:** Lead Generator, Proposal Writer, Outreach Specialist

```python
# Configuration
model = "gpt-5-mini"
reasoning_effort = "high"       # Complex multi-step planning
verbosity = "medium"            # Professional, concise communication
max_output_tokens = 2000

# Use case: Generate client acquisition strategy
result = await agent_llm_integration.generate_for_agent(
    agent_name="ClientAcquisition",
    prompt=f"Create acquisition strategy for: {service_details}",
    model=model,
    reasoning_effort=reasoning_effort,
    verbosity=verbosity,
    max_output_tokens=max_output_tokens
)
```

**Why:** Client acquisition requires deep strategic thinking (high reasoning) with professional output (medium verbosity).

---

### 5. Trading & Market Analysis Agents

**Examples:** Crypto Analyzer, Stock Predictor, Signal Generator

```python
# Configuration
model = "gpt-5-mini"
reasoning_effort = "medium"     # Analytical market assessment
verbosity = "low"               # Concise signals and recommendations
max_output_tokens = 800

# Use case: Generate trading signals
result = await agent_llm_integration.generate_for_agent(
    agent_name="TradingAgent",
    prompt=f"Analyze market data and generate signals: {market_data}",
    model=model,
    reasoning_effort=reasoning_effort,
    verbosity=verbosity,
    max_output_tokens=max_output_tokens
)
```

**Why:** Trading needs solid analysis (medium reasoning) but brief, actionable signals (low verbosity).

---

### 6. Classification & Tagging Agents

**Examples:** Category Classifier, Sentiment Analyzer, Tag Generator

```python
# Configuration
model = "gpt-5-nano"           # Cost-effective for simple tasks
reasoning_effort = "minimal"    # Very straightforward classification
verbosity = "low"              # Just the tags/categories
max_output_tokens = 200

# Use case: Classify content
result = await agent_llm_integration.generate_for_agent(
    agent_name="ContentClassifier",
    prompt=f"Classify this content into categories: {content}",
    model=model,
    reasoning_effort=reasoning_effort,
    verbosity=verbosity,
    max_output_tokens=max_output_tokens
)
```

**Why:** Simple classification tasks benefit from nano model for cost savings, minimal reasoning for speed, low verbosity for brief output.

---

### 7. Data Analysis & Insights Agents

**Examples:** Pattern Detector, Trend Analyzer, Insight Generator

```python
# Configuration
model = "gpt-5-mini"
reasoning_effort = "medium"     # Need analytical reasoning
verbosity = "medium"            # Clear insights with context
max_output_tokens = 1500

# Use case: Analyze spider data
result = await agent_llm_integration.generate_for_agent(
    agent_name="DataAnalyzer",
    prompt=f"Analyze patterns in this data: {spider_data}",
    model=model,
    reasoning_effort=reasoning_effort,
    verbosity=verbosity,
    max_output_tokens=max_output_tokens
)
```

**Why:** Data analysis requires moderate reasoning to identify patterns, medium verbosity for explanatory insights.

---

### 8. Code Generation & Debugging Agents

**Examples:** Code Generator, Bug Fixer, Refactoring Assistant

```python
# Configuration
model = "gpt-5"                # Best model for complex coding
reasoning_effort = "high"       # Deep problem-solving needed
verbosity = "medium"            # Code with helpful comments
max_output_tokens = 3000

# Use case: Debug complex issue
result = await agent_llm_integration.generate_for_agent(
    agent_name="CodeDebugger",
    prompt=f"Find and fix the bug in this code: {code}",
    model=model,
    reasoning_effort=reasoning_effort,
    verbosity=verbosity,
    max_output_tokens=max_output_tokens
)
```

**Why:** Complex coding tasks need the full gpt-5 model with high reasoning for problem-solving.

---

### 9. Quick Response & FAQ Agents

**Examples:** Customer Support, FAQ Bot, Quick Answer

```python
# Configuration
model = "gpt-5-nano"
reasoning_effort = "minimal"    # Fast, direct responses
verbosity = "low"              # Brief, to-the-point answers
max_output_tokens = 300

# Use case: Answer FAQ
result = await agent_llm_integration.generate_for_agent(
    agent_name="FAQBot",
    prompt=f"Answer this question: {user_question}",
    model=model,
    reasoning_effort=reasoning_effort,
    verbosity=verbosity,
    max_output_tokens=max_output_tokens
)
```

**Why:** FAQ responses should be fast and brief - nano with minimal reasoning provides instant, concise answers.

---

### 10. Multi-Turn Conversation Agents

**Examples:** Personal Assistant, Interview Bot, Dialog Manager

```python
# Configuration with chain of thought
model = "gpt-5-mini"
reasoning_effort = "low"
verbosity = "medium"
max_output_tokens = 1000

# First turn
result1 = await agent_llm_integration.generate_for_agent(
    agent_name="PersonalAssistant",
    prompt="What are your career goals?",
    model=model,
    reasoning_effort=reasoning_effort,
    verbosity=verbosity,
    max_output_tokens=max_output_tokens
)

# Second turn - with context!
result2 = await agent_llm_integration.generate_for_agent(
    agent_name="PersonalAssistant",
    prompt=f"User said: {user_response}. Ask follow-up question.",
    model=model,
    reasoning_effort=reasoning_effort,
    verbosity=verbosity,
    max_output_tokens=max_output_tokens,
    previous_response_id=result1.get('response_id')  # ✅ Chain of thought!
)
```

**Why:** Conversations benefit from passing chain of thought to maintain context and avoid re-reasoning.

---

## 🎯 Decision Matrix

| Agent Task Type | Model | Reasoning | Verbosity | Max Tokens | Why |
|----------------|-------|-----------|-----------|------------|-----|
| **Content Creation** | gpt-5-mini | medium | high | 2000 | Creative structure + detailed output |
| **Job Search** | gpt-5-mini | low | medium | 1000 | Straightforward matching |
| **Sports Analysis** | gpt-5-mini | medium | medium | 1500 | Analytical thinking needed |
| **Client Acquisition** | gpt-5-mini | high | medium | 2000 | Complex strategic planning |
| **Trading Signals** | gpt-5-mini | medium | low | 800 | Analysis + concise signals |
| **Classification** | gpt-5-nano | minimal | low | 200 | Fast, cheap, simple |
| **Data Analysis** | gpt-5-mini | medium | medium | 1500 | Pattern recognition |
| **Coding Tasks** | gpt-5 | high | medium | 3000 | Complex problem-solving |
| **FAQ/Support** | gpt-5-nano | minimal | low | 300 | Speed + brevity |
| **Conversations** | gpt-5-mini | low | medium | 1000 | With chain of thought |

---

## 💰 Cost Optimization

### When to Use Each Model

**gpt-5-nano** ($0.05 / $0.40 per 1M tokens)
- ✅ High-volume simple tasks
- ✅ Classification/tagging
- ✅ FAQ responses
- ✅ Quick categorization

**gpt-5-mini** ($0.25 / $2.00 per 1M tokens) ← **MOST COMMON**
- ✅ Most agent tasks
- ✅ Standard analysis
- ✅ Content creation
- ✅ Data processing

**gpt-5** ($1.25 / $10.00 per 1M tokens)
- ✅ Complex coding
- ✅ Deep strategic planning
- ✅ Multi-step problem solving
- ✅ When quality is paramount

### Cost Reduction Tips

1. **Start with nano/mini** - Only upgrade if quality isn't sufficient
2. **Use minimal reasoning** - When tasks are straightforward
3. **Lower verbosity** - When brief outputs are acceptable
4. **Leverage chain of thought** - Reuse reasoning with previous_response_id
5. **Reduce max_output_tokens** - Don't allocate more than needed

---

## 🚀 Quick Start Examples

### Example 1: Update Job Search Agent

**Before (incorrect):**
```python
result = await openai_client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,  # ❌ Error!
    max_tokens=1000
)
```

**After (correct):**
```python
result = await agent_llm_integration.generate_for_agent(
    agent_name="JobSearchAgent",
    prompt=prompt,
    model="gpt-5-mini",
    reasoning_effort="low",
    verbosity="medium",
    max_output_tokens=1000
)
```

---

### Example 2: Update Content Creator

**Before (incorrect):**
```python
response = await openai_client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": content_prompt}],
    temperature=0.9,  # ❌ Error!
    max_tokens=2000
)
content = response.choices[0].message.content
```

**After (correct):**
```python
result = await agent_llm_integration.generate_for_agent(
    agent_name="ContentCreator",
    prompt=content_prompt,
    model="gpt-5-mini",
    reasoning_effort="medium",
    verbosity="high",
    max_output_tokens=2000
)
content = result['response']
```

---

## 📊 Monitoring & Optimization

### Track Usage by Agent

```python
stats = agent_llm_integration.get_usage_stats()

for agent_name, agent_stats in stats['by_agent'].items():
    print(f"{agent_name}:")
    print(f"  Requests: {agent_stats['requests']}")
    print(f"  Input tokens: {agent_stats['tokens_in']}")
    print(f"  Output tokens: {agent_stats['tokens_out']}")
    print(f"  Reasoning tokens: {agent_stats['reasoning_tokens']}")
    print(f"  Cost: ${agent_stats['cost']:.4f}")
```

### Identify Optimization Opportunities

1. **High reasoning token usage?** → Consider lowering reasoning_effort
2. **High output tokens for simple tasks?** → Lower verbosity
3. **Using gpt-5 for simple tasks?** → Switch to mini or nano
4. **Multi-turn conversations?** → Use previous_response_id

---

## ✅ Implementation Checklist

- [ ] Review each agent's task complexity
- [ ] Choose appropriate model (nano/mini/full)
- [ ] Set reasoning_effort based on complexity
- [ ] Set verbosity based on output needs
- [ ] Configure max_output_tokens appropriately
- [ ] Implement previous_response_id for conversations
- [ ] Test with real prompts
- [ ] Monitor costs and optimize
- [ ] Document agent-specific configurations

---

**Next Steps:**
1. Update each agent file with proper configuration
2. Test with real prompts and data
3. Monitor performance and costs
4. Iterate on configurations as needed
