# UKF System Operations Guide

## Overview

The Unified Knowledge Framework (UKF) is a centralized memory and knowledge management system that provides semantic search, embedding generation, and intelligent caching for the entire application. This guide covers operational procedures, monitoring, and troubleshooting.

## System Architecture

### Core Components
- **UnifiedMemoryEntry**: Main data model storing all knowledge entries
- **UnifiedMemoryService**: Async service handling search and storage operations
- **Embedding Service**: Generates vector embeddings using OpenAI models
- **Search System**: Hybrid semantic/keyword search with PGVector
- **Caching Layer**: Redis-based intelligent query and result caching

### Key Metrics
- **Total Entries**: 40,687+ documents
- **Embedding Coverage**: 99.7%
- **Average Search Time**: 0.457s (semantic), 0.560s (keyword)
- **System Health**: 99.9%

## Health Monitoring

### Health Check Endpoints

1. **Basic Health Check** (Public)
   ```bash
   curl http://localhost:8000/api/shared-memory/health/
   ```
   Returns: `{"status": "healthy|degraded|unhealthy", "timestamp": "..."}`

2. **Detailed Health Check** (Staff Only)
   ```bash
   curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/shared-memory/health/detailed/
   ```
   Returns comprehensive health metrics including all subsystem checks

3. **Performance Status**
   ```bash
   curl http://localhost:8000/api/shared-memory/performance/status/
   ```
   Returns current search performance metrics

### Health Monitoring Commands

```bash
# Check embedding status
python manage.py monitor_embeddings --action=status

# Validate embeddings quality
python manage.py monitor_embeddings --action=validate --batch-size=100

# Generate performance report
python manage.py monitor_embeddings --action=report
```

### Health Thresholds
- **Embedding Coverage**: Must be > 95%
- **Search Performance**: < 1.0s average
- **Error Rate**: < 5%
- **Recent Activity**: Entries created in last 24h

## Performance Monitoring

### Real-time Metrics
Access real-time performance data:
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/shared-memory/performance/realtime/
```

### Performance Dashboard
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/shared-memory/performance/dashboard/
```

### Slow Query Analysis
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/shared-memory/performance/slow-queries/?limit=20
```

### Performance Benchmarking
```bash
python manage.py optimize_search_performance --benchmark
```

## Maintenance Procedures

### Daily Maintenance (Automated)

1. **Data Cleanup** (2 AM)
   - Removes search logs older than 30 days
   - Deletes inactive low-importance entries
   - Cleans up duplicate entries

2. **Database Optimization** (3 AM)
   - Runs ANALYZE on tables
   - Updates statistics
   - Checks and creates missing indexes

### Weekly Maintenance (Automated)

1. **Database VACUUM** (Sunday 4 AM)
   - Reclaims storage space
   - Updates visibility map
   - Improves query performance

### Manual Maintenance Commands

```bash
# Run all maintenance tasks
python manage.py ukf_maintenance --task=all

# Optimize database only
python manage.py ukf_maintenance --task=optimize

# Clean up old data (custom retention)
python manage.py ukf_maintenance --task=cleanup --days=60

# Vacuum database
python manage.py ukf_maintenance --task=vacuum

# Reindex embeddings
python manage.py ukf_maintenance --task=reindex

# Backfill missing data
python manage.py ukf_maintenance --task=backfill

# Clear and warm cache
python manage.py ukf_maintenance --task=cache

# Dry run mode (preview changes)
python manage.py ukf_maintenance --task=all --dry-run
```

## Embedding Management

### Monitor Embedding Generation
```bash
# Check current status
python manage.py monitor_embeddings --action=status

# Generate missing embeddings
python manage.py monitor_embeddings --action=generate --batch-size=100

# Continuous monitoring mode
python manage.py monitor_embeddings --action=generate --continuous --interval=300

# Backfill all missing embeddings
python manage.py monitor_embeddings --action=backfill
```

### Embedding Models
- **Primary**: text-embedding-3-small (28,842 entries)
- **Legacy**: text-embedding-ada-002 (11,720 entries)

## Troubleshooting Guide

### Common Issues

#### 1. High Search Latency
**Symptoms**: Search queries taking > 2 seconds
**Diagnosis**:
```bash
# Check slow queries
curl http://localhost:8000/api/shared-memory/performance/slow-queries/

# Check database statistics
python manage.py ukf_maintenance --task=optimize --dry-run
```
**Resolution**:
- Run database optimization: `python manage.py ukf_maintenance --task=optimize`
- Clear cache: `python manage.py ukf_maintenance --task=cache`
- Check for missing indexes

#### 2. Low Embedding Coverage
**Symptoms**: Coverage < 95%
**Diagnosis**:
```bash
python manage.py monitor_embeddings --action=status
```
**Resolution**:
```bash
# Generate missing embeddings
python manage.py monitor_embeddings --action=generate --batch-size=500

# For persistent issues, backfill
python manage.py monitor_embeddings --action=backfill
```

#### 3. Memory Growth Issues
**Symptoms**: Database size growing rapidly
**Diagnosis**:
```sql
SELECT 
    pg_size_pretty(pg_total_relation_size('unified_memory_entries')) as total_size,
    count(*) as row_count 
FROM unified_memory_entries;
```
**Resolution**:
- Run cleanup: `python manage.py ukf_maintenance --task=cleanup --days=30`
- Check for duplicates
- Review data retention policies

#### 4. Search Not Returning Results
**Symptoms**: Known content not found
**Diagnosis**:
```bash
# Test search directly
python manage.py shell
>>> from shared_memory.services import UnifiedMemoryService
>>> service = UnifiedMemoryService(user_id=1)
>>> import asyncio
>>> results = asyncio.run(service.search_memories("test query"))
```
**Resolution**:
- Check embedding generation status
- Verify user permissions
- Clear search cache
- Check for async context issues

### Emergency Procedures

#### System Unresponsive
1. Check health status: `curl http://localhost:8000/api/shared-memory/health/`
2. Check database connections
3. Clear all caches
4. Restart services if needed

#### Mass Embedding Failure
1. Stop embedding generation tasks
2. Check OpenAI API status and quota
3. Review error logs
4. Resume with smaller batch sizes

#### Database Performance Crisis
1. Kill long-running queries
2. Run emergency VACUUM
3. Temporarily disable non-critical features
4. Scale resources if needed

## Monitoring Checklist

### Daily Checks
- [ ] Health status is "healthy"
- [ ] Embedding coverage > 99%
- [ ] Average search time < 1s
- [ ] No critical alerts
- [ ] Maintenance tasks completed

### Weekly Checks
- [ ] Review slow query report
- [ ] Check database growth rate
- [ ] Verify backup completion
- [ ] Review error logs
- [ ] Check index usage

### Monthly Checks
- [ ] Performance trend analysis
- [ ] Capacity planning review
- [ ] Security audit
- [ ] Documentation updates
- [ ] Disaster recovery test

## Alerting Configuration

### Critical Alerts
- System health: unhealthy
- Embedding coverage < 90%
- Search performance > 2s average
- Error rate > 10%
- Database connection failures

### Warning Alerts
- System health: degraded
- Embedding coverage < 95%
- Search performance > 1s average
- Error rate > 5%
- Cache hit rate < 50%

## Performance Tuning

### Database Indexes
Ensure these indexes exist:
- `idx_ume_user_created` - User queries by date
- `idx_ume_content_type_user` - Content filtering
- `idx_ume_embedding_null` - Embedding generation
- HNSW index on embedding column

### Cache Configuration
- Query cache TTL: 300s (5 minutes)
- Embedding cache TTL: 1200s (20 minutes)
- Result cache TTL: 150s (2.5 minutes)

### Batch Sizes
- Embedding generation: 100-500 per batch
- Search results: 10-50 per query
- Maintenance cleanup: 1000 per batch

## Backup and Recovery

### Backup Strategy
1. **Database**: Daily PostgreSQL dumps
2. **Embeddings**: Included in database backup
3. **Configuration**: Version controlled
4. **Cache**: Not backed up (regenerated)

### Recovery Procedures
1. Restore database from backup
2. Verify embedding integrity
3. Clear and rebuild caches
4. Run health checks
5. Monitor for 24 hours

## Security Considerations

### Access Control
- Health endpoints: Public (basic) / Staff (detailed)
- Performance data: Authenticated users
- Maintenance commands: Admin only
- Direct database access: DBA only

### Data Privacy
- User isolation enforced at service level
- No cross-user data leakage
- Audit logging for sensitive operations
- PII handling in compliance with policies

## Contact and Escalation

### Support Levels
1. **L1**: Application logs and basic health checks
2. **L2**: Database queries and performance analysis
3. **L3**: Code changes and architectural decisions

### Escalation Path
1. Check this operations guide
2. Review application logs
3. Contact DevOps team
4. Escalate to engineering team
5. Vendor support (OpenAI, PostgreSQL)

---

Last Updated: August 4, 2025
Version: 1.0
Phase C5 Completion