"""
Research Agent - Specialized for Web & Spider Search ONLY
==========================================================

Session 268: Phase 2 - Research Agents
Session 304: Learning Infrastructure Integration

This agent searches for information. That's ALL it does.
It has NO access to creation, editing, or generation tools.

Tools Available:
    - web_search: Search the web using Serper API
    - spider_query: Query the spider network for data
    - analyze_trends: Analyze trending topics from spiders

Tools NOT Available (by design):
    - image/video/audio generation
    - editing operations
    - 3D generation
"""

import logging
import time
from typing import Dict, Any, List, Optional

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Agent specialized in research and information gathering. Cannot create content.

    This agent:
    1. Takes a research task like "find trending AI topics"
    2. Queries web search and/or spider network
    3. Synthesizes and returns findings

    It CANNOT:
    - Generate images, videos, or audio
    - Edit any content
    - Create 3D models
    """

    name = "ResearchAgent"

    system_prompt = """You are ResearchAgent, a specialist in finding and analyzing information.

Your ONLY job is to research topics and gather information. You do NOT create content.
You have these tools:
- web_search: Search the web for current information
- spider_query: Query cached spider data (70 spiders, but only 15 Reddit subreddits)
- reddit_search: Search ANY Reddit subreddit in real-time (use for specific communities!)
- analyze_trends: Analyze trending topics from spider data

Spider network categories:
- Tech: HackerNews, DevTo, TechCrunch, Wired, MIT Tech Review
- Jobs: RemoteOK, WeWorkRemotely, Adzuna
- Financial: CoinGecko, Yahoo Finance
- Creative: Dribbble, Behance, Unsplash
- Community: Reddit (15 cached subreddits)

Dynamic Reddit Search (Session 312):
Use reddit_search for specific communities not in spider cache:
- Combine subreddits with +: "python+learnpython+django"
- Industry subreddits: r/podcasting, r/coffee, r/photography
- Technical subs: r/reactjs, r/golang, r/rust

When given a research task:
1. Decide whether to use web search, spider query, reddit_search, or combination
2. For current events/news, prefer web_search
3. For trends/opportunities, prefer spider_query
4. For specific Reddit communities, use reddit_search
5. Synthesize findings into a clear summary

You CANNOT create images, videos, audio, or edit anything. Only research.
If asked to create content, explain you can only research and suggest using the appropriate agent."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for current information using Serper API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
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
                            "enum": ["search", "news", "images"],
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
                "description": "Query the spider network for data from 70 spiders across 24 sources",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for spider data"
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by spider category",
                            "enum": ["tech", "financial", "jobs", "news", "social", "creative", "crypto"],
                            "default": None
                        },
                        "hours": {
                            "type": "integer",
                            "description": "Look back period in hours",
                            "default": 72
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return",
                            "default": 20
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_trends",
                "description": "Analyze trending topics from spider data. Use topic_filter to focus on specific areas like 'ai' for AI/ML content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category to analyze",
                            "enum": ["tech", "financial", "jobs", "creative", "all"],
                            "default": "all"
                        },
                        "topic_filter": {
                            "type": "string",
                            "description": "Filter results to specific topic: 'ai' for AI/ML, 'web' for web dev, 'security' for cybersecurity, 'cloud' for cloud/devops, 'design' for UI/UX/graphic design",
                            "enum": ["ai", "web", "security", "cloud", "design"],
                            "default": None
                        },
                        "hours": {
                            "type": "integer",
                            "description": "Look back period in hours",
                            "default": 24
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top trends to return",
                            "default": 10
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "reddit_search",
                "description": "Search ANY Reddit subreddit in real-time. Use for specific communities not cached by spider_query. Supports combining subreddits with + (e.g., 'python+django+flask').",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "subreddits": {
                            "type": "string",
                            "description": "Subreddit(s) to search, joined with +. Use 'all' for all of Reddit.",
                            "default": "all"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return",
                            "default": 25
                        },
                        "sort": {
                            "type": "string",
                            "description": "Sort order",
                            "enum": ["relevance", "hot", "top", "new"],
                            "default": "relevance"
                        },
                        "time_filter": {
                            "type": "string",
                            "description": "Time period to search",
                            "enum": ["hour", "day", "week", "month", "year", "all"],
                            "default": "month"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]

    def __init__(self, user=None):
        super().__init__(user)
        self._spider_service = None
        self._search_service = None

    @property
    def spider_service(self):
        """Lazy-load Spider Intelligence Service."""
        if self._spider_service is None:
            from core.services.spider_intelligence import SpiderIntelligenceService
            self._spider_service = SpiderIntelligenceService()
        return self._spider_service

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute research based on the task."""
        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 529: Build intelligent prompt with full context
        self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

        with self.time_travel_session("research", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing research request",
                    reasoning=f"Received task: {task[:100]}",
                    confidence=0.9
                )

                # Session 401: Use prompt with attribution for transparency
                full_prompt, knowledge_attribution = self._build_prompt_with_attribution(task, scifi_context, spider_context)
                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    all_results = []
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for research",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        if tool_result.get('success'):
                            all_results.append({
                                'source': tool_name,
                                'data': tool_result.get('data', tool_result)
                            })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    if all_results:
                        result = AgentResult(
                            success=True,
                            message=f"Research completed from {len(all_results)} source(s)",
                            data={
                                'results': all_results,
                                'query': task
                            },
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made,
                            knowledge_attribution=knowledge_attribution  # Session 401
                        )

                        # === Session 304: Learning Infrastructure ===
                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=True,  # Always uses spider data
                            scifi_context_used=bool(scifi_context)
                        )

                        self._create_execution_memory(
                            result=result,
                            task=task,
                            memory_type="success",
                            importance=0.6
                        )

                        # Share knowledge about research patterns
                        sources_used = [r['source'] for r in all_results]
                        self._share_knowledge(
                            knowledge_type='trend',
                            title=f"Research: {task[:60]}",
                            knowledge_value={
                                'query': task,
                                'sources_used': sources_used,
                                'result_count': len(all_results),
                                'success': True
                            },
                            confidence=0.75
                        )

                        return result
                    else:
                        result = AgentResult(
                            success=False,
                            error="Research returned no results",
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            tool_calls=tool_calls_made
                        )

                        # Record failure for learning
                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=True,
                            scifi_context_used=bool(scifi_context)
                        )

                        self._create_execution_memory(
                            result=result,
                            task=task,
                            memory_type="failure",
                            importance=0.7
                        )

                        return result
                else:
                    return AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        knowledge_attribution=knowledge_attribution  # Session 401
                    )

            except Exception as e:
                logger.error(f"ResearchAgent error: {e}")
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
        """Execute a tool call for research."""

        if tool_name == "web_search":
            try:
                from core.tools.web_search import WebSearchTool
                search_tool = WebSearchTool()
                # Session 348: Fixed - method is 'execute' not 'search'
                results = search_tool.execute(
                    query=arguments.get('query', ''),
                    max_results=arguments.get('num_results', 10),
                    search_type=arguments.get('search_type', 'text')  # 'text' not 'search'
                )
                # execute() returns a dict with 'success' already
                return results
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Web search failed: {str(e)}"
                }

        elif tool_name == "spider_query":
            try:
                results = self.spider_service.search_spider_data(
                    query=arguments.get('query', ''),
                    category=arguments.get('category'),
                    hours=arguments.get('hours', 72),
                    limit=arguments.get('limit', 20)
                )
                return {
                    'success': True,
                    'data': results
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Spider query failed: {str(e)}"
                }

        elif tool_name == "analyze_trends":
            try:
                category = arguments.get('category', 'all')
                hours = arguments.get('hours', 24)
                limit = arguments.get('limit', 10)
                # Session 272: Extract topic filter from arguments or query
                topic_filter = arguments.get('topic_filter')

                if category == 'tech':
                    # Session 274: Exclude ProductHunt from research (shown separately in Trending Now cards)
                    results = self.spider_service.get_tech_trends(hours=hours, limit=limit, topic_filter=topic_filter, include_producthunt=False)
                elif category == 'creative':
                    # Session 272: For design queries, use get_tech_trends with design filter
                    # since it has topic filtering logic; fallback to creative_trends otherwise
                    if topic_filter == 'design':
                        # Session 274: Exclude ProductHunt from research
                        results = self.spider_service.get_tech_trends(hours=hours, limit=limit, topic_filter='design', include_producthunt=False)
                    else:
                        results = self.spider_service.get_creative_trends(hours=hours, limit=limit)
                elif category == 'jobs':
                    results = self.spider_service.get_job_market_summary(hours=hours, limit=limit)
                elif category == 'financial':
                    results = self.spider_service.get_market_insights()
                else:
                    # Session 272: For 'all' category, get trending topics AND tech discussions
                    # This provides both topic summaries AND clickable article links
                    # Session 274: Exclude ProductHunt from research (shown separately in Trending Now cards)
                    trending_topics = self.spider_service.get_trending_topics(hours=hours, limit=limit)
                    tech_trends = self.spider_service.get_tech_trends(hours=hours, limit=limit, topic_filter=topic_filter, include_producthunt=False)

                    results = {
                        'topics': trending_topics,
                        'discussions': tech_trends.get('discussions', []),
                        'projects': tech_trends.get('projects', []),  # Now only GitHub, no ProductHunt
                        'sources': tech_trends.get('sources', {}),
                        'last_updated': tech_trends.get('last_updated')
                    }

                return {
                    'success': True,
                    'data': results
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Trend analysis failed: {str(e)}"
                }

        elif tool_name == "reddit_search":
            # Session 312: Dynamic Reddit search for ANY subreddit
            return self._reddit_dynamic_search(
                query=arguments.get('query', ''),
                subreddits=arguments.get('subreddits', 'all'),
                limit=arguments.get('limit', 25),
                sort=arguments.get('sort', 'relevance'),
                time_filter=arguments.get('time_filter', 'month')
            )

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}. ResearchAgent only supports research tools."
            }

    def _reddit_dynamic_search(
        self,
        query: str,
        subreddits: str = 'all',
        limit: int = 25,
        sort: str = 'relevance',
        time_filter: str = 'month'
    ) -> Dict[str, Any]:
        """
        Session 312: Dynamic Reddit search for ANY subreddit.

        First tries the registered RedditSearchTool (requires API credentials).
        Falls back to public JSON endpoint if credentials aren't configured.
        """
        try:
            # Try the registered RedditSearchTool first (uses PRAW with full API)
            from core.tools import ToolRegistry
            reddit_tool = ToolRegistry.get_tool('reddit_api')

            if reddit_tool and reddit_tool.is_configured:
                logger.info(f"Using RedditSearchTool for: {query} in r/{subreddits}")
                result = reddit_tool.execute(
                    query=query,
                    search_type='posts',
                    subreddit=subreddits,
                    limit=limit,
                    sort=sort,
                    time_filter=time_filter
                )
                if result.get('success'):
                    return result

            # Fallback: Use public JSON endpoint (no auth required)
            logger.info(f"Using public Reddit JSON for: {query} in r/{subreddits}")
            return self._reddit_public_json_search(query, subreddits, limit)

        except Exception as e:
            logger.error(f"Reddit dynamic search failed: {e}")
            return {
                'success': False,
                'error': f"Reddit search failed: {str(e)}"
            }

    def _reddit_public_json_search(
        self,
        query: str,
        subreddits: str = 'all',
        limit: int = 25
    ) -> Dict[str, Any]:
        """
        Session 312: Fallback Reddit search using public JSON endpoints.
        Works without API credentials.
        """
        import requests
        from datetime import datetime

        try:
            headers = {
                'User-Agent': 'DonkeyBetz-Research/1.0 (AI Content Studio; Educational Research)'
            }

            url = f"https://www.reddit.com/r/{subreddits}/search.json"
            params = {
                'q': query,
                'limit': min(limit, 100),
                'restrict_sr': 'true' if subreddits != 'all' else 'false',
                'sort': 'relevance',
                't': 'month'
            }

            response = requests.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])

                results = []
                for post in posts:
                    post_data = post.get('data', {})
                    results.append({
                        'id': post_data.get('id', ''),
                        'title': post_data.get('title', ''),
                        'selftext': post_data.get('selftext', '')[:500],
                        'subreddit': post_data.get('subreddit', ''),
                        'url': f"https://reddit.com{post_data.get('permalink', '')}",
                        'score': post_data.get('score', 0),
                        'num_comments': post_data.get('num_comments', 0),
                        'created_utc': datetime.fromtimestamp(
                            post_data.get('created_utc', 0)
                        ).isoformat() if post_data.get('created_utc') else None,
                        'author': post_data.get('author', '[deleted]'),
                    })

                logger.info(f"Public Reddit search returned {len(results)} results")

                return {
                    'success': True,
                    'data': {
                        'query': query,
                        'subreddit': subreddits,
                        'results': results,
                        'total_results': len(results),
                        'source': 'reddit_public_json',
                        'timestamp': datetime.now().isoformat()
                    }
                }

            elif response.status_code == 429:
                return {
                    'success': False,
                    'error': "Reddit rate limit reached. Try again in a few minutes."
                }
            else:
                return {
                    'success': False,
                    'error': f"Reddit returned status {response.status_code}"
                }

        except requests.Timeout:
            return {
                'success': False,
                'error': "Reddit search timed out"
            }
        except Exception as e:
            logger.error(f"Public Reddit JSON search failed: {e}")
            return {
                'success': False,
                'error': f"Reddit search failed: {str(e)}"
            }
