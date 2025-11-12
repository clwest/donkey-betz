# Autonomous Learning Monitoring Guide
**Last Updated:** October 1, 2025
**Status:** ✅ System Active

---

## Quick Health Check

### 1. Verify Spiders Are Running
```bash
ps aux | grep deploy_freelance_spiders | grep -v grep
```

**Expected:** Process running with ~100% CPU

### 2. Check Data Collection Rate
```bash
python manage.py shell -c "
from persistence.models import SpiderData
from django.db.models import Count
breakdown = SpiderData.objects.values('spider_name').annotate(
    count=Count('spider_name')
).order_by('-count')[:10]
print('Top 10 spider types:')
for item in breakdown:
    print(f\"  {item['spider_name']}: {item['count']}\")
print(f'\nTotal: {SpiderData.objects.count()}')
"
```

**Expected:** Numbers increasing every minute

### 3. Verify 100% Routing Success
```bash
python manage.py shell -c "
from persistence.models import SpiderData
from django.utils import timezone
from datetime import timedelta

recent = SpiderData.objects.filter(
    spider_name__in=['guru', 'toptal', 'remoteok'],
    created_at__gte=timezone.now() - timedelta(minutes=5)
)
routed = recent.filter(
    routed_to_agents__isnull=False
).exclude(routed_to_agents=[]).count()

print(f'Recent entries: {recent.count()}')
print(f'Routed: {routed}')
print(f'Success: {routed/recent.count()*100 if recent.count() else 0:.1f}%')
"
```

**Expected:** 100% success rate

### 4. Sample Routed Entry
```bash
python manage.py shell -c "
from persistence.models import SpiderData
sample = SpiderData.objects.filter(
    spider_name='guru',
    routed_to_agents__isnull=False
).exclude(routed_to_agents=[]).order_by('-created_at').first()

if sample:
    print(f'Spider: {sample.spider_name}')
    print(f'Title: {sample.title}')
    print(f'Agents: {sample.routed_to_agents}')
    print(f'Quality: {sample.quality_score}')
else:
    print('No routed entries found')
"
```

**Expected:** Shows agent list like `['income-builder', 'job_application_agent', 'career-agent']`

---

## Detailed Monitoring

### Learning Bridge Activity
```bash
tail -100 server.log | grep -E "Learning Bridge|Agent Execution Bridge|autonomous"
```

**Expected:** Log entries showing learning events

### Redis Pub/Sub Activity
```bash
redis-cli
> PUBSUB CHANNELS intelligence:*
```

**Expected:** Shows active intelligence channels

### Check Income Agent Reality Score
```bash
python manage.py shell -c "
from agents.models import UnifiedAgentTemplate
try:
    agent = UnifiedAgentTemplate.objects.get(name='income-builder')
    metrics = agent.performance_metrics or {}
    print(f'Income Builder Agent:')
    print(f'  Reality Score: {metrics.get(\"reality_score\", 0.35):.1%}')
    print(f'  Success Rate: {metrics.get(\"success_rate\", 0):.1%}')
    print(f'  Total Executions: {metrics.get(\"total_executions\", 0)}')
except Exception as e:
    print(f'Error: {e}')
"
```

**Expected:** Reality score increasing over time

---

## Troubleshooting

### Problem: Spiders Not Running
```bash
# Check if process exists
ps aux | grep deploy_freelance_spiders

# If not running, start it
python scripts/deploy_freelance_spiders.py 60 &
```

### Problem: Routing at 0%
```bash
# Check recent data
python manage.py shell -c "
from persistence.models import SpiderData
recent = SpiderData.objects.filter(
    spider_name='guru'
).order_by('-created_at').first()
print(f'Routed to: {recent.routed_to_agents if recent else \"No data\"}')
"
```

**If empty:** Check spider code for correct agent names

### Problem: Collection Rate Too Slow
```bash
# Check Celery workers
ps aux | grep celery | grep -v grep

# Restart workers if needed
pkill -f "celery -A core worker"
celery -A core worker -l info -Q spider_queue --concurrency=4 &
```

---

## Performance Metrics

### Current Benchmarks (Session 8)
```
Collection Rate: ~80 entries/minute (guru + remoteok)
Routing Success: 100%
Learning Bridges: 7/7 active
Income Agents: 5 receiving data
Data Quality: 0.3-0.9 (avg 0.6)
```

### Expected Growth (24 Hours)
```
Total Entries: 9,161 → 20,000+
Freelance Jobs: 446 → 5,000+
Routed Entries: 591 → 5,000+
Income Agent Reality: 35% → 60%
```

---

## Key Files

### Spider Deployment Scripts
- `scripts/deploy_freelance_spiders.py` - Income-focused spiders
- `scripts/deploy_production_spiders.py` - General intelligence
- `scripts/monitor_spider_deployment.py` - Monitoring tool

### Spider Implementations
- `ai_core/spiders/base_spider.py` - Base class (routing logic here)
- `ai_core/spiders/specialized/guru_spider.py` - Guru freelance jobs
- `ai_core/spiders/specialized/toptal_spider.py` - Toptal premium jobs
- `ai_core/spiders/specialized/remoteok_spider.py` - Remote tech jobs

### Learning Infrastructure
- `intelligence/learning_bridges.py` - Learning signal handlers
- `persistence/models.py` - SpiderData model
- `agents/models.py` - UnifiedAgentTemplate model

---

## Alert Thresholds

### 🚨 CRITICAL (Action Required)
- Routing success < 50%
- No new data for 10+ minutes
- Learning bridges offline
- Celery workers down

### ⚠️ WARNING (Monitor Closely)
- Routing success 50-90%
- Collection rate < 20/min
- Spider process CPU < 50%

### ✅ HEALTHY
- Routing success > 90%
- Collection rate > 50/min
- All learning bridges active
- Spider process CPU ~100%

---

## Success Indicators

### Daily
- ✅ New spider data every minute
- ✅ 100% routing on new data
- ✅ Learning bridge events in logs
- ✅ Income agent metrics improving

### Weekly
- ✅ 10,000+ new opportunities collected
- ✅ Income agent reality 35% → 60%+
- ✅ Multiple agent categories learning
- ✅ Revenue attribution working

### Monthly
- ✅ 100,000+ opportunities processed
- ✅ Income agent reality 60% → 85%
- ✅ System reality score > 80%
- ✅ Real revenue being generated

---

## Quick Reference Commands

```bash
# Start monitoring
watch -n 60 'python scripts/monitor_spider_deployment.py'

# Check routing success
python manage.py shell -c "from persistence.models import SpiderData; from django.utils import timezone; from datetime import timedelta; recent = SpiderData.objects.filter(created_at__gte=timezone.now() - timedelta(minutes=5)); routed = recent.exclude(routed_to_agents=[]).count(); print(f'{routed}/{recent.count()} = {routed/recent.count()*100 if recent.count() else 0:.1f}%')"

# Watch learning activity
tail -f server.log | grep -E "Learning|autonomous|income-builder"

# Check all agent reality scores
python manage.py shell -c "from agents.models import UnifiedAgentTemplate; agents = UnifiedAgentTemplate.objects.filter(is_active=True)[:10]; [print(f'{a.name}: {(a.performance_metrics or {}).get(\"reality_score\", 0):.1%}') for a in agents]"
```

---

**Status:** ✅ Autonomous Learning Active
**Last Verified:** October 1, 2025 at 22:37 PM
**Next Check:** Every hour for first 24 hours
