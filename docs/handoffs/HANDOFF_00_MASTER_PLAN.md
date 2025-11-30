# Master Handoff Plan: Production Readiness Initiative

**Created:** November 29, 2025 (Session 274)
**Goal:** Transform the platform from "wires hanging everywhere" to production-ready
**Total Estimated Sessions:** 12-16 sessions

---

## Executive Summary

After a comprehensive system review, six key areas need attention to make this platform production-ready:

| # | Handoff | Priority | Sessions | Focus |
|---|---------|----------|----------|-------|
| 01 | Frontend Componentization | CRITICAL | 3-4 | Break 56k line file into Django templates |
| 02 | Agent Architecture Unification | HIGH | 2-3 | Merge 2 agent systems into 1 |
| 03 | Sci-Fi Feature Rationalization | MEDIUM | 2 | Simplify 15 features to 7 core |
| 04 | Database Model Consolidation | MEDIUM-HIGH | 2 | Organize 161 models |
| 05 | Test Infrastructure Overhaul | HIGH | 2-3 | Proper tests + CI/CD |
| 06 | Spider Network Wiring | MEDIUM | 2 | Verify 70 spiders, wire to agents |

---

## Recommended Execution Order

### Phase 1: Foundation (Sessions 1-5)
Run these in parallel where possible:

```
Week 1-2:
├── Handoff 05: Test Infrastructure (Session 1-2)
│   └── Get testing foundation in place first
│
├── Handoff 02: Agent Unification (Session 1)
│   └── Start agent audit
│
└── Handoff 01: Frontend (Session 1)
    └── Start frontend analysis
```

**Why this order:**
- Tests first = catch regressions from other changes
- Agent and frontend work are independent, can parallel

### Phase 2: Core Cleanup (Sessions 6-10)

```
Week 2-3:
├── Handoff 01: Frontend (Sessions 2-4)
│   └── Complete componentization
│
├── Handoff 02: Agent Unification (Sessions 2-3)
│   └── Complete migration
│
└── Handoff 05: Test Infrastructure (Session 3)
    └── CI/CD setup
```

### Phase 3: Polish (Sessions 11-16)

```
Week 3-4:
├── Handoff 03: Sci-Fi Rationalization (Sessions 1-2)
│   └── Requires agent unification complete
│
├── Handoff 04: Database Consolidation (Sessions 1-2)
│   └── Depends on sci-fi rationalization
│
└── Handoff 06: Spider Wiring (Sessions 1-2)
    └── Requires agent unification complete
```

---

## Session-by-Session Execution Guide

### Session 1: Test Foundation + Frontend Analysis + Agent Audit

**Start 3 parallel workstreams:**

1. **Test Infrastructure (Handoff 05, Session 1)**
   - Audit all 166 test files
   - Create pytest infrastructure
   - Setup conftest.py and fixtures

2. **Frontend Analysis (Handoff 01, Session 1)**
   - Analyze 56k line HTML file
   - Create directory structure
   - Extract CSS

3. **Agent Audit (Handoff 02, Session 1)**
   - Audit all 22+ legacy agents
   - Create compatibility shim
   - Document differences

---

### Session 2: Continue All Three

1. **Test Infrastructure (Handoff 05, Session 2)**
   - Move non-test files to scripts/
   - Write core unit tests
   - Write integration tests

2. **Frontend Components (Handoff 01, Session 2)**
   - Extract navigation components
   - Extract card components
   - Extract modal components

3. **Agent Migration (Handoff 02, Session 2)**
   - Migrate strategy agents
   - Migrate executive agents
   - Update AgentRouter

---

### Session 3: Complete Core Work

1. **Test CI/CD (Handoff 05, Session 3)**
   - Create GitHub Actions workflow
   - Setup coverage configuration
   - Establish baseline

2. **Frontend Panels (Handoff 01, Session 3)**
   - Extract generation panels
   - Extract forms
   - Extract shared widgets

3. **Agent Completion (Handoff 02, Session 3)**
   - Migrate remaining agents
   - Remove legacy duplicates
   - Enable clean architecture flag

---

### Session 4: Frontend Completion

**Handoff 01, Session 4:**
- Extract JavaScript modules
- Create final page templates
- Update views to use new templates
- Validate all functionality

---

### Session 5: Verification

**Cross-cutting:**
- Run full test suite
- Verify frontend works
- Verify agents work
- Fix any integration issues

---

### Sessions 6-7: Sci-Fi Rationalization

**Handoff 03, Sessions 1-2:**
- Audit feature usage
- Deprecate low-value features
- Simplify remaining features
- Update SciFiIntegrationService

---

### Sessions 8-9: Database Consolidation

**Handoff 04, Sessions 1-2:**
- Audit all 161 models
- Identify unused models
- Create new organized structure
- Migrate models with compatibility shims

---

### Sessions 10-11: Spider Wiring

**Handoff 06, Sessions 1-2:**
- Verify all 70 spiders
- Mark placeholders
- Complete spider-agent bridge
- Add health monitoring

---

### Sessions 12-16: Polish and Validation

**Final sessions:**
- Fix any remaining issues
- Remove deprecated code
- Update documentation
- Final validation

---

## How to Start Each Session

### For Any Claude Code Session:

```bash
# 1. Navigate to project
cd /Users/donkeyking/development/unified-donkey-betz

# 2. Read the master plan
cat docs/handoffs/HANDOFF_00_MASTER_PLAN.md

# 3. Read the specific handoff
cat docs/handoffs/HANDOFF_XX_*.md

# 4. Check git status
git status

# 5. Start the server to verify current state
make start

# 6. Begin tasks from the handoff
```

### Handoff File Locations:

```
docs/handoffs/
├── HANDOFF_00_MASTER_PLAN.md              # This file
├── HANDOFF_01_FRONTEND_COMPONENTIZATION.md
├── HANDOFF_02_AGENT_ARCHITECTURE_UNIFICATION.md
├── HANDOFF_03_SCIFI_FEATURE_RATIONALIZATION.md
├── HANDOFF_04_DATABASE_CONSOLIDATION.md
├── HANDOFF_05_TEST_INFRASTRUCTURE.md
└── HANDOFF_06_SPIDER_WIRING.md
```

---

## Success Criteria

### After Phase 1 (5 sessions):
- [ ] pytest runs with basic coverage
- [ ] CI pipeline exists
- [ ] Frontend componentization started
- [ ] Agent audit complete

### After Phase 2 (10 sessions):
- [ ] Frontend fully componentized (largest file < 500 lines)
- [ ] Single agent architecture (core.agents only)
- [ ] 50%+ test coverage

### After Phase 3 (16 sessions):
- [ ] 7 core sci-fi features (down from 15)
- [ ] Organized model structure
- [ ] Spider network verified and monitored
- [ ] Full CI/CD pipeline
- [ ] Production-ready codebase

---

## Key Metrics to Track

| Metric | Current | After Phase 1 | After Phase 2 | After Phase 3 |
|--------|---------|---------------|---------------|---------------|
| Frontend file size | 56,644 lines | 40,000 | < 500 | < 100 |
| Agent systems | 2 | 2 | 1 | 1 |
| Test coverage | Unknown | 30% | 50% | 60%+ |
| Sci-Fi features | 15 | 15 | 15 | 7 |
| Model classes | 161 | 161 | 161 | < 100 |
| Verified spiders | Unknown | Unknown | Unknown | 20+ |
| CI pipeline | None | Exists | Passing | Full |

---

## Risk Mitigation Across All Handoffs

1. **Feature flags** - All major changes have toggles
2. **Compatibility shims** - Old imports continue working
3. **Database preservation** - No destructive migrations
4. **Incremental delivery** - Each session produces working code
5. **Git branches** - Each handoff can be a separate branch

---

## Common Commands

```bash
# Start server
make start

# Start Celery (for spiders)
make celery

# Run tests
make test

# Check test coverage
make test-coverage

# Check spider health
curl http://localhost:8000/api/spiders/health/

# Check agent routing
python -c "from core.agent_router import AgentRouter; r = AgentRouter(); print(r.AGENT_MAP.keys())"

# Count models
grep "class.*Model" content/models.py agents/models.py core/models_unified_system.py | wc -l
```

---

## Notes for Claude Code Sessions

1. **Always read the specific handoff first** - It has detailed tasks
2. **Update 00-START-NEXT-SESSION.md** when completing a handoff
3. **Commit frequently** - After each successful task
4. **Run tests after changes** - Catch regressions early
5. **Ask for clarification** - If a task is unclear

---

## Contact/Escalation

If a session gets stuck:
1. Document what was attempted
2. Note the specific error or blocker
3. Update the handoff with findings
4. Move to next session/handoff if blocked

---

**Let's build a production-ready platform!**
