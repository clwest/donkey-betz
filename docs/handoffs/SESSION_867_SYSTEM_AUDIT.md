---
originating_session: 867
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 867 - System-Wide Audit Report

**Date:** January 29, 2026
**Purpose:** Comprehensive platform audit to identify disconnected features, incomplete implementations, and integration gaps

---

## Executive Summary

Conducted full audit of unified-donkey-betz platform. Found **significant gaps** between defined capabilities and actual implementations:

| Metric | Count | Issue |
|--------|-------|-------|
| Celery Tasks Defined | 291 | Only ~60 scheduled in beat_schedule |
| Frontend Stub Endpoints | 40+ | Placeholders returning fake success |
| Disabled UI Features | 3+ | Explicitly disabled with TODOs |
| Orphaned Systems | 2 | Built but not integrated |

---

## TIER 1: Critical Gaps (Block User Workflows)

### 1.1 Celery Beat Task Scheduling Chaos

**Problem:** 291 tasks defined in `core/tasks.py` but only ~60 in `app.conf.beat_schedule`

**Impact:** HIGH - System cannot self-heal, auto-advance pipelines, or run autonomous operations

**Missing Critical Tasks:**
```python
# Initiative Pipeline (LINE 30642)
advance_initiative_pipeline()  # NOT SCHEDULED

# ConceptForge Pipeline (LINE 30340)
run_conceptforge_pipeline()    # NOT SCHEDULED
promote_to_conceptforge()      # NOT SCHEDULED
run_conceptforge_stage()       # NOT SCHEDULED

# Spider Aggregation (LINE 30323)
compute_spider_aggregations()  # NOT SCHEDULED
invalidate_spider_aggregations()  # NOT SCHEDULED

# Agent Health (LINE 29323)
run_agent_health_rotation()    # NOT SCHEDULED

# Diagnostic Pipeline
discover_and_import_audits()   # NOT SCHEDULED
assign_open_findings_to_agents()  # NOT SCHEDULED
execute_remediation_tasks()    # NOT SCHEDULED

# Video Processing
poll_processing_videos()       # NOT SCHEDULED

# Agent Groups (8+ tasks)
run_narrative_culture_agents()
run_development_tech_agents()
run_executive_leadership_agents()
run_podcast_debate_agents()
run_content_studio_agents()
```

**Fix:** Create comprehensive beat_schedule entries or management command to register all autonomous tasks

**Files:**
- `core/tasks.py` (291 tasks, lines 1-30840+)
- `core/celery.py` (beat_schedule definition)

---

### 1.2 Gallery Series Endpoint Missing

**Problem:** Frontend explicitly disables AI Series feature

**Location:** `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx:138-147`

```typescript
// Session 860: Disabled - endpoint /api/v1/gallery/series/ doesn't exist yet
const { data: seriesData } = useQuery({
  queryKey: ['gallery-series'],
  queryFn: async () => {
    return { results: [], count: 0 }  // HARDCODED EMPTY
  },
  enabled: false,  // DISABLED
})
```

**Impact:** HIGH - Users cannot see AI-generated series content (podcasts, video series)

**Fix:** Create `/api/v1/gallery/series/` endpoint or wire to existing `/api/sessions/list/`

**Estimated Effort:** 1-2 hours

---

### 1.3 Reasoning Endpoints Broken

**Problem:** Intelligence tab calls endpoints that may not exist

**Location:** `frontend/src/pages/workspace/tabs/IntelligenceTab.tsx:100-145`

```typescript
// These fetch calls have no error handling and silently fail
fetch('/api/v1/reasoning/thoughts/')
fetch('/api/v1/reasoning/actions/')
fetch('/api/v1/reasoning/gates/')
```

**Impact:** MEDIUM-HIGH - Intelligence tab reasoning features non-functional

**Fix:**
1. Verify endpoints exist in `core/views*.py`
2. If missing, create endpoints
3. If paths different, fix frontend paths
4. Add proper error handling

---

### 1.4 Podcast TTS Integration Incomplete

**Problem:** Session 865 added backend but frontend wiring unclear

**Modified Files (in git status):**
- `core/services/podcast_audio_service.py`
- `core/views_podcast.py`
- `frontend/src/pages/workspace/tabs/ContentStudioTab.tsx`

**API Endpoint:** `podcast_generate_audio_view` exists

**Impact:** MEDIUM-HIGH - Core podcast TTS feature may not work end-to-end

**Fix:** Verify frontend properly calls TTS generation API and handles audio playback

---

## TIER 2: High Priority (Missing Key Features)

### 2.1 ATS UI Not Built (Backend Complete)

**Problem:** Session 866 built complete backend but no frontend UI

**Backend Complete:**
- `ATSKeywordService` (590+ lines)
- 4 Django Models: `PersonaResumeTemplate`, `ATSKeywordMapping`, `ResumeOptimizationLog`, `ResumeRewriteOrder`
- 6 API Endpoints ready

**API Endpoints:**
```
POST /api/ats/analyze/
POST /api/ats/extract-keywords/
POST /api/ats/optimize/
GET  /api/ats/templates/
POST /api/ats/generate-summary/
GET  /api/ats/stats/
```

**Missing:** Career Tab UI to consume these APIs

**Impact:** MEDIUM - Complete feature sitting unused

**Fix:** Build ATS score display + optimization panel in CareerTab.tsx

**Estimated Effort:** 2-3 hours

---

### 2.2 Frontend Stub Endpoints (40+)

**Problem:** `views_frontend_stubs.py` contains 40+ placeholder endpoints

**Location:** `core/views_frontend_stubs.py`

**Stubbed Features:**
- `stripe_plans()` - Returns fake plan data
- `stripe_payment_methods()` - Returns empty array
- `stripe_add_payment_method()` - Returns fake success
- Various intelligence endpoints
- Various infrastructure endpoints

**Impact:** MEDIUM - Features appear to work but actually don't

**Fix:** Implement real endpoints or remove stubs and disable UI features

---

### 2.3 Voice Marketplace Orphaned

**Problem:** Complete system built but not integrated

**Files:**
- `core/models_voice_marketplace.py` (4 models)
- `core/views_voice_marketplace.py` (API endpoints)
- `core/views_stripe_voice.py` (payment handling)

**Missing:** No workspace tab or UI integration

**Impact:** LOW-MEDIUM - Feature exists but users can't access it

**Fix:** Add Voice Marketplace tab or integrate into existing Content Studio

---

## TIER 3: Medium Priority (Data Flow & Quality)

### 3.1 Dream to Initiative Pipeline Unclear

**Problem:** Pipeline exists but user flow not obvious

**What Exists:**
- Full FK traceability (Session 862)
- Dream model
- Initiative model with 5 stages
- Deliverable model

**Gap:**
- How do Dreams trigger Initiatives? (automatic vs manual)
- No clear UI workflow for Dream → Initiative creation
- Deliverable creation from stages not visible

**Fix:** Document workflow and/or add UI for manual triggering

---

### 3.2 ConceptForge Artifact Interaction

**Problem:** Can view artifacts but can't interact with them

**What Works:**
- `ConceptForgeTab.tsx` shows runs/stages/artifacts
- Backend pipeline (6 stages) complete

**Gap:** No buttons to approve/reject/edit artifacts

**Fix:** Add interaction UI to ConceptForge artifacts

---

### 3.3 Learning Journey Dashboard

**Problem:** Feature exists but not properly surfaced

**What Exists:**
- Models: `LearningJourney`, `LearningTemplate`, `LearningStep`
- API: `views_learning_journey_api.py` (16+ endpoints)

**Gap:** No visible dashboard in workspace tabs

**Fix:** Add Learning Journey section to Career tab or new tab

---

### 3.4 Mock Data Fallbacks in Frontend

**Problem:** Silent failures instead of user feedback

**Locations:**
```typescript
// ContentStudioTab.tsx (Lines 129, 144)
return { results: [], count: 0 }  // Silent failure

// IntelligenceTab.tsx (Lines 116, 120)
return { results: [], count: 0 }  // Silent failure

// AIConsciousnessTab.tsx (Lines 1614, 1616)
return { results: [], count: 0 }  // Silent failure
```

**Fix:** Add proper error states and user messaging

---

## TIER 4: Lower Priority (Technical Debt)

### 4.1 Model Duplication & Dead Code

**Problem:** 181 models in `core/models_unified_system.py`

**Other Model Files with Unclear Usage:**
- `models_voice_marketplace.py` (4 models)
- `models_synthetic_users.py` (2 models)
- `models_odds_history.py` (2 models)
- `models_research.py` (1 model)
- `models_ai_series.py` (3 models)

**Fix:** Audit which models are actively used vs historical

---

### 4.2 API Path Inconsistencies

**Problem:** Mixed path patterns make discovery hard

**Examples:**
- `/api/v1/` - Standard versioned
- `/api/` - Unversioned
- `/v1/` - Missing api prefix
- `/podcasts/` - Direct resource
- `/reasoning/` - Direct resource

**Fix:** Document and standardize naming conventions

---

## Implementation Checklist

### Quick Wins (1-2 hours each)
- [ ] Create `/api/v1/gallery/series/` endpoint
- [ ] Fix reasoning endpoint paths in IntelligenceTab
- [ ] Register `advance_initiative_pipeline` in beat_schedule (DONE in Session 866)
- [ ] Schedule `run_conceptforge_pipeline` task
- [ ] Schedule `compute_spider_aggregations` task

### Medium Tasks (2-4 hours each)
- [ ] Build ATS UI in CareerTab (backend ready)
- [ ] Complete podcast TTS frontend integration
- [ ] Add ConceptForge artifact interaction buttons
- [ ] Add proper error states to frontend fallbacks

### Larger Tasks (4+ hours each)
- [ ] Audit and schedule all 231 missing Celery tasks
- [ ] Replace 40+ stub endpoints with real implementations
- [ ] Integrate Voice Marketplace into workspace
- [ ] Model deduplication audit

---

## Files Reference

### Critical Files Needing Attention
```
core/tasks.py                    # 291 tasks, ~60 scheduled
core/celery.py                   # beat_schedule needs expansion
core/views_frontend_stubs.py     # 40+ placeholder endpoints
frontend/src/pages/workspace/tabs/ContentStudioTab.tsx  # Disabled features
frontend/src/pages/workspace/tabs/IntelligenceTab.tsx   # Broken endpoints
frontend/src/pages/workspace/tabs/CareerTab.tsx         # Needs ATS UI
```

### Recently Modified (Verify Complete)
```
core/services/podcast_audio_service.py  # Session 865
core/views_podcast.py                    # Session 865
core/models_ats_optimization.py          # Session 866
core/views_ats_optimization.py           # Session 866
```

---

## Session 867 Accomplishments

1. **Cleaned up stuck executions** - 68 AgentExecutions marked failed, then deleted
2. **Fixed Initiative Pipeline** - Removed invalid `priority` field, added document viewer modal
3. **Created cleanup command enhancement** - `--delete-cleaned` option added
4. **Conducted system-wide audit** - Identified all gaps documented above

---

## Recommended Session 868 Focus

**Primary Goal:** Resolve Tier 1 critical gaps

1. **Schedule missing Celery tasks** - Create management command to register all autonomous tasks
2. **Create Gallery Series endpoint** - Unblock Content Studio AI Series feature
3. **Fix Intelligence tab endpoints** - Verify/create reasoning API paths
4. **Build ATS UI** - Consume ready backend in Career tab

**Secondary Goal:** Address Tier 2 items as time permits

---

*Audit conducted by Claude Code - Session 867*
