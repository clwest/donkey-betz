# Session 349: Prompt vs Chat Audit and Integration

**Date:** December 4, 2025
**Focus:** Auditing prompting vs conversational chat handling, integrating QueryClassifier into main chat flow
**Status:** COMPLETE

---

## Executive Summary

The system has sophisticated infrastructure (`QueryClassifier`, `DynamicPromptBuilder`, `AgentRouter`) that was NOT connected to the main chat flow. The 6800-line `PersonalAIAssistant` used keyword matching instead of classification. This session integrates the classification system into the main chat path.

---

## Part 1: Audit Findings

### The Problem: Two Parallel Systems

The platform had **two different paths** for user messages:

#### Path 1: SuperPlatformCoordinator (The "Brain")
**Location:** `core/super_platform/coordinator.py`

This sophisticated system uses:
- `QueryClassifier.classify()` - 9 query types, confidence scoring
- `DynamicPromptBuilder.build()` - Context-aware prompt construction
- `ContextAggregator` - Gathers spider data, memories, mood
- `AgentRouter` - Deterministic agent routing
- `LearningLoop` - Records outcomes

**BUT:** Only used when `USE_CLEAN_AGENT_ARCHITECTURE = True` and accessed via specific API endpoints in `views_super_platform.py`, NOT the main chat!

#### Path 2: PersonalAIAssistant (Main Chat)
**Location:** `core/personal_ai_assistant_enhanced.py` (6800+ lines)

This is what actually handles the AI Studio chat:
- Uses `PERSONAL_ASSISTANT_PROMPT` from registry
- Loads conversation history (limited to 5 turns)
- Injects spider intelligence
- Uses GPT tool calling
- Does NOT use `QueryClassifier`
- Does NOT use `DynamicPromptBuilder`
- Has hardcoded keyword matching instead

### Gap Analysis

| Described Behavior | Was Implemented? | Location |
|-------------------|------------------|----------|
| "Classify intent into QUESTION/CREATION/EDITING/RESEARCH" | Partial | QueryClassifier exists but wasn't used in main chat |
| "For CREATION/EDITING/RESEARCH, delegate to agents" | Partial | Keyword matching, not classification |
| "For QUESTIONS, answer directly" | LLM dependent | Prompt says to, no enforcement |
| "Ask clarifying questions for ambiguous" | No | No tracking/enforcement |
| "Delegation brief template" | No | Direct tool args |
| "Store minimal context from prior turns" | 5 turns only | `_load_conversation_history(limit=5)` |

### Key Files Audited

| File | Purpose | Status |
|------|---------|--------|
| `core/super_platform/query_classifier.py` | Intent classification with 9 query types | Underutilized |
| `core/super_platform/prompt_builder.py` | Dynamic prompt construction | Underutilized |
| `core/agent_router.py` | Deterministic agent routing | Working |
| `core/prompts/registry.py` | Central system prompts | Working |
| `core/prompts/tool_descriptions.py` | Tool routing rules | Working |
| `core/personal_ai_assistant_enhanced.py` | Main chat handler | Needed integration |

### QueryClassifier Capabilities (Already Built)

```python
class QueryType(Enum):
    QUESTION = "question"           # Informational - uses spider data
    CREATION = "creation"           # Generate content - uses agents
    WORKFLOW = "workflow"           # Multi-step - uses orchestrator
    ANALYSIS = "analysis"           # Research + insight - uses research agents
    MEMORY = "memory"               # Recall past interactions
    COLLABORATION = "collaboration" # Hive mind / multi-agent
    OPPORTUNITY = "opportunity"     # Revenue-focused queries
    SYSTEM = "system"               # Platform status, agent info
    CONVERSATION = "conversation"   # General chat, greeting
```

Features:
- Priority phrases that override keyword classification
- Confidence scoring (0-1)
- Entity detection (style, content_type, platform, agent, topic)
- Urgency detection
- Agent suggestions based on query type

---

## Part 2: Implementation Changes

### 2.1 Classification Integration Service

Created: `core/services/classification_integration.py`

This service bridges the QueryClassifier to the PersonalAIAssistant:

```python
class ClassificationIntegrationService:
    """
    Bridges QueryClassifier to PersonalAIAssistant for intelligent routing.

    Key behaviors:
    1. QUESTION/CONVERSATION: No tools, answer directly
    2. CREATION/WORKFLOW/ANALYSIS: Enable tools, proceed to GPT
    3. Low confidence (<0.6): May trigger clarification
    """
```

**Key Classes:**
- `ClarificationState` - Tracks clarification questions per conversation
- `DelegationBrief` - Structured agent delegation data
- `ClassificationDecision` - Routing decision with tool filtering

### 2.2 Clarification Tracking

Added clarification tracking to manage when to ask for more info:

```python
@dataclass
class ClarificationState:
    clarifications_asked: int = 0
    max_clarifications: int = 1
    last_clarification_type: Optional[str] = None
    missing_parameters: List[str] = field(default_factory=list)
```

### 2.3 Delegation Brief Structure

Created structured briefs for agent delegation:

```python
@dataclass
class DelegationBrief:
    agent_name: str
    task_objective: str
    deliverable_type: str
    style_preferences: List[str]
    constraints: List[str]
    reference_ids: List[str]
    count: int
    priority: str
    context: Dict[str, Any]
```

### 2.4 PersonalAIAssistant Integration

Modified `_generate_ai_response()` in `personal_ai_assistant_enhanced.py` (lines 6780-6888):

**Before (100+ hardcoded keywords):**
```python
operation_keywords = [
    'generate image', 'create image', 'draw', 'make image',
    # ... 100+ more keywords
]
is_operation = any(keyword in message.lower() for keyword in operation_keywords)
```

**After (Classification-based routing):**
```python
from core.services.classification_integration import (
    get_classification_integration_service,
    ClarificationState
)

classification_service = get_classification_integration_service()

if classification:
    query_type = classification.primary_type.value

    if query_type in ('question', 'conversation'):
        # NO TOOLS - direct response
        tools = []

    elif query_type in ('creation', 'workflow', 'analysis'):
        # TOOLS ENABLED - force tool execution
        is_operation = True
```

**Key Behavior Changes:**
1. **QUESTION/CONVERSATION** → `tools = None`, direct LLM response (no tool calling)
2. **CREATION/WORKFLOW/ANALYSIS** → Tools enabled, `mode: required`
3. **Low confidence (<0.6)** → Clarification suggested
4. **Fallback** → Legacy keyword matching if classification unavailable

---

## Part 3: Technical Details

### Query Type to Tool Mapping

| Query Type | Tools Enabled | Behavior |
|------------|---------------|----------|
| QUESTION | None | Answer directly with spider data |
| CONVERSATION | None | Casual response, no tools |
| CREATION | Image, Video, Audio, 3D | Enable generation tools |
| WORKFLOW | Workflow orchestration | Enable multi-step workflows |
| ANALYSIS | Research, Competitor, Customer | Enable analysis tools |
| MEMORY | Memory tools | Query Memory Palace |
| COLLABORATION | Hive mind | Multi-agent coordination |
| OPPORTUNITY | Opportunity scoring | Revenue analysis |
| SYSTEM | System info | Platform status |

### Clarification Triggers

Clarification is suggested when:
1. Classification confidence < 0.6
2. Required parameters are missing (detected via entity extraction)
3. Ambiguous content type (could be image OR video)

### Priority Phrases (Override Keywords)

These phrases are checked FIRST and override keyword-based classification:

```python
PRIORITY_PHRASES = {
    QueryType.ANALYSIS: [
        'competitor analysis', 'competitive analysis', 'market analysis',
        'swot analysis', 'customer research', 'customer personas',
        'target audience', 'pain point analysis',
    ],
    QueryType.WORKFLOW: [
        'research and create', 'brand identity package', 'thumbnail package',
        'logo package', 'full brand kit', 'complete package',
    ],
}
```

This prevents "generate a competitor analysis" from being classified as CREATION.

---

## Part 4: Files Modified

| File | Changes |
|------|---------|
| `core/services/classification_integration.py` | **NEW** - Classification bridge service |
| `core/personal_ai_assistant_enhanced.py` | Integrated classification before GPT calls (lines 6780-6888) |
| `core/super_platform/query_classifier.py` | Added QUESTION priority phrases for style/advice queries (line 259-268), expanded WORKFLOW patterns (line 277-284) |

---

## Part 5: Testing Results

All 6 core test cases pass:

| Test Case | Expected Type | Expected Tools | Result |
|-----------|--------------|----------------|--------|
| "What's trending in AI?" | QUESTION | No | ✅ |
| "Create a cyberpunk logo" | CREATION | Yes | ✅ |
| "Research competitors and create logos" | WORKFLOW | Yes | ✅ |
| "Analyze the coffee shop market" | ANALYSIS | Yes | ✅ |
| "hello" | CONVERSATION | No | ✅ |
| "What style would work best for a logo?" | QUESTION | No | ✅ |

**To run tests yourself:**
```bash
.venv/bin/python manage.py shell -c "
from core.services.classification_integration import get_classification_integration_service
service = get_classification_integration_service()
result = service.classify_and_decide('What style would work best?')
print(f'Type: {result.query_type}, Tools: {result.should_use_tools}')
"
```

---

## Part 6: Model-Agnostic Assessment (Bonus)

During this session, we also conducted a full review of GPT/OpenAI usage for potential Ollama support:

### Current State
- **80+ locations** with direct OpenAI imports
- **45+ hardcoded model names** (`gpt-5-mini`)
- **Existing Ollama infrastructure** in `llm/` module (not fully utilized)

### Ollama Infrastructure Already Built
- `core/settings.py` - `LLM_DEFAULT_PROVIDER = "ollama"` configured
- `llm/ollama_provider.py` - Working Ollama provider
- `ai_core/llm_adapter_async.py` - Async adapter with Ollama support

### Gap for Full Model-Agnosticism
- Need `OpenAIProvider` in `llm/router.py`
- Tool calling abstraction needed
- Embedding abstraction needed
- 50+ files need refactoring to use factory pattern

---

## Part 7: Bug Fix - BusinessResearchResult Project Linking

### Issue Found
BrandStrategyAgent reported "no competitor analysis or customer research available" even though prior research existed. The cause was research results being saved with `project=NULL`.

### Root Cause
The `save_competitor_analysis()` and `save_customer_research()` methods in `BusinessResearchResult` were trying to save a `user` field that doesn't exist in the model:

```python
# BROKEN (Session 349 initial fix):
instance = cls.objects.create(
    ...
    project=project,
    user=user,  # ❌ Model doesn't have this field!
)
```

This caused a `TypeError: BusinessResearchResult() got unexpected keyword arguments: 'user'`, silently failing the save operation.

### Fix Applied
Removed `user=user` from both methods since `BusinessResearchResult` doesn't have a `user` field:

```python
# FIXED:
instance = cls.objects.create(
    ...
    project=project,  # ✅ This works
)
```

### Files Changed
| File | Line | Change |
|------|------|--------|
| `core/models_unified_system.py` | 11900 | Removed `user=user` from `save_competitor_analysis()` |
| `core/models_unified_system.py` | 11840 | Removed `user=user` from `save_customer_research()` |

### Verification
```bash
.venv/bin/python manage.py shell -c "
from core.models_unified_system import BusinessResearchResult
from core.models_partnership import PartnershipProject
project = PartnershipProject.objects.first()
result = BusinessResearchResult.save_competitor_analysis(
    query='Test', synthesis={'analysis': 'Test'},
    project_id=str(project.id)
)
print(f'Project: {result.project}')  # ✅ Shows project, not None
"
```

---

## Next Session Priorities

1. **Test the full pipeline** - Create a new project through Agent Pipeline Visualizer
2. **Verify BrandStrategyAgent** now finds prior competitor/customer research
3. **Monitor classification accuracy** - tune confidence thresholds if needed
4. **Add metrics/logging** for classification decisions
5. **Consider enabling `USE_CLEAN_AGENT_ARCHITECTURE`** to use full SuperPlatformCoordinator

---

## Related Documentation

- `docs/ARCHITECTURE.md` - System architecture
- `docs/SESSION_266_PROMPTING_SYSTEM_INTEGRATION.md` - Original prompting system design
- `core/super_platform/query_classifier.py` - Classification implementation
- `core/prompts/registry.py` - Central prompt registry
