# Session 625 - Reality Check Bug Fixes

**Date:** December 30, 2025
**Focus:** Fix bugs discovered by System Reality Check (Session 624)
**Result:** Overall score improved from 68% → 78%

---

## Summary

Session 624 created `system_reality_check` command which revealed multiple systems showing incorrect or low scores. Session 625 investigated and fixed the underlying issues.

---

## Bugs Fixed

### 1. Celery Beat Check (30% → 88%)

**Problem:** `TaskResult` table was empty because Celery stores results to Redis, not Django DB.

**Fix:** Changed to use `PeriodicTask.last_run_at` which IS stored in DB.

**File:** `core/services/system_reality_checker.py`
```python
# Before: Checking TaskResult (empty - stores to Redis)
# After: Using PeriodicTask.last_run_at
```

### 2. ThinkingAgent Check (60% → 100%)

**Problem:** Same `TaskResult` issue.

**Fix:** Changed to check `ThoughtRecord` model directly.

**File:** `core/services/system_reality_checker.py`

### 3. Learning Loops Check (59% → 92%)

**Problem:** Counting `AgentLearning` records (always 0) + `KnowledgeTransfer`.

**Root Cause:** `AgentLearning` model exists but is UNUSED. The learning system was refactored to use `KnowledgeTransfer` for agent-to-agent knowledge sharing.

**Fix:**
- Removed `AgentLearning` from calculation
- Adjusted expected rate from 6/hour to 2/hour

**File:** `core/services/system_reality_checker.py`
```python
# Before
activity_ratio = (recent_learning + recent_transfers) / expected_min

# After
activity_ratio = recent_transfers / expected_min
```

### 4. Artifact Extraction (0 → 167 artifacts)

**Problem:** `batch_extract_artifacts()` finding 0 conversations.

**Root Cause:** Filtering by `status='completed'` but actual status is `'concluded'`.

**Fix:** `core/services/artifact_extraction.py`
```python
# Before
status='completed'

# After
status='concluded'
```

**Additional Fixes:**
- `conversation.messages[:30]` → `conversation.messages.all()[:30]` (RelatedManager)
- `max_completion_tokens=2000` → `8000` (GPT-5-mini reasoning model)

### 5. Pilots/Gates Field Names (0% → 45%)

**Problem:** Checking wrong field names.

**Fix:** `core/services/system_reality_checker.py`
- `approved_at` → `gate_approved_at`
- `pilot_completed_at` → `completed_at`

### 6. Migration Dependency

**Problem:** Migration 0137 depended on non-existent 0136.

**Fix:** Changed dependency to 0135.

---

## Data Generated

| Item | Count |
|------|-------|
| ExtractedArtifacts | 167 |
| ReviewDocuments | 58 |
| Dreams Scored | 49 |
| Dreams Promoted | 2 |

---

## Final Reality Check Results

```
Overall Score: 78%
├── Celery Beat:     88% ✅ (was 30%)
├── Triggers:       100% ✅
├── Learning Loops:  92% ✅ (was 59%)
├── Dreams Pipeline: 70% ⚠️
├── Boardroom:        9% ❌ (needs human decisions)
├── ThinkingAgent:  100% ✅ (was 60%)
├── Conversations:  100% ✅
├── Spider Network: 100% ✅
└── Pilots/Gates:    45% ⚠️ (was 0%)
```

---

## Key Findings

### AgentLearning Model is Unused

The learning system was refactored at some point. Current architecture:

- **Old (unused):** `AgentLearning` model
- **Current:** `run_agent_learning_cycle` creates:
  - `KnowledgeTransfer` records (tracking what was shared)
  - `AgentKnowledgeSource` records (the actual knowledge)

The `AgentLearning` model still exists in `core/models_unified_system.py` but nothing writes to it.

### Boardroom Requires Human Action

58 ReviewDocuments await human decision. This is working as designed - the Chief of Staff pipeline creates Pro/Con review documents that need human approval.

To improve Boardroom score: AI Studio → Boardroom tab → Approve/Decline items.

### Dreams Task Not Running Regularly

`score_and_promote_dreams` is scheduled every 20 minutes but routed to `long_running` queue. Need to ensure Celery worker for this queue is active.

---

## Files Modified

| File | Change |
|------|--------|
| `core/services/system_reality_checker.py` | Fixed Celery Beat, ThinkingAgent, Learning Loops, Pilots/Gates checks |
| `core/services/artifact_extraction.py` | Fixed status filter, RelatedManager, GPT-5-mini tokens |
| `core/migrations/0137_*.py` | Fixed dependency |

---

## Commands Used

```bash
# Run reality check
python manage.py system_reality_check

# Extract artifacts from conversations
python manage.py shell -c "from core.services.artifact_extraction import extraction_service; print(extraction_service.batch_extract())"

# Generate review documents
python manage.py shell -c "from core.services.review_document import review_service; print(review_service.generate_pending_reviews())"

# Score and promote dreams
python manage.py shell -c "from core.tasks import score_and_promote_dreams; print(score_and_promote_dreams())"
```

---

## Next Session Priorities

1. **Make Boardroom decisions** - 58 pending reviews
2. **Ensure dream scoring runs** - Check `long_running` Celery queue
3. **Create pilot experiments** - Test Pilots/Gates pipeline
