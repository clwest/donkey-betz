# Session 944 - Start Here

**Previous Session:** 943 (Stage Distribution Fix + Stale Investigation)
**Date:** February 5, 2026
**Status:** 76 Agents | 77 Spiders (ALL MAPPED) | 25 Advisors | 139 Personas | **373 INITIATIVES** | **Unified PA: FULL STACK** | **Voice System: COMPLETE** | **User Learning UI: COMPLETE** | **Spider Context: EXTENDED** | **Boardroom Tab: LIVE** | **PA Boardroom: COMPLETE** | **Boardroom Learning: ACTIVE** | **Auto-Approve: SCHEDULED** | **Experiment Cleanup: SCHEDULED** | **Bulk Actions: COMPLETE** | **Stage Distribution: FIXED**

---

## Session 943 Summary (Just Completed)

### Stage Distribution Bug Fix (PR #876)

Fixed the Pipeline Health UI showing incorrect stage distribution numbers:

**Problem:** All 5 stages displayed "436" - the total count of active initiatives. This was because the code counted all `InitiativeStage` records for each stage, but every initiative has 5 stage entries (one per stage), so all stages showed the same total.

**Fix:** Changed the query to count initiatives by their `current_stage` field:
- **Before:** Count all stage entries for stage N (showed total initiatives)
- **After:** Count initiatives WHERE `current_stage == N` (shows initiatives AT that stage)

| Stage | Old Display | New Display |
|-------|-------------|-------------|
| Stage 1 | 436 (all initiatives) | X (initiatives currently at Stage 1) |
| Stage 2 | 436 (all initiatives) | Y (initiatives currently at Stage 2) |
| etc. | ... | ... |

**Files Changed:**
- `core/views_initiative_kickstart.py` - Fixed `pipeline_health()` query
- `frontend/src/pages/workspace/tabs/InitiativesTab.tsx` - Use `count` field

### Stale Initiatives Investigation

The "Critical" warning showing 236 stale initiatives (54% with no activity in 48+ hours) is legitimate - the pipeline has many initiatives that aren't progressing. This is a real system health concern, not a display bug.

**Recommendations:**
- Use the cleanup API to archive truly abandoned initiatives
- Consider reducing the stale threshold or adjusting the warning levels

---

## PRIORITY OPTIONS FOR NEXT SESSION

### Option A: Learning Loop Backend (General)
Define success signals across the platform:
- Track tool execution outcomes
- Weight recent performance
- Inject learnings into prompts

### Option B: Spider Context for Remaining Paths
Extend SpiderContextBuilder to:
- `creative_orchestrator.py` (13 locations)
- `research_orchestrator.py` (5 locations)
- Other content generation tasks

### Option C: Boardroom ML Improvements
Improve ML recommendations for boardroom items:
- Train on actual user decisions
- Better confidence scoring
- Recommendations based on item content, not just type

### Option D: ConceptForge Pipeline Improvements
Address issues from prior panel/advisor system plan:
- Fix placeholder leakage ("[Learned] target")
- Dedupe repeated DecisionSummary blocks
- Add provenance headers to panel results

### Option E: Stale Initiative Cleanup
Address the 236 stale initiatives:
- Create automated cleanup for initiatives with no activity in X days
- Add "archive stale" scheduled task
- Investigate why so many initiatives are stalled

---

## Recent Session History

| Session | Focus | PRs |
|---------|-------|-----|
| **943** | Stage Distribution Fix + Stale Investigation | #876 |
| **942** | Integrity Anomaly Investigation + Halted Experiment Cleanup + Bulk Boardroom Actions | #874, #875 |
| **941** | Boardroom Auto-Approve Scheduled | #871 |
| **940** | PA Boardroom Complete (Awareness + Tools + Triage + Learning) | #866-#869 |
| **939** | Boardroom Tab + Cleanup Automation | #862-#864 |
| **937** | Content Quality Verification + Spider Fixes | #855, #857 |

---

## Key Files Reference

### Stage Distribution Fix (Session 943)
| File | Purpose |
|------|---------|
| `core/views_initiative_kickstart.py` | `pipeline_health()` endpoint - fixed stage distribution query |
| `frontend/src/pages/workspace/tabs/InitiativesTab.tsx` | Stage distribution UI display |

### Boardroom System (Session 940-942)
| File | Purpose |
|------|---------|
| `core/views_human_interface.py` | `BulkAttentionDecideView` for bulk actions |
| `core/views_agent_learning.py` | `bulk_promote_decisions`, `bulk_reject_decisions` |
| `frontend/src/pages/workspace/tabs/BoardroomTab.tsx` | Boardroom UI with bulk selection |
| `frontend/src/lib/api.ts` | `bulkDecide`, `bulkPromote`, `bulkReject` methods |
| `core/tasks.py` | `auto_approve_boardroom_items`, `cleanup_boardroom_junk`, `cleanup_halted_experiments` |
| `core/settings.py` | Celery Beat schedule |

### Experiment System
| File | Purpose |
|------|---------|
| `core/models_pilot_readiness.py` | Experiment model (is_halted, halt_reason) |
| `core/services/experiment_metrics.py` | `_detect_integrity_anomaly()` |

### Boardroom Models
| File | Model |
|------|-------|
| `core/models_human_interface.py` | HumanAttentionItem |
| `core/models_unified_system.py` | AgentDecisionSummary, LearningPattern |

---

**Session 944 Focus: Choose priority option above and continue building!**
