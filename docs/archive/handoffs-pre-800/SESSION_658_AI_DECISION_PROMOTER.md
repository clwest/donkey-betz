# Session 658: AI Decision Auto-Promoter

**Date:** January 1, 2026
**Focus:** AI-powered autonomous decision promotion using GPT-5-mini
**Status:** COMPLETE - System running autonomously

---

## Executive Summary

Built a fully autonomous AI decision promotion system that uses GPT-5-mini's reasoning capabilities to evaluate pending decisions and auto-promote high-quality ones to canonical policy status. This closes the governance loop: agents make decisions, AI evaluates them, and the best ones become official policies that influence future agent behavior.

### Key Metrics

| Metric | Before | After |
|--------|--------|-------|
| Total Decisions | 976 | 976 |
| Canonical | 130 | 884 (90.6%) |
| AI-Promoted | 0 | 754 |
| Pending Drafts | 842 | 78 |

---

## What Was Built

### 1. AI Decision Promoter Service

**File:** `core/services/ai_decision_promoter.py`

A service that uses GPT-5-mini (reasoning model) to evaluate decisions:

```python
from core.services.ai_decision_promoter import AIDecisionPromoterService

service = AIDecisionPromoterService()
result = service.run_batch_promotion(batch_size=50)
```

#### GPT-5-mini Configuration (Reasoning Model)

GPT-5-mini is a reasoning model with different parameters than standard chat models:

| Parameter | Value | Why |
|-----------|-------|-----|
| **API** | Responses API | Enables chain-of-thought reasoning |
| **reasoning.effort** | `medium` | Gives model time to think through evaluation |
| **text.verbosity** | `medium` | Allows room for explanation |
| **max_output_tokens** | `500` | Plenty of tokens for reasoning |
| **temperature** | NOT USED | Reasoning models don't support temperature |

```python
# CORRECT GPT-5-mini usage
response = self.client.responses.create(
    model="gpt-5-mini",
    input=prompt,
    reasoning={"effort": "medium"},
    text={"verbosity": "medium"},
    max_output_tokens=500
)
```

#### Evaluation Criteria

The AI evaluates each decision against these criteria:
1. Is it actionable and specific (not vague)?
2. Does it provide clear guidance?
3. Is it relevant to system operations, strategy, or development?
4. Does it contain concrete insights (not just platitudes)?

Decisions with **confidence >= 0.7** are auto-promoted to canonical.

#### Robust JSON Parsing (4 Strategies)

GPT-5-mini sometimes includes explanation text around JSON responses. The service handles this with 4 fallback strategies:

1. **Direct JSON parse** - Try parsing the full response
2. **Find JSON in text** - Extract `{...}` from response
3. **Regex extraction** - Find `"promote": true`, `"confidence": 0.85` patterns
4. **Keyword inference** - Look for "should be promoted" phrases

---

### 2. Celery Task

**File:** `core/tasks.py` (line ~20360)

```python
@shared_task
def ai_promote_decisions(batch_size: int = 50):
    """Session 658: AI-powered decision auto-promotion using GPT-5-mini."""
    from core.services.ai_decision_promoter import AIDecisionPromoterService

    service = AIDecisionPromoterService()
    result = service.run_batch_promotion(
        batch_size=batch_size,
        promoter_name="AI-AutoPromoter-Celery"
    )
    return result
```

Features:
- Sends Discord notification when 5+ decisions are promoted
- Returns comprehensive stats (evaluated, promoted, rejected, model, etc.)
- Logs all activity with `[SESSION 658]` prefix

---

### 3. Celery Beat Schedule

**File:** `core/celery.py` (line ~1446)

```python
'ai-promote-decisions': {
    'task': 'core.tasks.ai_promote_decisions',
    'schedule': crontab(hour='*/4', minute=20),  # Every 4 hours at :20
    'options': {
        'expires': 14400,  # 4 hours
        'queue': 'long_running',  # Uses OpenAI API, may take time
    },
    'kwargs': {
        'batch_size': 50,  # Process 50 decisions per run
    }
}
```

**Schedule:** Runs at 0:20, 4:20, 8:20, 12:20, 16:20, 20:20 every day

---

## How It Works

### The Governance Loop

```
1. Agents have conversations
       ↓
2. Conclusions extracted as AgentDecisionSummary (status='draft')
       ↓
3. AI Decision Promoter evaluates decisions using GPT-5-mini
       ↓
4. High-quality decisions promoted to canonical (is_canonical=True)
       ↓
5. PolicyContextService injects canonical policies into future prompts
       ↓
6. Future agents behave according to past wisdom
       ↓
   [Loop continues]
```

### Decision Flow

| Status | Meaning |
|--------|---------|
| `draft` | New decision, awaiting evaluation |
| `pending` | Under review |
| `review` | Needs human review |
| `canonical` | Promoted - official policy |

### Promoter Trail

Each promoted decision records who promoted it:
- `AI-AutoPromoter-Session658` - Manual run during session
- `AI-AutoPromoter-Celery` - Scheduled Celery task
- `AI-AutoPromoter-GPT5-Enhanced` - Enhanced GPT-5 run
- `human` - Manual promotion via UI
- `auto_promote_task` - Legacy rule-based promotion

---

## Files Modified/Created

| File | Changes |
|------|---------|
| `core/services/ai_decision_promoter.py` | **NEW** - AI promotion service |
| `core/tasks.py` | Added `ai_promote_decisions` task (~75 lines) |
| `core/celery.py` | Added `ai-promote-decisions` schedule (~12 lines) |

---

## Usage

### Manual Run

```python
# In Django shell
from core.services.ai_decision_promoter import run_ai_decision_promotion
result = run_ai_decision_promotion(batch_size=100)
print(f"Promoted: {result['promoted']}")
```

### Check Stats

```python
from core.services.ai_decision_promoter import AIDecisionPromoterService
service = AIDecisionPromoterService()
stats = service.get_promotion_stats()
print(f"Canonical: {stats['canonical']} ({stats['canonical_percentage']}%)")
print(f"AI-Promoted: {stats['ai_promoted']}")
print(f"Remaining Drafts: {stats['pending_draft']}")
```

### Trigger Celery Task

```bash
# From command line
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/celery -A core call core.tasks.ai_promote_decisions --kwargs='{"batch_size": 50}'
```

---

## Monitoring

### Logs

Look for `[SESSION 658]` in Celery worker logs:

```
🤖 [SESSION 658] Starting AI decision promotion (batch_size=50)...
🤖 [SESSION 658] AI promoted 12 decisions (rejected 38, model: gpt-5-mini)
```

### Discord

When 5+ decisions are promoted, a notification is sent to `#system-status`:

```
**🤖 AI Decision Promoter**
✅ Promoted 12 decisions to canonical
Model: gpt-5-mini
```

### Database

```sql
-- Check promotion stats
SELECT promoted_by, COUNT(*)
FROM core_agentdecisionsummary
WHERE is_canonical = true
GROUP BY promoted_by
ORDER BY COUNT(*) DESC;

-- Recent AI promotions
SELECT topic, promoted_at, promoted_by
FROM core_agentdecisionsummary
WHERE promoted_by LIKE 'AI-%'
ORDER BY promoted_at DESC
LIMIT 10;
```

---

## Why GPT-5-mini?

1. **Reasoning Capabilities** - Can think through evaluation criteria
2. **Cost Effective** - $0.25/1M input, $2.00/1M output
3. **Consistent** - Reasoning models produce more predictable outputs
4. **No Temperature** - Removes randomness for consistent evaluations

---

## The Remaining 78 Drafts

After processing 842 pending decisions, 78 remain as drafts. These were evaluated multiple times and consistently rejected because they:
- Lack concrete insights (too vague)
- Don't provide actionable guidance
- Are duplicates or low-quality

These will continue to be evaluated by the scheduled task, but are unlikely to be promoted unless they somehow improve.

---

## Session 659 Recommendations

1. **Monitor overnight** - Check logs tomorrow for AI promotion activity
2. **Review remaining 78** - Consider manual review or archival
3. **Tune threshold** - If too few are promoted, lower from 0.7 to 0.6
4. **Add metrics dashboard** - Show AI promotion stats in UI

---

## Quick Commands

```bash
# Start platform
make start
make celery

# Check Celery beat schedule
grep -A 10 "ai-promote-decisions" core/celery.py

# Check recent promotions
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentDecisionSummary
recent = AgentDecisionSummary.objects.filter(promoted_by__icontains='AI').order_by('-promoted_at')[:5]
for d in recent:
    print(f'{d.promoted_at}: {d.topic[:50]}...')
"

# Manual test run
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
from core.tasks import ai_promote_decisions
result = ai_promote_decisions(batch_size=10)
print(result)
"
```

---

**System is now running autonomously. Let it run overnight and check results tomorrow!**
