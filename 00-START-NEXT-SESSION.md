# Session 659 - Start Here

**Previous Session:** 658
**Date:** January 1, 2026
**Focus:** AI Decision Promoter - GPT-5-mini Autonomous Governance
**Health Score:** 90.6% Canonical Decisions

---

## Session 658 Accomplishments

### 1. AI Decision Promoter Service - COMPLETE

Built `core/services/ai_decision_promoter.py` using GPT-5-mini Responses API:

| Config | Value |
|--------|-------|
| Model | `gpt-5-mini` (reasoning model) |
| API | Responses API (not Chat Completions) |
| reasoning.effort | `medium` |
| max_output_tokens | `500` |
| Confidence Threshold | `0.7` |

### 2. Celery Scheduled Task - COMPLETE

Added `ai_promote_decisions` task running every 4 hours:

```python
'ai-promote-decisions': {
    'task': 'core.tasks.ai_promote_decisions',
    'schedule': crontab(hour='*/4', minute=20),  # 0:20, 4:20, 8:20, etc.
    'options': {'queue': 'long_running'},
    'kwargs': {'batch_size': 50}
}
```

### 3. Results

| Metric | Before | After |
|--------|--------|-------|
| Canonical Decisions | 130 | 884 (90.6%) |
| AI-Promoted | 0 | 754 |
| Remaining Drafts | 842 | 78 |

---

## System Stats (After Session 658)

| Component | Count | Status |
|-----------|-------|--------|
| **Running Pilots** | 18 | All at 80% System Health |
| **Completed Pilots** | 90 | Tracked |
| **Total Decisions** | 976 | 90.6% canonical |
| **AI-Promoted** | 754 | GPT-5-mini evaluated |
| **Active Agents** | 71 | All routable |
| **Spiders** | 77 | 100% health |

---

## Quick Start

```bash
# 1. Start platform
make start
make celery

# 2. Access AI Studio
open http://localhost:8000/ai-studio/

# 3. Check AI Promoter Stats
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
from core.services.ai_decision_promoter import AIDecisionPromoterService
stats = AIDecisionPromoterService().get_promotion_stats()
print(f'Canonical: {stats[\"canonical\"]} ({stats[\"canonical_percentage\"]}%)')
print(f'AI-Promoted: {stats[\"ai_promoted\"]}')
print(f'Remaining: {stats[\"pending_draft\"]}')
"

# 4. Check Celery logs for overnight activity
grep "SESSION 658" nohup.out | tail -20
```

---

## Key Files Modified (Session 658)

| File | Changes |
|------|---------|
| `core/services/ai_decision_promoter.py` | **NEW** - GPT-5-mini promotion service |
| `core/tasks.py` | Added `ai_promote_decisions` Celery task |
| `core/celery.py` | Added schedule (every 4h at :20) |
| `docs/handoffs/SESSION_658_AI_DECISION_PROMOTER.md` | Full documentation |

---

## GPT-5-mini Notes (Reasoning Model)

**CRITICAL:** GPT-5-mini uses different parameters than chat models!

```python
# CORRECT - Responses API
response = client.responses.create(
    model="gpt-5-mini",
    input=prompt,
    reasoning={"effort": "medium"},
    text={"verbosity": "medium"},
    max_output_tokens=500
    # NO temperature parameter!
)

# WRONG - Chat Completions (don't use)
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    temperature=0.7,  # ERROR - not supported!
    max_tokens=500    # WRONG - use max_output_tokens
)
```

See `docs/architecture/GPT5_REASONING_MODELS_GUIDE.md` for full details.

---

## Overnight Monitoring

The AI Decision Promoter runs every 4 hours. Check tomorrow:

1. **Celery logs:** `grep "SESSION 658" nohup.out`
2. **Discord:** Check `#system-status` for promotion notifications
3. **Stats:** Run the quick check command above

---

## Session 659 Suggestions

1. Review overnight AI promotion activity
2. Consider archiving the remaining 78 low-quality drafts
3. Add AI promotion stats to the UI dashboard
4. Tune confidence threshold if needed (currently 0.7)

---

## Key Handoff Documents

| Session | Document | Focus |
|---------|----------|-------|
| **658** | `SESSION_658_AI_DECISION_PROMOTER.md` | **AI Decision Promoter (GPT-5-mini)** |
| **657** | *(commits only)* | All pilots connected to all data sources |
| **656** | *(commits only)* | Pilot card hypothesis + recommended actions |
| **654** | `SESSION_654_AUTONOMOUS_GATE_APPROVAL.md` | Auto-waive low-risk gates |

---

**Always read this document first when starting a new session!**
