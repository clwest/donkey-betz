# Session 781: Agent Conversation Voice Fixes

**Date:** January 19, 2026
**Focus:** Eliminating repetitive agent conversation styles with 3-level improvements

## Problem Statement

Agent conversations were suffering from repetitive, corporate-sounding language:
- "I'd push back slightly" used 12+ times per conversation
- Generic hedging phrases across all agents
- Agents sounded like templates, not experts
- No distinct voice per agent type

**Root Cause:** Training data patterns + shared politeness priors causing all agents to use the same "safe disagreement" language.

## Solution: 3-Level Voice Improvement

### Level 2: Role-Anchored Disagreement Styles (The Real Fix)

Expanded `CONVERSATION_ROLES` in `core/prompts/registry.py` from 3 to 22 entries.

Each agent type now has:
- A distinct **Role Title** (DATA REALIST, NARRATIVE ARCHITECT, DEVIL'S ADVOCATE, etc.)
- A unique **Disagreement Style** with domain-specific openers
- Explicit **NEVER use** instructions banning generic hedging

**Agents with custom conversation roles:**

| Category | Agents |
|----------|--------|
| Research & Analysis | ResearchAgent, TrendAnalysisAgent, OpportunityScoringAgent |
| Strategy | ContentStrategyAgent, SEOOptimizerAgent, BrandIdentityAgent |
| Executive | CreativeDirectorAgent, CTOAgent, COOAgent |
| Workflow | WorkflowAgent |
| Content Studio | ContrarianAgent, TopicMinerAgent, PerformanceAnalystAgent |
| Podcast | DebateAdvocateAgent, DebateSkepticAgent, ModeratorAgent |
| Development | CodeGeneratorAgent, CodeReviewAgent |
| Business | CompetitorAnalysisAgent, CustomerResearchAgent |

**Example - ResearchAgent:**
```
WHEN CHALLENGING, use phrases like:
- "The data contradicts that assumption."
- "Our spider network shows a different pattern."
- "There's a hidden risk the numbers reveal."
- "The evidence points in another direction."

NEVER use generic hedges like "I'd push back slightly" or "That's a great point, but..."
```

### Level 1: Style De-duplication (Fast Win)

Added opener tracking to prevent the same opening phrase from being used twice.

**New in ConversationState:**
```python
used_openers: List[str] = field(default_factory=list)
```

**New functions:**
- `extract_opener(text)` - Extracts first 60 chars of response
- Tracking after each message
- Prompt injection: "These openers have been used, find fresh alternatives"

**Disallowed openers (global ban):**
- "I'd push back slightly"
- "That's a great point"
- "I agree, but"
- "That's a fair point"
- "Absolutely"
- "With all due respect"
- "I love that"

### Level 3: Discourse Memory (Comprehensive)

Tracks common discourse markers throughout conversations.

**DISCOURSE_MARKERS dictionary - 5 categories, 50+ phrases:**

```python
DISCOURSE_MARKERS = {
    'transitions': ["however", "that said", "building on that", ...],
    'agreement': ["i see your point", "that makes sense", ...],
    'disagreement': ["i'd question", "the concern is", ...],
    'fillers': ["to be honest", "in my view", ...],
    'hedges': ["sort of", "kind of", "slightly", ...],
}
```

**Prompt injection when phrases overused:**
```
DISCOURSE MEMORY (Session 781 Level 3):
These phrases have been OVERUSED in this conversation - find fresh alternatives:
"however", "in my view", "that said"

Vary your language. Don't fall into repetitive patterns.
```

## Files Modified

| File | Changes |
|------|---------|
| `core/prompts/registry.py` | +611 lines - Expanded CONVERSATION_ROLES from 3 to 22 |
| `core/conversation_orchestrator.py` | +222 lines - Opener tracking, discourse memory, prompt injection |
| `core/tasks.py` | +91 lines - Same tracking for multi-agent panel discussions |

## Expected Impact

**Before (repetitive, corporate):**
```
ContentStrategyAgent: I'd push back slightly — in content we see it as...
WorkflowAgent: I'd push back slightly — in automation, we see it as...
ResearchAgent: That's a great point, but I'd push back slightly...
```

**After (varied, distinctive):**
```
ContentStrategyAgent: The narrative falls apart at that point. Users will bounce before...
WorkflowAgent: That breaks down in the handoff between steps. The orchestration complexity...
ResearchAgent: The data contradicts that assumption. 50 data points from HackerNews show...
```

## State Tracking

Conversation results now include:
```python
'state': {
    'unique_openers_count': 5,
    'used_openers': [...],
    'discourse_markers_total': 12,
    'discourse_markers_unique': 8,
    'overused_phrases': [
        {'phrase': 'however', 'count': 3},
        {'phrase': 'that said', 'count': 2}
    ]
}
```

## Verification

The changes are immediately active for all:
- ConversationOrchestrator conversations
- Multi-agent panel discussions in Celery tasks
- Podcast debates

Monitor logs for:
- `Tracked opener: '...'`
- `Tracked N discourse markers`

## Related Sessions

- Session 717: Conversation Contract Page
- Session 261: Original ConversationOrchestrator
- Session 364: Panel diversity prompts

## Commit

```
feat(Session 781): Agent conversation style fixes - 3-level voice improvement
```
