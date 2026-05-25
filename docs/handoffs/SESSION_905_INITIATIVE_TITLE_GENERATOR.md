---
originating_session: 905
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 905: Initiative Title Generator + Research Self-Unblock Loop

**Date:** February 1, 2026
**Status:** COMPLETE
**PRs:** #694, #695, #697

---

## Summary

Initiative names were displaying messy text fragments instead of proper titles. Created a smart title generation system with LLM + heuristic fallbacks that generates clean, action-oriented titles.

---

## Problem

Initiative titles in the UI were showing raw content fragments:

| Bad Title Examples |
|-------------------|
| `day Competitor Scan — an MVP that ingests conversation insig...` |
| `quality scores, (4) exposes a validation workflow for ResearchAgent...` |
| `driven Content Blueprint Generator: inputs = seed persona JSON...` |
| `accessible API for recommendations.` |
| `offs, produces prioritized recommendations, and writes them...` |

These fragments came from:
1. Raw `proposed_feature['name']` values from HiveMind conversations
2. Extracted content snippets from conversation pipeline
3. No validation or cleanup before saving to database

---

## Solution

### New Service: `core/services/initiative_title_generator.py`

```python
from core.services.initiative_title_generator import generate_initiative_title

title = generate_initiative_title(
    content="Long raw text with the actual topic buried somewhere...",
    topic_hint="Optional hint about what this is about",
    max_length=60,
    use_llm=True
)
```

**4-Step Title Generation:**

1. **Clean topic_hint** - If provided and valid, use it
2. **LLM Generation** - GPT-4o-mini generates concise title (5-10 words)
3. **Heuristic Extraction** - Pattern matching for headers, action phrases
4. **Unique Fallback** - Timestamp + UUID suffix to prevent duplicates

### Title Validation (`_is_valid_title`)

Detects invalid fragment patterns:
- Starts with lowercase (likely mid-sentence)
- Contains `inputs =`, `outputs =`, `(4) exposes`
- Starts with conjunctions: `and `, `or `, `of `
- Contains ellipsis `...`
- Multiple mid-sentence markers (`, and `, `, or `)

### LLM Prompt

```
Generate a clear, concise title (5-10 words max) for this initiative.

Rules:
- Title should be action-oriented (e.g., "Audit Experiment Halt Conditions")
- Use Title Case capitalization
- No punctuation at the end
- Must make sense standalone
- Maximum 60 characters
```

---

## Integration Points

### 1. Conversation Initiative Pipeline

**File:** `core/services/conversation_initiative_pipeline.py` (~line 274)

```python
from core.services.initiative_title_generator import generate_initiative_title

content_preview = extracted['content'][:2000] if extracted else ""
initiative_name = generate_initiative_title(
    content=content_preview,
    topic_hint=topic,
    max_length=80,
    use_llm=True
)
```

### 2. HiveMind Execution Pipeline

**File:** `core/services/hivemind_execution_pipeline.py` (~line 448)

```python
from core.services.initiative_title_generator import generate_initiative_title

raw_name = proposed_feature.get('name')
raw_text = proposed_feature.get('raw_text', '')
initiative_name = generate_initiative_title(
    content=raw_text or raw_name or '',
    topic_hint=raw_name or question,
    max_length=80,
    use_llm=True
)
```

---

## Management Command

**File:** `core/management/commands/fix_initiative_titles.py`

```bash
# Dry run (preview changes)
python manage.py fix_initiative_titles

# Actually fix titles
python manage.py fix_initiative_titles --fix

# Fix specific initiatives
python manage.py fix_initiative_titles --fix --ids="uuid1,uuid2"

# Limit batch size
python manage.py fix_initiative_titles --fix --limit=100
```

---

## Production Fix Results

**Railway Command:**
```bash
railway run -s donkey-betz-platform python manage.py fix_initiative_titles --fix --limit=50
```

**Results:**
- Total analyzed: 50 initiatives
- Good titles: 20 (already valid)
- Bad titles: 30 (fixed)
- **Success rate: 100%**

### Sample Transformations

| Before | After |
|--------|-------|
| `day Competitor Scan — an MVP that ingests...` | Implement 30-Day Competitor Insights Scan MVP |
| `time Odds Normalization & Signal API — ingest 6+...` | Launch Real-Time Odds Normalization and Signal API Pilot |
| `quality scores, (4) exposes a validation workflow...` | Automated Competitor Analysis Content Matrix Generator |
| `accessible API for recommendations.` | Implement Content Competitor Analysis Module for Insights |
| `Persona Generator: an automated module that ingests...` | Automate Persona Generation for Enhanced Content Strategy |
| `Consent‑First Embeddable Guest Portal that captures...` | Implement Consent-First Guest Portal for Seamless Engagement |

---

## Bug Fixes (PR #695)

Two bugs discovered during first production run:

### 1. LLM Client Import Error

**Problem:** `No module named 'core.llm_client'` on Railway

**Fix:** Changed to direct OpenAI import:
```python
# Before
from core.llm_client import get_llm_client
client = get_llm_client()

# After
import os
from openai import OpenAI
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
```

### 2. Duplicate Key Constraint Violation

**Problem:** Generic fallback title "Auto-created From Conversation Decision" caused unique constraint errors when multiple initiatives got the same fallback.

**Fix:** Added UUID suffix to all fallback titles:
```python
import uuid
unique_suffix = str(uuid.uuid4())[:6]
return f"{phrase} ({unique_suffix})"
```

---

## Files Changed

| File | Changes |
|------|---------|
| `core/services/initiative_title_generator.py` | NEW - Title generation service |
| `core/management/commands/fix_initiative_titles.py` | NEW - Batch fix command |
| `core/services/conversation_initiative_pipeline.py` | Integrated title generator |
| `core/services/hivemind_execution_pipeline.py` | Integrated title generator |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Initiative Creation                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  HiveMind Session                 Conversation Pipeline      │
│       │                                  │                   │
│       ▼                                  ▼                   │
│  proposed_feature['name']         extracted['content']       │
│       │                                  │                   │
│       └──────────────┬───────────────────┘                   │
│                      ▼                                       │
│         ┌────────────────────────┐                          │
│         │ generate_initiative_   │                          │
│         │ title()                │                          │
│         └────────────────────────┘                          │
│                      │                                       │
│         ┌────────────┼────────────┐                         │
│         ▼            ▼            ▼                         │
│    topic_hint    LLM (GPT-4o   Heuristic                    │
│    cleanup       -mini)        extraction                   │
│         │            │            │                         │
│         └────────────┼────────────┘                         │
│                      ▼                                       │
│              Clean Title (max 80 chars)                     │
│                      │                                       │
│                      ▼                                       │
│              Initiative.name                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

---

# Part 2: Research Self-Unblock Loop (PR #697)

## Problem

When research showed "Insufficient Data", the system was incomplete:

```
ThinkingAgent → request_research → ResearchAgent
    ↓
Insufficient Data detected → Spider spawned ✅
    ↓
Research Brief created with "Insufficient Data" text ✅
    ↓
❌ STOPS HERE - Nobody watches for spider data to continue
```

The "Decision Gate" in the Research Brief said "DataExportAgent may be needed" but nothing actually followed up.

## Solution: Complete Self-Unblock Loop

```
Research insufficient → Spider spawned → ResearchResult(blocked) →
Celery task (30 min) → Re-run research → Complete or retry (max 3x)
```

### New Model Fields: `ResearchResult`

```python
# Session 905: Data sufficiency tracking
data_sufficient = models.BooleanField(default=True)
blocked_reason = models.TextField(blank=True)
retry_count = models.IntegerField(default=0)
max_retries = models.IntegerField(default=3)
retry_after = models.DateTimeField(null=True, blank=True)
unblock_trigger = models.CharField(max_length=100, blank=True)
```

### New Stage Status: `InitiativeStage`

```python
class StageStatus(models.TextChoices):
    # ... existing statuses ...
    BLOCKED = 'BLOCKED', 'Blocked - Awaiting Data'  # NEW
```

### Celery Tasks

**`retry_blocked_research`** - Retries blocked research:
1. Checks if spider data has arrived
2. Re-runs ResearchAgent
3. If sufficient: marks complete, updates stage to DRAFT
4. If still insufficient: schedules another retry (up to 3x)
5. After max retries: marks failed, updates stage to REJECTED

**`check_blocked_research_for_unblock`** - Periodic task (every 15 min):
- Finds all blocked research ready to retry
- Triggers retry_blocked_research for each

### Modified: `autonomous_action_executor.py`

When research is blocked, now creates:
1. `ResearchResult` record with `status='blocked'`
2. `InitiativeStage` with `status='BLOCKED'`
3. Schedules `retry_blocked_research` task for 30 minutes later

```python
# Session 905: Create blocked ResearchResult and schedule retry
research_result_record = self._create_blocked_research_result(
    topic=topic,
    reasoning=reasoning,
    findings=findings,
    findings_detailed=findings_detailed,
    owner_agent=owner_agent,
    unblock_result=unblock_result
)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RESEARCH SELF-UNBLOCK LOOP                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Research Request                                                    │
│       ↓                                                              │
│  ResearchAgent.execute()                                             │
│       ↓                                                              │
│  [Check] data_insufficient = findings < 50 chars?                    │
│       ↓                                                              │
│  ┌─────────────────┐         ┌─────────────────┐                    │
│  │ Sufficient      │         │ Insufficient    │                    │
│  │ Data            │         │ Data            │                    │
│  └────────┬────────┘         └────────┬────────┘                    │
│           ↓                           ↓                              │
│  Stage 1: DRAFT              1. Spawn Spider                        │
│  Research Complete           2. Create ResearchResult(blocked)       │
│                              3. Stage 1: BLOCKED                     │
│                              4. Schedule retry (30 min)              │
│                                       ↓                              │
│                              ┌────────────────────┐                  │
│                              │ Celery: retry_     │                  │
│                              │ blocked_research   │                  │
│                              └────────┬───────────┘                  │
│                                       ↓                              │
│                              [Re-run Research]                       │
│                                       ↓                              │
│                     ┌─────────────────┴─────────────────┐           │
│                     ↓                                   ↓           │
│              Still Insufficient               Now Sufficient         │
│              (retry < 3)                      → Complete!            │
│                     ↓                                               │
│              Schedule retry +30 min                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Files Changed (PR #697)

| File | Changes |
|------|---------|
| `core/models_document_registry.py` | Added BLOCKED status to InitiativeStage |
| `core/models_research.py` | Added data_sufficient, retry tracking fields |
| `core/services/autonomous_action_executor.py` | _create_blocked_research_result method |
| `core/tasks.py` | retry_blocked_research, check_blocked_research_for_unblock |
| `core/celery.py` | Added periodic check task |
| `core/migrations/0214_*` | New migration for model changes |

---

---

# Part 3: Initiative Auto-Progression (PR #698)

## Problem

Initiatives with sufficient data were getting stuck at DRAFT status indefinitely:

```
Research Brief created with sufficient data ✅
    ↓
Stage 1: DRAFT (good content)
    ↓
❌ STOPS HERE - Nobody approves and triggers Stage 2
```

Despite having quality content that met progression criteria, initiatives required manual intervention to move forward.

## Solution: Auto-Progression Service

```
Stage with DRAFT status + Quality criteria met →
Celery task (every 10 min) → Auto-approve → Trigger next stage generation
```

### New Service: `core/services/initiative_auto_progression.py`

```python
from core.services.initiative_auto_progression import (
    check_stage_for_progression,
    progress_initiative_stage,
    trigger_next_stage_generation,
    get_initiatives_ready_for_progression
)

# Check single initiative
result = check_stage_for_progression(initiative_id)

# Auto-progress with next stage generation
result = progress_initiative_stage(initiative_id, auto_generate_next=True)
```

### Quality Thresholds (per stage)

| Stage | Min Length | Required Sections |
|-------|------------|-------------------|
| 1 (Research Brief) | 100 chars | Research Findings, Data Sources |
| 2 (Prototype Plan) | 200 chars | Architecture, Implementation |
| 3 (Evaluation) | 150 chars | Success Criteria, Metrics |
| 4 (Technical Design) | 300 chars | Specification, Dependencies |
| 5 (Pilot Execution) | 100 chars | Results, Learnings |

### Quality Evaluation Logic

1. **Length Check** - Content meets minimum char threshold
2. **Section Check** - Required sections present (case-insensitive)
3. **Blocker Detection** - Rejects if contains "insufficient data", "awaiting data", "blocked"
4. **Completion Markers** - Bonus confidence for "research completed", "data available", "findings"
5. **Confidence Score** - 60%+ required for auto-progression

### Celery Tasks

**`process_initiative_auto_progression`** - Runs every 10 minutes:
1. Finds all DRAFT stages with documents
2. Evaluates quality criteria
3. Auto-approves passing stages
4. Triggers next stage document generation

**`generate_initiative_stage_document`** - Generates stage documents:
1. Uses stage-appropriate agent (ResearchAgent, ThinkingAgent, FullStackDeveloperAgent)
2. Includes context from all previous stages
3. Creates Document and links to InitiativeStage
4. Sets stage status to DRAFT

### Agent Mapping

| Stage | Agent | Document Type |
|-------|-------|---------------|
| 1 | ResearchAgent | Research Brief |
| 2 | ThinkingAgent | Prototype Plan |
| 3 | ThinkingAgent | Evaluation Protocol |
| 4 | FullStackDeveloperAgent | Technical Design |
| 5 | ThinkingAgent | Pilot Execution Plan |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INITIATIVE AUTO-PROGRESSION                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Celery Beat (every 10 min)                                         │
│       ↓                                                              │
│  process_initiative_auto_progression                                 │
│       ↓                                                              │
│  Find DRAFT stages with documents                                    │
│       ↓                                                              │
│  ┌─────────────────────────────────────────┐                        │
│  │     evaluate_stage_quality()            │                        │
│  │     - Check content length              │                        │
│  │     - Check required sections           │                        │
│  │     - Check for blockers                │                        │
│  │     - Calculate confidence (0-100%)     │                        │
│  └────────────────────┬────────────────────┘                        │
│                       ↓                                              │
│        ┌──────────────┴──────────────┐                              │
│        ↓                             ↓                              │
│   Quality < 60%               Quality >= 60%                        │
│   → Stay DRAFT                → Auto-approve                        │
│                                      ↓                              │
│                           progress_initiative_stage()                │
│                                      ↓                              │
│                           Stage → APPROVED                          │
│                           Initiative.current_stage += 1             │
│                                      ↓                              │
│                           trigger_next_stage_generation()           │
│                                      ↓                              │
│                           generate_initiative_stage_document.delay() │
│                                      ↓                              │
│                           New stage document created                │
│                           New stage → DRAFT                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Files Changed (PR #698)

| File | Changes |
|------|---------|
| `core/services/initiative_auto_progression.py` | NEW - Auto-progression service |
| `core/tasks.py` | Added process_initiative_auto_progression, generate_initiative_stage_document |
| `core/celery.py` | Added periodic schedule (every 10 min) |

---

## Complete Session 905 Summary

### Three Parts Completed

1. **Initiative Title Generator** (PR #694, #695)
   - Smart LLM + heuristic title generation
   - Fixed 30 messy production titles

2. **Research Self-Unblock Loop** (PR #697)
   - Blocked research tracking
   - Auto-retry with spider data
   - Celery retry mechanism

3. **Initiative Auto-Progression** (PR #698)
   - Quality-based stage progression
   - Auto-approval when criteria met
   - Next stage document generation

### The Complete Initiative Lifecycle

```
HiveMind/Conversation → Initiative Created
        ↓
Stage 1: Research Brief (PENDING)
        ↓
ResearchAgent executes
        ↓
┌───────────────────────────────────────┐
│  Insufficient Data?                   │
│  → BLOCKED + Spider spawn + Retry     │
│                                       │
│  Sufficient Data?                     │
│  → DRAFT                              │
└───────────────────────────────────────┘
        ↓
Auto-Progression (every 10 min)
Quality check: length + sections + no blockers
        ↓
┌───────────────────────────────────────┐
│  Quality < 60%? → Stay DRAFT          │
│  Quality >= 60%? → APPROVED           │
└───────────────────────────────────────┘
        ↓
current_stage = 2
        ↓
generate_initiative_stage_document → Stage 2 DRAFT
        ↓
... repeat for Stages 2-5 ...
        ↓
Stage 5 APPROVED → FinalDeliverable created!
```

---

## Next Steps

1. **Monitor Auto-Progression** - Check Celery logs for `[AUTO-PROGRESSION]` entries
2. **Monitor Research Retries** - Check Celery logs for `[RESEARCH-RETRY]` entries
3. **Tune Quality Thresholds** - Adjust min_length or required_sections if too strict/lenient
4. **Add Manual Override** - UI to force-progress or block auto-progression

---

**Session 905: Complete! Initiative titles + Research self-unblock + Auto-progression!**
