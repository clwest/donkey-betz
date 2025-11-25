# Code Review Session Prompts

Copy and paste the appropriate prompt into each Claude Code session.

---

## Session 1: AI Assistant & LLM Integration

```
# CODE REVIEW SESSION 1: AI Assistant & LLM Integration

You are conducting a comprehensive code review of the AI Assistant and LLM integration layer for the Unified Donkey Betz platform.

## Your Mission
Review all AI Assistant and LLM-related code, evaluating code quality, architecture, security, performance, error handling, and testing.

## Files to Review (Priority Order)
1. `core/personal_ai_assistant_enhanced.py` (~7,000 lines) - Main AI Assistant
2. `core/llm_enforcer.py` (~400 lines) - LLM configuration and enforcement
3. `core/views_assistant_bypass.py` (~300 lines) - Assistant API endpoints

## Review Focus Areas
- GPT function calling implementation
- Tool execution and routing logic
- Context management (20-message history)
- Error handling in AI responses
- Prompt engineering patterns
- Security of user inputs to LLM
- Token usage optimization
- Async/await patterns

## Output Requirements
Create a detailed report following this structure:

1. **Executive Summary** (2-3 paragraphs)
2. **Scores Table** (Code Quality, Architecture, Security, Performance, Error Handling, Testing - each 1-10)
3. **Critical Issues (P0)** - Must fix before production
4. **High Priority Issues (P1)** - Fix soon
5. **Medium Priority Issues (P2)** - Normal development
6. **Low Priority Issues (P3)** - Nice to have
7. **Positive Findings** - What's done well
8. **Detailed Findings** - Each with file, line, severity, description, impact, recommendation, code example
9. **Files Reviewed Summary Table**

## Instructions
1. Read each file completely using the Read tool
2. Analyze for issues in all categories
3. Document specific line numbers for each finding
4. Provide concrete code examples for fixes
5. Be thorough but practical - focus on real issues

Save your complete report. Begin the review now.
```

---

## Session 2: Image Generation Pipeline

```
# CODE REVIEW SESSION 2: Image Generation Pipeline

You are conducting a comprehensive code review of the Image Generation pipeline for the Unified Donkey Betz platform.

## Your Mission
Review all image generation and manipulation code, evaluating code quality, architecture, security, performance, error handling, and testing.

## Files to Review (Priority Order)
1. `content/image_generation.py` (~1,500 lines) - Stability AI integration
2. `core/views_image.py` (~2,500 lines) - Image operation views
3. `agents/editing_orchestrator_agent.py` (~400 lines) - Image editing orchestration

## Review Focus Areas
- Stability AI API integration patterns
- Image file handling and storage
- Memory management for large images
- Error handling for API failures
- Input validation for image operations
- Rate limiting and credit management
- Batch operation implementation
- Sequential number assignment logic

## Output Requirements
Create a detailed report following this structure:

1. **Executive Summary** (2-3 paragraphs)
2. **Scores Table** (Code Quality, Architecture, Security, Performance, Error Handling, Testing - each 1-10)
3. **Critical Issues (P0)** - Must fix before production
4. **High Priority Issues (P1)** - Fix soon
5. **Medium Priority Issues (P2)** - Normal development
6. **Low Priority Issues (P3)** - Nice to have
7. **Positive Findings** - What's done well
8. **Detailed Findings** - Each with file, line, severity, description, impact, recommendation, code example
9. **Files Reviewed Summary Table**

## Instructions
1. Read each file completely using the Read tool
2. Analyze for issues in all categories
3. Document specific line numbers for each finding
4. Provide concrete code examples for fixes
5. Be thorough but practical - focus on real issues

Save your complete report. Begin the review now.
```

---

## Session 3: Video Pipeline & Processing

```
# CODE REVIEW SESSION 3: Video Pipeline & Processing

You are conducting a comprehensive code review of the Video Pipeline for the Unified Donkey Betz platform.

## Your Mission
Review all video generation, processing, and editing code, evaluating code quality, architecture, security, performance, error handling, and testing.

## Files to Review (Priority Order)
1. `content/video_provider.py` (~800 lines) - Runway ML integration
2. `core/views_video.py` (~2,000 lines) - Video operation views
3. `content/davinci_provider.py` (~900 lines) - DaVinci Resolve integration
4. `content/talking_character_pipeline.py` (~400 lines) - TTS pipeline

## Review Focus Areas
- Runway ML API integration and polling
- ffmpeg command construction and execution
- DaVinci Resolve API usage
- Video file handling and storage
- Async video status polling
- Project association logic
- Memory management for video processing
- Command injection prevention in ffmpeg
- Temporary file cleanup

## Output Requirements
Create a detailed report following this structure:

1. **Executive Summary** (2-3 paragraphs)
2. **Scores Table** (Code Quality, Architecture, Security, Performance, Error Handling, Testing - each 1-10)
3. **Critical Issues (P0)** - Must fix before production
4. **High Priority Issues (P1)** - Fix soon
5. **Medium Priority Issues (P2)** - Normal development
6. **Low Priority Issues (P3)** - Nice to have
7. **Positive Findings** - What's done well
8. **Detailed Findings** - Each with file, line, severity, description, impact, recommendation, code example
9. **Files Reviewed Summary Table**

## Instructions
1. Read each file completely using the Read tool
2. Analyze for issues in all categories
3. Document specific line numbers for each finding
4. Provide concrete code examples for fixes
5. Be thorough but practical - focus on real issues

Save your complete report. Begin the review now.
```

---

## Session 4: Agent System & Orchestration

```
# CODE REVIEW SESSION 4: Agent System & Orchestration

You are conducting a comprehensive code review of the Agent System for the Unified Donkey Betz platform.

## Your Mission
Review all agent and orchestration code, evaluating code quality, architecture, security, performance, error handling, and testing.

## Files to Review (Priority Order)
1. `agents/video_agent.py` (~1,200 lines) - Video orchestration agent
2. `agents/audio_agent.py` (~462 lines) - Audio generation agent
3. `agents/three_d_generation_agent.py` (~350 lines) - 3D model agent
4. `intelligence/agent_query_protocol.py` (~403 lines) - Inter-agent communication
5. Any other files in `agents/` and `intelligence/` directories

## Review Focus Areas
- Agent design patterns and consistency
- Inter-agent communication protocol
- State management within agents
- Error propagation between agents
- Redis pub/sub implementation
- Timeout handling
- Agent registration and discovery
- Circular dependency prevention

## Output Requirements
Create a detailed report following this structure:

1. **Executive Summary** (2-3 paragraphs)
2. **Scores Table** (Code Quality, Architecture, Security, Performance, Error Handling, Testing - each 1-10)
3. **Critical Issues (P0)** - Must fix before production
4. **High Priority Issues (P1)** - Fix soon
5. **Medium Priority Issues (P2)** - Normal development
6. **Low Priority Issues (P3)** - Nice to have
7. **Positive Findings** - What's done well
8. **Detailed Findings** - Each with file, line, severity, description, impact, recommendation, code example
9. **Files Reviewed Summary Table**

## Instructions
1. First, use Glob to find all files in agents/ and intelligence/ directories
2. Read each file completely using the Read tool
3. Analyze for issues in all categories
4. Document specific line numbers for each finding
5. Provide concrete code examples for fixes

Save your complete report. Begin the review now.
```

---

## Session 5: Frontend & Templates

```
# CODE REVIEW SESSION 5: Frontend & Templates

You are conducting a comprehensive code review of the Frontend code for the Unified Donkey Betz platform.

## Your Mission
Review all frontend JavaScript, HTML templates, and CSS, evaluating code quality, architecture, security, performance, error handling, and testing.

## Files to Review (Priority Order)
1. `ai_core/templates/ai_image_studio.html` (~15,000 lines) - Main UI template
2. `core/static/js/unified_v2/common.js` (~500 lines) - Shared JavaScript
3. Any other significant JS files in `core/static/js/`

## Review Focus Areas
- JavaScript code organization
- DOM manipulation efficiency
- Event handling patterns
- WebSocket implementation
- AJAX/fetch error handling
- XSS prevention
- CSRF token handling
- Asset loading optimization
- Mobile responsiveness
- Accessibility (a11y)
- Code duplication in template

## Output Requirements
Create a detailed report following this structure:

1. **Executive Summary** (2-3 paragraphs)
2. **Scores Table** (Code Quality, Architecture, Security, Performance, Error Handling, Testing - each 1-10)
3. **Critical Issues (P0)** - Must fix before production
4. **High Priority Issues (P1)** - Fix soon
5. **Medium Priority Issues (P2)** - Normal development
6. **Low Priority Issues (P3)** - Nice to have
7. **Positive Findings** - What's done well
8. **Detailed Findings** - Each with file, line, severity, description, impact, recommendation, code example
9. **Files Reviewed Summary Table**

## Instructions
1. Read the main template file in chunks if needed (it's ~15,000 lines)
2. Identify JavaScript sections within the template
3. Analyze for issues in all categories
4. Document specific line numbers for each finding
5. Provide concrete code examples for fixes

Save your complete report. Begin the review now.
```

---

## Session 6: Database Models & Data Layer

```
# CODE REVIEW SESSION 6: Database Models & Data Layer

You are conducting a comprehensive code review of the Database Models and Data Layer for the Unified Donkey Betz platform.

## Your Mission
Review all database models, migrations, and data access patterns, evaluating code quality, architecture, security, performance, error handling, and testing.

## Files to Review (Priority Order)
1. `content/models.py` (~800 lines) - Content models
2. `core/models.py` (~300 lines) - Core models
3. `coleadership/models.py` - Co-leadership models
4. Key migration files in `*/migrations/`
5. Any model-related service files

## Review Focus Areas
- Model design and relationships
- Index usage and query optimization
- Field validation and constraints
- UUID vs integer primary keys
- Soft delete vs hard delete patterns
- Model method complexity
- QuerySet optimization (select_related, prefetch_related)
- N+1 query patterns
- Database transaction handling
- Migration safety

## Output Requirements
Create a detailed report following this structure:

1. **Executive Summary** (2-3 paragraphs)
2. **Scores Table** (Code Quality, Architecture, Security, Performance, Error Handling, Testing - each 1-10)
3. **Critical Issues (P0)** - Must fix before production
4. **High Priority Issues (P1)** - Fix soon
5. **Medium Priority Issues (P2)** - Normal development
6. **Low Priority Issues (P3)** - Nice to have
7. **Positive Findings** - What's done well
8. **Detailed Findings** - Each with file, line, severity, description, impact, recommendation, code example
9. **Files Reviewed Summary Table**

## Instructions
1. First, use Glob to find all models.py files
2. Read each model file completely
3. Check for migration patterns
4. Analyze for issues in all categories
5. Document specific line numbers for each finding

Save your complete report. Begin the review now.
```

---

## Session 7: API Integrations & External Services

```
# CODE REVIEW SESSION 7: API Integrations & External Services

You are conducting a comprehensive code review of the External API Integrations for the Unified Donkey Betz platform.

## Your Mission
Review all external API integration code, evaluating code quality, architecture, security, performance, error handling, and testing.

## Files to Review (Priority Order)
1. `content/elevenlabs_provider.py` (~400 lines) - ElevenLabs audio
2. `content/replicate_provider.py` (~370 lines) - Replicate 3D/training
3. `content/character_training.py` (~600 lines) - FLUX LoRA training
4. `content/minifig_services.py` (~500 lines) - 3D pipeline services
5. Any other `*_provider.py` files

## Review Focus Areas
- API key management and security
- Rate limiting implementation
- Retry logic and exponential backoff
- Error response handling
- Timeout configuration
- Response validation
- Cost tracking/credit management
- Webhook handling
- API version management
- Circuit breaker patterns

## Output Requirements
Create a detailed report following this structure:

1. **Executive Summary** (2-3 paragraphs)
2. **Scores Table** (Code Quality, Architecture, Security, Performance, Error Handling, Testing - each 1-10)
3. **Critical Issues (P0)** - Must fix before production
4. **High Priority Issues (P1)** - Fix soon
5. **Medium Priority Issues (P2)** - Normal development
6. **Low Priority Issues (P3)** - Nice to have
7. **Positive Findings** - What's done well
8. **Detailed Findings** - Each with file, line, severity, description, impact, recommendation, code example
9. **Files Reviewed Summary Table**

## Instructions
1. First, use Glob to find all *_provider.py and service files
2. Read each file completely
3. Analyze for issues in all categories
4. Document specific line numbers for each finding
5. Provide concrete code examples for fixes

Save your complete report. Begin the review now.
```

---

## Session 8: Security, Config & Infrastructure

```
# CODE REVIEW SESSION 8: Security, Config & Infrastructure

You are conducting a comprehensive code review of Security, Configuration, and Infrastructure for the Unified Donkey Betz platform.

## Your Mission
Review all security, configuration, and infrastructure code, evaluating code quality, architecture, security, performance, error handling, and testing.

## Files to Review (Priority Order)
1. `core/settings.py` (~500 lines) - Django settings
2. `core/urls.py` (~200 lines) - URL routing
3. `.env` or `.env.example` - Environment configuration
4. `Makefile` - Build/run commands
5. Authentication-related views and middleware
6. Any security-related files

## Review Focus Areas
- Django security settings (DEBUG, ALLOWED_HOSTS, etc.)
- Secret key management
- CORS configuration
- CSRF protection
- Authentication implementation
- Authorization/permissions
- Input sanitization
- SQL injection prevention
- File upload security
- Session management
- Logging configuration
- Error page handling (no stack traces in prod)

## Output Requirements
Create a detailed report following this structure:

1. **Executive Summary** (2-3 paragraphs)
2. **Scores Table** (Code Quality, Architecture, Security, Performance, Error Handling, Testing - each 1-10)
3. **Critical Issues (P0)** - Must fix before production
4. **High Priority Issues (P1)** - Fix soon
5. **Medium Priority Issues (P2)** - Normal development
6. **Low Priority Issues (P3)** - Nice to have
7. **Positive Findings** - What's done well
8. **Detailed Findings** - Each with file, line, severity, description, impact, recommendation, code example
9. **Files Reviewed Summary Table**

## Instructions
1. Read settings.py carefully for security misconfigurations
2. Check URL patterns for exposed endpoints
3. Review authentication flows
4. Look for hardcoded secrets
5. Analyze for issues in all categories

Save your complete report. Begin the review now.
```

---

## Session 9: CONSOLIDATION - Final Report Generation

```
# CODE REVIEW SESSION 9: CONSOLIDATION

You are the consolidation session for the Unified Donkey Betz code review. Your job is to read all 8 session outputs and create the final comprehensive report.

## Your Mission
Read all session outputs and create a unified, prioritized code review report.

## Input Files
Read these files from `docs/code-review/outputs/`:
1. `session-1-output.md` - AI Assistant & LLM
2. `session-2-output.md` - Image Generation
3. `session-3-output.md` - Video Pipeline
4. `session-4-output.md` - Agent System
5. `session-5-output.md` - Frontend
6. `session-6-output.md` - Database
7. `session-7-output.md` - API Integrations
8. `session-8-output.md` - Security & Config

## Consolidation Tasks

1. **Calculate Overall Scores**
   - Average scores across all sessions for each category
   - Identify lowest-scoring areas

2. **Deduplicate Issues**
   - Merge similar issues found across sessions
   - Assign consistent severity ratings

3. **Prioritize All Issues**
   - Create master P0, P1, P2, P3 lists
   - Rank by impact and effort

4. **Identify Cross-Cutting Concerns**
   - Patterns that appear in multiple areas
   - Architectural issues affecting whole system

5. **Generate Recommendations**
   - Short-term fixes (1-2 weeks)
   - Medium-term improvements (1-2 months)
   - Long-term refactoring (3-6 months)

## Output: FINAL-CODE-REVIEW-REPORT.md

Create the final report with this structure:

# Unified Donkey Betz - Comprehensive Code Review Report

## Executive Summary
[Overall health of the codebase, key findings, recommendation]

## Overall Scores
| Category | Score | Assessment |
|----------|-------|------------|
| Code Quality | X/10 | |
| Architecture | X/10 | |
| Security | X/10 | |
| Performance | X/10 | |
| Error Handling | X/10 | |
| Testing | X/10 | |
| **OVERALL** | X/10 | |

## Score Breakdown by Domain
[Table showing each session's scores]

## Critical Issues (P0) - MUST FIX
[Combined and prioritized from all sessions]

## High Priority Issues (P1)
[Combined and prioritized]

## Medium Priority Issues (P2)
[Combined and prioritized]

## Low Priority Issues (P3)
[Combined and prioritized]

## Cross-Cutting Concerns
[Issues that span multiple domains]

## Technical Debt Inventory
[Accumulated shortcuts and workarounds]

## Positive Findings
[Consolidated list of what's done well]

## Recommendations

### Immediate Actions (This Week)
### Short-Term (Next 2 Weeks)
### Medium-Term (Next Month)
### Long-Term (Next Quarter)

## Appendix: Session Summaries
[Brief summary of each session's findings]

---

Begin by reading all session output files, then generate the final report.
```

---

## Quick Reference: Running All Sessions

### Parallel Execution (Sessions 1-8)
Open 8 Claude Code terminals and paste each session prompt simultaneously.

### Sequential Execution (If Needed)
```bash
# Session 1
# [paste Session 1 prompt, wait for completion, save output]

# Session 2
# [paste Session 2 prompt, wait for completion, save output]

# ... continue for all 8 sessions

# Session 9 - Consolidation (after all others complete)
# [paste Session 9 prompt]
```

### Output Directory Setup
```bash
mkdir -p docs/code-review/outputs
```

### Saving Outputs
After each session completes, save the report to:
- `docs/code-review/outputs/session-1-output.md`
- `docs/code-review/outputs/session-2-output.md`
- ... etc.

---

**Document Version:** 1.0
**Last Updated:** November 25, 2025
