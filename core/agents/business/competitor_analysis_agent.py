"""
Competitor Analysis Agent - Business Intelligence
==================================================

Session 293: Business Research Extension

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

Tools NOT Available (by design):
    - image/video/audio generation
    - editing operations
"""

import logging
import time
import json
from typing import Dict, Any, List

from core.agents.base_agent import BaseAgent, AgentResult

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
- web_search: Search the web for competitor information, features, pricing
- spider_query: Query spider network for competitor mentions, news, discussions
- analyze_competitor: Deep analysis of a specific competitor (name, website)

When given a competitive analysis task:
1. First identify the market/industry from the user's description
2. Search for key competitors in that space
3. For each major competitor, gather:
   - Company overview and positioning
   - Key features/products
   - Pricing model (if available)
   - Strengths and weaknesses
   - Recent news/developments
4. Synthesize into a competitive landscape analysis
5. Identify market gaps and opportunities

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
        }
    ]

    def __init__(self, user=None):
        super().__init__(user)
        self._spider_service = None
        self._semantic_search = None

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

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing competitive research request",
                    reasoning=f"Received task: {task[:100]}",
                    confidence=0.9
                )

                # Build prompt with context
                full_prompt = self._build_prompt(task, scifi_context, spider_context)

                # Add instruction to be comprehensive
                full_prompt += """

IMPORTANT: For a thorough competitive analysis:
1. First use web_search to find competitors in this market
2. Then use spider_query to find discussions and reviews
3. For top 3-5 competitors, use analyze_competitor for deep dives
4. Finally, use generate_swot to synthesize findings

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

                    return AgentResult(
                        success=True,
                        message=f"Competitive analysis completed with {len(all_competitor_data)} data sources",
                        data={
                            'analysis': synthesis,
                            'raw_data': all_competitor_data,
                            'query': task
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )
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
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": swot_prompt}],
                max_completion_tokens=1500,
                reasoning_effort="medium",
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
        """Synthesize all gathered data into a coherent analysis."""

        # Collect all competitor names mentioned
        competitors_found = set()
        all_mentions = []

        for source in all_data:
            data = source.get('data', {})
            if isinstance(data, list):
                for item in data:
                    title = item.get('title', '')
                    all_mentions.append(title)
            elif isinstance(data, dict):
                if 'name' in data:
                    competitors_found.add(data['name'])
                if 'recent_mentions' in data.get('analysis', {}):
                    for mention in data['analysis']['recent_mentions']:
                        all_mentions.append(mention.get('title', ''))

        return {
            'query': task,
            'competitors_identified': list(competitors_found),
            'total_mentions_analyzed': len(all_mentions),
            'data_sources': len(all_data),
            'summary': f"Analyzed {len(all_data)} data sources, found {len(competitors_found)} competitors"
        }
