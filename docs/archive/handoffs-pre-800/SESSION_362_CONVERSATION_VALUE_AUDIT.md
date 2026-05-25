# Session 362: Agent Conversation Value Audit + Auto-Promotion Fix

**Date:** December 5, 2025
**Focus:** Are 1,280 Agent Conversations Actually Being Used?
**Status:** AUDIT COMPLETE + FIX IMPLEMENTED - Auto-promotion now closes the feedback loop!

---

## Executive Summary

**Question:** Are the 1,280 agent conversations just stored in the database without influencing decisions?

**Answer:** The pipelines exist and ARE connected, but with significant inefficiency:
- **71.6% of conversations (917) produce no actionable output**
- Only 9% convert to Boardroom decisions
- Only 19.4% generate project insights
- Only 1 of 115 decisions has been promoted to canonical policy

---

## Audit Findings

### 1. Conversation Pipeline EXISTS (Not Wasted!)

The code at `core/tasks.py:3993-4012` connects conversations to:

```python
# Session 323: Extract decision from conversation
from core.services.decision_extractor import get_decision_extractor
decision = extractor.create_decision_from_conversation(conversation)

# Session 335: Process conversation for Living Projects
from core.services.living_project_service import get_living_project_service
insights = living_service.process_agent_conversation(conversation)
```

### 2. Conversion Metrics

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Conversations | 1,280 | 100% |
| → Decisions Extracted | 115 | 9.0% |
| → Project Insights Created | 248 | 19.4% |
| **Total Actionable** | **363** | **28.4%** |
| **Waste (No Output)** | **917** | **71.6%** |

### 3. Root Causes of Waste

#### A. Low Decision Extraction Rate (9%)

The `DecisionExtractor` (`core/services/decision_extractor.py:80-88`) rejects conversations if:
- Conclusion is empty or missing
- Conclusion length < 50 characters
- GPT fails to extract a structured decision

**Finding:** 96% of conversations HAVE conclusions (1,229/1,280), but most are too generic to extract structured decisions.

#### B. Limited Project Insight Matching (19.4%)

The `LivingProjectService` (`core/services/living_project_service.py:241-317`) creates insights ONLY when:
1. The conversation topic matches project topics (keyword matching)
2. The relevance score >= 0.5

**Finding:**
- Only 10 active projects exist in the system
- **Zero LivingProjectConfig records** - projects aren't configured for living updates!
- Keyword matching is simplistic (substring matches only)

#### C. No Automatic Policy Promotion

**Critical Finding:** Only **1 of 115 decisions** has been promoted to canonical policy!

The `AgentDecisionSummary` model has `is_canonical=True` for promotion, but:
- There's no automatic promotion mechanism
- Policies require manual promotion through the Boardroom UI
- Without canonical policies, decisions don't influence future agent behavior

---

## Data Flow Diagram

```
[Agent Conversation] ---> [run_agent_conversation()] ---> [Conclusion Generated]
                                    |
                     +--------------+--------------+
                     |                             |
                     v                             v
        [DecisionExtractor]            [LivingProjectService]
               |                                   |
               v                                   v
    [AgentDecisionSummary]                [ProjectInsight]
         (115 records)                     (248 records)
               |                                   |
               v                                   |
    [Manual Promotion to Canonical]                |
         (1 promoted)                              |
               |                                   |
               v                                   |
    [PolicyContextService]                         |
    (Injects into agent prompts)                   |
               |                                   |
               v                                   v
    [Future Agent Behavior]        [Project Notifications]
    (Only 1 policy active)         (Working for 10 projects)
```

---

## Recommendations

### 1. **Fix Automatic Policy Promotion** (High Impact)
Add Celery task to auto-promote high-quality decisions:

```python
@shared_task
def auto_promote_decisions():
    """Automatically promote high-quality decisions to canonical policies."""
    from core.models_unified_system import AgentDecisionSummary

    # Find high-quality unpromoted decisions
    candidates = AgentDecisionSummary.objects.filter(
        is_canonical=False,
        quality_score__gte=0.7  # High quality threshold
    ).order_by('-quality_score')[:5]

    for decision in candidates:
        decision.is_canonical = True
        decision.promoted_at = timezone.now()
        decision.save()
```

### 2. **Auto-Create LivingProjectConfig** (Medium Impact)
When projects are created, automatically create living configs:

```python
# In PartnershipProject.save() or via signal
if not hasattr(self, 'living_config'):
    LivingProjectConfig.objects.create(
        project=self,
        is_active=True,
        watch_topics=list(extract_topics(self.project_name))
    )
```

### 3. **Improve Decision Extraction** (Medium Impact)
The 50-character minimum for conclusions is too restrictive. Consider:
- Lowering threshold to 30 characters
- Adding fallback extraction from conversation messages if conclusion is short

### 4. **Add Quality Scoring to Decisions** (Low Impact, Enables #1)
Add `quality_score` field to AgentDecisionSummary based on:
- Conclusion length
- Number of key insights extracted
- Participant diversity
- Conversation depth (message count)

---

## Implementation: Auto-Promotion System

### What We Built

1. **Quality Score Field** (`core/models_unified_system.py:12984-12989`)
   - Added `quality_score` field to `AgentDecisionSummary`
   - Scores based on: stance length, key insights count, rationale, conversation depth, participant diversity
   - Range: 0.0 to 1.0

2. **Quality Calculation Method** (`core/models_unified_system.py:13044-13112`)
   - `calculate_quality_score()` - Evaluates decision quality
   - `update_quality_score()` - Calculates and saves

3. **Auto-Promote Celery Task** (`core/tasks.py:4486-4611`)
   - `auto_promote_decisions()` - Runs every 30 minutes
   - Updates unscored decisions
   - Promotes top 3 high-quality decisions per run
   - Ensures diversity across impact areas

4. **Celery Beat Schedule** (`core/celery.py:342-354`)
   - Runs every 30 minutes
   - Quality threshold: 0.6
   - Max 3 promotions per cycle

### Results After First Run

| Before | After |
|--------|-------|
| 1 canonical policy | 4 canonical policies |
| 0.1% conversion | Now auto-promoting! |

### New Canonical Policies Created

1. **Product/Product:** AI podcast platform guidance
2. **Policy/Workflow:** Data sample size warning
3. **Policy/Security:** Hugging Face data handling

## Files Modified

| File | Changes |
|------|---------|
| `core/models_unified_system.py` | Added `quality_score` field, `calculate_quality_score()`, `update_quality_score()` |
| `core/tasks.py` | Added `auto_promote_decisions` task + data source attribution in conversations |
| `core/celery.py` | Added `auto-promote-decisions` to Beat schedule |
| `core/settings.py` | Added `auto-promote-decisions` and `multi-agent-panel-cycle` to CELERY_BEAT_SCHEDULE |
| `core/migrations/0069_*` | Migration for quality_score field |

## Additional Fix: Data Source Attribution

Agents were saying "11 data points" without explaining WHERE the data came from.

**Before:** "my review of the 11 data points shows worrying gaps"
**After:** "my review of the 11 data points from the Notion spider shows worrying gaps"

Changes to both `run_agent_conversation()` and `run_multi_agent_conversation()`:
- Added `source_spider_names` to knowledge context
- Added `spider_category` to knowledge context
- Added guideline: "When citing data, mention the source"

---

## Key Files for Future Work

| File | Purpose |
|------|---------|
| `core/tasks.py:3993-4012` | Where conversations connect to pipelines |
| `core/services/decision_extractor.py` | Extracts structured decisions |
| `core/services/living_project_service.py` | Creates project insights |
| `core/services/policy_context.py` | Injects policies into prompts |
| `core/models_unified_system.py` | AgentDecisionSummary, ProjectInsight models |

---

## Conclusion

The agent conversation system is **NOT wasted** - pipelines exist and work. However:
- **71.6% waste rate** due to low conversion at each stage
- **Policy feedback loop is broken** (only 1 canonical policy exists)
- **Living Projects not configured** (0 LivingProjectConfig records)

The system was built correctly but needs:
1. Auto-promotion of high-quality decisions to policies
2. Auto-creation of LivingProjectConfig for projects
3. Better extraction thresholds

**Estimated Impact:** Fixing these issues could reduce waste from 71.6% to ~30-40% and create a functional feedback loop where agent conversations actually influence future agent behavior.
