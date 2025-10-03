# UKF Troubleshooting Quick Reference

## 🚨 Emergency Commands

```bash
# System not responding
curl http://localhost:8000/api/shared-memory/health/

# Force health check refresh  
curl http://localhost:8000/api/shared-memory/health/?refresh=true

# Emergency cache clear
python manage.py ukf_maintenance --task=cache --force

# Kill long queries
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE query_time > interval '5 minutes';"
```

## 🔍 Quick Diagnostics

### Check System Status
```bash
# One-line health check
python manage.py monitor_embeddings --action=status | grep -E "Total|Coverage|LAST 24"

# Performance snapshot
curl -s http://localhost:8000/api/shared-memory/performance/status/ | jq .
```

### Common Issues → Quick Fixes

| Symptom | Quick Check | Quick Fix |
|---------|-------------|-----------|
| Slow searches | `curl .../performance/status/` | `python manage.py ukf_maintenance --task=optimize` |
| Missing embeddings | `python manage.py monitor_embeddings --action=status` | `python manage.py monitor_embeddings --action=generate` |
| High memory usage | `ps aux | grep python` | `python manage.py ukf_maintenance --task=cleanup` |
| No search results | Check user permissions | Clear cache: `--task=cache` |
| Database slow | `\l+ unified_memory_entries` | `python manage.py ukf_maintenance --task=vacuum` |

## 📊 Key Metrics to Monitor

```bash
# Embedding coverage (should be > 99%)
python -c "from shared_memory.models import UnifiedMemoryEntry; t=UnifiedMemoryEntry.objects.count(); e=UnifiedMemoryEntry.objects.exclude(embedding__isnull=True).count(); print(f'Coverage: {e/t*100:.1f}%')"

# Search performance (should be < 1s)
curl -s http://localhost:8000/api/shared-memory/performance/realtime/ | jq .recent_avg_duration

# Error rate (should be < 5%)
curl -s http://localhost:8000/api/shared-memory/performance/report/ | jq .periods.last_24h.error_rate
```

## 🛠️ Common Maintenance Tasks

### Daily Health Check (2 min)
```bash
# Run this every morning
python manage.py monitor_embeddings --action=status
curl http://localhost:8000/api/shared-memory/health/detailed/ | jq .overall_status
```

### Weekly Optimization (5 min)
```bash
# Run Sunday mornings
python manage.py ukf_maintenance --task=all --dry-run  # Preview
python manage.py ukf_maintenance --task=all            # Execute
```

### When Things Go Wrong
```bash
# 1. Check what's broken
python manage.py monitor_embeddings --action=report

# 2. Try automatic fix
python manage.py ukf_maintenance --task=all --force

# 3. If still broken, check logs
tail -f logs/django.log | grep -E "ERROR|CRITICAL"

# 4. Nuclear option - rebuild cache and indexes
python manage.py ukf_maintenance --task=reindex
python manage.py ukf_maintenance --task=cache --force
```

## 📈 Performance Tuning Checklist

- [ ] Embedding coverage > 99%? → If not: `--action=backfill`
- [ ] Search < 1s average? → If not: `--task=optimize`
- [ ] Cache hit rate > 50%? → If not: Review query patterns
- [ ] Dead tuples < 10%? → If not: `--task=vacuum`
- [ ] Recent errors < 5%? → If not: Check error logs

## 🔧 Developer Commands

```bash
# Test search performance
python manage.py optimize_search_performance --benchmark

# Debug specific entry
python manage.py shell
>>> from shared_memory.models import UnifiedMemoryEntry
>>> entry = UnifiedMemoryEntry.objects.get(id=12345)
>>> print(f"Has embedding: {bool(entry.embedding)}, Length: {len(entry.content_text)}")

# Force regenerate specific embedding
>>> entry.embedding = None
>>> entry.save()
>>> # Then run: python manage.py monitor_embeddings --action=generate
```

## 📞 Escalation

1. **Try Quick Fixes** (5 min)
2. **Run Full Diagnostics** (15 min)
3. **Check Logs** (10 min)
4. **Contact DevOps** if:
   - Health status "unhealthy" > 30 min
   - Search performance > 5s
   - Embedding coverage < 90%
   - Database connections maxed out

## 🎯 Golden Rules

1. **Always dry-run first**: `--dry-run` flag
2. **Monitor after changes**: Watch metrics for 1 hour
3. **Document issues**: Update this guide with solutions
4. **Backup before major ops**: Especially before vacuum/reindex

---
Quick Reference v1.0 | Phase C5 | Updated: August 4, 2025