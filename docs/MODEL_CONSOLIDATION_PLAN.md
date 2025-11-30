# Model Consolidation Plan

**Generated:** November 29, 2025 (Session 287)
**Part of:** HANDOFF_04 - Database Model Consolidation

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total Models Found | **160** |
| Models with Data | **10** (core models) |
| Empty Tables | **150** |
| Duplicate Model Names | **2** (AgentExecution, WorkflowExecution) |
| Tables with Missing Migrations | **31** (sports, self_awareness, etc.) |

### Key Findings

1. **Only ~10 models have significant data** - the rest are empty or unused
2. **150 empty tables** - massive cleanup opportunity
3. **31 models have no tables** - apps were removed but models remain in code
4. **2 duplicate model names** in different files (potential conflicts)

---

## Models with Data (KEEP)

These models have records and are actively used:

| Model | Records | Location |
|-------|---------|----------|
| `core.SpiderData` | 4,909 | core/models_unified_system.py |
| `core.ConversationMessage` | 2,500 | core/models_unified_system.py |
| `core.AgentKnowledgeSource` | 695 | core/models_unified_system.py |
| `core.UserMemoryContext` | 610 | core/models_unified_system.py |
| `core.ConversationMemory` | 578 | core/models_unified_system.py |
| `core.ChatConversation` | 578 | core/models_unified_system.py |
| `core.AgentDream` | 510 | core/models_unified_system.py (DEPRECATED) |
| `core.AgentConversation` | 419 | core/models_unified_system.py (DEPRECATED) |
| `core.AgentRelationship` | 380 | core/models_unified_system.py |
| `content.CharacterTrainingImage` | 178 | content/models.py |
| `content.ImageHistory` | 71 | content/models.py |
| `core.AgentSpiderConnection` | 57 | core/models_unified_system.py |
| `content.ContentAnalytics` | 54 | content/models.py |
| `agents.AgentContribution` | 48 | agents/models.py |
| `style_memory.StyleMemory` | 40 | style_memory/models.py |
| `core.AgentLearningConnection` | 37 | core/models_unified_system.py |
| `core.ThoughtBubble` | 34 | core/models_unified_system.py |
| `core.KnowledgeTransfer` | 32 | core/models_unified_system.py |
| `agents.UnifiedAgentTemplate` | 28 | agents/models.py |
| `content.CharacterModel` | 27 | content/models.py |
| `core.AgentMood` | 21 | core/models_unified_system.py |

---

## Empty Tables (150 - Review for Removal)

### Already Deprecated (from HANDOFF_03)
- `core.AgentDream` - 510 records but DEPRECATED
- `core.AgentConversation` - 419 records but DEPRECATED
- `core.AgentPrediction` - 0 records, DEPRECATED
- `core.TimeCapsule` - 0 records, DEPRECATED
- `core.MemoryCluster` - 0 records, DEPRECATED
- `core.Alliance` - 0 records, DEPRECATED
- `core.Rivalry` - 0 records, DEPRECATED

### Unused Sci-Fi Features (0 records)
- `core.ClusterEvolution`
- `core.DebugAnnotation`
- `core.LevelMilestone`
- `core.MemoryClusterMembership`
- `core.MemoryConnection`
- `core.MoodTriggerRule`
- `core.PredictionComment`
- `core.PredictionFollowUp`
- `core.PredictionStats`
- `core.RelationshipEvent`
- `core.ReplayBookmark`
- `core.TimeCapsuleReaction`

### Unused Revenue/Distribution (0 records)
- `core.Revenue`
- `core.ContentDistribution`
- `core.ContentPerformancePrediction`
- `core.DistributionAnalytics`
- `core.DistributionInsight`
- `core.DistributionRecommendation`
- `core.PricingOptimization`
- `core.SuccessPattern`

### Unused A/B Testing (0 records)
- `core.ABAssignment`
- `core.ABConversion`
- `core.ABExperiment`
- `core.ABExperimentResult`
- `core.ABTest`
- `core.ABTestEvent`
- `core.ABTestVariant`
- `core.ABVariant`

### Unused Proactive System (0 records)
- `core.ProactiveAlert`
- `core.ProactiveNotification`
- `core.SmartSuggestion`
- `core.AutomatedAction`
- `core.AutomatedActionLog`

### Unused Analytics (0 records)
- `core.AnalyticsAlert`
- `core.AnalyticsDashboard`
- `core.CostTracking`
- `core.PerformanceComparison`
- `core.PerformanceLog`
- `core.UsageMetric`

### Unused Collaboration (0 records)
- `core.Collaboration`
- `core.CollaborationSession`
- `core.InterAgentMessage`
- `core.SharedKnowledge`
- `core.SharedProject`
- `core.ProjectActivity`
- `core.ProjectCollaborator`
- `core.ProjectComment`
- `core.ProjectPresence`

### Unused Workflows (0 records)
- `core.CustomWorkflow`
- `core.CustomWorkflowStep`
- `core.ScheduledWorkflow`
- `core.WorkflowExecution`
- `core.WorkflowInstallation`
- `core.WorkflowReview`
- `core.PublishedWorkflow`

### Unused Agent Features (0 records)
- `core.AgentExecution` (duplicate name!)
- `core.AgentLearning`
- `core.AgentMessage`
- `core.AgentPerformanceMetric`
- `core.AgentSolution`
- `core.AgentTeamMembership`
- `core.AgentAssignment`
- `core.AgentCollaboration`
- `core.AgentQueryPerformance`

### Unused Content Features (0 records)
- `content.ContentTemplate`
- `content.ContentWorkflow`
- `content.Feedback`
- `content.KnowledgeBase`
- `content.ProjectWorkflow`
- `content.WorkflowExecution`
- `content.WorkflowFavorite`

### Agents Module (0 records)
- `agents.AgentChannel` - 1 record
- `agents.AgentChannelMembership`
- `agents.AgentChannelMessage`
- `agents.AgentOrchestration`
- `agents.AgentPerformanceMetrics`
- `agents.AgentTool`

---

## Missing Tables (31 - Remove from Code)

These apps were removed but models remain in code:

### sports app (14 models) - Remove
- `League`, `Team`, `Game`, `Sportsbook`, `BettingMarket`
- `OddsLine`, `LineMovement`, `Bet`, `BankrollManagement`
- `ArbitrageOpportunity`, `BettingRecommendation`, `SportsAnalytics`
- `MLPrediction`, `UserBet`

### self_awareness app (6 models) - Remove
- `SystemMetrics`, `CodebaseSnapshot`, `SelfAnalysisReport`
- `SystemEvolution`, `CodeEmbedding`, `SelfHealingAction`

### ai_intelligence app (7 models) - Remove
- `AgentLearningEvent`, `LearningDocument`, `AgentKnowledgeBase`
- `LearningEmbedding`, `AgentLearningSession`, `LearningInsight`

### intelligence app (3 models) - Remove
- `ActionPlan`, `ActionPlanStep`, `AgentExecution`

### learning_bridges app (1 model) - Remove
- `AdvisorConsultationFeedback`

---

## Duplicate Model Names

### 1. `AgentExecution` (3 definitions!)
| Location | Table | Records | Imports | Purpose |
|----------|-------|---------|---------|---------|
| `agents/models.py:436` | `agents_agentexecution` | 1 | 20+ files | Linked to UnifiedAgentTemplate |
| `core/models_unified_system.py:383` | `core_agentexecution` | 0 | 10+ files | General agent execution tracking |
| `intelligence/models.py:590` | `intelligence_rt_agentexecution` | 0 | 0 files | Action plan execution (no table) |

**Analysis:** Both `agents.AgentExecution` and `core.AgentExecution` are actively imported throughout the codebase. They serve different purposes:
- `agents.AgentExecution` is tied to `UnifiedAgentTemplate` for template-based execution
- `core.AgentExecution` is simpler, tied to `Agent` model for direct agent tracking

**Recommendation:**
1. Add deprecation warning to `core.AgentExecution` pointing to `agents.AgentExecution`
2. Migrate usages over time (Session 2+)
3. Remove `intelligence.AgentExecution` (no table, no imports)

### 2. `WorkflowExecution`
| Location | Table | Records | Imports | Purpose |
|----------|-------|---------|---------|---------|
| `content/models.py:1263` | `content_workflowexecution` | 0 | Used with ContentWorkflow |
| `core/models_unified_system.py:3088` | `core_workflowexecution` | 0 | Unused |

**Recommendation:** Keep `content.WorkflowExecution`, deprecate `core.WorkflowExecution`

---

## Apps with Missing Tables - FIXED (Session 288)

These apps had migrations marked as "applied" but tables didn't exist. **Fixed in Session 288:**

| App | Models Count | Migrations | Status |
|-----|--------------|-----------|--------|
| `sports` | 14 | 3 | **FIXED** - 14 tables created |
| `self_awareness` | 6 | 1 | **FIXED** - 6 tables created |
| `intelligence` | 3 | 2 | **FIXED** - 3 tables created |

**Fix Applied:**
1. Fake-unapplied migrations: `python manage.py migrate <app> zero --fake`
2. Dropped orphan indexes (intelligence had 22 orphan indexes)
3. Re-applied migrations: `python manage.py migrate <app>`

---

## Consolidation Strategy

### Phase 1: Deprecation Markers (Low Risk)

1. **Mark duplicate models as deprecated**
   - Add `# DEPRECATED: Use agents.AgentExecution instead` to `core.AgentExecution`
   - Add `# DEPRECATED: Use content.WorkflowExecution instead` to `core.WorkflowExecution`
   - Add logging warning on model save

2. **Remove orphan model**
   - Remove `intelligence.AgentExecution` (no table, no imports)

### Phase 2: Deprecate Empty Models (Medium Risk)

Mark these 100+ models as deprecated with warnings:
- All models in "Empty Tables" section above
- Add `DEPRECATED` comment and log warning on save

### Phase 3: Reorganize to core/models/ (Session 2)

Create new structure:
```
core/models/
├── __init__.py              # Exports all models
├── base.py                  # UnifiedBaseModel
├── content/
│   ├── media.py             # ImageHistory, VideoHistory
│   └── projects.py          # CreativeProject, CharacterModel
├── agents/
│   └── agents.py            # Agent, AgentMood, AgentRelationship
├── intelligence/
│   ├── spiders.py           # SpiderData
│   ├── learning.py          # AgentKnowledgeSource, KnowledgeTransfer
│   └── memory.py            # AgentMemory, UserMemoryContext
├── conversations/
│   └── conversations.py     # ChatConversation, ConversationMessage
└── deprecated/
    └── scifi_deprecated.py  # AgentDream, Prophecy, TimeCapsule, etc.
```

---

## Implementation Commands

### Phase 1: Quick Cleanup

```bash
# Check which apps are actually in INSTALLED_APPS
grep -A 50 "INSTALLED_APPS" core/settings.py

# Find references to removed apps
grep -r "from sports" --include="*.py" | grep -v migrations
grep -r "from self_awareness" --include="*.py" | grep -v migrations
grep -r "from ai_intelligence" --include="*.py" | grep -v migrations
```

### Validation

```bash
# After changes, verify migrations still work
python manage.py makemigrations --dry-run
python manage.py migrate --check

# Verify no import errors
python manage.py check
```

---

## Summary

| Action | Count | Risk |
|--------|-------|------|
| Remove dead models (no tables) | 31 | Low |
| Remove duplicate models | 2 | Low |
| Deprecate empty models | 100+ | Medium |
| Reorganize file structure | All | Session 2 |

**Expected Outcome:**
- Model count: 160 → ~60 active models
- File size reduction: ~50%
- Cleaner imports and organization
- Better maintainability

---

## Next Steps

1. **Now:** Review this plan with user
2. **Session 287:** Implement Phase 1 (remove dead code, duplicates)
3. **Session 288:** Implement Phases 2-3 (deprecation, reorganization)
