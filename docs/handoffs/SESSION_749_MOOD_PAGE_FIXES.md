# Session 749 - Mood Page & Time Capsules Audit

**Date:** January 14, 2026
**Branch:** `feature/session-52-ai-assistant`
**Previous Session:** 748 (Evolution XP System Fix)

---

## Summary

1. Fixed the Mood Page data display and added full CRUD for mood rules
2. Backfilled mood history for all 73 agents
3. Deep audit of Time Capsules page - found and fixed critical GPT-5-mini token bug
4. Fixed Time Capsules frontend to fetch detail on selection

---

## Part 1: Mood Page Fixes

### 1.1 Backend API Field Mapping (`core/views_agent_mood.py`)

**Problem:** Frontend expected different field names than backend returned.

**Fix:** Updated `get_mood_overview()` and `get_mood_history()` to return frontend-expected fields:

| Backend Field | Frontend Field | Notes |
|---------------|----------------|-------|
| `agent.id` | `agent_id` | Added |
| `agent.name` | `agent_name` | Added |
| `mood.mood_started_at` | `last_updated` | Added alias |
| `mood.total_mood_changes` | `mood_streak` | Added alias |
| `mood.intensity` (0-1) | `intensity` (0-100) | Converted to percentage |
| `h.trigger_source` | `reason` | Added to history |
| `h.created_at` | `recorded_at` | Added to history |

### 1.2 Frontend Mood Types (`frontend/src/pages/AgentMoodPage.tsx`)

**Problem:** "All Moods" dropdown showed duplicates of "Neutral" because backend moods weren't in `MOOD_CONFIG`.

**Fix:** Added all backend mood types: calm, energetic, confident, playful, contemplative, curious, inspired, focused

### 1.3 Create/Delete Rule Functionality

- Fixed `moodApi.createRule` API signature to match backend
- Added Create Rule modal with full form
- Added Delete Rule button with hover effect

### 1.4 Data Backfill

- Updated all 73 agent mood timestamps to today
- Created mood history for 28 agents that had none (763 total records)

---

## Part 2: Time Capsules Deep Audit

### 2.1 API Endpoints Tested

| Endpoint | Method | Status |
|----------|--------|--------|
| `/api/time-capsules/` | GET | ✅ Working |
| `/api/time-capsules/<id>/` | GET | ✅ Working |
| `/api/time-capsules/ready-to-reveal/` | GET | ✅ Working |
| `/api/time-capsules/agent/<id>/` | GET | ✅ Working |
| `/api/time-capsules/<id>/reveal/` | POST | ✅ Working |
| `/api/time-capsules/<id>/react/` | POST | ✅ Working |
| `/api/time-capsules/generate/` | POST | ✅ Fixed |
| `/api/time-capsules/expire-old/` | POST | ✅ Working |

### 2.2 Critical Bug Found: GPT-5-mini Empty Content

**Problem:** 6 out of 8 capsules had empty message content.

**Root Cause:** GPT-5-mini is a reasoning model that uses tokens for internal reasoning before producing output. The `max_completion_tokens` was set too low:
- `generate_capsule_reflection()`: 200 tokens
- `GenerateTimeCapsuleView`: 300 tokens

With these limits, GPT-5-mini exhausted tokens during reasoning and returned empty content (`finish_reason: length`).

**Fix:** Increased both to 2000 tokens in `core/views_time_capsules.py`

```python
# Before (broken)
max_completion_tokens=200  # or 300

# After (fixed)
max_completion_tokens=2000  # Enough for reasoning + output
```

### 2.3 Frontend Fixes (`frontend/src/pages/TimeCapsulePage.tsx`)

**Problem:** Clicking on opened capsules showed nothing because overview data doesn't include message/reflection.

**Fix:**
1. Added `handleSelectCapsule()` that fetches detail for opened/ready capsules
2. Added `selectedCapsuleDetail` state for full capsule data
3. Added loading state while fetching
4. Shows "Message to Future Self", "Reflection Upon Opening", and "Then vs Now" comparison

### 2.4 Backend Fix (`core/views_time_capsules.py`)

**Problem:** `recent_revealed` response was missing `reveal_at` field (original scheduled date).

**Fix:** Added `reveal_at` to the `recent_revealed` serialization.

### 2.5 Data Cleanup

- Deleted 6 capsules with empty messages (created before fix)
- Verified new capsule generation works correctly

### 2.6 Final Capsule State

| Capsule | Agent | Status | Content |
|---------|-------|--------|---------|
| Midnight Jazz of Data and Images | ImageAgent | Sealed | ✅ 535 chars |
| Workflow Reflection | WorkflowAgent | Revealed | ✅ 44 chars + 431 char reflection |
| Test Capsule | ImageAgent | Revealed | ✅ 14 chars |

---

## Files Modified

| File | Changes |
|------|---------|
| `core/views_agent_mood.py` | API field mapping for frontend compatibility |
| `core/views_time_capsules.py` | Added `reveal_at` to response, fixed GPT-5-mini token limits |
| `frontend/src/lib/api.ts` | Fixed `createRule` signature |
| `frontend/src/pages/AgentMoodPage.tsx` | Added mood types, create modal, delete button |
| `frontend/src/pages/TimeCapsulePage.tsx` | Fetch detail on selection, show content panels |

---

## Commits

1. `705c5531` - fix(Session 749): Mood Page data display + create/delete rules
2. `f4d0c135` - docs(Session 749): Update session handoff file
3. `444bb5c9` - docs(Session 749): Add comprehensive handoff documentation
4. `29aa1141` - fix(Session 749): Time Capsules page - fetch detail on selection
5. `3d66d77a` - fix(Session 749): Time Capsules GPT-5-mini token limit

---

## GPT-5-mini Token Guidance

**Important:** When using GPT-5-mini (reasoning model), always use sufficient `max_completion_tokens`:

| Use Case | Recommended Tokens |
|----------|-------------------|
| Simple response (1-2 sentences) | 1500-2000 |
| Medium response (paragraph) | 2000-3000 |
| Complex analysis | 4000-6000 |

The model uses tokens for internal reasoning before producing visible output. Low token limits cause empty responses with `finish_reason: length`.

---

## Next Session

Session 750 can continue with:
- Other frontend page audits
- Additional sci-fi feature pages
- System integration improvements
