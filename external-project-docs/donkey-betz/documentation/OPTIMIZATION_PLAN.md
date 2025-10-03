# Database Optimization Plan

## Current Performance Bottlenecks

### 1. Vector Search Performance 🔴 CRITICAL
**Issue**: No vector indexes on any embedding columns  
**Impact**: All similarity searches use sequential table scans  
**Affected Tables**: 
- `unified_memory_entries` (123 rows)
- `ai_partner_conversationembedding` (85 rows)

### 2. Data Capture Gap 🟡 IMPORTANT
**Issue**: Agent results not being stored  
**Impact**: Lost insights from 44 agent executions  
**Affected**: `agent_orchestra_agentresult` table (empty)

### 3. Underutilized Infrastructure 🟡 IMPORTANT
**Issue**: Multiple embedding tables created but empty  
**Impact**: Missing business intelligence capabilities  
**Affected Tables**:
- `agent_orchestra_legislativebillembedding`
- `agent_orchestra_governmentcontractembedding`
- `agent_orchestra_regulatorydocumentembedding`

## Optimization Roadmap

### Phase 1: Immediate Performance Fixes (Week 1)

#### Day 1-2: Add Vector Indexes
```sql
-- Primary memory index
CREATE INDEX CONCURRENTLY idx_unified_memory_embedding_hnsw 
ON unified_memory_entries 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Conversation embedding index
CREATE INDEX CONCURRENTLY idx_conversation_embedding_hnsw
ON ai_partner_conversationembedding
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Learning memory index
CREATE INDEX CONCURRENTLY idx_learning_memory_embedding_hnsw
ON learning_intelligence_learningmemoryentry
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

#### Day 3: Fix Missing Embeddings
```python
# Script to generate embeddings for 3 entries without them
from backend.ai_partner.services.unified_memory_store import UnifiedMemoryStore

async def fix_missing_embeddings():
    store = UnifiedMemoryStore()
    missing = UnifiedMemoryEntry.objects.filter(embedding__isnull=True)
    for entry in missing:
        await store.generate_embedding(entry)
```

#### Day 4-5: Implement Agent Result Capture
```python
# Update agent execution to store results
class AgentInstance:
    def complete_execution(self, result_data):
        AgentResult.objects.create(
            agent=self,
            result_data=result_data,
            success=True,
            execution_time=self.get_execution_time()
        )
```

### Phase 2: Data Enrichment (Week 2)

#### Enable Business Intelligence Features
1. **Legislative Tracking**
   - Connect to GovTrack API
   - Import current session bills
   - Generate embeddings for bill summaries

2. **Government Contracts**
   - Connect to SAM.gov API
   - Import relevant contracts
   - Create embeddings for descriptions

3. **Regulatory Documents**
   - Connect to Regulations.gov
   - Import recent regulations
   - Generate embeddings for abstracts

### Phase 3: System Optimization (Week 3-4)

#### Memory System Consolidation
```sql
-- Migrate legacy memory entries
INSERT INTO unified_memory_entries (
    user_id, content_text, content_type, 
    source_system, created_by_agent
)
SELECT 
    user_id, event, 'legacy_memory',
    'memory', 'migration_agent'
FROM memory_memoryentry;

-- Update references
UPDATE unified_memory_entries 
SET source_reference = 'legacy_memory_' || id
WHERE source_system = 'memory';
```

#### Implement Partitioning
```sql
-- Partition by user for better performance
CREATE TABLE unified_memory_entries_partitioned (
    LIKE unified_memory_entries INCLUDING ALL
) PARTITION BY HASH (user_id);

-- Create 10 partitions
CREATE TABLE unified_memory_entries_p0 
PARTITION OF unified_memory_entries_partitioned
FOR VALUES WITH (modulus 10, remainder 0);
-- ... repeat for p1 through p9
```

### Phase 4: Monitoring & Maintenance (Ongoing)

#### Create Monitoring Views
```sql
CREATE MATERIALIZED VIEW mv_embedding_stats AS
SELECT 
    'unified_memory_entries' as table_name,
    COUNT(*) as total_rows,
    COUNT(embedding) as with_embeddings,
    AVG(octet_length(embedding::text)) as avg_embedding_size,
    MAX(updated_at) as last_update
FROM unified_memory_entries
UNION ALL
SELECT 
    'ai_partner_conversationembedding',
    COUNT(*), COUNT(embedding),
    AVG(octet_length(embedding::text)),
    MAX(created_at)
FROM ai_partner_conversationembedding;

-- Refresh daily
CREATE EXTENSION IF NOT EXISTS pg_cron;
SELECT cron.schedule('refresh-embedding-stats', '0 2 * * *', 
    'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_embedding_stats;');
```

#### Performance Monitoring Queries
```sql
-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename IN ('unified_memory_entries', 'ai_partner_conversationembedding')
ORDER BY idx_scan DESC;

-- Check table sizes
SELECT 
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    pg_size_pretty(pg_indexes_size(relid)) AS indexes_size
FROM pg_stat_user_tables
WHERE relname LIKE '%embedding%' OR relname LIKE '%memory%'
ORDER BY pg_total_relation_size(relid) DESC;
```

## Expected Performance Improvements

### After Phase 1 (Week 1)
- **Vector Search**: 10-100x faster with HNSW indexes
- **Query Time**: <50ms for similarity search (from 500ms+)
- **Agent Insights**: Start capturing execution results

### After Phase 2 (Week 2)
- **Data Coverage**: +500 business intelligence entries
- **Search Relevance**: Improved with diverse content types
- **Feature Enablement**: Legislative tracking operational

### After Phase 3 (Week 3-4)
- **Memory Consolidation**: Single source of truth
- **Partition Performance**: 3-5x improvement for user queries
- **System Simplicity**: Reduced from 4 to 1 memory system

### After Phase 4 (Ongoing)
- **Visibility**: Real-time performance metrics
- **Proactive Maintenance**: Automated index maintenance
- **Growth Tracking**: Embedding growth patterns visible

## Resource Requirements

### Storage
- **Current**: ~500MB (including indexes)
- **After Optimization**: ~750MB (with new indexes)
- **6-Month Projection**: 2-3GB (with BI data)

### Memory
- **HNSW Index Build**: 2GB temporary
- **Runtime**: +500MB for index caching
- **Query Memory**: 256MB per concurrent search

### CPU
- **Index Creation**: 100% for 5-10 minutes
- **Similarity Search**: <5% with indexes (from 30%)
- **Embedding Generation**: 20% during bulk operations

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Vector Search Time | >500ms | <50ms | pg_stat_statements |
| Embedding Coverage | 97.6% | 99.9% | mv_embedding_stats |
| Agent Result Capture | 0% | 100% | agent_orchestra_agentresult count |
| BI Table Usage | 0 | 500+ | Legislative/contract embeddings |
| Memory Systems | 4 | 1 | Active table count |
| Index Hit Rate | 0% | >95% | pg_stat_user_indexes |

## Risk Mitigation

1. **Index Creation Impact**
   - Use CONCURRENTLY to avoid locks
   - Schedule during low-traffic periods
   - Monitor connection count during creation

2. **Data Migration Risks**
   - Create backups before consolidation
   - Test migration scripts on dev first
   - Keep legacy tables for 30 days post-migration

3. **Performance Regression**
   - Monitor query performance daily
   - Set up alerts for slow queries
   - Have rollback plan for each change

## Implementation Checklist

### Week 1
- [ ] Backup database
- [ ] Create HNSW indexes
- [ ] Fix missing embeddings
- [ ] Implement result capture
- [ ] Test performance improvements

### Week 2
- [ ] Connect to GovTrack API
- [ ] Import legislative data
- [ ] Generate BI embeddings
- [ ] Verify search improvements

### Week 3-4
- [ ] Design partition strategy
- [ ] Migrate legacy memory
- [ ] Implement partitioning
- [ ] Create monitoring views
- [ ] Document changes

### Ongoing
- [ ] Daily performance review
- [ ] Weekly optimization report
- [ ] Monthly capacity planning
- [ ] Quarterly architecture review

---

*Optimization plan created: August 10, 2025*  
*Target completion: 4 weeks*  
*Review schedule: Weekly progress updates*