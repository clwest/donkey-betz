# Content Pipeline Database Optimization

## Overview

The Content Pipeline includes comprehensive database optimization features to ensure high performance at scale. This includes query optimization, monitoring, and automatic performance analysis.

## Key Features

### 1. Query Optimization Service

The `QueryOptimizer` class provides optimized database queries that avoid N+1 problems:

```python
from content_pipeline.services.query_optimizer import QueryOptimizer

# Get pipelines with all related data in a single query
pipelines = QueryOptimizer.get_optimized_pipeline_queryset(user_id=user.id)

# Get pipeline with pre-calculated statistics
pipeline = QueryOptimizer.get_pipeline_with_stats(pipeline_id)

# Bulk update pipeline progress
QueryOptimizer.bulk_update_pipeline_progress(pipeline_ids)
```

### 2. Database Query Monitoring

Real-time monitoring of database queries with automatic slow query detection:

```python
# Add to Django settings
MIDDLEWARE = [
    # ... other middleware
    'content_pipeline.middleware.query_monitoring.QueryMonitoringMiddleware',
]

# Configure monitoring
SLOW_QUERY_THRESHOLD = 1.0  # Log queries slower than 1 second
QUERY_MONITORING_ENABLED = True
```

### 3. Performance Analysis

Use the management command to analyze query patterns:

```bash
# Analyze queries from the last 7 days
python manage.py analyze_queries

# Analyze specific view
python manage.py analyze_queries --view content_pipeline --days 30

# Generate recommendations
python manage.py analyze_queries --recommendations

# Export results
python manage.py analyze_queries --export query_analysis.json
```

## Database Indexes

### Applied Indexes

The following indexes are automatically created via migrations:

1. **ContentPipeline Indexes**
   - `(user_id, status, created_at)` - For user's pipeline listings
   - `(template_id, user_id)` - For template-based queries
   - `(status)` WHERE status NOT IN ('published', 'failed', 'paused') - For active pipelines

2. **PipelineStage Indexes**
   - `(pipeline_id, order)` - For ordered stage retrieval
   - `(status, pipeline_id)` - For stage status queries
   - `(type, status)` - For analytics

3. **PipelineTransition Indexes**
   - `(pipeline_id, created_at)` - For transition history
   - `(from_stage_id, to_stage_id)` - For stage relationships

### Manual Index Creation

For production databases, run the SQL script:

```bash
psql -U your_user -d your_database -f content_pipeline/database_indexes.sql
```

## Optimized Views

Use the optimized views instead of the standard ones:

```python
# In urls.py
from content_pipeline.views_optimized import (
    OptimizedContentPipelineViewSet,
    OptimizedPipelineStageViewSet,
    OptimizedWorkflowTemplateViewSet
)

router.register(r'pipelines', OptimizedContentPipelineViewSet)
router.register(r'stages', OptimizedPipelineStageViewSet)
router.register(r'templates', OptimizedWorkflowTemplateViewSet)
```

## Query Patterns to Avoid

### 1. N+1 Queries

❌ **Bad:**
```python
pipelines = ContentPipeline.objects.filter(user=user)
for pipeline in pipelines:
    print(pipeline.stages.count())  # N+1 query!
```

✅ **Good:**
```python
pipelines = ContentPipeline.objects.filter(user=user).annotate(
    stage_count=Count('stages')
)
for pipeline in pipelines:
    print(pipeline.stage_count)  # No additional query
```

### 2. Missing select_related

❌ **Bad:**
```python
stages = PipelineStage.objects.all()
for stage in stages:
    print(stage.pipeline.name)  # Additional query per stage!
```

✅ **Good:**
```python
stages = PipelineStage.objects.select_related('pipeline')
for stage in stages:
    print(stage.pipeline.name)  # No additional queries
```

### 3. Count() in loops

❌ **Bad:**
```python
def get_linked_resources_count(obj):
    return {
        'obs_recordings': obj.obs_recordings.count(),
        'ai_assets': obj.ai_assets.count(),
    }
```

✅ **Good:**
```python
# Pre-annotate counts in queryset
pipelines = ContentPipeline.objects.annotate(
    obs_recordings_count=Count('obs_recordings'),
    ai_assets_count=Count('ai_assets')
)
```

## Performance Monitoring

### Dashboard Metrics

Monitor database performance through the API:

```bash
# Get current database metrics
curl http://localhost:8000/api/pipeline/metrics/database/

# Get slow query summary
curl http://localhost:8000/api/pipeline/metrics/slow-queries/
```

### Automatic Alerts

Configure alerts for performance issues:

```python
# In settings.py
DATABASE_MONITORING = {
    'slow_query_threshold': 1.0,  # seconds
    'alert_on_n_plus_one': True,
    'max_queries_per_request': 50,
    'log_query_patterns': True,
}
```

## Best Practices

### 1. Use Bulk Operations

```python
# Instead of multiple saves
for pipeline in pipelines:
    pipeline.progress_percentage = calculate_progress(pipeline)
    pipeline.save()

# Use bulk_update
ContentPipeline.objects.bulk_update(
    pipelines, ['progress_percentage'], batch_size=100
)
```

### 2. Prefetch Complex Relations

```python
# For complex nested relations
pipelines = ContentPipeline.objects.prefetch_related(
    Prefetch(
        'stages',
        queryset=PipelineStage.objects.select_related('pipeline')
        .prefetch_related('dependencies')
    )
)
```

### 3. Use Database Views for Reports

Create materialized views for complex reports:

```sql
CREATE MATERIALIZED VIEW pipeline_analytics AS
SELECT 
    p.user_id,
    COUNT(DISTINCT p.id) as total_pipelines,
    COUNT(DISTINCT CASE WHEN p.status = 'published' THEN p.id END) as completed,
    AVG(EXTRACT(EPOCH FROM (p.completed_at - p.started_at))) as avg_duration
FROM content_pipeline_contentpipeline p
GROUP BY p.user_id;

-- Refresh periodically
REFRESH MATERIALIZED VIEW pipeline_analytics;
```

## Troubleshooting

### High Query Count

If you see high query counts in logs:

1. Check for N+1 queries:
   ```bash
   python manage.py analyze_queries --view your_view --recommendations
   ```

2. Enable query logging in development:
   ```python
   LOGGING = {
       'loggers': {
           'django.db.backends': {
               'level': 'DEBUG',
           }
       }
   }
   ```

### Slow Queries

For queries slower than expected:

1. Check query execution plan:
   ```sql
   EXPLAIN ANALYZE SELECT ... FROM content_pipeline_contentpipeline WHERE ...;
   ```

2. Verify indexes are being used:
   ```sql
   SELECT * FROM pg_stat_user_indexes 
   WHERE tablename = 'content_pipeline_contentpipeline';
   ```

3. Update table statistics:
   ```sql
   ANALYZE content_pipeline_contentpipeline;
   ```

### Memory Usage

For high memory usage with large result sets:

1. Use iterator() for large querysets:
   ```python
   for pipeline in ContentPipeline.objects.filter(user=user).iterator():
       process_pipeline(pipeline)
   ```

2. Use only() to limit fields:
   ```python
   pipelines = ContentPipeline.objects.only('id', 'name', 'status')
   ```

## Performance Benchmarks

Expected query performance with proper optimization:

| Operation | Target Time | Max Time |
|-----------|------------|----------|
| List 100 pipelines | < 50ms | 100ms |
| Get pipeline detail | < 30ms | 50ms |
| Bulk update 1000 records | < 200ms | 500ms |
| Complex aggregation | < 100ms | 200ms |

## Migration Guide

To apply database optimizations to existing installations:

1. Run migrations:
   ```bash
   python manage.py migrate content_pipeline
   ```

2. Create additional indexes:
   ```bash
   psql -f content_pipeline/database_indexes.sql
   ```

3. Update views to use optimized versions:
   ```python
   # Update your URLconf to use OptimizedContentPipelineViewSet
   ```

4. Enable query monitoring:
   ```python
   # Add middleware and settings
   ```

5. Analyze existing queries:
   ```bash
   python manage.py analyze_queries --days 30 --recommendations
   ```

## Maintenance

Regular maintenance tasks:

### Daily
- Monitor slow query logs
- Check cache hit rates

### Weekly
- Analyze query patterns
- Review index usage
- Update table statistics

### Monthly
- Rebuild fragmented indexes
- Review and optimize slow queries
- Update materialized views

### Commands

```bash
# Vacuum and analyze tables
python manage.py dbshell
VACUUM ANALYZE content_pipeline_contentpipeline;

# Rebuild indexes
REINDEX TABLE content_pipeline_contentpipeline;

# Check table sizes
SELECT 
    relname as table_name,
    pg_size_pretty(pg_total_relation_size(relid)) as size
FROM pg_catalog.pg_statio_user_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(relid) DESC;
```