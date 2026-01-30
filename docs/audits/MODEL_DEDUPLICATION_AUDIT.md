# Model Deduplication Audit Report

**Date:** January 29, 2026
**Session:** 870
**Status:** ANALYSIS COMPLETE - MIGRATION PENDING

---

## Executive Summary

Analysis of `models_unified_system.py` (20,600 lines, 281 models) identified significant deduplication opportunities:

| Category | Count | Impact |
|----------|-------|--------|
| Exact Duplicates | 2 | HIGH - Must consolidate |
| Overlapping Models | 15+ | MEDIUM - Can consolidate |
| Under-utilized Models | 10+ | LOW - Monitor usage |
| Profile Fragmentation | 5 classes | HIGH - Should consolidate |

**Estimated Savings:** ~40 model classes, ~3,100 lines of code, 14% fewer database tables

---

## 1. CRITICAL: Exact Duplicates

### 1.1 UserAgentLearning (DUAL DEFINITION)

**Location 1:** `core/models.py:2651` (10 learning_domain choices)
**Location 2:** `core/models_unified_system.py:3339` (20+ learning_domain choices)

**Import Distribution:**
- `from core.models import UserAgentLearning` - 12 files
- `from core.models_unified_system import UserAgentLearning` - 20+ files

**Differences:**
| Field | models.py | models_unified_system.py |
|-------|-----------|-------------------------|
| learning_domain choices | 10 | 20+ (includes sports betting, partnerships) |
| failure_count | ✓ | ✓ |
| success_rate | ✓ | ✓ |

**Recommendation:** Keep `models_unified_system.py` version (more complete), deprecate `models.py` version.

**Migration Files to Update:**
```
core/management/commands/discover_learning_cohorts.py
core/learning_dashboard_consumer.py (5 imports)
core/revenue_opportunities_consumer.py (4 imports)
core/unified_learning_pipeline.py
revenue/models.py
```

---

### 1.2 Revenue (DUAL IMPLEMENTATION)

**Location 1:** `core/models.py:2504` - Inherits `UnifiedBaseModel`, broader source choices
**Location 2:** `core/models_unified_system.py:663` - Extends `models.Model`, simpler sources

**Source Choices Comparison:**
| models.py | models_unified_system.py |
|-----------|-------------------------|
| quick_apply | job |
| freelance | gig |
| consulting | investment |
| trading | - |
| sports_betting | - |
| affiliate | - |

**Recommendation:** Merge choices into single comprehensive model in `models.py`.

---

## 2. HIGH PRIORITY: A/B Testing Duplication

Two parallel A/B testing systems exist:

### ABExperiment System (older)
```
ABExperiment (unified_system:4576) - 2 file references
ABVariant (unified_system:4656) - 2 file references
```

### ABTest System (newer, more used)
```
ABTest (unified_system:7885) - 7 file references
ABTestVariant (unified_system:8051) - 1 file
ABTestEvent (unified_system:8107) - 1 file
```

**Recommendation:** Deprecate ABExperiment, migrate to ABTest (more feature-rich).

---

## 3. HIGH PRIORITY: User Profile Fragmentation

5 different user profile classes across files:

| Class | File | Purpose |
|-------|------|---------|
| `UserProfile` | models.py:552 | Basic: avatar, bio, job prefs |
| `ExtendedUserProfile` | models.py:807 | Inherits UnifiedBaseModel |
| `EnhancedUserProfile` | models.py:1600 | Comprehensive personalization |
| `UserPreferenceProfile` | unified_system:4315 | Style/model preferences |
| `UserLearningProfile` | unified_system:7168 | Learning journey tracking |

**Recommendation:**
1. Consolidate `UserProfile` + `ExtendedUserProfile` + `EnhancedUserProfile` → `UnifiedUserProfile`
2. Keep `UserPreferenceProfile` and `UserLearningProfile` as specialized tables with FK

---

## 4. MEDIUM PRIORITY: Prediction Models

7 prediction-related models with overlap:

| Model | Line | Recommendation |
|-------|------|----------------|
| `AgentPrediction` | 13230 | KEEP - Base model (460+ lines) |
| `PredictionStats` | 13554 | KEEP |
| `PredictionOutcome` | 17958 | KEEP |
| `PredictionComment` | 13746 | MERGE with `PredictionFollowUp` |
| `PredictionFollowUp` | 13809 | MERGE → `PredictionFeedback` |
| `OpportunityPredictionAccuracy` | 2382 | DEPRECATE - use `OpportunityScore` |
| `ContentPerformancePrediction` | 6983 | KEEP - content-specific |

---

## 5. MEDIUM PRIORITY: Learning Models

7 learning-related models:

| Model | Line | Recommendation |
|-------|------|----------------|
| `AgentLearning` | 3097 | KEEP - Base |
| `UserAgentLearning` | 3339 | KEEP - User-specific |
| `AgentLearningConnection` | 292 | KEEP - Links agents to sources |
| `UserLearningProfile` | 7168 | KEEP - For learning journey |
| `LearningPattern` | 14286 | MERGE into `AgentLearning` as JSONField |
| `LearningCompanion` | 14500 | DEPRECATE - low usage |
| `LearningProgress` | 14591 | DEPRECATE - covered by others |

---

## 6. MEDIUM PRIORITY: Memory/Consciousness Models

18 models forming consciousness system. Consolidation recommendations:

### Keep As-Is
- `AgentMemory` (10120)
- `MemoryPalaceRoom` (10636)
- `AgentPersonality` (12814)

### Merge Candidates
- `MemoryConnection` + `MemoryCluster` + `ClusterEvolution` → Hierarchical structure
- `AgentMood` + `MoodHistory` → Single model with history tracking
- `AgentRelationship` + `RelationshipEvent` + `Alliance` + `Rivalry` → Single `AgentRelationship` with type field

---

## 7. LOW PRIORITY: Potentially Unused Models

| Model | Line | References | Action |
|-------|------|------------|--------|
| `OpportunityContent` | 2282 | 2 | Review usage |
| `DreamExploration` | 9761 | 2 | Merge with `AgentDream` |
| `ReplayBookmark` | 12719 | 4 | Consider deprecating |
| `DebugAnnotation` | 12773 | 4 | Remove if debug-only |

---

## 8. Migration Roadmap

### Phase 1: Documentation & Deprecation (Current Session)
- [x] Create this audit report
- [ ] Add deprecation comments to duplicate models
- [ ] Document canonical import locations

### Phase 2: Critical Duplicates (Next Session)
- [ ] Create data migration for UserAgentLearning
- [ ] Update 12 import statements in core/models.py users
- [ ] Create data migration for Revenue model

### Phase 3: A/B Testing Consolidation
- [ ] Migrate ABExperiment usage to ABTest
- [ ] Create deprecation migration

### Phase 4: Profile Consolidation
- [ ] Design unified profile schema
- [ ] Create migration plan
- [ ] Implement with backward compatibility

### Phase 5: Learning & Prediction Cleanup
- [ ] Merge prediction feedback models
- [ ] Consolidate learning models

### Phase 6: Memory System Consolidation
- [ ] Design consolidated memory schema
- [ ] Create phased migration

---

## 9. Risk Assessment

| Action | Risk | Mitigation |
|--------|------|------------|
| Remove UserAgentLearning from models.py | HIGH | Update all 12 imports first |
| Merge Revenue models | MEDIUM | Ensure all source choices preserved |
| Deprecate ABExperiment | LOW | ABTest already dominant |
| Profile consolidation | HIGH | Requires careful FK management |
| Memory consolidation | HIGH | Complex relationships |

---

## 10. Files Requiring Updates

### UserAgentLearning Migration
```
core/management/commands/discover_learning_cohorts.py
core/learning_dashboard_consumer.py
core/revenue_opportunities_consumer.py
core/unified_learning_pipeline.py
revenue/models.py
```

### A/B Testing Migration
```
core/services/ab_testing.py
core/views_ab_testing.py
```

### Profile Migration
```
core/agents/personal_assistant_agent.py
core/services/user_context_service.py
core/views_user_profile.py
```

---

## Appendix: Model Count by Category

| Category | Count |
|----------|-------|
| Agent/AI Models | 45 |
| User/Profile Models | 12 |
| Content Models | 28 |
| Learning Models | 15 |
| Memory/Consciousness | 18 |
| Opportunity/Revenue | 14 |
| A/B Testing | 5 |
| Workflow | 9 |
| Spider/Data | 8 |
| Analytics | 12 |
| Other | ~115 |
| **Total** | **281** |

---

*Audit completed by Claude Code - Session 870*
