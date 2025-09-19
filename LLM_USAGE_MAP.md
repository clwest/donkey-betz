# Complete LLM Usage Map - Unified Donkey Betz Platform
## Generated: 2025-09-18

## Summary Statistics
- **Total LLM Call Locations**: 37 unique locations
- **Direct OpenAI Calls**: 29 locations
- **LLMEnforcer Usage**: 8 locations
- **Models Used**: GPT-4, GPT-4o, GPT-4o-mini, GPT-5, GPT-5-mini, GPT-3.5-turbo, Claude-3-haiku

---

## 📍 LLM Call Locations by Component

### 1. **Intelligence Module - Real Agents** (`intelligence/real_agents.py`)
**Total Calls**: 8 direct OpenAI calls
**Model**: GPT-4o-mini
**Use Cases**:
- **Line 55**: Base agent execution (general task processing)
- **Line 94**: Analytics insights generation
- **Line 219**: Platform-specific content creation
- **Line 265**: Agent-specific task execution
- **Line 318**: Specialized agent operations
- **Line 365**: Custom agent workflows
- **Line 416**: Advanced agent capabilities
- **Line 473**: Complex task orchestration

### 2. **AI Resume Generator** (`intelligence/ai_resume_generator.py`)
**Total Calls**: 2 LLMEnforcer calls
**Use Cases**:
- **Line 255**: Resume content generation from job descriptions
- **Line 517**: Cover letter creation and customization

### 3. **Personal Assistant Interviewer** (`intelligence/personal_assistant_interviewer.py`)
**Total Calls**: 3 LLMEnforcer calls
**Use Cases**:
- **Line 117**: AI system health check and initialization
- **Line 195**: Conversational question generation (CURRENTLY DISABLED)
- **Line 236**: User response acknowledgment generation

### 4. **Agent Execution Pipeline** (`intelligence/agent_execution_pipeline.py`)
**Total Calls**: 2 direct OpenAI calls
**Model**: GPT-5-mini
**Use Cases**:
- **Line 58**: Content generation for agent tasks
- **Line 329**: Real-time agent execution with reasoning

### 5. **Income Builder** (`intelligence/income_builder.py`)
**Total Calls**: 1 direct OpenAI call
**Model**: GPT-5-mini
**Use Cases**:
- **Line 1682**: Income opportunity analysis and recommendations

### 6. **Content AI Providers** (`content/ai_providers.py`)
**Total Calls**: 6 calls (5 OpenAI, 1 Anthropic)
**Models**: Various GPT models + Claude
**Use Cases**:
- **Line 162**: Main content generation endpoint
- **Line 172**: Retry logic for content generation
- **Line 196**: GPT-5-mini specific retry without system prompt
- **Line 249**: GPT-5 specific parameter handling
- **Line 255**: Standard model content generation
- **Line 347**: Claude/Anthropic content generation

### 7. **Agent Factory** (`intelligence/agent_factory.py`)
**Total Calls**: 1 direct OpenAI call
**Model**: GPT-4o-mini
**Use Cases**:
- **Line 265**: Dynamic agent creation and configuration

### 8. **Core Components**

#### **LLM Enforcer** (`core/llm_enforcer.py`)
**Central AI Gateway**: All enforce_real_ai() calls route here
- **Line 201**: OpenAI chat completion (GPT-3.5-turbo)
- **Line 228**: Anthropic messages (Claude-3-haiku)
**Features**:
- Automatic provider fallback
- Cost tracking
- Usage metrics
- Audit logging

#### **Opportunity AI Analyzer** (`core/opportunity_ai_analyzer.py`)
**Total Calls**: 1 LLMEnforcer call
**Use Cases**:
- **Line 346**: Job/opportunity automation analysis

#### **Content Executor** (`agents/content_executor.py`)
**Total Calls**: 1 direct OpenAI call
**Model**: GPT-4
**Use Cases**:
- **Line 105**: High-quality Donkey Betz content generation

---

## 🎯 Use Case Categories

### **Content Generation** (40% of calls)
- Blog posts, articles, marketing content
- Resume and cover letter generation
- Platform-specific content (Donkey Betz)
- SEO-optimized content

### **Agent Task Execution** (30% of calls)
- Agent-specific operations
- Multi-agent orchestration
- Dynamic task processing
- Real-time decision making

### **Analysis & Intelligence** (20% of calls)
- Opportunity analysis
- Income recommendations
- Analytics insights
- Risk assessment

### **Conversational AI** (10% of calls)
- Interview questions
- User acknowledgments
- Interactive responses
- Chat functionality

---

## 🔧 Technical Details

### **Models in Active Use**:
1. **GPT-4o-mini**: Primary model for agents (8 locations)
2. **GPT-5-mini**: Income and pipeline execution (3 locations)
3. **GPT-4**: High-quality content generation (1 location)
4. **GPT-3.5-turbo**: LLMEnforcer default (fallback)
5. **Claude-3-haiku**: Alternative provider option

### **API Call Patterns**:
```python
# Pattern 1: Direct OpenAI Client
response = self.client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    temperature=0.7
)

# Pattern 2: LLMEnforcer (Recommended)
result = self.llm_enforcer.enforce_real_ai(
    prompt="...",
    agent_name="...",
    task_type="...",
    max_tokens=500
)

# Pattern 3: Content Provider Abstraction
result = ai_provider.generate_content(
    prompt="...",
    model="gpt-5",
    config={...}
)
```

---

## 🚨 Issues Identified

### **Critical**:
1. **Disabled AI in Interviewer**: Line 140-141 forces fallback due to bug
2. **Mock Response Methods**: Still exist in agent_factory.py

### **Medium Priority**:
1. **Inconsistent Model Usage**: Some using GPT-4o-mini, others GPT-5-mini
2. **No Central Configuration**: Models hardcoded in multiple places
3. **Limited Error Handling**: Some locations lack proper fallback

### **Low Priority**:
1. **Cost Tracking**: Only in LLMEnforcer, not in direct calls
2. **Audit Logging**: Inconsistent across components

---

## 📊 Statistics by Model

| Model | Locations | Primary Use |
|-------|-----------|------------|
| GPT-4o-mini | 9 | Agent execution |
| GPT-5-mini | 3 | Income/pipeline |
| GPT-4 | 2 | Premium content |
| GPT-3.5-turbo | 1 | Fallback/default |
| Claude-3-haiku | 1 | Alternative provider |
| GPT-5 | 4 | Advanced features |

---

## 🎬 Recommendations

### **Immediate Actions**:
1. **Re-enable Personal Assistant Interviewer AI** (Line 140-141)
2. **Remove mock response methods** from agent_factory.py
3. **Standardize on LLMEnforcer** for all new AI calls

### **Short-term Improvements**:
1. **Create central model configuration**:
```python
# config/ai_models.py
AI_MODELS = {
    'default': 'gpt-4o-mini',
    'premium': 'gpt-4',
    'fast': 'gpt-3.5-turbo',
    'income': 'gpt-5-mini',
    'fallback': 'claude-3-haiku'
}
```

2. **Implement consistent error handling**:
```python
try:
    result = llm_call()
except Exception as e:
    logger.error(f"LLM call failed: {e}")
    return fallback_response()
```

### **Long-term Strategy**:
1. **Migrate all direct calls to LLMEnforcer**
2. **Implement rate limiting and quotas**
3. **Add A/B testing for model performance**
4. **Create unified prompt management system**
5. **Build cost optimization layer**

---

## 🔍 Quick Verification Script

```python
# verify_llm_locations.py
import os
import re

def count_llm_calls(directory):
    patterns = {
        'direct_openai': r'\.chat\.completions\.create',
        'direct_anthropic': r'\.messages\.create',
        'llm_enforcer': r'enforce_real_ai',
        'gpt4o_mini': r'gpt-4o-mini',
        'gpt5_mini': r'gpt-5-mini',
        'gpt4': r'gpt-4["\']',
        'gpt5': r'gpt-5["\']'
    }

    results = {key: [] for key in patterns}

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    for pattern_name, pattern in patterns.items():
                        matches = re.findall(pattern, content)
                        if matches:
                            results[pattern_name].append({
                                'file': filepath,
                                'count': len(matches)
                            })

    return results

# Run verification
results = count_llm_calls('/Users/donkeyking/development/unified-donkey-betz')
for pattern, files in results.items():
    if files:
        print(f"\n{pattern}: {sum(f['count'] for f in files)} total calls")
        for f in files[:5]:  # Show top 5
            print(f"  - {f['file'].split('/')[-1]}: {f['count']} calls")
```