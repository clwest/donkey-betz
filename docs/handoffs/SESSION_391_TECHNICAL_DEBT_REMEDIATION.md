# Session 391: Technical Debt Remediation Plan

**Created:** December 7, 2025
**Updated:** December 7, 2025 (after model migration)
**Purpose:** Comprehensive plan to address all identified technical debt
**Context:** This handoff was created after a full system audit by Claude, identifying concerns that should be addressed proactively.

---

## SESSION 391 PROGRESS

### Completed This Session:
1. **Full database backup** - `backups/database/unified_donkey_betz_20251207_session391.dump` (123MB)
2. **Migration backups** - All migration files backed up
3. **State documentation** - `backups/database/state_before_session391.txt`
4. **Model migration** - `agents/models.py` → `core/models/agents_registry/models.py`
5. **Compatibility shim** - `agents/models.py` now imports from new location
6. **Health check script** - `scripts/health_check.py` + `make health-check`

### COMPLETED in Session 391:
- ✅ Updated **163+ imports** from `agents.models` to `core.models.agents_registry`
- ✅ Health check passes (7/7)
- ✅ Server starts correctly
- ✅ Both old and new import paths work (shim functional)

### Still TODO (Next Session):
- Move `agents/registry.py` to `core/`
- Delete deprecated agent classes from `agents/` (keep only models.py shim)
- Eventually remove the shim when all imports updated

### Key Files Changed:
| File | Change |
|------|--------|
| `core/models/agents_registry/__init__.py` | NEW - Package exports |
| `core/models/agents_registry/models.py` | NEW - Actual model definitions |
| `agents/models.py` | CHANGED - Now a shim that imports from core |
| `scripts/health_check.py` | NEW - System health verification |
| `Makefile` | UPDATED - Added `health-check` target |

---

---

## Executive Summary

After 390 sessions of human+Claude collaborative development, the platform has grown to:
- **737K lines of code** across the codebase
- **28 specialized agents** in the clean architecture (`core/agents/`)
- **103 data spiders** feeding 31 real sources
- **86 test files** with CI/CD pipeline in place
- **65K-line frontend** in a single HTML file

This document prioritizes and plans remediation of identified technical debt.

---

## Current State vs. Session 274 Master Plan

| Item | Session 274 State | Current State | Status |
|------|-------------------|---------------|--------|
| CI/CD Pipeline | None | ✅ GitHub Actions with tests, lint, security | **DONE** |
| Test Files | 166 scattered | 86 organized | **IMPROVED** |
| Agent Systems | 2 parallel | 2 (shim in place) | **PARTIAL** |
| Frontend | 56K lines | 65K lines | **WORSE** |
| Coverage | Unknown | Configured but unknown % | **PARTIAL** |
| View File Sizes | Large | 14K+ lines max | **UNCHANGED** |

---

## Priority 1: CRITICAL - Complete Agent Migration

### Problem
Two agent systems still exist:
- `agents/` - Legacy (80 files, deprecated shim in place)
- `core/agents/` - Clean architecture (28 agents, actively used)

The shim works but adds cognitive overhead and potential bugs.

### Current State
```
agents/                          # DEPRECATED - Has shim
├── __init__.py                  # Redirects to core.agents with warnings
├── _deprecated/                 # Already marked deprecated
├── base_agent.py               # Legacy BaseContentAgent
├── bookmaker_agent.py          # 46K lines - NOT migrated
└── ... (75+ more files)

core/agents/                     # CLEAN ARCHITECTURE - Active
├── __init__.py                  # Exports 28 agents
├── base_agent.py               # BaseAgent with TimeTravelMixin
├── image_agent.py              # Creation
├── video_agent.py              # Creation
├── audio_agent.py              # Creation
├── three_d_agent.py            # Creation
├── image_editing_agent.py      # Editing
├── video_editing_agent.py      # Editing
├── research_agent.py           # Research
├── personal_assistant_agent.py # Entry point
├── workflow_agent.py           # Orchestration
├── strategy/                   # 4 strategy agents
├── executive/                  # 4 executive agents
├── analysis/                   # 3 analysis agents
├── training/                   # 2 training agents
├── security/                   # 2 security agents
└── business/                   # 5 business research agents
```

### Action Plan

**Session A: Audit & Decide (1 session)**
```bash
# 1. Identify what in agents/ is still imported
grep -r "from agents\." core/ content/ --include="*.py" | grep -v "__pycache__" | sort -u

# 2. Check if any legacy agents have functionality not in core/agents
diff <(ls agents/*.py | xargs -I {} basename {} .py | sort) \
     <(ls core/agents/*.py core/agents/**/*.py | xargs -I {} basename {} .py | sort)

# 3. Identify agents with significant conversation/dream history
python manage.py shell -c "
from core.models_unified_system import Agent, AgentConversation, AgentDream
for a in Agent.objects.all():
    convs = AgentConversation.objects.filter(initiator=a).count()
    dreams = AgentDream.objects.filter(agent=a).count()
    if convs > 0 or dreams > 0:
        print(f'{a.name}: {convs} conversations, {dreams} dreams')
"
```

**Session B: Migration (1-2 sessions)**
1. Move any unique functionality from `agents/` to `core/agents/`
2. Update all imports to use `core.agents`
3. Delete `agents/` directory (keep git history)
4. Update `INSTALLED_APPS` if needed

**Deliverable:** Single agent system in `core/agents/`

---

## Priority 2: HIGH - Split Monolithic View Files

### Problem
Large view files are hard to navigate, test, and modify safely:

| File | Lines | Concern |
|------|-------|---------|
| `views_image.py` | 14,604 | **CRITICAL** - Should be ~1,500 max |
| `views_video.py` | 8,843 | HIGH - Should be ~1,000 max |
| `views_projects_api.py` | 2,143 | Medium |
| `views_odds_sports.py` | 1,969 | Medium |

### Action Plan

**Session C: Split views_image.py (2 sessions)**

Target structure:
```
core/views/
├── __init__.py
├── image/
│   ├── __init__.py              # Re-exports for backwards compatibility
│   ├── generation.py            # Image generation endpoints (~800 lines)
│   ├── editing.py               # Edit/upscale/variations (~800 lines)
│   ├── history.py               # History/gallery endpoints (~400 lines)
│   ├── batch.py                 # Batch operations (~400 lines)
│   ├── styles.py                # Style management (~300 lines)
│   └── utils.py                 # Shared utilities (~200 lines)
├── video/
│   ├── __init__.py
│   ├── generation.py
│   ├── editing.py
│   └── history.py
└── ... (other view modules)
```

Steps:
1. Create `core/views/image/` directory
2. Move generation endpoints to `generation.py`
3. Move editing endpoints to `editing.py`
4. Create `__init__.py` that re-exports all views
5. Update `urls.py` imports
6. Run tests to verify nothing broke
7. Repeat for `views_video.py`

**Deliverable:** No view file over 1,500 lines

---

## Priority 3: HIGH - Frontend Componentization

### Problem
`ai_core/templates/ai_image_studio.html` is **65,031 lines** - a single file containing:
- All HTML structure
- All CSS (inline and embedded)
- All JavaScript (inline)
- All Vue.js components (embedded)

This makes:
- Review by humans nearly impossible
- Changes risky (can't see what you're affecting)
- No code reuse across potential future pages

### Current Reality
This is the hardest item to address because:
1. It works
2. Claude can navigate it (we have context window)
3. Splitting requires careful extraction without breaking functionality

### Action Plan

**Session D: CSS Extraction (1 session)**
```bash
# Extract all <style> blocks to separate CSS files
mkdir -p ai_core/static/css/studio/

# Create base CSS file
# Create component CSS files
# Link from HTML

# Reduction target: ~5,000-10,000 lines from HTML
```

**Session E: JavaScript Extraction (2 sessions)**
```bash
# Extract all <script> blocks to separate JS files
mkdir -p ai_core/static/js/studio/

# Create modular JS files:
# - api.js (API calls)
# - websocket.js (WebSocket handling)
# - components.js (Vue components)
# - utils.js (Utilities)

# Reduction target: ~20,000-30,000 lines from HTML
```

**Session F: Template Splitting (2 sessions)**
```bash
# Use Django template includes
mkdir -p ai_core/templates/studio/partials/

# Create partial templates:
# - _header.html
# - _sidebar.html
# - _generation_panel.html
# - _history_panel.html
# - etc.

# Main template becomes orchestrator
```

**Target:** Main HTML file under 5,000 lines (structural only)

---

## Priority 4: MEDIUM - Test Coverage Improvement

### Current State
- CI/CD pipeline exists (`.github/workflows/test.yml`)
- 86 test files in `tests/`
- Coverage configured but actual percentage unknown
- Linting runs but with `|| true` (non-blocking)

### Action Plan

**Session G: Coverage Baseline (1 session)**
```bash
# 1. Run coverage locally
pytest tests/ --cov=core --cov=content --cov-report=html

# 2. Document baseline percentages
# 3. Identify lowest-coverage critical modules
# 4. Write tests for uncovered agent code
```

**Session H: Critical Path Tests (1-2 sessions)**
Focus on testing the critical user paths:
1. Image generation flow
2. Agent routing
3. Spider data retrieval
4. WebSocket communication

**Target:** 60% coverage on core/, 50% on agents/

---

## Priority 5: MEDIUM - Database Model Consolidation

### Current State
- `core/models_unified_system.py`: 14,144 lines (massive)
- `core/models.py`: 2,357 lines
- `content/models.py`: 3,867 lines
- Total: ~176 models across the system

### Problem
Single 14K-line model file is hard to navigate and understand.

### Action Plan

**Session I: Model Audit (1 session)**
```python
# Categorize all models in models_unified_system.py
# Group by domain:
# - Agent models (Agent, AgentCategory, AgentConversation, etc.)
# - Spider models (SpiderData, SpiderRegistry, etc.)
# - Learning models (AgentLearningOutcome, AgentXP, etc.)
# - Content models (should be in content/)
# - Project models (PartnershipProject, etc.)
```

**Session J: Model Splitting (2 sessions)**
```
core/models/
├── __init__.py          # Re-exports all models
├── agents.py            # Agent, AgentCategory, AgentAssignment
├── spiders.py           # SpiderData, SpiderRegistry
├── learning.py          # AgentLearningOutcome, AgentXP, AgentEvolution
├── scifi.py             # AgentMood, AgentMemory, AgentDream
├── opportunities.py     # Opportunity, OpportunitySetting
└── base.py              # UnifiedBaseModel, shared mixins
```

**Target:** No model file over 2,000 lines

---

## Priority 6: LOW - Linting Enforcement

### Current State
Linting runs in CI but with `|| true` (non-blocking).

### Action Plan

**Session K: Gradual Enforcement (1 session)**
1. Run `black` on entire codebase (auto-format)
2. Run `isort` on entire codebase (sort imports)
3. Fix critical `flake8` errors (E9, F63, F7, F82)
4. Remove `|| true` from CI for critical checks
5. Keep `|| true` for style checks temporarily

---

## Session Execution Order

| Session | Focus | Effort | Impact |
|---------|-------|--------|--------|
| **A** | Agent audit | 1 session | Medium |
| **B** | Agent migration | 1-2 sessions | High |
| **C** | Split views_image.py | 2 sessions | High |
| **D** | CSS extraction | 1 session | Medium |
| **E** | JS extraction | 2 sessions | High |
| **F** | Template splitting | 2 sessions | High |
| **G** | Coverage baseline | 1 session | Medium |
| **H** | Critical path tests | 1-2 sessions | High |
| **I** | Model audit | 1 session | Low |
| **J** | Model splitting | 2 sessions | Medium |
| **K** | Linting enforcement | 1 session | Low |

**Recommended Order:** A → B → C → G → D → E → F → H → I → J → K

**Total Estimated Sessions:** 15-19 sessions

---

## Quick Wins (Can Do Anytime)

These are low-risk improvements any session can tackle:

### 1. Remove Unused Files
```bash
# Find Python files not imported anywhere
# Review and delete dead code
```

### 2. Delete Empty __init__.py
```bash
find . -name "__init__.py" -empty -type f
```

### 3. Remove TODO Comments (Fix or Delete)
```bash
grep -rn "TODO\|FIXME" core/ --include="*.py" | wc -l
# Currently: 24 TODO/FIXME comments
```

### 4. Update CLAUDE.md Agent Count
The documentation says "27 clean agents" but there are actually 28. Keep docs accurate.

---

## Health Check Script

Create this script to run at session start:

```python
#!/usr/bin/env python
"""
System health check for Claude sessions.
Run: python scripts/health_check.py
"""
import os
import sys

def check_agents():
    """Verify agent system is healthy."""
    from core.agent_router import AgentRouter
    router = AgentRouter()
    count = len(router.AGENT_MAP)
    print(f"✓ AgentRouter: {count} agents registered")
    return count >= 20

def check_spiders():
    """Verify spider registry."""
    from ai_core.spiders.spider_registry import SpiderRegistry
    registry = SpiderRegistry()
    count = registry.get_spider_count()['total']
    print(f"✓ SpiderRegistry: {count} spiders")
    return count >= 100

def check_database():
    """Verify database connection."""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✓ Database: Connected")
    return True

def check_models():
    """Count active models."""
    from core.models_unified_system import Agent
    from content.models import ImageHistory
    agents = Agent.objects.filter(is_active=True).count()
    images = ImageHistory.objects.count()
    print(f"✓ Models: {agents} active agents, {images} images")
    return True

def main():
    print("=== System Health Check ===\n")

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    import django
    django.setup()

    checks = [
        ("Agents", check_agents),
        ("Spiders", check_spiders),
        ("Database", check_database),
        ("Models", check_models),
    ]

    all_passed = True
    for name, check in checks:
        try:
            if not check():
                all_passed = False
        except Exception as e:
            print(f"✗ {name}: {e}")
            all_passed = False

    print(f"\n{'All checks passed!' if all_passed else 'Some checks failed.'}")
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## Metrics to Track

Update these after each remediation session:

| Metric | Current (Session 390) | Target | After Session X |
|--------|----------------------|--------|-----------------|
| Frontend HTML lines | 65,031 | < 5,000 | - |
| Largest view file | 14,604 | < 1,500 | - |
| Agent directories | 2 | 1 | - |
| Model file max lines | 14,144 | < 2,000 | - |
| Test coverage | Unknown | 60% | - |
| TODO/FIXME count | 24 | 0 | - |

---

## Notes for Future Claude Sessions

1. **This is a human+Claude project** - Documentation is written for Claude onboarding, not human developers
2. **Session numbers matter** - Reference them in commits and docs for traceability
3. **The frontend is navigable** - Despite 65K lines, Claude can work with it; the split is for human review
4. **Test before committing** - Run `make start` and verify basic functionality
5. **Update 00-START-NEXT-SESSION.md** - After completing any remediation work

---

## Success Criteria

This technical debt initiative is complete when:
- [ ] Single agent system (`core/agents/` only)
- [ ] No view file over 1,500 lines
- [ ] Frontend HTML under 5,000 lines
- [ ] Test coverage over 60%
- [ ] No model file over 2,000 lines
- [ ] CI linting enforced (no `|| true`)
- [ ] Health check script passes

---

**Let's systematically eliminate this debt before it becomes a problem!**
