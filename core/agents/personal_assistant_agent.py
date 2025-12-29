"""
Personal Assistant Agent - The Traffic Cop
===========================================

Session 268: Phase 3 - Super Platform Integration
Session 293: Added business research agents + semantic routing

This agent is the main entry point for user requests in the clean architecture.
It receives messages, classifies intent, and delegates to specialized agents.

Unlike WorkflowAgent (which orchestrates multi-step workflows), this agent
handles the TOP-LEVEL routing decision:
- Is this a question? → Answer directly
- Is this a creation request? → Route to appropriate creation agent
- Is this a multi-step workflow? → Route to WorkflowAgent
- Is this an editing request? → Route to appropriate editing agent

Architecture:
    User → PersonalAssistantAgent → AgentRouter → Specialized Agent → Tools

Routing Strategy (Session 293):
    1. Semantic Routing (embeddings) - uses cosine similarity to match query to agents
    2. Keyword Fallback - if semantic confidence is low
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple

from core.agents.base_agent import BaseAgent, AgentResult, KnowledgeAttribution
from core.agents.routing_config import get_intent_keywords, AGENT_ROUTING_CONFIG

logger = logging.getLogger(__name__)

# Session 454: Import keywords from unified routing config
INTENT_KEYWORDS = get_intent_keywords()

# Session 454: Improved semantic routing with retry logic
_semantic_router = None
_semantic_router_last_attempt = None
_semantic_router_failure_count = 0
SEMANTIC_ROUTER_RETRY_INTERVAL = 300  # 5 minutes between retries
SEMANTIC_ROUTER_MAX_FAILURES = 3  # Give up after 3 consecutive failures

# Session 454: Routing analytics tracking
_routing_analytics = {
    'total_routes': 0,
    'routes_by_agent': {},
    'routes_by_method': {'semantic': 0, 'keyword': 0, 'workflow': 0, 'business_context': 0, 'gpt': 0},
    'question_vs_action': {'question': 0, 'action': 0},
    'recent_routes': [],  # Last 100 routing decisions
}
ROUTING_ANALYTICS_MAX_RECENT = 100


def record_routing_decision(
    task: str,
    selected_agent: str,
    method: str,
    confidence: float,
    is_question: bool,
    alternatives: list = None
):
    """
    Session 454: Record routing decision for analytics.

    Args:
        task: The user's task (truncated)
        selected_agent: Which agent was selected
        method: How the decision was made (semantic, keyword, workflow, etc.)
        confidence: Confidence score of the decision
        is_question: Whether this was classified as a question
        alternatives: Other agents that were considered
    """
    global _routing_analytics

    _routing_analytics['total_routes'] += 1

    # Track by agent
    if selected_agent not in _routing_analytics['routes_by_agent']:
        _routing_analytics['routes_by_agent'][selected_agent] = 0
    _routing_analytics['routes_by_agent'][selected_agent] += 1

    # Track by method
    if method in _routing_analytics['routes_by_method']:
        _routing_analytics['routes_by_method'][method] += 1

    # Track question vs action
    _routing_analytics['question_vs_action']['question' if is_question else 'action'] += 1

    # Store recent decision (circular buffer)
    decision = {
        'timestamp': time.time(),
        'task_preview': task[:100] if task else '',
        'agent': selected_agent,
        'method': method,
        'confidence': confidence,
        'is_question': is_question,
        'alternatives': alternatives[:3] if alternatives else [],
    }
    _routing_analytics['recent_routes'].append(decision)
    if len(_routing_analytics['recent_routes']) > ROUTING_ANALYTICS_MAX_RECENT:
        _routing_analytics['recent_routes'].pop(0)

    # Log for debugging
    logger.info(
        f"ROUTING: '{task[:50]}...' -> {selected_agent} "
        f"(method={method}, confidence={confidence:.2f}, is_question={is_question})"
    )


def get_routing_analytics() -> dict:
    """
    Session 454: Get current routing analytics.

    Returns:
        Dict with routing statistics
    """
    global _routing_analytics

    # Calculate percentages
    total = _routing_analytics['total_routes']
    if total == 0:
        return _routing_analytics

    analytics = _routing_analytics.copy()
    analytics['agent_percentages'] = {
        agent: (count / total * 100)
        for agent, count in _routing_analytics['routes_by_agent'].items()
    }
    analytics['method_percentages'] = {
        method: (count / total * 100)
        for method, count in _routing_analytics['routes_by_method'].items()
    }

    return analytics


def get_semantic_router():
    """
    Lazy-load the semantic routing service with retry logic.

    Session 454: Fixed silent failure by:
    1. Adding retry mechanism with exponential backoff
    2. Logging detailed failure reasons
    3. Allowing recovery from transient failures
    """
    global _semantic_router, _semantic_router_last_attempt, _semantic_router_failure_count

    # Already initialized successfully
    if _semantic_router is not None and _semantic_router is not False:
        return _semantic_router

    # Check if we should retry after previous failure
    if _semantic_router is False:
        if _semantic_router_failure_count >= SEMANTIC_ROUTER_MAX_FAILURES:
            # Too many failures, don't retry forever
            return None

        # Check if enough time has passed for retry
        if _semantic_router_last_attempt:
            elapsed = (time.time() - _semantic_router_last_attempt)
            # Exponential backoff: 5min, 10min, 20min
            retry_interval = SEMANTIC_ROUTER_RETRY_INTERVAL * (2 ** (_semantic_router_failure_count - 1))
            if elapsed < retry_interval:
                return None  # Not time to retry yet

        # Reset for retry
        _semantic_router = None
        logger.info(f"Retrying semantic routing initialization (attempt {_semantic_router_failure_count + 1})")

    # Attempt initialization
    if _semantic_router is None:
        _semantic_router_last_attempt = time.time()
        try:
            from core.services.semantic_routing import SemanticRoutingService
            router = SemanticRoutingService()

            if router.initialize():
                _semantic_router = router
                _semantic_router_failure_count = 0  # Reset on success
                logger.info("Semantic routing service initialized successfully")
            else:
                raise Exception("SemanticRoutingService.initialize() returned False")

        except ImportError as e:
            _semantic_router = False
            _semantic_router_failure_count += 1
            logger.error(f"Semantic routing import failed: {e}")

        except Exception as e:
            _semantic_router = False
            _semantic_router_failure_count += 1
            logger.warning(
                f"Semantic routing initialization failed (attempt {_semantic_router_failure_count}): {e}. "
                f"Will retry in {SEMANTIC_ROUTER_RETRY_INTERVAL * (2 ** (_semantic_router_failure_count - 1))}s"
            )

    return _semantic_router if _semantic_router and _semantic_router is not False else None


# Intent-to-Agent Mapping
INTENT_AGENT_MAP = {
    # Creation intents → Creation agents
    'create_image': 'ImageAgent',
    'create_logo': 'ImageAgent',
    'create_banner': 'ImageAgent',
    'create_illustration': 'ImageAgent',
    'generate_image': 'ImageAgent',

    'create_video': 'VideoAgent',
    'generate_video': 'VideoAgent',
    'animate': 'VideoAgent',
    'animate_image': 'VideoAgent',

    'create_audio': 'AudioAgent',
    'generate_voice': 'AudioAgent',
    'text_to_speech': 'AudioAgent',
    'voiceover': 'AudioAgent',

    'create_3d': 'ThreeDAgent',
    'convert_to_3d': 'ThreeDAgent',
    '3d_model': 'ThreeDAgent',

    # Editing intents → Editing agents
    'upscale': 'ImageEditingAgent',
    'remove_background': 'ImageEditingAgent',
    'edit_image': 'ImageEditingAgent',
    'recolor': 'ImageEditingAgent',
    'variations': 'ImageEditingAgent',

    'trim_video': 'VideoEditingAgent',
    'edit_video': 'VideoEditingAgent',
    'add_text_to_video': 'VideoEditingAgent',
    'video_effects': 'VideoEditingAgent',

    # Research intents → Research agent (for general searches)
    'search': 'ResearchAgent',
    'find': 'ResearchAgent',
    'trending': 'ResearchAgent',
    'analyze_trends': 'ResearchAgent',

    # Business Research intents → Business Research agents (Session 293)
    'market_research': 'CompetitorAnalysisAgent',
    'competitor_analysis': 'CompetitorAnalysisAgent',
    'swot_analysis': 'CompetitorAnalysisAgent',
    'business_research': 'CompetitorAnalysisAgent',
    'startup_research': 'CompetitorAnalysisAgent',
    'customer_research': 'CustomerResearchAgent',
    'customer_personas': 'CustomerResearchAgent',
    'pain_points': 'CustomerResearchAgent',

    # Legal intents → Legal agent (Session 403)
    'legal_question': 'LegalDocDrafterAgent',
    'legal_document': 'LegalDocDrafterAgent',
    'draft_motion': 'LegalDocDrafterAgent',
    'divorce_help': 'LegalDocDrafterAgent',
    'custody_help': 'LegalDocDrafterAgent',
    'court_procedure': 'LegalDocDrafterAgent',

    # Multi-step intents → Workflow agent
    'research_and_create': 'WorkflowAgent',
    'brand_package': 'WorkflowAgent',
    'thumbnail_package': 'WorkflowAgent',
    'workflow': 'WorkflowAgent',
}

# Session 454: INTENT_KEYWORDS now imported from routing_config.py (single source of truth)
# See: core/agents/routing_config.py for the unified agent routing configuration

# Session 414: UI Navigation guidance for platform features
# Maps keywords to helpful navigation instructions
UI_NAVIGATION_GUIDE = {
    # Spider data and data collection
    'spider': {
        'keywords': ['spider', 'spiders', 'crawl', 'crawling', 'data collection', 'web scraping'],
        'guidance': """**Spider Network Access:**
- Click the **🕷️ Intelligence** tab in the left sidebar
- Use the **Data Feed** sub-tab to see all collected data
- Use the **Knowledge** sub-tab to see what agents have learned
- Use the **Timeline** sub-tab to see recent spider activity
- Spiders run automatically every hour via Celery tasks"""
    },
    # Agent conversations
    'conversations': {
        'keywords': ['conversations', 'agent chat', 'agents talking', 'agent discussions', 'what are agents saying', 'agent dialogue'],
        'guidance': """**Agent Conversations Access:**
- Click the **🤖 Social** tab in the left sidebar
- The **Conversations** sub-tab shows real-time agent-to-agent discussions
- Agents automatically converse every 2 hours about creative topics
- You can see what they're learning from each other!"""
    },
    # Agent dreams
    'dreams': {
        'keywords': ['dreams', 'agent dreams', 'dreaming', 'what agents dream', 'creative dreams'],
        'guidance': """**Agent Dreams Access:**
- Click the **🤖 Social** tab in the left sidebar
- Use the **Dreams** sub-tab to see agent creative dreams
- Dreams are generated when agents are idle (every 4 hours)
- Dreams reveal unique insights and creative ideas from each agent"""
    },
    # Boardroom/decisions
    'boardroom': {
        'keywords': ['boardroom', 'decisions', 'board meeting', 'agent decisions', 'policy', 'policies', 'canonical'],
        'guidance': """**Boardroom & Decisions Access:**
- Click the **📊 Decisions** tab in the left sidebar
- **Pending Decisions** shows proposals awaiting your review
- **Active Policies** shows decisions you've approved
- **History** shows past decisions and outcomes
- Agents can propose policies based on their learnings!"""
    },
    # Evolution/growth
    'evolution': {
        'keywords': ['evolution', 'agent levels', 'xp', 'experience', 'agent growth', 'leveling'],
        'guidance': """**Agent Evolution Access:**
- Click the **📈 Growth** tab in the left sidebar
- See agent levels, XP, and progression
- Agents level up by completing tasks and learning
- Higher-level agents have enhanced capabilities"""
    },
    # Hive mind
    'hivemind': {
        'keywords': ['hive mind', 'collective', 'collective intelligence', 'shared learning', 'knowledge sharing'],
        'guidance': """**Collective Intelligence Access:**
- Click the **🧠 Hive Mind** tab in the left sidebar
- See shared knowledge across all agents
- Watch real-time knowledge transfer between agents
- View the knowledge graph of agent learnings"""
    },
}


class PersonalAssistantAgent(BaseAgent):
    """
    The main entry point agent that routes requests to specialized agents.

    This agent:
    1. Analyzes the user's message to understand intent
    2. Determines if it's a question (answer directly) or action request (delegate)
    3. Routes to the appropriate specialized agent via AgentRouter
    4. Synthesizes and returns the response

    It is the "traffic cop" of the clean architecture.
    """

    name = "PersonalAssistantAgent"

    system_prompt = """You are the Personal Assistant, the main interface for the AI Studio.

## CRITICAL: YOU HAVE REAL-TIME DATA ACCESS
You are NOT a vanilla LLM with a 2024 knowledge cutoff. You have access to:
- **77 LIVE SPIDERS** that gather real-time data from the web
- **71 SPECIALIZED AGENTS** with domain expertise
- **Real-time sports odds and scores** via TheOddsAPI spider
- **Live news and trends** from TechCrunch, HackerNews, Reddit, and more
- **Financial data** from CoinGecko, Yahoo Finance, Polygon, Kalshi
- **The current date is provided in your context**

When users ask for LIVE DATA (sports scores, current news, stock prices, odds):
- DO NOT say "I can't access live data" - you CAN through your spider network
- Delegate to the appropriate agent (SportsOddsAnalyst, ResearchAgent, etc.)
- Your spiders run continuously and have recent data

Your job is to understand what the user wants and route their request appropriately.

For SYSTEM STATUS queries (what should I focus on, catch me up, status, what needs attention, overview):
- IMPORTANT: When the user asks "what should I focus on?" in this platform context, they mean SYSTEM status
- Look at the Platform Intelligence section for "URGENT" or "Important System Items"
- Summarize what needs attention: failed cycles, stale concerns, overdue channels, pending dreams
- Do NOT give generic productivity advice - they want to know about THIS SYSTEM
- If system items are provided in context, prioritize discussing those

For FOLLOW-UP requests (complete those tasks, do what you suggested, work on those, proceed):
- IMPORTANT: When the user says "complete the tasks you suggested" or similar, they mean the SYSTEM attention items
- Look at the Platform Intelligence section for the specific attention items
- Explain which items CAN be automated vs which NEED user approval
- Boardroom decisions (pending decisions) = NEED user review/approval in the UI
- Failed cycles = May need manual investigation
- Overdue channels = Can trigger content generation
- If unsure, explain what each item is and how the user can address it

For QUESTIONS (what is, how does, explain, tell me about):
- Answer directly using your knowledge and any provided context

For CREATION requests (create, make, generate, design):
- Identify what type of content they want
- Delegate to the appropriate agent using delegate_to_agent

For EDITING requests (upscale, remove background, trim, edit):
- Identify the editing operation needed
- Delegate to the appropriate editing agent

For WRITING requests (write, blog post, podcast script, video script, article, newsletter):
- IMPORTANT: Use ContentWriterAgent for ALL written text content requests
- This includes: "write a blog post", "write a podcast script", "write an article", "create a newsletter"
- ContentWriterAgent transforms research into professionally formatted written content
- DO NOT use TrendAnalysisAgent or WorkflowAgent for writing requests

For RESEARCH requests (search, find, trending, analyze):
- For general trending/news: use ResearchAgent
- For BUSINESS/MARKET/STARTUP research: use CompetitorAnalysisAgent (SWOT, competitors)
- For CUSTOMER research: use CustomerResearchAgent (personas, pain points)

For SPORTS requests (scores, odds, betting, games, NFL, NBA, MLB, NHL):
- Use SportsOddsAnalyst for live odds, spreads, and game information
- You have access to real-time data from 40+ bookmakers via TheOddsAPI
- Sports covered: NFL, NBA, MLB, NHL, NCAAF, NCAAB, Soccer, UFC/MMA, Tennis, Golf
- NEVER say "I can't access live sports data" - YOU CAN through SportsOddsAnalyst

For FINANCIAL/MARKET requests (stocks, crypto, prices, markets):
- Use ResearchAgent which has access to financial spiders (Yahoo Finance, CoinGecko, Polygon)
- For prediction markets: use PredictionMarketAnalyst (Kalshi, Polymarket)

For LEGAL requests (divorce, custody, court, motion):
- Delegate to LegalDocDrafterAgent for Colorado family law questions
- This agent provides GENERAL LEGAL INFORMATION ONLY, not legal advice
- Always recommend consulting a licensed attorney

For CODE REVIEW requests (review, audit, check, analyze code/file):
- ALWAYS use CodeReviewAgent for reviewing existing code
- CodeReviewAgent can read files and analyze them for bugs, security, performance
- Do NOT use CodeGeneratorAgent for reviews - that is for WRITING NEW code only

For CODE GENERATION requests (generate, create, write code):
- Use CodeGeneratorAgent to write new code from specifications
- Use FullStackDeveloperAgent for complete feature implementations

For DEVOPS requests (deploy, CI/CD, Docker, Kubernetes, infrastructure):
- Use DevOpsAgent for deployment and infrastructure questions

For COMPLEX MULTI-STEP requests (research and create, brand package):
- Delegate to WorkflowAgent for orchestration

When delegating, provide:
1. The agent name (ImageAgent, VideoAgent, etc.)
2. A clear task description
3. Any relevant context (count, style, references)

Available agents:
- ImageAgent: Create images (logos, banners, illustrations)
- VideoAgent: Create videos (text-to-video, animations)
- AudioAgent: Create audio (TTS, voiceovers)
- ThreeDAgent: Create 3D models
- ImageEditingAgent: Edit images (upscale, remove bg, recolor)
- VideoEditingAgent: Edit videos (trim, effects, text)
- ResearchAgent: Search web and spider network (general trending, news, financial data)
- SportsOddsAnalyst: LIVE sports scores, odds, spreads from 40+ bookmakers (NFL, NBA, MLB, NHL, Soccer, UFC)
- PredictionMarketAnalyst: Prediction markets (Kalshi, Polymarket) and event contracts
- ArbitrageDetector: Find arbitrage opportunities across sportsbooks
- CompetitorAnalysisAgent: Business/market/startup research, SWOT, competitor analysis
- CustomerResearchAgent: Customer personas, pain points, sentiment
- LegalDocDrafterAgent: Colorado family law info, motion templates, court procedures (NOT legal advice)
- WorkflowAgent: Multi-step workflows"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "delegate_to_agent",
                "description": "Delegate a task to a specialized agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": """Which agent to delegate to:

RESEARCH & ANALYSIS (use for questions, trends, market info):
- ResearchAgent: Web search, spider data, general research, "what's trending", model recommendations
- TrendAnalysisAgent: Market trends, industry analysis, trend reports
- CompetitorAnalysisAgent: Business/market research, SWOT, competitor analysis
- CustomerResearchAgent: Customer personas, pain points, sentiment

WRITING & CONTENT:
- ContentWriterAgent: Blog posts, articles, scripts, newsletters - USE when user says "write a..."

CREATION (generating new assets):
- ImageAgent: Logos, banners, illustrations, any image generation
- VideoAgent: Video generation, animations, text-to-video
- AudioAgent: TTS, voiceovers, audio generation
- ThreeDAgent: 3D model generation

EDITING (modifying existing assets):
- ImageEditingAgent: Upscale, remove background, image variations
- VideoEditingAgent: Trim, effects, text overlays

DEVELOPMENT (code, infrastructure):
- CodeGeneratorAgent: WRITE NEW code from specifications (Python, JS, etc.) - use when user says "generate", "create", "write" code
- CodeReviewAgent: REVIEW EXISTING code for bugs, security, best practices - USE THIS when user says "review", "audit", "check", "analyze" code or a file
- FullStackDeveloperAgent: Build complete features (frontend + backend)
- DevOpsAgent: CI/CD, Docker, Kubernetes, infrastructure - USE for deployment questions

STRATEGY & PLANNING:
- BrandIdentityAgent: Brand colors, style, visual identity
- ContentStrategyAgent: Content planning, calendars
- SEOOptimizerAgent: Keywords, hashtags, metadata
- SocialMediaAgent: Platform-specific content strategy
- CTOAgent: Technical planning, architecture decisions
- COOAgent: Operations planning, risk analysis
- CreativeDirectorAgent: Creative guidance, prompt enhancement
- MeetingCoordinatorAgent: Coordinate meetings between multiple agents

SPECIALIZED:
- LegalDocDrafterAgent: Colorado family law, motion templates (NOT legal advice)
- PodcastCoordinatorAgent: Create AI podcast debates with multiple voices
- AISeriesWorkflowAgent: Multi-episode content series
- ResolveAgent: DaVinci Resolve video rendering with trend-based color grading
- AutonomousContentStudioCoordinator: Run autonomous content generation with agent debates

TRAINING & SCORING:
- CharacterTrainingAgent: LoRA character training
- TrainedCreationAgent: Generate with trained models
- OpportunityScoringAgent: Score business opportunities

SPORTS & BETTING (LIVE DATA - use for scores, odds, games):
- SportsOddsAnalyst: LIVE sports odds/scores from 40+ bookmakers (NFL, NBA, MLB, NHL, Soccer, UFC)
- PredictionMarketAnalyst: Prediction markets (Kalshi, Polymarket, event contracts)
- ArbitrageDetector: Find arbitrage opportunities across sportsbooks

ANALYSIS & AUDIT:
- StockAuditCoordinator: Stock market analysis and audit
- BlockchainAuditCoordinator: Blockchain/crypto analysis and audit
- ContentAuditAgent: Content moderation and safety audit

SECURITY:
- MemoryIsolationAgent: Memory isolation and security sandboxing

CONTENT STUDIO AGENTS (internal debate team):
- TopicMinerAgent: Find trending topics and opportunities
- ContrarianAgent: Challenge ideas, find weaknesses
- PerformanceAnalystAgent: Analyze historical performance data

PODCAST DEBATE AGENTS (internal podcast team):
- DebateAdvocateAgent: Argue FOR a position in debates
- DebateSkepticAgent: Argue AGAINST a position in debates
- ModeratorAgent: Moderate debates between agents

ORCHESTRATION:
- WorkflowAgent: Multi-step workflows combining multiple agents""",
                            "enum": [
                                # Research & Analysis
                                "ResearchAgent",
                                "TrendAnalysisAgent",
                                "CompetitorAnalysisAgent",
                                "CustomerResearchAgent",
                                # Sports & Betting (LIVE DATA)
                                "SportsOddsAnalyst",
                                "PredictionMarketAnalyst",
                                "ArbitrageDetector",
                                # Writing agents
                                "ContentWriterAgent",
                                # Creation agents
                                "ImageAgent",
                                "VideoAgent",
                                "AudioAgent",
                                "ThreeDAgent",
                                # Editing agents
                                "ImageEditingAgent",
                                "VideoEditingAgent",
                                # Development agents
                                "CodeGeneratorAgent",
                                "CodeReviewAgent",
                                "FullStackDeveloperAgent",
                                "DevOpsAgent",
                                # Strategy & Planning agents
                                "BrandIdentityAgent",
                                "ContentStrategyAgent",
                                "SEOOptimizerAgent",
                                "SocialMediaAgent",
                                "CTOAgent",
                                "COOAgent",
                                "CreativeDirectorAgent",
                                "MeetingCoordinatorAgent",
                                # Specialized agents
                                "LegalDocDrafterAgent",
                                "PodcastCoordinatorAgent",
                                "AISeriesWorkflowAgent",
                                "ResolveAgent",
                                "AutonomousContentStudioCoordinator",
                                # Training & Scoring agents
                                "CharacterTrainingAgent",
                                "TrainedCreationAgent",
                                "OpportunityScoringAgent",
                                # Analysis & Audit agents (Session 499)
                                "StockAuditCoordinator",
                                "BlockchainAuditCoordinator",
                                "ContentAuditAgent",
                                # Security agents
                                "MemoryIsolationAgent",
                                # Content Studio internal agents (Session 499)
                                "TopicMinerAgent",
                                "ContrarianAgent",
                                "PerformanceAnalystAgent",
                                # Podcast internal agents (Session 499)
                                "DebateAdvocateAgent",
                                "DebateSkepticAgent",
                                "ModeratorAgent",
                                # Orchestration
                                "WorkflowAgent"
                            ]
                        },
                        "task": {
                            "type": "string",
                            "description": "The task to perform, in natural language"
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context (count, style, reference_ids, etc.)"
                        }
                    },
                    "required": ["agent_name", "task"]
                }
            }
        },
        # Session 575: Direct sports data tool - queries internal API
        {
            "type": "function",
            "function": {
                "name": "get_sports_data",
                "description": """Get LIVE sports scores and odds from the system's internal data.
USE THIS for questions like:
- "What's the score of the [team] game?"
- "NFL scores today"
- "Who's winning the [team] game?"
- "Current NBA games"

This queries our INTERNAL database - no external lookup needed.
The system already has real-time data from 40+ bookmakers.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sport": {
                            "type": "string",
                            "description": "Sport to query",
                            "enum": ["nfl", "nba", "mlb", "nhl", "ncaaf", "ncaab", "soccer", "ufc"]
                        },
                        "team": {
                            "type": "string",
                            "description": "Optional team name to filter results (e.g., 'Chiefs', 'Lakers')"
                        }
                    },
                    "required": ["sport"]
                }
            }
        },
        # Session 576: System Status Tool
        {
            "type": "function",
            "function": {
                "name": "get_system_status",
                "description": """Get system attention items, pending decisions, and health status.
USE THIS for questions like:
- "What needs my attention?"
- "System status"
- "What decisions are pending?"
- "Show me action items"
- "What should I focus on?"

Returns pending boardroom decisions, failed cycles, stale concerns, and overdue content.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["all", "decisions", "health", "content", "urgent"],
                            "description": "Filter by category (default: all)"
                        },
                        "max_items": {
                            "type": "integer",
                            "description": "Maximum items to return (default: 10)"
                        }
                    }
                }
            }
        },
        # Session 576: Promote Boardroom Decision Tool
        {
            "type": "function",
            "function": {
                "name": "promote_boardroom_decision",
                "description": """Approve a pending decision from the boardroom.
USE THIS when user says:
- "Approve that decision"
- "Yes, let's go with that"
- "Promote the policy"
- "Accept the recommendation"

Requires the decision_id from get_system_status or attention items.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "decision_id": {
                            "type": "string",
                            "description": "The UUID of the decision to approve"
                        }
                    },
                    "required": ["decision_id"]
                }
            }
        },
        # Session 576: Reject Boardroom Decision Tool
        {
            "type": "function",
            "function": {
                "name": "reject_boardroom_decision",
                "description": """Reject a pending decision from the boardroom.
USE THIS when user says:
- "Reject that decision"
- "No, that won't work"
- "Decline the recommendation"

Requires the decision_id and a reason for rejection.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "decision_id": {
                            "type": "string",
                            "description": "The UUID of the decision to reject"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for rejection"
                        }
                    },
                    "required": ["decision_id", "reason"]
                }
            }
        },
        # Session 576: Query Agent Data Tool
        {
            "type": "function",
            "function": {
                "name": "query_agent_data",
                "description": """Query agent activity, learning progress, and performance metrics.
USE THIS for questions like:
- "Which agents are most active?"
- "Show me agent progress"
- "What did agents do today?"
- "How is ResearchAgent performing?"

Returns agent activity levels, XP, levels, and recent contributions.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Specific agent to query (optional)"
                        },
                        "metric_type": {
                            "type": "string",
                            "enum": ["activity", "learning", "performance", "all"],
                            "description": "Type of data to retrieve (default: all)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max agents to return (default: 10)"
                        }
                    }
                }
            }
        },
        # Session 576: Spider Intelligence Tool
        {
            "type": "function",
            "function": {
                "name": "get_spider_intelligence",
                "description": """Query spider network for trending topics and fresh data.
USE THIS for questions like:
- "What's trending in tech?"
- "Any fresh news?"
- "What are spiders finding?"
- "Show me recent data"

Returns trending topics, data freshness, and category coverage.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["all", "tech", "finance", "sports", "news", "legal", "entertainment"],
                            "description": "Data category to query (default: all)"
                        },
                        "hours": {
                            "type": "integer",
                            "description": "How many hours back to look (default: 24)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max items to return (default: 10)"
                        }
                    }
                }
            }
        },
        # Session 577: Phase 2 Tools
        {
            "type": "function",
            "function": {
                "name": "execute_spider",
                "description": """Run a specific spider on demand to fetch fresh data.
USE THIS for requests like:
- "Run the HackerNews spider"
- "Fetch latest from TechCrunch"
- "Update crypto prices"
- "Get fresh news"

Available categories: tech, finance, news, legal, entertainment, jobs, crypto.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "spider_name": {
                            "type": "string",
                            "description": "Spider name (e.g., 'hackernews', 'techcrunch', 'coingecko', 'kalshi')"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["tech", "finance", "news", "legal", "entertainment", "jobs", "crypto"],
                            "description": "Run all spiders in a category instead of a specific spider"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum items to fetch (default: 20)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_content",
                "description": """Trigger content creation workflows (images, videos, blog posts).
USE THIS for requests like:
- "Create an image of..."
- "Generate a blog post about..."
- "Make a video explaining..."
- "Design a logo for..."

Routes to ImageAgent, VideoAgent, ContentWriterAgent, etc.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content_type": {
                            "type": "string",
                            "enum": ["image", "video", "blog_post", "social_post", "logo"],
                            "description": "Type of content to create"
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Description of what to create"
                        },
                        "style": {
                            "type": "string",
                            "description": "Style preferences (e.g., 'photorealistic', 'cartoon', 'professional')"
                        }
                    },
                    "required": ["content_type", "prompt"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_content_channel",
                "description": """Control autonomous content channels (pause, resume, check status).
USE THIS for requests like:
- "Pause the AI Weekly channel"
- "Resume content generation"
- "Show channel status"
- "List my content channels"

These are autonomous channels that run forever, creating content on schedule.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "status", "pause", "resume"],
                            "description": "Action to perform"
                        },
                        "channel_id": {
                            "type": "integer",
                            "description": "Channel ID (required for status/pause/resume)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_prediction_markets",
                "description": """Query Kalshi prediction market data for event probabilities.
USE THIS for requests like:
- "What are the election odds?"
- "Show me prediction markets"
- "What's the probability of X?"
- "Any interesting markets?"

Returns real-time prediction market data with probabilities and volumes.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query or topic (e.g., 'election', 'fed rate', 'weather')"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["all", "politics", "economics", "climate", "tech", "sports"],
                            "description": "Market category filter"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max markets to return (default: 10)"
                        }
                    }
                }
            }
        },
        # Session 578: Phase 3 Tools
        {
            "type": "function",
            "function": {
                "name": "execute_workflow",
                "description": """Execute a multi-step workflow that coordinates multiple agents.
USE THIS for complex requests like:
- "Research AI trends and create 3 logo concepts"
- "Analyze competitors and write a strategy report"
- "Create a blog post with images"

Workflows coordinate multiple agents to complete complex tasks.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workflow_description": {
                            "type": "string",
                            "description": "Description of what the workflow should accomplish"
                        },
                        "workflow_type": {
                            "type": "string",
                            "enum": ["research_to_content", "content_pipeline", "analysis_report", "custom"],
                            "description": "Type of workflow to execute"
                        }
                    },
                    "required": ["workflow_description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_arbitrage",
                "description": """Find sports betting arbitrage opportunities across bookmakers.
USE THIS for requests like:
- "Any arbitrage opportunities?"
- "Show me arb alerts"
- "Check for sure bets"
- "Find guaranteed profit bets"

Returns opportunities where you can bet both sides for guaranteed profit.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sport": {
                            "type": "string",
                            "enum": ["nfl", "nba", "mlb", "nhl", "ncaaf", "ncaab", "soccer", "all"],
                            "description": "Sport to check (default: all)"
                        },
                        "min_profit": {
                            "type": "number",
                            "description": "Minimum profit percentage (default: 0.5%)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max opportunities to return (default: 10)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_bankroll",
                "description": """Query and manage your betting bankroll and wager history.
USE THIS for requests like:
- "What's my bankroll?"
- "Show betting history"
- "How am I doing on bets?"
- "Track my wagers"

Returns balance, win rate, ROI, and recent wagers.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["status", "history", "stats", "pending"],
                            "description": "Action to perform"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max wagers to return for history (default: 10)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_knowledge",
                "description": """Search the collective knowledge base learned by agents.
USE THIS for requests like:
- "What do agents know about X?"
- "Search our knowledge for Y"
- "Find insights about Z"
- "What have we learned about..."

Searches knowledge accumulated from spider data and agent learning.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "knowledge_type": {
                            "type": "string",
                            "enum": ["all", "trend", "market", "opportunity", "competitor", "content_idea"],
                            "description": "Type of knowledge to search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return (default: 10)"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        # Session 579: Phase 4 Tools
        {
            "type": "function",
            "function": {
                "name": "create_boardroom_decision",
                "description": """Submit a new decision to the Boardroom for review.
USE THIS for requests like:
- "Create a decision about X"
- "Submit this for boardroom review"
- "Propose a new policy"

Creates structured decisions that can be promoted to canonical policies.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title of the decision"
                        },
                        "description": {
                            "type": "string",
                            "description": "Full description and rationale"
                        },
                        "decision_type": {
                            "type": "string",
                            "enum": ["policy", "architecture", "tool", "workflow", "best_practice"],
                            "description": "Type of decision"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "description": "Priority level (default: medium)"
                        }
                    },
                    "required": ["title", "description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_dreams",
                "description": """Query agent dreams - creative ideas generated during idle time.
USE THIS for requests like:
- "What are agents dreaming about?"
- "Show me agent dreams"
- "Any creative ideas from agents?"

Dreams are speculative concepts and 'what if' scenarios.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Filter by specific agent"
                        },
                        "dream_type": {
                            "type": "string",
                            "enum": ["all", "product_idea", "feature_request", "integration", "optimization", "creative"],
                            "description": "Type of dream to query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max dreams to return (default: 10)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_situations",
                "description": """Control autonomous situations that run continuously.
USE THIS for requests like:
- "Show autonomous situations"
- "What situations are running?"
- "Pause the job matching situation"

Situations are Tier 1 Autonomous systems that run forever.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "status", "history"],
                            "description": "Action to perform"
                        },
                        "situation_type": {
                            "type": "string",
                            "description": "Filter by situation type (e.g., 'job_matching', 'content_studio')"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max items to return (default: 10)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_conversations",
                "description": """Query agent-to-agent conversations.
USE THIS for requests like:
- "What are agents discussing?"
- "Show agent conversations"
- "What have agents talked about?"

Conversations are where agents share knowledge and insights.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Filter by conversation topic"
                        },
                        "agent_name": {
                            "type": "string",
                            "description": "Filter by participating agent"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max conversations to return (default: 10)"
                        }
                    }
                }
            }
        }
    ]

    def __init__(self, user=None):
        super().__init__(user)
        self._router = None

    @property
    def router(self):
        """Lazy-load AgentRouter."""
        if self._router is None:
            from core.agent_router import AgentRouter
            self._router = AgentRouter(user=self.user)
        return self._router

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
        intelligence_context: Dict[str, Any] = None  # Session 565: Platform intelligence
    ) -> AgentResult:
        """
        Process a user message and route to appropriate agent or respond directly.
        """
        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}
        intelligence_context = intelligence_context or {}

        # Session 565: Store intelligence context for use in question answering
        self._intelligence_context = intelligence_context

        # Session 565: Debug logging for platform intelligence
        if intelligence_context:
            metadata = intelligence_context.get('metadata', {})
            logger.info(
                f"🧠 [Session 565] PersonalAssistant.execute() - intelligence_context: "
                f"{metadata.get('knowledge_count', 0)} knowledge, "
                f"{metadata.get('experts_count', 0)} experts, "
                f"{metadata.get('dreams_count', 0)} dreams"
            )

        # Session 483: Debug logging for spider context flow
        logger.info(f"🕷️ [Session 483] PersonalAssistant.execute() - spider_context keys: {list(spider_context.keys()) if spider_context else 'None'}")
        if spider_context:
            trends = spider_context.get('relevant_trends', [])
            logger.info(f"🕷️ [Session 483] spider_context has {len(trends)} relevant_trends")
            if trends:
                logger.info(f"🕷️ [Session 483] First trend: {trends[0] if trends else 'None'}")

        with self.time_travel_session("personal_assistant", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                # First, check if this is a simple question
                is_question, question_type = self._is_question(task)

                self.record_decision(
                    decision_type="intent_analysis",
                    action=f"Classified as {'question' if is_question else 'action request'}",
                    reasoning=f"Task: {task[:100]}",
                    confidence=0.85 if is_question else 0.9
                )

                if is_question:
                    # Answer directly without delegation
                    # Session 454: Pass question_type to enable enhanced handling
                    # Session 454: Track routing analytics
                    # Session 483: Debug logging
                    logger.info(f"🕷️ [Session 483] Detected question_type='{question_type}' for task: {task[:60]}")
                    record_routing_decision(
                        task=task,
                        selected_agent='PersonalAssistantAgent',
                        method='direct_answer',
                        confidence=0.85,
                        is_question=True,
                        alternatives=[]
                    )
                    return self._answer_question(task, scifi_context, spider_context, start_time, question_type)

                # It's an action request - determine which agent to use
                suggested_agent = self._detect_agent(task)

                if suggested_agent:
                    self.record_decision(
                        decision_type="agent_selection",
                        action=f"Routing to {suggested_agent}",
                        reasoning=f"Keywords matched for {suggested_agent}",
                        alternatives=list(INTENT_KEYWORDS.keys()),
                        confidence=0.9
                    )

                    # Session 454: Track routing analytics
                    # Determine routing method from the detect_agent decision
                    routing_method = 'keyword'  # Default to keyword
                    if hasattr(self, '_last_routing_method'):
                        routing_method = self._last_routing_method or 'keyword'
                    record_routing_decision(
                        task=task,
                        selected_agent=suggested_agent,
                        method=routing_method,
                        confidence=0.9,
                        is_question=False,
                        alternatives=list(INTENT_KEYWORDS.keys())[:5]
                    )

                    # Session 401: Get knowledge attribution before delegation
                    relevant_knowledge = self._get_relevant_knowledge_for_task(task)
                    attribution = self._build_knowledge_attribution(relevant_knowledge)

                    # Session 574: For action follow-ups to WorkflowAgent, inject system state
                    # So WorkflowAgent knows what "the checklist" or "those tasks" refers to
                    enhanced_task = task
                    enhanced_context = context.copy() if context else {}

                    if suggested_agent == 'WorkflowAgent' and getattr(self, '_last_routing_method', '') == 'action_followup':
                        try:
                            from core.services.system_state_aggregator import get_system_state_aggregator
                            aggregator = get_system_state_aggregator()
                            attention_items = aggregator.get_attention_items()

                            if attention_items:
                                # Build context about the attention items
                                items_context = "\n\n## System Attention Items (The tasks/checklist to work on):\n"
                                for item in attention_items[:10]:
                                    items_context += f"- [{item.section.upper()}] {item.title}\n"
                                    items_context += f"  Category: {item.category}, Priority: {item.priority}\n"
                                    if item.summary:
                                        items_context += f"  Summary: {item.summary[:150]}...\n"

                                enhanced_task = task + items_context
                                enhanced_context['system_attention_items'] = [
                                    {'section': i.section, 'title': i.title, 'category': i.category, 'priority': i.priority}
                                    for i in attention_items[:10]
                                ]
                                logger.info(f"[Session 574] Injected {len(attention_items)} system items into WorkflowAgent context")
                        except Exception as e:
                            logger.warning(f"Failed to inject system state for WorkflowAgent: {e}")

                    # Delegate to the agent
                    result = self.router.route(
                        agent_name=suggested_agent,
                        task=enhanced_task,
                        context=enhanced_context
                    )

                    tool_calls_made.append({
                        'tool': 'delegate_to_agent',
                        'agent': suggested_agent,
                        'task': task,
                        'result': result.to_dict()
                    })

                    self.mark_decision_outcome(
                        success=result.success,
                        result_summary=result.message[:100] if result.message else str(result.data)[:100]
                    )

                    execution_time = int((time.time() - start_time) * 1000)

                    # Session 401: Merge attribution from delegated agent if available
                    if result.knowledge_attribution:
                        attribution = KnowledgeAttribution(
                            spider_sources=list(set(attribution.spider_sources + result.knowledge_attribution.spider_sources)),
                            knowledge_items=attribution.knowledge_items + result.knowledge_attribution.knowledge_items,
                            confidence_score=(attribution.confidence_score + result.knowledge_attribution.confidence_score) / 2 if attribution.confidence_score else result.knowledge_attribution.confidence_score,
                            data_freshness_hours=min(attribution.data_freshness_hours, result.knowledge_attribution.data_freshness_hours) if attribution.data_freshness_hours else result.knowledge_attribution.data_freshness_hours,
                            total_sources=attribution.total_sources + result.knowledge_attribution.total_sources
                        )

                    final_result = AgentResult(
                        success=result.success,
                        message=result.message,
                        data={
                            'delegated_to': suggested_agent,
                            'agent_result': result.data,
                            'original_task': task
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made,
                        knowledge_attribution=attribution  # Session 401
                    )

                    # Record learning outcome for collective intelligence
                    try:
                        self._record_learning_outcome(
                            task=task,
                            result=final_result,
                            success=result.success,
                            context={
                                'agent_type': self.__class__.__name__,
                                'delegated_to': suggested_agent,
                                'execution_time_ms': execution_time,
                            }
                        )
                    except Exception as le:
                        logger.warning(f"Failed to record learning outcome: {le}")

                    return final_result

                else:
                    # Couldn't determine agent - use GPT to decide
                    # Session 454: Track GPT fallback routing
                    record_routing_decision(
                        task=task,
                        selected_agent='GPT_FALLBACK',
                        method='gpt',
                        confidence=0.5,
                        is_question=False,
                        alternatives=[]
                    )
                    return self._gpt_route(task, context, scifi_context, spider_context, start_time)

            except Exception as e:
                logger.error(f"PersonalAssistantAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _is_question(self, task: str) -> Tuple[bool, str]:
        """
        Determine if the task is a question (requiring direct answer) vs action request.

        Session 454: MAJOR FIX - Distinguish informational questions from action requests.
        - "What's trending in AI?" → Answer directly with spider data (informational)
        - "Research AI trends for my report" → Route to ResearchAgent (action request)

        Session 574: Added follow-up detection for "complete the tasks you suggested" patterns.

        Returns:
            Tuple of (is_question, question_type)
            - question_type can be: 'knowledge_question', 'trend_question', 'direct_question', 'followup_request', ''
        """
        task_lower = task.lower().strip()

        # Session 574: FOLLOW-UP detection - Split into INFORMATIONAL vs ACTION
        # INFORMATIONAL follow-ups = answer directly (explain the tasks)
        # ACTION follow-ups = route to agents (actually DO the tasks)

        # INFORMATIONAL patterns - user wants info about previous response
        info_followup_indicators = [
            'what were those', 'what are those', 'tell me more about',
            'explain those', 'describe those', 'which tasks',
            'what tasks', 'what items', 'list those',
        ]
        if any(indicator in task_lower for indicator in info_followup_indicators):
            logger.info(f"Detected INFO follow-up (answering directly): {task[:50]}")
            return True, 'followup_request'

        # ACTION follow-up patterns - these should route to WorkflowAgent!
        # We detect them here but return False so they go through _detect_agent()
        action_followup_indicators = [
            'complete the tasks', 'complete those tasks', 'complete all tasks',
            'complete the checklist', 'complete this checklist', 'complete that checklist',
            'do the tasks', 'do those tasks', 'do what you suggested',
            'work on those', 'work on the tasks', 'work on those items',
            'proceed with', 'go ahead and', 'yes do it', 'yes, do it',
            'address those', 'handle those', 'take care of those',
            'complete them', 'do them', 'finish them', 'execute',
            'you recommended', 'since you suggested', 'as you suggested',
            'lets use', "let's use", 'i choose', 'i pick', 'i select',
            # Session 574: Triage/planning patterns
            'triage these', 'triage the', 'triage those', 'triage ',
            'action plan', 'create a plan', 'draft a plan', 'make a plan',
            'prioritize these', 'prioritize those', 'prioritize the',
            'owners and timelines', 'assign owners', 'with owners',
            # Session 574: Draft/create for items patterns
            'draft the', 'create the', 'write the', 'prepare the',
            'for those items', 'for those research', 'for the items',
            'decision briefs', 'action items', 'those three', 'those five',
            'the three', 'the five', 'all three', 'all five',
        ]
        if any(indicator in task_lower for indicator in action_followup_indicators):
            # This is an ACTION request - let it flow to _detect_agent() for WorkflowAgent routing
            logger.info(f"Detected ACTION follow-up (routing to agents): {task[:50]}")
            return False, ''  # NOT a question - route to agents!

        # Session 454: Check for ACTION indicators first
        # If the user wants us to DO something, it's not a question
        action_indicators = [
            'create', 'make', 'generate', 'design', 'build', 'produce',
            'research for', 'research and', 'analyze for', 'prepare',
            'write a', 'draft a', 'compile', 'put together'
        ]
        has_action_intent = any(indicator in task_lower for indicator in action_indicators)

        # Session 454: Trend/news QUESTIONS can be answered directly
        # These use spider data but don't require agent routing
        trend_indicators = [
            'trending', 'trends', 'news', 'latest',
            'what\'s hot', "what's hot", 'whats hot', 'popular',
            'current events', 'happening', 'going on', 'hot in', 'hot right now'
        ]

        # Question starters that indicate informational intent
        question_starters = [
            'what is', 'what are', 'what does', 'what do', "what's",
            'how do', 'how does', 'how can', 'how should',
            'why is', 'why does', 'why do',
            'when is', 'when does', 'when do',
            'where is', 'where does', 'where do',
            'who is', 'who does', 'who can',
            'which is', 'which are',
            'can you explain', 'explain',
            'tell me about', 'describe',
            'is it', 'are there', 'do you', 'does it',
        ]

        is_question_format = (
            any(task_lower.startswith(starter) for starter in question_starters) or
            task_lower.endswith('?')
        )

        # Session 459: SEC/financial queries need to route to ResearchAgent FIRST
        # (before trend_question check, since "latest" is a trend indicator)
        sec_indicators = ['sec filing', 'sec filings', '10-k', '10k', '10-q', '10q', '8-k', '8k', 'edgar', 'company filing']
        if any(indicator in task_lower for indicator in sec_indicators):
            # SEC queries need to go to ResearchAgent to use the SEC spider
            logger.info(f"Routing SEC query to ResearchAgent: {task[:50]}")
            return False, ''

        # Session 454: INFORMATIONAL trend questions - answer directly with spider data
        # "What's trending in AI?" - question format + trend topic = answer directly
        # "Research AI trends for my report" - action intent = route to agent
        has_trend_topic = any(indicator in task_lower for indicator in trend_indicators)

        if has_trend_topic and is_question_format and not has_action_intent:
            # This is an informational question about trends
            # We'll answer directly using spider context (injected in _answer_question)
            logger.info(f"Detected trend question (answering directly): {task[:50]}")
            return True, 'trend_question'

        # Session 454: Market/business research REQUESTS should still go to agents
        # "What's the market for AI tools?" vs "Research the market for AI tools"
        business_action_indicators = [
            'research the market', 'analyze the market', 'competitor analysis',
            'market research', 'business research', 'industry analysis'
        ]
        if any(indicator in task_lower for indicator in business_action_indicators):
            # These are action requests, not questions
            return False, ''

        # Standard question detection
        for starter in question_starters:
            if task_lower.startswith(starter):
                return True, 'knowledge_question'

        # Check for question mark at end
        if task_lower.endswith('?'):
            # But exclude action questions like "can you create a logo?"
            if not has_action_intent:
                return True, 'direct_question'

        return False, ''

    def _detect_agent(self, task: str) -> Optional[str]:
        """
        Detect which agent should handle this task.

        Session 293: Uses a two-tier approach:
        1. Semantic routing (embeddings) - higher accuracy for natural language
        2. Keyword fallback - for cases where semantic routing fails or low confidence

        Session 454: Enhanced business context detection to suggest research workflows.

        Returns:
            Agent name or None if can't determine
        """
        task_lower = task.lower()

        # =========================================================================
        # TIER 0: Workflow patterns (highest priority - must check before semantic)
        # =========================================================================
        workflow_patterns = [
            'research and create', 'research then create',
            'brand identity package', 'brand package',
            'thumbnail package', 'complete package',
        ]
        for pattern in workflow_patterns:
            if pattern in task_lower:
                self._last_routing_method = 'workflow'  # Session 454: Track method
                return 'WorkflowAgent'

        # =========================================================================
        # Session 574: ACTION FOLLOW-UP patterns → WorkflowAgent
        # When user says "complete the checklist" or "do those tasks", route to
        # WorkflowAgent for orchestration of the action items
        # =========================================================================
        action_followup_patterns = [
            'complete the checklist', 'complete the tasks', 'complete those',
            'do the tasks', 'do those tasks', 'do what you suggested',
            'do what you recommended', 'do what you', 'do it',
            'proceed with', 'go ahead and do', 'execute the plan',
            'work on those', 'address those', 'handle those',
            'lets use', "let's use", 'i choose', 'i pick', 'i select',
            'activate', 'start the sprint', 'create the sprint',
            'set up the', 'configure the', 'implement the',
            # Session 574: Triage/planning patterns
            'triage these', 'triage the', 'triage those', 'triage ',
            'action plan', 'create a plan', 'draft a plan', 'make a plan',
            'prioritize these', 'prioritize those', 'prioritize the',
            'owners and timelines', 'assign owners', 'with owners',
            # Session 574: Draft/create for items patterns
            'draft the', 'create the', 'write the', 'prepare the',
            'for those items', 'for those research', 'for the items',
            'decision briefs', 'action items', 'those three', 'those five',
            'the three', 'the five', 'all three', 'all five',
        ]
        for pattern in action_followup_patterns:
            if pattern in task_lower:
                logger.info(f"[Session 574] Action follow-up detected: '{pattern}' -> WorkflowAgent")
                self._last_routing_method = 'action_followup'
                return 'WorkflowAgent'

        # =========================================================================
        # Session 496: TIER 0.5 - Writing patterns (BEFORE semantic routing!)
        # These patterns MUST be checked before semantic routing because
        # "Write a blog about AI trends" would otherwise match TrendAnalysisAgent
        # =========================================================================
        writing_patterns = [
            'write a blog', 'blog post', 'write blog', 'create a blog',
            'podcast script', 'write a podcast', 'podcast episode',
            'video script', 'write a video script', 'script for video',
            'write an article', 'create an article', 'write article',
            'newsletter', 'write a newsletter', 'create a newsletter',
            'social thread', 'write a thread', 'twitter thread',
            'turn into article', 'turn this into a blog', 'convert to blog',
            'write based on', 'write from research',
        ]
        for pattern in writing_patterns:
            if pattern in task_lower:
                self._last_routing_method = 'writing_pattern'  # Session 496: Track method
                logger.info(f"[Session 496] Writing pattern detected: '{pattern}' -> ContentWriterAgent")
                return 'ContentWriterAgent'

        # Check for multi-step patterns (research + creation = workflow)
        has_research = any(w in task_lower for w in ['research', 'analyze', 'find'])
        has_creation = any(w in task_lower for w in ['create', 'make', 'generate', 'design'])
        if has_research and has_creation:
            self._last_routing_method = 'workflow'  # Session 454: Track method
            return 'WorkflowAgent'

        # =========================================================================
        # Session 454: SMART BUSINESS CONTEXT DETECTION
        # =========================================================================
        # Detect when user has business context (startup, business, market)
        # AND wants to create something - suggest research-first workflow
        business_context_indicators = [
            'for my startup', 'for my business', 'for my company',
            'startup', 'business idea', 'new business', 'my company',
            'launching', 'going to market', 'go to market',
            'brand new', 'new venture', 'entrepreneur'
        ]
        has_business_context = any(indicator in task_lower for indicator in business_context_indicators)

        if has_business_context and has_creation:
            # Session 454: Business + creation = suggest research-first workflow
            # "Create a logo for my startup" → WorkflowAgent (research + create)
            # This ensures users get market-informed designs, not generic ones
            logger.info(f"Business context + creation detected: routing to WorkflowAgent for research-first approach")
            self.record_decision(
                decision_type="business_workflow_suggestion",
                action="Routing to WorkflowAgent for research-first approach",
                reasoning=f"Detected business context ({[i for i in business_context_indicators if i in task_lower]}) + creation intent",
                confidence=0.85
            )
            self._last_routing_method = 'business_context'  # Session 454: Track method
            return 'WorkflowAgent'

        # =========================================================================
        # TIER 1: Semantic Routing (embeddings-based)
        # =========================================================================
        semantic_router = get_semantic_router()
        if semantic_router:
            try:
                result = semantic_router.route_query(task)

                # Log semantic routing result
                logger.info(
                    f"Semantic routing: {result.agent_name} "
                    f"(confidence={result.confidence:.3f}, method={result.method})"
                )

                # High confidence semantic match - use it
                # But apply business research guard for creation intent
                SEMANTIC_CONFIDENCE_THRESHOLD = 0.45

                if result.confidence >= SEMANTIC_CONFIDENCE_THRESHOLD:
                    selected_agent = result.agent_name

                    # Session 293: Business Research agents ONLY when NO creation intent
                    # "Create a logo for my startup" should go to ImageAgent, not CompetitorAnalysisAgent
                    if has_creation and selected_agent in ('CompetitorAnalysisAgent', 'CustomerResearchAgent'):
                        # Fall through to keyword matching which handles this correctly
                        logger.info(f"Semantic chose {selected_agent} but creation intent detected, using keyword fallback")
                    else:
                        self.record_decision(
                            decision_type="semantic_routing",
                            action=f"Semantic routing selected {selected_agent}",
                            reasoning=f"Confidence: {result.confidence:.3f}, Top matches: {result.all_matches[:3]}",
                            confidence=result.confidence
                        )
                        self._last_routing_method = 'semantic'  # Session 454: Track method
                        return selected_agent

            except Exception as e:
                logger.warning(f"Semantic routing failed, using keyword fallback: {e}")

        # =========================================================================
        # TIER 2: Keyword Fallback
        # =========================================================================

        # Session 293: Business Research agents ONLY when NO creation intent
        # "Research AI market for my startup" -> CompetitorAnalysisAgent
        # "Create a logo for my startup" -> ImageAgent (has creation intent)
        if not has_creation:
            business_research_checks = [
                ('CompetitorAnalysisAgent', [
                    'for my startup', 'startup idea', 'business idea', 'market research',
                    'competitor analysis', 'competitive landscape', 'swot analysis',
                    'analyze competitors', 'research the market', 'market for my',
                    'research market', 'industry analysis'
                ]),
                ('CustomerResearchAgent', [
                    'customer personas', 'build personas', 'pain points', 'customer research',
                    'who are my customers', 'target audience', 'customer sentiment'
                ]),
            ]
            for agent, keywords in business_research_checks:
                for kw in keywords:
                    if kw in task_lower:
                        self._last_routing_method = 'keyword'  # Session 454: Track method
                        return agent

        # =========================================================================
        # Session 575: SPORTS & BETTING routing (LIVE DATA)
        # Route sports queries to SportsOddsAnalyst for real-time scores/odds
        # =========================================================================
        sports_patterns = [
            'nfl', 'nba', 'mlb', 'nhl', 'ncaa', 'ncaaf', 'ncaab',
            'football score', 'basketball score', 'baseball score', 'hockey score',
            'game score', 'final score', 'current score', 'live score',
            'sports odds', 'betting odds', 'spread', 'moneyline', 'over under',
            'who won', 'who is winning', 'playoff', 'super bowl', 'world series',
            'stanley cup', 'march madness', 'championship',
            'broncos', 'chiefs', 'bills', 'cowboys', 'eagles', 'packers', 'raiders',
            '49ers', 'rams', 'seahawks', 'vikings', 'bears', 'lions', 'giants',
            'lakers', 'celtics', 'warriors', 'nets', 'nuggets', 'bucks', 'heat',
            'yankees', 'dodgers', 'mets', 'braves', 'astros', 'phillies',
            'avalanche', 'lightning', 'panthers', 'oilers', 'rangers',
            'ufc', 'mma', 'boxing', 'premier league', 'la liga', 'champions league',
        ]
        for pattern in sports_patterns:
            if pattern in task_lower:
                logger.info(f"[Session 575] Sports pattern detected: '{pattern}' -> SportsOddsAnalyst")
                self._last_routing_method = 'sports_keyword'
                return 'SportsOddsAnalyst'

        # Priority keywords that override other matches
        # Ordered from most specific to least specific
        # These indicate strong intent for a specific agent
        priority_checks = [
            # Session 496: Content Writer Agent - HIGHEST PRIORITY for writing requests
            ('ContentWriterAgent', [
                'write a blog', 'blog post', 'write blog', 'create a blog',
                'podcast script', 'write a podcast', 'podcast episode',
                'video script', 'write a video script', 'script for video',
                'write an article', 'create an article', 'write article',
                'newsletter', 'write a newsletter', 'create a newsletter',
                'social thread', 'write a thread', 'twitter thread',
                'turn into article', 'turn this into a blog', 'convert to blog',
                'write based on this research', 'write from research',
            ]),
            # Session 403: Legal terms FIRST (before 'motion' triggers VideoAgent)
            ('LegalDocDrafterAgent', [
                'divorce', 'custody', 'child support', 'parenting time', 'court',
                'attorney', 'lawyer', 'legal', 'family law', 'pro se',
                'file motion', 'draft motion', 'motion to', 'jdf', 'parental responsibilities',
                'separation', 'decree', 'modification', 'enforcement',
                # Session 404: Added keywords for denied motion analysis
                'denied', 'denied motion', 'motion denied', 'rejected', 'dismissal',
                'rewrite', 'refile', 'magistrate', 'ruling', 'contempt', 'affidavit',
            ]),
            # Most specific compound terms first
            ('AudioAgent', ['voiceover', 'text to speech', 'tts', 'narration']),
            # Video editing terms (must check before generic 'video')
            ('VideoEditingAgent', ['trim video', 'cut video', 'edit video', 'slow motion', 'speed up video', 'trim', 'concatenate']),
            ('ImageEditingAgent', ['upscale', 'remove background', 'recolor', 'variations', 'edit image']),
            ('ThreeDAgent', ['3d', 'three-dimensional', 'convert to 3d']),
            # Then single keywords that are strong indicators
            ('AudioAgent', ['voice', 'speech', 'audio']),
            ('VideoAgent', ['animate', 'animation', 'video']),
        ]

        # Check priority keywords first (in order)
        for agent, keywords in priority_checks:
            for kw in keywords:
                if kw in task_lower:
                    self._last_routing_method = 'keyword'  # Session 454: Track method
                    return agent

        # Check each agent's keywords with scoring
        # Session 293: Exclude business research agents if there's creation intent
        business_research_agents = {'CompetitorAnalysisAgent', 'CustomerResearchAgent'}
        scores = {}
        for agent, keywords in INTENT_KEYWORDS.items():
            # Skip business research agents when user wants to CREATE something
            if has_creation and agent in business_research_agents:
                continue
            score = sum(1 for kw in keywords if kw in task_lower)
            if score > 0:
                scores[agent] = score

        if scores:
            # Session 454: Enhanced tie-breaking for keyword scoring
            # When multiple agents have same score, use these criteria:
            # 1. Agent priority from routing_config (higher = better)
            # 2. Creation agents preferred for creation requests
            # 3. Alphabetical as final fallback

            max_score = max(scores.values())
            tied_agents = [agent for agent, score in scores.items() if score == max_score]

            if len(tied_agents) == 1:
                selected_agent = tied_agents[0]
            else:
                # Tie-breaking needed
                logger.info(f"Tie between {tied_agents} (score={max_score}), applying tie-breakers")

                # Get priorities from routing config
                agent_priorities = {}
                for agent in tied_agents:
                    config = AGENT_ROUTING_CONFIG.get(agent, {})
                    agent_priorities[agent] = config.get('priority', 0)

                # Sort by: priority (desc), then prefer creation agents for creation, then alphabetical
                def tie_break_key(agent):
                    priority = agent_priorities.get(agent, 0)
                    # Boost creation agents if this is a creation request
                    creation_boost = 100 if has_creation and agent in ['ImageAgent', 'VideoAgent', 'AudioAgent', 'ThreeDAgent'] else 0
                    # Negative priority for descending sort (higher priority first)
                    return (-priority - creation_boost, agent)

                tied_agents.sort(key=tie_break_key)
                selected_agent = tied_agents[0]
                logger.info(f"Tie-breaker selected: {selected_agent}")

            self._last_routing_method = 'keyword'  # Session 454: Track method
            return selected_agent

        # Fallback: check for generic creation words
        if any(word in task_lower for word in ['create', 'make', 'generate', 'design']):
            # Default to ImageAgent for generic creation
            self._last_routing_method = 'keyword'  # Session 454: Track method
            return 'ImageAgent'

        self._last_routing_method = None  # Session 454: Track method
        return None

    def _check_ui_navigation(self, task: str) -> Optional[str]:
        """
        Session 414: Check if user is asking about UI navigation.

        Returns guidance string if matched, None otherwise.
        """
        task_lower = task.lower()

        for category, info in UI_NAVIGATION_GUIDE.items():
            for keyword in info['keywords']:
                if keyword in task_lower:
                    return info['guidance']

        return None

    def _answer_question(
        self,
        task: str,
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
        start_time: float,
        question_type: str = 'knowledge_question'
    ) -> AgentResult:
        """
        Answer a question directly using GPT.

        Session 401: Enhanced with knowledge attribution to show users
        what intelligence sources influenced the response.
        Session 414: Added UI navigation guidance for platform features.
        Session 454: Enhanced trend question handling with fresh spider data.
        """
        try:
            # Session 414: Check for UI navigation questions first
            # This provides instant, helpful guidance without GPT call
            ui_guidance = self._check_ui_navigation(task)
            if ui_guidance:
                return AgentResult(
                    success=True,
                    message=ui_guidance,
                    data={'type': 'ui_navigation', 'question': task},
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    decisions_made=1
                )

            # Session 454: For trend questions, fetch FRESH spider data
            # This ensures "What's trending in AI?" gets current intelligence
            enhanced_spider_context = spider_context.copy() if spider_context else {}

            if question_type == 'trend_question':
                try:
                    logger.info(f"🕷️ [Session 495] Fetching fresh trends for trend_question")
                    fresh_trends = self._fetch_fresh_trends_for_question(task)
                    if fresh_trends:
                        enhanced_spider_context['relevant_trends'] = fresh_trends.get('trends', [])
                        enhanced_spider_context['trend_articles'] = fresh_trends.get('articles', [])
                        # Session 495: Also pass through categories and cache info
                        enhanced_spider_context['categories'] = fresh_trends.get('categories', [])
                        enhanced_spider_context['topic'] = fresh_trends.get('topic_filter')
                        enhanced_spider_context['cache_hit'] = fresh_trends.get('cache_hit', False)
                        # Session 513: Track if web search fallback was used
                        enhanced_spider_context['used_web_search'] = fresh_trends.get('used_web_search', False)

                        logger.info(f"🕷️ [Session 495] SmartTrending injected: "
                                   f"topic='{fresh_trends.get('topic_filter')}', "
                                   f"categories={fresh_trends.get('categories', [])}, "
                                   f"{len(fresh_trends.get('trends', []))} keywords, "
                                   f"{len(fresh_trends.get('articles', []))} articles, "
                                   f"cache_hit={fresh_trends.get('cache_hit', False)}, "
                                   f"web_search={fresh_trends.get('used_web_search', False)}")

                        # Log sample for debugging
                        if fresh_trends.get('trends'):
                            logger.info(f"🕷️ [Session 495] Sample keywords: {fresh_trends['trends'][:5]}")
                        if fresh_trends.get('articles'):
                            logger.info(f"🕷️ [Session 495] Sample article: {fresh_trends['articles'][0].get('title', 'N/A')[:60]}")
                    else:
                        logger.warning(f"🕷️ [Session 495] _fetch_fresh_trends_for_question returned empty/None")
                except Exception as e:
                    logger.warning(f"Failed to fetch fresh trends: {e}")

            # Session 574: For follow-up requests, fetch system state and explain what can be done
            if question_type == 'followup_request':
                try:
                    logger.info(f"📋 [Session 574] Fetching system state for follow-up request")
                    from core.services.system_state_aggregator import get_system_state_aggregator
                    aggregator = get_system_state_aggregator()
                    attention_items = aggregator.get_attention_items()

                    if attention_items:
                        # Build context about the attention items
                        enhanced_spider_context['followup_context'] = True
                        enhanced_spider_context['attention_items'] = [
                            {
                                'section': item.section,
                                'category': item.category,
                                'title': item.title,
                                'summary': item.summary,
                                'priority': item.priority,
                                'action_url': item.action_url,
                            }
                            for item in attention_items[:10]
                        ]
                        logger.info(f"📋 [Session 574] Found {len(attention_items)} attention items for follow-up")
                    else:
                        logger.info(f"📋 [Session 574] No attention items found")
                except Exception as e:
                    logger.warning(f"Failed to fetch system state for follow-up: {e}")

            # Session 401: Build prompt with attribution to track what knowledge is used
            # Session 565: Now includes platform intelligence context
            intel_ctx = getattr(self, '_intelligence_context', None) or {}
            prompt, attribution = self._build_prompt_with_attribution(
                task, scifi_context, enhanced_spider_context, intel_ctx
            )

            # Session 454: Enhanced instruction for trend questions
            # Session 495: Now includes trending keywords + categories from SmartTrendingService
            logger.info(f"🕷️ [Session 495] trend_articles in context: {len(enhanced_spider_context.get('trend_articles', []))}")
            logger.info(f"🕷️ [Session 495] relevant_trends: {enhanced_spider_context.get('relevant_trends', [])[:5]}")

            if question_type == 'trend_question':
                # Session 513: Show data source (spider network vs web search)
                used_web_search = enhanced_spider_context.get('used_web_search', False)
                if used_web_search:
                    prompt += "\n\n## Data Source: Live Web Search (DuckDuckGo)"
                    prompt += "\nNote: Spider network didn't have data for this topic, using live web search."
                else:
                    # Session 495: Add matched categories info
                    categories = enhanced_spider_context.get('categories', [])
                    if categories:
                        prompt += f"\n\n## Data Sources: Spider Network ({', '.join(categories)})"

                # Session 495: Add trending keywords FIRST (gives GPT the key terms)
                trends = enhanced_spider_context.get('relevant_trends', [])
                if trends:
                    prompt += f"\n\n## Trending Keywords\n{', '.join(trends[:15])}"
                    logger.info(f"🕷️ [Session 495] Added {len(trends[:15])} trending keywords to prompt")

                # Then add articles
                articles = enhanced_spider_context.get('trend_articles', [])[:10]
                if articles:
                    prompt += "\n\n## Recent Articles for Context"
                    logger.info(f"🕷️ [Session 495] Adding {len(articles)} articles to prompt")
                    for article in articles:
                        title = article.get('title', '')[:80]
                        source = article.get('source', 'unknown')
                        url = article.get('url', '')
                        prompt += f"\n- [{source}] {title}"
                        if url:
                            prompt += f" ({url})"
                    logger.info(f"🕷️ [Session 495] First article added: {articles[0].get('title', 'N/A')[:60]}")

                # Session 483/513: Update attribution with data sources
                article_sources = list(set(
                    article.get('source', '') for article in articles if article.get('source')
                ))
                if article_sources:
                    # Session 513: Mark web search sources differently
                    if used_web_search:
                        # Prefix web search sources to distinguish them
                        all_sources = ['Web Search'] + article_sources[:9]
                    else:
                        # Merge with existing spider_sources
                        all_sources = list(set(attribution.spider_sources + article_sources))

                    attribution = KnowledgeAttribution(
                        spider_sources=all_sources[:10],  # Top 10 sources
                        knowledge_items=attribution.knowledge_items,
                        confidence_score=attribution.confidence_score,
                        data_freshness_hours=min(attribution.data_freshness_hours or 24.0, 0.5 if used_web_search else 1.0),  # Very fresh for web
                        total_sources=len(all_sources)
                    )
                    source_type = "web search" if used_web_search else "spider"
                    logger.info(f"🕷️ [Session 513] Updated attribution with {len(article_sources)} {source_type} sources: {article_sources[:5]}")

            # Session 574: Add attention items and instructions for follow-up requests
            if question_type == 'followup_request':
                attention_items = enhanced_spider_context.get('attention_items', [])
                if attention_items:
                    prompt += "\n\n## System Attention Items (These are the tasks from your previous response)"
                    prompt += "\nThe user wants to address these items. Explain which can be done automatically vs. need user action:\n"

                    for item in attention_items:
                        prompt += f"\n- [{item['section'].upper()}] {item['title']} (Priority: {item['priority']})"
                        prompt += f"\n  Category: {item['category']}"
                        if item.get('summary'):
                            prompt += f"\n  Summary: {item['summary'][:100]}..."
                        if item.get('action_url'):
                            prompt += f"\n  Action URL: {item['action_url']}"

                    prompt += "\n\n## How to Respond:"
                    prompt += "\n- For 'pending_decision' items: These are Boardroom decisions that NEED USER APPROVAL in the UI"
                    prompt += "\n- For 'overdue_task' items: I can potentially trigger content generation"
                    prompt += "\n- For 'stale_concern' or 'health_failure' items: Explain how to investigate"
                    prompt += "\n- Be specific about WHAT the user needs to do for each item"
                    prompt += "\n- Provide the action URLs where relevant"
                else:
                    prompt += "\n\n## No Active Attention Items"
                    prompt += "\nThere are currently no system items requiring attention. The system is running smoothly!"

            # Append instruction to answer directly
            prompt += "\n\nAnswer this question directly without delegating to an agent."
            if question_type == 'trend_question':
                # Session 513: Different instruction based on data source
                if enhanced_spider_context.get('used_web_search'):
                    prompt += " Use the live web search results provided above to give a current, relevant answer. "
                    prompt += "Cite specific articles and include URLs where relevant."
                else:
                    prompt += " Use the trend data and articles provided above to give a current, relevant answer."
            elif question_type == 'followup_request':
                prompt += " Explain what each attention item is and how the user can address it. Be specific about which items need manual approval vs. which can be automated."

            # Session 566: Increased max_completion_tokens from 1500 to 4000
            # GPT-5-mini uses tokens for reasoning before generating content.
            # With long system prompts, 1500 wasn't enough - model used all for reasoning.
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": task}
                ],
                max_completion_tokens=4000,
                reasoning_effort="medium",
            )

            answer = response.choices[0].message.content

            # Session 459: Handle empty GPT responses gracefully
            if not answer or not answer.strip():
                logger.warning(f"GPT returned empty response for question: {task[:50]}")
                answer = f"I don't have specific information about that topic right now. Try asking about trending topics in AI, tech, security, or financial news, or use the SEC spider directly for company filings."

            return AgentResult(
                success=True,
                message=answer,
                data={
                    'type': 'direct_answer',
                    'question': task,
                    'question_type': question_type  # Session 454
                },
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000),
                decisions_made=self._tt_decision_count,
                knowledge_attribution=attribution  # Session 401: Include attribution
            )

        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _fetch_fresh_trends_for_question(self, task: str) -> Dict[str, Any]:
        """
        Session 454: Fetch fresh spider trends for trend questions.
        Session 495: UPGRADED - Now uses SmartTrendingService for dynamic topic matching.

        Works for ANY topic without hardcoded if/elif chains!
        Examples:
            - "What's trending in startups?" -> Routes to startups, business spiders
            - "What's trending in AI?" -> Routes to ai_ml, tech spiders
            - "What's trending in healthcare?" -> Routes to healthtech spiders
            - "What's trending in crypto?" -> Routes to financial, blockchain spiders
        """
        try:
            from core.services.smart_trending_service import get_smart_trending_service

            service = get_smart_trending_service()

            # Session 495: Dynamic topic extraction and category mapping
            result = service.get_trending_for_query(
                query=task,
                hours=72,
                article_limit=15,
                use_cache=True
            )

            logger.info(f"🕷️ [Session 495] SmartTrending: topic='{result.get('topic')}', "
                       f"categories={result.get('categories')}, "
                       f"articles={len(result.get('articles', []))}, "
                       f"cache_hit={result.get('cache_hit', False)}")

            return {
                'trends': result.get('trends', []),
                'articles': result.get('articles', []),
                'topic_filter': result.get('topic'),  # For compatibility
                'categories': result.get('categories', []),  # New: matched categories
                'cache_hit': result.get('cache_hit', False)
            }

        except Exception as e:
            logger.warning(f"Error fetching fresh trends (falling back to legacy): {e}")
            # Fallback to legacy method if SmartTrendingService fails
            return self._fetch_fresh_trends_legacy(task)

    def _fetch_fresh_trends_legacy(self, task: str) -> Dict[str, Any]:
        """Legacy fallback method using SpiderIntelligenceService."""
        try:
            from core.services.spider_intelligence import SpiderIntelligenceService

            service = SpiderIntelligenceService()
            trends = service.get_trending_topics(hours=72, limit=10)
            tech_data = service.get_tech_trends(hours=72, limit=15, topic_filter=None)

            articles = []
            if isinstance(tech_data, dict):
                articles = tech_data.get('discussions', []) or tech_data.get('projects', [])
            elif isinstance(tech_data, list):
                articles = tech_data

            return {
                'trends': trends if isinstance(trends, list) else [],
                'articles': articles,
                'topic_filter': None
            }
        except Exception as e:
            logger.warning(f"Legacy trend fetch also failed: {e}")
            return {'trends': [], 'articles': [], 'topic_filter': None}

    def _gpt_route(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
        start_time: float
    ) -> AgentResult:
        """
        Use GPT to decide which agent to route to.

        Session 401: Enhanced with knowledge attribution.
        """
        try:
            # Session 401: Build prompt with attribution
            # Session 565: Include platform intelligence context
            intel_ctx = getattr(self, '_intelligence_context', None) or {}
            full_prompt, attribution = self._build_prompt_with_attribution(
                task, scifi_context, spider_context, intel_ctx
            )

            gpt_response = self._call_openai(full_prompt)

            if gpt_response.get('tool_calls'):
                # GPT decided to delegate
                for tool_call in gpt_response['tool_calls']:
                    if tool_call['name'] == 'delegate_to_agent':
                        agent_name = tool_call['arguments'].get('agent_name')
                        subtask = tool_call['arguments'].get('task', task)
                        subtask_context = tool_call['arguments'].get('context', context)

                        self.record_decision(
                            decision_type="gpt_routing",
                            action=f"GPT routed to {agent_name}",
                            reasoning=f"GPT analysis determined {agent_name} is best",
                            confidence=0.85
                        )

                        # Execute delegation
                        result = self.router.route(
                            agent_name=agent_name,
                            task=subtask,
                            context=subtask_context
                        )

                        # Session 401: Merge attribution from delegated agent if available
                        merged_attribution = attribution
                        if result.knowledge_attribution:
                            # Combine sources from both
                            merged_attribution = KnowledgeAttribution(
                                spider_sources=list(set(attribution.spider_sources + result.knowledge_attribution.spider_sources)),
                                knowledge_items=attribution.knowledge_items + result.knowledge_attribution.knowledge_items,
                                confidence_score=(attribution.confidence_score + result.knowledge_attribution.confidence_score) / 2,
                                data_freshness_hours=min(attribution.data_freshness_hours, result.knowledge_attribution.data_freshness_hours),
                                total_sources=attribution.total_sources + result.knowledge_attribution.total_sources
                            )

                        return AgentResult(
                            success=result.success,
                            message=result.message,
                            data={
                                'delegated_to': agent_name,
                                'agent_result': result.data,
                                'original_task': task
                            },
                            agent_name=self.name,
                            execution_time_ms=int((time.time() - start_time) * 1000),
                            decisions_made=self._tt_decision_count,
                            knowledge_attribution=merged_attribution  # Session 401
                        )

            # GPT responded without delegation
            return AgentResult(
                success=True,
                message=gpt_response.get('content', ''),
                data={'type': 'conversation'},
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000),
                knowledge_attribution=attribution  # Session 401
            )

        except Exception as e:
            logger.error(f"GPT routing failed: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute tool call - supports multiple PA tools."""

        # Session 575: Handle get_sports_data tool
        if tool_name == "get_sports_data":
            return self._get_sports_data(arguments)

        # Session 576: Handle system status tools
        if tool_name == "get_system_status":
            return self._get_system_status(arguments)

        if tool_name == "promote_boardroom_decision":
            return self._promote_boardroom_decision(arguments)

        if tool_name == "reject_boardroom_decision":
            return self._reject_boardroom_decision(arguments)

        if tool_name == "query_agent_data":
            return self._query_agent_data(arguments)

        if tool_name == "get_spider_intelligence":
            return self._get_spider_intelligence(arguments)

        # Session 577: Phase 2 Tools
        if tool_name == "execute_spider":
            return self._execute_spider(arguments)

        if tool_name == "create_content":
            return self._create_content(arguments)

        if tool_name == "manage_content_channel":
            return self._manage_content_channel(arguments)

        if tool_name == "query_prediction_markets":
            return self._query_prediction_markets(arguments)

        # Session 578: Phase 3 Tools
        if tool_name == "execute_workflow":
            return self._execute_workflow(arguments)

        if tool_name == "query_arbitrage":
            return self._query_arbitrage(arguments)

        if tool_name == "manage_bankroll":
            return self._manage_bankroll(arguments)

        if tool_name == "search_knowledge":
            return self._search_knowledge(arguments)

        # Session 579: Phase 4 Tools
        if tool_name == "create_boardroom_decision":
            return self._create_boardroom_decision(arguments)

        if tool_name == "query_dreams":
            return self._query_dreams(arguments)

        if tool_name == "manage_situations":
            return self._manage_situations(arguments)

        if tool_name == "query_conversations":
            return self._query_conversations(arguments)

        if tool_name == "delegate_to_agent":
            agent_name = arguments.get('agent_name')
            task = arguments.get('task', '')
            context = arguments.get('context', {})

            try:
                result = self.router.route(agent_name, task, context)
                return result.to_dict()
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }

        return {
            'success': False,
            'error': f"Unknown tool: {tool_name}"
        }

    def _get_sports_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 575: Query internal sports API for live scores and odds.
        This uses data already in the system - no external API calls needed.
        """
        import requests

        sport = arguments.get('sport', 'nfl')
        team_filter = arguments.get('team', '').lower()

        # Map short sport names to API keys
        sport_map = {
            'nfl': 'americanfootball_nfl',
            'nba': 'basketball_nba',
            'mlb': 'baseball_mlb',
            'nhl': 'icehockey_nhl',
            'ncaaf': 'americanfootball_ncaaf',
            'ncaab': 'basketball_ncaab',
            'soccer': 'soccer_epl',
            'ufc': 'mma_mixed_martial_arts',
        }
        sport_key = sport_map.get(sport.lower(), 'americanfootball_nfl')

        try:
            # Call internal API
            response = requests.get(
                f'http://localhost:8000/api/v1/sports/live-odds-scores/',
                params={'sport': sport_key},
                timeout=10
            )

            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Sports API returned {response.status_code}'
                }

            data = response.json()

            # Format games for easy reading
            games = []
            for game in data.get('odds', []):
                home = game.get('home_team', '')
                away = game.get('away_team', '')
                live = game.get('live', {})

                # Filter by team if specified
                if team_filter and team_filter not in home.lower() and team_filter not in away.lower():
                    continue

                game_info = {
                    'matchup': f"{away} @ {home}",
                    'home_team': home,
                    'away_team': away,
                    'home_score': live.get('home_score', 0),
                    'away_score': live.get('away_score', 0),
                    'status': live.get('status_detail', 'Scheduled'),
                    'is_live': live.get('is_live', False),
                    'is_final': live.get('is_final', False),
                }

                # Add simple score string
                if live.get('is_live') or live.get('is_final'):
                    game_info['score'] = f"{away} {live.get('away_score', 0)}, {home} {live.get('home_score', 0)}"
                else:
                    game_info['score'] = 'Not started'

                games.append(game_info)

            # Build summary
            live_games = [g for g in games if g['is_live']]
            final_games = [g for g in games if g['is_final']]
            upcoming_games = [g for g in games if not g['is_live'] and not g['is_final']]

            return {
                'success': True,
                'sport': sport.upper(),
                'total_games': len(games),
                'live_count': len(live_games),
                'final_count': len(final_games),
                'upcoming_count': len(upcoming_games),
                'games': games,
                'summary': self._format_scores_summary(games, sport)
            }

        except Exception as e:
            logger.error(f"Error fetching sports data: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _format_scores_summary(self, games: list, sport: str) -> str:
        """Format games into a readable summary."""
        lines = [f"**{sport.upper()} Scores:**\n"]

        live = [g for g in games if g['is_live']]
        final = [g for g in games if g['is_final']]
        upcoming = [g for g in games if not g['is_live'] and not g['is_final']]

        if live:
            lines.append("🔴 **LIVE:**")
            for g in live:
                lines.append(f"  {g['away_team']} {g['away_score']} @ {g['home_team']} {g['home_score']} ({g['status']})")

        if final:
            lines.append("\n✅ **FINAL:**")
            for g in final[:5]:  # Limit to 5
                winner = g['away_team'] if g['away_score'] > g['home_score'] else g['home_team']
                lines.append(f"  {g['away_team']} {g['away_score']} @ {g['home_team']} {g['home_score']} - {winner} wins")

        if upcoming and not live and not final:
            lines.append("\n📅 **UPCOMING:**")
            for g in upcoming[:5]:
                lines.append(f"  {g['matchup']} - {g['status']}")

        return '\n'.join(lines)

    # =========================================================================
    # Session 576: System Status & Intelligence Tools
    # =========================================================================

    def _get_system_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 576: Query SystemStateAggregator for attention items.
        Returns pending decisions, failed cycles, stale concerns, etc.
        """
        try:
            from core.services.system_state_aggregator import SystemStateAggregator

            category = arguments.get('category', 'all')
            max_items = arguments.get('max_items', 10)

            aggregator = SystemStateAggregator()
            items = aggregator.get_attention_items(max_per_section=max_items)

            # Convert to dicts for JSON serialization
            items_data = [item.to_dict() for item in items]

            # Filter by category if specified
            if category != 'all':
                category_map = {
                    'decisions': ['decision', 'boardroom'],
                    'health': ['health', 'alert', 'failed'],
                    'content': ['overdue', 'channel', 'content'],
                    'urgent': None  # Special case - filter by priority
                }

                if category == 'urgent':
                    items_data = [i for i in items_data if i.get('priority', 0) >= 80]
                elif category in category_map:
                    keywords = category_map[category]
                    items_data = [i for i in items_data
                                  if any(kw in i.get('category', '').lower() for kw in keywords)]

            # Build summary
            summary_lines = ["**System Status:**\n"]

            if not items_data:
                summary_lines.append("✅ No items need immediate attention.")
            else:
                # Group by section
                by_section = {}
                for item in items_data[:max_items]:
                    section = item.get('section', 'other')
                    if section not in by_section:
                        by_section[section] = []
                    by_section[section].append(item)

                section_icons = {
                    'command_center': '🎯',
                    'autonomous': '🤖',
                    'research': '🔬',
                    'boardroom': '🏛️'
                }

                for section, section_items in by_section.items():
                    icon = section_icons.get(section, '📋')
                    summary_lines.append(f"\n{icon} **{section.replace('_', ' ').title()}:**")
                    for item in section_items[:5]:
                        priority_icon = '🔴' if item.get('priority', 0) >= 80 else '🟡' if item.get('priority', 0) >= 60 else '🟢'
                        summary_lines.append(f"  {priority_icon} {item.get('title', 'Unknown')}")
                        if item.get('id'):
                            summary_lines.append(f"     ID: {item.get('id')}")

            return {
                'success': True,
                'total_items': len(items_data),
                'urgent_count': len([i for i in items_data if i.get('priority', 0) >= 80]),
                'items': items_data[:max_items],
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _promote_boardroom_decision(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 576: Approve a pending boardroom decision.
        Wraps /api/boardroom/decisions/{id}/promote/
        """
        import requests

        decision_id = arguments.get('decision_id')

        if not decision_id:
            return {
                'success': False,
                'error': 'decision_id is required'
            }

        try:
            # Call internal API
            response = requests.post(
                f'http://localhost:8000/api/boardroom/decisions/{decision_id}/promote/',
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'message': data.get('message', f'Decision {decision_id} approved'),
                    'decision_id': decision_id
                }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': f'Decision {decision_id} not found'
                }
            else:
                return {
                    'success': False,
                    'error': f'API returned {response.status_code}: {response.text}'
                }

        except Exception as e:
            logger.error(f"Error promoting decision: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _reject_boardroom_decision(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 576: Reject a pending boardroom decision.
        Wraps /api/boardroom/decisions/{id}/reject/
        """
        import requests

        decision_id = arguments.get('decision_id')
        reason = arguments.get('reason', '')

        if not decision_id:
            return {
                'success': False,
                'error': 'decision_id is required'
            }

        if not reason:
            return {
                'success': False,
                'error': 'reason is required for rejection'
            }

        try:
            # Call internal API
            response = requests.post(
                f'http://localhost:8000/api/boardroom/decisions/{decision_id}/reject/',
                json={'reason': reason},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'message': data.get('message', f'Decision {decision_id} rejected'),
                    'decision_id': decision_id,
                    'reason': reason
                }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': f'Decision {decision_id} not found'
                }
            else:
                return {
                    'success': False,
                    'error': f'API returned {response.status_code}: {response.text}'
                }

        except Exception as e:
            logger.error(f"Error rejecting decision: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _query_agent_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 576: Query agent activity, learning, and performance data.
        """
        try:
            from core.models_unified_system import Agent
            from django.db.models import Count, Sum
            from django.utils import timezone
            from datetime import timedelta

            agent_name = arguments.get('agent_name')
            metric_type = arguments.get('metric_type', 'all')
            limit = arguments.get('limit', 10)

            # Build query
            agents = Agent.objects.all()

            if agent_name:
                agents = agents.filter(name__icontains=agent_name)

            # Get agent stats
            agents_data = []
            for agent in agents[:limit]:
                agent_info = {
                    'name': agent.name,
                    'level': getattr(agent, 'level', 1),
                    'xp': getattr(agent, 'xp', 0),
                    'is_active': getattr(agent, 'is_active', True),
                }

                # Add learning stats if requested
                if metric_type in ['learning', 'all']:
                    agent_info['skills'] = list(getattr(agent, 'skills', []) or [])[:5]
                    agent_info['specialties'] = list(getattr(agent, 'specialties', []) or [])[:5]

                # Add activity stats if requested
                if metric_type in ['activity', 'all']:
                    # Try to get execution count
                    try:
                        from core.models_unified_system import AgentExecution
                        recent = timezone.now() - timedelta(hours=24)
                        exec_count = AgentExecution.objects.filter(
                            agent_name=agent.name,
                            created_at__gte=recent
                        ).count()
                        agent_info['executions_24h'] = exec_count
                    except Exception:
                        agent_info['executions_24h'] = 0

                agents_data.append(agent_info)

            # Sort by XP or activity
            if metric_type == 'learning':
                agents_data.sort(key=lambda x: x.get('xp', 0), reverse=True)
            elif metric_type == 'activity':
                agents_data.sort(key=lambda x: x.get('executions_24h', 0), reverse=True)

            # Build summary
            summary_lines = ["**Agent Status:**\n"]

            if not agents_data:
                summary_lines.append("No agents found matching criteria.")
            else:
                for agent in agents_data[:10]:
                    level = agent.get('level', 1)
                    xp = agent.get('xp', 0)
                    execs = agent.get('executions_24h', 0)
                    status = '🟢' if agent.get('is_active') else '🔴'
                    summary_lines.append(f"{status} **{agent['name']}** - Level {level} ({xp} XP)")
                    if execs > 0:
                        summary_lines.append(f"   📊 {execs} executions in last 24h")

            return {
                'success': True,
                'total_agents': len(agents_data),
                'agents': agents_data,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error querying agent data: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_spider_intelligence(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 576: Query spider network for trending topics and fresh data.
        """
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Count

            category = arguments.get('category', 'all')
            hours = arguments.get('hours', 24)
            limit = arguments.get('limit', 10)

            # Time filter
            since = timezone.now() - timedelta(hours=hours)

            # Build query
            query = SpiderData.objects.filter(created_at__gte=since)

            # Category mapping
            category_map = {
                'tech': ['hackernews', 'techcrunch', 'devto', 'github', 'producthunt'],
                'finance': ['coingecko', 'yahoo_finance', 'polygon_finance', 'kalshi'],
                'sports': ['theodds', 'espn'],
                'news': ['cnn', 'bbc', 'npr', 'reuters', 'axios'],
                'legal': ['courtlistener', 'findlaw', 'colorado_family_law'],
                'entertainment': ['variety', 'polygon_gaming', 'spotify']
            }

            if category != 'all' and category in category_map:
                spiders = category_map[category]
                query = query.filter(spider_name__in=spiders)

            # Get spider stats
            spider_stats = query.values('spider_name').annotate(
                count=Count('id')
            ).order_by('-count')[:limit]

            # Get recent items
            recent_items = query.order_by('-created_at')[:limit]

            items_data = []
            for item in recent_items:
                items_data.append({
                    'spider': item.spider_name,
                    'title': getattr(item, 'title', '')[:100] if hasattr(item, 'title') else '',
                    'category': getattr(item, 'category', 'general'),
                    'collected_at': item.created_at.isoformat() if item.created_at else None
                })

            # Build summary
            summary_lines = [f"**Spider Intelligence ({hours}h):**\n"]

            if not spider_stats:
                summary_lines.append("No recent spider data found.")
            else:
                summary_lines.append("📊 **Data by Spider:**")
                for stat in spider_stats[:10]:
                    summary_lines.append(f"  • {stat['spider_name']}: {stat['count']} items")

                if items_data:
                    summary_lines.append("\n📰 **Recent Items:**")
                    for item in items_data[:5]:
                        title = item.get('title', 'Untitled')[:50]
                        spider = item.get('spider', 'unknown')
                        summary_lines.append(f"  • [{spider}] {title}...")

            total_items = query.count()

            return {
                'success': True,
                'category': category,
                'hours': hours,
                'total_items': total_items,
                'spider_stats': list(spider_stats),
                'recent_items': items_data,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error getting spider intelligence: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # Session 577: Phase 2 Tool Handlers
    # =========================================================================

    def _execute_spider(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 577: Run a specific spider on demand to fetch fresh data.
        """
        try:
            from ai_core.spiders.spider_registry import SpiderRegistry
            import asyncio
            import inspect

            spider_name = arguments.get('spider_name')
            category = arguments.get('category')
            max_results = arguments.get('max_results', 20)

            registry = SpiderRegistry()

            # Category to spider mapping
            category_spiders = {
                'tech': ['hackernews', 'techcrunch', 'devto', 'github', 'producthunt'],
                'finance': ['coingecko', 'yahoo_finance', 'polygon_finance', 'finnhub'],
                'news': ['cnn', 'bbc', 'npr', 'reuters_rss', 'axios'],
                'legal': ['courtlistener', 'findlaw', 'colorado_family_law'],
                'entertainment': ['variety', 'polygon_gaming', 'spotify'],
                'jobs': ['remoteok', 'weworkremotely', 'adzuna'],
                'crypto': ['coingecko', 'etherscan_api']
            }

            # Determine which spiders to run
            if spider_name:
                spiders_to_run = [spider_name]
            elif category and category in category_spiders:
                spiders_to_run = category_spiders[category]
            else:
                return {
                    'success': False,
                    'error': 'Please provide either spider_name or category'
                }

            results = []
            errors = []

            for name in spiders_to_run:
                spider_class = registry.get_spider_class(name)
                if not spider_class or spider_class.__name__ == 'BaseIntelligenceSpider':
                    errors.append(f"Spider '{name}' not found")
                    continue

                try:
                    spider = spider_class()

                    # Run fetch_data
                    if hasattr(spider, 'fetch_data'):
                        fetch_method = spider.fetch_data

                        if asyncio.iscoroutinefunction(fetch_method):
                            # Async spider
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                data = loop.run_until_complete(fetch_method(max_results=max_results))
                            finally:
                                loop.close()
                        else:
                            # Sync spider
                            data = fetch_method(max_results=max_results)

                        if data:
                            item_count = len(data) if isinstance(data, list) else 1
                            results.append({
                                'spider': name,
                                'items_fetched': item_count,
                                'sample': data[:3] if isinstance(data, list) else data
                            })
                    else:
                        errors.append(f"Spider '{name}' has no fetch_data method")

                except Exception as e:
                    errors.append(f"Spider '{name}' error: {str(e)[:100]}")

            # Build summary
            total_items = sum(r['items_fetched'] for r in results)
            summary_lines = [f"**Spider Execution Results:**\n"]

            if results:
                summary_lines.append(f"✅ Fetched {total_items} items from {len(results)} spiders:")
                for r in results:
                    summary_lines.append(f"  • {r['spider']}: {r['items_fetched']} items")
            else:
                summary_lines.append("❌ No data fetched")

            if errors:
                summary_lines.append(f"\n⚠️ Errors ({len(errors)}):")
                for e in errors[:3]:
                    summary_lines.append(f"  • {e}")

            return {
                'success': len(results) > 0,
                'spiders_run': len(spiders_to_run),
                'successful': len(results),
                'total_items': total_items,
                'results': results,
                'errors': errors,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error executing spider: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _create_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 577: Trigger content creation by routing to appropriate agent.
        """
        try:
            content_type = arguments.get('content_type', 'image')
            prompt = arguments.get('prompt', '')
            style = arguments.get('style', '')

            if not prompt:
                return {
                    'success': False,
                    'error': 'Please provide a prompt describing what to create'
                }

            # Map content type to agent
            agent_map = {
                'image': 'ImageAgent',
                'video': 'VideoAgent',
                'blog_post': 'ContentWriterAgent',
                'social_post': 'SocialMediaAgent',
                'logo': 'BrandIdentityAgent'
            }

            agent_name = agent_map.get(content_type)
            if not agent_name:
                return {
                    'success': False,
                    'error': f"Unknown content type: {content_type}"
                }

            # Build task with style if provided
            task = prompt
            if style:
                task = f"{prompt} (Style: {style})"

            # Route to agent
            try:
                result = self.router.route(agent_name, task, {
                    'content_type': content_type,
                    'style': style,
                    'prompt': prompt
                })

                return {
                    'success': True,
                    'agent': agent_name,
                    'content_type': content_type,
                    'result': result.to_dict() if hasattr(result, 'to_dict') else str(result),
                    'summary': f"**Content Creation Started:**\n\n🎨 Agent: {agent_name}\n📝 Type: {content_type}\n💭 Prompt: {prompt[:100]}..."
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Agent routing failed: {str(e)}"
                }

        except Exception as e:
            logger.error(f"Error creating content: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _manage_content_channel(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 577: Control autonomous content channels.
        """
        try:
            from core.models_autonomous_studio import ContentChannel, ChannelStatus

            action = arguments.get('action', 'list')
            channel_id = arguments.get('channel_id')

            if action == 'list':
                # List all channels
                channels = ContentChannel.objects.all().order_by('-created_at')[:20]

                if not channels:
                    return {
                        'success': True,
                        'channels': [],
                        'summary': "**Content Channels:**\n\nNo content channels configured yet."
                    }

                channel_data = []
                summary_lines = ["**Content Channels:**\n"]

                for ch in channels:
                    status_emoji = {
                        'active': '🟢',
                        'paused': '⏸️',
                        'completed': '✅',
                        'failed': '❌'
                    }.get(ch.status, '❓')

                    channel_data.append({
                        'id': ch.id,
                        'name': ch.name,
                        'status': ch.status,
                        'platform': ch.platform,
                        'frequency': ch.frequency,
                        'episodes_count': ch.episodes.count() if hasattr(ch, 'episodes') else 0
                    })

                    summary_lines.append(f"{status_emoji} **{ch.name}** (ID: {ch.id})")
                    summary_lines.append(f"   Platform: {ch.platform} | Frequency: {ch.frequency}")

                return {
                    'success': True,
                    'channels': channel_data,
                    'total': len(channel_data),
                    'summary': '\n'.join(summary_lines)
                }

            elif action == 'status':
                if not channel_id:
                    return {'success': False, 'error': 'channel_id required for status'}

                channel = ContentChannel.objects.filter(id=channel_id).first()
                if not channel:
                    return {'success': False, 'error': f'Channel {channel_id} not found'}

                return {
                    'success': True,
                    'channel': {
                        'id': channel.id,
                        'name': channel.name,
                        'status': channel.status,
                        'platform': channel.platform,
                        'frequency': channel.frequency,
                        'created_at': channel.created_at.isoformat(),
                        'last_run': channel.last_run.isoformat() if channel.last_run else None,
                        'next_run': channel.next_run.isoformat() if channel.next_run else None
                    },
                    'summary': f"**Channel: {channel.name}**\n\nStatus: {channel.status}\nPlatform: {channel.platform}\nFrequency: {channel.frequency}"
                }

            elif action == 'pause':
                if not channel_id:
                    return {'success': False, 'error': 'channel_id required for pause'}

                channel = ContentChannel.objects.filter(id=channel_id).first()
                if not channel:
                    return {'success': False, 'error': f'Channel {channel_id} not found'}

                channel.status = ChannelStatus.PAUSED
                channel.save()

                return {
                    'success': True,
                    'channel_id': channel_id,
                    'name': channel.name,
                    'new_status': 'paused',
                    'summary': f"⏸️ **Channel Paused:**\n\n{channel.name} has been paused."
                }

            elif action == 'resume':
                if not channel_id:
                    return {'success': False, 'error': 'channel_id required for resume'}

                channel = ContentChannel.objects.filter(id=channel_id).first()
                if not channel:
                    return {'success': False, 'error': f'Channel {channel_id} not found'}

                channel.status = ChannelStatus.ACTIVE
                channel.save()

                return {
                    'success': True,
                    'channel_id': channel_id,
                    'name': channel.name,
                    'new_status': 'active',
                    'summary': f"▶️ **Channel Resumed:**\n\n{channel.name} is now active."
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing content channel: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _query_prediction_markets(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 577: Query Kalshi prediction market data.
        """
        try:
            from ai_core.spiders.specialized.kalshi_spider import KalshiSpider

            query = arguments.get('query', '').lower()
            category = arguments.get('category', 'all')
            limit = arguments.get('limit', 10)

            # Fetch markets from Kalshi spider
            spider = KalshiSpider()
            markets = spider.fetch_data(max_results=100)

            # Filter to actual markets (not metadata)
            prediction_markets = [
                m for m in markets
                if m.get('data_type') == 'prediction_market'
            ]

            # Apply filters
            if query:
                prediction_markets = [
                    m for m in prediction_markets
                    if query in m.get('title', '').lower() or query in m.get('subtitle', '').lower()
                ]

            # Category filtering (Kalshi uses category field)
            category_keywords = {
                'politics': ['election', 'president', 'congress', 'senate', 'trump', 'biden'],
                'economics': ['fed', 'rate', 'inflation', 'gdp', 'recession', 'unemployment'],
                'climate': ['temperature', 'weather', 'climate', 'hurricane'],
                'tech': ['ai', 'tech', 'apple', 'google', 'tesla'],
                'sports': ['nfl', 'nba', 'mlb', 'super bowl']
            }

            if category != 'all' and category in category_keywords:
                keywords = category_keywords[category]
                prediction_markets = [
                    m for m in prediction_markets
                    if any(kw in m.get('title', '').lower() for kw in keywords)
                ]

            # Sort by volume (most active markets first)
            prediction_markets.sort(key=lambda m: -(m.get('volume') or 0))

            # Limit results
            prediction_markets = prediction_markets[:limit]

            # Build summary
            summary_lines = [f"**Prediction Markets:**\n"]

            if not prediction_markets:
                summary_lines.append("No markets found matching your query.")
            else:
                for m in prediction_markets[:10]:
                    title = m.get('title', 'Unknown')[:50]
                    yes_prob = m.get('yes_price', 0)
                    volume = m.get('volume', 0)
                    volume_str = f"${volume:,.0f}" if volume else "N/A"

                    # Format probability nicely
                    prob_str = f"{yes_prob:.0%}" if yes_prob else "N/A"

                    summary_lines.append(f"📊 **{title}...**")
                    summary_lines.append(f"   Yes: {prob_str} | Volume: {volume_str}")
                    summary_lines.append("")

            return {
                'success': True,
                'markets': prediction_markets,
                'total_found': len(prediction_markets),
                'query': query,
                'category': category,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error querying prediction markets: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # Session 578: Phase 3 Tool Handlers
    # =========================================================================

    def _execute_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 578: Execute a multi-step workflow using WorkflowAgent.
        """
        try:
            from core.agents.workflow_agent import WorkflowAgent

            workflow_description = arguments.get('workflow_description', '')
            workflow_type = arguments.get('workflow_type', 'custom')

            if not workflow_description:
                return {
                    'success': False,
                    'error': 'Please provide a workflow_description'
                }

            # Create workflow agent and execute
            workflow_agent = WorkflowAgent(user=self.user)

            # Build context
            context = {
                'workflow_type': workflow_type,
                'requested_by': 'PersonalAssistant'
            }

            # Execute workflow
            result = workflow_agent.execute(
                task=workflow_description,
                context=context,
                scifi_context={},
                spider_context={}
            )

            # Build summary
            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                result_dict = {'output': str(result)}

            return {
                'success': True,
                'workflow_type': workflow_type,
                'description': workflow_description,
                'result': result_dict,
                'summary': f"**Workflow Executed:**\n\n🔄 Type: {workflow_type}\n📝 Task: {workflow_description[:100]}...\n\n{result_dict.get('content', result_dict.get('output', 'Completed'))[:500]}"
            }

        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _query_arbitrage(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 578: Find sports betting arbitrage opportunities.
        """
        try:
            from core.agents.markets.arbitrage_detector import ArbitrageDetector

            sport = arguments.get('sport', 'all')
            min_profit = arguments.get('min_profit', 0.5)
            limit = arguments.get('limit', 10)

            # Use ArbitrageDetector agent
            detector = ArbitrageDetector()

            # Execute detection
            result = detector.execute(
                task=f"Find arbitrage opportunities for {sport} with minimum {min_profit}% profit",
                context={'sport': sport, 'min_profit': min_profit, 'limit': limit},
                scifi_context={},
                spider_context={}
            )

            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                result_dict = {'output': str(result)}

            # Extract opportunities from result
            opportunities = result_dict.get('opportunities', [])
            content = result_dict.get('content', '')

            # Build summary
            summary_lines = ["**Arbitrage Opportunities:**\n"]

            if not opportunities and not content:
                summary_lines.append("No arbitrage opportunities found at this time.")
                summary_lines.append("\nArbitrage opportunities are rare - they occur when odds")
                summary_lines.append("across bookmakers create guaranteed profit situations.")
            else:
                if opportunities:
                    for opp in opportunities[:limit]:
                        profit = opp.get('profit_percentage', 0)
                        event = opp.get('event', 'Unknown event')
                        summary_lines.append(f"💰 **{profit:.2f}% profit** - {event[:50]}")
                elif content:
                    summary_lines.append(content[:500])

            return {
                'success': True,
                'sport': sport,
                'min_profit': min_profit,
                'opportunities': opportunities[:limit],
                'raw_result': result_dict,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error querying arbitrage: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _manage_bankroll(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 578: Query and manage betting bankroll.
        """
        try:
            from core.models_bankroll import Bankroll, Wager

            action = arguments.get('action', 'status')
            limit = arguments.get('limit', 10)

            # Try to get user's bankroll
            bankroll = None
            if self.user:
                bankroll = Bankroll.objects.filter(user=self.user).first()

            if not bankroll:
                # Return demo/sample data if no bankroll exists
                return {
                    'success': True,
                    'has_bankroll': False,
                    'summary': "**Bankroll Status:**\n\nNo bankroll configured yet.\n\nTo set up your bankroll, visit the Betting Dashboard in AI Studio."
                }

            if action == 'status':
                summary_lines = ["**Bankroll Status:**\n"]
                summary_lines.append(f"💰 **Balance:** ${bankroll.current_balance:,.2f}")
                summary_lines.append(f"📈 **Initial:** ${bankroll.initial_balance:,.2f}")
                summary_lines.append(f"📊 **P/L:** ${bankroll.profit_loss:+,.2f}")
                summary_lines.append(f"🎯 **Win Rate:** {bankroll.win_rate:.1f}%")
                summary_lines.append(f"📉 **ROI:** {bankroll.roi:.1f}%")
                summary_lines.append(f"\n**Record:** {bankroll.total_won}W - {bankroll.total_lost}L - {bankroll.total_pushed}P")
                summary_lines.append(f"**Pending:** {bankroll.total_pending} wagers")

                return {
                    'success': True,
                    'has_bankroll': True,
                    'bankroll': {
                        'current_balance': float(bankroll.current_balance),
                        'initial_balance': float(bankroll.initial_balance),
                        'profit_loss': float(bankroll.profit_loss),
                        'win_rate': float(bankroll.win_rate),
                        'roi': float(bankroll.roi),
                        'total_won': bankroll.total_won,
                        'total_lost': bankroll.total_lost,
                        'total_pending': bankroll.total_pending
                    },
                    'summary': '\n'.join(summary_lines)
                }

            elif action == 'history':
                wagers = Wager.objects.filter(bankroll=bankroll).order_by('-created_at')[:limit]

                summary_lines = ["**Recent Wagers:**\n"]
                wager_data = []

                for w in wagers:
                    status_emoji = {
                        'pending': '⏳',
                        'won': '✅',
                        'lost': '❌',
                        'pushed': '➖'
                    }.get(w.status, '❓')

                    wager_data.append({
                        'id': w.id,
                        'event': w.event_description,
                        'amount': float(w.amount),
                        'odds': float(w.odds),
                        'status': w.status,
                        'profit': float(w.profit) if w.profit else 0
                    })

                    summary_lines.append(f"{status_emoji} ${w.amount:.2f} @ {w.odds:+.0f} - {w.event_description[:40]}...")

                return {
                    'success': True,
                    'has_bankroll': True,
                    'wagers': wager_data,
                    'total': len(wager_data),
                    'summary': '\n'.join(summary_lines)
                }

            elif action == 'pending':
                pending = Wager.objects.filter(bankroll=bankroll, status='pending').order_by('-created_at')

                summary_lines = ["**Pending Wagers:**\n"]
                pending_data = []

                for w in pending:
                    pending_data.append({
                        'id': w.id,
                        'event': w.event_description,
                        'amount': float(w.amount),
                        'odds': float(w.odds),
                        'potential_profit': float(w.potential_profit)
                    })
                    summary_lines.append(f"⏳ ${w.amount:.2f} @ {w.odds:+.0f} - {w.event_description[:40]}...")

                if not pending_data:
                    summary_lines.append("No pending wagers.")

                return {
                    'success': True,
                    'has_bankroll': True,
                    'pending_wagers': pending_data,
                    'total': len(pending_data),
                    'summary': '\n'.join(summary_lines)
                }

            elif action == 'stats':
                summary_lines = ["**Betting Statistics:**\n"]
                summary_lines.append(f"📊 **Total Wagers:** {bankroll.total_wagers}")
                summary_lines.append(f"💵 **Total Wagered:** ${bankroll.total_wagered:,.2f}")
                summary_lines.append(f"💰 **Total Profit:** ${bankroll.total_profit:+,.2f}")
                summary_lines.append(f"\n🔥 **Current Streak:** {bankroll.current_streak:+d}")
                summary_lines.append(f"📈 **Best Streak:** {bankroll.best_streak}")
                summary_lines.append(f"📉 **Worst Streak:** {bankroll.worst_streak}")
                summary_lines.append(f"\n🏆 **Highest Balance:** ${bankroll.highest_balance:,.2f}")
                summary_lines.append(f"📉 **Lowest Balance:** ${bankroll.lowest_balance:,.2f}")

                return {
                    'success': True,
                    'has_bankroll': True,
                    'stats': {
                        'total_wagers': bankroll.total_wagers,
                        'total_wagered': float(bankroll.total_wagered),
                        'total_profit': float(bankroll.total_profit),
                        'current_streak': bankroll.current_streak,
                        'best_streak': bankroll.best_streak,
                        'worst_streak': bankroll.worst_streak
                    },
                    'summary': '\n'.join(summary_lines)
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing bankroll: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _search_knowledge(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 578: Search the collective knowledge base.
        """
        try:
            from core.models_unified_system import AgentKnowledgeSource
            from django.db.models import Q

            query = arguments.get('query', '')
            knowledge_type = arguments.get('knowledge_type', 'all')
            limit = arguments.get('limit', 10)

            if not query:
                return {
                    'success': False,
                    'error': 'Please provide a search query'
                }

            # Build search query
            search_filter = Q(title__icontains=query) | Q(summary__icontains=query)

            knowledge_query = AgentKnowledgeSource.objects.filter(
                search_filter,
                is_active=True
            )

            # Filter by knowledge type
            if knowledge_type != 'all':
                knowledge_query = knowledge_query.filter(knowledge_type=knowledge_type)

            # Order by relevance (confidence + freshness)
            knowledge_items = knowledge_query.order_by('-confidence_score', '-freshness_score')[:limit]

            # Build results
            results = []
            summary_lines = [f"**Knowledge Search: '{query}'**\n"]

            if not knowledge_items:
                summary_lines.append("No matching knowledge found.")
                summary_lines.append("\nTry a different search term or check agent learning dashboard.")
            else:
                summary_lines.append(f"Found {knowledge_items.count()} results:\n")

                for item in knowledge_items:
                    results.append({
                        'id': str(item.id),
                        'title': item.title,
                        'type': item.knowledge_type,
                        'agent': item.agent.name if item.agent else 'Unknown',
                        'summary': item.summary[:200],
                        'confidence': item.confidence_score,
                        'freshness': item.freshness_score
                    })

                    confidence_emoji = '🟢' if item.confidence_score > 0.7 else '🟡' if item.confidence_score > 0.4 else '🔴'
                    summary_lines.append(f"{confidence_emoji} **{item.title[:50]}...**")
                    summary_lines.append(f"   Type: {item.knowledge_type} | Agent: {item.agent.name if item.agent else 'Unknown'}")
                    summary_lines.append(f"   {item.summary[:100]}...")
                    summary_lines.append("")

            return {
                'success': True,
                'query': query,
                'knowledge_type': knowledge_type,
                'results': results,
                'total_found': len(results),
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # Session 579: Phase 4 Tool Handlers
    # =========================================================================

    def _create_boardroom_decision(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Create a new boardroom decision for review.
        """
        try:
            from core.models_unified_system import AgentDecisionSummary
            import uuid

            title = arguments.get('title', '')
            description = arguments.get('description', '')
            decision_type = arguments.get('decision_type', 'policy')
            priority = arguments.get('priority', 'medium')

            if not title or not description:
                return {
                    'success': False,
                    'error': 'Both title and description are required'
                }

            # Create the decision
            decision = AgentDecisionSummary.objects.create(
                decision_id=f"decision_{uuid.uuid4()}",
                title=title[:200],
                summary=description,
                decision_type=decision_type,
                priority=priority,
                status='pending',
                source='personal_assistant'
            )

            return {
                'success': True,
                'decision_id': decision.decision_id,
                'title': title,
                'decision_type': decision_type,
                'priority': priority,
                'summary': f"**Boardroom Decision Created:**\n\n📋 **{title}**\n\nType: {decision_type}\nPriority: {priority}\nStatus: Pending\n\nID: {decision.decision_id}\n\nThe decision is now available in the Boardroom for review and promotion."
            }

        except Exception as e:
            logger.error(f"Error creating boardroom decision: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _query_dreams(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Query agent dreams.
        """
        try:
            from core.models_unified_system import AgentDream, Agent

            agent_name = arguments.get('agent_name')
            dream_type = arguments.get('dream_type', 'all')
            limit = arguments.get('limit', 10)

            # Build query
            dreams_query = AgentDream.objects.all()

            if agent_name:
                agent = Agent.objects.filter(name__icontains=agent_name).first()
                if agent:
                    dreams_query = dreams_query.filter(agent=agent)

            if dream_type != 'all':
                dreams_query = dreams_query.filter(dream_type=dream_type)

            # Get recent dreams
            dreams = dreams_query.order_by('-dreamed_at')[:limit]

            # Build results
            results = []
            summary_lines = ["**Agent Dreams:**\n"]

            if not dreams:
                summary_lines.append("No dreams found.")
                summary_lines.append("\nDreams are generated when agents have idle time to be creative.")
            else:
                for dream in dreams:
                    results.append({
                        'id': str(dream.id),
                        'agent': dream.agent.name if dream.agent else 'Unknown',
                        'dream_type': dream.dream_type,
                        'title': dream.title if hasattr(dream, 'title') else 'Untitled',
                        'content': dream.content[:200] if dream.content else '',
                        'actionability': getattr(dream, 'actionability_score', 0),
                        'dreamed_at': dream.dreamed_at.isoformat() if dream.dreamed_at else None
                    })

                    emoji = '💡' if getattr(dream, 'actionability_score', 0) > 0.7 else '💭'
                    agent_name_display = dream.agent.name if dream.agent else 'Unknown'
                    title = getattr(dream, 'title', dream.content[:50] if dream.content else 'Untitled')
                    summary_lines.append(f"{emoji} **{agent_name_display}**: {title[:60]}...")

            return {
                'success': True,
                'dreams': results,
                'total_found': len(results),
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error querying dreams: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _manage_situations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Manage autonomous situations.
        """
        try:
            from core.models_autonomous_situations import AutonomousSituationSession

            action = arguments.get('action', 'list')
            situation_type = arguments.get('situation_type')
            limit = arguments.get('limit', 10)

            if action == 'list':
                # Get unique situation types with their latest sessions
                from django.db.models import Max, Count

                sessions = AutonomousSituationSession.objects.values('situation_type').annotate(
                    last_run=Max('started_at'),
                    count=Count('id')
                ).order_by('-last_run')[:limit]

                summary_lines = ["**Autonomous Situations:**\n"]
                situations = []

                situation_emojis = {
                    'design_trends': '🎨',
                    'job_matching': '💼',
                    'content_studio': '📺',
                    'stock_market': '📈',
                    'blockchain': '⛓️',
                    'market_intelligence': '🔍',
                    'narrative_drift': '📊',
                    'crypto_sentiment': '🪙',
                }

                for s in sessions:
                    situations.append({
                        'type': s['situation_type'],
                        'last_run': s['last_run'].isoformat() if s['last_run'] else None,
                        'total_sessions': s['count']
                    })

                    emoji = situation_emojis.get(s['situation_type'], '🔄')
                    summary_lines.append(f"{emoji} **{s['situation_type']}** ({s['count']} sessions)")

                if not sessions:
                    summary_lines.append("No autonomous situations have run yet.")

                return {
                    'success': True,
                    'situations': situations,
                    'total': len(situations),
                    'summary': '\n'.join(summary_lines)
                }

            elif action == 'history':
                # Get recent sessions
                sessions_query = AutonomousSituationSession.objects.all()

                if situation_type:
                    sessions_query = sessions_query.filter(situation_type=situation_type)

                sessions = sessions_query.order_by('-started_at')[:limit]

                summary_lines = ["**Situation History:**\n"]
                history = []

                for s in sessions:
                    history.append({
                        'id': str(s.id),
                        'type': s.situation_type,
                        'started_at': s.started_at.isoformat(),
                        'status': getattr(s, 'status', 'completed')
                    })

                    summary_lines.append(f"🔄 {s.situation_type} - {s.started_at.strftime('%Y-%m-%d %H:%M')}")

                return {
                    'success': True,
                    'history': history,
                    'total': len(history),
                    'summary': '\n'.join(summary_lines)
                }

            elif action == 'status':
                # Get current status of all situations
                from django.utils import timezone
                from datetime import timedelta

                recent = timezone.now() - timedelta(hours=24)
                recent_sessions = AutonomousSituationSession.objects.filter(
                    started_at__gte=recent
                ).values('situation_type').annotate(
                    count=models.Count('id')
                )

                summary_lines = ["**Situation Status (24h):**\n"]

                if recent_sessions:
                    for s in recent_sessions:
                        summary_lines.append(f"✅ {s['situation_type']}: {s['count']} runs")
                else:
                    summary_lines.append("No situations have run in the last 24 hours.")

                return {
                    'success': True,
                    'recent_activity': list(recent_sessions),
                    'summary': '\n'.join(summary_lines)
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing situations: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _query_conversations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Query agent-to-agent conversations.
        """
        try:
            from core.models_unified_system import HiveMindSession, Agent

            topic = arguments.get('topic', '')
            agent_name = arguments.get('agent_name')
            limit = arguments.get('limit', 10)

            # Query HiveMindSession with conversation mode
            conversations_query = HiveMindSession.objects.filter(
                session_mode='conversation'
            )

            if topic:
                conversations_query = conversations_query.filter(conversation_topic__icontains=topic)

            if agent_name:
                agent = Agent.objects.filter(name__icontains=agent_name).first()
                if agent:
                    conversations_query = conversations_query.filter(participant_ids__contains=[str(agent.id)])

            conversations = conversations_query.order_by('-created_at')[:limit]

            # Build results
            results = []
            summary_lines = ["**Agent Conversations:**\n"]

            if not conversations:
                summary_lines.append("No recent conversations found.")
                summary_lines.append("\nConversations happen during agent collaboration and knowledge sharing.")
            else:
                for conv in conversations:
                    participant_ids = getattr(conv, 'participant_ids', []) or []
                    results.append({
                        'id': str(conv.id),
                        'topic': conv.conversation_topic or conv.question or 'Untitled',
                        'participant_ids': participant_ids[:5],
                        'status': conv.status,
                        'created_at': conv.created_at.isoformat(),
                        'synthesis': (conv.synthesis_summary or conv.synthesis or '')[:200]
                    })

                    participant_str = f"{len(participant_ids)} agents" if participant_ids else 'Unknown'
                    topic_display = (conv.conversation_topic or conv.question or 'Untitled')[:40]
                    summary_lines.append(f"💬 **{topic_display}...**")
                    summary_lines.append(f"   Participants: {participant_str}")

            return {
                'success': True,
                'conversations': results,
                'total_found': len(results),
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error querying conversations: {e}")
            return {
                'success': False,
                'error': str(e)
            }
