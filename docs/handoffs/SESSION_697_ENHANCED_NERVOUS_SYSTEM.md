# Session 697: Enhanced Nervous System - Multi-Model LLM Routing

**Date:** January 6, 2026
**Focus:** Add multi-model LLM routing to route agents to specialized LLMs
**Status:** COMPLETE

---

## Summary

Session 697 enhanced the nervous system to support multiple LLM providers. Previously all agents used GPT-5.1 (OpenAI). Now agents can be routed to specialized models:
- **Coding agents** → DeepSeek Coder (excellent + cheap)
- **Creative agents** → Claude (excellent writing)
- **Reasoning agents** → Claude Opus (deep thinking)
- **Fast routing** → GPT-5-mini (quick + cheap)
- **Private/local** → Ollama (no API cost)

---

## What Was Built

### 1. Database Models (`core/models_llm_routing.py` ~647 lines)

**4 New Models:**

| Model | Purpose |
|-------|---------|
| `LLMProvider` | Provider configs (OpenAI, Anthropic, DeepSeek, Gemini, Ollama) |
| `LLMModel` | Individual models with capabilities, cost, specializations |
| `AgentLLMConfig` | Maps agents to their optimal primary/fallback models |
| `LLMCallLog` | Audit log for cost tracking, performance analysis |

**22 Default Agent Configs:**
- CodeGeneratorAgent → DeepSeek Coder
- ContentWriterAgent → Claude 3.5 Sonnet
- ThinkingAgent → Claude 3.5 Opus
- PersonalAssistantAgent → GPT-5-mini
- ResearchAgent → GPT-5.1
- (17 more...)

### 2. Provider Registry (`core/services/llm_provider_registry.py` ~927 lines)

Unified interface to 5 LLM providers:

| Provider | Models | Status |
|----------|--------|--------|
| **OpenAI** | GPT-5-mini, GPT-5.1, GPT-5.2 | ✅ Active |
| **Anthropic** | Claude 3.5 Sonnet/Haiku/Opus | ✅ Active |
| **DeepSeek** | DeepSeek Coder, DeepSeek Chat | ⚠️ Needs API key |
| **Gemini** | Gemini 2.0 Flash/Pro | ⚠️ Needs google-generativeai |
| **Ollama** | Llama 3.1, CodeLlama, Mistral | ✅ Active (local) |

**Key Features:**
- Standardized `LLMRequest` and `LLMResponse` dataclasses
- Per-provider cost calculation
- Health checking
- Automatic tool format conversion (OpenAI ↔ Anthropic)

### 3. Agent LLM Router (`core/services/agent_llm_router.py` ~400 lines)

Routes agents to their configured models with:
- Database-driven configuration
- Automatic fallback on failure
- Performance tracking and logging
- Task-specific model overrides
- Cost optimization

**Usage:**
```python
from core.services.agent_llm_router import route_agent_completion

response = route_agent_completion(
    agent_name='CodeGeneratorAgent',
    prompt='Write a Python function to...',
    system_prompt='You are an expert Python developer.'
)
print(response.content)  # From DeepSeek Coder
print(response.cost)     # $0.0004
```

### 4. BaseAgent Integration (`core/agents/base_agent.py`)

Added to BaseAgent:
- `llm_router` property (lazy-loaded)
- `_call_llm_routed()` method for multi-model calls

Agents can now use:
```python
# Old way (always GPT-5-mini)
result = self._call_openai(prompt)

# New way (routes to configured model)
result = self._call_llm_routed(prompt, task_type='coding')
```

### 5. Management Command (`core/management/commands/setup_llm_routing.py`)

```bash
# Setup all providers, models, and agent configs
python manage.py setup_llm_routing

# Check current status
python manage.py setup_llm_routing --check

# Clear and re-seed
python manage.py setup_llm_routing --clear
```

---

## Files Created/Modified

| File | Lines | Description |
|------|-------|-------------|
| `core/models_llm_routing.py` | +647 | 4 database models + default configs |
| `core/services/llm_provider_registry.py` | +927 | 5 provider implementations |
| `core/services/agent_llm_router.py` | +400 | Routing service |
| `core/agents/base_agent.py` | +80 | llm_router property + _call_llm_routed |
| `core/models/__init__.py` | +6 | Export LLM routing models |
| `core/migrations/0146_session_697_llm_routing.py` | +120 | Database migration |
| `core/management/commands/setup_llm_routing.py` | +190 | Setup command |

**Total New Code:** ~2,370 lines

---

## Human Body Metaphor Update

The nervous system now has two components:

| Component | File | Purpose |
|-----------|------|---------|
| NERVOUS SYSTEM (ML) | `core/services/agent_model_router.py` | Routes to ML models (LSTM, GNN, etc.) |
| NERVOUS SYSTEM (LLM) | `core/services/agent_llm_router.py` | Routes to LLM models (GPT, Claude, etc.) |

Like a biological nervous system:
- **ML Routing** = Muscle memory (fast pattern matching)
- **LLM Routing** = Conscious thought (deliberate reasoning)

---

## Database State

After running `setup_llm_routing`:

| Table | Count |
|-------|-------|
| `core_llm_providers` | 5 |
| `core_llm_models` | 13 |
| `core_agent_llm_configs` | 22 |
| `core_llm_call_logs` | 0 (populated on use) |

---

## API Keys Required

| Provider | Environment Variable | Status |
|----------|---------------------|--------|
| OpenAI | `OPENAI_API_KEY` | ✅ |
| Anthropic | `ANTHROPIC_API_KEY` | ✅ |
| DeepSeek | `DEEPSEEK_API_KEY` | ⚠️ Not set |
| Gemini | `GEMINI_API_KEY` | ✅ (library missing) |
| Ollama | None | ✅ (local) |

To add DeepSeek:
```bash
export DEEPSEEK_API_KEY="your-key"
```

To add Gemini:
```bash
pip install google-generativeai
export GEMINI_API_KEY="your-key"
```

---

## Testing Commands

```bash
# Check routing status
python manage.py setup_llm_routing --check

# Test in Django shell
python manage.py shell

>>> from core.services.agent_llm_router import get_agent_llm_router
>>> router = get_agent_llm_router()
>>> router.get_agent_config('CodeGeneratorAgent')
{'primary': {'provider': 'deepseek', 'model_id': 'deepseek-coder'}, ...}
```

---

## Session 698 Recommendations

1. **Add more agent configs** - Only 22 of 72 agents have configs
2. **Install google-generativeai** - Enable Gemini provider
3. **Get DeepSeek API key** - Unlock cheap coding model
4. **UI for LLM routing** - Admin panel to configure agent-model mappings
5. **Cost dashboard** - Show LLM costs per agent from LLMCallLog

---

## Commits

```
[To be committed after this handoff]
feat(Session 697): Enhanced Nervous System - Multi-Model LLM Routing
```

---

**Session 697 Status: COMPLETE**
