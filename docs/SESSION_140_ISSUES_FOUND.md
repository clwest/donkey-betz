# Session 140: Issues Found

**Date:** November 20, 2025
**Verification Status:** Partial (Phases 1-2 of 12 completed)
**Total Issues:** 5 Critical, 2 High Priority, 1 Medium Priority

---

## Critical Issues (Priority 0 - Must Fix)

### Issue #1: Missing 3D Generation Agent Registration
**Severity:** Critical
**Component:** Agent Registry
**Affected Feature:** 3D Model Generation (Session 139)
**Impact:** 4 3D models have NO agent attribution

**Description:**
The `ThreeDGenerationAgent` class exists in `agents/three_d_generation_agent.py` with complete implementation, but there is NO corresponding `UnifiedAgentTemplate` database record. This means all 3D models generated since Session 139 have zero agent tracking.

**Evidence:**
```bash
$ ls agents/three_d_generation_agent.py
agents/three_d_generation_agent.py  # ✅ File exists

$ echo "from agents.models import UnifiedAgentTemplate; print(UnifiedAgentTemplate.objects.filter(name='three-d-generation-agent').exists())" | python manage.py shell
False  # ❌ Not registered
```

**Steps to Reproduce:**
1. Check database for 3D agent: `UnifiedAgentTemplate.objects.filter(name__icontains='3d')`
2. Result: No 3D generation agent found
3. Check MiniFigAsset count: 4 models exist
4. Check AgentContribution for 3D models: 0 contributions

**Root Cause:**
Agent registration script was never created or run during Session 139 implementation.

**Recommended Fix:**
```bash
# Create registration script
cat > register_3d_generation_agent.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentSpecialization

# Check if exists
existing = UnifiedAgentTemplate.objects.filter(name='three-d-generation-agent').first()
if existing:
    print(f"⚠️  Agent already exists: {existing.name}")
    sys.exit(0)

# Create agent
agent = UnifiedAgentTemplate.objects.create(
    name='three-d-generation-agent',
    display_name='3D Generation Agent',
    description=(
        'Converts 2D images to 3D models using Replicate TRELLIS. '
        'Handles complete workflow: image validation → 3D generation → '
        'automatic polling → file download → local persistence. '
        'Includes Session 139 enhancements for automatic model completion.'
    ),
    specialization=AgentSpecialization.CONTENT,
    capabilities=[
        'image-to-3d-conversion',
        '3d-model-generation',
        'replicate-trellis',
        'glb-file-generation',
        'stl-conversion',
        'automatic-polling',
        'file-persistence',
        'cdn-to-local-download'
    ],
    required_tools=[
        'replicate-api',
        '3d-storage',
        'polling-system',
        'file-download'
    ],
    optional_tools=[
        'stl-converter',
        'model-viewer'
    ],
    llm_provider='openai',
    llm_model='gpt-5-mini',
    is_active=True,
    uses_tools=True,
    can_initiate_tasks=True,
    can_respond_to_queries=True
)

print(f"✅ Created agent: {agent.name}")
print(f"   Display Name: {agent.display_name}")
print(f"   Specialization: {agent.specialization}")
print(f"   Capabilities: {len(agent.capabilities)}")
EOF

# Run registration
python register_3d_generation_agent.py

# Verify
echo "from agents.models import UnifiedAgentTemplate; agent = UnifiedAgentTemplate.objects.get(name='three-d-generation-agent'); print(f'✅ Registered: {agent.display_name}')" | python manage.py shell
```

**Priority:** P0 (Block: affects all 3D model generation)
**Estimated Time:** 30 minutes
**Assigned To:** Session 141

---

### Issue #2: Celery Beat Database Connection Failure
**Severity:** Critical
**Component:** Background Tasks (Celery)
**Affected Feature:** Automatic 3D model polling, all scheduled tasks
**Impact:** Session 139 polling may not run automatically

**Description:**
Celery Beat scheduler is failing to initialize due to database connection errors. While worker processes are running (5 processes detected), the Beat scheduler cannot query django_celery_beat tables, preventing automatic task scheduling.

**Error Message:**
```
django.db.utils.DatabaseError: could not receive data from server: Bad file descriptor

Traceback:
  File ".../django_celery_beat/schedulers.py", line 290, in enabled_models_qs
    exclude_cron_tasks_query = self._get_crontab_exclude_query()
  ...
  File ".../django/db/backends/utils.py", line 105, in _execute
    return self.cursor.execute(sql, params)
django.db.utils.DatabaseError: could not receive data from server: Bad file descriptor
```

**Steps to Reproduce:**
1. Start Celery: `.venv/bin/celery -A core worker --beat --loglevel=info`
2. Check logs: `tail -f celery.log`
3. Observe database connection error during Beat initialization
4. Tasks are registered but may not execute on schedule

**Observed Behavior:**
```bash
# Tasks are registered
$ python -c "from core.celery import app; print(list(app.conf.beat_schedule.keys()))"
['collect-real-opportunities', 'refresh-ai-opportunities', ..., 'poll-pending-3d-models']  # 18 tasks

# But Beat fails to start
$ tail -f celery.log | grep "beat:"
# No output (Beat not initializing properly)

# Workers are running
$ ps aux | grep "celery -A core" | wc -l
5  # Main process + 4 workers
```

**Root Cause (Hypothesis):**
- PostgreSQL connection pool exhaustion
- Stale database connections from previous Django/Celery processes
- Multiple Celery processes competing for limited DB connections
- `CONN_MAX_AGE` setting causing connection reuse issues

**Impact:**
- `poll_pending_3d_models` task may not run automatically every 30 seconds
- Other scheduled tasks (17 additional tasks) may not execute
- System relies on manual task execution for critical features
- Session 139 automatic 3D model completion not fully operational

**Recommended Fix:**

```bash
# Step 1: Check PostgreSQL connection limits
psql -U donkeybetz -d unified_donkey_betz -c "SHOW max_connections;"
psql -U donkeybetz -d unified_donkey_betz -c "SELECT count(*) as active_connections FROM pg_stat_activity WHERE datname='unified_donkey_betz';"

# Step 2: Kill all stale connections
psql -U donkeybetz -d unified_donkey_betz -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE datname = 'unified_donkey_betz'
  AND pid <> pg_backend_pid()
  AND state = 'idle'
  AND state_change < NOW() - INTERVAL '5 minutes';
"

# Step 3: Restart PostgreSQL
brew services restart postgresql
sleep 5

# Step 4: Update Django settings
# In core/settings.py:
DATABASES = {
    'default': {
        ...
        'CONN_MAX_AGE': 0,  # Close connections immediately (disable connection pooling)
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Step 5: Restart Celery cleanly
pkill -9 -f "celery -A core"
rm -f celery.pid celery.log
sleep 2

.venv/bin/celery -A core worker --beat --loglevel=info --logfile=celery.log --detach --pidfile=celery.pid

# Step 6: Verify Beat is working
sleep 10
tail -f celery.log | grep -E "(beat:|celery beat|poll-pending-3d-models)" | head -20

# Expected output:
# [timestamp] [INFO/Beat] beat: Starting...
# [timestamp] [INFO/Beat] Scheduler: ...
# [timestamp] [INFO] poll-pending-3d-models sent.
```

**Alternative Fix (if above doesn't work):**
```bash
# Run Beat in separate process
.venv/bin/celery -A core worker --loglevel=info --logfile=celery-worker.log --detach --pidfile=celery-worker.pid
.venv/bin/celery -A core beat --loglevel=info --logfile=celery-beat.log --detach --pidfile=celery-beat.pid
```

**Priority:** P0 (Block: automatic polling doesn't work)
**Estimated Time:** 20-30 minutes
**Assigned To:** Session 141
**Dependencies:** None
**Verification:**
```bash
# 1. Check Beat is sending tasks
tail -f celery.log | grep "poll-pending-3d-models"
# Should see task execution every 30 seconds

# 2. Verify task executes successfully
echo "from core.tasks import poll_pending_3d_models; print(poll_pending_3d_models())" | python manage.py shell
# Expected: {'status': 'completed', 'checked': N, 'completed': N, ...}
```

---

### Issue #3: Low Agent Contribution Tracking Rate
**Severity:** Critical
**Component:** Agent Tracking System
**Affected Features:** All content creation, learning systems, revenue attribution
**Impact:** Only 46% of content has agent attribution (23 of 50 items)

**Description:**
The system has 50 content items (33 images, 13 videos, 4 3D models) but only 23 agent contributions, resulting in a 46% tracking rate. This means 27 content items have NO agent attribution, breaking learning systems, revenue tracking, and quality metrics.

**Evidence:**
```bash
# Content inventory
$ echo "from content.models import *; print(f'Images: {ImageHistory.objects.count()}, Videos: {VideoHistory.objects.count()}, 3D: {MiniFigAsset.objects.count()}')" | python manage.py shell
Images: 33, Videos: 13, 3D: 4
Total: 50 items

# Agent contributions
$ echo "from agents.models import AgentContribution; print(f'Contributions: {AgentContribution.objects.count()}')" | python manage.py shell
Contributions: 23

# Tracking rate
23 / 50 = 46%
```

**Breakdown by Agent:**
```
Creation Agent (image_generation): 7 contributions
VideoAgent (video_operations): 10 contributions
AudioAgent: 0 contributions
EditingOrchestratorAgent: 0 contributions
BrandStyleAgent: 0 contributions
CreativeDirectorAgent: 0 contributions
IterationAgent: 0 contributions
LogoAgent: 0 contributions

MISSING: three-d-generation-agent (0 contributions - Issue #1)
```

**Root Cause:**
- Most agent classes don't create `AgentContribution` records
- Service layer functions (image_generation.py, video_provider.py, etc.) don't call agent contribution creation
- Missing integration between agents and contribution tracking system
- No enforcement mechanism to ensure contributions are created

**Impact:**
1. **Learning Systems Broken:** Cannot track which techniques work best
2. **Revenue Attribution Broken:** Cannot determine which agents generate income
3. **Quality Metrics Unavailable:** Cannot measure agent performance
4. **A/B Testing Impossible:** Cannot compare agent versions
5. **User Analytics Limited:** Cannot show user which agents helped them

**Recommended Fix:**

**Step 1: Audit all service functions**
```bash
# Find all content creation functions
grep -r "ImageHistory.objects.create\|VideoHistory.objects.create\|MiniFigAsset.objects.create" content/
```

**Step 2: Add agent contribution creation pattern**
```python
# Template for all service functions
from agents.models import UnifiedAgentTemplate, AgentContribution

def create_content_function(...):
    # Existing content creation logic
    content = ImageHistory.objects.create(...)

    # NEW: Create agent contribution
    try:
        agent = UnifiedAgentTemplate.objects.get(name='appropriate-agent-name')
        AgentContribution.objects.create(
            agent=agent,
            image_history=content,  # or video_history, minifig_asset, etc.
            project=project,
            task_type='image_generation',  # or video_generation, 3d_generation, etc.
            input_data={
                'prompt': prompt,
                'model': model_name,
                'parameters': {...}
            },
            output_data={
                'asset_id': str(content.id),
                'file_path': content.file_path,
                'dimensions': {...}
            },
            execution_time_ms=execution_time,
            tokens_used=tokens_used if applicable else 0,
            api_cost=api_cost if tracked else 0,
            success=True
        )
    except Exception as e:
        logger.error(f"Failed to create agent contribution: {e}")
        # Don't fail content creation if contribution fails

    return content
```

**Step 3: Update key service files**
1. `content/image_generation.py` - All image generation functions
2. `content/video_provider.py` - Video generation and editing
3. `content/minifig_services.py` - 3D model generation (Session 139)
4. `content/audio_services.py` - Audio generation
5. `content/editing_services.py` - Image editing operations

**Priority:** P0 (Block: affects system-wide tracking)
**Estimated Time:** 2-3 hours
**Assigned To:** Session 141
**Dependencies:** Issue #1 must be fixed first (3D agent registration)
**Expected Result:** Tracking rate increases from 46% → 95%+

---

## High Priority Issues (Priority 1 - Should Fix Soon)

### Issue #4: Missing DaVinci Editing Agent Registration
**Severity:** High
**Component:** Agent Registry
**Affected Feature:** Video editing attribution
**Impact:** Video editing operations have no agent tracking

**Description:**
DaVinci Resolve integration exists (Session 103+) with video editing features, but there is no registered agent for video editing attribution. This means video editing operations cannot be tracked or attributed.

**Evidence:**
```bash
$ grep -r "davinci\|resolve" agents/*.py | grep -i "class.*Agent"
# No DaVinci agent class found

$ echo "from agents.models import UnifiedAgentTemplate; print(UnifiedAgentTemplate.objects.filter(name__icontains='davinci').exists())" | python manage.py shell
False
```

**Recommended Fix:**
Similar to Issue #1 - create registration script for DaVinci editing agent.

**Priority:** P1
**Estimated Time:** 30 minutes
**Assigned To:** Session 141

---

### Issue #5: Content Creation Agents with 0 Contributions
**Severity:** High
**Component:** Agent Integration
**Affected Features:** Audio, Brand Style, Creative Direction, Logo, Iteration
**Impact:** 6 agents registered but not creating contributions

**Description:**
6 content creation agents are properly registered but have never created a single contribution:

```
AudioAgent: 0 contributions (audio generation works)
BrandStyleAgent: 0 contributions
CreativeDirectorAgent: 0 contributions
EditingOrchestratorAgent: 0 contributions (editing works)
IterationAgent: 0 contributions
LogoAgent: 0 contributions
```

**Root Cause:**
- Agents are registered ✅
- Services work ✅
- But services don't call these agents ❌
- Missing integration between service layer and agents

**Recommended Fix:**
- Audit which services should use which agents
- Wire agent invocation into service functions
- Ensure agent contribution creation (relates to Issue #3)

**Priority:** P1
**Estimated Time:** 1-2 hours (part of Issue #3 fix)
**Assigned To:** Session 141
**Dependencies:** Issue #3 (low tracking rate)

---

## Medium Priority Issues (Priority 2 - Nice to Have)

### Issue #6: Possible Duplicate Agents
**Severity:** Medium
**Component:** Agent Registry
**Impact:** Confusion, potential conflicts

**Description:**
The agent registry shows possible duplicates:
- "Creation Agent" (image_generation, 7 contributions)
- "image-generation-agent" (exists but contributions unknown)

**Investigation Needed:**
```bash
# Check both agents
echo "
from agents.models import UnifiedAgentTemplate
for agent in UnifiedAgentTemplate.objects.filter(specialization__icontains='image'):
    print(f'{agent.name} | {agent.display_name} | {agent.specialization}')
" | python manage.py shell
```

**Recommended Action:**
- Investigate if these are duplicates
- If yes, merge into single agent
- Update all references to use canonical name

**Priority:** P2
**Estimated Time:** 1 hour
**Assigned To:** Session 142

---

## Summary Table

| ID | Issue | Severity | Component | Status | ETA |
|----|-------|----------|-----------|--------|-----|
| #1 | Missing 3D Agent Registration | Critical | Agent Registry | Open | 30 min |
| #2 | Celery Beat DB Connection | Critical | Background Tasks | Open | 30 min |
| #3 | Low Contribution Tracking (46%) | Critical | Agent Tracking | Open | 2-3 hrs |
| #4 | Missing DaVinci Agent | High | Agent Registry | Open | 30 min |
| #5 | Agents with 0 Contributions | High | Agent Integration | Open | 1-2 hrs |
| #6 | Possible Duplicate Agents | Medium | Agent Registry | Open | 1 hr |

**Total Estimated Fix Time:** 5-8 hours

---

## Session 141 Action Plan

**Critical Path (Must Fix):**
1. ✅ Fix Issue #1: Register 3D agent (30 min)
2. ✅ Fix Issue #2: Restart Celery/PostgreSQL (30 min)
3. ✅ Test 3D generation end-to-end (15 min)
4. ✅ Fix Issue #3: Wire agent contributions (2-3 hrs)
5. ✅ Verify tracking rate improvement (15 min)

**Secondary (Should Fix):**
6. ✅ Fix Issue #4: Register DaVinci agent (30 min)
7. ✅ Fix Issue #5: Wire inactive agents (1-2 hrs)
8. ✅ Complete verification Phases 3-11 (3 hrs)

**Total Session 141 Time:** 8-10 hours
**Expected Reality Score After:** 95-97%

---

**Report Generated:** Session 140
**Next Review:** Session 141
