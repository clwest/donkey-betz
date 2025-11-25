# Code Review Remediation Orchestrator

**Project:** Unified Donkey Betz - AI Content Studio
**Created:** November 25, 2025
**Total Issues:** 95+ (18 P0, 28 P1, 32 P2, 17 P3)
**Estimated Total Effort:** ~200 hours

---

## Overview

This document orchestrates the remediation of all issues identified in the comprehensive code review. The remediation is organized into **4 phases** with careful attention to:

1. **Dependencies** - Some fixes must complete before others can start
2. **Parallelization** - Independent fixes can run in multiple Claude Code instances
3. **Verification** - Each fix must be tested before marking complete
4. **Code Safety** - Ensuring working code remains functional

---

## Phase Structure

| Phase | Focus | Duration | Execution Mode | Issues |
|-------|-------|----------|----------------|--------|
| **Phase 1** | Critical Security (P0) | Week 1 | **SEQUENTIAL** | 18 |
| **Phase 2** | High Priority (P1) | Weeks 2-3 | Mixed | 28 |
| **Phase 3** | Architecture & Quality (P2) | Month 2 | **PARALLEL** | 32 |
| **Phase 4** | Testing & Polish (P3+) | Month 3 | **PARALLEL** | 17+ |

---

## Execution Rules

### Sequential Execution (One Claude Code at a time)
Use for:
- Security fixes that modify auth/permissions
- Database migrations
- Settings.py changes
- Any fix that modifies shared utilities

**Why:** Prevents merge conflicts and ensures each change is stable before the next.

### Parallel Execution (Multiple Claude Codes simultaneously)
Use for:
- Independent file refactoring
- Adding tests to different modules
- Documentation updates
- Isolated component fixes

**Why:** Maximizes throughput when changes don't overlap.

---

## Pre-Remediation Checklist

Before starting ANY remediation work:

- [ ] Create a new git branch: `git checkout -b remediation/phase-X-description`
- [ ] Verify platform starts: `make start`
- [ ] Run existing tests: `python manage.py test`
- [ ] Note current functionality baseline
- [ ] Have rollback plan ready

---

## Phase Overview

### Phase 1: Critical Security (SEQUENTIAL - One at a time)
**Document:** `01-PHASE1-CRITICAL-SECURITY.md`
**Duration:** 3-5 days
**Mode:** STRICTLY SEQUENTIAL

```
Order of Operations:
1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6 → 1.7 → 1.8 → 1.9

Each task MUST complete and verify before next starts.
```

### Phase 2: High Priority (MIXED - See task dependencies)
**Document:** `02-PHASE2-HIGH-PRIORITY.md`
**Duration:** 1-2 weeks
**Mode:** Sequential for dependencies, Parallel for independent tasks

```
Dependency Groups:
Group A (Sequential): 2.1 → 2.2 → 2.3 (Rate limiting chain)
Group B (Sequential): 2.4 → 2.5 → 2.6 (Input validation chain)
Group C (Parallel): 2.7, 2.8, 2.9, 2.10 (Independent fixes)
```

### Phase 3: Architecture Improvements (PARALLEL)
**Document:** `03-PHASE3-ARCHITECTURE.md`
**Duration:** 2-4 weeks
**Mode:** PARALLEL (files are independent)

```
Can run simultaneously:
- 3.1: Decompose personal_ai_assistant.py (Claude Code 1)
- 3.2: Decompose views_image.py (Claude Code 2)
- 3.3: Frontend modularization (Claude Code 3)
- 3.4: Database model improvements (Claude Code 4)
```

### Phase 4: Testing & Polish (PARALLEL)
**Document:** `04-PHASE4-TESTING.md`
**Duration:** 2-4 weeks
**Mode:** PARALLEL (test files are independent)

```
Can run simultaneously:
- 4.1: Model unit tests (Claude Code 1)
- 4.2: View unit tests (Claude Code 2)
- 4.3: Agent tests (Claude Code 3)
- 4.4: Integration tests (Claude Code 4)
```

---

## Quick Start

### To begin Phase 1 (Critical Security):
```
1. Open ONE Claude Code instance
2. Copy prompt from: docs/code-review/remediation/01-PHASE1-CRITICAL-SECURITY.md
3. Start with Task 1.1
4. Complete and verify before moving to 1.2
5. Continue sequentially through all Phase 1 tasks
```

### To begin Phase 2+ (After Phase 1 complete):
```
1. Check dependency groups in phase document
2. For sequential groups: One Claude Code, one task at a time
3. For parallel groups: Multiple Claude Codes, different tasks
4. Mark completion in tracking document
```

---

## Progress Tracking

### Master Progress
| Phase | Status | Started | Completed | Issues Fixed |
|-------|--------|---------|-----------|--------------|
| Phase 1 | NOT STARTED | | | 0/18 |
| Phase 2 | NOT STARTED | | | 0/28 |
| Phase 3 | NOT STARTED | | | 0/32 |
| Phase 4 | NOT STARTED | | | 0/17 |
| **TOTAL** | | | | **0/95** |

### Daily Log
```
[DATE] - [PHASE.TASK] - [STATUS] - [NOTES]
-------------------------------------------
Example:
2025-11-25 - 1.1 - COMPLETE - Credentials rotated, verified working
2025-11-25 - 1.2 - COMPLETE - SECRET_KEY regenerated
```

---

## Verification Protocol

After EACH fix, verify:

1. **Syntax Check:**
   ```bash
   python -m py_compile [modified_file.py]
   ```

2. **Django Check:**
   ```bash
   python manage.py check
   ```

3. **Platform Start:**
   ```bash
   make start
   # Wait for startup, check for errors
   ```

4. **Functionality Test:**
   - Test the specific feature that was modified
   - Test related features that might be affected

5. **Commit:**
   ```bash
   git add [modified_files]
   git commit -m "fix(security): [description] - Remediation [PHASE.TASK]"
   ```

---

## Rollback Procedures

### If a fix breaks something:

1. **Immediate rollback:**
   ```bash
   git checkout -- [file]  # Discard changes to specific file
   # OR
   git reset --hard HEAD~1  # Undo last commit
   ```

2. **Investigate:**
   - Check error messages
   - Compare with working version
   - Identify what broke

3. **Document:**
   - Note the issue in the task tracking
   - Update approach if needed

4. **Retry:**
   - Apply fix with corrections
   - Re-verify

---

## File Index

| Document | Purpose |
|----------|---------|
| `00-REMEDIATION-ORCHESTRATOR.md` | This file - master coordination |
| `01-PHASE1-CRITICAL-SECURITY.md` | Phase 1 tasks and prompts |
| `02-PHASE2-HIGH-PRIORITY.md` | Phase 2 tasks and prompts |
| `03-PHASE3-ARCHITECTURE.md` | Phase 3 tasks and prompts |
| `04-PHASE4-TESTING.md` | Phase 4 tasks and prompts |
| `05-VERIFICATION-CHECKLIST.md` | Final verification checklist |
| `PROGRESS-LOG.md` | Daily progress tracking |

---

## Emergency Contacts / Resources

- **Code Review Report:** `docs/code-review/FINAL-CODE-REVIEW-REPORT.md`
- **Session Outputs:** `docs/code-review/outputs/session-*-output.md`
- **Platform Docs:** `CLAUDE.md`, `00-START-NEXT-SESSION.md`

---

## Success Criteria

Remediation is complete when:

- [ ] All 18 P0 issues resolved and verified
- [ ] All 28 P1 issues resolved and verified
- [ ] All 32 P2 issues resolved and verified
- [ ] All 17 P3 issues resolved and verified
- [ ] Platform passes all verification checks
- [ ] Test coverage reaches 70%+
- [ ] Security scan shows no critical/high findings
- [ ] Documentation updated

---

**START HERE:** Open `01-PHASE1-CRITICAL-SECURITY.md` and begin Task 1.1
