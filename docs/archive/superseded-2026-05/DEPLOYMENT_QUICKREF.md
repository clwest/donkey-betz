# Deployment Quick Reference Card

**Print this out or keep handy during deployment**

---

## Essential Commands

### Start Everything
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Stop Everything
```bash
docker-compose -f docker-compose.prod.yml down
```

### View All Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Check Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Restart a Service
```bash
docker-compose -f docker-compose.prod.yml restart [service]
# Services: postgres, redis, backend, celery, celery-beat, nginx
```

---

## Health Checks

```bash
# Web health
curl https://yourdomain.com/health/ping/

# Database
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Celery workers
docker-compose -f docker-compose.prod.yml exec celery celery -A core inspect ping
```

---

## Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| 502 Bad Gateway | `docker-compose restart backend` |
| Tasks not running | `docker-compose restart celery-beat celery` |
| Database errors | `docker-compose restart postgres` then `restart backend` |
| SSL errors | `docker-compose restart certbot nginx` |
| Out of memory | `docker-compose restart celery` (or increase server RAM) |

---

## Logs by Service

```bash
# Backend/API errors
docker-compose -f docker-compose.prod.yml logs backend | tail -100

# Celery task errors
docker-compose -f docker-compose.prod.yml logs celery | tail -100

# Scheduler issues
docker-compose -f docker-compose.prod.yml logs celery-beat | tail -50

# Database issues
docker-compose -f docker-compose.prod.yml logs postgres | tail -50

# Nginx/SSL issues
docker-compose -f docker-compose.prod.yml logs nginx | tail -50
```

---

## Database Operations

```bash
# Backup database
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U unified_user unified_donkey_betz > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U unified_user unified_donkey_betz < backup.sql

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Django shell
docker-compose -f docker-compose.prod.yml exec backend python manage.py shell
```

---

## Scaling

```bash
# Scale Celery workers (e.g., to 4)
docker-compose -f docker-compose.prod.yml up -d --scale celery=4

# Scale backend instances (e.g., to 3)
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

---

## Updates & Deployments

```bash
# Pull latest code
git pull origin main

# Rebuild and deploy with zero downtime
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d --no-deps backend celery celery-beat

# Run migrations if needed
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

---

## Monitoring URLs

| Service | URL |
|---------|-----|
| Main App | `https://yourdomain.com` |
| Admin | `https://yourdomain.com/admin/` |
| API Docs | `https://yourdomain.com/api/docs/` |
| Grafana | `https://yourdomain.com:3001` |
| Prometheus | `https://yourdomain.com:9090` |
| Flower | `https://yourdomain.com:5555` |
| Kibana | `https://yourdomain.com:5601` |

---

## Minimum Required Environment Variables

```bash
# .env.prod - MUST SET THESE
DEBUG=False
SECRET_KEY=your-50-char-secret-key
ALLOWED_HOSTS=yourdomain.com
DOMAIN=yourdomain.com
DB_PASSWORD=secure-db-password
OPENAI_API_KEY=sk-...
SSL_EMAIL=admin@yourdomain.com
```

---

## Emergency Procedures

### Full System Restart
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### Database Won't Start
```bash
# Check disk space
df -h
# Check logs
docker-compose -f docker-compose.prod.yml logs postgres
# If corrupted, restore from backup
```

### Completely Out of Memory
```bash
# Kill everything
docker-compose -f docker-compose.prod.yml down
# Prune unused Docker resources
docker system prune -a
# Restart with fewer replicas
docker-compose -f docker-compose.prod.yml up -d --scale celery=1 --scale backend=1
```

---

*Full documentation: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)*
