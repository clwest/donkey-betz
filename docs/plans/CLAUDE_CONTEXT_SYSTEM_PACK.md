# System Context Pack for Claude Code

> Consolidated from uploaded docs to provide Claude Code a single, copy-pastable source of truth for implementing the “System Full Activation Plan” plus the Stock/Blockchain agent group operating patterns.

- Generated: 2025-12-16


---


## System Full Activation Plan (Canonical Build Target)

_Source: `SYSTEM_FULL_ACTIVATION_PLAN.md`_


---

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
| ApplicationOutcomeBridge | `core/learning_bridges/application_outcome_bridge.py` | Yes | **NO** | No job outcomes tracked |
| CollaborationBridge | `core/learning_bridges/collaboration_bridge.py` | Yes | Partial | Only HiveMind triggers |
| PersonalizationBridge | `core/learning_bridges/personalization_bridge.py` | Yes | **NO** | User preferences not captured |
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

### Phase 2: Learning Loop Completion (This Week)

| Task | Effort | Impact |
|------|--------|--------|
| Activate PersonalizationBridge | 4 hours | User preference learning |
| Activate ApplicationOutcomeBridge | 3 hours | Job success learning |
| Wire legal spiders to LegalDocDrafterAgent | 2 hours | Better legal research |

### Phase 3: Advisor Intelligence (Next Week)

| Task | Effort | Impact |
|------|--------|--------|
| Auto-consultation for high-risk findings | 4 hours | Smarter alerts |
| Advisor spider data access | 3 hours | Domain expertise |
| Advisor learning from outcomes | 4 hours | Improving advice |

### Phase 4: Cross-Domain Correlation (Future)

| Task | Effort | Impact |
|------|--------|--------|
| Stock/crypto correlation detection | 8 hours | Cross-market intelligence |
| Multi-source opportunity scoring | 6 hours | Better opportunity ranking |
| Prophecy generation system | 4 hours | Predictive capabilities |

---

## Part 10: Success Metrics

### Current System Health

| Metric | Current | Target |
|--------|---------|--------|
| Agent utilization | 60% | 95% |
| Spider data freshness | 75% | 90% |
| Learning bridge activation | 40% | 80% |
| Mythology coverage | 85% | 95% |
| Advisor utilization | 25% | 60% |

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

### If You Have 2 Hours
1. Add missing agent routing patterns to `core/agent_router.py`
2. Wire HallucinationPublisher to BaseAgent

### If You Have 4 Hours
1. Everything above, plus:
2. Create `/validate` Discord command
3. Add Discord alerts for critical mythology events

### If You Have 8 Hours
1. Everything above, plus:
2. Activate PersonalizationBridge
3. Wire legal spiders to LegalDocDrafterAgent
4. Create auto-verification Celery task

### If You Have A Full Day
1. Everything above, plus:
2. Implement advisor auto-consultation for Stock/Blockchain audit
3. Activate ApplicationOutcomeBridge
4. Create cross-domain correlation service

---

**This document should be updated as components are activated.**


---


## System Intelligence Atlas (Capabilities Map)

_Source: `SYSTEM_INTELLIGENCE_ATLAS.md`_


---

# System Intelligence Atlas

**Complete Catalog of All Intelligent Components**

**Last Updated:** Session 461 (December 16, 2025)
**Total Components:** 200+ intelligent entities

---

## Quick Stats

| Category | Count | Status |
|----------|-------|--------|
| **Agents** | 48 | Active |
| **Advisors** | 25 | Active |
| **Spiders** | 66 | Active |
| **Learning Bridges** | 10 | Active |
| **Autonomous Loops** | 3 | Active |
| **Services** | 40+ | Active |
| **Sci-Fi Features** | 15 | Active |

---

## Part 1: Agents (48 Total)

All agents inherit from `BaseAgent` with TimeTravelMixin for decision tracking.

### Creation Agents (4)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| ImageAgent | `core/agents/image_agent.py` | Generate images (logos, banners, illustrations) | `generate_image`, `generate_variations` |
| VideoAgent | `core/agents/video_agent.py` | Generate videos (text-to-video, animations) | `generate_video`, `animate_image` |
| AudioAgent | `core/agents/audio_agent.py` | Generate audio (TTS, voiceovers) | `generate_voice`, `generate_sfx` |
| ThreeDAgent | `core/agents/three_d_agent.py` | Generate 3D models | `convert_to_3d`, `generate_scene` |

### Editing Agents (2)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| ImageEditingAgent | `core/agents/image_editing_agent.py` | Edit images (upscale, remove bg, etc.) | `upscale`, `remove_background`, `search_replace` |
| VideoEditingAgent | `core/agents/video_editing_agent.py` | Edit videos (trim, effects, text) | `trim_video`, `add_text`, `add_effects` |

### Research Agents (1)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| ResearchAgent | `core/agents/research_agent.py` | Web search + spider network queries | `web_search`, `spider_query`, `analyze_trends` |

### Strategy Agents (4)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| ContentStrategyAgent | `core/agents/strategy/content_strategy_agent.py` | Content recommendations from trends | `analyze_content`, `suggest_topics` |
| BrandIdentityAgent | `core/agents/strategy/brand_identity_agent.py` | Brand colors, styles, consistency | `analyze_brand`, `suggest_identity` |
| SEOOptimizerAgent | `core/agents/strategy/seo_optimizer_agent.py` | Hashtags, metadata, keywords | `generate_keywords`, `optimize_meta` |
| SocialMediaAgent | `core/agents/strategy/social_media_agent.py` | Platform-specific content strategy | `platform_strategy`, `schedule_content` |

### Executive Agents (4)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| CTOAgent | `core/agents/executive/cto_agent.py` | Technical planning and analysis | `technical_review`, `architecture_plan` |
| COOAgent | `core/agents/executive/coo_agent.py` | Operations planning and risk analysis | `ops_review`, `risk_assessment` |
| CreativeDirectorAgent | `core/agents/executive/creative_director_agent.py` | Creative guidance and prompt enhancement | `enhance_prompt`, `creative_direction` |
| MeetingCoordinatorAgent | `core/agents/executive/meeting_coordinator_agent.py` | Coordinates meetings between agents | `schedule_meeting`, `synthesize_outcomes` |

### Analysis Agents (3)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| TrendAnalysisAgent | `core/agents/analysis/trend_analysis_agent.py` | Spider intelligence analysis | `analyze_trends`, `identify_patterns` |
| OpportunityScoringAgent | `core/agents/analysis/opportunity_scoring_agent.py` | Opportunity scoring engine | `score_opportunity`, `rank_opportunities` |
| MarketIntelligenceAgent | `core/agents/analysis/market_intelligence_agent.py` | Market analysis and intelligence | `market_scan`, `competitive_intel` |

### Training Agents (2)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| CharacterTrainingAgent | `core/agents/training/character_training_agent.py` | FLUX LoRA character training | `train_character`, `manage_lora` |
| TrainedCreationAgent | `core/agents/training/trained_creation_agent.py` | LoRA image generation | `generate_with_lora`, `list_trained` |

### Security Agents (2)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| MemoryIsolationAgent | `core/agents/security/memory_isolation_agent.py` | Memory isolation and security | `isolate_memory`, `verify_access` |
| ContentAuditAgent | `core/agents/security/content_audit_agent.py` | Content moderation and audit | `audit_content`, `flag_violations` |

### Business Research Agents (5)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| CompetitorAnalysisAgent | `core/agents/business/competitor_analysis_agent.py` | Competitor analysis, SWOT, positioning | `analyze_competitors`, `swot_analysis` |
| CustomerResearchAgent | `core/agents/business/customer_research_agent.py` | Customer personas, pain points, sentiment | `build_persona`, `analyze_sentiment` |
| BrandStrategyAgent | `core/agents/business/brand_strategy_agent.py` | Brand positioning, messaging, visual direction | `brand_positioning`, `messaging_framework` |
| MarketingStrategyAgent | `core/agents/business/marketing_strategy_agent.py` | Channel strategy, campaigns, funnel optimization | `channel_strategy`, `campaign_plan` |
| BusinessContentStrategyAgent | `core/agents/business/content_strategy_agent.py` | Content pillars, formats, topic ideas | `content_pillars`, `topic_ideation` |

### Development Agents (4)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| CodeGeneratorAgent | `core/agents/code_generator_agent.py` | Generate code from specifications | `generate_code`, `explain_code`, `refactor_code` |
| FullStackDeveloperAgent | `core/agents/fullstack_developer_agent.py` | Build complete features (frontend + backend + DB) | `design_feature`, `implement_backend`, `implement_frontend` |
| CodeReviewAgent | `core/agents/code_review_agent.py` | Review code for quality, security, performance | `review_code`, `check_security`, `check_performance` |
| DevOpsAgent | `core/agents/devops_agent.py` | CI/CD pipelines, Docker, K8s, infrastructure | `create_dockerfile`, `create_pipeline`, `create_k8s_manifests` |

### Legal Agents (1)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| LegalDocDrafterAgent | `core/agents/legal/legal_doc_drafter_agent.py` | Draft legal documents, motions, conferral emails | `draft_motion`, `analyze_motion`, `generate_conferral` |

### Blockchain Audit Agents (5)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| SmartContractAuditorAgent | `core/agents/blockchain/smart_contract_auditor_agent.py` | Audit Solidity code for vulnerabilities | `audit_contract`, `detect_vulnerabilities`, `audit_by_address` |
| TransactionMonitorAgent | `core/agents/blockchain/transaction_monitor_agent.py` | Watch for suspicious tx patterns | `monitor_transactions`, `flag_suspicious` |
| WhaleWatcherAgent | `core/agents/blockchain/whale_watcher_agent.py` | Track large token movements (100+ ETH) | `track_whales`, `alert_movements` |
| ExploitDetectorAgent | `core/agents/blockchain/exploit_detector_agent.py` | Pattern match known exploits | `detect_exploits`, `match_patterns` |
| BlockchainAuditCoordinator | `core/agents/blockchain/blockchain_audit_coordinator.py` | Orchestrate all blockchain audit agents | `run_audit_cycle`, `correlate_findings` |

### Stock Audit Agents (5)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| StockAnalystAgent | `core/agents/stocks/stock_analyst_agent.py` | Analyze SEC filings, fundamentals, valuations | `analyze_filing`, `check_valuation`, `assess_risk` |
| MarketMovementMonitorAgent | `core/agents/stocks/market_movement_monitor_agent.py` | Detect unusual price/volume movements | `monitor_movements`, `detect_spikes` |
| InstitutionalWatcherAgent | `core/agents/stocks/institutional_watcher_agent.py` | Track insider trading & 13F filings | `track_insiders`, `analyze_13f` |
| MarketAnomalyDetectorAgent | `core/agents/stocks/market_anomaly_detector_agent.py` | Detect pump & dump, manipulation patterns | `detect_manipulation`, `flag_anomalies` |
| StockAuditCoordinator | `core/agents/stocks/stock_audit_coordinator.py` | Orchestrate all stock audit agents | `run_audit_cycle`, `correlate_findings` |

### Orchestration Agents (4)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| PersonalAssistantAgent | `core/agents/personal_assistant_agent.py` | Main user interaction and routing | `delegate_to_agent`, `process_request` |
| WorkflowAgent | `core/agents/workflow_agent.py` | Multi-step workflow coordination | `execute_workflow`, `chain_agents` |
| WorkflowOrchestrationAgent | `core/agents/workflow_orchestration_agent.py` | Complex workflow management | `orchestrate_workflow`, `manage_steps` |
| AISeriesWorkflowAgent | `core/agents/ai_series_workflow_agent.py` | Multi-episode content series orchestration | `create_series`, `manage_episodes` |

### Pipeline Agents (2)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| OpportunityPipelineAgent | `core/agents/opportunity_pipeline_agent.py` | Income opportunity pipeline management | `process_opportunity`, `track_application` |
| ContentExecutorAgent | `core/agents/content_executor_agent.py` | Execute content creation pipelines | `execute_content`, `manage_assets` |

---

## Part 2: Advisors (25 Total)

Legendary advisors modeled after real-world experts. Location: `advisors/registry.py`

### Financial & Investment Advisors (6)

| ID | Name | Domain | Expertise Level |
|----|------|--------|-----------------|
| `financial_strategist` | Sarah Chen | Financial Planning | Expert |
| `crypto_expert` | Marcus Rodriguez | Crypto Analysis | Master |
| `options_master` | Jennifer Park | Options Trading | Legend |
| `warren_buffett_advisor` | Warren Buffett (AI) | Investment Strategy | Legend |
| `cathie_wood_advisor` | Cathie Wood (AI) | Investment Strategy | Legend |
| `ray_dalio_advisor` | Ray Dalio (AI) | Risk Management | Legend |

### Business & Strategy Advisors (4)

| ID | Name | Domain | Expertise Level |
|----|------|--------|-----------------|
| `business_strategist` | David Kim | Business Strategy | Expert |
| `startup_guru` | Lisa Thompson | Startup Consulting | Master |
| `gary_vaynerchuk_advisor` | Gary Vaynerchuk (AI) | Marketing Strategy | Legend |
| `grant_cardone_advisor` | Grant Cardone (AI) | Sales Optimization | Legend |

### Technology Advisors (4)

| ID | Name | Domain | Expertise Level |
|----|------|--------|-----------------|
| `tech_architect` | Alex Chen | Technical Architecture | Master |
| `ai_strategist` | Dr. Priya Patel | AI/ML Strategy | Legend |
| `elon_musk_advisor` | Elon Musk (AI) | Product Development | Legend |
| `sam_altman_advisor` | Sam Altman (AI) | AI/ML Strategy | Legend |

### Specialized Domain Advisors (7)

| ID | Name | Domain | Expertise Level |
|----|------|--------|-----------------|
| `sports_analytics_expert` | Mike Johnson | Sports Analytics | Master |
| `real_estate_mogul` | Robert Wilson | Real Estate | Legend |
| `legal_counsel` | Amanda Davis | Legal Counsel | Expert |
| `career_coach` | Dr. Maria Gonzalez | Career Coaching | Master |
| `billy_beane_advisor` | Billy Beane (AI) | Sports Analytics | Legend |
| `haralabos_voulgaris_advisor` | Haralabos Voulgaris (AI) | Sports Analytics | Legend |
| `mr_beast_advisor` | MrBeast (AI) | Content Strategy | Legend |

### Leadership & Specialized Advisors (4)

| ID | Name | Domain | Expertise Level |
|----|------|--------|-----------------|
| `chris_voss_advisor` | Chris Voss (AI) | Negotiation Strategy | Legend |
| `dr_peter_attia_advisor` | Dr. Peter Attia (AI) | Healthcare Strategy | Legend |
| `kevin_mitnick_advisor` | Kevin Mitnick (AI) | Cybersecurity | Legend |
| `sal_khan_advisor` | Sal Khan (AI) | Education Strategy | Legend |

### Advisor Domains

```python
class AdvisorDomain(Enum):
    FINANCIAL_PLANNING = "financial_planning"
    INVESTMENT_STRATEGY = "investment_strategy"
    RISK_MANAGEMENT = "risk_management"
    CRYPTO_ANALYSIS = "crypto_analysis"
    OPTIONS_TRADING = "options_trading"
    BUSINESS_STRATEGY = "business_strategy"
    STARTUP_CONSULTING = "startup_consulting"
    MARKETING_STRATEGY = "marketing_strategy"
    SALES_OPTIMIZATION = "sales_optimization"
    OPERATIONS_MANAGEMENT = "operations_management"
    TECHNICAL_ARCHITECTURE = "technical_architecture"
    AI_ML_STRATEGY = "ai_ml_strategy"
    PRODUCT_DEVELOPMENT = "product_development"
    DATA_STRATEGY = "data_strategy"
    CYBERSECURITY = "cybersecurity"
    LEGAL_COUNSEL = "legal_counsel"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    SPORTS_ANALYTICS = "sports_analytics"
    REAL_ESTATE = "real_estate"
    HEALTHCARE_STRATEGY = "healthcare_strategy"
    EDUCATION_STRATEGY = "education_strategy"
    CONTENT_STRATEGY = "content_strategy"
    CAREER_COACHING = "career_coaching"
    LEADERSHIP_DEVELOPMENT = "leadership_development"
    NEGOTIATION_STRATEGY = "negotiation_strategy"
```

---

## Part 3: Spider Network (66 Total)

Location: `ai_core/spiders/specialized/`

### Tech & News Spiders (15)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| HackerNewsSpider | `hackernews_spider.py` | news.ycombinator.com | Yes (JSON) |
| TechCrunchSpider | `techcrunch_spider.py` | techcrunch.com | RSS |
| DevToSpider | `devto_spider.py` | dev.to | Yes (API) |
| WiredSpider | `wired_spider.py` | wired.com | RSS |
| MITTechReviewSpider | `mit_tech_review_spider.py` | technologyreview.com | RSS |
| AxiosSpider | `axios_spider.py` | axios.com | RSS |
| TheVergeSpider | `verge_spider.py` | theverge.com | RSS |
| ArsTechnicaSpider | `arstechnica_spider.py` | arstechnica.com | RSS |
| BBCSpider | `bbc_spider.py` | bbc.com | RSS |
| NPRSpider | `npr_spider.py` | npr.org | RSS |
| ReutersSpider | `reuters_spider.py` | reuters.com | RSS |
| CNNSpider | `cnn_spider.py` | cnn.com | RSS |
| LifeHackerSpider | `lifehacker_spider.py` | lifehacker.com | RSS |
| SmashingMagazineSpider | `smashingmagazine_spider.py` | smashingmagazine.com | RSS |
| HashNodeSpider | `hashnode_spider.py` | hashnode.com | RSS |

### Financial Spiders (8)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| CoinGeckoSpider | `coingecko_spider.py` | coingecko.com | Yes (API) |
| YahooFinanceSpider | `yahoo_finance_spider.py` | finance.yahoo.com | Yes (API) |
| SeekingAlphaSpider | `seekingalpha_spider.py` | seekingalpha.com | RSS |
| BloombergSpider | `bloomberg_spider.py` | bloomberg.com | RSS |
| FinnhubSpider | `finnhub_spider.py` | finnhub.io | Yes (API) |
| PolygonSpider | `polygon_spider.py` | polygon.io | Yes (API) |
| SECSpider | `sec_spider.py` | sec.gov | Yes (EDGAR) |
| OpenSeaSpider | `opensea_spider.py` | opensea.io | Yes (API) |

### Blockchain Spiders (2)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| EtherscanAPISpider | `etherscan_api_spider.py` | Etherscan API V2 | Yes (API) |
| EtherscanSpider | `etherscan_spider.py` | etherscan.io | RSS |

### Jobs & Freelance Spiders (10)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| RemoteOKSpider | `remoteok_spider.py` | remoteok.com | Yes (JSON) |
| WeWorkRemotelySpider | `weworkremotely_spider.py` | weworkremotely.com | RSS |
| AdzunaSpider | `adzuna_spider.py` | adzuna.com | Yes (API) |
| FlexJobsSpider | `flexjobs_spider.py` | flexjobs.com | Scraper |
| AngelListSpider | `angellist_spider.py` | angel.co | Scraper |
| ToptalSpider | `toptal_spider.py` | toptal.com | Scraper |
| FiverrSpider | `fiverr_spider.py` | fiverr.com | Scraper |
| GuruSpider | `guru_spider.py` | guru.com | Scraper |
| PeoplePerHourSpider | `peopleperhour_spider.py` | peopleperhour.com | Scraper |
| HimalayasSpider | `himalayas_spider.py` | himalayas.app | Yes (API) |

### Creative & Design Spiders (10)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| DribbbleSpider | `dribbble_spider.py` | dribbble.com | Yes (API) |
| BehanceSpider | `behance_spider.py` | behance.net | Yes (API) |
| UnsplashSpider | `unsplash_spider.py` | unsplash.com | Yes (API) |
| FigmaSpider | `figma_spider.py` | figma.com | Scraper |
| CanvaSpider | `canva_spider.py` | canva.com | Scraper |
| ShutterstockSpider | `shutterstock_spider.py` | shutterstock.com | Yes (API) |
| AdobeStockSpider | `adobestock_spider.py` | stock.adobe.com | Yes (API) |
| CreativeMarketSpider | `creativemarket_spider.py` | creativemarket.com | Scraper |
| EnvatoSpider | `envato_spider.py` | envato.com | Scraper |
| 99DesignsSpider | `ninetyninedesigns_spider.py` | 99designs.com | Scraper |

### AI & ML Spiders (6)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| HuggingFaceSpider | `huggingface_spider.py` | huggingface.co | Yes (API) |
| MidjourneySpider | `midjourney_spider.py` | midjourney.com | Scraper |
| CivitaiSpider | `civitai_spider.py` | civitai.com | Yes (API) |
| RunwayMLSpider | `runwayml_spider.py` | runwayml.com | Scraper |
| ReplicateSpider | `replicate_spider.py` | replicate.com | Yes (API) |
| KaggleSpider | `kaggle_spider.py` | kaggle.com | Yes (API) |

### Digital Products Spiders (5)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| GumroadSpider | `gumroad_spider.py` | gumroad.com | Yes (API) |
| EtsySpider | `etsy_spider.py` | etsy.com | Yes (API) |
| LemonSqueezySpider | `lemonsqueezy_spider.py` | lemonsqueezy.com | Yes (API) |
| AppSumoSpider | `appsumo_spider.py` | appsumo.com | Scraper |
| SellfySpider | `sellfy_spider.py` | sellfy.com | Scraper |

### Content & Media Spiders (5)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| MediumSpider | `medium_spider.py` | medium.com | RSS |
| YouTubeSpider | `youtube_spider.py` | youtube.com | Yes (API) |
| SpotifySpider | `spotify_spider.py` | spotify.com | Yes (API) |
| IndieHackersSpider | `indiehackers_spider.py` | indiehackers.com | Scraper |
| VarietySpider | `variety_spider.py` | variety.com | RSS |

### Legal Spiders (5)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| CourtListenerSpider | `courtlistener_spider.py` | courtlistener.com | Yes (API) |
| JustiaSpider | `justia_spider.py` | justia.com | Scraper |
| JustiaPlaywrightSpider | `justia_playwright_spider.py` | justia.com | Playwright |
| FindLawSpider | `findlaw_spider.py` | findlaw.com | Scraper |
| LIISpider | `lii_spider.py` | law.cornell.edu | Scraper |
| ColoradoFamilyLawSpider | `colorado_family_law_spider.py` | Colorado courts | Playwright |

### Community Spiders (3)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| RedditSpider | `reddit_spider.py` | reddit.com (20+ subs) | Yes (API) |
| DiscordSpider | `discord_spider.py` | discord.com | Scraper |
| BlueSkySpider | `bluesky_spider.py` | bsky.app | Yes (API) |

### Education Spiders (3)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| TeachableSpider | `teachable_spider.py` | teachable.com | Scraper |
| UdemySpider | `udemy_spider.py` | udemy.com | Yes (API) |
| SkillshareSpider | `skillshare_spider.py` | skillshare.com | Scraper |

### Crowdfunding Spiders (4)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| KickstarterSpider | `kickstarter_spider.py` | kickstarter.com | Scraper |
| KickstarterPlaywrightSpider | `kickstarter_playwright_spider.py` | kickstarter.com | Playwright |
| IndiegogoSpider | `indiegogo_spider.py` | indiegogo.com | Scraper |
| IndiegogoPlaywrightSpider | `indiegogo_playwright_spider.py` | indiegogo.com | Playwright |

---

## Part 4: Learning Systems

### Learning Bridges (10)

Location: `core/learning_bridges/`

| Bridge | File | Purpose |
|--------|------|---------|
| SpiderDataBridge | `spider_data_bridge.py` | Feed spider data to agent prompts |
| AgentExecutionBridge | `agent_execution_bridge.py` | Track agent execution for learning |
| ApplicationOutcomeBridge | `application_outcome_bridge.py` | Learn from job application outcomes |
| CollaborationBridge | `collaboration_bridge.py` | Learn from agent collaborations |
| PersonalizationBridge | `personalization_bridge.py` | User preference learning |
| RevenueAttributionBridge | `revenue_attribution_bridge.py` | Track revenue generation learning |
| AdvisorFeedbackBridge | `advisor_feedback_bridge.py` | Learn from advisor consultations |
| SportsBettingBridge | `sports_betting_bridge.py` | Sports prediction learning |

### Collective Intelligence Services

Location: `core/services/`

| Service | File | Purpose |
|---------|------|---------|
| CollectiveIntelligence | `collective_intelligence.py` | Central knowledge sharing hub |
| AgentLearningService | `agent_learning_service.py` | Manage agent knowledge |
| AgentCollaborationHub | `agent_collaboration_hub.py` | Multi-agent collaboration |
| AgentCollaboration | `agent_collaboration.py` | Agent teamwork |
| ImplicitLearning | `implicit_learning.py` | Background learning from usage |
| PipelineLearning | `pipeline_learning.py` | Learn from pipeline executions |

---

## Part 5: Sci-Fi Features (15)

Database models: `core/models_unified_system.py`

| Feature | Model | Purpose |
|---------|-------|---------|
| Agent Learning | `AgentKnowledge` | Agents learn from each other |
| Agent Conversations | `AgentConversation` | Real-time AI-to-AI chat |
| Agent Dreams | `AgentDream` | Creative thoughts when idle |
| Hive Mind Mode | `HiveMindSession` | Collective intelligence problem-solving |
| Memory Palace | `AgentMemory` | Persistent agent memory |
| Mood System | `AgentMood` | Emotional states affect behavior |
| Rivalries/Alliances | `AgentRelationship` | Agent relationships and dynamics |
| Evolution System | `AgentEvolution` | XP, levels, progression |
| Time Travel Debug | `AgentDecision` | Replay agent decision-making |
| Personality Profiles | `AgentPersonality` | Distinct agent personalities |
| Memory Clusters | `MemoryCluster` | Grouped related memories |
| Prophecies | `AgentProphecy` | Agent predictions and forecasts |
| Time Capsules | `TimeCapsule` | Messages to future selves |
| Conversation Contract | `ConversationQuality` | Quality scoring for conversations |
| Spider Integration | Real-time via bridge | Agents use spider data in prompts |

---

## Part 6: Autonomous Loops (3)

### AutonomousIntelligenceLoop

Location: `core/services/autonomous_loop.py`

**Runs:** Every 15 minutes via Celery Beat

| Component | Method | Purpose |
|-----------|--------|---------|
| SEC Filing Monitor | `check_sec_filings()` | Monitor SEC EDGAR for new filings |
| Content Opportunity Scanner | `check_content_opportunities()` | Scan for content creation opportunities |
| Job Opportunity Scanner | `check_job_opportunities()` | Find matching job opportunities |
| Stock Security Check | `check_stock_security()` | Run stock audit agent group |
| Blockchain Security Check | `check_blockchain_security()` | Run blockchain audit agent group |

### BlockchainEventListener

Location: `core/services/blockchain_event_listener.py`

**Runs:** Continuous background thread (15-second polling)

| Event Type | Description |
|------------|-------------|
| WHALE_TRANSFER | Large ETH movements (100+ ETH) |
| CONTRACT_DEPLOY | New contract deployments |
| SUSPICIOUS_TX | Unusual transaction patterns |
| EXPLOIT_SIGNATURE | Known exploit pattern detection |

### Celery Beat Schedules

Location: `core/celery.py`

| Task | Schedule | Purpose |
|------|----------|---------|
| `run_autonomous_loop` | Every 15 min | Full autonomous cycle |
| `run_stock_audit_cycle` | Every 30 min (market hours) | Stock monitoring |
| `run_blockchain_audit_cycle` | Every 15 min | Blockchain monitoring |
| `generate_agent_dreams` | User-triggered (DreamsPanel button — no beat schedule per Session 1242 verification) | Agent idle thoughts |
| `run_daily_digest` | Daily at 8am | User opportunity digest |
| `send_daily_digest` | Daily at 9am | Email digests |
| `cleanup_old_records` | Daily at 3am | Database maintenance |

---

## Part 7: Core Services (40+)

Location: `core/services/`

### Intelligence & Learning

| Service | File | Purpose |
|---------|------|---------|
| CollectiveIntelligence | `collective_intelligence.py` | Central knowledge hub |
| AgentLearningService | `agent_learning_service.py` | Agent knowledge management |
| AgentIntelligenceContext | `agent_intelligence_context.py` | Context injection for agents |
| RecommendationEngine | `recommendation_engine.py` | Personalized recommendations |
| KnowledgeSimilarity | `knowledge_similarity.py` | Vector similarity search |

### Content & Creation

| Service | File | Purpose |
|---------|------|---------|
| ContentPipeline | `content_pipeline.py` | 6-tier content factory |
| CreativeOrchestrator | `creative_orchestrator.py` | Complex creative workflows |
| ResearchOrchestrator | `research_orchestrator.py` | Research coordination |
| ResearchToCreativePipeline | `research_to_creative_pipeline.py` | Research → Content flow |

### Communication

| Service | File | Purpose |
|---------|------|---------|
| DiscordBot | `discord_bot.py` | 45 interactive commands |
| DiscordNotifications | `discord_notifications.py` | Alert delivery |
| DiscordVoice | `discord_voice.py` | Voice recording/cloning |

### Analytics & Monitoring

| Service | File | Purpose |
|---------|------|---------|
| AnalyticsService | `analytics_service.py` | Platform analytics |
| ABTesting | `ab_testing.py` | A/B test framework |
| AutonomousLoop | `autonomous_loop.py` | Autonomous monitoring |
| BlockchainEventListener | `blockchain_event_listener.py` | Blockchain monitoring |

### Legal

| Service | File | Purpose |
|---------|------|---------|
| LitigationBrain | `litigation_brain.py` | Legal document analysis |
| ResearchPDFService | `research_pdf_service.py` | PDF extraction |

### Marketplace

| Service | File | Purpose |
|---------|------|---------|
| MarketplaceDiscoveryService | `marketplace_discovery_service.py` | Opportunity discovery |
| IncomeActionService | `income_action_service.py` | Job application actions |
| CertificateService | `certificate_service.py` | User certifications |

---

## Part 8: Agent Routing & Registration

### Agent Router

Location: `core/agent_router.py`

The router uses **deterministic routing** (no LLM involved) based on keyword patterns:

```python
ROUTING_PATTERNS = {
    'image': ['logo', 'image', 'picture', 'photo', 'banner', 'illustration'],
    'video': ['video', 'animation', 'animate', 'clip'],
    'audio': ['voice', 'audio', 'sound', 'speech', 'narration'],
    'research': ['research', 'find', 'search', 'look up', 'trending'],
    'legal': ['motion', 'legal', 'court', 'filing', 'attorney'],
    'code': ['code', 'function', 'implement', 'debug', 'refactor'],
    # ... etc
}
```

### Agent Registry

Location: `core/agents/registry.py`

Maintains runtime registration of all agents with:
- Agent instances
- Capability mappings
- Tool definitions
- Learning hook connections

---

## Part 9: Database Models for Intelligence

Location: `core/models_unified_system.py`

### Core Intelligence Models

| Model | Purpose |
|-------|---------|
| `Agent` | Agent definitions and stats |
| `AgentKnowledge` | Learned knowledge entries |
| `AgentConversation` | AI-to-AI conversations |
| `AgentDream` | Agent idle thoughts |
| `AgentMemory` | Persistent memories |
| `AgentMood` | Emotional states |
| `AgentDecision` | Time travel tracking |
| `AgentEvolution` | XP and leveling |
| `AgentRelationship` | Rivalries/alliances |
| `HiveMindSession` | Collective sessions |

### Data Models

| Model | Purpose |
|-------|---------|
| `SpiderData` | Raw spider data storage |
| `Opportunity` | Income opportunities |
| `OpportunityApplication` | Job applications |
| `ABTest` | A/B testing data |
| `UserGoal` | User goals and targets |

---

## Part 10: Extension Points

### Adding a New Agent

1. Create file in `core/agents/your_agent.py`
2. Inherit from `BaseAgent`
3. Define tools with `get_tools()`
4. Implement `execute()` method
5. Register in `core/agents/__init__.py`
6. Add routing pattern in `core/agent_router.py`

### Adding a New Spider

1. Create file in `ai_core/spiders/specialized/your_spider.py`
2. Inherit from `BaseSpider`
3. Implement `crawl()` method
4. Register in `ai_core/spiders/spider_registry.py`

### Adding a New Advisor

1. Add entry to `_initialize_advisor_network()` in `advisors/registry.py`
2. Define domain, specializations, decision frameworks
3. Advisor automatically available via Discord `/consult`

### Adding a New Learning Bridge

1. Create file in `core/learning_bridges/your_bridge.py`
2. Inherit from base bridge class
3. Implement `process()` and `learn()` methods
4. Register signal handlers

---

## Appendix: File Structure

```
unified-donkey-betz/
├── core/
│   ├── agents/                  # 48 agents
│   │   ├── blockchain/          # 5 blockchain audit agents
│   │   ├── stocks/              # 5 stock audit agents
│   │   ├── business/            # 5 business research agents
│   │   ├── executive/           # 4 executive agents
│   │   ├── strategy/            # 4 strategy agents
│   │   ├── analysis/            # 3 analysis agents
│   │   ├── security/            # 2 security agents
│   │   ├── training/            # 2 training agents
│   │   ├── legal/               # 1 legal agent
│   │   └── *.py                 # Core agents
│   ├── services/                # 40+ services
│   ├── learning_bridges/        # 10 learning bridges
│   └── models_unified_system.py # Sci-Fi models
├── advisors/
│   └── registry.py              # 25 advisors
├── ai_core/
│   └── spiders/
│       └── specialized/         # 66 spiders
└── docs/
    └── SYSTEM_INTELLIGENCE_ATLAS.md  # This file
```

---

**This atlas is a living document. Update as new components are added.**


---


## Session 461 — Stock Agent Group Audit (Operating Pattern + Gaps)

_Source: `SESSION_461_STOCK_AUDIT_AGENTS.md`_


---

# Session 461: Stock Audit Agent Group

**Date:** December 16, 2025
**Status:** COMPLETE
**Focus:** Autonomous Stock Market Security & Intelligence Monitoring

---

## Overview

Building an autonomous stock audit system that leverages existing infrastructure (agents, spiders, autonomous loop, Discord) to provide real-time market monitoring, insider trading detection, and investment intelligence.

---

## The Vision

```
┌─────────────────────────────────────────────────────────────────┐
│                   STOCK AUDIT AGENT GROUP                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │ MONITORING TIER  │    │  ANALYSIS TIER   │                   │
│  ├──────────────────┤    ├──────────────────┤                   │
│  │ MarketMovement   │───▶│ StockAnalyst     │                   │
│  │ InstitutionalWat │    │ AnomalyDetector  │                   │
│  │ SECFilingWatch   │    │                  │                   │
│  └────────┬─────────┘    └────────┬─────────┘                   │
│           │                       │                              │
│           ▼                       ▼                              │
│  ┌────────────────────────────────────────────┐                 │
│  │            StockAuditCoordinator           │                 │
│  │   - Routes findings to appropriate agents  │                 │
│  │   - Correlates cross-market activity       │                 │
│  │   - Manages alert severity                 │                 │
│  └────────────────────┬───────────────────────┘                 │
│                       │                                          │
│                       ▼                                          │
│  ┌────────────────────────────────────────────┐                 │
│  │         SPIDER NETWORK                      │                 │
│  │   SECEdgarSpider (filings, insider trades) │                 │
│  │   YahooFinanceSpider (prices, volume)      │                 │
│  │   FinvizSpider (screener, insider data)    │                 │
│  └────────────────────┬───────────────────────┘                 │
│                       │                                          │
│                       ▼                                          │
│  ┌────────────────────────────────────────────┐                 │
│  │           Discord #stock-alerts             │                 │
│  └────────────────────────────────────────────┘                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## New Components

### Agents (4 New)

| Agent | Purpose | Base Class | Key Tools |
|-------|---------|------------|-----------|
| **StockAnalystAgent** | Analyze SEC filings, fundamentals, valuations | BaseAgent | `analyze_filing`, `check_valuation`, `compare_peers`, `assess_risk` |
| **MarketMovementMonitorAgent** | Watch for unusual price/volume movements | BaseAgent | `detect_volume_spike`, `track_momentum`, `alert_breakout` |
| **InstitutionalWatcherAgent** | Track insider trading & institutional activity | BaseAgent | `monitor_insiders`, `track_13f_filings`, `alert_large_position` |
| **MarketAnomalyDetectorAgent** | Detect pump & dump, unusual options activity | BaseAgent | `detect_pump_dump`, `analyze_options_flow`, `flag_manipulation` |

### Coordinator (1 New)

| Component | Purpose |
|-----------|---------|
| **StockAuditCoordinator** | Orchestrates all stock audit agents, correlates findings, manages severity |

### Spiders (3 Enhanced/New)

| Spider | Source | Data Type |
|--------|--------|-----------|
| **SECEdgarSpider** | SEC EDGAR (existing) | Real-time filings, Form 4 insider trades |
| **YahooFinanceSpider** | Yahoo Finance API (existing) | Price, volume, fundamentals |
| **FinvizSpider** | Finviz.com (new) | Screener data, insider activity, analyst ratings |

---

## Existing Infrastructure Being Leveraged

| Component | Location | How We Use It |
|-----------|----------|---------------|
| AutonomousIntelligenceLoop | `core/services/autonomous_loop.py` | Add `check_stock_security()` method |
| SEC Spider | `ai_core/spiders/specialized/sec_spider.py` | Enhance with insider trading data |
| Yahoo Finance Spider | `ai_core/spiders/specialized/yahoo_finance_spider.py` | Enhance with real-time data |
| Discord Notifications | `core/services/discord_notifications.py` | Add `send_stock_alert()` method |
| Celery Beat | `core/celery.py` | Add stock monitoring schedule |
| Spider Registry | `ai_core/spiders/spider_registry.py` | Register new spiders |

---

## Implementation Plan

### Phase 1: Stock Analyst Agent
1. Create `StockAnalystAgent` for SEC filing analysis
2. Add fundamental analysis checks:
   - P/E ratio vs industry average
   - Debt-to-equity concerns
   - Revenue/earnings trend analysis
   - Cash flow health
   - Insider ownership changes
3. Integrate with existing SEC spider data

### Phase 2: Market Monitoring
1. Enhance `YahooFinanceSpider` for real-time data
2. Create `MarketMovementMonitorAgent` with pattern detection
3. Create `InstitutionalWatcherAgent` for insider activity
4. Add suspicious pattern library (pump & dump, front-running, etc.)

### Phase 3: Anomaly Detection
1. Create `FinvizSpider` for screener data
2. Create `MarketAnomalyDetectorAgent` with pattern matching
3. Build manipulation signature database
4. Cross-reference with volume/price patterns

### Phase 4: Autonomous Integration
1. Create `StockAuditCoordinator`
2. Wire into `autonomous_loop.py`
3. Add `check_stock_security()` to 15-min cycle
4. Add Discord `#stock-alerts` channel
5. Implement alert severity levels (CRITICAL, HIGH, MEDIUM, LOW)

---

## Alert Types

| Severity | Trigger | Example |
|----------|---------|---------|
| **CRITICAL** | Massive insider selling | CEO dumps 50% of holdings before earnings |
| **HIGH** | Unusual options activity | 10x normal put volume on single stock |
| **MEDIUM** | Significant price movement | Stock up 20% on no news |
| **LOW** | Informational | New 13F filing from major fund |

---

## Discord Integration

New channel: `#stock-alerts`

Notification format:
```
📈 STOCK ALERT
━━━━━━━━━━━━━━━━━━━━━━━━
Severity: HIGH
Type: Insider Trading Activity
━━━━━━━━━━━━━━━━━━━━━━━━

Significant insider sale detected:
• Company: ACME Corp (ACME)
• Insider: John Smith (CEO)
• Action: SELL
• Shares: 500,000
• Value: $12.5M
• Filed: 2 hours ago

Analysis: This represents 40% of CEO's holdings.
Recent filings show mixed guidance...

🔗 View SEC Filing
```

---

## Files Created/Modified

### New Files
- `core/agents/stocks/stock_analyst_agent.py`
- `core/agents/stocks/market_movement_monitor_agent.py`
- `core/agents/stocks/institutional_watcher_agent.py`
- `core/agents/stocks/market_anomaly_detector_agent.py`
- `core/agents/stocks/stock_audit_coordinator.py`
- `core/agents/stocks/__init__.py`
- `ai_core/spiders/specialized/finviz_spider.py`

### Modified Files
- `core/services/autonomous_loop.py` - Add stock monitoring
- `core/services/discord_notifications.py` - Add stock alerts
- `core/celery.py` - Add stock monitoring schedule
- `ai_core/spiders/spider_registry.py` - Register new spiders
- `core/agents/__init__.py` - Export new agents

---

## Success Criteria

- [x] StockAnalystAgent can analyze SEC filings
- [x] MarketMovementMonitorAgent detects unusual volume/price
- [x] InstitutionalWatcherAgent tracks insider trading
- [x] MarketAnomalyDetectorAgent matches manipulation patterns
- [x] All agents connected to Discord alerts
- [x] Autonomous loop includes stock monitoring
- [x] System runs 24/7 without intervention

---

## Future Enhancements

- Real-time WebSocket price feeds
- Machine learning for pattern detection
- Options flow analysis integration
- Earnings surprise prediction
- Sector rotation detection
- Portfolio risk monitoring
- Warren Buffett advisor integration for value analysis

---

## References

- Session 460: Autonomous Intelligence Loop (foundation)
- Session 461: Blockchain Audit Agents (architecture pattern)
- SEC EDGAR API: https://www.sec.gov/developer
- Yahoo Finance API: Via yfinance library
- Finviz: https://finviz.com/


---


## Session 461 — Blockchain Agent Group Audit (Operating Pattern + Gaps)

_Source: `SESSION_461_BLOCKCHAIN_AUDIT_AGENTS.md`_


---

# Session 461: Blockchain Audit Agent Group

**Date:** December 16, 2025
**Status:** COMPLETE
**Focus:** Autonomous Blockchain Security Monitoring

---

## Overview

Building an autonomous blockchain audit system that leverages existing infrastructure (agents, spiders, autonomous loop, Discord) to provide real-time security monitoring for blockchain ecosystems.

---

## The Vision

```
┌─────────────────────────────────────────────────────────────────┐
│                BLOCKCHAIN AUDIT AGENT GROUP                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │ MONITORING TIER  │    │  ANALYSIS TIER   │                   │
│  ├──────────────────┤    ├──────────────────┤                   │
│  │ TransactionMon   │───▶│ SmartContractAud │                   │
│  │ WhaleWatcher     │    │ ExploitDetector  │                   │
│  │ ContractDeployer │    │                  │                   │
│  └────────┬─────────┘    └────────┬─────────┘                   │
│           │                       │                              │
│           ▼                       ▼                              │
│  ┌────────────────────────────────────────────┐                 │
│  │         BlockchainAuditCoordinator         │                 │
│  │   - Routes findings to appropriate agents  │                 │
│  │   - Correlates cross-chain activity        │                 │
│  │   - Manages alert severity                 │                 │
│  └────────────────────┬───────────────────────┘                 │
│                       │                                          │
│                       ▼                                          │
│  ┌────────────────────────────────────────────┐                 │
│  │         SPIDER NETWORK                      │                 │
│  │   EtherscanAPISpider (transactions)        │                 │
│  │   DefiLlamaSpider (TVL, protocols)         │                 │
│  │   RektNewsSpider (exploits, post-mortems)  │                 │
│  └────────────────────┬───────────────────────┘                 │
│                       │                                          │
│                       ▼                                          │
│  ┌────────────────────────────────────────────┐                 │
│  │         Discord #blockchain-alerts          │                 │
│  └────────────────────────────────────────────┘                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## New Components

### Agents (4 New)

| Agent | Purpose | Base Class | Key Tools |
|-------|---------|------------|-----------|
| **SmartContractAuditorAgent** | Audit Solidity code for vulnerabilities | CodeReviewAgent | `audit_contract`, `check_reentrancy`, `check_overflow`, `check_access_control` |
| **TransactionMonitorAgent** | Watch for suspicious tx patterns | BaseAgent | `analyze_transaction`, `detect_anomaly`, `track_address` |
| **WhaleWatcherAgent** | Track large token movements | BaseAgent | `monitor_whales`, `alert_large_transfer`, `track_wallet` |
| **ExploitDetectorAgent** | Pattern match known exploits | BaseAgent | `match_exploit_pattern`, `analyze_attack_vector`, `generate_alert` |

### Coordinator (1 New)

| Component | Purpose |
|-----------|---------|
| **BlockchainAuditCoordinator** | Orchestrates all audit agents, correlates findings, manages severity |

### Spiders (3 New)

| Spider | Source | Data Type |
|--------|--------|-----------|
| **EtherscanAPISpider** | Etherscan API | Real-time transactions, internal txs, token transfers |
| **DefiLlamaSpider** | DeFi Llama API | TVL changes, protocol health metrics |
| **RektNewsSpider** | Rekt.news RSS | Known exploits, post-mortems, attack patterns |

---

## Existing Infrastructure Being Leveraged

| Component | Location | How We Use It |
|-----------|----------|---------------|
| AutonomousIntelligenceLoop | `core/services/autonomous_loop.py` | Add `check_blockchain_security()` method |
| CodeReviewAgent | `core/agents/code_review_agent.py` | Extend for Solidity-specific audits |
| EtherscanSpider | `ai_core/spiders/specialized/etherscan_spider.py` | Enhance with API transaction data |
| Discord Notifications | `core/services/discord_notifications.py` | Add `send_blockchain_alert()` method |
| Celery Beat | `core/celery.py` | Add blockchain monitoring schedule |
| Spider Registry | `ai_core/spiders/spider_registry.py` | Register new blockchain spiders |

---

## Implementation Plan

### Phase 1: Smart Contract Auditor
1. Create `SmartContractAuditorAgent` extending CodeReviewAgent
2. Add Solidity-specific vulnerability checks:
   - Reentrancy attacks
   - Integer overflow/underflow
   - Access control issues
   - Unchecked external calls
   - Front-running vulnerabilities
3. Add GitHub integration to fetch contract source code

### Phase 2: Transaction Monitoring
1. Create `EtherscanAPISpider` for real transaction data
2. Create `TransactionMonitorAgent` with pattern detection
3. Create `WhaleWatcherAgent` for large transfer alerts
4. Add suspicious pattern library (flash loan attacks, sandwich attacks, etc.)

### Phase 3: Exploit Detection
1. Create `RektNewsSpider` for known exploits
2. Create `ExploitDetectorAgent` with pattern matching
3. Build exploit signature database
4. Cross-reference with transaction patterns

### Phase 4: Autonomous Integration
1. Create `BlockchainAuditCoordinator`
2. Wire into `autonomous_loop.py`
3. Add `check_blockchain_security()` to 15-min cycle
4. Add Discord `#blockchain-alerts` channel
5. Implement alert severity levels (CRITICAL, HIGH, MEDIUM, LOW)

---

## Alert Types

| Severity | Trigger | Example |
|----------|---------|---------|
| **CRITICAL** | Active exploit detected | Flash loan attack in progress |
| **HIGH** | Suspicious transaction pattern | Large unexpected token movement |
| **MEDIUM** | Vulnerability in popular contract | Reentrancy risk in DeFi protocol |
| **LOW** | Informational | New large contract deployment |

---

## Discord Integration

New channel: `#blockchain-alerts`

Notification format:
```
🚨 BLOCKCHAIN ALERT
━━━━━━━━━━━━━━━━━━━━━━━━
Severity: HIGH
Type: Suspicious Transaction
━━━━━━━━━━━━━━━━━━━━━━━━

Large ETH transfer detected:
• From: 0x1234...5678
• To: 0xabcd...ef01
• Amount: 10,000 ETH
• Time: 2 minutes ago

Analysis: Pattern matches known mixer address...

🔗 View on Etherscan
```

---

## Files Created/Modified

### New Files
- `core/agents/blockchain/smart_contract_auditor_agent.py`
- `core/agents/blockchain/transaction_monitor_agent.py`
- `core/agents/blockchain/whale_watcher_agent.py`
- `core/agents/blockchain/exploit_detector_agent.py`
- `core/agents/blockchain/blockchain_audit_coordinator.py`
- `core/agents/blockchain/__init__.py`
- `ai_core/spiders/specialized/etherscan_api_spider.py`
- `ai_core/spiders/specialized/defillama_spider.py`
- `ai_core/spiders/specialized/rekt_news_spider.py`

### Modified Files
- `core/services/autonomous_loop.py` - Add blockchain monitoring
- `core/services/discord_notifications.py` - Add blockchain alerts
- `core/celery.py` - Add blockchain monitoring schedule
- `ai_core/spiders/spider_registry.py` - Register new spiders
- `core/agents/__init__.py` - Export new agents

---

## Success Criteria

- [x] SmartContractAuditorAgent can audit Solidity code
- [x] TransactionMonitorAgent detects suspicious patterns
- [x] WhaleWatcherAgent tracks large movements
- [x] ExploitDetectorAgent matches known attack patterns
- [x] All agents connected to Discord alerts
- [x] Autonomous loop includes blockchain monitoring
- [x] System runs 24/7 without intervention

## Additional Features Implemented

- **BlockchainEventListener** - Real-time event monitoring service with 15-second polling
- **Contract Audit by Address** - `/audit-contract <address>` Discord command
- **Etherscan API V2 Migration** - Updated from deprecated V1 API (Dec 2025)
- **Discord Channels:**
  - `#blockchain-agents` (ID: 1450589795058192465)
  - `/blockchain-status` command for monitoring health

---

## Future Enhancements

- Multi-chain support (BSC, Polygon, Arbitrum)
- Machine learning for anomaly detection
- Integration with on-chain analytics providers
- Real-time block monitoring via WebSocket
- Smart contract decompiler integration
- MEV detection and analysis

---

## References

- Session 460: Autonomous Intelligence Loop (foundation)
- Session 436: Development Agents (CodeReviewAgent base)
- Etherscan API: https://docs.etherscan.io/
- DeFi Llama API: https://defillama.com/docs/api
- Rekt.news: https://rekt.news/


---


## Integration Notes (Actionable)

- **Primary goal:** make the system run “countless situations” like Stock/Blockchain groups: persistent agent swarms that can (1) ingest signals, (2) argue/critique, (3) produce publishable outputs, (4) log everything, (5) iterate automatically on schedule.
- **Minimum viable loop:** (a) fetch signals (news/market/chain), (b) run multi-agent debate & synthesis, (c) output report + recommended actions, (d) store artifacts + citations + confidence, (e) schedule next run.
- **Trading algo extension (optional but powerful):** if the coding agents are in place, add a pipeline that can: strategy spec → code generation → backtest → metrics → critique → revise → re-run, with guardrails for paper-trading only unless explicitly enabled.

