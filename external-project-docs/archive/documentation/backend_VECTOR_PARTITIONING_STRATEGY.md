# Vector Partitioning Strategy for pgvector at Scale

## Overview

This document outlines the vector partitioning strategy for optimizing pgvector performance when dataset scales beyond 500K vectors.

## Current Status

- **ConversationEmbedding**: 46,940 vectors (No partitioning needed yet)
- **MarkdownEmbedding**: 2,004 vectors (No partitioning needed)
- **Threshold**: Implement partitioning at 500K+ vectors

## Partitioning Strategies

### 1. User-Based Partitioning (Recommended)

**Benefits:**
- Complete data isolation between users
- Parallel query execution per user
- Better privacy and security
- Simplified user data deletion (GDPR compliance)

**Implementation:**
```sql
-- Create partitioned table
CREATE TABLE ai_partner_conversationembedding_partitioned (
    LIKE ai_partner_conversationembedding INCLUDING ALL
) PARTITION BY HASH (user_id);

-- Create 16 partitions (adjust based on user distribution)
CREATE TABLE ai_partner_conversationembedding_p0 
    PARTITION OF ai_partner_conversationembedding_partitioned
    FOR VALUES WITH (MODULUS 16, REMAINDER 0);
    
CREATE TABLE ai_partner_conversationembedding_p1 
    PARTITION OF ai_partner_conversationembedding_partitioned
    FOR VALUES WITH (MODULUS 16, REMAINDER 1);
    
-- ... repeat for p2 through p15

-- Create vector indexes on each partition
CREATE INDEX CONCURRENTLY ON ai_partner_conversationembedding_p0 
USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64);

-- Repeat for all partitions
```

### 2. Time-Based Partitioning

**Benefits:**
- Efficient data archival
- Query optimization for recent data
- Easy old data cleanup

**Implementation:**
```sql
-- Monthly partitioning
CREATE TABLE ai_partner_conversationembedding_time_partitioned (
    LIKE ai_partner_conversationembedding INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE conversation_embedding_2025_01 
    PARTITION OF ai_partner_conversationembedding_time_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE conversation_embedding_2025_02 
    PARTITION OF ai_partner_conversationembedding_time_partitioned
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

### 3. Hybrid Partitioning (Advanced)

**Benefits:**
- Combines user isolation with time-based efficiency
- Maximum query optimization

**Implementation:**
```sql
-- First partition by user_id, then subpartition by time
CREATE TABLE ai_partner_conversationembedding_hybrid (
    LIKE ai_partner_conversationembedding INCLUDING ALL
) PARTITION BY HASH (user_id);

CREATE TABLE conversation_embedding_user_p0 
    PARTITION OF ai_partner_conversationembedding_hybrid
    FOR VALUES WITH (MODULUS 4, REMAINDER 0)
    PARTITION BY RANGE (created_at);
    
-- Create time subpartitions for each user partition
CREATE TABLE conversation_embedding_u0_2025_01 
    PARTITION OF conversation_embedding_user_p0
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

## Migration Strategy

### Phase 1: Preparation (Before 100K vectors)
1. Set up monitoring for dataset growth
2. Test partitioning on development environment
3. Prepare migration scripts

### Phase 2: Implementation (At 500K vectors)
1. Create partitioned table structure
2. Migrate data during maintenance window
3. Update application queries
4. Monitor performance improvements

### Phase 3: Optimization (Post-migration)
1. Fine-tune partition count based on usage patterns
2. Optimize vector indexes per partition
3. Implement partition pruning in queries

## Query Optimization with Partitioning

### Before Partitioning
```python
# Searches entire table
results = ConversationEmbedding.objects.raw("""
    SELECT id, embedding <-> %s::vector as distance
    FROM ai_partner_conversationembedding 
    WHERE embedding IS NOT NULL
    ORDER BY embedding <-> %s::vector 
    LIMIT 10
""", [vector_str, vector_str])
```

### After User Partitioning
```python
# Searches only user's partition
results = ConversationEmbedding.objects.raw("""
    SELECT id, embedding <-> %s::vector as distance
    FROM ai_partner_conversationembedding 
    WHERE user_id = %s AND embedding IS NOT NULL
    ORDER BY embedding <-> %s::vector 
    LIMIT 10
""", [vector_str, user_id, vector_str])
```

## Partition Maintenance

### Automatic Partition Creation
```sql
-- Extension for automatic partition management
CREATE EXTENSION IF NOT EXISTS pg_partman;

-- Setup automatic monthly partition creation
SELECT partman.create_parent(
    p_parent_table => 'public.ai_partner_conversationembedding_time_partitioned',
    p_control => 'created_at',
    p_type => 'range',
    p_interval => 'monthly'
);
```

### Partition Pruning
```sql
-- Enable constraint exclusion for partition pruning
SET constraint_exclusion = partition;

-- Query that benefits from partition pruning
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM ai_partner_conversationembedding 
WHERE user_id = 123 AND created_at >= '2025-01-01';
```

## Monitoring and Metrics

### Partition Size Monitoring
```sql
SELECT 
    schemaname,
    tablename,
    n_live_tup as rows,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_stat_user_tables 
WHERE tablename LIKE 'ai_partner_conversationembedding%'
ORDER BY n_live_tup DESC;
```

### Query Performance by Partition
```sql
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
FROM pg_stat_user_tables 
WHERE tablename LIKE 'ai_partner_conversationembedding%'
ORDER BY idx_scan DESC;
```

## Implementation Timeline

### Immediate Actions (Current)
- [x] Set up monitoring for dataset growth
- [x] Document partitioning strategy
- [ ] Create partitioning test environment

### At 100K Vectors
- [ ] Begin partition testing
- [ ] Benchmark partitioned vs non-partitioned performance
- [ ] Prepare production migration scripts

### At 500K Vectors
- [ ] Execute partitioning migration
- [ ] Update application code for partition-aware queries
- [ ] Monitor performance improvements

## Performance Expectations

### Without Partitioning (500K vectors)
- Query time: 500-2000ms
- Memory usage: High (full table scan possible)
- Maintenance: Complex (single large index)

### With User Partitioning (500K vectors, 16 partitions)
- Query time: 50-200ms (31K vectors per partition average)
- Memory usage: Lower (smaller working sets)
- Maintenance: Simpler (smaller indexes per partition)

### With Time Partitioning (500K vectors, monthly)
- Query time: 100-500ms (depends on time range)
- Memory usage: Lower for recent data queries
- Maintenance: Easy old data archival

## Code Examples

### Django Model Changes
```python
# Add partition-aware manager
class PartitionedConversationEmbeddingManager(models.Manager):
    def for_user(self, user_id):
        """Query specific user partition"""
        return self.filter(user_id=user_id)
    
    def recent(self, days=30):
        """Query recent partitions only"""
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)

class ConversationEmbedding(models.Model):
    # ... existing fields ...
    
    objects = PartitionedConversationEmbeddingManager()
    
    class Meta:
        # Add partition key to indexes
        indexes = [
            models.Index(fields=['user_id', 'created_at']),
            models.Index(fields=['user_id'], 
                        condition=models.Q(embedding__isnull=False))
        ]
```

### Optimized Vector Search Service
```python
class PartitionAwareVectorSearch:
    def search_conversations(self, query_vector, user_id, limit=10):
        """Search with partition pruning"""
        vector_str = self._normalize_vector(query_vector)
        
        with connection.cursor() as cursor:
            # This query will use partition pruning
            cursor.execute("""
                SELECT id, embedding <-> %s::vector as distance
                FROM ai_partner_conversationembedding 
                WHERE user_id = %s AND embedding IS NOT NULL
                ORDER BY embedding <-> %s::vector 
                LIMIT %s
            """, [vector_str, user_id, vector_str, limit])
            
            return cursor.fetchall()
```

## Conclusion

Vector partitioning provides significant performance benefits at scale:

1. **User-based partitioning** recommended for privacy and performance
2. **Implement at 500K vectors** for optimal cost/benefit ratio  
3. **Monitor growth** and prepare migration scripts in advance
4. **Test thoroughly** on development environment before production

The strategy balances performance gains with implementation complexity, ensuring the system can scale to millions of vectors while maintaining sub-100ms query times.