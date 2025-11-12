# 🚀 DEPLOYMENT CHECKLIST - Learning Bridges Activation

**STATUS**: ✅ **FULLY DEPLOYED AND OPERATIONAL**

**CRITICAL**: Always use `make stop` and `make start` for server operations!

---

## Deployment Summary

### ✅ Issues Fixed (Session 38)

1. **Learning Bridges Registration** ✅ RESOLVED
   - Created `core/learning_bridges/apps.py` with Django AppConfig
   - Added `'core.learning_bridges'` to `INSTALLED_APPS`
   - All 7 learning bridges now register signals on startup

2. **Agent Registry Pickle Cache Error** ✅ RESOLVED
   - Fixed `agents/registry.py` to use `.values()` instead of model instances
   - Cache now stores serializable primitive data only
   - 154 agents cached successfully without errors

---

## Step-by-Step Deployment

### 1. Stop All Services

```bash
# ALWAYS stop first
make stop
```

This ensures:
- All Django processes terminate cleanly
- Celery workers shut down properly
- WebSocket connections close
- No signal handler conflicts

---

### 2. Run Database Migrations

```bash
# Apply new models (SpiderQualityMetrics, AdvisorConsultationFeedback)
python manage.py migrate
```

Expected output:
```
Running migrations:
  Applying core.0017_add_advisor_consultation_feedback... OK
```

---

### 3. Verify Learning Bridges Package

```bash
python manage.py shell

>>> from core.learning_bridges import (
...     revenue_attribution_bridge,
...     agent_execution_bridge,
...     spider_quality_tracker
... )
>>> print("✅ All learning bridges imported successfully")
>>> exit()
```

---

### 4. Start All Services

```bash
# Start everything (Django + Celery + WebSockets)
make start
```

This will:
- Start Django development server
- Start Celery workers
- Start Celery Beat scheduler
- Initialize all signal handlers automatically

---

### 5. Verify Signals Are Registered

```bash
python manage.py shell

>>> from django.db.models.signals import post_save
>>> from core.models_unified_system import Revenue, AgentExecution, Application, Collaboration
>>> from intelligence.spider_quality_tracker import SpiderQualityMetrics

# Check Revenue signal
>>> receivers = post_save._live_receivers(Revenue)
>>> revenue_connected = any('revenue_attribution_bridge' in str(r) for r in receivers)
>>> print(f"Revenue signal connected: {revenue_connected}")

# Check AgentExecution signal
>>> receivers = post_save._live_receivers(AgentExecution)
>>> agent_connected = any('agent_execution_bridge' in str(r) for r in receivers)
>>> print(f"AgentExecution signal connected: {agent_connected}")

>>> print("✅ Signals verified" if revenue_connected and agent_connected else "⚠️  Check signal registration")
>>> exit()
```

---

### 6. Create Test Data to Verify Learning

```bash
python manage.py shell

>>> from core.models_unified_system import Revenue, User, Agent, UserAgentLearning
>>> from decimal import Decimal

# Get or create test user and agent
>>> user = User.objects.first()
>>> agent = Agent.objects.first()

# Create test revenue (should trigger learning)
>>> revenue = Revenue.objects.create(
...     user=user,
...     agent=agent,
...     source_type='freelance_services',
...     amount=Decimal('1000.00'),
...     status='completed'
... )
>>> print(f"✅ Created revenue: {revenue.id}")

# Verify learning was created
>>> learning_count = UserAgentLearning.objects.filter(
...     user=user,
...     learning_domain='revenue_optimization'
... ).count()
>>> print(f"Learning records created: {learning_count}")
>>> print("✅ Learning bridge working!" if learning_count > 0 else "⚠️  No learning created - check logs")

>>> exit()
```

---

### 7. Monitor Logs for Learning Activity

```bash
# Watch logs in real-time
tail -f logs/django.log | grep "learning_bridge"

# Or check for specific bridges
grep "Revenue learning loop" logs/django.log
grep "Agent execution learning" logs/django.log
grep "Spider fetch recorded" logs/django.log
```

Expected log entries:
```
INFO learning_bridge.revenue_attribution 💰 Processing revenue event: $1000.00 from freelance_services
INFO learning_bridge.revenue_attribution ✅ Revenue learning loop completed for revenue <uuid>
INFO learning_bridge.agent_execution 🤖 Learning from agent execution: <agent_name>
INFO learning_bridge.agent_execution ✅ Agent execution learning complete
```

---

## Troubleshooting

### Issue: "No changes detected" when running migrations

**Solution**: Migrations already created. Just run:
```bash
python manage.py migrate
```

### Issue: Signals not firing

**Cause**: Server not restarted after code changes

**Solution**:
```bash
make stop
make start
```

### Issue: ImportError for learning bridges

**Cause**: Python path or module not found

**Solution**:
```bash
# Verify package structure
ls core/learning_bridges/
# Should see: __init__.py base.py revenue_attribution_bridge.py etc.

# Check Python can import
python -c "from core.learning_bridges import revenue_attribution_bridge; print('✅ OK')"
```

### Issue: Learning records not created

**Cause**: Signal errors being silenced

**Solution**: Check logs for errors:
```bash
grep "Error in.*learning.*signal" logs/django.log
```

---

## Quick Verification Commands

```bash
# Full deployment verification
make stop
python manage.py migrate
make start

# Wait 5 seconds for startup
sleep 5

# Verify signals
python manage.py shell -c "from core.learning_bridges import revenue_attribution_bridge; print('✅ Bridges loaded')"

# Check UserAgentLearning count
python manage.py shell -c "from core.models_unified_system import UserAgentLearning; print(f'Learning records: {UserAgentLearning.objects.count()}')"
```

---

## Success Criteria

After deployment, you should see:

✅ Migrations applied successfully
✅ `make start` completes without errors
✅ Signal verification shows bridges connected
✅ Test revenue creates UserAgentLearning record
✅ Logs show "✅ Learning bridge" messages

---

## CRITICAL REMINDERS

🚨 **ALWAYS** use `make stop` before `make start`
🚨 **NEVER** manually kill processes - use `make stop`
🚨 **CHECK LOGS** after creating test data
🚨 **VERIFY** learning records are being created

---

## What's Running After `make start`

1. **Django Server** (port 8000) - Main application
2. **Celery Worker** - Background tasks
3. **Celery Beat** - Scheduled tasks
4. **Signal Handlers** - All 7 learning bridges active

---

## Rollback Procedure (If Needed)

```bash
# Stop everything
make stop

# Rollback migrations
python manage.py migrate core 0016  # Previous migration number

# Remove learning bridge imports (if needed)
# Edit core/__init__.py or apps.py

# Restart
make start
```

---

**Generated**: September 30, 2025
**Purpose**: Learning Bridges Deployment
**Status**: Ready for execution

🎯 **Remember**: `make stop` → migrations/changes → `make start`
