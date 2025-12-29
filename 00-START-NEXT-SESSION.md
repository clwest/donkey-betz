# Session 591 - Start Here

**Previous Session:** 590
**Date:** December 29, 2025
**Focus:** System Insights Ordering Fix + Session 589 Infrastructure Ready

---

## Session 590 Accomplishments

### Fixed System Insights API Ordering Bug

The `system_insights_api` in `core/views_research_demo.py` wasn't ordering results by `-created_at`, causing the UI to potentially show older insights instead of the latest.

**Fix:** Added `.order_by('-created_at')` to the query (line 646).

### Session 589 Infrastructure Verified Working

All execution gap infrastructure from Session 589 is operational:
- Auto-promotion task ran successfully (10 decisions promoted)
- Execution gap reduced from 82.6% to 81.3%
- ThinkingAgent Cycle #14 generated 5 insights, 4 patterns, 3 concerns

---

## Session 591 Options

### Option A: Continue Auto-Promotion

Run another promotion cycle to further reduce the execution gap:

```bash
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.tasks import auto_promote_low_risk_decisions
result = auto_promote_low_risk_decisions(dry_run=False)
print(f'Promoted: {result.get(\"promoted\", 0)} decisions')
"
```

### Option B: Expand Tier 1 Criteria

Current Tier 1 only promotes `guideline` type decisions. Could expand to:
- `product` decision type (299 in draft)
- `research` impact area

### Option C: Continue PA Tools Phase 26

81 tools at 6.03% coverage - continue adding endpoint coverage.

### Option D: ActionIntent Model

Design the ActionIntent model (ChatGPT recommendation):
- Bridge between decisions and execution
- Audit trail from decision → action
- Governance checkpoints

---

## Current System Stats

| Component | Count |
|-----------|-------|
| **Agents** | 71 (47 routable) |
| **Spiders** | 77 (72 working) |
| **PA Tools** | 81 |
| **API Endpoints** | 1,343+ |
| **Celery Tasks** | 230 |
| **Services** | 94 |
| **Decisions (Draft)** | 614 (81.3%) |
| **Decisions (Canonical)** | 127 |

---

## Test Commands

```bash
# Start services
make start && make celery

# Check execution gap metrics
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.services.decision_promotion_rules import get_execution_gap_metrics
metrics = get_execution_gap_metrics()
gap = metrics['execution_gap']
print(f'Execution Gap: {gap[\"draft_percentage\"]:.0f}%')
print(f'Draft: {gap[\"draft_count\"]} | Canonical: {gap[\"canonical_count\"]}')
print(f'Auto-promotable: {metrics[\"auto_promotable\"][\"count\"]}')
"

# Trigger ThinkingAgent cycle
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.tasks import run_autonomous_thinking_cycle
result = run_autonomous_thinking_cycle()
print(f'Cycle #{result.get(\"cycle_number\")}: {result.get(\"insights_count\")} insights')
"

# Access AI Studio
open http://localhost:8000/ai-studio/
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `core/views_research_demo.py` | Session 590 - Fixed system insights ordering |
| `core/services/decision_promotion_rules.py` | Session 589 - Promotion rules |
| `core/services/system_state_aggregator.py` | Session 589 - Gap monitoring |
| `core/tasks.py` | Auto-promotion tasks at lines 19780-19911 |

---

**Session 590: System Insights ordering fix + Execution gap infrastructure verified**
