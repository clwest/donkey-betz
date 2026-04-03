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
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_assistant_request_with_ml(request_data: dict) -> dict:
    """Analyze assistant request data using ML models (Text for intent classification)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=request_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'intent_classification': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML assistant request analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}

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



from core.agents.pa_handlers_tools import PAToolHandlersMixin
from core.agents.pa_handlers_manage import PAManageHandlersMixin
from core.agents.pa_handlers_query import PAQueryHandlersMixin
from core.agents.pa_handlers_fetch import PAFetchHandlersMixin


class PersonalAssistantAgent(PAToolHandlersMixin, PAManageHandlersMixin, PAQueryHandlersMixin, PAFetchHandlersMixin, BaseAgent):
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

For CODE GENERATION requests (generate, create, write code):
- CodeGeneratorAgent is BLOCKED (no codebase access on Railway) — do NOT dispatch to it
- Use CodeReviewAgent for code analysis and diff suggestions
- Use FullStackDeveloperAgent for complete feature implementations
- For actual file writing, recommend using Claude Code locally

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
- WorkflowAgent: Multi-step workflows

## PROFILE AWARENESS (Session 930)
Your context may include USER PROFILE STATUS with completeness percentage and suggested questions.
When profile is incomplete (<80%):
- Look for suggested profile questions in your context
- Weave them NATURALLY into conversation when appropriate
- Don't force it if user is focused on a specific task
- Frame questions as helping you serve them better
- If they provide information, acknowledge it warmly and use it to personalize responses

Example natural prompts:
- "By the way, to better match opportunities to your skills - what are your key skills?"
- "To help you achieve your goals, what are you trying to accomplish this quarter?"
- "For personalized recommendations, how would you describe your risk tolerance?"

NEVER ask profile questions if:
- User is in the middle of a specific task
- You've already asked a profile question in this conversation
- Context doesn't include profile status section"""

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
- "List them" or "List all items" - USE max_items=100 to get full lists

IMPORTANT: This tool returns ACTUAL ITEMS with titles, IDs, and details - not just counts.
When user asks to "list" items, CALL THIS TOOL with max_items=100 to get the items.
DO NOT say you cannot access items - you CAN by calling this tool.

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
                            "description": "Maximum items to return. Use 100 for 'list all' requests. Default: 10"
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
        # Session 944: List Boardroom Decisions Tool
        {
            "type": "function",
            "function": {
                "name": "list_boardroom_decisions",
                "description": """List pending boardroom decisions with full details.
USE THIS when user says:
- "List them" (when context is about boardroom items)
- "Show me all decisions"
- "List pending decisions"
- "Show draft decisions"
- "What are the 418 product decisions?"

IMPORTANT: This returns ACTUAL DECISIONS with titles, types, and details.
Use this to list items - DO NOT say you cannot access them.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["draft", "review", "all"],
                            "description": "Filter by status (default: draft)"
                        },
                        "decision_type": {
                            "type": "string",
                            "enum": ["all", "product", "experiment", "pipeline", "policy", "architecture", "guideline"],
                            "description": "Filter by type (default: all)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum items to return (default: 50, max: 100)"
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Offset for pagination (default: 0)"
                        }
                    }
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
        },
        # Session 579: Phase 5 Tools - Medium Priority from Roadmap
        {
            "type": "function",
            "function": {
                "name": "get_opportunity_pipeline",
                "description": """Query the revenue opportunity pipeline.
Use this for:
- "Show me top opportunities"
- "What's our revenue potential?"
- "What opportunities are in the pipeline?"
- "Any high-value opportunities?"
Returns opportunities with scores, sources, and revenue potential.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "new", "scored", "actioned", "converted"],
                            "description": "Filter by opportunity status"
                        },
                        "min_score": {
                            "type": "number",
                            "description": "Minimum opportunity score (0-100)"
                        },
                        "opportunity_type": {
                            "type": "string",
                            "enum": ["all", "job", "gig", "freelance", "business", "investment"],
                            "description": "Type of opportunity"
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
                "name": "create_project",
                "description": """Create a new project from conversation.
Use this for:
- "Create a project for [topic]"
- "Start a new research project"
- "Organize this into a project"
- "I want to start a project called..."
Creates a PartnershipProject with the specified details.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Project name (required)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Project description"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["general", "research", "creative", "business", "development", "content"],
                            "description": "Project category"
                        },
                        "goal": {
                            "type": "string",
                            "description": "What the project aims to achieve"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for the project"
                        }
                    },
                    "required": ["name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_agent_conversation",
                "description": """Start an agent-to-agent conversation/debate on a topic.
Use this for:
- "Have agents discuss this"
- "Get diverse perspectives on [topic]"
- "Start a debate about [issue]"
- "What do agents think about...?"
Triggers a multi-agent conversation where agents share perspectives.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic for agents to discuss (required)"
                        },
                        "agent_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific agents to include (optional - auto-selects if not provided)"
                        },
                        "max_rounds": {
                            "type": "integer",
                            "description": "Maximum conversation rounds (default: 3)"
                        },
                        "conversation_type": {
                            "type": "string",
                            "enum": ["discussion", "debate", "brainstorm", "analysis"],
                            "description": "Type of conversation"
                        }
                    },
                    "required": ["topic"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "schedule_content",
                "description": """Schedule content for distribution to platforms.
Use this for:
- "Publish this to Twitter and LinkedIn"
- "Schedule content for tomorrow"
- "Multi-platform distribution"
- "Post this to social media"
Creates content distribution entries for the specified platforms.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Content title (required)"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content body/description (required)"
                        },
                        "platforms": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["twitter", "linkedin", "youtube", "instagram", "medium", "substack"]
                            },
                            "description": "Platforms to distribute to"
                        },
                        "schedule_time": {
                            "type": "string",
                            "description": "ISO datetime to publish (optional - publishes immediately if not set)"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags/hashtags for the content"
                        }
                    },
                    "required": ["title", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_project_intelligence",
                "description": """Get deep intelligence and insights for a specific project.
Use this for:
- "Show me project intelligence"
- "What have agents learned about this project?"
- "Project deep-dive"
- "Give me insights on [project]"
Returns agent learnings, conversations, dreams, and spider data related to the project.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Project name to analyze (required)"
                        },
                        "include_sections": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["learnings", "conversations", "dreams", "spider_data", "recommendations"]
                            },
                            "description": "Sections to include (default: all)"
                        },
                        "time_period": {
                            "type": "string",
                            "enum": ["24h", "7d", "30d", "all"],
                            "description": "Time range for data"
                        }
                    },
                    "required": ["project_name"]
                }
            }
        },
        # Session 579: Query tracked concerns from ThinkingAgent
        {
            "type": "function",
            "function": {
                "name": "query_tracked_concerns",
                "description": """Query the system's tracked concerns and their resolution status.
Use this for:
- "What concerns need attention?"
- "Show me system concerns"
- "What issues have been resolved?"
- "What is the thinking engine tracking?"
- "What problems is the system aware of?"
Returns concerns identified by ThinkingAgent with their status, severity, and resolution details.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "in_progress", "resolved", "pending"],
                            "description": "Filter by status (default: all)"
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["all", "high", "medium", "low"],
                            "description": "Filter by severity (default: all)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of concerns to return (default: 20)"
                        }
                    }
                }
            }
        },
        # Session 579: Get latest System Insights report
        {
            "type": "function",
            "function": {
                "name": "get_system_insights",
                "description": """Get the latest System Insights report from the ThinkingAgent.
Use this for:
- "Show me system insights"
- "What did the thinking engine find?"
- "Get the latest thinking report"
- "What's the system analysis?"
Returns the most recent System Insights report with patterns, concerns, and opportunities.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of recent reports to retrieve (default: 1, max: 5)"
                        }
                    }
                }
            }
        },
        # Session 579: Phase 7 - Advisor consultation tool
        {
            "type": "function",
            "function": {
                "name": "get_advisor_consultation",
                "description": """Query the legendary advisors (Warren Buffett, Cathie Wood, etc.) for insights.
Use this for:
- "What would Warren Buffett say about this?"
- "Get advisor insights"
- "Consult the advisors about [topic]"
- "What do the experts think?"
Returns insights from the 25 legendary advisors with their wisdom and recommendations.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "advisor_name": {
                            "type": "string",
                            "description": "Optional: specific advisor to query (e.g., 'Warren Buffett', 'Cathie Wood')"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["investing", "technology", "business", "leadership", "all"],
                            "description": "Filter advisors by category (default: all)"
                        },
                        "topic": {
                            "type": "string",
                            "description": "Optional: topic to get insights about"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of insights to return (default: 10)"
                        }
                    }
                }
            }
        },
        # Session 579: Phase 7 - Revenue metrics tool
        {
            "type": "function",
            "function": {
                "name": "query_revenue_metrics",
                "description": """Query revenue metrics, earnings, and financial performance.
Use this for:
- "What's our revenue?"
- "Show me earnings"
- "Revenue metrics"
- "Financial performance"
- "How much have we made?"
Returns revenue by source, time period, and status with totals and trends.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time_period": {
                            "type": "string",
                            "enum": ["24h", "7d", "30d", "90d", "all"],
                            "description": "Time range for metrics (default: 30d)"
                        },
                        "source_type": {
                            "type": "string",
                            "description": "Optional: filter by source (job, gig, investment, betting, content)"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed", "cancelled"],
                            "description": "Filter by status (default: all)"
                        },
                        "include_opportunities": {
                            "type": "boolean",
                            "description": "Include potential revenue from opportunities (default: true)"
                        }
                    }
                }
            }
        },
        # =========================================================================
        # Session 580: Phase 8 - High-Impact Expansion (10 tools)
        # =========================================================================
        # Tool 29: manage_proactive_alerts
        {
            "type": "function",
            "function": {
                "name": "manage_proactive_alerts",
                "description": """Manage proactive alerts, notifications, and automations.
Use this for:
- "Create an alert for X"
- "Show my alerts"
- "Enable/disable automation"
- "What notifications do I have?"
- "Set up monitoring for..."
Supports alerts, notifications, suggestions, and automations.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list_alerts", "create_alert", "toggle_alert", "list_notifications", "list_automations", "run_check"],
                            "description": "Action to perform"
                        },
                        "alert_type": {
                            "type": "string",
                            "enum": ["price", "trend", "opportunity", "system", "custom"],
                            "description": "Type of alert (for create)"
                        },
                        "condition": {
                            "type": "string",
                            "description": "Alert condition description"
                        },
                        "alert_id": {
                            "type": "string",
                            "description": "Alert ID (for toggle)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # Tool 30: query_learning_progress
        {
            "type": "function",
            "function": {
                "name": "query_learning_progress",
                "description": """Query agent learning progress, evolution metrics, and training status.
Use this for:
- "How are agents learning?"
- "Learning progress"
- "Agent evolution stats"
- "Training status"
- "What have agents learned?"
Returns learning curves, preferences, and evolution metrics.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Optional: specific agent to query"
                        },
                        "metric_type": {
                            "type": "string",
                            "enum": ["learning_stats", "preferences", "evolution", "interactions", "all"],
                            "description": "Type of learning data (default: all)"
                        },
                        "time_period": {
                            "type": "string",
                            "enum": ["24h", "7d", "30d"],
                            "description": "Time range (default: 7d)"
                        }
                    }
                }
            }
        },
        # Tool 31: manage_team
        {
            "type": "function",
            "function": {
                "name": "manage_team",
                "description": """Manage agent teams, roles, and team workflows.
Use this for:
- "Create a team for X"
- "Show my teams"
- "Add agent to team"
- "Team stats"
- "List agent roles"
Supports team creation, member management, and team workflows.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list_teams", "create_team", "get_team", "add_member", "team_stats", "list_roles"],
                            "description": "Action to perform"
                        },
                        "team_id": {
                            "type": "string",
                            "description": "Team ID (for get/add_member)"
                        },
                        "team_name": {
                            "type": "string",
                            "description": "Team name (for create)"
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID (for add_member)"
                        },
                        "role": {
                            "type": "string",
                            "description": "Role for the agent"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # Tool 32: generate_video
        {
            "type": "function",
            "function": {
                "name": "generate_video",
                "description": """Generate videos using AI video agents.
Use this for:
- "Create a video about X"
- "Generate video content"
- "Make a promotional video"
- "Video for social media"
Supports text-to-video, image-to-video, and video editing.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Video description/prompt"
                        },
                        "video_type": {
                            "type": "string",
                            "enum": ["text_to_video", "image_to_video", "edit", "short_form", "explainer"],
                            "description": "Type of video to generate"
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Target duration in seconds (default: 30)"
                        },
                        "style": {
                            "type": "string",
                            "description": "Visual style (cinematic, animated, documentary, etc.)"
                        },
                        "aspect_ratio": {
                            "type": "string",
                            "enum": ["16:9", "9:16", "1:1", "4:3"],
                            "description": "Aspect ratio (default: 16:9)"
                        }
                    },
                    "required": ["prompt"]
                }
            }
        },
        # Tool 33: manage_distribution
        {
            "type": "function",
            "function": {
                "name": "manage_distribution",
                "description": """Manage content distribution across platforms.
Use this for:
- "Publish to Twitter/LinkedIn/etc"
- "Schedule content"
- "List my distributions"
- "Distribution stats"
- "Connect platform"
Supports multi-platform publishing and scheduling.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list_platforms", "list_distributions", "create_distribution", "publish", "schedule", "stats"],
                            "description": "Action to perform"
                        },
                        "platform": {
                            "type": "string",
                            "enum": ["twitter", "linkedin", "facebook", "instagram", "youtube", "tiktok", "all"],
                            "description": "Target platform"
                        },
                        "content_id": {
                            "type": "string",
                            "description": "Content ID to distribute"
                        },
                        "scheduled_time": {
                            "type": "string",
                            "description": "ISO timestamp for scheduling"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # Tool 34: query_analytics
        {
            "type": "function",
            "function": {
                "name": "query_analytics",
                "description": """Query system analytics, usage metrics, and performance data.
Use this for:
- "Show analytics"
- "Usage stats"
- "Performance metrics"
- "Cost breakdown"
- "Dashboard data"
Returns comprehensive analytics across the platform.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "report_type": {
                            "type": "string",
                            "enum": ["overview", "usage", "performance", "costs", "agents", "content", "all"],
                            "description": "Type of analytics report (default: overview)"
                        },
                        "time_period": {
                            "type": "string",
                            "enum": ["24h", "7d", "30d", "90d"],
                            "description": "Time range (default: 7d)"
                        },
                        "include_trends": {
                            "type": "boolean",
                            "description": "Include trend analysis (default: true)"
                        }
                    }
                }
            }
        },
        # Tool 35: time_travel_memory
        {
            "type": "function",
            "function": {
                "name": "time_travel_memory",
                "description": """Access agent memory time-travel capabilities.
Use this for:
- "Show agent memory history"
- "What did agent know at date X?"
- "Memory snapshots"
- "Replay agent state"
- "Memory timeline"
Access historical agent states and memory evolution.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list_snapshots", "get_snapshot", "compare", "timeline", "restore"],
                            "description": "Action to perform"
                        },
                        "agent_name": {
                            "type": "string",
                            "description": "Agent to query"
                        },
                        "snapshot_date": {
                            "type": "string",
                            "description": "ISO date for snapshot"
                        },
                        "compare_dates": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Two dates to compare"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # Tool 36: manage_memory_palace
        {
            "type": "function",
            "function": {
                "name": "manage_memory_palace",
                "description": """Manage agent memory palace and memory organization.
Use this for:
- "Show memory palace"
- "Organize memories"
- "Memory clusters"
- "Important memories"
- "Memory search"
Access structured memory organization and retrieval.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["overview", "list_rooms", "get_room", "search", "important", "recent"],
                            "description": "Action to perform"
                        },
                        "agent_name": {
                            "type": "string",
                            "description": "Agent to query"
                        },
                        "room_id": {
                            "type": "string",
                            "description": "Memory room ID"
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query for memories"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results (default: 10)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # Tool 37: run_diagnostics
        {
            "type": "function",
            "function": {
                "name": "run_diagnostics",
                "description": """Run system diagnostics and health checks.
Use this for:
- "Run diagnostics"
- "System health check"
- "Test spiders"
- "Check services"
- "Debug info"
Comprehensive system health and diagnostics.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "diagnostic_type": {
                            "type": "string",
                            "enum": ["full", "spiders", "agents", "services", "database", "celery", "quick"],
                            "description": "Type of diagnostic (default: quick)"
                        },
                        "include_details": {
                            "type": "boolean",
                            "description": "Include detailed output (default: false)"
                        },
                        "fix_issues": {
                            "type": "boolean",
                            "description": "Attempt to fix found issues (default: false)"
                        }
                    }
                }
            }
        },
        # Tool 38: manage_collaboration
        {
            "type": "function",
            "function": {
                "name": "manage_collaboration",
                "description": """Manage agent collaborations and partnerships.
Use this for:
- "Agent collaboration stats"
- "Start collaboration between agents"
- "Collaboration history"
- "Agent partnerships"
- "Collaboration network"
Track and manage how agents work together.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["stats", "history", "network", "start", "active", "performance"],
                            "description": "Action to perform"
                        },
                        "agent_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Agents to collaborate (for start)"
                        },
                        "collaboration_id": {
                            "type": "string",
                            "description": "Collaboration ID (for details)"
                        },
                        "time_period": {
                            "type": "string",
                            "enum": ["24h", "7d", "30d"],
                            "description": "Time range (default: 7d)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # =========================================================================
        # Session 580: Phase 9 - Deep System Coverage (5 tools)
        # =========================================================================
        # Tool 39: manage_project
        {
            "type": "function",
            "function": {
                "name": "manage_project",
                "description": """Manage partnership projects - list, create, update, export.
Use this for:
- "Show my projects"
- "Create a project"
- "Export project to PDF"
- "Project details"
- "Assign agent to project"
Full project lifecycle management.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "get", "create", "update", "delete", "export_pdf", "assign_agent", "get_intelligence"],
                            "description": "Action to perform"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project ID (for get/update/delete/export)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Project name (for create)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Project description (for create/update)"
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID (for assign_agent)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # Tool 40: query_legal
        {
            "type": "function",
            "function": {
                "name": "query_legal",
                "description": """Query legal case files, litigation documents, and case context.
Use this for:
- "Show my legal cases"
- "Get case details"
- "List case documents"
- "Analyze legal document"
- "Generate response to filing"
Legal document and case management.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list_cases", "get_case", "list_documents", "get_context", "active_case", "list_case_files"],
                            "description": "Action to perform"
                        },
                        "case_id": {
                            "type": "string",
                            "description": "Case ID (for get_case/list_documents)"
                        },
                        "document_id": {
                            "type": "string",
                            "description": "Document ID (for specific document operations)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # Tool 41: manage_agent_training
        {
            "type": "function",
            "function": {
                "name": "manage_agent_training",
                "description": """Manage agent training, capabilities, and templates.
Use this for:
- "Show training stats"
- "List agent capabilities"
- "Training history"
- "Available templates"
- "Train an agent"
Agent training and capability management.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list_agents", "get_agent", "list_capabilities", "list_templates", "stats", "history", "dashboard"],
                            "description": "Action to perform"
                        },
                        "agent_name": {
                            "type": "string",
                            "description": "Agent name (for get_agent)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # Tool 42: manage_workflow_templates
        {
            "type": "function",
            "function": {
                "name": "manage_workflow_templates",
                "description": """Manage workflow templates and active workflows.
Use this for:
- "Show workflow templates"
- "List active workflows"
- "Workflow status"
- "Create workflow from template"
Workflow template management.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list_templates", "list_active", "get_status", "create_from_template"],
                            "description": "Action to perform"
                        },
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID (for get_status)"
                        },
                        "template_name": {
                            "type": "string",
                            "description": "Template name (for create_from_template)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # Tool 43: generate_image
        {
            "type": "function",
            "function": {
                "name": "generate_image",
                "description": """Generate images using AI image agents.
Use this for:
- "Create an image of X"
- "Generate a logo"
- "Make a banner"
- "Create artwork"
Delegates to ImageAgent for AI image generation.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Image description/prompt"
                        },
                        "style": {
                            "type": "string",
                            "description": "Visual style (realistic, artistic, cartoon, etc.)"
                        },
                        "size": {
                            "type": "string",
                            "enum": ["1024x1024", "1792x1024", "1024x1792"],
                            "description": "Image size (default: 1024x1024)"
                        },
                        "image_type": {
                            "type": "string",
                            "enum": ["general", "logo", "banner", "icon", "artwork"],
                            "description": "Type of image to generate"
                        }
                    },
                    "required": ["prompt"]
                }
            }
        },
        # Session 581: Phase 10 - Betting/Sports Tools
        # Tool 44: query_live_odds
        {
            "type": "function",
            "function": {
                "name": "query_live_odds",
                "description": """Get detailed live odds from multiple sportsbooks.
Use this for:
- "What are the odds for the Chiefs game?"
- "Show me spreads for tonight's NBA games"
- "Compare odds across bookmakers"
- "What's the moneyline for the Lakers?"
Returns spreads, moneylines, totals from 40+ bookmakers.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sport": {
                            "type": "string",
                            "enum": ["nfl", "nba", "mlb", "nhl", "ncaaf", "ncaab", "soccer", "mma"],
                            "description": "Sport to query (default: nfl)"
                        },
                        "market_type": {
                            "type": "string",
                            "enum": ["spreads", "h2h", "totals", "all"],
                            "description": "Market type: spreads, h2h (moneyline), totals, or all"
                        },
                        "team": {
                            "type": "string",
                            "description": "Optional: filter by team name"
                        }
                    },
                    "required": []
                }
            }
        },
        # Tool 45: query_games
        {
            "type": "function",
            "function": {
                "name": "query_games",
                "description": """Query sports games - today's matchups, trending games, and analytics.
Use this for:
- "What games are on today?"
- "Show trending NFL games"
- "Game analytics for Lakers vs Celtics"
- "This week's schedule"
Returns game schedules, analytics, and betting metrics.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["today", "trending", "this_week", "analytics", "search"],
                            "description": "Action: today, trending, this_week, analytics, search"
                        },
                        "sport": {
                            "type": "string",
                            "enum": ["nfl", "nba", "mlb", "nhl", "ncaaf", "ncaab", "all"],
                            "description": "Sport filter (default: all)"
                        },
                        "game_id": {
                            "type": "string",
                            "description": "Game ID for analytics action"
                        },
                        "team": {
                            "type": "string",
                            "description": "Team name to search for"
                        }
                    },
                    "required": []
                }
            }
        },
        # Tool 46: query_line_movements
        {
            "type": "function",
            "function": {
                "name": "query_line_movements",
                "description": """Track betting line movements and identify sharp money.
Use this for:
- "Show line movement for Chiefs game"
- "Which games have the biggest line moves?"
- "Sharp money indicators"
- "Line history for tonight's game"
Returns line movement history and sharp action indicators.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["game", "movers", "sharp"],
                            "description": "Action: game (specific game), movers (biggest moves), sharp (sharp money)"
                        },
                        "game_id": {
                            "type": "string",
                            "description": "Game ID for specific line history"
                        },
                        "sport": {
                            "type": "string",
                            "enum": ["nfl", "nba", "mlb", "nhl", "all"],
                            "description": "Sport filter for movers"
                        },
                        "min_movement": {
                            "type": "number",
                            "description": "Minimum line movement points (default: 0.5)"
                        }
                    },
                    "required": []
                }
            }
        },
        # Tool 47: query_futures
        {
            "type": "function",
            "function": {
                "name": "query_futures",
                "description": """Get futures betting odds for championships, MVPs, etc.
Use this for:
- "Who's favored to win the Super Bowl?"
- "NBA championship odds"
- "MVP futures odds"
- "World Series winner odds"
Returns futures odds from multiple sportsbooks.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sport": {
                            "type": "string",
                            "enum": ["nfl", "nba", "mlb", "nhl", "ncaaf", "ncaab"],
                            "description": "Sport for futures"
                        },
                        "market": {
                            "type": "string",
                            "enum": ["championship", "conference", "division", "mvp", "all"],
                            "description": "Futures market type (default: championship)"
                        }
                    },
                    "required": []
                }
            }
        },
        # Tool 48: query_player_props
        {
            "type": "function",
            "function": {
                "name": "query_player_props",
                "description": """Get player prop betting odds for specific games.
Use this for:
- "Mahomes passing yards props"
- "LeBron points props tonight"
- "Player props for the Chiefs game"
- "Touchdown scorer odds"
Returns player prop lines from multiple books.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "Event/game ID for props"
                        },
                        "player": {
                            "type": "string",
                            "description": "Player name to search for"
                        },
                        "prop_type": {
                            "type": "string",
                            "enum": ["points", "rebounds", "assists", "passing_yards", "rushing_yards", "touchdowns", "all"],
                            "description": "Type of prop (default: all)"
                        }
                    },
                    "required": []
                }
            }
        },
        # Tool 49: query_betting_recommendations
        {
            "type": "function",
            "function": {
                "name": "query_betting_recommendations",
                "description": """Get AI-generated betting recommendations and picks.
Use this for:
- "Best bets today"
- "Your top picks for NFL"
- "Recommended bets this week"
- "High confidence picks"
Returns AI-analyzed betting recommendations with confidence scores.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "generate", "top_picks", "history"],
                            "description": "Action: list, generate new, top_picks, or history"
                        },
                        "sport": {
                            "type": "string",
                            "enum": ["nfl", "nba", "mlb", "nhl", "all"],
                            "description": "Sport filter"
                        },
                        "min_confidence": {
                            "type": "number",
                            "description": "Minimum confidence score 0-100 (default: 60)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max recommendations to return (default: 10)"
                        }
                    },
                    "required": []
                }
            }
        },
        # ===== Phase 11: Notification Tools (Session 582) =====
        {
            "type": "function",
            "function": {
                "name": "manage_notifications",
                "description": """Manage proactive notifications.
Use this for:
- "Show my notifications"
- "Any unread notifications?"
- "Mark all notifications as read"
- "Dismiss that notification"
- "Update my notification preferences"
Returns notification list, counts, and management actions.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "read", "dismiss", "read_all", "preferences", "counts"],
                            "description": "Action: list, read (mark as read), dismiss, read_all, preferences, counts"
                        },
                        "notification_id": {
                            "type": "string",
                            "description": "Notification ID (for read/dismiss actions)"
                        },
                        "unread_only": {
                            "type": "boolean",
                            "description": "Only show unread notifications (default: false)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max notifications to return (default: 20)"
                        },
                        "preferences": {
                            "type": "object",
                            "description": "Preference updates for preferences action",
                            "properties": {
                                "email_enabled": {"type": "boolean"},
                                "push_enabled": {"type": "boolean"},
                                "digest_frequency": {"type": "string", "enum": ["realtime", "hourly", "daily", "weekly"]}
                            }
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_push_notifications",
                "description": """Manage Web Push notification settings.
Use this for:
- "Check push notification status"
- "Am I subscribed to push notifications?"
- "Send me a test notification"
- "Update my push preferences"
- "Enable/disable arb alerts"
Returns push subscription status and settings.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["status", "preferences", "test"],
                            "description": "Action: status (check subscription), preferences (get/set), test (send test push)"
                        },
                        "preferences": {
                            "type": "object",
                            "description": "Preference updates for preferences action",
                            "properties": {
                                "notifications_enabled": {"type": "boolean"},
                                "arb_alerts_enabled": {"type": "boolean"},
                                "arb_min_profit_pct": {"type": "number", "description": "Minimum profit % for arb alerts (default: 1.0)"}
                            }
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # ===== Phase 12: Export & Scheduler Tools (Session 582) =====
        {
            "type": "function",
            "function": {
                "name": "manage_exports",
                "description": """Export data in various formats.
Use this for:
- "Export project as PDF"
- "Download research as ZIP"
- "Export revenue data"
- "Export legal documents"
- "Get my content as markdown"
Returns export URLs or file data.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "export_type": {
                            "type": "string",
                            "enum": ["project", "research", "content", "revenue", "legal", "portfolio"],
                            "description": "Type of data to export"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["pdf", "zip", "csv", "markdown", "docx", "text"],
                            "description": "Export format (default varies by type)"
                        },
                        "resource_id": {
                            "type": "string",
                            "description": "ID of resource to export (project_id, etc.)"
                        },
                        "options": {
                            "type": "object",
                            "description": "Additional export options",
                            "properties": {
                                "include_images": {"type": "boolean"},
                                "include_metadata": {"type": "boolean"},
                                "date_range": {"type": "string", "description": "Date range for revenue exports"}
                            }
                        }
                    },
                    "required": ["export_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_scheduler",
                "description": """Manage scheduled tasks and distributions.
Use this for:
- "Show scheduled distributions"
- "Cancel scheduled post"
- "Reschedule my content"
- "View Celery schedules"
- "Schedule a workflow"
Returns scheduled items and management actions.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "cancel", "reschedule", "celery_schedules", "schedule_workflow"],
                            "description": "Action: list, cancel, reschedule, celery_schedules, schedule_workflow"
                        },
                        "distribution_id": {
                            "type": "string",
                            "description": "Distribution ID for cancel/reschedule actions"
                        },
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID for schedule_workflow action"
                        },
                        "new_time": {
                            "type": "string",
                            "description": "New scheduled time (ISO format) for reschedule action"
                        },
                        "schedule_type": {
                            "type": "string",
                            "enum": ["distributions", "workflows", "all"],
                            "description": "Type of schedules to list (default: all)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # ===== Phase 13: Monitoring Tools (Session 582) =====
        {
            "type": "function",
            "function": {
                "name": "query_system_health",
                "description": """Get system health and status information.
Use this for:
- "How is the system doing?"
- "Check system health"
- "Content studio status"
- "ML scoring status"
- "Spider health"
- "Agent health check"
Returns health metrics and status for various subsystems.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subsystem": {
                            "type": "string",
                            "enum": ["unified", "content_studio", "narrative_drift", "market_intelligence", "ml_scoring", "agents", "spiders", "all"],
                            "description": "Subsystem to check (default: unified)"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_activity_metrics",
                "description": """Get activity streams, ROI metrics, and provenance data.
Use this for:
- "Show recent activity"
- "What's the ROI?"
- "Show activity stream"
- "Track content provenance"
Returns activity logs, ROI calculations, and provenance chains.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "metric_type": {
                            "type": "string",
                            "enum": ["activity", "roi", "provenance"],
                            "description": "Type of metrics: activity stream, ROI, or provenance"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max items to return (default: 20)"
                        }
                    },
                    "required": ["metric_type"]
                }
            }
        },
        # ===== Phase 14: Artifact & Review Tools (Session 582) =====
        {
            "type": "function",
            "function": {
                "name": "manage_artifacts",
                "description": """Manage AI-generated artifacts and their execution.
Use this for:
- "Show pending artifacts"
- "List all artifacts"
- "Execute that artifact"
- "Approve/reject artifact"
- "Show artifact executions"
Returns artifacts, execution status, and management actions.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "pending", "get", "decide", "execute", "executions", "execution_status"],
                            "description": "Action: list, pending, get, decide, execute, executions, execution_status"
                        },
                        "artifact_id": {
                            "type": "string",
                            "description": "Artifact ID for get/decide/execute/executions actions"
                        },
                        "decision": {
                            "type": "string",
                            "enum": ["approve", "reject"],
                            "description": "Decision for decide action"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for decision"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max items to return (default: 20)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_reviews",
                "description": """Manage Chief of Staff review documents (Pro/Con analysis).
Use this for:
- "Show review documents"
- "Get review details"
- "Ask the pro side a question"
- "Ask the con side a question"
- "Decide on review"
- "Generate review for artifact"
- "Trigger auto-reviews"
Returns review documents, pro/con arguments, and decisions.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "get", "ask_pro", "ask_con", "decide", "generate", "trigger_auto", "stats"],
                            "description": "Action: list, get, ask_pro, ask_con, decide, generate, trigger_auto, stats"
                        },
                        "review_id": {
                            "type": "string",
                            "description": "Review ID for get/ask_pro/ask_con/decide actions"
                        },
                        "artifact_id": {
                            "type": "string",
                            "description": "Artifact ID for generate action"
                        },
                        "question": {
                            "type": "string",
                            "description": "Question for ask_pro/ask_con actions"
                        },
                        "decision": {
                            "type": "string",
                            "enum": ["approve", "reject"],
                            "description": "Decision for decide action"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for decision"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # ===== Phase 15: Journey & Proposal Tools (Session 583) =====
        {
            "type": "function",
            "function": {
                "name": "manage_journeys",
                "description": """Manage learning journeys and progress tracking.
Use this for:
- "Start a learning journey"
- "Show my active journeys"
- "Get journey status"
- "Start journey step"
- "Complete journey step"
- "Reset journey progress"
Returns journey status, steps, and progress tracking.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["start", "status", "step_start", "step_complete", "active", "reset"],
                            "description": "Action: start, status, step_start, step_complete, active, reset"
                        },
                        "journey_id": {
                            "type": "string",
                            "description": "Journey ID for status/step/reset actions"
                        },
                        "step_id": {
                            "type": "integer",
                            "description": "Step ID for step_start/step_complete actions"
                        },
                        "journey_type": {
                            "type": "string",
                            "description": "Type of journey to start (for start action)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_proposals",
                "description": """Manage AI-generated proposals and their execution.
Use this for:
- "Show proposals"
- "Get proposal stats"
- "Approve proposal"
- "Reject proposal"
- "Execute proposal"
Returns proposals, stats, and execution status.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "stats", "approve", "reject", "execute"],
                            "description": "Action: list, stats, approve, reject, execute"
                        },
                        "proposal_id": {
                            "type": "string",
                            "description": "Proposal ID for approve/reject/execute actions"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for approval/rejection"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of proposals to return (default 20)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # ===== Phase 16: Solutions & Learning Tools (Session 583) =====
        {
            "type": "function",
            "function": {
                "name": "manage_solutions",
                "description": """Manage AI-discovered solutions and their application.
Use this for:
- "Show available solutions"
- "Get solution details"
- "Apply a solution"
Returns solutions, details, and application results.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "get", "apply"],
                            "description": "Action: list, get, apply"
                        },
                        "solution_id": {
                            "type": "string",
                            "description": "Solution ID for get/apply actions"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of solutions to return (default 20)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_learning",
                "description": """Query learning system data, patterns, and insights.
Use this for:
- "Show learning dashboard"
- "What patterns have been discovered?"
- "Show learning insights"
- "Get my learning profile"
- "Show learning progress"
- "How does data flow through learning?"
- "Show learning feed"
Returns learning metrics, patterns, insights, and progress.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["dashboard", "patterns", "insights", "profile", "progress", "data_flow", "feed"],
                            "description": "Type of learning data to query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of items to return (default 20)"
                        }
                    },
                    "required": ["query_type"]
                }
            }
        },
        # ===== Phase 17: Portfolio & Nexus Tools (Session 583) =====
        {
            "type": "function",
            "function": {
                "name": "manage_portfolio",
                "description": """Manage creative portfolio items (images, videos, content).
Use this for:
- "Show my portfolio"
- "Delete portfolio item"
- "Check for broken links in portfolio"
- "Bulk delete old items"
Returns portfolio items and management actions.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "delete", "bulk_delete", "check_broken"],
                            "description": "Action: list, delete, bulk_delete, check_broken"
                        },
                        "item_type": {
                            "type": "string",
                            "description": "Type of item (image, video, content) for delete"
                        },
                        "item_id": {
                            "type": "string",
                            "description": "Item ID for delete action"
                        },
                        "item_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Item IDs for bulk_delete action"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_nexus",
                "description": """Query the Nexus unified intelligence system.
Use this for:
- "Get unified intelligence data"
- "Implement an insight"
- "Investigate system behavior"
Returns intelligence data, insights, and behavioral analysis.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["intelligence_data", "implement_insight", "investigate_behavior"],
                            "description": "Type of nexus query"
                        },
                        "insight_id": {
                            "type": "string",
                            "description": "Insight ID for implement_insight action"
                        },
                        "behavior_query": {
                            "type": "string",
                            "description": "Behavior description for investigate_behavior"
                        }
                    },
                    "required": ["query_type"]
                }
            }
        },
        # ===== Phase 18: Predictions & Performance Tools (Session 583) =====
        {
            "type": "function",
            "function": {
                "name": "manage_predictions",
                "description": """Manage agent predictions (prophecies) and their verification.
Use this for:
- "Show predictions overview"
- "Show agent predictions"
- "Verify a prediction"
- "Upvote a prediction"
- "Show prediction leaderboard"
- "Generate predictions from dreams"
Returns predictions, verification status, and leaderboard.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["overview", "agent", "detail", "verify", "upvote", "leaderboard", "generate", "expire"],
                            "description": "Action: overview, agent, detail, verify, upvote, leaderboard, generate, expire"
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID for agent predictions"
                        },
                        "prediction_id": {
                            "type": "string",
                            "description": "Prediction ID for detail/verify/upvote"
                        },
                        "outcome": {
                            "type": "string",
                            "enum": ["correct", "incorrect", "partial"],
                            "description": "Outcome for verify action"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_performance",
                "description": """Query performance metrics, predictions, and pricing optimization.
Use this for:
- "Predict my performance"
- "Show performance predictions"
- "Get pricing optimization"
- "Compare performance"
Returns performance metrics, predictions, and optimization suggestions.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["predict", "predictions", "pricing", "compare"],
                            "description": "Type of performance query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of items to return (default 20)"
                        }
                    },
                    "required": ["query_type"]
                }
            }
        },
        # ===== Phase 19: Analytics Tools (Session 584) =====
        {
            "type": "function",
            "function": {
                "name": "query_workflow_analytics",
                "description": """Query workflow execution analytics, performance metrics, and trends.
Use this for:
- "Show workflow execution history"
- "Show workflow trends"
- "Show success/failure analysis"
- "Show workflow performance"
- "Compare workflows"
- "Show step performance"
- "Show execution heatmap"
- "Show workflow analytics dashboard"
Returns execution history, trends, performance metrics, comparisons, and heatmaps.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["history", "trends", "success_failure", "performance", "performance_comparison", "compare", "steps", "heatmap", "summary", "dashboard"],
                            "description": "Type of analytics query"
                        },
                        "workflow_id": {
                            "type": "integer",
                            "description": "Workflow ID for history/steps filtering"
                        },
                        "workflow_ids": {
                            "type": "string",
                            "description": "Comma-separated workflow IDs for compare"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to look back (default 30)"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "processing", "completed", "failed"],
                            "description": "Filter by execution status"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results for history (default 100)"
                        }
                    },
                    "required": ["query_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_video_analytics",
                "description": """Query video analytics including character performance and lip sync.
Use this for:
- "Show character performance"
- "Start lip sync job"
- "Check lip sync status"
Returns character performance metrics and lip sync job status.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["character_performance", "lip_sync", "lip_sync_status"],
                            "description": "Type of video analytics query"
                        },
                        "prediction_id": {
                            "type": "string",
                            "description": "Prediction ID for lip sync status check"
                        },
                        "video_url": {
                            "type": "string",
                            "description": "Video URL for lip sync"
                        },
                        "audio_url": {
                            "type": "string",
                            "description": "Audio URL for lip sync"
                        }
                    },
                    "required": ["query_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_model_analytics",
                "description": """Query LLM model performance analytics and preferences.
Use this for:
- "Show model performance"
- "Show model preferences"
- "Set model preferences"
Returns model performance metrics and preference settings.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["performance", "preferences", "set_preferences"],
                            "description": "Type of model analytics query"
                        },
                        "preferences": {
                            "type": "object",
                            "description": "Preferences object for set_preferences"
                        }
                    },
                    "required": ["query_type"]
                }
            }
        },
        # ===== Phase 20: Collaboration & Search Tools (Session 584) =====
        {
            "type": "function",
            "function": {
                "name": "query_collaboration",
                "description": """Query agent collaboration data, performance, and network.
Use this for:
- "Show collaboration history"
- "Show collaboration stats"
- "Find best collaborator for a task"
- "Show agent performance"
- "Show top performers"
- "Show collaboration network"
- "Show collaboration monitor"
Returns collaboration history, stats, network visualization, and performance metrics.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["history", "stats", "find_collaborator", "performance", "top_performers", "network", "monitor", "dashboard"],
                            "description": "Type of collaboration query"
                        },
                        "agent_name": {
                            "type": "string",
                            "description": "Agent name for performance query"
                        },
                        "task_type": {
                            "type": "string",
                            "description": "Task type for find_collaborator"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default 20)"
                        }
                    },
                    "required": ["query_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_favorites",
                "description": """Manage favorites and batch operations for images, videos, workflows.
Use this for:
- "Show my favorite images"
- "Toggle favorite on image/video/workflow"
- "Batch download images"
- "Show workflow favorites"
Returns favorite status and batch operation results.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list_images", "list_videos", "list_workflows", "toggle_image", "toggle_video", "toggle_workflow", "batch_download"],
                            "description": "Action to perform"
                        },
                        "item_id": {
                            "type": "string",
                            "description": "ID of item for toggle actions"
                        },
                        "item_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "IDs for batch download"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_semantic_search",
                "description": """Perform semantic search and RAG operations on documents and knowledge.
Use this for:
- "Search for documents about topic"
- "Semantic search for concept"
- "Show embeddings stats"
- "Generate answer from documents"
Returns semantically relevant documents and generated answers.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["search", "generate", "stats"],
                            "description": "Type of semantic query"
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query for semantic search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default 10)"
                        }
                    },
                    "required": ["query_type"]
                }
            }
        },
        # ===== Phase 21: Project & Workflow Collaboration Tools (Session 585) =====
        {
            "type": "function",
            "function": {
                "name": "manage_project_collaboration",
                "description": """Manage shared projects and collaborators.

- "Show shared projects"
- "Invite user to project"
- "Show my invitations"
- "Accept/decline invitation"
- "List project collaborators"
- "Remove collaborator"
- "Show project activity"

Supports project sharing, invitations, and collaborator management.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list_projects", "get_project", "invite", "list_invitations", "accept_invitation", "decline_invitation", "list_collaborators", "remove_collaborator", "get_activity", "get_comments"],
                            "description": "Action to perform"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project ID for project-specific actions"
                        },
                        "user_email": {
                            "type": "string",
                            "description": "Email to invite as collaborator"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID to remove as collaborator"
                        },
                        "invitation_id": {
                            "type": "string",
                            "description": "Invitation ID for accept/decline"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["viewer", "editor", "admin"],
                            "description": "Role for invited collaborator"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_workflow_sharing",
                "description": """Share and collaborate on workflows.

- "Share workflow with user"
- "List shared workflows"
- "Collaborate on workflow"

Supports workflow sharing and collaborative execution.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["share", "list_shared", "collaborate"],
                            "description": "Action to perform"
                        },
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID to share or collaborate on"
                        },
                        "user_email": {
                            "type": "string",
                            "description": "Email of user to share with"
                        },
                        "permissions": {
                            "type": "string",
                            "enum": ["view", "edit", "execute"],
                            "description": "Permission level for shared workflow"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # ===== Phase 22: Team Workflows & Agent Evolution Tools (Session 585) =====
        {
            "type": "function",
            "function": {
                "name": "manage_team_workflows",
                "description": """Manage team workflows - create, start, execute, and monitor team-based workflows.

- "Create team workflow"
- "Start team workflow"
- "Show team workflow status"
- "List active team workflows"
- "Execute workflow step"
- "Complete workflow step"

Supports team-based workflow orchestration.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create", "start", "status", "list_active", "list_templates", "execute", "run_full", "execute_step", "complete_step"],
                            "description": "Action to perform"
                        },
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID for workflow-specific actions"
                        },
                        "step_id": {
                            "type": "string",
                            "description": "Step ID for step-specific actions"
                        },
                        "name": {
                            "type": "string",
                            "description": "Workflow name (for create)"
                        },
                        "steps": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Workflow steps (for create)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_agent_evolution",
                "description": """Query agent evolution, XP, levels, and abilities.

- "Show agent evolution overview"
- "Show agent XP and level"
- "Show evolution leaderboard"
- "List available abilities"
- "Show recent XP gains"

Tracks agent growth and progression.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["overview", "agent_detail", "leaderboard", "abilities", "xp_gains", "award_xp", "unlock_ability"],
                            "description": "Type of evolution query"
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID for agent-specific queries"
                        },
                        "ability_id": {
                            "type": "string",
                            "description": "Ability ID for unlock action"
                        },
                        "xp_amount": {
                            "type": "integer",
                            "description": "XP amount to award"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for XP award"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default 10)"
                        }
                    },
                    "required": ["query_type"]
                }
            }
        },
        # ===== Phase 23: Voice Marketplace & Agent Relationships Tools (Session 586) =====
        {
            "type": "function",
            "function": {
                "name": "manage_voice_marketplace",
                "description": """Manage voice cloning and text-to-speech marketplace.

Actions:
- browse: Browse available voices in marketplace
- my_voices: List your created/owned voices
- earnings: View voice earnings summary
- transactions: View transaction history
- create: Create new voice from ElevenLabs
- clone_start: Start voice cloning request
- clone_status: Check clone request status
- detail: Get voice details
- publish: Publish voice to marketplace
- unpublish: Remove voice from marketplace
- update: Update voice settings
- generate: Generate speech from voice
- preview: Preview voice sample
- add_review: Add review to voice""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["browse", "my_voices", "earnings", "transactions", "create", "clone_start", "clone_status", "detail", "publish", "unpublish", "update", "generate", "preview", "add_review"],
                            "description": "Action to perform"
                        },
                        "voice_id": {
                            "type": "string",
                            "description": "Voice UUID (for detail/publish/unpublish/update/generate/preview/add_review)"
                        },
                        "request_id": {
                            "type": "string",
                            "description": "Clone request UUID (for clone_status)"
                        },
                        "text": {
                            "type": "string",
                            "description": "Text to generate speech (for generate)"
                        },
                        "elevenlabs_voice_id": {
                            "type": "string",
                            "description": "ElevenLabs voice ID (for create)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Voice name (for create/update)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Voice description (for update)"
                        },
                        "price": {
                            "type": "number",
                            "description": "Price per use (for publish)"
                        },
                        "rating": {
                            "type": "integer",
                            "description": "Rating 1-5 (for add_review)"
                        },
                        "review_text": {
                            "type": "string",
                            "description": "Review text (for add_review)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_agent_relationships",
                "description": """Query agent relationships, alliances, and rivalries.

Query types:
- overview: Get relationships overview for all agents
- agent_detail: Get specific agent's relationships
- create: Create new relationship between agents
- interact: Record interaction between agents
- events: Get relationship events history
- auto_generate: Auto-generate relationships based on activity
- alliance_detail: Get alliance details
- alliance_create: Create new alliance
- alliance_add: Add member to alliance
- alliance_disband: Disband alliance
- rivalry_detail: Get rivalry details
- rivalry_create: Create rivalry between agents
- rivalry_compete: Record competition result
- rivalry_end: End rivalry""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["overview", "agent_detail", "create", "interact", "events", "auto_generate", "alliance_detail", "alliance_create", "alliance_add", "alliance_disband", "rivalry_detail", "rivalry_create", "rivalry_compete", "rivalry_end"],
                            "description": "Type of query"
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "Agent UUID (for agent_detail)"
                        },
                        "relationship_id": {
                            "type": "string",
                            "description": "Relationship UUID (for interact/events)"
                        },
                        "alliance_id": {
                            "type": "string",
                            "description": "Alliance UUID (for alliance operations)"
                        },
                        "rivalry_id": {
                            "type": "string",
                            "description": "Rivalry UUID (for rivalry operations)"
                        },
                        "agent_a_id": {
                            "type": "string",
                            "description": "First agent UUID (for create/rivalry_create)"
                        },
                        "agent_b_id": {
                            "type": "string",
                            "description": "Second agent UUID (for create/rivalry_create)"
                        },
                        "relationship_type": {
                            "type": "string",
                            "description": "Type of relationship (mentor/peer/collaborator)"
                        },
                        "alliance_name": {
                            "type": "string",
                            "description": "Alliance name (for alliance_create)"
                        },
                        "member_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Member agent UUIDs (for alliance_create)"
                        },
                        "winner_id": {
                            "type": "string",
                            "description": "Winner agent UUID (for rivalry_compete)"
                        }
                    },
                    "required": ["query_type"]
                }
            }
        },
        # ===== Phase 24: Hive Mind & Time Capsules Tools (Session 587) =====
        {
            "type": "function",
            "function": {
                "name": "manage_hive_mind",
                "description": """Manage Hive Mind sessions - multi-agent collective intelligence.

Actions:
- start: Start new Hive Mind session with a question
- status: Get session status and contributions
- list: List recent Hive Mind sessions
- agents: Get available agents for Hive Mind
- preview: Preview which agents would be selected for a question""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["start", "status", "list", "agents", "preview"],
                            "description": "Action to perform"
                        },
                        "question": {
                            "type": "string",
                            "description": "Question for the Hive Mind (for start/preview)"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context (for start)"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session UUID (for status)"
                        },
                        "max_agents": {
                            "type": "integer",
                            "description": "Maximum agents to involve (default: 8, max: 12)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of sessions to return (for list)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_time_capsules",
                "description": """Manage agent time capsules - messages from agents to their future selves.

Actions:
- overview: Get time capsule statistics and recent capsules
- list_agent: List capsules for a specific agent
- create: Create new time capsule for an agent
- detail: Get time capsule details
- reveal: Reveal a capsule that's ready to open
- react: Add reaction to a revealed capsule
- ready: Get capsules ready to reveal
- generate: Auto-generate capsules for agents""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["overview", "list_agent", "create", "detail", "reveal", "react", "ready", "generate"],
                            "description": "Action to perform"
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "Agent UUID (for list_agent/create)"
                        },
                        "capsule_id": {
                            "type": "string",
                            "description": "Capsule UUID (for detail/reveal/react)"
                        },
                        "message": {
                            "type": "string",
                            "description": "Time capsule message (for create)"
                        },
                        "reveal_days": {
                            "type": "integer",
                            "description": "Days until capsule can be revealed (for create, default: 7)"
                        },
                        "capsule_type": {
                            "type": "string",
                            "enum": ["prediction", "reflection", "goal", "milestone", "wisdom", "confession"],
                            "description": "Type of time capsule (for create)"
                        },
                        "reaction": {
                            "type": "string",
                            "enum": ["nostalgic", "proud", "surprised", "amused", "inspired", "reflective"],
                            "description": "Reaction type (for react)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        # ===== Phase 25: A/B Testing & Memory Clusters Tools (Session 587) =====
        {
            "type": "function",
            "function": {
                "name": "manage_ab_testing",
                "description": """Manage A/B testing experiments for optimization.

Actions:
- dashboard: Get A/B testing overview and statistics
- list: List all A/B tests
- create: Create new A/B test
- detail: Get test details
- start: Start a test
- pause: Pause a running test
- complete: Complete a test
- results: Get test results
- add_variant: Add variant to test
- record_event: Record event for variant""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["dashboard", "list", "create", "detail", "start", "pause", "complete", "results", "add_variant", "record_event"],
                            "description": "Action to perform"
                        },
                        "test_id": {
                            "type": "string",
                            "description": "Test UUID (for detail/start/pause/complete/results/add_variant)"
                        },
                        "variant_id": {
                            "type": "string",
                            "description": "Variant UUID (for record_event)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Test name (for create)"
                        },
                        "test_type": {
                            "type": "string",
                            "enum": ["prompt", "model", "workflow", "ui", "pricing"],
                            "description": "Type of test (for create)"
                        },
                        "hypothesis": {
                            "type": "string",
                            "description": "Test hypothesis (for create)"
                        },
                        "variant_name": {
                            "type": "string",
                            "description": "Variant name (for add_variant)"
                        },
                        "variant_config": {
                            "type": "object",
                            "description": "Variant configuration (for add_variant)"
                        },
                        "event_type": {
                            "type": "string",
                            "description": "Event type (for record_event)"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["draft", "running", "paused", "completed"],
                            "description": "Filter by status (for list)"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_memory_clusters",
                "description": """Manage agent memory clusters - semantic grouping of memories.

Actions:
- overview: Get clusters overview across all agents
- list_agent: List clusters for specific agent
- generate: Generate clusters for an agent
- detail: Get cluster details
- add_memory: Add memory to cluster
- remove_memory: Remove memory from cluster
- evolution: Get cluster evolution history
- find_similar: Find similar clusters
- visualization: Get visualization data
- generate_all: Generate clusters for all agents""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["overview", "list_agent", "generate", "detail", "add_memory", "remove_memory", "evolution", "find_similar", "visualization", "generate_all"],
                            "description": "Action to perform"
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "Agent UUID (for list_agent/generate/evolution/visualization)"
                        },
                        "cluster_id": {
                            "type": "string",
                            "description": "Cluster UUID (for detail/add_memory/remove_memory)"
                        },
                        "memory_id": {
                            "type": "string",
                            "description": "Memory UUID (for add_memory/remove_memory)"
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query (for find_similar)"
                        }
                    },
                    "required": ["action"]
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

        # Session 739: Store context for sub-agent calls
        self._current_spider_context = spider_context
        self._current_scifi_context = scifi_context

        # Session 565: Store intelligence context for use in question answering
        self._intelligence_context = intelligence_context

        # Session 773: Inject dynamic PA knowledge based on query triggers
        try:
            from core.services.pa_knowledge_injector import get_pa_knowledge_injector
            injector = get_pa_knowledge_injector()
            pa_knowledge = injector.get_context_for_query(task)
            if pa_knowledge.get('has_dynamic_context'):
                spider_context['pa_knowledge'] = pa_knowledge
                self._current_spider_context = spider_context  # Update stored context
                logger.info(
                    f"🧠 [Session 773] PA Knowledge injected: "
                    f"triggers={pa_knowledge.get('triggered_by', [])}"
                )
        except Exception as e:
            logger.warning(f"Failed to inject PA knowledge: {e}")

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
        # Session 892: Expanded patterns for business research + creation workflows
        # =========================================================================
        workflow_patterns = [
            # Original patterns
            'research and create', 'research then create',
            'brand identity package', 'brand package',
            'thumbnail package', 'complete package',
            # Session 892: Business workflow patterns
            'business plan', 'create a business', 'write a business plan',
            'business model', 'startup plan', 'go to market plan',
            'with logo', 'with colors', 'with branding',
            'full package', 'complete branding', 'brand and logo',
            'research and write', 'analyze and create', 'analyze and write',
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
                model="gpt-5.2",
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

