# Optimization Agent Initialization Instructions

## How to Use This System Prompt

### 1. Starting a New Session with Claude

Copy the entire contents of `OPTIMIZATION_AGENT_SYSTEM_PROMPT.md` and use it as your initial message to Claude, prefaced with:

```
You are now operating as the System Optimization Agent for Session 129. Please confirm your understanding of the mission and begin the optimization protocol.

Current context:
- Working directory: /Users/donkeyking/development/donkey_betz/backend
- System health: 82/100 (from Session 128)
- Critical issues: 3 identified
- Target: 100% optimization

Please begin with Phase 1: Discovery and Analysis.
```

### 2. Required Context Files

Ensure the agent has access to:
- `/documentation/11-optimal-performance/REVIEW_FINDINGS.md` - Current system state
- `/documentation/11-optimal-performance/REVIEW_HANDOFF.md` - Known issues
- `/CLAUDE.md` - System overview and session history

### 3. Environment Setup

Before starting, ensure:
```bash
# Services are running
cd /Users/donkeyking/development/donkey_betz/backend
./start_celery_async.sh
./pgbouncer_start.sh
python manage.py runserver

# Monitoring is active
python api_health_dashboard.py  # In separate terminal
celery -A server flower  # http://localhost:5555

# Logs are accessible
tail -f logs/django.log  # In separate terminal
```

### 4. Agent Capabilities Required

The agent should have access to:
- File reading and writing
- Command execution (bash)
- Git operations
- Database queries
- Performance monitoring tools

### 5. Expected Session Duration

- Phase 1 (Discovery): 30 minutes
- Phase 2 (Documentation): 30 minutes  
- Phase 3 (Optimization): 2-3 hours
- Phase 4 (Testing & Documentation): 30 minutes
- Total: 3-4 hours

### 6. Checkpoints

The agent should provide status updates at:
- After Phase 1 completion (discovery results)
- After each P0 issue resolution
- Every hour during Phase 3
- Before final commit

### 7. Success Metrics

The session is successful when:
- System health score increases from 82 to 95+
- All P0 issues are resolved or documented as major issues
- Performance metrics meet targets
- Complete documentation is created
- All changes are committed and pushed

### 8. Human Oversight Points

Human intervention may be needed for:
- Architectural decisions on major issues
- Database schema changes
- API contract modifications
- Deployment to production

### 9. Sample Agent Responses

The agent should respond in this format:

```markdown
## 🔍 Phase 1: Discovery and Analysis - Starting

### Current Action
Running comprehensive system diagnostics...

### Findings So Far
1. [Finding 1]
2. [Finding 2]

### Next Steps
- [Next action]
- [Following action]

---
Status: In Progress | Elapsed: 5 minutes | Health: 82/100
```

### 10. Contingency Instructions

If the agent encounters issues it cannot resolve:

```markdown
## ⚠️ MAJOR ISSUE DISCOVERED

### Issue
[Description]

### Why I Cannot Proceed
[Explanation]

### Documentation Created
- File: /documentation/11-optimal-performance/MAJOR_ISSUES_DISCOVERED.md
- Entry: Issue #[X]

### Recommended Action
[Human intervention required / Architectural decision needed]

### Continuing With
[Next optimization task]
```

## Agent Performance Expectations

The optimization agent should:
1. Be methodical and systematic
2. Document before implementing
3. Test after every change
4. Maintain system stability
5. Communicate progress clearly
6. Know when to escalate issues
7. Complete all documentation
8. Leave the system better than found

## Monitoring Agent Progress

Track the agent's progress through:
- Git commits: `git log --oneline`
- Documentation updates: `ls -la /documentation/11-optimal-performance/`
- Performance metrics: `python api_health_dashboard.py`
- Test results: `python manage.py test`
- System health: Check the agent's reported score

## Post-Session Validation

After the agent completes:
1. Review all documentation
2. Check git diff for all changes
3. Run full test suite
4. Verify performance improvements
5. Ensure no new errors introduced
6. Validate documentation accuracy

---

**This agent is designed for autonomous operation with minimal supervision. Trust the process but verify the results.**