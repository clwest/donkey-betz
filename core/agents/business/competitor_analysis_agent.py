"""
Competitor Analysis Agent - Business Intelligence
==================================================

Session 293: Business Research Extension
Session 303: Unified Intelligence Search + Auto Spider Refresh
Session 304: Learning Infrastructure Integration

This agent analyzes competitors in a given market/industry.
It uses web search and spider data to:
1. Identify key competitors
2. Analyze their features, pricing, positioning
3. Generate SWOT analysis
4. Find market gaps and opportunities

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

logger = logging.getLogger(__name__)


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

    system_prompt = """You are CompetitorAnalysisAgent, a specialist in competitive intelligence and market analysis.

Your ONLY job is to analyze competitors and market positioning. You do NOT create content.

You have these tools:
- refresh_spider_data: Trigger fresh data collection (use FIRST for up-to-date intel)
- get_prior_research: Retrieve past research to build on existing knowledge
- web_search: Search the web for competitor information, features, pricing
- spider_query: Query spider network for competitor mentions, news, discussions
- analyze_competitor: Deep analysis of a specific competitor (name, website)

IMPORTANT - Session 303 Intelligence Integration:
1. ALWAYS start with get_prior_research to check for existing analysis
2. Use refresh_spider_data to ensure fresh market data
3. Then proceed with web_search and spider_query
4. Build on past research rather than starting from scratch

When given a competitive analysis task:
1. Check for prior research on this market/topic
2. Refresh spider data for latest intel
3. Search for key competitors in that space
4. For each major competitor, gather:
   - Company overview and positioning
   - Key features/products
   - Pricing model (if available)
   - Strengths and weaknesses
   - Recent news/developments
5. Synthesize into a competitive landscape analysis
6. Identify market gaps and opportunities

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
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for competitor information, features, pricing, news",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'AI writing assistant competitors', 'Jasper AI vs Copy.ai')"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 20
                        },
                        "search_type": {
                            "type": "string",
                            "description": "Type of search",
                            "enum": ["search", "news"],
                            "default": "search"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "spider_query",
                "description": "Query spider network for competitor mentions in tech news, Reddit, HackerNews, ProductHunt",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for competitor mentions"
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by category",
                            "enum": ["tech", "news", "social", "all"],
                            "default": "all"
                        },
                        "hours": {
                            "type": "integer",
                            "description": "Look back period in hours",
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

    def _get_project_context(self, project_id: str) -> Dict[str, Any]:
        """
        Session 302: Fetch project context when project_id is provided.

        This enables users to say "Analyze competitors for this project"
        and have the agent automatically use the project's topic/description.

        Args:
            project_id: UUID of the PartnershipProject

        Returns:
            Dict with project context (name, description, type) or empty dict
        """
        if not project_id:
            return {}

        try:
            from core.models_partnership import PartnershipProject
            project = PartnershipProject.objects.get(id=project_id)
            return {
                'project_name': project.project_name,
                'project_description': project.description,
                'project_type': project.project_type,
                'project_id': str(project.id)
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

        with self.time_travel_session("competitor_analysis", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                # Session 302: Check for project_id in context and fetch project data
                project_id = context.get('project_id')
                project_context = self._get_project_context(project_id) if project_id else {}

                # Session 302: Enhance task with project context if available
                task = self._enhance_task_with_project(task, project_context)

                # Session 303: Store current task for tool access
                self._current_task = task

                # Session 303: Auto-trigger spider refresh for fresh data
                try:
                    refresh_result = self.unified_search.refresh_spiders_for_query(task)
                    logger.info(f"Auto-triggered spider refresh: {refresh_result.get('categories', [])}")
                    self.record_decision(
                        decision_type="data_refresh",
                        action="Triggered spider network refresh",
                        reasoning=f"Ensuring fresh data for: {task[:50]}",
                        confidence=0.9
                    )
                except Exception as e:
                    logger.warning(f"Auto spider refresh failed (continuing anyway): {e}")

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
                full_prompt = self._build_prompt(task, scifi_context, spider_context)

                # Session 303: Inject prior research context if available
                if prior_context:
                    full_prompt += f"\n\n{prior_context}\n"

                # Add instruction to be comprehensive
                full_prompt += """

IMPORTANT: For a thorough competitive analysis:
1. First check get_prior_research for existing analysis on this market
2. Use refresh_spider_data if you need the absolute latest data
3. Use web_search to find competitors in this market
4. Use spider_query to find discussions and reviews
5. For top 3-5 competitors, use analyze_competitor for deep dives
6. Finally, use generate_swot to synthesize findings

Return a comprehensive competitive landscape analysis."""

                # Make GPT call to determine tools to use
                gpt_response = self._call_openai(full_prompt)

                # Process tool calls
                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
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

                execution_time = int((time.time() - start_time) * 1000)

                if all_competitor_data:
                    # Synthesize the competitive analysis
                    synthesis = self._synthesize_analysis(task, all_competitor_data)

                    # Session 294: Save to database with embedding for semantic search
                    saved_result = None
                    try:
                        from core.models_unified_system import BusinessResearchResult
                        saved_result = BusinessResearchResult.save_competitor_analysis(
                            query=task,
                            synthesis=synthesis,
                            execution_time_ms=execution_time
                        )
                        logger.info(f"Saved competitor analysis to database: {saved_result.id}")
                    except Exception as e:
                        logger.warning(f"Failed to save competitor analysis: {e}")

                    result = AgentResult(
                        success=True,
                        message=f"Competitive analysis completed with {len(all_competitor_data)} data sources",
                        data={
                            'analysis': synthesis,
                            'raw_data': all_competitor_data,
                            'query': task,
                            'saved_id': str(saved_result.id) if saved_result else None
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

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
            try:
                from core.tools.web_search import WebSearchTool
                search_tool = WebSearchTool()
                results = search_tool.search(
                    query=arguments.get('query', ''),
                    max_results=arguments.get('num_results', 10),
                    search_type=arguments.get('search_type', 'search')
                )
                return {
                    'success': True,
                    'data': results
                }
            except Exception as e:
                logger.warning(f"Web search failed: {e}, using spider data as fallback")
                # Fallback to spider data
                return self._spider_fallback(arguments.get('query', ''))

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

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}"
            }

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
            # Session 293: gpt-5-mini uses tokens for internal reasoning first
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": swot_prompt}],
                max_completion_tokens=4000,  # High enough for reasoning + output
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

    def _synthesize_analysis(
        self,
        task: str,
        all_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize all gathered data into a coherent analysis using GPT."""

        # Collect all data points for analysis
        all_items = []
        for source in all_data:
            data = source.get('data', {})
            source_name = source.get('source', 'unknown')
            if isinstance(data, list):
                for item in data[:15]:  # Limit per source
                    # Session 293: Strip HTML from titles and descriptions
                    all_items.append({
                        'title': strip_html_tags(item.get('title', '')),
                        'description': strip_html_tags(item.get('description', ''))[:200],
                        'source': item.get('source', source_name),
                        'url': item.get('url', '')
                    })

        # Limit total items to avoid token limits
        all_items = all_items[:30]

        # Build analysis prompt
        items_text = "\n".join([
            f"- {item['title']}: {item['description'][:100]}..."
            for item in all_items if item['title']
        ])

        analysis_prompt = f"""You are a competitive intelligence analyst. Analyze the following market research data and provide actionable insights.

RESEARCH QUERY: {task}

DATA COLLECTED ({len(all_items)} articles/mentions):
{items_text}

Based on this data, provide a comprehensive competitive analysis with:

1. **MARKET OVERVIEW** (2-3 sentences about this market)

2. **KEY COMPETITORS IDENTIFIED** (list 3-5 main competitors with brief description)

3. **MARKET TRENDS** (3-4 current trends you see in the data)

4. **OPPORTUNITIES** (3-4 gaps or opportunities for a new entrant)

5. **THREATS & CHALLENGES** (2-3 things to watch out for)

6. **STRATEGIC RECOMMENDATIONS** (3-4 actionable recommendations for someone entering this market)

Be specific and reference actual data points where possible. This analysis will be used for business planning."""

        try:
            # Session 293: gpt-5-mini uses tokens for internal reasoning first
            # Need 4000+ tokens to ensure room for reasoning + visible output
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_completion_tokens=6000,  # High enough for reasoning + output
            )

            analysis_text = response.choices[0].message.content

            return {
                'query': task,
                'analysis': analysis_text,
                'data_points_analyzed': len(all_items),
                'sources_used': len(all_data),
                'raw_data': all_items  # Include for reference
            }

        except Exception as e:
            logger.error(f"GPT analysis failed: {e}")
            # Fallback to basic summary
            return {
                'query': task,
                'analysis': f"Collected {len(all_items)} data points about {task}. Analysis generation failed.",
                'data_points_analyzed': len(all_items),
                'sources_used': len(all_data),
                'error': str(e),
                'raw_data': all_items
            }
