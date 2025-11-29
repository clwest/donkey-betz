"""
Research Agent - Specialized for Web & Spider Search ONLY
==========================================================

Session 268: Phase 2 - Research Agents

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
- spider_query: Query the spider network (70 spiders, 24 data sources)
- analyze_trends: Analyze trending topics from spider data

Spider network categories:
- Tech: HackerNews, DevTo, TechCrunch, Wired, MIT Tech Review
- Jobs: RemoteOK, WeWorkRemotely, Adzuna
- Financial: CoinGecko, Yahoo Finance
- Creative: Dribbble, Behance, Unsplash
- Community: Reddit (20+ subreddits)

When given a research task:
1. Decide whether to use web search, spider query, or both
2. For current events/news, prefer web_search
3. For trends/opportunities, prefer spider_query
4. Synthesize findings into a clear summary

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
                "description": "Analyze trending topics from spider data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category to analyze",
                            "enum": ["tech", "financial", "jobs", "creative", "all"],
                            "default": "all"
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

                full_prompt = self._build_prompt(task, scifi_context, spider_context)
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
                        return AgentResult(
                            success=True,
                            message=f"Research completed from {len(all_results)} source(s)",
                            data={
                                'results': all_results,
                                'query': task
                            },
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made
                        )
                    else:
                        return AgentResult(
                            success=False,
                            error="Research returned no results",
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            tool_calls=tool_calls_made
                        )
                else:
                    return AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
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

                if category == 'tech':
                    results = self.spider_service.get_tech_trends(hours=hours, limit=limit)
                elif category == 'creative':
                    results = self.spider_service.get_creative_trends(hours=hours, limit=limit)
                elif category == 'jobs':
                    results = self.spider_service.get_job_market_summary(hours=hours, limit=limit)
                elif category == 'financial':
                    results = self.spider_service.get_market_insights()
                else:
                    results = self.spider_service.get_trending_topics(hours=hours, limit=limit)

                return {
                    'success': True,
                    'data': results
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Trend analysis failed: {str(e)}"
                }

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}. ResearchAgent only supports research tools."
            }
