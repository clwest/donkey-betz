# Deployment Checklist

**Category:** DevOps
**Last Updated:** January 24, 2026
**Owner:** DevOps Agent

---

## Overview

This playbook provides the standard deployment checklist for the Donkey Betz platform. Follow this for every production deployment.

---

## Pre-Deployment Checks

### Code Quality
- [ ] All tests passing (`make test`)
- [ ] No TypeScript errors (`cd frontend && npm run build`)
- [ ] Linting passes (`make lint`)
- [ ] Code review approved
- [ ] PR merged to main

### Database
- [ ] Migrations reviewed for destructive changes
- [ ] Migrations tested on staging
- [ ] Backup created before deployment
- [ ] Rollback plan documented

### Dependencies
- [ ] No new security vulnerabilities (`pip-audit`, `npm audit`)
- [ ] All dependencies pinned
- [ ] Breaking changes in upgrades documented

---

## Deployment Steps

### Step 1: Pre-Flight
```bash
# Check current status
git status
git log --oneline -5

# Verify on main branch
git checkout main
git pull origin main
```

### Step 2: Stop Services
```bash
# Stop Celery workers first (drain tasks)
celery -A core control shutdown

# Stop Daphne/Django
pkill -f daphne

# Verify services stopped
ps aux | grep -E 'celery|daphne'
```

### Step 3: Database Migrations
```bash
# Backup first
pg_dump -h localhost -U donkey donkey_betz > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migrations
python manage.py migrate

# Verify
python manage.py showmigrations | grep "\[ \]"
```

### Step 4: Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Build frontend
cd frontend && npm run build
```

### Step 5: Start Services
```bash
# Start platform
make start

# Start Celery
make celery

# Verify services running
curl http://localhost:8000/health/ping/
```

### Step 6: Verification
```bash
# Check Django admin
open http://localhost:8000/admin/

# Check frontend
open http://localhost:8000/

# Check API health
curl http://localhost:8000/api/v1/health/

# Check Celery
celery -A core inspect ping
```

---

## Post-Deployment Checks

### Functional Verification
- [ ] Login works
- [ ] Dashboard loads
- [ ] Agent execution works
- [ ] WebSocket connections establish
- [ ] Celery tasks processing

### Performance Verification
- [ ] Page load times < 3s
- [ ] API response times < 500ms
- [ ] No memory leaks
- [ ] No CPU spikes

### Monitoring
- [ ] Error rates normal
- [ ] No new exceptions in logs
- [ ] Celery queues draining
- [ ] Database connections healthy

---

## Rollback Procedure

### Quick Rollback (< 5 min)
```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Restart services
make restart
```

### Database Rollback
```bash
# Restore from backup
psql -h localhost -U donkey donkey_betz < backup_YYYYMMDD_HHMMSS.sql

# Revert migrations (if needed)
python manage.py migrate app_name migration_name
```

### Full Rollback
```bash
# Stop all services
pkill -f daphne
pkill -f celery

# Restore database
psql -h localhost -U donkey donkey_betz < backup_YYYYMMDD_HHMMSS.sql

# Checkout previous version
git checkout <previous_tag>

# Reinstall dependencies
pip install -r requirements.txt
cd frontend && npm install

# Rebuild and restart
npm run build
make start && make celery
```

---

## Emergency Contacts

| Role | Contact |
|------|---------|
| Platform Owner | Chris West |
| On-Call DevOps | DevOpsAgent (automated) |

---

## Deployment Schedule

| Environment | Frequency | Window |
|-------------|-----------|--------|
| Development | Continuous | Any time |
| Staging | Daily | 6 PM - 10 PM |
| Production | Weekly | Saturday 2 AM - 6 AM |

---

## Environment-Specific Notes

### Local Development
```bash
make start && make celery
```

### Staging
- Uses staging database
- Mock payment providers
- Test API keys

### Production
- Real database with backups
- Live payment providers
- Production API keys
- Rate limiting enabled

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-24 | 1.0 | Initial playbook |
