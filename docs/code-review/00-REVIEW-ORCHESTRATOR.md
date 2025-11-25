# Code Review Orchestrator

**Project:** Unified Donkey Betz - AI Content Studio
**Review Date:** _______________
**Total Sessions Required:** 8 parallel sessions + 1 consolidation session

---

## Overview

This document orchestrates a comprehensive code review across multiple Claude Code sessions. Each session reviews a specific domain of the codebase, producing a standardized report that gets consolidated into a final comprehensive review.

## Session Distribution

| Session | Domain | Primary Files | Estimated Time |
|---------|--------|---------------|----------------|
| **Session 1** | AI Assistant & LLM Integration | `core/personal_ai_assistant_enhanced.py`, `core/llm_enforcer.py` | 30-45 min |
| **Session 2** | Image Generation Pipeline | `content/image_generation.py`, `core/views_image.py` | 30-45 min |
| **Session 3** | Video Pipeline & Processing | `content/video_provider.py`, `core/views_video.py`, `content/davinci_provider.py` | 30-45 min |
| **Session 4** | Agent System & Orchestration | `agents/*.py`, `intelligence/*.py` | 30-45 min |
| **Session 5** | Frontend & Templates | `ai_core/templates/ai_image_studio.html`, `core/static/js/` | 30-45 min |
| **Session 6** | Database Models & Data Layer | `content/models.py`, `core/models.py`, migrations | 25-35 min |
| **Session 7** | API Integrations & External Services | `content/*_provider.py`, API clients | 25-35 min |
| **Session 8** | Security, Config & Infrastructure | `core/settings.py`, auth, URLs, middleware | 25-35 min |
| **Session 9** | **CONSOLIDATION** - Final Report Generation | All session outputs | 45-60 min |

---

## How to Use This System

### Step 1: Distribute Reviews (Parallel)
Run Sessions 1-8 in parallel Claude Code instances. Each session:
1. Copy the session-specific prompt from `01-SESSION-PROMPTS.md`
2. Paste into a new Claude Code instance
3. Let it complete and save output to `outputs/session-X-output.md`

### Step 2: Consolidate (Sequential)
After all 8 sessions complete:
1. Run Session 9 with all outputs available
2. It generates the final `FINAL-CODE-REVIEW-REPORT.md`

---

## Review Standards

Each session must evaluate code against these criteria:

### Code Quality (Score 1-10)
- **Readability**: Clear naming, logical structure, appropriate comments
- **Maintainability**: DRY principles, separation of concerns, modularity
- **Complexity**: Cyclomatic complexity, nesting depth, function length

### Architecture (Score 1-10)
- **Design Patterns**: Appropriate use of patterns, consistency
- **Coupling**: Dependencies between modules, interface design
- **Cohesion**: Single responsibility, focused modules

### Security (Score 1-10)
- **Input Validation**: SQL injection, XSS, command injection prevention
- **Authentication/Authorization**: Proper access controls
- **Secrets Management**: No hardcoded credentials, proper env usage

### Performance (Score 1-10)
- **Database**: N+1 queries, indexing, query optimization
- **Caching**: Appropriate cache usage, invalidation strategies
- **Resource Management**: Memory usage, connection pooling

### Error Handling (Score 1-10)
- **Exception Handling**: Appropriate try/catch, error propagation
- **Logging**: Adequate logging for debugging and monitoring
- **Recovery**: Graceful degradation, retry logic

### Testing (Score 1-10)
- **Coverage**: Unit tests, integration tests present
- **Quality**: Test isolation, meaningful assertions
- **Edge Cases**: Boundary conditions, error paths tested

---

## Output Format

Each session produces a standardized markdown report following this structure:

```markdown
# Code Review: [Domain Name]

## Session Info
- **Session Number:** X
- **Reviewer:** Claude Code
- **Date:** YYYY-MM-DD
- **Files Reviewed:** [list]

## Executive Summary
[2-3 paragraph overview of findings]

## Scores
| Category | Score | Notes |
|----------|-------|-------|
| Code Quality | X/10 | |
| Architecture | X/10 | |
| Security | X/10 | |
| Performance | X/10 | |
| Error Handling | X/10 | |
| Testing | X/10 | |
| **Overall** | X/10 | |

## Critical Issues (P0)
[Issues that must be fixed before production]

## High Priority Issues (P1)
[Issues that should be fixed soon]

## Medium Priority Issues (P2)
[Issues to address in normal development]

## Low Priority Issues (P3)
[Nice-to-have improvements]

## Positive Findings
[What's done well that should be preserved]

## Detailed Findings

### Finding 1: [Title]
- **File:** `path/to/file.py`
- **Line(s):** XXX-XXX
- **Severity:** P0/P1/P2/P3
- **Category:** Security/Performance/etc.
- **Description:** [What the issue is]
- **Impact:** [Why it matters]
- **Recommendation:** [How to fix]
- **Code Example:**
```python
# Current
[problematic code]

# Recommended
[fixed code]
```

[Repeat for each finding]

## Recommendations Summary
1. [Prioritized list of actions]

## Files Reviewed Detail
| File | Lines | Complexity | Issues Found |
|------|-------|------------|--------------|
| file.py | XXX | Low/Med/High | X |
```

---

## File Inventory for Review

### Core Backend (~15,000 lines)
```
core/
├── personal_ai_assistant_enhanced.py  # ~7,000 lines - AI Assistant
├── views_image.py                      # ~2,500 lines - Image operations
├── views_video.py                      # ~2,000 lines - Video operations
├── views_audio.py                      # ~500 lines - Audio operations
├── views_assistant_bypass.py           # ~300 lines - Assistant API
├── llm_enforcer.py                     # ~400 lines - LLM configuration
├── settings.py                         # ~500 lines - Django settings
├── urls.py                             # ~200 lines - URL routing
└── models.py                           # ~300 lines - Core models
```

### Content Layer (~8,000 lines)
```
content/
├── image_generation.py                 # ~1,500 lines - Stability AI
├── video_provider.py                   # ~800 lines - Runway ML
├── davinci_provider.py                 # ~900 lines - DaVinci Resolve
├── elevenlabs_provider.py              # ~400 lines - Audio
├── replicate_provider.py               # ~370 lines - 3D/Training
├── character_training.py               # ~600 lines - FLUX LoRA
├── minifig_services.py                 # ~500 lines - 3D pipeline
├── talking_character_pipeline.py       # ~400 lines - TTS pipeline
└── models.py                           # ~800 lines - Content models
```

### Agent System (~3,500 lines)
```
agents/
├── video_agent.py                      # ~1,200 lines - Video orchestration
├── audio_agent.py                      # ~462 lines - Audio generation
├── three_d_generation_agent.py         # ~350 lines - 3D models
├── editing_orchestrator_agent.py       # ~400 lines - Image editing
└── [other agents]

intelligence/
├── agent_query_protocol.py             # ~403 lines - Inter-agent comms
└── [intelligence modules]
```

### Frontend (~15,000 lines)
```
ai_core/templates/
└── ai_image_studio.html                # ~15,000 lines - Main UI

core/static/js/
└── unified_v2/common.js                # ~500 lines - Shared JS
```

---

## Running the Review

### Prerequisites
- Access to the codebase at `/Users/donkeyking/development/unified-donkey-betz/`
- Claude Code with file read access
- Output directory: `docs/code-review/outputs/`

### Execution Commands

**For each parallel session:**
```
# In Claude Code, paste the session prompt from 01-SESSION-PROMPTS.md
# The prompt will guide the review process
# Save output to docs/code-review/outputs/session-X-output.md
```

**For consolidation:**
```
# After all sessions complete, run Session 9
# It reads all outputs and generates FINAL-CODE-REVIEW-REPORT.md
```

---

## Success Criteria

The review is complete when:
- [ ] All 8 domain sessions have completed
- [ ] Each session has produced a standardized report
- [ ] Session 9 has consolidated all findings
- [ ] Final report includes:
  - [ ] Executive summary with overall health score
  - [ ] Prioritized issue list (P0 → P3)
  - [ ] Architecture diagram assessment
  - [ ] Security audit results
  - [ ] Performance recommendations
  - [ ] Testing coverage analysis
  - [ ] Technical debt inventory
  - [ ] Roadmap recommendations

---

## Next Steps

1. **Read:** `01-SESSION-PROMPTS.md` - Contains copy/paste prompts for each session
2. **Create:** `outputs/` directory for session results
3. **Execute:** Run Sessions 1-8 in parallel
4. **Consolidate:** Run Session 9 to generate final report
5. **Review:** Examine `FINAL-CODE-REVIEW-REPORT.md`

---

**Document Version:** 1.0
**Last Updated:** November 25, 2025
