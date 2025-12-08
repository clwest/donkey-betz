# Start Next Session Here

**Last Session:** 391 - Technical Debt Remediation (Model Migration Complete!)
**Date:** December 7, 2025
**Status:** 103 spiders | 28 code agents | MODEL MIGRATION COMPLETE ✅

---

## Session 391 Accomplishments

### Agent Model Migration - COMPLETE! ✅

Successfully migrated all 10 Django models from `agents/models.py` to `core/models/agents_registry/` with zero database changes required.

| Step | Status | Files Changed |
|------|--------|---------------|
| Database backup | ✅ | 123MB full dump |
| Models migrated | ✅ | `core/models/agents_registry/models.py` |
| Shim created | ✅ | `agents/models.py` (66 lines, re-exports) |
| Imports updated | ✅ | **163+ files** |
| Health check | ✅ | 7/7 checks pass |

### Files Created/Modified

| File | Purpose |
|------|---------|
| `core/models/agents_registry/__init__.py` | Package exports |
| `core/models/agents_registry/models.py` | **Canonical model location** (1800+ lines) |
| `agents/models.py` | Shim for backwards compatibility |
| `scripts/health_check.py` | System health verification |
| `docs/handoffs/SESSION_391_TECHNICAL_DEBT_REMEDIATION.md` | Full remediation plan |
| `backups/database/unified_donkey_betz_20251207_session391.dump` | Database backup |

### Import Migration Stats
- **core/**: 47 files updated
- **ai_core/**: included in first batch
- **content/**: included in first batch
- **scripts/**: 37 files updated
- **intelligence/**: 33 files updated
- **agents/**: subdirectories updated
- **Total**: 163+ files now use `core.models.agents_registry`

### Technical Note: app_label Preservation
All models retain `app_label = 'agents'` in their Meta class:
```python
class Meta:
    app_label = 'agents'  # Keep using agents app tables
```
This means:
- **No database migration needed**
- **All existing data preserved**
- **Tables still named `agents_*`**

---

## Next Priority: agents/ Directory Cleanup

The `agents/models.py` migration is done. Next steps from technical debt plan:

### Phase 1B: Clean Up agents/ Directory (2-3 sessions)
1. **Move `agents/registry.py`** to `core/agents/registry.py`
2. **Audit remaining agents/** files:
   - Which are deprecated and can be deleted?
   - Which need to move to core/agents/?
3. **Remove duplicate agent implementations**

### Phase 2: Split Large Files (4-6 sessions)
1. `views_image.py` (14K lines) → modules
2. `ai_image_studio.html` (65K lines) → components
3. `core/tasks.py` (2K lines) → task modules

See `docs/handoffs/SESSION_391_TECHNICAL_DEBT_REMEDIATION.md` for full 15-19 session plan.

---

## Quick Start Next Session

```bash
# Start services
make start && make celery

# Run health check
make health-check

# Verify model imports work
.venv/bin/python -c "
from core.models.agents_registry import UnifiedAgentTemplate
print(f'Agents in DB: {UnifiedAgentTemplate.objects.count()}')
"

# Open AI Studio
open http://localhost:8000/ai-studio/
```

---

## Current System State

| Component | Count | Status |
|-----------|-------|--------|
| **Spiders** | **103** | All registered |
| **Code Agents** | **28** | In `core/agents/` |
| **DB Agents** | **28** | All active |
| **Learning Hooks** | **21** agents | Recording outcomes |
| **Models Location** | **core/models/agents_registry/** | ✅ Migrated |
| **Shim Status** | **agents/models.py** | Re-exports for backwards compat |

---

## Verification Commands

```bash
# Test model imports (both paths should work)
.venv/bin/python -c "
import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django; django.setup()

# New path (canonical)
from core.models.agents_registry import UnifiedAgentTemplate
print(f'✓ New import: {UnifiedAgentTemplate.objects.count()} agents')

# Old path (shim - still works)
from agents.models import Agent
print(f'✓ Shim import: {Agent.objects.count()} agents')
"

# Check for any remaining old imports in active code
grep -r "from agents\.models import" --include="*.py" | grep -v "^agents/models.py" | grep -v "^docs/"
# Should return NO results (only docs/ and the shim itself)

# Health check
make health-check
```

---

## Handoff Documents

- **This Session:** `docs/handoffs/SESSION_391_TECHNICAL_DEBT_REMEDIATION.md`
- **Previous:** Session 390 - Himalayas.app API Integration
- **Profile Integration:** `docs/handoffs/SESSION_389_USER_PROFILE_INTEGRATION.md`

---

## Important Notes

1. **No Database Migration Needed** - Models use `app_label='agents'` so they still map to `agents_*` tables
2. **Shim is Backwards Compatible** - Old imports via `from agents.models import` still work
3. **Documentation Files Unchanged** - Historical docs in `docs/` still reference old imports (intentional)
4. **Next Priority** - Clean up remaining files in `agents/` directory
5. **Full Backup Available** - `backups/database/unified_donkey_betz_20251207_session391.dump`
