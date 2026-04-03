"""
Competitor Analysis Agent - Business Intelligence
==================================================

Session 293: Business Research Extension
Session 303: Unified Intelligence Search + Auto Spider Refresh
Session 304: Learning Infrastructure Integration
Session 354: Mythology Validation - Prevents unrealistic claims in research output
Session 683: Added ML Integration (GNN+Text for entity analysis)

This agent analyzes competitors in a given market/industry.
It uses web search and spider data to:
1. Identify key competitors
2. Analyze their features, pricing, positioning
3. Generate SWOT analysis
4. Find market gaps and opportunities
5. ML-powered relationship analysis

Tools Available:
    - web_search: Search for competitor information
    - spider_query: Query spider network for competitor mentions
    - analyze_competitor: Deep analysis of a specific competitor
    - refresh_spider_data: Trigger fresh spider crawls for up-to-date data
    - get_prior_research: Retrieve relevant past research

Tools NOT Available (by design):
    - image/video/audio generation
    - editing operations
"""

import logging
import time
import json
import re
from typing import Dict, Any, List

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


# =============================================================================
# Session 683: ML Integration Helpers
# =============================================================================

def analyze_competitors_with_ml(graph_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze competitor relationships using ML models (GNN for entity graphs).

    Args:
        graph_data: Dict with 'nodes' (competitors) and 'edges' (relationships)

    Returns:
        Dict with ML analysis results including community detection
    """
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        result = router.auto_route(
            data=graph_data,
            task_hint=TaskType.GRAPH,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'graph'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'communities': result.prediction.get('communities') if hasattr(result, 'prediction') and result.prediction else None,
            'centrality_scores': result.prediction.get('centrality') if hasattr(result, 'prediction') and result.prediction else None,
        }
    except Exception as e:
        logger.warning(f"ML competitor graph analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


def analyze_competitor_text_with_ml(text_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze competitor text mentions using ML models (DistilBERT for text).

    Args:
        text_data: Dict with 'texts' key containing competitor mentions

    Returns:
        Dict with ML text analysis results
    """
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        result = router.auto_route(
            data=text_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'sentiment': result.prediction.get('sentiment') if hasattr(result, 'prediction') and result.prediction else None,
        }
    except Exception as e:
        logger.warning(f"ML competitor text analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


def strip_html_tags(text: str) -> str:
    """Strip HTML tags from text (Session 293)."""
    if not text:
        return ''
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(text, 'html.parser')
        clean_text = soup.get_text(separator=' ', strip=True)
        clean_text = ' '.join(clean_text.split())
        return clean_text
    except Exception:
        return re.sub(r'<[^>]+>', '', text).strip()


class CompetitorAnalysisAgent(BaseAgent):
    """
    Agent specialized in competitive analysis and market positioning.

    This agent:
    1. Takes a market/industry or business idea
    2. Identifies key competitors using web search and spider data
    3. Analyzes competitor strengths, weaknesses, features, pricing
    4. Generates SWOT analysis and positioning recommendations

    It CANNOT:
    - Generate images, videos, or audio
    - Edit any content
    - Create 3D models
    """

    name = "CompetitorAnalysisAgent"
    create_deliverable_on_schedule = False  # Session 1077: scheduled outputs go to AgentExecution only

    system_prompt = """You are CompetitorAnalysisAgent, a specialist in competitive intelligence and market analysis.

Your ONLY job is to analyze competitors and market positioning. You do NOT create content.

You have these tools:
- spider_query: Query spider network for competitor mentions, news, discussions (MOST IMPORTANT - real data!)
- web_search: Search the web for competitor information, features, pricing
- get_prior_research: Retrieve past research to build on existing knowledge
- analyze_competitor: Deep analysis of a specific competitor (name, website)

CRITICAL - You MUST use spider_query:
Session 324: The spider_query tool connects to our real-time data sources (Reddit, HackerNews, YouTube, etc).
You MUST call spider_query to get actual articles and discussions about competitors.
WITHOUT spider_query data, you cannot provide a proper competitive analysis.

When given a competitive analysis task:
1. FIRST: Call spider_query with a relevant search query to get real articles/discussions
2. OPTIONALLY: Check get_prior_research for any existing analysis on this market
3. THEN: Call web_search for additional competitor details
4. For each major competitor found, gather:
   - Company overview and positioning
   - Key features/products
   - Pricing model (if available)
   - Strengths and weaknesses
5. Synthesize ALL the data into a competitive landscape analysis
6. Identify market gaps and opportunities

IMPORTANT: If spider_query returns data, USE that data in your analysis. Reference the specific articles/discussions you found.

Output Format:
Return structured analysis with:
- market_overview: Brief description of the market
- competitors: List of competitors with details
- swot_analysis: Strengths, Weaknesses, Opportunities, Threats
- market_gaps: Identified opportunities
- positioning_recommendations: How to differentiate

You CANNOT create images, videos, audio, or edit anything. Only analyze competitors.
If asked to create content, explain you can only research and suggest using the appropriate agent."""

    tools = [
        # Session 324: spider_query FIRST - this is our primary data source!
        {
            "type": "function",
            "function": {
                "name": "spider_query",
                "description": "MUST USE FIRST: Query spider network for real articles/discussions from Reddit, HackerNews, YouTube, tech news. This provides actual data for analysis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for competitor mentions (e.g., 'AI content generation tools', 'best AI writing apps')"
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by category",
                            "enum": ["tech", "news", "social", "all"],
                            "default": "all"
                        },
                        "hours": {
                            "type": "integer",
                            "description": "Look back period in hours (default 168 = 1 week)",
                            "default": 168
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return",
                            "default": 30
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        # web_search tool definition removed — handled by BaseAgent fallback (Session 1090)
        {
            "type": "function",
            "function": {
                "name": "analyze_competitor",
                "description": "Deep analysis of a specific competitor - gathers all available info",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "competitor_name": {
                            "type": "string",
                            "description": "Name of the competitor company/product"
                        },
                        "competitor_website": {
                            "type": "string",
                            "description": "Competitor's website URL (optional)"
                        },
                        "analysis_focus": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["features", "pricing", "reviews", "news", "social", "technology"]
                            },
                            "description": "Areas to focus analysis on",
                            "default": ["features", "pricing", "reviews"]
                        }
                    },
                    "required": ["competitor_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_swot",
                "description": "Generate SWOT analysis based on gathered competitor data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "business_idea": {
                            "type": "string",
                            "description": "The user's business idea or product"
                        },
                        "competitors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of competitor names analyzed"
                        },
                        "market_context": {
                            "type": "string",
                            "description": "Market context and findings from research"
                        }
                    },
                    "required": ["business_idea", "competitors"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "refresh_spider_data",
                "description": "Trigger spider network to fetch fresh, real-time data before analysis. Use this at the START of analysis to ensure you have the latest market data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "categories": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["tech", "financial", "jobs", "news", "creative", "community"]
                            },
                            "description": "Spider categories to refresh (defaults to auto-detect from query)",
                            "default": []
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_prior_research",
                "description": "Retrieve relevant past research from previous competitor and customer analyses. Use this to build on existing knowledge rather than starting from scratch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "market_topic": {
                            "type": "string",
                            "description": "Market/topic to find related research for (e.g., 'AI writing tools', 'coffee industry')"
                        },
                        "research_type": {
                            "type": "string",
                            "description": "Type of research to retrieve",
                            "enum": ["competitor", "customer", "all"],
                            "default": "all"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return",
                            "default": 5
                        }
                    },
                    "required": ["market_topic"]
                }
            }
        }
    ]

    def __init__(self, user=None):
        super().__init__(user)
        self._spider_service = None
        self._semantic_search = None
        self._unified_search = None
        self._agent_intelligence = None  # Session 351: Agent intelligence context

    @property
    def spider_service(self):
        """Lazy-load Spider Intelligence Service."""
        if self._spider_service is None:
            from core.services.spider_intelligence import SpiderIntelligenceService
            self._spider_service = SpiderIntelligenceService()
        return self._spider_service

    @property
    def semantic_search(self):
        """Lazy-load Spider Semantic Search Service."""
        if self._semantic_search is None:
            from core.services.spider_semantic_search import get_spider_semantic_search
            self._semantic_search = get_spider_semantic_search()
        return self._semantic_search

    @property
    def unified_search(self):
        """Session 303: Lazy-load Unified Intelligence Search Service."""
        if self._unified_search is None:
            from core.services.unified_intelligence_search import get_unified_intelligence_search
            self._unified_search = get_unified_intelligence_search()
        return self._unified_search

    @property
    def agent_intelligence(self):
        """Session 351: Lazy-load Agent Intelligence Context Service."""
        if self._agent_intelligence is None:
            from core.services.agent_intelligence_context import get_agent_intelligence_context
            self._agent_intelligence = get_agent_intelligence_context()
        return self._agent_intelligence

    def _analyze_market_with_ml(
        self,
        competitors: List[Dict[str, Any]],
        mentions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Session 683: Analyze competitor market using ML models.

        Uses GNN for relationship analysis and Text models for sentiment.

        Args:
            competitors: List of competitor dicts with name, features, etc.
            mentions: List of mention dicts with title, content, etc.

        Returns:
            Dict with combined ML analysis results
        """
        ml_results = {'ml_used': False}

        # Build competitor relationship graph for GNN
        if len(competitors) >= 2:
            try:
                graph_data = self._build_competitor_graph(competitors, mentions)
                if graph_data.get('nodes') and graph_data.get('edges'):
                    graph_ml = analyze_competitors_with_ml(graph_data)
                    if graph_ml.get('ml_used'):
                        ml_results['graph_analysis'] = graph_ml
                        ml_results['ml_used'] = True
            except Exception as e:
                logger.warning(f"Competitor graph analysis failed: {e}")

        # Build text data for sentiment analysis
        if mentions:
            try:
                texts = [
                    f"{m.get('title', '')} {m.get('description', '')}"
                    for m in mentions if m.get('title')
                ][:50]

                if texts:
                    text_data = {'texts': texts, 'analysis_type': 'competitor_sentiment'}
                    text_ml = analyze_competitor_text_with_ml(text_data)
                    if text_ml.get('ml_used'):
                        ml_results['text_analysis'] = text_ml
                        ml_results['ml_used'] = True
            except Exception as e:
                logger.warning(f"Competitor text analysis failed: {e}")

        return ml_results

    def _build_competitor_graph(
        self,
        competitors: List[Dict[str, Any]],
        mentions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Session 683: Build competitor relationship graph for GNN analysis.

        Creates nodes for competitors and edges for shared features/markets.

        Args:
            competitors: List of competitor data
            mentions: List of mentions that may reference multiple competitors

        Returns:
            Dict with 'nodes' and 'edges' for graph analysis
        """
        nodes = []
        edges = []
        node_ids = {}

        # Create nodes for each competitor
        for i, comp in enumerate(competitors):
            name = comp.get('name', f'competitor_{i}')
            node_ids[name.lower()] = i
            nodes.append({
                'id': i,
                'name': name,
                'features': comp.get('features', []),
                'market': comp.get('market', 'general')
            })

        # Create edges based on co-mentions in data
        competitor_names = [n['name'].lower() for n in nodes]
        for mention in mentions:
            text = f"{mention.get('title', '')} {mention.get('description', '')}".lower()
            mentioned = [name for name in competitor_names if name in text]

            # Create edges between co-mentioned competitors
            for i, name1 in enumerate(mentioned):
                for name2 in mentioned[i + 1:]:
                    if name1 in node_ids and name2 in node_ids:
                        edges.append({
                            'source': node_ids[name1],
                            'target': node_ids[name2],
                            'type': 'co_mention',
                            'weight': 1.0
                        })

        return {'nodes': nodes, 'edges': edges}

    def _get_project_context(self, project_id: str) -> Dict[str, Any]:
        """
        Session 302: Fetch project context when project_id is provided.
        Session 350: Enhanced with domain targeting for spider queries.

        This enables users to say "Analyze competitors for this project"
        and have the agent automatically use the project's topic/description.

        Args:
            project_id: UUID of the PartnershipProject

        Returns:
            Dict with project context (name, description, type, domain targeting) or empty dict
        """
        if not project_id:
            return {}

        try:
            from core.models_partnership import PartnershipProject
            project = PartnershipProject.objects.get(id=project_id)

            # Session 350: Get or extract domain targeting
            domain_targeting = {}
            try:
                domain_targeting = project.get_domain_targeting()
                logger.info(f"Domain targeting for project: {domain_targeting.get('primary_domain')}, tags: {domain_targeting.get('domain_tags', [])[:5]}")
            except Exception as e:
                logger.warning(f"Failed to get domain targeting: {e}")

            return {
                'project_name': project.project_name,
                'project_description': project.description,
                'project_type': project.project_type,
                'project_id': str(project.id),
                # Session 350: Domain targeting for spider queries
                'domain_targeting': domain_targeting,
                'primary_domain': domain_targeting.get('primary_domain', 'general_startup'),
                'domain_tags': domain_targeting.get('domain_tags', []),
                'spider_queries': domain_targeting.get('spider_queries', []),
                'domain_subreddits': domain_targeting.get('subreddits', [])
            }
        except Exception as e:
            logger.warning(f"Failed to fetch project context: {e}")
            return {}

    def _enhance_task_with_project(self, task: str, project_context: Dict[str, Any]) -> str:
        """
        Session 302: Enhance the task with project context.

        If user says "Analyze competitors" and we have project context,
        enhance it to "Analyze competitors for [project name]: [description]"

        Args:
            task: Original task
            project_context: Dict from _get_project_context()

        Returns:
            Enhanced task with project context
        """
        if not project_context:
            return task

        project_name = project_context.get('project_name', '')
        project_description = project_context.get('project_description', '')

        # If task is vague (doesn't specify what to research), add project context
        vague_indicators = ['competitor', 'competitors', 'market analysis', 'competitive', 'swot']
        is_vague = any(indicator in task.lower() for indicator in vague_indicators) and \
                   len(task.split()) < 15  # Short task likely needs context

        if is_vague and project_name:
            enhanced = f"{task} for '{project_name}'"
            if project_description and len(project_description) < 200:
                enhanced += f": {project_description}"
            logger.info(f"Enhanced task with project context: {enhanced[:100]}...")
            return enhanced

        return task

    def _check_business_viability(self, task: str) -> Dict[str, Any]:
        """
        Session 350: "Idiot Protector" - Check if business idea is viable.
        Session 351: Enhanced with improvement suggestions and pivot ideas.

        Uses GPT to quickly assess if the business idea is:
        1. Viable - Proceed normally
        2. Questionable - Add warning but proceed with suggestions
        3. Absurd/Joke - Strong warning with pivot ideas

        Args:
            task: The business idea or research request

        Returns:
            Dict with viability_score (0-100), assessment, improvement_suggestions, pivot_ideas
        """
        try:
            # Session 857: Use inherited client with retry logic
            check_prompt = f"""Evaluate this business idea/research request for basic viability.

Business Idea: {task}

Score from 0-100:
- 80-100: Viable, reasonable business idea
- 50-79: Questionable but possible (niche, risky, or unusual)
- 20-49: Highly impractical or likely to fail
- 0-19: Joke/absurd/impossible (e.g., "selling air", "restaurant for invisible food")

IMPORTANT: For ANY score below 80, provide actionable improvement suggestions.
For scores below 50, also provide pivot ideas (alternative business concepts).

Respond in JSON format:
{{
    "viability_score": <0-100>,
    "assessment": "<one sentence assessment>",
    "is_joke": <true/false>,
    "key_concerns": ["<concern 1>", "<concern 2>"],
    "improvement_suggestions": [
        "<specific actionable suggestion 1>",
        "<specific actionable suggestion 2>",
        "<specific actionable suggestion 3>"
    ],
    "pivot_ideas": [
        "<alternative business concept 1>",
        "<alternative business concept 2>"
    ],
    "target_market_tip": "<suggestion for better target market if applicable>",
    "warning": "<warning message if score < 50, otherwise null>",
    "proceed": true
}}

Be constructive! Even bad ideas often have a kernel of something useful.
For questionable ideas, help them become viable.
For absurd ideas, suggest what realistic version might work."""

            # Session 857: Use retry-enabled completion call
            response = self._call_completion_with_retry(
                messages=[{"role": "user", "content": check_prompt}],
                model="gpt-5.2",  # Session 857: Fixed model name
                max_completion_tokens=2000
            )

            result = json.loads(response.choices[0].message.content)
            result['proceed'] = True  # Always proceed - we're warning, not blocking

            logger.info(
                f"Viability check: score={result.get('viability_score')}, "
                f"suggestions={len(result.get('improvement_suggestions', []))}"
            )

            return result

        except Exception as e:
            logger.warning(f"Viability check failed (proceeding anyway): {e}")
            return {
                'viability_score': 50,
                'assessment': 'Unable to assess viability',
                'is_joke': False,
                'key_concerns': [],
                'improvement_suggestions': [],
                'pivot_ideas': [],
                'target_market_tip': None,
                'warning': None,
                'proceed': True
            }

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute competitive analysis based on the task."""
        start_time = time.time()
        tool_calls_made = []
        all_competitor_data = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

        # Session 529: Build intelligent prompt with full context
        self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

        with self.time_travel_session("competitor_analysis", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                # Session 352: ALWAYS trigger spider refresh FIRST, before anything else
                # This ensures we have fresh data for every research request
                try:
                    logger.info(f"🕷️ [Session 352] Auto-refreshing spiders at start of research: {task[:50]}...")
                    refresh_result = self.unified_search.refresh_spiders_for_query(task)
                    logger.info(f"🕷️ Spider refresh triggered: {refresh_result.get('categories', [])}")
                except Exception as e:
                    logger.warning(f"Initial spider refresh failed (continuing anyway): {e}")

                # Session 302: Check for project_id in context and fetch project data
                project_id = context.get('project_id')
                project_context = self._get_project_context(project_id) if project_id else {}

                # Session 302: Enhance task with project context if available
                task = self._enhance_task_with_project(task, project_context)

                # Session 490: If no project domain targeting, extract domains from task directly
                # This enables domain-aware spider queries even without a project
                if not project_context.get('domain_targeting'):
                    try:
                        from core.services.domain_extraction_service import get_domain_extraction_service
                        domain_service = get_domain_extraction_service()
                        # Use fast keyword extraction (no GPT call)
                        domain_result = domain_service.extract_domains(task, use_gpt=False)
                        project_context['domain_targeting'] = domain_result.to_dict()
                        project_context['primary_domain'] = domain_result.primary_domain
                        project_context['domain_tags'] = domain_result.domain_tags
                        project_context['spider_queries'] = domain_result.spider_queries
                        project_context['domain_subreddits'] = domain_result.subreddits
                        project_context['domain_tags_auto_extracted'] = True
                        logger.info(
                            f"🎯 [Session 490] Extracted domain from task: {domain_result.primary_domain}, "
                            f"tags: {domain_result.domain_tags[:5]}, confidence: {domain_result.confidence:.2f}"
                        )
                    except Exception as e:
                        logger.debug(f"Domain extraction failed (non-fatal): {e}")

                # Session 303: Store current task for tool access
                self._current_task = task

                # Session 350/352: "Idiot Protector" - Check business viability FIRST
                # Session 352: Stop early for low scores to save API costs and give helpful feedback
                viability = self._check_business_viability(task)
                viability_score = viability.get('viability_score', 100)

                if viability_score < 50:
                    # Early exit with constructive feedback - don't waste research on bad ideas
                    self.record_decision(
                        decision_type="viability_check",
                        action="Stopped research due to low viability",
                        reasoning=f"Score: {viability_score}, Assessment: {viability.get('assessment')}",
                        confidence=0.85
                    )
                    logger.warning(f"Low viability idea (score={viability_score}), returning early: {task[:50]}...")

                    # Build helpful feedback message
                    feedback_parts = []
                    feedback_parts.append(f"## Business Idea Viability Check: {viability_score}/100")
                    feedback_parts.append(f"\n**Assessment:** {viability.get('assessment', 'This idea needs significant improvement.')}")

                    if viability.get('is_joke'):
                        feedback_parts.append("\n⚠️ *This appears to be a joke or highly impractical concept.*")

                    # Key concerns
                    key_concerns = viability.get('key_concerns', [])
                    if key_concerns:
                        feedback_parts.append("\n### Key Concerns")
                        for concern in key_concerns[:4]:
                            feedback_parts.append(f"- {concern}")

                    # Improvement suggestions
                    suggestions = viability.get('improvement_suggestions', [])
                    if suggestions:
                        feedback_parts.append("\n### How to Improve This Idea")
                        for i, suggestion in enumerate(suggestions[:5], 1):
                            feedback_parts.append(f"{i}. {suggestion}")

                    # Pivot ideas
                    pivot_ideas = viability.get('pivot_ideas', [])
                    if pivot_ideas:
                        feedback_parts.append("\n### Alternative Business Ideas to Consider")
                        for pivot in pivot_ideas[:3]:
                            feedback_parts.append(f"- {pivot}")

                    # Target market tip
                    market_tip = viability.get('target_market_tip')
                    if market_tip:
                        feedback_parts.append(f"\n### Target Market Tip\n{market_tip}")

                    feedback_parts.append("\n---\n*Refine your idea based on the suggestions above and try again!*")

                    execution_time = int((time.time() - start_time) * 1000)

                    return AgentResult(
                        success=True,  # Not an error, just early feedback
                        message="\n".join(feedback_parts),
                        data={
                            'type': 'viability_feedback',
                            'viability': {
                                'score': viability_score,
                                'assessment': viability.get('assessment'),
                                'is_joke': viability.get('is_joke', False),
                                'key_concerns': key_concerns,
                                'improvement_suggestions': suggestions,
                                'pivot_ideas': pivot_ideas,
                                'target_market_tip': market_tip
                            },
                            'query': task,
                            'early_exit': True
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time
                    )

                # For scores 50-79, add warning but continue with research
                viability_warning = None
                if viability_score < 80:
                    viability_warning = viability.get('warning') or viability.get('assessment')
                    logger.info(f"Moderate viability idea (score={viability_score}), proceeding with warning: {task[:50]}...")

                # Session 352: Spider refresh already triggered at start of execute()
                # Recording the decision for time travel debugging
                self.record_decision(
                    decision_type="data_refresh",
                    action="Spider network refresh triggered at start",
                    reasoning=f"Ensuring fresh data for: {task[:50]}",
                    confidence=0.9
                )

                # Session 303: Get prior research context
                prior_context = ""
                try:
                    prior_context = self.unified_search.get_research_context(
                        query=task,
                        max_spider_items=3,
                        max_research_items=2
                    )
                    if prior_context:
                        logger.info(f"Found prior research context ({len(prior_context)} chars)")
                except Exception as e:
                    logger.warning(f"Prior research lookup failed: {e}")

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing competitive research request",
                    reasoning=f"Received task: {task[:100]}",
                    confidence=0.9
                )

                # Build prompt with context
                # Session 354: Use mythology-guarded prompt to prevent unrealistic claims
                full_prompt = self._build_prompt_with_mythology_guard(task, scifi_context, spider_context)

                # Session 303: Inject prior research context if available
                if prior_context:
                    full_prompt += f"\n\n{prior_context}\n"

                # Session 351: Inject Agent Collective Intelligence
                # This brings in: SharedKnowledge, KnowledgeTransfers, AgentConversations, BoardroomPolicies
                try:
                    # Get domain from project context if available
                    domain = project_context.get('primary_domain') if project_context else None
                    agent_intel_context = self.agent_intelligence.get_context_for_research(
                        topic=task,
                        domain=domain,
                        max_items_per_category=5
                    )
                    agent_intel_prompt = agent_intel_context.to_prompt_context()
                    if agent_intel_prompt:
                        full_prompt += f"\n{agent_intel_prompt}"
                        logger.info(
                            f"🧠 [Session 351] Injected agent intelligence: "
                            f"{agent_intel_context.total_knowledge_items} knowledge, "
                            f"{agent_intel_context.total_conversations} conversations, "
                            f"{agent_intel_context.total_policies} policies"
                        )
                        self.record_decision(
                            decision_type="context_injection",
                            action="Injected agent collective intelligence",
                            reasoning=f"Added {agent_intel_context.total_knowledge_items} knowledge items, "
                                      f"{agent_intel_context.total_conversations} conversation insights, "
                                      f"{agent_intel_context.total_policies} canonical policies",
                            confidence=0.95
                        )
                except Exception as e:
                    logger.warning(f"Agent intelligence injection failed (continuing anyway): {e}")

                # Session 350: Add domain-aware spider targeting instructions
                domain_instructions = ""
                if project_context.get('domain_targeting'):
                    targeting = project_context['domain_targeting']
                    domain_instructions = f"""

DOMAIN-SPECIFIC RESEARCH GUIDANCE (Session 350):
Primary Domain: {targeting.get('primary_domain', 'general_startup')}
Domain Tags: {', '.join(targeting.get('domain_tags', [])[:8])}
Suggested Search Queries: {targeting.get('spider_queries', [])[:5]}
Relevant Subreddits: {', '.join(targeting.get('subreddits', [])[:6])}

CRITICAL: Use these DOMAIN-SPECIFIC search queries for spider_query and web_search!
Do NOT use generic "AI tools" or "tech trends" queries.
Your searches should match the SPECIFIC market: {project_context.get('project_name', task)[:100]}
"""

                # Add instruction to be comprehensive
                full_prompt += f"""

IMPORTANT: For a thorough competitive analysis:
1. First check get_prior_research for existing analysis on this market
2. Use refresh_spider_data if you need the absolute latest data
3. Use web_search to find competitors in this market - USE DOMAIN-SPECIFIC QUERIES
4. Use spider_query to find discussions and reviews - USE DOMAIN-SPECIFIC QUERIES
5. For top 3-5 competitors, use analyze_competitor for deep dives
6. Finally, use generate_swot to synthesize findings
{domain_instructions}
Return a comprehensive competitive landscape analysis with DOMAIN-RELEVANT data."""

                # Make GPT call to determine tools to use
                gpt_response = self._call_openai(full_prompt)

                # Process tool calls
                # Session 1075: Time budget — stop calling tools after 10 min
                # to leave time for synthesis before Celery kills us at 15 min
                TIME_BUDGET_SECONDS = 600  # 10 minutes
                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        elapsed = time.time() - start_time
                        if elapsed > TIME_BUDGET_SECONDS:
                            logger.warning(
                                f"⏱️ [Session 1075] Time budget exhausted ({elapsed:.0f}s > {TIME_BUDGET_SECONDS}s), "
                                f"skipping remaining {len(gpt_response['tool_calls']) - len(tool_calls_made)} tool calls"
                            )
                            break

                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for competitive analysis",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        if tool_result.get('success'):
                            all_competitor_data.append({
                                'source': tool_name,
                                'data': tool_result.get('data', tool_result)
                            })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                # Fallback: if GPT didn't call web_search, make an explicit call
                # to ensure we always combine spider + web data
                tools_used = {tc['tool'] for tc in tool_calls_made}
                if 'web_search' not in tools_used and (time.time() - start_time) < TIME_BUDGET_SECONDS:
                    search_query = self._extract_search_query(task)
                    if search_query:
                        logger.info(f"[Fallback] GPT skipped web_search, running: {search_query[:80]}")
                        web_result = self._execute_tool_call('web_search', {'query': search_query, 'num_results': 10})
                        if web_result.get('success'):
                            all_competitor_data.append({'source': 'web_search', 'data': web_result.get('data', web_result)})
                            tool_calls_made.append({'tool': 'web_search', 'arguments': {'query': search_query}, 'result': web_result})

                execution_time = int((time.time() - start_time) * 1000)

                if all_competitor_data:
                    # Synthesize the competitive analysis
                    # Session 350: Pass project_context for domain-aware synthesis
                    synthesis = self._synthesize_analysis(task, all_competitor_data, project_context)

                    # Session 1023: Check if evidence gate blocked synthesis
                    if synthesis.get('status') == 'insufficient_evidence':
                        execution_time = int((time.time() - start_time) * 1000)
                        gate_reason = synthesis.get('gate_reason', 'Insufficient evidence')
                        logger.info(f"[Evidence Gate] Returning insufficient_evidence: {gate_reason}")
                        return AgentResult(
                            success=True,  # Not an error — just insufficient data
                            message=(
                                f"Insufficient domain-relevant data to synthesize analysis. "
                                f"{gate_reason}\n\n"
                                f"Recommendations:\n"
                                + "\n".join(f"- {a}" for a in synthesis.get('recommended_actions', []))
                            ),
                            data={
                                'type': 'insufficient_evidence',
                                'domain_relevance': synthesis.get('domain_relevance', {}),
                                'raw_data': synthesis.get('raw_data', []),
                                'gate_reason': gate_reason,
                                'recommended_actions': synthesis.get('recommended_actions', []),
                                'data_points_analyzed': synthesis.get('data_points_analyzed', 0),
                                'sources_used': synthesis.get('sources_used', 0),
                            },
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made
                        )

                    # Session 683: Run ML analysis on competitor data
                    ml_analysis = {'ml_used': False}
                    try:
                        # Extract competitors and mentions from raw data
                        competitors = []
                        mentions = []
                        for source_data in all_competitor_data:
                            data = source_data.get('data', {})
                            if isinstance(data, list):
                                for item in data:
                                    if 'name' in item or 'competitor_name' in item:
                                        competitors.append(item)
                                    else:
                                        mentions.append(item)
                            elif isinstance(data, dict) and data.get('name'):
                                competitors.append(data)

                        if competitors or mentions:
                            ml_analysis = self._analyze_market_with_ml(competitors, mentions)
                            if ml_analysis.get('ml_used'):
                                logger.info(
                                    f"ML competitor analysis: graph={ml_analysis.get('graph_analysis', {}).get('ml_used', False)}, "
                                    f"text={ml_analysis.get('text_analysis', {}).get('ml_used', False)}"
                                )
                    except Exception as e:
                        logger.warning(f"ML integration in execute failed: {e}")

                    # Session 294: Save to database with embedding for semantic search
                    # Session 349: Pass project_id to link research to project
                    saved_result = None
                    try:
                        from core.models_unified_system import BusinessResearchResult
                        project_id = context.get('project_id')
                        saved_result = BusinessResearchResult.save_competitor_analysis(
                            query=task,
                            synthesis=synthesis,
                            execution_time_ms=execution_time,
                            project_id=project_id,  # Session 349: Link to project
                            user=self.user  # Session 349: Link to user
                        )
                        logger.info(f"Saved competitor analysis to database: {saved_result.id}, project_id={project_id}")
                    except Exception as e:
                        logger.warning(f"Failed to save competitor analysis: {e}")

                    # Session 352: Simplified - scores < 50 already return early with full feedback
                    result_message = f"Competitive analysis completed with {len(all_competitor_data)} data sources"

                    # Add domain relevance info to message
                    domain_relevance = synthesis.get('domain_relevance', {})
                    if domain_relevance.get('score', 100) < 30:
                        result_message += f"\n⚠️ DATA QUALITY: {synthesis.get('data_quality_warning', 'Limited domain-specific data found.')}"

                    # Show warning for scores 50-79 (low scores already returned early)
                    if viability_warning:
                        result_message = f"⚠️ Note: {viability_warning}\n\n{result_message}"

                    result = AgentResult(
                        success=True,
                        message=result_message,
                        data={
                            'analysis': synthesis,
                            'raw_data': all_competitor_data,
                            'query': task,
                            'saved_id': str(saved_result.id) if saved_result else None,
                            'ml_analysis': ml_analysis,  # Session 683: ML insights
                            # Session 352: Include viability for scores 50-79 (< 50 exits early)
                            'viability': {
                                'score': viability_score,
                                'assessment': viability.get('assessment'),
                                'warning': viability_warning
                            } if viability_warning else None,
                            # Session 350: Domain relevance tracking
                            'domain_relevance': domain_relevance,
                            'domain_targeting': project_context.get('domain_targeting') if project_context else None
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Session 861: Persist analysis to Deliverable
                    analysis_content = synthesis.get('analysis', '')
                    if analysis_content:
                        self._save_to_deliverable(
                            title=f"Competitor Analysis: {task[:50]}",
                            content=analysis_content,
                            deliverable_type='analysis',
                            category='Business',
                            tags=['competitor', 'analysis', 'market', 'research'],
                            content_format='markdown',
                            metadata={
                                'task': task,
                                'data_points': synthesis.get('data_points_analyzed', 0),
                                'sources_used': synthesis.get('sources_used', 0),
                            },
                        )

                    # Session 354: Validate output for mythology (unrealistic claims)
                    result = self._validate_output(result)

                    # === Session 304: Learning Infrastructure ===
                    # Record outcome for XP and pattern learning
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=True,  # Always uses spider data
                        scifi_context_used=bool(scifi_context)
                    )

                    # Create memory of successful research
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.7  # Research is important to remember
                    )

                    # Track contribution to research result
                    if saved_result:
                        self._track_contribution(
                            content_type='research',
                            content_id=saved_result.id,
                            contribution_type='primary_creator',
                            contribution_score=1.0
                        )

                    # Share knowledge about market/competitors discovered
                    if synthesis.get('analysis'):
                        self._share_knowledge(
                            knowledge_type='market',
                            title=f"Market Analysis: {task[:80]}",
                            knowledge_value={
                                'query': task,
                                'data_points': synthesis.get('data_points_analyzed', 0),
                                'sources': synthesis.get('sources_used', 0),
                                'success': True
                            },
                            confidence=0.85
                        )

                    return result
                else:
                    # Return conversational response if no tools called
                    return AgentResult(
                        success=True,
                        message=gpt_response.get('content', 'No competitive data found'),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=execution_time
                    )

            except Exception as e:
                logger.error(f"CompetitorAnalysisAgent error: {e}")
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
        """Execute a tool call for competitive analysis."""

        if tool_name == "web_search":
            # Session 1090: Deprecated — fall through to BaseAgent universal handler
            logger.warning(f"[{self.__class__.__name__}] web_search is deprecated — falling through to BaseAgent handler")
            return super()._execute_tool_call(tool_name, arguments)

        elif tool_name == "spider_query":
            try:
                # Use semantic search for better results
                results = self.semantic_search.semantic_search(
                    query=arguments.get('query', ''),
                    category=arguments.get('category'),
                    hours=arguments.get('hours', 168),
                    limit=arguments.get('limit', 30),
                    min_similarity=0.3
                )
                # Convert SemanticSearchResult objects to dicts
                data = [
                    {
                        'title': r.title,
                        'description': r.description,
                        'url': r.url,
                        'source': r.source,
                        'similarity': r.similarity,
                        'category': r.category
                    }
                    for r in results
                ]
                return {
                    'success': True,
                    'data': data,
                    'search_type': 'semantic'
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Spider query failed: {str(e)}"
                }

        elif tool_name == "analyze_competitor":
            return self._analyze_single_competitor(
                competitor_name=arguments.get('competitor_name', ''),
                competitor_website=arguments.get('competitor_website'),
                analysis_focus=arguments.get('analysis_focus', ['features', 'pricing', 'reviews'])
            )

        elif tool_name == "generate_swot":
            return self._generate_swot_analysis(
                business_idea=arguments.get('business_idea', ''),
                competitors=arguments.get('competitors', []),
                market_context=arguments.get('market_context', '')
            )

        elif tool_name == "refresh_spider_data":
            # Session 303: Trigger fresh spider crawls
            try:
                categories = arguments.get('categories', [])
                # Use the current task/query to determine categories if not specified
                result = self.unified_search.refresh_spiders_for_query(
                    query=self._current_task if hasattr(self, '_current_task') else '',
                    categories=categories if categories else None
                )
                return {
                    'success': True,
                    'data': result,
                    'message': f"Triggered spider refresh for: {result.get('categories', [])}"
                }
            except Exception as e:
                logger.warning(f"Spider refresh failed: {e}")
                return {
                    'success': False,
                    'error': f"Spider refresh failed: {str(e)}"
                }

        elif tool_name == "get_prior_research":
            # Session 303: Get prior research from unified intelligence
            try:
                market_topic = arguments.get('market_topic', '')
                research_type = arguments.get('research_type', 'all')
                limit = arguments.get('limit', 5)

                # Use unified search for combined results
                results = self.unified_search.unified_search(
                    query=market_topic,
                    include_spiders=False,  # Only get research, not spider data
                    include_research=True,
                    research_limit=limit
                )

                # Also get context string for prompt injection
                context = self.unified_search.get_research_context(
                    query=market_topic,
                    max_spider_items=0,
                    max_research_items=limit
                )

                return {
                    'success': True,
                    'data': [
                        {
                            'title': r.title,
                            'description': r.description,
                            'research_type': r.research_type,
                            'market_topic': r.market_topic,
                            'similarity': r.similarity
                        }
                        for r in results
                    ],
                    'context': context,
                    'count': len(results)
                }
            except Exception as e:
                logger.warning(f"Prior research lookup failed: {e}")
                return {
                    'success': False,
                    'error': f"Prior research lookup failed: {str(e)}"
                }

        return super()._execute_tool_call(tool_name, arguments)

    def _spider_fallback(self, query: str) -> Dict[str, Any]:
        """Fallback to spider data when web search fails - uses SEMANTIC search."""
        try:
            # Use semantic search for better results
            results = self.semantic_search.semantic_search(
                query=query,
                hours=168,
                limit=20,
                min_similarity=0.3
            )
            # Convert SemanticSearchResult objects to dicts
            data = [
                {
                    'title': r.title,
                    'description': r.description,
                    'url': r.url,
                    'source': r.source,
                    'similarity': r.similarity,
                    'category': r.category
                }
                for r in results
            ]
            return {
                'success': True,
                'data': data,
                'fallback': True,
                'search_type': 'semantic'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Spider fallback also failed: {str(e)}"
            }

    def _analyze_single_competitor(
        self,
        competitor_name: str,
        competitor_website: str = None,
        analysis_focus: List[str] = None
    ) -> Dict[str, Any]:
        """Deep analysis of a single competitor using multiple data sources."""
        analysis_focus = analysis_focus or ['features', 'pricing', 'reviews']
        competitor_data = {
            'name': competitor_name,
            'website': competitor_website,
            'analysis': {}
        }

        try:
            # Search spider data for competitor mentions using semantic search
            semantic_results = self.semantic_search.semantic_search(
                query=competitor_name,
                hours=720,  # Last 30 days
                limit=50,
                min_similarity=0.3
            )
            # Convert to list of dicts
            spider_results = [
                {
                    'title': r.title,
                    'description': r.description,
                    'url': r.url,
                    'source': r.source,
                    'content': r.description  # For sentiment analysis
                }
                for r in semantic_results
            ]

            # Extract relevant information
            mentions = []
            reviews = []
            news = []

            for item in spider_results:
                title = item.get('title', '').lower()
                content = item.get('content', '').lower()
                source = item.get('source', '')

                if 'review' in title or 'review' in content:
                    reviews.append(item)
                elif source in ['hackernews', 'reddit']:
                    mentions.append(item)
                else:
                    news.append(item)

            competitor_data['analysis'] = {
                'mentions_count': len(mentions),
                'reviews_count': len(reviews),
                'news_count': len(news),
                'recent_mentions': mentions[:5],
                'recent_reviews': reviews[:5],
                'recent_news': news[:5],
                'sentiment': self._analyze_sentiment(mentions + reviews),
                'focus_areas': analysis_focus
            }

            return {
                'success': True,
                'data': competitor_data
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Competitor analysis failed: {str(e)}"
            }

    def _analyze_sentiment(self, items: List[Dict]) -> Dict[str, Any]:
        """Simple sentiment analysis based on keywords."""
        positive_keywords = ['love', 'great', 'amazing', 'best', 'excellent', 'awesome', 'recommend']
        negative_keywords = ['hate', 'terrible', 'awful', 'worst', 'bad', 'avoid', 'problem', 'issue']

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for item in items:
            text = (item.get('title', '') + ' ' + item.get('content', '')).lower()
            has_positive = any(word in text for word in positive_keywords)
            has_negative = any(word in text for word in negative_keywords)

            if has_positive and not has_negative:
                positive_count += 1
            elif has_negative and not has_positive:
                negative_count += 1
            else:
                neutral_count += 1

        total = positive_count + negative_count + neutral_count
        return {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count,
            'score': round((positive_count - negative_count) / max(total, 1), 2),
            'total_analyzed': total
        }

    def _generate_swot_analysis(
        self,
        business_idea: str,
        competitors: List[str],
        market_context: str
    ) -> Dict[str, Any]:
        """Generate SWOT analysis based on competitive research."""

        # Use GPT to generate SWOT
        swot_prompt = f"""Based on the following competitive research, generate a SWOT analysis for this business idea.

Business Idea: {business_idea}

Competitors Analyzed: {', '.join(competitors)}

Market Context: {market_context}

Generate a structured SWOT analysis with:
- Strengths: What advantages could this business have?
- Weaknesses: What challenges might it face?
- Opportunities: What market gaps or trends could it exploit?
- Threats: What competitive or market threats exist?

Return as JSON with keys: strengths, weaknesses, opportunities, threats (each an array of strings)."""

        try:
            # Session 857: Use retry-enabled completion call
            response = self._call_completion_with_retry(
                messages=[{"role": "user", "content": swot_prompt}],
                model="gpt-5.2",  # Session 857: Fixed model name
                max_completion_tokens=4000,
            )

            content = response.choices[0].message.content

            # Try to parse as JSON
            try:
                # Find JSON in response
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    swot_data = json.loads(content[start:end])
                else:
                    swot_data = {'raw_response': content}
            except json.JSONDecodeError:
                swot_data = {'raw_response': content}

            return {
                'success': True,
                'data': {
                    'business_idea': business_idea,
                    'competitors': competitors,
                    'swot': swot_data
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"SWOT generation failed: {str(e)}"
            }

    def _extract_search_query(self, task: str) -> str:
        """Extract a concise web search query from a verbose task description.

        Looks for company/product names first, then falls back to trimming
        the task text to a reasonable search query length.
        """
        # Try to find explicit competitor names (Capitalized words, often after "covering" or "for")
        patterns = [
            r'(?:covering|including|for|vs\.?|versus|compare)\s+(.{10,120}?)(?:\.|$)',
            r'(?:competitors?|companies|players)[\s:]+(.{10,120}?)(?:\.|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                fragment = match.group(1).strip().rstrip(',.')
                return f"competitor analysis {fragment}"

        # Fallback: use the first meaningful portion of the task
        # Strip common task prefixes
        cleaned = re.sub(
            r'^(perform|conduct|do|run|create|generate)\s+(a\s+)?'
            r'(comprehensive\s+|detailed\s+|thorough\s+)?'
            r'(competitor\s+|competitive\s+|market\s+)?(analysis|audit|research|report)\s+'
            r'(for|on|of|about|covering)\s+',
            '', task, flags=re.IGNORECASE
        ).strip()

        if cleaned and len(cleaned) > 5:
            return cleaned[:120]

        # Last resort: first 100 chars of original task
        return task[:100]

    def _synthesize_analysis(
        self,
        task: str,
        all_data: List[Dict[str, Any]],
        project_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Synthesize all gathered data into a coherent analysis using GPT.

        Session 350: Enhanced with domain targeting and data relevance tracking.
        """

        # Collect all data points for analysis
        all_items = []
        domain_relevant_items = []
        domain_tags = (project_context or {}).get('domain_tags', [])

        for source in all_data:
            data = source.get('data', {})
            source_name = source.get('source', 'unknown')

            # Normalize dict data: web_search returns {'results': [...]},
            # spider_query may return {'data': [...]}, analyze_competitor wraps in a dict
            if isinstance(data, dict):
                data = data.get('results', data.get('data', data.get('discussions', [data])))
                if not isinstance(data, list):
                    data = [data]

            if isinstance(data, list):
                for item in data[:15]:  # Limit per source
                    # Session 293: Strip HTML from titles and descriptions
                    title = strip_html_tags(item.get('title', ''))
                    description = strip_html_tags(item.get('description', ''))[:200]

                    item_dict = {
                        'title': title,
                        'description': description,
                        'source': item.get('source', source_name),
                        'url': item.get('url', '')
                    }
                    all_items.append(item_dict)

                    # Session 350: Track domain-relevant items
                    if domain_tags:
                        combined_text = f"{title} {description}".lower()
                        for tag in domain_tags:
                            if tag.lower() in combined_text:
                                domain_relevant_items.append(item_dict)
                                break

        # Limit total items to avoid token limits
        all_items = all_items[:30]
        domain_relevant_count = len(domain_relevant_items)

        # Session 350: Calculate data relevance score
        data_relevance_score = 0
        if len(all_items) > 0:
            data_relevance_score = min(100, int((domain_relevant_count / len(all_items)) * 100))

        # Session 1023: Minimum Evidence Gate — block synthesis when data is insufficient
        # Prevents "beautiful nonsense": structured JSON analysis from zero-relevance data
        MIN_DATA_POINTS = 3
        MIN_DOMAIN_RELEVANCE = 15  # At least 15% of data must be domain-relevant

        if len(all_items) < MIN_DATA_POINTS:
            logger.warning(
                f"[Evidence Gate] Blocking synthesis: only {len(all_items)} data points "
                f"(minimum: {MIN_DATA_POINTS})"
            )
            return {
                'status': 'insufficient_evidence',
                'query': task,
                'analysis': None,
                'data_points_analyzed': len(all_items),
                'sources_used': len(all_data),
                'raw_data': all_items,
                'domain_relevance': {
                    'score': data_relevance_score,
                    'domain_relevant_items': domain_relevant_count,
                    'total_items': len(all_items),
                    'primary_domain': (project_context or {}).get('primary_domain', 'general_startup'),
                    'is_domain_specific': False,
                },
                'gate_reason': f'Only {len(all_items)} data points collected (minimum: {MIN_DATA_POINTS})',
                'recommended_actions': [
                    'Expand spider network coverage for this domain',
                    'Try broader search queries',
                    'Run targeted primary research',
                ],
            }

        domain_tags_reliable = not (project_context or {}).get('domain_tags_auto_extracted', False)
        if domain_tags and domain_tags_reliable and data_relevance_score < MIN_DOMAIN_RELEVANCE and domain_relevant_count == 0:
            logger.warning(
                f"[Evidence Gate] Blocking synthesis: {data_relevance_score}% domain relevance "
                f"({domain_relevant_count}/{len(all_items)} items), 0 domain matches"
            )
            return {
                'status': 'insufficient_evidence',
                'query': task,
                'analysis': None,
                'data_points_analyzed': len(all_items),
                'sources_used': len(all_data),
                'raw_data': all_items,
                'domain_relevance': {
                    'score': data_relevance_score,
                    'domain_relevant_items': domain_relevant_count,
                    'total_items': len(all_items),
                    'primary_domain': (project_context or {}).get('primary_domain', 'general_startup'),
                    'is_domain_specific': False,
                },
                'gate_reason': (
                    f'0 of {len(all_items)} data points matched domain tags '
                    f'{domain_tags[:5]}. Analysis would be hallucinated.'
                ),
                'recommended_actions': [
                    'Add more relevant spiders for this domain',
                    'Verify domain tags are correct for this project',
                    'Consider targeted web search with domain-specific queries',
                ],
            }

        # Build analysis prompt
        items_text = "\n".join([
            f"- {item['title']}: {item['description'][:100]}..."
            for item in all_items if item['title']
        ])

        # Session 350: Add domain context if available
        domain_context = ""
        if project_context and project_context.get('domain_targeting'):
            targeting = project_context['domain_targeting']
            domain_context = f"""
TARGET DOMAIN: {targeting.get('primary_domain', 'general')}
DOMAIN TAGS: {', '.join(targeting.get('domain_tags', [])[:6])}
DATA RELEVANCE: {data_relevance_score}% of data points appear domain-relevant ({domain_relevant_count}/{len(all_items)})
"""

        # Session 350: Add honest data source disclosure
        data_quality_note = ""
        if data_relevance_score < 30:
            data_quality_note = """
NOTE: Limited domain-specific data was found. This analysis is based on general market patterns
and trends. For more accurate insights, consider conducting targeted primary research in this niche.
"""

        # Session 879: Structured output template with Quality Header + Decision block
        analysis_prompt = f"""You are a competitive intelligence analyst. Analyze the following market research data and provide actionable insights.

RESEARCH QUERY: {task}
{domain_context}
DATA COLLECTED ({len(all_items)} articles/mentions):
{items_text}
{data_quality_note}

Provide a structured competitive analysis following this EXACT format:

---

## QUALITY HEADER

| Field | Value |
|-------|-------|
| **Purpose** | [What decision this analysis enables - be specific] |
| **Inputs** | {len(all_items)} data points from [list sources], collected [current date] |
| **Confidence** | [High/Medium/Low] overall - [brief reason based on sample size and data quality] |
| **Constraints** | [What's missing: e.g., pricing data, direct user feedback, regional coverage] |

---

## MARKET OVERVIEW
[2-3 sentences about this market, size estimate if available, growth trajectory]

---

## COMPETITIVE LANDSCAPE

### Direct Competitors ({'{N}'} found)
*Same buyer, same job-to-be-done as user's offering*

| Competitor | Positioning | Key Differentiator | Est. Market Share |
|------------|-------------|-------------------|-------------------|
| [Name] | [Brief positioning] | [What makes them unique] | [High/Med/Low or %] |

### Analogs ({'{N}'} found)
*Different market but similar playbook we can learn from*

| Analog | What We Can Borrow | Risk of Direct Copy |
|--------|-------------------|---------------------|
| [Name] | [Specific tactic/strategy] | [Why it might not transfer] |

---

## MARKET TRENDS
1. **[Trend Name]**: [Description with specific evidence from data]
2. **[Trend Name]**: [Description with specific evidence from data]
3. **[Trend Name]**: [Description with specific evidence from data]

---

## DECISION BLOCK

### Recommended Move
[ONE sentence: what should the user do based on this analysis]

### Top 3 Bets (ranked by evidence strength)
1. **[Bet]**: [Evidence supporting this] - Confidence: [High/Med/Low]
2. **[Bet]**: [Evidence supporting this] - Confidence: [High/Med/Low]
3. **[Bet]**: [Evidence supporting this] - Confidence: [High/Med/Low]

### Risks + Mitigations
- **[Risk]**: [Specific mitigation action]
- **[Risk]**: [Specific mitigation action]
- **[Risk]**: [Specific mitigation action]

### Next 7 Days
| Action | Owner | Est. Effort |
|--------|-------|-------------|
| [Specific action] | [Role: Founder/Marketing/Product] | [Hours] |
| [Specific action] | [Role] | [Hours] |
| [Specific action] | [Role] | [Hours] |

---

## DATA DISCLAIMER
> This analysis is based on {len(all_items)} data points. Treat findings as directional hypotheses until validated with primary research (customer interviews, competitor demos, pricing calls). Sample size affects confidence in [specific areas].

---

IMPORTANT INSTRUCTIONS:
- Use ACTUAL data from the collected articles - cite specific sources where possible
- For confidence levels: High = 20+ relevant data points, Medium = 10-20, Low = <10
- "Direct Competitors" must serve the SAME customer need - don't include tangential players
- "Analogs" are explicitly NOT competitors but offer strategic lessons
- Be honest about data gaps in the Constraints field
- Next 7 Days actions must be specific enough to calendar (not "do more research")"""

        try:
            # Session 857: Use retry-enabled completion call
            response = self._call_completion_with_retry(
                messages=[{"role": "user", "content": analysis_prompt}],
                model="gpt-5.2",  # Session 857: Fixed model name
                max_completion_tokens=6000,
            )

            analysis_text = response.choices[0].message.content

            # Session 350: Include domain relevance metrics
            result = {
                'query': task,
                'analysis': analysis_text,
                'data_points_analyzed': len(all_items),
                'sources_used': len(all_data),
                'raw_data': all_items,  # Include for reference
                # Session 350: Domain relevance tracking
                'domain_relevance': {
                    'score': data_relevance_score,
                    'domain_relevant_items': domain_relevant_count,
                    'total_items': len(all_items),
                    'primary_domain': (project_context or {}).get('primary_domain', 'general_startup'),
                    'is_domain_specific': data_relevance_score >= 30
                }
            }

            # Session 350: Add warning if data is mostly generic
            if data_relevance_score < 30:
                result['data_quality_warning'] = (
                    f"Only {data_relevance_score}% of data points matched the target domain. "
                    "Analysis is based on general market patterns. Consider targeted primary research."
                )

            return result

        except Exception as e:
            logger.error(f"GPT analysis failed: {e}")
            # Fallback to basic summary
            return {
                'query': task,
                'analysis': f"Collected {len(all_items)} data points about {task}. Analysis generation failed.",
                'data_points_analyzed': len(all_items),
                'sources_used': len(all_data),
                'error': str(e),
                'raw_data': all_items,
                'domain_relevance': {
                    'score': data_relevance_score,
                    'is_domain_specific': False
                }
            }
