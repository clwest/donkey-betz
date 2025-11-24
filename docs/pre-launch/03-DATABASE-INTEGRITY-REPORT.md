# Database Integrity Report

**Audit Date:** November 24, 2025 - Session 178
**Auditor:** Pre-Launch Audit System
**Status:** In Progress

---

## Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| **Total Images** | 44 | - |
| **Total Videos** | 71 | - |
| **Total 3D Models** | 2 | - |
| **Orphaned Images** | 2 | Needs Attention |
| **Orphaned Videos** | 14 | Critical Issue |
| **Stuck Pending Videos** | 1 | Minor |
| **Broken Completed Videos** | 0 | Good |
| **Broken 3D Models** | 2 | Needs Investigation |
| **Data Integrity Score** | 76% | Needs Improvement |

---

## Detailed Findings

### 1. Orphaned Content (No Project Association)

#### Orphaned Images (2 records)
| ID | Prompt | Issue |
|----|--------|-------|
| `01081efb-9f2d-4b3e-8073-8024d71a9ce1` | "test" | Test data, no project |
| `329d6d69-aad6-41c1-99f7-f5feaba3e984` | "Frame extracted at 2.0s..." | Frame extraction orphan |

**Root Cause:**
- Test image created without project context
- Frame extraction feature doesn't properly associate with source video's project

**Impact:** Minor - Only 2 images (4.5% of total)

**Fix Required:**
1. Delete test image (cleanup)
2. Fix `extract_video_frame()` to inherit project from source video

---

#### Orphaned Videos (14 records) - CRITICAL

| ID | Prompt | Status | Created | Has URL |
|----|--------|--------|---------|---------|
| `3eaf2e72-...` | Talking character with lip sync | completed | 2025-11-24 19:06 | Yes |
| `354e437d-...` | Talking character with lip sync | completed | 2025-11-24 18:58 | Yes |
| `a29677f1-...` | Talking character with lip sync | completed | 2025-11-24 18:27 | Yes |
| `a365a3b2-...` | Talking character with lip sync | completed | 2025-11-24 18:21 | Yes |
| `2f09e1b0-...` | Talking character with lip sync | completed | 2025-11-24 18:20 | Yes |
| `f9244b3a-...` | subtle talking motion... | completed | 2025-11-24 18:16 | Yes |
| `a9b93bd0-...` | subtle talking motion... | completed | 2025-11-24 18:08 | Yes |
| `7f124175-...` | subtle talking motion... | failed | 2025-11-24 18:03 | No |
| `ca13a719-...` | subtle talking motion... | completed | 2025-11-24 18:00 | Yes |
| `85935d5d-...` | Concatenated 2 videos | completed | 2025-11-21 20:05 | Yes |
| `726857e9-...` | Speed 0.5x of video... | completed | 2025-11-21 20:02 | Yes |
| `f6af84eb-...` | Trimmed 0.0s-3.0s... | completed | 2025-11-21 19:50 | Yes |
| `f29edd5e-...` | Reversed version of video... | completed | 2025-11-21 19:46 | Yes |
| `cd892259-...` | Animated from image #31... | pending | 2025-11-21 13:48 | No |

**Root Cause Analysis:**
1. **Lip Sync Pipeline (9 videos):** Session 176-177 implementation didn't properly pass project_id through the talking character pipeline
2. **Video Enhancement Operations (4 videos):** Concatenate, speed, trim, reverse operations from Session 160-161 not associating with projects
3. **One Failed + One Pending:** Normal operation states, but still orphaned

**Impact:** Critical - 19.7% of all videos are orphaned (14/71)

**Fix Required:**
1. **Immediate:** Run cleanup script to associate orphaned videos with correct projects based on source video/image project
2. **Code Fix:** Update `talking_character_pipeline.py` to properly propagate project_id
3. **Code Fix:** Verify all video enhancement functions in `views_video.py` inherit project from source video

---

### 2. Video Status Distribution

| Status | Count | Percentage | Health |
|--------|-------|------------|--------|
| completed | 66 | 93.0% | Good |
| processing | 3 | 4.2% | Normal |
| pending | 1 | 1.4% | Check if stuck |
| failed | 1 | 1.4% | Expected |

**Analysis:**
- 3 videos in "processing" state - need to verify these are actively being processed
- 1 video "pending" for >24 hours - likely abandoned task, should be cleaned up or retried

---

### 3. Stuck Operations

#### Stuck Pending Videos (>24 hours): 1

| ID | Prompt | Created |
|----|--------|---------|
| `cd892259-...` | Animated from image #31 | 2025-11-21 13:48 |

**Analysis:**
- This is a Runway ML animation task from Nov 21 that never completed
- Likely API timeout or error that wasn't handled

**Fix Required:**
1. Check Runway ML task status via API
2. Either retry the task or mark as failed
3. Add better timeout handling for long-running tasks

---

### 4. Broken Completed Records

#### Completed Videos with No URL: 0
**Status:** Good - All completed videos have valid URLs

#### Completed 3D Models with No GLB: 2
**Analysis Needed:**
- Need to investigate which 3D models are missing GLB files
- May be records from before local file storage was implemented

---

### 5. 3D Model Status

| Status | Count |
|--------|-------|
| completed | 2 |

**Note:** Small sample size - only 2 3D models in database. Both show as "completed" but GLB file check shows 2 broken records. This is likely the same 2 records - need to verify if GLB files exist on disk.

---

## Production Blockers

### CRITICAL - Must Fix Before Launch

1. **Lip Sync Project Association Bug**
   - **Impact:** All lip-synced videos created in production will be orphaned
   - **Location:** `content/talking_character_pipeline.py`
   - **Fix Effort:** ~30 minutes
   - **Priority:** P0 - Launch Blocker

2. **Video Enhancement Project Inheritance**
   - **Impact:** Speed change, trim, reverse, concatenate operations don't inherit project
   - **Location:** `core/views_video.py`
   - **Fix Effort:** ~1 hour
   - **Priority:** P0 - Launch Blocker

### MEDIUM - Should Fix Before Launch

3. **Frame Extraction Project Association**
   - **Impact:** Extracted frames don't appear in correct project
   - **Location:** `core/views_video.py` - `extract_video_frame()`
   - **Fix Effort:** ~20 minutes
   - **Priority:** P1

4. **Stuck Task Cleanup**
   - **Impact:** Orphaned pending tasks waste resources
   - **Fix:** Add cleanup script to mark stale tasks as failed
   - **Fix Effort:** ~30 minutes
   - **Priority:** P1

### LOW - Can Fix After Launch

5. **Test Data Cleanup**
   - **Impact:** Minor - orphaned test images
   - **Fix:** Delete orphaned test records
   - **Fix Effort:** ~5 minutes
   - **Priority:** P2

---

## Recommended Cleanup Scripts

### Script 1: Fix Orphaned Lip Sync Videos

```python
# fix_orphaned_lipsync_videos.py
from content.models import VideoHistory

# Find orphaned lip sync videos
orphaned = VideoHistory.objects.filter(
    project__isnull=True,
    prompt__icontains='lip sync'
)

for video in orphaned:
    # Try to find source video from prompt
    # Associate with same project
    print(f"Would fix: {video.id}")
```

### Script 2: Fix Orphaned Video Enhancement Operations

```python
# fix_orphaned_video_ops.py
from content.models import VideoHistory
import re

operations = ['Speed', 'Trimmed', 'Reversed', 'Concatenated']

for op in operations:
    orphaned = VideoHistory.objects.filter(
        project__isnull=True,
        prompt__startswith=op
    )
    for video in orphaned:
        # Extract source video ID from prompt
        # Associate with same project as source
        pass
```

### Script 3: Cleanup Stale Pending Tasks

```python
# cleanup_stale_tasks.py
from content.models import VideoHistory
from django.utils import timezone
from datetime import timedelta

stale = VideoHistory.objects.filter(
    status='pending',
    created_at__lt=timezone.now() - timedelta(hours=24)
)

for video in stale:
    video.status = 'failed'
    video.save()
    print(f"Marked {video.id} as failed")
```

---

## Summary

| Category | Score | Notes |
|----------|-------|-------|
| Image Data Integrity | 95% | Only 2 orphaned test/extracted images |
| Video Data Integrity | 80% | 14 orphaned videos, 1 stuck task |
| 3D Model Integrity | 50% | Need to verify GLB files exist |
| **Overall Data Integrity** | **76%** | Needs improvement before launch |

### Action Items for Session 178

1. [ ] Run orphaned video analysis to find source projects
2. [ ] Fix `talking_character_pipeline.py` project association
3. [ ] Fix video enhancement operations in `views_video.py`
4. [ ] Verify 3D model GLB files exist on disk
5. [ ] Mark stale pending video as failed

---

**Next Update:** After fixes are implemented
**Target Score:** 95%+ data integrity before launch
