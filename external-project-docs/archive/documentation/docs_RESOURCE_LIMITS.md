# Docker Container Resource Limits

## Overview

This document details the resource limits implemented for all Docker containers in the Donkey Betz platform to ensure system stability and prevent resource exhaustion.

## Resource Allocation Strategy

### Development Environment (docker-compose.yml)

**Total System Requirements:**
- **CPU**: 4.75 cores
- **Memory**: 4.89 GB

| Service | CPU Limit | Memory Limit | CPU Reserved | Memory Reserved | Rationale |
|---------|-----------|--------------|--------------|-----------------|-----------|
| postgres | 1.0 | 1G | 0.5 | 512M | Database operations require consistent resources |
| redis | 0.5 | 512M | 0.25 | 256M | In-memory cache with LRU eviction policy |
| backend | 2.0 | 2G | 1.0 | 1G | Django application with AI services |
| celery_worker | 1.0 | 1G | 0.5 | 512M | Async task processing |
| celery_beat | 0.5 | 256M | 0.25 | 128M | Lightweight scheduler |
| nginx | 0.5 | 256M | 0.25 | 128M | Static file serving and reverse proxy |

### Production Environment (docker-compose.prod.yml)

**Total System Requirements:**
- **CPU**: 9.0 cores
- **Memory**: 10.02 GB

| Service | CPU Limit | Memory Limit | CPU Reserved | Memory Reserved | Rationale |
|---------|-----------|--------------|--------------|-----------------|-----------|
| postgres | 2.0 | 2G | 1.0 | 1G | Higher load capacity for production |
| redis | 1.0 | 1G | 0.5 | 512M | Larger cache for production workloads |
| backend | 4.0 | 4G | 2.0 | 2G | Enhanced capacity for concurrent users |
| celery_worker | 2.0 | 2G | 1.0 | 1G | Increased concurrency (4 workers) |
| celery_beat | 1.0 | 512M | 0.5 | 256M | Production scheduler with persistence |
| nginx | 1.0 | 512M | 0.5 | 256M | SSL termination and static file serving |

## Implementation Details

### Resource Limits
- **CPU limits**: Prevent individual containers from consuming excessive CPU
- **Memory limits**: Prevent OOM conditions that could crash the host
- **Reservations**: Guarantee minimum resources for critical operations

### Health Checks
All services include comprehensive health checks:
- **PostgreSQL**: `pg_isready` command
- **Redis**: `redis-cli ping` command
- **Backend**: Django health endpoint
- **Celery Worker**: Celery ping inspection
- **Celery Beat**: Scheduled task inspection
- **Nginx**: HTTP health check

### Restart Policies
- **unless-stopped**: Containers restart automatically unless manually stopped
- **Graceful degradation**: Failed services don't cascade to other containers

## Memory Management

### Redis Configuration
- **Development**: 256MB max memory with LRU eviction
- **Production**: 1GB max memory with LRU eviction
- **Persistence**: Append-only file for data durability

### PostgreSQL Optimization
- **Connection pooling**: Managed by Django database settings
- **Shared buffers**: Configured automatically based on available memory
- **Work memory**: Optimized for concurrent connections

### Celery Configuration
- **Development**: 2 concurrent workers
- **Production**: 4 concurrent workers
- **Memory per worker**: ~250MB average, 500MB maximum

## Monitoring and Alerts

### Resource Usage Monitoring
```bash
# Check container resource usage
docker stats

# Monitor specific service
docker stats donkey-betz-backend

# Check resource limits
docker inspect <container_id> | grep -A 10 "Resources"
```

### Alert Thresholds
- **CPU**: Alert when > 80% for 5 minutes
- **Memory**: Alert when > 90% for 2 minutes
- **Disk**: Alert when > 85% usage

## Scaling Guidelines

### Horizontal Scaling
- **Celery Workers**: Can be scaled to multiple instances
- **Backend**: Can be load-balanced behind nginx
- **Redis**: Consider Redis Cluster for high availability

### Vertical Scaling
Increase limits in this order:
1. **Memory first**: Usually the first bottleneck
2. **CPU second**: Scale based on actual usage patterns
3. **Storage**: Monitor volume usage growth

### Resource Adjustment Rules
- **Never decrease reservations** below current usage
- **Increase limits gradually** (20-50% increments)
- **Monitor for 48 hours** after any changes

## Testing Resource Limits

### Load Testing
```bash
# Start with resource monitoring
docker-compose up -d
docker stats

# Generate load on specific services
# Backend load test
curl -X POST http://localhost:8000/api/test/load-test/

# Database load test
docker exec -it donkey-betz-postgres psql -U postgres -c "SELECT pg_stat_activity();"

# Redis load test
redis-cli --latency -h localhost -p 6379
```

### Memory Pressure Testing
```bash
# Test memory limits
docker exec -it donkey-betz-backend python -c "
x = []
for i in range(1000000):
    x.append('a' * 1000)
"

# Monitor OOM conditions
dmesg | grep -i "killed process"
```

## Troubleshooting

### Common Issues

**1. Container OOM Killed**
```bash
# Check container logs
docker logs <container_name>

# Increase memory limit in docker-compose.yml
# Then restart service
docker-compose up -d <service_name>
```

**2. High CPU Usage**
```bash
# Profile CPU usage
docker exec -it <container> top

# Check for runaway processes
docker exec -it <container> ps aux --sort=-%cpu
```

**3. Health Check Failures**
```bash
# Check health status
docker ps

# Run health check manually
docker exec -it <container> <health_check_command>
```

### Emergency Procedures

**1. System Resource Exhaustion**
```bash
# Stop non-critical services
docker-compose stop nginx celery_beat

# Restart with reduced limits
docker-compose up -d --scale celery_worker=1
```

**2. Database Performance Issues**
```bash
# Check database connections
docker exec -it donkey-betz-postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Restart database with maintenance
docker-compose stop postgres
docker-compose up -d postgres
```

## Security Considerations

### Resource-Based Security
- **DoS Prevention**: Resource limits prevent resource exhaustion attacks
- **Isolation**: Container limits prevent compromise of one service affecting others
- **Privilege Dropping**: Services run with minimal required privileges

### Network Security
- **Internal Networks**: Services communicate via internal Docker networks
- **Firewall Rules**: Only necessary ports exposed to host
- **SSL Termination**: Nginx handles SSL for external connections

## Environment Variables

### Required Variables
```bash
# Database configuration
POSTGRES_DB=moveyourass
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<secure_password>

# Redis configuration (optional)
REDIS_MAX_MEMORY=512mb
REDIS_POLICY=allkeys-lru
```

### Optional Tuning Variables
```bash
# Celery worker count
CELERY_WORKER_CONCURRENCY=4

# Django settings
DJANGO_SETTINGS_MODULE=server.settings
DEBUG=False  # Production only
```

## Backup and Recovery

### Resource Considerations
- **PostgreSQL Backups**: Schedule during low-resource periods
- **Redis Persistence**: AOF files managed automatically
- **Media Files**: Volume backups don't affect container limits

### Disaster Recovery
1. **Service Priority**: postgres > redis > backend > celery > nginx
2. **Resource Allocation**: Prioritize database recovery
3. **Monitoring**: Health checks ensure services are functional

## Performance Optimization

### Best Practices
1. **Monitor regularly**: Use `docker stats` to track usage patterns
2. **Scale gradually**: Increase resources based on actual needs
3. **Test changes**: Always test in staging before production
4. **Document changes**: Keep this file updated with any modifications

### Resource Efficiency
- **Shared volumes**: Reduce disk usage with shared static/media volumes
- **Image optimization**: Use alpine-based images where possible
- **Layer caching**: Optimize Dockerfile for better build times

## Compliance and Auditing

### Resource Auditing
```bash
# Generate resource usage report
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Check compliance with limits
docker inspect $(docker ps -q) | jq '.[] | {Name: .Name, Resources: .HostConfig.Resources}'
```

### Change Management
- **Version Control**: All changes tracked in git
- **Testing**: Resource changes tested in development first
- **Documentation**: Updates to this file for all changes
- **Approval**: Production changes require team approval

---

**Last Updated**: July 15, 2025
**Author**: Infrastructure Safety Engineer
**Review Schedule**: Monthly