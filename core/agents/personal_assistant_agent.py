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
            # Session 757: Return rich conversation data for Memory Palace display
            response_content = gpt_response.get('content', '')
            return AgentResult(
                success=True,
                message=response_content,
                data={
                    'type': 'conversation',
                    'content_type': 'assistant_response',
                    'response': response_content,
                    'query': task,
                },
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

        # Session 944: List boardroom decisions
        if tool_name == "list_boardroom_decisions":
            return self._list_boardroom_decisions(arguments)

        if tool_name == "query_dreams":
            return self._query_dreams(arguments)

        if tool_name == "manage_situations":
            return self._manage_situations(arguments)

        if tool_name == "query_conversations":
            return self._query_conversations(arguments)

        # Session 579: Phase 5 Tools
        if tool_name == "get_opportunity_pipeline":
            return self._get_opportunity_pipeline(arguments)

        if tool_name == "create_project":
            return self._create_project(arguments)

        if tool_name == "trigger_agent_conversation":
            return self._trigger_agent_conversation(arguments)

        if tool_name == "schedule_content":
            return self._schedule_content(arguments)

        if tool_name == "analyze_project_intelligence":
            return self._analyze_project_intelligence(arguments)

        # Session 579: ThinkingAgent/System Insights tools
        if tool_name == "query_tracked_concerns":
            return self._query_tracked_concerns(arguments)

        if tool_name == "get_system_insights":
            return self._get_system_insights(arguments)

        # Session 579: Phase 7 tools
        if tool_name == "get_advisor_consultation":
            return self._get_advisor_consultation(arguments)

        if tool_name == "query_revenue_metrics":
            return self._query_revenue_metrics(arguments)

        # Session 580: Phase 8 tools
        if tool_name == "manage_proactive_alerts":
            return self._manage_proactive_alerts(arguments)

        if tool_name == "query_learning_progress":
            return self._query_learning_progress(arguments)

        if tool_name == "manage_team":
            return self._manage_team(arguments)

        if tool_name == "generate_video":
            return self._generate_video(arguments)

        if tool_name == "manage_distribution":
            return self._manage_distribution(arguments)

        if tool_name == "query_analytics":
            return self._query_analytics(arguments)

        if tool_name == "time_travel_memory":
            return self._time_travel_memory(arguments)

        if tool_name == "manage_memory_palace":
            return self._manage_memory_palace(arguments)

        if tool_name == "run_diagnostics":
            return self._run_diagnostics(arguments)

        if tool_name == "manage_collaboration":
            return self._manage_collaboration(arguments)

        # Session 580: Phase 9 tools
        if tool_name == "manage_project":
            return self._manage_project(arguments)

        if tool_name == "query_legal":
            return self._query_legal(arguments)

        if tool_name == "manage_agent_training":
            return self._manage_agent_training(arguments)

        if tool_name == "manage_workflow_templates":
            return self._manage_workflow_templates(arguments)

        if tool_name == "generate_image":
            return self._generate_image(arguments)

        # Session 581: Phase 10 - Betting/Sports tools
        if tool_name == "query_live_odds":
            return self._query_live_odds(arguments)

        if tool_name == "query_games":
            return self._query_games(arguments)

        if tool_name == "query_line_movements":
            return self._query_line_movements(arguments)

        if tool_name == "query_futures":
            return self._query_futures(arguments)

        if tool_name == "query_player_props":
            return self._query_player_props(arguments)

        if tool_name == "query_betting_recommendations":
            return self._query_betting_recommendations(arguments)

        # Phase 11: Notification Tools (Session 582)
        if tool_name == "manage_notifications":
            return self._manage_notifications(arguments)

        if tool_name == "manage_push_notifications":
            return self._manage_push_notifications(arguments)

        # Phase 12: Export & Scheduler Tools (Session 582)
        if tool_name == "manage_exports":
            return self._manage_exports(arguments)

        if tool_name == "manage_scheduler":
            return self._manage_scheduler(arguments)

        # Phase 13: Monitoring Tools (Session 582)
        if tool_name == "query_system_health":
            return self._query_system_health(arguments)

        if tool_name == "query_activity_metrics":
            return self._query_activity_metrics(arguments)

        # ===== Phase 14: Artifact & Review Tools (Session 583) =====
        if tool_name == "manage_artifacts":
            return self._manage_artifacts(arguments)

        if tool_name == "manage_reviews":
            return self._manage_reviews(arguments)

        # ===== Phase 15: Journey & Proposal Tools (Session 583) =====
        if tool_name == "manage_journeys":
            return self._manage_journeys(arguments)

        if tool_name == "manage_proposals":
            return self._manage_proposals(arguments)

        # ===== Phase 16: Solutions & Learning Tools (Session 583) =====
        if tool_name == "manage_solutions":
            return self._manage_solutions(arguments)

        if tool_name == "query_learning":
            return self._query_learning(arguments)

        # ===== Phase 17: Portfolio & Nexus Tools (Session 583) =====
        if tool_name == "manage_portfolio":
            return self._manage_portfolio(arguments)

        if tool_name == "query_nexus":
            return self._query_nexus(arguments)

        # ===== Phase 18: Predictions & Performance Tools (Session 583) =====
        if tool_name == "manage_predictions":
            return self._manage_predictions(arguments)

        if tool_name == "query_performance":
            return self._query_performance(arguments)

        # ===== Phase 19: Analytics Tools (Session 584) =====
        if tool_name == "query_workflow_analytics":
            return self._query_workflow_analytics(arguments)

        if tool_name == "query_video_analytics":
            return self._query_video_analytics(arguments)

        if tool_name == "query_model_analytics":
            return self._query_model_analytics(arguments)

        # ===== Phase 20: Collaboration & Search Tools (Session 584) =====
        if tool_name == "query_collaboration":
            return self._query_collaboration(arguments)

        if tool_name == "manage_favorites":
            return self._manage_favorites(arguments)

        if tool_name == "query_semantic_search":
            return self._query_semantic_search(arguments)

        # ===== Phase 21: Project & Workflow Collaboration Tools (Session 585) =====
        if tool_name == "manage_project_collaboration":
            return self._manage_project_collaboration(arguments)

        if tool_name == "manage_workflow_sharing":
            return self._manage_workflow_sharing(arguments)

        # ===== Phase 22: Team Workflows & Agent Evolution Tools (Session 585) =====
        if tool_name == "manage_team_workflows":
            return self._manage_team_workflows(arguments)

        if tool_name == "query_agent_evolution":
            return self._query_agent_evolution(arguments)

        # ===== Phase 23: Voice Marketplace & Agent Relationships Tools (Session 586) =====
        if tool_name == "manage_voice_marketplace":
            return self._manage_voice_marketplace(arguments)

        if tool_name == "query_agent_relationships":
            return self._query_agent_relationships(arguments)

        # ===== Phase 24: Hive Mind & Time Capsules Tools (Session 587) =====
        if tool_name == "manage_hive_mind":
            return self._manage_hive_mind(arguments)

        if tool_name == "manage_time_capsules":
            return self._manage_time_capsules(arguments)

        # ===== Phase 25: A/B Testing & Memory Clusters Tools (Session 587) =====
        if tool_name == "manage_ab_testing":
            return self._manage_ab_testing(arguments)

        if tool_name == "manage_memory_clusters":
            return self._manage_memory_clusters(arguments)

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

        return super()._execute_tool_call(tool_name, arguments)

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
            # Session 739: Pass spider_context to sub-agents for real intelligence
            result = workflow_agent.execute(
                task=workflow_description,
                context=context,
                scifi_context=getattr(self, '_current_scifi_context', {}),
                spider_context=getattr(self, '_current_spider_context', {})
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
            # Session 739: Pass spider_context to sub-agents for real intelligence
            result = detector.execute(
                task=f"Find arbitrage opportunities for {sport} with minimum {min_profit}% profit",
                context={'sport': sport, 'min_profit': min_profit, 'limit': limit},
                scifi_context=getattr(self, '_current_scifi_context', {}),
                spider_context=getattr(self, '_current_spider_context', {})
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
                wagers = Wager.objects.filter(bankroll=bankroll).order_by('-placed_at')[:limit]

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
                pending = Wager.objects.filter(bankroll=bankroll, status='pending').order_by('-placed_at')

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

    def _list_boardroom_decisions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 944: List boardroom decisions with pagination support.
        Returns actual items from AgentDecisionSummary.
        """
        try:
            from core.models_unified_system import AgentDecisionSummary

            status_filter = arguments.get('status', 'draft')
            decision_type = arguments.get('decision_type', 'all')
            limit = min(arguments.get('limit', 50), 100)  # Cap at 100
            offset = arguments.get('offset', 0)

            # Build query
            query = AgentDecisionSummary.objects.all()

            # Filter by status
            if status_filter == 'draft':
                query = query.filter(status='draft')
            elif status_filter == 'review':
                query = query.filter(status='review')
            # 'all' shows both draft and review

            # Filter by decision type
            if decision_type and decision_type != 'all':
                query = query.filter(decision_type=decision_type)

            # Get total count
            total_count = query.count()

            # Get paginated results
            decisions = query.order_by('-created_at')[offset:offset + limit]

            # Build items list
            items = []
            for d in decisions:
                items.append({
                    'id': str(d.id),
                    'topic': d.topic,
                    'decision_type': d.decision_type,
                    'impact_area': d.impact_area,
                    'status': d.status,
                    'recommended_stance': d.recommended_stance[:200] if d.recommended_stance else '',
                    'created_at': d.created_at.isoformat() if d.created_at else None,
                })

            # Build summary
            summary_lines = [f"**Boardroom Decisions** ({total_count} total)\n"]

            if not items:
                summary_lines.append("No decisions found matching criteria.")
            else:
                # Group by type for display
                by_type = {}
                for item in items:
                    t = item['decision_type']
                    if t not in by_type:
                        by_type[t] = []
                    by_type[t].append(item)

                type_icons = {
                    'product': '🎯',
                    'experiment': '🧪',
                    'pipeline': '⚡',
                    'policy': '📜',
                    'architecture': '🏗️',
                    'guideline': '📋',
                }

                for dtype, dtype_items in by_type.items():
                    icon = type_icons.get(dtype, '📌')
                    summary_lines.append(f"\n{icon} **{dtype.title()}** ({len(dtype_items)}):")
                    for item in dtype_items[:10]:  # Show up to 10 per type in summary
                        summary_lines.append(f"  • {item['topic'][:60]}")
                        summary_lines.append(f"    ID: {item['id'][:8]}...")

                if total_count > offset + limit:
                    summary_lines.append(f"\n... and {total_count - offset - limit} more. Use offset={offset + limit} for next page.")

            return {
                'success': True,
                'total_count': total_count,
                'returned_count': len(items),
                'offset': offset,
                'limit': limit,
                'items': items,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error listing boardroom decisions: {e}")
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

    # ==================== SESSION 579: PHASE 5 TOOLS ====================

    def _get_opportunity_pipeline(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Query the opportunity pipeline.
        """
        try:
            from core.models_unified_system import Opportunity
            from django.utils import timezone
            from datetime import timedelta

            status = arguments.get('status', 'all')
            min_score = arguments.get('min_score', 0)
            opportunity_type = arguments.get('opportunity_type', 'all')
            limit = arguments.get('limit', 10)

            # Build query
            opps_query = Opportunity.objects.all()

            if status != 'all':
                opps_query = opps_query.filter(status=status)

            if min_score > 0:
                opps_query = opps_query.filter(overall_score__gte=min_score)

            if opportunity_type != 'all':
                opps_query = opps_query.filter(opportunity_type=opportunity_type)

            # Order by score descending, recent first
            opps = opps_query.order_by('-overall_score', '-created_at')[:limit]

            # Build results
            results = []
            summary_lines = ["**Opportunity Pipeline:**\n"]
            total_revenue = 0

            if not opps:
                summary_lines.append("No opportunities found matching criteria.")
                summary_lines.append("\nOpportunities are discovered by spiders and scored by agents.")
            else:
                for opp in opps:
                    score = getattr(opp, 'overall_score', 0) or 0
                    revenue = getattr(opp, 'potential_revenue', 0) or 0
                    total_revenue += revenue

                    results.append({
                        'id': str(opp.id),
                        'title': opp.title[:100] if opp.title else 'Untitled',
                        'type': getattr(opp, 'opportunity_type', 'unknown'),
                        'source': getattr(opp, 'source', 'unknown'),
                        'score': score,
                        'status': getattr(opp, 'status', 'new'),
                        'estimated_revenue': revenue,
                        'created_at': opp.created_at.isoformat() if hasattr(opp, 'created_at') and opp.created_at else None
                    })

                    # Score emoji
                    if score >= 80:
                        emoji = '🔥'
                    elif score >= 60:
                        emoji = '⭐'
                    else:
                        emoji = '📋'

                    title_short = opp.title[:45] if opp.title else 'Untitled'
                    summary_lines.append(f"{emoji} **{title_short}...** (Score: {score})")

                summary_lines.append(f"\n📊 Total: {len(results)} opportunities")
                if total_revenue > 0:
                    summary_lines.append(f"💰 Est. Revenue: ${total_revenue:,.0f}")

            return {
                'success': True,
                'opportunities': results,
                'total_count': len(results),
                'total_estimated_revenue': total_revenue,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error querying opportunity pipeline: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _create_project(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Create a new project.
        """
        try:
            from core.models_partnership import PartnershipProject
            from django.utils import timezone

            name = arguments.get('name', '').strip()
            if not name:
                return {
                    'success': False,
                    'error': 'Project name is required'
                }

            description = arguments.get('description', '')
            category = arguments.get('category', 'general')
            goal = arguments.get('goal', '')
            tags = arguments.get('tags', [])

            # Create the project
            project = PartnershipProject.objects.create(
                user=self.user,
                project_name=name,
                project_type=category,
                description=description,
                goal=goal,
                status='planning',
                category=category,
                tags=tags if isinstance(tags, list) else [],
                ai_contribution_percent=50,
                human_contribution_percent=50
            )

            logger.info(f"✅ PA created project: {project.project_name}")

            return {
                'success': True,
                'project_id': str(project.id),
                'project_name': project.project_name,
                'summary': f"**Project Created!**\n\n📁 **{project.project_name}**\n- Category: {category}\n- Status: planning\n- Goal: {goal[:100] if goal else 'Not specified'}\n\nYou can now assign agents and start work on this project."
            }

        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _trigger_agent_conversation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Trigger an agent-to-agent conversation.
        """
        try:
            from core.models_unified_system import HiveMindSession, Agent
            from core.tasks import run_multi_agent_conversation
            from django.utils import timezone
            import random

            topic = arguments.get('topic', '').strip()
            if not topic:
                return {
                    'success': False,
                    'error': 'Topic is required for agent conversation'
                }

            agent_names = arguments.get('agent_names', [])
            max_rounds = arguments.get('max_rounds', 3)
            conversation_type = arguments.get('conversation_type', 'discussion')

            # If no agents specified, pick relevant ones
            if not agent_names:
                # Get active agents and pick 3-4 randomly
                active_agents = Agent.objects.filter(
                    is_active=True
                ).exclude(
                    name__in=['PersonalAssistantAgent', 'ThinkingAgent']
                ).order_by('?')[:4]
                agent_names = [a.name for a in active_agents]

            if len(agent_names) < 2:
                return {
                    'success': False,
                    'error': 'Need at least 2 agents for a conversation'
                }

            # Create HiveMindSession for the conversation
            session = HiveMindSession.objects.create(
                session_mode='conversation',
                question=topic,
                conversation_topic=topic,
                context={
                    'conversation_type': conversation_type,
                    'max_rounds': max_rounds,
                    'triggered_by': 'personal_assistant'
                },
                status='active',
                participant_ids=[str(a.id) for a in Agent.objects.filter(name__in=agent_names)]
            )

            # Trigger the conversation task asynchronously
            try:
                run_multi_agent_conversation.delay(
                    max_conversations=1,
                    participants_per_conversation=len(agent_names),
                    max_rounds=max_rounds
                )
            except Exception as task_error:
                logger.warning(f"Could not trigger async conversation: {task_error}")

            return {
                'success': True,
                'session_id': str(session.id),
                'topic': topic,
                'participants': agent_names,
                'summary': f"**Agent Conversation Started!**\n\n💬 Topic: {topic}\n👥 Participants: {', '.join(agent_names[:4])}\n🔄 Type: {conversation_type}\n\nAgents are now discussing this topic. Check back soon for insights!"
            }

        except Exception as e:
            logger.error(f"Error triggering agent conversation: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _schedule_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Schedule content for distribution.
        """
        try:
            from core.models_unified_system import ContentDistribution
            from django.utils import timezone
            from django.utils.dateparse import parse_datetime

            title = arguments.get('title', '').strip()
            content = arguments.get('content', '').strip()

            if not title:
                return {
                    'success': False,
                    'error': 'Content title is required'
                }

            if not content:
                return {
                    'success': False,
                    'error': 'Content body is required'
                }

            platforms = arguments.get('platforms', ['twitter'])
            schedule_time_str = arguments.get('schedule_time')
            tags = arguments.get('tags', [])

            # Parse schedule time if provided
            schedule_time = None
            if schedule_time_str:
                schedule_time = parse_datetime(schedule_time_str)

            created_distributions = []
            summary_lines = ["**Content Scheduled:**\n"]

            for platform in platforms:
                try:
                    dist = ContentDistribution.objects.create(
                        user=self.user,
                        title=title,
                        description=content,
                        content_type='post',
                        tags=tags if isinstance(tags, list) else [],
                        platform_listing_id=None,  # Will be set when actually published
                    )
                    created_distributions.append({
                        'id': str(dist.id),
                        'platform': platform,
                        'scheduled_for': schedule_time.isoformat() if schedule_time else 'immediate'
                    })

                    time_str = schedule_time.strftime('%Y-%m-%d %H:%M') if schedule_time else 'Now'
                    summary_lines.append(f"📤 **{platform.title()}** - {time_str}")

                except Exception as platform_error:
                    logger.warning(f"Failed to schedule for {platform}: {platform_error}")

            if not created_distributions:
                return {
                    'success': False,
                    'error': 'Failed to schedule content for any platform'
                }

            summary_lines.append(f"\n📝 Title: {title[:50]}...")
            if tags:
                summary_lines.append(f"🏷️ Tags: {', '.join(tags[:5])}")

            return {
                'success': True,
                'distributions': created_distributions,
                'count': len(created_distributions),
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error scheduling content: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _analyze_project_intelligence(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Get deep intelligence for a project.
        """
        try:
            from core.models_partnership import PartnershipProject
            from core.models_unified_system import (
                AgentKnowledgeSource, HiveMindSession, AgentDream, SpiderData
            )
            from django.utils import timezone
            from datetime import timedelta

            project_name = arguments.get('project_name', '').strip()
            if not project_name:
                return {
                    'success': False,
                    'error': 'Project name is required'
                }

            include_sections = arguments.get('include_sections', ['learnings', 'conversations', 'dreams', 'spider_data', 'recommendations'])
            time_period = arguments.get('time_period', '7d')

            # Find the project
            project = PartnershipProject.objects.filter(
                project_name__icontains=project_name
            ).first()

            if not project:
                return {
                    'success': False,
                    'error': f'Project "{project_name}" not found'
                }

            # Time filter
            time_map = {
                '24h': timedelta(hours=24),
                '7d': timedelta(days=7),
                '30d': timedelta(days=30),
                'all': timedelta(days=365*10)
            }
            cutoff = timezone.now() - time_map.get(time_period, timedelta(days=7))

            results = {
                'project_id': str(project.id),
                'project_name': project.project_name,
                'status': project.status,
                'sections': {}
            }
            summary_lines = [f"**Project Intelligence: {project.project_name}**\n"]

            # Learnings
            if 'learnings' in include_sections:
                learnings = AgentKnowledgeSource.objects.filter(
                    project=project,
                    created_at__gte=cutoff
                ).order_by('-created_at')[:10]

                results['sections']['learnings'] = {
                    'count': learnings.count(),
                    'items': [{'title': l.title[:50], 'agent': l.source_agent.name if l.source_agent else 'Unknown'} for l in learnings[:5]]
                }
                summary_lines.append(f"📚 **Learnings:** {learnings.count()} knowledge items")

            # Conversations
            if 'conversations' in include_sections:
                conversations = HiveMindSession.objects.filter(
                    project=project,
                    created_at__gte=cutoff
                ).order_by('-created_at')[:10]

                results['sections']['conversations'] = {
                    'count': conversations.count(),
                    'items': [{'topic': c.conversation_topic or c.question or 'Untitled', 'status': c.status} for c in conversations[:5]]
                }
                summary_lines.append(f"💬 **Conversations:** {conversations.count()} agent discussions")

            # Dreams
            if 'dreams' in include_sections:
                dreams = AgentDream.objects.filter(
                    project=project,
                    dreamed_at__gte=cutoff
                ).order_by('-composite_score')[:10]

                results['sections']['dreams'] = {
                    'count': dreams.count(),
                    'items': [{'title': d.title[:50], 'score': float(d.composite_score)} for d in dreams[:5]]
                }
                summary_lines.append(f"💭 **Dreams:** {dreams.count()} creative ideas")

            # Spider data
            if 'spider_data' in include_sections:
                # Check for project-related spider data via tags or topics
                project_keywords = project.project_name.lower().split()
                spider_count = SpiderData.objects.filter(
                    created_at__gte=cutoff
                ).count()  # Simplified - would need proper project linking

                results['sections']['spider_data'] = {
                    'count': spider_count,
                    'note': 'Spider data related to project topics'
                }
                summary_lines.append(f"🕷️ **Spider Data:** {spider_count} recent items")

            # Recommendations
            if 'recommendations' in include_sections:
                recommendations = []
                if results['sections'].get('dreams', {}).get('count', 0) > 5:
                    recommendations.append("Consider reviewing high-score dreams for actionable ideas")
                if results['sections'].get('conversations', {}).get('count', 0) < 3:
                    recommendations.append("Trigger more agent conversations to generate insights")
                if results['sections'].get('learnings', {}).get('count', 0) > 20:
                    recommendations.append("Rich knowledge base - consider synthesizing key learnings")

                results['sections']['recommendations'] = recommendations
                if recommendations:
                    summary_lines.append(f"\n💡 **Recommendations:**")
                    for rec in recommendations[:3]:
                        summary_lines.append(f"  - {rec}")

            results['summary'] = '\n'.join(summary_lines)

            return {
                'success': True,
                **results
            }

        except Exception as e:
            logger.error(f"Error analyzing project intelligence: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # Session 579: ThinkingAgent/System Insights Tools
    # =========================================================================

    def _query_tracked_concerns(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query the system's tracked concerns and their resolution status.
        Returns concerns identified by ThinkingAgent with status, severity, and resolution.
        """
        try:
            from core.models_unified_system import TrackedConcern

            status_filter = arguments.get('status', 'all')
            severity_filter = arguments.get('severity', 'all')
            limit = min(arguments.get('limit', 20), 50)  # Cap at 50

            # Build query
            concerns = TrackedConcern.objects.all()

            if status_filter != 'all':
                concerns = concerns.filter(status=status_filter)

            if severity_filter != 'all':
                concerns = concerns.filter(severity=severity_filter)

            # Order by severity (high first), then by updated_at
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            concerns = concerns.order_by('-updated_at')[:limit]

            # Build summary
            status_counts = {
                'in_progress': TrackedConcern.objects.filter(status='in_progress').count(),
                'resolved': TrackedConcern.objects.filter(status='resolved').count(),
                'pending': TrackedConcern.objects.filter(status='pending').count()
            }

            concern_list = []
            for c in concerns:
                status_icon = '✅' if c.status == 'resolved' else '🔄' if c.status == 'in_progress' else '⏳'
                # Get action count (ManyToMany)
                actions_count = c.actions_taken.count()
                concern_list.append({
                    'id': c.id,
                    'status_icon': status_icon,
                    'status': c.status,
                    'severity': c.severity,
                    'category': c.category,
                    'concern': c.concern_text[:200] + ('...' if len(c.concern_text) > 200 else ''),
                    'times_detected': c.times_detected,
                    'verification_metric': c.verification_metric or 'manual',
                    'resolution_notes': c.resolution_notes[:150] if c.resolution_notes else None,
                    'actions_taken_count': actions_count,
                    'updated_at': c.updated_at.isoformat()
                })

            # Build summary message
            summary_lines = [
                f"## Tracked Concerns Overview",
                f"",
                f"**Total:** {sum(status_counts.values())} concerns",
                f"- 🔄 In Progress: {status_counts['in_progress']}",
                f"- ✅ Resolved: {status_counts['resolved']}",
                f"- ⏳ Pending: {status_counts['pending']}",
                f""
            ]

            if status_counts['in_progress'] > 0:
                summary_lines.append("### Active Concerns (In Progress)")
                in_progress = [c for c in concern_list if c['status'] == 'in_progress']
                for c in in_progress[:5]:
                    summary_lines.append(f"- **[{c['severity'].upper()}]** {c['concern'][:80]}...")

            return {
                'success': True,
                'status_counts': status_counts,
                'concerns': concern_list,
                'summary': '\n'.join(summary_lines),
                'filters_applied': {
                    'status': status_filter,
                    'severity': severity_filter,
                    'limit': limit
                }
            }

        except Exception as e:
            logger.error(f"Error querying tracked concerns: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_system_insights(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the latest System Insights reports from the ThinkingAgent.
        Returns the most recent report(s) with patterns, concerns, and opportunities.
        """
        try:
            from django.utils import timezone
            from core.models_unified_system import SelfBlog

            limit = min(arguments.get('limit', 1), 5)  # Cap at 5

            # Get System Insights reports
            reports = SelfBlog.objects.filter(
                title__icontains='System Insights'
            ).order_by('-created_at')[:limit]

            if not reports.exists():
                return {
                    'success': True,
                    'reports': [],
                    'summary': "No System Insights reports found. The ThinkingAgent may not have run yet."
                }

            report_list = []
            for r in reports:
                hours_ago = (timezone.now() - r.created_at).total_seconds() / 3600
                report_list.append({
                    'id': r.id,
                    'title': r.title,
                    'created_at': r.created_at.isoformat(),
                    'hours_ago': round(hours_ago, 1),
                    'content': r.full_text[:3000] if r.full_text else 'No content',  # Truncate for response
                    'stats_snapshot': r.stats_snapshot if hasattr(r, 'stats_snapshot') else None
                })

            # Summary for the most recent report
            latest = report_list[0]
            summary_lines = [
                f"## Latest System Insights",
                f"",
                f"**Generated:** {latest['hours_ago']} hours ago",
                f"",
                f"---",
                f""
            ]

            # Include the full content of the latest report
            if latest['content']:
                summary_lines.append(latest['content'][:2500])

            return {
                'success': True,
                'reports': report_list,
                'total_reports': SelfBlog.objects.filter(title__icontains='System Insights').count(),
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error getting system insights: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # Session 579: Phase 7 Tools - Advisors and Revenue
    # =========================================================================

    def _get_advisor_consultation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query the legendary advisors for insights and wisdom.
        Returns advisor information and their recent insights.
        """
        try:
            from django.utils import timezone
            from datetime import timedelta
            from core.models_unified_system import Advisor, AdvisorInsight

            advisor_name = arguments.get('advisor_name')
            category = arguments.get('category', 'all')
            topic = arguments.get('topic')
            limit = min(arguments.get('limit', 10), 25)

            # Get advisors
            advisors = Advisor.objects.filter(is_active=True)

            if advisor_name:
                advisors = advisors.filter(name__icontains=advisor_name)

            if category and category != 'all':
                advisors = advisors.filter(category__icontains=category)

            advisors = advisors.order_by('-influence_score')[:limit]

            if not advisors.exists():
                return {
                    'success': True,
                    'advisors': [],
                    'summary': "No advisors found matching your criteria."
                }

            advisor_list = []
            for a in advisors:
                # Get recent insights from this advisor
                insights = AdvisorInsight.objects.filter(advisor=a).order_by('-created_at')[:3]

                advisor_info = {
                    'id': str(a.id),
                    'name': a.name,
                    'title': a.title,
                    'category': a.category,
                    'expertise': a.expertise[:200] if a.expertise else '',
                    'influence_score': a.influence_score,
                    'total_consultations': a.total_consultations,
                    'wisdom': a.wisdom if a.wisdom else {},
                    'recent_insights': [
                        {
                            'content': i.content[:200],
                            'category': i.category,
                            'confidence': i.confidence,
                            'is_actionable': i.is_actionable
                        } for i in insights
                    ]
                }
                advisor_list.append(advisor_info)

            # Build summary
            summary_lines = [
                f"## Advisor Consultation",
                f"",
                f"**Found:** {len(advisor_list)} advisor(s)",
                f""
            ]

            for a in advisor_list[:5]:
                summary_lines.append(f"### {a['name']}")
                summary_lines.append(f"*{a['title']}* (Influence: {a['influence_score']}/100)")
                summary_lines.append(f"")
                # Handle wisdom - might be string or dict
                wisdom = a.get('wisdom', {})
                if isinstance(wisdom, dict) and wisdom.get('philosophy'):
                    summary_lines.append(f"**Philosophy:** {wisdom['philosophy'][:150]}...")
                elif isinstance(wisdom, str) and wisdom:
                    summary_lines.append(f"**Philosophy:** {wisdom[:150]}...")
                if a['recent_insights']:
                    summary_lines.append(f"**Recent Insight:** {a['recent_insights'][0]['content'][:150]}...")
                summary_lines.append(f"")

            return {
                'success': True,
                'advisors': advisor_list,
                'total_advisors': Advisor.objects.filter(is_active=True).count(),
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error getting advisor consultation: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _query_revenue_metrics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query revenue metrics, earnings, and financial performance.
        Returns revenue by source, status, and time period.
        """
        try:
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Sum, Count, Avg
            from decimal import Decimal
            from core.models_unified_system import Revenue, Opportunity

            time_period = arguments.get('time_period', '30d')
            source_type = arguments.get('source_type')
            status = arguments.get('status', 'all')
            include_opportunities = arguments.get('include_opportunities', True)

            # Calculate cutoff
            now = timezone.now()
            period_map = {
                '24h': timedelta(hours=24),
                '7d': timedelta(days=7),
                '30d': timedelta(days=30),
                '90d': timedelta(days=90),
                'all': timedelta(days=3650)  # ~10 years
            }
            cutoff = now - period_map.get(time_period, timedelta(days=30))

            # Query revenue
            revenue_qs = Revenue.objects.filter(created_at__gte=cutoff)

            if source_type:
                revenue_qs = revenue_qs.filter(source_type__icontains=source_type)

            if status and status != 'all':
                revenue_qs = revenue_qs.filter(status=status)

            # Aggregate metrics
            total_revenue = revenue_qs.aggregate(
                total=Sum('amount'),
                count=Count('id'),
                avg=Avg('amount')
            )

            # By status
            by_status = revenue_qs.values('status').annotate(
                total=Sum('amount'),
                count=Count('id')
            )

            # By source type
            by_source = revenue_qs.values('source_type').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')[:10]

            # Recent transactions
            recent = revenue_qs.order_by('-created_at')[:5]
            recent_list = [
                {
                    'amount': float(r.amount),
                    'source_type': r.source_type,
                    'status': r.status,
                    'description': r.description[:100] if r.description else '',
                    'created_at': r.created_at.isoformat()
                } for r in recent
            ]

            results = {
                'success': True,
                'time_period': time_period,
                'total_revenue': float(total_revenue['total'] or 0),
                'transaction_count': total_revenue['count'] or 0,
                'average_transaction': float(total_revenue['avg'] or 0),
                'by_status': {s['status']: {'total': float(s['total'] or 0), 'count': s['count']} for s in by_status},
                'by_source': {s['source_type']: {'total': float(s['total'] or 0), 'count': s['count']} for s in by_source},
                'recent_transactions': recent_list
            }

            # Include opportunities if requested
            if include_opportunities:
                opp_qs = Opportunity.objects.filter(
                    created_at__gte=cutoff,
                    status='active'
                )
                potential = opp_qs.aggregate(
                    total=Sum('potential_revenue'),
                    count=Count('id')
                )
                results['opportunities'] = {
                    'potential_revenue': float(potential['total'] or 0),
                    'active_count': potential['count'] or 0
                }

            # Build summary
            summary_lines = [
                f"## Revenue Metrics ({time_period})",
                f"",
                f"**Total Revenue:** ${results['total_revenue']:,.2f}",
                f"**Transactions:** {results['transaction_count']}",
                f"**Average:** ${results['average_transaction']:,.2f}",
                f""
            ]

            if results.get('by_status'):
                summary_lines.append("### By Status")
                for status, data in results['by_status'].items():
                    summary_lines.append(f"- **{status.title()}:** ${data['total']:,.2f} ({data['count']} transactions)")
                summary_lines.append("")

            if results.get('by_source'):
                summary_lines.append("### By Source")
                for source, data in list(results['by_source'].items())[:5]:
                    summary_lines.append(f"- **{source.title()}:** ${data['total']:,.2f}")
                summary_lines.append("")

            if include_opportunities and results.get('opportunities'):
                opp = results['opportunities']
                summary_lines.append("### Pipeline")
                summary_lines.append(f"- **Active Opportunities:** {opp['active_count']}")
                summary_lines.append(f"- **Potential Revenue:** ${opp['potential_revenue']:,.2f}")

            results['summary'] = '\n'.join(summary_lines)

            return results

        except Exception as e:
            logger.error(f"Error querying revenue metrics: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # Session 580: Phase 8 Tools - High-Impact Expansion
    # =========================================================================

    def _manage_proactive_alerts(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage proactive alerts, notifications, and automations.
        """
        try:
            import requests
            action = arguments.get('action', 'list_alerts')
            base_url = 'http://localhost:8000/api/proactive'

            if action == 'list_alerts':
                try:
                    response = requests.get(f'{base_url}/alerts/', timeout=10)
                    if response.status_code == 200:
                        alerts = response.json()
                        return {
                            'success': True,
                            'alerts': alerts[:20] if isinstance(alerts, list) else alerts.get('alerts', [])[:20],
                            'summary': f"Found {len(alerts) if isinstance(alerts, list) else len(alerts.get('alerts', []))} alerts"
                        }
                except:
                    pass
                return {'success': True, 'alerts': [], 'summary': 'No alerts configured'}

            elif action == 'list_notifications':
                try:
                    response = requests.get(f'{base_url}/notifications/', timeout=10)
                    if response.status_code == 200:
                        notifications = response.json()
                        return {
                            'success': True,
                            'notifications': notifications[:20] if isinstance(notifications, list) else notifications.get('notifications', [])[:20],
                            'summary': f"Found notifications"
                        }
                except:
                    pass
                return {'success': True, 'notifications': [], 'summary': 'No notifications'}

            elif action == 'list_automations':
                try:
                    response = requests.get(f'{base_url}/automations/', timeout=10)
                    if response.status_code == 200:
                        automations = response.json()
                        return {
                            'success': True,
                            'automations': automations[:20] if isinstance(automations, list) else automations.get('automations', [])[:20],
                            'summary': f"Found automations"
                        }
                except:
                    pass
                return {'success': True, 'automations': [], 'summary': 'No automations configured'}

            elif action == 'create_alert':
                alert_data = {
                    'alert_type': arguments.get('alert_type', 'custom'),
                    'condition': arguments.get('condition', ''),
                    'is_active': True
                }
                response = requests.post(f'{base_url}/alerts/create/', json=alert_data, timeout=10)
                return {
                    'success': response.status_code == 200 or response.status_code == 201,
                    'message': 'Alert created' if response.status_code in [200, 201] else response.text
                }

            elif action == 'toggle_alert':
                alert_id = arguments.get('alert_id')
                if alert_id:
                    response = requests.post(f'{base_url}/alerts/{alert_id}/toggle/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Alert toggled' if response.status_code == 200 else response.text
                    }

            elif action == 'run_check':
                response = requests.post(f'{base_url}/check/', timeout=30)
                return {
                    'success': response.status_code == 200,
                    'message': 'Proactive check completed' if response.status_code == 200 else response.text,
                    'data': response.json() if response.status_code == 200 else {}
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing proactive alerts: {e}")
            return {'success': False, 'error': str(e)}

    def _query_learning_progress(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query agent learning progress, evolution metrics, and training status.
        """
        try:
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Count, Avg

            agent_name = arguments.get('agent_name')
            metric_type = arguments.get('metric_type', 'all')
            time_period = arguments.get('time_period', '7d')

            # Calculate cutoff
            now = timezone.now()
            period_map = {'24h': timedelta(hours=24), '7d': timedelta(days=7), '30d': timedelta(days=30)}
            cutoff = now - period_map.get(time_period, timedelta(days=7))

            results = {'success': True, 'time_period': time_period}

            # Get learning stats from AgentLearning model
            if metric_type in ['learning_stats', 'all']:
                from core.models_unified_system import AgentLearning
                learning_qs = AgentLearning.objects.filter(created_at__gte=cutoff)
                if agent_name:
                    # Filter by teacher or student agent
                    from django.db.models import Q
                    learning_qs = learning_qs.filter(
                        Q(teacher_agent__name__icontains=agent_name) |
                        Q(student_agent__name__icontains=agent_name)
                    )

                stats = learning_qs.aggregate(
                    total=Count('id'),
                    avg_effectiveness=Avg('effectiveness_after')
                )
                results['learning_stats'] = {
                    'total_learnings': stats['total'] or 0,
                    'avg_effectiveness': round(float(stats['avg_effectiveness'] or 0), 2)
                }

            # Get evolution metrics
            if metric_type in ['evolution', 'all']:
                from core.models_unified_system import Agent
                agents = Agent.objects.filter(is_active=True)
                if agent_name:
                    agents = agents.filter(name__icontains=agent_name)

                agent_data = []
                for agent in agents[:10]:
                    agent_data.append({
                        'name': agent.name,
                        'specialization': agent.specialization,
                        'effectiveness_score': agent.effectiveness_score,
                        'total_executions': agent.total_executions
                    })
                results['evolution'] = agent_data

            # Get recent interactions
            if metric_type in ['interactions', 'all']:
                from core.models_unified_system import AgentExecution
                exec_qs = AgentExecution.objects.filter(created_at__gte=cutoff)
                if agent_name:
                    exec_qs = exec_qs.filter(agent__name__icontains=agent_name)

                exec_stats = exec_qs.aggregate(
                    total=Count('id'),
                    avg_time=Avg('execution_time_ms')
                )
                results['interactions'] = {
                    'total_executions': exec_stats['total'] or 0,
                    'avg_execution_time_ms': round(float(exec_stats['avg_time'] or 0), 0)
                }

            # Build summary
            summary_lines = [f"## Learning Progress ({time_period})", ""]
            if results.get('learning_stats'):
                ls = results['learning_stats']
                summary_lines.append(f"**Total Learnings:** {ls['total_learnings']}")
                summary_lines.append(f"**Avg Effectiveness:** {ls['avg_effectiveness']}")
            if results.get('interactions'):
                i = results['interactions']
                summary_lines.append(f"**Executions:** {i['total_executions']}")
            if results.get('evolution'):
                summary_lines.append(f"**Active Agents:** {len(results['evolution'])}")

            results['summary'] = '\n'.join(summary_lines)
            return results

        except Exception as e:
            logger.error(f"Error querying learning progress: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_team(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage agent teams, roles, and team workflows.
        """
        try:
            import requests
            action = arguments.get('action', 'list_teams')
            base_url = 'http://localhost:8000/api/teams'

            if action == 'list_teams':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        teams = response.json()
                        team_list = teams if isinstance(teams, list) else teams.get('teams', [])
                        return {
                            'success': True,
                            'teams': team_list[:20],
                            'total': len(team_list),
                            'summary': f"Found {len(team_list)} teams"
                        }
                except:
                    pass
                # Fallback - query Team model directly
                from core.models_unified_system import AgentTeam
                teams = AgentTeam.objects.all()[:20]
                return {
                    'success': True,
                    'teams': [{'id': str(t.id), 'name': t.name} for t in teams],
                    'total': AgentTeam.objects.count(),
                    'summary': f"Found {AgentTeam.objects.count()} teams"
                }

            elif action == 'team_stats':
                try:
                    response = requests.get(f'{base_url}/stats/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'stats': response.json()}
                except:
                    pass
                from core.models_unified_system import AgentTeam
                return {'success': True, 'stats': {'total_teams': AgentTeam.objects.count()}}

            elif action == 'list_roles':
                try:
                    response = requests.get(f'{base_url}/roles/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'roles': response.json()}
                except:
                    pass
                return {'success': True, 'roles': ['lead', 'member', 'specialist', 'coordinator']}

            elif action == 'get_team':
                team_id = arguments.get('team_id')
                if team_id:
                    response = requests.get(f'{base_url}/{team_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'team': response.json()}

            elif action == 'create_team':
                team_name = arguments.get('team_name', 'New Team')
                response = requests.post(f'{base_url}/create/', json={'name': team_name}, timeout=10)
                return {
                    'success': response.status_code in [200, 201],
                    'message': f'Team "{team_name}" created' if response.status_code in [200, 201] else response.text
                }

            elif action == 'add_member':
                team_id = arguments.get('team_id')
                agent_id = arguments.get('agent_id')
                role = arguments.get('role', 'member')
                if team_id and agent_id:
                    response = requests.post(
                        f'{base_url}/{team_id}/members/',
                        json={'agent_id': agent_id, 'role': role},
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Member added' if response.status_code == 200 else response.text
                    }

            return {'success': False, 'error': f'Unknown action or missing params: {action}'}

        except Exception as e:
            logger.error(f"Error managing team: {e}")
            return {'success': False, 'error': str(e)}

    def _generate_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate videos using AI video agents.
        """
        try:
            prompt = arguments.get('prompt', '')
            video_type = arguments.get('video_type', 'text_to_video')
            duration = arguments.get('duration', 30)
            style = arguments.get('style', 'cinematic')
            aspect_ratio = arguments.get('aspect_ratio', '16:9')

            if not prompt:
                return {'success': False, 'error': 'Prompt is required'}

            # Delegate to VideoAgent
            result = self.router.route(
                agent_name='VideoAgent',
                task=f"Create a {video_type} video: {prompt}. Style: {style}, Duration: {duration}s, Aspect: {aspect_ratio}",
                context={
                    'video_type': video_type,
                    'duration': duration,
                    'style': style,
                    'aspect_ratio': aspect_ratio
                }
            )

            return {
                'success': result.success,
                'message': result.message if result.success else result.error,
                'data': result.data if result.success else {},
                'summary': f"Video generation {'started' if result.success else 'failed'}: {prompt[:50]}..."
            }

        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_distribution(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage content distribution across platforms.
        """
        try:
            import requests
            action = arguments.get('action', 'list_platforms')
            base_url = 'http://localhost:8000/api/distribution'

            if action == 'list_platforms':
                try:
                    response = requests.get(f'{base_url}/platforms/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'platforms': response.json()}
                except:
                    pass
                # Fallback - return default platforms
                return {
                    'success': True,
                    'platforms': ['twitter', 'linkedin', 'facebook', 'instagram', 'youtube', 'tiktok'],
                    'summary': 'Available platforms (default list)'
                }

            elif action == 'list_distributions':
                try:
                    response = requests.get(f'{base_url}/content/', timeout=10)
                    if response.status_code == 200:
                        dist = response.json()
                        return {
                            'success': True,
                            'distributions': dist[:20] if isinstance(dist, list) else dist.get('distributions', [])[:20],
                            'summary': f"Found distributions"
                        }
                except:
                    pass
                return {'success': True, 'distributions': [], 'summary': 'No distributions found'}

            elif action == 'stats':
                try:
                    response = requests.get(f'{base_url}/stats/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'stats': response.json()}
                except:
                    pass
                return {'success': True, 'stats': {'message': 'Stats not available'}}

            elif action == 'create_distribution':
                content_id = arguments.get('content_id')
                platform = arguments.get('platform', 'all')
                if content_id:
                    response = requests.post(
                        f'{base_url}/content/create/',
                        json={'content_id': content_id, 'platform': platform},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': 'Distribution created' if response.status_code in [200, 201] else response.text
                    }

            elif action == 'schedule':
                content_id = arguments.get('content_id')
                scheduled_time = arguments.get('scheduled_time')
                platform = arguments.get('platform', 'all')
                if content_id and scheduled_time:
                    response = requests.post(
                        f'{base_url}/schedule/',
                        json={'content_id': content_id, 'platform': platform, 'scheduled_time': scheduled_time},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': f'Scheduled for {scheduled_time}' if response.status_code in [200, 201] else response.text
                    }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing distribution: {e}")
            return {'success': False, 'error': str(e)}

    def _query_analytics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query system analytics, usage metrics, and performance data.
        """
        try:
            import requests
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Count, Sum, Avg

            report_type = arguments.get('report_type', 'overview')
            time_period = arguments.get('time_period', '7d')
            include_trends = arguments.get('include_trends', True)

            now = timezone.now()
            period_map = {'24h': timedelta(hours=24), '7d': timedelta(days=7), '30d': timedelta(days=30), '90d': timedelta(days=90)}
            cutoff = now - period_map.get(time_period, timedelta(days=7))

            results = {'success': True, 'report_type': report_type, 'time_period': time_period}

            if report_type in ['overview', 'all']:
                # Try internal API first
                try:
                    response = requests.get('http://localhost:8000/api/analytics/overview/', timeout=10)
                    if response.status_code == 200:
                        results['overview'] = response.json()
                except:
                    pass

                # Fallback to direct DB queries
                from core.models_unified_system import Agent, AgentExecution

                results['overview'] = results.get('overview', {})
                results['overview'].update({
                    'total_agents': Agent.objects.filter(is_active=True).count(),
                    'executions': AgentExecution.objects.filter(created_at__gte=cutoff).count()
                })

            if report_type in ['agents', 'all']:
                from core.models_unified_system import Agent, AgentExecution
                exec_stats = AgentExecution.objects.filter(created_at__gte=cutoff).values('agent__name').annotate(
                    count=Count('id'),
                    avg_time=Avg('execution_time_ms')
                ).order_by('-count')[:10]

                results['agent_stats'] = [
                    {'agent': s['agent__name'], 'executions': s['count'], 'avg_time_ms': round(s['avg_time'] or 0, 0)}
                    for s in exec_stats
                ]

            if report_type in ['costs', 'all']:
                try:
                    response = requests.get('http://localhost:8000/api/analytics/cost-breakdown/', timeout=10)
                    if response.status_code == 200:
                        results['costs'] = response.json()
                except:
                    results['costs'] = {'message': 'Cost data not available'}

            # Build summary
            summary_lines = [f"## Analytics Report ({time_period})", ""]
            if results.get('overview'):
                o = results['overview']
                summary_lines.append(f"**Agents:** {o.get('total_agents', 'N/A')}")
                summary_lines.append(f"**Executions:** {o.get('executions', 'N/A')}")
                summary_lines.append(f"**Content:** {o.get('content_generated', 'N/A')}")

            results['summary'] = '\n'.join(summary_lines)
            return results

        except Exception as e:
            logger.error(f"Error querying analytics: {e}")
            return {'success': False, 'error': str(e)}

    def _time_travel_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Access agent memory time-travel capabilities.
        """
        try:
            import requests
            action = arguments.get('action', 'list_snapshots')
            agent_name = arguments.get('agent_name')
            base_url = 'http://localhost:8000/api/time-travel'

            if action == 'list_snapshots':
                url = f'{base_url}/snapshots/'
                if agent_name:
                    url += f'?agent={agent_name}'
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    snapshots = response.json()
                    return {
                        'success': True,
                        'snapshots': snapshots[:20] if isinstance(snapshots, list) else snapshots.get('snapshots', [])[:20],
                        'summary': f"Found memory snapshots"
                    }

            elif action == 'get_snapshot':
                snapshot_date = arguments.get('snapshot_date')
                if agent_name and snapshot_date:
                    response = requests.get(f'{base_url}/snapshots/{agent_name}/{snapshot_date}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'snapshot': response.json()}

            elif action == 'timeline':
                if agent_name:
                    response = requests.get(f'{base_url}/timeline/{agent_name}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'timeline': response.json()}

            elif action == 'compare':
                compare_dates = arguments.get('compare_dates', [])
                if agent_name and len(compare_dates) >= 2:
                    response = requests.post(
                        f'{base_url}/compare/',
                        json={'agent': agent_name, 'date1': compare_dates[0], 'date2': compare_dates[1]},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, 'comparison': response.json()}

            # Fallback to direct model access
            from core.models_unified_system import AgentMemory
            # Session 810: Defer embedding fields to reduce egress costs
            memories = AgentMemory.objects.defer('embedding').all().order_by('-created_at')[:20]
            return {
                'success': True,
                'snapshots': [
                    {'agent': m.agent.name if m.agent else 'Unknown', 'created': str(m.created_at), 'type': m.memory_type}
                    for m in memories
                ],
                'summary': f"Found {len(memories)} memory records"
            }

        except Exception as e:
            logger.error(f"Error accessing time travel memory: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_memory_palace(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage agent memory palace and memory organization.
        """
        try:
            import requests
            from django.db.models import Count

            action = arguments.get('action', 'overview')
            agent_name = arguments.get('agent_name')
            query = arguments.get('query', '')
            limit = min(arguments.get('limit', 10), 50)
            base_url = 'http://localhost:8000/api/memory-palace'

            if action == 'overview':
                # Get memory palace overview
                from core.models_unified_system import AgentMemory, Agent
                memory_stats = AgentMemory.objects.values('memory_type').annotate(count=Count('id')).order_by('-count')
                total_memories = AgentMemory.objects.count()

                return {
                    'success': True,
                    'overview': {
                        'total_memories': total_memories,
                        'by_type': {s['memory_type']: s['count'] for s in memory_stats}
                    },
                    'summary': f"Memory Palace: {total_memories} memories across {len(memory_stats)} types"
                }

            elif action == 'search':
                if query:
                    from core.models_unified_system import AgentMemory
                    # Session 810: Defer embedding fields to reduce egress costs
                    memories = AgentMemory.objects.defer('embedding').filter(content__icontains=query).order_by('-created_at')[:limit]
                    return {
                        'success': True,
                        'results': [
                            {'agent': m.agent.name if m.agent else 'Unknown', 'content': m.content[:200], 'type': m.memory_type}
                            for m in memories
                        ],
                        'summary': f"Found {len(memories)} memories matching '{query}'"
                    }

            elif action == 'recent':
                from core.models_unified_system import AgentMemory
                # Session 810: Defer embedding fields to reduce egress costs
                memories = AgentMemory.objects.defer('embedding').all().order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'memories': [
                        {'agent': m.agent.name if m.agent else 'Unknown', 'content': m.content[:200], 'type': m.memory_type, 'created': str(m.created_at)}
                        for m in memories
                    ],
                    'summary': f"Last {len(memories)} memories"
                }

            elif action == 'important':
                from core.models_unified_system import AgentMemory
                # Session 810: Defer embedding fields to reduce egress costs
                memories = AgentMemory.objects.defer('embedding').filter(importance__gte=0.7).order_by('-importance', '-created_at')[:limit]
                return {
                    'success': True,
                    'memories': [
                        {'agent': m.agent.name if m.agent else 'Unknown', 'content': m.content[:200], 'importance': m.importance}
                        for m in memories
                    ],
                    'summary': f"Found {len(memories)} high-importance memories"
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing memory palace: {e}")
            return {'success': False, 'error': str(e)}

    def _run_diagnostics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run system diagnostics and health checks.
        """
        try:
            import requests
            diagnostic_type = arguments.get('diagnostic_type', 'quick')
            include_details = arguments.get('include_details', False)

            results = {'success': True, 'diagnostic_type': diagnostic_type, 'checks': {}}

            # Quick health check
            if diagnostic_type in ['quick', 'full']:
                try:
                    response = requests.get('http://localhost:8000/health/ping/', timeout=5)
                    results['checks']['web_server'] = {'status': 'healthy' if response.status_code == 200 else 'unhealthy'}
                except:
                    results['checks']['web_server'] = {'status': 'unreachable'}

            # Database check
            if diagnostic_type in ['database', 'full']:
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                    results['checks']['database'] = {'status': 'healthy'}
                except Exception as e:
                    results['checks']['database'] = {'status': 'unhealthy', 'error': str(e)}

            # Agent check
            if diagnostic_type in ['agents', 'full']:
                from core.models_unified_system import Agent
                active_agents = Agent.objects.filter(is_active=True).count()
                results['checks']['agents'] = {'status': 'healthy', 'active_count': active_agents}

            # Spider check
            if diagnostic_type in ['spiders', 'full']:
                try:
                    response = requests.get('http://localhost:8000/api/diagnostics/test-spiders/', timeout=30)
                    if response.status_code == 200:
                        results['checks']['spiders'] = response.json()
                    else:
                        # Fallback
                        from ai_core.spiders.spider_registry import SpiderRegistry
                        results['checks']['spiders'] = {'status': 'available', 'count': len(SpiderRegistry._spiders)}
                except:
                    from ai_core.spiders.spider_registry import SpiderRegistry
                    results['checks']['spiders'] = {'status': 'available', 'count': len(SpiderRegistry._spiders)}

            # Celery check
            if diagnostic_type in ['celery', 'full']:
                try:
                    from core.celery import app
                    inspect = app.control.inspect()
                    active = inspect.active()
                    results['checks']['celery'] = {
                        'status': 'healthy' if active else 'no_workers',
                        'workers': len(active) if active else 0
                    }
                except Exception as e:
                    results['checks']['celery'] = {'status': 'error', 'error': str(e)}

            # Services check
            if diagnostic_type in ['services', 'full']:
                services_ok = 0
                services_list = ['redis', 'postgres']
                for svc in services_list:
                    try:
                        if svc == 'redis':
                            import redis
                            r = redis.Redis()
                            r.ping()
                            services_ok += 1
                    except:
                        pass
                results['checks']['services'] = {'healthy': services_ok, 'total': len(services_list)}

            # Build summary
            healthy_count = sum(1 for c in results['checks'].values() if c.get('status') == 'healthy')
            total_checks = len(results['checks'])
            results['summary'] = f"## Diagnostics ({diagnostic_type})\n\n**Health:** {healthy_count}/{total_checks} checks passed"

            for name, check in results['checks'].items():
                status_icon = "✅" if check.get('status') == 'healthy' else "❌"
                results['summary'] += f"\n- {status_icon} **{name}:** {check.get('status', 'unknown')}"

            return results

        except Exception as e:
            logger.error(f"Error running diagnostics: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_collaboration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage agent collaborations and partnerships.
        """
        try:
            import requests
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Count

            action = arguments.get('action', 'stats')
            time_period = arguments.get('time_period', '7d')
            base_url = 'http://localhost:8000/api/collaboration'

            now = timezone.now()
            period_map = {'24h': timedelta(hours=24), '7d': timedelta(days=7), '30d': timedelta(days=30)}
            cutoff = now - period_map.get(time_period, timedelta(days=7))

            if action == 'stats':
                try:
                    response = requests.get(f'{base_url}/stats/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'stats': response.json()}
                except:
                    pass

                # Fallback to direct query
                from core.models_unified_system import Collaboration
                collab_count = Collaboration.objects.filter(created_at__gte=cutoff).count()
                return {
                    'success': True,
                    'stats': {'collaborations': collab_count, 'period': time_period},
                    'summary': f"**Collaborations ({time_period}):** {collab_count}"
                }

            elif action == 'history':
                from core.models_unified_system import Collaboration
                collabs = Collaboration.objects.filter(created_at__gte=cutoff).order_by('-created_at')[:20]
                return {
                    'success': True,
                    'history': [
                        {
                            'id': str(c.id),
                            'lead_agent': c.lead_agent.name if c.lead_agent else 'Unknown',
                            'objective': c.objective[:100] if c.objective else '',
                            'status': c.status,
                            'created': str(c.created_at)
                        }
                        for c in collabs
                    ],
                    'summary': f"Found {len(collabs)} collaborations"
                }

            elif action == 'active':
                from core.models_unified_system import Collaboration
                active = Collaboration.objects.filter(status='active').order_by('-created_at')[:20]
                return {
                    'success': True,
                    'active': [
                        {'id': str(c.id), 'lead_agent': c.lead_agent.name if c.lead_agent else 'Unknown', 'objective': c.objective[:50]}
                        for c in active
                    ],
                    'summary': f"Found {len(active)} active collaborations"
                }

            elif action == 'network':
                try:
                    response = requests.get(f'{base_url}/network/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'network': response.json()}
                except:
                    return {'success': True, 'network': {'message': 'Network visualization not available via API'}}

            elif action == 'start':
                agent_names = arguments.get('agent_names', [])
                if len(agent_names) >= 2:
                    response = requests.post(
                        f'{base_url}/request/',
                        json={'initiator': agent_names[0], 'collaborator': agent_names[1]},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': 'Collaboration started' if response.status_code in [200, 201] else response.text
                    }

            elif action == 'performance':
                try:
                    response = requests.get(f'{base_url}/performance/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'performance': response.json()}
                except:
                    pass

                from core.models_unified_system import Collaboration
                perf = Collaboration.objects.filter(
                    created_at__gte=cutoff,
                    status='completed'
                ).count()
                return {
                    'success': True,
                    'performance': {'completed': perf, 'period': time_period},
                    'summary': f"**Completed collaborations ({time_period}):** {perf}"
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing collaboration: {e}")
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # Session 580: Phase 9 Tools - Deep System Coverage
    # =========================================================================

    def _manage_project(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage partnership projects - list, create, update, export.
        """
        try:
            import requests
            action = arguments.get('action', 'list')
            base_url = 'http://localhost:8000/api/projects'

            if action == 'list':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        projects = response.json()
                        project_list = projects if isinstance(projects, list) else projects.get('projects', [])
                        return {
                            'success': True,
                            'projects': project_list[:20],
                            'total': len(project_list),
                            'summary': f"Found {len(project_list)} projects"
                        }
                except:
                    pass
                # Fallback to direct query
                from core.models_partnership import PartnershipProject
                projects = PartnershipProject.objects.all().order_by('-created_at')[:20]
                return {
                    'success': True,
                    'projects': [{'id': str(p.id), 'name': p.name, 'status': p.status} for p in projects],
                    'total': PartnershipProject.objects.count(),
                    'summary': f"Found {PartnershipProject.objects.count()} projects"
                }

            elif action == 'get':
                project_id = arguments.get('project_id')
                if project_id:
                    try:
                        response = requests.get(f'{base_url}/{project_id}/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'project': response.json()}
                    except:
                        pass
                    from core.models_partnership import PartnershipProject
                    try:
                        p = PartnershipProject.objects.get(id=project_id)
                        return {'success': True, 'project': {'id': str(p.id), 'name': p.name, 'description': p.description, 'status': p.status}}
                    except:
                        return {'success': False, 'error': 'Project not found'}

            elif action == 'create':
                name = arguments.get('name', 'New Project')
                description = arguments.get('description', '')
                try:
                    response = requests.post(f'{base_url}/create/', json={'name': name, 'description': description}, timeout=10)
                    return {
                        'success': response.status_code in [200, 201],
                        'message': f'Project "{name}" created' if response.status_code in [200, 201] else response.text
                    }
                except:
                    return {'success': False, 'error': 'Could not create project'}

            elif action == 'get_intelligence':
                project_id = arguments.get('project_id')
                if project_id:
                    try:
                        response = requests.get(f'{base_url}/{project_id}/intelligence/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'intelligence': response.json()}
                    except:
                        pass
                return {'success': True, 'intelligence': {'message': 'Intelligence not available'}}

            elif action == 'export_pdf':
                project_id = arguments.get('project_id')
                if project_id:
                    return {
                        'success': True,
                        'message': f'PDF export available at /api/projects/{project_id}/export-comprehensive-pdf/',
                        'export_url': f'/api/projects/{project_id}/export-comprehensive-pdf/'
                    }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing project: {e}")
            return {'success': False, 'error': str(e)}

    def _query_legal(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query legal case files, litigation documents, and case context.
        """
        try:
            import requests
            action = arguments.get('action', 'list_cases')
            base_url = 'http://localhost:8000/api/legal'

            if action == 'list_cases':
                try:
                    response = requests.get(f'{base_url}/cases/', timeout=10)
                    if response.status_code == 200:
                        cases = response.json()
                        case_list = cases if isinstance(cases, list) else cases.get('cases', [])
                        return {
                            'success': True,
                            'cases': case_list[:20],
                            'summary': f"Found {len(case_list)} cases"
                        }
                except:
                    pass
                # Fallback
                from core.models_legal import CaseProfile
                cases = CaseProfile.objects.all().order_by('-created_at')[:20]
                return {
                    'success': True,
                    'cases': [{'id': str(c.id), 'case_title': c.case_title, 'case_number': c.case_number, 'status': c.status} for c in cases],
                    'summary': f"Found {CaseProfile.objects.count()} cases"
                }

            elif action == 'get_case':
                case_id = arguments.get('case_id')
                if case_id:
                    try:
                        response = requests.get(f'{base_url}/cases/{case_id}/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'case': response.json()}
                    except:
                        pass
                return {'success': False, 'error': 'Case not found'}

            elif action == 'active_case':
                try:
                    response = requests.get(f'{base_url}/active-case/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'active_case': response.json()}
                except:
                    pass
                return {'success': True, 'active_case': None, 'message': 'No active case'}

            elif action == 'list_case_files':
                try:
                    response = requests.get(f'{base_url}/case-files/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'files': response.json()}
                except:
                    pass
                return {'success': True, 'files': [], 'message': 'No case files'}

            elif action == 'get_context':
                case_id = arguments.get('case_id')
                if case_id:
                    try:
                        response = requests.get(f'{base_url}/cases/{case_id}/context/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'context': response.json()}
                    except:
                        pass
                return {'success': True, 'context': {'message': 'Context not available'}}

            elif action == 'list_documents':
                case_id = arguments.get('case_id')
                if case_id:
                    try:
                        response = requests.get(f'{base_url}/litigation/{case_id}/documents/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'documents': response.json()}
                    except:
                        pass
                return {'success': True, 'documents': []}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error querying legal: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_agent_training(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage agent training, capabilities, and templates.
        """
        try:
            import requests
            from django.db.models import Avg
            action = arguments.get('action', 'list_agents')
            base_url = 'http://localhost:8000/api/training'

            if action == 'list_agents':
                try:
                    response = requests.get(f'{base_url}/agents/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'agents': response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import Agent
                agents = Agent.objects.filter(is_active=True).order_by('name')[:20]
                return {
                    'success': True,
                    'agents': [{'name': a.name, 'type': a.agent_type, 'effectiveness': a.effectiveness_score} for a in agents],
                    'summary': f"Found {Agent.objects.filter(is_active=True).count()} trainable agents"
                }

            elif action == 'get_agent':
                agent_name = arguments.get('agent_name')
                if agent_name:
                    try:
                        response = requests.get(f'{base_url}/agents/{agent_name}/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'agent': response.json()}
                    except:
                        pass
                    from core.models_unified_system import Agent
                    try:
                        a = Agent.objects.get(name__iexact=agent_name)
                        return {'success': True, 'agent': {'name': a.name, 'type': a.agent_type, 'capabilities': a.capabilities}}
                    except:
                        return {'success': False, 'error': 'Agent not found'}

            elif action == 'list_capabilities':
                try:
                    response = requests.get(f'{base_url}/capabilities/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'capabilities': response.json()}
                except:
                    pass
                return {'success': True, 'capabilities': ['research', 'writing', 'analysis', 'creation', 'editing']}

            elif action == 'list_templates':
                try:
                    response = requests.get(f'{base_url}/templates/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'templates': response.json()}
                except:
                    pass
                return {'success': True, 'templates': []}

            elif action == 'stats':
                try:
                    response = requests.get(f'{base_url}/stats/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'stats': response.json()}
                except:
                    pass
                from core.models_unified_system import Agent
                return {
                    'success': True,
                    'stats': {
                        'total_agents': Agent.objects.filter(is_active=True).count(),
                        'avg_effectiveness': round(Agent.objects.filter(is_active=True).aggregate(avg=Avg('effectiveness_score'))['avg'] or 0, 1)
                    }
                }

            elif action == 'history':
                try:
                    response = requests.get(f'{base_url}/history/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'history': response.json()}
                except:
                    pass
                return {'success': True, 'history': []}

            elif action == 'dashboard':
                try:
                    response = requests.get(f'{base_url}/dashboard/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'dashboard': response.json()}
                except:
                    pass
                return {'success': True, 'dashboard': {'message': 'Dashboard data not available'}}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing agent training: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_workflow_templates(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage workflow templates and active workflows.
        """
        try:
            import requests
            action = arguments.get('action', 'list_templates')
            base_url = 'http://localhost:8000/api/teams/workflows'

            if action == 'list_templates':
                try:
                    response = requests.get(f'{base_url}/templates/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'templates': response.json()}
                except:
                    pass
                # Fallback - return default workflow templates
                return {
                    'success': True,
                    'templates': [
                        {'name': 'research_and_write', 'description': 'Research a topic and write content'},
                        {'name': 'analyze_and_report', 'description': 'Analyze data and generate report'},
                        {'name': 'create_and_distribute', 'description': 'Create content and distribute to platforms'}
                    ],
                    'summary': 'Available workflow templates'
                }

            elif action == 'list_active':
                try:
                    response = requests.get(f'{base_url}/active/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'active_workflows': response.json()}
                except:
                    pass
                return {'success': True, 'active_workflows': [], 'message': 'No active workflows'}

            elif action == 'get_status':
                workflow_id = arguments.get('workflow_id')
                if workflow_id:
                    try:
                        response = requests.get(f'{base_url}/{workflow_id}/status/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'status': response.json()}
                    except:
                        pass
                return {'success': False, 'error': 'Workflow not found'}

            elif action == 'create_from_template':
                template_name = arguments.get('template_name')
                if template_name:
                    return {
                        'success': True,
                        'message': f'Use execute_workflow tool with template: {template_name}',
                        'hint': 'The execute_workflow tool can run workflows based on templates'
                    }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing workflow templates: {e}")
            return {'success': False, 'error': str(e)}

    def _generate_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate images using AI image agents.
        """
        try:
            prompt = arguments.get('prompt', '')
            style = arguments.get('style', 'realistic')
            size = arguments.get('size', '1024x1024')
            image_type = arguments.get('image_type', 'general')

            if not prompt:
                return {'success': False, 'error': 'Prompt is required'}

            # Delegate to ImageAgent
            result = self.router.route(
                agent_name='ImageAgent',
                task=f"Create a {image_type} image: {prompt}. Style: {style}, Size: {size}",
                context={
                    'prompt': prompt,
                    'style': style,
                    'size': size,
                    'image_type': image_type
                }
            )

            return {
                'success': result.success,
                'message': result.message if result.success else result.error,
                'data': result.data if result.success else {},
                'summary': f"Image generation {'started' if result.success else 'failed'}: {prompt[:50]}..."
            }

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # Session 581: Phase 10 - Betting/Sports Tools
    # =========================================================================

    def _query_live_odds(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed live odds from multiple sportsbooks.
        """
        try:
            import requests
            sport = arguments.get('sport', 'nfl')
            market_type = arguments.get('market_type', 'all')
            team = arguments.get('team', '')

            # Try API first
            try:
                params = {'sport': sport}
                if market_type != 'all':
                    params['markets'] = market_type
                response = requests.get(
                    'http://localhost:8000/api/v1/sports/live-odds/',
                    params=params,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    odds_list = data if isinstance(data, list) else data.get('odds', [])

                    # Filter by team if specified
                    if team:
                        team_lower = team.lower()
                        odds_list = [o for o in odds_list if team_lower in str(o).lower()]

                    return {
                        'success': True,
                        'odds': odds_list[:20],
                        'sport': sport,
                        'market_type': market_type,
                        'total': len(odds_list),
                        'summary': f"Found {len(odds_list)} {sport.upper()} odds"
                    }
            except:
                pass

            # Fallback to SportsOddsAnalyst
            result = self.router.route(
                agent_name='SportsOddsAnalyst',
                task=f"Get live {market_type} odds for {sport}" + (f" filtered by {team}" if team else ""),
                context={'sport': sport, 'market_type': market_type, 'team': team}
            )

            return {
                'success': result.success,
                'odds': result.data.get('odds', []) if result.success else [],
                'summary': result.message if result.success else result.error
            }

        except Exception as e:
            logger.error(f"Error querying live odds: {e}")
            return {'success': False, 'error': str(e)}

    def _query_games(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query sports games - today's matchups, trending games, analytics.
        """
        try:
            import requests
            action = arguments.get('action', 'today')
            sport = arguments.get('sport', 'all')
            game_id = arguments.get('game_id', '')
            team = arguments.get('team', '')

            base_url = 'http://localhost:8000/api/v1/sports'

            if action == 'today':
                try:
                    response = requests.get(f'{base_url}/games/', params={'today': 'true', 'sport': sport}, timeout=10)
                    if response.status_code == 200:
                        games = response.json()
                        game_list = games if isinstance(games, list) else games.get('results', games.get('games', []))
                        return {
                            'success': True,
                            'games': game_list[:20],
                            'total': len(game_list),
                            'summary': f"Found {len(game_list)} games today"
                        }
                except:
                    pass

            elif action == 'trending':
                try:
                    response = requests.get(f'{base_url}/games/trending/', params={'sport': sport}, timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'games': response.json(), 'summary': 'Trending games retrieved'}
                except:
                    pass

            elif action == 'this_week':
                try:
                    response = requests.get(f'{base_url}/games/', params={'this_week': 'true', 'sport': sport}, timeout=10)
                    if response.status_code == 200:
                        games = response.json()
                        game_list = games if isinstance(games, list) else games.get('results', games.get('games', []))
                        return {
                            'success': True,
                            'games': game_list[:30],
                            'total': len(game_list),
                            'summary': f"Found {len(game_list)} games this week"
                        }
                except:
                    pass

            elif action == 'analytics' and game_id:
                try:
                    response = requests.get(f'{base_url}/games/{game_id}/analytics/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'analytics': response.json(), 'summary': 'Game analytics retrieved'}
                except:
                    pass

            elif action == 'search' and team:
                try:
                    response = requests.get(f'{base_url}/games/', params={'search': team}, timeout=10)
                    if response.status_code == 200:
                        games = response.json()
                        game_list = games if isinstance(games, list) else games.get('results', games.get('games', []))
                        return {
                            'success': True,
                            'games': game_list[:20],
                            'total': len(game_list),
                            'summary': f"Found {len(game_list)} games matching '{team}'"
                        }
                except:
                    pass

            # Fallback: use sports summary
            try:
                response = requests.get(f'{base_url}/summary/', timeout=10)
                if response.status_code == 200:
                    return {'success': True, 'data': response.json(), 'summary': 'Sports summary retrieved'}
            except:
                pass

            return {'success': True, 'games': [], 'summary': 'No games data available'}

        except Exception as e:
            logger.error(f"Error querying games: {e}")
            return {'success': False, 'error': str(e)}

    def _query_line_movements(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track betting line movements and identify sharp money.
        """
        try:
            import requests
            action = arguments.get('action', 'movers')
            game_id = arguments.get('game_id', '')
            sport = arguments.get('sport', 'all')
            min_movement = arguments.get('min_movement', 0.5)

            base_url = 'http://localhost:8000/api/v1/betting'

            if action == 'game' and game_id:
                try:
                    response = requests.get(f'{base_url}/line-movement/{game_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'movements': response.json(),
                            'game_id': game_id,
                            'summary': f'Line movement history for game {game_id}'
                        }
                except:
                    pass

            elif action == 'movers':
                try:
                    params = {'min_movement': min_movement}
                    if sport != 'all':
                        params['sport'] = sport
                    response = requests.get(f'{base_url}/movers/', params=params, timeout=10)
                    if response.status_code == 200:
                        movers = response.json()
                        mover_list = movers if isinstance(movers, list) else movers.get('movers', [])
                        return {
                            'success': True,
                            'movers': mover_list[:15],
                            'total': len(mover_list),
                            'summary': f"Found {len(mover_list)} games with significant line movement"
                        }
                except:
                    pass

            elif action == 'sharp':
                try:
                    response = requests.get(f'{base_url}/movers/', params={'sharp': 'true'}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'sharp_action': data,
                            'summary': 'Sharp money indicators retrieved'
                        }
                except:
                    pass

            return {'success': True, 'movements': [], 'summary': 'No line movement data available'}

        except Exception as e:
            logger.error(f"Error querying line movements: {e}")
            return {'success': False, 'error': str(e)}

    def _query_futures(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get futures betting odds for championships, MVPs, etc.
        """
        try:
            import requests
            sport = arguments.get('sport', 'nfl')
            market = arguments.get('market', 'championship')

            try:
                params = {'sport': sport, 'market': market}
                response = requests.get(
                    'http://localhost:8000/api/v1/betting/futures/',
                    params=params,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    futures = data if isinstance(data, list) else data.get('futures', data.get('odds', []))
                    return {
                        'success': True,
                        'futures': futures[:25],
                        'sport': sport,
                        'market': market,
                        'total': len(futures),
                        'summary': f"Found {len(futures)} {sport.upper()} {market} futures odds"
                    }
            except:
                pass

            # Fallback: delegate to SportsOddsAnalyst
            result = self.router.route(
                agent_name='SportsOddsAnalyst',
                task=f"Get {market} futures odds for {sport}",
                context={'sport': sport, 'market': market, 'futures': True}
            )

            return {
                'success': result.success,
                'futures': result.data.get('futures', []) if result.success else [],
                'summary': result.message if result.success else result.error
            }

        except Exception as e:
            logger.error(f"Error querying futures: {e}")
            return {'success': False, 'error': str(e)}

    def _query_player_props(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get player prop betting odds for specific games.
        """
        try:
            import requests
            event_id = arguments.get('event_id', '')
            player = arguments.get('player', '')
            prop_type = arguments.get('prop_type', 'all')

            # If we have an event_id, use the props endpoint
            if event_id:
                try:
                    response = requests.get(
                        f'http://localhost:8000/api/v1/sports/events/{event_id}/props/',
                        timeout=10
                    )
                    if response.status_code == 200:
                        props = response.json()
                        prop_list = props if isinstance(props, list) else props.get('props', [])

                        # Filter by player if specified
                        if player:
                            player_lower = player.lower()
                            prop_list = [p for p in prop_list if player_lower in str(p).lower()]

                        # Filter by prop type if specified
                        if prop_type != 'all':
                            prop_list = [p for p in prop_list if prop_type.lower() in str(p).lower()]

                        return {
                            'success': True,
                            'props': prop_list[:30],
                            'event_id': event_id,
                            'total': len(prop_list),
                            'summary': f"Found {len(prop_list)} player props"
                        }
                except:
                    pass

            # Fallback: delegate to SportsOddsAnalyst for player search
            if player:
                result = self.router.route(
                    agent_name='SportsOddsAnalyst',
                    task=f"Get {prop_type} props for player {player}",
                    context={'player': player, 'prop_type': prop_type}
                )

                return {
                    'success': result.success,
                    'props': result.data.get('props', []) if result.success else [],
                    'summary': result.message if result.success else result.error
                }

            return {
                'success': True,
                'props': [],
                'summary': 'Provide an event_id or player name to get props'
            }

        except Exception as e:
            logger.error(f"Error querying player props: {e}")
            return {'success': False, 'error': str(e)}

    def _query_betting_recommendations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI-generated betting recommendations and picks.
        """
        try:
            import requests
            action = arguments.get('action', 'list')
            sport = arguments.get('sport', 'all')
            min_confidence = arguments.get('min_confidence', 60)
            limit = arguments.get('limit', 10)

            base_url = 'http://localhost:8000/api/v1/sports/recommendations'

            if action == 'list':
                try:
                    params = {'limit': limit}
                    if sport != 'all':
                        params['sport'] = sport
                    if min_confidence > 0:
                        params['min_confidence'] = min_confidence
                    response = requests.get(f'{base_url}/', params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        recs = data if isinstance(data, list) else data.get('results', data.get('recommendations', []))
                        return {
                            'success': True,
                            'recommendations': recs[:limit],
                            'total': len(recs),
                            'summary': f"Found {len(recs)} betting recommendations"
                        }
                except:
                    pass

            elif action == 'generate':
                try:
                    response = requests.post(f'{base_url}/generate/', json={'sport': sport}, timeout=30)
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'recommendations': response.json(),
                            'summary': 'New recommendations generated'
                        }
                except:
                    pass

            elif action == 'top_picks':
                try:
                    response = requests.get(f'{base_url}/', params={'ordering': '-confidence', 'limit': 5}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        recs = data if isinstance(data, list) else data.get('results', data.get('recommendations', []))
                        return {
                            'success': True,
                            'top_picks': recs[:5],
                            'summary': f"Top {len(recs[:5])} high-confidence picks"
                        }
                except:
                    pass

            elif action == 'history':
                try:
                    response = requests.get(f'{base_url}/', params={'status': 'completed', 'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        recs = data if isinstance(data, list) else data.get('results', data.get('recommendations', []))
                        return {
                            'success': True,
                            'history': recs[:limit],
                            'summary': f"Found {len(recs)} past recommendations"
                        }
                except:
                    pass

            # Fallback: return graceful message when no recommendations available
            return {
                'success': True,
                'recommendations': [],
                'summary': 'No betting recommendations available at this time. Try during active game times.'
            }

        except Exception as e:
            logger.error(f"Error querying betting recommendations: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 11: Notification Tools (Session 582) =====

    def _manage_notifications(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 582: Manage proactive notifications.
        """
        try:
            import requests
            from django.utils import timezone

            action = arguments.get('action', 'list')
            notification_id = arguments.get('notification_id')
            unread_only = arguments.get('unread_only', False)
            limit = arguments.get('limit', 20)
            preferences = arguments.get('preferences', {})

            base_url = 'http://localhost:8000/api/proactive/notifications'

            if action == 'list':
                params = {'limit': limit}
                if unread_only:
                    params['unread'] = 'true'
                try:
                    response = requests.get(f'{base_url}/', params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'notifications': data.get('notifications', []),
                            'total': data.get('total', 0),
                            'unread_count': data.get('unread_count', 0),
                            'summary': f"Found {data.get('total', 0)} notifications ({data.get('unread_count', 0)} unread)"
                        }
                except:
                    pass

                # Fallback: Query database directly
                from core.models_unified_system import ProactiveNotification
                notifications = ProactiveNotification.objects.all()
                if unread_only:
                    notifications = notifications.filter(is_read=False, is_dismissed=False)
                notifications = notifications.order_by('-created_at')[:limit]
                total = ProactiveNotification.objects.count()
                unread = ProactiveNotification.objects.filter(is_read=False, is_dismissed=False).count()

                return {
                    'success': True,
                    'notifications': [
                        {
                            'id': str(n.id),
                            'type': n.notification_type,
                            'priority': n.priority,
                            'title': n.title,
                            'message': n.message,
                            'is_read': n.is_read,
                            'created_at': n.created_at.isoformat()
                        }
                        for n in notifications
                    ],
                    'total': total,
                    'unread_count': unread,
                    'summary': f"Found {total} notifications ({unread} unread)"
                }

            elif action == 'counts':
                try:
                    response = requests.get(f'{base_url}/', params={'limit': 1}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'total': data.get('total', 0),
                            'unread_count': data.get('unread_count', 0),
                            'summary': f"{data.get('unread_count', 0)} unread of {data.get('total', 0)} total"
                        }
                except:
                    pass

                from core.models_unified_system import ProactiveNotification
                total = ProactiveNotification.objects.count()
                unread = ProactiveNotification.objects.filter(is_read=False, is_dismissed=False).count()
                return {
                    'success': True,
                    'total': total,
                    'unread_count': unread,
                    'summary': f"{unread} unread of {total} total"
                }

            elif action == 'read':
                if not notification_id:
                    return {'success': False, 'error': 'notification_id required for read action'}
                try:
                    response = requests.post(f'{base_url}/{notification_id}/read/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'notification_id': notification_id,
                            'message': 'Notification marked as read'
                        }
                except:
                    pass

                from core.models_unified_system import ProactiveNotification
                try:
                    notification = ProactiveNotification.objects.get(id=notification_id)
                    notification.is_read = True
                    notification.read_at = timezone.now()
                    notification.save()
                    return {
                        'success': True,
                        'notification_id': notification_id,
                        'message': 'Notification marked as read'
                    }
                except ProactiveNotification.DoesNotExist:
                    return {'success': False, 'error': 'Notification not found'}

            elif action == 'dismiss':
                if not notification_id:
                    return {'success': False, 'error': 'notification_id required for dismiss action'}
                try:
                    response = requests.post(f'{base_url}/{notification_id}/dismiss/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'notification_id': notification_id,
                            'message': 'Notification dismissed'
                        }
                except:
                    pass

                from core.models_unified_system import ProactiveNotification
                try:
                    notification = ProactiveNotification.objects.get(id=notification_id)
                    notification.is_dismissed = True
                    notification.dismissed_at = timezone.now()
                    notification.save()
                    return {
                        'success': True,
                        'notification_id': notification_id,
                        'message': 'Notification dismissed'
                    }
                except ProactiveNotification.DoesNotExist:
                    return {'success': False, 'error': 'Notification not found'}

            elif action == 'read_all':
                try:
                    response = requests.post(f'{base_url}/read-all/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'updated_count': data.get('updated_count', 0),
                            'message': f"Marked {data.get('updated_count', 0)} notifications as read"
                        }
                except:
                    pass

                from core.models_unified_system import ProactiveNotification
                updated = ProactiveNotification.objects.filter(is_read=False).update(
                    is_read=True, read_at=timezone.now()
                )
                return {
                    'success': True,
                    'updated_count': updated,
                    'message': f'Marked {updated} notifications as read'
                }

            elif action == 'preferences':
                try:
                    if preferences:
                        response = requests.put(f'{base_url}/preferences/', json=preferences, timeout=10)
                    else:
                        response = requests.get(f'{base_url}/preferences/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'preferences': data.get('preferences', data),
                            'message': 'Preferences updated' if preferences else 'Current preferences'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'preferences': {'email_enabled': True, 'push_enabled': True, 'digest_frequency': 'realtime'},
                    'message': 'Default preferences (API unavailable)'
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing notifications: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_push_notifications(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 582: Manage Web Push notification settings.
        """
        try:
            import requests

            action = arguments.get('action', 'status')
            preferences = arguments.get('preferences', {})

            base_url = 'http://localhost:8000/api/v1/push'

            if action == 'status':
                try:
                    response = requests.get(f'{base_url}/status/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'subscribed': data.get('subscribed', False),
                            'subscription_count': data.get('subscription_count', 0),
                            'summary': 'Push notifications enabled' if data.get('subscribed') else 'Not subscribed to push notifications'
                        }
                except:
                    pass

                # Fallback: Query database
                from core.models_push_notifications import PushSubscription
                count = PushSubscription.objects.filter(is_active=True).count()
                return {
                    'success': True,
                    'subscribed': count > 0,
                    'subscription_count': count,
                    'summary': f'{count} active push subscription(s)' if count else 'No active push subscriptions'
                }

            elif action == 'preferences':
                try:
                    if preferences:
                        response = requests.put(f'{base_url}/preferences/', json=preferences, timeout=10)
                    else:
                        response = requests.get(f'{base_url}/preferences/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'preferences': data.get('preferences', data),
                            'message': 'Preferences updated' if preferences else 'Current push preferences'
                        }
                except:
                    pass

                # Fallback: Query database
                from core.models_push_notifications import NotificationPreference
                try:
                    pref = NotificationPreference.objects.first()
                    if pref:
                        return {
                            'success': True,
                            'preferences': {
                                'notifications_enabled': pref.notifications_enabled,
                                'arb_alerts_enabled': pref.arb_alerts_enabled,
                                'arb_min_profit_pct': float(pref.arb_min_profit_pct)
                            },
                            'message': 'Current push preferences'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'preferences': {
                        'notifications_enabled': True,
                        'arb_alerts_enabled': True,
                        'arb_min_profit_pct': 1.0
                    },
                    'message': 'Default preferences'
                }

            elif action == 'test':
                try:
                    response = requests.post(f'{base_url}/test/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'sent': data.get('sent', False),
                            'message': 'Test notification sent' if data.get('sent') else 'No active subscription to send to'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'sent': False,
                    'message': 'Test notification requires active browser subscription'
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing push notifications: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 12: Export & Scheduler Tools (Session 582) =====

    def _manage_exports(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 582: Export data in various formats.
        """
        try:
            import requests

            export_type = arguments.get('export_type', 'project')
            format = arguments.get('format', 'pdf')
            resource_id = arguments.get('resource_id')
            options = arguments.get('options', {})

            base_url = 'http://localhost:8000'

            if export_type == 'project':
                if not resource_id:
                    # List recent projects instead
                    from core.models_partnership import PartnershipProject
                    projects = PartnershipProject.objects.order_by('-created_at')[:5]
                    return {
                        'success': True,
                        'message': 'Provide a project_id to export. Recent projects:',
                        'projects': [
                            {'id': str(p.id), 'name': p.name, 'created': p.created_at.isoformat()}
                            for p in projects
                        ]
                    }

                format_map = {'pdf': 'pdf', 'zip': 'zip', 'csv': 'csv'}
                fmt = format_map.get(format, 'pdf')
                url = f'{base_url}/api/creative-projects/{resource_id}/export/{fmt}/'
                return {
                    'success': True,
                    'export_url': url,
                    'format': fmt,
                    'message': f'Export URL ready: {url}'
                }

            elif export_type == 'research':
                if not resource_id:
                    return {'success': False, 'error': 'resource_id (project_id) required for research export'}
                url = f'{base_url}/api/projects/{resource_id}/export-research-pdf/'
                return {
                    'success': True,
                    'export_url': url,
                    'format': 'pdf',
                    'message': f'Research PDF export URL: {url}'
                }

            elif export_type == 'content':
                if not resource_id:
                    return {'success': False, 'error': 'resource_id (project_id) required for content export'}
                url = f'{base_url}/api/projects/{resource_id}/export-content/'
                return {
                    'success': True,
                    'export_url': url,
                    'format': format or 'markdown',
                    'message': f'Content export URL: {url}'
                }

            elif export_type == 'revenue':
                try:
                    params = {}
                    if options.get('date_range'):
                        params['date_range'] = options['date_range']
                    response = requests.get(f'{base_url}/api/distribution/revenue/export/', params=params, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'revenue_data': data,
                            'format': 'json',
                            'summary': f"Revenue export complete"
                        }
                except:
                    pass

                # Fallback: return export URL
                return {
                    'success': True,
                    'export_url': f'{base_url}/api/distribution/revenue/export/',
                    'format': 'json',
                    'message': 'Revenue export endpoint ready'
                }

            elif export_type == 'legal':
                url = f'{base_url}/api/legal/export-section/'
                return {
                    'success': True,
                    'export_url': url,
                    'format': format or 'pdf',
                    'message': 'Legal document export URL ready'
                }

            elif export_type == 'portfolio':
                if not resource_id:
                    return {'success': False, 'error': 'resource_id (project_id) required for portfolio export'}
                url = f'{base_url}/api/v1/portfolio/projects/{resource_id}/export/'
                return {
                    'success': True,
                    'export_url': url,
                    'format': format or 'zip',
                    'message': f'Portfolio export URL: {url}'
                }

            return {'success': False, 'error': f'Unknown export type: {export_type}'}

        except Exception as e:
            logger.error(f"Error managing exports: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_scheduler(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 582: Manage scheduled tasks and distributions.
        """
        try:
            import requests
            from django.utils import timezone

            action = arguments.get('action', 'list')
            distribution_id = arguments.get('distribution_id')
            workflow_id = arguments.get('workflow_id')
            new_time = arguments.get('new_time')
            schedule_type = arguments.get('schedule_type', 'all')

            base_url = 'http://localhost:8000'

            if action == 'list':
                results = {'distributions': [], 'workflows': [], 'celery_schedules': []}

                if schedule_type in ['distributions', 'all']:
                    try:
                        response = requests.get(f'{base_url}/api/distribution/scheduled/', timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            results['distributions'] = data if isinstance(data, list) else data.get('results', [])
                    except:
                        from core.models_unified_system import ContentDistribution
                        dists = ContentDistribution.objects.filter(
                            status='scheduled',
                            scheduled_time__gte=timezone.now()
                        ).order_by('scheduled_time')[:10]
                        results['distributions'] = [
                            {
                                'id': str(d.id),
                                'platform': d.platform,
                                'scheduled_time': d.scheduled_time.isoformat(),
                                'status': d.status
                            }
                            for d in dists
                        ]

                if schedule_type in ['workflows', 'all']:
                    try:
                        from core.models_workflow import WorkflowExecution
                        workflows = WorkflowExecution.objects.filter(
                            status='scheduled'
                        ).order_by('-created_at')[:10]
                        results['workflows'] = [
                            {
                                'id': str(w.id),
                                'workflow_name': w.workflow.name if hasattr(w, 'workflow') else 'Unknown',
                                'status': w.status,
                                'created_at': w.created_at.isoformat()
                            }
                            for w in workflows
                        ]
                    except:
                        results['workflows'] = []

                total = len(results['distributions']) + len(results['workflows'])
                return {
                    'success': True,
                    'scheduled_items': results,
                    'total': total,
                    'summary': f"Found {len(results['distributions'])} scheduled distributions, {len(results['workflows'])} scheduled workflows"
                }

            elif action == 'cancel':
                if not distribution_id:
                    return {'success': False, 'error': 'distribution_id required for cancel action'}
                try:
                    response = requests.post(f'{base_url}/api/distribution/{distribution_id}/cancel/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'distribution_id': distribution_id,
                            'message': 'Distribution cancelled'
                        }
                except:
                    pass

                from core.models_unified_system import ContentDistribution
                try:
                    dist = ContentDistribution.objects.get(id=distribution_id)
                    dist.status = 'cancelled'
                    dist.save()
                    return {
                        'success': True,
                        'distribution_id': distribution_id,
                        'message': 'Distribution cancelled'
                    }
                except ContentDistribution.DoesNotExist:
                    return {'success': False, 'error': 'Distribution not found'}

            elif action == 'reschedule':
                if not distribution_id:
                    return {'success': False, 'error': 'distribution_id required for reschedule action'}
                if not new_time:
                    return {'success': False, 'error': 'new_time required for reschedule action'}

                try:
                    response = requests.post(
                        f'{base_url}/api/distribution/{distribution_id}/reschedule/',
                        json={'scheduled_time': new_time},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'distribution_id': distribution_id,
                            'new_time': new_time,
                            'message': f'Distribution rescheduled to {new_time}'
                        }
                except:
                    pass

                from core.models_unified_system import ContentDistribution
                from dateutil.parser import parse
                try:
                    dist = ContentDistribution.objects.get(id=distribution_id)
                    dist.scheduled_time = parse(new_time)
                    dist.save()
                    return {
                        'success': True,
                        'distribution_id': distribution_id,
                        'new_time': new_time,
                        'message': f'Distribution rescheduled to {new_time}'
                    }
                except ContentDistribution.DoesNotExist:
                    return {'success': False, 'error': 'Distribution not found'}

            elif action == 'celery_schedules':
                try:
                    response = requests.get(f'{base_url}/api/monitoring/schedules/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        schedules = data.get('schedules', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'celery_schedules': schedules[:20] if isinstance(schedules, list) else schedules,
                            'summary': f"Found {len(schedules) if isinstance(schedules, list) else 'multiple'} Celery beat schedules"
                        }
                except:
                    pass

                # Fallback: return basic schedule info
                from core.celery import app
                try:
                    schedules = list(app.conf.beat_schedule.keys())[:20]
                    return {
                        'success': True,
                        'celery_schedules': schedules,
                        'total': len(app.conf.beat_schedule),
                        'summary': f"Found {len(app.conf.beat_schedule)} Celery beat schedules"
                    }
                except:
                    return {
                        'success': True,
                        'celery_schedules': [],
                        'message': 'Unable to retrieve Celery schedules'
                    }

            elif action == 'schedule_workflow':
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required for schedule_workflow action'}

                try:
                    response = requests.post(
                        f'{base_url}/api/workflows/{workflow_id}/schedule/',
                        json={'scheduled_time': new_time} if new_time else {},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'workflow_id': workflow_id,
                            'message': 'Workflow scheduled successfully'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'workflow_id': workflow_id,
                    'schedule_url': f'{base_url}/api/workflows/{workflow_id}/schedule/',
                    'message': 'Use the schedule URL to schedule this workflow'
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing scheduler: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 13: Monitoring Tools (Session 582) =====

    def _query_system_health(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 582: Get system health and status information.
        """
        try:
            import requests

            subsystem = arguments.get('subsystem', 'unified')
            base_url = 'http://localhost:8000'

            results = {}

            if subsystem in ['unified', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/monitoring/health/', timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        results['unified'] = data.get('data', data)
                except:
                    results['unified'] = {'status': 'unknown', 'error': 'API unavailable'}

            if subsystem in ['content_studio', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/monitoring/content-studio/', timeout=10)
                    if response.status_code == 200:
                        results['content_studio'] = response.json()
                except:
                    results['content_studio'] = {'status': 'unknown'}

            if subsystem in ['narrative_drift', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/monitoring/narrative-drift/', timeout=10)
                    if response.status_code == 200:
                        results['narrative_drift'] = response.json()
                except:
                    results['narrative_drift'] = {'status': 'unknown'}

            if subsystem in ['market_intelligence', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/monitoring/market-intelligence/', timeout=10)
                    if response.status_code == 200:
                        results['market_intelligence'] = response.json()
                except:
                    results['market_intelligence'] = {'status': 'unknown'}

            if subsystem in ['ml_scoring', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/monitoring/ml-scoring/', timeout=10)
                    if response.status_code == 200:
                        results['ml_scoring'] = response.json()
                except:
                    results['ml_scoring'] = {'status': 'unknown'}

            if subsystem in ['agents', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/v1/agents/health/', timeout=10)
                    if response.status_code == 200:
                        results['agents'] = response.json()
                    else:
                        raise Exception('API error')
                except:
                    # Fallback: count agents
                    from core.models_unified_system import Agent
                    results['agents'] = {
                        'total': Agent.objects.count(),
                        'active': Agent.objects.filter(is_active=True).count(),
                        'status': 'ok'
                    }

            if subsystem in ['spiders', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/spider-health/summary/', timeout=10)
                    if response.status_code == 200:
                        results['spiders'] = response.json()
                    else:
                        raise Exception('API error')
                except:
                    # Fallback: count spiders
                    from ai_core.spiders.spider_registry import SpiderRegistry
                    registry = SpiderRegistry()
                    results['spiders'] = {
                        'total': registry.get_spider_count(),
                        'status': 'ok'
                    }

            # Generate summary
            healthy_count = sum(1 for v in results.values() if isinstance(v, dict) and v.get('status') != 'error')
            total_count = len(results)

            return {
                'success': True,
                'health': results,
                'subsystems_checked': list(results.keys()),
                'summary': f"Checked {total_count} subsystem(s): {healthy_count} healthy"
            }

        except Exception as e:
            logger.error(f"Error querying system health: {e}")
            return {'success': False, 'error': str(e)}

    def _query_activity_metrics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 582: Get activity streams, ROI metrics, and provenance data.
        """
        try:
            import requests

            metric_type = arguments.get('metric_type', 'activity')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if metric_type == 'activity':
                try:
                    response = requests.get(f'{base_url}/api/monitoring/activity/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        activities = data.get('activities', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'activities': activities[:limit] if isinstance(activities, list) else activities,
                            'summary': f"Found {len(activities) if isinstance(activities, list) else 'multiple'} recent activities"
                        }
                except:
                    pass

                # Fallback: Query recent agent executions
                from core.models_unified_system import AgentExecution
                executions = AgentExecution.objects.order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'activities': [
                        {
                            'type': 'agent_execution',
                            'agent': e.agent.name if hasattr(e, 'agent') and e.agent else 'Unknown',
                            'status': e.status,
                            'created_at': e.created_at.isoformat()
                        }
                        for e in executions
                    ],
                    'summary': f"Found {len(executions)} recent agent executions"
                }

            elif metric_type == 'roi':
                try:
                    response = requests.get(f'{base_url}/api/monitoring/roi/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'roi_metrics': data,
                            'summary': 'ROI metrics retrieved'
                        }
                except:
                    pass

                # Fallback: Basic revenue stats
                from core.models_unified_system import Revenue
                from django.db.models import Sum
                total = Revenue.objects.aggregate(total=Sum('amount'))['total'] or 0
                return {
                    'success': True,
                    'roi_metrics': {
                        'total_revenue': float(total),
                        'currency': 'USD'
                    },
                    'summary': f'Total revenue: ${total:.2f}'
                }

            elif metric_type == 'provenance':
                try:
                    response = requests.get(f'{base_url}/api/monitoring/provenance/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'provenance': data,
                            'summary': 'Provenance chain retrieved'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'provenance': [],
                    'message': 'Provenance tracking available via API'
                }

            return {'success': False, 'error': f'Unknown metric type: {metric_type}'}

        except Exception as e:
            logger.error(f"Error querying activity metrics: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 14: Artifact & Review Tools (Session 583) =====

    def _manage_artifacts(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage AI-generated artifacts and their execution.
        """
        try:
            import requests

            action = arguments.get('action', 'list')
            artifact_id = arguments.get('artifact_id')
            decision = arguments.get('decision')
            reason = arguments.get('reason', '')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if action == 'list':
                try:
                    response = requests.get(f'{base_url}/api/artifacts/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        artifacts = data.get('results', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'artifacts': artifacts[:limit] if isinstance(artifacts, list) else artifacts,
                            'summary': f"Found {len(artifacts) if isinstance(artifacts, list) else 'multiple'} artifacts"
                        }
                except:
                    pass

                # Fallback: Query database
                from core.models_artifacts import Artifact
                artifacts = Artifact.objects.order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'artifacts': [
                        {
                            'id': str(a.id),
                            'name': a.name,
                            'artifact_type': a.artifact_type,
                            'status': a.status,
                            'created_at': a.created_at.isoformat()
                        }
                        for a in artifacts
                    ],
                    'summary': f"Found {len(artifacts)} artifacts"
                }

            elif action == 'pending':
                try:
                    response = requests.get(f'{base_url}/api/artifacts/pending/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'pending_artifacts': data.get('results', data),
                            'summary': 'Retrieved pending artifacts for review'
                        }
                except:
                    pass

                from core.models_artifacts import Artifact
                pending = Artifact.objects.filter(status='pending').order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'pending_artifacts': [
                        {
                            'id': str(a.id),
                            'name': a.name,
                            'artifact_type': a.artifact_type,
                            'created_at': a.created_at.isoformat()
                        }
                        for a in pending
                    ],
                    'summary': f"Found {len(pending)} pending artifacts"
                }

            elif action == 'get':
                if not artifact_id:
                    return {'success': False, 'error': 'artifact_id required'}

                try:
                    response = requests.get(f'{base_url}/api/artifacts/{artifact_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'artifact': response.json(),
                            'summary': 'Retrieved artifact details'
                        }
                except:
                    pass

                from core.models_artifacts import Artifact
                try:
                    artifact = Artifact.objects.get(id=artifact_id)
                    return {
                        'success': True,
                        'artifact': {
                            'id': str(artifact.id),
                            'name': artifact.name,
                            'artifact_type': artifact.artifact_type,
                            'content': artifact.content if hasattr(artifact, 'content') else None,
                            'status': artifact.status,
                            'created_at': artifact.created_at.isoformat()
                        },
                        'summary': f"Retrieved artifact: {artifact.name}"
                    }
                except Artifact.DoesNotExist:
                    return {'success': False, 'error': 'Artifact not found'}

            elif action == 'decide':
                if not artifact_id or not decision:
                    return {'success': False, 'error': 'artifact_id and decision required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/artifacts/{artifact_id}/decide/',
                        json={'decision': decision, 'reason': reason},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': f"Artifact {decision}d successfully"
                        }
                except:
                    pass

                from core.models_artifacts import Artifact
                try:
                    artifact = Artifact.objects.get(id=artifact_id)
                    artifact.status = 'approved' if decision == 'approve' else 'rejected'
                    artifact.save()
                    return {
                        'success': True,
                        'result': {'status': artifact.status},
                        'summary': f"Artifact {decision}d: {artifact.name}"
                    }
                except Artifact.DoesNotExist:
                    return {'success': False, 'error': 'Artifact not found'}

            elif action == 'execute':
                if not artifact_id:
                    return {'success': False, 'error': 'artifact_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/artifacts/{artifact_id}/execute/',
                        timeout=30
                    )
                    if response.status_code in [200, 201, 202]:
                        return {
                            'success': True,
                            'execution': response.json(),
                            'summary': 'Artifact execution started'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not execute artifact via API'}

            elif action == 'executions':
                try:
                    response = requests.get(f'{base_url}/api/artifact-executions/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'executions': data.get('results', data),
                            'summary': 'Retrieved artifact executions'
                        }
                except:
                    pass

                from core.models_artifacts import ArtifactExecution
                executions = ArtifactExecution.objects.order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'executions': [
                        {
                            'id': str(e.id),
                            'artifact_id': str(e.artifact_id) if hasattr(e, 'artifact_id') else None,
                            'status': e.status,
                            'created_at': e.created_at.isoformat()
                        }
                        for e in executions
                    ],
                    'summary': f"Found {len(executions)} executions"
                }

            elif action == 'execution_status':
                if not artifact_id:
                    return {'success': False, 'error': 'artifact_id (execution_id) required'}

                try:
                    response = requests.get(f'{base_url}/api/artifact-executions/{artifact_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'execution': response.json(),
                            'summary': 'Retrieved execution status'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Execution not found'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing artifacts: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_reviews(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage Chief of Staff review documents (Pro/Con analysis).
        """
        try:
            import requests

            action = arguments.get('action', 'list')
            review_id = arguments.get('review_id')
            artifact_id = arguments.get('artifact_id')
            question = arguments.get('question', '')
            decision = arguments.get('decision')
            reason = arguments.get('reason', '')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if action == 'list':
                try:
                    response = requests.get(f'{base_url}/api/review-documents/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        reviews = data.get('results', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'reviews': reviews[:limit] if isinstance(reviews, list) else reviews,
                            'summary': f"Found {len(reviews) if isinstance(reviews, list) else 'multiple'} review documents"
                        }
                except:
                    pass

                # Fallback: Query database
                from core.models_conversation_artifacts import ReviewDocument
                reviews = ReviewDocument.objects.order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'reviews': [
                        {
                            'id': str(r.id),
                            'artifact_id': str(r.artifact_id) if hasattr(r, 'artifact_id') else None,
                            'status': r.status,
                            'created_at': r.created_at.isoformat()
                        }
                        for r in reviews
                    ],
                    'summary': f"Found {len(reviews)} review documents"
                }

            elif action == 'get':
                if not review_id:
                    return {'success': False, 'error': 'review_id required'}

                try:
                    response = requests.get(f'{base_url}/api/review-documents/{review_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'review': response.json(),
                            'summary': 'Retrieved review document'
                        }
                except:
                    pass

                from core.models_conversation_artifacts import ReviewDocument
                try:
                    review = ReviewDocument.objects.get(id=review_id)
                    return {
                        'success': True,
                        'review': {
                            'id': str(review.id),
                            'status': review.status,
                            'pro_arguments': review.pro_arguments if hasattr(review, 'pro_arguments') else None,
                            'con_arguments': review.con_arguments if hasattr(review, 'con_arguments') else None,
                            'created_at': review.created_at.isoformat()
                        },
                        'summary': 'Retrieved review document'
                    }
                except ReviewDocument.DoesNotExist:
                    return {'success': False, 'error': 'Review document not found'}

            elif action == 'ask_pro':
                if not review_id or not question:
                    return {'success': False, 'error': 'review_id and question required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/review-documents/{review_id}/ask-pro/',
                        json={'question': question},
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'pro_response': response.json(),
                            'summary': 'Pro side responded to question'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not get Pro response'}

            elif action == 'ask_con':
                if not review_id or not question:
                    return {'success': False, 'error': 'review_id and question required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/review-documents/{review_id}/ask-con/',
                        json={'question': question},
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'con_response': response.json(),
                            'summary': 'Con side responded to question'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not get Con response'}

            elif action == 'decide':
                if not review_id or not decision:
                    return {'success': False, 'error': 'review_id and decision required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/review-documents/{review_id}/decide/',
                        json={'decision': decision, 'reason': reason},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': f"Review decision: {decision}"
                        }
                except:
                    pass

                from core.models_conversation_artifacts import ReviewDocument
                try:
                    review = ReviewDocument.objects.get(id=review_id)
                    review.status = 'approved' if decision == 'approve' else 'rejected'
                    review.decision_reason = reason
                    review.save()
                    return {
                        'success': True,
                        'result': {'status': review.status},
                        'summary': f"Review decision recorded: {decision}"
                    }
                except ReviewDocument.DoesNotExist:
                    return {'success': False, 'error': 'Review document not found'}

            elif action == 'generate':
                if not artifact_id:
                    return {'success': False, 'error': 'artifact_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/review-documents/generate/',
                        json={'artifact_id': artifact_id},
                        timeout=60
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'review': response.json(),
                            'summary': 'Review document generated'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not generate review document'}

            elif action == 'trigger_auto':
                try:
                    response = requests.post(f'{base_url}/api/review-documents/trigger-auto-review/', timeout=30)
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Auto-review triggered'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not trigger auto-review'}

            elif action == 'stats':
                try:
                    response = requests.get(f'{base_url}/api/review-documents/stats/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'stats': response.json(),
                            'summary': 'Review statistics retrieved'
                        }
                except:
                    pass

                from core.models_conversation_artifacts import ReviewDocument
                from django.db.models import Count
                stats = ReviewDocument.objects.values('status').annotate(count=Count('id'))
                return {
                    'success': True,
                    'stats': {s['status']: s['count'] for s in stats},
                    'summary': 'Review statistics from database'
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing reviews: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 15: Journey & Proposal Tools (Session 583) =====

    def _manage_journeys(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage learning journeys and progress tracking.
        """
        try:
            import requests

            action = arguments.get('action', 'active')
            journey_id = arguments.get('journey_id')
            step_id = arguments.get('step_id')
            journey_type = arguments.get('journey_type', 'default')
            base_url = 'http://localhost:8000'

            if action == 'active':
                try:
                    response = requests.get(f'{base_url}/api/journey/active/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        journeys = data.get('journeys', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'journeys': journeys,
                            'summary': f"Found {len(journeys) if isinstance(journeys, list) else 'multiple'} active journeys"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'journeys': [],
                    'summary': 'No active journeys found'
                }

            elif action == 'start':
                try:
                    response = requests.post(
                        f'{base_url}/api/journey/start/',
                        json={'journey_type': journey_type},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'journey': response.json(),
                            'summary': f"Started {journey_type} journey"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not start journey'}

            elif action == 'status':
                if not journey_id:
                    return {'success': False, 'error': 'journey_id required'}

                try:
                    response = requests.get(f'{base_url}/api/journey/{journey_id}/status/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'status': response.json(),
                            'summary': 'Retrieved journey status'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Journey not found'}

            elif action == 'step_start':
                if not journey_id or step_id is None:
                    return {'success': False, 'error': 'journey_id and step_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/journey/{journey_id}/step/{step_id}/start/',
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'step': response.json(),
                            'summary': f"Started step {step_id}"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not start step'}

            elif action == 'step_complete':
                if not journey_id or step_id is None:
                    return {'success': False, 'error': 'journey_id and step_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/journey/{journey_id}/step/{step_id}/complete/',
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'step': response.json(),
                            'summary': f"Completed step {step_id}"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not complete step'}

            elif action == 'reset':
                if not journey_id:
                    return {'success': False, 'error': 'journey_id required'}

                try:
                    response = requests.post(f'{base_url}/api/journey/{journey_id}/reset/', timeout=10)
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Journey reset successfully'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not reset journey'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing journeys: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_proposals(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage AI-generated proposals and their execution.
        """
        try:
            import requests

            action = arguments.get('action', 'list')
            proposal_id = arguments.get('proposal_id')
            reason = arguments.get('reason', '')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if action == 'list':
                try:
                    response = requests.get(f'{base_url}/api/proposals/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        proposals = data.get('results', data.get('proposals', data)) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'proposals': proposals[:limit] if isinstance(proposals, list) else proposals,
                            'summary': f"Found {len(proposals) if isinstance(proposals, list) else 'multiple'} proposals"
                        }
                except:
                    pass

                # Fallback: Try to get proposals from database
                try:
                    from core.models_proposals import Proposal
                    proposals = Proposal.objects.order_by('-created_at')[:limit]
                    return {
                        'success': True,
                        'proposals': [
                            {
                                'id': str(p.id),
                                'title': p.title if hasattr(p, 'title') else str(p),
                                'status': p.status if hasattr(p, 'status') else 'unknown',
                                'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') else None
                            }
                            for p in proposals
                        ],
                        'summary': f"Found {len(proposals)} proposals"
                    }
                except:
                    return {
                        'success': True,
                        'proposals': [],
                        'summary': 'No proposals found'
                    }

            elif action == 'stats':
                try:
                    response = requests.get(f'{base_url}/api/proposals/stats/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'stats': response.json(),
                            'summary': 'Retrieved proposal statistics'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'stats': {'message': 'Stats available via API'},
                    'summary': 'Proposal stats endpoint available'
                }

            elif action == 'approve':
                if not proposal_id:
                    return {'success': False, 'error': 'proposal_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/proposals/{proposal_id}/approve/',
                        json={'reason': reason},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Proposal approved'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not approve proposal'}

            elif action == 'reject':
                if not proposal_id:
                    return {'success': False, 'error': 'proposal_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/proposals/{proposal_id}/reject/',
                        json={'reason': reason},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Proposal rejected'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not reject proposal'}

            elif action == 'execute':
                if not proposal_id:
                    return {'success': False, 'error': 'proposal_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/proposals/{proposal_id}/execute/',
                        timeout=30
                    )
                    if response.status_code in [200, 201, 202]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Proposal execution started'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not execute proposal'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing proposals: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 16: Solutions & Learning Tools (Session 583) =====

    def _manage_solutions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage AI-discovered solutions and their application.
        """
        try:
            import requests

            action = arguments.get('action', 'list')
            solution_id = arguments.get('solution_id')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if action == 'list':
                try:
                    response = requests.get(f'{base_url}/api/solutions/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        solutions = data.get('results', data.get('solutions', data)) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'solutions': solutions[:limit] if isinstance(solutions, list) else solutions,
                            'summary': f"Found {len(solutions) if isinstance(solutions, list) else 'multiple'} solutions"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'solutions': [],
                    'summary': 'No solutions found'
                }

            elif action == 'get':
                if not solution_id:
                    return {'success': False, 'error': 'solution_id required'}

                try:
                    response = requests.get(f'{base_url}/api/solutions/{solution_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'solution': response.json(),
                            'summary': 'Retrieved solution details'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Solution not found'}

            elif action == 'apply':
                if not solution_id:
                    return {'success': False, 'error': 'solution_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/solutions/{solution_id}/apply/',
                        timeout=30
                    )
                    if response.status_code in [200, 201, 202]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Solution applied successfully'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not apply solution'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing solutions: {e}")
            return {'success': False, 'error': str(e)}

    def _query_learning(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Query learning system data, patterns, and insights.
        """
        try:
            import requests

            query_type = arguments.get('query_type', 'dashboard')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if query_type == 'dashboard':
                try:
                    response = requests.get(f'{base_url}/api/learning/dashboard/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'dashboard': response.json(),
                            'summary': 'Retrieved learning dashboard'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'dashboard': {'message': 'Dashboard available via API'},
                    'summary': 'Learning dashboard endpoint available'
                }

            elif query_type == 'patterns':
                try:
                    response = requests.get(f'{base_url}/api/learning/patterns/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        patterns = data.get('patterns', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'patterns': patterns,
                            'summary': f"Found {len(patterns) if isinstance(patterns, list) else 'multiple'} patterns"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'patterns': [],
                    'summary': 'No patterns found'
                }

            elif query_type == 'insights':
                try:
                    response = requests.get(f'{base_url}/api/learning/insights/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        insights = data.get('insights', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'insights': insights,
                            'summary': f"Found {len(insights) if isinstance(insights, list) else 'multiple'} insights"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'insights': [],
                    'summary': 'No insights found'
                }

            elif query_type == 'profile':
                try:
                    response = requests.get(f'{base_url}/api/learning/profile/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'profile': response.json(),
                            'summary': 'Retrieved learning profile'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'profile': {'message': 'Profile available via API'},
                    'summary': 'Learning profile endpoint available'
                }

            elif query_type == 'progress':
                try:
                    response = requests.get(f'{base_url}/api/learning/progress/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'progress': response.json(),
                            'summary': 'Retrieved learning progress'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'progress': {'message': 'Progress available via API'},
                    'summary': 'Learning progress endpoint available'
                }

            elif query_type == 'data_flow':
                try:
                    response = requests.get(f'{base_url}/api/learning/data-flow/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'data_flow': response.json(),
                            'summary': 'Retrieved learning data flow'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'data_flow': {'message': 'Data flow available via API'},
                    'summary': 'Learning data flow endpoint available'
                }

            elif query_type == 'feed':
                try:
                    response = requests.get(f'{base_url}/api/learning/feed/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        feed = data.get('feed', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'feed': feed,
                            'summary': f"Found {len(feed) if isinstance(feed, list) else 'multiple'} feed items"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'feed': [],
                    'summary': 'No feed items found'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying learning: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 17: Portfolio & Nexus Tools (Session 583) =====

    def _manage_portfolio(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage creative portfolio items.
        """
        try:
            import requests

            action = arguments.get('action', 'list')
            item_type = arguments.get('item_type')
            item_id = arguments.get('item_id')
            item_ids = arguments.get('item_ids', [])
            base_url = 'http://localhost:8000'

            if action == 'list':
                try:
                    response = requests.get(f'{base_url}/api/portfolio/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        items = data.get('items', data.get('portfolio', data)) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'portfolio': items,
                            'summary': f"Found {len(items) if isinstance(items, list) else 'multiple'} portfolio items"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'portfolio': [],
                    'summary': 'No portfolio items found'
                }

            elif action == 'delete':
                if not item_type or not item_id:
                    return {'success': False, 'error': 'item_type and item_id required'}

                try:
                    response = requests.delete(
                        f'{base_url}/api/portfolio/{item_type}/{item_id}/delete/',
                        timeout=10
                    )
                    if response.status_code in [200, 204]:
                        return {
                            'success': True,
                            'result': {'deleted': True},
                            'summary': f"Deleted {item_type} item"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not delete item'}

            elif action == 'bulk_delete':
                if not item_ids:
                    return {'success': False, 'error': 'item_ids required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/portfolio/bulk-delete/',
                        json={'item_ids': item_ids},
                        timeout=10
                    )
                    if response.status_code in [200, 204]:
                        return {
                            'success': True,
                            'result': response.json() if response.content else {'deleted': len(item_ids)},
                            'summary': f"Bulk deleted {len(item_ids)} items"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not bulk delete items'}

            elif action == 'check_broken':
                try:
                    response = requests.get(f'{base_url}/api/portfolio/check-broken/', timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        broken = data.get('broken', data.get('broken_links', []))
                        return {
                            'success': True,
                            'broken_links': broken,
                            'summary': f"Found {len(broken) if isinstance(broken, list) else 0} broken links"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'broken_links': [],
                    'summary': 'No broken links found'
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing portfolio: {e}")
            return {'success': False, 'error': str(e)}

    def _query_nexus(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Query the Nexus unified intelligence system.
        """
        try:
            import requests

            query_type = arguments.get('query_type', 'intelligence_data')
            insight_id = arguments.get('insight_id')
            behavior_query = arguments.get('behavior_query', '')
            base_url = 'http://localhost:8000'

            if query_type == 'intelligence_data':
                try:
                    response = requests.get(f'{base_url}/api/nexus/intelligence-data/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'intelligence': response.json(),
                            'summary': 'Retrieved unified intelligence data'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'intelligence': {'message': 'Intelligence data available via API'},
                    'summary': 'Nexus intelligence endpoint available'
                }

            elif query_type == 'implement_insight':
                if not insight_id:
                    return {'success': False, 'error': 'insight_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/nexus/implement-insight/',
                        json={'insight_id': insight_id},
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Insight implementation started'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not implement insight'}

            elif query_type == 'investigate_behavior':
                try:
                    response = requests.post(
                        f'{base_url}/api/nexus/investigate-behavior/',
                        json={'query': behavior_query},
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'investigation': response.json(),
                            'summary': 'Behavior investigation complete'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'investigation': {'message': 'Investigation available via API'},
                    'summary': 'Nexus investigation endpoint available'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying nexus: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 18: Predictions & Performance Tools (Session 583) =====

    def _manage_predictions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage agent predictions (prophecies) and their verification.
        """
        try:
            import requests

            action = arguments.get('action', 'overview')
            agent_id = arguments.get('agent_id')
            prediction_id = arguments.get('prediction_id')
            outcome = arguments.get('outcome')
            base_url = 'http://localhost:8000'

            if action == 'overview':
                try:
                    response = requests.get(f'{base_url}/api/predictions/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'predictions': data,
                            'summary': 'Retrieved predictions overview'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'predictions': [],
                    'summary': 'No predictions found'
                }

            elif action == 'agent':
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}

                try:
                    response = requests.get(f'{base_url}/api/predictions/agent/{agent_id}/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'predictions': data,
                            'summary': f"Retrieved predictions for agent {agent_id}"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'predictions': [],
                    'summary': 'No predictions found for agent'
                }

            elif action == 'detail':
                if not prediction_id:
                    return {'success': False, 'error': 'prediction_id required'}

                try:
                    response = requests.get(f'{base_url}/api/predictions/{prediction_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'prediction': response.json(),
                            'summary': 'Retrieved prediction details'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Prediction not found'}

            elif action == 'verify':
                if not prediction_id or not outcome:
                    return {'success': False, 'error': 'prediction_id and outcome required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/predictions/{prediction_id}/verify/',
                        json={'outcome': outcome},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': f"Prediction verified as {outcome}"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not verify prediction'}

            elif action == 'upvote':
                if not prediction_id:
                    return {'success': False, 'error': 'prediction_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/predictions/{prediction_id}/upvote/',
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Prediction upvoted'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not upvote prediction'}

            elif action == 'leaderboard':
                try:
                    response = requests.get(f'{base_url}/api/predictions/leaderboard/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'leaderboard': response.json(),
                            'summary': 'Retrieved prediction leaderboard'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'leaderboard': [],
                    'summary': 'No leaderboard data found'
                }

            elif action == 'generate':
                try:
                    response = requests.post(
                        f'{base_url}/api/predictions/generate-from-dreams/',
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Generated predictions from dreams'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not generate predictions'}

            elif action == 'expire':
                try:
                    response = requests.post(
                        f'{base_url}/api/predictions/expire-old/',
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Expired old predictions'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not expire predictions'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing predictions: {e}")
            return {'success': False, 'error': str(e)}

    def _query_performance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Query performance metrics, predictions, and pricing optimization.
        """
        try:
            import requests

            query_type = arguments.get('query_type', 'predictions')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if query_type == 'predict':
                try:
                    response = requests.get(f'{base_url}/api/learning/predict/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'prediction': response.json(),
                            'summary': 'Retrieved performance prediction'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'prediction': {'message': 'Performance prediction available via API'},
                    'summary': 'Performance prediction endpoint available'
                }

            elif query_type == 'predictions':
                try:
                    response = requests.get(f'{base_url}/api/learning/predictions/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        predictions = data.get('predictions', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'predictions': predictions,
                            'summary': f"Found {len(predictions) if isinstance(predictions, list) else 'multiple'} predictions"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'predictions': [],
                    'summary': 'No predictions found'
                }

            elif query_type == 'pricing':
                try:
                    response = requests.get(f'{base_url}/api/learning/pricing/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'pricing': response.json(),
                            'summary': 'Retrieved pricing optimization'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'pricing': {'message': 'Pricing optimization available via API'},
                    'summary': 'Pricing optimization endpoint available'
                }

            elif query_type == 'compare':
                try:
                    response = requests.get(f'{base_url}/api/learning/compare/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'comparison': response.json(),
                            'summary': 'Retrieved performance comparison'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'comparison': {'message': 'Performance comparison available via API'},
                    'summary': 'Performance comparison endpoint available'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying performance: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 19: Analytics Tools (Session 584) =====

    def _query_workflow_analytics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 584: Query workflow execution analytics, performance, and trends.
        Covers 10 endpoints for comprehensive workflow analytics.
        """
        import requests

        query_type = arguments.get('query_type', 'summary')
        workflow_id = arguments.get('workflow_id')
        workflow_ids = arguments.get('workflow_ids', '')
        days = arguments.get('days', 30)
        status_filter = arguments.get('status')
        limit = arguments.get('limit', 100)

        base_url = 'http://localhost:8000'

        try:
            if query_type == 'history':
                params = {'days': days, 'limit': limit}
                if workflow_id:
                    params['workflow_id'] = workflow_id
                if status_filter:
                    params['status'] = status_filter
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/history/', params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'history': data.get('history', []),
                            'total': data.get('total', 0),
                            'days': data.get('days', days),
                            'summary': f"Found {data.get('total', 0)} workflow executions in last {days} days"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'history': [],
                    'summary': 'No workflow execution history found'
                }

            elif query_type == 'trends':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/trends/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'trends': response.json(),
                            'summary': f'Retrieved workflow trends for last {days} days'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'trends': {'labels': [], 'datasets': []},
                    'summary': 'No workflow trends data available'
                }

            elif query_type == 'success_failure':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/success-failure/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'analysis': data,
                            'summary': f"Success/failure analysis for last {days} days"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'analysis': {'success_rate': 0, 'total': 0},
                    'summary': 'No success/failure data available'
                }

            elif query_type == 'performance':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/performance/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'metrics': data.get('metrics', []),
                            'total': data.get('total', 0),
                            'summary': f"Performance metrics for {data.get('total', 0)} workflows"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'metrics': [],
                    'summary': 'No performance metrics available'
                }

            elif query_type == 'performance_comparison':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/performance-comparison/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'comparison': response.json(),
                            'summary': 'Retrieved performance comparison chart data'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'comparison': {'labels': [], 'datasets': []},
                    'summary': 'No comparison data available'
                }

            elif query_type == 'compare':
                if not workflow_ids:
                    return {'success': False, 'error': 'workflow_ids required for compare'}

                try:
                    response = requests.get(
                        f'{base_url}/api/workflow-analytics/compare/',
                        params={'workflow_ids': workflow_ids, 'days': days},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'comparison': response.json(),
                            'summary': f"Compared workflows: {workflow_ids}"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'comparison': {},
                    'summary': 'Workflow comparison not available'
                }

            elif query_type == 'steps':
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required for steps query'}

                try:
                    response = requests.get(
                        f'{base_url}/api/workflow-analytics/steps/{workflow_id}/',
                        params={'days': days},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'step_performance': response.json(),
                            'summary': f"Step performance for workflow {workflow_id}"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'step_performance': {'steps': []},
                    'summary': f'No step data for workflow {workflow_id}'
                }

            elif query_type == 'heatmap':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/heatmap/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'heatmap': response.json(),
                            'summary': f"Execution heatmap for last {days} days"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'heatmap': {'data': []},
                    'summary': 'No heatmap data available'
                }

            elif query_type == 'summary':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/summary/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'summary_data': data,
                            'summary': f"Analytics summary: {data.get('total_executions', 0)} executions, {data.get('success_rate', 0):.1f}% success rate"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'summary_data': {},
                    'summary': 'Analytics summary not available'
                }

            elif query_type == 'dashboard':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/dashboard/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'dashboard': response.json(),
                            'summary': 'Retrieved full analytics dashboard data'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'dashboard': {},
                    'summary': 'Dashboard data not available'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying workflow analytics: {e}")
            return {'success': False, 'error': str(e)}

    def _query_video_analytics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 584: Query video analytics including character performance and lip sync.
        """
        import requests

        query_type = arguments.get('query_type', 'character_performance')
        prediction_id = arguments.get('prediction_id')
        video_url = arguments.get('video_url')
        audio_url = arguments.get('audio_url')

        base_url = 'http://localhost:8000'

        try:
            if query_type == 'character_performance':
                try:
                    response = requests.get(f'{base_url}/api/v1/video/character-performance/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'performance': data,
                            'summary': 'Retrieved character performance metrics'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'performance': {},
                    'summary': 'No character performance data available'
                }

            elif query_type == 'lip_sync':
                if not video_url or not audio_url:
                    return {'success': False, 'error': 'video_url and audio_url required for lip sync'}

                try:
                    response = requests.post(
                        f'{base_url}/api/video/lip-sync/',
                        json={'video_url': video_url, 'audio_url': audio_url},
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        data = response.json()
                        return {
                            'success': True,
                            'job': data,
                            'summary': f"Lip sync job started: {data.get('prediction_id', 'unknown')}"
                        }
                except:
                    pass

                return {
                    'success': False,
                    'error': 'Failed to start lip sync job'
                }

            elif query_type == 'lip_sync_status':
                if not prediction_id:
                    return {'success': False, 'error': 'prediction_id required for status check'}

                try:
                    response = requests.get(f'{base_url}/api/video/lip-sync/status/{prediction_id}/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'status': data,
                            'summary': f"Lip sync status: {data.get('status', 'unknown')}"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'status': {'status': 'unknown'},
                    'summary': f'Could not retrieve status for {prediction_id}'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying video analytics: {e}")
            return {'success': False, 'error': str(e)}

    def _query_model_analytics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 584: Query LLM model performance analytics and preferences.
        """
        import requests

        query_type = arguments.get('query_type', 'performance')
        preferences = arguments.get('preferences', {})

        base_url = 'http://localhost:8000'

        try:
            if query_type == 'performance':
                try:
                    response = requests.get(f'{base_url}/api/v1/analytics/model-performance/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'performance': data,
                            'summary': 'Retrieved model performance analytics'
                        }
                except:
                    pass

                # Try database fallback
                try:
                    from core.models_unified_system import LLMUsage
                    from django.db.models import Avg, Sum, Count
                    from django.utils import timezone
                    from datetime import timedelta

                    thirty_days_ago = timezone.now() - timedelta(days=30)
                    stats = LLMUsage.objects.filter(
                        created_at__gte=thirty_days_ago
                    ).aggregate(
                        total_calls=Count('id'),
                        total_tokens=Sum('total_tokens'),
                        avg_latency=Avg('latency_ms')
                    )

                    return {
                        'success': True,
                        'performance': {
                            'total_calls': stats['total_calls'] or 0,
                            'total_tokens': stats['total_tokens'] or 0,
                            'avg_latency_ms': round(stats['avg_latency'] or 0, 2)
                        },
                        'summary': f"Model usage: {stats['total_calls'] or 0} calls, {stats['total_tokens'] or 0} tokens"
                    }
                except:
                    pass

                return {
                    'success': True,
                    'performance': {},
                    'summary': 'No model performance data available'
                }

            elif query_type == 'preferences':
                try:
                    response = requests.get(f'{base_url}/api/v1/model-preferences/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'preferences': data,
                            'summary': 'Retrieved model preferences'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'preferences': {'model': 'gpt-5-mini'},
                    'summary': 'Default model preferences'
                }

            elif query_type == 'set_preferences':
                if not preferences:
                    return {'success': False, 'error': 'preferences object required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/v1/model-preferences/',
                        json=preferences,
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Model preferences updated'
                        }
                except:
                    pass

                return {
                    'success': False,
                    'error': 'Failed to update model preferences'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying model analytics: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 20: Collaboration & Search Tools (Session 584) =====

    def _query_collaboration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 584: Query agent collaboration data, performance, and network.
        """
        import requests

        query_type = arguments.get('query_type', 'stats')
        agent_name = arguments.get('agent_name')
        task_type = arguments.get('task_type')
        limit = arguments.get('limit', 20)

        base_url = 'http://localhost:8000'

        try:
            if query_type == 'history':
                try:
                    response = requests.get(f'{base_url}/api/collaboration/history/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        history = data.get('history', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'history': history,
                            'summary': f"Found {len(history) if isinstance(history, list) else 'multiple'} collaborations"
                        }
                except:
                    pass

                # Database fallback
                try:
                    from core.models_collaboration import Collaboration
                    collabs = Collaboration.objects.order_by('-created_at')[:limit]
                    history = [{
                        'id': str(c.id),
                        'requester': c.requester,
                        'target_agents': c.target_agents,
                        'status': c.status,
                        'created_at': c.created_at.isoformat()
                    } for c in collabs]
                    return {
                        'success': True,
                        'history': history,
                        'summary': f"Found {len(history)} collaborations"
                    }
                except:
                    pass

                return {
                    'success': True,
                    'history': [],
                    'summary': 'No collaboration history found'
                }

            elif query_type == 'stats':
                try:
                    response = requests.get(f'{base_url}/api/collaboration/stats/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'stats': response.json(),
                            'summary': 'Retrieved collaboration stats'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'stats': {'total': 0, 'success_rate': 0},
                    'summary': 'No collaboration stats available'
                }

            elif query_type == 'find_collaborator':
                params = {}
                if task_type:
                    params['task_type'] = task_type
                try:
                    response = requests.get(f'{base_url}/api/collaboration/find-collaborator/', params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'collaborator': data,
                            'summary': f"Best collaborator: {data.get('agent_name', 'unknown')}"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'collaborator': {},
                    'summary': 'No collaborator recommendation available'
                }

            elif query_type == 'performance':
                params = {'limit': limit}
                if agent_name:
                    params['agent_name'] = agent_name
                try:
                    response = requests.get(f'{base_url}/api/collaboration/performance/', params=params, timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'performance': response.json(),
                            'summary': 'Retrieved agent performance metrics'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'performance': {},
                    'summary': 'No performance data available'
                }

            elif query_type == 'top_performers':
                try:
                    response = requests.get(f'{base_url}/api/collaboration/top-performers/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        performers = data.get('performers', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'performers': performers,
                            'summary': f"Top {len(performers) if isinstance(performers, list) else 'multiple'} performers"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'performers': [],
                    'summary': 'No top performers data available'
                }

            elif query_type == 'network':
                try:
                    response = requests.get(f'{base_url}/api/collective/network/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'network': response.json(),
                            'summary': 'Retrieved collaboration network'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'network': {'nodes': [], 'edges': []},
                    'summary': 'No network data available'
                }

            elif query_type == 'monitor':
                try:
                    response = requests.get(f'{base_url}/api/collective/monitor/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'monitor': response.json(),
                            'summary': 'Retrieved collaboration monitor data'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'monitor': {},
                    'summary': 'No monitor data available'
                }

            elif query_type == 'dashboard':
                try:
                    response = requests.get(f'{base_url}/api/dashboard/collaboration/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'dashboard': response.json(),
                            'summary': 'Retrieved collaboration dashboard'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'dashboard': {},
                    'summary': 'No dashboard data available'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying collaboration: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_favorites(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 584: Manage favorites and batch operations for images, videos, workflows.
        """
        import requests

        action = arguments.get('action', 'list_images')
        item_id = arguments.get('item_id')
        item_ids = arguments.get('item_ids', [])

        base_url = 'http://localhost:8000'

        try:
            if action == 'list_images':
                try:
                    from core.models_unified_system import GeneratedImage
                    favorites = GeneratedImage.objects.filter(is_favorite=True).order_by('-created_at')[:50]
                    images = [{
                        'id': str(img.id),
                        'prompt': img.prompt[:100] if img.prompt else '',
                        'created_at': img.created_at.isoformat()
                    } for img in favorites]
                    return {
                        'success': True,
                        'favorites': images,
                        'summary': f"Found {len(images)} favorite images"
                    }
                except:
                    pass

                return {
                    'success': True,
                    'favorites': [],
                    'summary': 'No favorite images found'
                }

            elif action == 'list_videos':
                try:
                    from core.models_unified_system import GeneratedVideo
                    favorites = GeneratedVideo.objects.filter(is_favorite=True).order_by('-created_at')[:50]
                    videos = [{
                        'id': str(v.id),
                        'prompt': v.prompt[:100] if v.prompt else '',
                        'created_at': v.created_at.isoformat()
                    } for v in favorites]
                    return {
                        'success': True,
                        'favorites': videos,
                        'summary': f"Found {len(videos)} favorite videos"
                    }
                except:
                    pass

                return {
                    'success': True,
                    'favorites': [],
                    'summary': 'No favorite videos found'
                }

            elif action == 'list_workflows':
                try:
                    response = requests.get(f'{base_url}/api/workflows/favorites/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        favorites = data.get('favorites', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'favorites': favorites,
                            'summary': f"Found {len(favorites) if isinstance(favorites, list) else 'multiple'} favorite workflows"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'favorites': [],
                    'summary': 'No favorite workflows found'
                }

            elif action == 'toggle_image':
                if not item_id:
                    return {'success': False, 'error': 'item_id required'}

                try:
                    response = requests.post(f'{base_url}/api/images/{item_id}/favorite/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'is_favorite': data.get('is_favorite'),
                            'summary': f"Image favorite toggled: {data.get('is_favorite')}"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Failed to toggle image favorite'}

            elif action == 'toggle_video':
                if not item_id:
                    return {'success': False, 'error': 'item_id required'}

                try:
                    response = requests.post(f'{base_url}/api/v1/video/history/{item_id}/favorite/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'is_favorite': data.get('is_favorite'),
                            'summary': f"Video favorite toggled: {data.get('is_favorite')}"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Failed to toggle video favorite'}

            elif action == 'toggle_workflow':
                if not item_id:
                    return {'success': False, 'error': 'item_id required'}

                try:
                    response = requests.post(f'{base_url}/api/workflows/history/{item_id}/toggle-favorite/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'is_favorite': data.get('is_favorite'),
                            'summary': f"Workflow favorite toggled: {data.get('is_favorite')}"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Failed to toggle workflow favorite'}

            elif action == 'batch_download':
                if not item_ids:
                    return {'success': False, 'error': 'item_ids required for batch download'}

                try:
                    response = requests.post(
                        f'{base_url}/api/images/batch-download/',
                        json={'image_ids': item_ids},
                        timeout=30
                    )
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'download_url': response.headers.get('Content-Disposition', 'download ready'),
                            'summary': f"Batch download prepared for {len(item_ids)} images"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Failed to prepare batch download'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing favorites: {e}")
            return {'success': False, 'error': str(e)}

    def _query_semantic_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 584: Perform semantic search and RAG operations.
        """
        import requests

        query_type = arguments.get('query_type', 'search')
        query = arguments.get('query', '')
        limit = arguments.get('limit', 10)

        base_url = 'http://localhost:8000'

        try:
            if query_type == 'search':
                if not query:
                    return {'success': False, 'error': 'query required for search'}

                try:
                    response = requests.post(
                        f'{base_url}/api/v1/rag/semantic-search/',
                        json={'query': query, 'limit': limit},
                        timeout=15
                    )
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('results', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'results': results,
                            'summary': f"Found {len(results) if isinstance(results, list) else 'multiple'} semantic matches"
                        }
                except:
                    pass

                # Try spider semantic search fallback
                try:
                    from core.services.spider_semantic_search import get_spider_semantic_search_service
                    service = get_spider_semantic_search_service()
                    results = service.semantic_search(query, limit=limit)
                    return {
                        'success': True,
                        'results': results,
                        'summary': f"Found {len(results)} semantic matches via spider search"
                    }
                except:
                    pass

                return {
                    'success': True,
                    'results': [],
                    'summary': 'No semantic search results'
                }

            elif query_type == 'generate':
                if not query:
                    return {'success': False, 'error': 'query required for RAG generation'}

                try:
                    response = requests.post(
                        f'{base_url}/api/v1/rag/generate/',
                        json={'query': query},
                        timeout=30
                    )
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'answer': data.get('answer', data.get('response', '')),
                            'sources': data.get('sources', []),
                            'summary': 'Generated RAG answer'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'answer': '',
                    'sources': [],
                    'summary': 'RAG generation not available'
                }

            elif query_type == 'stats':
                try:
                    response = requests.get(f'{base_url}/api/v1/rag/stats/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'stats': data,
                            'summary': f"Embeddings: {data.get('total_embeddings', 0)}, Documents: {data.get('total_documents', 0)}"
                        }
                except:
                    pass

                # Database fallback
                try:
                    from core.models_unified_system import DocumentEmbedding, RAGDocument
                    embed_count = DocumentEmbedding.objects.count()
                    doc_count = RAGDocument.objects.count()
                    return {
                        'success': True,
                        'stats': {
                            'total_embeddings': embed_count,
                            'total_documents': doc_count
                        },
                        'summary': f"Embeddings: {embed_count}, Documents: {doc_count}"
                    }
                except:
                    pass

                return {
                    'success': True,
                    'stats': {},
                    'summary': 'No embeddings stats available'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 21: Project & Workflow Collaboration Tools (Session 585) =====

    def _manage_project_collaboration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage shared projects and collaborators.
        """
        try:
            import requests
            action = arguments.get('action', 'list_projects')
            base_url = 'http://localhost:8000/api/projects/shared'

            if action == 'list_projects':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        projects = response.json()
                        project_list = projects if isinstance(projects, list) else projects.get('projects', [])
                        return {
                            'success': True,
                            'projects': project_list[:20],
                            'total': len(project_list),
                            'summary': f"Found {len(project_list)} shared projects"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback - query SharedProject model directly
                from core.models_unified_system import SharedProject
                projects = SharedProject.objects.all()[:20]
                return {
                    'success': True,
                    'projects': [{'id': str(p.id), 'name': p.name if hasattr(p, 'name') else str(p)} for p in projects],
                    'total': SharedProject.objects.count(),
                    'summary': f"Found {SharedProject.objects.count()} shared projects"
                }

            elif action == 'get_project':
                project_id = arguments.get('project_id')
                if not project_id:
                    return {'success': False, 'error': 'project_id required'}
                try:
                    response = requests.get(f'{base_url}/{project_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'project': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Could not retrieve project'}

            elif action == 'invite':
                project_id = arguments.get('project_id')
                user_email = arguments.get('user_email')
                role = arguments.get('role', 'editor')
                if not project_id or not user_email:
                    return {'success': False, 'error': 'project_id and user_email required'}
                try:
                    response = requests.post(
                        f'{base_url}/{project_id}/invite/',
                        json={'email': user_email, 'role': role},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': f'Invitation sent to {user_email}' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'list_invitations':
                try:
                    response = requests.get(f'{base_url}/invitations/', timeout=10)
                    if response.status_code == 200:
                        invitations = response.json()
                        inv_list = invitations if isinstance(invitations, list) else invitations.get('invitations', [])
                        return {
                            'success': True,
                            'invitations': inv_list,
                            'total': len(inv_list),
                            'summary': f"Found {len(inv_list)} pending invitations"
                        }
                except:
                    pass
                return {'success': True, 'invitations': [], 'summary': 'No invitations found'}

            elif action == 'accept_invitation':
                invitation_id = arguments.get('invitation_id')
                if not invitation_id:
                    return {'success': False, 'error': 'invitation_id required'}
                try:
                    response = requests.post(f'{base_url}/invitations/{invitation_id}/accept/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Invitation accepted' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'decline_invitation':
                invitation_id = arguments.get('invitation_id')
                if not invitation_id:
                    return {'success': False, 'error': 'invitation_id required'}
                try:
                    response = requests.post(f'{base_url}/invitations/{invitation_id}/decline/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Invitation declined' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'list_collaborators':
                project_id = arguments.get('project_id')
                if not project_id:
                    return {'success': False, 'error': 'project_id required'}
                try:
                    response = requests.get(f'{base_url}/{project_id}/collaborators/', timeout=10)
                    if response.status_code == 200:
                        collaborators = response.json()
                        collab_list = collaborators if isinstance(collaborators, list) else collaborators.get('collaborators', [])
                        return {
                            'success': True,
                            'collaborators': collab_list,
                            'total': len(collab_list),
                            'summary': f"Found {len(collab_list)} collaborators"
                        }
                except:
                    pass
                return {'success': True, 'collaborators': [], 'summary': 'No collaborators found'}

            elif action == 'remove_collaborator':
                project_id = arguments.get('project_id')
                user_id = arguments.get('user_id')
                if not project_id or not user_id:
                    return {'success': False, 'error': 'project_id and user_id required'}
                try:
                    response = requests.delete(f'{base_url}/{project_id}/collaborators/{user_id}/', timeout=10)
                    return {
                        'success': response.status_code in [200, 204],
                        'message': 'Collaborator removed' if response.status_code in [200, 204] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'get_activity':
                project_id = arguments.get('project_id')
                if not project_id:
                    return {'success': False, 'error': 'project_id required'}
                try:
                    response = requests.get(f'{base_url}/{project_id}/activity/', timeout=10)
                    if response.status_code == 200:
                        activity = response.json()
                        activity_list = activity if isinstance(activity, list) else activity.get('activity', [])
                        return {
                            'success': True,
                            'activity': activity_list[:20],
                            'summary': f"Found {len(activity_list)} activity items"
                        }
                except:
                    pass
                return {'success': True, 'activity': [], 'summary': 'No activity found'}

            elif action == 'get_comments':
                project_id = arguments.get('project_id')
                if not project_id:
                    return {'success': False, 'error': 'project_id required'}
                try:
                    response = requests.get(f'{base_url}/{project_id}/comments/', timeout=10)
                    if response.status_code == 200:
                        comments = response.json()
                        comment_list = comments if isinstance(comments, list) else comments.get('comments', [])
                        return {
                            'success': True,
                            'comments': comment_list[:20],
                            'summary': f"Found {len(comment_list)} comments"
                        }
                except:
                    pass
                return {'success': True, 'comments': [], 'summary': 'No comments found'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing project collaboration: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_workflow_sharing(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Share and collaborate on workflows.
        """
        try:
            import requests
            action = arguments.get('action', 'list_shared')
            base_url = 'http://localhost:8000/api/v1/workflows'

            if action == 'list_shared':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        workflows = response.json()
                        wf_list = workflows if isinstance(workflows, list) else workflows.get('workflows', [])
                        # Filter to shared workflows if possible
                        shared = [w for w in wf_list if w.get('is_shared', True)]
                        return {
                            'success': True,
                            'workflows': shared[:20],
                            'total': len(shared),
                            'summary': f"Found {len(shared)} shared workflows"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback
                from core.models_unified_system import PublishedWorkflow
                workflows = PublishedWorkflow.objects.all()[:20]
                return {
                    'success': True,
                    'workflows': [{'id': str(w.id), 'name': w.name if hasattr(w, 'name') else str(w)} for w in workflows],
                    'total': PublishedWorkflow.objects.count(),
                    'summary': f"Found {PublishedWorkflow.objects.count()} shared workflows"
                }

            elif action == 'share':
                workflow_id = arguments.get('workflow_id')
                user_email = arguments.get('user_email')
                permissions = arguments.get('permissions', 'view')
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/{workflow_id}/share/',
                        json={'email': user_email, 'permissions': permissions},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': f'Workflow shared with {user_email}' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'collaborate':
                workflow_id = arguments.get('workflow_id')
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/collaborate/',
                        json={'workflow_id': workflow_id},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, 'collaboration': response.json()}
                except:
                    pass

                # Try alternate endpoint
                try:
                    response = requests.get(f'{base_url}/{workflow_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'workflow': response.json(),
                            'message': 'Workflow ready for collaboration'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not initiate collaboration'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing workflow sharing: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 22: Team Workflows & Agent Evolution Tools (Session 585) =====

    def _manage_team_workflows(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage team workflows - create, start, execute, and monitor.
        """
        try:
            import requests
            action = arguments.get('action', 'list_active')
            base_url = 'http://localhost:8000/api/teams/workflows'

            if action == 'list_active':
                try:
                    response = requests.get(f'{base_url}/active/', timeout=10)
                    if response.status_code == 200:
                        workflows = response.json()
                        wf_list = workflows if isinstance(workflows, list) else workflows.get('workflows', [])
                        return {
                            'success': True,
                            'workflows': wf_list[:20],
                            'total': len(wf_list),
                            'summary': f"Found {len(wf_list)} active team workflows"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback
                from core.models_unified_system import TeamWorkflow
                workflows = TeamWorkflow.objects.filter(status='active')[:20]
                return {
                    'success': True,
                    'workflows': [{'id': str(w.id), 'name': w.name} for w in workflows],
                    'total': workflows.count(),
                    'summary': f"Found {workflows.count()} active team workflows"
                }

            elif action == 'list_templates':
                try:
                    response = requests.get(f'{base_url}/templates/', timeout=10)
                    if response.status_code == 200:
                        templates = response.json()
                        tmpl_list = templates if isinstance(templates, list) else templates.get('templates', [])
                        return {
                            'success': True,
                            'templates': tmpl_list[:20],
                            'total': len(tmpl_list),
                            'summary': f"Found {len(tmpl_list)} workflow templates"
                        }
                except:
                    pass
                return {'success': True, 'templates': [], 'summary': 'No templates found'}

            elif action == 'create':
                name = arguments.get('name', 'New Workflow')
                steps = arguments.get('steps', [])
                try:
                    response = requests.post(
                        f'{base_url}/',
                        json={'name': name, 'steps': steps},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': f'Workflow "{name}" created' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'start':
                workflow_id = arguments.get('workflow_id')
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required'}
                try:
                    response = requests.post(f'{base_url}/{workflow_id}/start/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Workflow started' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'status':
                workflow_id = arguments.get('workflow_id')
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required'}
                try:
                    response = requests.get(f'{base_url}/{workflow_id}/status/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'status': response.json()}
                except:
                    pass

                # Try getting workflow detail
                try:
                    response = requests.get(f'{base_url}/{workflow_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'workflow': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Could not get workflow status'}

            elif action == 'execute':
                workflow_id = arguments.get('workflow_id')
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required'}
                try:
                    response = requests.post(f'{base_url}/{workflow_id}/execute/', timeout=30)
                    return {
                        'success': response.status_code == 200,
                        'result': response.json() if response.status_code == 200 else None,
                        'message': 'Workflow executed' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'run_full':
                workflow_id = arguments.get('workflow_id')
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required'}
                try:
                    response = requests.post(f'{base_url}/{workflow_id}/run/', timeout=60)
                    return {
                        'success': response.status_code == 200,
                        'result': response.json() if response.status_code == 200 else None,
                        'message': 'Full workflow run completed' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'execute_step':
                workflow_id = arguments.get('workflow_id')
                step_id = arguments.get('step_id')
                if not workflow_id or not step_id:
                    return {'success': False, 'error': 'workflow_id and step_id required'}
                try:
                    response = requests.post(f'{base_url}/{workflow_id}/steps/{step_id}/execute/', timeout=30)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Step executed' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'complete_step':
                workflow_id = arguments.get('workflow_id')
                step_id = arguments.get('step_id')
                if not workflow_id or not step_id:
                    return {'success': False, 'error': 'workflow_id and step_id required'}
                try:
                    response = requests.post(f'{base_url}/{workflow_id}/steps/{step_id}/complete/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Step completed' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing team workflows: {e}")
            return {'success': False, 'error': str(e)}

    def _query_agent_evolution(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query agent evolution, XP, levels, and abilities.
        """
        try:
            import requests
            query_type = arguments.get('query_type', 'overview')
            limit = arguments.get('limit', 10)
            base_url = 'http://localhost:8000/api/agent-evolution'

            if query_type == 'overview':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'overview': data,
                            'summary': f"Evolution overview retrieved"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback
                from core.models_unified_system import AgentEvolution
                evolutions = AgentEvolution.objects.all()[:limit]
                return {
                    'success': True,
                    'evolutions': [
                        {
                            'agent': e.agent.name if e.agent else 'Unknown',
                            'level': e.current_level,
                            'xp': e.total_xp
                        }
                        for e in evolutions
                    ],
                    'total': AgentEvolution.objects.count(),
                    'summary': f"Found {AgentEvolution.objects.count()} agent evolutions"
                }

            elif query_type == 'agent_detail':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.get(f'{base_url}/agent/{agent_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'evolution': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Could not retrieve agent evolution'}

            elif query_type == 'leaderboard':
                try:
                    response = requests.get(f'{base_url}/leaderboard/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        leaders = data if isinstance(data, list) else data.get('leaderboard', [])
                        return {
                            'success': True,
                            'leaderboard': leaders[:limit],
                            'summary': f"Top {min(limit, len(leaders))} agents by XP"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback
                from core.models_unified_system import AgentEvolution
                leaders = AgentEvolution.objects.order_by('-total_xp')[:limit]
                return {
                    'success': True,
                    'leaderboard': [
                        {
                            'rank': i + 1,
                            'agent': e.agent.name if e.agent else 'Unknown',
                            'level': e.current_level,
                            'xp': e.total_xp
                        }
                        for i, e in enumerate(leaders)
                    ],
                    'summary': f"Top {leaders.count()} agents by XP"
                }

            elif query_type == 'abilities':
                try:
                    response = requests.get(f'{base_url}/abilities/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        abilities = data if isinstance(data, list) else data.get('abilities', [])
                        return {
                            'success': True,
                            'abilities': abilities[:20],
                            'total': len(abilities),
                            'summary': f"Found {len(abilities)} available abilities"
                        }
                except:
                    pass
                return {'success': True, 'abilities': [], 'summary': 'No abilities found'}

            elif query_type == 'xp_gains':
                try:
                    response = requests.get(f'{base_url}/xp-gains/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        gains = data if isinstance(data, list) else data.get('xp_gains', [])
                        return {
                            'success': True,
                            'xp_gains': gains[:limit],
                            'summary': f"Found {len(gains)} recent XP gains"
                        }
                except:
                    pass
                return {'success': True, 'xp_gains': [], 'summary': 'No XP gains found'}

            elif query_type == 'award_xp':
                agent_id = arguments.get('agent_id')
                xp_amount = arguments.get('xp_amount', 10)
                reason = arguments.get('reason', 'Manual award')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/agent/{agent_id}/award-xp/',
                        json={'xp': xp_amount, 'reason': reason},
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': f'Awarded {xp_amount} XP' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'unlock_ability':
                agent_id = arguments.get('agent_id')
                ability_id = arguments.get('ability_id')
                if not agent_id or not ability_id:
                    return {'success': False, 'error': 'agent_id and ability_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/agent/{agent_id}/unlock/{ability_id}/',
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Ability unlocked' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying agent evolution: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 23: Voice Marketplace & Agent Relationships Tools (Session 586) =====

    def _manage_voice_marketplace(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Manage voice cloning and TTS marketplace."""
        try:
            import requests
            action = arguments.get('action')
            base_url = 'http://localhost:8000/api/voice-marketplace'

            if action == 'browse':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        voices = data if isinstance(data, list) else data.get('voices', [])
                        return {
                            'success': True,
                            'voices': voices[:20],
                            'total': len(voices),
                            'summary': f"Found {len(voices)} voices in marketplace"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback
                from core.models_voice_marketplace import Voice
                voices = Voice.objects.filter(is_published=True)[:20]
                return {
                    'success': True,
                    'voices': [
                        {
                            'id': str(v.id),
                            'name': v.name,
                            'description': v.description[:100] if v.description else '',
                            'price': float(v.price_per_use) if hasattr(v, 'price_per_use') else 0
                        }
                        for v in voices
                    ],
                    'total': Voice.objects.filter(is_published=True).count(),
                    'summary': f"Found {voices.count()} published voices"
                }

            elif action == 'my_voices':
                try:
                    response = requests.get(f'{base_url}/my-voices/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'voices': response.json()}
                except:
                    pass
                return {'success': True, 'voices': [], 'message': 'No voices found'}

            elif action == 'earnings':
                try:
                    response = requests.get(f'{base_url}/earnings/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'earnings': response.json()}
                except:
                    pass
                return {'success': True, 'earnings': {'total': 0, 'pending': 0}}

            elif action == 'transactions':
                try:
                    response = requests.get(f'{base_url}/transactions/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'transactions': response.json()}
                except:
                    pass
                return {'success': True, 'transactions': []}

            elif action == 'detail':
                voice_id = arguments.get('voice_id')
                if not voice_id:
                    return {'success': False, 'error': 'voice_id required'}
                try:
                    response = requests.get(f'{base_url}/{voice_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'voice': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Voice not found'}

            elif action == 'create':
                elevenlabs_id = arguments.get('elevenlabs_voice_id')
                name = arguments.get('name')
                if not elevenlabs_id or not name:
                    return {'success': False, 'error': 'elevenlabs_voice_id and name required'}
                try:
                    response = requests.post(
                        f'{base_url}/create/',
                        json={'elevenlabs_voice_id': elevenlabs_id, 'name': name},
                        timeout=30
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'voice': response.json() if response.status_code in [200, 201] else None,
                        'message': 'Voice created' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'clone_start':
                try:
                    response = requests.post(f'{base_url}/clone/start/', json=arguments, timeout=30)
                    return {
                        'success': response.status_code in [200, 201],
                        'request': response.json() if response.status_code in [200, 201] else None
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'clone_status':
                request_id = arguments.get('request_id')
                if not request_id:
                    return {'success': False, 'error': 'request_id required'}
                try:
                    response = requests.get(f'{base_url}/clone/{request_id}/status/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'status': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Clone request not found'}

            elif action == 'publish':
                voice_id = arguments.get('voice_id')
                if not voice_id:
                    return {'success': False, 'error': 'voice_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/{voice_id}/publish/',
                        json={'price': arguments.get('price', 0)},
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Voice published' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'unpublish':
                voice_id = arguments.get('voice_id')
                if not voice_id:
                    return {'success': False, 'error': 'voice_id required'}
                try:
                    response = requests.post(f'{base_url}/{voice_id}/unpublish/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Voice unpublished' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'generate':
                voice_id = arguments.get('voice_id')
                text = arguments.get('text')
                if not voice_id or not text:
                    return {'success': False, 'error': 'voice_id and text required'}
                try:
                    response = requests.post(
                        f'{base_url}/{voice_id}/generate/',
                        json={'text': text},
                        timeout=60
                    )
                    return {
                        'success': response.status_code == 200,
                        'audio_url': response.json().get('audio_url') if response.status_code == 200 else None,
                        'message': 'Speech generated' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'preview':
                voice_id = arguments.get('voice_id')
                if not voice_id:
                    return {'success': False, 'error': 'voice_id required'}
                try:
                    response = requests.get(f'{base_url}/{voice_id}/preview/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'preview': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Preview not available'}

            elif action == 'add_review':
                voice_id = arguments.get('voice_id')
                rating = arguments.get('rating')
                review_text = arguments.get('review_text', '')
                if not voice_id or not rating:
                    return {'success': False, 'error': 'voice_id and rating required'}
                try:
                    response = requests.post(
                        f'{base_url}/{voice_id}/reviews/',
                        json={'rating': rating, 'text': review_text},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': 'Review added' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'update':
                voice_id = arguments.get('voice_id')
                if not voice_id:
                    return {'success': False, 'error': 'voice_id required'}
                update_data = {}
                if arguments.get('name'):
                    update_data['name'] = arguments['name']
                if arguments.get('description'):
                    update_data['description'] = arguments['description']
                try:
                    response = requests.post(
                        f'{base_url}/{voice_id}/update/',
                        json=update_data,
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Voice updated' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing voice marketplace: {e}")
            return {'success': False, 'error': str(e)}

    def _query_agent_relationships(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Query agent relationships, alliances, and rivalries."""
        try:
            import requests
            query_type = arguments.get('query_type')
            base_url = 'http://localhost:8000/api/agent-relationships'

            if query_type == 'overview':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'relationships': data,
                            'summary': f"Agent relationships overview"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback
                from core.models_unified_system import AgentRelationship
                relationships = AgentRelationship.objects.all()[:20]
                return {
                    'success': True,
                    'relationships': [
                        {
                            'id': str(r.id),
                            'agent_from': r.agent_from.name if r.agent_from else 'Unknown',
                            'agent_to': r.agent_to.name if r.agent_to else 'Unknown',
                            'type': r.relationship_type,
                            'strength': r.strength
                        }
                        for r in relationships
                    ],
                    'total': AgentRelationship.objects.count(),
                    'summary': f"Found {relationships.count()} relationships"
                }

            elif query_type == 'agent_detail':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.get(f'{base_url}/agent/{agent_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'relationships': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Could not retrieve agent relationships'}

            elif query_type == 'create':
                agent_a_id = arguments.get('agent_a_id')
                agent_b_id = arguments.get('agent_b_id')
                rel_type = arguments.get('relationship_type', 'peer')
                if not agent_a_id or not agent_b_id:
                    return {'success': False, 'error': 'agent_a_id and agent_b_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/create/',
                        json={
                            'agent_a_id': agent_a_id,
                            'agent_b_id': agent_b_id,
                            'relationship_type': rel_type
                        },
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'relationship': response.json() if response.status_code in [200, 201] else None,
                        'message': 'Relationship created' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'interact':
                relationship_id = arguments.get('relationship_id')
                if not relationship_id:
                    return {'success': False, 'error': 'relationship_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/relationship/{relationship_id}/interact/',
                        json=arguments,
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Interaction recorded' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'events':
                relationship_id = arguments.get('relationship_id')
                if not relationship_id:
                    return {'success': False, 'error': 'relationship_id required'}
                try:
                    response = requests.get(
                        f'{base_url}/relationship/{relationship_id}/events/',
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, 'events': response.json()}
                except:
                    pass
                return {'success': True, 'events': []}

            elif query_type == 'auto_generate':
                try:
                    response = requests.post(f'{base_url}/auto-generate/', timeout=30)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Relationships auto-generated' if response.status_code == 200 else response.text,
                        'result': response.json() if response.status_code == 200 else None
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'alliance_detail':
                alliance_id = arguments.get('alliance_id')
                if not alliance_id:
                    return {'success': False, 'error': 'alliance_id required'}
                try:
                    response = requests.get(f'{base_url}/alliances/{alliance_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'alliance': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Alliance not found'}

            elif query_type == 'alliance_create':
                alliance_name = arguments.get('alliance_name')
                member_ids = arguments.get('member_ids', [])
                if not alliance_name:
                    return {'success': False, 'error': 'alliance_name required'}
                try:
                    response = requests.post(
                        f'{base_url}/alliances/create/',
                        json={'name': alliance_name, 'member_ids': member_ids},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'alliance': response.json() if response.status_code in [200, 201] else None,
                        'message': 'Alliance created' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'alliance_add':
                alliance_id = arguments.get('alliance_id')
                agent_id = arguments.get('agent_id')
                if not alliance_id or not agent_id:
                    return {'success': False, 'error': 'alliance_id and agent_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/alliances/{alliance_id}/add/',
                        json={'agent_id': agent_id},
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Member added to alliance' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'alliance_disband':
                alliance_id = arguments.get('alliance_id')
                if not alliance_id:
                    return {'success': False, 'error': 'alliance_id required'}
                try:
                    response = requests.post(f'{base_url}/alliances/{alliance_id}/disband/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Alliance disbanded' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'rivalry_detail':
                rivalry_id = arguments.get('rivalry_id')
                if not rivalry_id:
                    return {'success': False, 'error': 'rivalry_id required'}
                try:
                    response = requests.get(f'{base_url}/rivalries/{rivalry_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'rivalry': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Rivalry not found'}

            elif query_type == 'rivalry_create':
                agent_a_id = arguments.get('agent_a_id')
                agent_b_id = arguments.get('agent_b_id')
                if not agent_a_id or not agent_b_id:
                    return {'success': False, 'error': 'agent_a_id and agent_b_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/rivalries/create/',
                        json={'agent_a_id': agent_a_id, 'agent_b_id': agent_b_id},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'rivalry': response.json() if response.status_code in [200, 201] else None,
                        'message': 'Rivalry created' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'rivalry_compete':
                rivalry_id = arguments.get('rivalry_id')
                winner_id = arguments.get('winner_id')
                if not rivalry_id or not winner_id:
                    return {'success': False, 'error': 'rivalry_id and winner_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/rivalries/{rivalry_id}/compete/',
                        json={'winner_id': winner_id},
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Competition recorded' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'rivalry_end':
                rivalry_id = arguments.get('rivalry_id')
                if not rivalry_id:
                    return {'success': False, 'error': 'rivalry_id required'}
                try:
                    response = requests.post(f'{base_url}/rivalries/{rivalry_id}/end/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Rivalry ended' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying agent relationships: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 24: Hive Mind & Time Capsules (Session 587) =====

    def _manage_hive_mind(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 587: Manage Hive Mind sessions - multi-agent collective intelligence.
        """
        action = arguments.get('action', 'list')
        base_url = 'http://localhost:8000/api/hive-mind'

        try:
            if action == 'start':
                question = arguments.get('question')
                if not question:
                    return {'success': False, 'error': 'question required to start Hive Mind session'}

                context = arguments.get('context', '')
                max_agents = min(arguments.get('max_agents', 8), 12)

                try:
                    response = requests.post(
                        f'{base_url}/start/',
                        json={
                            'question': question,
                            'context': context,
                            'max_agents': max_agents
                        },
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        data = response.json()
                        return {
                            'success': True,
                            'session_id': data.get('session_id'),
                            'status': data.get('status'),
                            'participants': data.get('participants', []),
                            'participant_count': data.get('participant_count', 0),
                            'message': data.get('message', 'Hive Mind session started')
                        }
                    return {'success': False, 'error': response.text}
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'status':
                session_id = arguments.get('session_id')
                if not session_id:
                    return {'success': False, 'error': 'session_id required'}

                try:
                    response = requests.get(f'{base_url}/session/{session_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                    return {'success': False, 'error': 'Session not found'}
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'list':
                limit = arguments.get('limit', 10)
                try:
                    response = requests.get(f'{base_url}/sessions/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback to direct DB query
                from core.models import HiveMindSession
                sessions = HiveMindSession.objects.order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'sessions': [
                        {
                            'id': str(s.id),
                            'question': s.question[:100] if s.question else '',
                            'status': s.status,
                            'participant_count': len(s.participant_ids) if s.participant_ids else 0,
                            'created_at': s.created_at.isoformat() if s.created_at else None
                        }
                        for s in sessions
                    ],
                    'total': sessions.count()
                }

            elif action == 'agents':
                try:
                    response = requests.get(f'{base_url}/agents/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback to direct DB query
                from core.models_unified_system import Agent
                agents = Agent.objects.filter(is_active=True).order_by('name')[:20]
                return {
                    'success': True,
                    'agents': [
                        {
                            'id': str(a.id),
                            'name': a.name,
                            'specialization': a.specialization or ''
                        }
                        for a in agents
                    ]
                }

            elif action == 'preview':
                question = arguments.get('question')
                if not question:
                    return {'success': False, 'error': 'question required for preview'}

                try:
                    response = requests.post(
                        f'{base_url}/preview/',
                        json={'question': question, 'max_agents': arguments.get('max_agents', 8)},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Preview not available'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing Hive Mind: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_time_capsules(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 587: Manage agent time capsules - messages from agents to their future selves.
        """
        action = arguments.get('action', 'overview')
        base_url = 'http://localhost:8000/api/time-capsules'

        try:
            if action == 'overview':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback to direct DB query
                from core.models_unified_system import TimeCapsule
                from django.utils import timezone
                total = TimeCapsule.objects.count()
                revealed = TimeCapsule.objects.filter(status='revealed').count()
                ready = TimeCapsule.objects.filter(
                    status='sealed',
                    reveal_at__lte=timezone.now()
                ).count()
                recent = TimeCapsule.objects.order_by('-created_at')[:5]
                return {
                    'success': True,
                    'stats': {
                        'total': total,
                        'revealed': revealed,
                        'sealed': total - revealed,
                        'ready_to_reveal': ready
                    },
                    'recent': [
                        {
                            'id': str(c.id),
                            'title': c.title or '',
                            'trigger': c.trigger or '',
                            'status': c.status,
                            'reveal_at': c.reveal_at.isoformat() if c.reveal_at else None,
                            'created_at': c.created_at.isoformat()
                        }
                        for c in recent
                    ]
                }

            elif action == 'list_agent':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.get(f'{base_url}/agent/{agent_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import TimeCapsule
                capsules = TimeCapsule.objects.filter(agent_id=agent_id).order_by('-created_at')[:10]
                return {
                    'success': True,
                    'capsules': [
                        {
                            'id': str(c.id),
                            'title': c.title or '',
                            'trigger': c.trigger or '',
                            'status': c.status,
                            'reveal_at': c.reveal_at.isoformat() if c.reveal_at else None
                        }
                        for c in capsules
                    ]
                }

            elif action == 'create':
                agent_id = arguments.get('agent_id')
                message = arguments.get('message')
                if not agent_id or not message:
                    return {'success': False, 'error': 'agent_id and message required'}

                capsule_type = arguments.get('capsule_type', 'reflection')
                reveal_days = arguments.get('reveal_days', 7)

                try:
                    response = requests.post(
                        f'{base_url}/agent/{agent_id}/',
                        json={
                            'message': message,
                            'capsule_type': capsule_type,
                            'reveal_days': reveal_days
                        },
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback to direct creation
                from core.models_unified_system import TimeCapsule, Agent
                from django.utils import timezone
                from datetime import timedelta
                try:
                    agent = Agent.objects.get(id=agent_id)
                    capsule = TimeCapsule.objects.create(
                        agent=agent,
                        title='Time Capsule Message',
                        message=message,
                        trigger=capsule_type,  # Uses 'trigger' field
                        status='sealed',
                        reveal_at=timezone.now() + timedelta(days=reveal_days)
                    )
                    return {
                        'success': True,
                        'capsule_id': str(capsule.id),
                        'reveal_at': capsule.reveal_at.isoformat(),
                        'message': f'Time capsule created for {agent.name}'
                    }
                except Agent.DoesNotExist:
                    return {'success': False, 'error': 'Agent not found'}

            elif action == 'detail':
                capsule_id = arguments.get('capsule_id')
                if not capsule_id:
                    return {'success': False, 'error': 'capsule_id required'}
                try:
                    response = requests.get(f'{base_url}/{capsule_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import TimeCapsule
                try:
                    capsule = TimeCapsule.objects.select_related('agent').get(id=capsule_id)
                    is_revealed = capsule.status == 'revealed'
                    return {
                        'success': True,
                        'capsule': {
                            'id': str(capsule.id),
                            'title': capsule.title or '',
                            'agent_name': capsule.agent.name if capsule.agent else 'Unknown',
                            'trigger': capsule.trigger or '',
                            'message': capsule.message if is_revealed else '[SEALED]',
                            'status': capsule.status,
                            'reveal_at': capsule.reveal_at.isoformat() if capsule.reveal_at else None,
                            'created_at': capsule.created_at.isoformat()
                        }
                    }
                except TimeCapsule.DoesNotExist:
                    return {'success': False, 'error': 'Capsule not found'}

            elif action == 'reveal':
                capsule_id = arguments.get('capsule_id')
                if not capsule_id:
                    return {'success': False, 'error': 'capsule_id required'}
                try:
                    response = requests.post(f'{base_url}/{capsule_id}/reveal/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import TimeCapsule
                from django.utils import timezone
                try:
                    capsule = TimeCapsule.objects.get(id=capsule_id)
                    if capsule.status == 'revealed':
                        return {'success': False, 'error': 'Capsule already revealed'}
                    if capsule.reveal_at and capsule.reveal_at > timezone.now():
                        return {'success': False, 'error': f'Capsule not ready until {capsule.reveal_at}'}
                    capsule.status = 'revealed'
                    capsule.revealed_at = timezone.now()
                    capsule.save()
                    return {
                        'success': True,
                        'message': capsule.message,
                        'revealed_at': capsule.revealed_at.isoformat()
                    }
                except TimeCapsule.DoesNotExist:
                    return {'success': False, 'error': 'Capsule not found'}

            elif action == 'react':
                capsule_id = arguments.get('capsule_id')
                reaction = arguments.get('reaction')
                if not capsule_id or not reaction:
                    return {'success': False, 'error': 'capsule_id and reaction required'}
                try:
                    response = requests.post(
                        f'{base_url}/{capsule_id}/react/',
                        json={'reaction': reaction},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Failed to add reaction'}

            elif action == 'ready':
                try:
                    response = requests.get(f'{base_url}/ready-to-reveal/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import TimeCapsule
                from django.utils import timezone
                capsules = TimeCapsule.objects.filter(
                    status='sealed',
                    reveal_at__lte=timezone.now()
                ).select_related('agent').order_by('reveal_at')[:10]
                return {
                    'success': True,
                    'ready_capsules': [
                        {
                            'id': str(c.id),
                            'title': c.title or '',
                            'agent_name': c.agent.name if c.agent else 'Unknown',
                            'trigger': c.trigger or '',
                            'reveal_at': c.reveal_at.isoformat() if c.reveal_at else None
                        }
                        for c in capsules
                    ],
                    'count': capsules.count()
                }

            elif action == 'generate':
                try:
                    response = requests.post(f'{base_url}/generate/', timeout=30)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Auto-generation not available'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing time capsules: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 25: A/B Testing & Memory Clusters (Session 587) =====

    def _manage_ab_testing(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 587: Manage A/B testing experiments.
        """
        action = arguments.get('action', 'dashboard')
        base_url = 'http://localhost:8000/api/ab-testing'

        try:
            if action == 'dashboard':
                try:
                    response = requests.get(f'{base_url}/dashboard/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback to direct DB query
                from core.models_unified_system import ABTest
                tests = ABTest.objects.all()
                status_counts = {
                    'draft': tests.filter(status='draft').count(),
                    'running': tests.filter(status='running').count(),
                    'paused': tests.filter(status='paused').count(),
                    'completed': tests.filter(status='completed').count(),
                }
                return {
                    'success': True,
                    'status_counts': status_counts,
                    'total_tests': sum(status_counts.values())
                }

            elif action == 'list':
                status_filter = arguments.get('status')
                try:
                    params = {'status': status_filter} if status_filter else {}
                    response = requests.get(f'{base_url}/tests/', params=params, timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import ABTest
                tests = ABTest.objects.all()
                if status_filter:
                    tests = tests.filter(status=status_filter)
                tests = tests.order_by('-created_at')[:20]
                return {
                    'success': True,
                    'tests': [
                        {
                            'id': str(t.id),
                            'name': t.name,
                            'test_type': t.test_type,
                            'status': t.status,
                            'created_at': t.created_at.isoformat()
                        }
                        for t in tests
                    ]
                }

            elif action == 'create':
                name = arguments.get('name')
                test_type = arguments.get('test_type')
                if not name or not test_type:
                    return {'success': False, 'error': 'name and test_type required'}

                try:
                    response = requests.post(
                        f'{base_url}/tests/create/',
                        json={
                            'name': name,
                            'test_type': test_type,
                            'hypothesis': arguments.get('hypothesis', ''),
                            'description': arguments.get('description', '')
                        },
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import ABTest
                test = ABTest.objects.create(
                    name=name,
                    test_type=test_type,
                    hypothesis=arguments.get('hypothesis', ''),
                    description=arguments.get('description', ''),
                    status='draft'
                )
                return {
                    'success': True,
                    'test_id': str(test.id),
                    'message': f'A/B test "{name}" created'
                }

            elif action == 'detail':
                test_id = arguments.get('test_id')
                if not test_id:
                    return {'success': False, 'error': 'test_id required'}
                try:
                    response = requests.get(f'{base_url}/tests/{test_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import ABTest
                try:
                    test = ABTest.objects.get(id=test_id)
                    return {
                        'success': True,
                        'test': {
                            'id': str(test.id),
                            'name': test.name,
                            'test_type': test.test_type,
                            'status': test.status,
                            'hypothesis': test.hypothesis,
                            'created_at': test.created_at.isoformat()
                        }
                    }
                except ABTest.DoesNotExist:
                    return {'success': False, 'error': 'Test not found'}

            elif action == 'start':
                test_id = arguments.get('test_id')
                if not test_id:
                    return {'success': False, 'error': 'test_id required'}
                try:
                    response = requests.post(f'{base_url}/tests/{test_id}/start/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import ABTest
                from django.utils import timezone
                try:
                    test = ABTest.objects.get(id=test_id)
                    test.status = 'running'
                    test.start_date = timezone.now()
                    test.save()
                    return {'success': True, 'message': f'Test "{test.name}" started'}
                except ABTest.DoesNotExist:
                    return {'success': False, 'error': 'Test not found'}

            elif action == 'pause':
                test_id = arguments.get('test_id')
                if not test_id:
                    return {'success': False, 'error': 'test_id required'}
                try:
                    response = requests.post(f'{base_url}/tests/{test_id}/pause/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import ABTest
                try:
                    test = ABTest.objects.get(id=test_id)
                    test.status = 'paused'
                    test.save()
                    return {'success': True, 'message': f'Test "{test.name}" paused'}
                except ABTest.DoesNotExist:
                    return {'success': False, 'error': 'Test not found'}

            elif action == 'complete':
                test_id = arguments.get('test_id')
                if not test_id:
                    return {'success': False, 'error': 'test_id required'}
                try:
                    response = requests.post(f'{base_url}/tests/{test_id}/complete/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import ABTest
                from django.utils import timezone
                try:
                    test = ABTest.objects.get(id=test_id)
                    test.status = 'completed'
                    test.end_date = timezone.now()
                    test.save()
                    return {'success': True, 'message': f'Test "{test.name}" completed'}
                except ABTest.DoesNotExist:
                    return {'success': False, 'error': 'Test not found'}

            elif action == 'results':
                test_id = arguments.get('test_id')
                if not test_id:
                    return {'success': False, 'error': 'test_id required'}
                try:
                    response = requests.get(f'{base_url}/tests/{test_id}/results/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Results not available'}

            elif action == 'add_variant':
                test_id = arguments.get('test_id')
                variant_name = arguments.get('variant_name')
                if not test_id or not variant_name:
                    return {'success': False, 'error': 'test_id and variant_name required'}
                try:
                    response = requests.post(
                        f'{base_url}/tests/{test_id}/variants/',
                        json={
                            'name': variant_name,
                            'config': arguments.get('variant_config', {})
                        },
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Failed to add variant'}

            elif action == 'record_event':
                variant_id = arguments.get('variant_id')
                event_type = arguments.get('event_type')
                if not variant_id or not event_type:
                    return {'success': False, 'error': 'variant_id and event_type required'}
                try:
                    response = requests.post(
                        f'{base_url}/variants/{variant_id}/event/',
                        json={'event_type': event_type},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Failed to record event'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing A/B testing: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_memory_clusters(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 587: Manage agent memory clusters - semantic grouping of memories.
        """
        action = arguments.get('action', 'overview')
        base_url = 'http://localhost:8000/api/memory-clusters'

        try:
            if action == 'overview':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback to direct DB query
                from core.models_unified_system import MemoryCluster
                total_clusters = MemoryCluster.objects.count()
                clusters_by_agent = {}
                for cluster in MemoryCluster.objects.select_related('agent').all()[:50]:
                    agent_name = cluster.agent.name if cluster.agent else 'Cross-Agent'
                    if agent_name not in clusters_by_agent:
                        clusters_by_agent[agent_name] = 0
                    clusters_by_agent[agent_name] += 1
                return {
                    'success': True,
                    'stats': {
                        'total_clusters': total_clusters,
                        'agents_with_clusters': len(clusters_by_agent)
                    },
                    'clusters_by_agent': clusters_by_agent
                }

            elif action == 'list_agent':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.get(f'{base_url}/agent/{agent_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import MemoryCluster
                clusters = MemoryCluster.objects.filter(agent_id=agent_id).order_by('-created_at')[:20]
                return {
                    'success': True,
                    'clusters': [
                        {
                            'id': str(c.id),
                            'name': c.name,
                            'description': c.description or '',
                            'memory_count': c.memories.count(),
                            'coherence_score': c.coherence_score,
                            'created_at': c.created_at.isoformat()
                        }
                        for c in clusters
                    ]
                }

            elif action == 'generate':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.post(f'{base_url}/agent/{agent_id}/', timeout=60)
                    if response.status_code in [200, 201]:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Cluster generation not available'}

            elif action == 'detail':
                cluster_id = arguments.get('cluster_id')
                if not cluster_id:
                    return {'success': False, 'error': 'cluster_id required'}
                try:
                    response = requests.get(f'{base_url}/cluster/{cluster_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import MemoryCluster
                try:
                    cluster = MemoryCluster.objects.select_related('agent').get(id=cluster_id)
                    return {
                        'success': True,
                        'cluster': {
                            'id': str(cluster.id),
                            'name': cluster.name,
                            'description': cluster.description or '',
                            'agent_name': cluster.agent.name if cluster.agent else 'Cross-Agent',
                            'memory_count': cluster.memories.count(),
                            'coherence_score': cluster.coherence_score,
                            'keywords': cluster.keywords or [],
                            'created_at': cluster.created_at.isoformat()
                        }
                    }
                except MemoryCluster.DoesNotExist:
                    return {'success': False, 'error': 'Cluster not found'}

            elif action == 'add_memory':
                cluster_id = arguments.get('cluster_id')
                memory_id = arguments.get('memory_id')
                if not cluster_id or not memory_id:
                    return {'success': False, 'error': 'cluster_id and memory_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/cluster/{cluster_id}/add-memory/',
                        json={'memory_id': memory_id},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Failed to add memory to cluster'}

            elif action == 'remove_memory':
                cluster_id = arguments.get('cluster_id')
                memory_id = arguments.get('memory_id')
                if not cluster_id or not memory_id:
                    return {'success': False, 'error': 'cluster_id and memory_id required'}
                try:
                    response = requests.delete(
                        f'{base_url}/cluster/{cluster_id}/memory/{memory_id}/',
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, 'message': 'Memory removed from cluster'}
                except:
                    pass
                return {'success': False, 'error': 'Failed to remove memory from cluster'}

            elif action == 'evolution':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.get(f'{base_url}/evolution/{agent_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Evolution data not available'}

            elif action == 'find_similar':
                query = arguments.get('query')
                if not query:
                    return {'success': False, 'error': 'query required'}
                try:
                    response = requests.post(
                        f'{base_url}/find-similar/',
                        json={'query': query},
                        timeout=15
                    )
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Similar cluster search not available'}

            elif action == 'visualization':
                agent_id = arguments.get('agent_id')
                url = f'{base_url}/visualization/{agent_id}/' if agent_id else f'{base_url}/visualization/'
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Visualization data not available'}

            elif action == 'generate_all':
                try:
                    response = requests.post(f'{base_url}/generate-all/', timeout=120)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Cluster generation for all agents not available'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing memory clusters: {e}")
            return {'success': False, 'error': str(e)}
