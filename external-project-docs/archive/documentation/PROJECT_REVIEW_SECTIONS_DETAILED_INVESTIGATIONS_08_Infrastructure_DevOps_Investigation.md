# Detailed Investigation: Infrastructure & DevOps

## Common Issues to Investigate

### Issue 1: Database Performance with pgvector
**Problem**: Vector similarity searches are slow, affecting memory retrieval

**Investigation Steps:**

1. **pgvector Index Analysis**
   ```sql
   -- Check existing indexes
   \d+ memory_conversationmemory;
   
   -- Check if vector index exists
   SELECT indexname, indexdef 
   FROM pg_indexes 
   WHERE tablename = 'memory_conversationmemory';
   
   -- Analyze query performance
   EXPLAIN ANALYZE
   SELECT * FROM memory_conversationmemory
   ORDER BY embedding <-> '[0.1, 0.2, ...]'::vector
   LIMIT 10;
   ```

2. **Vector Dimension Investigation**
   ```python
   # Check vector dimensions in Django
   from memory.models import ConversationMemory
   
   # Get a sample embedding
   memory = ConversationMemory.objects.exclude(embedding__isnull=True).first()
   if memory and memory.embedding:
       print(f"Vector dimension: {len(memory.embedding)}")
   
   # Check for dimension mismatches
   from django.db import connection
   with connection.cursor() as cursor:
       cursor.execute("""
           SELECT COUNT(*), array_length(embedding, 1) as dim
           FROM memory_conversationmemory
           WHERE embedding IS NOT NULL
           GROUP BY dim
       """)
       print("Dimension distribution:", cursor.fetchall())
   ```

3. **Index Type Optimization**
   ```sql
   -- Check current index type
   SELECT am.amname as index_type
   FROM pg_class c
   JOIN pg_index i ON i.indexrelid = c.oid
   JOIN pg_am am ON am.oid = c.relam
   WHERE i.indrelid = 'memory_conversationmemory'::regclass;
   
   -- Consider different index types
   -- ivfflat for large datasets
   -- hnsw for better recall
   ```

### Issue 2: Redis Memory Management
**Problem**: Redis consuming too much memory or evicting important cache

**Investigation Steps:**

1. **Memory Usage Analysis**
   ```bash
   # Check Redis memory stats
   redis-cli info memory
   
   # Check key patterns
   redis-cli --scan --pattern "*" | head -100
   
   # Find large keys
   redis-cli --bigkeys
   
   # Check eviction policy
   redis-cli config get maxmemory-policy
   ```

2. **Key Expiration Audit**
   ```bash
   # Find keys without TTL
   redis-cli --scan | while read key; do
       ttl=$(redis-cli ttl "$key")
       if [ "$ttl" -eq "-1" ]; then
           echo "No TTL: $key"
       fi
   done
   
   # Check cache key patterns in code
   grep -r "cache\.set\|cache\.get" backend/ --include="*.py" | grep -v "timeout\|expire"
   ```

3. **Celery Queue Analysis**
   ```bash
   # Check queue sizes
   redis-cli llen celery
   redis-cli llen celery:1
   redis-cli llen celery:2
   
   # Check for stuck tasks
   celery -A server inspect reserved
   celery -A server inspect active
   ```

### Issue 3: Docker Container Resource Limits
**Problem**: Containers running out of memory or CPU

**Investigation Steps:**

1. **Container Resource Usage**
   ```bash
   # Check current usage
   docker stats --no-stream
   
   # Check container limits
   docker inspect backend | grep -A 10 "HostConfig"
   
   # Check for OOM kills
   docker inspect backend | grep -i oom
   journalctl -u docker | grep -i "out of memory"
   ```

2. **Docker Compose Limits**
   ```yaml
   # Check docker-compose.yml for limits
   services:
     backend:
       mem_limit: ?
       cpus: ?
       deploy:
         resources:
           limits:
             cpus: ?
             memory: ?
   ```

## Specific Infrastructure Queries

### Query 1: Database Performance
```sql
-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Check connection count
SELECT count(*) FROM pg_stat_activity;
```

### Query 2: Service Health Checks
```bash
# Create health check script
cat > check_health.sh << 'EOF'
#!/bin/bash

echo "=== Service Health Check ==="

# PostgreSQL
pg_isready -h localhost -p 5432 && echo "✓ PostgreSQL" || echo "✗ PostgreSQL"

# Redis
redis-cli ping > /dev/null && echo "✓ Redis" || echo "✗ Redis"

# Django
curl -s http://localhost:8000/health/ > /dev/null && echo "✓ Django" || echo "✗ Django"

# Celery
celery -A server inspect ping > /dev/null 2>&1 && echo "✓ Celery" || echo "✗ Celery"

# Nginx
curl -s http://localhost/ > /dev/null && echo "✓ Nginx" || echo "✗ Nginx"
EOF

chmod +x check_health.sh
```

### Query 3: Log Analysis
```bash
# Find errors across all logs
find backend/logs -name "*.log" -exec grep -l "ERROR\|CRITICAL" {} \;

# Check log sizes
du -sh backend/logs/*

# Recent errors with context
grep -B 5 -A 5 "ERROR" backend/logs/error.log | tail -50

# Check for memory errors
journalctl --since "1 day ago" | grep -i "memory\|oom\|killed"
```

## Performance Testing

### Test 1: Database Load Test
```python
# test_db_performance.py
import time
import concurrent.futures
from django.db import connection

def query_test(n):
    start = time.time()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM memory_conversationmemory")
        result = cursor.fetchone()
    return time.time() - start

# Run concurrent queries
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(query_test, i) for i in range(100)]
    times = [f.result() for f in futures]

print(f"Average query time: {sum(times)/len(times):.3f}s")
print(f"Max query time: {max(times):.3f}s")
```

### Test 2: Redis Performance
```python
# test_redis_performance.py
import time
from django.core.cache import cache

# Write test
start = time.time()
for i in range(1000):
    cache.set(f'test:key:{i}', {'data': 'x' * 1000}, timeout=60)
write_time = time.time() - start

# Read test
start = time.time()
for i in range(1000):
    cache.get(f'test:key:{i}')
read_time = time.time() - start

print(f"Write 1000 keys: {write_time:.3f}s")
print(f"Read 1000 keys: {read_time:.3f}s")

# Cleanup
for i in range(1000):
    cache.delete(f'test:key:{i}')
```

## Critical Configuration Files

1. **Database Configuration**
   - `backend/server/settings/database.py` - Connection settings
   - `docker-compose.yml` - PostgreSQL service config
   - Migration files with vector field definitions

2. **Caching Configuration**
   - `backend/server/settings/cache.py` - Redis settings
   - `redis.conf` - Redis server config
   - Cache key patterns in services

3. **Container Configuration**
   - `docker-compose.yml` - Service definitions
   - `backend/Dockerfile` - Backend image
   - `nginx/nginx.conf` - Web server config

## Common Problems and Solutions

### Problem: Slow Vector Searches
```sql
-- Create proper index
CREATE INDEX idx_embedding_vector 
ON memory_conversationmemory 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Analyze table
ANALYZE memory_conversationmemory;

-- Consider dimension reduction
-- If vectors are 1536-dim, consider PCA to 512-dim
```

### Problem: Redis Memory Bloat
```python
# Add TTL to all cache operations
cache.set('key', value, timeout=300)  # 5 minutes

# Use cache deletion on model updates
from django.core.cache import cache
from django.db.models.signals import post_save

@receiver(post_save, sender=MyModel)
def invalidate_cache(sender, instance, **kwargs):
    cache.delete(f'model:{instance.id}')
```

### Problem: Container Resource Exhaustion
```yaml
# docker-compose.yml
services:
  backend:
    mem_limit: 2g
    mem_reservation: 1g
    cpus: '2.0'
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Monitoring Setup

### Create Monitoring Script
```bash
#!/bin/bash
# monitor.sh

while true; do
    clear
    echo "=== System Monitor - $(date) ==="
    
    # CPU and Memory
    echo -e "\n--- System Resources ---"
    free -h | grep -E "^Mem|^Swap"
    echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
    
    # Docker
    echo -e "\n--- Docker Containers ---"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    
    # Database connections
    echo -e "\n--- Database ---"
    echo "Connections: $(psql -U postgres -t -c "SELECT count(*) FROM pg_stat_activity")"
    
    # Redis
    echo -e "\n--- Redis ---"
    redis-cli info memory | grep used_memory_human
    
    # Celery
    echo -e "\n--- Celery ---"
    echo "Active tasks: $(celery -A server inspect active | grep -c "task")"
    
    sleep 5
done
```

### Setup Alerts
```python
# alerts.py
import psutil
from django.core.mail import send_mail

def check_system_health():
    alerts = []
    
    # CPU check
    if psutil.cpu_percent(interval=1) > 80:
        alerts.append("High CPU usage")
    
    # Memory check
    if psutil.virtual_memory().percent > 85:
        alerts.append("High memory usage")
    
    # Disk check
    if psutil.disk_usage('/').percent > 90:
        alerts.append("Low disk space")
    
    # Database connections
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM pg_stat_activity")
        if cursor.fetchone()[0] > 90:
            alerts.append("High database connections")
    
    if alerts:
        send_mail(
            'System Alert',
            '\n'.join(alerts),
            'system@donkeybetz.com',
            ['admin@donkeybetz.com']
        )
```