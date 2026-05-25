---
originating_session: 810
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 810: Celery Beat Fix & Production Database Sync

**Date:** January 24, 2026
**Previous Session:** 809 (Persona Agent Dormancy Root Cause)
**Status:** COMPLETE - 5 New Management Commands, 60+ Tasks Restored, $385/day Egress Fix

---

## Summary

This session addressed critical discrepancies between local and production environments:

1. **Celery Beat Override Issue** - 187 tasks in `celery.py` were NOT running because `settings.py` overrides them
2. **Blog Visibility** - 1,000+ SelfBlogs invisible due to missing HumanAttentionItem entries
3. **Agent Relationships** - Production had 0 relationships vs 462 locally
4. **Database Health Monitoring** - Created tool to compare environments
5. **pgvector Egress Costs** - $385.56/day (7,711 GB) from embedding vectors being pulled unnecessarily

---

## Critical Fix: Celery Beat Override

### The Problem

When using `DatabaseScheduler`, Django's `settings.py` `CELERY_BEAT_SCHEDULE` **completely overrides** `celery.py`'s `app.conf.beat_schedule`.

```
settings.py CELERY_BEAT_SCHEDULE (74 tasks)
    ↓ OVERRIDES
celery.py app.conf.beat_schedule (239 tasks)
    ↓ RESULT
187 tasks NOT RUNNING (including ALL body system health checks)
```

### The Fix

Created `add_critical_celery_tasks.py` with 94 critical tasks hardcoded:

```bash
python manage.py add_critical_celery_tasks
```

### Results

| Metric | Before | After |
|--------|--------|-------|
| Enabled Celery Beat Tasks | 168 | **228** (+60) |
| Body System Health Tasks | 0 | **16** |
| Agent Category Rotation Tasks | 0 | **15** |

### Body Systems Now Active

| System | Task | Interval |
|--------|------|----------|
| Heart | `run_heartbeat` | 60s |
| Lungs | `check_breathing` | 15min |
| Brain | `check_brain` | 60s |
| Skin | `check_skin` | 90s |
| Spine | `check_spine_alignment` | 60s |
| Immune | `immune_scan` | 45s |
| Digestive | `check_digestion` | 60s |
| Muscular | `check_muscular` | 90s |
| Nervous | `check_nervous` | 60s |
| Circulatory | `check_circulation` | 30s |
| Coordinator | `coordinate_body` | 60s |

---

## Blog Visibility Fix

### The Problem

Session 804 added `_create_blog_attention_item()` for NEW blogs, but existing blogs had no HumanAttentionItem entries.

- Local: 1,012 SelfBlogs, 0 blog attention items
- Result: Blogs invisible in Human Interface

### The Fix

Created `backfill_blog_attention_items.py`:

```bash
python manage.py backfill_blog_attention_items
```

---

## Local vs Production Database Comparison

### The Tool

Created `db_health_snapshot.py` to compare environments:

```bash
python manage.py db_health_snapshot        # Formatted output
python manage.py db_health_snapshot --json # For diff comparison
```

### Key Discrepancies Found

| Metric | Local | Production | Issue |
|--------|-------|------------|-------|
| SelfBlog | 1,012 | 61 | Historical data |
| AgentKnowledgeSource | 4,563 | 1,621 | Run `sync_persona_learning` |
| AgentLearningConnection | 345 | 158 | Run `sync_persona_learning` |
| AgentRelationship | 462 | **0** | Run `bootstrap_agent_relationships` |
| ConversationMemory | 617 | 11 | Natural accumulation |
| SpiderData_last_24h | 0 | 470 | Spiders running on prod |
| PeriodicTask_enabled | 228 | 262 | Prod ahead after fix |

---

## Agent Relationships Bootstrap

### The Problem

Production had **0 AgentRelationship** entries - the Sci-Fi "Relationships" feature showed nothing.

### The Fix

Created `bootstrap_agent_relationships.py`:

```bash
python manage.py bootstrap_agent_relationships           # Create all
python manage.py bootstrap_agent_relationships --dry-run # Preview
python manage.py bootstrap_agent_relationships --clear   # Replace all
```

Creates relationships based on category affinities:
- Research ↔ Content (alliance)
- Financial ↔ Predictions (alliance)
- Security ↔ Blockchain (alliance)
- Same-category dynamics (alliances, rivalries, mentorships)

---

## pgvector Egress Cost Fix

### The Problem

Railway billing showed **$385.56/day** in pgvector egress (7,711 GB). Root cause: SpiderData and AgentMemory queries were pulling embedding vectors (~6KB each) on every query, even when not needed.

```
SpiderData.embedding = 1536 floats × 4 bytes = ~6KB per record
AgentMemory.embedding = 1536 floats × 4 bytes = ~6KB per record

Celery tasks querying these tables constantly = massive egress
```

### The Fix

Added `.defer('embedding')` to 52 queries across 8 files:

| File | Queries Fixed |
|------|---------------|
| `core/tasks.py` | 34 |
| `core/views_memory_palace.py` | 7 |
| `core/agents/personal_assistant_agent.py` | 4 |
| `core/views_spider_feed.py` | 3 |
| `core/views_spider_dashboard.py` | 1 |
| `core/views_analytics.py` | 1 |
| `core/views_orchestration.py` | 1 |
| `core/views_predictions.py` | 1 |

### Expected Savings

- **Before**: ~7,711 GB egress/day = $385.56/day
- **After**: Significant reduction (embeddings only fetched when actually needed for similarity search)

---

## New Management Commands Created

| Command | Purpose | PR |
|---------|---------|-----|
| `add_critical_celery_tasks` | Add 94 critical Celery Beat tasks | #98 |
| `sync_celery_schedules` | Sync from celery.py to database | #98 |
| `backfill_blog_attention_items` | Create HumanAttentionItem for existing blogs | #99 |
| `db_health_snapshot` | Compare local vs production database | #100 |
| `bootstrap_agent_relationships` | Create agent relationships | #101, #102 |

---

## Production Deployment Commands

Run these on Railway production after deploying:

```bash
# 1. Add critical Celery tasks (already done)
railway run python manage.py add_critical_celery_tasks

# 2. Backfill blog attention items (already done)
railway run python manage.py backfill_blog_attention_items

# 3. Bootstrap agent relationships
railway run python manage.py bootstrap_agent_relationships

# 4. Sync persona learning (if knowledge sources low)
railway run python manage.py sync_persona_learning

# 5. Check database health
railway run python manage.py db_health_snapshot
```

---

## Files Changed

### New Files
- `core/management/commands/add_critical_celery_tasks.py` (716 lines)
- `core/management/commands/sync_celery_schedules.py` (266 lines)
- `core/management/commands/backfill_blog_attention_items.py` (145 lines)
- `core/management/commands/db_health_snapshot.py` (222 lines)
- `core/management/commands/bootstrap_agent_relationships.py` (275 lines)

### Modified Files
- `00-START-NEXT-SESSION.md` - Updated for Session 811
- `CLAUDE.md` - Updated Celery task count (139 → 228)
- `core/tasks.py` - Added `.defer('embedding')` to 34 queries
- `core/views_memory_palace.py` - Added `.defer('embedding')` to 7 queries
- `core/agents/personal_assistant_agent.py` - Added `.defer('embedding')` to 4 queries
- `core/views_spider_feed.py` - Added `.defer('embedding')` to 3 queries
- `core/views_spider_dashboard.py` - Added `.defer('embedding')` to 1 query
- `core/views_analytics.py` - Added `.defer('embedding')` to 1 query
- `core/views_orchestration.py` - Added `.defer('embedding')` to 1 query
- `core/views_predictions.py` - Added `.defer('embedding')` to 1 query

---

## Pull Requests

| PR | Title | Status |
|----|-------|--------|
| #98 | feat(Session 810): Fix Celery Beat override - restore 60 critical tasks | ✅ Merged |
| #99 | feat(Session 810): Backfill blog attention items | ✅ Merged |
| #100 | feat(Session 810): Database health snapshot | ✅ Merged |
| #101 | feat(Session 810): Bootstrap agent relationships | ✅ Merged |
| #102 | fix: Remove invalid collaboration_score field | ✅ Merged |
| #104 | fix(Session 810): Reduce pgvector egress costs with .defer('embedding') | ✅ Merged |

---

## Key Learnings

1. **DatabaseScheduler Override**: When using `django_celery_beat.schedulers:DatabaseScheduler`, settings.py completely overrides celery.py. Tasks must be in the database OR settings.py.

2. **Production vs Local Drift**: Running commands like `sync_persona_learning` on production but not locally causes environment drift. Document all initialization commands.

3. **Backfill Commands**: When adding features that create related records (like HumanAttentionItem for SelfBlog), always create a backfill command for existing data.

4. **Environment Comparison**: The `db_health_snapshot` command is invaluable for identifying drift between environments.

5. **pgvector Egress Costs**: Always use `.defer('embedding')` when querying models with vector fields unless you specifically need the embeddings. Each 1536-float vector is ~6KB, and Celery tasks running every minute can cause massive egress costs.

---

## Next Session Priorities

1. Monitor agent relationships creation on production
2. Verify all body system health checks are running
3. Check if any other features need production initialization
4. Consider creating a unified "production setup" command
