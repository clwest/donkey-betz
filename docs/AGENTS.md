# Agent Reference

**Last Updated:** Session 496 (December 19, 2025) - Added AI Podcast Studio Agents

---

## Overview

The platform uses a **Clean Agent Architecture** where each agent is specialized with isolated tools. Agents cannot call each other's tools directly - they must delegate through the WorkflowAgent.

**Session 400 Addition:** All agents now automatically inject learned knowledge into their prompts via `_build_prompt()`. The knowledge pipeline is:
```
Spider Data → Embeddings → Learning Bridge → AgentKnowledgeSource → Agent Prompts
```

**Session 303 Addition:** Business research agents now have unified intelligence search with auto-refresh and prior research context.

---

## Agent Knowledge Pipeline (Session 400)

All agents inherit from `BaseAgent` which provides:

### Knowledge Retrieval Methods

```python
# Get learned knowledge relevant to current task
knowledge = agent._get_relevant_knowledge_for_task("AI trends", limit=5)
# Returns: [{source_agent, title, summary, knowledge_type, confidence, spider_sources}]

# Get fresh spider intelligence by category
intel = agent._get_fresh_spider_intelligence(categories=['tech', 'news'], hours=24, limit=5)
# Returns: [{source, category, titles, item_count, relevance, timestamp}]
```

### Automatic Knowledge Injection

The `_build_prompt()` method automatically:
1. Calls `_get_relevant_knowledge_for_task(task)`
2. Injects relevant knowledge before the task
3. Includes source attribution

**Example prompt section:**
```
## Relevant Knowledge from Past Learning
You have learned the following that may be relevant:

1. [ResearchAgent] Research: AI trends in 2025
   Analysis shows growth in LLM applications...
   (from: techcrunch, hackernews)
```

### Learning Hooks

Agents record their executions for future learning:
```python
# After successful execution
self._record_learning_outcome(result, task, context)
self._create_execution_memory(result, task, memory_type="success")
self._share_knowledge(knowledge_type='trend', title='...', knowledge_value={...})
```

---

## Clean Architecture Agents (27)

### PersonalAssistantAgent

**Purpose:** Traffic cop - routes requests to specialized agents

**Location:** `core/agents/personal_assistant_agent.py`

**Tools:**
- `delegate_to_agent` - Send task to another agent

**Behavior:**
- Questions → Answer directly (no delegation)
- Creation requests → Delegate to ImageAgent/VideoAgent/etc.
- Research requests → Delegate to ResearchAgent
- Complex multi-step → Delegate to WorkflowAgent

**Intent Detection Keywords:**
```python
'ImageAgent': ['logo', 'banner', 'image', 'picture', 'illustration', 'icon', 'graphic']
'VideoAgent': ['video', 'animation', 'clip', 'movie', 'footage']
'AudioAgent': ['voice', 'speech', 'audio', 'sound', 'narration', 'voiceover']
'ResearchAgent': ['search', 'find', 'research', 'trending', 'what is', 'hot in']
'WorkflowAgent': ['research and create', 'find and make', 'package']
```

---

### ImageAgent

**Purpose:** Image generation ONLY

**Location:** `core/agents/image_agent.py`

**Tools:**
- `generate_image` - Create new images

**Parameters:**
```python
{
    "prompt": "A cyberpunk cityscape",
    "count": 3,
    "style": "cyberpunk",
    "quality": "sdxl"  # core, sdxl, sd3, ultra
}
```

**Cannot Access:** Video, audio, 3D, research tools

---

### VideoAgent

**Purpose:** Video generation ONLY

**Location:** `core/agents/video_agent.py`

**Tools:**
- `generate_video` - Text-to-video
- `animate_image` - Image-to-video
- `extend_video` - Extend existing video
- `chain_videos` - Concatenate clips

**Parameters:**
```python
{
    "prompt": "A sunset over the ocean",
    "duration": 5,
    "source_image_id": 123  # Optional for animate_image
}
```

**Cannot Access:** Image generation, audio, 3D, research tools

---

### AudioAgent

**Purpose:** Audio generation ONLY

**Location:** `core/agents/audio_agent.py`

**Tools:**
- `generate_voice` - Text-to-speech
- `generate_sfx` - Sound effects
- `add_voiceover` - Add narration to video

**Parameters:**
```python
{
    "text": "Welcome to our platform",
    "voice": "alloy",
    "video_id": 456  # For add_voiceover
}
```

**Cannot Access:** Image, video generation, 3D, research tools

---

### ThreeDAgent

**Purpose:** 3D generation ONLY

**Location:** `core/agents/three_d_agent.py`

**Tools:**
- `convert_to_3d` - Image to 3D model
- `generate_3d_scene` - Create 3D scenes

**Parameters:**
```python
{
    "image_id": 123,
    "output_format": "glb"  # glb, obj, gltf
}
```

**Cannot Access:** Image, video, audio, research tools

---

### ImageEditingAgent

**Purpose:** Image editing ONLY

**Location:** `core/agents/image_editing_agent.py`

**Tools:**
- `upscale` - 4x resolution increase
- `remove_background` - Transparent PNG
- `create_variations` - Similar images
- `recolor` - Change object colors
- `search_replace` - Replace objects

**Parameters:**
```python
{
    "image_id": 123,
    "operation": "upscale"
}
```

**Cannot Access:** Creation tools (image/video/audio generation)

---

### VideoEditingAgent

**Purpose:** Video editing ONLY

**Location:** `core/agents/video_editing_agent.py`

**Tools:**
- `trim` - Cut video
- `add_text` - Overlay text
- `add_effects` - Visual effects
- `extract_frame` - Get still image
- `concatenate` - Join videos
- `speed_change` - Adjust playback speed

**Parameters:**
```python
{
    "video_id": 456,
    "operation": "trim",
    "start_time": 0,
    "end_time": 5
}
```

**Cannot Access:** Creation tools

---

### ResearchAgent

**Purpose:** Web search + spider network ONLY

**Location:** `core/agents/research_agent.py`

**Tools:**
- `web_search` - Search the web (Serper API)
- `spider_query` - Query spider network data
- `analyze_trends` - Get trending topics

**Parameters:**
```python
{
    "query": "AI trends 2025",
    "category": "tech",  # tech, financial, jobs, creative
    "topic_filter": "ai",  # ai, web, security, cloud, design
    "hours": 72,
    "limit": 20
}
```

**Data Sources:**
- 70 spiders across 24 real sources
- SpiderIntelligenceService for trend analysis

**Cannot Access:** Any creation or editing tools

---

### WorkflowAgent

**Purpose:** Multi-step orchestration

**Location:** `core/agents/workflow_agent.py`

**Tools:**
- `delegate_to_agent` - Call other agents in sequence

**Workflow Examples:**
```python
# Research and create workflow
Step 1: delegate_to_agent("ResearchAgent", "Find AI trends")
Step 2: Analyze research results
Step 3: delegate_to_agent("ImageAgent", "Create logos based on trends")

# Brand package workflow
Step 1: Research brand aesthetics
Step 2: Generate logo options
Step 3: Create color palette
Step 4: Generate social media banners
```

**Special Powers:** Can orchestrate any other agent

---

### AISeriesWorkflowAgent (Session 445)

**Purpose:** Master orchestrator for multi-episode content series

**Location:** `core/agents/ai_series_workflow_agent.py`

**Tools:**
- `delegate_to_agent` - Delegate to ResearchAgent, ImageAgent, VideoAgent, AudioAgent
- `plan_series` - Generate episode structure and story arcs
- `lock_style` - Lock visual style for consistency across episodes
- `define_character` - Define character with visuals and voice
- `generate_episode` - Generate single episode through full pipeline

**Pipeline Stages:**
1. **Research** - Query spiders for trending topics and audience analysis
2. **Planning** - Create series outline, story arc, character profiles
3. **Character** - Generate consistent character visuals (ImageAgent)
4. **Script** - Generate episode scripts/narration (GPT)
5. **Voice** - Generate voiceovers (AudioAgent)
6. **Video** - Generate video content (VideoAgent)

**Series Types:**
- Educational (tutorials, explainers, courses)
- Entertainment (stories, animations, shows)
- Marketing (product series, brand content)

**Key Features:**
- Sequential episode generation for story continuity
- Character consistency enforcement across episodes
- Style locking for visual consistency
- Story arc tracking (setup → conflict → resolution)
- Episode count: 1-5 per series
- Progress tracking per episode
- Learning hooks for collective intelligence

**Database Models:**
- `AISeries` - Series metadata, status, progress
- `SeriesEpisode` - Individual episode data and results
- `SeriesCharacter` - Character definitions with visuals/voice

**Discord Commands:**
- `/series-create <type> <episodes> <prompt>` - Create new series
- `/series-status [id]` - Check generation progress
- `/series-list` - List user's series

**Celery Task:**
- `generate_ai_series(series_id)` - Background generation with retry logic

**Cannot Access:** Direct creation tools (delegates to specialist agents)

---

### AutonomousContentStudioCoordinator (Session 466)

**Purpose:** Orchestrates autonomous content generation with agent debates

**Location:** `core/agents/autonomous_content_studio_coordinator.py`

**Tools:**
- `check_channels_due_for_content` - Find channels ready for new content
- `get_channel_performance_summary` - Get channel performance stats
- `initiate_content_debate` - Coordinate TopicMiner vs Contrarian vs Analyst debate
- `trigger_content_creation` - Trigger AISeriesWorkflowAgent for content
- `update_channel_schedule` - Schedule next content cycle (self-renewal)
- `analyze_channel_performance` - Analyze and adjust confidence multipliers

**Key Features:**
- Implements Tier 1 Autonomous Situation (runs forever without intervention)
- Coordinates 3-agent debate system for topic selection
- Self-renewal via schedule_next_content()
- Learning loop adjusts confidence multipliers (0.5x-1.5x)

**Cannot Access:** Direct creation tools (delegates to specialist agents)

---

### TopicMinerAgent (Session 466)

**Purpose:** Argues FOR trending topics in content debates

**Location:** `core/agents/content/topic_miner_agent.py`

**Tools:**
- `query_spider_trends` - Query spider network for trending topics
- `score_topic_potential` - Score topics based on mentions, recency, relevance
- `detect_trending_gaps` - Find trending topics not yet covered by channel

**Behavior:**
- Analyzes spider data for trending keywords
- Scores potential topics on 0-1 scale
- Argues that popular topics will perform well
- Emphasizes momentum and current interest

**Example Output:**
```
"This topic is trending! 47 mentions in last 3 days, 85% potential score.
High relevance to channel domain. Strong momentum detected."
```

**Cannot Access:** Direct creation tools (focused on trend analysis only)

---

### ContrarianAgent (Session 466)

**Purpose:** Argues AGAINST oversaturated topics in content debates

**Location:** `core/agents/content/contrarian_agent.py`

**Tools:**
- `check_topic_saturation` - Detect oversaturated topics
- `suggest_unique_angles` - Generate contrarian angles
- `find_rising_topics` - Find rising (not yet saturated) topics

**Behavior:**
- Challenges obvious/popular choices
- Detects saturation levels (LOW/MODERATE/HIGH/CRITICAL)
- Suggests unique angles (opposite perspective, beginner/advanced splits, etc.)
- Warns against "everyone's doing this" topics

**Saturation Levels:**
- CRITICAL: >50 mentions (AVOID - Too saturated)
- HIGH: >20 mentions (Unique angle required)
- MODERATE: >10 mentions (Acceptable with differentiation)
- LOW: <10 mentions (Good opportunity)

**Example Output:**
```
"WARNING - Saturation level: CRITICAL (67 mentions in 14 days).
Everyone's covering this - hard to stand out. Suggest contrarian angle:
'Why [topic] might be overrated' to differentiate."
```

**Cannot Access:** Direct creation tools (focused on debate/analysis only)

---

### PerformanceAnalystAgent (Session 466)

**Purpose:** Argues from EVIDENCE using historical performance data

**Location:** `core/agents/content/performance_analyst_agent.py`

**Tools:**
- `get_topic_performance_history` - Get historical performance for similar topics
- `predict_topic_performance` - Predict performance (exact match/similar/channel avg)
- `get_success_patterns` - Identify patterns in top performing content
- `calculate_confidence_score` - Calculate confidence based on data availability

**Behavior:**
- Uses TopicPerformance database to find what worked before
- Predicts views/engagement/retention based on historical data
- Provides confidence scores (0-1) based on amount of supporting data
- Argues from evidence, not opinions

**Prediction Bases:**
- EXACT_MATCH: High confidence (0.9) - topic done before
- SIMILAR_TOPICS: Moderate confidence (0.6) - related topics exist
- CHANNEL_AVERAGE: Low confidence (0.3) - no historical data

**Example Output:**
```
"Historical data shows similar topics get 15,000 views avg (±3,000).
Based on 7 previous episodes with 68% avg retention.
Confidence: 0.7 (strong historical precedent)."
```

**Cannot Access:** Direct creation tools (focused on data analysis only)

---

### CompetitorAnalysisAgent (Session 293, Enhanced 303)

**Purpose:** Competitive intelligence and market analysis

**Location:** `core/agents/business/competitor_analysis_agent.py`

**Tools:**
- `refresh_spider_data` - Trigger fresh spider crawls before analysis (Session 303)
- `get_prior_research` - Retrieve relevant past research (Session 303)
- `web_search` - Search for competitor info, features, pricing
- `spider_query` - Query spider network for competitor mentions
- `analyze_competitor` - Deep analysis of a specific competitor
- `generate_swot` - Generate SWOT analysis

**Session 303 Enhancements:**
- Auto-triggers spider refresh at start of execution
- Injects prior research context into GPT prompts
- Uses `UnifiedIntelligenceSearch` for combined data access

**Parameters:**
```python
{
    "query": "Analyze AI content generation competitors",
    "project_id": "uuid"  # Optional - auto-enhances vague requests
}
```

**Cannot Access:** Image, video, audio, editing tools

---

### CustomerResearchAgent (Session 293, Enhanced 303)

**Purpose:** Customer research and persona development

**Location:** `core/agents/business/customer_research_agent.py`

**Tools:**
- `refresh_spider_data` - Trigger fresh spider crawls (Session 303)
- `get_prior_research` - Retrieve past research (Session 303)
- `spider_query` - Query Reddit, HackerNews, forums
- `web_search` - Search for reviews, testimonials
- `analyze_pain_points` - Extract pain points from discussions
- `build_persona` - Build customer personas
- `extract_quotes` - Extract customer quotes for messaging

**Session 303 Enhancements:**
- Auto-triggers spider refresh for fresh community data
- Cumulative intelligence from prior competitor analysis
- Uses `UnifiedIntelligenceSearch` for combined data access

**Parameters:**
```python
{
    "query": "Research customer pain points for AI writing tools",
    "project_id": "uuid"  # Optional
}
```

**Cannot Access:** Image, video, audio, editing tools

---

### CodeGeneratorAgent (Session 436)

**Purpose:** Generate code from natural language specifications

**Location:** `core/agents/code_generator_agent.py`

**Tools:**
- `generate_code` - Generate code from specification
- `explain_code` - Explain existing code
- `refactor_code` - Improve code structure

**Parameters:**
```python
{
    "specification": "Create a REST API endpoint for user authentication",
    "language": "python",  # python, javascript, typescript, go, rust, java
    "framework": "django",  # django, fastapi, express, react, vue
    "style": "modern"  # modern, legacy, minimal
}
```

**Supported Languages:** Python, JavaScript, TypeScript, Go, Rust, Java, C#, PHP, Ruby

**Cannot Access:** Image, video, audio, editing, research tools

---

### FullStackDeveloperAgent (Session 436)

**Purpose:** Build complete features spanning frontend, backend, and database

**Location:** `core/agents/fullstack_developer_agent.py`

**Tools:**
- `design_feature` - Create feature architecture
- `implement_backend` - Generate backend code (API, models, services)
- `implement_frontend` - Generate frontend code (components, pages)
- `generate_migrations` - Create database migrations
- `create_tests` - Generate test suites

**Parameters:**
```python
{
    "feature": "User profile management with avatar upload",
    "stack": {
        "frontend": "react",
        "backend": "django",
        "database": "postgresql"
    }
}
```

**Special Powers:** Can coordinate frontend + backend + database in single execution

**Cannot Access:** Image generation, video, audio tools

---

### CodeReviewAgent (Session 436)

**Purpose:** Review code for quality, security, performance, and best practices

**Location:** `core/agents/code_review_agent.py`

**Tools:**
- `review_code` - Comprehensive code review
- `check_security` - Security vulnerability scan
- `check_performance` - Performance analysis
- `check_style` - Style and convention check
- `suggest_improvements` - Improvement recommendations

**Parameters:**
```python
{
    "code": "...",  # Code to review
    "language": "python",
    "focus": ["security", "performance", "style"],  # Review focus areas
    "severity": "all"  # all, critical, high, medium
}
```

**Review Categories:**
- Security (OWASP Top 10, injection, XSS, CSRF)
- Performance (N+1 queries, memory leaks, complexity)
- Style (PEP8, ESLint, naming conventions)
- Best Practices (SOLID, DRY, error handling)

**Cannot Access:** Code generation, image, video, audio tools

---

### DevOpsAgent (Session 436)

**Purpose:** CI/CD pipelines, Docker, Kubernetes, infrastructure automation

**Location:** `core/agents/devops_agent.py`

**Tools:**
- `create_dockerfile` - Generate Dockerfiles
- `create_compose` - Generate docker-compose.yml
- `create_pipeline` - Generate CI/CD pipelines (GitHub Actions, GitLab CI)
- `create_k8s_manifests` - Generate Kubernetes manifests
- `diagnose_deployment` - Troubleshoot deployment issues

**Parameters:**
```python
{
    "project_type": "django",
    "deployment_target": "kubernetes",  # docker, kubernetes, aws, gcp
    "ci_platform": "github_actions",  # github_actions, gitlab_ci, jenkins
    "environment": "production"  # development, staging, production
}
```

**Supported Platforms:**
- Docker, Docker Compose
- Kubernetes (deployment, service, ingress, configmap, secrets)
- GitHub Actions, GitLab CI, Jenkins
- AWS (ECS, EKS, Lambda), GCP (Cloud Run, GKE)

**Cannot Access:** Code generation, image, video, audio tools

---

### Podcast Agents (Session 496)

**Purpose:** AI Podcast Studio - Generate debate podcasts with multi-agent discussions and TTS audio

**Location:** `core/agents/podcast/`

#### PodcastCoordinatorAgent

**File:** `core/agents/podcast/podcast_coordinator_agent.py`

**Purpose:** Orchestrates podcast creation by coordinating debaters and generating scripts

**Tools:**
- `structure_debate` - Create debate structure with participants and perspectives
- `generate_discussion_points` - Generate key discussion topics
- `generate_podcast_script` - Generate complete script with speaker labels

**Parameters:**
```python
{
    "topic": "Should AI replace human jobs?",
    "format_type": "debate",  # debate, roundtable, interview, monologue
    "participants": 4  # 2-4 participants
}
```

#### ModeratorAgent

**File:** `core/agents/podcast/moderator_agent.py`

**Purpose:** Hosts podcast debates as a warm, engaging moderator

**Voice:** Antoni (warm narrator)

**Tools:**
- `create_introduction` - Generate episode intro
- `generate_follow_up_questions` - Create probing follow-ups
- `summarize_discussion` - Recap key points
- `create_outro` - Generate episode closing

#### DebateAdvocateAgent

**File:** `core/agents/podcast/debate_advocate_agent.py`

**Purpose:** Argues FOR debate topics with research and enthusiasm

**Voice:** Rachel (enthusiastic, warm)

**Tools:**
- `research_positive_aspects` - Find benefits and success stories
- `build_argument` - Build structured arguments with evidence
- `generate_debate_statements` - Generate opening/key points/closing

#### DebateSkepticAgent

**File:** `core/agents/podcast/debate_skeptic_agent.py`

**Purpose:** Challenges debate topics with critical analysis

**Voice:** Clyde (authoritative, deep)

**Tools:**
- `research_concerns` - Find risks and problems
- `build_critique` - Build structured critique with evidence
- `generate_debate_statements` - Generate concerns and tough questions

### Audio Generation Service

**File:** `core/services/podcast_audio_service.py`

**Voice Mapping:**
| Speaker | Voice ID | Name |
|---------|----------|------|
| HOST/MODERATOR | ErXwobaYiN019PkySvjV | Antoni |
| ADVOCATE | 21m00Tcm4TlvDq8ikWAM | Rachel |
| SKEPTIC | 2EiwWnXFnvU5JabPnv8n | Clyde |
| ANALYST | 5Q0t7uMcjvnagumLfvZi | Paul |

**Functions:**
- `parse_podcast_script()` - Parse script into speaker segments
- `generate_segment_audio()` - Generate TTS via ElevenLabs
- `concatenate_audio_segments()` - Combine audio with pydub
- `generate_podcast_audio()` - Main orchestrator with progress

**Cannot Access:** Image, video, editing tools

---

### LegalDocDrafterAgent (Session 403, Enhanced 404F + Patch 4C)

**Purpose:** Pro Se Legal Assistant for Colorado Family Law

**Location:** `core/agents/legal/legal_doc_drafter_agent.py`

**Tools (10 total):**

*Core Tools:*
- `search_legal_resources` - Search spider network for legal info
- `draft_motion` - Generate motion templates
- `draft_email` - Generate meet-and-confer emails
- `draft_declaration` - Generate declaration templates
- `get_form_info` - Get Colorado JDF form information
- `explain_procedure` - Explain court procedures

*Session 404 Tools (Motion Rewriting):*
- `analyze_denied_motion` - Analyze why motion was denied, identify all deficiencies
- `rewrite_motion` - Generate corrected motion in proper JDF format with affidavit
- `generate_evidence_checklist` - Create checklist of required exhibits for motion type
- `check_non_party_issues` - Detect non-party relief requests and provide corrections

**Parameters:**
```python
{
    "query": "How do I file for divorce in Colorado?",
    "document_type": "guidance",  # guidance, motion, email, declaration, checklist
    "case_type": "divorce",  # divorce, custody, child_support, parenting_time, modification, enforcement
    "jurisdiction": "Colorado"
}
```

**Key Features:**
- Colorado family law focus (JDF forms)
- NOT legal advice - general information only
- Motion types: continuance, modify_parenting_time, modify_child_support, enforce_order, reconsideration
- **Case File Upload** - Analyze uploaded PDFs, DOC, TXT files
- **Document Context Injection** - Auto-injects uploaded case files into prompts
- **Corrective Filing Generation** - Generates refilings based on denied motion analysis
- **Motion Rewriter (Session 404)** - Transforms denied motions into correct JDF format
- **Non-Party Detection (Session 404)** - Warns when relief sought against non-parties
- **Evidence Checklist (Session 404)** - Motion-type specific exhibit requirements

**Session 404 Enhancements (Initial):**
- `JDF_FORM_MAPPING` - Maps relief types to correct Colorado forms
- `STATUTORY_CRITERIA` - Aligns facts to criteria categories (no statute citations)
- `NON_PARTY_INDICATORS` - Detects relief requests against girlfriends, grandparents, etc.
- Rewrote system prompt to focus on PROCEDURE only, never strategy
- Output structure: caption → facts → affidavit → proposed order → checklist

**Session 404F County/State Inference:**
- Auto-infers county and state from court address when not explicitly provided
- Colorado city → county mapping (Fort Collins → LARIMER, Denver → DENVER, etc.)
- State abbreviation expansion (CO → COLORADO, CA → CALIFORNIA)
- Falls back gracefully when inference not possible

**Session 404 Patch 4C (Incident & Enumeration Normalization):**
- **Strict 1-4 Numbered Allegations Format:**
  - Allegations 1-3: Individual incidents as complete sentences with dates
  - Allegation 4: Impact/pattern paragraph summarizing harm
- **Inline List Splitting:** Handles semicolon-separated inline lists ("1. Today...; 2. August 29...") and splits into separate allegations
- **No Raw PDF Fragments:** Removes orphan numbering ("1." "2." without content)
- **No Subheadings:** Strips "Today's Incident –" style headers
- **Date-Anchored Extraction:** Finds sentences with date references
- **Relative Time Handling:** Converts "the following week", "today" to dates
- **Deduplication:** Prevents duplicate incidents by description similarity
- **Full Restatement Section:** PART 5 contains 1:1 mapping of all petitioner's paragraphs (for verification)

**New Helper Functions (Patch 4C):**
```python
_extract_incident_candidates(text) → List[Tuple[str, str, int]]  # (text, date, priority)
_clean_incident_text(text) → str                                  # Strip noise
_extract_date_from_text(text) → str                               # Find dates
_build_clean_allegations(incidents, original) → List[str]         # Build 1-3
_generate_impact_paragraph(incidents, original) → str             # Build 4
```

**Database Models (Session 403):**
- `LegalCase` - User's case info (parties, dates, status)
- `LegalDocument` - Generated/uploaded documents
- `LegalResearchResult` - Saved research with embeddings
- `LegalMemory` - Legal-specific learning patterns

**Data Sources:**
- 6 legal spiders (colorado_family_law, justia_family_law, legal_news, courtlistener, findlaw, lii)
- Colorado JDF form database (embedded)
- User's uploaded case files (LegalDocument model)

**Cannot Access:** Image, video, audio, editing, creation tools

**UI Panel:** `ai_core/templates/components/panels/legal_assistant_panel.html`

**Sub-Tabs:**
- Guidance - Ask legal questions
- Documents - Motion/email/declaration templates
- Colorado Forms - JDF form reference
- Procedures - Step-by-step guides
- **My Case Files** - Upload and analyze case documents

---

### Stock Market Intelligence Agents (Session 465)

**Purpose:** Autonomous market intelligence system generating daily briefs with bull/bear debates

**Location:** `core/agents/stocks/`

**Part of:** Market Intelligence Desk (First Tier 1 Autonomous Situation)

#### BullCaseAgent

**Purpose:** Makes arguments for price appreciation (long thesis)

**Location:** `core/agents/stocks/bull_case_agent.py`

**Tools:**
- `analyze_fundamentals` - Revenue growth, margins, moat analysis
- `analyze_technicals` - Price action, volume, momentum
- `sector_positioning` - Industry trends, competitive position
- `catalyst_identification` - Upcoming events that could drive price up

**Behavior:** Generates bullish thesis with conviction score (0-100)

**Learning Integration:** Confidence multiplier based on prediction accuracy

---

#### BearCaseAgent

**Purpose:** Makes arguments for price depreciation (short thesis)

**Location:** `core/agents/stocks/bear_case_agent.py`

**Tools:**
- `risk_analysis` - Debt, valuation, market risk assessment
- `analyze_technicals` - Bearish patterns, resistance levels
- `downside_catalysts` - Events that could drive price down
- `sector_headwinds` - Industry challenges, competition

**Behavior:** Generates bearish thesis with conviction score (0-100)

**Learning Integration:** Confidence multiplier based on prediction accuracy

---

#### SignalScannerAgent

**Purpose:** Detects technical patterns and trading signals

**Location:** `core/agents/stocks/signal_scanner_agent.py`

**Tools:**
- `scan_patterns` - Chart patterns (breakouts, reversals, continuations)
- `volume_analysis` - Unusual volume activity, institutional flows
- `momentum_scan` - RSI, MACD, Stochastic momentum shifts
- `options_flow` - Unusual options activity (smart money positioning)

**Behavior:** Identifies high-probability technical setups with entry/exit criteria

**Integration:** Validates bull/bear cases with technical confirmation

---

#### StockAuditCoordinator

**Purpose:** Detects anomalies and risk signals across stocks

**Location:** `core/agents/stocks/stock_audit_coordinator.py`

**Tools:**
- `audit_fundamentals` - Accounting red flags, unusual metrics
- `audit_insider_activity` - Insider buying/selling patterns
- `audit_market_activity` - Volume spikes, price manipulation signals
- `audit_sec_filings` - 8-K events, material changes

**Behavior:** Generates risk alerts with severity levels (LOW/MEDIUM/HIGH/CRITICAL)

**Integration:** Feeds risk signals into market briefs

---

#### MarketIntelligenceCoordinator

**Purpose:** Synthesizes bull/bear/technical/risk into actionable brief

**Location:** `core/agents/stocks/market_intelligence_coordinator.py`

**Tools:**
- `synthesize_intelligence` - Combines all agent outputs
- `generate_brief` - Creates structured market brief
- `identify_opportunities` - High conviction plays
- `track_changes` - What changed from yesterday

**Output Structure:**
1. Executive Summary - Market thesis
2. High Conviction - Stocks with strong agreement
3. Debate Zone - Conflicting signals (alpha opportunities)
4. Risk Alerts - Items requiring attention
5. What Changed - Key differences from yesterday

**Delivery Channels:**
- Discord (#market-intelligence)
- Voice brief (ElevenLabs TTS - "Drew" voice)
- Web dashboard (MarketIntelligenceBrief model)

**Scheduling:**
- Daily: 6:30 AM Mon-Fri (before market open)
- Event-driven: Every 30 min during market hours when significant events occur

**Learning Loop:**
- Records predictions as PredictionOutcome
- Tracks 7-day and 30-day accuracy
- Updates agent confidence multipliers (0.5x-1.5x)
- Agents improve over time based on track record

---

## Legacy Agent Ecosystem (22 Agents)

These agents exist in `agents/` directory and are used by the legacy system:

### Generation Agents
- `CreationAgent` - Image generation
- `TrainedCreationAgent` - LoRA-based generation
- `VideoAgent` - Video operations
- `AudioAgent` - Voice/audio
- `3DGenerationAgent` - 3D models

### Research & Analysis
- `ResearchAgent` - Web search + spiders
- `TrendAnalysisAgent` - Trend detection

### Strategy Agents (Session 241)
- `ContentStrategyAgent` - Content recommendations
- `SEOOptimizerAgent` - Hashtags, metadata
- `BrandIdentityAgent` - Brand consistency
- `SocialMediaAgent` - Platform-specific content
- `CreativeDirectorAgent` - High-level direction

### Executive Agents
- `CTOAgent` - Technical decisions
- `COOAgent` - Operations
- `CFOAgent` - Financial strategy
- `HRAgent` - Team coordination
- `MeetingCoordinatorAgent` - Meeting management

### Specialized
- `WorkflowOrchestrationAgent` - Complex workflows
- `OpportunityScoringAgent` - Score opportunities
- `PromptEngineeringAgent` - Prompt optimization
- `DataAnalystAgent` - Data analysis
- `MemoryIsolationAgent` - Memory namespace management

---

## Advisor Network (25 Legendary Advisors)

**Location:** `advisors/registry.py`

Advisors provide expertise for complex decisions:

### Investment/Finance
- Warren Buffett - Value investing
- Charlie Munger - Mental models
- Ray Dalio - Macro economics
- Cathie Wood - Disruptive innovation
- Peter Lynch - Growth investing
- Howard Marks - Risk management

### Tech/Innovation
- Elon Musk - First principles
- Steve Jobs - Design/UX
- Jeff Bezos - Customer obsession
- Reid Hoffman - Network effects
- Marc Andreessen - Software trends
- Paul Graham - Startup wisdom

### Creative
- Kanye West - Creative boldness
- David Ogilvy - Advertising
- Seth Godin - Marketing

### Plus 10 more specialists...

---

## Agent Configuration

### Base Agent Class

```python
from core.agents.base_agent import BaseAgent, AgentResult

class MyAgent(BaseAgent):
    name = "MyAgent"

    system_prompt = """You are MyAgent. You do X.

    You ONLY have access to these tools:
    - tool_1: Description
    - tool_2: Description

    You CANNOT:
    - Do Y (that's OtherAgent's job)
    - Do Z (that's AnotherAgent's job)
    """

    tools = [
        {
            "type": "function",
            "function": {
                "name": "tool_1",
                "description": "...",
                "parameters": {...}
            }
        }
    ]

    def execute(self, task, context, scifi_context, spider_context):
        # Agent logic here
        return AgentResult(
            success=True,
            message="Task completed",
            data={...},
            agent_name=self.name
        )
```

### TimeTravelMixin

All agents inherit decision tracking:

```python
class MyAgent(BaseAgent, TimeTravelMixin):
    def execute(self, task, context, scifi_context, spider_context):
        with self.time_travel_session("task_type", task):
            self.record_decision(
                decision_type="tool_selection",
                action="Calling tool_1",
                reasoning="Because X",
                confidence=0.95
            )

            result = self._execute_tool_call("tool_1", {...})

            self.mark_decision_outcome(
                success=result['success'],
                result_summary="..."
            )
```

---

## Agent Router

**Location:** `core/agent_router.py`

Deterministic routing - no LLM needed:

```python
class AgentRouter:
    AGENT_MAP = {
        "ImageAgent": ImageAgent,
        "VideoAgent": VideoAgent,
        "AudioAgent": AudioAgent,
        "ThreeDAgent": ThreeDAgent,
        "ImageEditingAgent": ImageEditingAgent,
        "VideoEditingAgent": VideoEditingAgent,
        "ResearchAgent": ResearchAgent,
        "WorkflowAgent": WorkflowAgent,
    }

    def route(self, agent_name: str, task: str, context: dict) -> AgentResult:
        agent_class = self.AGENT_MAP.get(agent_name)

        # Inject context
        scifi_context = SciFiIntegrationService.get_context(agent_name)
        spider_context = SpiderIntelligenceService.get_insights_for_prompt(task)

        agent = agent_class()
        return agent.execute(task, context, scifi_context, spider_context)
```

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CAPABILITIES.md](CAPABILITIES.md) - Full feature list
- [SPIDERS.md](SPIDERS.md) - Spider network
- [SCIFI_FEATURES.md](SCIFI_FEATURES.md) - Sci-fi features
