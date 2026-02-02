# Session 905: Initiative Title Generator

**Date:** February 1, 2026
**Status:** COMPLETE
**PRs:** #694, #695

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

## Next Steps

1. **Monitor New Initiatives** - Verify titles are clean going forward
2. **Tune LLM Prompt** - Adjust if titles become too generic
3. **Add Title Edit UI** - Allow manual title override in modal

---

**Initiative titles are now clean and action-oriented!**
