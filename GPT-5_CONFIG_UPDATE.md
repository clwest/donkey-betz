# GPT-5 Configuration Update Guide

## Overview
This document outlines all necessary changes to update the Unified Donkey Betz Platform to support OpenAI's GPT-5 models, released in August 2025.

## GPT-5 Model Specifications

### Available Models
| Model | Input Price (per 1M tokens) | Output Price (per 1M tokens) | Description |
|-------|---------------------------|------------------------------|-------------|
| **gpt-5** | $1.25 | $10.00 | Standard reasoning model with full capabilities |
| **gpt-5-mini** | $0.25 | $2.00 | Smaller, faster variant for moderate complexity |
| **gpt-5-nano** | $0.05 | $0.40 | Most cost-effective for simple tasks |
| **gpt-5-chat-latest** | $1.25 | $10.00 | Non-reasoning version used in ChatGPT |

### Model Capabilities
- **Token Limits**: 272,000 input tokens, 128,000 output tokens (including reasoning tokens)
- **Input Types**: Text and images
- **Output Type**: Text only
- **Reasoning Levels**: minimal, low, medium, high
- **Special Features**:
  - Parallel tool calling
  - Built-in tools (web search, file search, image generation)
  - Prompt caching (90% discount on cached input tokens)
  - Structured outputs
  - Streaming support

## Required File Updates

### 1. AI Provider Configuration
**File**: `content/ai_providers.py`

Update the pricing dictionary:
```python
self.pricing = {
    # Add GPT-5 models
    'gpt-5': {'input': 1.25, 'output': 10.0},
    'gpt-5-mini': {'input': 0.25, 'output': 2.0},
    'gpt-5-nano': {'input': 0.05, 'output': 0.40},
    'gpt-5-chat-latest': {'input': 1.25, 'output': 10.0},
    # Keep existing GPT-4 models for fallback
    'gpt-4': {'input': 0.03, 'output': 0.06},
    'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
    # ... existing models
}
```

Update available models list:
```python
self.available_models = [
    'gpt-5',
    'gpt-5-mini',
    'gpt-5-nano',
    'gpt-5-chat-latest',
    'gpt-4o',  # Keep for fallback
    'gpt-4-turbo-preview',
    'gpt-4-turbo',
    'gpt-4',
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-16k'
]
```

### 2. Multi-Model Comparison Views
**File**: `core/views_multi_llm.py`

Add GPT-5 models to the model list (line 262):
```python
models = data.get('models', ['gpt-5', 'gpt-5-mini', 'gpt-4', 'claude-3-sonnet'])
```

Update model configurations:
```python
OPENAI_MODELS = [
    {
        'id': 'gpt-5',
        'name': 'GPT-5',
        'provider': 'openai',
        'context_window': 272000,
        'max_output': 128000,
        'supports_reasoning': True
    },
    {
        'id': 'gpt-5-mini',
        'name': 'GPT-5 Mini',
        'provider': 'openai',
        'context_window': 272000,
        'max_output': 128000,
        'supports_reasoning': True
    },
    {
        'id': 'gpt-5-nano',
        'name': 'GPT-5 Nano',
        'provider': 'openai',
        'context_window': 272000,
        'max_output': 128000,
        'supports_reasoning': True
    },
    # Keep existing models...
]
```

### 3. Core Views
**File**: `core/views.py` (line 380)
```python
# Update default model
model = 'gpt-5-mini'  # Changed from 'gpt-3.5-turbo'
```

**File**: `core/views_agent_orchestration.py`
```python
'model': 'gpt-5-mini',  # Updated from 'gpt-4'
```

**File**: `core/views_rag_embeddings.py` (line 128)
```python
model = data.get('model', 'gpt-5-mini')  # Updated from 'gpt-4'
```

### 4. Backend Settings
**File**: `backend/settings.py`
```python
AI_CONFIG = {
    'DEFAULT_LLM_MODEL': 'gpt-5-mini',  # Updated from 'gpt-4'
    # Add reasoning configuration
    'GPT5_REASONING_LEVELS': ['minimal', 'low', 'medium', 'high'],
    'DEFAULT_REASONING_LEVEL': 'medium',
}
```

### 5. Agent Configuration

**File**: `agents/models.py`
```python
llm_model = models.CharField(
    max_length=100,
    default='gpt-5-mini',  # Updated from 'gpt-4'
    help_text="LLM model to use for this agent"
)
```

**File**: `agents/management/commands/migrate_all_discovered_agents.py`
Update all instances of:
```python
"llm_model": "gpt-5-mini",  # Updated from "gpt-4"
```

**File**: `sports/agents.py` (line 71)
```python
self.llm_model = "gpt-5-mini"  # Updated from "gpt-4"
```

### 6. Content Management Commands

**File**: `content/management/commands/create_content_agents.py`
```python
'llm_model': 'gpt-5',  # Updated from 'gpt-4-turbo-preview'
```

**File**: `content/models.py`
```python
llm_model = models.CharField(
    max_length=100,
    default='gpt-5',  # Updated from 'gpt-4-turbo-preview'
)
```

### 7. Frontend Updates

**File**: `frontend/src/services/promptDiagnostics.service.ts`
```typescript
calculateCostEstimate(tokens: number, model: string = 'gpt-5-mini'): number {
  const rates = {
    'gpt-5': 0.00125,      // $1.25 per 1K input tokens
    'gpt-5-mini': 0.00025, // $0.25 per 1K input tokens
    'gpt-5-nano': 0.00005, // $0.05 per 1K input tokens
    'gpt-4': 0.00003,      // Keep for comparison
    'gpt-4-turbo': 0.00001,
    'gpt-3.5-turbo': 0.000002,
  };
  const rate = rates[model as keyof typeof rates] || rates['gpt-5-mini'];
  return (tokens / 1000) * rate;
}
```

**File**: `frontend/src/components/features/prompt-diagnostics/PromptAnalyzer.tsx`
```typescript
const [targetModel, setTargetModel] = useState('gpt-5-mini');

// In the select options:
<option value="gpt-5">GPT-5 (Best Reasoning)</option>
<option value="gpt-5-mini">GPT-5 Mini (Balanced)</option>
<option value="gpt-5-nano">GPT-5 Nano (Fast & Cheap)</option>
<option value="gpt-4">GPT-4 (Legacy)</option>
```

**File**: `frontend/src/pages/profile/ProfilePage.tsx`
```typescript
<option value="gpt-5">GPT-5</option>
<option value="gpt-5-mini">GPT-5 Mini</option>
<option value="gpt-5-nano">GPT-5 Nano</option>
<option value="gpt-4">GPT-4 (Legacy)</option>
```

**File**: `frontend/src/components/features/content-generation/TextGenerator.tsx`
```typescript
<option value="gpt-5">GPT-5 (Best)</option>
<option value="gpt-5-mini">GPT-5 Mini (Balanced)</option>
<option value="gpt-5-nano">GPT-5 Nano (Fast)</option>
<option value="gpt-4">GPT-4 (Legacy)</option>
```

**File**: `frontend/src/services/agent-orchestra.service.ts`
```typescript
llm_model: 'gpt-5-mini',  // Updated from 'gpt-4'
```

## New Features to Implement

### 1. Reasoning Level Support
Add support for GPT-5's reasoning levels in API calls:
```python
def call_gpt5_with_reasoning(prompt, reasoning_level='medium'):
    response = openai.ChatCompletion.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}],
        reasoning_effort=reasoning_level,  # New parameter
        verbosity='auto'  # New parameter
    )
    return response
```

### 2. Prompt Caching Implementation
Implement prompt caching to reduce costs:
```python
class PromptCache:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_cached_response(self, prompt_hash):
        if prompt_hash in self.cache:
            cached_item = self.cache[prompt_hash]
            if time.time() - cached_item['timestamp'] < self.cache_ttl:
                return cached_item['response']
        return None
```

### 3. Extended Token Handling
Update token counting and limits:
```python
MAX_INPUT_TOKENS = {
    'gpt-5': 272000,
    'gpt-5-mini': 272000,
    'gpt-5-nano': 272000,
    'gpt-4': 128000,
    'gpt-3.5-turbo': 16385
}

MAX_OUTPUT_TOKENS = {
    'gpt-5': 128000,
    'gpt-5-mini': 128000,
    'gpt-5-nano': 128000,
    'gpt-4': 4096,
    'gpt-3.5-turbo': 4096
}
```

## Migration Strategy

### Phase 1: Preparation (Week 1)
1. Update all configuration files with GPT-5 model definitions
2. Add GPT-5 pricing to cost tracking systems
3. Update frontend model selectors

### Phase 2: Testing (Week 2)
1. Deploy changes to development environment
2. Test each agent with GPT-5-nano first (lowest cost)
3. Compare performance metrics with GPT-4
4. Validate token usage and cost calculations

### Phase 3: Gradual Rollout (Week 3-4)
1. Start with non-critical agents using GPT-5-nano
2. Move content generation to GPT-5-mini
3. Upgrade complex reasoning agents to GPT-5
4. Keep GPT-4 as fallback option

### Phase 4: Optimization (Ongoing)
1. Implement prompt caching for frequently used prompts
2. Use reasoning levels appropriately:
   - `minimal` - Simple Q&A
   - `low` - Basic tasks
   - `medium` - Standard operations (default)
   - `high` - Complex reasoning tasks
3. Monitor costs and adjust model selection

## Cost Optimization Guidelines

### Model Selection Strategy
- **GPT-5-nano** ($0.05/$0.40): 
  - Simple text generation
  - Basic Q&A
  - Data formatting
  
- **GPT-5-mini** ($0.25/$2.00):
  - Code generation
  - Content creation
  - Standard agent operations
  
- **GPT-5** ($1.25/$10.00):
  - Complex reasoning
  - Multi-step problem solving
  - Critical decision making

### Cost Comparison
| Task Type | Previous (GPT-4) | Recommended (GPT-5) | Cost Change |
|-----------|------------------|---------------------|-------------|
| Simple Q&A | GPT-3.5 ($0.002) | GPT-5-nano ($0.05) | +25x input, -5x output |
| Code Generation | GPT-4 ($0.06) | GPT-5-mini ($0.25) | +4x input, -3x output |
| Complex Reasoning | GPT-4 ($0.06) | GPT-5 ($1.25) | +20x input, +166x output |

## Monitoring and Rollback Plan

### Key Metrics to Monitor
1. Response latency
2. Token usage per request
3. Cost per operation
4. Error rates
5. User satisfaction scores

### Rollback Triggers
- Cost increase >50% without corresponding value
- Error rate >5%
- Response time degradation >2x
- User complaints about quality

### Rollback Process
1. Keep GPT-4 configurations in place (commented out)
2. Use feature flags for model selection
3. Implement A/B testing for gradual migration
4. Maintain fallback logic in all API calls

## Environment Variables Update
Add to `.env`:
```bash
# GPT-5 Configuration
DEFAULT_GPT5_MODEL=gpt-5-mini
GPT5_REASONING_LEVEL=medium
ENABLE_PROMPT_CACHING=True
PROMPT_CACHE_TTL=300
GPT5_FALLBACK_MODEL=gpt-4
ENABLE_GPT5_MIGRATION=True
```

## Testing Checklist
- [ ] Update all model references in Python files
- [ ] Update all model references in TypeScript files
- [ ] Add GPT-5 pricing configurations
- [ ] Test agent orchestration with GPT-5-mini
- [ ] Validate content generation with GPT-5
- [ ] Test sports betting agents with GPT-5-nano
- [ ] Verify cost tracking accuracy
- [ ] Test fallback to GPT-4 on errors
- [ ] Validate token limit handling
- [ ] Test reasoning level parameters
- [ ] Verify prompt caching functionality
- [ ] Load test with extended token limits
- [ ] Validate frontend model selectors
- [ ] Test WebSocket real-time updates
- [ ] Verify database migrations

## Notes
- GPT-5 was released August 7, 2025
- Free tier users have access to GPT-5 with rate limits
- Plus/Pro subscribers get enhanced access
- Enterprise/Edu access requires separate registration
- Azure OpenAI users need registration for gpt-5 (not for mini/nano)

## Support Resources
- OpenAI Platform Docs: https://platform.openai.com/docs/models/gpt-5
- API Migration Guide: https://openai.com/index/introducing-gpt-5-for-developers/
- Pricing Calculator: https://openai.com/api/pricing/
- Community Forum: https://community.openai.com/t/gpt-5-gpt-5-mini-and-gpt-5-nano-now-available-in-the-api/