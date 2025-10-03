# PostgreSQL with pgvector Deployment Guide

## Overview
Complete deployment configuration for PostgreSQL with pgvector extension, optimized for AI Content Studio's vector operations and embedding storage.

## Quick Start

### 1. Deploy PostgreSQL with pgvector
```bash
cd deployment
./deploy-postgres.sh up
```

### 2. Deploy with pgAdmin (optional)
```bash
./deploy-postgres.sh admin
```

### 3. Test installation
```bash
./deploy-postgres.sh test
```

## Files Created

### Core Configuration
- `postgres-pgvector-compose.yml` - Docker Compose configuration
- `.env.postgres` - Environment variables template
- `deploy-postgres.sh` - Deployment management script

### PostgreSQL Configuration
- `postgres/init.sql` - Database initialization with pgvector
- `postgres/optimize.sql` - Performance optimizations
- `postgres/postgresql.conf` - PostgreSQL configuration
- `postgres/backup.sh` - Automated backup script
- `postgres/servers.json` - pgAdmin server configuration

## Features

### Database Capabilities
- **pgvector Extension**: Full vector similarity search support
- **Embedding Storage**: Optimized for 1536-dimensional vectors (OpenAI)
- **Index Types**: HNSW and IVFFlat indexes for fast search
- **Performance Tuning**: Optimized for SSD and high-memory operations

### Monitoring & Maintenance
- Health checks and readiness probes
- Automatic backup scheduling
- Performance monitoring functions
- Vector search benchmarking tools

### Security
- SCRAM-SHA-256 authentication
- Connection limits and timeouts
- Slow query logging
- Prepared transaction support

## Deployment Commands

### Basic Operations
```bash
# Start PostgreSQL
./deploy-postgres.sh up

# Stop PostgreSQL
./deploy-postgres.sh down

# Restart PostgreSQL
./deploy-postgres.sh restart

# View status
./deploy-postgres.sh status

# View logs
./deploy-postgres.sh logs
```

### Database Management
```bash
# Open PostgreSQL shell
./deploy-postgres.sh shell

# Backup database
./deploy-postgres.sh backup

# Restore from backup
./deploy-postgres.sh restore backup_file.sql.gz

# Test connection and pgvector
./deploy-postgres.sh test
```

### Advanced Operations
```bash
# Start with pgAdmin
./deploy-postgres.sh admin

# Clean all data (WARNING: destructive)
./deploy-postgres.sh clean
```

## Configuration

### Environment Variables
Copy `.env.postgres` to `.env` and configure:

```bash
# Database Settings
POSTGRES_DB=ai_content_studio
POSTGRES_USER=ai_studio_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_PORT=5432

# Performance Tuning
POSTGRES_SHARED_BUFFERS=512MB
POSTGRES_EFFECTIVE_CACHE_SIZE=2GB
VECTOR_MAX_MEMORY=256MB
```

### Connection Settings for Django
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ai_content_studio',
        'USER': 'ai_studio_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## pgvector Usage Examples

### Create Vector Table
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536)
);
```

### Create Indexes
```sql
-- HNSW index for fast approximate search
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);

-- IVFFlat index for memory efficiency
CREATE INDEX ON documents USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
```

### Similarity Search
```sql
-- Find similar documents
SELECT id, content, 1 - (embedding <=> '[...]'::vector) as similarity
FROM documents
ORDER BY embedding <=> '[...]'::vector
LIMIT 10;
```

## Performance Optimization

### Automatic Optimizations
The deployment includes:
- Optimized memory settings for vector operations
- Parallel query execution enabled
- Autovacuum tuned for vector tables
- Connection pooling configuration

### Manual Optimization
```sql
-- Optimize vector search for a table
SELECT optimize_vector_search('documents', 'embedding');

-- Benchmark vector search performance
SELECT * FROM benchmark_vector_search('documents', 'embedding', '[...]'::vector);

-- View vector index statistics
SELECT * FROM get_vector_stats();
```

## Monitoring

### Check Database Size
```sql
SELECT * FROM monitoring.table_sizes();
```

### Vector Search Performance
```sql
SELECT * FROM monitoring.vector_search_stats
ORDER BY query_timestamp DESC
LIMIT 10;
```

### Index Recommendations
```sql
SELECT * FROM index_recommendations;
```

## Backup & Recovery

### Automatic Backups
Backups are configured to run daily at 3 AM with 7-day retention.

### Manual Backup
```bash
./deploy-postgres.sh backup
# Backups stored in deployment/backups/
```

### Restore from Backup
```bash
./deploy-postgres.sh restore backups/ai_content_studio_20250104_030000.sql.gz
```

## Troubleshooting

### Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Test connection
./deploy-postgres.sh test

# View logs
./deploy-postgres.sh logs
```

### Performance Issues
```sql
-- Check slow queries
SELECT * FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Analyze tables
VACUUM ANALYZE;

-- Reindex vector indexes
CALL monitoring.reindex_vector_indexes();
```

### pgvector Issues
```sql
-- Verify pgvector installation
SELECT extversion FROM pg_extension WHERE extname = 'vector';

-- Check vector dimensions
SELECT vector_dims(embedding) FROM documents LIMIT 1;

-- Rebuild vector indexes
REINDEX INDEX idx_documents_embedding_hnsw;
```

## Production Considerations

### Resource Requirements
- **Memory**: Minimum 2GB, recommended 4GB+
- **Storage**: SSD recommended for optimal performance
- **CPU**: 2+ cores for parallel query execution

### Scaling
- Use connection pooling (PgBouncer) for high concurrent connections
- Consider read replicas for heavy read workloads
- Implement partitioning for very large vector tables

### Security
- Change default passwords in production
- Enable SSL/TLS for connections
- Implement network isolation
- Regular security updates

## Integration with AI Content Studio

The PostgreSQL deployment is configured to work seamlessly with:
- Django ORM with pgvector support
- Memory and embedding storage
- Vector similarity search
- Assistant memory system
- Document indexing

## Support

For issues or questions:
1. Check logs: `./deploy-postgres.sh logs`
2. Run tests: `./deploy-postgres.sh test`
3. Review this documentation
4. Check PostgreSQL and pgvector documentation

## Version Information
- PostgreSQL: 16 (latest)
- pgvector: Latest version
- Optimized for: OpenAI embeddings (1536 dimensions)

---

Deployment configured and ready for production use!