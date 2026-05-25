<!-- DOC-POINTER-V1 -->
> **⚠ HISTORICAL PLAN (Q4 2025 / Q1 2026 build phase).** Drafted during platform build-out; may be partially shipped, renamed in code, or quietly superseded. Preserved for historical reference, not current truth. For current truth see [`docs/INDEX.md`](../INDEX.md) + [`PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) + the latest handoff. See [`docs/plans/INDEX.md`](INDEX.md) for directory scope.

# System Full Activation Plan

**Purpose:** Complete roadmap to fully utilize every intelligent component in the system
**Created:** Session 461 (December 16, 2025)
**Status:** PLANNING DOCUMENT

---

## Executive Summary

This document catalogs **what exists**, **what's wired up**, **what's not connected**, and **what needs to be built** to achieve 100% system utilization.

**Current State:**
- 200+ intelligent components exist
- ~60% are fully wired and operational
- ~30% exist but aren't connected to the main flow
- ~10% are stubs or incomplete

---

## Part 1: Mythology & Hallucination Prevention

### What Exists

| Component | Location | Status |
|-----------|----------|--------|
| MythologyValidator | `ai_core/agents/mythology_validator.py` | **ACTIVE** |
| MythologyEnforcer | `ai_core/agents/mythology_validator.py` | **ACTIVE** |
| MythologyDetectionService | `mythology/services.py` | **ACTIVE** |
| MythologyPreventionService | `mythology/services.py` | **ACTIVE** |
| HallucinationFlaggingService | `mythology/services.py` | **PARTIAL** |
| HallucinationVerificationService | `mythology/services.py` | **PARTIAL** |
| HallucinationPublisher | `intelligence/hallucination_publisher.py` | **NOT WIRED** |
| `@validate_mythology` decorator | `ai_core/agents/mythology_validator.py` | **AVAILABLE** |

### Where It's Wired

| Integration Point | File | Lines | Status |
|-------------------|------|-------|--------|
| BaseAgent.execute() | `core/agents/base_agent.py` | 783-830 | **ACTIVE** |
| Intelligent Assistant | `core/views_assistant_intelligent.py` | 20+ | **ACTIVE** |
| Unified PA | `core/unified_personal_assistant.py` | 32+ | **ACTIVE** |
| WebSocket Consumer | `core/consumers_hallucination.py` | 9-10 | **ACTIVE** |
| Celery Tasks | `core/tasks.py` | 36 | **ACTIVE** |

### Gaps to Fill

1. **HallucinationPublisher not connected to Redis pub/sub UI**
   - Real-time hallucination dashboard doesn't receive events
   - Fix: Wire `HallucinationPublisher.publish_hallucination_blocked()` into BaseAgent

2. **Auto-verification not triggered**
   - `HallucinationVerificationService._schedule_auto_verification()` is a stub
   - Fix: Create Celery task to process pending verifications

3. **Discord notifications for critical hallucinations**
   - High-risk mythology events don't alert Discord
   - Fix: Add Discord webhook to `MythologyAlert` creation

### Implementation Priority: HIGH

```python
# Task 1: Wire HallucinationPublisher to BaseAgent
# In core/agents/base_agent.py, after mythology_enforcer.enforce():
if validated.get('mythology_corrected'):
    from intelligence.hallucination_publisher import HallucinationPublisher
    publisher = HallucinationPublisher()
    publisher.publish_hallucination_blocked(
        agent_name=self.name,
        original_text=str(result),
        patterns=validated.get('violations', []),
        risk_score=validated.get('risk_score', 0),
        corrected_text=validated.get('result'),
        severity=validated.get('severity', 'medium')
    )
```

---

## Part 2: Agent Ecosystem Activation

### Current Agent Status

| Category | Count | Wired | Active | Notes |
|----------|-------|-------|--------|-------|
| Creation Agents | 4 | 4 | 4 | Fully operational |
| Editing Agents | 2 | 2 | 2 | Fully operational |
| Research Agents | 1 | 1 | 1 | Fully operational |
| Strategy Agents | 4 | 4 | 2 | 2 not routed to |
| Executive Agents | 4 | 4 | 1 | Only CreativeDirector active |
| Analysis Agents | 3 | 3 | 2 | MarketIntelligence unused |
| Training Agents | 2 | 2 | 2 | Fully operational |
| Security Agents | 2 | 2 | 0 | **NOT CALLED** |
| Business Research | 5 | 5 | 5 | Fully operational |
| Development Agents | 4 | 4 | 0 | **NOT ROUTED** |
| Legal Agents | 1 | 1 | 1 | Fully operational |
| Blockchain Audit | 5 | 5 | 5 | Fully operational |
| Stock Audit | 5 | 5 | 5 | Fully operational |
| Orchestration | 4 | 4 | 4 | Fully operational |

### Agents Not Being Routed To

| Agent | Issue | Fix |
|-------|-------|-----|
| ContentAuditAgent | No routing pattern | Add to agent_router.py |
| MemoryIsolationAgent | No routing pattern | Add to agent_router.py |
| CodeGeneratorAgent | No routing pattern | Add patterns: "write code", "generate function" |
| FullStackDeveloperAgent | No routing pattern | Add patterns: "build feature", "create app" |
| CodeReviewAgent | No routing pattern | Add patterns: "review code", "check code" |
| DevOpsAgent | No routing pattern | Add patterns: "deploy", "docker", "kubernetes" |
| CTOAgent | Rarely called | Add patterns: "technical architecture", "tech stack" |
| COOAgent | Rarely called | Add patterns: "operations", "risk assessment" |
| MeetingCoordinatorAgent | Never called | Needs multi-agent workflow trigger |

### Implementation Priority: MEDIUM

```python
# Add to core/agent_router.py ROUTING_PATTERNS:
'code_generator': ['write code', 'generate code', 'create function', 'implement'],
'fullstack_developer': ['build feature', 'create app', 'full stack', 'frontend and backend'],
'code_review': ['review code', 'check code', 'code review', 'audit code'],
'devops': ['deploy', 'docker', 'kubernetes', 'ci/cd', 'pipeline', 'infrastructure'],
'content_audit': ['audit content', 'check content', 'moderate', 'review for safety'],
'memory_isolation': ['isolate memory', 'secure data', 'data isolation'],
```

---

## Part 3: Learning Systems Activation

### Learning Bridges Status

| Bridge | Location | Wired | Active | Notes |
|--------|----------|-------|--------|-------|
| SpiderDataBridge | `core/learning_bridges/spider_data_bridge.py` | Yes | **YES** | Feeds spider data to agents |
| AgentExecutionBridge | `core/learning_bridges/agent_execution_bridge.py` | Yes | Partial | Not recording all executions |
| ApplicationOutcomeBridge | `core/learning_bridges/application_outcome_bridge.py` | Yes | **YES** | Session 461: Now tracks JobApplication outcomes |
| CollaborationBridge | `core/learning_bridges/collaboration_bridge.py` | Yes | Partial | Only HiveMind triggers |
| PersonalizationBridge | `core/learning_bridges/personalization_bridge.py` | Yes | **YES** | Session 461: Now captures chat preferences |
| RevenueAttributionBridge | `core/learning_bridges/revenue_attribution_bridge.py` | Yes | **NO** | No revenue tracking |
| AdvisorFeedbackBridge | `core/learning_bridges/advisor_feedback_bridge.py` | Yes | Partial | Some consultations recorded |
| SportsBettingBridge | `core/learning_bridges/sports_betting_bridge.py` | Yes | **NO** | Sports features archived |

### Gaps to Fill

1. **ApplicationOutcomeBridge** - Track when users report job application success/failure
2. **PersonalizationBridge** - Capture user preferences from chat interactions
3. **RevenueAttributionBridge** - Track which agents/spiders led to revenue

### Implementation Priority: MEDIUM

---

## Part 4: Autonomous Loops Activation

### Current Autonomous Systems

| System | Location | Schedule | Status |
|--------|----------|----------|--------|
| AutonomousIntelligenceLoop | `core/services/autonomous_loop.py` | 15 min | **ACTIVE** |
| StockAuditCycle | `core/tasks.py` | 30 min (market hours) | **ACTIVE** |
| BlockchainAuditCycle | `core/tasks.py` | 15 min | **ACTIVE** |
| BlockchainEventListener | `core/services/blockchain_event_listener.py` | 15s polling | **ACTIVE** |
| AgentDreams | `core/tasks.py` | 30 min | **ACTIVE** |
| DailyDigest | `core/tasks.py` | Daily 8am | **ACTIVE** |

### Not Running / Not Wired

| System | Issue | Fix |
|--------|-------|-----|
| Spider quality learning | No feedback loop | Wire spider success rates to SpiderDataBridge |
| Agent evolution tracking | Passive only | Trigger evolution XP on task completion |
| Prophecy generation | Never triggered | Add to autonomous loop |
| Cross-domain correlation | Not implemented | Create correlation service |

### Implementation Priority: LOW (existing loops work)

---

## Part 5: Spider Network Activation

### Spider Categories Status

| Category | Count | Working | Data Fresh | Notes |
|----------|-------|---------|------------|-------|
| Tech & News | 15 | 12 | Yes | 3 broken RSS feeds |
| Financial | 8 | 8 | Yes | All APIs working |
| Blockchain | 2 | 2 | Yes | API V2 migrated |
| Jobs & Freelance | 10 | 8 | Partial | 2 scrapers blocked |
| Creative & Design | 10 | 7 | Partial | 3 need auth |
| AI & ML | 6 | 5 | Yes | 1 API changed |
| Digital Products | 5 | 4 | Partial | Etsy rate limited |
| Content & Media | 5 | 5 | Yes | All working |
| Legal | 5 | 4 | Yes | 1 Playwright issue |
| Community | 3 | 3 | Yes | Reddit API working |
| Education | 3 | 2 | Partial | 1 blocked |
| Crowdfunding | 4 | 3 | Yes | 1 Playwright issue |

### Spiders Not Feeding Agents

Several spiders collect data but agents don't query them:

| Spider | Data Type | Agents That Should Use It |
|--------|-----------|---------------------------|
| SECSpider | SEC filings | StockAnalystAgent (partially) |
| LegalSpiders | Case law | LegalDocDrafterAgent (not wired) |
| CrowdfundingSpiders | Campaigns | OpportunityPipelineAgent (not wired) |
| EducationSpiders | Courses | (no agent uses this) |

### Implementation Priority: MEDIUM

---

## Part 6: Advisors Activation

### Advisor Usage Status

| Advisor | Consultations (30d) | Status |
|---------|---------------------|--------|
| Warren Buffett | 12 | Active |
| Elon Musk | 8 | Active |
| Gary Vaynerchuk | 5 | Active |
| Others (22) | 0-3 each | **UNDERUTILIZED** |

### Gaps to Fill

1. **Auto-consultation routing** - Certain agent tasks should auto-consult relevant advisors
2. **Advisor specialization** - Advisors don't currently have access to their domain's spider data
3. **Advisor learning** - Advisors don't learn from consultation outcomes

### Proposed Wiring

```python
# In StockAnalystAgent, before returning high-risk findings:
if risk_level in ['HIGH', 'CRITICAL']:
    from advisors.registry import get_advisor
    buffett = get_advisor('warren_buffett_advisor')
    consultation = buffett.consult(
        question=f"What's your analysis of this stock situation: {findings}",
        context={'risk_level': risk_level, 'findings': findings}
    )
    findings['advisor_perspective'] = consultation
```

### Implementation Priority: MEDIUM

---

## Part 7: Validation System Activation

### Existing Validators

| Validator | Location | Status |
|-----------|----------|--------|
| ImageValidationAgent | `core/validation/image_validator.py` | **ACTIVE** |
| VideoValidationAgent | `core/validation/video_validator.py` | **ACTIVE** |
| AgentOrchestrationValidator | `core/validation/agent_validator.py` | **ACTIVE** |
| SpiderValidationAgent | `core/validation/spider_validator.py` | **ACTIVE** |
| AudioValidationAgent | Not created | **MISSING** |
| KnowledgeValidationAgent | Not created | **MISSING** |
| DiscordValidationAgent | Not created | **MISSING** |
| WorkflowValidationAgent | Not created | **MISSING** |

### CLI Already Works

```bash
python manage.py validate_section --all
python manage.py validate_section --section=images
```

### Implementation Priority: LOW (existing validators work)

---

## Part 8: Discord Integration Gaps

### Commands Status

| Category | Commands | Working | Notes |
|----------|----------|---------|-------|
| Content Creation | 8 | 8 | All working |
| Agent Access | 6 | 6 | All working |
| Income Pipeline | 4 | 4 | All working |
| Blockchain Audit | 2 | 2 | New in Session 461 |
| Voice | 4 | 4 | All working |
| System | 5 | 5 | All working |

### Missing Discord Features

1. **Hallucination alerts** - Critical mythology events should post to #system-status
2. **Validation command** - `/validate` to run section validators
3. **Learning status** - `/learning-status` to show agent knowledge stats
4. **Advisor roster** - `/advisors` exists but lacks detail

### Implementation Priority: LOW

---

## Part 9: Implementation Roadmap

### Phase 1: Critical Gaps (Immediate) - COMPLETED Session 461

| Task | Effort | Impact | Status |
|------|--------|--------|--------|
| Wire HallucinationPublisher to BaseAgent | 2 hours | Real-time hallucination visibility | **DONE** |
| Add missing agent routing patterns | 1 hour | 8 more agents accessible | **DONE** |
| Create auto-verification Celery task | 3 hours | Complete hallucination workflow | Pending |

**Session 461 Implementation Notes:**

1. **Agent Routing Patterns Added** (routing_config.py):
   - CodeGeneratorAgent: "write code", "generate code", "function", "implement"
   - FullStackDeveloperAgent: "build feature", "full stack", "frontend and backend"
   - CodeReviewAgent: "review code", "code review", "audit code", "check code"
   - DevOpsAgent: "docker", "kubernetes", "ci/cd", "deploy", "pipeline"
   - ContentAuditAgent: "audit content", "moderate", "content safety"
   - MemoryIsolationAgent: "memory isolation", "data isolation"
   - StockAuditCoordinator: "stock audit", "insider trading", "market manipulation"
   - BlockchainAuditCoordinator: "blockchain audit", "smart contract audit"

2. **HallucinationPublisher Wired** (base_agent.py:801-818):
   - Publishes to Redis on every mythology correction
   - Includes: agent_name, original_text, patterns, risk_score, corrected_text, severity
   - Real-time events available at `hallucination_events` Redis channel
   - History stored in `hallucination_history` Redis key

### Phase 2: Learning Loop Completion - COMPLETED Session 461

| Task | Effort | Impact | Status |
|------|--------|--------|--------|
| Activate PersonalizationBridge | 4 hours | User preference learning | **DONE** |
| Activate ApplicationOutcomeBridge | 3 hours | Job success learning | **DONE** |
| Wire legal spiders to LegalDocDrafterAgent | 2 hours | Better legal research | **DONE** |

**Session 461 Implementation Notes:**

1. **PersonalizationBridge Enhanced** (personalization_bridge.py):
   - Added ConversationMemory signal handler for chat preference extraction
   - Created PREFERENCE_PATTERNS for work_style, job_type, industry, skills, experience_level, salary
   - Extracts preferences like "I want a remote Python job in AI" → {work_style: remote, industry: ai, skills: python}
   - Stores in UserAgentLearning with learning_domain='chat_preferences'

2. **ApplicationOutcomeBridge Extended** (application_outcome_bridge.py):
   - Added JobApplication signal handler (was only tracking Application model)
   - SUCCESS_STATUSES: accepted, offer_received, offer_accepted
   - FAILURE_STATUSES: rejected
   - Tracks: best_platforms, best_methods, success_factors, failure_factors
   - Calculates success rates by platform and application method

3. **LegalDocDrafterAgent Spider Integration** (legal_doc_drafter_agent.py):
   - Added `_get_fresh_legal_spider_intelligence()` method
   - Queries 6 legal spiders: courtlistener, legal_news, findlaw, lii, colorado_family_law, justia_family_law
   - Injects fresh legal intelligence into `_build_legal_prompt()`
   - Legal documents now have access to recent case law and legal news

### Phase 3: Advisor Intelligence - COMPLETED Session 461

| Task | Effort | Impact | Status |
|------|--------|--------|--------|
| Auto-consultation for high-risk findings | 4 hours | Smarter alerts | **DONE** |
| Advisor spider data access | 3 hours | Domain expertise | **DONE** |
| Advisor learning from outcomes | 4 hours | Improving advice | **DONE** |

**Session 461 Implementation Notes:**

1. **Auto-Consultation for High-Risk Findings**:
   - StockAuditCoordinator: Added `_request_advisor_consultations()` method
     - Auto-consults Warren Buffett for CRITICAL/HIGH severity stock alerts
     - Limited to 3 consultations per cycle to control costs
     - Adds `advisor_perspective` to alert data
   - BlockchainAuditCoordinator: Added `_request_blockchain_advisor_consultation()` method
     - Auto-consults Elon Musk for high-risk blockchain security alerts
     - Returns consultation in security report

2. **Advisor Spider Data Access** (llm_advisor_system.py):
   - Created ADVISOR_DOMAIN_SPIDERS mapping (13 domains → spider lists)
   - Added `_get_domain_spider_intelligence()` method to LLMAdvisor class
   - Modified `_build_advisor_prompt()` to inject fresh spider intelligence
   - Each advisor now receives data from their domain:
     - Warren Buffett: financial spiders (yahoo_finance, financial_news, etc.)
     - Cathie Wood: tech + financial spiders (techcrunch, the_verge, yahoo_finance)
     - Elon Musk: crypto + tech spiders (coindesk, etherscan_api, techcrunch)

3. **Advisor Learning from Consultation Outcomes** (advisor_feedback_bridge.py):
   - Created `AutoConsultationLearningLoop` class
   - `track_auto_consultation()`: Records each auto-consultation with severity, type, response
   - `record_outcome()`: Records whether advisor predictions were correct
   - `get_advisor_accuracy_stats()`: Returns advisor accuracy metrics
   - Created `track_audit_advisor_consultation()` convenience function
   - Both audit coordinators now track their consultations for learning
   - Uses system user for anonymous consultation tracking

### Phase 4: Cross-Domain Correlation (Future)

| Task | Effort | Impact |
|------|--------|--------|
| Stock/crypto correlation detection | 8 hours | Cross-market intelligence |
| Multi-source opportunity scoring | 6 hours | Better opportunity ranking |
| Prophecy generation system | 4 hours | Predictive capabilities |

---

## Part 10: Success Metrics

### Current System Health

| Metric | Current | Target | Notes |
|--------|---------|--------|-------|
| Agent utilization | ~70% | 95% | Session 461: +8 agents routed |
| Spider data freshness | 75% | 90% | |
| Learning bridge activation | ~70% | 80% | Session 461: +2 bridges + auto-consultation learning |
| Mythology coverage | 85% | 95% | |
| Advisor utilization | ~50% | 60% | Session 461: Auto-consultations now trigger for audits |

### Measurement Commands

```bash
# Agent utilization
python manage.py shell -c "from core.models_unified_system import Agent; print(f'Active: {Agent.objects.filter(is_active=True).count()}')"

# Spider health
python manage.py validate_section --section=spiders

# Learning stats
python manage.py shell -c "from core.models_unified_system import AgentKnowledge; print(f'Knowledge: {AgentKnowledge.objects.count()}')"

# Mythology stats
python manage.py shell -c "from mythology.models import MythologyEvent; print(f'Events: {MythologyEvent.objects.count()}')"
```

---

## Quick Reference: What to Build Next

**✅ COMPLETED (Session 461):**
- Agent routing patterns added
- HallucinationPublisher wired to BaseAgent
- PersonalizationBridge activated
- ApplicationOutcomeBridge extended
- Legal spiders wired to LegalDocDrafterAgent
- Advisor auto-consultation for Stock/Blockchain audits
- Advisor spider data access
- Advisor consultation outcome learning

### If You Have 2 Hours
1. Create `/validate` Discord command
2. Add Discord alerts for critical mythology events

### If You Have 4 Hours
1. Everything above, plus:
2. Create auto-verification Celery task
3. Add `/learning-status` Discord command

### If You Have 8 Hours
1. Everything above, plus:
2. Implement stock/crypto correlation detection
3. Create prophecy generation system

### If You Have A Full Day
1. Everything above, plus:
2. Create cross-domain correlation service
3. Multi-source opportunity scoring
4. Create AudioValidationAgent and KnowledgeValidationAgent

---

**This document should be updated as components are activated.**
