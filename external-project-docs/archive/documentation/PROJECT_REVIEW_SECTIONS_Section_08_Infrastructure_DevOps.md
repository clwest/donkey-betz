# Section 8: Infrastructure & DevOps
**Agent Name: Infrastructure Analyst**

## Scope Overview
This section analyzes the infrastructure setup, deployment configurations, and DevOps practices that support the platform's operation.

### Primary Components:
- Docker containerization
- Database architecture (PostgreSQL + pgvector)
- Redis and Celery setup
- Nginx configuration
- Environment management
- Deployment processes

## Analysis Instructions for Claude Code Agent

### 1. Docker Configuration
**Investigate:**
- `docker-compose.yml` - Container orchestration
- `backend/Dockerfile` - Backend container
- `donkey-betz-frontend/Dockerfile` - Frontend container
- Docker networking and volumes

**Key Questions:**
- What services are containerized?
- How are containers networked?
- What volumes are mounted?
- How are images built?

### 2. Database Architecture
**Investigate:**
- PostgreSQL configuration
- pgvector extension setup
- `backend/server/settings/database.py` - DB settings
- Migration files across apps
- Database indexing strategy

**Key Questions:**
- What is the schema design?
- How is pgvector configured?
- What indexes exist?
- How are migrations managed?

### 3. Redis Configuration
**Investigate:**
- Redis setup for caching
- Redis as Celery broker
- `backend/server/settings/cache.py` - Cache config
- Redis persistence settings

**Key Questions:**
- What is cached in Redis?
- How is Redis configured?
- What is the eviction policy?
- Is Redis clustered?

### 4. Celery Task Queue
**Investigate:**
- `backend/server/celery.py` - Celery config
- Task definitions across apps
- `backend/celerybeat-schedule` - Periodic tasks
- Worker configuration

**Key Questions:**
- What tasks are async?
- How many workers run?
- What are the queues?
- How are tasks monitored?

### 5. Nginx Configuration
**Investigate:**
- `nginx/nginx.conf` - Main config
- SSL/TLS setup
- Reverse proxy configuration
- Static file serving

**Key Questions:**
- How is routing configured?
- Is SSL enabled?
- What are the proxy settings?
- How are statics served?

### 6. Environment Management
**Investigate:**
- `.env` files and examples
- `backend/server/settings/` - Settings structure
- Environment-specific configs
- Secret management

**Key Questions:**
- How are environments separated?
- Where are secrets stored?
- What env vars are required?
- How are configs validated?

### 7. CI/CD Pipeline
**Investigate:**
- GitHub Actions workflows
- Build processes
- Test automation
- Deployment scripts

**Key Questions:**
- What CI/CD exists?
- How are tests run?
- What is the deploy process?
- How are releases tagged?

### 8. Monitoring & Logging
**Investigate:**
- `backend/logs/` - Log files
- Logging configuration
- Error tracking setup
- Performance monitoring

**Key Questions:**
- What is logged?
- Where are logs stored?
- What monitoring exists?
- How are errors tracked?

### 9. Backup & Recovery
**Investigate:**
- Database backup scripts
- Media file backups
- Disaster recovery plans
- Data retention policies

**Key Questions:**
- How are backups performed?
- Where are backups stored?
- What is the RTO/RPO?
- How is recovery tested?

### 10. Scaling Architecture
**Investigate:**
- Horizontal scaling capability
- Load balancing setup
- Service discovery
- Auto-scaling rules

**Key Questions:**
- How does it scale?
- What are the bottlenecks?
- Is it cloud-ready?
- What are the limits?

## Critical Files to Review
1. `docker-compose.yml` - Service orchestration
2. `backend/Makefile` - Build and run commands
3. `backend/server/settings/production.py` - Production config
4. `nginx/nginx.conf` - Web server config
5. `backend/scripts/deploy.sh` - Deployment script

## Infrastructure Components
1. **Web Server** - Nginx reverse proxy
2. **Application Server** - Django + Gunicorn
3. **Database** - PostgreSQL + pgvector
4. **Cache** - Redis
5. **Task Queue** - Celery + Redis
6. **Search** - pgvector for embeddings
7. **Storage** - Local filesystem / S3
8. **Monitoring** - Logs + metrics

## Expected Outputs from Analysis
1. Infrastructure architecture diagram
2. Service dependency map
3. Database schema documentation
4. Performance bottleneck analysis
5. Scaling recommendations
6. Security audit findings
7. Cost optimization opportunities
8. Disaster recovery plan

## Special Considerations
- pgvector performance tuning
- Redis memory management
- Celery worker optimization
- Database connection pooling
- Static file CDN setup
- Container security scanning
- Secret rotation procedures
- Backup verification
- Load testing results
- Cloud migration readiness