# Session 446: AISeriesWorkflowAgent Database Persistence Fixes

**Date:** December 14, 2025
**Status:** COMPLETE
**Focus:** Fix database persistence for scripts, episodes, and results

---

## Summary

Fixed critical bugs in `AISeriesWorkflowAgent` where generated content was not being saved to the database. Episodes were showing as "failed" with empty scripts due to UUID serialization errors and missing save calls.

---

## Issues Fixed

### 1. Scripts Not Saving (0 chars)

**Problem:** Episode scripts were generated but never persisted to the database.

**Root Cause:** The `complete_generation()` method on SeriesEpisode only saves status fields (`status`, `generation_completed_at`, `content_package`, `updated_at`), not content fields like `script`.

**Fix:** Added explicit `save(update_fields=[...])` call BEFORE `complete_generation()`:

```python
# Save all fields BEFORE calling complete_generation()
db_episode.save(update_fields=[
    'script', 'script_result', 'character_result',
    'voice_result', 'video_result', 'updated_at'
])
db_episode.complete_generation()  # Only saves status fields
```

### 2. UUID Serialization Error

**Problem:** Episodes failing with "Object of type UUID is not JSON serializable" at save stage.

**Root Cause:** ImageAgent and other agents return data containing UUIDs which can't be directly stored in Django JSONFields.

**Fix:** Added `make_json_serializable()` helper function that recursively converts UUIDs and Decimals:

```python
def make_json_serializable(obj):
    """Convert UUIDs, Decimals, and nested structures to JSON-safe types."""
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    return obj
```

Applied to all result fields before saving:
```python
db_episode.script_result = make_json_serializable(script_result)
db_episode.character_result = make_json_serializable(character_result)
db_episode.voice_result = make_json_serializable(voice_result_data)
db_episode.video_result = make_json_serializable(video_result_data)
```

### 3. Series ID Tracking

**Problem:** Tool handlers couldn't access the current series to save data.

**Fix:** Added `self._series_id` instance variable set after series creation:

```python
self._series_id = str(series.id)  # Track for DB updates in tool handlers
```

---

## Test Results

| Metric | Before | After |
|--------|--------|-------|
| Script length | 0 chars | 1151 chars |
| Episode status | failed | complete |
| Error message | "UUID is not JSON serializable" | None |
| Series status | complete | complete |
| Style Config | True | True |

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/ai_series_workflow_agent.py` | Added `make_json_serializable()` helper, `self._series_id` tracking, explicit `save()` before `complete_generation()`, added logging |

---

## Code Changes Detail

### 1. New Helper Function (lines 42-57)

```python
def make_json_serializable(obj):
    """
    Convert an object to be JSON serializable.
    Handles UUIDs, Decimals, and nested structures.
    """
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(make_json_serializable(item) for item in obj)
    return obj
```

### 2. Series ID Tracking (line 277, 320, 353)

```python
self._series_id = None  # Track current series for DB updates
# ...
self._series_id = str(series.id)  # Set after series creation
```

### 3. Episode Save Fix (lines 836-848)

```python
# Convert results to be JSON serializable (handles UUIDs, Decimals, etc.)
db_episode.script_result = make_json_serializable(script_result)
db_episode.character_result = make_json_serializable(character_result)
db_episode.voice_result = make_json_serializable(voice_result_data)
db_episode.video_result = make_json_serializable(video_result_data)
# IMPORTANT: Save all fields BEFORE calling complete_generation()
db_episode.save(update_fields=[
    'script', 'script_result', 'character_result',
    'voice_result', 'video_result', 'updated_at'
])
db_episode.complete_generation()  # Sets status to COMPLETE
```

---

## Verification

```bash
# Test series generation
Series: A 1-episode series about dinosaurs for kids
Status: complete
Style Config: True
Characters: 1

Episode 1: Toby's Friendly Roar
  Status: complete
  Script: 1151 chars
  character_result: False  # Expected - no Stability AI credits
  Error: None
```

---

## Lessons Learned

1. **Django JSONField + UUIDs:** Always convert UUIDs to strings before saving to JSONFields
2. **Model save methods:** Custom state machine methods may not save all fields - verify what `update_fields` are included
3. **Order of operations:** Save content fields BEFORE calling status update methods

---

## Related Sessions

- **Session 445:** AISeriesWorkflowAgent initial implementation
- **Session 444:** Voice Chat (Whisper Integration)
